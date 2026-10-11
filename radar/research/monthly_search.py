"""Aylık hedef arama: python -m radar.research.monthly_search [iterasyon]

Her ayın ilk Cuması 20 hisse seçilir, 4 hafta tutulur. Hedef (aylık maksimum kâr): o ayın sonradan bakınca en iyi 20
hissesinin ortalama getirisi. Yakalama oranı = modelin 20 hissesinin ortalaması ÷ en iyi 20 ortalaması.

Model ailesi target_search ile aynı (havuz koşulları, eleme olayları, ağırlıklı/şekilli puan terimleri; haber konuları dahil).
Ezbere karşı:
- İç içe: test yılı Y'nin ayları için arama yalnızca, 4 haftalık getirisi Y başından önce gerçekleşmiş aylarla yapılır.
- Doğrulama: aramaya son 24 eğitim ayı katılmaz; birden çok başlangıçtan çıkan kurallar arasından bu 24 aydaki başarıya
  göre seçilir (aramanın kendi puanına göre değil).
- Karmaşıklık cezası: her havuz koşulu / terim / eleme küçük bir puan kaybettirir.
Çıktı: reports/research/aylik_arama.json, aylik_arama.jsonl
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from radar import config
from radar.research.target_search import K, Rule, mutate, picks, random_rule

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
EVENTS = config.ROOT / "data" / "derived" / "aylik_cerceve_olaylar.json"
OUT = config.ROOT / "reports" / "research" / "aylik_arama.json"
LOG = config.ROOT / "reports" / "research" / "aylik_arama.jsonl"
META = {"tarih", "yil", "getiri", "sektor", "sembol"}
TEST_YEARS = range(2016, 2026)  # haber konuları 2016'dan itibaren dolu
VALID_MONTHS = 24
PENALTY = 0.002


@dataclass
class Months:
    feats: list[str]
    events: list[str]
    dates: list[pd.Timestamp] = field(default_factory=list)
    X: list[np.ndarray] = field(default_factory=list)
    E: list[np.ndarray] = field(default_factory=list)
    R: list[np.ndarray] = field(default_factory=list)
    best: list[float] = field(default_factory=list)
    sym: list[np.ndarray] = field(default_factory=list)


def load() -> Months:
    df = pd.read_parquet(FRAME)
    events = [e for e in json.loads(EVENTS.read_text()) if e in df.columns]
    feats = [c for c in df.columns if c not in META and c not in events and pd.api.types.is_numeric_dtype(df[c])]
    m = Months(feats, events)
    for d, g in df.groupby("tarih"):
        g = g[np.isfinite(g.getiri)]
        m.dates.append(pd.Timestamp(d))
        m.X.append(g[feats].fillna(0.5).to_numpy(np.float32))
        m.E.append(g[events].fillna(0).to_numpy(np.float32) > 0)
        m.R.append(g.getiri.to_numpy(float))
        m.best.append(float(np.sort(m.R[-1])[-K:].mean()))
        m.sym.append(g.sembol.astype(str).to_numpy())
    return m


def month_result(rule: Rule, m: Months, i: int) -> tuple[float, float, np.ndarray]:
    p = picks(rule, m.X[i], m.E[i])
    if not len(p):
        return float("nan"), -1.0, p
    ret = float(m.R[i][p].mean())
    return ret, ret / m.best[i], p


def objective(rule: Rule, m: Months, idx: list[int]) -> float:
    caps = [month_result(rule, m, i)[1] for i in idx]
    size = len(rule.pool) + len(rule.terms) + len(rule.excl)
    return float(np.mean(caps)) - PENALTY * size


def search(m: Months, train: list[int], valid: list[int], iters: int, seed: int, restarts: int = 6):
    rng = np.random.default_rng(seed)
    cands = []
    per = max(iters // restarts, 1)
    shim = type("Y", (), {"feats": m.feats, "events": m.events})  # target_search.mutate/random_rule yalnızca adları kullanır
    for _ in range(restarts):
        cur = random_rule(rng, shim)
        cur_v = objective(cur, m, train)
        best, best_v = cur, cur_v
        for it in range(per):
            cand = mutate(cur, rng, shim)
            if len(cand.terms) > 6 or len(cand.excl) > 4:
                continue
            v = objective(cand, m, train)
            temp = 0.01 * (1 - it / per)
            if v >= cur_v or rng.random() < np.exp((v - cur_v) / max(temp, 1e-6)):
                cur, cur_v = cand, v
            if cur_v > best_v:
                best, best_v = cur, cur_v
        cands.append((best, best_v, objective(best, m, valid)))
    return max(cands, key=lambda c: c[2])  # doğrulama aylarına göre seçim


def describe(rule: Rule, m: Months) -> dict:
    shape = {0: "yüksek iyi", 1: "düşük iyi", 2: "yakın iyi"}
    return {"havuz": [f"{m.feats[f]} {'≥' if d > 0 else '≤'} {t:.2f}" for f, d, t in rule.pool],
            "eleme": [m.events[e] for e in rule.excl],
            "puan": [f"{w:.2f} × {m.feats[f]} ({shape[s]}{f' {c:.2f}' if s == 2 else ''})" for f, s, c, w in rule.terms]}


def main(iters: int = 3000) -> dict:
    t0 = time.time()
    m = load()
    dates = pd.DatetimeIndex(m.dates)
    rows, rules = [], {}
    for Y in TEST_YEARS:
        start = pd.Timestamp(f"{Y}-01-01")
        known = [i for i, d in enumerate(dates) if d + pd.Timedelta(weeks=4) < start]
        train, valid = known[:-VALID_MONTHS], known[-VALID_MONTHS:]
        test = [i for i, d in enumerate(dates) if d.year == Y]
        rule, fit, val = search(m, train, valid, iters, seed=Y)
        res = [month_result(rule, m, i) for i in test]
        rets = np.array([r for r, _, _ in res])
        caps = np.array([c for _, c, _ in res])
        hits = []
        for (r, c, p), i in zip(res, test):
            cut = np.quantile(m.R[i], 0.95)
            hits.append(int((m.R[i][p] >= cut).sum()))
        rows.append({"yil": Y, "egitim": round(fit, 4), "dogrulama": round(val, 4), "ay": len(test),
                     "aylik_getiri_ort": float(np.nanmean(rets)), "yillik_bilesik": float(np.nanprod(1 + rets) - 1),
                     "aylik_en_iyi20_ort": float(np.mean([m.best[i] for i in test])), "yakalama_ort": float(np.nanmean(caps)),
                     "en_iyi_yuzde5_ten_aylik": float(np.mean(hits)),
                     "son_ay_secim": [str(s) for s in m.sym[test[-1]][res[-1][2]]]})
        rules[str(Y)] = describe(rule, m)
        print(f"{Y}: eğitim {fit:.1%} doğrulama {val:.1%} → test yakalama {np.nanmean(caps):.1%}, aylık ort. {np.nanmean(rets):+.1%}, "
              f"yıllık bileşik {rows[-1]['yillik_bilesik']:+.0%}, en iyi %5'ten {np.mean(hits):.1f}/ay [{round(time.time() - t0)} sn]",
              flush=True)
    res = pd.DataFrame(rows)
    summary = {"iterasyon": iters, "yakalama_ort": float(res.yakalama_ort.mean()), "aylik_getiri_ort": float(res.aylik_getiri_ort.mean()),
               "yillik_bilesik_ort": float(res.yillik_bilesik.mean()), "aylik_en_iyi20_ort": float(res.aylik_en_iyi20_ort.mean()),
               "en_iyi_yuzde5_ten_aylik": float(res.en_iyi_yuzde5_ten_aylik.mean()), "rastgele_en_iyi_yuzde5_ten": K * 0.05,
               "yil": len(res)}
    out = {"ozet": summary, "yillar": rows, "kurallar": rules}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    with LOG.open("a") as f:
        f.write(json.dumps({"zaman": time.strftime("%Y-%m-%d %H:%M"), **summary}, ensure_ascii=False, default=float) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=float))
    return out


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3000)

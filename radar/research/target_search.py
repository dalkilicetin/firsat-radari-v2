"""Hedef arama: maksimum kâr raporundaki oranlara görmediği yılda ne kadar yaklaşılabilir?

python -m radar.research.target_search [iterasyon]

Hedef (Rapor 4): her yıl alınabilir hisseler içinde sonradan bakınca en iyi 20 hissenin ortalama getirisi.
Yakalama oranı = modelin 20 hissesinin ortalama getirisi ÷ o yılın en iyi 20 ortalaması; hedef ≥ %90.

Model ailesi (belirtiler raporundaki maddeler ve dağılımları):
- Havuz: en fazla 3 koşul (belirtinin yıl içi yüzdeliği ≤ / ≥ eşik).
- Eleme: seçilen olaylardan biri varsa hisse alınmaz.
- Puan: en fazla 8 terim; her terim bir belirti, şekil (yüksek iyi / düşük iyi / şu değere yakın iyi) ve ağırlık.
- Seçim: havuz içinde puanı en yüksek 20 hisse, eşit ağırlık, 1 yıl.

Doğrulama (görmediği veri): her test yılı Y için arama yalnızca Y'den önceki yıllarda yapılır, bulunan ayar Y'de ölçülür.
Ayrıca karşılaştırma için "ezber tavanı": aynı arama bütün yıllarda (test yılı dahil) yapılır — bu sayı gerçek başarı değildir.
Girdi: data/derived/belirti_cercevesi.parquet (indicators.py üretir). Çıktı: reports/research/hedef_arama.json, hedef_arama.jsonl
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from radar import config

FRAME = config.ROOT / "data" / "derived" / "belirti_cercevesi.parquet"
EVENTS = config.ROOT / "data" / "derived" / "belirti_cercevesi_olaylar.json"
OUT = config.ROOT / "reports" / "research" / "hedef_arama.json"
LOG = config.ROOT / "reports" / "research" / "hedef_arama.jsonl"
K = 20
FIRST_TEST = 2013  # en az 3 eğitim yılı (2010–2012)
META = {"yil", "getiri", "kazanan", "kaybeden", "sektor", "sembol"}


@dataclass
class Years:
    """Yıl başına numpy blokları (hızlı değerlendirme)."""
    feats: list[str]
    events: list[str]
    X: dict[int, np.ndarray] = field(default_factory=dict)   # yüzdelik, eksik = 0,5
    E: dict[int, np.ndarray] = field(default_factory=dict)   # olay 0/1
    R: dict[int, np.ndarray] = field(default_factory=dict)   # 1 yıl getiri
    best: dict[int, float] = field(default_factory=dict)     # en iyi 20 ortalaması
    sym: dict[int, np.ndarray] = field(default_factory=dict)


def load() -> Years:
    df = pd.read_parquet(FRAME)
    events = [e for e in json.loads(EVENTS.read_text()) if e in df.columns]
    feats = [c for c in df.columns if c not in META and c not in events and pd.api.types.is_numeric_dtype(df[c])]
    y = Years(feats, events)
    for yr, g in df.groupby("yil"):
        g = g[np.isfinite(g.getiri)]
        y.X[yr] = g[feats].fillna(0.5).to_numpy(np.float32)
        y.E[yr] = g[events].fillna(0).to_numpy(np.float32) > 0
        y.R[yr] = g.getiri.to_numpy(float)
        y.best[yr] = float(np.sort(y.R[yr])[-K:].mean())
        y.sym[yr] = g.sembol.astype(str).to_numpy()
    return y


@dataclass
class Rule:
    pool: list[tuple[int, int, float]]          # (belirti, yön +1: ≥ eşik / −1: ≤ eşik, eşik)
    excl: list[int]                             # olay indeksleri
    terms: list[tuple[int, int, float, float]]  # (belirti, şekil 0 yüksek/1 düşük/2 yakın, merkez, ağırlık)

    def describe(self, y: Years) -> dict:
        shape = {0: "yüksek iyi", 1: "düşük iyi", 2: "yakın iyi"}
        return {"havuz": [f"{y.feats[f]} {'≥' if d > 0 else '≤'} {t:.2f}" for f, d, t in self.pool],
                "eleme": [y.events[e] for e in self.excl],
                "puan": [f"{w:.2f} × {y.feats[f]} ({shape[s]}{f' {m:.2f}' if s == 2 else ''})" for f, s, m, w in self.terms]}


def picks(rule: Rule, X: np.ndarray, E: np.ndarray) -> np.ndarray:
    ok = np.ones(len(X), bool)
    for f, d, t in rule.pool:
        ok &= (X[:, f] >= t) if d > 0 else (X[:, f] <= t)
    for e in rule.excl:
        ok &= ~E[:, e]
    idx = np.flatnonzero(ok)
    if len(idx) < K:  # havuz çok dar: geçersiz kural
        return np.array([], int)
    s = np.zeros(len(idx))
    for f, sh, m, w in rule.terms:
        x = X[idx, f]
        s += w * (x if sh == 0 else (1 - x) if sh == 1 else -np.abs(x - m))
    return idx[np.argsort(-s, kind="stable")[:K]]


def year_result(rule: Rule, y: Years, yr: int) -> tuple[float, float]:
    """(portföy getirisi, yakalama oranı); geçersiz kural → (nan, -1)."""
    p = picks(rule, y.X[yr], y.E[yr])
    if not len(p):
        return float("nan"), -1.0
    ret = float(y.R[yr][p].mean())
    return ret, ret / y.best[yr]


def objective(rule: Rule, y: Years, years: list[int]) -> float:
    caps = [year_result(rule, y, yr)[1] for yr in years]
    return float(np.mean(caps))


def random_rule(rng: np.random.Generator, y: Years) -> Rule:
    nf, ne = len(y.feats), len(y.events)
    pool = [(int(rng.integers(nf)), int(rng.choice([-1, 1])), float(rng.uniform(0.1, 0.9))) for _ in range(rng.integers(0, 4))]
    excl = [int(e) for e in rng.choice(ne, size=rng.integers(0, min(3, ne) + 1), replace=False)] if ne else []
    terms = [(int(rng.integers(nf)), int(rng.integers(3)), float(rng.uniform(0.1, 0.9)), float(rng.uniform(0.1, 1)))
             for _ in range(rng.integers(1, 9))]
    return Rule(pool, excl, terms)


def mutate(rule: Rule, rng: np.random.Generator, y: Years) -> Rule:
    pool, excl, terms = list(rule.pool), list(rule.excl), list(rule.terms)
    nf, ne = len(y.feats), len(y.events)
    k = rng.integers(7)
    if k == 0 and pool:  # havuz eşiğini kaydır
        i = rng.integers(len(pool)); f, d, t = pool[i]
        pool[i] = (f, d, float(np.clip(t + rng.normal(0, 0.08), 0.02, 0.98)))
    elif k == 1:  # havuz koşulu ekle / çıkar
        if pool and (len(pool) >= 3 or rng.random() < 0.5):
            pool.pop(rng.integers(len(pool)))
        else:
            pool.append((int(rng.integers(nf)), int(rng.choice([-1, 1])), float(rng.uniform(0.1, 0.9))))
    elif k == 2 and terms:  # ağırlık
        i = rng.integers(len(terms)); f, s, m, w = terms[i]
        terms[i] = (f, s, m, float(np.clip(w + rng.normal(0, 0.15), 0.01, 1)))
    elif k == 3 and terms:  # şekil / merkez
        i = rng.integers(len(terms)); f, s, m, w = terms[i]
        terms[i] = (f, int(rng.integers(3)), float(np.clip(m + rng.normal(0, 0.1), 0.05, 0.95)), w)
    elif k == 4:  # terim ekle / çıkar
        if terms and (len(terms) >= 8 or rng.random() < 0.5) and len(terms) > 1:
            terms.pop(rng.integers(len(terms)))
        else:
            terms.append((int(rng.integers(nf)), int(rng.integers(3)), float(rng.uniform(0.1, 0.9)), float(rng.uniform(0.1, 1))))
    elif k == 5 and ne:  # eleme olayı aç / kapa
        e = int(rng.integers(ne))
        excl = [x for x in excl if x != e] if e in excl else excl + [e]
    else:  # terimin belirtisini değiştir
        if terms:
            i = rng.integers(len(terms)); f, s, m, w = terms[i]
            terms[i] = (int(rng.integers(nf)), s, m, w)
    return Rule(pool, excl, terms)


def search(y: Years, years: list[int], iters: int, seed: int, restarts: int = 8) -> tuple[Rule, float]:
    """Rastgele başlangıçlar + tepe tırmanma (tavlama). Yalnızca verilen yıllarla puanlanır."""
    rng = np.random.default_rng(seed)
    best, best_v = None, -np.inf
    per = max(iters // restarts, 1)
    for _ in range(restarts):
        cur = random_rule(rng, y)
        cur_v = objective(cur, y, years)
        for it in range(per):
            cand = mutate(cur, rng, y)
            v = objective(cand, y, years)
            temp = 0.02 * (1 - it / per)
            if v >= cur_v or rng.random() < np.exp((v - cur_v) / max(temp, 1e-6)):
                cur, cur_v = cand, v
            if cur_v > best_v:
                best, best_v = cur, cur_v
    return best, best_v


def main(iters: int = 4000) -> dict:
    t0 = time.time()
    y = load()
    years = sorted(y.X)
    rows, rules = [], {}
    for Y in [yr for yr in years if yr >= FIRST_TEST]:
        train = [yr for yr in years if yr < Y]
        rule, fit = search(y, train, iters, seed=Y)
        ret, cap = year_result(rule, y, Y)
        p = picks(rule, y.X[Y], y.E[Y])
        top20 = set(np.argsort(-y.R[Y])[:K])
        top5pct = set(np.argsort(-y.R[Y])[: max(1, len(y.R[Y]) // 20)])
        rows.append({"yil": Y, "egitim_yakalama": round(fit, 3), "test_getiri": ret, "en_iyi20": y.best[Y], "test_yakalama": cap,
                     "en_iyi20_den": len(top20 & set(p)), "en_iyi_yuzde5_ten": len(top5pct & set(p)),
                     "secim": [str(s) for s in y.sym[Y][p]]})
        rules[Y] = rule.describe(y)
        print(f"{Y}: eğitim yakalama {fit:.1%} → test {cap:.1%} (getiri {ret:+.0%} / en iyi 20 {y.best[Y]:+.0%}) "
              f"[{round(time.time() - t0)} sn]", flush=True)
    # Ezber tavanı: test yılı da aramaya dahil (gerçek başarı değildir; görülen veriye uyumun üst sınırı).
    ceil_rule, ceil_v = search(y, years, iters, seed=1)
    ceiling = {yr: year_result(ceil_rule, y, yr) for yr in years}
    res = pd.DataFrame(rows)
    summary = {"iterasyon": iters, "test_yakalama_ort": float(res.test_yakalama.mean()),
               "test_getiri_ort": float(res.test_getiri.mean()), "en_iyi20_ort": float(res.en_iyi20.mean()),
               "hedefe_ulasan_yil": int((res.test_yakalama >= 0.9).sum()), "yil": len(res),
               "en_iyi20_den_ort": float(res.en_iyi20_den.mean()), "en_iyi_yuzde5_ten_ort": float(res.en_iyi_yuzde5_ten.mean()),
               "rastgele_en_iyi_yuzde5_ten": K * 0.05,
               "ezber_tavani_yakalama_ort": float(np.mean([c for _, c in ceiling.values()])), "ezber_kurali": ceil_rule.describe(y)}
    out = {"ozet": summary, "yillar": rows, "kurallar": {str(k): v for k, v in rules.items()},
           "ezber_yillar": {str(k): {"getiri": r, "yakalama": c} for k, (r, c) in ceiling.items()}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    with LOG.open("a") as f:
        f.write(json.dumps({"zaman": time.strftime("%Y-%m-%d %H:%M"), **{k: v for k, v in summary.items() if k != "ezber_kurali"}},
                           ensure_ascii=False, default=float) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "ezber_kurali"}, ensure_ascii=False, indent=1, default=float))
    return out


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4000)

"""Belirti ağırlık dağılımı araması: python -m radar.research.agirlik_arama [3ay|6ay] [nesil]

Puan = Σ ağırlık_i × (belirti_i yüzdeliği − 0,5); dönemin en yüksek puanlı K hissesi alınır, ufuk boyunca tutulur.
Ağırlıklar (yüzde dağılımı) evrimsel arama ile bulunur (sıralama tabanlı evrim stratejisi; her nesilde N aday, iyiler
etrafında yeni adaylar). L1 cezası gereksiz belirtileri sıfıra iter.

Görmediği veri (yürüyen test): her test yılı Y için
- arama yılları: Y'den önceki yıllar, hedefi Y başından önce gerçekleşmiş dönemler; son 2 yıl doğrulama olarak ayrılır,
- birden çok başlangıçtan çıkan dağılımlar arasından doğrulama yıllarında en iyisi seçilir,
- seçilen dağılım Y'de ölçülür (Y hiçbir aşamada aramaya girmez).
Amaç ölçütü: seçilen K hissenin ufuk getirisi ortalaması − tahmini işlem maliyeti (likiditeye göre, gidiş-dönüş).
Çıktı: reports/research/agirlik_arama_<ufuk>.json (+ hizli_denemeler.jsonl'a özet)
"""

from __future__ import annotations

import json
import sys
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research.backtest import cost_rate

D = config.ROOT / "data" / "derived"
OUT_DIR = config.ROOT / "reports" / "research"
META = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari", "getiri_13h", "getiri_26h", "getiri_52h", "getiri_104h"}
UFUK = {"3ay": (13, "getiri_13h", (1, 4, 7, 10)), "6ay": (26, "getiri_26h", (1, 7))}
TEST_YEARS = range(2015, 2026)
K = 20
POP, ELITE = 40, 10
L1 = 0.002
RESTARTS = 3
VALID_YEARS = 2


class Block:
    """Dönem başına numpy blokları."""

    def __init__(self, df: pd.DataFrame, feats: list[str]):
        self.dates, self.X, self.R, self.C, self.year, self.month, self.best = [], [], [], [], [], [], []
        for d, g in df.groupby("tarih"):
            self.dates.append(pd.Timestamp(d))
            self.X.append((g[feats].to_numpy(np.float32) - 0.5).clip(-0.5, 0.5))
            self.X[-1][np.isnan(self.X[-1])] = 0.0
            self.R.append(g.getiri.to_numpy(np.float32))
            self.C.append(2 * cost_rate(g.islem_tutari.fillna(0)).to_numpy(np.float32))  # gidiş-dönüş
            self.year.append(pd.Timestamp(d).year)
            self.month.append(pd.Timestamp(d).month)
            self.best.append(float(np.sort(self.R[-1])[-K:].mean()))
        self.dates = pd.DatetimeIndex(self.dates)

    def value(self, w: np.ndarray, idx: list[int]) -> float:
        out = 0.0
        for i in idx:
            s = self.X[i] @ w
            top = np.argpartition(-s, K)[:K]
            out += float(self.R[i][top].mean() - self.C[i][top].mean())
        return out / max(len(idx), 1)

    def value_pop(self, W: np.ndarray, idx: list[int]) -> np.ndarray:
        """Bir neslin bütün adaylarını birlikte değerlendirir (dönem başına tek matris çarpımı)."""
        out = np.zeros(len(W))
        for i in idx:
            S = self.X[i] @ W.T                       # hisse × aday
            top = np.argpartition(-S, K, axis=0)[:K]  # K × aday
            out += (self.R[i][top] - self.C[i][top]).mean(0)
        return out / max(len(idx), 1)

    def picks(self, w: np.ndarray, i: int) -> np.ndarray:
        s = self.X[i] @ w
        return np.argpartition(-s, K)[:K]


def evolve(b: Block, idx: list[int], valid: list[int], nfeat: int, gens: int, seed: int) -> tuple[np.ndarray, float, float]:
    rng = np.random.default_rng(seed)
    cands = []
    for _ in range(RESTARTS):
        mean = rng.normal(0, 0.3, nfeat)
        sigma = 0.3
        best_w, best_v = mean.copy(), -np.inf
        for g in range(gens):
            pop = mean + sigma * rng.normal(size=(POP, nfeat))
            vals = b.value_pop(pop, idx) - L1 * np.abs(pop).sum(1)
            order = np.argsort(-vals)
            if vals[order[0]] > best_v:
                best_v, best_w = vals[order[0]], pop[order[0]].copy()
            ranks = np.log(ELITE + 0.5) - np.log(np.arange(1, ELITE + 1))
            mean = (ranks[:, None] * pop[order[:ELITE]]).sum(0) / ranks.sum()
            sigma *= 0.97
        cands.append((best_w, best_v, b.value(best_w, valid)))
    w, fit, val = max(cands, key=lambda c: c[2])  # doğrulama yıllarına göre seçim
    return w, fit, val


def main(freq: str = "6ay", gens: int = 60) -> dict:
    t0 = time.time()
    weeks, col, form_months = UFUK[freq]
    df = pd.read_parquet(D / "aylik_cerceve.parquet")
    df["getiri"] = df[col]
    df = df[np.isfinite(df.getiri) & (df.likidite >= 0.3)]  # çok az işlem görenler dışarıda (maliyet ve uygulanabilirlik)
    feats = [c for c in df.columns if c not in META and pd.api.types.is_numeric_dtype(df[c])
             and not c.startswith(("piyasa_",))]  # piyasa rejimi bütün hisseler için aynı: doğrusal puanda etkisiz
    b = Block(df, feats)
    gap = pd.Timedelta(weeks=weeks)
    rows, weights = [], {}
    for Y in TEST_YEARS:
        start = pd.Timestamp(f"{Y}-01-01")
        known = [i for i, d in enumerate(b.dates) if d + gap < start]
        cut = pd.Timestamp(f"{Y - VALID_YEARS}-01-01")
        search_idx = [i for i in known if b.dates[i] + gap < cut]
        valid_idx = [i for i in known if b.dates[i] >= cut]
        w, fit, val = evolve(b, search_idx, valid_idx, len(feats), gens, seed=Y)
        test = [i for i, d in enumerate(b.dates) if d.year == Y and d.month in form_months]
        gross, net, hits, caps = [], [], [], []
        for i in test:
            p = b.picks(w, i)
            r = float(b.R[i][p].mean())
            gross.append(r); net.append(r - float(b.C[i][p].mean()))
            hits.append(int((b.R[i][p] >= np.quantile(b.R[i], 0.95)).sum())); caps.append(r / b.best[i])
        per_year = 52 / weeks
        rows.append({"yil": Y, "net": float(np.prod(1 + np.array(net)) - 1), "brut": float(np.prod(1 + np.array(gross)) - 1),
                     "en_iyi_yuzde5": float(np.mean(hits)), "yakalama": float(np.mean(caps)),
                     "arama": round(fit, 4), "dogrulama": round(val, 4)})
        top = np.argsort(-np.abs(w))[:12]
        tot = np.abs(w).sum()
        weights[str(Y)] = {feats[j]: round(float(w[j] / tot), 4) for j in top}
        print(f"{Y}: net {rows[-1]['net']:+.0%} (brüt {rows[-1]['brut']:+.0%}), en iyi %5'ten {np.mean(hits):.1f}, "
              f"arama {fit:+.3f} doğrulama {val:+.3f} [{round(time.time() - t0)} sn]  ağırlık: "
              + ", ".join(f"{feats[j]} {w[j] / tot:+.0%}" for j in top[:5]), flush=True)
    res = pd.DataFrame(rows)
    summary = {"ufuk": freq, "nesil": gens, "net_yillik_ort": float(res.net.mean()), "zararli_yil": int((res.net < 0).sum()),
               "yil": len(res), "en_iyi_yuzde5_ort": float(res.en_iyi_yuzde5.mean()), "yil_yil_net": [round(x, 3) for x in res.net]}
    out = {"ozet": summary, "yillar": rows, "agirliklar": weights, "belirtiler": feats}
    (OUT_DIR / f"agirlik_arama_{freq}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    with (OUT_DIR / "hizli_denemeler.jsonl").open("a") as f:
        f.write(json.dumps({"zaman": time.strftime("%Y-%m-%d %H:%M"), "deneme": f"agirlik_arama_{freq}", **summary},
                           ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "6ay", int(sys.argv[2]) if len(sys.argv) > 2 else 60)

"""Belirti başına tam tarama: python -m radar.research.tek_tek [--son=2024]

Her belirti tek başına bir kural olarak: yön (yüksek iyi / düşük iyi) × seçim (10 hisse, 20 hisse, en iyi %5, en iyi %10)
× tutma (1, 3, 6, 12 ay) × likidite tabanı (yok, likidite yüzdeliği ≥ 0,3). Her kural 2013–son yıllarında yıl yıl,
devir tabanlı maliyet düşülerek ölçülür (2025–2026 kilitli). Sonra:
- geriye bakınca en iyi kurallar (iyimser, yalnızca bilgi)
- dürüst seçim: her yıl Y için yalnızca Y'den önceki (≥ 3) yıllarda ortalaması en iyi kural ve en iyi 10 kuralın
  sıra ortalaması (topluluk) Y'de uygulanır.
Çıktı: reports/research/tek_tek.json (tüm kuralların yıl yıl net getirisi) ve tek_tek_ozet.json
"""

from __future__ import annotations

import json
import sys
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import hizli
from radar.research.backtest import cost_rate

OUT = config.ROOT / "reports" / "research" / "tek_tek.json"
SUMMARY = config.ROOT / "reports" / "research" / "tek_tek_ozet.json"
HORIZONS = ("aylik", "3ay", "6ay", "1yil")
SELECT = (("k10", 10), ("k20", 20), ("y5", 0.05), ("y10", 0.10))
LIQ = (0.0, 0.3)


def run_horizon(freq: str, son: int, feats: list[str] | None = None) -> dict[str, dict[int, float]]:
    hizli.TEST_YEARS = tuple(range(2013, son + 1))
    df, all_feats = hizli.load(freq)
    feats = feats or [c for c in all_feats if not c.startswith("piyasa_") and c not in hizli.CIKAR]
    weeks, _, months = hizli.UFUK[freq]
    df = df[(df.yil >= 2013) & (df.yil <= son) & df.tarih.dt.month.isin(months)
            & (df.tarih + pd.Timedelta(weeks=weeks) < pd.Timestamp(f"{son + 1}-01-01"))]
    rules = [(f, d, sn, sv, lq) for f in feats for d in (1, -1) for sn, sv in SELECT for lq in LIQ]
    held = {r: {} for r in rules}
    per = {r: {} for r in rules}  # yıl → dönem net getirileri listesi
    for t, g in df.groupby("tarih"):
        y = t.year
        for lq in LIQ:
            gg = g[g.likidite >= lq] if lq else g
            if len(gg) < 100:
                continue
            ret = gg.getiri.to_numpy()
            ids = gg.index.astype(str).to_numpy()
            cost = cost_rate(gg.islem_tutari.fillna(0)).to_numpy()
            X = gg[feats].to_numpy(dtype="float64")
            for j, f in enumerate(feats):
                x = X[:, j]
                ok = np.isfinite(x)
                if ok.sum() < 50:
                    continue
                for d in (1, -1):
                    order = np.argsort(-d * np.where(ok, x, -d * np.inf), kind="stable")
                    order = order[ok[order]]
                    for sn, sv in SELECT:
                        k = sv if isinstance(sv, int) else max(int(round(sv * ok.sum())), 5)
                        pick = order[:k]
                        r = (f, d, sn, sv, lq)
                        rate = dict(zip(ids[pick], cost[pick]))
                        h = held[r]
                        c = (sum(v for n, v in rate.items() if n not in h) + sum(v for n, v in h.items() if n not in rate)) / len(pick)
                        held[r] = rate
                        per[r].setdefault(y, []).append(float(ret[pick].mean() - c))
    out = {}
    for r, ys in per.items():
        key = f"{freq}|{r[0]}|{'+' if r[1] > 0 else '-'}|{r[2]}|lik{r[4]}"
        yy = {}
        for y, nets in ys.items():
            if 52 / weeks < 1:
                nets = [(1 + v) ** (52 / weeks) - 1 for v in nets]
            yy[y] = float(np.prod(1 + np.array(nets)) - 1)
        out[key] = yy
    return out


def summarize(results: dict, son: int) -> dict:
    from radar.research import izgara
    years = list(range(2013, son + 1))
    tab = pd.DataFrame({k: {int(y): v for y, v in d.items()} for k, d in results.items()}).T.reindex(columns=years)
    full = tab.dropna()
    spy = pd.Series(izgara.spy_years()).reindex(years)
    mean = full.mean(axis=1).sort_values(ascending=False)
    meta, ens = {}, {}
    for i, y in enumerate(years):
        prev = years[:i]
        if len(prev) < 3:
            continue
        m = full[prev].mean(axis=1)
        best = m.idxmax()
        meta[y] = {"secilen": best, "net": float(full.at[best, y])}
        top10 = m.nlargest(10).index
        ens[y] = {"secilenler": list(top10), "net": float(full.loc[top10, y].mean())}
    mr = pd.Series({y: v["net"] for y, v in meta.items()})
    er = pd.Series({y: v["net"] for y, v in ens.items()})
    sp = spy.reindex(mr.index)
    out = {
        "kural": int(len(full)),
        "geriye_bakinca_ilk_20": {k: round(float(v), 3) for k, v in mean.head(20).items()},
        "spy_ort": float(sp.mean()),
        "durust_tek_kural": {"ort": float(mr.mean()), "spyi_gecen": int((mr > sp).sum()), "spy_x3": int((mr >= 3 * sp.clip(lower=0)).sum()),
                             "yil": int(len(mr)), "yillar": meta},
        "durust_ilk10_ortalama": {"ort": float(er.mean()), "spyi_gecen": int((er > sp).sum()), "yil": int(len(er)),
                                  "yillar": {y: round(v["net"], 3) for y, v in ens.items()}},
        "belirti_basina_en_iyi": {},
    }
    feat = full.index.str.split("|").str[1]
    for f in sorted(set(feat)):
        sub = mean[mean.index.isin(full.index[feat == f])]
        out["belirti_basina_en_iyi"][f] = {"kural": sub.index[0], "ort": round(float(sub.iloc[0]), 3),
                                          "kotu_yil": int((full.loc[sub.index[0]] < 0).sum())}
    SUMMARY.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("belirti_basina_en_iyi",)}, ensure_ascii=False, indent=1, default=float)[:4000])
    return out


def main(son: int = 2024) -> None:
    results = json.loads(OUT.read_text()) if OUT.exists() and "--devam" in sys.argv else {}
    t0 = time.time()
    for f in HORIZONS:
        if any(k.startswith(f + "|") for k in results):
            continue
        results |= run_horizon(f, son)
        OUT.write_text(json.dumps(results))
        print(f"{f} tamam: {len(results):,} kural [{round(time.time() - t0)} sn]", flush=True)
    summarize(results, son)


if __name__ == "__main__":
    son = next((int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--son=")), 2024)
    main(son)

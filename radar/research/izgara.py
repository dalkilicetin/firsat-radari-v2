"""Tam ızgara: python -m radar.research.izgara [ufuk,...]

Boyutlar: ufuk (aylik, 3ay, 6ay, 1yil) × hedef (sira, fark, karisim) × hisse sayısı (5, 10, 20, 30) × likidite tabanı
(0, 0,3, 0,5) × eğitim penceresi (3, 5, 8 yıl). Her kombinasyon 2013–2025 yürüyen testle ölçülür (her test yılında model
yalnızca o yıldan önce getirisi gerçekleşmiş verilerle eğitilir; maliyet devir tabanlı düşülür).
Hız: model her (ufuk, hedef, pencere, likidite, yıl) için bir kez eğitilir; hisse sayıları aynı puanlardan değerlendirilir.

İki sonuç:
- geriye bakınca en iyi kombinasyon (iyimser; yalnızca bilgi için)
- seçim sürecinin dürüst sonucu (meta yürüyen test): her yıl Y için, Y'den önceki test yıllarında (en az 3 yıl) ortalaması en iyi
  olan kombinasyon seçilir ve Y'de uygulanır.
Çıktı: reports/research/izgara.json (tüm kombinasyonların yıl yıl net getirisi) ve izgara_ozet.json
"""

from __future__ import annotations

import itertools
import json
import sys
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import hizli
from radar.research.backtest import cost_rate

OUT = config.ROOT / "reports" / "research" / "izgara.json"
SUMMARY = config.ROOT / "reports" / "research" / "izgara_ozet.json"
YEARS = tuple(range(2013, 2026))
TARGETS = ("sira", "fark")
KS = (5, 10, 20, 30)
LIQ = (0.0, 0.3)
WINDOWS = (5, 8)


def evaluate(te: pd.DataFrame, scores: np.ndarray, k: int, weeks: int) -> float:
    te = te.assign(puan=scores)
    net, held = [], {}
    for _, g in te.groupby("tarih"):
        top = g.nlargest(k, "puan")
        rate = dict(zip(top.index.astype(str), cost_rate(top.islem_tutari.fillna(0)).to_numpy()))
        c = (sum(v for x, v in rate.items() if x not in held) + sum(v for x, v in held.items() if x not in rate)) / len(top)
        held = rate
        net.append(top.getiri.mean() - c)
    if net and weeks >= 52:
        net[-1] -= sum(held.values()) / max(len(held), 1)
    if 52 / weeks < 1:
        net = [(1 + x) ** (52 / weeks) - 1 for x in net]
    return float(np.prod(1 + np.array(net)) - 1)


def run_horizon(freq: str, results: dict) -> None:
    hizli.TEST_YEARS = YEARS
    df, feats = hizli.load(freq)
    weeks, _, form_months = hizli.UFUK[freq]
    gap = pd.Timedelta(weeks=weeks)
    t0 = time.time()
    hizli.ROUNDS = 100  # hız: daha az ve daha büyük adımlı ağaç
    hizli.BASE["learning_rate"] = 0.1
    for target, window, liq in itertools.product(TARGETS, WINDOWS, LIQ):
        keys = [f"{freq}|{target}|k{k}|lik{liq}|p{window}" for k in KS]
        if all(len(results.get(k_, {})) >= len(YEARS) - 1 for k_ in keys):
            continue  # daha önce bitmiş blok
        for Y in YEARS:
            start = pd.Timestamp(f"{Y}-01-01")
            tr = df[(df.tarih + gap < start) & (df.yil >= Y - window)]
            te = df[(df.yil == Y) & df.tarih.dt.month.isin(form_months)]
            if liq:
                tr, te = tr[tr.likidite >= liq], te[te.likidite >= liq]
            if len(tr) < 5000 or te.empty:
                continue
            s, _ = hizli.score(target, tr, te, feats, {})
            for k in KS:
                key = f"{freq}|{target}|k{k}|lik{liq}|p{window}"
                results.setdefault(key, {})[Y] = evaluate(te, s, k, weeks)
        print(f"{freq} {target} pencere {window} likidite {liq} tamam [{round(time.time() - t0)} sn]", flush=True)
        OUT.write_text(json.dumps(results, ensure_ascii=False))


def spy_years() -> dict[int, float]:
    from radar.research import context
    spy = context.etf_prices(pd.date_range("2008-12-26", pd.Timestamp.today(), freq="W-FRI"))["SPY"].dropna()
    out = {}
    for y in YEARS:
        i0 = spy.index.get_indexer([pd.Timestamp(f"{y}-01-01")], method="bfill")[0]
        i1 = spy.index.get_indexer([pd.Timestamp(f"{y + 1}-01-01")], method="bfill")[0]
        out[y] = float(spy.iloc[min(i1, len(spy) - 1)] / spy.iloc[i0] - 1)
    return out


def summarize(results: dict) -> dict:
    tab = pd.DataFrame(results).T.reindex(columns=list(YEARS))
    spy = pd.Series(spy_years())
    full = tab.dropna()
    mean = full.mean(axis=1).sort_values(ascending=False)
    best = mean.index[0]
    # meta yürüyen test: her yıl, önceki (≥ 3) test yıllarında en iyi ortalamalı kombinasyon
    meta = {}
    for i, y in enumerate(YEARS):
        prev = list(YEARS[:i])
        if len(prev) < 3:
            continue
        pick = full[prev].mean(axis=1).idxmax()
        meta[y] = {"secilen": pick, "net": float(full.at[pick, y])}
    meta_ret = pd.Series({y: v["net"] for y, v in meta.items()})
    sp = spy.reindex(meta_ret.index)
    out = {
        "kombinasyon": int(len(full)),
        "geriye_bakinca_en_iyi": {"ad": best, "ort": float(mean.iloc[0]), "yillar": {int(k): round(v, 3) for k, v in full.loc[best].items()}},
        "ilk_10": {k: round(float(v), 3) for k, v in mean.head(10).items()},
        "meta_secim": {"ort": float(meta_ret.mean()), "spy_ort": float(sp.mean()),
                       "spy_x3_ulasan_yil": int((meta_ret >= 3 * sp.clip(lower=0)).sum()),
                       "spyi_gecen_yil": int((meta_ret > sp).sum()), "yil": int(len(meta_ret)), "yillar": meta},
        "spy": {int(k): round(v, 3) for k, v in spy.items()},
    }
    SUMMARY.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k != "meta_secim"} | {"meta_ort": out["meta_secim"]["ort"],
          "meta_spy_ort": out["meta_secim"]["spy_ort"], "meta_spyx3": out["meta_secim"]["spy_x3_ulasan_yil"],
          "meta_spyi_gecen": out["meta_secim"]["spyi_gecen_yil"]}, ensure_ascii=False, indent=1, default=float))
    return out


def main(freqs: list[str]) -> None:
    results = json.loads(OUT.read_text()) if OUT.exists() else {}
    for f in freqs:
        run_horizon(f, results)
    summarize(results)


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else ["3ay", "6ay"])

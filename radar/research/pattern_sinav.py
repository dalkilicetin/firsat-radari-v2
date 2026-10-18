"""Pattern avından çıkan aile için sınav: 'dipten çok yükselmiş + likit + büyüyen'.

Kural (temsilci): dipten_52h ≥ 1,15 (52 haftalık dibin 2,15 katı) VE likidite ≥ 0,7 (en likit %30) VE gelir_buyumesi ≥ 0,3.
Not: Bu aile, görmediği aylardaki sonuca bakılarak öne çıkarıldı; Şubat/Mart artık tam görülmemiş değildir.
Sınavlar: eşik ızgarası (plato), yıl yıl S&P farkı, dönemler, düşüş, tek hisse sınırı, hisse sayısı, en iyi hisse çıkarılınca.

python -m radar.research.pattern_sinav → reports/research/pattern_sinav.json
"""

from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd

from radar import config
from radar.research.pattern_avi import CACHE, CHAINS, MIN_N

R = config.ROOT / "reports" / "research"


def portfolio(d: pd.DataFrame, mask: pd.Series, cap=None, drop_best=False) -> pd.DataFrame:
    rows = []
    for t, g in d[mask].groupby("tarih"):
        r = g.net.clip(upper=cap) if cap else g.net
        if drop_best and len(r) > 1:
            r = r.drop(r.idxmax())
        rows.append((t, len(g), r.mean()))
    p = pd.DataFrame(rows, columns=["tarih", "n", "r"]).set_index("tarih")
    allt = d.groupby("tarih").spy.first()
    p = p.reindex(allt.index)
    p["spy"] = allt
    p["r"] = np.where(p.n.fillna(0) >= MIN_N, p.r, p.spy)
    return p


def stats(p: pd.DataFrame, months) -> dict:
    q = p[p.index.month.isin(months)].dropna(subset=["spy"])
    yrs = len(q) / 4
    w = np.cumprod(1 + q.r.to_numpy())
    sw = np.cumprod(1 + q.spy.to_numpy())
    yr = (1 + q[["r", "spy"]]).groupby(q.index.year).prod() - 1
    return {"yillik": round(float(w[-1] ** (1 / yrs) - 1), 4), "spy": round(float(sw[-1] ** (1 / yrs) - 1), 4),
            "en_kotu_dusus": round(float((w / np.maximum.accumulate(w) - 1).min()), 3),
            "spy_dusus": round(float((sw / np.maximum.accumulate(sw) - 1).min()), 3),
            "spy_ustu_yil": f"{int((yr.r > yr.spy).sum())}/{len(yr)}", "medyan_hisse": float(q.n.median())}


def main() -> dict:
    d = pd.read_parquet(CACHE, columns=["tarih", "cik", "net", "spy", "dipten_52h", "likidite", "gelir_buyumesi",
                                        "faaliyet_marji_degisimi", "kucuk_boyut"])
    base = (d.dipten_52h >= 1.15) & (d.likidite >= 0.7) & (d.gelir_buyumesi >= 0.3)
    out = {}
    p = portfolio(d, base)
    out["temsilci"] = {ch: stats(p, m) for ch, m in CHAINS.items()}
    out["tek_hisse_+%100_sinir"] = {ch: stats(portfolio(d, base, cap=1.0), m)["yillik"] for ch, m in CHAINS.items()}
    out["her_donem_en_iyi_hisse_cikarilinca"] = {ch: stats(portfolio(d, base, drop_best=True), m)["yillik"] for ch, m in CHAINS.items()}
    # dönemler (üç zincir birlikte, aylık başlangıçlar → her zincir ayrı hesaplanıp ortalaması)
    per = {}
    for a, z in [(2010, 2014), (2015, 2019), (2020, 2022), (2023, 2026), (2025, 2026)]:
        pp = p[(p.index.year >= a) & (p.index.year <= z)]
        per[f"{a}-{z}"] = {ch: {k: stats(pp, m)[k] for k in ("yillik", "spy")} for ch, m in CHAINS.items()}
    out["donemler"] = per
    # yıl yıl (Şubat zinciri, görmediği aylar)
    q = p[p.index.month.isin(CHAINS["subat"])].dropna(subset=["spy"])
    yr = (1 + q[["r", "spy"]]).groupby(q.index.year).prod() - 1
    out["yil_yil_subat"] = {int(k): {"kural": round(float(v.r), 3), "spy": round(float(v.spy), 3)} for k, v in yr.iterrows()}
    # eşik ızgarası: üç belirtinin eşiklerini değiştir
    grid = []
    for dip, liq, gb in itertools.product([0.5, 0.75, 1.0, 1.15, 1.5, 2.0], [0.5, 0.6, 0.7, 0.8, 0.9], [None, 0.1, 0.3, 0.5]):
        m = (d.dipten_52h >= dip) & (d.likidite >= liq)
        if gb is not None:
            m &= d.gelir_buyumesi >= gb
        pp = portfolio(d, m)
        s = {ch: stats(pp, mm) for ch, mm in CHAINS.items()}
        grid.append({"dipten_52h_en_az": dip, "likidite_en_az": liq, "gelir_buyumesi_en_az": -1 if gb is None else gb,
                     **{f"{ch}_yillik": s[ch]["yillik"] for ch in CHAINS}, "spy": s["subat"]["spy"],
                     "medyan_hisse": s["subat"]["medyan_hisse"], "dusus_subat": s["subat"]["en_kotu_dusus"]})
    g = pd.DataFrame(grid)
    g["en_kotu_zincir_farki"] = g[[f"{ch}_yillik" for ch in CHAINS]].min(axis=1) - g.spy
    out["izgara_ozet"] = {"kombinasyon": int(len(g)), "uc_zincirde_spy_ustu": int((g.en_kotu_zincir_farki > 0).sum()),
                          "uc_zincirde_spy_+10_puan_ustu": int((g.en_kotu_zincir_farki > 0.10).sum())}
    g.round(4).to_csv(R / "pattern_sinav_izgara.csv", index=False)
    # bugünkü (son tarih) seçimler, bilgi amaçlı
    last = d.tarih.max()
    out["son_tarih"] = str(last.date())
    out["son_tarih_secimleri"] = d[base & (d.tarih == last)].cik.astype(str).tolist()
    (R / "pattern_sinav.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items()}, ensure_ascii=False, indent=1, default=str)[:7000])
    pd.set_option("display.width", 250)
    print(g.pivot_table(index=["gelir_buyumesi_en_az", "likidite_en_az"], columns="dipten_52h_en_az", values="en_kotu_zincir_farki", dropna=False).round(3).to_string())
    return out


if __name__ == "__main__":
    main()

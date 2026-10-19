"""Eşik avı: dipten kat, zirveden uzaklık ve gelir büyümesi (gerçek sayılar) için en yüksek getirili eşikler.

Kural biçimi: dipten_52h_kat ≥ x VE zirveden ≥ −a (zirveye en fazla %a uzak) VE zirveden ≤ −b (zirveden en az %b uzak)
VE yıllık gelir büyümesi ≥ %g VE likidite sırası ≥ L. Portföy: uyan bütün hisseler eşit ağırlık, 13 hafta, maliyet dahil;
5'ten az hisse varsa o dönem S&P 500. Üç zincir (Ocak/Şubat/Mart) ayrı ölçülür; sıralama en kötü zincire göre
(üçünde de iyi olan). Uyarı: binlerce kombinasyondan en iyisi şans payı içerir; komşu eşiklerin de iyi olması (plato) aranır.

python -m radar.research.esik_avi → reports/research/esik_avi.json, esik_avi.csv
"""

from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals, panel
from radar.research.pattern_avi import CACHE, CHAINS, MIN_N
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import REVENUE, by_filing, load_fin

R = config.ROOT / "reports" / "research"
DIP = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 7.0, 10.0]                 # dibin en az kaç katı
NEAR = [0.05, 0.10, 0.20, 0.30, 0.50, 1.0]                       # zirveye en fazla bu kadar uzak (1.0 = sınırsız)
FAR = [0.0, 0.10, 0.20, 0.30]                                    # zirveden en az bu kadar uzak
GROW = [-9.0, 0.0, 0.10, 0.20, 0.30, 0.50, 0.75, 1.0, 2.0]       # yıllık gelir büyümesi en az (−9 = sınırsız)
LIQ = [0.0, 0.5, 0.7, 0.9]                                       # likidite sırası en az


def data() -> pd.DataFrame:
    d = pd.read_parquet(CACHE, columns=["tarih", "cik", "net", "spy", "dipten_52h", "zirveden_52h", "likidite"])
    p = panel.build()
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    fin = fundamentals.plain(load_fin())
    rev = by_filing(fin, REVENUE, [1, 4])
    g = pit(rev.rename(columns={"accepted": "date"}).assign(value=(rev.cur / rev.prev - 1).where(rev.prev > 0))[["cik", "date", "value"]],
            p["price"].index, p["price"].columns, FUNDAMENTAL_MAX_AGE).reindex(dates).clip(-1, 5)
    d["gelir"] = g.to_numpy()[dates.get_indexer(d.tarih), g.columns.get_indexer(d.cik.astype(str))]
    d["kat"] = 1 + d.dipten_52h
    return d


def main() -> dict:
    d = data()
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    di = dates.get_indexer(d.tarih)
    spy = d.groupby("tarih").spy.first().reindex(dates).to_numpy()
    month = dates.month.to_numpy()
    net = d.net.to_numpy(np.float64)
    kat, zir, gel, liq = (d[c].to_numpy() for c in ("kat", "zirveden_52h", "gelir", "likidite"))
    sel = {ch: np.isin(month, m) & np.isfinite(spy) for ch, m in CHAINS.items()}
    sp_cagr = {ch: np.prod(1 + spy[s]) ** (4 / s.sum()) - 1 for ch, s in sel.items()}
    rows = []
    for x, a, b, gg, L in itertools.product(DIP, NEAR, FAR, GROW, LIQ):
        if b >= a:
            continue
        m = (kat >= x) & (zir >= -a) & (zir <= -b) & (liq >= L)
        if gg > -9:
            m &= gel >= gg
        s = np.bincount(di[m], weights=net[m], minlength=len(dates))
        n = np.bincount(di[m], minlength=len(dates))
        rec = {"dipten_kat_en_az": x, "zirveye_en_fazla_uzak": a, "zirveden_en_az_uzak": b,
               "gelir_buyumesi_en_az": None if gg <= -9 else gg, "likidite_sira_en_az": L}
        for ch, sl in sel.items():
            inv = n[sl] >= MIN_N
            r = np.where(inv, s[sl] / np.maximum(n[sl], 1), spy[sl])
            rec[f"{ch}_yillik"] = float(np.prod(1 + r) ** (4 / sl.sum()) - 1)
            rec[f"{ch}_yatirimda"] = float(inv.mean())
            rec[f"{ch}_medyan_hisse"] = float(np.median(n[sl]))
            w = np.cumprod(1 + r)
            rec[f"{ch}_dusus"] = float((w / np.maximum.accumulate(w) - 1).min())
        rows.append(rec)
    t = pd.DataFrame(rows)
    ch = list(CHAINS)
    t["en_kotu_zincir"] = t[[f"{c}_yillik" for c in ch]].min(axis=1)
    t["ortalama"] = t[[f"{c}_yillik" for c in ch]].mean(axis=1)
    t["yatirimda_min"] = t[[f"{c}_yatirimda" for c in ch]].min(axis=1)
    t["en_kotu_dusus"] = t[[f"{c}_dusus" for c in ch]].min(axis=1)
    ok = t[t.yatirimda_min >= 0.75]
    ok.round(4).sort_values("en_kotu_zincir", ascending=False).to_csv(R / "esik_avi.csv", index=False)
    # her belirti için: diğerleri serbestken (en iyi kombinasyonların içinde) hangi eşik öne çıkıyor
    top = ok.sort_values("en_kotu_zincir", ascending=False).head(50)
    out = {"kombinasyon": int(len(t)), "yeterli_kapsam": int(len(ok)), "spy": {c: round(float(v), 4) for c, v in sp_cagr.items()},
           "en_iyi_20": top.head(20).round(4).to_dict(orient="records"),
           "en_iyi_50_icinde_esik_dagilimi": {c: top[c].value_counts(dropna=False).to_dict() for c in
                                             ["dipten_kat_en_az", "zirveye_en_fazla_uzak", "zirveden_en_az_uzak", "gelir_buyumesi_en_az", "likidite_sira_en_az"]},
           # tek belirti etkisi: diğer eşikler serbest bırakıldığında (dip ve gelir ızgarası, likidite 0.7)
           "dip_x_gelir_likidite07": ok[(ok.zirveye_en_fazla_uzak == 1.0) & (ok.zirveden_en_az_uzak == 0.0) & (ok.likidite_sira_en_az == 0.7)]
           .pivot_table(index="gelir_buyumesi_en_az", columns="dipten_kat_en_az", values="en_kotu_zincir", dropna=False).round(3)
           .reset_index().fillna("—").to_dict(orient="records"),
           "zirve_izgarasi_dip2_gelir30_lik07": ok[(ok.dipten_kat_en_az == 2.0) & (ok.gelir_buyumesi_en_az == 0.3) & (ok.likidite_sira_en_az == 0.7)]
           [["zirveye_en_fazla_uzak", "zirveden_en_az_uzak", "en_kotu_zincir", "ortalama", "ocak_medyan_hisse"]].round(3).to_dict(orient="records")}
    (R / "esik_avi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    pd.set_option("display.width", 250)
    cols = ["dipten_kat_en_az", "zirveye_en_fazla_uzak", "zirveden_en_az_uzak", "gelir_buyumesi_en_az", "likidite_sira_en_az",
            "ocak_yillik", "subat_yillik", "mart_yillik", "en_kotu_dusus", "ocak_medyan_hisse"]
    print(len(t), len(ok), out["spy"])
    print(top.head(25)[cols].round(3).to_string())
    print(json.dumps(out["en_iyi_50_icinde_esik_dagilimi"], ensure_ascii=False))
    print(pd.DataFrame(out["dip_x_gelir_likidite07"]).to_string())
    print(pd.DataFrame(out["zirve_izgarasi_dip2_gelir30_lik07"]).to_string())
    return out


if __name__ == "__main__":
    main()

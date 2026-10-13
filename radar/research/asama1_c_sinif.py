"""v1.2 (c) başarısızlıklarının sınıflandırılması (yalnızca betimleyici; kabul sonucu değişmez).

Her (c) sapması için ilk raporun hisse sayısının kaynağı (kapak/bilanço) ve geçerlilik tarihi bölünme tarihiyle karşılaştırılır:
- 'sayı bölünmeden önceye ait': ilk rapordaki sayının geçerlilik tarihi bölünmeden önce (karşılaştırma bölünme öncesi sayıyla yapılmış)
- 'kayıtta bölünme var, hisse sayısı değişmedi (ayrılma olası)': sayı bölünmeden sonraya ait ve bizim sayımız / ilk rapor ≈ oran
- 'birim/ölçek hatası olası': fark 10 katın üstünde
- 'ihraç (belgesiz)', 'azalma (belgesiz)': diğer yönlü sapmalar
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals
from radar.research.pit import to_friday

R = config.ROOT / "reports" / "research"


def main() -> dict:
    d = pd.read_csv(R / "asama1_v12_bolunme.csv", dtype={"cik": str})
    fin = fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"])
    cover = fin[(fin.tag == "EntityCommonStockSharesOutstanding")][["cik", "accepted"]].assign(cik=lambda x: x.cik.astype(str))
    cover_keys = set(zip(cover.cik, cover.accepted.astype(str).str[:10]))
    sh = fundamentals.shares_outstanding(fin).assign(cik=lambda x: x.cik.astype(str))
    sh["acc"] = sh.accepted.astype(str).str[:10]
    sh = sh.assign(fri=to_friday(sh.accepted))
    rows = []
    m = d[d.tur.isin(["bölünme", "ters bölünme"]) & (d.kaynak != "ftd_tahmini") & (d.c_kapak_farki.abs() > 0.02)]
    for r in m.itertuples():
        g = sh[(sh.cik == r.cik) & (sh.acc == r.ilk_rapor)]
        asof = pd.Timestamp(g["asof"].iloc[0]) if len(g) else pd.NaT
        x = np.log1p(r.c_kapak_farki) - np.log(r.oran)  # 0: bizim sayımız = ilk rapor × oran
        if not np.isfinite(r.c_kapak_farki) or abs(np.log1p(r.c_kapak_farki)) > np.log(10) and abs(x) > np.log(1.5):
            k = "birim/ölçek hatası olası"
        elif pd.notna(asof) and asof < pd.Timestamp(r.tarih):
            k = "sayı bölünmeden önceye ait"
        elif abs(x) < 0.03:
            k = "kayıtta bölünme var, hisse sayısı değişmedi (ayrılma olası)"
        elif r.c_kapak_farki < 0:
            k = "ilk rapordaki sayı fazla (ihraç vb.)"
        else:
            k = "ilk rapordaki sayı az (geri alım vb.)"
        rows.append({"cik": r.cik, "sembol": r.sembol, "tarih": r.tarih, "oran": r.oran, "tur": r.tur,
                     "belge": "satış belgesi var" if isinstance(r.satis_belgesi, str) else "belge yok",
                     "c_kapak_farki": r.c_kapak_farki, "ilk_rapor": r.ilk_rapor, "sayi_tarihi": str(asof.date()) if pd.notna(asof) else None,
                     "kapak_sayfasi": (r.cik, r.ilk_rapor) in cover_keys, "sinif": k})
    t = pd.DataFrame(rows)
    t.to_csv(R / "asama1_v12_c_siniflari.csv", index=False)
    out = {f"{tur} / {b}": g.sinif.value_counts().to_dict() for (tur, b), g in t.groupby(["tur", "belge"])}
    res = json.loads((R / "asama1_v12.json").read_text())
    res["c_siniflari"] = out
    (R / "asama1_v12.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    sp = t[t.sinif.str.startswith("kayıtta")]
    print(sp[["sembol", "tarih", "oran", "tur", "belge"]].to_string())
    return out


if __name__ == "__main__":
    main()


def c_tanima_uygun() -> dict:
    """(c) ön kayıttaki tanımıyla: bölünmeden SONRAYA tarihli (geçerlilik tarihi ≥ bölünme günü) ilk hisse sayısı.
    İlk uygulama, ilk raporun sayısı bölünmeden önceye ait olsa da onu kullanıyordu (uygulama hatası; sonuç kayıtta kalır)."""
    from radar.research import panel
    d = pd.read_csv(R / "asama1_v12_bolunme.csv", dtype={"cik": str})
    m = d[d.tur.isin(["bölünme", "ters bölünme"]) & (d.kaynak != "ftd_tahmini")].copy()
    p = panel.build()
    cols = pd.Index(sorted(set(m.cik) & set(p["price"].columns)))
    fin = fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"])
    sh = fundamentals.shares_outstanding(fin).assign(cik=lambda x: x.cik.astype(str))
    sh = sh[sh.cik.isin(set(cols))].assign(fri=lambda x: to_friday(x.accepted))
    shares = fundamentals.shares_wide(sh, p["price"][cols], p["raw"][cols])
    idx = shares.index
    by = {c: g.sort_values("accepted") for c, g in sh.groupby("cik")}
    out = []
    for r in m.itertuples():
        g = by.get(r.cik)
        val = np.nan
        if g is not None and r.cik in cols:
            t = pd.Timestamp(r.tarih)
            i = idx.searchsorted(t)
            if 0 < i < len(idx):
                nxt = g[(g["asof"] >= t) & (g.fri > idx[i])].head(1)
                if len(nxt) and (nxt.fri.iloc[0] - idx[i]).days <= 200:
                    j = idx.searchsorted(nxt.fri.iloc[0]) - 1
                    ours = shares.at[idx[j], r.cik]
                    if ours and np.isfinite(ours):
                        val = ours / nxt.value.iloc[0] - 1
        out.append(val)
    m["c_tanima_uygun"] = out
    m[["cik", "sembol", "tarih", "oran", "tur", "satis_belgesi", "c_kapak_farki", "c_tanima_uygun"]].to_csv(
        R / "asama1_v12_c_tanima_uygun.csv", index=False)
    res = {}
    for tur, g in m.groupby("tur"):
        for name, gg in (("belgesiz", g[g.satis_belgesi.isna()]), ("belgeli", g[g.satis_belgesi.notna()])):
            v = gg.c_tanima_uygun.dropna()
            res[f"{tur} / {name}"] = {"olcum": int(len(v)), "basarisiz": int((v.abs() > 0.02).sum()),
                                     "saglayan_pay": round(float((v.abs() <= 0.02).mean()), 4) if len(v) else None,
                                     "ilk_rapor_fazla": int((v < -0.02).sum()), "ilk_rapor_az": int((v > 0.02).sum()),
                                     "medyan": round(float(v.median()), 4) if len(v) else None}
    full = json.loads((R / "asama1_v12.json").read_text())
    full["c_tanima_uygun"] = res
    (R / "asama1_v12.json").write_text(json.dumps(full, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return res

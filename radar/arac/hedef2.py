"""Hedef denemesi, ikinci parti: piyasa rejimi süzgeci ve bilanço tepkisiyle giriş.

Önceden yazılmış 6 varyant (sonuç görülmeden sabitlendi), iki vade için (RADAR_YZ_VADE=3a ya da 1a):
- rejim: evrendeki hisselerin ortadaki 26 haftalık getirisi sıfırın altındaysa o dönem nakitte kal (getiri 0).
- kazanc: yalnızca son 4 haftada bilanço açıklamış ve açıklama günü piyasadan en az %5 iyi gitmiş hisseler arasından seç.
Toplam deneme sayısı (birinci parti dahil) rapora yazılır: çok deneme, şansla iyi görünen bir kural bulma riskini artırır.

python -m radar.arac.hedef2 → reports/research/arac_hedef2[_1a].md / .json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.arac import analiz, hedef, kazanc, yz
from radar.arac.analiz import Veri

R = config.ROOT / "reports" / "research"
TEPKI_ESIK = 0.05
TEPKI_GUN = 28
VARYANTLAR = {  # ad: (aday havuzu, sıralama, risk süzgeci, rejim süzgeci)
    "kural_10_rejim": ("kural", "kural", False, True),
    "kural_10_risk_rejim": ("kural", "kural", True, True),
    "kural30_B_10_risk_rejim": ("kural", "B", True, True),
    "kazanc_kural_10": ("kazanc", "kural", False, False),
    "kazanc_kural_10_rejim": ("kazanc", "kural", False, True),
    "kazanc_tepki_10": ("kazanc", "tepki", False, False),
}
ISIM = {"kural_10_rejim": "Kural radarı 10 hisse + kötü piyasada nakit", "kural_10_risk_rejim": "Aynısı + en riskli %20 elenir",
        "kural30_B_10_risk_rejim": "Kuralın ilk 30'undan büyük kazanan skoruyla 10 + risk süzgeci + kötü piyasada nakit",
        "kazanc_kural_10": "Güçlü bilanço tepkisi verenlerden kural puanına göre 10", "kazanc_kural_10_rejim": "Aynısı + kötü piyasada nakit",
        "kazanc_tepki_10": "Güçlü bilanço tepkisi verenlerden tepkinin büyüklüğüne göre 10"}
ONCEKI_DENEME = 16  # birinci parti: 8 varyant × 2 vade


def main() -> dict:
    v = Veri.yukle()
    S = pd.read_parquet(yz.OUT / "skorlar.parquet")
    P = analiz.puan(v, analiz.secilen_ayar())
    tab = v.tablo
    ev = tab["evren"]
    fiyat = tab["fiyat_persembe"].astype("float64")
    r26 = (fiyat / fiyat.shift(26) - 1).where(ev)
    rejim_iyi = r26.median(axis=1) > 0
    kz = kazanc.hesapla(fiyat.index, fiyat.columns)
    N, K = f"net_{yz.VADE}", f"kiyas_{yz.VADE}"
    tar = pd.DatetimeIndex(S.index.get_level_values(0).unique())

    def sec(t, havuz, sira, risk):
        row = P.loc[t].dropna()
        row = row[row >= 0]
        if havuz == "kazanc":
            ok = (kz["tepki1"].loc[t] >= TEPKI_ESIK) & (kz["tepki_gun"].loc[t] <= TEPKI_GUN)
            row = row[ok.reindex(row.index).fillna(False)]
        s = S.loc[t]
        if risk:
            row = row[s["C"].rank(pct=True).reindex(row.index).fillna(1) <= 0.8]
        if sira == "B":
            row = s["B"].reindex(row.sort_values(ascending=False).index[:30])
        elif sira == "tepki":
            row = kz["tepki1"].loc[t].reindex(row.index)
        return yz.ilk10(row, v.sektor)

    def zincir(yillar, havuz, sira, risk, rejim):
        if yz.VADE == "3a":
            qs = [t for t in analiz.ceyrek_baslari(tar, yillar) if tab[N].loc[t].notna().any()]
        else:
            qs = [t for t in tar[(tar.year >= yillar[0]) & (tar.year <= yillar[1])][:: yz.H] if tab[N].loc[t].notna().any()]
        r, spy, nakit, adet = [], [], 0, []
        for t in qs:
            spy.append(float(tab[K].at[t, "borsa"]))
            pk = [] if (rejim and not bool(rejim_iyi.get(t, True))) else sec(t, havuz, sira, risk)
            adet.append(len(pk))
            if not pk:
                r.append(0.0); nakit += 1; continue
            r.append(float(tab[N].loc[t, pk].mean()))
        r, spy = np.array(r), np.array(spy)
        yil = len(r) * yz.H / 52
        deger = np.cumprod(1 + r)
        yl, sp = float(deger[-1] ** (1 / yil) - 1), float(np.prod(1 + spy) ** (1 / yil) - 1)
        return dict(donem=len(r), nakit_donem=nakit, ort_hisse=float(np.mean(adet)), yillik=yl, borsa_yillik=sp,
                    kat=yl / sp if sp > 0 else float("nan"), en_buyuk_dusus=float((deger / np.maximum.accumulate(deger) - 1).min()),
                    en_kotu_ceyrek=float(r.min()), eksi_ceyrek=float((r < 0).mean()), bin_dolar=float(1000 * deger[-1]),
                    bin_dolar_borsa=float(1000 * np.prod(1 + spy)))

    out = {"gelistirme_2016_2022": {}, "ikinci_bakis_2023_2026": {}}
    for ad, a in VARYANTLAR.items():
        out["gelistirme_2016_2022"][ad] = zincir((yz.ILK_TEST, 2022), *a)
        out["ikinci_bakis_2023_2026"][ad] = zincir((2023, 2100), *a)
    out["deneme_sayisi"] = ONCEKI_DENEME + 2 * len(VARYANTLAR)
    (R / f"arac_hedef2{yz.EK}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    p = hedef.p
    L = [f"# Hedef denemesi, ikinci parti ({yz.H} hafta tut)", "",
         f"Önceden yazılmış {len(VARYANTLAR)} varyant; bugüne kadarki toplam deneme {out['deneme_sayisi']}. Masraflar düşülmüş, batanlar dahil. "
         "Nakitte geçen dönemlerin getirisi 0 sayılır.", ""]
    for bas, key in (("2016–2022", "gelistirme_2016_2022"), ("2023–2026", "ikinci_bakis_2023_2026")):
        L += [f"## {bas}", "", "| Varyant | Yıllık | Borsa yıllık | Kat | En büyük düşüş | En kötü dönem | Eksi kapanan dönem | Nakitte dönem | Ort. hisse | 1.000 $ → |", "|---|---|---|---|---|---|---|---|---|---|"]
        for ad, r in out[key].items():
            L.append(f"| {ISIM[ad]} | {p(r['yillik'])} | {p(r['borsa_yillik'])} | {r['kat']:.1f}× | {p(r['en_buyuk_dusus'])} | {p(r['en_kotu_ceyrek'])} | "
                     f"%{r['eksi_ceyrek'] * 100:.0f} | {r['nakit_donem']} / {r['donem']} | {r['ort_hisse']:.1f} | {r['bin_dolar']:,.0f} $ |")
        L.append("")
    (R / f"arac_hedef2{yz.EK}.md").write_text("\n".join(L))
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()

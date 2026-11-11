"""Hedef denemesi: "S&P 500'ün 3 katı" hedefine dürüst testte ne kadar yaklaşılıyor?

Önceden yazılmış 8 varyant (sonuçlar görülmeden sabitlendi; hepsi deneme defterine yazılır):
kural radarının puanı + Model C risk süzgeci + Model B sıralaması + liste boyu (10 / 5 / 3).
Her çeyrek başı cuma kapanışından alınır, 13 hafta tutulur, masraflar düşülür, batanlar dahil (zincir getirisi).
Model skorları yürüyen testten gelir (her yıl yalnızca önceki yıllarla eğitilmiş model).

python -m radar.arac.hedef → reports/research/arac_hedef.md / .json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.arac import analiz, yz
from radar.arac.analiz import Veri

R = config.ROOT / "reports" / "research"
VARYANTLAR = {  # ad: (liste boyu, risk süzgeci, B ile yeniden sıralama)
    "kural_10": (10, False, False),
    "kural_10_risk": (10, True, False),
    "kural_5": (5, False, False),
    "kural_5_risk": (5, True, False),
    "kural_3": (3, False, False),
    "kural_3_risk": (3, True, False),
    "kural30_B_10": (10, False, True),
    "kural30_B_10_risk": (10, True, True),
}
ISIM = {"kural_10": "Kural radarı, 10 hisse (mevcut)", "kural_10_risk": "10 hisse + en riskli %20 elenir", "kural_5": "İlk 5 hisse",
        "kural_5_risk": "İlk 5 + en riskli %20 elenir", "kural_3": "İlk 3 hisse", "kural_3_risk": "İlk 3 + en riskli %20 elenir",
        "kural30_B_10": "Kuralın ilk 30'u içinden büyük kazanan skoruna göre 10", "kural30_B_10_risk": "Aynısı + en riskli %20 elenir"}


def secim(v: Veri, P: pd.DataFrame, S: pd.DataFrame, t, n: int, risk: bool, b: bool) -> list[str]:
    row = P.loc[t].dropna()
    row = row[row >= 0]
    s = S.loc[t]
    if risk:
        cp = s["C"].rank(pct=True)
        row = row[cp.reindex(row.index).fillna(1) <= 0.8]
    if b:
        ilk = row.sort_values(ascending=False).index[:30]
        row = s["B"].reindex(ilk)
    return yz.ilk10(row, v.sektor, n=n, en_fazla=max(1, min(3, n // 2 + 1)))


def zincir(v: Veri, P, S, yillar, n, risk, b) -> dict:
    tab = v.tablo
    tar = pd.DatetimeIndex(S.index.get_level_values(0).unique())
    qs = [t for t in analiz.ceyrek_baslari(tar, yillar) if tab["net_3a"].loc[t].notna().any()]
    r, spy, kayip = [], [], []
    for t in qs:
        pk = secim(v, P, S, t, n, risk, b)
        if not pk:
            r.append(0.0); spy.append(tab["kiyas_3a"].at[t, "borsa"]); continue
        x = tab["net_3a"].loc[t, pk]
        r.append(float(x.mean())); spy.append(float(tab["kiyas_3a"].at[t, "borsa"])); kayip.append(float((x < -0.2).mean()))
    r, spy = np.array(r), np.array(spy)
    yil = len(r) / 4
    deger = np.cumprod(1 + r)
    dusus = float((deger / np.maximum.accumulate(deger) - 1).min())
    yl = float(deger[-1] ** (1 / yil) - 1)
    sp = float(np.prod(1 + spy) ** (1 / yil) - 1)
    return dict(ceyrek=len(r), yillik=yl, borsa_yillik=sp, kat=yl / sp if sp > 0 else float("nan"), en_buyuk_dusus=dusus,
                borsayi_gecen_ceyrek=float((r > spy).mean()), eksi_ceyrek=float((r < 0).mean()), en_kotu_ceyrek=float(r.min()),
                buyuk_kayip_orani=float(np.mean(kayip)) if kayip else float("nan"), bin_dolar=float(1000 * deger[-1]),
                bin_dolar_borsa=float(1000 * np.prod(1 + spy)))


def main() -> dict:
    v = Veri.yukle()
    S = pd.read_parquet(yz.OUT / "skorlar.parquet")
    P = analiz.puan(v, analiz.secilen_ayar())
    out = {"gelistirme_2016_2022": {}, "ikinci_bakis_2023_2026": {}}
    for ad, (n, risk, b) in VARYANTLAR.items():
        out["gelistirme_2016_2022"][ad] = zincir(v, P, S, (yz.ILK_TEST, 2022), n, risk, b)
        out["ikinci_bakis_2023_2026"][ad] = zincir(v, P, S, (2023, 2100), n, risk, b)
    out["deneme_sayisi"] = len(VARYANTLAR)
    (R / "arac_hedef.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    rapor(out)
    return out


def p(x) -> str:
    return "—" if x is None or pd.isna(x) else f"{'+' if x > 0 else '−' if x < 0 else ''}%{abs(x) * 100:.0f}"


def rapor(s: dict) -> None:
    L = ["# Hedef: S&P 500'ün 3 katı — dürüst testte nereye kadar?", "",
         f"Önceden yazılmış {s['deneme_sayisi']} varyant; hepsi burada (seçilip gösterilen yok). Her çeyrek başı alınır, 3 ay tutulur, masraflar düşülür, batanlar dahil. "
         "\"Kat\" = yıllık getiri ÷ borsanın yıllık getirisi. Kural ağırlıkları 2013–2022'de seçildiği için 2016–2022 sütunu kural lehine iyimserdir; "
         "2023–2026 daha önce açılmış bir dönemdir (ikinci bakış). Temiz sınav yalnızca bugünden sonraki canlı kayıttır.", ""]
    for bas, key in (("2016–2022", "gelistirme_2016_2022"), ("2023–2026", "ikinci_bakis_2023_2026")):
        L += [f"## {bas}", "", "| Varyant | Yıllık | Borsa yıllık | Kat | En büyük düşüş | En kötü çeyrek | Eksi kapanan çeyrek | 1.000 $ → | Borsada 1.000 $ → |", "|---|---|---|---|---|---|---|---|---|"]
        for ad, r in s[key].items():
            L.append(f"| {ISIM[ad]} | {p(r['yillik'])} | {p(r['borsa_yillik'])} | {r['kat']:.1f}× | {p(r['en_buyuk_dusus'])} | {p(r['en_kotu_ceyrek'])} | "
                     f"%{r['eksi_ceyrek'] * 100:.0f} | {r['bin_dolar']:,.0f} $ | {r['bin_dolar_borsa']:,.0f} $ |")
        L.append("")
    (R / "arac_hedef.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()

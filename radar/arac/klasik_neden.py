"""Klasik Radar (v5.16, varyant B): her çeyrek 10 hisse içinden en çok kazandıran / kaybettiren ve seçilme nedenleri.
→ reports/research/KLASIK_RADAR_EN_COK_KAZANDIRAN_KAYBETTIREN.md / klasik_radar_secimler_ozellik.csv

python -m radar.arac.klasik_neden
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.arac import analiz
from radar.arac.duzenek import Duzenek
from radar.arac.klasik import KURAL_OGRENME_BASI, kur, liste, p

R = config.ROOT / "reports" / "research"


def main() -> None:
    d = Duzenek.yukle(daralt=False)
    k = kur(d)
    P = k["P"]
    net3, net6 = d.net("3a"), d.net("6a")
    spy3 = d.kiyas("3a")["borsa"]
    son = d.brut("3a").dropna(how="all").index.max()
    bas = son - pd.DateOffset(years=3)
    weeks = [t for t in d.tarihler if bas <= t <= son]
    qs = list(analiz.ceyrek_baslari(pd.DatetimeIndex(weeks), (bas.year, 2100)))
    sec = d.sec.assign(cik=d.sec.cik.astype(str)).drop_duplicates("cik").set_index("cik")
    sym, ad = sec.symbol, sec.name
    r13 = P / P.shift(13) - 1
    r52 = P / P.shift(52) - 1
    mom = P.shift(13) / P.shift(52) - 1
    pull = (1 + r13) / (1 + k["mtd"] / 100) - 1
    rows = []
    for t in qs:
        pk = liste(d, k, t, "B")
        if not pk:
            continue
        n3 = net3.loc[t, pk]
        if n3.isna().all():
            continue
        top3 = set(k["mom_pct"].loc[t][k["evren"].loc[t]].index)  # evren
        for i, c in enumerate(pk, 1):
            rows.append(dict(tarih=t, sira=i, cik=c, sembol=sym.get(c, c), ad=str(ad.get(c, ""))[:26], net3=n3[c], net6=net6.at[t, c],
                             spy3=spy3.at[t], mom_pct=k["mom_pct"].at[t, c], duz_pct=k["duz_pct"].at[t, c], mom12_3=mom.at[t, c],
                             pull3_1=pull.at[t, c], r13=r13.at[t, c], r52=r52.at[t, c], mtd=k["mtd"].at[t, c], gun=k["gun"].at[t, c],
                             mcap_mr=k["mcap"].at[t, c] / 1e9, ni_mn=k["ni"].at[t, c] / 1e6, sok=bool(pd.notna(k["gun"].at[t, c]) and k["gun"].at[t, c] <= -8),
                             sektor=d.sektor_etf.get(c, "IWM"), temiz=t + pd.Timedelta(weeks=13) <= KURAL_OGRENME_BASI))
    A = pd.DataFrame(rows)
    A.to_csv(R / "klasik_radar_secimler_ozellik.csv", index=False)
    f = lambda x, n=0: "—" if pd.isna(x) else f"{x:.{n}f}"
    L = ["# Klasik Radar (v5.16, varyant B): her çeyrek en çok kazandıran ve kaybettiren", "",
         "Aynı yöntem: her çeyrek başı klasik radarın (fiyattan yeniden kurulabilen çekirdeği) 10 hissesi içinden 3 ayda en çok kazandıran ve en çok kaybettiren; "
         "cuma kapanışından alış, masraflar düşülmüş, batanlar dahil. Ham veri: `klasik_radar_secimler_ozellik.csv`. "
         "03.07.2026 çeyreği klasik kuralın öğrenildiği dönemle çakışır (işaretli).", ""]
    for kind, ad_, fn in (("kazandıran", "EN ÇOK KAZANDIRAN", "idxmax"), ("kaybettiren", "EN ÇOK KAYBETTİREN", "idxmin")):
        L += [f"## {ad_}", "", "| Çeyrek başı | Hisse | Listede | 3 ay | Borsa | 6 ay | Büyüklük | 12-3 ay getiri | Son çeyrek (3-1) | Son 52 hf | Not |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for t, g in A.groupby("tarih"):
            r = g.loc[getattr(g.net3, fn)()]
            nota = ("şok kaydı; " if r.sok else "") + ("kural bu dönemden öğrenildi" if not r.temiz else "")
            L.append(f"| {t:%d.%m.%Y} | {r.sembol} ({r.ad.strip()}) | {r.sira}. | {p(r.net3)} | {p(r.spy3)} | {p(r.net6)} | {f(r.mcap_mr, 1)} Mr$ | {p(r.mom12_3)} | {p(r.pull3_1)} | {p(r.r52)} | {nota} |")
        L.append("")
    # toplu karşılaştırma
    A["ust_yari"] = A.net3 > A.groupby("tarih").net3.transform("median")
    cols = ["mom_pct", "duz_pct", "mom12_3", "pull3_1", "r13", "r52", "mtd", "mcap_mr", "ni_mn"]
    med = A.groupby("ust_yari")[cols].median().T
    sp = A[cols].corrwith(A.net3, method="spearman")
    L += ["## Tüm seçimlerde (üst yarı ve alt yarı karşılaştırması)", "", f"{len(A)} seçim ({A.tarih.nunique()} çeyrek × 10). Ortadaki değerler; Spearman = 3 aylık getiri ile sıra ilişkisi (hata payı ≈ ±{1/np.sqrt(len(A)):.2f}).", "",
          "| Özellik | Alt yarı (ortadaki) | Üst yarı (ortadaki) | Spearman |", "|---|---|---|---|"]
    adlar = {"mom_pct": "12-3 momentum yüzdeliği", "duz_pct": "Düzeltme yüzdeliği", "mom12_3": "12-3 ay getirisi", "pull3_1": "Son çeyrek (3-1 ay) getirisi",
             "r13": "Son 13 hafta getirisi", "r52": "Son 52 hafta getirisi", "mtd": "Ay içi değişim %", "mcap_mr": "Piyasa değeri (Mr$)", "ni_mn": "Son 12 ay net kâr (M$)"}
    for c in cols:
        a, b = med.loc[c, False], med.loc[c, True]
        fm = (lambda x: p(x)) if c in ("mom12_3", "pull3_1", "r13", "r52") else (lambda x: f(x, 2) if c in ("mom_pct", "duz_pct") else f(x, 1))
        L.append(f"| {adlar[c]} | {fm(a)} | {fm(b)} | {sp[c]:+.2f} |")
    sk = A[A.sok]
    L += ["", f"**Şok kaydı olan seçimler:** {len(sk)} adet, ortalama 3 ay {p(sk.net3.mean()) if len(sk) else '—'} (tüm seçimler {p(A.net3.mean())}).",
          f"**Piyasa değeri < 5 Mr$:** {int((A.mcap_mr < 5).sum())} seçim, ortalama {p(A[A.mcap_mr < 5].net3.mean())}; ≥ 5 Mr$: {int((A.mcap_mr >= 5).sum())} seçim, ortalama {p(A[A.mcap_mr >= 5].net3.mean())}.",
          f"**Tüm seçimler:** ortalama {p(A.net3.mean())}, ortadaki {p(A.net3.median())}, −%20'den fazla kaybeden oranı %{(A.net3 < -0.2).mean() * 100:.0f}.", ""]
    (R / "KLASIK_RADAR_EN_COK_KAZANDIRAN_KAYBETTIREN.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

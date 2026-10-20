"""Ana analiz yöntemi, son 3 yıl: her çeyrek başında modelin seçtiği 10 hisse ve 3 / 6 ay sonra ne getirdikleri.

Her çeyrek başı Cuma'sında liste yalnızca o güne kadar bilinen veriyle (perşembe kesimi) ve kilitli ayarla çıkar; alış o
cuma kapanışı, getiriler masraf sonrası. Yanında: aynı dönemde borsa (SPY) ve evrenin gerçekte en çok kazandıran 3 hissesi.

python -m radar.arac.ceyrekler → reports/research/arac_ceyrekler.md / .csv
"""

from __future__ import annotations

import pandas as pd

from radar import config
from radar.arac import analiz
from radar.arac.analiz import Veri
from radar.identity import build as build_identity

R = config.ROOT / "reports" / "research"
YIL = 3


def yuzde(x) -> str:
    if x is None or pd.isna(x):
        return "henüz yok"
    return f"{'+' if x > 0 else '−' if x < 0 else ''}%{abs(x) * 100:.0f}"


def main() -> pd.DataFrame:
    v = Veri.yukle()
    ayar = analiz.secilen_ayar()
    sec = build_identity()["securities"]
    sym = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
    son = v.tablo["brut_3a"].dropna(how="all").index.max()
    qs = analiz.ceyrek_baslari(v.tarihler, (son.year - YIL, son.year))
    qs = qs[qs >= son - pd.DateOffset(years=YIL)]
    qs = pd.DatetimeIndex([t for t in qs if v.tablo["net_3a"].loc[t].notna().any()])  # 3 aylık sonucu henüz olmayan çeyrek yok
    ls = analiz.liste(v, ayar, qs)
    tab = v.tablo
    rows, L = [], [f"# Son {YIL} yıl, çeyrek çeyrek: model ne seçti, ne getirdi?", "",
                   f"Ayar: {ayar['ad']} (2013–2022 ile seçildi, kilitli). Getiriler cuma kapanışından alış, alış ve satış masrafları "
                   "düşülmüş. Borsadan çıkan / batan hisseler dahil (iflasta −%100).", ""]
    for t in qs:
        picks = ls.get(t, [])
        n3, n6 = tab["net_3a"].loc[t, picks], tab["net_6a"].loc[t, picks]
        spy3, spy6 = tab["kiyas_3a"].at[t, "borsa"], tab["kiyas_6a"].at[t, "borsa"]
        ev = tab["evren"].loc[t]
        b3 = tab["brut_3a"].loc[t].where(ev).nlargest(3)
        b6 = tab["brut_6a"].loc[t].where(ev).nlargest(3)
        kaz3 = tab["brut_3a"].loc[t].where(ev).rank(pct=True) >= 0.95
        L += [f"## {t:%d.%m.%Y}", "",
              f"**Bizim 10 hisse:** 3 ayda ortalama {yuzde(n3.mean())} (ortadaki {yuzde(n3.median())}), "
              f"6 ayda ortalama {yuzde(n6.mean())} · **Borsa:** 3 ay {yuzde(spy3)}, 6 ay {yuzde(spy6)}", "",
              "| # | Hisse | 3 ay | 6 ay | Dönemin en iyi %5'inde mi (3 ay) |", "|---|---|---|---|---|"]
        for k, c in enumerate(picks, 1):
            L.append(f"| {k} | {sym.get(c, c)} | {yuzde(n3[c])} | {yuzde(n6[c])} | {'evet' if kaz3.get(c, False) else ''} |")
            rows.append({"tarih": str(t.date()), "sira": k, "sembol": sym.get(c, c), "cik": c, "net_3a": n3[c], "net_6a": n6[c],
                         "en_iyi_yuzde5_3a": bool(kaz3.get(c, False))})
        L += ["", "**Gerçekte en çok kazandıranlar:** 3 ay: " + ", ".join(f"{sym.get(c, c)} {yuzde(x)}" for c, x in b3.items())
              + (" · 6 ay: " + ", ".join(f"{sym.get(c, c)} {yuzde(x)}" for c, x in b6.items()) if b6.notna().any() else " · 6 ay: henüz yok"), ""]
    df = pd.DataFrame(rows)
    ozet = df.groupby("tarih").agg(ort_3a=("net_3a", "mean"), ort_6a=("net_6a", "mean"), kazanan=("en_iyi_yuzde5_3a", "sum"))
    L[4:4] = ["## Özet", "", "| Çeyrek başı | Bizim 10 · 3 ay | Borsa · 3 ay | Bizim 10 · 6 ay | Borsa · 6 ay | En iyi %5'ten |",
              "|---|---|---|---|---|---|"] + [
        f"| {pd.Timestamp(t):%d.%m.%Y} | {yuzde(r.ort_3a)} | {yuzde(tab['kiyas_3a'].at[pd.Timestamp(t), 'borsa'])} | {yuzde(r.ort_6a)} | "
        f"{yuzde(tab['kiyas_6a'].at[pd.Timestamp(t), 'borsa'])} | {int(r.kazanan)} / 10 |" for t, r in ozet.iterrows()] + [""]
    (R / "arac_ceyrekler.md").write_text("\n".join(L) + "\n")
    df.to_csv(R / "arac_ceyrekler.csv", index=False)
    print("\n".join(L[:16 + len(ozet)]))
    return df


if __name__ == "__main__":
    main()

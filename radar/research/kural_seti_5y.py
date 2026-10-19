"""Beş kural, dip ve zirve SON 5 YIL (260 hafta) üzerinden: bugünkü liste + geçmiş testi; 52 haftalık sürümle yan yana.

dip_5y = son 260 haftanın en düşük düzeltilmiş fiyatı, zirve_5y = en yüksek (en az 208 hafta, yani 4 yıl veri şartı).
Kurallar ve test düzeneği kural_seti ile aynı (kurallar kullanıcıdan, veriye göre ayarlanmadı). Ayrıca en iyi 52 haftalık
kombinasyon (dip ≥ 2×, gelir ≥ %20, en likit %30) 5 yıllık dip ile. Her kural likidite şartsız ve 'en likit %30' ile.
Görmediği veri: kurallar veriden türetilmedi; ek olarak dönem bölünmesi (2013–2019 / 2020–2026) ve üç zincir.

python -m radar.research.kural_seti_5y → reports/research/kural_seti_5y.md, kural_seti_5y.json, kural_seti_5y_bugun.csv
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel
from radar.research.kural_seti import RULES, backtest, history, today
from radar.research.pattern_avi import CACHE, CHAINS

R = config.ROOT / "reports" / "research"
W, MINW = 260, 208
EXTRA = {"EN_IYI": ("Dibin ≥ 2 katı · gelir ≥ %20 artmış (52 haftalık en iyi kombinasyonun 5 yıllık sürümü)",
                    lambda x: (x.kat >= 2) & (x.gelir >= 0.20))}


def five_year(P: pd.DataFrame, dates) -> tuple[pd.DataFrame, pd.DataFrame]:
    lo = P.rolling(W, min_periods=MINW).min()
    hi = P.rolling(W, min_periods=MINW).max()
    return (P / lo).reindex(dates), (P / hi - 1).reindex(dates)


def split_stats(d: pd.DataFrame, m: pd.Series) -> dict:
    """2013–2019 ve 2020–2026 ayrı: üç zincirin ortalama yıllık getirisi ve S&P."""
    out = {}
    for nm, (a, b) in {"2013-2019": ("2013-01-01", "2019-12-31"), "2020-2026": ("2020-01-01", "2026-12-31")}.items():
        sl = (d.tarih >= a) & (d.tarih <= b)
        r = backtest(d[sl].reset_index(drop=True), m[sl].reset_index(drop=True))["tumu"]
        out[nm] = {"kural": float(np.mean([r[c]["yillik"] for c in CHAINS])), "spy": float(np.mean([r[c]["spy"] for c in CHAINS]))}
    return out


def main() -> dict:
    p = panel.build()
    P = p["price"]
    d = history()
    d["likidite"] = pd.read_parquet(CACHE, columns=["likidite"]).likidite.to_numpy()
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    k5, z5 = five_year(P, dates)
    ti, ci = dates.get_indexer(d.tarih), P.columns.get_indexer(d.cik.astype(str))
    d52 = d.copy()
    d["kat"] = k5.to_numpy()[ti, ci]
    d["zirveden"] = z5.to_numpy()[ti, ci]
    d = d[d.tarih >= "2013-01-01"].reset_index(drop=True)
    d52 = d52[d52.tarih >= "2013-01-01"].reset_index(drop=True)
    x = today()
    t = x.attrs["tarih"]
    k5t, z5t = five_year(P, P.index[-1:])
    x["kat_52h"], x["zirveden_52h"] = x.kat, x.zirveden
    x["kat"] = k5t.loc[t].reindex(x.index)
    x["zirveden"] = z5t.loc[t].reindex(x.index)
    dvr = p["dollar_volume"].loc[t].reindex(x.index)
    x["likidite"] = dvr.rank(pct=True)
    rules = dict(RULES) | EXTRA
    out, lists = {}, []
    for k, (desc, f) in rules.items():
        rec = {"tanim": desc}
        for liq_name, liq in (("likiditesiz", 0.0), ("likit30", 0.7)):
            m5 = (f(d) & (d.likidite >= liq)).fillna(False)
            m52 = (f(d52) & (d52.likidite >= liq)).fillna(False)
            rec[liq_name] = {"5y": backtest(d, m5), "52h": backtest(d52, m52), "5y_bolunme": split_stats(d, m5)}
            sel = x[(f(x) & (x.likidite >= liq)).fillna(False)].sort_values("kat", ascending=False)
            rec[liq_name]["bugun"] = sel.sembol.tolist()
            lists.append(sel.assign(kural=k, likidite_sarti=liq_name))
        out[k] = rec
    pd.concat(lists).round(4).to_csv(R / "kural_seti_5y_bugun.csv")
    (R / "kural_seti_5y.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    write(out, t)
    return out


def pct(v):
    return "—" if v is None or not np.isfinite(v) else f"%{v * 100:,.0f}"


def write(out, t):
    L = ["# Beş Kural — Dip ve Zirve SON 5 YIL Üzerinden", "",
         f"- Bugünkü liste: {t.date()} kapanışı. Dip/zirve: son 260 haftanın en düşük/en yüksek fiyatı (en az 4 yıl veri).",
         "- Test 2013–2026 (5 yıllık pencere için veri 2009'da başlıyor); her 3 ayda seçim, 3 ay tutma, eşit ağırlık, maliyet dahil; "
         "uyan hisse yoksa S&P. Yıllık getiriler üç zincir (Oca/Şub/Mar başlangıçlı) sırasıyla.",
         "- 'Likit %30' = günlük işlem tutarı en yüksek %30. Kurallar kullanıcıdan; veriye göre ayarlanmadı.", ""]
    for k, v in out.items():
        L += [f"## {k}: {v['tanim']}", ""]
        for liq_name, nm in (("likiditesiz", "Likidite şartı yok"), ("likit30", "En likit %30")):
            r = v[liq_name]
            b = r["bugun"]
            L.append(f"**{nm} — bugün uyan ({len(b)}):** " + (", ".join(b[:60]) + (" …" if len(b) > 60 else "") if b else "yok"))
            L.append("")
        L += ["| Şart | Pencere | 2013–2026 yıllık (Oca/Şub/Mar) | S&P | Son 5 yıl yıllık | Hisse olan dönem | Medyan hisse | 2013–19 / 2020–26 (kural vs S&P) |",
              "|---|---|---|---|---|---|---|---|"]
        for liq_name, nm in (("likiditesiz", "şartsız"), ("likit30", "likit %30")):
            for w in ("5y", "52h"):
                te = v[liq_name][w]
                a = " / ".join(pct(te["tumu"][c]["yillik"]) for c in CHAINS)
                s5 = " / ".join(pct(te["son5"][c]["yillik"]) for c in CHAINS)
                sp = pct(te["tumu"]["ocak"]["spy"])
                cov = pct(te["tumu"]["ocak"]["yatirimda"])
                med = f"{te['tumu']['ocak']['medyan_hisse']:.0f}"
                sb = ""
                if w == "5y":
                    s = v[liq_name]["5y_bolunme"]
                    sb = f"{pct(s['2013-2019']['kural'])} vs {pct(s['2013-2019']['spy'])} / {pct(s['2020-2026']['kural'])} vs {pct(s['2020-2026']['spy'])}"
                L.append(f"| {nm} | {'5 yıl' if w == '5y' else '52 hafta'} | {a} | {sp} | {s5} | {cov} | {med} | {sb} |")
        L.append("")
    (R / "kural_seti_5y.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()

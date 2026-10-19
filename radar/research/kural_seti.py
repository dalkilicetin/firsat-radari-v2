"""Kullanıcının beş kuralı (19 Ekim 2026): bugünkü liste + geçmiş testi.

Tanımlar (gerçek sayılar): dip/zirve son 52 haftanın en düşük/en yüksek (düzeltilmiş) fiyatı; dipten kat = fiyat / dip;
zirveden = fiyat / zirve − 1; gelir büyümesi = son raporun gelirinin bir yıl önceki aynı döneme göre artışı;
yıllık gelir = son 10-K'daki 12 aylık gelir (sağlam/büyük firma vekili; S&P 500 üyeliğinin geçmişi yok).
Evren: finans dışı, fiyat ≥ 1 $, günlük işlem ≥ 1 M$ (geriye_bakis ile aynı). Kurallar kullanıcı tarafından verildi;
veriye bakılarak ayarlanmadı.

Test: her ayın ilk Cuması seçim, 13 hafta tutma, eşit ağırlık, maliyet dahil. Üç zincir (Ocak/Şubat/Mart başlangıçlı,
çakışmayan). Uyan hisse yoksa o dönem S&P 500. Ayrıca seçim başına istatistik (her seçim tek tek). Dönemler: tümü
(2010–2026) ve son 5 yıl (Ekim 2021 →).

python -m radar.research.kural_seti → reports/research/kural_seti.md, kural_seti.json, kural_seti_bugun.csv
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals, panel, sectors
from radar.research.pattern_avi import CACHE, CHAINS
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import REVENUE, annual, by_filing, load_fin

R = config.ROOT / "reports" / "research"
RULES = {
    "K1": ("Dibin ≥ 2 katı · zirveden ≥ %40 düşmüş · gelir ≥ %60 artmış",
           lambda x: (x.kat >= 2) & (x.zirveden <= -0.40) & (x.gelir >= 0.60)),
    "K2": ("Dibin ≥ 2 katı · zirveden ≥ %60 düşmüş · gelir ≥ %100 artmış",
           lambda x: (x.kat >= 2) & (x.zirveden <= -0.60) & (x.gelir >= 1.00)),
    "K3": ("Zirveden ≥ %50 düşmüş · gelir ≥ %30 artmış · yıllık gelir ≥ 5 milyar $",
           lambda x: (x.zirveden <= -0.50) & (x.gelir >= 0.30) & (x.yillik_gelir >= 5e9)),
    "K3b": ("K3, yıllık gelir ≥ 1 milyar $ ile",
            lambda x: (x.zirveden <= -0.50) & (x.gelir >= 0.30) & (x.yillik_gelir >= 1e9)),
    "K4": ("Dibin ≥ 10 katı · gelir ≥ %200 artmış",
           lambda x: (x.kat >= 10) & (x.gelir >= 2.00)),
    "K5": ("Dibin ≥ 2 katı · gelir ≥ %62 artmış · zirveye en fazla %10 uzak",
           lambda x: (x.kat >= 2) & (x.gelir >= 0.62) & (x.zirveden >= -0.10)),
}


def fundamentals_wide(p, dates):
    fin = fundamentals.plain(load_fin())
    rev = by_filing(fin, REVENUE, [1, 4])
    P = lambda df, v: pit(df.rename(columns={"accepted": "date"}).assign(value=v)[["cik", "date", "value"]],
                          p["price"].index, p["price"].columns, FUNDAMENTAL_MAX_AGE).reindex(dates)
    g = P(rev, (rev.cur / rev.prev - 1).where(rev.prev > 0)).clip(-1, 5)
    a = annual(fin, REVENUE)
    lvl = P(a, a.value)
    return g, lvl


def history() -> pd.DataFrame:
    d = pd.read_parquet(CACHE, columns=["tarih", "cik", "net", "spy", "dipten_52h", "zirveden_52h"])
    p = panel.build()
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    g, lvl = fundamentals_wide(p, dates)
    ti, ci = dates.get_indexer(d.tarih), g.columns.get_indexer(d.cik.astype(str))
    d["gelir"] = g.to_numpy()[ti, ci]
    d["yillik_gelir"] = lvl.to_numpy()[ti, ci]
    d["kat"] = 1 + d.dipten_52h
    d["zirveden"] = d.zirveden_52h
    return d


def today() -> pd.DataFrame:
    p = panel.build()
    P, raw, dv, sec = p["price"], p["raw"], p["dollar_volume"], p["securities"]
    t = P.index[-1]
    inv = sectors.operating_universes(p)["tümü"].loc[t] & (raw.loc[t] >= 1) & (dv.loc[t] >= 1e6)
    u = inv[inv].index
    lo = P.rolling(52, min_periods=26).min().loc[t][u]
    hi = P.rolling(52, min_periods=26).max().loc[t][u]
    g, lvl = fundamentals_wide(p, P.index[-2:])
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    x = pd.DataFrame({"sembol": s.symbol.reindex(u), "sirket": s.name.reindex(u).str.replace(r"\s+-\s+.*$", "", regex=True),
                      "fiyat": raw.loc[t][u], "kat": P.loc[t][u] / lo, "zirveden": P.loc[t][u] / hi - 1,
                      "gelir": g.loc[t][u], "yillik_gelir": lvl.loc[t][u], "islem_milyon": dv.loc[t][u] / 1e6})
    x.attrs["tarih"] = t
    return x


def backtest(d: pd.DataFrame, mask: pd.Series) -> dict:
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    di = dates.get_indexer(d.tarih)
    spy = d.groupby("tarih").spy.first().reindex(dates).to_numpy()
    month, year = dates.month.to_numpy(), dates.year.to_numpy()
    m = mask.to_numpy()
    net = d.net.to_numpy(np.float64)
    s = np.bincount(di[m], weights=net[m], minlength=len(dates))
    n = np.bincount(di[m], minlength=len(dates))
    out = {}
    for per, lo in (("tumu", pd.Timestamp("2010-01-01")), ("son5", pd.Timestamp("2021-10-01"))):
        res = {}
        for ch, mm in CHAINS.items():
            sl = np.isin(month, mm) & np.isfinite(spy) & (dates >= lo)
            if not sl.any():
                res[ch] = None
                continue
            inv = n[sl] >= 1
            r = np.where(inv, s[sl] / np.maximum(n[sl], 1), spy[sl])
            yrs = sl.sum() / 4
            w = np.cumprod(1 + r)
            res[ch] = {"yillik": float(w[-1] ** (1 / yrs) - 1), "spy": float(np.prod(1 + spy[sl]) ** (1 / yrs) - 1),
                       "yatirimda": float(inv.mean()), "medyan_hisse": float(np.median(n[sl][inv])) if inv.any() else 0.0,
                       "en_kotu_dusus": float((w / np.maximum.accumulate(w) - 1).min())}
        # seçim başına (her ay, tüm seçimler; 13 haftalık getiri)
        sel = m & (d.tarih >= lo).to_numpy()
        r = net[sel]
        sp = d.spy.to_numpy()[sel]
        res["secim"] = {"adet": int(sel.sum()), "farkli_hisse": int(d.cik[sel].nunique()),
                        "ortalama_3ay": float(np.mean(r)) if len(r) else None, "medyan_3ay": float(np.median(r)) if len(r) else None,
                        "spy_ustu_pay": float(np.mean(r > sp)) if len(r) else None,
                        "yuzde50_ustu_pay": float(np.mean(r > 0.5)) if len(r) else None,
                        "yuzde50_kayip_pay": float(np.mean(r < -0.5)) if len(r) else None,
                        "spy_ortalama_3ay": float(np.nanmean(sp)) if len(sp) else None}
        out[per] = res
    return out


def pct(v):
    return "—" if v is None or not np.isfinite(v) else f"%{v * 100:,.1f}"


def main() -> dict:
    d = history()
    x = today()
    t = x.attrs["tarih"]
    out, lists = {}, []
    for k, (desc, f) in RULES.items():
        out[k] = {"tanim": desc, "test": backtest(d, f(d).fillna(False))}
        sel = x[f(x).fillna(False)].sort_values("kat", ascending=False)
        out[k]["bugun"] = sel.sembol.tolist()
        lists.append(sel.assign(kural=k))
    pd.concat(lists).round(4).to_csv(R / "kural_seti_bugun.csv")
    (R / "kural_seti.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))
    L = [f"# Beş Kural — Bugünkü Liste ve Geçmiş Testi", "", f"- Bugünkü liste: {t.date()} kapanışı (son fiyat verisi).",
         "- Evren: finans dışı, fiyat ≥ 1 $, günlük işlem ≥ 1 M$. Dip/zirve son 52 hafta. Kurallar kullanıcıdan; veriye göre ayarlanmadı.",
         "- Test: her 3 ayda seçim, 3 ay tutma, eşit ağırlık, maliyet dahil; uyan hisse yoksa S&P. Üç zincir (Oca/Şub/Mar başlangıçlı).", ""]
    for k, v in out.items():
        L += [f"## {k}: {v['tanim']}", ""]
        L.append(f"**Bugün uyan ({len(v['bugun'])}):** " + (", ".join(v["bugun"]) if v["bugun"] else "yok"))
        L.append("")
        L += ["| Dönem | Zincir | Kural yıllık | S&P yıllık | Hisse olan dönem | Medyan hisse | En kötü düşüş |", "|---|---|---|---|---|---|---|"]
        for per, nm in (("tumu", "2010–2026"), ("son5", "Son 5 yıl")):
            for ch in CHAINS:
                c = v["test"][per][ch]
                L.append(f"| {nm} | {ch} | {pct(c['yillik'])} | {pct(c['spy'])} | {pct(c['yatirimda'])} | {c['medyan_hisse']:.0f} | {pct(c['en_kotu_dusus'])} |")
        L += ["", "| Dönem | Seçim (farklı hisse) | 3 aylık ortalama | Medyan | S&P'yi geçen | +%50 üstü | −%50 kayıp | S&P 3 aylık ort. |",
              "|---|---|---|---|---|---|---|---|"]
        for per, nm in (("tumu", "2010–2026"), ("son5", "Son 5 yıl")):
            sc = v["test"][per]["secim"]
            L.append(f"| {nm} | {sc['adet']} ({sc['farkli_hisse']}) | {pct(sc['ortalama_3ay'])} | {pct(sc['medyan_3ay'])} | "
                     f"{pct(sc['spy_ustu_pay'])} | {pct(sc['yuzde50_ustu_pay'])} | {pct(sc['yuzde50_kayip_pay'])} | {pct(sc['spy_ortalama_3ay'])} |")
        L.append("")
    (R / "kural_seti.md").write_text("\n".join(L))
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()

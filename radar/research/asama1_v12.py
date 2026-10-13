"""1. aşama, ön kayıt v1.2 kontrolleri: bölünmeler (türlere ayrılmış, ihraç belgesi sınıflandırması), tetiklenmeyen 13 olay,
bölünmesiz hisselerde değişen hücreler (v1.1: 6.568), hisse sayısı kapsaması ve borç tanımı. Model eğitimi yok.

python -m radar.research.asama1_v12 [bolunme,on_uc,hucre,borc]
Çıktı: reports/research/asama1_v12.json, asama1_v12_bolunme.csv (olay başına), asama1_v12_hucre.csv (şirket başına)
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import fundamentals, panel
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit, to_friday

R = config.ROOT / "reports" / "research"
OUT = R / "asama1_v12.json"
V11_CSV = R / "asama1_bolunme_v11.csv"  # v1.1 olay tablosunun kopyası (commit a483c14)
ON_UC = [("1518461", "2021-02-17"), ("1734342", "2018-10-24"), ("2003977", "2026-02-13"), ("2023796", "2026-03-23"),
         ("2023796", "2026-05-04"), ("1928581", "2025-09-23"), ("1928581", "2026-01-08"), ("1928581", "2026-05-01"),
         ("1928581", "2026-07-02"), ("1928581", "2026-09-28"), ("1491419", "2017-10-17"), ("1673481", "2023-08-10"),
         ("1430723", "2014-07-17")]
SALE_FORMS = {"424B1", "424B2", "424B3", "424B4", "424B5", "424B7"}
REG_FORMS = {"S-1", "S-1/A", "F-1", "F-1/A", "S-3", "S-3/A", "S-3ASR", "F-3", "F-3/A", "F-3ASR"}


def event_type(r: float, source: str) -> str:
    if source == "ftd_tahmini":
        return "tahmini ters bölünme (FTD)"
    if r >= panel.SPLIT_MIN:
        return "bölünme"
    if r <= 1 / panel.SPLIT_MIN:
        return "ters bölünme"
    return "ayrılma / hisse temettüsü"


def _sh_long():
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    return sh.assign(cik=sh.cik.astype(str), fri=to_friday(sh.accepted))


def _docs() -> pd.DataFrame:
    """Şirket başına ihraç belgeleri: cik, date, form, satis (424B* ya da 8-K 3.02), kayit (S-1/S-3/F-1/F-3)."""
    iss = archive.load("ihrac_belgeleri", columns=["cik", "form", "filing_date"])
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    k = f[(f.form == "8-K") & f["items"].fillna("").str.contains(r"\b3\.02\b")][["cik", "form", "filing_date"]].assign(form="8-K 3.02")
    d = pd.concat([iss, k], ignore_index=True).rename(columns={"filing_date": "date"})
    d["cik"] = d.cik.astype(str)
    d["satis"] = d.form.isin(SALE_FORMS | {"8-K 3.02"})
    d["kayit"] = d.form.isin(REG_FORMS)
    return d


def splits(p: dict) -> tuple[dict, pd.DataFrame]:
    price, raw, idx = p["price"], p["raw"], p["price"].index
    ev = panel.split_events()
    ev = ev[ev.date >= "2010-01-01"].copy()
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    sh_long = _sh_long()
    shares = fundamentals.shares_wide(sh_long, price, raw)
    mcap = shares * raw
    by_cik = {c: g.sort_values("accepted") for c, g in sh_long.groupby("cik")}
    docs = {c: g for c, g in _docs().groupby("cik")}
    empty = sh_long.iloc[:0]
    rows = []
    for r in ev.itertuples():
        c, ratio = r.cik, float(r.ratio)
        row = {"cik": c, "sembol": sec.symbol.get(c), "tarih": str(r.date.date()), "oran": ratio, "kaynak": r.source,
               "tur": event_type(ratio, r.source), "asiri_oran": bool(ratio > 1000 or ratio < 1 / 1000)}
        i = idx.searchsorted(r.date)
        if c not in price.columns or i < 1 or i >= len(idx):
            row["durum"] = "panel dışı"
            rows.append(row)
            continue
        t0, t1 = idx[i - 1], idx[i]
        g = by_cik.get(c, empty)
        row["yeni_rapor_ayni_hafta"] = bool(((g.fri > t0) & (g.fri <= t1)).any())
        pr = price.at[t1, c] / price.at[t0, c] - 1
        rr = raw.at[t1, c] / raw.at[t0, c] - 1
        row["duz_fiyat_getirisi"] = pr
        row["tarih_hatasi"] = (1 + rr) * ratio / (1 + pr) - 1 if np.isfinite(pr) and np.isfinite(rr) else np.nan
        s0, s1, m0, m1 = shares.at[t0, c], shares.at[t1, c], mcap.at[t0, c], mcap.at[t1, c]
        row["hisse_once"], row["hisse_sonra"] = s0, s1
        row["a_oran_hatasi"] = s1 / s0 / ratio - 1 if s0 and np.isfinite(s0) else np.nan
        row["b_sureklilik_puan"] = (m1 / m0 - 1) - pr if m0 and np.isfinite(m0) else np.nan
        prev = g[g.fri <= t0].tail(1)
        nxt = g[g.fri > t1].head(1)
        row["c_kapak_farki"] = np.nan
        row["ilk_rapor"] = str(nxt.accepted.iloc[0])[:10] if len(nxt) else None
        if len(nxt) and (nxt.fri.iloc[0] - t1).days <= 200:
            j = idx.searchsorted(nxt.fri.iloc[0]) - 1
            ours = shares.at[idx[j], c] if 0 <= j < len(idx) else np.nan
            if ours and np.isfinite(ours):
                row["c_kapak_farki"] = ours / nxt.value.iloc[0] - 1
        # ihraç belgesi: önceki raporun kabulü < belge ≤ ilk raporun kabulü (ön kayıt v1.2, 6.3)
        lo = pd.Timestamp(prev.accepted.iloc[0]).normalize() if len(prev) else r.date - pd.Timedelta(days=120)
        hi = pd.Timestamp(nxt.accepted.iloc[0]).normalize() if len(nxt) else r.date + pd.Timedelta(days=120)
        dc = docs.get(c)
        win = dc[(dc.date > lo) & (dc.date <= hi)] if dc is not None else pd.DataFrame(columns=["form", "satis", "kayit"])
        row["satis_belgesi"] = ",".join(sorted(set(win[win.satis].form))) or None
        row["kayit_beyani"] = ",".join(sorted(set(win[win.kayit].form))) or None
        # ayrılma / hisse temettüsü alt sınıfı: önceki rapordan sonraki rapora dönem sonu sayısının değişimi
        if row["tur"] == "ayrılma / hisse temettüsü":
            if len(prev) and len(nxt) and prev.value.iloc[0] > 0:
                chg = nxt.value.iloc[0] / prev.value.iloc[0] - 1
                row["rapordan_rapora_hisse_degisimi"] = chg
                row["alt_sinif"] = "hisse temettüsü olası" if chg >= (ratio - 1) / 2 else "ayrılma olası"
            else:
                row["alt_sinif"] = "belirsiz"
        row["durum"] = "ölçüldü"
        rows.append(row)
    d = pd.DataFrame(rows)
    d.to_csv(R / "asama1_v12_bolunme.csv", index=False)
    return summarize(d), d


CHECKS = {"tarih": ("tarih_hatasi", 0.02), "fiyat": ("duz_fiyat_getirisi", 0.5), "a": ("a_oran_hatasi", 0.01),
          "b": ("b_sureklilik_puan", 0.02), "c": ("c_kapak_farki", 0.02)}


def _rate(g: pd.DataFrame, k: str) -> dict:
    col, tol = CHECKS[k]
    gg = g if k in ("tarih", "fiyat", "c") else g[~g.yeni_rapor_ayni_hafta.astype(bool)]
    v = gg[col].dropna()
    ok = v.abs() < tol if k == "fiyat" else v.abs() <= tol
    return {"olcum": int(len(v)), "basarisiz": int((~ok).sum()), "saglayan_pay": round(float(ok.mean()), 4) if len(v) else None}


def summarize(d: pd.DataFrame) -> dict:
    m = d[d.durum == "ölçüldü"].copy()
    m["yeni_rapor_ayni_hafta"] = m.yeni_rapor_ayni_hafta.astype(bool)
    out = {"olay_toplam": int(len(d))}
    out["kaynak_tur"] = d.groupby(["kaynak", "tur"]).size().rename("olay").reset_index().to_dict(orient="records")
    out["durum"] = d.durum.value_counts().to_dict()
    # v1.2: türlere ayrı; (c) yalnızca satış belgesi olmayanlarda
    v12 = {}
    for tur in ["bölünme", "ters bölünme"]:
        g = m[(m.tur == tur) & (m.kaynak != "ftd_tahmini")]
        res = {"olay": int(len(g)), "ayni_hafta_yeni_rapor": int(g.yeni_rapor_ayni_hafta.sum())}
        for k in ("tarih", "fiyat", "a", "b"):
            res[k] = _rate(g, k)
        nodoc = g[g.satis_belgesi.isna()]
        doc = g[g.satis_belgesi.notna()]
        res["c_belgesiz"] = _rate(nodoc, "c")
        cd = doc.c_kapak_farki.dropna()
        res["c_belgeli_kapsam_disi"] = {"olay": int(len(doc)), "olculen": int(len(cd)),
                                        "ilk_rapor_fazla": int((cd < -0.02).sum()), "uyumlu": int((cd.abs() <= 0.02).sum()),
                                        "ilk_rapor_az_aciklanmamis": int((cd > 0.02).sum()),
                                        "medyan_fark": round(float(cd.median()), 4) if len(cd) else None}
        cn = nodoc.c_kapak_farki.dropna()
        res["c_belgesiz_siniflar"] = {"saglandi": int((cn.abs() <= 0.02).sum()), "sayi_fazla (ilk rapor > bizim)": int((cn < -0.02).sum()),
                                      "sayi_az (ilk rapor < bizim)": int((cn > 0.02).sum()),
                                      "kayit_beyani_var": int(nodoc.kayit_beyani.notna().sum())}
        v12[tur] = res
    out["v12"] = v12
    # v1.1 kuralıyla (tek havuz, (c) her olaya): karşılaştırma için
    pool = m[m.tur.isin(["bölünme", "ters bölünme"]) & (m.kaynak == "yahoo")]
    out["v11_kurali_ayni_veride"] = {"olay": int(len(pool)), **{k: _rate(pool, k) for k in CHECKS}}
    for tur in ["ayrılma / hisse temettüsü", "tahmini ters bölünme (FTD)"]:
        g = m[m.tur == tur]
        res = {"olay": int(len(g)), **{k: _rate(g, k) for k in ("tarih", "fiyat", "b")}}
        if "alt_sinif" in g:
            res["alt_sinif"] = g.alt_sinif.value_counts().to_dict()
        out[tur] = res
    out["asiri_oranli"] = d[d.asiri_oran].drop(columns=[c for c in ["hisse_once", "hisse_sonra"] if c in d]).to_dict(orient="records")
    fails = []
    for tur in ["bölünme", "ters bölünme"]:
        g = m[(m.tur == tur) & (m.kaynak != "ftd_tahmini")]
        same = g.yeni_rapor_ayni_hafta
        bad = g[(~same & ((g.a_oran_hatasi.abs() > 0.01) | (g.b_sureklilik_puan.abs() > 0.02)))]
        fails.append(bad)
    out["a_b_basarisiz_olaylar"] = pd.concat(fails)[["cik", "sembol", "tarih", "oran", "tur", "kaynak", "a_oran_hatasi",
                                                    "b_sureklilik_puan", "duz_fiyat_getirisi"]].to_dict(orient="records")
    return out


def on_uc(p: dict, d: pd.DataFrame | None = None) -> dict:
    """v1.1'de hisse sayısı düzeltmesi hiç tetiklenmeyen 13 olay: tarih, sembol, oran yönü, hisse sayısı serisi."""
    if d is None:
        d = pd.read_csv(R / "asama1_v12_bolunme.csv", dtype={"cik": str})
    v11 = pd.read_csv(V11_CSV, dtype={"cik": str})
    sh = _sh_long()
    ev = panel.split_events()
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str))
    raw = p["raw"]
    out = []
    for c, t in ON_UC:
        new = d[(d.cik == c) & (d.tarih == t)]
        old = v11[(v11.cik == c) & (v11.tarih == t)]
        g = sh[sh.cik == c].sort_values("accepted")
        tt = pd.Timestamp(t)
        near = g[(g.accepted >= tt - pd.Timedelta(days=200)) & (g.accepted <= tt + pd.Timedelta(days=200))]
        # Panelde o şirketin ham fiyatı bölünme haftası dolu mu (eski yöntem S = ham / düzeltilmiş fiyat gerektiriyordu)
        i = raw.index.searchsorted(tt)
        rep_rows = []
        for x in near.itertuples():
            j = raw.index.searchsorted(to_friday(pd.Series([x.accepted])).iloc[0], side="right") - 1
            rep_rows.append({"kabul": str(x.accepted)[:10], "gecerlilik": str(x.asof)[:10], "hisse": float(x.value),
                             "rapor_haftasi_ham_fiyat_var": bool(c in raw.columns and j >= 0 and np.isfinite(raw.at[raw.index[j], c]))})
        out.append({
            "cik": c, "tarih": t, "sembol_sec": sec[sec.cik == c].symbol.tolist(),
            "olay_kayitlari": ev[ev.cik == c].assign(date=lambda x: x.date.astype(str)).to_dict(orient="records"),
            "oran": float(new.oran.iloc[0]) if len(new) else None,
            "v11": old[["a_oran_hatasi", "b_sureklilik_puan", "c_kapak_farki"]].round(4).to_dict(orient="records"),
            "v12": new[["a_oran_hatasi", "b_sureklilik_puan", "c_kapak_farki", "yeni_rapor_ayni_hafta", "satis_belgesi"]].round(4).to_dict(orient="records"),
            "bolunme_haftasi_ham_fiyat": [float(raw.at[raw.index[k], c]) if c in raw.columns else None for k in (i - 1, i)] if 0 < i < len(raw.index) else None,
            "raporlar": rep_rows,
        })
    return {"olaylar": out}


def _old_shares_wide(sh: pd.DataFrame, price, raw) -> pd.DataFrame:
    """v1.1 yöntemi (karşılaştırma için): fiyat oranından (S = ham / düzeltilmiş) türetilen düzeltme, kabul tarihinden."""
    dates, cols = price.index, price.columns
    S = (raw / price).replace([np.inf, -np.inf], np.nan).ffill()
    sh = sh.assign(cik=sh.cik.astype(str))
    day = pd.to_datetime(sh.accepted)
    row = dates.searchsorted(day.dt.normalize().to_numpy(), side="right") - 1
    col = pd.Index(cols.astype(str)).get_indexer(sh.cik)
    ok = (row >= 0) & (col >= 0)
    s_at = np.full(len(sh), -1.0)
    vals = S.to_numpy()[row[ok], col[ok]]
    s_at[ok] = np.where(np.isfinite(vals), vals, -1.0)
    long = sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]]
    n = pit(long, dates, cols, FUNDAMENTAL_MAX_AGE)
    s_rep = pit(long.assign(value=s_at), dates, cols, FUNDAMENTAL_MAX_AGE)
    ratio = (s_rep / S).where(s_rep > 0)
    ratio = ratio.where(np.abs(np.log(ratio)) > np.log(1.3), 1.0).fillna(1.0)
    return n * ratio


def hucre(p: dict) -> dict:
    """v1.1'de bölünme kaydı olmayan hisselerde değişen hücreler (6.568): her şirketin nedeni; yeni yöntemde olay kaydı olmayan
    hisselerde hiç hücre değişmemeli."""
    price, raw, idx = p["price"], p["raw"], p["price"].index
    v11 = pd.read_csv(V11_CSV, dtype={"cik": str})
    split_ciks_v11 = set(v11.cik)
    others = pd.Index([c for c in price.columns if c not in split_ciks_v11])
    sh = _sh_long()
    plain = pit(sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]], idx, others, FUNDAMENTAL_MAX_AGE)
    old = _old_shares_wide(sh, price[others], raw[others])
    changed = (old / plain - 1).abs() > 1e-9
    n_old = int(changed.sum().sum())
    ev = panel.split_events()
    big = panel.split_cum(ev)
    src = big.groupby("cik").source.agg(lambda s: ",".join(sorted(set(s))))
    early = big[big.date < "2010-01-01"].groupby("cik").size()
    per = changed.sum()
    per = per[per > 0]
    S = (raw[others] / price[others])
    rows = []
    for c, n in per.items():
        s = src.get(c)
        if s and "ftd_tahmini" in s:
            why = "FTD tahmini ters bölünme"
        elif s and "yahoo_cikan" in s:
            why = "çıkmış hissenin Yahoo bölünmesi (v1.1 olay listesinde yoktu)"
        elif c in early.index:
            why = "2010 öncesi Yahoo bölünmesi (v1.1 olay listesi 2010'dan başlıyordu)"
        elif s:
            why = "Yahoo bölünmesi (birleşmede taşınan geçmiş)"
        else:
            # olay kaydı yok: fiyat oranındaki sıçrama temettü kayması mı, veri hatası mı
            sc = S[c].dropna()
            jump = np.abs(np.log(sc / sc.shift(1))).max() if len(sc) > 1 else np.nan
            why = "temettü kayması (oran yavaş değişti)" if jump < np.log(1.1) else "olay kaydı yok, fiyat oranında sıçrama"
        rows.append({"cik": c, "hucre": int(n), "neden": why, "kaynak": s})
    t = pd.DataFrame(rows)
    t.to_csv(R / "asama1_v12_hucre.csv", index=False)
    # yeni yöntem: olay kaydı (eşik üstü) olmayan hisselerde değişen hücre
    no_ev = pd.Index([c for c in price.columns if c not in set(big.cik)])
    new = fundamentals.shares_wide(sh, price[no_ev], raw[no_ev], events=ev)
    plain2 = pit(sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]], idx, no_ev, FUNDAMENTAL_MAX_AGE)
    n_new = int(((new / plain2 - 1).abs() > 1e-9).sum().sum())
    return {"v11_yontemi_bolunmesiz_degisen_hucre": n_old,
            "not": "v1.1 sayısı (6.568) ağırlıklı ortalama yedeğiyle hesaplanmıştı; burada yedeksiz dönem sonu sayısıyla yeniden sayıldı.",
            "neden_dagilimi_hucre": t.groupby("neden").hucre.sum().to_dict() if len(t) else {},
            "neden_dagilimi_sirket": t.neden.value_counts().to_dict() if len(t) else {},
            "aciklanamayan_hucre": int(t[t.neden.str.startswith("olay kaydı yok")].hucre.sum()) if len(t) else 0,
            "yeni_yontem_olay_kaydi_olmayan_hisse": int(len(no_ev)), "yeni_yontem_degisen_hucre": n_new}


def borc() -> dict:
    from radar.research.ratios import debt_by_filing
    from radar.research.road1 import load_fin
    fin = fundamentals.plain(load_fin())
    d = debt_by_filing(fin)
    d["yil"] = pd.to_datetime(d.accepted).dt.year
    amb = d[d.belirsiz]
    old_double = d.tur.isin(["LT (LTC içinde)", "LT+(DC-LTC)"])
    return {"rapor": int(len(d)), "tur_dagilimi": d.tur.value_counts().to_dict(),
            "belirsiz_pay": round(float(d.belirsiz.mean()), 4),
            "belirsiz_ust_alt_orani_medyan": round(float((amb.ust / amb.value).replace([np.inf], np.nan).median()), 4) if len(amb) else None,
            "eski_tanimda_cift_sayilan_rapor": int(old_double.sum()),
            "yila_gore_belirsiz_pay": d.groupby("yil").belirsiz.mean().round(4).to_dict()}


def main(parts: list[str]) -> dict:
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    p = panel.build()
    d = None
    for k in parts:
        try:
            if k == "bolunme":
                res[k], d = splits(p)
            elif k == "on_uc":
                res[k] = on_uc(p, d)
            elif k == "hucre":
                res[k] = hucre(p)
            elif k == "borc":
                res[k] = borc()
        except Exception as e:
            import traceback
            res[k] = {"hata": f"{type(e).__name__}: {e}", "iz": traceback.format_exc()[-2500:]}
        print(f"=== {k}", json.dumps(res[k], ensure_ascii=False, default=str)[:4000], flush=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return res


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else ["bolunme", "on_uc", "hucre", "borc"])

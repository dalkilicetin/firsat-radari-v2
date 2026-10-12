"""1. aşama: veri doğrulama ve çıkış senaryoları (ön kayıt v1.1, bölüm 1, 5, 6). Model eğitimi yok.

python -m radar.research.asama1 [bolunme,kalem,oran,tarih,eksik,cikis,neweywest]
Çıktı: reports/research/asama1.json (her kontrol: ölçü, kabul koşulu, sonuç, sapan durumlar)
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import fundamentals, panel
from radar.research.pit import to_friday

OUT = config.ROOT / "reports" / "research" / "asama1.json"
FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"


def _shares(p):
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    return sh, fundamentals.shares_wide(sh, p["price"], p["raw"])


# --- Bölünmeler ------------------------------------------------------------------------------------------------
def split_type(r: float) -> str:
    if r <= 0 or not np.isfinite(r) or r > 1000 or r < 1 / 1000:
        return "bozuk kayıt"
    if r >= 1.3:
        return "bölünme"
    if r <= 1 / 1.3:
        return "ters bölünme"
    return "küçük oranlı düzeltme (hisse temettüsü / ayrılma olası)"


def splits(p: dict) -> dict:
    """Yahoo bölünme kayıtlarındaki her olay için ayrı ayrı: oran geçerliliği, tarih (işlem fiyatı o hafta oranla sıçradı mı),
    düzeltilmiş fiyat sürekliliği, hisse sayısı düzeltmesi (a), piyasa değeri sürekliliği (b), ilk kapak sayısı (c).
    Tüm olaylar reports/research/asama1_bolunme.csv'ye yazılır; bozuk kayıtlar silinmez, sınıflandırılır."""
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str))
    act = sec[sec.status == "aktif"].drop_duplicates("symbol")[["symbol", "cik"]]
    ev = archive.load("prices", columns=["symbol", "date", "split_ratio"])
    ev = ev[ev.split_ratio.notna() & (ev.split_ratio != 1)].merge(act, on="symbol")
    ev = ev[ev.date >= "2010-01-01"]
    price, raw = p["price"], p["raw"]
    sh_long, shares = _shares(p)
    sh_long = sh_long.assign(cik=sh_long.cik.astype(str), fri=to_friday(sh_long.accepted))
    by_cik = {c: g.sort_values("fri") for c, g in sh_long.groupby("cik")}
    empty = sh_long.iloc[:0]
    mcap = shares * raw
    idx = price.index
    rows = []
    for r in ev.itertuples():
        c, ratio = r.cik, float(r.split_ratio)
        row = {"cik": c, "sembol": r.symbol, "tarih": str(r.date.date()), "oran": ratio, "tur": split_type(ratio)}
        if row["tur"] == "bozuk kayıt" or c not in price.columns:
            row["durum"] = "oran geçersiz" if row["tur"] == "bozuk kayıt" else "evrende değil"
            rows.append(row)
            continue
        i = idx.searchsorted(r.date)
        if i < 1 or i >= len(idx):
            row["durum"] = "panel dışı tarih"
            rows.append(row)
            continue
        t0, t1 = idx[i - 1], idx[i]
        g = by_cik.get(c, empty)
        row["yeni_rapor_ayni_hafta"] = bool(((g.fri > t0) & (g.fri <= t1)).any())
        pr = price.at[t1, c] / price.at[t0, c] - 1
        rr = raw.at[t1, c] / raw.at[t0, c] - 1
        row["duz_fiyat_getirisi"] = pr
        row["tarih_hatasi"] = (1 + rr) * ratio / (1 + pr) - 1 if np.isfinite(pr) and np.isfinite(rr) else np.nan  # 0: ham fiyat tam o hafta oranla değişti
        s0, s1, m0, m1 = shares.at[t0, c], shares.at[t1, c], mcap.at[t0, c], mcap.at[t1, c]
        row["hisse_once"], row["hisse_sonra"] = s0, s1
        row["a_oran_hatasi"] = s1 / s0 / ratio - 1 if s0 and np.isfinite(s0) else np.nan
        row["b_sureklilik_puan"] = (m1 / m0 - 1) - pr if m0 and np.isfinite(m0) else np.nan
        nxt = g[g.fri > t1].head(1)
        row["c_kapak_farki"] = np.nan
        if len(nxt) and (nxt.fri.iloc[0] - t1).days <= 200:
            j = idx.searchsorted(nxt.fri.iloc[0]) - 1
            ours = shares.at[idx[j], c] if 0 <= j < len(idx) else np.nan
            if ours and np.isfinite(ours):
                row["c_kapak_farki"] = ours / nxt.value.iloc[0] - 1
        row["durum"] = "ölçüldü"
        rows.append(row)
    d = pd.DataFrame(rows)
    d.to_csv(config.ROOT / "reports" / "research" / "asama1_bolunme.csv", index=False)
    checks = {"tarih": ("tarih_hatasi", 0.02, "ham fiyat bölünme haftasında oranla değişti (±%2)"),
              "fiyat": ("duz_fiyat_getirisi", 0.5, "düzeltilmiş fiyatta bölünme haftası sıçraması yok (|getiri| < %50)"),
              "a": ("a_oran_hatasi", 0.01, "hisse sayısı düzeltmesi = bilinen oran (±%1)"),
              "b": ("b_sureklilik_puan", 0.02, "piyasa değeri değişimi = düzeltilmiş fiyat getirisi (≤ 2 puan)"),
              "c": ("c_kapak_farki", 0.02, "bölünme sonrası ilk kapak sayısı = bizim düzeltilmiş sayımız (±%2)")}
    res = {"olay_toplam": int(len(d)), "tur_dagilimi": d.tur.value_counts().to_dict(), "durum_dagilimi": d.durum.value_counts().to_dict(),
           "not": "(a) yapısal olarak döngüseldir (düzeltme oranı fiyat serisinden gelir); bağımsız kanıt (b) ve özellikle (c)'dir. "
                  "Aynı hafta yeni rapor gelen olaylarda (a) ve (b) ayrıştırılamaz, ayrı sayılır. Küçük oranlı düzeltmelerde hisse sayısı "
                  "değişmediği için (a) uygulanmaz.",
           "turler": {}}
    m = d[d.durum == "ölçüldü"]
    for tur, g in m.groupby("tur"):
        out = {"olay": int(len(g)), "ayni_hafta_yeni_rapor": int(g.yeni_rapor_ayni_hafta.sum())}
        for k, (col, tol, desc) in checks.items():
            gg = g if k in ("tarih", "fiyat", "c") else g[~g.yeni_rapor_ayni_hafta]
            if tur.startswith("küçük") and k == "a":
                continue
            v = gg[col].dropna()
            ok = v.abs() <= tol if k != "fiyat" else v.abs() < tol
            out[k] = {"kontrol": desc, "olcum": int(len(v)), "basarisiz": int((~ok).sum()), "saglayan_pay": float(ok.mean()) if len(v) else None}
        res["turler"][tur] = out
    # bölünmesiz hisselerde düzeltme değer değiştirmemeli
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    split_ciks = set(d.cik)
    others = [c for c in price.columns if c not in split_ciks]
    plain_w = pit(sh_long.rename(columns={"accepted": "date"})[["cik", "date", "value"]], idx, pd.Index(others), FUNDAMENTAL_MAX_AGE)
    diff = (shares[others] / plain_w - 1).abs()
    res["bolunmesiz"] = {"hisse": len(others), "hucre": int(diff.notna().sum().sum()), "farkli_hucre": int((diff > 1e-9).sum().sum()),
                         "en_buyuk_fark": float(np.nanmax(diff.to_numpy())) if diff.notna().any().any() else 0.0}
    return res


# --- Tablo kalemleri: şirketlerin 10-K rakamları (milyon $) ---------------------------------------------------
KNOWN = {  # (cik, mali yıl sonu): {kalem: değer}
    ("320193", "2019-09-28"): {"Gelir": 260174, "Faaliyet kârı": 63930, "Net kâr": 55256, "Varlıklar": 338516, "Özsermaye": 90488},
    ("320193", "2023-09-30"): {"Gelir": 383285, "Faaliyet kârı": 114301, "Net kâr": 96995, "Varlıklar": 352583, "Özsermaye": 62146},
    ("789019", "2019-06-30"): {"Gelir": 125843, "Faaliyet kârı": 42959, "Net kâr": 39240, "Varlıklar": 286556, "Özsermaye": 102330},
    ("789019", "2023-06-30"): {"Gelir": 211915, "Faaliyet kârı": 88523, "Net kâr": 72361, "Varlıklar": 411976, "Özsermaye": 206223},
    ("21344", "2019-12-31"): {"Gelir": 37266, "Faaliyet kârı": 10086, "Net kâr": 8920, "Varlıklar": 86381, "Özsermaye": 18981},
    ("21344", "2023-12-31"): {"Gelir": 45754, "Faaliyet kârı": 11311, "Net kâr": 10714, "Varlıklar": 97703, "Özsermaye": 25941},
    ("34088", "2019-12-31"): {"Gelir": 264938, "Net kâr": 14340, "Varlıklar": 362597, "Özsermaye": 191650},
    ("34088", "2022-12-31"): {"Gelir": 413680, "Net kâr": 55740, "Varlıklar": 369067, "Özsermaye": 195049},
    ("1045810", "2020-01-26"): {"Gelir": 10918, "Faaliyet kârı": 2846, "Net kâr": 2796, "Varlıklar": 17315, "Özsermaye": 12204},
    ("1045810", "2024-01-28"): {"Gelir": 60922, "Faaliyet kârı": 32972, "Net kâr": 29760, "Varlıklar": 65728, "Özsermaye": 42978},
}
TABLO = {"Gelir": ("gelir tablosu", "dönem içi, 12 ay"), "Faaliyet kârı": ("gelir tablosu", "dönem içi, 12 ay"),
         "Net kâr": ("gelir tablosu", "dönem içi, 12 ay"), "Varlıklar": ("bilanço", "dönem sonu"), "Özsermaye": ("bilanço", "dönem sonu")}
SIRKET = {"320193": "Apple", "789019": "Microsoft", "21344": "Coca-Cola", "34088": "Exxon Mobil", "1045810": "NVIDIA"}
TAGS = {"Gelir": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                  "RevenueFromContractWithCustomerIncludingAssessedTax"],
        "Faaliyet kârı": ["OperatingIncomeLoss"], "Net kâr": ["NetIncomeLoss", "ProfitLoss"], "Varlıklar": ["Assets"],
        "Özsermaye": ["StockholdersEquity"]}


def line_items() -> dict:
    fin = fundamentals.plain(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "form", "uom"]))
    fin = fin.assign(cik=fin.cik.astype(str))
    rows = []
    for (cik, fy), items in KNOWN.items():
        f = fin[(fin.cik == cik)]
        fyd = pd.Timestamp(fy)
        for k, exp in items.items():
            q = 0 if k in ("Varlıklar", "Özsermaye") else 4
            cand = f[f.tag.isin(TAGS[k]) & (f.qtrs == q) & ((pd.to_datetime(f.ddate) - fyd).abs() <= pd.Timedelta(days=7))]
            cand = cand.assign(prio=cand.tag.map({t: i for i, t in enumerate(TAGS[k])})).sort_values(["prio", "accepted"])
            got = float(cand.value.iloc[0]) / 1e6 if len(cand) else np.nan
            err = got / exp - 1 if np.isfinite(got) else np.nan
            top = cand.iloc[0] if len(cand) else None
            rows.append({"sirket": SIRKET[cik], "cik": cik, "mali_yil_sonu": fy, "kalem": k, "kaynak": f"{SIRKET[cik]} 10-K, mali yıl {fy[:4]}, {TABLO[k][0]}",
                         "olcum_niteligi": TABLO[k][1], "birim": "milyon USD", "10-K": exp,
                         "arsiv_etiketi": top.tag if top is not None else None, "arsiv_belge": top.adsh if top is not None else None,
                         "arsiv_belge_turu": top.form if top is not None else None, "arsiv_birimi": top.uom if top is not None else None,
                         "arsiv": round(got, 1) if np.isfinite(got) else None,
                         "fark": None if not np.isfinite(err) else round(err, 5), "gecti": bool(np.isfinite(err) and abs(err) <= 0.005)})
    d = pd.DataFrame(rows)
    return {"kosul": "±%0,5", "olcum": int(len(d)), "gecen": int(d.gecti.sum()), "satirlar": d.to_dict(orient="records"),
            "sinir": "5 şirket × 2 yıl × en çok 5 kalem: arşivin bu kalemleri doğru okuduğunu gösterir; tüm veri kümesinin doğruluğunu kanıtlamaz."}


def shares_fallback(p: dict) -> dict:
    """Dönem sonu (dolaşımdaki) hisse sayısı ile ağırlıklı ortalama hisse sayısı.
    1) ikisinin de bulunduğu şirket ve rapor sayısı; 2) mutlak ve göreli farkların dağılımı; 3) farkın şirket büyüklüğü ve
    hisse ihracı / geri alımla ilişkisi; 4) yedek (ağırlıklı ortalama) kullanılınca çerçevede etkilenen satırlar ve piyasa
    değerine dayalı sıralamanın ne kadar değiştiği. Belirti seçimi ve model yok; yalnızca düzeltmenin etkisi ölçülür."""
    fin = fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"])
    plain = fin[fin.segments == ""]
    w = plain[(plain.tag == "WeightedAverageNumberOfSharesOutstandingBasic") & (plain.qtrs > 0)]
    w = w[w.ddate == w.groupby("adsh").ddate.transform("max")].sort_values(["adsh", "qtrs"]).drop_duplicates("adsh")
    o = fundamentals.shares_outstanding(fin[fin.tag.isin(fundamentals.SHARE_TAGS) | (fin.tag == "__yok__")])  # yedeksiz dönem sonu sayısı
    o_adsh = fin[fin.tag.isin(fundamentals.SHARE_TAGS)].groupby("adsh").agg(cik=("cik", "first"), accepted=("accepted", "first"))
    o_val = fin[fin.tag.isin(fundamentals.SHARE_TAGS)].groupby("adsh").value.max()
    both = w.set_index("adsh")[["cik", "accepted", "value"]].rename(columns={"value": "agirlikli"}).join(o_val.rename("donem_sonu"), how="inner")
    both = both[(both.donem_sonu > 0) & (both.agirlikli > 0)].copy()
    both["goreli"] = both.agirlikli / both.donem_sonu - 1
    both["mutlak"] = (both.agirlikli - both.donem_sonu).abs()
    # büyüklük: rapor anındaki piyasa değeri dilimi; ihraç/geri alım: dönem sonu sayısının bir yıl önceki rapora göre değişimi
    both = both.sort_values(["cik", "accepted"])
    both["yillik_degisim"] = both.groupby("cik").donem_sonu.pct_change(4, fill_method=None)
    raw = p["raw"]
    fri = to_friday(both.accepted)
    ri = raw.index.searchsorted(fri.to_numpy()) - 1
    ci = raw.columns.get_indexer(both.cik.astype(int).astype(str))
    okk = (ri >= 0) & (ci >= 0)
    px = np.full(len(both), np.nan)
    px[okk] = raw.to_numpy()[ri[okk], ci[okk]]
    both["piyasa_degeri"] = px * both.donem_sonu
    both["buyukluk_dilimi"] = pd.qcut(both.piyasa_degeri.rank(method="first"), 5, labels=["en küçük", "2", "3", "4", "en büyük"])
    both["sermaye_hareketi"] = pd.cut(both.yillik_degisim, [-np.inf, -0.03, 0.10, np.inf], labels=["geri alım (≤ −%3)", "durağan", "ihraç (≥ +%10)"])
    by_size = both.groupby("buyukluk_dilimi", observed=True).goreli.apply(lambda x: x.abs().median()).round(4).to_dict()
    by_cap = both.groupby("sermaye_hareketi", observed=True).goreli.apply(lambda x: x.abs().median()).round(4).to_dict()
    # 4) çerçevede etki: yedek kullanılan şirketlerin satırları ve piyasa değeri sırasındaki değişim (ikisi de bulunan raporlarda simülasyon)
    have_out = set(fin[fin.tag.isin(fundamentals.SHARE_TAGS)].cik.astype(str))
    full = fundamentals.shares_outstanding(fin)
    fb = set(full.cik.astype(str)) - have_out
    df = pd.read_parquet(FRAME, columns=["tarih", "yil"])
    rows_fb = df.index.astype(str).isin(fb)
    sim = both.dropna(subset=["piyasa_degeri"]).copy()
    sim["yil"] = pd.to_datetime(sim.accepted).dt.year
    sim["pd_agirlikli"] = sim.piyasa_degeri * (1 + sim.goreli)
    rank_shift = sim.groupby("yil").apply(lambda g: (g.piyasa_degeri.rank(pct=True) - g.pd_agirlikli.rank(pct=True)).abs().median())
    return {
        "1_ikisi_de_bulunan": {"sirket": int(both.cik.nunique()), "rapor": int(len(both))},
        "2_fark_dagilimi": {"goreli": both.goreli.describe(percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(4).to_dict(),
                            "mutlak_hisse_medyan": float(both.mutlak.median()), "pay_mutlak_5_icinde": float((both.goreli.abs() <= 0.05).mean()),
                            "pay_mutlak_20_disinda": float((both.goreli.abs() > 0.2).mean())},
        "3_iliski": {"buyukluk_dilimine_gore_medyan_mutlak_goreli_fark": {str(k): v for k, v in by_size.items()},
                     "sermaye_hareketine_gore_medyan_mutlak_goreli_fark": {str(k): v for k, v in by_cap.items()}},
        "4_cerceve_etkisi": {"yedek_kullanan_sirket": len(fb), "etkilenen_cerceve_satiri": int(rows_fb.sum()),
                             "etkilenen_pay": float(rows_fb.mean()),
                             "etkilenen_belirtiler": ["kucuk_boyut", "kazanc_getirisi", "serbest_nakit_getirisi", "defter_fiyat", "satis_fiyat",
                                                      "favok_fd", "temettu_verimi", "nakit_piyasa", "altman_z", "hisse_sayisi_degisimi",
                                                      "piotroski_f", "geri_alim_getirisi", "icerden_alim_tutar_piyasa_degeri", "devralma_olasiligi"],
                             "simulasyon_piyasa_degeri_sirasi_medyan_mutlak_kayma": {int(k): round(float(v), 4) for k, v in rank_shift.items()},
                             "simulasyon_notu": "İki ölçümün de bulunduğu raporlarda dönem sonu yerine ağırlıklı ortalama kullanılsaydı piyasa "
                                                "değerinin yıl içi yüzdelik sırası ne kadar kayardı (0,01 = 1 yüzdelik puan)."},
        "not": "Ağırlıklı ortalama dönem içi bir ortalamadır (EPS gibi dönemsel hesaplar için); piyasa değeri için doğru ölçü dönem sonu "
               "sayısıdır. Yedeğin kullanılıp kullanılmayacağı kullanıcı kararıdır.",
    }


# --- Oranlar: bileşenlerden bağımsız yeniden hesap ------------------------------------------------------------
def ratios_check(p: dict, n: int = 200) -> dict:
    from radar.research import ratios as R
    from radar.research.road1 import signals as r1
    fin = fundamentals.plain(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "form"]))
    fin = fin.assign(cik=fin.cik.astype(str), fri=to_friday(fin.accepted))
    fin_by = {c: g for c, g in fin.groupby("cik")}
    rng = np.random.default_rng(20261012)
    dates = p["price"].index[(p["price"].index >= "2012-01-01") & (p["price"].index <= "2024-12-31")]
    cols = p["price"].columns
    sub_cols = pd.Index(rng.choice(cols, size=min(600, len(cols)), replace=False))
    sub = {"price": p["price"][sub_cols], "raw": p["raw"][sub_cols]}
    rs = R.signals(sub)
    r1s = r1(sub)
    _, shares = _shares(sub)
    mcap = shares * sub["raw"]

    def latest(cik, t, tags, qtrs):
        f = fin_by.get(cik, fin.iloc[:0])
        f = f[f.tag.isin(tags) & (f.qtrs == qtrs) & (f.fri <= t)]
        if f.empty:
            return np.nan
        f = f[f.accepted == f.accepted.max()]
        f = f[f.ddate == f.ddate.max()]
        f = f.assign(prio=f.tag.map({x: i for i, x in enumerate(tags)})).sort_values("prio")
        return float(f.value.iloc[0])
    def div(a, b):
        if b == 0:
            raise ZeroDivisionError
        return a / b
    checks = {"brut_marj": lambda c, t: div(latest(c, t, ["GrossProfit"], 4), latest(c, t, R.REVENUE, 4)),
              "faaliyet_marji": lambda c, t: div(latest(c, t, ["OperatingIncomeLoss"], 4), latest(c, t, R.REVENUE, 4)),
              "cari_oran": lambda c, t: div(latest(c, t, ["AssetsCurrent"], 0), latest(c, t, ["LiabilitiesCurrent"], 0)),
              "kazanc_getirisi": lambda c, t: div(latest(c, t, ["NetIncomeLoss", "ProfitLoss"], 4), mcap.at[t, c]),
              "defter_fiyat": lambda c, t: div(latest(c, t, R.EQUITY, 0), mcap.at[t, c])}
    src = {k: (r1s[k] if k == "kazanc_getirisi" else rs[k]) for k in checks}
    out = {}
    clip = {"brut_marj": (-2, 1), "faaliyet_marji": (-5, 1), "cari_oran": (0, 20), "kazanc_getirisi": (-2, 2), "defter_fiyat": (-5, 5)}
    for k, fn in checks.items():
        res, cnt = [], {"denenen": 0, "bizde_eksik": 0, "bagimsiz_eksik_bilesen": 0, "sifir_payda": 0, "kirpma_disi": 0,
                        "ikisi_de_eksik": 0, "hata": 0}
        while len(res) < n and cnt["denenen"] < n * 30:
            cnt["denenen"] += 1
            c, t = str(rng.choice(sub_cols)), dates[rng.integers(len(dates))]
            ours = src[k].at[t, c] if c in src[k] else np.nan
            try:
                ind = fn(c, t)
            except ZeroDivisionError:
                cnt["sifir_payda"] += 1
                continue
            except Exception:
                cnt["hata"] += 1
                continue
            if np.isfinite(ind) and ind == 0 and k in ("kazanc_getirisi",):
                pass
            if not np.isfinite(ours) and not np.isfinite(ind):
                cnt["ikisi_de_eksik"] += 1
                continue
            if not np.isfinite(ours):
                cnt["bizde_eksik"] += 1  # bağımsız hesap var, bizde yok: kapsama farkı
                continue
            if not np.isfinite(ind):
                cnt["bagimsiz_eksik_bilesen"] += 1
                continue
            lo, hi = clip[k]
            if not (lo < ind < hi):
                cnt["kirpma_disi"] += 1  # bizde kırpılmış uç değer; karşılaştırılmaz
                continue
            res.append({"cik": c, "tarih": str(t.date()), "bizim": float(ours), "bagimsiz": float(ind),
                        "mutlak_hata": float(abs(ours - ind)), "goreli_hata": float(ours / ind - 1) if ind else np.nan})
        d = pd.DataFrame(res)
        ok = d.goreli_hata.abs() <= 0.01
        out[k] = {"kosul": "göreli ±%1, karşılaştırılanların ≥ %99'u", "sayim": cnt, "karsilastirilan": int(len(d)),
                  "tolerans_icinde": int(ok.sum()), "saglayan_pay": float(ok.mean()) if len(d) else None,
                  "goreli_hata_dagilimi": d.goreli_hata.abs().describe(percentiles=[0.5, 0.9, 0.99]).round(5).to_dict() if len(d) else {},
                  "mutlak_hata_medyan": float(d.mutlak_hata.median()) if len(d) else None,
                  "sapanlar": d[~ok].head(15).round(5).to_dict(orient="records")}
    out["not"] = ("Örneklem sabit tohumla (20261012) rastgele şirket-tarih çiftlerinden; eksik bileşenli ve uç değerli kayıtlar atılmaz, "
                  "ayrı sayılır. Payda sıfırsa bağımsız hesap 'sıfır payda' sayılır (bizim kodda payda > 0 şartı var).")
    return out


# --- Ölçüm tarihleri ve pencereler ----------------------------------------------------------------------------
def dates_table(p: dict) -> dict:
    idx = p["price"].index
    rows = []
    for y in range(2013, 2027):
        for m in (1, 4, 7, 10):
            first = idx[(idx.year == y) & (idx.month == m)]
            if len(first):
                rows.append(first[0])
    rows = pd.DatetimeIndex(rows)
    tab = pd.DataFrame({"olcum_tarihi": rows[:-1], "sonraki_olcum": rows[1:]})
    tab["veri_kesim_fiyat"] = tab.olcum_tarihi  # o Cuma'nın kapanışı
    tab["veri_kesim_sec"] = tab.olcum_tarihi - pd.Timedelta(days=1)  # SEC: Perşembe gün sonuna kadar kabul edilenler (to_friday kuralı)
    tab["getiri_baslangic"] = tab.olcum_tarihi
    tab["getiri_bitis"] = tab.sonraki_olcum
    tab["hafta"] = ((tab.getiri_bitis - tab.getiri_baslangic).dt.days // 7).astype(int)
    tab["onceki_ile_cakisma_gun"] = [0] + [max(0, (a - b).days) for a, b in zip(tab.getiri_bitis.iloc[:-1], tab.getiri_baslangic.iloc[1:])]
    tab["sabit_13h_olsaydi_cakisma_gun"] = [0] + [max(0, (a + pd.Timedelta(weeks=13) - b).days)
                                                  for a, b in zip(tab.getiri_baslangic.iloc[:-1], tab.getiri_baslangic.iloc[1:])]
    fmt = lambda x: str(pd.Timestamp(x).date())
    return {"donem": int(len(tab)), "hafta_dagilimi": tab.hafta.value_counts().sort_index().to_dict(),
            "cakisma": int((tab.onceki_ile_cakisma_gun > 0).sum()),
            "sabit_13_hafta_olsaydi_cakisan": int((tab.sabit_13h_olsaydi_cakisma_gun > 0).sum()),
            "not": "Pencere çakışması ile veri sızıntısı ayrı sorunlardır; sızıntı belirti_dogrulama (T4 zamanlama, T5 sızıntı) ile ayrıca sınanır.",
            "tablo": [{k: (fmt(v) if isinstance(v, pd.Timestamp) else int(v)) for k, v in r.items()} for r in tab.to_dict(orient="records")]}


# --- Eksik veri dağılımı --------------------------------------------------------------------------------------
def missing() -> dict:
    df = pd.read_parquet(FRAME)
    meta = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari", "getiri_13h", "getiri_26h", "getiri_52h", "getiri_104h"}
    feats = [c for c in df.columns if c not in meta and pd.api.types.is_numeric_dtype(df[c])]
    q = df.groupby("tarih").fiyat_seviyesi.transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=False))
    out = {}
    for f in feats:
        nn = df[f].notna()
        by_q = nn.groupby(q).mean()
        by_y = nn.groupby(df.yil).mean()
        by_s = nn.groupby(df.sektor).mean()
        out[f] = {"dolu": round(float(nn.mean()), 3), "fiyat_dilimi_en_dusuk": round(float(by_q.min()), 3),
                  "fiyat_dilimi_en_yuksek": round(float(by_q.max()), 3), "yil_en_dusuk": round(float(by_y.min()), 3),
                  "yil_en_yuksek": round(float(by_y.max()), 3), "sektor_en_dusuk": round(float(by_s.min()), 3),
                  "dengesiz": bool(by_q.max() - by_q.min() > 0.3)}
    return {"belirti": len(out), "fiyat_dilimine_gore_dengesiz": [k for k, v in out.items() if v["dengesiz"]], "ayrinti": out}


# --- Çıkış senaryoları ----------------------------------------------------------------------------------------
def exit_classes(p: dict) -> pd.DataFrame:
    """Her borsadan çıkan şirket için son geçerli fiyatın kaynağı ve çıkış nedeni.
    Fiyat kaynağı: A = son fiyat günlük fiyat arşivinde (Yahoo, borsadan çıkmışlar) aynı hafta ve ±%1 fiyatla bulundu;
    B = son fiyat bir SEC FTD kaydında aynı hafta ve ±%1 fiyatla bulundu (kaynak doğrulandı, kayıt seyrek);
    C = kaynak doğrulanamadı. Neden: D = iflas (8-K 1.03; ön kayıt gereği çıkış değeri 0), E = diğer çıkışlar
    (satın alma, birleşme, borsa değişikliği vb.; ayrım mevcut veriyle yapılamıyor)."""
    price, sec = p["price"], p["securities"]
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    gone = s[s.status == "çıktı"]
    daily = archive.load("prices_exited", columns=["cik", "date", "close", "adjclose"])
    daily = daily.assign(cik=daily.cik.astype(str), fri=to_friday(daily.date - pd.Timedelta(days=1)))
    dmap = {c: g for c, g in daily.groupby("cik")}
    ftd = archive.load("ftd", columns=["settle_date", "symbol", "price"])
    ftd = ftd[ftd.price > 0]
    ftd = ftd.assign(date=ftd.settle_date - pd.offsets.BDay(1))
    ftd = ftd.assign(fri=to_friday(ftd.date - pd.Timedelta(days=1)))
    fmap = {sym: g for sym, g in ftd.groupby("symbol")}
    rows = []
    for c, r in gone.iterrows():
        if c not in price.columns:
            continue
        ser = price[c][price.index <= r.end + pd.Timedelta(days=10)].dropna()
        rawser = p["raw"][c][p["raw"].index <= r.end + pd.Timedelta(days=10)].dropna()
        if ser.empty:
            rows.append({"cik": c, "sembol": r.symbol, "kaynak": "C", "neden": "D" if r.bankrupt else "E", "not": "panelde fiyat yok"})
            continue
        lw, lraw = rawser.index[-1], float(rawser.iloc[-1])
        g, f = dmap.get(c), fmap.get(r.symbol)
        ma = g[(g.fri == lw) & (np.abs(g.close / lraw - 1) <= 0.01)] if g is not None else []
        mb = f[(f.fri == lw) & (np.abs(f.price / lraw - 1) <= 0.01)] if f is not None else []
        src = "A" if len(ma) else ("B" if len(mb) else "C")
        rows.append({"cik": c, "sembol": r.symbol, "cikis": str(pd.Timestamp(r.end).date()), "son_fiyat_haftasi": str(lw.date()),
                     "son_islem_fiyati": lraw, "kaynak": src, "neden": "D" if r.bankrupt else "E",
                     "a_aday": int(len(ma)), "b_aday": int(len(mb)), "ikisi_de_uydu": bool(len(ma) and len(mb)),
                     "coklu_aday": bool(len(ma) > 1 or len(mb) > 1)})
    d = pd.DataFrame(rows)
    d.to_csv(config.ROOT / "reports" / "research" / "asama1_cikislar.csv", index=False)
    return d


def exits(p: dict, tab: dict) -> dict:
    price, sec = p["price"], p["securities"]
    cls = exit_classes(p).set_index("cik")
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik").reindex(price.columns)
    member = panel.membership(sec, price.index, price.columns) & price.notna()
    rows = []
    for w in tab["tablo"]:
        t0, t1 = pd.Timestamp(w["getiri_baslangic"]), pd.Timestamp(w["getiri_bitis"])
        if t0.year > 2024:
            continue
        u = member.loc[t0] & (p["raw"].loc[t0] >= 1)
        cols = price.columns[u.to_numpy()]
        end = s.end.reindex(cols)
        ex = [c for c in cols[(end > t0).to_numpy() & (end <= t1).to_numpy()] if c in cls.index]
        base = price.loc[t1, cols] / price.loc[t0, cols] - 1
        ev = {}
        for c in ex:
            ser = price[c][(price.index > t0) & (price.index <= s.at[c, "end"] + pd.Timedelta(days=10))].dropna()
            last = ser.iloc[-1] if len(ser) else price.at[t0, c]
            ev[c] = (last / price.at[t0, c] - 1, cls.at[c, "kaynak"], cls.at[c, "neden"])
        out = {"donem": w["getiri_baslangic"], "evren": int(len(cols)), "cikan": len(ex)}
        for k in ("A", "B", "C"):
            out[f"cikan_{k}"] = sum(1 for v in ev.values() if v[1] == k and v[2] == "E")
        out["cikan_D"] = sum(1 for v in ev.values() if v[2] == "D")
        for name, mult in (("s1", 1.0), ("s2", 0.5), ("s3", 0.0)):
            for which in ("BC", "B", "C"):
                r = base.copy()
                for c, (ret, src, why) in ev.items():
                    if why == "D":
                        r[c] = -1.0
                    elif src in which:
                        r[c] = (1 + ret) * mult - 1  # alış fiyatına göre: son fiyat × çarpan
                    else:
                        r[c] = ret
                out[f"{name}_{which}"] = float(r.mean())
        rows.append(out)
    d = pd.DataFrame(rows)
    yr = d.groupby(d.donem.str[:4])
    ann = {col: yr[col].apply(lambda x: np.prod(1 + x) - 1).mean() for col in d.columns if col[:2] in ("s1", "s2", "s3")}
    n = len(cls)
    return {"siniflar": cls.groupby(["kaynak", "neden"]).size().rename("sirket").reset_index().to_dict(orient="records"),
            "pay": {k: round(float((cls.kaynak == k).mean()), 4) for k in ("A", "B", "C")}, "sirket": int(n),
            "ikisi_de_uydu": int(cls.get("ikisi_de_uydu", pd.Series(dtype=bool)).fillna(False).sum()),
            "coklu_aday": int(cls.get("coklu_aday", pd.Series(dtype=bool)).fillna(False).sum()),
            "tolerans_kurali": "Panelin son işlem fiyatı (bölünmeden arındırılmış ham kapanış, yuvarlanmamış) ile aday kaydın fiyatı "
                               "(Yahoo kapanışı ya da FTD fiyatı, sent hassasiyetinde) arasında |aday/son − 1| ≤ 0,01; aynı Cuma haftası. "
                               "Birden çok aday uyarsa kaynak yine doğrulanmış sayılır, kayıt 'çoklu aday' olarak işaretlenir.",
            "sinir": "C grubunda verinin eksik olması ile gerçek ekonomik kayıp mevcut veriyle ayırt edilemez; satın alma ile borsadan "
                     "atılma (E içinde) ayrımı da yapılamıyor.",
            "sinif_tanimi": exit_classes.__doc__,
            "evren_esit_agirlik_yillik": {k: round(float(v), 5) for k, v in ann.items()},
            "not": "Evren düzeyinde etki (model yok). s1/s2/s3 = son fiyat / son fiyat × 0,5 / 0; '_B' yalnızca FTD'si doğrulanan, '_C' yalnızca "
                   "kaynağı belirsiz, '_BC' ikisi birden değiştirilir. Portföy düzeyindeki etki 3a aşamasında raporlanır.",
            "donemler": d.round(5).to_dict(orient="records")}


# --- Newey–West doğrulaması -----------------------------------------------------------------------------------
def newey_west(y: np.ndarray, X: np.ndarray, lags: int = 4) -> tuple[np.ndarray, np.ndarray]:
    """EKK katsayıları ve Bartlett çekirdekli HAC standart hataları (küçük örneklem düzeltmesi yok)."""
    A = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(A, y, rcond=None)[0]
    e = y - A @ b
    XtX_inv = np.linalg.inv(A.T @ A)
    S = (A * e[:, None]).T @ (A * e[:, None])
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        G = (A[L:] * e[L:, None]).T @ (A[:-L] * e[:-L, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    return b, np.sqrt(np.diag(V))


def nw_loop(y, X, lags):
    """Bağımsız uygulama: açık döngülerle toplam (matris kısayolu yok)."""
    A = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(A, y, rcond=None)[0]
    e = y - A @ b
    k = A.shape[1]
    S = np.zeros((k, k))
    for t in range(len(y)):
        S += e[t] ** 2 * np.outer(A[t], A[t])
    for L in range(1, lags + 1):
        w = 1 - L / (lags + 1)
        for t in range(L, len(y)):
            S += w * e[t] * e[t - L] * (np.outer(A[t], A[t - L]) + np.outer(A[t - L], A[t]))
    Ai = np.linalg.inv(A.T @ A)
    return np.sqrt(np.diag(Ai @ S @ Ai))


def nw_check() -> dict:
    """Elle örnek + rastgele durumlar: gecikme 0–6, gözlem 8–80, 1–6 açıklayıcı; matris uygulaması döngülü uygulamayla aynı olmalı.
    Gecikme 0'da sonuç White (değişen varyansa dayanıklı) hatasına eşit olmalı."""
    rng = np.random.default_rng(20261012)
    cases, fails = 0, []
    for lags in range(0, 7):
        for n in (8, 20, 48, 80):
            for k in (1, 3, 6):
                if n <= k + 2 + lags:
                    continue
                X = rng.normal(size=(n, k))
                y = X @ rng.normal(size=k) + np.cumsum(rng.normal(size=n)) * 0.3  # seri korelasyonlu hata
                _, se = newey_west(y, X, lags)
                se2 = nw_loop(y, X, lags)
                cases += 1
                if not np.allclose(se, se2, rtol=1e-10, atol=1e-12):
                    fails.append({"gecikme": lags, "gozlem": n, "aciklayici": k})
    

    """Elle hesaplanabilir örnek: tek değişkenli, 6 gözlem, gecikme 1 — matris formülüyle döngülü toplam formülü aynı olmalı."""
    y = np.array([1.0, 2.0, 1.5, 3.0, 2.5, 4.0])
    x = np.array([0.0, 1.0, 1.0, 2.0, 2.0, 3.0])
    b, se = newey_west(y, x[:, None], lags=1)
    A = np.column_stack([np.ones(6), x])
    e = y - A @ b
    S = np.zeros((2, 2))
    for t in range(6):
        S += e[t] ** 2 * np.outer(A[t], A[t])
    for t in range(1, 6):
        S += 0.5 * e[t] * e[t - 1] * (np.outer(A[t], A[t - 1]) + np.outer(A[t - 1], A[t]))
    Ai = np.linalg.inv(A.T @ A)
    se_manual = np.sqrt(np.diag(Ai @ S @ Ai))
    return {"elle_ornek": {"katsayi": b.round(6).tolist(), "se_fonksiyon": se.round(8).tolist(), "se_elle": se_manual.round(8).tolist(),
                           "gecti": bool(np.allclose(se, se_manual))},
            "rastgele_durum": cases, "basarisiz_durum": fails,
            "gecti": bool(np.allclose(se, se_manual)) and not fails,
            "sinir": "Uygulamanın formülle tutarlılığını gösterir; çok küçük örneklemde HAC hatalarının kendisi yanlı olabilir (yöntem sınırı)."}


def main(parts: list[str]) -> dict:
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    p = panel.build()
    tab = dates_table(p)
    steps = {"tarih": lambda: tab, "neweywest": nw_check, "kalem": line_items, "hisse_yedegi": lambda: shares_fallback(p), "bolunme": lambda: splits(p),
             "oran": lambda: ratios_check(p), "eksik": missing, "cikis": lambda: exits(p, tab)}
    for k in parts:
        try:
            res[k] = steps[k]()
        except Exception as e:
            res[k] = {"hata": f"{type(e).__name__}: {e}"}
        short = {kk: vv for kk, vv in res[k].items() if kk not in ("tablo", "satirlar", "ayrinti", "donemler", "sapanlar")} if isinstance(res[k], dict) else res[k]
        print(f"=== {k}", json.dumps(short, ensure_ascii=False, default=str)[:3000], flush=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return res


if __name__ == "__main__":
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else ["tarih", "neweywest", "kalem", "hisse_yedegi", "bolunme", "oran", "eksik", "cikis"])

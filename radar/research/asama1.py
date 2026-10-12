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
def splits(p: dict) -> dict:
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str))
    act = sec[sec.status == "aktif"].drop_duplicates("symbol")[["symbol", "cik"]]
    ev = archive.load("prices", columns=["symbol", "date", "split_ratio"])
    ev = ev[ev.split_ratio.notna() & (ev.split_ratio != 1)].merge(act, on="symbol")
    bad = ev[ev.split_ratio <= 0]
    ev = ev[(ev.split_ratio > 0) & (ev.date >= "2010-01-01")]
    price, raw = p["price"], p["raw"]
    sh_long, shares = _shares(p)
    sh_long = sh_long.assign(cik=sh_long.cik.astype(str), fri=to_friday(sh_long.accepted))
    by_cik = {c: g.sort_values("fri") for c, g in sh_long.groupby("cik")}
    empty = sh_long.iloc[:0]
    mcap = shares * raw
    idx = price.index
    rows = []
    for r in ev.itertuples():
        c = r.cik
        if c not in price.columns:
            continue
        i = idx.searchsorted(r.date)  # bölünme gününü içeren haftanın Cuması
        if i < 1 or i >= len(idx):
            continue
        t0, t1 = idx[i - 1], idx[i]
        g = by_cik.get(c, empty)
        new_filing = ((g.fri > t0) & (g.fri <= t1)).any()
        s0, s1 = shares.at[t0, c], shares.at[t1, c]
        m0, m1 = mcap.at[t0, c], mcap.at[t1, c]
        pr = price.at[t1, c] / price.at[t0, c] - 1
        a = s1 / s0 / r.split_ratio - 1 if s0 and np.isfinite(s0) else np.nan
        b = (m1 / m0 - 1) - pr if m0 and np.isfinite(m0) else np.nan
        # (c) bölünmeden sonraki ilk raporun kapak sayısı ↔ bir hafta önceki düzeltilmiş sayımız
        nxt = g[g.fri > t1].head(1)
        cc = np.nan
        if len(nxt):
            j = idx.searchsorted(nxt.fri.iloc[0]) - 1
            if 0 <= j < len(idx) and (nxt.fri.iloc[0] - t1).days <= 200:
                ours = shares.at[idx[j], c]
                cc = ours / nxt.value.iloc[0] - 1 if ours and np.isfinite(ours) else np.nan
        rows.append({"cik": c, "sembol": r.symbol, "tarih": str(r.date.date()), "oran": float(r.split_ratio), "yeni_rapor_ayni_hafta": bool(new_filing),
                     "a_oran_hatasi": a, "b_sureklilik_puan": b, "c_kapak_farki": cc})
    d = pd.DataFrame(rows)
    usable = d[~d.yeni_rapor_ayni_hafta]
    ok_a = usable.a_oran_hatasi.abs() <= 0.01
    ok_b = usable.b_sureklilik_puan.abs() <= 0.02
    ok_c = d.c_kapak_farki.dropna().abs() <= 0.02
    res = {
        "olay": int(len(d)), "bozuk_oran_kaydi": int(len(bad)), "ayni_hafta_yeni_rapor_disarida": int(d.yeni_rapor_ayni_hafta.sum()),
        "a": {"olcu": "hisse sayısı düzeltmesi / bilinen oran", "kosul": "±%1, ≥ %99", "olcum": int(usable.a_oran_hatasi.notna().sum()),
              "saglayan_pay": float(ok_a[usable.a_oran_hatasi.notna()].mean())},
        "b": {"olcu": "piyasa değeri değişimi − düzeltilmiş fiyat getirisi", "kosul": "≤ 2 puan, ≥ %99",
              "olcum": int(usable.b_sureklilik_puan.notna().sum()), "saglayan_pay": float(ok_b[usable.b_sureklilik_puan.notna()].mean())},
        "c": {"olcu": "bölünme sonrası ilk kapak sayısı / bizim düzeltilmiş sayı", "kosul": "±%2, ≥ %99",
              "olcum": int(ok_c.size), "saglayan_pay": float(ok_c.mean()) if ok_c.size else None},
        "not": "(a) yapısal olarak döngüseldir: düzeltme oranı fiyat serisindeki bölünmeden gelir; bağımsız kanıt (b) ve özellikle (c)'dir.",
    }
    for k, col, tol in (("a", "a_oran_hatasi", 0.01), ("b", "b_sureklilik_puan", 0.02)):
        bad_rows = usable[usable[col].abs() > tol]
        res[k]["sapanlar"] = bad_rows.head(40).round(4).to_dict(orient="records")
    res["c"]["sapanlar"] = d[d.c_kapak_farki.abs() > 0.02].head(40).round(4).to_dict(orient="records")
    res["c"]["sapan_dagilim"] = d.c_kapak_farki.dropna().describe(percentiles=[0.01, 0.05, 0.5, 0.95, 0.99]).round(4).to_dict()
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
TAGS = {"Gelir": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
                  "RevenueFromContractWithCustomerIncludingAssessedTax"],
        "Faaliyet kârı": ["OperatingIncomeLoss"], "Net kâr": ["NetIncomeLoss", "ProfitLoss"], "Varlıklar": ["Assets"],
        "Özsermaye": ["StockholdersEquity"]}


def line_items() -> dict:
    fin = fundamentals.plain(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "form"]))
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
            rows.append({"cik": cik, "donem": fy, "kalem": k, "10-K": exp, "arsiv": round(got, 1) if np.isfinite(got) else None,
                         "fark": None if not np.isfinite(err) else round(err, 5), "gecti": bool(np.isfinite(err) and abs(err) <= 0.005),
                         "etiket": cand.tag.iloc[0] if len(cand) else None})
    d = pd.DataFrame(rows)
    return {"kosul": "±%0,5", "olcum": int(len(d)), "gecen": int(d.gecti.sum()), "satirlar": d.to_dict(orient="records")}


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
    sub_cols = pd.Index(rng.choice(cols, size=min(1500, len(cols)), replace=False))
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
    checks = {"brut_marj": lambda c, t: latest(c, t, ["GrossProfit"], 4) / latest(c, t, R.REVENUE, 4),
              "faaliyet_marji": lambda c, t: latest(c, t, ["OperatingIncomeLoss"], 4) / latest(c, t, R.REVENUE, 4),
              "cari_oran": lambda c, t: latest(c, t, ["AssetsCurrent"], 0) / latest(c, t, ["LiabilitiesCurrent"], 0),
              "kazanc_getirisi": lambda c, t: latest(c, t, ["NetIncomeLoss", "ProfitLoss"], 4) / mcap.at[t, c],
              "defter_fiyat": lambda c, t: latest(c, t, R.EQUITY, 0) / mcap.at[t, c]}
    src = {k: (r1s[k] if k == "kazanc_getirisi" else rs[k]) for k in checks}
    out = {}
    for k, fn in checks.items():
        res, tries = [], 0
        while len(res) < n and tries < n * 20:
            tries += 1
            c, t = str(rng.choice(sub_cols)), dates[rng.integers(len(dates))]
            ours = src[k].at[t, c] if c in src[k] else np.nan
            if not np.isfinite(ours):
                continue
            try:
                ind = fn(c, t)
            except Exception:
                continue
            if not np.isfinite(ind) or ind == 0:
                continue
            res.append({"cik": c, "tarih": str(t.date()), "bizim": float(ours), "bagimsiz": float(ind), "fark": float(ours / ind - 1)})
        d = pd.DataFrame(res)
        clipped = {"brut_marj": (-2, 1), "faaliyet_marji": (-5, 1), "cari_oran": (0, 20), "kazanc_getirisi": (-2, 2), "defter_fiyat": (-5, 5)}[k]
        d = d[(d.bagimsiz > clipped[0]) & (d.bagimsiz < clipped[1])]  # kırpılan uç değerler karşılaştırılmaz
        ok = d.fark.abs() <= 0.01
        out[k] = {"kosul": "±%1, ≥ %99", "olcum": int(len(d)), "saglayan_pay": float(ok.mean()) if len(d) else None,
                  "sapanlar": d[~ok].head(15).round(5).to_dict(orient="records")}
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
    tab = pd.DataFrame({"baslangic": rows[:-1], "bitis": rows[1:]})
    tab["hafta"] = ((tab.bitis - tab.baslangic).dt.days // 7).astype(int)
    overlap = (tab.baslangic.iloc[1:].to_numpy() < tab.bitis.iloc[:-1].to_numpy()).sum()
    return {"donem": int(len(tab)), "hafta_dagilimi": tab.hafta.value_counts().sort_index().to_dict(), "cakisma": int(overlap),
            "13_haftadan_kisa": int((tab.hafta < 13).sum()),
            "tablo": [{"baslangic": str(a.date()), "bitis": str(b.date()), "hafta": int(h)} for a, b, h in tab.itertuples(index=False)]}


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
def exits(p: dict, tab: dict) -> dict:
    price, dv, sec = p["price"], p["dollar_volume"], p["securities"]
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik").reindex(price.columns)
    gone = s.status.to_numpy() == "çıktı"
    member = panel.membership(sec, price.index, price.columns) & price.notna()
    rows = []
    for w in tab["tablo"]:
        t0, t1 = pd.Timestamp(w["baslangic"]), pd.Timestamp(w["bitis"])
        if t0.year > 2024:
            continue
        u = member.loc[t0] & (p["raw"].loc[t0] >= 1)
        cols = price.columns[u.to_numpy()]
        end = s.end.reindex(cols)
        ex = cols[gone[price.columns.get_indexer(cols)] & (end > t0).to_numpy() & (end <= t1).to_numpy()]
        res = {}
        for name, mult in (("s1", 1.0), ("s2", 0.5), ("s3", 0.0)):
            r = price.loc[t1, cols] / price.loc[t0, cols] - 1
            for c in ex:
                before = price[c][(price.index > t0) & (price.index <= s.at[c, "end"] + pd.Timedelta(days=10))].dropna()
                last = before.iloc[-1] if len(before) else price.at[t0, c]
                lastw = before.index[-1] if len(before) else t0
                ftd = pd.isna(dv.at[lastw, c])
                if s.at[c, "bankrupt"]:
                    val = 0.0
                else:
                    val = last * (mult if ftd else 1.0)
                r[c] = val / price.at[t0, c] - 1
            res[name] = float(r.mean())
        n_ftd = sum(1 for c in ex if not s.at[c, "bankrupt"])
        rows.append({"donem": w["baslangic"], "evren": int(len(cols)), "cikan": int(len(ex)), "ftd_fiyatli_cikis_ust_sinir": n_ftd, **res})
    d = pd.DataFrame(rows)
    yr = d.groupby(d.donem.str[:4]).agg(s1=("s1", lambda x: np.prod(1 + x) - 1), s2=("s2", lambda x: np.prod(1 + x) - 1),
                                        s3=("s3", lambda x: np.prod(1 + x) - 1), cikan=("cikan", "sum"))
    return {"not": "Evrenin eşit ağırlıklı çeyrek getirisi; senaryolar yalnızca iflas dışı ve son fiyatı hacimsiz (FTD) çıkışları değiştirir.",
            "yillik_ortalama": {k: float(yr[k].mean()) for k in ("s1", "s2", "s3")}, "yillar": yr.round(4).to_dict(orient="index"),
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


def nw_check() -> dict:
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
    return {"katsayi": b.round(6).tolist(), "se_fonksiyon": se.round(8).tolist(), "se_elle": se_manual.round(8).tolist(),
            "gecti": bool(np.allclose(se, se_manual))}


def main(parts: list[str]) -> dict:
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    p = panel.build()
    tab = dates_table(p)
    steps = {"tarih": lambda: tab, "neweywest": nw_check, "kalem": line_items, "bolunme": lambda: splits(p),
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
    main(sys.argv[1].split(",") if len(sys.argv) > 1 else ["tarih", "neweywest", "kalem", "bolunme", "oran", "eksik", "cikis"])

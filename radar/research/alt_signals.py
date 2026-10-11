"""Alternatif veri belirtileri (aylık tarihlerde): Reddit arşivi ve GDELT haber adres kelimeleri / birlikte anılan kurumlar.

Her tarih t için yalnızca t'den önce TAMAMLANMIŞ aylar kullanılır.
Reddit (reddit_arsiv; alt-forumlar toplanır):
- reddit_anilma: son ay gönderi sayısı (log), reddit_anilma_ivme: son ay ÷ önceki 6 ay ortalaması (log)
- reddit_ofke_payi, reddit_olumlu_payi, reddit_olumsuz_payi: son 3 ay gönderilerinde oran (en az 5 gönderi)
- reddit_puan: son 3 ay gönderi başına ortalama puan (log)
Haber kelimeleri (gdelt_words):
- yukselen_kelime_maruziyeti: her ay bütün haber adreslerinde payı en hızlı yükselen 50 kelime (son 3 ay ÷ önceki 12 ay;
  elle liste yok) — şirketin son 3 ay haber kelimelerinin ne kadarı bunlar
- yukselen_kurum_birlikteligi: şirket haberlerinde birlikte anılma sayısı en hızlı yükselen 50 kurumla birlikte anılma payı
- yeni_kurum_orani: şirketin son 3 ayda birlikte anıldığı kurumların, önceki 12 ayda hiç anılmamış olanlarının payı
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive

GEN = {"inc", "corp", "company", "group", "news", "reuters", "associated press", "bloomberg", "twitter", "facebook",
       "youtube", "instagram", "nasdaq", "new york stock exchange", "securities and exchange commission", "united states"}


def _month_idx(d: pd.Series) -> np.ndarray:
    return ((d.dt.year - 2009) * 12 + d.dt.month - 1).to_numpy()


def _end_month(t) -> int:
    t = pd.Timestamp(t)
    return (t.year - 2009) * 12 + t.month - 2  # son tamamlanmış ay


def _cols_index(cols) -> dict[int, int]:
    return {int(c): i for i, c in enumerate(cols) if str(c).isdigit()}


def reddit_features(dates: pd.DatetimeIndex, columns) -> dict[str, pd.DataFrame]:
    try:
        r = archive.load("reddit_arsiv")
    except Exception:
        return {}
    r = r[r.kind == "month_cik"].dropna(subset=["cik"])
    if r.empty:
        return {}
    ci = _cols_index(columns)
    c = r.cik.astype("int64").map(ci)
    ok = c.notna()
    r, c = r[ok], c[ok].astype(int).to_numpy()
    m = _month_idx(r.date)
    nm, nc = int(m.max()) + 2, len(columns)
    arr = {k: np.zeros((nm, nc)) for k in ("posts", "score", "pos", "neg", "angry")}
    for k in arr:
        np.add.at(arr[k], (m, c), r[k].to_numpy(float))
    out = {k: np.full((len(dates), nc), np.nan) for k in
           ("reddit_anilma", "reddit_anilma_ivme", "reddit_ofke_payi", "reddit_olumlu_payi", "reddit_olumsuz_payi", "reddit_puan")}
    for i, t in enumerate(dates):
        e = _end_month(t)
        if e < 6 or e >= nm:
            continue
        p1 = arr["posts"][e]
        p6 = arr["posts"][e - 6:e].mean(0)
        p3 = arr["posts"][e - 2:e + 1].sum(0)
        has = p3 >= 5
        out["reddit_anilma"][i] = np.log1p(p1)
        out["reddit_anilma_ivme"][i] = np.log((p1 + 1) / (p6 + 1))
        for k, name in (("angry", "reddit_ofke_payi"), ("pos", "reddit_olumlu_payi"), ("neg", "reddit_olumsuz_payi")):
            out[name][i, has] = arr[k][e - 2:e + 1].sum(0)[has] / p3[has]
        out["reddit_puan"][i, has] = np.log1p(np.maximum(arr["score"][e - 2:e + 1].sum(0)[has], 0) / p3[has])
    return {k: pd.DataFrame(v, index=dates, columns=[str(x) for x in columns]) for k, v in out.items()}


def word_features(dates: pd.DatetimeIndex, columns, top_n: int = 50) -> dict[str, pd.DataFrame]:
    import pyarrow.parquet as pq
    try:
        t = pq.read_table(archive.fetch("gdelt_words"), columns=["kind", "date", "cik", "token", "count"],
                          read_dictionary=["kind", "token"])
    except Exception:
        return {}
    df = t.to_pandas()
    del t
    df["count"] = df["count"].astype("float32")
    ci = _cols_index(columns)
    nc = len(columns)
    tokens = pd.Index(df.token.cat.categories)
    m_all = _month_idx(df.date)
    nm = int(m_all.max()) + 2
    code = df.token.cat.codes.to_numpy()
    kind = df.kind.astype(str).to_numpy()
    cnt = df["count"].to_numpy(float)
    cik = df.cik.to_numpy(dtype="float64", na_value=np.nan)
    del df
    is_word, is_cw, is_co = kind == "month_word", kind == "month_cik_word", kind == "month_cik_org"
    # global kelime payları (ay × kelime)
    G = np.zeros((nm, len(tokens)))
    np.add.at(G, (m_all[is_word], code[is_word]), cnt[is_word])
    gt = G.sum(1)
    # kurumların şirket haberlerindeki toplam birlikte anılması (ay × kurum) — global kurum sayısı yerine
    O = np.zeros((nm, len(tokens)))
    np.add.at(O, (m_all[is_co], code[is_co]), cnt[is_co])
    generic = np.array([str(x) in GEN for x in tokens])

    def company_arrays(mask):
        cc = pd.Series(cik[mask]).map(ci).to_numpy(dtype=float)
        ok = ~np.isnan(cc)
        return m_all[mask][ok], cc[ok].astype(int), code[mask][ok], cnt[mask][ok]
    wm, wc, wt, wv = company_arrays(is_cw)
    om, oc, ot, ov = company_arrays(is_co)
    out = {k: np.full((len(dates), nc), np.nan) for k in ("yukselen_kelime_maruziyeti", "yukselen_kurum_birlikteligi", "yeni_kurum_orani")}
    for i, t in enumerate(dates):
        e = _end_month(t)
        if e < 15 or e >= nm:
            continue
        lo3, lo12, hi12 = e - 2, e - 14, e - 3
        # yükselen kelimeler
        s3 = G[lo3:e + 1].sum(0) / max(gt[lo3:e + 1].sum(), 1)
        b = G[lo12:hi12 + 1].sum(0)
        s12 = b / max(gt[lo12:hi12 + 1].sum(), 1)
        mom = np.where((b >= 200) & ~generic, np.log((s3 + 1e-8) / (s12 + 1e-8)), -np.inf)
        top = set(np.argsort(-mom)[:top_n])
        wmask = (wm >= lo3) & (wm <= e)
        hit = np.isin(wt, list(top)) & wmask
        tot = np.bincount(wc[wmask], weights=wv[wmask], minlength=nc)
        num = np.bincount(wc[hit], weights=wv[hit], minlength=nc)
        has = tot >= 20
        out["yukselen_kelime_maruziyeti"][i, has] = num[has] / tot[has]
        # yükselen kurumlar
        o3, o12 = O[lo3:e + 1].sum(0), O[lo12:hi12 + 1].sum(0)
        omom = np.where((o12 >= 50) & ~generic, np.log((o3 / 3 + 1) / (o12 / 12 + 1)), -np.inf)
        otop = set(np.argsort(-omom)[:top_n])
        omask = (om >= lo3) & (om <= e)
        ohit = np.isin(ot, list(otop)) & omask
        otot = np.bincount(oc[omask], weights=ov[omask], minlength=nc)
        onum = np.bincount(oc[ohit], weights=ov[ohit], minlength=nc)
        ohas = otot >= 10
        out["yukselen_kurum_birlikteligi"][i, ohas] = onum[ohas] / otot[ohas]
        # yeni kurum oranı: son 3 ayda anılan kurumlardan önceki 12 ayda hiç anılmamış olanların payı
        prev = (om >= lo12) & (om <= hi12)
        seen = set(zip(oc[prev], ot[prev]))
        new = np.array([(c_, t_) not in seen for c_, t_ in zip(oc[omask], ot[omask])], dtype=bool)
        nn = np.bincount(oc[omask][new], weights=ov[omask][new], minlength=nc)
        out["yeni_kurum_orani"][i, ohas] = nn[ohas] / otot[ohas]
    return {k: pd.DataFrame(v, index=dates, columns=[str(x) for x in columns]) for k, v in out.items()}

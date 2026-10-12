"""Finansal veriler için ortak okuma: segmentsiz değerler ve toplam hisse sayısı.

Arşivdeki finansal tablolar, hisse sayısı etiketlerinde sınıf bazındaki (A/B hisse) değerleri de içerir
(segments sütunu dolu). Diğer tüm kalemler segmentsizdir. Toplam hisse sayısı: önce şirket genelindeki değer,
yoksa sınıf değerlerinin toplamı (çok sınıflı şirketler, SPAC'ler).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive

SHARE_TAGS = ["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"]


def load(columns: list[str]) -> pd.DataFrame:
    cols = list(dict.fromkeys(columns + ["segments"]))
    try:
        fin = archive.load("financials", columns=cols)
    except Exception:  # eski bölümlerde segments sütunu yok
        fin = archive.load("financials", columns=columns).assign(segments="")
    fin["segments"] = fin["segments"].fillna("")
    return fin


def plain(fin: pd.DataFrame) -> pd.DataFrame:
    """Segmentsiz (şirket geneli) değerler."""
    return fin[fin.segments == ""]


def shares_outstanding(fin: pd.DataFrame) -> pd.DataFrame:
    """Rapor başına toplam hisse sayısı: (cik, accepted, value)."""
    d = fin[fin.tag.isin(SHARE_TAGS) & (fin.qtrs == 0)].copy()
    d = d[d.ddate == d.groupby(["adsh", "tag"]).ddate.transform("max")]
    d["prio"] = d.tag.map({t: i for i, t in enumerate(SHARE_TAGS)}) * 2 + (d.segments != "").astype(int)
    whole = d[d.segments == ""].groupby(["adsh", "cik", "accepted", "prio"]).value.first()
    by_class = d[d.segments != ""].groupby(["adsh", "cik", "accepted", "prio"]).value.sum()
    both = pd.concat([whole, by_class]).reset_index().sort_values(["adsh", "prio"])
    out = both.drop_duplicates("adsh")[["adsh", "cik", "accepted", "value"]]
    # Yedek: dolaşımdaki hisse sayısını hiç vermeyen şirketler (ör. KO) için raporun ağırlıklı ortalama hisse sayısı
    # (en kısa dönem; yalnızca o şirketin hiçbir raporunda dolaşımdaki sayı yoksa)
    w = fin[(fin.tag == "WeightedAverageNumberOfSharesOutstandingBasic") & (fin.segments == "") & (fin.qtrs > 0)
            & ~fin.cik.isin(set(out.cik))]
    if len(w):
        w = w[w.ddate == w.groupby("adsh").ddate.transform("max")].sort_values(["adsh", "qtrs"]).drop_duplicates("adsh")
        out = pd.concat([out, w[["adsh", "cik", "accepted", "value"]]])
    return out[["cik", "accepted", "value"]]


def shares_wide(sh: pd.DataFrame, price: pd.DataFrame, raw: pd.DataFrame, max_age: int | None = None) -> pd.DataFrame:
    """Hisse sayısı (tarih × cik), rapordan sonraki hisse bölünmelerine göre düzeltilmiş.

    Rapordaki hisse sayısı bir sonraki rapora kadar taşınır; arada bölünme olursa işlem fiyatı (raw) düşer ama sayı eski
    kalır ve piyasa değeri bölünme oranı kadar küçük görünür (NVDA 2024: 2,98 tn $ → 0,30 tn $). Düzeltme: düzeltilmiş
    fiyatla işlem fiyatı arasındaki oran (S = raw / price) yalnızca bölünmede sıçrar; rapor anındaki S ile bugünkü S'nin
    oranı hisse sayısını çarpar. Temettü düzeltmesinden gelen küçük kaymalar (oran 1/1,3–1,3) yok sayılır.
    """
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    max_age = max_age or FUNDAMENTAL_MAX_AGE
    dates, cols = price.index, price.columns
    S = (raw / price).replace([np.inf, -np.inf], np.nan).ffill()
    sh = sh.assign(cik=sh.cik.astype(str))
    day = pd.to_datetime(sh.accepted)
    if getattr(day.dt, "tz", None) is not None:
        day = day.dt.tz_convert("America/New_York").dt.tz_localize(None)
    row = dates.searchsorted(day.dt.normalize().to_numpy(), side="right") - 1
    col = pd.Index(cols.astype(str)).get_indexer(sh.cik)
    ok = (row >= 0) & (col >= 0)
    s_at = np.full(len(sh), -1.0)
    vals = S.to_numpy()[row[ok], col[ok]]
    s_at[ok] = np.where(np.isfinite(vals), vals, -1.0)
    long = sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]]
    n = pit(long, dates, cols, max_age)
    s_rep = pit(long.assign(value=s_at), dates, cols, max_age)
    ratio = (s_rep / S).where(s_rep > 0)
    ratio = ratio.where(np.abs(np.log(ratio)) > np.log(1.3), 1.0).fillna(1.0)
    return n * ratio

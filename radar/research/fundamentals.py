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
    """Rapor başına toplam dönem sonu hisse sayısı: (cik, accepted, asof, value); asof = sayının geçerli olduğu tarih.

    Yalnızca dönem sonu sayısı (kapak ya da bilanço). Ağırlıklı ortalama yedek olarak kullanılmaz (ön kayıt v1.2, 6.1-1);
    sayısı olmayan raporlarda piyasa değeri ve ondan türeyenler eksik kalır."""
    d = fin[fin.tag.isin(SHARE_TAGS) & (fin.qtrs == 0)].copy()
    d = d[d.ddate == d.groupby(["adsh", "tag"]).ddate.transform("max")]
    d["prio"] = d.tag.map({t: i for i, t in enumerate(SHARE_TAGS)}) * 2 + (d.segments != "").astype(int)
    whole = d[d.segments == ""].groupby(["adsh", "cik", "accepted", "prio", "ddate"]).value.first()
    by_class = d[d.segments != ""].groupby(["adsh", "cik", "accepted", "prio", "ddate"]).value.sum()
    both = pd.concat([whole, by_class]).reset_index().sort_values(["adsh", "prio"])
    out = both.drop_duplicates("adsh").rename(columns={"ddate": "asof"})
    return out[["cik", "accepted", "asof", "value"]].reset_index(drop=True)


def shares_wide(sh: pd.DataFrame, price: pd.DataFrame, raw: pd.DataFrame | None = None, max_age: int | None = None,
                events: pd.DataFrame | None = None) -> pd.DataFrame:
    """Hisse sayısı (tarih × cik), sayının geçerli olduğu tarihten sonraki hisse bölünmelerine göre düzeltilmiş.

    Rapordaki sayı bir sonraki rapora kadar taşınır; arada bölünme olursa işlem fiyatı düşer ama sayı eski kalır
    (NVDA 2024: 2,98 tn $ → 0,30 tn $). Düzeltme oranı bölünme olay kayıtlarından alınır (ön kayıt v1.2, 6.1-3):
    C(t) / C(asof), C = o güne kadarki bölünme oranlarının çarpımı (panel.split_events; 1/1,3–1,3 arası kayıtlar hariç).
    Fiyat oranı (düzeltilmiş / ham) kullanılmaz; o oran temettü düzeltmesini de içerir."""
    from radar.research import panel
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    max_age = max_age or FUNDAMENTAL_MAX_AGE
    dates, cols = price.index, price.columns
    events = panel.split_events() if events is None else events
    import os
    sh = sh.assign(cik=sh.cik.astype(str))
    # Karşılaştırma için (1. aşama, karar bekliyor): RADAR_HISSE_CAPA=kabul → düzeltme raporun kabul tarihinden başlar.
    # Bilanço sayısı, dönem sonundan sonra ama rapor yayımlanmadan önceki bölünmeye göre geriye dönük düzeltilir (SAB Topic 4C).
    anchor = os.environ.get("RADAR_HISSE_CAPA", "gecerlilik")
    asof = sh["asof"] if ("asof" in sh and anchor == "gecerlilik") else sh["accepted"]
    asof = pd.to_datetime(asof)
    if getattr(asof.dt, "tz", None) is not None:
        asof = asof.dt.tz_convert("America/New_York").dt.tz_localize(None)
    c_at = panel.split_cum_at(sh.cik, asof.dt.normalize(), events)
    long = sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]]
    n = pit(long, dates, cols, max_age)
    c_rep = pit(long.assign(value=c_at), dates, cols, max_age)
    c_now = panel.split_cum_wide(dates, cols, events)
    return n * (c_now / c_rep).fillna(1.0)

"""Finansal veriler için ortak okuma: segmentsiz değerler ve toplam hisse sayısı.

Arşivdeki finansal tablolar, hisse sayısı etiketlerinde sınıf bazındaki (A/B hisse) değerleri de içerir
(segments sütunu dolu). Diğer tüm kalemler segmentsizdir. Toplam hisse sayısı: önce şirket genelindeki değer,
yoksa sınıf değerlerinin toplamı (çok sınıflı şirketler, SPAC'ler).
"""

from __future__ import annotations

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
    return both.drop_duplicates("adsh")[["cik", "accepted", "value"]]

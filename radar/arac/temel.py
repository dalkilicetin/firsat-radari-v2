"""Bilanço ve gelir verisi: SEC Financial Statement Data Sets (çeyreklik toplu) + SEC companyfacts (her gece güncel).

İki kaynak aynı biçime getirilir (adsh, cik, tag, value, accepted, qtrs, ddate, uom, segments). Aynı rapor ve kalem
ikisinde de varsa çeyreklik toplu set tercih edilir. companyfacts satırlarının yayım anı, accession numarası dosyalama
geçmişindeki kabul anıyla eşleştirilerek bulunur; eşleşmezse dosyalama gününün sonu (ertesi gün) sayılır.
companyfacts yalnızca sınıf/segment ayrımı olmayan değerleri içerir.
"""

from __future__ import annotations

import pandas as pd

from radar import archive
from radar.research import fundamentals


def _gun_sonu(filed: pd.Series) -> pd.Series:
    """Yalnızca tarihi olan kayıt: o günün sonunda (ertesi gün 00:00, New York) yayımlanmış sayılır."""
    return pd.to_datetime(filed) + pd.Timedelta(days=1)


def kabul_anlari() -> pd.DataFrame:
    """accession → dosyalama geçmişindeki kabul anı (duvar saati New York sayılır: geç yorum, duzenek.duvar_saati)."""
    acc = archive.load("filings", columns=["accession", "accepted"]).drop_duplicates("accession")
    return acc.assign(accepted=acc.accepted.dt.tz_localize(None))


def companyfacts(acc: pd.DataFrame | None = None, tags: list[str] | None = None) -> pd.DataFrame:
    try:
        cf = archive.load("sirket_olgulari", filters=[("tag", "in", tags)] if tags else None)
    except Exception:
        return pd.DataFrame()
    if cf.empty:
        return cf
    acc = kabul_anlari() if acc is None else acc
    cf = cf.merge(acc, left_on="accn", right_on="accession", how="left")
    cf["accepted"] = cf.accepted.fillna(_gun_sonu(cf.filed))
    days = (cf.end - cf.start).dt.days
    qtrs = pd.Series(pd.NA, index=cf.index, dtype="Int64")
    qtrs[cf.start.isna()] = 0
    qtrs[days.between(80, 100)] = 1
    qtrs[days.between(170, 190)] = 2
    qtrs[days.between(260, 280)] = 3
    qtrs[days.between(350, 380)] = 4
    out = pd.DataFrame({"adsh": cf.accn, "cik": cf.cik.astype("int64"), "tag": cf.tag.astype(str), "value": cf.value.astype(float),
                        "accepted": cf.accepted, "qtrs": qtrs, "ddate": cf.end, "uom": cf.unit.astype(str), "segments": "",
                        "kaynak": "companyfacts"})
    return out[out.qtrs.notna()].astype({"qtrs": "int64"})


def gerekli_etiketler() -> list[str]:
    from radar.arac import isaretler
    from radar.research.road1 import REVENUE
    return sorted(set(fundamentals.SHARE_TAGS) | set(REVENUE) | set(isaretler.NET_INCOME) | set(isaretler.CASH)
                  | set(isaretler.SHORT_INV) | set(isaretler.OCF))


def finans(columns: list[str] | None = None, tags: list[str] | None = None) -> pd.DataFrame:
    """Birleşik tablo (yalnızca analiz aracının kullandığı kalemler). accepted: New York duvar saati (naive)."""
    tags = gerekli_etiketler() if tags is None else tags
    cols = ["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "uom", "segments"]
    try:
        fs = archive.load("financials", columns=cols, filters=[("tag", "in", tags)])
    except Exception:  # eski bölümlerde segments sütunu yok
        fs = archive.load("financials", columns=cols[:-1], filters=[("tag", "in", tags)]).assign(segments="")
    fs["segments"] = fs["segments"].fillna("")
    fs = fs.assign(kaynak="fsds")
    fs["accepted"] = pd.to_datetime(fs.accepted)
    if getattr(fs.accepted.dt, "tz", None) is not None:
        fs["accepted"] = fs.accepted.dt.tz_localize(None)
    fs["ddate"] = pd.to_datetime(fs.ddate)
    # İki kaynaktaki kabul anı bazen saatlerce farklı (saat dilimi etiketi): geç olan alınır.
    acc = kabul_anlari()
    later = pd.Series(fs.adsh.map(acc.set_index("accession").accepted).to_numpy(), index=fs.index).fillna(fs.accepted)
    fs["accepted"] = later.where(later > fs.accepted, fs.accepted)
    cf = companyfacts(acc, tags)
    if len(cf):
        key = ["adsh", "tag", "qtrs", "ddate"]
        seen = pd.MultiIndex.from_frame(fs[key].drop_duplicates())
        cf = cf[~pd.MultiIndex.from_frame(cf[key]).isin(seen)]
        fs = pd.concat([fs, cf[fs.columns]], ignore_index=True)
    # Aynı rapor (accession) iki kaynakta farklı kabul anıyla kayıtlı olabilir: raporun bütün satırlarına en geç olanı ver.
    # Yoksa bir rapor bir kaynakta kesimden önce, diğerinde sonra görünür ve o gün hangi değerlerin bilindiği tutarsızlaşır
    # (doğrulamadaki sızıntı testi bunu yakaladı).
    fs["accepted"] = fs.groupby("adsh").accepted.transform("max")
    for c in ("tag", "uom", "segments", "kaynak"):
        fs[c] = fs[c].astype("category")
    return fs if columns is None else fs[columns]

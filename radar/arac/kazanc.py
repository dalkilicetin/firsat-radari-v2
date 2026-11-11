"""Bilanço açıklamasına tepki işaretleri (8-K 2.02 basın bülteni + günlük fiyat).

Her bülten için tepki günü: SEC kabul saati New York 16:00'dan önceyse o gün, sonraysa ertesi işlem günü.
Tepki = hissenin o günkü getirisi − aynı gün tüm hisselerin ortadaki getirisi. Cuma t için yalnızca tepki günü perşembe
(t−1) ya da öncesi olan, son 100 gündeki en yeni bülten kullanılır; 3 günlük tepki ancak 3. gün de perşembeye kadar bittiyse.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive
from radar.identity import build as build_identity

AD = ["tepki1", "tepki3", "tepki_hacim", "tepki_gun", "bulten_ton", "bulten_rehberlik", "bulten_rekor", "bulten_beklenti_ustu"]
EN_ESKI = 100


def gunluk() -> pd.DataFrame:
    sec = build_identity()["securities"]
    sec = sec.assign(cik=sec.cik.astype(str))
    a = archive.load("prices", columns=["symbol", "date", "adjclose", "volume"])
    a = a.merge(sec[sec.status == "aktif"][["symbol", "cik"]], on="symbol")[["cik", "date", "adjclose", "volume"]]
    try:
        ex = archive.load("prices_exited", columns=["cik", "date", "adjclose", "volume"]).assign(cik=lambda x: x.cik.astype(str))
        a = pd.concat([a, ex], ignore_index=True)
    except Exception:
        pass
    a["date"] = pd.to_datetime(a.date).astype("datetime64[ns]")
    a = a.dropna(subset=["adjclose"]).drop_duplicates(["cik", "date"], keep="last").sort_values(["cik", "date"], kind="stable")
    g = a.groupby("cik", sort=False)
    a["ret"] = g.adjclose.pct_change()
    a.loc[a.ret.abs() > 5, "ret"] = np.nan
    a["ab"] = a.ret - a.groupby("date").ret.transform("median")
    a["ab3"] = a.ab + g.ab.shift(-1) + g.ab.shift(-2)
    a["d3"] = g.date.shift(-2)
    a["volr"] = a.volume / g.volume.transform(lambda s: s.shift(1).rolling(60, min_periods=20).median())
    a["volr"] = a.volr.replace([np.inf, -np.inf], np.nan)
    return a[["cik", "date", "ab", "ab3", "d3", "volr"]]


def olaylar(kes: pd.Timestamp | None = None) -> pd.DataFrame:
    b = archive.load("bilanco_bulteni")
    b["cik"] = b.cik.astype(str)
    ny = b.accepted.dt.tz_convert("America/New_York")
    b["etki"] = (ny.dt.normalize() + pd.to_timedelta((ny.dt.hour >= 16).astype(int), unit="D")).dt.tz_localize(None).astype("datetime64[ns]")
    b["rehber"] = b.rehberlik_yukari - b.rehberlik_asagi
    g = gunluk()
    if kes is not None:  # sızıntı testi: T'den sonraki fiyat ve bültenleri at
        g = g[g.date <= kes]
        g.loc[g.d3 > kes, ["ab3", "d3"]] = np.nan
        b = b[b.etki <= kes]
    b = b.sort_values("etki", kind="stable")
    e = pd.merge_asof(b, g.sort_values("date", kind="stable"), left_on="etki", right_on="date", by="cik", direction="forward",
                      tolerance=pd.Timedelta(days=5))
    e = e.dropna(subset=["date"]).rename(columns={"date": "rgun"})
    return e[["cik", "rgun", "ab", "ab3", "d3", "volr", "ton", "rehber", "rekor", "beklenti_ustu"]]


def hesapla(tarihler: pd.DatetimeIndex, sutunlar: pd.Index, kes: pd.Timestamp | None = None) -> dict[str, pd.DataFrame]:
    e = olaylar(kes).sort_values("rgun", kind="stable")
    e = e[e.cik.isin(set(sutunlar))]
    grid = pd.MultiIndex.from_product([tarihler, e.cik.unique()], names=["t", "cik"]).to_frame(index=False)
    grid["per"] = (grid.t - pd.Timedelta(days=1)).astype("datetime64[ns]")
    m = pd.merge_asof(grid.sort_values("per", kind="stable"), e, left_on="per", right_on="rgun", by="cik",
                      tolerance=pd.Timedelta(days=EN_ESKI))
    m = m.dropna(subset=["rgun"])
    m["tepki1"] = m.ab
    m["tepki3"] = m.ab3.where(m.d3 <= m.per)
    m["tepki_hacim"] = m.volr
    m["tepki_gun"] = (m.per - m.rgun).dt.days.astype(float)
    m = m.rename(columns={"ton": "bulten_ton", "rehber": "bulten_rehberlik", "rekor": "bulten_rekor", "beklenti_ustu": "bulten_beklenti_ustu"})
    return {n: m.pivot(index="t", columns="cik", values=n).reindex(index=tarihler, columns=sutunlar).astype("float32") for n in AD}

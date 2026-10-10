"""Zaman hizalama: olaylar ve değerler, yalnızca kullanılabilir oldukları ilk Cuma'dan itibaren panelde görünür."""

from __future__ import annotations

import numpy as np
import pandas as pd

FUNDAMENTAL_MAX_AGE = 400  # gün: bundan eski finansal değer yok sayılır


def to_friday(dates: pd.Series) -> pd.Series:
    """Bir olayın kullanılabileceği ilk Cuma: olay gününden SONRAKİ ilk Cuma (aynı gün kapanışına yetişmeyebilir)."""
    day = pd.to_datetime(dates)
    if getattr(day.dt, "tz", None) is not None:
        day = day.dt.tz_convert("America/New_York").dt.tz_localize(None)
    return (day.dt.normalize() + pd.Timedelta(days=1)) + pd.offsets.Week(weekday=4, n=0)


def weekly(long: pd.DataFrame, dates, columns, agg: str) -> pd.DataFrame:
    long = long.assign(cik=long.cik.astype(str))
    long = long[long.cik.isin(set(columns))]
    long = long.assign(friday=to_friday(long.date))
    g = long.groupby(["friday", "cik"]).value
    wide = (g.last() if agg == "last" else g.sum()).unstack("cik")
    return wide.reindex(columns=columns)


def pit(long: pd.DataFrame, dates: pd.DatetimeIndex, columns, max_age: int) -> pd.DataFrame:
    """(cik, date, value) → her Cuma için o güne kadar bilinen son değer (max_age gün sınırlı)."""
    wide = weekly(long.dropna(subset=["value"]), dates, columns, "last")
    idx = wide.index.union(dates)
    raw = wide.reindex(idx)
    obs = pd.DataFrame(np.where(raw.notna(), idx.values[:, None], np.datetime64("NaT")), index=idx, columns=raw.columns).ffill()
    age = (idx.values[:, None] - obs.values.astype("datetime64[ns]")) / np.timedelta64(1, "D")
    return raw.ffill().mask(age > max_age).reindex(dates)


def rolling_count(ev: pd.DataFrame, dates, columns, window_days) -> pd.DataFrame:
    """(cik, date) olaylarından: Cuma itibarıyla son window_days içindeki olay sayısı."""
    wide = weekly(ev.assign(value=1.0), dates, columns, "sum")
    filled = wide.reindex(wide.index.union(dates)).fillna(0)
    return filled.rolling(f"{window_days}D").sum().reindex(dates).fillna(0)


def recent_events(events: pd.DataFrame, dates, columns, window_days: int) -> pd.DataFrame:
    return rolling_count(events, dates, columns, window_days) > 0

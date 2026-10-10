"""Haftalık fiyat paneli (Cuma kapanışları), borsadan çıkan hisseler dahil.

- Aktif hisseler: Yahoo temettü ve bölünmeye göre düzeltilmiş kapanış.
- Çıkan hisseler: SEC FTD fiyatları (seyrek, ham). Ters bölünmeler (fiyatın bir günde tam sayı katına
  sıçraması) sezgisel olarak düzeltilir; gerçek çöküşleri silmemek için ileri bölünmelere dokunulmaz.
- Bir fiyat en fazla STALE_DAYS gün eski olabilir; daha eskiyse o hafta "işlem görmüyor" sayılır.
- Üyelik: kimlik katmanındaki [start, end] aralığı.
- İleri getiri: t'den t+h'ye. Hisse arada çıktıysa çıkış değeri kullanılır (iflasta 0, değilse son fiyat)
  ve sonrası nakit kabul edilir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive, config
from radar.identity import build as build_identity

STALE_DAYS = 30
HORIZONS = {"1h": 1, "1a": 4, "3a": 13, "6a": 26, "1y": 52}  # hafta
REVERSE_SPLIT_FACTORS = np.array([4, 5, 8, 10, 12, 15, 20, 25, 30, 35, 40, 50, 60, 75, 80, 100, 150, 200, 250, 500])
CACHE = config.DATA_DIR / "derived"


def fridays(start="2015-01-02", end=None) -> pd.DatetimeIndex:
    end = end or pd.Timestamp.today().normalize()
    return pd.date_range(start, end, freq="W-FRI")


def adjust_reverse_splits(px: np.ndarray) -> np.ndarray:
    """Tarihe göre sıralı ham seyrek fiyat dizisinde ters bölünmeleri geriye dönük düzeltir."""
    px = np.asarray(px, dtype=float)
    factor = np.ones(len(px))
    for i in range(1, len(px)):
        r = px[i] / px[i - 1]
        if np.isfinite(r) and r >= 3.5:
            k = REVERSE_SPLIT_FACTORS[np.argmin(np.abs(REVERSE_SPLIT_FACTORS - r))]
            if abs(r / k - 1) < 0.08:
                factor[:i] *= k  # bölünme öncesi fiyatları yeni ölçeğe taşı
    return px * factor


def weekly_last(df: pd.DataFrame, value: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Uzun tablo (cik, date, value) → geniş tablo: her Cuma için o güne kadarki son değer (STALE_DAYS sınırlı)."""
    wide = df.pivot_table(index="date", columns="cik", values=value, aggfunc="last").sort_index()
    idx = wide.index.union(dates)
    raw = wide.reindex(idx)
    filled = raw.ffill()
    # Son gözlemden bu yana geçen gün: gözlem tarihini ileri taşıyarak hesaplanır.
    obs_date = pd.DataFrame(np.where(raw.notna(), idx.values[:, None], np.datetime64("NaT")),
                            index=idx, columns=wide.columns).ffill()
    age_days = (idx.values[:, None] - obs_date.values.astype("datetime64[ns]")) / np.timedelta64(1, "D")
    return filled.mask(age_days > STALE_DAYS).reindex(dates)


def build(force: bool = False) -> dict[str, pd.DataFrame]:
    """price: düzeltilmiş kapanış (getiri için); raw: ham kapanış (düşük fiyat riski için);
    dollar_volume: 13 haftalık medyan günlük işlem tutarı (yalnızca aktif hisseler; FTD'de hacim yok)."""
    names = ["price", "raw", "dollar_volume"]
    paths = {n: CACHE / f"panel_{n}.parquet" for n in names}
    ident = build_identity()
    sec = ident["securities"]
    if all(p.exists() for p in paths.values()) and not force:
        return {n: pd.read_parquet(p) for n, p in paths.items()} | {"securities": sec}

    dates = fridays()
    active = sec[sec.status == "aktif"]
    daily = archive.load("prices", columns=["symbol", "date", "adjclose", "close", "volume"])
    daily = daily.merge(active[["symbol", "cik"]], on="symbol")
    daily["dollar_volume"] = daily.close * daily.volume
    px = daily.rename(columns={"adjclose": "price"})[["cik", "date", "price"]]
    raw_px = daily.rename(columns={"close": "price"})[["cik", "date", "price"]]
    dv = (daily.sort_values("date").groupby("cik", group_keys=False)
          .apply(lambda g: g.set_index("date").dollar_volume.rolling("91D").median().reset_index().assign(cik=g.name)))

    gone = sec[sec.status == "çıktı"]
    ftd = archive.load("ftd", columns=["settle_date", "symbol", "price"])
    ftd = ftd[ftd.price > 0].merge(gone[["symbol", "cik", "start", "end"]], on="symbol")
    # Sembol yeniden kullanılmış olabilir: yalnızca üyelik aralığı (+10 gün) içindeki gözlemler.
    ftd = ftd[(ftd.settle_date >= ftd.start - pd.Timedelta(days=60)) & (ftd.settle_date <= ftd.end + pd.Timedelta(days=10))]
    # FTD fiyatı takas tarihinden önceki işlem gününün kapanışıdır.
    ftd["date"] = ftd.settle_date - pd.offsets.BDay(1)
    ftd = ftd.groupby(["cik", "date"]).price.last().reset_index().sort_values(["cik", "date"])
    ftd_raw = ftd.copy()
    ftd["price"] = ftd.groupby("cik").price.transform(adjust_reverse_splits)

    columns = sec.cik.astype(str)  # hiç fiyatı olmayan üyeler de sütun olarak kalır (kapsamda görünsünler)
    out = {
        "price": weekly_last(pd.concat([px, ftd], ignore_index=True), "price", dates),
        "raw": weekly_last(pd.concat([raw_px, ftd_raw], ignore_index=True), "price", dates),
        "dollar_volume": weekly_last(dv, "dollar_volume", dates),
    }
    CACHE.mkdir(parents=True, exist_ok=True)
    for n, df in out.items():
        df.columns = df.columns.astype(str)
        out[n] = df.reindex(columns=columns)
        out[n].to_parquet(paths[n])
    return out | {"securities": sec}


def membership(sec: pd.DataFrame, dates: pd.DatetimeIndex, columns) -> pd.DataFrame:
    s = sec.set_index(sec.cik.astype(str)).reindex(columns)
    start = s.start.to_numpy(dtype="datetime64[ns]")
    end = s.end.fillna(pd.Timestamp("2100-01-01")).to_numpy(dtype="datetime64[ns]")
    d = dates.to_numpy(dtype="datetime64[ns]")[:, None]
    return pd.DataFrame((d >= start) & (d <= end), index=dates, columns=columns)


def forward_returns(price: pd.DataFrame, sec: pd.DataFrame, weeks: int) -> pd.DataFrame:
    """t'de fiyatı olan üyeler için t→t+h getirisi; arada çıkanlara çıkış değeri uygulanır."""
    s = sec.set_index(sec.cik.astype(str)).reindex(price.columns)
    dates = price.index
    member = membership(sec, dates, price.columns)
    future = price.shift(-weeks)
    # Çıkış değeri: iflasta 0, değilse çıkıştan önceki son fiyat.
    last_px = price.ffill()
    exit_value = pd.Series(index=price.columns, dtype=float)
    for c in price.columns[s.status.to_numpy() == "çıktı"]:
        end = s.at[c, "end"]
        before = last_px[c][last_px.index <= end + pd.Timedelta(days=10)].dropna()
        exit_value[c] = 0.0 if s.at[c, "bankrupt"] else (before.iloc[-1] if len(before) else np.nan)
    horizon_end = pd.Series(dates, index=dates).shift(-weeks)
    end_dates = s.end.to_numpy(dtype="datetime64[ns]")
    exited = pd.DataFrame(end_dates[None, :] < horizon_end.to_numpy(dtype="datetime64[ns]")[:, None],
                          index=dates, columns=price.columns)
    exit_matrix = pd.DataFrame(np.broadcast_to(exit_value.to_numpy(), future.shape), index=dates, columns=price.columns)
    future = future.mask(exited, exit_matrix)
    ret = future / price - 1
    ret = ret.where(member & price.notna())
    return ret.iloc[:-weeks] if weeks else ret

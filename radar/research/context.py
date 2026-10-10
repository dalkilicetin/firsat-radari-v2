"""Piyasa bağlamı: sektör ETF'leri ve piyasa dönemi.

- Hisse başına (kesitsel sıralanabilir): hissenin sektör ETF'inin son 13 hafta ve 12-1 ay getirisi, QQQ'ya göre beta.
- Dönem (o hafta tüm hisseler için aynı; yalnızca ağaç modellerinde anlamlı): QQQ'nun 13 haftalık getirisi,
  40 haftalık ortalamanın üstünde mi, piyasa oynaklığı, küçük/büyük şirket farkı (IWM − SPY).
Sektör eşlemesi SEC SIC kodundan; ETF fiyatları arşivdeki günlük fiyatlardan (yalnızca o Cuma'ya kadarki kapanışlar).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive
from radar.research import sectors
from radar.research.panel import weekly_last

# (SIC aralığı başlangıç, bitiş, ETF) — ilk eşleşen kullanılır.
SIC_ETF = [
    (3674, 3674, "SMH"), (3559, 3559, "SMH"), (3672, 3672, "SMH"), (3825, 3825, "SMH"),
    (7370, 7379, "IGV"),
    (2836, 2836, "XBI"), (8731, 8731, "XBI"), (2833, 2835, "XLV"), (3841, 3845, "XLV"), (8000, 8099, "XLV"),
    (1300, 1399, "XLE"), (2911, 2911, "XLE"), (4922, 4925, "XLE"), (2990, 2999, "XLE"),
    (3720, 3729, "ITA"), (3760, 3769, "ITA"), (3812, 3812, "ITA"),
    (1000, 1099, "GDX"), (1040, 1040, "GDX"),
    (4911, 4991, "XLU"),
    (1520, 1531, "XHB"), (2430, 2452, "XHB"),
    (4512, 4522, "JETS"),
    (5200, 5999, "XRT"), (5000, 5199, "XLY"), (7000, 7099, "XLY"), (7800, 7999, "XLY"), (5800, 5899, "XLY"),
    (6000, 6499, "XLF"), (6500, 6599, "XLRE"),
    (4800, 4899, "XLC"), (2700, 2799, "XLC"),
    (2000, 2199, "XLP"), (2840, 2844, "XLP"),
    (2800, 2899, "XLB"), (3300, 3399, "XLB"), (2600, 2699, "XLB"),
    (3500, 3599, "XLI"), (3600, 3699, "XLK"), (3700, 3799, "XLI"), (4000, 4799, "XLI"), (8700, 8799, "XLI"),
    (3800, 3899, "XLK"),
]
DEFAULT_ETF = "IWM"


def etf_for_sic(code: str) -> str:
    try:
        c = int(code)
    except (TypeError, ValueError):
        return DEFAULT_ETF
    for lo, hi, etf in SIC_ETF:
        if lo <= c <= hi:
            return etf
    return DEFAULT_ETF


def etf_prices(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Haftalık (Cuma) düzeltilmiş kapanış, ETF başına sütun."""
    from radar.backfill.market import BENCHMARKS
    px = archive.load("prices", columns=["symbol", "date", "adjclose"],
                      filters=[("symbol", "in", BENCHMARKS)])
    if px.empty:
        return pd.DataFrame(index=dates)
    return weekly_last(px.rename(columns={"symbol": "cik"}), "adjclose", dates)


def signals(p: dict) -> dict[str, pd.DataFrame]:
    price = p["price"]
    dates, cols = price.index, price.columns
    etf = etf_prices(dates)
    if etf.empty or "QQQ" not in etf:
        return {}
    sic = sectors.load_sic().reindex(cols).fillna("")
    sector = pd.Series([etf_for_sic(c) for c in sic], index=cols)
    r13 = etf / etf.shift(13) - 1
    r12_1 = etf.shift(4) / etf.shift(52) - 1
    to_stock = lambda m: pd.DataFrame({c: m[sector[c]] if sector[c] in m else np.nan for c in cols}, index=dates)
    wret = price / price.shift(1) - 1
    q = etf["QQQ"] / etf["QQQ"].shift(1) - 1
    cov = wret.rolling(52, min_periods=26).cov(q)
    beta = cov.div(q.rolling(52, min_periods=26).var(), axis=0)
    return {"sektor_getiri_13h": to_stock(r13), "sektor_momentum_12_1": to_stock(r12_1), "beta_qqq": beta}


def regime(dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Dönem özellikleri (tarih × özellik); yalnızca o haftaya kadarki fiyatlar."""
    etf = etf_prices(dates)
    if etf.empty or "QQQ" not in etf:
        return pd.DataFrame(index=dates)
    q = etf["QQQ"]
    wq = q / q.shift(1) - 1
    out = pd.DataFrame({
        "piyasa_13h": q / q.shift(13) - 1,
        "piyasa_52h": q / q.shift(52) - 1,
        "piyasa_trend_ustu": (q > q.rolling(40, min_periods=20).mean()).astype(float),
        "piyasa_oynaklik": wq.rolling(13, min_periods=8).std() * np.sqrt(52),
    }, index=dates)
    if "IWM" in etf and "SPY" in etf:
        out["kucuk_buyuk_13h"] = (etf["IWM"] / etf["IWM"].shift(13)) - (etf["SPY"] / etf["SPY"].shift(13))
    return out

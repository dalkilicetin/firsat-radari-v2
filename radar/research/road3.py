"""3. yol: kurumsal sinyaller (içeriden işlemler, fon pozisyonları, 8-K olayları, geri alımlar).

Her sinyal, yalnızca kullanılabilir olduğu ilk Cuma'dan itibaren panelde görünür.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit, rolling_count, weekly

MIN_PURCHASE = 10_000  # $; daha küçük alımlar sinyal sayılmaz
EIGHT_K_ITEMS = {"1.01": "önemli anlaşma", "1.02": "anlaşma feshi", "2.01": "satın alma/elden çıkarma tamamlandı",
                 "2.03": "yeni borç yükümlülüğü", "3.02": "kayıtsız hisse satışı (sulandırma)",
                 "5.02": "yönetici değişikliği", "7.01": "kamuyu aydınlatma (FD)", "8.01": "diğer olaylar"}


def insider_signals(dates, columns, shares: pd.DataFrame, raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    ins = archive.load("insider", columns=["issuer_cik", "owner_cik", "relationship", "owner_title", "code",
                                           "shares", "price", "available_date"])
    ins = ins.dropna(subset=["issuer_cik", "available_date"])
    # Açık piyasa alımı: P kodu, fiyat > 0 (0 fiyatlılar yanlış kodlanmış özel işlemlerdir), en az 10 bin $.
    buys = ins[(ins.code == "P") & (ins.price > 0)].copy()
    buys["value"] = buys.shares * buys.price
    buys = buys[buys.value >= MIN_PURCHASE]
    buys = buys.assign(cik=buys.issuer_cik.astype("int64").astype(str), date=buys.available_date)
    distinct = buys.drop_duplicates(["cik", "owner_cik", "date"])
    title = buys.owner_title.fillna("").str.upper()
    top = buys[title.str.contains(r"\bCEO\b|CHIEF EXECUTIVE|\bCFO\b|CHIEF FINANCIAL|PRESIDENT")]
    n_buyers_90 = rolling_count(distinct[["cik", "date"]], dates, columns, 90)
    value_90 = _rolling_sum(buys[["cik", "date", "value"]], dates, columns, 90)
    mcap = shares * raw
    return {
        "icerden_alici_sayisi_90g": n_buyers_90.where(n_buyers_90 > 0),
        "icerden_alim_kumesi_3plus": n_buyers_90 >= 3,
        "icerden_alim_tutar_piyasa_degeri": (value_90 / mcap).where(value_90 > 0),
        "ust_yonetici_alimi_90g": rolling_count(top.drop_duplicates(["cik", "owner_cik", "date"])[["cik", "date"]],
                                                dates, columns, 90) > 0,
    }


def _rolling_sum(ev: pd.DataFrame, dates, columns, window_days) -> pd.DataFrame:
    wide = weekly(ev, dates, columns, "sum")
    w = wide.reindex(wide.index.union(dates)).fillna(0)
    return w.rolling(f"{window_days}D").sum().reindex(dates).fillna(0)


def cusip_to_cik() -> pd.DataFrame:
    """FTD'deki CUSIP → sembol eşleşmesini, Form 4 sembol geçmişiyle zaman aralığı örtüşmesine göre CIK'e bağlar."""
    cmap = archive.load("ftd", names=["cusip_map"])
    hist = pd.read_parquet(config.DATA_DIR / "derived" / "identity_tickers.parquet")
    m = cmap.merge(hist, left_on="symbol", right_on="ticker", suffixes=("_c", "_t"))
    overlap = (m.first_seen_c <= m.last_seen_t + pd.Timedelta(days=180)) & (m.last_seen_c >= m.first_seen_t - pd.Timedelta(days=180))
    m = m[overlap].sort_values("days", ascending=False).drop_duplicates("cusip")
    return m[["cusip", "cik"]]


def holdings_signals(dates, columns, shares: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Çeyreklik 13F: kurumsal sahip sayısı ve tutulan hisse değişimi. Kullanılabilirlik: dönem sonu + 46 gün."""
    cmap = cusip_to_cik()
    rows = []
    for name in sorted(archive.entries("holdings")):
        df = archive.load("holdings", names=[name], columns=["filer_cik", "period", "cusip", "shares", "share_type",
                                                             "put_call", "is_amendment", "amendment_type"])
        df = df[(df.share_type == "SH") & (df.put_call == "") &
                ~(df.is_amendment & (df.amendment_type == "NEW HOLDINGS"))]
        df = df.merge(cmap, on="cusip")
        rows.append(df.groupby(["period", "cik"]).agg(holders=("filer_cik", "nunique"), inst_shares=("shares", "sum")).reset_index())
    agg = pd.concat(rows).groupby(["period", "cik"]).agg(holders=("holders", "max"), inst_shares=("inst_shares", "max")).reset_index()
    agg["date"] = agg.period + pd.Timedelta(days=46)
    agg = agg.sort_values(["cik", "period"])
    agg["holders_chg"] = agg.groupby("cik").holders.pct_change(fill_method=None)
    agg["inst_shares_chg"] = agg.groupby("cik").inst_shares.diff()
    holders_chg = pit(agg[["cik", "date"]].assign(value=agg.holders_chg), dates, columns, 120)
    inst_chg = pit(agg[["cik", "date"]].assign(value=agg.inst_shares_chg), dates, columns, 120)
    holders = pit(agg[["cik", "date"]].assign(value=agg.holders), dates, columns, 120)
    return {"kurumsal_sahip_degisimi": holders_chg.where(holders >= 5),
            "kurumsal_hisse_degisimi_payi": (inst_chg / shares).where(holders >= 5)}


def eight_k_signals(dates, columns) -> dict[str, pd.DataFrame]:
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    ek = f[f.form == "8-K"]
    items = ek["items"].fillna("")
    out = {}
    for code, label in EIGHT_K_ITEMS.items():
        ev = ek[items.str.contains(rf"\b{code.replace('.', r'\.')}\b")].rename(columns={"filing_date": "date"})[["cik", "date"]]
        out[f"8k_{code}_{label}"] = rolling_count(ev, dates, columns, 30) > 0
    return out


def buyback_signal(dates, columns, shares: pd.DataFrame, raw: pd.DataFrame) -> dict[str, pd.DataFrame]:
    fin = archive.load("financials", columns=["cik", "tag", "value", "accepted", "qtrs", "ddate"])
    fin = fin[(fin.tag == "PaymentsForRepurchaseOfCommonStock") & (fin.qtrs == 4)]
    fin = fin[fin.ddate == fin.groupby(["cik", "accepted"]).ddate.transform("max")]
    bb = pit(fin.rename(columns={"accepted": "date"})[["cik", "date", "value"]], dates, columns, FUNDAMENTAL_MAX_AGE)
    return {"geri_alim_getirisi": (bb / (shares * raw)).where(bb > 0)}


def signals(p: dict) -> dict[str, pd.DataFrame]:
    price, raw = p["price"], p["raw"]
    dates, cols = price.index, price.columns
    fin = archive.load("financials", columns=["cik", "tag", "value", "accepted", "qtrs", "ddate"])
    sh = fin[fin.tag.isin(["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"]) & (fin.qtrs == 0)]
    sh = sh[sh.ddate == sh.groupby(["cik", "accepted"]).ddate.transform("max")]
    shares = pit(sh.rename(columns={"accepted": "date"})[["cik", "date", "value"]], dates, cols, FUNDAMENTAL_MAX_AGE)
    out = {}
    out |= insider_signals(dates, cols, shares, raw)
    out |= holdings_signals(dates, cols, shares)
    out |= eight_k_signals(dates, cols)
    out |= buyback_signal(dates, cols, shares, raw)
    return out

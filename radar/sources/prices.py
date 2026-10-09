"""Günlük fiyatlar: Stooq ve Yahoo, birbirine karşı çapraz kontrol edilir.

İkisi de resmî kaynak değildir; bu yüzden aynı günün kapanışı iki kaynakta tutmuyorsa
o hissenin fiyatı güvenilmez sayılır.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime, timezone
from statistics import median

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "prices", "Günlük fiyatlar (Stooq ↔ Yahoo)", 2, [1, 2, 3, 4]

STOOQ = "https://stooq.com/q/d/l/?s={sym}.us&i=d"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={range}&interval=1d&events=split,div&includeAdjustedClose=true"

# Borsadan çıkmış hisseler: geriye dönük testte hayatta kalan yanılgısını önlemek için gerekir.
DELISTED = {"SIVB": "SVB Financial (2023)", "ATVI": "Activision Blizzard (2023)", "SGEN": "Seagen (2023)"}


def parse_stooq(text: str) -> dict[date, dict]:
    if not text.startswith("Date"):
        return {}
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        try:
            out[date.fromisoformat(r["Date"])] = {"close": float(r["Close"]), "volume": float(r.get("Volume") or 0)}
        except (ValueError, KeyError):
            continue
    return out


def parse_yahoo(data: dict) -> tuple[dict[date, dict], list[date]]:
    result = (data.get("chart", {}).get("result") or [None])[0]
    if not result or not result.get("timestamp"):
        return {}, []
    quote = result["indicators"]["quote"][0]
    adj = (result["indicators"].get("adjclose") or [{}])[0].get("adjclose") or [None] * len(result["timestamp"])
    out = {}
    for ts, close, a, vol in zip(result["timestamp"], quote["close"], adj, quote["volume"]):
        if close is None:
            continue
        d = datetime.fromtimestamp(ts, tz=timezone.utc).date()
        out[d] = {"close": float(close), "adjclose": float(a) if a is not None else None, "volume": float(vol or 0)}
    splits = [datetime.fromtimestamp(int(s["date"]), tz=timezone.utc).date()
              for s in (result.get("events", {}).get("splits") or {}).values()]
    return out, splits


def pct_diff(a: float, b: float) -> float:
    return abs(a - b) / b * 100 if b else float("inf")


def big_jumps(series: dict[date, dict], key: str = "close", limit: float = 0.6) -> list[date]:
    days = sorted(series)
    return [d for prev, d in zip(days, days[1:])
            if series[prev][key] and abs(series[d][key] / series[prev][key] - 1) > limit]


def fetch(ctx: Context, sym: str, yahoo_range: str = "1y"):
    try:
        stooq = parse_stooq(ctx.client.get(STOOQ.format(sym=sym.lower().replace(".", "-"))).text)
    except FetchError:
        stooq = {}
    try:
        yahoo, splits = parse_yahoo(ctx.client.get(YAHOO.format(sym=sym.replace(".", "-"), range=yahoo_range),
                                                   ok_statuses=(200,)).json())
    except FetchError:
        yahoo, splits = {}, []
    return stooq, yahoo, splits


def run(ctx: Context, rep: SourceReport) -> None:
    symbols = ["AAPL", "MSFT", "NVDA"] + ctx.sample_symbols(12)
    stooq_ok = yahoo_ok = agree = compared = 0
    fresh_days, details, jumpy = [], [], []
    close_vs_adj = {"close": [], "adjclose": []}

    for sym in symbols:
        stooq, yahoo, splits = fetch(ctx, sym)
        stooq_ok += bool(stooq)
        yahoo_ok += bool(yahoo)
        for series in (stooq, yahoo):
            if series:
                fresh_days.append(max(series))
        if stooq and yahoo:
            common = sorted(set(stooq) & set(yahoo))[-60:]
            if len(common) >= 20:
                compared += 1
                medians = {}
                for key in ("close", "adjclose"):
                    diffs = [pct_diff(stooq[d]["close"], yahoo[d][key]) for d in common if yahoo[d].get(key)]
                    if diffs:
                        medians[key] = median(diffs)
                        close_vs_adj[key].append(medians[key])
                best = min(medians.values(), default=99.0)
                agree += best < 0.5
                details.append(f"{sym}: %{best:.2f}")
        for name, series in (("stooq", stooq), ("yahoo", yahoo)):
            jumps = [d for d in big_jumps(series) if not any(abs((d - s).days) <= 3 for s in splits)]
            if jumps:
                jumpy.append(f"{name}:{sym}:{jumps[:2]}")

    rep.expect_min_ratio("Stooq veri dönen hisse", stooq_ok, len(symbols), 0.9, 0.7)
    rep.expect_min_ratio("Yahoo veri dönen hisse", yahoo_ok, len(symbols), 0.9, 0.7)
    rep.expect_min_ratio("Çapraz kontrol: son 60 gün kapanışlar %0,5 içinde", agree, compared, 0.9, 0.75)
    rep.add("Çapraz kontrol detayı (medyan fark)", Status.INFO, ", ".join(details))
    if close_vs_adj["close"] and close_vs_adj["adjclose"]:
        rep.add("Stooq hangi Yahoo serisine yakın", Status.INFO,
                f"ham kapanış: %{median(close_vs_adj['close']):.3f}, düzeltilmiş: %{median(close_vs_adj['adjclose']):.3f}")
    rep.add("Bölünme dışı %60+ günlük sıçrama", Status.WARN if jumpy else Status.OK,
            "; ".join(jumpy) if jumpy else "yok")
    if fresh_days:
        rep.expect_fresh("Fiyat güncelliği (en eski son bar)", min(fresh_days), 5, ctx.today)

    # NVDA 10'a 1 bölünmesi (10 Haziran 2024): seri düzeltilmemişse %90 düşüş görünür.
    stooq, yahoo, _ = fetch(ctx, "NVDA", "5y")
    for name, series in (("Stooq", stooq), ("Yahoo", yahoo)):
        before, after = series.get(date(2024, 6, 7)), series.get(date(2024, 6, 10))
        if before and after:
            change = after["close"] / before["close"] - 1
            rep.add(f"{name}: NVDA bölünmesi düzeltilmiş", Status.OK if abs(change) < 0.15 else Status.FAIL,
                    f"7→10 Haziran 2024 değişim %{change * 100:.1f}")
        else:
            rep.add(f"{name}: NVDA bölünmesi düzeltilmiş", Status.WARN, "2024-06-07/10 barı yok")

    found = []
    for sym, label in DELISTED.items():
        stooq, yahoo, _ = fetch(ctx, sym, "max")
        found.append(f"{sym} ({label}): stooq={'var' if stooq else 'yok'}, yahoo={'var' if yahoo else 'yok'}")
    rep.add("Borsadan çıkmış hisselerin geçmiş fiyatı", Status.INFO, "; ".join(found))

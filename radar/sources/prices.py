"""Günlük fiyatlar: Yahoo, Nasdaq ve Stooq birbirine karşı çapraz kontrol edilir.

Hiçbiri resmî ve garantili bir kaynak değildir; bu yüzden aynı günün kapanışı en az iki kaynakta
tutmuyorsa o hissenin fiyatı güvenilmez sayılır.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime, timedelta, timezone
from itertools import combinations
from statistics import median

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "prices", "Günlük fiyatlar (Yahoo ↔ Nasdaq ↔ Stooq)", 2, [1, 2, 3, 4]

STOOQ = "https://stooq.com/q/d/l/?s={sym}.us&i=d"
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range={range}&interval=1d&events=split,div&includeAdjustedClose=true"
NASDAQ = "https://api.nasdaq.com/api/quote/{sym}/historical"
# Nasdaq API'si tarayıcı benzeri başlık ister.
NASDAQ_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                  "Accept": "application/json, text/plain, */*", "Origin": "https://www.nasdaq.com",
                  "Referer": "https://www.nasdaq.com/"}

# Borsadan çıkmış hisseler: geriye dönük testte hayatta kalan yanılgısını önlemek için gerekir.
DELISTED = {"SIVB": "SVB Financial (2023)", "ATVI": "Activision Blizzard (2023)", "SGEN": "Seagen (2023)"}

Series = dict[date, dict]


def parse_stooq(text: str) -> Series:
    if not text.startswith("Date"):
        return {}
    out = {}
    for r in csv.DictReader(io.StringIO(text)):
        try:
            out[date.fromisoformat(r["Date"])] = {"close": float(r["Close"]), "volume": float(r.get("Volume") or 0)}
        except (ValueError, KeyError):
            continue
    return out


def parse_yahoo(data: dict) -> tuple[Series, list[date]]:
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


def parse_nasdaq(data: dict) -> Series:
    rows = ((data.get("data") or {}).get("tradesTable") or {}).get("rows") or []
    out = {}
    for r in rows:
        try:
            d = datetime.strptime(r["date"], "%m/%d/%Y").date()
            out[d] = {"close": float(r["close"].replace("$", "").replace(",", "")),
                      "volume": float((r.get("volume") or "0").replace(",", "") or 0)}
        except (KeyError, ValueError, AttributeError):
            continue
    return out


def pct_diff(a: float, b: float) -> float:
    return abs(a - b) / b * 100 if b else float("inf")


def big_jumps(series: Series, key: str = "close", limit: float = 0.6) -> list[date]:
    days = sorted(series)
    return [d for prev, d in zip(days, days[1:])
            if series[prev][key] and abs(series[d][key] / series[prev][key] - 1) > limit]


def agreement(a: Series, b: Series, last: int = 60) -> float | None:
    """İki serinin son ortak `last` günündeki kapanışlarının medyan yüzde farkı."""
    common = sorted(set(a) & set(b))[-last:]
    if len(common) < 20:
        return None
    return median(pct_diff(a[d]["close"], b[d]["close"]) for d in common)


def fetch_all(ctx: Context, sym: str, days: int = 365) -> tuple[dict[str, Series], list[date], dict[str, str]]:
    """Üç kaynaktan seri, Yahoo'nun bölünme tarihleri ve boş dönen kaynaklar için kısa tanı notu."""
    series: dict[str, Series] = {}
    notes: dict[str, str] = {}
    splits: list[date] = []
    yrange = "1y" if days <= 365 else "5y" if days <= 5 * 365 else "max"

    try:
        series["yahoo"], splits = parse_yahoo(ctx.client.get(YAHOO.format(sym=sym.replace(".", "-"), range=yrange)).json())
    except (FetchError, ValueError) as exc:
        series["yahoo"], notes["yahoo"] = {}, str(exc)[:120]

    try:
        params = {"assetclass": "stocks", "fromdate": (ctx.today - timedelta(days=days)).isoformat(),
                  "todate": ctx.today.isoformat(), "limit": 9999}
        resp = ctx.client.get(NASDAQ.format(sym=sym.replace(".", "/")), params=params, headers=NASDAQ_HEADERS)
        series["nasdaq"] = parse_nasdaq(resp.json())
        if not series["nasdaq"]:
            notes["nasdaq"] = resp.text[:120]
    except (FetchError, ValueError) as exc:
        series["nasdaq"], notes["nasdaq"] = {}, str(exc)[:120]

    try:
        resp = ctx.client.get(STOOQ.format(sym=sym.lower().replace(".", "-")))
        series["stooq"] = parse_stooq(resp.text)
        if not series["stooq"]:
            notes["stooq"] = resp.text[:120]
    except FetchError as exc:
        series["stooq"], notes["stooq"] = {}, str(exc)[:120]
    return series, splits, notes


def run(ctx: Context, rep: SourceReport) -> None:
    symbols = ["AAPL", "MSFT", "NVDA"] + ctx.sample_symbols(12)
    got = {"yahoo": 0, "nasdaq": 0, "stooq": 0}
    pair_diffs: dict[tuple[str, str], list[float]] = {}
    confirmed, fresh_days, jumpy, notes_seen = 0, [], [], {}

    for sym in symbols:
        series, splits, notes = fetch_all(ctx, sym)
        for k, v in notes.items():
            notes_seen.setdefault(k, f"{sym}: {v}")
        for name, s in series.items():
            if s:
                got[name] += 1
                fresh_days.append(max(s))
                jumps = [d for d in big_jumps(s) if not any(abs((d - x).days) <= 3 for x in splits)]
                if jumps:
                    jumpy.append(f"{name}:{sym}:{[str(d) for d in jumps[:2]]}")
        sym_ok = False
        for a, b in combinations(series, 2):
            diff = agreement(series[a], series[b])
            if diff is not None:
                pair_diffs.setdefault((a, b), []).append(diff)
                sym_ok |= diff < 0.5
        confirmed += sym_ok

    for name, n in got.items():
        check = rep.expect_min_ratio(f"{name.capitalize()}: veri dönen hisse", n, len(symbols), 0.9, 0.7)
        if name in notes_seen and n < len(symbols):
            check.detail += f" — örnek yanıt: {notes_seen[name]}"
    rep.expect_min_ratio("Çapraz kontrol: en az iki kaynak %0,5 içinde (son 60 gün)", confirmed, len(symbols), 0.9, 0.75)
    for (a, b), diffs in pair_diffs.items():
        rep.add(f"{a} ↔ {b} medyan fark", Status.INFO, f"%{median(diffs):.3f} ({len(diffs)} hisse)")
    rep.add("Bölünme dışı %60+ günlük sıçrama", Status.WARN if jumpy else Status.OK, "; ".join(jumpy) or "yok")
    if fresh_days:
        rep.expect_fresh("Fiyat güncelliği (en eski son bar)", min(fresh_days), 5, ctx.today)

    # NVDA 10'a 1 bölünmesi (10 Haziran 2024): seri düzeltilmemişse %90 düşüş görünür.
    series, _, _ = fetch_all(ctx, "NVDA", days=(ctx.today - date(2024, 5, 1)).days)
    for name, s in series.items():
        before, after = s.get(date(2024, 6, 7)), s.get(date(2024, 6, 10))
        if before and after:
            change = after["close"] / before["close"] - 1
            adjusted = abs(change) < 0.15
            rep.add(f"{name}: NVDA bölünmesi düzeltilmiş", Status.OK if adjusted else Status.INFO,
                    f"7→10 Haziran 2024 değişim %{change * 100:.1f}"
                    + ("" if adjusted else " — ham fiyat; bölünme düzeltmesi bizim tarafta yapılmalı"))
        else:
            rep.add(f"{name}: NVDA bölünmesi düzeltilmiş", Status.INFO, "2024-06-07/10 barı yok")

    found = []
    for sym, label in DELISTED.items():
        series, _, _ = fetch_all(ctx, sym, days=365 * 6)
        found.append(f"{sym} ({label}): " + ", ".join(f"{k}={'var' if v else 'yok'}" for k, v in series.items()))
    rep.add("Borsadan çıkmış hisselerin geçmiş fiyatı", Status.INFO, "; ".join(found))

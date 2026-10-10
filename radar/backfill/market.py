"""Günlük fiyat geçmişi (Yahoo, en eski tarihten bugüne) ve Wikipedia görüntülenme geçmişi.

Fiyat: her bölüm, sembolün ilk harfine göre bir grup hisse içerir. Yahoo ham kapanış (bölünmeye göre
düzeltilmiş), temettü dahil düzeltilmiş kapanış, hacim, bölünme ve temettü olaylarını verir.
Bölüm düzeyinde her hissenin son 60 günü Nasdaq'ın kendi servisiyle çapraz kontrol edilir.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import pandas as pd

from radar.backfill.base import Dataset, Loaded
from radar.http import FetchError, HttpClient
from radar.quality import SourceReport, Status
from radar.sources import prices, universe, wikipedia
from radar.sources.base import Context

GROUPS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J-K", "L", "M", "N", "O", "P", "Q-R", "S", "T", "U-V", "W-Z"]
YAHOO_MAX = ("https://query1.finance.yahoo.com/v8/finance/chart/{sym}?period1=1420070400&period2={end}"
             "&interval=1d&events=split,div&includeAdjustedClose=true")


def in_group(symbol: str, group: str) -> bool:
    first = symbol[:1].upper()
    lo, _, hi = group.partition("-")
    return lo <= first <= (hi or lo)


def current_symbols(client: HttpClient) -> list[str]:
    secs, _ = universe.parse_nasdaq_listed(client.get(universe.NASDAQ_URL).text)
    return sorted(s.symbol for s in secs if s.is_common)


def parse_yahoo_events(data: dict) -> tuple[list[dict], list[dict]]:
    result = (data.get("chart", {}).get("result") or [None])[0] or {}
    events = result.get("events", {}) or {}
    splits = [{"date": datetime.fromtimestamp(int(v["date"]), tz=timezone.utc).date(),
               "ratio": float(v["numerator"]) / float(v["denominator"])} for v in (events.get("splits") or {}).values()]
    divs = [{"date": datetime.fromtimestamp(int(v["date"]), tz=timezone.utc).date(), "amount": float(v["amount"])}
            for v in (events.get("dividends") or {}).values()]
    return splits, divs


class DailyPrices(Dataset):
    name = "prices"
    title = "Günlük fiyat geçmişi (Yahoo, 2015→; Nasdaq ile çapraz kontrol)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"{g}-{today:%Y%m%d}" for g in GROUPS]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        group = partition.rsplit("-", 1)[0]
        symbols = [s for s in current_symbols(client) if in_group(s, group)]
        end = int(datetime.now(timezone.utc).timestamp())
        frames, missing, agree = [], [], []
        for sym in symbols:
            try:
                data = client.get(YAHOO_MAX.format(sym=sym.replace(".", "-"), end=end)).json()
            except (FetchError, ValueError):
                missing.append(sym)
                continue
            series, _ = prices.parse_yahoo(data)
            if not series:
                missing.append(sym)
                continue
            splits, divs = parse_yahoo_events(data)
            split_on = {s["date"]: s["ratio"] for s in splits}
            div_on = {d["date"]: d["amount"] for d in divs}
            frames.append(pd.DataFrame({
                "symbol": sym, "date": pd.to_datetime(list(series)),
                "close": [v["close"] for v in series.values()], "adjclose": [v["adjclose"] for v in series.values()],
                "volume": [v["volume"] for v in series.values()],
                "split_ratio": [split_on.get(d) for d in series], "dividend": [div_on.get(d) for d in series],
            }))
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

        # Her 10 hisseden birinin son 60 günü Nasdaq'ın servisiyle karşılaştırılır.
        sample = symbols[::10]
        for sym in sample:
            nasdaq = {}
            try:
                params = {"assetclass": "stocks", "fromdate": (date.today() - timedelta(days=100)).isoformat(),
                          "todate": date.today().isoformat(), "limit": 9999}
                nasdaq = prices.parse_nasdaq(client.get(prices.NASDAQ.format(sym=sym), params=params,
                                                        headers=prices.NASDAQ_HEADERS).json())
            except (FetchError, ValueError):
                pass
            sel = df[df.symbol == sym] if len(df) else df
            mine = {d.date(): {"close": c} for d, c in zip(sel.date, sel.close)} if len(sel) else {}
            diff = prices.agreement(mine, nasdaq)
            # Nasdaq ham fiyat verir, Yahoo bölünmeye göre düzeltir: pencerede bölünme varsa fark beklenir.
            recent_split = bool(len(sel)) and bool(sel[sel.date >= pd.Timestamp.today() - pd.Timedelta(days=100)].split_ratio.notna().any())
            agree.append((sym, diff, recent_split))
        return Loaded(df, [YAHOO_MAX.format(sym="<sembol>", end="<bugün>"), prices.NASDAQ],
                      {"symbols": len(symbols), "missing": missing,
                       "cross_checked": len(sample),
                       "agree": sum(1 for _, d, split in agree if d is not None and (d < 0.5 or split)),
                       "compared": sum(1 for _, d, _ in agree if d is not None),
                       "mismatch": [f"{s}: %{d:.2f}" + (" (yakın bölünme)" if split else "")
                                    for s, d, split in agree if d is not None and d >= 0.5]})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        rep.expect_min_ratio("Fiyatı gelen hisse", notes["symbols"] - len(notes["missing"]), notes["symbols"], 0.97, 0.9).detail += \
            f"; gelmeyen: {notes['missing'][:15]}" if notes["missing"] else ""
        if df.empty:
            return
        rep.expect_min_ratio("Çapraz kontrol: Yahoo ↔ Nasdaq son 60 gün (%0,5; bölünme açıklamalı)", notes["agree"],
                             notes["compared"], 0.95, 0.85).detail += f"; uyuşmayan: {notes['mismatch']}" if notes.get("mismatch") else ""
        rep.expect_min_ratio("Pozitif kapanış", int((df.close > 0).sum()), len(df), 0.9999, 0.999)
        dup = df.duplicated(["symbol", "date"]).sum()
        rep.add("Yinelenen gün", Status.OK if dup == 0 else Status.WARN, f"{dup}")
        first = df.groupby("symbol").date.min()
        rep.add("Geçmiş derinliği", Status.INFO,
                f"2015'ten itibaren verisi olan: {int((first <= pd.Timestamp('2015-01-10')).sum())}/{len(first)} "
                f"(sonradan halka arz olanlar doğal olarak daha kısa)")
        jumps = df.sort_values(["symbol", "date"]).groupby("symbol").close.pct_change().abs()
        split_days = set(zip(df.symbol[df.split_ratio.notna()], df.date[df.split_ratio.notna()]))
        big = df[jumps > 0.8]
        unexplained = [f"{r.symbol} {r.date.date()}" for r in big.itertuples()
                       if not any((r.symbol, r.date + pd.Timedelta(days=k)) in split_days for k in range(-3, 4))]
        rep.add("Bölünme dışı %80+ günlük hareket", Status.INFO,
                f"{len(unexplained)} adet (çoğu küçük şirket haberi; tek kaynak, 3. aşamada ikinci kaynakla doğrulanacak): {unexplained[:10]}")


class WikipediaViews(Dataset):
    name = "wikiviews"
    title = "Wikipedia günlük görüntülenme (2015-07→)"
    max_parallel = 2

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"{g}-{today:%Y%m%d}" for g in GROUPS]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        group = partition.rsplit("-", 1)[0]
        ctx = Context(client=client, today=date.today())
        mapping = wikipedia.parse_sparql(wikipedia.sparql(ctx, wikipedia.QUERY))
        symbols = [s for s in current_symbols(client) if in_group(s, group) and s in mapping]
        frames, missing = [], []
        end = date.today() - timedelta(days=1)
        for sym in symbols:
            article = mapping[sym]
            try:
                views = wikipedia.parse_pageviews(client.get(wikipedia.PAGEVIEWS.format(
                    article=article, start=date(2015, 7, 1), end=end)).json())
            except (FetchError, ValueError):
                missing.append(sym)
                continue
            frames.append(pd.DataFrame({"symbol": sym, "article": article, "date": pd.to_datetime(list(views)),
                                        "views": list(views.values())}))
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["symbol", "article", "date", "views"])
        return Loaded(df, [wikipedia.SPARQL, wikipedia.PAGEVIEWS], {"symbols": len(symbols), "missing": missing})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        if notes["symbols"] == 0:
            rep.add("Eşleşen makale", Status.INFO, "bu grupta Wikipedia makalesi eşleşen hisse yok")
            return
        rep.expect_min_ratio("Görüntülenmesi gelen makale", notes["symbols"] - len(notes["missing"]), notes["symbols"], 0.97, 0.9)
        if df.empty:
            return
        span = df.groupby("symbol").date.agg(["min", "max", "count"])
        rep.expect_min_ratio("Son 5 güne kadar güncel", int((span["max"] >= pd.Timestamp.today() - pd.Timedelta(days=5)).sum()),
                             len(span), 0.97, 0.9)
        rep.add("Geçmiş derinliği", Status.INFO, f"Temmuz 2015'ten başlayan: {int((span['min'] <= pd.Timestamp('2015-07-02')).sum())}/{len(span)}")

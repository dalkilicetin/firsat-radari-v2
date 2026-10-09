"""Borsadan çıkmış hisseler için kaynaklar.

1. SEC Fails-to-Deliver (FTD): ayda iki dosya; her satırda takas tarihi, CUSIP, sembol, açıklama ve fiyat.
   SEC'e göre fiyat, takas tarihinden önceki işlem gününün kapanışıdır. Yalnızca o gün teslim
   başarısızlığı olan hisseler listelenir; bu yüzden fiyat serisi seyrek ama borsadan çıkmışları da içerir.
   Yan ürün: CUSIP → sembol eşleştirmesi (13F pozisyonlarını hisselere bağlamak için).
2. Tiingo hisse listesi: her sembolün borsası ve veri başlangıç/bitiş tarihi (kimlik gerekmez).
   Hayatta kalan yanılgısı olmayan bir evren listesi için kullanılır.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from radar.backfill.base import Dataset, Loaded, links, read_zip_member, to_date, to_number
from radar.http import FetchError, HttpClient
from radar.quality import SourceReport, Status
from radar.sources import prices

FTD_PAGE = "https://www.sec.gov/data-research/sec-markets-data/fails-deliver-data"
TIINGO_LIST = "https://apimedia.tiingo.com/docs/tiingo/daily/supported_tickers.zip"
CUSIP_RE = r"^[0-9A-Z]{8}[0-9]$"

# Borsadan çıkmış örnekler ve yaklaşık çıkış tarihleri.
DELISTED_PROBES = {"SIVB": "2023-03", "ATVI": "2023-10", "SGEN": "2023-12"}


class FailsToDeliver(Dataset):
    name = "ftd"
    title = "SEC fails-to-deliver (fiyat + CUSIP eşleştirmesi, 2015→)"
    max_parallel = 3

    def _links(self, client: HttpClient) -> dict[str, list[str]]:
        by_year: dict[str, list[str]] = {}
        for key, url in links(client, FTD_PAGE, r"cnsfails(\d{6}[ab])\.zip").items():
            by_year.setdefault(key[:4], []).append(url)
        return by_year

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return sorted(y for y in self._links(client) if y >= "2015")

    def load(self, client: HttpClient, partition: str) -> Loaded:
        urls = sorted(self._links(client)[partition])
        frames = []
        for url in urls:
            df = read_zip_member(client.get(url, timeout=300).content, "", sep="|")  # üye adının uzantısı yok
            df = df.rename(columns={"SETTLEMENT DATE": "SETTLE", "QUANTITY (FAILS)": "QTY"})
            frames.append(df)
        df = pd.concat(frames, ignore_index=True)
        out = pd.DataFrame({
            "settle_date": to_date(df["SETTLE"], "%Y%m%d"),
            "cusip": df["CUSIP"].str.strip().str.upper(),
            "symbol": df["SYMBOL"].str.strip().str.upper(),
            "qty": to_number(df["QTY"]),
            "description": df["DESCRIPTION"].str.strip(),
            "price": to_number(df["PRICE"]),
        })
        out = out[out.settle_date.notna()]  # dosya sonu özet satırları
        return Loaded(out, urls, {"files": len(urls), "columns": list(df.columns)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        n = len(df)
        rep.expect_range("Dosya sayısı (ayda 2)", loaded.notes["files"], 2, 24)
        rep.expect_range("Satır sayısı", n, 50_000, 5_000_000)
        rep.expect_min_ratio("Takas tarihi yıl içinde", int((df.settle_date.dt.year == int(partition)).sum()), n, 0.995, 0.98)
        rep.expect_min_ratio("Geçerli CUSIP", int(df.cusip.str.match(CUSIP_RE).sum()), n, 0.99, 0.97)
        rep.expect_min_ratio("Fiyat sayısal ve > 0", int((df.price > 0).sum()), n, 0.97, 0.9)
        rep.add("Özet", Status.INFO, f"{df.cusip.nunique():,} CUSIP, {df.symbol.nunique():,} sembol, "
                                     f"{df.settle_date.nunique()} işlem günü")

    def check_dataset(self, client: HttpClient, manifest: dict, rep: SourceReport) -> dict[str, pd.DataFrame]:
        from radar.backfill.storage import read_partition
        ok = sorted(p for p, e in manifest["partitions"].items() if e["status"] != "fail")
        rep.add("Yüklenen yıl", Status.OK if ok else Status.FAIL, f"{len(ok)} yıl: {ok[:1]} … {ok[-1:]}")
        if not ok:
            return {}
        df = pd.concat([read_partition(self.name, p) for p in ok], ignore_index=True)

        # 1) Fiyat doğruluğu: AAPL'in FTD fiyatı, Yahoo kapanışıyla (aynı gün ve önceki gün) karşılaştırılır.
        series, _ = prices.parse_yahoo(client.get(prices.YAHOO.format(sym="AAPL", range="5y")).json())
        days = sorted(series)
        aapl = df[(df.symbol == "AAPL") & (df.settle_date >= pd.Timestamp(days[0]) + pd.Timedelta(days=5))]
        same, prev = [], []
        for r in aapl.itertuples():
            d = r.settle_date.date()
            before = [x for x in days if x < d]
            if d in series:
                same.append(prices.pct_diff(r.price, series[d]["close"]))
            if before:
                prev.append(prices.pct_diff(r.price, series[before[-1]]["close"]))
        if prev:
            within = sum(1 for x in prev if x < 0.5)
            check = rep.expect_min_ratio("Fiyat doğruluğu: AAPL FTD fiyatı ↔ Yahoo önceki gün kapanışı (%0,5)",
                                         within, len(prev), 0.95, 0.85)
            check.detail += f"; aynı gün eşleşmesi: %{100 * sum(1 for x in same if x < 0.5) / max(len(same), 1):.0f}"

        # 2) Borsadan çıkmış hisselerin kapsamı: çıkıştan önceki 12 ayda kaç gün fiyat var?
        notes = []
        for sym, month in DELISTED_PROBES.items():
            end = pd.Timestamp(month) + pd.offsets.MonthEnd(0)
            rows = df[(df.symbol == sym) & (df.settle_date > end - pd.DateOffset(years=1)) & (df.settle_date <= end)]
            notes.append(f"{sym}: {rows.settle_date.nunique()} gün (son {rows.settle_date.max().date() if len(rows) else '-'})")
        rep.add("Borsadan çıkmış hisseler: çıkıştan önceki 12 ayda fiyatlı gün (~250 işlem günü)", Status.INFO, "; ".join(notes))

        # 3) CUSIP → sembol eşleştirmesi (türetilmiş tablo).
        cmap = (df.groupby(["cusip", "symbol"]).agg(first_seen=("settle_date", "min"), last_seen=("settle_date", "max"),
                                                    description=("description", "last"), days=("settle_date", "nunique"))
                .reset_index())
        multi = cmap.groupby("cusip").symbol.nunique()
        rep.add("CUSIP → sembol eşleştirmesi", Status.INFO,
                f"{cmap.cusip.nunique():,} CUSIP; birden çok sembole bağlanan (sembol değişikliği): {int((multi > 1).sum()):,}")
        return {"cusip_map": cmap}


class TiingoListing(Dataset):
    name = "listings"
    title = "Tiingo hisse listesi (borsadan çıkmışlar dahil)"
    max_parallel = 1

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"tiingo-{today:%Y%m%d}"]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        df = read_zip_member(client.get(TIINGO_LIST, timeout=300).content, ".csv", sep=",")
        df.columns = [c.lower() for c in df.columns]
        out = pd.DataFrame({
            "ticker": df["ticker"].str.upper(), "exchange": df["exchange"], "asset_type": df["assettype"],
            "currency": df["pricecurrency"], "start_date": to_date(df["startdate"], "%Y-%m-%d"),
            "end_date": to_date(df["enddate"], "%Y-%m-%d"),
        })
        from radar.backfill.market import current_symbols
        return Loaded(out, [TIINGO_LIST], {"universe": current_symbols(client)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        rep.expect_range("Satır sayısı", len(df), 20_000, 300_000)
        nasdaq = df[(df.exchange.str.upper() == "NASDAQ") & (df.asset_type.str.lower() == "stock")]
        recent = nasdaq.end_date >= pd.Timestamp.today() - pd.Timedelta(days=7)
        ours = set(loaded.notes.get("universe", []))
        if ours:
            rep.expect_min_ratio("Evrenimizdeki hisseler listede aktif", len(ours & set(nasdaq.ticker[recent])), len(ours), 0.95, 0.85)
        gone = nasdaq[~recent & (nasdaq.end_date >= "2015-01-01")]
        rep.add("2015'ten bu yana Nasdaq'tan çıkan hisse", Status.INFO, f"{len(gone):,}")
        reused = df.ticker.value_counts()
        rep.add("Birden çok kaydı olan sembol (yeniden kullanım)", Status.INFO, f"{int((reused > 1).sum()):,}")
        found, good = [], 0
        for sym, month in DELISTED_PROBES.items():
            rows = df[df.ticker == sym]
            ends = [str(e.date()) for e in rows.end_date.dropna()]
            ok_months = {month, str(pd.Period(month) + 1), str(pd.Period(month) - 1)}
            good += any(e[:7] in ok_months for e in ends)
            found.append(f"{sym}: {ends or 'yok'}")
        rep.expect_min_ratio("Bilinen çıkışlar doğru tarihle listede", good, len(found), 1.0, 0.6).detail += f"; {found}"

"""Geçmiş veri yükleyicilerinin uçtan uca testleri (kaynak biçimlerini taklit eden sahte dosyalarla)."""

import io
import zipfile

import pandas as pd
import pytest

from radar.backfill import base, delisted, financials, insider, runner, storage
from radar.quality import SourceReport, Status


class FakeClient:
    def __init__(self, responses: dict[str, bytes]):
        self.responses = responses
        self.request_count = 0

    def get(self, url, **kwargs):
        self.request_count += 1
        for key, body in self.responses.items():
            if key in url:
                return type("R", (), {"content": body, "text": body.decode("utf-8", "replace")})()
        raise AssertionError(f"beklenmeyen istek: {url}")


def make_zip(files: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return buf.getvalue()


def tsv(rows: list[list[str]]) -> str:
    return "\n".join("\t".join(r) for r in rows) + "\n"


def test_links_and_quarters():
    html = b'<a href="/files/structureddata/data/insider-transactions-data-sets/2024q1_form345.zip">x</a>' \
           b'<a href="/files/x/2014q4_form345.zip">y</a>'
    got = base.links(FakeClient({"page": html}), "https://sec/page", r"(\d{4}q[1-4])_form345\.zip")
    assert got["2024q1"] == "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/2024q1_form345.zip"
    assert base.quarter_bounds("2024q2") == (pd.Timestamp("2024-04-01"), pd.Timestamp("2024-06-30"))


INSIDER_ZIP = make_zip({
    "SUBMISSION.tsv": tsv([["ACCESSION_NUMBER", "FILING_DATE", "PERIOD_OF_REPORT", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERNAME", "ISSUERTRADINGSYMBOL"],
                           ["0001-24-1", "05-FEB-2024", "01-FEB-2024", "4", "1045810", "NVIDIA CORP", "nvda"],
                           ["0001-24-2", "06-FEB-2024", "05-FEB-2024", "4", "320193", "Apple Inc.", "AAPL"]]),
    "REPORTINGOWNER.tsv": tsv([["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP", "RPTOWNER_TITLE"],
                               ["0001-24-1", "11", "DOE JANE", "Director", ""],
                               ["0001-24-1", "12", "DOE FUND", "TenPercentOwner", ""],
                               ["0001-24-2", "13", "COOK TIM", "Officer", "CEO"]]),
    "NONDERIV_TRANS.tsv": tsv([["ACCESSION_NUMBER", "SECURITY_TITLE", "TRANS_DATE", "TRANS_CODE", "TRANS_SHARES",
                                "TRANS_PRICEPERSHARE", "TRANS_ACQUIRED_DISP_CD", "SHRS_OWND_FOLWNG_TRANS", "DIRECT_INDIRECT_OWNERSHIP"],
                               ["0001-24-1", "Common", "01-FEB-2024", "P", "1000", "600.5", "A", "5000", "D"],
                               ["0001-24-2", "Common", "05-FEB-2024", "S", "200", "190", "D", "3000000", "D"]]),
})


def test_insider_load_and_checks():
    ds = insider.InsiderTransactions()
    client = FakeClient({"2024q1_form345.zip": INSIDER_ZIP,
                         "data-research": b'<a href="/files/d/2024q1_form345.zip">'})
    loaded = ds.load(client, "2024q1")
    df = loaded.df
    assert list(df.ticker) == ["NVDA", "AAPL"]
    nvda = df.iloc[0]
    assert nvda.relationship == "Director,TenPercentOwner" and nvda.n_owners == 2
    assert nvda.filing_date == pd.Timestamp("2024-02-05") and nvda.available_date == pd.Timestamp("2024-02-06")
    assert (nvda.code, nvda.shares, nvda.price) == ("P", 1000, 600.5)
    rep = SourceReport("k", "t", 1, [])
    ds.check_partition(loaded, "2024q1", rep)
    by = {c.name: c.status for c in rep.checks}
    assert by["Kod/yön tutarlılığı (P→A, S→D)"] == Status.OK
    assert by["İşlem sayısı"] == Status.FAIL  # 2 satır, gerçek çeyrek on binlerce


def test_financials_load_and_golden():
    sub = tsv([["adsh", "cik", "name", "sic", "countryba", "form", "period", "fy", "fp", "filed", "accepted"],
               ["A1", "320193", "APPLE INC", "3571", "US", "10-K", "20230930", "2023", "FY", "20231103", "2023-11-02 18:04:00.0"],
               ["A2", "1", "X", "1", "US", "8-K", "20230930", "2023", "FY", "20231103", "2023-11-02 18:04:00.0"]])
    num = tsv([["adsh", "tag", "version", "coreg", "ddate", "qtrs", "uom", "segments", "value", "footnote"],
               ["A1", "RevenueFromContractWithCustomerExcludingAssessedTax", "us-gaap/2023", "", "20230930", "4", "USD", "", "383285000000", ""],
               ["A1", "RevenueFromContractWithCustomerExcludingAssessedTax", "us-gaap/2023", "", "20230930", "4", "USD", "ProductOrService=iPhone;", "200", ""],
               ["A1", "SomethingElse", "us-gaap/2023", "", "20230930", "4", "USD", "", "1", ""],
               ["A2", "Revenues", "us-gaap/2023", "", "20230930", "4", "USD", "", "5", ""]])
    blob = make_zip({"sub.txt": sub, "num.txt": num, "tag.txt": "", "pre.txt": ""})
    ds = financials.FinancialStatements()
    loaded = ds.load(FakeClient({"2023q4.zip": blob, "data-research": b'<a href="/files/dera/2023q4.zip">'}), "2023q4")
    df = loaded.df
    assert len(df) == 1  # segmentli, listede olmayan etiket ve 8-K elendi
    assert df.iloc[0].accepted == pd.Timestamp("2023-11-02 18:04:00")
    rep = SourceReport("k", "t", 1, [])
    ds.check_partition(loaded, "2023q4", rep)
    golden = [c for c in rep.checks if c.name.startswith("Doğrulanmış")]
    assert golden and golden[0].status == Status.OK


FTD_TXT = ("SETTLEMENT DATE|CUSIP|SYMBOL|QUANTITY (FAILS)|DESCRIPTION|PRICE\n"
           "20230301|78486Q101|SIVB|1200|SVB FINL GROUP COM|284.5\n"
           "20230302|037833100|AAPL|15000|APPLE INC COM|145.91\n"
           "Trailer record count 2\n")


def test_ftd_load():
    ds = delisted.FailsToDeliver()
    page = b'<a href="/files/data/fails-deliver-data/cnsfails202303a.zip">'
    loaded = ds.load(FakeClient({"cnsfails202303a.zip": make_zip({"cnsfails202303a": FTD_TXT}),
                                 "data-research": page}), "2023")
    df = loaded.df
    assert list(df.symbol) == ["SIVB", "AAPL"] and df.price.tolist() == [284.5, 145.91]
    assert df.cusip.str.match(delisted.CUSIP_RE).all()


def test_tiingo_listing():
    csv = ("ticker,exchange,assetType,priceCurrency,startDate,endDate\n"
           "SIVB,NASDAQ,Stock,USD,1987-01-01,2023-03-09\nAAPL,NASDAQ,Stock,USD,1980-12-12,2099-01-01\n")
    nasdaq = b"Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\nAAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N\n"
    loaded = delisted.TiingoListing().load(FakeClient({"supported_tickers": make_zip({"supported_tickers.csv": csv}), "nasdaqlisted": nasdaq}), "tiingo-x")
    assert loaded.notes["universe"] == ["AAPL"]
    assert loaded.df.set_index("ticker").end_date["SIVB"] == pd.Timestamp("2023-03-09")


def test_runner_run_and_finalize(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "BACKFILL_DIR", tmp_path / "backfill")
    monkeypatch.setattr(storage, "MANIFEST_DIR", tmp_path / "manifest")
    monkeypatch.setattr(runner, "PARTS_DIR", tmp_path / "manifest" / "parts")
    monkeypatch.setattr(runner, "REPORT_DIR", tmp_path / "reports")
    client = FakeClient({"2024q1_form345.zip": INSIDER_ZIP, "data-research": b'<a href="/f/2024q1_form345.zip">'})
    monkeypatch.setattr(runner, "HttpClient", lambda: client)
    monkeypatch.setattr(insider.InsiderTransactions, "check_dataset", lambda self, c, m, rep: rep.add("x", Status.OK, "") and {})
    runner.main(["run", "--dataset", "insider", "--partition", "2024q1"])
    runner.main(["finalize", "--dataset", "insider"])
    manifest = storage.load_manifest("insider")
    entry = manifest["partitions"]["2024q1"]
    # İşlem sayısı kontrolü kırmızı olduğu için bölüm arşive alınmaz, ama manifestte nedeniyle kayıtlıdır.
    assert entry["status"] == "fail" and entry["rows"] == 2
    assert not storage.partition_path("insider", "2024q1").exists()
    assert (tmp_path / "reports" / "insider.md").exists()


def test_market_groups_and_events():
    from radar.backfill import market
    assert market.in_group("AAPL", "A") and market.in_group("KLAC", "J-K") and not market.in_group("LULU", "J-K")
    assert all(any(market.in_group(c + "X", g) for g in market.GROUPS) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    data = {"chart": {"result": [{"events": {"splits": {"1": {"date": 1718026200, "numerator": 10, "denominator": 1}},
                                             "dividends": {"2": {"date": 1717767000, "amount": 0.01}}}}]}}
    splits, divs = market.parse_yahoo_events(data)
    assert splits[0]["ratio"] == 10 and divs[0]["amount"] == 0.01


def test_holdings_load_units():
    from radar.backfill import holdings
    z = make_zip({
        "SUBMISSION.tsv": tsv([["ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT"],
                               ["A1", "14-NOV-2022", "13F-HR", "102909", "30-SEP-2022"],
                               ["A2", "14-FEB-2023", "13F-HR", "102909", "31-DEC-2022"]]),
        "COVERPAGE.tsv": tsv([["ACCESSION_NUMBER", "ISAMENDMENT", "FILINGMANAGER_NAME"], ["A1", "N", "VANGUARD"], ["A2", "N", "VANGUARD"]]),
        "INFOTABLE.tsv": tsv([["ACCESSION_NUMBER", "NAMEOFISSUER", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE", "PUTCALL"],
                              ["A1", "APPLE INC", "037833100", "138", "1000", "SH", ""],
                              ["A2", "APPLE INC", "037833100", "130000", "1000", "SH", ""]]),
    })
    ds = holdings.InstitutionalHoldings()
    loaded = ds.load(FakeClient({"2022q4_form13f.zip": z, "data-research": b'<a href="/f/2022q4_form13f.zip">'}), "2022q4")
    assert loaded.df.value.tolist() == [138_000, 130_000]  # 2023 öncesi bin $ → $
    assert holdings.partition_start("01jun2024-31aug2024") == pd.Timestamp("2024-06-01")
    assert holdings.partition_start("2023q3") == pd.Timestamp("2023-07-01")


def test_runner_plan_from_request_file(tmp_path, monkeypatch, capsys):
    import json
    monkeypatch.setattr(storage, "MANIFEST_DIR", tmp_path / "manifest")
    req = tmp_path / "req.json"
    req.write_text(json.dumps({"requests": [{"dataset": "insider", "only": "2024q1"}, {"dataset": "fred"}]}))
    monkeypatch.setattr(runner, "REQUEST_FILE", req)
    client = FakeClient({"data-research": b'<a href="/f/2024q1_form345.zip"><a href="/f/2024q2_form345.zip">'})
    monkeypatch.setattr(runner, "HttpClient", lambda: client)
    runner.main(["plan"])
    out = json.loads(capsys.readouterr().out)
    parts = [(m["dataset"], m["partition"][:3]) for m in out["matrix"]["include"]]
    assert parts == [("insider", "202"), ("fred", "all")]
    assert out["datasets"] == "insider fred" and 1 <= out["max_parallel"] <= 6

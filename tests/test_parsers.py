"""Ayrıştırıcı testleri. Girdiler, kaynakların belgelenmiş biçimlerini taklit eder;
gerçek veriyle doğrulama `python -m radar.health` (GitHub Actions) ile yapılır."""

from datetime import date, datetime

from radar.quality import SourceReport, Status
from radar.sources import fred, finra, gdelt, prices, sec_13f, sec_form4, sec_index, sec_submissions, sec_xbrl, universe, wikipedia
from radar.sources.social import parse_rss

NASDAQ = """Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
AAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N
QQQ|Invesco QQQ Trust, Series 1|G|N|N|100|Y|N
ABCDW|ABCD Corp. - Warrant|S|N|N|100|N|N
ZXZZT|NASDAQ TEST STOCK|G|Y|N|100|N|N
UAL|United Airlines Holdings, Inc. - Common Stock|Q|N|D|100|N|N
BABA|Foo Ltd - American Depositary Shares|Q|N|N|100|N|N
File Creation Time: 1009202618:02|||||||"""


def test_parse_nasdaq_listed():
    secs, created = universe.parse_nasdaq_listed(NASDAQ)
    by = {s.symbol: s for s in secs}
    assert created == datetime(2026, 10, 9, 18, 2)
    assert "ZXZZT" not in by  # test hissesi
    assert by["AAPL"].is_common and by["UAL"].is_common and by["BABA"].is_common
    assert not by["QQQ"].is_common and not by["ABCDW"].is_common
    assert by["UAL"].financial_status == "D"


def test_parse_sec_tickers_and_normalize():
    data = {"fields": ["cik", "name", "ticker", "exchange"], "data": [[320193, "Apple Inc.", "AAPL", "Nasdaq"], [1, "X", "BRK-B", "NYSE"]]}
    m = universe.parse_sec_tickers(data)
    assert m["AAPL"] == (320193, "Nasdaq")
    assert universe.normalize_symbol("BRK.B") == "BRK-B"


FORM_IDX = """Description:           Daily Index of EDGAR Dissemination Feed by Form Type
Last Data Received:    October 8, 2026

Form Type   Company Name                                                  CIK         Date Filed  File Name
---------------------------------------------------------------------------------------------------------------------------------------------
10-K        ACME CORP                                                     1234567     20261008    edgar/data/1234567/0001234567-26-000010.txt
4           DOE JOHN                                                      7654321     20261008    edgar/data/7654321/0000950170-26-001234.txt
SC 13G/A    BIG  FUND  LP                                                 1111        20261008    edgar/data/1111/0001111-26-000001.txt
"""


def test_parse_form_index():
    rows = sec_index.parse_form_index(FORM_IDX)
    assert [r.form for r in rows] == ["10-K", "4", "SC 13G/A"]
    assert rows[1].cik == 7654321 and rows[1].filed == date(2026, 10, 8)
    assert rows[2].company == "BIG  FUND  LP"
    assert rows[0].path.endswith("0001234567-26-000010.txt")


def test_business_days_back_skips_weekend():
    days = sec_index.business_days_back(date(2026, 10, 12), 3)  # Pazartesi
    assert days == [date(2026, 10, 9), date(2026, 10, 8), date(2026, 10, 7)]


def test_parse_recent_submissions():
    data = {"filings": {"recent": {"form": ["8-K", "10-K"], "filingDate": ["2026-10-01", "2025-11-01"],
                                   "acceptanceDateTime": ["2026-10-01T16:05:00.000Z", "2025-10-31T18:00:00.000Z"],
                                   "accessionNumber": ["a", "b"], "primaryDocument": ["x.htm", "y.htm"],
                                   "items": ["2.02,9.01", ""], "reportDate": ["", "2025-09-30"]}}}
    rows = sec_submissions.parse_recent(data)
    assert rows[0]["items"] == "2.02,9.01" and rows[1]["form"] == "10-K"


def test_annual_value_picks_full_year_10k():
    facts = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"start": "2023-07-01", "end": "2023-09-30", "val": 1, "form": "10-K", "filed": "2023-11-03"},  # çeyrek
        {"start": "2022-10-01", "end": "2023-09-30", "val": 5, "form": "10-Q", "filed": "2023-11-03"},
        {"start": "2022-10-02", "end": "2023-09-30", "val": 383, "form": "10-K", "filed": "2023-11-03"},
    ]}}}}}
    assert sec_xbrl.annual_value(facts, ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"], "2023-09-30") == 383


FORM4_TXT = """<SEC-DOCUMENT>
<XML>
<?xml version="1.0"?>
<ownershipDocument>
  <issuer><issuerCik>0001045810</issuerCik><issuerName>NVIDIA CORP</issuerName><issuerTradingSymbol>nvda</issuerTradingSymbol></issuer>
  <reportingOwner>
    <reportingOwnerId><rptOwnerCik>1</rptOwnerCik><rptOwnerName>DOE JANE</rptOwnerName></reportingOwnerId>
    <reportingOwnerRelationship><isDirector>1</isDirector><isOfficer>0</isOfficer><officerTitle></officerTitle></reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>2026-10-06</value></transactionDate>
      <transactionCoding><transactionFormType>4</transactionFormType><transactionCode>P</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>1,000</value></transactionShares>
        <transactionPricePerShare><value>120.5</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
      <postTransactionAmounts><sharesOwnedFollowingTransaction><value>5000</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>
</XML>
</SEC-DOCUMENT>"""


def test_parse_form4():
    xml = sec_form4.extract_xml(FORM4_TXT, "ownershipDocument")
    [tx] = sec_form4.parse_form4(xml)
    assert (tx.ticker, tx.code, tx.shares, tx.price, tx.acquired) == ("NVDA", "P", 1000.0, 120.5, "A")
    assert tx.is_director and not tx.is_officer and tx.date == date(2026, 10, 6) and tx.issuer_cik == 1045810


INFO_TABLE = """<ns1:informationTable xmlns:ns1="http://www.sec.gov/edgar/document/thirteenf/informationtable">
<ns1:infoTable><ns1:nameOfIssuer>APPLE INC</ns1:nameOfIssuer><ns1:titleOfClass>COM</ns1:titleOfClass>
<ns1:cusip>037833100</ns1:cusip><ns1:value>1500000</ns1:value>
<ns1:shrsOrPrnAmt><ns1:sshPrnamt>7000</ns1:sshPrnamt><ns1:sshPrnamtType>SH</ns1:sshPrnamtType></ns1:shrsOrPrnAmt>
</ns1:infoTable></ns1:informationTable>"""


def test_parse_13f_info_table():
    [row] = sec_13f.parse_info_table(INFO_TABLE)
    assert row["cusip"] == "037833100" and row["shares"] == 7000 and sec_13f.CUSIP.match(row["cusip"])


def test_parse_yahoo():
    data = {"chart": {"result": [{"timestamp": [1717767000, 1718026200],
                                  "events": {"splits": {"1718026200": {"date": 1718026200, "numerator": 10, "denominator": 1}}},
                                  "indicators": {"quote": [{"close": [120.88, None], "volume": [1, 2]}],
                                                 "adjclose": [{"adjclose": [120.8, None]}]}}]}}
    y, splits = prices.parse_yahoo(data)
    assert y == {date(2024, 6, 7): {"close": 120.88, "adjclose": 120.8, "volume": 1.0}}
    assert splits == [date(2024, 6, 10)]


def test_big_jumps():
    s = {date(2024, 1, 1): {"close": 100}, date(2024, 1, 2): {"close": 10}, date(2024, 1, 3): {"close": 11}}
    assert prices.big_jumps(s) == [date(2024, 1, 2)]


def test_parse_fred_csv_handles_missing():
    s = fred.parse_fred_csv("observation_date,DCOILWTICO\n2024-01-01,.\n2024-01-02,70.38\n")
    assert s == {date(2024, 1, 1): None, date(2024, 1, 2): 70.38}


def test_parse_finra():
    rows = finra.parse_short_volume("Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market\n20261008|AAPL|100|0|300|B,Q,N\n")
    assert rows == [{"date": "20261008", "symbol": "AAPL", "short": 100.0, "exempt": 0.0, "total": 300.0}]


def test_parse_gdelt_and_wiki():
    pts = gdelt.parse_timeline({"timeline": [{"series": "Article Count", "data": [{"date": "20261008T000000Z", "value": 42}]}]})
    assert pts[0][1] == 42.0
    views = wikipedia.parse_pageviews({"items": [{"timestamp": "2026100800", "views": 1234}]})
    assert views == {date(2026, 10, 8): 1234}
    assert wikipedia.parse_sparql({"results": {"bindings": [{"cik": {"value": "0001045810"}, "article": {"value": "https://en.wikipedia.org/wiki/Nvidia"}}]}}, key="cik") == {"1045810": "Nvidia"}
    m = wikipedia.parse_sparql({"results": {"bindings": [{"ticker": {"value": "nvda"}, "article": {"value": "https://en.wikipedia.org/wiki/Nvidia"}}]}})
    assert m == {"NVDA": "Nvidia"}


def test_parse_rss():
    rss = """<rss><channel><item><title>Nvidia rises</title><pubDate>Thu, 08 Oct 2026 14:00:00 GMT</pubDate>
    <source url="x">Reuters</source><link>http://a</link></item></channel></rss>"""
    [item] = parse_rss(rss)
    assert item["title"] == "Nvidia rises" and item["source"] == "Reuters" and item["published"].year == 2026


def test_source_status_is_worst_check():
    rep = SourceReport("k", "t", 1, [1])
    rep.add("a", Status.OK, "")
    rep.add("b", Status.INFO, "")
    assert rep.status == Status.OK
    rep.expect_range("c", 5, 10, 20, warn_only=True)
    assert rep.status == Status.WARN
    rep.expect_min_ratio("d", 1, 10, 0.9, 0.5)
    assert rep.status == Status.FAIL
    assert rep.expect_equal("e", 383_285_000_000.0, 383_285_000_000).status == Status.OK


def test_parse_nasdaq_prices():
    data = {"data": {"tradesTable": {"rows": [{"date": "10/09/2026", "close": "$1,254.04", "volume": "40,123,456"},
                                              {"date": "bad", "close": "$1"}]}}}
    assert prices.parse_nasdaq(data) == {date(2026, 10, 9): {"close": 1254.04, "volume": 40123456.0}}
    assert prices.parse_nasdaq({"data": None}) == {}


def test_price_agreement():
    a = {date(2024, 1, d): {"close": 100.0} for d in range(1, 31)}
    b = {d: {"close": 100.2} for d in a}
    assert round(prices.agreement(a, b), 3) == 0.2
    assert prices.agreement(a, {}) is None


def test_gdelt_last_update_and_gkg():
    import io, zipfile
    text = ("100 aaa http://data.gdeltproject.org/gdeltv2/20261009220000.export.CSV.zip\n"
            "200 bbb http://data.gdeltproject.org/gdeltv2/20261009220000.mentions.CSV.zip\n"
            "300 ccc http://data.gdeltproject.org/gdeltv2/20261009220000.gkg.csv.zip\n")
    files = gdelt.parse_last_update(text)
    assert files["gkg"] == (300, "ccc", "http://data.gdeltproject.org/gdeltv2/20261009220000.gkg.csv.zip")
    row = ["x"] * gdelt.GKG_COLUMNS
    row[gdelt.COL_ORGS] = "nvidia;apple"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.gkg.csv", "\t".join(row) + "\n")
    rows = gdelt.read_gkg(buf.getvalue())
    assert len(rows) == 1 and rows[0][gdelt.COL_ORGS] == "nvidia;apple"


def test_parse_13f_unbound_prefix():
    xml = ('<informationTable xsi:schemaLocation="a b"><n1:infoTable><n1:nameOfIssuer>X</n1:nameOfIssuer>'
           '<n1:cusip>037833100</n1:cusip><n1:value>5</n1:value><n1:shrsOrPrnAmt><n1:sshPrnamt>2</n1:sshPrnamt>'
           '</n1:shrsOrPrnAmt></n1:infoTable></informationTable>')
    assert sec_13f.parse_info_table(xml)[0]["shares"] == 2


def test_latest_shares_filed_falls_back_to_balance_sheet():
    facts = {"facts": {"us-gaap": {"CommonStockSharesOutstanding": {"units": {"shares": [{"filed": "2026-08-01"}]}}}}}
    assert sec_xbrl.latest_shares_filed(facts) == "2026-08-01"
    assert sec_xbrl.latest_shares_filed({}) is None


def test_acceptance_time_converted_to_new_york():
    from radar.sources.sec_submissions import NEW_YORK
    accepted = datetime.fromisoformat("2026-10-09T02:30:32+00:00").astimezone(NEW_YORK).date()
    assert accepted == date(2026, 10, 8)


def test_gdelt_previous_slot_and_zip_check():
    url = "http://data.gdeltproject.org/gdeltv2/20261009230000.gkg.csv.zip"
    assert gdelt.previous_slot(url) == "http://data.gdeltproject.org/gdeltv2/20261009224500.gkg.csv.zip"
    assert not gdelt.zip_intact(b"not a zip")


def test_parse_other_listed_keeps_nyse_common_only():
    from radar.sources import universe
    text = "\n".join([
        "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
        "JPM|JPMorgan Chase & Co. Common Stock|N|JPM|N|100|N|JPM",
        "BAC$K|Bank of America Corporation Depositary Shares|N|BACpK|N|100|N|BAC-K",
        "SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY",
        "XYZ.WS|XYZ Corp Warrants|N|XYZ.WS|N|100|N|XYZ+",
        "UEC|Uranium Energy Corp. Common Stock|A|UEC|N|100|N|UEC",
        "BRK.B|Berkshire Hathaway Inc. Class B|N|BRK.B|N|100|N|BRK.B",
        "File Creation Time: 1010202612:00|||||||",
    ])
    secs = universe.parse_other_listed(text)
    common = {s.symbol: s.exchange for s in secs if s.is_common}
    assert common == {"JPM": "N", "UEC": "A", "BRK.B": "N"}

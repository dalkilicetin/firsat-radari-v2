"""SEC XBRL finansal verileri (companyfacts API).

Her değer, ait olduğu dönem (start/end) ve SEC'e dosyalandığı tarih (filed) ile gelir.
Geriye dönük testte bir değeri yalnızca `filed` tarihinden sonra kullanabiliriz.
"""

from __future__ import annotations

from datetime import date

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "sec_xbrl", "SEC XBRL finansal verileri", 1, [1]

URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
]

# Yıllık raporlardan doğrulanmış gelirler (dolar): (ticker, mali yıl sonu, değer)
GOLDEN_REVENUE = [
    ("AAPL", "2023-09-30", 383_285_000_000),
    ("MSFT", "2023-06-30", 211_915_000_000),
    ("NVDA", "2024-01-28", 60_922_000_000),
]


def annual_value(facts: dict, tags: list[str], end: str, taxonomy: str = "us-gaap") -> float | None:
    """Verilen dönem sonuna ait, ~1 yıllık süreli, 10-K'da raporlanmış ilk değer."""
    gaap = facts.get("facts", {}).get(taxonomy, {})
    for tag in tags:
        for unit_values in gaap.get(tag, {}).get("units", {}).values():
            for v in unit_values:
                if v.get("end") != end or not v.get("start") or not v.get("form", "").startswith("10-K"):
                    continue
                days = (date.fromisoformat(v["end"]) - date.fromisoformat(v["start"])).days
                if 350 <= days <= 380:
                    return float(v["val"])
    return None


# Sınıf bazında (A/B hisse) raporlanan değerler companyfacts'te yer almaz; bu yüzden sırayla yedeklere bakılır.
SHARES_TAGS = [("dei", "EntityCommonStockSharesOutstanding"), ("us-gaap", "CommonStockSharesOutstanding"),
               ("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic"),
               ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding")]


def latest_shares_filed(facts: dict) -> str | None:
    """Hisse sayısının en son dosyalandığı tarih. Kapak sayfası (dei) yoksa bilanço kalemine bakılır."""
    dates = [v["filed"] for tx, tag in SHARES_TAGS
             for v in facts.get("facts", {}).get(tx, {}).get(tag, {}).get("units", {}).get("shares", [])]
    return max(dates, default=None)


def iter_values(facts: dict):
    for taxonomy, tags in facts.get("facts", {}).items():
        for tag, body in tags.items():
            for unit, values in body.get("units", {}).items():
                for v in values:
                    yield taxonomy, tag, unit, v


def run(ctx: Context, rep: SourceReport) -> None:
    golden_tickers = [g[0] for g in GOLDEN_REVENUE]
    facts_by_ticker = {}
    for t in golden_tickers + ctx.sample_symbols(20, with_cik=True):
        cik = ctx.cik_by_ticker.get(t.replace(".", "-"))
        if not cik or t in facts_by_ticker:
            continue
        try:
            facts_by_ticker[t] = ctx.client.get(URL.format(cik=cik)).json()
        except Exception as exc:  # şirketin XBRL'i hiç olmayabilir (404)
            facts_by_ticker[t] = {"_error": str(exc)[:120]}

    for t, end, expected in GOLDEN_REVENUE:
        got = annual_value(facts_by_ticker.get(t, {}), REVENUE_TAGS, end)
        rep.expect_equal(f"Doğrulanmış gerçek: {t} geliri ({end})", got, expected)

    sampled = [t for t in facts_by_ticker if t not in golden_tickers]
    has_core = 0
    for t in sampled:
        facts = facts_by_ticker[t].get("facts", {})
        if any(tag in facts.get(tx, {}) for tx in ("us-gaap", "ifrs-full") for tag in ("Assets", "Revenues", "NetIncomeLoss", "ProfitLoss")):
            has_core += 1
    rep.expect_min_ratio("Rastgele şirketlerde temel kalem (varlık/gelir/kâr) bulunan", has_core, len(sampled), 0.85, 0.7)

    total = bad_time = 0
    for t, facts in facts_by_ticker.items():
        for _, _, _, v in iter_values(facts):
            if "filed" in v and "end" in v:
                total += 1
                if v["filed"] < v["end"]:
                    bad_time += 1
    rep.expect_min_ratio("Zaman tutarlılığı: dosyalama tarihi ≥ dönem sonu", total - bad_time, total, 0.999, 0.99)

    fresh, missing = 0, []
    for t in sampled:
        last = latest_shares_filed(facts_by_ticker[t])
        if last and (ctx.today - date.fromisoformat(last)).days <= 200:
            fresh += 1
        else:
            missing.append(f"{t}:{last or 'yok'}")
    check = rep.expect_min_ratio("Güncel hisse sayısı (son 200 gün) bulunan", fresh, len(sampled), 0.85, 0.7)
    if missing:
        check.detail += f"; eksik/eski: {missing}"

    ifrs = sum(1 for t in sampled if "ifrs-full" in facts_by_ticker[t].get("facts", {}))
    errors = [t for t in sampled if "_error" in facts_by_ticker[t]]
    rep.add("Kapsam notu", Status.INFO, f"{ifrs} şirket IFRS raporluyor (yabancı), {len(errors)} şirkette XBRL yok: {errors}")

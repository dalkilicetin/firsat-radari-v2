"""Wikipedia sayfa görüntülenmeleri + Wikidata ile şirket ↔ makale eşleştirmesi.

Görüntülenme verisi Temmuz 2015'ten beri günlük olarak resmî API'den gelir.
Hangi şirketin hangi makaleye karşılık geldiğini Wikidata'daki borsa kodu (P249) söyler.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from urllib.parse import quote

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "wikipedia", "Wikipedia ilgisi + Wikidata eşleştirmesi", 2, [2, 4]

PAGEVIEWS = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
             "{article}/daily/{start:%Y%m%d}/{end:%Y%m%d}")
SPARQL = "https://query.wikidata.org/sparql"
# Nasdaq (Q82059) üzerinde borsa kodu olan şirketler ve İngilizce Wikipedia makaleleri.
QUERY = """
SELECT ?ticker ?article WHERE {
  ?item p:P414 ?listing . ?listing ps:P414 wd:Q82059 ; pq:P249 ?ticker .
  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
}"""

ARTICLES = ["Nvidia", "Apple_Inc.", "Microsoft"]


def parse_pageviews(data: dict) -> dict[date, int]:
    return {datetime.strptime(i["timestamp"][:8], "%Y%m%d").date(): int(i["views"]) for i in data.get("items", [])}


def parse_sparql(data: dict) -> dict[str, str]:
    out = {}
    for b in data["results"]["bindings"]:
        out.setdefault(b["ticker"]["value"].upper(), b["article"]["value"].rsplit("/", 1)[-1])
    return out


def run(ctx: Context, rep: SourceReport) -> None:
    end, start = ctx.today - timedelta(days=1), ctx.today - timedelta(days=60)
    sample = {}
    for art in ARTICLES:
        views = parse_pageviews(ctx.client.get(PAGEVIEWS.format(article=art, start=start, end=end)).json())
        rep.expect_range(f"{art}: gün sayısı (60 gün)", len(views), 55, 61)
        rep.expect_fresh(f"{art}: güncellik", max(views) if views else None, 3, ctx.today)
        sample[art] = sorted(views.items())[-3:]

    hist = parse_pageviews(ctx.client.get(PAGEVIEWS.format(article="Nvidia", start=date(2015, 7, 1), end=date(2015, 7, 31))).json())
    rep.expect_range("Geçmiş veri: Temmuz 2015 gün sayısı", len(hist), 30, 31)

    mapping = parse_sparql(ctx.client.get(SPARQL, params={"query": QUERY, "format": "json"},
                                          headers={"Accept": "application/sparql-results+json"}).json())
    common = [s.symbol for s in ctx.common_stocks()]
    covered = [s for s in common if s in mapping]
    rep.expect_min_ratio("Wikidata ile makalesi bulunan Nasdaq hissesi", len(covered), len(common), 0.5, 0.3)
    rep.add("Eşleştirme kontrolü", Status.OK if mapping.get("NVDA") == "Nvidia" else Status.WARN,
            f"NVDA → {mapping.get('NVDA')}, AAPL → {mapping.get('AAPL')}")
    rep.sample = {"pageviews": sample, "mapping_count": len(mapping)}

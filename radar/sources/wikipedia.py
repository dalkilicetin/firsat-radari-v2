"""Wikipedia sayfa görüntülenmeleri + Wikidata ile şirket ↔ makale eşleştirmesi.

Görüntülenme verisi Temmuz 2015'ten beri günlük olarak resmî API'den gelir.
Hangi şirketin hangi makaleye karşılık geldiğini Wikidata söyler: Nasdaq borsa kodu (P249)
ya da SEC CIK numarası (P5531) üzerinden.
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

QUERY_CIK = """
SELECT ?cik ?article WHERE {
  ?item wdt:P5531 ?cik .
  ?article schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> .
}"""

ARTICLES = ["Nvidia", "Apple_Inc.", "Microsoft"]


def parse_pageviews(data: dict) -> dict[date, int]:
    return {datetime.strptime(i["timestamp"][:8], "%Y%m%d").date(): int(i["views"]) for i in data.get("items", [])}


def parse_sparql(data: dict, key: str = "ticker") -> dict[str, str]:
    out = {}
    for b in data["results"]["bindings"]:
        k = b[key]["value"].upper()
        if key == "cik":
            k = k.lstrip("0")
        out.setdefault(k, b["article"]["value"].rsplit("/", 1)[-1])
    return out


def sparql(ctx: Context, query: str) -> dict:
    return ctx.client.get(SPARQL, params={"query": query, "format": "json"},
                          headers={"Accept": "application/sparql-results+json"}).json()


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

    mapping = parse_sparql(sparql(ctx, QUERY))
    by_cik = parse_sparql(sparql(ctx, QUERY_CIK), key="cik")
    common = ctx.common_stocks()
    via_ticker = {s.symbol for s in common if s.symbol in mapping}
    via_cik = {s.symbol for s in common if s.cik and str(s.cik) in by_cik}
    rep.add("Eşleşme yolu: Nasdaq kodu / SEC CIK", Status.INFO,
            f"kod ile {len(via_ticker)}, CIK ile {len(via_cik)}"
            + ("" if any(s.cik for s in common) else " (CIK yok: SEC erişimi bekleniyor)"))
    # Küçük şirketlerin çoğunun Wikipedia makalesi yoktur; bu sinyal doğası gereği büyük/orta şirketleri kapsar.
    rep.expect_min_ratio("Wikipedia makalesi eşleşen Nasdaq hissesi", len(via_ticker | via_cik), len(common), 0.35, 0.2)
    rep.add("Eşleştirme kontrolü", Status.OK if mapping.get("NVDA") == "Nvidia" else Status.WARN,
            f"NVDA → {mapping.get('NVDA')}, AAPL → {mapping.get('AAPL')}")
    rep.sample = {"pageviews": sample, "mapping_count": len(mapping)}

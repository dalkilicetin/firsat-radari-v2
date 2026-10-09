"""USAspending.gov: ABD federal hükümet sözleşmeleri.

Küçük bir şirket için büyük bir devlet sözleşmesi oyun değiştirici olabilir.
Şirket ↔ yüklenici adı eşleştirmesi puanlama aşamasında yapılacak.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "usaspending", "USAspending devlet sözleşmeleri", 1, [3]

SEARCH = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
LAST_UPDATED = "https://api.usaspending.gov/api/v2/awards/last_updated/"

# Devletle çalıştığı bilinen Nasdaq şirketleri.
PROBES = ["Palantir", "Microsoft", "Amazon Web Services"]


def search_awards(ctx: Context, recipient: str, start: date, end: date) -> list[dict]:
    body = {
        "filters": {
            "recipient_search_text": [recipient],
            "award_type_codes": ["A", "B", "C", "D"],
            "time_period": [{"start_date": start.isoformat(), "end_date": end.isoformat()}],
        },
        "fields": ["Award ID", "Recipient Name", "Award Amount", "Start Date", "Awarding Agency"],
        "limit": 50, "page": 1, "sort": "Award Amount", "order": "desc",
    }
    return ctx.client.post(SEARCH, json=body).json().get("results", [])


def run(ctx: Context, rep: SourceReport) -> None:
    updated = ctx.client.get(LAST_UPDATED).json().get("last_updated", "")
    try:
        # API tarihi MM/DD/YYYY biçiminde döner.
        rep.expect_fresh("Veritabanı güncelliği", datetime.strptime(updated[:10], "%m/%d/%Y").date(), 10, ctx.today)
    except ValueError:
        rep.add("Veritabanı güncelliği", Status.WARN, f"tarih okunamadı: {updated!r}")

    sample = {}
    for name in PROBES:
        results = search_awards(ctx, name, ctx.today - timedelta(days=365), ctx.today)
        amounts = [r.get("Award Amount") for r in results]
        numeric = sum(1 for a in amounts if isinstance(a, (int, float)))
        rep.add(f"{name}: son 1 yıl sözleşme", Status.OK if results and numeric == len(amounts) else Status.FAIL,
                f"{len(results)} kayıt, tutarlar sayısal: {numeric}/{len(amounts)}")
        sample[name] = results[:2]
    rep.sample = sample

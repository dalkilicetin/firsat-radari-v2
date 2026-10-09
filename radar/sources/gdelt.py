"""GDELT: dünya çapında haber akışı.

DOC API son 3 ayı kapsar (haftalık çalışma için). 2015'e uzanan geçmiş, GDELT'in
15 dakikalık ham dosyalarından alınır; burada o dosyaların güncelliği de test edilir.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "gdelt", "GDELT haber akışı", 2, [2, 4]

DOC = "https://api.gdeltproject.org/api/v2/doc/doc?query={q}&mode=timelinevolraw&format=json&timespan=3months"
LAST_UPDATE = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
QUERIES = ['"Nvidia"', '"Apple Inc"', '"small modular reactor"']


def parse_timeline(data: dict) -> list[tuple[datetime, float]]:
    points = []
    for series in data.get("timeline", []):
        for p in series.get("data", []):
            try:
                points.append((datetime.strptime(p["date"], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc), float(p["value"])))
            except (KeyError, ValueError):
                continue
    return points


def run(ctx: Context, rep: SourceReport) -> None:
    sample = {}
    for q in QUERIES:
        points = parse_timeline(ctx.client.get(DOC.format(q=q)).json())
        if not points:
            rep.add(f"{q}: zaman serisi", Status.FAIL, "boş")
            continue
        nonzero = sum(1 for _, v in points if v > 0)
        rep.expect_min_ratio(f"{q}: haber olan gün", nonzero, len(points), 0.8, 0.5)
        rep.expect_fresh(f"{q}: güncellik", max(t for t, _ in points), 2)
        sample[q] = [(t.date().isoformat(), v) for t, v in points[-3:]]

    text = ctx.client.get(LAST_UPDATE).text
    m = re.search(r"/(\d{14})\.", text)
    stamp = datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc) if m else None
    rep.expect_fresh("Ham dosya akışı (geçmiş veri kaynağı)", stamp, 0.25)
    rep.sample = sample

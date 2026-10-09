"""FINRA günlük açığa satış hacmi (Reg SHO).

Toplam işlem hacminin ne kadarının açığa satış olduğunu gösterir; risk puanına girer.
"""

from __future__ import annotations

import csv
import io
from datetime import date

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context
from radar.sources.sec_index import business_days_back

KEY, TITLE, TIER, ROADS = "finra", "FINRA açığa satış hacmi", 1, [3]

URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{d:%Y%m%d}.txt"


def parse_short_volume(text: str) -> list[dict]:
    rows = []
    for r in csv.DictReader(io.StringIO(text), delimiter="|"):
        try:
            rows.append({"date": r["Date"], "symbol": r["Symbol"], "short": float(r["ShortVolume"]),
                         "exempt": float(r["ShortExemptVolume"]), "total": float(r["TotalVolume"])})
        except (KeyError, ValueError, TypeError):
            continue  # son satır toplam/boş olabilir
    return rows


def run(ctx: Context, rep: SourceReport) -> None:
    rows, day = [], None
    for d in business_days_back(ctx.today, 6):
        try:
            rows = parse_short_volume(ctx.client.get(URL.format(d=d)).text)
        except FetchError as exc:
            if exc.status in (403, 404):
                continue
            raise
        day = d
        break
    rep.expect_fresh("Güncellik", day, 5, ctx.today)
    if not rows:
        return
    rep.expect_range("Sembol sayısı", len(rows), 5000, 20000)
    rep.expect_min_ratio("Açığa satış ≤ toplam hacim", sum(1 for r in rows if r["short"] <= r["total"]), len(rows), 0.999, 0.99)
    symbols = {r["symbol"] for r in rows}
    common = [s.symbol for s in ctx.common_stocks()]
    rep.expect_min_ratio("Evren kapsamı", sum(1 for s in common if s in symbols), len(common), 0.9, 0.8)
    rep.sample = rows[:3]

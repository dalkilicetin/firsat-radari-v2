"""FRED (St. Louis Fed): emtia, enerji, faiz, üretim ve fiyat serileri.

1. yolda şirketin girdi ve çıktılarının trend yönünü bu seriler verir.
BLS ve EIA'nın birçok serisi FRED'de de yayımlanır; anahtar gerekmez.
"""

from __future__ import annotations

import csv
import io
from datetime import date

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "fred", "FRED makro ve emtia serileri", 1, [1, 4]

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"

# seri: (açıklama, güncellik sınırı gün olarak; aylık seriler ~1-2 ay gecikmeyle yayımlanır)
SERIES = {
    "DCOILWTICO": ("Ham petrol WTI (günlük)", 10),
    "DGS10": ("ABD 10 yıllık faiz (günlük)", 10),
    "PCOPPUSDM": ("Bakır fiyatı (aylık, IMF kaynaklı ~3 ay gecikmeli)", 130),
    "INDPRO": ("Sanayi üretimi (aylık)", 75),
    "CPIAUCSL": ("Tüketici fiyat endeksi (aylık)", 75),
    "IPG3344S": ("Yarı iletken üretimi (aylık)", 75),
}


def parse_fred_csv(text: str) -> dict[date, float | None]:
    out = {}
    reader = csv.reader(io.StringIO(text))
    next(reader, None)
    for row in reader:
        if len(row) < 2:
            continue
        try:
            d = date.fromisoformat(row[0])
        except ValueError:
            continue
        try:
            out[d] = float(row[1])
        except ValueError:
            out[d] = None  # FRED eksik gözlemi "." yazar
    return out


def run(ctx: Context, rep: SourceReport) -> None:
    sample = {}
    for sid, (label, max_age) in SERIES.items():
        series = parse_fred_csv(ctx.client.get(URL.format(sid=sid)).text)
        valid = {d: v for d, v in series.items() if v is not None}
        if not valid:
            rep.add(f"{sid} – {label}", Status.FAIL, "veri yok")
            continue
        latest = max(valid)
        first = min(valid)
        check = rep.expect_fresh(f"{sid} – {label}: güncellik", latest, max_age, ctx.today)
        check.detail += f"; {len(valid)} gözlem, başlangıç {first}"
        if first > date(2015, 1, 1):
            rep.add(f"{sid}: 2015'ten geriye uzanıyor", Status.WARN, f"başlangıç {first}")
        sample[sid] = {str(d): valid[d] for d in sorted(valid)[-3:]}
    rep.sample = sample

"""SEC günlük dosya indeksi: o gün SEC'e gelen tüm dosyaların listesi.

Haftalık çalışmada "bu hafta ne geldi?" sorusunun cevabı buradan çıkar:
Form 4 (içeriden işlemler), 8-K (önemli olaylar), 13F (fon pozisyonları),
S-1 / F-1 / 424B4 (halka arz hazırlığı ve fiyatlaması).
"""

from __future__ import annotations

import re
from collections import Counter
from datetime import date, datetime, timedelta

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context, IndexRow

KEY, TITLE, TIER, ROADS = "sec_index", "SEC günlük dosya indeksi", 1, [1, 3]

URL = "https://www.sec.gov/Archives/edgar/daily-index/{y}/QTR{q}/form.{d:%Y%m%d}.idx"
ROW = re.compile(
    r"^(?P<form>\S.*?)\s{2,}(?P<company>.+?)\s{2,}(?P<cik>\d{1,10})\s{2,}(?P<date>\d{8}|\d{4}-\d{2}-\d{2})\s+(?P<path>edgar/\S+)\s*$"
)
IPO_FORMS = {"S-1", "S-1/A", "F-1", "F-1/A", "424B4"}
# Sinyal üretmek için kullandığımız formlar. Diğerleri (EFFECT, DRS, MA-I, ATS-N...) idari formlardır.
USED_FORMS = {"4", "8-K", "10-K", "10-Q", "20-F", "6-K", "13F-HR", "SCHEDULE 13D", "SCHEDULE 13G", "NT 10-K", "NT 10-Q"} | IPO_FORMS


def parse_form_index(text: str) -> list[IndexRow]:
    rows = []
    for line in text.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        raw = m.group("date").replace("-", "")
        rows.append(IndexRow(
            form=m.group("form").strip(), company=m.group("company").strip(), cik=int(m.group("cik")),
            filed=datetime.strptime(raw, "%Y%m%d").date(), path=m.group("path"),
        ))
    return rows


def business_days_back(today: date, n: int) -> list[date]:
    days, d = [], today
    while len(days) < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:
            days.append(d)
    return days


def run(ctx: Context, rep: SourceReport) -> None:
    per_day: dict[date, list[IndexRow]] = {}
    for d in business_days_back(ctx.today, 7):
        try:
            text = ctx.client.get(URL.format(y=d.year, q=(d.month - 1) // 3 + 1, d=d),
                                  ok_statuses=(200,)).text
        except FetchError as exc:
            if exc.status in (403, 404):  # resmî tatil veya henüz yayımlanmamış gün
                continue
            raise
        per_day[d] = parse_form_index(text)
        if len(per_day) == 5:
            break

    rep.expect_range("Erişilebilen iş günü sayısı (son 7 iş günü içinde)", len(per_day), 4, 5)
    if not per_day:
        return
    latest_day = max(per_day)
    rep.expect_fresh("İndeks güncelliği", latest_day, max_days=4, today=ctx.today)

    for d, rows in sorted(per_day.items()):
        forms = Counter(r.form for r in rows)
        rep.expect_range(f"{d}: toplam dosya", len(rows), 1500, 15000)
        rep.expect_range(f"{d}: Form 4 sayısı", forms["4"], 300, 6000)
        # Bir kayıt indekse, SEC'in onu yayımladığı gün girer. Mesai sonrası dosyalamalar 1 gün kayabilir;
        # kullandığımız formlarda daha büyük fark beklenmez.
        used = [r for r in rows if r.form in USED_FORMS]
        late = [r for r in used if (d - r.filed).days > 1 + (d.weekday() == 0) * 2]
        check = rep.expect_min_ratio(f"{d}: kullanılan formlar 1 iş günü içinde yayımlanmış", len(used) - len(late), len(used), 0.999, 0.99)
        if late:
            check.detail += f"; örnek: {[(r.form, r.company[:25], str(r.filed)) for r in late[:3]]}"
        delayed = [r for r in rows if r.form.startswith("DRS") and r.filed != d]
        if delayed:
            rep.add(f"{d}: gizli taslak (DRS) — dosyalama ≠ yayım", Status.INFO,
                    f"{len(delayed)} kayıt, medyan gecikme {sorted((d - r.filed).days for r in delayed)[len(delayed) // 2]} gün "
                    "(geriye dönük testte yayım tarihi esas alınır)")

    all_rows = [r for rows in per_day.values() for r in rows]
    forms = Counter(r.form for r in all_rows)
    rep.add("Haftalık form dağılımı", Status.INFO,
            ", ".join(f"{f}: {forms[f]}" for f in ["4", "8-K", "13F-HR", "SCHEDULE 13D", "SCHEDULE 13G", "10-K", "10-Q", "S-1", "424B4", "NT 10-K"]),
            {f: forms[f] for f in ["4", "8-K", "13F-HR", "10-K", "10-Q", "S-1", "424B4", "NT 10-K"]})
    ipo = [r for r in all_rows if r.form in IPO_FORMS]
    rep.add("Halka arz hazırlığı (S-1/F-1/424B4)", Status.INFO,
            f"{len(ipo)} dosya; örnek: {[r.company for r in ipo[:8]]}")

    ctx.daily_index = all_rows
    rep.sample = [vars(r) | {"filed": str(r.filed)} for r in per_day[latest_day][:5]]

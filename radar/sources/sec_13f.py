"""SEC 13F: 100 milyon $ üzeri yöneten kurumların çeyreklik hisse pozisyonları.

Çeyrek sonundan 45 gün sonra gelir (en yavaş sinyal). Pozisyonlar CUSIP koduyla raporlanır;
CUSIP→ticker eşleştirmesi bir sonraki aşamanın işi.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from radar.quality import SourceReport, Status
from radar.sources.base import Context
from radar.sources.sec_form4 import ARCHIVE

KEY, TITLE, TIER, ROADS = "sec_13f", "SEC 13F (fon pozisyonları)", 1, [3]

BULK_PAGE = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
CUSIP = re.compile(r"^[0-9A-Z]{8}[0-9]$")


def parse_info_table(xml: str) -> list[dict]:
    # Ad alanlarını (namespace) yok sayarak ayrıştır.
    xml = re.sub(r'\sxmlns(:\w+)?="[^"]+"', "", xml)
    xml = re.sub(r"<(/?)\w+:", r"<\1", xml)
    root = ET.fromstring(xml)
    rows = []
    for it in root.iter("infoTable"):
        get = lambda p: (it.findtext(p) or "").strip()
        rows.append({
            "issuer": get("nameOfIssuer"), "cusip": get("cusip").upper(),
            "value": float(get("value") or 0), "shares": float(get("shrsOrPrnAmt/sshPrnamt") or 0),
            "type": get("shrsOrPrnAmt/sshPrnamtType"), "put_call": get("putCall"),
        })
    return rows


def run(ctx: Context, rep: SourceReport) -> None:
    filings = [r for r in ctx.daily_index if r.form == "13F-HR"]
    rep.add("Bu hafta gelen 13F-HR", Status.INFO, f"{len(filings)} dosya (çeyrek sonu +45 gün civarında yoğunlaşır)")
    sample = ctx.rng.sample(filings, min(5, len(filings)))
    tables, rows = 0, []
    for f in sample:
        text = ctx.client.get(ARCHIVE + f.path).text
        m = re.search(r"<(\w+:)?informationTable[\s>].*?</(\w+:)?informationTable>", text, re.DOTALL)
        if m:
            rows += parse_info_table(m.group(0))
            tables += 1
    if sample:
        rep.expect_min_ratio("Pozisyon tablosu ayrıştırılan 13F", tables, len(sample), 1.0, 0.8)
        rep.expect_min_ratio("Geçerli CUSIP", sum(1 for r in rows if CUSIP.match(r["cusip"])), len(rows), 0.99, 0.95)
        rep.expect_min_ratio("Değer ve adet pozitif", sum(1 for r in rows if r["value"] > 0 and r["shares"] > 0), len(rows), 0.97, 0.9)
    else:
        rep.add("13F örnekleme", Status.INFO, "bu hafta 13F-HR yok; örnek ayrıştırma atlandı")

    page = ctx.client.get(BULK_PAGE).text
    zips = sorted(set(re.findall(r'href="([^"]*13f[^"]*\.zip)"', page, re.IGNORECASE)))
    rep.expect_range("Toplu veri seti sayısı (geriye dönük test için)", len(zips), 20, 500)
    rep.add("Toplu veri seti örnekleri", Status.INFO, f"{zips[:2]} … {zips[-2:]}")
    rep.sample = rows[:5]

"""GDELT: dünya çapında haber akışı.

Asıl kaynak, GDELT'in 15 dakikada bir yayımladığı ham GKG dosyalarıdır: hız sınırı yoktur,
MD5 özetiyle doğrulanabilir ve Şubat 2015'e kadar geriye uzanır (geriye dönük test için).
Her kayıt bir haber makalesidir; içinde geçen kurumlar (Organizations) ve ton (V2Tone) bulunur.
DOC API (son 3 ay, hazır zaman serisi) yardımcı kaynaktır; paylaşımlı IP'lerde hız sınırına takılabilir.
"""

from __future__ import annotations

import csv
import hashlib
import io
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone

from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "gdelt", "GDELT haber akışı", 2, [2, 4]

LAST_UPDATE = "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
HISTORY_PROBE = "http://data.gdeltproject.org/gdeltv2/20150301000000.gkg.csv.zip"
DOC = "https://api.gdeltproject.org/api/v2/doc/doc?query={q}&mode=timelinevolraw&format=json&timespan=3months"

GKG_COLUMNS = 27
COL_DATE, COL_SOURCE, COL_URL, COL_ORGS, COL_TONE = 1, 3, 4, 13, 15

csv.field_size_limit(sys.maxsize)


def parse_last_update(text: str) -> dict[str, tuple[int, str, str]]:
    """{'export'|'mentions'|'gkg': (boyut, md5, url)}"""
    out = {}
    for line in text.split("\n"):
        parts = line.split()
        if len(parts) == 3:
            kind = "gkg" if ".gkg." in parts[2] else "mentions" if ".mentions." in parts[2] else "export"
            out[kind] = (int(parts[0]), parts[1], parts[2])
    return out


def read_gkg(zipped: bytes) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(zipped)) as zf:
        raw = zf.read(zf.namelist()[0]).decode("utf-8", errors="replace")
    return list(csv.reader(io.StringIO(raw), delimiter="\t", quoting=csv.QUOTE_NONE))


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
    files = parse_last_update(ctx.client.get(LAST_UPDATE).text)
    if "gkg" not in files:
        rep.add("Son güncelleme listesi", Status.FAIL, "GKG dosyası listede yok")
        return
    size, md5, url = files["gkg"]
    m = re.search(r"/(\d{14})\.", url)
    rep.expect_fresh("Ham dosya akışı güncelliği", datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc), 0.25)

    blob = ctx.client.get(url).content
    rep.add("İndirilen dosya bütünlüğü (boyut + MD5)",
            Status.OK if len(blob) == size and hashlib.md5(blob).hexdigest() == md5 else Status.FAIL,
            f"{len(blob):,} bayt, md5 {'eşleşti' if hashlib.md5(blob).hexdigest() == md5 else 'EŞLEŞMEDİ'}")

    rows = read_gkg(blob)
    rep.expect_range("15 dakikalık dosyada makale", len(rows), 500, 50_000)
    rep.expect_min_ratio(f"Sütun sayısı = {GKG_COLUMNS}", sum(1 for r in rows if len(r) == GKG_COLUMNS), len(rows), 0.999, 0.99)
    full = [r for r in rows if len(r) == GKG_COLUMNS]
    rep.expect_min_ratio("Kurum (Organizations) bilgisi olan", sum(1 for r in full if r[COL_ORGS]), len(full), 0.5, 0.3)
    tone_ok = 0
    for r in full:
        try:
            tone_ok += -100 <= float(r[COL_TONE].split(",")[0]) <= 100
        except ValueError:
            pass
    rep.expect_min_ratio("Ton değeri okunabilen", tone_ok, len(full), 0.99, 0.95)
    orgs = Counter(o for r in full for o in r[COL_ORGS].split(";") if o)
    rep.add("Bu 15 dakikada en çok geçen kurumlar", Status.INFO, ", ".join(f"{o} ({n})" for o, n in orgs.most_common(8)))

    try:
        old = read_gkg(ctx.client.get(HISTORY_PROBE).content)
        rep.expect_range("Geçmiş veri: 1 Mart 2015 dosyası makale", len(old), 100, 50_000)
    except (FetchError, zipfile.BadZipFile) as exc:
        rep.add("Geçmiş veri: 1 Mart 2015 dosyası", Status.FAIL, str(exc)[:150])

    try:
        points = parse_timeline(ctx.client.get(DOC.format(q='"Nvidia"'), retries=1).json())
        rep.add("Yardımcı: DOC API zaman serisi", Status.OK if points else Status.WARN, f"{len(points)} nokta")
    except (FetchError, ValueError) as exc:
        rep.add("Yardımcı: DOC API zaman serisi", Status.INFO,
                f"erişilemedi (HTTP {getattr(exc, 'status', '?')}); ham dosyalar yeterli")
    rep.sample = [{"date": r[COL_DATE], "source": r[COL_SOURCE], "orgs": r[COL_ORGS][:120]} for r in full[:3]]

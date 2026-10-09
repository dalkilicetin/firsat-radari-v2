"""Veri Sağlık Raporu: tüm kaynakları çeker, kontrol eder, raporu yazar.

Kullanım:
    python -m radar.health                 # tüm kaynaklar
    python -m radar.health --only fred,gdelt
"""

from __future__ import annotations

import argparse
import json
import time
import traceback
from datetime import date, datetime, timezone

from radar import config
from radar.http import HttpClient
from radar.quality import SourceReport, Status
from radar.sources import (fred, finra, gdelt, prices, sec_13f, sec_form4, sec_index, sec_submissions, sec_xbrl,
                           universe, usaspending, wikipedia)
from radar.sources.base import Context
from radar.sources.innovation import GitHubActivity, Patents
from radar.sources.social import GoogleNews, HackerNews, Reddit

# Sıra önemli: evren ve SEC indeksi, sonraki kaynakların örneklemi için bağlamı doldurur.
SOURCES = [universe, sec_index, sec_submissions, sec_xbrl, sec_form4, sec_13f, finra, usaspending, Patents,
           prices, fred, gdelt, wikipedia, HackerNews, GoogleNews, Reddit, GitHubActivity]

ICON = {Status.OK: "🟢", Status.WARN: "🟡", Status.FAIL: "🔴", Status.INFO: "ℹ️"}
LABEL = {Status.OK: "Kullanılabilir", Status.WARN: "Dikkat", Status.FAIL: "Kullanılamaz", Status.INFO: "Bilgi"}


def run_source(source, ctx: Context) -> SourceReport:
    rep = SourceReport(source.KEY, source.TITLE, source.TIER, source.ROADS)
    before, start = ctx.client.request_count, time.monotonic()
    try:
        source.run(ctx, rep)
    except Exception as exc:
        rep.error = f"{type(exc).__name__}: {exc}"[:500]
        rep.add("Çalışma hatası", Status.FAIL, rep.error, traceback.format_exc()[-1500:])
    rep.duration_s = round(time.monotonic() - start, 1)
    rep.requests = ctx.client.request_count - before
    return rep


def render_markdown(reports: list[SourceReport], run_at: datetime) -> str:
    counts = {s: sum(1 for r in reports if r.status == s) for s in (Status.OK, Status.WARN, Status.FAIL)}
    lines = [
        f"# Veri Sağlık Raporu — {run_at:%Y-%m-%d %H:%M} UTC",
        "",
        f"{ICON[Status.OK]} {counts[Status.OK]} kullanılabilir · {ICON[Status.WARN]} {counts[Status.WARN]} dikkat · "
        f"{ICON[Status.FAIL]} {counts[Status.FAIL]} kullanılamaz",
        "",
        "Kırmızı kaynaklar o hafta puanlamada kullanılmaz. Sınıf: 1 = resmî, 2 = güvenilir ama dolaylı.",
        "",
        "| Kaynak | Sınıf | Yol | Durum | Süre | İstek |",
        "|---|---|---|---|---|---|",
    ]
    for r in reports:
        lines.append(f"| [{r.title}](#{r.key}) | {r.tier} | {', '.join(map(str, r.roads))} | "
                     f"{ICON[r.status]} {LABEL[r.status]} | {r.duration_s} sn | {r.requests} |")
    for r in reports:
        lines += ["", f"<a id=\"{r.key}\"></a>", f"## {ICON[r.status]} {r.title}", "", "| Kontrol | Durum | Detay |", "|---|---|---|"]
        for c in r.checks:
            detail = str(c.detail).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {c.name} | {ICON[c.status]} | {detail} |")
    lines.append("")
    return "\n".join(lines)


def to_json(reports: list[SourceReport], run_at: datetime) -> dict:
    return {
        "run_at": run_at.isoformat(),
        "sources": [{
            "key": r.key, "title": r.title, "tier": r.tier, "roads": r.roads, "status": r.status.value,
            "error": r.error, "duration_s": r.duration_s, "requests": r.requests,
            "checks": [{"name": c.name, "status": c.status.value, "detail": c.detail, "value": c.value} for c in r.checks],
            "sample": r.sample,
        } for r in reports],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="virgülle ayrılmış kaynak anahtarları (evren ve SEC indeksi her zaman çalışır)")
    args = parser.parse_args(argv)

    only = set(args.only.split(",")) if args.only else None
    run_at = datetime.now(timezone.utc)
    ctx = Context(client=HttpClient(), today=date.today())
    reports = []
    for source in SOURCES:
        if only and source.KEY not in only and source.KEY not in ("universe", "sec_index"):
            continue
        rep = run_source(source, ctx)
        print(f"{ICON[rep.status]} {rep.title}: {rep.duration_s} sn, {rep.requests} istek", flush=True)
        reports.append(rep)

    config.REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md = render_markdown(reports, run_at)
    (config.REPORT_DIR / "latest.md").write_text(md)
    (config.REPORT_DIR / f"{run_at:%Y-%m-%d}.md").write_text(md)
    (config.REPORT_DIR / "latest.json").write_text(json.dumps(to_json(reports, run_at), ensure_ascii=False, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

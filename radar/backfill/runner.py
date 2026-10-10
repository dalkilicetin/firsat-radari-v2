"""Geçmiş veri yükleme komutları (GitHub Actions'tan çağrılır).

    python -m radar.backfill.runner plan [--dataset insider [--only 2024q1,2024q2] [--force]]
        (--dataset yoksa istekler backfill-request.json dosyasından okunur)
    python -m radar.backfill.runner run --dataset insider --partition 2024q1
    python -m radar.backfill.runner finalize --dataset insider
"""

from __future__ import annotations

import argparse
import json
import re
import time
import traceback
from datetime import date

from radar.backfill import storage
from radar.backfill.delisted import FailsToDeliver
from radar.backfill.filings import Filings, GdeltHistory
from radar.backfill.financials import FinancialStatements
from radar.backfill.holdings import InstitutionalHoldings
from radar.backfill.insider import InsiderTransactions
from radar.backfill.macro import FredSeries
from radar.backfill.market import DailyPrices, WikipediaViews
from radar.health import ICON, LABEL
from radar.http import HttpClient
from radar.quality import SourceReport, Status

DATASETS = {d.name: d for d in [InsiderTransactions(), FinancialStatements(), FailsToDeliver(), FredSeries(),
                                         DailyPrices(), WikipediaViews(), InstitutionalHoldings(),
                                         Filings(), GdeltHistory()]}
PARTS_DIR = storage.MANIFEST_DIR / "parts"
REPORT_DIR = storage.config.ROOT / "reports" / "backfill"


REQUEST_FILE = storage.config.ROOT / "backfill-request.json"
MATRIX_LIMIT = 250  # GitHub Actions matrix sınırı 256; fazlası sonraki istekte devam eder.


def plan(dataset: str, only: str = "", force: bool = False) -> list[str]:
    ds = DATASETS[dataset]
    available = ds.partitions(HttpClient(), date.today())
    if only:
        # "A" gibi bir önek, tarihli "A-20261009" bölümüyle de eşleşir; eşleşmeyen değer (örn. "yok") yalnızca kontrolleri çalıştırır.
        wanted = set(only.split(","))
        return [p for p in available if p in wanted or p.rsplit("-", 1)[0] in wanted]
    done = {p for p, e in storage.load_manifest(ds.name)["partitions"].items() if e["status"] != "fail"}
    return available if force else [p for p in available if p not in done]


def cmd_plan(args) -> None:
    """İstek: komut satırı (--dataset) ya da backfill-request.json ([{"dataset", "only", "force"}, ...])."""
    if args.dataset:
        requests = [{"dataset": args.dataset, "only": args.only or "", "force": args.force}]
    else:
        requests = json.loads(REQUEST_FILE.read_text())["requests"]
    include, datasets = [], []
    for r in requests:
        parts = plan(r["dataset"], r.get("only", ""), r.get("force", False))
        include += [{"dataset": r["dataset"], "partition": p} for p in parts]
        datasets.append(r["dataset"])
    print(json.dumps({"matrix": {"include": include[:MATRIX_LIMIT]}, "count": len(include[:MATRIX_LIMIT]),
                      "total": len(include), "datasets": " ".join(datasets),
                      "max_parallel": min(sum(DATASETS[d].max_parallel for d in set(datasets)), 12)}))


def cmd_run(args) -> int:
    ds = DATASETS[args.dataset]
    rep = SourceReport(f"{ds.name}:{args.partition}", ds.title, 1, [])
    client = HttpClient()
    entry = {"partition": args.partition, "fetched_at": storage.now_iso()}
    start = time.monotonic()
    try:
        loaded = ds.load(client, args.partition)
        ds.check_partition(loaded, args.partition, rep)
        path = storage.write_partition(ds.name, args.partition, loaded.df)
        entry |= {"rows": len(loaded.df), "bytes": path.stat().st_size, "sha256": storage.sha256(path),
                  "columns": {c: str(t) for c, t in loaded.df.dtypes.items()}, "sources": loaded.sources,
                  "notes": loaded.notes, "asset": storage.asset_name(ds.name, args.partition)}
    except Exception as exc:
        rep.add("Çalışma hatası", Status.FAIL, f"{type(exc).__name__}: {exc}"[:800], traceback.format_exc()[-2000:])
        entry |= {"rows": 0}
    entry |= {"status": rep.status.value, "duration_s": round(time.monotonic() - start, 1), "requests": client.request_count,
              "checks": [{"name": c.name, "status": c.status.value, "detail": c.detail} for c in rep.checks]}
    # Kırmızı bölüm arşive yüklenmez.
    if rep.status == Status.FAIL and storage.partition_path(ds.name, args.partition).exists():
        storage.partition_path(ds.name, args.partition).unlink()
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    (PARTS_DIR / f"{ds.name}__{args.partition}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=1, default=str))
    print(f"{ICON[rep.status]} {ds.name} {args.partition}: {entry['rows']:,} satır, {entry['duration_s']} sn")
    for c in rep.checks:
        print(f"  {ICON[c.status]} {c.name}: {c.detail}")
    return 0


def cmd_finalize(args) -> int:
    ds = DATASETS[args.dataset]
    manifest = storage.load_manifest(ds.name)
    manifest["title"] = ds.title
    for f in sorted(PARTS_DIR.glob(f"{ds.name}__*.json")):
        entry = json.loads(f.read_text())
        manifest["partitions"][entry["partition"]] = entry
        f.unlink()

    # Tarihli anlık görüntü bölümlerinde (A-20261009, snapshot-20261010) yalnızca grubun en yenisi geçerlidir.
    manifest["removed_assets"] = []
    for old in superseded(manifest["partitions"]):
        manifest["removed_assets"].append(manifest["partitions"].pop(old).get("asset"))

    rep = SourceReport(ds.name, ds.title, 1, [])
    derived = {}
    try:
        derived = ds.check_dataset(HttpClient(), manifest, rep)
    except Exception as exc:
        rep.add("Veri seti kontrolü hatası", Status.FAIL, f"{type(exc).__name__}: {exc}"[:800])
    manifest["derived"] = {}
    for name, df in derived.items():
        path = storage.write_partition(ds.name, name, df)
        manifest["derived"][name] = {"asset": storage.asset_name(ds.name, name), "rows": len(df), "sha256": storage.sha256(path)}
    manifest["dataset_checks"] = [{"name": c.name, "status": c.status.value, "detail": c.detail} for c in rep.checks]
    manifest["finalized_at"] = storage.now_iso()
    storage.save_manifest(manifest)
    write_report(manifest)
    return 0


def superseded(partitions: dict) -> list[str]:
    latest: dict[str, str] = {}
    for p, e in partitions.items():
        m = re.fullmatch(r"(.+)-(\d{8})", p)
        if m and e["status"] != "fail":
            group = m.group(1)
            if p > latest.get(group, ""):
                latest[group] = p
    # Başarısız bölümler kayıtta kalır (neden başarısız olduğu görünsün); plan onları yeniden dener.
    return [p for p, e in partitions.items()
            if e["status"] != "fail" and (m := re.fullmatch(r"(.+)-(\d{8})", p))
            and m.group(1) in latest and p != latest[m.group(1)]]


def write_report(manifest: dict) -> None:
    parts = manifest["partitions"]
    status_of = lambda checks: max((Status(c["status"]) for c in checks if c["status"] != "info"),
                                   key=lambda s: ["ok", "warn", "fail"].index(s.value), default=Status.OK)
    overall = status_of(manifest["dataset_checks"] + [{"status": e["status"]} for e in parts.values()])
    total_rows = sum(e.get("rows", 0) for e in parts.values())
    lines = [f"# {ICON[overall]} {manifest.get('title', manifest['dataset'])}", "",
             f"Son güncelleme: {manifest['finalized_at']} · {len(parts)} bölüm · {total_rows:,} satır", "",
             "## Veri seti kontrolleri", "", "| Kontrol | Durum | Detay |", "|---|---|---|"]
    lines += [f"| {c['name']} | {ICON[Status(c['status'])]} | {str(c['detail']).replace('|', '/')} |" for c in manifest["dataset_checks"]]
    lines += ["", "## Bölümler", "", "| Bölüm | Durum | Satır | Uyarı / hata |", "|---|---|---|---|"]
    for p, e in sorted(parts.items()):
        issues = "; ".join(f"{c['name']}: {c['detail']}" for c in e["checks"] if c["status"] in ("warn", "fail"))
        lines.append(f"| {p} | {ICON[Status(e['status'])]} {LABEL[Status(e['status'])]} | {e.get('rows', 0):,} | "
                     f"{issues.replace('|', '/')[:300]} |")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"{manifest['dataset']}.md").write_text("\n".join(lines) + "\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "run", "finalize"):
        sp = sub.add_parser(name)
        sp.add_argument("--dataset", required=name != "plan", choices=sorted(DATASETS))
        if name == "plan":
            sp.add_argument("--only")
            sp.add_argument("--force", action="store_true")
        if name == "run":
            sp.add_argument("--partition", required=True)
    args = p.parse_args(argv)
    return {"plan": cmd_plan, "run": cmd_run, "finalize": cmd_finalize}[args.cmd](args) or 0


if __name__ == "__main__":
    raise SystemExit(main())

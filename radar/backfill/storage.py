"""Bölüm dosyaları ve manifest."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from radar import config

BACKFILL_DIR = config.DATA_DIR / "backfill"
MANIFEST_DIR = config.DATA_DIR / "manifest"
RELEASE_TAG = "veri-arsivi"


def asset_name(dataset: str, partition: str) -> str:
    return f"{dataset}__{partition}.parquet"


def partition_path(dataset: str, partition: str) -> Path:
    return BACKFILL_DIR / dataset / asset_name(dataset, partition)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_partition(dataset: str, partition: str, df: pd.DataFrame) -> Path:
    path = partition_path(dataset, partition)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False, compression="zstd")
    return path


def read_partition(dataset: str, partition: str) -> pd.DataFrame:
    return pd.read_parquet(partition_path(dataset, partition))


def manifest_path(dataset: str) -> Path:
    return MANIFEST_DIR / f"{dataset}.json"


def load_manifest(dataset: str) -> dict:
    path = manifest_path(dataset)
    if path.exists():
        return json.loads(path.read_text())
    return {"dataset": dataset, "partitions": {}, "dataset_checks": []}


def save_manifest(manifest: dict) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest["partitions"] = dict(sorted(manifest["partitions"].items()))
    manifest_path(manifest["dataset"]).write_text(json.dumps(manifest, ensure_ascii=False, indent=1, default=str) + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

"""Geçmiş veri arşivini okuma.

Bölümler GitHub Releases'teki 'veri-arsivi' sürümünden indirilir, yerelde data/backfill/ altında saklanır
ve okunmadan önce sha256 özetleri manifestle karşılaştırılır. Özet tutmayan dosya kullanılmaz.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from radar.backfill import storage

RELEASE_URL = "https://github.com/dalkilicetin/firsat-radari-v2/releases/download/veri-arsivi/{asset}"


class IntegrityError(Exception):
    pass


def entries(dataset: str) -> dict[str, dict]:
    """Geçerli (kırmızı olmayan) bölümler ve türetilmiş tablolar: ad -> manifest kaydı."""
    m = storage.load_manifest(dataset)
    out = {p: e for p, e in m["partitions"].items() if e["status"] != "fail" and e.get("asset")}
    out |= {name: e for name, e in m.get("derived", {}).items()}
    return out


def ensure(dataset: str, name: str, entry: dict) -> str:
    path = storage.partition_path(dataset, name)
    if path.exists() and storage.sha256(path) == entry["sha256"]:
        return str(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    with requests.get(RELEASE_URL.format(asset=entry["asset"]), stream=True, timeout=600) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1 << 22):
                f.write(chunk)
    tmp.replace(path)
    if storage.sha256(path) != entry["sha256"]:
        path.unlink()
        raise IntegrityError(f"{entry['asset']}: sha256 manifestle eşleşmiyor")
    return str(path)


def fetch(dataset: str, names: list[str] | None = None, workers: int = 4) -> list[str]:
    ent = entries(dataset)
    names = sorted(ent) if names is None else names
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda n: ensure(dataset, n, ent[n]), names))


def load(dataset: str, names: list[str] | None = None, columns: list[str] | None = None,
         filters=None) -> pd.DataFrame:
    """Bir veri setinin (ya da seçilen bölümlerinin) tamamını tek tabloda okur."""
    ent = entries(dataset)
    names = [n for n in sorted(ent) if n not in storage.load_manifest(dataset).get("derived", {})] if names is None else names
    paths = fetch(dataset, names)
    frames = [pd.read_parquet(p, columns=columns, filters=filters) for p in paths]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=columns)


if __name__ == "__main__":
    # python -m radar.archive insider ftd ...   → bölümleri indirip doğrular
    for ds in sys.argv[1:]:
        paths = fetch(ds)
        print(f"{ds}: {len(paths)} dosya doğrulandı")

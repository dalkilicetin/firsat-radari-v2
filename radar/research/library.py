"""Sinyal kütüphanesi: tüm yolların sinyalleri tek yerde, önbellekli.

Her sinyal bir yola aittir (piyasa, 1–4). Hesaplanan sinyaller data/derived/signals/ altında saklanır;
girdi verisi değişirse (manifest sha256) önbellek yenilenir.
"""

from __future__ import annotations

import hashlib
import json
import re

import numpy as np
import pandas as pd

from radar import config
from radar.backfill import storage
from radar.research import panel

CACHE = config.DATA_DIR / "derived" / "signals"

ROADS = {
    "piyasa": "Piyasa (fiyat hareketi)",
    "yol1": "1. yol: iş modeli ve yön",
    "yol2": "2. yol: gündem",
    "yol3": "3. yol: kurumsal sinyaller",
    "yol4": "4. yol: temadan hisseye",
}
# Grup → (yol, girdi veri setleri, üretici)
GROUPS = {
    "piyasa": ("piyasa", ["prices", "ftd", "financials"]),
    "road1": ("yol1", ["financials", "prices"]),
    "road1_text": ("yol1", ["tenk"]),
    "road2": ("yol2", ["gdelt", "wikiviews"]),
    "road3": ("yol3", ["insider", "holdings", "filings", "financials", "ftd"]),
    "road4": ("yol4", ["gdelt_themes"]),
    "baglam": ("piyasa", ["prices", "filings"]),  # sektör ETF'leri ve beta
}


def market_signals(p: dict) -> dict[str, pd.DataFrame]:
    """Fiyat kökenli kontrol sinyalleri (literatürde bilinen etkiler)."""
    from radar.research import fundamentals
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    price, raw = p["price"], p["raw"]
    wret = price / price.shift(1) - 1
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    shares = pit(sh.rename(columns={"accepted": "date"}), price.index, price.columns, FUNDAMENTAL_MAX_AGE)
    return {
        "momentum_12_1": price.shift(4) / price.shift(52) - 1,
        "kisa_vade_donus": -(price / price.shift(1) - 1),
        "dusuk_oynaklik": -wret.rolling(26, min_periods=13).std(),
        "kucuk_boyut": -np.log(shares * raw),
    }


def producers():
    from radar.research import context, road1, road2, road3, road4
    return {
        "piyasa": market_signals,
        "road1": road1.signals,
        "road1_text": road1.text_signals,
        "road2": road2.signals,
        "road3": road3.signals,
        "road4": lambda p: road4.signals(p, road4.VARIANTS),
        "baglam": context.signals,
    }


def filename(name: str) -> str:
    """Sinyal adı → güvenli dosya adı (ad '/' ya da boşluk içerebilir)."""
    return re.sub(r"[^0-9A-Za-z_.-]+", "_", name) + ".parquet"


# Sinyaller şirket listesine (kimlik katmanı: evren, çıkışlar, semboller) bağlıdır; bu veri setleri değişince tüm
# gruplar yeniden hesaplanır (ör. NYSE eklendiğinde haber eşleştirmesi yeni şirketleri de kapsamalı).
IDENTITY_INPUTS = ["universe", "filings", "insider", "prices", "ftd"]


def fingerprint(datasets: list[str]) -> str:
    h = hashlib.sha256()
    for ds in sorted(set(datasets) | set(IDENTITY_INPUTS)):
        m = storage.load_manifest(ds)
        h.update(json.dumps({k: e.get("sha256") for k, e in sorted(m["partitions"].items())}).encode())
    return h.hexdigest()[:16]


def load_group(group: str, p: dict, force: bool = False) -> dict[str, pd.DataFrame]:
    road, datasets = GROUPS[group]
    fp = fingerprint(datasets)
    meta_path = CACHE / f"{group}.json"
    if not force and meta_path.exists() and json.loads(meta_path.read_text()).get("fingerprint") == fp:
        names = json.loads(meta_path.read_text())["signals"]
        return {n: pd.read_parquet(CACHE / filename(n)) for n in names}
    sigs = producers()[group](p)
    CACHE.mkdir(parents=True, exist_ok=True)
    for name, df in sigs.items():
        df.astype("float32").to_parquet(CACHE / filename(name))
    meta_path.write_text(json.dumps({"fingerprint": fp, "road": road, "signals": list(sigs)}))
    return {n: df.astype("float32") for n, df in sigs.items()}


def load_all(p: dict, groups: list[str] | None = None) -> dict[str, tuple[str, pd.DataFrame]]:
    """ad → (yol, geniş tablo; olaylar 1/0)."""
    out = {}
    for g in groups or list(GROUPS):
        road = GROUPS[g][0]
        for name, df in load_group(g, p).items():
            out[name] = (road, df.reindex(index=p["price"].index, columns=p["price"].columns))
    return out

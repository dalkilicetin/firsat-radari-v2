"""2. yol: gündem sinyalleri (Wikipedia görüntülenme ve GDELT haber akışı).

Kurum adı eşleştirmesi: GDELT kurumları küçük harfli serbest metindir ("apple inc", "nvidia", "microsoft corp").
Her şirket için SEC/Nasdaq adından varyantlar üretilir (tam ad, sade ad, sade ad + inc/corp/corporation);
birden çok şirkete denk gelen varyantlar ve tek kelimelik genel sözcükler kullanılmaz.
Not: Google News ve Hacker News'in geçmişi yok; bunlar yalnızca canlı haftalık çalışmada kullanılacak.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research.pit import to_friday, weekly

SUFFIXES = r"\b(incorporated|inc|corporation|corp|company|co|ltd|limited|plc|holdings?|group|n\.?v|s\.?a|ag|se|lp|llc|the)\b"
# Tek başına geçtiğinde şirketten çok genel anlam taşıyan sözcükler.
GENERIC = {"apple", "target", "visa", "amazon", "alphabet", "meta", "block", "match", "gap", "ball", "progressive",
           "general", "american", "united", "first", "national", "global", "international", "energy", "capital",
           "financial", "health", "bank", "pacific", "atlantic", "southern", "northern", "western", "eastern", "central",
           "digital", "data", "power", "solar", "gold", "silver", "oil", "gas", "life", "care", "home", "auto", "air",
           "water", "food", "media", "network", "systems", "technologies", "therapeutics", "pharmaceuticals", "bio"}


def clean_name(name: str) -> str:
    n = str(name).split(" - ")[0].lower()
    n = n.replace("&", " and ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", n)).strip()


def aliases(securities: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cik, name in zip(securities.cik, securities.name):
        full = clean_name(name)
        base = re.sub(r"\s+", " ", re.sub(SUFFIXES, " ", full)).strip()
        variants = {full, base, f"{base} inc", f"{base} corp", f"{base} corporation", f"{base} holdings"}
        for v in variants:
            if not v or len(v) < 4:
                continue
            if " " not in v and (v in GENERIC or len(v) < 5):
                continue
            rows.append((v, int(cik)))
    df = pd.DataFrame(rows, columns=["org", "cik"]).drop_duplicates()
    ambiguous = df.groupby("org").cik.nunique()
    return df[df.org.isin(ambiguous[ambiguous == 1].index)]


def gdelt_weekly(dates, columns, securities: pd.DataFrame) -> dict[str, pd.DataFrame]:
    al = aliases(securities)
    names = set(al.org) | {"__TOPLAM_MAKALE__"}
    frames = []
    for part in sorted(archive.entries("gdelt")):
        df = archive.load("gdelt", names=[part], filters=[("org", "in", list(names))])
        frames.append(df)
    g = pd.concat(frames, ignore_index=True)
    total = g[g.org == "__TOPLAM_MAKALE__"][["date", "mentions"]]
    g = g.merge(al, on="org")
    g["tone_x"] = g.tone * g.mentions
    daily = g.groupby(["date", "cik"]).agg(mentions=("mentions", "sum"), tone_x=("tone_x", "sum")).reset_index()
    m = weekly(daily.rename(columns={"mentions": "value"})[["cik", "date", "value"]], dates, columns, "sum")
    tx = weekly(daily.rename(columns={"tone_x": "value"})[["cik", "date", "value"]], dates, columns, "sum")
    tot = total.assign(friday=to_friday(total.date)).groupby("friday").mentions.sum().reindex(dates)
    return {"mentions": m.reindex(dates).fillna(0), "tone_x": tx.reindex(dates).fillna(0), "total": tot,
            "coverage": al.cik.nunique()}


def wiki_weekly(dates, columns, securities: pd.DataFrame) -> pd.DataFrame:
    w = archive.load("wikiviews", columns=["symbol", "date", "views"])
    w = w.merge(securities[securities.status == "aktif"][["symbol", "cik"]], on="symbol")
    return weekly(w.rename(columns={"views": "value"})[["cik", "date", "value"]], dates, columns, "sum").reindex(dates)


def signals(p: dict) -> dict[str, pd.DataFrame]:
    price, sec = p["price"], p["securities"]
    dates, cols = price.index, price.columns
    out = {}

    views = wiki_weekly(dates, cols, sec)
    base = views.shift(4).rolling(52, min_periods=26).mean()
    recent = views.rolling(4).mean()
    out["wiki_ilgi_ivmesi"] = np.log((recent + 1) / (base + 1)).where(base > 50)
    out["wiki_ani_ilgi"] = (views > 3 * base) & (base > 50)

    g = gdelt_weekly(dates, cols, sec)
    m, tx = g["mentions"], g["tone_x"]
    # Toplam haber hacmindeki değişimi (GDELT kaynak sayısı yıllar içinde değişti) ayıklamak için normalize et.
    norm = m.div(g["total"] / g["total"].rolling(52, min_periods=26).mean(), axis=0)
    hb = norm.shift(4).rolling(52, min_periods=26).mean()
    hr = norm.rolling(4).mean()
    out["haber_ivmesi"] = np.log((hr + 1) / (hb + 1)).where(hb >= 1)
    out["haber_ani_artis"] = (norm > 3 * hb) & (m >= 5) & (hb >= 1)
    tone_recent = tx.rolling(4).sum() / m.rolling(4).sum()
    tone_base = tx.shift(4).rolling(52, min_periods=26).sum() / m.shift(4).rolling(52, min_periods=26).sum()
    out["haber_ton_degisimi"] = (tone_recent - tone_base).where(m.rolling(4).sum() >= 5)
    out["haber_ton_seviyesi"] = tone_recent.where(m.rolling(4).sum() >= 5)
    return out

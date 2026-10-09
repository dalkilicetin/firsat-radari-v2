"""Veri seti arayüzü ve ortak yardımcılar."""

from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from radar.http import HttpClient
from radar.quality import SourceReport


@dataclass
class Loaded:
    df: pd.DataFrame
    sources: list[str]
    notes: dict = field(default_factory=dict)


class Dataset:
    name = ""
    title = ""
    # Aynı anda en fazla kaç bölüm yüklensin (kaynağın hız sınırına saygı).
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        raise NotImplementedError

    def load(self, client: HttpClient, partition: str) -> Loaded:
        raise NotImplementedError

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        pass

    def check_dataset(self, client: HttpClient, manifest: dict, rep: SourceReport) -> dict[str, pd.DataFrame]:
        """Veri seti düzeyinde kontroller. Türetilmiş tablolar dönebilir (ad -> tablo); bunlar da arşive yüklenir."""
        return {}


# --- Yardımcılar -------------------------------------------------------------

def links(client: HttpClient, page: str, pattern: str) -> dict[str, str]:
    """Bir listeleme sayfasındaki zip bağlantıları: {yakalanan anahtar: tam adres}. Desen tek grup içermeli."""
    html = client.get(page).text
    out = {}
    for href in re.findall(r'href="([^"]+\.zip)"', html):
        m = re.search(pattern, href, re.IGNORECASE)
        if m:
            url = href if href.startswith("http") else "https://www.sec.gov" + href
            out.setdefault(m.group(1).lower(), url)
    return out


def quarter_of(d: date) -> str:
    return f"{d.year}q{(d.month - 1) // 3 + 1}"


def quarter_bounds(partition: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    year, q = int(partition[:4]), int(partition[-1])
    start = pd.Timestamp(year=year, month=3 * q - 2, day=1)
    return start, start + pd.offsets.QuarterEnd(0)


def read_zip_member(blob: bytes, suffix: str, **kwargs) -> pd.DataFrame:
    """Zip içindeki adı `suffix` ile biten sekme/çizgi ayraçlı tabloyu metin olarak okur; sütun adları büyük harf."""
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(suffix.lower())]
        if not names:
            raise KeyError(f"zip içinde *{suffix} yok: {zf.namelist()}")
        with zf.open(names[0]) as f:
            kwargs.setdefault("sep", "\t")
            df = pd.read_csv(f, dtype=str, keep_default_na=False, quoting=3, encoding="utf-8",
                             encoding_errors="replace", on_bad_lines="warn", **kwargs)
    df.columns = [c.strip().upper() for c in df.columns]
    return df


def require(df: pd.DataFrame, columns: list[str], what: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KeyError(f"{what}: eksik sütunlar {missing}; mevcut: {list(df.columns)}")


def to_number(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.replace(",", "", regex=False).str.strip(), errors="coerce")


def to_date(s: pd.Series, fmt: str | None = None) -> pd.Series:
    out = pd.to_datetime(s.str.strip(), format=fmt, errors="coerce")
    if fmt:  # biçim tutmayanlar için genel ayrıştırıcıyla ikinci deneme
        rest = out.isna() & (s.str.strip() != "")
        if rest.any():
            out[rest] = pd.to_datetime(s[rest].str.strip(), format="mixed", errors="coerce")
    return out

"""Şirket türü: faaliyet şirketi / finans / SPAC.

Kullanıcı kararları (2026-10-10): yalnızca faaliyet şirketleri, sektörlere bölünmeden tek genel liste.
Hariç: bankalar, sigorta, GYO (REIT), fonlar/BDC'ler ve SPAC'ler. Dahil: aracı kurum, fintech, kripto ve diğer
finansal hizmet şirketleri (HOOD, SOFI, COIN, MSTR, AFRM gibi).

SIC kodu SEC şirket kaydından gelir (güncel değer; SIC nadiren değişir, geçmiş için de kullanılır).
SPAC'ler çoğu zaman hedef sektörün SIC kodunu taşır; bu yüzden adla da yakalanır.
"""

from __future__ import annotations

import re

import pandas as pd

from radar import archive

SPAC_NAME = re.compile(
    r"\bacquisitions?\b(?:\s+[ivx\d]+)?\s+(?:corp|co\b|company|limited|ltd|inc|holdings?)"
    r"|\bspac\b|\bmerger\s+corp|\bcapital\s+corp(?:oration)?\s+[ivx]+\b|\bblank\s+check",
    re.IGNORECASE)
# SIC kodu olmayanlar için: ad finans şirketine işaret ediyorsa.
FINANCE_NAME = re.compile(
    r"\b(?:bank|bancorp|bancshares|bancorporation|financial\s+corp|finance\s+corp|bdc|business\s+development|"
    r"investment\s+corp|insurance|capital\s+southwest|real\s+estate\s+investment|reit)\b", re.IGNORECASE)


def load_sic() -> pd.Series:
    f = archive.load("filings", columns=["cik", "sic"]).drop_duplicates("cik")
    return f.assign(cik=f.cik.astype(str)).set_index("cik").sic.fillna("").astype(str)


def classify(sec: pd.DataFrame, sic: pd.Series | None = None) -> pd.Series:
    """cik → 'faaliyet' | 'finans' | 'spac'."""
    sic = load_sic() if sic is None else sic
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik")
    code = sic.reindex(s.index).fillna("")
    name = s.name.fillna("")
    out = pd.Series("faaliyet", index=s.index)
    excluded = code.str.match(r"^(?:60[2-3]\d|671\d|63\d\d|64\d\d|6798|6722|6726|6799)$")
    out[excluded | ((code == "") & name.str.contains(FINANCE_NAME))] = "finans"
    out[(code == "6770") | name.str.contains(SPAC_NAME)] = "spac"
    return out


def operating_mask(p: dict, sic: pd.Series | None = None) -> pd.Series:
    """Panel sütunları için: finans dışı faaliyet şirketi mi (bool)."""
    kind = classify(p["securities"], sic).reindex(p["price"].columns)
    return kind.eq("faaliyet")


def operating_universes(p: dict) -> dict[str, pd.DataFrame]:
    """report.universes ile aynı yapı, yalnızca faaliyet şirketleri."""
    from radar.research.report import universes
    keep = operating_mask(p)
    return {k: u & keep for k, u in universes(p).items()}

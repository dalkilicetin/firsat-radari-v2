"""Kaynakların paylaştığı çalışma bağlamı."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date

from radar.http import HttpClient


@dataclass
class Security:
    symbol: str
    name: str
    market_category: str
    financial_status: str
    is_common: bool
    cik: int | None = None


@dataclass
class IndexRow:
    form: str
    company: str
    cik: int
    filed: date
    path: str


@dataclass
class Context:
    client: HttpClient
    today: date
    universe: list[Security] = field(default_factory=list)
    cik_by_ticker: dict[str, int] = field(default_factory=dict)
    daily_index: list[IndexRow] = field(default_factory=list)
    rng: random.Random = field(default_factory=lambda: random.Random(0))

    def common_stocks(self) -> list[Security]:
        return [s for s in self.universe if s.is_common]

    def sample_symbols(self, n: int, with_cik: bool = False) -> list[str]:
        pool = [s.symbol for s in self.common_stocks() if s.cik or not with_cik]
        return self.rng.sample(sorted(pool), min(n, len(pool)))

"""Veri kalitesi kontrol modeli.

Bir kaynak birden çok kontrol üretir; kaynağın durumu kontrollerin en kötüsüdür.
- OK   (yeşil): kullanılabilir.
- WARN (sarı):  kullanılabilir ama dikkat; rapor nedenini yazar.
- FAIL (kırmızı): o hafta puanlamada kullanılmaz.
- INFO: bilgi amaçlı, durumu etkilemez.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any


class Status(str, Enum):
    OK = "ok"
    WARN = "warn"
    FAIL = "fail"
    INFO = "info"


SEVERITY = {Status.INFO: 0, Status.OK: 1, Status.WARN: 2, Status.FAIL: 3}


@dataclass
class Check:
    name: str
    status: Status
    detail: str
    value: Any = None


@dataclass
class SourceReport:
    key: str
    title: str
    tier: int
    roads: list[int]
    checks: list[Check] = field(default_factory=list)
    error: str | None = None
    duration_s: float = 0.0
    requests: int = 0
    sample: Any = None

    @property
    def status(self) -> Status:
        if self.error:
            return Status.FAIL
        scored = [c.status for c in self.checks if c.status != Status.INFO]
        if not scored:
            return Status.WARN
        return max(scored, key=SEVERITY.__getitem__)

    def add(self, name: str, status: Status, detail: str, value: Any = None) -> Check:
        check = Check(name, status, detail, value)
        self.checks.append(check)
        return check

    # Sık kullanılan kontrol kalıpları --------------------------------------

    def expect_range(self, name: str, value: float | None, lo: float, hi: float, unit: str = "",
                     warn_only: bool = False) -> Check:
        if value is None:
            return self.add(name, Status.FAIL, "değer yok")
        ok = lo <= value <= hi
        status = Status.OK if ok else (Status.WARN if warn_only else Status.FAIL)
        return self.add(name, status, f"{_fmt(value)}{unit} (beklenen {_fmt(lo)}–{_fmt(hi)}{unit})", value)

    def expect_min_ratio(self, name: str, good: int, total: int, ok_at: float, warn_at: float,
                         what: str = "") -> Check:
        if total == 0:
            return self.add(name, Status.FAIL, "örnek yok")
        ratio = good / total
        status = Status.OK if ratio >= ok_at else Status.WARN if ratio >= warn_at else Status.FAIL
        return self.add(name, status, f"{good}/{total} = %{ratio * 100:.1f} {what}".rstrip(), round(ratio, 4))

    def expect_fresh(self, name: str, latest: date | datetime | None, max_days: float,
                     today: date | None = None) -> Check:
        if latest is None:
            return self.add(name, Status.FAIL, "tarih bulunamadı")
        if isinstance(latest, datetime):
            now = datetime.now(timezone.utc)
            if latest.tzinfo is None:
                latest = latest.replace(tzinfo=timezone.utc)
            age = (now - latest).total_seconds() / 86400
        else:
            age = ((today or date.today()) - latest).days
        status = Status.OK if age <= max_days else Status.WARN if age <= max_days * 2 else Status.FAIL
        return self.add(name, status, f"en son kayıt {latest:%Y-%m-%d}, {age:.1f} gün önce (sınır {max_days})",
                        round(age, 2))

    def expect_equal(self, name: str, actual: float | None, expected: float, rel_tol: float = 0.0) -> Check:
        if actual is None:
            return self.add(name, Status.FAIL, f"değer yok (beklenen {_fmt(expected)})")
        ok = abs(actual - expected) <= abs(expected) * rel_tol if rel_tol else actual == expected
        return self.add(name, Status.OK if ok else Status.FAIL,
                        f"okunan {_fmt(actual)}, beklenen {_fmt(expected)}", actual)


def _fmt(v: float) -> str:
    if isinstance(v, float) and not v.is_integer():
        return f"{v:,.3f}"
    return f"{int(v):,}"

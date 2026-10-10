"""Sinyal değerlendirme: bir sinyalin tek başına gelecekteki fazla getiriyle ilişkisi.

Ölçütler (her vade için):
- IC: her hafta sinyal ile ileri fazla getiri arasındaki sıralama korelasyonu (Spearman); ortalaması ve t değeri.
  t değeri örtüşmeyen haftalarla hesaplanır (3 aylık vadede her 13 haftada bir), yoksa şişer.
- İlk-son %10 farkı: sinyali en yüksek %10'un ortalama fazla getirisi eksi en düşük %10'unki
  (uç değerler her hafta %1/%99'da kırpılır).
- İsabet: en yüksek %10'un fazla getirisi pozitif olan payı.
- Yıllara göre IC: istikrar.
Fazla getiri = hissenin getirisi − o haftaki aynı evrendeki (universe) üyelerin medyan getirisi. Evren
daraltıldığında (ör. yatırılabilir hisseler) kıyas da o evrenin medyanıdır; aksi halde büyüklük etkisi
sinyal sanılır.

Son dönem kuralı: ileri getiri penceresi HOLDOUT_START'a taşan haftalar kullanılmaz (4. aşamanın sonuna saklanır).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from radar.research import panel

HOLDOUT_START = pd.Timestamp("2025-07-01")
MIN_NAMES = 50
_RET_CACHE: dict[tuple[int, str], pd.DataFrame] = {}
PERIOD = "gelistirme"  # "gelistirme": son dönem öncesi; "son_donem": yalnızca tek seferlik test (run_holdout)


def forward(price: pd.DataFrame, sec: pd.DataFrame, weeks: int) -> pd.DataFrame:
    key = (weeks, PERIOD)
    if key not in _RET_CACHE:
        r = panel.forward_returns(price, sec, weeks)
        if PERIOD == "gelistirme":
            r = r[r.index + pd.Timedelta(weeks=weeks) < HOLDOUT_START]
        else:
            r = r[r.index >= HOLDOUT_START]
        _RET_CACHE[key] = r
    return _RET_CACHE[key]


def excess_returns(price: pd.DataFrame, sec: pd.DataFrame, weeks: int, universe: pd.DataFrame | None = None) -> pd.DataFrame:
    r = forward(price, sec, weeks)
    if universe is not None:
        r = r.where(universe.reindex(index=r.index, columns=r.columns).fillna(False).astype(bool))
    return r.sub(r.median(axis=1), axis=0)


def tstat(x: pd.Series) -> float:
    """Ortalama / standart hata; örnek < 3 ya da sapma 0 ise tanımsız."""
    sd = x.std(ddof=1)
    return float(x.mean() / sd * np.sqrt(len(x))) if len(x) > 2 and sd > 0 else float("nan")


def _winsor(df: pd.DataFrame, q: float = 0.01) -> pd.DataFrame:
    lo, hi = df.quantile(q, axis=1), df.quantile(1 - q, axis=1)
    return df.clip(lo, hi, axis=0)


@dataclass
class Result:
    name: str
    rows: list[dict] = field(default_factory=list)
    yearly: dict[str, dict[int, float]] = field(default_factory=dict)
    coverage: float = 0.0

    def table(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows).set_index("vade")


def evaluate(signal: pd.DataFrame, price: pd.DataFrame, sec: pd.DataFrame, name: str,
             horizons: dict[str, int] | None = None, sign: int = 1, universe: pd.DataFrame | None = None) -> Result:
    """signal: panel ile aynı indeks/sütunlarda geniş tablo (NaN = sinyal yok). sign=-1: düşük değer iyi."""
    horizons = horizons or panel.HORIZONS
    sig = (signal * sign).reindex(index=price.index, columns=price.columns)
    res = Result(name, coverage=float(sig.notna().sum(axis=1).median()))
    for label, weeks in horizons.items():
        ex = excess_returns(price, sec, weeks, universe)
        s = sig.reindex(ex.index)
        valid = s.notna() & ex.notna()
        n = valid.sum(axis=1)
        dates = n[n >= MIN_NAMES].index
        if len(dates) == 0:
            res.rows.append({"vade": label, "hafta": 0})
            continue
        s_rank = s.where(valid).loc[dates].rank(axis=1, pct=True)
        e_rank = ex.where(valid).loc[dates].rank(axis=1, pct=True)
        ic = s_rank.corrwith(e_rank, axis=1, method="pearson")  # sıralar üzerinde Pearson = Spearman
        step = ic.iloc[::max(weeks, 1)]
        t = tstat(step)
        exw = _winsor(ex.where(valid).loc[dates])
        top = exw.where(s_rank >= 0.9)
        bottom = exw.where(s_rank <= 0.1)
        spread = (top.mean(axis=1) - bottom.mean(axis=1))
        res.rows.append({
            "vade": label, "hafta": len(dates), "ort_hisse": int(n.loc[dates].mean()),
            "IC": round(float(ic.mean()), 4), "IC_t": round(float(t), 2),
            "ilk10_fazla": round(float(top.mean(axis=1).mean()), 4),
            "son10_fazla": round(float(bottom.mean(axis=1).mean()), 4),
            "fark": round(float(spread.mean()), 4),
            "isabet_ilk10": round(float((top > 0).sum().sum() / max(top.notna().sum().sum(), 1)), 3),
        })
        res.yearly[label] = {int(y): round(float(v), 3) for y, v in ic.groupby(ic.index.year).mean().items()}
    return res


def evaluate_event(flag: pd.DataFrame, price: pd.DataFrame, sec: pd.DataFrame, name: str,
                   horizons: dict[str, int] | None = None, universe: pd.DataFrame | None = None) -> Result:
    """Seyrek olay sinyalleri (True/False): olay olan hisselerin ortalama fazla getirisi."""
    horizons = horizons or panel.HORIZONS
    flag = flag.reindex(index=price.index, columns=price.columns).fillna(False).astype(bool)
    res = Result(name, coverage=float(flag.sum(axis=1).mean()))
    for label, weeks in horizons.items():
        ex = excess_returns(price, sec, weeks, universe)
        f = flag.reindex(ex.index).fillna(False) & ex.notna()
        exw = _winsor(ex)
        vals = exw.where(f)
        per_date = vals.mean(axis=1).dropna()
        step = per_date.iloc[::max(weeks, 1)]
        t = tstat(step)
        events = vals.stack().dropna()
        res.rows.append({
            "vade": label, "olay": int(f.sum().sum()), "olaylı_hafta": len(per_date),
            "ort_fazla": round(float(events.mean()), 4), "medyan_fazla": round(float(events.median()), 4),
            "t": round(float(t), 2), "isabet": round(float((events > 0).mean()), 3),
        })
        res.yearly[label] = {int(y): round(float(v), 3) for y, v in per_date.groupby(per_date.index.year).mean().items()}
    return res


def markdown(results: list[Result]) -> str:
    out = []
    for r in results:
        out += [f"### {r.name}", "", f"Kapsam: haftada ortalama {r.coverage:,.0f} hisse", "",
                r.table().to_markdown(), "", "Yıllara göre (3 aylık vade): " + str(r.yearly.get("3a", {})), ""]
    return "\n".join(out)

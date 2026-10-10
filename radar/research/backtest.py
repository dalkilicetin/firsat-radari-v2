"""Ölçüm düzeneği: portföy simülasyonu (maliyet sonrası), puan dilimi kalibrasyonu, büyük kazanan oranı.

Kurallar (reports/research/firsat_on_kayit.md):
- Eşit ağırlık, REBALANCE haftada bir yeniden dengeleme; dönem getirisi panel.forward_returns ile (arada borsadan
  çıkan hisse çıkış değeriyle, iflasta 0). Getirisi bilinmeyen (fiyatı kesilen, çıkışı kayıtlı olmayan) hisse o
  dönemin ortalamasına girmez.
- Maliyet tek yön, ağırlık değişimi × hissenin likidite dilimine göre oran. Kıyas portföyü maliyetsizdir
  (portföy aleyhine, temkinli).
- Güven aralıkları: 52 haftalık bloklarla bootstrap (getiriler yıllar içinde ilişkili olduğu için).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from radar.research import evaluate as ev
from radar.research import panel

REBALANCE = 4
COSTS = [(50e6, 0.0005), (10e6, 0.0015), (1e6, 0.004)]  # (en az günlük işlem $, tek yön oran); altı: UNKNOWN_COST
UNKNOWN_COST = 0.01
PERIODS_PER_YEAR = 52 / REBALANCE


def cost_rate(dv: pd.Series) -> pd.Series:
    out = pd.Series(UNKNOWN_COST, index=dv.index)
    for floor, rate in reversed(COSTS):
        out[dv >= floor] = rate
    return out


def dev_dates(dates: pd.DatetimeIndex, weeks: int) -> pd.DatetimeIndex:
    """Geliştirme dönemi: tahmin tarihi + vade < HOLDOUT_START."""
    return dates[dates + pd.Timedelta(weeks=weeks) < ev.HOLDOUT_START]


@dataclass
class Sim:
    returns: pd.DataFrame   # dönem × [portfoy, kiyas, maliyet, devir, n]
    metrics: dict
    yearly: pd.DataFrame


def select(score_row: pd.Series, how: str | int) -> pd.Index:
    s = score_row.dropna()
    if isinstance(how, int):
        return s.nlargest(how).index
    q = float(how)  # ör. 0.9 → ilk %10
    return s[s.rank(pct=True) > q].index


def simulate(score: pd.DataFrame, p: dict, universe: pd.DataFrame, how: str | int = "0.9",
             rebalance: int = REBALANCE, dates: pd.DatetimeIndex | None = None) -> Sim:
    price, sec, dv = p["price"], p["securities"], p["dollar_volume"]
    fwd = panel.forward_returns(price, sec, rebalance).reindex(price.index)
    dates = dates if dates is not None else dev_dates(price.index, rebalance)
    dates = dates[::rebalance]
    rows, prev = [], pd.Series(dtype=float)
    for d in dates:
        u = universe.loc[d]
        sc = score.loc[d].where(u)
        r = fwd.loc[d]
        bench = r[u & r.notna()]
        picks = select(sc, how)
        picks = picks[r[picks].notna()]
        if len(picks) == 0 or len(bench) < 50:
            continue
        w_new = pd.Series(1 / len(picks), index=picks)
        allc = w_new.index.union(prev.index)
        dw = (w_new.reindex(allc, fill_value=0) - prev.reindex(allc, fill_value=0)).abs()
        cost = float((dw * cost_rate(dv.loc[d].reindex(allc))).sum())
        gross = float((w_new * r[picks]).sum())
        net = gross - cost
        # Dönem sonu ağırlıkları (fiyat hareketiyle kayar); bir sonraki dengelemenin devri buna göre.
        grown = w_new * (1 + r[picks])
        prev = grown / grown.sum() if grown.sum() > 0 else pd.Series(dtype=float)
        rows.append({"tarih": d, "portfoy": net, "brut": gross, "kiyas": float(bench.mean()), "maliyet": cost,
                     "devir": float(dw.sum()) / 2, "n": len(picks)})
    df = pd.DataFrame(rows).set_index("tarih")
    return Sim(df, metrics(df), yearly(df))


def _ann(r: pd.Series) -> float:
    return float((1 + r).prod() ** (PERIODS_PER_YEAR / len(r)) - 1) if len(r) else np.nan


def max_drawdown(r: pd.Series) -> float:
    curve = (1 + r).cumprod()
    return float((curve / curve.cummax() - 1).min())


def block_bootstrap(x: np.ndarray, stat, block: int, n: int = 2000, seed: int = 0) -> tuple[float, float]:
    """%90 güven aralığı (5. ve 95. yüzdelik)."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    nb = max(1, int(np.ceil(len(x) / block)))
    starts = np.arange(0, max(1, len(x) - block + 1))
    vals = []
    for _ in range(n):
        idx = np.concatenate([np.arange(s, min(s + block, len(x))) for s in rng.choice(starts, nb)])[: len(x)]
        vals.append(stat(x[idx]))
    return float(np.nanpercentile(vals, 5)), float(np.nanpercentile(vals, 95))


def metrics(df: pd.DataFrame) -> dict:
    r, b = df.portfoy, df.kiyas
    ex = r - b
    down = r[r < 0]
    block = int(round(PERIODS_PER_YEAR))
    ann_ex = lambda x: float(np.mean(x) * PERIODS_PER_YEAR)
    lo, hi = block_bootstrap(ex.to_numpy(), ann_ex, block)
    return {
        "yillik_getiri": _ann(r), "kiyas_yillik": _ann(b), "yillik_fazla_ort": ann_ex(ex),
        "fazla_ga_alt": lo, "fazla_ga_ust": hi,
        "oynaklik": float(r.std() * np.sqrt(PERIODS_PER_YEAR)),
        "sharpe": float(r.mean() / r.std() * np.sqrt(PERIODS_PER_YEAR)) if r.std() > 0 else np.nan,
        "sortino": float(r.mean() / down.std() * np.sqrt(PERIODS_PER_YEAR)) if len(down) > 1 else np.nan,
        "kiyas_sharpe": float(b.mean() / b.std() * np.sqrt(PERIODS_PER_YEAR)),
        "en_buyuk_dusus": max_drawdown(r), "kiyas_en_buyuk_dusus": max_drawdown(b),
        "yillik_maliyet": float(df.maliyet.mean() * PERIODS_PER_YEAR), "devir_donem": float(df.devir.mean()),
        "donem": len(df), "ort_hisse": float(df.n.mean()),
    }


def yearly(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(df.index.year)
    return pd.DataFrame({"portfoy": g.portfoy.apply(lambda r: (1 + r).prod() - 1),
                         "kiyas": g.kiyas.apply(lambda r: (1 + r).prod() - 1)}).assign(fark=lambda d: d.portfoy - d.kiyas)


def calibration(score: pd.DataFrame, p: dict, universe: pd.DataFrame, weeks: int,
                dates: pd.DatetimeIndex | None = None, edges=tuple(range(0, 101, 10))) -> pd.DataFrame:
    """Puan dilimi → gerçekleşen fazla getiri (aynı evrenin medyanına göre, %1/%99 kırpılmış), medyanı geçme oranı.
    Haftalık dilim değerleri 52 haftalık bloklarla bootstrap edilir (%90 GA)."""
    fwd = panel.forward_returns(p["price"], p["securities"], weeks).reindex(p["price"].index).where(universe)
    dates = dates if dates is not None else dev_dates(p["price"].index, weeks)
    pct = score.where(universe).rank(axis=1, pct=True) * 100
    weekly = {}
    for d in dates:
        r = fwd.loc[d]
        ok = r.notna() & pct.loc[d].notna()
        if ok.sum() < 50:
            continue
        ex = (r[ok] - r[ok].median()).clip(*r[ok].sub(r[ok].median()).quantile([0.01, 0.99]))
        b = pd.cut(pct.loc[d][ok], list(edges), include_lowest=True, right=True)
        weekly[d] = ex.groupby(b, observed=False).agg(["mean", lambda x: (x > 0).mean()]).set_axis(["ort", "isabet"], axis=1)
    rows = []
    for k in weekly[next(iter(weekly))].index:
        s = pd.DataFrame({d: w.loc[k] for d, w in weekly.items()}).T.dropna()
        if s.empty:
            continue
        lo, hi = block_bootstrap(s.ort.to_numpy(), np.mean, 52)
        rows.append({"dilim": f"{max(0, round(k.left))}–{round(k.right)}", "ort_fazla": s.ort.mean(),
                     "ga_alt": lo, "ga_ust": hi, "isabet": s.isabet.mean(), "hafta": len(s)})
    return pd.DataFrame(rows)


def winner_lift(score: pd.DataFrame, target: pd.DataFrame, universe: pd.DataFrame, dates: pd.DatetimeIndex,
                top: float = 0.9) -> dict:
    """İlk %10'daki büyük kazanan oranı / evrendeki genel oran; yıllara göre bootstrap %90 GA."""
    sc = score.where(universe)
    rows = []
    for d in dates:
        y = target.loc[d]
        s = sc.loc[d]
        ok = y.notna() & s.notna()
        if ok.sum() < 50:
            continue
        q = s[ok].rank(pct=True) > top
        rows.append({"yil": d.year, "ust_n": int(q.sum()), "ust_k": float(y[ok][q].sum()),
                     "tum_n": int(ok.sum()), "tum_k": float(y[ok].sum())})
    df = pd.DataFrame(rows)
    lift = lambda g: (g.ust_k.sum() / g.ust_n.sum()) / (g.tum_k.sum() / g.tum_n.sum())
    years = df.yil.unique()
    rng = np.random.default_rng(0)
    boots = []
    by_year = {y: df[df.yil == y] for y in years}
    for _ in range(2000):
        pick = rng.choice(years, len(years))
        boots.append(lift(pd.concat([by_year[y] for y in pick])))
    return {"ust_oran": df.ust_k.sum() / df.ust_n.sum(), "genel_oran": df.tum_k.sum() / df.tum_n.sum(),
            "kat": lift(df), "ga_alt": float(np.percentile(boots, 5)), "ga_ust": float(np.percentile(boots, 95)),
            "yillik": df.groupby("yil").apply(lift).rename("kat")}

"""Kayan pencere (walk-forward) modeli: her yol için ve toplam için, her vadede ayrı.

- Girdiler: her sinyal her hafta evren içinde yüzdelik sıraya çevrilir ve ortalanır (−0,5…+0,5); eksik = 0
  (nötr: eksik veri puanı düşürmez). Olaylar: 1/0 − o haftanın ortalaması.
- Hedef: h haftalık ileri getirinin evren içindeki ortalanmış yüzdelik sırası (uç değerlere dayanıklı).
- Eğitim: t haftasında yalnızca getirisi t'ye kadar GERÇEKLEŞMİŞ haftalar (s + h ≤ t) kullanılır.
  Model her REFIT haftada bir yeniden kurulur; ridge cezası sabittir (son dönemde ayarlanmaz).
- Tahmin: t haftasının girdileri × o ana kadar öğrenilen ağırlıklar → puan; 0–100 = haftalık yüzdelik.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from radar.research import panel

REFIT_WEEKS = 4
MIN_TRAIN_WEEKS = 52
RIDGE = 0.05  # göreli ceza (özellik varyansının oranı); sabit, ayarlanmadı


def ranked_inputs(sigs: dict[str, tuple[str, pd.DataFrame]], universe: pd.DataFrame) -> dict[str, np.ndarray]:
    out = {}
    u = universe.to_numpy()
    for name, (_, df) in sigs.items():
        x = df.where(universe)
        vals = x.to_numpy(dtype=float)
        finite = np.isfinite(vals)
        is_event = np.nanmax(np.where(finite, np.abs(vals - np.round(vals)), 0)) == 0 and np.nanmax(np.where(finite, vals, 0)) <= 1
        if is_event:
            v = np.where(finite, vals, 0.0)
            mean = np.where(u, v, np.nan)
            mean = np.nanmean(mean, axis=1, keepdims=True)
            z = np.where(u, v - np.nan_to_num(mean), 0.0)
        else:
            z = x.rank(axis=1, pct=True).to_numpy() - 0.5
            z = np.where(np.isfinite(z), z, 0.0)
        out[name] = z.astype(np.float32)
    return out


def ranked_target(price: pd.DataFrame, sec: pd.DataFrame, weeks: int, universe: pd.DataFrame) -> np.ndarray:
    r = panel.forward_returns(price, sec, weeks).reindex(price.index).where(universe)
    return (r.rank(axis=1, pct=True) - 0.5).to_numpy(dtype=np.float32)


@dataclass
class Fit:
    pred: np.ndarray          # T × N tahmin (NaN = tahmin yok)
    weights: pd.DataFrame     # yeniden kurulum haftası × özellik
    features: list[str]


def walk_forward(X: dict[str, np.ndarray], y: np.ndarray, weeks: int, dates: pd.DatetimeIndex,
                 features: list[str], universe: np.ndarray) -> Fit:
    T, N = y.shape
    k = len(features) + 1  # + sabit
    xtx = np.zeros((k, k))
    xty = np.zeros(k)
    beta = None
    pred = np.full((T, N), np.nan, dtype=np.float32)
    weights, n_weeks_in = {}, 0
    for t in range(T):
        s = t - weeks  # getirisi t'de gerçekleşen en son hafta
        if s >= 0:
            mask = np.isfinite(y[s]) & universe[s]
            if mask.any():
                Xs = np.column_stack([np.ones(mask.sum())] + [X[f][s][mask] for f in features])
                xtx += Xs.T @ Xs
                xty += Xs.T @ y[s][mask]
                n_weeks_in += 1
        if n_weeks_in >= MIN_TRAIN_WEEKS and (beta is None or t % REFIT_WEEKS == 0):
            pen = RIDGE * np.mean(np.diag(xtx)[1:]) if k > 1 else 0.0
            reg = np.eye(k) * pen
            reg[0, 0] = 0.0
            beta = np.linalg.solve(xtx + reg, xty)
            weights[dates[t]] = beta[1:]
        if beta is not None:
            Xt = np.column_stack([X[f][t] for f in features]) if features else np.zeros((N, 0))
            p = Xt @ beta[1:] + beta[0]
            pred[t] = np.where(universe[t], p, np.nan)
    return Fit(pred, pd.DataFrame(weights, index=features).T, features)


def to_score(pred: np.ndarray, dates, columns) -> pd.DataFrame:
    """0–100: haftalık yüzdelik."""
    return pd.DataFrame(pred, index=dates, columns=columns).rank(axis=1, pct=True) * 100


def run(p: dict, sigs: dict[str, tuple[str, pd.DataFrame]], horizons: dict[str, int] | None = None,
        universe: pd.DataFrame | None = None) -> dict[tuple[str, str], Fit]:
    """(model adı, vade) → Fit. Modeller: her yol ayrı + 'toplam'."""
    horizons = horizons or panel.HORIZONS
    price, sec = p["price"], p["securities"]
    if universe is None:
        universe = panel.membership(sec, price.index, price.columns) & price.notna()
    X = ranked_inputs(sigs, universe)
    roads = sorted({r for r, _ in sigs.values()})
    groups = {road: [n for n, (r, _) in sigs.items() if r == road] for road in roads} | {"toplam": list(sigs)}
    fits = {}
    u = universe.to_numpy()
    for label, weeks in horizons.items():
        y = ranked_target(price, sec, weeks, universe)
        for g, feats in groups.items():
            fits[(g, label)] = walk_forward(X, y, weeks, price.index, feats, u)
    return fits


def horizon_choice(fits: dict, dates, columns, threshold: float = 70.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Toplam modelin vade bazındaki puanlarından: en yüksek puan ve o vade (eşik altı = potansiyel yok)."""
    labels = [h for (g, h) in fits if g == "toplam"]
    scores = np.stack([to_score(fits[("toplam", h)].pred, dates, columns).to_numpy() for h in labels])
    filled = np.where(np.isfinite(scores), scores, -1)
    best = filled.argmax(axis=0)
    top = filled.max(axis=0)
    horizon = pd.DataFrame(np.array(labels, dtype=object)[best], index=dates, columns=columns)
    potential = pd.DataFrame(np.where(top >= 0, top, np.nan), index=dates, columns=columns)
    horizon = horizon.where(potential >= threshold)
    return potential, horizon

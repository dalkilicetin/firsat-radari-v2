"""Yıl başı testi: model her yılın ilk Cuma'sında, yalnızca o güne kadar bilinen verilerle eğitilip çalıştırılır;
seçtiği hisselerin o yılki (52 haftalık) sonucu ölçülür.

Kurallar:
- Eğitim satırları: hedefi tahmin tarihinden ÖNCE gerçekleşmiş haftalar (s + 52 hafta ≤ t). Girdiler her hafta
  kesitsel sıraya çevrilir (o haftanın bilgisiyle). Böylece 2015 başındaki model 2015'i hiç görmez.
- Ölçüm: yatırılabilir faaliyet şirketleri (≥ 5 $, ≥ 1 mn $/gün), 52 haftalık getiri, arada borsadan çıkan hisseye
  çıkış değeri (iflasta 0). Alım + satım maliyeti likiditeye göre düşülür.
- Kilitli yıllar (LOCKED): iyileştirme turlarında sonuçlarına bakılmaz; en sonda bir kez açılır.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from radar import config
from radar.research import backtest as bt
from radar.research import model, panel

LOCKED = (2023, 2024, 2025)
HORIZON = 52
STEP = 4  # eğitim satırları 4 haftada bir (ardışık haftalar neredeyse aynı bilgiyi taşır)
LOG = config.ROOT / "reports" / "research" / "yillik_denemeler.jsonl"


@dataclass
class Recipe:
    name: str
    target: str = "sira"              # sira | fazla | ust10 | kazanan100
    learner: str = "ridge"            # ridge | lgbm
    features: list[str] | None = None  # None = tümü
    exclude: set[str] = field(default_factory=set)
    params: dict = field(default_factory=dict)
    note: str = ""


def year_starts(dates: pd.DatetimeIndex, years) -> dict[int, int]:
    """yıl → o yılın ilk Cuma'sının panel sırası."""
    out = {}
    for y in years:
        idx = np.flatnonzero(dates >= pd.Timestamp(f"{y}-01-01"))
        if len(idx):
            out[y] = int(idx[0])
    return out


def targets(fwd: pd.DataFrame, universe: pd.DataFrame) -> dict[str, np.ndarray]:
    r = fwd.where(universe)
    rank = r.rank(axis=1, pct=True)
    lo, hi = r.quantile(0.01, axis=1), r.quantile(0.99, axis=1)
    w = r.clip(lo, hi, axis=0)
    z = w.sub(w.mean(axis=1), axis=0).div(w.std(axis=1).replace(0, np.nan), axis=0)
    return {"sira": (rank - 0.5).to_numpy(np.float32), "fazla": z.to_numpy(np.float32),
            "ust10": (rank >= 0.9).astype(np.float32).where(r.notna()).to_numpy(np.float32),
            "kazanan100": (r >= 1.0).astype(np.float32).where(r.notna()).to_numpy(np.float32)}


class Data:
    """Bir kez hazırlanır: girdiler (T × N sıra), hedefler, ileri getiriler, evrenler."""

    def __init__(self, p: dict, sigs: dict, train_universe: pd.DataFrame, eval_universe: pd.DataFrame):
        self.p, self.sigs = p, sigs
        self.dates, self.cols = p["price"].index, p["price"].columns
        self.train_u = train_universe.to_numpy()
        self.eval_u = eval_universe
        self.X = model.ranked_inputs(sigs, train_universe)
        self.fwd = panel.forward_returns(p["price"], p["securities"], HORIZON).reindex(self.dates)
        self.Y = targets(self.fwd, train_universe)

    def rows(self, t_idx: list[int], feats: list[str], target: str | None = None):
        Xs, ys = [], []
        for t in t_idx:
            m = self.train_u[t]
            if target is not None:
                m = m & np.isfinite(self.Y[target][t])
            Xs.append(np.column_stack([self.X[f][t][m] for f in feats]))
            if target is not None:
                ys.append(self.Y[target][t][m])
        X = np.vstack(Xs) if Xs else np.zeros((0, len(feats)))
        return (X, np.concatenate(ys)) if target is not None else X


def fit_predict(rec: Recipe, data: Data, t: int, feats: list[str]) -> pd.Series:
    """t haftasında: yalnızca s + HORIZON ≤ t olan haftalarla eğit, t'deki evreni puanla."""
    train_t = [s for s in range(0, t - HORIZON + 1, STEP)]
    train_t = [s for s in train_t if s + HORIZON <= t]
    X, y = data.rows(train_t, feats, rec.target)
    m = data.train_u[t]
    Xt = np.column_stack([data.X[f][t][m] for f in feats])
    if len(y) < 1000:
        return pd.Series(dtype=float)
    if rec.learner == "ridge":
        Xa = np.column_stack([np.ones(len(X)), X])
        xtx = Xa.T @ Xa
        pen = rec.params.get("ridge", model.RIDGE) * np.mean(np.diag(xtx)[1:])
        reg = np.eye(xtx.shape[0]) * pen
        reg[0, 0] = 0
        beta = np.linalg.solve(xtx + reg, Xa.T @ y)
        pred = Xt @ beta[1:] + beta[0]
    elif rec.learner == "lgbm":
        import lightgbm as lgb
        prm = {"n_estimators": 300, "learning_rate": 0.05, "num_leaves": 15, "min_child_samples": 300,
               "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "reg_lambda": 1.0,
               "random_state": 0, "verbose": -1, "n_jobs": 4} | rec.params
        binary = rec.target in ("ust10", "kazanan100")
        mdl = (lgb.LGBMClassifier if binary else lgb.LGBMRegressor)(**prm)
        mdl.fit(X, y)
        pred = mdl.predict_proba(Xt)[:, 1] if binary else mdl.predict(Xt)
    else:
        raise ValueError(rec.learner)
    return pd.Series(pred, index=data.cols[m])


def evaluate_year(score: pd.Series, data: Data, t: int) -> dict:
    u = data.eval_u.iloc[t]
    r = data.fwd.iloc[t][u].dropna()
    s = score.reindex(r.index).dropna()
    r = r[s.index]
    if len(r) < 100:
        return {}
    dv = data.p["dollar_volume"].iloc[t].reindex(r.index)
    cost = 2 * bt.cost_rate(dv)  # alım + satım
    top_dec = r >= r.quantile(0.9)
    out = {"tarih": str(data.dates[t].date()), "evren": len(r), "evren_ort": r.mean(), "evren_medyan": r.median(),
           "evren_yukselen": (r > 0).mean()}
    for label, picks in (("ilk20", s.nlargest(20).index), ("ilk10y", s[s.rank(pct=True) > 0.9].index)):
        net = r[picks] - cost[picks]
        out |= {f"{label}_ort": net.mean(), f"{label}_medyan": net.median(), f"{label}_yukselen": (net > 0).mean(),
                f"{label}_medyani_gecen": (r[picks] > r.median()).mean(),
                f"{label}_yilin_en_iyi10": top_dec[picks].mean(), f"{label}_fazla": net.mean() - r.mean(),
                f"{label}_hisseler": ",".join(data.p["securities"].assign(cik=lambda d: d.cik.astype(str))
                                              .drop_duplicates("cik").set_index("cik").symbol.reindex(picks[:20]).fillna("?"))
                if label == "ilk20" else ""}
    return out


def run(rec: Recipe, data: Data, years, reveal_locked: bool = False) -> pd.DataFrame:
    feats = [f for f in (rec.features or list(data.X)) if f not in rec.exclude]
    rows = []
    for y, t in year_starts(data.dates, years).items():
        if (y in LOCKED and not reveal_locked) or t + HORIZON >= len(data.dates):
            continue
        score = fit_predict(rec, data, t, feats)
        if score.empty:
            continue
        res = evaluate_year(score, data, t)
        if res:
            rows.append({"yil": y} | res)
    return pd.DataFrame(rows).set_index("yil") if rows else pd.DataFrame()


def summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    return {"yil": len(df), "ilk20_fazla_ort": df.ilk20_fazla.mean(), "ilk20_fazla_pozitif_yil": int((df.ilk20_fazla > 0).sum()),
            "ilk20_yukselen": df.ilk20_yukselen.mean(), "ilk20_medyani_gecen": df.ilk20_medyani_gecen.mean(),
            "ilk20_yilin_en_iyi10": df.ilk20_yilin_en_iyi10.mean(),
            "ilk10y_fazla_ort": df.ilk10y_fazla.mean(), "ilk10y_fazla_pozitif_yil": int((df.ilk10y_fazla > 0).sum()),
            "ilk10y_yukselen": df.ilk10y_yukselen.mean(), "evren_yukselen": df.evren_yukselen.mean(),
            "en_kotu_yil_ilk20_fazla": df.ilk20_fazla.min()}


def log_trial(rec: Recipe, df: pd.DataFrame, extra: dict | None = None) -> dict:
    s = summary(df)
    entry = {"zaman": time.strftime("%Y-%m-%d %H:%M"), "deneme": rec.name, "hedef": rec.target, "ogrenici": rec.learner,
             "ozellik_sayisi": len(rec.features) if rec.features else "tümü", "haric": sorted(rec.exclude),
             "parametre": rec.params, "not": rec.note, "yillar": list(map(int, df.index)) if len(df) else []} | \
            {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()} | (extra or {})
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

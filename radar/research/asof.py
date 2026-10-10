""""O gün çalıştırsaydık" testi: herhangi bir tarihte model yalnızca o güne kadar bilinen verilerle eğitilir,
seçtiği hisseler alınır ve 1 hafta / 1 ay / 3 ay / 6 ay / 1 yıl sonra sonuç ölçülür.

Cevaplanan sorular (her başlangıç tarihi ve vade için):
- 10.000 $ ile modelin ilk 20 hissesi alınsaydı (eşit ağırlık, alım + satım maliyeti düşülerek) kaç $ olurdu?
- Aynı parayla tüm evren (eşit ağırlık) alınsaydı?
- Sonradan bakınca o dönemin en iyi 20 hissesi ne getirdi; modelin seçimi bunun ne kadarını yakaladı?
- Seçilen hisselerin kaçı yükseldi, kaçı evrenin medyanını geçti, kaçı dönemin en iyi %10'undaydı?
- 6 ay ve 1 yıl vadede yol boyunca portföyün en büyük düşüşü.

Ön tanımlı kurallar:
- Eğitim: hedefi t'den önce gerçekleşmiş haftalar (s + h ≤ t), STEP haftada bir örneklenir. Model REFIT haftada bir
  yeniden kurulur; aradaki haftalar son kurulan modelle puanlanır (yalnızca geçmiş bilgi).
- Ölçüm evreni: yatırılabilir faaliyet şirketleri. Getiri: çıkışta çıkış değeri, iflasta 0.
- Kilitli dönem: tutma süresi 2023-01-01'e taşan başlangıçlar iyileştirme turlarında ölçülmez (LOCK_FROM).
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

HORIZONS = dict(panel.HORIZONS)  # 1h 1a 3a 6a 1y
LOCK_FROM = pd.Timestamp("2023-01-01")
# Tüm denemeler aynı başlangıç tarihlerinde ölçülür (2009 verisi + en az 1 yıllık gerçekleşmiş hedef).
EVAL_FROM = pd.Timestamp("2011-01-01")
STEP = 4
PICKS = 20
CAPITAL = 10_000
LOG = config.ROOT / "reports" / "research" / "asof_denemeler.jsonl"


@dataclass
class Recipe:
    name: str
    target: str = "sira"               # sira | fazla | ust10 | kazanan
    learner: str = "ridge"             # ridge | lgbm
    features: list[str] | None = None
    exclude: set[str] = field(default_factory=set)
    regime: bool = False               # dönem özellikleri (yalnızca ağaç modelleri)
    params: dict = field(default_factory=dict)
    refit: int = 4                     # hafta
    note: str = ""


def make_targets(fwd: pd.DataFrame, universe: pd.DataFrame, weeks: int) -> dict[str, np.ndarray]:
    r = fwd.where(universe)
    rank = r.rank(axis=1, pct=True)
    w = r.clip(r.quantile(0.01, axis=1), r.quantile(0.99, axis=1), axis=0)
    z = w.sub(w.mean(axis=1), axis=0).div(w.std(axis=1).replace(0, np.nan), axis=0)
    big = {1: 0.10, 4: 0.25, 13: 0.5, 26: 0.75, 52: 1.0}[weeks]  # vadeye göre "büyük yükseliş" eşiği
    as_f = lambda df: df.to_numpy(np.float32)
    return {"sira": as_f(rank - 0.5), "fazla": as_f(z),
            "ust10": as_f((rank >= 0.9).astype(np.float32).where(r.notna())),
            "kazanan": as_f((r >= big).astype(np.float32).where(r.notna()))}


class Data:
    def __init__(self, p: dict, sigs: dict, train_universe: pd.DataFrame, eval_universe: pd.DataFrame):
        self.p, self.sigs = p, sigs
        self.dates, self.cols = p["price"].index, p["price"].columns
        self.train_u = train_universe.to_numpy()
        self.eval_u = eval_universe.to_numpy()
        self.X = model.ranked_inputs(sigs, train_universe)
        from radar.research import context
        reg = context.regime(self.dates)
        self.R = {f"donem_{c}": np.broadcast_to(reg[c].to_numpy(np.float32)[:, None], (len(self.dates), len(self.cols)))
                  for c in reg.columns}
        self.fwd = {h: panel.forward_returns(p["price"], p["securities"], w).reindex(self.dates) for h, w in HORIZONS.items()}
        self.Y = {h: make_targets(self.fwd[h], train_universe, w) for h, w in HORIZONS.items()}
        self.path = {k: panel.forward_returns(p["price"], p["securities"], k).reindex(self.dates).to_numpy(np.float32)
                     for k in range(4, 53, 4)}
        self.cost = 2 * np.vstack([bt.cost_rate(p["dollar_volume"].iloc[t]).to_numpy() for t in range(len(self.dates))])
        sec = p["securities"].assign(cik=lambda d: d.cik.astype(str)).drop_duplicates("cik").set_index("cik")
        self.symbols = sec.symbol.reindex(self.cols).fillna("?").to_numpy()

    def col(self, f: str) -> np.ndarray:
        """Sıralanmış hisse sinyali ya da (ağaç modelleri için) ham dönem özelliği."""
        return self.X[f] if f in self.X else self.R[f]


def _fit(rec: Recipe, X: np.ndarray, y: np.ndarray):
    if rec.learner == "ridge":
        Xa = np.column_stack([np.ones(len(X)), X])
        xtx = Xa.T @ Xa
        reg = np.eye(xtx.shape[0]) * rec.params.get("ridge", model.RIDGE) * np.mean(np.diag(xtx)[1:])
        reg[0, 0] = 0
        beta = np.linalg.solve(xtx + reg, Xa.T @ y)
        return lambda Z: Z @ beta[1:] + beta[0]
    if rec.learner == "lgbm":
        import lightgbm as lgb
        prm = {"n_estimators": 200, "learning_rate": 0.05, "num_leaves": 15, "min_child_samples": 300,
               "subsample": 0.8, "subsample_freq": 1, "colsample_bytree": 0.8, "reg_lambda": 1.0,
               "random_state": 0, "verbose": -1, "n_jobs": 4} | rec.params
        binary = rec.target in ("ust10", "kazanan")
        mdl = (lgb.LGBMClassifier if binary else lgb.LGBMRegressor)(**prm).fit(X, y)
        return (lambda Z: mdl.predict_proba(Z)[:, 1]) if binary else mdl.predict
    raise ValueError(rec.learner)


def predict(rec: Recipe, data: Data, h: str, t_range) -> np.ndarray:
    """Her t için (t_range) yalnızca geçmişle kurulan modelin puanları; T × N, puanlanmayan NaN."""
    w = HORIZONS[h]
    feats = [f for f in (rec.features or list(data.X)) if f not in rec.exclude]
    if rec.regime:
        assert rec.learner == "lgbm", "dönem özellikleri sıralanmaz; yalnızca ağaç modelinde anlamlı"
        feats = feats + list(data.R)
    Y = data.Y[h][rec.target]
    if rec.learner == "ridge" and not rec.params and not rec.regime:  # artımlı kayan pencere (model.walk_forward, 4 haftada bir kurulum)
        return model.walk_forward(data.X, Y, w, data.dates, feats, data.train_u).pred
    T, N = Y.shape
    out = np.full((T, N), np.nan, dtype=np.float32)
    fn, last_fit = None, -10**9
    for t in t_range:
        if fn is None or t - last_fit >= rec.refit:
            rows = [s for s in range(t - w, -1, -STEP)]  # en yeni gerçekleşmiş haftadan geriye
            Xs, ys = [], []
            for s in rows:
                m = data.train_u[s] & np.isfinite(Y[s])
                if m.any():
                    Xs.append(np.column_stack([data.col(f)[s][m] for f in feats]))
                    ys.append(Y[s][m])
            if sum(len(y) for y in ys) >= 2000:
                fn, last_fit = _fit(rec, np.vstack(Xs), np.concatenate(ys)), t
        if fn is None:
            continue
        m = data.train_u[t]
        out[t, m] = fn(np.column_stack([data.col(f)[t][m] for f in feats]))
    return out


def outcome(data: Data, score_row: np.ndarray, t: int, h: str) -> dict | None:
    """t'de ilk PICKS hisse alınsaydı h sonra ne olurdu."""
    w = HORIZONS[h]
    r = data.fwd[h].iloc[t].to_numpy()
    ok = data.eval_u[t] & np.isfinite(r) & np.isfinite(score_row)
    if ok.sum() < 100:
        return None
    idx = np.flatnonzero(ok)
    order = idx[np.argsort(-score_row[idx])]
    picks = order[:PICKS]
    best = idx[np.argsort(-r[idx])][:PICKS]
    net = r[picks] - data.cost[t, picks]
    top10 = r[idx] >= np.quantile(r[idx], 0.9)
    in_top10 = np.isin(picks, idx[top10])
    res = {"tarih": data.dates[t], "vade": h, "evren": len(idx),
           "portfoy": float(net.mean()), "evren_ort": float(r[idx].mean()), "en_iyi20": float(r[best].mean()),
           "yukselen": float((net > 0).mean()), "medyani_gecen": float((r[picks] > np.median(r[idx])).mean()),
           "en_iyi10_icinde": float(in_top10.mean()), "secim": ",".join(data.symbols[picks]),
           "secim_getiri": ",".join(f"{x:.3f}" for x in r[picks])}
    if w >= 26:  # yol boyunca en büyük düşüş (4 haftalık adımlarla)
        vals = [1.0] + [float(np.nanmean(1 + data.path[k][t, picks])) for k in range(4, w + 1, 4)]
        curve = np.array(vals)
        res["yol_en_buyuk_dusus"] = float((curve / np.maximum.accumulate(curve) - 1).min())
    return res


def evaluate(rec: Recipe, data: Data, horizons=None, start_every: int = 4, locked: bool = False) -> pd.DataFrame:
    rows = []
    T = len(data.dates)
    for h in horizons or HORIZONS:
        w = HORIZONS[h]
        sc = predict(rec, data, h, range(T))
        for t in range(0, T - w, start_every):
            if data.dates[t] < EVAL_FROM:
                continue
            end = data.dates[t] + pd.Timedelta(weeks=w)
            if not locked and end >= LOCK_FROM:
                continue
            res = outcome(data, sc[t], t, h)
            if res:
                rows.append(res)
    return pd.DataFrame(rows)


def summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    g = df.assign(kar=df.portfoy > 0, piyasayi_gecti=df.portfoy > df.evren_ort,
                  yakalama=df.portfoy / df.en_iyi20, fazla=df.portfoy - df.evren_ort).groupby("vade", sort=False)
    out = pd.DataFrame({
        "baslangic": g.size(), "karda_bitme": g.kar.mean(), "piyasayi_gecme": g.piyasayi_gecti.mean(),
        "ort_getiri": g.portfoy.mean(), "medyan_getiri": g.portfoy.median(), "evren_ort": g.evren_ort.mean(),
        "ort_fazla": g.fazla.mean(), "en_iyi20_ort": g.en_iyi20.mean(), "yakalama": g.portfoy.mean() / g.en_iyi20.mean(),
        "hisse_yukselen": g.yukselen.mean(), "hisse_medyani_gecen": g.medyani_gecen.mean(),
        "hisse_en_iyi10": g.en_iyi10_icinde.mean(), "en_kotu": g.portfoy.min(), "en_iyi": g.portfoy.max()})
    if "yol_en_buyuk_dusus" in df:
        out["yol_dusus_medyan"] = g.yol_en_buyuk_dusus.median()
    return out


def log_trial(rec: Recipe, summ: pd.DataFrame, extra: dict | None = None) -> dict:
    entry = {"zaman": time.strftime("%Y-%m-%d %H:%M"), "deneme": rec.name, "hedef": rec.target, "ogrenici": rec.learner,
             "haric": sorted(rec.exclude), "ozellik": rec.features or "tümü", "parametre": rec.params, "refit": rec.refit,
             "not": rec.note, "sonuc": json.loads(summ.round(4).to_json(orient="index", force_ascii=False))} | (extra or {})
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

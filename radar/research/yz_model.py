"""Yürüyen model düzeneği — Aşama 1–2: her test yılı için yalnızca geçmişle eğit, o yılın çeyrek başlarında tahmin et.

Eğitim satırları: tarih + hedef süresi (13 ya da 26 hafta) < test yılının ilk Cuması (boşluk/embargo: etiketi test yılı
başlamadan kapanmamış hiçbir satır eğitime girmez). Ayarlar SABİT (aşağıda); test sonuçlarına göre ayar araması yapılmaz.
Tahminler: test yılındaki Ocak/Nisan/Temmuz/Ekim'in ilk Cuması, bütün evren için puan.
Test yılları: 2013–2024 geliştirme; 2025–2026 KİLİTLİ (tahmin üretilir, sonuçlar seçim yapılıp ön kayda yazılana kadar
değerlendirilmez — yz_degerlendir.py kilidi uygular).

python -m radar.research.yz_model <model> → data/derived/yz_tahmin/<model>.parquet
Modeller: rastgele, momentum_buyuk, kural_ogrenici, lgb_sinif5, lgb_sinif1, lgb_sirala, lgb_sirala_6a, iki_asama, kuyruk_q90
"""

from __future__ import annotations

import itertools
import sys
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research.yz_veri import OUT as VERI, features

TAHMIN = config.DATA_DIR / "derived" / "yz_tahmin"
YEARS = list(range(2013, 2027))
LGB = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=300, colsample_bytree=0.7, subsample=0.7,
           subsample_freq=1, reg_lambda=10.0, n_jobs=4, verbose=-1, random_state=7)
H = {"3a": 13, "6a": 26}


def split(d: pd.DataFrame, year: int, horizon: str):
    first = d.tarih[d.tarih.dt.year == year].min()
    train = d[(d.tarih + pd.Timedelta(weeks=H[horizon])) < first]
    test = d[(d.tarih.dt.year == year) & d.tarih.dt.month.isin([1, 4, 7, 10])]
    return train, test


def fit_predict(name: str, train: pd.DataFrame, test: pd.DataFrame, feats: list[str]) -> np.ndarray:
    import lightgbm as lgb
    X, Xt = train[feats].astype("float32"), test[feats].astype("float32")
    if name == "rastgele":
        return np.random.default_rng(int(test.tarih.iloc[0].year)).random(len(test))
    if name == "momentum_buyuk":
        ok = (test.kucuk_boyut <= 0.3) & (test.likidite >= 0.7)
        return np.where(ok, test.momentum_12_1.fillna(-1), -np.inf)
    if name == "kural_ogrenici":
        return rule_learner(train, test)
    if name in ("lgb_sinif5", "lgb_sinif1"):
        y = train["ust5_3a" if name == "lgb_sinif5" else "ust1_3a"]
        ok = y.notna()
        pos = float(y[ok].mean())
        m = lgb.LGBMClassifier(**LGB, scale_pos_weight=(1 - pos) / pos)
        m.fit(X[ok], y[ok].astype(int))
        return m.predict_proba(Xt)[:, 1]
    if name in ("lgb_sirala", "lgb_sirala_6a"):
        h = "6a" if name.endswith("6a") else "3a"
        tr = train[train[f"sira_{h}"].notna()].sort_values("tarih", kind="stable")
        r = tr[f"sira_{h}"]
        rel = np.select([r >= 0.99, r >= 0.95, r >= 0.90, r >= 0.75], [4, 3, 2, 1], 0)
        grp = tr.groupby("tarih", sort=False).size().to_numpy()
        m = lgb.LGBMRanker(**LGB, objective="lambdarank", lambdarank_truncation_level=50, label_gain=[0, 1, 3, 7, 15])
        m.fit(tr[feats].astype("float32"), rel, group=grp)
        return m.predict(Xt)
    if name == "iki_asama":
        y1 = train.buyuk_hareket_3a
        ok = y1.notna()
        p1 = float(y1[ok].mean())
        m1 = lgb.LGBMClassifier(**LGB, scale_pos_weight=(1 - p1) / p1).fit(X[ok], y1[ok].astype(int))
        big = ok & (y1 == 1)
        y2 = (train.sira_3a[big] >= 0.5).astype(int)
        m2 = lgb.LGBMClassifier(**LGB).fit(X[big], y2)
        return m1.predict_proba(Xt)[:, 1] * m2.predict_proba(Xt)[:, 1]
    if name == "kuyruk_q90":
        y = train.hedef_3a.clip(-1, 3)
        ok = y.notna()
        m = lgb.LGBMRegressor(**LGB, objective="quantile", alpha=0.9).fit(X[ok], y[ok])
        return m.predict(Xt)
    raise ValueError(name)


def rule_learner(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Kural araması YALNIZCA eğitim verisinde: ızgaradaki her kural için eğitim tarihlerinde uyan bütün hisselerin ortalama
    13 haftalık getirisinin tarih ortalaması; şart: tarihlerin ≥ %70'inde uyan hisse ve medyan ≥ 3 hisse. En iyi kural test
    yılına uygulanır; uyanlar dipten kata göre puanlanır."""
    grid = itertools.product([1.5, 2.0, 2.5], [0.0, 0.2, 0.5], [0.5, 0.7, 0.9], [0.0, 0.8, 0.87, 0.92])
    best, best_v = None, -np.inf
    tr = train[train.hedef_3a.notna()]
    for dip, gel, liq, sek in grid:
        m = (tr.dipten_52h >= dip - 1) & (tr.gelir_ham >= gel) & (tr.likidite >= liq) & (tr.sektor_momentum_12_1.fillna(0) >= sek)
        g = tr[m].groupby("tarih").hedef_3a
        n = g.size().reindex(tr.tarih.unique()).fillna(0)
        if (n > 0).mean() < 0.7 or n.median() < 3:
            continue
        v = g.mean().mean()
        if v > best_v:
            best, best_v = (dip, gel, liq, sek), v
    if best is None:
        return np.full(len(test), -np.inf)
    dip, gel, liq, sek = best
    m = (test.dipten_52h >= dip - 1) & (test.gelir_ham >= gel) & (test.likidite >= liq) & (test.sektor_momentum_12_1.fillna(0) >= sek)
    rule_learner.last = best
    return np.where(m, test.dipten_52h.fillna(0), -np.inf)


def main(name: str):
    t0 = time.time()
    d = pd.read_parquet(VERI)
    feats = features(d)
    horizon = "6a" if name.endswith("6a") else "3a"
    out = []
    for y in YEARS:
        train, test = split(d, y, horizon)
        if test.empty:
            continue
        s = fit_predict(name, train, test, feats)
        rec = test[["tarih", "cik"]].copy()
        rec["puan"] = s
        rec["model"] = name
        if name == "kural_ogrenici":
            rec["kural"] = str(getattr(rule_learner, "last", None))
        out.append(rec)
        print(f"{name} {y}: eğitim {len(train):,} (son etiket < {test.tarih.min().date()}), test {len(test):,} ({round(time.time() - t0)} sn)", flush=True)
    TAHMIN.mkdir(parents=True, exist_ok=True)
    pd.concat(out).to_parquet(TAHMIN / f"{name}.parquet")


if __name__ == "__main__":
    main(sys.argv[1])

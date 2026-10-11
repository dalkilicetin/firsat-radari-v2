"""Hızlı iterasyon: model yalnızca seçilen yıl başlarında kurulur ve 1 yıl sonra kontrol edilir.

Kullanıcı kararı (2026-10-10): iterasyonlar 3 yıl üzerinde yapılır (ITER_YEARS). Ezberi önlemek için:
- Seçilen model, iterasyonda kullanılmamış geliştirme yıllarında (VALID_YEARS) bir kez doğrulanır.
- Kilitli yıllar (2023–2025) en sonda tek sefer açılır.
Kurallar asof.py ile aynıdır: eğitim yalnızca s + 52 hafta ≤ t olan haftalarla; ölçüm yatırılabilir faaliyet
şirketlerinde, ilk 20 hisse, eşit ağırlık, alım + satım maliyeti düşülerek.

Hazırlanan girdiler data/derived/quick/ altında saklanır (her denemede yeniden hesaplanmaz); sinyal kütüphanesi
değişince parmak izi değişir ve yeniden hazırlanır.
"""

from __future__ import annotations

import dataclasses
import json
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import asof, library, model, panel, sectors
from radar.research import backtest as bt
from radar.research.asof import Recipe

ITER_YEARS = (2013, 2018, 2021)        # yükseliş, düşüş, balon + çöküş
VALID_YEARS = (2011, 2012, 2014, 2015, 2016, 2017, 2019, 2020)
LOCKED_YEARS = (2023, 2024, 2025)
W = 52
STEP = 4
CACHE = config.DATA_DIR / "derived" / "quick"
LOG = config.ROOT / "reports" / "research" / "hizli_denemeler.jsonl"


def year_start(dates: pd.DatetimeIndex, year: int) -> int:
    return int(np.flatnonzero(dates >= pd.Timestamp(f"{year}-01-01"))[0])


class QuickData:
    def __init__(self, force: bool = False):
        CACHE.mkdir(parents=True, exist_ok=True)
        import hashlib
        fp = hashlib.sha256("".join(library.group_fingerprint(g) for g in library.GROUPS).encode()
                            + (config.ROOT / "radar" / "research" / "asof.py").read_bytes()).hexdigest()[:16]
        meta = CACHE / "meta.json"
        if not force and meta.exists() and json.loads(meta.read_text()).get("fingerprint") == fp:
            self._load()
            return
        t0 = time.time()
        p = panel.build()
        sigs = library.load_all(p)
        unis = sectors.operating_universes(p)
        inv = unis[[k for k in unis if k != "tümü"][0]]
        X = model.ranked_inputs(sigs, unis["tümü"])
        from radar.research import context
        reg = context.regime(p["price"].index)
        fwd = panel.forward_returns(p["price"], p["securities"], W).reindex(p["price"].index)
        Y = asof.make_targets(fwd, unis["tümü"], W)
        sec = p["securities"].assign(cik=lambda d: d.cik.astype(str)).drop_duplicates("cik").set_index("cik")
        arrays = {"train_u": unis["tümü"].to_numpy(), "eval_u": inv.to_numpy(), "fwd": fwd.to_numpy(np.float32),
                  "dv": p["dollar_volume"].to_numpy(np.float32)}
        for k, v in Y.items():
            arrays[f"Y_{k}"] = v
        for k, v in X.items():
            arrays[f"X_{library.filename(k)[:-8]}"] = v.astype(np.float16)
        for name, a in arrays.items():
            np.save(CACHE / f"{name}.npy", a)
        # Yol boyu düşüş için 4 haftalık adımlarla getiriler yalnızca yıl başlarında gerekir.
        starts = [year_start(p["price"].index, y) for y in range(2010, 2027)]
        path = {k: panel.forward_returns(p["price"], p["securities"], k).reindex(p["price"].index).to_numpy(np.float32)[starts]
                for k in range(4, W + 1, 4)}
        np.save(CACHE / "path.npy", np.stack([path[k] for k in sorted(path)]))
        meta.write_text(json.dumps({
            "fingerprint": fp, "features": list(X), "regime": list(reg.columns), "starts": starts,
            "dates": [str(d.date()) for d in p["price"].index], "cols": list(p["price"].columns),
            "symbols": sec.symbol.reindex(p["price"].columns).fillna("?").tolist()}, ensure_ascii=False))
        reg.to_parquet(CACHE / "regime.parquet")
        print(f"hızlı veri hazırlandı ({round(time.time() - t0)} sn)", flush=True)
        self._load()

    def _load(self):
        meta = json.loads((CACHE / "meta.json").read_text())
        self.features, self.starts = meta["features"], meta["starts"]
        self.dates = pd.DatetimeIndex(meta["dates"])
        self.cols, self.symbols = meta["cols"], np.array(meta["symbols"])
        ld = lambda n: np.load(CACHE / f"{n}.npy", mmap_mode="r")
        self.train_u, self.eval_u, self.fwd, self.dv = ld("train_u"), ld("eval_u"), ld("fwd"), ld("dv")
        self.Y = {k: ld(f"Y_{k}") for k in ("sira", "fazla", "ust10", "kazanan")}
        self.X = {f: ld(f"X_{library.filename(f)[:-8]}") for f in self.features}
        self.reg = pd.read_parquet(CACHE / "regime.parquet")
        self.path = ld("path")

    def col(self, f: str, t: int) -> np.ndarray:
        if f in self.X:
            return np.asarray(self.X[f][t], dtype=np.float32)
        return np.full(len(self.cols), self.reg[f.removeprefix("donem_")].iloc[t], dtype=np.float32)

    def feats(self, rec: Recipe) -> list[str]:
        fs = [f for f in (rec.features or self.features) if f not in rec.exclude]
        return fs + [f"donem_{c}" for c in self.reg.columns] if rec.regime else fs


# Eleme kuralları (geriye bakış 2010–2022: bu işaretler büyük kaybeden olma olasılığını tutarlı biçimde artırdı).
# Değerler kesitsel sıralardır (−0,5…+0,5; eksik = 0 → elenmez); olaylarda > 0 = olay var.
SCREEN = {
    "zirveye_yakinlik_52h": lambda x: x <= -0.30,          # 52 haftalık zirveden en uzak %20
    "kazanc_getirisi": lambda x: x <= -0.25,               # kâr / piyasa değeri en düşük %25 (zarar edenler)
    "devamlilik_suphesi": lambda x: x > 0,                 # denetçinin süreklilik şüphesi
    "8k_3.02_kayıtsız hisse satışı (sulandırma)": lambda x: x > 0,
}


def screened(d: "QuickData", t: int) -> np.ndarray:
    out = np.zeros(len(d.cols), dtype=bool)
    for f, rule in SCREEN.items():
        if f in d.X:
            out |= rule(np.asarray(d.X[f][t], dtype=np.float32))
    return out


def score_at(rec: Recipe, d: QuickData, t: int) -> np.ndarray:
    """t haftasında yalnızca geçmişle eğitilmiş modelin puanları (N), puanlanmayan NaN."""
    out = _score_at(rec, d, t)
    if rec.screen:
        out = np.where(screened(d, t), np.nan, out)
    return out


def _score_at(rec: Recipe, d: QuickData, t: int) -> np.ndarray:
    if rec.learner == "ensemble":
        ranks = [pd.Series(score_at(m, d, t)).rank(pct=True).to_numpy() for m in rec.members]
        return np.nanmean(np.stack(ranks), axis=0)
    feats = d.feats(rec)
    Y = d.Y[rec.target]
    window = rec.params.get("pencere")  # yalnızca son N haftanın eğitim satırları (piyasa değişimine uyum)
    if window:
        rec = dataclasses.replace(rec, params={k: v for k, v in rec.params.items() if k != "pencere"})
    stop = max(-1, t - W - window) if window else -1
    Xs, ys = [], []
    for s in range(t - W, stop, -STEP):
        m = np.asarray(d.train_u[s]) & np.isfinite(Y[s])
        if rec.train_on != "tum":
            m &= np.asarray(d.eval_u[s])
        if m.any():
            Xs.append(np.column_stack([d.col(f, s)[m] for f in feats]))
            ys.append(np.asarray(Y[s])[m])
    fn = asof._fit(rec, np.vstack(Xs), np.concatenate(ys))
    m = np.asarray(d.train_u[t])
    out = np.full(len(d.cols), np.nan)
    out[m] = fn(np.column_stack([d.col(f, t)[m] for f in feats]))
    return out


def outcome(d: QuickData, score: np.ndarray, t: int, min_volume: float = 0.0) -> dict:
    r = np.asarray(d.fwd[t])
    universe = np.asarray(d.eval_u[t]) & np.isfinite(r)
    idx = np.flatnonzero(universe)                      # piyasa ve "en iyi 20" tüm evrenden (elenenler dahil)
    pickable = np.flatnonzero(universe & np.isfinite(score))
    if min_volume:
        pickable = pickable[np.nan_to_num(np.asarray(d.dv[t])[pickable]) >= min_volume]
    picks = pickable[np.argsort(-score[pickable])][:asof.PICKS]
    best = idx[np.argsort(-r[idx])][:asof.PICKS]
    cost = 2 * bt.cost_rate(pd.Series(np.asarray(d.dv[t])[picks])).to_numpy()
    net = r[picks] - cost
    k = d.starts.index(t) if t in d.starts else None
    dd = np.nan
    if k is not None:
        curve = np.concatenate([[1.0], np.nanmean(1 + d.path[:, k, picks], axis=1)])
        dd = float((curve / np.maximum.accumulate(curve) - 1).min())
    top10 = r[idx] >= np.quantile(r[idx], 0.9)
    return {"tarih": str(d.dates[t].date()), "portfoy": float(net.mean()), "evren_ort": float(r[idx].mean()),
            "en_iyi20": float(r[best].mean()), "yukselen": int((net > 0).sum()),
            "medyani_gecen": int((r[picks] > np.median(r[idx])).sum()),
            "en_iyi10_icinde": int(np.isin(picks, idx[top10]).sum()), "yol_en_buyuk_dusus": dd,
            "secim": [(str(d.symbols[i]), round(float(r[i]), 3)) for i in picks],
            "en_iyi20_hisseler": [(str(d.symbols[i]), round(float(r[i]), 3)) for i in best]}


def run(rec: Recipe, d: QuickData, years=ITER_YEARS) -> pd.DataFrame:
    rows = []
    for y in years:
        t = year_start(d.dates, y)
        rows.append({"yil": y} | outcome(d, score_at(rec, d, t), t, rec.min_volume))
    return pd.DataFrame(rows).set_index("yil")


def summarize(df: pd.DataFrame) -> dict:
    return {"ort_getiri": round(df.portfoy.mean(), 4), "ort_piyasa": round(df.evren_ort.mean(), 4),
            "ort_fazla": round((df.portfoy - df.evren_ort).mean(), 4), "kar_yili": int((df.portfoy > 0).sum()),
            "piyasayi_gecen_yil": int((df.portfoy > df.evren_ort).sum()), "en_kotu_fazla": round((df.portfoy - df.evren_ort).min(), 4),
            "yukselen_hisse_ort": round(df.yukselen.mean(), 1), "yakalama": round(df.portfoy.sum() / df.en_iyi20.sum(), 4)}


def log(rec: Recipe, df: pd.DataFrame, mode: str = "iterasyon") -> dict:
    entry = {"zaman": time.strftime("%Y-%m-%d %H:%M"), "mod": mode, "deneme": rec.name, "hedef": rec.target,
             "ogrenici": rec.learner, "parametre": rec.params, "donem": rec.regime, "egitim": rec.train_on,
             "min_hacim": rec.min_volume, "eleme": rec.screen, "haric": sorted(rec.exclude), "uyeler": [m.name for m in rec.members],
             "yillar": list(map(int, df.index)), "ozet": summarize(df),
             "yil_yil": {int(y): {"portfoy": round(r.portfoy, 4), "piyasa": round(r.evren_ort, 4), "yukselen": int(r.yukselen)}
                         for y, r in df.iterrows()}}
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry

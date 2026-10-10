"""Haftalık anlık görüntü: son haftanın puanları, gerekçeleri ve modelin gerçekleşmiş karnesi.

Puanlar 4. aşamada dondurulan kayan pencere modeliyle (data/derived/model_fits.pkl) üretilir; son haftanın
tahmini, yalnızca o haftaya kadar getirisi gerçekleşmiş verilerle eğitilmiş ağırlıkları kullanır.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass

import numpy as np
import pandas as pd

from radar.research import library, model, panel, risk
from radar.research.report import universes
from radar.research.run_model import FITS

THRESHOLD = 70.0  # potansiyel < 70 → belirgin potansiyel yok (vade atanmaz)
DEFAULT_HORIZON = "3a"  # vade atanmayan hisselerde yol puanları bu vadeden gösterilir


@dataclass
class Snapshot:
    date: pd.Timestamp
    table: pd.DataFrame                    # hisse başına puanlar (index: cik)
    reasons: dict[str, list[tuple]]        # cik → [(sinyal, katkı, açıklama türü, yüzdelik/var)]
    risk_reasons: dict[str, list[str]]     # cik → risk etkenleri
    track: pd.DataFrame                    # modelin son 12 aylık gerçekleşmiş karnesi


def _pct(row: np.ndarray, universe: np.ndarray) -> np.ndarray:
    s = pd.Series(np.where(universe, row, np.nan))
    return (s.rank(pct=True) * 100).to_numpy()


def load_fits() -> dict:
    with FITS.open("rb") as f:
        return pickle.load(f)["tümü"]


def scores(p: dict, fits: dict, member: np.ndarray, t: int = -1) -> tuple[pd.DataFrame, pd.DataFrame]:
    """t haftası için (vade bazında toplam puanlar, yol puanları vade bazında)."""
    cols = p["price"].columns
    total = pd.DataFrame({h: _pct(fits[("toplam", h)].pred[t], member) for h in panel.HORIZONS}, index=cols)
    roads = {(g, h): _pct(f.pred[t], member) for (g, h), f in fits.items() if g != "toplam"}
    return total, pd.DataFrame(roads, index=cols)


def contributions(sigs: dict, fit: model.Fit, member_row: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, set[str]]:
    """Son hafta: sinyal katkıları (ağırlık × girdi), sinyalin yüzdeliği / olay bayrağı ve olay sinyalleri."""
    feats = fit.features
    w = fit.weights.iloc[-1]
    rows = {n: (r, df.iloc[[-1]]) for n, (r, df) in sigs.items() if n in feats}
    X = model.ranked_inputs(rows, member_row)
    cols = member_row.columns
    contrib = pd.DataFrame({f: X[f][0] * w[f] for f in feats}, index=cols)
    events = set()
    level = {}
    for f in feats:
        raw = rows[f][1].iloc[0].where(member_row.iloc[0])
        vals = raw.dropna().unique()
        if len(vals) and set(np.round(vals, 6)) <= {0.0, 1.0}:
            events.add(f)
            level[f] = raw.fillna(0)
        else:
            level[f] = pd.Series(np.where(raw.notna(), X[f][0] + 0.5, np.nan), index=cols) * 100
    return contrib, pd.DataFrame(level, index=cols), events


def explain(cik: str, contrib: pd.DataFrame, level: pd.DataFrame, events: set[str], n: int = 4) -> list[tuple]:
    c = contrib.loc[cik]
    out = []
    for f in c.abs().sort_values(ascending=False).index:
        v = level.at[cik, f]
        if c[f] == 0 or (f in events and v == 0) or (f not in events and pd.isna(v)):
            continue  # eksik veri nötrdür; olay olmaması gerekçe sayılmaz
        out.append((f, float(c[f]), "olay" if f in events else "sira", float(v)))
    pos = [x for x in out if x[1] > 0][:n]
    neg = [x for x in out if x[1] < 0][:n]
    return pos + neg


def risk_drivers(f: dict, member_row: pd.Series, t: int = -1, n: int = 3) -> dict[str, list[str]]:
    """Her hisse için risk puanını en çok yükselten bileşenler (evrenin en riskli %20'sindekiler) + olaylar."""
    ranks = {k: f[k].iloc[t].where(member_row).rank(pct=True) for k in risk.WEIGHTS}
    out = {}
    for c in member_row.index[member_row.to_numpy()]:
        items = [(ranks[k].get(c, np.nan) * w, k) for k, w in risk.WEIGHTS.items() if ranks[k].get(c, 0) >= 0.8]
        names = [k for _, k in sorted(items, reverse=True)[:n]]
        names += [k for k in risk.EVENT_POINTS if f[k].iloc[t].get(c, 0) > 0]
        out[c] = names
    return out


def track_record(p: dict, fits: dict, unis: dict, weeks_back: int = 52) -> pd.DataFrame:
    """Son 12 ayda verilmiş puanların gerçekleşen sonucu (getirisi tamamlanmış haftalar)."""
    price, sec = p["price"], p["securities"]
    T = len(price.index)
    rows = []
    for h in ("1a", "3a", "6a"):
        w = panel.HORIZONS[h]
        fwd = panel.forward_returns(price, sec, w).reindex(price.index)
        pred = fits[("toplam", h)].pred
        for uni_name, uni in unis.items():
            u = uni.to_numpy()
            tops, bots, alls = [], [], []
            for t in range(max(0, T - 1 - w - weeks_back), T - w):
                r = fwd.iloc[t].to_numpy()
                ok = u[t] & np.isfinite(r) & np.isfinite(pred[t])
                if ok.sum() < 50:
                    continue
                ex = r[ok] - np.median(r[ok])
                lo, hi = np.quantile(ex, [0.01, 0.99])
                ex = np.clip(ex, lo, hi)
                q = pd.Series(pred[t][ok]).rank(pct=True).to_numpy()
                tops.append(ex[q >= 0.9])
                bots.append(ex[q <= 0.1])
                alls.append(ex)
            if not tops:
                continue
            top, bot = np.concatenate(tops), np.concatenate(bots)
            rows.append({"vade": h, "evren": uni_name.split(" ")[0], "hafta": len(tops),
                         "ilk10_ort": top.mean(), "ilk10_isabet": (top > 0).mean(),
                         "son10_ort": bot.mean(), "son10_isabet": (bot > 0).mean()})
    return pd.DataFrame(rows)


def build() -> Snapshot:
    p = panel.build()
    price, raw, dv, sec = p["price"], p["raw"], p["dollar_volume"], p["securities"]
    date = price.index[-1]
    unis = universes(p)
    inv_key = [k for k in unis if k != "tümü"][0]
    member_df = unis["tümü"]
    member = member_df.iloc[-1].to_numpy()
    investable = unis[inv_key].iloc[-1]

    fits = load_fits()
    sigs = library.load_all(p)
    total, roads = scores(p, fits, member)
    filled = total.fillna(-1)
    best = filled.idxmax(axis=1)
    potential = filled.max(axis=1).where(lambda s: s >= 0)
    horizon = best.where(potential >= THRESHOLD)
    show_h = horizon.fillna(DEFAULT_HORIZON)

    rf = risk.features(p)
    risk_pct, risk_level = risk.score(rf, member_df)

    s = sec.set_index(sec.cik.astype(str)).reindex(price.columns)
    table = pd.DataFrame({
        "sembol": s.symbol, "sirket": s.name.str.replace(r" - .*$", "", regex=True),
        "fiyat": raw.iloc[-1], "islem_hacmi": dv.iloc[-1], "yatirilabilir": investable,
        "potansiyel": potential, "vade": horizon, "risk": risk_level.iloc[-1], "risk_yuzdelik": risk_pct.iloc[-1] * 100,
    })
    for h in panel.HORIZONS:
        table[f"puan_{h}"] = total[h]
    for g in ("yol1", "yol2", "yol3", "yol4", "piyasa"):
        table[g] = [roads.at[c, (g, show_h[c])] if (g, show_h[c]) in roads.columns else np.nan for c in table.index]
    table = table[member]

    reasons = {}
    by_h = {}
    for h in panel.HORIZONS:
        by_h[h] = contributions(sigs, fits[("toplam", h)], member_df.iloc[[-1]])
    for c in table.index:
        contrib, level, events = by_h[show_h[c]]
        reasons[c] = explain(c, contrib, level, events)
    drivers = risk_drivers(rf, member_df.iloc[-1])
    return Snapshot(date, table, reasons, drivers, track_record(p, fits, unis))

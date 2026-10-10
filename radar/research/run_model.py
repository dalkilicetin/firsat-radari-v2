"""4. aşama raporu: python -m radar.research.run_model → reports/research/model.md

Son dönem (HOLDOUT_START sonrası) bu raporda kullanılmaz; ayrı ve tek seferlik test: run_holdout.
"""

from __future__ import annotations

import pickle
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import evaluate as ev
from radar.research import library, model, panel
from radar.research.report import universes

REPORT = config.ROOT / "reports" / "research" / "model.md"
FITS = config.DATA_DIR / "derived" / "model_fits.pkl"


def correlations(sigs, universe, sample_every: int = 8) -> pd.DataFrame:
    """Sinyaller arası ortalama kesitsel sıra korelasyonu (her 8 haftada bir örnek)."""
    names = list(sigs)
    dates = universe.index[::sample_every]
    acc = np.zeros((len(names), len(names)))
    n = 0
    for d in dates:
        u = universe.loc[d]
        m = pd.DataFrame({k: sigs[k][1].loc[d][u] for k in names}).rank(pct=True)
        c = m.corr(min_periods=50).to_numpy()
        if np.isfinite(c).sum() == 0:
            continue
        acc += np.nan_to_num(c)
        n += 1
    return pd.DataFrame(acc / max(n, 1), index=names, columns=names)


def main() -> None:
    t0 = time.time()
    p = panel.build()
    sigs = library.load_all(p)
    unis = universes(p)
    member = unis["tümü"]
    print(f"{len(sigs)} sinyal yüklendi ({round(time.time() - t0)} sn)", flush=True)

    fits = model.run(p, sigs, universe=member)
    inv_name = [k for k in unis if k != "tümü"][0]
    fits_inv = model.run(p, sigs, universe=unis[inv_name])
    FITS.parent.mkdir(parents=True, exist_ok=True)
    with FITS.open("wb") as f:
        pickle.dump({"tümü": fits, "yatırılabilir": fits_inv}, f)
    print(f"modeller kuruldu ({round(time.time() - t0)} sn)", flush=True)

    price, sec, dates, cols = p["price"], p["securities"], p["price"].index, p["price"].columns
    rows = []
    for train_name, fset in (("tümü", fits), ("yatırılabilir", fits_inv)):
        for (g, h), fit in fset.items():
            score = model.to_score(fit.pred, dates, cols)
            for uni_name, uni in unis.items():
                if train_name == "yatırılabilir" and uni_name == "tümü":
                    continue
                r = ev.evaluate(score.where(uni), price, sec, g, {h: panel.HORIZONS[h]}, universe=uni).rows[0]
                rows.append({"eğitim": train_name, "model": g, "vade": h, "evren": uni_name.split(" ")[0],
                             "IC": r.get("IC"), "IC_t": r.get("IC_t"), "ilk10_fazla": r.get("ilk10_fazla"),
                             "son10_fazla": r.get("son10_fazla"), "fark": r.get("fark"), "isabet_ilk10": r.get("isabet_ilk10")})
    res = pd.DataFrame(rows)

    # Karşılaştırma: tek başına momentum (bilinen etki) ile toplam model.
    base = []
    for h, w in panel.HORIZONS.items():
        for uni_name, uni in unis.items():
            r = ev.evaluate(sigs["momentum_12_1"][1].where(uni), price, sec, "momentum", {h: w}, universe=uni).rows[0]
            base.append({"vade": h, "evren": uni_name.split(" ")[0], "IC": r["IC"], "IC_t": r["IC_t"], "fark": r["fark"]})
    base = pd.DataFrame(base)

    # Vade seçimi: atanan vadede gerçekleşen fazla getiri (haftalık ortalamaya çevrilmiş) vs sabit 3a.
    potential, horizon = model.horizon_choice(fits, dates, cols)
    hz_rows = []
    for h, w in panel.HORIZONS.items():
        ex = ev.excess_returns(price, sec, w, member)
        sel = (horizon.reindex(ex.index) == h)
        vals = ex.where(sel).stack().dropna()
        ex3 = ev.excess_returns(price, sec, 13, member).where(sel.reindex(ev.excess_returns(price, sec, 13, member).index)).stack().dropna()
        hz_rows.append({"atanan vade": h, "hisse-hafta": len(vals), "ort fazla getiri (vadede)": round(vals.mean(), 4),
                        "haftalık eşdeğer": round(vals.mean() / w, 5), "aynı hisseler sabit 3a, haftalık": round(ex3.mean() / 13, 5)})
    hz = pd.DataFrame(hz_rows)
    bucket_rows = []
    ex13 = ev.excess_returns(price, sec, 13, member)
    pot = potential.reindex(ex13.index)
    # Uç değerler (birkaç mikro hissenin yüzlerce yüzdelik sıçraması) ortalamayı çarpıtmasın: haftalık %1/%99 kırpma.
    ex13w = ex13.clip(ex13.quantile(0.01, axis=1), ex13.quantile(0.99, axis=1), axis=0)
    for lo, hi in ((0, 30), (30, 50), (50, 70), (70, 80), (80, 90), (90, 101)):
        m = (pot >= lo) & (pot < hi)
        v, vw = ex13.where(m).stack().dropna(), ex13w.where(m).stack().dropna()
        bucket_rows.append({"potansiyel": f"{lo}–{min(hi, 100)}", "hisse-hafta": len(v),
                            "3a kırpılmış ort fazla": round(vw.mean(), 4), "3a medyan fazla": round(v.median(), 4),
                            "pozitif fazla getiri payı": round((v > 0).mean(), 3)})
    buckets = pd.DataFrame(bucket_rows)

    last_w = {h: fits[("toplam", h)].weights.iloc[-1] for h in panel.HORIZONS}
    wtab = pd.DataFrame(last_w)
    wtab["yol"] = [sigs[n][0] for n in wtab.index]
    wtab = wtab.reindex(wtab["3a"].abs().sort_values(ascending=False).index)

    corr = correlations(sigs, member)
    pairs = corr.where(np.triu(np.ones(corr.shape), 1).astype(bool)).stack().sort_values(key=abs, ascending=False).head(15)

    pivot = lambda df, uni, train: df[(df.evren == uni) & (df["eğitim"] == train)].pivot(index="model", columns="vade", values="IC")[list(panel.HORIZONS)]
    lines = [
        "# 4. aşama: kayan pencere modeli", "",
        f"Dönem: 2016 → {ev.HOLDOUT_START.date()} öncesi; son dönem kullanılmadı. Her hafta yalnızca o ana kadar "
        "gerçekleşmiş getirilerle eğitilen modelin tahmini değerlendirilir (örneklem dışı). Değerler IC "
        "(puan ile gerçekleşen fazla getirinin sıralama korelasyonu).", "",
        "## Örneklem dışı IC — tüm evrende eğitilen modeller, tüm evrende ölçüm", "", pivot(res, "tümü", "tümü").round(4).to_markdown(), "",
        "## Örneklem dışı IC — yatırılabilir evrende ölçüm", "",
        "Tüm evrende eğitilen:", "", pivot(res, "yatırılabilir", "tümü").round(4).to_markdown(), "",
        "Yatırılabilir evrende eğitilen:", "", pivot(res, "yatırılabilir", "yatırılabilir").round(4).to_markdown(), "",
        "## Karşılaştırma: yalnızca 12-1 ay momentum", "", base.pivot(index="evren", columns="vade", values="IC")[list(panel.HORIZONS)].to_markdown(), "",
        "## Toplam modelin ayrıntısı (tüm evren)", "",
        res[(res.model == "toplam") & (res["eğitim"] == "tümü")].drop(columns=["eğitim", "model"]).to_markdown(index=False), "",
        "## Potansiyel puanı ve gerçekleşen 3 aylık fazla getiri", "", buckets.to_markdown(index=False), "",
        "## Vade seçimi", "",
        "Her hisse için en yüksek puanı aldığı vade (puan ≥ 70). Atanan vadedeki gerçekleşen fazla getiri, aynı "
        "hisselerin sabit 3 aylık vadesiyle haftalık eşdeğer olarak karşılaştırılır.", "", hz.to_markdown(index=False), "",
        "## Son ağırlıklar (toplam model, en büyük 3a ağırlıklara göre)", "", wtab.round(4).to_markdown(), "",
        "## Birbirine en çok benzeyen sinyaller (ortalama kesitsel sıra korelasyonu)", "",
        pairs.round(3).rename("korelasyon").to_frame().to_markdown(), "",
    ]
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines[:30]))
    print(f"{round(time.time() - t0)} sn")


if __name__ == "__main__":
    main()

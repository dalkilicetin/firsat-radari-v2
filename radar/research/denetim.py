"""Dış inceleme denetimi: python -m radar.research.denetim [--son 2024]

Sabit model (sıra hedefi, temiz belirti seti, 10 hisse, 3 ay, 5 yıl pencere, 5 tohum) ile yürüyen test yapılır; yalnızca
--son yılına kadar (varsayılan 2024; 2025–2026 kilitli son test dönemi) ölçülür. Puanlar kaydedilir, sonra:
1. Risk ve maliyet: yıllık bileşik getiri, oynaklık, Sharpe (risksiz: FEDFUNDS), en kötü düşüş, kazançlı dönem oranı,
   devir hızı, brüt–maliyet–net, maliyet ×2 stres testi, en iyi seçimlere bağımlılık, sektör ve küçük hisse yoğunlaşması,
   yıl yıl (rejim) döküm.
2. Teorik / uygulanabilir: tüm hisseler, likit (günlük işlem ≥ 1 M$), çok likit (≥ 10 M$) evrende aynı puanlarla seçim;
   kapasite: her seçimde 5 günde günlük işlemin %5'ini aşmadan kurulabilecek portföy büyüklüğü.
3. Faktör regresyonu: çeyreklik portföy getirisi ~ piyasa + boyut + değer + momentum + kârlılık + yatırım
   (faktörler çerçeveden üçte birlik uzun–kısa portföylerle kurulur); alfa ve t.
4. Kıyas: bütün belirtilerin eşit ağırlıklı toplamı (yönler yalnızca eğitim döneminin IC işaretinden) ile 10 hisse.
5. Kopyalarda ek bilgi: |r| ≥ 0,85 çiftlerde, ikizinden arındırılmış belirtinin IC'si.
Çıktı: reports/research/denetim.json
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import hizli
from radar.research.backtest import cost_rate

OUT = config.ROOT / "reports" / "research" / "denetim.json"
SCORES = config.ROOT / "data" / "derived" / "denetim_puanlar.parquet"
K, WEEKS = 10, 13


def oos_scores(son: int) -> pd.DataFrame:
    hizli.TEST_YEARS = tuple(range(2013, son + 1))
    df, all_feats = hizli.load("3ay")
    mode, groups, params = hizli.EXPERIMENTS["t5_temiz"]
    feats = [c for c in all_feats if any(hizli.GROUPS[g](c) for g in groups) and c not in hizli.CIKAR]
    gap = pd.Timedelta(weeks=WEEKS)
    parts = []
    for Y in hizli.TEST_YEARS:
        tr = df[(df.tarih + gap < pd.Timestamp(f"{Y}-01-01")) & (df.yil >= Y - hizli.PENCERE)]
        te = df[(df.yil == Y) & df.tarih.dt.month.isin((1, 4, 7, 10))]
        s, _ = hizli.score(mode, tr, te, feats, params)
        parts.append(te.assign(puan=s))
        print("puan", Y, flush=True)
    out = pd.concat(parts)
    out.to_parquet(SCORES)
    return out


def portfolio(x: pd.DataFrame, col: str = "puan", k: int = K, cost_mult: float = 1.0, mask=None) -> pd.DataFrame:
    rows, held = [], {}
    for t, g in x.groupby("tarih"):
        if mask is not None:
            g = g[mask.loc[g.index] if isinstance(mask, pd.Series) else mask(g)]
        top = g.nlargest(k, col)
        if top.empty:
            continue
        rate = dict(zip(top.index.astype(str), cost_mult * cost_rate(top.islem_tutari.fillna(0)).to_numpy()))
        c = (sum(v for n, v in rate.items() if n not in held) + sum(v for n, v in held.items() if n not in rate)) / len(top)
        turnover = len(set(rate) - set(held)) / len(top)
        held = rate
        rows.append({"tarih": t, "brut": float(top.getiri.mean()), "maliyet": c, "net": float(top.getiri.mean() - c),
                     "devir": turnover, "en_iyi_cikarilinca": float(top.getiri.drop(top.getiri.idxmax()).mean() - c),
                     "kucuk_pay": float((top.kucuk_boyut >= 0.8).mean()) if "kucuk_boyut" in top else np.nan,
                     "sektor_max_pay": float(top.sektor.value_counts(normalize=True).iloc[0]) if "sektor" in top else np.nan,
                     "kapasite": float((top.islem_tutari.fillna(0) * 0.05 * 5).min() * len(top)),
                     "secilen": list(top.sembol.astype(str))})
    return pd.DataFrame(rows).set_index("tarih")


def stats(p: pd.DataFrame, rf: pd.Series, spy: pd.Series) -> dict:
    n = p.net
    eq = (1 + n).cumprod()
    dd = float((eq / eq.cummax() - 1).min())
    per_year = 52 / WEEKS
    cagr = float(eq.iloc[-1] ** (per_year / len(n)) - 1)
    r = rf.reindex(n.index, method="ffill").fillna(0) / 100 / per_year
    ex = n - r
    yearly = p.groupby(p.index.year).agg(net=("net", lambda s: np.prod(1 + s) - 1), brut=("brut", lambda s: np.prod(1 + s) - 1))
    yearly["spy"] = spy.reindex(yearly.index)
    return {"yillik_bilesik": cagr, "yillik_ortalama": float(yearly.net.mean()), "oynaklik": float(n.std() * np.sqrt(per_year)),
            "sharpe": float(ex.mean() / ex.std() * np.sqrt(per_year)), "en_kotu_dusus": dd,
            "kazancli_donem": float((n > 0).mean()), "devir": float(p.devir.mean()),
            "yillik_maliyet": float(p.maliyet.mean() * per_year), "brut_yillik_ortalama": float(yearly.brut.mean()),
            "en_iyi_secim_cikarilinca_yillik": float(p.groupby(p.index.year).en_iyi_cikarilinca.apply(lambda s: np.prod(1 + s) - 1).mean()),
            "kucuk_hisse_payi": float(p.kucuk_pay.mean()), "en_buyuk_sektor_payi": float(p.sektor_max_pay.mean()),
            "kapasite_medyan_usd": float(p.kapasite.median()), "kapasite_p10_usd": float(p.kapasite.quantile(0.1)),
            "spyi_gecen_yil": int((yearly.net > yearly.spy).sum()), "yil": int(len(yearly)),
            "yillar": {int(y): {"net": round(float(v.net), 3), "spy": round(float(v.spy), 3)} for y, v in yearly.iterrows()}}


def factors(x: pd.DataFrame) -> pd.DataFrame:
    def ls(col, sign=1):
        def f(g):
            q = g[col].rank(pct=True)
            return float(sign * (g.getiri[q >= 2 / 3].mean() - g.getiri[q <= 1 / 3].mean()))
        return x.groupby("tarih").apply(f)
    return pd.DataFrame({"piyasa": x.groupby("tarih").getiri.mean(), "boyut": ls("kucuk_boyut"), "deger": ls("defter_fiyat"),
                         "momentum": ls("momentum_12_1"), "karlilik": ls("ozsermaye_karliligi"), "yatirim": ls("varlik_buyumesi_dusuk")})


def regress(y: pd.Series, X: pd.DataFrame) -> dict:
    d = pd.concat([y.rename("y"), X], axis=1).dropna()
    A = np.column_stack([np.ones(len(d)), d[X.columns].to_numpy()])
    b, *_ = np.linalg.lstsq(A, d.y.to_numpy(), rcond=None)
    res = d.y.to_numpy() - A @ b
    s2 = res @ res / (len(d) - A.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(A.T @ A)))
    names = ["alfa"] + list(X.columns)
    r2 = 1 - (res @ res) / ((d.y - d.y.mean()) @ (d.y - d.y.mean()))
    return {"katsayi": dict(zip(names, np.round(b, 4))), "t": dict(zip(names, np.round(b / se, 2))),
            "alfa_yillik": float(b[0] * 52 / WEEKS), "r2": float(r2), "donem": int(len(d))}


def equal_weight(df: pd.DataFrame, x: pd.DataFrame, feats: list[str]) -> pd.DataFrame:
    from radar.research import belirti_testi as bt
    parts = []
    for Y in sorted(x.yil.unique()):
        tr = df[(df.tarih + pd.Timedelta(weeks=WEEKS) < pd.Timestamp(f"{Y}-01-01")) & (df.yil >= Y - hizli.PENCERE)]
        ic = bt.ic_by_month(tr, feats, "getiri").mean()
        sign = np.sign(ic).fillna(0)
        te = x[x.yil == Y]
        z = (te[feats].fillna(0.5) - 0.5).mul(sign, axis=1).sum(axis=1)
        parts.append(te.assign(esit=z))
    return pd.concat(parts)


def twins(x: pd.DataFrame, feats: list[str]) -> list[dict]:
    smp = x.sample(min(len(x), 60_000), random_state=0)
    C = smp[feats].corr(method="spearman").abs()
    out = []
    for i, a in enumerate(feats):
        for b in feats[i + 1:]:
            if C.at[a, b] >= 0.85:
                for keep, test in ((a, b), (b, a)):
                    def res_ic(g):
                        d = g[[keep, test, "getiri"]].dropna()
                        if len(d) < 100:
                            return np.nan
                        beta = np.polyfit(d[keep], d[test], 1)
                        resid = d[test] - np.polyval(beta, d[keep])
                        return resid.corr(d.getiri.rank(pct=True), method="spearman")
                    s = x.groupby("tarih").apply(res_ic).dropna()
                    out.append({"belirti": test, "ikiz": keep, "r": round(float(C.at[a, b]), 2),
                                "ek_ic": round(float(s.mean()), 4), "t": round(float(s.mean() / s.std() * np.sqrt(len(s))), 2)})
    return out


def main(son: int = 2024) -> dict:
    x = pd.read_parquet(SCORES) if "--hazir" in sys.argv and SCORES.exists() else oos_scores(son)
    x = x[x.yil <= son]
    fred = archive.load("fred")
    rf = fred[fred.series == "FEDFUNDS"].set_index("date").value.sort_index()
    from radar.research import izgara
    spy = pd.Series(izgara.spy_years())
    res = {}
    base = portfolio(x)
    res["risk"] = stats(base, rf, spy)
    res["maliyet_x2"] = stats(portfolio(x, cost_mult=2.0), rf, spy)
    res["likit_1M"] = stats(portfolio(x, mask=lambda g: g.islem_tutari.fillna(0) >= 1e6), rf, spy)
    res["likit_10M"] = stats(portfolio(x, mask=lambda g: g.islem_tutari.fillna(0) >= 1e7), rf, spy)
    print(json.dumps({k: {kk: v[kk] for kk in ("yillik_ortalama", "yillik_bilesik", "sharpe", "en_kotu_dusus", "kapasite_medyan_usd")}
                      for k, v in res.items()}, ensure_ascii=False, indent=1), flush=True)
    F = factors(x)
    res["faktor"] = regress(base.net, F)
    print("faktör:", json.dumps(res["faktor"], ensure_ascii=False), flush=True)
    df, all_feats = hizli.load("3ay")
    feats = [c for c in all_feats if c not in hizli.CIKAR and not c.startswith("piyasa_")]
    ew = equal_weight(df, x, feats)
    res["esit_agirlik"] = stats(portfolio(ew, col="esit"), rf, spy)
    print("eşit ağırlık:", res["esit_agirlik"]["yillik_ortalama"], flush=True)
    res["ikizler"] = twins(x, feats)
    print("ikizler:", json.dumps(res["ikizler"], ensure_ascii=False), flush=True)
    res["son_secimler"] = {str(k.date()): v for k, v in base.secilen.tail(4).items()}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    return res


if __name__ == "__main__":
    son = next((int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--son=")), 2024)
    main(son)

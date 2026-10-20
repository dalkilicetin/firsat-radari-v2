"""Yeni radar v2: üç model (A sıralama, B büyük kazanan, C risk) ve yürüyen test.

Model A: 3 aylık getirinin evren içindeki sırasını tahmin eder (getiri skoru).
Model B: 3 ayda evrenin en iyi %5'ine girmeyi tahmin eder (büyük kazanan skoru).
Model C: 3 ayda −%20'den fazla kaybetmeyi tahmin eder (risk skoru).

Skorlar o haftanın evreni içindeki yüzdelik sıradır (0–100); olasılık değildir.
Özellikler yalnızca perşembe fiyat panelinden ve o gün bilinen işaretlerden gelir. Eğitim: her test yılı için, etiketi
test yılı başından önce tamamlanmış satırlar (13 hafta aralık). Parametreler sabit; ayar yok.
2013–2022 geliştirme, 2023–2026 ikinci bakış (o dönem bir kez hatalı veriyle açıldı; temiz sınav canlı kayıttır).

python -m radar.arac.yz → reports/research/arac_yz.json / arac_yz.md, data/derived/arac/yz/skorlar.parquet
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import config
from radar.arac import analiz, isaretler
from radar.arac.analiz import Veri

R = config.ROOT / "reports" / "research"
OUT = isaretler.CACHE / "yz"
VADE = "3a"
H = 13                 # hafta; etiket aralığı
BUYUK_KAYIP = -0.20
LGB = dict(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=300, colsample_bytree=0.7,
           subsample=0.7, subsample_freq=1, reg_lambda=10.0, n_jobs=4, verbose=-1, random_state=7)
ILK_TEST = 2016
OZELLIKLER = ["r4", "r13", "r26", "r52", "vol13", "vol26", "vol_daralma", "tepe_uzaklik", "kirilim", "dip_kat", "hacim_degisim",
              "r26_sira", "r13_sira", "piyasa_ilerleme", "log_pd", "log_islem"] + isaretler.OLUMLU + ["dikkat_sayisi"]


def ozellikler(v: Veri) -> dict[str, pd.DataFrame]:
    """Özellik tablosu: ad -> (tarih × cik). Hepsi perşembe verisiyle hesaplanır."""
    tab = v.tablo
    P = tab["fiyat_persembe"].astype("float64")
    g = np.log(P).diff()
    ev = tab["evren"]
    f = {}
    for k in (4, 13, 26, 52):
        f[f"r{k}"] = P / P.shift(k) - 1
    f["vol13"] = g.rolling(13, min_periods=10).std()
    f["vol26"] = g.rolling(26, min_periods=20).std()
    f["vol_daralma"] = f["vol13"] / g.rolling(52, min_periods=40).std()
    f["tepe_uzaklik"] = P / P.rolling(52, min_periods=40).max() - 1
    f["kirilim"] = P / P.shift(1).rolling(26, min_periods=20).max() - 1      # >0: 26 haftalık zirve aşıldı
    f["dip_kat"] = P / P.rolling(52, min_periods=40).min()
    isl = tab["islem_tutari"].astype("float64")
    f["hacim_degisim"] = isl / isl.shift(13) - 1
    f["r26_sira"] = f["r26"].where(ev).rank(axis=1, pct=True)
    f["r13_sira"] = f["r13"].where(ev).rank(axis=1, pct=True)
    pi = (f["r13"].where(ev) > 0).sum(axis=1) / ev.sum(axis=1).replace(0, np.nan)
    f["piyasa_ilerleme"] = pd.DataFrame(np.repeat(pi.to_numpy()[:, None], P.shape[1], axis=1), index=P.index, columns=P.columns)
    f["log_pd"] = np.log(tab["piyasa_degeri"].astype("float64"))
    f["log_islem"] = np.log(isl)
    for n in isaretler.OLUMLU:
        f[n] = v.isaret[n].astype(float)
    f["dikkat_sayisi"] = v.isaret["dikkat_sayisi"].astype(float)
    return f


def tablo_uzun(v: Veri) -> pd.DataFrame:
    """Evrendeki (tarih, cik) satırları: özellikler + etiketler (etiket henüz yoksa NaN)."""
    f = ozellikler(v)
    ev = v.tablo["evren"]
    cols = {k: f[k].where(ev).stack(future_stack=True) for k in OZELLIKLER}
    X = pd.DataFrame(cols)
    X = X[ev.stack(future_stack=True).reindex(X.index).fillna(False).astype(bool)]
    n3 = v.tablo[f"net_{VADE}"].stack(future_stack=True).reindex(X.index)
    b3 = v.tablo[f"brut_{VADE}"].where(ev).rank(axis=1, pct=True).stack(future_stack=True).reindex(X.index)
    X["net"] = n3
    X["sira"] = b3                       # Model A hedefi: evren içi yüzdelik sıra (brüt getiri)
    X["kazanan"] = np.where(b3.isna(), np.nan, (b3 >= analiz.KAZANAN_SIRA).astype(float))
    X["buyuk_kayip"] = np.where(n3.isna(), np.nan, (n3 < BUYUK_KAYIP).astype(float))
    return X


def _lgb(hedef: str):
    import lightgbm as lgb
    return lgb.LGBMRegressor(**LGB) if hedef == "sira" else lgb.LGBMClassifier(**LGB)


HEDEFLER = {"A": "sira", "B": "kazanan", "C": "buyuk_kayip"}


def _skor(m, hedef: str, X: pd.DataFrame) -> np.ndarray:
    return m.predict(X) if hedef == "sira" else m.predict_proba(X)[:, 1]


def yuruyen(X: pd.DataFrame, son_yil: int) -> pd.DataFrame:
    """Her test yılı için, etiketi yıl başından önce bitmiş satırlarla eğit; yılı tahmin et. Son yıl dahil."""
    tarih = X.index.get_level_values(0)
    out = []
    for y in range(ILK_TEST, son_yil + 1):
        bas = pd.Timestamp(f"{y}-01-01")
        tr = X[tarih <= bas - pd.Timedelta(weeks=H + 1)]
        te = X[(tarih >= bas) & (tarih < pd.Timestamp(f"{y + 1}-01-01"))]
        if len(te) == 0 or len(tr) < 50_000:
            continue
        tr = tr.iloc[:: 2]  # her iki satırdan biri: aynı hafta içi satırlar zaten çok benzer, hız için
        o = pd.DataFrame(index=te.index)
        for ad, h in HEDEFLER.items():
            t = tr[tr[h].notna()]
            m = _lgb(h).fit(t[OZELLIKLER], t[h])
            o[ad] = _skor(m, h, te[OZELLIKLER])
        out.append(o)
        print(f"  {y}: eğitim {len(tr):,} satır, test {len(te):,}", flush=True)
    return pd.concat(out)


def son_hafta(X_son: pd.DataFrame, X: pd.DataFrame) -> pd.DataFrame:
    """En son perşembe satırları için skor: etiketi bilinen tüm satırlarla eğitilmiş model."""
    tr = X[X["net"].notna()].iloc[:: 2]
    o = pd.DataFrame(index=X_son.index)
    for ad, h in HEDEFLER.items():
        t = tr[tr[h].notna()]
        o[ad] = _skor(_lgb(h).fit(t[OZELLIKLER], t[h]), h, X_son[OZELLIKLER])
    return o


def yuzdelik(s: pd.DataFrame) -> pd.DataFrame:
    """Haftanın evreni içinde 0–100 yüzdelik sıra (olasılık değil)."""
    return s.groupby(level=0).rank(pct=True) * 100


def ilk10(skor: pd.Series, sektor: pd.Series, n: int = 10, en_fazla: int = 3) -> list[str]:
    """Skora göre ilk n; aynı sektörden en fazla 3."""
    picks, per = [], {}
    for c in skor.dropna().sort_values(ascending=False).index:
        s = sektor.get(c, "")
        if per.get(s, 0) >= en_fazla:
            continue
        picks.append(c)
        per[s] = per.get(s, 0) + 1
        if len(picks) == n:
            break
    return picks


def degerlendir(v: Veri, X: pd.DataFrame, S: pd.DataFrame, yillar: tuple[int, int], kural_listeleri: dict) -> dict:
    """Aynı haftalarda: kural radarı, Model A, Model B, basit momentum (26 hafta), rastgele. Masraf sonrası 3 ay."""
    tab = v.tablo
    net = tab[f"net_{VADE}"]
    spy = tab[f"kiyas_{VADE}"]["borsa"]
    kaz = v.kazanan(VADE)
    tarihler = [t for t in S.index.get_level_values(0).unique() if yillar[0] <= t.year <= yillar[1] and net.loc[t].notna().any()]
    rng = np.random.default_rng(7)
    sek = v.sektor
    adlar = ["kural", "A", "B", "momentum", "rastgele", "A_dusuk_risk"]
    sonuc = {a: [] for a in adlar}
    for t in tarihler:
        s = S.loc[t]
        ev = v.tablo["evren"].loc[t]
        havuz = ev[ev].index
        mom = X.loc[t, "r26"].reindex(havuz)
        listeler = {
            "kural": kural_listeleri.get(t, []),
            "A": ilk10(s["A"], sek),
            "B": ilk10(s["B"], sek),
            "momentum": ilk10(mom, sek),
            "rastgele": list(rng.choice(havuz, size=min(10, len(havuz)), replace=False)),
        }
        c_ort = s["C"].median()
        listeler["A_dusuk_risk"] = ilk10(s["A"].where(s["C"] <= c_ort), sek)
        for a, pk in listeler.items():
            if not pk:
                continue
            n = net.loc[t, pk]
            sonuc[a].append(dict(t=t, ort=n.mean(), med=n.median(), spy=spy.at[t], kazanan=kaz.loc[t, pk].mean(),
                                 kayip=(n < BUYUK_KAYIP).mean()))
    out = {}
    for a, rows in sonuc.items():
        d = pd.DataFrame(rows)
        if d.empty:
            continue
        zincir = d.iloc[:: H]                       # üst üste binmeyen 13 haftalık zincir
        fazla = d.ort - d.spy
        out[a] = dict(hafta=len(d), ort=float(d.ort.mean()), medyan=float(d.med.mean()), fazla_ort=float(fazla.mean()),
                      spy_yenen=float((fazla > 0).mean()), kazanan_orani=float(d.kazanan.mean()),
                      buyuk_kayip_orani=float(d.kayip.mean()), sharpe=float(_sharpe(zincir.ort)), sharpe_spy=float(_sharpe(zincir.spy)),
                      fazla_ci=analiz._boot(fazla))
    return out


def _sharpe(r: pd.Series) -> float:
    """13 haftalık zincir getirilerinden yıllıklandırılmış Sharpe (risksiz oran 0)."""
    r = r.dropna()
    return float(r.mean() / r.std() * np.sqrt(4)) if len(r) > 3 and r.std() > 0 else float("nan")


def risk_kovalari(X: pd.DataFrame, S: pd.DataFrame, yillar: tuple[int, int]) -> dict:
    """Model C'nin skor kovaları: her kovanın gerçekte büyük kayıp (−%20'den fazla) yaşama oranı. Haftalık yüzdeliğe göre 5 kova."""
    y = S.index.get_level_values(0).year
    s = S[(y >= yillar[0]) & (y <= yillar[1])].copy()
    s["kayip"] = X["buyuk_kayip"].reindex(s.index)
    s = s[s.kayip.notna()]
    pct = s["C"].groupby(level=0).rank(pct=True)
    s["kova"] = np.minimum((pct * 5).astype(int), 4) + 1
    g = s.groupby("kova").kayip.agg(["mean", "size"])
    return {int(k): dict(kayip_orani=float(r["mean"]), satir=int(r["size"])) for k, r in g.iterrows()}


def main(sinav_da: bool = True) -> dict:
    v = Veri.yukle()
    X = tablo_uzun(v)
    son_t = v.tarihler.max()
    X_son = X[X.index.get_level_values(0) == son_t]
    son_yil = X[X["net"].notna()].index.get_level_values(0).max().year
    print("yürüyen test...", flush=True)
    S = yuruyen(X, son_yil)
    OUT.mkdir(parents=True, exist_ok=True)
    ayar = analiz.secilen_ayar()
    tar = pd.DatetimeIndex(S.index.get_level_values(0).unique())
    kural = analiz.liste(v, ayar, tar)
    sonuc = {"gelistirme_2016_2022": degerlendir(v, X, S, (ILK_TEST, 2022), kural),
             "risk_kovalari_2016_2022": risk_kovalari(X, S, (ILK_TEST, 2022))}
    if sinav_da:
        sonuc["ikinci_bakis_2023_2026"] = degerlendir(v, X, S, (2023, 2100), kural)
        sonuc["risk_kovalari_2023_2026"] = risk_kovalari(X, S, (2023, 2100))
    sonuc["not"] = ("Skorlar yüzdelik sıradır, olasılık değil. 2013–2015 yalnızca eğitimde. 2023–2026 bir kez hatalı veriyle açılmıştı; "
                    "temiz sınav canlı kayıttır.")
    S.to_parquet(OUT / "skorlar.parquet")
    # canlı skorlar: en son perşembe, tam eğitim
    if len(X_son):
        sk = son_hafta(X_son, X)
        sk.to_parquet(OUT / "son_hafta.parquet")
    (R / "arac_yz.json").write_text(json.dumps(sonuc, indent=1, ensure_ascii=False, default=float))
    rapor_yaz(sonuc)
    return sonuc


def p(x) -> str:
    return "—" if x is None or pd.isna(x) else f"{'+' if x > 0 else '−' if x < 0 else ''}%{abs(x) * 100:.1f}"


ISIM = {"kural": "Kural radarı (mevcut)", "A": "Model A (getiri sırası)", "B": "Model B (büyük kazanan)", "momentum": "Basit momentum (26 hafta)",
        "rastgele": "Rastgele 10", "A_dusuk_risk": "Model A, düşük riskli yarı"}


def rapor_yaz(s: dict | None = None) -> None:
    s = s or json.loads((R / "arac_yz.json").read_text())
    L = ["# Yapay zekâ modelleri: A (getiri), B (büyük kazanan), C (risk) — yürüyen test", "",
         "Her yıl, yalnızca o yıldan önce sonucu bilinen satırlarla eğitilmiş model o yılı tahmin eder (sabit ayar, ayar yok). "
         "Her hafta 10 hisse (sektör başına en fazla 3), alış cuma kapanışı, masraflar düşülmüş, 3 ay. "
         "Skorlar yüzdelik sıradır; **olasılık değildir**.", ""]
    for bas, key in (("2016–2022 (geliştirme)", "gelistirme_2016_2022"), ("2023–2026 (ikinci bakış)", "ikinci_bakis_2023_2026")):
        if key not in s:
            continue
        L += [f"## {bas}", "", "| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for a, r in s[key].items():
            ci = r["fazla_ci"]
            L.append(f"| {ISIM[a]} | {r['hafta']} | {p(r['ort'])} | {p(r['medyan'])} | {p(r['fazla_ort'])} ({p(ci[0])} … {p(ci[1])}) | "
                     f"%{r['spy_yenen'] * 100:.0f} | %{r['kazanan_orani'] * 100:.1f} | %{r['buyuk_kayip_orani'] * 100:.1f} | {r['sharpe']:.2f} ({r['sharpe_spy']:.2f}) |")
        L.append("")
    for bas, key in (("2016–2022", "risk_kovalari_2016_2022"), ("2023–2026", "risk_kovalari_2023_2026")):
        if key in s:
            L += [f"## Risk skoru kovaları ({bas})", "", "Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.", "",
                  "| Kova | Büyük kayıp oranı | Satır |", "|---|---|---|"]
            L += [f"| {k} | %{r['kayip_orani'] * 100:.1f} | {r['satir']:,} |" for k, r in s[key].items()]
            L.append("")
    L += [s["not"], ""]
    (R / "arac_yz.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    if "--rapor" in sys.argv:
        rapor_yaz()
    else:
        main()

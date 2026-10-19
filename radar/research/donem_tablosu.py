"""ANA ANALİZ YÖNTEMİ: dönem karşılaştırma tablosu (kullanıcı isteği, 19 Ekim 2026).

Her çeyrek başı (Ocak/Nisan/Temmuz/Ekim'in ilk Cuması) için:
  - Gerçekte en çok kazandıran 3 hisse (sonraki 13 hafta getirisine göre) ve 3 ay / 6 ay getirileri,
  - Her modelin o gün (yalnızca o güne kadarki veriyle) seçtiği hisseler: ilk 3'ünün adı (sıra: dipten kat, büyükten küçüğe)
    ve seçtiği BÜTÜN hisselerin ortalama 3 ay / 6 ay getirisi (model hepsini eşit ağırlıkla alır),
  - S&P 500 (SPY) 3 ay / 6 ay.
Evren: finans dışı, fiyat ≥ 1 $, günlük işlem ≥ 1 M$ (bilinen). Getiriler brüt (maliyetsiz), düzeltilmiş fiyattan; 3 ay =
13 hafta, 6 ay = 26 hafta; dönemde borsadan çıkanlarda son fiyat, iflasta −%100.

'Görmediği veri' sütunu: seçim her zaman yalnızca o güne kadarki veriyle yapılır. Ancak kuralın kendisi: kullanıcı kuralları
(K1–K5) veriye bakılarak ayarlanmadı; bizim bulduğumuz kurallar 2010–2026 verisine bakılarak bulundu (geçmiş sonuçları
iyimser olabilir). Gerçekten görülmemiş tek test: canlı kayıt (12 Ekim 2026 →).

Yeni model eklemek: MODELS sözlüğüne (ad, açıklama, kural verisi gördü mü, maske fonksiyonu) satırı eklenir.

python -m radar.research.donem_tablosu → reports/research/donem_tablosu.md, donem_tablosu.csv, donem_tablosu_ozet.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, panel
from radar.research.kural_seti import RULES, history
from radar.research.pattern_avi import CACHE, FRAME

R = config.ROOT / "reports" / "research"

# (açıklama, kural veriye bakılarak mı bulundu, maske)
MODELS = {
    "K1": (RULES["K1"][0], "hayır (kullanıcı)", RULES["K1"][1]),
    "K2": (RULES["K2"][0], "hayır (kullanıcı)", RULES["K2"][1]),
    "K3": (RULES["K3"][0], "hayır (kullanıcı)", RULES["K3"][1]),
    "K3b": (RULES["K3b"][0], "hayır (kullanıcı)", RULES["K3b"][1]),
    "K4": (RULES["K4"][0], "hayır (kullanıcı)", RULES["K4"][1]),
    "K5": (RULES["K5"][0], "hayır (kullanıcı)", RULES["K5"][1]),
    "Pattern (canlı kayıt #1)": ("Dibin ≥ 2,15 katı · en likit %30 · gelir büyümesi sırası ≥ %30", "evet",
                                 lambda x: (x.kat >= 2.15) & (x.likidite >= 0.7) & (x.gelir_buyumesi >= 0.3)),
    "En iyi kombinasyon": ("Dibin ≥ 2 katı · gelir ≥ %20 · en likit %30", "evet",
                           lambda x: (x.kat >= 2) & (x.gelir >= 0.2) & (x.likidite >= 0.7)),
    "A (sektör momentumu)": ("En iyi kombinasyon + sektör momentumu en üst %13", "evet",
                             lambda x: (x.kat >= 2) & (x.gelir >= 0.2) & (x.likidite >= 0.7) & (x.sektor_momentum_12_1 >= 0.8694)),
    "B (A + trend)": ("A + 10 haftalık ortalama 40 haftalığın ≥ %19 üstünde", "evet",
                      lambda x: (x.kat >= 2) & (x.gelir >= 0.2) & (x.likidite >= 0.7) & (x.sektor_momentum_12_1 >= 0.8694)
                      & (x.ort_10_40 >= 0.1909)),
    "Momentum (büyük hisseler)": ("Büyük ve likit hisselerde son 1 yılın en güçlü 10'u", "evet", None),  # özel: sıralama
}


def data() -> pd.DataFrame:
    d = history()  # tarih, cik, net, spy, gelir, yillik_gelir, kat, zirveden (+ pattern_avi önbelleği sırası)
    extra = pd.read_parquet(CACHE, columns=["likidite", "gelir_buyumesi", "sektor_momentum_12_1", "ort_10_40", "momentum_12_1",
                                            "kucuk_boyut"])
    for c in extra:
        d[c] = extra[c].to_numpy()
    fr = pd.read_parquet(FRAME, columns=["tarih", "islem_tutari", "getiri_13h", "getiri_26h", "sembol"]).reset_index()
    fr = fr[(fr.islem_tutari >= 1e6) & fr.getiri_13h.notna()][["tarih", "cik", "getiri_13h", "getiri_26h"]]
    d = d.merge(fr, on=["tarih", "cik"], how="left")
    return d


def symbols(p):
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    tick = pd.read_parquet(config.DATA_DIR / "derived" / "identity_tickers.parquet").assign(cik=lambda x: x.cik.astype(str))
    by = {c: g for c, g in tick.groupby("cik")}

    def at(c, t):
        g = by.get(c)
        if g is not None:
            h = g[(g.first_seen <= t + pd.Timedelta(days=45)) & (g.last_seen >= t - pd.Timedelta(days=45))]
            if len(h):
                return h.sort_values("n").ticker.iloc[-1]
        return sec.symbol.get(c, c)
    return at


def main() -> pd.DataFrame:
    p = panel.build()
    d = data()
    sym = symbols(p)
    rng = np.random.default_rng(20261019)
    d["_r"] = rng.random(len(d))  # eşitlikleri rastgele boz (tablo satır sırası geleceği taşır)
    dates = panel.fridays()
    spy = context.etf_prices(dates)["SPY"]
    starts = [t for t in sorted(d.tarih.unique()) if pd.Timestamp(t).month in (1, 4, 7, 10)]
    rows = []
    for t in starts:
        t = pd.Timestamp(t)
        g = d[d.tarih == t]
        i = dates.searchsorted(t)
        s3 = float(spy.iloc[i + 13] / spy.iloc[i] - 1) if i + 13 < len(spy) else np.nan
        s6 = float(spy.iloc[i + 26] / spy.iloc[i] - 1) if i + 26 < len(spy) else np.nan
        top = g.sort_values(["getiri_13h", "_r"], ascending=False).head(3)
        base = {"donem": f"{t.year}-{['', 'Ocak', '', '', 'Nisan', '', '', 'Temmuz', '', '', 'Ekim'][t.month]}", "tarih": str(t.date()),
                "spy_3a": s3, "spy_6a": s6, "evren": len(g)}
        rows.append(base | {"model": "EN YÜKSEK GETİRİ (sonradan bakınca)", "secilen": 3,
                            "hisseler": ", ".join(sym(c, t) for c in top.cik.astype(str)),
                            "ort_3a": top.getiri_13h.mean(), "ort_6a": top.getiri_26h.mean(),
                            "ilk3_3a": top.getiri_13h.mean(), "ilk3_6a": top.getiri_26h.mean(), "veriyi_gordu": "—"})
        top20 = set(g.nlargest(20, "getiri_13h").cik)
        for name, (desc, seen, f) in MODELS.items():
            if f is None:
                big = g[(g.kucuk_boyut <= 0.3) & (g.likidite >= 0.7)]
                sel = big.sort_values(["momentum_12_1", "_r"], ascending=False).head(10)
            else:
                sel = g[f(g).fillna(False)]
            sel = sel.sort_values(["kat", "_r"], ascending=False)
            show = sel.head(3)
            rows.append(base | {"model": name, "secilen": len(sel), "hisseler": ", ".join(sym(c, t) for c in show.cik.astype(str)),
                                "ort_3a": sel.getiri_13h.mean() if len(sel) else np.nan,
                                "ort_6a": sel.getiri_26h.mean() if len(sel) else np.nan,
                                "ilk3_3a": show.getiri_13h.mean() if len(show) else np.nan,
                                "ilk3_6a": show.getiri_26h.mean() if len(show) else np.nan,
                                "ilk20_yakalanan": int(sel.cik.isin(top20).sum()), "veriyi_gordu": seen})
    t = pd.DataFrame(rows)
    t.round(4).to_csv(R / "donem_tablosu.csv", index=False)
    # özet: model başına
    m = t[t.model != "EN YÜKSEK GETİRİ (sonradan bakınca)"]
    summ = m.groupby("model", sort=False).agg(
        donem=("donem", "size"), secim_yapilan=("secilen", lambda s: int((s > 0).sum())), medyan_hisse=("secilen", "median"),
        ort_3a=("ort_3a", "mean"), ort_6a=("ort_6a", "mean"), ilk3_3a=("ilk3_3a", "mean"), ilk3_6a=("ilk3_6a", "mean"),
        spy_ustu_3a=("ort_3a", lambda s: float(np.mean(s.dropna().to_numpy() > m.loc[s.dropna().index, "spy_3a"].to_numpy()))),
        en_iyi_20den_yakalanan=("ilk20_yakalanan", "sum"))
    summ["veriyi_gordu"] = [MODELS[k][1] for k in summ.index]
    o = t[t.model == "EN YÜKSEK GETİRİ (sonradan bakınca)"]
    summ.loc["EN YÜKSEK GETİRİ (sonradan bakınca)"] = [len(o), len(o), 3, o.ort_3a.mean(), o.ort_6a.mean(), o.ort_3a.mean(),
                                                       o.ort_6a.mean(), 1.0, len(o) * 3, "—"]
    summ.loc["S&P 500"] = [len(o), len(o), np.nan, o.spy_3a.mean(), o.spy_6a.mean(), o.spy_3a.mean(), o.spy_6a.mean(), np.nan, np.nan, "—"]
    summ.round(4).to_csv(R / "donem_tablosu_ozet.csv")
    write(t, summ)
    return t


def pct(v):
    return "—" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v * 100:+,.0f}%"


def write(t, summ):
    L = ["# Dönem Karşılaştırma Tablosu (ana analiz yöntemi)", "",
         "Her çeyrek başı: gerçekte en çok kazandıran 3 hisse ve her modelin o gün seçtikleri. Getiriler brüt; 3 ay = 13 hafta, "
         "6 ay = 26 hafta. Model 3'ten fazla hisse seçtiyse ilk 3'ün adı yazılır (sıra: dipten kat), getiri ise seçilen bütün "
         "hisselerin ortalamasıdır. 'Veriyi gördü = evet': kural 2010–2026 verisine bakılarak bulundu (geçmiş sonucu iyimser olabilir).", "",
         "## Özet (bütün dönemler)", "",
         "| Model | Veriyi gördü mü | Seçim yapılan dönem | Medyan hisse | 3 hisse: ort. 3 ay | 3 hisse: ort. 6 ay | Tümü: ort. 3 ay | Tümü: ort. 6 ay | 3 ayda S&P'yi geçtiği dönem | En iyi 20'den yakalanan |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k, r in summ.iterrows():
        L.append(f"| {k} | {r.veriyi_gordu} | {int(r.secim_yapilan)}/{int(r.donem)} | {'' if not np.isfinite(r.medyan_hisse) else int(r.medyan_hisse)} | "
                 f"{pct(r.ilk3_3a)} | {pct(r.ilk3_6a)} | {pct(r.ort_3a)} | {pct(r.ort_6a)} | {pct(r.spy_ustu_3a) if np.isfinite(r.spy_ustu_3a) else '—'} | "
                 f"{'' if not np.isfinite(r.en_iyi_20den_yakalanan) else int(r.en_iyi_20den_yakalanan)} |")
    L += ["", "Not: 'Ort. 3 ay' dönem ortalamasıdır (bileşik değildir); seçim olmayan dönemler ortalamaya girmez.", ""]
    for donem, g in t.groupby("tarih", sort=True):
        g0 = g.iloc[0]
        L += [f"## {g0.donem} ({donem}) — S&P: 3 ay {pct(g0.spy_3a)}, 6 ay {pct(g0.spy_6a)}", "",
              "| Model | Seçilen | 3 hisse | Bu 3'ün 3 ayı | Bu 3'ün 6 ayı | Tüm seçimlerin 3 ayı | Tüm seçimlerin 6 ayı |",
              "|---|---|---|---|---|---|---|"]
        for r in g.itertuples():
            L.append(f"| {r.model} | {r.secilen} | {r.hisseler or '—'} | {pct(r.ilk3_3a)} | {pct(r.ilk3_6a)} | {pct(r.ort_3a)} | {pct(r.ort_6a)} |")
        L.append("")
    (R / "donem_tablosu.md").write_text("\n".join(L))
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()

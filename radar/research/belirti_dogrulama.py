"""Belirti doğrulama paketi: python -m radar.research.belirti_dogrulama

Her belirti için, varsa, şu testler (sonuç: reports/research/belirti_dogrulama.json ve .csv):
T1 tutarlılık   çerçevedeki yüzdelik değer, kaynak geniş tablodan aynı tarih/hisse için yeniden sıralanan değerle örtüşüyor mu
                (tarih kayması, hisse eşleşme hatası). Ölçü: tarih başına Spearman ortalaması ≥ 0,99.
T2 bağımsız     fiyattan türeyen belirtiler, haftalık panelden değil günlük fiyat arşivinden ayrı formülle yeniden hesaplanır.
                Ölçü: tarih başına Spearman ortalaması ≥ 0,90 (günlük/haftalık örnekleme farkı payı).
T3 bilinen      AAPL, MSFT, KO, XOM, NVDA için oranların ham değeri kamuya açık rakamlarla karşılaştırılır (±%35).
T4 zamanlama    pit / weekly / rolling_count mekanizması yapay olaylarla sınanır: değer kabul tarihinden sonraki ilk Cuma'dan
                önce görünmemeli. Ayrıca bölünme testi: hisse sayısı ve piyasa değeri bölünme haftasında sıçramamalı.
T5 sızıntı      belirtinin t→t+1 hafta getirisiyle IC'si, t+1→t+2 hafta IC'sine göre olağan dışı yüksek mi (gelecekten bilgi).
T6 yön          "düşük" ve "küçük" adlı belirtilerde yüksek değer gerçekten düşük ölçüye mi karşılık geliyor.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import panel

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
OUT = config.ROOT / "reports" / "research" / "belirti_dogrulama.json"


def per_date_spearman(a: pd.Series, b: pd.Series, dates: pd.Series) -> float:
    x = pd.DataFrame({"a": a.to_numpy(), "b": b.to_numpy(), "t": dates.to_numpy()}).dropna()
    if x.empty:
        return np.nan
    s = x.groupby("t").apply(lambda g: g.a.corr(g.b, method="spearman") if len(g) > 30 else np.nan)
    return float(s.mean())


def long_at(wide: pd.DataFrame, df: pd.DataFrame) -> pd.Series:
    """Geniş tablodan (tarih × cik) çerçeve satırlarının değerini al."""
    w = wide.copy()
    w.columns = w.columns.astype(str)
    st = w.stack(future_stack=True)
    st.index.names = ["tarih", "cik"]
    key = pd.MultiIndex.from_arrays([df.tarih, df.index.astype(str)])
    return pd.Series(st.reindex(key).to_numpy(), index=df.index)


# --- T1: tutarlılık --------------------------------------------------------------------------------------------
def t1_consistency(df: pd.DataFrame, p: dict, events: set[str]) -> dict[str, dict]:
    from radar.research import hindsight as hs, library, monthly, ratios, sectors, context
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    sources: dict[str, pd.DataFrame] = {}
    for g in library.GROUPS:
        for n, w in library.load_group(g, p).items():
            sources[n] = w.reindex(index=dates, columns=p["price"].columns)
    sources |= {n: w.reindex(dates) for n, w in hs.extra_signals(p).items()}
    sic = sectors.load_sic().reindex(p["price"].columns).fillna("")
    sector = pd.Series([hs.ETF_NAMES.get(context.etf_for_sic(c), "Diğer") for c in sic], index=p["price"].columns)
    extra, _ = monthly.new_features(p, sector)
    sources |= {n: w.reindex(dates) for n, w in extra.items()}
    sources |= {n: w.reindex(dates) for n, w in ratios.signals(p).items()}
    out = {}
    for n, w in sources.items():
        if n not in df:
            continue
        v = long_at(w, df)
        if n in events or n == "bilanco_bu_ay_bekleniyor":
            a = (v.fillna(0) > 0).astype(float) if n != "bilanco_bu_ay_bekleniyor" else v
            ok = float((a.fillna(-1) == df[n].fillna(-1)).mean())
            out[n] = {"olcu": round(ok, 4), "gecti": ok >= 0.99, "tur": "olay eşleşmesi"}
        else:
            r = per_date_spearman(v, df[n], df.tarih)
            out[n] = {"olcu": round(r, 4), "gecti": bool(r >= 0.99), "tur": "Spearman"}
    return out


# --- T2: günlük fiyattan bağımsız yeniden hesap ---------------------------------------------------------------
def t2_independent(df: pd.DataFrame, p: dict) -> dict[str, dict]:
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str))
    act = sec[sec.status == "aktif"].drop_duplicates("symbol")[["symbol", "cik"]]
    d = archive.load("prices", columns=["symbol", "date", "close", "adjclose", "split_ratio"]).merge(act, on="symbol")
    # Yahoo 'close' bölünmeye göre düzeltilmiştir; gerçek işlem fiyatı için sonraki bölünmelerin çarpımıyla geri çevrilir
    d = d.sort_values(["cik", "date"])
    r = d.split_ratio.where((d.split_ratio > 0) & np.isfinite(d.split_ratio), 1.0).fillna(1.0)
    after = r[::-1].groupby(d.cik[::-1]).cumprod()[::-1] / r  # bu günden SONRAKİ bölünmelerin çarpımı
    d["close"] = d.close * after
    adj = d.pivot_table(index="date", columns="cik", values="adjclose", aggfunc="last").sort_index()
    close = d.pivot_table(index="date", columns="cik", values="close", aggfunc="last").sort_index()
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    # t tarihinde (Cuma) bilinen son kapanış: t dahil
    at = lambda wide, lag_days: wide.reindex(wide.index.union(dates - pd.Timedelta(days=lag_days))).ffill().reindex(dates - pd.Timedelta(days=lag_days))
    now = at(adj, 0).set_axis(dates)
    m4 = at(adj, 28).set_axis(dates)
    m52 = at(adj, 364).set_axis(dates)
    m26 = at(adj, 182).set_axis(dates)
    hi = adj.rolling(252, min_periods=120).max()
    hi = hi.reindex(hi.index.union(dates)).ffill().reindex(dates)
    dret = adj.pct_change(fill_method=None)
    vol = dret.rolling(126, min_periods=60).std()
    vol = vol.reindex(vol.index.union(dates)).ffill().reindex(dates)
    raw = at(close, 0).set_axis(dates)
    indep = {
        "momentum_12_1": m4 / m52 - 1,
        "getiri_1a": now / m4 - 1,
        "getiri_6a": at(adj, 7).set_axis(dates) / m26 - 1,
        "zirveye_yakinlik_52h": now / hi,
        "dusuk_oynaklik": -vol,
        "fiyat_seviyesi": raw,
    }
    out = {}
    sub = df[df.index.astype(str).isin(set(act.cik))]
    for n, w in indep.items():
        if n in df:
            r = per_date_spearman(long_at(w, sub), sub[n], sub.tarih)
            out[n] = {"olcu": round(r, 4), "gecti": bool(r >= 0.90), "tur": "günlük fiyattan Spearman"}
    return out


# --- T3: bilinen değerler --------------------------------------------------------------------------------------
# (cik, tarih, belirti) → beklenen yaklaşık değer (kamuya açık raporlardan; o tarihte bilinen son yıllık rapor)
KNOWN = [
    ("320193", "2020-01-03", "kazanc_getirisi", 55.3 / 1300), ("320193", "2020-01-03", "brut_marj", 0.378),
    ("320193", "2020-01-03", "faaliyet_marji", 0.246), ("320193", "2020-01-03", "temettu_verimi", 14.1 / 1300),
    ("320193", "2020-01-03", "cari_oran", 1.54), ("320193", "2020-01-03", "piyasa_degeri", 1.30e12),
    ("789019", "2020-01-03", "kazanc_getirisi", 39.2 / 1210), ("789019", "2020-01-03", "brut_marj", 0.659),
    ("789019", "2020-01-03", "faaliyet_marji", 0.341), ("789019", "2020-01-03", "piyasa_degeri", 1.21e12),
    ("21344", "2020-01-03", "temettu_verimi", 0.029), ("21344", "2020-01-03", "brut_marj", 0.64),
    ("21344", "2020-01-03", "piyasa_degeri", 2.37e11),
    ("34088", "2023-01-06", "kazanc_getirisi", 23.0 / 450), ("34088", "2023-01-06", "temettu_verimi", 0.033),
    ("34088", "2023-01-06", "piyasa_degeri", 4.5e11),
    ("1045810", "2024-01-05", "piyasa_degeri", 1.21e12), ("1045810", "2024-07-05", "piyasa_degeri", 3.08e12),
    ("1045810", "2024-07-05", "kazanc_getirisi", 29.8 / 3080), ("1045810", "2024-07-05", "hisse_sayisi_degisimi", 0.0),
    ("1045810", "2024-10-04", "hisse_sayisi_degisimi", 0.0), ("320193", "2020-10-02", "hisse_sayisi_degisimi", -0.05),
]


def t3_known(p: dict) -> list[dict]:
    from radar.research import fundamentals, ratios
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    ciks = sorted({k[0] for k in KNOWN})
    dts = pd.DatetimeIndex(sorted({pd.Timestamp(k[1]) for k in KNOWN}))
    sub = {"price": p["price"][ciks], "raw": p["raw"][ciks]}
    rs = ratios.signals(sub)
    from radar.research.road1 import signals as r1
    r1s = r1(sub)
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    shares = fundamentals.shares_wide(sh, sub["price"], sub["raw"])
    mcap = shares * sub["raw"]
    src = rs | {k: v for k, v in r1s.items() if k in ("kazanc_getirisi",)} | {"piyasa_degeri": mcap}
    out = []
    for cik, t, n, exp in KNOWN:
        w = src[n]
        i = w.index.searchsorted(pd.Timestamp(t), side="right") - 1
        got = float(w[cik].iloc[i]) if cik in w and i >= 0 else np.nan
        if exp == 0 or exp < 0:
            ok = bool(np.isfinite(got) and abs(got - exp) <= 0.1)
        else:
            ok = bool(np.isfinite(got) and abs(got / exp - 1) <= 0.35)
        out.append({"cik": cik, "tarih": t, "belirti": n, "beklenen": exp, "bulunan": got, "gecti": ok})
    return out


# --- T4: zamanlama --------------------------------------------------------------------------------------------
def t4_timing() -> list[dict]:
    from radar.research.pit import pit, rolling_count, to_friday
    dates = pd.date_range("2020-01-03", periods=12, freq="W-FRI")
    cols = pd.Index(["1"])
    tests = []
    # Çarşamba 17:30 kabul → o haftanın Cuma'sı (2 gün sonra) görünür; Cuma 18:00 kabul → bir sonraki Cuma
    for acc, first in (("2020-01-15 17:30", "2020-01-17"), ("2020-01-17 18:00", "2020-01-24"), ("2020-01-17 09:00", "2020-01-24")):
        ev = pd.DataFrame({"cik": ["1"], "date": [pd.Timestamp(acc)], "value": [5.0]})
        w = pit(ev, dates, cols, 400)["1"]
        seen = w.dropna().index.min()
        tests.append({"test": f"pit: kabul {acc} → ilk görünme {seen.date() if pd.notna(seen) else None}",
                      "gecti": bool(pd.notna(seen) and seen == pd.Timestamp(first) and seen > pd.Timestamp(acc))})
        c = rolling_count(ev[["cik", "date"]], dates, cols, 90)["1"]
        seen_c = c[c > 0].index.min()
        tests.append({"test": f"olay sayacı: kabul {acc} → ilk görünme {seen_c.date() if pd.notna(seen_c) else None}",
                      "gecti": bool(pd.notna(seen_c) and seen_c > pd.Timestamp(acc))})
    return tests


def t4_split(p: dict) -> list[dict]:
    """Bölünme haftasında hisse sayısı × fiyat (piyasa değeri) ve hisse sayısı değişimi sıçramamalı."""
    from radar.research import fundamentals
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    cases = [("1045810", "2024-06-10", 10), ("1045810", "2021-07-20", 4), ("320193", "2020-08-31", 4), ("1318605", "2020-08-31", 5),
             ("1018724", "2022-06-06", 20), ("1652044", "2022-07-18", 20)]
    ciks = sorted({c[0] for c in cases} & set(p["price"].columns))
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    shares = fundamentals.shares_wide(sh, p["price"][ciks], p["raw"][ciks])
    mcap = shares * p["raw"][ciks]
    out = []
    for cik, day, ratio in cases:
        if cik not in ciks:
            continue
        i = p["price"].index.searchsorted(pd.Timestamp(day))
        before, after = mcap[cik].iloc[i - 1], mcap[cik].iloc[i + 2]
        chg = after / before - 1 if before else np.nan
        out.append({"test": f"piyasa değeri bölünme ({cik}, {day}, {ratio}:1): önce {before / 1e9:,.0f} mr $, sonra {after / 1e9:,.0f} mr $",
                    "gecti": bool(np.isfinite(chg) and abs(chg) < 0.5)})
    return out


# --- T5: sızıntı ----------------------------------------------------------------------------------------------
def t5_leak(df: pd.DataFrame, p: dict, feats: list[str]) -> dict[str, dict]:
    price = p["price"]
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    i = price.index.get_indexer(dates)
    ok = (i >= 0) & (i + 2 < len(price.index))
    dates, i = dates[ok], i[ok]
    r1 = pd.DataFrame(price.iloc[i + 1].to_numpy() / price.iloc[i].to_numpy() - 1, index=dates, columns=price.columns)
    r2 = pd.DataFrame(price.iloc[i + 2].to_numpy() / price.iloc[i + 1].to_numpy() - 1, index=dates, columns=price.columns)
    sub = df[df.tarih.isin(dates)]
    a1, a2 = long_at(r1, sub), long_at(r2, sub)
    out = {}
    for n in feats:
        ic1 = per_date_spearman(sub[n], a1, sub.tarih)
        ic2 = per_date_spearman(sub[n], a2, sub.tarih)
        bad = bool(np.isfinite(ic1) and abs(ic1) > 0.06 and abs(ic1) > 2.5 * abs(ic2) + 0.03)
        out[n] = {"ic_1hafta": round(ic1, 4) if np.isfinite(ic1) else None, "ic_2hafta": round(ic2, 4) if np.isfinite(ic2) else None,
                  "gecti": not bad}
    return out


# --- T6: yön --------------------------------------------------------------------------------------------------
def t6_direction(df: pd.DataFrame, p: dict) -> dict[str, dict]:
    from radar.research import fundamentals
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    price = p["price"]
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    wret = price / price.shift(1) - 1
    vol = wret.rolling(26, min_periods=13).std().reindex(dates)
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    shares = fundamentals.shares_wide(sh, price, p["raw"])
    mcap = (shares * p["raw"]).reindex(dates)
    out = {}
    for n, ref, want in (("dusuk_oynaklik", vol, -1), ("kucuk_boyut", mcap, -1), ("ivol_3a", vol, 1), ("max_gunluk_1a", vol, 1)):
        if n in df:
            r = per_date_spearman(df[n], long_at(ref, df), df.tarih)
            out[n] = {"olcu": round(r, 3), "gecti": bool(np.sign(r) == want and abs(r) > 0.3),
                      "tur": f"ölçüyle {'ters' if want < 0 else 'aynı'} yönde olmalı"}
    return out


def main() -> dict:
    df = pd.read_parquet(FRAME)
    meta = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari", "getiri_13h", "getiri_26h", "getiri_52h", "getiri_104h"}
    feats = [c for c in df.columns if c not in meta and pd.api.types.is_numeric_dtype(df[c])]
    events = set(json.loads(FRAME.with_name("aylik_cerceve_olaylar.json").read_text()))
    p = panel.build()
    res = {}
    for name, fn in (("T4_zamanlama", lambda: t4_timing()), ("T4_bolunme", lambda: t4_split(p)),
                     ("T3_bilinen", lambda: t3_known(p)), ("T6_yon", lambda: t6_direction(df, p)),
                     ("T2_bagimsiz", lambda: t2_independent(df, p)), ("T5_sizinti", lambda: t5_leak(df, p, feats)),
                     ("T1_tutarlilik", lambda: t1_consistency(df, p, events))):
        try:
            res[name] = fn()
        except Exception as e:  # bir testin hatası diğerlerini durdurmasın
            res[name] = {"hata": f"{type(e).__name__}: {e}"}
        print(f"=== {name}", flush=True)
        r = res[name]
        if isinstance(r, list):
            for x in r:
                print(("GEÇTİ " if x["gecti"] else "KALDI ") + json.dumps({k: v for k, v in x.items() if k != "gecti"}, ensure_ascii=False, default=str), flush=True)
        elif "hata" in r:
            print("HATA", r["hata"], flush=True)
        else:
            bad = {k: v for k, v in r.items() if not v["gecti"]}
            print(f"{len(r) - len(bad)}/{len(r)} geçti; kalanlar: {json.dumps(bad, ensure_ascii=False, default=str)}", flush=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return res


if __name__ == "__main__":
    main()

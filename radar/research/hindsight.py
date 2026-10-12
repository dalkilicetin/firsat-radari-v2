"""Geriye bakış: her yıl başında (ilk Cuma) yatırılabilir faaliyet şirketlerinin sonraki 52 haftası.

1. "Ne olmalıydı?": en çok kazandıranlar, S&P 500'ün (SPY) üstünde / altında bitirenler, asla alınmaması
   gerekenler (−%50 ve altı, iflas).
2. "Neden?": kazananların (en iyi %10) ve kaybedenlerin (en kötü %10) yıl başındaki sinyal profilleri.
   Her sinyal için: kazanan/kaybeden oranının genele göre katı (sinyal en yüksek %20'deyken), yön tutarlılığı
   (kaç yılda kazananların ortalaması kaybedenlerinkinden yüksek). Olaylarda: olay varken kazanan/kaybeden olma katı.
Sinyaller yalnızca yıl başında bilinen değerlerdir (aynı nokta-zaman kuralı). Kilitli yıllar (2023–2025) son testten
sonra eklenir.
"""

from __future__ import annotations

import os

from dataclasses import dataclass

import numpy as np
import pandas as pd

from radar.research import context, library, panel, sectors

YEARS = tuple(range(2010, 2023))
TOP = 0.10  # kazanan / kaybeden dilimi
ETF_NAMES = {"SMH": "Yarı iletken", "IGV": "Yazılım", "XBI": "Biyoteknoloji", "XLV": "Sağlık", "XLE": "Enerji",
             "ITA": "Savunma/havacılık", "GDX": "Madencilik", "XLU": "Kamu hizmetleri", "XHB": "İnşaat",
             "JETS": "Havayolu", "XRT": "Perakende", "XLY": "Tüketici", "XLF": "Finansal hizmet", "XLRE": "Gayrimenkul",
             "XLC": "İletişim/medya", "XLP": "Temel tüketim", "XLB": "Hammadde", "XLI": "Sanayi", "XLK": "Teknoloji donanım",
             "IWM": "Diğer"}


@dataclass
class YearResult:
    year: int
    date: pd.Timestamp
    table: pd.DataFrame        # hisse başına: sembol, ad, sektör, getiri, SPY'ye göre, sınıf, çıkış
    summary: dict


def extra_signals(p: dict) -> dict[str, pd.DataFrame]:
    """Yalnızca analiz için ek fiyat/hacim özellikleri (modelde henüz yok)."""
    price, raw, dv = p["price"], p["raw"], p["dollar_volume"]
    return {
        "zirveye_yakinlik_52h": price / price.rolling(52, min_periods=26).max(),
        "getiri_6a": price.shift(1) / price.shift(26) - 1,
        "getiri_1a": price / price.shift(4) - 1,
        "hacim_artisi": dv / dv.shift(26),
        "fiyat_seviyesi": raw,
    }


def prepare():
    p = panel.build()
    sigs = {n: df for n, (_, df) in library.load_all(p).items()}
    sigs |= extra_signals(p)
    unis = sectors.operating_universes(p)
    inv = unis[[k for k in unis if k != "tümü"][0]]
    floor = float(os.environ.get("RADAR_MIN_PRICE", "5"))
    if floor != 5:  # deneme: fiyat tabanı (ör. 1 $) — büyük kazananların bir kısmı yıl başında 5 $'ın altında
        dv = p["dollar_volume"]
        inv = unis["tümü"] & (p["raw"] >= floor) & ((dv >= 1e6) | dv.isna())
    etf = context.etf_prices(p["price"].index)
    sic = sectors.load_sic().reindex(p["price"].columns).fillna("")
    sector = pd.Series([ETF_NAMES.get(context.etf_for_sic(c), "Diğer") for c in sic], index=p["price"].columns)
    return p, sigs, inv, etf, sector


def year_tables(p, inv, etf, sector) -> list[YearResult]:
    price, sec, dates = p["price"], p["securities"], p["price"].index
    fwd = panel.forward_returns(price, sec, 52).reindex(dates)
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").reindex(price.columns)
    out = []
    for y in YEARS:
        t = int(np.flatnonzero(dates >= pd.Timestamp(f"{y}-01-01"))[0])
        d = dates[t]
        u = inv.iloc[t]
        r = fwd.iloc[t][u].dropna()
        spy = float(etf["SPY"].iloc[t + 52] / etf["SPY"].iloc[t] - 1)
        qqq = float(etf["QQQ"].iloc[t + 52] / etf["QQQ"].iloc[t] - 1)
        end = d + pd.Timedelta(weeks=52)
        exited = s.end.reindex(r.index).between(d, end)
        bankrupt = exited & s.bankrupt.reindex(r.index).fillna(False).astype(bool)
        tab = pd.DataFrame({
            "sembol": s.symbol.reindex(r.index), "sirket": s.name.reindex(r.index).str.replace(r" - .*$", "", regex=True),
            "sektor": sector.reindex(r.index), "fiyat": p["raw"].iloc[t].reindex(r.index), "getiri": r,
            "spy_farki": r - spy, "cikis": np.where(bankrupt, "iflas", np.where(exited, "borsadan çıktı", ""))})
        tab["sinif"] = np.select([r >= 1.0, r <= -0.5, r > spy], ["çok kazandıran", "asla alınmamalı", "piyasanın üstünde"],
                                 "piyasanın altında")
        q = r.rank(pct=True)
        tab["dilim"] = np.select([q > 1 - TOP, q <= TOP], ["kazanan", "kaybeden"], "orta")
        out.append(YearResult(y, d, tab.sort_values("getiri", ascending=False), {
            "hisse": len(r), "spy": spy, "qqq": qqq, "medyan": float(r.median()), "ortalama": float(r.mean()),
            "spy_ustu": int((r > spy).sum()), "spy_alti": int((r <= spy).sum()), "yuz_ustu": int((r >= 1).sum()),
            "elli_kayip": int((r <= -0.5).sum()), "iflas": int(bankrupt.sum()), "cikis": int(exited.sum())}))
    return out


def is_event(df: pd.DataFrame) -> bool:
    v = df.stack().dropna()
    v = v.sample(min(len(v), 200_000), random_state=0) if len(v) else v
    return len(v) > 0 and set(np.unique(np.round(v.to_numpy(), 6))) <= {0.0, 1.0}


def signal_study(results: list[YearResult], sigs: dict[str, pd.DataFrame], dates) -> tuple[pd.DataFrame, dict]:
    """Her sinyal × yıl: kazanan/kaybeden ayırt etme gücü. Döner: özet tablo, yıl başı yüzdelikler."""
    rows, pcts = [], {}
    events = {n for n, df in sigs.items() if is_event(df)}
    for res in results:
        t = dates.get_loc(res.date)
        tab = res.table
        win, lose = tab.dilim == "kazanan", tab.dilim == "kaybeden"
        pw, pl = win.mean(), lose.mean()
        P = {}
        for n, df in sigs.items():
            v = df.iloc[t].reindex(tab.index)
            if n in events:
                has = v.fillna(0) > 0
                P[n] = has.astype(float)
                if has.sum() < 5:
                    continue
                rows.append({"sinyal": n, "tur": "olay", "yil": res.year, "kapsam": float(has.mean()),
                             "kazanan_kat": win[has].mean() / pw, "kaybeden_kat": lose[has].mean() / pl,
                             "yon": np.sign(tab.getiri[has].median() - tab.getiri.median())})
            else:
                pct = v.rank(pct=True)
                P[n] = pct
                ok = pct.notna()
                if ok.sum() < 200:
                    continue
                hi, lo = pct >= 0.8, pct <= 0.2
                rows.append({"sinyal": n, "tur": "sürekli", "yil": res.year, "kapsam": float(ok.mean()),
                             "kazanan_kat": win[hi].mean() / win[ok].mean(), "kaybeden_kat": lose[hi].mean() / lose[ok].mean(),
                             "kazanan_kat_dusuk": win[lo].mean() / win[ok].mean(), "kaybeden_kat_dusuk": lose[lo].mean() / lose[ok].mean(),
                             "yon": np.sign(pct[win].mean() - pct[lose].mean())})
        pcts[res.year] = pd.DataFrame(P)
    df = pd.DataFrame(rows)
    agg = df.groupby(["sinyal", "tur"]).agg(
        yil=("yil", "size"), kapsam=("kapsam", "mean"), kazanan_kat=("kazanan_kat", "mean"),
        kaybeden_kat=("kaybeden_kat", "mean"), kazanan_kat_dusuk=("kazanan_kat_dusuk", "mean"),
        kaybeden_kat_dusuk=("kaybeden_kat_dusuk", "mean"),
        yon_yukari=("yon", lambda s: int((s > 0).sum())), yon_asagi=("yon", lambda s: int((s < 0).sum()))).reset_index()
    agg["tutarlilik"] = agg[["yon_yukari", "yon_asagi"]].max(axis=1) / agg.yil
    return agg, {"yillik": df, "yuzdelik": pcts, "olaylar": events}


def profiles(res: YearResult, pct: pd.DataFrame, events: set[str], n: int = 10) -> pd.DataFrame:
    """En iyi ve en kötü n hisse: yıl başında en uç olan sinyalleri (yüzdelik ≥ 90 / ≤ 10) ve olaylar."""
    rows = []
    for label, sub in (("kazanan", res.table.head(n)), ("kaybeden", res.table.tail(n).iloc[::-1])):
        for cik, r in sub.iterrows():
            p = pct.loc[cik] if cik in pct.index else pd.Series(dtype=float)
            cont_all = p.drop([e for e in events if e in p.index], errors="ignore")
            cont = cont_all.dropna()
            high = cont[cont >= 0.9].sort_values(ascending=False).index.tolist()
            low = cont[cont <= 0.1].sort_values().index.tolist()
            ev = [e for e in events if p.get(e, 0) > 0]
            rows.append({"grup": label, "sembol": r.sembol, "sirket": r.sirket, "sektor": r.sektor, "getiri": r.getiri,
                         "cikis": r.cikis, "yuksek": high, "dusuk": low, "olaylar": ev,
                         "veri_kapsami": float(cont_all.notna().mean()) if len(cont_all) else 0.0})
    return pd.DataFrame(rows)

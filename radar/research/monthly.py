"""Aylık belirti çerçevesi: python -m radar.research.monthly

Her ayın ilk Cuması (2010→) için: alınabilir faaliyet şirketleri × o gün bilinen bütün belirtiler (yıl içi yüzdelik değil,
o ayın kesitindeki yüzdelik; olaylar 0/1) + haber konusu belirtileri (2015→) + sonraki 4 haftanın getirisi
(arada borsadan çıkanlar çıkış değeriyle, iflas 0).
Çıktı: data/derived/aylik_cerceve.parquet, data/derived/aylik_cerceve_olaylar.json (hedef arama motoru okur).
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import hindsight as hs
from radar.research import news_topics, panel, road4

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
EVENTS = config.ROOT / "data" / "derived" / "aylik_cerceve_olaylar.json"
H = 4  # hafta


def new_features(p: dict, sector: pd.Series) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Aylık ufka özgü yeni belirtiler (hisse × hafta) ve piyasa rejimi (hafta × özellik; bütün hisseler için aynı)."""
    from radar.research import context
    from radar.research.pit import to_friday
    from radar import archive
    price, dv = p["price"], p["dollar_volume"]
    wret = price / price.shift(1) - 1
    r4 = price / price.shift(4) - 1
    # Bilanço yaklaşıyor: son 8-K 2.02'den bu yana geçen hafta (≈13 haftada bir açıklanır; 9–13 hafta → bu ay açıklama beklenir)
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    e = f[(f.form == "8-K") & f["items"].fillna("").str.contains(r"\b2\.02\b")][["cik", "filing_date"]].copy()
    e = e.assign(date=to_friday(e.filing_date), cik=e.cik.astype(str))
    e = e[e.cik.isin(set(price.columns)) & e.date.isin(price.index)].drop_duplicates(["cik", "date"])
    mark = pd.DataFrame(0.0, index=price.index, columns=price.columns)
    for c, g in e.groupby("cik"):
        mark.loc[g.date, c] = 1.0
    week_no = pd.Series(np.arange(len(price.index)), index=price.index)
    last = mark.mul(week_no, axis=0).where(mark > 0).ffill(limit=26)
    since = (-last).add(week_no, axis=0)
    # Sektör yayılımı: aynı sektördeki hisselerin son 4 hafta ortalaması − hissenin kendi 4 haftası
    sect = sector.reindex(price.columns)
    sec_mean = r4.T.groupby(sect.to_numpy()).transform("mean").T
    out = {
        "bilanco_uzerinden_hafta": since,
        "bilanco_bu_ay_bekleniyor": ((since >= 9) & (since <= 13)).astype(float).where(since.notna()),
        "sektor_4h": sec_mean,
        "sektorun_gerisinde": sec_mean - r4,
        "oynaklik_genislemesi": wret.rolling(4, min_periods=3).std() / wret.rolling(26, min_periods=13).std(),
        "max_haftalik_4h": wret.rolling(4, min_periods=2).max(),
        "kirilim": (price / price.rolling(52, min_periods=26).max()) * (dv / dv.shift(13)),
    }
    etf = context.etf_prices(price.index)
    spy = etf["SPY"]
    wspy = spy / spy.shift(1) - 1
    reg = pd.DataFrame({"piyasa_4h": spy / spy.shift(4) - 1, "piyasa_52h": spy / spy.shift(52) - 1,
                        "piyasa_oynaklik_13h": wspy.rolling(13, min_periods=8).std()}, index=price.index)
    return out, reg


def month_starts(dates: pd.DatetimeIndex, h: int = H) -> list[int]:
    s = pd.Series(range(len(dates)), index=dates)
    first = s.groupby(dates.to_period("M")).min()
    return [int(i) for i in first.to_numpy() if dates[i].year >= 2010 and i + h < len(dates)]


def main(freq: str = "aylik", first: int = 2010, last: int = 2100) -> pd.DataFrame:
    """freq: 'aylik' (her ayın ilk Cuması, 4 hafta getiri) ya da 'haftalik' (her Cuma, 1 hafta getiri; first–last yılları)."""
    t0 = time.time()
    h = H if freq == "aylik" else 1
    out_path = FRAME if freq == "aylik" else FRAME.with_name("haftalik_cerceve.parquet")
    p, sigs, inv, etf, sector = hs.prepare()
    price, sec, dates = p["price"], p["securities"], p["price"].index
    fwd = panel.forward_returns(price, sec, h).reindex(dates)
    idx = month_starts(dates) if freq == "aylik" else [i for i in range(len(dates) - h) if first <= dates[i].year <= last]
    events = sorted(n for n, df in sigs.items() if hs.is_event(df)) + ["bilanco_bu_ay_bekleniyor"]
    day, pairs = road4.load_themes()
    news = news_topics.features(day, pairs, dates[idx], price.columns)
    extra, reg = new_features(p, sector)
    rising = news_topics.rising_topics(day, pairs, dates[idx], price.columns)
    (out_path.parent / f"yukselen_konular_{freq}.json").write_text(json.dumps(rising.pop("_secilen_konular"), ensure_ascii=False, indent=0))
    news |= rising
    dv = p["dollar_volume"]
    print(f"hazır ({round(time.time() - t0)} sn), {len(idx)} ay, {len(sigs)} belirti + {len(news)} haber belirtisi", flush=True)
    sym = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
    rows = []
    for t in idx:
        d = dates[t]
        u = inv.iloc[t]
        r = fwd.iloc[t][u].dropna()
        if len(r) < 200:
            continue
        f = {"tarih": d, "yil": d.year, "getiri": r.to_numpy(), "sektor": sector.reindex(r.index).to_numpy(),
             "sembol": sym.reindex(r.index).to_numpy(), "islem_tutari": dv.iloc[t].reindex(r.index).to_numpy()}
        for n, df in sigs.items():
            v = df.iloc[t].reindex(r.index)
            f[n] = ((v.fillna(0) > 0).astype(np.float32) if n in events else v.rank(pct=True).astype(np.float32)).to_numpy()
        for n, df in news.items():
            f[n] = df.loc[d].reindex(r.index).rank(pct=True).astype(np.float32).to_numpy()
        for n, df in extra.items():
            f[n] = (df.iloc[t].reindex(r.index) if n == "bilanco_bu_ay_bekleniyor"
                    else df.iloc[t].reindex(r.index).rank(pct=True)).astype(np.float32).to_numpy()
        f["likidite"] = dv.iloc[t].reindex(r.index).rank(pct=True).astype(np.float32).to_numpy()
        # Haber–fiyat ayrışması: haber hacmi hızlanıyor, fiyat son 4 haftada henüz tepki vermemiş
        f["haber_fiyat_ayrismasi"] = f["haber_hacmi_ivme"] - f["getiri_1a"]
        for n in reg:  # piyasa rejimi: bütün hisseler için aynı ham değer (öğrenen model etkileşim kurabilsin)
            f[n] = np.full(len(r), reg[n].iloc[t], dtype=np.float32)
        rows.append(pd.DataFrame(f, index=r.index))
    df = pd.concat(rows)
    df.index.name = "cik"
    FRAME.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path)
    EVENTS.write_text(json.dumps(events, ensure_ascii=False))
    print(f"{len(df):,} satır, {df.tarih.nunique()} dönem ({round(time.time() - t0)} sn) → {out_path}")
    return df


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "haftalik":
        main("haftalik", int(sys.argv[2]) if len(sys.argv) > 2 else 2013, int(sys.argv[3]) if len(sys.argv) > 3 else 2021)
    else:
        main()

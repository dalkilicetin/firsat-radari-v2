"""Haftalık fiyat paneli (Cuma kapanışları), borsadan çıkan hisseler dahil.

- Aktif hisseler: Yahoo temettü ve bölünmeye göre düzeltilmiş kapanış.
- Çıkan hisseler: SEC FTD fiyatları (seyrek, ham). Ters bölünmeler (fiyatın bir günde tam sayı katına
  sıçraması) sezgisel olarak düzeltilir; gerçek çöküşleri silmemek için ileri bölünmelere dokunulmaz.
- Bir fiyat en fazla STALE_DAYS gün eski olabilir; daha eskiyse o hafta "işlem görmüyor" sayılır.
- Üyelik: kimlik katmanındaki [start, end] aralığı.
- İleri getiri: t'den t+h'ye. Hisse arada çıktıysa çıkış değeri kullanılır (iflasta 0, değilse son fiyat)
  ve sonrası nakit kabul edilir.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive, config
from radar.identity import build as build_identity

STALE_DAYS = 30
HORIZONS = {"1h": 1, "1a": 4, "3a": 13, "6a": 26, "1y": 52}  # hafta
REVERSE_SPLIT_FACTORS = np.array([4, 5, 8, 10, 12, 15, 20, 25, 30, 35, 40, 50, 60, 75, 80, 100, 150, 200, 250, 500])
CACHE = config.DATA_DIR / "derived"


def fridays(start="2009-01-02", end=None) -> pd.DatetimeIndex:
    end = end or pd.Timestamp.today().normalize()
    return pd.date_range(start, end, freq="W-FRI")


def adjust_reverse_splits(px: np.ndarray) -> np.ndarray:
    """Tarihe göre sıralı ham seyrek fiyat dizisinde ters bölünmeleri geriye dönük düzeltir."""
    px = np.asarray(px, dtype=float)
    factor = np.ones(len(px))
    for i in range(1, len(px)):
        r = px[i] / px[i - 1]
        if np.isfinite(r) and r >= 3.5:
            k = REVERSE_SPLIT_FACTORS[np.argmin(np.abs(REVERSE_SPLIT_FACTORS - r))]
            if abs(r / k - 1) < 0.08:
                factor[:i] *= k  # bölünme öncesi fiyatları yeni ölçeğe taşı
    return px * factor


def unsplit_factor(daily: pd.DataFrame) -> np.ndarray:
    """Her satır için: aynı sembolde o tarihten SONRA gerçekleşen bölünme oranlarının çarpımı (bölünme günü dahil değil)."""
    d = daily[["symbol", "date", "split_ratio"]].copy()
    d["r"] = d.split_ratio.where(d.split_ratio > 0).fillna(1.0)
    d = d.sort_values(["symbol", "date"], ascending=[True, False])
    after = d.groupby("symbol").r.cumprod() / d.r  # tersten kümülatif çarpım, kendi günü hariç
    return after.reindex(daily.index).to_numpy()


def weekly_last(df: pd.DataFrame, value: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Uzun tablo (cik, date, value) → geniş tablo: her Cuma için o güne kadarki son değer (STALE_DAYS sınırlı)."""
    wide = df.pivot_table(index="date", columns="cik", values=value, aggfunc="last").sort_index()
    idx = wide.index.union(dates)
    raw = wide.reindex(idx)
    filled = raw.ffill()
    # Son gözlemden bu yana geçen gün: gözlem tarihini ileri taşıyarak hesaplanır.
    obs_date = pd.DataFrame(np.where(raw.notna(), idx.values[:, None], np.datetime64("NaT", "ns")),
                            index=idx, columns=wide.columns).ffill()
    age_days = (idx.values[:, None] - obs_date.values.astype("datetime64[ns]")) / np.timedelta64(1, "D")
    return filled.mask(age_days > STALE_DAYS).reindex(dates)


def build(force: bool = False) -> dict[str, pd.DataFrame]:
    """price: düzeltilmiş kapanış (getiri için); raw: ham kapanış (düşük fiyat riski için);
    dollar_volume: 13 haftalık medyan günlük işlem tutarı (Yahoo serisi olanlar; FTD'de hacim yok)."""
    names = ["price", "raw", "dollar_volume"]
    paths = {n: CACHE / f"panel_{n}.parquet" for n in names}
    ident = build_identity()
    sec = ident["securities"]
    if all(p.exists() for p in paths.values()) and not force:
        return {n: pd.read_parquet(p) for n, p in paths.items()} | {"securities": sec}

    dates = fridays()
    active = sec[sec.status == "aktif"]
    daily = archive.load("prices", columns=["symbol", "date", "adjclose", "close", "volume", "split_ratio"])
    daily = daily.merge(active[["symbol", "cik"]], on="symbol")
    daily["dollar_volume"] = daily.close * daily.volume  # ikisi de bölünmeye göre düzeltilmiş; çarpım gerçek işlem tutarıdır
    px = daily.rename(columns={"adjclose": "price"})[["cik", "date", "price"]]
    # Yahoo "close" sonraki bölünmelere göre düzeltilmiştir (WKHS 2020 başı 9.210 $, NVDA 2015 0,5 $ görünür).
    # O gün gerçekten işlem gören fiyat: close × o tarihten sonraki bölünme oranlarının çarpımı.
    raw_px = daily.assign(price=daily.close * unsplit_factor(daily))[["cik", "date", "price"]]
    dv = (daily.sort_values("date").groupby("cik", group_keys=False)
          .apply(lambda g: g.set_index("date").dollar_volume.rolling("91D").median().reset_index().assign(cik=g.name)))

    gone = sec[sec.status == "çıktı"]
    ftd = archive.load("ftd", columns=["settle_date", "symbol", "price"])
    ftd = ftd[ftd.price > 0].merge(gone[["symbol", "cik", "start", "end"]], on="symbol")
    # Sembol yeniden kullanılmış olabilir: yalnızca üyelik aralığı (+10 gün) içindeki gözlemler.
    ftd = ftd[(ftd.settle_date >= ftd.start - pd.Timedelta(days=60)) & (ftd.settle_date <= ftd.end + pd.Timedelta(days=10))]
    # FTD fiyatı takas tarihinden önceki işlem gününün kapanışıdır.
    ftd["date"] = ftd.settle_date - pd.offsets.BDay(1)
    # Aynı sembolün aynı günkü fiyatı tek şirkete ait olmalı (ör. ZYME: eski ve yeniden kurulan şirket; eski şirketin sembolünü
    # sonradan alan SPAC). Aktif hissenin Yahoo fiyatı varsa o gün FTD gözlemi atılır; yoksa başlangıcı en yakın olan alır.
    # Tatile denk gelen tek tük günler de kaçmasın diye: aktif hissenin Yahoo verisinin kapsadığı aralıktaki bütün FTD gözlemleri.
    span = daily[daily.symbol.isin(set(ftd.symbol))].groupby("symbol").date.agg(["min", "max"])
    lo, hi = ftd.symbol.map(span["min"]), ftd.symbol.map(span["max"])
    ftd = ftd[~((ftd.date >= lo - pd.Timedelta(days=7)) & (ftd.date <= hi + pd.Timedelta(days=7)))]
    ftd = ftd.sort_values("start").drop_duplicates(["symbol", "date"], keep="last")
    ftd = ftd.groupby(["cik", "date"]).price.last().reset_index().sort_values(["cik", "date"])

    # Çıkmış şirketlerin günlük Yahoo serisi: FTD fiyatlarıyla örtüşüyorsa (sembol başka şirkete geçmemiş) FTD'nin yerini alır.
    ex_px, ex_raw, ex_dv = exited_daily(gone, ftd)
    if len(ex_px):  # Yahoo serisinin kapsadığı aralıkta FTD gözlemi gereksiz
        cov = ex_px.groupby("cik").date.agg(["min", "max"])
        c = ftd.cik.astype(str)
        ftd = ftd[~((ftd.date >= c.map(cov["min"])) & (ftd.date <= c.map(cov["max"])))]
    ftd_raw = ftd.copy()
    ftd["price"] = ftd.groupby("cik").price.transform(adjust_reverse_splits)

    columns = sec.cik.astype(str)  # hiç fiyatı olmayan üyeler de sütun olarak kalır (kapsamda görünsünler)
    px, raw_px, dv, ftd, ftd_raw = (f.assign(cik=f.cik.astype(str)) for f in (px, raw_px, dv, ftd, ftd_raw))
    out = {
        "price": weekly_last(pd.concat([px, ex_px, ftd], ignore_index=True), "price", dates),
        "raw": weekly_last(pd.concat([raw_px, ex_raw, ftd_raw], ignore_index=True), "price", dates),
        "dollar_volume": weekly_last(pd.concat([dv, ex_dv], ignore_index=True), "dollar_volume", dates),
    }
    for n, df in out.items():
        df.columns = df.columns.astype(str)
        out[n] = df.reindex(columns=columns)
    # Birleşmede hayatta kalan şirketin Yahoo geçmişi çoğu zaman öncülün geçmişidir (AAL ← US Airways/LCC, VTRS ← MYL,
    # LIN ← PX). Aynı fiyat iki kez sayılmasın: öncülün çıkışına kadar o geçmiş öncüle ait, hayatta kalandan silinir.
    for gone_c, act_c, end in successor_overlaps(out["raw"], sec):
        mask = out["raw"].index <= end
        for n in out:
            out[n].loc[mask, act_c] = np.nan
    CACHE.mkdir(parents=True, exist_ok=True)
    for n in out:
        out[n].to_parquet(paths[n])
    return out | {"securities": sec}


def successor_overlaps(raw: pd.DataFrame, sec: pd.DataFrame, tol: float = 0.03, min_match: float = 0.85,
                       min_weeks: int = 26) -> list[tuple[str, str, pd.Timestamp]]:
    """(çıkmış öncül, aktif hayatta kalan, öncülün çıkış tarihi): öncülün fiyatlı haftalarının ≥ %85'inde gerçek fiyatlar %3 içinde.
    SPAC'ler (≈10 $ düz seri, birbirine benzer) ve neredeyse hiç oynamayan seriler değerlendirilmez."""
    from radar.research.sectors import classify
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").reindex(raw.columns)
    kind = classify(sec).reindex(raw.columns)
    act = raw.columns[s.status.to_numpy() == "aktif"]
    A = raw[act].to_numpy(np.float32)
    out = []
    for c in raw.columns[(s.status.to_numpy() == "çıktı") & (kind.to_numpy() == "faaliyet")]:
        x = raw[c].to_numpy(np.float32)
        v = np.isfinite(x) & (raw.index <= s.at[c, "end"])
        if v.sum() < min_weeks or np.std(np.diff(np.log(x[v]))) < 0.02:
            continue
        sub, xv = A[v], x[v][:, None]
        n = np.isfinite(sub).sum(0)
        frac = (np.abs(sub - xv) <= tol * xv).sum(0) / np.maximum(n, 1)
        hits = [j for j in np.flatnonzero((n >= min_weeks) & (frac >= min_match))
                if np.nanstd(np.diff(np.log(sub[:, j][np.isfinite(sub[:, j])]))) >= 0.02]
        if len(hits) > 3:  # düz (SPAC benzeri) seri birçok şirkete "benzer": gerçek öncül-ardıl değil
            continue
        out.extend((c, act[j], s.at[c, "end"]) for j in hits)
    return out


def exited_daily(gone: pd.DataFrame, ftd: pd.DataFrame, tol: float = 0.03, min_match: float = 0.8):
    """Çıkmış şirketlerin Yahoo günlük serisi (prices_exited) → (düzeltilmiş fiyat, gerçek fiyat, işlem tutarı) uzun tabloları.

    Kabul: FTD ile ortak günlerin en az %80'inde gerçek kapanış FTD fiyatına %3 yakın (en az 5 ortak gün). FTD gözlemi
    olmayan şirket kabul edilmez (sembolün o şirkete ait olduğu doğrulanamaz)."""
    empty = pd.DataFrame(columns=["cik", "date", "price"]), pd.DataFrame(columns=["cik", "date", "price"]), \
        pd.DataFrame(columns=["cik", "date", "dollar_volume"])
    try:
        ex = archive.load("prices_exited", columns=["cik", "symbol", "date", "close", "adjclose", "volume", "split_ratio"])
    except Exception:  # veri seti henüz yüklenmemiş
        return empty
    if ex.empty:
        return empty
    ex = ex.assign(cik=ex.cik.astype(str)).dropna(subset=["close", "adjclose"])
    win = gone.assign(cik=gone.cik.astype(str)).set_index("cik")
    ex = ex[ex.cik.isin(win.index)]
    ex = ex[(ex.date >= ex.cik.map(win.start) - pd.Timedelta(days=60)) & (ex.date <= ex.cik.map(win.end) + pd.Timedelta(days=10))]
    ex = ex.reset_index(drop=True)
    ex["true"] = ex.close * unsplit_factor(ex.assign(symbol=ex.cik))
    m = ex.merge(ftd.assign(cik=ftd.cik.astype(str)), on=["cik", "date"])
    ok = (m.true / m.price - 1).abs().le(tol).groupby(m.cik).agg(["mean", "size"])
    good = set(ok[(ok["mean"] >= min_match) & (ok["size"] >= 5)].index)
    ex = ex[ex.cik.isin(good)]
    ex["dollar_volume"] = ex.close * ex.volume
    dv = (ex.sort_values("date").groupby("cik", group_keys=False)
          .apply(lambda g: g.set_index("date").dollar_volume.rolling("91D").median().reset_index().assign(cik=g.name)))
    return (ex.rename(columns={"adjclose": "price"})[["cik", "date", "price"]],
            ex.assign(price=ex.true)[["cik", "date", "price"]], dv if len(ex) else empty[2])


def membership(sec: pd.DataFrame, dates: pd.DatetimeIndex, columns) -> pd.DataFrame:
    s = sec.set_index(sec.cik.astype(str)).reindex(columns)
    start = s.start.to_numpy(dtype="datetime64[ns]")
    end = s.end.fillna(pd.Timestamp("2100-01-01")).to_numpy(dtype="datetime64[ns]")
    d = dates.to_numpy(dtype="datetime64[ns]")[:, None]
    return pd.DataFrame((d >= start) & (d <= end), index=dates, columns=columns)


def exit_price(px: pd.Series) -> float:
    """Çıkıştan önceki son geçerli fiyat. Satın almalarda FTD, çıkıştan sonra 0,01 $ gibi yer tutucu fiyatlar
    yazabilir: önceki 8 gözlemin medyanının %20'sinin altına inen son değer yerine o medyan kullanılır
    (gerçek çöküşler iflas olarak ayrıca 0 sayılır; yavaş düşüşte medyan da düşüktür)."""
    px = px.dropna()
    if px.empty:
        return np.nan
    last = float(px.iloc[-1])
    ref = float(px.iloc[-9:-1].median()) if len(px) > 1 else last
    return ref if ref > 0 and last < 0.2 * ref else last


def forward_returns(price: pd.DataFrame, sec: pd.DataFrame, weeks: int) -> pd.DataFrame:
    """t'de fiyatı olan üyeler için t→t+h getirisi; arada çıkanlara çıkış değeri uygulanır."""
    s = sec.set_index(sec.cik.astype(str)).reindex(price.columns)
    dates = price.index
    member = membership(sec, dates, price.columns)
    future = price.shift(-weeks)
    # Çıkış değeri: iflasta 0, değilse çıkıştan önceki son geçerli fiyat (FTD yer tutucu fiyatları atlanır).
    exit_value = pd.Series(index=price.columns, dtype=float)
    for c in price.columns[s.status.to_numpy() == "çıktı"]:
        end = s.at[c, "end"]
        before = price[c][price.index <= end + pd.Timedelta(days=10)]
        exit_value[c] = 0.0 if s.at[c, "bankrupt"] else exit_price(before)
    horizon_end = pd.Series(dates, index=dates).shift(-weeks)
    end_dates = s.end.to_numpy(dtype="datetime64[ns]")
    exited = pd.DataFrame(end_dates[None, :] < horizon_end.to_numpy(dtype="datetime64[ns]")[:, None],
                          index=dates, columns=price.columns)
    exit_matrix = pd.DataFrame(np.broadcast_to(exit_value.to_numpy(), future.shape), index=dates, columns=price.columns)
    future = future.mask(exited, exit_matrix)
    ret = future / price - 1
    ret = ret.where(member & price.notna())
    return ret.iloc[:-weeks] if weeks else ret

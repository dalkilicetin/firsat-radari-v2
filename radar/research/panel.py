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
    ftd, ftd_raw, (ex_px, ex_raw, ex_dv, _) = _exited_sources(daily, gone)

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
    # Holding yeniden yapılanması (ör. XOM 2026: yeni CIK): yeni kaydın Yahoo geçmişi SEC'e kaydından yıllar önce başlıyorsa,
    # eski kaydın çıkışına kadarki fiyatlar eski kayda (bilanço, 8-K ve içeriden işlemlerin bağlı olduğu CIK) aittir.
    for gone_c, act_c, end in reorg_pairs(out["price"], sec):
        mask = out["price"].index <= end
        for n in out:
            out[n].loc[mask, gone_c] = out[n].loc[mask, act_c]
            out[n].loc[mask, act_c] = np.nan
    for gone_c, act_c, end in successor_overlaps(out["raw"], sec):
        mask = out["raw"].index <= end
        for n in out:
            out[n].loc[mask, act_c] = np.nan
    CACHE.mkdir(parents=True, exist_ok=True)
    for n in out:
        out[n].to_parquet(paths[n])
    return out | {"securities": sec}


def _exited_sources(daily: pd.DataFrame, gone: pd.DataFrame):
    """Borsadan çıkmış şirketlerin fiyat kaynakları: FTD (düzeltilmiş, ham) ve Yahoo serisi (exited_daily çıktısı)."""
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
    ex = exited_daily(gone, ftd)
    ex_px = ex[0]
    if len(ex_px):  # Yahoo serisinin kapsadığı aralıkta FTD gözlemi gereksiz
        cov = ex_px.groupby("cik").date.agg(["min", "max"])
        c = ftd.cik.astype(str)
        ftd = ftd[~((ftd.date >= c.map(cov["min"])) & (ftd.date <= c.map(cov["max"])))]
    ftd_raw = ftd.copy()
    ftd["price"] = ftd.groupby("cik").price.transform(adjust_reverse_splits)
    return ftd, ftd_raw, ex


SPLIT_MIN = 1.3  # bu oranın altındaki kayıtlar (ayrılma, hisse temettüsü) hisse sayısını düzeltmez (ön kayıt v1.2, 6.2)


def split_events(force: bool = False) -> pd.DataFrame:
    """Bölünme olayları (ön kayıt v1.2, 6.1-3): cik, date, ratio (yeni hisse / eski hisse), source.

    Kaynaklar: Yahoo günlük fiyat kayıtları ('yahoo': işlemdeki hisseler, 'yahoo_cikan': çıkmış hisselerin Yahoo serisi) ve
    Yahoo serisi olmayan çıkmış hisselerde fiyat panelinin uyguladığı tahmini ters bölünmeler ('ftd_tahmini'). Sembol → şirket
    eşleştirmesi ve birleşmelerde geçmişin taşınması fiyat paneliyle aynıdır. Bütün oranlar tutulur; eşik uygulanmaz."""
    path = CACHE / "panel_bolunme_olaylari.parquet"
    if path.exists() and not force:
        return pd.read_parquet(path)
    sec = build_identity()["securities"]
    active, gone = sec[sec.status == "aktif"], sec[sec.status == "çıktı"]
    daily = archive.load("prices", columns=["symbol", "date", "split_ratio"])
    daily = daily.merge(active[["symbol", "cik"]], on="symbol")
    ev = [daily[(daily.split_ratio > 0) & (daily.split_ratio != 1)][["cik", "date", "split_ratio"]].assign(source="yahoo")]
    ftd, ftd_raw, ex = _exited_sources(daily, gone)
    xs = ex[3]
    ev.append(xs[(xs.split_ratio > 0) & (xs.split_ratio != 1)].assign(source="yahoo_cikan"))
    # FTD: düzeltilmiş / ham oranı yalnızca tahmini ters bölünmede değişir; değiştiği gözlem bölünme sonrası ilk gözlemdir.
    f = ftd_raw.assign(k=ftd.price.to_numpy() / ftd_raw.price.to_numpy())
    prev = f.groupby("cik").k.shift(1)
    jump = f[prev.notna() & (np.abs(np.log(prev / f.k)) > 1e-9)]
    ev.append(jump.assign(split_ratio=jump.k / prev[jump.index])[["cik", "date", "split_ratio"]].assign(source="ftd_tahmini"))
    out = pd.concat(ev, ignore_index=True).rename(columns={"split_ratio": "ratio"})
    out["cik"] = out.cik.astype(str)
    out["date"] = pd.to_datetime(out.date)
    # Birleşme ve yeniden yapılanmalar: fiyat geçmişi nereye taşındıysa olaylar da oraya.
    p = build()
    moved = []
    for gone_c, act_c, end in reorg_pairs(p["price"], sec):
        m = (out.cik == act_c) & (out.date <= end)
        moved.append(out[m].assign(cik=gone_c))
        out = out[~m]
    for gone_c, act_c, end in successor_overlaps(p["raw"], sec):
        out = out[~((out.cik == act_c) & (out.date <= end))]
    out = pd.concat([out, *moved], ignore_index=True).sort_values(["cik", "date"]).reset_index(drop=True)
    out.to_parquet(path)
    return out


def split_cum(events: pd.DataFrame, min_ratio: float = SPLIT_MIN) -> pd.DataFrame:
    """Eşiği geçen olaylar (oran ≥ min_ratio ya da ≤ 1/min_ratio) ve şirket içinde kümülatif oran çarpımı (cum)."""
    e = events[np.abs(np.log(events.ratio)) >= np.log(min_ratio)].sort_values(["cik", "date"]).copy()
    e["cum"] = e.groupby("cik").ratio.cumprod()
    return e


def split_cum_wide(dates: pd.DatetimeIndex, columns, events: pd.DataFrame | None = None) -> pd.DataFrame:
    """Her Cuma t için C(t) = o güne kadar (dahil) gerçekleşen bölünme oranlarının çarpımı; olay yoksa 1."""
    e = split_cum(split_events() if events is None else events)
    cols = pd.Index(columns).astype(str)
    out = pd.DataFrame(1.0, index=dates, columns=cols)
    e = e[e.cik.isin(set(cols))]
    for cik, g in e.groupby("cik"):
        k = dates.searchsorted(g.date.to_numpy(), side="left")  # olay tarihinden sonraki ilk Cuma (ya da aynı gün)
        vals = np.ones(len(dates))
        for kk, c in zip(k, g.cum.to_numpy()):
            vals[kk:] = c
        out[cik] = vals
    return out


def split_cum_at(cik: pd.Series, when: pd.Series, events: pd.DataFrame | None = None) -> np.ndarray:
    """Her (cik, tarih) için C(tarih): o tarihe kadar (dahil) gerçekleşen bölünme oranlarının çarpımı."""
    e = split_cum(split_events() if events is None else events)
    out = np.ones(len(cik))
    cik = pd.Series(np.asarray(cik).astype(str))
    when = pd.to_datetime(pd.Series(np.asarray(when)))
    groups = {c: g for c, g in e.groupby("cik")}
    for c, idx in cik.groupby(cik).groups.items():
        g = groups.get(c)
        if g is None:
            continue
        d = g.date.to_numpy()
        pos = d.searchsorted(when[idx].to_numpy(), side="right") - 1
        cum = np.concatenate([[1.0], g.cum.to_numpy()])
        out[np.asarray(idx)] = cum[pos + 1]
    return out


def reorg_pairs(price: pd.DataFrame, sec: pd.DataFrame) -> list[tuple[str, str, pd.Timestamp]]:
    from radar.research.road2 import clean_name
    """(eski CIK, yeni CIK, eski kaydın çıkış tarihi): aynı sembol; yeni CIK'in ilk SEC kaydı, fiyat geçmişinin
    başlangıcından en az 2 yıl sonra ve eski kaydın çıkışından en fazla 1 yıl önce (yani yeni kayıt, eski şirketin devamı)."""
    f = archive.load("filings", columns=["cik", "filing_date"])
    first_filing = f.assign(cik=f.cik.astype(str)).groupby("cik").filing_date.min()
    s = sec.assign(cik=sec.cik.astype(str))
    act, gone = s[s.status == "aktif"], s[s.status == "çıktı"]
    out = []
    for r in gone.merge(act, on="symbol", suffixes=("_g", "_a")).itertuples():
        if r.cik_a not in price.columns or r.cik_g not in price.columns or pd.isna(r.end_g):
            continue
        pa = price[r.cik_a].dropna()
        ff = first_filing.get(r.cik_a)
        if len(pa) < 52 or ff is None or pd.isna(ff):
            continue
        if not (ff >= pa.index[0] + pd.Timedelta(days=730) and ff >= r.end_g - pd.Timedelta(days=365) and pa.index[0] < r.end_g):
            continue
        # Aynı şirket mi? Adın ilk anlamlı kelimesi uyuşmalı (sembolü sonradan alan başka şirketi ayıklar: NEWP, ARIS...)
        w = lambda n: (clean_name(n).replace("the ", "", 1).split() or [""])[0]
        a, g = w(r.name_a), w(r.name_g)
        if len(a) >= 4 and len(g) >= 4 and (a.startswith(g) or g.startswith(a)):
            out.append((r.cik_g, r.cik_a, r.end_g))
    return out


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
        pd.DataFrame(columns=["cik", "date", "dollar_volume"]), pd.DataFrame(columns=["cik", "date", "split_ratio"])
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
            ex.assign(price=ex.true)[["cik", "date", "price"]], dv if len(ex) else empty[2],
            ex[["cik", "date", "split_ratio"]])


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

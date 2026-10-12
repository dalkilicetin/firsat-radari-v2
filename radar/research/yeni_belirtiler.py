"""Literatür taramasından gelen yeni belirtiler (2. tur): python -m radar.research.yeni_belirtiler

Hepsi elimizdeki veriden, aylık çerçevenin tarihlerinde (o gün bilinen bilgiyle) hesaplanır ve çerçeveye eklenir:
Günlük fiyatlardan:
- fip_bilgi_surekliligi: Da, Gurun & Warachka (RFS 2014) "frog-in-the-pan": −sign(12 ay getiri) × (%negatif gün − %pozitif gün);
  yüksek = momentum sürekli küçük adımlarla oluşmuş (daha kalıcı)
- max_gunluk_1a: son 21 işlem gününün en yüksek günlük getirisi (Bali-Cakici-Whitelaw 2011; piyango — negatif beklenir)
- ivol_3a: son 63 günde SPY'a göre artık getirinin oynaklığı (Ang ve diğ. 2006 — negatif beklenir)
SEC dosyalarından (kabul tarihinden sonraki ilk Cuma; son 13 / 26 hafta):
- aktivist_13d: son 13 haftada yeni SC 13D (Brav-Jiang-Partnoy-Thomas 2008), aktivist_13d_degisiklik: 13D/A sayısı
- pasif_13g_yeni: son 13 haftada yeni SC 13G (≥ %5 pasif pay)
- gec_rapor_bildirimi: son 26 haftada NT 10-K / NT 10-Q (negatif beklenir)
- hisse_ihraci: son 13 haftada S-1 / S-3 / 424B4 (ek ihraç — negatif beklenir)
- sektor_ma_dalgasi: aynı sektörde son 52 haftada 8-K 2.01 (satın alma tamamlandı) sayısı ÷ sektördeki şirket sayısı
  (devralma olasılığı; Cremers-Nair-John 2009)
XBRL'den:
- sue_fiyat: çeyreklik seyreltilmiş HBK − geçen yıl aynı çeyrek HBK, fiyata bölünmüş (analistsiz kazanç sürprizi;
  Jegadeesh-Livnat 2006); gelir_surprizi: çeyreklik gelir büyümesi − son 4 çeyreğin ortalama büyümesi
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import panel

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"


def daily_features(dates: pd.DatetimeIndex, cols: pd.Index) -> dict[str, pd.DataFrame]:
    sec = panel.build()["securities"].assign(cik=lambda x: x.cik.astype(str))
    act = sec[sec.status == "aktif"][["symbol", "cik"]]
    d = archive.load("prices", columns=["symbol", "date", "adjclose"])
    spy = d[d.symbol == "SPY"].set_index("date").adjclose.sort_index()
    d = d.merge(act, on="symbol")
    try:
        ex = archive.load("prices_exited", columns=["cik", "date", "adjclose"])
        d = pd.concat([d[["cik", "date", "adjclose"]], ex.assign(cik=ex.cik.astype(str))], ignore_index=True)
    except Exception:
        d = d[["cik", "date", "adjclose"]]
    d = d[d.date >= dates.min() - pd.Timedelta(days=400)]
    wide = d.pivot_table(index="date", columns="cik", values="adjclose", aggfunc="last").sort_index()
    ret = wide.pct_change(fill_method=None)
    mret = spy.reindex(wide.index).pct_change(fill_method=None)
    out = {k: pd.DataFrame(np.nan, index=dates, columns=cols) for k in ("fip_bilgi_surekliligi", "max_gunluk_1a", "ivol_3a")}
    for t in dates:
        i = wide.index.searchsorted(t, side="right")  # t dahil son işlem günü
        if i < 260:
            continue
        r = ret.iloc[i - 252:i]
        n = r.notna().sum()
        pos, neg = (r > 0).sum() / n, (r < 0).sum() / n
        r12 = wide.iloc[i - 1] / wide.iloc[i - 252] - 1
        fip = (-(np.sign(r12) * (neg - pos))).where(n >= 200)
        mx = ret.iloc[i - 21:i].max().where(ret.iloc[i - 21:i].notna().sum() >= 15)
        r3, m3 = ret.iloc[i - 63:i], mret.iloc[i - 63:i]
        mc = m3 - m3.mean()
        beta = (r3.sub(r3.mean()).mul(mc, axis=0)).sum() / (mc ** 2).sum()
        resid = r3 - np.outer(m3.to_numpy(), beta.to_numpy())
        iv = resid.std().where(r3.notna().sum() >= 50)
        for k, v in (("fip_bilgi_surekliligi", fip), ("max_gunluk_1a", mx), ("ivol_3a", iv)):
            out[k].loc[t] = v.reindex(cols).to_numpy()
    return out


def filing_features(dates: pd.DatetimeIndex, cols: pd.Index, sector: pd.Series) -> dict[str, pd.DataFrame]:
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    f = f.assign(cik=f.cik.astype(str))
    f = f[f.cik.isin(set(cols))]
    f["date"] = pd.to_datetime(f.filing_date)

    def count(forms, weeks, item=None):
        x = f[f.form.isin(forms)]
        if item:
            x = x[x["items"].fillna("").str.contains(item, regex=False)]
        out = pd.DataFrame(0.0, index=dates, columns=cols)
        for t in dates:
            w = x[(x.date < t) & (x.date >= t - pd.Timedelta(weeks=weeks))]
            c = w.groupby("cik").size()
            out.loc[t, c.index] = c.to_numpy()
        return out
    res = {
        "aktivist_13d": (count(["SC 13D", "SCHEDULE 13D"], 13) > 0).astype(float),
        "aktivist_13d_degisiklik": count(["SC 13D/A", "SCHEDULE 13D/A"], 13),
        "pasif_13g_yeni": (count(["SC 13G", "SCHEDULE 13G"], 13) > 0).astype(float),
        "gec_rapor_bildirimi": (count(["NT 10-K", "NT 10-Q"], 26) > 0).astype(float),
        "hisse_ihraci": (count(["S-1", "S-3", "424B4"], 13) > 0).astype(float),
    }
    ma = count(["8-K"], 52, item="2.01")
    sect = sector.reindex(cols)
    wave = ma.T.groupby(sect.to_numpy()).transform("sum").T / pd.Series(cols, index=cols).groupby(sect.to_numpy()).transform("size").to_numpy()
    res["sektor_ma_dalgasi"] = wave
    return res


def xbrl_features(dates: pd.DatetimeIndex, cols: pd.Index, price: pd.DataFrame) -> dict[str, pd.DataFrame]:
    from radar.research import fundamentals
    from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
    from radar.research.road1 import REVENUE, by_filing, load_fin
    fin = fundamentals.plain(load_fin())
    eps = by_filing(fin, ["EarningsPerShareDiluted", "EarningsPerShareBasic"], [1])
    rev = by_filing(fin, REVENUE, [1])
    P = lambda df, v: pit(df.rename(columns={"accepted": "date"}).assign(value=v)[["cik", "date", "value"]],
                          price.index, price.columns, FUNDAMENTAL_MAX_AGE)
    d_eps = P(eps, eps.cur - eps.prev)
    g = P(rev, (rev.cur / rev.prev - 1).where(rev.prev > 0))
    sue = (d_eps / price.where(price > 0)).clip(-1, 1)
    rs = (g - g.rolling(52, min_periods=26).mean()).clip(-3, 3)
    take = lambda x: x.reindex(index=dates, method="ffill").reindex(columns=cols)
    return {"sue_fiyat": take(sue), "gelir_surprizi": take(rs)}


def augment() -> None:
    from radar.research import hindsight as hs
    df = pd.read_parquet(FRAME)
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    p = panel.build()
    cols = p["price"].columns.astype(str)
    from radar.research import context, sectors
    sic = sectors.load_sic().reindex(p["price"].columns).fillna("")
    sector = pd.Series([hs.ETF_NAMES.get(context.etf_for_sic(c), "Diğer") for c in sic], index=cols)
    feats = {}
    for name, fn in (("günlük", lambda: daily_features(dates, cols)), ("dosyalar", lambda: filing_features(dates, cols, sector)),
                     ("xbrl", lambda: xbrl_features(dates, cols, p["price"]))):
        part = fn()
        feats |= part
        print(name, "tamam:", list(part), flush=True)
    events = {"aktivist_13d", "pasif_13g_yeni", "gec_rapor_bildirimi", "hisse_ihraci"}
    key = pd.MultiIndex.from_arrays([df.tarih, df.index.astype(str)])
    for name, wide in feats.items():
        long = wide.stack()
        long.index.names = ["tarih", "cik"]
        if name not in events:
            long = long.groupby(level=0).rank(pct=True)
        df[name] = long.reindex(key).to_numpy(dtype="float32")
        if name in events:
            df[name] = df[name].fillna(0)
        print(name, f"dolu %{df[name].notna().mean() * 100:.0f}, ort {np.nanmean(df[name]):.3f}", flush=True)
    df.to_parquet(FRAME)
    ev_path = FRAME.with_name("aylik_cerceve_olaylar.json")
    import json
    ev = set(json.loads(ev_path.read_text())) | events
    ev_path.write_text(json.dumps(sorted(ev), ensure_ascii=False))


if __name__ == "__main__":
    augment()

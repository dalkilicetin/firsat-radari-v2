"""Risk puanı (1–5): her hafta, yalnızca o güne kadar bilinen verilerle.

Bileşenler kesitsel yüzdelik sıralamaya çevrilir (1 = en riskli), olaylar ek puan olarak eklenir,
toplam yüzdelik dilimlere göre 1–5'e bölünür. Ağırlıklar başlangıçta uzman görüşüdür; 4. aşamada
gerçekleşen düşüş ve çıkışlarla kalibre edilecek.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive
from radar.research import panel
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit, recent_events, rolling_count


# (bileşen, ağırlık). Yüksek değer = yüksek risk olacak şekilde hazırlanır.
# Doğrulamada (2015–2024) ters yönde çıkan bileşenler çıkarıldı:
# - borç/varlık: yüksek borçlular çoğunlukla bankalar/olgun şirketler, daha az düşüyor (IC −0,10)
# - içeriden satış: büyük, başarılı şirketlerde hisse bazlı ücret satışları yaygın (IC −0,07)
WEIGHTS = {
    "oynaklik": 0.25, "dusus": 0.20, "dusuk_fiyat": 0.10, "likidite": 0.10, "yeni": 0.05,
    "nakit_suresi": 0.20, "sulandirma": 0.10,
}
DROPPED = {"borc": "ters yön (IC −0,10)", "icerden_satis": "ters yön (IC −0,07)"}
EVENT_POINTS = {"delist_uyarisi": 0.25, "denetci_degisikligi": 0.10, "geciken_rapor": 0.20}
BUCKETS = [0.30, 0.55, 0.75, 0.90]  # bileşik yüzdelik → 1..5


def financial_features(dates, columns) -> dict[str, pd.DataFrame]:
    fin = archive.load("financials", columns=["cik", "tag", "value", "accepted", "qtrs", "ddate", "form"])
    fin = fin.rename(columns={"accepted": "date"})
    # Aynı rapordaki karşılaştırmalı (geçmiş dönem) değerleri değil, raporun kendi dönemini al.
    latest_period = fin.groupby(["cik", "date"]).ddate.transform("max")
    cur = fin[fin.ddate == latest_period]

    def tag(names, qtrs):
        d = cur[cur.tag.isin(names) & (cur.qtrs == qtrs)]
        return d.sort_values("date").groupby(["cik", "date"]).value.first().reset_index()

    cash = pit(tag(["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
                     "CashAndCashEquivalents"], 0), dates, columns, FUNDAMENTAL_MAX_AGE)
    ocf = pit(tag(["NetCashProvidedByUsedInOperatingActivities"], 4), dates, columns, FUNDAMENTAL_MAX_AGE)
    shares = pit(tag(["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"], 0), dates, columns, FUNDAMENTAL_MAX_AGE)
    assets = pit(tag(["Assets"], 0), dates, columns, FUNDAMENTAL_MAX_AGE)
    liab = pit(tag(["Liabilities"], 0), dates, columns, FUNDAMENTAL_MAX_AGE)

    burn = (-ocf).clip(lower=0)
    runway_months = (cash / burn.replace(0, np.nan) * 12).where(burn > 0)
    # Nakit yakmayan şirket: en düşük risk (çok uzun süre).
    runway_risk = (-runway_months).where(burn > 0, -1e6).where(cash.notna() & ocf.notna())
    dilution = shares / shares.shift(52) - 1
    leverage = liab / assets
    return {"nakit_suresi": runway_risk, "sulandirma": dilution, "borc": leverage}


def event_features(dates, columns) -> dict[str, pd.DataFrame]:
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    eight_k = f[f.form == "8-K"]
    items = eight_k["items"].fillna("")
    mk = lambda d: d.rename(columns={"filing_date": "date"})[["cik", "date"]]
    return {
        "delist_uyarisi": recent_events(mk(eight_k[items.str.contains(r"\b3\.01\b")]), dates, columns, 180),
        "denetci_degisikligi": recent_events(mk(eight_k[items.str.contains(r"\b4\.01\b")]), dates, columns, 365),
        "geciken_rapor": recent_events(mk(f[f.form.isin(["NT 10-K", "NT 10-Q"])]), dates, columns, 365),
    }


def insider_selling(dates, columns) -> pd.DataFrame:
    ins = archive.load("insider", columns=["issuer_cik", "owner_cik", "code", "price", "available_date"])
    ins = ins.dropna(subset=["issuer_cik", "available_date"])
    ins = ins[ins.code.isin(["S", "P"]) & (ins.price > 0)]
    ins = ins.assign(cik=ins.issuer_cik.astype("int64").astype(str), date=ins.available_date)
    sellers = ins[ins.code == "S"].drop_duplicates(["cik", "owner_cik", "date"])
    buyers = ins[ins.code == "P"].drop_duplicates(["cik", "owner_cik", "date"])
    count = lambda d: rolling_count(d[["cik", "date"]], dates, columns, 90)
    return count(sellers) - count(buyers)


def features(p: dict) -> dict[str, pd.DataFrame]:
    price, raw, dv, sec = p["price"], p["raw"], p["dollar_volume"], p["securities"]
    dates, cols = price.index, price.columns
    wret = price / price.shift(1) - 1
    first = price.notna().idxmax()
    weeks_listed = pd.DataFrame((dates.values[:, None] - first.values[None, :]) / np.timedelta64(7, "D"),
                                index=dates, columns=cols)
    f = {
        "oynaklik": wret.rolling(26, min_periods=13).std() * np.sqrt(52),
        "dusus": -(price / price.rolling(52, min_periods=13).max() - 1),
        "dusuk_fiyat": pd.DataFrame(np.select([raw < 1, raw < 5], [2.0, 1.0], 0.0), index=dates, columns=cols).where(raw.notna()),
        "likidite": -np.log1p(dv),
        "yeni": (weeks_listed < 52).astype(float).where(price.notna()),
        "icerden_satis": insider_selling(dates, cols),
    }
    f |= financial_features(dates, cols)
    f |= event_features(dates, cols)
    return f


def score(f: dict[str, pd.DataFrame], universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bileşik risk yüzdeliği ve 1–5 puan. universe: o hafta fiyatı olan üyeler (bool)."""
    total = pd.DataFrame(0.0, index=universe.index, columns=universe.columns)
    weight = pd.DataFrame(0.0, index=universe.index, columns=universe.columns)
    for name, w in WEIGHTS.items():
        r = f[name].where(universe).rank(axis=1, pct=True)
        total += (r * w).fillna(0)
        weight += r.notna() * w  # eksik bileşen puanı düşürmez: ağırlık yeniden ölçeklenir
    comp = total / weight.replace(0, np.nan)
    for name, pts in EVENT_POINTS.items():
        comp += f[name].astype(float).where(universe, 0) * pts
    pct = comp.where(universe).rank(axis=1, pct=True)
    level = pd.DataFrame(np.digitize(pct.fillna(-1), BUCKETS) + 1, index=pct.index, columns=pct.columns).where(pct.notna())
    return pct, level


def outcomes(price: pd.DataFrame, sec: pd.DataFrame, weeks: int = 52) -> dict[str, pd.DataFrame]:
    """Doğrulama için: sonraki `weeks` haftadaki en büyük düşüş ve kötü çıkış (iflas ya da %50+ kayıpla çıkış)."""
    fwd = [panel.forward_returns(price, sec, w).reindex(price.index) for w in range(1, weeks + 1, 4)]
    worst = pd.concat(fwd).groupby(level=0).min() if fwd else None
    s = sec.set_index(sec.cik.astype(str)).reindex(price.columns)
    end = s.end.to_numpy(dtype="datetime64[ns]")
    d = price.index.to_numpy(dtype="datetime64[ns]")[:, None]
    exits_soon = (end[None, :] > d) & (end[None, :] <= d + np.timedelta64(weeks * 7, "D"))
    year_ret = panel.forward_returns(price, sec, weeks).reindex(price.index)
    bad_exit = pd.DataFrame(exits_soon, index=price.index, columns=price.columns) & (year_ret < -0.5)
    return {"en_buyuk_dusus": worst, "kotu_cikis": bad_exit, "yillik_getiri": year_ret}

"""Test düzeneği: analiz aracının bütün ölçümleri bu kurallarla yapılır (analiz_araci_plani.md, bölüm 1).

Takvim (her hafta, Cuma t):
- Bilgi kesimi: perşembe 16:00 (New York). Fiyatlar perşembe kapanışı; belgeler bu saatten önce SEC'e kabul edilmiş olmalı.
  Saat dilimi belirsiz kayıtlarda geç olan yorum seçilir: saat değeri New York saati sayılır (SEC kayıtlarında 'Z' etiketi
  bazen yanlış). Yalnızca tarihi olan kayıtlar (ör. Form 4'te bir iş günü sonrası) o günün sonunda kullanılabilir sayılır.
- Rapor cuma 14:00 TR (07:00 New York); alış cuma kapanışı. Satış 13 / 26 hafta sonraki cuma kapanışı.
- Masraf: alışta ve satışta ayrı ayrı, perşembe itibarıyla 13 haftalık medyan günlük işlem tutarına göre (backtest.COSTS).
- Hayatta kalma yanlılığı yok: o gün borsada olan her hisse (sonradan çıkanlar dahil). Arada çıkan hisse için çıkış değeri:
  iflasta 0, değilse çıkıştan önceki son geçerli fiyat (panel.forward_returns).
- Evren (o günkü değerlerle): finans dışı faaliyet şirketi (yalnızca 20-F/40-F dosyalayan yabancılar hariç), perşembe fiyatı ≥ 5 $, piyasa değeri ≥ 500 M$, işlem tutarı
  ≥ 5 M$/gün. Borsadan çıkmış hisselerin çoğunda günlük hacim yoktur (yalnızca FTD fiyatı): işlem tutarı FINRA aylık
  hacminden tahmin edilir (son tamamlanmış ay, hisse/gün × perşembe fiyatı × o hafta Yahoo/FINRA oranının medyanı).
  Bunu yapmazsak sonradan çıkan hisseler evrenden düşer ve hayatta kalma yanlılığı geri gelir.
- Karşılaştırma: S&P 500 (SPY), hissenin sektör ETF'i, evrenin eşit ağırlıklı ortalaması — aynı cuma kapanışları arasında.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd

from radar import archive
from radar.identity import build as build_identity
from radar.research import backtest, context, fundamentals, panel, sectors
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit

ET = "America/New_York"
KESIM = pd.Timedelta(hours=8)  # 16:00 + 8 saat = gece yarısı: 16:00'dan sonraki kayıt ertesi güne kayar
MIN_FIYAT, MIN_PD, MIN_ISLEM = 5.0, 5e8, 5e6
VADE = {"3a": 13, "6a": 26}
AYAR = (2013, 2022)   # eşik ve ağırlıklar yalnızca bu yıllarla ayarlanır
SINAV = (2023, 2026)  # bir kez açılır
PERSEMBE = "_persembe"


def duvar_saati(ts) -> pd.Series:
    """Zaman damgası → New York duvar saati (naive). tz'li kayıtta saat değeri olduğu gibi alınır (geç yorum)."""
    t = pd.to_datetime(pd.Series(ts))
    if getattr(t.dt, "tz", None) is not None:
        t = t.dt.tz_localize(None)
    return t


def kullanilabilir(ts, saatli: bool = True) -> pd.Series:
    """Kaydın ilk kullanılabileceği Cuma. saatli: perşembe 16:00 kesimi; değilse tarihin bittiği gün."""
    t = duvar_saati(ts)
    gun = (t + KESIM).dt.normalize() if saatli else t.dt.normalize()
    return gun + pd.Timedelta(days=1) + pd.offsets.Week(weekday=4, n=0)


def masrafli(brut: pd.DataFrame, oran: pd.DataFrame) -> pd.DataFrame:
    """Alışta ve satışta tek yön masraf: (1 − c)(1 + r)(1 − c) − 1."""
    return (1 - oran) * (1 + brut) * (1 - oran) - 1


@dataclass
class Duzenek:
    cuma: dict          # Cuma kapanışları paneli (giriş / çıkış)
    persembe: dict      # perşembe kapanışları, Cuma etiketli (işaretler)

    @classmethod
    def yukle(cls, daralt: bool = True) -> "Duzenek":
        """daralt: yalnızca faaliyet şirketleri ve perşembe fiyatı bir kez olsun ≥ 5 $ olmuş hisseler (bellek için;
        evrene giremeyecek sütunlar sonucu değiştirmez)."""
        cuma = panel.build()
        dates = cuma["price"].index
        thu = panel.build(dates=dates - pd.Timedelta(days=1), tag=PERSEMBE)
        persembe = {k: (v.reindex(dates - pd.Timedelta(days=1)).set_axis(dates, axis=0).reindex(columns=cuma["price"].columns)
                        if k != "securities" else v) for k, v in thu.items()}
        if daralt:
            keep = sectors.operating_mask(cuma).to_numpy() & (persembe["raw"] >= MIN_FIYAT).any().to_numpy()
            cols = cuma["price"].columns[keep]
            import os
            if os.environ.get("RADAR_ARAC_ORNEK"):  # hızlı deneme: ilk N sütun (sonuç için kullanılmaz)
                cols = cols[: int(os.environ["RADAR_ARAC_ORNEK"])]
            cuma = {k: (v[cols].astype("float32") if k != "securities" else v) for k, v in cuma.items()}
            persembe = {k: (v[cols].astype("float32") if k != "securities" else v) for k, v in persembe.items()}
        return cls(cuma, persembe)

    @property
    def tarihler(self) -> pd.DatetimeIndex:
        return self.cuma["price"].index

    @property
    def sutunlar(self) -> pd.Index:
        return self.cuma["price"].columns

    @cached_property
    def sec(self) -> pd.DataFrame:
        return self.cuma["securities"]

    @cached_property
    def uye(self) -> pd.DataFrame:
        return panel.membership(self.sec, self.tarihler, self.sutunlar)

    @cached_property
    def faaliyet(self) -> pd.Series:
        return sectors.operating_mask(self.cuma) & ~self.yabanci

    @cached_property
    def yabanci(self) -> pd.Series:
        """Yalnızca 20-F / 40-F dosyalayan (hiç 10-K vermemiş) şirketler. Bunlarda piyasa değeri (adi hisse sayısı × ADR fiyatı)
        ADR oranı yüzünden yanlış çıkıyor; küçük yabancı şirketler büyük görünüyor, bu yüzden evrene alınmaz."""
        f = archive.load("filings", columns=["cik", "form"])
        forms = f.assign(cik=f.cik.astype(str)).groupby("cik").form.agg(set)
        yab = {c for c, st in forms.items() if ("20-F" in st or "40-F" in st) and "10-K" not in st}
        return pd.Series([c in yab for c in self.sutunlar], index=self.sutunlar)

    @cached_property
    def finans(self) -> pd.DataFrame:
        from radar.arac import temel
        return temel.finans()

    @cached_property
    def hisse_sayisi(self) -> pd.DataFrame:
        """Perşembe 16:00'ya kadar yayımlanmış son rapordaki hisse sayısı; rapordan sonraki bölünmelere göre düzeltilir
        (bölünme ölçüsü perşembe itibarıyla). Sayı, raporun yayım tarihinden itibaren geçerlidir (K1: yayım tarihi)."""
        sh = fundamentals.shares_outstanding(self.finans)
        sh = sh.assign(cik=sh.cik.astype(str), gun=kullanilabilir(sh.accepted).to_numpy())
        events = panel.split_events()
        # Bölünme ölçüsü: raporun yayımlandığı gün ve perşembe (Cuma t − 1 gün).
        c_rep = panel.split_cum_at(sh.cik, duvar_saati(sh.accepted).dt.normalize(), events)
        # pit, olay gününden sonraki ilk Cuma'yı alır; kullanılabilir Cuma'dan bir gün önceyi vererek aynı Cuma'ya düşürürüz.
        long = sh.assign(date=sh.gun - pd.Timedelta(days=1))
        n = pit(long[["cik", "date", "value"]], self.tarihler, self.sutunlar, FUNDAMENTAL_MAX_AGE)
        rep = pit(long.assign(value=c_rep)[["cik", "date", "value"]], self.tarihler, self.sutunlar, FUNDAMENTAL_MAX_AGE)
        now = panel.split_cum_wide(self.tarihler - pd.Timedelta(days=1), self.sutunlar, events).set_axis(self.tarihler, axis=0)
        return n * (now / rep).fillna(1.0)

    @cached_property
    def finra_hisse_gun(self) -> pd.DataFrame:
        """FINRA aylık hacmi (hisse/gün), ay bittikten sonraki ilk Cuma'dan itibaren; sembol → CIK, sembolün geçerli aralığına göre."""
        f = archive.load("finra_aciga_satis")
        f = f[f.days > 0].assign(value=lambda x: x.total / x.days)
        tk = build_identity()["tickers"]
        tk = tk.assign(cik=tk.cik.astype(str))
        m = f.merge(tk, left_on="symbol", right_on="ticker")
        m = m[(m.date >= m.first_seen - pd.Timedelta(days=31)) & (m.date <= m.last_seen + pd.Timedelta(days=31))]
        m = m[m.groupby(["symbol", "date"]).cik.transform("nunique") == 1]  # aynı sembol iki şirkete çıkıyorsa atla
        m = m.assign(date=m.date + pd.offsets.MonthBegin(1) - pd.Timedelta(days=1))  # ayın son günü biter
        return pit(m[["cik", "date", "value"]], self.tarihler, self.sutunlar, 45)

    @cached_property
    def islem_tutari(self) -> pd.DataFrame:
        """Günlük işlem tutarı ($): Yahoo 13 haftalık medyan; yoksa FINRA tahmini."""
        yahoo = self.persembe["dollar_volume"]
        finra = self.finra_hisse_gun * self.persembe["raw"]
        oran = (yahoo / finra).where(yahoo >= 1e6).replace([np.inf, -np.inf], np.nan).median(axis=1)
        return yahoo.fillna(finra.mul(oran, axis=0))

    @cached_property
    def islem_kaynagi(self) -> pd.DataFrame:
        y = self.persembe["dollar_volume"].notna()
        return pd.DataFrame(np.where(y, "yahoo", np.where(self.islem_tutari.notna(), "finra", "yok")),
                            index=y.index, columns=y.columns)

    @cached_property
    def piyasa_degeri(self) -> pd.DataFrame:
        return self.hisse_sayisi * self.persembe["raw"]

    @cached_property
    def evren(self) -> pd.DataFrame:
        """O gün alınabilir hisseler (Cuma t kararı için): yukarıdaki kurallar + Cuma kapanış fiyatı var."""
        th = self.persembe
        ok = (self.uye & self.faaliyet.to_numpy()[None, :] & self.cuma["price"].notna() & th["price"].notna()
              & (th["raw"] >= MIN_FIYAT) & (self.piyasa_degeri >= MIN_PD) & (self.islem_tutari >= MIN_ISLEM))
        return ok

    @cached_property
    def islem_bilinmeyen(self) -> pd.DataFrame:
        """Kapsam raporu için: diğer şartları geçip işlem tutarı hiç bilinmeyenler."""
        th = self.persembe
        return (self.uye & self.faaliyet.to_numpy()[None, :] & self.cuma["price"].notna() & (th["raw"] >= MIN_FIYAT)
                & (self.piyasa_degeri >= MIN_PD) & self.islem_tutari.isna())

    def brut(self, vade: str) -> pd.DataFrame:
        """Cuma t kapanışından vade sonu Cuma kapanışına brüt getiri (arada çıkana çıkış değeri, iflasta −%100)."""
        r = panel.forward_returns(self.cuma["price"], self.sec, VADE[vade])
        return r.reindex(self.tarihler)

    @cached_property
    def masraf_orani(self) -> pd.DataFrame:
        dv = self.islem_tutari
        out = np.full(dv.shape, backtest.UNKNOWN_COST)
        for floor, rate in reversed(backtest.COSTS):
            out[dv.to_numpy() >= floor] = rate
        return pd.DataFrame(out, index=dv.index, columns=dv.columns)

    def net(self, vade: str) -> pd.DataFrame:
        return masrafli(self.brut(vade), self.masraf_orani)

    @cached_property
    def etf(self) -> pd.DataFrame:
        return context.etf_prices(self.tarihler)

    @cached_property
    def etf_persembe(self) -> pd.DataFrame:
        return context.etf_prices(self.tarihler - pd.Timedelta(days=1)).set_axis(self.tarihler, axis=0)

    @cached_property
    def sektor_etf(self) -> pd.Series:
        sic = sectors.load_sic().reindex(self.sutunlar).fillna("")
        return pd.Series([context.etf_for_sic(c) for c in sic], index=self.sutunlar)

    def kiyas(self, vade: str) -> dict[str, pd.DataFrame | pd.Series]:
        """Aynı Cuma kapanışları arasında: borsa (SPY), hissenin sektör ETF'i (hisse başına) ve eşit ağırlıklı evren."""
        h = VADE[vade]
        e = self.etf.shift(-h) / self.etf - 1
        sek = pd.DataFrame({c: e[s] if s in e else np.nan for c, s in self.sektor_etf.items()}, index=self.tarihler)
        esit = self.brut(vade).where(self.evren).mean(axis=1)
        return {"borsa": e["SPY"], "sektor": sek, "esit": esit}

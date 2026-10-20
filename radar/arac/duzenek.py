"""Test düzeneği: analiz aracının bütün ölçümleri bu kurallarla yapılır (analiz_araci_plani.md, bölüm 1).

Takvim (her hafta, Cuma t):
- Bilgi kesimi: perşembe 16:00 (New York). Fiyatlar perşembe kapanışı; belgeler bu saatten önce SEC'e kabul edilmiş olmalı.
  Saat dilimi belirsiz kayıtlarda geç olan yorum seçilir: saat değeri New York saati sayılır (SEC kayıtlarında 'Z' etiketi
  bazen yanlış). Yalnızca tarihi olan kayıtlar (ör. Form 4'te bir iş günü sonrası) o günün sonunda kullanılabilir sayılır.
- Rapor cuma 14:00 TR (07:00 New York); alış cuma kapanışı. Satış 13 / 26 hafta sonraki cuma kapanışı.
- Masraf: alışta ve satışta ayrı ayrı, perşembe itibarıyla 13 haftalık medyan günlük işlem tutarına göre (backtest.COSTS).
- Hayatta kalma yanlılığı yok: o gün borsada olan her hisse (sonradan çıkanlar dahil). Arada çıkan hisse için çıkış değeri:
  iflasta 0, değilse çıkıştan önceki son geçerli fiyat (panel.forward_returns).
- Evren (o günkü değerlerle): finans dışı faaliyet şirketi, perşembe fiyatı ≥ 5 $, piyasa değeri ≥ 500 M$, işlem tutarı
  ≥ 5 M$/gün. İşlem tutarı bilinmeyen (yalnızca FTD fiyatlı, çoğu sonradan çıkmış) hisseler ayrıca sayılır; varsayılan
  evrene girmez, kapsam raporunda gösterilir.
- Karşılaştırma: S&P 500 (SPY), hissenin sektör ETF'i, evrenin eşit ağırlıklı ortalaması — aynı cuma kapanışları arasında.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import numpy as np
import pandas as pd

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
    def yukle(cls) -> "Duzenek":
        cuma = panel.build()
        dates = cuma["price"].index
        thu = panel.build(dates=dates - pd.Timedelta(days=1), tag=PERSEMBE)
        persembe = {k: (v.reindex(dates - pd.Timedelta(days=1)).set_axis(dates, axis=0).reindex(columns=cuma["price"].columns)
                        if k != "securities" else v) for k, v in thu.items()}
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
        return sectors.operating_mask(self.cuma)

    @cached_property
    def hisse_sayisi(self) -> pd.DataFrame:
        """Perşembe 16:00'ya kadar yayımlanmış son rapordaki hisse sayısı; rapordan sonraki bölünmelere göre düzeltilir
        (bölünme ölçüsü perşembe itibarıyla). Sayı, raporun yayım tarihinden itibaren geçerlidir (K1: yayım tarihi)."""
        fin = fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate", "segments"])
        sh = fundamentals.shares_outstanding(fin)
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
    def piyasa_degeri(self) -> pd.DataFrame:
        return self.hisse_sayisi * self.persembe["raw"]

    @cached_property
    def evren(self) -> pd.DataFrame:
        """O gün alınabilir hisseler (Cuma t kararı için): yukarıdaki kurallar + Cuma kapanış fiyatı var."""
        th = self.persembe
        ok = (self.uye & self.faaliyet.to_numpy()[None, :] & self.cuma["price"].notna() & th["price"].notna()
              & (th["raw"] >= MIN_FIYAT) & (self.piyasa_degeri >= MIN_PD) & (th["dollar_volume"] >= MIN_ISLEM))
        return ok

    @cached_property
    def islem_bilinmeyen(self) -> pd.DataFrame:
        """Kapsam raporu için: diğer şartları geçip işlem tutarı bilinmeyenler."""
        th = self.persembe
        return (self.uye & self.faaliyet.to_numpy()[None, :] & self.cuma["price"].notna() & (th["raw"] >= MIN_FIYAT)
                & (self.piyasa_degeri >= MIN_PD) & th["dollar_volume"].isna())

    def brut(self, vade: str) -> pd.DataFrame:
        """Cuma t kapanışından vade sonu Cuma kapanışına brüt getiri (arada çıkana çıkış değeri, iflasta −%100)."""
        r = panel.forward_returns(self.cuma["price"], self.sec, VADE[vade])
        return r.reindex(self.tarihler)

    @cached_property
    def masraf_orani(self) -> pd.DataFrame:
        dv = self.persembe["dollar_volume"]
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

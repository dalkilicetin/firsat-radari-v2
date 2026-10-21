"""Kirilma noktasi: rejim gecislerini oncu degiskenlerle tahmin etme (lojistik, ileri yurumeye yakin: egitim/test ayri dunyalar)."""
import numpy as np
import pandas as pd

from mekanizma.ozellik import fiyat, korelasyon
from mekanizma.ozellik.rejim import kural_rejim

OZ = ["genislik_ayrisma", "vix_degisim_21", "vix_vol_21", "kredi_egim_60", "ort_kor_63", "kor_degisim_21", "momentum_farki", "dd"]


def momentum_farki(hisseler, n=21):
    """12-1 momentum en ust %20 - en alt %20 portfoyunun son n bar toplam getirisi. Uyelik bir onceki barin skoruna gore (sizinti yok)."""
    skor = hisseler.shift(21) / hisseler.shift(252) - 1
    sira = skor.rank(axis=1, pct=True).shift(1)
    r = hisseler.pct_change()
    ust = r.where(sira >= 0.8).mean(axis=1)
    alt = r.where(sira <= 0.2).mean(axis=1)
    return (ust - alt).rolling(n, min_periods=n // 2).sum()


def ozellikler(adj, hisseler, vix, kredi, p):
    oz = pd.DataFrame(index=adj.index)
    ust = fiyat.ust_oran(hisseler, p["genislik_n"])
    oz["genislik_ayrisma"] = (-(ust - ust.shift(63))).clip(lower=0) * (fiyat.getiri(adj, 63) > 0)
    oz["vix_degisim_21"] = vix / vix.shift(21) - 1
    oz["vix_vol_21"] = vix.pct_change().rolling(21, min_periods=10).std()
    oz["kredi_egim_60"] = kredi - kredi.shift(60)
    kor = korelasyon.ort_ikili_korelasyon(np.log(hisseler).diff(), 63)
    oz["ort_kor_63"] = kor
    oz["kor_degisim_21"] = kor - kor.shift(21)
    oz["momentum_farki"] = momentum_farki(hisseler)
    oz["dd"] = fiyat.dusus(adj, 252)
    return oz


def rejim(adj, p):
    return kural_rejim(adj, p["vol_n"], p["vol_esik"], p["trend_n"], p["min_sure"])

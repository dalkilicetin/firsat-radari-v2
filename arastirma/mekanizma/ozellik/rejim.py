"""Kural tabanli piyasa rejimi (kara kutu yok). Sadece gecmise bakar."""
import numpy as np
import pandas as pd

from mekanizma.ozellik import fiyat

REJIMLER = ("sakin_yukselis", "oynak_yukselis", "sakin_dusus", "oynak_dusus")


def kural_rejim(adj, vol_n=63, vol_esik=0.70, trend_n=200, min_sure=10, min_gecmis=252):
    """4 rejim: trend (adj > SMA_trend_n) x oynaklik (vol'un genisleyen yuzdeligi > vol_esik).
    Histerezis: yeni rejim min_sure bar ust uste surmedikce eski rejim korunur (gecikme yaratir, gecikmenin kendisi gecmise bakar)."""
    yuz = fiyat.yuzdelik_genisleyen(fiyat.vol(adj, vol_n), min_gecmis)
    sma = adj.rolling(trend_n, min_periods=trend_n).mean()
    gecerli = (yuz.notna() & sma.notna()).to_numpy()
    yuk, oyn = (adj > sma).to_numpy(), (yuz > vol_esik).to_numpy()
    ham = np.where(yuk, np.where(oyn, "oynak_yukselis", "sakin_yukselis"), np.where(oyn, "oynak_dusus", "sakin_dusus"))
    cikti = np.full(len(adj), None, dtype=object)
    mevcut, aday, say = None, None, 0
    for i in range(len(adj)):
        if not gecerli[i]:
            continue
        if mevcut is None:
            mevcut = ham[i]
        elif ham[i] == mevcut:
            aday, say = None, 0
        else:
            if ham[i] == aday:
                say += 1
            else:
                aday, say = ham[i], 1
            if say >= min_sure:
                mevcut, aday, say = aday, None, 0
        cikti[i] = mevcut
    return pd.Series(cikti, index=adj.index, dtype=object)

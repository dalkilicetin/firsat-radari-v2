"""Fiyat ozellikleri. Hepsi SADECE gecmise bakar (t anindaki deger t ve oncesiyle hesaplanir).
Pencereler 'bar' cinsindendir (gun ya da ay)."""
import bisect

import numpy as np
import pandas as pd


def dusus(adj, n=252):
    """n bar zirvesinden dusus (<=0)."""
    return adj / adj.rolling(n, min_periods=1).max() - 1


def getiri(adj, n):
    return adj / adj.shift(n) - 1


def vol(adj, n):
    """n bar log getiri standart sapmasi (yillandirilmamis)."""
    return np.log(adj).diff().rolling(n, min_periods=max(2, n // 2)).std()


def zskor(x, n=252):
    mu = x.rolling(n, min_periods=max(2, n // 2)).mean()
    sd = x.rolling(n, min_periods=max(2, n // 2)).std()
    return (x - mu) / sd.replace(0, np.nan)


def ust_oran(adj_genis, n=200):
    """Her bar icin SMA_n uzerindeki hisse orani (sadece o gun verisi ve SMA'si olanlar)."""
    sma = adj_genis.rolling(n, min_periods=n).mean()
    gecerli = sma.notna() & adj_genis.notna()
    return ((adj_genis > sma) & gecerli).sum(axis=1) / gecerli.sum(axis=1).replace(0, np.nan)


def beta(hisse, endeks, n=252):
    """Hisse(ler)in endekse n bar rolling beta'si (log getiri)."""
    rh = np.log(hisse).diff()
    re = np.log(endeks).diff()
    cov = rh.rolling(n, min_periods=n // 2).cov(re)
    var = re.rolling(n, min_periods=n // 2).var()
    return cov / var if isinstance(cov, pd.Series) else cov.div(var, axis=0)


def yuzdelik_genisleyen(x, min_n=252):
    """t anindaki degerin x[:t+1] icindeki yuzdeligi (0-1). min_n bardan once NaN."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    gecmis = []
    for i, a in enumerate(v):
        if np.isnan(a):
            continue
        bisect.insort(gecmis, a)
        if len(gecmis) >= min_n:
            out[i] = bisect.bisect_right(gecmis, a) / len(gecmis)
    return pd.Series(out, index=x.index)

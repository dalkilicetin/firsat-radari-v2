"""Gelecege bakan TEK modul. Sinyal t kapanisinda olusur, giris t+1 kapanisinda, cikis t+1+h kapanisinda."""
import numpy as np
import pandas as pd


def ileri_getiri(adj, ufuklar=(5, 21, 63, 126, 252)):
    """Seri -> DataFrame (sutun = ufuk). DataFrame -> {ufuk: DataFrame}."""
    giris = adj.shift(-1)
    if isinstance(adj, pd.Series):
        return pd.DataFrame({h: adj.shift(-(1 + h)) / giris - 1 for h in ufuklar})
    return {h: adj.shift(-(1 + h)) / giris - 1 for h in ufuklar}


def _pencere(adj, ufuk, fonk):
    ters = adj.iloc[::-1].rolling(ufuk + 1, min_periods=ufuk + 1)
    pen = getattr(ters, fonk)().iloc[::-1]           # [t, t+ufuk]
    return pen.shift(-1)                              # [t+1, t+1+ufuk]


def mae(adj, ufuk):
    """Giristen (t+1) sonra ufuk boyunca en kotu dusus (<=0)."""
    return _pencere(adj, ufuk, "min") / adj.shift(-1) - 1


def mfe(adj, ufuk):
    return _pencere(adj, ufuk, "max") / adj.shift(-1) - 1


def toparlanma_suresi(adj, tarihler, n=252):
    """Her tarih t icin t+1'den sonra fiyatin t'deki n bar zirveye ilk donusune kadar bar sayisi (donmediyse NaN)."""
    v = adj.to_numpy(dtype=float)
    out = {}
    for t in tarihler:
        i = adj.index.get_loc(t)
        zirve = np.nanmax(v[max(0, i - n + 1): i + 1])
        ileri = v[i + 1:]
        k = np.flatnonzero(ileri >= zirve)
        out[t] = float(k[0]) if len(k) else np.nan
    return pd.Series(out, dtype=float)

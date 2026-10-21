"""t sonrasi veriyi cop degerlerle degistirince t'deki ozellik degismemeli."""
import numpy as np
import pandas as pd
import pytest

from mekanizma.ozellik import fiyat

rng = np.random.default_rng(5)
N = 700
IDX = pd.bdate_range("2000-01-03", periods=N)
SERI = pd.Series(100 * np.exp(np.cumsum(0.01 * rng.standard_normal(N))), index=IDX)
GENIS = pd.DataFrame({f"S{i}": 100 * np.exp(np.cumsum(0.015 * rng.standard_normal(N))) for i in range(8)}, index=IDX)

VAKALAR = {
    "dusus": lambda s, g: fiyat.dusus(s, 100),
    "getiri": lambda s, g: fiyat.getiri(s, 20),
    "vol": lambda s, g: fiyat.vol(s, 20),
    "zskor": lambda s, g: fiyat.zskor(fiyat.vol(s, 20), 100),
    "ust_oran": lambda s, g: fiyat.ust_oran(g, 50),
    "beta": lambda s, g: fiyat.beta(g["S0"], s, 100),
    "yuzdelik": lambda s, g: fiyat.yuzdelik_genisleyen(fiyat.getiri(s, 20), 50),
}


@pytest.mark.parametrize("ad", VAKALAR)
def test_sizinti_yok(ad):
    f = VAKALAR[ad]
    tam = f(SERI, GENIS)
    for t in (300, 450, 600):
        s2, g2 = SERI.copy(), GENIS.copy()
        s2.iloc[t + 1:] = rng.uniform(1, 1000, N - t - 1)
        g2.iloc[t + 1:] = rng.uniform(1, 1000, (N - t - 1, GENIS.shape[1]))
        degisik = f(s2, g2)
        a, b = tam.iloc[t], degisik.iloc[t]
        assert (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-9, (ad, t)

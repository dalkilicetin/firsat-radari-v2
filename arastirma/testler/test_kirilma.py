import numpy as np
import pandas as pd

from mekanizma.motor import sonuc
from mekanizma.ozellik import korelasyon
from mekanizma.ozellik.rejim import kural_rejim


def test_korelasyon_uclar():
    rng = np.random.default_rng(0)
    n = 600
    ortak = rng.standard_normal(n)
    ayni = pd.DataFrame({f"S{i}": ortak for i in range(20)})
    bagimsiz = pd.DataFrame(rng.standard_normal((n, 20)))
    assert korelasyon.ort_ikili_korelasyon(ayni, 63).iloc[-1] > 0.95
    assert abs(korelasyon.ort_ikili_korelasyon(bagimsiz, 63).iloc[-1]) < 0.12


def test_gecis_hedefi_elle():
    r = pd.Series(["a", "a", "b", "b", "c", "c", "c", "a"], index=pd.bdate_range("2020-01-01", periods=8), dtype=object)
    h = sonuc.gecis_hedefi(r, 2, ["a", "b"], ["c"])
    # t=2 (b): sonraki 2 bar [b, c] -> 1 ; t=0 (a): [a, b] -> 0 ; t=4 (c) kaynakta degil -> NaN
    assert h.iloc[2] == 1 and h.iloc[0] == 0 and np.isnan(h.iloc[4])
    assert np.isnan(h.iloc[7])      # pencere dolmadi


def test_rejim_histerezis_ve_sizinti():
    rng = np.random.default_rng(3)
    n = 1500
    adj = pd.Series(100 * np.exp(np.cumsum(0.01 * rng.standard_normal(n))), index=pd.bdate_range("2000-01-03", periods=n))
    r = kural_rejim(adj, 63, 0.7, 200, 10)
    degisim = (r != r.shift(1)) & r.notna() & r.shift(1).notna()
    # histerezis: iki degisim arasi en az 10 bar
    pos = np.flatnonzero(degisim.to_numpy())
    assert len(pos) == 0 or (np.diff(pos) >= 10).all()
    adj2 = adj.copy()
    adj2.iloc[1000:] = rng.uniform(1, 500, n - 1000)
    r2 = kural_rejim(adj2, 63, 0.7, 200, 10)
    assert (r.iloc[:1000].fillna('-') == r2.iloc[:1000].fillna('-')).all()

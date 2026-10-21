import time

import numpy as np

from mekanizma.sim.piyasa import Ayar, simule


def test_tohum_ayni():
    a = Ayar(n_gun=800, n_hisse=10)
    x, y = simule(a, 3), simule(a, 3)
    assert np.allclose(x.endeks["adj"], y.endeks["adj"])
    assert not np.allclose(x.endeks["adj"], simule(a, 4).endeks["adj"])


def test_panik_geri_doner():
    # tek panik: m -0.20'ye iner, 3 yarilanma (180g) sonra ~%12.5'ine yaklasir; F etkilenmez
    a = Ayar(n_gun=700, n_hisse=5, sm=0.0, olay_zorla=[(100, "panik", 0.20, 20)], gelgit_etkisi=False)
    d = simule(a, 0).endeks
    assert d["m"].min() < -0.15
    assert abs(d["m"].iloc[120 + 180]) < 0.06
    assert abs(d["m"].iloc[-1]) < 0.02


def test_yarilanma_cok_uzunsa_donmez():
    a = Ayar(n_gun=700, n_hisse=5, sm=0.0, yarilanma=1e9, olay_zorla=[(100, "panik", 0.20, 20)], gelgit_etkisi=False)
    d = simule(a, 0).endeks
    assert d["m"].iloc[-1] < -0.19


def test_bozulma_kalici():
    a = Ayar(n_gun=1200, n_hisse=5, sm=0.0, olay_zorla=[(100, "bozulma", 0.30, 200)], gelgit_etkisi=False)
    d = simule(a, 0).endeks
    # F yaklasik 0.30 duser (gurultu ve surukleme payi var), m geri doner
    assert d["F"].iloc[320] - d["F"].iloc[100] < -0.15
    assert abs(d["m"].iloc[-1]) < 0.02
    assert d["sahm"].max() == 1.0


def test_kenetlenme_stres_artar():
    a = Ayar(n_gun=900, n_hisse=60, olay_zorla=[(400, "panik", 0.30, 30)])
    d = simule(a, 1)
    r = np.log(d.hisseler).diff().dropna()
    sakin = r.iloc[100:300].corr().to_numpy()
    stres = r.iloc[400:440].corr().to_numpy()
    iu = np.triu_indices(60, 1)
    assert stres[iu].mean() > sakin[iu].mean() + 0.1


def test_hiz():
    t0 = time.time()
    simule(Ayar(), 0)
    assert time.time() - t0 < 10

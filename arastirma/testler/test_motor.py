import numpy as np
import pandas as pd

from mekanizma.motor import sonuc
from mekanizma.motor.istatistik import blok_bootstrap_ga, ozet
from mekanizma.motor.olay import ayikla, bolumle, olay_testi


def seri(v):
    return pd.Series(v, index=pd.bdate_range("2000-01-03", periods=len(v)), dtype=float)


def test_ileri_getiri_elle():
    a = seri([100, 110, 121, 100, 90, 95])
    r = sonuc.ileri_getiri(a, [1, 2])
    # t=0: giris a[1]=110, h=1 -> a[2]=121 => +10%, h=2 -> a[3]=100 => -9.09%
    assert abs(r[1].iloc[0] - 0.10) < 1e-12
    assert abs(r[2].iloc[0] - (100 / 110 - 1)) < 1e-12
    assert r[1].iloc[-2:].isna().all() and r[2].iloc[-3:].isna().all()


def test_mae_mfe_elle():
    a = seri([100, 100, 80, 90, 120, 100])
    # t=0: giris a[1]=100, pencere a[1..3]=[100,80,90] (h=2) -> mae=-20%, mfe=0
    assert abs(sonuc.mae(a, 2).iloc[0] + 0.20) < 1e-12
    assert abs(sonuc.mfe(a, 2).iloc[0]) < 1e-12
    assert np.isnan(sonuc.mae(a, 2).iloc[-1])


def test_toparlanma():
    a = seri([100, 90, 80, 85, 95, 101, 102])
    t = a.index[1]      # t'ye kadar zirve 100; giris t+1 (80); ileri=[80,85,95,101,102]; 101 girisin 3 bar sonrasi
    assert sonuc.toparlanma_suresi(a, [t], n=10)[t] == 3
    assert np.isnan(sonuc.toparlanma_suresi(seri([100, 90, 80, 85]), [seri([1, 1]).index[1]], n=10).iloc[0])


def test_ayikla_ve_bolum():
    s = seri([0] * 30).astype(bool)
    s.iloc[[2, 3, 4, 10, 25]] = True
    ol = ayikla(s, 5)               # 2 alinir, 3-7 atlanir, 10 alinir, 25 alinir
    assert list(s.index.get_indexer(ol)) == [2, 10, 25]
    b = bolumle(ol, s.index, bosluk=10)
    assert list(b) == [0, 0, 1]    # 2-10 ayni bolum (8<10), 25 yeni


def test_ozet_ve_bootstrap():
    rng = np.random.default_rng(0)
    x = rng.normal(0.05, 0.1, 400)
    lo, hi = blok_bootstrap_ga(x)
    se = x.std(ddof=1) / np.sqrt(len(x))
    assert lo < x.mean() < hi and abs((hi - lo) - 2 * 1.645 * se) < 0.4 * 2 * 1.645 * se
    assert ozet([])["n"] == 0 and np.isnan(blok_bootstrap_ga([1, 2])[0])


def test_olay_testi_yay_bulunur():
    # her 300 barda -20% dusus (30 bar) sonra +30% toparlanma (60 bar): dibe yakin sinyal -> getiri pozitif olmali
    rng = np.random.default_rng(1)
    v, p, sinyal_gunleri = [], 100.0, []
    for k in range(10):
        for i in range(210):
            p *= np.exp(0.0002 + 0.003 * rng.standard_normal()); v.append(p)
        for i in range(30):
            p *= 0.9926; v.append(p)
        sinyal_gunleri.append(len(v) - 1)
        for i in range(60):
            p *= 1.0044; v.append(p)
    a = seri(v)
    sinyal = pd.Series(False, index=a.index); sinyal.iloc[sinyal_gunleri] = True
    r = olay_testi(a, sinyal, [21, 63], bekleme=63)
    assert r["n_olay"] == 10 and r["n_bolum"] == 10
    d = r["ufuk"]["63"]
    assert d["olay"]["ort"] > 0.10 and d["fark_olay"] > 0.08 and d["olay"]["ga_alt"] > 0
    rastgele = pd.Series(False, index=a.index); rastgele.iloc[::97] = True
    rr = olay_testi(a, rastgele, [63], bekleme=63)["ufuk"]["63"]
    assert rr["olay"]["ga_alt"] < d["olay"]["ga_alt"]

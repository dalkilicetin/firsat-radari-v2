import numpy as np

from mekanizma.veri.katalog import katalog


def test_turetilen_sutunlar():
    k = katalog().set_index("kimlik")
    r = k.loc["2020"]
    assert abs(r["dusus"] - (2237.40 / 3386.15 - 1)) < 1e-9
    # 2020-02-19 -> 2020-03-23: 23 is gunu; 2020-03-23 -> 2020-08-18: 105 is gunu
    assert r["gun_dibe"] == np.busday_count("2020-02-19", "2020-03-23")
    assert r["gun_toparlanma"] == np.busday_count("2020-03-23", "2020-08-18")
    assert abs(r["sertlik"] - r["gun_toparlanma"] / r["gun_dibe"]) < 1e-12
    assert r["hiz"] < 0 and r["vix_dipten_once"] == np.busday_count("2020-03-16", "2020-03-23")


def test_katalog_boyutu():
    k = katalog()
    assert (k.piyasa == "SPX").sum() == 13 and len(k) == 15
    assert (k["dip"] < k["zirve"]).all() and (k["toparlanma_tarih"] > k["dip_tarih"]).all()

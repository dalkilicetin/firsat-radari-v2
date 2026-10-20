"""Analiz aracı test düzeneğinin kuralları (analiz_araci_plani.md, bölüm 1)."""

import numpy as np
import pandas as pd

from radar.arac import duzenek, isaretler
from radar.research import panel


def fri(s):
    return pd.Timestamp(s)


def test_persembe_16_kesimi():
    # 2024-06-06 perşembe; 2024-06-07 cuma
    ts = pd.Series(pd.to_datetime(["2024-06-06 15:59", "2024-06-06 16:01", "2024-06-05 22:00", "2024-06-07 09:00",
                                   "2024-06-08 10:00"]))
    got = duzenek.kullanilabilir(ts).tolist()
    assert got == [fri("2024-06-07"), fri("2024-06-14"), fri("2024-06-07"), fri("2024-06-14"), fri("2024-06-14")]


def test_utc_etiketli_kayit_gec_yorumla():
    # 'Z' etiketli 15:30: gerçek UTC ise 11:30 New York olurdu; geç yorum 15:30 New York sayar → aynı hafta.
    # 'Z' etiketli 17:00: geç yorumla 17:00 New York → kesimden sonra, sonraki hafta.
    ts = pd.Series(pd.to_datetime(["2024-06-06 15:30:00+00:00", "2024-06-06 17:00:00+00:00"]))
    assert duzenek.kullanilabilir(ts).tolist() == [fri("2024-06-07"), fri("2024-06-14")]


def test_yalnizca_tarihli_kayit_gun_sonu():
    ts = pd.Series(pd.to_datetime(["2024-06-05", "2024-06-06", "2024-06-07"]))
    assert duzenek.kullanilabilir(ts, saatli=False).tolist() == [fri("2024-06-07"), fri("2024-06-07"), fri("2024-06-14")]


def test_masraf_iki_yonlu():
    brut = pd.DataFrame([[0.818181818, -1.0]])
    oran = pd.DataFrame([[0.0015, 0.0015]])
    net = duzenek.masrafli(brut, oran)
    assert abs(net.iloc[0, 0] - ((1 - 0.0015) ** 2 * 1.818181818 - 1)) < 1e-12
    assert net.iloc[0, 1] == -1.0  # iflas: masraf sonrası da −%100


def test_yakalanabilir_getiri_ornegi():
    # İşaret 10 $, alınabilecek ilk fiyat 11 $, 3 ay sonra 20 $ → %81,8 (kullanıcı örneği)
    assert round((20 / 11 - 1) * 100, 1) == 81.8


def _sec(rows):
    return pd.DataFrame(rows, columns=["cik", "symbol", "start", "end", "status", "bankrupt"])


def test_iflas_eden_hisse_sifir_sayilir_ve_birlesen_son_fiyat():
    dates = pd.date_range("2020-01-03", periods=6, freq="W-FRI")
    price = pd.DataFrame({"1": [10, 9, 8, np.nan, np.nan, np.nan], "2": [10, 11, 12, np.nan, np.nan, np.nan],
                          "3": [10, 10, 10, 10, 10, 12]}, index=dates, dtype=float)
    sec = _sec([("1", "A", dates[0], dates[2], "çıktı", True), ("2", "B", dates[0], dates[2], "çıktı", False),
                ("3", "C", dates[0], pd.NaT, "aktif", False)])
    r = panel.forward_returns(price, sec, 3)
    assert r.loc[dates[0], "1"] == -1.0          # iflas: −%100
    assert abs(r.loc[dates[0], "2"] - 0.2) < 1e-12  # birleşme/çıkış: son geçerli fiyat (12)
    assert r.loc[dates[0], "3"] == 0.0


def test_son_gunlerde_pencere():
    dates = pd.date_range("2024-01-05", periods=20, freq="W-FRI")
    ev = pd.DataFrame({"cik": ["1"], "gun": [dates[2]]})
    w = isaretler._son_gunlerde(ev, dates, pd.Index(["1"]), 90)
    on = w["1"]
    assert not on.iloc[1] and on.iloc[2] and on.iloc[14] and not on.iloc[15]  # 13 hafta açık


def test_farkli_alici_sayisi():
    dates = pd.date_range("2024-01-05", periods=20, freq="W-FRI")
    pairs = pd.DataFrame({"cik": ["1", "1", "1"], "owner_cik": [10, 11, 10], "gun": [dates[0], dates[5], dates[6]]})
    n = isaretler._farkli_alici(pairs, dates, pd.Index(["1"]), 90)["1"]
    assert n.iloc[0] == 1 and n.iloc[5] == 2 and n.iloc[12] == 2 and n.iloc[13] == 2 and n.iloc[17] == 2 and n.iloc[18] == 1 and n.iloc[19] == 0

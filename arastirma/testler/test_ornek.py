import pandas as pd
from pathlib import Path

from mekanizma.veri import ornek

MINI = Path(__file__).parent / "ornek" / "mini_sonuclar.json"


def test_aylik_hizalama_ve_yon():
    df = ornek.aylik(MINI)
    assert df.index[-1] == pd.Timestamp("2026-10-31")
    assert df.index[0] == pd.Timestamp("2026-06-30")
    assert df["AAA"].iloc[-1] == 50 and df["AAA"].iloc[0] == 10   # closes[0] en yeni
    assert df["BBB"].isna().sum() == 2                              # kisa seri basa NaN
    assert df["BBB"].iloc[-1] == 5


def test_profil():
    p = ornek.profil(MINI)
    assert p.loc["AAA", "sektor"] == "Software"
    assert p.loc["BBB", "mcap"] == 50


def test_gercek_spy_2022():
    df = ornek.aylik()
    spy = df["SPY"]
    assert 340 < spy["2022-09-30"] < 375
    dusus = spy["2022-09-30"] / spy["2022-01-31":"2022-01-31"].iloc[0] - 1
    assert -0.27 < dusus < -0.15

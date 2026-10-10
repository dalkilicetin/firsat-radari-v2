"""Panel ve değerlendirme düzeneği testleri (küçük sentetik verilerle)."""

import numpy as np
import pandas as pd

from radar import identity
from radar.research import evaluate as ev
from radar.research import panel


def test_reverse_split_adjustment():
    px = np.array([1.0, 1.1, 11.0, 12.0])  # 1:10 ters bölünme
    adj = panel.adjust_reverse_splits(px)
    assert np.allclose(adj, [10.0, 11.0, 11.0, 12.0])
    crash = np.array([10.0, 2.0, 2.1])  # gerçek çöküşe dokunulmaz
    assert np.allclose(panel.adjust_reverse_splits(crash), crash)


def test_weekly_last_staleness():
    dates = pd.date_range("2024-01-05", periods=9, freq="W-FRI")  # son Cuma, son gözlemden 36 gün sonra
    df = pd.DataFrame({"cik": [1, 1], "date": pd.to_datetime(["2024-01-03", "2024-01-25"]), "price": [10.0, 12.0]})
    w = panel.weekly_last(df, "price", dates)
    assert w[1].iloc[0] == 10.0 and w[1].iloc[3] == 12.0
    assert np.isnan(w[1].iloc[-1])  # son gözlemden 30+ gün sonra fiyat yok sayılır


def _toy():
    dates = pd.date_range("2024-01-05", periods=6, freq="W-FRI")
    price = pd.DataFrame({"1": [10, 11, 12, 13, 14, 15], "2": [10, 10, 10, np.nan, np.nan, np.nan],
                          "3": [10, 10, 8, np.nan, np.nan, np.nan]}, index=dates, dtype=float)
    sec = pd.DataFrame({"cik": [1, 2, 3], "start": [dates[0]] * 3,
                        "end": [pd.NaT, dates[2] + pd.Timedelta(days=3), dates[2] + pd.Timedelta(days=3)],
                        "status": ["aktif", "çıktı", "çıktı"], "bankrupt": [False, False, True]})
    return price, sec


def test_forward_returns_exit_values():
    price, sec = _toy()
    r = panel.forward_returns(price, sec, 2)
    assert r["1"].iloc[0] == 12 / 10 - 1
    assert r["2"].iloc[1] == 0.0          # satın alma: son fiyatla (10) çıkış
    assert r["3"].iloc[1] == -1.0         # iflas: değer 0
    assert np.isnan(r["2"].iloc[3])       # çıkıştan sonra üye değil


def test_identity_ticker_history_filters_noise():
    ins = pd.DataFrame({"issuer_cik": [1, 1, 1, 2], "ticker": ["ABC", "ABC", "NONE", "XYZ"],
                        "filing_date": pd.to_datetime(["2020-01-01", "2021-01-01", "2020-06-01", "2020-01-01"])})
    h = identity.ticker_history(ins)
    assert h.to_dict("records") == [{"cik": 1, "ticker": "ABC", "first_seen": pd.Timestamp("2020-01-01"),
                                     "last_seen": pd.Timestamp("2021-01-01"), "n": 2}]


def test_evaluate_detects_perfect_and_random_signal(monkeypatch):
    rng = np.random.default_rng(1)
    dates = pd.date_range("2016-01-01", periods=80, freq="W-FRI")
    cols = [str(i) for i in range(120)]
    price = pd.DataFrame(np.exp(np.cumsum(rng.normal(0, 0.05, (80, 120)), axis=0)) * 10, index=dates, columns=cols)
    sec = pd.DataFrame({"cik": range(120), "start": dates[0], "end": pd.NaT, "status": "aktif", "bankrupt": False})
    ev._RET_CACHE.clear()
    perfect = panel.forward_returns(price, sec, 1).reindex(dates)
    good = ev.evaluate(perfect, price, sec, "p", {"1h": 1}).rows[0]
    noise = ev.evaluate(pd.DataFrame(rng.random((80, 120)), index=dates, columns=cols), price, sec, "r", {"1h": 1}).rows[0]
    assert good["IC"] > 0.99 and good["fark"] > 0
    assert abs(noise["IC"]) < 0.05
    ev._RET_CACHE.clear()


def test_pit_rolling_count_uses_next_friday():
    from radar.research import pit
    dates = pd.date_range("2024-01-05", periods=4, freq="W-FRI")
    ev = pd.DataFrame({"cik": [7, 7], "date": pd.to_datetime(["2024-01-05", "2024-01-10"])})
    c = pit.rolling_count(ev, dates, ["7"], 30)
    # Cuma günü olan olay o Cuma değil, bir sonraki Cuma'dan itibaren sayılır.
    assert c["7"].tolist() == [0.0, 2.0, 2.0, 2.0]


def test_event_excess_uses_own_universe_and_hit_rate():
    dates = pd.date_range("2016-01-01", periods=30, freq="W-FRI")
    cols = [str(i) for i in range(100)]
    # 0-49 "büyük" hisseler her hafta %1, 50-99 "küçük" hisseler %-1 getiri veriyor.
    growth = np.where(np.arange(100) < 50, 1.01, 0.99)
    price = pd.DataFrame(np.cumprod(np.tile(growth, (30, 1)), axis=0), index=dates, columns=cols)
    sec = pd.DataFrame({"cik": range(100), "start": dates[0], "end": pd.NaT, "status": "aktif", "bankrupt": False})
    big = pd.DataFrame(np.tile(np.arange(100) < 50, (30, 1)), index=dates, columns=cols)
    flag = big & pd.DataFrame(np.tile(np.arange(100) % 2 == 0, (30, 1)), index=dates, columns=cols)
    ev._RET_CACHE.clear()
    # Tüm hisselere göre büyük hisselerdeki olay pozitif görünür (büyüklük etkisi)...
    biased = ev.evaluate_event(flag, price, sec, "x", {"1h": 1}).rows[0]
    # ...ama kendi evrenine (büyükler) göre fazla getiri sıfırdır.
    fair = ev.evaluate_event(flag, price, sec, "x", {"1h": 1}, universe=big).rows[0]
    assert biased["ort_fazla"] > 0.005 and abs(fair["ort_fazla"]) < 1e-9
    assert 0 <= fair["isabet"] <= 1 and biased["isabet"] == 1.0
    ev._RET_CACHE.clear()

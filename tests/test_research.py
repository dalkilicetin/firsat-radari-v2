"""Panel ve değerlendirme düzeneği testleri (küçük sentetik verilerle)."""

import pytest
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


def test_text_changes_lazy_prices_similarity():
    from radar.research import road1
    t = pd.DataFrame({
        "cik": [1, 1, 1], "accepted": pd.to_datetime(["2020-03-01", "2021-03-01", "2022-03-01"]),
        "going_concern": [False, False, True],
        "item1": ["we sell widgets worldwide", "we sell widgets worldwide", "we now mine bitcoin exclusively"],
        "item1a": ["risk " * 1000, "risk " * 1000, "risk " * 3000], "item7": ["revenue grew", "revenue grew", "revenue fell"]})
    ch = road1.text_changes(t)
    assert np.isnan(ch.sim_item1.iloc[0])
    assert ch.sim_item1.iloc[1] > 0.99 and ch.sim_item1.iloc[2] < 0.1
    assert abs(ch.risk_len_growth.iloc[2] - 2.0) < 0.01


def test_theme_wind_uses_completed_months_and_momentum(monkeypatch):
    from radar.research import road4
    dates = pd.date_range("2016-01-01", periods=70, freq="W-FRI")
    days = pd.date_range("2015-01-01", dates[-1], freq="D")
    # HOT teması son 4 haftada patlıyor, COLD sabit; çok sayıda yaygın tema dışlanacak.
    day = pd.DataFrame([{"kind": "day_theme", "date": d, "cik": pd.NA, "theme": th,
                         "count": (100 if (th == "HOT" and d > dates[-5]) else 10)} for d in days for th in ("HOT", "COLD")])
    common = pd.DataFrame([{"kind": "day_theme", "date": days[0], "cik": pd.NA, "theme": f"C{i}", "count": 10**6} for i in range(50)])
    months = pd.date_range("2015-01-01", dates[-1], freq="MS")
    pairs = pd.DataFrame([{"kind": "month_cik_theme", "date": m, "cik": c, "theme": th, "count": 30}
                          for m in months for c, th in ((1, "HOT"), (2, "COLD"))])
    monkeypatch.setattr(road4, "load_themes", lambda: (pd.concat([day, common]), pairs))
    price = pd.DataFrame(1.0, index=dates, columns=["1", "2"])
    w = road4.signals({"price": price})["tema_ruzgari"]
    # HOT payı 0,5 → 0,91 (log ≈ +0,6); COLD payı 0,5 → 0,09 (log ≈ −1,7)
    assert w["1"].iloc[-1] > 0.5 and w["2"].iloc[-1] < -1.5
    assert np.isnan(w["1"].iloc[0])  # ilk ay: tamamlanmış ay yok


def test_identity_name_matching_for_foreign_issuers():
    assert identity.norm_name("TRANSGLOBE ENERGY CORP COM") == identity.norm_name("TransGlobe Energy Corp") == "transglobe energy"
    assert identity.norm_name("ACME HOLDINGS LTD SPONSORED ADR") == "acme"
    missing = pd.DataFrame({"cik": [5], "name": ["TransGlobe Energy Corp"], "end": [pd.Timestamp("2022-10-20")]})
    ftd = pd.DataFrame({"settle_date": pd.to_datetime(["2022-09-01", "2015-01-01"]), "symbol": ["TGA", "OLD"],
                        "description": ["TRANSGLOBE ENERGY CORP COM", "TRANSGLOBE ENERGY CORP COM"]})
    assert identity.match_by_name(missing, ftd) == {5: "TGA"}
    spac = pd.DataFrame({"cik": [6], "name": ["Healthwell Acquisition Corp I"], "end": [pd.Timestamp("2023-12-04")]})
    f2 = pd.DataFrame({"settle_date": pd.to_datetime(["2023-11-01"] * 3), "symbol": ["HWELW", "HWELW", "HWEL"],
                       "description": ["HEALTHWELL ACQUISITION CORP I", "HEALTHWELL ACQUISITION CORP I", "HEALTHWELL ACQUISITION CORP I"]})
    assert identity.match_by_name(spac, f2) == {6: "HWEL"}  # varant sembolü (W eki) seçilmez


def test_shares_outstanding_prefers_total_then_sums_classes():
    from radar.research import fundamentals
    fin = pd.DataFrame({
        "adsh": ["a", "b", "b", "c", "c"], "cik": [1, 2, 2, 3, 3], "accepted": pd.Timestamp("2024-05-01"),
        "tag": ["EntityCommonStockSharesOutstanding"] * 3 + ["EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"],
        "qtrs": 0, "ddate": pd.Timestamp("2024-04-30"),
        "segments": ["", "ClassOfStock=A;", "ClassOfStock=B;", "ClassOfStock=A;", ""],
        "value": [100.0, 30.0, 70.0, 5.0, 900.0]})
    s = fundamentals.shares_outstanding(fin).set_index("cik").value
    assert s[1] == 100 and s[2] == 100  # tek değer; sınıfların toplamı
    assert s[3] == 5  # kapak sayfası (dei) sınıf toplamı, bilanço kaleminden önce gelir


def test_walk_forward_uses_only_realized_returns():
    from radar.research import model
    rng = np.random.default_rng(3)
    T, N, h = 120, 200, 4
    dates = pd.date_range("2016-01-01", periods=T, freq="W-FRI")
    x = rng.random((T, N)).astype(np.float32) - 0.5
    sign = np.where(np.arange(T) < 80, 1.0, -1.0)[:, None]  # 80. haftada ilişki tersine döner
    y = (sign * x + 0.1 * rng.normal(size=(T, N))).astype(np.float32)
    y[T - h:] = np.nan
    fit = model.walk_forward({"f": x}, y, h, dates, ["f"], np.ones((T, N), bool))
    first = np.argmax(np.isfinite(fit.pred).any(axis=1))
    assert first >= model.MIN_TRAIN_WEEKS + h - 1          # öğrenme için yeterli gerçekleşmiş hafta yok
    w = fit.weights["f"]
    # 80+4. haftaya kadar ters ilişkiden hiçbir hafta gerçekleşmediği için ağırlık hâlâ pozitif olmalı.
    assert (w[w.index <= dates[80 + h - 1]] > 0).all()
    assert w.iloc[-1] < w.iloc[0]                            # sonra ters ilişkiyi öğrenmeye başlar


def test_ranked_inputs_missing_is_neutral_and_events_centered():
    from radar.research import model
    dates = pd.date_range("2016-01-01", periods=2, freq="W-FRI")
    cont = pd.DataFrame([[1.0, 2.0, np.nan, 4.0]] * 2, index=dates, columns=list("abcd"))
    ev = pd.DataFrame([[1.0, 0.0, 0.0, 0.0]] * 2, index=dates, columns=list("abcd"))
    uni = pd.DataFrame(True, index=dates, columns=list("abcd"))
    X = model.ranked_inputs({"c": ("yol1", cont), "e": ("yol3", ev)}, uni)
    assert X["c"][0, 2] == 0.0 and X["c"][0, 3] > X["c"][0, 0]
    assert abs(X["e"][0].sum()) < 1e-6 and X["e"][0, 0] > 0


def test_backtest_simulation_costs_and_exit():
    from radar.research import backtest
    dates = pd.date_range("2020-01-03", periods=20, freq="W-FRI")
    cols = [str(i) for i in range(60)]
    price = pd.DataFrame(100.0, index=dates, columns=cols)
    price["0"] = 100.0 * (1.1 ** np.arange(20))  # en iyi hisse her hafta %10
    sec = pd.DataFrame({"cik": cols, "symbol": cols, "name": cols, "start": dates[0], "end": pd.NaT,
                        "price_source": "yahoo", "status": "aktif", "transferred_from_other": False, "bankrupt": False})
    p = {"price": price, "raw": price, "dollar_volume": pd.DataFrame(1e8, index=dates, columns=cols), "securities": sec}
    score = pd.DataFrame(0.0, index=dates, columns=cols)
    score["0"] = 1.0
    uni = pd.DataFrame(True, index=dates, columns=cols)
    sim = backtest.simulate(score, p, uni, how=1, rebalance=4, dates=dates[:-4])
    r = sim.returns
    assert np.allclose(r.brut, 1.1 ** 4 - 1)
    assert r.maliyet.iloc[0] == pytest.approx(0.0005)  # ilk alım: tek yön
    assert (r.maliyet.iloc[1:] == 0).all()  # aynı hisse tutuluyor: devir yok
    assert np.allclose(r.kiyas, ((1.1 ** 4 - 1) / 60))


def test_big_win_target():
    from radar.research import model
    dates = pd.date_range("2020-01-03", periods=60, freq="W-FRI")
    price = pd.DataFrame({"a": np.linspace(10, 40, 60), "b": 10.0})
    price.index = dates
    sec = pd.DataFrame({"cik": ["a", "b"], "symbol": ["a", "b"], "name": ["a", "b"], "start": dates[0], "end": pd.NaT,
                        "price_source": "yahoo", "status": "aktif", "transferred_from_other": False, "bankrupt": False})
    y = model.TARGETS["kazanan_100"](price, sec, 52, pd.DataFrame(True, index=dates, columns=["a", "b"]))
    assert y[0, 0] == 1.0 and y[0, 1] == 0.0
    assert np.isnan(y[-1]).all()  # getirisi henüz bilinmiyor

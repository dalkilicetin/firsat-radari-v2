import numpy as np
import pandas as pd

from radar.weekly import pdf, snapshot


def test_explain_skips_missing_and_absent_events():
    cols = ["a"]
    contrib = pd.DataFrame({"s1": [0.02], "s2": [-0.01], "olay": [-0.005], "eksik": [0.0]}, index=cols)
    level = pd.DataFrame({"s1": [90.0], "s2": [20.0], "olay": [0.0], "eksik": [np.nan]}, index=cols)
    out = snapshot.explain("a", contrib, level, {"olay"})
    assert [x[0] for x in out] == ["s1", "s2"]


def test_reason_text_direction():
    assert "yüksek" in pdf.reason_text(("kazanc_getirisi", 0.01, "sira", 91.0))
    assert "düşük" in pdf.reason_text(("arge_yogunlugu", 0.01, "sira", 5.0))
    assert pdf.reason_text(("devamlilik_suphesi", -0.01, "olay", 1.0)).endswith("<b>var</b>")
    assert pdf._money(2.5e5) == "250 bin $" and pdf._money(3e9) == "3.0 mr $"

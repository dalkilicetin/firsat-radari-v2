"""Finansal oranlar ve teknik göstergeler (hisse × hafta). SEC XBRL kalemleri, rapor kabulünden sonraki ilk Cuma'dan itibaren.

Değerleme: defter_fiyat (F/DD tersi), satis_fiyat (F/S tersi), favok_fd (FD/FAVÖK tersi), temettu_verimi, nakit_piyasa
Kârlılık: ozsermaye_karliligi, aktif_karliligi, brut_kar_aktif (Novy-Marx), brut_marj, faaliyet_marji
Bilanço sağlığı: borc_ozsermaye, cari_oran, faiz_karsilama, altman_z, piotroski_f
Büyüme: kar_buyumesi, hisse_sayisi_degisimi
Teknik (haftalık fiyattan): rsi_14h, ort_10h_uzaklik (~50 gün), ort_40h_uzaklik (~200 gün), macd, bollinger_konum
Not: 'ters' oranlar (kazanç/fiyat gibi) sıfır ve negatif paydalarda da anlamlı kaldığı için F/K yerine K/F kullanılır.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar.research import fundamentals
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import REVENUE, annual, balance, by_filing, load_fin

EQUITY = ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"]
DEBT_LT = ["LongTermDebtNoncurrent", "LongTermDebt"]
DEBT_ST = ["LongTermDebtCurrent", "DebtCurrent"]
CASH = ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"]
DA = ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "DepreciationAmortizationAndAccretionNet"]
DIV = ["PaymentsOfDividends", "PaymentsOfDividendsCommonStock"]


def signals(p: dict) -> dict[str, pd.DataFrame]:
    price, raw = p["price"], p["raw"]
    dates, cols = price.index, price.columns
    all_fin = load_fin()
    fin = fundamentals.plain(all_fin)

    def P(df: pd.DataFrame, col: str = "value") -> pd.DataFrame:
        return pit(df.rename(columns={"accepted": "date"})[["cik", "date", col]].rename(columns={col: "value"}),
                   dates, cols, FUNDAMENTAL_MAX_AGE).astype("float32")

    B = lambda tags: P(balance(fin, tags))
    A = lambda tags: P(annual(fin, tags))
    shares = fundamentals.shares_wide(fundamentals.shares_outstanding(all_fin), price, raw).astype("float32")  # bölünmeye göre düzeltilmiş
    mcap = (shares * raw).where(shares * raw > 0)
    equity, assets, liab = B(EQUITY), B(["Assets"]), B(["Liabilities"])
    cur_a, cur_l = B(["AssetsCurrent"]), B(["LiabilitiesCurrent"])
    cash = B(CASH)
    debt = B(DEBT_LT).fillna(0) + B(DEBT_ST).fillna(0)
    retained = B(["RetainedEarningsAccumulatedDeficit"])
    rev, ni, gp, op = A(REVENUE), A(["NetIncomeLoss", "ProfitLoss"]), A(["GrossProfit"]), A(["OperatingIncomeLoss"])
    da, interest, div = A(DA), A(["InterestExpense", "InterestExpenseNonoperating", "InterestExpenseDebt"]), A(DIV)
    ocf = A(["NetCashProvidedByUsedInOperatingActivities"])
    nig = by_filing(fin, ["NetIncomeLoss", "ProfitLoss"], [1, 4])
    nig = nig.assign(value=((nig.cur - nig.prev) / nig.prev.abs()).where(nig.prev.abs() > 0))
    earn_growth = P(nig)

    pos = lambda x: x.where(x > 0)
    ev = mcap + debt - cash.fillna(0)
    ebitda = op + da.fillna(0)
    roa = ni / pos(assets)
    lev = debt / pos(assets)
    cr = cur_a / pos(cur_l)
    gm = gp / pos(rev)
    turnover = rev / pos(assets)
    lag = lambda x: x.shift(52)
    # Piotroski F-skoru (9 kriter; eksik veri o kriteri 0 sayar; ROA, nakit akışı ve geçen yıl ROA bilinmeli)
    crit = [roa > 0, ocf > 0, roa > lag(roa), ocf > ni, lev < lag(lev), cr > lag(cr),
            shares <= lag(shares) * 1.01, gm > lag(gm), turnover > lag(turnover)]
    have = (roa.notna() & ocf.notna() & lag(roa).notna()).astype(float)
    pf = sum(c.astype("float32") for c in crit).where(have > 0)
    # Altman Z (halka açık imalat sürümü; finans dışı faaliyet şirketleri için kaba bir iflas riski ölçüsü)
    ta = pos(assets)
    z = (1.2 * (cur_a - cur_l) / ta + 1.4 * retained / ta + 3.3 * op / ta + 0.6 * mcap / pos(liab) + 1.0 * rev / ta)

    # Teknik göstergeler (haftalık kapanış)
    w = price
    chg = w.diff()
    up, dn = chg.clip(lower=0).rolling(14, min_periods=10).mean(), (-chg.clip(upper=0)).rolling(14, min_periods=10).mean()
    rsi = 100 - 100 / (1 + up / dn.replace(0, np.nan))
    ma10, ma40 = w.rolling(10, min_periods=8).mean(), w.rolling(40, min_periods=30).mean()
    ema = lambda n: w.ewm(span=n, min_periods=n).mean()
    macd = (ema(12) - ema(26)) / w
    mid, sd = w.rolling(20, min_periods=15).mean(), w.rolling(20, min_periods=15).std()

    c = lambda x, lo, hi: x.clip(lo, hi).astype("float32")
    return {
        "defter_fiyat": c(equity / mcap, -5, 5),
        "satis_fiyat": c(rev / mcap, 0, 20),
        "favok_fd": c(ebitda / pos(ev), -2, 2),
        "temettu_verimi": c(div.abs().fillna(0) / mcap, 0, 0.3).where(mcap.notna()),
        "nakit_piyasa": c(cash / mcap, 0, 5),
        "ozsermaye_karliligi": c(ni / pos(equity), -3, 3),
        "aktif_karliligi": c(roa, -2, 2),
        "brut_kar_aktif": c(gp / ta, -1, 3),
        "brut_marj": c(gm, -2, 1),
        "faaliyet_marji": c(op / pos(rev), -5, 1),
        "borc_ozsermaye": c(debt / pos(equity), 0, 20),
        "cari_oran": c(cr, 0, 20),
        "faiz_karsilama": c(op / pos(interest), -50, 100),
        "altman_z": c(z, -10, 30),
        "piotroski_f": pf.astype("float32"),
        "kar_buyumesi": c(earn_growth, -5, 5),
        "hisse_sayisi_degisimi": c(shares / lag(shares) - 1, -0.5, 2),
        "rsi_14h": rsi.astype("float32"),
        "ort_10h_uzaklik": c(w / ma10 - 1, -1, 3),
        "ort_40h_uzaklik": c(w / ma40 - 1, -1, 5),
        "macd": c(macd, -1, 1),
        "bollinger_konum": c((w - mid) / (2 * sd), -3, 3),
    }

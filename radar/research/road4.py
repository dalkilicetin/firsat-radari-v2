"""4. yol: temadan hisseye (LLM'siz, tam otomatik).

1. Tema ivmesi: her hafta her GDELT temasının son 4 haftadaki haber payı / önceki 52 hafta payı (log).
2. Şirketin tema maruziyeti: son 12 ayda şirketin adının geçtiği makalelerde temaların dağılımı
   (ay bittikten sonra kullanılır).
3. Tema rüzgârı = Σ_tema maruziyet × ivme. Her habere çıkan çok yaygın temalar (ilk COMMON_DROP) dışlanır.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import archive

COMMON_DROP = 50   # en yaygın temalar ayırt edici değildir
MAX_THEMES = 4000  # şirket-tema eşleşmesi en yoğun temalar

# 4. aşama ön kaydı (sonuçlara bakılmadan, 2026-10-10'da sabitlendi): (ad, kısa pencere, uzun pencere, dışlanan yaygın tema)
VARIANTS = [
    ("tema_ruzgari", 4, 52, 50),                 # 3. aşamadaki temel sürüm
    ("tema_ruzgari_v1_uzun", 13, 104, 50),       # V1: uzun vadeli tema trendi
    ("tema_ruzgari_v2_nadir", 4, 52, 500),       # V2: yalnızca nadir/özgül temalar
    ("tema_ruzgari_v3_uzun_nadir", 13, 104, 500),  # V3: ikisi birden
]


def load_themes() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = archive.load("gdelt_themes")
    return df[df.kind == "day_theme"], df[df.kind == "month_cik_theme"]


def theme_momentum(day: pd.DataFrame, dates: pd.DatetimeIndex, themes: list[str], short: int = 4, long: int = 52) -> pd.DataFrame:
    d = day[day.theme.isin(themes)]
    w = d.assign(friday=d.date + pd.offsets.Week(weekday=4, n=1)).pivot_table(
        index="friday", columns="theme", values="count", aggfunc="sum").reindex(dates).fillna(0)
    share = w.div(w.sum(axis=1).replace(0, np.nan), axis=0)
    recent = share.rolling(short).mean()
    base = share.shift(short).rolling(long, min_periods=long // 2).mean()
    return np.log((recent + 1e-6) / (base + 1e-6)).where(base > 0)


def signals(p: dict, variants=None) -> dict[str, pd.DataFrame]:
    day, pairs = load_themes()
    out = {}
    for name, short, long, drop in (variants or VARIANTS[:1]):
        out[name] = wind_signal(p, day, pairs, short, long, drop)
    return out


def wind_signal(p: dict, day: pd.DataFrame, pairs: pd.DataFrame, short: int, long: int, drop: int) -> pd.DataFrame:
    price = p["price"]
    dates, cols = price.index, price.columns
    common = day.groupby("theme")["count"].sum().nlargest(drop).index
    pairs = pairs[~pairs.theme.isin(common)]
    themes = list(pairs.groupby("theme")["count"].sum().nlargest(MAX_THEMES).index)
    pairs = pairs[pairs.theme.isin(themes)]
    mom = theme_momentum(day, dates, themes, short, long)

    pairs = pairs.assign(cik=pairs.cik.astype(str))
    pairs = pairs[pairs.cik.isin(set(cols))]
    theme_idx = {t: i for i, t in enumerate(themes)}
    cik_idx = {c: i for i, c in enumerate(cols)}
    pairs = pairs.assign(ci=pairs.cik.map(cik_idx), ti=pairs.theme.map(theme_idx))

    wind = np.full((len(dates), len(cols)), np.nan)
    exposure_cache: dict[pd.Timestamp, tuple] = {}
    for i, t in enumerate(dates):
        key = (t.to_period("M") - 1).to_timestamp()  # t'den önce tamamlanmış son ay
        if key not in exposure_cache:
            win = pairs[(pairs.date > key - pd.DateOffset(months=12)) & (pairs.date <= key)]
            agg = win.groupby(["ci", "ti"])["count"].sum().reset_index()
            total = agg.groupby("ci")["count"].transform("sum")
            agg = agg[total >= 20]  # en az 20 tema geçişi olan şirketler
            exposure_cache[key] = (agg.ci.to_numpy(), agg.ti.to_numpy(),
                                   (agg["count"] / total[total >= 20]).to_numpy())
        ci, ti, w = exposure_cache[key]
        if len(ci) == 0:
            continue
        row = mom.loc[t].reindex(themes)
        if row.isna().all():  # ivme henüz hesaplanamıyor: sinyal yok (0 değil)
            continue
        m_t = row.fillna(0).to_numpy()
        score = np.bincount(ci, weights=w * m_t[ti], minlength=len(cols))
        has = np.bincount(ci, minlength=len(cols)) > 0
        wind[i, has] = score[has]
    return pd.DataFrame(wind, index=dates, columns=cols)

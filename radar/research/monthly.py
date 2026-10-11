"""Aylık belirti çerçevesi: python -m radar.research.monthly

Her ayın ilk Cuması (2010→) için: alınabilir faaliyet şirketleri × o gün bilinen bütün belirtiler (yıl içi yüzdelik değil,
o ayın kesitindeki yüzdelik; olaylar 0/1) + haber konusu belirtileri (2015→) + sonraki 4 haftanın getirisi
(arada borsadan çıkanlar çıkış değeriyle, iflas 0).
Çıktı: data/derived/aylik_cerceve.parquet, data/derived/aylik_cerceve_olaylar.json (hedef arama motoru okur).
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import hindsight as hs
from radar.research import news_topics, panel, road4

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
EVENTS = config.ROOT / "data" / "derived" / "aylik_cerceve_olaylar.json"
H = 4  # hafta


def month_starts(dates: pd.DatetimeIndex) -> list[int]:
    s = pd.Series(range(len(dates)), index=dates)
    first = s.groupby(dates.to_period("M")).min()
    return [int(i) for i in first.to_numpy() if dates[i].year >= 2010 and i + H < len(dates)]


def main() -> pd.DataFrame:
    t0 = time.time()
    p, sigs, inv, etf, sector = hs.prepare()
    price, sec, dates = p["price"], p["securities"], p["price"].index
    fwd = panel.forward_returns(price, sec, H).reindex(dates)
    idx = month_starts(dates)
    events = sorted(n for n, df in sigs.items() if hs.is_event(df))
    day, pairs = road4.load_themes()
    news = news_topics.features(day, pairs, dates[idx], price.columns)
    print(f"hazır ({round(time.time() - t0)} sn), {len(idx)} ay, {len(sigs)} belirti + {len(news)} haber belirtisi", flush=True)
    sym = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
    rows = []
    for t in idx:
        d = dates[t]
        u = inv.iloc[t]
        r = fwd.iloc[t][u].dropna()
        if len(r) < 200:
            continue
        f = {"tarih": d, "yil": d.year, "getiri": r.to_numpy(), "sektor": sector.reindex(r.index).to_numpy(),
             "sembol": sym.reindex(r.index).to_numpy()}
        for n, df in sigs.items():
            v = df.iloc[t].reindex(r.index)
            f[n] = ((v.fillna(0) > 0).astype(np.float32) if n in events else v.rank(pct=True).astype(np.float32)).to_numpy()
        for n, df in news.items():
            f[n] = df.loc[d].reindex(r.index).rank(pct=True).astype(np.float32).to_numpy()
        rows.append(pd.DataFrame(f, index=r.index))
    df = pd.concat(rows)
    df.index.name = "cik"
    FRAME.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(FRAME)
    EVENTS.write_text(json.dumps(events, ensure_ascii=False))
    print(f"{len(df):,} satır, {df.tarih.nunique()} ay ({round(time.time() - t0)} sn) → {FRAME}")
    return df


if __name__ == "__main__":
    main()

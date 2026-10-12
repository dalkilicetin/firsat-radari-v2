"""main dalındaki v5.16 'TREND + DÜZELTME' kuralının 2010–2025 geçmiş testi: python -m radar.research.trend_duzeltme

Kural (scanner.mjs ile aynı mantık, aylık): her ayın ilk Cuması
- mom = 12-3 momentum (52 hafta getirisi, son 13 hafta hariç) → evrende yüzdelik ≥ 0,70
- pull = 3-1 getiri (son 13 haftanın, son 4 hafta hariç kısmı) → düşük olan iyi: (1 − yüzdelik) ≥ 0,50
- sağlam: piyasa değeri ≥ 2 mlr $ ve son yıllık net kâr > 0
- sıralama: momPct + pullPct, ilk K hisse; 1 ay ve 3 ay tutma, maliyet düşülür.
Kural main dalında 3 aylık canlı veriyle bulundu; burada 16 yıllık geçmişte, kuralın hiçbir parametresi değiştirilmeden ölçülür.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, library, panel, sectors
from radar.research.backtest import cost_rate

OUT = config.ROOT / "reports" / "research" / "trend_duzeltme.json"


def main(k: int = 10) -> dict:
    p = panel.build()
    price, raw, dv, dates = p["price"], p["raw"], p["dollar_volume"], p["price"].index
    inv = sectors.operating_universes(p)["yatırılabilir (≥5 $, ≥1 M$/gün)"]
    sigs = {**library.load_group("piyasa", p), **library.load_group("road1", p)}
    mcap = np.exp(-sigs["kucuk_boyut"])  # kucuk_boyut = −log(hisse × fiyat)
    profitable = sigs["kazanc_getirisi"] > 0
    mom = price.shift(13) / price.shift(52) - 1
    pull = price.shift(4) / price.shift(13) - 1
    spy = context.etf_prices(dates)["SPY"]
    res = {}
    for hold in (4, 13):
        fwd = panel.forward_returns(price, p["securities"], hold).reindex(dates)
        rows, held = [], {}
        months = pd.Series(range(len(dates)), index=dates).groupby(dates.to_period("M")).min()
        idxs = [i for i in months if dates[i].year >= 2010 and i + hold < len(dates)]
        idxs = idxs[::hold // 4]  # çakışmasız tutma
        for i in idxs:
            u = inv.iloc[i].fillna(False)
            m, pl = mom.iloc[i][u].dropna(), pull.iloc[i][u].dropna()
            common = m.index.intersection(pl.index)
            mp, pp = m[common].rank(pct=True), 1 - pl[common].rank(pct=True)
            solid = (mcap.iloc[i].reindex(common) >= 2e9) & profitable.iloc[i].reindex(common).fillna(False)
            ok = (mp >= 0.7) & (pp >= 0.5) & solid
            pick = (mp + pp)[ok].sort_values(ascending=False).head(k).index
            r = fwd.iloc[i].reindex(pick).dropna()
            if r.empty:
                continue
            rate = dict(zip(r.index, cost_rate(dv.iloc[i].reindex(r.index).fillna(0)).to_numpy()))
            c = (sum(v for x, v in rate.items() if x not in held) + sum(v for x, v in held.items() if x not in rate)) / len(r)
            held = rate
            ew = fwd.iloc[i][u].mean()
            s = float(spy.iloc[i + hold] / spy.iloc[i] - 1)
            rows.append({"tarih": dates[i], "net": float(r.mean() - c), "spy": s, "esit": float(ew), "n": len(r)})
        df = pd.DataFrame(rows).set_index("tarih")
        yearly = df.groupby(df.index.year).apply(lambda g: pd.Series({"model": np.prod(1 + g.net) - 1, "spy": np.prod(1 + g.spy) - 1,
                                                                        "esit": np.prod(1 + g.esit) - 1}))
        res[f"{hold}h"] = {"yillik_ort": float(yearly.model.mean()), "spy_ort": float(yearly.spy.mean()),
                           "esit_ort": float(yearly.esit.mean()), "spyi_gecen_yil": int((yearly.model > yearly.spy).sum()),
                           "yil": len(yearly), "donem_fazla_ort": float((df.net - df.spy).mean()),
                           "isabet": float((df.net > df.spy).mean()), "yillar": yearly.round(3).to_dict(orient="index")}
        print(f"tutma {hold} hafta: model {yearly.model.mean():+.1%}/yıl, S&P {yearly.spy.mean():+.1%}, eşit ağırlık {yearly.esit.mean():+.1%}, "
              f"S&P'yi geçtiği yıl {res[f'{hold}h']['spyi_gecen_yil']}/{len(yearly)}, dönem başına S&P'ye göre {res[f'{hold}h']['donem_fazla_ort']:+.2%}, "
              f"isabet %{res[f'{hold}h']['isabet'] * 100:.0f}")
        print(yearly.round(3).T.to_string())
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    return res


if __name__ == "__main__":
    main()

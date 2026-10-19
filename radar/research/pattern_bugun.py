"""Pattern'e bugün uyan hisseler: 52 haftalık dibin ≥ 2,15 katı VE en likit %30 VE gelir büyümesi alt %30'da değil.

Tanımlar çerçeve ve pattern_avi ile aynı: evren = finans dışı, işlem fiyatı ≥ 1 $, günlük işlem tutarı (13 haftalık medyan)
≥ 1 M$; likidite ve gelir büyümesi o tarihteki evren içi yüzdelik sıra; dipten_52h düzeltilmiş haftalık fiyattan.
Tarih: panelin son Cuması (fiyat verisinin son günü).

python -m radar.research.pattern_bugun → reports/research/pattern_bugun.md, pattern_bugun.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals, panel, sectors
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import REVENUE, by_filing, load_fin

R = config.ROOT / "reports" / "research"


def main(t: pd.Timestamp | None = None, write: bool = True) -> pd.DataFrame:
    p = panel.build()
    P, raw, dv, sec = p["price"], p["raw"], p["dollar_volume"], p["securities"]
    t = P.index[-1] if t is None else t
    inv = sectors.operating_universes(p)["tümü"].loc[t] & (raw.loc[t] >= 1) & (dv.loc[t] >= 1e6)
    u = inv[inv].index
    lo = P.rolling(52, min_periods=26).min().loc[t]
    hi = P.rolling(52, min_periods=26).max().loc[t]
    dip = (P.loc[t] / lo - 1)[u]
    liq = dv.loc[t][u].rank(pct=True)
    fin = fundamentals.plain(load_fin())
    rev = by_filing(fin, REVENUE, [1, 4])
    g = pit(rev.rename(columns={"accepted": "date"}).assign(value=(rev.cur / rev.prev - 1).where(rev.prev > 0))[["cik", "date", "value"]],
            P.index[P.index <= t][-2:], P.columns, FUNDAMENTAL_MAX_AGE).loc[t].clip(-1, 5)[u]
    gr = g.rank(pct=True)
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    d = pd.DataFrame({"sembol": s.symbol.reindex(u), "sirket": s.name.reindex(u).str.replace(r"\s+-\s+.*$", "", regex=True),
                      "fiyat": raw.loc[t][u].round(2), "dipten_kat": (1 + dip).round(2), "zirveden": (P.loc[t] / hi - 1)[u].round(3),
                      "gunluk_islem_milyon": (dv.loc[t][u] / 1e6).round(1), "likidite_sira": liq.round(3),
                      "gelir_buyumesi": g.round(3), "gelir_buyumesi_sira": gr.round(3)})
    pick = d[(dip >= 1.15) & (liq >= 0.7) & (gr >= 0.3)].sort_values("dipten_kat", ascending=False)
    if not write:
        return pick
    pick.to_csv(R / "pattern_bugun.csv")
    L = [f"# Pattern'e Uyan Hisseler — {t.date()} (son fiyat verisi)", "",
         "Kural: 52 haftalık dibinin en az 2,15 katı · en likit %30 · gelir büyümesi alt %30'da değil. "
         f"Evren {len(u):,} hisse; uyan {len(pick)}. Pattern'e göre hepsi eşit ağırlıkla 3 ay tutulur.", "",
         "Bu bir yatırım tavsiyesi değildir; kural canlı olarak henüz sınanmadı.", "",
         "| # | Hisse | Şirket | Fiyat ($) | Dipten kat | Zirveden | Günlük işlem (M$) | Gelir büyümesi (yıllık) |",
         "|---|---|---|---|---|---|---|---|"]
    for i, (c, r) in enumerate(pick.iterrows(), 1):
        L.append(f"| {i} | {r.sembol} | {str(r.sirket)[:40]} | {r.fiyat:,.2f} | {r.dipten_kat:.2f}× | {r.zirveden * 100:+.0f}% | "
                 f"{r.gunluk_islem_milyon:,.0f} | {r.gelir_buyumesi * 100:+.0f}% |")
    (R / "pattern_bugun.md").write_text("\n".join(L))
    print(t.date(), len(u), len(pick))
    print(pick[["sembol", "sirket", "fiyat", "dipten_kat", "zirveden", "gunluk_islem_milyon", "gelir_buyumesi"]].to_string())
    return pick


if __name__ == "__main__":
    main()

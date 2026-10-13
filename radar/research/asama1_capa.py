"""Hisse sayısının düzeltme başlangıcı: geçerlilik (dönem sonu) mu, kabul tarihi mi? (1. aşama, karar bekliyor)

Bölünme, sayının dönem sonu ile raporun kabulü arasına düşen raporlarda iki kural farklı sonuç verir. Bu raporlarda sayının
geriye dönük düzeltilip düzeltilmediği, bir önceki raporun sayısıyla karşılaştırılarak ölçülür:
  oran_yakin = |log(sayı / önceki sayı × bölünme oranı)| < log 1,25  → düzeltilmiş (bölünme sonrası)
  bir_yakin  = |log(sayı / önceki sayı)| < log 1,25                   → düzeltilmemiş (bölünme öncesi)
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals, panel

R = config.ROOT / "reports" / "research"


def main() -> dict:
    sh = fundamentals.shares_outstanding(fundamentals.load(["adsh", "cik", "tag", "value", "accepted", "qtrs", "ddate"]))
    sh = sh.assign(cik=sh.cik.astype(str), acc=pd.to_datetime(sh.accepted).dt.normalize()).sort_values(["cik", "accepted"])
    sh["prev"] = sh.groupby("cik").value.shift(1)
    ev = panel.split_cum(panel.split_events())
    ev = ev[ev.source != "ftd_tahmini"]
    rows = []
    for c, g in ev.groupby("cik"):
        s = sh[sh.cik == c]
        for e in g.itertuples():
            hit = s[(s["asof"] < e.date) & (s.acc >= e.date)]
            for h in hit.itertuples():
                if not (h.prev and h.prev > 0):
                    continue
                q = h.value / h.prev
                rows.append({"cik": c, "bolunme": str(e.date.date()), "oran": e.ratio, "kabul": str(h.acc.date()),
                             "gecerlilik": str(pd.Timestamp(h.asof).date()), "sayi_onceki_orani": q,
                             "sinif": "düzeltilmiş (bölünme sonrası)" if abs(np.log(q / e.ratio)) < np.log(1.25)
                             else "düzeltilmemiş (bölünme öncesi)" if abs(np.log(q)) < np.log(1.25) else "belirsiz"})
    t = pd.DataFrame(rows)
    t.to_csv(R / "asama1_capa.csv", index=False)
    out = {"etkilenen_rapor": int(len(t)), "sirket": int(t.cik.nunique()) if len(t) else 0,
           "sinif": t.sinif.value_counts().to_dict() if len(t) else {},
           "yorum": "Düzeltilmiş çoğunluktaysa doğru başlangıç kabul tarihidir (geçerlilik tarihi çift düzeltme yapar); "
                    "düzeltilmemiş çoğunluktaysa geçerlilik tarihi doğrudur."}
    res = json.loads((R / "asama1_v12.json").read_text())
    res["hisse_capa"] = out
    (R / "asama1_v12.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    main()

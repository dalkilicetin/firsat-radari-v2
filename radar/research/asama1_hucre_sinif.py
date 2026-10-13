"""Olay kaydı olmadan fiyat oranı sıçrayan hisseler (v1.1 yönteminin değiştirdiği, açıklanamayan hücreler): sınıflandırma.
Sıçrama oranı tam bir bölünme oranına (±%2) yakınsa 'olay kaydı eksik bölünme', değilse 'özel temettü / dağıtım'
(Yahoo düzeltilmiş fiyatı bunu temettü olarak işler; hisse sayısı değişmez)."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel

R = config.ROOT / "reports" / "research"
FACTORS = np.array([1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 100])


def main() -> dict:
    p = panel.build()
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    t = pd.read_csv(R / "asama1_v12_hucre.csv", dtype={"cik": str})
    t = t[t.neden.str.startswith("olay kaydı yok")]
    rows = []
    for r in t.itertuples():
        S = (p["raw"][r.cik] / p["price"][r.cik]).dropna()
        j = np.log(S / S.shift(1)).abs()
        d = j.idxmax()
        k = float(S[d] / S.shift(1)[d])
        f = max(k, 1 / k)
        near = np.abs(np.log(f / FACTORS)).min() < 0.02
        rows.append({"cik": r.cik, "sembol": sec.symbol.get(r.cik), "durum": sec.status.get(r.cik), "tarih": str(d.date()),
                     "fiyat_orani_sicramasi": round(k, 4), "hucre": int(r.hucre),
                     "sinif": "olay kaydı eksik bölünme" if near else "özel temettü / dağıtım"})
    d = pd.DataFrame(rows)
    d.to_csv(R / "asama1_v12_hucre_aciklama.csv", index=False)
    out = {"sirket": d.sinif.value_counts().to_dict(), "hucre": d.groupby("sinif").hucre.sum().to_dict(),
           "eksik_bolunmeler": d[d.sinif == "olay kaydı eksik bölünme"].to_dict(orient="records")}
    res = json.loads((R / "asama1_v12.json").read_text())
    res["hucre_aciklama"] = out
    (R / "asama1_v12.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return out


if __name__ == "__main__":
    main()

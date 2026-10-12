"""1. aşama yaması: doğrulamada bulunan hata düzeltildikten sonra etkilenen belirtileri çerçevede yeniden hesaplar.
python -m radar.research.asama1_yama hisse_sayisi_degisimi,piotroski_f
Yalnızca verilen sütunlar değişir; diğer belirtiler ve satırlar aynı kalır. Önceki ve yeni değerlerin farkı raporlanır."""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel, ratios

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
OUT = config.ROOT / "reports" / "research" / "asama1_yama.json"


def main(cols: list[str]) -> None:
    df = pd.read_parquet(FRAME)
    p = panel.build()
    rs = ratios.signals(p)
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    key = pd.MultiIndex.from_arrays([df.tarih, df.index.astype(str)])
    rep = {}
    for c in cols:
        w = rs[c].reindex(dates)
        w.columns = w.columns.astype(str)
        long = w.stack(future_stack=True)
        long.index.names = ["tarih", "cik"]
        new = long.groupby(level=0).rank(pct=True).reindex(key).to_numpy(dtype="float32")
        old = df[c].to_numpy()
        both = np.isfinite(old) & np.isfinite(new)
        rep[c] = {"satir": int(len(df)), "degisen_satir": int((np.abs(old - new) > 1e-6)[both].sum() + (np.isfinite(old) != np.isfinite(new)).sum()),
                  "ortalama_mutlak_yuzdelik_kayma": float(np.abs(old - new)[both].mean()),
                  "spearman_eski_yeni": float(pd.Series(old[both]).corr(pd.Series(new[both]), method="spearman"))}
        df[c] = new
        print(c, json.dumps(rep[c]), flush=True)
    df.to_parquet(FRAME)
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1].split(","))

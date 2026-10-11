"""Teşhis: sürüm 2 modeli 2023–2025'te neden başarısız oldu ve hangi işaretler yıllar boyunca istikrarlı?

python -m radar.research.diagnose → reports/research/teshis.json (+ ekrana özet)

1. Seçim profili: modelin her yıl seçtiği 20 hissenin işaretlerdeki ortalama sırası (yatırılabilir evren içinde
   yüzdelik; 50 = ortalama), geliştirme (2011–2022) ve test (2023–2025) yılları ayrı.
2. İşaret istikrarı: her işaretin her yıl, yıl başı değeri ile sonraki 52 hafta getirisi arasındaki sıra korelasyonu
   (IC; yatırılabilir faaliyet şirketleri). Ortalama, pozitif yıl sayısı, geliştirme ve test ortalamaları.
3. Piyasa yapısı: her yıl S&P 500 (büyük şirket ağırlıklı) − eşit ağırlıklı evren farkı; küçük şirket − büyük şirket.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, quick

OUT = config.ROOT / "reports" / "research" / "teshis.json"
PROFILE = ["kucuk_boyut", "dusuk_oynaklik", "beta_qqq", "momentum_12_1", "getiri_6a", "zirveye_yakinlik_52h",
           "kazanc_getirisi", "serbest_nakit_getirisi", "gelir_buyumesi", "arge_yogunlugu", "kazanc_aciklamasi_tepkisi",
           "sektor_momentum_12_1", "geri_alim_getirisi", "hacim_artisi"]


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 100:
        return np.nan
    return float(pd.Series(a[ok]).rank().corr(pd.Series(b[ok]).rank()))


def main() -> None:
    d = quick.QuickData()
    etf = context.etf_prices(d.dates)
    picks = pd.read_csv(config.ROOT / "reports" / "research" / "bir_yil_secimler_v2.csv")
    sym_idx = {}
    for i, s in enumerate(d.symbols):
        sym_idx.setdefault(s, []).append(i)
    prof_rows, ic_rows, mkt_rows = [], [], []
    for y in range(2011, 2026):
        t = quick.year_start(d.dates, y)
        u = np.asarray(d.eval_u[t])
        r = np.where(u, np.asarray(d.fwd[t], dtype=np.float64), np.nan)
        # 1. seçim profili (yatırılabilir evrende yüzdelik)
        chosen = [j for s in picks[picks.yil == y].sembol for j in sym_idx.get(s, []) if u[j]]
        row = {"yil": y, "grup": "test" if y >= 2023 else "geliştirme"}
        for f in PROFILE:
            if f not in d.X:
                continue
            x = np.where(u, np.asarray(d.X[f][t], dtype=np.float64), np.nan)
            x[x == 0] = np.nan  # eksik (nötr) değerler profili bozmasın
            pct = pd.Series(x).rank(pct=True).to_numpy() * 100
            row[f] = float(np.nanmean(pct[chosen])) if chosen else np.nan
        prof_rows.append(row)
        # 2. işaret istikrarı
        for f in d.features:
            x = np.where(u, np.asarray(d.X[f][t], dtype=np.float64), np.nan)
            x[x == 0] = np.nan
            ic_rows.append({"isaret": f, "yil": y, "ic": spearman(x, r)})
        # 3. piyasa yapısı
        spy = float(etf["SPY"].iloc[t + 52] / etf["SPY"].iloc[t] - 1)
        iwm = float(etf["IWM"].iloc[t + 52] / etf["IWM"].iloc[t] - 1)
        mkt_rows.append({"yil": y, "spy": spy, "iwm": iwm, "esit_agirlik": float(np.nanmean(r)), "medyan": float(np.nanmedian(r))})
    prof = pd.DataFrame(prof_rows)
    ic = pd.DataFrame(ic_rows).pivot(index="isaret", columns="yil", values="ic")
    summary = pd.DataFrame({
        "ort_ic": ic.mean(axis=1), "gelistirme_ic": ic.loc[:, 2011:2022].mean(axis=1), "test_ic": ic.loc[:, 2023:2025].mean(axis=1),
        "pozitif_yil": (ic > 0).sum(axis=1), "negatif_yil": (ic < 0).sum(axis=1),
        "istikrar": ic.mean(axis=1) / ic.std(axis=1)}).sort_values("istikrar", key=abs, ascending=False)
    mkt = pd.DataFrame(mkt_rows)
    OUT.write_text(json.dumps({"profil": prof.round(1).to_dict(orient="records"),
                               "ic_yillik": ic.round(4).reset_index().to_dict(orient="records"),
                               "ic_ozet": summary.round(4).reset_index().to_dict(orient="records"),
                               "piyasa": mkt.round(4).to_dict(orient="records")}, ensure_ascii=False, indent=1))
    pd.set_option("display.width", 220)
    print("SEÇİM PROFİLİ (yüzdelik, 50 = ortalama)\n", prof.groupby("grup")[[c for c in PROFILE if c in prof]].mean().round(0).T.to_string())
    print("\nİŞARET İSTİKRARI\n", summary.round(3).to_string())
    print("\nPİYASA\n", mkt.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

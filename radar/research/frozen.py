"""Dondurulmuş model — sürüm 3 (2026-10-11): istikrarlı işaretler + ridge.

Kurallar (değiştirilmez; değişiklik yeni sürüm demektir):
- Evren: Nasdaq + NYSE + NYSE American yatırılabilir faaliyet şirketleri (≥ 5 $, ≥ 1 mn $/gün; banka, sigorta, GYO,
  fon/BDC, devlet kredi kuruluşu ve SPAC hariç).
- İşaret seçimi: her işaretin geçmiş yıllardaki IC'si (yıl başı değer ↔ sonraki 52 hafta getirisi). Yıllarının en az
  %70'inde aynı işaretli ve ortalama/standart sapma ≥ 0,5 olanlar; yön = ortalama IC işareti (nested.select).
- Puan: yalnızca seçilen işaretlerle ridge (sıra hedefi, 1 yıl), eğitim satırları hedefi gerçekleşmiş haftalar.
- Seçim: puanı en yüksek 20 hisse, eşit ağırlık, 1 yıl tutma.
İç içe testte (2014–2025, her yıl yalnızca geçmişle): ort. +%15,3 / yıl, eşit ağırlıklı piyasayı 10/12, S&P 500'ü 6/12 yıl geçti.

python -m radar.research.frozen → reports/canli/<tarih>_v3.csv ve reports/canli/model_v3.json (canlı takip kaydı)
"""

from __future__ import annotations

import json
import subprocess

import numpy as np
import pandas as pd

from radar import config
from radar.research import nested, panel, quick
from radar.research.asof import Recipe

VERSION = "v3"
OUT = config.ROOT / "reports" / "canli"


def signs_for(d: quick.QuickData, ic: pd.DataFrame, year: int) -> dict[str, float]:
    return nested.select(ic, year)


def picks_at(d: quick.QuickData, t: int, signs: dict[str, float], n: int = 20) -> list[int]:
    score = quick.score_at(Recipe("v3 ridge", "sira", "ridge", features=list(signs)), d, t)
    ok = np.asarray(d.eval_u[t]) & np.isfinite(score)
    idx = np.flatnonzero(ok)
    return list(idx[np.argsort(-score[idx])][:n])


def main() -> dict:
    d = quick.QuickData()
    last_year = d.dates[-1].year
    ic = nested.ic_table(d, range(nested.FIRST_IC_YEAR, last_year))  # yalnızca 52 haftası tamamlanmış yıllar
    signs = signs_for(d, ic, last_year)
    t_now = len(d.dates) - 1
    t_y = quick.year_start(d.dates, last_year)
    p = panel.build()
    price = p["price"].to_numpy()
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik").set_index("cik")
    names = sec.name.reindex(p["price"].columns).fillna("").str.replace(r" - .*$", "", regex=True).to_numpy()
    now = picks_at(d, t_now, signs)
    ytd = picks_at(d, t_y, signs)
    ytd_ret = price[t_now, ytd] / price[t_y, ytd] - 1
    u = np.asarray(d.eval_u[t_y])
    uni_ytd = float(np.nanmean(price[t_now, u] / price[t_y, u] - 1))
    spy = d.spy()
    spy_ytd = float(spy.iloc[t_now] / spy.iloc[t_y] - 1)
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=config.ROOT).stdout.strip()
    OUT.mkdir(parents=True, exist_ok=True)
    day = d.dates[t_now].date().isoformat()
    pd.DataFrame({"sira": range(1, len(now) + 1), "sembol": d.symbols[now], "sirket": names[now],
                  "fiyat": price[t_now, now].round(2)}).to_csv(OUT / f"{day}_{VERSION}.csv", index=False)
    spec = {"surum": VERSION, "dondurulma": day, "kod": commit, "kurallar": {"min_pay": nested.MIN_SHARE,
            "min_istikrar": nested.MIN_STAB, "ic_yillari": [nested.FIRST_IC_YEAR, last_year - 1], "hisse": 20, "vade": "1 yıl"},
            "isaretler": signs, "secim_bugun": [str(s) for s in d.symbols[now]],
            "yil_basi": {"tarih": str(d.dates[t_y].date()), "secim": [str(s) for s in d.symbols[ytd]],
                         "getiri": [None if np.isnan(x) else round(float(x), 4) for x in ytd_ret], "model": float(np.nanmean(ytd_ret)),
                         "evren": uni_ytd, "spy": spy_ytd}}
    (OUT / f"model_{VERSION}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in spec.items() if k != "isaretler"}, ensure_ascii=False, indent=1))
    return spec


if __name__ == "__main__":
    main()

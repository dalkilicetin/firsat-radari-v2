"""Son dönem testi (TEK SEFERLİK): python -m radar.research.run_holdout → reports/research/son_donem.md

Kurallar:
- Model ve sinyaller 4. aşama raporundaki (model.md) haliyle dondurulmuştur; bu betik ayar yapmaz.
- Son dönem: HOLDOUT_START'tan bugüne. Kayan pencere modeli bu dönemde de yalnızca o ana kadar gerçekleşmiş
  getirilerle eğitilmeye devam eder (gerçek kullanımda olacağı gibi).
- Sonuç ne olursa olsun raporlanır; sonuca bakıp modeli değiştirmek son dönemi "kullanmak" olur.
"""

from __future__ import annotations

import pickle
import subprocess
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import evaluate as ev
from radar.research import model, panel, risk
from radar.research.report import universes
from radar.research.run_model import FITS

REPORT = config.ROOT / "reports" / "research" / "son_donem.md"


def main() -> None:
    t0 = time.time()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=config.ROOT).stdout.strip()
    p = panel.build()
    price, sec, dates, cols = p["price"], p["securities"], p["price"].index, p["price"].columns
    with FITS.open("rb") as f:
        fits_all = pickle.load(f)
    unis = universes(p)
    ev.PERIOD = "son_donem"
    ev._RET_CACHE.clear()
    last = dates[-1]

    rows = []
    for train_name, fits in fits_all.items():
        for (g, h), fit in fits.items():
            if g != "toplam" and train_name != "tümü":
                continue
            score = model.to_score(fit.pred, dates, cols)
            for uni_name, uni in unis.items():
                if train_name == "yatırılabilir" and uni_name == "tümü":
                    continue
                r = ev.evaluate(score.where(uni), price, sec, g, {h: panel.HORIZONS[h]}, universe=uni).rows[0]
                rows.append({"eğitim": train_name, "model": g, "vade": h, "evren": uni_name.split(" ")[0],
                             "hafta": r.get("hafta", 0), "IC": r.get("IC"), "IC_t": r.get("IC_t"),
                             "ilk10_fazla": r.get("ilk10_fazla"), "son10_fazla": r.get("son10_fazla"), "fark": r.get("fark")})
    res = pd.DataFrame(rows)

    # Geliştirme dönemiyle karşılaştırma için aynı tablo (model.md'deki değerler).
    ev.PERIOD = "gelistirme"
    ev._RET_CACHE.clear()
    dev = []
    for (g, h), fit in fits_all["tümü"].items():
        if g != "toplam":
            continue
        r = ev.evaluate(model.to_score(fit.pred, dates, cols), price, sec, g, {h: panel.HORIZONS[h]},
                        universe=unis["tümü"]).rows[0]
        dev.append({"vade": h, "geliştirme IC": r.get("IC")})
    ev.PERIOD = "son_donem"
    ev._RET_CACHE.clear()

    # Risk puanı: son dönemde 26 haftalık en büyük düşüş seviyeye göre artıyor mu?
    f = risk.features(p)
    member = unis["tümü"]
    _, level = risk.score(f, member)
    fwd = [panel.forward_returns(price, sec, w).reindex(dates) for w in range(1, 27, 2)]
    worst = pd.concat(fwd).groupby(level=0).min()
    ok = (dates >= ev.HOLDOUT_START) & (dates + pd.Timedelta(weeks=26) <= last)
    risk_rows = []
    for lv in range(1, 6):
        dd = worst.loc[ok].where(level.loc[ok] == lv).stack().dropna()
        risk_rows.append({"Risk": lv, "Gözlem": len(dd), "Medyan en büyük düşüş (26 hafta)": f"%{dd.median() * 100:.0f}",
                          "%30+ düşüş olasılığı": f"%{(dd < -0.3).mean() * 100:.0f}"})

    tot = res[(res.model == "toplam")].copy()
    piv = lambda d: d.pivot_table(index=["eğitim", "evren"], columns="vade", values="IC")[[h for h in panel.HORIZONS if h in d.vade.unique()]]
    lines = [
        "# Son dönem testi (tek seferlik)", "",
        f"Kod sürümü: `{commit}` · Dönem: {ev.HOLDOUT_START.date()} → {last.date()} · Çalıştırma: {pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} UTC", "",
        "Model ve sinyaller geliştirme dönemi sonunda dondurulmuş haliyle çalıştırıldı; bu sonuçlara bakılarak değişiklik yapılmadı. "
        "Uzun vadelerde getirisi gerçekleşmiş hafta sayısı azdır (1y vadesi için yalnızca son dönemin ilk birkaç ayı).", "",
        "## Toplam model: son dönem IC", "", piv(tot).round(4).to_markdown(), "",
        "## Geliştirme dönemiyle karşılaştırma (tüm evren)", "",
        pd.DataFrame(dev).merge(tot[(tot["eğitim"] == "tümü") & (tot.evren == "tümü")][["vade", "IC", "IC_t", "hafta"]]
                                .rename(columns={"IC": "son dönem IC", "IC_t": "son dönem t", "hafta": "son dönem hafta"}), on="vade").to_markdown(index=False), "",
        "## Toplam modelin ayrıntısı", "", tot.drop(columns=["model"]).to_markdown(index=False), "",
        "## Yol modelleri (tüm evren, son dönem IC)", "",
        res[(res["eğitim"] == "tümü") & (res.evren == "tümü")].pivot(index="model", columns="vade", values="IC").round(4).to_markdown(), "",
        "## Risk puanı (son dönem, 26 haftalık pencere)", "", pd.DataFrame(risk_rows).to_markdown(index=False), "",
    ]
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"{round(time.time() - t0)} sn")


if __name__ == "__main__":
    main()

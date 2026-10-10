""""O gün çalıştırsaydık" denemeleri: python -m radar.research.run_asof <tur> [vade]

Sıra (kullanıcı kararı): önce 1 yıl (1y) iyileştirilir, sonra 1 ay (1a), en son 1 hafta (1h).

Her deneme reports/research/asof_denemeler.jsonl dosyasına yazılır (yapılan deneme sayısı saklanır).
Kilitli dönem (tutma süresi 2023'e taşan başlangıçlar) bu betikle ölçülmez.
"""

from __future__ import annotations

import sys
import time

import pandas as pd

from radar import config
from radar.research import asof, library, panel, sectors
from radar.research.asof import Recipe

OUT = config.ROOT / "reports" / "research" / "asof"
ROUNDS = {
    "tur1": [
        Recipe("R1 ridge sıra (tüm sinyaller)", "sira"),
        Recipe("R2 ridge sıra, oynaklık hariç (mevcut güvenlik modeli)", "sira", exclude={"dusuk_oynaklik"}),
        Recipe("R3 ridge fazla getiri", "fazla"),
        Recipe("R4 ridge dönemin en iyi %10'u", "ust10"),
        Recipe("R5 lgbm sıra", "sira", "lgbm", refit=13),
        Recipe("R6 lgbm dönemin en iyi %10'u", "ust10", "lgbm", refit=13),
    ],
    # Tur 2: Nasdaq + NYSE, 2011→ başlangıçlar, sektör/beta sinyalleri; 10-K metinleri henüz yüklenmedi.
    "tur2": [
        Recipe("T2a ridge sıra, oynaklık hariç (güvenlik modeli)", "sira", exclude={"dusuk_oynaklik"}),
        Recipe("T2b lgbm sıra (tur 1 kazananı)", "sira", "lgbm", refit=13),
        Recipe("T2c lgbm sıra + piyasa dönemi", "sira", "lgbm", refit=13, regime=True),
        Recipe("T2d lgbm sıra, daha büyük ağaçlar", "sira", "lgbm", refit=13,
               params={"n_estimators": 500, "num_leaves": 31, "learning_rate": 0.03}),
        Recipe("T2e lgbm fazla getiri + dönem", "fazla", "lgbm", refit=13, regime=True),
    ],
}


def prepare():
    p = panel.build()
    sigs = library.load_all(p)
    unis = sectors.operating_universes(p)
    inv_key = [k for k in unis if k != "tümü"][0]
    return asof.Data(p, sigs, unis["tümü"], unis[inv_key])


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "tur1"
    horizon = sys.argv[2] if len(sys.argv) > 2 else "1y"
    t0 = time.time()
    data = prepare()
    print(f"veri hazır ({round(time.time() - t0)} sn)", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for rec in ROUNDS[name]:
        df = asof.evaluate(rec, data, horizons=[horizon])
        summ = asof.summary(df)
        asof.log_trial(rec, summ, {"tur": name, "vade": horizon})
        df.to_parquet(OUT / f"{rec.name.split(' ')[0]}_{name}_{horizon}.parquet")
        print(f"\n== {rec.name} ({round(time.time() - t0)} sn)\n{summ.round(3).to_string()}", flush=True)


if __name__ == "__main__":
    main()

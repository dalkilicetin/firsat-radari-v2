"""Hızlı iterasyon turları: python -m radar.research.run_quick <tur> [dogrula]

<tur> ROUNDS içindeki adlardan biri. "dogrula" verilirse tarifler iterasyonda kullanılmamış geliştirme yıllarında
(quick.VALID_YEARS) çalıştırılır. Kilitli yıllar bu betikle açılmaz.
"""

from __future__ import annotations

import sys
import time

import pandas as pd

from radar.research import quick
from radar.research.asof import Recipe

LGBM_BIG = {"n_estimators": 500, "num_leaves": 31, "learning_rate": 0.03}
ROUNDS: dict[str, list[Recipe]] = {
    "h1": [
        Recipe("H1a ridge sıra, oynaklık hariç (güvenlik)", "sira", exclude={"dusuk_oynaklik"}),
        Recipe("H1b lgbm sıra", "sira", "lgbm"),
        Recipe("H1c lgbm sıra + dönem", "sira", "lgbm", regime=True),
        Recipe("H1d lgbm sıra + dönem, büyük ağaçlar", "sira", "lgbm", regime=True, params=LGBM_BIG),
        Recipe("H1e lgbm fazla getiri + dönem", "fazla", "lgbm", regime=True),
        Recipe("H1f lgbm sıra + dönem, yatırılabilirde eğitim", "sira", "lgbm", regime=True, train_on="yatirilabilir"),
        Recipe("H1g lgbm sıra + dönem, ≥ 5 mn $/gün", "sira", "lgbm", regime=True, min_volume=5e6),
    ],
}


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "h1"
    validate = len(sys.argv) > 2 and sys.argv[2] == "dogrula"
    years = quick.VALID_YEARS if validate else quick.ITER_YEARS
    t0 = time.time()
    d = quick.QuickData()
    print(f"veri hazır ({round(time.time() - t0)} sn)", flush=True)
    rows = []
    for rec in ROUNDS[name]:
        df = quick.run(rec, d, years)
        e = quick.log(rec, df, "dogrulama" if validate else "iterasyon")
        rows.append({"deneme": rec.name} | e["ozet"] |
                    {f"{y}": f"{r['portfoy']:+.0%} / piyasa {r['piyasa']:+.0%} ({r['yukselen']}/20 yükseldi)"
                     for y, r in e["yil_yil"].items()})
        print(f"{rec.name} ({round(time.time() - t0)} sn)", flush=True)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(rows).set_index("deneme").to_string())


if __name__ == "__main__":
    main()

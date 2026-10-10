"""Yıl başı testi denemeleri: python -m radar.research.run_yearly [tur adı]

Her deneme reports/research/yillik_denemeler.jsonl dosyasına yazılır (kaç deneme yapıldığı saklanır).
Kilitli yıllar (yearly.LOCKED) bu betikle açılmaz.
"""

from __future__ import annotations

import sys
import time

import pandas as pd

from radar import config
from radar.research import library, panel, sectors
from radar.research import yearly as yr
from radar.research.yearly import Recipe

ROUNDS = {
    "tur1": [
        Recipe("R1 ridge sıra", "sira", "ridge", note="4. aşama modelinin yıllık hali (oynaklık dahil)"),
        Recipe("R2 ridge sıra, oynaklık hariç", "sira", "ridge", exclude={"dusuk_oynaklik"}),
        Recipe("R3 ridge fazla getiri", "fazla", "ridge"),
        Recipe("R4 ridge yılın en iyi %10'u", "ust10", "ridge"),
        Recipe("R5 lgbm sıra", "sira", "lgbm"),
        Recipe("R6 lgbm yılın en iyi %10'u", "ust10", "lgbm"),
    ],
}


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "tur1"
    t0 = time.time()
    p = panel.build()
    sigs = library.load_all(p)
    unis = sectors.operating_universes(p)
    inv_key = [k for k in unis if k != "tümü"][0]
    data = yr.Data(p, sigs, unis["tümü"], unis[inv_key])
    print(f"veri hazır ({round(time.time() - t0)} sn)", flush=True)
    rows = []
    for rec in ROUNDS[name]:
        df = yr.run(rec, data, range(2010, 2027))
        e = yr.log_trial(rec, df, {"tur": name})
        rows.append(e)
        out = config.ROOT / "reports" / "research" / "yillik" / f"{rec.name.split(' ')[0]}_{name}.csv"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out)
        print(f"{rec.name}: {e} ({round(time.time() - t0)} sn)", flush=True)
    cols = ["deneme", "yillar", "ilk20_fazla_ort", "ilk20_fazla_pozitif_yil", "ilk20_yukselen", "ilk20_medyani_gecen",
            "ilk20_yilin_en_iyi10", "ilk10y_fazla_ort", "ilk10y_fazla_pozitif_yil", "evren_yukselen", "en_kotu_yil_ilk20_fazla"]
    print(pd.DataFrame(rows)[[c for c in cols if c in rows[0]]].to_string())


if __name__ == "__main__":
    main()

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
# Tur h2: yeni sinyaller (zirveye yakınlık, 6 ay getiri, hacim artışı, kazanç açıklaması tepkisi) + iki aşamalı seçim.
_R = Recipe("H2a ridge sıra, oynaklık hariç (güvenlik)", "sira", exclude={"dusuk_oynaklik"})
_RS = Recipe("H2b güvenlik + eleme", "sira", exclude={"dusuk_oynaklik"}, screen=True)
_L = Recipe("H2c lgbm sıra", "sira", "lgbm")
_LS = Recipe("H2d lgbm sıra + eleme", "sira", "lgbm", screen=True)
ROUNDS["h2"] = [
    _R, _RS, _L, _LS,
    Recipe("H2e lgbm sıra + eleme, yatırılabilirde eğitim", "sira", "lgbm", screen=True, train_on="yatirilabilir"),
    Recipe("H2f topluluk (güvenlik + lgbm) + eleme", learner="ensemble", members=[_R, _L], screen=True),
    Recipe("H2g lgbm sıra + dönem + eleme", "sira", "lgbm", regime=True, screen=True),
]

# Doğrulama adayları (h2'nin en iyileri): iterasyonda kullanılmamış yıllarda bir kez çalıştırılır.
ROUNDS["aday1"] = [_L, _LS, _R]

# Tur h3: LightGBM'in yıldan yıla dalgalanmasını azaltma.
_NOISY = {"wiki_ilgi_ivmesi", "wiki_ani_ilgi", "haber_ivmesi", "haber_ani_artis", "haber_ton_degisimi",
          "haber_ton_seviyesi", "tema_ruzgari", "tema_ruzgari_v1_uzun", "tema_ruzgari_v2_nadir", "tema_ruzgari_v3_uzun_nadir"}
_SEEDS = [Recipe(f"lgbm tohum {s}", "sira", "lgbm", params={"random_state": s}) for s in range(5)]
ROUNDS["h3"] = [
    Recipe("H3a lgbm 5 tohum ortalaması", learner="ensemble", members=_SEEDS),
    Recipe("H3b lgbm güçlü düzenleme", "sira", "lgbm",
           params={"n_estimators": 400, "num_leaves": 7, "min_child_samples": 1000, "learning_rate": 0.03}),
    Recipe("H3c lgbm son 6 yıl", "sira", "lgbm", params={"pencere": 6 * 52}),
    Recipe("H3d lgbm, haber/tema sinyalleri hariç", "sira", "lgbm", exclude=_NOISY),
    Recipe("H3e lgbm + güvenlik (eşit ağırlık)", learner="ensemble", members=[_L, _R]),
    Recipe("H3f 5 tohum + güvenlik", learner="ensemble", members=_SEEDS + [_R] * 5),
]

ROUNDS["aday2"] = [ROUNDS["h3"][0]]  # 5 tohum ortalaması: doğrulama yıllarında

# Tur h4 (kilit açıldıktan sonra, 2011–2025 tüm yıllar): yılın en çok yükselenlerini yakalama.
_UP = Recipe("lgbm en iyi %10", "ust10", "lgbm")
_DOWN = Recipe("lgbm en kötü %10", "alt10", "lgbm")
_UPS = [Recipe(f"lgbm en iyi %10 t{s}", "ust10", "lgbm", params={"random_state": s}) for s in range(3)]
ROUNDS["h4"] = [
    ROUNDS["h3"][0],
    Recipe("H4b lgbm en iyi %10 + eleme", "ust10", "lgbm", screen=True),
    Recipe("H4c asimetrik (λ=1) + eleme", learner="fark", members=[_UP, _DOWN], screen=True),
    Recipe("H4d asimetrik (λ=0,5) + eleme", learner="fark", members=[_UP, _DOWN], screen=True, params={"lam": 0.5}),
    Recipe("H4e asimetrik (λ=2) + eleme", learner="fark", members=[_UP, _DOWN], screen=True, params={"lam": 2.0}),
    Recipe("H4f asimetrik + 5 tohum sıra (topluluk)", learner="ensemble",
           members=[Recipe("asim", learner="fark", members=[_UP, _DOWN], screen=True), ROUNDS["h3"][0]]),
]


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "h1"
    validate = len(sys.argv) > 2 and sys.argv[2] == "dogrula"
    all_years = len(sys.argv) > 2 and sys.argv[2] == "tum"
    years = quick.VALID_YEARS if validate else quick.ALL_YEARS if all_years else quick.ITER_YEARS
    t0 = time.time()
    d = quick.QuickData()
    print(f"veri hazır ({round(time.time() - t0)} sn)", flush=True)
    rows = []
    for rec in ROUNDS[name]:
        df = quick.run(rec, d, years)
        e = quick.log(rec, df, "dogrulama" if validate else "tum_yillar" if all_years else "iterasyon")
        if all_years:  # 15 yıl tabloya sığmaz: yalnızca özet (yıl yıl sonuçlar jsonl kaydında)
            rows.append({"deneme": rec.name} | e["ozet"])
            print(f"{rec.name} ({round(time.time() - t0)} sn)", flush=True)
            continue
        rows.append({"deneme": rec.name} | e["ozet"] |
                    {f"{y}": f"{r['portfoy']:+.0%} / piyasa {r['piyasa']:+.0%} ({r['yukselen']}/20 yükseldi)"
                     for y, r in e["yil_yil"].items()})
        print(f"{rec.name} ({round(time.time() - t0)} sn)", flush=True)
    pd.set_option("display.width", 250)
    print(pd.DataFrame(rows).set_index("deneme").to_string())


if __name__ == "__main__":
    main()

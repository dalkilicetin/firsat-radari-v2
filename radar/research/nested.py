"""İç içe (nested) test: seçim kuralının kendisi de görmediği yılda test edilir.

python -m radar.research.nested

Her test yılı Y (2014–2025) için, YALNIZCA Y'den önce gerçekleşmiş bilgiyle:
1. İşaret seçimi: her işaretin 2011..Y−1 yıllarındaki IC'leri (yıl başı değer ↔ sonraki 52 hafta getirisi;
   yatırılabilir faaliyet şirketleri). Kural (önceden sabit): yıllarının en az %70'inde aynı işaretli ve
   ortalama/standart sapma ≥ 0,5. Yön = ortalama IC'nin işareti.
2. Puanlar:
   - "bileşik": seçilen işaretlerin yönlü sıralarının ortalaması (öğrenme yok).
   - "lgbm_secili": yalnızca seçilen işaretlerle LightGBM (sıra hedefi; quick ile aynı eğitim kuralı).
   - "ridge_secili": aynı, ridge.
3. Aile seçimi: her aile için Y'den önceki test yıllarındaki (en az 3 yıl) ortalama fazla getiri; en iyisi Y'de kullanılır.
Y yılı yıl başında puanlanır, ilk 20 hisse alınır, 52 hafta sonra ölçülür (quick.outcome: maliyet, çıkış değeri).
Çıktı: reports/research/nested.json ve ekranda yıl yıl tablo.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import quick
from radar.research.asof import Recipe

OUT = config.ROOT / "reports" / "research" / "nested.json"
FIRST_IC_YEAR, TEST_YEARS = 2011, range(2014, 2026)
MIN_SHARE, MIN_STAB = 0.70, 0.5


def ic_table(d: quick.QuickData, years) -> pd.DataFrame:
    rows = []
    for y in years:
        t = quick.year_start(d.dates, y)
        u = np.asarray(d.eval_u[t])
        r = np.where(u, np.asarray(d.fwd[t], dtype=np.float64), np.nan)
        rr = pd.Series(r).rank()
        for f in d.features:
            x = np.where(u, np.asarray(d.X[f][t], dtype=np.float64), np.nan)
            x[x == 0] = np.nan
            ok = np.isfinite(x) & np.isfinite(r)
            ic = float(pd.Series(x[ok]).rank().corr(pd.Series(r[ok]).rank())) if ok.sum() >= 100 else np.nan
            rows.append({"isaret": f, "yil": y, "ic": ic})
    return pd.DataFrame(rows).pivot(index="isaret", columns="yil", values="ic")


def select(ic: pd.DataFrame, before: int) -> dict[str, float]:
    """Y'den önceki yıllara göre istikrarlı işaretler → yön (+1/−1)."""
    h = ic.loc[:, [c for c in ic.columns if c < before]]
    m, s = h.mean(axis=1), h.std(axis=1)
    n = h.notna().sum(axis=1)
    share = pd.concat([(h > 0).sum(axis=1), (h < 0).sum(axis=1)], axis=1).max(axis=1) / n
    ok = (n >= 3) & (share >= MIN_SHARE) & ((m / s).abs() >= MIN_STAB)
    return {f: float(np.sign(m[f])) for f in ic.index[ok]}


def composite(d: quick.QuickData, t: int, signs: dict[str, float]) -> np.ndarray:
    u = np.asarray(d.train_u[t])
    acc = np.zeros(len(d.cols))
    for f, sgn in signs.items():
        acc += sgn * np.asarray(d.X[f][t], dtype=np.float64)
    out = np.full(len(d.cols), np.nan)
    out[u] = acc[u] / max(len(signs), 1)
    return out


def main() -> None:
    d = quick.QuickData()
    spy = d.spy()
    ic = ic_table(d, range(FIRST_IC_YEAR, 2026))  # Y için yalnızca < Y sütunları kullanılır
    fam_results: dict[str, dict[int, dict]] = {"bileşik": {}, "lgbm_secili": {}, "ridge_secili": {}}
    chosen_rows = []
    for Y in TEST_YEARS:
        t = quick.year_start(d.dates, Y)
        signs = select(ic, Y)
        feats = list(signs)
        scores = {"bileşik": composite(d, t, signs),
                  "lgbm_secili": quick.score_at(Recipe("lgbm seçili", "sira", "lgbm", features=feats), d, t),
                  "ridge_secili": quick.score_at(Recipe("ridge seçili", "sira", "ridge", features=feats), d, t)}
        spy_y = float(spy.iloc[t + quick.W] / spy.iloc[t] - 1)
        for fam, sc in scores.items():
            res = quick.outcome(d, sc, t)
            fam_results[fam][Y] = res | {"spy": spy_y}
        # aile seçimi: Y'den önceki test yıllarındaki ortalama fazla getiri (en az 3 yıl)
        past = {fam: [r["portfoy"] - r["evren_ort"] for y, r in fr.items() if y < Y] for fam, fr in fam_results.items()}
        pick = max(past, key=lambda k: np.mean(past[k])) if all(len(v) >= 3 for v in past.values()) else "bileşik"
        r = fam_results[pick][Y]
        chosen_rows.append({"yil": Y, "secilen_aile": pick, "isaret_sayisi": len(signs), "model": r["portfoy"], "spy": spy_y,
                            "esit": r["evren_ort"], "yukselen": r["yukselen"], "en_iyi10": r["en_iyi10_icinde"],
                            "isaretler": ", ".join(f"{'+' if v > 0 else '−'}{k}" for k, v in signs.items()),
                            "secim": r["secim"]})
        print(Y, pick, f"model {r['portfoy']:+.1%} SPY {spy_y:+.1%} eşit {r['evren_ort']:+.1%} "
              f"({r['yukselen']}/20 yükseldi, {r['en_iyi10_icinde']} en iyi %10'da) işaret {len(signs)}", flush=True)
    ch = pd.DataFrame(chosen_rows)
    fam_tab = {fam: {"ort": float(np.mean([v["portfoy"] for v in fr.values()])),
                     "kar_yili": int(sum(v["portfoy"] > 0 for v in fr.values())),
                     "esiti_gecen": int(sum(v["portfoy"] > v["evren_ort"] for v in fr.values())),
                     "spyi_gecen": int(sum(v["portfoy"] > v["spy"] for v in fr.values())),
                     "en_iyi10_ort": float(np.mean([v["en_iyi10_icinde"] for v in fr.values()]))} for fam, fr in fam_results.items()}
    summary = {"ic_secimli_surec": {"ort": float(ch.model.mean()), "spy_ort": float(ch.spy.mean()), "esit_ort": float(ch.esit.mean()),
                                    "kar_yili": int((ch.model > 0).sum()), "esiti_gecen": int((ch.model > ch.esit).sum()),
                                    "spyi_gecen": int((ch.model > ch.spy).sum()), "en_iyi10_ort": float(ch.en_iyi10.mean()),
                                    "yil": len(ch)}, "aileler": fam_tab}
    fam_years = {fam: {int(y): {"model": v["portfoy"], "esit": v["evren_ort"], "spy": v["spy"], "yukselen": v["yukselen"],
                                "en_iyi10": v["en_iyi10_icinde"], "secim": v["secim"]} for y, v in fr.items()}
                 for fam, fr in fam_results.items()}
    for fam, fy in fam_years.items():
        print(fam, " ".join(f"{y}:{v['model']:+.0%}/{v['esit']:+.0%}" for y, v in fy.items()))
    OUT.write_text(json.dumps({"ozet": summary, "aile_yillar": fam_years, "yillar": ch.drop(columns=["secim"]).to_dict(orient="records"),
                               "secimler": {int(r.yil): r.secim for r in ch.itertuples()},
                               "ic": ic.round(4).reset_index().to_dict(orient="records")}, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(summary, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

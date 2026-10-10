"""Model varyantı seçimi (yalnızca geliştirme dönemi): python -m radar.research.compare_variants

Önceden belirlenen seçim ölçütü (2026-10-10): yatırılabilir evrende, puanı en yüksek %10'un 3 aylık kırpılmış
ortalama fazla getirisi en yüksek olan varyant; medyan fazla getirisi de pozitif olmalı.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import config
from radar.research import evaluate as ev
from radar.research import library, model, panel
from radar.research.report import universes

REPORT = config.ROOT / "reports" / "research" / "model_varyantlari.md"
VARIANTS = {
    "A: sıra hedefi, oynaklık dahil": ("sira", set()),
    "B: sıra hedefi, oynaklık hariç": ("sira", {"dusuk_oynaklik"}),
    "C: getiri hedefi, oynaklık hariç": ("getiri", {"dusuk_oynaklik"}),
    "D: getiri hedefi, oynaklık dahil": ("getiri", set()),
}
SHOW = {"1a": 4, "3a": 13, "6a": 26}


def top_decile_stats(score: pd.DataFrame, ex: pd.DataFrame) -> tuple[float, float, float]:
    s = score.reindex(ex.index)
    valid = s.notna() & ex.notna()
    rank = s.where(valid).rank(axis=1, pct=True)
    top = ex.where(valid & (rank >= 0.9))
    lo, hi = ex.quantile(0.01, axis=1), ex.quantile(0.99, axis=1)
    wins = top.clip(lo, hi, axis=0)
    vals = top.stack().dropna()
    return float(wins.mean(axis=1).mean()), float(vals.median()), float((vals > 0).mean())


def main() -> None:
    p = panel.build()
    sigs = library.load_all(p)
    unis = universes(p)
    inv_key = [k for k in unis if k != "tümü"][0]
    price, sec, dates, cols = p["price"], p["securities"], p["price"].index, p["price"].columns
    rows = []
    for vname, (target, exclude) in VARIANTS.items():
        for train_name, uni in (("tümü", unis["tümü"]), ("yatırılabilir", unis[inv_key])):
            fits = model.run(p, sigs, SHOW, universe=uni, target=target, exclude=exclude, only_total=True)
            for h, w in SHOW.items():
                score = model.to_score(fits[("toplam", h)].pred, dates, cols)
                for eval_name, eval_uni in (("tümü", unis["tümü"]), ("yatırılabilir", unis[inv_key])):
                    if train_name == "yatırılabilir" and eval_name == "tümü":
                        continue
                    ex = ev.excess_returns(price, sec, w, eval_uni)
                    r = ev.evaluate(score.where(eval_uni), price, sec, vname, {h: w}, universe=eval_uni).rows[0]
                    mean10, med10, hit10 = top_decile_stats(score.where(eval_uni), ex)
                    rows.append({"varyant": vname, "eğitim": train_name, "ölçüm": eval_name, "vade": h,
                                 "IC": r["IC"], "ilk10 kırpılmış ort": round(mean10, 4), "ilk10 medyan": round(med10, 4),
                                 "ilk10 isabet": round(hit10, 3), "fark (ilk10-son10)": r["fark"]})
            print(vname, train_name, "tamam", flush=True)
    df = pd.DataFrame(rows)
    key = df[(df["ölçüm"] == "yatırılabilir") & (df.vade == "3a")].sort_values("ilk10 kırpılmış ort", ascending=False)
    eligible = key[key["ilk10 medyan"] > 0]
    choice = eligible.iloc[0] if len(eligible) else key.iloc[0]
    lines = ["# Model varyantı seçimi (geliştirme dönemi)", "",
             "Önceden belirlenen ölçüt: yatırılabilir evrende puanı en yüksek %10'un 3 aylık kırpılmış ortalama fazla "
             "getirisi en yüksek olan varyant (medyanı da pozitif olmalı). Son dönem kullanılmadı.", "",
             f"**Seçilen:** {choice['varyant']} — eğitim evreni: {choice['eğitim']}", "",
             "## Seçim tablosu (yatırılabilir evren, 3 ay)", "", key.drop(columns=["ölçüm", "vade"]).to_markdown(index=False), "",
             "## Tüm sonuçlar", "", df.to_markdown(index=False), ""]
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines[:16]))


if __name__ == "__main__":
    main()

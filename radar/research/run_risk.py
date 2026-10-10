"""Risk puanı doğrulama raporu: python -m radar.research.run_risk → reports/research/risk.md"""

from __future__ import annotations

import pandas as pd

from radar import config
from radar.research import panel, risk
from radar.research.evaluate import HOLDOUT_START

REPORT = config.ROOT / "reports" / "research" / "risk.md"


def auc(score: pd.DataFrame, label: pd.DataFrame) -> float:
    d = pd.concat([score.stack(), label.reindex_like(score).stack()], axis=1, keys=["s", "y"]).dropna()
    d["r"] = d.s.rank()
    pos = d.y.astype(bool)
    n1, n0 = pos.sum(), (~pos).sum()
    return float((d.r[pos].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def main() -> None:
    p = panel.build()
    f = risk.features(p)
    universe = p["price"].notna() & panel.membership(p["securities"], p["price"].index, p["price"].columns)
    pct, level = risk.score(f, universe)
    o = risk.outcomes(p["price"], p["securities"])
    ok = (level.index + pd.Timedelta(weeks=52)) < HOLDOUT_START

    rows = []
    for lv in range(1, 6):
        m = (level == lv).loc[ok]
        dd = o["en_buyuk_dusus"].loc[ok].where(m).stack().dropna()
        ex = o["kotu_cikis"].loc[ok].where(m).stack().dropna().astype(float)
        yr = o["yillik_getiri"].loc[ok].where(m).stack().dropna()
        rows.append({"Risk": lv, "Gözlem (hisse-hafta)": f"{len(dd):,}",
                     "Medyan en büyük düşüş (1 yıl)": f"%{dd.median() * 100:.0f}",
                     "%50+ düşüş olasılığı": f"%{(dd < -0.5).mean() * 100:.0f}",
                     "Kötü çıkış olasılığı": f"%{ex.mean() * 100:.2f}",
                     "Medyan 1 yıllık getiri": f"%{yr.median() * 100:.1f}"})
    dd = o["en_buyuk_dusus"].loc[ok]
    comp_rows = []
    for k in list(risk.WEIGHTS) + list(risk.EVENT_POINTS) + list(risk.DROPPED):
        x = f[k].astype(float).where(universe).loc[ok]
        ic = x.rank(axis=1, pct=True).corrwith((-dd).rank(axis=1, pct=True), axis=1).mean()
        cov = x.notna().sum(axis=1).median() / universe.loc[ok].sum(axis=1).median()
        state = "çıkarıldı: " + risk.DROPPED[k] if k in risk.DROPPED else (
            f"ağırlık {risk.WEIGHTS[k]:.2f}" if k in risk.WEIGHTS else f"olay puanı {risk.EVENT_POINTS[k]:.2f}")
        comp_rows.append({"Bileşen": k, "Düşüşle sıralama korelasyonu": f"{ic:+.3f}", "Kapsam": f"%{cov * 100:.0f}", "Durum": state})
    comp_ic = pct.loc[ok].corrwith((-dd).rank(axis=1, pct=True), axis=1).mean()
    vol_pct = f["oynaklik"].where(universe).rank(axis=1, pct=True)

    lines = [
        "# Risk puanı doğrulaması", "",
        f"Dönem: 2015 → {HOLDOUT_START.date()} öncesi (sonuç penceresi son döneme taşan haftalar hariç). "
        "Evren: o hafta Nasdaq'ta işlem gören tüm hisseler, sonradan çıkanlar dahil.",
        "Kötü çıkış: sonraki 1 yıl içinde iflasla ya da %50'den fazla kayıpla borsadan çıkış.", "",
        pd.DataFrame(rows).to_markdown(index=False), "",
        f"- Bileşik puanın sonraki 1 yıldaki düşüşle sıralama korelasyonu: **{comp_ic:+.3f}**",
        f"- Kötü çıkışı ayırt etme gücü (AUC): bileşik **{auc(pct.loc[ok], o['kotu_cikis'].loc[ok]):.3f}**, "
        f"yalnızca oynaklık {auc(vol_pct.loc[ok], o['kotu_cikis'].loc[ok]):.3f}", "",
        "## Bileşenler", "", pd.DataFrame(comp_rows).to_markdown(index=False), "",
        "Ağırlıklar uzman görüşüdür; 4. aşamada bu sonuçlarla kalibre edilecek.", "",
    ]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()

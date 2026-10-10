"""Fırsat modeli ve güvenlik modeli (faaliyet şirketleri): python -m radar.research.run_opportunity

Ön kayıt: reports/research/firsat_on_kayit.md. Yalnızca geliştirme dönemi ölçülür.
Çıktılar: reports/research/firsat_modeli.md, data/derived/firsat_fits.pkl
"""

from __future__ import annotations

import pickle
import sys
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import backtest as bt
from radar.research import library, model, panel, sectors

REPORT = config.ROOT / "reports" / "research" / "firsat_modeli.md"
FITS = config.DATA_DIR / "derived" / "firsat_fits.pkl"
KNOWN = ["APP", "NVDA", "SMCI", "HOOD", "RKLB", "AXON", "CELH", "TSLA", "DUOL", "CRWD", "AXTI", "ASTS"]


def frame(fit: model.Fit, p: dict) -> pd.DataFrame:
    return pd.DataFrame(fit.pred, index=p["price"].index, columns=p["price"].columns)


def pct(x: float) -> str:
    return "—" if pd.isna(x) else f"%{x * 100:.1f}"


def main() -> None:
    t0 = time.time()
    log = lambda m: print(f"{m} ({round(time.time() - t0)} sn)", flush=True)
    p = panel.build()
    sigs = library.load_all(p)
    unis = sectors.operating_universes(p)
    inv_key = [k for k in unis if k != "tümü"][0]
    op_all, op_inv = unis["tümü"], unis[inv_key]
    log("panel ve sinyaller")

    if "--yeniden-kullan" in sys.argv and FITS.exists():  # yalnızca değerlendirme/rapor kodu değiştiyse
        with FITS.open("rb") as f:
            fits = pickle.load(f)
        safety, opp = fits["guvenlik"], fits["firsat"]
    else:
        safety = model.run(p, sigs, universe=op_all)  # 4. aşama ayarı B, değiştirilmeden
        log("güvenlik modeli")
        opp = model.run(p, sigs, {"1y": 52}, universe=op_all, target="kazanan_100", exclude=set())
        opp |= model.run(p, sigs, {"6a": 26}, universe=op_all, target="kazanan_50", exclude=set())
        log("fırsat modeli")
        FITS.parent.mkdir(parents=True, exist_ok=True)
        with FITS.open("wb") as f:
            pickle.dump({"guvenlik": safety, "firsat": opp}, f)

    price, sec, dates = p["price"], p["securities"], p["price"].index
    f52 = panel.forward_returns(price, sec, 52).reindex(dates)
    f26 = panel.forward_returns(price, sec, 26).reindex(dates)
    y100 = (f52 >= 1.0).astype(float).where(f52.notna())
    y50 = (f26 >= 0.5).astype(float).where(f26.notna())
    d52, d26 = bt.dev_dates(dates, 52), bt.dev_dates(dates, 26)

    opp1, opp6 = frame(opp[("toplam", "1y")], p), frame(opp[("toplam", "6a")], p)
    safe3, safe1 = frame(safety[("toplam", "3a")], p), frame(safety[("toplam", "1y")], p)
    vol = -sigs["dusuk_oynaklik"][1]  # basit kıyas: en yüksek geçmiş oynaklık
    mom = sigs["momentum_12_1"][1]

    # 1–2. Büyük kazanan oranı (yatırılabilir faaliyet şirketleri, 1 yıl, +%100)
    lifts = {name: bt.winner_lift(s, y100, op_inv, d52) for name, s in
             (("Fırsat modeli", opp1), ("Basit kıyas: en yüksek oynaklık", vol), ("Momentum 12-1", mom),
              ("Güvenlik modeli (1y)", safe1))}
    lift_all = bt.winner_lift(opp1, y100, op_all, d52)
    lift6 = {name: bt.winner_lift(s, y50, op_inv, d26) for name, s in
             (("Fırsat modeli (6a)", opp6), ("Basit kıyas: oynaklık", vol))}
    log("büyük kazanan oranları")

    # 3. Portföyler (maliyet sonrası)
    sims = {
        "Fırsat — ilk %10": bt.simulate(opp1, p, op_inv, "0.9"),
        "Fırsat — ilk 20": bt.simulate(opp1, p, op_inv, 20),
        "Güvenlik — ilk %10": bt.simulate(safe3, p, op_inv, "0.9"),
        "Güvenlik — ilk 20": bt.simulate(safe3, p, op_inv, 20),
        "Basit kıyas: oynaklık ilk %10": bt.simulate(vol, p, op_inv, "0.9"),
    }
    log("portföyler")

    # Kayıplar: ilk %10'da 1 yılda -%50 ve altı
    def loser_share(score, uni):
        top, allv = [], []
        for d in d52:
            s, r = score.loc[d].where(uni.loc[d]), f52.loc[d]
            ok = s.notna() & r.notna()
            if ok.sum() < 50:
                continue
            q = s[ok].rank(pct=True) > 0.9
            top.append(r[ok][q])
            allv.append(r[ok])
        t, a = pd.concat(top), pd.concat(allv)
        return {"ilk10_kayip50": (t <= -0.5).mean(), "genel_kayip50": (a <= -0.5).mean(),
                "ilk10_medyan_1y": t.median(), "genel_medyan_1y": a.median()}
    losses = {"Fırsat modeli": loser_share(opp1, op_inv), "Güvenlik modeli": loser_share(safe1, op_inv),
              "Basit kıyas: oynaklık": loser_share(vol, op_inv)}

    cal_safe = bt.calibration(safe3, p, op_inv, 13)
    cal_opp = bt.calibration(opp1, p, op_inv, 52)
    log("kalibrasyon")

    # Ön kayıtlı başarı ölçütü
    lo = lifts["Fırsat modeli"]
    c1 = lo["kat"] >= 1.5 and lo["ga_alt"] > 1.0
    c2 = lo["ust_oran"] > lifts["Basit kıyas: en yüksek oynaklık"]["ust_oran"]
    m = sims["Fırsat — ilk %10"].metrics
    c3 = m["yillik_getiri"] >= m["kiyas_yillik"]
    passed = c1 and c2 and c3

    # Bilinen kazananlar: fırsat puanı (yüzdelik, tüm faaliyet şirketleri)
    sc_pct = opp1.where(op_all).rank(axis=1, pct=True) * 100
    sym = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
    known_rows = []
    for s in KNOWN:
        cs = [c for c in sym[sym == s].index if c in sc_pct.columns]
        if not cs:
            continue
        c = cs[0]
        for d in ("2022-12-30", "2023-06-30", "2023-12-29", "2024-06-28"):
            d = dates[dates.get_indexer([pd.Timestamp(d)], method="pad")[0]]
            v, r = sc_pct.at[d, c], f52.at[d, c]
            if pd.notna(v):
                known_rows.append({"hisse": s, "tarih": d.date(), "fırsat puanı": round(v),
                                   "güvenlik puanı (1y)": round(float(safe1.where(op_all).loc[d].rank(pct=True)[c] * 100)) if pd.notna(safe1.at[d, c]) else None,
                                   "sonraki 1 yıl": pct(r)})
    known = pd.DataFrame(known_rows)

    # Son ağırlıklar (fırsat modeli)
    w = opp[("toplam", "1y")].weights.iloc[-1]
    wtab = pd.DataFrame({"ağırlık": w, "yol": [sigs[n][0] for n in w.index]}).reindex(w.abs().sort_values(ascending=False).index).head(20)

    lift_tab = pd.DataFrame([{"puan": k, "ilk %10'da kazanan oranı": pct(v["ust_oran"]), "genel oran": pct(v["genel_oran"]),
                              "kat": round(v["kat"], 2), "%90 GA": f"{v['ga_alt']:.2f} – {v['ga_ust']:.2f}"} for k, v in lifts.items()])
    lift6_tab = pd.DataFrame([{"puan": k, "ilk %10'da +%50 oranı": pct(v["ust_oran"]), "genel oran": pct(v["genel_oran"]),
                               "kat": round(v["kat"], 2), "%90 GA": f"{v['ga_alt']:.2f} – {v['ga_ust']:.2f}"} for k, v in lift6.items()])
    sim_tab = pd.DataFrame([{"portföy": k, "yıllık getiri": pct(s.metrics["yillik_getiri"]), "kıyas": pct(s.metrics["kiyas_yillik"]),
                             "yıllık fazla (ort.)": pct(s.metrics["yillik_fazla_ort"]),
                             "%90 GA": f"{pct(s.metrics['fazla_ga_alt'])} – {pct(s.metrics['fazla_ga_ust'])}",
                             "Sharpe": round(s.metrics["sharpe"], 2), "Sortino": round(s.metrics["sortino"], 2),
                             "en büyük düşüş": pct(s.metrics["en_buyuk_dusus"]), "yıllık maliyet": pct(s.metrics["yillik_maliyet"]),
                             "devir/dönem": pct(s.metrics["devir_donem"])} for k, s in sims.items()])
    bench = sims["Fırsat — ilk %10"].metrics
    years = pd.DataFrame({k: s.yearly.fark for k, s in sims.items()}).map(pct)
    loss_tab = pd.DataFrame(losses).T.map(pct)
    fmt_cal = lambda c: c.assign(ort_fazla=c.ort_fazla.map(pct), ga=lambda d: [f"{pct(a)} – {pct(b)}" for a, b in zip(c.ga_alt, c.ga_ust)],
                                  isabet=c.isabet.map(pct)).drop(columns=["ga_alt", "ga_ust"])

    lines = [
        "# Fırsat modeli ve güvenlik modeli — faaliyet şirketleri (geliştirme dönemi)", "",
        "Ön kayıt: [firsat_on_kayit.md](firsat_on_kayit.md). Evren: finans dışı faaliyet şirketleri (finans ve SPAC hariç). "
        f"Ölçüm: yatırılabilir faaliyet şirketleri, tahmin tarihi + vade < 2025-07-01. Son dönem kullanılmadı.", "",
        f"## Sonuç: ön kayıtlı ölçüt {'SAĞLANDI ✅' if passed else 'SAĞLANMADI ❌'}", "",
        f"1. İlk %10'da büyük kazanan oranı genelin ≥ 1,5 katı ve GA alt sınırı > 1: **{'evet' if c1 else 'hayır'}** "
        f"({lo['kat']:.2f} kat, GA {lo['ga_alt']:.2f}–{lo['ga_ust']:.2f})",
        f"2. Basit kıyastan (en yüksek oynaklık) yüksek: **{'evet' if c2 else 'hayır'}** "
        f"({pct(lo['ust_oran'])} ↔ {pct(lifts['Basit kıyas: en yüksek oynaklık']['ust_oran'])})",
        f"3. İlk %10 portföyü (maliyet sonrası) eşit ağırlıklı evrenden düşük değil: **{'evet' if c3 else 'hayır'}** "
        f"({pct(m['yillik_getiri'])} ↔ {pct(m['kiyas_yillik'])} yıllık)", "",
        "## 1 yılda +%100 kazananlar (yatırılabilir faaliyet şirketleri)", "", lift_tab.to_markdown(index=False), "",
        f"Tüm faaliyet şirketlerinde (likit olmayanlar dahil) fırsat modeli: {pct(lift_all['ust_oran'])} ↔ genel "
        f"{pct(lift_all['genel_oran'])} ({lift_all['kat']:.2f} kat, GA {lift_all['ga_alt']:.2f}–{lift_all['ga_ust']:.2f}).", "",
        "Yıl yıl (kat, fırsat modeli):", "", lifts["Fırsat modeli"]["yillik"].round(2).to_frame().T.to_markdown(index=False), "",
        "## İkincil: 6 ayda +%50", "", lift6_tab.to_markdown(index=False), "",
        "## İlk %10'un 1 yıllık sonuç dağılımı", "",
        "Büyük kazananları yakalamak büyük kayıplarla birlikte gelebilir; bu yüzden %50+ kayıp payı da gösteriliyor.", "",
        loss_tab.rename(columns={"ilk10_kayip50": "ilk %10'da −%50 ve altı", "genel_kayip50": "genelde −%50 ve altı",
                                 "ilk10_medyan_1y": "ilk %10 medyan 1y getiri", "genel_medyan_1y": "genel medyan 1y getiri"}).to_markdown(), "",
        "## Portföy simülasyonu (maliyet sonrası, 4 haftada bir dengeleme)", "",
        f"Kıyas: yatırılabilir faaliyet şirketlerinin eşit ağırlıklı portföyü (maliyetsiz). Kıyas Sharpe "
        f"{bench['kiyas_sharpe']:.2f}, en büyük düşüş {pct(bench['kiyas_en_buyuk_dusus'])}. GA: 52 haftalık bloklarla bootstrap.", "",
        sim_tab.to_markdown(index=False), "",
        "Yıl yıl fazla getiri (portföy − kıyas):", "", years.to_markdown(), "",
        "## Puan dilimi kalibrasyonu", "",
        "Güvenlik puanı (3 ay): her dilimin gerçekleşen ortalama fazla getirisi (aynı evrenin medyanına göre, kırpılmış), "
        "%90 GA ve medyanı geçme oranı.", "", fmt_cal(cal_safe).to_markdown(index=False), "",
        "Fırsat puanı (1 yıl):", "", fmt_cal(cal_opp).to_markdown(index=False), "",
        "## Bilinen kazananlar: o tarihteki puanlar", "", known.to_markdown(index=False), "",
        "## Fırsat modelinin son ağırlıkları (en büyük 20)", "", wtab.round(4).to_markdown(), "",
    ]
    REPORT.write_text("\n".join(lines))
    print("\n".join(lines[:40]))
    log("bitti")


if __name__ == "__main__":
    main()

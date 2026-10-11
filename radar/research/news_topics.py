"""Haber konusu belirtileri (GDELT, 2015→): şirketin haberleri hangi konularda, ne hızla değişiyor, konu piyasada yükseliyor mu?

Örnek mantık: NVDA — "yapay zekâ / teknoloji" konusu bütün haberlerde yükselirken NVDA'nın haberlerinin büyük kısmı bu konuda
(konu rüzgârı yüksek). PLTR — haberlerinde "uzay / savunma / devlet sözleşmesi" payı son 3 ayda arttı (konu ivmesi).
VW (örnek) — "ticaret / Çin / yaptırım" payı artıyor (olumsuz olabilir).

Her tarih t için yalnızca t'den önce TAMAMLANMIŞ aylar kullanılır (ay sonu verisi bir sonraki ayın başında bilinir).
Belirtiler (aile başına): haber_<aile>_pay (son 3 ay payı), haber_<aile>_ivme (son 3 ay payı ÷ önceki 12 ay payı, log),
haber_<aile>_ruzgar (ailenin bütün haberlerdeki son 3 ay / önceki 12 ay artışı × şirketin son 12 ay payı).
Ayrıca haber_hacmi (son 3 ay, log) ve haber_hacmi_ivme.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

FAMILIES = {
    "yz_teknoloji": ["TECH_AUTOMATION", "WB_676_CLOUD_COMPUTING", "WB_660_BUSINESS_INTELLIGENCE",
                     "WB_2399_ICT_INNOVATION_AND_TRANSFORMATION", "WB_652_ICT_APPLICATIONS", "WB_2401_ICT_INNOVATION_METHODOLOGIES"],
    "uzay_savunma_devlet": ["WB_2120_SATELLITES", "MILITARY", "WB_957_GOVERNMENT_PROCUREMENT", "TAX_FNCACT_CONTRACTOR",
                            "TAX_WEAPONS_AIR_DEFENSE_SYSTEMS", "WB_1889_PROCUREMENT_PLANNING"],
    "inovasyon_patent": ["SOC_INNOVATION", "WB_376_INNOVATION_TECHNOLOGY_AND_ENTREPRENEURSHIP",
                         "WB_377_FIRM_INNOVATION_PRODUCTIVITY_AND_GROWTH", "WB_1041_PATENTS", "WB_380_FUNDING_INNOVATION"],
    "saglik_ilac": ["WB_1431_CANCER", "TAX_DISEASE_CANCER", "WB_1358_GENERIC_DRUGS", "WB_1435_OBESITY", "TAX_DISEASE_OBESITY",
                    "WB_1433_DIABETES", "TAX_CHRONICDISEASE_DIABETES"],
    "enerji_emtia": ["ENV_OIL", "ECON_OILPRICE", "WB_2936_GOLD", "ECON_GOLDPRICE", "WB_1699_METAL_ORE_MINING", "ENV_MINING",
                     "ENV_SOLAR", "WB_525_RENEWABLE_ENERGY", "WB_509_NUCLEAR_ENERGY", "ENV_NUCLEARPOWER"],
    "kripto": ["ECON_BITCOIN"],
    "borsa_olaylari": ["ECON_IPO", "ECON_EARNINGSREPORT"],
    "ticaret_cin_yaptirim": ["WB_698_TRADE", "WB_778_NON_TARIFF_MEASURES", "SANCTIONS", "EPU_POLICY_PEOPLE_BANK_OF_CHINA"],
    "hukuk_sorunu": ["TRIAL", "WB_2025_INVESTIGATION", "WB_2020_BRIBERY_FRAUD_AND_COLLUSION", "SCANDAL"],
    "finansal_sikinti": ["ECON_BANKRUPTCY", "WB_1277_BANKRUPTCY_AND_LIQUIDATION", "ECON_DEBT", "UNEMPLOYMENT", "RESIGNATION", "STRIKE"],
    "siber": ["CYBER_ATTACK", "WB_2457_CYBER_CRIME"],
}
SHORT, LONG = 3, 12


def _family_of() -> dict[str, str]:
    return {t: f for f, ts in FAMILIES.items() for t in ts}


def features(day: pd.DataFrame, pairs: pd.DataFrame, dates: pd.DatetimeIndex, columns) -> dict[str, pd.DataFrame]:
    """dates × columns tabloları (yalnızca istenen tarihler; aylık çerçeve için)."""
    fam = _family_of()
    cols = pd.Index([str(c) for c in columns])
    months = pd.period_range("2015-01", pd.Timestamp(dates.max()).to_period("M"), freq="M")
    mi = {m: i for i, m in enumerate(months)}
    ci = {c: i for i, c in enumerate(cols)}
    nm, nc, nf = len(months), len(cols), len(FAMILIES)
    fnames = list(FAMILIES)

    pr = pairs.assign(cik=pairs.cik.astype(str))
    pr = pr[pr.cik.isin(ci)]
    m_idx = pr.date.dt.to_period("M").map(mi)
    pr = pr.assign(m=m_idx, c=pr.cik.map(ci)).dropna(subset=["m"])
    total = np.zeros((nm, nc))
    np.add.at(total, (pr.m.astype(int).to_numpy(), pr.c.to_numpy()), pr["count"].to_numpy(float))
    famc = np.zeros((nf, nm, nc))
    sub = pr[pr.theme.isin(fam)]
    np.add.at(famc, (sub.theme.map({t: fnames.index(f) for t, f in fam.items()}).to_numpy(), sub.m.astype(int).to_numpy(),
                     sub.c.to_numpy()), sub["count"].to_numpy(float))

    # Bütün haberlerde ailenin payı (ay bazında)
    dd = day.assign(m=day.date.dt.to_period("M").map(mi)).dropna(subset=["m"])
    g_total = np.bincount(dd.m.astype(int), weights=dd["count"].to_numpy(float), minlength=nm)
    dsub = dd[dd.theme.isin(fam)]
    g_fam = np.zeros((nf, nm))
    np.add.at(g_fam, (dsub.theme.map({t: fnames.index(f) for t, f in fam.items()}).to_numpy(), dsub.m.astype(int).to_numpy()),
              dsub["count"].to_numpy(float))

    def window(a: np.ndarray, end: int, n: int) -> np.ndarray:  # [end-n+1, end] toplamı (son eksen hariç ilk eksen ay)
        lo = max(end - n + 1, 0)
        return a[lo:end + 1].sum(axis=0) if end >= 0 else np.zeros(a.shape[1:])

    out = {f"haber_{f}_{k}": np.full((len(dates), nc), np.nan) for f in fnames for k in ("pay", "ivme", "ruzgar")}
    out["haber_hacmi"] = np.full((len(dates), nc), np.nan)
    out["haber_hacmi_ivme"] = np.full((len(dates), nc), np.nan)
    for i, t in enumerate(dates):
        end = mi.get(pd.Timestamp(t).to_period("M") - 1, -1)  # son tamamlanmış ay
        if end < SHORT + LONG - 1:
            continue
        tot_s = window(total, end, SHORT)
        tot_l = window(total, end - SHORT, LONG)
        tot_12 = window(total, end, LONG)
        has = tot_12 >= 20  # en az 20 konu geçişi
        out["haber_hacmi"][i, has] = np.log1p(tot_s[has])
        out["haber_hacmi_ivme"][i, has] = np.log((tot_s[has] / SHORT + 1) / (tot_l[has] / LONG + 1))
        gs, gl = window(g_total[:, None], end, SHORT)[0], window(g_total[:, None], end - SHORT, LONG)[0]
        for k, f in enumerate(fnames):
            fs, fl, f12 = window(famc[k], end, SHORT), window(famc[k], end - SHORT, LONG), window(famc[k], end, LONG)
            pay_s = np.where(tot_s > 0, fs / np.maximum(tot_s, 1), 0.0)
            pay_l = np.where(tot_l > 0, fl / np.maximum(tot_l, 1), 0.0)
            out[f"haber_{f}_pay"][i, has] = pay_s[has]
            out[f"haber_{f}_ivme"][i, has] = np.log((pay_s[has] + 1e-4) / (pay_l[has] + 1e-4))
            g_mom = np.log((window(g_fam[k][:, None], end, SHORT)[0] / max(gs, 1) + 1e-6) /
                           (window(g_fam[k][:, None], end - SHORT, LONG)[0] / max(gl, 1) + 1e-6))
            out[f"haber_{f}_ruzgar"][i, has] = g_mom * (f12[has] / np.maximum(tot_12[has], 1))
    return {k: pd.DataFrame(v, index=dates, columns=cols) for k, v in out.items()}


def rising_topics(day: pd.DataFrame, pairs: pd.DataFrame, dates: pd.DatetimeIndex, columns, top_n: int = 30,
                  min_base: float = 2000) -> dict[str, pd.DataFrame]:
    """Elle seçilmiş liste olmadan: her tarihte, yalnızca o güne kadarki haberlere bakarak, bütün konular arasında payı
    en hızlı yükselen top_n konuyu seç (son 3 ay payı ÷ önceki 12 ay payı; önceki 12 ayda en az min_base geçiş).
    - yukselen_konu_maruziyeti: şirketin son 12 ay haberlerinin ne kadarı bu yükselen konularda (ivmeyle ağırlıklı)
    - yukselen_konuya_yonelis: şirketin bu konulardaki payının son 3 ayda önceki 12 aya göre artışı
    Konu listesi her ay kendiliğinden değişir; geçmişte olmayan / önemsiz olan konu yükselince listeye girer."""
    cols = pd.Index([str(c) for c in columns])
    ci = {c: i for i, c in enumerate(cols)}
    months = pd.period_range("2015-01", pd.Timestamp(dates.max()).to_period("M"), freq="M")
    mi = {m: i for i, m in enumerate(months)}
    themes = pd.Index(sorted(set(day.theme)))
    ti = {t: i for i, t in enumerate(themes)}
    dd = day.assign(m=day.date.dt.to_period("M").map(mi)).dropna(subset=["m"])
    G = np.zeros((len(months), len(themes)))
    np.add.at(G, (dd.m.astype(int).to_numpy(), dd.theme.map(ti).to_numpy()), dd["count"].to_numpy(float))
    gtot = G.sum(1)
    pr = pairs.assign(cik=pairs.cik.astype(str))
    pr = pr[pr.cik.isin(ci) & pr.theme.isin(ti)]
    pm = pr.date.dt.to_period("M").map(mi).to_numpy()
    ok = ~pd.isna(pm)
    pm = pm[ok].astype(int); pc = pr.cik.map(ci).to_numpy()[ok]; pt = pr.theme.map(ti).to_numpy()[ok]
    pv = pr["count"].to_numpy(float)[ok]
    ctot = np.zeros((len(months), len(cols)))
    np.add.at(ctot, (pm, pc), pv)
    expo = np.full((len(dates), len(cols)), np.nan)
    turn = np.full((len(dates), len(cols)), np.nan)
    chosen = {}
    for i, t in enumerate(dates):
        end = mi.get(pd.Timestamp(t).to_period("M") - 1, -1)
        if end < SHORT + LONG - 1:
            continue
        s_lo, l_lo, l_hi = end - SHORT + 1, end - SHORT - LONG + 1, end - SHORT
        share_s = G[s_lo:end + 1].sum(0) / max(gtot[s_lo:end + 1].sum(), 1)
        base = G[l_lo:l_hi + 1].sum(0)
        share_l = base / max(gtot[l_lo:l_hi + 1].sum(), 1)
        mom = np.where(base >= min_base, np.log((share_s + 1e-7) / (share_l + 1e-7)), -np.inf)
        top = np.argsort(-mom)[:top_n]
        top = top[np.isfinite(mom[top]) & (mom[top] > 0)]
        chosen[str(pd.Timestamp(t).date())] = [str(themes[k]) for k in top[:10]]
        w = np.zeros(len(themes)); w[top] = mom[top]
        sel = w[pt] > 0
        in12 = sel & (pm >= end - LONG + 1) & (pm <= end)
        in3 = sel & (pm >= s_lo) & (pm <= end)
        inl = sel & (pm >= l_lo) & (pm <= l_hi)
        e12 = np.bincount(pc[in12], weights=pv[in12] * w[pt[in12]], minlength=len(cols))
        c3 = np.bincount(pc[in3], weights=pv[in3], minlength=len(cols))
        cl = np.bincount(pc[inl], weights=pv[inl], minlength=len(cols))
        t12 = ctot[end - LONG + 1:end + 1].sum(0)
        t3 = ctot[s_lo:end + 1].sum(0)
        tl = ctot[l_lo:l_hi + 1].sum(0)
        has = t12 >= 20
        expo[i, has] = e12[has] / t12[has]
        turn[i, has] = np.log((c3[has] / np.maximum(t3[has], 1) + 1e-4) / (cl[has] / np.maximum(tl[has], 1) + 1e-4))
    out = {"yukselen_konu_maruziyeti": pd.DataFrame(expo, index=dates, columns=cols),
           "yukselen_konuya_yonelis": pd.DataFrame(turn, index=dates, columns=cols)}
    out["_secilen_konular"] = chosen  # rapor için: her ay seçilen ilk 10 yükselen konu
    return out

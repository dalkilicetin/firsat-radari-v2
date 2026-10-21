"""Yay mekanizmali yapay piyasa simulatoru (gunluk adim).

log fiyat = F (temel deger) + m (sapma = yay gerilimi).
Panik olaylari m'yi asagi iter, m ortalamaya doner (yay). Bozulma olaylari F'yi kalici dusurur.
Simulasyon olcum aletini dener; piyasada yay oldugunu KANITLAMAZ.
"""
from dataclasses import dataclass, field, replace

import numpy as np
import pandas as pd


@dataclass
class Ayar:
    n_gun: int = 252 * 60
    n_hisse: int = 200
    baslangic: str = "1990-01-02"
    mu: float = 0.10 / 252           # log surukleme; bozulmalar ~%2,7/yil goturdugu icin 0.07'den yukari
    sF: float = 0.10 / np.sqrt(252)
    # bozulma (kalici temel deger kaybi)
    lam_B: float = 1 / 12            # yilda
    sB: tuple = (0.20, 0.45)         # log kayip
    DB: tuple = (120, 400)           # gun
    rho_B: float = 0.3               # bozulmanin m'ye yansiyan asiri tepki orani
    # panik (gecici sapma)
    lam_P: float = 1 / 5
    sP: tuple = (0.10, 0.35)
    DP: tuple = (10, 50)
    yarilanma: float = 60.0          # m yarilanma suresi (gun)
    sm: float = 0.004
    sigma0: float = 0.008
    korku: float = 0.5
    panik_kredi: float = 2.0
    # gelgit (likidite) ve kenetlenme
    gelgit_etkisi: bool = True
    yarilanma_lik: float = 120.0
    sl: float = 0.03
    ortak_dinamik: bool = True       # False: ortak faktor payi sabit (kontrol)
    c0: float = 0.15
    c1: float = 0.60
    olay_zorla: list | None = None   # [(gun, "panik"|"bozulma", buyukluk, sure)] testler icin


@dataclass
class Dunya:
    endeks: pd.DataFrame
    hisseler: pd.DataFrame
    meta: pd.DataFrame
    olaylar: pd.DataFrame
    ayar: Ayar


def _olaylar(ay: Ayar, rng):
    if ay.olay_zorla is not None:
        return [dict(gun=g, tur=t, buyukluk=b, sure=int(d)) for g, t, b, d in ay.olay_zorla]
    ol = []
    for tur, lam, sb, dd in (("bozulma", ay.lam_B, ay.sB, ay.DB), ("panik", ay.lam_P, ay.sP, ay.DP)):
        gelis = np.flatnonzero(rng.random(ay.n_gun) < lam / 252)
        for g in gelis:
            ol.append(dict(gun=int(g), tur=tur, buyukluk=float(rng.uniform(*sb)), sure=int(rng.integers(dd[0], dd[1] + 1))))
    return sorted(ol, key=lambda o: o["gun"])


def simule(ay: Ayar, tohum: int = 0) -> Dunya:
    rng = np.random.default_rng(tohum)
    n, N = ay.n_gun, ay.n_hisse
    ol = _olaylar(ay, rng)

    sok_m = np.zeros(n)         # m'ye eklenen gunluk sok
    akis = np.zeros(n)          # bozulma log kayip hizi (pozitif)
    aktif = np.zeros(n, bool)   # bozulma suruyor mu
    sahm = np.zeros(n)
    for o in ol:
        g, d, b = o["gun"], o["sure"], o["buyukluk"]
        a, z = g, min(g + d, n)
        if o["tur"] == "panik":
            sok_m[a:z] -= b / d
        else:
            akis[a:z] += b / d
            sok_m[a:z] -= ay.rho_B * b / d
            aktif[a:z] = True
            bas = min(g + int(rng.integers(60, 151)), n)
            sahm[bas:min(g + d + 120, n)] = 1.0

    e = {k: rng.standard_normal(n) for k in ("F", "m", "g2", "l", "k", "z")}
    e_i = rng.standard_normal((n, N))
    e_u = rng.standard_normal((n, N))

    beta = rng.uniform(0.6, 1.6, N)
    kalite = rng.uniform(0, 1, N)
    asiri = beta * rng.uniform(0.7, 1.3, N)
    sig_i = 0.015

    kappa = np.log(2) / ay.yarilanma
    d_l = np.exp(-np.log(2) / ay.yarilanma_lik)
    d_bb = np.exp(-np.log(2) / 252)
    d_u = np.exp(-np.log(2) / 40)

    F = np.zeros(n); m = np.zeros(n); lik = np.zeros(n); kred = np.full(n, 1.8); bb = np.zeros(n)
    Fi = np.zeros((n, N)); u = np.zeros((n, N))
    stres = np.zeros(n)
    for t in range(n - 1):
        kap = kappa
        if ay.gelgit_etkisi and t >= 63:
            kap = kappa * (1 + 0.4 * np.clip(-(lik[t] - lik[t - 63]), -1, 1))   # likidite gevserken yay daha hizli doner
        m[t + 1] = m[t] * np.exp(-kap) + ay.sm * e["m"][t] + sok_m[t]
        stres[t] = np.clip(max(-m[t], 0) * 3 + 0.5 * aktif[t], 0, 1)
        sigma_t = ay.sigma0 * (1 + 4 * max(-m[t], 0) + 1.5 * aktif[t])
        mu_t = ay.mu - (0.02 * lik[t] / 252 if ay.gelgit_etkisi else 0.0)     # gevsek likidite sürüklemeyi arttirir
        dF = mu_t + ay.sF * e["F"][t] - akis[t] + sigma_t * e["g2"][t]
        F[t + 1] = F[t] + dF
        lik[t + 1] = lik[t] * d_l + ay.sl * e["l"][t] + 4 * (max(-sok_m[t], 0) + akis[t])
        bb[t + 1] = bb[t] * d_bb + akis[t]
        hedef = 1.8 + 8 * bb[t] + ay.panik_kredi * max(-m[t], 0)
        kred[t + 1] = kred[t] + 0.05 * (hedef - kred[t]) + 0.03 * e["k"][t]
        c = ay.c0 + ay.c1 * stres[t] if ay.ortak_dinamik else ay.c0
        sis = dF - mu_t
        Fi[t + 1] = (Fi[t] + mu_t + beta * sis + 0.8 * (kalite - 0.5) * akis[t]
                     + sig_i * (np.sqrt(c) * e["z"][t] + np.sqrt(1 - c) * e_i[t]))
        u[t + 1] = d_u * u[t] + 0.01 * e_u[t]
    stres[n - 1] = stres[n - 2]

    idx = pd.bdate_range(ay.baslangic, periods=n)
    logp = F + m
    ret = pd.Series(np.diff(logp, prepend=logp[0]), index=idx)
    vix = np.clip(100 * np.sqrt(252) * ret.ewm(halflife=10).std().bfill().to_numpy() * 1.15
                  + ay.korku * 100 * np.maximum(-m, 0), 9, 90)
    endeks = pd.DataFrame({"adj": 100 * np.exp(logp), "F": F, "m": m, "vix": vix, "kredi": kred,
                           "sahm": sahm, "likidite": lik}, index=idx)
    cols = [f"H{i:03d}" for i in range(N)]
    hisseler = pd.DataFrame(100 * np.exp(Fi + asiri * m[:, None] + u), index=idx, columns=cols)
    meta = pd.DataFrame({"beta": beta, "kalite": kalite, "asiri": asiri}, index=cols)
    olaylar = pd.DataFrame(ol)
    if len(olaylar):
        olaylar["tarih"] = idx[olaylar["gun"].to_numpy()]
    return Dunya(endeks, hisseler, meta, olaylar, ay)

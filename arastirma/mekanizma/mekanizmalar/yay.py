"""Yay (endeks): asiri dusus + panik + genislik gerilimi ve bosalma isaretleri.

Dedektor SADECE adj, vix, kredi, sahm ve hisse fiyatlarini gorur (simulasyondaki F ve m'yi gormez).
"""
import numpy as np
import pandas as pd

from mekanizma.ozellik import fiyat


def _itki(oran, alt, ust, n):
    """Son n bar icinde alt'in altindan ust'un ustune cikis (Zweig tipi itki)."""
    en_dusuk = oran.rolling(n + 1, min_periods=1).min()
    return (oran > ust) & (en_dusuk < alt)


def ozellikler(adj, p, hisseler=None, vix=None, kredi=None, sahm=None):
    oz = pd.DataFrame(index=adj.index)
    oz["dd"] = fiyat.dusus(adj, p["dd_n"])
    oz["hiz"] = fiyat.getiri(adj, p["hiz_n"])
    oz["teyit"] = adj > adj.rolling(p["teyit_n"]).max().shift(1)
    if vix is not None:
        oz["vix_z"] = fiyat.zskor(vix, p["vix_z_n"])
        oz["vix_dusus"] = vix <= (1 - p["vix_dusus"]) * vix.rolling(p["vix_dusus_n"], min_periods=1).max()
    if hisseler is not None:
        oz["genislik"] = 1 - fiyat.ust_oran(hisseler, p["genislik_n"])
        kisa = fiyat.ust_oran(hisseler, p["itki_ma"])
        oz["itki"] = _itki(kisa, p["itki_alt"], p["itki_ust"], p["itki_n"])
    if kredi is not None:
        oz["kredi60"] = kredi - kredi.shift(p["kredi_n"])
    if sahm is not None:
        oz["sahm"] = sahm
    return oz


def gerilim_skoru(oz, p, min_bilesen=2):
    """Bilesenlerin genisleyen yuzdeliklerinin ortalamasi (0-1). Eksik bilesen atlanir."""
    parcalar = []
    for ad, isaret in (("dd", -1), ("vix_z", 1), ("genislik", 1)):
        if ad in oz:
            parcalar.append(fiyat.yuzdelik_genisleyen(isaret * oz[ad], p["min_gecmis"]))
    if not parcalar:
        return pd.Series(np.nan, index=oz.index)
    m = pd.concat(parcalar, axis=1)
    skor = m.mean(axis=1)
    skor[m.notna().sum(axis=1) < min_bilesen] = np.nan
    return skor


def tur_tahmini(oz, p):
    """'bozulma': kredi spread'i acildi veya Sahm tetikte; aksi halde 'panik'."""
    boz = pd.Series(False, index=oz.index)
    if "kredi60" in oz:
        boz |= oz["kredi60"] > p["kredi_esik"]
    if "sahm" in oz:
        boz |= oz["sahm"] == 1
    return boz.map({True: "bozulma", False: "panik"})


def sinyaller(oz, p):
    skor = gerilim_skoru(oz, p)
    y1 = ((skor >= p["bilesik_yuzdelik"]) & (oz["dd"] <= p["dd_esik"])).fillna(False)
    bosalma = pd.Series(False, index=oz.index)
    for c in ("vix_dusus", "itki", "teyit"):
        if c in oz:
            bosalma |= oz[c].fillna(False).astype(bool)
    yakin = y1.rolling(p["pencere"] + 1, min_periods=1).max().astype(bool)
    y2 = (yakin & bosalma & (oz["dd"] <= p["dd_esik"])).fillna(False)
    out = pd.DataFrame({"skor": skor, "Y1": y1, "Y2": y2, "bosalma": bosalma,
                        "basit": (oz["dd"] <= p["basit_dd"]).fillna(False), "tur": tur_tahmini(oz, p)})
    return out


def durum(oz, sin):
    """Son bar: gerilim, bilesenler, tur."""
    son = oz.index[-1]
    return dict(tarih=str(son.date()), skor=None if np.isnan(sin["skor"].iloc[-1]) else float(sin["skor"].iloc[-1]),
                Y1=bool(sin["Y1"].iloc[-1]), Y2=bool(sin["Y2"].iloc[-1]), tur=sin["tur"].iloc[-1],
                bilesenler={k: (None if pd.isna(v) else float(v)) for k, v in oz.iloc[-1].items() if k in ("dd", "hiz", "vix_z", "genislik", "kredi60")})

"""Tarihi kriz katalogu yukleyicisi ve turetilen sutunlar."""
import numpy as np
import pandas as pd

from mekanizma.ayarlar import TARIH

TARIH_SUTUNLARI = ["zirve_tarih", "dip_tarih", "toparlanma_tarih", "vix_zirve_tarih"]
KREDI_SIRA = {"dusuk": 1, "orta": 2, "orta_yuksek": 3, "yuksek": 4, "cok_yuksek": 5, "yetersiz": 0}


def _gun(a, b):
    """Iki tarih arasi is gunu (b sonrasi ise pozitif). NaT ise NaN."""
    out = []
    for x, y in zip(a, b):
        out.append(np.nan if pd.isna(x) or pd.isna(y) else float(np.busday_count(x.date(), y.date())))
    return pd.Series(out, index=a.index)


def katalog(yol=None) -> pd.DataFrame:
    df = pd.read_csv(yol or TARIH / "kriz_katalogu.csv", comment="#")
    for c in TARIH_SUTUNLARI:
        df[c] = pd.to_datetime(df[c])
    df["dusus"] = df["dip"] / df["zirve"] - 1
    df["gun_dibe"] = _gun(df["zirve_tarih"], df["dip_tarih"])
    df["gun_toparlanma"] = _gun(df["dip_tarih"], df["toparlanma_tarih"])
    df["toplam_gun"] = df["gun_dibe"] + df["gun_toparlanma"]
    df["hiz"] = df["dusus"] / df["gun_dibe"]                      # gunluk ortalama kayip (negatif)
    df["sertlik"] = df["gun_toparlanma"] / df["gun_dibe"]         # <1: geri donus dususten hizli
    df["vix_dipten_once"] = _gun(df["vix_zirve_tarih"], df["dip_tarih"])   # >0: VIX zirvesi dipten once
    df["toparlanma_ay"] = df["gun_toparlanma"] / 21
    df["kredi_sayi"] = df["kredi_stresi"].map(KREDI_SIRA)
    df["resesyon_sayi"] = (df["resesyon"] == "E").astype(int)
    return df

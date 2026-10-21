"""Kenetlenme olcumleri: hisselerin birlikte hareketi. Sadece gecmise bakar."""
import numpy as np
import pandas as pd


def ort_ikili_korelasyon(getiri_genis, n=63, en_cok=60):
    """Ortalama ikili korelasyon (sigma_i*sigma_j agirlikli): rho = (N^2*var_p - sum s_i^2) / ((sum s_i)^2 - sum s_i^2),
    var_p = esit agirlikli portfoy getirisinin n barlik varyansi, s_i = hisse i'nin n barlik std'si. Hepsi ayni pencere; mukemmel korelasyonda 1.
    Hiz icin ilk `en_cok` sutun kullanilir (belirleyici)."""
    r = getiri_genis.iloc[:, :en_cok]
    N = r.shape[1]
    s = r.rolling(n, min_periods=n).std()
    var_p = r.mean(axis=1).rolling(n, min_periods=n).var()
    s2 = (s ** 2).sum(axis=1, min_count=N)
    s1 = s.sum(axis=1, min_count=N)
    return ((N ** 2 * var_p - s2) / (s1 ** 2 - s2).replace(0, np.nan)).clip(-1, 1)


def kesitsel_dagilim(getiri_genis, n=21):
    """Gunluk kesitsel standart sapmanin n barlik ortalamasi (yuksek = hisseler birbirinden ayriliyor)."""
    return getiri_genis.std(axis=1).rolling(n, min_periods=n // 2).mean()

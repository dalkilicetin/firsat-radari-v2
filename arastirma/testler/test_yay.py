import numpy as np

from mekanizma.hipotez import yukle
from mekanizma.mekanizmalar import yay
from mekanizma.sim.piyasa import Ayar, simule

P = yukle("yay")["gunluk"]


def _calistir(e, hisseler, p=P):
    oz = yay.ozellikler(e["adj"], p, hisseler, e["vix"], e["kredi"], e["sahm"])
    return oz, yay.sinyaller(oz, p)


def test_buyuk_panikleri_yakalar():
    yak, top = 0, 0
    for tohum in range(3):
        d = simule(Ayar(), tohum)
        _, sg = _calistir(d.endeks, d.hisseler)
        for _, o in d.olaylar[(d.olaylar.tur == "panik") & (d.olaylar.buyukluk >= 0.25)].iterrows():
            top += 1
            yak += bool(sg["Y1"].iloc[o.gun: o.gun + o.sure + 60].any())
    assert top >= 10 and yak / top >= 0.70


def test_sakin_piyasada_alarm_tavani():
    # Olaysiz dunyada da rastgele dususler Y1 uretir (~%3,5); bu sorun S3 deneyinde (Y1 getirisi koşulsuza göre fark mi?) olculur.
    # Burada sadece mantikli bir tavan kontrolu var.
    d = simule(Ayar(lam_P=0, lam_B=0), 0)
    _, sg = _calistir(d.endeks, d.hisseler)
    assert sg["Y1"].mean() < 0.08


def test_tur_tahmini_kredisiz_panik():
    # Panik kredi spread'ini acmiyorsa kural calisir; bozulmanin gec evresinde (Sahm devrede) de dogru.
    d = simule(Ayar(n_gun=1500, n_hisse=20, panik_kredi=0.0,
                    olay_zorla=[(400, "bozulma", 0.30, 200), (1100, "panik", 0.30, 30)]), 0)
    _, sg = _calistir(d.endeks, d.hisseler)
    assert (sg["tur"].iloc[600:700] == "bozulma").mean() > 0.8
    assert (sg["tur"].iloc[1120:1150] == "panik").mean() > 0.8


def test_tur_tahmini_kredili_panik_yanilir():
    # Bilinen zayiflik: panik de kredi spread'ini acarsa (1998, 2020 gibi) kural paniga 'bozulma' der.
    # Bu bir hata degil olculecek bir sinir: L6-S1'de panik_kredi duyarliligi olarak raporlanir.
    d = simule(Ayar(n_gun=1500, n_hisse=20, panik_kredi=8.0, olay_zorla=[(1100, "panik", 0.30, 30)]), 0)
    _, sg = _calistir(d.endeks, d.hisseler)
    assert (sg["tur"].iloc[1120:1150] == "bozulma").mean() > 0.5


def test_yay_sizinti_yok():
    d = simule(Ayar(n_gun=900, n_hisse=10), 2)
    e, h = d.endeks.copy(), d.hisseler.copy()
    _, tam = _calistir(e, h)
    rng = np.random.default_rng(0)
    for t in (500, 700):
        e2, h2 = e.copy(), h.copy()
        e2.iloc[t + 1:] = rng.uniform(1, 500, e2.iloc[t + 1:].shape)
        h2.iloc[t + 1:] = rng.uniform(1, 500, h2.iloc[t + 1:].shape)
        _, sg = _calistir(e2, h2)
        a, b = tam.iloc[t], sg.iloc[t]
        assert (np.isnan(a["skor"]) and np.isnan(b["skor"])) or abs(a["skor"] - b["skor"]) < 1e-9
        for c in ("Y1", "Y2", "basit", "tur"):
            assert a[c] == b[c], (c, t)

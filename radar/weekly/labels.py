"""Raporda kullanılan Türkçe adlar."""

from __future__ import annotations

HORIZONS = {"1h": "1 hafta", "1a": "1 ay", "3a": "3 ay", "6a": "6 ay", "1y": "1 yıl"}
ROADS = {"yol1": "İş modeli", "yol2": "Gündem", "yol3": "Kurumsal", "yol4": "Tema", "piyasa": "Piyasa"}

SIGNALS = {
    "momentum_12_1": "Son 12 ayın fiyat performansı (son ay hariç)",
    "kisa_vade_donus": "Geçen haftaki fiyat hareketinin tersi",
    "kucuk_boyut": "Şirketin küçüklüğü (piyasa değeri)",
    "gelir_buyumesi": "Gelir büyümesi",
    "buyume_ivmesi": "Büyümenin hızlanması",
    "brut_marj_degisimi": "Brüt marj değişimi",
    "faaliyet_marji_degisimi": "Faaliyet marjı değişimi",
    "arge_yogunlugu": "Ar-Ge harcamasının gelire oranı",
    "serbest_nakit_getirisi": "Serbest nakit akışı / piyasa değeri",
    "kazanc_getirisi": "Net kâr / piyasa değeri",
    "tahakkuklar_dusuk": "Kârın nakde dönüşmesi (düşük tahakkuk)",
    "varlik_buyumesi_dusuk": "Varlıkların ölçülü büyümesi",
    "metin_benzerligi_is_tanimi": "10-K iş tanımının geçen yıla benzerliği",
    "metin_benzerligi_riskler": "10-K risk bölümünün geçen yıla benzerliği",
    "metin_benzerligi_yonetim": "10-K yönetim değerlendirmesinin geçen yıla benzerliği",
    "metin_benzerligi_ortalama": "10-K metninin geçen yıla genel benzerliği",
    "risk_bolumu_buyumesi_dusuk": "10-K risk bölümünün büyümemesi",
    "devamlilik_suphesi": "Denetçinin işletmenin sürekliliğinden şüphe etmesi",
    "wiki_ilgi_ivmesi": "Wikipedia ilgisinin artışı",
    "wiki_ani_ilgi": "Wikipedia'da ani ilgi",
    "haber_ivmesi": "Haber sayısının artışı",
    "haber_ani_artis": "Haberlerde ani artış",
    "haber_ton_degisimi": "Haber tonunun iyileşmesi",
    "haber_ton_seviyesi": "Haber tonu",
    "icerden_alici_sayisi_90g": "Son 90 günde hisse alan yönetici/ortak sayısı",
    "icerden_alim_kumesi_3plus": "Son 90 günde 3+ yöneticinin hisse alması",
    "icerden_alim_tutar_piyasa_degeri": "Yönetici alım tutarı / piyasa değeri",
    "ust_yonetici_alimi_90g": "CEO/CFO'nun son 90 günde hisse alması",
    "kurumsal_sahip_degisimi": "Hisseyi tutan fon sayısındaki değişim",
    "kurumsal_hisse_degisimi_payi": "Fonların tuttuğu paydaki değişim",
    "geri_alim_getirisi": "Hisse geri alımı / piyasa değeri",
    "tema_ruzgari": "Şirketin temalarına ilgi artışı",
    "tema_ruzgari_v1_uzun": "Temalara uzun vadeli ilgi artışı",
    "tema_ruzgari_v2_nadir": "Nadir temalara ilgi artışı",
    "tema_ruzgari_v3_uzun_nadir": "Nadir temalara uzun vadeli ilgi artışı",
}

RISK = {
    "oynaklik": "Yüksek fiyat oynaklığı",
    "dusus": "Son bir yılın zirvesinden uzaklık",
    "dusuk_fiyat": "Düşük hisse fiyatı",
    "likidite": "Düşük işlem hacmi",
    "yeni": "Bir yıldan kısa süredir işlem görüyor",
    "nakit_suresi": "Nakdin kısa sürede tükenme riski",
    "sulandirma": "Hisse sayısının hızlı artışı (sulandırma)",
    "delist_uyarisi": "Borsadan çıkarma uyarısı aldı",
    "denetci_degisikligi": "Denetçi değişti",
    "geciken_rapor": "Finansal raporu gecikti",
    "devamlilik_suphesi": "Denetçi süreklilik şüphesi bildirdi",
}


def signal(name: str) -> str:
    if name in SIGNALS:
        return SIGNALS[name]
    if name.startswith("8k_"):
        return "8-K bildirimi: " + name.split("_", 2)[2]
    return name

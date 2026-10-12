"""Belirti Haritası raporu, sürüm 2 (iki dış incelemenin önerileri uygulanmış): python -m radar.research.belirti_raporu

Girdiler: reports/research/belirti_testi_2024.json (kilitli dönem hariç, BH-FDR), belirti_testi.json (2013–2025),
belirti_denetimi.csv (doluluk, başlangıç, ikiz), belirti_dogrulama.json, hizli_denemeler.jsonl, izgara_ozet.json,
akış / ilişki görselleri (--gorsel klasörü). Çıktı: reports/research/8_belirti_haritasi_v2.pdf
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from radar import config
from radar.weekly.pdf import ACCENT, Styles, _table

R = config.ROOT / "reports" / "research"
OUT = R / "8_belirti_haritasi_v2.pdf"

GRUP_AD = {"fiyat": "Fiyat", "teknik": "Teknik", "yeni": "Zamanlama/kırılım", "sektor_piyasa": "Sektör ve piyasa",
           "oneriler": "Öneriler", "literatur": "Literatür", "temel": "Temel büyüme", "oranlar": "Finansal oranlar",
           "metin": "10-K metni", "kurumsal_olay": "Kurumsal olay", "haber": "Haber ve gündem", "alternatif": "Alternatif veri"}

KONU = {"yz_teknoloji": "yapay zekâ/teknoloji", "uzay_savunma_devlet": "uzay, savunma, kamu", "inovasyon_patent": "inovasyon/patent",
        "saglik_ilac": "sağlık/ilaç", "enerji_emtia": "enerji/emtia", "kripto": "kripto", "borsa_olaylari": "borsa olayları",
        "ticaret_cin_yaptirim": "ticaret, Çin, yaptırım", "hukuk_sorunu": "hukuki sorun", "finansal_sikinti": "finansal sıkıntı",
        "siber": "siber güvenlik"}

DESC = {
    "momentum_12_1": "Son 12 ayın getirisi (son ay hariç)", "kisa_vade_donus": "Son haftanın getirisinin tersi",
    "dusuk_oynaklik": "Son 26 haftanın düşük fiyat oynaklığı", "kucuk_boyut": "Küçük piyasa değeri (−log)",
    "zirveye_yakinlik_52h": "Fiyatın 52 haftalık zirveye oranı", "getiri_6a": "Son 6 ayın getirisi (son hafta hariç)",
    "getiri_1a": "Son 4 haftanın getirisi", "hacim_artisi": "İşlem tutarının 26 hafta öncesine oranı",
    "fiyat_seviyesi": "Gerçek işlem fiyatı ($)", "beta_qqq": "Nasdaq-100'e göre beta", "likidite": "Günlük işlem tutarı sırası",
    "gelir_buyumesi": "Gelirin geçen yılın aynı dönemine göre büyümesi", "buyume_ivmesi": "Gelir büyümesindeki yıllık değişim",
    "brut_marj_degisimi": "Brüt marjın yıllık değişimi", "faaliyet_marji_degisimi": "Faaliyet marjının yıllık değişimi",
    "arge_yogunlugu": "Ar-Ge gideri ÷ gelir", "serbest_nakit_getirisi": "Serbest nakit akışı ÷ piyasa değeri",
    "kazanc_getirisi": "Net kâr ÷ piyasa değeri (F/K'nın tersi)", "tahakkuklar_dusuk": "Kârın nakitle desteklenmesi (−tahakkuk)",
    "varlik_buyumesi_dusuk": "Düşük varlık büyümesi", "metin_benzerligi_is_tanimi": "10-K iş tanımının geçen yılla benzerliği",
    "metin_benzerligi_riskler": "10-K risk bölümünün geçen yılla benzerliği", "metin_benzerligi_yonetim": "10-K yönetim yorumunun benzerliği",
    "metin_benzerligi_ortalama": "Üç bölümün ortalama benzerliği", "risk_bolumu_buyumesi_dusuk": "Risk bölümünün az uzaması",
    "devamlilik_suphesi": "Denetçinin işletmenin sürekliliği şüphesi", "wiki_ilgi_ivmesi": "Wikipedia görüntülenme artışı",
    "wiki_ani_ilgi": "Wikipedia'da ani ilgi sıçraması", "haber_ivmesi": "Haber sayısındaki artış",
    "haber_ani_artis": "Haber sayısında ani sıçrama", "haber_ton_degisimi": "Haber tonundaki değişim",
    "haber_ton_seviyesi": "Haber tonunun seviyesi", "icerden_alici_sayisi_90g": "90 günde hisse alan yönetici sayısı (yoksa 0)",
    "icerden_alim_kumesi_3plus": "90 günde ≥3 yönetici alımı", "icerden_alim_tutar_piyasa_degeri": "Yönetici alım tutarı ÷ piyasa değeri",
    "ust_yonetici_alimi_90g": "CEO/CFO açık piyasa alımı", "kurumsal_sahip_degisimi": "13F kurumsal sahip sayısı değişimi",
    "kurumsal_hisse_degisimi_payi": "Kurumların tuttuğu hisse değişimi", "8k_1.01_önemli anlaşma": "8-K 1.01: önemli anlaşma (çoğunlukla finansman)",
    "8k_1.02_anlaşma feshi": "8-K 1.02: anlaşma feshi", "8k_2.01_satın alma/elden çıkarma tamamlandı": "8-K 2.01: satın alma/satış tamamlandı",
    "8k_2.03_yeni borç yükümlülüğü": "8-K 2.03: yeni borç", "8k_3.02_kayıtsız hisse satışı (sulandırma)": "8-K 3.02: kayıtsız hisse satışı",
    "8k_5.02_yönetici değişikliği": "8-K 5.02: yönetici değişikliği", "8k_7.01_kamuyu aydınlatma (FD)": "8-K 7.01: kamuyu aydınlatma",
    "8k_8.01_diğer olaylar": "8-K 8.01: diğer olaylar", "geri_alim_getirisi": "Hisse geri alımı ÷ piyasa değeri",
    "tema_ruzgari": "Şirketin temalarının gündemdeki yükselişi", "tema_ruzgari_v1_uzun": "Tema rüzgârı (uzun pencere)",
    "tema_ruzgari_v2_nadir": "Tema rüzgârı (nadir temalar)", "tema_ruzgari_v3_uzun_nadir": "Tema rüzgârı (uzun + nadir)",
    "sektor_getiri_13h": "Sektörün son 13 haftalık getirisi", "sektor_momentum_12_1": "Sektörün 12-1 momentumu",
    "kazanc_aciklamasi_tepkisi": "Son bilanço açıklamasına fiyat tepkisi", "haber_hacmi": "Haber sayısı",
    "haber_hacmi_ivme": "Haber sayısının ivmesi", "yukselen_konu_maruziyeti": "Yükselen gündem konularına maruziyet",
    "yukselen_konuya_yonelis": "Yükselen konulara yöneliş", "bilanco_uzerinden_hafta": "Son bilançodan bu yana geçen hafta",
    "bilanco_bu_ay_bekleniyor": "Bu ay bilanço açıklaması bekleniyor", "sektor_4h": "Sektörün son 4 haftalık getirisi",
    "sektorun_gerisinde": "Sektör getirisi − kendi getirisi", "oynaklik_genislemesi": "Kısa / uzun dönem oynaklık oranı",
    "max_haftalik_4h": "Son 4 haftanın en yüksek haftalık getirisi", "kirilim": "Zirveye yakınlık × hacim artışı",
    "defter_fiyat": "Özsermaye ÷ piyasa değeri", "satis_fiyat": "Gelir ÷ piyasa değeri", "favok_fd": "FAVÖK ÷ firma değeri",
    "temettu_verimi": "Ödenen temettü ÷ piyasa değeri", "nakit_piyasa": "Nakit ÷ piyasa değeri",
    "ozsermaye_karliligi": "Net kâr ÷ özsermaye", "aktif_karliligi": "Net kâr ÷ varlıklar", "brut_kar_aktif": "Brüt kâr ÷ varlıklar",
    "brut_marj": "Brüt kâr ÷ gelir", "faaliyet_marji": "Faaliyet kârı ÷ gelir", "borc_ozsermaye": "Finansal borç ÷ özsermaye",
    "cari_oran": "Dönen varlık ÷ kısa vadeli borç", "faiz_karsilama": "Faaliyet kârı ÷ faiz gideri",
    "altman_z": "Altman Z iflas riski skoru", "piotroski_f": "Piotroski F mali güç skoru (0–9)",
    "kar_buyumesi": "Net kârın yıllık büyümesi", "hisse_sayisi_degisimi": "Hisse sayısının yıllık değişimi (bölünme düzeltilmiş)",
    "rsi_14h": "14 haftalık RSI", "ort_10h_uzaklik": "10 haftalık ortalamaya uzaklık", "ort_40h_uzaklik": "40 haftalık ortalamaya uzaklık",
    "macd": "MACD ÷ fiyat", "bollinger_konum": "Bollinger bandındaki konum", "haber_fiyat_ayrismasi": "Haber ivmesi − fiyat getirisi",
    "reddit_anilma": "Reddit'te anılma sayısı", "reddit_anilma_ivme": "Reddit anılma artışı", "reddit_ofke_payi": "Reddit öfke payı",
    "reddit_olumlu_payi": "Reddit olumlu payı", "reddit_olumsuz_payi": "Reddit olumsuz payı", "reddit_puan": "Reddit gönderi puanı",
    "yukselen_kelime_maruziyeti": "Haberlerde yükselen kelimelere maruziyet", "yukselen_kurum_birlikteligi": "Yükselen kurumlarla birlikte anılma",
    "yeni_kurum_orani": "Haberlerde yeni kurumların payı", "fip_bilgi_surekliligi": "Momentumun küçük adımlarla oluşması (FIP)",
    "max_gunluk_1a": "Son ayın en yüksek günlük getirisi (piyango)", "ivol_3a": "3 aylık artık oynaklık",
    "aktivist_13d": "Son 13 haftada yeni 13D (≥%5 aktif pay bildirimi) var mı", "aktivist_13d_degisiklik": "Son 13 haftadaki 13D/A değişiklik bildirimi sayısı",
    "pasif_13g_yeni": "Son 13 haftada yeni 13G (≥%5 pasif pay)", "gec_rapor_bildirimi": "Son 26 haftada geç rapor bildirimi (NT 10-K/Q)",
    "hisse_ihraci": "Son 13 haftada ihraç belgesi (S-1, S-3, 424B4)", "sektor_ma_dalgasi": "Sektördeki satın alma yoğunluğu",
    "sue_fiyat": "Analistsiz kazanç sürprizi ÷ fiyat", "gelir_surprizi": "Gelir büyümesinin kendi ortalamasından sapması",
    "emsal_getiri_1a": "10-K'sı en benzer 10 şirketin 1 aylık getirisi", "emsal_getiri_3a": "Emsallerin 3 aylık getirisi",
    "emsal_farki_1a": "Emsal getirisi − kendi getirisi", "devralma_olasiligi": "Model: 52 haftada satın alınma olasılığı",
}


def desc(f: str) -> str:
    if f in DESC:
        return DESC[f]
    if f.startswith("haber_"):
        for k, v in KONU.items():
            if f == f"haber_{k}_pay":
                return f"Şirket haberlerinde '{v}' payı"
            if f == f"haber_{k}_ivme":
                return f"'{v}' payının artışı"
            if f == f"haber_{k}_ruzgar":
                return f"'{v}' konusunun gündem rüzgârı"
    return ""


VERI = {"reddit_anilma", "reddit_anilma_ivme", "reddit_ofke_payi", "reddit_olumlu_payi", "reddit_olumsuz_payi", "reddit_puan",
        "wiki_ani_ilgi", "wiki_ilgi_ivmesi", "haber_ani_artis", "likidite", "hacim_artisi", "kirilim"}
BOLUNME = {"kazanc_getirisi", "defter_fiyat", "satis_fiyat", "favok_fd", "temettu_verimi", "nakit_piyasa", "kucuk_boyut",
           "hisse_sayisi_degisimi", "piotroski_f", "altman_z", "serbest_nakit_getirisi", "geri_alim_getirisi",
           "icerden_alim_tutar_piyasa_degeri", "devralma_olasiligi"}
EKSIK_KALEM = {"temettu_verimi", "favok_fd", "faiz_karsilama", "ozsermaye_karliligi", "defter_fiyat", "borc_ozsermaye"}
KOPYA = {"sektorun_gerisinde": "getiri_1a", "aktif_karliligi": "ozsermaye_karliligi", "ort_40h_uzaklik": "macd"}
TERS = {"aktivist_13d", "aktivist_13d_degisiklik", "icerden_alici_sayisi_90g", "icerden_alim_kumesi_3plus",
        "icerden_alim_tutar_piyasa_degeri", "ust_yonetici_alimi_90g", "tahakkuklar_dusuk", "arge_yogunlugu", "sue_fiyat",
        "borc_ozsermaye", "kurumsal_hisse_degisimi_payi", "kisa_vade_donus", "varlik_buyumesi_dusuk"}


def classify(r: pd.Series) -> str:
    if r.belirti in VERI:
        return "Veri sorunu"
    if r.belirti in KOPYA:
        return "Kopya"
    if r.kesin:
        return "Fırsat belirtisi" if r.ic > 0 else "Risk belirtisi (eleme)"
    if r.q < 0.10 or abs(r.t) >= 2:
        return "Zayıf"
    return "Etkisiz"


def load() -> pd.DataFrame:
    lock = pd.DataFrame(json.loads((R / "belirti_testi_2024.json").read_text())["3ay"])
    six = pd.DataFrame(json.loads((R / "belirti_testi_2024.json").read_text())["6ay"]).set_index("belirti")
    a = pd.read_csv(R / "belirti_denetimi.csv").set_index("belirti")
    df = lock.set_index("belirti").join(six[["ic", "t", "q"]].add_suffix("_6"), how="left").join(a[["grup", "dolu", "baslangic"]], how="left")
    df = df.reset_index()
    df["durum"] = df.apply(classify, axis=1)
    flags = []
    for f in df.belirti:
        fl = []
        if f in BOLUNME:
            fl.append("bölünme hatası etkiliyordu (düzeltildi)")
        if f in EKSIK_KALEM:
            fl.append("eksik XBRL kalemi (indirildi)")
        if f in TERS:
            fl.append("literatürle ters yön")
        if f in KOPYA:
            fl.append(f"{KOPYA[f]} ile r ≥ 0,9")
        flags.append("; ".join(fl))
    df["not"] = flags
    return df


def pc(v: float, d: int = 1) -> str:
    s = f"{abs(v) * 100:.{d}f}".replace(".", ",")
    return ("+%" if v >= 0 else "−%") + s


def para(st, text, style=None):
    return Paragraph(text, style or st.body)


def build(img_dir: Path) -> Path:
    st = Styles()
    df = load()
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.3 * cm, rightMargin=1.3 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.2 * cm, title="Fırsat Radarı — Belirti Haritası (sürüm 2)")
    W = landscape(A4)[0] - 2.6 * cm
    E = []
    counts = df.durum.value_counts()
    trials = [json.loads(line) for line in (R / "hizli_denemeler.jsonl").read_text().splitlines() if line.strip()]
    t5 = next(t for t in reversed(trials) if t["deneme"] == "t5_temiz")
    t20 = next(t for t in reversed(trials) if t["deneme"] == "t5_k20_temiz")
    grid = json.loads((R / "izgara_ozet.json").read_text())

    # 1. Kapak ve karar
    E += [para(st, "Fırsat Radarı — Belirti Haritası (sürüm 2)", st.h1),
          para(st, "İki dış incelemenin önerileri uygulanmış sürüm · 12 Ekim 2026 · Evren: ABD borsalarında ≥1 $ fiyatlı, finans dışı "
                   "faaliyet şirketleri (banka, sigorta, GYO, fon, SPAC hariç) · 2010–2026", st.small), Spacer(1, 6),
          para(st, "Karar özeti", st.h2)]
    karar = [
        "<b>%26 doğrulanmış bir sonuç değildir.</b> Önceden sabitlenmiş tek bir ayar (3 ay tutma, 10 hisse, sıra hedefi) görmediği "
        f"yıllarda (2013–2025) net {pc(t5['net_yillik_ort'], 0)}/yıl verdi; S&amp;P 500 +%15,4. Ama bu ayar birçok denemeden "
        f"sonra seçildi. Her yıl yalnızca geçmiş yıllara bakarak ayar seçilince (64 ayar, 3 tohum) sonuç "
        f"<b>{pc(grid['meta_secim']['ort'])}/yıl</b>, S&amp;P {pc(grid['meta_secim']['spy_ort'])}: S&amp;P'den farksız.",
        "<b>Sonuçlar yeniden ölçülecek.</b> Doğrulama turunda hisse bölünmelerinden sonra piyasa değerinin 2–3 ay boyunca bölünme "
        "oranı kadar küçük hesaplandığı bulundu (NVDA 2024: 2.979 mr $ yerine 304 mr $). Değerleme belirtileri bundan etkileniyordu. "
        "Hata düzeltildi; bu rapordaki belirti ölçümleri düzeltme öncesi çerçeveden gelir ve tabloda işaretlidir.",
        "<b>Sızıntı yok.</b> 148 belirtinin 148'i gelecek bilgisi testinden geçti; SEC'e kabul anından önce hiçbir bilgi görünmüyor.",
        "<b>Kilitli son dönem (yarı temiz).</b> 2025–2026 kilitlendi; belirti testi ve bundan sonraki her seçim yalnızca 2013–2024 ile "
        "yapılır. Ancak 2025 sonuçları önceki denemelerde görüldü ve ön kayıttaki son dönem (Temmuz 2025 →) 4. aşamada bir kez kullanıldı. "
        "Bu yüzden tamamen temiz tek test, Ekim 2026'dan itibaren kaydedilen canlı seçimlerin takibidir.",
        "<b>Çoklu test düzeltmesi uygulandı.</b> Benjamini–Hochberg düzeltmesinden sonra da kesin kalan belirti sayısı: "
        f"{int((df.durum.str.startswith(('Fırsat', 'Risk'))).sum())} / {len(df)} (q &lt; 0,05, |t| ≥ 3, yılların ≥ %70'inde aynı yön).",
    ]
    for k in karar:
        E += [para(st, "• " + k), Spacer(1, 3)]
    E += [Spacer(1, 6), para(st, "Belirti durumları (3 ay ufuk, 2013–2024)", st.h3)]
    order = ["Fırsat belirtisi", "Risk belirtisi (eleme)", "Zayıf", "Etkisiz", "Veri sorunu", "Kopya"]
    E.append(_table(st, [["Durum", "Sayı", "Anlamı"]] + [[o, int(counts.get(o, 0)), para(st, m, st.cell)] for o, m in zip(order, [
        "Yüksek değer daha yüksek getiriyle ilişkili; kesin", "Yüksek değer daha düşük getiriyle ilişkili; kötü adayları elemek için",
        "Kesin değil ama sınırda (q < 0,10 ya da |t| ≥ 2)", "Anlamlı etki yok", "Canlıda üretilemiyor ya da veri eksik",
        "Başka bir belirtiyle r ≥ 0,9"])], [5 * cm, 2 * cm, W - 7 * cm]))
    E.append(PageBreak())

    # 1b. Hedef
    E += [para(st, "Proje hedefi ve başarı ölçütleri", st.h1)]
    hedef = [
        ("Amaç", "ABD borsalarında (Nasdaq, NYSE, NYSE American) işlem gören faaliyet şirketleri arasından geleceğin büyük kazananlarını, "
                 "yükselişleri başlamadan önce bulmak. Örnek: yapay zekâ döneminin başında NVDA, kamu sözleşmeleriyle PLTR; tersi için Çin "
                 "pazarında gerileyen otomotiv şirketleri."),
        ("Nicel hedef", "Görmediği yıllarda S&P 500'ün 3 katı yıllık getiri. 2013–2025'te S&P ortalaması +%15,4 → hedef ≈ +%46/yıl, "
                        "işlem maliyeti düşüldükten sonra."),
        ("İlk hedef (vazgeçildi)", "Geriye bakış 'en yüksek kâr' raporundaki (Rapor 4) oranları %10 toleransla tutturmak. Rapor 4 her yılın "
                                   "gerçekleşmiş kazananlarını sonradan seçtiği için ulaşılabilir bir hedef değil, bir tavan; S&P×3 hedefine geçildi."),
        ("Yöntem ilkesi", "Ezber yok: her sonuç yalnızca modelin eğitimde görmediği verilerle ölçülür. Amaç belirtileri, oranlarını ve "
                          "parametrelerini doğru bulmak; geçmişi açıklamak değil."),
        ("Kapsam", "Banka, sigorta, GYO, fon/BDC, SPAC ve eğitim şirketleri (SIC 611x) hariç; HOOD, COIN gibi aracı/borsa şirketleri dahil. "
                   "Borsadan çıkan şirketler dahil (hayatta kalma yanlılığı yok)."),
        ("Ufuk ve çözünürlük", "Aylık karar; 1, 3, 6, 12 ve 24 aylık tutma süreleri test edilir (haftalık çok kısa bulundu)."),
        ("Bilgi kaynakları", "Fiyat, finansal tablolar, SEC belgeleri ve haberler. Haberler kritik: daha önce hiç görülmemiş konuların "
                             "yükselişini yakalayabilmek gerekir. Alışılmadık belirtiler de denenir (ör. sosyal medyada bir hisse "
                             "hakkındaki öfke yoğunluğu)."),
    ]
    E.append(_table(st, [["Konu", "Açıklama"]] + [[a, para(st, b, st.cell)] for a, b in hedef], [4 * cm, W - 4 * cm]))
    E += [Spacer(1, 8), para(st, "Ön kayıtlı başarı ölçütleri (10 Ekim 2026, sonuçlara bakılmadan yazıldı)", st.h3)]
    olcut = [["Ölçüt", "Tanım", "Bugünkü durum"],
             ["Getiri hedefi", "Görmediği yıllarda net yıllık getiri ≥ S&P × 3 (≈ +%46)", "Ulaşılmadı: dürüst seçimle +%15,6, tek ayarla +%26"],
             ["Büyük kazanan oranı", "Puanı en yüksek %10'da +%100 kazananların oranı ≥ genel oranın 1,5 katı; bootstrap %90 alt sınır > 1",
              "Belirti düzeyinde ölçülüyor (kazanan katı); model düzeyinde yeniden ölçülecek"],
             ["Basit kıyas", "Aynı oran, yalnızca 'en yüksek oynaklık' ile seçilen %10'dan yüksek olmalı", "Ölçülecek"],
             ["Portföy", "İlk %10 eşit ağırlıklı portföy, maliyet sonrası, evrenin eşit ağırlıklı portföyünden düşük olmamalı", "Ölçülecek"],
             ["Sızıntı", "Hiçbir belirti, açıklandığı andan önce görünmemeli", "Sağlandı: 148/148"]]
    E.append(_table(st, [[para(st, c, st.cell) for c in row] if i else row for i, row in enumerate(olcut)], [4 * cm, 13 * cm, W - 17 * cm]))
    E.append(PageBreak())

    # 2. Yöntem
    E += [para(st, "Yöntem: sayılar nasıl hesaplandı", st.h1)]
    yontem = [
        ("Zamanlama", "Her ayın ilk Cuması, o gün kamuya açık olan bilgiyle. SEC belgeleri kabul anından sonraki ilk Cuma görünür "
                      "(Cuma 16:00 sonrası kabul → bir sonraki Cuma). Finansal tablolar dönem sonuyla değil kabul tarihiyle, en fazla 400 gün taşınır."),
        ("Hedef ve IC", "Sonraki 3 (ve 6) ayın getirisi. IC: belirtinin yüzdelik sırası ile getiri sırası arasındaki korelasyon, her ay ayrı."),
        ("t değeri", "Aylık IC'lerin ortalaması ÷ standart hata; ufuklar çakışmasın diye yalnızca her 3. (6 ayda her 6.) ayın IC'si kullanılır. "
                     "Her ay tüm hisselerin tek bir IC'si alındığı için aynı şirketin tekrarlayan gözlemleri t'yi şişirmez."),
        ("Çoklu test", "t'den p değeri, 145 belirti üzerinde Benjamini–Hochberg q değeri. Kesin: q < 0,05, |t| ≥ 3, yıl tutarlılığı ≥ %70."),
        ("Kazanan katı", "Belirtinin en yüksek %20'lik diliminde, ufkun en iyi %5'ine giren hisse oranı ÷ %5 (1 = rastgele). "
                         "Büyük kazananı bulma gücünü ortalama getiriden ayrı ölçer."),
        ("Model", "LightGBM, hedef 3 aylık getiri sırası, her test yılı için yalnızca o yıldan önce getirisi gerçekleşmiş son 5 yılla eğitilir; "
                  "5 farklı tohumun ortalaması. Tüm belirtiler kullanılır; belirti seçimi yapılmaz."),
        ("Portföy", "Her çeyrek başı en yüksek puanlı 10 hisse, eşit ağırlık, 3 ay tutulur."),
        ("Maliyet", "Tek yön: günlük işlem ≥ 50 M$ %0,05; ≥ 10 M$ %0,15; ≥ 1 M$ %0,40; altı ya da bilinmiyor %1,0. "
                    "Yalnızca değişen hisseler için alınır (devir tabanlı). 10 hisse brüt +%27 → net +%26: yılda ~1 puan."),
        ("Borsadan çıkanlar", "Satın alma vb. çıkışta son geçerli fiyat, iflasta 0. Çıkan hisselerin %92'sinin fiyatı seyrek SEC FTD kayıtlarından "
                              "geliyor; işlem tutarı bu yüzden satırların %33'ünde boş (bilinmeyen = sıfır sayılmaz, en yüksek maliyet uygulanır)."),
        ("Ayar seçimi", "Ayarlar (tutma süresi, hisse sayısı, hedef, pencere) tüm yıllara bakılarak seçildi; seçim yanlılığı buradan gelir. "
                        "Dürüst ölçü: her yıl yalnızca önceki yıllarda en iyi olan ayarı uygulamak (meta yürüyen test)."),
    ]
    E.append(_table(st, [["Konu", "Açıklama"]] + [[a, para(st, b, st.cell)] for a, b in yontem], [4 * cm, W - 4 * cm], zebra=True))
    E.append(PageBreak())

    # 3. Performans
    E += [para(st, "Performans: neyin kanıtlandığı, neyin kanıtlanmadığı", st.h1)]
    yrs = t5["yillar"]
    perf = [["", "Getiri/yıl", "Not"],
            ["Tek ayar, 10 hisse (önceden sabit)", pc(t5['net_yillik_ort']), f"zararlı yıl {t5['zararli_yil']}/{len(yrs)}; seçim yanlılığı içerir"],
            ["Tek ayar, 20 hisse", pc(t20['net_yillik_ort']), f"zararlı yıl {t20['zararli_yil']}/{len(yrs)}"],
            ["Geriye bakınca en iyi ayar (64 içinden)", pc(grid['geriye_bakinca_en_iyi']['ort']), "iyimser; yalnızca bilgi için"],
            ["Dürüst ayar seçimi (meta yürüyen test)", pc(grid['meta_secim']['ort']),
             f"S&P'yi {grid['meta_secim']['spyi_gecen_yil']}/{grid['meta_secim']['yil']} yılda geçiyor"],
            ["Eşit ağırlıklı belirti toplamı (kıyas)", "+%4 ile +%15", "ağırlık taramasındaki eşit varyant; resmî kıyas bekliyor"],
            ["S&P 500", pc(grid['meta_secim']['spy_ort']), "aynı yıllar"],
            ["Hedef (S&P × 3)", "+%46", "ulaşılmadı"]]
    E.append(_table(st, perf, [8 * cm, 3 * cm, W - 11 * cm]))
    E += [Spacer(1, 6), para(st, "Tek ayar (10 hisse) yıl yıl net getiri", st.h3)]
    E.append(_table(st, [[str(y) for y in yrs], [pc(v, 0) for v in t5["yil_yil_net"]]], [W / len(yrs)] * len(yrs), zebra=False))
    E += [Spacer(1, 8), para(st, "Henüz ölçülmeyenler (iş planında)", st.h3),
          para(st, "En kötü düşüş, Sharpe, kazançlı dönem oranı, devir hızı, maliyet ×2 stres testi, likit evren (≥ 1 M$ ve ≥ 10 M$) sonuçları, "
                   "kapasite, faktör regresyonu (boyut, değer, momentum, kârlılık, yatırım) ve alfa, resmî eşit ağırlıklı kıyas. "
                   "Kod yazıldı; bölünme düzeltmeli çerçeveyle koşulacak.")]
    E.append(PageBreak())

    # 4. Doğrulama
    E += [para(st, "Belirti doğrulama sonuçları", st.h1)]
    dog = [["Test", "Sonuç", "Açıklama"],
           ["Sızıntı (gelecek bilgisi)", "148/148 geçti", "Belirtinin sonraki haftayla IC'si, ondan sonraki haftaya göre olağan dışı yüksek değil"],
           ["Zamanlama", "6/6 geçti", "Yapay olaylar: değer kabul anından sonraki ilk Cuma'dan önce görünmüyor"],
           ["Yön", "4/4 geçti", "'düşük', 'küçük' adlı belirtiler ölçüyle doğru yönde"],
           ["Bağımsız yeniden hesap", "6/6 geçti", "Fiyat belirtileri günlük fiyattan ayrı formülle; fiyat_seviyesi farkı testin kendi hatası "
                                                   "(Yahoo kapanışı bölünme düzeltmeli), bölünmesiz 3.899 hissede birebir aynı"],
           ["Bilinen değerler", "AAPL, MSFT, XOM geçti", "F/K, brüt ve faaliyet marjı, cari oran, piyasa değeri kamuya açık rakamlarla ±%3"],
           ["Bölünme", "5/6 kaldı → düzeltildi, 6/6", "Hisse sayısı rapordan sonraki bölünmeye göre düzeltiliyor; bölünmesiz hisselerde değişiklik yok"],
           ["Eksik hisse sayısı", "808 şirket → düzeltildi", "Dolaşımdaki sayıyı vermeyenlerde (ör. KO) ağırlıklı ortalama hisse sayısı"],
           ["Eksik finansal kalemler", "4 kalem → indirildi", "Temettü (XOM tipi), azınlık paylı özsermaye, iki amortisman kalemi; ayrıca faiz gideri kalemleri"],
           ["Tutarlılık (çerçeve ↔ kaynak)", "yeniden koşulacak", "Düzeltme sırasında kod karıştığı için tamamlanamadı"]]
    E.append(_table(st, [[para(st, str(c), st.cell) for c in row] if i else row for i, row in enumerate(dog)], [5 * cm, 4.5 * cm, W - 9.5 * cm]))
    E.append(PageBreak())

    # 4b. İncelemeciler için ayrıntılar
    E += [para(st, "İncelemeciler için ayrıntılar", st.h1), para(st, "Veri kaynakları", st.h2)]
    kaynak = [["Kaynak", "İçerik", "Dönem", "Zaman damgası", "Bilinen sorun"],
              ["Yahoo günlük fiyat", "Kapanış, düzeltilmiş kapanış, hacim, bölünme", "2009 →", "işlem günü", "Borsadan çıkmışların çoğu yok"],
              ["SEC fails-to-deliver", "Borsadan çıkmışların seyrek fiyatı, CUSIP eşleşmesi", "2009 →", "takas günü − 1", "Seyrek; hacim yok"],
              ["SEC finansal tablo veri setleri", "XBRL; 60 kalem", "2009 Q3 →", "SEC kabul anı", "2009 ilk yarı neredeyse boş"],
              ["SEC belge listesi", "8-K maddeleri, 13D/13G, NT 10-K/Q, S-1/S-3, Form 25/15", "tamamı", "kabul anı", "—"],
              ["SEC Form 3/4/5", "İçeriden işlemler", "2009 →", "kabul anı", "—"],
              ["SEC 13F", "Kurumsal pozisyonlar", "2013 Q3 – 2023 Q4", "dönem sonu + 46 gün", "2024 sonrası bölümler eksik"],
              ["10-K metinleri", "Madde 1, 1A, 7", "2008 →", "kabul anı", "—"],
              ["GDELT", "Haber konuları, ton, kurum, tema", "2015 →", "yayın günü (ay bitince)", "2015 öncesi yok"],
              ["Wikipedia", "Günlük görüntülenme", "2015-07 →", "gün", "Az şirket eşleşiyor"],
              ["Reddit arşivi", "6 alt forum, yalnızca toplamlar", "→ 2024 ortası", "gönderi zamanı", "Güncel veri yok"],
              ["Bilanço bültenleri", "8-K 2.02 ekleri, metin özellikleri", "2009 →", "kabul anı", "Henüz modelde değil"],
              ["FINRA açığa satış", "Ay × sembol açığa satış hacmi", "2009-08 →", "ay sonu", "Henüz modelde değil"],
              ["FRED", "Makro seriler", "uzun", "yayın", "Kullanılmıyor (yalnızca risksiz faiz)"]]
    E.append(_table(st, [[para(st, c, st.cell) for c in row] if i else row for i, row in enumerate(kaynak)],
                    [4.5 * cm, 6.5 * cm, 3.5 * cm, 4 * cm, W - 18.5 * cm]))
    E += [para(st, "Evren, panel ve model ayarları", st.h2)]
    ayar = [
        ("Panel", "Haftalık (Cuma kapanışı). Gerçek işlem fiyatı bölünmelerden arındırılır. Holding yeniden yapılanmaları ve aynı şirketin "
                  "sembol değişiklikleri birleştirilir. Borsadan çıkışta son geçerli fiyat, iflasta (8-K 1.03) 0."),
        ("Evren", "Ay başında fiyat ≥ 1 $ ve (işlem tutarı bilinmiyorsa dahil) günlük işlem ≥ 1 M$; ayda ~2.700 hisse, 201 ay, ~580 bin satır. "
                  "Önceki sürüm ≥ 5 $ idi; 1 $'a inince yıllık getiri +%20'den +%25'e çıktı (son yıllarda büyük kazananların %20–30'u 5 $ altındaydı)."),
        ("Belirti biçimi", "Her belirti her ay kendi içinde yüzdelik sıraya çevrilir (aykırı değer etkisi yok). Olaylar 0/1. Eksik değer boş bırakılır."),
        ("Model", "LightGBM regresyon; hedef: 3 aylık getirinin ay içi sırası. 200 ağaç, öğrenme hızı 0,05, 31 yaprak, yaprak başına en az 400 "
                  "gözlem, belirti örnekleme %60, satır örnekleme %70, L2 cezası 10. Eğitim: test yılından önceki 5 yıl, son 13 hafta boşluk. "
                  "5 tohumun sıra ortalaması (tek koşunun rastgeleliği ±5 puan/yıl)."),
        ("Temiz belirti seti", "Reddit (6), wiki_ani_ilgi, haber_ani_artis ve 3 kopya modelden çıkarıldı; içeriden alım yoksa 0."),
    ]
    E.append(_table(st, [["Konu", "Açıklama"]] + [[a, para(st, b, st.cell)] for a, b in ayar], [4 * cm, W - 4 * cm]))
    E.append(PageBreak())
    E += [para(st, "Denenenler ve sonuçları (görmediği yıllar)", st.h2)]
    deneme = [["Deneme", "Sonuç", "Karar"],
              ["Sürüm 3: istikrarlı işaretler + ridge (yıllık)", "S&P × 1,1–1,5", "Donduruldu, temel alındı"],
              ["Aylık çerçeve + LightGBM, 3 ay, 10 hisse", "+%20 (≥5 $) → +%25–29 (≥1 $)", "Ana model"],
              ["6 ay tutma", "+%13–14", "S&P altında"],
              ["Ayar ızgarası (64 ayar, meta seçim)", "Geriye bakınca +%37, dürüst +%15,6", "Ayar aramak kazandırmıyor"],
              ["Evrimsel doğrusal ağırlık taraması", "+%10–28, 2–5 zararlı yıl", "Ağaç modelinden daha oynak"],
              ["Büyük kazanan hedefi (en iyi %5)", "+%1–7", "Daha kötü"],
              ["Lambdarank (ilk sıraları optimize)", "+%6–14", "Daha kötü; piyango hisselerine yöneliyor"],
              ["Piyasa rejimi kapısı", "İyileştirme yok", "Reddedildi"],
              ["Haber (GDELT) ve alternatif veri", "≈ +3 puan", "Tutuldu (Reddit hariç)"],
              ["Finansal oranlar ve teknik göstergeler", "≈ +8 puan", "Tutuldu"],
              ["Literatür belirtileri (MAX, IVOL, 13D, ihraç...)", "Gürültü bandında", "Tutuldu (risk belirtileri)"],
              ["Emsal momentumu, devralma olasılığı", "Gürültü bandında (±4)", "Tutuldu"],
              ["main dalındaki 'trend + düzeltme' kuralı", "2010–2026'da başarısız", "Kullanılmıyor"],
              ["Kâhin testi (düzeneğin kontrolü)", "IC 0,12 → ≈ +%45; IC 0,06 → ≈ +%25", "Düzenek doğru; S&P×3 için IC ≈ 0,12 gerekli"],
              ["Puan dilimi profili", "En kötü dilim −%2,4, en iyi +%1,3 / çeyrek", "Model tek yönlü ama zayıf; gücü daha çok kötüleri ayırmakta"]]
    E.append(_table(st, [[para(st, c, st.cell) for c in row] if i else row for i, row in enumerate(deneme)], [9 * cm, 7 * cm, W - 16 * cm]))
    E += [para(st, "Bilinen sınırlamalar", st.h2)]
    sinir = [
        "Kilitli dönem yarı temiz: 2025 sonuçları görüldü; tek temiz test canlı takip.",
        "Deneme sayısı yüksek: belirti düzeyinde FDR uygulandı, ama ayar ve model düzeyinde yüzlerce deneme yapıldı; dürüst ölçü meta seçimdir.",
        "Borsadan çıkmış hisselerin %92'sinin fiyatı seyrek FTD kayıtlarından; bu satırlarda işlem tutarı yok (satırların %33'ü, 2010'da %57).",
        "Maliyet modeli işlem tutarına göre kademeli; düşük fiyatlı hisselerde alış-satış farkı daha yüksek olabilir (×2 stres testi bekliyor).",
        "Bölünme hatası ve eksik finansal kalemler düzeltildi ama düzeltilmiş veriyle sonuçlar henüz ölçülmedi.",
        "Analist beklentisi verisi yok (kazanç sürprizi analistsiz ölçülüyor).",
        "Yalnızca uzun pozisyon; açığa satış ya da kaldıraç yok. Vergi düşülmedi.",
    ]
    for x in sinir:
        E.append(para(st, "• " + x))
    E += [para(st, "Yeniden üretme", st.h2),
          para(st, "Depo: github.com/dalkilicetin/firsat-radari-v2, dal claude/firsat-modeli. Veri: GitHub Releases + manifest (sha256). "
                   "Çerçeve: RADAR_MIN_PRICE=1 python -m radar.research.monthly, ardından alt_signals, yeni_belirtiler, oneriler emsal,devralma. "
                   "Belirti testi: python -m radar.research.belirti_testi --son=2024. Model: python -m radar.research.hizli 3ay t5_temiz. "
                   "Doğrulama: python -m radar.research.belirti_dogrulama. Denetim: python -m radar.research.denetim --son=2024."),
          para(st, "İncelemecilere sorular", st.h2)]
    for x in ["S&P×3 hedefi bu evren ve veriyle gerçekçi mi; değilse hangi ara hedefi önerirsiniz?",
              "Kilitli dönem yarı temiz; canlı takip dışında güvenilir bir son test önerisi var mı?",
              "Model gücünü daha çok kötü hisseleri ayırarak kazanıyor. Büyük kazananı bulmak için hangi belirti ya da hedef tanımını önerirsiniz?",
              "Borsadan çıkmış hisselerin fiyatı için ücretli kaynak (ör. EODHD) gerekli mi, yoksa FTD + çıkış değeri yeterli mi?",
              "Ücretsiz ve zaman damgalı geçmişi olan, henüz kullanmadığımız bir veri kaynağı biliyor musunuz?"]:
        E.append(para(st, "• " + x))
    E.append(PageBreak())

    # 5. Akış ve ilişki
    for title, fn, cap in (("Veri nereden geliyor, nereye gidiyor", "rapor_akis.png",
                            "Kutuların altındaki çubuk, gruptaki belirtilerin ilk denetim sonucudur. Kırmızı: Reddit arşivi 2024 ortasında bitiyor. "
                            "Kesikli: bilanço bülteni ve FINRA açığa satış verisi indirildi, henüz modelde değil."),
                           ("Belirtiler arasındaki ilişki", "rapor_cember.png",
                            "Çember: sıra korelasyonu |r| ≥ 0,6 olan çiftler (bu eşik yalnızca çizim içindir, modeli etkilemez)."),
                           ("Grup içi ve gruplar arası ortalama |r|", "rapor_isi.png",
                            "Teknik grup kendi içinde 0,71: çoğu aynı bilgiyi taşıyor. Haber, metin ve kurumsal olay grupları diğerlerinden neredeyse bağımsız.")):
        p = img_dir / fn
        if p.exists():
            from reportlab.lib.utils import ImageReader
            iw, ih = ImageReader(str(p)).getSize()
            h = min(15.5 * cm, W * ih / iw)
            E += [para(st, title, st.h1), Image(str(p), width=h * iw / ih, height=h), Spacer(1, 4), para(st, cap, st.small), PageBreak()]

    # 6. Tüm belirtiler
    E += [para(st, "Tüm belirtiler (3 ay ufuk, 2013–2024; kilitli dönem hariç)", st.h1),
          para(st, "Sütunlar: IC ve t 3 ay ufuk; q Benjamini–Hochberg düzeltilmiş; Tutarlılık = aynı yönde çıkan yılların payı; "
                   "IC 6a = 6 ay ufuk; Kazanan katı = en yüksek %20'lik dilimde ufkun en iyi %5'inden kaç kat fazla hisse (1 = rastgele); "
                   "Dolu = değeri olan satır payı.", st.small), Spacer(1, 4)]
    hdr = ["Belirti", "Ne ölçer", "Grup", "Durum", "IC", "t", "q", "Tutarl.", "IC 6a", "Kaz. katı", "Dolu", "Not"]
    widths = [4.6 * cm, 5.6 * cm, 2.4 * cm, 2.6 * cm, 1.1 * cm, 1.0 * cm, 1.1 * cm, 1.2 * cm, 1.1 * cm, 1.5 * cm, 1.1 * cm]
    widths.append(W - sum(widths))
    gorder = list(GRUP_AD)
    df["_g"] = df.grup.map(lambda g: gorder.index(g) if g in gorder else 99)
    rows = [hdr]
    for _, r in df.sort_values(["_g", "t"], key=lambda s: s if s.name == "_g" else -s.abs()).iterrows():
        f = lambda v, d=3: "–" if pd.isna(v) else f"{v:.{d}f}".replace(".", ",")
        rows.append([para(st, r.belirti, st.cell), para(st, desc(r.belirti), st.cell), GRUP_AD.get(r.grup, r.grup or ""),
                     para(st, r.durum, st.cell), f(r.ic), f(r.t, 1), f(r.q, 3), "–" if pd.isna(r.tutarlilik) else f"%{r.tutarlilik * 100:.0f}",
                     f(r.ic_6), f(r.ust_dilim_kat, 2), "–" if pd.isna(r.dolu) else f"%{r.dolu * 100:.0f}", para(st, r["not"], st.cell)])
    t = _table(st, rows, widths)
    colmap = {"Fırsat belirtisi": "#d9efe0", "Risk belirtisi (eleme)": "#fbe3cf", "Veri sorunu": "#f6d3d0", "Kopya": "#e6dcf3"}
    extra = []
    for i, row in enumerate(rows[1:], start=1):
        c = colmap.get(df.sort_values(["_g", "t"], key=lambda s: s if s.name == "_g" else -s.abs()).iloc[i - 1].durum)
        if c:
            extra.append(("BACKGROUND", (3, i), (3, i), colors.HexColor(c)))
    t.setStyle(TableStyle(extra))
    E += [t, PageBreak()]

    # 7. İncelemelere yanıt
    E += [para(st, "Dış incelemelere yanıt", st.h1)]
    yan = [
        ["Öneri", "Karar", "Durum"],
        ["Çoklu test düzeltmesi (FDR)", "Katılıyorum", "Uygulandı: bu raporda q sütunu ve kesin ölçütü"],
        ["Bağımsız / dokunulmamış son test dönemi", "Katılıyorum", "Uygulandı: 2025–2026 kilitli; tüm seçimler 2013–2024"],
        ["%26 doğrulanmış sayılmamalı", "Katılıyorum", "Dürüst ayar seçimi +%15,6; bölünme düzeltmesiyle yeniden ölçülecek"],
        ["Sızıntı testi", "Katılıyorum", "Yapıldı: 148/148 temiz"],
        ["Risk raporu (düşüş, Sharpe, devir, yoğunlaşma, rejimler)", "Katılıyorum", "Kod hazır, koşulacak"],
        ["Maliyet ayrımı ve ×2 stres testi", "Katılıyorum", "Brüt/net var (~1 puan/yıl); stres testi kod hazır"],
        ["Teorik / likit / uygulanabilir performans, kapasite", "Katılıyorum", "Kod hazır, koşulacak"],
        ["Faktör maruziyeti (Fama-French tipi)", "Katılıyorum", "Kod hazır: faktörler çerçeveden kuruluyor"],
        ["Eşit ağırlıklı kıyas modeli", "Katılıyorum", "Kod hazır; ağırlık taramasında +%4–15 bulunmuştu"],
        ["Fırsat ve risk belirtilerini ayırmak", "Katılıyorum", "Uygulandı: durum sütunu"],
        ["Seviye / değişim / sürpriz ayrımı", "Katılıyorum", "15 yeni belirti yazıldı (kârlılık, marj, nakit, kazanç)"],
        ["Sıkışma, hacim daralması, kırılım dayanıklılığı", "Katılıyorum", "5 yeni belirti yazıldı"],
        ["Kopyalarda ek bilgi testi", "Katılıyorum", "Kod hazır (ikizinden arındırılmış IC)"],
        ["Reddit/Wikipedia canlıdan çıkarılsın", "Katılıyorum", "Uygulandı: temiz belirti setinde yok"],
        ["Ad düzeltmeleri (8-K 1.01, 13D/13D-A farkı)", "Katılıyorum", "Bu raporda açıklamalar düzeltildi"],
        ["Büyük kazanan için ayrı model (Model B)", "Kısmen", "Denendi: en iyi %5 hedefi +%1–7, lambdarank +%6–14; ölçü olarak kazanan katı kullanılıyor"],
        ["Düşük IC ile %26 sızıntı şüphesi", "Katılmıyorum", "Sızıntı testi temiz; IC ≈ 0,06 kâhin testinde ≈ +%25'e karşılık geliyor"],
        ["%26, seçilmiş 38 belirtiyle mi?", "Katılmıyorum", "Model tüm belirtileri kullanır; yanlılık ayar seçiminden gelir"],
        ["Sayfa 11'de Azerbaycan Türkçesi / bozuk metin", "Kaynak bizde değil", "PDF'e çevirirken tarayıcı çevirisinden; bu sürüm doğrudan PDF"],
        ["Teknik grubu 5–6 belirtiye indir", "Kısmen", "Ağaç modeli bundan az etkilenir; ek bilgi testiyle karar verilecek"],
        ["Analist beklentileri, iş ilanları", "Veri yok", "Zaman damgalı geçmiş verisi ücretli; karar kullanıcıda"],
    ]
    E.append(_table(st, [[para(st, c, st.cell) for c in row] if i else row for i, row in enumerate(yan)], [9 * cm, 3 * cm, W - 12 * cm]))
    E.append(PageBreak())

    # 8. Plan
    E += [para(st, "Önerilen iş planı (onay bekliyor)", st.h1)]
    plan = [
        ["Sıra", "İş", "Neden"],
        ["1", "Bölünme düzeltmeli ve yeni kalemli çerçeveyi kurmak; doğrulama paketini baştan koşmak", "Mevcut sayılar hatalı veriyle"],
        ["2", "Belirti testi (FDR, 2013–2024) ve modelin yeniden ölçümü", "Düzeltmenin etkisini görmek"],
        ["3", "Risk, maliyet ×2, likit evren, kapasite, faktör ve alfa, eşit ağırlıklı kıyas", "İki incelemenin ortak talebi"],
        ["4", "Yeni belirtilerin (seviye/değişim/sürpriz, sıkışma) ve kopyaların ek bilgi testi", "Yalnızca bilgi katıyorsa eklenir"],
        ["5", "Belirti başına tam tarama (~9.500 kural), dürüst seçimle", "Kullanıcı isteği"],
        ["6", "Tek bir model ve ayar seçimi (yalnızca 2013–2024 ile), sonra kilitli 2025–2026'da bir kez test", "Gerçek başarı ölçüsü"],
        ["Karar", "Çıkmış hisselerin günlük fiyatı için ücretli kaynak (EODHD ~20 $/ay)", "Geçmişin yarısı seyrek FTD fiyatıyla"],
    ]
    E.append(_table(st, [[para(st, c, st.cell) for c in row] if i else row for i, row in enumerate(plan)], [1.6 * cm, 15 * cm, W - 16.6 * cm]))

    def footer(canvas, d):
        canvas.saveState()
        canvas.setFont(st.reg, 7)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(1.3 * cm, 0.7 * cm, "Fırsat Radarı · Belirti Haritası sürüm 2 · yatırım tavsiyesi değildir")
        canvas.drawRightString(landscape(A4)[0] - 1.3 * cm, 0.7 * cm, f"Sayfa {d.page}")
        canvas.restoreState()

    doc.build(E, onFirstPage=footer, onLaterPages=footer)
    return OUT


if __name__ == "__main__":
    img = Path(sys.argv[1]) if len(sys.argv) > 1 else R
    print(build(img))

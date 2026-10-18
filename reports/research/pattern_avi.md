# Pattern Avı — Sonuç: "Dipten Çok Yükselmiş + Likit + Büyüyen"

## Arama
- **Yeni belirtiler:** dibe yakınlık, zirveden uzaklık (1 yıl, 3 yıl, tüm geçmiş), düşüş ve yükseliş miktarları, 1 hafta–3 yıl getirileri, trend eğimi ve düzgünlüğü, oynaklık, hacim değişimi, ham fiyat, sızıntısız kâr sürprizi.
  - Sıra yerine gerçek sayılar kullanıldı.
  - Sızıntı kontrolü: bütün yeni belirtilerin gelecek getiriyle uyumu (IC) |0,07| altında.
- **Koşullar:** 84 belirti × 9 eşik × 2 yön = 1.548 koşul.
- **Denenen kurallar:** bütün tekler, bütün ikililer (1,2 milyon) ve en iyi 300 ikiliye eklenen üçüncü koşul.
- **Portföy ve seçim:** Koşulu sağlayan bütün hisseler eşit ağırlıkla alındı; maliyet dahil, 3 ay tutma. Seçim Ocak zincirinde yapıldı.
- **Ezber:** Ocak'ta en iyi görünen kurallar (yıllık %35–37) görmediği aylarda %10–29'a düştü. Ocak ile görmediği aylar arasındaki ilişki 0,41.
- **Bir aile üç zincirde de aynı kaldı:** dipten çok yükselmiş + likit + büyüyen.
  - **Dürüstlük notu:** Bu aile görmediği aylardaki sonuçlara bakılarak öne çıkarıldı. Bu yüzden Şubat ve Mart zincirleri artık tam görülmemiş sayılmaz.

## Kural
**Son 52 haftanın dibinden en az %115 yükselmiş (dip fiyatın 2,15 katı) VE en likit %30'da VE gelir büyümesi evrenin alt %30'unda değil.** Bütün uyan hisseler (medyan 13–16 hisse) eşit ağırlıkla 3 ay tutulur.

## Sınav (`radar/research/pattern_sinav.py`)

| | Ocak | Şubat | Mart |
|---|---|---|---|
| Yıllık getiri (maliyet dahil) | %31,1 | %36,6 | %32,6 |
| S&P 500 | %14,0 | %14,6 | %13,7 |
| En kötü düşüş (kural / S&P) | −%34 / −%23 | −%34 / −%19 | −%24 / −%13 |
| S&P'yi geçtiği yıl | 14/17 | 15/17 | 15/17 |
| Tek hisse getirisi +%100'de kesilince | %27,4 | %32,0 | %29,9 |
| Her dönemin en iyi hissesi çıkarılınca | %16,6 | %20,2 | %18,1 |

| Dönem | Kural (3 zincir) | S&P |
|---|---|---|
| 2010–2014 | %29–31 | %15–16 |
| 2015–2019 | %22–27 | %8–12 |
| 2020–2022 | %9–49 | %8–13 |
| 2023–2026 | %58–61 | %21–22 |

**Eşik ızgarası (plato testi):** Üç eşik değiştirilerek 120 kombinasyon denendi.
- 115'i üç zincirde de S&P'yi geçti.
- 22'si üç zincirde de S&P'yi 10 puandan fazla geçti.
- En iyi bölge: dipten ×2,0–2,15, likidite üst %20–30, gelir büyümesi alt %10–30 dışı.
- Sonuç tek bir eşiğe bağlı değil; geniş bir platoda duruyor.

## Sınırlar
- Bu, momentum etkisinin likit ve büyüyen şirketlerdeki bir biçimi; akademide bilinen bir etki.
- Getirinin önemli kısmı her dönemin en iyi 1–2 hissesinden geliyor. En iyi hisse çıkarılınca getiri %17–20'ye iniyor.
- 2020 (+%269) ve 2023–2026 çok güçlü; 2011, 2021 ve 2022 zayıf.
- Yalnızca günlük fiyatı olan hisseler kullanıldı; likit hisselerde hayatta kalan yanılgısı küçük ama sıfır değil.
- Zincirler aynı yılları paylaşıyor. Gerçekten görülmemiş tek veri, bugünden sonraki canlı dönem.
- S&P × 3 hedefi yıllık ≈ %45. Kural ≈ S&P × 2,2–2,5.

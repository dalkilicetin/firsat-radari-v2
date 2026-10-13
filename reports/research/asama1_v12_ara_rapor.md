# 1. Aşama (v1.2) — Ara Rapor: Düzeltmeler ve Bölünme Kontrolleri

- **Tarih:** 13 Ekim 2026
- **Ön kayıt:** v1.2 (commit 744d13e)
- **Kapsam:** Yalnızca veri. Yeni belirti, model eğitimi, parametre araması yok. Çerçeve **henüz yeniden kurulmadı**: kurulumu doğrudan etkileyen bir karar gerekiyor (K1).
- **Ayrıntılı çıktılar:**
  - `asama1_v12.json`
  - `asama1_v12_bolunme.csv` ve `asama1_v12_bolunme_kabul.csv` (olay başına)
  - `asama1_v12_c_siniflari.csv`, `asama1_v12_c_tanima_uygun.csv`
  - `asama1_v12_hucre.csv`, `asama1_v12_hucre_aciklama.csv`
  - `asama1_capa.csv`

## Özet

| Sonuç | Konu |
|---|---|
| ✅ Geçti | (a) hisse oranı ve (b) piyasa değeri sürekliliği: bölünme ve ters bölünme ayrı ayrı ≥ %99 |
| ✅ Geçti | Tetiklenmeyen 13 olayın tamamı artık doğru düzeltiliyor |
| ✅ Geçti | Olay kaydı olmayan hisselerde düzeltme hiçbir hücreyi değiştirmiyor (0 / 8.655 hisse) |
| ✅ Geçti | Borç çift sayımı giderildi (1.300 rapor); belirsiz gözlem %0,42 |
| ❌ Başarısız | (c) ilk rapor kontrolü, belgesiz olaylarda: bölünme %71,5, ters bölünme %45,4 (eşik %99) |
| ⚠️ Karar gerektiriyor | K1: Düzeltmenin başlangıcı. v1.2'de benim yazdığım kural 644 raporda çift düzeltme yapıyor |
| ⚠️ Karar gerektiriyor | K2: Yahoo kayıt hataları: bölünme diye kaydedilmiş ayrılmalar, çift kayıtlar, eksik bölünmeler |
| ⚠️ Karar gerektiriyor | K3: (c) kontrolünün uygulanışı: arşivde kapak sayfası sayısı neredeyse yok |

## 1. Olaylar (2010 →)

| Tür | Kaynak | Olay |
|---|---|---|
| Bölünme | Yahoo / çıkmış hisselerin Yahoo serisi | 631 / 4 |
| Ters bölünme | Yahoo / çıkmış hisselerin Yahoo serisi | 2.408 / 138 |
| Ayrılma ya da hisse temettüsü (1/1,3–1,3) | Yahoo / çıkmış hisselerin Yahoo serisi | 395 / 10 |
| Tahmini ters bölünme | FTD | 563 |

## 2. Kabul kontrolleri (v1.2 kuralıyla, düzeltilmiş kodla)

| Kontrol | Bölünme | Ters bölünme | Eşik | Sonuç |
|---|---|---|---|---|
| (a) hisse oranı ±%1 | 360/360 (%100) | 1.929/1.939 (%99,48) | ≥ %99 | ✅ |
| (b) piyasa değeri sürekliliği ≤ 2 puan | 359/360 (%99,72) | 1.927/1.938 (%99,43) | ≥ %99 | ✅ |
| (c) ilk rapor ±%2, satış belgesi olmayanlar | 206/288 (%71,5) | 292/643 (%45,4) | ≥ %99 | ❌ |
| (c) kapsam dışı (satış belgesi var: 424B*, 8-K 3.02) | 162 olay | 1.559 olay | — | ayrı raporlandı |

- (a) ve (b), aynı hafta yeni rapor gelmeyen olaylarda ölçüldü: bölünmede 21, ters bölünmede 139 olay bu nedenle dışarıda.
- Kalan 22 (a)/(b) başarısızlığı `asama1_v12.json → bolunme.a_b_basarisiz_olaylar` içinde.

**v1.1 ile karşılaştırma.** v1.1 kuralı (tek havuz, (c) her olaya) aynı düzeltilmiş veriye uygulandı:

| Kontrol | Eski çerçeve, v1.1 kuralı | Düzeltilmiş veri, v1.1 kuralı | Düzeltilmiş veri, v1.2 kuralı |
|---|---|---|---|
| (a) | %94,4 (bölünme) / %97,0 (ters) | %99,54 | %100 / %99,48 |
| (b) | %97,8 / %98,7 | %99,49 | %99,72 / %99,43 |
| (c) | %65,8 / %28,7 | %36,0 | %71,5 / %45,4 (yalnızca belgesiz) |

- (a) ve (b)'deki iyileşme veri düzeltmesinden geliyor; kapsam değişmedi.
- (c)'deki yükseliş kapsam değişikliğinden geliyor: belgeli olaylar dışarıda.

**Ayrılma / hisse temettüsü (405 olay; kabul hesabı dışında):**
- Alt sınıflar: hisse temettüsü olası 79, ayrılma olası 90, belirsiz 236.
- (b) yalnızca %11 sağlanıyor. Bu beklenen bir sonuç: hisse sayısı düzeltilmediği için piyasa değeri olay haftası düşüyor. Ayrılmada bu düşüş gerçek; hisse temettüsünde bir sonraki rapora kadar süren bir hata.

**Tahmini ters bölünmeler (FTD, 563 olay):** (b) %100.

## 3. Tetiklenmeyen 13 olay

Hepsinde (a) = 0 ve (b) = 0; yani düzeltme artık doğru tetikleniyor.

**v1.1'deki neden:** Düzeltme fiyat oranından (S) alınıyordu. Raporun kabul haftasında bu oran boştu ve düzeltme hiç uygulanmıyordu. Etkilenen olaylar:
- AMPG 2021
- AMTB 2018
- CRE 2026
- FCHL 2026 (iki olay)
- GMEX 2025–26 (beş olay)
- LVO 2017
- SEGG 2023
- SFBS 2014

Olay kaydından alınan oran bu sorunu ortadan kaldırdı.

**Tarih, sembol ve oran yönü:**
- Olayların hepsinde Yahoo kaydı ile ham fiyat sıçraması aynı haftada (tarih hatası 0).
- Oran yönü fiyatla tutarlı.
- Sembol ile şirket eşleşmesi tutarlı.

**(c) sonuçları:**

| Olay | (c) sonucu |
|---|---|
| AMTB, LVO, SEGG | Sağlandı (0 / −%0,2 / 0) |
| AMPG, CRE, FCHL, SFBS | İlk raporda sayı fazla (−%7 ile −%47 arası); hepsinde satış belgesi var (424B4/424B5/8-K 3.02) |
| GMEX 2025 | İlk raporda sayı 17 kat fazla; satış belgesi (424B5) var, yani yoğun ihraç |
| GMEX 2026 (4 olay) | Sonraki rapor yok |

## 4. Bölünme kaydı olmayan hisselerde değişen hücreler

| | Hücre | Şirket |
|---|---|---|
| v1.1 yöntemiyle değişen (yedeksiz sayıyla yeniden sayıldı; v1.1'de 6.568) | 6.488 | 419 |
| FTD tahmini ters bölünme (artık açık olay kaydı) | 4.446 | 303 |
| Çıkmış hissenin Yahoo bölünmesi (v1.1 olay listesinde yoktu; artık olay kaydı) | 1.348 | 77 |
| Olay kaydı yok, fiyat oranı sıçramış | 694 | 39 |
| — özel temettü / dağıtım (ör. KDP 2018, WY 2010, BAH 2012, GLPI 2014, VC 2016, GEN 2020, ELME 2026) | 544 | 35 |
| — **Yahoo kaydı eksik bölünme** (ETN 2011 2:1, XRX 2017 1:4, NEWT 2014 1:5, XPRO 2021 1:6) | 150 | 4 |
| **Yeni yöntem: olay kaydı olmayan hisselerde değişen hücre** | **0** | 8.655 hisse |

- Otomatik sınıflama oranı 1,5'e yakın olan 3 özel temettüyü (NATH 2015, NLOP 2026, TORO 2026) bölünme saydı; elle düzeltildi.
- Açıklanamayan hücre kalmadı.
- Özel temettülerde eski yöntem hatalıydı: hisse sayısını yanlışlıkla bölüyordu. Yeni yöntem bunu yapmıyor.
- 4 eksik bölünmede ise yeni yöntem hatalı, çünkü Yahoo kaydı eksik (K2). Hepsi borsadan çıkmış şirketler; etkileri bir sonraki rapora kadar.

## 5. Borç tanımı

| | Değer |
|---|---|
| Rapor | 138.891 |
| Kalem bileşimi | Uzun vade (kısa vadesiz) + uzun vadenin kısa kısmı 56.569; yalnız uzun vade (kısa vadesiz) 32.020; yalnız toplam uzun vade 21.310; yalnız uzun vadenin kısa kısmı 9.882; uzun vade (kısa vadesiz) + kısa vadeli borçlar 9.551; yalnız kısa vadeli borçlar 7.682 |
| Eski tanımda çift sayılan | 1.300 rapor (toplam uzun vadeli borç + kısa vadeli kısmı yeniden) |
| Belirsiz (toplam uzun vadeli borç + kısa vadeli borç; kısmın ayrı kalemi yok) | 577 rapor (%0,42); üst sınır / alt sınır medyanı 1,13 |

Borca dayanan belirtilerin değişimi ve eksik veri oranı, çerçeve kurulunca ölçülecek.

## 6. Karar gerektiren konular

### K1. Düzeltmenin başlangıcı: v1.2'deki kendi kuralımda hata

v1.2'de "hisse sayısı, sayının geçerli olduğu tarihten itibaren düzeltilir" yazdım. Bu kural iki gerçekle çelişiyor:
- Arşivde kapak sayfası sayısı neredeyse yok (759 kayıt). Hisse sayısı bilançodan geliyor; tarihi dönem sonu.
- ABD muhasebe kuralına göre (SAB Topic 4C), dönem sonundan sonra ama rapor yayımlanmadan önce yapılan bölünme, rapordaki sayıya geriye dönük yansıtılır. Örnek: Alphabet'in 30 Haziran 2022 dönemli raporu, 15 Temmuz'daki 20'ye 1 bölünmeden sonra yayımlandı ve 13,08 milyar (bölünme sonrası) sayısını veriyor. v1.2 kuralı bunu bir kez daha 20 ile çarpar.

Bölünmenin dönem sonu ile rapor arasına düştüğü 1.294 rapor (778 şirket) ölçüldü:

| Rapordaki sayı | Rapor |
|---|---|
| Geriye dönük düzeltilmiş | 644 |
| Düzeltilmemiş | 200 |
| Belirsiz (arada ihraç vb.) | 450 |

| Seçenek | Doğru olduğu rapor | Hatalı olduğu rapor |
|---|---|---|
| (a) Kabul tarihi (v1.1'in başlangıcı; yalnızca oran olay kaydından) | 644 | 200 (bir sonraki rapora kadar düzeltme eksik) |
| (b) Geçerlilik tarihi (v1.2'de yazılan) | 200 | 644 (çift düzeltme) |
| (c) Rapor başına sınama: sayı, önceki raporun sayısı × oran'a mı yoksa önceki sayıya mı yakın (iki bilgi de kabul anında bilinir; sızıntı yok) | ikisi de | belirsiz 450 |

- Seçeneklerin (a)/(b) kontrollerine etkisi yok; (c)'yi biraz değiştiriyor (bölünme %71,5 → %74,0; ters %45,4 → %46,5).
- (c) seçeneği yeni bir algoritmadır ve v1.3 gerektirir.
- Önerim: (a). Muhasebe kuralına uyuyor, çoğunlukta doğru ve v1.1'in kanıtlanmış davranışı.

### K2. Yahoo kayıt hataları (kayıt mutlak doğru kabul edilmedi)

1. **Ayrılmanın 1,3'ün üstündeki oranla bölünme diye kaydı:** EBAY 2015, WDC 2025, A 2014, XPO 2021/2022, HPE 2017, FTV 2025, ASH 2017, SPXC 2015, AIV 2020, OIS 2014, ENSG 2014, FWONK 2014, OPLN 2019, LILAK 2026 vb.
   - (c) sınıflamasında "kayıtta bölünme var, hisse sayısı değişmedi" diye toplam 66 olay çıktı; hepsi elle doğrulanmadı.
   - Bu olaylarda hisse sayısı yanlışlıkla oranla çarpılıyor ve piyasa değeri bir sonraki rapora kadar yüksek kalıyor.
2. **Aynı olayın bir hafta arayla iki kez kaydı:** WFCF 2020, CENN 2023. Düzeltme iki kez uygulanıyor.
3. **Eksik bölünme kaydı:** ETN, XRX, NEWT, XPRO (bölüm 4).

Seçenekler:
- (i) Hatalar yalnızca raporlanır, çerçeve böyle kurulur.
- (ii) Olay başına elle doğrulanmış bir düzeltme listesi tutulur: ayrılma bölünme sayılmaz, çift kayıt bir kez sayılır, eksik bölünme eklenir. Bu da v1.3 gerektirir.

Önerim (ii). Liste tüm olayları elle doğrular ve kural olarak değil, olay başına gerekçeyle tutulur.

### K3. (c) kontrolü fiilen kapak sayfası sayısını ölçemiyor

Ön kayıt "ilk raporun kapak sayfası sayısı" diyor; arşivde bu sayı yok, bilanço sayısı var. Başarısız (c) olaylarının büyük kısmı şu sınıflarda (belgesiz ve belgeli toplam):

| Sınıf | Bölünme | Ters bölünme |
|---|---|---|
| İlk raporun sayısı dönem sonu itibarıyla bölünmeden önceye ait | 48 | 573 |
| İlk rapordaki sayı fazla (ihraç vb.) | 11 | 428 |
| Birim / ölçek hatası olası (10 katın üstünde fark) | 7 | 164 |
| Kayıtta bölünme var, hisse sayısı değişmedi (K2-1) | 33 | 33 |

- "Bölünmeden önceye ait" sınıfı K1 ile bağlantılı: bu raporların bir kısmı geriye dönük düzeltilmiş, bir kısmı değil.
- Sayının geçerlilik tarihi bölünmeden sonraya düşen ilk rapor kullanıldığında sonuç düzelmedi, kötüleşti: belgesiz bölünme %50, belgesiz ters bölünme %25. Nedeni yine K1: bilanço tarihine güvenilemiyor.

Seçenekler:
- (i) (c) olduğu gibi başarısız kalır ve 1. aşama bu maddede başarısız sayılır.
- (ii) Kapak sayfası sayısı ayrıca indirilir. SEC XBRL `companyfacts` API'si `dei:EntityCommonStockSharesOutstanding` değerini kapak tarihiyle verir. (c) bununla yeniden ölçülür; eşik değişmez.

Önerim (ii): ön kayıttaki kontrolü yazıldığı gibi uygulamanın tek yolu bu.

## 7. Kalan işler (kararlardan sonra)

1. K1–K3 kararlarına göre kod (gerekirse v1.3).
2. Çerçevenin yeniden kurulması (bütün belirti grupları; `panel.py` değiştiği için önbellek yenilenir).
3. Kontrollerin her biri ayrı süreçte yeniden koşulacak:
   - tarih tablosu, Newey–West, kalemler, oranlar, eksik veri;
   - hisse sayısı kapsaması (Karar 1: etkilenen belirtiler, kapsama, şirket bileşimi);
   - borca dayanan belirtiler;
   - çıkış senaryoları (4,6 puanlık farkın düzeltilmiş çerçevede ne kadar kaldığı);
   - belirti doğrulama (T1–T6).
4. Nihai rapor: Geçti / Başarısız / Karar gerektiriyor, dört grupta.

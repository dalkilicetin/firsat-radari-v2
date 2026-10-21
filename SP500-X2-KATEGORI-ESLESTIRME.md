# S&P 500'ü 2 kat geride bırakan hisseler: kategori eşleştirmesi ve hikâyeler

> Liste için: `SP500-X2-HISSELER.md`. Kategoriler: `DIPTEN-TOPARLANMA-BELIRTILERI.md` belgesindeki ~40 belirtinin çalışma versiyonu. Yatırım tavsiyesi değildir.

## Nasıl okunmalı (önce bunlar)

- **40 kategorinin yalnızca 22'si eldeki veriyle ölçülebiliyor.** Kalan 18'i (haber, nakit ömrü, borç, geri alım, açığa satış, spin-off, endeks girişi…) için hiçbir hisse etiketlenemedi; bu "yok" demek değil, **"bilmiyoruz"** demek.
- **Hiçbiri** = ölçülebilir "hikâye" kategorilerinin (K01, K02, K03, K05, K07, K08, K10, K11, K19, K20, K21) hiçbirine uymuyor. Bu örnekte hiçbir kazanan "hiçbiri" çıkmadı; kategoriler geniş olduğu için bu tek başına bilgi taşımayabilir, bu yüzden ≤2 kategorili **zayıf eşleşme** de ayrıca verildi.
- **Temel veri (satış büyümesi, marj, F/K, bilanço sürprizi, içeriden alım) bugünün anlık görüntüsü.** Yükselişten *sonraki* durumu gösterir; "yükselmeden önce bu belirti vardı" diye okunamaz.
- Bazı kategoriler kazanmanın kendisinden türediği için kazananlarda zaten yüksek çıkar (K01, K05, K08, K21). **Sızıntısız tek bilgi, pencere başlamadan önceki durumdur** (K03, K04).
- Eşikleri ben koydum, **ama koymadan önce bu hisselerin rakamlarına bakmıştım**; eşikler ayarlı sayılmalı, tarafsız bir test değil.
- Örneklem yanlı (bkz. `SP500-X2-HISSELER.md`). Aşağıdaki oranlar betimseldir, kanıt değildir.

## 1. Kategori kataloğu (40)

| Kod | Kategori | Ölçülebildi mi? | Kural ya da neden ölçülemedi |
|---|---|---|---|
| K01 | Dışsal şoktan toparlanma | evet | 2025 şubat zirvesinden nisana ≥%10 düşmüş ve mayıs→ekim ≥%25 toparlamış |
| K02 | Şokta dayanıklı (gizli güç) | evet | 2025 şubat zirvesinden nisana düşüş ≤%3 (S&P 500 ≈ −%8) |
| K03 | Önceki ayı piyasasından toparlanma | evet | Pencere başında (2023-10) kendi önceki zirvesinden ≥%35 aşağıda |
| K04 | 2022 ayı piyasasında çok dayanıklı | evet | 2021-12→2022-09 düşüşü ≤%10 (S&P 500 ≈ −%25) ya da yükseliş |
| K05 | Trend lideri / istikrarlı yürüyüş | evet | Ayların ≥%60'ı 10 aylık ortalamanın üstünde ve en kötü düşüş ≤%35 |
| K06 | Çalkantılı yolculuk (uyarı) | evet | Pencere içinde en kötü düşüş ≥%45 |
| K07 | Tek dalga patlama | evet | Toplam kazancın ≥%90'ı tek bir 12 aylık dilimde |
| K08 | Çok yıllı yürüyüş | evet | Toplam kazancın en çok %65'i tek 12 ay; kazanç yıllara yayılmış |
| K09 | Hâlâ tepeye yakın (kovalama riski) | evet | Pencere sonunda pencere zirvesinin ≤%5 altında |
| K10 | Satışlar güçlü büyüyor | evet | Son rapor satış büyümesi ≥%20 (bugünkü veri) |
| K11 | Marj iyileşti | evet | Brüt marj bugün − 5 yıl önce ≥ +3 puan (bugünkü veri) |
| K12 | Marj daraldı (uyarı) | evet | Brüt marj bugün − 5 yıl önce ≤ −3 puan (bugünkü veri) |
| K13 | Kârlı | evet | Net marj ≥%10 (bugünkü veri) |
| K14 | Zararda (spekülatif) | evet | Net marj < 0 (bugünkü veri) |
| K15 | Pahalı değerleme | evet | F/K ≥60 ya da fiyat/satış ≥20 (bugünkü veri) |
| K16 | Makul değerleme | evet | F/K < 20 (bugünkü veri) |
| K17 | Dev şirket | evet | Piyasa değeri ≥100 milyar $ |
| K18 | Küçük şirket | evet | Piyasa değeri <10 milyar $ |
| K19 | Son bilançoda beklentiyi aştı | evet | Son bilanço kâr sürprizi ≥%8 (bugünkü veri) |
| K20 | İçeriden alım | evet | Son dönemde içeriden alan yönetici var (bugünkü veri) |
| K21 | Tema dalgası | evet | Aynı sektörde (Yarı iletken ya da Teknoloji) ≥5 kazanan hisse daha var |
| K22 | Zirveden sert geri çekilme (uyarı) | evet | Pencere sonunda pencere zirvesinin ≥%30 altında |
| K23 | Dışsal korku mu, şirkete özgü mü | **hayır** | Haber verisi gerekir |
| K24 | Fiyat kötü haberi yansıttı mı | **hayır** | Haber ve beklenti verisi gerekir |
| K25 | Nakit ömrü | **hayır** | Çeyreklik nakit akışı verisi yok |
| K26 | Borç vadesi | **hayır** | Borç vade verisi yok |
| K27 | Hisse seyrelmesi | **hayır** | Hisse sayısı geçmişi yok |
| K28 | Kâr–nakit dönüşümü | **hayır** | Nakit akışı verisi yok |
| K29 | Beklenti revizyonu | **hayır** | Analist tahmin geçmişi yok |
| K30 | Tetikleyici olay (sözleşme, onay) | **hayır** | Haber/sözleşme verisi yok |
| K31 | Büyük fon alımı | **hayır** | 13F verisi yok |
| K32 | Hisse geri alımı | **hayır** | Geri alım verisi yok |
| K33 | Açığa satış sıkışması | **hayır** | Açığa satış verisi yok |
| K34 | Şirket bölünmesi (spin-off) | **hayır** | Olay takvimi yok (yalnızca hafızadan not) |
| K35 | Endekse giriş | **hayır** | Endeks üyelik geçmişi yok (yalnızca hafızadan not) |
| K36 | Kilit açılışı | **hayır** | Halka arz kilit verisi yok |
| K37 | Bilanço sonrası kayma | **hayır** | Aylık veri bilanço gününü ayıramaz |
| K38 | Sıkışma sonrası kırılım | **hayır** | Günlük fiyat gerekir |
| K39 | Sektör öncüsü domino | **hayır** | Günlük fiyat ve bilanço takvimi gerekir |
| K40 | Yıl sonu vergi satışı | **hayır** | Günlük fiyat gerekir |

## 2. Özet: kazananlarda hangi belirtiler daha sık?

Kazanan 43 şirket ve kazanamayan 112 hisse (aynı örneklemden, GOOG tek sayıldı) aynı kurallardan geçirildi.

| Kod | Kategori | Kazananlarda | Diğerlerinde | Not |
|---|---|---|---|---|
| K01 | Dışsal şoktan toparlanma | %53 | %13 | kısmen mekanik (aynı dönemin getirisiyle ilişkili) |
| K02 | Şokta dayanıklı (gizli güç) | %23 | %21 |  |
| K03 | Önceki ayı piyasasından toparlanma | %53 | %28 | **sızıntısız** (pencere öncesi) |
| K04 | 2022 ayı piyasasında çok dayanıklı | %7 | %35 | **sızıntısız** (pencere öncesi) |
| K05 | Trend lideri / istikrarlı yürüyüş | %47 | %13 | kısmen mekanik |
| K06 | Çalkantılı yolculuk (uyarı) | %21 | %27 |  |
| K07 | Tek dalga patlama | %30 | %44 |  |
| K08 | Çok yıllı yürüyüş | %35 | %14 | kısmen mekanik |
| K09 | Hâlâ tepeye yakın (kovalama riski) | %21 | %36 |  |
| K10 | Satışlar güçlü büyüyor | %58 | %9 | bugünkü veri (sonuç) |
| K11 | Marj iyileşti | %40 | %45 | bugünkü veri (sonuç) |
| K12 | Marj daraldı (uyarı) | %5 | %7 |  |
| K13 | Kârlı | %77 | %66 |  |
| K14 | Zararda (spekülatif) | %7 | %4 |  |
| K15 | Pahalı değerleme | %26 | %9 | bugünkü veri (sonuç) |
| K16 | Makul değerleme | %19 | %38 | bugünkü veri (sonuç) |
| K17 | Dev şirket | %49 | %26 | bugünkü piyasa değeri (kazanmanın sonucu) |
| K18 | Küçük şirket | %12 | %10 | bugünkü piyasa değeri |
| K19 | Son bilançoda beklentiyi aştı | %40 | %37 | bugünkü veri |
| K20 | İçeriden alım | %0 | %1 | kimsede yok, doğrulanamadı |
| K21 | Tema dalgası | %51 | %12 | kazananların kendisinden türetildi (döngüsel) |
| K22 | Zirveden sert geri çekilme (uyarı) | %33 | %26 |  |

### Ana bulgular

1. **Önceki ayı piyasasında cezalandırılmış olmak (sızıntısız):** pencere başında kendi zirvesinden ≥%35 aşağıda olanlar kazananlarda %53, diğerlerinde %28. 2022'de piyasadan dayanıklı olanlar kazananlarda yalnızca %7, diğerlerinde %35. **Yani büyük kazananların çoğu 2022'de en çok dayak yiyenler arasındaydı.** Bu, "dipten toparlanma" hikâyesiyle uyumlu; yine de örneklem yanlı.
2. **Şokta toparlanma (2025 tarife düşüşü):** şokta ≥%10 düşüp sonraki 5 ayda ≥%25 toparlayanlar kazananlarda %53, diğerlerinde %13. Kısmen mekanik, ama "şokta düşenler sonra çok toparladı" hikâyesi kazananların yaklaşık yarısında var.
3. **Şokta dayanıklılık (gizli güç) kazananları ayırmıyor:** kazananlarda %23, diğerlerinde %21. Dayanıklı olmak ile büyük kazanmak aynı şey değil.
4. **Tema:** yarı iletken ya da teknoloji sektöründe olanlar kazananlarda %51. En kalabalık sektörler: Yarı iletken 12, Teknoloji 10, Elektrik ekipmanı 4, Havacılık ve savunma 2; geri kalan 15 şirket çok sayıda farklı sektöre dağılıyor. Büyük çoğunluk **yapay zekâ altyapısı** (çip, ekipman, bellek/depolama, bağlantı, ağ) temasına bağlanıyor (hafızaya göre).
5. **Satış büyümesi ≥%20:** kazananlarda %58, diğerlerinde %9. Bugünkü veri olduğu için "neden yükseldi"yi açıklar, "yükselmeden önce işaretti" değil.
6. **Pahalı değerleme:** kazananlarda %26, diğerlerinde %9; makul/ucuz olanlar kazananlarda daha seyrek (%19 ve %38). **"Ucuz" olmak kazanmayı öngörmedi.**
7. **İçeriden alım:** hiçbirinde yok. Bugünkü anlık görüntüden bu belirtiyi bu örnekte doğrulayamadık.
8. **Ortalama hikâye sayısı:** kazananlarda 4.3, diğerlerinde 2.4.
9. **Hiçbiri:** ölçülebilir hikâye kategorilerinin hiçbirine uymayan kazanan: **0**. **Zayıf eşleşme (≤2 kategori):** HOOD, KLAC, MPC, FTNT.
10. **Ölçülemeyen 18 kategori:** hiçbir hisse için etiketlenemedi. Özellikle **tetikleyici olay (K30)**, **geri alım (K32)**, **beklenti revizyonu (K29)** ve **haber (K23-K24)** bilinmiyor; bu yüzden "hiçbirine uymayan" hisseler aslında "hikâyesi ölçülemeyen" hisseler.

## 3. Hisse hisse eşleştirme

Hikâye kategorileri: K01, K02, K03, K05, K07, K08, K10, K11, K19, K20, K21. "Uyarı" kategorileri (K06, K09, K12, K14, K22) ve "profil" kategorileri (K13, K15–K18) hikâye sayılmaz. GOOG: GOOGL ile aynı şirket.

| Sembol | Hikâye kategorileri | Uyarı/profil kategorileri | Ölçülemeyen (hafızadan not) | Sonuç |
|---|---|---|---|---|
| AXTI | K01, K03, K07, K10, K11, K19, K21 | K06, K15, K18, K22 | bilinmiyor | hikâye var |
| QBTS | K02, K03, K07, K21 | K06, K14, K15, K18, K22 | bilinmiyor | hikâye var |
| PLTR | K02, K03, K10, K11, K19, K21 | K09, K13, K15, K17 | bilinmiyor | hikâye var |
| MU | K01, K10, K11, K21 | K13, K16, K17 | bilinmiyor | hikâye var |
| WDC | K01, K03, K07, K10, K11, K21 | K13, K16, K17, K22 | K34 spin-off | hikâye var |
| HOOD | K03, K10 | K06, K13, K22 | K35 endekse giriş | zayıf (≤2) |
| RGTI | K01, K03, K07, K10, K21 | K06, K12, K14, K15, K18, K22 | bilinmiyor | hikâye var |
| STX | K01, K03, K05, K10, K11, K19, K21 | K13, K17, K22 | bilinmiyor | hikâye var |
| COHR | K01, K03, K10 | K13, K22 | bilinmiyor | hikâye var |
| APP | K01, K03, K07, K10, K11, K21 | K06, K13, K22 | K35 endekse giriş | hikâye var |
| AMD | K01, K03, K07, K10, K11, K21 | K06, K13, K15, K17 | bilinmiyor | hikâye var |
| NVDA | K01, K05, K10, K11, K21 | K09, K13, K17 | bilinmiyor | hikâye var |
| SITM | K01, K03, K05, K10, K19, K21 | K15, K22 | bilinmiyor | hikâye var |
| HWM | K02, K05, K08, K11 | K04, K13 | bilinmiyor | hikâye var |
| GLW | K01, K03, K07 | K06, K13, K15, K17, K22 | bilinmiyor | hikâye var |
| TWLO | K03, K05, K19, K21 | K13 | bilinmiyor | hikâye var |
| LRCX | K01, K07, K10, K21 | K13, K17, K22 | bilinmiyor | hikâye var |
| APH | K02, K05, K08, K10, K11, K19 | K13, K17 | bilinmiyor | hikâye var |
| AVGO | K01, K10, K11, K21 | K13, K17 | bilinmiyor | hikâye var |
| TER | K01, K03, K07, K10, K19, K21 | K06, K13, K22 | bilinmiyor | hikâye var |
| HPE | K01, K05, K10, K11, K19, K21 | – | bilinmiyor | hikâye var |
| KLAC | K07, K21 | K13, K17, K22 | bilinmiyor | zayıf (≤2) |
| ZYME | K01, K03, K05, K08 | K14, K15, K18 | bilinmiyor | hikâye var |
| GE | K02, K05, K08, K10 | K13, K17 | K34 spin-off | hikâye var |
| ANET | K01, K05, K08, K10, K19 | K13, K15, K17 | bilinmiyor | hikâye var |
| BK | K05, K08, K10 | K13, K16 | bilinmiyor | hikâye var |
| FORM | K01, K07, K11, K19, K21 | K06, K13, K15, K18 | bilinmiyor | hikâye var |
| CAT | K01, K05, K19 | K13, K17 | bilinmiyor | hikâye var |
| NEM | K02, K03, K07, K10, K11 | K13, K16, K17 | bilinmiyor | hikâye var |
| FFIV | K03, K05, K08, K19 | K09, K13 | bilinmiyor | hikâye var |
| MPC | K19 | K04, K09, K16, K17 | bilinmiyor | zayıf (≤2) |
| AMAT | K01, K07, K21 | K13, K17, K22 | bilinmiyor | hikâye var |
| C | K01, K03, K05, K08, K10 | K13, K16, K17 | bilinmiyor | hikâye var |
| PANW | K02, K08, K10, K21 | K15, K17 | bilinmiyor | hikâye var |
| EBAY | K02, K03, K05, K08 | K09, K13 | bilinmiyor | hikâye var |
| EXPE | K01, K03, K08, K11 | K13, K16 | bilinmiyor | hikâye var |
| JCI | K02, K03, K05, K08, K11 | K09, K13 | bilinmiyor | hikâye var |
| FTNT | K19, K21 | K09, K13, K17 | bilinmiyor | zayıf (≤2) |
| GM | K03, K05, K08, K19 | K12 | bilinmiyor | hikâye var |
| NTAP | K08, K19, K21 | K09, K13 | bilinmiyor | hikâye var |
| KEYS | K03, K05, K10, K19 | K13 | bilinmiyor | hikâye var |
| CAH | K02, K05, K08 | K04, K09 | bilinmiyor | hikâye var |
| GOOGL | K01, K05, K10, K11 | K13, K16, K17 | bilinmiyor | hikâye var |
| GOOG | K01, K10, K11 | K13, K16, K17 | bilinmiyor | hikâye var |

## 4. Hisse hisse hikâyeler

Her hissede önce **veriden çıkan hikâye** (fiyat yolu ve bugünkü temel veri), sonra **hafızama göre arka plan** var. Hafıza kısmı repodaki verilerden gelmez, haber kaynağı yoktur ve doğrulanmamıştır; "belirsiz" yazılanlar tahmindir.

### 1. AXTI — AXT Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %3,148 (37.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %77 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%24. En büyük 12 aylık dalga 2026-05 ayında bitti (+%6,732); yolda en kötü düşüş %69. 2025 tarife düşüşünde zirveden nisana −%33, sonraki 5 ayda %426. Şu an pencere zirvesinin %37 altında. Bugünkü temel veri: satış büyümesi %46, brüt marj %32 (5 yıl önce %25), net marj %3, F/K 947, piyasa değeri 4 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ veri merkezlerinin optik bağlantılarında kullanılan indiyum fosfat altlık üreticisi; çok küçük bir şirketin tema talebiyle sıçraması. Yükseliş çok sert, değerleme aşırı.

### 2. QBTS — D-Wave Quantum Inc (Teknoloji)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %1,539 (18.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %93 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%20. En büyük 12 aylık dalga 2025-10 ayında bitti (+%3,396); yolda en kötü düşüş %68. 2025 tarife düşüşünde zirveden nisana %16, sonraki 5 ayda %127. Şu an pencere zirvesinin %68 altında. Bugünkü temel veri: satış büyümesi %-44, brüt marj %64 (5 yıl önce %66), net marj %-2002, piyasa değeri 4 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Kuantum bilişim temasının spekülatif adlarından; geliri küçük, zararı büyük. Yükseliş temaya ve büyük olasılıkla sermaye artırımlarına dayanıyor; temel veri bunu desteklemiyor.

### 3. PLTR — Palantir Technologies Inc (Teknoloji)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K03 Önceki ayı piyasasından toparlanma, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %1,255 (15.1 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %43 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%55. En büyük 12 aylık dalga 2025-05 ayında bitti (+%508); yolda en kötü düşüş %42. 2025 tarife düşüşünde zirveden nisana %39, sonraki 5 ayda %52. Şu an pencere zirvesinin %0 altında. Bugünkü temel veri: satış büyümesi %79, brüt marj %85 (5 yıl önce %80), net marj %49, F/K 155, piyasa değeri 468 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ yazılım platformu ve devlet/savunma müşterileri; zarardan güçlü kârlılığa geçiş hikâyesi.

### 4. MU — Micron Technology Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %1,253 (15.0 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %28 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%46. En büyük 12 aylık dalga 2026-05 ayında bitti (+%928); yolda en kötü düşüş %41. 2025 tarife düşüşünde zirveden nisana −%18, sonraki 5 ayda %137. Şu an pencere zirvesinin %22 altında. Bugünkü temel veri: satış büyümesi %256, brüt marj %81 (5 yıl önce %36), net marj %64, F/K 12, piyasa değeri 1,047 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ için yüksek bant genişlikli bellek talebi ve bellek fiyat döngüsünün yukarı dönmesi.

### 5. WDC — Western Digital Corp (Teknoloji)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %1,100 (13.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %38 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%50. En büyük 12 aylık dalga 2026-05 ayında bitti (+%930); yolda en kötü düşüş %43. 2025 tarife düşüşünde zirveden nisana −%11, sonraki 5 ayda %191. Şu an pencere zirvesinin %43 altında. Bugünkü temel veri: satış büyümesi %36, brüt marj %49 (5 yıl önce %34), net marj %73, F/K 14, piyasa değeri 133 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Depolama döngüsü ve yapay zekâ veri merkezi talebi. Şubat 2025'te SanDisk'in ayrılması (spin-off) hikâyenin parçası (K34, hafızadan).

### 6. HOOD — Robinhood Markets Inc (Finansal hizmet)

- **Kategoriler:** K03 Önceki ayı piyasasından toparlanma, K10 Satışlar güçlü büyüyor
- **Veriden hikâye:** 3 yılda %1,006 (12.1 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %74 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%43. En büyük 12 aylık dalga 2025-10 ayında bitti (+%525); yolda en kötü düşüş %53. 2025 tarife düşüşünde zirveden nisana −%5, sonraki 5 ayda %122. Şu an pencere zirvesinin %31 altında. Bugünkü temel veri: satış büyümesi %38, brüt marj %95 (5 yıl önce %93), net marj %42, F/K 42, piyasa değeri 87 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Bireysel yatırımcı işlem hacmi ve kripto canlanması; 2025'te S&P 500'e girdiğini hatırlıyorum (K35, hafızadan).

### 7. RGTI — Rigetti Computing Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %1,001 (12.0 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %90 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%82. En büyük 12 aylık dalga 2025-09 ayında bitti (+%3,705); yolda en kötü düşüş %74. 2025 tarife düşüşünde zirveden nisana −%33, sonraki 5 ayda %266. Şu an pencere zirvesinin %74 altında. Bugünkü temel veri: satış büyümesi %68, brüt marj %35 (5 yıl önce %63), net marj %-1787, piyasa değeri 4 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Kuantum bilişim teması; spekülatif, zarar büyük. Yükseliş temaya dayanıyor.

### 8. STX — Seagate Technology Holdings PLC (Teknoloji)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %836 (10.0 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %40 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%53. En büyük 12 aylık dalga 2026-05 ayında bitti (+%646); yolda en kötü düşüş %34. 2025 tarife düşüşünde zirveden nisana −%11, sonraki 5 ayda %117. Şu an pencere zirvesinin %34 altında. Bugünkü temel veri: satış büyümesi %34, brüt marj %46 (5 yıl önce %30), net marj %26, F/K 47, piyasa değeri 150 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Depolama döngüsü ve yapay zekâ veri merkezi diski talebi.

### 9. COHR — Coherent Corp (Elektrik ekipmanı)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K10 Satışlar güçlü büyüyor
- **Veriden hikâye:** 3 yılda %687 (8.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %59 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%49. En büyük 12 aylık dalga 2026-04 ayında bitti (+%397); yolda en kötü düşüş %41. 2025 tarife düşüşünde zirveden nisana −%29, sonraki 5 ayda %74. Şu an pencere zirvesinin %41 altında. Bugünkü temel veri: satış büyümesi %23, brüt marj %38 (5 yıl önce %35), net marj %11, F/K 57, piyasa değeri 46 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Optik iletişim bileşenleri; yapay zekâ veri merkezi bağlantı talebi.

### 10. APP — Applovin Corp (Teknoloji)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %630 (7.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %63 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%79. En büyük 12 aylık dalga 2025-01 ayında bitti (+%799); yolda en kötü düşüş %63. 2025 tarife düşüşünde zirveden nisana −%27, sonraki 5 ayda %62. Şu an pencere zirvesinin %63 altında. Bugünkü temel veri: satış büyümesi %61, brüt marj %88 (5 yıl önce %73), net marj %65, F/K 20, piyasa değeri 90 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Mobil reklam teknolojisi; yapay zekâ reklam motoru ile marj sıçraması. 2025'te S&P 500'e girdiğini hatırlıyorum (K35, hafızadan).

### 11. AMD — Advanced Micro Devices Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %446 (5.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %38 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%56. En büyük 12 aylık dalga 2026-05 ayında bitti (+%366); yolda en kötü düşüş %49. 2025 tarife düşüşünde zirveden nisana −%16, sonraki 5 ayda %131. Şu an pencere zirvesinin %12 altında. Bugünkü temel veri: satış büyümesi %40, brüt marj %53 (5 yıl önce %48), net marj %16, F/K 137, piyasa değeri 882 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ hızlandırıcıları ve sunucu işlemcileri.

### 12. NVDA — NVIDIA Corp (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %432 (5.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %17 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%59. En büyük 12 aylık dalga 2024-10 ayında bitti (+%226); yolda en kötü düşüş %22. 2025 tarife düşüşünde zirveden nisana −%13, sonraki 5 ayda %50. Şu an pencere zirvesinin %5 altında. Bugünkü temel veri: satış büyümesi %83, brüt marj %75 (5 yıl önce %69), net marj %64, F/K 27, piyasa değeri 5,161 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ eğitim ve çıkarım çipleri; yapay zekâ altyapı dalgasının merkezi.

### 13. SITM — SiTime Corp (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %403 (4.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %67 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%73. En büyük 12 aylık dalga 2026-04 ayında bitti (+%283); yolda en kötü düşüş %33. 2025 tarife düşüşünde zirveden nisana −%28, sonraki 5 ayda %48. Şu an pencere zirvesinin %33 altında. Bugünkü temel veri: satış büyümesi %83, brüt marj %59 (5 yıl önce %58), net marj %3, F/K 1085, piyasa değeri 15 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Zamanlama çipleri; yapay zekâ ağ ve veri merkezi talebi.

### 14. HWM — Howmet Aerospace Inc (Havacılık ve savunma)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %399 (4.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %14 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%3. En büyük 12 aylık dalga 2025-06 ayında bitti (+%140); yolda en kötü düşüş %22. 2025 tarife düşüşünde zirveden nisana %1, sonraki 5 ayda %21. Şu an pencere zirvesinin %22 altında. Bugünkü temel veri: satış büyümesi %18, brüt marj %36 (5 yıl önce %30), net marj %21, F/K 47, piyasa değeri 88 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Uçak motoru ve havacılık parçaları; sipariş birikimi ve fiyatlama gücü.

### 15. GLW — Corning Inc (Elektrik ekipmanı)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama
- **Veriden hikâye:** 3 yılda %396 (4.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %36 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%22. En büyük 12 aylık dalga 2026-06 ayında bitti (+%386); yolda en kötü düşüş %48. 2025 tarife düşüşünde zirveden nisana −%15, sonraki 5 ayda %80. Şu an pencere zirvesinin %48 altında. Bugünkü temel veri: satış büyümesi %19, brüt marj %36 (5 yıl önce %34), net marj %11, F/K 61, piyasa değeri 116 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Fiber optik kablo; yapay zekâ veri merkezi bağlantı talebi.

### 16. TWLO — Twilio Inc (Teknoloji)

- **Kategoriler:** K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %377 (4.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %82 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%74. En büyük 12 aylık dalga 2026-09 ayında bitti (+%192); yolda en kötü düşüş %34. 2025 tarife düşüşünde zirveden nisana −%34, sonraki 5 ayda %15. Şu an pencere zirvesinin %16 altında. Bugünkü temel veri: satış büyümesi %18, brüt marj %49 (5 yıl önce %49), net marj %21, F/K 35, piyasa değeri 40 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** İletişim platformu; maliyet disiplini ve kârlılığa dönüş.

### 17. LRCX — Lam Research Corp (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %363 (4.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %18 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%49. En büyük 12 aylık dalga 2026-06 ayında bitti (+%345); yolda en kötü düşüş %37. 2025 tarife düşüşünde zirveden nisana −%12, sonraki 5 ayda %95. Şu an pencere zirvesinin %37 altında. Bugünkü temel veri: satış büyümesi %26, brüt marj %50 (5 yıl önce %48), net marj %31, F/K 45, piyasa değeri 330 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Çip üretim ekipmanı; bellek ve yapay zekâ yatırım döngüsü.

### 18. APH — Amphenol Corp (Elektrik ekipmanı)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %299 (3.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %9 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%23. En büyük 12 aylık dalga 2026-02 ayında bitti (+%119); yolda en kötü düşüş %13. 2025 tarife düşüşünde zirveden nisana %9, sonraki 5 ayda %55. Şu an pencere zirvesinin %9 altında. Bugünkü temel veri: satış büyümesi %54, brüt marj %39 (5 yıl önce %33), net marj %18, F/K 39, piyasa değeri 200 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Konnektör ve kablo; yapay zekâ veri merkezi, savunma ve otomotiv talebi.

### 19. AVGO — Broadcom Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %298 (3.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %9 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%33. En büyük 12 aylık dalga 2025-11 ayında bitti (+%149); yolda en kötü düşüş %28. 2025 tarife düşüşünde zirveden nisana −%13, sonraki 5 ayda %53. Şu an pencere zirvesinin %25 altında. Bugünkü temel veri: satış büyümesi %49, brüt marj %69 (5 yıl önce %66), net marj %43, F/K 42, piyasa değeri 1,602 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ özel çipleri ve ağ çipleri.

### 20. TER — Teradyne Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %290 (3.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %49 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%54. En büyük 12 aylık dalga 2026-06 ayında bitti (+%438); yolda en kötü düşüş %50. 2025 tarife düşüşünde zirveden nisana −%36, sonraki 5 ayda %131. Şu an pencere zirvesinin %33 altında. Bugünkü temel veri: satış büyümesi %58, brüt marj %59 (5 yıl önce %59), net marj %26, F/K 46, piyasa değeri 53 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Çip test ekipmanı; yapay zekâ çipi test talebi.

### 21. HPE — Hewlett Packard Enterprise Co (Teknoloji)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %281 (3.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %12 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%24. En büyük 12 aylık dalga 2026-09 ayında bitti (+%160); yolda en kötü düşüş %28. 2025 tarife düşüşünde zirveden nisana −%23, sonraki 5 ayda %41. Şu an pencere zirvesinin %8 altında. Bugünkü temel veri: satış büyümesi %27, brüt marj %37 (5 yıl önce %33), net marj %7, F/K 27, piyasa değeri 74 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Sunucu ve ağ; Juniper Networks alımı (2025) ve yapay zekâ ağ talebi.

### 22. KLAC — KLA Corp (Yarı iletken)

- **Kategoriler:** K07 Tek dalga patlama, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %281 (3.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %9 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%30. En büyük 12 aylık dalga 2026-06 ayında bitti (+%237); yolda en kötü düşüş %42. 2025 tarife düşüşünde zirveden nisana −%5, sonraki 5 ayda %60. Şu an pencere zirvesinin %41 altında. Bugünkü temel veri: satış büyümesi %12, brüt marj %62 (5 yıl önce %62), net marj %36, F/K 45, piyasa değeri 219 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Çip üretim denetim ekipmanı; yapay zekâ ve gelişmiş paketleme yatırımları.

### 23. ZYME — Zymeworks Inc (Biyoteknoloji)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş
- **Veriden hikâye:** 3 yılda %264 (3.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %68 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%62. En büyük 12 aylık dalga 2026-05 ayında bitti (+%120); yolda en kötü düşüş %29. 2025 tarife düşüşünde zirveden nisana −%11, sonraki 5 ayda %67. Şu an pencere zirvesinin %13 altında. Bugünkü temel veri: satış büyümesi %-61, net marj %-404, piyasa değeri 2 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Biyoteknoloji; klinik veri ve ortaklık haberlerine bağlı olduğunu tahmin ediyorum (belirsiz).

### 24. GE — General Electric Co (Havacılık ve savunma)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor
- **Veriden hikâye:** 3 yılda %259 (3.1 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %5 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%34. En büyük 12 aylık dalga 2024-10 ayında bitti (+%98); yolda en kötü düşüş %17. 2025 tarife düşüşünde zirveden nisana −%3, sonraki 5 ayda %26. Şu an pencere zirvesinin %17 altında. Bugünkü temel veri: satış büyümesi %22, brüt marj %34 (5 yıl önce %31), net marj %18, F/K 36, piyasa değeri 324 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** GE Vernova ayrılmasından (Nisan 2024) sonra saf havacılık şirketi; uçak motoru servis geliri (K34, hafızadan).

### 25. ANET — Arista Networks Inc (İletişim ağı)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %253 (3.0 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %0 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%21. En büyük 12 aylık dalga 2026-04 ayında bitti (+%110); yolda en kötü düşüş %33. 2025 tarife düşüşünde zirveden nisana −%29, sonraki 5 ayda %82. Şu an pencere zirvesinin %13 altında. Bugünkü temel veri: satış büyümesi %33, brüt marj %63 (5 yıl önce %63), net marj %38, F/K 55, piyasa değeri 223 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Veri merkezi ağ anahtarları; bulut ve yapay zekâ yatırımları.

### 26. BK —  (bilinmiyor)

- **Kategoriler:** K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor
- **Veriden hikâye:** 3 yılda %235 (2.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %28 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%34. En büyük 12 aylık dalga 2024-10 ayında bitti (+%77); yolda en kötü düşüş %12. 2025 tarife düşüşünde zirveden nisana −%10, sonraki 5 ayda %22. Şu an pencere zirvesinin %12 altında. Bugünkü temel veri: satış büyümesi %285, net marj %21, F/K 16, piyasa değeri 94 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Büyük banka/saklama kuruluşu; faiz ortamı, hizmet gelirleri ve hisse geri alımları (belirsiz).

### 27. FORM — FormFactor Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K07 Tek dalga patlama, K11 Marj iyileşti, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %235 (2.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %26 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%45. En büyük 12 aylık dalga 2026-04 ayında bitti (+%383); yolda en kötü düşüş %54. 2025 tarife düşüşünde zirveden nisana −%30, sonraki 5 ayda %84. Şu an pencere zirvesinin %29 altında. Bugünkü temel veri: satış büyümesi %18, brüt marj %46 (5 yıl önce %40), net marj %13, F/K 77, piyasa değeri 9 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yarı iletken test probe kartları; yapay zekâ bellek (HBM) test talebi.

### 28. CAT — Caterpillar Inc (Makine)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %231 (2.8 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %20 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%21. En büyük 12 aylık dalga 2026-04 ayında bitti (+%188); yolda en kötü düşüş %30. 2025 tarife düşüşünde zirveden nisana −%17, sonraki 5 ayda %66. Şu an pencere zirvesinin %30 altında. Bugünkü temel veri: satış büyümesi %18, brüt marj %35 (5 yıl önce %34), net marj %15, F/K 31, piyasa değeri 337 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** İnşaat/madencilik makineleri; veri merkezi için enerji jeneratörü talebi (belirsiz).

### 29. NEM — Newmont Corporation (Madencilik)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K03 Önceki ayı piyasasından toparlanma, K07 Tek dalga patlama, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %215 (2.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %53 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%32. En büyük 12 aylık dalga 2026-02 ayında bitti (+%203); yolda en kötü düşüş %30. 2025 tarife düşüşünde zirveden nisana %23, sonraki 5 ayda %54. Şu an pencere zirvesinin %9 altında. Bugünkü temel veri: satış büyümesi %25, brüt marj %69 (5 yıl önce %52), net marj %33, F/K 15, piyasa değeri 125 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Altın madencisi; altın fiyatı yükselişi ve maliyet disiplini.

### 30. FFIV — F5 Inc (İletişim ağı)

- **Kategoriler:** K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %214 (2.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %38 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%41. En büyük 12 aylık dalga 2026-10 ayında bitti (+%88); yolda en kötü düşüş %26. 2025 tarife düşüşünde zirveden nisana −%11, sonraki 5 ayda −%11. Şu an pencere zirvesinin %0 altında. Bugünkü temel veri: satış büyümesi %9, brüt marj %82 (5 yıl önce %80), net marj %22, F/K 34, piyasa değeri 25 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Ağ ve uygulama güvenliği yazılımı; yapay zekâ trafiği ve yenileme döngüsü (belirsiz).

### 31. MPC — Marathon Petroleum Corp (Enerji)

- **Kategoriler:** K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %213 (2.6 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %0 altındaydı; 2022'de (Ara 2021→Eyl 2022) %55. En büyük 12 aylık dalga 2026-10 ayında bitti (+%143); yolda en kötü düşüş %32. 2025 tarife düşüşünde zirveden nisana −%9, sonraki 5 ayda %21. Şu an pencere zirvesinin %0 altında. Bugünkü temel veri: satış büyümesi %16, brüt marj %14 (5 yıl önce %12), net marj %5, F/K 16, piyasa değeri 134 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Rafineri; rafineri marjları ve hisse geri alımları (belirsiz).

### 32. AMAT — Applied Materials Inc (Yarı iletken)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K07 Tek dalga patlama, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %212 (2.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %16 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%48. En büyük 12 aylık dalga 2026-06 ayında bitti (+%295); yolda en kötü düşüş %43. 2025 tarife düşüşünde zirveden nisana −%16, sonraki 5 ayda %49. Şu an pencere zirvesinin %43 altında. Bugünkü temel veri: satış büyümesi %8, brüt marj %49 (5 yıl önce %47), net marj %30, F/K 35, piyasa değeri 325 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Çip üretim ekipmanı; yapay zekâ ve bellek yatırım döngüsü.

### 33. C — Citigroup Inc (Bankacılık)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor
- **Veriden hikâye:** 3 yılda %212 (2.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %43 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%31. En büyük 12 aylık dalga 2026-04 ayında bitti (+%87); yolda en kötü düşüş %16. 2025 tarife düşüşünde zirveden nisana −%16, sonraki 5 ayda %34. Şu an pencere zirvesinin %12 altında. Bugünkü temel veri: satış büyümesi %99, net marj %17, F/K 11, piyasa değeri 204 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Büyük banka; yeniden yapılanma ve getiri hedefleri (belirsiz).

### 34. PANW — Palo Alto Networks Inc (Teknoloji)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K08 Çok yıllı yürüyüş, K10 Satışlar güçlü büyüyor, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %209 (2.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %5 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%12. En büyük 12 aylık dalga 2026-08 ayında bitti (+%101); yolda en kötü düşüş %32. 2025 tarife düşüşünde zirveden nisana −%2, sonraki 5 ayda %14. Şu an pencere zirvesinin %6 altında. Bugünkü temel veri: satış büyümesi %24, brüt marj %70 (5 yıl önce %72), net marj %3, F/K 911, piyasa değeri 280 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Siber güvenlik platformu; yapay zekâ güvenlik talebi ve ürün birleştirme.

### 35. EBAY — eBay Inc (Perakende)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş
- **Veriden hikâye:** 3 yılda %207 (2.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %49 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%45. En büyük 12 aylık dalga 2025-07 ayında bitti (+%65); yolda en kötü düşüş %12. 2025 tarife düşüşünde zirveden nisana %1, sonraki 5 ayda %11. Şu an pencere zirvesinin %0 altında. Bugünkü temel veri: satış büyümesi %15, brüt marj %72 (5 yıl önce %73), net marj %18, F/K 24, piyasa değeri 53 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Pazar yeri; maliyet disiplini, kârlılık ve hisse geri alımları (belirsiz).

### 36. EXPE — Expedia Group Inc (Seyahat ve eğlence)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K03 Önceki ayı piyasasından toparlanma, K08 Çok yıllı yürüyüş, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %206 (2.5 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %51 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%48. En büyük 12 aylık dalga 2024-10 ayında bitti (+%64); yolda en kötü düşüş %26. 2025 tarife düşüşünde zirveden nisana −%21, sonraki 5 ayda %32. Şu an pencere zirvesinin %8 altında. Bugünkü temel veri: satış büyümesi %12, brüt marj %90 (5 yıl önce %87), net marj %13, F/K 17, piyasa değeri 35 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Seyahat; maliyet kesintisi ve verimlilik (belirsiz).

### 37. JCI — Johnson Controls International PLC (Bina sistemleri)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %201 (2.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %40 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%39. En büyük 12 aylık dalga 2026-04 ayında bitti (+%74); yolda en kötü düşüş %9. 2025 tarife düşüşünde zirveden nisana −%2, sonraki 5 ayda %13. Şu an pencere zirvesinin %1 altında. Bugünkü temel veri: satış büyümesi %5, brüt marj %43 (5 yıl önce %34), net marj %17, F/K 25, piyasa değeri 89 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Bina sistemleri; veri merkezi soğutma talebi.

### 38. FTNT — Fortinet Inc (Teknoloji)

- **Kategoriler:** K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %200 (2.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %26 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%32. En büyük 12 aylık dalga 2026-08 ayında bitti (+%117); yolda en kötü düşüş %27. 2025 tarife düşüşünde zirveden nisana −%4, sonraki 5 ayda −%15. Şu an pencere zirvesinin %4 altında. Bugünkü temel veri: satış büyümesi %19, brüt marj %80 (5 yıl önce %78), net marj %28, F/K 59, piyasa değeri 125 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Siber güvenlik; güvenlik duvarı yenileme döngüsü.

### 39. GM — General Motors Co (Otomotiv)

- **Kategoriler:** K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %198 (2.4 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %52 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%45. En büyük 12 aylık dalga 2024-10 ayında bitti (+%80); yolda en kötü düşüş %19. 2025 tarife düşüşünde zirveden nisana −%9, sonraki 5 ayda %39. Şu an pencere zirvesinin %6 altında. Bugünkü temel veri: satış büyümesi %-1, brüt marj %6 (5 yıl önce %12), net marj %1, F/K 38, piyasa değeri 74 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Otomotiv; maliyet disiplini ve hisse geri alımları (belirsiz).

### 40. NTAP — NetApp Inc (Teknoloji)

- **Kategoriler:** K08 Çok yıllı yürüyüş, K19 Son bilançoda beklentiyi aştı, K21 Tema dalgası
- **Veriden hikâye:** 3 yılda %185 (2.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %21 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%33. En büyük 12 aylık dalga 2026-09 ayında bitti (+%77); yolda en kötü düşüş %32. 2025 tarife düşüşünde zirveden nisana −%26, sonraki 5 ayda %19. Şu an pencere zirvesinin %1 altında. Bugünkü temel veri: satış büyümesi %12, brüt marj %71 (5 yıl önce %69), net marj %19, F/K 28, piyasa değeri 40 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Depolama; yapay zekâ veri hazırlığı talebi.

### 41. KEYS — Keysight Technologies Inc (Elektrik ekipmanı)

- **Kategoriler:** K03 Önceki ayı piyasasından toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K19 Son bilançoda beklentiyi aştı
- **Veriden hikâye:** 3 yılda %180 (2.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %41 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%24. En büyük 12 aylık dalga 2026-04 ayında bitti (+%141); yolda en kötü düşüş %18. 2025 tarife düşüşünde zirveden nisana −%18, sonraki 5 ayda %17. Şu an pencere zirvesinin %6 altında. Bugünkü temel veri: satış büyümesi %26, brüt marj %65 (5 yıl önce %63), net marj %19, F/K 45, piyasa değeri 56 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Test ve ölçüm cihazları; yapay zekâ/veri iletişimi ve savunma.

### 42. CAH — Cardinal Health Inc (Sağlık)

- **Kategoriler:** K02 Şokta dayanıklı (gizli güç), K05 Trend lideri / istikrarlı yürüyüş, K08 Çok yıllı yürüyüş
- **Veriden hikâye:** 3 yılda %179 (2.2 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %4 altındaydı; 2022'de (Ara 2021→Eyl 2022) %30. En büyük 12 aylık dalga 2026-02 ayında bitti (+%77); yolda en kötü düşüş %16. 2025 tarife düşüşünde zirveden nisana %9, sonraki 5 ayda %24. Şu an pencere zirvesinin %0 altında. Bugünkü temel veri: satış büyümesi %14, brüt marj %4 (5 yıl önce %4), net marj %1, F/K 34, piyasa değeri 58 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** İlaç dağıtımı; kârlılık ve hisse geri alımları (belirsiz).

### 43. GOOGL — Alphabet Inc (Medya/internet)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K05 Trend lideri / istikrarlı yürüyüş, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %177 (2.1 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %16 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%34. En büyük 12 aylık dalga 2026-04 ayında bitti (+%142); yolda en kötü düşüş %24. 2025 tarife düşüşünde zirveden nisana −%22, sonraki 5 ayda %64. Şu an pencere zirvesinin %11 altında. Bugünkü temel veri: satış büyümesi %20, brüt marj %61 (5 yıl önce %57), net marj %55, F/K 17, piyasa değeri 4,228 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ endişelerinden toparlanma ve bulut büyümesi. (GOOG aynı şirketin ikinci hisse sınıfı.)

### 44. GOOG — Alphabet Inc (Medya/internet)

- **Kategoriler:** K01 Dışsal şoktan toparlanma, K10 Satışlar güçlü büyüyor, K11 Marj iyileşti
- **Veriden hikâye:** 3 yılda %171 (2.1 kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %15 altındaydı; 2022'de (Ara 2021→Eyl 2022) −%34. En büyük 12 aylık dalga 2026-04 ayında bitti (+%137); yolda en kötü düşüş %24. 2025 tarife düşüşünde zirveden nisana −%22, sonraki 5 ayda %63. Şu an pencere zirvesinin %11 altında. Bugünkü temel veri: satış büyümesi %20, brüt marj %61 (5 yıl önce %57), net marj %55, F/K 17, piyasa değeri 4,228 milyar $.
- **Hafızaya göre arka plan (doğrulanmadı):** Yapay zekâ endişelerinden toparlanma ve bulut büyümesi. (GOOG aynı şirketin ikinci hisse sınıfı.)

## 5. Bu çalışmadan ne çıkar, ne çıkmaz

**Çıkan:**
- Kazananların ortak paydası bir **tema** (yapay zekâ altyapısı) ve **önceki ayı piyasasında ezilmiş olmak**. Tek tek şirket hikâyeleri farklı olsa da ana dalga aynı.
- "Şokta düşenin sonra çok toparlaması" kazananların yarısında var; "şokta dayanıklılık" ve "ucuzluk" kazananları ayırmıyor.
- Kazananların büyük çoğunluğunun **bugün** güçlü büyüme, yüksek marj ve pahalı değerleme taşıması, yükselişin temelde de karşılık bulduğunu gösteriyor (sonuç olarak).

**Çıkmayan:**
- Bu belirtilerin ileride kazananı **önceden** bulduğu. Bu liste yalnızca geriye dönük açıklama; ileriye dönük test ayrı bir iş.
- Ölçülemeyen 18 kategori (haber, sözleşme, geri alım, nakit, borç…) için hiçbir şey. Senin en çok önem verdiğin tetikleyici olay ve sözleşme bilgisi burada **tamamen eksik**.
- Gerçek S&P 500 için bir sonuç. Örneklem 156 hisse ve kazananlara doğru yanlı.

**Sonraki adım önerisi:** Gerçek S&P 500 üyeleriyle (tarihsel üyelik dahil), haber/sözleşme verisiyle ve her tarihte o gün bilinen mali tabloyla bu eşleştirmeyi tekrarlamak. Ancak o zaman "hangi belirti önceden gelir" sorusuna cevap verilebilir.

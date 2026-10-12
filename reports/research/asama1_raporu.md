# 1. Aşama Raporu — Veri Doğrulama ve Çıkış Senaryoları

- **Tarih:** 12 Ekim 2026
- **Ön kayıt:** v1.1 (commit e756242)
- **Kapsam:** Yalnızca veri. Yeni belirti, model eğitimi, parametre araması yapılmadı.
- **Ayrıntılı çıktılar:** `asama1.json`, `asama1_bolunme.csv` (olay başına), `asama1_cikislar.csv` (şirket başına), `belirti_dogrulama.json`

## Özet karar

**1. aşama tamamlanmadı.** Ön kaydın kuralına göre açıklanamayan sapma varken aşama tamamlanmış sayılmaz; bölünme kontrolleri eşikleri geçemedi. Doğrulama üç gerçek kod hatası buldu ve düzeltti; ancak çerçeve bu düzeltmelerin tamamıyla henüz yeniden kurulmadı. Dört karar senden bekleniyor (sonda).

| Grup | Durum |
|---|---|
| Veri bütünlüğü | ⚠️ Kalemler ve oranlar geçti (iki hata düzeltildikten sonra); bölünme kontrolleri geçmedi; hisse sayısı yedeği karar bekliyor |
| Zamansal bütünlük | ✅ Geçti |
| Örneklem bütünlüğü | ⚠️ Eksik veri sistematik; çıkış fiyatı varsayımı evren getirisini yılda 4,6 puana kadar değiştiriyor |
| İstatistiksel uygulama | ✅ Geçti |

## Doğrulamanın bulduğu ve düzelttiği kod hataları

| # | Hata | Etkisi | Düzeltme | Doğrulama |
|---|---|---|---|---|
| 1 | Bölünmeden sonra hisse sayısı eski kalıyordu | Piyasa değeri bölünme oranı kadar küçük (NVDA 2024: 2.979 → 304 mr $); F/K, defter/fiyat, temettü verimi, büyüklük bozuk | Hisse sayısı rapordan sonraki bölünme oranıyla düzeltilir | 6/6 bilinen bölünme; bölünmesiz hisselerin %99,8'inde değer değişmedi |
| 2 | Hisse sayısı değişimi ve Piotroski'nin hisse kriteri bölünmeyi ayıklamıyordu | Bölünme "%900 hisse ihracı" görünüyordu | 52 hafta önceki sayı aradaki bölünme oranıyla çarpılır | NVDA −%0,1, AAPL −%6 (bilinen değerler 22/22) |
| 3 | Finansal kalem seçiminde öncelik sırası uygulanmıyordu | Özsermaye, net kâr ve gelirde bazen yanlış kalem (azınlık payı dahil özsermaye vb.) | Öncelik sırası uygulandı | Kazanç getirisi %92 → %99,5; defter/fiyat %95,5 → %99,5 |

Ek olarak üç veri eksiği giderildi: arşive hiç indirilmemiş 4 XBRL kalemi (temettü, amortisman, azınlık paylı özsermaye) ve faiz gideri kalemleri indirildi.

**Çerçevenin durumu:** Mevcut çerçeve hata 1 ve eksik kalemlerle kuruldu; hata 2 ve 3 kodda düzeltildi ama çerçeveye yansıtma yaması bellek yetersizliğinden çalışmadı. Çerçeve, kararlarından sonra bir kez daha baştan kurulmalı.

## 1. Veri bütünlüğü

| Kontrol | Beklenen | Gerçekleşen | Başarısız | Neden | Çözüm |
|---|---|---|---|---|---|
| 10-K kalemleri (5 şirket × 2 yıl) | ±%0,5 | 48/48 | 0 | — | — (sınır: 5 şirketlik örnek tüm veriyi kanıtlamaz) |
| Oranlar, bağımsız yeniden hesap (5 oran × 200) | ≥ %99 ±%1 | Brüt marj %100, cari oran %100, faaliyet marjı %99,0, kazanç getirisi %99,5, defter/fiyat %99,5 | 4 kayıt | 3 yabancı şirket (20-F) aynı kalemi hem yerel parayla hem dolarla bildiriyor; bizim kodumuz doları alıyor (doğru), bağımsız kontrolüm para birimine bakmadığı için yerel parayı aldı | Kontrolün kusuru; veri doğru |
| Bilinen değerler (AAPL, MSFT, KO, XOM, NVDA) | ±%35 (T3) | 22/22 | 0 | — | — |
| **Bölünmeler** (olay başına, ayrıntı aşağıda) | ≥ %99 | Birçok kontrolde altında | bkz. tablo | Karışık: gerçek hata + yöntem kusuru + kriter kusuru | Karar 3 ve 4 |
| Hisse sayısı yedeği (ağırlıklı ortalama) | — | 807 şirket, çerçevenin %9,2'si | — | Ölçüm amacına uymuyor | Karar 1 |
| Borç tanımı | — | Uzun vadeli toplam borç bulunursa kısa vadeli kısım iki kez eklenebiliyor | — | Tanım hatası | Karar 2 |

### Bölünmeler: olay türüne göre

3.434 olay (2010 →), her biri `asama1_bolunme.csv`'de.

| Tür | Olay | Tarih doğru | Düzeltilmiş fiyatta sıçrama yok | (a) hisse oranı ±%1 | (b) piyasa değeri sürekliliği ≤ 2 puan | (c) ilk kapak sayısı ±%2 |
|---|---|---|---|---|---|---|
| Bölünme | 631 | %99,7 | %97,9 | %94,4 | %97,8 | %65,8 |
| Ters bölünme | 2.401 | %98,9 | %89,6 | %97,0 | %98,7 | %28,7 |
| Küçük oranlı düzeltme (ayrılma, hisse temettüsü) | 395 | %93,1 | %99,5 | uygulanmaz | %15,8 | %53,0 |
| Aşırı oranlı kayıt (< 1/1000) | 7 | — | — | — | — | — |

Başarısızlıkların açıklaması:
1. **Gerçek hata (13 olay):** Hisse sayısı düzeltmesi hiç tetiklenmemiş, piyasa değeri bölünme oranı kadar sıçrıyor (ör. AMPG 2021 20'ye 1 ters bölünme: 12,5 kat; CRE 2026: 8,7 kat; AMTB 2018: 1,9 kat).
2. **Yöntem kusuru (65 olay, %1–8):** Düzeltme oranı, düzeltilmiş/ham fiyat oranından türetiliyor. Bu oran temettü düzeltmesini de içerdiği için raporundan bu yana biriken temettü kayması bölünme anında hisse sayısına ekleniyor. Yüksek temettülü şirketlerde (GYO benzeri: ARR, CIM, BGC, CMCT) belirgin. Toplam 78 olay, 67 hisse; her biri en çok bir sonraki rapora kadar (~13 hafta) etkili.
3. **Kriter kusuru (c):** Ters bölünme yapan şirketler çoğunlukla hemen ardından yeni hisse çıkarıyor; ilk rapordaki sayı bizim düzeltilmiş sayımızdan medyan %17 fazla. Bu gerçek bir ekonomik değişim. ±%2 kriteri bu durumu hata sayıyor; ön kayıtta yeniden tanımlanmalı.
4. **Küçük oranlı düzeltmeler:** Yahoo ayrılmaları da (ADP–CDK 2014, AIV 2020) "bölünme" diye kaydediyor. Ayrılmada piyasa değerinin düşmesi gerçek (değer yeni şirkete geçiyor). Hisse temettüsünde ise hisse sayısı artar ama biz düzeltmiyoruz; piyasa değeri bir sonraki rapora kadar %5 kadar düşük kalabilir.
5. **Bölünmesiz hisseler:** 2,71 milyon hücrenin 6.568'inde (%0,24) düzeltme devreye girmiş. Büyük olasılıkla FTD fiyatlarındaki tahmini ters bölünmelerden; doğrulanmalı.
6. **Aşırı oranlı 7 kayıt** (ör. ABVC 2015, 5.000'e 1): silinmedi, "doğrulanmalı" olarak işaretli.

### Hisse sayısı: dönem sonu ve ağırlıklı ortalama

| Ölçü | Değer |
|---|---|
| İkisinin de bulunduğu | 10.171 şirket, 181.486 rapor |
| Göreli fark (ağırlıklı / dönem sonu − 1) | medyan −%0,3; %77'si ±%5 içinde; %10,5'i %20'den fazla; uçlarda birim hatası (10¹¹ kat) |
| Büyüklüğe göre medyan mutlak fark | en küçük dilim %1,2 → en büyük dilim %0,6 |
| Sermaye hareketine göre | geri alım %2,0; durağan %0,4; ihraç %3,2 |
| Yedeği kullanan | 807 şirket; 53.530 satır (%9,2) |
| Etkilenen belirtiler | büyüklük, kazanç getirisi, serbest nakit getirisi, defter/fiyat, satış/fiyat, FAVÖK/FD, temettü verimi, nakit/piyasa, Altman Z, hisse sayısı değişimi, Piotroski, geri alım, içeriden alım tutarı, devralma olasılığı |
| Simülasyon: ağırlıklı ortalama kullanılsaydı piyasa değeri sırası | medyan 0,3–1,0 yüzdelik puan kayma |

## 2. Zamansal bütünlük ✅

| Kontrol | Beklenen | Gerçekleşen |
|---|---|---|
| Getiri pencereleri | Çakışma yok | 55 dönem, 0 çakışma (51 × 13 hafta, 3 × 14, 1 × 12); sabit 13 hafta kullanılsaydı 1 çakışma olurdu |
| Veri kesimi | Fiyat: Cuma kapanışı; SEC: Perşembe gün sonu | Tablo `asama1.json → tarih` |
| Zamanlama (yapay olaylar) | Kabulden önce görünmez | 6/6 |
| Sızıntı (sonraki haftayla olağan dışı IC) | Yok | 148/148 belirti temiz |

Pencere çakışması ve veri sızıntısı ayrı ayrı sınandı.

## 3. Örneklem bütünlüğü ⚠️

**Eksik veri sistematik.** 148 belirtiden 8'inin doluluğu fiyat dilimine göre 30 puandan fazla değişiyor. Hepsi hacim ya da günlük fiyat gerektiren belirtiler ve hepsi düşük fiyatlı hisselerde az dolu:

| Belirti | En düşük fiyat dilimi | En yüksek fiyat dilimi | En kötü yıl |
|---|---|---|---|
| likidite | %44 | %83 | %43 |
| hacim_artisi, kirilim | %43 | %83 | %42 |
| max_gunluk_1a, ivol_3a, fip | %43–45 | %82–83 | %39–40 |
| sue_fiyat | %52 | %84 | %20 |
| geri_alim_getirisi | %16 | %53 | %5 |

Neden: borsadan çıkmış hisselerin çoğunun günlük fiyat ve hacmi yok (fiyatları seyrek FTD kayıtlarından). Bu, modelin düşük fiyatlı ve sonradan borsadan çıkan hisseleri sistematik olarak daha az bilgiyle değerlendirdiği anlamına gelir.

**Çıkışlar** (5.118 şirket; `asama1_cikislar.csv`):

| | D: İflas | E: Diğer | Toplam |
|---|---|---|---|
| A: günlük fiyatla doğrulandı | 10 | 232 | 242 (%4,7) |
| B: FTD kaydıyla doğrulandı | 400 | 4.253 | 4.653 (%90,9) |
| C: kaynak doğrulanamadı | 35 | 188 | 223 (%4,4) |

- **Tolerans kuralı:** panelin son işlem fiyatı (yuvarlanmamış) ile aday kaydın fiyatı arasında ±%1; aday kayıt son fiyat haftası ya da önceki 6 hafta içinde.
- **Taşıma:** Panel son gerçek fiyatı çıkışa kadar taşıyor. Kaynak kaydı son haftada 1.387 şirkette, 1 hafta önce 1.931 şirkette, 2–4 hafta önce 1.576 şirkette.
- **Çoklu aday:** 3.657 şirkette birden çok aday kayıt uydu (fiyat sabit kaldığı için); 100 şirkette hem günlük fiyat hem FTD uydu.
- **Veri sınırları:**
  - C grubunda veri eksikliği ile gerçek ekonomik kayıp ayırt edilemiyor.
  - E içinde satın alma ile borsadan atılma ayrılamıyor.
  - İlk sınıflandırma denemesi yalnızca son haftaya baktığı için C'yi %73 buldu; panelin fiyat taşıması fark edilince pencere 6 haftaya genişletildi.

**Senaryoların evren düzeyinde etkisi** (≥1 $ evren, eşit ağırlık, 2013–2024; model yok):

| Değiştirilen kayıtlar | S1: son fiyat | S2: × 0,5 | S3: 0 |
|---|---|---|---|
| B + C | %9,80 | %7,46 | %5,17 |
| Yalnızca B | %9,80 | %7,47 | %5,17 |
| Yalnızca C | %9,80 | %9,80 | %9,79 |

- Her çeyrekte evrenin ~%1'i (≈51 hisse) borsadan çıkıyor; bunların neredeyse tamamı B grubunda.
- Çıkış fiyatı varsayımı evren getirisini yılda 4,6 puana kadar değiştiriyor.
- Ön kayıttaki ücretli veri kuralı (portföy düzeyinde 3 puan) 3a aşamasında uygulanacak. Evren düzeyindeki bu duyarlılık, kuralın tetiklenme ihtimalinin yüksek olduğunu gösteriyor.

## 4. İstatistiksel uygulama ✅

| Kontrol | Beklenen | Gerçekleşen |
|---|---|---|
| Newey–West | Matris uygulaması = bağımsız döngülü uygulama | Elle örnek + 71 rastgele durum (gecikme 0–6, gözlem 8–80, 1–6 açıklayıcı): hepsi aynı |
| Tutarlılık (çerçeve ↔ kaynak) | Spearman ≥ 0,99; olaylarda ≥ %99 | 82/82 |
| Bağımsız hesap (günlük fiyattan) | Spearman ≥ 0,90 | 6/6 (fiyat_seviyesi testi Yahoo'nun bölünme düzeltmeli kapanışı yüzünden ilk koşuda kaldı; test düzeltildi, sonuç 1,000) |
| Yön | Doğru yön | 4/4 |

Sınır: Newey–West kontrolü uygulamanın formülle tutarlılığını gösterir; çok küçük örneklemde HAC hatalarının kendisi yanlı olabilir.

## Karar bekleyen konular

1. **Hisse sayısı yedeği (807 şirket, satırların %9,2'si).**
   - Seçenekler: (a) kaldır, bu şirketlerde değerleme belirtileri boş kalır; (b) koru; (c) net kâr ÷ hisse başına kâr ile çapraz kontrol edip yalnızca tutarlı olanları koru.
   - Önerim (a): ön kayıt dönem sonu sayısını tanımlıyor ve birim hatası örnekleri var.
2. **Borç tanımı.** Uzun vadeli toplam borç kalemi bulunursa kısa vadeli kısım ayrıca eklenmesin. Önerim: düzelt.
3. **Bölünme yöntemi.**
   - Düzeltme oranı fiyat oranından değil Yahoo'nun bölünme kayıtlarından alınsın; temettü kayması ortadan kalkar.
   - Tetiklenmeyen 13 olay ve bölünmesiz hisselerde değişen %0,24 hücre ayrıca incelensin.
   - Önerim: uygula, ardından bölünme kontrollerini yeniden koş.
4. **Ön kayıt v1.2 (gerekçeli):**
   - (c) kontrolü ters bölünmelerde ihraç etkisini hata sayıyor. Yalnızca bölünme ile ilk rapor arasında ihraç belgesi (S-1/S-3/424B) olmayan olaylara uygulansın.
   - Ayrılmalar ve hisse temettüleri (küçük oranlı düzeltmeler) kabul hesabından çıkarılıp ayrı raporlansın.

Kararlarından sonra: çerçeve tüm düzeltmelerle bir kez baştan kurulur, 1. aşama kontrolleri tekrar koşulur ve bu rapor güncellenir. 2. aşamaya ancak ondan sonra ve onayınla geçilir.

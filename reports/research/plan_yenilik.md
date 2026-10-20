# Plan yenilik — Analiz Radarı'nda yapılacak değişiklikler

**Tarih:** 20 Ekim 2026. **Kaynak:** `EN_COK_KAYBETTIREN_HISSE_SEBEPLERI.md` ve `EN_COK_KAZANDIRAN_HISSE_SEBEPLERI.md`.
**Durum:** karar verildi, uygulanmadı. Hiçbir eşik henüz sabitlenmedi.

## Çıkarılan sonuç (kullanıcı kararı)
**Model, kazananı kaybedenden ayıramıyor.** Son 3 yılda her çeyrek modelin 10'u içinden en çok kaybettiren 12 hissenin 9'unda, en çok kazandıranlarla aynı 4 işaretin hepsi vardı. Mevcut 6 işaret "iyi görünen" hisseleri buluyor; hangisinin çökeceğini söyleyemiyor. Bu yüzden ayar değişecek.

## Değişiklikler

### 1. Küçük şirketler elenecek (kural)
- Bulgu: 12 kaybedenin 6'sı 2 Mr$'ın altındaydı (ortadaki 2,3 Mr$; tüm seçimlerde ortadaki yaklaşık 4,4 Mr$). Büyüklük ile 3 aylık getiri arasındaki sıra ilişkisi +0,13.
- Karar: evrendeki piyasa değeri alt sınırı yükseltilecek (şimdi 500 M$).
- **Eşik açık:** yeni alt sınır (ör. 1, 2 ya da 3 Mr$) yalnızca **2013–2022** verisiyle ölçülüp sabitlenecek, sonra 2023–2026'da denenecek. Ölçüt: eşiğin kazananları ne kadar kaybettirdiği ve kaybedenleri ne kadar elediği (plan bölüm 3'teki karar kuralı: kazananı ≥ %90 koru, kaybedeni ≥ 2× daha sık ele, ilk 10'un medyan fazla getirisini düşürme).

### 2. Çok yükselmiş hisseler için düşüş uyarısı (kural; otomatik ret değil)
- Bulgu: LUNR (son 26 haftada +%429), IDR (+%209), LIF (+%193), LINC (+%117), TSSI (+%105) en çok kaybettirenler arasındaydı. 120 seçimde son 26 haftalık getiri ile sonraki 3 ay arasındaki sıra ilişkisi −0,17 (en güçlü negatif ilişki). Ama en iyi seçimlerde de benzer yükselmiş hisseler vardı.
- Karar: son 26 haftada çok yükselmiş hisseler kartta ve listede "Dikkat: çok yükselmiş, geri çekilme riski" uyarısı alacak; listeden çıkarılmayacak, yalnızca uyarı.
- **Eşik açık:** "çok yükselmiş" sınırı (ör. 26 haftada +%100 / +%150 / +%200) 2013–2022'de ölçülüp sabitlenecek.
- Not: bu madde "düşen hisseler için uyarı niteliğinde kural" talimatının yorumudur: uyarı, düşme olasılığı yüksek görünen (aşırı yükselmiş) hisseler içindir. Farklı bir niyet varsa düzeltilecek.

### 3. Mevcut uyarıların durumu (kayıt)
- Bulgu: uyarı taşıyan 43 seçimin 3 aylık ortalama getirisi +%8,8; taşımayan 77'ninki +%4,7. Yani mevcut uyarılar (hisse satışı, nakit sıkıntısı, geç rapor, devamlılık şüphesi…) kaybedeni ayırmıyor. 12 kaybedenin 5'inde uyarı vardı. Hisse satışı olan 35 seçimin %20'si −%20'den fazla kaybetti (tüm seçimlerde %25).
- Karar: bu uyarılar **uyarı olarak kalır**, otomatik elemede kullanılmaz (2013–2022 ölçümü de zaten ret kuralını geçmemişti). Kartlarda "tek başına ret sebebi değil" notu sürer.

## Sıradaki adım
1. 2013–2022'de büyüklük ve 26 haftalık yükseliş için eşik taraması (önceden yazılmış kısa aday listesiyle; deneme sayısı kayda geçer).
2. Eşikler dondurulup `arac_ayar.json` yenilenir ve commit edilir.
3. 2023–2026 ikinci bakış olarak yeniden ölçülür; asıl temiz sınav bugünden sonra her cuma kilitlenen listelerdir.
4. Kartlara yeni uyarı ve "Neden almamalı?" cümlesi eklenir.

## Bilinen sınırlar
- Kaybeden ve kazanan örnek sayıları küçük (12 en iyi, 12 en kötü, 120 seçim; ilişkilerin hata payı ±0,09). Bu bir ipucu listesi; kuralların değeri 2013–2022 ölçümünde belli olacak.
- 2023–2026 dönemi bir kez hatalı veriyle açıldı ve sonuçları görüldü; yeni kuralların ayarı bu sonuçlara göre değil, yalnızca 2013–2022'ye göre yapılacak.

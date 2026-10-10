# Veri Sağlık Raporu — 2026-10-10 14:33 UTC

🟢 12 kullanılabilir · 🟡 5 dikkat · 🔴 0 kullanılamaz

Kırmızı kaynaklar o hafta puanlamada kullanılmaz. Sınıf: 1 = resmî, 2 = güvenilir ama dolaylı.

| Kaynak | Sınıf | Yol | Durum | Süre | İstek |
|---|---|---|---|---|---|
| [Hisse evreni (Nasdaq + SEC)](#universe) | 1 | 1, 2, 3, 4 | 🟢 Kullanılabilir | 0.5 sn | 2 |
| [SEC günlük dosya indeksi](#sec_index) | 1 | 1, 3 | 🟢 Kullanılabilir | 0.7 sn | 5 |
| [SEC şirket dosya geçmişi](#sec_submissions) | 1 | 1, 3 | 🟢 Kullanılabilir | 2.0 sn | 15 |
| [SEC XBRL finansal verileri](#sec_xbrl) | 1 | 1 | 🟡 Dikkat | 6.7 sn | 23 |
| [SEC Form 4 (içeriden işlemler)](#sec_form4) | 1 | 3 | 🟢 Kullanılabilir | 7.7 sn | 61 |
| [SEC 13F (fon pozisyonları)](#sec_13f) | 1 | 3 | 🟢 Kullanılabilir | 0.7 sn | 6 |
| [FINRA açığa satış hacmi](#finra) | 1 | 3 | 🟢 Kullanılabilir | 0.1 sn | 1 |
| [USAspending devlet sözleşmeleri](#usaspending) | 1 | 3 | 🟢 Kullanılabilir | 1.0 sn | 4 |
| [USPTO patentleri (PatentsView)](#uspto) | 1 | 3 | 🟡 Dikkat | 0.0 sn | 0 |
| [Günlük fiyatlar (Yahoo ↔ Nasdaq)](#prices) | 2 | 1, 2, 3, 4 | 🟡 Dikkat | 38.1 sn | 38 |
| [FRED makro ve emtia serileri](#fred) | 1 | 1, 4 | 🟢 Kullanılabilir | 1.5 sn | 6 |
| [GDELT haber akışı](#gdelt) | 2 | 2, 4 | 🟢 Kullanılabilir | 21.2 sn | 5 |
| [Wikipedia ilgisi + Wikidata eşleştirmesi](#wikipedia) | 2 | 2, 4 | 🟡 Dikkat | 15.0 sn | 6 |
| [Hacker News](#hackernews) | 2 | 2, 4 | 🟢 Kullanılabilir | 0.7 sn | 2 |
| [Google News RSS](#gnews) | 2 | 2, 4 | 🟢 Kullanılabilir | 1.5 sn | 3 |
| [Reddit](#reddit) | 2 | 2, 4 | 🟡 Dikkat | 4.1 sn | 3 |
| [GitHub aktivitesi](#github) | 2 | 3 | 🟢 Kullanılabilir | 1.7 sn | 3 |

<a id="universe"></a>
## 🟢 Hisse evreni (Nasdaq + SEC)

| Kontrol | Durum | Detay |
|---|---|---|
| Nasdaq adi hisse sayısı | 🟢 | 3,434 (beklenen 2,500–4,500) |
| Nasdaq listesi güncelliği | 🟢 | en son kayıt 2026-10-09, 0.7 gün önce (sınır 4) |
| Bilinen hisseler listede | 🟢 | 4/4 bulundu |
| SEC CIK eşleşme oranı | 🟢 | 3424/3434 = %99.7 adi hisse |
| Doğrulanmış CIK değerleri | 🟢 | AAPL, MSFT, NVDA, AMZN doğru |
| Çapraz kontrol: SEC'te 'Nasdaq' görünenler Nasdaq listesinde | 🟢 | 4337/4376 = %99.1 |
| Finansal durum dağılımı (risk sinyali) | ℹ️ | normal: 3133, yetersiz (deficient): 281, geciken rapor (delinquent): 17, yetersiz+geciken: 3 |
| Yeni listelenen / çıkan hisseler (önceki çalışmaya göre) | ℹ️ | +0 yeni: [] \| -0 çıkan: [] |

<a id="sec_index"></a>
## 🟢 SEC günlük dosya indeksi

| Kontrol | Durum | Detay |
|---|---|---|
| Erişilebilen iş günü sayısı (son 7 iş günü içinde) | 🟢 | 5 (beklenen 4–5) |
| İndeks güncelliği | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 4) |
| 2026-10-05: toplam dosya | 🟢 | 4,886 (beklenen 1,500–15,000) |
| 2026-10-05: Form 4 sayısı | 🟢 | 2,413 (beklenen 300–6,000) |
| 2026-10-05: kullanılan formlar 1 iş günü içinde yayımlanmış | 🟢 | 2815/2815 = %100.0 |
| 2026-10-05: gizli taslak (DRS) — dosyalama ≠ yayım | ℹ️ | 11 kayıt, medyan gecikme 70 gün (geriye dönük testte yayım tarihi esas alınır) |
| 2026-10-06: toplam dosya | 🟢 | 3,501 (beklenen 1,500–15,000) |
| 2026-10-06: Form 4 sayısı | 🟢 | 837 (beklenen 300–6,000) |
| 2026-10-06: kullanılan formlar 1 iş günü içinde yayımlanmış | 🟢 | 1268/1268 = %100.0 |
| 2026-10-06: gizli taslak (DRS) — dosyalama ≠ yayım | ℹ️ | 3 kayıt, medyan gecikme 36 gün (geriye dönük testte yayım tarihi esas alınır) |
| 2026-10-07: toplam dosya | 🟢 | 3,159 (beklenen 1,500–15,000) |
| 2026-10-07: Form 4 sayısı | 🟢 | 660 (beklenen 300–6,000) |
| 2026-10-07: kullanılan formlar 1 iş günü içinde yayımlanmış | 🟢 | 1093/1093 = %100.0 |
| 2026-10-07: gizli taslak (DRS) — dosyalama ≠ yayım | ℹ️ | 5 kayıt, medyan gecikme 99 gün (geriye dönük testte yayım tarihi esas alınır) |
| 2026-10-08: toplam dosya | 🟢 | 3,193 (beklenen 1,500–15,000) |
| 2026-10-08: Form 4 sayısı | 🟢 | 639 (beklenen 300–6,000) |
| 2026-10-08: kullanılan formlar 1 iş günü içinde yayımlanmış | 🟢 | 1106/1106 = %100.0 |
| 2026-10-08: gizli taslak (DRS) — dosyalama ≠ yayım | ℹ️ | 3 kayıt, medyan gecikme 59 gün (geriye dönük testte yayım tarihi esas alınır) |
| 2026-10-09: toplam dosya | 🟢 | 3,216 (beklenen 1,500–15,000) |
| 2026-10-09: Form 4 sayısı | 🟢 | 564 (beklenen 300–6,000) |
| 2026-10-09: kullanılan formlar 1 iş günü içinde yayımlanmış | 🟢 | 1044/1044 = %100.0 |
| 2026-10-09: gizli taslak (DRS) — dosyalama ≠ yayım | ℹ️ | 25 kayıt, medyan gecikme 67 gün (geriye dönük testte yayım tarihi esas alınır) |
| Haftalık form dağılımı | ℹ️ | 4: 5113, 8-K: 907, 13F-HR: 392, SCHEDULE 13D: 58, SCHEDULE 13G: 292, 10-K: 12, 10-Q: 42, S-1: 20, 424B4: 7, NT 10-K: 0 |
| Halka arz hazırlığı (S-1/F-1/424B4) | ℹ️ | 62 dosya; örnek: ['DarkIris Inc.', 'DarkIris Inc.', 'Retension Pharmaceuticals, Inc.', 'Sunshine Biopharma Inc.', 'TRex Bio, Inc.', 'OPAY Ltd', 'vVARDIS Holding AG', 'Kainan Holding Group Ltd'] |

<a id="sec_submissions"></a>
## 🟢 SEC şirket dosya geçmişi

| Kontrol | Durum | Detay |
|---|---|---|
| Çekilen şirket | 🟢 | 15/15 = %100.0 |
| Çapraz kontrol: dosyadaki ticker evrendeki ticker ile aynı | 🟢 | 15/15 = %100.0 |
| Doğrulanmış gerçek: AAPL 10-K 2023-11-03 | 🟢 | bulundu |
| 8-K'larda olay kodu (items) dolu | 🟢 | 1233/1233 = %100.0 |
| Kabul anı ile dosyalama tarihi tutarlı (zaman damgası) | 🟢 | 6754/6755 = %100.0; formlar: {'S-1/A': 1}; örnek: [('S-1/A', '2024-09-03', '2024-08-30T23:09:30.000Z')] |
| Önceki güne tarihlenen gece kabulleri | ℹ️ | 153 dosya — dosyalama tarihi değil kabul anı esas alınır |
| AAPL son dosya güncelliği | 🟢 | en son kayıt 2026-10-08, 2.0 gün önce (sınır 45) |
| Yıllık rapor (10-K/20-F/40-F) bulunan şirket | 🟢 | 15/15 = %100.0 |

<a id="sec_xbrl"></a>
## 🟡 SEC XBRL finansal verileri

| Kontrol | Durum | Detay |
|---|---|---|
| Doğrulanmış gerçek: AAPL geliri (2023-09-30) | 🟢 | okunan 383,285,000,000, beklenen 383,285,000,000 |
| Doğrulanmış gerçek: MSFT geliri (2023-06-30) | 🟢 | okunan 211,915,000,000, beklenen 211,915,000,000 |
| Doğrulanmış gerçek: NVDA geliri (2024-01-28) | 🟢 | okunan 60,922,000,000, beklenen 60,922,000,000 |
| Rastgele şirketlerde temel kalem (varlık/gelir/kâr) bulunan | 🟢 | 19/20 = %95.0 |
| Zaman tutarlılığı: dosyalama tarihi ≥ dönem sonu | 🟢 | 349447/349490 = %100.0 |
| Güncel hisse sayısı (son 200 gün) bulunan | 🟡 | 14/20 = %70.0; eksik/eski: ['PGAC:yok', 'DNMX:2025-12-10', 'CCAQ:yok', 'WENN:yok', 'NUR:yok', 'BID:yok'] |
| Kapsam notu | ℹ️ | 0 şirket IFRS raporluyor (yabancı), 0 şirkette XBRL yok: [] |

<a id="sec_form4"></a>
## 🟢 SEC Form 4 (içeriden işlemler)

| Kontrol | Durum | Detay |
|---|---|---|
| Ayrıştırılan Form 4 | 🟢 | 60/60 = %100.0 |
| Geçerli işlem kodu | 🟢 | 106/106 = %100.0 |
| İşlem tarihi ≤ dosyalama tarihi | 🟢 | 106/106 = %100.0 |
| Hisse adedi > 0 | 🟢 | 106/106 = %100.0 |
| Alım/satışta fiyat > 0 | 🟢 | 48/48 = %100.0 |
| Kod/yön tutarlılığı (P→A, S→D) | 🟢 | 48/48 = %100.0 |
| Ticker dolu | 🟢 | 106/106 = %100.0 |
| İşlem kodu dağılımı (örnek) | ℹ️ | S: 36, A: 24, F: 20, P: 12, M: 11, D: 2, J: 1 |
| Bildirim gecikmesi (gün, medyan / %95) | ℹ️ | 4 / 35 |
| Toplu veri seti sayısı (geriye dönük test için) | 🟢 | 83 (beklenen 40–500) |
| Toplu veri seti örnekleri | ℹ️ | ['/files/datastandardsinnovation/data/insider-transactions-data-sets/2026q2_form345.zip', '/files/datastandardsinnovation/data/insider-transactions-data-sets/2026q3_form345.zip'] … ['/files/structureddata/data/insider-transactions-data-sets/2025q4_form345.zip', '/files/structureddata/data/insider-transactions-data-sets/2026q1_form345.zip'] |

<a id="sec_13f"></a>
## 🟢 SEC 13F (fon pozisyonları)

| Kontrol | Durum | Detay |
|---|---|---|
| Bu hafta gelen 13F-HR | ℹ️ | 392 dosya (çeyrek sonu +45 gün civarında yoğunlaşır) |
| Pozisyon tablosu ayrıştırılan 13F | 🟢 | 5/5 = %100.0 |
| Geçerli CUSIP | 🟢 | 1289/1289 = %100.0 |
| Değer ve adet pozitif | 🟢 | 1289/1289 = %100.0 |
| Toplu veri seti sayısı (geriye dönük test için) | 🟢 | 54 (beklenen 20–500) |
| Toplu veri seti örnekleri | ℹ️ | ['/files/datastandardsinnovation/data/form-13f-data-sets/01jun2026-31aug2026_form13f.zip', '/files/structureddata/data/form-13f-data-sets/01dec2024-28feb2025_form13f.zip'] … ['/files/structureddata/data/form-13f-data-sets/2023q3_form13f.zip', '/files/structureddata/data/form-13f-data-sets/2023q4_form13f.zip'] |

<a id="finra"></a>
## 🟢 FINRA açığa satış hacmi

| Kontrol | Durum | Detay |
|---|---|---|
| Güncellik | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 5) |
| Sembol sayısı | 🟢 | 12,278 (beklenen 5,000–20,000) |
| Açığa satış ≤ toplam hacim | 🟢 | 12278/12278 = %100.0 |
| Evren kapsamı | 🟢 | 3364/3434 = %98.0 |

<a id="usaspending"></a>
## 🟢 USAspending devlet sözleşmeleri

| Kontrol | Durum | Detay |
|---|---|---|
| Veritabanı güncelliği | 🟢 | en son kayıt 2026-10-10, 0.0 gün önce (sınır 10) |
| Palantir: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |
| Microsoft: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |
| Amazon Web Services: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |

<a id="uspto"></a>
## 🟡 USPTO patentleri (PatentsView)

| Kontrol | Durum | Detay |
|---|---|---|
| API anahtarı | 🟡 | PATENTSVIEW_API_KEY yok. Ücretsiz anahtar: https://patentsview.org/apis/keyrequest — alınınca GitHub secret olarak eklenecek |

<a id="prices"></a>
## 🟡 Günlük fiyatlar (Yahoo ↔ Nasdaq)

| Kontrol | Durum | Detay |
|---|---|---|
| Yahoo: veri dönen hisse | 🟢 | 15/15 = %100.0 |
| Nasdaq: veri dönen hisse | 🟢 | 15/15 = %100.0 |
| Çapraz kontrol: en az iki kaynak %0,5 içinde (son 60 gün) | 🟢 | 15/15 = %100.0 |
| yahoo ↔ nasdaq medyan fark | ℹ️ | %0.000 (15 hisse) |
| Tek kaynakta görünen %60+ sıçrama (veri hatası şüphesi) | 🟡 | nasdaq:SHAZ 2025-12-26; nasdaq:SHAZ 2026-02-18 |
| İki kaynağın doğruladığı %60+ hareket (gerçek, risk sinyali) | ℹ️ | yok |
| Fiyat güncelliği (medyan hissenin son barı) | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 5) |
| 5 günden eski son bar (işlem durdurma / likidite riski) | ℹ️ | yok |
| yahoo: NVDA bölünmesi düzeltilmiş | 🟢 | 7→10 Haziran 2024 değişim %0.7 |
| nasdaq: NVDA bölünmesi düzeltilmiş | 🟢 | 7→10 Haziran 2024 değişim %0.7 |
| Borsadan çıkmış hisselerin geçmiş fiyatı | ℹ️ | SIVB (SVB Financial (2023)): yahoo=yok, nasdaq=yok; ATVI (Activision Blizzard (2023)): yahoo=yok, nasdaq=yok; SGEN (Seagen (2023)): yahoo=yok, nasdaq=yok |

<a id="fred"></a>
## 🟢 FRED makro ve emtia serileri

| Kontrol | Durum | Detay |
|---|---|---|
| DCOILWTICO – Ham petrol WTI (günlük): güncellik | 🟢 | en son kayıt 2026-10-06, 4.0 gün önce (sınır 10); 9517 gözlem, başlangıç 1986-01-02 |
| DGS10 – ABD 10 yıllık faiz (günlük): güncellik | 🟢 | en son kayıt 2026-10-08, 2.0 gün önce (sınır 10); 16178 gözlem, başlangıç 1962-01-02 |
| PCOPPUSDM – Bakır fiyatı (aylık, IMF kaynaklı ~3 ay gecikmeli): güncellik | 🟢 | en son kayıt 2026-07-01, 101.0 gün önce (sınır 130); 415 gözlem, başlangıç 1992-01-01 |
| INDPRO – Sanayi üretimi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 70.0 gün önce (sınır 75); 1292 gözlem, başlangıç 1919-01-01 |
| CPIAUCSL – Tüketici fiyat endeksi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 70.0 gün önce (sınır 75); 955 gözlem, başlangıç 1947-01-01 |
| IPG3344S – Yarı iletken üretimi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 70.0 gün önce (sınır 75); 656 gözlem, başlangıç 1972-01-01 |

<a id="gdelt"></a>
## 🟢 GDELT haber akışı

| Kontrol | Durum | Detay |
|---|---|---|
| Ham dosya akışı güncelliği | 🟢 | en son kayıt 2026-10-10, 0.0 gün önce (sınır 0.25) |
| İndirilen dosya bütünlüğü (boyut + MD5) | 🟢 | 3,695,766 bayt, md5 eşleşti |
| 15 dakikalık dosyada makale | 🟢 | 813 (beklenen 500–50,000) |
| Sütun sayısı = 27 | 🟢 | 813/813 = %100.0 |
| Kurum (Organizations) bilgisi olan | 🟢 | 609/813 = %74.9 |
| Ton değeri okunabilen | 🟢 | 813/813 = %100.0 |
| Bu 15 dakikada en çok geçen kurumlar | ℹ️ | united states (48), associated press (44), white house (28), xinhua (21), instagram (21), google (19), facebook (18), cnn (16) |
| Geçmiş veri: 1 Mart 2015 dosyası makale | 🟢 | 1,209 (beklenen 100–50,000) |
| Yardımcı: DOC API zaman serisi | ℹ️ | erişilemedi (HTTP 429); ham dosyalar yeterli |

<a id="wikipedia"></a>
## 🟡 Wikipedia ilgisi + Wikidata eşleştirmesi

| Kontrol | Durum | Detay |
|---|---|---|
| Nvidia: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Nvidia: güncellik | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 3) |
| Apple_Inc.: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Apple_Inc.: güncellik | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 3) |
| Microsoft: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Microsoft: güncellik | 🟢 | en son kayıt 2026-10-09, 1.0 gün önce (sınır 3) |
| Geçmiş veri: Temmuz 2015 gün sayısı | 🟢 | 31 (beklenen 30–31) |
| Eşleşme yolu: Nasdaq kodu / SEC CIK | ℹ️ | kod ile 777, CIK ile 596 |
| Wikipedia makalesi eşleşen Nasdaq hissesi | 🟡 | 870/3434 = %25.3 |
| Eşleştirme kontrolü | 🟢 | NVDA → Nvidia, AAPL → Apple_Inc. |

<a id="hackernews"></a>
## 🟢 Hacker News

| Kontrol | Durum | Detay |
|---|---|---|
| Son 7 gün 'nvidia' haberi | 🟢 | 36 (beklenen 5–100) |
| Güncellik | 🟢 | en son kayıt 2026-10-10, 0.2 gün önce (sınır 2) |
| Geçmiş veri: Ocak 2016 sonuç | 🟢 | 30 (beklenen 1–10,000) |

<a id="gnews"></a>
## 🟢 Google News RSS

| Kontrol | Durum | Detay |
|---|---|---|
| 'Nvidia stock': haber sayısı | 🟢 | 104 (beklenen 20–200) |
| 'Nvidia stock': tarihi okunabilen | 🟢 | 104/104 = %100.0 |
| 'Nvidia stock': güncellik | 🟢 | en son kayıt 2026-10-10, 0.1 gün önce (sınır 2) |
| 'Nvidia stock': tekil başlık | 🟢 | 103/104 = %99.0 |
| 'Apple earnings': haber sayısı | 🟢 | 100 (beklenen 20–200) |
| 'Apple earnings': tarihi okunabilen | 🟢 | 100/100 = %100.0 |
| 'Apple earnings': güncellik | 🟢 | en son kayıt 2026-10-10, 0.1 gün önce (sınır 2) |
| 'Apple earnings': tekil başlık | 🟢 | 98/100 = %98.0 |
| 'Nasdaq IPO': haber sayısı | 🟢 | 100 (beklenen 20–200) |
| 'Nasdaq IPO': tarihi okunabilen | 🟢 | 100/100 = %100.0 |
| 'Nasdaq IPO': güncellik | 🟢 | en son kayıt 2026-10-10, 0.1 gün önce (sınır 2) |
| 'Nasdaq IPO': tekil başlık | 🟢 | 99/100 = %99.0 |

<a id="reddit"></a>
## 🟡 Reddit

| Kontrol | Durum | Detay |
|---|---|---|
| Erişim yöntemi | ℹ️ | kimliksiz; REDDIT_CLIENT_ID/SECRET tanımlanırsa OAuth kullanılır |
| r/stocks | 🟡 | erişilemedi (HTTP 403) — ücretsiz Reddit OAuth uygulaması gerekiyor |
| r/investing | 🟡 | erişilemedi (HTTP 403) — ücretsiz Reddit OAuth uygulaması gerekiyor |
| r/wallstreetbets | 🟡 | erişilemedi (HTTP 403) — ücretsiz Reddit OAuth uygulaması gerekiyor |

<a id="github"></a>
## 🟢 GitHub aktivitesi

| Kontrol | Durum | Detay |
|---|---|---|
| NVIDIA: depo sayısı (ilk sayfa) | 🟢 | 30 (beklenen 10–30) |
| NVIDIA: son push | 🟢 | en son kayıt 2026-10-10, 0.0 gün önce (sınır 3) |
| microsoft: depo sayısı (ilk sayfa) | 🟢 | 30 (beklenen 10–30) |
| microsoft: son push | 🟢 | en son kayıt 2026-10-10, 0.0 gün önce (sınır 3) |
| apple: depo sayısı (ilk sayfa) | 🟢 | 30 (beklenen 10–30) |
| apple: son push | 🟢 | en son kayıt 2026-10-10, 0.0 gün önce (sınır 3) |
| Kapsam notu | ℹ️ | Yalnızca açık kaynak yapan şirketlerde anlamlı; şirket ↔ organizasyon eşleştirmesi 3. aşamada |

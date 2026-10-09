# Veri Sağlık Raporu — 2026-10-09 22:47 UTC

🟢 10 kullanılabilir · 🟡 4 dikkat · 🔴 3 kullanılamaz

Kırmızı kaynaklar o hafta puanlamada kullanılmaz. Sınıf: 1 = resmî, 2 = güvenilir ama dolaylı.

| Kaynak | Sınıf | Yol | Durum | Süre | İstek |
|---|---|---|---|---|---|
| [Hisse evreni (Nasdaq + SEC)](#universe) | 1 | 1, 2, 3, 4 | 🟢 Kullanılabilir | 0.6 sn | 2 |
| [SEC günlük dosya indeksi](#sec_index) | 1 | 1, 3 | 🔴 Kullanılamaz | 0.9 sn | 5 |
| [SEC şirket dosya geçmişi](#sec_submissions) | 1 | 1, 3 | 🔴 Kullanılamaz | 1.9 sn | 15 |
| [SEC XBRL finansal verileri](#sec_xbrl) | 1 | 1 | 🟡 Dikkat | 6.2 sn | 23 |
| [SEC Form 4 (içeriden işlemler)](#sec_form4) | 1 | 3 | 🟢 Kullanılabilir | 9.1 sn | 61 |
| [SEC 13F (fon pozisyonları)](#sec_13f) | 1 | 3 | 🔴 Kullanılamaz | 0.9 sn | 5 |
| [FINRA açığa satış hacmi](#finra) | 1 | 3 | 🟢 Kullanılabilir | 0.4 sn | 1 |
| [USAspending devlet sözleşmeleri](#usaspending) | 1 | 3 | 🟢 Kullanılabilir | 0.9 sn | 4 |
| [USPTO patentleri (PatentsView)](#uspto) | 1 | 3 | 🟡 Dikkat | 0.0 sn | 0 |
| [Günlük fiyatlar (Yahoo ↔ Nasdaq)](#prices) | 2 | 1, 2, 3, 4 | 🟢 Kullanılabilir | 42.5 sn | 38 |
| [FRED makro ve emtia serileri](#fred) | 1 | 1, 4 | 🟢 Kullanılabilir | 3.8 sn | 6 |
| [GDELT haber akışı](#gdelt) | 2 | 2, 4 | 🟢 Kullanılabilir | 28.5 sn | 5 |
| [Wikipedia ilgisi + Wikidata eşleştirmesi](#wikipedia) | 2 | 2, 4 | 🟡 Dikkat | 7.3 sn | 6 |
| [Hacker News](#hackernews) | 2 | 2, 4 | 🟢 Kullanılabilir | 0.7 sn | 2 |
| [Google News RSS](#gnews) | 2 | 2, 4 | 🟢 Kullanılabilir | 1.2 sn | 3 |
| [Reddit](#reddit) | 2 | 2, 4 | 🟡 Dikkat | 4.1 sn | 3 |
| [GitHub aktivitesi](#github) | 2 | 3 | 🟢 Kullanılabilir | 1.8 sn | 3 |

<a id="universe"></a>
## 🟢 Hisse evreni (Nasdaq + SEC)

| Kontrol | Durum | Detay |
|---|---|---|
| Nasdaq adi hisse sayısı | 🟢 | 3,434 (beklenen 2,500–4,500) |
| Nasdaq listesi güncelliği | 🟢 | en son kayıt 2026-10-09, 0.2 gün önce (sınır 4) |
| Bilinen hisseler listede | 🟢 | 4/4 bulundu |
| SEC CIK eşleşme oranı | 🟢 | 3424/3434 = %99.7 adi hisse |
| Doğrulanmış CIK değerleri | 🟢 | AAPL, MSFT, NVDA, AMZN doğru |
| Çapraz kontrol: SEC'te 'Nasdaq' görünenler Nasdaq listesinde | 🟢 | 4337/4376 = %99.1 |
| Finansal durum dağılımı (risk sinyali) | ℹ️ | normal: 3133, yetersiz (deficient): 280, geciken rapor (delinquent): 17, yetersiz+geciken: 4 |
| Yeni listelenen / çıkan hisseler (önceki çalışmaya göre) | ℹ️ | +0 yeni: [] \| -0 çıkan: [] |

<a id="sec_index"></a>
## 🔴 SEC günlük dosya indeksi

| Kontrol | Durum | Detay |
|---|---|---|
| Erişilebilen iş günü sayısı (son 7 iş günü içinde) | 🟢 | 5 (beklenen 4–5) |
| İndeks güncelliği | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 4) |
| 2026-10-02: toplam dosya | 🟢 | 7,159 (beklenen 1,500–15,000) |
| 2026-10-02: Form 4 sayısı | 🟢 | 3,079 (beklenen 300–6,000) |
| 2026-10-02: dosya tarihi indeks günüyle aynı | 🟡 | 7125/7159 = %99.5 |
| 2026-10-05: toplam dosya | 🟢 | 4,886 (beklenen 1,500–15,000) |
| 2026-10-05: Form 4 sayısı | 🟢 | 2,413 (beklenen 300–6,000) |
| 2026-10-05: dosya tarihi indeks günüyle aynı | 🟡 | 4854/4886 = %99.3 |
| 2026-10-06: toplam dosya | 🟢 | 3,501 (beklenen 1,500–15,000) |
| 2026-10-06: Form 4 sayısı | 🟢 | 837 (beklenen 300–6,000) |
| 2026-10-06: dosya tarihi indeks günüyle aynı | 🟡 | 3482/3501 = %99.5 |
| 2026-10-07: toplam dosya | 🟢 | 3,159 (beklenen 1,500–15,000) |
| 2026-10-07: Form 4 sayısı | 🟢 | 660 (beklenen 300–6,000) |
| 2026-10-07: dosya tarihi indeks günüyle aynı | 🟡 | 3138/3159 = %99.3 |
| 2026-10-08: toplam dosya | 🟢 | 3,193 (beklenen 1,500–15,000) |
| 2026-10-08: Form 4 sayısı | 🟢 | 639 (beklenen 300–6,000) |
| 2026-10-08: dosya tarihi indeks günüyle aynı | 🔴 | 3141/3193 = %98.4 |
| Haftalık form dağılımı | ℹ️ | 4: 7628, 8-K: 943, 13F-HR: 259, SC 13D: 0, SC 13G: 0, 10-K: 9, 10-Q: 39, S-1: 19, 424B4: 3, NT 10-K: 0 |
| Halka arz hazırlığı (S-1/F-1/424B4) | ℹ️ | 51 dosya; örnek: ['Basel Medical Group Ltd', '707 Cayman Holdings Ltd.', 'Tracx Logis Ltd.', 'CYABRA, INC.', 'Amaero Inc.', 'Calm Seas Acquisition Corp.', 'Essential Minerals Acquisition Corp', 'Gravity Acquisition Corp.'] |

<a id="sec_submissions"></a>
## 🔴 SEC şirket dosya geçmişi

| Kontrol | Durum | Detay |
|---|---|---|
| Çekilen şirket | 🟢 | 15/15 = %100.0 |
| Çapraz kontrol: dosyadaki ticker evrendeki ticker ile aynı | 🟢 | 15/15 = %100.0 |
| Doğrulanmış gerçek: AAPL 10-K 2023-11-03 | 🟢 | bulundu |
| 8-K'larda olay kodu (items) dolu | 🟢 | 1233/1233 = %100.0 |
| Kabul anı ile dosyalama tarihi tutarlı (zaman damgası) | 🔴 | 7168/9841 = %72.8 |
| AAPL son dosya güncelliği | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 45) |
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
| Güncel hisse sayısı (son 200 gün) bulunan | 🟡 | 14/20 = %70.0 |
| Kapsam notu | ℹ️ | 0 şirket IFRS raporluyor (yabancı), 0 şirkette XBRL yok: [] |

<a id="sec_form4"></a>
## 🟢 SEC Form 4 (içeriden işlemler)

| Kontrol | Durum | Detay |
|---|---|---|
| Ayrıştırılan Form 4 | 🟢 | 60/60 = %100.0 |
| Geçerli işlem kodu | 🟢 | 108/108 = %100.0 |
| İşlem tarihi ≤ dosyalama tarihi | 🟢 | 108/108 = %100.0 |
| Hisse adedi > 0 | 🟢 | 108/108 = %100.0 |
| Alım/satışta fiyat > 0 | 🟢 | 51/51 = %100.0 |
| Kod/yön tutarlılığı (P→A, S→D) | 🟢 | 51/51 = %100.0 |
| Ticker dolu | 🟢 | 108/108 = %100.0 |
| İşlem kodu dağılımı (örnek) | ℹ️ | S: 46, A: 24, F: 12, M: 11, D: 9, P: 5, J: 1 |
| Bildirim gecikmesi (gün, medyan / %95) | ℹ️ | 2 / 4 |
| Toplu veri seti sayısı (geriye dönük test için) | 🟢 | 83 (beklenen 40–500) |
| Toplu veri seti örnekleri | ℹ️ | ['/files/datastandardsinnovation/data/insider-transactions-data-sets/2026q2_form345.zip', '/files/datastandardsinnovation/data/insider-transactions-data-sets/2026q3_form345.zip'] … ['/files/structureddata/data/insider-transactions-data-sets/2025q4_form345.zip', '/files/structureddata/data/insider-transactions-data-sets/2026q1_form345.zip'] |

<a id="sec_13f"></a>
## 🔴 SEC 13F (fon pozisyonları)

| Kontrol | Durum | Detay |
|---|---|---|
| Bu hafta gelen 13F-HR | ℹ️ | 259 dosya (çeyrek sonu +45 gün civarında yoğunlaşır) |
| Çalışma hatası | 🔴 | ParseError: unbound prefix: line 1, column 0 |

<a id="finra"></a>
## 🟢 FINRA açığa satış hacmi

| Kontrol | Durum | Detay |
|---|---|---|
| Güncellik | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 5) |
| Sembol sayısı | 🟢 | 12,334 (beklenen 5,000–20,000) |
| Açığa satış ≤ toplam hacim | 🟢 | 12334/12334 = %100.0 |
| Evren kapsamı | 🟢 | 3355/3434 = %97.7 |

<a id="usaspending"></a>
## 🟢 USAspending devlet sözleşmeleri

| Kontrol | Durum | Detay |
|---|---|---|
| Veritabanı güncelliği | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 10) |
| Palantir: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |
| Microsoft: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |
| Amazon Web Services: son 1 yıl sözleşme | 🟢 | 50 kayıt, tutarlar sayısal: 50/50 |

<a id="uspto"></a>
## 🟡 USPTO patentleri (PatentsView)

| Kontrol | Durum | Detay |
|---|---|---|
| API anahtarı | 🟡 | PATENTSVIEW_API_KEY yok. Ücretsiz anahtar: https://patentsview.org/apis/keyrequest — alınınca GitHub secret olarak eklenecek |

<a id="prices"></a>
## 🟢 Günlük fiyatlar (Yahoo ↔ Nasdaq)

| Kontrol | Durum | Detay |
|---|---|---|
| Yahoo: veri dönen hisse | 🟢 | 15/15 = %100.0 |
| Nasdaq: veri dönen hisse | 🟢 | 15/15 = %100.0 |
| Çapraz kontrol: en az iki kaynak %0,5 içinde (son 60 gün) | 🟢 | 15/15 = %100.0 |
| yahoo ↔ nasdaq medyan fark | ℹ️ | %0.000 (15 hisse) |
| Tek kaynakta görünen %60+ sıçrama (veri hatası şüphesi) | 🟢 | yok |
| İki kaynağın doğruladığı %60+ hareket (gerçek, risk sinyali) | ℹ️ | CXAI 2026-06-04 |
| Fiyat güncelliği (medyan hissenin son barı) | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 5) |
| 5 günden eski son bar (işlem durdurma / likidite riski) | ℹ️ | yok |
| yahoo: NVDA bölünmesi düzeltilmiş | 🟢 | 7→10 Haziran 2024 değişim %0.7 |
| nasdaq: NVDA bölünmesi düzeltilmiş | 🟢 | 7→10 Haziran 2024 değişim %0.7 |
| Borsadan çıkmış hisselerin geçmiş fiyatı | ℹ️ | SIVB (SVB Financial (2023)): yahoo=yok, nasdaq=yok; ATVI (Activision Blizzard (2023)): yahoo=yok, nasdaq=yok; SGEN (Seagen (2023)): yahoo=yok, nasdaq=yok |

<a id="fred"></a>
## 🟢 FRED makro ve emtia serileri

| Kontrol | Durum | Detay |
|---|---|---|
| DCOILWTICO – Ham petrol WTI (günlük): güncellik | 🟢 | en son kayıt 2026-10-06, 3.0 gün önce (sınır 10); 9517 gözlem, başlangıç 1986-01-02 |
| DGS10 – ABD 10 yıllık faiz (günlük): güncellik | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 10); 16178 gözlem, başlangıç 1962-01-02 |
| PCOPPUSDM – Bakır fiyatı (aylık, IMF kaynaklı ~3 ay gecikmeli): güncellik | 🟢 | en son kayıt 2026-07-01, 100.0 gün önce (sınır 130); 415 gözlem, başlangıç 1992-01-01 |
| INDPRO – Sanayi üretimi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 69.0 gün önce (sınır 75); 1292 gözlem, başlangıç 1919-01-01 |
| CPIAUCSL – Tüketici fiyat endeksi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 69.0 gün önce (sınır 75); 955 gözlem, başlangıç 1947-01-01 |
| IPG3344S – Yarı iletken üretimi (aylık): güncellik | 🟢 | en son kayıt 2026-08-01, 69.0 gün önce (sınır 75); 656 gözlem, başlangıç 1972-01-01 |

<a id="gdelt"></a>
## 🟢 GDELT haber akışı

| Kontrol | Durum | Detay |
|---|---|---|
| Ham dosya akışı güncelliği | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 0.25) |
| İndirilen dosya bütünlüğü (boyut + MD5) | 🟢 | 4,984,826 bayt, md5 eşleşti |
| 15 dakikalık dosyada makale | 🟢 | 1,165 (beklenen 500–50,000) |
| Sütun sayısı = 27 | 🟢 | 1165/1165 = %100.0 |
| Kurum (Organizations) bilgisi olan | 🟢 | 867/1165 = %74.4 |
| Ton değeri okunabilen | 🟢 | 1165/1165 = %100.0 |
| Bu 15 dakikada en çok geçen kurumlar | ℹ️ | united states (75), white house (67), parades commission (28), department of homeland security (28), new york times (23), national weather service (23), google (22), police service of northern ireland (21) |
| Geçmiş veri: 1 Mart 2015 dosyası makale | 🟢 | 1,209 (beklenen 100–50,000) |
| Yardımcı: DOC API zaman serisi | ℹ️ | erişilemedi (HTTP 429); ham dosyalar yeterli |

<a id="wikipedia"></a>
## 🟡 Wikipedia ilgisi + Wikidata eşleştirmesi

| Kontrol | Durum | Detay |
|---|---|---|
| Nvidia: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Nvidia: güncellik | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 3) |
| Apple_Inc.: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Apple_Inc.: güncellik | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 3) |
| Microsoft: gün sayısı (60 gün) | 🟢 | 60 (beklenen 55–61) |
| Microsoft: güncellik | 🟢 | en son kayıt 2026-10-08, 1.0 gün önce (sınır 3) |
| Geçmiş veri: Temmuz 2015 gün sayısı | 🟢 | 31 (beklenen 30–31) |
| Eşleşme yolu: Nasdaq kodu / SEC CIK | ℹ️ | kod ile 777, CIK ile 596 |
| Wikipedia makalesi eşleşen Nasdaq hissesi | 🟡 | 870/3434 = %25.3 |
| Eşleştirme kontrolü | 🟢 | NVDA → Nvidia, AAPL → Apple_Inc. |

<a id="hackernews"></a>
## 🟢 Hacker News

| Kontrol | Durum | Detay |
|---|---|---|
| Son 7 gün 'nvidia' haberi | 🟢 | 33 (beklenen 5–100) |
| Güncellik | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 2) |
| Geçmiş veri: Ocak 2016 sonuç | 🟢 | 30 (beklenen 1–10,000) |

<a id="gnews"></a>
## 🟢 Google News RSS

| Kontrol | Durum | Detay |
|---|---|---|
| 'Nvidia stock': haber sayısı | 🟢 | 102 (beklenen 20–200) |
| 'Nvidia stock': tarihi okunabilen | 🟢 | 102/102 = %100.0 |
| 'Nvidia stock': güncellik | 🟢 | en son kayıt 2026-10-09, 0.1 gün önce (sınır 2) |
| 'Nvidia stock': tekil başlık | 🟢 | 102/102 = %100.0 |
| 'Apple earnings': haber sayısı | 🟢 | 100 (beklenen 20–200) |
| 'Apple earnings': tarihi okunabilen | 🟢 | 100/100 = %100.0 |
| 'Apple earnings': güncellik | 🟢 | en son kayıt 2026-10-09, 0.2 gün önce (sınır 2) |
| 'Apple earnings': tekil başlık | 🟢 | 98/100 = %98.0 |
| 'Nasdaq IPO': haber sayısı | 🟢 | 100 (beklenen 20–200) |
| 'Nasdaq IPO': tarihi okunabilen | 🟢 | 100/100 = %100.0 |
| 'Nasdaq IPO': güncellik | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 2) |
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
| NVIDIA: son push | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 3) |
| microsoft: depo sayısı (ilk sayfa) | 🟢 | 30 (beklenen 10–30) |
| microsoft: son push | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 3) |
| apple: depo sayısı (ilk sayfa) | 🟢 | 30 (beklenen 10–30) |
| apple: son push | 🟢 | en son kayıt 2026-10-09, 0.0 gün önce (sınır 3) |
| Kapsam notu | ℹ️ | Yalnızca açık kaynak yapan şirketlerde anlamlı; şirket ↔ organizasyon eşleştirmesi 3. aşamada |

# Veri Sağlık Raporu — 2026-10-09 22:40 UTC

🟢 8 kullanılabilir · 🟡 3 dikkat · 🔴 6 kullanılamaz

Kırmızı kaynaklar o hafta puanlamada kullanılmaz. Sınıf: 1 = resmî, 2 = güvenilir ama dolaylı.

| Kaynak | Sınıf | Yol | Durum | Süre | İstek |
|---|---|---|---|---|---|
| [Hisse evreni (Nasdaq + SEC)](#universe) | 1 | 1, 2, 3, 4 | 🔴 Kullanılamaz | 0.5 sn | 2 |
| [SEC günlük dosya indeksi](#sec_index) | 1 | 1, 3 | 🔴 Kullanılamaz | 0.8 sn | 7 |
| [SEC şirket dosya geçmişi](#sec_submissions) | 1 | 1, 3 | 🔴 Kullanılamaz | 0.0 sn | 0 |
| [SEC XBRL finansal verileri](#sec_xbrl) | 1 | 1 | 🔴 Kullanılamaz | 0.0 sn | 0 |
| [SEC Form 4 (içeriden işlemler)](#sec_form4) | 1 | 3 | 🔴 Kullanılamaz | 0.0 sn | 0 |
| [SEC 13F (fon pozisyonları)](#sec_13f) | 1 | 3 | 🔴 Kullanılamaz | 0.1 sn | 1 |
| [FINRA açığa satış hacmi](#finra) | 1 | 3 | 🟢 Kullanılabilir | 0.2 sn | 1 |
| [USAspending devlet sözleşmeleri](#usaspending) | 1 | 3 | 🟢 Kullanılabilir | 0.9 sn | 4 |
| [USPTO patentleri (PatentsView)](#uspto) | 1 | 3 | 🟡 Dikkat | 0.0 sn | 0 |
| [Günlük fiyatlar (Yahoo ↔ Nasdaq)](#prices) | 2 | 1, 2, 3, 4 | 🟢 Kullanılabilir | 42.3 sn | 38 |
| [FRED makro ve emtia serileri](#fred) | 1 | 1, 4 | 🟢 Kullanılabilir | 2.2 sn | 6 |
| [GDELT haber akışı](#gdelt) | 2 | 2, 4 | 🟢 Kullanılabilir | 24.8 sn | 5 |
| [Wikipedia ilgisi + Wikidata eşleştirmesi](#wikipedia) | 2 | 2, 4 | 🟡 Dikkat | 5.5 sn | 6 |
| [Hacker News](#hackernews) | 2 | 2, 4 | 🟢 Kullanılabilir | 0.6 sn | 2 |
| [Google News RSS](#gnews) | 2 | 2, 4 | 🟢 Kullanılabilir | 1.5 sn | 3 |
| [Reddit](#reddit) | 2 | 2, 4 | 🟡 Dikkat | 4.1 sn | 3 |
| [GitHub aktivitesi](#github) | 2 | 3 | 🟢 Kullanılabilir | 1.9 sn | 3 |

<a id="universe"></a>
## 🔴 Hisse evreni (Nasdaq + SEC)

| Kontrol | Durum | Detay |
|---|---|---|
| Nasdaq adi hisse sayısı | 🟢 | 3,434 (beklenen 2,500–4,500) |
| Nasdaq listesi güncelliği | 🟢 | en son kayıt 2026-10-09, 0.2 gün önce (sınır 4) |
| Bilinen hisseler listede | 🟢 | 4/4 bulundu |
| SEC ticker→CIK eşleştirmesi | 🔴 | erişilemedi (HTTP 403) |
| Yeni listelenen / çıkan hisseler (önceki çalışmaya göre) | ℹ️ | +0 yeni: [] \| -0 çıkan: [] |

<a id="sec_index"></a>
## 🔴 SEC günlük dosya indeksi

| Kontrol | Durum | Detay |
|---|---|---|
| Erişilebilen iş günü sayısı (son 7 iş günü içinde) | 🔴 | 0 (beklenen 4–5) |

<a id="sec_submissions"></a>
## 🔴 SEC şirket dosya geçmişi

| Kontrol | Durum | Detay |
|---|---|---|
| Çekilen şirket | 🔴 | 0/3 = %0.0 |
| Çapraz kontrol: dosyadaki ticker evrendeki ticker ile aynı | 🔴 | örnek yok |
| Doğrulanmış gerçek: AAPL 10-K 2023-11-03 | 🔴 | bulunamadı |
| 8-K'larda olay kodu (items) dolu | 🔴 | örnek yok |
| Kabul anı ile dosyalama tarihi tutarlı (zaman damgası) | 🔴 | örnek yok |
| AAPL son dosya güncelliği | 🔴 | tarih bulunamadı |
| Yıllık rapor (10-K/20-F/40-F) bulunan şirket | 🔴 | örnek yok |

<a id="sec_xbrl"></a>
## 🔴 SEC XBRL finansal verileri

| Kontrol | Durum | Detay |
|---|---|---|
| Doğrulanmış gerçek: AAPL geliri (2023-09-30) | 🔴 | değer yok (beklenen 383,285,000,000) |
| Doğrulanmış gerçek: MSFT geliri (2023-06-30) | 🔴 | değer yok (beklenen 211,915,000,000) |
| Doğrulanmış gerçek: NVDA geliri (2024-01-28) | 🔴 | değer yok (beklenen 60,922,000,000) |
| Rastgele şirketlerde temel kalem (varlık/gelir/kâr) bulunan | 🔴 | örnek yok |
| Zaman tutarlılığı: dosyalama tarihi ≥ dönem sonu | 🔴 | örnek yok |
| Güncel hisse sayısı (son 200 gün) bulunan | 🔴 | örnek yok |
| Kapsam notu | ℹ️ | 0 şirket IFRS raporluyor (yabancı), 0 şirkette XBRL yok: [] |

<a id="sec_form4"></a>
## 🔴 SEC Form 4 (içeriden işlemler)

| Kontrol | Durum | Detay |
|---|---|---|
| Form 4 listesi | 🔴 | SEC günlük indeksi boş; Form 4 örneklenemedi |

<a id="sec_13f"></a>
## 🔴 SEC 13F (fon pozisyonları)

| Kontrol | Durum | Detay |
|---|---|---|
| Bu hafta gelen 13F-HR | ℹ️ | 0 dosya (çeyrek sonu +45 gün civarında yoğunlaşır) |
| 13F örnekleme | ℹ️ | bu hafta 13F-HR yok; örnek ayrıştırma atlandı |
| Çalışma hatası | 🔴 | FetchError: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets -> 403: <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> <html xmlns="http://www.w3.org/1999/xhtml"> <head> <meta http-equiv="Content-T |

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
| İki kaynağın doğruladığı %60+ hareket (gerçek, risk sinyali) | ℹ️ | KRRO 2025-11-13 |
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
| Ham dosya akışı güncelliği | 🟢 | en son kayıt 2026-10-09, -0.0 gün önce (sınır 0.25) |
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
| Eşleşme yolu: Nasdaq kodu / SEC CIK | ℹ️ | kod ile 777, CIK ile 0 (CIK yok: SEC erişimi bekleniyor) |
| Wikipedia makalesi eşleşen Nasdaq hissesi | 🟡 | 777/3434 = %22.6 |
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
| 'Nvidia stock': haber sayısı | 🟢 | 104 (beklenen 20–200) |
| 'Nvidia stock': tarihi okunabilen | 🟢 | 104/104 = %100.0 |
| 'Nvidia stock': güncellik | 🟢 | en son kayıt 2026-10-09, 0.1 gün önce (sınır 2) |
| 'Nvidia stock': tekil başlık | 🟢 | 104/104 = %100.0 |
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

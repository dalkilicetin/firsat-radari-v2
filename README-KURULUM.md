# FIRSAT RADARI v5.11 — Kurulum

## Bu sürümde ne değişti
- Sürüm numarası artık her yerde doğru görünür (eski "v4" yazısı kalkti; servis worker cache adı da güncellendi, yani site artık yeni sürümü anında gösterir).
- Sekme sırası ve isimleri sadeleşti: Giriş · Özet · Keşif · Listem · Sektörler · Ağaç · Analiz · Metal · Takvim · Fon · Günlük.
- Ağaç sayfası: açtığın dallar sen kapatana kadar açık kalır ("Hepsini Kapat" butonu eklendi).
- Özet kartlarına her firmanın son 1 ay / 3 ay / 1 yıl / 5 yıl getirisi eklendi.
- Açıklamalar sade dille yeniden yazıldı; "Bu sayfayı nasıl okurum?" kutusu eklendi.
- Her firmada Konu / Kalite / Neden şimdi puanları basit dolu-nokta rozetiyle görünür.
- Bir önceki güne göre sıralamada yükselen/düşen/yeni/kaybolan firmalar işaretlenir; bu geçmiş GitHub'daki data/sonuclar.json içinde de tutulur (cihaz değişince kaybolmaz).

## Yapı
- Uygulama (PWA): repo kökündeki index.html, app.js, sw.js, ikonlar
- Gece tarayıcısı: scanner.mjs — GitHub Actions'ta çalışır, sonucu data/sonuclar.json'a yazar
- Uygulama açılınca önce hazır sonucu yükler (saniyeler); yoksa/bayatsa cihazda tarar (eski davranış)

## Kurulum (bir kez, ~10 dk)

### 1. Dosyalar
Bu klasördeki HER ŞEYİ (.github klasörü dahil) repo'nun KÖKÜNE yükle, main dalına.

### 2. API anahtarlarını Secrets'a ekle
Repo → Settings → Secrets and variables → Actions → New repository secret:
- Ad: FINNHUB_KEY  → değer: finnhub.io anahtarın
- Ad: TWELVEDATA_KEY → değer: twelvedata.com anahtarın
(Secrets şifrelidir; kodda ve loglarda görünmez.)

### 3. Pages'i aç
Settings → Pages → Deploy from a branch → main → / (root) → Save.

### 4. İlk taramayı elle tetikle
Repo → Actions → "Gece Taramasi" → Run workflow.
~40-50 dk sürer. Bittiğinde data/sonuclar.json oluşur. Sonrası her gece 03:00 UTC'de otomatik.

### 5. (Opsiyonel) Uygulamadaki "GitHub'da Tara" butonu
İstediğin an telefondan tetiklemek için:
- GitHub → Settings (profil) → Developer settings → Fine-grained tokens → Generate
- Repository access: SADECE bu repo
- Permissions: Actions → Read and write (başka hiçbir izin verme)
- Token'ı uygulamada Ayarlar → GitHub kartına yapıştır (repo adıyla birlikte: kullaniciadi/repo)

### 6. İzleme listesi
Gece taramasının derin haber analizi yaptığı listeler repo'daki watchlist.json'da:
{"other":[...], "micro":[...], "spin":[...]}
GitHub'dan düzenleyebilirsin. Uygulamadaki yerel listeler buna EK olarak cihazda taranmaya devam eder.

## Notlar
- Public repo'da Actions dakikaları sınırsız ücretsizdir. Private repo'da ayda 2.000 dk (gece taraması ~50 dk × 30 = sınıra yakın; public öneririm — kodda gizli bilgi yok, anahtarlar Secrets'ta).
- Uygulama API anahtarı girilmeden de çalışır (sadece gece sonuçlarını okur). Anahtar girersen açılışta canlı fiyat tazeleme de yapar.
- Actions bir gün aksarsa uygulama otomatik eski yönteme (cihazda tarama) döner — sistem tek noktaya bağımlı değil.

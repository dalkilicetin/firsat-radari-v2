# Telegram Otomatik Özet — Kurulum (5 dakika)

Gece taraması bitince Özet + 🚀x5 Moonshot listesi Telegram'dan sana gelir.
Token yoksa scanner normal çalışır, sadece mesaj göndermez (güvenli).

## 1) Bot oluştur
1. Telegram'da **@BotFather**'a yaz → `/newbot`
2. İsim ve kullanıcı adı ver → sana bir **token** verir (örn `8123456:AAH...`). Bunu sakla.

## 2) Chat ID'ni öğren
1. Kendi botuna Telegram'da bir "merhaba" mesajı gönder (sohbeti başlat).
2. Tarayıcıda şunu aç (TOKEN'ı değiştir):
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Dönen JSON içinde `"chat":{"id":123456789` → o **sayı** senin chat id'in.
   (Görünmüyorsa bota bir mesaj daha atıp sayfayı yenile.)

## 3) GitHub'a iki secret ekle
Repo → **Settings → Secrets and variables → Actions → New repository secret**:
- `TELEGRAM_TOKEN` = BotFather'ın verdiği token
- `TELEGRAM_CHAT_ID` = getUpdates'ten aldığın sayı

## 4) Test et
Repo → **Actions → Gece Taramasi → Run workflow** (elle tetikle).
Tarama bitince (~40-50 dk) Telegram'a mesaj düşer. Log'da `Telegram gönderildi: N mesaj` görürsün.

## Mesajda ne var?
- **■ ÖZET (ilk 10)** — en güçlü adaylar
- **■ 🚀 x5 MOONSHOT** — kademeli: 🔥 Fitil (doğrula) · 🌱 Kurulum (izle) · ⚠️ Geç (kovalama)

Not: Keşif ve Listem bölümleri kişisel/cihaz-yerel veri olduğu için Telegram'a değil,
uygulama içindeki **📄 Özet Rapor İndir (TXT/PDF)** butonuna girer.

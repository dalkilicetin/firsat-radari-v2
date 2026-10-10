# Fırsat Radarı — Plan

Amaç: Nasdaq'taki tüm hisseler (yeni halka arzlar dahil) için her hafta
**potansiyel (0–100)** ve **risk (1–5)** puanı üretmek, her puanı dört ayrı
yolun gerekçesiyle açıklamak, önerileri takip edip sistemi sonuçlara göre
yeniden ayarlamak.

Temel ilke: **puanlama ancak veri kadar iyidir.** Her kaynak, kullanılmadan önce
testten geçer; bozuk veri sessizce puana girmez.

---

## Dört yol

| Yol | Ne sorar | Ana kaynaklar |
|---|---|---|
| 1. İş modeli ve yön | Şirket ne üretiyor, neye ihtiyaç duyuyor, kime satıyor, yönetim ne karar veriyor? Bu girdi/çıktıların trendi ne yönde? | SEC 10-K/10-Q/20-F metinleri, XBRL, 8-K, DEF 14A; FRED/EIA/BLS trend verisi; 10-K metin değişimi (Lazy Prices) |
| 2. Gündem | Şirket/ürün/tema hakkında konuşma ve ilgi artıyor mu? | GDELT, Google News RSS, Wikipedia görüntülenmeleri, Hacker News, Reddit |
| 3. Kurumsal sinyaller | İçeridekiler ve kurumlar ne yapıyor? | SEC Form 4, 8-K, 13F; FINRA açığa satış; USAspending; USPTO; GitHub |
| 4. Temadan hisseye | Yükselen temalardan hangi şirketler kazanır? | 2. yolun metinleri → tema tespiti → 10-K metniyle anlamsal eşleştirme → müşteri/tedarikçi zinciri |

4. yol LLM kullanmadan tam otomatik çalışır (kelime öbeği patlaması + yerel
embedding modeli). LLM bu sürümde yok; elle kullanım için prompt dosyaları
sağlanacak.

## Kaynak güvenilirlik sınıfları

- **1. sınıf (resmî):** SEC (submissions, XBRL, Form 4, 8-K, 13F, günlük
  indeks), Nasdaq sembol listesi, FRED, FINRA, USAspending, USPTO.
- **2. sınıf (güvenilir ama dolaylı):** Wikipedia görüntülenmeleri, GDELT,
  Hacker News, GitHub, fiyat verisi (resmî değil → iki kaynaktan çapraz
  kontrol: Stooq + Yahoo).
- **3. sınıf (ertelendi):** iş ilanları, bilanço görüşme metinleri — ücretsiz
  ve güvenilir kaynak yok.
- **Kapsam dışı:** Twitter/X, Instagram, TikTok, Google Trends, StockTwits.

## Veri kalitesi kontrolleri (her kaynak için)

1. **Doğrulanmış gerçekler:** bilinen değerlerle karşılaştırma
   (örn. Apple FY2023 geliri = 383.285 milyar $).
2. **Şema ve kapsam:** beklenen alanlar var mı, kaç şirket kapsanıyor.
3. **Güncellik:** son kayıt ne kadar eski.
4. **Çapraz kontrol:** aynı veri iki kaynaktan (fiyat: Stooq ↔ Yahoo).
5. **Anomali:** kayıt sayısı / değerler normalin dışında mı.
6. **Zaman damgası:** her veri, *yayımlandığı an* ve *çekildiği an* ile
   saklanır (geriye dönük testte ileriye bakma hatasını önler).
   Kural: bir veri, kaynağın onu **kamuya açtığı an** itibarıyla bilinir; şirketin
   dosyalama tarihi değil. (Örnek: halka arz taslakları (DRS) SEC'e aylar önce gizlice
   verilir, sonra yayımlanır. SEC'te esas alınan an: `acceptanceDateTime` (UTC) ve
   günlük indekse giriş günü.)

Sonuç: her çalışmada `reports/data_health/` altında yeşil/sarı/kırmızı
**Veri Sağlık Raporu**. Kırmızı kaynak o hafta puanlamada kullanılmaz.

## Risk puanı (1–5)

Fiyat oynaklığı ve en büyük düşüş, likidite, nakit yeterliliği, hisse
sulandırma (hisse sayısı artışı, S-3/ATM), 10-K'da "substantial doubt",
denetçi değişikliği (8-K 4.01), geciken rapor (NT 10-K), borsadan çıkarılma
uyarısı (8-K 3.01), toplu içeriden satış, açığa satış yoğunluğu, yeni halka arz.

## Puanlama

- Her yol ayrı puan + gerekçe; eksik veri puanı düşürmez, "veri yok" yazılır.
- Vade modelin çıktısıdır: 1 hafta / 1 ay / 3 ay / 6 ay / 1 yıl / 3 yıl için
  ayrı tahmin, en güçlü vade raporlanır; hiçbiri eşiği geçmezse "potansiyel yok".
- Potansiyel 0–100, risk 1–5 (1 düşük, 5 çok yüksek).

## Geriye dönük doğrulama

- Kayan pencere (walk-forward): 2015'ten itibaren eğit → sonraki ayı tahmin et →
  gerçekle karşılaştır → bir ay kaydır.
- Son dönem (2025-07 → bugün) ayarlama sırasında hiç kullanılmaz; en sonda
  tek sefer test edilir.
- Hedef "sıfır hata" değil (aşırı öğrenme); hedef: puan sıralaması ile gelecek
  getiri sıralaması arasında tutarlı pozitif ilişki, en yüksek %10'luk dilimin
  en düşük %10'luk dilimi istikrarlı şekilde geçmesi, yüksek risk puanının
  gerçekten daha sert düşüşlerle eşleşmesi.
- Getiri, endekse (QQQ) ve sektöre göre fazla getiri olarak ölçülür.
- Borsadan çıkmış şirketler teste dahil edilir.

## Öneri takibi

Her hafta tüm şirketler için puanlar, vade ve fiyat kaydedilir; 1h/1a/3a/6a/1y/3y
sonra sonuç ölçülür; ağırlıklar ve vade eşleştirmesi bu sonuçlarla yeniden
ayarlanır. Raporun "Karne" bölümü bunu gösterir.

## Altyapı

Python; GitHub Actions (repo açık → dakika sınırı yok) üzerinde haftalık çalışma;
özet veriler repoda, büyük ham veriler GitHub Releases'te; rapor PDF ve Türkçe.

## Aşamalar

1. **Veri katmanı** — bağlayıcılar, kalite kontrolleri, sağlık raporu. ✅
2. **Geçmiş veri yüklemesi** — SEC, FRED, GDELT, Wikipedia, fiyatlar (2015→). ✅
   (10-K metinleri, şirket profili analiziyle birlikte 3. aşamada.)
3. **Sinyaller ve puanlar** — dört yol + risk puanı. ✅ ([özet](reports/research/OZET.md))
4. **Geriye dönük doğrulama** — kayan pencere, ağırlık ayarı, son dönem testi. ✅ ([özet](reports/research/ASAMA4_OZET.md))
5. **Haftalık çalışma + PDF rapor + öneri takibi.** ← *sıradaki*
6. **İsteğe bağlı** — LLM prompt'ları, ertelenen kaynaklar.

# Açık Liste

Unutulmaması gereken, bekleyen işler.

| # | Konu | Ne gerekiyor | Kimde | Durum |
|---|---|---|---|---|
| 1 | SEC erişimi (403) | `RADAR_USER_AGENT` secret'ı | Kullanıcı | ✅ Tamamlandı |
| 2 | Reddit (403) | reddit.com/prefs/apps → "script" uygulaması → `REDDIT_CLIENT_ID` ve `REDDIT_CLIENT_SECRET` secret'ları. İstenmezse Reddit kaynağı çıkarılır. | Kullanıcı | Bekliyor |
| 3 | USPTO patentleri | patentsview.org/apis/keyrequest → ücretsiz anahtar → `PATENTSVIEW_API_KEY` secret'ı (isteğe bağlı) | Kullanıcı | Bekliyor |
| 4 | Borsadan çıkmış hisselerin geçmiş fiyatı | Tam günlük seri ücretsiz yok. Çıkış tarihi SEC Form 25/15'ten (CIK ile), fiyat SEC fails-to-deliver'dan. Ölçüm (Ekim 2026): 2015 sonrası çıkan ve sembolü bilinen 4.088 şirketin %51'inde çıkıştan önceki 30 günde, %63'ünde 180 günde fiyat var. Kalan boşluk 13F değer/adet (çeyrek sonu fiyatı) ve Form 4 işlem fiyatlarıyla doldurulacak. Tiingo listesi denendi, güvenilir değil. | Claude | ✅ Çözüldü: panelde çıkan hisseler FTD fiyatlarıyla, üye-haftaların %93'ünde fiyat; iflasta çıkış değeri 0 (8-K 1.03) |
| 5 | Çok sınıflı şirketlerde (SPAC'ler, A/B hisse) hisse sayısı | SEC companyfacts sınıf bazlı değerleri içermiyor; örneklemin ~%30'unda eksik. 10-Q/10-K kapak sayfasından okunacak (sulandırma riski için gerekli) | Claude | ✅ Çözüldü: finansal tablolarda sınıf bazındaki hisse sayıları (2024 sonrası SEC verisinde var) toplanıyor; önceki yıllar için kapak sayfası değeri |
| 7 | GDELT kurum adı → şirket eşleştirmesi | GDELT bazı şirketleri yalnızca tam adla kodluyor ("apple inc", "apple app"; "apple" yok). Şirket başına isim listesi (SEC adı, Wikidata takma adları) gerekli | Claude | ✅ Çözüldü: SEC/Nasdaq adı varyantları, belirsiz ve genel sözcükler hariç (5.431 şirket) |
| 8 | Borsadan çıkış tarihi kuralı | Form 25 adi hisse dışındaki menkul kıymetler için de verilebiliyor (SVB 2017). Çıkış = son Form 25/15 + fiyat verisinin kesilmesi birlikte | Claude | ✅ Çözüldü: Nasdaq'ın kendi 25-NSE'si (dosya no öneki) + şirketin kendi Form 25'i (borsa geçişi) |
| 9 | Fiyatı 0 olan "P" (alım) kayıtları | Yanlış kodlanmış özel yerleşim/dönüşüm; açık piyasa alımı sinyalinden çıkarılacak | Claude | ✅ Çözüldü: 0 fiyatlı ve 10 bin $ altı alımlar sinyal dışı |
| 6 | Haftalık otomatik çalışma | GitHub zamanlaması yalnızca varsayılan branch'te (main) çalışır; sistem main'e alınınca devreye girer | Kullanıcı + Claude | **En son yapılacak** (kullanıcı kararı 2026-10-11); o zamana kadar seçimler elle güncellenir |
| 10 | Geriye bakış analizinin ay ay ve hafta hafta sürümü | Yıl yıl PDF'lerin (ne olmalıydı / neden) aylık ve haftalık karşılıkları | Claude | Bekliyor — kullanıcıya hatırlatılacak |
| 11 | S&P 500'ü geçme hedefi | Ayrı dal: claude/sp500-hedefi; sürüm 3 (claude/firsat-modeli) dondurulmuş haliyle kalır | Claude | Sürüyor |
| 12 | Kilitli son test dönemi | 2025–2026 kilitlenir; belirti, ayar ve model seçimi yalnızca 2013–2024'te; kilitli döneme tek bir kez bakılır (iki dış inceleme, 2026-10-12) | Claude | Bekliyor |
| 13 | Çoklu test düzeltmesi | Belirti testinde Benjamini–Hochberg (FDR) düzeltilmiş p değerleri; "etkili" listesi buna göre | Claude | Bekliyor |
| 14 | Risk ve maliyet raporu | En kötü düşüş, Sharpe, kazançlı ay oranı, devir hızı, brüt–maliyet–net ayrımı, maliyet ×2 stres testi, sektör/büyüklük yoğunlaşması | Claude | Bekliyor |
| 15 | Teorik / uygulanabilir performans | Üç sonuç: tüm hisseler, likit hisseler (işlem tutarı tabanı), kapasite sınırıyla | Claude | Bekliyor |
| 16 | Faktör maruziyeti | Portföy getirisinin piyasa, boyut, değer, momentum, kârlılık, yatırım faktörlerine regresyonu (alfa var mı) | Claude | Bekliyor |
| 17 | Kıyas modeli | Tüm belirtileri eşit ağırlıkla kullanan sıralama ile karşılaştırma (seçim yanlılığı ölçüsü) | Claude | Bekliyor |
| 18 | Seviye / değişim / sürpriz | Kârlılık, marj, nakit akışı için üç ayrı belirti; sıkışma süresi, hacim daralması, kırılım sonrası dayanıklılık | Claude | Bekliyor |
| 19 | Kopyalarda ek bilgi testi | Kopya sayılan belirti, diğeri modeldeyken ek bilgi taşıyor mu (silmek yerine); teknik grup için kümeleme | Claude | Bekliyor |
| 20 | Belirti başına tam tarama | Her belirti × yön × seçim × tutma süresi × likidite (~9.500 kural), kazanan yalnızca 2013–2024 ile seçilir | Claude | Bekliyor (kullanıcı isteği) |
| 21 | Ad düzeltmeleri | 8k_1.01 "önemli anlaşma" → çoğunlukla finansman anlaşması; aktivist_13d (yeni 13D var mı) ile aktivist_13d_degisiklik (13D/A sayısı) farkı haritada yazılmalı | Claude | Bekliyor |
| 22 | Analist beklentisi, iş ilanı, ürün kullanımı verisi | Zaman damgalı geçmiş verisi ücretsiz yok (I/B/E/S vb. ücretli); kaynak bulunursa eklenecek | Kullanıcı kararı | Bekliyor |
| 23 | Çıkmış hisselerin günlük fiyatı | %92'si seyrek FTD fiyatı; ücretli kaynak (EODHD ~20 $/ay) önerildi | Kullanıcı kararı | Bekliyor |

Secret ekleme: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

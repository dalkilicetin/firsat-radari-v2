# Açık Liste

Unutulmaması gereken, bekleyen işler.

| # | Konu | Ne gerekiyor | Kimde | Durum |
|---|---|---|---|---|
| 1 | SEC erişimi (403) | `RADAR_USER_AGENT` secret'ı | Kullanıcı | ✅ Tamamlandı |
| 2 | Reddit (403) | reddit.com/prefs/apps → "script" uygulaması → `REDDIT_CLIENT_ID` ve `REDDIT_CLIENT_SECRET` secret'ları. İstenmezse Reddit kaynağı çıkarılır. | Kullanıcı | Bekliyor |
| 3 | USPTO patentleri | patentsview.org/apis/keyrequest → ücretsiz anahtar → `PATENTSVIEW_API_KEY` secret'ı (isteğe bağlı) | Kullanıcı | Bekliyor |
| 4 | Borsadan çıkmış hisselerin geçmiş fiyatı | Tam günlük seri ücretsiz yok. Çıkış tarihi SEC Form 25/15'ten (CIK ile), fiyat SEC fails-to-deliver'dan. Ölçüm (Ekim 2026): 2015 sonrası çıkan ve sembolü bilinen 4.088 şirketin %51'inde çıkıştan önceki 30 günde, %63'ünde 180 günde fiyat var. Kalan boşluk 13F değer/adet (çeyrek sonu fiyatı) ve Form 4 işlem fiyatlarıyla doldurulacak. Tiingo listesi denendi, güvenilir değil. | Claude | ✅ Çözüldü: panelde çıkan hisseler FTD fiyatlarıyla, üye-haftaların %93'ünde fiyat; iflasta çıkış değeri 0 (8-K 1.03) |
| 5 | Çok sınıflı şirketlerde (SPAC'ler, A/B hisse) hisse sayısı | SEC companyfacts sınıf bazlı değerleri içermiyor; örneklemin ~%30'unda eksik. 10-Q/10-K kapak sayfasından okunacak (sulandırma riski için gerekli) | Claude | 3. aşama |
| 7 | GDELT kurum adı → şirket eşleştirmesi | GDELT bazı şirketleri yalnızca tam adla kodluyor ("apple inc", "apple app"; "apple" yok). Şirket başına isim listesi (SEC adı, Wikidata takma adları) gerekli | Claude | ✅ Çözüldü: SEC/Nasdaq adı varyantları, belirsiz ve genel sözcükler hariç (5.431 şirket) |
| 8 | Borsadan çıkış tarihi kuralı | Form 25 adi hisse dışındaki menkul kıymetler için de verilebiliyor (SVB 2017). Çıkış = son Form 25/15 + fiyat verisinin kesilmesi birlikte | Claude | ✅ Çözüldü: Nasdaq'ın kendi 25-NSE'si (dosya no öneki) + şirketin kendi Form 25'i (borsa geçişi) |
| 9 | Fiyatı 0 olan "P" (alım) kayıtları | Yanlış kodlanmış özel yerleşim/dönüşüm; açık piyasa alımı sinyalinden çıkarılacak | Claude | ✅ Çözüldü: 0 fiyatlı ve 10 bin $ altı alımlar sinyal dışı |
| 6 | Haftalık otomatik çalışma | GitHub zamanlaması yalnızca varsayılan branch'te (main) çalışır; sistem main'e alınınca devreye girer | Kullanıcı + Claude | 5. aşama |

Secret ekleme: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

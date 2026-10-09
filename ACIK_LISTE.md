# Açık Liste

Unutulmaması gereken, bekleyen işler.

| # | Konu | Ne gerekiyor | Kimde | Durum |
|---|---|---|---|---|
| 1 | SEC erişimi (403) | `RADAR_USER_AGENT` secret'ı | Kullanıcı | ✅ Tamamlandı |
| 2 | Reddit (403) | reddit.com/prefs/apps → "script" uygulaması → `REDDIT_CLIENT_ID` ve `REDDIT_CLIENT_SECRET` secret'ları. İstenmezse Reddit kaynağı çıkarılır. | Kullanıcı | Bekliyor |
| 3 | USPTO patentleri | patentsview.org/apis/keyrequest → ücretsiz anahtar → `PATENTSVIEW_API_KEY` secret'ı (isteğe bağlı) | Kullanıcı | Bekliyor |
| 5 | Çok sınıflı şirketlerde (SPAC'ler, A/B hisse) hisse sayısı | SEC companyfacts sınıf bazlı değerleri içermiyor; örneklemin ~%30'unda eksik. 10-Q/10-K kapak sayfasından okunacak (sulandırma riski için gerekli) | Claude | 3. aşama |
| 6 | Haftalık otomatik çalışma | GitHub zamanlaması yalnızca varsayılan branch'te (main) çalışır; sistem main'e alınınca devreye girer | Kullanıcı + Claude | 5. aşama |
| 4 | Borsadan çıkmış hisselerin geçmiş fiyatı | Yahoo ve Nasdaq vermiyor; ücretsiz kaynak araştırılacak (geriye dönük testte hayatta kalan yanılgısı) | Claude | 2. aşamanın ilk işi |

Secret ekleme: GitHub repo → Settings → Secrets and variables → Actions → New repository secret.

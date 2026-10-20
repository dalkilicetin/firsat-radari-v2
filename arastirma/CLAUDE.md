# arastirma/ — kod yazan model için kurallar

Önce `PLAN.md` (neden) ve `GOREVLER.md` içindeki **sana verilen görevi** oku. Başka görevlere geçme, plan yeniden tasarlama.

## Dil ve araçlar
- Python 3.11+ (Actions'ta 3.11). Bağımlılıklar sadece `requirements.txt` içindekiler. Yeni paket eklemek gerekiyorsa görev bunu söyler.
- Kod içi isimler ve yorumlar **Türkçe**, ASCII (ı→i, ş→s, ğ→g, ü→u, ö→o, ç→c): `dusus`, `genislik`. Kullanıcıya görünen metin (rapor, sayfa) düzgün Türkçe olur.
- Test: `cd arastirma && python -m pytest -q`. Her görev, testleri yeşil bırakarak biter.
- Bu konteynerde Yahoo, FRED, Stooq ve SEC'e **ağ erişimi yok**. Ağ kodunu `requests` sahte nesneleriyle (monkeypatch) test et. Gerçek çalıştırma GitHub Actions'ta yapılır.

## Zorunlu araştırma kuralları (ihlali = hata)
1. **Geleceği görme yok.** `ozellik/` ve `mekanizmalar/` içinde `shift(-…)`, `center=True` ya da sonraki satırı okuyan hiçbir şey olmaz. Gelecek getiri **sadece** `motor/sonuc.py` içinde hesaplanır.
2. Sinyal t kapanışında oluşur, giriş **t+1 kapanışında** yapılır. Ufuk h işlem günü, getiri `kapanis[t+1+h]/kapanis[t+1]-1` formülüyle hesaplanır.
3. Getiriler **düzeltilmiş kapanıştan** (`adj`) hesaplanır. OHLC'den hesaplanan ATR gibi ölçümlerde ham fiyat × (adj/close) oranı kullanılır.
4. Eşikler ve ufuklar koda gömülmez, `hipotezler/<mekanizma>.yaml` dosyasından okunur. Bir eşiği değiştiriyorsan `deneme_gunlugu.csv` dosyasına satır ekle (`motor/karar.py: gunluge_yaz`).
5. Temel veri (EDGAR), `filed` tarihinden **1 işlem günü sonra** kullanılabilir.
6. Her ortalama yanında n (olay sayısı), bağımsız bölüm sayısı ve %90 güven aralığı raporlanır.
7. Hisse sonuçlarına hayatta kalan yanlılığı uyarısı eklenir (`rapor` bunu otomatik yapar).

## Veri sözleşmesi
- Fiyat: `pd.DataFrame` sütunları `open high low close adj volume`, `DatetimeIndex` (tz yok, artan, tekrar yok).
- Çoklu hisse: geniş tablo `adj[tarih x sembol]` (`Veri.genis("adj")`).
- Makro: `Veri.makro[seri_kodu]` → `pd.Series`, ileri doldurma sadece yayın gecikmesi kadar (haftalık seri en fazla 7 gün).

## Sentetik test verisi
`testler/sentetik.py` dosyasını kullan: bilinen bir etki **eklenmiş** rastgele yürüyüş. Motor bu etkiyi bulmalı, saf rastgele yürüyüşte bulmamalı. Yeni mekanizma = en az 1 "etkiyi bulur" + 1 "gelecek sızıntısı yok" testi. Sızıntı testi: t sonrası veriyi değiştirince t'deki özellik değişmemeli.

## Yapma
- Repo kökündeki `scanner.mjs`, `app.js`, `index.html`, `data/`, `analiz/` dosyalarına dokunma. İstisna: görev açıkça söylerse.
- `onbellek/` klasörünü commit etme.
- Sonuç iyi çıksın diye eşik veya ufuk oynama. Kötü sonuç da sonuçtur.

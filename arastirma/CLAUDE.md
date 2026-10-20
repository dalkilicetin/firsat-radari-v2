# arastirma/ — kod yazan model için kurallar

Önce `PLAN.md` (neden) ve `GOREVLER.md` içindeki **sana verilen görevi** oku. Başka görevlere geçme, plan yeniden tasarlama.

## Dil ve araçlar
- Python 3.11+ (oturumda 3.13). Bağımlılıklar sadece `requirements.txt` içindekiler. Yeni paket eklemek gerekiyorsa görev bunu söyler.
- Kod içi isimler ve yorumlar **Türkçe**, ASCII (ı→i, ş→s, ğ→g, ü→u, ö→o, ç→c): `dusus`, `genislik`. Kullanıcıya görünen metin (rapor, sayfa) düzgün Türkçe olur.
- Test: `cd arastirma && python -m pytest -q`. Her görev, testleri yeşil bırakarak biter.
- **Laboratuvar aşaması: ağdan veri çekme, Actions kullanma.** Veri kaynakları: `tarih/kriz_katalogu.csv`, simülatör (`mekanizma/sim/`), `../data/sonuclar.json` ve onun git geçmişi. `pip install` serbest.
- Simülasyon sonuçlarını hiçbir zaman "piyasada böyle" diye yazma. Simülasyon ölçüm aletini dener. Raporlarda bu ayrımı koru.

## Zorunlu araştırma kuralları (ihlali = hata)
1. **Geleceği görme yok.** `ozellik/` ve `mekanizmalar/` içinde `shift(-…)`, `center=True` ya da sonraki satırı okuyan hiçbir şey olmaz. Gelecek getiri **sadece** `motor/sonuc.py` içinde hesaplanır.
2. Sinyal t kapanışında oluşur, giriş **t+1 kapanışında** yapılır. Ufuk h bar (gün veya ay), getiri `kapanis[t+1+h]/kapanis[t+1]-1` formülüyle hesaplanır.
3. Getiriler **düzeltilmiş kapanıştan** (`adj`) hesaplanır. Örnek veride elde ne varsa o kullanılır (TwelveData aylık kapanışı).
4. Eşikler ve ufuklar koda gömülmez, `hipotezler/<mekanizma>.yaml` dosyasından okunur. Bir eşiği değiştiriyorsan `deneme_gunlugu.csv` dosyasına satır ekle (`zaman, deney, parametreler, ana_sonuc`).
5. Katalogda "sonradan bilinen" sütunlar (dip tarihi, toparlanma, `tur_on_kabul`, resesyon ilanı) **sinyal olarak** kullanılamaz, sadece karşılaştırma için kullanılır.
6. Her ortalama yanında n (olay sayısı), bağımsız bölüm sayısı ve %90 güven aralığı raporlanır.
7. Hisse sonuçlarına hayatta kalan yanlılığı uyarısı eklenir (`rapor` bunu otomatik yapar).

## Veri sözleşmesi
- Fiyat serisi: `pd.Series` / geniş `pd.DataFrame[tarih x sembol]`, `DatetimeIndex` (tz yok, artan, tekrar yok). Adı `adj`.
- Motor ve özellikler **frekanstan bağımsızdır**: pencere ve ufuk "bar" cinsindendir (simülasyonda gün, örnek veride ay). Aylık parametreler `yay.yaml → aylik` içindedir.
- Endeks çerçevesi (sim): `adj, F, m, vix, kredi, sahm` sütunları. `F` ve `m` **sadece** doğru cevap (etiket) için kullanılır. Dedektör bunları göremez; özellik fonksiyonlarına verilmez.

## Test verisi
Simülatörü (`mekanizma/sim/piyasa.py`, L3) kullan: bilinen bir etki **eklenmiş** yapay piyasa. L3 bitmeden önceki görevlerde küçük elle yazılmış seriler yeterli. Motor bu etkiyi bulmalı, saf rastgele yürüyüşte bulmamalı. Yeni mekanizma = en az 1 "etkiyi bulur" + 1 "gelecek sızıntısı yok" testi. Sızıntı testi: t sonrası veriyi değiştirince t'deki özellik değişmemeli.

## Yapma
- Repo kökündeki `scanner.mjs`, `app.js`, `index.html`, `data/`, `analiz/` dosyalarına dokunma (`data/` sadece okunur).
- `onbellek/` klasörünü commit etme.
- Sonuç iyi çıksın diye eşik veya ufuk oynama. Kötü sonuç da sonuçtur.

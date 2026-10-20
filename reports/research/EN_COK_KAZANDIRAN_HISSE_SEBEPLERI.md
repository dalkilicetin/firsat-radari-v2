# Konuşma özeti — Analiz Aracı (20 Ekim 2026)

Bu dosya, "tahmin modeli" yerine "analiz aracı" kararından sonraki konuşmanın kaydıdır: kararlar, kurulanlar, bulgular ve açık işler.

## 1. Strateji değişikliği
- **Önceki durum:** Yürüyen modellerin (LightGBM vb.) 2025–2026 kilitli döneminde sabitlenen seçimleri tutmadı (topluluk ve lgb_sinif5 başarısız; momentum ve lgb_sirala iyi). Fiyat ve bilanço verisinden çıkan sinyal büyük ölçüde tükenmişti.
- **Yeni amaç:** Tahmin yerine analiz aracı. Her cuma en fazla 10 hisselik, gerekçeli bir liste; karar kullanıcıda. Plan: `reports/research/analiz_araci_plani.md`.
- **Kullanıcının kararları:** haftalık tarama (günlük değil), cuma öğleden sonra hazır; vade hem 3 hem 6 ay; çok küçük şirketler elensin, orta boy öncelikli; sade ve anlaşılır Türkçe; telefon öncelikli görünüm; "otopsi" adı korunur.
- **Kullanıcı önerileri, plana işlendi:** yakalanabilir getiri (sinyal fiyatı ≠ alınabilir fiyat), hayatta kalma yanlılığı olmadan test (batan ve çıkan şirketler dahil), süzgeçlerin kazananı koruma / kaybedeni eleme oranıyla ölçülmesi, ret listesinin iki gruba ayrılması (güvenilirlik / piyasa), karne ölçütlerinin genişletilmesi.

## 2. Kesin test kuralları (kodlandı: `radar/arac/duzenek.py`)
- Bilgi kesimi: perşembe 16:00 New York. Belgeler SEC kabul anından itibaren kullanılır; alış cuma kapanışı; satış 13 / 26 hafta sonra.
- Masraf: alışta ve satışta ayrı, işlem hacmine göre (%0,05 – %1).
- Evren o günkü değerlerle: finans dışı faaliyet şirketi, fiyat ≥ 5 $, piyasa değeri ≥ 500 M$, işlem tutarı ≥ 5 M$/gün. Borsadan çıkanların işlem tutarı FINRA hacminden tahmin edilir (yoksa sonradan çıkan hisseler evrenden düşer).
- Çıkış: iflasta −%100, birleşmede son geçerli fiyat. Karşılaştırma: S&P 500, hissenin sektör ETF'i, evrenin eşit ağırlıklı ortalaması.
- Ayar yalnızca 2013–2022; 2023–2026 sınav (kilitli ayar dosyası commit edilmeden açılmaz: `radar/arac/analiz.py --sinav`).

## 3. Veri ve altyapı işleri
- **SEC companyfacts** (`sirket_olgulari`): kapak sayfası hisse sayısı ve güncel temel kalemler; AAPL, LLY, JNJ kapak değerleri doğrulandı.
- **Güncel Form 4** (`insider_guncel`): çeyreklik toplu dosyası çıkmamış günler için günlük indeksten.
- **Birleşik bilanço kaynağı** (`radar/arac/temel.py`): FSDS + companyfacts; aynı raporun kabul anı en geç olana eşitlenir.
- **Haftalık iş akışı** (`.github/workflows/haftalik-tarama.yml`): veri tazeleme → hesap → kilitli liste → site. İlk uçtan uca deneme hesaplama adımlarında başarılı oldu; Pages yayın adımı dal kuralı yüzünden düştü (aşağıda).
- `requirements.txt`'e `reportlab` eklendi (eski haftalık PDF testi CI'da içe aktarılamıyordu).

## 4. Sızıntı bulguları ve düzeltmeler
Doğrulama (`radar/arac/dogrula.py`, girdiler o tarihte kesilerek) ilk çalışmada **kaldı**; nedenler:
1. Aynı rapor iki kaynakta farklı kabul anıyla kayıtlıydı → raporun tüm satırlarına en geç kabul anı verildi.
2. Aynı Cuma'ya düşen birden çok rapordan hangisinin "son" sayıldığı satır sırasına bağlıydı → en geç kabul edilen kazanır.
3. Ortak bilanço eşlemesindeki sıralamalar kararsızdı → kararlı sıralama.
4. Devamlılık sütunlarında boş / yok gösterim farkı → kesin evet/hayır.

**Sonuç:** 2014, 2018, 2021 ve 2025 kesimlerinde fark **0** (288.637 değer). Düzeltmeden sonra ayar yeniden 2013–2022 ile seçildi (aynı varyant: `lift_ceza0`) ve sınav yeniden koşuldu; sonuçlar neredeyse aynı çıktı.

Hayatta kalma kontrolü: 2013'te haftalık evrenin yaklaşık %40'ı sonradan borsadan çıkan şirketlerdir; 135 iflas eden hisse evrende; bilinen değerler (AAPL, JNJ piyasa değeri, SPY getirisi) tuttu.

## 5. Sonuçlar (2023–2026 sınavı, kilitli ayar, masraf sonrası)
| Ölçü | 3 ay | 6 ay |
|---|---|---|
| Ortadaki hissenin getirisi | +%3,2 | +%7,5 |
| Borsadan fazla (ortalama) | +%3,6 (%90 aralık +%2,2 … +%4,7) | +%10,7 |
| Borsayı geçen hafta oranı | %54 | %71 |
| Kazanan çıkma oranı (listedeki hisseler) | %15,7 | %17,7 |

- Çeyrek başı al-tut zinciri yıllık +%19,5; borsa +%21,6. En büyük düşüş −%40. Kazananların %91'i hiç listeye girmedi.
- **3 yıllık yakalama oranı** (10 Temmuz 2023 – 10 Temmuz 2026, haftalık liste, `arac_yakalama.md`): çeyrek içinde listeye giren kazanan **%8,8 (3 ay) / %15,5 (6 ay)**; rastgele 10'luk listelerle %6,2 / %11,1. Listedeki hissenin kazanan çıkma oranı %15 / %17,9 (rastgele %5). Yükselişin yarısından önce yakalama %5,4 / %7,5.
- Çeyrek çeyrek seçimler ve getiriler: `arac_ceyrekler.md` / `.csv`. 12 çeyreğin 7'sinde 3 aylıkta borsa geçildi; zayıf dönemler 2025 başı ve 2026 başı.
- Ret süzgeçleri 2013–2022'de önceden sabitlenen kuralı (kazananı ≥ %90 koru, kaybedeni ≥ 2× daha sık ele, getiriyi düşürme) **geçemedi**; bu yüzden hiçbir hisse otomatik elenmiyor, uyarı olarak gösteriliyor.

## 6. "Modelin 10'u içinden en iyisi" analizi (geriye bakış tavanı)
Her çeyrek başı modelin 10 hissesi içinden 3 ay sonunda en çok kazandıran: LPG +%69, APP +%96, AVGO +%27, WGS +%71, CRDO +%122, DAVE −%21, RKLB +%118, MP +%124, RKLB +%35, PL +%76, LPTH +%32, XMTR +%11. Hepsi her çeyrek tek hisseye konup yeniden yatırılsaydı 1.000 $ → yaklaşık 215.300 $ (10'luk eşit pay ≈ 1.600 $, borsa ≈ 1.860 $).
**Bu gerçek bir strateji değil:** en iyisini önceden bilmenin yolu yok; bileşik hesap şişirir; tek hissede yoğunlaşma ve likidite riski var.

**Neden listedeydiler:** 12'nin 11'inde aynı "tipik 4 işaret" (yükseliş sürüyor, satışlar büyüyor ve hızlanıyor, dipten kalkmış, sektör borsadan iyi). Model bunları ayırt edemedi: çoğu hisse aynı puanı (1,54) aldı; en iyisi 12 çeyreğin 8'inde ilk 5'te bile değildi (RKLB Nisan 2025'te listede 10., MP 9.). Kazananlarda sektör borsadan 2–3 kat iyiydi (çip %55–103, altın %52, yazılım %56) ve satışlar %35–120 artıyordu; model bunları yalnızca var / yok diye okuyor. 6 kazananda "hisse satışı" ya da "nakit sıkıntısı" uyarısı vardı. Kaybedenlerle (aynı listedeki diğer 9) karşılaştırma yapılmadı; bulgu 12 örneğe dayanır.

## 7. Telefon sayfaları ve iki radar
- Üretim: `radar/arac/haftalik.py` + `radar/arac/site.py` (statik, telefon öncelikli, sade çizgi simgeler, koyu tema desteği, yatay kaydırma yok). Sayfalar: liste, hisse kartı, karne (test kuralları dahil), otopsi listesi, otopsi detay kartı (dört sonuç, fiyat yolu, üç bölüm).
- İlk örnek sayfa (ön hesapla) özel bir artifact olarak paylaşıldı.
- **Tek site, iki radar kararı:** eski "Fırsat Radarı v5" (PWA, `main` kökünde, gece taraması `scanner.mjs`) aynen kalır; yeni Analiz Radarı `main`'de `/analiz/` altına yazılır; iki yönlü geçiş bağlantısı. `sw.js`'e `/analiz/` için "her zaman ağdan" kuralı eklendi. Haftalık iş akışı sonucu `main/analiz/` klasörüne yazacak şekilde değiştirildi (ayrı Pages ortamı gerekmez).
- **Durum:** `main`'e yazma için kullanıcı onayı verildi; hazırlık dalda ve `main` çalışma kopyasında (index.html'e geçiş çubuğu + sw.js ayarı) tamam, **henüz `main`'e gönderilmedi**.

## 8. Açık işler
1. `main`'e iki radarlı siteyi yazmak (onaylı): eski `index.html` / `sw.js` değişikliği + `analiz/` klasörü; ardından siteyi sızıntısız veriyle yeniden üretip yayımlamak.
2. Haftalık zamanlama (GitHub yalnızca `main`'deki iş akışını zamanlar): iş akışı dosyasının `main`'e alınması gerekecek; kullanıcı "cuma işine sonra bakarız" dedi.
3. Listeyi 10'dan 2–3'e daraltan sıralama denemesi: sektör farkı ve satış büyümesini sayısal puana katmak, yalnızca 2013–2022 ile kurup 2023–2026'da denemek (kullanıcıya önerildi, onay bekliyor).
4. Gerçek temiz sınav: her cuma kilitlenen listeler (`reports/canli/arac/`) 3 ve 6 ay sonra ölçülür; 2023–2026 artık "ikinci bakış" sayılır (bir kez hatalı veriyle açıldı, sonuçlar görüldü; ayar o sonuçlara göre değiştirilmedi).
5. Ana hat (`claude/firsat-modeli`): Aşama 1 K1–K3 kararları hâlâ kullanıcıda; K1 için yayım tarihine göre hisse sayısı kuralı bu araçta uygulandı.

## 9. Önemli dosyalar
`radar/arac/` (duzenek, temel, isaretler, analiz, yakalama, ceyrekler, haftalik, site, dogrula, hazirla), `reports/research/arac_ayar.json` (kilitli ayar), `arac_sinav.json`, `arac_yakalama.md`, `arac_ceyrekler.md`, `arac_dogrulama.md`, `arac_duzenek_kapsam.json`, `analiz_araci_plani.md`.

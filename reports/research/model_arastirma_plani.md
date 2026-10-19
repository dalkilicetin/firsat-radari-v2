# Araştırma ve Plan: Her Dönemin En Çok Kazandıranlarını Bulan Model

**Tarih:** 19 Ekim 2026. Durum: plan; onay bekliyor, model kurulmadı.

## Hedef ve iki kesin kural (kullanıcı)
1. **Hedef:** Her dönem (3 ay ve 6 ay) için en yüksek getiriyi getiren hisseleri önceden bulan model.
2. **Kural 1:** Model test edilirken asla gelecekteki veriyi görmez.
3. **Kural 2:** Model de yalnızca görmediği veriyle yapılan teste göre kurulur. Seçim, ayar ve belirti kararları test döneminin verisine hiç dokunmaz.

## 1. Araştırma bulguları

### 1.1 Test yöntemi (en kritik konu)
- **Yürüyen test + boşluk (purging / embargo).** Her test dönemi için model yalnızca o dönemden önce etiketi kesinleşmiş verilerle eğitilir. Eğitim ile test arasına hedef süresi kadar (13 / 26 hafta) boşluk konur. Aksi halde etiketler test dönemine taşar ([Purged CV](https://en.wikipedia.org/wiki/Purged_cross-validation); López de Prado 2018, bölüm 7).
- **Tek yürüyen yol yetmez.** Sonuç tek bir bölmeye bağlı kalır. Kombinatoryal temizlenmiş çapraz doğrulama (CPCV) birçok test yolu üretir ve aşırı uyum olasılığını (PBO) ölçmeye izin verir ([fynance CPCV](https://fynance.readthedocs.io/en/latest/generated/fynance.data.combinatorial_purged_cv.html), [walk-forward vs CPCV](https://dev.to/shaktitiwari/walk-forward-testing-for-trading-models-the-honest-method-lopez-de-prado-165j)).
- **Çok deneme yapınca en iyisi şans eseri iyi görünür.** Deneme sayısı arttıkça aşırı uyumlu strateji seçme olasılığı hızla büyür. Çare:
  - her denemeyi kaydetmek;
  - Deflated Sharpe ile düzeltmek ([Bailey & López de Prado 2014](https://papers.ssrn.com/abstract=2460551));
  - PBO raporlamak ([PBO/CSCV](https://escholarship.org/content/qt4w1110bb/qt4w1110bb.pdf), [özet](https://www.luxalgo.com/library/concept/probability-of-backtest-overfitting.md)).
- **Bu projede bulduğumuz test tuzakları** (planın parçası olarak hepsi kapatılacak):

  | Tuzak | Etkisi | Durum |
  |---|---|---|
  | Satır sırası sızıntısı | İlk 5 hisse %14,3, rastgele 5 hisse %9,2 | Bulundu |
  | sue_fiyat | Düzeltilmiş fiyatla bölünüyordu | Bulundu |
  | Hedef sütun adı çakışması | Geleceği doğrudan verirdi | Son anda yakalandı |
  | Kuralların bütün geçmişe bakılarak seçilmesi | "Veriyi gördü" sorunu | Bilinen sorun |

### 1.2 Algoritmalar
- **Sıralamayı öğrenen modeller (learning-to-rank).** Kesitsel hisse seçiminde LambdaMART çoğu çalışmada birinci; klasik yönteme göre Sharpe oranında yaklaşık 3 kat iyileşme raporlanıyor ([Poh vd., arXiv 2012.07149](https://arxiv.org/pdf/2012.07149)). Döviz piyasasında da aynı sonuç ([arXiv 2105.10019](https://arxiv.org/pdf/2105.10019)). Listenin tepesini ve dibini vurgulayan kayıp fonksiyonları da var ([arXiv 2104.12484](https://arxiv.org/abs/2104.12484v1)). Bu sonuçların çoğu maliyet öncesi.
- **Doğrudan "kazanan mı?" sınıflandırması.** En iyi %10'u ayrı ikili model olarak tahmin etmek, getiriyi tahmin etmekten iyi çalışıyor ([arXiv 2108.02283](https://arxiv.org/html/2108.02283v2), [Rihtamo/Turku](https://finance.utu.fi/2023/09/22/turku-applied-mathematics-and-statistics-seminar-tams/)). Modelin emin olmadığı tahminler performansı düşürüyor.
- **Ağaç modelleri ve sinir ağları.** Doğrusal modellerin kaçırdığı etkileşimleri yakalıyor. Bütün yöntemlerin ortak en güçlü sinyalleri momentum, likidite ve oynaklık ([Gu, Kelly, Xiu 2020](https://papers.ssrn.com/abstract=3159577)). 900'den fazla belirtiyle cezasız doğrusal model görülmemiş veride çöküyor; düzenleme şart.
- **Momentum çöküşleri.** Momentum, piyasa sert düştükten sonraki toparlanmalarda çöküyor. Oynaklığa göre ölçekleme ya da dinamik ağırlık Sharpe'ı yaklaşık iki katına çıkarıyor ([Daniel & Moskowitz](https://business.columbia.edu/sites/default/files-efs/pubfiles/4607/mom11.pdf), [Alpha Architect](https://alphaarchitect.com/avoiding-momentum-crashes/)). Bizim kurallarımızın 2021–2022'deki zayıflığı buna uyuyor.
- **Büyük kazananların ortak özellikleri.** 222 kazananı inceleyen [Reinganum 1988](https://rpc.cfainstitute.org/research/financial-analysts-journal/1988/the-anatomy-of-a-stock-market-winner) çalışmasına göre kâr hızlanması ve zaten yüksek olup daha da artan göreli güç belirleyici. Bizim kazanan profili bulgumuz da aynı yönde: iş düzeliyor ve trend kırılmamış. Uygulayıcı kaynaklar ([O'Neil](https://tintintrading.substack.com/p/2022-model-book-of-greatest-stock-415)) geriye bakış yanlılığı taşıyor.

### 1.3 Gerçekçi beklenti
- Her dönemin en iyi 3 hissesi, yaklaşık 2.000 hissenin %0,15'i. Bunları tam yakalamak pratikte mümkün değil.
- Literatürdeki başarılar "en iyi %10'u" ayırt etme düzeyinde. Bizim dönem tablomuzda bile en iyi kural tavanın (%220) yalnızca %8'ini alıyor (+%18).
- Gerçekçi hedef: en iyi %1–5'ten olabildiğince çok hisse yakalamak ve seçilen 3–10 hissenin S&P'yi tutarlı biçimde geçmesi.

## 2. Plan (onay bekliyor)

### Aşama 0 — Test düzeneği (önce bu kurulur, modelden bağımsız)
1. **Veri temizliği:**
   - satır sırası rastgele karıştırılır;
   - sue_fiyat ham fiyatla yeniden hesaplanır;
   - yalnızca güvenilir belirtiler kullanılır;
   - bugün değeri olmayan belirti kullanılmaz.
2. **Yürüyen test:** Test dönemleri 2013 Ocak → 2024 Aralık, her çeyrek. Her test çeyreği için eğitim yalnızca etiketi o çeyrekten en az 13 hafta (6 ay hedefinde 26 hafta) önce kapanan satırlardan oluşur.
3. **İç içe seçim:** Model türü, ayarlar, belirti seti ve eşikler yalnızca eğitim verisinin içinde, ayrıca bir iç yürüyen testle seçilir. Test çeyreği bu kararların hiçbirine katılmaz.
4. **Kilitli son dönem:** 2025 Ocak → 2026 Temmuz hiçbir seçimde kullanılmaz; en sonda bir kez açılır. Ardından canlı kayıt.
5. **Deneme defteri:** Her konfigürasyon kaydedilir. Sonunda PBO (CSCV) ve deneme sayısına göre düzeltilmiş başarı raporlanır.
6. **Çıktı:** Ana analiz yöntemi, yani her çeyrek için en yüksek getirili 3 hisse ile her modelin seçimleri (3 ve 6 ay) yan yana. Ayrıca:
   - en iyi %1 ve %5'ten yakalanan oranı;
   - S&P'yi geçen dönem oranı;
   - maliyetli bileşik getiri;
   - en kötü düşüş.

### Aşama 1 — Kıyas modelleri (aynı düzenekte)
Rastgele 3 hisse; momentum; bizim kurallar (A, B, en iyi kombinasyon). Ancak bu kurallar her yıl yalnızca geçmiş verilerle **yeniden aranır** (yürüyen kural araması). Böylece "veriyi gördü" sorunu ortadan kalkar.

### Aşama 2 — Model aileleri (her biri yürüyen ve iç içe)
1. **Kural öğrenici:** eşik ve kombinasyon araması, her yıl yalnızca geçmişte.
2. **Sınıflandırıcı (LightGBM):** hedef en iyi %1 ve %5; sınıf ağırlığıyla.
3. **Sıralayıcı (LambdaMART):** tepeyi vurgulayan etiketler.
4. **İki aşamalı model:** önce "büyük hareket olacak mı?", sonra "yön yukarı mı?". Kazanan profili bulgumuzdan türetildi.
5. **Kuyruk regresyonu:** getirinin %90 / %95 yüzdeliğini tahmin eden kuantil model.
6. **Rejim süzgeci:** piyasa sert düştükten sonra ya da oynaklık yüksekken momentum ağırlığını azaltmak (Daniel & Moskowitz).
7. **Toplama (ensemble):** en iyi 2–3 ailenin ortalaması.

Sinir ağları, verimiz küçük olduğu için (yaklaşık 200 dönem) en sona bırakılır.

### Aşama 3 — Seçim ve son sınav
- Aileler arasında seçim yalnızca 2013–2024 yürüyen test sonucuyla yapılır; ön kayıtla sabitlenir.
- Kilitli 2025–2026 dönemi bir kez açılır.
- Ardından canlı kayıt başlar (her çeyrek dondurulur).

### Başarı ölçütleri (sonuçlardan önce sabitlenecek)
- Seçilen 3 hissenin ortalama 3 aylık getirisi:
  - S&P'den yüksek;
  - momentum kıyasından yüksek;
  - %90 güven aralığının alt sınırı sıfırın üstünde.
- En iyi %5'ten yakalama oranı rastgelenin en az 3 katı.
- PBO < %50 (en iyi seçilen konfigürasyonun görülmemiş veride medyanın altında kalma olasılığı).

### Süre ve risk
- **Süre:** Aşama 0 bir oturum; Aşama 1–2 birkaç saatlik hesaplama.
- **Bellek:** Yaklaşık 14 GB; yürüyen eğitim çeyrek çeyrek ayrı süreçte koşulur.
- **Olası sonuç:** Hiçbir model ölçütleri geçemeyebilir. Bu durumda olduğu gibi raporlanır ve yeni veri türlerine (analist beklentileri, önemli yatırımcı işlemleri) geçilir.

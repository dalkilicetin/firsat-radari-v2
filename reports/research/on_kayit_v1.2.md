# Fırsat Radarı — Ön Kayıt Belgesi v1.2

- **Tarih:** 13 Ekim 2026 (v1.0: 12 Ekim, commit 7516e9a; v1.1: 12 Ekim, commit e756242; v1.1 ve v1.2 değişiklikleri sonda)
- **Bağlam:** v1.2, 1. aşamanın ilk koşusundan (rapor commit a483c14) sonra yazıldı. Bu nedenle "sonuçlara bakılmadan" yazılmış sayılmaz; değişikliklerin hangi sonuçlar görüldükten sonra ve neden yapıldığı bölüm 10'da açıkça kayıtlıdır. Kullanıcı kararlarıyla (13 Ekim 2026) onaylandı. v1.0 ve v1.1 değiştirilmeden korunur.
- **Durum:** Sabit. Bu belge model sonuçlarına bakılmadan yazıldı ve kullanıcı tarafından onaylandı. Değişiklik ancak yeni sürüm numarasıyla, gerekçesi yazılarak yapılabilir; eski sürüm silinmez.
- **Önceki ön kayıt:** `firsat_on_kayit.md` (10 Ekim 2026). O belgedeki ölçütler bu belgeyle değiştirilmiştir; o tarihten bu yana yapılan denemeler aşağıda kayıtlıdır.

## 1. Kapsam

| Konu | Tanım |
|---|---|
| Evren | ABD borsalarında (Nasdaq, NYSE, NYSE American) işlem gören, ay başında fiyatı ≥ 1 $ olan finans dışı faaliyet şirketleri. Hariç: banka, sigorta, GYO, fon/BDC, SPAC, eğitim (SIC 611x). Günlük işlem tutarı (13 haftalık medyan) ≥ 1 M$ ya da bilinmiyor. |
| Borsadan çıkanlar | Dahil. Satın alma vb. çıkışta son geçerli fiyat, iflasta (8-K 1.03) 0. Senaryolar için bkz. bölüm 5. |
| Geliştirme dönemi | 2013–2024. Belirti araştırması, model ve ayar seçimi yalnızca bu dönemle yapılır (getirisi 1 Ocak 2025'ten önce gerçekleşen aylar). |
| İkincil test dönemi | 2025–2026. **Tamamen dokunulmamış değildir:** 2025 sonuçları önceki denemelerde görüldü; 10 Ekim ön kaydındaki son dönem (Temmuz 2025 →) 4. aşamada bir kez kullanıldı. Bu dönemin sonucu "ikinci derece kanıt" olarak raporlanır. |
| Asıl ileriye dönük test | 12 Ekim 2026 ve sonrası, canlı kayıt (bölüm 7). |
| Ölçüm tarihleri | Her çeyrek başının ilk Cuması (Ocak, Nisan, Temmuz, Ekim). 2013–2024: 48 çeyrek. |
| Getiri penceresi | Ölçüm tarihi t'nin Cuma kapanışından **bir sonraki ölçüm tarihinin** Cuma kapanışına kadar (12, 13 ya da 14 hafta; iki ilk Cuma arası takvime göre değişir). Pencereler tanım gereği uç uca eklenir, çakışmaz. Model A portföy getirisi ve Model B'nin 'en iyi %5' etiketi bu pencereyle hesaplanır. Model eğitimindeki hedef (13 haftalık sıra) bundan bağımsızdır; eğitimde test tarihinden önce gerçekleşmiş hedefler kullanılır (13 hafta boşluk). 1. aşamada bütün tarihler ve pencereler tablo olarak üretilir ve çakışma olmadığı kontrol edilir. |

## 2. Model A — Getiri modeli

### 2.1 Sabit tanım
Önceden sabitlenen tek ayar: LightGBM regresyon, hedef sonraki 13 haftanın getiri sırası; 200 ağaç, öğrenme hızı 0,05, 31 yaprak, yaprakta en az 400 gözlem, belirti örnekleme %60, satır örnekleme %70, L2 = 10; eğitim penceresi test yılından önceki 5 yıl, 13 hafta boşluk; 5 tohumun sıra ortalaması; temiz belirti seti (2. aşamada kesinleşecek, bölüm 6); en yüksek puanlı 10 hisse, eşit ağırlık, 13 hafta tutma; maliyet `backtest.cost_rate` kademeleri, devir tabanlı.

**Açıklama:** Bu ayar, 2013–2025 sonuçları görülerek birçok deneme arasından seçildi. Bu nedenle geliştirme dönemi sonucu seçim yanlılığı içerir; dürüst karşılaştırma için meta seçim (her yıl yalnızca önceki yıllara bakarak ayar seçimi) sonucu ayrıca raporlanır.

### 2.2 Başarı koşulları (geliştirme dönemi, hepsi birlikte sağlanmalı)
Tek bir olumlu ölçüt, sağlanmayan diğer koşulları telafi etmez.

| # | Koşul | Eşik |
|---|---|---|
| A1 | Getiri | Net CAGR > aynı çeyreklerde S&P 500 (SPY, temettü dahil) CAGR'ı **ve** CAGR farkının %90 güven aralığının alt sınırı > 0 |
| A2 | Düşüş | Portföyün en büyük düşüşünün **mutlak büyüklüğü**, aynı dönemde S&P 500'ün en büyük düşüşünün mutlak büyüklüğünün 1,5 katını aşmamalı. Örnek: S&P −%20 ise izin verilen en büyük düşüş −%30; portföy −%25 → sağlanır, −%35 → sağlanmaz. İki taraf aynı değerleme sıklığıyla (çeyreklik) ölçülür. |
| A3 | Maliyet | Maliyetler 2 katına çıkarıldığında net CAGR > S&P 500 CAGR |
| A4 | Likidite | Yalnızca günlük işlem ≥ 1 M$ (bilinmeyen hariç) evrende seçildiğinde net CAGR > S&P 500 CAGR |
| A5 | Alfa | Faktör regresyonunda alfa > 0 ve t ≥ 2 |
| A6 | Çıkış senaryoları | A1'in getiri kısmı (net CAGR > S&P CAGR) üç çıkış senaryosunun en az ikisinde sağlanmalı |

Sonuç: Altı koşulun tamamı → **başarılı**. Herhangi biri sağlanmazsa → **başarısız**; sistem yatırım için kullanılmaz, araştırma aracı olarak kalır.

İddialı hedef (başarı ölçütü değildir, ayrıca izlenir): net CAGR ≥ 3 × S&P 500 CAGR.

### 2.3 Ayrıca raporlanacaklar (eşiksiz)
Aritmetik ortalama yıllık getiri, CAGR, toplam dönem getirisi, yıllık oynaklık, Sharpe ve Sortino (risksiz faiz: FRED FEDFUNDS), kazançlı çeyrek oranı, en kötü yıl, devir hızı, sektör yoğunluğu, küçük hisse payı, en iyi tek seçim çıkarılınca getiri, kapasite (her seçimde günlük işlemin %5'i × 5 gün × 10 hisse), yıl yıl S&P farkı, meta seçim sonucu, eşit ağırlıklı belirti kıyası.

## 3. Model B — Büyük kazanan modeli (üçüncü deneme)

### 3.1 Önceki denemeler
1. **"kazanan" hedefi** (en iyi %5 ikili sınıflandırma, ağırlıksız): yalnızca portföy getirisi ölçüldü, +%1–7/yıl.
2. **Lambdarank** (ilk sıraları optimize eden sıralama): yalnızca portföy getirisi ölçüldü, +%6–14/yıl.

Precision ve Recall hiçbirinde ölçülmedi. Bu belgedeki eşikler bu denemelerden türetilmedi. Yeni deneme araştırma sürecinin **üçüncü denemesi** sayılır.

### 3.2 Sabit tanım
- **Hedef:** Her ölçüm tarihinde, aynı tarihteki evren içinde sonraki 13 haftanın getiri sıralamasında en iyi %5'e girmek (1), değilse 0. Çıkış değeri bölüm 1'deki gibi (senaryo 1).
- **Model:** LightGBM ikili sınıflandırma; Model A ile aynı belirti seti, eğitim penceresi, ağaç ayarları ve 5 tohum; sınıf dengesizliği için pozitif sınıf ağırlığı 19 (= 95/5). Seçim: tahmin edilen olasılığa göre sıra.
- **Tek koşu:** Ayar araması yapılmaz. Sonuç görüldükten sonra değişiklik yapılırsa bu ayrı bir dördüncü deneme olarak kaydedilir.

### 3.3 Ölçütler
- **Precision@10:** İlk 10 seçimden en iyi %5'e girenlerin oranı (çeyrek başına; rastgele beklenti %5).
- **Recall@%5:** Gerçek en iyi %5'in, modelin ilk %5'lik aday listesinde bulunan oranı (çeyrek başına; rastgele beklenti %5).
- Not: Recall@10 kullanılmaz; ilk 10 sabit olduğundan Recall@10 = Precision@10 × 10 / (en iyi %5'teki hisse sayısı) olur ve ek bilgi taşımaz.
- Precision@10'da çeyrek başına rastgele beklenti 0,5 hissedir; çeyrek sonuçları çok oynaktır. Karar yalnızca 48 çeyreğin ortalaması ve bölüm 4'teki güven aralığıyla verilir; tek çeyrek ya da yıl sonucu yorumlanmaz.

### 3.4 Kıyas yöntemleri (sabit)
1. Rastgele seçim: matematiksel beklenti %5 (her iki ölçüt).
2. En yüksek 12-1 momentum (son 12 ay, son ay hariç).
3. En yüksek geçmiş oynaklık (son 26 haftanın haftalık getiri oynaklığı).

Kıyaslar aynı tarihlerde, aynı evrende hesaplanır.

### 3.5 Başarı koşulları (geliştirme dönemi)
| Seviye | Koşul (her iki ölçüt için ayrı ayrı sağlanmalı) |
|---|---|
| **Asgari: beceri var** | (a) Ortalama > %5 ve %90 güven aralığının alt sınırı > %5; (b) momentum ve oynaklık kıyaslarının her birine karşı ortalama fark > 0 ve farkın %90 güven aralığının alt sınırı > 0; (c) yılların ≥ %60'ında yıllık ortalama > %5 |
| **Hedef: yatırım için anlamlı** | Asgari koşullar + ortalama ≥ %15 |

Precision@10 ile Recall@%5 farklı listelere bakar ama aynı model puanından türediği için matematiksel olarak bağımsız değildir; ikisinin birlikte sağlanması iki bağımsız doğrulama gibi yorumlanmaz.

Sonuç sınıfları: asgari sağlanmazsa **beceri yok**; asgari sağlanıp hedef sağlanmazsa **beceri var, yatırım için yetersiz**; ikisi de sağlanırsa **başarılı**.

%15 önceden belirlenmiş operasyonel bir hedeftir; sağlanması tek başına S&P × 3 getirisini kanıtlamaz. Gerekçesi (model sonucundan değil, hedeften ve dağılımdan): S&P × 3 ≈ +%46/yıl ≈ çeyrekte +%10. En iyi %5'e girmenin alt sınırı çeyrekte yaklaşık +%39'dur (evrenin getiri dağılımının özelliği). Diğer seçimler ortalama 0 getirse hedef için seçimlerin ≈ %25'i büyük kazanan olmalıdır; diğer seçimlerin de getiri katkısı olacağından %15 (rastgelenin 3 katı) asgari yatırım hedefi olarak seçildi.

### 3.6 Sinyal öncülüğü (yalnızca betimleyici, eşik yok)
Büyük kazananın yükselişe başladığı an için ilkeli bir tanım olmadığından eşik konmaz. Raporlanacaklar: yakalanan kazananların 1, 2 ve 3 çeyrek önceki ilk %5 listelerinde de bulunma oranı; işaretlendikleri anda son 4 haftalık getirilerinin dağılımı; kaçırılan kazananların belirti profili.

## 4. İstatistik yöntemleri (sabit)

| Konu | Yöntem |
|---|---|
| Güven aralığı | **Yıllık blok bootstrap**: 2013–2024'ün 12 takvim yılı, yerine koyarak 12 yıl çekilir (her yıl 4 çeyreğiyle birlikte); 10.000 tekrar; rastgele tohum 20261012; %90 yüzdelik aralığı (5. ve 95. yüzdelik, doğrusal ara değer). Yıl içi ve şirketler arası bağımlılık bloğun içinde kalır. |
| Eşleştirilmiş farklar | Model ile kıyas (S&P 500 ya da kıyas yöntemi) her bootstrap tekrarında **aynı çekilen yıllar** üzerinden hesaplanır; fark istatistiği bu eşleştirilmiş örneklerden alınır. |
| CAGR farkı | Her tekrarda çekilen yılların çeyreklik net getirileri (portföy ve S&P aynı çeyrekler) bileşiklenir, iki CAGR'ın farkı alınır. |
| En kötü düşüş | Çeyreklik bileşik değer serisi üzerinden, portföy ve S&P için aynı sıklıkta (çeyrek içi düşüşler iki tarafta da görünmez). |
| Faktör regresyonu | Çeyreklik net portföy getirisi ~ piyasa + boyut + değer + momentum + kârlılık + yatırım. Faktörler aynı evrenden, aynı tarihlerde üçte birlik uzun–kısa portföylerle kurulur (boyut: küçük − büyük; değer: yüksek − düşük defter/fiyat; momentum: yüksek − düşük 12-1; kârlılık: yüksek − düşük özsermaye kârlılığı; yatırım: düşük − yüksek varlık büyümesi; piyasa: evrenin eşit ağırlıklı getirisi). EKK; standart hata **Newey–West (HAC)**: Bartlett çekirdeği, 4 çeyrek gecikme, küçük örneklem düzeltmesi yok; kendi uygulamamız (`denetim.py`), 1. aşamada bilinen bir örnekte elle hesaplanan sonuçla karşılaştırılarak doğrulanır. Alfa yıllıklandırılarak da raporlanır. |
| Belirti testi | IC t değeri çakışmayan aylarla; Benjamini–Hochberg q; kesin: q < 0,05, \|t\| ≥ 3, yılların ≥ %70'inde aynı yön (`belirti_testi.py`). |

## 5. Borsadan çıkanlar: çıkış senaryoları

Senaryolar, iflas dışı çıkışlarda son geçerli fiyatı seyrek SEC FTD kaydından gelen hisselere uygulanır (Yahoo günlük fiyatı olanlar gerçek fiyatla kalır; iflaslar her senaryoda 0).

| Senaryo | Çıkış değeri |
|---|---|
| 1 (birincil) | Son geçerli fiyat |
| 2 | Son geçerli fiyat × 0,5 |
| 3 | 0 (tam kayıp) |

Getiri her zaman pozisyonun alış fiyatına göre hesaplanır; "%50 aşağı" son fiyata uygulanır, toplam yatırımın %50 kaybı anlamına gelmez.

İki ayrı soru ayrı kurallarla yanıtlanır:
1. **Strateji dayanıklı mı?** → Koşul A6.
2. **Veri karar verecek kadar güvenilir mi?** → Senaryo 3'ün net CAGR'ı senaryo 1'den yılda **3 puan ya da daha fazla** düşükse, ya da A1'in getiri kısmı senaryo 3'te sağlanmıyorsa, çıkmış hisselerin ücretli günlük fiyat verisi alınmadan hiçbir Model A sonucu kesin kabul edilmez. *(3 puan eşiği bu belgede önerilmiştir.)*

## 6. Veri doğrulama (1. aşama) kabul koşulları

Toleranslar ölçümün niteliğine göre ayrıdır; tek bir genel tolerans kullanılmaz. Bir kontrol geçmezse sapan her durum tek tek listelenir ve nedeni açıklanır; açıklanamayan sapma varsa aşama tamamlanmış sayılmaz.

| Veri türü | Kontrol | Kabul koşulu |
|---|---|---|
| Hisse bölünmeleri (bölünme ve ters bölünme; bkz. 6.2) | Yahoo bölünme kayıtlarındaki oranı 1/1,3'ün altında ya da 1,3'ün üstünde olan **her** olay: (a) hisse sayısına uygulanan düzeltme oranı = kayıttaki bölünme oranı; (b) bölünme haftasında piyasa değerindeki değişim = aynı haftanın düzeltilmiş fiyat getirisi; (c) bölünmeden sonraki ilk raporun kapak sayfası hisse sayısı × o günkü işlem fiyatı = bizim piyasa değerimiz — **yalnızca 6.3'teki ihraç belgesi bulunmayan olaylarda** | (a) ±%1; (b) mutlak fark ≤ 2 yüzde puan (o hafta yeni rapor gelmediyse); (c) ±%2. Her kontrol için, kontrolün uygulandığı olayların ≥ %99'u sağlamalı; bölünme ve ters bölünme **ayrı ayrı** değerlendirilir; kalan her olay tek tek açıklanır. |
| Hisse sayısı ve piyasa değeri | Bölünme kaydı olmayan hisselerde düzeltme değer değiştirmez | Birebir aynı (fark 0). Değişen her hücre bir olay kaynağına (6.1-3) bağlanır; bağlanamayan hücre kalırsa kontrol başarısız. |
| Ayrılma ve hisse temettüsü (6.2) | Ayrı olay türü; (a)–(c) kabul hesabına girmez | Olay başına raporlanır: tür, oran, piyasa değeri değişimi, sonraki raporda hisse sayısı değişimi |
| Gelir, faaliyet kârı, net kâr, varlık, özsermaye | Aynı raporlama dönemi ve aynı tanımla, şirketlerin 10-K'larındaki rakamlarla (en az 5 şirket × 2 dönem: AAPL, MSFT, KO, XOM, NVDA) | ±%0,5 (yuvarlama) |
| F/K, nakit akışı getirisi, temettü verimi vb. | Pay ve payda ayrı ayrı doğrulanır (yukarıdaki iki satır); oran, doğrulanmış bileşenlerden yeniden hesaplanıp çerçevedeki ham değerle karşılaştırılır | Bileşenler kendi toleranslarında; yeniden hesap ±%1 |
| Diğer finansal oranlar | Arşivden rastgele 200 şirket-tarih için bileşenlerden bağımsız yeniden hesap | ±%1; ≥ %99 sağlamalı |
| Zamanlama | Yapay olay testleri; finansal değerlerin ve belgelerin kabul anından sonraki ilk Cuma'dan önce görünmemesi; sızıntı testi (148+ belirti) | Kesin (hiç istisna yok) |
| Tutarlılık | Çerçevedeki her belirti kaynak tablosuyla örtüşür | Spearman ≥ 0,99; olaylarda ≥ %99 eşleşme |
| Bağımsız hesap | Fiyat belirtileri günlük fiyattan ayrı formülle | Spearman ≥ 0,90 (günlük/haftalık örnekleme farkı payı) |
| Ölçüm tarihleri | Bölüm 1'deki tarih ve pencere tablosu | Çakışma yok; her pencerenin başı ve sonu yazılı |
| Eksik veri | Eksikliğin şirket büyüklüğü, sektör ve yıla göre dağılımı | Raporlanır |
| Çıkış senaryoları | Bölüm 5'teki üç senaryo için evren düzeyinde etki | Raporlanır |

Önceki doğrulama sonuçları sıfırdan yapılmamış sayılmaz; düzeltilmiş çerçevede tekrarlanıp eskiyle karşılaştırılır.

### 6.1 Veri tanımları (v1.2)

1. **Hisse sayısı yalnızca dönem sonu sayısıdır.** Kaynak: kapak sayfası (`dei:EntityCommonStockSharesOutstanding`), yoksa bilanço (`CommonStockSharesOutstanding`); sınıf bazında verilmişse sınıflar toplanır. Ağırlıklı ortalama hisse sayısı (`WeightedAverageNumberOfSharesOutstandingBasic`) yedek olarak **kullanılmaz**. Dönem sonu sayısı yoksa bu sayıya dayanan bütün hesaplar (piyasa değeri ve ondan türeyen belirtiler) eksik kalır; eksiklik doldurulmaz. Etkilenen belirtilerin kapsama oranı ve kapsanan şirketlerin bileşimi (büyüklük, sektör, yıl, fiyat dilimi) raporlanır.
2. **Toplam finansal borç** her rapor için o raporun kalemlerinden, kalem tanımlarına göre kurulur (`us-gaap` tanımları: `LongTermDebt` uzun vadeli borcun kısa vadeli kısmını **içerir**; `LongTermDebtNoncurrent` içermez; `LongTermDebtCurrent` yalnızca uzun vadeli borcun kısa vadeli kısmıdır; `DebtCurrent` kısa vadeli borçların tamamıdır ve kısa vadeli kısmı içerir):
   - Uzun vadeli kısım (kısa vadesiz) varsa: `LongTermDebtNoncurrent` + (`DebtCurrent`, yoksa `LongTermDebtCurrent`, yoksa 0).
   - Yalnızca toplam uzun vadeli borç (`LongTermDebt`) varsa: `LongTermDebt`; kısa vadeli kısım (`LongTermDebtCurrent`) ikinci kez **eklenmez**. `DebtCurrent` ve `LongTermDebtCurrent` birlikte varsa aradaki fark (diğer kısa vadeli borçlar, en az 0) eklenir.
   - `LongTermDebt` ile yalnızca `DebtCurrent` varsa (`LongTermDebtCurrent` yok): `DebtCurrent`'in `LongTermDebt` içindeki kısmı belirlenemez. Gözlem **belirsiz** olarak işaretlenir; değer `LongTermDebt` (alt sınır) alınır ve üst sınırla (`LongTermDebt + DebtCurrent`) birlikte raporlanır.
   - Yalnızca kısa vadeli kalem varsa o kalem; hiç borç kalemi yoksa borç 0 kabul edilir (önceki tanımla aynı; oranı raporlanır).
   - Borca dayanan belirtiler (borç/özsermaye, FAVÖK/FD, Piotroski kaldıraç kriteri) ve eksik veri oranları yeniden hesaplanır; belirsiz gözlem oranı belirti başına raporlanır.
3. **Bölünme düzeltmesi olay kayıtlarından yapılır.** Hisse sayısı, sayının geçerli olduğu tarihten (kapak ya da bilanço tarihi) t gününe kadar gerçekleşen bölünme olaylarının oranlarının çarpımıyla düzeltilir. Fiyat oranından (düzeltilmiş / ham fiyat) türetilen oran **kullanılmaz**; o oran temettü düzeltmesini de içerir. Aynı kural 52 hafta önceki hisse sayısına (hisse sayısı değişimi, Piotroski) uygulanır. Olay kaynakları ve önceliği:
   - Yahoo günlük fiyat verisindeki bölünme kayıtları (işlemdeki hisseler ve borsadan çıkmış hisselerin Yahoo serileri). Sembol → şirket eşleştirmesi, fiyat panelindeki eşleştirmenin aynısıdır.
   - Yahoo serisi olmayan, fiyatı seyrek SEC FTD kayıtlarından gelen çıkmış hisselerde, fiyat panelinin zaten uyguladığı **tahmini ters bölünmeler** (bilinen oranlardan birine ±%8 uyan ≥ 3,5 kat sıçrama). Bunlar "tahmini" olarak etiketlenir, ayrı raporlanır ve Yahoo olaylarıyla aynı kabul hesabına katılmaz.
   - Oran eşiği değişmez: 1/1,3 ile 1,3 arasındaki kayıtlar (6.2) hisse sayısını düzeltmez.
   - Yahoo kaydı mutlak doğru kabul edilmez: tetiklenmeyen ya da sapan her olayda tarih, sembol, oran yönü ve şirketin hisse sayısı serisi kontrol edilir ve çözüm gerekçesi olay başına yazılır. Oranı 1/1000'in altında ya da 1000'in üstünde olan kayıtlar ("aşırı oranlı") silinmez, kabul hesabında kalır ve tek tek doğrulanır.

### 6.2 Bölünme olay türleri

| Tür | Tanım (Yahoo oranı r) | Kabul hesabı |
|---|---|---|
| Bölünme | r ≥ 1,3 | (a), (b), (c) |
| Ters bölünme | r ≤ 1/1,3 | (a), (b), (c); ayrıca ilk rapordaki sayının bizim sayımızdan sapma yönü ve büyüklüğü raporlanır |
| Ayrılma ya da hisse temettüsü | 1/1,3 < r < 1,3 | Kabul hesabına girmez; veri kalitesi analizinde ayrı tür olarak raporlanır (silinmez). Alt sınıf: önceki rapordan sonraki rapora hisse sayısı, r − 1'in en az yarısı kadar arttıysa "hisse temettüsü olası", artmadıysa "ayrılma olası", rapor yoksa "belirsiz". Bu ayrım yalnızca betimleyicidir. |
| Tahmini ters bölünme (FTD) | 6.1-3 | Ayrı raporlanır |

### 6.3 İlk rapor kontrolü (c) ve ihraç belgesi

- **İhraç belgesi:** Şirketin, bölünmeden önceki son raporunun kabulü ile bölünmeden sonraki ilk raporunun kabulü arasında SEC'e verdiği bir satış izahnamesi (Form 424B1, 424B2, 424B3, 424B4, 424B5, 424B7) ya da kayıtsız hisse satışı bildirimi (8-K madde 3.02). Kayıt beyanı (S-1, S-3, F-1, F-3) tek başına satış belgesi sayılmaz; ayrıca raporlanır.
- **Belge varsa:** (c) uygulanmaz. Sapma yönü (ilk rapordaki sayı bizimkinden büyük mü) ve büyüklüğü ayrıca raporlanır; belge olduğu hâlde sayı **düşükse** olay açıklanmamış sapma sayılır.
- **Belge yoksa:** (c) ±%2 ile uygulanır ve %99 kabul hesabına girer. Belgenin bulunmaması ihraç olmadığı anlamına gelmez (ör. varant kullanımı, borç dönüşümü, ücret olarak hisse, arşivde olmayan form türleri); bu olaylar ayrıca sınıflandırılır: "belge yok, (c) sağlandı", "belge yok, sayı fazla", "belge yok, sayı az". Bu sınıflandırma kabul sonucunu değiştirmez.
- Belge araması yalnızca SEC dosyalama arşivinin kapsadığı form türleriyle yapılabilir; arşivde bulunmayan bir form türü sonradan eklenirse sonuç her iki belge kümesiyle ayrı ayrı raporlanır.

**Belirti haritasının yeniden yorumlanması kuralı:** v2 raporunda kesin olan 47 belirtiden **en az 12'si** (47'nin dörtte biri 11,75) düzeltilmiş veride kesinliğini kaybeder ya da IC işareti değişirse, eski belirti haritasına dayanan bütün yorumlar geçersiz sayılır ve harita düzeltilmiş veriyle baştan yorumlanır. Bu, yeni modelin başarısız olduğu anlamına gelmez; yeni haritanın geçerliliği düzeltilmiş veride ayrıca belirlenir.

**Belirti seti:** 2. aşamada, belirtinin modele ek bilgi katıp katmadığına göre kesinleşir (ikizinden arındırılmış IC ve modelden çıkarıldığında geliştirme dönemi sonucu). Bu karar yalnızca 2013–2024 ile verilir ve 4. aşamadan önce sabitlenir. 1. aşama bitene kadar yeni belirti üretilmez.

## 7. Canlı test protokolü

- Canlı test dönemi 12 Ekim 2026'da başlar. İlk kayıt, 4. aşamada sabitlenen modelle yapılır; bu tarihten önceki dönem için geriye dönük kayıt yapılmaz.
- Her seçim tarihinde kaydedilir: zaman damgası, veri kesim tarihi, model sürümü ve kod commit'i, seçilen hisseler ve puanları, seçim gerekçeleri (en etkili belirtiler), kıyas yöntemlerinin seçimleri.
- 13 hafta dolmadan performans yazılmaz; sonuçlar olgunlaştıkça eklenir; maliyet ve risk ölçüleri bölüm 2.3'teki gibi.
- Model değişirse yeni sürüm ayrı numarayla kaydedilir; eski sürümün sonuçları yeni sürümün başarısı gibi gösterilmez.
- İlk değerlendirme 4 olgun çeyrekten sonra yapılır. Model A, S&P 500'ün altında kalırsa ya da Model B asgari koşulu (ortalama > %5) sağlamazsa sonuç olduğu gibi raporlanır.

## 8. Önceden yazılı karar kuralları

1. Bölüm 5'teki veri güvenilirliği kuralı tetiklenirse → ücretli çıkış fiyatı verisi alınmadan Model A sonucu kesin kabul edilmez.
2. Bölüm 6'daki dörtte bir kuralı tetiklenirse → eski belirti haritası geçersiz; harita baştan yorumlanır.
3. Model B asgari koşulu sağlamazsa → mevcut veri türleriyle büyük kazanan modellemesi bırakılır; yeni belirti değil yeni veri türü aranır.
4. Model A başarısız olursa → sistem yatırım için kullanılmaz.
5. İkincil test (2025–2026) ya da canlı test sonucu görüldükten sonra model değiştirilirse → değişen model için yeni ve kullanılmamış bir doğrulama dönemi gerekir; aynı dönemde yeniden test edilmez.

## 9. Aşama geçişleri

| Aşama | İçerik | Sonunda |
|---|---|---|
| 0 | Bu belge | Sabitlendi |
| 1 | Veri doğrulama ve çıkış senaryoları (bölüm 5–6) | Rapor, onay beklenir |
| 2 | Belirti haritası (düzeltilmiş veri), ek bilgi testleri, belirti seti kararı | Rapor, onay beklenir |
| 3a | Model A (bölüm 2) | Rapor, onay beklenir |
| 3b | Model B (bölüm 3) | Rapor, onay beklenir |
| 4 | Tek model ve ayarın sabitlenmesi (yalnızca 2013–2024 ile) | Kayıt, onay beklenir |
| 5 | İkincil test (2025–2026) bir kez + canlı kaydın başlaması | Rapor |

Her aşamanın sonunda durulur; bir sonraki aşamaya kullanıcı onayı olmadan geçilmez.

## 10. v1.1 sonuçlarıyla karşılaştırma (v1.2)

- 1. aşamanın v1.1 sonuçları (rapor commit a483c14, `asama1.json` o sürümü) silinmez ve değiştirilmez.
- Yeniden kurulan çerçevede bölünme kontrolleri **iki kez** raporlanır: v1.1 kurallarıyla (bütün olaylar tek havuzda, (c) her olaya uygulanır) ve v1.2 kurallarıyla (türlere ayrılmış, (c) yalnızca belgesiz olaylara). Her satırda pay ve payda yazılır; böylece bir olayın başarısızlıktan çıkmasının nedeni (veri düzeltmesi mi, kapsam değişikliği mi) görülebilir.
- Kapsamdan çıkarılan her olay (ihraç belgesi olan ters bölünmeler, ayrılma ve hisse temettüleri) adıyla listelenir. Kapsam dışına çıkan olay sayısı, kabul oranının yanında yazılır.
- Kabul eşikleri (±%1, ≤ 2 puan, ±%2, ≥ %99) değişmez. Yeni çerçevede eşiklerden biri yine sağlanmazsa kontrol başarısız sayılır; sonucu görüp eşik, olay türü sınırı (1,3), belge kümesi ya da bölünme algoritması değiştirilmez. Böyle bir değişiklik gerekirse yeni ön kayıt sürümü gerekir ve önceki sonuç başarısız olarak kayıtta kalır.
- Veri tanımı değişiklikleri (6.1) yalnızca hata düzeltmesidir; etkileri belirti başına (kapsama, eksik veri, değer değişimi) ölçülür. Bu aşamada belirti eklenmez, çıkarılmaz, model eğitilmez, parametre aranmaz.

## Değişiklik kaydı

### v1.1 (12 Ekim 2026, sonuçlara bakılmadan; kullanıcı incelemesi üzerine)
1. **Veri doğrulama toleransları daraltıldı ve türlerine ayrıldı** (bölüm 6). v1.0'daki bölünme için ±%50 ve finansal değerler için ±%35 toleransları, hatalı veriyi doğrulanmış sayabilecek kadar genişti. Yerine: bölünme oranı ±%1, piyasa değeri sürekliliği ≤ 2 yüzde puan, kapak sayfası kontrolü ±%2; tablo kalemleri ±%0,5; oranlar pay ve paydası ayrı doğrulanıp ±%1.
2. **A2 düşüş koşulu** mutlak büyüklük üzerinden yazıldı, örnekle.
3. **Model B:** iki ölçütün bağımsız olmadığı ve %15'in operasyonel hedef olduğu (S&P × 3'ü kanıtlamadığı) açıklandı.
4. **Dörtte bir kuralı:** "12'den fazla" yerine "en az 12".
5. **Getiri pencereleri:** İki çeyrek başı Cuması arası 12 hafta olabildiği için (ör. 7 Ocak → 1 Nisan) 13 haftalık sabit pencereler örtüşebiliyordu. Pencere, bir sonraki ölçüm tarihine kadar tanımlandı; tarih tablosu 1. aşamada üretilip kontrol edilecek.
6. **Newey–West** uygulama ayrıntısı (Bartlett, 4 gecikme, küçük örneklem düzeltmesi yok, kendi uygulama ve doğrulaması) yazıldı.

### v1.2 (13 Ekim 2026, 1. aşamanın ilk koşusu görüldükten sonra; kullanıcı kararlarıyla)

Bu değişiklikler 1. aşamanın ilk sonuçları görüldükten sonra yapıldı. Amaç, ilk koşudaki başarısızlıkları sonradan başarılı göstermek değildir; v1.1 sonuçları yerinde kalır ve bölüm 10'daki gibi yan yana raporlanır.

1. **(c) kontrolünün kapsamı (6.3).** *Neden:* Ters bölünme yapan şirketler çoğunlukla bölünmeden hemen sonra yeni hisse satıyor (ilk koşuda ilk rapordaki sayı bizimkinden medyan %17 fazla). Bu, ekonomik olarak gerçek bir hisse artışıdır; ±%2 kuralı onu veri hatası sayıyordu. *Uygulandığı olaylar:* yalnızca bağımsız ihraç belgesi (424B*, 8-K 3.02) bulunan bölünme ve ters bölünmeler kapsam dışına alınır. Belgesi bulunmayan olaylar kontrolde kalır ve ayrıca sınıflandırılır. *Gelecek sürümlerde:* bu kural bölünme türünden bağımsızdır.
2. **Ayrılma ve hisse temettüsü ayrı tür (6.2).** *Neden:* Yahoo bunları da "bölünme" olarak kaydediyor (ör. ADP–CDK 2014, AIV 2020). Ayrılmada piyasa değerinin düşmesi gerçek bir ekonomik olaydır (değer yeni şirkete geçer), hisse sayısı oranı tanımsızdır. *Uygulandığı olaylar:* 1/1,3 < r < 1,3 (ilk koşuda 395 olay). Bu olaylar silinmez; ayrı tablo olarak raporlanır.
3. **Hisse sayısı yedeği kaldırıldı (6.1-1).** *Neden:* Ön kayıt dönem sonu sayısını tanımlar; ağırlıklı ortalama farklı bir ölçüdür (ilk koşuda %10,5'i %20'den fazla sapıyor, birim hatası örnekleri var) ve 807 şirkette satırların %9,2'sini dolduruyordu.
4. **Borç tanımı (6.1-2).** *Neden:* `LongTermDebt` kısa vadeli kısmı içerdiği hâlde kısa vadeli kısım ikinci kez ekleniyordu (çift sayım). Kapsamı belirlenemeyen gözlemler belirsiz olarak işaretlenir.
5. **Bölünme oranı olay kayıtlarından (6.1-3).** *Neden:* Fiyat oranından türetilen düzeltme, temettü kaymasını bölünme anında hisse sayısına ekliyordu (ilk koşuda 65 olay, yüksek temettülü şirketler) ve bölünme kaydı olmayan hisselerde 6.568 hücreyi değiştiriyordu. Hisse sayısının geçerli olduğu tarih olarak raporun kabul tarihi yerine sayının kendi tarihi (kapak ya da bilanço tarihi) alınır; çünkü kabul tarihinden önce gerçekleşen bir bölünme, sayının tarihi bölünmeden önceyse sayıya yansımamıştır.
6. **Kabul hesabı türlere göre ayrı (6.2).** Bölünme ve ters bölünme ayrı ayrı ≥ %99 koşuluna tabidir; tek havuzda yüksek orana sahip türün düşük olanı gizlemesi önlenir. Bu, v1.1'den daha sıkı bir kuraldır.

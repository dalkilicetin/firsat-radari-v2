# Piyasa Mekanizmaları Araştırma Motoru — Ana Plan

> Bu belge **ne** yapılacağını ve **neden** yapılacağını anlatır.
> **Nasıl** yapılacağı adım adım `GOREVLER.md` dosyasında yazıyor. Kod yazacak model önce `CLAUDE.md` dosyasını, sonra ilgili görevi okumalı.
>
> **Güncel durum (karar):** Günlük veri indirilmeyecek, Actions kullanılmayacak. İlk aşama bir **laboratuvar**: tarihî kriz kataloğu + simülasyon + repodaki örnek veri (`GOREVLER.md`, L0–L8). Aşağıdaki mekanizma kataloğu ve araştırma disiplini geçerliliğini koruyor. Gerçek veriyle tam test (`ILERIDE-GERCEK-VERI.md`) laboratuvar sonuçlarına göre sonra yapılacak.

## 0. Tek cümlede amaç

Piyasada tekrar eden yapısal durumları (yay, baraj, sarkaç…) **ölçülebilir hipotezlere** dönüştürmek. Her birini 30+ yıllık veride, birden fazla piyasada ve "hile yapmadan" (geleceği görmeden, eşik oynamadan) test etmek. Sonra sadece testi geçenleri haftalık bir panoda canlı izlemek.

Bu bir al-sat botu değil, bir **keşif ve doğrulama** sistemidir. Bir mekanizmanın çalışmadığını kanıtlamak da başarılı bir sonuçtur.

---

## 1. Mevcut sistemle ilişkisi

| | Klasik Radar (`scanner.mjs`) | Analiz Radarı (`/analiz/`) | **Mekanizma Motoru (yeni)** |
|---|---|---|---|
| Soru | Bugün hangi hisse ilginç? | Bu hissenin 3 aylık görünümü ne? | Hangi piyasa **durumu** geçmişte işe yaradı ve şu an o durumda mıyız? |
| Veri | ~5 yıl aylık kapanış + anlık temel veri | — | Laboratuvar: kriz kataloğu + simülasyon + repodaki aylık/günlük örnekler. İleride: 30+ yıl günlük |
| Dil | Node | — | **Python** (pandas/numpy/scipy). İstatistik işi için doğru araç |
| Çalışma | Her gece | Haftalık | Yerelde / Claude oturumunda (`python calistir.py ...`), Actions gerekmez |

Mevcut sistemlere **dokunulmaz**. Yeni her şey `arastirma/` altına yazılır. Sonuç sayfası `/mekanizma/` altına konur ve Analiz Radarı'nın `stil.css` dosyasını kullanır. Tek ortak nokta, iki radarın üst menüsüne konacak bir bağlantıdır (son faz).

v5.16'dan gelen ipuçları bu projeyi destekliyor:
- **⚡ Şok** (günlük ≤ −%8): 5 gün sonra +%5. Bu hisse düzeyinde kısa vadeli bir **yay**.
- **Trend + düzeltme**: güçlü trendde soluklanan hisseler SPY'ı geçiyor. Bu da yükseliş trendi içinde bir yay.
- **Rejim filtresi** (son 20 gün getirisi) işe yaramadı. Bu yüzden Kırılma Noktası mekanizması daha zengin değişkenlerle denenmeli.

---

## 2. Mekanizma kataloğu (11 mekanizma)

Kullanıcının verdiği 8 fikre 3 yeni bakış açısı eklendi: Kenetlenme, Gelgit, Mıknatıs. Her mekanizmanın dört parçası var:
**Gerilim** (ne birikiyor), **Tetik** (ne boşaltıyor), **Ölçüm** (veriyle nasıl yakalanıyor), **Hipotez** (neyi test ediyoruz).

### Seviye ve veri uygunluğu

| # | Mekanizma | Seviye | Veri (ücretsiz + geçmişe dönük) | Faz |
|---|---|---|---|---|
| 1 | 🌀 **Yay** (endeks) | Endeks | Fiyat + VIX + kredi spread'i ✅ | 1 |
| 1b | 🌀 **Yay** (hisse) | Hisse | Fiyat ✅ (hayatta kalan yanlılığı ⚠️) | 1 |
| 7 | 🛡️ **Gizli güç** | Hisse | Fiyat ✅ | 1 |
| 8 | ⚡ **Kırılma noktası** | Endeks/sektör | Fiyat + makro ✅ | 1 |
| 9 | 🔗 **Kenetlenme** (yeni) | Endeks | Fiyat ✅ | 2 |
| 10 | 🌊 **Gelgit** (yeni) | Makro | FRED ✅ | 2 |
| 2 | 🧱 **Baraj** | Hisse | Fiyat + hacim ✅ | 2 |
| 11 | 🧲 **Mıknatıs** (yeni) | Hisse | Fiyat ✅ | 2 |
| 4 | 🏔️ **Çığ** | Hisse | Fiyat ✅ (haber yerine "anormal gün") | 2 |
| 6 | 🁢 **Domino** | Sektör→hisse | Fiyat ✅ | 3 |
| 3 | 🪢 **Gerilmiş lastik** | Hisse | SEC EDGAR temel veri ✅ (ağır) | 3 |
| 5 | ⏱️ **Sarkaç** | Sektör | SEC EDGAR + fiyat ⚠️ | 3 |

Analist tahmin geçmişi, opsiyon pozisyonları ve fon akışları ücretsiz ve güvenilir bir geçmişle bulunamıyor. Bunlara dayanan alt fikirler **kapsam dışı**. Aşağıda yerine konan vekil (proxy) ölçümler yazılı.

---

### 2.1 🌀 Yay — aşırı sıkışma ve geri dönüş (ÖNCELİK 1)

Kullanıcının asıl sorusu. İki ayrı soru olarak ele alınır.

**A) Endeks yayı: piyasa ne zaman "yeterince sıkıştı"?**

Gerilim bileşenleri (her biri sürekli bir skor, eşik değil):
- `dd`: Endeksin 252 günlük zirvesinden düşüşü.
- `vix_z`: VIX'in 252 günlük z-skoru. VIX'in olmadığı piyasalarda 20 günlük gerçekleşmiş oynaklığın z-skoru kullanılır.
- `vade_yapisi`: VIX / VIX3M > 1 ise panik var demektir (ters vade yapısı, 2006'dan beri).
- `genislik`: Evrendeki hisselerin kaçta kaçı 200 günlük ortalamanın altında. Hayatta kalan yanlılığına karşı ikinci bir ölçüm de var: 11 sektör ETF'sinden kaçı 200 günlük ortalamanın altında.
- `hiz`: Düşüşün hızı (20 günlük getiri). Hızlı düşüş zorunlu satışa, yavaş düşüş ekonomik bozulmaya işaret eder.

**Panik mi, bozulma mı?** Bu ayrımı yapan "tür" değişkenleri:
- Kredi spread'i (`BAA10Y`, 1986'dan beri) 60 günde ne kadar açıldı.
- Sahm kuralı (`SAHMREALTIME`): resesyon başladı mı.
- Getiri eğrisi (`T10Y3M`).
→ **Panik** = gerilim yüksek, kredi sakin. **Bozulma** = gerilim yüksek, kredi açılıyor veya Sahm tetiklenmiş.

Boşalma işaretleri ("satış baskısı zayıflıyor"):
- `vix_dusus`: VIX, 20 günlük zirvesinden %20+ geriledi.
- `genislik_itkisi`: 20 günlük ortalamanın üstündeki hisse oranı 10 gün içinde <%15'ten >%50'ye çıktı (Zweig tipi itki).
- `vade_normal`: VIX/VIX3M 1'in üstünden altına döndü.
- `fiyat_teyidi`: Endeks gerilim durumundayken 10 günlük zirvesinin üstünde kapattı.
- `ayrisma`: Endeks yeni dip yaptı ama yeni 20 günlük dip yapan hisse sayısı azaldı.

Hipotezler:
- **Y1** — Gerilim yüksekken (ör. bileşik skor en üst %5'te) sonraki 63/126 günlük getiri, koşulsuz getiriden yüksektir.
- **Y2** — Gerilim + boşalma işareti, tek başına gerilime göre **daha az ek düşüş** (MAE) ile benzer getiri verir. Kullanıcının "toparlanmadan hemen önceki bölge" sorusunun ölçülebilir hâli budur.
- **Y3** — Panik türü yaylar, bozulma türü yaylardan daha güçlü geri döner.
- **Y4** — Y1–Y2 ABD dışında (DAX, Nikkei, FTSE, BIST100) da geçerlidir. Gerçek bir mekanizma tek piyasaya özgü olmamalı.

Ana görsel: **düşüş kovası × VIX kovası ısı haritası**. Her hücrede 63 günlük medyan getiri, olay sayısı ve en kötü ek düşüş yazar. Tek eşik seçmeye gerek kalmaz; yayın "sertliği" doğrudan görülür.

**B) Hisse yayı ve 🛡️ Gizli güç — birbirine rakip iki hipotez**

Bu iki fikir **zıt bahislerdir**. Kriz bitince hangisi kazanır?
- **Hisse yayı**: Krizde en çok düşenler en çok toparlanır. Literatürde "momentum çöküşü" olarak biliniyor (Daniel & Moskowitz 2016). Ayı piyasası dibinden sonra en çok düşmüş hisseler sert yükselir.
- **Gizli güç**: Krizde en az düşenler, toparlanmada da lider olur.

Test (her düşüş dönemi için):
1. Dönem: endeks −%10'u geçti. Başlangıç = son zirve.
2. Değerlendirme günü = **boşalma işaretinin ilk çıktığı gün**. Gerçek dip KULLANILMAZ, çünkü o gün gerçek zamanda bilinemez.
3. Her hissenin dönem getirisi ve beta'dan arındırılmış kalıntı getirisi hesaplanır. Beta, dönem öncesi 252 güne göre bulunur.
4. Hisseler 5 dilime ayrılır. Her dilimin sonraki 21/63/126/252 günlük getirisi, evrenin eşit ağırlıklı getirisine göre ölçülür.
5. Sonuçlar ayrıca kırılır: panik/bozulma türü, büyüklük, dönem öncesi oynaklık.

Hipotezler:
- **G1** — Gizli güç dilimi (en az düşen kalıntı) 126–252 günde evreni geçer.
- **G2** — Yay dilimi (en çok düşen) 21–63 günde evreni geçer.
- **G3** — Hangisinin kazanacağını dönemin türü (panik/bozulma) belirler.

G3 doğrulanırsa sistemin asıl değeri bu olur: "Bu krizde yay mı oynanır, gizli güç mü?"

Ayrıca v5.16'daki tekil **şok yayı** (tek gün ≤ −%8) 30 yıllık veride tekrar test edilir. Hangi koşullarda toparlanıyor: trendde mi, kalitede mi, piyasa genelinde mi?

### 2.2 ⚡ Kırılma noktası — rejim değişimi (ÖNCELİK 1)

Önce rejimler **basit ve şeffaf kurallarla** etiketlenir. Kara kutu kullanılmaz.
- Trend: endeks 200 günlük ortalamanın üstünde mi, altında mı.
- Oynaklık: 63 günlük gerçekleşmiş oynaklık, geçmiş yüzdeliğinde 70'in üstünde mi.
- → 4 rejim: Sakin yükseliş / Oynak yükseliş / Sakin düşüş / Oynak düşüş. Gürültüyü bastırmak için rejim en az 10 gün sürmeli (histerezis).

Geçişten **önce** gözlenen öncü değişkenler:
- Genişlik ayrışması: endeks yükselirken 200 günlük ortalamanın üstündeki hisse oranı düşüyor.
- Liderlik değişimi: sektör sıralamasının 63 günlük sıra korelasyonu (devir hızı).
- Momentum faktörünün çöküşü: 12-1 momentum'da üst ve alt dilim farkının son 21 gündeki getirisi.
- Korelasyon (bkz. Kenetlenme), VIX'in oynaklığı, kredi spread'inin eğimi.

Hipotez:
- **K1** — Bu değişkenler, sonraki 21/63 günde rejim değişimi olasılığını koşulsuz orana göre anlamlı biçimde artırır.

Model önce **lojistik regresyon** olacak, ileri yürüyen (walk-forward) yöntemle ve genişleyen pencereyle eğitilecek. Ölçüm: AUC, isabet/kaçırma tablosu, sinyalin dönüşe göre kaç gün gecikmeli/erken geldiği. HMM (gizli Markov modeli) isteğe bağlı bir ek; ancak sadece ileri yürüyen biçimde, geleceği görmeden.

Kırılma noktasının bir yan ürünü daha var: Her mekanizmanın sonucu **rejime göre** de kırılır. Böylece "Yay oynak düşüşte çalışıyor, sakin yükselişte çalışmıyor" gibi bilgiler ortaya çıkar.

### 2.3 🔗 Kenetlenme (yeni) — her şey birlikte hareket edince

Gerilim: Krizlerde hisseler arası korelasyon 1'e yaklaşır. Herkes aynı anda satar, çeşitlendirme ortadan kalkar. Bu "sürü sıkışması" bir yay türüdür.
- Ölçüm: En büyük 100 hissenin 63 günlük getirilerinin ortalama ikili korelasyonu. Ayrıca kesitsel dağılım (günlük getirilerin kesitsel standart sapması).
- **KN1** — Korelasyon zirvesi kapitülasyonla çakışır. Zirveden düşüş, endeks toparlanmasına öncülük eder.
- **KN2** — Düşük korelasyon / yüksek dağılım dönemlerinde hisse seçme stratejileri (Gizli güç, Mıknatıs) daha iyi çalışır.

### 2.4 🌊 Gelgit (yeni) — likidite bütün tekneleri kaldırır

Hisseye özgü olmayan, "su seviyesi" mekanizması.
- Ölçüm: Chicago Fed finansal koşullar endeksi (`NFCI`, 1971'den beri), Fed bilançosu (`WALCL`, 2002'den beri) 13 haftalık değişimi, reel faiz (`DFII10`), dolar endeksi (`DTWEXBGS`).
- **GL1** — Likidite gevşerken (NFCI düşüyor) sonraki 63–126 günlük endeks getirisi daha yüksektir.
- **GL2** — Yay sinyali gelgit lehteyken daha güçlüdür (etkileşim testi).

### 2.5 🧱 Baraj — sıkışma sonrası kırılım

- Gerilim: ATR(14)/fiyat oranı, hissenin kendi 1 yıllık geçmişinin en alt %10'unda. 40 günlük fiyat aralığı dar (Bollinger bant genişliği düşük). Sıkışma süresi (gün) ayrıca kaydedilir.
- Tetik: 40 günlük zirvenin üstünde kapanış (yukarı kırılım) veya dibin altında kapanış (aşağı kırılım).
- Destekleyiciler: Sektör ETF'sine göre göreli güç (RS), 52 haftalık zirveye yakınlık (Mıknatıs), sıkışma sırasında hacmin daralması ve kırılım günü hacmin artması.
- **B1** — Sıkışma, sonraki hareketin **büyüklüğünü** öngörür (|getiri|) ama **yönünü** öngörmez. Bu beklenen bir sonuçtur ve kontrol amaçlı test edilir.
- **B2** — Sıkışma + RS + zirveye yakınlık birlikteyse yukarı kırılımın 21/63 günlük başarısı artar ve başarısızlık oranı düşer. Başarısızlık = 10 gün içinde aralığa geri dönüş.

### 2.6 🧲 Mıknatıs (yeni) — 52 haftalık zirvenin çekimi

Yatırımcılar 52 haftalık zirveye "çapa" atar. Zirveye yakın hisse haberi yavaş fiyatlar (George & Hwang 2004).
- Ölçüm: fiyat / 52 haftalık zirve.
- **M1** — En üst dilim sonraki 63–126 günde evreni geçer.

Bu mekanizmanın ikinci bir rolü var: **motorun pozitif kontrolü**. Literatürde bilinen bir etkiyi yeniden üretemiyorsak motorda hata var demektir.

### 2.7 🏔️ Çığ — küçük olay, büyük hareket

Haber verisi yerine **anormal gün** kullanılır. Anormal gün = beta'dan arındırılmış günlük getirinin |kalıntı|'sı > 3σ (60 günlük) ve hacmin 20 günlük ortalamanın 2 katından fazla olması. Bilanço günleri çoğunlukla zaten böyle görünür.
- Olaydan **önceki** koşullar: RS, zirveye yakınlık, önceden sıkışma (Baraj), trend yönü.
- **C1** — Aynı büyüklükteki olumlu olaylar, olay öncesi koşullar "hazır" iken daha büyük olay sonrası kayma (drift) yaratır. Ölçüm: olay+1'den olay+63'e kadar kalıntı getiri.
- Opsiyon ve açığa satış verileri kapsam dışı. FINRA'nın iki haftada bir yayımlanan açığa satış verisi Faz 3+ için isteğe bağlı.

### 2.8 🁢 Domino — sektörden sektöre, liderden takipçiye yayılma

- **D1** (sektör içi): Sektörün en büyük 3 hissesinde olumlu anormal gün olduğunda, aynı sektörün o gün tepki vermeyen hisseleri sonraki 5–20 günde sektörü yakalar mı?
- **D2** (sektörler arası): Haftalık sektör ETF getirileri, diğer sektörlerin sonraki 1–4 haftasını öngörüyor mu? Ölçüm: ileri yürüyen öncü-gecikmeli korelasyon matrisi ve bu ilişkilerin kararlılığı.

### 2.9 🪢 Gerilmiş lastik — fiyat ile temel veri arasında kopukluk

Kaynak: SEC EDGAR `companyfacts`. Ücretsiz, 2009 sonrası XBRL, **dosyalama tarihli**. Bu sayede o gün gerçekten bilinen veri kullanılabilir.
- Temel ivme: Son 4 çeyreklik gelir büyümesinin bir önceki döneme göre değişimi, brüt marj değişimi, serbest nakit akışı marjı değişimi → evrende yüzdelik.
- Fiyat ivmesi: 6 aylık getirinin evrendeki yüzdeliği.
- Kopukluk = temel yüzdelik − fiyat yüzdeliği.
  - **L-B** (temel iyi, fiyat geride): sonraki 3–12 ayda evreni geçer mi?
  - **L-A** (fiyat koştu, temel yok): sonraki dönemde geride kalır mı?
- Analist tahminleri kapsam dışı.

### 2.10 ⏱️ Sarkaç — beklentilerin uçlara gitmesi

- Sektör düzeyinde: EDGAR'dan toplam kâr / toplam piyasa değeri (sektör F/K), sektörün 5 yıllık getirisinin evrendeki yüzdeliği, sektörün piyasa içindeki ağırlığı.
- **S1** — Değerleme ve ağırlık tarihsel uçtayken sektörün sonraki 1–3 yıllık göreli getirisi ters yöndedir.
- Örneklem çok küçük. Burada istatistiksel kanıttan çok **durum göstergesi** ("sarkaç şu an nerede") üretilir. Rapor bunu açıkça yazar.

---

## 3. Araştırma disiplini — bu bölüm pazarlık konusu değil

Güzel görünen hikâyeleri ayıklamanın tek yolu bu kurallar.

1. **Geleceği görmeme.** t günündeki her özellik sadece t ve öncesindeki veriyle hesaplanır. Sinyal t kapanışında oluşur, giriş t+1 kapanışında yapılır. Gelecek getiriler **sadece** `sonuc.py` içinde hesaplanır. Temel veri, dosyalama tarihinden **1 gün sonra** kullanılabilir.
2. **Önceden kayıt.** Her hipotezin eşikleri, ufukları ve başarı ölçütü testten **önce** `hipotezler/*.yaml` dosyasına yazılır. Sonradan eşik değiştirilirse eski sonuç silinmez. `deneme_gunlugu.csv` dosyasına yeni bir satır eklenir. Toplam deneme sayısı rapora yazılır ve anlamlılık eşiği buna göre sıkılaştırılır (Holm düzeltmesi + deflated Sharpe).
3. **Örtüşmeyen olaylar.** Aynı olayın art arda günleri tekrar sayılmaz. Sinyalden sonra ufuk kadar (ör. 63 gün) bekleme uygulanır. Ayrıca "bağımsız bölüm sayısı" ayrıca raporlanır. 2008 krizi 200 gün sinyal verse de **1 bölümdür**.
4. **Belirsizlik.** Her ortalamanın yanında blok bootstrap ile %90 güven aralığı verilir. Hisse düzeyi testlerde Newey-West t-istatistiği kullanılır. Bağımsız bölüm sayısı 10'un altındaysa sonuç "vaka çalışması" diye etiketlenir.
5. **Zaman dışı test.** Ana bölünme: 1990–2009 keşif, 2010–bugün doğrulama. Eşikler sadece keşif döneminde seçilir. Ayrıca ileri yürüyen (genişleyen pencere) test yapılır.
6. **Piyasa dışı test.** Endeks mekanizmaları DAX, Nikkei, FTSE ve BIST100'de aynı eşiklerle tekrarlanır.
7. **Basit rakip.** Her mekanizma kendi en basit hâliyle yarışır. Örneğin Yay ile "−%15 düştüyse al" kuralı. Basit kuralı geçemeyen karmaşıklık atılır.
8. **Maliyet.** İşlem başı 10 bp (hisse için 20 bp) düşülür. Kısa vadeli sinyaller için maliyetin 2 katında da sonucun tuttuğu gösterilir.
9. **Kontroller.**
   - Pozitif kontrol: 12-1 momentum ve Mıknatıs, literatürdeki işaretle çıkmalı.
   - Negatif kontrol: Rastgele sinyal 200 kez çalıştırılır. Anlamlı sonuç oranı ~%10'u aşmamalı (yanlış alarm oranı).
10. **Hayatta kalan yanlılığı.** Hisse evreni bugünkü S&P 500 + Nasdaq-100 üyeleridir. Batmış şirketler yok. Bu yüzden:
    - (a) Hisse testleri hep **evrene göre göreli** ölçülür (yanlılık iki tarafta da var).
    - (b) Genişlik ölçümleri sektör ETF'leriyle teyit edilir.
    - (c) Rapor her hisse sonucunun yanına bu uyarıyı yazar.
    - (d) İsteğe bağlı: tarihsel S&P 500 üyelik listesi (açık kaynak `fja05680/sp500` CSV'si) ile "o tarihte endekste miydi" filtresi.

### Karar ölçeği (her hipotez için otomatik)

| Karar | Koşul |
|---|---|
| ✅ **Tutarlı** | Keşif ve doğrulamada aynı işaret, doğrulamada %90 GA sıfırı dışlıyor, basit rakibi geçiyor, ≥10 bağımsız bölüm (hisse testinde ≥60 ay), maliyet sonrası pozitif, (endeksse) 4 yabancı piyasanın ≥2'sinde aynı işaret |
| 🟡 **Zayıf** | Aynı işaret ama GA sıfırı içeriyor, veya bölüm sayısı az |
| ⚪ **Yok** | İşaret tutarsız veya etki ≈ 0 |
| 🔴 **Ters** | Doğrulamada anlamlı ters işaret. Bu da değerli bir bilgi |

Canlı panoda sadece ✅ ve 🟡 mekanizmalar sinyal üretir. ⚪/🔴 olanlar "test edildi, çalışmıyor" diye listelenir.

---

## 4. Veri — laboratuvar aşaması

İnternetten veri çekilmez. Üç kaynak kullanılır:

| Kaynak | İçerik | Ne için |
|---|---|---|
| `tarih/kriz_katalogu.csv` | 13 S&P 500 düşüşü (1987–2025) + 2 karşı örnek (Nikkei 1989, Nasdaq 2000). Zirve/dip/toparlanma tarihleri, VIX zirvesi, resesyon, kredi stresi, politika tepkisi | Yayların "anatomisi": hız ↔ toparlanma, panik ↔ bozulma. Hipotez **üretir**, kanıtlamaz (n=13) |
| Simülatör (`mekanizma/sim/`) | Temel değer (F) + sapma (m = yay gerilimi, OU süreci) + panik ve bozulma şokları + VIX/kredi/Sahm vekilleri + 200 hisse (beta, kalite, aşırı tepki). Katalog istatistiklerine kalibre edilir | Ölçüm aletini ayarlamak. Doğru cevap bilinir. Dedektör yayı tanıyor mu, yanlış alarm veriyor mu, 13 krizle neyi görebiliriz? |
| `data/sonuclar.json` | 154 hisse + 26 ETF, 61 aylık kapanış (2021-10 → 2026-10): **2022 ayı piyasası**, 2025 tarife düşüşü, 2026 Mart düşüşü | Gerçeklik kontrolü: iki doğal deney (2022 = bozulma, 2025 = panik) |
| Git geçmişi (103 gece) | ~600 hisse günlük fiyat + `r13w r52w mtd` (2026-07 → 2026-10) | Günlük şok yayı kontrolü |

Katalog değerleri model bilgisinden **yaklaşık** yazıldı. `guven=orta` satırları bir grafikte kontrol edilmeli.
Örnek verideki hisseler küratörlü (teknoloji ağırlıklı) ve hayatta kalanlardan oluşuyor. Raporlar bunu açıkça yazar.

**Laboratuvarın mantığı:**
- Tarih "neye bakmalıyız" der.
- Simülasyon "baktığımız aletle görebilir miyiz" der.
- Örnek veri "gerçekte, küçük ölçekte, öyle mi" der.

Üçü aynı yönü gösterirse gerçek günlük veriye yatırım yapmaya değer.

## 5. Mimari

```
arastirma/
  CLAUDE.md              ← kod yazan model için kurallar (kısa)
  PLAN.md  GOREVLER.md
  requirements.txt       ← pandas numpy scipy pyarrow requests pyyaml statsmodels scikit-learn pytest jinja2 (sürümler sabit)
  calistir.py            ← CLI:  veri | test <mekanizma|hepsi> | pano | saglik
  hipotezler/*.yaml      ← önceden kayıtlı hipotezler
  deneme_gunlugu.csv
  tarih/     kriz_katalogu.csv  inceleme.py          ← laboratuvar
  mekanizma/
    sim/       piyasa.py  deneyler.py                 ← laboratuvar
    veri/      ornek.py  katalog.py  (ileride: kaynaklar.py onbellek.py evren.py saglik.py)
    ozellik/   fiyat.py  genislik.py  korelasyon.py  rejim.py  makro.py  temel.py
    motor/     sonuc.py  olay.py  kesit.py  istatistik.py  ileri.py  karar.py  kontrol.py
    mekanizmalar/  taban.py  yay.py  hisse_yay.py  kirilma.py  kenetlenme.py  gelgit.py
                   baraj.py  miknatis.py  cig.py  domino.py  lastik.py  sarkac.py
    rapor/     json_yaz.py  html_yaz.py  sablonlar/
  testler/   (pytest; sentetik veri + ornek/)
  sonuclar/  (git'e girer)
mekanizma/   (yayın sayfaları: index.html + her mekanizma için bir sayfa; ../analiz/stil.css kullanır)
(ileride) .github/workflows/mekanizma.yml
```

**Ortak sözleşme** (her mekanizma bunu uygular, `taban.py`):

```python
class Mekanizma:
    ad: str; seviye: Literal["endeks","hisse","sektor","makro"]
    def ozellikler(self, v: Veri) -> pd.DataFrame        # index=tarih (+ sembol), sadece geçmiş veri
    def sinyaller(self, oz, h: Hipotez) -> pd.DataFrame  # tarih, [sembol], skor, tur, bilesenler(json)
    def durum(self, oz) -> dict                          # BUGÜN: gerilim seviyesi, bileşenler, en yakın tarihsel benzerler
```

Motor iki test türünü tek tip çalıştırır:
- **`olay.py`** (endeks/makro): sinyal tarihleri → ayıklanmış olaylar → ileri getiri, MAE, toparlanma süresi, bölüm tablosu, bootstrap GA, keşif/doğrulama ayrımı, rejim kırılımı, koşulsuz ve basit rakip karşılaştırması.
- **`kesit.py`** (hisse): her ayın son günü skor → 5 dilim → evrene göre ileri göreli getiri, sıra IC, uzun-kısa fark, Newey-West t, dilim devir hızı, maliyet sonrası.

`karar.py`, Bölüm 3'teki tabloyu otomatik uygular. `kontrol.py` pozitif ve negatif kontrolleri çalıştırır.

**"Tarihsel benzer" (analog) çıktısı**, kullanıcıya en anlaşılır olan şey: "Bugünkü yay gerilimine en yakın 10 geçmiş an: 2011-08, 2018-12, 2020-03… Bunların 63 gün sonrası: 8 yükseliş, 2 düşüş, medyan +%9, en kötü ek düşüş −%7." Benzerlik, standartlaştırılmış bileşenler üzerinde öklid uzaklığıyla ölçülür. Benzerler, bekleme kuralıyla farklı bölümlerden seçilir.

---

## 6. Fazlar ve teslimatlar

| Faz | İçerik | Görevler |
|---|---|---|
| **Lab-0** | İskelet + örnek veri yükleyici | L0, L1 |
| **Lab-1 — Tarih** | Kriz kataloğu incelemesi → hipotez listesi | L2 ⛔ |
| **Lab-2 — Alet** | Ortak özellikler + motor + Yay dedektörü + simülatör | L3, L4, L5 |
| **Lab-3 — Deney** | Kalibrasyon, ayırt edilebilirlik, boşalma/MAE, sahte yay, güç analizi, hisse yayı ⟷ gizli güç | L6 ⛔ |
| **Lab-4 — Gerçeklik** | 2022/2025/2026 doğal deneyleri, günlük şok yayı | L7 |
| **Lab-5 — Rapor** | `sonuclar/LAB-RAPORU.md` + karar tablosu + sonraki adım önerisi | L8 ⛔ |
| Sonra | Diğer mekanizmalar laboratuvara; gerçek günlük veri (`ILERIDE-GERCEK-VERI.md`); canlı pano | — |

## 7. Riskler ve dürüst beklenti

- **Örneklem küçük.** 1990'dan beri ABD'de ~12–15 bağımsız ciddi düşüş var. Endeks yayı büyük olasılıkla "vaka çalışması" seviyesinde kalacak. Yabancı piyasalar bunu biraz genişletir ama mucize beklenmemeli.
- **Yahoo resmî bir API değil.** Kaynak zinciri ve önbellek bu yüzden var.
- **Hayatta kalan yanlılığı** hisse yayını iyimser gösterir, çünkü batan "en çok düşenler" veride yok. Hisse yayı sonucu ✅ çıksa bile bu yüzden bir kademe düşürülerek okunmalı. Rapor bunu otomatik yazar.
- **Rejim değişir.** 2010 sonrası Fed desteği yayları güçlendirmiş olabilir. Keşif/doğrulama ayrımı bunu kısmen yakalar.
- Bu sistem yatırım tavsiyesi değildir. Panoda bu açıkça yazar.

---

## 8. Sonnet ile çalışma yöntemi (token tasarrufu)

- Her oturumda tek görev verin: *"arastirma/CLAUDE.md ve arastirma/GOREVLER.md içindeki L3'ü uygula."*
- Görevler bağımsız ve küçük tutuldu. Her birinde dosya listesi, formüller, parametreler ve kabul testleri var. Model planlamaya değil uygulamaya odaklanır.
- Her şey Claude oturumunda çalışır (`pip install -r requirements.txt` yeterli). Actions ve API anahtarı gerekmez.
- ⛔ noktalarında Opus'a şunu söyleyin: *"sonuclar/ içindeki son raporları oku, yorumla, sızıntı/hata var mı bak."*
- Bir sonuç fazla iyi çıkarsa (ör. her şey 🟢), önce sızıntı şüphesiyle inceleyin.

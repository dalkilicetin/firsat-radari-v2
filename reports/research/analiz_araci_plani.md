# Fırsat Radarı — Analiz Aracı: Final Plan (v2)

**Tarih:** 20 Ekim 2026. **Durum:** plan; kullanıcı onayı bekliyor.
**v2'deki değişiklikler:** kesin test kuralları, yakalanabilir getiri, otopsi detay kartı, iki gruplu alınmaz süzgeci ve ölçümü, genişletilmiş karne ölçütleri, telefona uygun görünüm.

## Amaç
Her cuma en fazla 10 hisselik bir öneri listesi çıkarmak. Her hissenin yanında sade Türkçeyle "neden listede, neden almamalı" yazacak. Karar her zaman kullanıcıda.

## Sabit kararlar
| Konu | Karar |
|---|---|
| Tarama | Haftalık. Veri perşembe kapanışına göre hazırlanır; sonuçlar cuma 14:00'te (TR) hazır olur. |
| Vade | Her hisse için 3 ve 6 aylık uygunluk ayrı gösterilir. |
| Büyüklük (o günkü değerle) | Piyasa değeri ≥ 500 milyon $, fiyat ≥ 5 $, günlük işlem ≥ 5 milyon $. Orta boy şirketler (2–10 milyar $) öncelikli. |
| Liste | En fazla 10 hisse; aynı sektörden en fazla 3. |
| Dil | Sade Türkçe. Kesin sayılar ve kaynaklar yalnızca kapalı duran "Ayrıntılar" bölümünde. |
| Görünüm | Önce telefon: tablo yok, kartlar ve büyük dokunma alanları. Bilgisayarda da aynı sayfa genişler. |
| Veri | Yalnızca güvenilir kaynaklar: SEC belgeleri, fiyatlar, FINRA. |

## 1. Kesin test kuralları (her ölçümde aynen uygulanır)
1. **Hayatta kalma yanlılığı yok.** Geçmişte o gün borsada işlem gören her hisse evrene girer; sonradan batan, borsadan çıkarılan ya da birleşen şirketler dahil. Büyüklük sınırı o günkü değerle uygulanır, bugünkü değerle değil.
2. **Çıkış kuralları.**
   - İflas eden ya da hissesi değersizleşen şirket: hisse **0** sayılır (−%100).
   - Satın alınan / birleşen şirket: son işlem fiyatı.
   - Başka sebeple borsadan çıkan şirket: son geçerli işlem fiyatı.
   - Güvenilir fiyatı olmayan hisse o gün alınamaz sayılır ve evrene girmez.
3. **Sinyal tarihi = bilginin gerçekten yayımlandığı an.**
   - Her belge SEC'e kabul edildiği saatten itibaren kullanılır.
   - Perşembe 16:00'dan (New York) sonra gelen belge sonraki haftanın taramasına girer.
   - Hisse sayısı ve bilanço değerleri de belgenin yayım tarihine göre alınır, dönem sonu tarihine göre değil. Bu kural Aşama 1'deki K1 sorusunu da "yayım tarihine göre" diye kapatır.
4. **Uygulanabilir giriş fiyatı.** İşaretin oluştuğu fiyattan değil, rapordan sonra alınabilecek ilk fiyattan alınmış sayılır: **cuma kapanışı**.
5. **Masraflar.** Alışta ve satışta ayrı ayrı düşülür (mevcut maliyet tablosu):

   | Günlük işlem | Tek yön masraf |
   |---|---|
   | ≥ 50 M$ | %0,05 |
   | ≥ 10 M$ | %0,15 |
   | ≥ 1 M$ | %0,4 |
   | Bilinmiyor | %1 |

6. **İleriye dönük getiri.** Girişten 13 ve 26 hafta sonraki cuma kapanışına kadar, masraflar düşülerek.
7. **Üç karşılaştırma** (aynı tarihler arasında):
   - borsa (S&P 500, SPY);
   - hissenin sektör ETF'i;
   - evrendeki bütün hisselerin eşit ağırlıklı ortalaması ("benzer büyüklükteki hisseler").
8. **Ayar ve sınav ayrı.**
   - Bütün eşikler ve ağırlıklar yalnızca **2013–2022** verisiyle ayarlanır.
   - **2023–2026** sınav dönemidir: ayarlar dondurulup repoya kaydedildikten sonra bir kez açılır.
   - Sınav dönemindeki kazananların otopsisine sınavdan önce bakılmaz.
   - **Dürüst not:** 2025–2026'nın en iyi hisselerinin adlarını önceki çalışmada gördük. Bu yüzden asıl temiz sınav, canlı kayıttır: her cuma liste kilitlenir.
9. **Deneme defteri.** Denenen her ayar kaydedilir; kaç deneme yapıldığı raporda yazar.

## 2. Otopsi (her kazanan için)
**Kazanan:** O dönem evrendeki hisselerin en iyi %5'inde getiri yapan hisse (3 ve 6 ay için ayrı). Her çeyreğin ilk 20'si için tam kart hazırlanır.

### Yakalanabilir getiri
Çeyrek sonunda %200 yükselmiş olmak, bunun önceden yakalanabileceği anlamına gelmez.

**Örnek:** işaret 10 $'da oluştu, alınabilecek ilk fiyat 11 $, 3 ay sonra 20 $.
- Getiri 20 ÷ 11 − 1 = **%81,8**'dir, %100 değil.
- İşaret ancak 18 $'da oluşsaydı, getiri yalnızca %11 olurdu.

Her otopsi kartında şu **dört sonuç** ayrı gösterilir:
1. İlk güvenilir işaret tarihi.
2. İşaretten sonraki uygulanabilir giriş fiyatı.
3. Girişten itibaren 3 ve 6 aylık getiri (masraflar düşülmüş).
4. Aynı dönemde borsaya ve sektörüne göre fazla getiri.

**İlk güvenilir işaret:** Hissenin 6 işaretten en az 4'ünü ilk kez taşıdığı ve alınmaz süzgecinden geçtiği hafta. Listeye ilk girdiği hafta da ayrıca yazılır.

### Kartın üç bölümü
1. **Kazanç hikâyesi**
   - Hisse neden yükseldi?
   - Kaynağı işlerdeki gelişme mi, sektör hareketi mi, değerleme değişimi mi?
   - Yükselişin ne kadarı tek bir haberden geldi? Haber günü ve ertesi haftanın toplam yükselişteki payı ölçülür.
2. **İlk yakalanabilir işaret**
   - İlk olumlu belirti hangi tarihte oluştu?
   - O gün yatırımcı hangi bilgiye gerçekten ulaşabiliyordu? Yayımlanmış belgeler ✓, henüz olmamış olaylar ✕.
   - Hisse o noktadan sonra ne kadar getirdi?
3. **Aynı görünüp yükselmeyenler**
   - Aynı hafta aynı işaretleri veren ama yükselmeyen hisseler hangileriydi?
   - Kazananı kaybedenden hangi özellik ayırıyordu?
   - Yanılmanın ortak nedeni neydi?

## 3. Alınmaz süzgeci: iki grup ve ölçüm
**Kesin ret (şirket güvenilirliği):**
- devamlılık şüphesi;
- mali tabloları geç açıklama;
- borsadan çıkarılma uyarısı.

**Dikkat (tek başına ret sebebi değil, bağlamıyla değerlendirilir):**
- *Şirket tarafı:*
  - hisse basma / yeni hisse satışı;
  - ters bölünme;
  - nakit sıkıntısı.
- *Piyasa tarafı:*
  - düşen bıçak;
  - ucuzluk tuzağı.

Dikkat işaretinin bağlamı: Parayı neye harcayacak? Şirketin ne kadar finansmana ihtiyacı var? Fiyat haberden sonra nasıl davrandı?

**Her işaret için ayrı ayrı ölçülür** (yalnızca 2013–2022'de, 3 ve 6 ay için ayrı):

| Ölçüm | Anlamı |
|---|---|
| Kazananı koruma oranı | Kazananların yüzde kaçı süzgeçten geçiyor (yanlışlıkla elenmiyor)? |
| Kaybedeni eleme oranı | Kaybedenlerin yüzde kaçını yakalıyor? Kaybeden = borsanın gerisinde kalan hisse. |
| Listeye etkisi | Süzgeç varken ve yokken ilk 10'un medyan getirisi, borsadan fazla getirisi, kazanan bulma oranı ve en büyük düşüşü. |
| Birlikte mi, tek başına mı | İşaret tek başına mı, başka bir işaretle birlikte mi anlamlı? |

**Karar kuralı** (ölçümden önce sabitlenir):
- **Kesin ret işareti tutulur, eğer:**
  - kazananların en az %90'ını koruyorsa,
  - kaybedenleri kazananlara oranla en az 2 kat daha sık eliyorsa,
  - ve ilk 10'un medyan fazla getirisini düşürmüyorsa.
- **Bu şartları geçemeyen işaret** "dikkat" grubuna iner; kartta uyarı olarak yazar.
- **Dikkat işaretleri** puanı düşürür, otomatik ret yapmaz. İkisi birlikte görülünce ret olabilir; bu da aynı yöntemle ölçülür.

## 4. Sıralama (6 işaret)
1. Yükselişi sürüyor
2. İşleri iyileşiyor
3. Dipten kalktı
4. Sektörü yükselişte
5. İçeriden alım var
6. Yakında önemli haber var

Sıra işaret sayısına göre belirlenir; eşitlikte yükseliş gücü kazanır. Dikkat işaretleri sırayı düşürür. Ağırlıklar yalnızca 2013–2022 otopsi ve benzer analizinden çıkar. Piyasa çok dalgalıysa ya da sert düşüşten yeni çıkıyorsa 1. işaretin ağırlığı azalır.

## 5. Karne ölçütleri (yalnızca ortalama getiri değil)
| Ölçüt | Sade anlamı |
|---|---|
| İlk 10'un 3 ve 6 aylık medyan getirisi | Ortadaki hissenin getirisi (tek büyük kazanan sonucu çarpıtmasın diye) |
| Ortalama getiri | Medyanın yanında |
| Borsaya, sektörüne ve benzer büyüklüktekilere göre fazla getiri | Üç karşılaştırma |
| Kazanan bulma oranı | İlk 10'da geleceğin en çok kazandıranlarından kaç hisse vardı? Rastgele seçimle karşılaştırılır. |
| Tamamen kaçırılan kazanan oranı | Kazananların yüzde kaçı yükselişten önce hiçbir haftanın listesine girmedi? |
| Yakalanan pay | Kazananlarda yakalanabilir getirinin toplam yükselişe oranı |
| En büyük düşüş | Liste portföyünün zirveden dibe en büyük kaybı |
| Masraflar | Yıllık toplam masraf (getiriden düşülmüş) |
| Devir hızı | Liste haftada ve çeyrekte kaç hisse değişiyor? |
| Borsayı geçen dönem oranı | — |
| Güven aralığı | Her ölçüt için, şans payını göstermek amacıyla |

**Portföy testi:** Çeyrek başı listeleri birbirine karışmadan izlenir. Haftalık listelerin her biri ayrıca 3 ve 6 ay izlenir; medyan ve kazanan bulma oranı bunlardan hesaplanır.

## 6. Haftalık rapor (telefon öncelikli)
Görünüm taslağı: Fırsat Radarı — Haftalık Tarama Taslağı (5 sayfa, örnek veri).
1. **Liste:** piyasanın hali, öneri kartları, alınmaz ve dikkat listesi, yaklaşan önemli günler.
2. **Hisse kartı:** 6 işaret, benzerleri ne yaptı (borsadan çıkanlar dahil), haberler, neden almamalı, ayrıntılar.
3. **Karne:** yukarıdaki ölçütler, liste liste sonuçlar, test kuralları.
4. **Otopsi listesi:** toplam yükseliş ile yakalanabilir getiri yan yana.
5. **Otopsi detay kartı:** dört sonuç, fiyat yolu, üç bölüm.

## 7. Sıra
1. Test düzeneği: kuralları koda dökmek ve doğrulamak (batanlar, yayım saati, giriş fiyatı, masraf, üç karşılaştırma).
2. Otopsi, 2013–2022: kartlar ve yakalanabilir getiri.
3. Benzerler ve alınmaz süzgeci ölçümü.
4. Sıralama ayarı; ayarlar dondurulup kaydedilir.
5. Sınav, 2023–2026: bir kez açılır; karne yazılır.
6. Haftalık sayfa ve cuma otomatik çalışma; ilk kilitli liste.

## Bilinen sınırlar
- Devralma ve tek günlük haber sıçramaları önceden görülemez. Otopside "yakalanamazdı" diye işaretlenir.
- Büyüklük sınırı yüzünden çok küçük şirketlerin büyük sıçramaları evrenin dışında kalır.
- Haber yorumu yarı otomatik; son karar kullanıcının.

# Fırsat Radarı — Analiz Aracı: Final Plan

**Tarih:** 20 Ekim 2026. **Durum:** plan; kullanıcı onayı bekliyor.

## Amaç
Her cuma en fazla 10 hisselik bir öneri listesi çıkarmak. Her hissenin yanında sade Türkçeyle "neden listede, neden almamalı" yazacak. Karar her zaman kullanıcıda.

Yöntem değişikliği: "geleceği tahmin eden kara kutu model" yerine **"geçmiş kazananları anlayan ve bugün benzerlerini arayan analiz aracı"**.

## Sabit kararlar
| Konu | Karar |
|---|---|
| Tarama sıklığı | Haftalık. Veri perşembe kapanışına göre hazırlanır, sonuçlar cuma 14:00'te (TR) hazır olur. ABD borsası 16:30'da açılır. |
| Vade | Her hisse için 3 aylık ve 6 aylık uygunluk ayrı gösterilir. |
| Büyüklük | Piyasa değeri ≥ 500 milyon $, fiyat ≥ 5 $, günlük işlem ≥ 5 milyon $. Orta boy şirketler (2–10 milyar $) öncelikli. |
| Liste | En fazla 10 hisse; aynı sektörden en fazla 3. |
| Dil | Sade Türkçe. Teknik sayılar ve belge kaynakları yalnızca en alttaki "Ayrıntılar" bölümünde durur. |
| Veri | Yalnızca güvenilir kaynaklar: SEC belgeleri, fiyatlar, FINRA. Wikipedia, Reddit ve sosyal medya yok. |
| Dürüstlük | Her işaret, aynı görünüp kaybettiren benzerleriyle birlikte ölçülür. |

## Aşama 1 — Otopsi (geçmişi anlamak)
Yeni evrende 2013–2026 arasındaki her çeyreğin en çok kazandıran 20 hissesi incelenir (3 ay ve 6 ay için).

Her hisse için bir otopsi kartı hazırlanır:
- **Ne oldu?** Yükselişin sebebi şu türlerden biri: anlaşma, devralma, kâr sürprizi, ürün onayı, sektör dalgası, açığa satışların kapanması. Kaynak: 8-K başlıkları ve şirket bültenleri.
- **Yükselişten önce nasıl görünüyordu?** Fiyat hareketi, satışlar, kâr, yönetici alımları, büyük fon hareketleri, hisse ihracı.
- **İlk işaret ne zaman görüldü** ve o anda hisse ne kadar yükselmişti?
- **Kazancın ne kadarı ilk işaretten sonra geldi?** Yani ne kadarı yakalanabilirdi?
- **O gün alınabilir miydi?** İşlem hacmi, fiyat, sulandırma riski.

Çıktı: Kazanan tipleri ve her tipin "önceden görülebilir mi, yakalanabilir mi" karnesi.

## Aşama 2 — Benzerler ve alınmaz süzgeci
1. Her kazanan tipi için yükselişten önce **aynı görünen bütün hisseler** bulunur. Bunların kaçının kazandırdığı ölçülür. Böylece işaret kazananlarda sık görülüyor diye değil, gerçekten işe yaradığı için seçilir.
2. **Alınmaz süzgeci:**
   - devamlılık şüphesi;
   - mali tabloları geç açıklama;
   - borsadan çıkarılma uyarısı;
   - son 12 ayda hisse sayısının %20'den fazla artması ya da yeni hisse satışı;
   - ters bölünme;
   - zirveden %70'ten fazla düşmüş olup hâlâ düşmesi;
   - satışlar düşerken zararın büyümesi;
   - 12 aydan az yetecek nakit.

   Süzgeç benzerlerle sınanır: kaybettirenleri kazananlardan çok daha fazla eliyorsa tutulur. AGL, RILY ve IHRT'nin o tarihlerde hangi işaretleri taşıdığı tek tek kontrol edilir.
3. Eksik veri eklenir: FINRA açığa satış verisi (ücretsiz). Ürün onay tarihleri ise yalnızca gerekiyorsa eklenir.

## Aşama 3 — Sıralama (6 işaret)
Her işaret ya var ya yok:
1. **Yükselişi sürüyor.** Son 1 yılda hisselerin çoğundan çok yükselmiş ve zirvesine yakın.
2. **İşleri iyileşiyor.** Satışlar en az %20 artıyor ve artış hızlanıyor, ya da beklenenden iyi kâr açıklamış.
3. **Dipten kalktı.** En düşük fiyatının en az 2 katında.
4. **Sektörü yükselişte.**
5. **İçeriden alım var.** Yöneticiler kendi parasıyla alıyor ya da büyük bir fon yeni ortak oldu.
6. **Yakında önemli bir haber bekleniyor.** Bilanço, onay kararı ya da yatırımcı günü.

Sıra, işaret sayısına göre belirlenir; eşitlikte yükseliş gücü kazanır. İşaretlerin önemi Aşama 1–2'nin sonucuna göre, yalnızca 2013–2022 verisiyle ayarlanır.

Piyasa çok dalgalıysa ya da sert düşüşten yeni çıkıyorsa 1. işaretin ağırlığı azaltılır.

## Aşama 4 — Geçmişe uygulama (sınav)
Aracın aynı ayarlarıyla her çeyreğe yalnızca o güne kadarki veriler kullanılarak "o gün ne önerirdi?" sorusu sorulur. Sonuçlar ana analiz tablosuna konur: her dönem için o dönemin en iyi 3'ü, bizim 10'umuz ve S&P yan yana.
- **Ayar dönemi:** 2013–2022.
- **Sınav dönemi:** 2023–2026, yalnızca bir kez açılır.
- **Gerçekçi hedef:** 10 hissenin S&P'yi geçmesi ve içinden 1–2 tanesinin dönemin en çok kazandıranlarından çıkması.

## Aşama 5 — Haftalık rapor ve otomatik çalışma
Her cuma otomatik çalışacak (GitHub zamanlanmış görev). Raporun bölümleri:
1. **Piyasanın hali.**
2. **Öneriler (en fazla 10):** 3 ve 6 ay için ayrı uygunluk, haber yorumu, geçen haftaya göre değişim.
3. **Hisse kartı:** neden listede, geçmişte benzerleri ne yaptı, haberler, neden almamalı.
4. **Alınmaz listesi**, sebepleriyle.
5. **Yaklaşan önemli günler.**
6. **Karne:** eski listelerin gerçek sonucu. Listeler yayın günü kilitlenir.
7. **Otopsi:** son biten çeyreğin en çok kazandıranları; yakaladık mı, kaçırdık mı, neden.

Görünüm taslağı: Fırsat Radarı — Haftalık Tarama Taslağı (örnek verilerle, üç sayfa).

## Sıra ve süre
1. Otopsi: 1–2 oturum.
2. Benzerler ve alınmaz süzgeci: 1 oturum.
3. Sıralama ve geçmişe uygulama: 1 oturum.
4. Haftalık rapor sayfası ve otomatik çalışma: 1 oturum.
5. İlk gerçek cuma raporu ve ilk kilitli liste.

## Bilinen sınırlar
- Devralma ve tek günlük sıçramalar önceden görülemez; araç bunları yakalamayı vaat etmez.
- Büyüklük sınırı yüzünden %300–500'lük küçük şirket sıçramalarının çoğu evrenin dışında kalır.
- Haberin yorumlanması yarı otomatik olacak. Son karar kullanıcının.

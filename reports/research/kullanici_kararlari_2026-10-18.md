# Kullanıcı Kararları ve Notlar — 18 Ekim 2026

**Durum:** Not alındı; **henüz uygulanmadı**. Şu an çalışma ve plan aşamasındayız. Bu kararlar bir sonraki ön kayıt sürümüne (v1.3) gerekçeleriyle işlenip ondan sonra uygulanacak.

**Ana ilke:** Yalnızca güvenilir verilerle hareket edilecek.

## Veri kararları

| # | Veri | Karar | Not |
|---|---|---|---|
| 2 | Mali tablolar: hisse sayısı | **Açıkta bırakılmayacak, tamamlanacak.** | Kapak sayfası hisse sayısı SEC XBRL `companyfacts` API'sinden (`dei:EntityCommonStockSharesOutstanding`, kapak tarihiyle) ayrıca indirilecek; bölünme düzeltmesi bunun üzerine kurulacak (K1, K3). |
| 5 | Büyük fonların ne aldığı (13F) | Kullanıcı görüşü: anlık bilgi ancak haber ve sosyal medyadan (Twitter/X, Reddit, Instagram) gelir; bu verileri çekmek kolay değil. | Açıklama: 13F, fonların SEC'e verdiği resmî çeyreklik bildirimdir (45 gün gecikmeli). Aşağıdaki "önemli yatırımcıların işlemleri" maddesiyle birlikte değerlendirilecek. |
| 6 | Borsadan silinmiş şirketlerin fiyatları (seyrek FTD kayıtları) | **Silinecek.** | Riskli şirketler başka yöntemlerle elenecek. *Etkisi:* Borsadan çıkan ve Yahoo serisi olmayan hisseler evrenden ve getiri hesabından düşer. Bu, geçmiş getirileri olduğundan iyi gösterebilir (hayatta kalan yanılgısı). Raporlarda ayrıca belirtilecek. |
| 7 | Hisse bölünme kayıtları | **Düzeltilecek.** | Olay başına elle doğrulanmış düzeltme listesi (K2): ayrılma bölünme sayılmaz, çift kayıt bir kez sayılır, eksik bölünme eklenir. |
| 8 | Yıllık rapor metinleri (10-K) | **Silinecek.** | Metin belirtileri modelden çıkarılacak. |
| 9 | Haberler (GDELT) | **Şimdilik silinecek; ileride kullanılacak.** | Çok önemli ama çok zor. → `ACIK_LISTE.md`'ye ileride yeniden ele alınacak madde olarak eklendi. |
| 10 | Açığa satış (düşüşe bahse girenler) | Kullanıcı sorusu: "bahse girenleri nasıl buluyoruz?" | Yanıt aşağıda. Karar sonra verilecek. |
| 11 | Wikipedia, Reddit | **Çıkarılacak.** | — |

## Yeni veri ihtiyacı

**En büyük firmaların, uzmanların ve önemli yatırımcıların alım satım yaptığı hisselerin listesi bulunacak.** Olası kaynaklar (güvenilirlik sırasıyla):
1. **SEC 13F** (elimizde): 100 milyon $'dan büyük fonların çeyreklik portföyleri. Berkshire, Pershing Square, Appaloosa gibi "önemli isimler" ayrı ayrı izlenebilir. Resmî, ama 45 gün gecikmeli.
2. **SEC 13D/13G** (elimizde, dosyalama geçmişinde): bir şirketin %5'inden fazlasını alan yatırımcının 10 gün içinde verdiği bildirim. 13D aktivist yatırımcı demektir. Resmî ve hızlı.
3. **SEC Form 4** (elimizde): şirket yöneticilerinin ve %10'dan büyük ortakların kendi hisse işlemleri, 2 iş günü içinde. Resmî.
4. **ABD Kongre üyelerinin hisse işlemleri** (elimizde değil): yasa gereği 45 gün içinde açıklanıyor; ücretsiz kaynaklar var (House/Senate açıklama siteleri).
5. **Analist (uzman) kâr beklentileri ve tavsiye değişiklikleri** (elimizde değil): ücretli veri.

## Soru 10'un yanıtı: düşüşe bahse girenleri nasıl buluyoruz?

Bir hissenin düşeceğine bahse giren yatırımcı, o hisseyi ödünç alıp satar (açığa satış); fiyat düşünce ucuzdan geri alıp iade eder. Bunu iki resmî kaynaktan görürüz:
- **FINRA günlük açığa satış hacmi** (elimizde, 2010 →): her gün işlem gören hisselerin ne kadarının açığa satış olduğu. Günlük ama gürültülü: piyasa yapıcıların gün içi işlemleri de girer.
- **Borsaların bildirdiği açık pozisyon** (elimizde değil, FINRA'dan ücretsiz): ayda iki kez, o gün itibarıyla kapatılmamış toplam açığa satış miktarı. Daha anlamlıdır: "kaç gün içinde kapatmak zorundalar" gibi ölçüler buradan çıkar. Çok yüksek açık pozisyonlu hisseler hem düşüş riski hem de "sıkışma" ile hızlı yükseliş adayıdır.

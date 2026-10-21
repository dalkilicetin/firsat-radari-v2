# Piyasa Mekanizmaları Laboratuvarı — Rapor

> Bu rapor `arastirma/sonuclar/*.json` dosyalarından otomatik üretilir (`python calistir.py rapor`). **Simülasyon sonuçları piyasada yay olduğunu kanıtlamaz; ölçüm aletini dener.** Gerçek örnekler küçük ve hayatta kalan hisselerden oluşur. Yatırım tavsiyesi değildir.

## 1. Özet — ne öğrendik?

1. **Yay (endeks) tek başına işlem sinyali değil.** Yalnızca gerilim (Y1) koşulsuz günden *daha kötü*: 63 bar getiri koşulsuza göre -1.1%. Boşalma işareti beklenince (Y2) 1.0% (63 bar getiri 3.2%, GA [2.1%, 4.5%]); basit '−%15 düştüyse al' kuralı -0.1%. Yay mekanizmasının *var olduğu* simüle dünyada bile etki küçük.
2. **33 yıllık endeks tarihi yayı kanıtlamaya yetmez.** Simüle edilen yay tam olduğu gibi gerçek olsa bile, ~33 yılda ~10 bağımsız krizle Y2'yi yakalama olasılığı **13%** (yay yokken yanlış alarm 1%); güçlü yay varsayımıyla 31%. Endeks düzeyinde sonuç 'vaka çalışması' kalır.
3. **Panik / bozulma ayrımı bu özelliklerle zayıf.** Kural tabanlı ayrım %48 doğru ('hep bozulma de' tabanı %81); lojistik %85. Panik de kredi spread'ini açtığında (1998/2020 gibi) kural paniği bozulma sanıyor.
4. **Hisse düzeyi en umut verici alan.** Panik olaylarında en çok düşen hisseler, normal zamandaki ters dönüşün *ötesinde* 1.9% [0.9%, 2.8%] (126 bar) ekstra toparlıyor; bozulma olaylarında 0.2% [-0.5%, 1.0%] (≈0). Gerçek 2025 vakasında krize özgü fark aynı yönde (kalıntı sıralaması, 3/6/12 ay: 24.3% / 46.7% / 59.1%), ancak hisse listesi seçim yanlılığı taşıyor; 2022'de karma (3 ay -18.7%, 12 ay 35.7%).
5. **Kırılma noktası: yüksek AUC büyük ölçüde mekanik.** Olay olmayan dünyada bile AUC 0.71 / 0.75 (kalibre: 0.77 / 0.72). `dd` dışındaki öncüler yalnızca panik bitişinde gerçek bilgi taşıyor (AUC farkı +0.13). **Kenetlenme ve Gelgit bağımsız bilgi eklemiyor, stres vekili gibi davranıyor;** Gelgit gerçek veride hiç test edilemedi.

## 2. Tarih (13 SPX düşüşü, `katalog.md`)

- Hızlı düşüşler daha çabuk toparlanıyor gibi: ρ(hız, toparlanma) = 0.48 (p=0.10, n=13); derinlik sabitlenince bile pozitif, ama 'hız' düşüşün *süresini* içerdiğinden büyük ölçüde süre simetrisi.
- Simülatörün yayı bu ilişkiyi **üretmiyor** (derinlik sabit, ρ(hız, toparlanma) = -0.00; ρ(süre, toparlanma) = 0.02). Katalogdaki ilişki bu mekanizmayla açıklanmıyor; şans (n=13, çok sütun denendi) veya başka bir mekanizma.
- Kredi stresi tek başına panik/bozulma ayırt etmiyor (1998, 2020 yüksek kredi stresi ama hızlı toparlanma; 2000, 2007 yavaş). VIX zirvesi dipten önce gelen kriz: 10/13.
- Karşı örnekler (Nikkei 1989, Nasdaq 2000): çok yavaş düşüş, kredi/banka kaynaklı, destek yetersiz/geç → 'yay' değil.

## 3. Simülasyon (ölçüm aleti çalışıyor mu?)

- **Kalibrasyon:** 4 metrik yarılanma süresini belirlemiyor (ızgara noktaları ayırt edilemiyor); simülatör katalogdan daha hızlı toparlıyor → güç sonuçları iyimser.
- **S2:** Y2, Y1'e göre ek acıyı azaltıyor: MAE ortalaması -8.7% vs -10.2%; MAE < −%10 oranı 33% vs 41%.
- **S3 (negatif kontrol):** yay yok + bozulma var dünyasında Y2 koşulsuzun -3.1% altında (bıçağı tutmak); saf yürüyüşte -0.5%. Yay var dünyasında 1.0%. Aradaki ~4 puan 'yayın payı'. Rastgele sinyal yanlış alarm oranı: 9%.
- **S4 (güç):** bkz. özet 2. Bir dünya ≈33 yılda 15 Y2 olayı / 10 bağımsız bölüm veriyor; farkı ayırt etmek için ~477 olay gerekir.
- **S5:** hisse sıralamasında genel (krizden bağımsız) ters dönüş etkisi büyük; krize özgü pay küçük. Her zaman sakin-taban kontrolü gerekir.

## 4. Gerçek örnek (küçük, vaka çalışması)

- **R1:** 61 aylık veri aylık yay dedektörünü ısıtmaya yetmiyor (Y1=0, Y2=0); 2022 görünmez. Betimsel olarak gerilim skoru 2025-03/04'te en yüksek (0.80/0.82).
- **R2:** 2025: yay (en çok düşen ekstra toparladı); 2022: kısa vadede (3 ay) gizli güç (enerji hisseleri dirençli), 12 ayda yay. Sakin taban, 2023–26 AI rallisi rejiminde negatif (momentum) → krize özgü fark şişmiş olabilir.
- **R3:** şok yayı (5 gün): 2.2% [-0.1%, 6.5%], n=27 gün. v5.16'daki +%5'i ne doğruluyor ne çürütüyor. Panel fiyat kapsamı düzensiz: 105 sabit hisseyle sınırlı; 4–6 hafta sonra tekrarlanmalı.

## 4b. Koşul haritası (simülasyon): hangi koşulda hangi yaklaşım?

Hücreler: Yay = Y2 sonrası 63 bar getirinin *aynı koşuldaki her güne göre* farkı; Hisse yayı ⟷ Gizli güç = krize özgü D1 − D5 (126 bar, + = yay, − = gizli güç); Kırılma = panikten normale AUC.
Düşük terçil hücreleri küçük (n≈40–100); fark güven aralıkları geniş.

| Yaklaşım | Kenetlenme düşük | Kenetlenme yüksek | Likidite değişimi düşük (gevşek) | Likidite değişimi yüksek (sıkı) |
|---|---|---|---|---|
| Yay (Y2 farkı) | 1.5% (n=40) | 0.4% (n=409) | -0.4% (n=96) | 2.1% (n=309) |
| Hisse yayı ⟷ Gizli güç | -0.5% (n=31) | 1.1% (n=238) | 0.0% (n=47) | 1.2% (n=206) |
| Kırılma (panikten normale AUC) | 0.67 | 0.79 | 0.75 | 0.77 |

Okuma: Yüksek-stres hücrelerinde (yüksek kenetlenme / sıkı likidite) etkiler daha belirgin; ama Y2 olaylarının çoğu zaten orada olduğundan bu, koşulun bağımsız bilgi taşıdığını göstermiyor. Yay satırı için kontrol dünyalarında (gelgit etkisi kapalı / ortak faktör stresle artmıyor) aynı örüntü sürdü; diğer iki satır kontrol dünyalarında çalıştırılmadı.

## 5. Karar tablosu

🟢 simülasyonda ölçülebilir ve tutarlı · 🟡 belirsiz / yalnızca simülasyonda · ⚪ desteklenmiyor / ölçülemedi

| Hipotez | Karar | Gerekçe |
|---|---|---|
| Y1: aşırı gerilim sonrası toparlanma | ⚪ | Koşulsuz günden -1.1% kötü; yay yoksa da benzer (S3) |
| Y2: gerilim + boşalma işareti | 🟡 | Koşulsuza 1.0%, GA koşulsuzu kapsayabilir; ek acıyı azaltıyor; 33 yılda kanıtlanamaz (güç 13%) |
| Panik / bozulma ayrımı | ⚪ | Lojistik tabanı yalnızca +4 puan geçiyor; kural tabanın altında |
| Hisse yayı: panikte en çok düşen ekstra toparlanır | 🟢 sim / 🟡 gerçek | Sim: 1.9% [0.9%, 2.8%]; 2025 tutarlı ama seçim yanlılığı, 2022 karma |
| Gizli güç: bozulmada dayanıklı hisse ekstra kazanır | ⚪ | Sim: 0.2% [-0.5%, 1.0%]; gerçekte yalnızca 2022'de 3 ay (enerji) |
| Kırılma noktası: öncülerle rejim geçişi | ⚪ (genel) / 🟡 (panik bitişi) | Negatif kontrol AUC 0.71; panik bitişinde `dd` dışı öncü AUC 0.69 vs 0.55 |
| Kenetlenme koşulu | ⚪ | Y2 farkı -1.1% (GA 0'ı içeriyor); stres vekili |
| Gelgit koşulu | ⚪ | Sim: mekanizma açık/kapalı ayırt edilemiyor; gerçek veride test yok |
| Şok yayı (günlük −%8) | 🟡 | 5 günde 2.2% [-0.1%, 6.5%]; v5.16 ile uyumlu ama kanıt değil |
| Katalog: hızlı düşüş → hızlı toparlanma | ⚪ | n=13, süre simetrisi; sim mekanizması üretmiyor |

## 6. Sonraki adım önerisi

**Gerçek günlük veriye geçmeye değer mi? Kısmen evet — ama hedefi daralt.**

1. **Öncelik 1 — Hisse düzeyi Yay ⟷ Gizli güç (günlük, 30 yıl, S&P 500 üyeleri).** Her krizde yüzlerce hisse olduğu için güç, endeks testinden çok yüksek. Zorunlu kontroller: *krize özgü* fark (sakin taban çıkarılır), hayatta kalan yanlılığı (tarihsel endeks üyeliği), beta'dan arındırma, medyan bazlı dilimler.
2. **Öncelik 2 — Kenetlenme için günlük veri:** ortalama korelasyonun stres anındaki davranışı aylık veriyle görünmüyor. Gelgit için NFCI / Fed bilançosu (FRED).
3. **Endeks Yay'ı için tek bir piyasa yetmez:** çok piyasalı (ABD dışı endeksler, sektör ETF'leri) örneklem gerekir; yine de 'vaka çalışması' olarak sunulmalı.
4. **Kırılma noktası için etiketi yeniden tasarla:** kural rejimi fiyat ve oynaklıkla tanımlı olduğu için tahmin mekanik. Daha anlamlı hedef: panik/bozulma olayının bitişi veya kredi spread'inin normalleşmesi.
5. **Küçük düzeltmeler:** katalog değerlerini (özellikle `guven=orta` satırları) bir grafikte doğrula; R3'ü gece taramaları tam kapsama ulaşınca (≈4–6 hafta) yeniden çalıştır; simülatörün toparlanma hızını katalogla uyumlu hâle getir.

## 7. Bilinen sınırlar

- Simülatör, yayı biz koyduğumuz için 'bulundu' sonuçları bir kanıt değil, aletin duyarlılığıdır. Simdeki 'bozulma' etiketi rastgele geri dönmeyen düşüşleri de içerir.
- Kalibrasyon 4 metrik ve 13 satırlık katalogla yapıldı; yarılanma süresi belirlenmiyor.
- Gerçek örnek: 154 küratörlü hisse + 26 ETF, 2021-10→2026-10, tek rejim (yarı iletken/AI rallisi). Hayatta kalan ve izleme listesi yanlılığı var.
- Gelgit gerçek veride sınanamadı; Kenetlenme yalnızca aylık betimsel.
- Eşikler `hipotezler/*.yaml` dosyalarında önceden kayıtlı; kalibrasyon ızgarası dışında eşik oynanmadı (`deneme_gunlugu.csv`).

## 8. Opus incelemesinde özellikle bakılacak noktalar

1. **Etiket tanımı (S1/S5):** 'gerçek tür' düşüşün çoğunun `m`'den mi `F`'den mi geldiğine göre; sıradan rastgele düşüşler 'bozulma' sayılıyor. Olay bazlı etiket (S5) ikinci kontrol olarak var ama S1'de yok.
2. **Kalibrasyon seçim kuralı:** yarılanma belirlenemediği için 'en iyiye %10 yakın olanlar arasında varsayılana en yakın' kuralı sonuca bakmadan sabitlendi; ama kuralın kendisi bir serbestlik derecesi.
3. **S5/R2 'sakin taban':** simde ve gerçekte tabanın nasıl tanımlandığı (aynı pencere uzunluğu, dd > −%3 ayları) sonucu belirliyor. R2'de taban 30 ardışık aydan, tek rejimden geliyor.
4. **Kırılma:** negatif kontrol başarısızlığı hedef tanımının mekanik olduğunu gösterdi; etiket yeniden tasarlanmadan gerçek veriye taşınmamalı.
5. **R2 medyan/ortalama değişikliği:** ilk sürümde ortalama kullanıldı, aşırı sonuç (D1−D5 %265) çıkınca medyana geçildi; bu bir metodolojik karar, `deneme_gunlugu.csv`'ye değil bu rapora not düşüldü.
6. **R3 veri kuralı:** kapsama ≥570 kuralı çok katı çıktı (75 günden 70'ini atıyordu); sabit hisse seti kuralına (≥%95 gün) geçildi. İkisi de sonuçlara bakmadan değil, boş çıktıya bakarak seçildi.
7. **Katalog değerleri hafızadan yazıldı;** özellikle `guven=orta` satırlar doğrulanmadı.

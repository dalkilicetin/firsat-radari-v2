# S1 — Panik mi, bozulma mı? Ayırt edilebilirlik

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Her Y1 olayında **gerçek tür** simülatörden bilinir (düşüşün çoğu `m`'den mi, `F`'den mi). Dedektör bunu göremez; kural (`kredi60 > 0.5` veya Sahm) ve lojistik regresyon (tohum 0–9 eğitim, 10–19 test) karşılaştırılır.
**Etiket notu:** 'bozulma' = düşüşün çoğu geri dönmeyen kısımdan (`F`) geliyor. Sıradan rastgele yürüyüş düşüşleri de `F`'ye yazıldığı için bu sınıfa girer; bu yüzden Y1 olaylarının çoğu 'bozulma' etiketli çıkar. Yani 'bozulma' = *geri dönmeyecek düşüş*, ekonomik kriz anlamına gelmez.
`panik_kredi`: panik anında kredi spread'inin ne kadar açıldığı (0 = hiç; 1998/2020'de gerçekte açılmıştı).

| panik_kredi | n (test) | panik oranı | kural doğruluğu | lojistik doğruluğu | hep-çoğunluk | panik yakalama: kural | panik yakalama: lojistik | kural: panik→bozulma hatası |
|---|---|---|---|---|---|---|---|---|
| 0.0 | 285 | 19% | 49% | 85% | 81% | 100% | 49% | 0% |
| 2.0 | 285 | 19% | 48% | 85% | 81% | 89% | 47% | 11% |
| 4.0 | 285 | 19% | 46% | 85% | 81% | 68% | 55% | 32% |
| 8.0 | 285 | 19% | 43% | 88% | 81% | 43% | 66% | 57% |

## Lojistik katsayıları (standartlaştırılmış; + = bozulma lehine)

| panik_kredi | sabit | hiz | vix_z | kredi60 | genislik | sahm | dd |
|---|---|---|---|---|---|---|---|
| 0.0 | 1.64 | 0.83 | -0.61 | 1.13 | -0.09 | 0.12 | -0.26 |
| 2.0 | 1.41 | 0.73 | -0.62 | 0.07 | -0.01 | 0.48 | -0.20 |
| 4.0 | 1.48 | 0.73 | -0.56 | -0.56 | 0.00 | 0.67 | -0.50 |
| 8.0 | 1.78 | 0.88 | -0.42 | -1.43 | 0.01 | 0.77 | -1.17 |

## Karışıklık matrisleri (satır = gerçek, sütun = tahmin)

- panik_kredi=0.0: kural {'panik': {'panik': 53, 'bozulma': 0}, 'bozulma': {'panik': 145, 'bozulma': 87}}; lojistik {'panik': {'panik': 26, 'bozulma': 27}, 'bozulma': {'panik': 17, 'bozulma': 215}}
- panik_kredi=2.0: kural {'panik': {'panik': 47, 'bozulma': 6}, 'bozulma': {'panik': 143, 'bozulma': 89}}; lojistik {'panik': {'panik': 25, 'bozulma': 28}, 'bozulma': {'panik': 15, 'bozulma': 217}}
- panik_kredi=4.0: kural {'panik': {'panik': 36, 'bozulma': 17}, 'bozulma': {'panik': 136, 'bozulma': 96}}; lojistik {'panik': {'panik': 29, 'bozulma': 24}, 'bozulma': {'panik': 18, 'bozulma': 214}}
- panik_kredi=8.0: kural {'panik': {'panik': 23, 'bozulma': 30}, 'bozulma': {'panik': 132, 'bozulma': 100}}; lojistik {'panik': {'panik': 35, 'bozulma': 18}, 'bozulma': {'panik': 15, 'bozulma': 217}}

## Okuma
- **Kural** doğruluğu (48%) 'hep çoğunluk' tabanının (81%) altında: bozulmaların çoğunu ilk aşamada 'panik' sanıyor (kredi/Sahm gecikmeli).
- **Lojistik** tabanı yalnızca +4 puan aşıyor; paniklerin 47%'ını yakalıyor. Tür ayrımı bu özelliklerle **zayıf**.
- `panik_kredi` arttıkça kural paniği bozulma sanıyor (son sütun) ve `kredi60` katsayısı işaret değiştiriyor: kredi spread'i ancak panik kredi açmıyorsa ayırt edici (katalogdaki 1998/2020 paniklerinde açmıştı).
- Sonuç: panik/bozulma ayrımına **güvenerek** karar verilmemeli; asıl ölçüm tür tahmini değil, sinyal sonrası getiri ve ek düşüş (S2). Bu simülasyon-içi bir sınırdır.

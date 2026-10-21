# Simülatör kalibrasyonu

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Katalog (13 SPX düşüşü, ~38 yıl) ile simüle edilen ≥%10 düşüş bölümlerinin dağılımı karşılaştırıldı. Her ızgara noktası 8 dünya × 60 yıl. Mesafe: 4 metriğin çeyreklik/medyanlarında göreli fark + yıllık sıklık farkı (düşük = iyi).

> Dikkat: katalog **seçilmiş** önemli düşüşlerdir, ≥%10'luk bütün düşüşler değil; sıklık karşılaştırması zayıftır. Izgaraya katalogda olmayan `lam_B` (bozulma sıklığı) eklendi çünkü varsayılanlarla düşüşler katalogdan çok derin çıkıyordu.

| Sıra | yarılanma | lam_P | sB üst | lam_B | mesafe | yıllık sıklık |
|---|---|---|---|---|---|---|
| 1 | 30 | 0.333 | 0.45 | 0.083 | 2.99 | 0.46 |
| 2 | 60 | 0.200 | 0.45 | 0.083 | 3.10 | 0.47 |
| 3 | 60 | 0.200 | 0.35 | 0.083 | 3.12 | 0.49 |
| 4 | 120 | 0.200 | 0.45 | 0.083 | 3.14 | 0.47 |
| 5 | 30 | 0.200 | 0.45 | 0.083 | 3.18 | 0.48 |
| 6 | 120 | 0.333 | 0.45 | 0.083 | 3.23 | 0.45 |
| 7 | 60 | 0.125 | 0.45 | 0.083 | 3.26 | 0.48 |
| 8 | 120 | 0.125 | 0.45 | 0.083 | 3.28 | 0.48 |

Hedef sıklık (katalog): 0.34/yıl.

## En iyi ayar ile katalog (çeyreklik 25 / medyan / 75)

| Metrik | Katalog | Simülasyon |
|---|---|---|
| dusus | -34% / -20% / -19% | -30% / -19% / -14% |
| gun_dibe | 50.0 / 67.0 / 190.0 | 40.8 / 78.5 / 199.0 |
| gun_top | 86.0 / 104.0 / 332.0 | 46.2 / 92.5 / 204.2 |
| sertlik | 1.3 / 1.7 / 1.9 | 0.6 / 1.1 / 1.9 |

**Seçim kuralı (sonuçlara bakmadan sabitlendi):** en iyi mesafenin %10'u içindeki 11 ayardan, varsayılana (yarılanma 60, lam_P 0.2) en yakını: yarılanma=60, lam_P=0.200, sB üst=0.45, lam_B=0.083.

## Bu kalibrasyonun sınırları
- Izgara noktaları arasındaki fark küçük: bu 4 metrik **yarılanma süresini belirlemiyor**. Yay gücü simülasyon sonuçlarında bir *varsayım*; S4'te `yarılanma` bir duyarlılık ekseni olarak değiştirilir.
- Simülatör, katalogdan **daha hızlı toparlanıyor** (medyan sertlik ~1.0, katalogda ~1.7). Yani simdeki yay muhtemelen gerçek piyasadakinden güçlü. S4 'bulunma olasılığı' sonuçları **iyimser** okunmalı.
- Katalog 13 satır; dağılımların kendisi de belirsiz.

Seçilen ayar `sonuclar/sim_ayar.yaml` dosyasına yazıldı; sonraki deneyler bunu kullanır.

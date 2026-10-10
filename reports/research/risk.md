# Risk puanı doğrulaması

Dönem: 2015 → 2025-07-01 öncesi (sonuç penceresi son döneme taşan haftalar hariç). Evren: o hafta Nasdaq'ta işlem gören tüm hisseler, sonradan çıkanlar dahil.
Kötü çıkış: sonraki 1 yıl içinde iflasla ya da %50'den fazla kayıpla borsadan çıkış.

|   Risk |   Gözlem (hisse-hafta) | Medyan en büyük düşüş (1 yıl)   | %50+ düşüş olasılığı   | Kötü çıkış olasılığı   | Medyan 1 yıllık getiri   |
|-------:|-----------------------:|:--------------------------------|:-----------------------|:-----------------------|:-------------------------|
|      1 |                382,300 | %-10                            | %5                     | %0.04                  | %5.8                     |
|      2 |                319,118 | %-19                            | %16                    | %0.18                  | %0.2                     |
|      3 |                255,133 | %-32                            | %31                    | %0.45                  | %-12.0                   |
|      4 |                191,399 | %-40                            | %40                    | %1.77                  | %-21.7                   |
|      5 |                127,829 | %-56                            | %55                    | %7.05                  | %-42.6                   |

- Bileşik puanın sonraki 1 yıldaki düşüşle sıralama korelasyonu: **+0.421**
- Kötü çıkışı ayırt etme gücü (AUC): bileşik **0.885**, yalnızca oynaklık 0.806

## Bileşenler

| Bileşen             |   Düşüşle sıralama korelasyonu | Kapsam   | Durum                          |
|:--------------------|-------------------------------:|:---------|:-------------------------------|
| oynaklik            |                          0.432 | %98      | ağırlık 0.25                   |
| dusus               |                          0.359 | %98      | ağırlık 0.20                   |
| dusuk_fiyat         |                          0.109 | %100     | ağırlık 0.10                   |
| likidite            |                          0.167 | %71      | ağırlık 0.10                   |
| yeni                |                          0.083 | %100     | ağırlık 0.05                   |
| nakit_suresi        |                          0.341 | %80      | ağırlık 0.20                   |
| sulandirma          |                          0.188 | %69      | ağırlık 0.10                   |
| delist_uyarisi      |                          0.148 | %100     | olay puanı 0.25                |
| denetci_degisikligi |                          0.069 | %100     | olay puanı 0.10                |
| geciken_rapor       |                          0.104 | %100     | olay puanı 0.20                |
| devamlilik_suphesi  |                          0.198 | %100     | olay puanı 0.25                |
| borc                |                         -0.099 | %80      | çıkarıldı: ters yön (IC −0,10) |
| icerden_satis       |                         -0.07  | %100     | çıkarıldı: ters yön (IC −0,07) |

Ağırlıklar uzman görüşüdür; 4. aşamada bu sonuçlarla kalibre edilecek.

# S4 — Güç analizi: ~33 yıllık tarihle yayı görebilir miyiz?

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Her satır: 120 ayrı 33 yıllık dünya (gerçek tarihin uzunluğu). Sinyal: **Y2**. 'Bulundu' = Y2 olaylarının 63 bar getirisinin %90 GA alt sınırı koşulsuz ortalamanın **üstünde**. 'Olay' = ayıklanmış tüm olaylar; 'bölüm' = aynı krizdeki tekrarlar tek sayılır (gerçek tarih bu kadar bağımsız kriz verir).
Son satır **yay olmayan** dünya: orada 'bulundu' oranı yanlış alarm oranıdır (tek yönlü ≈ %5 beklenir).

| Dünya | olay/dünya | bölüm/dünya | Y2 − koşulsuz | bulundu (olay) | bulundu (bölüm) | gereken olay sayısı* |
|---|---|---|---|---|---|---|
| yarılanma 30g, panik 0.6/5yıl | 15 | 9 | 0.3% | 12% | 11% | ~6298 |
| yarılanma 30g, panik 1.0/5yıl | 15 | 9 | 1.4% | 15% | 21% | ~292 |
| yarılanma 30g, panik 1.7/5yıl | 16 | 10 | 3.3% | 25% | 31% | ~63 |
| yarılanma 60g, panik 0.6/5yıl | 15 | 9 | 0.3% | 8% | 10% | ~4606 |
| yarılanma 60g, panik 1.0/5yıl | 15 | 10 | 1.1% | 13% | 13% | ~477 |
| yarılanma 60g, panik 1.7/5yıl | 16 | 10 | 2.8% | 20% | 23% | ~98 |
| yarılanma 120g, panik 0.6/5yıl | 15 | 9 | -0.4% | 9% | 9% | yetersiz fark |
| yarılanma 120g, panik 1.0/5yıl | 15 | 9 | 0.3% | 12% | 12% | ~9878 |
| yarılanma 120g, panik 1.7/5yıl | 16 | 10 | 1.8% | 20% | 15% | ~248 |
| YAY YOK (bozulma var) | 14 | 8 | -2.2% | 1% | 1% | yetersiz fark |

\* Gereken olay sayısı: ortalama farkı %90 GA ile ayırt etmek için `(1.645·sd/fark)²` (olaylar bağımsız varsayımıyla; olay getirileri çakıştığı için gerçekte daha çok gerekir).

## Okuma
- 'Bölüm' sütunu, gerçek tarihin verebileceği bağımsız kriz sayısına karşılık gelir. Burada 'bulundu' oranı yanlış alarm satırına yakınsa, **33 yıllık tarihten bu mekanizma kanıtlanamaz** (var olsa bile).
- 'Olay' sütunu çakışan/aynı kriz içi olayları ayrı sayar; iyimser bir üst sınırdır.
- Simülatör katalogdan hızlı toparlandığı için (bkz. kalibrasyon) buradaki oranlar iyimser okunmalı.
- Çıkarım: daha fazla bağımsız kriz gerekir → birden çok piyasa (ABD dışı endeksler, sektör ETF'leri) ve hisse düzeyi test (Gizli güç) önem kazanır.

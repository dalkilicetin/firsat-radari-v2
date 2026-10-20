# Test düzeneği doğrulaması

## 1. Sızıntı testi (girdiler o tarihte kesilerek)

| Tarih | Karşılaştırılan değer | Farklı |
|---|---|---|
| 2014-09-05 | 288,785 | 41 ['gelir_buyume', 'gelir_ivme', 'net_kar', 'net_kar_once', 'devamlilik'] |
| 2018-03-02 | 288,785 | 97 ['net_kar', 'net_kar_once', 'devamlilik', 'ucuzluk_tuzagi', 'kesin_ret'] |
| 2021-11-05 | 288,785 | 14 ['net_kar', 'net_kar_once', 'devamlilik'] |
| 2025-05-02 | 288,785 | 6 ['net_kar', 'net_kar_once'] |

Sonuç: KALDI — yukarıdaki işaretler incelenmeli.

## 2. Hayatta kalma yanlılığı

| Yıl | Haftalık evren (ort.) | Sonradan borsadan çıkan | İşlem tutarı FINRA'dan |
|---|---|---|---|
| 2013 | 1324 | 536 | 520 |
| 2014 | 1480 | 588 | 574 |
| 2015 | 1527 | 580 | 567 |
| 2016 | 1458 | 491 | 477 |
| 2017 | 1503 | 457 | 443 |
| 2018 | 1640 | 446 | 433 |
| 2019 | 1620 | 366 | 356 |
| 2020 | 1658 | 323 | 312 |
| 2021 | 1979 | 362 | 349 |
| 2022 | 1892 | 292 | 283 |
| 2023 | 1803 | 211 | 204 |
| 2024 | 1833 | 149 | 146 |
| 2025 | 1916 | 95 | 92 |
| 2026 | 2054 | 33 | 31 |

İflas eden ve evrende bulunmuş hisse: 135; bunların 3 aylık getirisi −%100 olan hisse-hafta: 7.

## 3. Bilinen değerler

| Kontrol | Beklenen | Bulunan | Durum |
|---|---|---|---|
| AAPL piyasa değeri 2024-06-06 | 2,9–3,05 tn $ | 2.98 tn $ | tamam |
| JNJ piyasa değeri 2024-06-06 | 350–365 Mr $ | 352 Mr $ | tamam |
| SPY 3 ay 2019-01-04 | +0.1484 | +0.1484 | tamam |

## 4. Masraf

Net getiri bağımsız formülle aynı: evet; evrende ortalama tek yön masraf: %0.15.

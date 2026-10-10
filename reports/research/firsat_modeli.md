# Fırsat modeli ve güvenlik modeli — faaliyet şirketleri (geliştirme dönemi)

Ön kayıt: [firsat_on_kayit.md](firsat_on_kayit.md). Evren: finans dışı faaliyet şirketleri (finans ve SPAC hariç). Ölçüm: yatırılabilir faaliyet şirketleri, tahmin tarihi + vade < 2025-07-01. Son dönem kullanılmadı.

## Sonuç: ön kayıtlı ölçüt SAĞLANMADI ❌

1. İlk %10'da büyük kazanan oranı genelin ≥ 1,5 katı ve GA alt sınırı > 1: **evet** (1.72 kat, GA 1.50–2.08)
2. Basit kıyastan (en yüksek oynaklık) yüksek: **evet** (%9.9 ↔ %9.4)
3. İlk %10 portföyü (maliyet sonrası) eşit ağırlıklı evrenden düşük değil: **hayır** (%-7.8 ↔ %4.3 yıllık)

## 1 yılda +%100 kazananlar (yatırılabilir faaliyet şirketleri)

| puan                            | ilk %10'da kazanan oranı   | genel oran   |   kat | %90 GA      |
|:--------------------------------|:---------------------------|:-------------|------:|:------------|
| Fırsat modeli                   | %9.9                       | %5.7         |  1.72 | 1.50 – 2.08 |
| Basit kıyas: en yüksek oynaklık | %9.4                       | %5.4         |  1.73 | 1.55 – 1.95 |
| Momentum 12-1                   | %8.9                       | %5.6         |  1.58 | 1.33 – 1.99 |
| Güvenlik modeli (1y)            | %5.7                       | %5.7         |  1    | 0.80 – 1.12 |

Tüm faaliyet şirketlerinde (likit olmayanlar dahil) fırsat modeli: %15.6 ↔ genel %8.4 (1.87 kat, GA 1.75–2.05).

Yıl yıl (kat, fırsat modeli):

|   2016 |   2017 |   2018 |   2019 |   2020 |   2021 |   2022 |   2023 |   2024 |
|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
|   1.25 |   2.02 |   2.06 |   1.76 |   1.32 |   1.06 |   2.26 |   2.14 |   2.36 |

## İkincil: 6 ayda +%50

| puan                  | ilk %10'da +%50 oranı   | genel oran   |   kat | %90 GA      |
|:----------------------|:------------------------|:-------------|------:|:------------|
| Fırsat modeli (6a)    | %14.6                   | %9.1         |  1.61 | 1.38 – 1.92 |
| Basit kıyas: oynaklık | %12.9                   | %8.7         |  1.49 | 1.32 – 1.72 |

## İlk %10'un 1 yıllık sonuç dağılımı

Büyük kazananları yakalamak büyük kayıplarla birlikte gelebilir; bu yüzden %50+ kayıp payı da gösteriliyor.

|                       | ilk %10'da −%50 ve altı   | genelde −%50 ve altı   | ilk %10 medyan 1y getiri   | genel medyan 1y getiri   |
|:----------------------|:--------------------------|:-----------------------|:---------------------------|:-------------------------|
| Fırsat modeli         | %31.5                     | %15.7                  | %-23.9                     | %-2.5                    |
| Güvenlik modeli       | %8.8                      | %15.7                  | %2.9                       | %-2.5                    |
| Basit kıyas: oynaklık | %33.8                     | %13.9                  | %-27.5                     | %-0.1                    |

## Portföy simülasyonu (maliyet sonrası, 4 haftada bir dengeleme)

Kıyas: yatırılabilir faaliyet şirketlerinin eşit ağırlıklı portföyü (maliyetsiz). Kıyas Sharpe 0.30, en büyük düşüş %-51.6. GA: 52 haftalık bloklarla bootstrap.

| portföy                       | yıllık getiri   | kıyas   | yıllık fazla (ort.)   | %90 GA         |   Sharpe |   Sortino | en büyük düşüş   | yıllık maliyet   | devir/dönem   |
|:------------------------------|:----------------|:--------|:----------------------|:---------------|---------:|----------:|:-----------------|:-----------------|:--------------|
| Fırsat — ilk %10              | %-7.8           | %4.3    | %-8.4                 | %-18.9 – %1.5  |    -0.01 |     -0.02 | %-83.2           | %6.5             | %38.0         |
| Fırsat — ilk 20               | %-21.8          | %4.3    | %-23.2                | %-42.0 – %-8.9 |    -0.36 |     -0.57 | %-93.3           | %10.2            | %54.4         |
| Güvenlik — ilk %10            | %10.7           | %6.0    | %4.0                  | %-0.1 – %10.1  |     0.55 |      0.66 | %-38.9           | %4.2             | %36.6         |
| Güvenlik — ilk 20             | %17.0           | %6.0    | %10.5                 | %0.9 – %18.5   |     0.71 |      0.96 | %-41.6           | %5.3             | %49.0         |
| Basit kıyas: oynaklık ilk %10 | %-17.0          | %3.4    | %-17.5                | %-26.8 – %-8.1 |    -0.28 |     -0.44 | %-92.3           | %5.0             | %31.2         |

Yıl yıl fazla getiri (portföy − kıyas):

|   tarih | Fırsat — ilk %10   | Fırsat — ilk 20   | Güvenlik — ilk %10   | Güvenlik — ilk 20   | Basit kıyas: oynaklık ilk %10   |
|--------:|:-------------------|:------------------|:---------------------|:--------------------|:--------------------------------|
|    2015 | —                  | —                 | —                    | —                   | %-10.5                          |
|    2016 | %-2.0              | %-7.1             | %-2.9                | %8.2                | %-27.4                          |
|    2017 | %6.4               | %22.3             | %-3.8                | %-11.9              | %-8.1                           |
|    2018 | %-22.1             | %-33.5            | %0.4                 | %-3.2               | %-21.0                          |
|    2019 | %-9.0              | %-39.4            | %-5.4                | %-10.1              | %-10.7                          |
|    2020 | %32.0              | %36.9             | %-7.8                | %3.2                | %36.3                           |
|    2021 | %-23.5             | %-24.9            | %13.8                | %25.6               | %-32.9                          |
|    2022 | %0.7               | %-21.3            | %11.0                | %12.3               | %-21.9                          |
|    2023 | %-18.6             | %-37.4            | %13.0                | %23.5               | %-34.0                          |
|    2024 | %-26.0             | %-47.8            | %16.5                | %35.7               | %-25.1                          |
|    2025 | %-3.2              | %-11.0            | %-0.9                | %11.3               | %-4.4                           |

## Puan dilimi kalibrasyonu

Güvenlik puanı (3 ay): her dilimin gerçekleşen ortalama fazla getirisi (aynı evrenin medyanına göre, kırpılmış), %90 GA ve medyanı geçme oranı.

| dilim   | ort_fazla   | isabet   |   hafta | ga            |
|:--------|:------------|:---------|--------:|:--------------|
| 0–10    | %-2.4       | %41.8    |     471 | %-4.2 – %-0.2 |
| 10–20   | %0.1        | %45.8    |     471 | %-1.3 – %1.5  |
| 20–30   | %1.0        | %48.5    |     471 | %-0.2 – %2.3  |
| 30–40   | %1.1        | %49.3    |     471 | %0.4 – %2.0   |
| 40–50   | %1.2        | %50.4    |     471 | %0.6 – %1.9   |
| 50–60   | %1.7        | %51.3    |     471 | %1.4 – %2.1   |
| 60–70   | %2.1        | %52.1    |     471 | %1.8 – %2.6   |
| 70–80   | %2.4        | %52.8    |     471 | %2.0 – %3.0   |
| 80–90   | %2.9        | %53.4    |     471 | %2.3 – %3.8   |
| 90–100  | %3.4        | %54.4    |     471 | %2.6 – %4.4   |

Fırsat puanı (1 yıl):

| dilim   | ort_fazla   | isabet   |   hafta | ga            |
|:--------|:------------|:---------|--------:|:--------------|
| 0–10    | %12.6       | %65.5    |     393 | %9.0 – %16.2  |
| 10–20   | %11.1       | %60.0    |     393 | %8.4 – %14.2  |
| 20–30   | %10.1       | %56.3    |     393 | %8.2 – %12.1  |
| 30–40   | %8.1        | %52.8    |     393 | %6.7 – %9.6   |
| 40–50   | %7.2        | %50.4    |     393 | %4.4 – %10.0  |
| 50–60   | %6.2        | %47.8    |     393 | %2.2 – %10.1  |
| 60–70   | %4.8        | %44.7    |     393 | %-0.5 – %10.9 |
| 70–80   | %3.4        | %42.9    |     393 | %-1.9 – %10.0 |
| 80–90   | %3.4        | %41.7    |     393 | %-2.4 – %10.8 |
| 90–100  | %0.2        | %37.7    |     393 | %-5.6 – %6.9  |

## Bilinen kazananlar: o tarihteki puanlar

| hisse   | tarih      |   fırsat puanı |   güvenlik puanı (1y) | sonraki 1 yıl   |
|:--------|:-----------|---------------:|----------------------:|:----------------|
| APP     | 2022-12-30 |             50 |                    74 | %278.4          |
| APP     | 2023-06-30 |             34 |                    56 | %223.4          |
| APP     | 2023-12-29 |             16 |                    63 | %741.1          |
| APP     | 2024-06-28 |             21 |                    88 | %301.1          |
| NVDA    | 2022-12-30 |             10 |                    84 | %239.0          |
| NVDA    | 2023-06-30 |             13 |                    96 | %192.1          |
| NVDA    | 2023-12-29 |              9 |                    96 | %176.7          |
| NVDA    | 2024-06-28 |             11 |                    93 | %27.7           |
| SMCI    | 2022-12-30 |             23 |                    88 | %246.2          |
| SMCI    | 2023-06-30 |             23 |                    86 | %228.7          |
| SMCI    | 2023-12-29 |             16 |                    98 | %12.5           |
| SMCI    | 2024-06-28 |             31 |                    95 | %-41.9          |
| RKLB    | 2022-12-30 |             63 |                    11 | %46.7           |
| RKLB    | 2023-06-30 |             30 |                    52 | %-20.0          |
| RKLB    | 2023-12-29 |             34 |                    56 | %392.2          |
| RKLB    | 2024-06-28 |             45 |                    37 | %637.1          |
| AXON    | 2022-12-30 |              7 |                    26 | %55.7           |
| AXON    | 2023-06-30 |             14 |                    60 | %50.8           |
| AXON    | 2023-12-29 |              7 |                    61 | %136.5          |
| AXON    | 2024-06-28 |              7 |                    45 | %178.2          |
| CELH    | 2022-12-30 |             20 |                    31 | %57.2           |
| CELH    | 2023-06-30 |             34 |                    63 | %14.8           |
| CELH    | 2023-12-29 |             28 |                    64 | %-51.5          |
| CELH    | 2024-06-28 |             22 |                    55 | %-19.6          |
| TSLA    | 2022-12-30 |             24 |                    45 | %101.7          |
| TSLA    | 2023-06-30 |             21 |                    54 | %-24.4          |
| TSLA    | 2023-12-29 |              9 |                    74 | %73.7           |
| TSLA    | 2024-06-28 |             12 |                    50 | %63.5           |
| DUOL    | 2022-12-30 |             35 |                    26 | %218.9          |
| DUOL    | 2023-06-30 |             32 |                    53 | %46.0           |
| DUOL    | 2023-12-29 |             32 |                    66 | %46.9           |
| DUOL    | 2024-06-28 |             28 |                    74 | %97.1           |
| CRWD    | 2022-12-30 |             42 |                    47 | %142.5          |
| CRWD    | 2023-06-30 |             30 |                    55 | %160.9          |
| CRWD    | 2023-12-29 |             10 |                    78 | %39.0           |
| CRWD    | 2024-06-28 |             15 |                    80 | %30.3           |
| AXTI    | 2022-12-30 |             53 |                    89 | %-45.2          |
| AXTI    | 2023-06-30 |             52 |                    75 | %-1.7           |
| AXTI    | 2023-12-29 |             60 |                    74 | %-5.0           |
| AXTI    | 2024-06-28 |             90 |                    81 | %-39.9          |
| ASTS    | 2022-12-30 |             68 |                    22 | %25.1           |
| ASTS    | 2023-06-30 |             58 |                    23 | %147.0          |
| ASTS    | 2023-12-29 |             39 |                    28 | %280.1          |
| ASTS    | 2024-06-28 |             24 |                    18 | %325.2          |

## Fırsat modelinin son ağırlıkları (en büyük 20)

|                                            |   ağırlık | yol    |
|:-------------------------------------------|----------:|:-------|
| dusuk_oynaklik                             |   -0.0755 | piyasa |
| kucuk_boyut                                |    0.074  | piyasa |
| kazanc_getirisi                            |   -0.0531 | yol1   |
| geri_alim_getirisi                         |    0.0213 | yol3   |
| tema_ruzgari                               |   -0.0211 | yol4   |
| icerden_alici_sayisi_90g                   |   -0.0185 | yol3   |
| wiki_ani_ilgi                              |    0.0182 | yol2   |
| 8k_2.03_yeni borç yükümlülüğü              |    0.0141 | yol3   |
| haber_ton_seviyesi                         |   -0.0139 | yol2   |
| icerden_alim_kumesi_3plus                  |    0.0133 | yol3   |
| devamlilik_suphesi                         |   -0.013  | yol1   |
| icerden_alim_tutar_piyasa_degeri           |    0.0126 | yol3   |
| 8k_1.01_önemli anlaşma                     |   -0.0124 | yol3   |
| 8k_3.02_kayıtsız hisse satışı (sulandırma) |   -0.0118 | yol3   |
| arge_yogunlugu                             |    0.0115 | yol1   |
| haber_ivmesi                               |    0.011  | yol2   |
| momentum_12_1                              |   -0.0102 | piyasa |
| gelir_buyumesi                             |    0.009  | yol1   |
| tema_ruzgari_v1_uzun                       |    0.0087 | yol4   |
| 8k_8.01_diğer olaylar                      |   -0.0081 | yol3   |

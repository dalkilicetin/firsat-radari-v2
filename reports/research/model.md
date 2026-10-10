# 4. aşama: kayan pencere modeli

Dönem: 2016 → 2025-07-01 öncesi; son dönem kullanılmadı. Her hafta yalnızca o ana kadar gerçekleşmiş getirilerle eğitilen modelin tahmini değerlendirilir (örneklem dışı). Değerler IC (puan ile gerçekleşen fazla getirinin sıralama korelasyonu).

## Örneklem dışı IC — tüm evrende eğitilen modeller, tüm evrende ölçüm

| model   |     1h |     1a |     3a |     6a |      1y |
|:--------|-------:|-------:|-------:|-------:|--------:|
| piyasa  | 0.085  | 0.1197 | 0.1729 | 0.2039 |  0.2204 |
| toplam  | 0.0876 | 0.1234 | 0.1758 | 0.2066 |  0.2237 |
| yol1    | 0.0561 | 0.0855 | 0.1208 | 0.1412 |  0.1564 |
| yol2    | 0.0078 | 0.0118 | 0.0167 | 0.0184 |  0.0128 |
| yol3    | 0.0191 | 0.0298 | 0.0424 | 0.0505 |  0.0538 |
| yol4    | 0.0049 | 0.0073 | 0.0082 | 0.0091 | -0.0078 |

## Örneklem dışı IC — yatırılabilir evrende ölçüm

Tüm evrende eğitilen:

| model   |     1h |     1a |     3a |     6a |      1y |
|:--------|-------:|-------:|-------:|-------:|--------:|
| piyasa  | 0.0508 | 0.0722 | 0.1145 | 0.1414 |  0.1512 |
| toplam  | 0.0523 | 0.0741 | 0.1139 | 0.1386 |  0.1449 |
| yol1    | 0.0328 | 0.0503 | 0.0765 | 0.0975 |  0.1092 |
| yol2    | 0.0082 | 0.0103 | 0.0147 | 0.0154 |  0.0082 |
| yol3    | 0.0081 | 0.0143 | 0.0285 | 0.0421 |  0.044  |
| yol4    | 0.0017 | 0.0048 | 0.0057 | 0.0065 | -0.0134 |

Yatırılabilir evrende eğitilen:

| model   |      1h |      1a |      3a |     6a |      1y |
|:--------|--------:|--------:|--------:|-------:|--------:|
| piyasa  |  0.0471 |  0.0669 |  0.1088 | 0.1352 |  0.1432 |
| toplam  |  0.0482 |  0.0675 |  0.1051 | 0.1278 |  0.1175 |
| yol1    |  0.0306 |  0.0475 |  0.0718 | 0.0928 |  0.0901 |
| yol2    |  0.0077 |  0.0081 |  0.0108 | 0.0071 |  0.0123 |
| yol3    |  0.0076 |  0.0132 |  0.0268 | 0.043  |  0.0414 |
| yol4    | -0.0009 | -0.001  | -0.001  | 0.0017 | -0.0064 |

## Karşılaştırma: yalnızca 12-1 ay momentum

| evren         |     1h |     1a |     3a |     6a |     1y |
|:--------------|-------:|-------:|-------:|-------:|-------:|
| tümü          | 0.0469 | 0.0663 | 0.0888 | 0.1012 | 0.1052 |
| yatırılabilir | 0.0179 | 0.0202 | 0.0273 | 0.0336 | 0.042  |

## Toplam modelin ayrıntısı (tüm evren)

| vade   | evren         |     IC |   IC_t |   ilk10_fazla |   son10_fazla |   fark |   isabet_ilk10 |
|:-------|:--------------|-------:|-------:|--------------:|--------------:|-------:|---------------:|
| 1h     | tümü          | 0.0876 |  17.28 |        0.0062 |       -0.0078 | 0.0141 |          0.55  |
| 1h     | yatırılabilir | 0.0523 |   8.74 |        0.0036 |       -0.0047 | 0.0083 |          0.522 |
| 1a     | tümü          | 0.1234 |   9.37 |        0.0155 |       -0.0202 | 0.0357 |          0.583 |
| 1a     | yatırılabilir | 0.0741 |   5.35 |        0.009  |       -0.0143 | 0.0233 |          0.544 |
| 3a     | tümü          | 0.1758 |   5.65 |        0.0377 |       -0.0435 | 0.0813 |          0.618 |
| 3a     | yatırılabilir | 0.1139 |   3.65 |        0.0224 |       -0.0382 | 0.0606 |          0.569 |
| 6a     | tümü          | 0.2066 |   4.58 |        0.0658 |       -0.0632 | 0.129  |          0.633 |
| 6a     | yatırılabilir | 0.1386 |   3.27 |        0.0391 |       -0.06   | 0.0991 |          0.583 |
| 1y     | tümü          | 0.2237 |   3.97 |        0.1088 |       -0.032  | 0.1407 |          0.623 |
| 1y     | yatırılabilir | 0.1449 |   2.46 |        0.059  |       -0.0589 | 0.118  |          0.572 |

## Potansiyel puanı ve gerçekleşen 3 aylık fazla getiri

| potansiyel   |   hisse-hafta |   3a ort fazla |   3a medyan fazla |
|:-------------|--------------:|---------------:|------------------:|
| 0–30         |        257971 |         0.7045 |           -0.1001 |
| 30–50        |        244549 |         0.0898 |           -0.0329 |
| 50–70        |        263778 |         0.0496 |            0.0024 |
| 70–80        |        142837 |         0.0399 |            0.0194 |
| 80–90        |        162339 |         0.0425 |            0.0264 |
| 90–100       |        217501 |         0.0436 |            0.0305 |

## Vade seçimi

Her hisse için en yüksek puanı aldığı vade (puan ≥ 70). Atanan vadedeki gerçekleşen fazla getiri, aynı hisselerin sabit 3 aylık vadesiyle haftalık eşdeğer olarak karşılaştırılır.

| atanan vade   |   hisse-hafta |   ort fazla getiri (vadede) |   haftalık eşdeğer |   aynı hisseler sabit 3a, haftalık |
|:--------------|--------------:|----------------------------:|-------------------:|-----------------------------------:|
| 1h            |        212917 |                      0.007  |            0.00702 |                            0.00337 |
| 1a            |         55532 |                      0.0159 |            0.00398 |                            0.00334 |
| 3a            |         65145 |                      0.0402 |            0.00309 |                            0.00309 |
| 6a            |         68797 |                      0.0734 |            0.00282 |                            0.0029  |
| 1y            |        112680 |                      0.1475 |            0.00284 |                            0.00309 |

## Son ağırlıklar (toplam model, en büyük 3a ağırlıklara göre)

|                                             |      1h |      1a |      3a |      6a |      1y | yol    |
|:--------------------------------------------|--------:|--------:|--------:|--------:|--------:|:-------|
| dusuk_oynaklik                              |  0.0644 |  0.101  |  0.1451 |  0.1671 |  0.1761 | piyasa |
| momentum_12_1                               |  0.0292 |  0.0394 |  0.0509 |  0.0589 |  0.0578 | piyasa |
| devamlilik_suphesi                          | -0.0157 | -0.0283 | -0.0455 | -0.059  | -0.0772 | yol1   |
| kucuk_boyut                                 |  0.005  |  0.0199 |  0.0448 |  0.0705 |  0.1028 | piyasa |
| 8k_3.02_kayıtsız hisse satışı (sulandırma)  | -0.0172 | -0.0273 | -0.0338 | -0.0392 | -0.0476 | yol3   |
| serbest_nakit_getirisi                      |  0.0113 |  0.0193 |  0.0266 |  0.0323 |  0.0418 | yol1   |
| icerden_alici_sayisi_90g                    | -0.0074 | -0.0142 | -0.0257 | -0.0313 | -0.0401 | yol3   |
| geri_alim_getirisi                          |  0.01   |  0.0167 |  0.0255 |  0.0329 |  0.0505 | yol3   |
| icerden_alim_tutar_piyasa_degeri            |  0.0103 |  0.0142 |  0.0234 |  0.0251 |  0.0314 | yol3   |
| icerden_alim_kumesi_3plus                   |  0.0053 |  0.0091 |  0.0159 |  0.0179 |  0.02   | yol3   |
| haber_ani_artis                             |  0.0063 |  0.0101 |  0.0145 |  0.0192 |  0.0212 | yol2   |
| 8k_2.01_satın alma/elden çıkarma tamamlandı | -0.005  | -0.0058 | -0.0144 | -0.0202 | -0.0215 | yol3   |
| metin_benzerligi_yonetim                    |  0.0049 |  0.009  |  0.0142 |  0.0163 |  0.0188 | yol1   |
| haber_ton_seviyesi                          | -0.0043 | -0.0092 | -0.0131 | -0.0153 | -0.0245 | yol2   |
| 8k_1.01_önemli anlaşma                      | -0.0052 | -0.0074 | -0.0127 | -0.0117 | -0.0179 | yol3   |
| haber_ton_degisimi                          |  0.0052 |  0.0099 |  0.0098 |  0.013  |  0.0177 | yol2   |
| tema_ruzgari_v3_uzun_nadir                  |  0.005  |  0.0058 |  0.0087 |  0.0138 |  0.0132 | yol4   |
| brut_marj_degisimi                          |  0.0047 |  0.0062 |  0.0086 |  0.0123 |  0.0106 | yol1   |
| kazanc_getirisi                             | -0.004  | -0.0075 | -0.0085 | -0.0034 | -0.0002 | yol1   |
| kurumsal_sahip_degisimi                     | -0.0027 | -0.0036 | -0.0079 | -0.0073 | -0.0146 | yol3   |
| faaliyet_marji_degisimi                     |  0.0039 |  0.0066 |  0.0074 |  0.0095 |  0.0152 | yol1   |
| 8k_2.03_yeni borç yükümlülüğü               |  0.0046 |  0.0058 |  0.007  |  0.0072 |  0.0142 | yol3   |
| haber_ivmesi                                | -0.0007 |  0.0005 |  0.0069 |  0.0127 |  0.0209 | yol2   |
| tahakkuklar_dusuk                           | -0.004  | -0.0057 | -0.0066 | -0.004  | -0.0022 | yol1   |
| wiki_ani_ilgi                               |  0.0011 |  0.0024 |  0.0061 |  0.0139 |  0.018  | yol2   |
| ust_yonetici_alimi_90g                      |  0.0047 |  0.0065 |  0.0055 |  0.0067 |  0.0083 | yol3   |
| kisa_vade_donus                             |  0.0355 |  0.0245 |  0.0053 | -0.0086 | -0.0147 | piyasa |
| 8k_1.02_anlaşma feshi                       |  0.0015 | -0      |  0.0043 |  0.0085 |  0.0135 | yol3   |
| buyume_ivmesi                               | -0.0015 | -0.0022 | -0.0042 | -0.0045 | -0.0049 | yol1   |
| gelir_buyumesi                              |  0.0051 |  0.0055 |  0.0041 |  0.0043 |  0.0008 | yol1   |
| metin_benzerligi_is_tanimi                  |  0.0013 |  0.0032 |  0.004  |  0.0058 |  0.0063 | yol1   |
| arge_yogunlugu                              | -0.0018 | -0.0017 | -0.0039 | -0.0065 | -0.0152 | yol1   |
| tema_ruzgari_v2_nadir                       | -0.0005 |  0.0015 |  0.0039 |  0.0047 |  0.0091 | yol4   |
| metin_benzerligi_ortalama                   | -0.0014 | -0.0033 | -0.0038 | -0.0027 |  0.0009 | yol1   |
| metin_benzerligi_riskler                    |  0.0017 |  0.0037 |  0.0037 |  0.0018 | -0.0022 | yol1   |
| wiki_ilgi_ivmesi                            |  0.0018 |  0.0028 |  0.0037 |  0.0017 | -0.006  | yol2   |
| tema_ruzgari_v1_uzun                        | -0.0004 | -0.0024 | -0.0032 |  0.0035 |  0.0207 | yol4   |
| 8k_7.01_kamuyu aydınlatma (FD)              |  0.0001 | -0.0006 |  0.0022 |  0.0013 | -0.0007 | yol3   |
| kurumsal_hisse_degisimi_payi                |  0.0023 |  0.0017 | -0.0019 | -0.013  |  0.0007 | yol3   |
| 8k_8.01_diğer olaylar                       | -0.001  | -0.0026 | -0.0014 | -0.0017 | -0.0014 | yol3   |
| 8k_5.02_yönetici değişikliği                |  0.0012 |  0.0019 |  0.001  |  0.003  |  0.006  | yol3   |
| tema_ruzgari                                | -0.0002 |  0.0011 | -0.001  | -0.0116 | -0.024  | yol4   |
| varlik_buyumesi_dusuk                       | -0.0028 | -0.0017 | -0.0005 | -0.0008 | -0.0061 | yol1   |
| risk_bolumu_buyumesi_dusuk                  | -0.0007 | -0.0007 |  0      | -0.0003 | -0.0003 | yol1   |

## Birbirine en çok benzeyen sinyaller (ortalama kesitsel sıra korelasyonu)

|                                                             |   korelasyon |
|:------------------------------------------------------------|-------------:|
| ('icerden_alici_sayisi_90g', 'icerden_alim_kumesi_3plus')   |        0.842 |
| ('tema_ruzgari', 'tema_ruzgari_v2_nadir')                   |        0.714 |
| ('metin_benzerligi_is_tanimi', 'metin_benzerligi_ortalama') |        0.685 |
| ('metin_benzerligi_yonetim', 'metin_benzerligi_ortalama')   |        0.674 |
| ('tema_ruzgari_v1_uzun', 'tema_ruzgari_v3_uzun_nadir')      |        0.656 |
| ('serbest_nakit_getirisi', 'kazanc_getirisi')               |        0.644 |
| ('metin_benzerligi_riskler', 'metin_benzerligi_ortalama')   |        0.611 |
| ('kucuk_boyut', 'icerden_alim_tutar_piyasa_degeri')         |        0.588 |
| ('haber_ton_degisimi', 'haber_ton_seviyesi')                |        0.555 |
| ('gelir_buyumesi', 'faaliyet_marji_degisimi')               |        0.528 |
| ('8k_1.01_önemli anlaşma', '8k_2.03_yeni borç yükümlülüğü') |        0.52  |
| ('tema_ruzgari', 'tema_ruzgari_v1_uzun')                    |        0.519 |
| ('dusuk_oynaklik', 'kazanc_getirisi')                       |        0.518 |
| ('tema_ruzgari_v2_nadir', 'tema_ruzgari_v3_uzun_nadir')     |        0.516 |
| ('gelir_buyumesi', 'buyume_ivmesi')                         |        0.486 |

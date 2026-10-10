# 4. aşama: kayan pencere modeli

Dönem: 2016 → 2025-07-01 öncesi; son dönem kullanılmadı. Her hafta yalnızca o ana kadar gerçekleşmiş getirilerle eğitilen modelin tahmini değerlendirilir (örneklem dışı). Değerler IC (puan ile gerçekleşen fazla getirinin sıralama korelasyonu).

## Örneklem dışı IC — tüm evrende eğitilen modeller, tüm evrende ölçüm

| model   |     1h |     1a |     3a |     6a |      1y |
|:--------|-------:|-------:|-------:|-------:|--------:|
| piyasa  | 0.0533 | 0.062  | 0.0807 | 0.0902 |  0.09   |
| toplam  | 0.0721 | 0.0975 | 0.1366 | 0.1626 |  0.1809 |
| yol1    | 0.0561 | 0.0855 | 0.1208 | 0.1412 |  0.1564 |
| yol2    | 0.0078 | 0.0118 | 0.0167 | 0.0184 |  0.0128 |
| yol3    | 0.0191 | 0.0298 | 0.0424 | 0.0505 |  0.0538 |
| yol4    | 0.0049 | 0.0073 | 0.0082 | 0.0091 | -0.0078 |

## Örneklem dışı IC — yatırılabilir evrende ölçüm

Tüm evrende eğitilen:

| model   |     1h |     1a |     3a |     6a |      1y |
|:--------|-------:|-------:|-------:|-------:|--------:|
| piyasa  | 0.0306 | 0.0288 | 0.0283 | 0.0271 |  0.0171 |
| toplam  | 0.0423 | 0.0554 | 0.0789 | 0.0965 |  0.101  |
| yol1    | 0.0328 | 0.0503 | 0.0765 | 0.0975 |  0.1092 |
| yol2    | 0.0082 | 0.0103 | 0.0147 | 0.0154 |  0.0082 |
| yol3    | 0.0081 | 0.0143 | 0.0285 | 0.0421 |  0.044  |
| yol4    | 0.0017 | 0.0048 | 0.0057 | 0.0065 | -0.0134 |

Yatırılabilir evrende eğitilen:

| model   |      1h |      1a |      3a |      6a |      1y |
|:--------|--------:|--------:|--------:|--------:|--------:|
| piyasa  |  0.0302 |  0.022  |  0.0096 | -0.0075 | -0.0048 |
| toplam  |  0.0402 |  0.0501 |  0.0693 |  0.0869 |  0.0816 |
| yol1    |  0.0306 |  0.0475 |  0.0718 |  0.0928 |  0.0901 |
| yol2    |  0.0077 |  0.0081 |  0.0108 |  0.0071 |  0.0123 |
| yol3    |  0.0076 |  0.0132 |  0.0268 |  0.043  |  0.0414 |
| yol4    | -0.0009 | -0.001  | -0.001  |  0.0017 | -0.0064 |

## Karşılaştırma: yalnızca 12-1 ay momentum

| evren         |     1h |     1a |     3a |     6a |     1y |
|:--------------|-------:|-------:|-------:|-------:|-------:|
| tümü          | 0.0469 | 0.0663 | 0.0888 | 0.1012 | 0.1052 |
| yatırılabilir | 0.0179 | 0.0202 | 0.0273 | 0.0336 | 0.042  |

## Toplam modelin ayrıntısı (tüm evren)

| vade   | evren         |     IC |   IC_t |   ilk10_fazla |   son10_fazla |   fark |   isabet_ilk10 |
|:-------|:--------------|-------:|-------:|--------------:|--------------:|-------:|---------------:|
| 1h     | tümü          | 0.0721 |  17.47 |        0.0073 |       -0.0054 | 0.0127 |          0.54  |
| 1h     | yatırılabilir | 0.0423 |   8.86 |        0.0043 |       -0.0036 | 0.0079 |          0.52  |
| 1a     | tümü          | 0.0975 |  10.04 |        0.0194 |       -0.0134 | 0.0328 |          0.565 |
| 1a     | yatırılabilir | 0.0554 |   6.25 |        0.011  |       -0.0097 | 0.0207 |          0.533 |
| 3a     | tümü          | 0.1366 |   5.94 |        0.0478 |       -0.0278 | 0.0755 |          0.587 |
| 3a     | yatırılabilir | 0.0789 |   3.97 |        0.0286 |       -0.0257 | 0.0543 |          0.545 |
| 6a     | tümü          | 0.1626 |   4.52 |        0.0884 |       -0.0362 | 0.1247 |          0.602 |
| 6a     | yatırılabilir | 0.0965 |   3.29 |        0.0561 |       -0.0403 | 0.0964 |          0.558 |
| 1y     | tümü          | 0.1809 |   4.3  |        0.1545 |        0.004  | 0.1505 |          0.607 |
| 1y     | yatırılabilir | 0.101  |   2.66 |        0.0943 |       -0.0341 | 0.1285 |          0.556 |

## Potansiyel puanı ve gerçekleşen 3 aylık fazla getiri

| potansiyel   |   hisse-hafta |   3a kırpılmış ort fazla |   3a medyan fazla |   pozitif fazla getiri payı |
|:-------------|--------------:|-------------------------:|------------------:|----------------------------:|
| 0–30         |        238408 |                  -0.0098 |           -0.0743 |                       0.4   |
| 30–50        |        207831 |                   0.0189 |           -0.0169 |                       0.469 |
| 50–70        |        268814 |                   0.0228 |            0.0035 |                       0.508 |
| 70–80        |        162662 |                   0.0308 |            0.0127 |                       0.532 |
| 80–90        |        185760 |                   0.0333 |            0.0173 |                       0.546 |
| 90–100       |        225500 |                   0.0433 |            0.0234 |                       0.563 |

## Vade seçimi

Her hisse için en yüksek puanı aldığı vade (puan ≥ 70). Atanan vadedeki gerçekleşen fazla getiri, aynı hisselerin sabit 3 aylık vadesiyle haftalık eşdeğer olarak karşılaştırılır.

| atanan vade   |   hisse-hafta |   ort fazla getiri (vadede) |   haftalık eşdeğer |   aynı hisseler sabit 3a, haftalık |
|:--------------|--------------:|----------------------------:|-------------------:|-----------------------------------:|
| 1h            |        235324 |                      0.0092 |            0.00921 |                            0.00317 |
| 1a            |         65085 |                      0.018  |            0.0045  |                            0.0037  |
| 3a            |         64928 |                      0.0629 |            0.00484 |                            0.00484 |
| 6a            |         76085 |                      0.0855 |            0.00329 |                            0.00333 |
| 1y            |        124562 |                      0.1539 |            0.00296 |                            0.00323 |

## Son ağırlıklar (toplam model, en büyük 3a ağırlıklara göre)

|                                             |      1h |      1a |      3a |      6a |      1y | yol    |
|:--------------------------------------------|--------:|--------:|--------:|--------:|--------:|:-------|
| momentum_12_1                               |  0.0398 |  0.0559 |  0.0745 |  0.0861 |  0.0871 | piyasa |
| devamlilik_suphesi                          | -0.0217 | -0.038  | -0.0597 | -0.0759 | -0.0953 | yol1   |
| serbest_nakit_getirisi                      |  0.0223 |  0.0366 |  0.0515 |  0.0608 |  0.0709 | yol1   |
| kucuk_boyut                                 |  0.0064 |  0.0216 |  0.0472 |  0.0733 |  0.1062 | piyasa |
| 8k_3.02_kayıtsız hisse satışı (sulandırma)  | -0.021  | -0.0334 | -0.0427 | -0.0494 | -0.0585 | yol3   |
| geri_alim_getirisi                          |  0.0119 |  0.0197 |  0.0298 |  0.0379 |  0.0561 | yol3   |
| icerden_alici_sayisi_90g                    | -0.009  | -0.0167 | -0.0294 | -0.0358 | -0.0448 | yol3   |
| kazanc_getirisi                             |  0.0127 |  0.0187 |  0.0289 |  0.0396 |  0.0458 | yol1   |
| metin_benzerligi_yonetim                    |  0.0094 |  0.0161 |  0.0244 |  0.0281 |  0.0311 | yol1   |
| tahakkuklar_dusuk                           | -0.011  | -0.0165 | -0.022  | -0.0216 | -0.0209 | yol1   |
| icerden_alim_kumesi_3plus                   |  0.0063 |  0.0107 |  0.0183 |  0.0208 |  0.0228 | yol3   |
| 8k_1.01_önemli anlaşma                      | -0.0077 | -0.0114 | -0.0183 | -0.0183 | -0.0249 | yol3   |
| icerden_alim_tutar_piyasa_degeri            |  0.0073 |  0.0096 |  0.0169 |  0.0179 |  0.0241 | yol3   |
| kurumsal_sahip_degisimi                     | -0.0059 | -0.0086 | -0.0149 | -0.0153 | -0.0226 | yol3   |
| 8k_2.01_satın alma/elden çıkarma tamamlandı | -0.0049 | -0.0055 | -0.0138 | -0.0195 | -0.0205 | yol3   |
| 8k_2.03_yeni borç yükümlülüğü               |  0.0073 |  0.01   |  0.0131 |  0.0143 |  0.0216 | yol3   |
| metin_benzerligi_is_tanimi                  |  0.0053 |  0.0095 |  0.013  |  0.0164 |  0.0179 | yol1   |
| haber_ani_artis                             |  0.0054 |  0.0088 |  0.0125 |  0.0169 |  0.0189 | yol2   |
| faaliyet_marji_degisimi                     |  0.0061 |  0.0101 |  0.0125 |  0.0154 |  0.0212 | yol1   |
| arge_yogunlugu                              | -0.0044 | -0.0059 | -0.0101 | -0.0138 | -0.0233 | yol1   |
| tema_ruzgari_v3_uzun_nadir                  |  0.0042 |  0.0046 |  0.0071 |  0.0119 |  0.0113 | yol4   |
| haber_ivmesi                                | -0.0006 |  0.0006 |  0.007  |  0.013  |  0.0214 | yol2   |
| brut_marj_degisimi                          |  0.004  |  0.0051 |  0.0068 |  0.0103 |  0.0085 | yol1   |
| haber_ton_degisimi                          |  0.0034 |  0.0071 |  0.0056 |  0.008  |  0.0123 | yol2   |
| wiki_ilgi_ivmesi                            |  0.0027 |  0.0042 |  0.0055 |  0.0041 | -0.0033 | yol2   |
| ust_yonetici_alimi_90g                      |  0.0046 |  0.0064 |  0.0054 |  0.0066 |  0.0079 | yol3   |
| tema_ruzgari                                | -0.0021 | -0.0019 | -0.0054 | -0.0169 | -0.03   | yol4   |
| tema_ruzgari_v2_nadir                       | -0.0001 |  0.002  |  0.0047 |  0.0057 |  0.0103 | yol4   |
| kurumsal_hisse_degisimi_payi                |  0.0013 |  0      | -0.0044 | -0.016  | -0.0022 | yol3   |
| wiki_ani_ilgi                               |  0.0003 |  0.0012 |  0.0042 |  0.0119 |  0.0158 | yol2   |
| 8k_7.01_kamuyu aydınlatma (FD)              |  0.0009 |  0.0007 |  0.0042 |  0.0036 |  0.0016 | yol3   |
| metin_benzerligi_ortalama                   | -0.001  | -0.0028 | -0.0031 | -0.0019 |  0.0015 | yol1   |
| 8k_1.02_anlaşma feshi                       |  0.0006 | -0.0015 |  0.0024 |  0.0061 |  0.0108 | yol3   |
| tema_ruzgari_v1_uzun                        |  0.0004 | -0.0011 | -0.0012 |  0.0064 |  0.0251 | yol4   |
| gelir_buyumesi                              |  0.0028 |  0.0018 | -0.0012 | -0.0017 | -0.0056 | yol1   |
| 8k_5.02_yönetici değişikliği                |  0.0011 |  0.0017 |  0.0008 |  0.0028 |  0.0056 | yol3   |
| buyume_ivmesi                               |  0      |  0.0002 | -0.0007 | -0.0005 | -0.0003 | yol1   |
| varlik_buyumesi_dusuk                       | -0.0027 | -0.0017 | -0.0006 | -0.001  | -0.0058 | yol1   |
| metin_benzerligi_riskler                    |  0.0003 |  0.0014 |  0.0005 | -0.0019 | -0.0063 | yol1   |
| 8k_8.01_diğer olaylar                       | -0.0002 | -0.0013 |  0.0004 |  0.0005 |  0.0009 | yol3   |
| kisa_vade_donus                             |  0.0333 |  0.021  |  0.0003 | -0.0144 | -0.0205 | piyasa |
| risk_bolumu_buyumesi_dusuk                  | -0.0007 | -0.0006 |  0.0001 | -0.0001 | -0      | yol1   |
| haber_ton_seviyesi                          |  0.0015 | -0.0001 |  0.0001 |  0.0001 | -0.0081 | yol2   |

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

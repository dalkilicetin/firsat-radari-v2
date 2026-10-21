# Kriz kataloğu incelemesi

> n = 13 S&P 500 düşüşü. Bu bir **test değil**, hipotez üretme alıştırmasıdır. Katalog değerleri yaklaşık ve hafızadan yazılmıştır.

## 1. Düşüşler, hızlıdan yavaşa (günlük ortalama kayıp, %)

| Kriz | Yıl | Düşüş % | Dibe gün | Hız %/gün | Toparlanma (ay) | Sertlik | Etiket |
|---|---|---|---|---|---|---|---|
| 2020 | 2020 | -33.9 | 23.0 | -1.47 | 5.0 | 4.6 | panik |
| 1998 | 1998 | -19.3 | 31.0 | -0.62 | 2.9 | 1.9 | panik |
| 2025 | 2025 | -18.9 | 34.0 | -0.56 | 2.8 | 1.7 | panik |
| 1987 | 1987 | -33.5 | 73.0 | -0.46 | 20.4 | 5.9 | panik |
| 2010 | 2010 | -16.0 | 50.0 | -0.32 | 4.2 | 1.8 | panik |
| 1990 | 1990 | -19.9 | 63.0 | -0.32 | 4.2 | 1.4 | karma |
| 2018 | 2018 | -19.8 | 67.0 | -0.3 | 4.1 | 1.3 | panik |
| 2011 | 2011 | -19.4 | 111.0 | -0.17 | 5.0 | 0.9 | panik |
| 2023 | 2023 | -10.3 | 64.0 | -0.16 | 1.2 | 0.4 | panik |
| 2007 | 2007 | -56.8 | 369.0 | -0.15 | 50.4 | 2.9 | bozulma |
| 2022 | 2022 | -25.4 | 202.0 | -0.13 | 15.8 | 1.6 | bozulma |
| 2015 | 2015 | -14.2 | 190.0 | -0.07 | 5.1 | 0.6 | karma |
| 2000 | 2000 | -49.1 | 663.0 | -0.07 | 57.6 | 1.8 | bozulma |


## 2. Düşüş hızı ile toparlanma süresi

- Spearman(hız, toparlanma günü) = 0.48 (p=0.10, n=13). Hız negatif sayı olduğundan **pozitif ρ = hızlı düşüş daha hızlı toparlanır**.
- Spearman(düşüş derinliği, toparlanma günü) = -0.75 (p=0.00). **Derinlik toparlanmayı mekanik olarak uzatır** (eski zirveye dönmek için daha çok yol).
- Derinlik sabitlenince (sıra kısmi korelasyon) hız–toparlanma ρ = 0.60 (p=0.03). Hız ilişkisi esas olarak derinlikten geliyorsa 'yay hızı' ayrı bir bilgi taşımıyor demektir.
- Spearman(dibe kadar gün, toparlanma günü) = 0.72 (p=0.01)
- Medyan hız: -0.30 %/gün; medyan toparlanma: 104 iş günü

```
gun_toparlanma  kisa toparlanma  uzun toparlanma
hiz                                             
hizli dusus                   5                2
yavas dusus                   2                4
```

## 3. Gruplara göre medyan toparlanma (ay)

**Resesyon (sonradan bilinir)**

```
          n  medyan_toparlanma_ay  medyan_dusus_p
resesyon                                         
E         4                  27.7           -41.5
H         9                   4.2           -19.3
```

**Kredi stresi**

```
              n  medyan_toparlanma_ay  medyan_dusus_p
kredi_stresi                                         
cok_yuksek    1                  50.4           -56.8
dusuk         2                  10.8           -21.9
orta          6                   4.2           -19.6
orta_yuksek   1                   5.1           -14.2
yuksek        3                   5.0           -33.9
```

**Politika tepkisi**

```
                        n  medyan_toparlanma_ay  medyan_dusus_p
politika_tepkisi                                               
Fed_donusu              1                   4.1           -19.8
QE2                     1                   4.2           -16.0
QE_ve_kurtarma          1                  50.4           -56.8
faiz_artisi_erteleme    1                   5.1           -14.2
faiz_indirimi           2                  30.9           -34.5
faiz_indirimi_kurtarma  1                   2.9           -19.3
faiz_indirimi_likidite  1                  20.4           -33.5
faiz_zirvesi            1                   1.2           -10.3
operation_twist         1                   5.0           -19.4
sikilastirma_devam      1                  15.8           -25.4
sinirsiz_QE_ve_tesvik   1                   5.0           -33.9
tarife_ertelemesi       1                   2.8           -18.9
```

**Etiket (panik / bozulma / karma; sonradan konmuş, sadece karşılaştırma)**

```
              n  top_ay  sertlik  dusus_p
tur_on_kabul                             
bozulma       3    50.4      1.8    -49.1
karma         2     4.7      1.0    -17.0
panik         8     4.2      1.7    -19.4
```

## 4. VIX zirvesi ve dip

- VIX zirvesi dipten **önce** gelen kriz: 10/13; dipten ±10 iş günü içinde olan: 4/13
- Medyan fark (iş günü, + = VIX zirvesi dipten önce): 34

```
kimlik  vix_zirve  vix_dipten_once
  1987        NaN             34.0
  1990       36.5             35.0
  1998       45.7            -28.0
  2000       45.1             47.0
  2007       80.9             77.0
  2010       45.8             31.0
  2011       48.0             40.0
  2015       40.7            123.0
  2018       36.1              0.0
  2020       82.7              5.0
  2022       36.5            157.0
  2023       21.7              5.0
  2025       52.3              0.0
```

- Spearman(VIX zirvesi, toparlanma günü) = 0.27 (p=0.40, n=12)

## 5. 'O anda bilinebilir mi?'

| Sütun | Durum |
|---|---|
| hiz | kismen (dibe kadar olan hiz gercek zamanda izlenir; dipteki nihai hiz sonradan) |
| dusus | kismen (o ana kadarki dusus gercek zamanli; nihai dip sonradan) |
| vix_zirve | gercek zamanli (VIX o gun gorulur) |
| kredi_sayi | gercek zamanli (spread izlenir) |
| resesyon_sayi | SONRADAN (resesyon aylar sonra ilan edilir) |
| gun_dibe | SONRADAN (dip tarihi bilinmez) |

Sadece gerçek zamanlı/kısmen bilinen sütunlardan çıkan desenler hipotez sayılır.

## 6. Karşı örnekler (yay olmayan)

| Vaka | Düşüş % | Dibe (yıl) | Toparlanma (yıl) | Kredi stresi | Politika |
|---|---|---|---|---|---|
| N1989 | -81.9 | 19.9 | 15.5 | cok_yuksek | yetersiz |
| NDX2000 | -77.9 | 2.7 | 13.0 | yuksek | faiz_indirimi |

SPX medyan: dibe 0.27 yıl, toparlanma 0.41 yıl. Karşı örneklerde dibe ulaşma ve toparlanma çok daha uzun; ortak nokta düşüşün **yavaş**, **kredi/banka kaynaklı** ve politika desteğinin **yetersiz/geç** olması.

## 7. Üretilen hipotezler (n=13, test değil)

1. **Hızlı düşüş → hızlı toparlanma** ham ρ = 0.48, derinlik sabitlenince 0.60. Derinlik sabitlenince de yön korunuyor; ancak 'hız' = düşüş / dibe kadar gün olduğundan bu büyük ölçüde **süre simetrisi** (uzun süren düşüş uzun süren toparlanma; ρ(dibe gün, toparlanma) yukarıda). Yay'a özgü bir bilgi mi, sadece süre mi, simülasyonda (S2) ayrıştırılacak.
2. **Kredi stresi tek başına panik/bozulma ayırt etmeye yetmiyor.** Kredi stresi yüksek (4-5) krizler: 1998 (3 ay), 2020 (5 ay), 2007 (50 ay), 2000 (58 ay); düşük (1-2): 1987 (20 ay), 1990 (4 ay), 2010 (4 ay), 2011 (5 ay), 2018 (4 ay), 2022 (16 ay), 2023 (1 ay), 2025 (3 ay). Yüksek kredi stresli krizlerin bir kısmı hızlı toparlandı (müdahale ile kredi stresi hızla söndüğünde); ayırt edici olan stresin **düzeyi değil, ne kadar sürdüğü/açıldığı** olabilir. Test: `kredi60` (60 günlük değişim) ve `sahm` birlikte (L6-S1, `panik_kredi` duyarlılığı).
3. **VIX zirvesi dip için tek başına yeterli değil.** VIX zirvesi dipten önce gelen kriz 10/13, ±10 iş günü içinde olan 4/13. 'VIX zirveden düştü' işareti dibe yakınlık verebilir ama dipten önce ek düşüş kalabilir: bu yüzden asıl ölçüm **MAE** (Yay Y2).
4. **En uzun toparlananlar:** 1987 (20 ay, etiket: panik), 2000 (58 ay, etiket: bozulma), 2007 (50 ay, etiket: bozulma). Etiketi 'panik' olan 1987 de uzun sürdü: 'panik = hızlı dönüş' kuralı derin düşüşlerde (−%30+) zayıflıyor olabilir; derinlik ayrıca kontrol edilmeli.
5. **Politika tepkisi (Gelgit adayı):** kategoriler n=1'lik ve çok dağınık; tabloda net bir desen yok (örn. QE'li 2007 en uzun, QE'li 2020 kısa). Bu katalogdan hipotez çıkmıyor; Gelgit sadece simülasyonda 'likidite durumu' değişkeni olarak sınanır (L10).

> Uyarı: n = 13, birçok sütunu birlikte inceledik (çoklu karşılaştırma). Bu hipotezler **L6 (simülasyon)** ve **L7 (gerçek örnek)** ile ayrıca sınanacak.

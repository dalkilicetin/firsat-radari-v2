# S5 — Hisse yayı ⟷ Gizli güç

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

20 dünya × 60 yıl; her krizde (Y2'nin ilk günü, *gerçek dip değil*) hisseler zirveden bu yana **beta'dan arındırılmış kalıntı getirisine** göre 5 dilime ayrılır. **D1 = en çok düşen (yay adayı), D5 = en az düşen (gizli güç adayı).** Sonraki 63/126/252 bar getiri evren ortalamasına göre. Toplam 321 kriz.

**Önemli kontrol:** simülatörde her hissenin kendine özgü sapması normal zamanda da geri döner (kısa vadeli ters dönüş, krizden bağımsız); gerçek piyasada da benzeri olabilir. Bu yüzden her krizin yanında **aynı pencere uzunluğunda 3 sakin tarihte** aynı sıralama yapılır; tablodaki 'krize özgü' sütunu `kriz − sakin taban` farkıdır.

İki tür etiket: *ayrıştırma* (düşüşün çoğu geri dönen `m`'den mi — rastgele düşüşler de 'bozulma' sayılır) ve *olay* (zirve–t arasında gerçekten bozulma/panik olayı var mıydı).

## Ufuk 63 bar

| Grup | n | D1 − D5 (kriz) | D1 − D5 (sakin taban) | **Krize özgü** [%90 GA] |
|---|---|---|---|---|
| Tüm krizler | 321 | 3.0% | 2.6% | **0.3%** [0.0%, 0.7%] |
| Ayrıştırma etiketi: panik | 108 | 4.1% | 2.7% | **1.4%** [0.7%, 2.0%] |
| Ayrıştırma etiketi: bozulma | 213 | 2.4% | 2.6% | **-0.2%** [-0.5%, 0.2%] |
| Olay etiketi: panik olayı | 120 | 3.9% | 2.7% | **1.2%** [0.6%, 2.0%] |
| Olay etiketi: bozulma olayı | 101 | 2.2% | 2.7% | **-0.4%** [-1.0%, 0.1%] |
| Olay etiketi: olaysız (rastgele düşüş) | 100 | 2.6% | 2.5% | **0.1%** [-0.4%, 0.8%] |

## Ufuk 126 bar

| Grup | n | D1 − D5 (kriz) | D1 − D5 (sakin taban) | **Krize özgü** [%90 GA] |
|---|---|---|---|---|
| Tüm krizler | 321 | 4.4% | 3.5% | **0.8%** [0.4%, 1.3%] |
| Ayrıştırma etiketi: panik | 108 | 6.0% | 3.7% | **2.3%** [1.2%, 3.2%] |
| Ayrıştırma etiketi: bozulma | 213 | 3.5% | 3.4% | **0.1%** [-0.4%, 0.5%] |
| Olay etiketi: panik olayı | 120 | 5.7% | 3.8% | **1.9%** [0.9%, 2.8%] |
| Olay etiketi: bozulma olayı | 101 | 3.7% | 3.5% | **0.2%** [-0.5%, 1.0%] |
| Olay etiketi: olaysız (rastgele düşüş) | 100 | 3.4% | 3.2% | **0.2%** [-0.4%, 1.0%] |

## Ufuk 252 bar

| Grup | n | D1 − D5 (kriz) | D1 − D5 (sakin taban) | **Krize özgü** [%90 GA] |
|---|---|---|---|---|
| Tüm krizler | 321 | 5.5% | 4.4% | **1.1%** [0.5%, 1.9%] |
| Ayrıştırma etiketi: panik | 108 | 7.4% | 4.8% | **2.6%** [0.8%, 3.9%] |
| Ayrıştırma etiketi: bozulma | 213 | 4.5% | 4.2% | **0.3%** [-0.2%, 1.3%] |
| Olay etiketi: panik olayı | 120 | 6.9% | 4.8% | **2.0%** [0.6%, 3.5%] |
| Olay etiketi: bozulma olayı | 101 | 4.1% | 4.2% | **-0.1%** [-0.8%, 1.2%] |
| Olay etiketi: olaysız (rastgele düşüş) | 100 | 5.2% | 4.1% | **1.1%** [0.1%, 2.4%] |

## Sonuç (ufuk 126, olay etiketi)

- Panik olaylarında krize özgü fark **1.9%** [0.9%, 2.8%]; bozulma olaylarında **0.2%** [-0.5%, 1.0%].
- D1 − D5'in toplamı 4.4%, ama bunun 3.5%'i sakin dönemde de var (genel ters dönüş): **krize özgü pay küçük**.
- Yani 'panikte en çok düşen ekstra toparlanır' simülasyonda ölçülebiliyor; 'bozulmada dayanıklı olan ekstra kazanır' bu gürültü düzeyinde ölçülemiyor.

## Okuma
- **Krize özgü** pozitif: en çok düşenler, normal zamandaki ters dönüşün *ötesinde* krizde ekstra geri dönüyor (yay). Negatif: en az düşenler krizde ekstra avantaj kazanıyor (gizli güç).
- Tüm gruplarda 'sakin taban' büyükse, kriz sıralamasının getirisi çoğunlukla normal ters dönüşten gelir ve **krize özgü bir hikâye** değildir. Bu, R2'deki gerçek veri için de zorunlu bir kontroldür.
- Gizli güç hipotezi (G1/G3) bozulma olayı satırında *negatif* krize özgü fark bekler; gelmiyorsa simülatördeki kalite etkisi ya da sıralama gürültüsü baskındır. Sonuç kanıt değil, aletin duyarlılığıdır.
- Hisse sıralamasındaki gürültü (günlük 1.5% kendine özgü sapma) çok yüksek; bu, gerçek verideki dilim farklarının da küçük olacağı anlamına gelir.

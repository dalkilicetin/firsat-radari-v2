# L10 — Kenetlenme ve Gelgit: Yay / Gizli güç / Kırılma hangi koşulda daha iyi?

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

**Kenetlenme** = son 63 barın ortalama ikili korelasyonu; **Gelgit** = likidite endeksinin 63 bar değişimi (yüksek = sıkılaşma). Her ikisi de olay anında **genişleyen yüzdeliğe** göre üçe bölünür (düşük/orta/yüksek; geleceğe bakmaz).
Koşulların kendi etkisini ayırmak için 'fark' = olay ortalaması − **aynı terçildeki bütün günlerin** ortalaması.

## A. Yay (Y2, 63 bar) × koşul

### NORMAL dünya (kalibre) — 517 olay

| Kenetlenme terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 40 | 3.2% [1.4, 6.0] (n=40) | 1.7% | **1.5%** | -5.3% (-6.0%) |
| orta | 68 | 2.6% [1.5, 4.0] (n=68) | 2.4% | **0.2%** | -6.2% (-5.8%) |
| yüksek | 409 | 3.0% [1.7, 4.5] (n=409) | 2.7% | **0.4%** | -9.5% (-7.8%) |

| Gelgit (likidite değişimi) terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 96 | 2.3% [0.6, 4.5] (n=96) | 2.7% | **-0.4%** | -7.5% (-5.9%) |
| orta | 112 | 1.0% [-0.6, 2.9] (n=112) | 2.2% | **-1.2%** | -7.9% (-6.2%) |
| yüksek | 309 | 3.9% [2.4, 5.7] (n=309) | 1.8% | **2.1%** | -9.5% (-7.6%) |

- Kenetlenme: yüksek − düşük terçil farkı **-1.1%** [-4.5%, 2.2%]
- Gelgit: yüksek − düşük terçil farkı **2.5%** [-0.2%, 5.0%]

### KONTROL: gelgit etkisi kapalı — 516 olay

| Kenetlenme terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 43 | 3.4% [1.4, 6.2] (n=43) | 1.8% | **1.6%** | -5.1% (-5.9%) |
| orta | 72 | 2.7% [1.3, 4.4] (n=72) | 2.5% | **0.2%** | -6.3% (-5.7%) |
| yüksek | 401 | 3.3% [2.0, 4.7] (n=401) | 2.7% | **0.6%** | -9.0% (-7.7%) |

| Gelgit (likidite değişimi) terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 93 | 2.9% [1.5, 4.8] (n=93) | 2.7% | **0.3%** | -6.9% (-5.9%) |
| orta | 112 | 0.7% [-0.9, 2.8] (n=112) | 2.3% | **-1.6%** | -8.0% (-6.2%) |
| yüksek | 311 | 4.3% [2.7, 6.0] (n=311) | 2.1% | **2.2%** | -8.9% (-7.4%) |

- Kenetlenme: yüksek − düşük terçil farkı **-1.0%** [-4.5%, 2.2%]
- Gelgit: yüksek − düşük terçil farkı **1.9%** [-0.7%, 4.6%]

### KONTROL: ortak faktör stresle artmıyor — 520 olay

| Kenetlenme terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 38 | 4.1% [1.8, 7.4] (n=38) | 1.9% | **2.2%** | -4.8% (-5.9%) |
| orta | 75 | 3.0% [1.5, 4.9] (n=75) | 2.6% | **0.4%** | -6.3% (-5.7%) |
| yüksek | 407 | 3.0% [1.6, 4.4] (n=407) | 2.3% | **0.7%** | -9.5% (-8.0%) |

| Gelgit (likidite değişimi) terçili | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |
|---|---|---|---|---|---|
| düşük | 92 | 3.3% [1.5, 5.4] (n=92) | 2.7% | **0.6%** | -7.0% (-5.9%) |
| orta | 114 | 1.4% [-0.4, 3.3] (n=114) | 2.2% | **-0.8%** | -7.9% (-6.2%) |
| yüksek | 314 | 3.6% [2.0, 5.4] (n=314) | 1.8% | **1.7%** | -9.5% (-7.6%) |

- Kenetlenme: yüksek − düşük terçil farkı **-1.5%** [-5.2%, 1.9%]
- Gelgit: yüksek − düşük terçil farkı **1.2%** [-1.6%, 4.0%]

## B. Hisse yayı ⟷ Gizli güç × koşul

**Kenetlenme (ort. korelasyon)** — kalıntı sıralaması, ufuk 126, krize özgü D1 − D5 (kriz − sakin taban)

| Terçil | n kriz | Krize özgü D1 − D5 [%90 GA] | Panik olayı | Bozulma olayı |
|---|---|---|---|---|
| düşük | 31 | **-0.5%** [-1.3%, 0.9%] | – | – |
| orta | 52 | **0.2%** [-0.8%, 1.3%] | -0.8% | – |
| yüksek | 238 | **1.1%** [0.5%, 1.8%] | 2.1% | 0.3% |

**Gelgit (likidite değişimi)** — kalıntı sıralaması, ufuk 126, krize özgü D1 − D5 (kriz − sakin taban)

| Terçil | n kriz | Krize özgü D1 − D5 [%90 GA] | Panik olayı | Bozulma olayı |
|---|---|---|---|---|
| düşük | 47 | **0.0%** [-0.9%, 0.9%] | – | 0.8% |
| orta | 68 | **0.3%** [-0.5%, 1.3%] | – | -0.3% |
| yüksek | 206 | **1.2%** [0.6%, 1.9%] | 1.9% | 0.4% |

## C. Kırılma noktası AUC × koşul (kalibre dünya, test dünyaları)

- **panikten_normale** (ufuk 63): Kenetlenme (ort_kor_63): düşük AUC 0.67 (n=1043), orta AUC 0.76 (n=1848), yüksek AUC 0.79 (n=1948); Gelgit (likidite değişimi): düşük AUC 0.75 (n=1666), orta AUC 0.75 (n=1707), yüksek AUC 0.77 (n=1466)
- **yukselisten_dususe** (ufuk 63): Kenetlenme (ort_kor_63): düşük AUC 0.73 (n=4590), orta AUC 0.71 (n=6332), yüksek AUC 0.73 (n=7474); Gelgit (likidite değişimi): düşük AUC 0.69 (n=5966), orta AUC 0.71 (n=6229), yüksek AUC 0.74 (n=6201)

## D. Gerçek örnek (aylık, 154 hisse): ortalama korelasyon

12 aylık pencere (aylık getiriler); likidite verisi yok (NFCI repoda yok) → **Gelgit için gerçek test yapılamadı**.

| Ay | Ort. korelasyon (12a) | SPY dd |
|---|---|---|
| 2022-10 | 0.39 | -18.7% |
| 2023-01 | 0.46 | -10.0% |
| 2023-04 | 0.46 | 0.0% |
| 2023-07 | 0.36 | 0.0% |
| 2023-10 | 0.35 | -8.6% |
| 2024-01 | 0.33 | 0.0% |
| 2024-04 | 0.35 | -4.0% |
| 2024-07 | 0.33 | 0.0% |
| 2024-10 | 0.21 | -0.9% |
| 2025-01 | 0.16 | -0.1% |
| 2025-04 | 0.15 | -8.0% |
| 2025-07 | 0.20 | 0.0% |
| 2025-10 | 0.19 | 0.0% |
| 2026-01 | 0.15 | 0.0% |
| 2026-04 | 0.12 | 0.0% |
| 2026-07 | 0.10 | -1.2% |
| 2026-10 | 0.11 | -0.1% |

- **Seküler düşüş:** ilk 6 ayda (2022-10…) ortalama 0.44, son 12 ayda 0.12. Hisseler zamanla birbirinden ayrışmış (ya da küratörlü liste çeşitlenmiş); tek yönlü bir trend var.
- 2025-04 (tarife düşüşü dibi): 0.15; 2025 Ocak–Temmuz ortalaması 0.18. 12 aylık pencerede **stres anında belirgin bir kenetlenme sıçraması görünmüyor**.
- dd ≤ −%5 aylarda ortalama 0.33 (n=10) vs zirveye yakın aylarda 0.24 (n=38): fark var gibi ama düşüş aylarının çoğu korelasyonun yüksek olduğu 2022–23'e denk geliyor → trendle **karışık**, stresin etkisi olarak okunamaz.
- Aylık veriyle 12 aylık pencere, kısa stres olaylarını (1–3 ay) ayıramaz. Kenetlenme ölçümü için günlük veri gerekir (ILERIDE-GERCEK-VERI.md).

## Okuma — hangi koşulda ne işe yarıyor?

1. **Koşullar büyük ölçüde stres vekili.** Y2 olaylarının %79'ı yüksek-kenetlenme, %60'ı yüksek-likidite-sıkılaşması terçilinde. Yay sinyali zaten stres anında çıkıyor; düşük terçil hücreleri küçük (n≈40–100) ve güven aralıkları geniş.
2. **Yay × Kenetlenme:** yüksek − düşük fark -1.1% [-4.5%, 2.2%]; kontrol (ortak faktör stresle artmıyor): -1.5% [-5.2%, 1.9%]. Sıfırdan ayırt edilemiyor: kenetlenme, yay getirisini stresin ötesinde ayrıca değiştirmiyor.
3. **Yay × Gelgit:** yüksek − düşük fark 2.5% [-0.2%, 5.0%]; gelgit mekanizması kapalıyken 1.9% [-0.7%, 4.6%]. İkisi de benzer: simülatöre koyduğumuz 'likidite gevşerken yay daha hızlı toparlar' etkisi (±%40 yarılanma) bu örneklemle **ayırt edilemiyor**; gözlenen fark, sıkılaşma anının daha derin stres olması (daha büyük sıçrama) nedeniyle olabilir.
4. **Hisse yayı ⟷ Gizli güç × koşul:** krize özgü D1 − D5 yüksek-kenetlenmede 1.1% [0.5%, 1.8%], düşükte -0.5% [-1.3%, 0.9%]. Yani 'en çok düşen ekstra toparlanır' etkisi yalnızca yüksek stres/kenetlenme koşullarında görünüyor; düşük kenetlenmede sıfıra yakın (örnek küçük).
5. **Kırılma noktası × koşul:** *panikten normale* geçiş AUC'u kenetlenme arttıkça artıyor (bölüm C); yükselişten düşüşe geçişte belirgin örüntü yok. Panik bitişi, yüksek-kenetlenme (panik) durumunda daha tahmin edilebilir.
6. **Gerçek veri:** Gelgit için hiç test yapılamadı (likidite serisi yok). Kenetlenme için aylık veri yetersiz; korelasyonun seküler düşüşü stres etkisini gizliyor.

**Genel sonuç:** Kenetlenme ve Gelgit bu aşamada *bağımsız* bir bilgi eklemiyor; stres düzeyinin göstergesi gibi davranıyorlar. Yay ve hisse yayı etkisi yüksek stres koşullarında ortaya çıkıyor. Gerçek günlük veriyle (korelasyon) ve makro seri ile (NFCI) tekrar sınanmadan ilerlemek erken.

> Bu tablolardaki yönler simülatörün yapısından (korelasyon ve likiditenin stresle birlikte hareket etmesi) beklenir; gerçek piyasada geçerliliği bu deneyle sınanmaz.

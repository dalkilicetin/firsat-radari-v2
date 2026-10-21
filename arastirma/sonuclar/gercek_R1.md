# R1 — Aylık endeks yayı (gerçek örnek, SPY + 154 hisse)

> **Küçük örneklem:** 61 aylık / ~100 günlük veri, tek tek vakalar. Sonuçlar vaka çalışmasıdır, istatistiksel kanıt değildir. Hisse seti küratörlü (teknoloji ağırlıklı) ve **hayatta kalan** şirketlerden oluşur; batan şirketler yok.

## 1. Önceden kayıtlı aylık dedektör ne gösterdi?

Parametreler `hipotezler/yay.yaml → aylik` (değiştirilmedi): `dd ≤ -10%` ve bileşik gerilim yüzdeliği ≥ 0.8.

- Y1 tetiklenen ay sayısı: **0**, Y2: **0**.
- Gerilim skoru hesaplanabilen ilk ay: **2023-06** (genişlik 10 aylık ortalama + yüzdelik ısınması 12 ay).
- Bu yüzden **2022 düşüşü dedektör için görünmez** (skor NaN), 2025 (SPY −%8) ve 2026-03 (−%6) ise `dd ≤ −%10` eşiğine ulaşmadı.
- Sonuç: 61 aylık veri bu dedektörü sınamaya **yetmiyor**; bu bir dedektör başarısı ya da başarısızlığı değil, veri uzunluğu sınırı.

## 2. Betimsel: gerilim skoru (dd eşiği olmadan) en yüksek aylar

> Post-hoc betimleme, test değil. Skor = dd, genişlik yüzdeliklerinin ortalaması.

| Ay | SPY dd | Gerilim skoru | İleri 3 ay | İleri 6 ay | İleri 12 ay |
|---|---|---|---|---|---|
| 2023-10 | -8.6% | 0.69 | 11.3% | 15.5% | 32.0% |
| 2024-12 | -2.7% | 0.65 | -7.9% | 5.0% | 15.0% |
| 2025-03 | -7.2% | 0.80 | 14.0% | 23.0% | 29.6% |
| 2025-04 | -8.0% | 0.82 | 9.4% | 15.9% | 28.3% |
| 2025-05 | -2.2% | 0.64 | 7.8% | 10.4% | 20.9% |
| 2026-03 | -6.0% | 0.69 | 3.9% | 6.7% | – |

## 3. Üç düşüş bölümü: SPY ve ETF'ler (giriş = sonraki ay sonu)

Başlangıç ayları sabit kurallarla (sonuca bakmadan) seçildi: ilk −%10 / ilk −%20 / ilk −%5 ay. 'Dip' sütunları **sonradan bilinen** dibi gösterir (üst sınır, hile).

| Bölüm | Ay | Etiket | SPY dd | SPY 3a | SPY 6a | SPY 12a |
|---|---|---|---|---|---|---|
| 2022 | 2022-04 | ilk −%10 | -13.3% | -4.3% | -1.3% | 1.2% |
| 2022 | 2022-06 | ilk −%20 | -20.6% | -6.3% | -1.3% | 11.1% |
| 2022 | 2022-09 | DİP (sonradan) | -24.8% | 5.2% | 7.7% | 8.3% |
| 2025 | 2025-03 | ilk −%5 | -7.2% | 14.0% | 23.0% | 29.6% |
| 2025 | 2025-04 | DİP (sonradan) | -8.0% | 9.4% | 15.9% | 28.3% |
| 2026 | 2026-03 | DİP (sonradan) | -6.0% | 3.9% | 6.7% | – |

### ETF'ler: 2022 bölümü, ilk −%20 ayından (2022-06) sonraki getiri

| ETF | 2021-12→2022-06 | İleri 3a | İleri 6a | İleri 12a |
|---|---|---|---|---|
| ARKG | -48.6% | -7.8% | -7.9% | 3.8% |
| BOTZ | -43.5% | -12.9% | 5.7% | 29.4% |
| SMH | -34.0% | -20.2% | -0.0% | 35.5% |
| XBI | -33.7% | 1.3% | 9.6% | 3.9% |
| IGV | -32.2% | -9.4% | -4.5% | 23.4% |
| QTUM | -27.3% | -16.0% | -1.3% | 19.6% |
| REMX | -22.6% | -7.6% | 3.0% | -11.7% |
| VGK | -22.6% | -9.8% | 9.5% | 14.5% |
| JETS | -21.8% | 0.2% | 14.1% | 20.8% |
| EWJ | -21.1% | -11.0% | 4.5% | 12.9% |
| PAVE | -20.9% | -1.5% | 10.1% | 23.2% |
| SPY | -20.6% | -6.3% | -1.3% | 11.1% |
| XLF | -19.5% | 0.8% | 8.5% | 4.8% |
| URA | -18.7% | -6.4% | 6.7% | 5.2% |
| CPER | -18.3% | -6.2% | 18.2% | 14.4% |
| EEM | -17.9% | -14.4% | 3.5% | 5.0% |
| LIT | -14.0% | -10.2% | -4.9% | -10.4% |
| SLV | -13.3% | -5.8% | 16.7% | 21.3% |
| MCHI | -11.1% | -28.4% | 7.8% | 0.2% |
| KWEB | -10.2% | -32.3% | 19.5% | 12.7% |
| ICLN | -10.0% | -15.3% | -7.0% | -18.0% |
| PPLT | -7.6% | 3.5% | 12.9% | 5.9% |
| ITA | -3.5% | 3.3% | 10.5% | 13.4% |
| XAU/USD | -1.2% | -7.5% | 9.2% | 11.3% |
| PALL | 1.4% | -12.8% | -22.2% | -39.9% |
| XLE | 28.8% | 14.8% | 14.7% | 11.6% |

## Okuma
- SPY, 2022'de ilk −%20 ayından (2022-06) sonra 3 ayda -6.3%, 6 ayda -1.3%, 12 ayda 11.1%: toparlanma hemen değil, ancak 12. ayda belirgin. Dipten (2022-09) alan ise 3 ayda 5.2% görürdü; **dibi önceden bilmek** büyük fark yaratır (üst sınır).
- ETF düzeyi (2021-12→2022-06 düşüşü ile ileri getiri arasında sıra korelasyonu, n=26): 3a ρ=+0.17, 6a ρ=+0.29, 12a ρ=-0.36. ρ<0 = en çok düşenler daha çok toparlandı (yay), ρ>0 = en az düşenler daha iyi (gizli güç). En çok düşenler: ARKG, BOTZ, SMH; en az düşenler/yükselenler: XAU/USD, PALL, XLE.
- Bu tek bir vaka, 26 ETF; sonuç kanıt değil. Hisse düzeyindeki karşılığı R2'dedir.

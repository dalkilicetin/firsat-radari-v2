# Yapay zekâ modelleri: A (getiri), B (büyük kazanan), C (risk) — yürüyen test

Her yıl, yalnızca o yıldan önce sonucu bilinen satırlarla eğitilmiş model o yılı tahmin eder (sabit ayar, ayar yok). Her hafta 10 hisse (sektör başına en fazla 3), alış cuma kapanışı, masraflar düşülmüş, 3 ay. Skorlar yüzdelik sıradır; **olasılık değildir**.

## 2016–2022 (geliştirme)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 366 | +%2.1 | +%0.6 | +%1.0 (+%0.1 … +%1.9) | %55 | %13.7 | %13.9 | 0.73 (0.66) |
| Model A (getiri sırası) | 366 | +%1.5 | +%0.5 | +%0.5 (−%0.2 … +%1.1) | %54 | %13.1 | %16.2 | 0.26 (0.66) |
| Model B (büyük kazanan) | 366 | +%2.3 | +%0.0 | +%1.3 (+%0.2 … +%2.3) | %51 | %18.3 | %22.4 | 0.45 (0.66) |
| Basit momentum (26 hafta) | 366 | +%1.5 | −%0.6 | +%0.4 (−%1.3 … +%2.5) | %49 | %16.6 | %20.9 | 0.45 (0.66) |
| Rastgele 10 | 366 | +%0.5 | +%0.3 | −%0.6 (−%1.0 … −%0.2) | %43 | %4.5 | %7.7 | 0.13 (0.66) |
| Model A, düşük riskli yarı | 366 | +%1.6 | +%1.3 | +%0.5 (+%0.1 … +%1.1) | %51 | %3.5 | %5.1 | 0.93 (0.66) |

## 2023–2026 (ikinci bakış)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 197 | +%3.3 | +%0.9 | +%1.8 (+%1.7 … +%2.0) | %57 | %15.9 | %15.5 | 1.56 (1.66) |
| Model A (getiri sırası) | 197 | +%1.1 | +%0.4 | −%0.4 (−%1.5 … +%0.7) | %41 | %8.6 | %13.2 | 0.33 (1.66) |
| Model B (büyük kazanan) | 197 | +%1.8 | −%1.5 | +%0.3 (−%0.7 … +%1.2) | %51 | %19.2 | %27.5 | 0.42 (1.66) |
| Basit momentum (26 hafta) | 197 | +%1.0 | −%1.8 | −%0.5 (−%1.1 … +%0.2) | %43 | %16.0 | %25.3 | 0.42 (1.66) |
| Rastgele 10 | 197 | +%0.4 | −%0.2 | −%1.1 (−%1.5 … −%0.7) | %40 | %5.3 | %9.1 | 0.35 (1.66) |
| Model A, düşük riskli yarı | 197 | +%1.0 | +%0.6 | −%0.6 (−%1.0 … +%0.0) | %43 | %2.5 | %3.4 | 0.75 (1.66) |

## Risk skoru kovaları (2016–2022)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %1.9 | 114,092 |
| 2 | %3.8 | 114,287 |
| 3 | %6.5 | 114,312 |
| 4 | %10.3 | 114,287 |
| 5 | %16.4 | 114,533 |

## Risk skoru kovaları (2023–2026)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %1.3 | 66,443 |
| 2 | %3.7 | 66,568 |
| 3 | %6.5 | 66,551 |
| 4 | %10.5 | 66,568 |
| 5 | %18.9 | 66,675 |

Skorlar yüzdelik sıradır, olasılık değil. 2013–2015 yalnızca eğitimde. 2023–2026 bir kez hatalı veriyle açılmıştı; temiz sınav canlı kayıttır.

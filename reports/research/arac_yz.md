# Yapay zekâ modelleri: A (getiri), B (büyük kazanan), C (risk) — yürüyen test

Her yıl, yalnızca o yıldan önce sonucu bilinen satırlarla eğitilmiş model o yılı tahmin eder (sabit ayar, ayar yok). Her hafta 10 hisse (sektör başına en fazla 3), alış cuma kapanışı, masraflar düşülmüş, 3 ay. Skorlar yüzdelik sıradır; **olasılık değildir**.

## 2016–2022 (geliştirme)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 366 | +%7.3 | +%3.2 | +%4.0 (+%0.5 … +%7.9) | %61 | %14.2 | %16.4 | 0.86 (0.75) |
| Model A (getiri sırası) | 366 | +%3.2 | +%0.8 | −%0.1 (−%3.1 … +%2.7) | %51 | %9.1 | %18.4 | 0.35 (0.75) |
| Model B (büyük kazanan) | 366 | +%4.0 | +%0.1 | +%0.7 (−%5.5 … +%7.3) | %49 | %15.0 | %26.9 | 0.21 (0.75) |
| Basit momentum (26 hafta) | 366 | +%4.9 | −%1.3 | +%1.6 (−%3.8 … +%7.3) | %51 | %15.4 | %25.9 | 0.27 (0.75) |
| Rastgele 10 | 366 | +%3.0 | +%2.2 | −%0.3 (−%2.1 … +%1.6) | %47 | %5.1 | %10.8 | 0.20 (0.75) |
| Model A, düşük riskli yarı | 366 | +%2.9 | +%2.4 | −%0.4 (−%2.3 … +%1.5) | %46 | %4.0 | %10.1 | 0.54 (0.75) |

## 2023–2026 (ikinci bakış)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 188 | +%9.1 | +%2.9 | +%4.0 (+%3.5 … +%4.4) | %53 | %16.4 | %20.1 | 1.10 (1.25) |
| Model A (getiri sırası) | 188 | +%5.3 | +%1.3 | +%0.2 (−%1.0 … +%1.2) | %46 | %9.5 | %15.9 | 0.88 (1.25) |
| Model B (büyük kazanan) | 188 | +%11.0 | +%1.3 | +%5.8 (−%0.6 … +%11.0) | %56 | %19.3 | %31.7 | 0.81 (1.25) |
| Basit momentum (26 hafta) | 188 | +%5.7 | −%2.5 | +%0.6 (−%3.0 … +%4.9) | %40 | %15.2 | %33.2 | 0.20 (1.25) |
| Rastgele 10 | 188 | +%3.1 | +%1.6 | −%2.0 (−%3.8 … +%0.2) | %35 | %4.3 | %12.9 | 0.67 (1.25) |
| Model A, düşük riskli yarı | 188 | +%3.6 | +%2.1 | −%1.5 (−%3.6 … +%0.3) | %39 | %2.7 | %6.5 | 0.73 (1.25) |

## Risk skoru kovaları (2016–2022)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %3.3 | 114,054 |
| 2 | %6.6 | 114,263 |
| 3 | %10.4 | 114,270 |
| 4 | %15.2 | 114,263 |
| 5 | %23.4 | 114,488 |

## Risk skoru kovaları (2023–2026)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %2.7 | 63,142 |
| 2 | %6.7 | 63,253 |
| 3 | %10.7 | 63,254 |
| 4 | %17.2 | 63,253 |
| 5 | %25.4 | 63,362 |

Skorlar yüzdelik sıradır, olasılık değil. 2013–2015 yalnızca eğitimde. 2023–2026 bir kez hatalı veriyle açılmıştı; temiz sınav canlı kayıttır.

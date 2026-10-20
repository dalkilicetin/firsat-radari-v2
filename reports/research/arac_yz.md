# Yapay zekâ modelleri: A (getiri), B (büyük kazanan), C (risk) — yürüyen test

Her yıl, yalnızca o yıldan önce sonucu bilinen satırlarla eğitilmiş model o yılı tahmin eder (sabit ayar, ayar yok). Her hafta 10 hisse (sektör başına en fazla 3), alış cuma kapanışı, masraflar düşülmüş, 3 ay. Skorlar yüzdelik sıradır; **olasılık değildir**.

## 2016–2022 (geliştirme)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 366 | +%7.3 | +%3.1 | +%4.0 (+%0.5 … +%7.9) | %61 | %14.1 | %16.4 | 0.86 (0.75) |
| Model A (getiri sırası) | 366 | +%4.3 | +%1.7 | +%1.0 (−%3.1 … +%5.4) | %55 | %11.7 | %19.9 | 0.23 (0.75) |
| Model B (büyük kazanan) | 366 | +%4.3 | +%0.7 | +%1.0 (−%3.9 … +%5.6) | %51 | %16.0 | %25.6 | 0.06 (0.75) |
| Basit momentum (26 hafta) | 366 | +%4.9 | −%1.3 | +%1.6 (−%3.8 … +%7.3) | %51 | %15.4 | %25.9 | 0.27 (0.75) |
| Rastgele 10 | 366 | +%3.2 | +%2.7 | −%0.1 (−%1.9 … +%1.9) | %46 | %5.0 | %11.2 | 0.43 (0.75) |
| Model A, düşük riskli yarı | 366 | +%2.2 | +%1.4 | −%1.1 (−%3.2 … +%1.3) | %42 | %3.7 | %10.7 | 0.37 (0.75) |

## 2023–2026 (ikinci bakış)

| Liste | Hafta | Ortalama | Ortadaki | Borsaya göre fazla (%90 aralık) | Borsayı yendiği hafta | İlk %5'ten oran | −%20'den fazla kaybeden | Sharpe (borsa) |
|---|---|---|---|---|---|---|---|---|
| Kural radarı (mevcut) | 184 | +%9.6 | +%3.2 | +%4.4 (+%3.8 … +%5.2) | %54 | %16.8 | %19.7 | 1.10 (1.25) |
| Model A (getiri sırası) | 184 | +%6.4 | +%2.6 | +%1.2 (−%0.6 … +%3.0) | %47 | %8.4 | %13.4 | 1.12 (1.25) |
| Model B (büyük kazanan) | 184 | +%9.8 | −%0.1 | +%4.6 (−%1.7 … +%10.0) | %52 | %18.6 | %30.5 | 0.52 (1.25) |
| Basit momentum (26 hafta) | 184 | +%6.2 | −%2.2 | +%1.0 (−%3.0 … +%5.6) | %41 | %15.5 | %33.0 | 0.20 (1.25) |
| Rastgele 10 | 184 | +%4.4 | +%2.4 | −%0.7 (−%2.6 … +%1.6) | %42 | %5.8 | %10.7 | 1.01 (1.25) |
| Model A, düşük riskli yarı | 184 | +%4.3 | +%3.1 | −%0.9 (−%2.1 … +%0.5) | %47 | %2.2 | %5.5 | 0.92 (1.25) |

## Risk skoru kovaları (2016–2022)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %3.4 | 114,072 |
| 2 | %6.5 | 114,279 |
| 3 | %10.2 | 114,288 |
| 4 | %15.3 | 114,279 |
| 5 | %23.3 | 114,502 |

## Risk skoru kovaları (2023–2026)

Haftanın evreni risk skoruna göre 5 eşit kovaya bölünür (1 = en düşük risk). Değer: 3 ayda −%20'den fazla kaybeden hisse oranı.

| Kova | Büyük kayıp oranı | Satır |
|---|---|---|
| 1 | %2.7 | 61,683 |
| 2 | %6.5 | 61,791 |
| 3 | %10.9 | 61,795 |
| 4 | %16.5 | 61,791 |
| 5 | %25.0 | 61,900 |

Skorlar yüzdelik sıradır, olasılık değil. 2013–2015 yalnızca eğitimde. 2023–2026 bir kez hatalı veriyle açılmıştı; temiz sınav canlı kayıttır.

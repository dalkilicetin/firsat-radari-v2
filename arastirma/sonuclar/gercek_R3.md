# R3 — Günlük panel: şok yayı (tek gün ≤ −%8)

> **Küçük örneklem:** 61 aylık / ~100 günlük veri, tek tek vakalar. Sonuçlar vaka çalışmasıdır, istatistiksel kanıt değildir. Hisse seti küratörlü (teknoloji ağırlıklı) ve **hayatta kalan** şirketlerden oluşur; batan şirketler yok.

Panel: 2026-07-06 → 2026-10-20, hafta sonu tekrarları atılınca **75 işlem günü**.

## Veri kalitesi: panel uygun bir günlük fiyat paneli değil
- Fiyat (`quotes`) yalnızca bir alt küme için kayıtlı: kapsam Temmuz'da ~419, Ağustos–Eylül'de ~241, **yalnızca son haftada** 589 hisse. Kapsam zamanla ve büyük olasılıkla önceki sıralamaya göre değişiyor (seçim yanlılığı).
- `mtd` alanı fiyat değişimleriyle tutarsız (aynı gün fiyat −%1.1 iken mtd +%1.1 artıyor), yedek olarak kullanılamaz.
- Bu yüzden **sabit hisse seti** kullanıldı: gün sayısının ≥%95'inde fiyatı olan **105 hisse**. Bu set de tarama listelerinden geldiği için temsil gücü sınırlı.
- Gerçek zaman damgası tarama commit gününe aittir; fiyat önceki seans kapanışıdır (1 günlük ofset, sonucu etkilemez).

Şok = günlük getiri ≤ −%8 ve ≥ −%50 (bölünme filtresi). Getiri = ertesi gün girişli, **SPY'a göre fazla getiri**. Aynı gündeki olaylar ortalanıp **gün bazında** özetlenir (aynı gün şokları bağımsız değil).

Toplam şok: **88** hisse-günü, **30** farklı gün.

| Grup | Ufuk | Gün | Hisse-gün | Şok sonrası fazla getiri (gün ortalaması) [%90 GA] | Tüm hisse-gün tabanı | **Şok − taban** |
|---|---|---|---|---|---|---|
| Tüm şoklar (ana sonuç) | 5g | 27 | 75 | 2.2% [-0.1%, 6.5%] | -0.1% | **2.4%** |
| Tüm şoklar (ana sonuç) | 10g | 26 | 74 | 0.9% [-1.0%, 5.0%] | -0.3% | **1.2%** |
| Tüm şoklar (ana sonuç) | 20g | 24 | 71 | 3.4% [-1.6%, 9.3%] | -0.8% | **4.2%** |
| Trendde (r52w > 0) | 5g | 23 | 67 | 2.6% [-0.6%, 7.1%] | -0.1% | **2.7%** |
| Trendde (r52w > 0) | 10g | 22 | 66 | 1.0% [-0.9%, 6.0%] | -0.3% | **1.3%** |
| Trendde (r52w > 0) | 20g | 20 | 63 | 5.2% [-0.4%, 12.7%] | -0.8% | **6.1%** |
| Trend dışı (r52w ≤ 0) | 5g | 7 | 8 | 0.3% [-2.9%, 2.2%] | -0.1% | **0.4%** |
| Trend dışı (r52w ≤ 0) | 10g | 7 | 8 | 1.5% [-4.8%, 7.5%] | -0.3% | **1.8%** |
| Trend dışı (r52w ≤ 0) | 20g | 7 | 8 | -3.2% [-9.3%, -0.7%] | -0.8% | **-2.4%** |
| Duyarlılık: ertesi gün +%6 sıçrayan şüpheli olaylar çıkarıldı (gelecekten bilgi!) | 5g | 27 | 66 | 2.9% [0.2%, 7.6%] | -0.1% | **3.0%** |
| Duyarlılık: ertesi gün +%6 sıçrayan şüpheli olaylar çıkarıldı (gelecekten bilgi!) | 10g | 26 | 65 | 1.2% [-0.9%, 6.0%] | -0.3% | **1.5%** |
| Duyarlılık: ertesi gün +%6 sıçrayan şüpheli olaylar çıkarıldı (gelecekten bilgi!) | 20g | 24 | 63 | 4.2% [-0.5%, 10.1%] | -0.8% | **5.0%** |

## Ekim 2026 ortası satışı (betimsel; ileri 5 gün henüz yok)

- 2026-10-15: SPY -1.1%, sabit sette şok 9 hisse; ertesi gün ortalaması 0.4%.
- 2026-10-17: SPY -1.1%, sabit sette şok 3 hisse; ertesi gün ortalaması 1.6%.

## Okuma
- Ana sonuç: şok sonrası 5 günde SPY'a göre fazla getiri **2.2%** [-0.1%, 6.5%] (n=27 gün); tabanla fark 2.4%. Güven aralığı sıfırı içeriyor ve v5.16'daki +%5'i de içeriyor: bu veri v5.16 bulgusunu ne doğrular ne çürütür. Gün sayısı az, olaylar kümelenmiş.
- Şüpheli-olaylar duyarlılık satırı gelecekten bilgi kullanır; yalnızca ana sonucun veri hatalarına ne kadar duyarlı olduğunu göstermek içindir.
- Panel yapısı (değişen kapsam) nedeniyle bu test ancak yeni gece taramaları tam kapsamlı (589 hisse) birikince (≈ 4–6 hafta) güvenilir olur; o zaman `python calistir.py gercek R3` yeniden çalıştırılmalı.

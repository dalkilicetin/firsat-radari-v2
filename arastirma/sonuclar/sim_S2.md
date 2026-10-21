# S2 — Boşalma işaretleri ve ek acı (MAE)

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

20 dünya × 60 yıl, kalibre ayar. Her satır, ayıklanmış olayların (63 bar bekleme) **63 bar ileri getirisi** ve girişten sonraki **en kötü ek düşüş (MAE)**.
Koşulsuz (her gün girilseydi): ortalama 63g getiri 2.3%, ortalama MAE -6.5%.

| Sinyal | n olay | 63g ort. getiri [%90 GA] | koşulsuza fark | isabet | MAE ort. | MAE < −%5 | MAE < −%10 |
|---|---|---|---|---|---|---|---|
| Y1 (sadece gerilim) | 535 | 1.2% [0.1, 2.3] (n=535) | -1.1% | 56% | -10.2% | 63% | 41% |
| Y2 (gerilim + herhangi bosalma) | 530 | 3.2% [2.1, 4.5] (n=530) | 1.0% | 60% | -8.7% | 55% | 33% |
| Y2: sadece VIX düşüşü | 318 | 3.6% [2.2, 4.8] (n=318) | 1.3% | 64% | -8.0% | 51% | 27% |
| Y2: sadece genişlik itkisi | 433 | 3.4% [2.1, 4.8] (n=433) | 1.1% | 61% | -8.9% | 55% | 33% |
| Y2: sadece fiyat teyidi | 486 | 3.8% [2.7, 5.0] (n=486) | 1.6% | 63% | -8.4% | 55% | 31% |
| basit: dd ≤ −%15 | 1974 | 2.1% [1.7, 2.7] (n=1974) | -0.1% | 58% | -7.8% | 52% | 27% |

## Katalog hipotezi 1: 'hızlı düşüş → hızlı toparlanma' hıza mı süreye mi bağlı?

Y1 olaylarında (n=479, toparlanması bilinenler). Spearman, **derinlik (dd) sabitlenerek**; toparlanma = girişten eski 252 bar zirvesine dönüş.

| Grup | n | ρ(hız, toparlanma \| dd) | ρ(düşüş süresi, toparlanma \| dd) |
|---|---|---|---|
| hepsi | 479 | -0.00 | 0.02 |
| gerçek panik | 114 | -0.02 | 0.03 |
| gerçek bozulma | 365 | -0.04 | -0.05 |

**Sonuç:** simülatörün yayı hız–toparlanma ilişkisi **üretmiyor** (ρ≈0); katalogdaki ilişki bu mekanizmayla açıklanmıyor, şans (n=13, çok sütun denendi) veya başka bir mekanizma olabilir.

Katalogda (n=13, derinlik sabit): ρ(hız, toparlanma) = +0.60. Bu bir *hız* etkisi mi yoksa düşüşün **süresi**nin toparlanma süresini belirlemesi mi — burada ayrıştırılır.

## Okuma
- 'MAE < −%5' sütunu, 'toparlanmadan hemen önceki bölge' sorusunun cevabıdır: sinyalden sonra ne kadar daha acı çekilir?
- Y2, Y1'e göre MAE'yi azaltıyor ve getiriyi koruyorsa boşalma işaretleri değer katıyor demektir.
- 'koşulsuza fark' ≈ 0 ise sinyal, piyasanın zaten yükselmesinden başka bir şey yakalamıyordur (bkz. S3).

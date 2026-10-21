# L9 — Kırılma noktası: rejim geçişlerini önceden görebilir miyiz?

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Rejim (kural tabanlı): trend (200 bar ortalama) × oynaklık (63 bar vol'un genişleyen yüzdeliği > 0.70), yeni rejim 10 bar sürmedikçe geçilmez. **İki görev:** (a) *panikten normale*: `oynak_düşüş` rejimindeyken sonraki 21/63 barda yükseliş rejimine geçiş; (b) *yükselişten düşüşe*: yükseliş rejimindeyken sonraki 21/63 barda düşüş rejimine geçiş.
Model: ridge lojistik regresyon (8 öncü değişken, standartlaştırılmış). **Eğitim: tohum 0–9, test: tohum 10–19** (farklı dünyalar). Her 5. bar alınır (ardışık barlar bağımlı).
Metrikler: AUC (0.5 = şans), Brier (taban oranı tahmininden düşükse iyi), lift = en yüksek %10 tahminde gerçekleşme oranı / taban oranı.

## Dünya: yay + bozulma var (kalibre)

| Görev | Ufuk | n (test) | Taban oranı | AUC | Brier (taban) | Lift %10 |
|---|---|---|---|---|---|---|
| panikten_normale | 21 | 4844 | 15% | **0.85** | 0.096 (0.127) | 4.0× |
| panikten_normale | 63 | 4839 | 40% | **0.77** | 0.190 (0.240) | 2.0× |
| yukselisten_dususe | 21 | 18430 | 11% | **0.85** | 0.082 (0.097) | 4.1× |
| yukselisten_dususe | 63 | 18396 | 28% | **0.72** | 0.179 (0.204) | 2.2× |

**Ablation (AUC):** tam model / sadece `dd` / `dd` olmadan diğer 7 öncü

| Görev | Ufuk | Tam | Sadece dd | dd olmadan | Öncülerin ek katkısı (tam − sadece dd) |
|---|---|---|---|---|---|
| panikten_normale | 21 | 0.85 | 0.82 | 0.68 | +0.03 |
| panikten_normale | 63 | 0.77 | 0.74 | 0.69 | +0.03 |
| yukselisten_dususe | 21 | 0.85 | 0.84 | 0.62 | +0.00 |
| yukselisten_dususe | 63 | 0.72 | 0.72 | 0.57 | -0.00 |

## Dünya: olay yok (negatif kontrol)

| Görev | Ufuk | n (test) | Taban oranı | AUC | Brier (taban) | Lift %10 |
|---|---|---|---|---|---|---|
| panikten_normale | 21 | 2645 | 20% | **0.81** | 0.122 (0.158) | 3.5× |
| panikten_normale | 63 | 2630 | 48% | **0.71** | 0.215 (0.250) | 1.8× |
| yukselisten_dususe | 21 | 20229 | 9% | **0.86** | 0.068 (0.081) | 4.5× |
| yukselisten_dususe | 63 | 20183 | 24% | **0.75** | 0.157 (0.181) | 2.4× |

**Ablation (AUC):** tam model / sadece `dd` / `dd` olmadan diğer 7 öncü

| Görev | Ufuk | Tam | Sadece dd | dd olmadan | Öncülerin ek katkısı (tam − sadece dd) |
|---|---|---|---|---|---|
| panikten_normale | 21 | 0.81 | 0.80 | 0.59 | +0.01 |
| panikten_normale | 63 | 0.71 | 0.72 | 0.55 | -0.01 |
| yukselisten_dususe | 21 | 0.86 | 0.86 | 0.55 | +0.00 |
| yukselisten_dususe | 63 | 0.75 | 0.75 | 0.50 | +0.00 |

## Hangi öncü değişken işe yarıyor? (kalibre dünya, tek değişkenli AUC ≥ 0.5 yönüne çevrilmiş, ufuk 63)

| Değişken | panikten_normale | yukselisten_dususe | katsayı işareti kararlılığı (panikten normale) |
|---|---|---|---|
| genislik_ayrisma | 0.51 | 0.52 | 60% |
| vix_degisim_21 | 0.56 | 0.55 | 70% |
| vix_vol_21 | 0.53 | 0.55 | 90% |
| kredi_egim_60 | 0.66 | 0.55 | 70% |
| ort_kor_63 | 0.63 | 0.50 | 60% |
| kor_degisim_21 | 0.55 | 0.54 | 90% |
| momentum_farki | 0.60 | 0.51 | 80% |
| dd | 0.74 | 0.72 | 100% |

(Tek değişkenli AUC bilerek yön-bağımsız: 0.5 = bilgi yok. Kararlılık: 10 eğitim dünyasının ayrı ayrı fit'inde katsayı işareti toplu fit ile aynı olan dünya oranı.)

## Gerçek örnek: aylık SPY rejimi (2022–2026, betimsel)

Aylık parametreler (`kirilma.yaml → aylik`): vol 6 ay, trend 10 ay ortalaması, min süre 2 ay. VIX, kredi ve hisse genişliği öncüleri aylık örnekte yok/ısınma yetersiz; sadece rejim yolu gösterilir. **Test değil.**

| Ay | Rejim | SPY |
|---|---|---|
| 2022-12 | oynak_dusus | 382 |
| 2023-01 | oynak_dusus | 406 |
| 2023-02 | oynak_yukselis | 396 |
| 2023-03 | oynak_yukselis | 409 |
| 2023-04 | sakin_yukselis | 416 |
| 2023-05 | sakin_yukselis | 418 |
| 2023-06 | sakin_yukselis | 443 |
| 2023-07 | sakin_yukselis | 458 |
| 2023-08 | sakin_yukselis | 450 |
| 2023-09 | sakin_yukselis | 427 |
| 2023-10 | sakin_yukselis | 418 |
| 2023-11 | sakin_yukselis | 456 |
| 2023-12 | sakin_yukselis | 475 |
| 2024-01 | sakin_yukselis | 483 |
| 2024-02 | sakin_yukselis | 508 |
| 2024-03 | sakin_yukselis | 523 |
| 2024-04 | sakin_yukselis | 502 |
| 2024-05 | sakin_yukselis | 527 |
| 2024-06 | sakin_yukselis | 544 |
| 2024-07 | sakin_yukselis | 551 |
| 2024-08 | sakin_yukselis | 564 |
| 2024-09 | sakin_yukselis | 574 |
| 2024-10 | sakin_yukselis | 569 |
| 2024-11 | sakin_yukselis | 603 |
| 2024-12 | sakin_yukselis | 586 |
| 2025-01 | sakin_yukselis | 602 |
| 2025-02 | sakin_yukselis | 594 |
| 2025-03 | sakin_yukselis | 559 |
| 2025-04 | sakin_dusus | 555 |
| 2025-05 | sakin_dusus | 589 |
| 2025-06 | sakin_yukselis | 618 |
| 2025-07 | sakin_yukselis | 632 |
| 2025-08 | sakin_yukselis | 645 |
| 2025-09 | sakin_yukselis | 666 |
| 2025-10 | sakin_yukselis | 682 |
| 2025-11 | sakin_yukselis | 683 |
| 2025-12 | sakin_yukselis | 682 |
| 2026-01 | sakin_yukselis | 692 |
| 2026-02 | sakin_yukselis | 686 |
| 2026-03 | sakin_yukselis | 650 |
| 2026-04 | sakin_yukselis | 719 |
| 2026-05 | oynak_yukselis | 756 |
| 2026-06 | oynak_yukselis | 747 |
| 2026-07 | oynak_yukselis | 747 |
| 2026-08 | oynak_yukselis | 767 |
| 2026-09 | oynak_yukselis | 763 |
| 2026-10 | sakin_yukselis | 766 |

Geçişler: 2023-02: oynak_dusus→oynak_yukselis; 2023-04: oynak_yukselis→sakin_yukselis; 2025-04: sakin_yukselis→sakin_dusus; 2025-06: sakin_dusus→sakin_yukselis; 2026-05: sakin_yukselis→oynak_yukselis; 2026-10: oynak_yukselis→sakin_yukselis
**Gecikme notu:** 2025'te 'düşüş' rejimi ancak SPY'ın dip ayında (2025-04, −%8) ilan edildi ve 2 ay sonra yükselişe döndü; kural krizi *geç* etiketliyor. 2022'nin düşüşü ise rejimin ısınma süresine (vol yüzdeliği + 10 ay ortalaması) denk geldiği için aylık yolda hiç görünmüyor.

## Okuma
- **Negatif kontrol başarısız:** olay olmayan dünyada bile AUC yüksek (0.71 / 0.75, ufuk 63) — kalibre dünyadakiyle (0.77 / 0.72) neredeyse aynı. Yani yüksek AUC, öncü değişkenlerin geçişi *önceden gördüğünü* göstermiyor; rejim tanımı (fiyat − 200 bar ortalama, oynaklık yüzdeliği) ile `dd` arasındaki **mekanik ilişkiyi** ölçüyor.
- `dd` tek başına AUC 0.74 / 0.72; tam model 0.77 / 0.72. Diğer 7 öncünün (genişlik ayrışması, VIX, kredi, korelasyon, momentum) **ek katkısı** +0.03 / -0.00: küçük.
- `dd` olmadan 7 öncü: kalibre dünyada AUC 0.69 / 0.57, olaysız dünyada 0.55 / 0.50. Aradaki fark (**+0.13 / +0.07**) mekanik `dd` etkisinden arındırılmış, *olay kaynaklı* öncü bilgidir.
  - Panikten normale: fark belirgin; en iyi tek değişkenler `kredi_egim_60` (0.66), `ort_kor_63` (0.63), `momentum_farki` (0.60). Bunlar simülatörde panikle birlikte oynayan değişkenler (kredi spread'i `m`'ye bağlı, korelasyon stresle artıyor) — yani bulgu *tasarımın sonucu*, gerçek piyasada ayrıca sınanmalı.
  - Yükselişten düşüşe: fark küçük; yükselişteki düşüş geçişlerini bu öncüllerle önceden görmek zayıf.
- Özet: yüksek AUC'nin büyük kısmı mekanik; **panik bitişi** için kredi eğimi ve korelasyon küçük ama gerçek bir artı bilgi taşıyor; **yükselişten düşüşe** geçiş için öncü bilgi yok denecek kadar az.
- Rejim kuralı histerezis nedeniyle ≥10 bar gecikmeli: 'geçişi önceden görmek' aslında *gecikmeli etiketlenen* geçişi görmek demektir.

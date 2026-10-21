# S3 — Sahte yay (negatif kontrol)

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Aynı dedektör, **yayın olmadığı** dünyalarda da çalıştırıldı. Amaç: 'dipten alma sırf piyasa uzun vadede yükseldiği için iyi görünür' tuzağını sayıyla görmek ve yanlış alarm oranını ölçmek.
20 dünya × 60 yıl. 'GA dışlıyor' = sinyal olaylarının ortalama getirisi ile koşulsuz ortalama arasındaki fark %90 güven aralığında sıfırı dışlıyor (şans eseri beklenen ≈ %10; 20 dünyada ±%7 oynar).

| Dünya | Sinyal | Koşulsuz 63g | Sinyal ort. getiri | Fark | GA sıfırı dışlayan dünya oranı | Rastgele sinyal yanlış alarm | olay/dünya |
|---|---|---|---|---|---|---|---|
| yay var (kalibre) | Y1 | 2.3% | 1.0% | -1.3% | 5% | 6% | 27 |
| yay var (kalibre) | Y2 | 2.3% | 3.2% | 1.0% | 5% | 7% | 26 |
| yay yok, bozulma var | Y1 | 2.2% | -0.8% | -2.9% | 15% | 14% | 23 |
| yay yok, bozulma var | Y2 | 2.2% | -0.9% | -3.1% | 35% | 10% | 23 |
| yay yok, bozulma yok (saf yürüyüş) | Y1 | 2.8% | 2.4% | -0.4% | 20% | 6% | 26 |
| yay yok, bozulma yok (saf yürüyüş) | Y2 | 2.8% | 2.3% | -0.5% | 20% | 9% | 26 |

## Okuma
- **Saf yürüyüşte** (yay yok, bozulma yok) sinyal − koşulsuz ≈ 0 olmalı. Sinyal ortalaması yine de pozitiftir (koşulsuz sürüklenme kadar): 'dipten al' kuralı piyasa yükseldiği için *kazanıyormuş gibi* görünür, ama yaydan değil.
- **Yay yok ama bozulma var** dünyasında sinyal sonrası getiri koşulsuzun altında kalır: dedektör düşüşü yakalar, düşüş sürer ('bıçağı tutmak'). Yay olmayan piyasada dedektör **zarar** eder.
- Rastgele sinyallerde yanlış alarm oranı ~%10 civarındaysa güven aralıkları kabaca doğru; belirgin üstündeyse sonuçlar sıkılaştırılmalı.
- 'Yay var' dünyasındaki farkı bu iki yay-yok dünyasıyla yan yana oku: **fark farkı** yayın gerçek payıdır.

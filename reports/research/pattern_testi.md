# Pattern Testi: Kazanan Profilindeki Pattern, Görmediği Aylarda

- **Kural:** `radar/research/pattern_testi.py` (sonuçlardan önce commit edildi). Küçük + ucuz + oynak hisseler; trendi kırılmış, işi bozulan, hisse basan ve devamlılık şüphesi olanlar elenir; kalanlar içeriden alım, marj iyileşmesi, sürpriz, büyüme ve trende göre puanlanır; en iyi 10 hisse, 3 ay tutulur; maliyet dahil.
- **Görmediği veri:** Pattern yalnızca Ocak/Nisan/Temmuz/Ekim başlarından çıkarıldı. Test Şubat (Şub/May/Ağu/Kas) ve Mart (Mar/Haz/Eyl/Ara) zincirlerinde yapıldı. Aynı yıllar olduğu için tam bağımsız değil.

| Zincir | Pattern (yıllık, maliyetli) | Maliyetsiz | S&P 500 | Tüm evren | Yalnızca piyango grubu | En kötü düşüş (pattern / S&P) | S&P'yi geçtiği yıl |
|---|---|---|---|---|---|---|---|
| Ocak (gördüğü) | %7,7 | %11,0 | %13,9 | %10,4 | %6,0 | −%50 / −%23 | 6 / 16 |
| Şubat (görmediği) | %5,0 | %8,3 | %15,3 | %12,5 | %4,3 | −%47 / −%18 | 5 / 17 |
| Mart (görmediği) | %13,5 | %17,0 | %15,0 | %12,2 | %6,3 | −%57 / −%13 | 6 / 17 |

| Zincir | Seçimlerin büyük kazanan olma oranı | Piyango grubunda | Seçimlerin büyük kaybeden olma oranı | Piyango grubunda |
|---|---|---|---|---|
| Ocak | %7,0 | %5,4 | %4,9 | %5,3 |
| Şubat | %6,1 | %5,8 | %5,4 | %6,4 |
| Mart | %6,3 | %5,6 | %5,3 | %6,3 |

Rastgele bir hissenin büyük kazanan (ilk 20) olma olasılığı ≈ %1.

## Sonuç
- Pattern S&P 500'ü geçmedi: üç zincirin ikisinde açık farkla geride, birinde maliyetten sonra biraz geride. Düşüşler S&P'nin 2–4 katı.
- Pattern'in "çürükleri ele" kısmı işe yarıyor: aynı piyango grubunun tamamına göre getiri yılda +1 ile +7 puan daha iyi, büyük kaybeden oranı biraz daha düşük.
- Büyük kazananı bulma oranı rastgelenin ~6 katı, ama bu neredeyse tamamen piyango grubundan geliyor (o grubun kendisi de ~5,6 kat). Seçilen hisselerin büyük kaybeden olma oranı neredeyse aynı yüksek.
- Yıllar çok dalgalı: Mart zincirinde 2020 +%253, 2014 −%35.
- Pattern'i gördüğü Ocak zincirinde bile S&P'yi geçemedi; yani bu pattern "ezber" haliyle bile yatırım kuralı olarak yetmiyor.

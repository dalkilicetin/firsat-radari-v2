# Sistematik Pattern Araması — Sonuç

- **Yöntem:** `radar/research/pattern_arama.py`. Yalnızca güvenilir veri; 1.252 kural (tek belirti ve ikili kombinasyon × iki yön × üç havuz: tümü, piyango, büyük ve likit). Her kural: en iyi 10 hisse, 3 ay tutma, maliyet dahil.
- **Görmediği veri:** Seçim Ocak zincirinde (Oca/Nis/Tem/Eki), doğrulama Şubat ve Mart zincirlerinde. Ocak'taki sonuç ile görmediği aylardaki sonuç arasındaki ilişki 0,76: kurallar aylar arasında taşınıyor. Ama zincirler aynı yılları paylaştığı için bu tam bağımsız bir test değil.
- **Kontroller:** `pattern_kontrol_esitlik.py`, `pattern_kontrol_saglamlik.py`, `pattern_kontrol_sue.py`.

## Bulgular

| Kural | Görmediği aylarda yıllık (Şubat / Mart) | S&P | Kontrol sonucu |
|---|---|---|---|
| Piyango havuzunda temettü verimi en düşük 10 | %59 / %43 | %15 / %14 | ❌ **Sahte.** Yüzlerce hisse aynı değerde (0 temettü); seçimi tablo sırası yapıyor. Eşitlik rastgele bozulunca −%17 ile +%22 arası |
| Piyango havuzunda borç/özsermaye en düşük 10 | %37 / %60 | | ❌ **Sahte**, aynı neden; rastgele bozulunca −%13 ile +%2 |
| Tüm hisselerde kâr sürprizi en kötü 10 (sue_fiyat) | %46 / %29 | | ⚠️ **Kısmen sızıntı.** Belirti düzeltilmiş fiyata bölünüyor; düzeltilmiş fiyat sonraki bölünmeleri içerir (geleceği taşır). Ham fiyatla: Ocak %24, Şubat %28, Mart %14 |
| Büyük ve likit hisselerde son 1 yılın en güçlü 10'u (momentum) | %27 / %24 | | ✅ **Gerçek görünüyor.** Tek seçim +%100'de kesilince %21–24; 2020–21 hariç %24–27; S&P'yi 17 yılın 10–12'sinde geçiyor. En kötü düşüş −%54 ile −%65 |

## Momentum kuralının dönemlere göre yıllık getirisi (üç zincir)

| Dönem | Momentum | S&P |
|---|---|---|
| 2010–2014 | %20–27 | %15–16 |
| 2015–2019 | %12–17 | %8–12 |
| 2020–2022 | %6–15 | %8–13 |
| 2023–2026 | %56–64 | %21–22 |

## Bulunan hata (ayrıca kayda alındı)
`sue_fiyat` belirtisi düzeltilmiş fiyatla hesaplanıyor; bu, sonraki hisse bölünmelerinden geleceğe dair bilgi taşıyor. Belirti önceki modellerin belirti setindeydi; onların sonuçlarını da kısmen şişirmiş olabilir. Sızıntı testi (bir sonraki haftayla IC) bunu yakalamadı, çünkü sızıntı haftalar değil yıllar sonraki bölünmeden geliyor. Düzeltme: ham fiyata bölmek.

## Sınırlar
- Büyük hisse havuzu yalnızca günlük fiyatı olan hisseleri içeriyor; borsadan çıkmış büyük şirketlerin bir kısmı eksik olabilir (hayatta kalan yanılgısı).
- Momentum bilinen bir etkidir (akademide 1993'ten beri); 2009 ve 2020 gibi ani dönüşlerde sert kaybettirir.
- 1.252 kural denendi; en iyileri kısmen şans eseri iyi görünür.

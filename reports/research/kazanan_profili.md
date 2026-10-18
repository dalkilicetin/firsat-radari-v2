# Kazanan Profili: Büyük Kazananlar Dönem Başında Nasıl Görünüyordu?

- **Veri:** 2010–2026, 67 çeyrek; her çeyrekte en çok kazandıran 20 hisse (1.340 kazanan) ve en çok kaybettiren 20 hisse, ortalama ~1.900 hisselik evrenle karşılaştırıldı. Değerler dönem başında, o gün bilinen veriyle.
- **Yalnızca güvenilir veri:** fiyat, hacim, mali tablolar, içeriden alımlar, fon bildirimleri, 8-K olayları. Haber, metin, Wikipedia, Reddit yok.
- **Ölçek:** Her belirti o tarihteki evren içinde 0–1 arası sıra; herkesin ortalaması 0,50. Ayrıntılı tablolar: `kazanan_profili.json`.
- **Sınır:** Betimleyici. Bulgular geçmişe bakılarak çıkarıldı; görülmemiş dönemde sınanmadı (bu, 2. aşamanın işi). Çerçeve 1. aşama düzeltmelerinden önceki sürüm; aşağıdaki ayırt edici belirtiler hisse sayısına bağlı değil.

## Bulgu 1: Kazananlar "piyango hisseleri" — ama kaybedenler de öyle

| Özellik | Kazananlar | Kaybedenler | Herkes |
|---|---|---|---|
| Şirkete özgü oynaklık | 0,80 | 0,82 | 0,50 |
| Kârlılık (aktif kârlılığı) | 0,18 | 0,18 | 0,50 |
| Hisse fiyatı | 0,25 | 0,27 | 0,50 |
| Küçük şirket | 0,71 | 0,74 | 0,50 |
| Hisse sayısı artışı (sulandırma) | 0,76 | 0,74 | 0,50 |
| Sağlık + biyoteknoloji payı | %31 | %34 | %14 |
| Denetçi "devamlılık şüphesi" | %9,2 | %12,2 | %2,5 |

"Küçük + ucuz + çok oynak" profilindeki bir hissenin büyük kazanan olma olasılığı %4,6 (genel %1,0), büyük kaybeden olma olasılığı %4,4. Profil büyük hareketi gösteriyor, yönünü göstermiyor.

## Bulgu 2: Yönü ayıran şey — iş düzeliyor, trend kırılmamış, içeriden alım var

| Belirti | Kazananlar | Kaybedenler | Fark |
|---|---|---|---|
| İçeriden alan yönetici sayısı (90 gün) | 0,57 | 0,30 | +0,27 |
| Faaliyet marjı iyileşmesi | 0,56 | 0,34 | +0,22 |
| Son 1 yıl getirisi (son ay hariç) | 0,49 | 0,29 | +0,20 |
| Brüt marj iyileşmesi | 0,60 | 0,40 | +0,20 |
| 40 haftalık ortalamaya uzaklık | 0,50 | 0,33 | +0,17 |
| Gelir sürprizi | 0,49 | 0,33 | +0,16 |
| Büyüme ivmesi | 0,54 | 0,39 | +0,14 |

Kazananlar bu belirtilerde ortalama düzeyde (≈0,50); kaybedenler belirgin biçimde kötü. Ayırt edici güç "en iyiyi bulmak"tan çok "kötüyü elemek"ten geliyor. Not: içeriden alım verisi satırların yalnızca %17'sinde, marj ve sürpriz belirtileri %30–58'inde dolu.

## Bulgu 3: Olaylar

- 3+ yöneticinin birlikte alımı: kazananlarda 1,76 kat, kaybedenlerde 1,51 kat sık.
- Yeni büyük pasif yatırımcı (13G): 1,39 kat / 1,24 kat.
- Hisse ihracı, kayıtsız hisse satışı, devamlılık şüphesi, rapor gecikmesi: ikisinde de sık, kaybedenlerde daha sık.

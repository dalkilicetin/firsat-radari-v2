# En çok kaybettiren hisseler: model neden seçmişti?

`EN_COK_KAZANDIRAN_HISSE_SEBEPLERI.md` ile aynı çalışma, ters yönde: son 3 yılda her çeyrek başında modelin önerdiği 10 hisse içinden **3 ayda en çok kaybettireni**, seçilme nedenleri ve en iyilerle karşılaştırması. Ayar kilitli (`lift_ceza0`), getiriler masraf sonrası, bilgi kesimi perşembe 16:00 (New York). Ham veri: `arac_secimler_ozellik.csv` (120 seçim, çeyrek başına 10).

**Not:** "En kötü" geriye bakışla seçildi; model bunu önceden bilemezdi.

## 1. Her çeyrekte en çok kaybettiren

| Çeyrek başı | Hisse | Listede | 3 ay | Borsa | Model neden koymuştu |
|---|---|---|---|---|---|
| 06.10.2023 | AEHR | 2. | −%42 | +%9 | Tipik 4 işaret (yükseliş sürüyor, satışlar +%28 ve hızlanıyor, dibin 2,7 katı, çip sektörü +%53). 1,3 Mr$ küçük şirket. |
| 05.01.2024 | BBIO | 8. | −%26 | +%11 | Yükseliş + satış artışı (+%1000'lik taban etkisi) + dibin 4,5 katı + bilanço yaklaşıyordu. Sektörü (sağlık) borsanın gerisindeydi. Uyarı: nakit sıkıntısı. |
| 05.04.2024 | ACMR | 5. | −%26 | +%7 | Tipik 4 işaret. Çip sektörü +%87 (borsa +%27) ama 6 ayda zaten +%77 yükselmişti. |
| 05.07.2024 | ML | 8. | −%43 | +%4 | Tipik 4 işaret + bilanço yaklaşıyordu. 0,8 Mr$ küçük şirket, dibin 6,6 katı, zirveden %24 aşağı. Uyarı: hisse satışı. |
| 04.10.2024 | GRBK | 10. (son) | −%30 | +%4 | Tipik 4 işaret + bilanço yaklaşıyordu. İnşaat sektörü +%52. |
| 03.01.2025 | LUNR | 9. | −%69 | −%14 | Yükseliş + satışlar +%359 + dibin 8,1 katı. Sektör işareti yoktu. Uyarı: hisse satışı ve geç rapor. 6 ayda +%429 yükselmişti. |
| 04.04.2025 | TGTX | 3. | −%2 | +%24 | Yükseliş + satış artışı (+%41, hızlanıyor) + dibin 2,8 katı. Sektörü (sağlık) borsanın gerisindeydi. |
| 04.07.2025 | TSSI | 4. | −%36 | +%7 | Tipik 4 işaret. Satışlar +%523 (küçük tabandan), dibin 11,9 katı. 0,7 Mr$. Uyarı: geç rapor. |
| 03.10.2025 | LIF | 10. (son) | −%40 | +%2 | Tipik 4 işaret, zirvesindeydi. 6 ayda +%193 yükselmişti. |
| 02.01.2026 | IDR | 5. | −%15 | −%4 | Tipik 4 işaret. Altın sektörü +%130. 0,6 Mr$, 6 ayda +%209. Uyarı: hisse satışı. |
| 03.04.2026 | VAL | **1.** | −%23 | +%14 | Listenin en yüksek puanı (5 işaret, içeriden alım dahil). Enerji sektörü +%34. |
| 03.07.2026 | LINC | 8. | −%58 | +%4 | Tipik 4 işaret, zirvesindeydi, 6 ayda +%117. |

**Tipik 4 işaret:** yükseliş sürüyor, satışlar büyüyor ve hızlanıyor, dipten kalkmış, sektörü borsadan iyi gidiyor.

## 2. Ne öne çıkıyor?

1. **12 kaybedenin 9'unda tipik 4 işaretin hepsi vardı; yani en iyilerle aynı görünüyorlardı.** Model ikisini ayıramadı; en kötü seçim 3 çeyrekte listenin ilk 5'indeydi, birinde 1.'ydi (VAL).
2. **Küçük şirket ağırlığı:** 12 kaybedenin 6'sı 2 Mr$'ın altında (AEHR, ML, ACMR, TSSI, IDR, LINC); ortadaki 2,3 Mr$. 120 seçimin ortadaki büyüklüğü yaklaşık 4,4 Mr$. Büyüklük ile 3 aylık getiri arasındaki sıra ilişkisi +0,13 (büyük şirketler biraz daha iyi).
3. **Aşırı yükselmiş hisseler:** LUNR (+%429), LIF (+%193), IDR (+%209), TSSI (+%105), LINC (+%117), ACMR (+%77) son 6 ayda zaten çok yükselmişti. 120 seçimde son 26 haftalık getiri ile sonraki 3 ay arasındaki sıra ilişkisi −0,17: önceki yükseliş büyüdükçe sonrası biraz daha kötü. Ama en iyi seçimlerde de aynı ölçüde yükselmiş hisseler vardı (üst yarının ortadaki 26 haftalık getirisi +%66, alt yarının +%75).
4. **Kötü genel hava:** Ocak 2025'te borsa da −%14'tü (LUNR −%69). Çip sektörü hisseleri (AEHR, ACMR) sektör güçlüyken bile düştü.
5. **Uyarılar kaybedeni ayırmadı:** 12 kaybedenin 5'inde uyarı vardı (hisse satışı: ML, LUNR, IDR; geç rapor: LUNR, TSSI; nakit sıkıntısı: BBIO). Ama uyarı taşıyan 43 seçimin ortalama getirisi +%8,8, taşımayan 77'ninki +%4,7; yani uyarılı seçimler daha iyiydi. Hisse satışı olan 35 seçimin %20'si −%20'den fazla kaybetti (tüm seçimlerde %25).

## 3. 120 seçimin tamamında hangi özellik getiri ile ilişkili?

Çeyrek başına 10 seçimde, 3 aylık getiri ile sıra ilişkisi (Spearman):

| Özellik | İlişki | Anlamı |
|---|---|---|
| Son 90 günde yönetici/ortak alımı | +0,15 | Alım olanlar biraz daha iyi (nadir: çoğu seçimde 0) |
| Piyasa değeri | +0,13 | Büyük şirket biraz daha iyi |
| Son 26 haftalık getiri | −0,17 | Çok yükselmiş olan biraz daha kötü |
| Satış büyümesi | −0,12 | Çok büyüyen biraz daha kötü (küçük tabandan gelen sıçramalar) |
| Sektörün 1 yıllık getirisi | −0,11 | |
| Dipten kat | −0,08 | |
| Son rapordan geçen gün | −0,10 | |
| Satış büyümesi hızlanması | −0,09 | |
| Yükseliş sırası, zirveye uzaklık, sektör farkı, olumlu işaret sayısı | −0,03 … +0,04 | Neredeyse ilişkisiz |

**Önemli sınır:** 120 gözlemle bu ilişkilerin standart hatası yaklaşık ±0,09. Yani hiçbiri tek başına güvenilir bir sonuç sayılmaz; bu bir ipucu listesi, kural değil. Ayrıca bu 120 seçimin tamamı zaten modelin üst 10'u olduğu için ilişkiler evrenin tamamından daha zayıf görünür.

## 4. Sonuç

- Kaybedenleri ve kazananları ayıran, modelin şimdiki 6 işaretinde yok. Model "iyi görünen" hisseleri bulup 10'a diziyor; içlerinden hangisinin çökeceğini ayırt edemiyor.
- Küçük şirket ve önceden çok yükselmiş olmak, kaybetme riskini biraz artırıyor gibi görünüyor; bu 120 örnekte güçlü değil. İki ipucu da (büyüklük ve son 26 haftalık getiri) yalnızca 2013–2022 verisinde, evrenin tamamında sınanmadan kural yapılmamalı.
- Sıradaki doğru adım: büyüklük, önceki yükseliş (26 hafta), satış büyümesinin büyüklüğü ve sektör farkını **2013–2022'de** sayısal puana katıp 2023–2026'da denemek. Test edilmeden ayarlanmadı.

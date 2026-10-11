# v5.16 — Ölçüme dayalı model düzeltmesi (hedef: SPY'ı geçmek)

12.07–10.10.2026 arası 65 işlem gününün gece taraması (git geçmişindeki `sonuclar.json`) incelendi.
Her öneri, sonraki 5/10/20 işlem günü fiyatıyla SPY'a karşı ölçüldü. Kalıcılığı test etmek için
veri iki yarıya bölündü: Tem–Ağu ve Eyl–Eki. Değişiklikler sadece İKİ YARIDA DA tutan bulgulara dayanıyor.

## Ne öneriyordu → ne oldu (20 gün, SPY'a göre)
| Liste | Önce | Sebep | Değişiklik |
|---|---|---|---|
| 🔥 Fitil | −%4.8, isabet %38 | Tetiklerin çoğu `epsSurprise`: son raporun (aylar önceki olabilir) sürprizi, çoktan fiyatlanmış. EPS tetikli −%4.7, dönüş+gelir tetikli −%5.7, insider tetikli +%3.2 | Tetik **sadece insider alımı** |
| ⚠️ Geç "kovalama" | **+%5.7**, isabet %61 | Marj dönüşü + güçlü trend = kurumsal para girişi sürüyor | **📈 Trend lideri** olarak yeniden adlandırıldı, Bugünün 10'una eklendi |
| 🌱 Kurulum | −%2.4 | Tetiksiz marj dönüşü fiyata yansımıyor | Bugünün 10'u bonusu kaldırıldı |
| Özet sıralaması (13h getiri) | ilk 10: +%0.7; 11–30: −%1.3 | Son 1–3 ayda en çok koşan hisse geri veriyor | **Trend + düzeltme** sıralaması |
| ⚡ Şok (günlük ≤−%8, ≥2 mlr$) | 5g **+%5**, 20g ~0 | Panik satışı kısa vadede toparlanıyor | "1 hafta toparlanma" etiketi; aylık şok (avantajı yok) Bugünün 10'undan çıktı |

## Yeni ana kural: TREND + DÜZELTME
- 12-3 momentum (52 haftalık getiri, son çeyrek hariç) evrende **ilk %30**
- Son çeyrekteki koşu (3-1 momentum) **medyanın altında**, yani hisse soluklanmış
- Sağlam şirket: ≥2 mlr$ ve kârlı

Geriye dönük sonuç (ilk 10, 20 gün, SPY'a göre): **+%5.9** (Tem–Ağu +%4.9, Eyl–Eki +%10.0).
Eski sıralama aynı dönemde +%0.7. Fiyatı eksik hisseler piyasa değeri değişimiyle tamamlandığında da sonuç tutuyor
(+%7.3 / +%8.9). Uzun vadeli momentumu en zayıf %40'ta olanlar cezalandırılıyor (Eyl–Eki 20g −%5.1).

Test edilip **eklenmeyenler**: rejim filtresi (son 20 günün getirisine göre aç/kapa) işe yaramadı.
Marj dönüşü (gmT−gm5), ROE ve net marj tek başına getiriyi ayırt etmedi.

## Veri hataları düzeltildi
- **Evren 13.08'den beri 1089 → 601**: Wikipedia çekimi sessizce başarısızdı. Düzgün User-Agent eklendi, hata loglanıyor,
  Wikipedia düşerse önceki gecenin evreni kullanılıyor.
- **Yarım koşu (31.08: 601 hissenin 221'i)**: ekranın %85'inden azı geldiyse dosya yazılmıyor, önceki gece korunuyor.
- **Makro `null`**: FRED eksik günleri "." yazıyor, regex bunu sayı sanıp NaN üretiyordu. Düzeltildi; ayrıca önceki değer taşınıyor.
- **Bölünme/spin-off (CTVA 02.10 −%84)**: tek günde −%50'den sert düşüş şok sayılmıyor.
- **Fiyat kapsamı**: artık tüm evrenin fiyatı çekiliyor (+10–19 dk), iş zaman aşımı 180 dk'ya çıkarıldı.

## Karne (yeni)
Gece taraması her gün önerileri giriş fiyatıyla `picks` alanına kaydediyor. 7/14/28 gün önceki önerileri
bugünkü fiyatla SPY'a karşı ölçüp `karne` alanına yazıyor. Uygulamada **Giriş → 📊 Karne** bölümünde görünüyor.
Model SPY'ı geçmeyi bırakırsa ilk burada fark edilir.

## Sınırlar
3 ay ve tek bir piyasa ortamı (yarı iletken/mega şirket rallisi) var. Momentum stratejileri sert dönüşlerde
(momentum çöküşü) topluca kaybedebilir. Kural 6+ ay karneyle izlenmeli. Telegram mesajı bu sürümde değiştirilmedi.

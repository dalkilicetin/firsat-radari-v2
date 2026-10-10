# 4. aşama özeti: model ve doğrulama

Ayrıntılar: [model.md](model.md) (geliştirme dönemi), [model_varyantlari.md](model_varyantlari.md) (ayar seçimi),
[son_donem.md](son_donem.md) (tek seferlik son dönem testi).

## Ne kuruldu

- **Kayan pencere modeli (ridge):** her 4 haftada bir, yalnızca o tarihte getirisi gerçekleşmiş haftalarla yeniden
  eğitilir; en az 52 hafta geçmiş. Girdiler kesitsel sıralar (eksik = nötr), olaylar haftalık ortalamadan sapma.
- **Yol puanları + toplam puan**, beş vade için ayrı (1 hafta, 1 ay, 3 ay, 6 ay, 1 yıl).
- **Potansiyel puanı (0–100):** toplam modelin kesitsel yüzdeliği. **Vade:** puanın en yüksek olduğu vade
  (puan < 70 ise "belirgin potansiyel yok").
- **Ayar seçimi önceden yazılı ölçütle yapıldı** (yatırılabilir evren, 3 ay, ilk %10'un kırpılmış fazla getirisi):
  seçilen B — sıra hedefi, düşük oynaklık sinyali modelden çıkarıldı (risk puanında kalıyor), tüm evrende eğitim.

## Geliştirme dönemi (2016 → Haziran 2025, örneklem dışı)

| Vade | IC tümü (t) | IC yatırılabilir | İlk %10 − son %10 (tümü) |
|---|---|---|---|
| 1 hafta | 0.072 (17.5) | 0.042 | %1.3 |
| 1 ay | 0.098 (10.0) | 0.055 | %3.3 |
| 3 ay | 0.137 (5.9) | 0.079 | %7.6 |
| 6 ay | 0.163 (4.5) | 0.097 | %12.5 |
| 1 yıl | 0.181 (4.3) | 0.101 | %15.1 |

Yalnızca momentum (karşılaştırma): yatırılabilir evrende 3 ay IC 0.027 — model yaklaşık 3 kat.
Potansiyel puanı dilimleri sıralı: 0–30 diliminde 3 ay medyan fazla getiri −%7.4, 90–100 diliminde +%2.3.

## Son dönem testi (Temmuz 2025 → Ekim 2026, tek seferlik)

Model `1098926` sürümünde donduruldu, test bir kez çalıştırıldı, sonuca göre değişiklik yapılmadı.

| Vade | Geliştirme IC | Son dönem IC (tümü) | t | Son dönem IC (yatırılabilir) |
|---|---|---|---|---|
| 1 hafta | 0.072 | 0.077 | 6.4 | 0.024 |
| 1 ay | 0.098 | 0.126 | 3.6 | 0.049 |
| 3 ay | 0.137 | 0.179 | 3.0 | 0.064 |
| 6 ay | 0.163 | 0.221 | — | 0.088 |
| 1 yıl | 0.181 | 0.229 | — | 0.050 |

- **Tüm evrende** model son dönemde geliştirme dönemi kadar, hatta daha iyi çalıştı.
- **Yatırılabilir evrende** yön doğru ama zayıfladı ve tek başına istatistiksel olarak anlamlı değil (t < 2).
  Gerçekçi beklenti: büyük/likit hisselerde sinyal küçük; asıl ayrışma küçük hisselerde ve kötü hisseleri elemekte
  (son %10 belirgin şekilde kötü).
- 6 ay ve 1 yıl için gerçekleşmiş hafta sayısı az (41 ve 15, çakışan pencereler); bu satırlar güvenilir değil.
  Yatırılabilir evrende 1 yılda ilk %10 − son %10 farkı negatif çıktı (15 hafta).
- **Risk puanı son dönemde de tutarlı:** 26 haftalık medyan en büyük düşüş seviye 1'de −%7, seviye 5'te −%52;
  %30+ düşüş olasılığı %10 → %71.

## Yollar

- **1. yol (iş modeli ve yön)** modelin taşıyıcısı (son dönem 3 ay IC 0.156).
- **3. yol (kurumsal)** katkı veriyor (0.049).
- **Piyasa sinyalleri** (momentum, boyut) güçlü kontrol.
- **2. yol (gündem)** ve **4. yol (tema)** son dönemde sıfır/negatif. Raporda gösterilecekler ama toplam puandaki
  ağırlıkları model tarafından zaten çok küçük tutuluyor; bu iki yol "açıklama" amaçlı kalacak.

## 5. aşamaya taşınanlar

- Vade seçimi yalnızca kısa vadede belirgin değer katıyor; raporda vade + o vadenin puanı birlikte gösterilecek.
- Öneri takibi: her haftanın önerileri kaydedilip gerçekleşen getirilerle karşılaştırılacak; model zaten her
  4 haftada yeni verilerle yeniden eğitiliyor (kalibrasyon bu döngüyle sürer).

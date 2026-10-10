# Fırsat modeli — ön kayıt (2026-10-10, sonuçlara bakılmadan yazıldı)

Amaç: "geleceğin fırsatları" — büyük kazananları (PLTR tipi) önceden işaretleyebilen bir puan. Mevcut model
(medyanı geçme hedefi) büyük kazananları yakalamadı: geliştirme döneminde 1 yılda +%200 üstü kazanan
hisselerin medyan puanı 32, ilk %10'da olma payı %5 (bkz. 4. aşama sonrası analiz).

## Evren

- Finans dışı faaliyet şirketleri: SIC 6xxx (banka, sigorta, GYO, BDC, diğer finans) ve SPAC'ler (SIC 6770 ya da
  adı) hariç (`radar/research/sectors.py`). Borsadan çıkan şirketler dahil (çıkış değeri, iflasta 0).
- Eğitim: tüm faaliyet şirketleri. **Birincil ölçüm: yatırılabilir faaliyet şirketleri** (fiyat ≥ 5 $,
  günlük işlem ≥ 1 mn $).

## Dönem

- Yalnızca geliştirme dönemi: tahmin tarihi + vade < 2025-07-01.
- Son dönem (Temmuz 2025 →) 4. aşamada bir kez kullanıldı; yeniden "temiz test" sayılmaz. Bu modelin gerçek
  testi bundan sonraki haftaların canlı takibidir (her haftanın puanları kaydedilir).

## Hedef

- **Birincil:** 52 haftalık getiri ≥ +%100 → 1, değilse 0 (çıkış değeri dahil).
- İkincil (yalnızca raporlanır): 26 haftalık getiri ≥ +%50.

## Model (tek sürüm, ayar yok)

- Kayan pencere ridge (doğrusal olasılık modeli), 4. aşamayla aynı altyapı: kesitsel sıra girdileri, eksik = nötr,
  4 haftada bir yeniden kurulum, en az 52 hafta, ceza 0,05. Yalnızca gerçekleşmiş hedefler kullanılır.
- Girdiler: kütüphanedeki 44 sinyalin tamamı (oynaklık dahil — hedef asimetrik olduğu için).
- Bu turda yeni sinyal eklenmez; sonuca bakıp sinyal ya da ayar değiştirilmez.

## Başarı ölçütü (yatırılabilir faaliyet şirketleri, geliştirme dönemi, 1 yıl vade)

Üçü birden sağlanmalı:

1. **Büyük kazanan oranı:** puanı en yüksek %10'da +%100 kazananların oranı, evrendeki genel orana göre
   ≥ 1,5 kat; yıllık bloklarla bootstrap %90 güven aralığının alt sınırı > 1,0 kat.
2. **Basit kıyas:** aynı oran, yalnızca "en yüksek geçmiş oynaklık" ile seçilen %10'un oranından yüksek olmalı
   (oynak küçük hisseler doğal olarak daha çok büyük kazanan üretir; model bundan fazlasını yapmalı).
3. **Portföy:** ilk %10'dan eşit ağırlıklı portföy (4 haftada bir yeniden dengeleme, maliyet sonrası) yıllık
   getirisi, aynı evrenin eşit ağırlıklı portföyünden düşük olmamalı (piyango bileti toplayıp toplamda
   kaybettirmemeli).

Ölçüt sağlanmazsa sonuç olduğu gibi raporlanır; model "fırsat puanı" olarak kullanılmaz.

## Güvenlik modeli

4. aşamanın seçilen ayarı (B: sıra hedefi, oynaklık hariç) değiştirilmeden yeni evrende yeniden kurulur.

## Portföy simülasyonu (iki model için de)

- İlk %10 ve ilk 20 hisse, eşit ağırlık; 4 haftada bir yeniden dengeleme; arada çıkan hisse çıkış değeriyle
  nakde döner.
- İşlem maliyeti (tek yön, 13 haftalık medyan günlük işlem tutarına göre): ≥ 50 mn $: %0,05; 10–50 mn $: %0,15;
  1–10 mn $: %0,40; < 1 mn $ ya da bilinmiyor: %1,00.
- Kıyas: aynı evrenin eşit ağırlıklı portföyü.
- Ölçüler: yıllık getiri, oynaklık, Sharpe, Sortino, en büyük düşüş, devir hızı, yıl yıl fazla getiri,
  52 haftalık bloklarla bootstrap %90 güven aralığı.
- Puan dilimi kalibrasyonu: her 10 puanlık dilimin gerçekleşen medyan fazla getirisi, medyanı geçme oranı ve
  güven aralığı (raporda puanın yanında gösterilecek).

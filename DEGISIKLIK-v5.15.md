# v5.15 — ŞOK kapsamı + BUGÜNÜN 10'U

## 1. "Data geç mi geliyor?" — HAYIR, bug başkaydı

15 Temmuz taraman (05:23 UTC) IBM'i **doğru yakalamış**:
  quotes.IBM = { price: 217.07, chgPct: -25.21 }   ✓
  screen.IBM.r52w = -23.5                          ✓

Data tam ve güncel. Sorun: raporu **v5.13** ile ürettin ve v5.13'te `chgPct`'yi
okuyan hiçbir kod yoktu. Veri oradaydı, kimse bakmıyordu.
v5.14'teki ŞOK paterni bunu zaten çözdü.

## 2. Kapsam sorunu (gerçek eksik) — ÇÖZÜLDÜ

`quotes` sadece ~419 hissede var, `screen` ~1097'de.
Eski ŞOK taraması sadece quotes'a bakıyordu → 678 hisse kör noktadaydı.

**Yeni `shockList()`** iki sinyali birleştirir:
- **Günlük**: `quotes.chgPct <= -8`  (419 hisse, en acil)
- **Aylık/haftalık**: `screen.mtd <= -12`  (1097 hisse, geniş kapsam)

Sıralama şiddet + kaliteye göre: DEV (+30), NDX100 üyesi (+20),
mikro-cap <2 mlr$ (-25, gürültü riski).

Bugünkü datada yakaladıkları:
  IBM  ⚡ gün  -25.2%  [DEV]
  ERIC ⚡ gün  -13.5%  [DEV]
  MRVL 📉 ay   -25.3%  [DEV/NDX]
  KLAC 📉 ay   -23.6%  [DEV/NDX]
  INTC 📉 ay   -22.8%  [DEV/NDX]
  ARM  📉 ay   -20.7%  [DEV/NDX]
  LRCX 📉 ay   -20.1%  [DEV/NDX]
→ Yarı iletkende toplu kırılma görünüyor: tek hisse hikayesi değil, TEMA olayı.

## 3. ★ BUGÜNÜN 10'U — seçim felcine çözüm

Yeni sekme + raporun en üstünde. 150 isim yerine 10.

Üç kaynaktan harmanlanır:
- Güçlü adaylar (conviction >= 7)
- 🚀 Moonshot fitilleri
- ⚡ Sert düşen kaliteli devler (şiddete göre ölçekli puan)

**Çeşitlilik zorunlu**: aynı sektörden en fazla 3 isim.
**Ceza**: ENKAZ -20, skandal -15, değer tuzağı -5, marj daralması -4.

Bugünkü çıktı:
  1. FSLR  güçlü aday + fitil   <semiconductors>
  2. APH   güçlü aday + fitil   <electrical equipment>
  3. APP   fitil + şok          <technology>
  4. IBM   ⚡ şok               <technology>
  5. LRCX  aday + şok           <semiconductors>
  ...

Not: ŞOK puanı şiddete göre ölçeklenir (günlük -%25 → 16 puan), çünkü
kaliteli bir devin tarihi çöküşü sıradan bir adaydan fazla dikkat hak eder.

## Kalıcı sınır
Gece taraması günde bir çalışır. Gün içi çöküş, bir sonraki tarama çalışana
kadar görünmez. Anlık alarm için saatlik cron gerekir (API kotası ~24x artar).

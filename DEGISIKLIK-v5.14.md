# v5.14 — ŞOK RADARI (IBM dersi)

## Sorun
14.07.2026: IBM tek günde **-%25.21** düştü (1968'den beri en kötü günü; 1987 Black Monday'deki
-%23.7'yi bile geçti). Sebep: şirket 22 Temmuz'daki planlı rapordan önce, plansız bir yatırımcı
mektubuyla zayıf ön Q2 sonuçları açıkladı (gelir 17.2 mlr$ vs beklenti 17.86 mlr$).

**v5.13 bunu tespit edemedi. Üç ayrı sebepten:**

1. **Veri gecikmesi (kök sebep):** Gece taraması günde bir çalışır. Rapor 12 Temmuz verisiyle
   üretilmişti, olay 14 Temmuz'da oldu. Datada IBM hâlâ $287.56 görünüyordu (gerçek: ~$217).

2. **"Tek günlük şok" kavramı yoktu:** Sistemde sadece aylık (r1m), 3-aylık, yıllık pencereler
   vardı. Tek günde -%25, aylık pencerede yumuşayıp kayboluyordu.
   `quotes.chgPct` (günlük değişim) datada VARDI ama hiçbir yerde kullanılmıyordu.

3. **C paterni "şampiyon" şartına takılıyordu:** C ("olayı incele") için `r60m >= 1.00`
   (5 yılda en az x2) şartı vardı. IBM'in 1y getirisi +%0.05 — şampiyon sayılmadığı için
   %25 çakılsa bile C paterni tetiklenmiyordu.

## Çözüm

### 1. Yeni patern: ŞOK
`quotes.chgPct <= -8` → "⚡ Tek günde %X çöküş — OLAYI OKU"
Ek olarak dev+kaliteli şirket (mcap≥50 mlr$, max(roic,roe)>12) ve chgPct≤-15 ise:
**ŞOK-DEV** → "panik mi, kırılma mı? Sebebi oku, aceleyle alma"

Not: IBM'in roic'i 11.44 (roe 35.53). `roic ?? roe` kullanınca kalite şartına takılıyordu;
`max(roic, roe)` olarak düzeltildi.

### 2. Yeni patern: C2 (C-geniş)
Şampiyon olmayan ama **büyük/kaliteli** şirketin sert düşüşü de olay adayı:
`r1m <= -0.18 && (mcap>=50 mlr$ || max(roic,roe)>15)`

### 3. ŞOK RADARI bölümü (rapor + Telegram)
Raporun **en üstünde**, Özet'ten önce. **Skordan bağımsız** listelenir —
çünkü ŞOK cezası skoru düşürüyordu ve hisse listeden tamamen kayboluyordu.
Amaç gizlemek değil, uyarıyla göstermek.

### 4. Veri tazeliği uyarısı
Rapor başında: "⚠️ VERİ N GÜN ESKİ. Bu süre içinde açıklanan bilanço uyarısı,
kâr kılavuzu kesintisi veya ani çöküşler bu raporda YOK."

## Kalıcı sınır (dürüst not)
Gece taraması günde bir çalışır. Gün içi olan bir çöküş, bir sonraki tarama çalışana
kadar raporda görünmez. ŞOK RADARI bunu *tarama sonrası* yakalar — *anlık alarm değildir*.
Anlık tespit için intraday tarama (saatlik cron) gerekir; bu API kotanı ~24x artırır.

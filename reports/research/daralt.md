# Listeyi Daraltma: Temel Kural + Ek Koşul

**Temel kural:** dibin ≥ 2 katı (52 hafta) + gelir ≥ %20 + en likit %30.

**Arama**
- 137.732 daraltma denendi (`radar/research/daralt.py`):
  - tek ek koşul;
  - iki ek koşul;
  - bir belirtiye göre en iyi 3/5/8/10.
- Yalnızca güvenilir ve bugün değeri olan belirtiler kullanıldı.
- **Seçim yalnızca Ocak zincirinde.** Şartlar: getiri temelden yüksek, hisse sayısı en az yarıya inmiş.
- **Doğrulama:** Şubat ve Mart zincirlerinde ve 2010–2017 / 2018–2026 dönemlerinde temelden düşük olmamalı.

**Bulunan sızıntı.** Hisse tablosunun satır sırası bugünkü büyüklüğe göre (NVDA, TSLA, MU …) ve geleceği taşıyor: satır sırasına göre seçilen ilk 5 hisse %14,3, rastgele 5 hisse %9,2 getiriyor. Eşitliklerin satır sırasıyla bozulduğu bütün kurallar (olay "en düşük K", temettü/borç kuralları) sahte çıktı. Eşitlikler artık rastgele bozuluyor.

## Sonuç: sektör momentumu

**Kural A:** temel + hissenin sektörünün son 1 yıl momentumu en üst %13'te (`sektor_momentum_12_1` ≥ 0,87).

| | Ocak | Şubat | Mart | Tipik hisse | En kötü düşüş |
|---|---|---|---|---|---|
| Temel | %24,9 | %34,7 | %27,5 | 14–15 | −%35 ile −%44 |
| **A** | **%45,9** | **%35,3** | **%34,1** | **4** | −%48 ile −%51 |
| A, tek hisse +%100 sınırı | %40,7 | %33,8 | %31,8 | | |
| B: A + 10 hafta ortalama 40 haftalığın ≥ %19 üstünde | %54,9 | %36,5 | %41,3 | 3 | −%39 ile −%48 |

- **Dönemler:** A, 2010–2017'de %31 (temel %22), 2018–2026'da %45 (temel %35).
- **Plato:** Sektör eşiği 0,81 / 0,87 / 0,92'nin üçünde de temelden iyi; 0,72'de etki azalıyor.
- **Yıl yıl (Şubat zinciri):** A, S&P'yi 17 yılın 11'inde geçti.
  - Güçlü yıllar: 2016 +%71, 2018 +%67, 2020 +%165, 2025 +%117.
  - Zayıf yıllar: 2011, 2015, 2021, 2023.
- **Daha çok kâr, daha çok risk:** Hisse sayısı azalınca düşüşler derinleşiyor.

## Bugün (9 Ekim 2026)
- **Temel kural:** 82 hisse.
- **A:** 30 hisse (geçmişte tipik 4; piyasa çok yükselmiş).
- **B:** 17 hisse.
- Bugün en güçlü sektörler yarı iletken, enerji (rafineri) ve biyoteknoloji. Liste: `daralt_bugun.csv`.

**Uyarı:** 137.732 aday denendi. Ocak'ta en iyi 20 adayın yarısı doğrulamayı geçti; seçim yanlılığı var. Şubat zincirinde A temelle neredeyse eşit (%35,3 / %34,7).

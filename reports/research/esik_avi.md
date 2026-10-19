# Eşik Avı: Dipten, Zirveden, Gelir Büyümesi (gerçek sayılar)

- `radar/research/esik_avi.py`. 4.320 kombinasyon: dipten kat (1,5–10), zirveye en fazla uzaklık (%5–sınırsız), zirveden en az uzaklık (%0–30), gelir büyümesi en az (sınırsız, %0–200), likidite sırası (tümü, üst %50, %30, %10).
- Portföy: uyan bütün hisseler eşit ağırlık, 3 ay, maliyet dahil; 5'ten az hisse varsa S&P. Yeterli kapsam (dönemlerin ≥%75'inde yatırım): 396 kombinasyon. Sıralama üç zincirin en kötüsüne göre.
- S&P 500 aynı dönemlerde: %13,7–14,6/yıl.

## En iyi eşikler (üç zincirde de)

| Dipten en az | Zirveye en fazla | Gelir büyümesi en az | Likidite | Ocak | Şubat | Mart | En kötü düşüş | Tipik hisse sayısı |
|---|---|---|---|---|---|---|---|---|
| 2,0× | sınırsız | %20 | üst %30 | %28,9 | %33,7 | %29,7 | −%36 | 14 |
| 2,0× | %50 | %0 | üst %30 | %29,2 | %35,9 | %28,5 | −%33 | 18 |
| 2,0× | sınırsız | %0 | üst %30 | %30,8 | %34,7 | %28,4 | −%33 | 19 |
| 2,0× | %30 | %10 | üst %30 | %26,2 | %36,2 | %31,3 | −%34 | 14 |

## Her eşiğin etkisi (en iyi 50 kombinasyonun içinde)
- **Dipten:** 2,0× açık ara en iyi (50'nin 37'si). 1,5× çok gevşek (getiri %18–21). 2,5× ve üstünde hisse sayısı çoğu dönemde 5'in altına iniyor; 3×, 5×, 10× yeterli kapsam bulamıyor.
- **Zirveden uzaklık:** "Zirveden en az %10/20/30 uzak" şartı en iyi 50'de hiç yok. Zirveden uzak olmak hiç yardımcı olmuyor; zirveye yakın olmak zararsız. Zirveye en fazla %20–50 uzaklık ile sınırsız arasında fark küçük.
- **Gelir büyümesi:** En iyi bölge en az %0–20. %30'dan sonra hisse sayısı azalıyor; %50 ve üstü getiriyi düşürüyor (dipten 1,5× ile %17).
- **Likidite:** En likit %30 en iyi; %50'ye genişlemek getiriyi ~5 puan düşürüyor; en likit %10 hisse sayısını çok azaltıyor.

## Sonuç
"En yüksek" eşikler aşırı uçlarda değil, ortada: **dibin en az 2 katı, gelir en az %10–20 artmış, zirveye yakın ya da zirvede, çok likit**. Daha sıkı eşikler (3×, %50 gelir) tek tek büyük kazananları yakalar ama portföyü çok az hisseye indirir ve ortalama getiriyi düşürür.

**Uyarı:** 4.320 kombinasyondan en iyisi seçildiği için şans payı var. Dipten 2,0× etrafındaki geniş plato bunun gerçek bir etki olduğunu düşündürüyor.

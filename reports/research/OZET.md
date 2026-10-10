# 3. aşama özeti: sinyaller ve risk puanı

Dönem: 2015 → 2025-07-01 öncesi. Son dönem (2025-07 → bugün) hiçbir ölçümde kullanılmadı; 4. aşamanın sonunda
tek sefer test edilecek. Evren: her hafta o gün Nasdaq'ta işlem gören hisseler, sonradan borsadan çıkanlar dahil
(çıkışta iflas = 0). Fazla getiri: aynı evrenin haftalık medyanına göre. Yatırılabilir evren: fiyat ≥ 5 $ ve
günlük işlem ≥ 1 M$.

Ayrıntılar: [risk.md](risk.md) · [road1.md](road1.md) · [road1_text.md](road1_text.md) · [road2.md](road2.md) ·
[road3.md](road3.md) · [road4.md](road4.md)

## Risk puanı (1–5)

| Risk | Medyan en büyük düşüş (1 yıl) | %50+ düşüş olasılığı | Kötü çıkış olasılığı | Medyan 1 yıllık getiri |
|---|---|---|---|---|
| 1 | -%10 | %5 | %0,04 | +%5,8 |
| 2 | -%19 | %16 | %0,18 | +%0,2 |
| 3 | -%32 | %31 | %0,45 | -%12,0 |
| 4 | -%40 | %40 | %1,77 | -%21,7 |
| 5 | -%56 | %55 | %7,05 | -%42,6 |

Kötü çıkış (iflas ya da %50+ kayıpla borsadan çıkış) ayırt etme gücü AUC 0,885 (yalnızca oynaklık: 0,806).

## Sinyaller (3 aylık vade)

Sürekli sinyallerde etki = IC (sıralama korelasyonu); olaylarda etki = ortalama fazla getiri.
Hüküm: |t| ≥ 3 güçlü, ≥ 2 zayıf.

| Yol | Sinyal | Tür | Tüm hisseler (3a etki, t) | Yatırılabilir (3a etki, t) |
|---|---|---|---|---|
| 1. yol | gelir_buyumesi | sürekli | 0.0105 (t=1.21) — anlamlı değil | -0.0004 (t=0.62) — anlamlı değil |
| 1. yol | buyume_ivmesi | sürekli | 0.0145 (t=0.88) — anlamlı değil | 0 (t=0.37) — anlamlı değil |
| 1. yol | brut_marj_degisimi | sürekli | 0.0202 (t=3.1) — güçlü pozitif | 0.0159 (t=2.3) — zayıf pozitif |
| 1. yol | faaliyet_marji_degisimi | sürekli | 0.0129 (t=2.23) — zayıf pozitif | 0.0037 (t=1.26) — anlamlı değil |
| 1. yol | arge_yogunlugu | sürekli | -0.0879 (t=-5.06) — güçlü negatif | -0.0598 (t=-2.8) — zayıf negatif |
| 1. yol | serbest_nakit_getirisi | sürekli | 0.1053 (t=4.51) — güçlü pozitif | 0.0757 (t=3) — güçlü pozitif |
| 1. yol | kazanc_getirisi | sürekli | 0.1063 (t=5.06) — güçlü pozitif | 0.0882 (t=3.83) — güçlü pozitif |
| 1. yol | tahakkuklar_dusuk | sürekli | -0.0666 (t=-4.42) — güçlü negatif | -0.0323 (t=-2.24) — zayıf negatif |
| 1. yol | varlik_buyumesi_dusuk | sürekli | -0.032 (t=-2.38) — zayıf negatif | -0.0016 (t=-0.13) — anlamlı değil |
| 1. yol (metin) | metin_benzerligi_is_tanimi | sürekli | 0.0365 (t=2.93) — zayıf pozitif | 0.0181 (t=1.34) — anlamlı değil |
| 1. yol (metin) | metin_benzerligi_riskler | sürekli | 0.0131 (t=0.93) — anlamlı değil | 0.0053 (t=-0.08) — anlamlı değil |
| 1. yol (metin) | metin_benzerligi_yonetim | sürekli | 0.0524 (t=4.25) — güçlü pozitif | 0.0248 (t=1.76) — anlamlı değil |
| 1. yol (metin) | metin_benzerligi_ortalama | sürekli | 0.0423 (t=3.63) — güçlü pozitif | 0.0218 (t=1.36) — anlamlı değil |
| 1. yol (metin) | risk_bolumu_buyumesi_dusuk | sürekli | 0.0039 (t=1.78) — anlamlı değil | -0.0036 (t=-0.2) — anlamlı değil |
| 1. yol (metin) | devamlilik_suphesi | olay | -0.0257 (t=-1.1) — anlamlı değil | -0.0475 (t=-3.67) — güçlü negatif |
| 2. yol | wiki_ilgi_ivmesi | sürekli | 0.0202 (t=0.98) — anlamlı değil | 0.0095 (t=-0.18) — anlamlı değil |
| 2. yol | wiki_ani_ilgi | olay | 0.0613 (t=1.5) — anlamlı değil | 0.0303 (t=0.96) — anlamlı değil |
| 2. yol | haber_ivmesi | sürekli | 0.0183 (t=2.28) — zayıf pozitif | 0.0138 (t=1.91) — anlamlı değil |
| 2. yol | haber_ani_artis | olay | 0.0371 (t=4.5) — güçlü pozitif | 0.0188 (t=3.19) — güçlü pozitif |
| 2. yol | haber_ton_degisimi | sürekli | 0.0074 (t=0.16) — anlamlı değil | 0.0045 (t=0.14) — anlamlı değil |
| 2. yol | haber_ton_seviyesi | sürekli | 0.0307 (t=3.98) — güçlü pozitif | 0.0216 (t=2.7) — zayıf pozitif |
| 3. yol | icerden_alici_sayisi_90g | sürekli | -0.0044 (t=-0.31) — anlamlı değil | -0.0066 (t=0.59) — anlamlı değil |
| 3. yol | icerden_alim_kumesi_3plus | olay | 0.0312 (t=3.51) — güçlü pozitif | 0.0083 (t=0.39) — anlamlı değil |
| 3. yol | icerden_alim_tutar_piyasa_degeri | sürekli | 0.019 (t=1.48) — anlamlı değil | -0.0056 (t=-0.39) — anlamlı değil |
| 3. yol | ust_yonetici_alimi_90g | olay | 0.0258 (t=3.54) — güçlü pozitif | 0.0078 (t=0.56) — anlamlı değil |
| 3. yol | kurumsal_sahip_degisimi | sürekli | 0.0013 (t=-0.04) — anlamlı değil | -0.0086 (t=-0.89) — anlamlı değil |
| 3. yol | kurumsal_hisse_degisimi_payi | sürekli | -0.0053 (t=-0.92) — anlamlı değil | -0.0216 (t=-1.69) — anlamlı değil |
| 3. yol | 8k_1.01_önemli anlaşma | olay | -0.0055 (t=-0.72) — anlamlı değil | -0.007 (t=-2.15) — zayıf negatif |
| 3. yol | 8k_1.02_anlaşma feshi | olay | 0.0093 (t=1.51) — anlamlı değil | 0.0046 (t=1.9) — anlamlı değil |
| 3. yol | 8k_2.01_satın alma/elden çıkarma tamamlandı | olay | -0.0085 (t=-0.3) — anlamlı değil | -0.0202 (t=-1.58) — anlamlı değil |
| 3. yol | 8k_2.03_yeni borç yükümlülüğü | olay | 0.0053 (t=0.68) — anlamlı değil | 0.0034 (t=0.63) — anlamlı değil |
| 3. yol | 8k_3.02_kayıtsız hisse satışı (sulandırma) | olay | -0.0419 (t=-2.44) — zayıf negatif | -0.041 (t=-3.05) — güçlü negatif |
| 3. yol | 8k_5.02_yönetici değişikliği | olay | 0.0121 (t=1.24) — anlamlı değil | 0.0044 (t=0.36) — anlamlı değil |
| 3. yol | 8k_7.01_kamuyu aydınlatma (FD) | olay | 0.0138 (t=1.54) — anlamlı değil | 0.0049 (t=0.6) — anlamlı değil |
| 3. yol | 8k_8.01_diğer olaylar | olay | 0.0081 (t=0.93) — anlamlı değil | 0.004 (t=0.47) — anlamlı değil |
| 3. yol | geri_alim_getirisi | sürekli | 0.0586 (t=3.94) — güçlü pozitif | 0.0476 (t=2.95) — zayıf pozitif |
| 4. yol | tema_ruzgari | sürekli | 0.0052 (t=0.9) — anlamlı değil | -0.0051 (t=0.35) — anlamlı değil |

## Öne çıkanlar

- **İki evrende de güçlü:** kazanç getirisi, serbest nakit akışı getirisi, geri alım getirisi (pozitif);
  ani haber artışı (pozitif); 8-K 3.02 sulandırma ve devamlılık şüphesi (negatif); Ar-Ge yoğunluğu (negatif).
- **Yalnızca küçük/az takip edilen hisselerde:** içeriden alım kümeleri, üst yönetici alımı, Lazy Prices
  (10-K metin benzerliği). Bu sinyaller büyük hisselerde kayboluyor — literatürle uyumlu.
- **İşe yaramayanlar:** 13F değişimleri, çoğu 8-K olayı, Wikipedia ilgisi, gelir büyümesi, tema rüzgârı.
- **Literatürün tersi:** düşük tahakkuk ve düşük varlık büyümesi bu evrende negatif.

## Sınırlamalar

- Çıkan hisselerde fiyat seyrek (FTD); çıkış anındaki son düşüş eksik kalabilir.
- GDELT: günde 24 dosya örneklemi (akışın ~%25'i); kurum adı eşleştirmesi isim varyantlarıyla.
- Form 4 vermeyen yabancı şirketler çıkış evreninde eksik.
- Sinyaller tek tek ölçüldü; birbirleriyle örtüşmeleri (ör. ani haber artışı ↔ momentum) 4. aşamada ayıklanacak.

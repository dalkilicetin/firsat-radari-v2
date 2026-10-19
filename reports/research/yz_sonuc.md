# Yürüyen Modeller — Görülmemiş Veride Sonuçlar (geliştirme 2013–2024)

Her test yılı için model yalnızca etiketi o yıl başlamadan kapanmış verilerle eğitildi; ayarlar sabit. 2025–2026 kilitli.

| Model | İlk 3: ort. 3 ay | İlk 3: ort. 6 ay | İlk 3: S&P'yi geçen çeyrek | İlk 3 en iyi %5'te | İlk 10: ort. 3 ay | İlk 10: net bileşik yıllık | İlk 10 en kötü düşüş | İlk 3 − S&P (%90 GA) | İlk 3 − momentum (%90 GA) |
|---|---|---|---|---|---|---|---|---|---|
| rastgele | +3.3% | +7.7% | +39.6% | +6.2% | +4.6% | +13.5% | -37.7% | -3.7% … +2.7% | -14.6% … -0.4% |
| momentum_buyuk | +10.3% | +23.0% | +54.2% | +18.1% | +7.2% | +22.9% | -53.8% | +1.4% … +12.6% | — |
| kural_ogrenici | +9.8% | +15.9% | +63.0% | +15.2% | +9.1% | +33.0% | -27.2% | +3.7% … +8.5% | -5.6% … +4.6% |
| lgb_sinif5 | +11.0% | +17.6% | +54.2% | +18.8% | +12.3% | +41.7% | -42.5% | +0.3% … +14.9% | -4.8% … +6.6% |
| lgb_sinif1 | +8.2% | +8.3% | +56.2% | +20.8% | +5.5% | +9.7% | -79.3% | -2.6% … +11.7% | -7.3% … +3.5% |
| lgb_sirala | +12.5% | +25.6% | +56.2% | +21.5% | +12.4% | +34.0% | -66.0% | -0.4% … +20.1% | -5.0% … +9.5% |
| lgb_sirala_6a | +15.8% | +33.9% | +58.3% | +25.7% | +9.0% | +24.6% | -75.6% | +4.8% … +20.0% | -0.8% … +10.6% |
| iki_asama | +3.6% | +4.9% | +43.8% | +12.5% | +6.2% | +15.3% | -67.0% | -5.3% … +5.2% | -11.6% … -1.7% |
| kuyruk_q90 | +8.7% | +14.2% | +50.0% | +20.1% | +7.0% | +12.2% | -81.9% | -4.7% … +16.3% | -10.7% … +9.0% |
| topluluk | +16.0% | +32.5% | +50.0% | +24.3% | +11.6% | +33.9% | -42.0% | +3.8% … +21.5% | -1.6% … +13.8% |
| kural_A_gordu | +13.1% | +21.1% | +60.9% | +20.3% | +12.8% | +48.1% | -23.9% | +6.6% … +12.2% | -1.4% … +7.0% |
| kural_B_gordu | +17.8% | +27.5% | +69.0% | +24.2% | +17.0% | +59.8% | -26.4% | +7.8% … +21.8% | +0.0% … +14.5% |

- S&P 500: 3 ay +3.7%, 6 ay +6.9%. Gerçek en iyi 3: 3 ay +229.6%, 6 ay +242.6%.
- Rastgele beklenti: en iyi %5'te olma %5.
- Aşırı uyum olasılığı (PBO, öğrenen modeller arasında): +31.4%.
- Meta seçim (her yıl yalnızca geçmiş sonuçlara göre model seçimi, 2016–2024): ilk 3 ort. 3 ay +15.0%, 6 ay +38.6%. Seçimler: {2016: 'kural_ogrenici', 2017: 'lgb_sirala_6a', 2018: 'momentum_buyuk', 2019: 'lgb_sirala_6a', 2020: 'lgb_sirala_6a', 2021: 'lgb_sirala_6a', 2022: 'lgb_sirala_6a', 2023: 'lgb_sirala_6a', 2024: 'lgb_sirala_6a'}
- 'kural_A_gordu' / 'kural_B_gordu': geçmişin tamamına bakılarak bulunmuş kurallar; yalnızca kıyas, görülmemiş sayılmaz.

## Kilitli dönem 2025–2026 (seçim yz_secim.json ile sabitlendikten sonra bir kez açıldı)

Sabitlenen seçim: ilk3_3a = topluluk, ilk3_6a = lgb_sirala_6a, ilk10_portfoy = lgb_sinif5. Sonuca göre model ya da ayar değiştirilmez.

| Model | Çeyrek | İlk 3: ort. 3 ay | İlk 3: ort. 6 ay | İlk 3: S&P'yi geçen çeyrek | İlk 3 en iyi %5'te | İlk 10: ort. 3 ay | İlk 10: net bileşik yıllık | İlk 3 − S&P (%90 GA) |
|---|---|---|---|---|---|---|---|---|
| rastgele | 7 | +7.6% | +8.1% | +57.1% | +14.3% | +12.2% | +43.4% | -5.7% … +14.3% |
| momentum_buyuk | 7 | +20.5% | +35.7% | +57.1% | +19.0% | +19.0% | +69.5% | +14.8% … +16.5% |
| kural_ogrenici | 6 | +7.0% | +36.6% | +66.7% | +11.1% | +7.8% | +20.9% | -6.6% … +17.5% |
| lgb_sinif5 | 7 | -1.3% | +30.3% | +42.9% | +9.5% | -5.3% | -33.9% | -17.4% … +2.5% |
| lgb_sinif1 | 7 | -7.3% | +15.8% | +28.6% | +4.8% | -3.0% | -34.6% | -34.8% … +5.0% |
| lgb_sirala | 7 | +50.2% | +57.2% | +57.1% | +14.3% | +21.0% | +59.1% | -0.1% … +106.1% |
| lgb_sirala_6a | 7 | +8.6% | +16.8% | +71.4% | +19.0% | +17.6% | +50.7% | -6.0% … +17.2% |
| iki_asama | 7 | -8.3% | +10.5% | +14.3% | +4.8% | -1.1% | -23.1% | -19.4% … -8.3% |
| kuyruk_q90 | 7 | +45.1% | +36.1% | +28.6% | +9.5% | +18.3% | +38.7% | -4.2% … +99.9% |
| topluluk | 7 | -6.3% | +4.4% | +42.9% | +0.0% | -5.6% | -31.8% | -20.4% … +1.3% |
| kural_A_gordu | 7 | +27.0% | +78.6% | +57.1% | +23.8% | +28.9% | +75.8% | +18.3% … +25.3% |
| kural_B_gordu | 7 | +31.2% | +84.5% | +57.1% | +23.8% | +33.5% | +106.6% | +18.3% … +32.5% |

- Yalnızca 7 çeyrek (6 aylıkta daha az); güven aralıkları geniş, tek başına karar için yetersiz.

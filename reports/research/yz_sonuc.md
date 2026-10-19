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

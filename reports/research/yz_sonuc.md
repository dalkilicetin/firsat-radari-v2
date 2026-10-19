# Yürüyen Modeller — Görülmemiş Veride Sonuçlar (geliştirme 2013–2024)

Her test yılı için model yalnızca etiketi o yıl başlamadan kapanmış verilerle eğitildi; ayarlar sabit. 2025–2026 kilitli.

| Model | İlk 3: ort. 3 ay | İlk 3: ort. 6 ay | İlk 3: S&P'yi geçen çeyrek | İlk 3 en iyi %5'te | İlk 10: ort. 3 ay | İlk 10: net bileşik yıllık | İlk 10 en kötü düşüş | İlk 3 − S&P (%90 GA) | İlk 3 − momentum (%90 GA) |
|---|---|---|---|---|---|---|---|---|---|
| rastgele | +3.3% | +7.7% | +39.6% | +6.2% | +4.6% | +13.5% | -37.7% | -3.7% … +2.7% | -14.6% … -0.4% |
| momentum_buyuk | +10.3% | +23.0% | +54.2% | +18.1% | +7.2% | +22.9% | -53.8% | +1.4% … +12.6% | — |
| kural_ogrenici | +9.8% | +15.9% | +63.0% | +15.2% | +9.1% | +33.0% | -27.2% | +3.7% … +8.5% | -5.6% … +4.6% |
| kural_A_gordu | +13.1% | +21.1% | +60.9% | +20.3% | +12.8% | +48.1% | -23.9% | +6.6% … +12.2% | -1.4% … +7.0% |
| kural_B_gordu | +17.8% | +27.5% | +69.0% | +24.2% | +17.0% | +59.8% | -26.4% | +7.8% … +21.8% | +0.0% … +14.5% |

- S&P 500: 3 ay +3.7%, 6 ay +6.9%. Gerçek en iyi 3: 3 ay +229.6%, 6 ay +242.6%.
- Rastgele beklenti: en iyi %5'te olma %5.
- Aşırı uyum olasılığı (PBO, öğrenen modeller arasında): —.
- Meta seçim (her yıl yalnızca geçmiş sonuçlara göre model seçimi, 2016–2024): ilk 3 ort. 3 ay +6.2%, 6 ay +16.1%. Seçimler: {2016: 'kural_ogrenici', 2017: 'kural_ogrenici', 2018: 'momentum_buyuk', 2019: 'momentum_buyuk', 2020: 'kural_ogrenici', 2021: 'momentum_buyuk', 2022: 'momentum_buyuk', 2023: 'momentum_buyuk', 2024: 'momentum_buyuk'}
- 'kural_A_gordu' / 'kural_B_gordu': geçmişin tamamına bakılarak bulunmuş kurallar; yalnızca kıyas, görülmemiş sayılmaz.

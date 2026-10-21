# S7 — Dibi bilmeden girmek: kademeli alım

> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** Yay mekanizmasını simülatöre biz koyduk.

Soru: dibi gerçek zamanda bulamıyorsak, tek seferde değil **kademe kademe** alarak ne kadarını kurtarırız? Her Y1 krizinde (bölüm başına bir) 252 bar sonraki değer ölçülür; kademeler eşit ağırlıklı. **ORACLE** sinyalden sonraki 126 barın gerçek dibine girer (bilinemez, üst sınır).
'Dibe uzaklık' = ortalama giriş fiyatının oracle diplerinden yüzde kaç yukarıda olduğu. RASTGELE: aynı yapıda rastgele bir günde tek seferlik giriş (piyasanın kendiliğinden yükselmesi tabanı).

| Strateji | n kriz | 252 bar getiri (ort.) [%90 GA] | medyan | pozitif oranı | dibe uzaklık |
|---|---|---|---|---|---|
| A: tek seferde Y1'de | 329 | 12.4% [9.8, 15.7] (n=329) | 11.6% | 71% | 17.9% |
| B: tek seferde Y2'de | 323 | 14.4% [11.8, 17.8] (n=323) | 14.9% | 72% | 15.7% |
| D: 3 kademe, 21'er bar arayla (Y1'den) | 329 | 12.7% [10.3, 15.7] (n=329) | 13.3% | 73% | 16.8% |
| E: Y1 + %5 daha düşünce + Y2 (3 kademe) | 329 | 12.0% [9.6, 14.9] (n=329) | 12.7% | 72% | 17.9% |
| F: 3 kademe, 21'er bar arayla (Y2'den) | 323 | 12.9% [10.5, 15.8] (n=323) | 14.0% | 73% | 16.3% |
| ORACLE: sinyalden sonraki gerçek dip (bilinemez) | 329 | 28.5% [25.7, 31.5] (n=329) | 25.5% | 88% | 0.0% |
| RASTGELE gün, tek seferde (taban) | 329 | 9.1% [6.6, 11.4] (n=329) | 7.2% | 61% | – |

## Okuma
- Tabana (rastgele gün) göre kazanç: Y1'de tek seferde 3.3%, Y2'de 5.3%, 3 kademe 3.6%, düşüşe duyarlı kademe 2.9%, **oracle 19.4%**.
- Dibi bilmenin değeri (oracle − en iyi kural tabanlı) ≈ 14.1%. Kademeli alım bunun ne kadarını kapatıyor, yukarıdaki satırlardan okunur.
- Ortalama giriş oracle dibinden Y1'de 17.9%, 3 kademede 16.8%, Y2'de 15.7% yukarıda: kademeli alım dibe yaklaşmayı **neredeyse hiç sağlamıyor**. Fiyat/VIX/genişlik işaretleriyle dibi gerçek zamanda yakalamak bu simülatörde de çözülmüyor; dibi bilmenin değeri başka bilgiye (şirket/sektör) bağlı olmalı.

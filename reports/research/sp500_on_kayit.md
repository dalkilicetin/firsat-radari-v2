# S&P 500'ü geçme hedefi — ön kayıt (2026-10-11, sonuçlara bakılmadan yazıldı)

Dal: `claude/sp500-hedefi`. Sürüm 3 (`claude/firsat-modeli`) dondurulmuş haliyle kalır.

## Başarı ölçütü

İç içe testte (2014–2025, 12 yıl; her yıl yalnızca o yıldan önceki verilerle işaret seçimi, yön ve model):

1. S&P 500'ü (SPY, temettü dahil) **en az 8/12 yılda** geçmek,
2. ortalama yıllık fazla getiri **≥ +2 puan** (maliyet sonrası).

## Neden şimdiki model S&P 500'ü güvenilir geçemiyor

S&P 500 piyasa değeriyle ağırlıklıdır; son yıllarda getirisini birkaç dev şirket taşıdı. Sürüm 3 tüm büyüklüklerden eşit
ağırlıklı 20 hisse seçiyor. Bu yüzden yöntemler büyük şirketlere ve/veya piyasa değeri ağırlığına yöneliyor.

## Denenecek yöntemler (liste sabit; yenisi eklenirse ayrıca kaydedilir)

Hepsinde: büyük şirket evreni = o tarihte piyasa değeri en büyük N faaliyet şirketi (yalnızca o güne kadar bilinen hisse
sayısı × fiyat). İşaretler sürüm 3 kuralıyla (yılların ≥ %70'inde aynı yön, ortalama/sapma ≥ 0,5) seçilir.

| Kod | Evren | İşaret seçimi | Puan | Portföy |
|---|---|---|---|---|
| S1 | en büyük 500 | sürüm 3 (tüm evrende ölçülen IC) | ridge | ilk 20, eşit ağırlık |
| S2 | en büyük 1000 | sürüm 3 | ridge | ilk 20, eşit ağırlık |
| S3 | en büyük 500 | büyük şirket evreninde ölçülen IC | ridge (büyük evrende eğitim) | ilk 20, eşit ağırlık |
| S4 | en büyük 500 | büyük şirket evreninde ölçülen IC | ridge (büyük evrende eğitim) | ilk 30, piyasa değeri ağırlığı |
| S5 | en büyük 500 | büyük şirket evreninde ölçülen IC | ridge (büyük evrende eğitim) | piyasa değeri ağırlığı × puan eğimi, ilk 100 |
| S6 | en büyük 500 | büyük şirket evreninde ölçülen IC | bileşik (öğrenmesiz) | ilk 20, eşit ağırlık |

Puan eğimi (S5): ağırlık ∝ piyasa değeri × (1 + 2·(puan yüzdeliği − 0,5)), yalnızca puanı en yüksek 100 hisse.

## Raporlama

Her yöntemin 12 yılı ayrı ayrı; ölçütü geçen olursa en basit olanı seçilir. Hiçbiri geçmezse sonuç olduğu gibi raporlanır.
Seçilen yöntem ayrıca canlı takiple doğrulanır.

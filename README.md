# Fırsat Radarı

Nasdaq hisseleri için haftalık potansiyel (0–100) ve risk (1–5) puanı üreten sistem.
Plan ve aşamalar: [PLAN.md](PLAN.md) · Bekleyen işler: [ACIK_LISTE.md](ACIK_LISTE.md)

## Canlı veri sağlığı (1. aşama)

Her kaynak çekilir, kalite kontrollerinden geçer; sonuç
[`reports/data_health/latest.md`](reports/data_health/latest.md).

```bash
pip install -r requirements.txt
python -m pytest -q
python -m radar.health                 # internet gerekir
python -m radar.health --only fred,gdelt
```

## Geçmiş veri arşivi (2. aşama)

2015'ten bugüne veriler Parquet bölümleri halinde GitHub Releases'teki `veri-arsivi` sürümündedir.
Her veri setinin bölümleri, satır sayıları, sha256 özetleri, kaynak adresleri ve kontrol sonuçları
`data/manifest/<veri seti>.json`, insan okunur raporu `reports/backfill/<veri seti>.md` dosyasındadır.

| Veri seti | İçerik | Bölüm |
|---|---|---|
| `insider` | SEC Form 4 içeriden işlemler | çeyrek |
| `financials` | SEC XBRL finansal tablolar (kabul anıyla) | çeyrek |
| `holdings` | SEC 13F kurumsal pozisyonlar | çeyrek / 3 aylık pencere |
| `filings` | SEC dosyalama geçmişi: 8-K olayları, borsadan çıkışlar | anlık görüntü |
| `ftd` | SEC fails-to-deliver: fiyat + CUSIP eşleştirmesi (`ftd__cusip_map`) | yıl |
| `prices` | Günlük fiyat (Yahoo; Nasdaq ile çapraz kontrol) | sembol grubu |
| `wikiviews` | Wikipedia günlük görüntülenme | sembol grubu |
| `gdelt` | GDELT kurum başına günlük haber sayısı ve ton (saatlik örneklem) | yıl |
| `fred` | 43 makro/emtia/sektör serisi | anlık görüntü |

Yeni yükleme istemek için `backfill-request.json` dosyasını düzenleyip gönderin; "Geçmiş Veri Yükleme"
iş akışı çalışır. Bir bölümü okumak:

```python
import pandas as pd
url = "https://github.com/dalkilicetin/firsat-radari-v2/releases/download/veri-arsivi/insider__2024q1.parquet"
df = pd.read_parquet(url)
```

Zaman kuralı: bir veri, kaynağın onu kamuya açtığı an itibarıyla bilinir (`accepted`, `available_date`).

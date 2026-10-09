# Fırsat Radarı

Nasdaq hisseleri için haftalık potansiyel (0–100) ve risk (1–5) puanı üreten sistem.
Plan ve aşamalar: [PLAN.md](PLAN.md).

## Şu anki aşama: 1 — Veri katmanı

Her kaynak çekilir, kalite kontrollerinden geçer ve sonuç
[`reports/data_health/latest.md`](reports/data_health/latest.md) dosyasına yazılır.

```bash
pip install -r requirements.txt
python -m pytest -q          # ayrıştırıcı testleri
python -m radar.health       # canlı veri sağlık raporu (internet gerekir)
python -m radar.health --only fred,gdelt
```

GitHub Actions bu kontrolü bu branch'e her kod değişikliğinde çalıştırır ve raporu branch'e geri yazar.

İsteğe bağlı secret'lar: `RADAR_USER_AGENT` (SEC için iletişim bilgisi),
`REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET`, `PATENTSVIEW_API_KEY`.

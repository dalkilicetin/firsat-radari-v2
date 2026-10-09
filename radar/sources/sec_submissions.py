"""SEC şirket dosya geçmişi (submissions API).

Her şirketin tüm dosyaları: form türü, dosyalama tarihi, SEC'e kabul anı (acceptanceDateTime)
ve 8-K'lar için olay kodları (items). 8-K kodları risk ve fırsat sinyalidir:
1.01 önemli anlaşma, 2.02 sonuç açıklaması, 3.01 borsadan çıkarılma uyarısı,
4.01 denetçi değişikliği, 5.02 yönetici değişikliği.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, datetime

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "sec_submissions", "SEC şirket dosya geçmişi", 1, [1, 3]

URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"

# Apple'ın 2023 mali yılı 10-K'sı 3 Kasım 2023'te dosyalandı.
GOLDEN_FILING = ("AAPL", "10-K", "2023-11-03")


def parse_recent(data: dict) -> list[dict]:
    recent = data["filings"]["recent"]
    keys = ["form", "filingDate", "acceptanceDateTime", "accessionNumber", "primaryDocument", "items", "reportDate"]
    n = len(recent["form"])
    return [{k: (recent.get(k) or [""] * n)[i] for k in keys} for i in range(n)]


def run(ctx: Context, rep: SourceReport) -> None:
    tickers = ["AAPL", "MSFT", "NVDA"] + ctx.sample_symbols(12, with_cik=True)
    filings_by_ticker: dict[str, list[dict]] = {}
    ticker_match = 0
    for t in tickers:
        cik = ctx.cik_by_ticker.get(t.replace(".", "-"))
        if not cik:
            continue
        data = ctx.client.get(URL.format(cik=cik)).json()
        filings_by_ticker[t] = parse_recent(data)
        if t.replace(".", "-") in [x.upper() for x in data.get("tickers", [])]:
            ticker_match += 1

    rep.expect_min_ratio("Çekilen şirket", len(filings_by_ticker), len(tickers), 1.0, 0.9)
    rep.expect_min_ratio("Çapraz kontrol: dosyadaki ticker evrendeki ticker ile aynı",
                         ticker_match, len(filings_by_ticker), 0.95, 0.85)

    aapl = filings_by_ticker.get("AAPL", [])
    t, form, day = GOLDEN_FILING
    found = any(f["form"] == form and f["filingDate"] == day for f in aapl)
    rep.add(f"Doğrulanmış gerçek: {t} {form} {day}", Status.OK if found else Status.FAIL,
            "bulundu" if found else "bulunamadı")

    all_filings = [f for fs in filings_by_ticker.values() for f in fs]
    eight_k = [f for f in all_filings if f["form"] == "8-K"]
    rep.expect_min_ratio("8-K'larda olay kodu (items) dolu", sum(1 for f in eight_k if f["items"]),
                         len(eight_k), 0.97, 0.9)

    consistent, bad = 0, []
    for f in all_filings:
        try:
            accepted = datetime.fromisoformat(f["acceptanceDateTime"].replace("Z", "+00:00")).date()
            filed = date.fromisoformat(f["filingDate"])
        except ValueError:
            continue
        # Kabul anı, dosyalama tarihiyle aynı gün ya da (17:30 sonrası kabullerde) bir gün önce olur.
        if 0 <= (filed - accepted).days <= 3:
            consistent += 1
        else:
            bad.append(f)
    check = rep.expect_min_ratio("Kabul anı ile dosyalama tarihi tutarlı (zaman damgası)", consistent, len(all_filings), 0.99, 0.95)
    if bad:
        check.detail += (f"; formlar: {dict(Counter(f['form'] for f in bad).most_common(6))}"
                         f"; örnek: {[(f['form'], f['filingDate'], f['acceptanceDateTime']) for f in bad[:4]]}")

    latest = max((f["filingDate"] for f in aapl), default=None)
    rep.expect_fresh("AAPL son dosya güncelliği", date.fromisoformat(latest) if latest else None, 45, ctx.today)

    with_10k = sum(1 for fs in filings_by_ticker.values() if any(f["form"] in ("10-K", "20-F", "40-F") for f in fs))
    rep.expect_min_ratio("Yıllık rapor (10-K/20-F/40-F) bulunan şirket", with_10k, len(filings_by_ticker), 0.85, 0.7)
    rep.sample = {t: fs[:3] for t, fs in list(filings_by_ticker.items())[:2]}

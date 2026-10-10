"""Hisse evreni: Nasdaq'ın resmî sembol listeleri (Nasdaq + NYSE + NYSE American) + SEC'in ticker→CIK eşleştirmesi.

Yeni halka arzlar, her çalışmada listeyi bir önceki anlık görüntüyle karşılaştırarak yakalanır.
"""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime

from radar import config
from radar.http import FetchError
from radar.quality import SourceReport, Status
from radar.sources.base import Context, Security

KEY, TITLE, TIER, ROADS = "universe", "Hisse evreni (Nasdaq + SEC)", 1, [1, 2, 3, 4]

NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
# Diğer borsalar (NYSE = N, NYSE American = A; Arca/BATS/IEX çoğunlukla ETF olduğundan alınmaz).
OTHER_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
OTHER_EXCHANGES = {"N", "A"}
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
SNAPSHOT = config.STATE_DIR / "universe.csv"

# Adi hisse olmayan menkul kıymetler (varant, hak, ünite, tercihli hisse, tahvil).
NON_COMMON = re.compile(
    r"\b(warrants?|rights?|units?|preferred|notes? due|debentures?|subordinated|depositary shares? representing .*preferred)\b",
    re.IGNORECASE,
)

# Nasdaq "Financial Status" kodları. N dışındakiler risk sinyalidir.
FINANCIAL_STATUS = {
    "N": "normal", "D": "yetersiz (deficient)", "E": "geciken rapor (delinquent)",
    "Q": "iflas", "G": "yetersiz+iflas", "H": "yetersiz+geciken", "J": "geciken+iflas",
    "K": "yetersiz+geciken+iflas",
}

GOLDEN_CIKS = {"AAPL": 320193, "MSFT": 789019, "NVDA": 1045810, "AMZN": 1018724}


def parse_nasdaq_listed(text: str) -> tuple[list[Security], datetime | None]:
    lines = text.strip().splitlines()
    created = None
    if lines and lines[-1].startswith("File Creation Time"):
        m = re.search(r"(\d{10}:\d{2})", lines[-1])
        if m:
            created = datetime.strptime(m.group(1), "%m%d%Y%H:%M")
        lines = lines[:-1]
    rows = csv.DictReader(io.StringIO("\n".join(lines)), delimiter="|")
    securities = []
    for r in rows:
        if r.get("Test Issue") == "Y":
            continue
        name = r["Security Name"]
        is_common = r.get("ETF") != "Y" and not NON_COMMON.search(name)
        securities.append(Security(
            symbol=r["Symbol"].strip(), name=name, market_category=r.get("Market Category", ""),
            financial_status=r.get("Financial Status", ""), is_common=is_common,
        ))
    return securities, created


def parse_other_listed(text: str) -> list[Security]:
    lines = [ln for ln in text.strip().splitlines() if not ln.startswith("File Creation Time")]
    out = []
    for r in csv.DictReader(io.StringIO("\n".join(lines)), delimiter="|"):
        if r.get("Test Issue") == "Y" or r.get("Exchange") not in OTHER_EXCHANGES:
            continue
        sym, name = r["ACT Symbol"].strip(), r["Security Name"]
        # "$" tercihli hisse, ".W"/".U"/".R" varant/ünite/hak sınıflarıdır.
        is_common = r.get("ETF") != "Y" and not NON_COMMON.search(name) and "$" not in sym \
            and not re.search(r"\.(W|WS|U|R|RT)$", sym)
        out.append(Security(symbol=sym, name=name, market_category="", financial_status="", is_common=is_common,
                            exchange=r["Exchange"]))
    return out


def listed_securities(client) -> list[Security]:
    """Nasdaq + NYSE + NYSE American; CIK'ler SEC eşleştirmesinden."""
    nasdaq, _ = parse_nasdaq_listed(client.get(NASDAQ_URL).text)
    other = parse_other_listed(client.get(OTHER_URL).text)
    secs = nasdaq + other
    sec = parse_sec_tickers(client.get(SEC_TICKERS_URL).json())
    for s in secs:
        hit = sec.get(normalize_symbol(s.symbol))
        s.cik = hit[0] if hit else None
    return secs


def parse_sec_tickers(data: dict) -> dict[str, tuple[int, str]]:
    """ticker -> (cik, borsa)."""
    fields = data["fields"]
    i_cik, i_ticker, i_exch = fields.index("cik"), fields.index("ticker"), fields.index("exchange")
    return {row[i_ticker].upper(): (int(row[i_cik]), row[i_exch] or "") for row in data["data"]}


def normalize_symbol(symbol: str) -> str:
    # Nasdaq "ABC.A" ya da "ABC A" yazabilir; SEC "ABC-A" kullanır.
    return re.sub(r"[.\s/]", "-", symbol.upper())


def read_snapshot() -> set[str]:
    if not SNAPSHOT.exists():
        return set()
    with SNAPSHOT.open() as f:
        return {row["symbol"] for row in csv.DictReader(f)}


def write_snapshot(securities: list[Security]) -> None:
    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    with SNAPSHOT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["symbol", "name", "cik", "market_category", "financial_status"])
        for s in sorted(securities, key=lambda s: s.symbol):
            if s.is_common:
                w.writerow([s.symbol, s.name, s.cik or "", s.market_category, s.financial_status])


def _new_listings(rep: SourceReport, common: list[Security]) -> None:
    previous = read_snapshot()
    current = {s.symbol for s in common}
    if previous:
        added, removed = sorted(current - previous), sorted(previous - current)
        rep.add("Yeni listelenen / çıkan hisseler (önceki çalışmaya göre)", Status.INFO,
                f"+{len(added)} yeni: {added[:30]} | -{len(removed)} çıkan: {removed[:30]}",
                {"added": added, "removed": removed})
    else:
        rep.add("Yeni listelenen / çıkan hisseler", Status.INFO, "ilk çalışma, karşılaştırılacak anlık görüntü yok")


def run(ctx: Context, rep: SourceReport) -> None:
    nasdaq = ctx.client.get(NASDAQ_URL)
    securities, created = parse_nasdaq_listed(nasdaq.text)
    common = [s for s in securities if s.is_common]

    rep.expect_range("Nasdaq adi hisse sayısı", len(common), 2500, 4500)
    rep.expect_fresh("Nasdaq listesi güncelliği", created, max_days=4)
    missing = [t for t in GOLDEN_CIKS if t not in {s.symbol for s in common}]
    rep.add("Bilinen hisseler listede", Status.FAIL if missing else Status.OK,
            f"eksik: {missing}" if missing else f"{len(GOLDEN_CIKS)}/{len(GOLDEN_CIKS)} bulundu")

    # SEC erişilemese bile Nasdaq listesi diğer kaynaklar için kullanılabilir kalsın.
    ctx.universe = securities
    try:
        sec = parse_sec_tickers(ctx.client.get(SEC_TICKERS_URL).json())
    except FetchError as exc:
        rep.add("SEC ticker→CIK eşleştirmesi", Status.FAIL, f"erişilemedi (HTTP {exc.status})")
        _new_listings(rep, common)
        write_snapshot(securities)
        return
    for s in securities:
        hit = sec.get(normalize_symbol(s.symbol))
        s.cik = hit[0] if hit else None
    mapped = [s for s in common if s.cik]
    rep.expect_min_ratio("SEC CIK eşleşme oranı", len(mapped), len(common), 0.92, 0.85, "adi hisse")
    wrong = {t: sec.get(t, (None,))[0] for t, cik in GOLDEN_CIKS.items() if sec.get(t, (None,))[0] != cik}
    rep.add("Doğrulanmış CIK değerleri", Status.FAIL if wrong else Status.OK,
            f"hatalı: {wrong}" if wrong else "AAPL, MSFT, NVDA, AMZN doğru")

    sec_nasdaq = {t for t, (_, exch) in sec.items() if exch == "Nasdaq"}
    ours = {normalize_symbol(s.symbol) for s in securities}
    rep.expect_min_ratio("Çapraz kontrol: SEC'te 'Nasdaq' görünenler Nasdaq listesinde",
                         len(sec_nasdaq & ours), len(sec_nasdaq), 0.95, 0.90)

    status_counts: dict[str, int] = {}
    for s in common:
        label = FINANCIAL_STATUS.get(s.financial_status, s.financial_status or "?")
        status_counts[label] = status_counts.get(label, 0) + 1
    rep.add("Finansal durum dağılımı (risk sinyali)", Status.INFO,
            ", ".join(f"{k}: {v}" for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1])), status_counts)

    _new_listings(rep, common)
    write_snapshot(securities)

    ctx.cik_by_ticker = {t: cik for t, (cik, _) in sec.items()}
    rep.sample = [vars(s) for s in common[:5]]

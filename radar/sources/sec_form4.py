"""SEC Form 4: şirket içindekilerin (yönetici, yönetim kurulu, %10+ ortak) hisse işlemleri.

İşlemden en geç 2 iş günü sonra dosyalanır. En güçlü sinyal "P" kodlu açık piyasa alımıdır.
Geriye dönük test için SEC'in üç aylık toplu veri setleri kullanılır; burada erişilebilirliği de test edilir.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import date

from radar.quality import SourceReport, Status
from radar.sources.base import Context

KEY, TITLE, TIER, ROADS = "sec_form4", "SEC Form 4 (içeriden işlemler)", 1, [3]

ARCHIVE = "https://www.sec.gov/Archives/"
BULK_PAGE = "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"

# P alım, S satış, A ödül/hibe, M opsiyon kullanımı, F vergi için elde tutma, G hediye, ...
VALID_CODES = set("PSAMFGDCEHIJKLOUVWXZ")


@dataclass
class Transaction:
    issuer_cik: int | None
    ticker: str
    owner: str
    is_director: bool
    is_officer: bool
    officer_title: str
    date: date | None
    code: str
    shares: float | None
    price: float | None
    acquired: str  # A (edinme) / D (elden çıkarma)
    owned_after: float | None


def _text(node: ET.Element | None, path: str) -> str:
    if node is None:
        return ""
    found = node.find(path)
    if found is None:
        return ""
    value = found.find("value")
    return ((value.text if value is not None else found.text) or "").strip()


def _num(s: str) -> float | None:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def extract_xml(full_submission: str, root_tag: str) -> str | None:
    m = re.search(rf"<{root_tag}[\s>].*?</{root_tag}>", full_submission, re.DOTALL)
    return m.group(0) if m else None


def parse_form4(xml: str) -> list[Transaction]:
    root = ET.fromstring(xml)
    issuer_cik = _num(_text(root, "issuer/issuerCik"))
    ticker = _text(root, "issuer/issuerTradingSymbol").upper()
    owner = root.find("reportingOwner")
    rel = owner.find("reportingOwnerRelationship") if owner is not None else None
    flag = lambda tag: _text(rel, tag).lower() in ("1", "true")
    txs = []
    for tx in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        raw_date = _text(tx, "transactionDate")[:10]
        txs.append(Transaction(
            issuer_cik=int(issuer_cik) if issuer_cik else None,
            ticker=ticker,
            owner=_text(owner, "reportingOwnerId/rptOwnerName"),
            is_director=flag("isDirector"),
            is_officer=flag("isOfficer"),
            officer_title=_text(rel, "officerTitle"),
            date=date.fromisoformat(raw_date) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date) else None,
            code=_text(tx, "transactionCoding/transactionCode"),
            shares=_num(_text(tx, "transactionAmounts/transactionShares")),
            price=_num(_text(tx, "transactionAmounts/transactionPricePerShare")),
            acquired=_text(tx, "transactionAmounts/transactionAcquiredDisposedCode"),
            owned_after=_num(_text(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction")),
        ))
    return txs


def run(ctx: Context, rep: SourceReport) -> None:
    form4 = [r for r in ctx.daily_index if r.form == "4"]
    if not form4:
        rep.add("Form 4 listesi", Status.FAIL, "SEC günlük indeksi boş; Form 4 örneklenemedi")
        return
    sample = ctx.rng.sample(form4, min(60, len(form4)))

    parsed = 0
    txs: list[tuple[date, Transaction]] = []
    for row in sample:
        text = ctx.client.get(ARCHIVE + row.path).text
        xml = extract_xml(text, "ownershipDocument")
        if not xml:
            continue
        try:
            for tx in parse_form4(xml):
                txs.append((row.filed, tx))
            parsed += 1
        except ET.ParseError:
            pass

    rep.expect_min_ratio("Ayrıştırılan Form 4", parsed, len(sample), 0.97, 0.9)
    rep.expect_min_ratio("Geçerli işlem kodu", sum(1 for _, t in txs if t.code in VALID_CODES), len(txs), 0.99, 0.95)
    rep.expect_min_ratio("İşlem tarihi ≤ dosyalama tarihi",
                         sum(1 for f, t in txs if t.date and t.date <= f), len(txs), 0.99, 0.95)
    rep.expect_min_ratio("Hisse adedi > 0", sum(1 for _, t in txs if t.shares and t.shares > 0), len(txs), 0.97, 0.9)
    ps = [t for _, t in txs if t.code in ("P", "S")]
    rep.expect_min_ratio("Alım/satışta fiyat > 0", sum(1 for t in ps if t.price and t.price > 0), len(ps), 0.97, 0.9)
    rep.expect_min_ratio("Kod/yön tutarlılığı (P→A, S→D)",
                         sum(1 for t in ps if (t.code, t.acquired) in (("P", "A"), ("S", "D"))), len(ps), 0.99, 0.95)
    rep.expect_min_ratio("Ticker dolu", sum(1 for _, t in txs if t.ticker), len(txs), 0.95, 0.85)

    codes = Counter(t.code for _, t in txs)
    rep.add("İşlem kodu dağılımı (örnek)", Status.INFO, ", ".join(f"{k}: {v}" for k, v in codes.most_common()))
    lag = sorted((f - t.date).days for f, t in txs if t.date)
    if lag:
        rep.add("Bildirim gecikmesi (gün, medyan / %95)", Status.INFO, f"{lag[len(lag) // 2]} / {lag[int(len(lag) * 0.95)]}")

    page = ctx.client.get(BULK_PAGE).text
    zips = sorted(set(re.findall(r'href="([^"]*form345[^"]*\.zip)"', page)))
    rep.expect_range("Toplu veri seti sayısı (geriye dönük test için)", len(zips), 40, 500)
    rep.add("Toplu veri seti örnekleri", Status.INFO, f"{zips[:2]} … {zips[-2:]}")
    rep.sample = [vars(t) | {"date": str(t.date)} for _, t in txs[:5]]

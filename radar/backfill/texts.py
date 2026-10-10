"""10-K metinleri: Madde 1 (iş tanımı), 1A (risk faktörleri), 7 (yönetimin değerlendirmesi).

Kaynak: her 10-K'nın ana belgesi (EDGAR arşivi). Evren: kimlik katmanındaki şirketler (bugün Nasdaq'ta olanlar
ve 2015 sonrası çıkanlar). Bölüm başlıkları içindekiler tablosunda da geçtiği için her başlığın en uzun
metni veren geçişi seçilir. Ayrıca tüm metinde "substantial doubt ... going concern" ifadesi aranır.
"""

from __future__ import annotations

import html
import re
from datetime import date

import pandas as pd

from radar.backfill.base import Dataset, Loaded
from radar.http import FetchError, HttpClient
from radar.quality import SourceReport, Status

FIRST_YEAR = 2014  # 2015 raporlarının yıldan yıla karşılaştırması için
MAX_CHARS = 250_000

HEADINGS = {
    "item1": r"item\s*1\s*[\.\:\-—–]?\s*business",
    "item1a": r"item\s*1a\s*[\.\:\-—–]?\s*risk\s*factors",
    "item1b": r"item\s*1b\s*[\.\:\-—–]?\s*unresolved",
    "item1c": r"item\s*1c\s*[\.\:\-—–]?\s*cybersecurity",
    "item2": r"item\s*2\s*[\.\:\-—–]?\s*properties",
    "item3": r"item\s*3\s*[\.\:\-—–]?\s*legal",
    "item7": r"item\s*7\s*[\.\:\-—–]?\s*management",
    "item7a": r"item\s*7a\s*[\.\:\-—–]?\s*quantitative",
    "item8": r"item\s*8\s*[\.\:\-—–]?\s*financial\s*statements",
}
KEEP = ["item1", "item1a", "item7"]
# Gerçek devamlılık uyarısı: "koşullar ... ciddi şüphe DOĞURMAKTADIR / ciddi şüphe VARDIR". Varsayımsal
# risk cümleleri ("şüphe doğabilir", "could raise") ve 2016'dan beri zorunlu muhasebe politikası metni
# ("yönetim ... şüphe olup olmadığını değerlendirir") sayılmaz.
GOING_CONCERN = re.compile(
    r"(raises?|raised|there\s+is|there\s+exists|exists)\s+substantial\s+doubt\s+(about|regarding|as\s+to|on)\s+"
    r"[^.]{0,60}?ability\s+to\s+continue\s+as\s+a\s+going\s+concern", re.I)
HYPOTHETICAL = re.compile(r"\b(could|may|might|would|will|can|if|whether|not)\b[^.]{0,40}$", re.I)


ALLEVIATED = re.compile(r"alleviat|mitigat|no\s+longer|has\s+been\s+resolved", re.I)


def has_going_concern(text: str) -> bool:
    """Kesin uyarı; aynı cümlede şüphenin 'giderildiği' (alleviated) belirtiliyorsa sayılmaz."""
    for m in GOING_CONCERN.finditer(text):
        before = text[max(0, m.start() - 60):m.start()]
        start = text.rfind(".", 0, m.start()) + 1
        end = text.find(".", m.end())
        sentence_after = text[m.end(): end if end != -1 else m.end() + 300]
        if HYPOTHETICAL.search(before) or ALLEVIATED.search(text[start:m.start()] + sentence_after):
            continue
        return True
    return False


def html_to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|ix:header)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h[1-6]|table)>", "\n", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    text = html.unescape(raw).replace("\xa0", " ")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()


def extract_sections(text: str) -> dict[str, str]:
    """Her başlığın tüm geçişlerini bulur; bölüm = başlıktan sonraki ilk başka başlığa kadar. En uzunu seçilir."""
    marks = []
    for key, pat in HEADINGS.items():
        for m in re.finditer(pat, text, re.I):
            marks.append((m.start(), key))
    marks.sort()
    best: dict[str, str] = {}
    for i, (pos, key) in enumerate(marks):
        nxt = next((p for p, k in marks[i + 1:] if k != key), len(text))
        body = text[pos:nxt]
        if len(body) > len(best.get(key, "")):
            best[key] = body
    return {k: best.get(k, "")[:MAX_CHARS] for k in KEEP}


def universe_ciks() -> set[int]:
    from radar.identity import build
    return set(build()["securities"].cik.astype(int))


class TenKTexts(Dataset):
    name = "tenk"
    title = "10-K metinleri (Madde 1, 1A, 7; 2014→)"
    max_parallel = 3

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [str(y) for y in range(FIRST_YEAR, today.year + 1)]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        from radar import archive
        f = archive.load("filings", columns=["cik", "form", "filing_date", "accepted", "accession", "primary_doc"])
        f = f[(f.form == "10-K") & (f.filing_date.dt.year == int(partition)) & f.cik.isin(universe_ciks())]
        rows, failed = [], 0
        for r in f.itertuples():
            url = f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{r.accession.replace('-', '')}/{r.primary_doc}"
            try:
                text = html_to_text(client.get(url, retries=2).text)
            except FetchError:
                failed += 1
                continue
            sec = extract_sections(text)
            rows.append({"cik": r.cik, "accession": r.accession, "filing_date": r.filing_date, "accepted": r.accepted,
                         "chars": len(text), "going_concern": has_going_concern(text), **sec})
        df = pd.DataFrame(rows)
        return Loaded(df, ["https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/<primary_doc>"],
                      {"filings": len(f), "failed": failed})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, n = loaded.df, loaded.notes["filings"]
        rep.expect_range("10-K sayısı", n, 1_500, 8_000)
        rep.expect_min_ratio("İndirilen", n - loaded.notes["failed"], n, 0.98, 0.9)
        if df.empty:
            return
        for k, ok_at in (("item1", 0.9), ("item1a", 0.8), ("item7", 0.85)):
            found = int((df[k].str.len() > 2_000).sum())
            rep.expect_min_ratio(f"{k} bulundu (>2.000 karakter)", found, len(df), ok_at, ok_at - 0.15)
        # Analitik bir bayrak: eşik dışı olması veriyi geçersiz kılmaz (uyarı).
        rep.expect_range("Devamlılık şüphesi oranı (substantial doubt)", float(df.going_concern.mean()), 0.01, 0.2, warn_only=True)
        aapl = df[df.cik == 320193]
        if len(aapl):
            ok = aapl.item1.str.contains("iPhone").any()
            rep.add("Doğrulama: Apple Madde 1'de 'iPhone' geçiyor", Status.OK if ok else Status.FAIL, "evet" if ok else "hayır")
        rep.add("Medyan uzunluk (karakter)", Status.INFO,
                ", ".join(f"{k}: {int(df[k].str.len().median()):,}" for k in KEEP))

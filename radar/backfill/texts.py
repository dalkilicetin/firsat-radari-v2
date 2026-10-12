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

FIRST_YEAR = 2008  # 2009 raporlarının yıldan yıla karşılaştırması için
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
    title = "10-K metinleri (Madde 1, 1A, 7; 2008→)"
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


# --- Bilanço basın bültenleri (8-K Madde 2.02, EX-99.1) — yalnızca sayısal metin özellikleri saklanır -------------------

LM_POS = set("""achieve achieved achievement attractive beat beneficial benefit best better boost breakthrough exceed exceeded exceeding
excellent exceptional favorable gain gained gains great greater growth highest improve improved improvement improving increase
increased momentum outperform outperformed positive profitable progress record records robust solid strength strengthen strong
stronger strongest success successful surpass surpassed upside""".split())
LM_NEG = set("""adverse adversely challenging challenge challenges decline declined declines declining decrease decreased deficit
deteriorate deteriorated deterioration difficult disappoint disappointing downturn impairment impaired loss losses lower negative
pressure pressures restructuring shortfall slowdown slowed slower soft softer softness unfavorable weak weaker weakness
headwind headwinds delay delayed uncertainty volatile""".split())
GUIDE = r"(?:guidance|outlook|forecast|full[- ]year (?:revenue|earnings|eps)|fiscal (?:year )?20\d\d (?:revenue|earnings|eps))"
UP = re.compile(r"\b(?:rais(?:e|es|ed|ing)|increas(?:e|es|ed|ing)|improv(?:e|es|ed|ing)|lift(?:s|ed)?|boost(?:s|ed)?|"
                r"upgrad(?:e|ed|ing))\b(?:\W+\w+){0,6}?\W+" + GUIDE, re.IGNORECASE)
DOWN = re.compile(r"\b(?:lower(?:s|ed|ing)?|reduc(?:e|es|ed|ing)|cut(?:s|ting)?|withdr(?:aw|ew|awn|awing)|suspend(?:s|ed|ing)?|"
                  r"narrow(?:s|ed)?\W+(?:\w+\W+){0,3}?(?:low|bottom))\b(?:\W+\w+){0,6}?\W+" + GUIDE, re.IGNORECASE)
WORD_RE = re.compile(r"[a-z]+")


def release_features(text: str) -> dict:
    t = text[:200_000]
    words = WORD_RE.findall(t.lower())
    n = max(len(words), 1)
    pos = sum(w in LM_POS for w in words)
    neg = sum(w in LM_NEG for w in words)
    return {"kelime": len(words), "olumlu": pos / n, "olumsuz": neg / n, "ton": (pos - neg) / max(pos + neg, 1),
            "rehberlik_yukari": len(UP.findall(t)), "rehberlik_asagi": len(DOWN.findall(t)),
            "rekor": len(re.findall(r"\brecord\b", t, re.IGNORECASE)),
            "beklenti_ustu": len(re.findall(r"\b(?:exceed(?:ed|s)?|above|ahead of|beat)\b\W+(?:\w+\W+){0,3}?(?:expectations|guidance|consensus)",
                                            t, re.IGNORECASE))}


class EarningsReleases(Dataset):
    """8-K Madde 2.02 basın bültenleri (EX-99.1): ton, rehberlik yükseltme/düşürme, rekor ve beklenti üstü ifadeleri.
    Ham metin saklanmaz; bülten başına sayısal özellikler. Point-in-time: SEC kabul zamanı."""
    name = "bilanco_bulteni"
    title = "Bilanço basın bültenleri — metin özellikleri (8-K 2.02, 2009→)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"{y}h{h}" for y in range(2009, today.year + 1) for h in (1, 2) if date(y, 1 if h == 1 else 7, 1) <= today]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        from radar import archive
        year, half = int(partition[:4]), int(partition[-1])
        f = archive.load("filings", columns=["cik", "form", "filing_date", "accepted", "accession", "primary_doc", "items"])
        f = f[(f.form == "8-K") & f["items"].fillna("").str.contains(r"\b2\.02\b") & (f.filing_date.dt.year == year)
              & ((f.filing_date.dt.month <= 6) == (half == 1)) & f.cik.isin(universe_ciks())]
        rows, failed = [], 0
        for r in f.itertuples():
            base = f"https://www.sec.gov/Archives/edgar/data/{r.cik}/{r.accession.replace('-', '')}"
            try:
                items = client.get(base + "/index.json", retries=2).json().get("directory", {}).get("item", [])
                names = [i["name"] for i in items if re.search(r"ex-?99(?:[._-]?0?1)?\D", i["name"].lower() + ".")
                         and i["name"].lower().endswith((".htm", ".html", ".txt"))]
                doc = names[0] if names else r.primary_doc
                text = html_to_text(client.get(f"{base}/{doc}", retries=2).text)
            except (FetchError, ValueError, KeyError):
                failed += 1
                continue
            rows.append({"cik": r.cik, "accession": r.accession, "filing_date": r.filing_date, "accepted": r.accepted,
                         "ek99": bool(names), **release_features(text)})
        return Loaded(pd.DataFrame(rows), ["https://www.sec.gov/Archives/edgar/data/<cik>/<accession>/<ex99.1>"],
                      {"filings": len(f), "failed": failed})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, n = loaded.df, loaded.notes["filings"]
        rep.expect_min_ratio("İndirilen bülten", n - loaded.notes["failed"], max(n, 1), 0.97, 0.9)
        if df.empty:
            return
        rep.expect_min_ratio("EX-99 bulundu", int(df.ek99.sum()), len(df), 0.85, 0.7)
        rep.add("Rehberlik yükseltme geçen bülten", Status.INFO, f"%{(df.rehberlik_yukari > 0).mean() * 100:.1f}")
        rep.add("Rehberlik düşürme geçen bülten", Status.INFO, f"%{(df.rehberlik_asagi > 0).mean() * 100:.1f}")
        rep.add("Medyan kelime", Status.INFO, f"{int(df.kelime.median()):,}")

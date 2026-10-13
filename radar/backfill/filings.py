"""SEC dosyalama geçmişi (submissions toplu dosyası) ve GDELT haber geçmişi.

Dosyalama geçmişi: her şirketin tüm dosyaları, SEC kabul anı ve 8-K olay kodlarıyla. Ayrıca
Form 25 (borsadan çıkarılma) ve Form 15 (kayıt sonlandırma) borsadan çıkış tarihlerini verir;
geriye dönük testte hayatta kalan yanılgısını önlemek için gerekir.

GDELT: 2015-02-19'dan bu yana her saatin ilk 15 dakikalık GKG dosyası örneklenir (günde 24 dosya, akışın ~%25'i);
her gün için kurum adı başına makale sayısı ve ortalama ton tutulur. Küçük şirketler kaybolmasın diye
günde bir kez geçen kurumlar da tutulur. Not: GDELT bazı şirketleri yalnızca tam adıyla kodlar
("apple" değil "apple inc"); kurum → şirket eşleştirmesi isim listeleriyle 3. aşamada yapılır.
"""

from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import pandas as pd
import requests

from radar import config
from radar.backfill.base import Dataset, Loaded
from radar.http import HttpClient
from radar.quality import SourceReport, Status
from radar.sources import gdelt

SUBMISSIONS_ZIP = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
FORMS = {"8-K", "8-K/A", "10-K", "10-K/A", "10-Q", "20-F", "40-F", "6-K", "NT 10-K", "NT 10-Q", "S-1", "S-1/A", "F-1",
         "424B4", "DEF 14A", "SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A", "SCHEDULE 13D", "SCHEDULE 13D/A",
         "SCHEDULE 13G", "SCHEDULE 13G/A", "25-NSE", "25", "15-12B", "15-12G", "15-15D"}
PERIODIC = {"10-K", "10-Q", "20-F", "40-F"}  # faaliyet gösteren şirketi belirler
# Hisse satışı izahnameleri ve kayıt beyanları (ön kayıt v1.2, bölüm 6.3: ters bölünme sonrası ihraç belgesi)
ISSUE_FORMS = {"424B1", "424B2", "424B3", "424B4", "424B5", "424B7", "S-1", "F-1", "S-3", "S-3/A", "F-3", "F-3/A",
               "S-3ASR", "F-3ASR", "S-1/A", "F-1/A"}
# Borsadan çıkışı bildiren formlar.
DELIST_FORMS = {"25-NSE", "25", "15-12B", "15-12G", "15-15D"}


def parse_submission(data: dict, forms_wanted: set[str] = FORMS) -> list[dict]:
    """Bir şirketin submissions JSON'u (ya da ek sayfası) → dosya satırları."""
    block = data.get("filings", {}).get("recent", data)  # ek sayfalarda doğrudan sütunlar vardır
    forms = block.get("form") or []
    rows = []
    for i, form in enumerate(forms):
        if form not in forms_wanted:
            continue
        get = lambda k: (block.get(k) or [""] * len(forms))[i]
        rows.append({"form": form, "filing_date": get("filingDate"), "accepted": get("acceptanceDateTime"),
                     "accession": get("accessionNumber"), "items": get("items"), "report_date": get("reportDate"),
                     "primary_doc": get("primaryDocument")})
    return rows


class Filings(Dataset):
    name = "filings"
    title = "SEC dosyalama geçmişi (8-K olayları, borsadan çıkışlar)"
    max_parallel = 1
    forms = FORMS

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"snapshot-{today:%Y%m%d}"]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        path = config.DATA_DIR / "backfill" / "submissions.zip"
        path.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(SUBMISSIONS_ZIP, headers={"User-Agent": config.USER_AGENT}, stream=True, timeout=600) as r:
            r.raise_for_status()
            with path.open("wb") as f:
                for chunk in r.iter_content(1 << 22):
                    f.write(chunk)
        companies, rows, operating = {}, [], set()
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if not name.endswith(".json"):
                    continue
                cik = int(name[3:13])
                data = json.loads(zf.read(name))
                if "filings" in data:
                    companies[cik] = {"name": data.get("name", ""), "tickers": ",".join(data.get("tickers") or []),
                                      "exchanges": ",".join(e or "" for e in data.get("exchanges") or []),
                                      "sic": data.get("sic", ""), "category": data.get("category", "")}
                for row in parse_submission(data, self.forms | PERIODIC):
                    if row["filing_date"] < "2008":  # 2009 başlangıcı için ön tampon
                        continue
                    row["cik"] = cik
                    rows.append(row)
                    if row["form"] in ("10-K", "10-Q", "20-F", "40-F"):
                        operating.add(cik)
        path.unlink()
        df = pd.DataFrame(rows)
        df = df[df.cik.isin(operating) & df.form.isin(self.forms)]  # yalnızca faaliyet gösteren (periyodik rapor veren) şirketler
        meta = pd.DataFrame.from_dict(companies, orient="index").rename_axis("cik").reset_index()
        df = df.merge(meta, on="cik", how="left")
        df["filing_date"] = pd.to_datetime(df.filing_date, errors="coerce")
        df["accepted"] = pd.to_datetime(df.accepted, errors="coerce", utc=True)
        df["report_date"] = pd.to_datetime(df.report_date, errors="coerce")
        return Loaded(df, [SUBMISSIONS_ZIP], {"companies": len(operating)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        rep.expect_range("Faaliyet gösteren şirket", loaded.notes["companies"], 8_000, 60_000)
        rep.expect_range("Dosya satırı", len(df), 1_000_000, 30_000_000)
        eight_k = df[df.form == "8-K"]
        recent = eight_k[eight_k.filing_date >= "2015-01-01"]
        rep.expect_min_ratio("2015 sonrası 8-K'larda olay kodu dolu", int((recent["items"] != "").sum()), len(recent), 0.97, 0.9)
        rep.expect_min_ratio("Kabul anı okunabilen", int(df.accepted.notna().sum()), len(df), 0.99, 0.95)
        aapl = df[(df.cik == 320193) & (df.form == "10-K") & (df.filing_date == "2023-11-03")]
        rep.add("Doğrulanmış gerçek: AAPL 10-K 2023-11-03", Status.OK if len(aapl) else Status.FAIL, "bulundu" if len(aapl) else "yok")
        delist = df[df.form.isin(DELIST_FORMS) & (df.filing_date >= "2015-01-01")]
        rep.add("2015 sonrası borsadan çıkış / kayıt sonlandırma bildirimi", Status.INFO,
                f"{delist.cik.nunique():,} şirket ({delist.form.value_counts().to_dict()})")
        for cik, label in ((719739, "SVB Financial"), (718877, "Activision Blizzard"), (1060736, "Seagen")):
            hit = df[(df.cik == cik) & df.form.isin(DELIST_FORMS)]
            rep.add(f"Borsadan çıkış kaydı: {label}", Status.OK if len(hit) else Status.WARN,
                    f"{sorted(hit.form + ' ' + hit.filing_date.dt.strftime('%Y-%m-%d'))[:3] or 'yok'}")


class IssuanceFilings(Filings):
    """Hisse satışı izahnameleri (424B*) ve kayıt beyanları (S-1, S-3, F-1, F-3). Dosyalama geçmişinden ayrı tutulur;
    böylece mevcut çerçevenin girdisi değişmez."""
    name = "ihrac_belgeleri"
    title = "SEC hisse satışı izahnameleri ve kayıt beyanları (424B*, S-1/S-3/F-1/F-3)"
    forms = ISSUE_FORMS

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        rep.expect_range("Faaliyet gösteren şirket", loaded.notes["companies"], 8_000, 60_000)
        rep.expect_range("Dosya satırı", len(df), 50_000, 5_000_000)
        rep.expect_min_ratio("Kabul anı okunabilen", int(df.accepted.notna().sum()), len(df), 0.99, 0.95)
        counts = df.form.value_counts().to_dict()
        rep.add("Form dağılımı", Status.INFO, str(counts))
        for f in ("424B5", "S-3", "424B3"):
            rep.add(f"{f} kaydı var", Status.OK if counts.get(f, 0) > 1000 else Status.FAIL, f"{counts.get(f, 0):,}")


SLOT_HOURS = list(range(24))
GKG_START = date(2015, 2, 19)


def gkg_url(d: date, hour: int) -> str:
    return f"http://data.gdeltproject.org/gdeltv2/{d:%Y%m%d}{hour:02d}0000.gkg.csv.zip"


def _fetch(url: str) -> bytes | None:
    for _ in range(3):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 404:
                return None
            if r.ok:
                return r.content
        except requests.RequestException:
            pass
    return None


def aggregate_gkg(blob: bytes) -> tuple[pd.DataFrame, int]:
    rows = gdelt.read_gkg(blob)
    records = []
    for r in rows:
        if len(r) != gdelt.GKG_COLUMNS or not r[gdelt.COL_ORGS]:
            continue
        try:
            tone = float(r[gdelt.COL_TONE].split(",")[0])
        except ValueError:
            continue
        for org in set(r[gdelt.COL_ORGS].split(";")):
            if org:
                records.append((org, tone))
    df = pd.DataFrame(records, columns=["org", "tone"])
    return df, len(rows)


class GdeltHistory(Dataset):
    name = "gdelt"
    title = "GDELT haber geçmişi (kurum başına günlük makale ve ton, örneklem)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [str(y) for y in range(2015, today.year + 1)]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        year = int(partition)
        start = max(date(year, 1, 1), GKG_START)
        end = min(date(year, 12, 31), date.today() - timedelta(days=1))
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        slots = len(days) * len(SLOT_HOURS)
        daily_frames, articles, missing = [], {}, 0
        buffer: list[pd.DataFrame] = []

        def flush(day: date) -> None:
            # Bellek için her günün dosyaları birleşince hemen özetlenir.
            if buffer:
                agg = pd.concat(buffer).groupby("org").tone.agg(["size", "mean"]).reset_index()
                agg.columns = ["org", "mentions", "tone"]
                agg.insert(0, "date", pd.Timestamp(day))
                daily_frames.append(agg)
                buffer.clear()

        # Gün gün indir: aynı anda bellekte en fazla bir günün dosyaları (24) bulunur.
        with ThreadPoolExecutor(max_workers=8) as pool:
            for d in days:
                day_urls = [gkg_url(d, h) for h in SLOT_HOURS]
                for blob in pool.map(_fetch, day_urls):
                    if blob is None:
                        missing += 1
                        continue
                    try:
                        orgs, n = aggregate_gkg(blob)
                    except (zipfile.BadZipFile, ValueError, csv.Error):
                        missing += 1
                        continue
                    articles[d] = articles.get(d, 0) + n
                    buffer.append(orgs)
                flush(d)
        daily = pd.concat(daily_frames, ignore_index=True)
        totals = pd.DataFrame({"date": pd.to_datetime(list(articles)), "org": "__TOPLAM_MAKALE__",
                               "mentions": list(articles.values()), "tone": float("nan")})
        df = pd.concat([daily, totals], ignore_index=True)
        return Loaded(df, ["http://data.gdeltproject.org/gdeltv2/<YYYYMMDDHH0000>.gkg.csv.zip"],
                      {"slots": slots, "missing": missing, "days": len(days)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        rep.expect_min_ratio("İndirilen örneklem dosyası", notes["slots"] - notes["missing"], notes["slots"], 0.97, 0.9)
        totals = df[df.org == "__TOPLAM_MAKALE__"]
        rep.expect_min_ratio("Makale verisi olan gün", len(totals), notes["days"], 0.99, 0.95)
        if len(totals):
            rep.expect_range("Gün başına örneklenen makale (medyan)", float(totals.mentions.median()), 10_000, 120_000)
        orgs = df[df.org != "__TOPLAM_MAKALE__"]
        top = orgs.groupby("org").mentions.sum().nlargest(8)
        rep.add("Yılın en çok geçen kurumları", Status.INFO, ", ".join(f"{o} ({n:,})" for o, n in top.items()))
        for org in ("apple inc", "microsoft", "nvidia"):
            days = orgs[orgs.org == org].date.nunique()
            rep.add(f"'{org}' geçen gün", Status.OK if days > 0.5 * notes["days"] else Status.WARN, f"{days}/{notes['days']}")


COL_THEMES = 7


class GdeltThemes(Dataset):
    """GDELT tema geçmişi (4. yol için).

    Aynı saatlik örneklemden iki tablo üretilir (kind sütunu):
    - day_theme: gün × tema → makale sayısı (tema ivmesi için)
    - month_cik_theme: ay × şirket × tema → şirketin adının geçtiği makalelerde temanın sayısı
      (şirketin tema maruziyeti; kurum adı → şirket eşleştirmesi radar.research.road2.aliases ile)
    """
    name = "gdelt_themes"
    title = "GDELT tema geçmişi (günlük tema sayıları + şirket-tema maruziyeti)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [str(y) for y in range(2015, today.year + 1)]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        from collections import Counter
        from radar.identity import build
        from radar.research.road2 import aliases
        alias = dict(aliases(build()["securities"]).itertuples(index=False, name=None))
        year = int(partition)
        start = max(date(year, 1, 1), GKG_START)
        end = min(date(year, 12, 31), date.today() - timedelta(days=1))
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        day_rows, month_pairs, missing = [], Counter(), 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            for d in days:
                themes_today = Counter()
                for blob in pool.map(_fetch, [gkg_url(d, h) for h in SLOT_HOURS]):
                    if blob is None:
                        missing += 1
                        continue
                    try:
                        rows = gdelt.read_gkg(blob)
                    except (zipfile.BadZipFile, ValueError, csv.Error):
                        missing += 1
                        continue
                    month = d.replace(day=1)
                    for r in rows:
                        if len(r) != gdelt.GKG_COLUMNS or not r[COL_THEMES]:
                            continue
                        themes = {t for t in r[COL_THEMES].split(";") if t}
                        themes_today.update(themes)
                        ciks = {alias[o] for o in r[gdelt.COL_ORGS].split(";") if o in alias}
                        for c in ciks:
                            for t in themes:
                                month_pairs[(month, c, t)] += 1
                day_rows += [(d, None, t, n) for t, n in themes_today.items() if n >= 3]
        mrows = [(m, c, t, n) for (m, c, t), n in month_pairs.items() if n >= 2]
        df = pd.DataFrame(
            [("day_theme",) + r for r in day_rows] + [("month_cik_theme",) + r for r in mrows],
            columns=["kind", "date", "cik", "theme", "count"])
        df["date"] = pd.to_datetime(df.date)
        df["cik"] = df.cik.astype("Int64")
        return Loaded(df, ["http://data.gdeltproject.org/gdeltv2/<YYYYMMDDHH0000>.gkg.csv.zip"],
                      {"slots": len(days) * len(SLOT_HOURS), "missing": missing, "days": len(days)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        rep.expect_min_ratio("İndirilen örneklem dosyası", notes["slots"] - notes["missing"], notes["slots"], 0.97, 0.9)
        day = df[df.kind == "day_theme"]
        rep.expect_min_ratio("Tema verisi olan gün", day.date.nunique(), notes["days"], 0.99, 0.95)
        pairs = df[df.kind == "month_cik_theme"]
        rep.expect_range("Tema maruziyeti olan şirket", pairs.cik.nunique(), 300, 6000)
        top = day.groupby("theme")["count"].sum().nlargest(8)
        rep.add("En sık temalar", Status.INFO, ", ".join(f"{t} ({n:,})" for t, n in top.items()))
        nv = pairs[pairs.cik == 1045810].groupby("theme")["count"].sum().nlargest(5)
        rep.add("Örnek: NVIDIA'nın en yoğun temaları", Status.INFO, ", ".join(nv.index) or "yok")


# Adres (URL) kelimelerinde anlamsız/genel sözcükler.
URL_STOP = set("""html htm index article articles news story stories world business markets market www com php aspx
amp the and for with from that this have will your about after over into more than says said year years new week
2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 2026 video watch live update updates report reports latest
local national politics sport sports opinion home page content posts post blog category tag tags""".split())


def url_words(url: str) -> set[str]:
    """Haber adresinin yol kısmındaki kelimeler (ör. .../nvidia-openai-chatgpt-deal → nvidia, openai, chatgpt, deal)."""
    path = url.split("://", 1)[-1].split("/", 1)[-1].lower()
    return {w for w in re.split(r"[^a-z0-9]+", path) if 4 <= len(w) <= 24 and not w.isdigit() and w not in URL_STOP
            and not re.fullmatch(r"[0-9a-f]{8,}", w)}


class GdeltWords(Dataset):
    """Yeni konuları keşfetmek için GDELT'in sabit tema sınıflaması dışındaki sinyaller (2015→).

    Aynı saatlik örneklemden (kind sütunu):
    - month_word: ay × adres kelimesi → bütün haberlerde geçiş sayısı (≥ 20)
    - month_cik_word: ay × şirket × adres kelimesi → şirketin adının geçtiği haberlerde (şirket başına en sık 60)
    - month_cik_org: ay × şirket × birlikte anılan kurum → (şirket başına en sık 40)
    Yeni kavramlar (ör. 'chatgpt', 'openai', 'glp1') sınıflamada yokken adreslerde ve kurum adlarında görünür.
    """
    name = "gdelt_words"
    title = "GDELT adres kelimeleri ve birlikte anılan kurumlar (yeni konu keşfi)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [str(y) for y in range(2015, today.year + 1)]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        from collections import Counter, defaultdict
        from radar.identity import build
        from radar.research.road2 import aliases
        alias = dict(aliases(build()["securities"]).itertuples(index=False, name=None))
        year = int(partition)
        start = max(date(year, 1, 1), GKG_START)
        end = min(date(year, 12, 31), date.today() - timedelta(days=1))
        days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
        month_words: dict = defaultdict(Counter)
        cik_words: dict = defaultdict(Counter)
        cik_orgs: dict = defaultdict(Counter)
        missing = 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            for d in days:
                month = d.replace(day=1)
                for blob in pool.map(_fetch, [gkg_url(d, h) for h in SLOT_HOURS]):
                    if blob is None:
                        missing += 1
                        continue
                    try:
                        rows = gdelt.read_gkg(blob)
                    except (zipfile.BadZipFile, ValueError, csv.Error):
                        missing += 1
                        continue
                    for r in rows:
                        if len(r) != gdelt.GKG_COLUMNS:
                            continue
                        words = url_words(r[gdelt.COL_URL])
                        month_words[month].update(words)
                        orgs = [o for o in r[gdelt.COL_ORGS].split(";") if o]
                        ciks = {alias[o] for o in orgs if o in alias}
                        for c in ciks:
                            cik_words[(month, c)].update(words)
                            cik_orgs[(month, c)].update(o for o in set(orgs) if alias.get(o) != c)
        rows = [("month_word", m, None, w, n) for m, cnt in month_words.items() for w, n in cnt.items() if n >= 20]
        rows += [("month_cik_word", m, c, w, n) for (m, c), cnt in cik_words.items() for w, n in cnt.most_common(60) if n >= 2]
        rows += [("month_cik_org", m, c, o, n) for (m, c), cnt in cik_orgs.items() for o, n in cnt.most_common(40) if n >= 2]
        df = pd.DataFrame(rows, columns=["kind", "date", "cik", "token", "count"])
        df["date"] = pd.to_datetime(df.date)
        df["cik"] = df.cik.astype("Int64")
        return Loaded(df, ["http://data.gdeltproject.org/gdeltv2/<YYYYMMDDHH0000>.gkg.csv.zip"],
                      {"slots": len(days) * len(SLOT_HOURS), "missing": missing, "days": len(days)})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df, notes = loaded.df, loaded.notes
        rep.expect_min_ratio("İndirilen örneklem dosyası", notes["slots"] - notes["missing"], notes["slots"], 0.97, 0.9)
        cw = df[df.kind == "month_cik_word"]
        rep.expect_range("Kelime verisi olan şirket", cw.cik.nunique(), 300, 8000)
        nv = cw[cw.cik == 1045810].groupby("token")["count"].sum().nlargest(8)
        rep.add("Örnek: NVIDIA haber adreslerinde en sık kelimeler", Status.INFO, ", ".join(nv.index) or "yok")
        co = df[(df.kind == "month_cik_org") & (df.cik == 1045810)].groupby("token")["count"].sum().nlargest(8)
        rep.add("Örnek: NVIDIA ile birlikte anılan kurumlar", Status.INFO, ", ".join(co.index) or "yok")

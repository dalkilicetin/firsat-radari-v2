"""SEC Insider Transactions Data Sets (Form 3/4/5), çeyreklik toplu dosyalar.

Kullanılabilirlik: toplu dosyada SEC kabul anı yok; dosyalama tarihinden 1 iş günü sonrasını
"bilinme tarihi" sayıyoruz (gece yarısından sonra kabul edilip önceki güne tarihlenen dosyalar için güvenli taraf).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from radar.backfill.base import Dataset, Loaded, links, quarter_bounds, read_zip_member, require, to_date, to_number
from radar.http import HttpClient
from radar.quality import SourceReport, Status
from radar.sources import sec_form4

PAGE = "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"
FIRST = "2009q1"


class InsiderTransactions(Dataset):
    name = "insider"
    title = "SEC içeriden işlemler (Form 4, 2009→)"
    max_parallel = 3

    def _links(self, client: HttpClient) -> dict[str, str]:
        return links(client, PAGE, r"(\d{4}q[1-4])_form345\.zip")

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return sorted(p for p in self._links(client) if p >= FIRST)

    def load(self, client: HttpClient, partition: str) -> Loaded:
        url = self._links(client)[partition]
        blob = client.get(url, timeout=300).content
        sub = read_zip_member(blob, "SUBMISSION.tsv")
        owners = read_zip_member(blob, "REPORTINGOWNER.tsv")
        trans = read_zip_member(blob, "NONDERIV_TRANS.tsv")
        require(sub, ["ACCESSION_NUMBER", "FILING_DATE", "DOCUMENT_TYPE", "ISSUERCIK", "ISSUERTRADINGSYMBOL"], "SUBMISSION")
        require(owners, ["ACCESSION_NUMBER", "RPTOWNERCIK", "RPTOWNERNAME", "RPTOWNER_RELATIONSHIP"], "REPORTINGOWNER")
        require(trans, ["ACCESSION_NUMBER", "TRANS_DATE", "TRANS_CODE", "TRANS_SHARES", "TRANS_PRICEPERSHARE",
                        "TRANS_ACQUIRED_DISP_CD", "SHRS_OWND_FOLWNG_TRANS"], "NONDERIV_TRANS")

        # Bir dosyada birden çok raporlayan olabilir; ilkini ve tüm ilişkileri tutuyoruz.
        owners = owners.groupby("ACCESSION_NUMBER", sort=False).agg(
            owner_cik=("RPTOWNERCIK", "first"), owner_name=("RPTOWNERNAME", "first"),
            relationship=("RPTOWNER_RELATIONSHIP", lambda s: ",".join(sorted({x for v in s for x in v.split(",") if x}))),
            owner_title=("RPTOWNER_TITLE", "first") if "RPTOWNER_TITLE" in owners.columns else ("RPTOWNERNAME", lambda s: ""),
            n_owners=("RPTOWNERCIK", "size"),
        ).reset_index()

        df = trans.merge(sub, on="ACCESSION_NUMBER", how="left").merge(owners, on="ACCESSION_NUMBER", how="left")
        filing = to_date(df["FILING_DATE"], "%d-%b-%Y")
        out = pd.DataFrame({
            "accession": df["ACCESSION_NUMBER"],
            "form": df["DOCUMENT_TYPE"],
            "filing_date": filing,
            "available_date": filing + pd.offsets.BDay(1),
            "issuer_cik": pd.to_numeric(df["ISSUERCIK"], errors="coerce").astype("Int64"),
            "ticker": df["ISSUERTRADINGSYMBOL"].str.strip().str.upper(),
            "owner_cik": pd.to_numeric(df["owner_cik"], errors="coerce").astype("Int64"),
            "owner_name": df["owner_name"],
            "relationship": df["relationship"],
            "owner_title": df["owner_title"],
            "n_owners": df["n_owners"].astype("Int64"),
            "trans_date": to_date(df["TRANS_DATE"], "%d-%b-%Y"),
            "code": df["TRANS_CODE"].str.strip(),
            "shares": to_number(df["TRANS_SHARES"]),
            "price": to_number(df["TRANS_PRICEPERSHARE"]),
            "acq_disp": df["TRANS_ACQUIRED_DISP_CD"].str.strip(),
            "owned_after": to_number(df["SHRS_OWND_FOLWNG_TRANS"]),
            "direct": df.get("DIRECT_INDIRECT_OWNERSHIP", pd.Series("", index=df.index)).str.strip(),
            "security": df.get("SECURITY_TITLE", pd.Series("", index=df.index)),
        })
        return Loaded(out, [url], {"columns": {"SUBMISSION": list(sub.columns), "NONDERIV_TRANS": list(trans.columns)}})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        n = len(df)
        rep.expect_range("İşlem sayısı", n, 20_000, 2_000_000)
        start, end = quarter_bounds(partition)
        rep.expect_min_ratio("Dosyalama tarihi okunabilen", int(df.filing_date.notna().sum()), n, 0.999, 0.99)
        in_q = df.filing_date.between(start, end).sum()
        rep.expect_min_ratio("Dosyalama tarihi çeyrek içinde", int(in_q), n, 0.995, 0.97)
        rep.expect_min_ratio("Geçerli işlem kodu", int(df.code.isin(list(sec_form4.VALID_CODES)).sum()), n, 0.995, 0.98)
        dated = df.trans_date.notna() & df.filing_date.notna()
        rep.expect_min_ratio("İşlem tarihi ≤ dosyalama tarihi", int((df.trans_date[dated] <= df.filing_date[dated]).sum()),
                             int(dated.sum()), 0.995, 0.98)
        ps = df[df.code.isin(["P", "S"])]
        rep.expect_min_ratio("Kod/yön tutarlılığı (P→A, S→D)",
                             int(((ps.code == "P") & (ps.acq_disp == "A") | (ps.code == "S") & (ps.acq_disp == "D")).sum()),
                             len(ps), 0.99, 0.97)
        # Fiyatı 0/boş "P" kayıtları çoğunlukla yanlış kodlanmış özel yerleşim/dönüşümlerdir (örn. FOMC 2023q3);
        # açık piyasa alımı sinyalinden çıkarılırlar. Oran düşerse kaynakta bir sorun olabilir.
        rep.expect_min_ratio("Alım/satışta fiyat > 0 (0 fiyatlılar sinyalden çıkarılır)", int((ps.price > 0).sum()), len(ps), 0.94, 0.85)
        rep.expect_min_ratio("Ticker dolu", int((df.ticker.fillna("") != "").sum()), n, 0.97, 0.9)
        rep.add("Özet", Status.INFO, f"{df.issuer_cik.nunique():,} şirket, açık piyasa alımı (P): {int((df.code == 'P').sum()):,}")

    def check_dataset(self, client: HttpClient, manifest: dict, rep: SourceReport) -> dict[str, pd.DataFrame]:
        from radar.backfill.storage import read_partition
        parts = manifest["partitions"]
        ok = sorted(p for p, e in parts.items() if e["status"] != "fail")
        rep.add("Yüklenen çeyrek", Status.OK if ok else Status.FAIL, f"{len(ok)} çeyrek: {ok[:1]} … {ok[-1:]}")
        counts = {p: parts[p]["rows"] for p in ok}
        if counts:
            med = sorted(counts.values())[len(counts) // 2]
            low = [p for p, c in counts.items() if c < med * 0.5]
            rep.add("Çeyrek başına işlem sayısı tutarlılığı", Status.WARN if low else Status.OK,
                    f"medyan {med:,}; medyanın yarısının altında: {low or 'yok'}")
        if not ok:
            return {}

        # Bağımsız çapraz kontrol: toplu veri setindeki işlemleri EDGAR'daki özgün Form 4 XML'iyle karşılaştır.
        df = read_partition(self.name, ok[-1])
        filings = df[df.form == "4"].drop_duplicates("accession")
        sample = filings.sample(n=min(20, len(filings)), random_state=1)
        match = 0
        diffs = []
        for _, row in sample.iterrows():
            acc = row.accession
            url = f"https://www.sec.gov/Archives/edgar/data/{int(row.issuer_cik)}/{acc.replace('-', '')}/{acc}.txt"
            xml = sec_form4.extract_xml(client.get(url).text, "ownershipDocument")
            raw = sorted((t.code, round(t.shares or 0, 2), t.price or 0.0) for t in sec_form4.parse_form4(xml)) if xml else []
            bulk = sorted((r.code, round(r.shares if pd.notna(r.shares) else 0, 2), r.price if pd.notna(r.price) else 0.0)
                          for r in df[df.accession == acc].itertuples())
            # Toplu veri seti fiyatı 2 ondalığa yuvarlar; kuruş içi fark eşleşme sayılır.
            if len(raw) == len(bulk) and all(a[:2] == b[:2] and abs(a[2] - b[2]) <= 0.006 for a, b in zip(raw, bulk)):
                match += 1
            else:
                diffs.append(f"{acc}: toplu={bulk[:2]} ham={raw[:2]}")
        check = rep.expect_min_ratio(f"Çapraz kontrol: toplu veri ↔ özgün Form 4 ({ok[-1]})", match, len(sample), 0.95, 0.85)
        if diffs:
            check.detail += f"; farklar: {diffs[:3]}"
        return {}


RECENT_COLUMNS = ["accession", "form", "filing_date", "available_date", "issuer_cik", "ticker", "owner_cik", "owner_name",
                  "relationship", "owner_title", "n_owners", "trans_date", "code", "shares", "price", "acq_disp", "owned_after",
                  "direct", "security"]


class InsiderRecent(Dataset):
    """Çeyreklik toplu dosyası henüz yayımlanmamış günlerin Form 4'leri (haftalık tarama için).

    Kaynak: SEC günlük dosya indeksi → her Form 4'ün özgün XML'i. Yalnızca bugün borsada olan şirketlerin (universe veri
    seti) işlemleri. Bilinme tarihi toplu setle aynı kural: dosyalama tarihinden 1 iş günü sonra."""
    name = "insider_guncel"
    title = "SEC Form 4 (toplu dosyası henüz çıkmamış günler, günlük indeksten)"
    max_parallel = 2

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        quarters = InsiderTransactions()._links(client)
        last = max(quarters) if quarters else f"{today.year}q1"
        start = quarter_bounds(last)[1] + pd.Timedelta(days=1)
        days = pd.bdate_range(start, pd.Timestamp(today) - pd.Timedelta(days=1))
        return [f"{d:%Y%m%d}" for d in days]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        import re
        from radar import archive
        from radar.sources import sec_index
        d = pd.Timestamp(partition)
        url = sec_index.URL.format(y=d.year, q=(d.month - 1) // 3 + 1, d=d)
        try:
            rows = sec_index.parse_form_index(client.get(url).text)
        except Exception:  # tatil günü: indeks yok
            return Loaded(pd.DataFrame(columns=RECENT_COLUMNS), [url], {"filings": 0, "failed": 0, "holiday": True})
        listed = set(archive.load("universe", columns=["cik"]).cik.dropna().astype(int))
        paths = {}
        for r in rows:
            if r.form in ("4", "4/A"):
                paths.setdefault(r.path, (r.form, set()))[1].add(r.cik)
        todo = {p: f for p, (f, ciks) in paths.items() if ciks & listed}
        out, failed = [], 0
        for path, form in todo.items():
            try:
                text = client.get(sec_form4.ARCHIVE + path).text
            except Exception:
                failed += 1
                continue
            xml = sec_form4.extract_xml(text, "ownershipDocument")
            if not xml:
                failed += 1
                continue
            try:
                txs = sec_form4.parse_form4(xml)
            except Exception:
                failed += 1
                continue
            ten = bool(re.search(r"<isTenPercentOwner>\s*(1|true)\s*</isTenPercentOwner>", xml, re.I))
            owner_cik = re.search(r"<rptOwnerCik>\s*0*(\d+)\s*</rptOwnerCik>", xml)
            acc = path.rsplit("/", 1)[-1].replace(".txt", "")
            for t in txs:
                rel = ",".join(x for x, on in (("Director", t.is_director), ("Officer", t.is_officer), ("TenPercentOwner", ten)) if on)
                out.append({"accession": acc, "form": form, "filing_date": d, "available_date": d + pd.offsets.BDay(1),
                            "issuer_cik": t.issuer_cik, "ticker": t.ticker, "owner_cik": int(owner_cik.group(1)) if owner_cik else None,
                            "owner_name": t.owner, "relationship": rel, "owner_title": t.officer_title, "n_owners": 1,
                            "trans_date": pd.Timestamp(t.date) if t.date else pd.NaT, "code": t.code, "shares": t.shares,
                            "price": t.price, "acq_disp": t.acquired, "owned_after": t.owned_after, "direct": "", "security": ""})
        df = pd.DataFrame(out, columns=RECENT_COLUMNS)
        if len(df):
            df["issuer_cik"] = df.issuer_cik.astype("Int64")
            df["owner_cik"] = df.owner_cik.astype("Int64")
            df["n_owners"] = df.n_owners.astype("Int64")
        return Loaded(df, [url, sec_form4.ARCHIVE + "<form4>"], {"filings": len(todo), "failed": failed})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        n = loaded.notes
        if n.get("holiday"):
            rep.add("Günlük indeks", Status.INFO, "yok (tatil)")
            return
        rep.expect_min_ratio("Okunan Form 4", n["filings"] - n["failed"], max(n["filings"], 1), 0.97, 0.9)
        rep.add("İşlem satırı", Status.INFO, f"{len(loaded.df):,}")

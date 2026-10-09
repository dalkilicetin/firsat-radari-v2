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
FIRST = "2015q1"


class InsiderTransactions(Dataset):
    name = "insider"
    title = "SEC içeriden işlemler (Form 4, 2015→)"
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
        rep.expect_min_ratio("Alım/satışta fiyat > 0", int((ps.price > 0).sum()), len(ps), 0.97, 0.9)
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
            raw = sorted((t.code, round(t.shares or 0, 2), round(t.price or 0, 4)) for t in sec_form4.parse_form4(xml)) if xml else []
            bulk = sorted((r.code, round(r.shares if pd.notna(r.shares) else 0, 2), round(r.price if pd.notna(r.price) else 0, 4))
                          for r in df[df.accession == acc].itertuples())
            if raw == bulk:
                match += 1
            else:
                diffs.append(f"{acc}: toplu={bulk[:2]} ham={raw[:2]}")
        check = rep.expect_min_ratio(f"Çapraz kontrol: toplu veri ↔ özgün Form 4 ({ok[-1]})", match, len(sample), 0.95, 0.85)
        if diffs:
            check.detail += f"; farklar: {diffs[:3]}"
        return {}

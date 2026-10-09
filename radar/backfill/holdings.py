"""SEC Form 13F Data Sets: kurumsal yatırımcıların çeyreklik pozisyonları.

Notlar:
- SEC 2024'ten itibaren dosyaları takvim çeyreği yerine kayan 3 aylık pencerelerle yayımlıyor;
  bölüm adı dosya adının kendisidir (örn. 2023q3, 01jun2024-31aug2024).
- 3 Ocak 2023'ten önceki dosyalarda değer bin dolar cinsindendir; dolara çevrilir.
- Kullanılabilirlik: dosyalama tarihinden 1 iş günü sonrası.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from radar.backfill.base import Dataset, Loaded, links, read_zip_member, require, to_date, to_number
from radar.http import HttpClient
from radar.quality import SourceReport, Status

PAGE = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
UNIT_CHANGE = pd.Timestamp("2023-01-03")
AAPL_CUSIP = "037833100"


def partition_start(key: str) -> pd.Timestamp:
    if key[4] == "q":
        return pd.Timestamp(year=int(key[:4]), month=3 * int(key[5]) - 2, day=1)
    return pd.to_datetime(key.split("-")[0], format="%d%b%Y")


class InstitutionalHoldings(Dataset):
    name = "holdings"
    title = "SEC 13F kurumsal pozisyonlar (2015→)"
    max_parallel = 3

    def _links(self, client: HttpClient) -> dict[str, str]:
        return links(client, PAGE, r"/([^/]+)_form13f\.zip")

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return sorted((k for k in self._links(client) if partition_start(k) >= pd.Timestamp("2015-01-01")), key=partition_start)

    def load(self, client: HttpClient, partition: str) -> Loaded:
        url = self._links(client)[partition]
        blob = client.get(url, timeout=900).content
        sub = read_zip_member(blob, "SUBMISSION.tsv")
        cover = read_zip_member(blob, "COVERPAGE.tsv")
        info = read_zip_member(blob, "INFOTABLE.tsv")
        require(sub, ["ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT"], "SUBMISSION")
        require(info, ["ACCESSION_NUMBER", "CUSIP", "VALUE", "SSHPRNAMT", "SSHPRNAMTTYPE"], "INFOTABLE")
        cover_cols = [c for c in ("ACCESSION_NUMBER", "ISAMENDMENT", "AMENDMENTTYPE", "FILINGMANAGER_NAME") if c in cover.columns]
        df = info.merge(sub, on="ACCESSION_NUMBER", how="left").merge(cover[cover_cols], on="ACCESSION_NUMBER", how="left")
        col = lambda c: df[c] if c in df.columns else pd.Series("", index=df.index)
        filing = to_date(df["FILING_DATE"], "%d-%b-%Y")
        value = to_number(df["VALUE"])
        value = value.where(filing >= UNIT_CHANGE, value * 1000)  # bin dolar → dolar
        out = pd.DataFrame({
            "accession": df["ACCESSION_NUMBER"], "filer_cik": pd.to_numeric(df["CIK"], errors="coerce").astype("Int64"),
            "filer_name": col("FILINGMANAGER_NAME"), "form": df["SUBMISSIONTYPE"],
            "is_amendment": col("ISAMENDMENT").eq("Y"), "amendment_type": col("AMENDMENTTYPE"),
            "period": to_date(df["PERIODOFREPORT"], "%d-%b-%Y"), "filing_date": filing,
            "available_date": filing + pd.offsets.BDay(1),
            "cusip": df["CUSIP"].str.strip().str.upper(), "issuer": col("NAMEOFISSUER"),
            "title": col("TITLEOFCLASS"), "value": value, "shares": to_number(df["SSHPRNAMT"]),
            "share_type": df["SSHPRNAMTTYPE"], "put_call": col("PUTCALL").str.strip(),
        })
        return Loaded(out, [url], {"filings": int(sub.ACCESSION_NUMBER.nunique())})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        n = len(df)
        rep.expect_range("Dosya (13F-HR) sayısı", loaded.notes["filings"], 3_000, 15_000)
        rep.expect_range("Pozisyon satırı", n, 500_000, 6_000_000)
        rep.expect_min_ratio("Geçerli CUSIP", int(df.cusip.str.match(r"^[0-9A-Z]{8}[0-9]$").sum()), n, 0.99, 0.97)
        rep.expect_min_ratio("Değer ve adet > 0", int(((df.value > 0) & (df.shares > 0)).sum()), n, 0.97, 0.93)
        rep.expect_min_ratio("Dönem sonu ≤ dosyalama tarihi", int((df.period <= df.filing_date).sum()), n, 0.999, 0.99)
        # Birim tutarlılığı: AAPL için değer/adet, o çeyrek sonundaki gerçek fiyata yakın olmalı (bin $ hatası 1000 kat sapar).
        aapl = df[(df.cusip == AAPL_CUSIP) & (df.share_type == "SH") & (df.put_call == "") & (df.shares > 0)]
        if len(aapl):
            implied = (aapl.value / aapl.shares).median()
            rep.add("Birim kontrolü: AAPL değer/adet (medyan $)", Status.OK if 20 < implied < 1000 else Status.FAIL,
                    f"{implied:,.2f} $ ({aapl.period.mode().iloc[0].date()} dönemi)")
        rep.add("Özet", Status.INFO, f"{df.filer_cik.nunique():,} kurum, {df.cusip.nunique():,} CUSIP, "
                                     f"düzeltme dosyası: {int(df.is_amendment.sum()):,} satır")

    def check_dataset(self, client: HttpClient, manifest: dict, rep: SourceReport) -> dict[str, pd.DataFrame]:
        ok = sorted((p for p, e in manifest["partitions"].items() if e["status"] != "fail"), key=partition_start)
        rep.add("Yüklenen bölüm", Status.OK if ok else Status.FAIL, f"{len(ok)} bölüm: {ok[:1]} … {ok[-1:]}")
        return {}

"""SEC Financial Statement Data Sets: 10-K/10-Q/20-F'lerin XBRL değerleri, çeyreklik toplu dosyalar.

Her değer, ait olduğu raporun SEC'e kabul anı (`accepted`) ile saklanır; geriye dönük testte bir değer
ancak bu andan sonra kullanılabilir. Yalnızca temel kalemler ve sınıf/segment ayrımı olmayan değerler tutulur.
"""

from __future__ import annotations

import io
import zipfile
from datetime import date

import pandas as pd

from radar.backfill.base import Dataset, Loaded, links, quarter_bounds, read_zip_member, require, to_date
from radar.http import HttpClient
from radar.quality import SourceReport, Status

PAGE = "https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets"
FIRST = "2015q1"
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "20-F", "20-F/A", "40-F", "40-F/A", "10-KT", "10-QT"}

TAGS = {
    # Gelir ve kârlılık
    "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet", "CostOfRevenue", "CostOfGoodsAndServicesSold", "GrossProfit", "ResearchAndDevelopmentExpense",
    "SellingGeneralAndAdministrativeExpense", "OperatingIncomeLoss", "NetIncomeLoss", "ProfitLoss",
    "EarningsPerShareBasic", "EarningsPerShareDiluted", "IncomeTaxExpenseBenefit", "InterestExpense",
    "DepreciationDepletionAndAmortization", "ShareBasedCompensation",
    # Bilanço
    "Assets", "AssetsCurrent", "Liabilities", "LiabilitiesCurrent", "StockholdersEquity",
    "CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
    "ShortTermInvestments", "MarketableSecuritiesCurrent", "LongTermDebt", "LongTermDebtNoncurrent", "LongTermDebtCurrent",
    "DebtCurrent", "InventoryNet", "AccountsReceivableNetCurrent", "Goodwill", "IntangibleAssetsNetExcludingGoodwill",
    "ContractWithCustomerLiabilityCurrent", "DeferredRevenueCurrent", "RetainedEarningsAccumulatedDeficit",
    # Nakit akışı ve sermaye kararları
    "NetCashProvidedByUsedInOperatingActivities", "NetCashProvidedByUsedInInvestingActivities",
    "NetCashProvidedByUsedInFinancingActivities", "PaymentsToAcquirePropertyPlantAndEquipment",
    "PaymentsForRepurchaseOfCommonStock", "PaymentsOfDividends", "ProceedsFromIssuanceOfCommonStock",
    "PaymentsToAcquireBusinessesNetOfCashAcquired",
    # Hisse sayısı (sulandırma)
    "CommonStockSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic",
    "WeightedAverageNumberOfDilutedSharesOutstanding", "EntityCommonStockSharesOutstanding", "EntityPublicFloat",
    # IFRS (yabancı şirketler)
    "Revenue", "Equity", "CashAndCashEquivalents", "ProfitLossAttributableToOwnersOfParent",
}

SHARE_TAGS = {"EntityCommonStockSharesOutstanding", "CommonStockSharesOutstanding"}

# Doğrulanmış gerçekler: (bölüm, CIK, etiket, dönem sonu (ay sonuna yuvarlanmış), çeyrek sayısı, değer)
GOLDEN = [
    ("2023q4", 320193, "RevenueFromContractWithCustomerExcludingAssessedTax", "2023-09-30", 4, 383_285_000_000),
    ("2023q3", 789019, "RevenueFromContractWithCustomerExcludingAssessedTax", "2023-06-30", 4, 211_915_000_000),
    ("2024q1", 1045810, "Revenues", "2024-01-31", 4, 60_922_000_000),
]


def read_num(blob: bytes) -> pd.DataFrame:
    """num.txt büyük olduğu için parça parça okunup yalnızca gerekli satırlar tutulur."""
    keep = []
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = next(n for n in zf.namelist() if n.lower().endswith("num.txt"))
        with zf.open(name) as f:
            for chunk in pd.read_csv(f, sep="\t", dtype=str, keep_default_na=False, quoting=3, chunksize=500_000,
                                     encoding="utf-8", encoding_errors="replace", on_bad_lines="warn"):
                chunk.columns = [c.strip().upper() for c in chunk.columns]
                mask = chunk["TAG"].isin(TAGS) & (chunk["COREG"] == "")
                if "SEGMENTS" in chunk.columns:
                    # Segmentsiz değerler + hisse sayısının sınıf bazındaki değerleri (A/B sınıfı; toplanarak
                    # çok sınıflı şirketlerin toplam hisse sayısı bulunur). Sınıf ekseni tek boyutlu olmalı.
                    seg = chunk["SEGMENTS"]
                    class_rows = chunk["TAG"].isin(SHARE_TAGS) & seg.str.contains("Class", case=False) & (seg.str.count(";") <= 1)
                    mask &= (seg == "") | class_rows
                else:
                    chunk["SEGMENTS"] = ""
                keep.append(chunk.loc[mask, [c for c in ("ADSH", "TAG", "VERSION", "DDATE", "QTRS", "UOM", "VALUE", "SEGMENTS") if c in chunk.columns]])
    return pd.concat(keep, ignore_index=True)


class FinancialStatements(Dataset):
    name = "financials"
    title = "SEC finansal tablo verileri (XBRL, 2015→)"
    max_parallel = 3

    def _links(self, client: HttpClient) -> dict[str, str]:
        return links(client, PAGE, r"/(\d{4}q[1-4])\.zip")

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return sorted(p for p in self._links(client) if p >= FIRST)

    def load(self, client: HttpClient, partition: str) -> Loaded:
        url = self._links(client)[partition]
        blob = client.get(url, timeout=600).content
        sub = read_zip_member(blob, "sub.txt")
        require(sub, ["ADSH", "CIK", "NAME", "SIC", "FORM", "PERIOD", "FY", "FP", "FILED", "ACCEPTED"], "sub.txt")
        sub = sub[sub.FORM.isin(FORMS)]
        num = read_num(blob)
        require(num, ["ADSH", "TAG", "DDATE", "QTRS", "UOM", "VALUE"], "num.txt")
        df = num.merge(sub[["ADSH", "CIK", "NAME", "SIC", "FORM", "PERIOD", "FY", "FP", "FILED", "ACCEPTED"]], on="ADSH")
        out = pd.DataFrame({
            "adsh": df.ADSH, "cik": pd.to_numeric(df.CIK, errors="coerce").astype("Int64"), "name": df.NAME,
            "sic": df.SIC, "form": df.FORM, "fy": df.FY, "fp": df.FP,
            "period": to_date(df.PERIOD, "%Y%m%d"), "filed": to_date(df.FILED, "%Y%m%d"),
            "accepted": to_date(df.ACCEPTED, "%Y-%m-%d %H:%M:%S.%f"),
            "tag": df.TAG, "version": df.get("VERSION", ""), "ddate": to_date(df.DDATE, "%Y%m%d"),
            "qtrs": pd.to_numeric(df.QTRS, errors="coerce").astype("Int64"), "uom": df.UOM,
            "value": pd.to_numeric(df.VALUE, errors="coerce"),
            "segments": df.get("SEGMENTS", pd.Series("", index=df.index)).fillna(""),
        })
        # XBRL'de değeri boş ("nil") olarak raporlanmış kalemler tutulmaz.
        empty = int(out.value.isna().sum())
        out = out[out.value.notna()]
        return Loaded(out, [url], {"filings": int(sub.ADSH.nunique()), "forms": sub.FORM.value_counts().to_dict(),
                                   "empty_values": empty})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        n = len(df)
        rep.expect_range("Rapor sayısı (10-K/10-Q/20-F)", loaded.notes["filings"], 3_000, 20_000)
        rep.expect_range("Değer sayısı (temel kalemler)", n, 100_000, 3_000_000)
        rep.expect_min_ratio("Kabul anı okunabilen", int(df.accepted.notna().sum()), n, 0.999, 0.99)
        start, end = quarter_bounds(partition)
        rep.expect_min_ratio("Dosyalama tarihi çeyrek içinde", int(df.filed.between(start, end).sum()), n, 0.995, 0.97)
        both = df.accepted.notna() & df.filed.notna()
        gap = (df.filed[both] - df.accepted[both].dt.normalize()).dt.days
        rep.expect_min_ratio("Kabul günü ≤ dosyalama günü (≤3 gün)", int(gap.between(0, 3).sum()), int(both.sum()), 0.99, 0.98)
        rep.add("Boş (nil) değer, ayıklandı", Status.INFO, f"{loaded.notes['empty_values']:,} satır")
        rep.expect_min_ratio("Dönem sonu ≤ kabul anı", int((df.ddate <= df.accepted).sum()), int(both.sum()), 0.999, 0.99)
        for part, cik, tag, ddate, qtrs, value in GOLDEN:
            if part != partition:
                continue
            hit = df[(df.cik == cik) & (df.tag == tag) & (df.ddate == pd.Timestamp(ddate)) & (df.qtrs == qtrs) & df.form.str.startswith("10-K")]
            got = float(hit.value.iloc[0]) if len(hit) else None
            rep.expect_equal(f"Doğrulanmış gerçek: CIK {cik} {tag} {ddate}", got, value)
        rep.add("Form dağılımı", Status.INFO, str(loaded.notes["forms"]))
        seg = df[df.segments != ""]
        if len(seg):
            # Doğrulama: Alphabet'in A+B+C sınıfı toplam hisse sayısı ~12 milyar.
            goog = seg[(seg.cik == 1652044) & (seg.tag == "EntityCommonStockSharesOutstanding")]
            goog = goog[goog.ddate == goog.ddate.max()].value.sum() if len(goog) else None
            rep.add("Sınıf bazında hisse sayısı satırı", Status.INFO, f"{len(seg):,} satır, {seg.cik.nunique():,} şirket")
            if goog:
                rep.expect_range("Doğrulama: Alphabet sınıf toplamı hisse sayısı", float(goog), 11e9, 13.5e9, warn_only=True)

    def check_dataset(self, client: HttpClient, manifest: dict, rep: SourceReport) -> dict[str, pd.DataFrame]:
        parts = manifest["partitions"]
        ok = sorted(p for p, e in parts.items() if e["status"] != "fail")
        rep.add("Yüklenen çeyrek", Status.OK if ok else Status.FAIL, f"{len(ok)} çeyrek: {ok[:1]} … {ok[-1:]}")
        golden_parts = {g[0] for g in GOLDEN}
        verified = [p for p in golden_parts if p in parts and all(
            c["status"] == "ok" for c in parts[p]["checks"] if c["name"].startswith("Doğrulanmış"))]
        rep.add("Doğrulanmış gerçek içeren çeyrekler", Status.OK if len(verified) == len(golden_parts) else Status.FAIL,
                f"{len(verified)}/{len(golden_parts)} geçti")
        return {}

"""FRED serileri: şirketlerin girdi ve çıktılarının (emtia, enerji, sektör üretimi, fiyatlar, faiz) geçmişi.

1. yolda bir şirketin girdisi/çıktısı bu serilerden birine bağlanır ve serinin yönü şirketin yönüne taşınır.
Seri listesi 3. aşamada şirket profilleri çıkarıldıkça genişletilecek.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from radar.backfill.base import Dataset, Loaded
from radar.http import HttpClient
from radar.quality import SourceReport, Status
from radar.sources.fred import URL, parse_fred_csv

SERIES = {
    # Enerji
    "DCOILWTICO": "Ham petrol WTI", "DCOILBRENTEU": "Ham petrol Brent", "DHHNGSP": "Doğal gaz Henry Hub",
    "GASREGW": "Benzin perakende", "APU000072610": "Elektrik fiyatı (kWh)",
    # Metaller ve hammadde (IMF, aylık)
    "PCOPPUSDM": "Bakır", "PALUMUSDM": "Alüminyum", "PNICKUSDM": "Nikel", "PIORECRUSDM": "Demir cevheri",
    "PURANUSDM": "Uranyum", "PZINCUSDM": "Çinko", "PCOTTINDUSDM": "Pamuk", "PWHEAMTUSDM": "Buğday",
    "PMAIZMTUSDM": "Mısır", "PSOYBUSDM": "Soya",
    # Üretim (sektör)
    "INDPRO": "Sanayi üretimi", "IPG3344S": "Yarı iletken üretimi", "IPG3341S": "Bilgisayar ve çevre birimi üretimi",
    "IPG325S": "Kimya üretimi", "IPG3254S": "İlaç üretimi", "IPG336S": "Ulaşım ekipmanı üretimi",
    "IPG2211S": "Elektrik üretimi", "IPN213111N": "Petrol/gaz sondajı", "TCU": "Kapasite kullanımı",
    # Talep ve yatırım
    "RSAFS": "Perakende satışlar", "ECOMSA": "E-ticaret satışları", "TTLCONS": "İnşaat harcaması",
    "HOUST": "Konut başlangıçları", "TOTALSA": "Otomobil satışları", "ANDENO": "Savunma dışı sermaye malı siparişleri",
    "A679RC1Q027SBEA": "Bilgi işlem ekipmanı yatırımı", "PNFI": "Özel sabit yatırım",
    # Fiyatlar ve maliyetler
    "CPIAUCSL": "Tüketici fiyatları", "PPIACO": "Üretici fiyatları", "CES0500000003": "Saatlik ücret",
    "PCU334413334413": "Yarı iletken üretici fiyatı",
    # Finansal koşullar
    "DGS10": "10 yıllık faiz", "DGS2": "2 yıllık faiz", "FEDFUNDS": "Fed faizi", "BAA10Y": "Baa kurumsal tahvil makası",
    "DTWEXBGS": "Dolar endeksi", "VIXCLS": "VIX", "UNRATE": "İşsizlik",
}


class FredSeries(Dataset):
    name = "fred"
    title = "FRED makro, emtia ve sektör serileri"
    max_parallel = 1

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [f"all-{today:%Y%m%d}"]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        frames, failed = [], {}
        for sid in SERIES:
            try:
                s = parse_fred_csv(client.get(URL.format(sid=sid)).text)
            except Exception as exc:  # tek seri tüm bölümü düşürmesin; kontrolde görünür
                failed[sid] = str(exc)[:100]
                continue
            frames.append(pd.DataFrame({"series": sid, "date": pd.to_datetime(list(s)), "value": list(s.values())}))
        df = pd.concat(frames, ignore_index=True).dropna(subset=["value"])
        return Loaded(df, [URL.format(sid="<seri>")], {"failed": failed})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        df = loaded.df
        failed = loaded.notes["failed"]
        rep.expect_min_ratio("İndirilen seri", len(SERIES) - len(failed), len(SERIES), 1.0, 0.9).detail += \
            f"; başarısız: {failed}" if failed else ""
        span = df.groupby("series").date.agg(["min", "max"])
        late_start = span[span["min"] > pd.Timestamp("2015-01-01")]
        rep.add("2015'ten önce başlayan seri", Status.OK if late_start.empty else Status.WARN,
                f"{len(span) - len(late_start)}/{len(span)}; geç başlayanlar: "
                f"{ {s: str(d.date()) for s, d in late_start['min'].items()} or 'yok'}")
        stale = span[span["max"] < pd.Timestamp.today() - pd.Timedelta(days=200)]
        rep.add("Son 200 günde güncellenen seri", Status.OK if stale.empty else Status.WARN,
                f"{len(span) - len(stale)}/{len(span)}; eskiler: { {s: str(d.date()) for s, d in stale['max'].items()} or 'yok'}")

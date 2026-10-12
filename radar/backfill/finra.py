"""FINRA Reg SHO günlük açığa satış hacmi (ücretsiz) → ay × sembol toplamları.

Kaynak: https://cdn.finra.org/equity/regsho/daily/<TESİS>shvol<YYYYMMDD>.txt (Tarih|Sembol|AçığaSatış|Muaf|Toplam|Pazar).
2018-08'den itibaren konsolide dosya (CNMS); öncesinde tesis dosyaları (FNSQ, FNQC, FNYX, FORF) toplanır.
Saklanan: ay × sembol → açığa satış hacmi, toplam hacim, gün sayısı.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta

import pandas as pd

from radar.backfill.base import Dataset, Loaded
from radar.http import FetchError, HttpClient
from radar.quality import SourceReport, Status

URL = "https://cdn.finra.org/equity/regsho/daily/{fac}shvol{d:%Y%m%d}.txt"
OLD = ["FNSQ", "FNQC", "FNYX", "FORF"]


class ShortVolume(Dataset):
    name = "finra_aciga_satis"
    title = "FINRA günlük açığa satış hacmi — ay × sembol (2009→)"
    max_parallel = 4

    def partitions(self, client: HttpClient, today: date) -> list[str]:
        return [str(y) for y in range(2009, today.year + 1)]

    def load(self, client: HttpClient, partition: str) -> Loaded:
        y = int(partition)
        agg = defaultdict(lambda: [0.0, 0.0, 0])
        days = ok_days = 0
        d = date(y, 1, 1)
        end = min(date(y, 12, 31), date.today() - timedelta(days=1))
        while d <= end:
            if d.weekday() < 5:
                days += 1
                facs = ["CNMS"] if d >= date(2018, 8, 1) else OLD
                got = False
                for fac in facs:
                    try:
                        text = client.get(URL.format(fac=fac, d=d), retries=1).text
                    except FetchError:
                        continue
                    lines = text.splitlines()
                    if not lines:
                        continue
                    # Sütunlar başlıktan: eski dosyalarda (≤2011) muaf hacim sütunu yok, sıra farklı
                    head = [h.strip().lower() for h in lines[0].split("|")]
                    try:
                        i_sym, i_short, i_tot = head.index("symbol"), head.index("shortvolume"), head.index("totalvolume")
                    except ValueError:
                        continue
                    for line in lines[1:]:
                        p = line.split("|")
                        if len(p) <= max(i_short, i_tot) or not p[i_short].replace(".", "").isdigit() \
                                or not p[i_tot].replace(".", "").isdigit():
                            continue
                        v = agg[(d.replace(day=1), p[i_sym])]
                        v[0] += float(p[i_short]); v[1] += float(p[i_tot])
                        if fac in ("CNMS", "FNSQ"):
                            v[2] += 1
                        got = True
                ok_days += got
            d += timedelta(days=1)
        df = pd.DataFrame([(m, s, *v) for (m, s), v in agg.items()], columns=["date", "symbol", "short", "total", "days"])
        df["date"] = pd.to_datetime(df.date)
        return Loaded(df, [URL.format(fac="<tesis>", d=date(y, 1, 2))], {"days": days, "ok_days": ok_days})

    def check_partition(self, loaded: Loaded, partition: str, rep: SourceReport) -> None:
        n = loaded.notes
        rep.expect_min_ratio("Dosyası gelen işlem günü", n["ok_days"], max(n["days"], 1), 0.9, 0.7)
        df = loaded.df
        if len(df):
            r = (df.short.sum() / df.total.sum())
            rep.expect_range("Açığa satış payı (toplam)", float(r), 0.2, 0.7)
            rep.add("Sembol sayısı", Status.INFO, f"{df.symbol.nunique():,}")

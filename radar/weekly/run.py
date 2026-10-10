"""Haftalık rapor: python -m radar.weekly.run → reports/weekly/<tarih>.pdf ve <tarih>.csv

CSV, o haftanın tüm puanlarını saklar; öneri takibi (gerçekleşen sonuçlarla karşılaştırma) bu dosyalardan yapılır.
"""

from __future__ import annotations

import time

from radar import config
from radar.weekly import pdf, snapshot

OUT = config.ROOT / "reports" / "weekly"


def main() -> None:
    t0 = time.time()
    snap = snapshot.build()
    day = snap.date.date().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    cols = ["sembol", "sirket", "fiyat", "islem_hacmi", "yatirilabilir", "potansiyel", "vade", "risk", "risk_yuzdelik",
            "puan_1h", "puan_1a", "puan_3a", "puan_6a", "puan_1y", "yol1", "yol2", "yol3", "yol4", "piyasa"]
    snap.table[cols].sort_values("potansiyel", ascending=False).round(2).to_csv(OUT / f"{day}.csv", index_label="cik")
    path = pdf.render(snap, OUT / f"{day}.pdf")
    print(f"{path} ({round(time.time() - t0)} sn)")


if __name__ == "__main__":
    main()

"""Ortak ayarlar."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
STATE_DIR = DATA_DIR / "state"
REPORT_DIR = ROOT / "reports" / "data_health"

# SEC, istekte kim olduğumuzu belirten bir User-Agent ister; tanımsız istemcileri engeller.
# GitHub Actions'ta RADAR_USER_AGENT secret'ı ile değiştirilebilir.
USER_AGENT = os.environ.get("RADAR_USER_AGENT") or (
    "FirsatRadari/0.1 (research; https://github.com/dalkilicetin/firsat-radari-v2)"
)

# Host başına saniyedeki en fazla istek. SEC'in sınırı 10/sn; güvenli tarafta kalıyoruz.
RATE_LIMITS = {
    "www.sec.gov": 8.0,
    "data.sec.gov": 8.0,
    "api.gdeltproject.org": 0.2,
    "www.reddit.com": 0.5,
    "oauth.reddit.com": 1.0,
    "query.wikidata.org": 0.5,
    "stooq.com": 1.0,
    "query1.finance.yahoo.com": 2.0,
}
DEFAULT_RATE = 4.0

# Sağlık kontrolünde her zaman örneklenen, değerlerini bildiğimiz şirketler.
REFERENCE_TICKERS = ["AAPL", "MSFT", "NVDA"]

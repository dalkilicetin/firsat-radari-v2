"""Yol sabitleri ve ortak ayarlar."""
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent      # arastirma/
REPO = KOK.parent
ONBELLEK = KOK / "onbellek"
SONUCLAR = KOK / "sonuclar"
HIPOTEZLER = KOK / "hipotezler"
TARIH = KOK / "tarih"

MALIYET_BP = {"endeks": 10, "hisse": 20}

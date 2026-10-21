"""Repodaki ornek verinin yukleyicisi (ag yok)."""
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from mekanizma.ayarlar import ONBELLEK, REPO, SONUCLAR

SONUC_JSON = REPO / "data" / "sonuclar.json"


def _oku(yol=None):
    return json.loads(Path(yol or SONUC_JSON).read_text(encoding="utf-8"))


def _aylik_seri(closes, bitis):
    """closes yeniden eskiye; closes[0] = bitis ayi. Ay sonu indeksli seri (eskiden yeniye)."""
    bitis = pd.Timestamp(bitis) + pd.offsets.MonthEnd(0)
    idx = pd.date_range(end=bitis, periods=len(closes), freq="ME")
    return pd.Series(list(reversed(closes)), index=idx, dtype=float)


def aylik(yol=None) -> pd.DataFrame:
    """Hisse + ETF aylik kapanislari. Sutun = sembol, indeks = ay sonu. Kisa seriler sona hizali."""
    d = _oku(yol)
    seriler = {}
    for kaynak in ("series", "etf"):
        for s, v in d.get(kaynak, {}).items():
            c = v.get("closes")
            if not c:
                continue
            bitis = v.get("dateIso") or v.get("date") or d["generatedAt"][:10]
            seriler[s] = _aylik_seri(c, bitis)
    df = pd.DataFrame(seriler).sort_index()
    return df


def profil(yol=None) -> pd.DataFrame:
    """sembol, ad, sektor, mcap (prof ve fin alanlarindan)."""
    d = _oku(yol)
    satir = {}
    for s, f in d.get("fin", {}).items():
        satir[s] = {"ad": f.get("name"), "sektor": f.get("industry"), "mcap": f.get("mcap")}
    for s, p in d.get("prof", {}).items():
        if not isinstance(p, dict):
            continue
        r = satir.setdefault(s, {"ad": None, "sektor": None, "mcap": None})
        r["ad"] = r["ad"] or p.get("name")
        r["sektor"] = p.get("ind") or r["sektor"]
    out = pd.DataFrame.from_dict(satir, orient="index")
    out.index.name = "sembol"
    return out


def _git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout


def gunluk_panel(yenile=False, dal="origin/main") -> pd.DataFrame:
    """Git gecmisindeki gece taramalarindan uzun format panel:
    tarih, sembol, fiyat, mtd, r13w, r52w, hi52, mcap"""
    onb = ONBELLEK / "gunluk_panel.pkl"
    if onb.exists() and not yenile:
        return pd.read_pickle(onb)
    if _git("rev-parse", "--is-shallow-repository").strip() == "true":
        raise RuntimeError("Git gecmisi eksik (shallow). Calistir: git fetch --unshallow origin main")
    try:
        _git("rev-parse", "--verify", dal)
    except subprocess.CalledProcessError:
        dal = "HEAD"
    satirlar = _git("log", dal, "--format=%H %ad", "--date=short", "--", "data/sonuclar.json").strip().splitlines()
    gunluk = {}
    for s in satirlar:  # yeniden eskiye; ayni tarihte ilk gorulen = en yeni
        h, tarih = s.split()
        gunluk.setdefault(tarih, h)
    kayit = []
    for tarih, h in sorted(gunluk.items()):
        try:
            d = json.loads(_git("show", f"{h}:data/sonuclar.json"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        scr, q = d.get("screen", {}), d.get("quotes", {})
        for sembol in set(scr) | set(q):
            e = scr.get(sembol, {})
            fiyat = (q.get(sembol) or {}).get("price")
            kayit.append((pd.Timestamp(tarih), sembol, fiyat, e.get("mtd"), e.get("r13w"),
                          e.get("r52w"), e.get("hi52"), e.get("mcap")))
    df = pd.DataFrame(kayit, columns=["tarih", "sembol", "fiyat", "mtd", "r13w", "r52w", "hi52", "mcap"])
    onb.parent.mkdir(exist_ok=True)
    df.to_pickle(onb)
    return df


def ozet_yaz() -> int:
    a, p = aylik(), profil()
    satir = ["# Ornek veri ozeti", "",
             f"- Aylik: {a.shape[1]} sembol, {a.index[0]:%Y-%m} → {a.index[-1]:%Y-%m}, NaN orani %{a.isna().mean().mean()*100:.1f}",
             f"- Profil: {len(p)} sembol, sektoru olan {p['sektor'].notna().sum()}"]
    try:
        g = gunluk_panel()
        satir.append(f"- Gunluk panel: {g['tarih'].nunique()} gun, {g['sembol'].nunique()} sembol, "
                     f"{g['tarih'].min():%Y-%m-%d} → {g['tarih'].max():%Y-%m-%d}, fiyat NaN orani %{g['fiyat'].isna().mean()*100:.1f}")
    except RuntimeError as e:
        satir.append(f"- Gunluk panel: YUKLENEMEDI ({e})")
    SONUCLAR.mkdir(exist_ok=True)
    (SONUCLAR / "ornek_veri.md").write_text("\n".join(satir) + "\n", encoding="utf-8")
    print("\n".join(satir))
    return 0

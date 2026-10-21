"""Simulasyon deneylerinin ortak yardimcilari."""
import json
import math

import numpy as np
import pandas as pd
import yaml

from mekanizma.ayarlar import KOK, SONUCLAR
from mekanizma.hipotez import yukle
from mekanizma.mekanizmalar import yay
from mekanizma.sim.piyasa import Ayar

BASLIK = ("> **Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener.** "
          "Yay mekanizmasını simülatöre biz koyduk.\n")
AYAR_DOSYASI = SONUCLAR / "sim_ayar.yaml"


def ayar_yukle(**ek) -> Ayar:
    kw = {}
    if AYAR_DOSYASI.exists():
        d = yaml.safe_load(AYAR_DOSYASI.read_text(encoding="utf-8"))
        kw = dict(yarilanma=d["yarilanma"], lam_P=d["lam_P"], lam_B=d["lam_B"], sB=tuple(d["sB"]))
    kw.update(ek)
    return Ayar(**kw)


def yay_p():
    return yukle("yay")["gunluk"]


def yay_calistir(d, p=None):
    p = p or yay_p()
    e = d.endeks
    oz = yay.ozellikler(e["adj"], p, d.hisseler, e["vix"], e["kredi"], e["sahm"])   # F ve m verilmez
    return oz, yay.sinyaller(oz, p)


def gercek_tur(d, t):
    """t gunundeki dususun (son 252 bar zirvesinden) cogu m'den mi (panik) F'den mi (bozulma)?"""
    e = d.endeks
    a = max(0, t - 251)
    pk = a + int(np.argmax(e["adj"].to_numpy()[a:t + 1]))
    dF = e["F"].iloc[t] - e["F"].iloc[pk]
    dm = e["m"].iloc[t] - e["m"].iloc[pk]
    tot = dF + dm
    if tot >= 0:
        return None, pk
    return ("panik" if dm / tot > 0.5 else "bozulma"), pk


def dusus_bolumleri(adj, esik=-0.10):
    """Zirve -> dip -> eski zirveye donus bolumleri (donusu tamamlanmis, dip dususu <= esik)."""
    v = adj.to_numpy(float)
    pk, tr, mn, out = 0, 0, 0.0, []
    for t in range(1, len(v)):
        if v[t] >= v[pk]:
            if mn <= esik:
                out.append((pk, tr, t))
            pk, tr, mn = t, t, 0.0
        else:
            dd = v[t] / v[pk] - 1
            if dd < mn:
                mn, tr = dd, t
    r = pd.DataFrame(out, columns=["zirve", "dip", "top"])
    if len(r):
        r["dusus"] = [v[b] / v[a] - 1 for a, b in zip(r.zirve, r.dip)]
        r["gun_dibe"] = r.dip - r.zirve
        r["gun_top"] = r.top - r.dip
        r["sertlik"] = r.gun_top / r.gun_dibe
    return r


def guvenli(o):
    if isinstance(o, dict):
        return {str(k): guvenli(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [guvenli(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if (math.isnan(o) or math.isinf(o)) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def yaz(ad, md, js):
    SONUCLAR.mkdir(exist_ok=True)
    (SONUCLAR / f"{ad}.md").write_text(md, encoding="utf-8")
    (SONUCLAR / f"{ad}.json").write_text(json.dumps(guvenli(js), ensure_ascii=False, indent=1), encoding="utf-8")


def gunluge_yaz(deney, parametreler, ana_sonuc):
    import csv
    from datetime import datetime
    yol = KOK / "deneme_gunlugu.csv"
    yeni = not yol.exists()
    with open(yol, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if yeni:
            w.writerow(["zaman", "deney", "parametreler", "ana_sonuc"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), deney, json.dumps(guvenli(parametreler), ensure_ascii=False),
                    json.dumps(guvenli(ana_sonuc), ensure_ascii=False)])


def pct(x, d=1):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x*100:.{d}f}%"


def ga_str(o):
    if not o or o.get("n", 0) == 0 or o.get("ort") is None:
        return "–"
    ga = "" if o.get("ga_alt") is None else f" [{o['ga_alt']*100:.1f}, {o['ga_ust']*100:.1f}]"
    return f"{o['ort']*100:.1f}%{ga} (n={o['n']})"

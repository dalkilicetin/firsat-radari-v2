"""Önbellek: test düzeneği (evren, getiriler, karşılaştırmalar) ve işaretler → data/derived/arac/.

python -m radar.arac.hazirla
"""

from __future__ import annotations

import json
import time

import pandas as pd

from radar import config
from radar.arac import isaretler
from radar.arac.duzenek import VADE, Duzenek

CACHE = isaretler.CACHE


def main() -> dict:
    t0 = time.time()
    d = Duzenek.yukle()
    k = isaretler.Kaynaklar.yukle(d)
    o = isaretler.hesapla(d, k)
    isaretler.kaydet(o)
    tablo = {"evren": d.evren, "piyasa_degeri": d.piyasa_degeri, "islem_tutari": d.islem_tutari,
             "masraf_orani": d.masraf_orani, "fiyat_persembe": d.persembe["price"], "fiyat_cuma": d.cuma["price"],
             "ham_persembe": d.persembe["raw"]}
    for v in VADE:
        tablo[f"brut_{v}"] = d.brut(v)
        tablo[f"net_{v}"] = d.net(v)
        kz = d.kiyas(v)
        tablo[f"sektor_{v}"] = kz["sektor"]
        tablo[f"kiyas_{v}"] = pd.DataFrame({"borsa": kz["borsa"], "esit": kz["esit"]})
    path = CACHE / "duzenek"
    path.mkdir(parents=True, exist_ok=True)
    for n, df in tablo.items():
        df.astype("float32").to_parquet(path / f"{n}.parquet")
    d.islem_kaynagi.to_parquet(path / "islem_kaynagi.parquet")
    ev = d.evren
    sec = d.sec.set_index(d.sec.cik.astype(str)).reindex(d.sutunlar)
    cikan = sec.status.eq("çıktı").to_numpy()
    yil = ev.index.year
    kapsam = pd.DataFrame({
        "evren_ort": ev.sum(axis=1).groupby(yil).mean().round(0),
        "sonradan_cikan_ort": ev.loc[:, cikan].sum(axis=1).groupby(yil).mean().round(0),
        "finra_tahminli_ort": (ev & d.islem_kaynagi.eq("finra")).sum(axis=1).groupby(yil).mean().round(0),
        "islem_bilinmeyen_ort": d.islem_bilinmeyen.sum(axis=1).groupby(yil).mean().round(0),
    })
    rep = {"sure_sn": round(time.time() - t0), "kapsam": kapsam.reset_index(names="yil").to_dict("records")}
    (config.ROOT / "reports" / "research" / "arac_duzenek_kapsam.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(kapsam.to_string())
    return rep


if __name__ == "__main__":
    main()

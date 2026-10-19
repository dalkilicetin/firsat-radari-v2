"""Yürüyen model düzeneği — Aşama 0: veri seti (model_arastirma_plani.md).

Satır: her ayın ilk Cuması × hisse (evren: finans dışı, fiyat ≥ 1 $, günlük işlem ≥ 1 M$ bilinen).
Belirtiler: yalnızca o güne kadarki veri (fiyat geometrisi gerçek sayılar, güvenilir sinyaller tarih içi sıra, olaylar 0/1,
piyasa rejimi, sektör, ham gelir büyümesi, sızıntısız kâr sürprizi). Haber, metin, wiki, reddit yok; sue_fiyat yok.
Hedefler (ADLARI 'hedef_' ile başlar, asla belirti değildir): hedef_3a = sonraki 13 hafta brüt getiri, hedef_3a_net = maliyet
sonrası, hedef_6a = sonraki 26 hafta brüt getiri; tarih içi sıra etiketleri (ust1_3a, ust5_3a, ust5_6a ...).
Sızıntı önlemleri: satırlar tarih içinde rastgele karıştırılır (tablo sırası bugünkü büyüklüğe göreydi ve geleceği taşıyordu);
her belirtinin hedefle tarih içi Spearman uyumu ölçülür, |IC| > 0,15 olan belirti varsa kurulum durur.

python -m radar.research.yz_veri → data/derived/yz_veri.parquet, reports/research/yz_veri.json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel
from radar.research.esik_avi import data as esik_data
from radar.research.pattern_avi import CACHE, FRAME

OUT = config.DATA_DIR / "derived" / "yz_veri.parquet"
R = config.ROOT / "reports" / "research"
EVENTS = ["devamlilik_suphesi", "icerden_alim_kumesi_3plus", "ust_yonetici_alimi_90g", "8k_1.01_önemli anlaşma",
          "8k_1.02_anlaşma feshi", "8k_2.01_satın alma/elden çıkarma tamamlandı", "8k_2.03_yeni borç yükümlülüğü",
          "8k_3.02_kayıtsız hisse satışı (sulandırma)", "8k_5.02_yönetici değişikliği", "8k_7.01_kamuyu aydınlatma (FD)",
          "8k_8.01_diğer olaylar", "aktivist_13d", "pasif_13g_yeni", "gec_rapor_bildirimi", "hisse_ihraci"]
REGIME = ["piyasa_4h", "piyasa_52h", "piyasa_oynaklik_13h"]
NOT_FEATURES = {"cik", "tarih", "yil", "hedef_3a", "hedef_3a_net", "hedef_6a", "spy_3a", "spy_6a", "sektor"}


def build() -> pd.DataFrame:
    d = pd.read_parquet(CACHE).drop(columns=["__index_level_0__"], errors="ignore")
    d = d.rename(columns={"getiri_13h": "hedef_3a", "net": "hedef_3a_net", "spy": "spy_3a"})
    fr = pd.read_parquet(FRAME, columns=["tarih", "islem_tutari", "getiri_13h", "getiri_26h", "sektor"] + EVENTS + REGIME).reset_index()
    fr = fr[(fr.islem_tutari >= 1e6) & fr.getiri_13h.notna()].rename(columns={"getiri_26h": "hedef_6a"})
    fr = fr.drop(columns=["islem_tutari", "getiri_13h"])
    d = d.merge(fr, on=["tarih", "cik"], how="left")
    g = esik_data()[["tarih", "cik", "gelir"]].rename(columns={"gelir": "gelir_ham"})
    d = d.merge(g, on=["tarih", "cik"], how="left")
    dates = panel.fridays()
    spy = __import__("radar.research.context", fromlist=["x"]).etf_prices(dates)["SPY"]
    u = pd.DatetimeIndex(sorted(d.tarih.unique()))
    pos = dates.searchsorted(u)
    s6 = {t: (float(spy.iloc[i + 26] / spy.iloc[i] - 1) if i + 26 < len(spy) else np.nan) for t, i in zip(u, pos)}
    d["spy_6a"] = d.tarih.map(s6)
    d["sektor_kod"] = d.sektor.astype("category").cat.codes.astype("int16")
    d["islem_log"] = np.log10(d.islem_tutari.clip(lower=1))
    d = d.drop(columns=["islem_tutari"])
    # tarih içinde rastgele sıra
    rng = np.random.default_rng(20261019)
    d = d.iloc[rng.permutation(len(d))].sort_values("tarih", kind="stable").reset_index(drop=True)
    for h in ("3a", "6a"):
        rk = d.groupby("tarih")[f"hedef_{h}"].rank(pct=True)
        d[f"sira_{h}"] = rk
        d[f"ust1_{h}"] = (rk >= 0.99).astype("int8").where(rk.notna())
        d[f"ust5_{h}"] = (rk >= 0.95).astype("int8").where(rk.notna())
        d[f"buyuk_hareket_{h}"] = ((rk >= 0.95) | (rk <= 0.05)).astype("int8").where(rk.notna())
    return d


def features(d: pd.DataFrame) -> list[str]:
    return [c for c in d.columns if c not in NOT_FEATURES and not c.startswith(("sira_", "ust1_", "ust5_", "buyuk_hareket_"))
            and pd.api.types.is_numeric_dtype(d[c])]


def leak_check(d: pd.DataFrame, feats: list[str]) -> dict:
    out = {}
    sample = d[d.tarih.dt.month.isin([1, 4, 7, 10])]
    for f in feats:
        ic = sample.groupby("tarih")[[f, "hedef_3a"]].apply(
            lambda g: g[f].corr(g["hedef_3a"], method="spearman") if g[f].notna().sum() > 50 else np.nan)
        out[f] = float(ic.mean())
    return out


def main():
    d = build()
    feats = features(d)
    ic = leak_check(d, feats)
    bad = {k: v for k, v in ic.items() if abs(v) > 0.15}
    rep = {"satir": int(len(d)), "tarih": int(d.tarih.nunique()), "ilk": str(d.tarih.min().date()), "son": str(d.tarih.max().date()),
           "belirti": len(feats), "belirtiler": feats, "ic_en_yuksek_10": dict(sorted(ic.items(), key=lambda x: -abs(x[1]))[:10]),
           "sizinti_supheli": bad}
    (R / "yz_veri.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in rep.items() if k != "belirtiler"}, ensure_ascii=False, indent=1))
    if bad:
        raise SystemExit(f"SIZINTI ŞÜPHESİ: {bad}")
    d.to_parquet(OUT)


if __name__ == "__main__":
    main()

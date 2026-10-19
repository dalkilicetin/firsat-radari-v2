"""Temel kuralı daralt: dibin ≥ 2 katı + gelir ≥ %20 + en likit %30 içinde ek koşul ya da sıralama ile daha az hisse,
getiri temel kuraldan düşük olmamak şartıyla.

Belirtiler: yalnızca güvenilir ve BUGÜN (9 Ekim 2026) değeri bulunan belirtiler: fiyat geometrisi (pattern_avi.NEW, gerçek
sayılar) + önbellekteki haftalık sinyaller (sıra; haber, metin, wiki, tema hariç) + olaylar (0/1).
Daraltma türleri: (a) tek ek koşul (eşik: temel kurala uyan Ocak satırlarının %10…%90 değerleri, ≤ / ≥),
(b) iki ek koşul (en iyi 150 tek koşulun her biri × bütün koşullar), (c) sıralama: bir belirtiye göre en iyi K (3/5/8/10).
Portföy: uyan hisseler eşit ağırlık, 13 hafta, maliyet dahil; hiç hisse yoksa o dönem S&P (temel kural da aynı yöntemle).
Seçim YALNIZCA Ocak zincirinde: Ocak getirisi > temel, medyan hisse ≤ temelin yarısı, dönemlerin ≥ %80'inde yatırımda.
Doğrulama (görmediği): Şubat ve Mart zincirlerinin ikisinde de getiri ≥ temel; ayrıca 2010–2017 ve 2018–2026 (üç zincir
ortalaması) ikisinde de ≥ temel; tek hisse +%100 sınırıyla da ≥ temel.

python -m radar.research.daralt → reports/research/daralt.md, daralt.json, daralt_adaylar.csv, daralt_bugun.csv
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import fundamentals, library, panel, sectors
from radar.research.pattern_avi import CACHE, CHAINS, FRAME, NEW, QS, geometry, sue_raw
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit
from radar.research.road1 import REVENUE, by_filing, load_fin

R = config.ROOT / "reports" / "research"
SIG = ["momentum_12_1", "getiri_6a", "kisa_vade_donus", "zirveye_yakinlik_52h", "dusuk_oynaklik", "beta_qqq", "kucuk_boyut",
       "hacim_artisi", "gelir_buyumesi", "buyume_ivmesi", "brut_marj_degisimi", "faaliyet_marji_degisimi", "arge_yogunlugu",
       "serbest_nakit_getirisi", "kazanc_getirisi", "tahakkuklar_dusuk", "varlik_buyumesi_dusuk", "geri_alim_getirisi",
       "kazanc_aciklamasi_tepkisi", "icerden_alici_sayisi_90g", "icerden_alim_tutar_piyasa_degeri", "kurumsal_sahip_degisimi",
       "kurumsal_hisse_degisimi_payi", "sektor_getiri_13h", "sektor_momentum_12_1"]
EVENTS = ["devamlilik_suphesi", "icerden_alim_kumesi_3plus", "ust_yonetici_alimi_90g", "8k_1.01_önemli anlaşma",
          "8k_2.03_yeni borç yükümlülüğü", "8k_3.02_kayıtsız hisse satışı (sulandırma)", "8k_5.02_yönetici değişikliği",
          "8k_8.01_diğer olaylar"]
FEATS = NEW + SIG + EVENTS
KS = [3, 5, 8, 10]


def revenue_growth(p, dates):
    fin = fundamentals.plain(load_fin())
    rev = by_filing(fin, REVENUE, [1, 4])
    return pit(rev.rename(columns={"accepted": "date"}).assign(value=(rev.cur / rev.prev - 1).where(rev.prev > 0))[["cik", "date", "value"]],
               p["price"].index, p["price"].columns, FUNDAMENTAL_MAX_AGE).reindex(dates).clip(-1, 5)


def load_hist(p) -> pd.DataFrame:
    d = pd.read_parquet(CACHE, columns=["tarih", "cik", "net", "spy", "likidite"] + NEW + SIG)
    ev = pd.read_parquet(FRAME, columns=["tarih", "islem_tutari", "getiri_13h"] + EVENTS).reset_index()
    ev = ev[(ev.islem_tutari >= 1e6) & ev.getiri_13h.notna()][["tarih", "cik"] + EVENTS]
    d = d.merge(ev, on=["tarih", "cik"], how="left")
    dates = pd.DatetimeIndex(sorted(d.tarih.unique()))
    g = revenue_growth(p, dates)
    d["gelir"] = g.to_numpy()[dates.get_indexer(d.tarih), g.columns.get_indexer(d.cik.astype(str))]
    return d


def base_mask(x):
    return (x.dipten_52h >= 1.0) & (x.gelir >= 0.20) & (x.likidite >= 0.7)


class Eval:
    def __init__(self, b: pd.DataFrame):
        self.b = b
        self.dates = pd.DatetimeIndex(sorted(b.tarih.unique()))
        self.di = self.dates.get_indexer(b.tarih)
        self.spy = b.groupby("tarih").spy.first().reindex(self.dates).to_numpy()
        self.month, self.year = self.dates.month.to_numpy(), self.dates.year.to_numpy()
        self.net = b.net.to_numpy(np.float64)
        self.cap = np.minimum(self.net, 1.0)

    def run(self, m, cap=False):
        r = self.cap if cap else self.net
        s = np.bincount(self.di[m], weights=r[m], minlength=len(self.dates))
        n = np.bincount(self.di[m], minlength=len(self.dates))
        out = {}
        for ch, mm in CHAINS.items():
            sl = np.isin(self.month, mm) & np.isfinite(self.spy)
            inv = n[sl] >= 1
            rr = np.where(inv, s[sl] / np.maximum(n[sl], 1), self.spy[sl])
            w = np.cumprod(1 + rr)
            out[ch] = (float(w[-1] ** (4 / sl.sum()) - 1), float(inv.mean()), float(np.median(n[sl])),
                       float((w / np.maximum.accumulate(w) - 1).min()))
            for nm, (a, z) in {"y1": (2010, 2017), "y2": (2018, 2026)}.items():
                sl2 = sl & (self.year >= a) & (self.year <= z)
                inv2 = n[sl2] >= 1
                r2 = np.where(inv2, s[sl2] / np.maximum(n[sl2], 1), self.spy[sl2])
                out[f"{ch}_{nm}"] = float(np.prod(1 + r2) ** (4 / sl2.sum()) - 1)
        return out


def main() -> dict:
    t0 = time.time()
    p = panel.build()
    d = load_hist(p)
    b = d[base_mask(d).fillna(False)].reset_index(drop=True)
    E = Eval(b)
    ones = np.ones(len(b), bool)
    base = E.run(ones)
    base_cap = E.run(ones, cap=True)
    jan_rows = np.isin(b.tarih.dt.month.to_numpy(), CHAINS["ocak"])
    conds, names = [], []
    for f in FEATS:
        v = b[f].to_numpy(np.float64)
        if np.isfinite(v[jan_rows]).sum() < 50:
            continue
        for q, th in zip(QS, np.unique(np.nanquantile(v[jan_rows], QS))):
            conds.append(v <= th); names.append(f"{f} ≤ {th:.4g}")
            conds.append(v >= th); names.append(f"{f} ≥ {th:.4g}")
    M = np.vstack(conds)
    # sıralama: tarih içinde belirtiye göre en iyi K. EŞİTLİKLER RASTGELE bozulur: tablo satır sırası bugünkü büyüklüğe
    # göre (NVDA, TSLA, MU ...) ve geleceği taşır; 'ilk gelen' seçimi sızıntıdır (ilk 5 satır %14,3 / rastgele 5 %9,2).
    noise = np.random.default_rng(int(__import__("os").environ.get("DARALT_TOHUM", "20261019"))).random(len(b)) * 1e-9
    for f in FEATS:
        for asc in (False, True):
            rk = (b[f] + noise).groupby(b.tarih).rank(ascending=asc, method="first").to_numpy()
            for k in KS:
                conds.append(rk <= k); names.append(f"{f} {'en düşük' if asc else 'en yüksek'} {k}")
    M = np.vstack(conds)
    print(f"{len(b):,} temel satır, {len(names)} daraltma, {round(time.time() - t0)} sn", flush=True)

    def summarize(m):
        r = E.run(m)
        return {"ocak": r["ocak"][0], "subat": r["subat"][0], "mart": r["mart"][0], "kapsam": r["ocak"][1], "medyan_hisse": r["ocak"][2],
                "dusus": min(r[c][3] for c in CHAINS),
                "y1": np.mean([r[f"{c}_y1"] for c in CHAINS]), "y2": np.mean([r[f"{c}_y2"] for c in CHAINS])}

    rows = []
    for i, nm in enumerate(names):
        rows.append({"daraltma": nm, "tur": "sıralama" if (" en " in nm) else "tek koşul", **summarize(M[i])})
    t = pd.DataFrame(rows)
    ok1 = (t.kapsam >= 0.8) & (t.medyan_hisse <= base["ocak"][2] / 2)
    top = t[ok1 & ~(t.tur == "sıralama")].sort_values("ocak", ascending=False).head(150).index
    pair_rows = []
    for i in top:
        for j in range(len(names)):
            if j == i or " en " in names[j] or names[j].split(" ")[0] == names[i].split(" ")[0]:
                continue
            m = M[i] & M[j]
            if m.sum() < 30:
                continue
            pair_rows.append({"daraltma": f"{names[i]} VE {names[j]}", "tur": "iki koşul", **summarize(m)})
    t = pd.concat([t, pd.DataFrame(pair_rows)], ignore_index=True)
    print(f"toplam {len(t):,} aday ({round(time.time() - t0)} sn)", flush=True)
    bo, bs, bm = base["ocak"][0], base["subat"][0], base["mart"][0]
    by1 = np.mean([base[f"{c}_y1"] for c in CHAINS]); by2 = np.mean([base[f"{c}_y2"] for c in CHAINS])
    t["secim_sarti"] = (t.ocak > bo) & (t.kapsam >= 0.8) & (t.medyan_hisse <= base["ocak"][2] / 2)
    t["dogrulama"] = t.secim_sarti & (t.subat >= bs) & (t.mart >= bm) & (t.y1 >= by1) & (t.y2 >= by2)
    t = t.sort_values("ocak", ascending=False)
    t.round(4).to_csv(R / "daralt_adaylar.csv", index=False)
    sel = t[t.secim_sarti]
    out = {"temel": {"ocak": bo, "subat": bs, "mart": bm, "medyan_hisse": base["ocak"][2], "y1": by1, "y2": by2,
                     "sinirli_ocak_subat_mart": [base_cap[c][0] for c in CHAINS]},
           "aday": int(len(t)), "secim_sartini_gecen": int(len(sel)), "dogrulamayi_gecen": int(t.dogrulama.sum()),
           "ocakta_en_iyi_20": sel.head(20).round(4).to_dict(orient="records"),
           "dogrulamayi_gecen_en_iyi_20": t[t.dogrulama].sort_values(["subat", "mart"], ascending=False).head(20).round(4).to_dict(orient="records"),
           "ocakta_en_iyi_20_dogrulama_orani": float(sel.head(20).dogrulama.mean()) if len(sel) else None}
    # seçim kuralı: Ocak'ta en iyi ve doğrulamayı geçen ilk aday (sırayla), ayrıca tek hisse sınırıyla kontrol
    final = t[t.dogrulama].head(5)
    checks = []
    for r in final.itertuples():
        m = mask_of(r.daraltma, names, M)
        c = E.run(m, cap=True)
        checks.append({"daraltma": r.daraltma, "sinirli": [c[ch][0] for ch in CHAINS],
                       "sinirli_temelden_iyi": all(c[ch][0] >= base_cap[ch][0] for ch in CHAINS)})
    out["final_adaylar_sinirli_kontrol"] = checks
    (R / "daralt.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 110)
    print("TEMEL", json.dumps(out["temel"], default=float))
    print(out["aday"], out["secim_sartini_gecen"], out["dogrulamayi_gecen"], out["ocakta_en_iyi_20_dogrulama_orani"])
    cols = ["daraltma", "ocak", "subat", "mart", "medyan_hisse", "kapsam", "dusus", "y1", "y2", "dogrulama"]
    print(sel.head(20)[cols].round(3).to_string())
    print(t[t.dogrulama].head(20)[cols].round(3).to_string())
    print(json.dumps(checks, ensure_ascii=False, default=float))
    return out


def mask_of(rule, names, M):
    parts = rule.split(" VE ")
    m = np.ones(M.shape[1], bool)
    for pt in parts:
        m &= M[names.index(pt)]
    return m


if __name__ == "__main__":
    main()

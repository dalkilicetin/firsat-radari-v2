"""Yürüyen modellerin değerlendirmesi (ana analiz yöntemi biçiminde) + PBO + meta seçim. 2025–2026 KİLİTLİ.

Geliştirme: 2013–2024 çeyrek başları. Her model, her çeyrek: puana göre ilk 3 ve ilk 10 hisse (eşitlik rastgele), 3 ay / 6 ay
brüt getiri; aynı çeyreğin gerçek en iyi 3'ü; S&P. Yakalama: seçilenlerin en iyi %1 / %5 / ilk 20'de olma oranı.
Güven aralığı: yıllık blok bootstrap (10.000, tohum 20261012, %90). PBO: CSCV (8 blok, 4'ü dışarıda, 70 bölme) çeyreklik
ilk-3 getirisi üzerinden. Meta seçim: her yıl, yalnızca önceki yılların görülmemiş sonuçlarına göre en iyi model seçilir.
Kilit: --kilitli verilirse ve reports/research/yz_secim.json git'te commit edilmişse 2025–2026 de raporlanır.

python -m radar.research.yz_degerlendir [--kilitli] → reports/research/yz_sonuc.md, yz_sonuc.json, yz_donemler.csv
"""

from __future__ import annotations

import itertools
import json
import subprocess
import sys

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel
from radar.research.donem_tablosu import symbols
from radar.research.yz_model import TAHMIN
from radar.research.yz_veri import OUT as VERI

R = config.ROOT / "reports" / "research"
SECIM = R / "yz_secim.json"
DEV = (2013, 2024)
LEARNED = ["kural_ogrenici", "lgb_sinif5", "lgb_sinif1", "lgb_sirala", "lgb_sirala_6a", "iki_asama", "kuyruk_q90", "topluluk"]
BASE = ["rastgele", "momentum_buyuk"]


def load():
    cols = ["tarih", "cik", "hedef_3a", "hedef_6a", "hedef_3a_net", "spy_3a", "spy_6a", "sira_3a", "dipten_52h", "gelir_ham",
            "likidite", "sektor_momentum_12_1", "ort_10_40"]
    d = pd.read_parquet(VERI, columns=cols)
    d = d[d.tarih.dt.month.isin([1, 4, 7, 10]) & (d.tarih.dt.year >= 2013)].copy()
    preds = {}
    for f in sorted(TAHMIN.glob("*.parquet")):
        p = pd.read_parquet(f)
        preds[f.stem] = p.set_index(["tarih", "cik"]).puan
    key = pd.MultiIndex.from_frame(d[["tarih", "cik"]])
    for k, s in preds.items():
        d[k] = s.reindex(key).to_numpy()
    # sabit kurallar (veriyi gördü — yalnızca kıyas)
    base = (d.dipten_52h >= 1.0) & (d.gelir_ham >= 0.2) & (d.likidite >= 0.7)
    d["kural_A_gordu"] = np.where(base & (d.sektor_momentum_12_1 >= 0.8694), d.dipten_52h, -np.inf)
    d["kural_B_gordu"] = np.where(base & (d.sektor_momentum_12_1 >= 0.8694) & (d.ort_10_40 >= 0.1909), d.dipten_52h, -np.inf)
    parts = [c for c in ("lgb_sinif5", "lgb_sirala", "kuyruk_q90") if c in d]
    if len(parts) == 3:
        d["topluluk"] = sum(d.groupby("tarih")[c].rank(pct=True) for c in parts) / 3
    return d


def picks(d, model, k):
    rng = np.random.default_rng(20261019)
    s = d[model].to_numpy(dtype=float) + rng.random(len(d)) * 1e-12
    d = d.assign(_s=s)
    d = d[np.isfinite(d._s)]
    return d.sort_values(["tarih", "_s"], ascending=[True, False]).groupby("tarih").head(k)


def quarter_table(d, models):
    rows = []
    for t, g in d.groupby("tarih"):
        top = g.nlargest(3, "hedef_3a")
        top20 = set(g.nlargest(20, "hedef_3a").cik)
        base = {"tarih": t, "yil": t.year, "spy_3a": g.spy_3a.iloc[0], "spy_6a": g.spy_6a.iloc[0],
                "en_iyi3_3a": top.hedef_3a.mean(), "en_iyi3_6a": top.hedef_6a.mean(), "en_iyi3": list(top.cik)}
        rows.append(base)
    q = pd.DataFrame(rows).set_index("tarih")
    for m in models:
        for k in (3, 10):
            p = picks(d, m, k)
            g = p.groupby("tarih")
            q[f"{m}@{k}_3a"] = g.hedef_3a.mean()
            q[f"{m}@{k}_6a"] = g.hedef_6a.mean()
            q[f"{m}@{k}_net3a"] = g.hedef_3a_net.mean()
            q[f"{m}@{k}_ust1"] = g.sira_3a.apply(lambda s: float((s >= 0.99).mean()))
            q[f"{m}@{k}_ust5"] = g.sira_3a.apply(lambda s: float((s >= 0.95).mean()))
            if k == 3:
                q[f"{m}@3_hisseler"] = g.cik.apply(list)
    return q


def boot_ci(diff: pd.Series, years: pd.Series, n=10000, seed=20261012):
    rng = np.random.default_rng(seed)
    by = {y: diff[years == y].to_numpy() for y in sorted(years.unique())}
    ys = list(by)
    vals = []
    for _ in range(n):
        pick = rng.choice(len(ys), len(ys))
        vals.append(np.mean(np.concatenate([by[ys[i]] for i in pick])))
    return float(np.percentile(vals, 5)), float(np.percentile(vals, 95))


def pbo(mat: pd.DataFrame, blocks=8, test_blocks=4) -> float:
    """CSCV: her bölmede eğitimde en iyi olan konfigürasyonun testteki sırası; sırası medyanın altındaysa aşırı uyum."""
    idx = np.array_split(np.arange(len(mat)), blocks)
    lam = []
    for comb in itertools.combinations(range(blocks), test_blocks):
        te = np.concatenate([idx[i] for i in comb])
        tr = np.concatenate([idx[i] for i in range(blocks) if i not in comb])
        best = mat.iloc[tr].mean().idxmax()
        rk = mat.iloc[te].mean().rank(pct=True)[best]
        lam.append(rk)
    lam = np.array(lam)
    return float((lam <= 0.5).mean())


def summarize(q, models, mom="momentum_buyuk"):
    out = {}
    for m in models:
        r = {}
        for k in (3, 10):
            c = f"{m}@{k}"
            x = q[f"{c}_3a"]
            ok = x.notna()
            r[f"ilk{k}_3a"] = float(x.mean())
            r[f"ilk{k}_6a"] = float(q[f"{c}_6a"].mean())
            r[f"ilk{k}_spy_ustu"] = float((x[ok] > q.spy_3a[ok]).mean())
            r[f"ilk{k}_ust1_orani"] = float(q[f"{c}_ust1"].mean())
            r[f"ilk{k}_ust5_orani"] = float(q[f"{c}_ust5"].mean())
            net = q[f"{c}_net3a"].fillna(q.spy_3a)
            r[f"ilk{k}_net_yillik_bilesik"] = float(np.prod(1 + net) ** (4 / len(net)) - 1)
            w = np.cumprod(1 + net.to_numpy())
            r[f"ilk{k}_en_kotu_dusus"] = float((w / np.maximum.accumulate(w) - 1).min())
            dspy = (x - q.spy_3a)[ok]
            r[f"ilk{k}_spy_farki_ci90"] = boot_ci(dspy, q.yil[ok])
            if m != mom and f"{mom}@{k}_3a" in q:
                dm = (x - q[f"{mom}@{k}_3a"])[ok]
                r[f"ilk{k}_momentum_farki"] = float(dm.mean())
                r[f"ilk{k}_momentum_farki_ci90"] = boot_ci(dm, q.yil[ok])
            r["donem"] = int(ok.sum())
        out[m] = r
    return out


def meta(q, models, start=2016):
    rows = {}
    for y in range(start, int(q.yil.max()) + 1):
        past = q[q.yil < y]
        best = max(models, key=lambda m: past[f"{m}@3_3a"].mean())
        cur = q[q.yil == y]
        for t in cur.index:
            rows[t] = {"secilen_model": best, "meta@3_3a": cur.at[t, f"{best}@3_3a"], "meta@3_6a": cur.at[t, f"{best}@3_6a"],
                       "meta@10_3a": cur.at[t, f"{best}@10_3a"], "meta@10_net3a": cur.at[t, f"{best}@10_net3a"]}
    return pd.DataFrame(rows).T


def holdout_allowed() -> bool:
    if not SECIM.exists():
        return False
    r = subprocess.run(["git", "status", "--porcelain", str(SECIM)], capture_output=True, text=True, cwd=config.ROOT)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(SECIM)], capture_output=True, cwd=config.ROOT).returncode == 0
    return tracked and r.stdout.strip() == ""


def main(kilitli: bool):
    d = load()
    models = [m for m in BASE + LEARNED + ["kural_A_gordu", "kural_B_gordu"] if m in d]
    if kilitli and not holdout_allowed():
        raise SystemExit("Kilit: önce reports/research/yz_secim.json yazılıp commit edilmeli.")
    dev = d[(d.tarih.dt.year >= DEV[0]) & (d.tarih.dt.year <= DEV[1])]
    q = quarter_table(dev, models)
    s = summarize(q, models)
    learned = [m for m in models if m in LEARNED]
    pbo_v = pbo(q[[f"{m}@3_3a" for m in learned]].apply(lambda c: c.fillna(q.spy_3a))) if len(learned) >= 3 else None
    mt = meta(q, [m for m in models if m in BASE + LEARNED])
    res = {"gelistirme": s, "pbo_ilk3": pbo_v, "meta_ilk3_3a": float(mt["meta@3_3a"].mean()),
           "meta_ilk3_6a": float(mt["meta@3_6a"].mean()), "meta_secimleri": mt.secilen_model.groupby(mt.index.year).first().to_dict(),
           "spy_3a": float(q.spy_3a.mean()), "spy_6a": float(q.spy_6a.mean()), "en_iyi3_3a": float(q.en_iyi3_3a.mean()),
           "en_iyi3_6a": float(q.en_iyi3_6a.mean())}
    if kilitli:
        ho = d[d.tarih.dt.year >= 2025]
        qh = quarter_table(ho, models)
        res["kilitli_2025_2026"] = summarize(qh, models)
        q = pd.concat([q, qh])
    write(q, res, models)
    return res


def write(q, res, models):
    p = panel.build()
    sym = symbols(p)
    names = lambda lst, t: ", ".join(sym(str(c), t) for c in lst) if isinstance(lst, list) else "—"
    rows = []
    for t, r in q.iterrows():
        rows.append({"tarih": str(t.date()), "model": "EN YÜKSEK GETİRİ", "hisseler": names(r.en_iyi3, t), "3a": r.en_iyi3_3a, "6a": r.en_iyi3_6a})
        for m in models:
            rows.append({"tarih": str(t.date()), "model": m, "hisseler": names(r.get(f"{m}@3_hisseler"), t),
                         "3a": r.get(f"{m}@3_3a"), "6a": r.get(f"{m}@3_6a")})
        rows.append({"tarih": str(t.date()), "model": "S&P 500", "hisseler": "", "3a": r.spy_3a, "6a": r.spy_6a})
    pd.DataFrame(rows).to_csv(R / "yz_donemler.csv", index=False)
    (R / "yz_sonuc.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    pct = lambda v: "—" if v is None or not np.isfinite(v) else f"{v * 100:+,.1f}%"
    L = ["# Yürüyen Modeller — Görülmemiş Veride Sonuçlar (geliştirme 2013–2024)", "",
         "Her test yılı için model yalnızca etiketi o yıl başlamadan kapanmış verilerle eğitildi; ayarlar sabit. 2025–2026 kilitli.", "",
         "| Model | İlk 3: ort. 3 ay | İlk 3: ort. 6 ay | İlk 3: S&P'yi geçen çeyrek | İlk 3 en iyi %5'te | İlk 10: ort. 3 ay | İlk 10: net bileşik yıllık | İlk 10 en kötü düşüş | İlk 3 − S&P (%90 GA) | İlk 3 − momentum (%90 GA) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for m, r in res["gelistirme"].items():
        ci = r["ilk3_spy_farki_ci90"]
        cm = r.get("ilk3_momentum_farki_ci90")
        L.append(f"| {m} | {pct(r['ilk3_3a'])} | {pct(r['ilk3_6a'])} | {pct(r['ilk3_spy_ustu'])} | {pct(r['ilk3_ust5_orani'])} | "
                 f"{pct(r['ilk10_3a'])} | {pct(r['ilk10_net_yillik_bilesik'])} | {pct(r['ilk10_en_kotu_dusus'])} | "
                 f"{pct(ci[0])} … {pct(ci[1])} | {'—' if cm is None else pct(cm[0]) + ' … ' + pct(cm[1])} |")
    L += ["", f"- S&P 500: 3 ay {pct(res['spy_3a'])}, 6 ay {pct(res['spy_6a'])}. Gerçek en iyi 3: 3 ay {pct(res['en_iyi3_3a'])}, 6 ay {pct(res['en_iyi3_6a'])}.",
          f"- Rastgele beklenti: en iyi %5'te olma %5.",
          f"- Aşırı uyum olasılığı (PBO, öğrenen modeller arasında): {pct(res['pbo_ilk3']) if res['pbo_ilk3'] is not None else '—'}.",
          f"- Meta seçim (her yıl yalnızca geçmiş sonuçlara göre model seçimi, 2016–2024): ilk 3 ort. 3 ay {pct(res['meta_ilk3_3a'])}, 6 ay {pct(res['meta_ilk3_6a'])}. Seçimler: {res['meta_secimleri']}",
          "- 'kural_A_gordu' / 'kural_B_gordu': geçmişin tamamına bakılarak bulunmuş kurallar; yalnızca kıyas, görülmemiş sayılmaz.", ""]
    (R / "yz_sonuc.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main("--kilitli" in sys.argv)

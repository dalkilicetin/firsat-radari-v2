"""Sistematik pattern araması (yalnızca güvenilir veri): tek belirti ve ikili kombinasyonlar, üç havuzda.

Seçim Ocak zincirinde (Oca/Nis/Tem/Eki başları), doğrulama görmediği Şubat ve Mart zincirlerinde. Her kural: havuzdaki
hisseleri puana göre sırala, en iyi 10'u eşit ağırlıkla 13 hafta tut, maliyet dahil (alış + satış).
Puan: belirtinin o tarihteki sırası (yön: + yüksek iyi, − düşük iyi); ikili kombinasyonda iki sıranın ortalaması.
Havuzlar: tümü; piyango (küçük ≥ 0,7, fiyat ≤ 0,3, oynaklık ≥ 0,7); büyük (küçük şirket ≤ 0,3 ve likidite ≥ 0,7).
Çoklu deneme uyarısı: binlerce kural denenince en iyisi şans eseri iyi görünür. Bu yüzden 'sağlam' kural:
Ocak zincirinde seçilip Şubat ve Mart zincirlerinin İKİSİNDE de S&P'yi geçen ve 2010–2017 ile 2018–2026'nın İKİSİNDE de
(üç zincirin ortalamasıyla) S&P'yi geçen kural.

python -m radar.research.pattern_arama  →  reports/research/pattern_arama.json, pattern_arama.csv
"""

from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, panel
from radar.research.kazanan_profili import AD
from radar.research.pattern_testi import cost

R = config.ROOT / "reports" / "research"
FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
N = 10
CHAINS = {"ocak": (1, 4, 7, 10), "subat": (2, 5, 8, 11), "mart": (3, 6, 9, 12)}
FEATS = [f for f in AD if f not in ("bilanco_uzerinden_hafta",)]


def load():
    cols = ["tarih", "islem_tutari", "getiri_13h"] + FEATS
    df = pd.read_parquet(FRAME, columns=list(dict.fromkeys(cols)))
    df = df[(df.islem_tutari >= 1e6) & df.getiri_13h.notna()].copy()
    df["maliyet"] = 2 * cost(df.islem_tutari).to_numpy()
    df["net"] = df.getiri_13h - df.maliyet
    dates = panel.fridays()
    spy = context.etf_prices(dates)["SPY"]
    idx = dates.searchsorted(df.tarih.drop_duplicates().sort_values())
    sp = {t: (float(spy.iloc[i + 13] / spy.iloc[i] - 1) if i + 13 < len(spy) else np.nan)
          for t, i in zip(df.tarih.drop_duplicates().sort_values(), idx)}
    pools = {"tümü": np.ones(len(df), bool),
             "piyango": ((df.kucuk_boyut >= 0.7) & (df.fiyat_seviyesi <= 0.3) & (df.ivol_3a >= 0.7)).to_numpy(),
             "büyük": ((df.kucuk_boyut <= 0.3) & (df.likidite >= 0.7)).to_numpy()}
    blocks = []
    for t, g in df.groupby("tarih"):
        blocks.append({"t": t, "ay": t.month, "yil": t.year, "X": g[FEATS].to_numpy(np.float32), "net": g.net.to_numpy(),
                       "pools": {k: v[df.tarih.to_numpy() == t] for k, v in pools.items()}, "spy": sp[t]})
    return blocks


def run_rule(blocks, cols, signs, pool):
    """Her blok için seçilen 10 hissenin net getirisi (seçim yoksa NaN)."""
    out = np.full(len(blocks), np.nan)
    for b_i, b in enumerate(blocks):
        m = b["pools"][pool]
        X = b["X"][m][:, cols]
        s = np.where(np.asarray(signs) > 0, X, 1 - X)
        score = np.nanmean(s, axis=1) if len(cols) > 1 else s[:, 0]
        ok = np.isfinite(score)
        if ok.sum() < N:
            continue
        sc, r = score[ok], b["net"][m][ok]
        top = np.argpartition(-sc, N - 1)[:N]
        out[b_i] = r[top].mean()
    return out


def cagr(r, n_per_year=4):
    r = r[np.isfinite(r)]
    return float(np.prod(1 + r) ** (n_per_year / len(r)) - 1) if len(r) else np.nan


def evaluate(blocks, rets):
    b = pd.DataFrame({"ay": [x["ay"] for x in blocks], "yil": [x["yil"] for x in blocks], "spy": [x["spy"] for x in blocks],
                      "r": rets}).dropna()
    res = {}
    for ch, months in CHAINS.items():
        d = b[b.ay.isin(months)]
        res[ch] = cagr(d.r.to_numpy()) - cagr(d.spy.to_numpy())
    for nm, (a, z) in {"ilk_yari": (2010, 2017), "ikinci_yari": (2018, 2026)}.items():
        d = b[(b.yil >= a) & (b.yil <= z)]
        res[nm] = cagr(d.r.to_numpy(), 12) - cagr(d.spy.to_numpy(), 12)  # aylık başlangıçlar, çakışan 13 hafta: kaba ölçü
    res["ocak_cagr"] = cagr(b[b.ay.isin(CHAINS["ocak"])].r.to_numpy())
    res["subat_cagr"] = cagr(b[b.ay.isin(CHAINS["subat"])].r.to_numpy())
    res["mart_cagr"] = cagr(b[b.ay.isin(CHAINS["mart"])].r.to_numpy())
    return res


def main():
    blocks = load()
    rows = []
    # 1) tek belirtiler, iki yön, üç havuz
    for pool in ("tümü", "piyango", "büyük"):
        for j, f in enumerate(FEATS):
            for sgn in (1, -1):
                ev = evaluate(blocks, run_rule(blocks, [j], [sgn], pool))
                rows.append({"havuz": pool, "kural": f"{'+' if sgn > 0 else '−'}{f}", "n_belirti": 1} | ev)
    single = pd.DataFrame(rows)
    # 2) ikili kombinasyonlar: her havuzda Ocak zincirinde en iyi 25 tek kural arasından
    for pool in ("tümü", "piyango", "büyük"):
        best = single[single.havuz == pool].sort_values("ocak", ascending=False).head(25)
        parsed = [(FEATS.index(k[1:]), 1 if k[0] == "+" else -1, k) for k in best.kural]
        for (j1, s1, k1), (j2, s2, k2) in itertools.combinations(parsed, 2):
            if j1 == j2:
                continue
            ev = evaluate(blocks, run_rule(blocks, [j1, j2], [s1, s2], pool))
            rows.append({"havuz": pool, "kural": f"{k1} & {k2}", "n_belirti": 2} | ev)
    t = pd.DataFrame(rows)
    t["sağlam"] = (t.ocak > 0) & (t.subat > 0) & (t.mart > 0) & (t.ilk_yari > 0) & (t.ikinci_yari > 0)
    t["gorulmeyen_ort"] = (t.subat + t.mart) / 2
    t.round(4).to_csv(R / "pattern_arama.csv", index=False)
    # Ocak'ta seçilen en iyi kuralların görmediği aylardaki sonucu
    top_jan = t.sort_values("ocak", ascending=False).head(20)
    out = {"denenen_kural": int(len(t)), "sağlam_kural": int(t["sağlam"].sum()),
           "ocakta_en_iyi_20_gorulmeyende": top_jan[["havuz", "kural", "ocak", "subat", "mart", "ilk_yari", "ikinci_yari",
                                                    "ocak_cagr", "subat_cagr", "mart_cagr"]].round(4).to_dict(orient="records"),
           "sağlam_kurallar": t[t["sağlam"]].sort_values("gorulmeyen_ort", ascending=False).head(30)[
               ["havuz", "kural", "ocak", "subat", "mart", "ilk_yari", "ikinci_yari", "ocak_cagr", "subat_cagr", "mart_cagr"]].round(4).to_dict(orient="records"),
           "ocak_ile_gorulmeyen_iliskisi": float(t[["ocak", "gorulmeyen_ort"]].corr().iloc[0, 1])}
    (R / "pattern_arama.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in out.items() if k not in ("ocakta_en_iyi_20_gorulmeyende", "sağlam_kurallar")}, ensure_ascii=False))
    pd.set_option("display.width", 250)
    print(pd.DataFrame(out["ocakta_en_iyi_20_gorulmeyende"]).to_string())
    print(pd.DataFrame(out["sağlam_kurallar"]).to_string())


if __name__ == "__main__":
    main()

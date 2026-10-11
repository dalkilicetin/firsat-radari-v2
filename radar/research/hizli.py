"""Hızlı iterasyon motoru: python -m radar.research.hizli [aylik|haftalik] [deneme_adı ...]

Amaç: bir denemeyi ~1 dakikada ölçmek. Test yılları 2018–2021; her test yılı için model yalnızca o yıldan önceki son
PENCERE yılda eğitilir (iç içe; 4 hafta/1 hafta getiri sınırı gözetilir). Bir koşuda birden çok deneme (belirti grubu,
hedef türü, ayar) karşılaştırılır; her sonuç reports/research/hizli_denemeler.jsonl'a yazılır.
Uyarı: 2018–2021'e göre seçilen en iyi ayar, en sonda bir kez bütün yıllarda (monthly_ml) doğrulanmalıdır.
Ölçütler: maliyet sonrası dönem getirisi (devir tabanlı, backtest.cost_rate), dönemin en iyi %5'inden yakalanan hisse
(rastgele: 1,0), yakalama oranı (en iyi 20'ye göre), zararlı yıl.
"""

from __future__ import annotations

import json
import sys
import time

import lightgbm as lgb
import numpy as np
import pandas as pd

from radar import config
from radar.research.backtest import cost_rate

D = config.ROOT / "data" / "derived"
LOG = config.ROOT / "reports" / "research" / "hizli_denemeler.jsonl"
META = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari"}
TEST_YEARS = (2018, 2019, 2020, 2021)
PENCERE = 5
K = 20
BASE = dict(objective="binary", learning_rate=0.05, num_leaves=31, min_child_samples=400, feature_fraction=0.6,
            bagging_fraction=0.7, bagging_freq=1, lambda_l2=10.0, verbose=-1, seed=0, num_threads=4)
ROUNDS = 200

# Belirti grupları (ada göre; deneme hangi grupları kullanacağını seçer)
GROUPS = {
    "fiyat": lambda c: c in {"momentum_12_1", "kisa_vade_donus", "dusuk_oynaklik", "kucuk_boyut", "zirveye_yakinlik_52h",
                              "getiri_6a", "getiri_1a", "hacim_artisi", "fiyat_seviyesi", "beta_qqq", "likidite"},
    "sektor_piyasa": lambda c: c.startswith(("sektor_", "piyasa_")),
    "temel": lambda c: c in {"gelir_buyumesi", "buyume_ivmesi", "brut_marj_degisimi", "faaliyet_marji_degisimi", "arge_yogunlugu",
                              "serbest_nakit_getirisi", "kazanc_getirisi", "tahakkuklar_dusuk", "varlik_buyumesi_dusuk"},
    "metin": lambda c: c.startswith(("metin_", "risk_bolumu", "devamlilik")),
    "kurumsal_olay": lambda c: c.startswith(("8k_", "icerden", "ust_yonetici", "kurumsal_", "geri_alim")),
    "haber": lambda c: c.startswith(("haber_", "wiki_", "tema_", "yukselen_")),
    "yeni": lambda c: c in {"bilanco_uzerinden_hafta", "bilanco_bu_ay_bekleniyor", "sektorun_gerisinde", "oynaklik_genislemesi",
                             "max_haftalik_4h", "kirilim", "kazanc_aciklamasi_tepkisi"},
}
ALL = list(GROUPS)

# Denemeler: ad → (hedef türü, belirti grupları, ek ayar)
EXPERIMENTS = {
    "sira_hepsi": ("sira", ALL, {}),
    "fark_hepsi": ("fark", ALL, {}),
    "kazanan_hepsi": ("kazanan", ALL, {}),
    "sira_habersiz": ("sira", [g for g in ALL if g != "haber"], {}),
    "sira_yenisiz": ("sira", [g for g in ALL if g != "yeni"], {}),
    "sira_likit": ("sira", ALL, {"min_likidite": 0.5}),
    "fark_likit": ("fark", ALL, {"min_likidite": 0.5}),
}


def load(freq: str) -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_parquet(D / ("aylik_cerceve.parquet" if freq == "aylik" else "haftalik_cerceve.parquet"))
    df = df[np.isfinite(df.getiri) & (df.yil >= min(TEST_YEARS) - PENCERE - 1) & (df.yil <= max(TEST_YEARS))].copy()
    feats = [c for c in df.columns if c not in META and pd.api.types.is_numeric_dtype(df[c])]
    q = df.groupby("tarih").getiri.rank(pct=True)
    df["hedef"], df["kaybeden"], df["sira"] = (q > 0.95).astype(int), (q <= 0.05).astype(int), q
    return df, feats


def score(mode: str, tr: pd.DataFrame, te: pd.DataFrame, feats: list[str], params: dict) -> tuple[np.ndarray, lgb.Booster]:
    p = BASE | params.get("lgb", {})
    if mode == "kazanan":
        m = lgb.train(p, lgb.Dataset(tr[feats], tr.hedef), ROUNDS)
        return m.predict(te[feats]), m
    if mode == "fark":
        m = lgb.train(p, lgb.Dataset(tr[feats], tr.hedef), ROUNDS)
        lose = lgb.train(p, lgb.Dataset(tr[feats], tr.kaybeden), ROUNDS)
        return m.predict(te[feats]) - params.get("lam", 1.0) * lose.predict(te[feats]), m
    m = lgb.train(p | {"objective": "regression"}, lgb.Dataset(tr[feats], tr.sira), ROUNDS)
    return m.predict(te[feats]), m


def run(freq: str, name: str, df: pd.DataFrame, all_feats: list[str]) -> dict:
    mode, groups, params = EXPERIMENTS[name]
    feats = [c for c in all_feats if any(GROUPS[g](c) for g in groups)]
    gap = pd.Timedelta(weeks=4 if freq == "aylik" else 1)
    years, imps = [], pd.Series(0.0, index=feats)
    t0 = time.time()
    for Y in TEST_YEARS:
        start = pd.Timestamp(f"{Y}-01-01")
        tr = df[(df.tarih + gap < start) & (df.yil >= Y - PENCERE)]
        te = df[df.yil == Y]
        if "min_likidite" in params:
            tr, te = tr[tr.likidite >= params["min_likidite"]], te[te.likidite >= params["min_likidite"]]
        s, model = score(mode, tr, te, feats, params)
        imps += pd.Series(model.feature_importance("gain"), index=feats)
        te = te.assign(puan=s)
        gross, net, hits, caps = [], [], [], []
        held: dict = {}
        for _, g in te.groupby("tarih"):
            top = g.nlargest(K, "puan")
            r = top.getiri.mean()
            rate = dict(zip(top.index.astype(str), cost_rate(top.islem_tutari.fillna(0)).to_numpy()))
            c = (sum(v for k, v in rate.items() if k not in held) + sum(v for k, v in held.items() if k not in rate)) / K
            held = rate
            gross.append(r); net.append(r - c); hits.append(int(top.hedef.sum())); caps.append(r / g.getiri.nlargest(K).mean())
        years.append({"yil": Y, "brut": float(np.prod(1 + np.array(gross)) - 1), "net": float(np.prod(1 + np.array(net)) - 1),
                      "en_iyi_yuzde5": float(np.mean(hits)), "yakalama": float(np.mean(caps))})
    res = pd.DataFrame(years)
    imp = (imps / imps.sum()).sort_values(ascending=False)
    out = {"zaman": time.strftime("%Y-%m-%d %H:%M"), "ufuk": freq, "deneme": name, "hedef": mode, "gruplar": groups,
           "ayar": params, "yillar": list(TEST_YEARS), "net_yillik_ort": float(res.net.mean()), "brut_yillik_ort": float(res.brut.mean()),
           "zararli_yil": int((res.net < 0).sum()), "en_iyi_yuzde5_ort": float(res.en_iyi_yuzde5.mean()),
           "yakalama_ort": float(res.yakalama.mean()), "yil_yil_net": [round(x, 3) for x in res.net],
           "onemli": [f"{k} {v:.0%}" for k, v in imp.head(8).items()], "sure_sn": round(time.time() - t0)}
    with LOG.open("a") as f:
        f.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"{name:16s} net {out['net_yillik_ort']:+.0%}/yıl (brüt {out['brut_yillik_ort']:+.0%}), zararlı {out['zararli_yil']}/4, "
          f"en iyi %5'ten {out['en_iyi_yuzde5_ort']:.1f}, yıllar {out['yil_yil_net']} [{out['sure_sn']} sn]  önemli: {out['onemli'][:4]}",
          flush=True)
    return out


if __name__ == "__main__":
    freq = sys.argv[1] if len(sys.argv) > 1 else "aylik"
    names = sys.argv[2:] or list(EXPERIMENTS)
    df, feats = load(freq)
    print(f"{freq}: {len(df):,} satır, {len(feats)} belirti", flush=True)
    for n in names:
        run(freq, n, df, feats)

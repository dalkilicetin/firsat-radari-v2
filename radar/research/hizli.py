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
META = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari", "getiri_13h", "getiri_26h", "getiri_52h", "getiri_104h"}
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
    "haber": lambda c: c.startswith(("haber_", "wiki_", "tema_", "yukselen_konu")),
    "oranlar": lambda c: c in {"defter_fiyat", "satis_fiyat", "favok_fd", "temettu_verimi", "nakit_piyasa", "ozsermaye_karliligi",
                                "aktif_karliligi", "brut_kar_aktif", "brut_marj", "faaliyet_marji", "borc_ozsermaye", "cari_oran",
                                "faiz_karsilama", "altman_z", "piotroski_f", "kar_buyumesi", "hisse_sayisi_degisimi"},
    "teknik": lambda c: c in {"rsi_14h", "ort_10h_uzaklik", "ort_40h_uzaklik", "macd", "bollinger_konum"},
    "alternatif": lambda c: c.startswith(("reddit_", "yukselen_kelime", "yukselen_kurum", "yeni_kurum")),
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
    # Yeni verinin katkısı (en istikrarlı ayar: sıra, 10 hisse, 5 yıl pencere)
    "en_iyi_hepsi": ("sira", ALL, {"k": 10}),
    "en_iyi_alternatifsiz": ("sira", [g for g in ALL if g != "alternatif"], {"k": 10}),
    "en_iyi_haber_alternatifsiz": ("sira", [g for g in ALL if g not in ("alternatif", "haber")], {"k": 10}),
    "en_iyi_oransiz": ("sira", [g for g in ALL if g not in ("oranlar", "teknik")], {"k": 10}),
}


# Ufuk → (hafta, hedef sütunu, yıl içindeki seçim ayları)
UFUK = {"aylik": (4, "getiri", range(1, 13)), "3ay": (13, "getiri_13h", (1, 4, 7, 10)), "6ay": (26, "getiri_26h", (1, 7)),
        "1yil": (52, "getiri_52h", (1,)), "2yil": (104, "getiri_104h", (1,))}


def grid() -> dict:
    """Sistematik denemeler: belirti grubu çıkarma + parametre taraması (temel: sıra, likit ≥ 0,5, 20 hisse, 5 yıl)."""
    base = {"min_likidite": 0.5}
    ex = {"temel_sira_likit": ("sira", ALL, base)}
    for g in ALL:
        ex[f"cikar_{g}"] = ("sira", [x for x in ALL if x != g], base)
    for k in (10, 30):
        ex[f"k{k}"] = ("sira", ALL, base | {"k": k})
    for lq in (0.0, 0.3, 0.7):
        ex[f"likidite_{lq}"] = ("sira", ALL, {"min_likidite": lq})
    for pw in (3, 8):
        ex[f"pencere_{pw}"] = ("sira", ALL, base | {"pencere": pw})
    ex["sade_model"] = ("sira", ALL, base | {"lgb": {"num_leaves": 7, "min_child_samples": 1500}})
    ex["karmasik_model"] = ("sira", ALL, base | {"lgb": {"num_leaves": 63, "min_child_samples": 200}, "rounds": 400})
    for w in (0.25, 0.5):
        ex[f"karisim_{w}"] = ("karisim", ALL, base | {"w": w})
    return ex


def load(freq: str) -> tuple[pd.DataFrame, list[str]]:
    weeks, col, _ = UFUK[freq]
    df = pd.read_parquet(D / "aylik_cerceve.parquet")
    df = df[(df.yil >= min(TEST_YEARS) - 11) & (df.yil <= max(TEST_YEARS))].copy()
    df["getiri"] = df[col]
    df = df[np.isfinite(df.getiri)]
    feats = [c for c in df.columns if c not in META and not c.startswith("getiri_") or c in ("getiri_6a", "getiri_1a")]
    feats = [c for c in feats if c not in META and pd.api.types.is_numeric_dtype(df[c])]
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
    if mode == "karisim":  # sıra puanı ile fark puanının dönem içi sıralarının ağırlıklı ortalaması
        s1, m = score("sira", tr, te, feats, params)
        s2, _ = score("fark", tr, te, feats, params)
        r1 = pd.Series(s1, index=te.index).groupby(te.tarih).rank(pct=True)
        r2 = pd.Series(s2, index=te.index).groupby(te.tarih).rank(pct=True)
        w = params.get("w", 0.5)
        return ((1 - w) * r1 + w * r2).to_numpy(), m
    m = lgb.train(p | {"objective": "regression"}, lgb.Dataset(tr[feats], tr.sira), params.get("rounds", ROUNDS))
    return m.predict(te[feats]), m


def run(freq: str, name: str, df: pd.DataFrame, all_feats: list[str]) -> dict:
    mode, groups, params = (EXPERIMENTS | grid())[name]
    feats = [c for c in all_feats if any(GROUPS[g](c) for g in groups)]
    weeks, _, form_months = UFUK[freq]
    gap = pd.Timedelta(weeks=weeks)
    years, imps = [], pd.Series(0.0, index=feats)
    t0 = time.time()
    for Y in TEST_YEARS:
        start = pd.Timestamp(f"{Y}-01-01")
        tr = df[(df.tarih + gap < start) & (df.yil >= Y - params.get("pencere", PENCERE))]
        te = df[(df.yil == Y) & df.tarih.dt.month.isin(form_months)]
        if "min_likidite" in params:
            tr, te = tr[tr.likidite >= params["min_likidite"]], te[te.likidite >= params["min_likidite"]]
        s, model = score(mode, tr, te, feats, params)
        imps += pd.Series(model.feature_importance("gain"), index=feats)
        te = te.assign(puan=s)
        gross, net, hits, caps = [], [], [], []
        held: dict = {}
        for _, g in te.groupby("tarih"):
            top = g.nlargest(params.get("k", K), "puan")
            r = top.getiri.mean()
            rate = dict(zip(top.index.astype(str), cost_rate(top.islem_tutari.fillna(0)).to_numpy()))
            c = (sum(v for k, v in rate.items() if k not in held) + sum(v for k, v in held.items() if k not in rate)) / len(top)
            held = rate
            gross.append(r); net.append(r - c); hits.append(int(top.hedef.sum())); caps.append(r / g.getiri.nlargest(K).mean())
        if net and weeks >= 52:  # tek seçimli ufuklarda dönem sonu satış maliyeti (alış zaten düşüldü)
            net[-1] -= sum(held.values()) / max(len(held), 1)
        per_year = 52 / weeks  # yıllığa çevir (2 yıl ufukta tek seçimin getirisi ^ 1/2)
        if per_year < 1:
            gross, net = [(1 + x) ** per_year - 1 for x in gross], [(1 + x) ** per_year - 1 for x in net]
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
    print(f"{name:16s} net {out['net_yillik_ort']:+.0%}/yıl (brüt {out['brut_yillik_ort']:+.0%}), zararlı {out['zararli_yil']}/{len(TEST_YEARS)}, "
          f"en iyi %5'ten {out['en_iyi_yuzde5_ort']:.1f}, yıllar {out['yil_yil_net']} [{out['sure_sn']} sn]  önemli: {out['onemli'][:4]}",
          flush=True)
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--yillar" in args:  # ör. --yillar 2013-2017,2022-2025 (aramada kullanılmamış yıllarda doğrulama)
        i = args.index("--yillar")
        spec = args[i + 1]
        del args[i:i + 2]
        TEST_YEARS = tuple(y for part in spec.split(",") for y in range(int(part.split("-")[0]), int(part.split("-")[-1]) + 1))
    freqs = args[0].split(",") if args else ["aylik"]
    names = args[1:] or list(EXPERIMENTS)
    if names == ["izgara"]:
        names = list(grid())
    for freq in freqs:
        df, feats = load(freq)
        print(f"=== {freq}: {len(df):,} satır, {len(feats)} belirti", flush=True)
        for n in names:
            run(freq, n, df, feats)

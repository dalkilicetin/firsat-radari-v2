"""Aylık öğrenen model: python -m radar.research.monthly_ml

Kural aramasından farklı yol: belirtiler arasındaki birleşimleri (etkileşimleri) model kendisi bulur.
Hedef: sonraki 4 haftada ayın en iyi %5'inde olmak (sınıflandırma). Öğrenen: LightGBM, sabit ve tutucu ayarlar
(ayarlar test yıllarına bakılarak değiştirilmez).
İç içe: test yılı Y için model, 4 haftalık getirisi Y başından önce gerçekleşmiş aylarla eğitilir; Y'nin 12 ayında
her ay puanı en yüksek 20 hisse alınır.
Açıklama: her yıl için belirti önemleri (kazanç katkısı) kaydedilir; son modelde en önemli belirtilerin hangi değer
aralıklarında büyük kazanan olasılığını artırdığı (kısmi bağımlılık) çıkarılır.
Çıktı: reports/research/aylik_ml.json
"""

from __future__ import annotations

import json
import time

import lightgbm as lgb
import numpy as np
import pandas as pd

from radar import config

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
OUT_DIR = config.ROOT / "reports" / "research"
META = {"tarih", "yil", "getiri", "sektor", "sembol"}
TEST_YEARS = range(2013, 2026)
K = 20
PARAMS = dict(objective="binary", learning_rate=0.03, num_leaves=31, min_child_samples=400, feature_fraction=0.6,
              bagging_fraction=0.7, bagging_freq=1, lambda_l2=10.0, verbose=-1, seed=0, num_threads=4)
ROUNDS = 400
MODE = "kazanan"


def load() -> tuple[pd.DataFrame, list[str]]:
    df = pd.read_parquet(FRAME)
    df = df[np.isfinite(df.getiri)].copy()
    feats = [c for c in df.columns if c not in META and pd.api.types.is_numeric_dtype(df[c])]
    q = df.groupby("tarih").getiri.transform(lambda r: r.rank(pct=True))
    df["hedef"] = (q > 0.95).astype(int)
    df["kaybeden"] = (q <= 0.05).astype(int)
    df["sira"] = q
    return df, feats


def partial_dependence(model, X: pd.DataFrame, feat: str, grid=np.linspace(0.05, 0.95, 10)) -> list[float]:
    s = X.sample(min(len(X), 20000), random_state=0).copy()
    out = []
    for g in grid:
        s[feat] = g
        out.append(float(model.predict(s).mean()))
    return out


def main() -> dict:
    t0 = time.time()
    df, feats = load()
    rows, imps = [], {}
    model = None
    for Y in TEST_YEARS:
        start = pd.Timestamp(f"{Y}-01-01")
        tr = df[df.tarih + pd.Timedelta(weeks=4) < start]
        te = df[df.yil == Y]
        if MODE == "kazanan":
            model = lgb.train(PARAMS, lgb.Dataset(tr[feats], tr.hedef), ROUNDS)
            puan = model.predict(te[feats])
        elif MODE == "fark":  # büyük kazanan olasılığı − büyük kaybeden olasılığı (oynaklığın iki yüzü birbirini götürür)
            model = lgb.train(PARAMS, lgb.Dataset(tr[feats], tr.hedef), ROUNDS)
            lose = lgb.train(PARAMS, lgb.Dataset(tr[feats], tr.kaybeden), ROUNDS)
            puan = model.predict(te[feats]) - lose.predict(te[feats])
        else:  # sira: sonraki ayın getiri sırası (regresyon)
            model = lgb.train(PARAMS | {"objective": "regression"}, lgb.Dataset(tr[feats], tr.sira), ROUNDS)
            puan = model.predict(te[feats])
        te = te.assign(puan=puan)
        rets, caps, hits = [], [], []
        last = None
        for d, g in te.groupby("tarih"):
            top = g.nlargest(K, "puan")
            best = g.getiri.nlargest(K).mean()
            rets.append(top.getiri.mean())
            caps.append(top.getiri.mean() / best)
            hits.append(int(top.hedef.sum()))
            last = top.sembol.astype(str).tolist()
        rets = np.array(rets)
        imp = pd.Series(model.feature_importance("gain"), index=feats)
        imps[str(Y)] = (imp / imp.sum()).sort_values(ascending=False).head(15).round(4).to_dict()
        rows.append({"yil": Y, "aylik_getiri_ort": float(rets.mean()), "yillik_bilesik": float(np.prod(1 + rets) - 1),
                     "yakalama_ort": float(np.mean(caps)), "en_iyi_yuzde5_ten_aylik": float(np.mean(hits)), "son_ay_secim": last})
        print(f"{Y}: yakalama {np.mean(caps):.1%}, aylık ort. {rets.mean():+.1%}, yıllık bileşik {rows[-1]['yillik_bilesik']:+.0%}, "
              f"en iyi %5'ten {np.mean(hits):.1f}/ay [{round(time.time() - t0)} sn]", flush=True)
    res = pd.DataFrame(rows)
    # Son modelin (2025 testi için eğitilen) en önemli belirtileri ve değer aralıkları
    imp_all = pd.DataFrame(imps).fillna(0).mean(axis=1).sort_values(ascending=False)
    tr_last = df[df.tarih + pd.Timedelta(weeks=4) < pd.Timestamp(f"{max(TEST_YEARS)}-01-01")]
    pdp = {f: partial_dependence(model, tr_last[feats], f) for f in imp_all.head(12).index}
    summary = {"yakalama_ort": float(res.yakalama_ort.mean()), "aylik_getiri_ort": float(res.aylik_getiri_ort.mean()),
               "yillik_bilesik_ort": float(res.yillik_bilesik.mean()), "en_iyi_yuzde5_ten_aylik": float(res.en_iyi_yuzde5_ten_aylik.mean()),
               "rastgele_en_iyi_yuzde5_ten": K * 0.05, "yil": len(res)}
    out = {"ozet": summary, "yillar": rows, "onem_ort": imp_all.head(25).round(4).to_dict(), "onem_yillar": imps,
           "kismi_bagimlilik": {"izgara": list(np.round(np.linspace(0.05, 0.95, 10), 2)), "egriler": pdp}}
    out["mod"] = MODE
    (OUT_DIR / f"aylik_ml_{MODE}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print("en önemli belirtiler:", list(imp_all.head(12).index))
    return out


if __name__ == "__main__":
    import sys
    MODE = sys.argv[1] if len(sys.argv) > 1 else "kazanan"
    main()

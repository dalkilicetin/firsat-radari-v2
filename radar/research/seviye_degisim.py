"""Dış incelemelerden gelen belirtiler: python -m radar.research.seviye_degisim

Finansal kalite için seviye / değişim / sürpriz ayrımı (seviye zaten çerçevede):
- <x>_degisim: son değer − 52 hafta önceki değer (iyileşiyor mu)
- <x>_surpriz: son çeyrek değişimi ÷ son 3 yılın çeyreklik değişim oynaklığı (şirketin kendi geçmişine göre olağan dışı mı)
  x ∈ özsermaye kârlılığı, faaliyet marjı, brüt marj, serbest nakit getirisi, kazanç getirisi
- nakit_pozitife_gecis: serbest nakit getirisi 26 hafta önce ≤ 0, şimdi > 0 (olay)
Fiyat sıkışması ve kırılım (haftalık kapanış ve işlem tutarı; yalnızca geçmiş):
- sikisma: 8 haftalık en yüksek/en düşük aralığı ÷ fiyat (düşük = sıkışık)
- sikisma_suresi: aralığın kendi 52 haftalık %30'luk diliminin altında kaldığı ardışık hafta (en çok 26)
- hacim_daralmasi: 4 haftalık ortalama işlem tutarı ÷ 26 haftalık ortalama
- kirilim_dayanikliligi: son 8 haftada 52 haftalık zirve kırıldıysa, fiyatın kırılım seviyesine göre konumu
- sikismadan_kirilim: en az 4 hafta sıkışmadan sonra, işlem tutarı 1,5 katına çıkarken 52 haftalık zirve kırılımı (olay)
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import panel

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
EVENTS = {"nakit_pozitife_gecis", "sikismadan_kirilim"}


def quality_features(p: dict) -> dict[str, pd.DataFrame]:
    from radar.research import library, ratios
    rs = ratios.signals(p)
    r1 = library.load_group("road1", p)
    base = {"ozsermaye_karliligi": rs["ozsermaye_karliligi"], "faaliyet_marji": rs["faaliyet_marji"],
            "brut_marj": rs["brut_marj"], "serbest_nakit_getirisi": r1["serbest_nakit_getirisi"],
            "kazanc_getirisi": r1["kazanc_getirisi"]}
    out = {}
    for n, x in base.items():
        x = x.reindex(index=p["price"].index, columns=p["price"].columns).astype("float64")
        out[f"{n}_degisim"] = x - x.shift(52)
        q = x - x.shift(13)
        vol = q.rolling(156, min_periods=104).std()
        out[f"{n}_surpriz"] = (q / vol.where(vol > 0)).clip(-10, 10)
    f = base["serbest_nakit_getirisi"].reindex(index=p["price"].index, columns=p["price"].columns)
    out["nakit_pozitife_gecis"] = ((f.shift(26) <= 0) & (f > 0)).astype(float)
    return out


def squeeze_features(p: dict) -> dict[str, pd.DataFrame]:
    price, dv = p["price"], p["dollar_volume"]
    rng = (price.rolling(8, min_periods=6).max() - price.rolling(8, min_periods=6).min()) / price
    tight = rng < rng.rolling(52, min_periods=26).quantile(0.3)
    # ardışık sıkışık hafta sayısı
    t = tight.astype(int).to_numpy()
    run = np.zeros_like(t)
    for i in range(1, len(t)):
        run[i] = np.where(t[i] == 1, np.minimum(run[i - 1] + 1, 26), 0)
    run = pd.DataFrame(run, index=price.index, columns=price.columns).where(rng.notna())
    vol_ratio = dv.rolling(4, min_periods=3).mean() / dv.rolling(26, min_periods=13).mean()
    hi_prev = price.shift(1).rolling(52, min_periods=26).max()
    broke = price > hi_prev
    level = hi_prev.where(broke).ffill(limit=8)
    spike = dv / dv.shift(1).rolling(26, min_periods=13).mean()
    return {
        "sikisma": rng,
        "sikisma_suresi": run.astype(float),
        "hacim_daralmasi": vol_ratio,
        "kirilim_dayanikliligi": (price / level - 1).clip(-1, 3),
        "sikismadan_kirilim": (broke & (run.shift(1) >= 4) & (spike > 1.5)).astype(float).where(price.notna()),
    }


def augment() -> None:
    df = pd.read_parquet(FRAME)
    p = panel.build()
    feats = {}
    for name, fn in (("kalite", quality_features), ("sıkışma", squeeze_features)):
        part = fn(p)
        feats |= part
        print(name, "tamam:", list(part), flush=True)
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    key = pd.MultiIndex.from_arrays([df.tarih, df.index.astype(str)])
    for name, wide in feats.items():
        w = wide.reindex(dates)
        w.columns = w.columns.astype(str)
        long = w.stack(future_stack=True)
        long.index.names = ["tarih", "cik"]
        if name not in EVENTS:
            long = long.groupby(level=0).rank(pct=True)
        df[name] = long.reindex(key).to_numpy(dtype="float32")
        if name in EVENTS:
            df[name] = df[name].fillna(0)
        print(name, f"dolu %{df[name].notna().mean() * 100:.0f}, ort {np.nanmean(df[name]):.3f}", flush=True)
    df.to_parquet(FRAME)
    ev_path = FRAME.with_name("aylik_cerceve_olaylar.json")
    ev = set(json.loads(ev_path.read_text())) | EVENTS
    ev_path.write_text(json.dumps(sorted(ev), ensure_ascii=False))


if __name__ == "__main__":
    augment()

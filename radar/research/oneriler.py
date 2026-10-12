"""Araştırma önerileri (3. tur): python -m radar.research.oneriler [emsal,devralma,bulten,aciga]

Hepsi aylık çerçevenin tarihlerinde, o gün bilinen bilgiyle hesaplanır ve çerçeveye eklenir.

- Metin tabanlı emsal momentumu (Hoberg-Phillips TNIC benzeri; Lee-Sun-Wang-Zhang 2019 "technological links"):
  her yıl Y'de verilen 10-K'ların Madde 1 (iş tanımı) metinleri TF-IDF ile karşılaştırılır, her şirketin en benzer 10 şirketi
  bulunur. Bu emsal kümesi Y+1 boyunca kullanılır (Y'nin tüm 10-K'ları o zaman bilinmektedir).
  emsal_getiri_1a / emsal_getiri_3a: emsallerin son 4 / 13 haftalık ortalama getirisi;
  emsal_farki_1a: emsal getirisi − şirketin kendi getirisi (geride kalan şirketin yetişmesi).
- devralma_olasiligi: iç içe model. Etiket: sonraki 52 haftada iflas dışı borsadan çıkış ve çıkıştan önceki fiyat ≥ 2 $
  (çoğunlukla satın alma). Her test yılı Y için yalnızca etiketi Y'den önce gerçekleşmiş satırlarla lojistik regresyon.
- bulten_*: 8-K 2.02 bilanço bülteni tonu ve rehberlik ifadeleri (son bülten, en fazla 13 hafta eski).
- aciga_satis_*: FINRA açığa satış hacmi payı (son ay) ve 3 aylık değişimi.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from radar import archive, config
from radar.research import panel

FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
PEERS = 10


def peer_sets(cols: pd.Index) -> dict[int, dict[str, list[str]]]:
    """Yıl → {cik: en benzer 10 cik} (o yıl verilen 10-K'ların Madde 1 metninden)."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
    out = {}
    keep = set(cols)
    for y in sorted(archive.entries("tenk")):
        t = archive.load("tenk", names=[y], columns=["cik", "accepted", "item1"])
        t = t.assign(cik=t.cik.astype(str))
        t = t[t.cik.isin(keep) & (t.item1.str.len() > 2000)].sort_values("accepted").drop_duplicates("cik", keep="last")
        if len(t) < 200:
            continue
        vec = TfidfVectorizer(max_features=40_000, min_df=3, max_df=0.25, stop_words="english", sublinear_tf=True,
                              token_pattern=r"(?u)\b[a-z][a-z]{2,}\b", dtype=np.float32)
        X = vec.fit_transform(t.item1.str[:60_000].str.lower())
        nn = NearestNeighbors(n_neighbors=PEERS + 1, metric="cosine").fit(X)
        _, idx = nn.kneighbors(X)
        ciks = t.cik.to_numpy()
        out[int(y)] = {ciks[i]: [ciks[j] for j in row if j != i][:PEERS] for i, row in enumerate(idx)}
        print(f"emsal {y}: {len(t):,} şirket", flush=True)
    return out


def peer_features(dates: pd.DatetimeIndex, cols: pd.Index, price: pd.DataFrame) -> dict[str, pd.DataFrame]:
    sets = peer_sets(cols)
    r1 = (price / price.shift(4) - 1).reindex(dates)
    r3 = (price / price.shift(13) - 1).reindex(dates)
    pos = {c: i for i, c in enumerate(price.columns.astype(str))}
    out = {k: pd.DataFrame(np.nan, index=dates, columns=cols) for k in ("emsal_getiri_1a", "emsal_getiri_3a", "emsal_farki_1a")}
    for y, s in sets.items():
        rows = [i for i, t in enumerate(dates) if t.year == y + 1]
        if not rows:
            continue
        firms = [c for c in s if c in pos]
        # seyrek ağırlık matrisi: firma × emsal (eşit ağırlık, NaN getirili emsal dışarıda)
        A1, A3 = r1.iloc[rows].to_numpy(), r3.iloc[rows].to_numpy()
        for c in firms:
            j = [pos[p] for p in s[c] if p in pos]
            if not j:
                continue
            m1, m3 = np.nanmean(A1[:, j], axis=1), np.nanmean(A3[:, j], axis=1)
            out["emsal_getiri_1a"].iloc[rows, out["emsal_getiri_1a"].columns.get_loc(c)] = m1
            out["emsal_getiri_3a"].iloc[rows, out["emsal_getiri_3a"].columns.get_loc(c)] = m3
            out["emsal_farki_1a"].iloc[rows, out["emsal_farki_1a"].columns.get_loc(c)] = m1 - A1[:, pos[c]]
    return out


TAKEOVER_X = ["kucuk_boyut", "defter_fiyat", "satis_fiyat", "nakit_piyasa", "borc_ozsermaye", "gelir_buyumesi",
              "aktif_karliligi", "momentum_12_1", "getiri_1a", "zirveye_yakinlik_52h", "sektor_ma_dalgasi", "aktivist_13d",
              "aktivist_13d_degisiklik", "pasif_13g_yeni", "kurumsal_hisse_degisimi_payi", "dusuk_oynaklik", "likidite"]


def takeover_label(df: pd.DataFrame, p: dict) -> pd.Series:
    s = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    raw = p["raw"]
    gone = s[(s.status != "aktif") & ~s.bankrupt.fillna(False)]
    last_px = {c: raw[c].loc[:e].dropna().iloc[-1] if c in raw and raw[c].loc[:e].notna().any() else np.nan
               for c, e in gone.end.items()}
    ok = pd.Series({c: v for c, v in last_px.items() if v >= 2})
    end = gone.end.reindex(ok.index)
    e = pd.to_datetime(pd.Series(df.index.astype(str), index=df.index).map(end))
    return ((e > df.tarih) & (e <= df.tarih + pd.Timedelta(weeks=52))).astype(float)


def takeover_feature(df: pd.DataFrame, p: dict) -> np.ndarray:
    from sklearn.linear_model import LogisticRegression
    y = takeover_label(df, p).to_numpy()
    X = df[[c for c in TAKEOVER_X if c in df]].astype("float32")
    X = X.fillna(X.groupby(df.tarih).transform("median")).fillna(0.5).to_numpy()
    out = np.full(len(df), np.nan)
    known = (df.tarih + pd.Timedelta(weeks=52)).to_numpy()  # etiket bu tarihte kesinleşir
    for Y in range(2012, df.yil.max() + 1):
        start = np.datetime64(f"{Y}-01-01")
        tr = known < start
        te = (df.yil == Y).to_numpy()
        if tr.sum() < 20_000 or y[tr].sum() < 100 or not te.any():
            continue
        m = LogisticRegression(C=0.5, max_iter=500, class_weight="balanced").fit(X[tr], y[tr])
        out[te] = m.predict_proba(X[te])[:, 1]
        print(f"devralma {Y}: eğitim {tr.sum():,} satır, {int(y[tr].sum()):,} çıkış", flush=True)
    yy = pd.Series(y, index=df.index)
    sc = pd.Series(out, index=df.index)
    top = sc.groupby(df.tarih.to_numpy()).rank(pct=True) >= 0.9
    print(f"devralma: en üst %10'da 52 hafta içinde çıkış oranı %{yy[top].mean() * 100:.1f}, genel %{yy[sc.notna()].mean() * 100:.1f}")
    return out


def release_features(dates: pd.DatetimeIndex, cols: pd.Index) -> dict[str, pd.DataFrame]:
    from radar.research.pit import pit
    b = archive.load("bilanco_bulteni")
    b = b.assign(cik=b.cik.astype(str), date=b.accepted)
    b = b[b.kelime >= 150]
    feats = {"bulten_ton": b.ton, "bulten_olumsuz": b.olumsuz, "bulten_rehberlik": (b.rehberlik_yukari > 0).astype(float)
             - (b.rehberlik_asagi > 0).astype(float), "bulten_rekor": (b.rekor > 0).astype(float),
             "bulten_beklenti_ustu": (b.beklenti_ustu > 0).astype(float)}
    # ton değişimi: aynı şirketin bir önceki bültenine göre
    b = b.sort_values("accepted")
    feats["bulten_ton_degisimi"] = b.ton - b.groupby("cik").ton.shift(1)
    out = {}
    for k, v in feats.items():
        w = pit(b.assign(value=v)[["cik", "date", "value"]], dates, cols, 13 * 7)
        out[k] = w
    return out


def short_features(dates: pd.DatetimeIndex, cols: pd.Index) -> dict[str, pd.DataFrame]:
    s = archive.load("finra_aciga_satis")
    s = s.groupby(["date", "symbol"], as_index=False)[["short", "total"]].sum()
    sec = panel.build()["securities"].assign(cik=lambda x: x.cik.astype(str))
    # sembol → cik: sembolün kullanıldığı dönem içinde (kimlik pencereleri)
    m = s.merge(sec[["symbol", "cik", "start", "end"]], on="symbol")
    end = m.end.fillna(pd.Timestamp("2100-01-01"))
    m = m[(m.date + pd.offsets.MonthEnd(0) >= m.start.fillna(pd.Timestamp("1900-01-01"))) & (m.date <= end)]
    m = m.groupby(["date", "cik"], as_index=False)[["short", "total"]].sum()
    m["pay"] = (m.short / m.total).where(m.total > 0)
    wide = m.pivot(index="date", columns="cik", values="pay").reindex(columns=cols)
    # ay M'nin verisi M+1'in ilk günü kesinleşir
    wide.index = wide.index + pd.offsets.MonthBegin(1)
    full = wide.reindex(wide.index.union(dates)).ffill(limit=1)
    level = full.reindex(dates)
    chg = (full - full.shift(3)).reindex(dates) if len(full) else level
    lvl3 = full.rolling(3, min_periods=2).mean()
    return {"aciga_satis_payi": level, "aciga_satis_degisimi": chg,
            "aciga_satis_anomali": (full - lvl3).reindex(dates)}


def augment(parts: list[str]) -> None:
    df = pd.read_parquet(FRAME)
    dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
    p = panel.build()
    cols = p["price"].columns.astype(str)
    key = pd.MultiIndex.from_arrays([df.tarih, df.index.astype(str)])
    feats = {}
    if "emsal" in parts:
        feats |= peer_features(dates, cols, p["price"])
    if "bulten" in parts:
        feats |= release_features(dates, cols)
    if "aciga" in parts:
        feats |= short_features(dates, cols)
    events = {"bulten_rekor", "bulten_beklenti_ustu"}
    for name, wide in feats.items():
        long = wide.stack()
        long.index.names = ["tarih", "cik"]
        if name not in events:
            long = long.groupby(level=0).rank(pct=True)
        df[name] = long.reindex(key).to_numpy(dtype="float32")
        if name in events:
            df[name] = df[name].fillna(0)
        print(name, f"dolu %{df[name].notna().mean() * 100:.0f}", flush=True)
    if "devralma" in parts:
        v = pd.Series(takeover_feature(df, p), index=df.index)
        df["devralma_olasiligi"] = v.groupby(df.tarih.to_numpy()).rank(pct=True).astype("float32").to_numpy()
    df.to_parquet(FRAME)
    ev_path = FRAME.with_name("aylik_cerceve_olaylar.json")
    ev = set(json.loads(ev_path.read_text())) | (events & set(df.columns))
    ev_path.write_text(json.dumps(sorted(ev), ensure_ascii=False))


if __name__ == "__main__":
    augment(sys.argv[1].split(",") if len(sys.argv) > 1 else ["emsal", "devralma"])

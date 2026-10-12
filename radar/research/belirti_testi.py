"""Belirti testi: her belirtinin tek başına etkisi (3 ay ve 6 ay ufuk). python -m radar.research.belirti_testi

Ölçüm (her ay, alınabilir faaliyet şirketleri):
- IC: belirti yüzdeliği ile sonraki ufuk getirisinin sıra korelasyonu (Spearman).
- t: ufuk çakışmasın diye yalnızca her k'inci ayın IC'leriyle (3 ay → her 3. ay, 6 ay → her 6. ay) ort / (std/√n).
- Yıl tutarlılığı: yıllık ortalama IC'nin genel ortalamayla aynı işaretli olduğu yıl oranı.
- Büyük kazanan katı: belirtinin en yüksek ve en düşük %20'sinde ufkun en iyi %5'ine girme olasılığı ÷ %5.
Kesin belirti: |t| ≥ 3, yıl tutarlılığı ≥ %70 ve Benjamini–Hochberg q < 0,05 (çoklu test düzeltmesi: ~150 belirti
aynı veride test edildiği için şans eseri "anlamlı" çıkanların payı sınırlanır).
Kilitli dönem: --son 2024 verilirse yalnızca getirisi 2025'ten önce gerçekleşen aylar kullanılır.
ic_by_month() iç içe seçim için de kullanılır (agirlik_arama: her test yılında yalnızca önceki aylarla seçim).
Çıktı: reports/research/belirti_testi.json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config

D = config.ROOT / "data" / "derived"
OUT = config.ROOT / "reports" / "research" / "belirti_testi.json"
META = {"tarih", "yil", "getiri", "sektor", "sembol", "islem_tutari", "getiri_13h", "getiri_26h", "getiri_52h", "getiri_104h"}
UFUK = {"3ay": ("getiri_13h", 3), "6ay": ("getiri_26h", 6)}
T_MIN, CONSIST_MIN = 3.0, 0.7


def features(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in META and pd.api.types.is_numeric_dtype(df[c]) and not c.startswith("piyasa_")]


def ic_by_month(df: pd.DataFrame, feats: list[str], col: str) -> pd.DataFrame:
    """ay × belirti Spearman IC (yüzdelikler zaten sıra; getiri sıraya çevrilir)."""
    rows = {}
    for d, g in df.groupby("tarih"):
        r = g[col]
        ok = r.notna()
        if ok.sum() < 200:
            continue
        rr = r[ok].rank(pct=True)
        X = g.loc[ok, feats]
        rows[d] = X.corrwith(rr, method="pearson")  # X yüzdelik (sıra) olduğundan Pearson ≈ Spearman
    return pd.DataFrame(rows).T.sort_index()


def bh_q(p: pd.Series) -> pd.Series:
    """Benjamini–Hochberg yanlış keşif oranı düzeltmesi: q değerleri."""
    p = p.dropna()
    order = p.sort_values()
    m = len(order)
    q = (order * m / np.arange(1, m + 1)).iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    return q.reindex(p.index)


def summarize(ic: pd.DataFrame, step: int) -> pd.DataFrame:
    from scipy import stats
    sub = ic.iloc[::step]
    mean, sd, n = sub.mean(), sub.std(), sub.notna().sum()
    t = mean / (sd / np.sqrt(n))
    yearly = ic.groupby(ic.index.year).mean()
    consist = (np.sign(yearly) == np.sign(mean)).sum() / yearly.notna().sum()
    p = pd.Series(2 * stats.t.sf(t.abs(), (n - 1).clip(lower=1)), index=t.index)
    return pd.DataFrame({"ic": mean, "t": t, "tutarlilik": consist, "ay": n, "p": p, "q": bh_q(p)})


TOP_N = None  # verilirse: eşik yerine tutarlılığı ≥ %70 olanlar arasından |t| en yüksek N belirti


def select(ic: pd.DataFrame, step: int) -> dict[str, float]:
    """Seçilen belirtiler ve yönleri (+1/−1) — yalnızca verilen IC satırlarıyla (iç içe kullanım)."""
    s = summarize(ic, step)
    s = s[s.tutarlilik >= CONSIST_MIN]
    keep = s.reindex(s.t.abs().sort_values(ascending=False).index).head(TOP_N) if TOP_N else s[(s.t.abs() >= T_MIN) & (s.q < 0.05)]
    return {k: float(np.sign(v)) for k, v in keep.ic.items()}


def winner_lift(df: pd.DataFrame, feats: list[str], col: str) -> pd.DataFrame:
    d = df[df[col].notna()]
    top = d.groupby("tarih")[col].rank(pct=True) > 0.95
    out = {}
    for f in feats:
        x = d[f]
        hi, lo = x >= 0.8, x <= 0.2
        out[f] = {"ust_dilim_kat": float(top[hi].mean() / 0.05) if hi.any() else np.nan,
                  "alt_dilim_kat": float(top[lo].mean() / 0.05) if lo.any() else np.nan}
    return pd.DataFrame(out).T


def main(son: int | None = None) -> dict:
    df = pd.read_parquet(D / "aylik_cerceve.parquet")
    feats = features(df)
    out = {}
    for name, (col, step) in UFUK.items():
        d = df
        if son:  # kilitli dönem: getirisi son+1 yılı başından önce gerçekleşen aylar
            w = {"getiri_13h": 13, "getiri_26h": 26}[col]
            d = df[df.tarih + pd.Timedelta(weeks=w) < pd.Timestamp(f"{son + 1}-01-01")]
        ic = ic_by_month(d, feats, col)
        s = summarize(ic, step).join(winner_lift(d, feats, col))
        s["kesin"] = (s.t.abs() >= T_MIN) & (s.tutarlilik >= CONSIST_MIN) & (s.q < 0.05)
        s = s.sort_values("t", key=abs, ascending=False)
        out[name] = s.round(4).reset_index(names="belirti").to_dict(orient="records")
        print(f"=== {name}: {len(feats)} belirti, {int(s.kesin.sum())} kesin")
        print(s.head(30).round(3).to_string())
    (OUT.with_name(f"belirti_testi_{son}.json") if son else OUT).write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    return out


if __name__ == "__main__":
    import sys
    son = next((int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--son=")), None)
    main(son)

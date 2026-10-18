"""Pattern avı: fiyat geometrisi belirtileri + güvenilir belirtiler; tek, ikili ve üçlü koşulların tamamı.

1) Yeni belirtiler (gerçek sayılar, sıra değil; t gününe kadarki haftalık düzeltilmiş fiyattan; aynı andaki fiyatların
   oranı olduğu için sonraki bölünmeler sadeleşir, sızıntı yok):
   getiri_{4,26,52,104,156}h, getiri_13h_gecmis (geçmiş 13 hafta; çerçevedeki getiri_13h İLERİ getiridir, hedef); zirveden_{52h,156h,tum} = fiyat / en yüksek − 1; dipten_{52h,156h,tum} = fiyat / en düşük − 1;
   konum_52h = (fiyat − dip) / (zirve − dip); zirveden_hafta_52h, dipten_hafta_52h; en_buyuk_dusus_52h, en_buyuk_yukselis_52h;
   yukselen_hafta_13h (son 13 haftada yükselen hafta sayısı); oynaklik_13h, oynaklik_52h, oynaklik_orani;
   trend_egim_26h (log fiyat eğimi, haftalık), trend_r2_26h; ort_10_40 (10 haftalık / 40 haftalık ortalama − 1);
   hacim_degisimi (13 haftalık medyan işlem tutarı / 39 hafta önceki − 1); ham_fiyat ($). Ayrıca sue_ham: kâr değişimi ÷ HAM
   fiyat (sue_fiyat'ın sızıntısız hali).
2) Koşullar: her belirti için Ocak zinciri verisinin %10…%90 yüzdelik değerleri eşik; '≤' ve '≥'.
3) Kural = koşulların VE'si; portföy = koşulu sağlayan bütün hisseler, eşit ağırlık, 13 hafta, maliyet dahil.
   Bir tarihte 5'ten az hisse varsa o dönem S&P 500 (SPY) tutulur. Tek hisse getirisi seçimde +%200 ile sınırlanır
   (tek bir piyango kazancının kuralı seçtirmesini önlemek için); raporda sınırsız sonuç da verilir.
4) Seçim YALNIZCA Ocak zincirinde (Oca/Nis/Tem/Eki başları): tek koşulların tamamı, ikili koşulların tamamı, en iyi 300
   ikiliye üçüncü koşul. Şart: dönemlerin ≥ %75'inde yatırımda. Doğrulama: Şubat ve Mart zincirleri, dönemler, sınırsız getiri.

python -m radar.research.pattern_avi  →  reports/research/pattern_avi.json, pattern_avi_kurallar.csv
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, fundamentals, panel
from radar.research.kazanan_profili import AD
from radar.research.pattern_testi import cost
from radar.research.pit import FUNDAMENTAL_MAX_AGE, pit

R = config.ROOT / "reports" / "research"
FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
CACHE = config.DATA_DIR / "derived" / "pattern_avi_veri.parquet"
CHAINS = {"ocak": (1, 4, 7, 10), "subat": (2, 5, 8, 11), "mart": (3, 6, 9, 12)}
QS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
MIN_N, CAP = 5, 2.0
OLD = [f for f in AD if f not in ("sue_fiyat", "bilanco_uzerinden_hafta")]


def geometry(p: dict, dates: pd.DatetimeIndex) -> dict[str, pd.DataFrame]:
    P, raw, dv = p["price"], p["raw"], p["dollar_volume"]
    idx = P.index
    out = {}
    for k in (4, 13, 26, 52, 104, 156):
        # 13 hafta: çerçevedeki ileri getiri (hedef) sütunuyla karışmasın diye ayrı ad
        out["getiri_13h_gecmis" if k == 13 else f"getiri_{k}h"] = (P / P.shift(k) - 1).reindex(dates)
    for w in (52, 156):
        hi, lo = P.rolling(w, min_periods=w // 2).max(), P.rolling(w, min_periods=w // 2).min()
        out[f"zirveden_{w}h"] = (P / hi - 1).reindex(dates)
        out[f"dipten_{w}h"] = (P / lo - 1).reindex(dates)
        if w == 52:
            out["konum_52h"] = ((P - lo) / (hi - lo)).reindex(dates)
    out["zirveden_tum"] = (P / P.cummax() - 1).reindex(dates)
    out["dipten_tum"] = (P / P.cummin() - 1).reindex(dates)
    ma10, ma40 = P.rolling(10, min_periods=8).mean(), P.rolling(40, min_periods=30).mean()
    out["ort_10_40"] = (ma10 / ma40 - 1).reindex(dates)
    lr = np.log(P / P.shift(1))
    out["oynaklik_13h"] = lr.rolling(13, min_periods=10).std().reindex(dates)
    out["oynaklik_52h"] = lr.rolling(52, min_periods=40).std().reindex(dates)
    out["oynaklik_orani"] = out["oynaklik_13h"] / out["oynaklik_52h"]
    out["yukselen_hafta_13h"] = (lr > 0).astype(float).where(lr.notna()).rolling(13, min_periods=10).sum().reindex(dates)
    out["hacim_degisimi"] = (dv / dv.shift(39) - 1).reindex(dates)
    out["ham_fiyat"] = raw.reindex(dates)
    # pencere içi ölçüler: yalnızca örnek tarihlerde
    names = ["zirveden_hafta_52h", "dipten_hafta_52h", "en_buyuk_dusus_52h", "en_buyuk_yukselis_52h", "trend_egim_26h", "trend_r2_26h"]
    arr = {n: np.full((len(dates), P.shape[1]), np.nan, np.float32) for n in names}
    Pv = P.to_numpy(np.float64)
    x26 = np.arange(26) - 12.5
    for i, t in enumerate(dates):
        j = idx.get_loc(t)
        if j < 51:
            continue
        win = Pv[j - 51:j + 1]  # 52 hafta, son satır t
        ok = np.isfinite(win).sum(0) >= 40
        w = np.where(np.isfinite(win), win, np.nan)
        with np.errstate(all="ignore"):
            arr["zirveden_hafta_52h"][i] = np.where(ok, 51 - np.nanargmax(np.where(np.isfinite(w), w, -np.inf), 0), np.nan)
            arr["dipten_hafta_52h"][i] = np.where(ok, 51 - np.nanargmin(np.where(np.isfinite(w), w, np.inf), 0), np.nan)
            ff = pd.DataFrame(w).ffill().to_numpy()
            runmax, runmin = np.fmax.accumulate(ff, 0), np.fmin.accumulate(ff, 0)
            arr["en_buyuk_dusus_52h"][i] = np.where(ok, np.nanmin(ff / runmax - 1, 0), np.nan)
            arr["en_buyuk_yukselis_52h"][i] = np.where(ok, np.nanmax(ff / runmin - 1, 0), np.nan)
            y = np.log(ff[-26:])
            good = np.isfinite(y).all(0)
            yc = y - y.mean(0)
            slope = (x26[:, None] * yc).sum(0) / (x26 ** 2).sum()
            ss = (yc ** 2).sum(0)
            r2 = (slope ** 2 * (x26 ** 2).sum()) / np.where(ss > 0, ss, np.nan)
            arr["trend_egim_26h"][i] = np.where(good, slope, np.nan)
            arr["trend_r2_26h"][i] = np.where(good, r2, np.nan)
    for n in names:
        out[n] = pd.DataFrame(arr[n], index=dates, columns=P.columns)
    return out


def sue_raw(p: dict, dates) -> pd.DataFrame:
    from radar.research.road1 import by_filing, load_fin
    price, raw = p["price"], p["raw"]
    fin = fundamentals.plain(load_fin())
    eps = by_filing(fin, ["EarningsPerShareDiluted", "EarningsPerShareBasic"], [1])
    d = pit(eps.rename(columns={"accepted": "date"}).assign(value=eps.cur - eps.prev)[["cik", "date", "value"]],
            price.index, price.columns, FUNDAMENTAL_MAX_AGE)
    return (d / raw.where(raw > 0)).clip(-1, 1).reindex(dates)


def build() -> pd.DataFrame:
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    t0 = time.time()
    fr = pd.read_parquet(FRAME, columns=["tarih", "yil", "islem_tutari", "getiri_13h"] + OLD).reset_index()
    fr = fr[(fr.islem_tutari >= 1e6) & fr.getiri_13h.notna()].copy()
    p = panel.build()
    dates = pd.DatetimeIndex(sorted(fr.tarih.unique()))
    g = geometry(p, dates)
    g["sue_ham"] = sue_raw(p, dates)
    ti = dates.get_indexer(fr.tarih)
    ci = p["price"].columns.get_indexer(fr.cik.astype(str))
    for n, df in g.items():
        fr[n] = df.to_numpy()[ti, ci].astype(np.float32)
    fr["net"] = (fr.getiri_13h - 2 * cost(fr.islem_tutari).to_numpy()).astype(np.float32)
    spy = context.etf_prices(panel.fridays())["SPY"]
    fd = panel.fridays()
    sp = {t: (float(spy.iloc[fd.searchsorted(t) + 13] / spy.iloc[fd.searchsorted(t)] - 1)
              if fd.searchsorted(t) + 13 < len(spy) else np.nan) for t in dates}
    fr["spy"] = fr.tarih.map(sp).astype(np.float32)
    fr.to_parquet(CACHE)
    print(f"veri hazır: {len(fr):,} satır, {round(time.time() - t0)} sn", flush=True)
    return fr


NEW = ["getiri_4h", "getiri_13h_gecmis", "getiri_26h", "getiri_52h", "getiri_104h", "getiri_156h", "zirveden_52h", "dipten_52h",
       "zirveden_156h", "dipten_156h", "konum_52h", "zirveden_tum", "dipten_tum", "ort_10_40", "oynaklik_13h", "oynaklik_52h",
       "oynaklik_orani", "yukselen_hafta_13h", "hacim_degisimi", "ham_fiyat", "zirveden_hafta_52h", "dipten_hafta_52h",
       "en_buyuk_dusus_52h", "en_buyuk_yukselis_52h", "trend_egim_26h", "trend_r2_26h", "sue_ham"]


class Engine:
    """Koşul maskeleri ve hızlı değerlendirme (tarih başına toplam / sayı, matris çarpımıyla)."""

    def __init__(self, df: pd.DataFrame, feats: list[str]):
        self.df = df
        self.dates = pd.DatetimeIndex(sorted(df.tarih.unique()))
        self.di = self.dates.get_indexer(df.tarih)
        self.month = self.dates.month.to_numpy()
        self.spy = df.groupby("tarih").spy.first().reindex(self.dates).to_numpy(np.float64)
        jan = np.isin(self.df.tarih.dt.month.to_numpy(), CHAINS["ocak"])
        conds, names = [], []
        for f in feats:
            v = df[f].to_numpy(np.float32)
            q = np.nanquantile(v[jan], QS)
            for qq, th in zip(QS, q):
                if not np.isfinite(th):
                    continue
                conds.append(v <= th)
                names.append((f, "≤", float(th), qq))
                conds.append(v >= th)
                names.append((f, "≥", float(th), qq))
        # aynı maskeyi üreten tekrarlar atılır
        self.M = np.vstack(conds)
        self.names = names
        self.net = df.net.to_numpy(np.float64)
        self.capped = np.minimum(self.net, CAP)

    def per_date(self, mask: np.ndarray, capped=True):
        r = self.capped if capped else self.net
        s = np.bincount(self.di[mask], weights=r[mask], minlength=len(self.dates))
        n = np.bincount(self.di[mask], minlength=len(self.dates))
        return s, n

    def chain_stats(self, s, n, months):
        sel = np.isin(self.month, months) & np.isfinite(self.spy)
        inv = n[sel] >= MIN_N
        r = np.where(inv, s[sel] / np.maximum(n[sel], 1), self.spy[sel])
        yrs = sel.sum() / 4
        cg = np.prod(1 + r) ** (1 / yrs) - 1
        sp = np.prod(1 + self.spy[sel]) ** (1 / yrs) - 1
        return cg, sp, inv.mean(), np.median(n[sel])


def main():
    df = build()
    feats = NEW + OLD
    E = Engine(df, feats)
    C = len(E.names)
    print(f"{C} koşul, {len(df):,} satır", flush=True)
    jan_rows = np.isin(df.tarih.dt.month.to_numpy(), CHAINS["ocak"])
    jan_dates = np.isin(E.month, CHAINS["ocak"]) & np.isfinite(E.spy)
    Dj = np.flatnonzero(jan_dates)
    yrs = len(Dj) / 4
    spy_j = E.spy[Dj]
    sp_cagr = np.prod(1 + spy_j) ** (1 / yrs) - 1
    Mj = E.M[:, jan_rows]
    di_j = E.di[jan_rows]
    r_j = E.capped[jan_rows]
    # tarih göstergesi (Ocak satırları × Ocak tarihleri)
    pos = {d: k for k, d in enumerate(Dj)}
    col = np.array([pos.get(d, -1) for d in di_j])
    W = np.zeros((len(di_j), len(Dj)), np.float32)
    Wn = np.zeros_like(W)
    ok = col >= 0
    W[np.flatnonzero(ok), col[ok]] = r_j[ok]
    Wn[np.flatnonzero(ok), col[ok]] = 1

    def score(S, N):
        inv = N >= MIN_N
        r = np.where(inv, S / np.maximum(N, 1), spy_j[None, :])
        cg = np.prod(1 + r, axis=1) ** (1 / yrs) - 1
        return cg - sp_cagr, inv.mean(1)

    t0 = time.time()
    Mf = Mj.astype(np.float32)
    S1, N1 = Mf @ W, Mf @ Wn
    ex1, cov1 = score(S1, N1)
    singles = pd.DataFrame({"i": np.arange(C), "fark": ex1, "kapsam": cov1})
    print(f"tekler: {round(time.time() - t0)} sn", flush=True)
    # ikililer: her i için (M_i & M_j) — i'nin satırlarıyla sınırlı matris çarpımı
    best_pairs = []
    for i in range(C):
        rows = np.flatnonzero(Mj[i])
        if len(rows) < MIN_N * len(Dj):
            continue
        Mi = Mf[i + 1:, rows]
        S, N = Mi @ W[rows], Mi @ Wn[rows]
        ex, cov = score(S, N)
        good = np.flatnonzero((cov >= 0.75) & (ex > 0))
        if len(good):
            top = good[np.argsort(-ex[good])[:40]]
            best_pairs += [(i, i + 1 + j, float(ex[j]), float(cov[j])) for j in top]
        if i % 200 == 0:
            print(f"  ikili {i}/{C} ({round(time.time() - t0)} sn)", flush=True)
    pairs = pd.DataFrame(best_pairs, columns=["i", "j", "fark", "kapsam"]).sort_values("fark", ascending=False)
    pairs = pairs[pairs.i.map(lambda a: E.names[a][0]) != pairs.j.map(lambda b: E.names[b][0])]
    print(f"ikililer: {len(pairs)} aday ({round(time.time() - t0)} sn)", flush=True)
    triples = []
    for r in pairs.head(300).itertuples():
        rows = np.flatnonzero(Mj[r.i] & Mj[r.j])
        S, N = Mf[:, rows] @ W[rows], Mf[:, rows] @ Wn[rows]
        ex, cov = score(S, N)
        good = np.flatnonzero((cov >= 0.75) & (ex > r.fark))
        for k in good[np.argsort(-ex[good])[:20]]:
            if E.names[k][0] not in (E.names[r.i][0], E.names[r.j][0]):
                triples.append((r.i, r.j, int(k), float(ex[k]), float(cov[k])))
    trip = pd.DataFrame(triples, columns=["i", "j", "k", "fark", "kapsam"]).drop_duplicates().sort_values("fark", ascending=False)
    print(f"üçlüler: {len(trip)} aday ({round(time.time() - t0)} sn)", flush=True)
    # aday kurallar: en iyi 100 tek, 300 ikili, 300 üçlü → tam değerlendirme (görmediği aylar dahil)
    cands = [((int(a),), "tek") for a in singles[singles.kapsam >= 0.75].sort_values("fark", ascending=False).i.head(100)]
    cands += [((int(a), int(b)), "ikili") for a, b in pairs[["i", "j"]].head(300).to_numpy()]
    cands += [((int(a), int(b), int(c)), "üçlü") for a, b, c in trip[["i", "j", "k"]].head(300).to_numpy()]
    rows = []
    for ids, kind in cands:
        m = np.logical_and.reduce([E.M[x] for x in ids])
        rec = {"tur": kind, "kural": " VE ".join(fmt(E.names[x]) for x in ids), "ids": list(ids)}
        for capped in (True, False):
            s, n = E.per_date(m, capped)
            for ch, months in CHAINS.items():
                cg, sp, cov, med = E.chain_stats(s, n, months)
                key = f"{ch}{'' if capped else '_sinirsiz'}"
                rec[key] = cg
                rec[f"{ch}_spy"] = sp
                rec[f"{ch}_kapsam"] = cov
                rec[f"{ch}_medyan_hisse"] = med
        rows.append(rec)
    t = pd.DataFrame(rows)
    t["gorulmeyen_min"] = t[["subat", "mart"]].min(axis=1) - t[["subat_spy", "mart_spy"]].max(axis=1)
    t["ocak_fark"] = t.ocak - t.ocak_spy
    t.sort_values("ocak_fark", ascending=False).round(4).to_csv(R / "pattern_avi_kurallar.csv", index=False)
    out = {"kosul": C, "tek_kural": int(C), "ikili_denenen": int(C * (C - 1) / 2), "ucuncu_eklenen_ikili": 300,
           "ocak_ile_gorulmeyen_iliskisi": float(t[["ocak_fark", "gorulmeyen_min"]].corr().iloc[0, 1]),
           "en_iyi_ocak": t.sort_values("ocak_fark", ascending=False).head(15).drop(columns=["ids"]).round(4).to_dict(orient="records"),
           "en_iyi_gorulmeyen": t.sort_values("gorulmeyen_min", ascending=False).head(15).drop(columns=["ids"]).round(4).to_dict(orient="records")}
    (R / "pattern_avi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    pd.set_option("display.width", 300)
    show = ["tur", "kural", "ocak", "subat", "mart", "ocak_sinirsiz", "subat_sinirsiz", "mart_sinirsiz", "ocak_spy", "ocak_medyan_hisse"]
    print("=== Ocak'ta en iyi 15 (görmediği aylardaki sonucuyla)")
    print(t.sort_values("ocak_fark", ascending=False).head(15)[show].round(3).to_string())


def fmt(n):
    f, op, th, q = n
    return f"{f} {op} {th:.4g} (%{int(q * 100)})"


if __name__ == "__main__":
    main()

"""Kazanan profilinden çıkan pattern'in sabit kuralla testi (kural sonuçlara bakılmadan yazıldı, 18 Ekim 2026).

Pattern (kazanan_profili.md): küçük, ucuz, oynak hisseler arasında işi düzelen, trendi kırılmamış, yöneticilerin aldığı
hisseler. Pattern yalnızca çeyrek başı aylarından (Ocak/Nisan/Temmuz/Ekim) çıkarıldı.

Görmediği veri: diğer ayların başlangıçları. İki zincir, her biri 3 ayda bir seçim, 3 ay (13 hafta) tutma, çakışma yok:
  Şubat zinciri: Şub → May → Ağu → Kas;  Mart zinciri: Mar → Haz → Eyl → Ara.
Karşılaştırma için pattern'in çıkarıldığı (gördüğü) Ocak zinciri: Oca → Nis → Tem → Eki.
Not: Zincirler aynı yılları kapsar; tarihler farklı ama piyasa dönemleri ortaktır. Bu tam bağımsız bir test değildir.

KURAL (sabit, değiştirilmez):
1. Evren: finans dışı, fiyat ≥ 1 $, günlük işlem tutarı ≥ 1 M$ olarak bilinen hisseler (geriye_bakis ile aynı).
2. Piyango süzgeci: küçük şirket ≥ 0,7; hisse fiyatı ≤ 0,3; şirkete özgü oynaklık ≥ 0,7 (o tarihin evren içi sırası).
3. Çürükleri ele: son 1 yıl getirisi < 0,3; 40 haftalık ortalamaya uzaklık < 0,3; faaliyet marjı iyileşmesi < 0,3;
   gelir sürprizi < 0,3 (bilinmiyorsa elenmez); devamlılık şüphesi, hisse ihracı ya da 8-K 3.02 kayıtsız hisse satışı varsa.
4. Puan: içeriden alan yönetici sayısı, faaliyet marjı iyileşmesi, brüt marj iyileşmesi, gelir sürprizi, büyüme ivmesi,
   son 1 yıl getirisi, 40 haftalık ortalamaya uzaklık sıralarının (bilinenlerin) ortalaması.
5. En yüksek puanlı 10 hisse, eşit ağırlık, 13 hafta. Maliyet: işlem tutarına göre kademeli (backtest.COSTS), alış + satış.
Kıyaslar: S&P 500 (SPY), evrenin eşit ağırlıklı ortalaması, yalnızca piyango süzgeci (adım 2; 3–4 yok, rastgele değil
tamamı), bunlar aynı tarihlerde.
Başarı göstergeleri: getiri; seçimlerin büyük kazanan (ilk 20) ve büyük kaybeden (son 20) olma oranı.

python -m radar.research.pattern_testi  →  reports/research/pattern_testi.json, pattern_testi.md
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, panel
from radar.research.backtest import COSTS, UNKNOWN_COST

R = config.ROOT / "reports" / "research"
FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
N = 10
SCORE = ["icerden_alici_sayisi_90g", "faaliyet_marji_degisimi", "brut_marj_degisimi", "gelir_surprizi", "buyume_ivmesi",
         "momentum_12_1", "ort_40h_uzaklik"]
EV = ["devamlilik_suphesi", "hisse_ihraci", "8k_3.02_kayıtsız hisse satışı (sulandırma)"]
CHAINS = {"Ocak zinciri (gördüğü)": (1, 4, 7, 10), "Şubat zinciri (görmediği)": (2, 5, 8, 11), "Mart zinciri (görmediği)": (3, 6, 9, 12)}


def cost(dv: pd.Series) -> pd.Series:
    out = pd.Series(UNKNOWN_COST, index=dv.index)
    for floor, rate in reversed(COSTS):
        out[dv >= floor] = rate
    return out


def pick(g: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    lot = g[(g.kucuk_boyut >= 0.7) & (g.fiyat_seviyesi <= 0.3) & (g.ivol_3a >= 0.7)]
    bad = ((lot.momentum_12_1 < 0.3) | (lot.ort_40h_uzaklik < 0.3) | (lot.faaliyet_marji_degisimi < 0.3) | (lot.gelir_surprizi < 0.3)
           | (lot[EV].fillna(0) > 0).any(axis=1))
    ok = lot[~bad].copy()
    ok["puan"] = ok[SCORE].mean(axis=1, skipna=True)
    return ok.sort_values("puan", ascending=False).head(N), lot


def main() -> dict:
    cols = ["tarih", "yil", "sembol", "islem_tutari", "getiri_13h", "kucuk_boyut", "fiyat_seviyesi", "ivol_3a"] + SCORE + EV
    df = pd.read_parquet(FRAME, columns=list(dict.fromkeys(cols)))
    df = df[(df.islem_tutari >= 1e6) & df.getiri_13h.notna()]
    dates = panel.fridays()
    spy = context.etf_prices(dates)["SPY"]
    res, rows, picks_all = {}, [], []
    for name, months in CHAINS.items():
        d = df[df.tarih.dt.month.isin(months)]
        per = []
        for t, g in d.groupby("tarih"):
            top_cut = g.getiri_13h.nlargest(20).min()
            bot_cut = g.getiri_13h.nsmallest(20).max()
            sel, lot = pick(g)
            if len(sel) == 0:
                continue
            c = 2 * cost(sel.islem_tutari)
            i = dates.searchsorted(t)
            s = float(spy.iloc[i + 13] / spy.iloc[i] - 1) if i + 13 < len(spy) else np.nan
            per.append({"zincir": name, "tarih": str(t.date()), "yil": t.year, "secilen": len(sel),
                        "pattern": float((sel.getiri_13h - c).mean()), "pattern_maliyetsiz": float(sel.getiri_13h.mean()),
                        "piyango": float(lot.getiri_13h.mean()), "evren": float(g.getiri_13h.mean()), "spy": s,
                        "buyuk_kazanan_orani": float((sel.getiri_13h >= top_cut).mean()),
                        "buyuk_kaybeden_orani": float((sel.getiri_13h <= bot_cut).mean()),
                        "piyango_buyuk_kazanan": float((lot.getiri_13h >= top_cut).mean()),
                        "piyango_buyuk_kaybeden": float((lot.getiri_13h <= bot_cut).mean())})
            for r in sel.itertuples():
                picks_all.append({"zincir": name, "tarih": str(t.date()), "sembol": r.sembol, "getiri_13h": round(float(r.getiri_13h), 4)})
        p = pd.DataFrame(per)
        rows.append(p)
        yrs = len(p) / 4
        cagr = lambda col: float(np.prod(1 + p[col].dropna()) ** (1 / yrs) - 1)
        wealth = np.cumprod(1 + p.pattern.to_numpy())
        dd = float((wealth / np.maximum.accumulate(wealth) - 1).min())
        sw = np.cumprod(1 + p.spy.fillna(0).to_numpy())
        res[name] = {"donem": int(len(p)), "ilk": p.tarih.iloc[0], "son": p.tarih.iloc[-1],
                     "yillik_pattern": cagr("pattern"), "yillik_pattern_maliyetsiz": cagr("pattern_maliyetsiz"),
                     "yillik_spy": cagr("spy"), "yillik_evren": cagr("evren"), "yillik_piyango": cagr("piyango"),
                     "en_kotu_dusus_pattern": dd, "en_kotu_dusus_spy": float((sw / np.maximum.accumulate(sw) - 1).min()),
                     "spy_ustu_donem_payi": float((p.pattern > p.spy).mean()),
                     "buyuk_kazanan_orani": float(p.buyuk_kazanan_orani.mean()), "buyuk_kaybeden_orani": float(p.buyuk_kaybeden_orani.mean()),
                     "piyango_buyuk_kazanan": float(p.piyango_buyuk_kazanan.mean()), "piyango_buyuk_kaybeden": float(p.piyango_buyuk_kaybeden.mean()),
                     "ortalama_secilen": float(p.secilen.mean())}
        ann = p.groupby("yil")[["pattern", "spy", "evren", "piyango"]].apply(lambda x: np.prod(1 + x.fillna(0)) - 1)
        res[name]["yil_yil"] = {int(k): {c: round(float(v), 4) for c, v in r.items()} for k, r in ann.iterrows()}
    pd.concat(rows).to_csv(R / "pattern_testi_donemler.csv", index=False)
    pd.DataFrame(picks_all).to_csv(R / "pattern_testi_secimler.csv", index=False)
    (R / "pattern_testi.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    for k, v in res.items():
        print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != "yil_yil"})
    return res


if __name__ == "__main__":
    main()

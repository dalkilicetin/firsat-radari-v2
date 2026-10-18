"""Geriye bakış: her 3 ayda ve her 6 ayda, sonradan bakınca en çok kazandıran hisseler (model yok, yalnızca sonuç).

Kurallar (yalnızca güvenilir veri, kullanıcı kararı 18 Ekim 2026):
- Evren: finans dışı faaliyet şirketleri; başlangıçta işlem fiyatı ≥ 1 $ ve günlük işlem tutarı (13 hafta medyanı)
  ≥ 1 M$ olarak BİLİNEN hisseler. Seyrek FTD fiyatlı (günlük fiyatı ve hacmi olmayan) hisseler dahil edilmez.
- Dönemler: her çeyrek başının ilk Cuması (Ocak, Nisan, Temmuz, Ekim). 3 ay: bir sonraki çeyrek başına kadar;
  6 ay: Ocak→Temmuz ve Temmuz→Ocak (çakışmayan).
- Getiri: düzeltilmiş kapanışla (bölünme ve temettü dahil). Dönem içinde borsadan çıkanlarda son günlük fiyat,
  iflasta 0.
- Veri kontrolü: listeye giren her hissenin getirisi, ham işlem fiyatı ve bölünme kayıtlarıyla yeniden hesaplanır;
  %15'ten fazla tutarsızlık 'kontrol' olarak işaretlenir. Çok düşük işlem tutarı da işaretlenir.

python -m radar.research.geriye_bakis
Çıktı: reports/research/geriye_bakis.md, geriye_bakis_3ay.csv, geriye_bakis_6ay.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from radar import config
from radar.research import context, panel, sectors

R = config.ROOT / "reports" / "research"
TOP = 20  # CSV'de dönem başına
SHOW = 5  # raporda dönem başına


def starts(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    out = []
    for y in range(2010, 2027):
        for m in (1, 4, 7, 10):
            f = dates[(dates.year == y) & (dates.month == m)]
            if len(f):
                out.append(f[0])
    return out


def window_returns(p, sec, t0, t1):
    price = p["price"]
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    a = price.loc[t0]
    span = price.loc[(price.index > t0) & (price.index <= t1)]
    b = price.loc[t1]
    # dönem içinde çıkanlar: son geçerli günlük fiyat (iflasta 0)
    end = s.end.reindex(price.columns)
    exited = (end > t0) & (end <= t1)
    last = span.ffill().iloc[-1]
    b = b.where(~exited, last)
    bk = s.bankrupt.reindex(price.columns).fillna(False).astype(bool)
    b = b.where(~(exited & bk), 0.0)
    return b / a - 1, exited, exited & bk


def main() -> None:
    p = panel.build()
    sec = p["securities"]
    price, raw, dv = p["price"], p["raw"], p["dollar_volume"]
    unis = sectors.operating_universes(p)
    inv = unis["tümü"] & (raw >= 1) & (dv >= 1e6)
    etf = context.etf_prices(price.index)
    s = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik", keep="last").set_index("cik")
    sic = sectors.load_sic().reindex(price.columns).fillna("")
    from radar.research.hindsight import ETF_NAMES
    sector = pd.Series([ETF_NAMES.get(context.etf_for_sic(c), "Diğer") for c in sic], index=price.columns)
    ev = panel.split_cum(panel.split_events())
    ev = ev[ev.source != "ftd_tahmini"]
    st = starts(price.index)
    tick = pd.read_parquet(config.DATA_DIR / "derived" / "identity_tickers.parquet").assign(cik=lambda x: x.cik.astype(str))
    tick_by = {c: g for c, g in tick.groupby("cik")}

    def symbol_at(c, t):
        """O dönemdeki sembol (SEC sembol geçmişi, 2015 →); bulunamazsa güncel sembol."""
        g = tick_by.get(c)
        if g is not None:
            hit = g[(g.first_seen <= t + pd.Timedelta(days=45)) & (g.last_seen >= t - pd.Timedelta(days=45))]
            if len(hit):
                return hit.sort_values("n").ticker.iloc[-1]
        return s.symbol.get(c)
    last_full = price.index[-1]
    tables = {}
    for label, step, pick in (("3ay", 1, lambda i, d: True), ("6ay", 2, lambda i, d: d.month in (1, 7))):
        rows, summ = [], []
        for i, t0 in enumerate(st):
            if not pick(i, t0) or i + step >= len(st):
                continue
            t1 = st[i + step]
            if t1 > last_full:
                continue
            u = inv.loc[t0]
            r, exited, bk = window_returns(p, sec, t0, t1)
            r = r[u].dropna()
            spy = float(etf["SPY"].loc[t1] / etf["SPY"].loc[t0] - 1)
            top = r.sort_values(ascending=False).head(TOP)
            for rank, (c, v) in enumerate(top.items(), 1):
                # bağımsız yeniden hesap: ham fiyat × aradaki bölünme oranları (temettü hariç → küçük fark normal)
                e = ev[(ev.cik == c) & (ev.date > t0) & (ev.date <= t1)]
                f = float(np.prod(e.ratio)) if len(e) else 1.0
                r_raw = raw.at[t1, c] * f / raw.at[t0, c] - 1 if np.isfinite(raw.at[t1, c]) else np.nan
                flags = []
                if np.isfinite(r_raw) and abs((1 + r_raw) / (1 + v) - 1) > 0.15:
                    flags.append("getiri tutarsız")
                if dv.at[t0, c] < 3e6:
                    flags.append("düşük hacim")
                if exited.get(c, False):
                    flags.append("iflas" if bk.get(c, False) else "dönemde borsadan çıktı")
                rows.append({"donem": f"{t0.year}-{['', 'Q1', '', '', 'Q2', '', '', 'Q3', '', '', 'Q4'][t0.month]}" if label == "3ay"
                             else f"{t0.year}-{'H1' if t0.month == 1 else 'H2'}",
                             "baslangic": str(t0.date()), "bitis": str(t1.date()), "sira": rank, "sembol": symbol_at(c, t0), "guncel_sembol": s.symbol.get(c),
                             "sirket": clean(s.name.get(c, "")), "sektor": sector.get(c), "baslangic_fiyati": round(float(raw.at[t0, c]), 2),
                             "gunluk_islem_milyon_usd": round(float(dv.at[t0, c]) / 1e6, 1), "getiri": round(float(v), 4),
                             "ham_fiyatla_getiri": round(float(r_raw), 4) if np.isfinite(r_raw) else None,
                             "spy": round(spy, 4), "uyari": ", ".join(flags)})
            summ.append({"donem": rows[-1]["donem"], "evren": int(len(r)), "spy": spy, "medyan": float(r.median()),
                         "ilk3": float(top.head(3).mean()), "ilk5": float(top.head(5).mean()), "ilk10": float(top.head(10).mean())})
        d = pd.DataFrame(rows)
        d.to_csv(R / f"geriye_bakis_{label}.csv", index=False)
        tables[label] = (d, pd.DataFrame(summ))
    write_report(tables)


def clean(n) -> str:
    import re
    n = re.sub(r"\s+-\s+.*$", "", str(n or ""))
    n = re.sub(r"\s+(Class [A-Z]|Common Stock|Ordinary Shares|American Depositary).*$", "", n)
    return n[:38]


def pct(x):
    return "—" if x is None or not np.isfinite(x) else f"{x * 100:+,.0f}%"


def write_report(tables) -> None:
    L = ["# Geriye Bakış: Her Dönemin En Çok Kazandıran Hisseleri", "",
         "- **Ne bu?** Sonradan bakınca, her 3 ayda ve her 6 ayda en çok yükselen hisseler. Model yok; bunlar o gün bilinemezdi. "
         "Amaç, avlamak istediğimiz hisselerin neye benzediğini ve tavan getiriyi görmek.",
         "- **Evren:** Finans dışı ABD şirketleri; dönem başında fiyatı ≥ 1 $ ve günlük işlem hacmi ≥ 1 milyon $ olarak bilinen hisseler. "
         "Günlük fiyatı olmayan (seyrek kayıtlı) borsadan çıkmış hisseler dahil değil (yalnızca güvenilir veri).",
         "- **Getiri:** Bölünme ve temettü dahil. Dönemde borsadan çıkanlarda son fiyat, iflasta −%100.",
         "- **Veri kontrolü:** Her hissenin getirisi ham fiyat ve bölünme kayıtlarıyla yeniden hesaplandı; tutarsızlık 'Not' sütununda.",
         "- **Sembol:** O dönemdeki sembol (SEC sembol geçmişi 2015'ten başlıyor; öncesinde güncel sembol). Şirket adı güncel addır.",
         "- **Önemli sınır:** Günlük fiyatı olmayan, borsadan çıkmış hisseler hariç tutulduğu için özellikle ilk yıllarda evren küçük "
         "(2010'da ~1.150, 2026'da ~3.000 hisse). Bu listeler o yılların bütün kazananlarını değil, bugün güvenilir verisi olanları gösterir.",
         "- **Düşük hacim:** Dönem başında günlük işlem 3 milyon $'ın altında; büyük para bu hisselere kolay giremez.",
         "- **Tam liste** (dönem başına ilk 20): `geriye_bakis_3ay.csv`, `geriye_bakis_6ay.csv`.", ""]
    for label, title in (("3ay", "3 aylık dönemler"), ("6ay", "6 aylık dönemler")):
        d, sm = tables[label]
        L += [f"## {title}", "", "### Özet: en iyi 3 / 5 / 10 hissenin ortalama getirisi", "",
              "| Dönem | Hisse sayısı | S&P 500 | Evren medyanı | En iyi 3 | En iyi 5 | En iyi 10 |", "|---|---|---|---|---|---|---|"]
        for r in sm.itertuples():
            L.append(f"| {r.donem} | {r.evren:,} | {pct(r.spy)} | {pct(r.medyan)} | {pct(r.ilk3)} | {pct(r.ilk5)} | {pct(r.ilk10)} |")
        per_year = 4 if label == "3ay" else 2
        g = lambda col: (np.prod(1 + sm[col]) ** (per_year / len(sm)) - 1) if len(sm) else np.nan
        L += ["", f"Bileşik yıllık (her dönem yalnızca o grubu alıp tutmuş olsaydık; tavan, ulaşılamaz): "
                  f"S&P {pct(g('spy'))}, en iyi 3 {pct(g('ilk3'))}, en iyi 10 {pct(g('ilk10'))}.", ""]
        for y in sorted(set(d.donem.str[:4])):
            L += [f"### {y}", "", "| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |",
                  "|---|---|---|---|---|---|---|---|---|"]
            for r in d[(d.donem.str[:4] == y) & (d.sira <= SHOW)].itertuples():
                L.append(f"| {r.donem} | {r.sira} | {r.sembol} | {r.sirket} | {r.sektor} | {r.baslangic_fiyati:,.2f} $ | "
                         f"{r.gunluk_islem_milyon_usd:,.1f} | {pct(r.getiri)} | {r.uyari if isinstance(r.uyari, str) else ''} |")
            L.append("")
    (R / "geriye_bakis.md").write_text("\n".join(L))


if __name__ == "__main__":
    main()

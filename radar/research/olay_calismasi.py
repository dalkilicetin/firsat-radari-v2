"""Olay çalışması — "şu olursa yüksek kâr belirtisidir": python -m radar.research.olay_calismasi

Bir olay hissede gerçekleştiği hafta (o Cuma bilinen bilgiyle), sonraki 4 / 13 / 26 haftada hisse piyasaya göre ne yaptı?
Evren: alınabilir faaliyet şirketleri (olay haftasında). Fazla getiri = hisse getirisi − aynı haftanın evren ortalaması (eşit ağırlıklı).
Olay = ilk gerçekleştiği hafta (taşınan bayraklarda başlangıç anı).
Ölçütler: olay sayısı, ortalama ve medyan fazla getiri, isabet (fazla getiri > 0), büyük kazanan katı (ufkun en iyi %5'ine
girme ÷ %5), büyük kaybeden katı, t (aynı haftadaki olaylar tek gözlem: hafta ortalamaları üzerinden), yıl tutarlılığı.
Sınıf (13 hafta): Yüksek kâr belirtisi: ort ≥ +%2, t ≥ 3, tutarlılık ≥ %70 | Uyarı: ort ≤ −%2, t ≤ −3, tutarlılık ≥ %70 |
Büyük hareket (yön belirsiz): kazanan ve kaybeden katı ≥ 1,5 | Etkisiz: diğerleri.
Çıktı: reports/research/7_olay_belirtileri.pdf, reports/research/olay_belirtileri.json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import archive, config
from radar.research import hindsight as hs
from radar.research import panel
from radar.research.pit import to_friday
from radar.weekly import labels
from radar.weekly.pdf import Styles, _table

OUT = config.ROOT / "reports" / "research" / "7_olay_belirtileri.pdf"
JSON = config.ROOT / "reports" / "research" / "olay_belirtileri.json"
HORIZONS = (4, 13, 26)
ITEM_NAMES = {
    "1.01": "Önemli anlaşma imzalandı", "1.02": "Önemli anlaşma feshedildi", "1.03": "İflas / kayyum",
    "1.05": "Siber güvenlik olayı", "2.01": "Satın alma / varlık satışı tamamlandı", "2.02": "Bilanço açıklaması",
    "2.03": "Yeni borç yükümlülüğü", "2.04": "Borç hızlandırma / temerrüt tetikleyicisi", "2.05": "Çıkış / yeniden yapılanma maliyeti",
    "2.06": "Varlık değer düşüklüğü", "3.01": "Borsadan çıkarma uyarısı / kotasyon kuralı ihlali", "3.02": "Kayıtsız hisse satışı",
    "3.03": "Hissedar haklarında değişiklik", "4.01": "Denetçi değişikliği", "4.02": "Geçmiş bilançolara güvenilmez (düzeltme)",
    "5.01": "Kontrol değişikliği", "5.02": "Yönetici / yönetim kurulu değişikliği", "5.03": "Esas sözleşme değişikliği",
    "5.07": "Genel kurul oy sonuçları", "7.01": "Kamuyu aydınlatma (FD)", "8.01": "Diğer önemli olaylar",
}


def onset(flag: pd.DataFrame) -> pd.DataFrame:
    f = flag.fillna(0) > 0
    return f & ~f.shift(1, fill_value=False)


def events(p: dict, sigs: dict) -> dict[str, pd.DataFrame]:
    price, raw, dv = p["price"], p["raw"], p["dollar_volume"]
    dates, cols = price.index, price.columns
    out = {}
    # 8-K maddeleri (dosyalama tarihinden sonraki ilk Cuma)
    f = archive.load("filings", columns=["cik", "form", "filing_date", "items"])
    f = f[f.form.isin(["8-K", "8-K/A"]) & f["items"].notna()].assign(cik=lambda x: x.cik.astype(str))
    f = f[f.cik.isin(set(cols))]
    f["date"] = to_friday(f.filing_date)
    f = f[f.date.isin(dates)]
    ex = f.assign(item=f["items"].str.split(",")).explode("item")
    ex["item"] = ex.item.str.strip()
    for item, name in ITEM_NAMES.items():
        e = ex[ex.item == item].drop_duplicates(["cik", "date"])
        if len(e) < 50:
            continue
        idx_d, idx_c = dates.get_indexer(e.date), cols.get_indexer(e.cik)
        arr = np.zeros((len(dates), len(cols)), dtype=bool)
        arr[idx_d, idx_c] = True
        out[f"8-K {item}: {name}"] = pd.DataFrame(arr, index=dates, columns=cols)
    # Kurumsal ve metin olayları (taşınan bayrakların başlangıcı)
    for n, label in [("icerden_alim_kumesi_3plus", "90 günde 3+ yönetici hisse aldı"), ("ust_yonetici_alimi_90g", "CEO/CFO hisse aldı"),
                     ("devamlilik_suphesi", "Denetçi süreklilik şüphesi bildirdi"), ("haber_ani_artis", "Haberlerde ani artış"),
                     ("wiki_ani_ilgi", "Wikipedia'da ani ilgi")]:
        if n in sigs:
            out[label] = onset(sigs[n])
    wret = price / price.shift(1) - 1
    hi52 = price.rolling(52, min_periods=26).max().shift(1)
    lo52 = price.rolling(52, min_periods=26).min().shift(1)
    vol_ratio = dv / dv.shift(13)
    out["Tek haftada +%30 ve üzeri yükseliş"] = wret >= 0.30
    out["Tek haftada −%30 ve üzeri düşüş"] = wret <= -0.30
    out["52 haftalık zirve kırılımı + hacim patlaması (×2)"] = onset((price > hi52) & (vol_ratio >= 2))
    out["52 haftalık zirveye ilk çıkış"] = onset(price > hi52)
    out["52 haftalık dibe ilk iniş"] = onset(price < lo52)
    out["İşlem hacmi patlaması (13 haftaya göre ×3)"] = onset(vol_ratio >= 3)
    if "kazanc_aciklamasi_tepkisi" in sigs:
        er = sigs["kazanc_aciklamasi_tepkisi"]
        first = er.notna() & er.shift(1).isna() | (er != er.shift(1))
        out["Bilanço haftasında piyasaya göre +%15 ve üzeri"] = first & (er >= 0.15)
        out["Bilanço haftasında piyasaya göre −%15 ve altı"] = first & (er <= -0.15)
    if "haber_ton_seviyesi" in sigs and "haber_ivmesi" in sigs:
        tone, buzz = sigs["haber_ton_seviyesi"], sigs["haber_ivmesi"]
        q = tone.rank(axis=1, pct=True)
        out["Aşırı olumsuz haber tonu (en kötü %5) + yoğun haber"] = onset((q <= 0.05) & (buzz.rank(axis=1, pct=True) >= 0.8))
        out["Aşırı olumsuz ton + fiyat 52 hafta dibine yakın (karşıt)"] = onset((q <= 0.05) & (price <= lo52 * 1.1))
    if "kurumsal_sahip_degisimi" in sigs:
        k = sigs["kurumsal_sahip_degisimi"]
        out["Fon sahipliğinde sıçrama (en üst %5)"] = onset(k.rank(axis=1, pct=True) >= 0.95)
    # FTD patlaması: haftalık teslim edilemeyen hisse, 52 haftalık medyanının 10 katı ve ≥ 100 bin adet
    ftd = archive.load("ftd", columns=["settle_date", "symbol", "qty"])
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str))
    act = sec[sec.status == "aktif"][["symbol", "cik"]]
    ftd = ftd.merge(act, on="symbol")
    ftd["date"] = to_friday(ftd.settle_date)
    wk = ftd.pivot_table(index="date", columns="cik", values="qty", aggfunc="sum").reindex(index=dates, columns=cols)
    med = wk.fillna(0).rolling(52, min_periods=13).median().shift(1)
    out["Teslim edilemeyen hisse (FTD) patlaması"] = onset((wk >= 10 * med.clip(lower=1)) & (wk >= 100_000))
    return out


def study(ev: dict[str, pd.DataFrame], p: dict, inv: pd.DataFrame) -> pd.DataFrame:
    price, sec, dates = p["price"], p["securities"], p["price"].index
    U = inv.reindex(index=dates, columns=price.columns).fillna(False).to_numpy()
    fwd = {h: panel.forward_returns(price, sec, h).reindex(dates).to_numpy() for h in HORIZONS}
    exc, top, bot = {}, {}, {}
    for h, r in fwd.items():
        r = np.where(U, r, np.nan)
        med = np.nanmean(r, axis=1, keepdims=True)  # ortalama: çarpık dağılımda medyan, olayları olduğundan iyi gösterir
        exc[h] = r - med
        q = pd.DataFrame(r).rank(axis=1, pct=True).to_numpy()
        top[h], bot[h] = q > 0.95, q <= 0.05
    years = dates.year.to_numpy()
    rows = []
    for name, e in ev.items():
        E = e.reindex(index=dates, columns=price.columns).fillna(False).to_numpy() & U
        di, ci = np.nonzero(E)
        row = {"olay": name}
        for h in HORIZONS:
            x = exc[h][di, ci]
            ok = np.isfinite(x)
            if ok.sum() < 30:
                continue
            d_ok, x_ok = di[ok], x[ok]
            wk = pd.Series(x_ok).groupby(d_ok).mean()
            t = wk.mean() / (wk.std() / np.sqrt(len(wk))) if len(wk) > 2 else np.nan
            yr = pd.Series(x_ok).groupby(years[d_ok]).mean()
            row |= {f"n_{h}": int(ok.sum()), f"ort_{h}": float(np.mean(x_ok)), f"medyan_{h}": float(np.median(x_ok)),
                    f"isabet_{h}": float((x_ok > 0).mean()), f"t_{h}": float(t),
                    f"kazanan_kat_{h}": float(top[h][d_ok, ci[ok]].mean() / 0.05),
                    f"kaybeden_kat_{h}": float(bot[h][d_ok, ci[ok]].mean() / 0.05),
                    f"tutarlilik_{h}": float((np.sign(yr) == np.sign(np.mean(x_ok))).mean()), f"yil_{h}": int(len(yr))}
        rows.append(row)
    df = pd.DataFrame(rows)

    def cls(r):
        if pd.isna(r.get("ort_13")):
            return "Yetersiz örnek"
        if r.ort_13 >= 0.02 and r.t_13 >= 3 and r.tutarlilik_13 >= 0.7:
            return "Yüksek kâr belirtisi"
        if r.ort_13 <= -0.02 and r.t_13 <= -3 and r.tutarlilik_13 >= 0.7:
            return "Uyarı"
        if r.kazanan_kat_13 >= 1.5 and r.kaybeden_kat_13 >= 1.5:
            return "Büyük hareket (yön belirsiz)"
        return "Etkisiz / zayıf"
    df["sinif"] = df.apply(cls, axis=1)
    return df.sort_values("ort_13", ascending=False)


def render(df: pd.DataFrame) -> None:
    st = Styles()
    H = lambda cells: [Paragraph(c, st.hdr) for c in cells]
    pc = lambda x: "—" if pd.isna(x) else f"{x * 100:+.1f}%"
    f2 = lambda x: "—" if pd.isna(x) else f"{x:.2f}"
    order = ["Yüksek kâr belirtisi", "Büyük hareket (yön belirsiz)", "Uyarı", "Etkisiz / zayıf", "Yetersiz örnek"]

    def table(sub):
        t = [H(["Olay", "Örnek", "1 ay fazla", "3 ay fazla", "6 ay fazla", "3 ay isabet", "t (3 ay)", "Yıl tutarlılığı",
                "Büyük kazanan katı (3 ay)", "Büyük kaybeden katı (3 ay)"])]
        for r in sub.itertuples():
            t.append([Paragraph(r.olay, st.cell), f"{int(r.n_13):,}" if not pd.isna(r.n_13) else "—", pc(r.ort_4), pc(r.ort_13),
                      pc(r.ort_26), "—" if pd.isna(r.isabet_13) else f"%{r.isabet_13 * 100:.0f}",
                      f2(r.t_13), "—" if pd.isna(r.tutarlilik_13) else f"%{r.tutarlilik_13 * 100:.0f}", f2(r.kazanan_kat_13),
                      f2(r.kaybeden_kat_13)])
        return _table(st, t, [x * cm for x in (8.2, 1.7, 1.8, 1.8, 1.8, 1.8, 1.6, 2.0, 2.4, 2.4)])

    cnt = df.sinif.value_counts()
    story = [Paragraph("Rapor 7 — Olay belirtileri: \"şu olursa yüksek kâr belirtisidir\"", st.h1),
             Paragraph("Her olay, hissede gerçekleştiği hafta (o gün bilinen bilgiyle) ele alınır ve hissenin sonraki 1, 3 ve 6 ayda "
                       "aynı haftanın evren ortalamasına göre fazla getirisi ölçülür. Dönem 2010–2025; evren alınabilir faaliyet şirketleri "
                       "(≥ 5 $, ≥ 1 mn $/gün; banka, sigorta, GYO, fon, SPAC hariç). t değeri aynı haftadaki olayları tek gözlem sayar. "
                       "<b>Yüksek kâr belirtisi</b>: 3 ayda ort. ≥ +%2, t ≥ 3, yılların ≥ %70'inde aynı yön. <b>Uyarı</b>: tersi. "
                       "<b>Büyük hareket</b>: hem büyük kazanan hem büyük kaybeden olasılığı ≥ 1,5 kat (yön belirsiz, oynaklık habercisi). "
                       "Bu olaylar modelde 'olay geldiği an' sinyali olarak kullanılacak; Reddit, haber kelimeleri ve yeni kaynaklar "
                       "geldikçe rapora eklenecek.", st.box),
             Paragraph("Özet: " + ", ".join(f"{k}: {cnt.get(k, 0)}" for k in order), st.body)]
    for k in order:
        sub = df[df.sinif == k]
        if len(sub):
            story += [Spacer(1, 6), Paragraph(f"{k} ({len(sub)})", st.h2), table(sub)]
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.2 * cm, rightMargin=1.2 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.2 * cm, title="Rapor 7 — Olay belirtileri")
    doc.build(story)


def main() -> pd.DataFrame:
    p, sigs, inv, etf, sector = hs.prepare()
    ev = events(p, sigs)
    print(f"{len(ev)} olay türü", flush=True)
    df = study(ev, p, inv)
    JSON.write_text(json.dumps(df.round(4).to_dict(orient="records"), ensure_ascii=False, indent=1, default=float))
    render(df)
    cols = ["olay", "sinif", "n_13", "ort_4", "ort_13", "ort_26", "t_13", "tutarlilik_13", "kazanan_kat_13", "kaybeden_kat_13"]
    print(df[cols].round(3).to_string(index=False))
    print(OUT)
    return df


if __name__ == "__main__":
    main()

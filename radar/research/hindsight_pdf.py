"""Geriye bakış PDF'leri: python -m radar.research.hindsight_pdf

- reports/geriye_bakis/1_ne_olmaliydi_yillik.pdf: her yıl en çok kazandıranlar, SPY üstü/altı, asla alınmamalı
- reports/geriye_bakis/2_neden_yillik.pdf: yıl başındaki işaretler (tüm sinyaller), tutarlılık, hisse profilleri
- reports/geriye_bakis/yillik_tum_hisseler.csv: tüm listeler (her yıl her hisse ve sınıfı)
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.research import hindsight as hs
from radar.weekly import labels
from radar.weekly.pdf import Styles, _table, pct, tr_date

OUT = config.ROOT / "reports" / "geriye_bakis"
N_LIST = 25


def lab(name: str) -> str:
    return labels.signal(name)


def _doc(path, title):
    return SimpleDocTemplate(str(path), pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm,
                             topMargin=1.2 * cm, bottomMargin=1.3 * cm, title=title)


def _footer(st, text):
    def f(canvas, doc):
        canvas.saveState()
        canvas.setFont(st.reg, 7)
        canvas.drawString(1.4 * cm, 0.8 * cm, text)
        canvas.drawRightString(landscape(A4)[0] - 1.4 * cm, 0.8 * cm, f"Sayfa {doc.page}")
        canvas.restoreState()
    return f


def stock_table(st, df: pd.DataFrame, with_exit: bool = False):
    head = ["#", "Sembol", "Şirket", "Sektör", "Yıl başı fiyat $", "1 yıl getiri", "S&P 500'e göre"] + (["Not"] if with_exit else [])
    data = [head]
    for i, (_, r) in enumerate(df.iterrows(), 1):
        data.append([str(i), Paragraph(str(r.sembol), st.cellb), Paragraph(str(r.sirket)[:45], st.cell), r.sektor,
                     f"{r.fiyat:.2f}" if pd.notna(r.fiyat) else "—", pct(r.getiri, 0), pct(r.spy_farki, 0)]
                    + ([r.cikis or ""] if with_exit else []))
    w = [0.7, 1.6, 7.0, 3.2, 2.4, 2.2, 2.6] + ([2.8] if with_exit else [])
    return _table(st, data, [x * cm for x in w])


def render_what(results: list[hs.YearResult], path) -> None:
    st = Styles()
    story = [Paragraph("Geriye Bakış 1 — Ne olmalıydı? (yıl yıl)", st.h1),
             Paragraph("Her yılın ilk Cuma'sında yatırılabilir faaliyet şirketlerinden (fiyat ≥ 5 $, günlük işlem ≥ 1 mn $; "
                       "banka, sigorta, GYO, fon ve SPAC hariç) alınsaydı, 52 hafta sonra ne olurdu? Borsadan çıkan hisseler "
                       "çıkış değeriyle, iflas edenler 0 ile hesaplandı. "
                       "<b>Piyasa</b> = S&amp;P 500 (SPY, temettü dahil). Kilitli yıllar (2023–2025) son testten sonra eklenecek.", st.body),
             Spacer(1, 6)]
    data = [["Yıl", "Hisse", "S&P 500", "Nasdaq 100", "Medyan hisse", "S&P'yi geçen", "S&P'nin altında", "+%100 ve üstü",
             "−%50 ve altı", "İflas", "Borsadan çıkan"]]
    for r in results:
        s = r.summary
        data.append([str(r.year), f"{s['hisse']:,}", pct(s["spy"], 0), pct(s["qqq"], 0), pct(s["medyan"], 0),
                     f"{s['spy_ustu']:,} (%{s['spy_ustu'] / s['hisse'] * 100:.0f})", f"{s['spy_alti']:,}",
                     str(s["yuz_ustu"]), str(s["elli_kayip"]), str(s["iflas"]), str(s["cikis"])])
    story += [Paragraph("Özet", st.h2), _table(st, data, [x * cm for x in (1.3, 1.6, 2.0, 2.2, 2.4, 3.2, 2.8, 2.6, 2.6, 1.4, 2.6)]),
              Spacer(1, 4),
              Paragraph("Tam listeler (her yıl her hisse, getiri ve sınıf): yillik_tum_hisseler.csv. "
                        "Piyasanın üstünde/altında biten hisseler her yıl binlerce olduğu için PDF'te en uç örnekler gösterilir.", st.small)]
    for r in results:
        tab = r.table
        story += [PageBreak(), Paragraph(f"{r.year} — başlangıç {tr_date(r.date)}", st.h2),
                  Paragraph(f"S&amp;P 500 {pct(r.summary['spy'], 0)}, Nasdaq 100 {pct(r.summary['qqq'], 0)}, medyan hisse "
                            f"{pct(r.summary['medyan'], 0)}. {r.summary['spy_ustu']:,} hisse piyasanın üstünde, "
                            f"{r.summary['spy_alti']:,} hisse altında bitirdi; {r.summary['yuz_ustu']} hisse iki katına çıktı, "
                            f"{r.summary['elli_kayip']} hisse yarısından fazlasını kaybetti ({r.summary['iflas']} iflas).", st.body),
                  Paragraph(f"Alınsaydı çok kazandıracaklar (en iyi {N_LIST})", st.h3), stock_table(st, tab.head(N_LIST)),
                  Spacer(1, 4),
                  Paragraph(f"Asla alınmamalıydı (en kötü {N_LIST})", st.h3), stock_table(st, tab.tail(N_LIST).iloc[::-1], True)]
        mid = tab[(tab.sinif == "piyasanın üstünde")]
        low = tab[(tab.sinif == "piyasanın altında")]
        story += [Spacer(1, 4), Paragraph(
            f"Piyasanın üstünde (çok kazandıranlar dışında) {len(mid):,} hisse; örnekler: " +
            ", ".join(f"{s} {pct(g, 0)}" for s, g in zip(mid.sembol.head(30), mid.getiri.head(30))) + ". "
            f"Piyasanın altında (asla alınmamalılar dışında) {len(low):,} hisse; örnekler: " +
            ", ".join(f"{s} {pct(g, 0)}" for s, g in zip(low.sembol.tail(30), low.getiri.tail(30))) + ".", st.small)]
    doc = _doc(path, "Geriye bakış 1 — Ne olmalıydı")
    f = _footer(st, "Fırsat Radarı · Geriye bakış 1 · yıl yıl")
    doc.build(story, onFirstPage=f, onLaterPages=f)


def render_why(results, agg: pd.DataFrame, extra: dict, path) -> None:
    st = Styles()
    years = len(results)
    cont = agg[agg.tur == "sürekli"].copy()
    ev = agg[agg.tur == "olay"].copy()
    story = [Paragraph("Geriye Bakış 2 — Neden? Yıl başındaki işaretler (yıl yıl)", st.h1),
             Paragraph(
                 "Her yıl başında, o yıl en çok kazandıran %10 (<b>kazananlar</b>) ve en çok kaybettiren %10 (<b>kaybedenler</b>) "
                 "hisselerin elimizdeki tüm sinyallerdeki durumu incelendi. Sinyaller yalnızca o gün bilinen değerlerdir.<br/>"
                 "<b>Kazanan katı</b>: sinyal en yüksek %20'deyken kazanan çıkma olasılığı / genel olasılık (1,0 = etkisiz; "
                 "1,5 = %50 daha olası). <b>Kaybeden katı</b> aynı şekilde. <b>Tutarlılık</b>: kaç yılda kazananların sinyal "
                 "ortalaması kaybedenlerinkinden aynı yönde farklıydı.<br/>"
                 "<b>Önemli</b>: hiçbir sinyal kesin değildir; en güçlüleri bile olasılığı artırır, garanti etmez. Bu sayfalar "
                 "hangi işaretlerin geçmişte tutarlı çalıştığını gösterir ve modeli yönlendirmek için kullanılacak.", st.box)]

    def sig_table(df, cols, heads, widths):
        data = [[Paragraph(h, st.hdr) for h in heads]]
        for _, r in df.iterrows():
            data.append([Paragraph(lab(r.sinyal), st.cell)] + [c(r) for c in cols])
        return _table(st, data, [x * cm for x in widths])

    fmt = lambda x: "—" if pd.isna(x) else f"{x:.2f}"
    cont["guc"] = (cont.kazanan_kat - 1).abs() + (cont.kaybeden_kat - 1).abs() + \
        (cont.kazanan_kat_dusuk - 1).abs() + (cont.kaybeden_kat_dusuk - 1).abs()
    cont = cont.sort_values(["guc"], ascending=False)
    story += [Paragraph("1. Sürekli sinyaller — kazananları ve kaybedenleri ayırt etme gücü", st.h2),
              Paragraph("Yüksek (en üst %20) ve düşük (en alt %20) uçlar ayrı gösterilir. Örnek okuma: kazanan katı (yüksek) 1,6 ve "
                        "kaybeden katı (yüksek) 0,6 → bu sinyal yüksek olan hisselerde kazanan çıkma olasılığı %60 daha fazla, "
                        "kaybeden çıkma olasılığı %40 daha az.", st.small), Spacer(1, 3),
              sig_table(cont, [lambda r: fmt(r.kazanan_kat), lambda r: fmt(r.kaybeden_kat), lambda r: fmt(r.kazanan_kat_dusuk),
                               lambda r: fmt(r.kaybeden_kat_dusuk),
                               lambda r: f"{int(r.yon_yukari)}↑ / {int(r.yon_asagi)}↓ ({r.tutarlilik * 100:.0f}%)",
                               lambda r: f"%{r.kapsam * 100:.0f}", lambda r: str(int(r.yil))],
                        ["Sinyal", "Kazanan katı (yüksek)", "Kaybeden katı (yüksek)", "Kazanan katı (düşük)", "Kaybeden katı (düşük)",
                         "Yön (yıl)", "Kapsam", "Yıl"], [8.5, 2.6, 2.6, 2.6, 2.6, 3.4, 1.8, 1.0])]
    ev = ev.sort_values("kaybeden_kat", ascending=False)
    story += [PageBreak(), Paragraph("2. Olaylar (8-K bildirimleri, yönetici alımları, denetçi uyarısı vb.)", st.h2),
              Paragraph("Olay varken kazanan / kaybeden çıkma olasılığının genele oranı.", st.small), Spacer(1, 3),
              sig_table(ev, [lambda r: fmt(r.kazanan_kat), lambda r: fmt(r.kaybeden_kat),
                             lambda r: f"{int(r.yon_yukari)}↑ / {int(r.yon_asagi)}↓", lambda r: f"%{r.kapsam * 100:.1f}",
                             lambda r: str(int(r.yil))],
                        ["Olay", "Kazanan katı", "Kaybeden katı", "Medyan getiri yönü (yıl)", "Hisselerin yüzde kaçında", "Yıl"],
                        [9.5, 2.8, 2.8, 4.0, 3.6, 1.2])]

    # En güçlü ve tutarlı işaretlerin sade özeti
    good = cont[(cont.tutarlilik >= 0.75) & (cont.yil >= 8)]
    lines = []
    for _, r in good.head(12).iterrows():
        side = "yüksek" if r.yon_yukari >= r.yon_asagi else "düşük"
        lines.append(f"• <b>{lab(r.sinyal)}</b>: {side} olması kazanmaya işaret etti ({r.tutarlilik * 100:.0f}% yıl tutarlı; "
                     f"yüksek uçta kazanan katı {fmt(r.kazanan_kat)}, kaybeden katı {fmt(r.kaybeden_kat)}).")
    ev_bad = ev[(ev.kaybeden_kat >= 1.3) & (ev.yil >= 8)]
    for _, r in ev_bad.head(6).iterrows():
        lines.append(f"• <b>{lab(r.sinyal)}</b> olayı kaybetme olasılığını {fmt(r.kaybeden_kat)} kat artırdı.")
    story += [Paragraph("3. Özet: geçmişte en tutarlı işaretler", st.h2),
              Paragraph("<br/>".join(lines) or "Tutarlı işaret bulunamadı.", st.body)]

    story += [Paragraph("4. Elimizde olmayan ama eklenebilecek işaretler", st.h2), Paragraph(
        "• <b>Yönetimin söyledikleri çıktı mı?</b> Şirketin önceki yıl verdiği hedefler (8-K/10-K metninden) ile gerçekleşen "
        "sonuçların karşılaştırılması — ücretsiz, SEC metinlerinden çıkarılabilir; en özgün işaret olabilir.<br/>"
        "• <b>Kazanç açıklaması sonrası tepki</b> (8-K Madde 2.02 haftasındaki fiyat hareketi; literatürde güçlü) — eldeki "
        "verilerle hemen eklenebilir.<br/>"
        "• <b>Açığa satış oranı</b> (FINRA, ücretsiz; geçmiş veri yüklenmeli).<br/>"
        "• <b>Devlet sözleşmeleri</b> (USAspending, ücretsiz; geçmiş veri yüklenmeli).<br/>"
        "• <b>Patent başvuruları</b> (USPTO; anahtar bekleniyor).<br/>"
        "• <b>Analist beklenti değişimleri, opsiyon akışı, sosyal medya (X, Reddit, TikTok)</b> — ücretsiz ve güvenilir geçmiş "
        "verisi yok; yalnızca canlı takipte kullanılabilir.", st.body)]

    # Hisse profilleri
    story += [PageBreak(), Paragraph("5. Yıl yıl: kazananlar ve kaybedenler yıl başında nasıl görünüyordu?", st.h2),
              Paragraph("Her yılın en iyi ve en kötü 10 hissesi: yıl başında en uç olduğu sinyaller (yüzdelik ≥ 90 ya da ≤ 10) ve "
                        "olaylar. Veri kapsamı: sürekli sinyallerin yüzde kaçında değeri vardı.", st.small)]
    for res in results:
        prof = hs.profiles(res, extra["yuzdelik"][res.year], extra["olaylar"])
        data = [["", "Sembol", "Getiri", "Yüksek olanlar (≥ 90)", "Düşük olanlar (≤ 10)", "Olaylar", "Kapsam"]]
        for _, r in prof.iterrows():
            data.append([r.grup, Paragraph(r.sembol, st.cellb), pct(r.getiri, 0) + (f" ({r.cikis})" if r.cikis else ""),
                         Paragraph(", ".join(lab(x) for x in r.yuksek[:6]) or "—", st.cell),
                         Paragraph(", ".join(lab(x) for x in r.dusuk[:6]) or "—", st.cell),
                         Paragraph(", ".join(lab(x) for x in r.olaylar[:4]) or "—", st.cell), f"%{r.veri_kapsami * 100:.0f}"])
        story += [Paragraph(f"{res.year}", st.h3), _table(st, data, [x * cm for x in (1.6, 1.6, 2.6, 8.0, 7.0, 4.6, 1.4)])]
    doc = _doc(path, "Geriye bakış 2 — Neden")
    f = _footer(st, "Fırsat Radarı · Geriye bakış 2 · yıl yıl")
    doc.build(story, onFirstPage=f, onLaterPages=f)


def main() -> None:
    t0 = time.time()
    p, sigs, inv, etf, sector = hs.prepare()
    print(f"hazır ({round(time.time() - t0)} sn)", flush=True)
    results = hs.year_tables(p, inv, etf, sector)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.concat([r.table.assign(yil=r.year) for r in results]).to_csv(OUT / "yillik_tum_hisseler.csv", index_label="cik")
    render_what(results, OUT / "1_ne_olmaliydi_yillik.pdf")
    print(f"PDF 1 ({round(time.time() - t0)} sn)", flush=True)
    agg, extra = hs.signal_study(results, sigs, p["price"].index)
    agg.to_csv(OUT / "yillik_sinyal_ozeti.csv", index=False)
    extra["yillik"].to_csv(OUT / "yillik_sinyal_yil_yil.csv", index=False)
    render_why(results, agg, extra, OUT / "2_neden_yillik.pdf")
    print(f"PDF 2 ({round(time.time() - t0)} sn)", flush=True)


if __name__ == "__main__":
    main()

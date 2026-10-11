"""Her yıl için ulaşılabilecek en yüksek kâr (sonradan bakınca): python -m radar.research.maxprofit

Yıl başında (ilk Cuma) alınıp 52 hafta tutulsaydı, alınabilir hisseler (faaliyet şirketleri, ≥ 5 $, ≥ 1 mn $/gün)
arasından en iyi N hisse (eşit ağırlık) ne getirirdi? Borsadan çıkanlar çıkış değeriyle, iflaslar 0 ile.
Karşılaştırma: medyan hisse, S&P 500, sürüm 3 modeli (iç içe test; 2014–2025).
Çıktı: reports/research/4_her_yil_maksimum_kar.pdf
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.research import panel, quick
from radar.weekly.pdf import Styles, _table, pct

OUT = config.ROOT / "reports" / "research" / "4_her_yil_maksimum_kar.pdf"
NS = (5, 10, 20, 50, 100, 1000)
YEARS = range(2010, 2026)


def main() -> None:
    st = Styles()
    d = quick.QuickData()
    spy = d.spy()
    p = panel.build()
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik").set_index("cik")
    names = sec.name.reindex(p["price"].columns).fillna("").str.replace(r" - .*$", "", regex=True).to_numpy()
    raw = p["raw"].to_numpy()
    px = p["price"].to_numpy()
    sec_c = sec.reindex(p["price"].columns)
    status, end, bankrupt = sec_c.status.to_numpy(), sec_c.end.to_numpy(dtype="datetime64[ns]"), sec_c.bankrupt.fillna(False).to_numpy()

    def detail(i: int, t: int) -> tuple[str, str, str]:
        """Yıl sonu/çıkış gerçek fiyatı, çıkış türü, veri notu."""
        t1 = min(t + quick.W, len(d.dates) - 1)
        out = "borsada"
        last = raw[t1, i]
        if status[i] == "çıktı" and end[i] < np.datetime64(d.dates[t1]):
            out = "iflas (0)" if bankrupt[i] else f"borsadan çıktı {str(end[i])[:10]} (satın alma/birleşme)"
            seg = raw[t:t1 + 1, i]
            last = seg[np.isfinite(seg)][-1] if np.isfinite(seg).any() else np.nan
        path = px[t:t1 + 1, i]
        steps = np.diff(path[np.isfinite(path)])
        notes = []
        if (steps == 0).sum() > 10:
            notes.append("seyrek fiyat (SEC FTD)")
        w = path[1:] / path[:-1] - 1
        if np.nanmax(w, initial=0) > 1.5:
            notes.append(f"tek hafta +{np.nanmax(w):.0%}")
        return ("—" if not np.isfinite(last) else f"{last:.2f}"), out, ", ".join(notes) or "—"
    nested = json.loads((config.ROOT / "reports" / "research" / "nested.json").read_text())["aile_yillar"]["ridge_secili"]
    H = lambda cells: [Paragraph(c, st.hdr) for c in cells]

    summary = [H(["Yıl", "En iyi 5", "En iyi 10", "En iyi 20", "En iyi 100", "Medyan hisse", "S&amp;P 500", "Sürüm 3 modeli",
                  "Modelin en iyi 20'den yakaladığı"])]
    pages = []
    for y in YEARS:
        t = quick.year_start(d.dates, y)
        r = np.asarray(d.fwd[t], dtype=float)
        ok = np.asarray(d.eval_u[t]) & np.isfinite(r)
        idx = np.flatnonzero(ok)
        top = idx[np.argsort(-r[idx])]
        avg = {n: float(r[top[:n]].mean()) for n in NS}
        spy_y = float(spy.iloc[t + quick.W] / spy.iloc[t] - 1)
        model = nested.get(str(y))
        caught = "—"
        if model:
            best20 = {str(d.symbols[i]) for i in top[:20]}
            caught = f"{sum(s in best20 for s, _ in model['secim'])}/20"
        summary.append([str(y), pct(avg[5], 0), pct(avg[10], 0), pct(avg[20], 0), pct(avg[100], 0), pct(float(np.median(r[idx])), 0),
                        pct(spy_y, 0), pct(model["model"], 0) if model else "—", caught])
        tab = [H(["Seçim", "Ort. getiri", "10.000 $ ne olurdu", "Listenin en kötüsü"])] + \
              [[f"En iyi {n}", pct(avg[n], 0), f"{10000 * (1 + avg[n]):,.0f} $", pct(float(r[top[n - 1]]), 0)] for n in NS]
        best = [H(["#", "Sembol", "Şirket", "Giriş fiyatı $", "Çıkış fiyatı $", "1 yıl getiri", "Çıkış", "Veri notu"])]
        for k, i in enumerate(top[:20]):
            last, out, note = detail(i, t)
            best.append([str(k + 1), Paragraph(str(d.symbols[i]), st.cellb), Paragraph(names[i][:45], st.cell),
                         f"{raw[t, i]:.2f}" if np.isfinite(raw[t, i]) else "—", last, pct(float(r[i]), 0),
                         Paragraph(out, st.cell), Paragraph(note, st.cell)])
        pages += [PageBreak(), Paragraph(f"{y} — {d.dates[t].date()} başlangıç ({ok.sum():,} alınabilir hisse)", st.h2),
                  Paragraph(f"Medyan hisse {pct(float(np.median(r[idx])), 0)}, S&amp;P 500 {pct(spy_y, 0)}"
                            + (f", sürüm 3 modeli {pct(model['model'], 0)}" if model else "") + ".", st.body), Spacer(1, 3),
                  _table(st, tab, [x * cm for x in (3, 3, 4, 4)]), Spacer(1, 5),
                  Paragraph("Sonradan bakınca en çok kazandıran 20 hisse", st.h3), _table(st, best, [x * cm for x in (0.8, 1.7, 7, 2.2, 2.2, 2.1, 5.8, 4.8)])]
        print(y, f"en iyi 5 {avg[5]:+.0%}", flush=True)

    story = [Paragraph("Rapor 4 — Her yıl ulaşılabilecek en yüksek kâr (sonradan bakınca)", st.h1),
             Paragraph("Soru: Yılın ilk Cuma'sında hisse alınıp 1 yıl tutulsaydı ve hangi hisselerin yükseleceği önceden bilinseydi, en fazla "
                       "ne kazanılırdı? En yüksek kâr her zaman en iyi 5 hissededir; hisse sayısı arttıkça ortalama düşer. Evren: alınabilir "
                       "faaliyet şirketleri (Nasdaq + NYSE + NYSE American; fiyat ≥ 5 $, günlük işlem ≥ 1 mn $; banka, sigorta, GYO, fon, "
                       "SPAC hariç). Borsadan çıkanlar çıkış değeriyle, iflaslar 0 ile hesaplandı; alım-satım maliyeti düşülmedi (tavan).", st.body),
             Paragraph("Çok küçük ve az işlem gören hisseler dahil edilmedi: alınabilir değiller ve fiyatları seyrek kaynaktan geldiği için bazı "
                       "uç değerler (ör. 2012'de +%27.400) veri hatası şüphesi taşıyor. Fiyatlar o gün borsada işlem gören gerçek fiyattır "
                       "(sonraki bölünmeler geri alınmış); getiriler temettü ve bölünmelere göre düzeltilmiştir. Borsadan çıkan şirketlerde "
                       "çıkış fiyatı kullanılır (çoğu satın alma primidir), iflasta 0. 'Seyrek fiyat': günlük seri yok, SEC FTD "
                       "kayıtlarındaki fiyatlar kullanıldı (yaklaşık değer). Sürüm 3 modeli sütunu: iç içe testte (yalnızca geçmiş "
                       "verilerle) o yıl seçtiği 20 hissenin getirisi ve bunlardan kaçının yılın en iyi 20'si içinde olduğu.", st.small),
             Spacer(1, 5), _table(st, summary, [x * cm for x in (1.4, 2.2, 2.2, 2.2, 2.4, 2.6, 2.2, 2.8, 4.2)])] + pages
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.3 * cm, title="Rapor 4 — maksimum kâr")
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()

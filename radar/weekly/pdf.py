"""Haftalık Türkçe PDF rapor (reportlab)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from radar import config
from radar.weekly import labels
from radar.weekly.snapshot import THRESHOLD, Snapshot

FONT_DIRS = [Path("/usr/share/fonts/truetype/dejavu"), Path("/usr/share/fonts/dejavu"), Path("/usr/share/fonts/TTF")]
MONTHS = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
RISK_COLORS = {1: "#2e7d32", 2: "#7cb342", 3: "#f9a825", 4: "#ef6c00", 5: "#c62828"}
RISK_NAMES = {1: "çok düşük", 2: "düşük", 3: "orta", 4: "yüksek", 5: "çok yüksek"}
ACCENT = colors.HexColor("#1a3c6e")


def _fonts() -> tuple[str, str]:
    for d in FONT_DIRS:
        if (d / "DejaVuSans.ttf").exists():
            pdfmetrics.registerFont(TTFont("Gov", str(d / "DejaVuSans.ttf")))
            pdfmetrics.registerFont(TTFont("Gov-B", str(d / "DejaVuSans-Bold.ttf")))
            return "Gov", "Gov-B"
    raise FileNotFoundError("DejaVuSans.ttf bulunamadı (Türkçe karakterler için gerekli): apt install fonts-dejavu-core")


def tr_date(d: pd.Timestamp) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def pct(x: float, digits: int = 1) -> str:
    return "—" if pd.isna(x) else f"%{x * 100:+.{digits}f}".replace("%+", "+%").replace("%-", "−%")


class Styles:
    def __init__(self):
        reg, bold = _fonts()
        self.reg, self.bold = reg, bold
        self.h1 = ParagraphStyle("h1", fontName=bold, fontSize=20, leading=24, textColor=ACCENT, spaceAfter=6)
        self.h2 = ParagraphStyle("h2", fontName=bold, fontSize=13, leading=16, textColor=ACCENT, spaceBefore=10, spaceAfter=5)
        self.h3 = ParagraphStyle("h3", fontName=bold, fontSize=10.5, leading=13, spaceBefore=2, spaceAfter=2)
        self.body = ParagraphStyle("body", fontName=reg, fontSize=9, leading=12, alignment=TA_LEFT)
        self.small = ParagraphStyle("small", fontName=reg, fontSize=7.5, leading=9.5, textColor=colors.HexColor("#444444"))
        self.cell = ParagraphStyle("cell", fontName=reg, fontSize=7.5, leading=9)
        self.cellb = ParagraphStyle("cellb", fontName=bold, fontSize=7.5, leading=9)
        self.box = ParagraphStyle("box", parent=self.body, backColor=colors.HexColor("#eef2f8"), borderPadding=6,
                                  borderColor=colors.HexColor("#c5d0e0"), borderWidth=0.5, spaceBefore=4, spaceAfter=8)


def _table(st: Styles, data: list[list], widths: list[float], risk_col: int | None = None,
           risk_vals: list | None = None, zebra: bool = True) -> Table:
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("FONT", (0, 0), (-1, 0), st.bold, 7.5), ("FONT", (0, 1), (-1, -1), st.reg, 7.5),
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (2, 1), (-1, -1), "CENTER"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#d0d7e2")),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    if zebra:
        for i in range(2, len(data), 2):
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f6f8fb")))
    if risk_col is not None and risk_vals:
        for i, lv in enumerate(risk_vals, start=1):
            if pd.notna(lv):
                style += [("BACKGROUND", (risk_col, i), (risk_col, i), colors.HexColor(RISK_COLORS[int(lv)])),
                          ("TEXTCOLOR", (risk_col, i), (risk_col, i), colors.white)]
    t.setStyle(TableStyle(style))
    return t


def _num(x, d=0) -> str:
    return "—" if pd.isna(x) else f"{x:.{d}f}"


def _money(x) -> str:
    if pd.isna(x):
        return "—"
    if x >= 1e9:
        return f"{x / 1e9:.1f} mr $"
    return f"{x / 1e6:.1f} mn $" if x >= 1e6 else f"{x / 1e3:.0f} bin $"


def ranking_table(st: Styles, df: pd.DataFrame) -> Table:
    head = ["#", "Sembol", "Şirket", "Fiyat $", "Hacim/gün", "Potansiyel", "Vade", "Risk",
            "İş modeli", "Gündem", "Kurumsal", "Tema", "Piyasa"]
    data = [head]
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        data.append([str(i), Paragraph(r.sembol, st.cellb), Paragraph(str(r.sirket)[:48], st.cell),
                     _num(r.fiyat, 2), _money(r.islem_hacmi), _num(r.potansiyel, 1),
                     labels.HORIZONS.get(r.vade, "—") if pd.notna(r.vade) else "—",
                     _num(r.risk), _num(r.yol1), _num(r.yol2), _num(r.yol3), _num(r.yol4), _num(r.piyasa)])
    w = [0.7, 1.5, 6.2, 1.5, 1.9, 1.7, 1.5, 1.0, 1.6, 1.5, 1.6, 1.3, 1.4]
    return _table(st, data, [x * cm for x in w], risk_col=7, risk_vals=list(df.risk))


def reason_text(item: tuple) -> str:
    name, _, kind, v = item
    lab = labels.signal(name)
    if kind == "olay":
        return f"{lab}: <b>var</b>"
    if name == "kucuk_boyut":
        return f"{'Küçük' if v >= 50 else 'Büyük'} şirket (küçüklük yüzdeliği {v:.0f}/100)"
    return f"{lab}: <b>{'yüksek' if v >= 50 else 'düşük'}</b> (yüzdelik {v:.0f}/100)"


def card(st: Styles, cik: str, r: pd.Series, snap: Snapshot) -> KeepTogether:
    reasons = snap.reasons.get(cik, [])
    pos = [reason_text(x) for x in reasons if x[1] > 0]
    neg = [reason_text(x) for x in reasons if x[1] < 0]
    risks = [labels.RISK.get(k, k) for k in snap.risk_reasons.get(cik, [])]
    title = (f"{r.sembol} · {r.sirket} — potansiyel {_num(r.potansiyel, 1)}, "
             f"vade {labels.HORIZONS.get(r.vade, '—') if pd.notna(r.vade) else '—'}, risk {_num(r.risk)} "
             f"({RISK_NAMES.get(int(r.risk), '—') if pd.notna(r.risk) else '—'})")
    hz = " · ".join(f"{labels.HORIZONS[h]}: {_num(r[f'puan_{h}'])}" for h in labels.HORIZONS)
    roads = " · ".join(f"{labels.ROADS[g]}: {_num(r[g])}" for g in ("yol1", "yol2", "yol3", "yol4", "piyasa"))
    left = [Paragraph("<b>Puanı yükselten</b>", st.cell)] + [Paragraph("+ " + x, st.cell) for x in pos or ["—"]]
    mid = [Paragraph("<b>Puanı düşüren</b>", st.cell)] + [Paragraph("− " + x, st.cell) for x in neg or ["—"]]
    right = [Paragraph("<b>Risk etkenleri</b>", st.cell)] + [Paragraph("• " + x, st.cell) for x in risks or ["belirgin risk etkeni yok"]]
    body = Table([[left, mid, right]], colWidths=[10.2 * cm, 9.2 * cm, 6.4 * cm])
    body.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
    return KeepTogether([
        Paragraph(title, st.h3),
        Paragraph(f"Vadelere göre puan — {hz}", st.small),
        Paragraph(f"Yol puanları ({labels.HORIZONS.get(r.vade, '3 ay') if pd.notna(r.vade) else '3 ay'}) — {roads}", st.small),
        Spacer(1, 2), body, Spacer(1, 6),
    ])


def health_line(path: Path) -> str:
    try:
        d = json.loads(path.read_text())
    except (FileNotFoundError, ValueError):
        return "Veri sağlık raporu bulunamadı."
    s = [x["status"] for x in d["sources"]]
    warn = [x["title"] for x in d["sources"] if x["status"] != "ok"]
    when = pd.Timestamp(d["run_at"]).tz_convert("UTC")
    return (f"Veri sağlığı ({when:%Y-%m-%d %H:%M} UTC): {s.count('ok')} kaynak kullanılabilir · {s.count('warn')} dikkat · "
            f"{s.count('fail')} kullanılamaz." + (f" Dikkat gerektirenler: {', '.join(warn)}." if warn else ""))


def render(snap: Snapshot, out: Path, health_path: Path | None = None) -> Path:
    st = Styles()
    t = snap.table
    inv = t[t.yatirilabilir.fillna(False).astype(bool)]
    small = t[~t.yatirilabilir.fillna(False).astype(bool)]
    order = lambda d: d.sort_values(["potansiyel", "puan_3a"], ascending=False)
    top = order(inv).head(25)
    top_small = order(small).head(15)
    avoid = inv.sort_values("puan_3a").head(15)
    n_pot = int((inv.potansiyel >= THRESHOLD).sum())
    hz_counts = inv.vade.value_counts()

    story = [
        Paragraph("Fırsat Radarı — Haftalık Rapor", st.h1),
        Paragraph(f"<b>Hafta:</b> {tr_date(snap.date)} (Cuma kapanışı) · <b>Oluşturulma:</b> "
                  f"{pd.Timestamp.now(tz='UTC'):%Y-%m-%d %H:%M} UTC", st.body),
        Spacer(1, 6),
        Paragraph(f"Bu hafta Nasdaq'ta işlem gören <b>{len(t):,}</b> hisse puanlandı; bunların <b>{len(inv):,}</b> tanesi "
                  f"yatırılabilir (fiyat ≥ 5 $ ve günlük işlem hacmi ≥ 1 mn $). Yatırılabilir hisselerden <b>{n_pot}</b> "
                  f"tanesinin potansiyeli {THRESHOLD:.0f} ve üzeri. Atanan vadeler: " +
                  ", ".join(f"{labels.HORIZONS[h]} {int(hz_counts.get(h, 0))}" for h in labels.HORIZONS) + ".", st.body),
        Spacer(1, 4),
        Paragraph(health_line(health_path or config.ROOT / "reports" / "data_health" / "latest.json"), st.small),
        Paragraph("Nasıl okunur", st.h2),
        Paragraph(
            "<b>Potansiyel (0–100):</b> hissenin, bu hafta puanlanan tüm hisseler içinde modelin beklediği fazla getiriye "
            "göre sırası (100 = en iyi). Fazla getiri, hissenin getirisi ile aynı haftadaki medyan hissenin getirisi "
            "arasındaki farktır. Her vade için ayrı model var; potansiyel, en yüksek puanın alındığı vadedir.<br/>"
            "<b>Vade:</b> potansiyelin en yüksek olduğu süre (1 hafta → 1 yıl). Potansiyel 70'in altındaysa vade atanmaz.<br/>"
            "<b>Risk (1–5):</b> önümüzdeki 6–12 ayda büyük düşüş ve kötü çıkış (iflas, borsadan çıkarılma) olasılığı. "
            "Geçmişte risk 5 hisselerin yarısından fazlası bir yıl içinde %50+ düştü; risk 1'de bu oran %5.<br/>"
            "<b>Yol puanları (0–100):</b> her yolun kendi modelinin sırası. İş modeli = finansallar ve 10-K metinleri; "
            "Gündem = haber ve Wikipedia ilgisi; Kurumsal = yönetici alımları, fonlar, 8-K olayları, geri alımlar; "
            "Tema = şirketin temalarına ilgi; Piyasa = fiyat momentumu ve şirket büyüklüğü. Yaklaşık 50 = nötr ya da veri yok.",
            st.box),
        Paragraph(
            "Bu rapor istatistiksel bir modelin çıktısıdır, yatırım tavsiyesi değildir. Model hisseleri ortalamada "
            "doğru sıralar; tek tek hisselerde yanılması olağandır (ilk %10'un yaklaşık %55–60'ı medyanı geçer). "
            "Karar vermeden önce şirketi ayrıca incelemek gerekir.", st.small),
        PageBreak(),
        Paragraph("1. Öne çıkan fırsatlar — yatırılabilir hisseler", st.h2),
        Paragraph("Potansiyeli en yüksek 25 hisse. Risk sütunu renklidir (yeşil = düşük, kırmızı = yüksek).", st.small),
        Spacer(1, 3), ranking_table(st, top),
        PageBreak(),
        Paragraph("2. Küçük ve az işlem gören hisseler", st.h2),
        Paragraph("Fiyatı 5 $'ın altında ya da günlük işlem hacmi 1 mn $'ın altında olan hisseler. Model bu grupta "
                  "geçmişte daha güçlü ayrıştırdı, ancak alım-satım maliyeti ve risk belirgin şekilde yüksektir.", st.small),
        Spacer(1, 3), ranking_table(st, top_small),
        Paragraph("3. Uzak durulması gerekenler — yatırılabilir hisseler", st.h2),
        Paragraph("3 aylık puanı en düşük 15 hisse. Model en güvenilir şekilde bu grubu ayırt ediyor: geçmişte en düşük "
                  "%10'luk dilim medyan hisseden belirgin şekilde kötü getiri verdi.", st.small),
        Spacer(1, 3), ranking_table(st, avoid),
        PageBreak(),
        Paragraph("4. Hisse kartları — öne çıkan ilk 15 hisse", st.h2),
        Paragraph("Her kartta puanı en çok yükselten ve düşüren etkenler (modelin bu hafta kullandığı ağırlıklara göre) "
                  "ve risk etkenleri yer alır. Yüzdelik, hissenin o sinyalde evren içindeki sırasıdır (100 = en yüksek). "
                  "Birbiriyle ilişkili sinyallerde (ör. yönetici alımı sinyalleri) model birinin etkisini diğeriyle "
                  "dengeleyebilir; bu yüzden tek bir etken ters yönde görünebilir.", st.small),
        Spacer(1, 4),
    ]
    for cik, r in top.head(15).iterrows():
        story.append(card(st, cik, r, snap))

    story += [PageBreak(), Paragraph("5. Modelin karnesi — son 12 ay", st.h2),
              Paragraph("Son 12 ayda her hafta verilen puanların, getirisi tamamlanmış haftalardaki gerçekleşen sonucu. "
                        "Fazla getiri = hissenin getirisi − aynı evrendeki medyan hisse (uç değerler %1/%99'da kırpıldı). "
                        "İsabet = medyanı geçen hisse payı.", st.small), Spacer(1, 3)]
    tr = snap.track
    data = [["Vade", "Evren", "Hafta", "İlk %10 ort. fazla getiri", "İlk %10 isabet", "Son %10 ort. fazla getiri", "Son %10 isabet"]]
    for _, r in tr.iterrows():
        data.append([labels.HORIZONS[r.vade], r.evren, str(r.hafta), pct(r.ilk10_ort), f"%{r.ilk10_isabet * 100:.0f}",
                     pct(r.son10_ort), f"%{r.son10_isabet * 100:.0f}"])
    story += [_table(st, data, [x * cm for x in (2, 3, 1.5, 4.5, 3, 4.5, 3)]), Spacer(1, 6),
              Paragraph("Uzun dönem doğrulama (2016–2025, örneklem dışı) ve tek seferlik son dönem testi: "
                        "reports/research/ASAMA4_OZET.md. Özet: tüm hisselerde puan ile gerçekleşen fazla getiri arasındaki "
                        "sıra korelasyonu 3 ayda 0,14 (son dönemde 0,18); yatırılabilir hisselerde 0,08 (son dönemde 0,06, "
                        "istatistiksel olarak zayıf).", st.small),
              Paragraph("6. Notlar ve sınırlamalar", st.h2),
              Paragraph(
                  "• Model değer ve nakit akışı sinyallerine (serbest nakit akışı, kâr / piyasa değeri, geri alım) ağırlık "
                  "verir. Bu sinyaller bankalar ve finans şirketlerinde sistematik olarak yüksek çıktığından listelerde "
                  "finans sektörü ağırlıklı görünebilir. Sektör dengesi ileride ayrıca değerlendirilecek.<br/>"
                  "• Gündem (haber, Wikipedia) ve Tema yolları açıklama amaçlıdır; tek başlarına anlamlı bir öngörü gücü "
                  "göstermediler ve toplam puandaki ağırlıkları küçüktür.<br/>"
                  "• 6 ay ve 1 yıl vadelerinde son dönemde getirisi tamamlanmış hafta sayısı azdır; bu vadelerin karnesi "
                  "henüz güvenilir değildir.<br/>"
                  "• Veriler yalnızca yayımlandıkları tarihten itibaren kullanılır (geleceği görme yok). Eksik veri puanı "
                  "düşürmez, nötr sayılır.", st.body)]

    out.parent.mkdir(parents=True, exist_ok=True)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(st.reg, 7)
        canvas.setFillColor(colors.HexColor("#777777"))
        canvas.drawString(1.5 * cm, 0.9 * cm, f"Fırsat Radarı · {tr_date(snap.date)} · yatırım tavsiyesi değildir")
        canvas.drawRightString(landscape(A4)[0] - 1.5 * cm, 0.9 * cm, f"Sayfa {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(out), pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.3 * cm, bottomMargin=1.5 * cm, title=f"Fırsat Radarı {snap.date.date()}")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out

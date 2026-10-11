"""Rapor 3 — teşhis, istikrarlı işaretler, iç içe test ve dondurulmuş model (sürüm 3).

python -m radar.research.report_v3 → reports/research/3_teshis_ve_saglam_model.pdf
Girdiler: reports/research/teshis.json, nested.json, reports/canli/model_v3.json (+ <tarih>_v3.csv)
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.weekly import labels
from radar.weekly.pdf import Styles, _table, pct

R = config.ROOT / "reports"
OUT = R / "research" / "3_teshis_ve_saglam_model.pdf"


def lab(f: str) -> str:
    return labels.signal(f)


def main() -> None:
    st = Styles()
    tes = json.loads((R / "research" / "teshis.json").read_text())
    nes = json.loads((R / "research" / "nested.json").read_text())
    spec = json.loads((R / "canli" / "model_v3.json").read_text())
    picks = pd.read_csv(sorted((R / "canli").glob("*_v3.csv"))[-1])
    H = lambda cells: [Paragraph(c, st.hdr) for c in cells]

    fams = nes["aile_yillar"]
    def fam_row(name, fy):
        m = np.array([v["model"] for v in fy.values()]); e = np.array([v["esit"] for v in fy.values()])
        s = np.array([v["spy"] for v in fy.values()])
        return [name, pct(m.mean(), 1), f"{(m > 0).sum()}/{len(m)}", f"{(m > e).sum()}/{len(m)}", f"{(m > s).sum()}/{len(m)}",
                f"{np.mean([v['yukselen'] for v in fy.values()]):.1f}", f"{np.mean([v['en_iyi10'] for v in fy.values()]):.1f}"]
    proc = nes["ozet"]["ic_secimli_surec"]
    any_fy = next(iter(fams.values()))
    e_avg = np.mean([v["esit"] for v in any_fy.values()]); s_avg = np.mean([v["spy"] for v in any_fy.values()])
    res_tab = [H(["Yöntem", "Ort. 1 yıl getiri", "Kârda biten yıl", "Eşit ağırlıklı piyasayı geçen", "S&P 500'ü geçen",
                  "20 hisseden yükselen", "Yılın en iyi %10'undan"])]
    res_tab += [fam_row("İstikrarlı işaretler + ridge (DONDURULAN)", fams["ridge_secili"]),
                fam_row("Bileşik puan (öğrenmesiz)", fams["bileşik"]), fam_row("İstikrarlı işaretler + LightGBM", fams["lgbm_secili"]),
                ["Otomatik seçim süreci (en dürüst)", pct(proc["ort"], 1), f"{proc['kar_yili']}/12", f"{proc['esiti_gecen']}/12",
                 f"{proc['spyi_gecen']}/12", "—", f"{proc['en_iyi10_ort']:.1f}"],
                ["Eşit ağırlıklı piyasa", pct(e_avg, 1), "", "", "", "", ""], ["S&P 500", pct(s_avg, 1), "", "", "", "", ""]]
    years = sorted(fams["ridge_secili"], key=int)
    yy = [H(["Yıl"] + years)]
    yy.append(["Model (ridge)"] + [pct(fams["ridge_secili"][y]["model"], 0) for y in years])
    yy.append(["Eşit ağırlıklı"] + [pct(fams["ridge_secili"][y]["esit"], 0) for y in years])
    yy.append(["S&P 500"] + [pct(fams["ridge_secili"][y]["spy"], 0) for y in years])

    prof = pd.DataFrame(tes["profil"])
    pcols = [c for c in prof.columns if c not in ("yil", "grup")]
    pg = prof.groupby("grup")[pcols].mean()
    prof_tab = [H(["Özellik", "Geliştirme 2011–2022", "Test 2023–2025"])] + \
               [[Paragraph(lab(c), st.cell), f"{pg.at['geliştirme', c]:.0f}", f"{pg.at['test', c]:.0f}"] for c in pcols]
    mk = pd.DataFrame(tes["piyasa"])
    mk_tab = [H(["Yıl", "S&P 500", "Küçük şirketler (IWM)", "Eşit ağırlıklı evren", "Medyan hisse"])] + \
             [[str(int(r.yil)), pct(r.spy, 0), pct(r.iwm, 0), pct(r.esit_agirlik, 0), pct(r.medyan, 0)] for r in mk.itertuples()]
    ic = pd.DataFrame(tes["ic_ozet"])
    ic = ic[(ic.pozitif_yil + ic.negatif_yil) >= 8].copy()
    ic["guc"] = ic.istikrar.abs()
    ic = ic.sort_values("guc", ascending=False)
    ic_tab = [H(["İşaret", "Yön", "Doğru yön (yıl)", "Ort. IC", "IC 2011–2022", "IC 2023–2025", "İstikrar"])]
    for r in ic.itertuples():
        up = r.ort_ic > 0
        ic_tab.append([Paragraph(lab(r.isaret), st.cell), "yüksek iyi" if up else "yüksek kötü",
                       f"{r.pozitif_yil if up else r.negatif_yil}/{r.pozitif_yil + r.negatif_yil}", f"{r.ort_ic:+.3f}",
                       f"{r.gelistirme_ic:+.3f}", f"{r.test_ic:+.3f}", f"{abs(r.istikrar):.2f}"])
    sig_tab = [H(["Modelde kullanılan işaret", "Yön"])] + [[Paragraph(lab(f), st.cell), "yüksek olan iyi" if v > 0 else "yüksek olan kötü"]
                                                         for f, v in spec["isaretler"].items()]
    pk_tab = [H(["#", "Sembol", "Şirket", "Fiyat $"])] + [[str(r.sira), Paragraph(str(r.sembol), st.cellb),
                                                          Paragraph(str(r.sirket)[:60], st.cell), f"{r.fiyat:.2f}"] for r in picks.itertuples()]
    yb = spec["yil_basi"]

    story = [
        Paragraph("Rapor 3 — Neden başarısız olduk, hangi işaretler işe yarıyor, sağlam model", st.h1),
        Paragraph(
            "<b>Özet.</b> Sürüm 2 (asimetrik model) geliştirme yıllarında çok iyi görünüp 2023–2025'te çöktü: yılın en iyi %10'unu "
            "hedeflemek fiilen en oynak, en küçük hisseleri seçtirdi ve aynı 12 yıl üzerinde ~60 deneme modeli o yılların "
            "tesadüflerine uydurdu. 15 yılın verisinde istikrarlı çalışan işaretler belirlendi ve <b>iç içe test</b> uygulandı: her test "
            "yılı için işaret seçimi, yönleri ve model yalnızca o yıldan önceki verilerle belirlendi. Bu yöntemle 2014–2025'in 12 yılının "
            "tamamı modelin görmediği veridir. Sonuç: istikrarlı işaretler + ridge modeli eşit ağırlıklı piyasayı 12 yılın "
            f"{(np.array([v['model'] for v in fams['ridge_secili'].values()]) > np.array([v['esit'] for v in fams['ridge_secili'].values()])).sum()}"
            "'inde geçti, düşüş yıllarında kaybı çok sınırlı tuttu; S&amp;P 500 ile ortalamada başa baş. Bu model sürüm 3 olarak "
            "donduruldu; canlı takip başladı.", st.box),
        Paragraph("1. Sürüm 2 neden başarısız oldu?", st.h2),
        Paragraph("Seçilen 20 hissenin evren içindeki ortalama yüzdeliği (50 = ortalama). Test yıllarında model daha küçük, çok daha oynak "
                  "ve gözden düşmüş sektörlerdeki hisselere kaydı:", st.body), Spacer(1, 3),
        _table(st, prof_tab, [x * cm for x in (9, 4, 4)]), Spacer(1, 6),
        Paragraph("Piyasa yapısı: 2023–2025'te S&amp;P 500'ü dev şirketler taşıdı; küçük şirketler ve eşit ağırlıklı evren belirgin geride kaldı. "
                  "Küçük/oynak hisseye yönelen bir model bu dönemde kaybetmek zorundaydı.", st.body), Spacer(1, 3),
        _table(st, mk_tab, [x * cm for x in (1.5, 2.5, 4, 4, 3)]),
        PageBreak(), Paragraph("2. Hangi işaretler doğru hisseleri bulmaya yardım ediyor? (2011–2025, her yıl ayrı)", st.h2),
        Paragraph("IC: yıl başı değer ile sonraki 1 yıl getirisi arasındaki sıra korelasyonu (yatırılabilir faaliyet şirketleri). "
                  "Doğru yön: işaretin ortalama yönünde çalıştığı yıl sayısı. İstikrar: ortalama / standart sapma (yüksek = her yıl benzer). "
                  "Hiçbir işaret kesin değildir; en güçlüleri bile tek tek hisselerde sık yanılır, ancak yüzlerce hisse ve yıllar boyunca "
                  "olasılığı tutarlı biçimde kaydırır.", st.small), Spacer(1, 3),
        _table(st, ic_tab, [x * cm for x in (9, 2.6, 2.6, 2.0, 2.4, 2.4, 1.8)]),
        PageBreak(), Paragraph("3. İç içe test: görmediği veriyle eğit, görmediği veriyle test et (2014–2025)", st.h2),
        Paragraph("Her yıl Y için yalnızca Y'den önceki yıllarla: (1) istikrarlı işaretler seçildi (yıllarının ≥ %70'inde aynı yön ve "
                  "ortalama/sapma ≥ 0,5 — kural önceden sabitlendi), (2) puan hesaplandı, (3) yıl başında ilk 20 hisse eşit ağırlıkla alındı, "
                  "alım-satım maliyeti düşüldü, 52 hafta sonra ölçüldü. Borsadan çıkanlar çıkış değeriyle, iflaslar 0 ile.", st.body), Spacer(1, 3),
        _table(st, res_tab, [x * cm for x in (7, 2.6, 2.6, 3.4, 2.6, 2.8, 3.0)]), Spacer(1, 6),
        Paragraph("Yıl yıl (dondurulan model):", st.h3), _table(st, yy, [2.6 * cm] + [1.6 * cm] * len(years)), Spacer(1, 4),
        Paragraph("Not: tabloda en iyi görünen yöntemi sonuçlara bakarak seçmek de küçük bir seçim yanlılığıdır; sistemin her yıl kendi kendine "
                  "yaptığı seçimin sonucu 'otomatik seçim süreci' satırıdır.", st.small),
        PageBreak(), Paragraph(f"4. Dondurulan model — sürüm 3 ({spec['dondurulma']}, kod {spec['kod']})", st.h2),
        Paragraph("Kurallar değiştirilmeyecek; her değişiklik yeni sürüm demektir. İşaretler ve yönleri 2011–"
                  f"{spec['kurallar']['ic_yillari'][1]} verisinden aynı kuralla seçildi:", st.body), Spacer(1, 3),
        _table(st, sig_tab, [x * cm for x in (11, 4)]), Spacer(1, 6),
        Paragraph(f"2026 yıl başı seçimleri, bugüne kadar: model {pct(yb['model'], 1)}, eşit ağırlıklı evren {pct(yb['evren'], 1)}, "
                  f"S&amp;P 500 {pct(yb['spy'], 1)} (yıl bitmedi; kesin değil).", st.body),
        Paragraph(", ".join(f"<b>{s}</b> {pct(g, 0) if g is not None else '(çıktı)'}" for s, g in zip(yb["secim"], yb["getiri"])), st.small),
        Spacer(1, 6), Paragraph(f"Bugünkü seçimler ({spec['dondurulma']}) — canlı takibin başlangıcı", st.h3),
        Paragraph("Yatırım tavsiyesi değildir. Her hafta yeni seçimler kaydedilip gerçekleşen sonuçla karşılaştırılacak; modelin "
                  "gerçek başarısı geçmişe uydurulamayan bu takiple ölçülecek.", st.small), _table(st, pk_tab, [x * cm for x in (0.8, 2, 11, 2)]),
        Paragraph("5. Sınırlamalar ve sonraki adım", st.h2),
        Paragraph("• Model yılın en büyük kazananlarını yakalamıyor (20 hisseden ortalama ~1'i yılın en iyi %10'unda); bunu hedeflemek geçmişte "
                  "piyango bileti etkisi yarattı.<br/>• S&amp;P 500'ü güvenilir şekilde geçmiyor (dev şirketlerin taşıdığı yıllarda geride). "
                  "Bu hedef ayrı bir dalda (claude/sp500-hedefi) aynı iç içe yöntemle çalışılacak.<br/>• Aylık ve haftalık vadeler ile geriye bakış "
                  "analizinin ay ay / hafta hafta sürümleri planda.", st.body),
    ]
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.3 * cm, title="Rapor 3")
    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    main()

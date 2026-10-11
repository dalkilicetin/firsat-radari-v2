"""Tüm belirtiler tek raporda: python -m radar.research.all_indicators

Şimdiye kadarki çalışmaların (Rapor 2 geriye bakış, Rapor 3 teşhis/IC, iç içe test, Rapor 5 büyük kazanan belirtileri)
bulgularını işaret başına tek satırda birleştirir; yeni hesap yapmaz, kayıtlı sonuçları okur.
Girdiler: reports/research/teshis.json, nested.json, belirtiler.json, reports/geriye_bakis/yillik_sinyal_ozeti.csv
Çıktı: reports/research/6_tum_belirtiler.pdf
"""

from __future__ import annotations

import json

import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.research.library import CACHE, GROUPS
from radar.weekly import labels
from radar.weekly.pdf import Styles, _table

R = config.ROOT / "reports" / "research"
OUT = R / "6_tum_belirtiler.pdf"
ROAD = {"piyasa": "Fiyat", "baglam": "Fiyat / sektör", "road1": "İş modeli", "road1_text": "İş modeli (10-K metni)",
        "road2": "Haber / ilgi", "road3": "Kurumsal / olay", "road4": "Tema"}
SIDE = {1: "çok düşük", 2: "düşük", 3: "orta", 4: "yüksek", 5: "çok yüksek"}
TAGS = {"net": "Büyük kazanan belirtisi", "secici": "Riskli hisseler içinde seçici", "ort": "Ortalamayı geçme belirtisi",
        "uyari": "Uyarı (ortalamanın altı)", "havuz": "Havuz belirtisi (oynaklık)", "zayif": "Zayıf / tutarsız"}


def lab(f: str) -> str:
    return labels.signal(f)


def load() -> pd.DataFrame:
    road_of = {}
    for g in GROUPS:
        meta = CACHE / f"{g}.json"
        if meta.exists():
            for s in json.loads(meta.read_text())["signals"]:
                road_of[s] = ROAD[g]
    road_of.setdefault("fiyat_seviyesi", "Fiyat")
    road_of.setdefault("getiri_1a", "Fiyat")
    t = json.loads((R / "teshis.json").read_text())
    ic = pd.DataFrame(t["ic_ozet"]).set_index("isaret")
    b = json.loads((R / "belirtiler.json").read_text())
    q = pd.DataFrame(b["dilim"]).set_index("isaret")
    v = pd.DataFrame(b["oynak"]).set_index("isaret")
    e = pd.DataFrame(b["olay"]).set_index("isaret")
    n = json.loads((R / "nested.json").read_text())
    sel: dict[str, int] = {}
    for y in n["yillar"]:
        for s in y["isaretler"].split(", "):
            sel[s[1:]] = sel.get(s[1:], 0) + 1
    names = sorted(set(ic.index) | set(q.index) | set(e.index))
    rows = []
    for s in names:
        r = {"isaret": s, "yol": road_of.get(s, "—"), "secim": sel.get(s, 0), "secim_yil": len(n["yillar"])}
        if s in ic.index:
            r.update(ic_ort=ic.at[s, "ort_ic"], ic_poz=int(ic.at[s, "pozitif_yil"]), ic_neg=int(ic.at[s, "negatif_yil"]),
                     istikrar=ic.at[s, "istikrar"])
        if s in q.index:
            k = int(q.at[s, "en_iyi_dilim"])
            r.update(dilim=k, kw=q.at[s, f"K{k}"], kl=q.at[s, f"L{k}"], dilim_tut=q.at[s, "tutarlilik"])
            best = None  # net ayırıcı: kazanan katı ≥ 1,15 ve kazanan/kaybeden ≥ 1,3
            for j in range(1, 6):
                kw, kl = q.at[s, f"K{j}"], q.at[s, f"L{j}"]
                if pd.notna(kw) and pd.notna(kl) and kl > 0 and kw >= 1.15 and kw / kl >= 1.3 and (best is None or kw / kl > best[3]):
                    best = (j, kw, kl, kw / kl)
            if best:
                r.update(net_dilim=best[0], net_kw=best[1], net_kl=best[2])
        elif s in e.index:
            r.update(dilim=None, kw=e.at[s, "kazanan_kat"], kl=e.at[s, "kaybeden_kat"], dilim_tut=e.at[s, "tutarlilik"], olay=True)
        if s in v.index:
            r.update(oynak_fark=v.at[s, "fark"], oynak_tut=v.at[s, "tutarlilik"], oynak_ok=bool(v.at[s, "tutarli_yil"] >= 0.75 * v.at[s, "yil"]))
        rows.append(r)
    df = pd.DataFrame(rows)
    df["etiket"] = df.apply(tags, axis=1)
    return df


def tags(r) -> list[str]:
    t = []
    if pd.notna(r.get("net_kw")):
        t.append("net")
    if pd.notna(r.get("oynak_fark")) and bool(r.get("oynak_ok")) and abs(r["oynak_fark"]) >= 5:
        t.append("secici")
    if pd.notna(r.get("istikrar")) and r["istikrar"] >= 0.5:
        t.append("ort")
    if pd.notna(r.get("istikrar")) and r["istikrar"] <= -0.5:
        t.append("uyari")
    if pd.notna(r.get("kw")) and pd.notna(r.get("kl")) and r["kw"] >= 1.3 and r["kl"] >= r["kw"]:
        t.append("havuz")
    return t or ["zayif"]


def main() -> None:
    st = Styles()
    df = load()
    H = lambda cells: [Paragraph(c, st.hdr) for c in cells]
    f2 = lambda x: "—" if pd.isna(x) else f"{x:.2f}"
    P = lambda x, s=None: Paragraph(x, s or st.cell)

    def main_row(r):
        if pd.notna(r.get("dilim")):
            dil = f"{SIDE[int(r.dilim)]}: {f2(r.kw)} / {f2(r.kl)}"
        elif r.get("olay") is True:
            dil = f"olay varken: {f2(r.kw)} / {f2(r.kl)}"
        else:
            dil = "—"
        ic = "—" if pd.isna(r.get("ic_ort")) else f"{r.ic_ort:+.3f} ({int(r.ic_poz)}+ / {int(r.ic_neg)}−)"
        oy = "—" if pd.isna(r.get("oynak_fark")) else f"{r.oynak_fark:+.0f} ({r.oynak_tut})"
        return [P(lab(r.isaret)), P(r.yol), ic, P(dil), oy, f"{r.secim}/{r.secim_yil}", P(", ".join(TAGS[x] for x in r.etiket))]

    order = ["Fiyat", "Fiyat / sektör", "İş modeli", "İş modeli (10-K metni)", "Kurumsal / olay", "Haber / ilgi", "Tema"]
    df["_o"] = df.yol.map({k: i for i, k in enumerate(order)}).fillna(99)
    m_tab = [H(["İşaret", "Yol", "Genel getiri IC ort. (yıl + / −)", "En güçlü dilim: büyük kazanan / kaybeden katı",
                "Oynak grupta fark (yıl)", "İç içe testte seçildiği yıl", "Hüküm"])]
    m_tab += [main_row(r) for _, r in df.sort_values(["_o", "isaret"]).iterrows()]

    has = lambda t: df[df.etiket.map(lambda x: t in x)]
    net = has("net").sort_values("net_kw", ascending=False)
    n_tab = [H(["İşaret", "Yol", "Dilim", "Büyük kazanan katı", "Büyük kaybeden katı", "Oran"])] + \
            [[P(lab(r.isaret)), P(r.yol), SIDE[int(r.net_dilim)], f2(r.net_kw), f2(r.net_kl), f2(r.net_kw / r.net_kl)]
             for _, r in net.iterrows()]
    sec = has("secici").sort_values("oynak_fark", key=abs, ascending=False)
    s_tab = [H(["İşaret", "Yol", "Kazananlarda daha …", "Fark (yüzdelik puan)", "Aynı yönde yıl"])] + \
            [[P(lab(r.isaret)), P(r.yol), "yüksek" if r.oynak_fark > 0 else "düşük", f"{r.oynak_fark:+.0f}", r.oynak_tut]
             for _, r in sec.iterrows()]
    ort = has("ort").sort_values("istikrar", ascending=False)
    o_tab = [H(["İşaret", "Yol", "Ort. IC", "Pozitif yıl", "İstikrar (ort/std)", "İç içe seçim"])] + \
            [[P(lab(r.isaret)), P(r.yol), f"{r.ic_ort:+.3f}", f"{int(r.ic_poz)}/{int(r.ic_poz + r.ic_neg)}", f2(r.istikrar),
              f"{r.secim}/{r.secim_yil}"] for _, r in ort.iterrows()]
    uy = has("uyari").sort_values("istikrar")
    u_tab = [H(["İşaret", "Yol", "Ort. IC", "Negatif yıl", "İstikrar", "Büyük kazanan / kaybeden katı"])] + \
            [[P(lab(r.isaret)), P(r.yol), f"{r.ic_ort:+.3f}", f"{int(r.ic_neg)}/{int(r.ic_poz + r.ic_neg)}", f2(r.istikrar),
              f"{f2(r.kw)} / {f2(r.kl)}"] for _, r in uy.iterrows()]
    hv = has("havuz").sort_values("kl", ascending=False)
    h_tab = [H(["İşaret", "Yol", "Dilim / olay", "Büyük kazanan katı", "Büyük kaybeden katı"])] + \
             [[P(lab(r.isaret)), P(r.yol), SIDE[int(r.dilim)] if pd.notna(r.get("dilim")) else "olay varken", f2(r.kw), f2(r.kl)]
              for _, r in hv.iterrows()]
    zy = has("zayif")

    ic_y = pd.DataFrame(json.loads((R / "nested.json").read_text())["ic"]).set_index("isaret")
    top = list(ort.isaret) + list(uy.isaret)
    years = [c for c in ic_y.columns if c.isdigit()]
    y_tab = [H(["İşaret"] + [c[2:] for c in years])]
    for s in top:
        if s in ic_y.index:
            y_tab.append([P(lab(s))] + [("—" if pd.isna(ic_y.at[s, c]) else f"{ic_y.at[s, c] * 100:+.0f}") for c in years])

    rules = json.loads((R / "belirtiler.json").read_text())["kurallar"]
    r_tab = [H(["Kural (yüzdelik eşikleri)", "Hisse-yıl", "Büyük kazanan oranı", "Kazanan katı", "Kaybeden katı", "Yıl"])]
    for r in rules:
        cond = " ve ".join(f"{lab(f)} {op} {th * 100:.0f}" for f, op, th in r["kural"])
        r_tab.append([P(cond), f"{r['hisse_yil']:,}", f"%{r['kazanan_orani'] * 100:.1f}", f2(r["kat"]), f2(r["kaybeden_kat"]),
                      r["tutarlilik"]])

    cnt = {k: len(has(k)) for k in TAGS}
    story = [
        Paragraph("Belirtiler Raporu — şimdiye kadar bulunan tüm belirtiler", st.h1),
        Paragraph(f"Bu rapor {len(df)} işaretin tamamını tek yerde toplar: Rapor 2 (geriye bakış), Rapor 3 (teşhis: işaretlerin yıl yıl "
                  "getiriyle ilişkisi), iç içe test (her yıl yalnızca geçmişe bakarak seçilen işaretler) ve Rapor 5 (her yılın en çok "
                  "yükselen %5'ini ayıran belirtiler). Dönem 2010/2011–2025; evren alınabilir faaliyet şirketleri (Nasdaq + NYSE + NYSE "
                  "American, ≥ 5 $, ≥ 1 mn $/gün; banka, sigorta, GYO, fon, SPAC hariç). Bütün işaretler yalnızca yıl başında bilinen "
                  "değerlerdir.", st.box), Spacer(1, 4),
        Paragraph("İki farklı amaç, iki farklı belirti seti", st.h2),
        Paragraph("<b>1) Ortalamayı geçmek</b> (piyasadan iyi 20 hisse): istikrarlı, sakin, ucuz, nakit üreten, zirveye yakın şirketler. "
                  "Sürüm 3 modeli bunu yapıyor (2014–2025 ort. +%15,3/yıl) ama yılın en iyi 20'sinden hiçbirini yakalamadı. "
                  "<b>2) Yılın büyük kazananlarını yakalamak</b> (asıl hedef): büyük kazananlar oynak, küçük, düşük fiyatlı hisse havuzundan "
                  "çıkıyor — ama büyük kaybedenler de. Bu yüzden 2. amaç için iki adım gerekir: önce havuz, sonra havuz içinde doğru "
                  "olanı seçen belirtiler.", st.body),
        Paragraph("Hüküm türleri", st.h2),
        Paragraph(f"• <b>{TAGS['net']}</b> ({cnt['net']}): bir dilimde büyük kazanan olasılığı artıyor, büyük kaybeden olasılığı "
                  "artmıyor (kazanan katı ≥ 1,15 ve kazanan/kaybeden ≥ 1,3).<br/>"
                  f"• <b>{TAGS['secici']}</b> ({cnt['secici']}): oynaklığı en yüksek %40'ta kazananlar ile kaybedenlerin yıl başı "
                  "yüzdeliği ≥ 5 puan farklı ve yılların ≥ %75'inde aynı yönde.<br/>"
                  f"• <b>{TAGS['ort']}</b> ({cnt['ort']}): yıl başı değeri ile sonraki 1 yıl getirisi arasındaki sıra korelasyonu (IC) "
                  "istikrarlı pozitif (ort/std ≥ 0,5).<br/>"
                  f"• <b>{TAGS['uyari']}</b> ({cnt['uyari']}): IC istikrarlı negatif — ortalamada kötü sonuç.<br/>"
                  f"• <b>{TAGS['havuz']}</b> ({cnt['havuz']}): büyük kazanan katı ≥ 1,3 ama aynı yerde büyük kaybeden katı daha yüksek "
                  "— büyük hareketin habercisi, yönün değil.<br/>"
                  f"• <b>{TAGS['zayif']}</b> ({cnt['zayif']}): yukarıdakilerin hiçbiri.<br/>"
                  "Bir işaret birden çok hüküm alabilir (ör. küçük şirket: hem havuz hem uyarı).", st.body),
        Paragraph("Neye bakmalıyız — kontrol listesi", st.h2),
        Paragraph("<b>Adım 1 – Havuz:</b> oynak, küçük, düşük fiyatlı, kârı piyasa değerine göre düşük hisseler (büyük kazananların "
                  "çoğu buradan; sığ ağaç kuralında bu havuzda büyük kazanan oranı %14, genel %5).<br/>"
                  "<b>Adım 2 – Havuz içinde seç:</b> son 12 ay güçlü fiyat (momentum), 52 haftalık zirveye yakın, son 6 ay güçlü, "
                  "Ar-Ge orta-yüksek (aşırı değil), haber sayısı artıyor ve ton iyileşiyor, içeriden alım tutarı yüksek, 10-K iş tanımı "
                  "geçen yıla benzer (iş modeli istikrarlı).<br/>"
                  "<b>Adım 3 – Ele:</b> denetçi süreklilik şüphesi, kayıtsız hisse satışı (sulandırma), 52 haftalık dibe yakın, çok "
                  "düşük fiyat + yükselmeyen fiyat.<br/>"
                  "<b>Sektör:</b> tek başına belirti değil — her yıl başka sektör öne çıktı (2012 madencilik/inşaat, 2016 madencilik, "
                  "2020 biyoteknoloji/yazılım, 2025 madencilik); sektörün son 1 yıllık gücü zayıf bir yardımcı.", st.body),
        PageBreak(), Paragraph("1. Ana tablo — her işaret tek satırda", st.h2),
        Paragraph("IC: yıl başı değer ile sonraki 52 hafta getirisinin sıra korelasyonu (+0,05 bu alanda güçlüdür). Dilim: işaretin en "
                  "güçlü %20'lik dilimi; katlar o dilimde büyük kazanan (en iyi %5) / büyük kaybeden (en kötü %5) olma olasılığının genel "
                  "olasılığa oranı. Oynak grupta fark: oynaklığı en yüksek %40'ta kazananların ortalama yüzdeliği eksi kaybedenlerinki. "
                  "İç içe seçim: 2014–2025'te o yıl yalnızca geçmiş yıllara bakılarak kaç kez seçildi. Not: 'Düşük fiyat oynaklığı — çok düşük' "
                  "= en oynak hisseler.", st.small), Spacer(1, 3),
        _table(st, m_tab, [x * cm for x in (6.2, 2.8, 3.3, 4.6, 2.6, 2.2, 5.3)]),
        PageBreak(), Paragraph(f"2. {TAGS['net']} — asıl hedef için", st.h2),
        Paragraph("Bu dilimdeki hisselerin büyük kazanan olma olasılığı artıyor, büyük kaybeden olma olasılığı artmıyor. Hepsi 2010–2025'in "
                  "tamamına bakılarak bulundu; modele girmeden önce iç içe testle doğrulanacak.", st.small), Spacer(1, 3),
        _table(st, n_tab, [x * cm for x in (8, 3.6, 2.4, 3, 3, 2)]),
        Paragraph(f"3. {TAGS['secici']}", st.h2),
        Paragraph("Büyük kazananların ve kaybedenlerin çoğunun çıktığı oynak grupta, ikisini yıl başında ayıran işaretler.", st.small),
        Spacer(1, 3), _table(st, s_tab, [x * cm for x in (8, 3.6, 3.2, 3.2, 2.8)]),
        PageBreak(), Paragraph(f"4. {TAGS['ort']}", st.h2),
        Paragraph("Geniş evrende ortalamanın üstünde getiri ile istikrarlı ilişkili işaretler (Sürüm 3 modelinin dayanağı). Büyük "
                  "kazananları değil, ortalamayı geçen hisseleri bulurlar.", st.small), Spacer(1, 3),
        _table(st, o_tab, [x * cm for x in (8, 3.6, 2.2, 2.4, 2.8, 2.6)]),
        Paragraph(f"5. {TAGS['uyari']}", st.h2),
        Paragraph("IC istikrarlı negatif. Dikkat: bazıları (içeriden alım kümesi, küçük şirket) büyük kazanan katı da 1'in üstünde — yani "
                  "ortalamada kötü, ama nadiren büyük kazandırıyor. Denetçi şüphesi ve sulandırmada kaybeden katı çok daha yüksek: elenmeli.",
                  st.small), Spacer(1, 3),
        _table(st, u_tab, [x * cm for x in (8, 3.6, 2.2, 2.4, 2.2, 4)]),
        PageBreak(), Paragraph("6. Yıl yıl IC (×100) — istikrarlı işaretler", st.h2),
        Paragraph("Her hücre o yılın IC'si ×100. Ortalamayı geçme ve uyarı belirtilerinin yıllar boyunca ne kadar tutarlı olduğunu gösterir.",
                  st.small), Spacer(1, 3),
        _table(st, y_tab, [7.2 * cm] + [1.25 * cm] * len(years)),
        PageBreak(), Paragraph(f"7. {TAGS['havuz']}", st.h2),
        Paragraph("Büyük hareketin habercisi: hem büyük kazanan hem büyük kaybeden olasılığı artıyor. Tek başına seçim yaptırmaz, havuzu "
                  "tanımlar (Adım 1).", st.small), Spacer(1, 3),
        _table(st, h_tab, [x * cm for x in (8, 3.6, 3, 3, 3)]),
        Paragraph("8. Birlikte çalışan işaretler — sığ karar ağacı kuralları (Rapor 5)", st.h2),
        _table(st, r_tab, [x * cm for x in (12, 2, 2.6, 2.2, 2.2, 2)]),
        PageBreak(), Paragraph(f"9. {TAGS['zayif']}", st.h2),
        Paragraph(", ".join(lab(s) for s in zy.isaret) + ".", st.body),
        Paragraph("10. Haberler (2. ve 4. yol) — durum", st.h2),
        Paragraph("Şimdiye kadarki haber işaretleri (GDELT haber sayısı, ton, Wikipedia ilgisi, tema rüzgârı) genel getiride tutarsız; "
                  "ama büyük kazanan tarafında iki net belirti verdiler: haber sayısının artışı (yüksek dilim: kazanan 1,53 kat, "
                  "kaybeden 0,73 kat) ve haber tonunun iyileşmesi (çok yüksek dilim: 1,41 / 1,00). Haber verisi 2015 sonrasını kapsadığı "
                  "için yıl sayısı azdır (6–10 yıl). Şirket × haber konusu verisi (GDELT konuları, NYSE dahil) yeniden yükleniyor; "
                  "geldiğinde konu bazlı işaretler (ör. 'yapay zekâ', 'FDA onayı', 'sözleşme' haberlerindeki artış) bu rapora eklenecek.", st.body),
        Paragraph("11. Henüz bakılamayan belirtiler", st.h2),
        Paragraph("• Sosyal medya (Reddit, X, TikTok, Instagram): veri erişimi gerekiyor (Reddit anahtarı kullanıcıda).<br/>"
                  "• Patent başvuruları: PatentsView anahtarı bekleniyor.<br/>"
                  "• Açığa satış oranı, analist tahmin revizyonları, opsiyon akışı: ücretsiz geçmiş veri yok.<br/>"
                  "• Ay ay ve hafta hafta belirtiler: yıllık çalışma onaylanınca yapılacak (açık liste #10).", st.body),
    ]
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.3 * cm, rightMargin=1.3 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.3 * cm, title="Belirtiler Raporu")
    doc.build(story)
    print(OUT, cnt)


if __name__ == "__main__":
    main()

"""Belirti araştırması: yılın büyük kazananlarını yıl başında ne ayırt ediyordu? python -m radar.research.indicators

Büyük kazanan = o yıl alınabilir faaliyet şirketleri içinde 1 yıl getirisi en yüksek %5 (her yıl ~120 hisse).
Büyük kaybeden = en düşük %5. Tüm işaretler yalnızca yıl başında bilinen değerlerdir.

Bölümler:
1. Dilim analizi: her işaret 5 dilime bölünür; her dilimde büyük kazanan / kaybeden olma olasılığı ÷ genel olasılık (kat).
   Yıl tutarlılığı: en güçlü dilimin katı kaç yılda > 1.
2. Oynak hisseler içinde kazanan ile kaybedeni ayıranlar (oynaklığı en yüksek %40).
3. Olaylar (0/1): olay varken kazanan / kaybeden olma katı.
4. Sektörler: yıl yıl büyük kazananların sektör dağılımı ve sektör katı.
5. Birlikte çalışan işaretler: sığ karar ağacı (derinlik 3) — kurallar, katlar ve yıl tutarlılığı.
6. Her yılın en iyi 5 hissesinin yıl başı profili.
Çıktı: reports/research/5_belirtiler_raporu.pdf ve reports/research/belirtiler.json
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.research import hindsight as hs
from radar.weekly import labels
from radar.weekly.pdf import Styles, _table, pct

OUT = config.ROOT / "reports" / "research" / "5_belirtiler_raporu.pdf"
JSON = config.ROOT / "reports" / "research" / "belirtiler.json"
FRAME = config.ROOT / "data" / "derived" / "belirti_cercevesi.parquet"
YEARS = range(2010, 2026)
WIN = 0.05


def lab(f: str) -> str:
    return labels.signal(f)


def build_frame(p, sigs, inv, sector) -> tuple[pd.DataFrame, list[str], set[str]]:
    """Yıl × hisse satırları: yüzdelikler (yatırılabilir evren içinde), olay bayrakları, getiri, sınıf."""
    from radar.research import panel
    price, sec, dates = p["price"], p["securities"], p["price"].index
    fwd = panel.forward_returns(price, sec, 52).reindex(dates)
    events = {n for n, df in sigs.items() if hs.is_event(df)}
    rows = []
    for y in YEARS:
        t = int(np.flatnonzero(dates >= pd.Timestamp(f"{y}-01-01"))[0])
        u = inv.iloc[t]
        r = fwd.iloc[t][u].dropna()
        q = r.rank(pct=True)
        f = pd.DataFrame({"yil": y, "getiri": r, "kazanan": (q > 1 - WIN).astype(int), "kaybeden": (q <= WIN).astype(int),
                          "sektor": sector.reindex(r.index)})
        for n, df in sigs.items():
            v = df.iloc[t].reindex(r.index)
            f[n] = (v.fillna(0) > 0).astype(float) if n in events else v.rank(pct=True)
        rows.append(f)
    return pd.concat(rows), [n for n in sigs if n not in events], events


def quintile_table(df: pd.DataFrame, cont: list[str]) -> pd.DataFrame:
    rows = []
    pw, pl = df.kazanan.mean(), df.kaybeden.mean()
    for n in cont:
        x = df[[n, "kazanan", "kaybeden", "yil"]].dropna()
        if len(x) < 5000:
            continue
        x["q"] = np.minimum((x[n] * 5).astype(int), 4) + 1
        g = x.groupby("q")
        w = g.kazanan.mean() / pw
        l = g.kaybeden.mean() / pl
        best_q = int(w.idxmax())
        yearly = x[x.q == best_q].groupby("yil").kazanan.mean() / x.groupby("yil").kazanan.mean()
        rows.append({"isaret": n, "kapsam": len(x) / len(df), **{f"K{q}": w.get(q, np.nan) for q in range(1, 6)},
                     **{f"L{q}": l.get(q, np.nan) for q in range(1, 6)}, "en_iyi_dilim": best_q,
                     "en_iyi_kat": float(w.max()), "tutarlilik": f"{int((yearly > 1).sum())}/{len(yearly)}",
                     "tutarli_yil": int((yearly > 1).sum()), "yil": len(yearly)})
    return pd.DataFrame(rows).sort_values("en_iyi_kat", ascending=False)


def volatile_table(df: pd.DataFrame, cont: list[str]) -> pd.DataFrame:
    """Oynaklığı en yüksek %40 içinde: kazananların ve kaybedenlerin ortalama yüzdeliği."""
    v = df[df["dusuk_oynaklik"] <= 0.4]  # dusuk_oynaklik yüksek = düşük oynaklık → ≤ 0,4 en oynak %40
    rows = []
    for n in cont:
        if n == "dusuk_oynaklik":
            continue
        x = v[[n, "kazanan", "kaybeden", "yil"]].dropna()
        if x.kazanan.sum() < 100 or x.kaybeden.sum() < 100:
            continue
        mw, ml = x[x.kazanan == 1][n].mean(), x[x.kaybeden == 1][n].mean()
        yw = x[x.kazanan == 1].groupby("yil")[n].mean()
        yl = x[x.kaybeden == 1].groupby("yil")[n].mean()
        common = yw.index.intersection(yl.index)
        same = int((np.sign(yw[common] - yl[common]) == np.sign(mw - ml)).sum())
        rows.append({"isaret": n, "kazanan_ort": mw * 100, "kaybeden_ort": ml * 100, "fark": (mw - ml) * 100,
                     "tutarlilik": f"{same}/{len(common)}", "tutarli_yil": same, "yil": len(common)})
    return pd.DataFrame(rows).sort_values("fark", key=abs, ascending=False)


def event_table(df: pd.DataFrame, events: set[str]) -> pd.DataFrame:
    pw, pl = df.kazanan.mean(), df.kaybeden.mean()
    rows = []
    for n in events:
        has = df[n] > 0
        if has.sum() < 200:
            continue
        yearly = df[has].groupby("yil").kazanan.mean() / df.groupby("yil").kazanan.mean()
        rows.append({"isaret": n, "kapsam": float(has.mean()), "kazanan_kat": df[has].kazanan.mean() / pw,
                     "kaybeden_kat": df[has].kaybeden.mean() / pl, "tutarlilik": f"{int((yearly > 1).sum())}/{len(yearly)}"})
    return pd.DataFrame(rows).sort_values("kazanan_kat", ascending=False)


def sector_table(df: pd.DataFrame) -> pd.DataFrame:
    share_w = df[df.kazanan == 1].groupby(["yil", "sektor"]).size() / df[df.kazanan == 1].groupby("yil").size()
    share_u = df.groupby(["yil", "sektor"]).size() / df.groupby("yil").size()
    return (share_w / share_u).unstack("yil").fillna(0)


def tree_rules(df: pd.DataFrame, cont: list[str]) -> list[dict]:
    from sklearn.tree import DecisionTreeClassifier
    feats = [c for c in cont if df[c].notna().mean() > 0.5]
    X = df[feats].fillna(0.5).to_numpy()
    y = df.kazanan.to_numpy()
    tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=800, class_weight=None, random_state=0).fit(X, y)
    leaves = tree.apply(X)
    base = y.mean()
    t = tree.tree_
    rules = []

    def path(node, conds):
        if t.children_left[node] == -1:
            m = leaves == node
            yearly = df[m].groupby("yil").kazanan.mean() / df.groupby("yil").kazanan.mean()
            rules.append({"kural": conds, "hisse_yil": int(m.sum()), "kazanan_orani": float(y[m].mean()),
                          "kat": float(y[m].mean() / base), "kaybeden_kat": float(df[m].kaybeden.mean() / df.kaybeden.mean()),
                          "tutarlilik": f"{int((yearly.reindex(YEARS).fillna(0) > 1).sum())}/{len(YEARS)}"})
            return
        f, th = feats[t.feature[node]], t.threshold[node]
        path(t.children_left[node], conds + [(f, "≤", th)])
        path(t.children_right[node], conds + [(f, ">", th)])
    path(0, [])
    return sorted(rules, key=lambda r: -r["kat"])


def main() -> None:
    p, sigs, inv, etf, sector = hs.prepare()
    df, cont, events = build_frame(p, sigs, inv, sector)
    FRAME.parent.mkdir(parents=True, exist_ok=True)
    df.assign(sembol=p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol
              .reindex(df.index).to_numpy()).to_parquet(FRAME)  # hedef arama motoru (target_search) bunu okur
    (FRAME.parent / "belirti_cercevesi_olaylar.json").write_text(json.dumps(sorted(events), ensure_ascii=False))
    qt, vt, et, stb, rules = quintile_table(df, cont), volatile_table(df, cont), event_table(df, events), sector_table(df), tree_rules(df, cont)
    JSON.write_text(json.dumps({"dilim": qt.round(3).to_dict(orient="records"), "oynak": vt.round(2).to_dict(orient="records"),
                                "olay": et.round(3).to_dict(orient="records"), "kurallar": rules}, ensure_ascii=False, indent=1, default=str))
    # Her yılın en iyi 5'i
    profiles = []
    for y in YEARS:
        top = df[df.yil == y].nlargest(5, "getiri")
        for cik, r in top.iterrows():
            vals = r[cont].dropna().astype(float)
            hi = [n for n in vals.sort_values(ascending=False).index if vals[n] >= 0.9][:5]
            lo = [n for n in vals.sort_values().index if vals[n] <= 0.1][:4]
            ev = [n for n in events if r.get(n, 0) > 0]
            sym = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik").set_index("cik").symbol.get(cik, "?")
            profiles.append({"yil": y, "sembol": sym, "sektor": r.sektor, "getiri": r.getiri, "yuksek": hi, "dusuk": lo, "olay": ev})
    render(df, qt, vt, et, stb, rules, profiles)
    print(OUT)


def render(df, qt, vt, et, stb, rules, profiles) -> None:
    st = Styles()
    H = lambda cells: [Paragraph(c, st.hdr) for c in cells]
    f2 = lambda x: "—" if pd.isna(x) else f"{x:.2f}"
    n_win = int(df.kazanan.sum())

    q_tab = [H(["İşaret", "Dilim 1 (en düşük)", "Dilim 2", "Dilim 3", "Dilim 4", "Dilim 5 (en yüksek)", "En güçlü dilim",
                "Yıl tutarlılığı", "Kaybeden katı (dilim 1 / 5)"])]
    for r in qt.itertuples():
        q_tab.append([Paragraph(lab(r.isaret), st.cell)] + [f2(getattr(r, f"K{q}")) for q in range(1, 6)] +
                     [str(r.en_iyi_dilim), r.tutarlilik, f"{f2(r.L1)} / {f2(r.L5)}"])
    v_tab = [H(["İşaret", "Kazananların ort. yüzdeliği", "Kaybedenlerin ort. yüzdeliği", "Fark", "Yıl tutarlılığı"])] + \
            [[Paragraph(lab(r.isaret), st.cell), f"{r.kazanan_ort:.0f}", f"{r.kaybeden_ort:.0f}", f"{r.fark:+.0f}", r.tutarlilik]
             for r in vt.head(25).itertuples()]
    e_tab = [H(["Olay", "Hisselerin yüzde kaçında", "Kazanan katı", "Kaybeden katı", "Kazanan katı > 1 olan yıl"])] + \
            [[Paragraph(lab(r.isaret), st.cell), f"%{r.kapsam * 100:.1f}", f2(r.kazanan_kat), f2(r.kaybeden_kat), r.tutarlilik]
             for r in et.itertuples()]
    s_rows = stb.loc[stb.max(axis=1).sort_values(ascending=False).index]
    s_tab = [H(["Sektör"] + [str(c) for c in s_rows.columns])] + \
            [[r[0]] + [("<b>" + f"{v:.1f}" + "</b>") if v >= 2 else f"{v:.1f}" for v in r[1:]] for r in s_rows.itertuples()]
    s_tab = [[Paragraph(str(c), st.cell) if i else c for i, c in enumerate(row)] if k else row for k, row in enumerate(s_tab)]
    r_tab = [H(["Kural (yüzdelik eşikleri)", "Hisse-yıl", "Büyük kazanan oranı", "Kazanan katı", "Kaybeden katı", "Kat > 1 olan yıl"])]
    for r in rules:
        cond = " ve ".join(f"{lab(f)} {op} {th * 100:.0f}" for f, op, th in r["kural"])
        r_tab.append([Paragraph(cond, st.cell), f"{r['hisse_yil']:,}", f"%{r['kazanan_orani'] * 100:.1f}", f2(r["kat"]),
                      f2(r["kaybeden_kat"]), r["tutarlilik"]])
    p_tab = [H(["Yıl", "Sembol", "Sektör", "Getiri", "Yıl başında yüksek (≥ 90)", "Yıl başında düşük (≤ 10)", "Olaylar"])]
    for r in profiles:
        p_tab.append([str(r["yil"]), Paragraph(str(r["sembol"]), st.cellb), r["sektor"], pct(r["getiri"], 0),
                      Paragraph(", ".join(lab(x) for x in r["yuksek"]) or "—", st.cell),
                      Paragraph(", ".join(lab(x) for x in r["dusuk"]) or "—", st.cell),
                      Paragraph(", ".join(lab(x) for x in r["olay"][:3]) or "—", st.cell)])

    side_of = {1: "çok düşük", 2: "düşük", 3: "orta", 4: "yüksek", 5: "çok yüksek"}
    net = []  # kazanan katı yüksek, aynı dilimde kaybeden katı düşük: oynaklık değil, gerçek ayırıcı
    for r in qt.itertuples():
        for k in range(1, 6):
            kw, kl = getattr(r, f"K{k}"), getattr(r, f"L{k}")
            if pd.notna(kw) and pd.notna(kl) and kl > 0 and kw >= 1.15 and kw / kl >= 1.3:
                net.append((kw / kl, r.isaret, k, kw, kl))
    net.sort(reverse=True)
    n_tab = [H(["İşaret", "Dilim", "Büyük kazanan katı", "Büyük kaybeden katı", "Oran"])] + \
            [[Paragraph(lab(f), st.cell), side_of[k], f2(kw), f2(kl), f2(ratio)] for ratio, f, k, kw, kl in net]
    top_q = qt[(qt.tutarli_yil >= 12)].head(8)
    findings = ["<b>A) Kazananı da kaybedeni de çok çıkaran işaretler (oynaklık belirtisi — tek başına seçim yaptırmaz):</b>"]
    for r in top_q.itertuples():
        side = {1: "çok düşük", 2: "düşük", 3: "orta", 4: "yüksek", 5: "çok yüksek"}[r.en_iyi_dilim]
        findings.append(f"• <b>{lab(r.isaret)}</b> {side} olan hisselerde büyük kazanan olasılığı {r.en_iyi_kat:.1f} kat "
                        f"({r.tutarlilik} yıl); aynı dilimde kaybeden katı {f2(getattr(r, f'L{r.en_iyi_dilim}'))}.")
    findings.append("<b>B) Oynak hisseler içinde kazananı kaybedenden ayıranlar (yüzdelik 0–100):</b>")
    vt_c = vt[vt.tutarli_yil >= 0.75 * vt.yil].head(6)
    for r in vt_c.itertuples():
        findings.append(f"• Oynak hisseler içinde: kazananlarda <b>{lab(r.isaret)}</b> ortalama {r.kazanan_ort:.0f}, kaybedenlerde "
                        f"{r.kaybeden_ort:.0f} ({r.tutarlilik} yıl aynı yönde).")

    story = [
        Paragraph("Rapor 5 — Belirtiler: yılın büyük kazananlarını yıl başında ne ayırt ediyordu?", st.h1),
        Paragraph(f"<b>Tanım.</b> Her yıl (2010–2025) alınabilir faaliyet şirketleri arasında 1 yıl getirisi en yüksek %5 = <b>büyük kazanan</b> "
                  f"(toplam {n_win:,} hisse-yıl), en düşük %5 = <b>büyük kaybeden</b>. Bütün işaretler yalnızca yıl başında bilinen değerlerdir. "
                  "<b>Kat</b> = o grupta büyük kazanan olma olasılığı ÷ genel olasılık (1,0 = etkisiz; 2,0 = iki kat olası). "
                  "<b>Yıl tutarlılığı</b> = katın 1'in üstünde olduğu yıl sayısı. Haber konuları (GDELT, NYSE dahil) yükleniyor; geldiğinde bu "
                  "rapora ayrı bölüm olarak eklenecek. <b>Önemli:</b> büyük kazananlar ile büyük kaybedenler çoğu işarette benzer görünür "
                  "(ikisi de oynak, küçük, gözden düşmüş hisselerden çıkar); asıl belirtiler B ve C'dekilerdir.", st.box),
        Paragraph("Öne çıkan bulgular", st.h2),
        Paragraph("<br/>".join(findings) or "—", st.body),
        PageBreak(), Paragraph("<b>C) Net ayırıcılar</b> — bu dilimde büyük kazanan olasılığı artıyor, büyük kaybeden olasılığı artmıyor:", st.body),
        _table(st, n_tab, [x * cm for x in (8, 2.4, 3.2, 3.2, 2)]), Spacer(1, 3),
        PageBreak(), Paragraph("1. Dilim analizi — her işaretin 5 diliminde büyük kazanan olma katı", st.h2),
        Paragraph("Dilim 1 = işaretin en düşük %20'si, dilim 5 = en yüksek %20'si. Doğrusal olmayan ilişkileri gösterir (ör. hem çok düşük hem "
                  "çok yüksek değerlerde kazanan çıkması). Son sütun aynı uçlarda büyük kaybeden olma katı.", st.small), Spacer(1, 3),
        _table(st, q_tab, [x * cm for x in (6.8, 2.1, 1.7, 1.7, 1.7, 2.3, 1.8, 2.1, 3.6)]),
        PageBreak(), Paragraph("2. Oynak hisseler içinde kazananı kaybedenden ayıran işaretler", st.h2),
        Paragraph("Oynaklığı en yüksek %40'lık grupta (büyük kazananların ve kaybedenlerin çoğu buradan çıkar): kazananların ve kaybedenlerin "
                  "yıl başındaki ortalama yüzdeliği. Fark büyük ve yıllar boyunca aynı yöndeyse işaret, riskli hisseler arasında doğru olanı seçmeye "
                  "yardım eder.", st.small), Spacer(1, 3), _table(st, v_tab, [x * cm for x in (9, 3.4, 3.4, 2, 2.6)]),
        PageBreak(), Paragraph("3. Olaylar (8-K bildirimleri, yönetici alımları, denetçi uyarısı vb.)", st.h2), Spacer(1, 3),
        _table(st, e_tab, [x * cm for x in (9, 3.2, 2.6, 2.6, 3.6)]),
        Paragraph("4. Sektörler — büyük kazananlar hangi sektörlerden çıktı? (kat: sektörün kazananlar içindeki payı ÷ evrendeki payı; "
                  "kalın ≥ 2)", st.h2), Spacer(1, 3), _table(st, s_tab, [3.4 * cm] + [1.45 * cm] * (len(s_tab[0]) - 1)),
        PageBreak(), Paragraph("5. Birlikte çalışan işaretler — sığ karar ağacı kuralları", st.h2),
        Paragraph("Bütün yıllar birlikte, derinlik 3, her yaprakta en az 800 hisse-yıl. Kurallar keşif amaçlıdır (2010–2025'in tamamı kullanıldı); "
                  "modele girmeden önce iç içe testle (yalnızca geçmiş yıllarla) doğrulanmalıdır.", st.small), Spacer(1, 3),
        _table(st, r_tab, [x * cm for x in (12, 2, 2.6, 2.2, 2.2, 2.4)]),
        PageBreak(), Paragraph("6. Her yılın en iyi 5 hissesi — yıl başında nasıl görünüyorlardı?", st.h2), Spacer(1, 3),
        _table(st, p_tab, [x * cm for x in (1.2, 1.6, 2.8, 1.8, 7.4, 6.4, 4.2)]),
        Paragraph("7. Sonuç ve sonraki adım", st.h2),
        Paragraph("<b>Neye bakmalıyız (kontrol listesi).</b> (1) Ön eleme: oynak, küçük, düşük fiyatlı hisseler — büyük kazananların "
                  "havuzu burası, ama kaybedenler de buradan çıkar. (2) Havuzun içinde: son 12 ayda güçlü fiyat (momentum), 52 haftalık "
                  "zirveye yakın, Ar-Ge harcaması orta-yüksek (aşırı değil), haber akışı hızlanan, haber tonu iyileşen, içeriden alım yapılan "
                  "hisseler. (3) Uzak dur: denetçinin süreklilik şüphesi, kayıtsız hisse satışı (sulandırma), 52 haftalık dibe yakınlık. "
                  "(4) Sektör tek başına belirti değil: her yıl farklı sektör öne çıkıyor.", st.body),
        Paragraph("Bu rapor belirti adaylarını gösterir. Bir sonraki adımda tutarlı adaylar (yıl tutarlılığı yüksek olanlar, oynak hisseler içinde "
                  "kazananı ayıranlar ve tutarlı kurallar) iç içe testle, yani her yıl yalnızca geçmiş yıllara bakarak seçilip görülmemiş yılda "
                  "denenecek; birinci ölçüt seçilen 20 hisseden kaçının o yılın en iyileri arasında olduğu.", st.body),
    ]
    doc = SimpleDocTemplate(str(OUT), pagesize=landscape(A4), leftMargin=1.3 * cm, rightMargin=1.3 * cm, topMargin=1.2 * cm,
                            bottomMargin=1.3 * cm, title="Rapor 5 — Belirtiler")
    doc.build(story)


if __name__ == "__main__":
    main()

"""1 yıl vadesi — kontrol noktası raporu: python -m radar.research.final_1y

Seçilen model (ön kayıtlı iterasyon + doğrulama sonrası): 5 tohumlu LightGBM ortalaması (H3a).
Her yılın ilk Cuma'sında model yalnızca o güne kadarki verilerle eğitilir, ilk 20 hisseyi seçer; 52 hafta sonra kontrol.
Yıl türleri: iterasyon (2013, 2018, 2021), doğrulama (diğer geliştirme yılları), KİLİTLİ (2023–2025; burada ilk ve tek
kez açılır). 2026: yıl başından bugüne. Ayrıca bugünkü (son veri haftası) seçimler.
Çıktı: reports/research/bir_yil_raporu.pdf, reports/research/bir_yil_secimler.csv
"""

from __future__ import annotations

import json
import time

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

from radar import config
from radar.research import context, quick
from radar.research.run_quick import ROUNDS
from radar.weekly.pdf import Styles, _table, pct, tr_date

import sys

# Sürüm 2 (2026-10-11): asimetrik fırsat modeli H8a; iyileştirme yalnızca 2011–2022, test 2023–2025.
V2 = len(sys.argv) > 1 and sys.argv[1] == "v2"
OUT_PDF = config.ROOT / "reports" / "research" / ("bir_yil_raporu_v2.pdf" if V2 else "bir_yil_raporu.pdf")
OUT_CSV = config.ROOT / "reports" / "research" / ("bir_yil_secimler_v2.csv" if V2 else "bir_yil_secimler.csv")
MODEL = ROUNDS["h8"][0] if V2 else ROUNDS["h3"][0]  # H8a asimetrik λ=3,5 + tehlike elemesi | H3a 5 tohum
YEARS = range(2011, 2026)


def kind(y: int) -> str:
    if V2:
        return "TEST (iyileştirmede kullanılmadı)" if y in quick.LOCKED_YEARS else "geliştirme"
    return "iterasyon" if y in quick.ITER_YEARS else "KİLİTLİ (ilk açılış)" if y in quick.LOCKED_YEARS else "doğrulama"


def main() -> None:
    t0 = time.time()
    d = quick.QuickData()
    etf = context.etf_prices(d.dates)
    rows, picks = [], []
    for y in YEARS:
        t = quick.year_start(d.dates, y)
        res = quick.outcome(d, quick.score_at(MODEL, d, t), t)
        spy = float(etf["SPY"].iloc[t + 52] / etf["SPY"].iloc[t] - 1)
        best = {s for s, _ in res["en_iyi20_hisseler"]}
        overlap = [s for s, _ in res["secim"] if s in best]
        rows.append({"yil": y, "tur": kind(y), "tarih": res["tarih"], "model": res["portfoy"], "spy": spy,
                     "evren": res["evren_ort"], "en_iyi20": res["en_iyi20"], "yukselen": res["yukselen"],
                     "medyani_gecen": res["medyani_gecen"], "en_iyi10_icinde": res["en_iyi10_icinde"],
                     "yol_dusus": res["yol_en_buyuk_dusus"], "ortusme": overlap})
        picks += [{"yil": y, "sira": i + 1, "sembol": s, "getiri": g} for i, (s, g) in enumerate(res["secim"])]
        print(y, kind(y), f"model {res['portfoy']:+.1%} SPY {spy:+.1%}", flush=True)
        if y in quick.LOCKED_YEARS:
            quick.log(MODEL, pd.DataFrame([{"yil": y} | res]).set_index("yil"), "test_v2" if V2 else "kilitli_acilis")

    # 2026: yıl başından bugüne; ve bugünkü seçim
    t26, tl = quick.year_start(d.dates, 2026), len(d.dates) - 1
    sc26 = quick.score_at(MODEL, d, t26)
    from radar.research import panel
    p = panel.build()
    price = p["price"].to_numpy()
    ok = np.asarray(d.eval_u[t26]) & np.isfinite(sc26)
    idx = np.flatnonzero(ok)
    top26 = idx[np.argsort(-sc26[idx])][:20]
    ytd = price[tl, top26] / price[t26, top26] - 1
    uni_ytd = np.nanmean(price[tl, idx] / price[t26, idx] - 1)
    spy_ytd = float(etf["SPY"].iloc[tl] / etf["SPY"].iloc[t26] - 1)
    sc_now = quick.score_at(MODEL, d, tl)
    ok_now = np.asarray(d.eval_u[tl]) & np.isfinite(sc_now)
    idn = np.flatnonzero(ok_now)
    top_now = idn[np.argsort(-sc_now[idn])][:20]
    sec = p["securities"].assign(cik=lambda x: x.cik.astype(str)).drop_duplicates("cik").set_index("cik")
    names = sec.name.reindex(p["price"].columns).fillna("").str.replace(r" - .*$", "", regex=True).to_numpy()

    df = pd.DataFrame(rows)
    pd.DataFrame(picks).to_csv(OUT_CSV, index=False)
    render(df, picks, d, (top26, ytd, uni_ytd, spy_ytd, d.dates[t26]), (top_now, d.dates[tl]), names)
    print(f"bitti ({round(time.time() - t0)} sn)")


MODEL_TEXT = (
    "<b>Model (sürüm 2)</b>: asimetrik fırsat puanı = P(yılın en iyi %10'u) − 3,5 × P(yılın en kötü %10'u); iki LightGBM "
    "sınıflandırıcısı, 51 sinyal. Önce yalnızca gerçek tehlike işaretleri elenir (sulandırma, denetçinin süreklilik şüphesi). "
    "<b>Yıl türleri</b>: model 2011–2022 üzerinde iyileştirildi (yaklaşık 60 deneme); <b>2023–2025 iyileştirmede hiç "
    "kullanılmadı ve bu raporda yalnızca test olarak çalıştırıldı</b>." if V2 else
    "<b>Model</b>: 5 farklı tohumla eğitilmiş LightGBM ağaç modellerinin ortalaması; 51 sinyal (finansallar, 10-K metni, "
    "yönetici alımları, 8-K olayları, fon pozisyonları, haber, sektör ETF'leri, kazanç açıklaması tepkisi, fiyat/hacim). "
    "<b>Yıl türleri</b>: iterasyon yılları (2013, 2018, 2021) model seçilirken kullanıldı; doğrulama yılları bir kez "
    "kontrol için kullanıldı; <b>kilitli yıllar (2023–2025) bu raporda ilk ve tek kez açıldı</b> — modelin gerçek sınavı.")


def render(df, picks, d, ytd, now, names) -> None:
    st = Styles()
    pk = pd.DataFrame(picks)
    groups = ({"geliştirme 2011–2022": df.tur == "geliştirme", "TEST 2023–2025": df.tur.str.startswith("TEST")} if V2 else
              {"iterasyon": df.tur == "iterasyon", "doğrulama": df.tur == "doğrulama", "kilitli": df.tur.str.startswith("KİLİTLİ")})
    summ = [["Yıl grubu", "Yıl", "Model ort.", "S&P 500 ort.", "Kârda biten yıl", "S&P'yi geçen yıl", "20 hisseden yükselen (ort.)"]]
    for g, m in list(groups.items()) + [("hepsi", df.tur.notna())]:
        s = df[m]
        summ.append([g, str(len(s)), pct(s.model.mean(), 1), pct(s.spy.mean(), 1), f"{int((s.model > 0).sum())}/{len(s)}",
                     f"{int((s.model > s.spy).sum())}/{len(s)}", f"{s.yukselen.mean():.1f}"])
    story = [
        Paragraph("1 Yıl Vadesi — " + ("Sürüm 2 (asimetrik fırsat modeli)" if V2 else "Kontrol Noktası Raporu"), st.h1),
        Paragraph("Soru: Model her yılın ilk Cuma'sında, yalnızca o güne kadar bilinen verilerle çalıştırılsaydı ve seçtiği 20 hisse "
                  "eşit ağırlıkla alınsaydı, 1 yıl sonra ne olurdu? Alım-satım maliyeti düşüldü; borsadan çıkanlar çıkış değeriyle, "
                  "iflas edenler 0 ile hesaplandı. Evren: Nasdaq + NYSE + NYSE American faaliyet şirketleri (banka, sigorta, GYO, "
                  "fon, SPAC hariç), fiyat ≥ 5 $, günlük işlem ≥ 1 mn $.", st.body),
        Paragraph(MODEL_TEXT, st.box),
        Paragraph("Özet", st.h2), _table(st, summ, [x * cm for x in (3, 1.4, 2.6, 2.8, 3.2, 3.2, 4.4)]), Spacer(1, 6)]
    data = [["Yıl", "Tür", "Model", "S&P 500", "Medyan hisseden iyi", "Yükselen", "Yol boyu en büyük düşüş", "Sonradan bakınca en iyi 20",
             "Modelin seçtiği 'en iyi 20'den"]]
    for _, r in df.iterrows():
        data.append([str(r.yil), r.tur, pct(r.model, 0), pct(r.spy, 0), f"{r.medyani_gecen}/20", f"{r.yukselen}/20",
                     pct(r.yol_dusus, 0), pct(r.en_iyi20, 0), ", ".join(r.ortusme) or "—"])
    story += [Paragraph("Yıl yıl", st.h2), _table(st, data, [x * cm for x in (1.2, 3.6, 1.8, 1.8, 2.8, 1.8, 3.2, 3.4, 5.4)])]
    for _, r in df.iterrows():
        sel = pk[pk.yil == r.yil]
        story += [PageBreak() if r.yil in (2011, 2016, 2021) else Spacer(1, 4),
                  Paragraph(f"{r.yil} ({r.tur}) — {r.tarih}: model {pct(r.model, 0)}, S&amp;P 500 {pct(r.spy, 0)}", st.h3),
                  Paragraph(", ".join(f"<b>{s}</b> {pct(g, 0)}" for s, g in zip(sel.sembol, sel.getiri)), st.small)]
    top26, ytd_r, uni, spy, d26 = ytd
    story += [PageBreak(), Paragraph(f"2026 — {tr_date(d26)} seçimleri, yıl başından bugüne", st.h2),
              Paragraph(f"Model ort. {pct(np.nanmean(ytd_r), 1)}, evren ort. {pct(uni, 1)}, S&amp;P 500 {pct(spy, 1)} "
                        f"(sonuç kesin değil; yıl bitmedi).", st.body),
              Paragraph(", ".join(f"<b>{d.symbols[i]}</b> {pct(g, 0)}" for i, g in zip(top26, ytd_r)), st.small)]
    top_now, dnow = now
    data = [["#", "Sembol", "Şirket"]] + [[str(k + 1), Paragraph(str(d.symbols[i]), st.cellb), Paragraph(names[i][:60], st.cell)]
                                          for k, i in enumerate(top_now)]
    story += [Paragraph(f"Bugünkü seçimler ({tr_date(dnow)}) — önümüzdeki 1 yıl için", st.h2),
              Paragraph("Yatırım tavsiyesi değildir; modelin geçmişte gösterdiği isabet yukarıdaki tablolardadır.", st.small),
              _table(st, data, [x * cm for x in (0.8, 2.0, 10.0)])]
    doc = SimpleDocTemplate(str(OUT_PDF), pagesize=landscape(A4), leftMargin=1.4 * cm, rightMargin=1.4 * cm,
                            topMargin=1.2 * cm, bottomMargin=1.3 * cm, title="1 yıl vadesi raporu")
    doc.build(story)


if __name__ == "__main__":
    main()

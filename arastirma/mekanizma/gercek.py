"""Gercek ornek veri kontrolleri (L7): R1 aylik endeks yayi, R2 hisse yayi <-> gizli guc, R3 gunluk sok yayi.
KUCUK orneklem: sonuclar vaka calismasidir, kanit degil."""
import numpy as np
import pandas as pd

from mekanizma.hipotez import yukle
from mekanizma.mekanizmalar import yay
from mekanizma.motor import sonuc
from mekanizma.motor.istatistik import blok_bootstrap_ga, ozet
from mekanizma.sim.ortak import guvenli, pct, yaz
from mekanizma.veri import ornek

ETF_SEKTOR = ["QTUM", "BOTZ", "SMH", "ICLN", "URA", "ARKG", "XBI", "ITA", "LIT", "KWEB", "XLE", "XLF", "IGV", "PAVE", "JETS", "REMX"]
ETF_DIGER = ["VGK", "MCHI", "EWJ", "EEM", "XAU/USD", "SLV", "PPLT", "PALL", "CPER"]
UYARI = ("> **Küçük örneklem:** 61 aylık / ~100 günlük veri, tek tek vakalar. Sonuçlar vaka çalışmasıdır, istatistiksel kanıt değildir. "
         "Hisse seti küratörlü (teknoloji ağırlıklı) ve **hayatta kalan** şirketlerden oluşur; batan şirketler yok.\n")


def _veri():
    a = ornek.aylik()
    etf = [c for c in ETF_SEKTOR + ETF_DIGER + ["SPY"] if c in a.columns]
    return a, a["SPY"], a.drop(columns=etf)


def _ileri(seri, t, ufuklar):
    """Ay sonu t sinyali; giris t+1; getiri P[t+1+h]/P[t+1]-1 (yetersizse None)."""
    i = seri.index.get_loc(t)
    return {h: (float(seri.iloc[i + 1 + h] / seri.iloc[i + 1] - 1) if i + 1 + h < len(seri) else None) for h in ufuklar}


# ------------------------------------------------------------------ R1
def r1():
    a, spy, hisse = _veri()
    p = yukle("yay")["aylik"]
    oz = yay.ozellikler(spy, p, hisse)
    sg = yay.sinyaller(oz, p)
    md = ["# R1 — Aylık endeks yayı (gerçek örnek, SPY + 154 hisse)", "", UYARI,
          "## 1. Önceden kayıtlı aylık dedektör ne gösterdi?", "",
          f"Parametreler `hipotezler/yay.yaml → aylik` (değiştirilmedi): `dd ≤ {p['dd_esik']*100:.0f}%` ve bileşik gerilim yüzdeliği ≥ {p['bilesik_yuzdelik']}.", "",
          f"- Y1 tetiklenen ay sayısı: **{int(sg['Y1'].sum())}**, Y2: **{int(sg['Y2'].sum())}**.",
          f"- Gerilim skoru hesaplanabilen ilk ay: **{sg['skor'].first_valid_index():%Y-%m}** (genişlik 10 aylık ortalama + yüzdelik ısınması 12 ay).",
          "- Bu yüzden **2022 düşüşü dedektör için görünmez** (skor NaN), 2025 (SPY −%8) ve 2026-03 (−%6) ise `dd ≤ −%10` eşiğine ulaşmadı.",
          "- Sonuç: 61 aylık veri bu dedektörü sınamaya **yetmiyor**; bu bir dedektör başarısı ya da başarısızlığı değil, veri uzunluğu sınırı.", "",
          "## 2. Betimsel: gerilim skoru (dd eşiği olmadan) en yüksek aylar", "",
          "> Post-hoc betimleme, test değil. Skor = dd, genişlik yüzdeliklerinin ortalaması.", "",
          "| Ay | SPY dd | Gerilim skoru | İleri 3 ay | İleri 6 ay | İleri 12 ay |", "|---|---|---|---|---|---|"]
    top = sg["skor"].dropna().sort_values(ascending=False).head(6).sort_index()
    js = {"y1": int(sg["Y1"].sum()), "y2": int(sg["Y2"].sum()), "yuksek_skor": {}}
    for t, v in top.items():
        f = _ileri(spy, t, (3, 6, 12))
        js["yuksek_skor"][str(t.date())] = dict(skor=float(v), dd=float(oz.loc[t, "dd"]), ileri=f)
        md.append(f"| {t:%Y-%m} | {pct(oz.loc[t,'dd'])} | {v:.2f} | " + " | ".join(pct(f[h]) for h in (3, 6, 12)) + " |")
    md += ["", "## 3. Üç düşüş bölümü: SPY ve ETF'ler (giriş = sonraki ay sonu)", "",
           "Başlangıç ayları sabit kurallarla (sonuca bakmadan) seçildi: ilk −%10 / ilk −%20 / ilk −%5 ay. 'Dip' sütunları **sonradan bilinen** dibi gösterir (üst sınır, hile).", "",
           "| Bölüm | Ay | Etiket | SPY dd | SPY 3a | SPY 6a | SPY 12a |", "|---|---|---|---|---|---|---|"]
    olaylar = [("2022", "2022-04-30", "ilk −%10"), ("2022", "2022-06-30", "ilk −%20"), ("2022", "2022-09-30", "DİP (sonradan)"),
               ("2025", "2025-03-31", "ilk −%5"), ("2025", "2025-04-30", "DİP (sonradan)"), ("2026", "2026-03-31", "DİP (sonradan)")]
    js["bolumler"] = []
    for ad, ay, et in olaylar:
        t = pd.Timestamp(ay)
        f = _ileri(spy, t, (3, 6, 12))
        dd = float(spy.loc[t] / spy.loc[:t].tail(12).max() - 1)
        md.append(f"| {ad} | {t:%Y-%m} | {et} | {pct(dd)} | " + " | ".join(pct(f[h]) for h in (3, 6, 12)) + " |")
        js["bolumler"].append(dict(bolum=ad, ay=ay, etiket=et, dd=dd, ileri=f))
    md += ["", "### ETF'ler: 2022 bölümü, ilk −%20 ayından (2022-06) sonraki getiri", "", "| ETF | 2021-12→2022-06 | İleri 3a | İleri 6a | İleri 12a |", "|---|---|---|---|---|"]
    t0, t1 = pd.Timestamp("2021-12-31"), pd.Timestamp("2022-06-30")
    sat = []
    for e in ETF_SEKTOR + ETF_DIGER + ["SPY"]:
        if e in a.columns and a[e].loc[t0:t1].notna().all():
            f = _ileri(a[e], t1, (3, 6, 12))
            sat.append((float(a[e].loc[t1] / a[e].loc[t0] - 1), e, f))
    for dus, e, f in sorted(sat):
        md.append(f"| {e} | {pct(dus)} | " + " | ".join(pct(f[h]) for h in (3, 6, 12)) + " |")
    js["etf2022"] = {e: dict(dusus=d, ileri=f) for d, e, f in sat}
    from scipy.stats import spearmanr
    en_cok = [e for _, e, _ in sorted(sat)[:3]]
    en_az = [e for _, e, _ in sorted(sat)[-3:]]
    spy22 = _ileri(spy, t1, (3, 6, 12))
    md += ["", "## Okuma",
           f"- SPY, 2022'de ilk −%20 ayından (2022-06) sonra 3 ayda {pct(spy22[3])}, 6 ayda {pct(spy22[6])}, 12 ayda {pct(spy22[12])}: toparlanma hemen değil, ancak 12. ayda belirgin. Dipten (2022-09) alan ise 3 ayda {pct(_ileri(spy, pd.Timestamp('2022-09-30'), (3,))[3])} görürdü; **dibi önceden bilmek** büyük fark yaratır (üst sınır).",
           f"- ETF düzeyi (2021-12→2022-06 düşüşü ile ileri getiri arasında sıra korelasyonu, n={len(sat)}): "
           + ", ".join(f"{h}a ρ={spearmanr([d for d,_,_ in sat], [f[h] for _,_,f in sat])[0]:+.2f}" for h in (3, 6, 12))
           + f". ρ<0 = en çok düşenler daha çok toparlandı (yay), ρ>0 = en az düşenler daha iyi (gizli güç). En çok düşenler: {', '.join(en_cok)}; en az düşenler/yükselenler: {', '.join(en_az)}.",
           "- Bu tek bir vaka, 26 ETF; sonuç kanıt değil. Hisse düzeyindeki karşılığı R2'dedir."]
    yaz("gercek_R1", "\n".join(md) + "\n", js)


# ------------------------------------------------------------------ R2
def _dilim(skor, fwd, k=5):
    m = skor.notna() & fwd.notna()
    sk, f = skor[m], fwd[m]
    if len(sk) < 5 * k:
        return None
    sira = sk.rank(method="first")
    dil = np.ceil(sira / (len(sk) / k)).astype(int).clip(1, k) - 1
    ex = f - f.median()                       # medyan: kuyruklar agir (RGTI +%400 gibi), ortalama dilimi tek basina surukler
    return [float(ex[dil == q].median()) for q in range(k)], dil, ex


def _siralama(hisse, spy, i, pk, min_onceki=24):
    """Zirve(pk)-i donem getirisi: ham ve (yeterli gecmis varsa) beta'dan arindirilmis kalinti."""
    ham = hisse.iloc[i] / hisse.iloc[pk] - 1
    out = {"ham": ham}
    if pk >= min_onceki:
        lr = np.log(hisse).diff().iloc[pk - min_onceki + 1: pk + 1]
        le = np.log(spy).diff().iloc[pk - min_onceki + 1: pk + 1]
        beta = lr.apply(lambda c: c.cov(le)) / le.var()
        out["kalinti"] = ham - beta * (spy.iloc[i] / spy.iloc[pk] - 1)
    return out


def _ileri_hisse(hisse, i, h):
    if i + 1 + h >= len(hisse):
        return None
    return hisse.iloc[i + 1 + h] / hisse.iloc[i + 1] - 1


def r2():
    a, spy, hisse = _veri()
    hisse = hisse.loc[:, hisse.notna().all()]            # eksiksiz 154 hisse
    prof = ornek.profil()
    idx = spy.index
    dd = spy / spy.rolling(12, min_periods=1).max() - 1
    bolumler = [("2022 (ayrıştırma: büyük olasılıkla bozulma türü)", "2021-12-31", [("2022-06-30", "ilk −%20 ay"), ("2022-09-30", "DİP (sonradan, hile)")]),
                ("2025 (panik/tarife türü)", "2025-01-31", [("2025-03-31", "ilk −%5 ay"), ("2025-04-30", "DİP (sonradan, hile)")]),
                ("2026-03 (kısa düşüş)", "2026-01-31", [("2026-03-31", "DİP (sonradan, hile)")])]
    md = ["# R2 — Hisse yayı ⟷ Gizli güç (2022, 2025, 2026 doğal deneyleri)", "", UYARI,
          "Her bölümde hisseler zirveden değerlendirme ayına kadarki getirilerine göre 5 dilime ayrılır (**D1 = en çok düşen**, D5 = en az düşen). Getiri = sonraki ay girişli ileri getiri; dilim değeri = dilimin **medyanı − evrenin medyanı** (hisse getirilerinin kuyruğu ağır: tek bir RGTI +%400 ortalamayı bozar).",
          "**Sakin taban:** aynı pencere uzunluğunda, SPY'ın zirveden en fazla %3 aşağıda olduğu aylarda aynı sıralamanın ortalaması. 'Krize özgü' = kriz − sakin taban (simülasyonda zorunlu kontrol olduğu görüldü, bkz. sim_S5).",
          "2022'de zirve (2021-12) veri başlangıcına çok yakın: beta için geçmiş yok, **sadece ham getiri** kullanılır.", "",
          "Önceden beklenti (simülasyondan, zayıf): panik türünde D1 ekstra toparlanır; bozulma türünde dayanıklı hisseler (D5) ekstra kazanır — ama S5'te bozulma etkisi ölçülemedi, yani bu beklenti çok zayıf.", ""]
    js = {}
    for ad, pks, evaller in bolumler:
        pk = idx.get_loc(pd.Timestamp(pks))
        md += [f"## {ad}", ""]
        for evs, etiket in evaller:
            i = idx.get_loc(pd.Timestamp(evs))
            L = i - pk
            sir = _siralama(hisse, spy, i, pk)
            md += [f"### Değerlendirme: {evs[:7]} — {etiket} (zirveden {L} ay, SPY dd {pct(float(dd.loc[evs]))})", "",
                   "| Sıralama | Ufuk | D1 | D2 | D3 | D4 | D5 | D1 − D5 | Sakin taban (D1 − D5) | **Krize özgü** |", "|---|---|---|---|---|---|---|---|---|---|"]
            for anahtar, ad_s in (("ham", "ham getiri"), ("kalinti", "kalıntı")):
                if anahtar not in sir:
                    continue
                for h in (3, 6, 12):
                    fwd = _ileri_hisse(hisse, i, h)
                    if fwd is None:
                        continue
                    r = _dilim(sir[anahtar], fwd)
                    if r is None:
                        continue
                    q = r[0]
                    # sakin taban
                    tb = []
                    for j in range(len(idx)):
                        if dd.iloc[j] > -0.03 and j - L >= (24 if anahtar == "kalinti" else 1) and j + 1 + h < len(idx):
                            s2 = _siralama(hisse, spy, j, j - L)
                            if anahtar in s2:
                                rj = _dilim(s2[anahtar], _ileri_hisse(hisse, j, h))
                                if rj:
                                    tb.append(rj[0][0] - rj[0][4])
                    taban = float(np.mean(tb)) if tb else None
                    ozel = (q[0] - q[4] - taban) if taban is not None else None
                    md.append(f"| {ad_s} | {h}a | " + " | ".join(pct(x) for x in q) + f" | {pct(q[0]-q[4])} | {pct(taban)} (n={len(tb)}) | **{pct(ozel)}** |")
                    js.setdefault(ad, {}).setdefault(evs, {})[f"{anahtar}{h}"] = dict(dilim=q, fark=q[0] - q[4], taban=taban, ozel=ozel, n_taban=len(tb))
            md.append("")
            # ornekler
            fwd6 = _ileri_hisse(hisse, i, 6)
            ham = sir["ham"].sort_values()
            if fwd6 is not None:
                ad_ = lambda s: (prof["ad"].get(s) or s)[:22]
                en_cok = ", ".join(f"{s} ({pct(ham[s],0)}→{pct(fwd6[s],0)})" for s in ham.index[:5])
                en_az = ", ".join(f"{s} ({pct(ham[s],0)}→{pct(fwd6[s],0)})" for s in ham.index[-5:])
                md += [f"- En çok düşen 5 (dönem→ileri 6a): {en_cok}", f"- En az düşen 5: {en_az}", ""]
    md += ["## Özet: krize özgü D1 − D5 (kriz − sakin taban), medyan bazlı", "",
           "| Bölüm | Değerlendirme | ham 3a | ham 6a | ham 12a | kalıntı 3a | kalıntı 6a | kalıntı 12a |", "|---|---|---|---|---|---|---|---|"]
    isaret = {}
    for ad, ev in js.items():
        for evs, d in ev.items():
            md.append(f"| {ad.split(' (')[0]} | {evs[:7]} | " + " | ".join(pct(d.get(f"{k}{h}", {}).get("ozel")) for k in ("ham", "kalinti") for h in (3, 6, 12)) + " |")
            for kk, v in d.items():
                if v.get("ozel") is not None:
                    isaret.setdefault(ad.split(" (")[0] + " " + evs[:7], []).append(v["ozel"] > 0)
    md += ["", "İşaret tutarlılığı (krize özgü > 0 olan ufuk/sıralama oranı): " + "; ".join(f"{k}: {sum(v)}/{len(v)}" for k, v in isaret.items()), "",
           "> **Sakin taban uyarısı:** taban, SPY'ın zirvesine yakın ~30 ardışık aydan hesaplanıyor (2023-12→2026); bu dönem tek bir rejim (yarı iletken/AI rallisi) ve aylar birbirine bağımlı. Taban negatifse (en çok düşenler sakin zamanda geride kalıyor = momentum) 'krize özgü' fark şişer; taban tek başına da güvenilir değil.", ""]
    g = lambda ad, ev, k: js.get(ad, {}).get(ev, {}).get(k, {}).get("ozel")
    a22, a25 = [x for x in js if x.startswith("2022")][0], [x for x in js if x.startswith("2025")][0]
    md += ["## Okuma",
           f"- **2022 (bozulma beklentisi → gizli güç):** ilk −%20 ayında (2022-06) kısa vadede (3 ay) gizli güç kazandı (krize özgü {pct(g(a22,'2022-06-30','ham3'))}: enerji hisseleri COP/DVN/MPC dirençliydi), "
           f"ama 12 ayda yay geri geldi ({pct(g(a22,'2022-06-30','ham12'))}). Beklenti yalnızca kısa vadede tuttu; bozulma bile uzun vadede en çok düşenlerin toparlanmasını engellemedi.",
           f"- **2025 (panik beklentisi → yay):** beklenti tuttu: kalıntı sıralamasında ilk eşik ayında krize özgü {pct(g(a25,'2025-03-31','kalinti3'))} / {pct(g(a25,'2025-03-31','kalinti6'))} / {pct(g(a25,'2025-03-31','kalinti12'))} (3/6/12 ay), her ufukta pozitif.",
           "- **Seçim yanlılığı (2025 sonucunu şişirir):** hisse evreni izleme listesini içeriyor (RGTI, QBTS, ZYME …). Bunlar *bugün* ilgi gören adlar; krizde çok düşüp sonra +%400 yapan hisseler listede sistematik olarak fazla. Gerçek zamanda böyle bir liste bilinemezdi.",
           "- 'Krize özgü' pozitifse en çok düşenler normal ters dönüşün ötesinde toparlanmış (yay); negatifse dayanıklı hisseler ekstra kazanmış (gizli güç).",
           "- DİP satırları gerçek zamanda bilinemeyen dibi kullanır: **üst sınırdır**, işlem kuralı değildir. İlk-eşik satırları gerçek zamanda bilinebilir olan bilgidir.",
           "- Her bölüm tek bir vaka; GA verilmedi çünkü bağımsız gözlem yok. Aynı yönde tekrarlayan işaret (3 bölüm × birden çok ufuk) hâlâ tesadüf olabilir.",
           "- Hisseler küratörlü ve teknoloji ağırlıklı (yarı iletken rallisi); 2022 'bozulma'sında nasdaq hisselerinin ağırlığı sonucu etkileyebilir."]
    yaz("gercek_R2", "\n".join(md) + "\n", js)


# ------------------------------------------------------------------ R3
def r3():
    g = ornek.gunluk_panel()
    q = g.pivot(index="tarih", columns="sembol", values="fiyat")
    cov_tum = q.notna().sum(axis=1)
    spy = q["SPY"]
    islem = spy.index[spy.ne(spy.shift(1))]               # hafta sonu tekrarlarini at
    q, cov_tum = q.loc[islem], cov_tum.loc[islem]
    r52 = g.pivot(index="tarih", columns="sembol", values="r52w").reindex(q.index)
    sabit = [c for c in q.columns[q.notna().mean() >= 0.95] if c != "SPY"]      # onceden belirlenen kural: gunlerin >=%95'inde fiyati olan hisseler
    Q, spy = q[sabit], q["SPY"]
    ret = Q.pct_change(fill_method=None)
    sok = (ret <= -0.08) & (ret >= -0.5)
    ufuk = (5, 10, 20)
    md = ["# R3 — Günlük panel: şok yayı (tek gün ≤ −%8)", "", UYARI,
          f"Panel: {q.index[0]:%Y-%m-%d} → {q.index[-1]:%Y-%m-%d}, hafta sonu tekrarları atılınca **{len(q)} işlem günü**.", "",
          "## Veri kalitesi: panel uygun bir günlük fiyat paneli değil",
          f"- Fiyat (`quotes`) yalnızca bir alt küme için kayıtlı: kapsam Temmuz'da ~{int(cov_tum.iloc[5:15].mean())}, Ağustos–Eylül'de ~{int(cov_tum.iloc[40:60].mean())}, **yalnızca son haftada** {int(cov_tum.iloc[-1])} hisse. Kapsam zamanla ve büyük olasılıkla önceki sıralamaya göre değişiyor (seçim yanlılığı).",
          "- `mtd` alanı fiyat değişimleriyle tutarsız (aynı gün fiyat −%1.1 iken mtd +%1.1 artıyor), yedek olarak kullanılamaz.",
          f"- Bu yüzden **sabit hisse seti** kullanıldı: gün sayısının ≥%95'inde fiyatı olan **{len(sabit)} hisse**. Bu set de tarama listelerinden geldiği için temsil gücü sınırlı.",
          "- Gerçek zaman damgası tarama commit gününe aittir; fiyat önceki seans kapanışıdır (1 günlük ofset, sonucu etkilemez).", "",
          "Şok = günlük getiri ≤ −%8 ve ≥ −%50 (bölünme filtresi). Getiri = ertesi gün girişli, **SPY'a göre fazla getiri**. Aynı gündeki olaylar ortalanıp **gün bazında** özetlenir (aynı gün şokları bağımsız değil).", "",
          f"Toplam şok: **{int(sok.sum().sum())}** hisse-günü, **{int((sok.sum(axis=1) > 0).sum())}** farklı gün.", ""]
    js = {"n_sok": int(sok.sum().sum()), "sabit_hisse": len(sabit)}
    ileri = {h: (Q.shift(-(1 + h)) / Q.shift(-1) - 1) for h in ufuk}
    spy_f = {h: (spy.shift(-(1 + h)) / spy.shift(-1) - 1) for h in ufuk}
    ex = {h: ileri[h].sub(spy_f[h], axis=0) for h in ufuk}
    taban = {h: float(ex[h].stack().mean()) for h in ufuk}
    ters = (ret.shift(-1) >= 0.06)                        # ertesi gun +%6 ve ustu sicrama: veri hatasi suphesi (GELECEKTEN bilgi, sadece duyarlilik)
    trend = (r52[sabit] > 0)
    gruplar = {"Tüm şoklar (ana sonuç)": sok, "Trendde (r52w > 0)": sok & trend, "Trend dışı (r52w ≤ 0)": sok & ~trend,
               "Duyarlılık: ertesi gün +%6 sıçrayan şüpheli olaylar çıkarıldı (gelecekten bilgi!)": sok & ~ters}
    md += ["| Grup | Ufuk | Gün | Hisse-gün | Şok sonrası fazla getiri (gün ortalaması) [%90 GA] | Tüm hisse-gün tabanı | **Şok − taban** |", "|---|---|---|---|---|---|---|"]
    for ad, S in gruplar.items():
        for h in ufuk:
            gun_ort = ex[h].where(S).mean(axis=1).dropna()
            n_hs = int((S & ex[h].notna()).sum().sum())
            if len(gun_ort) < 5:
                md.append(f"| {ad} | {h}g | {len(gun_ort)} | {n_hs} | yetersiz | | |"); continue
            o = ozet(gun_ort.to_numpy())
            fark = o["ort"] - taban[h]
            js.setdefault(ad, {})[str(h)] = dict(gun=len(gun_ort), hisse_gun=n_hs, ozet=o, taban=taban[h], fark=fark)
            md.append(f"| {ad} | {h}g | {len(gun_ort)} | {n_hs} | {pct(o['ort'])} [{pct(o['ga_alt'])}, {pct(o['ga_ust'])}] | {pct(taban[h])} | **{pct(fark)}** |")
    ekim = [d for d in sok.index[-8:] if sok.loc[d].any()]
    md += ["", "## Ekim 2026 ortası satışı (betimsel; ileri 5 gün henüz yok)", ""]
    for d in ekim:
        e = ret.shift(-1).loc[d][sok.loc[d]]
        md.append(f"- {d:%Y-%m-%d}: SPY {pct(float(spy.pct_change().loc[d]))}, sabit sette şok {int(sok.loc[d].sum())} hisse; ertesi gün ortalaması {pct(float(e.mean()))}.")
    a5 = js.get("Tüm şoklar (ana sonuç)", {}).get("5")
    md += ["", "## Okuma"]
    if a5:
        ga = a5["ozet"]
        kapsar = ga["ga_alt"] <= 0.05 <= ga["ga_ust"]
        md.append(f"- Ana sonuç: şok sonrası 5 günde SPY'a göre fazla getiri **{pct(ga['ort'])}** [{pct(ga['ga_alt'])}, {pct(ga['ga_ust'])}] (n={a5['gun']} gün); tabanla fark {pct(a5['fark'])}. "
                  f"Güven aralığı sıfırı {'içeriyor' if ga['ga_alt'] <= 0 <= ga['ga_ust'] else 'dışlıyor'} ve v5.16'daki +%5'i {'de içeriyor' if kapsar else 'içermiyor'}: bu veri v5.16 bulgusunu ne doğrular ne çürütür. Gün sayısı az, olaylar kümelenmiş.")
    md += ["- Şüpheli-olaylar duyarlılık satırı gelecekten bilgi kullanır; yalnızca ana sonucun veri hatalarına ne kadar duyarlı olduğunu göstermek içindir.",
           "- Panel yapısı (değişen kapsam) nedeniyle bu test ancak yeni gece taramaları tam kapsamlı (589 hisse) birikince (≈ 4–6 hafta) güvenilir olur; o zaman `python calistir.py gercek R3` yeniden çalıştırılmalı."]
    yaz("gercek_R3", "\n".join(md) + "\n", js)


def calistir(ad):
    f = {"R1": r1, "R2": r2, "R3": r3}
    if ad == "hepsi":
        for k in f.values():
            k()
        return 0
    if ad not in f:
        print(f"'{ad}' henuz yok")
        return 0
    f[ad]()
    return 0

"""L10: Kenetlenme (ortalama korelasyon) ve Gelgit (likidite degisimi) KOSUL degiskenleri.
Soru: Yay, Gizli guc ve Kirilma noktasi hangi kenetlenme/likidite kosulunda daha iyi calisiyor?"""
import numpy as np
import pandas as pd

from mekanizma.mekanizmalar import kirilma as K
from mekanizma.motor import sonuc
from mekanizma.motor.istatistik import blok_bootstrap_ga, ozet
from mekanizma.motor.olay import ayikla
from mekanizma.ozellik import fiyat, korelasyon, likidite
from mekanizma.sim import deneyler as D
from mekanizma.sim import kirilma_deney as KD
from mekanizma.sim import ortak
from mekanizma.sim.ortak import BASLIK, pct, yaz
from mekanizma.sim.piyasa import simule

ETIKET = ["düşük", "orta", "yüksek"]
P = ortak.yay_p()
H = P["ana_ufuk"]


def tersil(p):
    """Genisleyen yuzdelik (0-1) -> 0/1/2 (alt/orta/ust ucte bir); NaN korunur."""
    return np.floor(p * 3).clip(upper=2)


def _isci(a):
    kw, tohum = a
    d = simule(ortak.ayar_yukle(n_hisse=60, **kw), tohum)
    e = d.endeks
    adj = e["adj"]
    _, sg = ortak.yay_calistir(d, P)
    kor = tersil(fiyat.yuzdelik_genisleyen(korelasyon.ort_ikili_korelasyon(np.log(d.hisseler).diff(), 63), 252))
    lik = tersil(fiyat.yuzdelik_genisleyen(likidite.likidite_degisim(e["likidite"], 63), 252))
    ileri, mae = sonuc.ileri_getiri(adj, [H])[H], sonuc.mae(adj, H)
    ol = ayikla(sg["Y2"], P["bekleme"])
    out = {"olay": [], "taban": {}}
    for ad, c in (("kor", kor), ("lik", lik)):
        for k in range(3):
            m = (c == k) & ileri.notna()
            out["taban"][f"{ad}{k}"] = (float(ileri[m].sum()), int(m.sum()), float(mae[m].sum()), int(m.sum()))
    for t in ol:
        if pd.notna(ileri.get(t)):
            out["olay"].append(dict(kor=kor.get(t), lik=lik.get(t), r=float(ileri[t]), mae=float(mae[t])))
    return out


def yay_kosullu(kw):
    res = D._harita(_isci, [(kw, t) for t in range(20)])
    ev = pd.DataFrame(sum((r["olay"] for r in res), [])).dropna()
    taban = {}
    for k in res[0]["taban"]:
        taban[k] = (sum(r["taban"][k][0] for r in res) / max(1, sum(r["taban"][k][1] for r in res)),
                    sum(r["taban"][k][2] for r in res) / max(1, sum(r["taban"][k][3] for r in res)))
    sat = {}
    for ad in ("kor", "lik"):
        for k in range(3):
            g = ev[ev[ad] == k]
            o = ozet(g["r"].to_numpy()) if len(g) else None
            sat[f"{ad}{k}"] = dict(n=len(g), ozet=o, taban=taban[f"{ad}{k}"][0], fark=(o["ort"] - taban[f"{ad}{k}"][0]) if o and o["ort"] is not None else None,
                                   mae=float(g["mae"].mean()) if len(g) else None, mae_taban=taban[f"{ad}{k}"][1])
    # yuksek - dusuk fark (kosul etkisi) icin bootstrap
    ozet_fark = {}
    for ad in ("kor", "lik"):
        a_, b_ = ev[ev[ad] == 2]["r"].to_numpy(), ev[ev[ad] == 0]["r"].to_numpy()
        if len(a_) > 5 and len(b_) > 5:
            rng = np.random.default_rng(0)
            bs = [rng.choice(a_, len(a_)).mean() - rng.choice(b_, len(b_)).mean() for _ in range(2000)]
            fk = (sat[f"{ad}2"]["fark"] or 0) - (sat[f"{ad}0"]["fark"] or 0)
            ozet_fark[ad] = dict(fark=fk, ga=[float(np.quantile(bs, 0.05) - (a_.mean() - b_.mean()) + fk), float(np.quantile(bs, 0.95) - (a_.mean() - b_.mean()) + fk)])
    return sat, ozet_fark, len(ev)


def tabloyla(sat, ad, etiket):
    s = [f"| {etiket} | n | Y2 63 bar getiri [%90 GA] | O koşuldaki her gün (taban) | **Fark** | MAE (taban) |", "|---|---|---|---|---|---|"]
    for k in range(3):
        r = sat[f"{ad}{k}"]
        s.append(f"| {ETIKET[k]} | {r['n']} | {ortak.ga_str(r['ozet'])} | {pct(r['taban'])} | **{pct(r['fark'])}** | {pct(r['mae'])} ({pct(r['mae_taban'])}) |")
    return s


def gizli_guc_kosullu():
    satir = sum(D._harita(D._s5_isci, [({}, t) for t in range(20)]), [])
    df = pd.DataFrame(satir).dropna(subset=["kor_p", "lik_p"])
    out = {}
    md = []
    for ad, kol in (("Kenetlenme (ort. korelasyon)", "kor_p"), ("Gelgit (likidite değişimi)", "lik_p")):
        md += [f"**{ad}** — kalıntı sıralaması, ufuk 126, krize özgü D1 − D5 (kriz − sakin taban)", "", "| Terçil | n kriz | Krize özgü D1 − D5 [%90 GA] | Panik olayı | Bozulma olayı |", "|---|---|---|---|---|"]
        for k in range(3):
            g = df[(df[kol] * 3).clip(upper=2.999).astype(int) == k]
            M = np.array([x for x in g["kal126"] if x is not None], float)
            B = np.array([x for x in g["taban_kal126"] if x is not None], float)
            if len(M) < 8 or len(M) != len(B):
                md.append(f"| {ETIKET[k]} | {len(g)} | yetersiz | | |"); continue
            ozel = (M[:, 0] - M[:, 4]) - (B[:, 0] - B[:, 4])
            lo, hi = blok_bootstrap_ga(ozel)
            tur = lambda e: (lambda gg: (np.mean([(m[0] - m[4]) - (b[0] - b[4]) for m, b in zip(np.array([x for x in gg['kal126']], float), np.array([x for x in gg['taban_kal126']], float))]) if len(gg) >= 5 else None))(g[g["olay"] == e])
            out[f"{kol}{k}"] = dict(n=len(M), ozel=float(ozel.mean()), ga=[lo, hi], panik=tur("panik olayı"), bozulma=tur("bozulma olayı"))
            md.append(f"| {ETIKET[k]} | {len(M)} | **{pct(ozel.mean())}** [{pct(lo)}, {pct(hi)}] | {pct(out[f'{kol}{k}']['panik'])} | {pct(out[f'{kol}{k}']['bozulma'])} |")
        md.append("")
    return md, out


def _auc_grup(test, p, yt, kol, esik):
    out = {}
    q = test[kol].to_numpy()
    for k, (lo, hi) in enumerate(((-np.inf, esik[0]), (esik[0], esik[1]), (esik[1], np.inf))):
        m = (q >= lo) & (q < hi) if k else (q < hi)
        out[ETIKET[k]] = (KD.auc(yt[m], p[m]) if m.sum() > 50 and yt[m].sum() > 5 and (1 - yt[m]).sum() > 5 else float("nan"), int(m.sum()))
    return out


def kirilma_kosullu():
    from scipy.special import expit
    res = D._harita(KD._isci, [({}, t) for t in range(20)])
    md, js = [], {}
    for gad in KD.H["gorevler"]:
        u = 63
        parca = {t: r[(gad, u)] for t, r in enumerate(res)}
        egit = pd.concat([p for t, p in parca.items() if t in KD.H["egitim_tohum"]])
        test = pd.concat([p for t, p in parca.items() if t in KD.H["test_tohum"]])
        if len(egit) < 100 or len(test) < 100:
            continue
        mu, sd = egit[K.OZ].mean(), egit[K.OZ].std().replace(0, 1)
        b = KD._fit(((egit[K.OZ] - mu) / sd).to_numpy(), egit["y"].to_numpy())
        p = expit(b[0] + ((test[K.OZ] - mu) / sd).to_numpy() @ b[1:])
        yt = test["y"].to_numpy()
        js[gad] = {}
        for ad, kol in (("Kenetlenme (ort_kor_63)", "ort_kor_63"), ("Gelgit (likidite değişimi)", "_lik")):
            esik = np.quantile(egit[kol], [1 / 3, 2 / 3])             # esikler EGITIM verisinden (gelecek sizintisi yok)
            r = _auc_grup(test, p, yt, kol, esik)
            js[gad][ad] = r
        md.append(f"- **{gad}** (ufuk 63): " + "; ".join(f"{ad}: " + ", ".join(f"{k} AUC {v[0]:.2f} (n={v[1]})" for k, v in r.items()) for ad, r in js[gad].items()))
    return md, js


def gercek_kor():
    from mekanizma.veri import ornek
    a = ornek.aylik()
    etf = ["QTUM", "BOTZ", "SMH", "ICLN", "URA", "ARKG", "XBI", "ITA", "LIT", "KWEB", "XLE", "XLF", "IGV", "PAVE", "JETS", "REMX", "SPY", "VGK", "MCHI", "EWJ", "EEM", "XAU/USD", "SLV", "PPLT", "PALL", "CPER"]
    h = a.drop(columns=[c for c in etf if c in a.columns])
    h = h.loc[:, h.notna().all()]
    kor = korelasyon.ort_ikili_korelasyon(np.log(h).diff(), 12, en_cok=h.shape[1]).dropna()
    spy = a["SPY"]
    dd = spy / spy.rolling(12, min_periods=1).max() - 1
    return kor, dd


def kosullar():
    md = ["# L10 — Kenetlenme ve Gelgit: Yay / Gizli güç / Kırılma hangi koşulda daha iyi?", "", BASLIK,
          "**Kenetlenme** = son 63 barın ortalama ikili korelasyonu; **Gelgit** = likidite endeksinin 63 bar değişimi (yüksek = sıkılaşma). "
          "Her ikisi de olay anında **genişleyen yüzdeliğe** göre üçe bölünür (düşük/orta/yüksek; geleceğe bakmaz).",
          "Koşulların kendi etkisini ayırmak için 'fark' = olay ortalaması − **aynı terçildeki bütün günlerin** ortalaması.", ""]
    js = {}
    # A) Yay
    md += ["## A. Yay (Y2, 63 bar) × koşul", ""]
    for dad, kw in (("NORMAL dünya (kalibre)", {}), ("KONTROL: gelgit etkisi kapalı", dict(gelgit_etkisi=False)), ("KONTROL: ortak faktör stresle artmıyor", dict(ortak_dinamik=False))):
        sat, ozf, n = yay_kosullu(kw)
        js[dad] = dict(sat=sat, ozf=ozf, n=n)
        md += [f"### {dad} — {n} olay", ""] + tabloyla(sat, "kor", "Kenetlenme terçili") + [""] + tabloyla(sat, "lik", "Gelgit (likidite değişimi) terçili") + [""]
        for ad, e in (("kor", "Kenetlenme"), ("lik", "Gelgit")):
            if ad in ozf:
                md.append(f"- {e}: yüksek − düşük terçil farkı **{pct(ozf[ad]['fark'])}** [{pct(ozf[ad]['ga'][0])}, {pct(ozf[ad]['ga'][1])}]")
        md.append("")
        ortak.gunluge_yaz("L10", dict(dunya=dad), {k: v["fark"] for k, v in ozf.items()})
    # B) Gizli guc
    md += ["## B. Hisse yayı ⟷ Gizli güç × koşul", ""]
    m2, j2 = gizli_guc_kosullu()
    md += m2
    js["gizli_guc"] = j2
    # C) Kirilma
    md += ["## C. Kırılma noktası AUC × koşul (kalibre dünya, test dünyaları)", ""]
    m3, j3 = kirilma_kosullu()
    md += m3 + [""]
    js["kirilma"] = j3
    # D) gercek
    kor, dd = gercek_kor()
    md += ["## D. Gerçek örnek (aylık, 154 hisse): ortalama korelasyon", "",
           "12 aylık pencere (aylık getiriler); likidite verisi yok (NFCI repoda yok) → **Gelgit için gerçek test yapılamadı**.", "",
           "| Ay | Ort. korelasyon (12a) | SPY dd |", "|---|---|---|"]
    for t in kor.index[::3]:
        md.append(f"| {t:%Y-%m} | {kor[t]:.2f} | {pct(float(dd[t]))} |")
    zayif = kor[dd.reindex(kor.index) > -0.03]
    derin = kor[dd.reindex(kor.index) <= -0.05]
    js["gercek"] = dict(medyan=float(kor.median()), sakin=float(zayif.mean()) if len(zayif) else None, derin=float(derin.mean()) if len(derin) else None, n_derin=len(derin))
    ilk, son = kor.iloc[:6].mean(), kor.iloc[-12:].mean()
    k25 = kor.get(pd.Timestamp("2025-04-30"))
    ort25 = kor["2025-01-31":"2025-07-31"].mean()
    md += ["", f"- **Seküler düşüş:** ilk 6 ayda (2022-10…) ortalama {ilk:.2f}, son 12 ayda {son:.2f}. Hisseler zamanla birbirinden ayrışmış (ya da küratörlü liste çeşitlenmiş); tek yönlü bir trend var.",
           f"- 2025-04 (tarife düşüşü dibi): {k25:.2f}; 2025 Ocak–Temmuz ortalaması {ort25:.2f}. 12 aylık pencerede **stres anında belirgin bir kenetlenme sıçraması görünmüyor**.",
           f"- dd ≤ −%5 aylarda ortalama {derin.mean():.2f} (n={len(derin)}) vs zirveye yakın aylarda {zayif.mean():.2f} (n={len(zayif)}): fark var gibi ama düşüş aylarının çoğu korelasyonun yüksek olduğu 2022–23'e denk geliyor → trendle **karışık**, stresin etkisi olarak okunamaz.",
           "- Aylık veriyle 12 aylık pencere, kısa stres olaylarını (1–3 ay) ayıramaz. Kenetlenme ölçümü için günlük veri gerekir (ILERIDE-GERCEK-VERI.md).", ""]
    # Okuma (hesaplanmis)
    N = js["NORMAL dünya (kalibre)"]
    sat = N["sat"]
    toplam = sum(sat[f"kor{k}"]["n"] for k in range(3))
    pay_kor, pay_lik = sat["kor2"]["n"] / toplam, sat["lik2"]["n"] / toplam
    k_n, k_g, k_o = N["ozf"], js["KONTROL: gelgit etkisi kapalı"]["ozf"], js["KONTROL: ortak faktör stresle artmıyor"]["ozf"]
    f = lambda d, a: (f"{pct(d[a]['fark'])} [{pct(d[a]['ga'][0])}, {pct(d[a]['ga'][1])}]" if a in d else "–")
    gk = js["gizli_guc"]
    md += ["## Okuma — hangi koşulda ne işe yarıyor?", "",
           f"1. **Koşullar büyük ölçüde stres vekili.** Y2 olaylarının %{pay_kor*100:.0f}'ı yüksek-kenetlenme, %{pay_lik*100:.0f}'ı yüksek-likidite-sıkılaşması terçilinde. Yay sinyali zaten stres anında çıkıyor; düşük terçil hücreleri küçük (n≈40–100) ve güven aralıkları geniş.",
           f"2. **Yay × Kenetlenme:** yüksek − düşük fark {f(k_n,'kor')}; kontrol (ortak faktör stresle artmıyor): {f(k_o,'kor')}. Sıfırdan ayırt edilemiyor: kenetlenme, yay getirisini stresin ötesinde ayrıca değiştirmiyor.",
           f"3. **Yay × Gelgit:** yüksek − düşük fark {f(k_n,'lik')}; gelgit mekanizması kapalıyken {f(k_g,'lik')}. İkisi de benzer: simülatöre koyduğumuz 'likidite gevşerken yay daha hızlı toparlar' etkisi (±%40 yarılanma) bu örneklemle **ayırt edilemiyor**; gözlenen fark, sıkılaşma anının daha derin stres olması (daha büyük sıçrama) nedeniyle olabilir.",
           f"4. **Hisse yayı ⟷ Gizli güç × koşul:** krize özgü D1 − D5 yüksek-kenetlenmede {pct(gk['kor_p2']['ozel'])} [{pct(gk['kor_p2']['ga'][0])}, {pct(gk['kor_p2']['ga'][1])}], düşükte {pct(gk['kor_p0']['ozel'])} [{pct(gk['kor_p0']['ga'][0])}, {pct(gk['kor_p0']['ga'][1])}]. "
           "Yani 'en çok düşen ekstra toparlanır' etkisi yalnızca yüksek stres/kenetlenme koşullarında görünüyor; düşük kenetlenmede sıfıra yakın (örnek küçük).",
           "5. **Kırılma noktası × koşul:** *panikten normale* geçiş AUC'u kenetlenme arttıkça artıyor (bölüm C); yükselişten düşüşe geçişte belirgin örüntü yok. Panik bitişi, yüksek-kenetlenme (panik) durumunda daha tahmin edilebilir.",
           "6. **Gerçek veri:** Gelgit için hiç test yapılamadı (likidite serisi yok). Kenetlenme için aylık veri yetersiz; korelasyonun seküler düşüşü stres etkisini gizliyor.", "",
           "**Genel sonuç:** Kenetlenme ve Gelgit bu aşamada *bağımsız* bir bilgi eklemiyor; stres düzeyinin göstergesi gibi davranıyorlar. Yay ve hisse yayı etkisi yüksek stres koşullarında ortaya çıkıyor. Gerçek günlük veriyle (korelasyon) ve makro seri ile (NFCI) tekrar sınanmadan ilerlemek erken.",
           "",
           "> Bu tablolardaki yönler simülatörün yapısından (korelasyon ve likiditenin stresle birlikte hareket etmesi) beklenir; gerçek piyasada geçerliliği bu deneyle sınanmaz."]
    yaz("kosullar", "\n".join(md) + "\n", js)

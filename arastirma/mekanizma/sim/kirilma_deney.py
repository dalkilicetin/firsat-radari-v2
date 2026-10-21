"""Kirilma noktasi deneyi (L9): rejim gecislerini oncu degiskenlerle tahmin. Sim + aylik gercek ornek."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.special import expit
from scipy.stats import rankdata

from mekanizma.hipotez import yukle
from mekanizma.mekanizmalar import kirilma as K
from mekanizma.motor import sonuc
from mekanizma.sim import ortak
from mekanizma.sim.deneyler import _harita
from mekanizma.sim.ortak import BASLIK, pct, yaz
from mekanizma.sim.piyasa import simule

H = yukle("kirilma")
DUNYALAR = {"yay + bozulma var (kalibre)": {}, "olay yok (negatif kontrol)": dict(lam_P=0.0, lam_B=0.0, rho_B=0.0, sm=0.0)}


def _isci(a):
    kw, tohum = a
    d = simule(ortak.ayar_yukle(n_hisse=40, **kw), tohum)
    e = d.endeks
    oz = K.ozellikler(e["adj"], d.hisseler, e["vix"], e["kredi"], H)
    rj = K.rejim(e["adj"], H["rejim"])
    out = {}
    for gad, g in H["gorevler"].items():
        for u in H["hedef_ufuklar"]:
            y = sonuc.gecis_hedefi(rj, u, g["kaynak"], g["hedef"])
            df = oz.copy()
            df["y"] = y
            df = df.dropna().iloc[:: H["inceltme"]]
            df["tohum"] = tohum
            out[(gad, u)] = df
    return out


def auc(y, s):
    y = np.asarray(y, bool)
    n1, n0 = y.sum(), (~y).sum()
    if n1 == 0 or n0 == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def _fit(X, y):
    Xc = sm.add_constant(X, has_constant="add")
    r = sm.GLM(y, Xc, family=sm.families.Binomial()).fit_regularized(alpha=H["ridge"], L1_wt=0.0)
    return np.asarray(r.params)


def degerlendir(parca, OZ=None):
    OZ = OZ or K.OZ
    egit = pd.concat([p for t, p in parca.items() if t in H["egitim_tohum"]] or [pd.DataFrame()])
    test = pd.concat([p for t, p in parca.items() if t in H["test_tohum"]] or [pd.DataFrame()])
    if len(egit) < 100 or len(test) < 100 or egit["y"].sum() < 10 or test["y"].sum() < 10:
        return None
    mu, sd = egit[OZ].mean(), egit[OZ].std().replace(0, 1)
    Xe, Xt = ((egit[OZ] - mu) / sd).to_numpy(), ((test[OZ] - mu) / sd).to_numpy()
    b = _fit(Xe, egit["y"].to_numpy())
    p = expit(b[0] + Xt @ b[1:])
    yt = test["y"].to_numpy()
    taban = yt.mean()
    ust = p >= np.quantile(p, 0.90)
    # katsayi kararliligi: her egitim dunyasinda ayri fit
    isaretler = []
    for t, pp in parca.items():
        if t in H["egitim_tohum"] and pp["y"].sum() >= 5 and len(pp) > 50:
            bb = _fit(((pp[OZ] - mu) / sd).to_numpy(), pp["y"].to_numpy())
            isaretler.append(np.sign(bb[1:]))
    kararlilik = (np.mean([np.mean(i == np.sign(b[1:])) for i in isaretler], axis=0) if False else
                  np.mean(np.array([i == np.sign(b[1:]) for i in isaretler]), axis=0)) if isaretler else np.full(len(OZ), np.nan)
    tek = {c: max(auc(yt, test[c].to_numpy()), 1 - auc(yt, test[c].to_numpy())) for c in OZ}
    return dict(n_test=int(len(test)), taban=float(taban), auc=auc(yt, p), brier=float(np.mean((p - yt) ** 2)), brier_taban=float(np.mean((taban - yt) ** 2)),
                lift10=float(yt[ust].mean() / taban) if taban > 0 else float("nan"), katsayi=dict(zip(["sabit"] + OZ, map(float, b))),
                kararlilik=dict(zip(OZ, map(float, kararlilik))), tek_auc=tek)


def aylik_gercek():
    from mekanizma.veri import ornek
    from mekanizma.ozellik.rejim import kural_rejim
    a = ornek.aylik()
    spy = a["SPY"]
    r = H["aylik"]["rejim"]
    rj = kural_rejim(spy, r["vol_n"], r["vol_esik"], r["trend_n"], r["min_sure"], H["aylik"]["min_gecmis"])
    return spy, rj


def kirilma():
    md = ["# L9 — Kırılma noktası: rejim geçişlerini önceden görebilir miyiz?", "", BASLIK,
          "Rejim (kural tabanlı): trend (200 bar ortalama) × oynaklık (63 bar vol'un genişleyen yüzdeliği > 0.70), yeni rejim 10 bar sürmedikçe geçilmez. "
          "**İki görev:** (a) *panikten normale*: `oynak_düşüş` rejimindeyken sonraki 21/63 barda yükseliş rejimine geçiş; (b) *yükselişten düşüşe*: yükseliş rejimindeyken sonraki 21/63 barda düşüş rejimine geçiş.",
          "Model: ridge lojistik regresyon (8 öncü değişken, standartlaştırılmış). **Eğitim: tohum 0–9, test: tohum 10–19** (farklı dünyalar). Her 5. bar alınır (ardışık barlar bağımlı).",
          "Metrikler: AUC (0.5 = şans), Brier (taban oranı tahmininden düşükse iyi), lift = en yüksek %10 tahminde gerçekleşme oranı / taban oranı.", ""]
    js = {}
    for dad, kw in DUNYALAR.items():
        res = _harita(_isci, [(kw, t) for t in range(20)])
        md += [f"## Dünya: {dad}", "", "| Görev | Ufuk | n (test) | Taban oranı | AUC | Brier (taban) | Lift %10 |", "|---|---|---|---|---|---|---|"]
        js[dad] = {}
        for gad in H["gorevler"]:
            for u in H["hedef_ufuklar"]:
                parca = {t: r[(gad, u)] for t, r in enumerate(res)}
                m = degerlendir(parca)
                if m is not None:
                    m["auc_sadece_dd"] = degerlendir(parca, ["dd"])["auc"]
                    m["auc_dd_yok"] = degerlendir(parca, [c for c in K.OZ if c != "dd"])["auc"]
                js[dad][f"{gad}_{u}"] = m
                if m is None:
                    md.append(f"| {gad} | {u} | yetersiz örnek | | | | |"); continue
                md.append(f"| {gad} | {u} | {m['n_test']} | {pct(m['taban'],0)} | **{m['auc']:.2f}** | {m['brier']:.3f} ({m['brier_taban']:.3f}) | {m['lift10']:.1f}× |")
                ortak.gunluge_yaz("kirilma", dict(dunya=dad, gorev=gad, ufuk=u), dict(auc=m["auc"], lift=m["lift10"]))
        md += ["", "**Ablation (AUC):** tam model / sadece `dd` / `dd` olmadan diğer 7 öncü", "", "| Görev | Ufuk | Tam | Sadece dd | dd olmadan | Öncülerin ek katkısı (tam − sadece dd) |", "|---|---|---|---|---|---|"]
        for gad in H["gorevler"]:
            for u in H["hedef_ufuklar"]:
                m = js[dad].get(f"{gad}_{u}")
                if m:
                    md.append(f"| {gad} | {u} | {m['auc']:.2f} | {m['auc_sadece_dd']:.2f} | {m['auc_dd_yok']:.2f} | {m['auc']-m['auc_sadece_dd']:+.2f} |")
        md.append("")
    ana = DUNYALAR and list(DUNYALAR)[0]
    md += ["## Hangi öncü değişken işe yarıyor? (kalibre dünya, tek değişkenli AUC ≥ 0.5 yönüne çevrilmiş, ufuk 63)", "",
           "| Değişken | " + " | ".join(H["gorevler"]) + " | katsayı işareti kararlılığı (panikten normale) |", "|---|" + "---|" * (len(H["gorevler"]) + 1)]
    for c in K.OZ:
        satir = []
        for gad in H["gorevler"]:
            m = js[ana].get(f"{gad}_63")
            satir.append("–" if not m else f"{m['tek_auc'][c]:.2f}")
        m0 = js[ana].get("panikten_normale_63")
        md.append(f"| {c} | " + " | ".join(satir) + f" | {pct(m0['kararlilik'][c],0) if m0 else '–'} |")
    md += ["", "(Tek değişkenli AUC bilerek yön-bağımsız: 0.5 = bilgi yok. Kararlılık: 10 eğitim dünyasının ayrı ayrı fit'inde katsayı işareti toplu fit ile aynı olan dünya oranı.)", ""]
    # gercek ornek
    spy, rj = aylik_gercek()
    gecisler = [(t, rj.shift(1)[t], rj[t]) for t in rj.index if rj[t] is not None and rj.shift(1)[t] is not None and rj[t] != rj.shift(1)[t]]
    md += ["## Gerçek örnek: aylık SPY rejimi (2022–2026, betimsel)", "",
           "Aylık parametreler (`kirilma.yaml → aylik`): vol 6 ay, trend 10 ay ortalaması, min süre 2 ay. VIX, kredi ve hisse genişliği öncüleri aylık örnekte yok/ısınma yetersiz; sadece rejim yolu gösterilir. **Test değil.**", "",
           "| Ay | Rejim | SPY |", "|---|---|---|"]
    for t in rj.index:
        if t >= pd.Timestamp("2022-01-01") and rj[t] is not None:
            md.append(f"| {t:%Y-%m} | {rj[t]} | {spy[t]:.0f} |")
    js["gercek_gecisler"] = [(str(t.date()), a, b) for t, a, b in gecisler]
    md += ["", "Geçişler: " + "; ".join(f"{t:%Y-%m}: {a}→{b}" for t, a, b in gecisler if t >= pd.Timestamp('2022-01-01')),
           "**Gecikme notu:** 2025'te 'düşüş' rejimi ancak SPY'ın dip ayında (2025-04, −%8) ilan edildi ve 2 ay sonra yükselişe döndü; kural krizi *geç* etiketliyor. "
           "2022'nin düşüşü ise rejimin ısınma süresine (vol yüzdeliği + 10 ay ortalaması) denk geldiği için aylık yolda hiç görünmüyor.", "",
           "## Okuma"]
    kal, nul = js[ana], js[list(DUNYALAR)[1]]
    k63, n63 = kal.get("panikten_normale_63"), nul.get("panikten_normale_63")
    y63, ny63 = kal.get("yukselisten_dususe_63"), nul.get("yukselisten_dususe_63")
    if k63 and n63 and y63 and ny63:
        md += [f"- **Negatif kontrol başarısız:** olay olmayan dünyada bile AUC yüksek ({n63['auc']:.2f} / {ny63['auc']:.2f}, ufuk 63) — kalibre dünyadakiyle ({k63['auc']:.2f} / {y63['auc']:.2f}) neredeyse aynı. "
               "Yani yüksek AUC, öncü değişkenlerin geçişi *önceden gördüğünü* göstermiyor; rejim tanımı (fiyat − 200 bar ortalama, oynaklık yüzdeliği) ile `dd` arasındaki **mekanik ilişkiyi** ölçüyor.",
               f"- `dd` tek başına AUC {k63['auc_sadece_dd']:.2f} / {y63['auc_sadece_dd']:.2f}; tam model {k63['auc']:.2f} / {y63['auc']:.2f}. Diğer 7 öncünün (genişlik ayrışması, VIX, kredi, korelasyon, momentum) **ek katkısı** {k63['auc']-k63['auc_sadece_dd']:+.2f} / {y63['auc']-y63['auc_sadece_dd']:+.2f}: küçük.",
               f"- `dd` olmadan 7 öncü: kalibre dünyada AUC {k63['auc_dd_yok']:.2f} / {y63['auc_dd_yok']:.2f}, olaysız dünyada {n63['auc_dd_yok']:.2f} / {ny63['auc_dd_yok']:.2f}. "
               f"Aradaki fark (**{k63['auc_dd_yok']-n63['auc_dd_yok']:+.2f} / {y63['auc_dd_yok']-ny63['auc_dd_yok']:+.2f}**) mekanik `dd` etkisinden arındırılmış, *olay kaynaklı* öncü bilgidir.",
               f"  - Panikten normale: fark belirgin; en iyi tek değişkenler `kredi_egim_60` ({kal['panikten_normale_63']['tek_auc']['kredi_egim_60']:.2f}), `ort_kor_63` ({kal['panikten_normale_63']['tek_auc']['ort_kor_63']:.2f}), `momentum_farki` ({kal['panikten_normale_63']['tek_auc']['momentum_farki']:.2f}). "
               "Bunlar simülatörde panikle birlikte oynayan değişkenler (kredi spread'i `m`'ye bağlı, korelasyon stresle artıyor) — yani bulgu *tasarımın sonucu*, gerçek piyasada ayrıca sınanmalı.",
               "  - Yükselişten düşüşe: fark küçük; yükselişteki düşüş geçişlerini bu öncüllerle önceden görmek zayıf.",
               "- Özet: yüksek AUC'nin büyük kısmı mekanik; **panik bitişi** için kredi eğimi ve korelasyon küçük ama gerçek bir artı bilgi taşıyor; **yükselişten düşüşe** geçiş için öncü bilgi yok denecek kadar az.",
               "- Rejim kuralı histerezis nedeniyle ≥10 bar gecikmeli: 'geçişi önceden görmek' aslında *gecikmeli etiketlenen* geçişi görmek demektir."]
    yaz("kirilma", "\n".join(md) + "\n", js)

"""Kriz katalogu incelemesi -> sonuclar/katalog.md"""
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from mekanizma.ayarlar import SONUCLAR
from mekanizma.veri.katalog import katalog

# Her sutun gercek zamanli mi bilinir, sonradan mi?
BILINIRLIK = {
    "hiz": "kismen (dibe kadar olan hiz gercek zamanda izlenir; dipteki nihai hiz sonradan)",
    "dusus": "kismen (o ana kadarki dusus gercek zamanli; nihai dip sonradan)",
    "vix_zirve": "gercek zamanli (VIX o gun gorulur)",
    "kredi_sayi": "gercek zamanli (spread izlenir)",
    "resesyon_sayi": "SONRADAN (resesyon aylar sonra ilan edilir)",
    "gun_dibe": "SONRADAN (dip tarihi bilinmez)",
}


def _tablo(df, kolonlar, adlar):
    s = "| " + " | ".join(adlar) + " |\n|" + "---|" * len(adlar) + "\n"
    for _, r in df.iterrows():
        s += "| " + " | ".join(str(r[k]) for k in kolonlar) + " |\n"
    return s


def _rho(x, y):
    m = x.notna() & y.notna()
    if m.sum() < 4:
        return np.nan, np.nan, int(m.sum())
    r, p = spearmanr(x[m], y[m])
    return r, p, int(m.sum())


def _kismi(x, y, z):
    """Sira donusumlu kismi korelasyon: z'nin etkisi (sira rejresyonu) cikarilir."""
    m = x.notna() & y.notna() & z.notna()
    rx, ry, rz = x[m].rank(), y[m].rank(), z[m].rank()
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    r, p = spearmanr(ex, ey)
    return r, p


def uret():
    k = katalog()
    spx = k[k["piyasa"] == "SPX"].copy()
    karsi = k[k["piyasa"] != "SPX"].copy()
    o = ["# Kriz kataloğu incelemesi", "",
         "> n = 13 S&P 500 düşüşü. Bu bir **test değil**, hipotez üretme alıştırmasıdır. Katalog değerleri yaklaşık ve hafızadan yazılmıştır.", ""]

    # 1) Tablo
    t = spx.sort_values("hiz").copy()
    t["yil"] = t["zirve_tarih"].dt.year
    t["dusus_p"] = (t["dusus"] * 100).round(1)
    t["hiz_p"] = (t["hiz"] * 100).round(2)
    t["sert"] = t["sertlik"].round(1)
    t["top_ay"] = t["toparlanma_ay"].round(1)
    o += ["## 1. Düşüşler, hızlıdan yavaşa (günlük ortalama kayıp, %)", "",
          _tablo(t, ["kimlik", "yil", "dusus_p", "gun_dibe", "hiz_p", "top_ay", "sert", "tur_on_kabul"],
                 ["Kriz", "Yıl", "Düşüş %", "Dibe gün", "Hız %/gün", "Toparlanma (ay)", "Sertlik", "Etiket"]), ""]

    # 2) Hiz ve toparlanma
    r, p, n = _rho(spx["hiz"], spx["gun_toparlanma"])
    r2, p2, _ = _rho(spx["dusus"], spx["gun_toparlanma"])
    r3, p3, _ = _rho(spx["gun_dibe"], spx["gun_toparlanma"])
    med_h, med_t = spx["hiz"].median(), spx["gun_toparlanma"].median()
    hizli = spx["hiz"] <= med_h          # negatif: daha cok kayip = hizli
    kisa = spx["gun_toparlanma"] <= med_t
    ct = pd.crosstab(hizli.map({True: "hizli dusus", False: "yavas dusus"}),
                     kisa.map({True: "kisa toparlanma", False: "uzun toparlanma"}))
    o += ["## 2. Düşüş hızı ile toparlanma süresi", "",
          f"- Spearman(hız, toparlanma günü) = {r:.2f} (p={p:.2f}, n={n}). Hız negatif sayı olduğundan **pozitif ρ = hızlı düşüş daha hızlı toparlanır**.",
          f"- Spearman(düşüş derinliği, toparlanma günü) = {r2:.2f} (p={p2:.2f}). **Derinlik toparlanmayı mekanik olarak uzatır** (eski zirveye dönmek için daha çok yol).",
          f"- Derinlik sabitlenince (sıra kısmi korelasyon) hız–toparlanma ρ = {_kismi(spx['hiz'], spx['gun_toparlanma'], spx['dusus'])[0]:.2f} (p={_kismi(spx['hiz'], spx['gun_toparlanma'], spx['dusus'])[1]:.2f}). "
          "Hız ilişkisi esas olarak derinlikten geliyorsa 'yay hızı' ayrı bir bilgi taşımıyor demektir.",
          f"- Spearman(dibe kadar gün, toparlanma günü) = {r3:.2f} (p={p3:.2f})",
          f"- Medyan hız: {med_h*100:.2f} %/gün; medyan toparlanma: {med_t:.0f} iş günü", "", "```", ct.to_string(), "```", ""]

    # 3) Gruplar
    o += ["## 3. Gruplara göre medyan toparlanma (ay)", ""]
    for kol, ad in [("resesyon", "Resesyon (sonradan bilinir)"), ("kredi_stresi", "Kredi stresi"),
                    ("politika_tepkisi", "Politika tepkisi")]:
        g = spx.groupby(kol).agg(n=("kimlik", "count"), medyan_toparlanma_ay=("toparlanma_ay", "median"),
                                 medyan_dusus_p=("dusus", lambda x: round(x.median() * 100, 1))).round(1)
        o += [f"**{ad}**", "", "```", g.to_string(), "```", ""]
    gt = spx.groupby("tur_on_kabul").agg(n=("kimlik", "count"), top_ay=("toparlanma_ay", "median"),
                                          sertlik=("sertlik", "median"), dusus_p=("dusus", lambda x: round(x.median() * 100, 1))).round(1)
    o += ["**Etiket (panik / bozulma / karma; sonradan konmuş, sadece karşılaştırma)**", "", "```", gt.to_string(), "```", ""]

    # 4) VIX
    v = spx.dropna(subset=["vix_dipten_once"])
    once = int((v["vix_dipten_once"] > 0).sum())
    ayni = int((v["vix_dipten_once"].abs() <= 10).sum())
    o += ["## 4. VIX zirvesi ve dip", "",
          f"- VIX zirvesi dipten **önce** gelen kriz: {once}/{len(v)}; dipten ±10 iş günü içinde olan: {ayni}/{len(v)}",
          f"- Medyan fark (iş günü, + = VIX zirvesi dipten önce): {v['vix_dipten_once'].median():.0f}",
          "", "```", v[["kimlik", "vix_zirve", "vix_dipten_once"]].to_string(index=False), "```", ""]
    rv, pv, nv = _rho(spx["vix_zirve"], spx["gun_toparlanma"])
    o += [f"- Spearman(VIX zirvesi, toparlanma günü) = {rv:.2f} (p={pv:.2f}, n={nv})", ""]

    # 5) Bilinirlik
    o += ["## 5. 'O anda bilinebilir mi?'", "", "| Sütun | Durum |\n|---|---|"]
    o += [f"| {a} | {b} |" for a, b in BILINIRLIK.items()]
    o += ["", "Sadece gerçek zamanlı/kısmen bilinen sütunlardan çıkan desenler hipotez sayılır.", ""]

    # 6) Karsi ornekler
    kr = karsi.copy()
    kr["dusus_p"] = (kr["dusus"] * 100).round(1)
    kr["top_yil"] = (kr["gun_toparlanma"] / 252).round(1)
    kr["dibe_yil"] = (kr["gun_dibe"] / 252).round(1)
    o += ["## 6. Karşı örnekler (yay olmayan)", "",
          _tablo(kr, ["kimlik", "dusus_p", "dibe_yil", "top_yil", "kredi_stresi", "politika_tepkisi"],
                 ["Vaka", "Düşüş %", "Dibe (yıl)", "Toparlanma (yıl)", "Kredi stresi", "Politika"]),
          f"SPX medyan: dibe {spx['gun_dibe'].median()/252:.2f} yıl, toparlanma {spx['gun_toparlanma'].median()/252:.2f} yıl. "
          "Karşı örneklerde dibe ulaşma ve toparlanma çok daha uzun; ortak nokta düşüşün **yavaş**, **kredi/banka kaynaklı** ve politika desteğinin **yetersiz/geç** olması.", ""]

    # 7) Hipotezler (sonuca gore otomatik)
    rk, _ = _kismi(spx["hiz"], spx["gun_toparlanma"], spx["dusus"])
    yuksek_kredi = spx[spx["kredi_sayi"] >= 4].sort_values("toparlanma_ay")
    dusuk_kredi = spx[spx["kredi_sayi"] <= 2]
    uzun = spx[spx["gun_toparlanma"] > spx["gun_toparlanma"].quantile(0.75)]
    h = ["## 7. Üretilen hipotezler (n=13, test değil)", ""]
    h.append(f"1. **Hızlı düşüş → hızlı toparlanma** ham ρ = {r:.2f}, derinlik sabitlenince {rk:.2f}. "
             + ("Derinlik sabitlenince de yön korunuyor; ancak 'hız' = düşüş / dibe kadar gün olduğundan bu büyük ölçüde **süre simetrisi** (uzun süren düşüş uzun süren toparlanma; ρ(dibe gün, toparlanma) yukarıda). Yay'a özgü bir bilgi mi, sadece süre mi, simülasyonda (S2) ayrıştırılacak." if rk > 0.3 else
                "Derinlik sabitlenince ilişki zayıflıyor/ters dönüyor: yay hızını tek başına düşüş hızından okumak yeterli değil; **gerilim bileşik skor** (düşüş + VIX + genişlik) gerekli."))
    h.append("2. **Kredi stresi tek başına panik/bozulma ayırt etmeye yetmiyor.** Kredi stresi yüksek (4-5) krizler: "
             + ", ".join(f"{a} ({b:.0f} ay)" for a, b in zip(yuksek_kredi["kimlik"], yuksek_kredi["toparlanma_ay"]))
             + f"; düşük (1-2): " + ", ".join(f"{a} ({b:.0f} ay)" for a, b in zip(dusuk_kredi["kimlik"], dusuk_kredi["toparlanma_ay"]))
             + ". Yüksek kredi stresli krizlerin bir kısmı hızlı toparlandı (müdahale ile kredi stresi hızla söndüğünde); ayırt edici olan stresin **düzeyi değil, ne kadar sürdüğü/açıldığı** olabilir. "
             "Test: `kredi60` (60 günlük değişim) ve `sahm` birlikte (L6-S1, `panik_kredi` duyarlılığı).")
    h.append(f"3. **VIX zirvesi dip için tek başına yeterli değil.** VIX zirvesi dipten önce gelen kriz {once}/{len(v)}, ±10 iş günü içinde olan {ayni}/{len(v)}. "
             "'VIX zirveden düştü' işareti dibe yakınlık verebilir ama dipten önce ek düşüş kalabilir: bu yüzden asıl ölçüm **MAE** (Yay Y2).")
    h.append("4. **En uzun toparlananlar:** " + ", ".join(f"{a} ({b:.0f} ay, etiket: {e})" for a, b, e in zip(uzun["kimlik"], uzun["toparlanma_ay"], uzun["tur_on_kabul"]))
             + ". " + ("Etiketi 'panik' olan 1987 de uzun sürdü: 'panik = hızlı dönüş' kuralı derin düşüşlerde (−%30+) zayıflıyor olabilir; derinlik ayrıca kontrol edilmeli." if (uzun["tur_on_kabul"] == "panik").any() else ""))
    pol = spx.sort_values("toparlanma_ay")[["kimlik", "politika_tepkisi", "toparlanma_ay"]]
    h.append("5. **Politika tepkisi (Gelgit adayı):** kategoriler n=1'lik ve çok dağınık; tabloda net bir desen yok (örn. QE'li 2007 en uzun, QE'li 2020 kısa). "
             "Bu katalogdan hipotez çıkmıyor; Gelgit sadece simülasyonda 'likidite durumu' değişkeni olarak sınanır (L10).")
    h.append("")
    h.append("> Uyarı: n = 13, birçok sütunu birlikte inceledik (çoklu karşılaştırma). Bu hipotezler **L6 (simülasyon)** ve **L7 (gerçek örnek)** ile ayrıca sınanacak.")
    o += h
    SONUCLAR.mkdir(exist_ok=True)
    (SONUCLAR / "katalog.md").write_text("\n".join(o) + "\n", encoding="utf-8")
    return "\n".join(o)


if __name__ == "__main__":
    print(uret())

"""Simulasyon deneyleri (L6). Her deney sonuclar/sim_<ad>.md + .json yazar."""
import itertools
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import yaml

from mekanizma.motor import sonuc
from mekanizma.motor.istatistik import blok_bootstrap_ga, ozet
from mekanizma.motor.olay import ayikla, bolumle
from mekanizma.sim import ortak
from mekanizma.sim.ortak import BASLIK, gercek_tur, guvenli, pct, yaz
from mekanizma.sim.piyasa import Ayar, simule
from mekanizma.veri.katalog import katalog

HAVUZ = 4


def _harita(f, args):
    with ProcessPoolExecutor(HAVUZ) as ex:
        return list(ex.map(f, args, chunksize=1))


# ---------------------------------------------------------------- 1) Kalibrasyon
METRIKLER = ["dusus", "gun_dibe", "gun_top", "sertlik"]


def _kal_isci(a):
    kw, tohum = a
    d = simule(Ayar(n_gun=252 * 60, n_hisse=5, **kw), tohum)
    return ortak.dusus_bolumleri(d.endeks["adj"]).assign(tohum=tohum)


def _ozet_dagilim(df):
    return {m: [float(df[m].quantile(q)) for q in (0.25, 0.5, 0.75)] for m in METRIKLER}


def kalibre(tohum_sayisi=8):
    k = katalog()
    spx = k[k.piyasa == "SPX"].rename(columns={"gun_toparlanma": "gun_top"})
    hedef = _ozet_dagilim(spx)
    yil = (spx.toparlanma_tarih.max() - spx.zirve_tarih.min()).days / 365.25
    hedef_oran = len(spx) / yil
    izgara = list(itertools.product((30, 60, 120), (1 / 3, 1 / 5, 1 / 8), (0.35, 0.45), (1 / 12, 1 / 20)))
    sat = []
    for yar, lp, sb, lb in izgara:
        kw = dict(yarilanma=float(yar), lam_P=lp, sB=(0.20, sb), lam_B=lb)
        bol = pd.concat(_harita(_kal_isci, [(kw, s) for s in range(tohum_sayisi)]), ignore_index=True)
        dag = _ozet_dagilim(bol)
        oran = len(bol) / (tohum_sayisi * 60)
        mesafe = sum(abs(abs(dag[m][i]) - abs(hedef[m][i])) / abs(hedef[m][i]) for m in METRIKLER for i in range(3))
        mesafe += abs(oran - hedef_oran) / hedef_oran
        sat.append(dict(yarilanma=yar, lam_P=lp, sB_ust=sb, lam_B=lb, mesafe=mesafe, oran=oran, dag=dag))
        ortak.gunluge_yaz("kalibre", kw, dict(mesafe=mesafe, oran=oran))
    sat.sort(key=lambda r: r["mesafe"])
    # Dort metrik yarilanmayi ayirt etmiyor: en iyiye %10 yakin olanlar arasindan onceden belirlenen varsayilana (60, 0.2) en yakini secilir
    yakin = [r for r in sat if r["mesafe"] <= sat[0]["mesafe"] * 1.10]
    en = min(yakin, key=lambda r: abs(np.log(r["yarilanma"] / 60)) + abs(np.log(r["lam_P"] / 0.2)))
    ortak.SONUCLAR.mkdir(exist_ok=True)
    ortak.AYAR_DOSYASI.write_text(yaml.safe_dump(
        dict(yarilanma=float(en["yarilanma"]), lam_P=float(en["lam_P"]), lam_B=float(en["lam_B"]), sB=[0.20, float(en["sB_ust"])],
             mesafe=float(en["mesafe"])), sort_keys=False), encoding="utf-8")
    md = ["# Simülatör kalibrasyonu", "", BASLIK,
          f"Katalog (13 SPX düşüşü, ~{yil:.0f} yıl) ile simüle edilen ≥%10 düşüş bölümlerinin dağılımı karşılaştırıldı. "
          f"Her ızgara noktası {tohum_sayisi} dünya × 60 yıl. Mesafe: 4 metriğin çeyreklik/medyanlarında göreli fark + yıllık sıklık farkı (düşük = iyi).",
          "",
          "> Dikkat: katalog **seçilmiş** önemli düşüşlerdir, ≥%10'luk bütün düşüşler değil; sıklık karşılaştırması zayıftır. Izgaraya katalogda olmayan `lam_B` (bozulma sıklığı) eklendi çünkü varsayılanlarla düşüşler katalogdan çok derin çıkıyordu.", "",
          "| Sıra | yarılanma | lam_P | sB üst | lam_B | mesafe | yıllık sıklık |", "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(sat[:8], 1):
        md.append(f"| {i} | {r['yarilanma']} | {r['lam_P']:.3f} | {r['sB_ust']} | {r['lam_B']:.3f} | {r['mesafe']:.2f} | {r['oran']:.2f} |")
    md += ["", f"Hedef sıklık (katalog): {hedef_oran:.2f}/yıl.", "",
           "## En iyi ayar ile katalog (çeyreklik 25 / medyan / 75)", "", "| Metrik | Katalog | Simülasyon |", "|---|---|---|"]
    for m in METRIKLER:
        f = (lambda v: " / ".join(f"{x*100:.0f}%" if m == "dusus" else f"{x:.1f}" for x in v))
        md.append(f"| {m} | {f(hedef[m])} | {f(en['dag'][m])} |")
    md += ["", f"**Seçim kuralı (sonuçlara bakmadan sabitlendi):** en iyi mesafenin %10'u içindeki {len(yakin)} ayardan, varsayılana (yarılanma 60, lam_P 0.2) en yakını: "
           f"yarılanma={en['yarilanma']}, lam_P={en['lam_P']:.3f}, sB üst={en['sB_ust']}, lam_B={en['lam_B']:.3f}.",
           "",
           "## Bu kalibrasyonun sınırları",
           "- Izgara noktaları arasındaki fark küçük: bu 4 metrik **yarılanma süresini belirlemiyor**. Yay gücü simülasyon sonuçlarında bir *varsayım*; S4'te `yarılanma` bir duyarlılık ekseni olarak değiştirilir.",
           "- Simülatör, katalogdan **daha hızlı toparlanıyor** (medyan sertlik ~1.0, katalogda ~1.7). Yani simdeki yay muhtemelen gerçek piyasadakinden güçlü. S4 'bulunma olasılığı' sonuçları **iyimser** okunmalı.",
           "- Katalog 13 satır; dağılımların kendisi de belirsiz.",
           "", "Seçilen ayar `sonuclar/sim_ayar.yaml` dosyasına yazıldı; sonraki deneyler bunu kullanır."]
    yaz("sim_kalibre", "\n".join(md) + "\n", dict(hedef=hedef, hedef_oran=hedef_oran, izgara=sat))
    return en


# ---------------------------------------------------------------- S1) Panik / bozulma ayirt edilebilirligi
S1_OZ = ["hiz", "vix_z", "kredi60", "genislik", "sahm", "dd"]


def _s1_isci(a):
    kw, tohum = a
    P = ortak.yay_p()
    d = simule(ortak.ayar_yukle(n_hisse=40, **kw), tohum)
    oz, sg = ortak.yay_calistir(d, P)
    satir = []
    for t in ayikla(sg["Y1"], P["bekleme"]):
        i = d.endeks.index.get_loc(t)
        gt, _ = gercek_tur(d, i)
        if gt is None or oz.loc[t, S1_OZ].isna().any():
            continue
        satir.append(dict(tohum=tohum, gercek=gt, kural=sg.loc[t, "tur"], **{c: float(oz.loc[t, c]) for c in S1_OZ}))
    return satir


def _logit(egit, test):
    import statsmodels.api as sm
    mu, sd = egit[S1_OZ].mean(), egit[S1_OZ].std().replace(0, 1)
    X = sm.add_constant((egit[S1_OZ] - mu) / sd)
    y = (egit["gercek"] == "bozulma").astype(float)
    try:
        r = sm.Logit(y, X).fit(disp=0, maxiter=200)
        b = r.params
    except Exception:
        r = sm.Logit(y, X).fit_regularized(disp=0, alpha=1e-2)
        b = r.params
    Xt = sm.add_constant((test[S1_OZ] - mu) / sd, has_constant="add")
    tahmin = np.where(Xt.to_numpy() @ b.to_numpy() > 0, "bozulma", "panik")
    return tahmin, b


def _karisiklik(gercek, tahmin):
    return {g: {t: int(((gercek == g) & (tahmin == t)).sum()) for t in ("panik", "bozulma")} for g in ("panik", "bozulma")}


def s1():
    sonuc_ = {}
    md = ["# S1 — Panik mi, bozulma mı? Ayırt edilebilirlik", "", BASLIK,
          "Her Y1 olayında **gerçek tür** simülatörden bilinir (düşüşün çoğu `m`'den mi, `F`'den mi). Dedektör bunu göremez; "
          "kural (`kredi60 > 0.5` veya Sahm) ve lojistik regresyon (tohum 0–9 eğitim, 10–19 test) karşılaştırılır.",
          "**Etiket notu:** 'bozulma' = düşüşün çoğu geri dönmeyen kısımdan (`F`) geliyor. Sıradan rastgele yürüyüş düşüşleri de `F`'ye yazıldığı için bu sınıfa girer; bu yüzden Y1 olaylarının çoğu 'bozulma' etiketli çıkar. Yani 'bozulma' = *geri dönmeyecek düşüş*, ekonomik kriz anlamına gelmez.",
          "`panik_kredi`: panik anında kredi spread'inin ne kadar açıldığı (0 = hiç; 1998/2020'de gerçekte açılmıştı).", "",
          "| panik_kredi | n (test) | panik oranı | kural doğruluğu | lojistik doğruluğu | hep-çoğunluk | panik yakalama: kural | panik yakalama: lojistik | kural: panik→bozulma hatası |", "|---|---|---|---|---|---|---|---|---|"]
    for pk in (0.0, 2.0, 4.0, 8.0):
        satir = sum(_harita(_s1_isci, [(dict(panik_kredi=pk), t) for t in range(20)]), [])
        df = pd.DataFrame(satir)
        egit, test = df[df.tohum < 10], df[df.tohum >= 10]
        tah, b = _logit(egit, test)
        kural_ok = float((test["kural"] == test["gercek"]).mean())
        loj_ok = float((tah == test["gercek"].to_numpy()).mean())
        taban = float(max((test["gercek"] == "panik").mean(), (test["gercek"] == "bozulma").mean()))
        pan = test[test.gercek == "panik"]
        yan = float((pan["kural"] == "bozulma").mean()) if len(pan) else float("nan")
        sonuc_[str(pk)] = dict(n_test=len(test), panik_orani=float((test.gercek == "panik").mean()), kural=kural_ok, lojistik=loj_ok,
                                taban=taban, kural_panik_hatasi=yan, kural_karisiklik=_karisiklik(test["gercek"].to_numpy(), test["kural"].to_numpy()),
                                loj_karisiklik=_karisiklik(test["gercek"].to_numpy(), tah), katsayilar=dict(b))
        kc, lc = sonuc_[str(pk)]["kural_karisiklik"]["panik"], sonuc_[str(pk)]["loj_karisiklik"]["panik"]
        sonuc_[str(pk)]["panik_recall_kural"] = kc["panik"] / max(1, kc["panik"] + kc["bozulma"])
        sonuc_[str(pk)]["panik_recall_loj"] = lc["panik"] / max(1, lc["panik"] + lc["bozulma"])
        md.append(f"| {pk} | {len(test)} | {pct(sonuc_[str(pk)]['panik_orani'],0)} | {pct(kural_ok,0)} | {pct(loj_ok,0)} | {pct(taban,0)} | "
                  f"{pct(sonuc_[str(pk)]['panik_recall_kural'],0)} | {pct(sonuc_[str(pk)]['panik_recall_loj'],0)} | {pct(yan,0)} |")
        ortak.gunluge_yaz("S1", dict(panik_kredi=pk), dict(kural=kural_ok, lojistik=loj_ok, taban=taban))
    md += ["", "## Lojistik katsayıları (standartlaştırılmış; + = bozulma lehine)", "", "| panik_kredi | " + " | ".join(["sabit"] + S1_OZ) + " |", "|" + "---|" * (len(S1_OZ) + 2)]
    for pk, r in sonuc_.items():
        md.append(f"| {pk} | " + " | ".join(f"{r['katsayilar'].get(c, float('nan')):.2f}" for c in ["const"] + S1_OZ) + " |")
    md += ["", "## Karışıklık matrisleri (satır = gerçek, sütun = tahmin)", ""]
    for pk, r in sonuc_.items():
        md.append(f"- panik_kredi={pk}: kural {r['kural_karisiklik']}; lojistik {r['loj_karisiklik']}")
    r2 = sonuc_["2.0"]
    md += ["", "## Okuma",
           f"- **Kural** doğruluğu ({pct(r2['kural'],0)}) 'hep çoğunluk' tabanının ({pct(r2['taban'],0)}) {'altında' if r2['kural'] < r2['taban'] else 'üstünde'}: bozulmaların çoğunu ilk aşamada 'panik' sanıyor (kredi/Sahm gecikmeli).",
           f"- **Lojistik** tabanı yalnızca {(r2['lojistik']-r2['taban'])*100:+.0f} puan aşıyor; paniklerin {pct(r2['panik_recall_loj'],0)}'ını yakalıyor. Tür ayrımı bu özelliklerle **zayıf**.",
           "- `panik_kredi` arttıkça kural paniği bozulma sanıyor (son sütun) ve `kredi60` katsayısı işaret değiştiriyor: kredi spread'i ancak panik kredi açmıyorsa ayırt edici (katalogdaki 1998/2020 paniklerinde açmıştı).",
           "- Sonuç: panik/bozulma ayrımına **güvenerek** karar verilmemeli; asıl ölçüm tür tahmini değil, sinyal sonrası getiri ve ek düşüş (S2). Bu simülasyon-içi bir sınırdır."]
    yaz("sim_S1", "\n".join(md) + "\n", sonuc_)


# ---------------------------------------------------------------- S2) Bosalma isaretleri ve ek aci
S2_VARYANT = {"Y1 (sadece gerilim)": "Y1", "Y2 (gerilim + herhangi bosalma)": "Y2", "Y2: sadece VIX düşüşü": "Y2_vix_dusus",
              "Y2: sadece genişlik itkisi": "Y2_itki", "Y2: sadece fiyat teyidi": "Y2_teyit", "basit: dd ≤ −%15": "basit"}


def _s2_isci(a):
    kw, tohum = a
    P = ortak.yay_p()
    h = P["ana_ufuk"]
    d = simule(ortak.ayar_yukle(n_hisse=40, **kw), tohum)
    adj = d.endeks["adj"]
    oz, sg = ortak.yay_calistir(d, P)
    ileri, mae = sonuc.ileri_getiri(adj, [h])[h], sonuc.mae(adj, h)
    out = dict(kosulsuz=float(ileri.mean()), kosulsuz_mae=float(mae.mean()), v={})
    for ad, kol in S2_VARYANT.items():
        ol = ayikla(sg[kol], P["bekleme"])
        out["v"][ad] = (ileri.reindex(ol).dropna().tolist(), mae.reindex(ol).dropna().tolist())
    # katalog hipotezi: hiz mi, sure mi (Y1 olaylari)
    ol = ayikla(sg["Y1"], P["bekleme"])
    top = sonuc.toparlanma_suresi(adj, list(ol), 252)
    satir = []
    for t in ol:
        i = adj.index.get_loc(t)
        gt, pk = gercek_tur(d, i)
        satir.append(dict(tur=gt, dd=float(oz.loc[t, "dd"]), hiz=float(oz.loc[t, "hiz"]), sure=i - pk, top=top.get(t, np.nan)))
    out["hiz_sure"] = satir
    return out


def _kismi_spearman(x, y, z):
    from scipy.stats import spearmanr
    rx, ry, rz = x.rank(), y.rank(), z.rank()
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
    ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return float(spearmanr(ex, ey)[0])


def s2():
    res = _harita(_s2_isci, [({}, t) for t in range(20)])
    kos = float(np.mean([r["kosulsuz"] for r in res]))
    kos_mae = float(np.mean([r["kosulsuz_mae"] for r in res]))
    md = ["# S2 — Boşalma işaretleri ve ek acı (MAE)", "", BASLIK,
          "20 dünya × 60 yıl, kalibre ayar. Her satır, ayıklanmış olayların (63 bar bekleme) **63 bar ileri getirisi** ve girişten sonraki **en kötü ek düşüş (MAE)**.",
          f"Koşulsuz (her gün girilseydi): ortalama 63g getiri {pct(kos)}, ortalama MAE {pct(kos_mae)}.", "",
          "| Sinyal | n olay | 63g ort. getiri [%90 GA] | koşulsuza fark | isabet | MAE ort. | MAE < −%5 | MAE < −%10 |", "|---|---|---|---|---|---|---|---|"]
    js = {}
    for ad in S2_VARYANT:
        g = np.array(sum((r["v"][ad][0] for r in res), []))
        m = np.array(sum((r["v"][ad][1] for r in res), []))
        o = ozet(g)
        js[ad] = dict(getiri=o, mae_ort=float(m.mean()) if len(m) else None, mae5=float((m < -0.05).mean()) if len(m) else None,
                      mae10=float((m < -0.10).mean()) if len(m) else None, fark=(o["ort"] - kos) if o["ort"] is not None else None)
        md.append(f"| {ad} | {o['n']} | {ortak.ga_str(o)} | {pct(js[ad]['fark'])} | {pct(o['isabet'],0)} | {pct(js[ad]['mae_ort'])} | {pct(js[ad]['mae5'],0)} | {pct(js[ad]['mae10'],0)} |")
        ortak.gunluge_yaz("S2", dict(sinyal=ad), dict(ort=o["ort"], n=o["n"]))
    hs = pd.DataFrame(sum((r["hiz_sure"] for r in res), []))
    hs = hs.dropna()
    md += ["", "## Katalog hipotezi 1: 'hızlı düşüş → hızlı toparlanma' hıza mı süreye mi bağlı?", "",
           f"Y1 olaylarında (n={len(hs)}, toparlanması bilinenler). Spearman, **derinlik (dd) sabitlenerek**; toparlanma = girişten eski 252 bar zirvesine dönüş.", ""]
    from scipy.stats import spearmanr
    md += ["| Grup | n | ρ(hız, toparlanma \\| dd) | ρ(düşüş süresi, toparlanma \\| dd) |", "|---|---|---|---|"]
    gr = {"hepsi": hs, "gerçek panik": hs[hs.tur == "panik"], "gerçek bozulma": hs[hs.tur == "bozulma"]}
    js["hiz_sure"] = {}
    for ad, g in gr.items():
        if len(g) < 8:
            md.append(f"| {ad} | {len(g)} | – | – |"); continue
        a, b = _kismi_spearman(g["hiz"], g["top"], g["dd"]), _kismi_spearman(g["sure"], g["top"], g["dd"])
        js["hiz_sure"][ad] = dict(n=len(g), hiz=a, sure=b)
        md.append(f"| {ad} | {len(g)} | {a:.2f} | {b:.2f} |")
    hz = js["hiz_sure"].get("hepsi")
    md += ["", ("**Sonuç:** simülatörün yayı hız–toparlanma ilişkisi **üretmiyor** (ρ≈0); katalogdaki ilişki bu mekanizmayla açıklanmıyor, şans (n=13, çok sütun denendi) veya başka bir mekanizma olabilir." if hz and abs(hz["hiz"]) < 0.15 else "Simülasyonda hız–toparlanma ilişkisi var; katalogdakiyle karşılaştırılabilir."),
           "", "Katalogda (n=13, derinlik sabit): ρ(hız, toparlanma) = +0.60. Bu bir *hız* etkisi mi yoksa düşüşün **süresi**nin toparlanma süresini belirlemesi mi — burada ayrıştırılır.", "",
           "## Okuma", "- 'MAE < −%5' sütunu, 'toparlanmadan hemen önceki bölge' sorusunun cevabıdır: sinyalden sonra ne kadar daha acı çekilir?",
           "- Y2, Y1'e göre MAE'yi azaltıyor ve getiriyi koruyorsa boşalma işaretleri değer katıyor demektir.",
           "- 'koşulsuza fark' ≈ 0 ise sinyal, piyasanın zaten yükselmesinden başka bir şey yakalamıyordur (bkz. S3)."]
    yaz("sim_S2", "\n".join(md) + "\n", js)


# ---------------------------------------------------------------- S3) Sahte yay (negatif kontrol)
S3_DUNYA = {"yay var (kalibre)": {}, "yay yok, bozulma var": dict(lam_P=0.0, rho_B=0.0, sm=0.0),
            "yay yok, bozulma yok (saf yürüyüş)": dict(lam_P=0.0, lam_B=0.0, rho_B=0.0, sm=0.0)}


def _ga_disliyor(x, kosulsuz):
    lo, hi = blok_bootstrap_ga(x)
    if np.isnan(lo):
        return None
    return bool(lo - kosulsuz > 0 or hi - kosulsuz < 0)


def _s3_isci(a):
    kw, tohum = a
    P = ortak.yay_p()
    h = P["ana_ufuk"]
    d = simule(ortak.ayar_yukle(n_hisse=40, **kw), tohum)
    adj = d.endeks["adj"]
    _, sg = ortak.yay_calistir(d, P)
    ileri = sonuc.ileri_getiri(adj, [h])[h]
    u = float(ileri.mean())
    out = dict(kosulsuz=u, s={})
    for kol in ("Y1", "Y2"):
        ol = ayikla(sg[kol], P["bekleme"])
        y = ileri.reindex(ol).dropna().to_numpy()
        rng = np.random.default_rng(1000 + tohum)
        n_ol = max(len(ol), 10)
        yanlis = []
        for _ in range(10):                                  # ayni sayida rastgele sinyal
            gun = np.sort(rng.choice(len(adj) - 400, size=n_ol * 3, replace=False))
            rs = pd.Series(False, index=adj.index); rs.iloc[gun] = True
            r = ileri.reindex(ayikla(rs, P["bekleme"])).dropna().to_numpy()
            yanlis.append(_ga_disliyor(r, u))
        out["s"][kol] = dict(ort=float(y.mean()) if len(y) else None, n=len(y), disliyor=_ga_disliyor(y, u),
                             fark=(float(y.mean()) - u) if len(y) else None, yanlis=[x for x in yanlis if x is not None])
    return out


def s3():
    md = ["# S3 — Sahte yay (negatif kontrol)", "", BASLIK,
          "Aynı dedektör, **yayın olmadığı** dünyalarda da çalıştırıldı. Amaç: 'dipten alma sırf piyasa uzun vadede yükseldiği için iyi görünür' tuzağını sayıyla görmek ve yanlış alarm oranını ölçmek.",
          "20 dünya × 60 yıl. 'GA dışlıyor' = sinyal olaylarının ortalama getirisi ile koşulsuz ortalama arasındaki fark %90 güven aralığında sıfırı dışlıyor (şans eseri beklenen ≈ %10; 20 dünyada ±%7 oynar).", "",
          "| Dünya | Sinyal | Koşulsuz 63g | Sinyal ort. getiri | Fark | GA sıfırı dışlayan dünya oranı | Rastgele sinyal yanlış alarm | olay/dünya |", "|---|---|---|---|---|---|---|---|"]
    js = {}
    for ad, kw in S3_DUNYA.items():
        res = _harita(_s3_isci, [(kw, t) for t in range(20)])
        js[ad] = {}
        for kol in ("Y1", "Y2"):
            ys = [r["s"][kol] for r in res if r["s"][kol]["ort"] is not None]
            dis = [x["disliyor"] for x in ys if x["disliyor"] is not None]
            yan = sum((r["s"][kol]["yanlis"] for r in res), [])
            j = dict(kosulsuz=float(np.mean([r["kosulsuz"] for r in res])), ort=float(np.mean([x["ort"] for x in ys])),
                     fark=float(np.mean([x["fark"] for x in ys])), dislama_orani=float(np.mean(dis)) if dis else None,
                     yanlis_alarm=float(np.mean(yan)) if yan else None, olay=float(np.mean([x["n"] for x in ys])))
            js[ad][kol] = j
            md.append(f"| {ad} | {kol} | {pct(j['kosulsuz'])} | {pct(j['ort'])} | {pct(j['fark'])} | {pct(j['dislama_orani'],0)} | {pct(j['yanlis_alarm'],0)} | {j['olay']:.0f} |")
            ortak.gunluge_yaz("S3", dict(dunya=ad, sinyal=kol), dict(fark=j["fark"], dislama=j["dislama_orani"]))
    md += ["", "## Okuma",
           "- **Saf yürüyüşte** (yay yok, bozulma yok) sinyal − koşulsuz ≈ 0 olmalı. Sinyal ortalaması yine de pozitiftir (koşulsuz sürüklenme kadar): 'dipten al' kuralı piyasa yükseldiği için *kazanıyormuş gibi* görünür, ama yaydan değil.",
           "- **Yay yok ama bozulma var** dünyasında sinyal sonrası getiri koşulsuzun altında kalır: dedektör düşüşü yakalar, düşüş sürer ('bıçağı tutmak'). Yay olmayan piyasada dedektör **zarar** eder.",
           "- Rastgele sinyallerde yanlış alarm oranı ~%10 civarındaysa güven aralıkları kabaca doğru; belirgin üstündeyse sonuçlar sıkılaştırılmalı.",
           "- 'Yay var' dünyasındaki farkı bu iki yay-yok dünyasıyla yan yana oku: **fark farkı** yayın gerçek payıdır."]
    yaz("sim_S3", "\n".join(md) + "\n", js)


# ---------------------------------------------------------------- S4) Guc analizi
def _s4_isci(a):
    kw, tohum, yil = a
    P = ortak.yay_p()
    h = P["ana_ufuk"]
    d = simule(ortak.ayar_yukle(n_gun=252 * yil, n_hisse=20, **kw), tohum)
    adj = d.endeks["adj"]
    _, sg = ortak.yay_calistir(d, P)
    ileri = sonuc.ileri_getiri(adj, [h])[h]
    u = float(ileri.mean())
    ol = ayikla(sg["Y2"], P["bekleme"])
    bol = bolumle(ol, adj.index, 126) if len(ol) else pd.Series(dtype=int)
    ilk = ol[~bol.duplicated().to_numpy()] if len(ol) else ol
    y_ol = ileri.reindex(ol).dropna().to_numpy()
    y_bol = ileri.reindex(ilk).dropna().to_numpy()

    def bul(y):
        if len(y) < 4:
            return None
        lo, hi = blok_bootstrap_ga(y)
        return bool(lo - u > 0)
    return dict(u=u, n_olay=len(y_ol), n_bolum=len(y_bol), fark_olay=float(y_ol.mean() - u) if len(y_ol) else None,
                bul_olay=bul(y_ol), bul_bolum=bul(y_bol), sd=float(y_ol.std()) if len(y_ol) > 1 else None)


def s4(dunya=120, yil=33):
    conf = {f"yarılanma {y}g, panik {l*5:.1f}/5yıl": dict(yarilanma=float(y), lam_P=l) for y in (30, 60, 120) for l in (1 / 8, 1 / 5, 1 / 3)}
    conf["YAY YOK (bozulma var)"] = dict(lam_P=0.0, rho_B=0.0, sm=0.0)
    md = ["# S4 — Güç analizi: ~33 yıllık tarihle yayı görebilir miyiz?", "", BASLIK,
          f"Her satır: {dunya} ayrı {yil} yıllık dünya (gerçek tarihin uzunluğu). Sinyal: **Y2**. 'Bulundu' = Y2 olaylarının 63 bar getirisinin %90 GA alt sınırı koşulsuz ortalamanın **üstünde**. "
          "'Olay' = ayıklanmış tüm olaylar; 'bölüm' = aynı krizdeki tekrarlar tek sayılır (gerçek tarih bu kadar bağımsız kriz verir).",
          "Son satır **yay olmayan** dünya: orada 'bulundu' oranı yanlış alarm oranıdır (tek yönlü ≈ %5 beklenir).", "",
          "| Dünya | olay/dünya | bölüm/dünya | Y2 − koşulsuz | bulundu (olay) | bulundu (bölüm) | gereken olay sayısı* |", "|---|---|---|---|---|---|---|", ]
    js = {}
    for ad, kw in conf.items():
        res = _harita(_s4_isci, [(kw, t, yil) for t in range(dunya)])
        fark = [r["fark_olay"] for r in res if r["fark_olay"] is not None]
        sd = float(np.mean([r["sd"] for r in res if r["sd"] is not None]))
        bo = [r["bul_olay"] for r in res if r["bul_olay"] is not None]
        bb = [r["bul_bolum"] for r in res if r["bul_bolum"] is not None]
        mf = float(np.mean(fark))
        gerek = (1.645 * sd / mf) ** 2 if mf > 0.002 else float("inf")
        js[ad] = dict(n_olay=float(np.mean([r["n_olay"] for r in res])), n_bolum=float(np.mean([r["n_bolum"] for r in res])), fark=mf,
                      bulundu_olay=float(np.mean(bo)) if bo else None, bulundu_bolum=float(np.mean(bb)) if bb else None, sd=sd, gereken_n=gerek)
        j = js[ad]
        gs = "yetersiz fark" if gerek == float("inf") else f"~{gerek:.0f}"
        md.append(f"| {ad} | {j['n_olay']:.0f} | {j['n_bolum']:.0f} | {pct(mf)} | {pct(j['bulundu_olay'],0)} | {pct(j['bulundu_bolum'],0)} | {gs} |")
        ortak.gunluge_yaz("S4", dict(config=ad, dunya=dunya, yil=yil), dict(bulundu_olay=j["bulundu_olay"], bulundu_bolum=j["bulundu_bolum"]))
    md += ["", "\\* Gereken olay sayısı: ortalama farkı %90 GA ile ayırt etmek için `(1.645·sd/fark)²` (olaylar bağımsız varsayımıyla; olay getirileri çakıştığı için gerçekte daha çok gerekir).", "",
           "## Okuma",
           "- 'Bölüm' sütunu, gerçek tarihin verebileceği bağımsız kriz sayısına karşılık gelir. Burada 'bulundu' oranı yanlış alarm satırına yakınsa, **33 yıllık tarihten bu mekanizma kanıtlanamaz** (var olsa bile).",
           "- 'Olay' sütunu çakışan/aynı kriz içi olayları ayrı sayar; iyimser bir üst sınırdır.",
           "- Simülatör katalogdan hızlı toparlandığı için (bkz. kalibrasyon) buradaki oranlar iyimser okunmalı.",
           "- Çıkarım: daha fazla bağımsız kriz gerekir → birden çok piyasa (ABD dışı endeksler, sektör ETF'leri) ve hisse düzeyi test (Gizli güç) önem kazanır."]
    yaz("sim_S4", "\n".join(md) + "\n", js)


# ---------------------------------------------------------------- S5) Hisse yayi <-> Gizli guc
S5_UFUK = (63, 126, 252)


def _dilimler(skor, fwd, k=5):
    """skor artan siralanir: dilim 0 = en dusuk skor (en cok dusen). Evren ortalamasina gore asiri getiri."""
    m = skor.notna() & fwd.notna()
    sk, f = skor[m], fwd[m]
    if len(sk) < 5 * k:
        return None
    sira = sk.rank(method="first")
    dil = np.ceil(sira / (len(sk) / k)).astype(int).clip(1, k) - 1
    ex = f - f.mean()
    return [float(ex[dil == q].mean()) for q in range(k)]


def _olay_etiketi(d, pk, t):
    """Zirve-t araliginda gercekten bir bozulma olayi / panik olayi var miydi? (olay bazli gercek etiket)"""
    boz = pan = False
    for _, o in d.olaylar.iterrows():
        if o.gun <= t and o.gun + o.sure >= pk:
            boz |= o.tur == "bozulma"
            pan |= o.tur == "panik"
    return "bozulma olayı" if boz else ("panik olayı" if pan else "olaysız")


def _s5_isci(a):
    kw, tohum = a
    P = ortak.yay_p()
    d = simule(ortak.ayar_yukle(n_hisse=200, **kw), tohum)
    adj, H = d.endeks["adj"], d.hisseler
    oz, sg = ortak.yay_calistir(d, P)
    ol = ayikla(sg["Y2"], P["bekleme"])
    bol = bolumle(ol, adj.index, 126) if len(ol) else pd.Series(dtype=int)
    ilk = ol[~bol.duplicated().to_numpy()] if len(ol) else ol
    lr_h, lr_e = np.log(H).diff(), np.log(adj).diff()
    n = len(adj)
    rng = np.random.default_rng(7000 + tohum)
    sakin = np.flatnonzero((oz["dd"] > -0.03).to_numpy())

    def sirala(i, pk):
        a0 = max(1, pk - 252)
        ve = lr_e.iloc[a0:pk + 1]
        beta = lr_h.iloc[a0:pk + 1].apply(lambda c: c.cov(ve)) / ve.var()
        ham = H.iloc[i] / H.iloc[pk] - 1
        kalinti = ham - beta * (adj.iloc[i] / adj.iloc[pk] - 1)
        out = {}
        for h in S5_UFUK:
            fwd = H.iloc[i + 1 + h] / H.iloc[i + 1] - 1
            out[f"ham{h}"], out[f"kal{h}"] = _dilimler(ham, fwd), _dilimler(kalinti, fwd)
        return out

    satir = []
    for t in ilk:
        i = adj.index.get_loc(t)
        gt, pk = gercek_tur(d, i)
        if gt is None or pk < 130 or i + 2 + max(S5_UFUK) >= n:
            continue
        r = dict(tohum=tohum, tarih=str(t.date()), gercek=gt, olay=_olay_etiketi(d, pk, i), tahmin=sg.loc[t, "tur"])
        r.update(sirala(i, pk))
        L = i - pk
        adaylar = sakin[(sakin - L >= 130) & (sakin + 2 + max(S5_UFUK) < n)]
        if len(adaylar) < 3:
            continue
        tab = [sirala(int(j), int(j) - L) for j in rng.choice(adaylar, 3, replace=False)]
        for k in tab[0]:
            v = [x[k] for x in tab if x[k] is not None]
            r["taban_" + k] = list(np.mean(v, axis=0)) if v else None
        satir.append(r)
    return satir


def s5():
    satir = sum(_harita(_s5_isci, [({}, t) for t in range(20)]), [])
    df = pd.DataFrame(satir)
    gruplar = [("Tüm krizler", df), ("Ayrıştırma etiketi: panik", df[df.gercek == "panik"]), ("Ayrıştırma etiketi: bozulma", df[df.gercek == "bozulma"]),
               ("Olay etiketi: panik olayı", df[df.olay == "panik olayı"]), ("Olay etiketi: bozulma olayı", df[df.olay == "bozulma olayı"]),
               ("Olay etiketi: olaysız (rastgele düşüş)", df[df.olay == "olaysız"])]
    md = ["# S5 — Hisse yayı ⟷ Gizli güç", "", BASLIK,
          f"20 dünya × 60 yıl; her krizde (Y2'nin ilk günü, *gerçek dip değil*) hisseler zirveden bu yana **beta'dan arındırılmış kalıntı getirisine** göre 5 dilime ayrılır. "
          f"**D1 = en çok düşen (yay adayı), D5 = en az düşen (gizli güç adayı).** Sonraki 63/126/252 bar getiri evren ortalamasına göre. Toplam {len(df)} kriz.", "",
          "**Önemli kontrol:** simülatörde her hissenin kendine özgü sapması normal zamanda da geri döner (kısa vadeli ters dönüş, krizden bağımsız); gerçek piyasada da benzeri olabilir. "
          "Bu yüzden her krizin yanında **aynı pencere uzunluğunda 3 sakin tarihte** aynı sıralama yapılır; tablodaki 'krize özgü' sütunu `kriz − sakin taban` farkıdır.", "",
          "İki tür etiket: *ayrıştırma* (düşüşün çoğu geri dönen `m`'den mi — rastgele düşüşler de 'bozulma' sayılır) ve *olay* (zirve–t arasında gerçekten bozulma/panik olayı var mıydı).", ""]
    js = {"n": len(df)}
    for h in S5_UFUK:
        md += [f"## Ufuk {h} bar", "", "| Grup | n | D1 − D5 (kriz) | D1 − D5 (sakin taban) | **Krize özgü** [%90 GA] |", "|---|---|---|---|---|"]
        for ad, g in gruplar:
            M = np.array([x for x in g[f"kal{h}"] if x is not None], float)
            B = np.array([x for x in g[f"taban_kal{h}"] if x is not None], float)
            if len(M) < 8 or len(B) != len(M):
                md.append(f"| {ad} | {len(g)} | yetersiz | | |"); continue
            kr, tb = M[:, 0] - M[:, 4], B[:, 0] - B[:, 4]
            ozel = kr - tb
            lo, hi = blok_bootstrap_ga(ozel)
            js.setdefault(str(h), {})[ad] = dict(n=len(M), kriz=float(kr.mean()), taban=float(tb.mean()), ozel=float(ozel.mean()), ga=[lo, hi])
            md.append(f"| {ad} | {len(M)} | {pct(kr.mean())} | {pct(tb.mean())} | **{pct(ozel.mean())}** [{pct(lo)}, {pct(hi)}] |")
        md.append("")
    k = js.get("126", {})
    pan, boz, tum = k.get("Olay etiketi: panik olayı"), k.get("Olay etiketi: bozulma olayı"), k.get("Tüm krizler")
    if pan and boz and tum:
        md += ["## Sonuç (ufuk 126, olay etiketi)", "",
               f"- Panik olaylarında krize özgü fark **{pct(pan['ozel'])}** [{pct(pan['ga'][0])}, {pct(pan['ga'][1])}]; bozulma olaylarında **{pct(boz['ozel'])}** [{pct(boz['ga'][0])}, {pct(boz['ga'][1])}].",
               f"- D1 − D5'in toplamı {pct(tum['kriz'])}, ama bunun {pct(tum['taban'])}'i sakin dönemde de var (genel ters dönüş): **krize özgü pay küçük**.",
               "- Yani 'panikte en çok düşen ekstra toparlanır' simülasyonda ölçülebiliyor; 'bozulmada dayanıklı olan ekstra kazanır' bu gürültü düzeyinde ölçülemiyor.", ""]
    md += ["## Okuma",
           "- **Krize özgü** pozitif: en çok düşenler, normal zamandaki ters dönüşün *ötesinde* krizde ekstra geri dönüyor (yay). Negatif: en az düşenler krizde ekstra avantaj kazanıyor (gizli güç).",
           "- Tüm gruplarda 'sakin taban' büyükse, kriz sıralamasının getirisi çoğunlukla normal ters dönüşten gelir ve **krize özgü bir hikâye** değildir. Bu, R2'deki gerçek veri için de zorunlu bir kontroldür.",
           "- Gizli güç hipotezi (G1/G3) bozulma olayı satırında *negatif* krize özgü fark bekler; gelmiyorsa simülatördeki kalite etkisi ya da sıralama gürültüsü baskındır. Sonuç kanıt değil, aletin duyarlılığıdır.",
           "- Hisse sıralamasındaki gürültü (günlük 1.5% kendine özgü sapma) çok yüksek; bu, gerçek verideki dilim farklarının da küçük olacağı anlamına gelir."]
    ortak.gunluge_yaz("S5", {}, {k: v for k, v in js.items() if k == "126"})
    yaz("sim_S5", "\n".join(md) + "\n", js)


def calistir(ad):
    f = {"kalibre": kalibre, "S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5}.get(ad)
    if f is None:
        print(f"'{ad}' henuz yok")
        return 0
    f()
    return 0

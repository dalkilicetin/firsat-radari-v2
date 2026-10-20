"""Son 3 yılın her haftası listeyi koştursaydık neleri yakalardık? → reports/research/arac_yakalama.md / .json

Her cuma t için ayarlı (arac_ayar.json) ilk 10 listesi o günün verisiyle çıkar. Üç soru:

1. Kazananları yakalama: dönemin en çok kazandıranları (3 ay / 6 ay, evrenin en iyi %5'i). Bir kazanan, kendi çeyreğinin
   başlangıcından itibaren (a) başlangıç haftasında, (b) çeyrek içinde herhangi bir haftada, (c) yükselişin ortasından önce
   (yükselişin ilk yarısı bitmeden) listeye girdiyse yakalanmış sayılır. Yakalama oranı = yakalanan kazanan / tüm kazananlar.
2. Liste isabeti: listedeki hisselerin kaçı sonradan kazanan oldu (hisse-hafta bazında), borsayı geçti, %30'dan fazla kaybetti.
3. Yakalanan kazanç: yakalanan kazananlarda, ilk listeye giriş haftasının kapanışından alınsaydı getirinin toplam yükselişe oranı.

Pencere: son 3 yıl (3 aylık sonucu bilinen son haftaya kadar). Karşılaştırma: aynı sayıda hisseyi rastgele seçmek (tekrarlı,
1.000 çekiliş) ve evrenin tamamını almak.

python -m radar.arac.yakalama
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config
from radar.arac import analiz
from radar.arac.analiz import Veri
from radar.arac.duzenek import VADE

R = config.ROOT / "reports" / "research"
YIL = 3
KAZANAN_PAY = 0.05


def ana(v: Veri, ayar: dict, bas: pd.Timestamp, vade: str, listeler: dict) -> dict:
    tab = v.tablo
    h = VADE[vade]
    pos = {t: i for i, t in enumerate(v.tarihler)}
    brut = tab[f"brut_{vade}"]
    ev = tab["evren"]
    haftalar = [t for t in v.tarihler if t >= bas and not brut.loc[t].where(ev.loc[t]).isna().all()]
    qs = list(analiz.ceyrek_baslari(pd.DatetimeIndex(haftalar), (bas.year, 2100)))
    kaz = (brut.where(ev).rank(axis=1, pct=True) >= 1 - KAZANAN_PAY)
    px = tab["fiyat_cuma"]
    top = {"toplam": 0, "ilk_hafta": 0, "icinde": 0, "yarimdan_once": 0}
    pay = []
    detay = []
    for t0 in qs:
        i0 = pos[t0]
        if i0 + h >= len(v.tarihler):
            continue
        weeks = v.tarihler[i0: i0 + h + 1]
        kazananlar = kaz.loc[t0][kaz.loc[t0]].index
        first = {}
        for s in weeks[:-1]:
            for c in listeler.get(s, []):
                first.setdefault(c, s)
        for c in kazananlar:
            toplam = brut.at[t0, c]
            top["toplam"] += 1
            if c in first:
                s = first[c]
                top["icinde"] += 1
                top["ilk_hafta"] += int(s == t0)
                # Yükselişin yarısı: fiyat, çeyrek başı fiyatının (1 + toplam/2) katına ulaşmadan önce girildi mi
                hedef = px.at[t0, c] * (1 + toplam / 2)
                yol = px.loc[weeks, c]
                yarim = yol.index[yol >= hedef]
                top["yarimdan_once"] += int(len(yarim) == 0 or s <= yarim[0])
                bitis = px.at[t0, c] * (1 + toplam)
                pay.append(float(np.clip((bitis / px.at[s, c] - 1) / toplam, -1, 1)) if toplam > 0 else np.nan)
            detay.append({"tarih": str(t0.date()), "cik": c, "toplam": float(toplam), "listede": c in first,
                          "giris": str(first[c].date()) if c in first else None})
    n = max(top["toplam"], 1)
    # Liste isabeti: hisse-hafta
    isabet = {"hisse_hafta": 0, "kazanan": 0, "borsayi_gecti": 0, "sert_kayip": 0}
    for s in haftalar:
        picks = listeler.get(s, [])
        net = tab[f"net_{vade}"].loc[s, picks].dropna()
        if net.empty:
            continue
        b = tab[f"kiyas_{vade}"].at[s, "borsa"]
        isabet["hisse_hafta"] += len(net)
        isabet["kazanan"] += int(kaz.loc[s, net.index].sum())
        isabet["borsayi_gecti"] += int((net > b).sum())
        isabet["sert_kayip"] += int((net < -0.30).sum())
    k = max(isabet["hisse_hafta"], 1)
    # Rastgele kıyas: her hafta listedeki kadar hisseyi evrenden çek; kazanan olma oranı ve çeyrek içinde yakalama beklentisi
    rng = np.random.default_rng(7)
    rastgele_isabet = float(np.mean([(kaz.loc[s][ev.loc[s]].mean()) for s in haftalar]))
    # rastgele listelerle çeyrek içi yakalama (1.000 simülasyon, her hafta 10 hisse)
    sim = []
    for _ in range(300):
        got = tot = 0
        rl = {}
        for t in haftalar:
            pool = ev.columns[ev.loc[t].to_numpy()]
            if len(pool):
                rl[t] = list(rng.choice(pool, size=min(10, len(pool)), replace=False))
        for t0 in qs:
            i0 = pos[t0]
            if i0 + h >= len(v.tarihler):
                continue
            seen = {c for s in v.tarihler[i0: i0 + h] for c in rl.get(s, [])}
            kz = kaz.loc[t0][kaz.loc[t0]].index
            tot += len(kz)
            got += sum(c in seen for c in kz)
        sim.append(got / max(tot, 1))
    return {"vade": vade, "ceyrek": len(qs), "kazanan": top["toplam"],
            "yakalama_ceyrek_icinde": top["icinde"] / n, "yakalama_ilk_hafta": top["ilk_hafta"] / n,
            "yakalama_yarimdan_once": top["yarimdan_once"] / n,
            "yakalanan_kazanc_payi_medyan": float(np.nanmedian(pay)) if pay else None,
            "liste_hisse_hafta": isabet["hisse_hafta"], "liste_kazanan_orani": isabet["kazanan"] / k,
            "liste_borsayi_gecen": isabet["borsayi_gecti"] / k, "liste_sert_kayip": isabet["sert_kayip"] / k,
            "rastgele_kazanan_orani": rastgele_isabet, "rastgele_yakalama": float(np.mean(sim)),
            "rastgele_yakalama_ga90": [float(np.quantile(sim, 0.05)), float(np.quantile(sim, 0.95))],
            "_detay": detay}


def main() -> dict:
    v = Veri.yukle()
    ayar = analiz.secilen_ayar()
    son = v.tablo["brut_3a"].dropna(how="all").index.max()
    bas = son - pd.DateOffset(years=YIL)
    tum = [t for t in v.tarihler if t >= bas - pd.Timedelta(weeks=1) and t <= v.tarihler[-1]]
    listeler = analiz.liste(v, ayar, pd.DatetimeIndex(tum))
    out = {"pencere": f"{bas.date()} … {son.date()}", "ayar": ayar["ad"], "sonuclar": {}}
    for vade in VADE:
        out["sonuclar"][vade] = ana(v, ayar, bas, vade, listeler)
    det = {vade: out["sonuclar"][vade].pop("_detay") for vade in VADE}
    (R / "arac_yakalama.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    pd.DataFrame([dict(vade=vade, **r) for vade, rows in det.items() for r in rows]).to_csv(R / "arac_yakalama_kazananlar.csv", index=False)
    p = lambda x: "—" if x is None else f"%{x * 100:.1f}".replace(".", ",")
    L = [f"# Son 3 yılın her haftası listeyi koştursaydık ({out['pencere']})", "",
         "| Ölçü | 3 ay | 6 ay |", "|---|---|---|"]
    s3, s6 = out["sonuclar"]["3a"], out["sonuclar"]["6a"]
    rows = [("Çeyrek sayısı", "ceyrek", int), ("Kazanan sayısı (evrenin en iyi %5'i)", "kazanan", int),
            ("**Yakalama oranı** — çeyrek içinde listeye giren kazanan", "yakalama_ceyrek_icinde", p),
            ("Çeyrek başı haftasında zaten listede olan", "yakalama_ilk_hafta", p),
            ("Yükselişin yarısından önce listeye giren", "yakalama_yarimdan_once", p),
            ("Rastgele 10'luk listelerle çeyrek içinde yakalama", "rastgele_yakalama", p),
            ("Yakalanan kazançta orta pay", "yakalanan_kazanc_payi_medyan", p),
            ("Listedeki hisselerin kazanan çıkma oranı", "liste_kazanan_orani", p),
            ("Rastgele hissenin kazanan çıkma oranı", "rastgele_kazanan_orani", p),
            ("Listedeki hisselerin borsayı geçme oranı", "liste_borsayi_gecen", p),
            ("Listedeki hisselerin %30'dan fazla kaybetme oranı", "liste_sert_kayip", p)]
    for ad, key, f in rows:
        L.append(f"| {ad} | {f(s3[key]) if f is not int else s3[key]} | {f(s6[key]) if f is not int else s6[key]} |")
    L += ["", f"Rastgele yakalama %90 aralığı: 3 ay {p(s3['rastgele_yakalama_ga90'][0])} … {p(s3['rastgele_yakalama_ga90'][1])}; "
              f"6 ay {p(s6['rastgele_yakalama_ga90'][0])} … {p(s6['rastgele_yakalama_ga90'][1])}."]
    (R / "arac_yakalama.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return out


if __name__ == "__main__":
    main()

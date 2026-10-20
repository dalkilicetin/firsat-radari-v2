"""Haftalık tarama: son Cuma'nın listesi, kartlar, alınmaz/dikkat, yaklaşan günler, karne, otopsi → site/.

python -m radar.arac.haftalik            (önbellek hazır olmalı: radar.arac.hazirla; ayar: analiz.ayarla + sınav)
Her çalışmada liste reports/canli/arac/<tarih>.json olarak kilitlenir (sonradan değiştirilmez).
"""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from radar import archive, config
from radar.arac import analiz, isaretler, site
from radar.arac.analiz import Veri
from radar.identity import build as build_identity

CANLI = config.ROOT / "reports" / "canli" / "arac"
PROFIL = analiz.R / "arac_profil.json"
SINAV_DOSYA = analiz.R / "arac_sinav.json"

SEKTOR_ADI = {"SMH": "Yarı iletken", "IGV": "Yazılım", "XBI": "Biyoteknoloji", "XLV": "Sağlık", "XLE": "Enerji",
              "ITA": "Savunma ve havacılık", "GDX": "Altın madenciliği", "XLU": "Elektrik ve altyapı", "XHB": "İnşaat",
              "JETS": "Havayolu", "XRT": "Perakende", "XLY": "Tüketim", "XLF": "Finansal hizmet", "XLRE": "Gayrimenkul",
              "XLC": "İletişim ve medya", "XLP": "Temel tüketim", "XLB": "Hammadde", "XLI": "Sanayi", "XLK": "Teknoloji donanımı",
              "IWM": "Diğer"}
MADDE = {"1.01": "önemli bir anlaşma imzaladı", "1.02": "önemli bir anlaşmayı sonlandırdı", "1.03": "iflas / konkordato başvurusu",
         "2.01": "satın alma ya da varlık satışını tamamladı", "2.02": "dönem sonuçlarını açıkladı",
         "2.03": "yeni borç aldı", "2.05": "yeniden yapılanma / işten çıkarma maliyeti açıkladı", "2.06": "değer düşüklüğü kaydetti",
         "3.01": "borsa kotasyon uyarısı aldı", "3.02": "kayıtsız hisse sattı", "4.01": "denetçisi değişti",
         "4.02": "önceki mali tablolarının geçersiz olduğunu açıkladı", "5.01": "kontrol değişikliği bildirdi",
         "5.02": "üst yönetiminde değişiklik oldu", "7.01": "yatırımcılara sunum / açıklama yaptı", "8.01": "önemli bir gelişme bildirdi"}


def _ad(name: str) -> str:
    name = re.split(r"\s+-\s+|\s+Common Stock|\s+Class [A-C]\b|\s+Ordinary Shares|\s+American Depositary", str(name))[0]
    return name.strip().rstrip(",")


def _buyukluk(x: float) -> str:
    if not np.isfinite(x):
        return "—"
    return (f"{x / 1e9:.1f} Mr$" if x >= 1e9 else f"{x / 1e6:.0f} M$").replace(".", ",")


def _y(x, isaret=True) -> str:
    return site.yuzde(None if pd.isna(x) else float(x), isaret)


def piyasa(v: Veri, t: pd.Timestamp) -> dict:
    from radar.research import context
    spy = context.etf_prices(v.tarihler - pd.Timedelta(days=1)).set_axis(v.tarihler, axis=0)["SPY"]
    ay = spy.loc[t] / spy.shift(4).loc[t] - 1
    yil = spy.loc[t] / spy.shift(52).loc[t] - 1
    vol = np.log(spy / spy.shift(1)).rolling(13).std()
    rel = vol.loc[t] / vol.loc[:t].median()
    dalga = "Yüksek" if rel > 1.3 else ("Düşük" if rel < 0.8 else "Normal")
    if dalga == "Yüksek" or ay < -0.05:
        bas, met = "Borsa dalgalı. Bu hafta liste daha temkinli okunmalı.", ("Sert düşüş ve dalgalanma dönemlerinde \"çok yükselen daha da "
                                                                             "yükselir\" mantığı sık bozulur. İşlerin iyileşmesine daha çok önem verin.")
    elif ay > 0.03 and yil > 0.10:
        bas, met = "Borsa yükseliş eğiliminde.", "Genel hava olumlu; yine de tek bir hisseye büyük pay ayırmamak gerekir."
    else:
        bas, met = "Borsa sakin.", "Belirgin bir yön yok; listedeki işaretler normal ağırlığıyla okunabilir."
    return {"ay": float(ay), "yil": float(yil), "dalga": dalga, "baslik": bas, "metin": met}


class Hafta:
    def __init__(self, v: Veri, ayar: dict, profil: pd.DataFrame):
        self.v, self.ayar, self.profil = v, ayar, profil
        sec = build_identity()["securities"]
        self.sec = sec.assign(cik=sec.cik.astype(str)).drop_duplicates("cik").set_index("cik")
        f = archive.load("filings", columns=["cik", "form", "items", "accepted", "filing_date"])
        self.f = f[f.form == "8-K"].assign(cik=f.cik.astype(str))
        self.lift = {}

    def sembol(self, c: str) -> str:
        return str(self.sec.symbol.get(c, c))

    def isaret_metni(self, t, c) -> tuple[dict, dict]:
        i = self.v.isaret
        g = lambda n: i[n].at[t, c] if c in i[n].columns else np.nan
        mom, zir, dip = g("momentum_sira"), g("zirve_uzaklik"), g("dip_kat")
        gel, ivm = g("gelir_buyume"), g("gelir_ivme")
        sek_etf = self.v.sektor.get(c, "IWM")
        alici = g("alici_sayisi_90g")
        gun = g("son_rapordan_gun")
        metin = {
            "yukselis": f"Son 1 yılda evrendeki hisselerin %{site.ayrilma(round(mom * 100)) if pd.notna(mom) else '—'} çok yükseldi; "
                        f"52 haftalık zirvesine uzaklığı {_y(zir)}.",
            "is_iyilesiyor": (f"Son raporda satışlar geçen yılın aynı dönemine göre {_y(gel)}; önceki rapora göre büyüme "
                              f"{'hızlandı' if pd.notna(ivm) and ivm > 0 else 'yavaşladı'}." if pd.notna(gel) else "Satış verisi yok."),
            "dipten_kalkti": f"Fiyatı 52 haftalık en düşük seviyesinin {dip:.1f} katı.".replace(".", ",", 1) if pd.notna(dip) else "Fiyat geçmişi kısa.",
            "sektor": f"Sektörü ({SEKTOR_ADI.get(sek_etf, sek_etf)}) son 1 yılda {_y(g('sektor_12_1'))}; borsa {_y(g('spy_12_1'))}.",
            "iceriden": ("; ".join(x for x in [f"son 90 günde {int(alici)} yönetici/ortak borsadan hisse aldı" if pd.notna(alici) and alici > 0 else "",
                                                "yeni aktivist yatırımcı (13D)" if g("aktivist_13d") else "",
                                                "büyük bir yatırımcı yeni %5+ ortak oldu (13G)" if g("yeni_13g") else ""] if x)
                         or "son 90 günde yönetici alımı ya da yeni büyük ortak yok."),
            "yakin_haber": (f"Son rapordan bu yana {int(gun)} gün geçti; sonraki bilanço yaklaşık {max(0, round((91 - gun) / 7))} hafta içinde bekleniyor."
                            if pd.notna(gun) else "Rapor takvimi bilinmiyor."),
        }
        yok = {"yukselis": "Yükseliş zayıf", "is_iyilesiyor": "İşlerde belirgin iyileşme yok", "dipten_kalkti": "Dibe yakın",
               "sektor": "Sektörü borsanın gerisinde", "iceriden": "İçeriden alım yok", "yakin_haber": "Yakında bilanço yok"}
        metin["iceriden"] = metin["iceriden"][:1].upper() + metin["iceriden"][1:]
        return metin, yok

    def aciklamalar(self, t, c, gun=30) -> list[dict]:
        cut_hi = t - pd.Timedelta(days=1) + pd.Timedelta(hours=16)
        x = self.f[(self.f.cik == c)]
        acc = x.accepted.dt.tz_localize(None)
        x = x[(acc <= cut_hi) & (acc > cut_hi - pd.Timedelta(days=gun))].sort_values("accepted", ascending=False)
        out = []
        for r in x.itertuples():
            ms = [MADDE[m] for m in re.findall(r"\d\.\d\d", r.items or "") if m in MADDE]
            if ms:
                out.append({"tarih": f"{r.filing_date:%d.%m}", "ne": "Şirket " + ", ".join(dict.fromkeys(ms)) + "."})
        return out[:5]

    def benzer(self, t, c) -> dict | None:
        code = sum(int(self.v.isaret[n].at[t, c]) << k for k, n in enumerate(isaretler.OLUMLU))
        if code not in self.profil.index:
            return None
        r = self.profil.loc[code]
        if r.adet < 200:
            return None
        return {"adet": int(r.adet), "adet_metni": f"{int(r.adet):,}".replace(",", "."), **{k: float(r[k]) for k in
                ["borsayi_gecen_3a", "borsayi_gecen_6a", "kazanan_3a", "kazanan_6a", "sert_kayip_3a", "medyan_3a", "medyan_6a"]}}

    def almamali(self, t, c) -> list[str]:
        i = self.v.isaret
        out = []
        g26 = i["getiri_26h"].at[t, c]
        if pd.notna(g26) and g26 > 0.8:
            out.append(f"Son 6 ayda zaten {_y(g26)} yükseldi. Sert bir geri çekilme olabilir; tek seferde büyük para koymamak gerekir.")
        txt = {"hisse_basma": "Yeni hisse satışı belgesi var ya da hisse sayısı 1 yılda %20'den fazla arttı: mevcut ortakların payı küçülebilir.",
               "ters_bolunme": "Son 1 yılda ters bölünme yaptı; bu genelde fiyatı kurtarma çabasıdır.",
               "nakit_sikintisi": "Faaliyetleri nakit yakıyor ve kasası 4 çeyreklik yakıma yetmiyor; yakında borç ya da hisse satışı gelebilir.",
               "dusen_bicak": "Zirvesinden %70'ten fazla aşağıda ve düşüşü sürüyor.",
               "ucuzluk_tuzagi": "Satışları düşüyor ve zararı büyüyor: ucuz görünse de tuzak olabilir."}
        out += [txt[n] for n in isaretler.DIKKAT if i[n].at[t, c]]
        if i["devamlilik"].at[t, c]:
            out.append("Son yıllık raporunda ayakta kalma şüphesi dile getirildi; şirket zarar ediyor ve nakit yakıyor.")
        if i["gec_rapor"].at[t, c]:
            out.append("Son 6 ayda mali tablolarını zamanında açıklayamadığını bildirdi.")
        if not i["is_iyilesiyor"].at[t, c]:
            out.append("Satışlarda belirgin bir hızlanma yok; yükseliş beklentiye dayanıyor olabilir.")
        return out or ["Belirgin bir risk işareti yok; yine de her hisse beklenmedik haberle sert düşebilir."]

    def vade(self, b: dict | None, h: str) -> str:
        if not b:
            return "Benzer örnek az; geçmiş sonuç gösterilmiyor."
        return f"Benzerlerinin {site.oran_metni(b[f'borsayi_gecen_{h}'], True)} borsayı geçti; ortadaki hisse {site.yuzde(b[f'medyan_{h}'])}."

    def kart(self, t, c, sira, onceki: list[str]) -> dict:
        v = self.v
        i = v.isaret
        isa = {n: bool(i[n].at[t, c]) for n in isaretler.OLUMLU}
        metin, yok = self.isaret_metni(t, c)
        var = [n for n in isaretler.OLUMLU if isa[n]]
        oz = {"yukselis": "yükselişi sürüyor", "is_iyilesiyor": "satışları hızlanarak artıyor", "dipten_kalkti": "dipten güçlü kalktı",
              "sektor": "sektörünün rüzgârı arkasında", "iceriden": "yöneticileri ya da büyük yatırımcılar alıyor",
              "yakin_haber": "bilançosu yaklaşıyor"}
        g = lambda n: i[n].at[t, c]
        somut = {"yukselis": f"1 yılda hisselerin %{site.ayrilma(round(g('momentum_sira') * 100))} çok yükseldi" if pd.notna(g("momentum_sira")) else oz["yukselis"],
                 "is_iyilesiyor": f"satışları {_y(g('gelir_buyume'))} arttı ve hızlanıyor" if pd.notna(g("gelir_buyume")) else oz["is_iyilesiyor"],
                 "dipten_kalkti": f"dibinin {g('dip_kat'):.1f} katında".replace(".", ",") if pd.notna(g("dip_kat")) else oz["dipten_kalkti"],
                 "sektor": f"sektörü 1 yılda {_y(g('sektor_12_1'))}", "iceriden": oz["iceriden"], "yakin_haber": oz["yakin_haber"]}
        sira_w = sorted(var, key=lambda n: -self.ayar["agirlik"].get(n, 0))
        neden = "; ".join(somut[n] for n in sira_w[:3])
        neden = neden[:1].upper() + neden[1:] if neden else "İşaret sayısı düşük"
        b = self.benzer(t, c)
        pdg = v.tablo["piyasa_degeri"].at[t, c]
        sek = SEKTOR_ADI.get(v.sektor.get(c, "IWM"), "Diğer")
        degisim = "Aynı yerde" if c in onceki and onceki.index(c) + 1 == sira else (
            "Yeni girdi" if c not in onceki else (f"{onceki.index(c) + 1 - sira} sıra yükseldi" if onceki.index(c) + 1 > sira
                                                  else f"{sira - onceki.index(c) - 1} sıra düştü"))
        ac = self.aciklamalar(t, c)
        ayr = (f"momentum sırası {i['momentum_sira'].at[t, c]:.2f} · zirveye uzaklık {i['zirve_uzaklik'].at[t, c]:.3f} · dipten kat "
               f"{i['dip_kat'].at[t, c]:.2f} · gelir büyümesi {i['gelir_buyume'].at[t, c]:.3f} · ivme {i['gelir_ivme'].at[t, c]:.3f} · "
               f"sektör ETF {v.sektor.get(c)} 12-1 {i['sektor_12_1'].at[t, c]:.3f} (SPY {i['spy_12_1'].at[t, c]:.3f}) · "
               f"90 günde alıcı {i['alici_sayisi_90g'].at[t, c]:.0f} · son rapordan gün {i['son_rapordan_gun'].at[t, c]:.0f} · "
               f"piyasa değeri {pdg:,.0f} $ · işlem tutarı {v.tablo['islem_tutari'].at[t, c]:,.0f} $/gün · CIK {c}")
        ad = _ad(self.sec.name.get(c, ""))
        return {"sira": sira, "cik": c, "sembol": self.sembol(c), "ad": ad, "sektor": sek, "buyukluk": _buyukluk(pdg),
                "neden": neden + ".", "ozet": f"{ad}: {neden.lower()}.", "isaretler": isa, "olumlu": len(var),
                "isaret_metni": metin, "isaret_yok": yok, "benzer": b, "vade_3a": self.vade(b, "3a"), "vade_6a": self.vade(b, "6a"),
                "degisim": degisim, "dikkat": [n for n in isaretler.DIKKAT + isaretler.KESIN_RET if i[n].at[t, c]], "yeni_aciklama": bool(ac),
                "aciklamalar": ac, "almamali": self.almamali(t, c), "ayrinti": ayr.replace("nan", "—")}

    def alinmaz(self, t, n=5) -> dict:
        v, i = self.v, self.v.isaret
        ok = v.tablo["evren"].loc[t]
        liq = v.tablo["islem_tutari"].loc[t].where(ok).dropna().sort_values(ascending=False)
        kes, dik = [], []
        txt_k = {"devamlilik": "Son yıllık raporunda ayakta kalma şüphesi dile getirildi; şirket zarar ediyor ve nakit yakıyor.",
                 "gec_rapor": "Mali tablolarını zamanında açıklayamadığını bildirdi (son 6 ay)."}
        txt_d = {"dusen_bicak": "Zirvesinden %70'ten fazla aşağıda ve düşüş sürüyor.",
                 "ucuzluk_tuzagi": "Satışları düşüyor ve zararı büyüyor: ucuzluk tuzağı olabilir.",
                 "hisse_basma": "Yeni hisse satıyor ya da hisse sayısı hızla arttı; parayı neye harcayacağına bakılmalı.",
                 "ters_bolunme": "Son 1 yılda ters bölünme yaptı.",
                 "nakit_sikintisi": "Nakit yakıyor; kasası 1 yıla yetmeyebilir."}
        for c in liq.index:
            ks = [k for k in isaretler.KESIN_RET if i[k].at[t, c]]
            if ks and len(kes) < n:
                kes.append({"sembol": self.sembol(c), "neden": " ".join(txt_k[k] for k in ks)})
            ds = [k for k in ("dusen_bicak", "ucuzluk_tuzagi", "nakit_sikintisi", "hisse_basma", "ters_bolunme") if i[k].at[t, c]]
            if ds and not ks and len(dik) < n and (len(ds) >= 2 or ds[0] in ("dusen_bicak", "ucuzluk_tuzagi")):
                dik.append({"sembol": self.sembol(c), "neden": " ".join(txt_d[k] for k in ds[:2])})
            if len(kes) >= n and len(dik) >= n:
                break
        return {"kesin": kes, "dikkat": dik}

    def yaklasan(self, t, ciks: list[str]) -> list[dict]:
        out = []
        for c in ciks:
            gun = self.v.isaret["son_rapordan_gun"].at[t, c]
            if pd.notna(gun) and 63 <= gun <= 100:
                d = t + pd.Timedelta(days=int(91 - gun))
                out.append({"tarih": f"~{d:%d.%m}", "sembol": self.sembol(c), "ne": "Çeyreklik sonuçlarını açıklaması bekleniyor"})
        return sorted(out, key=lambda x: x["tarih"])[:6]


def karne_verisi(v: Veri, ayar: dict, h: Hafta) -> dict:
    bloklar = []
    ay = json.loads(analiz.AYAR_DOSYA.read_text())
    sec_k = next(d["karne"] for d in ay["defter"] if d["ayar"]["ad"] == ayar["ad"])
    bloklar.append({"baslik": "Ayar dönemi · 2013–2022", "aciklama": "Kurallar bu yıllarla ayarlandı; bu yüzden sonuçlar iyimser olabilir.", "ozet": sec_k})
    if SINAV_DOSYA.exists():
        s = json.loads(SINAV_DOSYA.read_text())
        bloklar.insert(0, {"baslik": "Sınav dönemi · 2023–2026", "aciklama": "Ayarlar dondurulduktan sonra bir kez açıldı; aracın görmediği yıllar.",
                           "ozet": s["karne"]})
    # Liste liste: son çeyrek başları (sınav ve sonrası)
    listeler = []
    qs = analiz.ceyrek_baslari(v.tarihler, (2023, 2026))
    ls = analiz.liste(v, ayar, qs)
    kaz = v.kazanan("3a")
    for t in list(qs)[::-1][:8]:
        picks = ls.get(t, [])
        n3 = v.tablo["net_3a"].loc[t, picks] if picks else pd.Series(dtype=float)
        if n3.isna().all():
            continue
        n6 = v.tablo["net_6a"].loc[t, picks] if picks else pd.Series(dtype=float)
        b3 = v.tablo["brut_3a"].loc[t].where(v.tablo["evren"].loc[t]).nlargest(3).mean()
        k = int(kaz.loc[t, picks].sum())
        listeler.append({"tarih": f"{t:%d.%m.%Y}", "bizim_3a": float(n3.mean()), "borsa_3a": float(v.tablo["kiyas_3a"].at[t, "borsa"]),
                         "en_iyi3_3a": float(b3), "bizim_6a_metni": "henüz yok" if n6.isna().all() else
                         f"{site.yuzde(float(n6.mean()))} (borsa {site.yuzde(float(v.tablo['kiyas_6a'].at[t, 'borsa']))})",
                         "yakalanan": f"En iyilerden {k} hisse" if k else "En iyilerden hiçbiri"})
    return {"bloklar": bloklar, "listeler": listeler}


def otopsi_verisi(v: Veri, ayar: dict, h: Hafta) -> dict:
    last = v.tablo["brut_3a"].dropna(how="all").index.max()
    qs = analiz.ceyrek_baslari(v.tarihler, (last.year - 1, last.year))
    q0 = max(t for t in qs if t <= last)
    pos = {t: i for i, t in enumerate(v.tarihler)}
    weeks = v.tarihler[pos[q0]: pos[q0] + 13]
    ls = analiz.liste(v, ayar, weeks)
    rows = analiz.otopsi(v, ls, (q0.year, q0.year), "3a", adet=10, ret=ayar.get("ret", []))
    rows = [r for r in rows if r["tarih"] == str(q0.date())]
    kartlar = []
    for k, r in enumerate(rows):
        c = r["cik"]
        sym = h.sembol(c)
        tur = "Haber sıçraması" if (r.get("tek_hafta_payi") or 0) >= 0.6 else (
            "İşler iyileşiyor" if r["kaynak_is"] else ("Tema dalgası" if r["kaynak_sektor"] else "Değerleme değişimi"))
        yak = r.get("yakalanabilir_net")
        caught = r.get("listeye_giris") is not None
        if r.get("ilk_isaret"):
            ozet = f"İlk güvenilir işaret {pd.Timestamp(r['ilk_isaret']):%d.%m}'de geldi."
            hukum, hn = ("Yakaladık." if caught else "Listede değildi."), (
                f"{pd.Timestamp(r['listeye_giris']):%d.%m} haftasında listeye girdi." if caught else "İşaretleri vardı ama sıralamada ilk 10'a giremedi.")
        else:
            ozet = "Çeyrek boyunca güvenilir işaret oluşmadı."
            hukum, hn = "Yakalanamazdı.", f"Sebep: {r.get('neden')}."
        detay = {"id": f"{q0:%Y%m%d}-{sym}", "sembol": sym, "tur": tur, "toplam": r["toplam"], "yakalanabilir": yak, "ozet": ozet,
                 "yakalandi": caught, "hukum": hukum, "hukum_neden": hn, "donem": f"{q0:%d.%m.%Y} başlayan çeyrek",
                 "ad": _ad(h.sec.name.get(c, "")), "sektor": SEKTOR_ADI.get(v.sektor.get(c, "IWM"), "Diğer")}
        if r.get("ilk_isaret"):
            s = pd.Timestamp(r["ilk_isaret"])
            ham_giris = v.tablo["ham_persembe"].at[s, c]
            oran = r["giris_fiyati_duz"] / v.tablo["fiyat_persembe"].at[s, c] if v.tablo["fiyat_persembe"].at[s, c] else 1
            giris_ham = ham_giris * oran
            detay["dort"] = {"tarih": f"{s - pd.Timedelta(days=1):%d.%m.%Y} (perşembe)", "isaret_fiyati": site.para(ham_giris),
                             "giris": site.para(giris_ham), "giris_not": f"{s:%d.%m} cuma kapanışı", "net_3a": r.get("net_3a"),
                             "net_6a": r.get("net_6a"), "fazla_borsa": r.get("fazla_borsa_3a"), "fazla_sektor": r.get("fazla_sektor_3a")}
            end_ham = giris_ham * (1 + r["yakalanabilir"])
            detay["yol"] = [{"etiket": "Çeyrek başı", "fiyat": "", "not": f"{q0:%d.%m}", "renk": "#9AA0A6"},
                            {"etiket": "İlk güvenilir işaret", "fiyat": site.para(ham_giris), "not": "Perşembe kapanışı; belgeler yayımlanmıştı.", "renk": "var(--yazi)"},
                            {"etiket": "Alınabilecek ilk fiyat", "fiyat": site.para(giris_ham), "not": "Rapor cuma çıkar; o günün kapanışından alınmış sayılır.", "renk": "var(--mavi)"},
                            {"etiket": "Çeyrek sonu", "fiyat": site.para(end_ham), "not": f"Yakalanabilir getiri: {site.yuzde(r['yakalanabilir'], True, 1)} (masraflı {site.yuzde(yak, True, 1)})", "renk": "var(--mavi)"}]
            detay["yol_ozet"] = (f"Çeyrekte toplam yükseliş {site.yuzde(r['toplam'])} görünüyor; alınabilecek ilk fiyattan getiri "
                                 f"{site.yuzde(r['yakalanabilir'])}.")
            bilinen = [{"var": True, "metin": analiz.ISARET_METNI[n] + "."} for n in r.get("isaretler", [])]
            bilinen += [{"var": False, "metin": ISARET_YOKTU[n] + "."} for n in isaretler.OLUMLU if n not in r.get("isaretler", [])][:2]
            detay["bilinen"] = bilinen
            sonra = ", ".join(f"{a} {site.yuzde(r.get(k_))}" for a, k_ in (("3 ayda", "net_3a"), ("6 ayda", "net_6a")) if r.get(k_) is not None)
            detay["ilk_metin"] = (f"İlk güvenilir işaret: {s - pd.Timedelta(days=1):%d.%m.%Y} perşembe. "
                                  + (f"O noktadan sonra {sonra}." if sonra else "Sonrası için 3 aylık süre henüz dolmadı."))
            if r.get("benzer_adet"):
                ayr = r.get("ayiran_isaret")
                ayr_txt = None
                if ayr:
                    ad = ISARET_AYIRAN.get(ayr, ayr)
                    ayr_txt = (f"Kazananda {ad} vardı; kaybeden benzerlerin çoğunda yoktu." if (r.get("ayiran_fark") or 0) > 0
                               else f"Kazananda {ad} yoktu; kaybeden benzerlerin çoğunda vardı.")
                neden = r.get("kaybedenlerde_sik_dikkat")
                detay["benzer"] = {"metin": f"O hafta aynı eşiği geçen {r['benzer_adet']} hisse daha vardı. {site.iyelik(r['benzer_gecen'])} borsadan çok kazandırdı, "
                                            f"{site.iyelik(r['benzer_sert_kayip'])} %20'den fazla değer kaybetti.",
                                   "ornek": [{"sembol": h.sembol(x["cik"]), "net": x["net"]} for x in r.get("benzer_ornek", [])],
                                   "ayiran": ayr_txt,
                                   "neden": (f"Kaybeden benzerlerin çoğunda (yüzde {round(r['kaybedenlerde_oran'] * 100)}) '{ISARET_AYIRAN.get(neden, neden)}' işareti vardı." if neden else None)}
        else:
            detay["bilinen"] = [{"var": False, "metin": f"Güvenilir işaret oluşmadı: {r.get('neden')}."}]
            detay["ilk_metin"] = "Bu hisse çeyrek boyunca aracın eşiğini geçmedi."
        detay["hikaye"] = ("Yükselişin büyük kısmı tek bir haftada geldi; büyük olasılıkla tek bir habere bağlı." if tur == "Haber sıçraması" else
                           "Satışları hızlanırken fiyat yükseldi." if tur == "İşler iyileşiyor" else
                           "Sektörüyle birlikte yükseldi." if tur == "Tema dalgası" else "Şirket verilerinde belirgin bir değişim olmadan yeniden fiyatlandı.")
        detay["kaynak"] = [("İşlerdeki gelişme", r["kaynak_is"]), ("Sektör hareketi", r["kaynak_sektor"]),
                           ("Değerleme değişimi", not r["kaynak_is"] and not r["kaynak_sektor"])]
        detay["tek_hafta"] = r.get("tek_hafta_payi")
        detay["tek_hafta_not"] = f"En büyük hafta: {pd.Timestamp(r['en_buyuk_hafta']):%d.%m}" if r.get("en_buyuk_hafta") else ""
        detay["ayrinti"] = json.dumps({k_: r[k_] for k_ in r if k_ not in ("benzer_ornek",)}, ensure_ascii=False, default=str)
        kartlar.append(detay)
    return {"donem_metni": f"{q0:%d.%m.%Y} başlayan çeyreğin", "kartlar": kartlar}


ISARET_YOKTU = {"yukselis": "Yükselişi sürmüyordu", "is_iyilesiyor": "Satışlarında hızlanma yoktu", "dipten_kalkti": "Dipten belirgin kalkmamıştı",
                "sektor": "Sektörü borsanın gerisindeydi", "iceriden": "İçeriden alım yoktu", "yakin_haber": "Yakında bilanço beklenmiyordu"}
ISARET_AYIRAN = {"yukselis": "yükselişin sürmesi", "is_iyilesiyor": "satışların hızlanması", "dipten_kalkti": "dipten kalkış",
                 "sektor": "sektör rüzgârı", "iceriden": "içeriden alım", "yakin_haber": "yaklaşan bilanço",
                 "hisse_basma": "hisse basma", "ters_bolunme": "ters bölünme", "nakit_sikintisi": "nakit sıkıntısı",
                 "dusen_bicak": "düşen bıçak", "ucuzluk_tuzagi": "ucuzluk tuzağı"}


def veri(t: pd.Timestamp | None = None) -> dict:
    v = Veri.yukle()
    ayar = analiz.secilen_ayar()
    profil = pd.DataFrame(json.loads(PROFIL.read_text())).set_index("kod")
    h = Hafta(v, ayar, profil)
    ok_dates = v.tablo["evren"].index[v.tablo["evren"].sum(axis=1) > 0]
    t = ok_dates.max() if t is None else t
    prev = ok_dates[ok_dates < t].max()
    ls = analiz.liste(v, ayar, pd.DatetimeIndex([prev, t]))
    picks, onceki = ls[t], ls[prev]
    kartlar = [h.kart(t, c, k + 1, onceki) for k, c in enumerate(picks)]
    cikan = []
    for c in onceki:
        if c in picks:
            continue
        i = v.isaret
        if bool(i["kesin_ret"].at[t, c]):
            n = "kesin ret işareti çıktı."
        elif bool(i["hisse_basma"].at[t, c]) and not bool(i["hisse_basma"].at[prev, c]):
            n = "yeni hisse satışı belgesi verdi."
        elif bool(i["yukselis"].at[prev, c]) and not bool(i["yukselis"].at[t, c]):
            n = "yükselişi zayıfladı."
        else:
            n = "işaretleri azaldı; yerini daha güçlü bir aday aldı."
        cikan.append({"sembol": h.sembol(c), "neden": n})
    out = {"tarih": str(t.date()), "tarih_metni": f"{t:%d.%m.%Y}, Cuma", "veri_metni": "Perşembe kapanış fiyatlarıyla",
           "piyasa": piyasa(v, t), "liste": kartlar, "cikanlar": cikan, "alinmaz": h.alinmaz(t),
           "yaklasan": h.yaklasan(t, picks), "karne": karne_verisi(v, ayar, h), "otopsi": otopsi_verisi(v, ayar, h),
           "ayar": ayar["ad"]}
    return out


def kilitle(v: dict) -> None:
    CANLI.mkdir(parents=True, exist_ok=True)
    path = CANLI / f"{v['tarih']}.json"
    if path.exists():
        return  # kilitli kayıt değiştirilmez
    path.write_text(json.dumps({"tarih": v["tarih"], "ayar": v["ayar"], "liste": [{"sira": x["sira"], "cik": x["cik"], "sembol": x["sembol"]}
                                                                                  for x in v["liste"]]}, ensure_ascii=False, indent=1))


def main():
    v = veri()
    kilitle(v)
    out = site.yaz(v)
    print(f"{out} · {v['tarih']} · {len(v['liste'])} hisse")


if __name__ == "__main__":
    main()

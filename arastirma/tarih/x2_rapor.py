"""x2_analiz sonuclarindan iki md dosyasi uretir (repo kokune):
  SP500-X2-HISSELER.md             : bulunan hisse listesi
  SP500-X2-KATEGORI-ESLESTIRME.md  : 40 kategori, eslesme, hisse hikayeleri, ozet"""
from pathlib import Path

import numpy as np
import pandas as pd

from tarih.x2_analiz import HIKAYE, KAT, kategoriler, ozellikler

KOK = Path(__file__).resolve().parents[2]
SEKTOR = {"Semiconductors": "Yarı iletken", "Technology": "Teknoloji", "Electrical Equipment": "Elektrik ekipmanı",
          "Aerospace & Defense": "Havacılık ve savunma", "Communications": "İletişim ağı", "Machinery": "Makine", "Metals & Mining": "Madencilik",
          "Energy": "Enerji", "Banking": "Bankacılık", "Retail": "Perakende", "Hotels, Restaurants & Leisure": "Seyahat ve eğlence",
          "Building": "Bina sistemleri", "Automobiles": "Otomotiv", "Health Care": "Sağlık", "Media": "Medya/internet", "Biotechnology": "Biyoteknoloji",
          "Financial Services": "Finansal hizmet", "": "bilinmiyor"}
# S&P 500 uyeligi: repo dogrulayamiyor; HAFIZAYA GORE
SP_UYE = {t: "evet" for t in "NVDA AMD MU WDC STX PLTR HOOD APP AVGO LRCX KLAC AMAT TER HPE ANET GE CAT NEM MPC C BK PANW EBAY EXPE JCI FTNT GM NTAP KEYS CAH GOOGL GOOG APH GLW HWM FFIV".split()}
SP_UYE.update({t: "hayır" for t in "RGTI QBTS AXTI ZYME SITM FORM".split()})
SP_UYE.update({t: "emin değilim" for t in "COHR TWLO".split()})
# Hafizaya gore arka plan (DOGRULANMADI; repoda haber yok). Sadece genis temalar + hatirladigim birkac olay.
HAFIZA = {
    "AXTI": "Yapay zekâ veri merkezlerinin optik bağlantılarında kullanılan indiyum fosfat altlık üreticisi; çok küçük bir şirketin tema talebiyle sıçraması. Yükseliş çok sert, değerleme aşırı.",
    "QBTS": "Kuantum bilişim temasının spekülatif adlarından; geliri küçük, zararı büyük. Yükseliş temaya ve büyük olasılıkla sermaye artırımlarına dayanıyor; temel veri bunu desteklemiyor.",
    "PLTR": "Yapay zekâ yazılım platformu ve devlet/savunma müşterileri; zarardan güçlü kârlılığa geçiş hikâyesi.",
    "MU": "Yapay zekâ için yüksek bant genişlikli bellek talebi ve bellek fiyat döngüsünün yukarı dönmesi.",
    "WDC": "Depolama döngüsü ve yapay zekâ veri merkezi talebi. Şubat 2025'te SanDisk'in ayrılması (spin-off) hikâyenin parçası (K34, hafızadan).",
    "HOOD": "Bireysel yatırımcı işlem hacmi ve kripto canlanması; 2025'te S&P 500'e girdiğini hatırlıyorum (K35, hafızadan).",
    "RGTI": "Kuantum bilişim teması; spekülatif, zarar büyük. Yükseliş temaya dayanıyor.",
    "STX": "Depolama döngüsü ve yapay zekâ veri merkezi diski talebi.",
    "COHR": "Optik iletişim bileşenleri; yapay zekâ veri merkezi bağlantı talebi.",
    "APP": "Mobil reklam teknolojisi; yapay zekâ reklam motoru ile marj sıçraması. 2025'te S&P 500'e girdiğini hatırlıyorum (K35, hafızadan).",
    "AMD": "Yapay zekâ hızlandırıcıları ve sunucu işlemcileri.",
    "NVDA": "Yapay zekâ eğitim ve çıkarım çipleri; yapay zekâ altyapı dalgasının merkezi.",
    "SITM": "Zamanlama çipleri; yapay zekâ ağ ve veri merkezi talebi.",
    "HWM": "Uçak motoru ve havacılık parçaları; sipariş birikimi ve fiyatlama gücü.",
    "GLW": "Fiber optik kablo; yapay zekâ veri merkezi bağlantı talebi.",
    "TWLO": "İletişim platformu; maliyet disiplini ve kârlılığa dönüş.",
    "LRCX": "Çip üretim ekipmanı; bellek ve yapay zekâ yatırım döngüsü.",
    "APH": "Konnektör ve kablo; yapay zekâ veri merkezi, savunma ve otomotiv talebi.",
    "AVGO": "Yapay zekâ özel çipleri ve ağ çipleri.",
    "TER": "Çip test ekipmanı; yapay zekâ çipi test talebi.",
    "HPE": "Sunucu ve ağ; Juniper Networks alımı (2025) ve yapay zekâ ağ talebi.",
    "KLAC": "Çip üretim denetim ekipmanı; yapay zekâ ve gelişmiş paketleme yatırımları.",
    "ZYME": "Biyoteknoloji; klinik veri ve ortaklık haberlerine bağlı olduğunu tahmin ediyorum (belirsiz).",
    "GE": "GE Vernova ayrılmasından (Nisan 2024) sonra saf havacılık şirketi; uçak motoru servis geliri (K34, hafızadan).",
    "ANET": "Veri merkezi ağ anahtarları; bulut ve yapay zekâ yatırımları.",
    "BK": "Büyük banka/saklama kuruluşu; faiz ortamı, hizmet gelirleri ve hisse geri alımları (belirsiz).",
    "FORM": "Yarı iletken test probe kartları; yapay zekâ bellek (HBM) test talebi.",
    "CAT": "İnşaat/madencilik makineleri; veri merkezi için enerji jeneratörü talebi (belirsiz).",
    "NEM": "Altın madencisi; altın fiyatı yükselişi ve maliyet disiplini.",
    "FFIV": "Ağ ve uygulama güvenliği yazılımı; yapay zekâ trafiği ve yenileme döngüsü (belirsiz).",
    "MPC": "Rafineri; rafineri marjları ve hisse geri alımları (belirsiz).",
    "AMAT": "Çip üretim ekipmanı; yapay zekâ ve bellek yatırım döngüsü.",
    "C": "Büyük banka; yeniden yapılanma ve getiri hedefleri (belirsiz).",
    "PANW": "Siber güvenlik platformu; yapay zekâ güvenlik talebi ve ürün birleştirme.",
    "EBAY": "Pazar yeri; maliyet disiplini, kârlılık ve hisse geri alımları (belirsiz).",
    "EXPE": "Seyahat; maliyet kesintisi ve verimlilik (belirsiz).",
    "JCI": "Bina sistemleri; veri merkezi soğutma talebi.",
    "FTNT": "Siber güvenlik; güvenlik duvarı yenileme döngüsü.",
    "GM": "Otomotiv; maliyet disiplini ve hisse geri alımları (belirsiz).",
    "NTAP": "Depolama; yapay zekâ veri hazırlığı talebi.",
    "KEYS": "Test ve ölçüm cihazları; yapay zekâ/veri iletişimi ve savunma.",
    "CAH": "İlaç dağıtımı; kârlılık ve hisse geri alımları (belirsiz).",
    "GOOGL": "Yapay zekâ endişelerinden toparlanma ve bulut büyümesi. (GOOG aynı şirketin ikinci hisse sınıfı.)",
}
KAD = {k[0]: k[1] for k in KAT}


def p(x, d=0):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    return f"{'−' if x < 0 else ''}%{abs(x)*100:.{d}f}"


def sayi(x, d=0):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{d}f}"


def hikaye(r):
    s = [f"3 yılda %{r.ret3*100:,.0f} ({r.kat:.1f} kat S&P 500). Pencere başında (Ekim 2023) kendi önceki zirvesinin %{abs(r.dd0)*100:.0f} altındaydı; "
         f"2022'de (Ara 2021→Eyl 2022) {p(r.kay22)}.",
         f"En büyük 12 aylık dalga {r.en_iyi_bitis[:7]} ayında bitti (+%{r.en_iyi_12*100:,.0f}); yolda en kötü düşüş %{abs(r.mdd)*100:.0f}. "
         f"2025 tarife düşüşünde zirveden nisana {p(r.d25)}, sonraki 5 ayda {p(r.f25)}. Şu an pencere zirvesinin %{abs(r.son_dd)*100:.0f} altında."]
    t = []
    if not np.isnan(r.revG if r.revG is not None else np.nan): t.append(f"satış büyümesi %{r.revG:.0f}")
    if r.gmT is not None and not np.isnan(r.gmT) and r.gm5 is not None and not np.isnan(r.gm5): t.append(f"brüt marj %{r.gmT:.0f} (5 yıl önce %{r.gm5:.0f})")
    if r.netM is not None and not np.isnan(r.netM): t.append(f"net marj %{r.netM:.0f}")
    if r.pe is not None and not np.isnan(r.pe): t.append(f"F/K {r.pe:.0f}")
    if r.mcap is not None and not np.isnan(r.mcap): t.append(f"piyasa değeri {r.mcap/1000:,.0f} milyar $")
    if t: s.append("Bugünkü temel veri: " + ", ".join(t) + ".")
    return " ".join(s)


def uret():
    df, sp, son = ozellikler()
    df = kategoriler(df)
    w = df[df.kazanan].sort_values("ret3", ascending=False).reset_index(drop=True)
    wt, ot = w[w.tekil], df[(~df.kazanan) & df.tekil]
    n_ev = len(df)
    esik = 2 * sp
    # ------------------------------------------------ dosya 1
    L = ["# S&P 500'ü en az 2 kat geride bırakan hisseler (son 3 yıl)", "",
         f"> Bu liste, elimizdeki veriyle yapılabilen **en iyi yaklaşıktır**; S&P 500'ün tamamı değildir (aşağıdaki sınırlara bak). Yatırım tavsiyesi değildir.", "",
         "## Ölçüt",
         f"- Dönem: 31 Ekim 2023 → Ekim 2026 (son ay tamamlanmamış olabilir).",
         f"- S&P 500 getirisi (SPY fonu ile ölçüldü): **%{sp*100:.0f}**. Bir hisse, 3 yıllık getirisi bunun **en az 2 katıysa** (yani en az **%{esik*100:.0f}**) listeye girer.",
         f"- Alternatif okuma, \"fiyatını ikiye katladı\" (≥ %100), daha geniş bir küme verirdi; **bu dosya \"S&P 500'ün 2 katı\" okumasını kullanır.**", "",
         "## Sınırlar (önce bunları oku)",
         f"1. **Tüm S&P 500 değil.** Fiyat geçmişi yalnızca taranan **{n_ev} hissede** var (gece taramasının adayları ve izleme listesi). Gerçek S&P 500'de bunlara ek kazananlar olabilir.",
         "2. **Kazananlara doğru yanlı.** Bu 156 hisse tarama adayı olarak seçilmiş; dolayısıyla listenin kazanan oranı gerçek S&P 500'ünkinden yüksektir. Bu dosya \"S&P 500'ün %X'i kazandı\" demek için kullanılamaz.",
         "3. **S&P 500 üyeliği repodan doğrulanamıyor.** Üyelik sütunu hafızama göredir. Listede S&P 500 dışı olan küçük şirketler var (RGTI, QBTS, AXTI, ZYME, SITM, FORM).",
         "4. **Hayatta kalan yanlılığı:** Bugün hâlâ listede olan şirketler var; bu dönemde batan ya da çıkarılanlar yok.", "",
         f"## Liste: {len(w)} hisse ({len(wt)} şirket)", "",
         "GOOG ile GOOGL aynı şirketin iki hisse sınıfıdır; istatistiklerde bir kez sayılır.", "",
         "| # | Sembol | Şirket | Sektör | 3 yıllık getiri | S&P 500'ün katı | S&P 500 üyesi? (hafıza) | Piyasa değeri (milyar $) |", "|---|---|---|---|---|---|---|---|"]
    for i, r in w.iterrows():
        L.append(f"| {i+1} | {r.sembol} | {r.ad} | {SEKTOR.get(r.sektor, r.sektor)} | %{r.ret3*100:,.0f} | {r.kat:.1f}× | {SP_UYE.get(r.sembol, 'emin değilim')} | {sayi(r.mcap/1000 if r.mcap else np.nan)} |")
    L += ["", "## Hızlı bakış", "",
          f"- **{len(wt)} şirket** kriteri geçti ({len(w)} hisse, GOOG/GOOGL aynı şirket).",
          f"- Taranan {n_ev} hissenin {len(w)} tanesi (%{len(w)/n_ev*100:.0f}) geçti: yanlı örneklem olduğundan bu oranı genelleme.",
          "- Sektör dağılımı (şirket sayısı): " + ", ".join(f"{SEKTOR.get(k, k)} {v}" for k, v in wt.groupby('sektor').size().sort_values(ascending=False).items()) + ".",
          f"- En yüksek 5: " + ", ".join(f"{r.sembol} (%{r.ret3*100:,.0f})" for _, r in w.head(5).iterrows()) + ".",
          "", "Kategori eşleştirmesi ve hisse hikâyeleri: `SP500-X2-KATEGORI-ESLESTIRME.md`.",
          "", "_Üretim: `arastirma/tarih/x2_analiz.py` ve `x2_rapor.py` (dal: `claude/mekanizma-arastirma`); veri: `data/sonuclar.json`._"]
    (KOK / "SP500-X2-HISSELER.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ------------------------------------------------ dosya 2
    M = ["# S&P 500'ü 2 kat geride bırakan hisseler: kategori eşleştirmesi ve hikâyeler", "",
         "> Liste için: `SP500-X2-HISSELER.md`. Kategoriler: `DIPTEN-TOPARLANMA-BELIRTILERI.md` belgesindeki ~40 belirtinin çalışma versiyonu. Yatırım tavsiyesi değildir.", "",
         "## Nasıl okunmalı (önce bunlar)", "",
         "- **40 kategorinin yalnızca 22'si eldeki veriyle ölçülebiliyor.** Kalan 18'i (haber, nakit ömrü, borç, geri alım, açığa satış, spin-off, endeks girişi…) için hiçbir hisse etiketlenemedi; bu \"yok\" demek değil, **\"bilmiyoruz\"** demek.",
         "- **Hiçbiri** = ölçülebilir \"hikâye\" kategorilerinin (K01, K02, K03, K05, K07, K08, K10, K11, K19, K20, K21) hiçbirine uymuyor. Bu örnekte hiçbir kazanan \"hiçbiri\" çıkmadı; kategoriler geniş olduğu için bu tek başına bilgi taşımayabilir, bu yüzden ≤2 kategorili **zayıf eşleşme** de ayrıca verildi.",
         "- **Temel veri (satış büyümesi, marj, F/K, bilanço sürprizi, içeriden alım) bugünün anlık görüntüsü.** Yükselişten *sonraki* durumu gösterir; \"yükselmeden önce bu belirti vardı\" diye okunamaz.",
         "- Bazı kategoriler kazanmanın kendisinden türediği için kazananlarda zaten yüksek çıkar (K01, K05, K08, K21). **Sızıntısız tek bilgi, pencere başlamadan önceki durumdur** (K03, K04).",
         "- Eşikleri ben koydum, **ama koymadan önce bu hisselerin rakamlarına bakmıştım**; eşikler ayarlı sayılmalı, tarafsız bir test değil.",
         "- Örneklem yanlı (bkz. `SP500-X2-HISSELER.md`). Aşağıdaki oranlar betimseldir, kanıt değildir.", "",
         "## 1. Kategori kataloğu (40)", "", "| Kod | Kategori | Ölçülebildi mi? | Kural ya da neden ölçülemedi |", "|---|---|---|---|"]
    for kod, ad, g, ol, kural in KAT:
        M.append(f"| {kod} | {ad} | {'evet' if ol else '**hayır**'} | {kural} |")
    M += ["", "## 2. Özet: kazananlarda hangi belirtiler daha sık?", "",
          f"Kazanan {len(wt)} şirket ve kazanamayan {len(ot)} hisse (aynı örneklemden, GOOG tek sayıldı) aynı kurallardan geçirildi.", "",
          "| Kod | Kategori | Kazananlarda | Diğerlerinde | Not |", "|---|---|---|---|---|"]
    NOT = {"K01": "kısmen mekanik (aynı dönemin getirisiyle ilişkili)", "K03": "**sızıntısız** (pencere öncesi)", "K04": "**sızıntısız** (pencere öncesi)",
           "K05": "kısmen mekanik", "K08": "kısmen mekanik", "K10": "bugünkü veri (sonuç)", "K11": "bugünkü veri (sonuç)", "K15": "bugünkü veri (sonuç)",
           "K16": "bugünkü veri (sonuç)", "K19": "bugünkü veri", "K20": "kimsede yok, doğrulanamadı", "K21": "kazananların kendisinden türetildi (döngüsel)",
           "K17": "bugünkü piyasa değeri (kazanmanın sonucu)", "K18": "bugünkü piyasa değeri"}
    js = {}
    for kod, ad, g, ol, kural in KAT:
        if not ol:
            continue
        a = sum(kod in k for k in wt.kategoriler) / len(wt)
        b = sum(kod in k for k in ot.kategoriler) / len(ot)
        js[kod] = (a, b)
        M.append(f"| {kod} | {ad} | {p(a)} | {p(b)} | {NOT.get(kod, '')} |")
    ort_w, ort_o = wt.hikaye.str.len().mean(), ot.hikaye.str.len().mean()
    zayif = w[(w.hikaye.str.len() <= 2) & w.tekil]
    hic = w[(w.hikaye.str.len() == 0) & w.tekil]
    M += ["", "### Ana bulgular", "",
          f"1. **Önceki ayı piyasasında cezalandırılmış olmak (sızıntısız):** pencere başında kendi zirvesinden ≥%35 aşağıda olanlar kazananlarda {p(js['K03'][0])}, diğerlerinde {p(js['K03'][1])}. "
          f"2022'de piyasadan dayanıklı olanlar kazananlarda yalnızca {p(js['K04'][0])}, diğerlerinde {p(js['K04'][1])}. **Yani büyük kazananların çoğu 2022'de en çok dayak yiyenler arasındaydı.** Bu, \"dipten toparlanma\" hikâyesiyle uyumlu; yine de örneklem yanlı.",
          f"2. **Şokta toparlanma (2025 tarife düşüşü):** şokta ≥%10 düşüp sonraki 5 ayda ≥%25 toparlayanlar kazananlarda {p(js['K01'][0])}, diğerlerinde {p(js['K01'][1])}. Kısmen mekanik, ama \"şokta düşenler sonra çok toparladı\" hikâyesi kazananların yaklaşık yarısında var.",
          f"3. **Şokta dayanıklılık (gizli güç) kazananları ayırmıyor:** kazananlarda {p(js['K02'][0])}, diğerlerinde {p(js['K02'][1])}. Dayanıklı olmak ile büyük kazanmak aynı şey değil.",
          f"4. **Tema:** yarı iletken ya da teknoloji sektöründe olanlar kazananlarda {p(js['K21'][0])}. En kalabalık sektörler: " + ", ".join(f"{SEKTOR.get(k, k)} {v}" for k, v in wt.groupby('sektor').size().sort_values(ascending=False).head(4).items()) + f"; geri kalan {int((wt.groupby('sektor').size().sort_values(ascending=False).iloc[4:]).sum())} şirket çok sayıda farklı sektöre dağılıyor. Büyük çoğunluk **yapay zekâ altyapısı** (çip, ekipman, bellek/depolama, bağlantı, ağ) temasına bağlanıyor (hafızaya göre).",
          f"5. **Satış büyümesi ≥%20:** kazananlarda {p(js['K10'][0])}, diğerlerinde {p(js['K10'][1])}. Bugünkü veri olduğu için \"neden yükseldi\"yi açıklar, \"yükselmeden önce işaretti\" değil.",
          f"6. **Pahalı değerleme:** kazananlarda {p(js['K15'][0])}, diğerlerinde {p(js['K15'][1])}; makul/ucuz olanlar kazananlarda daha seyrek ({p(js['K16'][0])} ve {p(js['K16'][1])}). **\"Ucuz\" olmak kazanmayı öngörmedi.**",
          f"7. **İçeriden alım:** hiçbirinde yok. Bugünkü anlık görüntüden bu belirtiyi bu örnekte doğrulayamadık.",
          f"8. **Ortalama hikâye sayısı:** kazananlarda {ort_w:.1f}, diğerlerinde {ort_o:.1f}.",
          f"9. **Hiçbiri:** ölçülebilir hikâye kategorilerinin hiçbirine uymayan kazanan: **{len(hic)}**. **Zayıf eşleşme (≤2 kategori):** " + (", ".join(f"{r.sembol}" for _, r in zayif.iterrows()) or "yok") + ".",
          "10. **Ölçülemeyen 18 kategori:** hiçbir hisse için etiketlenemedi. Özellikle **tetikleyici olay (K30)**, **geri alım (K32)**, **beklenti revizyonu (K29)** ve **haber (K23-K24)** bilinmiyor; bu yüzden \"hiçbirine uymayan\" hisseler aslında \"hikâyesi ölçülemeyen\" hisseler.", "",
          "## 3. Hisse hisse eşleştirme", "",
          "Hikâye kategorileri: " + ", ".join(sorted(HIKAYE)) + ". \"Uyarı\" kategorileri (K06, K09, K12, K14, K22) ve \"profil\" kategorileri (K13, K15–K18) hikâye sayılmaz. GOOG: GOOGL ile aynı şirket.", "",
          "| Sembol | Hikâye kategorileri | Uyarı/profil kategorileri | Ölçülemeyen (hafızadan not) | Sonuç |", "|---|---|---|---|---|"]
    notlar = {"WDC": "K34 spin-off", "GE": "K34 spin-off", "HOOD": "K35 endekse giriş", "APP": "K35 endekse giriş"}
    for _, r in w.iterrows():
        h = [c for c in r.kategoriler if c in HIKAYE]
        d = [c for c in r.kategoriler if c not in HIKAYE]
        sonuc = "**HİÇBİRİ**" if not h else ("zayıf (≤2)" if len(h) <= 2 else "hikâye var")
        M.append(f"| {r.sembol} | {', '.join(h) or '–'} | {', '.join(d) or '–'} | {notlar.get(r.sembol, 'bilinmiyor')} | {sonuc} |")
    M += ["", "## 4. Hisse hisse hikâyeler", "",
          "Her hissede önce **veriden çıkan hikâye** (fiyat yolu ve bugünkü temel veri), sonra **hafızama göre arka plan** var. Hafıza kısmı repodaki verilerden gelmez, haber kaynağı yoktur ve doğrulanmamıştır; \"belirsiz\" yazılanlar tahmindir.", ""]
    for i, r in w.iterrows():
        h = [c for c in r.kategoriler if c in HIKAYE]
        ad = SEKTOR.get(r.sektor, r.sektor)
        M += [f"### {i+1}. {r.sembol} — {r.ad} ({ad})", "",
              f"- **Kategoriler:** {', '.join(f'{c} {KAD[c]}' for c in h) if h else '**HİÇBİRİ**'}",
              f"- **Veriden hikâye:** {hikaye(r)}",
              f"- **Hafızaya göre arka plan (doğrulanmadı):** {HAFIZA.get(r.sembol) or (HAFIZA["GOOGL"] if r.sembol == "GOOG" else "bilinmiyor")}", ""]
    M += ["## 5. Bu çalışmadan ne çıkar, ne çıkmaz", "",
          "**Çıkan:**",
          "- Kazananların ortak paydası bir **tema** (yapay zekâ altyapısı) ve **önceki ayı piyasasında ezilmiş olmak**. Tek tek şirket hikâyeleri farklı olsa da ana dalga aynı.",
          "- \"Şokta düşenin sonra çok toparlaması\" kazananların yarısında var; \"şokta dayanıklılık\" ve \"ucuzluk\" kazananları ayırmıyor.",
          "- Kazananların büyük çoğunluğunun **bugün** güçlü büyüme, yüksek marj ve pahalı değerleme taşıması, yükselişin temelde de karşılık bulduğunu gösteriyor (sonuç olarak).", "",
          "**Çıkmayan:**",
          "- Bu belirtilerin ileride kazananı **önceden** bulduğu. Bu liste yalnızca geriye dönük açıklama; ileriye dönük test ayrı bir iş.",
          "- Ölçülemeyen 18 kategori (haber, sözleşme, geri alım, nakit, borç…) için hiçbir şey. Senin en çok önem verdiğin tetikleyici olay ve sözleşme bilgisi burada **tamamen eksik**.",
          "- Gerçek S&P 500 için bir sonuç. Örneklem 156 hisse ve kazananlara doğru yanlı.", "",
          "**Sonraki adım önerisi:** Gerçek S&P 500 üyeleriyle (tarihsel üyelik dahil), haber/sözleşme verisiyle ve her tarihte o gün bilinen mali tabloyla bu eşleştirmeyi tekrarlamak. Ancak o zaman \"hangi belirti önceden gelir\" sorusuna cevap verilebilir."]
    (KOK / "SP500-X2-KATEGORI-ESLESTIRME.md").write_text("\n".join(M) + "\n", encoding="utf-8")
    return w, js, hic, zayif


if __name__ == "__main__":
    w, js, hic, zayif = uret()
    print(len(w), "hiçbiri:", list(hic.sembol), "zayıf:", list(zayif.sembol))

"""Dipten toparlanma kontrol listesi (DIPTEN-TOPARLANMA-BELIRTILERI.md'nin uygulamasi).

Bu bir TARAMA/KONTROL LISTESIDIR, dogrulanmis bir sinyal degildir. Her madde:
  yesil = olumlu, kirmizi = sorun, sari = belirsiz/karisik, bilinmiyor = eldeki veriyle olculemiyor.
Veri: data/sonuclar.json (fiyat ozeti, bugunku temel veri). Haber, nakit, borc, seyrelme YOK -> 'bilinmiyor'."""
import json
import statistics as st

from mekanizma.ayarlar import REPO, SONUCLAR
from mekanizma.sim.ortak import guvenli

BASLIKLAR = ["1. Neden düştü?", "2. Kötü günü atlatır mı?", "3. İşler nasıl?", "4. Fiyat cazip mi?", "5. Toparlanma işareti", "6. Kaybım sınırlı mı?"]
ESIK = dict(zirveden=-25.0, mtd=-12.0, gun=-8.0, sektor_min=5, kucuk=2000.0, orta=10000.0, hacim_dusuk=0.3)


def _gecerli(x):
    return x is not None and not (isinstance(x, float) and x != x)


def veri_tutarli(s, q):
    """52 hafta zirvesi (hi52) bazi hisselerde yerel para birimi/cift listeleme yuzunden bozuk (ornek: TSM 2590).
    Zirveden >=%60 asagida gorunup 52 haftalik getirisi pek dusmemisse veri supheli sayilir."""
    if not (q and s.get("hi52") and _gecerli(s.get("r52w"))):
        return True
    uzak = (q["price"] / s["hi52"] - 1) * 100
    return not (uzak <= -60 and s["r52w"] > -30)


def aday_mi(s, q):
    """Dusmus mu? Zirveden >=%25 asagida, ya da ay basindan >=%12 dusmus, ya da tek gunde >=%8 dusmus."""
    if not s:
        return False
    uzak = (q["price"] / s["hi52"] - 1) * 100 if q and s.get("hi52") else None
    return bool((uzak is not None and uzak <= ESIK["zirveden"]) or (_gecerli(s.get("mtd")) and s["mtd"] <= ESIK["mtd"]) or (q and q.get("chgPct", 0) <= ESIK["gun"]))


def degerlendir(h):
    """h: dict(s, q, f, sektor, piyasa_r13w, sek) ; sek: dict(n, r13w, pe, ps) sektor medyanlari (None olabilir).
    Donus: [(baslik_no, madde, durum, aciklama), ...]"""
    s, q, f, sek = h["s"], h.get("q"), h.get("f") or {}, h.get("sek")
    o = []
    add = lambda b, m, d, a: o.append((b, m, d, a))
    # --- 1. Neden dustu
    if sek and sek.get("r13w") is not None and _gecerli(s.get("r13w")):
        fark = s["r13w"] - sek["r13w"]
        if sek["r13w"] <= -5 and fark > -10:
            add(1, "Sektör mü, şirket mi?", "yesil", f"Sektör de düşmüş (3 ay medyan {sek['r13w']:+.0f}%); hisse sektörden çok farklı değil ({fark:+.0f} puan)")
        elif fark <= -15:
            add(1, "Sektör mü, şirket mi?", "kirmizi", f"Şirkete özgü görünüyor: sektörden {fark:+.0f} puan kötü (3 ay)")
        else:
            add(1, "Sektör mü, şirket mi?", "sari", f"Sektörden {fark:+.0f} puan farklı (3 ay); net değil")
    else:
        add(1, "Sektör mü, şirket mi?", "bilinmiyor", "Sektör karşılaştırması için yeterli veri yok")
    add(1, "Düşüşün haberi/nedeni", "bilinmiyor", "Haber verisi yok. ELLE BAK: bu düşüşün sebebi ne?" + (f" (Son haber başlıkları: {'; '.join(n['h'][:70] for n in f.get('news', [])[:2])})" if f.get("news") else ""))
    # --- 2. Kotu gunu atlatir mi
    for m in ("Nakit ömrü", "Borç vadesi", "Hisse seyrelmesi"):
        add(2, m, "bilinmiyor", "Veri yok. ELLE BAK: kasa, borç takvimi, yeni hisse çıkarma geçmişi")
    nm = f.get("netM", s.get("netM"))
    if _gecerli(nm):
        if nm < 0:
            add(2, "Kârlılık (nakit vekili)", "kirmizi", f"Zararda (net marj {nm:.0f}%): nakit ömrü kritik")
        else:
            add(2, "Kârlılık (nakit vekili)", "yesil", f"Kârlı (net marj {nm:.0f}%); nakit sıkıntısı olasılığı düşük ama bu bir vekil")
    # --- 3. Isler
    rg = f.get("revG", s.get("revG"))
    if _gecerli(rg):
        add(3, "Satışlar", "yesil" if rg >= 0 else "kirmizi", f"Son rapor satış büyümesi {rg:+.0f}%" + ("" if rg >= 0 else " (küçülüyor; nedeni geçici mi?)"))
    gt, g5 = f.get("gmT", s.get("gmT")), f.get("gm5", s.get("gm5"))
    if _gecerli(gt) and _gecerli(g5):
        d = gt - g5
        add(3, "Brüt marj", "yesil" if d >= -3 else "kirmizi", f"Brüt marj {gt:.0f}% (5 yıl önce {g5:.0f}%, {d:+.0f} puan)" + ("" if d >= -3 else "; daralmanın nedeni geçici mi, kalıcı mı?"))
    if _gecerli(nm):
        add(3, "Net marj", "yesil" if nm > 0 else "kirmizi", f"Net marj {nm:.0f}%")
    add(3, "Kâr gerçek mi (nakit dönüşümü)", "bilinmiyor", "Nakit akışı verisi yok. ELLE BAK: kâr kasaya para olarak giriyor mu?")
    pe = f.get("pe", s.get("pe"))
    if _gecerli(pe) and _gecerli(rg) and pe < 15 and rg < 0:
        add(3, "Değer tuzağı", "kirmizi", "Ucuz görünüyor ama satışlar küçülüyor")
    if _gecerli(nm) and _gecerli(pe) and nm > 40 and pe < 6:
        add(3, "Tek seferlik kâr", "kirmizi", "Aşırı yüksek net marj + çok düşük F/K: kâr tek seferlik olabilir")
    if _gecerli(s.get("r52w")) and s["r52w"] > 300 and _gecerli(gt) and gt < 0:
        add(3, "Enkaz sıçraması", "kirmizi", "Çok sıçramış ama brüt marj negatif: iflas sonrası olabilir")
    # --- 4. Fiyat cazip mi
    if sek and _gecerli(pe) and pe > 0 and sek.get("pe"):
        r = pe / sek["pe"]
        add(4, "Değerleme (sektöre göre F/K)", "yesil" if r <= 1.0 else ("kirmizi" if r >= 1.5 else "sari"), f"F/K {pe:.0f}, sektör medyanı {sek['pe']:.0f} ({r:.1f}×)")
    elif sek and _gecerli(s.get("ps")) and sek.get("ps"):
        r = s["ps"] / sek["ps"]
        add(4, "Değerleme (sektöre göre fiyat/satış)", "yesil" if r <= 1.0 else ("kirmizi" if r >= 1.5 else "sari"), f"Fiyat/satış {s['ps']:.1f}, sektör medyanı {sek['ps']:.1f} ({r:.1f}×); kârsız olduğu için F/K yok")
    else:
        add(4, "Değerleme", "bilinmiyor", "Sektör karşılaştırması için yeterli veri yok")
    add(4, "Beklentiler değişti mi", "bilinmiyor", "Analist tahmin geçmişi yok. ELLE BAK: kazanç beklentisi düşüşle birlikte ne kadar kırıldı?")
    # --- 5. Toparlanma isareti
    ins = f.get("insBuyers")
    if ins is not None:
        add(5, "İçeriden alım", "yesil" if ins >= 1 else "sari", "Son dönemde içeriden alan yönetici var (ipucu, garanti değil)" if ins >= 1 else "İçeriden alım yok")
    eps = f.get("epsSurprise")
    if _gecerli(eps) and eps >= 8:
        add(5, "Son bilanço sürprizi", "bilgi", f"Kâr sürprizi {eps:+.0f}% (puana katılmaz; Klasik Radar ölçümünde tek başına güvenilmez)")
    add(5, "Yeni ve iyi haber / beklentiden iyi mi", "bilinmiyor", "Haber verisi yok. ELLE BAK")
    if q and _gecerli(q.get("chgPct")):
        add(5, "Bugünkü fiyat tepkisi", "bilgi", f"Bugün {q['chgPct']:+.1f}% (tek günlük hareket, puana katılmaz)")
    # --- 6. Risk
    mc = f.get("mcap", s.get("mcap"))
    if _gecerli(mc):
        if mc < ESIK["kucuk"]:
            add(6, "Şirket büyüklüğü", "kirmizi", f"Çok küçük ({mc/1000:.1f} mlr$): batma/likidite riski, küçük tutarla gir")
        elif mc < ESIK["orta"]:
            add(6, "Şirket büyüklüğü", "sari", f"Küçük-orta ({mc/1000:.1f} mlr$)")
        else:
            add(6, "Şirket büyüklüğü", "yesil", f"Büyük ({mc/1000:.0f} mlr$)")
    av = s.get("avgVol")
    if _gecerli(av):
        add(6, "İşlem hacmi (çıkabilir miyim?)", "kirmizi" if av < ESIK["hacim_dusuk"] else "yesil", f"Ortalama hacim {av:.2f} milyon hisse" + (" (düşük)" if av < ESIK["hacim_dusuk"] else ""))
    return o


def ozet(maddeler):
    y = sum(m[2] == "yesil" for m in maddeler)
    k = sum(m[2] == "kirmizi" for m in maddeler)
    sr = sum(m[2] == "sari" for m in maddeler)
    b = sum(m[2] == "bilinmiyor" for m in maddeler)
    olculen = y + k + sr
    skor = (y - 2 * k) / olculen if olculen else 0.0
    baslik = {}
    for no in range(1, 7):
        ds = [m[2] for m in maddeler if m[0] == no]
        ds = [d for d in ds if d != "bilgi"]
        if not ds or all(d == "bilinmiyor" for d in ds):
            baslik[no] = "bilinmiyor"
        elif "kirmizi" in ds:
            baslik[no] = "kirmizi"
        elif all(d in ("yesil", "bilinmiyor", "bilgi") for d in ds):
            baslik[no] = "yesil"
        else:
            baslik[no] = "sari"
    return dict(yesil=y, kirmizi=k, sari=sr, bilinmiyor=b, olculen=olculen, skor=skor, baslik=baslik)


def sektor_istatistik(d):
    """Sektor medyanlari (screen + prof evreni)."""
    gruplar = {}
    for t, s in d["screen"].items():
        i = (d["prof"].get(t) or {}).get("ind")
        if i:
            gruplar.setdefault(i, []).append(s)
    out = {}
    for i, lst in gruplar.items():
        if len(lst) < ESIK["sektor_min"]:
            continue
        med = lambda a: (st.median([x[a] for x in lst if _gecerli(x.get(a)) and (a != "pe" or x[a] > 0)]) if any(_gecerli(x.get(a)) and (a != "pe" or x[a] > 0) for x in lst) else None)
        out[i] = dict(n=len(lst), r13w=med("r13w"), pe=med("pe"), ps=med("ps"))
    return out


def calistir(yol=None, ilk=30):
    d = json.loads((yol or REPO / "data" / "sonuclar.json").read_text(encoding="utf-8"))
    sek = sektor_istatistik(d)
    sonuc, tutarsiz = [], []
    for t, s in d["screen"].items():
        q = d["quotes"].get(t)
        if not aday_mi(s, q):
            continue
        if not veri_tutarli(s, q):
            tutarsiz.append(dict(sembol=t, fiyat=q["price"], hi52=s["hi52"], r52w=s["r52w"]))
            continue
        ind = (d["prof"].get(t) or {}).get("ind")
        m = degerlendir(dict(s=s, q=q, f=d["fin"].get(t), sek=sek.get(ind)))
        o = ozet(m)
        sonuc.append(dict(sembol=t, ad=(d["prof"].get(t) or {}).get("name") or (d["fin"].get(t) or {}).get("name"), sektor=ind,
                          zirveden=(q["price"] / s["hi52"] - 1) * 100 if q and s.get("hi52") else None, mtd=s.get("mtd"), maddeler=m, **o))
    sonuc.sort(key=lambda r: (-r["skor"], -r["olculen"], r["kirmizi"]))
    return d["generatedAt"][:10], sonuc, tutarsiz


IKON = {"yesil": "🟢", "kirmizi": "🔴", "sari": "🟡", "bilinmiyor": "⚪", "bilgi": "ℹ️"}


def rapor(tarih, sonuc, tutarsiz=(), ilk=25):
    n = len(sonuc)
    L = ["# Dipten toparlanma kontrol listesi — aday taraması", "",
         f"Veri tarihi: **{tarih}**. Düşmüş sayılan hisse sayısı: **{n}** (zirveden ≥%25 aşağıda, ya da ay başından ≥%12 düşmüş, ya da tek günde ≥%8 düşmüş).", "",
         "> **Bu bir kontrol listesidir, doğrulanmış bir sinyal değildir; yatırım tavsiyesi değildir.** `DIPTEN-TOPARLANMA-BELIRTILERI.md` belgesindeki maddelerin eldeki veriyle ölçülebilen kısmını uygular.", "",
         "**⚪ Bilinmiyor** olan maddeler (haber nedeni, nakit ömrü, borç, seyrelme, kâr–nakit dönüşümü, beklenti değişimi, yeni haber) bu veriyle **ölçülemiyor**; bunlar karar için en önemli kısım. Her hisse için 'ELLE BAK' notları var. Bunlara bakmadan karar verme.", "",
         "Puan = (🟢 − 2×🔴) / ölçülen madde. Sıralama bilgi amaçlıdır; yüksek puan 'al' demek değil, 'önce şuraya bak' demektir.", "",
         "Tablodaki başlık sütunları: " + " · ".join(BASLIKLAR), "",
         f"## En yüksek puanlı {min(ilk, n)} hisse", "",
         "| Sembol | Şirket | Sektör | Zirveden | Puan | 🟢 | 🔴 | ⚪ | 1 | 2 | 3 | 4 | 5 | 6 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sonuc[:ilk]:
        L.append(f"| {r['sembol']} | {(r['ad'] or '')[:28]} | {r['sektor'] or ''} | {r['zirveden']:.0f}% | {r['skor']:+.2f} | {r['yesil']} | {r['kirmizi']} | {r['bilinmiyor']} | " + " | ".join(IKON[r['baslik'][i]] for i in range(1, 7)) + " |")
    L += ["", "## Ayrıntı (ilk 10)", ""]
    for r in sonuc[:10]:
        L += [f"### {r['sembol']} — {r['ad']}  ({r['sektor']})", f"Zirveden {r['zirveden']:.0f}% aşağıda; ay başından {r['mtd']:+.0f}%." if r["mtd"] is not None else "", ""]
        for b in range(1, 7):
            ms = [m for m in r["maddeler"] if m[0] == b]
            if ms:
                L.append(f"**{BASLIKLAR[b-1]}** {IKON[r['baslik'][b]]}")
                L += [f"- {IKON[m[2]]} {m[1]}: {m[3]}" for m in ms]
        L.append("")
    if tutarsiz:
        L += ["## Puanlanmayan hisseler: veri tutarsız", "",
              "Aşağıdaki hisselerde 52 haftalık zirve (`hi52`) ile fiyat uyuşmuyor (yerel para birimi ya da çift listeleme olabilir). Yanlış aday üretmemek için **puanlanmadı**; elle kontrol et.", "",
              "| Sembol | Fiyat | 52 hafta zirvesi | 52 hafta getirisi |", "|---|---|---|---|"]
        L += [f"| {x['sembol']} | {x['fiyat']:g} | {x['hi52']:g} | {x['r52w']:+.0f}% |" for x in tutarsiz]
        L.append("")
    k_say = sum(1 for r in sonuc if r["kirmizi"] == 0)
    L += ["## Genel durum", "",
          f"- {n} düşmüş hissenin {k_say} tanesinde hiç kırmızı bayrak yok (ama ölçülemeyen maddeler hâlâ bilinmiyor).",
          f"- Ortalama ölçülen madde sayısı {st.mean(r['olculen'] for r in sonuc):.1f}; bilinmeyen {st.mean(r['bilinmiyor'] for r in sonuc):.1f}. Yani her hissenin yaklaşık yarısı henüz ölçülemiyor.",
          "- Bu liste haber okumadan **tamamlanmış sayılmaz**."]
    return "\n".join(L) + "\n"


def uret():
    tarih, sonuc, tutarsiz = calistir()
    SONUCLAR.mkdir(exist_ok=True)
    (SONUCLAR / "dip_adaylari.md").write_text(rapor(tarih, sonuc, tutarsiz), encoding="utf-8")
    (SONUCLAR / "dip_adaylari.json").write_text(json.dumps(guvenli(dict(tarih=tarih, adaylar=sonuc, tutarsiz=tutarsiz)), ensure_ascii=False, indent=1), encoding="utf-8")
    return sonuc

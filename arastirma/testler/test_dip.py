from mekanizma.dip.kontrol import aday_mi, degerlendir, ozet, veri_tutarli


def durumlar(m):
    return {x[1]: x[2] for x in m}


def test_aday_mi():
    assert aday_mi({"hi52": 100, "mtd": 0, "r52w": -10}, {"price": 70, "chgPct": 0})          # zirveden -%30
    assert aday_mi({"hi52": 100, "mtd": -15, "r52w": 0}, {"price": 99, "chgPct": 0})          # ay basindan -%15
    assert aday_mi({"hi52": 100, "mtd": 0, "r52w": 0}, {"price": 99, "chgPct": -9})           # tek gunde -%9
    assert not aday_mi({"hi52": 100, "mtd": -2, "r52w": 0}, {"price": 95, "chgPct": -1})


def test_veri_tutarsizligi_yakalanir():
    # TSM benzeri: yerel para birimi zirvesi -> fiyat zirvenin %16'si ama 52 haftalik getiri pozitif
    assert not veri_tutarli({"hi52": 2590, "r52w": 17}, {"price": 420})
    assert veri_tutarli({"hi52": 100, "r52w": -50}, {"price": 38})                           # gercek dusus: tutarli


def test_kirmizi_bayraklar():
    s = {"r13w": -30, "mtd": -10, "hi52": 100, "r52w": -20, "gmT": 20, "gm5": 40, "netM": -5, "revG": -10, "pe": 8, "avgVol": 0.1, "mcap": 800, "ps": 1}
    m = durumlar(degerlendir(dict(s=s, q={"price": 60, "chgPct": 1.0}, f={}, sek={"n": 20, "r13w": -2, "pe": 20, "ps": 3})))
    assert m["Sektör mü, şirket mi?"] == "kirmizi"          # sektorden -28 puan kotu
    assert m["Satışlar"] == "kirmizi" and m["Brüt marj"] == "kirmizi" and m["Net marj"] == "kirmizi"
    assert m["Değer tuzağı"] == "kirmizi"                    # ucuz ama satis kuculuyor
    assert m["Şirket büyüklüğü"] == "kirmizi"
    assert m["Nakit ömrü"] == "bilinmiyor" and m["Düşüşün haberi/nedeni"] == "bilinmiyor"


def test_saglam_sirket_sektor_dususu():
    s = {"r13w": -12, "mtd": -3, "hi52": 100, "r52w": -10, "gmT": 50, "gm5": 48, "netM": 20, "revG": 12, "pe": 14, "avgVol": 3, "mcap": 80000}
    f = {"insBuyers": 2}
    d = durumlar(degerlendir(dict(s=s, q={"price": 70, "chgPct": 0.5}, f=f, sek={"n": 20, "r13w": -14, "pe": 22, "ps": 3})))
    assert d["Sektör mü, şirket mi?"] == "yesil" and d["Değerleme (sektöre göre F/K)"] == "yesil" and d["İçeriden alım"] == "yesil"
    assert d["Bugünkü fiyat tepkisi"] == "bilgi"


def test_ozet_bilgi_puana_katilmaz():
    m = [(5, "a", "bilgi", ""), (5, "b", "bilinmiyor", ""), (3, "c", "yesil", ""), (3, "d", "kirmizi", "")]
    o = ozet(m)
    assert o["olculen"] == 2 and o["yesil"] == 1 and o["kirmizi"] == 1 and o["baslik"][5] == "bilinmiyor" and o["baslik"][3] == "kirmizi"

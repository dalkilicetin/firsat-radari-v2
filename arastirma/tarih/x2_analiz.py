"""Son 3 yilda S&P 500 getirisinin >=2 kati getiri saglayan hisseleri bul, ozelliklerini ve kategori eslesmesini cikar.
Veri: data/sonuclar.json (156 hisse, aylik kapanis). TUM S&P 500 degil; aday/izleme listesi agirlikli."""
import json

import numpy as np
import pandas as pd

from mekanizma.veri import ornek

BAS = pd.Timestamp("2023-10-31")
ETF = ["QTUM", "BOTZ", "SMH", "ICLN", "URA", "ARKG", "XBI", "ITA", "LIT", "KWEB", "XLE", "XLF", "IGV", "PAVE", "JETS", "REMX", "SPY", "VGK", "MCHI", "EWJ", "EEM", "XAU/USD", "SLV", "PPLT", "PALL", "CPER"]
AYNI_SIRKET = {"GOOG": "GOOGL"}      # ayni sirketin ikinci sinifi: istatistikte bir kez sayilir

# 40 kategori: (kod, ad, grup, olculebilir mi, kural/neden)
KAT = [
    ("K01", "Dışsal şoktan toparlanma", "dip", True, "2025 şubat zirvesinden nisana ≥%10 düşmüş ve mayıs→ekim ≥%25 toparlamış"),
    ("K02", "Şokta dayanıklı (gizli güç)", "dip", True, "2025 şubat zirvesinden nisana düşüş ≤%3 (S&P 500 ≈ −%8)"),
    ("K03", "Önceki ayı piyasasından toparlanma", "dip", True, "Pencere başında (2023-10) kendi önceki zirvesinden ≥%35 aşağıda"),
    ("K04", "2022 ayı piyasasında çok dayanıklı", "dip", True, "2021-12→2022-09 düşüşü ≤%10 (S&P 500 ≈ −%25) ya da yükseliş"),
    ("K05", "Trend lideri / istikrarlı yürüyüş", "fiyat", True, "Ayların ≥%60'ı 10 aylık ortalamanın üstünde ve en kötü düşüş ≤%35"),
    ("K06", "Çalkantılı yolculuk (uyarı)", "fiyat", True, "Pencere içinde en kötü düşüş ≥%45"),
    ("K07", "Tek dalga patlama", "fiyat", True, "Toplam kazancın ≥%90'ı tek bir 12 aylık dilimde"),
    ("K08", "Çok yıllı yürüyüş", "fiyat", True, "Toplam kazancın en çok %65'i tek 12 ay; kazanç yıllara yayılmış"),
    ("K09", "Hâlâ tepeye yakın (kovalama riski)", "fiyat", True, "Pencere sonunda pencere zirvesinin ≤%5 altında"),
    ("K10", "Satışlar güçlü büyüyor", "temel", True, "Son rapor satış büyümesi ≥%20 (bugünkü veri)"),
    ("K11", "Marj iyileşti", "temel", True, "Brüt marj bugün − 5 yıl önce ≥ +3 puan (bugünkü veri)"),
    ("K12", "Marj daraldı (uyarı)", "temel", True, "Brüt marj bugün − 5 yıl önce ≤ −3 puan (bugünkü veri)"),
    ("K13", "Kârlı", "temel", True, "Net marj ≥%10 (bugünkü veri)"),
    ("K14", "Zararda (spekülatif)", "temel", True, "Net marj < 0 (bugünkü veri)"),
    ("K15", "Pahalı değerleme", "temel", True, "F/K ≥60 ya da fiyat/satış ≥20 (bugünkü veri)"),
    ("K16", "Makul değerleme", "temel", True, "F/K < 20 (bugünkü veri)"),
    ("K17", "Dev şirket", "profil", True, "Piyasa değeri ≥100 milyar $"),
    ("K18", "Küçük şirket", "profil", True, "Piyasa değeri <10 milyar $"),
    ("K19", "Son bilançoda beklentiyi aştı", "temel", True, "Son bilanço kâr sürprizi ≥%8 (bugünkü veri)"),
    ("K20", "İçeriden alım", "yatirimci", True, "Son dönemde içeriden alan yönetici var (bugünkü veri)"),
    ("K21", "Tema dalgası", "piyasa", True, "Aynı sektörde (Yarı iletken ya da Teknoloji) ≥5 kazanan hisse daha var"),
    ("K22", "Zirveden sert geri çekilme (uyarı)", "fiyat", True, "Pencere sonunda pencere zirvesinin ≥%30 altında"),
    ("K23", "Dışsal korku mu, şirkete özgü mü", "dip", False, "Haber verisi gerekir"),
    ("K24", "Fiyat kötü haberi yansıttı mı", "dip", False, "Haber ve beklenti verisi gerekir"),
    ("K25", "Nakit ömrü", "dip", False, "Çeyreklik nakit akışı verisi yok"),
    ("K26", "Borç vadesi", "dip", False, "Borç vade verisi yok"),
    ("K27", "Hisse seyrelmesi", "dip", False, "Hisse sayısı geçmişi yok"),
    ("K28", "Kâr–nakit dönüşümü", "temel", False, "Nakit akışı verisi yok"),
    ("K29", "Beklenti revizyonu", "temel", False, "Analist tahmin geçmişi yok"),
    ("K30", "Tetikleyici olay (sözleşme, onay)", "olay", False, "Haber/sözleşme verisi yok"),
    ("K31", "Büyük fon alımı", "yatirimci", False, "13F verisi yok"),
    ("K32", "Hisse geri alımı", "yatirimci", False, "Geri alım verisi yok"),
    ("K33", "Açığa satış sıkışması", "yatirimci", False, "Açığa satış verisi yok"),
    ("K34", "Şirket bölünmesi (spin-off)", "takvim", False, "Olay takvimi yok (yalnızca hafızadan not)"),
    ("K35", "Endekse giriş", "takvim", False, "Endeks üyelik geçmişi yok (yalnızca hafızadan not)"),
    ("K36", "Kilit açılışı", "takvim", False, "Halka arz kilit verisi yok"),
    ("K37", "Bilanço sonrası kayma", "olay", False, "Aylık veri bilanço gününü ayıramaz"),
    ("K38", "Sıkışma sonrası kırılım", "fiyat", False, "Günlük fiyat gerekir"),
    ("K39", "Sektör öncüsü domino", "piyasa", False, "Günlük fiyat ve bilanço takvimi gerekir"),
    ("K40", "Yıl sonu vergi satışı", "takvim", False, "Günlük fiyat gerekir"),
]
HIKAYE = {"K01", "K02", "K03", "K05", "K07", "K08", "K10", "K11", "K19", "K20", "K21"}   # 'hiçbiri' tanımı için


def ozellikler():
    a = ornek.aylik()
    prof = ornek.profil()
    d = json.load(open(ornek.SONUC_JSON, encoding="utf-8"))
    son = a.index[-1]
    spy = a["SPY"]
    sp = float(spy[son] / spy[BAS] - 1)
    h = a.drop(columns=[c for c in ETF if c in a.columns])
    satir = []
    for t in h.columns:
        p = a[t].dropna()
        if BAS not in p.index or son not in p.index:
            continue
        w = p[BAS:]
        pre = p[:BAS]
        ret = float(w.iloc[-1] / w.iloc[0] - 1)
        g = lambda x, y: float(a.loc[x, t] / a.loc[y, t] - 1) if pd.notna(a.loc[x, t]) and pd.notna(a.loc[y, t]) else np.nan
        zirve25 = a.loc["2025-01-31":"2025-02-28", t].max()
        yil = np.log(w).diff(12).dropna()
        f = d["fin"].get(t, {})
        pay = float(yil.max() / np.log(w.iloc[-1] / w.iloc[0])) if w.iloc[-1] > w.iloc[0] and len(yil) else np.nan
        satir.append(dict(
            sembol=t, ad=prof["ad"].get(t) or f.get("name"), sektor=prof["sektor"].get(t) or f.get("industry") or "",
            ret3=ret, kat=ret / sp, dd0=float(pre.iloc[-1] / pre.max() - 1), kay22=g("2022-09-30", "2021-12-31"),
            d25=float(a.loc["2025-04-30", t] / zirve25 - 1), f25=g("2025-10-31", "2025-05-31"), d26=g("2026-03-31", "2026-01-31"),
            en_iyi_12=float(np.exp(yil.max()) - 1), pay=pay, en_iyi_bitis=str(yil.idxmax().date()),
            mdd=float((w / w.cummax() - 1).min()), ust=float((w > w.rolling(10).mean()).dropna().mean()),
            son_dd=float(w.iloc[-1] / w.max() - 1),
            revG=f.get("revG"), gmT=f.get("gmT"), gm5=f.get("gm5"), netM=f.get("netM"), pe=f.get("pe"), ps=f.get("ps"),
            mcap=f.get("mcap"), ins=f.get("insBuyers"), eps=f.get("epsSurprise"), haber=len(f.get("news") or [])))
    df = pd.DataFrame(satir)
    df["kazanan"] = df["ret3"] >= 2 * sp
    df["tekil"] = ~df["sembol"].isin(AYNI_SIRKET)
    return df, sp, son


def _v(x):
    return x is not None and not (isinstance(x, float) and np.isnan(x))


def kategoriler(df):
    kazanan = df[df.kazanan]
    n_sek = kazanan[kazanan.tekil].groupby("sektor").size().to_dict()
    sonuc = []
    for _, r in df.iterrows():
        k = set()
        if r.d25 <= -0.10 and _v(r.f25) and r.f25 >= 0.25: k.add("K01")
        if r.d25 >= -0.03: k.add("K02")
        if r.dd0 <= -0.35: k.add("K03")
        if _v(r.kay22) and r.kay22 >= -0.10: k.add("K04")
        if r.ust >= 0.60 and r.mdd >= -0.35: k.add("K05")
        if r.mdd <= -0.45: k.add("K06")
        if _v(r.pay) and r.pay >= 0.90: k.add("K07")
        if _v(r.pay) and r.pay <= 0.65: k.add("K08")
        if r.son_dd >= -0.05: k.add("K09")
        if r.son_dd <= -0.30: k.add("K22")
        if _v(r.revG) and r.revG >= 20: k.add("K10")
        if _v(r.gmT) and _v(r.gm5):
            if r.gmT - r.gm5 >= 3: k.add("K11")
            if r.gmT - r.gm5 <= -3: k.add("K12")
        if _v(r.netM):
            if r.netM >= 10: k.add("K13")
            if r.netM < 0: k.add("K14")
        if (_v(r.pe) and r.pe >= 60) or (_v(r.ps) and r.ps >= 20): k.add("K15")
        if _v(r.pe) and r.pe < 20: k.add("K16")
        if _v(r.mcap):
            if r.mcap >= 100000: k.add("K17")
            if r.mcap < 10000: k.add("K18")
        if _v(r.eps) and r.eps >= 8: k.add("K19")
        if _v(r.ins) and r.ins >= 1: k.add("K20")
        if r.sektor in ("Semiconductors", "Technology") and (n_sek.get(r.sektor, 0) - (1 if r.kazanan and r.tekil else 0)) >= 5: k.add("K21")
        sonuc.append(sorted(k))
    df = df.copy()
    df["kategoriler"] = sonuc
    df["hikaye"] = [sorted(set(k) & HIKAYE) for k in sonuc]
    return df


if __name__ == "__main__":
    df, sp, son = ozellikler()
    df = kategoriler(df)
    w = df[df.kazanan]
    print(len(df), len(w), round(sp, 3))
    print(w[["sembol", "kategoriler", "hikaye"]].to_string())
    print("hikayesiz kazanan:", list(w[w.hikaye.str.len() == 0].sembol))

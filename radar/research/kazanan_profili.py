"""Kazanan profili: her 3 aylık dönemin en çok kazandıran hisseleri, dönem başında (o gün bilinen verilerle) nasıl görünüyordu?

Karşılaştırma üç grup arasında, aynı tarihte, aynı evrende:
  kazananlar = sonraki 13 haftada en yüksek getirili 20 hisse
  kaybedenler = en düşük getirili 20 hisse
  herkes = evrenin tamamı (belirtiler tarih içinde yüzdelik sıra olduğu için herkesin medyanı ≈ 0,50)
Yalnızca güvenilir veri: fiyat, hacim, mali tablolar, içeriden alım (Form 4), fon bildirimleri (13F/13D/13G), 8-K olayları.
Haber, metin (10-K), Wikipedia, Reddit belirtileri kullanılmaz (kullanıcı kararı 18 Ekim 2026).
Evren: çerçevedeki ≥ 1 $ hisseler, günlük işlem tutarı ≥ 1 M$ olarak bilinen (geriye_bakis ile aynı kural).

python -m radar.research.kazanan_profili  →  reports/research/kazanan_profili.json, kazanan_profili.md
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from radar import config

R = config.ROOT / "reports" / "research"
FRAME = config.ROOT / "data" / "derived" / "aylik_cerceve.parquet"
N = 20

AD = {  # belirti → anlaşılır ad
    "momentum_12_1": "son 1 yıl getirisi (son ay hariç)", "getiri_6a": "son 6 ay getirisi", "getiri_1a": "son 1 ay getirisi",
    "kisa_vade_donus": "kısa vadeli geri dönüş (son ay düşüş)", "zirveye_yakinlik_52h": "1 yıllık zirveye yakınlık",
    "dusuk_oynaklik": "düşük oynaklık", "ivol_3a": "şirkete özgü oynaklık", "max_gunluk_1a": "son ayın en büyük günlük yükselişi",
    "max_haftalik_4h": "son 4 haftanın en büyük haftalık yükselişi", "oynaklik_genislemesi": "oynaklık genişlemesi",
    "beta_qqq": "Nasdaq'a duyarlılık (beta)", "kucuk_boyut": "küçük şirket", "fiyat_seviyesi": "hisse fiyatı",
    "likidite": "işlem hacmi (tutar)", "hacim_artisi": "hacim artışı", "kirilim": "fiyat kırılımı",
    "rsi_14h": "RSI", "ort_10h_uzaklik": "10 haftalık ortalamaya uzaklık", "ort_40h_uzaklik": "40 haftalık ortalamaya uzaklık",
    "macd": "MACD", "bollinger_konum": "Bollinger konumu", "fip_bilgi_surekliligi": "yükselişin istikrarı (çok günde yavaş)",
    "gelir_buyumesi": "gelir büyümesi", "buyume_ivmesi": "büyüme ivmesi", "kar_buyumesi": "kâr büyümesi",
    "brut_marj_degisimi": "brüt marj iyileşmesi", "faaliyet_marji_degisimi": "faaliyet marjı iyileşmesi",
    "arge_yogunlugu": "Ar-Ge yoğunluğu", "serbest_nakit_getirisi": "serbest nakit / piyasa değeri",
    "kazanc_getirisi": "kâr / piyasa değeri", "defter_fiyat": "defter değeri / piyasa değeri", "satis_fiyat": "satış / piyasa değeri",
    "favok_fd": "FAVÖK / firma değeri", "temettu_verimi": "temettü verimi", "nakit_piyasa": "nakit / piyasa değeri",
    "ozsermaye_karliligi": "özsermaye kârlılığı", "aktif_karliligi": "aktif kârlılığı", "brut_kar_aktif": "brüt kâr / varlık",
    "brut_marj": "brüt marj", "faaliyet_marji": "faaliyet marjı", "borc_ozsermaye": "borç / özsermaye", "cari_oran": "cari oran",
    "faiz_karsilama": "faiz karşılama", "altman_z": "Altman Z (iflas riski düşük)", "piotroski_f": "Piotroski (finansal sağlık)",
    "tahakkuklar_dusuk": "düşük tahakkuk (kâr kalitesi)", "varlik_buyumesi_dusuk": "düşük varlık büyümesi",
    "hisse_sayisi_degisimi": "hisse sayısı artışı (sulandırma)", "geri_alim_getirisi": "hisse geri alımı",
    "kazanc_aciklamasi_tepkisi": "son kâr açıklamasına fiyat tepkisi", "sue_fiyat": "kâr sürprizi (fiyattan)",
    "gelir_surprizi": "gelir sürprizi", "bilanco_uzerinden_hafta": "son bilançodan bu yana hafta",
    "icerden_alici_sayisi_90g": "içeriden alan yönetici sayısı (90 gün)", "icerden_alim_tutar_piyasa_degeri": "içeriden alım tutarı / piyasa değeri",
    "kurumsal_sahip_degisimi": "kurumsal sahip sayısı değişimi", "kurumsal_hisse_degisimi_payi": "kurumsal hisse payı değişimi",
    "sektor_getiri_13h": "sektörün son 3 ayı", "sektor_momentum_12_1": "sektörün son 1 yılı", "sektor_4h": "sektörün son ayı",
    "sektor_ma_dalgasi": "sektörde birleşme dalgası",
}
EVENTS = {"devamlilik_suphesi": "denetçi 'devamlılık şüphesi'", "icerden_alim_kumesi_3plus": "3+ yöneticinin birlikte alımı",
          "ust_yonetici_alimi_90g": "üst yöneticinin alımı", "8k_1.01_önemli anlaşma": "8-K: önemli anlaşma",
          "8k_1.02_anlaşma feshi": "8-K: anlaşma feshi", "8k_2.01_satın alma/elden çıkarma tamamlandı": "8-K: satın alma tamamlandı",
          "8k_2.03_yeni borç yükümlülüğü": "8-K: yeni borç", "8k_3.02_kayıtsız hisse satışı (sulandırma)": "8-K: kayıtsız hisse satışı",
          "8k_5.02_yönetici değişikliği": "8-K: yönetici değişikliği", "8k_7.01_kamuyu aydınlatma (FD)": "8-K: kamuyu aydınlatma",
          "8k_8.01_diğer olaylar": "8-K: diğer olaylar", "aktivist_13d": "aktivist yatırımcı (%5+, 13D)",
          "aktivist_13d_degisiklik": "aktivist pozisyon değişikliği (13D/A)", "pasif_13g_yeni": "yeni büyük pasif yatırımcı (13G)",
          "gec_rapor_bildirimi": "rapor gecikme bildirimi", "hisse_ihraci": "hisse ihracı", "bilanco_bu_ay_bekleniyor": "bu ay bilanço bekleniyor"}


def main() -> dict:
    cols = ["tarih", "yil", "sektor", "sembol", "islem_tutari", "getiri_13h"] + list(AD) + list(EVENTS)
    df = pd.read_parquet(FRAME, columns=[c for c in dict.fromkeys(cols)])
    df = df[(df.tarih.dt.month.isin([1, 4, 7, 10])) & (df.islem_tutari >= 1e6) & df.getiri_13h.notna()]
    # çeyrek başı = ayın ilk Cuması (çerçeve satırları zaten ayın ilk Cuması)
    rank = df.groupby("tarih").getiri_13h.rank(ascending=False, method="first")
    rank_low = df.groupby("tarih").getiri_13h.rank(ascending=True, method="first")
    df["grup"] = np.select([rank <= N, rank_low <= N], ["kazanan", "kaybeden"], "diğer")
    W, L, A = df[df.grup == "kazanan"], df[df.grup == "kaybeden"], df
    out = {"donem": int(df.tarih.nunique()), "kazanan_satir": int(len(W)), "evren_ortalama": round(float(df.groupby("tarih").size().mean()))}
    rows = []
    for c, name in AD.items():
        if c not in df:
            continue
        w, l = W[c].median(), L[c].median()
        # yıllık tutarlılık: kazananların medyanının 0,5'ten aynı yönde saptığı yılların payı
        by = W.groupby("yil")[c].median()
        sign = np.sign(w - 0.5)
        cons = float((np.sign(by - 0.5) == sign).mean()) if len(by) else np.nan
        # kazananların bu belirtinin en üst %20'sinde olma oranı (rastgele beklenti %20)
        top = float((W[c] >= 0.8).mean()) if W[c].notna().any() else np.nan
        top_l = float((L[c] >= 0.8).mean()) if L[c].notna().any() else np.nan
        bot = float((W[c] <= 0.2).mean()) if W[c].notna().any() else np.nan
        rows.append({"belirti": c, "ad": name, "kazanan_medyan": w, "kaybeden_medyan": l, "kazanan_ust20": top,
                     "kaybeden_ust20": top_l, "kazanan_alt20": bot, "yil_tutarliligi": cons, "dolu": float(W[c].notna().mean())})
    t = pd.DataFrame(rows)
    t["sapma"] = (t.kazanan_medyan - 0.5).abs()
    t["kazanani_kaybedenden_ayirir"] = (t.kazanan_medyan - t.kaybeden_medyan)
    ev = []
    for c, name in EVENTS.items():
        if c not in df:
            continue
        base = float((A[c] > 0).mean())
        ev.append({"olay": c, "ad": name, "kazanan": float((W[c] > 0).mean()), "kaybeden": float((L[c] > 0).mean()), "herkes": base})
    e = pd.DataFrame(ev)
    e["kat_kazanan"] = e.kazanan / e.herkes
    e["kat_kaybeden"] = e.kaybeden / e.herkes
    sec = pd.DataFrame({"kazanan": W.sektor.value_counts(normalize=True), "kaybeden": L.sektor.value_counts(normalize=True),
                        "herkes": A.sektor.value_counts(normalize=True)}).fillna(0).sort_values("kazanan", ascending=False)
    # Kombinasyon: "piyango profili" (küçük + düşük fiyat + yüksek oynaklık) kazanan ve kaybedenlerde ne kadar yaygın
    lot = (A.kucuk_boyut >= 0.7) & (A.fiyat_seviyesi <= 0.3) & (A.ivol_3a >= 0.7)
    out["piyango_profili"] = {"tanim": "küçük şirket (üst %30), düşük fiyat (alt %30), yüksek şirkete özgü oynaklık (üst %30)",
                              "kazanan": float(lot[A.grup == "kazanan"].mean()),
                              "kaybeden": float(lot[A.grup == "kaybeden"].mean()), "herkes": float(lot.mean()),
                              "bu_profilde_kazanan_olma_olasiligi": float((A.grup[lot] == "kazanan").mean()),
                              "bu_profilde_kaybeden_olma_olasiligi": float((A.grup[lot] == "kaybeden").mean()),
                              "genel_kazanan_olasiligi": float((A.grup == "kazanan").mean())}
    # dönemler arası istikrar: 2010–2017 ile 2018–2026
    halves = {}
    for nm, (a, b) in {"2010-2017": (2010, 2017), "2018-2026": (2018, 2026)}.items():
        ww = W[(W.yil >= a) & (W.yil <= b)]
        halves[nm] = {c: round(float(ww[c].median()), 3) for c in t.sort_values("sapma", ascending=False).belirti.head(15)}
    out["donem_istikrari"] = halves
    out["belirtiler"] = t.sort_values("sapma", ascending=False).round(3).to_dict(orient="records")
    out["olaylar"] = e.sort_values("kat_kazanan", ascending=False).round(4).to_dict(orient="records")
    out["sektor"] = sec.round(3).reset_index(names="sektor").to_dict(orient="records")
    # getiri dağılımı: kazananların kaçı dönem başında son 1 ayda zaten yükseliyordu
    out["baslangic_durumu"] = {"son_1_ay_ust_yari_kazanan": float((W.getiri_1a >= 0.5).mean()),
                               "son_1_yil_alt_yari_kazanan": float((W.momentum_12_1 <= 0.5).mean())}
    (R / "kazanan_profili.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("belirtiler", "olaylar", "sektor")}, ensure_ascii=False, indent=1, default=float))
    print(t.sort_values("sapma", ascending=False).head(25)[["ad", "kazanan_medyan", "kaybeden_medyan", "kazanan_ust20", "kaybeden_ust20", "yil_tutarliligi", "dolu"]].round(2).to_string())
    print(e.sort_values("kat_kazanan", ascending=False).round(3).to_string())
    print(sec.head(10).round(3).to_string())
    return out


if __name__ == "__main__":
    main()

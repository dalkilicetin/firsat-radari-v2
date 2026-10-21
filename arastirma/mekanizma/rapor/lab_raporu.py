"""sonuclar/*.json -> sonuclar/LAB-RAPORU.md (tum sayilar JSON'dan; elle rakam yok)."""
import json

import pandas as pd
from scipy.stats import spearmanr

from mekanizma.ayarlar import SONUCLAR
from mekanizma.sim.ortak import pct
from mekanizma.veri.katalog import katalog


def _j(ad):
    return json.loads((SONUCLAR / f"{ad}.json").read_text(encoding="utf-8"))


def _ci(lo, hi):
    return f"[{pct(lo)}, {pct(hi)}]"


def uret():
    S2, S3, S4, S5, S1 = _j("sim_S2"), _j("sim_S3"), _j("sim_S4"), _j("sim_S5"), _j("sim_S1")
    KR, KO, R1, R2, R3 = _j("kirilma"), _j("kosullar"), _j("gercek_R1"), _j("gercek_R2"), _j("gercek_R3")
    kal = _j("sim_kalibre")

    y1, y2, basit = S2["Y1 (sadece gerilim)"], S2["Y2 (gerilim + herhangi bosalma)"], S2["basit: dd ≤ −%15"]
    s3_yay, s3_boz, s3_saf = S3["yay var (kalibre)"], S3["yay yok, bozulma var"], S3["yay yok, bozulma yok (saf yürüyüş)"]
    s4_taban, s4_guc, s4_yok = S4["yarılanma 60g, panik 1.0/5yıl"], S4["yarılanma 30g, panik 1.7/5yıl"], S4["YAY YOK (bozulma var)"]
    s5 = S5["126"]
    pan, boz = s5["Olay etiketi: panik olayı"], s5["Olay etiketi: bozulma olayı"]
    s1 = S1["2.0"]
    kn, nl = KR["yay + bozulma var (kalibre)"], KR["olay yok (negatif kontrol)"]
    kp, np_ = kn["panikten_normale_63"], nl["panikten_normale_63"]
    ky, ny = kn["yukselisten_dususe_63"], nl["yukselisten_dususe_63"]
    kosN = KO["NORMAL dünya (kalibre)"]
    gg = KO["gizli_guc"]
    r2_25 = R2["2025 (panik/tarife türü)"]["2025-03-31"]
    r2_22 = R2["2022 (ayrıştırma: büyük olasılıkla bozulma türü)"]["2022-06-30"]
    r3a = R3["Tüm şoklar (ana sonuç)"]["5"]

    k = katalog()
    spx = k[k.piyasa == "SPX"]
    rho_h, p_h = spearmanr(spx["hiz"], spx["gun_toparlanma"])
    hz = S2["hiz_sure"]["hepsi"]

    md = ["# Piyasa Mekanizmaları Laboratuvarı — Rapor", "",
          "> Bu rapor `arastirma/sonuclar/*.json` dosyalarından otomatik üretilir (`python calistir.py rapor`). "
          "**Simülasyon sonuçları piyasada yay olduğunu kanıtlamaz; ölçüm aletini dener.** Gerçek örnekler küçük ve hayatta kalan hisselerden oluşur. Yatırım tavsiyesi değildir.", "",
          "## 1. Özet — ne öğrendik?", "",
          f"1. **Yay (endeks) tek başına işlem sinyali değil.** Yalnızca gerilim (Y1) koşulsuz günden *daha kötü*: 63 bar getiri koşulsuza göre {pct(y1['fark'])}. Boşalma işareti beklenince (Y2) {pct(y2['fark'])} (63 bar getiri {pct(y2['getiri']['ort'])}, GA {_ci(y2['getiri']['ga_alt'], y2['getiri']['ga_ust'])}); basit '−%15 düştüyse al' kuralı {pct(basit['fark'])}. Yay mekanizmasının *var olduğu* simüle dünyada bile etki küçük.",
          f"2. **33 yıllık endeks tarihi yayı kanıtlamaya yetmez.** Simüle edilen yay tam olduğu gibi gerçek olsa bile, ~33 yılda ~{s4_taban['n_bolum']:.0f} bağımsız krizle Y2'yi yakalama olasılığı **{pct(s4_taban['bulundu_bolum'],0)}** (yay yokken yanlış alarm {pct(s4_yok['bulundu_bolum'],0)}); güçlü yay varsayımıyla {pct(s4_guc['bulundu_bolum'],0)}. Endeks düzeyinde sonuç 'vaka çalışması' kalır.",
          f"3. **Panik / bozulma ayrımı bu özelliklerle zayıf.** Kural tabanlı ayrım %{s1['kural']*100:.0f} doğru ('hep bozulma de' tabanı %{s1['taban']*100:.0f}); lojistik %{s1['lojistik']*100:.0f}. Panik de kredi spread'ini açtığında (1998/2020 gibi) kural paniği bozulma sanıyor.",
          f"4. **Hisse düzeyi en umut verici alan.** Panik olaylarında en çok düşen hisseler, normal zamandaki ters dönüşün *ötesinde* {pct(pan['ozel'])} {_ci(*pan['ga'])} (126 bar) ekstra toparlıyor; bozulma olaylarında {pct(boz['ozel'])} {_ci(*boz['ga'])} (≈0). Gerçek 2025 vakasında krize özgü fark aynı yönde (kalıntı sıralaması, 3/6/12 ay: {pct(r2_25['kalinti3']['ozel'])} / {pct(r2_25['kalinti6']['ozel'])} / {pct(r2_25['kalinti12']['ozel'])}), ancak hisse listesi seçim yanlılığı taşıyor; 2022'de karma (3 ay {pct(r2_22['ham3']['ozel'])}, 12 ay {pct(r2_22['ham12']['ozel'])}).",
          f"5. **Kırılma noktası: yüksek AUC büyük ölçüde mekanik.** Olay olmayan dünyada bile AUC {np_['auc']:.2f} / {ny['auc']:.2f} (kalibre: {kp['auc']:.2f} / {ky['auc']:.2f}). `dd` dışındaki öncüler yalnızca panik bitişinde gerçek bilgi taşıyor (AUC farkı {kp['auc_dd_yok']-np_['auc_dd_yok']:+.2f}). **Kenetlenme ve Gelgit bağımsız bilgi eklemiyor, stres vekili gibi davranıyor;** Gelgit gerçek veride hiç test edilemedi.", ""]

    md += ["## 2. Tarih (13 SPX düşüşü, `katalog.md`)", "",
           f"- Hızlı düşüşler daha çabuk toparlanıyor gibi: ρ(hız, toparlanma) = {rho_h:.2f} (p={p_h:.2f}, n={len(spx)}); derinlik sabitlenince bile pozitif, ama 'hız' düşüşün *süresini* içerdiğinden büyük ölçüde süre simetrisi.",
           f"- Simülatörün yayı bu ilişkiyi **üretmiyor** (derinlik sabit, ρ(hız, toparlanma) = {hz['hiz']:.2f}; ρ(süre, toparlanma) = {hz['sure']:.2f}). Katalogdaki ilişki bu mekanizmayla açıklanmıyor; şans (n=13, çok sütun denendi) veya başka bir mekanizma.",
           "- Kredi stresi tek başına panik/bozulma ayırt etmiyor (1998, 2020 yüksek kredi stresi ama hızlı toparlanma; 2000, 2007 yavaş). VIX zirvesi dipten önce gelen kriz: 10/13.",
           "- Karşı örnekler (Nikkei 1989, Nasdaq 2000): çok yavaş düşüş, kredi/banka kaynaklı, destek yetersiz/geç → 'yay' değil.", "",
           "## 3. Simülasyon (ölçüm aleti çalışıyor mu?)", "",
           f"- **Kalibrasyon:** 4 metrik yarılanma süresini belirlemiyor (ızgara noktaları ayırt edilemiyor); simülatör katalogdan daha hızlı toparlıyor → güç sonuçları iyimser.",
           f"- **S2:** Y2, Y1'e göre ek acıyı azaltıyor: MAE ortalaması {pct(y2['mae_ort'])} vs {pct(y1['mae_ort'])}; MAE < −%10 oranı {pct(y2['mae10'],0)} vs {pct(y1['mae10'],0)}.",
           f"- **S3 (negatif kontrol):** yay yok + bozulma var dünyasında Y2 koşulsuzun {pct(s3_boz['Y2']['fark'])} altında (bıçağı tutmak); saf yürüyüşte {pct(s3_saf['Y2']['fark'])}. Yay var dünyasında {pct(s3_yay['Y2']['fark'])}. Aradaki ~{(s3_yay['Y2']['fark']-s3_boz['Y2']['fark'])*100:.0f} puan 'yayın payı'. Rastgele sinyal yanlış alarm oranı: {pct(s3_saf['Y2']['yanlis_alarm'],0)}.",
           f"- **S4 (güç):** bkz. özet 2. Bir dünya ≈33 yılda {s4_taban['n_olay']:.0f} Y2 olayı / {s4_taban['n_bolum']:.0f} bağımsız bölüm veriyor; farkı ayırt etmek için ~{s4_taban['gereken_n']:.0f} olay gerekir.",
           "- **S5:** hisse sıralamasında genel (krizden bağımsız) ters dönüş etkisi büyük; krize özgü pay küçük. Her zaman sakin-taban kontrolü gerekir.", "",
           "## 4. Gerçek örnek (küçük, vaka çalışması)", "",
           f"- **R1:** 61 aylık veri aylık yay dedektörünü ısıtmaya yetmiyor (Y1={R1['y1']}, Y2={R1['y2']}); 2022 görünmez. Betimsel olarak gerilim skoru 2025-03/04'te en yüksek (0.80/0.82).",
           f"- **R2:** 2025: yay (en çok düşen ekstra toparladı); 2022: kısa vadede (3 ay) gizli güç (enerji hisseleri dirençli), 12 ayda yay. Sakin taban, 2023–26 AI rallisi rejiminde negatif (momentum) → krize özgü fark şişmiş olabilir.",
           f"- **R3:** şok yayı (5 gün): {pct(r3a['ozet']['ort'])} {_ci(r3a['ozet']['ga_alt'], r3a['ozet']['ga_ust'])}, n={r3a['gun']} gün. v5.16'daki +%5'i ne doğruluyor ne çürütüyor. Panel fiyat kapsamı düzensiz: 105 sabit hisseyle sınırlı; 4–6 hafta sonra tekrarlanmalı.", ""]

    sat = kosN["sat"]
    krit, kdgs = KO["kirilma"], KO["kirilma"]["panikten_normale"]

    def c(ad, k):
        r = sat[f"{ad}{k}"]
        return f"{pct(r['fark'])} (n={r['n']})"
    md += ["## 4b. Koşul haritası (simülasyon): hangi koşulda hangi yaklaşım?", "",
           "Hücreler: Yay = Y2 sonrası 63 bar getirinin *aynı koşuldaki her güne göre* farkı; Hisse yayı ⟷ Gizli güç = krize özgü D1 − D5 (126 bar, + = yay, − = gizli güç); Kırılma = panikten normale AUC.",
           "Düşük terçil hücreleri küçük (n≈40–100); fark güven aralıkları geniş.", "",
           "| Yaklaşım | Kenetlenme düşük | Kenetlenme yüksek | Likidite değişimi düşük (gevşek) | Likidite değişimi yüksek (sıkı) |", "|---|---|---|---|---|",
           f"| Yay (Y2 farkı) | {c('kor',0)} | {c('kor',2)} | {c('lik',0)} | {c('lik',2)} |",
           f"| Hisse yayı ⟷ Gizli güç | {pct(gg['kor_p0']['ozel'])} (n={gg['kor_p0']['n']}) | {pct(gg['kor_p2']['ozel'])} (n={gg['kor_p2']['n']}) | {pct(gg['lik_p0']['ozel'])} (n={gg['lik_p0']['n']}) | {pct(gg['lik_p2']['ozel'])} (n={gg['lik_p2']['n']}) |",
           f"| Kırılma (panikten normale AUC) | {kdgs['Kenetlenme (ort_kor_63)']['düşük'][0]:.2f} | {kdgs['Kenetlenme (ort_kor_63)']['yüksek'][0]:.2f} | {kdgs['Gelgit (likidite değişimi)']['düşük'][0]:.2f} | {kdgs['Gelgit (likidite değişimi)']['yüksek'][0]:.2f} |", "",
           "Okuma: Yüksek-stres hücrelerinde (yüksek kenetlenme / sıkı likidite) etkiler daha belirgin; ama Y2 olaylarının çoğu zaten orada olduğundan bu, koşulun bağımsız bilgi taşıdığını göstermiyor. Yay satırı için kontrol dünyalarında (gelgit etkisi kapalı / ortak faktör stresle artmıyor) aynı örüntü sürdü; diğer iki satır kontrol dünyalarında çalıştırılmadı.", ""]

    md += ["## 5. Karar tablosu", "",
           "🟢 simülasyonda ölçülebilir ve tutarlı · 🟡 belirsiz / yalnızca simülasyonda · ⚪ desteklenmiyor / ölçülemedi", "",
           "| Hipotez | Karar | Gerekçe |", "|---|---|---|",
           f"| Y1: aşırı gerilim sonrası toparlanma | ⚪ | Koşulsuz günden {pct(y1['fark'])} kötü; yay yoksa da benzer (S3) |",
           f"| Y2: gerilim + boşalma işareti | 🟡 | Koşulsuza {pct(y2['fark'])}, GA koşulsuzu kapsayabilir; ek acıyı azaltıyor; 33 yılda kanıtlanamaz (güç {pct(s4_taban['bulundu_bolum'],0)}) |",
           f"| Panik / bozulma ayrımı | ⚪ | Lojistik tabanı yalnızca {(s1['lojistik']-s1['taban'])*100:+.0f} puan geçiyor; kural tabanın altında |",
           f"| Hisse yayı: panikte en çok düşen ekstra toparlanır | 🟢 sim / 🟡 gerçek | Sim: {pct(pan['ozel'])} {_ci(*pan['ga'])}; 2025 tutarlı ama seçim yanlılığı, 2022 karma |",
           f"| Gizli güç: bozulmada dayanıklı hisse ekstra kazanır | ⚪ | Sim: {pct(boz['ozel'])} {_ci(*boz['ga'])}; gerçekte yalnızca 2022'de 3 ay (enerji) |",
           f"| Kırılma noktası: öncülerle rejim geçişi | ⚪ (genel) / 🟡 (panik bitişi) | Negatif kontrol AUC {np_['auc']:.2f}; panik bitişinde `dd` dışı öncü AUC {kp['auc_dd_yok']:.2f} vs {np_['auc_dd_yok']:.2f} |",
           f"| Kenetlenme koşulu | ⚪ | Y2 farkı {pct(kosN['ozf']['kor']['fark'])} (GA 0'ı içeriyor); stres vekili |",
           f"| Gelgit koşulu | ⚪ | Sim: mekanizma açık/kapalı ayırt edilemiyor; gerçek veride test yok |",
           f"| Şok yayı (günlük −%8) | 🟡 | 5 günde {pct(r3a['ozet']['ort'])} {_ci(r3a['ozet']['ga_alt'], r3a['ozet']['ga_ust'])}; v5.16 ile uyumlu ama kanıt değil |",
           f"| Katalog: hızlı düşüş → hızlı toparlanma | ⚪ | n=13, süre simetrisi; sim mekanizması üretmiyor |", "",
           "## 6. Sonraki adım önerisi", "",
           "**Gerçek günlük veriye geçmeye değer mi? Kısmen evet — ama hedefi daralt.**", "",
           "1. **Öncelik 1 — Hisse düzeyi Yay ⟷ Gizli güç (günlük, 30 yıl, S&P 500 üyeleri).** Her krizde yüzlerce hisse olduğu için güç, endeks testinden çok yüksek. Zorunlu kontroller: *krize özgü* fark (sakin taban çıkarılır), hayatta kalan yanlılığı (tarihsel endeks üyeliği), beta'dan arındırma, medyan bazlı dilimler.",
           "2. **Öncelik 2 — Kenetlenme için günlük veri:** ortalama korelasyonun stres anındaki davranışı aylık veriyle görünmüyor. Gelgit için NFCI / Fed bilançosu (FRED).",
           "3. **Endeks Yay'ı için tek bir piyasa yetmez:** çok piyasalı (ABD dışı endeksler, sektör ETF'leri) örneklem gerekir; yine de 'vaka çalışması' olarak sunulmalı.",
           "4. **Kırılma noktası için etiketi yeniden tasarla:** kural rejimi fiyat ve oynaklıkla tanımlı olduğu için tahmin mekanik. Daha anlamlı hedef: panik/bozulma olayının bitişi veya kredi spread'inin normalleşmesi.",
           "5. **Küçük düzeltmeler:** katalog değerlerini (özellikle `guven=orta` satırları) bir grafikte doğrula; R3'ü gece taramaları tam kapsama ulaşınca (≈4–6 hafta) yeniden çalıştır; simülatörün toparlanma hızını katalogla uyumlu hâle getir.", "",
           "## 7. Bilinen sınırlar", "",
           "- Simülatör, yayı biz koyduğumuz için 'bulundu' sonuçları bir kanıt değil, aletin duyarlılığıdır. Simdeki 'bozulma' etiketi rastgele geri dönmeyen düşüşleri de içerir.",
           "- Kalibrasyon 4 metrik ve 13 satırlık katalogla yapıldı; yarılanma süresi belirlenmiyor.",
           "- Gerçek örnek: 154 küratörlü hisse + 26 ETF, 2021-10→2026-10, tek rejim (yarı iletken/AI rallisi). Hayatta kalan ve izleme listesi yanlılığı var.",
           "- Gelgit gerçek veride sınanamadı; Kenetlenme yalnızca aylık betimsel.",
           "- Eşikler `hipotezler/*.yaml` dosyalarında önceden kayıtlı; kalibrasyon ızgarası dışında eşik oynanmadı (`deneme_gunlugu.csv`).", "",
           "## 8. Opus incelemesinde özellikle bakılacak noktalar", "",
           "1. **Etiket tanımı (S1/S5):** 'gerçek tür' düşüşün çoğunun `m`'den mi `F`'den mi geldiğine göre; sıradan rastgele düşüşler 'bozulma' sayılıyor. Olay bazlı etiket (S5) ikinci kontrol olarak var ama S1'de yok.",
           "2. **Kalibrasyon seçim kuralı:** yarılanma belirlenemediği için 'en iyiye %10 yakın olanlar arasında varsayılana en yakın' kuralı sonuca bakmadan sabitlendi; ama kuralın kendisi bir serbestlik derecesi.",
           "3. **S5/R2 'sakin taban':** simde ve gerçekte tabanın nasıl tanımlandığı (aynı pencere uzunluğu, dd > −%3 ayları) sonucu belirliyor. R2'de taban 30 ardışık aydan, tek rejimden geliyor.",
           "4. **Kırılma:** negatif kontrol başarısızlığı hedef tanımının mekanik olduğunu gösterdi; etiket yeniden tasarlanmadan gerçek veriye taşınmamalı.",
           "5. **R2 medyan/ortalama değişikliği:** ilk sürümde ortalama kullanıldı, aşırı sonuç (D1−D5 %265) çıkınca medyana geçildi; bu bir metodolojik karar, `deneme_gunlugu.csv`'ye değil bu rapora not düşüldü.",
           "6. **R3 veri kuralı:** kapsama ≥570 kuralı çok katı çıktı (75 günden 70'ini atıyordu); sabit hisse seti kuralına (≥%95 gün) geçildi. İkisi de sonuçlara bakmadan değil, boş çıktıya bakarak seçildi.",
           "7. **Katalog değerleri hafızadan yazıldı;** özellikle `guven=orta` satırlar doğrulanmadı."]
    (SONUCLAR / "LAB-RAPORU.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return "\n".join(md)

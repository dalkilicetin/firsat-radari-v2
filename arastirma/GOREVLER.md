# Görevler — Laboratuvar aşaması (L0–L8)

**İnternetten veri çekilmez, Actions kullanılmaz.** Üç kaynakla çalışılır:
1. **Tarih** — `tarih/kriz_katalogu.csv`: 13 S&P 500 düşüşü + 2 karşı örnek (Japonya 1989, Nasdaq 2000).
2. **Simülasyon** — yay mekanizması bilinçli olarak eklenmiş yapay piyasalar. Kesin doğru cevap bilindiği için ölçüm aletleri bunlarla ayarlanır.
3. **Örnek veri** — repodaki gerçek veriler:
   - `data/sonuclar.json`: 154 hisse + 26 ETF, 61 aylık kapanış (2021-10 → 2026-10). Bu aralık 2022 ayı piyasasını, 2025 ve 2026 Mart düşüşlerini içerir.
   - Git geçmişindeki 103 gecelik tarama: ~600 hisse için günlük panel (2026-07 → 2026-10).

Görev sırası: L0 → L1 → L2 ⛔ → L3 → L4 → L5 → L6 ⛔ → L7 → L9 → L10 → L8 ⛔. Sonnet'e her görevi şu cümleyle verin:
> `arastirma/CLAUDE.md` ve `arastirma/GOREVLER.md` içindeki **L<n>** bölümünü oku ve uygula. Bitince testleri çalıştır, `claude/mekanizma-arastirma` dalına commit + push yap.

**⛔ DUR** = Opus ile sonuçlar birlikte incelenir. Sonraki adım buna göre ayarlanabilir.

### Öncelik sırası (kullanıcı kararı)
Sadece şu sırayla ilerlenir; 11 mekanizmanın geri kalanı bu aşamada **yapılmaz**:
1. **Yay**: kriz sonrası toparlanma olasılığı ve ek düşüş riski (L3–L6, L7-R1)
2. **Gizli güç**: toparlanmada hangi hisseler öne çıkıyor (L6-S5, L7-R2)
3. **Kırılma noktası**: panikten normale / yükselişten düşüşe geçiş (L9)
4. **Kenetlenme ve Gelgit**: ilk üçünün hangi koşullarda daha iyi çalıştığını gösteren **koşul değişkenleri** (L10). Bağımsız strateji değil.

Amaç tek bir hisse sıralaması değil, "hangi piyasa koşulunda hangi yaklaşım işe yarar" haritası.

### Simülasyon ne işe yarar, ne işe yaramaz
Simülatöre yay mekanizması **biz** koyuyoruz. Bu yüzden simülasyon "piyasada yay var" diye bir kanıt üretmez. Şu üç soruya cevap verir:
- (a) Dedektörlerimiz gerçek bir yayı tanıyabiliyor mu?
- (b) 13 kriz gibi küçük bir örneklemle neyi ayırt edebiliriz (güç analizi)?
- (c) Yay olmayan bir piyasada dedektör yanlış alarm veriyor mu?

Gerçeklik testi sadece tarih ve örnek veriyle yapılır. Raporlar bu ayrımı her zaman açıkça yazar.

---

## L0 · İskelet
- `requirements.txt`: `pandas>=2.2.3 numpy>=2.1 scipy>=1.14.1 statsmodels>=0.14.4 PyYAML>=6.0 pytest>=8.3` (yerel Python 3.13). Kurulum: `pip install -r requirements.txt`
- `.gitignore`: `onbellek/ __pycache__/ .pytest_cache/`
- `pytest.ini`: `testpaths = testler`, `pythonpath = .`
- Paketler (boş `__init__.py`): `mekanizma/{veri,ozellik,motor,sim,mekanizmalar,rapor}`, `testler/`, `sonuclar/`
- `mekanizma/ayarlar.py`:
  - yollar: `KOK` (=arastirma), `REPO` (=KOK.parent), `ONBELLEK`, `SONUCLAR`, `HIPOTEZLER`, `TARIH`
  - `MALIYET_BP={"endeks":10,"hisse":20}`
- `calistir.py` (argparse): `ornek`, `katalog`, `sim kalibre|S1..S5`, `gercek R1|R2|R3`, `rapor`. Henüz yazılmamış komut "henüz yok" yazıp 0 koduyla çıkar.

Kabul: `pip install -r requirements.txt && python -m pytest -q && python calistir.py --help`

## L1 · Örnek veri yükleyici
`mekanizma/veri/ornek.py`:
- `aylik() -> pd.DataFrame`
  - Kaynak: `REPO/data/sonuclar.json` dosyasının `series` ve `etf` alanları. Sütun = sembol, index = ay sonu tarihi (artan).
  - Dikkat: `closes` listesi **yeniden eskiye** sıralı. `closes[0]` = `dateIso` tarihinin ayı (o ay tamamlanmamış olabilir). `closes[k]` = k ay öncesi.
  - Kısa seriler (hisse sonradan halka arz) sona hizalanır, başı NaN kalır.
  - Doğrulama: SPY'ın 2022-09 değeri ≈ 357 ve 2022-01 → 2022-09 düşüşü ≈ %25 olmalı. Bunu teste yaz.
- `profil() -> pd.DataFrame`: `prof` ve `fin` alanlarından `sembol, ad, sektor(industry), mcap`. Sektör ETF eşlemesi gerekmez.
- `gunluk_panel(yenile=False) -> pd.DataFrame` (uzun format: `tarih, sembol, fiyat, mtd, r13w, r52w, hi52, mcap`):
  - `git -C REPO log origin/main --format="%H %ad" --date=short -- data/sonuclar.json` → her commit için `git show <hash>:data/sonuclar.json`.
  - `fiyat` = `quotes[s].price`. Diğer alanlar `screen[s]` içinden.
  - Aynı tarihte birden fazla commit varsa en sonuncusu alınır. SPY her gün dahil olmalı.
  - Sonuç `ONBELLEK/gunluk_panel.parquet` dosyasına yazılır (pyarrow yoksa `pickle`).
  - Geçmiş sığ (shallow) klonsa açık bir hata mesajı ver: `git fetch --unshallow origin main` çalıştırılmalı.
- Testler: `testler/ornek/mini_sonuclar.json` (3 sembol, 5 ay) ile `aylik` hizalaması. `gunluk_panel` testi `subprocess` ile monkeypatch edilir.
- `calistir.py ornek`: Üç tablonun özetini yazar (boyut, tarih aralığı, NaN oranı) → `sonuclar/ornek_veri.md`.

## L2 · Kriz kataloğu incelemesi
`mekanizma/veri/katalog.py` → `katalog()`: CSV'yi okur (`comment="#"`). Türetilen sütunlar:
- `dusus = dip/zirve-1`
- `gun_dibe`, `gun_toparlanma` (dipten eski zirveye), `toplam_gun`: işlem günü, `np.busday_count` ile
- `hiz = dusus / gun_dibe` (günlük ortalama kayıp)
- `sertlik = gun_toparlanma / gun_dibe` (yay benzetmesi: <1 ise geri dönüş düşüşten hızlı)
- `vix_dipten_once`: VIX zirvesi dipten önce mi geldi (gün farkı)
- `dipten_sonra_toparlanma_ay = gun_toparlanma/21`

`tarih/inceleme.py` → `sonuclar/katalog.md` (Türkçe, tablolar):
1. Bütün düşüşler `hiz` sırasına göre bir tabloda.
2. Hız ile toparlanma süresi arasındaki Spearman korelasyonu (n ile birlikte). Ayrıca 2×2 tablo: hızlı/yavaş × kısa/uzun toparlanma. Bölme noktası medyan.
3. Resesyon E/H, kredi stresi ve politika tepkisi gruplarına göre medyan toparlanma süresi.
4. VIX zirvesi ile dip ilişkisi. Kaç krizde VIX zirvesi dipten önce geldi? (Yani "VIX zirvesi = dip" doğru mu?)
5. **"O anda bilinebilir" ayrımı.** Her sütun ya **gerçek zamanlı bilinir** (hız, VIX, kredi) ya da **sonradan bilinir** (dip tarihi, NBER resesyon ilanı, toparlanma) diye etiketlenir. Sadece ilk gruptan çıkan desenler hipotez sayılır.
6. Karşı örnekler: Japonya 1989 ve Nasdaq 2000'in hangi özellikleri "yay olmayan" türü ayırıyor?
7. Sonda **"Üretilen hipotezler"** listesi. Örnek: "Hızlı düşüşler (günde > %0,4) daha hızlı toparlanır." Uyarı: n = 13, bu bir test değildir.

Testler: Türetilen sütunlar için 1–2 elle hesaplanmış satır kontrolü.

**⛔ DUR**: `sonuclar/katalog.md` dosyasını Opus'la oku. Üretilen hipotezler L5/L6'nın odağını belirler.

## L3 · Simülatör
`mekanizma/sim/piyasa.py`. Yapı: `Ayar` dataclass'ı ve `simule(ayar, tohum) -> Dunya` fonksiyonu. Günlük adım, 252 gün = 1 yıl.

**Piyasa** (log fiyat = temel değer + sapma):
- `F` (temel değer): sürüklenme `mu=0.07/252`, oynaklık `sF=0.10/√252`.
  - **Bozulma olayları**: Poisson oranı `lam_B=1/12` (yılda). Büyüklük `s_B~U(0.20,0.45)` (log kayıp), `D_B~U(120,400)` gün boyunca doğrusal dağıtılır.
  - Bozulmanın `rho_B=0.3` katı ayrıca sapmaya (`m`) şok olarak eklenir: gerçek bozulmada da aşırı tepki olur.
- `m` (sapma = yay gerilimi): OU süreci `m[t+1]=m[t]*(1-kappa)+sm*eps+sok`. `kappa=ln2/yarilanma`, `yarilanma=60` gün, `sm=0.004`.
  - **Panik olayları**: `lam_P=1/5`, büyüklük `s_P~U(0.10,0.35)`, `D_P~U(10,50)` günde eklenir.
- Stres oynaklığı: `sigma_t = 0.008*(1 + 4*max(-m,0) + 1.5*bozulma_aktif)`. Günlük getiri = `ΔF + Δm + sigma_t*eps2`. Fiyat bundan birikimli hesaplanır. Not: `eps2` gürültüsü F'ye eklenir, yani kalıcıdır.
- `vix = clip(100*√252*ewm_std(getiri, halflife=10)*1.15 + korku*100*max(-m,0), 9, 90)`, `korku=0.5`.
- `kredi`: AR(1) `c[t+1]=c[t]+0.05*(hedef-c[t])+0.03*eps`. `hedef = 1.8 + 8*bozulma_birikimi + panik_kredi*max(-m,0)`. `bozulma_birikimi` = aktif ve son 1 yılda biten bozulmaların gerçekleşmiş kaybı, 1 yıl yarılanmayla söner. `panik_kredi=2` (duyarlılık testinde 0–8; 1998/2020 gibi kredi spread'i açılan panikler için).
- `likidite` (Gelgit vekili, NFCI gibi; yüksek = sıkı): AR(1), yarılanma 120 gün, `sl=0.03`. Panik ve bozulma şokları değeri yükseltir. `mu`'ya `-0.02*likidite` eklenir (gevşek likidite biraz daha yüksek sürüklenme). Gelgit etkisi **ayrıca** yaylanma hızını değiştirir: `kappa *= (1 - 0.4*clip(-likidite_degisim_63, -1, 1))` (likidite gevşerken yay daha hızlı toparlar). Bu varsayım `ayar.gelgit_etkisi` ile kapatılabilir (kontrol deneyi için).
- `sahm`: Bozulma başladıktan `U(60,150)` gün sonra 1 olur, bittikten 120 gün sonra 0 olur.

**Ortak faktör ve korelasyon** (Kenetlenme için): hisse günlük gürültüsü `sigma_i*(sqrt(c_t)*z_ortak + sqrt(1-c_t)*eps_i)`. `c_t = 0.15 + 0.6*stres_t`, `stres_t = clip(max(-m,0)*3 + 0.5*bozulma_aktif, 0, 1)`. Böylece stres arttıkça hisseler kenetlenir.

**Hisseler** (`n_hisse=200`):
- `beta~U(0.6,1.6)`, `kalite~U(0,1)`, `asiri=beta*U(0.7,1.3)`
- `F_i`: günlük `mu + beta*(ΔF_genel - mu - bozulma_akisi) - (0.4+1.2*(1-kalite))*bozulma_akisi + 0.015*eps`
  - Bozulmada kalitesiz şirket kalıcı olarak daha çok kaybeder.
- `m_i = asiri*m + OU_idio`: kendi OU'su, yarılanma 40, `sm=0.01`.
  - Panikte aşırı tepki veren hisse daha çok düşer ama tamamen geri döner.
- Fiyat `P_i = exp(F_i + m_i)`.

**Çıktı** (`Dunya`): `endeks` (DataFrame: `adj, F, m, vix, kredi, sahm`), `hisseler` (geniş adj), `meta` (beta, kalite, asiri), `olaylar` (gerçek cevap: `baslangic, tur, buyukluk, sure`), `ayar`.

Testler:
- Tohum sabitken çıktı aynı.
- `yarilanma=10**9` ve `lam_P=0` iken `m` ortalamaya dönmez.
- Panik olayından 3 yarılanma sonra `m` ortalaması ≈ 0.
- 60 yıllık simülasyon < 10 sn.

## L4 · Ortak özellikler + motor (frekanstan bağımsız: "bar" = gün veya ay)
- `ozellik/fiyat.py`: `dusus(adj, n)`, `getiri(adj, n)`, `vol(adj, n)`, `zskor(x, n)`, `ust_oran(adj_genis, n)` (SMA_n üstündeki oran), `beta(hisse, endeks, n)`. **Genişleyen** yüzdelik: `yuzdelik_genisleyen(x)`.
- `motor/sonuc.py` (geleceğe bakan tek modül): `ileri_getiri(adj, ufuklar)` (t+1 girişli), `mae`, `toparlanma_suresi`.
- `motor/istatistik.py`: `blok_bootstrap_ga`, `ozet` (n, ort, medyan, isabet, GA).
- `motor/olay.py`:
  - `ayikla(sinyal, bekleme)`
  - `olay_testi(adj, sinyal, ufuklar, bekleme, kosullar: dict[str, Series]|None)` → koşulsuz kıyas + koşul kırılımı + olay tablosu
  - `isi_haritasi(adj, x, y, x_kova, y_kova, ufuk, bekleme)`
- `testler/test_sizinti.py`: t sonrası veri çöp değerle değiştirilince t'deki özellik değişmemeli. Bunu bütün `ozellik` fonksiyonlarına parametrik olarak uygula.

## L5 · Yay dedektörü
`hipotezler/yay.yaml` (önceden kayıt):
```yaml
gerilim: {dd_n: 252, dd_esik: -0.10, bilesik_yuzdelik: 0.90, bilesenler: [dd, vix_z, genislik]}
tur:     {kredi_degisim_n: 60, kredi_esik: 0.5, hiz_n: 20}      # bozulma = kredi60>esik VEYA sahm==1
bosalma: {vix_dusus: 0.20, itki_alt: 0.15, itki_ust: 0.50, itki_n: 10, teyit_n: 10, pencere: 20}
ufuklar: [21, 63, 126, 252]
ana_ufuk: 63
bekleme: 63
aylik:   {dd_n: 12, hiz_n: 3, ufuklar: [3, 6, 12, 24], bekleme: 3}   # örnek veri için
```
`mekanizmalar/yay.py`:
- `ozellikler(endeks_df, hisseler=None)`: `dd, hiz, vix_z, genislik (1-ust_oran(200)), kredi60, sahm, vix_dusus, itki, teyit`. Eksik sütun varsa o bileşen atlanır.
- `gerilim_skoru`: bileşenlerin genişleyen yüzdeliklerinin ortalaması.
- `tur_tahmini`: panik veya bozulma.
- `sinyaller`:
  - `Y1` = gerilim durumu
  - `Y2` = gerilim durumu son `pencere` gün içinde gerçekleşti VE boşalma işaretlerinden en az biri var
  - `basit` = `dd <= -0.15`
- `durum()`: son gün için skor, tür ve bileşenler.
- Aylık mod: `aylik` parametreleriyle aynı sınıf. VIX ve kredi yoksa `dd, hiz, genislik` kullanılır.

Testler: Simülasyonda panik olaylarının ≥ %70'i Y1 ile yakalanır. Sızıntı testi.

## L6 · Simülasyon deneyleri
`mekanizma/sim/deneyler.py`. Her deney bir `sonuclar/sim_<ad>.md` + `.json` üretir. Her rapor şu cümleyle başlar: **"Bu sonuç simülasyondur; piyasada yay olduğunu kanıtlamaz, ölçüm aletini dener."**

1. **Kalibrasyon** (`sim kalibre`):
   - 60 yıl × 20 tohum simüle edilir.
   - Endeksteki ≥%10 düşüş bölümleri çıkarılır. Dağılımları (düşüş, gün_dibe, gün_toparlanma, sertlik) katalogla (`piyasa==SPX`) yan yana karşılaştırılır.
   - Küçük ızgara: `yarilanma∈{30,60,120}`, `lam_P∈{1/3,1/5,1/8}`, `s_B` üst sınırı `∈{0.35,0.45}`.
   - Mesafe = 4 metriğin medyan ve çeyrekliklerinde göreli fark toplamı. En yakın ayar `sonuclar/sim_ayar.yaml` dosyasına yazılır. Diğer deneyler bu ayarı kullanır.
   - Her ızgara noktası `deneme_gunlugu.csv` dosyasına bir satır olarak yazılır.
2. **S1 Ayırt edilebilirlik**:
   - Her Y1 olayında gerçek tür: olay günündeki düşüşün çoğu `m`'den geliyorsa panik, `F`'den geliyorsa bozulma.
   - Kural tabanlı `tur_tahmini` ve lojistik regresyon karşılaştırılır. Özellikler: `hiz, vix_z, kredi60, genislik, sahm`. Eğitim tohumları 0–9, test tohumları 10–19.
   - Çıktılar: karışıklık matrisi, isabet, özellik katsayıları.
   - Duyarlılık: `panik_kredi∈{0,2,4,8}`. Panik kredi spread'ini de açarsa ayrım bozuluyor mu?
3. **S2 Boşalma ve ek acı**:
   - Y1 tek başına ve Y1+her boşalma işareti (`vix_dusus, itki, teyit`, hepsi) karşılaştırılır.
   - Ölçümler: 63g getiri, **MAE** (girişten sonraki en kötü ek düşüş), isabet.
   - Soru: Hangi işaret "toparlanmadan hemen önceki bölgeyi" en iyi yakalıyor?
4. **S3 Sahte yay (negatif kontrol)**:
   - `lam_P=0`, `rho_B=0`, `yarilanma=1e9` (yay yok, sadece sürüklenme + bozulma).
   - Y1 getirisi ile koşulsuz getiri arasındaki fark ≈ 0 olmalı. Ayrıca rastgele 200 sinyalle yanlış alarm oranı ölçülür.
   - Sonuç "dipten almak, sırf piyasa uzun vadede yükseldiği için iyi görünebilir" uyarısını sayısal olarak gösterir.
5. **S4 Güç analizi**:
   - 33 yıllık (≈1990–2023) 500 dünya simüle edilir. Her dünyada bölüm sayısı ve Y1'in koşulsuza göre farkının %90 GA'nın sıfırı dışlayıp dışlamadığı ölçülür.
   - Tablo: `yarilanma × lam_P` → bulunma olasılığı.
   - Soru: "Gerçek veride ~13 krizle bu etkiyi görme şansımız ne?"
6. **S5 Hisse yayı ⟷ Gizli güç**:
   - Her bölümde değerlendirme günü = Y2'nin ilk günü (gerçek dip kullanılmaz).
   - Hisseler dönem getirisine göre 5 dilime ayrılır. Ayrıca beta'dan arındırılmış kalıntıya göre ayrı bir 5 dilim yapılır.
   - Evrene göre 63/126/252g ileri getiri hesaplanır.
   - Kırılımlar: gerçek türe göre ve `tur_tahmini` ile tahmin edilen türe göre. Tür yanlış tahmin edilince ne kaybediliyor?

**⛔ DUR**: Opus ile `sim_*.md` dosyaları birlikte okunur.

## L7 · Gerçek örnek kontrolü (küçük ama gerçek)
`mekanizma/gercek.py`, çıktı `sonuclar/gercek_<ad>.md`:
- **R1 Aylık endeks ve sektör yayları**:
  - SPY + sektör/tema ETF'leri + `VGK EWJ EEM MCHI`.
  - Aylık Y1/Y2 durum çizelgesi (tablo: ay × ETF, gerilim skoru).
  - 2022, 2025-03/04 ve 2026-03 bölümleri. Her bölüm için yay dedektörünün ne zaman alarm verdiği ve sonrasında ne olduğu (3/6/12 ay).
  - Katalogdaki 2022 ve 2025 satırlarıyla karşılaştırma.
- **R2 2022 ve 2025 doğal deneyleri — Hisse yayı ⟷ Gizli güç** (154 hisse + 26 ETF):
  - 2022: zirve ayı = SPY 2021-12. Değerlendirme ayı üç varyantla:
    - (a) ilk −%20 ayı (2022-06)
    - (b) dedektörün Y2 ayı
    - (c) gerçek dip 2022-09. **Bu "hile/üst sınır" diye etiketlenir.**
  - 2025: zirve 2025-01/02, değerlendirme = 2025-04 ve Y2 ayı.
  - Dilimler dönem getirisine göre. İleri 3/6/12/24 ay, eşit ağırlıklı evrene göre.
  - Beta: 2025 için dönem öncesi 36 aydan hesaplanır. 2022 için yeterli geçmiş yok (veri 2021-10'da başlıyor). Bu yüzden 2022'de ham getiri kullanılır ve açıkça yazılır.
  - Beklenti (simülasyon S5'ten): 2022 bozulma türü → gizli güç kazanmalı; 2025 panik türü → hisse yayı kazanmalı. Sonuç bu beklentiyle karşılaştırılır.
  - Sektör düzeyi: 2022'de en az düşen ETF'ler (XLE vb.) ve en çok düşenler (ARKG, IGV vb.) sonra ne yaptı?
  - Uyarı: 154 hisse küratörlü (teknoloji ağırlıklı) ve hayatta kalanlardan oluşuyor.
- **R3 Günlük panel: şok yayı**:
  - 103 günde tek günlük fiyat düşüşü ≤ −%8 (ve ≥ −%50) olan olaylar → 5/10/20 gün sonra SPY'a göre getiri.
  - Kırılım: `r52w>0` (trendde) mi, değil mi.
  - Ekim 2026 ortası satışı ayrıca incelenir.
  - v5.16'daki "şok 5 günde +%5" bulgusu tekrar ediyor mu?

## L8 · Laboratuvar raporu
`rapor/lab_raporu.py` → `sonuclar/LAB-RAPORU.md` (tek dosya, Türkçe, sade dil, GitHub'da okunur):
1. Özet: 5 madde ("ne öğrendik").
2. Tarih: katalogdan üretilen hipotezler.
3. Simülasyon: ölçüm aleti çalışıyor mu, kaç krizle neyi görebiliriz?
4. Gerçek örnek: 2022 / 2025 / 2026 ne söylüyor?
4b. Koşul haritası: satırlar Yay / Gizli güç / Kırılma noktası, sütunlar kenetlenme düşük-yüksek ve likidite gevşek-sıkı. Hücre = hangi koşulda daha iyi çalıştığı.
5. Karar tablosu: her hipotez için 🟢 umut verici / 🟡 belirsiz / ⚪ desteklenmiyor + tek cümle gerekçe.
6. Sonraki adım önerisi: gerçek günlük veriye (ILERIDE-GERCEK-VERI.md) geçmeye değer mi, hangi mekanizmayla?

**⛔ DUR — Opus son inceleme.**

---

## L9 · ⚡ Kırılma noktası (üçüncü öncelik)
Hedef: panikten normale geçişi ve yükselişten düşüşe geçişi öncüllerle tahmin etmek.
- `hipotezler/kirilma.yaml`: `rejim: {vol_n: 63, vol_esik: 0.70, trend_n: 200, min_sure: 10}`, `hedef_ufuklar: [21, 63]`, `modeller: [lojistik]`, `egitim_tohum: [0..9]`, `test_tohum: [10..19]`.
- `ozellik/rejim.py`: `kural_rejim(adj, vol_n, vol_esik, trend_n, min_sure)` → 4 rejim (`sakin_yukselis, oynak_yukselis, sakin_dusus, oynak_dusus`). Vol yüzdeliği **genişleyen** pencereyle. Histerezis: yeni rejim `min_sure` bar sürmedikçe eski korunur.
- `mekanizmalar/kirilma.py`: öncüller `genislik_ayrisma` (endeks 63g getiri > 0 iken 200g üstü oran 63 günde 10+ puan düştü), `vix_degisim_21`, `vix_vol_21`, `kredi_egim_60`, `ort_korelasyon_63` ve `korelasyon_degisim_21` (L10 ile ortak), `momentum_farki` (12-1 Q5−Q1 son 21g getirisi), `dd`.
- Hedefler: (a) 21/63 bar içinde `oynak_dusus → sakin_yukselis|oynak_yukselis` geçişi (panikten normale), (b) `sakin_yukselis|oynak_yukselis → *_dusus` geçişi.
- Model: sklearn yerine `statsmodels` Logit (sklearn kurulu değil). Eğitim tohumlarında eğitilir, test tohumlarında ölçülür. Ölçümler: AUC (Mann-Whitney ile elle), Brier, üst %10 tahminde gerçekleşme oranı / koşulsuz oran, katsayı işaretleri (tohumlar arası kararlılık).
- Simülasyon kontrolü: `lam_P=0, lam_B=0` dünyada AUC ≈ 0.5 olmalı (negatif kontrol).
- Gerçek örnek: aylık SPY serisinde 2022 sonu ve 2025-04 sonrası geçişlerin dedektörde görünüp görünmediği (R1 ile birleşik tablo).
- Çıktı: `sonuclar/kirilma.md` + `.json`.

## L10 · 🔗 Kenetlenme + 🌊 Gelgit: koşul değişkenleri (dördüncü öncelik)
Bunlar ayrı strateji değil. Soru: **Yay, Gizli güç ve Kırılma noktası hangi Kenetlenme/Gelgit koşulunda daha iyi çalışır?**
- `ozellik/korelasyon.py`: `ort_ikili_korelasyon(getiri_genis, n=63)` (ortalama ikili korelasyon, hız için eşit bölünmüş rastgele olmayan 60 hisse alt kümesi), `kesitsel_dagilim(getiri_genis, n=21)`.
- `ozellik/likidite.py`: `likidite_degisim(seri, n=63)` (sim `likidite` serisi; gerçekte NFCI olurdu).
- `mekanizmalar/kosullar.py`: iki koşul değişkenini **genişleyen** üçte birlik dilimlere ayırır (düşük/orta/yüksek).
- `sim/deneyler.py` → `S6`: Yay Y2 olaylarının 63g getirisi ve MAE'si, olay günündeki korelasyon üçte biri ve likidite değişimi işaretine göre kırılım. Gizli güç Q5−Q1 farkı korelasyon üçte birine göre. Kırılma AUC'si koşullara göre. Kontrol: `gelgit_etkisi=False` ve `c_t` sabit iken kırılımın farksız çıkması.
- Gerçek örnek (aylık, 154 hisse): ortalama ikili korelasyon (12 aylık pencere) 2022 ve 2025'te yükseliyor mu? Likidite için veri yok, bu kısım "yapılamadı" diye açıkça yazılır.
- Çıktı: `sonuclar/kosullar.md` + `.json`.

## Sonra (laboratuvar başarılı olursa)
- Aynı laboratuvara diğer mekanizmaları ekle:
  - Baraj: simülatöre oynaklık sıkışma rejimi eklenir.
  - Kenetlenme: simülasyonda ortak faktörden doğal olarak oluşan korelasyon ölçülür.
  - Gelgit: likidite durumu `mu`'yu değiştiren bir durum değişkeni olur.
- Ardından `ILERIDE-GERCEK-VERI.md`: gerçek 30 yıllık günlük veri. Kullanıcının bilgisayarında da çalıştırılabilir.

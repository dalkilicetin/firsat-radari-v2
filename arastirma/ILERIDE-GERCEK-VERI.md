# İLERİDE — Gerçek günlük veri ile tam test (şimdilik ASKIDA)

> Bu dosya şimdi uygulanmayacak. Actions kotası dolu ve günlük veri indirmeye şimdilik gerek görülmedi.
> Önce `GOREVLER.md` içindeki laboratuvar aşaması (L0–L8) yapılacak. Laboratuvar sonuçları umut verirse bu dosya yeniden ele alınır.
> Veri, kullanıcının kendi bilgisayarında `python calistir.py veri` ile de çekilebilir; Actions şart değil.

Her görev tek oturumda bitecek şekilde ayrıldı. Sonnet'e şu cümleyle verin:

> `arastirma/CLAUDE.md` ve `arastirma/GOREVLER.md` içindeki **G<n>** bölümünü oku ve uygula. Bitince testleri çalıştır, `claude/mekanizma-arastirma` dalına commit + push yap.

Sıra önemli. Her görev, önceki görevlerin dosyalarını kullanır. **⛔ DUR** işaretli yerlerde Opus incelemesi yapılır.

---

# FAZ 0 — Altyapı

## G0 · İskelet
Oluştur:
- `arastirma/requirements.txt` (sabit sürümler):
  `pandas==2.2.3 numpy==2.1.3 scipy==1.14.1 pyarrow==18.1.0 requests==2.32.3 PyYAML==6.0.2 statsmodels==0.14.4 scikit-learn==1.5.2 Jinja2==3.1.4 pytest==8.3.4`
- `arastirma/.gitignore`: `onbellek/`, `__pycache__/`, `.pytest_cache/`
- `arastirma/pytest.ini`: `testpaths = testler`, `pythonpath = .`
- Bölüm 5'teki (PLAN.md) bütün paket klasörleri ve boş `__init__.py` dosyaları.
- `arastirma/calistir.py`: `argparse` alt komutları `veri`, `saglik`, `test <ad|hepsi>`, `pano`. Şimdilik "henüz yok" yazıp çıkar. `--kaynak-yok` bayrağı ekle: ağ yerine `testler/ornek/` kullanılır.
- `mekanizma/ayarlar.py`: yol sabitleri (`KOK`, `ONBELLEK`, `SONUCLAR`, `HIPOTEZLER`, `YAYIN = KOK.parent/"mekanizma"`), `MALIYET_BP = {"endeks":10,"hisse":20}`, `KESIF_BITIS = "2009-12-31"`.
- `testler/sentetik.py`:
  - `rastgele_yuruyus(n_gun, n_hisse, tohum, yillik_getiri=0.07, yillik_vol=0.18) -> pd.DataFrame` (geniş adj, iş günü indeksi 1990-01-02'den başlar)
  - `yay_ekle(seri, olay_gunleri, dusus=-0.25, sure=40, toparlanma=0.20, toparlanma_suresi=60)`: belirtilen günlerde düşüş ve ardından toparlanma enjekte eder.
  - `ohlcv_uret(adj)`: kapanıştan makul OHLCV üretir.

Kabul: `python -m pytest -q` çalışır (0 test bile olsa hata vermez). `python calistir.py --help` çalışır.

## G1 · Veri kaynakları + önbellek + evren
`mekanizma/veri/kaynaklar.py`:
- `yahoo_gunluk(sembol, baslangic="1980-01-01") -> pd.DataFrame`. URL: `https://query1.finance.yahoo.com/v8/finance/chart/{sembol}?period1={unix}&period2={unix}&interval=1d&events=div%2Csplit&includeAdjustedClose=true`, başlık `User-Agent: Mozilla/5.0`. `chart.result[0].timestamp` ve `indicators.quote[0]` ile `indicators.adjclose[0].adjclose` okunur. Tarih = UTC zaman damgasının borsa saat dilimindeki günü (`meta.exchangeTimezoneName`). Tamamen NaN satırlar atılır.
- `stooq_gunluk(sembol)`: `https://stooq.com/q/d/l/?s={sembol_stooq}&i=d`. Sembol eşlemesi: `AAPL→aapl.us`, `^GSPC→^spx`, `^NDX→^ndx`. adj=close (Stooq düzeltilmiş verir).
- `twelvedata_gunluk(sembol)`: `TWELVEDATA_KEY` ortam değişkeni, `outputsize=5000`. Sadece son çare.
- `gunluk(sembol)`: Yahoo → Stooq → TwelveData sırasıyla dener, başarılı kaynağı `df.attrs["kaynak"]` alanına yazar. Hata durumunda 2 s/4 s/8 s bekleyip yeniden dener. İstekler arasında 0,35 s bekler.
- `fred(seri) -> pd.Series`: `https://fred.stlouisfed.org/graph/fredgraph.csv?id={seri}`. `"."` değeri NaN olur (v5.16'daki hatanın aynısı, dikkat).

`mekanizma/veri/onbellek.py`:
- Her sembol `onbellek/fiyat/{guvenli_ad}.parquet` dosyasına, makro seriler `onbellek/makro/{seri}.parquet` dosyasına yazılır. `guvenli_ad`: `^`→`_I_`, `/`→`_`, `.`→`_D_`.
- `guncelle(sembol)`: Dosya varsa son 10 günü yeniden çeker ve birleştirir (yeni değer kazanır). Çakışan günlerde adj oranı %0,5'ten fazla değiştiyse (geriye dönük düzeltme, bölünme/temettü) seriyi baştan çeker.
- `oku(sembol)`, `oku_makro(seri)`.

`mekanizma/veri/evren.py`:
- `ENDEKSLER = ["^GSPC","^NDX","^RUT","^VIX","^VIX3M","^GDAXI","^N225","^FTSE","XU100.IS"]`
- `ETFLER = ["SPY","QQQ","IWM","RSP","XLK","XLF","XLE","XLV","XLI","XLY","XLP","XLU","XLB","XLRE","XLC"]`
- `MAKRO = ["VIXCLS","BAA10Y","T10Y3M","T10Y2Y","NFCI","WALCL","DFII10","SAHMREALTIME","DTWEXBGS"]`
- `hisse_evreni()`: `../data/sonuclar.json` → `screen` anahtarları ∪ `../universe-fallback.txt` ∪ `dead` anahtarları. `BRK.B` → Yahoo'da `BRK-B`. Sıralı liste döner.
- `SEKTOR_ETF`: `sonuclar.json → prof[s].industry` bilgisini 11 sektör ETF'sine eşleyen sözlük. Eşlenemeyenler `None` olur. Eşleme tablosunu dosyada açıkça yaz.

`mekanizma/veri/__init__.py` → `class Veri`: `fiyat(sembol)`, `genis(alan, semboller)`, `makro(seri)`, `evren`. Örnek mod (`--kaynak-yok`) için `testler/ornek/` içinden okur.

`testler/ornek/`: Sentetik veriden üretilmiş 5 hisse + `^GSPC` + `^VIX` + `BAA10Y` parquet dosyaları (≤300 KB toplam). Bunları üreten `testler/ornek_uret.py` de eklenir.

Testler: Yahoo JSON ayrıştırma (sahte yanıt), FRED `"."` işleme, kaynak yedeğine geçiş (Yahoo hata verince Stooq), önbellek birleştirme ve adj değişince baştan çekme, sembol adı dönüşümleri.

## G2 · Veri sağlığı + Actions iş akışı
`mekanizma/veri/saglik.py` → `kontrol(df, sembol) -> list[str]` sorun listesi döner:
- ≥%50 tek günlük adj değişimi, bölünme şüphesi
- 5+ ardışık gün aynı kapanış
- `close<=0`
- NYSE iş günlerine göre >%5 eksik gün (pandas `bdate_range` yeterli)
- Son veri 5 iş gününden eski

`saglik_raporu()` bütün evreni tarar ve `sonuclar/veri_sagligi.json` dosyasına yazar: `{sembol: {"kaynak", "ilk", "son", "n", "sorunlar": [...]}, "ozet": {...}}`. Sorunlu hisseler `karantina` listesine girer ve sonraki adımlarda kullanılmaz.

`calistir.py veri` → evrenin hepsini günceller. `calistir.py saglik` → raporu yazar.

`.github/workflows/mekanizma.yml` (repo kökünde):
```yaml
name: Mekanizma Arastirma
on:
  schedule: [{cron: "17 6 * * 6"}]   # Cumartesi
  workflow_dispatch:
    inputs:
      komut: {description: "test hedefi (hepsi / yay / ...)", default: "hepsi"}
permissions: {contents: write}
concurrency: {group: mekanizma, cancel-in-progress: false}
jobs:
  calis:
    runs-on: ubuntu-latest
    timeout-minutes: 150
    defaults: {run: {working-directory: arastirma}}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: "3.11", cache: pip, cache-dependency-path: arastirma/requirements.txt}
      - run: pip install -r requirements.txt
      - uses: actions/cache@v4
        with:
          path: arastirma/onbellek
          key: onbellek-${{ github.run_id }}
          restore-keys: onbellek-
      - run: python -m pytest -q
      - run: python calistir.py veri
        env: {TWELVEDATA_KEY: "${{ secrets.TWELVEDATA_KEY }}", SEC_UA: "${{ secrets.SEC_UA }}"}
      - run: python calistir.py saglik
      - run: python calistir.py test ${{ github.event.inputs.komut || 'hepsi' }}
      - run: python calistir.py pano
      - name: Commit
        working-directory: .
        run: |
          git config user.name "firsat-radari-bot"; git config user.email "bot@users.noreply.github.com"
          git add arastirma/sonuclar mekanizma arastirma/deneme_gunlugu.csv || true
          git diff --cached --quiet || git commit -m "Mekanizma araştırması $(date -u +%F)"
          git pull --rebase origin ${{ github.ref_name }} && git push origin HEAD:${{ github.ref_name }}
```
Not: Henüz yazılmamış komutlar "henüz yok" diyerek 0 koduyla çıkmalı ki iş akışı yeşil kalsın.

Kabul: Testler yeşil. Kullanıcı Actions'ı bu daldan elle çalıştırınca `sonuclar/veri_sagligi.json` commitlenir. **⛔ DUR**: Kullanıcı çalıştırsın, sağlık raporunu Opus'a okutsun. Kaynak sorunu varsa düzeltilir.

## G3 · Sonuç ve istatistik çekirdeği
`motor/sonuc.py` (geleceğe bakan TEK modül):
- `ileri_getiri(adj: Series|DataFrame, ufuklar=(5,21,63,126,252)) -> DataFrame`: t satırında `adj[t+1+h]/adj[t+1]-1`. Veri yoksa NaN.
- `mae(adj, ufuk)`: t+1 girişinden sonra ufuk boyunca en kötü düşüş, `min(adj[t+1..t+1+h])/adj[t+1]-1`.
- `mfe(adj, ufuk)`: en iyi yükseliş.
- `toparlanma_suresi(adj)`: t+1'den sonra fiyatın t'deki 252 günlük zirveye ilk dönüşüne kadar geçen iş günü. Dönmediyse NaN.
- `goreli(ileri_hisse, ileri_kiyas)`: fark.

`motor/istatistik.py`:
- `blok_bootstrap_ga(x, blok=None, n=2000, ga=0.90, tohum=0)`: Hareketli blok bootstrap. Blok uzunluğu verilmezse `ceil(n**(1/3))`. Ortalama için alt/üst sınır döner.
- `newey_west_t(x, gecikme=None)`: statsmodels `HAC` kullanır.
- `holm(p_listesi)`: düzeltilmiş p değerleri.
- `deflated_sharpe(sr, n_deneme, n_gozlem, carpiklik, basiklik)`: Bailey & López de Prado 2014 formülü. Docstring'e formülü yaz.
- `ozet(x)`: `n, ortalama, medyan, isabet (x>0 oranı), std, min, max, ga_alt, ga_ust`.

Testler: Bilinen dizide ileri getiri ve MAE elle doğrulanır. `ileri_getiri` son h satırda NaN döner. Bootstrap GA, büyük örneklemde normal GA'ya yakın çıkar.

## G4 · Olay çalışması motoru
`motor/olay.py`:
- `ayikla(sinyal: pd.Series[bool], bekleme: int) -> DatetimeIndex`: İlk True alınır, sonraki `bekleme` gün yok sayılır.
- `bolumle(olaylar, bosluk=126)`: Aralarında 126 günden az olan olaylar aynı **bölüme** girer. Bölüm kimliği döner.
- `olay_testi(fiyat_adj, sinyal, h: Hipotez, rejim: Series|None=None, kiyas_sinyaller: dict[str,Series]={}) -> dict`:
  - ileri getiri, MAE, MFE, toparlanma (her ufuk)
  - **koşulsuz** dağılım (tüm günler) ve her `kiyas_sinyaller` için aynı istatistikler (basit rakip)
  - `kesif` (≤ `KESIF_BITIS`) / `dogrulama` ayrımı
  - bölüm tablosu: her bölüm için ilk sinyal tarihi, o andaki bileşenler, 21/63/126 getiri, MAE
  - rejim verildiyse rejime göre kırılım
  - maliyet: giriş + çıkış `MALIYET_BP` düşülür
  - Dönen sözlük JSON'a yazılabilir olmalı (tarihler ISO metin).
- `isi_haritasi(fiyat_adj, x: Series, y: Series, x_kovalar, y_kovalar, ufuk, bekleme)`: Her hücrede `n`, `bolum_n`, `medyan`, `isabet`, `mae_medyan`.

Testler: Sentetik veride `yay_ekle` ile 8 olay enjekte edilir. Gerilim sinyali (dd ≤ −%20) bu olayları bulmalı ve 63 günlük ortalama koşulsuzdan anlamlı yüksek çıkmalı. Saf rastgele yürüyüşte GA sıfırı içermeli (tohum sabit).

## G5 · Kesitsel test motoru
`motor/kesit.py`:
- `kesit_testi(skor: DataFrame[tarih x sembol], adj: DataFrame, h: Hipotez, dilim=5, frekans="ME", kiyas="esit") -> dict`:
  - Her ay sonu: skoru olan hisseler (min 30) dilimlere ayrılır.
  - Dilim getirisi = eşit ağırlıklı ileri getiri − evren eşit ağırlıklı ileri getirisi (`sonuc.ileri_getiri`, ufuklar h'den).
  - Ölçümler: dilim ortalamaları, Q5−Q1 farkı (Newey-West t, gecikme = ufuk/21), Spearman IC ortalaması ve IC t-değeri, ay bazında isabet, dilim devir hızı, maliyet sonrası fark (`devir × 2 × MALIYET_BP`)
  - keşif/doğrulama ayrımı ve rejime göre kırılım (opsiyonel `rejim` serisi)
- `olay_kesit_testi(...)`: Belirli olay tarihlerinde (Gizli güç / Hisse yayı için) dilim testi. Bölüm tablosu da üretir.

Testler: Sentetik veride skor = gelecek getiriyle zayıf korelasyonlu bir sinyal (sadece test için) olduğunda IC > 0 ve t > 2 çıkar. Rastgele skorda |t| < 2 çıkar.

## G6 · Hipotez kaydı, karar ve kontroller
`motor/hipotez.py`: `Hipotez` dataclass alanları: `kimlik, mekanizma, tur ("olay"|"kesit"), aciklama, parametreler: dict, ufuklar, ana_ufuk, bekleme, beklenen_isaret (+1/-1), basit_rakip: str|None`. `yukle(ad) -> list[Hipotez]` fonksiyonu `hipotezler/{ad}.yaml` dosyasını okur.

`motor/karar.py`:
- `karar_ver(sonuc: dict, h: Hipotez, n_deneme: int) -> {"karar": "tutarli|zayif|yok|ters", "gerekce": [..]}`. PLAN.md §3 tablosunu birebir uygular. Gerekçe satırları Türkçe ve sade olur (sayfada gösterilecek).
- `gunluge_yaz(h, sonuc_ozeti)`: `deneme_gunlugu.csv` dosyasına `zaman, kimlik, parametre_hash, ana_ufuk, dogrulama_ortalama, karar` ekler. `n_deneme(kimlik_onek)` toplamı sayar.

`motor/kontrol.py`:
- `negatif_kontrol(adj, n=200, oran=0.02)`: Rastgele tarih sinyalleri üretir, `olay_testi` sonuçlarında "tutarlı" çıkma oranını hesaplar.
- `pozitif_kontrol(adj_genis)`: 12-1 momentum kesit testi (skor = `adj.shift(21)/adj.shift(252)-1`, bu geçmişe bakar, geleceğe değil). Q5−Q1 63 günlük farkı raporlanır.
- Çıktı: `sonuclar/kontroller.json`.

`calistir.py test kontrol` bu ikisini çalıştırır.

Kabul: Testler yeşil. Sentetik veride negatif kontrolün yanlış alarm oranı ≤ %10.

---

# FAZ 1 — Çekirdek mekanizmalar

## G7 · Ortak özellikler
`ozellik/fiyat.py` (hepsi Series veya geniş DataFrame alır, sadece geçmişi kullanır):
`dusus(adj, pencere=252)`, `getiri(adj, n)`, `gerceklesen_vol(adj, n)` (yıllık), `zskor(x, n=252)`, `ust_ort(adj, n)` (adj > SMA_n), `atr_oran(df, n=14)`, `yuzdelik_kendi(x, n=252)` (kendi geçmişindeki yüzdelik), `zirveye_yakinlik(adj, 252)`, `beta(adj_hisse, adj_endeks, n=252)`, `kalinti_getiri(...)`.

`ozellik/genislik.py`:
- `ust_oran(adj_genis, n)`: SMA_n üstündeki hisse oranı. Sadece o gün verisi olan hisseler sayılır.
- `yeni_dip_oran(adj_genis, n=20)`
- `sektor_ust_oran(etf_adj, n=200)`: 11 ETF'den kaçının SMA_n üstünde olduğu. Hiç ETF yoksa NaN.
- `itki(oran, alt=0.15, ust=0.50, pencere=10)`: Son 10 gün içinde alt değerin altından üst değerin üstüne çıkış.

`ozellik/makro.py`: `kredi_degisim(baa10y, 60)`, `sahm_tetik(seri, 0.5)`, `egri(t10y3m)`. Yayın gecikmesi için haftalık seriler 7 gün ileri doldurulur, günlükler 3 gün.

`ozellik/rejim.py`:
- `kural_rejim(adj_endeks, vol_n=63, vol_esik=0.70, min_sure=10) -> Series` (4 değer: `sakin_yukselis`, `oynak_yukselis`, `sakin_dusus`, `oynak_dusus`). Vol yüzdeliği **genişleyen** pencereyle hesaplanır (geleceği görmemek için). Histerezis: yeni rejim min_sure gün sürmedikçe eski rejim korunur. Bu, gecikme yaratır ve gecikmenin kendisi geçmişe bakar.

Sızıntı testi şart: Rastgele bir t seçilir. t+1 sonrası veri çöp değerle değiştirildiğinde her fonksiyonun t'deki değeri aynı kalmalı. Bunu `testler/test_sizinti.py` içinde parametrik olarak bütün fonksiyonlara uygula.

## G8 · 🌀 Yay (endeks)
`hipotezler/yay.yaml` dosyasına Y1–Y4'ü yaz. Parametreler: `dd_esik: -0.10`, `vix_z_esik: 2.0`, `genislik_esik: 0.25`, `bilesik_yuzdelik: 0.95`, `vix_dusus: 0.20`, `ufuklar: [21,63,126,252]`, `ana_ufuk: 63`, `bekleme: 63`. Basit rakip: `dd <= -0.15`.

`mekanizmalar/yay.py` → `class Yay(Mekanizma)`, endeks parametreli (`^GSPC` varsayılan, `^NDX` ikincil):
- `ozellikler`: `dd`, `hiz` (20g getiri), `vix_z` (VIX yoksa 20g gerçekleşen vol z-skoru), `vade` (VIX/VIX3M, 2006 öncesi NaN), `genislik` (1 − 200g üst oranı), `sektor_genislik`, `kredi60`, `sahm`, `vix_dusus`, `itki`, `fiyat_teyidi`, `ayrisma`.
- `gerilim_skoru`: `dd`, `vix_z`, `genislik` bileşenlerinin **genişleyen** yüzdeliklerinin ortalaması (0–1). Eksik bileşen atlanır, en az 2 bileşen gerekir.
- `tur`: Gerilim durumunda `kredi60 > +0.5 puan` veya `sahm == 1` ise `"bozulma"`, değilse `"panik"`.
- `sinyaller(h)`:
  - Y1 → `gerilim_skoru ≥ bilesik_yuzdelik`
  - Y2 → `Y1_durumu son 20 günde gerçekleşti VE (vix_dusus VEYA itki VEYA fiyat_teyidi)`
  - Y3 → Y1'in `tur` kırılımı
- Y4: `^GDAXI ^N225 ^FTSE XU100.IS` için aynı sınıf, VIX yerine gerçekleşen vol, genişlik yerine yok (sadece `dd` + `vol_z`). BIST için not: TL enflasyonu, bu yüzden XU100'ü **USD bazlı** da test et (`USDTRY=X` Yahoo'dan; listeye ekle).
- `durum`: bugünkü skor, bileşenler, tür, en yakın 10 tarihsel benzer (standartlaştırılmış `dd, vix_z, genislik, hiz` üzerinde öklid uzaklığı, her bölümden en fazla 1 tane) ve benzerlerin 63g sonucu.
- Isı haritası: `dd` kovaları `[0,-5,-10,-15,-20,-30,-40,-100]%` × `vix` kovaları `[0,15,20,25,30,40,100]`, ufuk 63.

`calistir.py test yay` → `sonuclar/yay.json` dosyasına Y1–Y4 sonuçları, kararlar, ısı haritası ve bölüm tablosu yazılır. Ayrıca insan okuyabilir bir `sonuclar/yay.md` (tablolar, Türkçe) üretilir.

Testler: Sentetik yay enjeksiyonu bulunur. Sızıntı testi. `tur` mantığı birim testi.

## G9 · 🧲 Mıknatıs + pozitif kontrol (motoru doğrulama)
`hipotezler/miknatis.yaml`: M1 (kesit, skor = `zirveye_yakinlik`, ufuklar 21/63/126, ana 126, beklenen +1, rakip = 12-1 momentum).
`mekanizmalar/miknatis.py`: Hisse evreni, karantina hariç, minimum 252 gün geçmiş.
`calistir.py test miknatis` → `sonuclar/miknatis.json` + `.md`.

**⛔ DUR (önemli)**: Gerçek veride (Actions) 12-1 momentum ve Mıknatıs pozitif işaretle çıkmıyorsa motorda hata vardır. Faz 1'in geri kalanına geçmeden Opus'a incelet.

## G10 · 🌀 Hisse yayı ⟷ 🛡️ Gizli güç
`hipotezler/gizli_guc.yaml`: G1, G2, G3. Parametreler: `endeks: "^GSPC"`, `dd_esik: -0.10`, `beta_pencere: 252`, `ufuklar: [21,63,126,252]`, `degerlendirme: "bosalma"` (Yay'ın Y2 işaretinin dönem içindeki ilk günü; işaret çıkmazsa dönemin `dd ≤ dd_esik` olduğu 40. işlem günü).
`mekanizmalar/hisse_yay.py`:
- `donemler(adj_endeks)`: `dd ≤ dd_esik` olan kesintisiz bölümler. Başlangıç = önceki 252g zirvenin tarihi. Değerlendirme günü yukarıdaki kurala göre bulunur. Gerçek dip kullanılmaz.
- Her dönem için hisse başına: `donem_getiri`, `beta` (dönem öncesi), `kalinti = donem_getiri − beta × endeks_donem_getiri`, `onceki_vol` (dönem öncesi 63g), `buyukluk` (varsa `sonuclar.json` mcap, yoksa NaN; sadece kırılım için, bugünkü değer, uyarılı).
- `olay_kesit_testi` ile kalıntıya göre 5 dilim → ileri göreli getiri.
- G3: dönem `tur` (Yay'dan) ile kırılım. Tablo: hangi türde Q1 (yay), hangisinde Q5 (gizli güç) kazanıyor.
- Ek: **Şok yayı** (`S1`). Tek gün kalıntı ≤ −%8 ve ≥ −%50 (bölünme filtresi) olan olaylar. Olay sonrası 5/21/63 günlük kalıntı getiri. Koşul kırılımları: hisse 200g üstünde mi, piyasa rejimi, `dd` endeks.
- Çıktı: `sonuclar/gizli_guc.json` + `.md`. Bölüm tablosunda her kriz için en iyi 5 ve en kötü 5 hisse örnek olarak yer alır.

## G11 · ⚡ Kırılma noktası
`hipotezler/kirilma.yaml`: K1. Hedef: sonraki 21 ve 63 günde `kural_rejim` değişimi. Ayrıca ikinci hedef: "düşüşten yükselişe geçiş".
`ozellik/korelasyon.py` (G13 ile ortak, burada yaz): `ort_ikili_korelasyon(adj_genis, n=63, en_buyuk=100)`. Hız için hisse sayısını sınırla, hesap haftalık yapılır, araya ileri doldurma. `kesitsel_dagilim(getiri_genis)`.
`mekanizmalar/kirilma.py`:
- Öncü özellikler: `genislik_ayrisma` (endeks 63g getirisi > 0 ve 200g üst oranı 63 günde > 10 puan düştü), `liderlik_devri` (sektör ETF'lerinin 63g getiri sıralamasının 63 gün önceki sıralamayla Spearman'ı), `momentum_cokusu` (12-1 Q5−Q1 son 21g getirisi), `ort_korelasyon` ve 21g değişimi, `vix_vol` (VIX'in 21g std'si), `kredi_egim`.
- Model: Her yıl başında genişleyen pencereyle `LogisticRegression(C=1.0, class_weight="balanced")` yeniden eğitilir, o yıl tahmin edilir (ileri yürüyen). Standartlaştırma da sadece eğitim verisiyle yapılır.
- Ölçümler: Doğrulama dönemi AUC, Brier, koşulsuz orana göre kaldıraç (üst %10 tahminde gerçekleşen oran / koşulsuz oran), katsayılar (yıl yıl, kararlılık), gerçek rejim dönüşlerine göre ilk alarm gecikmesi tablosu.
- Rejim serisi `sonuclar/rejim.json` dosyasına yazılır. Diğer mekanizmalar rejim kırılımı için bunu kullanır.

## G12 · Faz 1 raporu
`rapor/json_yaz.py`: Her mekanizma için tek tip özet: `{ad, seviye, son_calisma, hipotezler:[{kimlik, aciklama, karar, gerekce, ana_sonuc:{ort, ga, n, bolum_n}, kesif, dogrulama}], durum, uyarilar}` → `sonuclar/ozet.json`.
`rapor/html_yaz.py` + Jinja şablonları → repo kökünde `mekanizma/index.html` (mekanizma kartları, karar rozetleri) ve `mekanizma/<ad>.html` (hipotez tabloları, bölüm tablosu, ısı haritası HTML tablo/hücre renklendirmesi, analoglar).
- Stil: `<link rel="stylesheet" href="../analiz/stil.css">`, analiz sayfalarındaki `nav.radar` yapısı (bağlantılar: Klasik Radar, Analiz Radarı, Mekanizmalar). Tasarım Analiz Radarı'yla aynı dilde. Mobil öncelikli, grafik kütüphanesi yok (ısı haritası renkli tablo).
- Her sayfanın altında: "Bu sayfa araştırma çıktısıdır, yatırım tavsiyesi değildir." + hayatta kalan yanlılığı notu (hisse mekanizmaları).
- `calistir.py pano` bunu üretir.

**⛔ DUR — Faz 1 incelemesi (Opus)**: Kullanıcı Actions'ı çalıştırır. Opus `sonuclar/*.json` dosyalarını okuyup sızıntı ve tutarlılık kontrolü yapar, sonuçları yorumlar. Faz 2'nin sırası buna göre güncellenir.

---

# FAZ 2 — Genişleme (ayrıntılar Faz 1 sonrası Opus tarafından netleştirilecek)

- **G13 · 🔗 Kenetlenme**: `ort_ikili_korelasyon` ve `kesitsel_dagilim` olay testleri (KN1). KN2: Gizli güç ve Mıknatıs dilim farkının korelasyon üçte birlik dilimlerine göre kırılımı.
- **G14 · 🌊 Gelgit**: NFCI 13 haftalık değişim beşte birlik dilimleri → endeks ileri getiri (GL1). Yay×Gelgit etkileşimi (GL2): Y1 olaylarını NFCI değişim işaretine göre ikiye bölme.
- **G15 · 🧱 Baraj**: `atr_oran` yüzdeliği ≤ 0.10 ve 40g aralık genişliği evrende en alt %20 → sıkışma. Kırılım olayları (yukarı/aşağı). B1: |ileri getiri| karşılaştırması. B2: RS (hisse/sektör ETF 63g) üst yarı + zirveye yakınlık ≥ 0.90 koşulu. Başarısızlık oranı = 10 gün içinde aralığa dönüş.
- **G16 · 🏔️ Çığ**: Anormal gün tanımı (PLAN §2.7). Olay öncesi koşul kombinasyonlarına göre olay sonrası 63g kalıntı kayma. Koşul sayısı ≤ 4 (çoklu test sınırı).
- **G17 · Etkileşimler**: Yay×Gelgit, Gizli güç×Kenetlenme, her mekanizma×Kırılma rejimi. Tek tablo.

# FAZ 3 — Temel veri

- **G18 · EDGAR katmanı**: `company_tickers.json` → CIK. `companyfacts` → `Revenues|RevenueFromContractWithCustomerExcludingAssessedTax`, `GrossProfit`, `NetIncomeLoss`, `NetCashProvidedByUsedInOperatingActivities`, `PaymentsToAcquirePropertyPlantAndEquipment`, `EntityCommonStockSharesOutstanding`. Her değer `filed` tarihine göre indekslenir (+1 iş günü). Yıllık ve çeyreklik 10-Q/10-K ayrımı, TTM (son 4 çeyrek) hesabı. İstek arası ≥ 0,15 s, `SEC_UA` başlığı zorunlu.
- **G19 · 🪢 Gerilmiş lastik**: L-A ve L-B kesit testleri (2010+).
- **G20 · ⏱️ Sarkaç**: Sektör F/K ve ağırlık uç değerleri. Durum göstergesi ağırlıklı, istatistik "vaka çalışması".
- **G21 · 🁢 Domino**: D1 (sektör lideri anormal günü → takipçi kayması), D2 (haftalık sektör öncü-gecikmeli, ileri yürüyen).

# FAZ 4 — Canlı pano

- **G22 · Haftalık durum**: Her ✅/🟡 mekanizmanın `durum()` çıktısı panonun en üstünde "Şu an" kartlarında gösterilir (gerilim göstergesi, analoglar). Hisse mekanizmaları için güncel ilk 10 liste.
- **G23 · Mekanizma karnesi**: Her haftanın sinyalleri `sonuclar/canli_sinyaller.json` dosyasına kaydedilir. 4/13/26 hafta sonra gerçekleşen getiri ölçülür (v5.16 karnesine benzer).
- **G24 · Entegrasyon**: Kökteki `index.html` üst çubuğuna ve `analiz/` nav'ına "Mekanizmalar" bağlantısı eklenir. `sw.js` içinde `/mekanizma/` her zaman ağdan gelir (`/analiz/` kuralının aynısı), önbellek sürümü artırılır. Telegram'a isteğe bağlı haftalık özet: "Yay gerilimi: düşük · Rejim: sakin yükseliş · …".

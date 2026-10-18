# Geriye Bakış: Her Dönemin En Çok Kazandıran Hisseleri

- **Ne bu?** Sonradan bakınca, her 3 ayda ve her 6 ayda en çok yükselen hisseler. Model yok; bunlar o gün bilinemezdi. Amaç, avlamak istediğimiz hisselerin neye benzediğini ve tavan getiriyi görmek.
- **Evren:** Finans dışı ABD şirketleri; dönem başında fiyatı ≥ 1 $ ve günlük işlem hacmi ≥ 1 milyon $ olarak bilinen hisseler. Günlük fiyatı olmayan (seyrek kayıtlı) borsadan çıkmış hisseler dahil değil (yalnızca güvenilir veri).
- **Getiri:** Bölünme ve temettü dahil. Dönemde borsadan çıkanlarda son fiyat, iflasta −%100.
- **Veri kontrolü:** Her hissenin getirisi ham fiyat ve bölünme kayıtlarıyla yeniden hesaplandı; tutarsızlık 'Not' sütununda.
- **Sembol:** O dönemdeki sembol (SEC sembol geçmişi 2015'ten başlıyor; öncesinde güncel sembol). Şirket adı güncel addır.
- **Önemli sınır:** Günlük fiyatı olmayan, borsadan çıkmış hisseler hariç tutulduğu için özellikle ilk yıllarda evren küçük (2010'da ~1.150, 2026'da ~3.000 hisse). Bu listeler o yılların bütün kazananlarını değil, bugün güvenilir verisi olanları gösterir.
- **Düşük hacim:** Dönem başında günlük işlem 3 milyon $'ın altında; büyük para bu hisselere kolay giremez.
- **Tam liste** (dönem başına ilk 20): `geriye_bakis_3ay.csv`, `geriye_bakis_6ay.csv`.

## 3 aylık dönemler

### Özet: en iyi 3 / 5 / 10 hissenin ortalama getirisi

| Dönem | Hisse sayısı | S&P 500 | Evren medyanı | En iyi 3 | En iyi 5 | En iyi 10 |
|---|---|---|---|---|---|---|
| 2010-Q1 | 1,149 | +6% | +7% | +67% | +65% | +62% |
| 2010-Q2 | 1,184 | -13% | -11% | +66% | +56% | +43% |
| 2010-Q3 | 1,216 | +13% | +15% | +127% | +106% | +87% |
| 2010-Q4 | 1,177 | +12% | +13% | +98% | +92% | +83% |
| 2011-Q1 | 1,247 | +5% | +6% | +79% | +74% | +68% |
| 2011-Q2 | 1,271 | +1% | +0% | +79% | +66% | +55% |
| 2011-Q3 | 1,271 | -13% | -19% | +32% | +28% | +24% |
| 2011-Q4 | 1,263 | +11% | +11% | +116% | +107% | +94% |
| 2012-Q1 | 1,245 | +10% | +9% | +84% | +81% | +76% |
| 2012-Q2 | 1,289 | -3% | -3% | +57% | +55% | +51% |
| 2012-Q3 | 1,257 | +8% | +7% | +89% | +81% | +68% |
| 2012-Q4 | 1,262 | +1% | +5% | +70% | +66% | +58% |
| 2013-Q1 | 1,274 | +6% | +6% | +91% | +79% | +68% |
| 2013-Q2 | 1,318 | +6% | +6% | +201% | +172% | +136% |
| 2013-Q3 | 1,350 | +4% | +7% | +252% | +196% | +147% |
| 2013-Q4 | 1,389 | +9% | +7% | +108% | +99% | +89% |
| 2014-Q1 | 1,454 | +2% | +2% | +175% | +141% | +100% |
| 2014-Q2 | 1,531 | +7% | +5% | +85% | +76% | +65% |
| 2014-Q3 | 1,513 | -0% | -6% | +173% | +132% | +88% |
| 2014-Q4 | 1,483 | +5% | +6% | +101% | +94% | +82% |
| 2015-Q1 | 1,534 | +1% | +3% | +98% | +94% | +82% |
| 2015-Q2 | 1,541 | +1% | -2% | +109% | +94% | +76% |
| 2015-Q3 | 1,588 | -5% | -10% | +63% | +56% | +45% |
| 2015-Q4 | 1,585 | +5% | +2% | +131% | +112% | +89% |
| 2016-Q1 | 1,585 | +2% | +3% | +127% | +115% | +100% |
| 2016-Q2 | 1,581 | +2% | +3% | +141% | +128% | +113% |
| 2016-Q3 | 1,584 | +3% | +4% | +146% | +129% | +111% |
| 2016-Q4 | 1,618 | +6% | +6% | +89% | +83% | +73% |
| 2017-Q1 | 1,680 | +4% | +3% | +140% | +119% | +95% |
| 2017-Q2 | 1,696 | +3% | +4% | +135% | +119% | +100% |
| 2017-Q3 | 1,706 | +6% | +6% | +221% | +175% | +129% |
| 2017-Q4 | 1,718 | +8% | +6% | +235% | +202% | +151% |
| 2018-Q1 | 1,794 | -5% | -5% | +97% | +93% | +81% |
| 2018-Q2 | 1,829 | +7% | +7% | +302% | +258% | +196% |
| 2018-Q3 | 1,847 | +5% | -1% | +252% | +178% | +117% |
| 2018-Q4 | 1,853 | -12% | -13% | +68% | +61% | +54% |
| 2019-Q1 | 1,863 | +15% | +16% | +145% | +129% | +113% |
| 2019-Q2 | 1,862 | +4% | +1% | +95% | +92% | +81% |
| 2019-Q3 | 1,917 | -1% | -4% | +103% | +91% | +71% |
| 2019-Q4 | 1,912 | +10% | +10% | +367% | +278% | +200% |
| 2020-Q1 | 1,931 | -23% | -33% | +184% | +154% | +114% |
| 2020-Q2 | 2,014 | +26% | +34% | +758% | +650% | +503% |
| 2020-Q3 | 2,086 | +7% | +5% | +384% | +341% | +271% |
| 2020-Q4 | 2,166 | +12% | +21% | +480% | +454% | +385% |
| 2021-Q1 | 2,278 | +8% | +11% | +909% | +736% | +514% |
| 2021-Q2 | 2,705 | +9% | +2% | +349% | +277% | +205% |
| 2021-Q3 | 2,638 | +0% | -4% | +130% | +124% | +105% |
| 2021-Q4 | 2,603 | +8% | -3% | +211% | +156% | +110% |
| 2022-Q1 | 2,657 | -3% | -6% | +169% | +152% | +128% |
| 2022-Q2 | 2,570 | -15% | -18% | +94% | +81% | +66% |
| 2022-Q3 | 2,488 | -4% | -4% | +281% | +225% | +171% |
| 2022-Q4 | 2,370 | +7% | +9% | +238% | +221% | +187% |
| 2023-Q1 | 2,357 | +6% | +0% | +117% | +113% | +105% |
| 2023-Q2 | 2,388 | +8% | +4% | +245% | +213% | +184% |
| 2023-Q3 | 2,405 | -2% | -7% | +124% | +111% | +94% |
| 2023-Q4 | 2,393 | +9% | +9% | +442% | +346% | +252% |
| 2024-Q1 | 2,422 | +11% | +5% | +250% | +216% | +176% |
| 2024-Q2 | 2,525 | +7% | -4% | +302% | +253% | +198% |
| 2024-Q3 | 2,513 | +4% | +7% | +461% | +344% | +243% |
| 2024-Q4 | 2,556 | +4% | -1% | +649% | +573% | +427% |
| 2025-Q1 | 2,671 | -14% | -19% | +415% | +291% | +177% |
| 2025-Q2 | 2,672 | +24% | +21% | +449% | +409% | +347% |
| 2025-Q3 | 2,751 | +7% | +5% | +407% | +356% | +305% |
| 2025-Q4 | 2,918 | +2% | -2% | +337% | +311% | +250% |
| 2026-Q1 | 2,940 | -4% | -3% | +301% | +269% | +212% |
| 2026-Q2 | 3,013 | +14% | +7% | +564% | +469% | +361% |
| 2026-Q3 | 3,089 | +4% | -6% | +303% | +260% | +201% |

Bileşik yıllık (her dönem yalnızca o grubu alıp tutmuş olsaydık; tavan, ulaşılamaz): S&P +14%, en iyi 3 +6,551%, en iyi 10 +2,720%.

### 2010

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2010-Q1 | 1 | LYV | Live Nation Entertainment, Inc. | Tüketici | 8.51 $ | 4.0 | +69% |  |
| 2010-Q1 | 2 | NKTR | Nektar Therapeutics | Sağlık | 9.32 $ | 5.5 | +67% |  |
| 2010-Q1 | 3 | DPZ | Domino's Pizza Inc | Tüketici | 8.38 $ | 3.0 | +64% |  |
| 2010-Q1 | 4 | ZUMZ | Zumiez Inc. | Perakende | 12.72 $ | 3.7 | +63% |  |
| 2010-Q1 | 5 | CAL | Caleres, Inc. | Diğer | 9.87 $ | 2.8 | +62% | düşük hacim |
| 2010-Q2 | 1 | CRUS | Cirrus Logic, Inc. | Yarı iletken | 8.45 $ | 5.0 | +84% |  |
| 2010-Q2 | 2 | MUX | McEwen Inc. | Madencilik | 2.71 $ | 1.7 | +64% | düşük hacim |
| 2010-Q2 | 3 | OLED | Universal Display Corporation | Teknoloji donanım | 11.86 $ | 1.9 | +51% | düşük hacim |
| 2010-Q2 | 4 | NFLX | Netflix, Inc. | Tüketici | 75.00 $ | 83.5 | +43% |  |
| 2010-Q2 | 5 | EGO | Eldorado Gold Corporation | Madencilik | 12.51 $ | 53.4 | +35% |  |
| 2010-Q3 | 1 | VHC | VirnetX Holding Corp | Diğer | 5.97 $ | 1.5 | +152% | düşük hacim |
| 2010-Q3 | 2 | MSB | Mesabi Trust | Diğer | 16.61 $ | 1.9 | +137% | düşük hacim |
| 2010-Q3 | 3 | BKNG | Booking Holdings Inc. | Sanayi | 176.41 $ | 266.6 | +92% |  |
| 2010-Q3 | 4 | URI | United Rentals, Inc. | Diğer | 8.53 $ | 20.6 | +75% |  |
| 2010-Q3 | 5 | RDWR | Radware Ltd. | Diğer | 19.89 $ | 2.5 | +75% | düşük hacim |
| 2010-Q4 | 1 | QMCO | Quantum Corporation | Sanayi | 2.09 $ | 2.8 | +106% | düşük hacim |
| 2010-Q4 | 2 | EXEL | Exelixis, Inc. | Biyoteknoloji | 3.97 $ | 2.9 | +102% | düşük hacim |
| 2010-Q4 | 3 | NXPI | NXP Semiconductors N.V. | Yarı iletken | 12.36 $ | 4.6 | +85% |  |
| 2010-Q4 | 4 | AGIG | Abundia Global Impact Group Inc. Commo | Enerji | 10.40 $ | 1.6 | +83% | düşük hacim |
| 2010-Q4 | 5 | CVI | CVR Energy Inc. | Enerji | 8.19 $ | 1.5 | +82% | düşük hacim |

### 2011

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2011-Q1 | 1 | DDD | 3D Systems Corporation | Yazılım | 29.57 $ | 2.3 | +86% | düşük hacim |
| 2011-Q1 | 2 | IPGP | IPG Photonics Corporation | Yarı iletken | 30.11 $ | 5.4 | +83% |  |
| 2011-Q1 | 3 | MERC | Mercer International Inc. | Hammadde | 8.11 $ | 1.6 | +68% | düşük hacim |
| 2011-Q1 | 4 | FTK | Flotek Industries, Inc. | Hammadde | 5.14 $ | 4.2 | +68% |  |
| 2011-Q1 | 5 | GLNG | Golar LNG Limited | Sanayi | 15.92 $ | 2.4 | +67% | düşük hacim |
| 2011-Q2 | 1 | AMRN | Amarin Corporation plc | Sağlık | 7.43 $ | 13.6 | +99% |  |
| 2011-Q2 | 2 | MLCO | Melco Resorts & Entertainment Limited | Tüketici | 8.01 $ | 40.1 | +70% |  |
| 2011-Q2 | 3 | EGHT | 8x8 Inc | Yazılım | 2.91 $ | 1.1 | +67% | düşük hacim |
| 2011-Q2 | 4 | BIIB | Biogen Inc. | Biyoteknoloji | 72.96 $ | 115.2 | +49% |  |
| 2011-Q2 | 5 | ANIP | ANI Pharmaceuticals, Inc. | Sağlık | 1.99 $ | 2.6 | +46% | düşük hacim |
| 2011-Q3 | 1 | LQDT | Liquidity Services, Inc. | Diğer | 23.18 $ | 2.9 | +36% | düşük hacim |
| 2011-Q3 | 2 | PSMT | PriceSmart, Inc. | Perakende | 52.51 $ | 6.4 | +35% |  |
| 2011-Q3 | 3 | OLED | Universal Display Corporation | Teknoloji donanım | 35.32 $ | 41.8 | +25% |  |
| 2011-Q3 | 4 | RGR | Sturm, Ruger & Company, Inc. | Diğer | 8.28 $ | 2.5 | +23% | düşük hacim |
| 2011-Q3 | 5 | SIMO | Silicon Motion Technology Corporation | Yarı iletken | 10.88 $ | 4.6 | +22% |  |
| 2011-Q4 | 1 | FTK | Flotek Industries, Inc. | Hammadde | 4.98 $ | 7.7 | +142% |  |
| 2011-Q4 | 2 | MIND | MIND Technology, Inc. | Savunma/havacılık | 1.09 $ | 2.0 | +111% | düşük hacim |
| 2011-Q4 | 3 | LNG | Cheniere Energy, Inc. | Enerji | 4.60 $ | 19.8 | +96% |  |
| 2011-Q4 | 4 | BZH | Beazer Homes USA, Inc. | İnşaat | 1.47 $ | 4.3 | +95% |  |
| 2011-Q4 | 5 | CX | Cemex, S.A.B. de C.V. Sponsored ADR | Diğer | 2.82 $ | 73.0 | +93% |  |

### 2012

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2012-Q1 | 1 | REGN | Regeneron Pharmaceuticals, Inc. | Sağlık | 65.79 $ | 52.5 | +88% |  |
| 2012-Q1 | 2 | CPRI | Capri Holdings Limited | Diğer | 26.00 $ | 26.5 | +83% |  |
| 2012-Q1 | 3 | LNG | Cheniere Energy, Inc. | Enerji | 9.00 $ | 33.4 | +82% |  |
| 2012-Q1 | 4 | SWBI | Smith & Wesson Brands, Inc. | Diğer | 4.68 $ | 1.4 | +77% | düşük hacim |
| 2012-Q1 | 5 | TRX | TRX Gold Corporation | Madencilik | 2.71 $ | 1.4 | +76% | düşük hacim |
| 2012-Q2 | 1 | MDGL | Madrigal Pharmaceuticals, Inc. | Sağlık | 4.06 $ | 1.2 | +61% | düşük hacim |
| 2012-Q2 | 2 | LXRX | Lexicon Pharmaceuticals, Inc. | Sağlık | 1.77 $ | 1.1 | +55% | düşük hacim |
| 2012-Q2 | 3 | IONS | Ionis Pharmaceuticals, Inc. | Sağlık | 8.55 $ | 3.8 | +54% |  |
| 2012-Q2 | 4 | VHC | VirnetX Holding Corp | Diğer | 23.84 $ | 16.1 | +53% |  |
| 2012-Q2 | 5 | CAL | Caleres, Inc. | Diğer | 8.99 $ | 3.5 | +52% |  |
| 2012-Q3 | 1 | TMUS | T-Mobile US, Inc. | İletişim/medya | 6.41 $ | 36.2 | +97% |  |
| 2012-Q3 | 2 | ONIT | Onity Group Inc. | Finansal hizmet | 19.32 $ | 18.2 | +90% |  |
| 2012-Q3 | 3 | AFFY | AFFYMAX INC | Sağlık | 12.68 $ | 10.8 | +80% |  |
| 2012-Q3 | 4 | GEOY | GeoEye, Inc. | İletişim/medya | 16.04 $ | 4.1 | +70% |  |
| 2012-Q3 | 5 | CDE | Coeur Mining, Inc. | Madencilik | 16.94 $ | 26.3 | +69% |  |
| 2012-Q4 | 1 | HOV | Hovnanian Enterprises, Inc. | İnşaat | 3.85 $ | 11.2 | +79% |  |
| 2012-Q4 | 2 | FSLR | First Solar, Inc. | Yarı iletken | 20.07 $ | 136.5 | +67% |  |
| 2012-Q4 | 3 | DDD | 3D Systems Corporation | Yazılım | 35.89 $ | 51.1 | +64% |  |
| 2012-Q4 | 4 | PPC | Pilgrim's Pride Corporation | Temel tüketim | 4.99 $ | 3.4 | +63% |  |
| 2012-Q4 | 5 | NOK | Nokia Corporation Sponsored | Teknoloji donanım | 2.68 $ | 112.7 | +56% |  |

### 2013

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2013-Q1 | 1 | BBY | Best Buy Co., Inc. | Perakende | 12.11 $ | 77.8 | +112% |  |
| 2013-Q1 | 2 | VIPS | Vipshop Holdings Limited | Perakende | 16.60 $ | 1.3 | +90% | düşük hacim |
| 2013-Q1 | 3 | NFLX | Netflix, Inc. | Tüketici | 95.98 $ | 291.7 | +72% |  |
| 2013-Q1 | 4 | ANGI | Angie's List, Inc. | Diğer | 11.50 $ | 3.5 | +63% |  |
| 2013-Q1 | 5 | IONS | Ionis Pharmaceuticals, Inc. | Sağlık | 10.89 $ | 12.5 | +59% |  |
| 2013-Q2 | 1 | CSIQ | Canadian Solar Inc. | Yarı iletken | 3.47 $ | 2.4 | +247% | düşük hacim |
| 2013-Q2 | 2 | TSLA | Tesla, Inc. | Sanayi | 41.37 $ | 53.9 | +190% |  |
| 2013-Q2 | 3 | JKS | JinkoSolar Holding Company Limited | Yarı iletken | 4.15 $ | 2.1 | +165% | düşük hacim |
| 2013-Q2 | 4 | ACAD | ACADIA Pharmaceuticals Inc. | Sağlık | 7.70 $ | 8.7 | +134% |  |
| 2013-Q2 | 5 | RH | RH | Perakende | 33.78 $ | 2.8 | +121% | düşük hacim |
| 2013-Q3 | 1 | BCRX | BioCryst Pharmaceuticals, Inc. | Biyoteknoloji | 1.62 $ | 1.4 | +354% | düşük hacim |
| 2013-Q3 | 2 | RMTI | Rockwell Medical, Inc. | Sağlık | 3.42 $ | 1.6 | +264% | düşük hacim |
| 2013-Q3 | 3 | VIPS | Vipshop Holdings Limited | Perakende | 28.37 $ | 13.1 | +139% |  |
| 2013-Q3 | 4 | JKS | JinkoSolar Holding Company Limited | Yarı iletken | 11.00 $ | 3.7 | +113% |  |
| 2013-Q3 | 5 | META | Meta Platforms, Inc. | Yazılım | 24.37 $ | 823.0 | +109% |  |
| 2013-Q4 | 1 | SLS | SELLAS Life Sciences Group, Inc. | Sağlık | 2.29 $ | 3.8 | +122% |  |
| 2013-Q4 | 2 | PRDO | Perdoceo Education Corporation | Diğer | 2.68 $ | 1.8 | +106% | düşük hacim |
| 2013-Q4 | 3 | VIVS | VivoSim Labs, Inc. | Biyoteknoloji | 5.55 $ | 14.5 | +96% |  |
| 2013-Q4 | 4 | GTN | Gray Media, Inc. | İletişim/medya | 7.84 $ | 4.2 | +86% |  |
| 2013-Q4 | 5 | PBYI | Puma Biotechnology Inc | Sağlık | 56.29 $ | 6.6 | +85% |  |

### 2014

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2014-Q1 | 1 | ALTO | Alto Ingredients, Inc. | Hammadde | 5.08 $ | 1.2 | +194% | düşük hacim |
| 2014-Q1 | 2 | PLUG | Plug Power, Inc. | Teknoloji donanım | 2.61 $ | 1.8 | +173% | düşük hacim |
| 2014-Q1 | 3 | ABUS | Arbutus Biopharma Corporation | Sağlık | 7.80 $ | 1.1 | +158% | düşük hacim |
| 2014-Q1 | 4 | MYGN | Myriad Genetics, Inc. | Sağlık | 21.20 $ | 49.8 | +93% |  |
| 2014-Q1 | 5 | SBSW | D/B/A Sibanye-Stillwater Limited ADS | Madencilik | 4.98 $ | 3.4 | +89% |  |
| 2014-Q2 | 1 | LEU | Centrus Energy Corp. | Diğer | 3.71 $ | 1.1 | +98% | düşük hacim |
| 2014-Q2 | 2 | RGEN | Repligen Corporation | Biyoteknoloji | 13.26 $ | 7.0 | +79% |  |
| 2014-Q2 | 3 | TGTX | TG Therapeutics, Inc. | Sağlık | 6.18 $ | 1.5 | +79% | düşük hacim |
| 2014-Q2 | 4 | GERN | Geron Corporation | Sağlık | 1.94 $ | 16.2 | +64% |  |
| 2014-Q2 | 5 | GSAT | Globalstar, Inc. | İletişim/medya | 2.80 $ | 4.2 | +59% |  |
| 2014-Q3 | 1 | PBYI | Puma Biotechnology Inc | Sağlık | 70.00 $ | 25.1 | +257% |  |
| 2014-Q3 | 2 | ABUS | Arbutus Biopharma Corporation | Sağlık | 11.63 $ | 4.7 | +154% |  |
| 2014-Q3 | 3 | GPRO | GoPro, Inc. | Teknoloji donanım | 41.58 $ | 1,334.7 | +109% |  |
| 2014-Q3 | 4 | OSPN | OneSpan Inc. | Yazılım | 11.89 $ | 2.1 | +70% | düşük hacim |
| 2014-Q3 | 5 | PTCT | PTC Therapeutics, Inc. | Sağlık | 27.26 $ | 5.4 | +68% |  |
| 2014-Q4 | 1 | CYTK | Cytokinetics, Incorporated | Sağlık | 3.61 $ | 1.7 | +104% | düşük hacim |
| 2014-Q4 | 2 | ANIP | ANI Pharmaceuticals, Inc. | Sağlık | 27.93 $ | 4.3 | +104% |  |
| 2014-Q4 | 3 | TCRT | Alaunos Therapeutics, Inc. | Sağlık | 2.64 $ | 1.6 | +94% | düşük hacim |
| 2014-Q4 | 4 | OMER | Omeros Corporation | Sağlık | 13.03 $ | 3.4 | +92% |  |
| 2014-Q4 | 5 | FRO | Frontline Plc | Sanayi | 1.41 $ | 1.5 | +78% | düşük hacim |

### 2015

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2015-Q1 | 1 | AMRN | Amarin Corporation plc | Sağlık | 1.13 $ | 1.3 | +109% | düşük hacim |
| 2015-Q1 | 2 | ZIOP | Alaunos Therapeutics, Inc. | Sağlık | 5.13 $ | 3.0 | +94% |  |
| 2015-Q1 | 3 | PAM | Pampa Energia S.A. | Kamu hizmetleri | 9.52 $ | 1.1 | +91% | düşük hacim |
| 2015-Q1 | 4 | TVTX | Travere Therapeutics, Inc. | Sağlık | 12.67 $ | 3.3 | +88% |  |
| 2015-Q1 | 5 | PRTA | Prothena Corporation plc | Sağlık | 20.35 $ | 4.7 | +88% |  |
| 2015-Q2 | 1 | HRTX | Heron Therapeutics, Inc. | Sağlık | 14.07 $ | 1.7 | +115% | düşük hacim |
| 2015-Q2 | 2 | SRPT | Sarepta Therapeutics, Inc. | Sağlık | 14.25 $ | 8.8 | +112% |  |
| 2015-Q2 | 3 | ASPS | Altisource Portfolio Solutions S.A. | Diğer | 15.00 $ | 10.3 | +100% |  |
| 2015-Q2 | 4 | DMRC | Digimarc Corporation | Yazılım | 22.22 $ | 1.0 | +79% | düşük hacim |
| 2015-Q2 | 5 | RARE | Ultragenyx Pharmaceutical Inc. | Sağlık | 62.20 $ | 14.8 | +65% |  |
| 2015-Q3 | 1 | EXEL | Exelixis, Inc. | Biyoteknoloji | 3.44 $ | 8.5 | +72% |  |
| 2015-Q3 | 2 | TRVN | TREVENA INC | Sağlık | 6.01 $ | 1.3 | +71% | düşük hacim |
| 2015-Q3 | 3 | LPCN | Lipocine Inc. | Sağlık | 8.83 $ | 1.1 | +47% | düşük hacim |
| 2015-Q3 | 4 | LXRX | Lexicon Pharmaceuticals, Inc. | Sağlık | 8.16 $ | 2.2 | +45% | düşük hacim |
| 2015-Q3 | 5 | CENT | Central Garden & Pet Company | Tüketici | 11.34 $ | 1.2 | +44% | düşük hacim |
| 2015-Q4 | 1 | VTL | Immunic, Inc. | Sağlık | 4.00 $ | 3.5 | +188% |  |
| 2015-Q4 | 2 | PACB | Pacific Biosciences of California, Inc | Teknoloji donanım | 6.13 $ | 2.1 | +114% | düşük hacim |
| 2015-Q4 | 3 | KNDI | Kandi Technologies Group, Inc. | Sanayi | 5.73 $ | 2.7 | +90% | düşük hacim |
| 2015-Q4 | 4 | PCRX | Pacira BioSciences, Inc. | Sağlık | 40.74 $ | 44.4 | +88% |  |
| 2015-Q4 | 5 | ANGI | Angie's List, Inc. | Diğer | 5.25 $ | 3.7 | +78% |  |

### 2016

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2016-Q1 | 1 | SBSW | D/B/A Sibanye-Stillwater Limited ADS | Madencilik | 6.09 $ | 6.9 | +153% |  |
| 2016-Q1 | 2 | CDE | Coeur Mining, Inc. | Madencilik | 2.48 $ | 5.3 | +127% |  |
| 2016-Q1 | 3 | TECK | Teck Resources Ltd | Diğer | 3.86 $ | 39.7 | +102% |  |
| 2016-Q1 | 4 | AG | First Majestic Silver Corp. | Madencilik | 3.27 $ | 5.2 | +99% |  |
| 2016-Q1 | 5 | AU | AngloGold Ashanti PLC | Madencilik | 7.10 $ | 24.6 | +94% |  |
| 2016-Q2 | 1 | EZPW | EZCORP, Inc. | Perakende | 2.98 $ | 1.4 | +155% | düşük hacim |
| 2016-Q2 | 2 | SSRM | SSR Mining Inc. | Diğer | 5.64 $ | 8.4 | +141% |  |
| 2016-Q2 | 3 | AG | First Majestic Silver Corp. | Madencilik | 6.51 $ | 10.3 | +127% |  |
| 2016-Q2 | 4 | MUX | McEwen Inc. | Madencilik | 1.94 $ | 2.8 | +112% | düşük hacim |
| 2016-Q2 | 5 | ETE | Energy Transfer LP | Enerji | 6.88 $ | 180.5 | +105% |  |
| 2016-Q3 | 1 | SRPT | Sarepta Therapeutics, Inc. | Sağlık | 20.25 $ | 72.3 | +186% |  |
| 2016-Q3 | 2 | MOMO | Hello Group Inc. | Yazılım | 9.95 $ | 11.1 | +137% |  |
| 2016-Q3 | 3 | OCN | Onity Group Inc. | Finansal hizmet | 1.74 $ | 3.9 | +115% |  |
| 2016-Q3 | 4 | RGNX | REGENXBIO Inc. | Biyoteknoloji | 7.99 $ | 1.2 | +103% | düşük hacim |
| 2016-Q3 | 5 | AAOI | Applied Optoelectronics, Inc. | Yarı iletken | 11.22 $ | 4.2 | +102% |  |
| 2016-Q4 | 1 | WTI | W&T Offshore, Inc. | Enerji | 1.61 $ | 1.5 | +98% | düşük hacim |
| 2016-Q4 | 2 | IPI | Intrepid Potash, Inc | Diğer | 1.09 $ | 1.0 | +94% | düşük hacim |
| 2016-Q4 | 3 | STRA | Strategic Education, Inc. | Diğer | 46.25 $ | 3.2 | +77% |  |
| 2016-Q4 | 4 | KRO | Kronos Worldwide Inc | Hammadde | 7.69 $ | 2.5 | +74% | düşük hacim |
| 2016-Q4 | 5 | CVI | CVR Energy Inc. | Enerji | 13.95 $ | 12.7 | +72% |  |

### 2017

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2017-Q1 | 1 | AUPH | Aurinia Pharmaceuticals Inc | Sağlık | 2.36 $ | 2.9 | +199% | düşük hacim |
| 2017-Q1 | 2 | TGTX | TG Therapeutics, Inc. | Sağlık | 4.95 $ | 2.7 | +113% | düşük hacim |
| 2017-Q1 | 3 | SBLK | Star Bulk Carriers Corp. | Sanayi | 6.11 $ | 1.4 | +108% | düşük hacim |
| 2017-Q1 | 4 | AAOI | Applied Optoelectronics, Inc. | Yarı iletken | 22.42 $ | 7.1 | +99% |  |
| 2017-Q1 | 5 | CARA | Tvardi Therapeutics, Inc. | Sağlık | 10.28 $ | 9.5 | +77% |  |
| 2017-Q2 | 1 | PBYI | Puma Biotechnology Inc | Sağlık | 35.65 $ | 27.4 | +144% |  |
| 2017-Q2 | 2 | NK | ImmunityBio, Inc. | Biyoteknoloji | 3.12 $ | 1.2 | +131% | düşük hacim |
| 2017-Q2 | 3 | ANGI | Angie's List, Inc. | Diğer | 5.59 $ | 2.4 | +128% | düşük hacim |
| 2017-Q2 | 4 | PTCT | PTC Therapeutics, Inc. | Sağlık | 9.84 $ | 9.7 | +96% |  |
| 2017-Q2 | 5 | PETS | PetMed Express, Inc. | Perakende | 21.34 $ | 3.8 | +95% |  |
| 2017-Q3 | 1 | MNKD | MannKind Corporation | Sağlık | 1.17 $ | 2.8 | +330% | düşük hacim |
| 2017-Q3 | 2 | VERI | Veritone, Inc. | Yazılım | 11.54 $ | 1.1 | +221% | düşük hacim |
| 2017-Q3 | 3 | ABEO | Abeona Therapeutics Inc. | Sağlık | 8.35 $ | 1.0 | +112% | düşük hacim |
| 2017-Q3 | 4 | NC | NACCO Industries, Inc. | Diğer | 70.10 $ | 1.1 | +107% | düşük hacim |
| 2017-Q3 | 5 | SGH | Penguin Solutions, Inc. | Yarı iletken | 15.99 $ | 1.3 | +105% | düşük hacim |
| 2017-Q4 | 1 | ACB | Aurora Cannabis Inc. | Sağlık | 2.33 $ | 1.1 | +338% | düşük hacim |
| 2017-Q4 | 2 | ANAB | AnaptysBio, Inc. | Sağlık | 35.68 $ | 4.8 | +184% |  |
| 2017-Q4 | 3 | OSTK | Neighborhood Intelligence, Inc. | Perakende | 30.00 $ | 6.7 | +181% |  |
| 2017-Q4 | 4 | CGC | Canopy Growth Corporation | Sağlık | 9.97 $ | 1.3 | +175% | düşük hacim |
| 2017-Q4 | 5 | NKTR | Nektar Therapeutics | Sağlık | 24.81 $ | 22.7 | +133% |  |

### 2018

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2018-Q1 | 1 | SSTI | SoundThinking, Inc. | Yazılım | 15.53 $ | 1.3 | +105% | düşük hacim |
| 2018-Q1 | 2 | VIRT | Virtu Financial, Inc. | Finansal hizmet | 18.65 $ | 8.3 | +93% |  |
| 2018-Q1 | 3 | VCEL | Vericel Corporation | Biyoteknoloji | 5.85 $ | 2.0 | +91% | düşük hacim |
| 2018-Q1 | 4 | ATRA | Atara Biotherapeutics, Inc. | Biyoteknoloji | 18.50 $ | 2.4 | +90% | düşük hacim |
| 2018-Q1 | 5 | GERN | Geron Corporation | Sağlık | 1.87 $ | 2.4 | +86% | düşük hacim |
| 2018-Q2 | 1 | SLDB | Solid Biosciences Inc. | Biyoteknoloji | 9.54 $ | 4.0 | +343% |  |
| 2018-Q2 | 2 | TNDM | Tandem Diabetes Care, Inc. | Sağlık | 5.75 $ | 3.5 | +301% |  |
| 2018-Q2 | 3 | EOLS | Evolus, Inc. | Sağlık | 7.58 $ | 1.0 | +261% | düşük hacim |
| 2018-Q2 | 4 | MDGL | Madrigal Pharmaceuticals, Inc. | Sağlık | 101.55 $ | 24.5 | +195% |  |
| 2018-Q2 | 5 | RGNX | REGENXBIO Inc. | Biyoteknoloji | 27.20 $ | 7.6 | +192% |  |
| 2018-Q3 | 1 | AMRN | Amarin Corporation plc | Sağlık | 2.98 $ | 5.1 | +564% |  |
| 2018-Q3 | 2 | TRVN | TREVENA INC | Sağlık | 1.49 $ | 1.5 | +109% | düşük hacim |
| 2018-Q3 | 3 | CDNA | CareDx, Inc. | Sağlık | 13.03 $ | 5.0 | +82% |  |
| 2018-Q3 | 4 | MDXG | MiMedx Group, Inc | Sağlık | 3.35 $ | 13.1 | +69% |  |
| 2018-Q3 | 5 | AMD | Advanced Micro Devices, Inc. | Yarı iletken | 16.36 $ | 630.9 | +67% |  |
| 2018-Q4 | 1 | CIG | Comp En De Mn Cemig ADS | Kamu hizmetleri | 2.18 $ | 5.6 | +72% |  |
| 2018-Q4 | 2 | PACB | Pacific Biosciences of California, Inc | Teknoloji donanım | 4.38 $ | 4.1 | +66% |  |
| 2018-Q4 | 3 | MITK | Mitek Systems, Inc. | Sanayi | 6.58 $ | 1.5 | +65% | düşük hacim |
| 2018-Q4 | 4 | VCYT | Veracyte, Inc. | Sağlık | 9.31 $ | 2.7 | +53% | düşük hacim |
| 2018-Q4 | 5 | AU | AngloGold Ashanti PLC | Madencilik | 8.49 $ | 21.7 | +51% |  |

### 2019

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2019-Q1 | 1 | FTK | Flotek Industries, Inc. | Hammadde | 1.13 $ | 1.1 | +194% | düşük hacim |
| 2019-Q1 | 2 | QURE | uniQure N.V. | Sağlık | 28.14 $ | 8.2 | +121% |  |
| 2019-Q1 | 3 | VYGR | Voyager Therapeutics, Inc. | Biyoteknoloji | 9.47 $ | 3.4 | +120% |  |
| 2019-Q1 | 4 | DOMO | Huckleberry.ai, Inc. | Yazılım | 18.46 $ | 5.5 | +105% |  |
| 2019-Q1 | 5 | INSM | Insmed Incorporated | Sağlık | 14.85 $ | 13.3 | +104% |  |
| 2019-Q2 | 1 | ENPH | Enphase Energy, Inc. | Yarı iletken | 9.84 $ | 14.5 | +100% |  |
| 2019-Q2 | 2 | IOVA | Iovance Biotherapeutics, Inc. | Biyoteknoloji | 12.64 $ | 7.7 | +94% |  |
| 2019-Q2 | 3 | PAYS | Paysign, Inc. | Diğer | 7.50 $ | 1.3 | +93% | düşük hacim |
| 2019-Q2 | 4 | AXSM | Axsome Therapeutics, Inc. | Sağlık | 14.50 $ | 10.2 | +86% |  |
| 2019-Q2 | 5 | PI | Impinj, Inc. | Teknoloji donanım | 18.09 $ | 2.5 | +85% | düşük hacim |
| 2019-Q3 | 1 | HOV | Hovnanian Enterprises, Inc. | İnşaat | 8.18 $ | 1.5 | +130% | düşük hacim |
| 2019-Q3 | 2 | SLDB | Solid Biosciences Inc. | Biyoteknoloji | 5.19 $ | 2.1 | +93% | düşük hacim |
| 2019-Q3 | 3 | NXTC | NextCure, Inc. | Sağlık | 16.63 $ | 1.1 | +86% | düşük hacim |
| 2019-Q3 | 4 | OMI | Accendra Health, Inc. | Tüketici | 3.30 $ | 3.9 | +82% |  |
| 2019-Q3 | 5 | BXC | Bluelinx Holdings Inc. | Tüketici | 19.15 $ | 3.1 | +65% |  |
| 2019-Q4 | 1 | AXSM | Axsome Therapeutics, Inc. | Sağlık | 18.46 $ | 17.8 | +413% |  |
| 2019-Q4 | 2 | KOD | Kodiak Sciences Inc | Biyoteknoloji | 13.90 $ | 1.5 | +387% | düşük hacim |
| 2019-Q4 | 3 | AUPH | Aurinia Pharmaceuticals Inc | Sağlık | 5.14 $ | 2.5 | +301% | düşük hacim |
| 2019-Q4 | 4 | BE | Bloom Energy Corporation | Teknoloji donanım | 3.21 $ | 11.0 | +150% |  |
| 2019-Q4 | 5 | SCOR | comScore, Inc. | Diğer | 2.05 $ | 1.9 | +139% | düşük hacim |

### 2020

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2020-Q1 | 1 | NVAX | Novavax, Inc. | Biyoteknoloji | 4.44 $ | 2.9 | +252% | düşük hacim |
| 2020-Q1 | 2 | INO | Inovio Pharmaceuticals, Inc. | Sağlık | 2.98 $ | 1.8 | +160% | düşük hacim |
| 2020-Q1 | 3 | VIR | Vir Biotechnology, Inc. | Biyoteknoloji | 12.04 $ | 1.7 | +141% | düşük hacim |
| 2020-Q1 | 4 | KALA | KALA BIO, Inc. | Sağlık | 3.83 $ | 1.1 | +128% | düşük hacim |
| 2020-Q1 | 5 | ZM | Zoom Communications, Inc. | Yazılım | 67.28 $ | 149.3 | +91% |  |
| 2020-Q2 | 1 | WKHS | Workhorse Group, Inc. | Sanayi | 1.66 $ | 4.5 | +1,160% |  |
| 2020-Q2 | 2 | OSTK | Neighborhood Intelligence, Inc. | Perakende | 4.91 $ | 10.4 | +581% |  |
| 2020-Q2 | 3 | LOVE | The Lovesac Company | Perakende | 4.21 $ | 2.2 | +533% | düşük hacim |
| 2020-Q2 | 4 | CWH | Camping World Holdings, Inc. | Perakende | 4.54 $ | 9.5 | +515% |  |
| 2020-Q2 | 5 | MGNX | MacroGenics, Inc. | Sağlık | 5.24 $ | 4.0 | +463% |  |
| 2020-Q3 | 1 | MCRB | Seres Therapeutics, Inc. | Sağlık | 4.99 $ | 1.8 | +455% | düşük hacim |
| 2020-Q3 | 2 | CLSK | CleanSpark, Inc. | Finansal hizmet | 2.45 $ | 2.2 | +416% | düşük hacim |
| 2020-Q3 | 3 | RUN | Sunrun Inc. | Diğer | 20.00 $ | 27.9 | +282% |  |
| 2020-Q3 | 4 | RMBL | RideNow Group, Inc. | Yazılım | 9.02 $ | 1.2 | +278% | düşük hacim |
| 2020-Q3 | 5 | SAVA | Filana Therapeutics, Inc. | Sağlık | 2.86 $ | 4.8 | +273% |  |
| 2020-Q4 | 1 | RIOT | Riot Platforms, Inc. | Finansal hizmet | 2.60 $ | 15.1 | +553% |  |
| 2020-Q4 | 2 | FCEL | FuelCell Energy, Inc. | Teknoloji donanım | 2.02 $ | 31.8 | +453% |  |
| 2020-Q4 | 3 | MARA | MARA Holdings, Inc. | Finansal hizmet | 1.96 $ | 13.6 | +433% |  |
| 2020-Q4 | 4 | QS | QuantumScape Corporation | Teknoloji donanım | 15.93 $ | 21.8 | +430% |  |
| 2020-Q4 | 5 | JMIA | Jumia Technologies AG | Perakende | 8.08 $ | 53.0 | +399% |  |

### 2021

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2021-Q1 | 1 | AMTX | Aemetis, Inc | Hammadde | 2.49 $ | 2.7 | +950% | düşük hacim |
| 2021-Q1 | 2 | GME | GameStop Corporation | Perakende | 18.84 $ | 120.8 | +916% |  |
| 2021-Q1 | 3 | NCTY | The9 Limited | Finansal hizmet | 3.54 $ | 1.9 | +860% | düşük hacim |
| 2021-Q1 | 4 | SAVA | Filana Therapeutics, Inc. | Sağlık | 6.82 $ | 13.7 | +587% |  |
| 2021-Q1 | 5 | MARA | MARA Holdings, Inc. | Finansal hizmet | 10.44 $ | 66.5 | +368% |  |
| 2021-Q2 | 1 | AMC | AMC Entertainment Holdings, Inc. | Tüketici | 9.36 $ | 864.7 | +455% |  |
| 2021-Q2 | 2 | NTN | Ernexa Therapeutics Inc. | Sağlık | 3.75 $ | 2.0 | +350% | düşük hacim |
| 2021-Q2 | 3 | ANVS | Annovis Bio, Inc. | Sağlık | 28.23 $ | 4.0 | +244% |  |
| 2021-Q2 | 4 | BTU | Peabody Energy Corporation | Diğer | 3.01 $ | 13.4 | +183% |  |
| 2021-Q2 | 5 | PDSB | PDS Biotechnology Corporation | Sağlık | 4.71 $ | 2.1 | +153% | düşük hacim |
| 2021-Q3 | 1 | UPST | Upstart Holdings, Inc. | Finansal hizmet | 121.21 $ | 501.2 | +146% |  |
| 2021-Q3 | 2 | ANY | DarkHorse Technologies Inc. | Finansal hizmet | 2.69 $ | 2.0 | +122% | düşük hacim |
| 2021-Q3 | 3 | AMR | Alpha Metallurgical Resources, Inc. | Diğer | 25.14 $ | 2.7 | +121% | düşük hacim |
| 2021-Q3 | 4 | SD | SandRidge Energy, Inc. | Enerji | 6.26 $ | 1.7 | +117% | düşük hacim |
| 2021-Q3 | 5 | CIDM | Cineverse Corp. | Tüketici | 1.23 $ | 19.4 | +111% |  |
| 2021-Q4 | 1 | DWACU | Trump Media & Technology Group Corp. | Yazılım | 9.94 $ | 2.2 | +443% | düşük hacim |
| 2021-Q4 | 2 | XENE | Xenon Pharmaceuticals Inc. | Sağlık | 15.60 $ | 3.3 | +96% |  |
| 2021-Q4 | 3 | PTGX | Protagonist Therapeutics, Inc. | Sağlık | 17.95 $ | 15.4 | +94% |  |
| 2021-Q4 | 4 | IRTC | iRhythm Holdings, Inc. | Sağlık | 58.64 $ | 15.4 | +74% |  |
| 2021-Q4 | 5 | F | Ford Motor Company | Sanayi | 14.16 $ | 766.5 | +73% |  |

### 2022

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2022-Q1 | 1 | VYGR | Voyager Therapeutics, Inc. | Biyoteknoloji | 2.80 $ | 1.7 | +198% | düşük hacim |
| 2022-Q1 | 2 | NEXT | NextDecade Corporation | Enerji | 2.65 $ | 1.1 | +162% | düşük hacim |
| 2022-Q1 | 3 | SINO | Singularity Future Technology Ltd. | Sanayi | 4.97 $ | 2.2 | +149% | düşük hacim |
| 2022-Q1 | 4 | BTU | Peabody Energy Corporation | Diğer | 11.37 $ | 55.9 | +129% |  |
| 2022-Q1 | 5 | LXU | LSB Industries, Inc. | Hammadde | 10.31 $ | 2.5 | +125% | düşük hacim |
| 2022-Q2 | 1 | VERU | Veru Inc. | Sağlık | 4.85 $ | 4.3 | +131% |  |
| 2022-Q2 | 2 | ALT | Altimmune, Inc. | Sağlık | 6.22 $ | 5.0 | +81% |  |
| 2022-Q2 | 3 | NVCT | Nuvectis Pharma, Inc. | Sağlık | 7.02 $ | 2.4 | +71% | düşük hacim |
| 2022-Q2 | 4 | DQ | DAQO New Energy Corp. | Yarı iletken | 43.19 $ | 54.1 | +64% |  |
| 2022-Q2 | 5 | STNG | Scorpio Tankers Inc. Common Shares | Sanayi | 21.70 $ | 15.2 | +58% |  |
| 2022-Q3 | 1 | RYTM | Rhythm Pharmaceuticals, Inc. | Sağlık | 4.30 $ | 2.3 | +457% | düşük hacim |
| 2022-Q3 | 2 | VLD | Velo3D, Inc. | Yarı iletken | 1.35 $ | 5.2 | +199% |  |
| 2022-Q3 | 3 | PLRX | Pliant Therapeutics, Inc. | Sağlık | 7.67 $ | 1.3 | +186% | düşük hacim |
| 2022-Q3 | 4 | AEHR | Aehr Test Systems | Yarı iletken | 6.94 $ | 3.1 | +148% |  |
| 2022-Q3 | 5 | KLXE | KLX Energy Services Holdings, Inc. | Enerji | 4.45 $ | 1.5 | +137% | düşük hacim |
| 2022-Q4 | 1 | MDGL | Madrigal Pharmaceuticals, Inc. | Sağlık | 75.03 $ | 13.0 | +275% |  |
| 2022-Q4 | 2 | FDMT | 4D Molecular Therapeutics, Inc. | Biyoteknoloji | 7.12 $ | 1.2 | +226% | düşük hacim |
| 2022-Q4 | 3 | EH | EHang Holdings Limited | Savunma/havacılık | 3.98 $ | 2.1 | +213% | düşük hacim |
| 2022-Q4 | 4 | GOTU | Gaotu Techedu Inc. | Diğer | 1.18 $ | 2.7 | +199% | düşük hacim |
| 2022-Q4 | 5 | VKTX | Viking Therapeutics, Inc. | Sağlık | 2.87 $ | 1.5 | +194% | düşük hacim |

### 2023

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2023-Q1 | 1 | RRGB | Red Robin Gourmet Burgers, Inc. | Perakende | 6.36 $ | 1.5 | +127% | düşük hacim |
| 2023-Q1 | 2 | RIOT | Riot Platforms, Inc. | Finansal hizmet | 4.28 $ | 47.2 | +114% |  |
| 2023-Q1 | 3 | BBIO | BridgeBio Pharma, Inc. | Sağlık | 7.39 $ | 10.6 | +111% |  |
| 2023-Q1 | 4 | AI | C3.ai, Inc. | Yazılım | 10.95 $ | 16.6 | +109% |  |
| 2023-Q1 | 5 | SYM | Symbotic Inc. | Sanayi | 12.41 $ | 1.7 | +105% | düşük hacim |
| 2023-Q2 | 1 | AMTX | Aemetis, Inc | Hammadde | 2.03 $ | 1.9 | +273% | düşük hacim |
| 2023-Q2 | 2 | APLD | Applied Digital Corporation | Yazılım | 2.50 $ | 1.8 | +235% | düşük hacim |
| 2023-Q2 | 3 | CVNA | Carvana Co. | Perakende | 9.01 $ | 140.6 | +227% |  |
| 2023-Q2 | 4 | BTBT | Bit Digital, Inc. | Finansal hizmet | 1.52 $ | 2.6 | +166% | düşük hacim |
| 2023-Q2 | 5 | WULF | TeraWulf Inc. | Finansal hizmet | 1.00 $ | 1.3 | +164% | düşük hacim |
| 2023-Q3 | 1 | GRPN | Groupon, Inc. | Diğer | 6.11 $ | 5.4 | +139% |  |
| 2023-Q3 | 2 | CDLX | Cardlytics, Inc. | Yazılım | 6.06 $ | 3.9 | +119% |  |
| 2023-Q3 | 3 | USM | Array Digital Infrastructure, Inc. Com | İletişim/medya | 18.62 $ | 5.3 | +113% |  |
| 2023-Q3 | 4 | IMVT | Immunovant, Inc. | Biyoteknoloji | 18.55 $ | 16.3 | +95% |  |
| 2023-Q3 | 5 | TDS | Telephone and Data Systems, Inc. Commo | İletişim/medya | 8.76 $ | 15.8 | +91% |  |
| 2023-Q4 | 1 | ZJYL | JIN MEDICAL INTERNATIONAL LTD. | Sağlık | 13.77 $ | 2.9 | +771% | düşük hacim |
| 2023-Q4 | 2 | ALT | Altimmune, Inc. | Sağlık | 2.52 $ | 2.8 | +344% | düşük hacim |
| 2023-Q4 | 3 | IBRX | ImmunityBio, Inc. | Biyoteknoloji | 1.42 $ | 4.5 | +211% |  |
| 2023-Q4 | 4 | CYTK | Cytokinetics, Incorporated | Sağlık | 30.60 $ | 25.5 | +206% |  |
| 2023-Q4 | 5 | MARA | MARA Holdings, Inc. | Finansal hizmet | 8.08 $ | 354.5 | +199% |  |

### 2024

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2024-Q1 | 1 | VKTX | Viking Therapeutics, Inc. | Sağlık | 18.19 $ | 28.2 | +320% |  |
| 2024-Q1 | 2 | SMCI | Super Micro Computer, Inc. | Sanayi | 292.13 $ | 757.1 | +225% |  |
| 2024-Q1 | 3 | ARQT | Arcutis Biotherapeutics, Inc. | Sağlık | 3.71 $ | 6.6 | +206% |  |
| 2024-Q1 | 4 | MNMD | Definium Therapeutics, Inc. | Sağlık | 4.09 $ | 1.1 | +169% | düşük hacim |
| 2024-Q1 | 5 | SOUN | SoundHound AI, Inc. | Yazılım | 1.99 $ | 13.8 | +160% |  |
| 2024-Q2 | 1 | ASTS | AST SpaceMobile, Inc. | İletişim/medya | 2.20 $ | 9.9 | +462% |  |
| 2024-Q2 | 2 | EBS | Emergent BioSolutions Inc. | Sağlık | 2.29 $ | 2.8 | +246% | düşük hacim |
| 2024-Q2 | 3 | CORZ | Core Scientific, Inc. | Finansal hizmet | 3.45 $ | 11.2 | +198% |  |
| 2024-Q2 | 4 | WGS | GeneDx Holdings Corp. | Sağlık | 9.99 $ | 1.2 | +189% | düşük hacim |
| 2024-Q2 | 5 | NVAX | Novavax, Inc. | Biyoteknoloji | 4.42 $ | 27.8 | +169% |  |
| 2024-Q3 | 1 | LUMN | Lumen Technologies, Inc. | İletişim/medya | 1.03 $ | 10.1 | +558% |  |
| 2024-Q3 | 2 | COMM | Vistance Networks, Inc. | Teknoloji donanım | 1.07 $ | 3.4 | +476% |  |
| 2024-Q3 | 3 | CAPR | Capricor Therapeutics, Inc. | Sağlık | 4.81 $ | 1.8 | +350% | düşük hacim |
| 2024-Q3 | 4 | TIGR | UP Fintech Holding Limited | Finansal hizmet | 4.59 $ | 3.6 | +170% |  |
| 2024-Q3 | 5 | SAVA | Filana Therapeutics, Inc. | Sağlık | 10.22 $ | 16.6 | +165% |  |
| 2024-Q4 | 1 | QBTS | D-Wave Quantum Inc. | Yazılım | 1.00 $ | 2.6 | +814% | düşük hacim |
| 2024-Q4 | 2 | CRNC | Cerence Inc. | Yazılım | 2.68 $ | 2.6 | +621% | düşük hacim |
| 2024-Q4 | 3 | DXYZ | Destiny Tech100 Inc. | Diğer | 10.11 $ | 2.3 | +510% | düşük hacim |
| 2024-Q4 | 4 | SRRK | Scholar Rock Holding Corporation | Biyoteknoloji | 7.42 $ | 5.6 | +509% |  |
| 2024-Q4 | 5 | IONQ | IonQ, Inc. | Yazılım | 9.31 $ | 34.4 | +413% |  |

### 2025

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2025-Q1 | 1 | MLGO | MicroAlgo, Inc. | Yazılım | 2.95 $ | 3.4 | +529% |  |
| 2025-Q1 | 2 | DBGI | Digital Brands Group, Inc. | Perakende | 1.54 $ | 1.1 | +507% | düşük hacim |
| 2025-Q1 | 3 | BYAH | Park Ha Biological Technology Co., Ltd | Temel tüketim | 4.40 $ | 2.0 | +209% | düşük hacim |
| 2025-Q1 | 4 | NUTX | Nutex Health Inc. | Diğer | 33.88 $ | 1.2 | +111% | düşük hacim |
| 2025-Q1 | 5 | AGL | agilon health, inc. | Sağlık | 2.09 $ | 7.3 | +99% |  |
| 2025-Q2 | 1 | SEZL | Sezzle Inc. | Diğer | 28.70 $ | 32.6 | +535% |  |
| 2025-Q2 | 2 | NNNN | Anbio Biotechnology | Sağlık | 7.22 $ | 1.0 | +412% | düşük hacim |
| 2025-Q2 | 3 | AEVA | Aeva Technologies, Inc. | Sanayi | 6.57 $ | 1.3 | +401% | düşük hacim |
| 2025-Q2 | 4 | TSSI | TSS, Inc. | Sanayi | 6.24 $ | 13.1 | +350% |  |
| 2025-Q2 | 5 | TNGX | Tango Therapeutics, Inc. | Sağlık | 1.27 $ | 1.5 | +349% | düşük hacim |
| 2025-Q3 | 1 | MENS | Jyong Biotech Ltd. | Sağlık | 7.94 $ | 1.9 | +505% | düşük hacim |
| 2025-Q3 | 2 | ONDS | Ondas Inc | Teknoloji donanım | 1.85 $ | 8.4 | +436% |  |
| 2025-Q3 | 3 | KOD | Kodiak Sciences Inc | Biyoteknoloji | 3.95 $ | 1.2 | +281% | düşük hacim |
| 2025-Q3 | 4 | QURE | uniQure N.V. | Sağlık | 14.42 $ | 16.5 | +281% |  |
| 2025-Q3 | 5 | VERI | Veritone, Inc. | Yazılım | 1.49 $ | 1.0 | +275% | düşük hacim |
| 2025-Q4 | 1 | PRAX | Praxis Precision Medicines, Inc. | Sağlık | 54.38 $ | 20.5 | +427% |  |
| 2025-Q4 | 2 | SIDU | Sidus Space, Inc. | İletişim/medya | 1.10 $ | 1.2 | +294% | düşük hacim |
| 2025-Q4 | 3 | HYMC | Hycroft Mining Holding Corporation | Madencilik | 6.24 $ | 2.8 | +291% | düşük hacim |
| 2025-Q4 | 4 | CAPR | Capricor Therapeutics, Inc. | Sağlık | 7.36 $ | 10.3 | +285% |  |
| 2025-Q4 | 5 | OMER | Omeros Corporation | Sağlık | 4.58 $ | 3.5 | +258% |  |

### 2026

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2026-Q1 | 1 | ERAS | Erasca, Inc. | Sağlık | 3.59 $ | 4.9 | +396% |  |
| 2026-Q1 | 2 | IBRX | ImmunityBio, Inc. | Biyoteknoloji | 2.02 $ | 22.3 | +261% |  |
| 2026-Q1 | 3 | SATL | Satellogic Inc. | Teknoloji donanım | 1.96 $ | 6.6 | +245% |  |
| 2026-Q1 | 4 | FSLY | Fastly, Inc. | Yazılım | 10.19 $ | 31.9 | +229% |  |
| 2026-Q1 | 5 | AXTI | AXT Inc | Yarı iletken | 16.76 $ | 31.7 | +215% |  |
| 2026-Q2 | 1 | AGL | agilon health, inc. | Sağlık | 10.74 $ | 3.6 | +934% |  |
| 2026-Q2 | 2 | MXL | MaxLinear, Inc | Yarı iletken | 17.98 $ | 18.1 | +418% |  |
| 2026-Q2 | 3 | APPS | Digital Turbine, Inc. | Diğer | 2.89 $ | 10.5 | +340% |  |
| 2026-Q2 | 4 | BLZE | Backblaze, Inc. | Yazılım | 3.64 $ | 2.9 | +329% | düşük hacim |
| 2026-Q2 | 5 | FCEL | FuelCell Energy, Inc. | Teknoloji donanım | 6.60 $ | 10.6 | +326% |  |
| 2026-Q3 | 1 | USDE | StablecoinX Inc. | Finansal hizmet | 2.78 $ | 1.6 | +409% | düşük hacim |
| 2026-Q3 | 2 | PSIG | PS International Group Ltd. | Sanayi | 1.27 $ | 4.8 | +261% |  |
| 2026-Q3 | 3 | QMCO | Quantum Corporation | Sanayi | 10.16 $ | 6.2 | +240% |  |
| 2026-Q3 | 4 | IOVA | Iovance Biotherapeutics, Inc. | Biyoteknoloji | 4.31 $ | 47.0 | +230% |  |
| 2026-Q3 | 5 | BRR | Silvia, Inc. | Finansal hizmet | 1.65 $ | 1.5 | +159% | düşük hacim |

## 6 aylık dönemler

### Özet: en iyi 3 / 5 / 10 hissenin ortalama getirisi

| Dönem | Hisse sayısı | S&P 500 | Evren medyanı | En iyi 3 | En iyi 5 | En iyi 10 |
|---|---|---|---|---|---|---|
| 2010-H1 | 1,149 | -7% | -5% | +103% | +93% | +77% |
| 2010-H2 | 1,216 | +26% | +29% | +177% | +166% | +152% |
| 2011-H1 | 1,247 | +6% | +7% | +129% | +113% | +94% |
| 2011-H2 | 1,271 | -4% | -9% | +79% | +68% | +53% |
| 2012-H1 | 1,245 | +7% | +6% | +116% | +104% | +93% |
| 2012-H2 | 1,257 | +9% | +11% | +126% | +117% | +100% |
| 2013-H1 | 1,274 | +12% | +11% | +238% | +217% | +181% |
| 2013-H2 | 1,350 | +13% | +15% | +273% | +240% | +200% |
| 2014-H1 | 1,454 | +9% | +7% | +165% | +144% | +116% |
| 2014-H2 | 1,513 | +5% | +0% | +150% | +128% | +103% |
| 2015-H1 | 1,534 | +2% | +2% | +141% | +134% | +122% |
| 2015-H2 | 1,588 | -1% | -8% | +97% | +84% | +72% |
| 2016-H1 | 1,585 | +4% | +6% | +327% | +292% | +241% |
| 2016-H2 | 1,584 | +9% | +10% | +181% | +167% | +149% |
| 2017-H1 | 1,680 | +8% | +7% | +174% | +155% | +135% |
| 2017-H2 | 1,706 | +14% | +13% | +362% | +307% | +234% |
| 2018-H1 | 1,794 | +2% | +2% | +226% | +210% | +180% |
| 2018-H2 | 1,847 | -7% | -15% | +178% | +140% | +101% |
| 2019-H1 | 1,863 | +19% | +16% | +229% | +212% | +192% |
| 2019-H2 | 1,917 | +9% | +5% | +297% | +253% | +192% |
| 2020-H1 | 1,931 | -2% | -12% | +980% | +763% | +510% |
| 2020-H2 | 2,086 | +21% | +27% | +795% | +694% | +539% |
| 2021-H1 | 2,278 | +17% | +14% | +1,516% | +1,054% | +684% |
| 2021-H2 | 2,638 | +8% | -6% | +142% | +126% | +108% |
| 2022-H1 | 2,657 | -18% | -24% | +139% | +125% | +109% |
| 2022-H2 | 2,488 | +3% | +4% | +458% | +367% | +288% |
| 2023-H1 | 2,357 | +14% | +3% | +400% | +344% | +285% |
| 2023-H2 | 2,405 | +8% | +2% | +217% | +195% | +170% |
| 2024-H1 | 2,422 | +19% | +2% | +272% | +238% | +208% |
| 2024-H2 | 2,513 | +7% | +5% | +687% | +619% | +530% |
| 2025-H1 | 2,671 | +6% | +0% | +638% | +491% | +345% |
| 2025-H2 | 2,751 | +10% | +3% | +565% | +537% | +477% |
| 2026-H1 | 2,940 | +10% | +6% | +451% | +421% | +358% |

Bileşik yıllık (her dönem yalnızca o grubu alıp tutmuş olsaydık; tavan, ulaşılamaz): S&P +14%, en iyi 3 +1,260%, en iyi 10 +764%.

### 2010

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2010-H1 | 1 | CRUS | Cirrus Logic, Inc. | Yarı iletken | 6.82 $ | 3.5 | +128% |  |
| 2010-H1 | 2 | NFLX | Netflix, Inc. | Tüketici | 55.09 $ | 59.8 | +94% |  |
| 2010-H1 | 3 | MUX | McEwen Inc. | Madencilik | 2.37 $ | 2.9 | +87% | düşük hacim |
| 2010-H1 | 4 | CROX | Crocs, Inc. | Diğer | 5.75 $ | 14.8 | +84% |  |
| 2010-H1 | 5 | NC | NACCO Industries, Inc. | Diğer | 49.80 $ | 1.8 | +70% | düşük hacim |
| 2010-H2 | 1 | URI | United Rentals, Inc. | Diğer | 8.53 $ | 20.6 | +196% |  |
| 2010-H2 | 2 | LNG | Cheniere Energy, Inc. | Enerji | 2.68 $ | 2.7 | +169% | düşük hacim |
| 2010-H2 | 3 | VSH | Vishay Intertechnology, Inc. | Teknoloji donanım | 6.69 $ | 19.6 | +165% |  |
| 2010-H2 | 4 | VHC | VirnetX Holding Corp | Diğer | 5.97 $ | 1.5 | +151% | düşük hacim |
| 2010-H2 | 5 | BKNG | Booking Holdings Inc. | Sanayi | 176.41 $ | 266.6 | +150% |  |

### 2011

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2011-H1 | 1 | IPGP | IPG Photonics Corporation | Yarı iletken | 30.11 $ | 5.4 | +150% |  |
| 2011-H1 | 2 | GLNG | Golar LNG Limited | Sanayi | 15.92 $ | 2.4 | +133% | düşük hacim |
| 2011-H1 | 3 | VHC | VirnetX Holding Corp | Diğer | 15.00 $ | 14.1 | +103% |  |
| 2011-H1 | 4 | MLCO | Melco Resorts & Entertainment Limited | Tüketici | 7.01 $ | 30.0 | +94% |  |
| 2011-H1 | 5 | MSTR | Strategy Inc | Finansal hizmet | 89.21 $ | 6.2 | +87% |  |
| 2011-H2 | 1 | SIMO | Silicon Motion Technology Corporation | Yarı iletken | 10.88 $ | 4.6 | +103% |  |
| 2011-H2 | 2 | ROYL | ROYALE ENERGY FUNDS, INC | Enerji | 2.85 $ | 1.6 | +71% | düşük hacim |
| 2011-H2 | 3 | RGR | Sturm, Ruger & Company, Inc. | Diğer | 8.28 $ | 2.5 | +62% | düşük hacim |
| 2011-H2 | 4 | LQDT | Liquidity Services, Inc. | Diğer | 23.18 $ | 2.9 | +61% | düşük hacim |
| 2011-H2 | 5 | MG | Mistras Group Inc | Sanayi | 16.81 $ | 1.6 | +43% | düşük hacim |

### 2012

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2012-H1 | 1 | DDD | 3D Systems Corporation | Yazılım | 16.01 $ | 5.8 | +124% |  |
| 2012-H1 | 2 | AMRN | Amarin Corporation plc | Sağlık | 6.75 $ | 14.8 | +124% |  |
| 2012-H1 | 3 | AVD | American Vanguard Corporation | Hammadde | 13.80 $ | 1.8 | +99% | düşük hacim |
| 2012-H1 | 4 | SWBI | Smith & Wesson Brands, Inc. | Diğer | 4.68 $ | 1.4 | +88% | düşük hacim |
| 2012-H1 | 5 | PCRX | Pacira BioSciences, Inc. | Sağlık | 8.50 $ | 1.4 | +87% | düşük hacim |
| 2012-H2 | 1 | HOV | Hovnanian Enterprises, Inc. | İnşaat | 2.94 $ | 6.7 | +135% |  |
| 2012-H2 | 2 | FSLR | First Solar, Inc. | Yarı iletken | 15.01 $ | 90.7 | +124% |  |
| 2012-H2 | 3 | NOK | Nokia Corporation Sponsored | Teknoloji donanım | 1.92 $ | 95.2 | +118% |  |
| 2012-H2 | 4 | GEOS | Geospace Technologies Corporation | Teknoloji donanım | 84.99 $ | 3.8 | +112% |  |
| 2012-H2 | 5 | GEOY | GeoEye, Inc. | İletişim/medya | 16.04 $ | 4.1 | +99% |  |

### 2013

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2013-H1 | 1 | ACAD | ACADIA Pharmaceuticals Inc. | Sağlık | 4.95 $ | 4.5 | +264% |  |
| 2013-H1 | 2 | TSLA | Tesla, Inc. | Sanayi | 34.40 $ | 28.7 | +249% |  |
| 2013-H1 | 3 | CLDX | Celldex Therapeutics, Inc. | Sağlık | 7.08 $ | 4.0 | +200% |  |
| 2013-H1 | 4 | PBYI | Puma Biotechnology Inc | Sağlık | 19.35 $ | 1.0 | +188% | düşük hacim |
| 2013-H1 | 5 | MNKD | MannKind Corporation | Sağlık | 2.49 $ | 4.2 | +180% |  |
| 2013-H2 | 1 | BCRX | BioCryst Pharmaceuticals, Inc. | Biyoteknoloji | 1.62 $ | 1.4 | +422% | düşük hacim |
| 2013-H2 | 2 | VIPS | Vipshop Holdings Limited | Perakende | 28.37 $ | 13.1 | +200% |  |
| 2013-H2 | 3 | JKS | JinkoSolar Holding Company Limited | Yarı iletken | 11.00 $ | 3.7 | +196% |  |
| 2013-H2 | 4 | CSIQ | Canadian Solar Inc. | Yarı iletken | 12.04 $ | 15.6 | +193% |  |
| 2013-H2 | 5 | RMTI | Rockwell Medical, Inc. | Sağlık | 3.42 $ | 1.6 | +189% | düşük hacim |

### 2014

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2014-H1 | 1 | ALTO | Alto Ingredients, Inc. | Hammadde | 5.08 $ | 1.2 | +206% | düşük hacim |
| 2014-H1 | 2 | GSAT | Globalstar, Inc. | İletişim/medya | 1.74 $ | 4.3 | +156% |  |
| 2014-H1 | 3 | VIPS | Vipshop Holdings Limited | Perakende | 85.10 $ | 64.3 | +134% |  |
| 2014-H1 | 4 | SBSW | D/B/A Sibanye-Stillwater Limited ADS | Madencilik | 4.98 $ | 3.4 | +116% |  |
| 2014-H1 | 5 | GBX | Greenbrier Companies, Inc. (The) | Sanayi | 32.32 $ | 8.5 | +108% |  |
| 2014-H2 | 1 | PBYI | Puma Biotechnology Inc | Sağlık | 70.00 $ | 25.1 | +171% |  |
| 2014-H2 | 2 | AGIO | Agios Pharmaceuticals, Inc. | Sağlık | 44.22 $ | 13.5 | +148% |  |
| 2014-H2 | 3 | OSPN | OneSpan Inc. | Yazılım | 11.89 $ | 2.1 | +130% | düşük hacim |
| 2014-H2 | 4 | AXON | Axon Enterprise, Inc. | Diğer | 13.18 $ | 14.0 | +101% |  |
| 2014-H2 | 5 | GRBK | Green Brick Partners, Inc. | İnşaat | 6.61 $ | 1.7 | +90% | düşük hacim |

### 2015

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2015-H1 | 1 | TVTX | Travere Therapeutics, Inc. | Sağlık | 12.67 $ | 3.3 | +151% |  |
| 2015-H1 | 2 | PRTA | Prothena Corporation plc | Sağlık | 20.35 $ | 4.7 | +148% |  |
| 2015-H1 | 3 | HALO | Halozyme Therapeutics, Inc. | Biyoteknoloji | 9.82 $ | 9.4 | +125% |  |
| 2015-H1 | 4 | AMRN | Amarin Corporation plc | Sağlık | 1.13 $ | 1.3 | +123% | düşük hacim |
| 2015-H1 | 5 | RARE | Ultragenyx Pharmaceutical Inc. | Sağlık | 46.40 $ | 10.2 | +121% |  |
| 2015-H2 | 1 | PACB | Pacific Biosciences of California, Inc | Teknoloji donanım | 5.20 $ | 2.9 | +152% | düşük hacim |
| 2015-H2 | 2 | TRVN | TREVENA INC | Sağlık | 6.01 $ | 1.3 | +75% | düşük hacim |
| 2015-H2 | 3 | CYTK | Cytokinetics, Incorporated | Sağlık | 6.35 $ | 1.6 | +65% | düşük hacim |
| 2015-H2 | 4 | EXEL | Exelixis, Inc. | Biyoteknoloji | 3.44 $ | 8.5 | +64% |  |
| 2015-H2 | 5 | BAK | Braskem SA ADR | Hammadde | 8.26 $ | 4.1 | +64% |  |

### 2016

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2016-H1 | 1 | CDE | Coeur Mining, Inc. | Madencilik | 2.48 $ | 5.3 | +354% |  |
| 2016-H1 | 2 | AG | First Majestic Silver Corp. | Madencilik | 3.27 $ | 5.2 | +353% |  |
| 2016-H1 | 3 | TECK | Teck Resources Ltd | Diğer | 3.86 $ | 39.7 | +274% |  |
| 2016-H1 | 4 | CLF | Cleveland-Cliffs Inc. | Madencilik | 1.58 $ | 9.5 | +263% |  |
| 2016-H1 | 5 | IAG | Iamgold Corporation | Madencilik | 1.42 $ | 6.5 | +215% |  |
| 2016-H2 | 1 | OCN | Onity Group Inc. | Finansal hizmet | 1.74 $ | 3.9 | +231% |  |
| 2016-H2 | 2 | KRO | Kronos Worldwide Inc | Hammadde | 5.32 $ | 2.2 | +156% | düşük hacim |
| 2016-H2 | 3 | CC | Chemours Company (The) | Hammadde | 8.48 $ | 27.5 | +155% |  |
| 2016-H2 | 4 | TROX | Tronox Holdings plc | Hammadde | 4.72 $ | 6.0 | +150% |  |
| 2016-H2 | 5 | BCRX | BioCryst Pharmaceuticals, Inc. | Biyoteknoloji | 2.94 $ | 2.5 | +143% | düşük hacim |

### 2017

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2017-H1 | 1 | AAOI | Applied Optoelectronics, Inc. | Yarı iletken | 22.42 $ | 7.1 | +200% |  |
| 2017-H1 | 2 | AUPH | Aurinia Pharmaceuticals Inc | Sağlık | 2.36 $ | 2.9 | +169% | düşük hacim |
| 2017-H1 | 3 | PBYI | Puma Biotechnology Inc | Sağlık | 34.35 $ | 28.4 | +153% |  |
| 2017-H1 | 4 | BGNE | BeOne Medicines Ltd. | Sağlık | 30.81 $ | 3.5 | +128% |  |
| 2017-H1 | 5 | NVCR | NovoCure Limited | Sağlık | 8.00 $ | 2.7 | +126% | düşük hacim |
| 2017-H2 | 1 | OSTK | Neighborhood Intelligence, Inc. | Perakende | 16.30 $ | 1.3 | +417% | düşük hacim |
| 2017-H2 | 2 | CGC | Canopy Growth Corporation | Sağlık | 6.08 $ | 1.1 | +351% | düşük hacim |
| 2017-H2 | 3 | ANAB | AnaptysBio, Inc. | Sağlık | 24.28 $ | 1.2 | +318% | düşük hacim |
| 2017-H2 | 4 | CBIO | Gyre Therapeutics, Inc. | Sağlık | 4.61 $ | 1.3 | +233% | düşük hacim |
| 2017-H2 | 5 | DQ | DAQO New Energy Corp. | Yarı iletken | 20.40 $ | 1.3 | +218% | düşük hacim |

### 2018

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2018-H1 | 1 | FOSL | Fossil Group, Inc. | Teknoloji donanım | 8.34 $ | 13.0 | +243% |  |
| 2018-H1 | 2 | ARWR | Arrowhead Pharmaceuticals, Inc. | Sağlık | 4.87 $ | 2.8 | +225% | düşük hacim |
| 2018-H1 | 3 | MDGL | Madrigal Pharmaceuticals, Inc. | Sağlık | 96.53 $ | 4.1 | +210% |  |
| 2018-H1 | 4 | RGNX | REGENXBIO Inc. | Biyoteknoloji | 27.85 $ | 8.9 | +185% |  |
| 2018-H1 | 5 | ENPH | Enphase Energy, Inc. | Yarı iletken | 2.47 $ | 1.4 | +185% | düşük hacim |
| 2018-H2 | 1 | AMRN | Amarin Corporation plc | Sağlık | 2.98 $ | 5.1 | +343% |  |
| 2018-H2 | 2 | PACB | Pacific Biosciences of California, Inc | Teknoloji donanım | 3.67 $ | 1.6 | +99% | düşük hacim |
| 2018-H2 | 3 | CIG | Comp En De Mn Cemig ADS | Kamu hizmetleri | 1.93 $ | 7.1 | +94% |  |
| 2018-H2 | 4 | CDNA | CareDx, Inc. | Sağlık | 13.03 $ | 5.0 | +91% |  |
| 2018-H2 | 5 | VCEL | Vericel Corporation | Biyoteknoloji | 10.10 $ | 11.1 | +71% |  |

### 2019

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2019-H1 | 1 | ENPH | Enphase Energy, Inc. | Yarı iletken | 5.08 $ | 7.3 | +287% |  |
| 2019-H1 | 2 | SE | Sea Limited | Diğer | 11.56 $ | 12.6 | +209% |  |
| 2019-H1 | 3 | ROKU | Roku, Inc. | İletişim/medya | 33.73 $ | 332.0 | +191% |  |
| 2019-H1 | 4 | VYGR | Voyager Therapeutics, Inc. | Biyoteknoloji | 9.47 $ | 3.4 | +191% |  |
| 2019-H1 | 5 | IIPR | Innovative Industrial Properties, Inc. | Gayrimenkul | 46.30 $ | 10.3 | +184% |  |
| 2019-H2 | 1 | KOD | Kodiak Sciences Inc | Biyoteknoloji | 13.22 $ | 1.1 | +412% | düşük hacim |
| 2019-H2 | 2 | AXSM | Axsome Therapeutics, Inc. | Sağlık | 27.04 $ | 24.8 | +250% |  |
| 2019-H2 | 3 | NXTC | NextCure, Inc. | Sağlık | 16.63 $ | 1.1 | +229% | düşük hacim |
| 2019-H2 | 4 | AUPH | Aurinia Pharmaceuticals Inc | Sağlık | 6.45 $ | 2.9 | +220% | düşük hacim |
| 2019-H2 | 5 | HOV | Hovnanian Enterprises, Inc. | İnşaat | 8.18 $ | 1.5 | +156% | düşük hacim |

### 2020

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2020-H1 | 1 | NVAX | Novavax, Inc. | Biyoteknoloji | 4.44 $ | 2.9 | +1,739% | düşük hacim |
| 2020-H1 | 2 | INO | Inovio Pharmaceuticals, Inc. | Sağlık | 2.98 $ | 1.8 | +620% | düşük hacim |
| 2020-H1 | 3 | WKHS | Workhorse Group, Inc. | Sanayi | 3.07 $ | 3.7 | +581% |  |
| 2020-H1 | 4 | VERI | Veritone, Inc. | Yazılım | 2.56 $ | 1.0 | +511% | düşük hacim |
| 2020-H1 | 5 | OSTK | Neighborhood Intelligence, Inc. | Perakende | 7.21 $ | 10.9 | +364% |  |
| 2020-H2 | 1 | CLSK | CleanSpark, Inc. | Finansal hizmet | 2.45 $ | 2.2 | +1,086% | düşük hacim |
| 2020-H2 | 2 | JMIA | Jumia Technologies AG | Perakende | 5.33 $ | 9.9 | +657% |  |
| 2020-H2 | 3 | RIOT | Riot Platforms, Inc. | Finansal hizmet | 2.29 $ | 7.1 | +642% |  |
| 2020-H2 | 4 | PACB | Pacific Biosciences of California, Inc | Teknoloji donanım | 3.74 $ | 4.4 | +594% |  |
| 2020-H2 | 5 | GRWG | GrowGeneration Corp. | Perakende | 6.80 $ | 2.7 | +491% | düşük hacim |

### 2021

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2021-H1 | 1 | AMC | AMC Entertainment Holdings, Inc. | Tüketici | 2.12 $ | 56.0 | +2,351% |  |
| 2021-H1 | 2 | SAVA | Filana Therapeutics, Inc. | Sağlık | 6.82 $ | 13.7 | +1,220% |  |
| 2021-H1 | 3 | GME | GameStop Corporation | Perakende | 18.84 $ | 120.8 | +977% |  |
| 2021-H1 | 4 | PRTA | Prothena Corporation plc | Sağlık | 12.01 $ | 2.3 | +362% | düşük hacim |
| 2021-H1 | 5 | CDEV | Permian Resources Corporation | Enerji | 1.50 $ | 5.3 | +359% |  |
| 2021-H2 | 1 | CAR | Avis Budget Group, Inc. | Diğer | 78.94 $ | 91.7 | +150% |  |
| 2021-H2 | 2 | AMR | Alpha Metallurgical Resources, Inc. | Diğer | 25.14 $ | 2.7 | +149% | düşük hacim |
| 2021-H2 | 3 | LQDA | Liquidia Corporation | Sağlık | 2.76 $ | 1.1 | +127% | düşük hacim |
| 2021-H2 | 4 | PHUN | Phunware, Inc. | Yazılım | 1.30 $ | 2.2 | +105% | düşük hacim |
| 2021-H2 | 5 | LEU | Centrus Energy Corp. | Diğer | 25.77 $ | 1.9 | +101% | düşük hacim |

### 2022

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2022-H1 | 1 | STNG | Scorpio Tankers Inc. Common Shares | Sanayi | 13.13 $ | 12.0 | +163% |  |
| 2022-H1 | 2 | LNTH | Lantheus Holdings, Inc. | Sağlık | 26.89 $ | 10.4 | +136% |  |
| 2022-H1 | 3 | VYGR | Voyager Therapeutics, Inc. | Biyoteknoloji | 2.80 $ | 1.7 | +117% | düşük hacim |
| 2022-H1 | 4 | VERU | Veru Inc. | Sağlık | 5.46 $ | 5.3 | +105% |  |
| 2022-H1 | 5 | CEIX | Core Natural Resources, Inc. | Diğer | 23.52 $ | 10.4 | +105% |  |
| 2022-H2 | 1 | RYTM | Rhythm Pharmaceuticals, Inc. | Sağlık | 4.30 $ | 2.3 | +696% | düşük hacim |
| 2022-H2 | 2 | IMVT | Immunovant, Inc. | Biyoteknoloji | 3.98 $ | 1.4 | +395% | düşük hacim |
| 2022-H2 | 3 | MDGL | Madrigal Pharmaceuticals, Inc. | Sağlık | 73.59 $ | 13.5 | +282% |  |
| 2022-H2 | 4 | FDMT | 4D Molecular Therapeutics, Inc. | Biyoteknoloji | 6.96 $ | 1.7 | +233% | düşük hacim |
| 2022-H2 | 5 | KLXE | KLX Energy Services Holdings, Inc. | Enerji | 4.45 $ | 1.5 | +230% | düşük hacim |

### 2023

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2023-H1 | 1 | CVNA | Carvana Co. | Perakende | 4.41 $ | 148.8 | +568% |  |
| 2023-H1 | 2 | APLD | Applied Digital Corporation | Yazılım | 1.86 $ | 1.0 | +350% | düşük hacim |
| 2023-H1 | 3 | MARA | MARA Holdings, Inc. | Finansal hizmet | 4.09 $ | 134.6 | +283% |  |
| 2023-H1 | 4 | RIOT | Riot Platforms, Inc. | Finansal hizmet | 4.28 $ | 47.2 | +262% |  |
| 2023-H1 | 5 | AI | C3.ai, Inc. | Yazılım | 10.95 $ | 16.6 | +258% |  |
| 2023-H2 | 1 | ALT | Altimmune, Inc. | Sağlık | 3.29 $ | 6.6 | +240% |  |
| 2023-H2 | 2 | AFRM | Affirm Holdings, Inc. | Finansal hizmet | 13.65 $ | 179.1 | +215% |  |
| 2023-H2 | 3 | NKTX | Nkarta, Inc. | Sağlık | 2.05 $ | 1.3 | +196% | düşük hacim |
| 2023-H2 | 4 | CYTK | Cytokinetics, Incorporated | Sağlık | 34.71 $ | 29.2 | +170% |  |
| 2023-H2 | 5 | ANF | Abercrombie & Fitch Company | Perakende | 35.54 $ | 42.4 | +155% |  |

### 2024

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2024-H1 | 1 | SMR | NuScale Power Corporation | Diğer | 2.62 $ | 6.1 | +366% |  |
| 2024-H1 | 2 | EBS | Emergent BioSolutions Inc. | Sağlık | 2.20 $ | 3.0 | +260% |  |
| 2024-H1 | 3 | SMCI | Super Micro Computer, Inc. | Sanayi | 292.13 $ | 757.1 | +190% |  |
| 2024-H1 | 4 | WULF | TeraWulf Inc. | Finansal hizmet | 1.93 $ | 10.9 | +189% |  |
| 2024-H1 | 5 | VITL | Vital Farms, Inc. | Temel tüketim | 15.35 $ | 3.0 | +187% |  |
| 2024-H2 | 1 | GRRR | Gorilla Technology Group Inc. | Yazılım | 2.66 $ | 1.3 | +784% | düşük hacim |
| 2024-H2 | 2 | QBTS | D-Wave Quantum Inc. | Yazılım | 1.10 $ | 3.8 | +731% |  |
| 2024-H2 | 3 | IONQ | IonQ, Inc. | Yazılım | 7.41 $ | 33.9 | +545% |  |
| 2024-H2 | 4 | CRNC | Cerence Inc. | Yazılım | 3.09 $ | 5.8 | +526% |  |
| 2024-H2 | 5 | LUNR | Intuitive Machines, Inc. | Savunma/havacılık | 3.59 $ | 9.9 | +510% |  |

### 2025

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2025-H1 | 1 | BYAH | Park Ha Biological Technology Co., Ltd | Temel tüketim | 4.40 $ | 2.0 | +822% | düşük hacim |
| 2025-H1 | 2 | DBGI | Digital Brands Group, Inc. | Perakende | 1.54 $ | 1.1 | +561% | düşük hacim |
| 2025-H1 | 3 | AEVA | Aeva Technologies, Inc. | Sanayi | 5.22 $ | 1.4 | +530% | düşük hacim |
| 2025-H1 | 4 | SEZL | Sezzle Inc. | Diğer | 278.69 $ | 29.0 | +292% |  |
| 2025-H1 | 5 | NUTX | Nutex Health Inc. | Diğer | 33.88 $ | 1.2 | +249% | düşük hacim |
| 2025-H2 | 1 | CELC | Celcuity Inc. | Sağlık | 13.79 $ | 1.9 | +629% | düşük hacim |
| 2025-H2 | 2 | KOD | Kodiak Sciences Inc | Biyoteknoloji | 3.95 $ | 1.2 | +559% | düşük hacim |
| 2025-H2 | 3 | PRAX | Praxis Precision Medicines, Inc. | Sağlık | 47.26 $ | 11.6 | +506% |  |
| 2025-H2 | 4 | ONDS | Ondas Inc | Teknoloji donanım | 1.85 $ | 8.4 | +496% |  |
| 2025-H2 | 5 | SNDK | Sandisk Corporation | Sanayi | 46.41 $ | 84.4 | +493% |  |

### 2026

| Dönem | Sıra | Hisse | Şirket | Sektör | Başlangıç fiyatı | Günlük işlem (M$) | Getiri | Not |
|---|---|---|---|---|---|---|---|---|
| 2026-H1 | 1 | SNDK | Sandisk Corporation | Sanayi | 275.24 $ | 1,916.0 | +534% |  |
| 2026-H1 | 2 | ERAS | Erasca, Inc. | Sağlık | 3.59 $ | 4.9 | +414% |  |
| 2026-H1 | 3 | MXL | MaxLinear, Inc | Yarı iletken | 18.51 $ | 19.2 | +403% |  |
| 2026-H1 | 4 | ICHR | Ichor Holdings | Yarı iletken | 20.41 $ | 13.2 | +381% |  |
| 2026-H1 | 5 | ATEX | Anterix Inc. | İletişim/medya | 22.23 $ | 4.0 | +373% |  |

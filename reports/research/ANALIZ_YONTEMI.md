# Ana Analiz Yöntemi: Dönem Karşılaştırma Tablosu

Kullanıcı kararı (19 Ekim 2026): her yeni kural ya da model bu tabloyla değerlendirilir ve sonuçlar bu biçimde sunulur.

Her çeyrek başı (Ocak, Nisan, Temmuz, Ekim) için yan yana:
1. **Gerçekte en çok kazandıran 3 hisse** (sonradan bakınca) ve bunların 3 ay / 6 ay getirisi.
2. **Her model:** o gün yalnızca o güne kadarki veriyle seçtiği hisseler, seçtiği 3 hissenin 3 ay / 6 ay getirisi ve seçtiği bütün hisselerin ortalaması.
3. **S&P 500:** aynı dönemde 3 ay / 6 ay.

Bunlara ek olarak her model için iki bilgi verilir:
- **Veriyi gördü mü:** Kural geçmiş veriye bakılarak mı bulundu? Gerçekten görülmemiş test yalnızca canlı kayıttır.
- **Özet tablo:** ortalamalar, S&P'yi geçtiği dönem payı ve en iyi 20'den yakalanan hisse sayısı.

**Kod ve çıktılar:**
- Kod: `radar/research/donem_tablosu.py`. Yeni model eklemek için `MODELS` sözlüğüne bir satır eklenir.
- Çıktılar: `donem_tablosu.md` (her dönem), `donem_tablosu.csv`, `donem_tablosu_ozet.csv`.

**Kurallar:**
- Eşitlikler rastgele bozulur; tablo satır sırası geleceği taşıdığı için.
- Getiriler brüt hesaplanır; maliyetli bileşik sonuçlar ayrı raporlarda verilir.

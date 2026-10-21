/* Dip Radarı — kontrol listesi mantığı (arastirma/mekanizma/dip/kontrol.py ile birebir aynı kurallar).
   Bu bir KONTROL LİSTESİDİR; doğrulanmış sinyal değildir. */
(function (root) {
  "use strict";
  var ESIK = { zirveden: -25, mtd: -12, gun: -8, sektorMin: 5, kucuk: 2000, orta: 10000, hacimDusuk: 0.3 };
  var BASLIKLAR = ["1. Neden düştü?", "2. Kötü günü atlatır mı?", "3. İşler nasıl?", "4. Fiyat cazip mi?", "5. Toparlanma işareti", "6. Kaybım sınırlı mı?"];

  function g(x) { return typeof x === "number" && !isNaN(x); }
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  function pick(f, s, k) { return has(f, k) ? f[k] : s[k]; }
  function sg(x, d) { return (x >= 0 ? "+" : "−") + Math.abs(x).toFixed(d || 0); }
  function median(a) { a = a.slice().sort(function (x, y) { return x - y; }); var n = a.length; return n % 2 ? a[(n - 1) / 2] : (a[n / 2 - 1] + a[n / 2]) / 2; }

  function veriTutarli(s, q) {
    if (!(q && s.hi52 && g(s.r52w))) return true;
    var uzak = (q.price / s.hi52 - 1) * 100;
    return !(uzak <= -60 && s.r52w > -30);
  }
  function adayMi(s, q) {
    if (!s) return false;
    var uzak = (q && s.hi52) ? (q.price / s.hi52 - 1) * 100 : null;
    return !!((uzak !== null && uzak <= ESIK.zirveden) || (g(s.mtd) && s.mtd <= ESIK.mtd) || (q && (q.chgPct === undefined || q.chgPct === null ? 0 : q.chgPct) <= ESIK.gun));
  }

  function sektorIstatistik(d) {
    var gr = {};
    Object.keys(d.screen).forEach(function (t) {
      var i = d.prof[t] && d.prof[t].ind;
      if (i) (gr[i] = gr[i] || []).push(d.screen[t]);
    });
    var out = {};
    Object.keys(gr).forEach(function (i) {
      var lst = gr[i];
      if (lst.length < ESIK.sektorMin) return;
      var med = function (a) {
        var v = lst.map(function (x) { return x[a]; }).filter(function (x) { return g(x) && (a !== "pe" || x > 0); });
        return v.length ? median(v) : null;
      };
      out[i] = { n: lst.length, r13w: med("r13w"), pe: med("pe"), ps: med("ps") };
    });
    return out;
  }

  /* h: {s, q, f, sek} -> [[baslikNo, madde, durum, aciklama], ...] ; durum: yesil|kirmizi|sari|bilinmiyor|bilgi */
  function degerlendir(h) {
    var s = h.s, q = h.q, f = h.f || {}, sek = h.sek, o = [];
    var add = function (b, m, d, a) { o.push([b, m, d, a]); };
    // 1. Neden düştü
    if (sek && sek.r13w !== null && sek.r13w !== undefined && g(s.r13w)) {
      var fark = s.r13w - sek.r13w;
      if (sek.r13w <= -5 && fark > -10) add(1, "Sektör mü, şirket mi?", "yesil", "Sektör de düşmüş (3 ay medyan " + sg(sek.r13w) + "%); hisse sektörden çok farklı değil (" + sg(fark) + " puan)");
      else if (fark <= -15) add(1, "Sektör mü, şirket mi?", "kirmizi", "Şirkete özgü görünüyor: sektörden " + sg(fark) + " puan kötü (3 ay)");
      else add(1, "Sektör mü, şirket mi?", "sari", "Sektörden " + sg(fark) + " puan farklı (3 ay); net değil");
    } else add(1, "Sektör mü, şirket mi?", "bilinmiyor", "Sektör karşılaştırması için yeterli veri yok");
    add(1, "Düşüşün haberi/nedeni", "bilinmiyor", "Haber verisi yok. ELLE BAK: bu düşüşün sebebi ne?");
    // 2. Kötü günü atlatır mı
    ["Nakit ömrü", "Borç vadesi", "Hisse seyrelmesi"].forEach(function (m) { add(2, m, "bilinmiyor", "Veri yok. ELLE BAK: kasa, borç takvimi, yeni hisse çıkarma geçmişi"); });
    var nm = pick(f, s, "netM");
    if (g(nm)) {
      if (nm < 0) add(2, "Kârlılık (nakit vekili)", "kirmizi", "Zararda (net marj " + nm.toFixed(0) + "%): nakit ömrü kritik");
      else add(2, "Kârlılık (nakit vekili)", "yesil", "Kârlı (net marj " + nm.toFixed(0) + "%); nakit sıkıntısı olasılığı düşük ama bu bir vekil");
    }
    // 3. İşler
    var rg = pick(f, s, "revG");
    if (g(rg)) add(3, "Satışlar", rg >= 0 ? "yesil" : "kirmizi", "Son rapor satış büyümesi " + sg(rg) + "%" + (rg >= 0 ? "" : " (küçülüyor; nedeni geçici mi?)"));
    var gt = pick(f, s, "gmT"), g5 = pick(f, s, "gm5");
    if (g(gt) && g(g5)) {
      var dm = gt - g5;
      add(3, "Brüt marj", dm >= -3 ? "yesil" : "kirmizi", "Brüt marj " + gt.toFixed(0) + "% (5 yıl önce " + g5.toFixed(0) + "%, " + sg(dm) + " puan)" + (dm >= -3 ? "" : "; daralmanın nedeni geçici mi, kalıcı mı?"));
    }
    if (g(nm)) add(3, "Net marj", nm > 0 ? "yesil" : "kirmizi", "Net marj " + nm.toFixed(0) + "%");
    add(3, "Kâr gerçek mi (nakit dönüşümü)", "bilinmiyor", "Nakit akışı verisi yok. ELLE BAK: kâr kasaya para olarak giriyor mu?");
    var pe = pick(f, s, "pe");
    if (g(pe) && g(rg) && pe < 15 && rg < 0) add(3, "Değer tuzağı", "kirmizi", "Ucuz görünüyor ama satışlar küçülüyor");
    if (g(nm) && g(pe) && nm > 40 && pe < 6) add(3, "Tek seferlik kâr", "kirmizi", "Aşırı yüksek net marj + çok düşük F/K: kâr tek seferlik olabilir");
    if (g(s.r52w) && s.r52w > 300 && g(gt) && gt < 0) add(3, "Enkaz sıçraması", "kirmizi", "Çok sıçramış ama brüt marj negatif: iflas sonrası olabilir");
    // 4. Fiyat cazip mi
    if (sek && g(pe) && pe > 0 && sek.pe) {
      var r = pe / sek.pe;
      add(4, "Değerleme (sektöre göre F/K)", r <= 1 ? "yesil" : (r >= 1.5 ? "kirmizi" : "sari"), "F/K " + pe.toFixed(0) + ", sektör medyanı " + sek.pe.toFixed(0) + " (" + r.toFixed(1) + "×)");
    } else if (sek && g(s.ps) && sek.ps) {
      var r2 = s.ps / sek.ps;
      add(4, "Değerleme (sektöre göre fiyat/satış)", r2 <= 1 ? "yesil" : (r2 >= 1.5 ? "kirmizi" : "sari"), "Fiyat/satış " + s.ps.toFixed(1) + ", sektör medyanı " + sek.ps.toFixed(1) + " (" + r2.toFixed(1) + "×); kârsız olduğu için F/K yok");
    } else add(4, "Değerleme", "bilinmiyor", "Sektör karşılaştırması için yeterli veri yok");
    add(4, "Beklentiler değişti mi", "bilinmiyor", "Analist tahmin geçmişi yok. ELLE BAK: kazanç beklentisi düşüşle birlikte ne kadar kırıldı?");
    // 5. Toparlanma işareti
    var ins = f.insBuyers;
    if (ins !== undefined && ins !== null) add(5, "İçeriden alım", ins >= 1 ? "yesil" : "sari", ins >= 1 ? "Son dönemde içeriden alan yönetici var (ipucu, garanti değil)" : "İçeriden alım yok");
    var eps = f.epsSurprise;
    if (g(eps) && eps >= 8) add(5, "Son bilanço sürprizi", "bilgi", "Kâr sürprizi " + sg(eps) + "% (puana katılmaz; Klasik Radar ölçümünde tek başına güvenilmez)");
    add(5, "Yeni ve iyi haber / beklentiden iyi mi", "bilinmiyor", "Haber verisi yok. ELLE BAK");
    if (q && g(q.chgPct)) add(5, "Bugünkü fiyat tepkisi", "bilgi", "Bugün " + sg(q.chgPct, 1) + "% (tek günlük hareket, puana katılmaz)");
    // 6. Risk
    var mc = pick(f, s, "mcap");
    if (g(mc)) {
      if (mc < ESIK.kucuk) add(6, "Şirket büyüklüğü", "kirmizi", "Çok küçük (" + (mc / 1000).toFixed(1) + " mlr$): batma/likidite riski, küçük tutarla gir");
      else if (mc < ESIK.orta) add(6, "Şirket büyüklüğü", "sari", "Küçük-orta (" + (mc / 1000).toFixed(1) + " mlr$)");
      else add(6, "Şirket büyüklüğü", "yesil", "Büyük (" + (mc / 1000).toFixed(0) + " mlr$)");
    }
    var av = s.avgVol;
    if (g(av)) add(6, "İşlem hacmi (çıkabilir miyim?)", av < ESIK.hacimDusuk ? "kirmizi" : "yesil", "Ortalama hacim " + av.toFixed(2) + " milyon hisse" + (av < ESIK.hacimDusuk ? " (düşük)" : ""));
    return o;
  }

  function ozet(m) {
    var c = { yesil: 0, kirmizi: 0, sari: 0, bilinmiyor: 0, bilgi: 0 };
    m.forEach(function (x) { c[x[2]]++; });
    var olculen = c.yesil + c.kirmizi + c.sari;
    var baslik = {};
    for (var no = 1; no <= 6; no++) {
      var ds = m.filter(function (x) { return x[0] === no; }).map(function (x) { return x[2]; }).filter(function (d) { return d !== "bilgi"; });
      if (!ds.length || ds.every(function (d) { return d === "bilinmiyor"; })) baslik[no] = "bilinmiyor";
      else if (ds.indexOf("kirmizi") >= 0) baslik[no] = "kirmizi";
      else if (ds.every(function (d) { return d === "yesil" || d === "bilinmiyor"; })) baslik[no] = "yesil";
      else baslik[no] = "sari";
    }
    return { yesil: c.yesil, kirmizi: c.kirmizi, sari: c.sari, bilinmiyor: c.bilinmiyor, olculen: olculen, skor: olculen ? (c.yesil - 2 * c.kirmizi) / olculen : 0, baslik: baslik };
  }

  /* HER hisse için elle bakılacaklar: önce bu hisseye özgü uyarılar, sonra ölçülemeyen standart maddeler. */
  function kontrolSorulari(m, tutarsiz) {
    var has_ = function (madde, durum) { return m.some(function (x) { return x[1] === madde && x[2] === durum; }); };
    var o = [];
    if (tutarsiz) o.push({ ozel: true, t: "Bu hissenin fiyat/zirve verisi tutarsız (yerel para birimi ya da çift listeleme olabilir). Önce gerçek fiyatı ve gerçek düşüşü doğrula." });
    if (has_("Sektör mü, şirket mi?", "kirmizi")) o.push({ ozel: true, t: "Sektöründen çok daha kötü düştü: şirkete özgü bir sorun var mı (ürün, müşteri kaybı, dava, yönetim, kılavuz kesintisi)?" });
    if (has_("Kârlılık (nakit vekili)", "kirmizi")) o.push({ ozel: true, t: "Zararda: kasadaki para yıllık nakit yakımına kaç ay yetiyor? Para bulmak için yeni hisse çıkarması bekleniyor mu?" });
    if (has_("Satışlar", "kirmizi") || has_("Değer tuzağı", "kirmizi")) o.push({ ozel: true, t: "Satışlar küçülüyor: neden? Geçici mi (tek müşteri, mevsim), yapısal mı (ürün eskidi, rakip aldı)?" });
    if (has_("Brüt marj", "kirmizi")) o.push({ ozel: true, t: "Marj daraldı: geçici maliyet artışı mı, yeni pazara giriş mi, yoksa fiyat gücü mü kaybediliyor? Rakipler de aynı mı?" });
    if (has_("Tek seferlik kâr", "kirmizi")) o.push({ ozel: true, t: "Kâr tek seferlik olabilir: varlık satışı, vergi iadesi, dava geliri var mı? Normalleşmiş kâr ne?" });
    if (has_("Enkaz sıçraması", "kirmizi")) o.push({ ozel: true, t: "İflas sonrası sıçrama olabilir: yeniden yapılanma geçmişi ve borç durumunu kontrol et." });
    if (m.some(function (x) { return x[0] === 4 && x[2] === "kirmizi"; })) o.push({ ozel: true, t: "Düştü ama hâlâ sektöründen pahalı: gerçek değeri nedir, beklentiler hâlâ geçerli mi?" });
    if (has_("Şirket büyüklüğü", "kirmizi")) o.push({ ozel: true, t: "Çok küçük şirket: batma riski, günlük işlem hacmi, kaybetmeyi göze alabileceğin tutar. Yakın bir tetikleyici (sözleşme, onay) var mı?" });
    if (has_("İşlem hacmi (çıkabilir miyim?)", "kirmizi")) o.push({ ozel: true, t: "İşlem hacmi düşük: satmak istediğinde alıcı bulabilir misin?" });
    var std = [
      "Neden düştü? Son haberleri oku: şirkete özgü mü, dışsal korku mu? Fiyat kötü haberin ne kadarını zaten yansıttı?",
      "Nakit ömrü: kasadaki para, ayda yaktığı paraya bölününce kaç ay yetiyor?",
      "Borç: ne zaman vadesi doluyor, faizi ne? Yeniden finansman gerekiyor mu?",
      "Seyrelme: son yıllarda para bulmak için yeni hisse çıkardı mı? Çıkarması bekleniyor mu?",
      "Kâr gerçek mi: işletmeden nakit girişi pozitif mi? Alacaklar ve stoklar şişiyor mu?",
      "Beklentiler: analistlerin kazanç tahmini düşüşten beri ne kadar kırıldı?",
      "Yeni ve iyi haber var mı, piyasanın beklediğinden daha mı iyi? (Resmî açıklamalara bak)",
      "İçeriden alım/satım: yöneticiler piyasadan gerçek alım mı yapıyor, otomatik plan mı?"
    ];
    std.forEach(function (t) { o.push({ ozel: false, t: t }); });
    return o;
  }

  function hesapla(d) {
    var sek = sektorIstatistik(d), adaylar = [], tutarsiz = [];
    Object.keys(d.screen).forEach(function (t) {
      var s = d.screen[t], q = d.quotes[t];
      if (!adayMi(s, q)) return;
      var ind = d.prof[t] && d.prof[t].ind;
      var ad = (d.prof[t] && d.prof[t].name) || (d.fin[t] && d.fin[t].name) || t;
      var uzak = (q && s.hi52) ? (q.price / s.hi52 - 1) * 100 : null;
      var m = degerlendir({ s: s, q: q, f: d.fin[t], sek: sek[ind] });
      var haber = ((d.fin[t] && d.fin[t].news) || []).slice(0, 3);
      if (!veriTutarli(s, q)) {
        tutarsiz.push({ sembol: t, ad: ad, sektor: ind || "", zirveden: uzak, mtd: s.mtd, maddeler: m, sorular: kontrolSorulari(m, true), haber: haber, tutarsiz: true });
        return;
      }
      var oz = ozet(m);
      adaylar.push({ sembol: t, ad: ad, sektor: ind || "", zirveden: uzak, mtd: s.mtd, maddeler: m, yesil: oz.yesil, kirmizi: oz.kirmizi, sari: oz.sari, bilinmiyor: oz.bilinmiyor, olculen: oz.olculen, skor: oz.skor, baslik: oz.baslik, sorular: kontrolSorulari(m, false), haber: haber });
    });
    adaylar.sort(function (a, b) { return (b.skor - a.skor) || (b.olculen - a.olculen) || (a.kirmizi - b.kirmizi); });
    return { tarih: (d.generatedAt || "").slice(0, 10), adaylar: adaylar, tutarsiz: tutarsiz };
  }

  var API = { hesapla: hesapla, degerlendir: degerlendir, ozet: ozet, kontrolSorulari: kontrolSorulari, adayMi: adayMi, veriTutarli: veriTutarli, sektorIstatistik: sektorIstatistik, BASLIKLAR: BASLIKLAR };
  if (typeof module !== "undefined" && module.exports) module.exports = API; else root.DipKontrol = API;
})(typeof window !== "undefined" ? window : globalThis);

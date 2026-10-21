// Dip Radarı kural testleri. Çalıştır: node --test dip/kontrol.test.js
const test = require("node:test");
const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");
const K = require("./kontrol.js");

const durum = (m) => Object.fromEntries(m.map((x) => [x[1], x[2]]));

test("aday seçimi: zirveden, ay başından ya da tek günde düşüş", () => {
  assert.ok(K.adayMi({ hi52: 100, mtd: 0, r52w: -10 }, { price: 70, chgPct: 0 }));
  assert.ok(K.adayMi({ hi52: 100, mtd: -15, r52w: 0 }, { price: 99, chgPct: 0 }));
  assert.ok(K.adayMi({ hi52: 100, mtd: 0, r52w: 0 }, { price: 99, chgPct: -9 }));
  assert.ok(!K.adayMi({ hi52: 100, mtd: -2, r52w: 0 }, { price: 95, chgPct: -1 }));
});

test("tutarsız zirve verisi yakalanır (yerel para birimi)", () => {
  assert.ok(!K.veriTutarli({ hi52: 2590, r52w: 17 }, { price: 420 }));
  assert.ok(K.veriTutarli({ hi52: 100, r52w: -50 }, { price: 38 }));
});

test("sektör karşılaştırması aday ölçüsüyle aynı: zirveden düşüş", () => {
  const s = { hi52: 100, r13w: 5, mtd: 1, r52w: -30 };          // son 3 ayda yükselmiş ama zirveden -%40
  const kotu = durum(K.degerlendir({ s, q: { price: 60 }, f: {}, sek: { zirveden: -10, mtd: 0, pe: 20, ps: 3 } }));
  assert.strictEqual(kotu["Sektör mü, şirket mi?"], "kirmizi");  // sektör -%10, hisse -%40: şirkete özgü
  const ortak = durum(K.degerlendir({ s, q: { price: 60 }, f: {}, sek: { zirveden: -35, mtd: 0, pe: 20, ps: 3 } }));
  assert.strictEqual(ortak["Sektör mü, şirket mi?"], "yesil");   // sektör de -%35
  const fiyatsiz = durum(K.degerlendir({ s: { mtd: -15 }, q: null, f: {}, sek: { zirveden: -10, mtd: -2 } }));
  assert.strictEqual(fiyatsiz["Sektör mü, şirket mi?"], "kirmizi"); // fiyat yoksa bu ayki düşüşle kıyaslanır
});

test("kırmızı bayraklar ve bilinmeyenler", () => {
  const s = { hi52: 100, mtd: -10, r52w: -20, gmT: 20, gm5: 40, netM: -5, revG: -10, pe: 8, avgVol: 0.1, mcap: 800, ps: 1 };
  const m = durum(K.degerlendir({ s, q: { price: 60, chgPct: 1 }, f: {}, sek: { zirveden: -5, mtd: 0, pe: 20, ps: 3 } }));
  for (const k of ["Satışlar", "Brüt marj", "Net marj", "Değer tuzağı", "Şirket büyüklüğü", "Kârlılık (nakit vekili)"]) assert.strictEqual(m[k], "kirmizi", k);
  for (const k of ["Nakit ömrü", "Borç vadesi", "Hisse seyrelmesi", "Düşüşün haberi/nedeni"]) assert.strictEqual(m[k], "bilinmiyor", k);
  assert.strictEqual(m["Bugünkü fiyat tepkisi"], "bilgi");
});

test("puan: az ölçülen hisse sırf veri az diye öne geçmez", () => {
  const az = K.ozet([[3, "a", "yesil", ""], [3, "b", "yesil", ""], [6, "c", "yesil", ""]]);
  const cok = K.ozet(Array.from({ length: 9 }, (_, i) => [3, "m" + i, i < 8 ? "yesil" : "sari", ""]));
  assert.ok(cok.skor > az.skor, `${cok.skor} > ${az.skor}`);
  const bilgili = K.ozet([[5, "a", "bilgi", ""], [3, "b", "yesil", ""]]);
  assert.strictEqual(bilgili.olculen, 1);                        // bilgi satırı puana katılmaz
  assert.strictEqual(bilgili.baslik[5], "bilinmiyor");
});

test("her hisse için kontrol soruları: özel uyarılar önce, 8 standart soru her zaman", () => {
  const m = [[3, "Satışlar", "kirmizi", ""], [2, "Kârlılık (nakit vekili)", "kirmizi", ""]];
  const q = K.kontrolSorulari(m, false);
  assert.strictEqual(q.filter((x) => !x.ozel).length, 8);
  assert.ok(q[0].ozel && q[1].ozel);
  assert.ok(K.kontrolSorulari([], true)[0].t.includes("tutarsız"));
});

test("AI metni: '-0%' yazmaz, her hisse için bir satır", () => {
  const h = { sembol: "X", ad: "X Inc", sektor: "S", zirveden: -30, mtd: -0.2, metrik: { revG: 0.3 }, kirmiziAd: [] };
  const t = K.aiMetni([h, Object.assign({}, h, { sembol: "Y" })], "2026-01-01");
  assert.ok(!t.includes("−0%"));
  assert.strictEqual(t.split("\n").filter((l) => /^[XY] \|/.test(l)).length, 2);
});

test("görünüm: öncelikli liste daraltır, 'tum' hepsini gösterir", () => {
  const temiz = { kirmizi: 0, olculen: 8 }, azVeri = { kirmizi: 0, olculen: 5 }, birKirmizi = { kirmizi: 1, olculen: 9 };
  assert.ok(K.gorunumdeMi(temiz, "oncelikli") && !K.gorunumdeMi(azVeri, "oncelikli") && !K.gorunumdeMi(birKirmizi, "oncelikli"));
  assert.ok(K.gorunumdeMi(birKirmizi, "bir") && !K.gorunumdeMi(azVeri, "bir"));
  assert.ok([temiz, azVeri, birKirmizi].every((h) => K.gorunumdeMi(h, "tum")));
});

test("gerçek veriyle duman testi", { skip: !fs.existsSync(path.join(__dirname, "..", "data", "sonuclar.json")) }, () => {
  const d = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "data", "sonuclar.json"), "utf8"));
  const r = K.hesapla(d);
  assert.ok(r.adaylar.length > 0);
  const tut = new Set(r.tutarsiz.map((x) => x.sembol));
  assert.ok(r.adaylar.every((h) => !tut.has(h.sembol)));        // tutarsız hisse puanlanmaz
  assert.ok(r.adaylar.every((h) => h.sorular.filter((x) => !x.ozel).length === 8));
  for (let i = 1; i < r.adaylar.length; i++) assert.ok(r.adaylar[i - 1].skor >= r.adaylar[i].skor);
});

// FIRSAT RADARI — gece tarayıcısı (GitHub Actions'ta çalışır)
// Anahtarlar repo Secrets'tan gelir: FINNHUB_KEY, TWELVEDATA_KEY
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";

const FH_KEY = process.env.FINNHUB_KEY;
const TD_KEY = process.env.TWELVEDATA_KEY;
if(!FH_KEY || !TD_KEY){ console.error("FINNHUB_KEY / TWELVEDATA_KEY secrets eksik"); process.exit(1); }

const sleep = ms => new Promise(r=>setTimeout(r,ms));
const iso = d => d.toISOString().slice(0,10);
const FH_GAP = 1050, TD_GAP = 7800;

const EMBEDDED = readFileSync(new URL("./universe-fallback.txt", import.meta.url), "utf8").trim().split(",");
const NDX35 = EMBEDDED.slice(0,35);
const TREE_EXTRA = ["AVAV","AZZ","CCJ","J","KTOS","LEU","NVO","OKLO","PSTG","RXRX","S","SATS","SMR","SYM","TSM","UEC"]; // küratörlü ağacın evren dışı üyeleri — taramaya dahil
const METAL_ETF = ["QTUM","BOTZ","SMH","ICLN","URA","ARKG","XBI","ITA","LIT","KWEB","XLE","XLF","IGV","PAVE","JETS","REMX","SPY","VGK","MCHI","EWJ","EEM","XAU/USD","SLV","PPLT","PALL","CPER"];

// izleme listesi repo'dan (uygulamadaki yerel liste buna ek olarak cihazda taranmaya devam eder)
let WATCH = { other:["RGTI","QBTS","SWK","ZYME","LGIH"], micro:[], spin:["SNDK"] };
try{ WATCH = {...WATCH, ...JSON.parse(readFileSync("watchlist.json","utf8"))}; }catch(e){}

// önceki çıktı (artımlı profil çekimi için)
let prev = {prof:{}, series:{}, dead:{}};
try{ prev = JSON.parse(readFileSync("data/sonuclar.json","utf8")); }catch(e){}

async function fh(path){
  const r = await fetch("https://finnhub.io/api/v1"+path+(path.includes("?")?"&":"?")+"token="+FH_KEY);
  if(r.status===429){ await sleep(20000); return fh(path); }
  if(r.status===401) throw new Error("Finnhub anahtarı geçersiz");
  return r.json();
}
async function td(path){
  const r = await fetch("https://api.twelvedata.com"+path+(path.includes("?")?"&":"?")+"apikey="+TD_KEY);
  const j = await r.json();
  if(j && j.code===429){ await sleep(62000); return td(path); }
  if(j && j.code===401) throw new Error("TwelveData anahtarı geçersiz");
  return j;
}

async function wikiTickers(page){
  const r = await fetch("https://en.wikipedia.org/w/api.php?action=parse&format=json&prop=wikitext&page="+encodeURIComponent(page),
    {headers:{ "User-Agent":"firsat-radari-scanner/1.0" }});
  const j = await r.json();
  const txt = j?.parse?.wikitext?.["*"] || "";
  const out = new Set();
  for(const m of txt.matchAll(/\{\{\s*(?:NYSE|NASDAQ|Nasdaq|nyse|nasdaq)[^|}]*\|\s*([A-Z]{1,5}(?:\.[A-Z])?)\s*\}\}/g)) out.add(m[1]);
  for(const m of txt.matchAll(/\|\|?\s*([A-Z]{1,5}(?:\.[A-Z])?)\s*(?:\|\||\n)/g)) out.add(m[1]);
  return out;
}

function stage1(x){
  if(!x) return [];
  const out = [];
  if(x.r52w>=20 && x.mtd<=-4 && x.mtd>=-16) out.push("A");
  if(Math.abs(x.r52w)<=12 && x.r13w>0) out.push("B?");
  if(x.r52w>=40 && x.mtd<=-15) out.push("C?");
  if(x.r52w>=30 && x.r13w>0 && x.mtd>=-3) out.push("D");
  if(x.mtd<0 && x.r13w<0 && x.r52w<0) out.push("BIÇAK?");
  if(x.gmT!==null && x.gm5!==null && x.gmT > x.gm5+2) out.push("MARJ");
  // MOONSHOT ön-işareti: marj dönüşü + gmT gerçekten pozitif (sahte EV dönüşünü ele)
  if(x.gmT!==null && x.gm5!==null && (x.gmT-x.gm5)>2 && x.gmT>=10 && (x.netM===null||x.netM>=-25)) out.push("MOONSHOT");
  if(x.r13w>0 && x.pe && x.pe<15 && x.r52w<0) out.push("ERKEN+UCUZ?");
  return out;
}

const out = { app:"firsat-radari", generatedAt:new Date().toISOString(), dead: prev.dead||{},
  vix:null, dynUni:null, screen:{}, prof:prev.prof||{}, quotes:{}, series:prev.series||{}, fin:{}, etf:{}, earnCal:{list:[]} };

// ---- 1) VIX (Node'da CORS derdi yok) ----
try{
  const r = await fetch("https://cdn.cboe.com/api/global/delayed_quotes/quotes/_VIX.json");
  const j = await r.json();
  const v = parseFloat(j?.data?.current_price ?? j?.data?.close ?? NaN);
  if(v>=5 && v<=90) out.vix = {val:v, src:"Cboe"};
}catch(e){}
if(!out.vix){
  try{
    const r = await fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS");
    const lines = (await r.text()).trim().split("\n").reverse();
    for(const ln of lines){
      const m = ln.match(/^(\d{4}-\d{2}-\d{2}),\s*([0-9.]+)\s*$/);
      if(m){ const v=parseFloat(m[2]); if(v>=5&&v<=90){ out.vix={val:v, src:"FRED"}; break; } }
    }
  }catch(e){}
}
out.macro = {};
async function fredLast(id){
  try{
    const r = await fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id="+id);
    const lines = (await r.text()).trim().split("\n").reverse();
    for(const ln of lines){ const m = ln.match(/^\d{4}-\d{2}-\d{2},\s*(-?[0-9.]+)\s*$/); if(m) return parseFloat(m[1]); }
  }catch(e){} return null;
}
out.macro.t10y2y = await fredLast("T10Y2Y");        // faiz eğrisi (negatif = ters)
out.macro.hy = await fredLast("BAMLH0A0HYM2");      // yüksek getirili tahvil spreadi
console.log("VIX:", out.vix, "| makro:", out.macro);

// ---- 2) Evren ----
const merged = new Set(EMBEDDED);
try{ (await wikiTickers("List of S%26P 500 companies")).forEach(t=>merged.add(t)); }catch(e){}
try{ (await wikiTickers("Nasdaq-100")).forEach(t=>merged.add(t)); }catch(e){}
try{ const ru = await wikiTickers("Russell 1000 Index"); if(ru.size>200) ru.forEach(t=>merged.add(t)); }catch(e){}
TREE_EXTRA.forEach(t=>merged.add(t));
const ONE_OK = new Set(["A","C","D","F","J","K","L","O","S","T","V","U"]);
const ETF_BLACKLIST = new Set(["QQQ","SPY","DIA","IWM","VOO","VTI","GLD","SLV"]);
const DEAD = prev.dead || {};
const UNI = [...merged].filter(t=>/^[A-Z]{1,5}(\.[A-Z])?$/.test(t) && (t.length>1 || ONE_OK.has(t)) && !ETF_BLACKLIST.has(t) && (DEAD[t]||0) < 2);
out.dynUni = {list:UNI, date:iso(new Date()), src:"Actions gece taraması"};
console.log("Evren:", UNI.length);

// ---- 3) Ekran taraması (metric) ----
let i=0;
for(const s of UNI){
  try{
    const m = await fh("/stock/metric?symbol="+encodeURIComponent(s)+"&metric=all");
    const M = m?.metric || {};
    out.screen[s] = { date: iso(new Date()),
      mtd:M["monthToDatePriceReturnDaily"] ?? null, r13w:M["13WeekPriceReturnDaily"] ?? null,
      r52w:M["52WeekPriceReturnDaily"] ?? null, hi52:M["52WeekHigh"] ?? null,
      pe:M["peBasicExclExtraTTM"]||M["peNormalizedAnnual"]||null, ps:M["psTTM"] ?? null,
      mcap:M["marketCapitalization"] ?? null, gmT:M["grossMarginTTM"] ?? null, gm5:M["grossMargin5Y"] ?? null,
      roe:M["roeTTM"] ?? null, roic:M["roiTTM"] ?? null, netM:M["netProfitMarginTTM"] ?? null, revG:M["revenueGrowthTTMYoy"] ?? null, avgVol:M["10DayAverageTradingVolume"] ?? null };
    if(out.screen[s].mcap===null && out.screen[s].r52w===null) out.dead = {...(out.dead||DEAD), [s]:(DEAD[s]||0)+1};
    else if(DEAD[s]) { out.dead = out.dead||DEAD; delete out.dead[s]; }
  }catch(e){ if(String(e).includes("geçersiz")) throw e; }
  if(++i % 100 === 0) console.log("metric", i, "/", UNI.length);
  await sleep(FH_GAP);
}

// adaylar
const spin = new Set(WATCH.spin||[]);
const solid = s => spin.has(s) || ((out.screen[s]?.mcap||0)>=2000 && !!out.screen[s]?.pe);
const STRONG = new Set(["A","C?","D","ERKEN+UCUZ?"]);
const qualifies = pats => pats.some(p=>STRONG.has(p)) || pats.filter(p=>p!=="BIÇAK?").length>=2;
const CAND = UNI.filter(s => { const p = stage1(out.screen[s]); return p.length && qualifies(p) && solid(s); });
const DISC = UNI.filter(s => { const x=out.screen[s]; return x && (x.mcap||0)>=300 && (x.mcap||0)<2000 && qualifies(stage1(x)); });
console.log("Core aday:", CAND.length, "| Discovery:", DISC.length);

// ---- 4) Profiller (artımlı: eksik/30 gün eskimiş) ----
const needProf = UNI.filter(s => !out.prof[s] || !out.prof[s].date || (Date.now()-new Date(out.prof[s].date))>30*86400000);
console.log("Profil gereken:", needProf.length);
for(const s of needProf){
  try{ const p = await fh("/stock/profile2?symbol="+encodeURIComponent(s));
    out.prof[s] = {name:p?.name||"", ind:p?.finnhubIndustry||"", date:iso(new Date())};
  }catch(e){ out.prof[s]={name:"",ind:"",date:iso(new Date())}; }
  await sleep(FH_GAP);
}

// ---- 5) Fiyatlar (adaylar + izleme + nabız örneklemi) ----
const QUOTE_SET = [...new Set(["SPY", ...CAND, ...DISC.slice(0,40), ...WATCH.other, ...WATCH.micro, ...NDX35])];
for(const s of QUOTE_SET){
  try{ const q = await fh("/quote?symbol="+s); if(q?.c) out.quotes[s]={price:q.c, chgPct:q.dp}; }catch(e){}
  await sleep(FH_GAP);
}

// ---- 6) 5 yıllık seriler (TD) — adaylar + izleme, 7 gün artımlı ----
// Seri önceliği: izleme listeleri > 5y dogrulamasi gerekenler (B?/C?/BICAK?) > kalanlar
const NEEDS_5Y = new Set(["B?","C?","BIÇAK?"]);
const candNeeds5y = CAND.filter(s => stage1(out.screen[s]).some(p=>NEEDS_5Y.has(p)));
const candRest = CAND.filter(s => !candNeeds5y.includes(s));
const SERIES_SET = [...new Set([...WATCH.other, ...WATCH.micro, ...candNeeds5y, ...DISC.slice(0,25), ...candRest])].slice(0,160);
const needSeries = SERIES_SET.filter(s => !out.series[s] || !out.series[s].dateIso || (Date.now()-new Date(out.series[s].dateIso))>7*86400000);
console.log("Seri gereken:", needSeries.length);
for(const s of needSeries){
  try{
    const j = await td("/time_series?symbol="+encodeURIComponent(s)+"&interval=1month&outputsize=61");
    if(j?.values) out.series[s] = {closes:j.values.map(v=>parseFloat(v.close)), dateIso:iso(new Date())};
  }catch(e){}
  await sleep(TD_GAP);
}
// izleme dışı bayat serileri temizle (dosya şişmesin)
for(const k of Object.keys(out.series)) if(!SERIES_SET.includes(k)) delete out.series[k];

// ---- 7) Derin veri (insider/haber/eps) — adaylar + izleme ----
const CONF_WORDS = ["contract","awarded","award","agreement","signs","signed","partnership","order from","supply deal","procure","government","pentagon","defense","nasa","chips act","subsidy","acquisition of","acquires","stake in"];
const RUMOR_WORDS = ["talks","rumor","rumour","in discussions","reportedly","considering","exploring","potential deal","sources say"];
const SCANDAL_WORDS = ["fraud","investigation","sec probe","accounting","short report","short seller","subpoena","lawsuit alleging","restatement"];
const CATALYST_WORDS = ["new ceo","ceo appoint","spin-off","spinoff","cost cutting","restructuring","new product","launches","fda approval","fda clear","ai ","artificial intelligence","datacenter","data center","hyperscaler","capacity expansion","factory","fab ","expands production","record backlog","guidance raise","raises guidance"];
const deepNews = new Set([...WATCH.other, ...WATCH.micro]);
const FIN_SET = [...new Set([...CAND, ...DISC.slice(0,25), ...WATCH.other, ...WATCH.micro])];
const from30 = iso(new Date(Date.now()-30*86400000)), from90 = iso(new Date(Date.now()-90*86400000));
for(const s of FIN_SET){
  const rec = {date:iso(new Date()), news:[], scandal:false, epsSurprise:null, catN:0};
  const x = out.screen[s]||{};
  rec.high52=x.hi52; rec.pe=x.pe; rec.ps=x.ps; rec.mcap=x.mcap; rec.gmT=x.gmT; rec.gm5=x.gm5;
  rec.roe=x.roe; rec.roic=x.roic; rec.netM=x.netM; rec.revG=x.revG; rec.avgVol=x.avgVol;
  rec.name=(out.prof[s]||{}).name||""; rec.industry=((out.prof[s]||{}).ind||"").toLowerCase();
  try{
    const ins = await fh("/stock/insider-transactions?symbol="+s+"&from="+from30);
    const buyers = new Set();
    for(const t of (ins?.data||[])) if(t.transactionCode==="P" && (t.change||0)>0) buyers.add((t.name||"").toUpperCase());
    rec.insBuyers = buyers.size;
  }catch(e){ rec.insBuyers=0; }
  await sleep(FH_GAP);
  try{
    const er = await fh("/stock/earnings?symbol="+s+"&limit=1");
    if(er?.[0]?.estimate) rec.epsSurprise = 100*(er[0].actual-er[0].estimate)/Math.abs(er[0].estimate);
  }catch(e){}
  await sleep(FH_GAP);
  try{
    const rc = await fh("/stock/recommendation?symbol="+s);
    if(Array.isArray(rc) && rc[0]){
      const f = r => (r.strongBuy+r.buy)/Math.max(1, r.strongBuy+r.buy+r.hold+(r.sell||0)+(r.strongSell||0));
      rec.buyNow = f(rc[0]); rec.buyPrev = rc[2] ? f(rc[2]) : (rc[1] ? f(rc[1]) : null);
    }
  }catch(e){}
  await sleep(FH_GAP);
  if(deepNews.has(s)){
    try{
      const n = await fh("/company-news?symbol="+s+"&from="+from90+"&to="+iso(new Date()));
      for(const a of (n||[])){
        const h = (a.headline||"").toLowerCase(); if(!h) continue;
        if(SCANDAL_WORDS.some(w=>h.includes(w))) rec.scandal = true;
        if(CATALYST_WORDS.some(w=>h.includes(w))) rec.catN++;
        const conf = CONF_WORDS.some(w=>h.includes(w)), rum = RUMOR_WORDS.some(w=>h.includes(w));
        if((conf||rum) && rec.news.length<4)
          rec.news.push({h:a.headline.slice(0,105), dt:new Date(a.datetime*1000).toLocaleDateString("tr-TR"), type:conf?"conf":"rumor"});
      }
    }catch(e){}
    await sleep(FH_GAP);
  }
  out.fin[s]=rec;
}

// ---- 8) ETF + metaller (TD) ----
for(const s of METAL_ETF){
  try{
    const j = await td("/time_series?symbol="+encodeURIComponent(s)+"&interval=1month&outputsize=61");
    if(j?.values){
      const c = j.values.map(v=>parseFloat(v.close));
      const at = n=>c[Math.min(n,c.length-1)];
      out.etf[s] = {r3m:c[0]/at(3)-1, r12m:c[0]/at(12)-1, date:iso(new Date()), closes:c};
    }
  }catch(e){}
  await sleep(TD_GAP);
}

// ---- 9) Bilanço takvimi ----
try{
  const to = iso(new Date(Date.now()+45*86400000));
  const j = await fh("/calendar/earnings?from="+iso(new Date())+"&to="+to);
  const mine = new Set([...CAND, ...WATCH.other, ...WATCH.micro]);
  out.earnCal = {date:iso(new Date()), list:(j?.earningsCalendar||[]).filter(e=>mine.has(e.symbol)).map(e=>({s:e.symbol,d:e.date}))};
}catch(e){}

// ---- 10) Sıralama geçmişi (GitHub'da kalıcı) ----
// Basit günlük sıralama: adaylar 13 haftalık getiriye göre — uygulamadaki yıldız
// sıralamasının kaba bir vekili. Amaç: cihaz değişse de "dün neredeydi" bilgisi kalsın.
out.rankHist = prev.rankHist || {};
{
  const ordered = [...CAND].sort((a,b)=>((out.screen[b]||{}).r13w||0)-((out.screen[a]||{}).r13w||0)).slice(0,30);
  const d = iso(new Date());
  out.rankHist[d] = ordered;
  const keys = Object.keys(out.rankHist).sort(); while(keys.length>60){ delete out.rankHist[keys.shift()]; }
}

// ---- 11) MOONSHOT gece özeti (marj dönüşü profili — istemci detay hesabı yapar) ----
// Kademe: r52w>=120 → geç, r52w<40 → kurulum, arası → izle. Gate: gmT-gm5>2 & gmT>=10 & netM>=-25.
out.moonHist = prev.moonHist || {};
{
  const cand = [];
  for(const s of UNI){
    const x = out.screen[s]; if(!x) continue;
    const gmT=x.gmT, gm5=x.gm5, netM=x.netM;
    if(gmT==null||gm5==null) continue;
    const dl = gmT-gm5;
    if(dl<=2 || gmT<10 || (netM!=null && netM<-25)) continue;
    // Kademe app.js moonshot() ile birebir aynı: fitil = tetik var; kurulum = sadece dönüş; geç = uçmuş
    const f = out.fin[s] || {};
    const revG = x.revG, revStrong = (revG!=null && revG>15);
    const insBuy = (f.insBuyers||0) >= 1;
    const eps = (f.epsSurprise!=null && f.epsSurprise >= 8);
    const ser = out.series[s];
    let r3m = null;
    if(ser && ser.closes && ser.closes.length>=4){ const c=ser.closes; r3m = c[0]/c[Math.min(3,c.length-1)]-1; }
    else if(x.r13w!=null){ r3m = x.r13w/100; }
    const turning = (r3m!=null && r3m>0);
    const hi = (x.r52w!=null && x.r52w>=120);
    const dip = (x.r52w!=null && x.r52w<40);
    // Kural 3 — güçlü temel + tetik (app.js ile birebir): zayıf marj+gelir tek EPS ile fitile giremez
    const gucluTemel = (revG!=null && revG>=30) || (dl>=5);
    const tetik = insBuy || eps || (turning && revStrong);
    const gucluTetik = gucluTemel && tetik;
    let tier;
    if(hi) tier = "gec";
    else if(gucluTetik && (turning || !dip)) tier = "fitil";
    else tier = "kurulum";
    cand.push({s, dl:+dl.toFixed(1), r52w:x.r52w, revG:x.revG, insBuy, eps, tier});
  }
  cand.sort((a,b)=>b.dl-a.dl);
  // Kural 4 — aynı şirketin sınıflarını (GOOG/GOOGL, FWONA/FWONK) tekilleştir
  {
    const seenName = new Set(), dedup = [];
    for(const c of cand){
      const nm = ((out.prof[c.s]||{}).name || (out.fin[c.s]||{}).name || "").trim();
      if(nm && seenName.has(nm)) continue;
      if(nm) seenName.add(nm);
      dedup.push(c);
    }
    cand.length = 0; cand.push(...dedup);
  }
  const d = iso(new Date());
  out.moonHist[d] = cand.slice(0,60);
  const mk = Object.keys(out.moonHist).sort(); while(mk.length>30){ delete out.moonHist[mk.shift()]; }
  console.log("Moonshot adayı:", cand.length, "(fitil/kurulum/geç:",
    cand.filter(c=>c.tier==="fitil").length, "/", cand.filter(c=>c.tier==="kurulum").length, "/", cand.filter(c=>c.tier==="gec").length, ")");
}

mkdirSync("data", {recursive:true});
writeFileSync("data/sonuclar.json", JSON.stringify(out));
console.log("Yazıldı: data/sonuclar.json | boyut:", (JSON.stringify(out).length/1024).toFixed(0), "KB");

// ==================== TELEGRAM ÖZET (opsiyonel) ====================
// GitHub Secrets: TELEGRAM_TOKEN + TELEGRAM_CHAT_ID varsa gönderir; yoksa atlar.
await sendTelegram(out).catch(e=>console.log("Telegram atlandı:", e.message));

async function sendTelegram(out){
  const TOKEN = process.env.TELEGRAM_TOKEN, CHAT = process.env.TELEGRAM_CHAT_ID;
  if(!TOKEN || !CHAT){ console.log("Telegram secret yok — mesaj gönderilmedi."); return; }
  const px = s => { const q=(out.quotes||{})[s]; return q?("$"+q.price.toFixed(2)):"-"; };
  const nm = s => (((out.prof||{})[s]||{}).name || ((out.fin||{})[s]||{}).name || "").slice(0,24);
  const esc = t => String(t).replace(/[<>&]/g, c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]));
  const L = [];
  const today = iso(new Date());
  L.push("<b>🎯 FIRSAT RADARI</b> — " + today);

  // ⚡ ŞOK: bugün sert düşenler (skordan bağımsız — en üstte)
  {
    const shocked = [];
    const evren = new Set([...Object.keys(out.screen||{}), ...Object.keys(out.quotes||{})]);
    for(const sym of evren){
      const q = (out.quotes||{})[sym], x = (out.screen||{})[sym] || {}, f = (out.fin||{})[sym] || {};
      const mcap = (f.mcap ?? x.mcap) || 0;
      const gun = (q && typeof q.chgPct==="number") ? q.chgPct : null;
      const ay  = (typeof x.mtd==="number") ? x.mtd : null;
      let chg=null, tip=null, siddet=0;
      if(gun!==null && gun<=-8){ chg=gun; tip="gun"; siddet=100+Math.abs(gun); }
      else if(ay!==null && ay<=-12){ chg=ay; tip="ay"; siddet=Math.abs(ay); }
      else continue;
      const dev = mcap>=50000;
      if(dev) siddet+=30;
      if(mcap>0 && mcap<2000) siddet-=25;
      shocked.push({sym, chg, tip, mcap, siddet});
    }
    shocked.sort((a,b)=>b.siddet-a.siddet);
    if(shocked.length){
      L.push("\n<b>■ ⚡ ŞOK — Sert Düşenler (gün/ay)</b>");
      for(const {sym, chg, tip, mcap} of shocked.slice(0,10)){
        const dev = mcap>=50000 ? " <b>[DEV]</b>" : "";
        const ico = tip==="gun" ? "⚡ gün" : "📉 ay";
        L.push("• <b>"+esc(sym)+"</b> "+px(sym)+"  "+ico+" %"+chg.toFixed(1)+dev+"  <i>"+esc(nm(sym))+"</i>");
      }
      L.push("<i>Sebebini oku — bilanço uyarısı/dava/kılavuz kesintisi olabilir.</i>");
    }
  }

  // ÖZET: rankHist bugünkü ilk sıralar (scanner zaten conviction sıralı ordered üretiyor)
  const ordered = (out.rankHist||{})[today] || [];
  if(ordered.length){
    L.push("\n<b>■ ÖZET (ilk 10)</b>");
    for(const s of ordered.slice(0,10)) L.push("• <b>"+esc(s)+"</b> "+px(s)+"  <i>"+esc(nm(s))+"</i>");
  }

  // 🚀 x5 MOONSHOT: moonHist bugünkü, kademeli
  const mh = (out.moonHist||{})[today] || [];
  if(mh.length){
    const grp = {kurulum:[], izle:[], gec:[]};
    for(const c of mh){ (grp[c.tier]||grp.izle).push(c); }
    const lbl = {kurulum:"🌱 Kurulum (izle)", izle:"🔥 Fitil (doğrula)", gec:"⚠️ Geç (kovalama)"};
    L.push("\n<b>■ 🚀 x5 MOONSHOT</b>");
    for(const key of ["izle","kurulum","gec"]){
      const arr = grp[key]; if(!arr || !arr.length) continue;
      L.push("<u>"+lbl[key]+"</u>");
      for(const c of arr.slice(0,8)){
        const bits = ["marj +"+c.dl];
        if(c.revG!=null && c.revG>15) bits.push("gelir +%"+Math.round(c.revG));
        if(c.r52w!=null) bits.push("1y "+Math.round(c.r52w)+"%");
        L.push("• <b>"+esc(c.s)+"</b> "+px(c.s)+" — "+bits.join(" · "));
      }
    }
  }

  L.push("\n<i>AL listesi değil — katalizörü kendin doğrula.</i>");
  const text = L.join("\n");

  // Telegram mesaj limiti ~4096; parçala
  const chunks = [];
  let buf = "";
  for(const line of text.split("\n")){
    if((buf+line+"\n").length > 3800){ chunks.push(buf); buf=""; }
    buf += line + "\n";
  }
  if(buf) chunks.push(buf);

  for(const chunk of chunks){
    const r = await fetch("https://api.telegram.org/bot"+TOKEN+"/sendMessage", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ chat_id: CHAT, text: chunk, parse_mode:"HTML", disable_web_page_preview:true })
    });
    if(!r.ok){ const t = await r.text(); throw new Error("HTTP "+r.status+" "+t.slice(0,120)); }
    await new Promise(res=>setTimeout(res, 400)); // flood koruması
  }
  console.log("Telegram gönderildi:", chunks.length, "mesaj.");
}

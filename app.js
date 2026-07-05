"use strict";
// ================= FIRSAT RADARI v4 =================
const NDX = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","AVGO","TSLA","COST","NFLX","AMD","PEP","ADBE","CSCO","QCOM","TMUS","INTU","AMAT","TXN","CMCSA","ISRG","HON","BKNG","AMGN","VRTX","ADP","SBUX","PANW","GILD","MU","ADI","INTC","LRCX","MDLZ","REGN","KLAC","SNPS","CDNS","PDD","MELI","CTAS","CSX","MAR","ORLY","CRWD","ABNB","FTNT","NXPI","PCAR","ROP","WDAY","DASH","ADSK","CPRT","PAYX","ROST","MNST","CHTR","AEP","ODFL","KDP","FAST","DDOG","EA","GEHC","EXC","VRSK","CCEP","XEL","CTSH","KHC","IDXX","TTWO","FANG","ON","ZS","DXCM","TEAM","CSGP","BKR","WBD","GFS","MDB","MRVL","BIIB","ARM","LULU","AXON","CDW","TTD","PLTR","APP","MSTR","LIN","ASML","AZN","SMCI","ILMN","ANSS"];
const UNIVERSE = "A,AAPL,ABBV,ABNB,ABT,ACN,ADBE,ADI,ADM,ADP,ADSK,AEE,AEP,AES,AFL,AIG,AIZ,AJG,AKAM,ALB,ALGN,ALL,ALLE,AMAT,AMCR,AMD,AME,AMGN,AMP,AMT,AMZN,ANET,ANSS,AON,AOS,APA,APD,APH,APTV,ARE,ATO,AVB,AVGO,AVY,AWK,AXON,AXP,AZO,BA,BAC,BALL,BAX,BBY,BDX,BEN,BG,BIIB,BK,BKNG,BKR,BLDR,BLK,BMY,BR,BRK.B,BRO,BSX,BX,BXP,C,CAG,CAH,CARR,CAT,CB,CBOE,CBRE,CCI,CCL,CDNS,CDW,CE,CEG,CF,CFG,CHD,CHRW,CHTR,CI,CINF,CL,CLX,CMCSA,CME,CMG,CMI,CMS,CNC,CNP,COF,COO,COP,COST,CPB,CPRT,CPT,CRL,CRM,CSCO,CSGP,CSX,CTAS,CTSH,CTVA,CVS,CVX,CZR,D,DAL,DD,DE,DECK,DFS,DG,DGX,DHI,DHR,DIS,DLR,DLTR,DOC,DOV,DOW,DPZ,DRI,DTE,DUK,DVA,DVN,DXCM,EA,EBAY,ECL,ED,EFX,EG,EIX,EL,ELV,EMN,EMR,ENPH,EOG,EPAM,EQIX,EQR,EQT,ES,ESS,ETN,ETR,EVRG,EW,EXC,EXPD,EXPE,EXR,F,FANG,FAST,FCX,FDS,FDX,FE,FFIV,FI,FICO,FIS,FITB,FMC,FOX,FOXA,FRT,FSLR,FTNT,FTV,GD,GDDY,GE,GEHC,GEN,GILD,GIS,GL,GLW,GM,GNRC,GOOG,GOOGL,GPC,GPN,GRMN,GS,GWW,HAL,HAS,HBAN,HCA,HD,HES,HIG,HII,HLT,HOLX,HON,HPE,HPQ,HRL,HSIC,HST,HSY,HUBB,HUM,HWM,IBM,ICE,IDXX,IEX,IFF,ILMN,INCY,INTC,INTU,INVH,IP,IPG,IQV,IR,IRM,ISRG,IT,ITW,IVZ,J,JBHT,JCI,JKHY,JNJ,JNPR,JPM,K,KDP,KEY,KEYS,KHC,KIM,KKR,KLAC,KMB,KMI,KMX,KO,KR,KVUE,L,LDOS,LEN,LH,LHX,LIN,LKQ,LLY,LMT,LNT,LOW,LRCX,LULU,LUV,LVS,LW,LYB,LYV,MA,MAA,MAR,MAS,MCD,MCHP,MCK,MCO,MDLZ,MDT,MET,META,MGM,MHK,MKC,MKTX,MLM,MMC,MMM,MNST,MO,MOH,MOS,MPC,MPWR,MRK,MRNA,MS,MSCI,MSFT,MSI,MTB,MTCH,MTD,MU,NCLH,NDAQ,NDSN,NEE,NEM,NFLX,NI,NKE,NOC,NOW,NRG,NSC,NTAP,NTRS,NUE,NVDA,NVR,NWS,NWSA,NXPI,O,ODFL,OKE,OMC,ON,ORCL,ORLY,OTIS,OXY,PANW,PARA,PAYC,PAYX,PCAR,PCG,PEG,PEP,PFE,PFG,PG,PGR,PH,PHM,PKG,PLD,PM,PNC,PNR,PNW,PODD,POOL,PPG,PPL,PRU,PSA,PSX,PTC,PWR,PYPL,QCOM,QRVO,RCL,REG,REGN,RF,RJF,RL,RMD,ROK,ROL,ROP,ROST,RSG,RTX,RVTY,SBAC,SBUX,SCHW,SHW,SJM,SLB,SMCI,SNA,SNPS,SO,SOLV,SPG,SPGI,SRE,STE,STLD,STT,STX,STZ,SWK,SWKS,SYF,SYK,SYY,T,TAP,TDG,TDY,TECH,TEL,TER,TFC,TGT,TJX,TMO,TMUS,TPR,TRGP,TRMB,TROW,TRV,TSCO,TSLA,TSN,TT,TTWO,TXN,TXT,TYL,UAL,UBER,UDR,UHS,ULTA,UNH,UNP,UPS,URI,USB,V,VICI,VLO,VLTO,VMC,VRSK,VRSN,VRTX,VST,VTR,VTRS,VZ,WAB,WAT,WBD,WDC,WEC,WELL,WFC,WM,WMB,WMT,WRB,WST,WTW,WY,WYNN,XEL,XOM,XYL,YUM,ZBH,ZBRA,ZTS,PDD,MELI,CRWD,DASH,WDAY,MDB,MRVL,ARM,TTD,PLTR,APP,MSTR,ASML,AZN,TEAM,ZS,DDOG,GFS,CCEP,CLS,SNDK,IONQ,RGTI,QBTS,COHR,LITE,ONTO,NBIS,CRDO,ALAB,VRT,NVT,MOD,FIX,EME,IESC,STRL,PWP,HIMS,SOFI,HOOD,AFRM,RKLB,ASTS,LUNR,PL,IREN,CIFR,WULF,APLD,NOK,ERIC,BP,SHOP,SE,NET,SNOW,OKTA,TWLO,U,RBLX,PATH,DKNG,PENN,LGIH,TMHC,MTH,KBH,TOL,GRBK,SKY,CVCO,ZYME,EXAS,NTRA,GH,TXG,PACB,QGEN,AXTI,AEHR,CAMT,UCTT,ICHR,FORM,ACLS,COHU,KLIC,PLAB,VECO,AMBA,SITM,POWI,SLAB,CRUS,SYNA,MTSI,WOLF,NVTS,AOSL,DIOD".split(",");
const THEMES = [["QTUM","Quantum"],["BOTZ","Robotik/AI"],["SMH","Yarı iletken"],["ICLN","Temiz enerji"],["URA","Uranyum/Nükleer"],["ARKG","Genomik"],["XBI","Biotech"],["ITA","Savunma"],["LIT","Batarya/Lityum"],["KWEB","Çin internet"],["XLE","Enerji"],["XLF","Finans"],["IGV","Yazılım"],["PAVE","Altyapı"],["JETS","Havacılık"],["REMX","Nadir toprak"]];
const REGIONS = [["SPY","ABD"],["VGK","Avrupa"],["MCHI","Çin"],["EWJ","Japonya"],["EEM","Gelişen P."]];
const METALS = [["XAU/USD","Altın"],["XAG/USD","Gümüş"],["XPT/USD","Platin"],["XPD/USD","Paladyum"],["CPER","Bakır (ETF)"]];
const CONF_WORDS = ["contract","awarded","award","agreement","signs","signed","partnership","order from","supply deal","procure","government","pentagon","defense","nasa","chips act","subsidy","acquisition of","acquires","stake in"];
const RUMOR_WORDS = ["talks","rumor","rumour","in discussions","reportedly","considering","exploring","potential deal","sources say"];
const CATALYST_WORDS = ["new ceo","ceo appoint","spin-off","spinoff","cost cutting","restructuring","new product","launches","fda approval","fda clear","ai ","artificial intelligence","datacenter","data center","hyperscaler","capacity expansion","factory","fab ","expands production","record backlog","guidance raise","raises guidance"];
const SCANDAL_WORDS = ["fraud","investigation","sec probe","accounting","short report","short seller","subpoena","lawsuit alleging","restatement"];
const FIN_INDUSTRIES = ["bank","banking","financial services","insurance","capital markets"];

const LS = k => "fr4_" + k;
const $ = id => document.getElementById(id);
const store = {
  get(k, d){ try{ const v = JSON.parse(localStorage.getItem(LS(k))); return v===null||v===undefined? d : v; }catch(e){ return d; } },
  set(k, v){ localStorage.setItem(LS(k), JSON.stringify(v)); }
};
function today(){ return new Date().toDateString(); }
function iso(d){ return d.toISOString().slice(0,10); }
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }

// -------- state --------
let quotes = store.get("quotes", {});       // sym -> {price, chgPct}
let series = store.get("series", {});       // sym -> {closes:[newest..], date}
let fin = store.get("fin", {});             // sym -> {mcap, pe, ps, high52, low52, insBuyers, industry, news:[], scandal, epsSurprise, date}
let firstSeen = store.get("firstSeen", {}); // sym -> isoDate (değer tuzağı sayacı)
let earnCal = store.get("earnCal", {list:[], date:""});
let screen = store.get("screen", {}); // sym -> {mtd,r13w,r52w,hi52,pe,ps,mcap,date}
let vix = store.get("vix", {val:null, date:"", manual:false});
let running = false;
let curSec = "durum", patTab = "hepsi";

// -------- lists --------
function bigList(){ return store.get("bigList", NDX); }
function otherList(){ return store.get("otherList", ["RGTI","QBTS","SWK","ZYME","LGIH"]); }
function microList(){ return store.get("microList", []); }
function spinList(){ return store.get("spinList", ["SNDK"]); }
function allSyms(){ return [...new Set([...bigList(), ...otherList(), ...microList()])]; }

// -------- API layer --------
async function fh(path){ // finnhub
  const key = store.get("fhKey","");
  const r = await fetch("https://finnhub.io/api/v1"+path+(path.includes("?")?"&":"?")+"token="+key);
  if(r.status===429){ await sleep(20000); return fh(path); }
  if(r.status===401) throw new Error("auth-fh");
  return r.json();
}
async function td(path){ // twelvedata (8/min)
  const key = store.get("tdKey","");
  const r = await fetch("https://api.twelvedata.com"+path+(path.includes("?")?"&":"?")+"apikey="+key);
  const j = await r.json();
  if(j && j.code===429){ await sleep(62000); return td(path); }
  if(j && j.code===401) throw new Error("auth-td");
  return j;
}
const FH_GAP = 1150, TD_GAP = 8000;

// -------- returns & patterns --------
function rets(sym){
  const s = series[sym]; if(!s || !s.closes || s.closes.length<2) return null;
  const c = s.closes, last = c[0];
  const at = n => c[Math.min(n, c.length-1)];
  return {
    r1m: last/at(1)-1, r3m: last/at(3)-1, r12m: last/at(12)-1,
    r60m: c.length>=48 ? last/at(60)-1 : null,
    hi5y: Math.max(...c), off5y: 1 - last/Math.max(...c)
  };
}
function isSolid(sym){
  if(spinList().includes(sym)) return true; // spin-off istisnası
  const f = fin[sym]; if(!f) return null;
  return (f.mcap||0) >= 2000 && !!f.pe; // ≥2 milyar $ + kârlı (F/K var)
}
function patterns(sym){
  const r = rets(sym); if(!r) return {list:[], r};
  const f = fin[sym]||{};
  const out = [];
  if(spinList().includes(sym)){ // SPIN-OFF MODU: 5y verisi anlamsız — A-E kapalı, momentum+insider+anlaşma esas
    out.push(["SPIN-MODU","İlk 18 ay: klasik patternler kapalı; insider + anlaşma + görece güç izlenir","p"]);
    if(r.r3m>0.10) out.push(["SPIN-MOM","3 aylık momentum pozitif","g"]);
    if(f.gmT!==null && f.gm5!==null && f.gmT > f.gm5 + 2) out.push(["MARJ","Brüt marj genişliyor","p"]);
    return {list:out, r};
  }
  if((f.roe||0)>15 && (f.revG||0)>8) out.push(["KALİTE","ROE>15 + gelir büyümesi >%8","g"]);
  if(r.r12m>=0.20 && r.r1m<=-0.05 && r.r1m>=-0.15) out.push(["A","Trend içi düzeltme","g"]);
  if(r.r60m!==null && r.r60m<=-0.50 && Math.abs(r.r12m)<=0.10 && r.r3m>0) out.push(["B","Kaybedenin dönüşü","g"]);
  if(r.r60m!==null && r.r60m>=1.00 && r.r1m<=-0.20) out.push(["C","Şampiyonun kötü günü — olayı incele","a"]);
  if(r.r1m<0 && r.r3m<0 && r.r12m<0 && (r.r60m===null || r.r60m<0)) out.push(["BIÇAK","Düşen bıçak — uzak dur","r"]);
  const offH = f.high52 && quotes[sym] ? 1 - quotes[sym].price/f.high52 : null;
  if(offH!==null && offH<=0.05 && r.r12m>=0.30) out.push(["D","Momentum devamı","g"]);
  if(f.epsSurprise!==null && f.epsSurprise!==undefined && f.epsSurprise>=8) out.push(["E","Bilanço sürprizi — drift adayı","b"]);
  // dip-dönüş & değer tuzağı (dev+düşüş bağlamı)
  if(r.off5y>=0.50 && r.r3m>0) out.push(["DÖNÜŞ","Dip-dönüş adayı","g"]);
  if(r.off5y>=0.40){
    if(!firstSeen[sym]){ firstSeen[sym]=iso(new Date()); store.set("firstSeen", firstSeen); }
    const days = (Date.now()-new Date(firstSeen[sym]).getTime())/86400000;
    if(days>365 && r.r3m<0) out.push(["TUZAK","12+ aydır ucuz + hâlâ düşüyor","a"]);
  }
  if(f.gmT!==null && f.gm5!==null && f.gmT > f.gm5 + 2) out.push(["MARJ","Brüt marj genişliyor — darboğaz/fiyatlama gücü vekili","p"]);
  if(r.r3m>0 && f.pe && f.pe<15 && r.off5y>=0.30) out.push(["ERKEN+UCUZ","Momentum başladı + hâlâ ucuz + zirveden uzak","g"]);
  if(f.ps && f.ps>30 && out.some(p=>["A","D","E","DÖNÜŞ"].includes(p[0]))) out.push(["PAHALI","F/S > 30 — değerleme uyarısı","a"]);
  return {list:out, r};
}

// -------- refresh pipeline --------
function setStatus(t){ $("statusText").textContent = t; }
function setBar(d,t){ $("bar").style.width = Math.min(100, Math.round(100*d/Math.max(1,t)))+"%"; }

async function refreshAll(){
  if(running) return; running = true;
  $("statusCard").style.display = "block";
  try{
    await phaseVix();
    await phaseScreen();
    await phaseQuotes();
    await phaseSeries();
    await phaseFin();
    await phaseEtfMetal();
    await phaseCalendar();
    setStatus("Güncel • " + new Date().toLocaleTimeString("tr-TR",{hour:"2-digit",minute:"2-digit"}));
    renderAll();
  }catch(e){
    if(e.message==="auth-fh") alert("Finnhub anahtarı geçersiz görünüyor.");
    else if(e.message==="auth-td") alert("Twelve Data anahtarı geçersiz görünüyor.");
    setStatus("Hata — Ayarlar'ı kontrol et");
  }finally{ running = false; }
}

async function phaseVix(){
  if(vix.date===today() && vix.val!==null){ return; }
  setStatus("VIX çekiliyor…");
  try{
    const r = await fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS");
    const txt = await r.text();
    const lines = txt.trim().split("\n").reverse();
    for(const ln of lines){
      const v = parseFloat(ln.split(",")[1]);
      if(!isNaN(v)){ vix = {val:v, date:today(), manual:false}; store.set("vix", vix); renderDurum(); return; }
    }
    throw new Error("nodata");
  }catch(e){
    $("vixManual").style.display = "block";
    if(vix.val===null) renderDurum();
  }
}
function manualVix(v){
  const x = parseFloat(v); if(isNaN(x)) return;
  vix = {val:x, date:today(), manual:true}; store.set("vix", vix); renderDurum();
}


function weekOld(d){ return !d || (Date.now()-new Date(d).getTime()) > 7*86400000; }
function solidScreen(s){
  if(spinList().includes(s)) return true;
  const x = screen[s]; if(!x) return false;
  return (x.mcap||0) >= 2000 && !!x.pe;
}
function stage1(s){ // ön eleme pattern adayları
  const x = screen[s]; if(!x) return [];
  const out = [];
  if(x.r52w>=20 && x.mtd<=-4 && x.mtd>=-16) out.push("A");
  if(Math.abs(x.r52w)<=12 && x.r13w>0) out.push("B?");
  if(x.r52w>=40 && x.mtd<=-15) out.push("C?");
  if(x.r52w>=30 && x.r13w>0 && x.mtd>=-3) out.push("D");
  if(x.mtd<0 && x.r13w<0 && x.r52w<0) out.push("BIÇAK?");
  if(x.gmT!==null && x.gm5!==null && x.gmT > x.gm5 + 2) out.push("MARJ");
  if(x.r13w>0 && x.pe && x.pe<15 && x.hi52 && x.r52w<0) out.push("ERKEN+UCUZ?");
  return out;
}
function candidates(){ // Core: ≥2 milyar $ + kârlı
  const c = [];
  for(const s of UNIVERSE){
    const pats = stage1(s);
    if(pats.length && solidScreen(s)) c.push(s);
  }
  return c;
}
function discCandidates(){ // Discovery: 300M–2 milyar $ — sadece Keşif bölmesine akar (çift teyit şartıyla vurgulanır)
  const c = [];
  for(const s of UNIVERSE){
    const x = screen[s]; if(!x) continue;
    if((x.mcap||0)>=300 && (x.mcap||0)<2000 && stage1(s).length) c.push(s);
  }
  return c;
}
async function phaseScreen(){
  const need = UNIVERSE.filter(s => !screen[s] || weekOld(screen[s].date));
  if(!need.length) return;
  setStatus("Evrensel tarama (haftalık, "+need.length+" hisse)… ~"+Math.ceil(need.length*FH_GAP/60000)+" dk");
  let i=0;
  for(const s of need){
    try{
      const m = await fh("/stock/metric?symbol="+encodeURIComponent(s)+"&metric=all");
      if(m && m.metric){
        const M = m.metric;
        screen[s] = { date: iso(new Date()),
          mtd: M["monthToDatePriceReturnDaily"] ?? null,
          r13w: M["13WeekPriceReturnDaily"] ?? null,
          r52w: M["52WeekPriceReturnDaily"] ?? null,
          hi52: M["52WeekHigh"] ?? null, pe: M["peBasicExclExtraTTM"] || M["peNormalizedAnnual"] || null,
          ps: M["psTTM"] ?? null, mcap: M["marketCapitalization"] ?? null,
          gmT: M["grossMarginTTM"] ?? null, gm5: M["grossMargin5Y"] ?? null,
          roe: M["roeTTM"] ?? null, revG: M["revenueGrowthTTMYoy"] ?? null, avgVol: M["10DayAverageTradingVolume"] ?? null };
      } else screen[s] = {date: iso(new Date())};
    }catch(e){ if(e.message==="auth-fh") throw e; }
    i++; setBar(i, need.length);
    if(i%25===0){ store.set("screen", screen); renderAll(); }
    await sleep(FH_GAP);
  }
  store.set("screen", screen); renderAll();
}

function activeSyms(){ return [...new Set([...otherList(), ...microList(), ...candidates(), ...discCandidates().slice(0,25)])]; }
async function phaseQuotes(){
  const syms = [...new Set([...activeSyms(), ...NDX.slice(0,35)])]; // 35 NDX = piyasa nabzı örneklemi
  setStatus("Fiyatlar… (~"+Math.ceil(syms.length*FH_GAP/60000)+" dk)");
  let i=0;
  for(const s of syms){
    try{ const q = await fh("/quote?symbol="+s); if(q && q.c) quotes[s]={price:q.c, chgPct:q.dp}; }catch(e){ if(e.message==="auth-fh") throw e; }
    i++; setBar(i, syms.length);
    if(i%10===0){ store.set("quotes", quotes); renderAll(); }
    await sleep(FH_GAP);
  }
  store.set("quotes", quotes); renderAll();
}

async function phaseSeries(){
  const wanted = activeSyms().slice(0,150); // TD günlük bütçe koruması
  const need = wanted.filter(s => !series[s] || weekOld(series[s].dateIso));
  if(!need.length) return;
  setStatus("Pattern verisi (5 yıl, aylık)… "+need.length+" sembol, ~"+Math.ceil(need.length*TD_GAP/60000)+" dk arka planda");
  let i=0;
  for(const s of need){
    try{
      const j = await td("/time_series?symbol="+encodeURIComponent(s)+"&interval=1month&outputsize=61");
      if(j && j.values) series[s] = {closes: j.values.map(v=>parseFloat(v.close)), date: today(), dateIso: iso(new Date())};
    }catch(e){ if(e.message==="auth-td") throw e; }
    i++; setBar(i, need.length);
    if(i%5===0){ store.set("series", series); renderAll(); }
    await sleep(TD_GAP);
  }
  store.set("series", series); renderAll();
}

async function phaseFin(){
  const deepNews = new Set([...otherList(), ...microList()]);
  const need = activeSyms().filter(s => !fin[s] || fin[s].date!==today());
  if(!need.length) return;
  setStatus("Derin veri (insider, F/K, haber)… ~"+Math.ceil(need.length*4*FH_GAP/60000)+" dk");
  const from30 = iso(new Date(Date.now()-30*86400000));
  const from90 = iso(new Date(Date.now()-90*86400000));
  let i=0, total = need.length*4;
  for(const s of need){
    const rec = {date: today(), news: [], scandal:false, epsSurprise:null};
    try{
      const m = await fh("/stock/metric?symbol="+s+"&metric=all");
      if(m && m.metric){
        rec.high52=m.metric["52WeekHigh"]||null; rec.low52=m.metric["52WeekLow"]||null;
        rec.pe=m.metric["peBasicExclExtraTTM"]||m.metric["peNormalizedAnnual"]||null;
        rec.ps=m.metric["psTTM"]||null;
        rec.gmT=m.metric["grossMarginTTM"]??null; rec.gm5=m.metric["grossMargin5Y"]??null;
        rec.roe=m.metric["roeTTM"]??null; rec.revG=m.metric["revenueGrowthTTMYoy"]??null; rec.avgVol=m.metric["10DayAverageTradingVolume"]??null;
      }
    }catch(e){ if(e.message==="auth-fh") throw e; } i++; setBar(i,total); await sleep(FH_GAP);
    try{
      const p = await fh("/stock/profile2?symbol="+s);
      if(p){ rec.mcap=p.marketCapitalization||null; rec.industry=(p.finnhubIndustry||"").toLowerCase(); }
    }catch(e){} i++; setBar(i,total); await sleep(FH_GAP);
    try{
      const ins = await fh("/stock/insider-transactions?symbol="+s+"&from="+from30);
      const buyers = new Set();
      if(ins && Array.isArray(ins.data)) for(const t of ins.data) if(t.transactionCode==="P" && (t.change||0)>0) buyers.add((t.name||"").toUpperCase());
      rec.insBuyers = buyers.size;
    }catch(e){} i++; setBar(i,total); await sleep(FH_GAP);
    try{
      const er = await fh("/stock/earnings?symbol="+s+"&limit=1");
      if(Array.isArray(er) && er[0] && er[0].estimate) rec.epsSurprise = 100*(er[0].actual-er[0].estimate)/Math.abs(er[0].estimate);
    }catch(e){} i++; setBar(i,total); await sleep(FH_GAP);
    if(deepNews.has(s)){
      try{
        const n = await fh("/company-news?symbol="+s+"&from="+from90+"&to="+iso(new Date()));
        if(Array.isArray(n)){
          for(const a of n){
            const h = (a.headline||"").toLowerCase(); if(!h) continue;
            if(SCANDAL_WORDS.some(w=>h.includes(w))) rec.scandal = true;
            if(CATALYST_WORDS.some(w=>h.includes(w))) rec.catN = (rec.catN||0)+1;
            const conf = CONF_WORDS.some(w=>h.includes(w)), rum = RUMOR_WORDS.some(w=>h.includes(w));
            if((conf||rum) && rec.news.length<4)
              rec.news.push({h:a.headline.slice(0,105), dt:new Date(a.datetime*1000).toLocaleDateString("tr-TR"), type: conf?"conf":"rumor"});
          }
        }
      }catch(e){}
      await sleep(FH_GAP);
    }
    fin[s]=rec;
    if(Object.keys(fin).length%6===0){ store.set("fin", fin); renderAll(); }
  }
  store.set("fin", fin); renderAll();
}

let etf = store.get("etf", {});   // sym -> {r3m, r12m, date}
async function phaseEtfMetal(){
  const all = [...THEMES, ...REGIONS, ...METALS].map(x=>x[0]);
  const need = all.filter(s => !etf[s] || etf[s].date!==today());
  if(!need.length) return;
  setStatus("ETF + metaller… ~"+Math.ceil(need.length*TD_GAP/60000)+" dk");
  let i=0;
  for(const s of need){
    try{
      const j = await td("/time_series?symbol="+encodeURIComponent(s)+"&interval=1month&outputsize=61");
      if(j && j.values){
        const c = j.values.map(v=>parseFloat(v.close));
        const at = n => c[Math.min(n,c.length-1)];
        etf[s] = {r3m:c[0]/at(3)-1, r12m:c[0]/at(12)-1, date:today(), closes:c};
      }
    }catch(e){ if(e.message==="auth-td") throw e; }
    i++; setBar(i, need.length);
    store.set("etf", etf);
    await sleep(TD_GAP);
  }
  renderTrend(); renderMetal();
}

async function phaseCalendar(){
  if(earnCal.date===today()) return;
  setStatus("Bilanço takvimi…");
  try{
    const to = iso(new Date(Date.now()+45*86400000));
    const j = await fh("/calendar/earnings?from="+iso(new Date())+"&to="+to);
    const mine = new Set(allSyms());
    if(j && Array.isArray(j.earningsCalendar)){
      earnCal = {date:today(), list: j.earningsCalendar.filter(e=>mine.has(e.symbol)).map(e=>({s:e.symbol, d:e.date}))};
      store.set("earnCal", earnCal);
    }
  }catch(e){}
  renderCal();
}

// -------- renderers --------
function chipRow(sym){
  const f = fin[sym]||{}, q = quotes[sym], p = patterns(sym);
  const chips = [];
  for(const [code,label,cls] of p.list) chips.push('<span class="chip '+cls+'" title="'+label+'">'+code+'</span>');
  if(f.scandal) chips.push('<span class="chip r">OLAY İNCELE</span>');
  if(f.industry && FIN_INDUSTRIES.some(w=>f.industry.includes(w))) chips.push('<span class="chip a" title="Pattern bilanço krizini göremez">FİNANS</span>');
  if((f.insBuyers||0)>=3) chips.push('<span class="chip g">KÜME ALIM '+f.insBuyers+'</span>');
  else if((f.insBuyers||0)>=1) chips.push('<span class="chip a">insider '+f.insBuyers+'</span>');
  const r = p.r;
  if(r){
    chips.push('<span class="chip">1a '+(100*r.r1m).toFixed(0)+'%</span>');
    chips.push('<span class="chip">1y '+(100*r.r12m).toFixed(0)+'%</span>');
    if(r.r60m!==null) chips.push('<span class="chip">5y '+(100*r.r60m).toFixed(0)+'%</span>');
  }
  if(f.pe) chips.push('<span class="chip'+(f.pe<15?' g':'')+'">F/K '+f.pe.toFixed(1)+'</span>');
  const confN = (f.news||[]).filter(n=>n.type==="conf").length;
  if(confN>=2) chips.push('<span class="chip b">ANLAŞMA AKIŞI '+confN+'</span>');
  if((f.catN||0)>=2) chips.push('<span class="chip p">KATALİZÖR '+f.catN+'</span>');
  const av = f.avgVol ?? (screen[sym]||{}).avgVol;
  if(av!==null && av!==undefined && av < 0.3) chips.push('<span class="chip a">LİKİDİTE DÜŞÜK</span>');
  const e = (earnCal.list||[]).find(x=>x.s===sym);
  if(e){ const days = Math.round((new Date(e.d)-new Date())/86400000);
    if(days>=0 && days<=7) chips.push('<span class="chip a">BİLANÇO '+days+' gün</span>'); }
  return {chips, p, f, q};
}
function stockHtml(sym, opts={}){
  const {chips, p, f, q} = chipRow(sym);
  if(!q) return "";
  if(opts.micro){ // çift teyit vurgusu
    const hasPat = p.list.some(x=>!["BIÇAK","TUZAK","PAHALI"].includes(x[0]));
    const confirm = (f.insBuyers||0)>=1 || (f.news||[]).some(n=>n.type==="conf");
    if(hasPat && confirm) chips.unshift('<span class="chip g">ÇİFT TEYİT ✓</span>');
  }
  const chgCol = q.chgPct<=-3?"var(--green)":q.chgPct<0?"var(--amber)":"var(--dim)";
  let news = "";
  if(opts.news && f.news && f.news.length)
    news = f.news.map(n=>'<div class="news'+(n.type==="rumor"?' rumor':'')+'">'+(n.type==="rumor"?"[DEDİKODU] ":"")+n.h+'… <small>('+n.dt+')</small></div>').join("");
  return '<div class="stock"><div class="l1"><div class="tick">'+sym+'</div><div class="price">$'+q.price.toFixed(2)+'</div>'+
    '<div class="chg" style="color:'+chgCol+'">'+(q.chgPct>=0?"+":"")+(q.chgPct||0).toFixed(1)+'%</div></div>'+
    '<div class="l2">'+chips.join("")+'</div>'+news+'</div>';
}

function renderDurum(){
  if(vix.val!==null){
    $("vixVal").textContent = vix.val.toFixed(1) + (vix.manual?" (elle)":"");
    const b = $("verdictBadge");
    if(vix.val>=40){ b.textContent="FIRSAT: VAR"; b.style.background="#16281F"; b.style.color="var(--green)";
      $("vixNote").textContent="Tarihsel panik bölgesi — endeks için 12 aylık pencere tarihsel olarak güçlü. Plana sadık kal, kademeli al."; }
    else if(vix.val>=28){ b.textContent="FIRSAT: YAKINDA"; b.style.background="#33280F"; b.style.color="var(--amber)";
      $("vixNote").textContent="Gerginlik yükseliyor — nakit hazırla, listeyi tara, henüz panik değil."; }
    else { b.textContent="FIRSAT: YOK"; b.style.background="#1A2233"; b.style.color="var(--dim)";
      $("vixNote").textContent="Sakin piyasa — düzenli aylık alım planına devam, zamanlama arama."; }
  }
  const rows = NDX.slice(0,35).map(s=>quotes[s]).filter(Boolean);
  if(rows.length){
    const avg = rows.reduce((a,q)=>a+(q.chgPct||0),0)/rows.length;
    $("pulseVal").textContent = (avg>=0?"+":"")+avg.toFixed(2)+"%";
    const pb = $("pulseBadge");
    if(avg<=-3){ pb.textContent="PANİK GÜNÜ"; pb.style.background="#16281F"; pb.style.color="var(--green)"; }
    else if(avg<=-1.5){ pb.textContent="SATIŞ BASKISI"; pb.style.background="#33280F"; pb.style.color="var(--amber)"; }
    else { pb.textContent="NORMAL"; pb.style.background="#1A2233"; pb.style.color="var(--dim)"; }
  }
  // özet
  const counts = {};
  for(const s of allSyms()){ const p = patterns(s); for(const [c] of p.list) counts[c]=(counts[c]||0)+1; }
  const nice = Object.entries(counts).map(([k,v])=>k+": "+v).join(" • ");
  const nextE = (earnCal.list||[]).slice(0,3).map(e=>e.s+" "+e.d.slice(5)).join(", ");
  $("summaryBox").innerHTML = (nice?("Pattern sayıları — "+nice+"<br>"):"Pattern verisi henüz yükleniyor.<br>") + (nextE?("Yaklaşan bilanço: "+nextE):"");
}

const PAT_TABS = [["hepsi","Adaylar"],["A","A"],["B","B"],["C","C"],["D","D"],["DÖNÜŞ","Dönüş"],["BIÇAK","Bıçak"],["insider","Insider"]];
function renderBig(){
  $("patTabs").innerHTML = PAT_TABS.map(([id,l])=>'<button class="ghost" style="'+(patTab===id?'border-color:var(--blue);color:var(--text);':'')+'" onclick="patTab=\''+id+'\';renderBig()">'+l+'</button>').join("");
  const descs = {hepsi:"586 hisselik evrenden sağlam-firma filtresini (≥2 milyar $ + kârlı) geçip en az bir pattern yakalayanlar. \"?\" = ön eleme, derin veri doğrulaması sırada.", A:"12ay +%20 VE 1ay −%5/−15.", B:"5y −%50 VE 1y yatay VE 3ay pozitif.", C:"5y +%100 VE 1ay −%20 — olayı incele.", D:"Momentum devamı.", "DÖNÜŞ":"5y zirvesinden −%50+ VE 3ay pozitif.", "BIÇAK":"Her vadede negatif — uzak dur.", insider:"Adaylar içinde son 30 günde alım yapılanlar."};
  $("patDesc").textContent = descs[patTab]||"";
  let syms = candidates();
  const deep = s => series[s] ? patterns(s).list.map(p=>p[0]) : null;
  if(patTab==="insider") syms = syms.filter(s=>(fin[s]||{}).insBuyers>0).sort((a,b)=>(fin[b].insBuyers||0)-(fin[a].insBuyers||0));
  else if(patTab!=="hepsi") syms = syms.filter(s=>{
    const d = deep(s); if(d) return d.includes(patTab);
    return stage1(s).some(x=>x.replace("?","")===patTab);
  });
  syms.sort((a,b)=>((screen[b]||{}).mtd||0)-((screen[a]||{}).mtd||0)).reverse();
  $("bigStockList").innerHTML = syms.length ? syms.slice(0,80).map(s=>scanHtml(s)).join("") :
    '<div class="stock muted" style="padding:14px;">Aday yok — evrensel tarama sürüyor olabilir (ilk tarama ~12 dk).</div>';
}
function scanHtml(s){
  const x = screen[s]||{}, q = quotes[s];
  const deepDone = !!series[s];
  let chips = [];
  if(deepDone){ const {chips:c} = chipRow(s); chips = c; }
  else {
    for(const p of stage1(s)) chips.push('<span class="chip '+(p.startsWith("BIÇAK")?"r":p==="MARJ"?"p":p.includes("?")?"a":"g")+'">'+p+'</span>');
    if(x.mtd!==null) chips.push('<span class="chip">ay '+x.mtd.toFixed(0)+'%</span>');
    if(x.r13w!==null) chips.push('<span class="chip">3a '+x.r13w.toFixed(0)+'%</span>');
    if(x.r52w!==null) chips.push('<span class="chip">1y '+x.r52w.toFixed(0)+'%</span>');
    if(x.pe) chips.push('<span class="chip'+(x.pe<15?' g':'')+'">F/K '+x.pe.toFixed(1)+'</span>');
    chips.push('<span class="chip">ön eleme</span>');
  }
  const inOther = otherList().includes(s);
  const price = q ? "$"+q.price.toFixed(2) : (x.mcap? Math.round(x.mcap/1000)+" mlr$" : "");
  const chg = q ? '<div class="chg" style="color:'+(q.chgPct<0?"var(--amber)":"var(--dim)")+'">'+(q.chgPct>=0?"+":"")+(q.chgPct||0).toFixed(1)+'%</div>' : "";
  return '<div class="stock"><div class="l1"><div class="tick">'+s+'</div><div class="price">'+price+'</div>'+chg+
    (inOther?'':'<button class="ghost" style="padding:4px 9px;font-size:11px;" onclick="addToOther(\''+s+'\')">+ Takip</button>')+
    '</div><div class="l2">'+chips.join("")+'</div></div>';
}
function addToOther(s){
  const l = otherList(); if(!l.includes(s)){ l.push(s); store.set("otherList", l); $("otherList").value=l.join(", "); }
  renderAll();
}
function renderOther(){
  const syms = otherList().filter(s=>quotes[s]);
  $("otherStockList").innerHTML = syms.length ? syms.map(s=>stockHtml(s,{news:true})).join("") :
    '<div class="stock muted" style="padding:14px;">Liste boş veya veri bekleniyor.</div>';
}
function renderMicro(){
  const syms = [...new Set([...microList(), ...discCandidates()])].filter(s=>quotes[s]||screen[s]);
  $("microStockList").innerHTML = syms.length ? syms.map(s=>stockHtml(s,{news:true, micro:true})).join("") :
    '<div class="stock muted" style="padding:14px;">Liste boş — Ayarlar\'dan ekle (örn AEHR, AXT profili).</div>';
}

function renderTrend(){
  const rows = THEMES.map(([s,n])=>({s,n,d:etf[s]})).filter(r=>r.d);
  if(rows.length){
    rows.sort((a,b)=>b.d.r3m-a.d.r3m);
    const spy3 = (etf["SPY"]||{}).r3m ?? null;
    $("themeTable").innerHTML = '<table class="mini">'+rows.map((r,i)=>{
      const col = r.d.r3m>0.08?"var(--green)":r.d.r3m<0?"var(--red)":"var(--text)";
      const rs = spy3!==null ? ' • RS '+(100*(r.d.r3m-spy3)).toFixed(1) : '';
      return '<tr><td>'+(i+1)+'. '+r.n+' <span class="muted">('+r.s+')</span></td><td style="color:'+col+'">3a '+(100*r.d.r3m).toFixed(1)+'%'+rs+'</td></tr>';
    }).join("")+'</table>';
  }
  const reg = REGIONS.map(([s,n])=>({s,n,d:etf[s]})).filter(r=>r.d);
  if(reg.length){
    reg.sort((a,b)=>b.d.r12m-a.d.r12m);
    $("regionTable").innerHTML = '<table class="mini">'+reg.map(r=>{
      const col = r.d.r12m>0.1?"var(--green)":r.d.r12m<0?"var(--red)":"var(--text)";
      return '<tr><td>'+r.n+'</td><td style="color:'+col+'">1y '+(100*r.d.r12m).toFixed(1)+'%</td></tr>';
    }).join("")+'</table>';
  }
}

function renderMetal(){
  const rows = METALS.map(([s,n])=>({s,n,d:etf[s]})).filter(r=>r.d);
  if(!rows.length){ return; }
  $("metalList").innerHTML = rows.map(r=>{
    const c = r.d.closes||[]; let pats = [];
    if(c.length>4){
      const at = n=>c[Math.min(n,c.length-1)];
      const r1=c[0]/at(1)-1, r3=c[0]/at(3)-1, r12=c[0]/at(12)-1, r60=c.length>=48?c[0]/at(60)-1:null;
      if(r12>=0.20 && r1<=-0.05 && r1>=-0.15) pats.push('<span class="chip g">A</span>');
      if(r60!==null && r60>=1.00 && r1<=-0.20) pats.push('<span class="chip a">C</span>');
      if(r1<0&&r3<0&&r12<0&&(r60===null||r60<0)) pats.push('<span class="chip r">BIÇAK</span>');
      const hi = Math.max(...c);
      if(1-c[0]/hi<=0.05 && r12>=0.30) pats.push('<span class="chip g">D</span>');
      pats.push('<span class="chip">1a '+(100*r1).toFixed(0)+'%</span><span class="chip">1y '+(100*r12).toFixed(0)+'%</span>');
      if(r60!==null) pats.push('<span class="chip">5y '+(100*r60).toFixed(0)+'%</span>');
    }
    return '<div class="stock"><div class="l1"><div class="tick" style="min-width:90px;">'+r.n+'</div>'+
      '<div class="chg" style="color:'+(r.d.r3m>=0?"var(--green)":"var(--red)")+'">3a '+(100*r.d.r3m).toFixed(1)+'%</div></div>'+
      '<div class="l2">'+pats.join("")+'</div></div>';
  }).join("");
}

function renderFunds(){
  const funds = store.get("funds", []);
  const dep = store.get("depositRate", null);
  if(dep!==null) $("depositRate").value = dep;
  $("fundList").innerHTML = funds.length ? funds.map((f,i)=>{
    const beat = dep!==null && f.r1y!==null ? f.r1y > dep : null;
    return '<div class="stock"><div class="l1"><div class="tick" style="min-width:0;flex:1;">'+f.name+'</div>'+
      (beat===null?'':'<span class="badge" style="background:'+(beat?'#16281F':'#3a1518')+';color:'+(beat?'var(--green)':'var(--red)')+'">'+(beat?'FAİZİ YENDİ':'YENEMEDİ')+'</span>')+
      '<button class="del" onclick="delFund('+i+')">Sil</button></div>'+
      '<div class="l2"><span class="chip">'+f.cat+'</span><span class="chip">1y %'+f.r1y+'</span><span class="chip">3a %'+f.r3m+'</span></div></div>';
  }).join("") : '<div class="stock muted" style="padding:14px;">Fon eklenmedi. TEFAS\'tan ayda bir güncelle.</div>';
}
function addFund(){
  const name=$("fundName").value.trim(); if(!name) return;
  const funds = store.get("funds", []);
  funds.push({name, r1y:parseFloat($("fund1y").value)||0, r3m:parseFloat($("fund3m").value)||0, cat:$("fundCat").value});
  store.set("funds", funds); $("fundName").value=$("fund1y").value=$("fund3m").value="";
  renderFunds();
}
function delFund(i){ const f=store.get("funds",[]); f.splice(i,1); store.set("funds",f); renderFunds(); }
function saveFunds(){ store.set("depositRate", parseFloat($("depositRate").value)||null); renderFunds(); }

function next13F(){
  const y = new Date().getFullYear();
  const dates = [[1,14],[4,15],[7,14],[10,14],[13,14]].map(([m,d])=>new Date(m>=12?y+1:y, m%12, d));
  return dates.find(d=>d>new Date());
}
function renderCal(){
  const list = (earnCal.list||[]).slice().sort((a,b)=>a.d.localeCompare(b.d));
  const f13 = next13F();
  const f13row = '<div class="stock"><div class="l1"><div class="tick" style="min-width:0;flex:1;">13F sezonu — dataroma.com\'dan büyük yatırımcı alımlarını temalarla kesiştir</div>'+
    '<div class="chg" style="color:var(--purple)">'+f13.toLocaleDateString("tr-TR",{day:"numeric",month:"short"})+'</div></div></div>';
  $("calList").innerHTML = f13row + (list.length ? list.map(e=>{
    const days = Math.round((new Date(e.d)-new Date())/86400000);
    return '<div class="stock"><div class="l1"><div class="tick">'+e.s+'</div><div class="price">'+e.d+'</div>'+
      '<div class="chg" style="color:'+(days<=7?"var(--amber)":"var(--dim)")+'">'+(days<=0?"bugün":days+" gün")+'</div></div></div>';
  }).join("") : '<div class="stock muted" style="padding:14px;">45 gün içinde izleme listende bilanço yok (veya veri bekleniyor).</div>');
}

function renderJournal(){
  const j = store.get("journal", []);
  $("journalList").innerHTML = j.length ? j.map((e,i)=>
    '<div class="stock"><div class="l1"><div class="tick">'+e.sym+'</div><div class="price">'+e.date+'</div>'+
    '<button class="del" onclick="delJournal('+i+')">Sil</button></div>'+
    '<div class="muted" style="margin-top:4px;"><b>Tez:</b> '+e.thesis+'<br><b>Haksız çıkaran:</b> '+e.kill+'</div></div>'
  ).join("") : '<div class="stock muted" style="padding:14px;">Kayıt yok. Pozisyon açmadan önce tezini yaz — 6 ay sonra kendinle yüzleş.</div>';
}
function addJournal(){
  const sym=$("jSym").value.trim().toUpperCase(); if(!sym) return;
  const j = store.get("journal", []);
  j.unshift({sym, thesis:$("jThesis").value.trim(), kill:$("jKill").value.trim(), date:new Date().toLocaleDateString("tr-TR")});
  store.set("journal", j); $("jSym").value=$("jThesis").value=$("jKill").value="";
  renderJournal();
}
function delJournal(i){ const j=store.get("journal",[]); j.splice(i,1); store.set("journal",j); renderJournal(); }


function reasonsFor(s){
  const f = fin[s]||{}, x = screen[s]||{};
  const deep = !!series[s];
  const pros = [], cons = [];
  let conv = 0;
  const W = {A:2,B:2,C:1,D:2,E:3,"DÖNÜŞ":2,"MARJ":2,"KALİTE":2,"ERKEN+UCUZ":2,"SPIN-MOM":1};
  const NAME = {A:"trend içi düzeltme", B:"kaybedenin dönüşü (5y dip + dönüş başladı)",
    C:"olay bazlı sert düşüş — geçiciyse fırsat", D:"momentum devamı (zirveye yakın)",
    E:"bilanço sürprizi drift penceresi", "DÖNÜŞ":"5y zirvesinden −%50+ sonrası 3 ay pozitif",
    "MARJ":"brüt marj genişliyor (fiyatlama gücü)", "ERKEN+UCUZ":"momentum başladı + hâlâ ucuz",
    "KALİTE":"kalite: ROE>15 + gelir büyüyor", "SPIN-MOM":"spin-off momentumu pozitif"};
  const pats = deep ? patterns(s).list : stage1(s).map(p=>[p.replace("?",""), "", ""]);
  for(const [code] of pats){
    if(code==="BIÇAK") return null;
    if(code==="TUZAK"){ cons.push("değer tuzağı: 12+ aydır ucuz, hâlâ düşüyor"); conv -= 4; }
    else if(code==="PAHALI"){ cons.push("F/S > 30 — değerleme yüklü"); conv -= 1; }
    else if(code==="SPIN-MODU"){ pros.push("spin-off modu: klasik patternler kapalı, insider+anlaşma esas"); }
    else if(NAME[code]){ pros.push(NAME[code]); conv += (W[code]||1); }
  }
  if((f.insBuyers||0)>=3){ pros.push("küme insider alımı ("+f.insBuyers+" yönetici)"); conv += 3; }
  else if((f.insBuyers||0)>=1){ pros.push("insider alımı ("+f.insBuyers+")"); conv += 1; }
  const confN = (f.news||[]).filter(n=>n.type==="conf").length;
  if(confN>=2){ pros.push("anlaşma akışı ("+confN+" teyitli/90g)"); conv += 1; }
  if((f.catN||0)>=2){ pros.push("katalizör haber kümesi ("+f.catN+")"); conv += 2; }
  const pe = f.pe||x.pe;
  if(pe && pe<15){ pros.push("F/K "+pe.toFixed(1)); conv += 1; }
  if(f.scandal){ cons.push("skandal/soruşturma — OLAY İNCELE"); conv -= 4; }
  if(f.industry && FIN_INDUSTRIES.some(w=>(f.industry||"").includes(w))){ cons.push("finans — pattern bilanço krizini göremez"); conv -= 1; }
  const av = f.avgVol ?? x.avgVol;
  if(av!==null && av!==undefined && av<0.3){ cons.push("likidite düşük"); conv -= 1; }
  if(!deep){ cons.push("ön eleme — derin doğrulama sırada"); conv -= 1; }
  return {pros, cons, conviction: conv};
}
function tierOf(c){
  if(c>=7) return ["🟢 GÜÇLÜ ADAY","var(--green)"];
  if(c>=4) return ["🟡 İZLENMELİ","var(--amber)"];
  if(c>=2) return ["⚪ ÖN İZLEME","var(--dim)"];
  return ["🔴 RİSK BASKIN","var(--red)"];
}
function renderOzet(){
  const pool = [...new Set([...candidates(), ...otherList(), ...microList()])];
  const rows = [];
  for(const s of pool){
    const r = reasonsFor(s);
    if(r && r.pros.length>=2 && r.conviction>=2) rows.push({s, ...r});
  }
  rows.sort((a,b)=>b.conviction-a.conviction);
  $("ozetList").innerHTML = rows.length ? rows.slice(0,15).map(({s,pros,cons,conviction})=>{
    const q = quotes[s];
    const [tl,tc] = tierOf(conviction);
    return '<div class="stock"><div class="l1"><div class="tick">'+s+'</div>'+
      (q?'<div class="price">$'+q.price.toFixed(2)+'</div>':'')+
      '<span class="badge" style="background:#101724;color:'+tc+'">'+tl+' • '+conviction+'</span>'+
      (otherList().includes(s)?'':'<button class="ghost" style="padding:4px 9px;font-size:11px;" onclick="addToOther(\''+s+'\')">+ Takip</button>')+'</div>'+
      '<div class="muted" style="margin-top:5px;"><span style="color:var(--green);font-weight:700;">Sinyaller:</span> '+pros.join("; ")+'.'+
      (cons.length?'<br><span style="color:var(--amber);font-weight:700;">Dikkat:</span> '+cons.join("; ")+'.':'')+'</div></div>';
  }).join("") : '<div class="stock muted" style="padding:14px;">En az 2 olumlu sinyali birleşen aday yok — tarama sürüyor olabilir.</div>';
}

function renderAll(){ renderOzet(); renderDurum(); renderBig(); renderOther(); renderMicro(); renderTrend(); renderMetal(); renderFunds(); renderCal(); renderJournal(); }

// -------- nav & settings --------
const SECTIONS = [["durum","Durum"],["ozet","Özet"],["trend","Trend"],["buyuk","Tarama"],["diger","Diğer"],["kesif","Keşif"],["metal","Metal"],["fon","Fon"],["takvim","Takvim"],["gunluk","Günlük"]];
function show(sec){
  curSec = sec;
  document.querySelectorAll("section").forEach(s=>s.classList.remove("active"));
  const el = $("sec-"+sec); if(el) el.classList.add("active");
  document.querySelectorAll("nav button").forEach(b=>b.classList.toggle("active", b.dataset.s===sec));
  const t = SECTIONS.find(x=>x[0]===sec);
  $("pageTitle").textContent = sec==="ayar" ? "Ayarlar" : (t?t[1]:"");
}
function saveKeys(){
  const f=$("fhKey").value.trim(), t=$("tdKey").value.trim();
  if(f) store.set("fhKey", f);
  if(t) store.set("tdKey", t);
  if(store.get("fhKey","") && store.get("tdKey","")){ show("durum"); refreshAll(); }
  else alert("İki anahtar da gerekli.");
}
function parseList(v){ return v.split(",").map(s=>s.trim().toUpperCase()).filter(Boolean); }
function saveLists(){
  store.set("bigList", parseList($("bigList").value));
  store.set("otherList", parseList($("otherList").value));
  store.set("microList", parseList($("microList").value));
  store.set("spinList", parseList($("spinList").value));
  alert("Kaydedildi."); renderAll();
}

// -------- init & PWA --------
function init(){
  $("navBar").innerHTML = SECTIONS.map(([id,l])=>'<button data-s="'+id+'" onclick="show(\''+id+'\')">'+l+'</button>').join("");
  $("bigList").value = bigList().join(", ");
  $("otherList").value = otherList().join(", ");
  $("microList").value = microList().join(", ");
  $("spinList").value = spinList().join(", ");
  const haveKeys = store.get("fhKey","") && store.get("tdKey","");
  show(haveKeys ? "durum" : "ayar");
  if(haveKeys){ $("statusCard").style.display="block"; renderAll(); refreshAll(); }
}
if("serviceWorker" in navigator) window.addEventListener("load", ()=>navigator.serviceWorker.register("./sw.js").catch(()=>{}));
window.addEventListener("offline", ()=>setStatus("Çevrimdışı — son veriler gösteriliyor"));
init();

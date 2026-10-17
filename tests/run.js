// Automatski testovi za Čestica ZG: učitava index.html u jsdom (bez mreže) i provjerava pravila, kalkulatore i spremanje.
// Pokretanje: cd tests && npm install && npm test
const fs=require("fs"), path=require("path");
const {JSDOM,VirtualConsole}=require("jsdom");
const ROOT=path.join(__dirname,"..");
let html=fs.readFileSync(path.join(ROOT,"index.html"),"utf8");
const lib=f=>fs.readFileSync(path.join(__dirname,"node_modules",f),"utf8");
html=html.replace(/<script src="[^"]*leaflet[^"]*"><\/script>/,()=>"<script>"+lib("leaflet/dist/leaflet.js")+"</script>")
         .replace(/<script src="[^"]*turf[^"]*"><\/script>/i,()=>"<script>"+lib("@turf/turf/turf.min.js")+"</script>")
         .replace(/<link[^>]+leaflet[^>]*>/,"");

let pass=0, fail=0; const fails=[];
const ok=(c,msg)=>{ if(c){pass++} else {fail++; fails.push(msg)} };
const near=(a,b,eps=0.01)=>Math.abs(a-b)<=eps;
const num=s=>{const m=String(s).replace(/ /g," ").match(/-?[\d.]+(,\d+)?/); return m?parseFloat(m[0].replace(/\./g,"").replace(",",".")):NaN};

function boot(){
  const vc=new VirtualConsole(); const errs=[];
  vc.on("jsdomError",e=>errs.push(String(e.message||e))); vc.on("error",e=>errs.push(String(e)));
  const dom=new JSDOM(html,{runScripts:"dangerously",pretendToBeVisual:true,url:"https://example.org/cestica-zg/",virtualConsole:vc,
    beforeParse(w){ w.fetch=()=>Promise.reject(new Error("bez mreže u testu")); w.print=()=>{}; w.scrollTo=()=>{};
      w.HTMLElement.prototype.scrollIntoView=function(){};
      // jsdom nema canvas: Leaflet crta na lažni kontekst koji prihvaća sve pozive
      const ctx=new Proxy({},{get:(t,k)=>k in t?t[k]:(()=>{}),set:(t,k,v)=>(t[k]=v,true)});
      w.HTMLCanvasElement.prototype.getContext=function(){return ctx};
      w.SVGElement.prototype.createSVGRect=function(){return {}}; }});
  return {w:dom.window, errs};
}
// pravokutna čestica w × d metara
function parcelRect(w,d,props){
  const o=[15.97,45.84], dx=w/(111320*Math.cos(45.84*Math.PI/180)), dy=d/110540;
  const g={type:"Polygon",coordinates:[[[o[0],o[1]],[o[0]+dx,o[1]],[o[0]+dx,o[1]+dy],[o[0],o[1]+dy],[o[0],o[1]]]]};
  return {type:"Feature",geometry:g,properties:{KATASTARSKA_CESTICA:"1/1",KATASTARSKA_OPCINA:"ŠESTINE",GRADSKA_CETVRT:"Podsljeme",...props}};
}
function data(w,parcel,code,extra={}){
  const T=w.turf, area=T.area(parcel.geometry);
  const rows=[{p:{Analitika:"Stambena i mješovita",Namjena:"Stambena",Naziv_plana:"GUP Grada Zagreba"},share:1,geom:parcel.geometry}];
  const up={v:[{properties:{BROJ_UP:code}}]};
  const d={ll:{lat:45.84,lng:15.97},parcel,area,rows,ces:{v:[parcel]},nam:{v:rows},up,upx:{v:[]},gn:{v:[]},checks:w.eval("CHECKS").map(c=>({c,v:[]})),slope:null,zgrade:{v:{area:0,n:0,geoms:[]}},...extra};
  d.envelope=w.eval("buildEnvelope")(parcel,rows,up);
  return d;
}
const $=(w,id)=>w.document.getElementById(id);
const txt=(w,id)=>($(w,id)?$(w,id).textContent.replace(/\s+/g," "):"");
function setv(w,id,v,ev="input"){const e=$(w,id); if(e.type==="checkbox") e.checked=v; else e.value=v; e.dispatchEvent(new w.Event(ev,{bubbles:true}));}

// ---------------- 1. Urbanistička pravila: mala čestica u pravilu 2.2 (GUP čl. 69)
{
  const {w,errs}=boot();
  ok(typeof w.render==="function","aplikacija se učitala (render postoji)");
  // 20 × 22,5 m = 450 m² < 600 m²
  w.eval("render")(data(w,parcelRect(20,22.5),"2.2."));
  const s=w.document.getElementById("sheet").textContent;
  ok(s.includes("potrebna dodatna provjera"),"2.2: čestica 450 m² označena kao 'potrebna dodatna provjera'");
  ok(!/čestica premala/.test(s),"2.2: čestica 450 m² nije označena kao 'čestica premala'");
  ok(s.includes("manjim od 600 m²"),"2.2: prikazana je odredba o česticama manjim od 600 m²");
  // 30 × 25 m = 750 m²
  w.eval("render")(data(w,parcelRect(30,25),"2.2."));
  const s2=w.document.getElementById("sheet").textContent;
  ok(/nova gradnja\)\s*ispunjeno/.test(s2)&&!/manja od propisane/.test(s2),"2.2: čestica 750 m² ispunjava min. površinu");
  ok(errs.length===0,"bez JS grešaka pri renderiranju pravila: "+errs.join(" | "));
}
// pravilo bez posebne odredbe za male čestice ostaje "premala" (provjera da iznimka ne vrijedi posvuda)
{
  const {w}=boot();
  const spr=w.eval("smallParcelRule");
  ok(spr({items:["najmanja površina građevne čestice je 600 m²;","najveća izgrađenost građevne čestice je 30%;"]})===null,"zona bez posebne odredbe: iznimka se ne primjenjuje");
  ok(!!spr({items:["rekonstrukcija i gradnja građevina i interpolacija moguća je i na građevnim česticama manjim od propisanih za novu gradnju, uz uvjet..."]}),"prepoznaje 'manjim od propisanih' (pravila 2.4–2.7)");
  ok(spr({items:["iznimno, čestica manja od 600 m² može se koristiti kao vrt"]})===null,"ne prepoznaje rečenicu bez rekonstrukcije/interpolacije/zamjenske gradnje");
  // sva pravila GUP-a s min. površinom imaju posebnu odredbu: provjeri da je prepoznata u svakom
  const R=w.eval("RULES"), miss=[];
  for(const [c,r] of Object.entries(R)){ const z=w.eval("pickZone")(r,"Stambena i mješovita"); if(z&&w.eval("parseParams")(z.key,"slob").minC&&!spr(z)) miss.push(c); }
  ok(miss.length===0,"posebna odredba prepoznata u svim pravilima GUP-a s min. površinom (nedostaje: "+miss.join(", ")+")");
}

// ---------------- 2. Jedinstveni financijski model
{
  const {w,errs}=boot();
  try{w.localStorage.clear()}catch(e){}
  w.eval("render")(data(w,parcelRect(30,25),"2.2."));
  ok(!!$(w,"bArea")&&!!$(w,"kdVol")&&!!$(w,"costs"),"kalkulatori su prikazani");
  setv(w,"bArea","150"); setv(w,"bFloors","P","change");
  ok(num($(w,"kdVol").value)===450,"obujam za komunalni = 150 m² × 3 m = 450 m³ (dobiveno "+$(w,"kdVol").value+")");
  setv(w,"kdZone","I","change");
  const kd=450*18.35, hep=193*11.04*1.25, pr=106.18;
  ok(near(w.__fin.house.kd,kd),"komunalni doprinos = 450 × 18,35");
  ok(near(w.__fin.house.hep,hep),"HEP = 193 × 11,04 × 1,25");
  ok(near(w.__fin.build.naknade,kd+hep+pr),"naknade = komunalni + HEP + pristojba");
  // ista vrijednost naknada u "Priključci i dozvole" i u "Procjeni cijene gradnje"
  const costTxt=txt(w,"costs"), bTxt=txt(w,"bOut");
  const want=w.eval("fmt")(kd+hep+pr)+" €";
  ok(costTxt.includes("Ukupno naknade")&&costTxt.includes(want),"Priključci i dozvole: ukupno naknade "+want);
  ok(bTxt.includes("Naknade, priključci i pristojbe")&&bTxt.includes(want),"Procjena gradnje koristi isti iznos naknada "+want);
  // promjena kuće mijenja obujam i komunalni u oba modula
  setv(w,"bArea","200");
  ok(num($(w,"kdVol").value)===600,"nakon promjene kuće obujam = 600 m³");
  ok(txt(w,"costs").includes(w.eval("fmt")(600*18.35+hep+pr)+" €")&&txt(w,"bOut").includes(w.eval("fmt")(600*18.35+hep+pr)+" €"),"oba modula prate promjenu kuće");
  // ručni obujam
  setv(w,"kdVol","500");
  setv(w,"bArea","120");
  ok(num($(w,"kdVol").value)===500,"ručno upisan obujam se ne prepisuje");
  $(w,"kdVolAuto").dispatchEvent(new w.Event("click",{bubbles:true}));
  ok(num($(w,"kdVol").value)===360,"gumb 'iz kuće' vraća obujam 120 × 3 = 360");
  // podrum ulazi u obujam
  setv(w,"bBase",true,"change");
  ok(num($(w,"kdVol").value)===720,"s podrumom obujam = (120 + 120) × 3 = 720");
  setv(w,"bBase",false,"change");
  // plin: raspon samo za plin, rezerva odvojena
  setv(w,"kdGas",true,"change");
  const F=w.__fin;
  ok(near(F.build.naknadeHi-F.build.naknadeLo,700),"plin daje raspon 800–1.500 € samo u naknadama");
  const g=F.items.filter(i=>i.group==="gradnja").reduce((s,i)=>s+i.base,0);
  ok(near(F.build.rez,g*0.15),"rezerva = 15 % gradnje, projekata i nadzora");
  ok(near(F.build.base,F.items.reduce((s,i)=>s+i.base,0)),"ukupno = zbroj stavki (bez dvostrukog zbrajanja)");
  ok(!/NaN|undefined/.test(txt(w,"bOut")+txt(w,"costs")),"nema NaN/undefined u ispisu");
  // okoliš
  setv(w,"bYard","8000");
  ok(w.__fin.items.some(i=>i.k==="okolis"&&i.base===8000),"uređenje okoliša ulazi kao korisnički unos");
  ok(errs.length===0,"bez JS grešaka u financijama: "+errs.join(" | "));
}

// ---------------- 3. Kupnja zemljišta
{
  const {w,errs}=boot();
  try{w.localStorage.clear()}catch(e){}
  w.eval("render")(data(w,parcelRect(40,25),"2.2.")); // 1.000 m²
  const A=w.__cur.area;
  setv(w,"yPrice","100000");
  ok(near(num($(w,"yM2").value),Math.round(100000/A),1),"cijena po m² se računa iz cijene");
  let B=w.__fin.buy;
  ok(near(B.rows.find(r=>r.k==="porez").v,3000),"porez na promet 3 % = 3.000 €");
  ok(near(B.rows.find(r=>r.k==="zkpr").v,3.25+26.54),"sudske pristojbe e-uknjižba = 3,25 + 26,54 €");
  setv(w,"yAgency","3");
  B=w.__fin.buy;
  ok(near(B.rows.find(r=>r.k==="agencija").v,3750),"agencija 3 % + PDV = 3.750 €");
  setv(w,"yNotary","150"); setv(w,"yLawyer","600"); setv(w,"yGeo","400");
  B=w.__fin.buy;
  const costs=3000+3750+29.79+150+600+400;
  ok(near(B.costs,costs),"ukupni troškovi kupnje = "+costs);
  ok(near(B.acq,100000+costs),"cijena stjecanja = cijena + troškovi");
  ok(near(B.effM2,(100000+costs)/A),"efektivna cijena po m²");
  ok(B.missing.length===0,"svi troškovi upisani");
  // kapara nije dodatni trošak
  setv(w,"yKapara","10000");
  B=w.__fin.buy;
  ok(near(B.acq,100000+costs)&&near(B.rest,90000),"kapara 10.000 € ne mijenja cijenu stjecanja; ostatak 90.000 €");
  // PDV režim
  setv(w,"yReg","pdv","change");
  B=w.__fin.buy;
  ok(near(B.rows.find(r=>r.k==="porez").v,25000)&&!B.rows.some(r=>/promet/.test(r.label)),"PDV režim: 25 % i bez poreza na promet");
  setv(w,"yVatIncl",true,"change");
  ok(near(w.__fin.buy.rows.find(r=>r.k==="porez").v,0),"PDV uključen u cijenu: nema dodatnog poreza");
  setv(w,"yReg","osl","change");
  ok(near(w.__fin.buy.rows.find(r=>r.k==="porez").v,0),"oslobođeno: porez 0");
  setv(w,"yReg","ppn","change");
  // ukupna investicija = stjecanje + gradnja
  setv(w,"bArea","150"); setv(w,"kdZone","II","change");
  const F=w.__fin;
  ok(near(F.total.base,F.buy.acq+F.build.base),"ukupna investicija = stjecanje + gradnja s naknadama");
  ok(near(F.total.lo,F.buy.acq+F.build.lo)&&near(F.total.hi,F.buy.acq+F.build.hi),"raspon investicije dolazi samo od procjena gradnje");
  ok(txt(w,"totOut").includes(w.eval("fmt")(F.total.lo)),"ukupna investicija prikazana");
  // spremanje po čestici i ponovno učitavanje
  w.eval("render")(data(w,parcelRect(40,25),"2.2."));
  ok(num($(w,"yPrice").value)===100000&&num($(w,"yAgency").value)===3&&num($(w,"yKapara").value)===10000,"unosi kupnje se vraćaju nakon ponovnog prikaza");
  const other=parcelRect(40,25,{KATASTARSKA_CESTICA:"2/2"});
  w.eval("render")(data(w,other,"2.2."));
  ok($(w,"yPrice").value==="","druga čestica ima prazne unose kupnje");
  ok(errs.length===0,"bez JS grešaka u kupnji: "+errs.join(" | "));
}

// ---------------- 4. Kontrolna lista kupnje
{
  const {w,errs}=boot();
  try{w.localStorage.clear()}catch(e){}
  const p=parcelRect(30,25);
  w.eval("render")(data(w,p,"2.2."));
  const items=w.document.querySelectorAll("li[data-ck]");
  ok(items.length===14,"kontrolna lista ima 14 koraka (ima "+items.length+")");
  const li=items[7]; // predugovor
  li.querySelector("[data-ckd]").checked=true; li.querySelector("[data-ckd]").dispatchEvent(new w.Event("change",{bubbles:true}));
  li.querySelector("[data-ckdt]").value="2026-10-20"; li.querySelector("[data-ckdt]").dispatchEvent(new w.Event("change",{bubbles:true}));
  li.querySelector("[data-ckn]").value="kod bilježnika X"; li.querySelector("[data-ckn]").dispatchEvent(new w.Event("input",{bubbles:true}));
  ok(txt(w,"ckSum")==="1/14","sažetak 1/14");
  w.eval("render")(data(w,p,"2.2."));
  const li2=w.document.querySelector('li[data-ck="pred"]');
  ok(li2.querySelector("[data-ckd]").checked&&li2.querySelector("[data-ckdt]").value==="2026-10-20"&&li2.querySelector("[data-ckn]").value==="kod bilježnika X","kvačica, datum i bilješka se spremaju");
  w.eval("render")(data(w,parcelRect(30,25,{KATASTARSKA_CESTICA:"9/9"}),"2.2."));
  ok(!w.document.querySelector('li[data-ck="pred"] [data-ckd]').checked,"druga čestica ima svoju listu");
  const all=w.document.getElementById("sheet").innerHTML;
  ok(/porezna-uprava\.gov\.hr/.test(all)&&/gov\.hr\/hr\/upis-prava-vlasnistva/.test(all),"koraci imaju službene poveznice");
  ok(/15 dana/.test(all)&&/60 dana/.test(all),"prikazani su samo zakonski rokovi (15, 30 i 60 dana)");
  ok(errs.length===0,"bez JS grešaka u kontrolnoj listi: "+errs.join(" | "));
}

// ---------------- 5. Postojeće funkcije i nedostupni servisi
{
  const {w,errs}=boot();
  const d=data(w,parcelRect(30,25),"2.2.");
  d.checks=w.eval("CHECKS").map(c=>({c,e:"bez mreže"}));
  w.eval("render")(d);
  const s=w.document.getElementById("sheet").textContent;
  ok(/Nisu odgovorili/.test(s),"neuspjeli servisi su prijavljeni, a ne prikazani kao 'nema ograničenja'");
  ok(!/Nisu nađena ograničenja/.test(s),"neuspjeh se ne prikazuje kao 'nisu nađena ograničenja'");
  ok(!!$(w,"zkFile")&&!!$(w,"tipSel")&&!!$(w,"saveBtn")&&!!$(w,"printBtn"),"postojeće funkcije (ZK, tip kuće, spremanje, ispis) i dalje postoje");
  ok(errs.length===0,"bez JS grešaka: "+errs.join(" | "));
}

// ---------------- 6. Parametri pravila (A1)
{
  const {w,errs}=boot();
  const RP=(set,code,tip,area)=>{const R=w.eval(set), z=w.eval("pickZone")(R[code],"Stambena i mješovita"); return w.eval("ruleParams")(z,tip,area)};
  const get=(P,id)=>P.find(x=>x.id===id)||{};
  let P=RP("RULES","2.1.","slob",900);
  ok(get(P,"meda").value==="3,0 m","2.1: udaljenost od međe 3,0 m iz stavke za novu gradnju (ne iz stavke o rekonstrukciji)");
  ok(get(P,"etaze").num===2,"2.1: najviše dvije nadzemne etaže");
  ok(get(P,"teren").value==="60 %","2.1: prirodni teren 60 %");
  ok(get(P,"pravac").value==="najmanje 5,0 m"&&get(P,"pravac").status==="provjera","2.1: građevni pravac 5,0 m, označen za dodatnu provjeru");
  ok(get(P,"jed").num===3&&/6 PGM/.test(get(P,"pgm").value),"2.1: 3 jedinice i 2 PGM po stanu = 6 PGM");
  P=RP("RULES","2.7.","slob",800);
  ok(get(P,"jed").num===8,"2.7: najviše 8 jedinica (1 na 80 m², čestica 800 m²)");
  P=RP("RULES","2.7.","slob",400);
  ok(get(P,"jed").num===5,"2.7: na 400 m² najviše 5 jedinica (1 na 80 m²)");
  P=RP("RULES","1.3.","slob",800);
  ok(get(P,"sirina").value==="20,0 m"&&get(P,"sirina").status==="provjera","1.3: najmanja širina uz ulicu 20,0 m, za provjeru");
  P=RP("RULES_PP","PPGZ","polu",400);
  ok(get(P,"teren").value==="30 %"&&get(P,"meda").hHalf,"PPGZ poluugrađena: teren 30 %, međa h/2");
  ok(get(P,"etaze").num===3,"PPGZ: tri nadzemne etaže");
  P=RP("RULES","1.2.","slob",800);
  ok(get(P,"meda").value==null,"1.2: broj iz rečenice o dubini gradnje (75 m) nije uzet kao udaljenost od međe");
  // h/2 u prostoru za kuću je označen kao procjena
  const pr=parcelRect(40,30);
  const d=data(w,pr,"PPGZ"); d.up={v:[]}; d.rows[0].p.Naziv_plana="Prostorni plan Grada Zagreba";
  d.envelope=w.eval("buildEnvelope")(pr,d.rows,d.up);
  ok(d.envelope&&/h\/2/.test(d.envelope.est||""),"PPGZ: prostor za kuću s h/2 označen je kao procjena");
  w.eval("render")(d);
  ok(/Udaljenost od međa je procjena/.test(w.document.getElementById("sheet").textContent),"napomena o procjeni udaljenosti od međa je prikazana");
  // vrsta zahvata
  const {w:w2,errs:e2}=boot();
  w2.eval("ZAHVAT='interp'");
  w2.eval("render")(data(w2,parcelRect(20,22.5),"2.2."));
  const t2=w2.document.getElementById("sheet").textContent;
  ok(/interpolacija: potrebna dodatna provjera/.test(t2)&&/manjim od 600 m²/.test(t2),"interpolacija: prikazane posebne odredbe i status provjere");
  // iznimke: ulica iz OSM-a koja se spominje u iznimci
  const d3=data(w2,parcelRect(30,25),"2.2."); d3.env={v:{roads:[{name:"Karažnik",hw:"residential",ok:true}],stops:[]}};
  w2.eval("render")(d3);
  ok(/iznimku koja spominje ulicu uz ovu česticu \(Karažnik\)/.test(w2.document.getElementById("sheet").textContent),"iznimka za ulicu Karažnik je istaknuta");
  w2.eval("ZAHVAT='nova'");
  ok(errs.length===0&&e2.length===0,"bez JS grešaka u pravilima: "+errs.concat(e2).join(" | "));
}

// ---------------- 7. Mreža: ponovni pokušaj, predmemorija, greške (A3)
async function netTests(){
  const {w}=boot();
  const G=w.eval("getJSON"), NET=w.eval("NET");
  const resp=(status,body)=>Promise.resolve({ok:status<400,status,json:()=>Promise.resolve(body)});
  let n=0;
  w.fetch=()=>{n++; return n===1?resp(503,{}):resp(200,{features:[1]})};
  let r=await G("https://x.test/arcgis/rest/services/A/FeatureServer/0/query?a=1");
  ok(n===2&&r.features.length===1,"privremena greška 503: jedan ponovni pokušaj i uspjeh");
  n=0; w.fetch=()=>{n++; return resp(200,{features:[2]})};
  r=await G("https://x.test/arcgis/rest/services/A/FeatureServer/0/query?a=1");
  ok(n===0&&r.features[0]===1,"isti zahtjev se čita iz predmemorije");
  n=0; w.fetch=()=>{n++; return resp(404,{})};
  try{await G("https://x.test/b"); ok(false,"404 mora baciti grešku")}catch(e){ok(n===1&&/HTTP 404/.test(e.message),"greška 404 se ne ponavlja i jasno je opisana")}
  n=0; w.fetch=()=>{n++; return resp(200,{error:{code:400,message:"Invalid query"}})};
  try{await G("https://x.test/c")}catch(e){ok(n===1&&/servis javlja grešku: Invalid query/.test(e.message),"ArcGIS greška u odgovoru je prepoznata")}
  n=0; w.fetch=(u,o)=>{n++; return new Promise((_,rej)=>o.signal.addEventListener("abort",()=>{const e=new Error("a");e.name="AbortError";rej(e)}))};
  try{await G("https://x.test/d",{},300)}catch(e){ok(n===2&&/nema odgovora nakon 0.3 s/.test(e.message),"isteklo vrijeme: ponovljeno jednom, poruka s trajanjem")}
  // najviše 6 istodobnih zahtjeva
  let act=0,peak=0; w.fetch=()=>{act++;peak=Math.max(peak,act); return new Promise(res=>setTimeout(()=>{act--;res({ok:true,status:200,json:()=>Promise.resolve({})})},30))};
  await Promise.all(Array.from({length:15},(_,i)=>G("https://x.test/e?"+i,{},2000,{cache:false})));
  ok(peak<=6,"najviše 6 istodobnih zahtjeva (vrh "+peak+")");
  ok(NET.stat["x.test"]&&NET.stat["x.test"].fail>0,"stanje servisa bilježi neuspjehe");
  // nepotpun rezultat
  const f=w.eval("featuresOf")({features:[1,2],exceededTransferLimit:true});
  ok(f.incomplete===true,"dosegnuta granica broja objekata označava rezultat kao nepotpun");
}

// ---------------- 8. Infrastruktura (C)
async function infraTests(){
  const {w,errs}=boot();
  const pr=parcelRect(30,25), c=pr.geometry.coordinates[0];
  const off=(m)=>m/110540; // pomak prema sjeveru u stupnjevima
  const line=(m)=>({type:"LineString",coordinates:[[c[0][0]-0.001,c[2][1]+off(m)],[c[1][0]+0.001,c[2][1]+off(m)]]});
  w.fetch=(u,o)=>{
    const ok=b=>Promise.resolve({ok:true,status:200,json:()=>Promise.resolve(b)});
    if(/3c_voda_JR_PJR_swipe\/FeatureServer\/26\/query/.test(u)) return ok({type:"FeatureCollection",features:[{type:"Feature",geometry:line(50),properties:{Layer:"Vodoopskrbni cjevovod - postojeci"}}]});
    if(/GUP_Infrastruktura\/FeatureServer\/14\/query/.test(u)) return ok({type:"FeatureCollection",features:[{type:"Feature",geometry:line(120),properties:{PLINOVOD_OPIS:"Plinovod VT (planirani)"}}]});
    if(/GUP_Infrastruktura\/FeatureServer\/22\/query/.test(u)) return Promise.resolve({ok:false,status:500,json:()=>Promise.resolve({})});
    return ok({type:"FeatureCollection",features:[]});
  };
  const inf=await w.eval("settle")(w.eval("loadInfra")(pr,{lat:45.84,lng:15.97}));
  ok(inf.v&&inf.v.vod.ex&&Math.abs(inf.v.vod.ex.d-50)<2,"magistralni vodovod iz GUP-a na oko 50 m");
  ok(inf.v.plin.pl&&!inf.v.plin.ex&&Math.abs(inf.v.plin.pl.d-120)<3,"planirani VT plinovod na oko 120 m, prepoznat kao planirani");
  ok(inf.v.top.e,"neuspjeh servisa za toplovod je zabilježen kao greška");
  const html=w.eval("infraHtml")(inf), t=html.replace(/<[^>]+>/g," ");
  ok(/Vodovod\s+nema dostupnih podataka/.test(t)&&/Kanalizacija\s+nema dostupnih podataka/.test(t),"vodovod i kanalizacija: 'nema dostupnih podataka', a ne 'nema infrastrukture'");
  ok(/magistralni vodoopskrbni cjevovod \(postojeći\) oko 50 m/.test(t)&&/ne priključuje izravno/.test(t),"blizina magistralnog voda je navedena uz napomenu da priključak nije izravan");
  ok(/Plinovod VT \(planirani\) oko 1[12][0-9] m/.test(t),"planirani plinovod prikazan kao planirani");
  ok(!/Toplovod/.test(t),"za toplovod s greškom nema tvrdnje o (ne)postojanju");
  ok(/U GUP-u nema dalekovoda, kabela ni trafostanica 110 kV u krugu 300 m/.test(t),"za struju bez vodova u krugu jasno piše da ih nema u podacima GUP-a");
  // korisnički unos troška priključaka ulazi u model jednom
  w.eval("render")(data(w,pr,"2.2."));
  const set=(id,v)=>{const e=w.document.getElementById(id); e.value=v; e.dispatchEvent(new w.Event("input",{bubbles:true}));};
  set("bArea","150"); w.document.getElementById("kdZone").value="I"; w.document.getElementById("kdZone").dispatchEvent(new w.Event("change",{bubbles:true}));
  const before=w.__fin.build.naknade;
  set("kdWorks","4000"); set("kdSeptic","5000");
  ok(Math.abs(w.__fin.build.naknade-before-9000)<0.01,"radovi na priključcima i sabirna jama ulaze u naknade i priključke jednom");
  w.eval("render")(data(w,pr,"2.2."));
  ok(w.document.getElementById("kdWorks").value==="4000","unos radova na priključcima se sprema po čestici");
  ok(errs.length===0,"bez JS grešaka u infrastrukturi: "+errs.join(" | "));
}

// ---------------- 9. Simulator kuće (D1)
{
  const {w,errs}=boot();
  const pr=parcelRect(30,25), c=pr.geometry.coordinates[0];
  const d=data(w,pr,"2.2.");
  // ulica uz južni rub čestice, 4 m južnije
  const y=c[0][1]-4/110540; d.env={v:{roads:[{name:"Test",hw:"residential",ok:true}],roadLines:[{ok:true,geom:[[c[0][0]-0.001,y],[c[1][0]+0.001,y]]}],stops:[]}};
  w.__env=d.envelope; w.eval("OPEN").add("tloc"); w.eval("render")(d);
  const TL=w.eval("TL"), tDraw=w.eval("tDraw");
  tDraw(); let R=w.__sim;
  ok(R&&R.inEnv,"kuća 12 × 9 m u sredini je unutar udaljenosti od međa");
  const row=l=>R.C.find(x=>x.label.startsWith(l))||{};
  const tlx=w.eval("fmt")(Math.round(d.area*0.3)); ok(row("Tlocrt").st==="ok"&&row("Tlocrt").val.startsWith("108 od najviše "+tlx),"tlocrt 108 m² od dopuštenih "+tlx+" m² (30 % površine)");
  ok(row("GBP").st==="ok"&&/108 od najviše 400/.test(row("GBP").val),"GBP prizemnice 108 m², granica 400 m²");
  ok(row("Prirodni teren").st==="warn","prirodni teren: zadovoljen samo ako ostatak nije popločen (potrebna provjera)");
  ok(TL.zones&&TL.zones.orange&&row("Građevni pravac").st==="ok","prepoznata ulica uz južni rub; kuća u sredini je izvan pojasa građevnog pravca");
  // pomak prema ulici
  const c0=TL.center.slice(); TL.center=[c0[0],c[0][1]+8/110540]; tDraw(); R=w.__sim;
  ok(row("Građevni pravac").st==="warn","kuća u pojasu uz ulicu: potrebna provjera (narančasto)");
  TL.center=c0;
  // prevelika kuća
  TL.w=28; tDraw(); R=w.__sim;
  ok(!R.inEnv&&R.st==="no","kuća šira od prostora za gradnju je crvena (ne zadovoljava)");
  TL.w=20; TL.d=15; tDraw(); R=w.__sim;
  ok(row("Tlocrt").st==="no","tlocrt 300 m² prelazi dopušteni tlocrt");
  // etaže i potkrovlje
  TL.w=12; TL.d=9; TL.fl="2.5"; tDraw(); R=w.__sim;
  ok(Math.abs(R.gbpN-(108*2+108*0.75))<0.01&&row("Nadzemne etaže").st==="ok","P+1+Pk: GBP = 2 × 108 + 75 % × 108, tri etaže dopuštene");
  TL.fl="3"; TL.w=14; TL.d=11; tDraw(); R=w.__sim;
  ok(row("GBP").st==="no","P+2 s 154 m² tlocrta: GBP 462 m² prelazi 400 m²");
  // garaža
  TL.fl="1"; TL.w=12; TL.d=9; TL.gar=true; TL.gw=3.5; TL.gd=6; tDraw(); R=w.__sim;
  ok(Math.abs(R.tl-(108+21))<0.01,"garaža 3,5 × 6 m ulazi u tlocrt");
  // prijenos u financije
  TL.gar=false; TL.fl="1.5"; tDraw();
  w.document.getElementById("tToFin").dispatchEvent(new w.Event("click",{bubbles:true}));
  ok(+w.document.getElementById("bArea").value===Math.round(108*1.75)&&w.document.getElementById("bFloors").value==="PPk","simulator prenosi GBP i katnost u procjenu troškova");
  ok(Math.abs(w.__fin.house.foot-108)<0.6,"procjena troškova računa isti tlocrt kao simulator (108 m²)");
  // udaljenosti od granice i pomak upisom
  TL.fl="1"; TL.w=12; TL.d=9; TL.rot=0; TL.center=null; tDraw();
  const S=w.eval("sideDists")();
  ok(S&&Math.abs(S[1].dist+S[3].dist+12-30)<0.3&&Math.abs(S[0].dist+S[2].dist+9-25)<0.3,"udaljenosti stranica do granice se zbrajaju na širinu i dubinu čestice");
  w.eval("tMoveSide")(3,4); const S2=w.eval("sideDists")();
  ok(Math.abs(S2[3].dist-4)<0.2,"upis 4 m lijevo pomakne kuću na 4 m od lijeve granice");
  // koraci + i −
  const bw=w.document.querySelector('[data-step="tW"][data-d="0.5"]'); bw.dispatchEvent(new w.Event("click",{bubbles:true}));
  ok(TL.w===12.5,"gumb + povećava širinu za 0,5 m");
  const br=w.document.querySelector('[data-step="tRot"][data-d="-5"]'); br.dispatchEvent(new w.Event("click",{bubbles:true}));
  ok(TL.rot===355,"gumb − okreće za 5° (preko 0° na 355°)");
  ok(!!TL.rotM,"na karti postoji ručka za okretanje");
  ok(errs.length===0,"bez JS grešaka u simulatoru: "+errs.join(" | "));
}

// ---------------- 10. Sunce, elektrana, potres (D2–D4)
async function sunTests(){
  const {w,errs}=boot();
  const sp=w.eval("solarPos"), zd=w.eval("zgDate"), st=w.eval("sunTimes");
  const maxAlt=d=>{let b=-99; for(let x=10;x<15;x+=1/60) b=Math.max(b,sp(zd(d,x),45.815,15.98).alt); return b};
  ok(Math.abs(maxAlt("2026-06-21")-67.6)<0.3&&Math.abs(maxAlt("2026-12-21")-20.7)<0.3,"visina Sunca u podne: 67,6° (21. 6.) i 20,7° (21. 12.)");
  const mins=h=>Math.round(h*60), ref=[["2026-03-21",5*60+56,18*60+9],["2026-06-21",5*60+6,20*60+49],["2026-12-21",7*60+34,16*60+14]];
  ok(ref.every(([d,r,z])=>{const t=st(d,45.815,15.98); return Math.abs(mins(t.rise)-r)<=3&&Math.abs(mins(t.set)-z)<=3}),"izlazak i zalazak unutar 3 min od tablica za Zagreb (calendar.center)");
  ok(Math.abs(sp(zd("2026-06-21",9),45.815,15.98).az-90)<25&&Math.abs(sp(zd("2026-06-21",17),45.815,15.98).az-270)<25,"ujutro je Sunce na istoku, popodne na zapadu");
  // elektrana: zračenje 100 W/m² svaki sat
  let called=0;
  w.fetch=(u)=>{called++; const t=[],v=[]; for(const y of [2023,2024,2025]){const n=(y===2024?366:365)*24; for(let i=0;i<n;i++){const d=new Date(Date.UTC(y,0,1)+i*3600e3); t.push(d.toISOString().slice(0,13)+":00"); v.push(100);}}
    ok(/tilt=30/.test(u)&&/azimuth=0/.test(u)&&/global_tilted_irradiance/.test(u),"zahtjev za zračenje šalje nagib i orijentaciju");
    return Promise.resolve({ok:true,status:200,json:()=>Promise.resolve({hourly:{time:t,global_tilted_irradiance:v}})})};
  const r=await w.eval("pvFetch")(45.8,15.98,30,0);
  ok(Math.abs(r.annual-(100*(8760*2+8784)/3/1000))<0.01,"godišnje zračenje = prosjek tri godine");
  const d=data(w,parcelRect(30,25),"2.2."); w.eval("render")(d);
  w.document.getElementById("pvKwp").value="5"; w.document.getElementById("pvShade").value="10";
  called=0; await w.eval("pvRun")(); await w.eval("pvRun")();
  const E=r.annual*5*0.8*0.9, t=w.document.getElementById("pvOut").textContent;
  ok(t.includes(w.eval("fmt")(E)+" kWh godišnje"),"proizvodnja = zračenje × kWp × 0,80 × (1 − zasjenjenje)");
  ok(called===1,"podaci o zračenju se pamte (jedan zahtjev)");
  w.fetch=()=>Promise.reject(new Error("x"));
  w.document.getElementById("pvTilt").value="45"; await w.eval("pvRun")();
  ok(/ne može izračunati/.test(w.document.getElementById("pvOut").textContent)&&!/kWh godišnje/.test(w.document.getElementById("pvOut").textContent),"bez podataka nema procjene proizvodnje");
  // potres
  const sh=w.document.getElementById("sheet").textContent;
  ok(/95 godina/.test(sh)&&/475 godina/.test(sh)&&/Vrijednosti nisu upisane/.test(sh),"potres: objašnjena povratna razdoblja, bez izmišljene vrijednosti");
  const i=w.document.getElementById("sz475"); i.value="0.26"; i.dispatchEvent(new w.Event("input",{bubbles:true}));
  w.eval("render")(d);
  ok(w.document.getElementById("sz475").value==="0.26"&&/2,55 m\/s²/.test(w.document.getElementById("sheet").textContent),"upisana vrijednost a_gR se sprema i preračunava u m/s²");
  ok(!/serklaž/.test(w.document.getElementById("sheet").textContent),"nema zaključaka o konstrukciji");
  ok(errs.length===0,"bez JS grešaka (sunce, elektrana, potres): "+errs.join(" | "));
}

// ---------------- 11. Mobilno sučelje: unosi se čuvaju pri ponovnom prikazu i promjeni kartice
{
  const {w,errs}=boot();
  const d=data(w,parcelRect(30,25),"2.2."); w.eval("render")(d);
  const b=w.document.getElementById("bArea"); b.value="177"; b.dispatchEvent(new w.Event("input",{bubbles:true}));
  w.eval("render")({...d,env:{v:{roads:[],roadLines:[],stops:[]}}});
  ok(w.document.getElementById("bArea").value==="177","unos površine kuće ostaje nakon ponovnog prikaza iste čestice");
  w.eval("setTab")("troskovi"); w.eval("setTab")("analiza");
  ok(w.document.getElementById("bArea").value==="177","unos ostaje nakon promjene kartice");
  const groups=[...w.document.querySelectorAll("#sheet .grp")].map(g=>g.dataset.g);
  ok(groups.includes("sum")&&groups.includes("analiza")&&groups.includes("troskovi"),"sadržaj je podijeljen u skupine sažetak, analiza i troškovi");
  ok(!!w.document.querySelector('.grp[data-g=troskovi] details[data-k="buy"]')&&!!w.document.querySelector('.grp[data-g=troskovi] details[data-k="build"]')&&!!w.document.querySelector('.grp[data-g=analiza] details[data-k="zk"]'),"moduli su u ispravnim skupinama");
  w.eval("setTab")("spremljeno");
  ok(!w.document.getElementById("aux").hidden&&w.document.getElementById("sheet").hidden,"Spremljeno se otvara bez brisanja analize");
  w.document.getElementById("auxBack").dispatchEvent(new w.Event("click",{bubbles:true}));
  ok(w.document.getElementById("bArea").value==="177"&&!w.document.getElementById("sheet").hidden,"povratak iz Spremljenog vraća analizu s unosima");
  ok(errs.length===0,"bez JS grešaka u mobilnom sučelju: "+errs.join(" | "));
}

netTests().then(infraTests).then(sunTests).then(()=>{
  console.log(`\n${pass} prošlo, ${fail} palo`);
  if(fails.length){console.log("PALO:\n - "+fails.join("\n - ")); process.exit(1)}
});

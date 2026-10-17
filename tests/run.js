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
      w.HTMLElement.prototype.scrollIntoView=function(){}; }});
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
  ok(/ispunjeno/.test(s2)&&!/potrebna dodatna provjera/.test(s2),"2.2: čestica 750 m² ispunjava min. površinu");
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

console.log(`\n${pass} prošlo, ${fail} palo`);
if(fails.length){console.log("PALO:\n - "+fails.join("\n - ")); process.exit(1)}

// Usporedba prije/poslije Plan Integrity za kontrolne slučajeve (Krk 735/76, 735/54; Zagreb 1541/2 k.o. Remete).
//   node tests/plan_integrity/usporedba_prije_poslije.js <index.html prije> <index.html poslije> [izlaz.json]
// Učitava obje izgrađene aplikacije u jsdom (bez mreže), prikazuje iste čestice s istim odabirima i ispisuje registar
// pouzdanosti (A/B/C) te, gdje postoji, status rezultata i dokazni lanac. Ništa ne mijenja.
const fs=require("fs"), path=require("path"), {JSDOM,VirtualConsole}=require(path.join(__dirname,"../node_modules/jsdom"));
const T=path.join(__dirname,".."), lib=f=>fs.readFileSync(path.join(T,"node_modules",f),"utf8"), rd=f=>JSON.parse(fs.readFileSync(path.join(T,f),"utf8"));
const bez3=g=>JSON.parse(JSON.stringify(g,(k,v)=>Array.isArray(v)&&v.length===3&&v.every(x=>typeof x==="number")?v.slice(0,2):v));
function boot(file){let h=fs.readFileSync(file,"utf8").replace(/<script src="[^"]*leaflet[^"]*"><\/script>/,()=>"<script>"+lib("leaflet/dist/leaflet.js")+"</script>").replace(/<script src="[^"]*turf[^"]*"><\/script>/i,()=>"<script>"+lib("@turf/turf/turf.min.js")+"</script>").replace(/<link[^>]+leaflet[^>]*>/,"");
  const errs=[], vc=new VirtualConsole(); vc.on("jsdomError",e=>errs.push(String(e.message||e)));
  const dom=new JSDOM(h,{runScripts:"dangerously",pretendToBeVisual:true,url:"https://example.org/cestica-zg/",virtualConsole:vc,beforeParse(w){w.fetch=()=>Promise.reject(new Error("bez mreže")); w.scrollTo=()=>{}; w.HTMLElement.prototype.scrollIntoView=function(){};
    const ctx=new Proxy({},{get:(t,k)=>k in t?t[k]:(()=>{}),set:(t,k,v)=>(t[k]=v,true)}); w.HTMLCanvasElement.prototype.getContext=function(){return ctx}; w.SVGElement.prototype.createSVGRect=function(){return {}};}});
  try{dom.window.eval('SRC_KRK.oss=""; SRC_KRK.oss2=""; (()=>{const k=RASTER_KATALOZI.find(k=>k.tip==="wms"); k.obuhvat=[0,0,0,0];})()')}catch(e){}
  return {w:dom.window,errs};}
const tick=(ms=40)=>new Promise(r=>setTimeout(r,ms));
const ID=/^(pov-graf|namjena|namjena-udio|izgradenost|plan-UPU|zona-korisnik|zast-korisnik|pravilo|pravilo-karta|zona|calc-|blok-)/;
function snap(w){const E=x=>w.eval(x), L=[...E("PZREG").items.values()].filter(x=>ID.test(x.id)), ob=(()=>{try{return E("piObjava")}catch(e){return null}})();
  return L.map(x=>({id:x.id,naziv:x.naziv,vrijednost:x.vrijednost,pouzdanost:x.raz,status_rezultata:ob?(ob(x)||{}).razina||null:null,
    karike:(x.lanac||[]).map(k=>k.karika+(k.uskladenost?" ["+k.uskladenost+"]":"")),uvjeti:(x.uvjeti||[]).filter(u=>!u.razrijeseno).map(u=>u.tekst),blokada:x.blokada||null}));}
async function krk(file,parcel,namF,plF,koraci){const {w,errs}=boot(file), E=x=>w.eval(x), Tf=w.turf; for(const k of Object.keys(w.localStorage)) w.localStorage.removeItem(k);
  const p=w.JSON.parse(JSON.stringify(parcel)), area=Tf.area(p), nam=namF.map(f=>w.JSON.parse(JSON.stringify(bez3(f))));
  const rows=nam.map(f=>{let sh=0; try{const i=Tf.intersect(p,f); sh=i?Tf.area(i)/area:0}catch(e){} return {p:f.properties,share:sh,geom:f.geometry}}).filter(r=>r.share>0).sort((a,b)=>b.share-a.share);
  const c=Tf.pointOnFeature(p).geometry.coordinates, d={region:"krk",ll:{lat:c[1],lng:c[0]},parcel:p,area,rows,ces:{v:[p]},nam:{v:nam},pl:{v:w.JSON.parse(JSON.stringify(plF))},slope:null,env:null};
  E("KRK_TIP").tip="obit"; E("KRK_TIP").oblik="dvoj"; const out={};
  for(const [ime,zona,zast] of koraci){E("renderKrk")(d); await tick(); if(zona) E("krkZonaSet")(zona); if(zast!=null) E("krkZastSet")(zast); E("renderKrk")(d); await tick(); out[ime]=snap(w);}
  return {koraci:out,greske:errs};}
async function zg(file){const {w,errs}=boot(file), E=x=>w.eval(x), Tf=w.turf, F=rd("pgz-odgovori/zg-1541-2-remete-2026-10-27/podaci.json"), p0=F.ces.features[0], par=w.JSON.parse(JSON.stringify({type:"Feature",geometry:p0.geometry,properties:p0.properties}));
  const area=Tf.area(par), rows=F.zones.features.map(f=>{let sh=0; try{const i=Tf.intersect(par,f); sh=i?Tf.area(i)/area:0}catch(e){} return {p:f.properties,share:sh,geom:f.geometry}}).filter(r=>r.share>0.005).sort((a,b)=>b.share-a.share);
  const d={ll:{lat:F.tocka.lat,lng:F.tocka.lng},parcel:par,area,rows,ces:{v:[par]},nam:{v:F.nam_tocka.features},up:{v:F.up.features},upx:{v:F.upx.features},gn:{v:F.gn.features},checks:E("CHECKS").map(c=>({c,v:[]})),slope:null,zgrade:{v:{area:0,n:0,geoms:[]}}};
  d.envelope=E("buildEnvelope")(par,rows,d.up); E("render")(d); await tick(); return {koraci:{"pravilo 2.2., slobodnostojeća":snap(w)},greske:errs};}
(async()=>{const [A,B,O]=process.argv.slice(2), D="pgz-odgovori/735-76-kornic-2026-10-22/";
  const gj=rd("../docs/primjeri/kornic_cestica_735_76.geojson").features[0], p76={type:"Feature",geometry:bez3(gj.geometry),properties:{broj:"735/76",ko:"KORNIĆ",ref:"735/76@315907",cid:19311099,povrsinaKatastar:405}};
  const F54=rd("pgz-odgovori/735-54-kornic-2026-10-27/podaci.json"), p54={type:"Feature",geometry:F54.granica,properties:{broj:"735/54",ko:"KORNIĆ",ref:"735/54@315907",cid:19311175,povrsinaKatastar:773.54}};
  const res={};
  for(const [ime,f] of [["prije",A],["poslije",B]]){
    res[ime]={"Krk 735/76":await krk(f,p76,rd(D+"namjena_cestica_app.geojson").features,rd(D+"planovi_tocka_app.geojson").features,[["bez zone",null,null],["M11, dvojna obiteljska","M11",null],["M11 + zona zaštite C","M11","C"]]),
      "Krk 735/54":await krk(f,p54,F54.namjena.features,F54.planovi.features,[["M11, dvojna obiteljska","M11",null]]),
      "Zagreb 1541/2 Remete":await zg(f)};}
  const s=JSON.stringify(res,null,1); if(O) fs.writeFileSync(O,s); else console.log(s);
})();

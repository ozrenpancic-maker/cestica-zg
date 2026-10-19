# Servisi Primorsko-goranske županije u aplikaciji Čestica HR

Izvadak iz `src/app.template.html` (grana `razvoj`), bez izmjena. Python ekvivalent iste logike je `tools/pgz/pgz_upit.py`.

Oba servisa su javni ArcGIS REST FeatureServer bez ključa. Aplikacija ih poziva izravno iz preglednika i odgovor traži kao GeoJSON (`f=geojson`, `outSR=4326`).

- **Namjena po točki:** GET, točka u WGS84 (`lon,lat`).
- **Namjena po granici čestice:** POST, jer je geometrija duga. Šalje se Esri poligon s prstenovima čestice u WGS84, a udio svake zone računa se presjekom (turf).
- **Planovi:** GET po točki, uz popis polja.

## Polja koja aplikacija koristi

| Servis | Polje | Primjer | Kako se koristi |
| --- | --- | --- | --- |
| NAMJENA_POVRSINA_NOVO | `OPCINA_GRAD` | KRK | jedinica lokalne samouprave |
| | `POLAZNA_NAMJENA` | građevna područja | razlikuje GP od ostalog (`krkKind`) |
| | `PRIMARNA_NAMJENA` | naselje | GP naselja ili izdvojeno GP |
| | `OZNAKA_NAMJENE` | GPN-1, NA2, P3 | oznaka zone iz PPUO/G |
| | `IZGRADJENOST` | izgrađeno | izgrađeni ili neizgrađeni dio GP-a |
| | `NASELJE`, `NAZIV` | Kornić | naselje |
| | `IZVOR_PODATAKA` | SN 18/19 | službeno glasilo izvora |
| IZRADA_PP | `VRSTA_PP` | PPUO/G, UPU, PPŽ, DPPR | vrsta plana (DPPR se ne prikazuje) |
| | `STATUS_PP` | VAŽEĆI, U IZRADI, VAN SNAGE | status |
| | `GRAD_OPCINA` | Krk | jedinica |
| | `NAZIV` | Odluka o donošenju … | naziv odluke |
| | `SN_BROJ` | 2020-29 | broj glasila (godina-broj); najveći = zadnja važeća odluka po vrsti |
| | `SN_LINK`, `PDF_LINK_PUBLIC` | URL | poveznice na glasilo i dokument |
| | `DatumStNaSnPlana`, `DatumDonOdlIzr` | | datumi stupanja na snagu i odluke o izradi (dohvaćaju se, aplikacija ih još ne prikazuje) |

Primjeri vrijednosti su iz prikaza aplikacije na česticama u Korniću (735/58, 735/129, 735/166), ne iz sirovog odgovora za 735/76.

## Upiti za česticu 735/76, k.o. Kornić

Točka je težište granice iz DGU-a (45,044049, 14,615896). Otvori ove dvije adrese u pregledniku: odgovor je izvorni JSON servisa.

- Namjena: `https://gisportal.pgz.hr/server/rest/services/STANJE/NAMJENA_POVRSINA_NOVO/FeatureServer/0/query?geometry=14.615896,45.044049&geometryType=esriGeometryPoint&inSR=4326&outFields=*&returnGeometry=false&f=json`
- Planovi: `https://gisportal.pgz.hr/server/rest/services/STANJE/IZRADA_PP/FeatureServer/0/query?geometry=14.615896,45.044049&geometryType=esriGeometryPoint&inSR=4326&outFields=*&returnGeometry=false&f=json`

Za cijelu česticu i udjele zona: `python3 tools/pgz/pgz_upit.py kornic_cestica_735_76.geojson`. Skripta sprema izvorne odgovore u `pgz_odgovori/`.

## Adrese servisa

```js
const PGZ="https://gisportal.pgz.hr/server/rest/services/STANJE/";
const SRC_KRK={
  namjena:PGZ+"NAMJENA_POVRSINA_NOVO/FeatureServer/0/query",
  planovi:PGZ+"IZRADA_PP/FeatureServer/0/query",
  // posrednik prema javnom OSS-u za upisanu (ZK) površinu; prazno = isključeno (tools/oss-posrednik)
  oss:"https://cestica-oss.ozren-pancic.workers.dev/",
};
```

## Upit po točki i po poligonu (pointQuery, polyQuery)

```js
function pointQuery(url,ll,fields="*",geom=true){
  const p=new URLSearchParams({geometry:ll.lng+","+ll.lat,geometryType:"esriGeometryPoint",inSR:"4326",spatialRel:"esriSpatialRelIntersects",outFields:fields,returnGeometry:String(geom),outSR:"4326",f:"geojson"});
  return getJSON(url+"?"+p.toString()).then(featuresOf);
}
function polyQuery(url,geom,fields="*",withGeom=true){
  const rings=geom.type==="Polygon"?geom.coordinates:geom.coordinates.flat();
  const p=new URLSearchParams({geometry:JSON.stringify({rings,spatialReference:{wkid:4326}}),geometryType:"esriGeometryPolygon",inSR:"4326",spatialRel:"esriSpatialRelIntersects",outFields:fields,returnGeometry:String(withGeom),outSR:"4326",f:"geojson"});
  return getJSON(url,{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},body:p.toString()}).then(featuresOf);
}
```

## Tijek za Krk: čestica, namjena po točki i po granici čestice, planovi po točki (inspectKrk)

```js
async function inspectKrk(ll){
  const id=++clickId;
  selLayer.clearLayers(); infLayer.clearLayers(); skiLayer.clearLayers(); TL.layer=null; TL.marker=null; TL.rotM=null; TL.center=null; TL.zones=null;
  window.__lastData=null; window.__infra=null; window.__ski=null; window.__env=null; KRK_CUR=null;
  L.circleMarker(ll,{radius:5,color:"#000",weight:2,fillColor:"#fff",fillOpacity:1}).addTo(selLayer);
  sheet.innerHTML='<p class="hint"><span class="spin"></span>Otok Krk (pilot): tražim česticu u katastru i namjenu iz županijskog sloja…</p>';
  const [ces,nam,pl]=await Promise.all([
    settle(loadParcelKrk(ll)),
    settle(pointQuery(SRC_KRK.namjena,ll,"*",false)),
    settle(pointQuery(SRC_KRK.planovi,ll,"GRAD_OPCINA,VRSTA_PP,STATUS_PP,NAZIV,SN_BROJ,SN_LINK,PDF_LINK_PUBLIC,DatumStNaSnPlana,DatumDonOdlIzr",false))
  ]);
  if(id!==clickId) return;
  const parcel=ces.v||null, area=parcel?turf.area(parcel.geometry):null;
  let rows=(nam.v||[]).map(f=>({p:f.properties||{},share:null,geom:null}));
  if(parcel){
    L.geoJSON(parcel.geometry,{style:{color:"#111",weight:3,fill:false},interactive:false}).addTo(selLayer);
    try{const z=await polyQuery(SRC_KRK.namjena,parcel.geometry,"*",true);
      rows=z.map(f=>{let share=null; try{const i=turf.intersect(parcel.geometry,f.geometry); share=i?turf.area(i)/area:0}catch(e){} return {p:f.properties||{},share,geom:f.geometry}})
           .filter(r=>r.share===null||r.share>0.005).sort((a,b)=>(b.share??0)-(a.share??0));
    }catch(e){}
    if(id!==clickId) return;
    rows.forEach(r=>r.geom&&L.geoJSON(r.geom,{style:{color:KRK_COLORS[krkKind(r.p)],weight:1,fillOpacity:.3},interactive:false}).addTo(selLayer));
  }
  const d={region:"krk",ll,parcel,area,rows,ces,nam,pl,slope:null,env:null};
  renderKrk(d);
  const [slope,env,ski]=await Promise.all([settle(loadSlope(parcel,ll)),settle(loadEnv(ll,parcel)),FEATURES.infra?settle(loadSki(parcel,ll,SKI_KRK)):Promise.resolve(null)]);
  if(id!==clickId) return;
  window.__ski=ski||null; skiDraw(ski);
  renderKrk({...d,slope,env,ski});
}
```

## Vrsta područja i odabir važećih planova (krkKind, snKey, krkPlans)

```js
function krkKind(p){
  const pol=String(p.POLAZNA_NAMJENA||"").toLowerCase(), pri=String(p.PRIMARNA_NAMJENA||"").toLowerCase();
  if(/građevn|gradevn|građevinsk/.test(pol)) return /naselj/.test(pri)?"gpn":"gpi";
  if(pol||pri) return "van";
  return "nep";
}

const snKey=s=>{const m=String(s||"").match(/(\d{4})\D+(\d+)/); return m?+m[1]*1000+ +m[2]:0};
function krkPlans(feats){
  const P=(feats||[]).map(f=>f.properties||{}).filter(p=>p.VRSTA_PP&&p.VRSTA_PP!=="DPPR");
  const vazeci={}, izrada=[];
  for(const p of P){
    const st=String(p.STATUS_PP||"").toUpperCase();
    if(st==="VAŽEĆI"){const k=p.VRSTA_PP+"|"+(p.GRAD_OPCINA||""); if(!vazeci[k]||snKey(p.SN_BROJ)>snKey(vazeci[k].SN_BROJ)) vazeci[k]=p;}
    else if(st==="U IZRADI") izrada.push(p);
  }
  const ord=v=>["UPU","DPU","GUP","PPUO/G","PPŽ"].indexOf(v);
  return {vazeci:Object.values(vazeci).sort((a,b)=>ord(a.VRSTA_PP)-ord(b.VRSTA_PP)), izrada:izrada.sort((a,b)=>snKey(b.SN_BROJ)-snKey(a.SN_BROJ)),
          upu:Object.values(vazeci).filter(p=>p.VRSTA_PP==="UPU"||p.VRSTA_PP==="DPU")};
}
```

## Jedinica lokalne samouprave iz odgovora (krkJls)

```js
function krkJls(rows,pl){
  const r=rows.find(x=>x.p.OPCINA_GRAD); if(r) return String(r.p.OPCINA_GRAD).toUpperCase();
  const p=pl&&pl.v&&pl.v.map(f=>f.properties||{}).find(x=>x.VRSTA_PP==="PPUO/G"&&x.GRAD_OPCINA); return p?String(p.GRAD_OPCINA).toUpperCase():null;
}
```

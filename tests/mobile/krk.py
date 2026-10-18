"""Pilot otok Krk na mobitelu (Chromium, lažni servisi): prikaz bez vodoravnog pomicanja, karta i panel, snimke zaslona.
Pokretanje: cd tests && node mobile/make_local.js && python3 mobile/krk.py
"""
import os, json
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out"); LOCAL=os.path.join(OUT,"preview_local.html")
CHROME=os.environ.get("CHROME","/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
MOCK=r"""async()=>{
  const ll={lat:45.0274,lng:14.5935}, [E0,N0]=tmFwd(ll.lng,ll.lat);
  const ring=[[E0-15,N0-10],[E0+15,N0-10],[E0+15,N0+10],[E0-15,N0+10],[E0-15,N0-10]], w=ring.map(([e,n])=>tmInv(e,n)), mid=(w[0][0]+w[1][0])/2;
  const half=(a,b)=>({type:"Polygon",coordinates:[[[a,w[0][1]-1e-4],[b,w[0][1]-1e-4],[b,w[2][1]+1e-4],[a,w[2][1]+1e-4],[a,w[0][1]-1e-4]]]});
  const gp={OPCINA_GRAD:"KRK",POLAZNA_NAMJENA:"građevna područja",PRIMARNA_NAMJENA:"naselje",OZNAKA_NAMJENE:"GPN-1",IZGRADJENOST:"izgrađeno",NASELJE:"Kornić",IZVOR_PODATAKA:"SN 18/19"};
  const ag={OPCINA_GRAD:"KRK",POLAZNA_NAMJENA:"poljoprivredno tlo",PRIMARNA_NAMJENA:"ostalo obradivo tlo",OZNAKA_NAMJENE:"P3",IZVOR_PODATAKA:"SN 18/19"};
  const plans=[{GRAD_OPCINA:"Krk",VRSTA_PP:"PPUO/G",STATUS_PP:"VAŽEĆI",NAZIV:"Odluka o donošenju Prostornog plana uređenja Grada Krka, pročišćeni tekst odredbi za provedbu i grafičkog dijela",SN_BROJ:"2020-29",SN_LINK:"https://example.org/a.pdf"},
    {GRAD_OPCINA:"Krk",VRSTA_PP:"PPUO/G",STATUS_PP:"U IZRADI",NAZIV:"Odluka o izradi",SN_BROJ:"2025-07"},{GRAD_OPCINA:"Primorsko-goranska županija",VRSTA_PP:"PPŽ",STATUS_PP:"VAŽEĆI",NAZIV:"Odredbe za provedbu, pročišćeni tekst",SN_BROJ:"2024-12"}];
  const ok=b=>Promise.resolve(new Response(JSON.stringify(b),{status:200,headers:{"Content-Type":"application/json"}}));
  window.fetch=(u,o={})=>{u=String(u);
    if(u.includes("uredjenazemlja")) return ok({type:"FeatureCollection",features:/CadastralZoning/.test(u)?[{type:"Feature",geometry:{type:"Polygon",coordinates:[ring]},properties:{name:"KORNIĆ"}}]:[{type:"Feature",geometry:{type:"Polygon",coordinates:[ring]},properties:{label:"2345/6",areaValue:600}}]});
    if(u.includes("NAMJENA_POVRSINA_NOVO")) return ok({type:"FeatureCollection",features:/esriGeometryPolygon/.test(o.body||"")?[{type:"Feature",geometry:half(w[0][0]-1e-4,mid),properties:gp},{type:"Feature",geometry:half(mid,w[1][0]+1e-4),properties:ag}]:[{type:"Feature",geometry:null,properties:gp}]});
    if(u.includes("IZRADA_PP")) return ok({type:"FeatureCollection",features:plans.map(p=>({type:"Feature",geometry:null,properties:p}))});
    if(u.includes("open-meteo")) return ok({elevation:[40,42,40,38,40]});
    if(/interpreter/.test(u)) return ok({elements:[]});
    return Promise.reject(new TypeError("Failed to fetch"));
  };
  map.setView([ll.lat,ll.lng],18); await inspect(L.latLng(ll.lat,ll.lng)); await new Promise(r=>setTimeout(r,300));
}"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    for wd,ht in ((390,844),(320,640)):
        pg=b.new_page(viewport={"width":wd,"height":ht},device_scale_factor=2,has_touch=True,is_mobile=True)
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        pg.route("**/*",lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
        pg.goto("file://"+LOCAL); pg.wait_for_timeout(400)
        pg.evaluate(MOCK)
        st=pg.evaluate("UI.state")
        pg.screenshot(path=f"{OUT}/krk_{wd}_half.png")
        pg.evaluate("setState('full')"); pg.wait_for_timeout(300)
        pg.screenshot(path=f"{OUT}/krk_{wd}_full.png")
        r={"state_after":st,
           "scrollW":pg.evaluate("document.documentElement.scrollWidth"),
           "overflow":pg.evaluate("""()=>[...document.querySelectorAll('#sheet *')].filter(e=>e.offsetParent&&e.scrollWidth>e.clientWidth+2&&!['INPUT','SELECT','TEXTAREA'].includes(e.tagName)&&getComputedStyle(e).overflowX!=='auto').map(e=>e.tagName+'.'+e.className).slice(0,5)"""),
           "parcel":pg.evaluate("document.querySelector('#sheet .parcel')&&document.querySelector('#sheet .parcel').textContent"),
           "layers":pg.evaluate("selLayer.getLayers().length"),
           "errors":errs}
        res[f"{wd}x{ht}"]=r; pg.close()
    b.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
bad=[k for k,r in res.items() if r["scrollW"]>int(k.split("x")[0]) or r["overflow"] or r["errors"] or r["parcel"]!="2345/6" or r["layers"]<3 or r["state_after"]!="half"]
print("KRK mobilno:", "sve u redu" if not bad else "PROBLEM: "+", ".join(bad))

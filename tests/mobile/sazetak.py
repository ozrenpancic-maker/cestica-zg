"""Sažetak uvjeta gradnje i pilot prijedloga zone za 735/76 k.o. Kornić (Chromium, spremljeni odgovori PGŽ-a, bez mreže):
snimke zaslona na računalu i mobitelu, provjera vodoravnog pomicanja, prihvaćanje prijedloga.
Pokretanje: cd tests && node mobile/make_local.js && python3 mobile/sazetak.py"""
import os, json, base64
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out"); LOCAL=os.path.join(OUT,"preview_local.html"); T=os.path.dirname(HERE)
CHROME=os.environ.get("CHROME","/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
D=os.path.join(T,"pgz-odgovori","735-76-kornic-2026-10-22")
rd=lambda f: json.load(open(os.path.join(D,f),encoding="utf-8"))
PNG=open(os.path.join(D,"karte","karta4_izvorno.png"),"rb").read()
EXT=rd("karte/_meta.json")["karta4"]["extent"]
FIX={"parcel":json.load(open(os.path.join(T,"..","docs","primjeri","kornic_cestica_735_76.geojson")))["features"][0]["geometry"]["coordinates"][0],
     "namPoly":rd("namjena_cestica_app.geojson"),"namPt":rd("namjena_tocka_app.geojson"),"plan":rd("planovi_tocka_app.geojson"),"ext":EXT,"png":base64.b64encode(PNG).decode()}
MOCK=r"""async(F)=>{
  const ll={lat:45.044049,lng:14.615896}, W2=F.parcel.map(([a,b])=>[Math.round(a*1e6),Math.round(b*1e6)]), enc=[W2[0][0],W2[0][1]]; for(let i=1;i<W2.length;i++) enc.push(W2[i][0]-W2[i-1][0],W2[i][1]-W2[i-1][1]);
  const key=Math.floor(ll.lat/0.009)+"_"+Math.floor(ll.lng/0.013), bin=Uint8Array.from(atob(F.png),c=>c.charCodeAt(0));
  const ok=b=>Promise.resolve(new Response(JSON.stringify(b),{status:200,headers:{"Content-Type":"application/json"}}));
  const att={OBJECTID:7104,Name:"618_karta4_i.tif",KARTA_NAZIV:null,PLAN_NAZIV:"UPU 2 - Kornić",OPCINA:"KRK",KARTA_SIFRA:"618_karta4",MJERILO:"1:1000",STANJE_1212:null};
  window.__mreza=[];
  window.fetch=(u,o={})=>{u=String(u); window.__mreza.push(u.slice(0,90));
    if(u.includes("data/kat_krk/")){ if(u.endsWith("index.json")) return ok({v:1,preuzeto:"2026-10-19",dlat:0.009,dlon:0.013,prednost:[],ko:{"315907":{naziv:"KORNIĆ"}},kvadrati:[key]}); return ok([[19311099,"735/76","315907",405,[[enc]]]]);}
    if(u.includes("NAMJENA_POVRSINA_NOVO")) return ok(/esriGeometryPolygon/.test((o.body||"")+u)?F.namPoly:F.namPt);
    if(u.includes("IZRADA_PP")) return ok(F.plan);
    if(u.includes("PP_RASTERI")&&u.includes("/5/query")) return ok({features:[{attributes:att}]});
    if(u.includes("PP_RASTERI")&&u.includes("/query")) return ok({features:[]});
    if(u.includes("PP_RASTERI")&&u.includes("/export")&&u.includes("f=json")) return ok({href:"https://gisportal.pgz.hr/server/rest/directories/arcgisoutput/karta4_735_76.png",extent:F.ext,width:800,height:800});
    if(u.includes("PP_RASTERI")&&u.includes("/export")) return Promise.resolve(new Response(new Blob([bin],{type:"image/png"}),{status:200}));
    return Promise.reject(new TypeError("Failed to fetch"));};
  try{localStorage.setItem("uzPilot","1"); localStorage.setItem("krkTip",JSON.stringify({tip:"obit",oblik:"slob"})); localStorage.removeItem("krkZahvat");}catch(e){}
  Object.assign(KRK_TIP,{tip:"obit",oblik:"slob"});
  map.setView([ll.lat,ll.lng],18); await inspect(L.latLng(ll.lat,ll.lng)); await new Promise(r=>setTimeout(r,1500));
}"""
res={}
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    for ime,vp,mob in (("racunalo",(1280,900),False),("mobitel",(390,844),True)):
        pg=b.new_page(viewport={"width":vp[0],"height":vp[1]},device_scale_factor=2 if mob else 1,has_touch=mob,is_mobile=mob)
        errs=[]; pg.on("pageerror",lambda e: errs.append(str(e)))
        def route(r):
            u=r.request.url
            if u.startswith("file:"): return r.continue_()
            if "gisportal.pgz.hr" in u and u.endswith(".png"): return r.fulfill(status=200,body=PNG,content_type="image/png")
            return r.abort()
        pg.route("**/*",route)
        pg.goto("file://"+LOCAL); pg.wait_for_timeout(400)
        pg.evaluate("()=>{try{localStorage.clear()}catch(e){}}")
        pg.evaluate(MOCK,FIX)
        if mob: pg.evaluate("setState('full')"); pg.wait_for_timeout(300)
        else: pg.evaluate("document.getElementById('wideBtn')&&document.getElementById('wideBtn').click()"); pg.wait_for_timeout(300)
        r={"uz":pg.evaluate("(()=>{const e=document.querySelector('#uzUvjeti .uz'); return e?e.dataset.uz:null})()"),
           "kandidat":pg.evaluate("(()=>{const e=document.querySelector('[data-uz-kandidat]'); return e?e.dataset.uzKandidat:null})()")}
        OPEN="(sel)=>{let e=document.querySelector(sel); while(e){if(e.tagName==='DETAILS') e.open=true; e=e.parentElement;}}"
        pg.evaluate(OPEN,"#uzUvjeti"); pg.wait_for_timeout(200)
        r["uz_lanac"]=pg.evaluate("(()=>{let e=document.querySelector('#uzUvjeti .uz'),o=[]; while(e&&e!==document.body){o.push(e.tagName+(e.id?'#'+e.id:'')+'.'+String(e.className).slice(0,20)+':'+getComputedStyle(e).display+(e.hidden?':hidden':'')); e=e.parentElement;} return o})()")
        r["uz_vidljiv"]=pg.evaluate("(()=>{const e=document.querySelector('#uzUvjeti .uz'); return !!(e&&e.offsetParent)})()")
        uz=pg.query_selector("#uzUvjeti .uz") if r["uz_vidljiv"] else None
        if uz:
            pg.evaluate("document.querySelector('#uzUvjeti .uz details')&&(document.querySelector('#uzUvjeti .uz details').open=true)")
            pg.evaluate("document.querySelector('#uzUvjeti').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300)
            pg.screenshot(path=f"{OUT}/prijedlog_zone_{ime}.png")
        btn=pg.query_selector('#uzUvjeti [data-uzb="prihvati"]')
        if btn and r["uz_vidljiv"]: btn.click(); pg.wait_for_timeout(600)
        r["zona_nakon"]=pg.evaluate("krkZonaGet()")
        r["zona_pz"]=pg.evaluate("(()=>{const z=PZREG.items.get('zona-korisnik'); return z?[z.raz,z.izvor||null]:null})()")
        pg.evaluate(OPEN,"[data-pi-sazetak]"); pg.wait_for_timeout(200)
        sz=pg.query_selector("[data-pi-sazetak]")
        r["sazetak"]=bool(sz)
        if sz:
            pg.evaluate("document.getElementById('sec-uvjeti').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/sazetak_{ime}.png")
            red=pg.query_selector('[data-pi-id="calc-min"] > summary')
            if red: red.click(); pg.wait_for_timeout(200); pg.evaluate("document.querySelector('[data-pi-id=\"calc-min\"]').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/sazetak_{ime}_prosireno.png")
            pg.evaluate("document.querySelector('[data-pi-provjeri]').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/sazetak_{ime}_provjeri.png")
            r["redovi"]=pg.evaluate("[...document.querySelectorAll('[data-pi-sazetak] .pis-r > summary')].filter(s=>s.parentElement.matches('.pis-r')).map(s=>s.innerText.replace(/\\s+/g,' ').slice(0,140))")
        pg.evaluate("krkZastSet('C'); renderKrk(KRK_CUR)"); pg.wait_for_timeout(400); pg.evaluate(OPEN,"[data-pi-sazetak]")
        r["krov_C"]=pg.evaluate("(()=>{const e=document.querySelector('[data-pi-id=\"blok-krov\"] > summary'); return e?e.innerText.replace(/\\s+/g,' '):null})()")
        pg.evaluate("document.getElementById('sec-uvjeti').scrollIntoView({block:'start'})"); pg.wait_for_timeout(300); pg.screenshot(path=f"{OUT}/sazetak_{ime}_zonaC.png")
        pg.evaluate("krkZastSet(''); renderKrk(KRK_CUR)"); pg.wait_for_timeout(300)
        r["scrollW"]=pg.evaluate("document.documentElement.scrollWidth"); r["sirina"]=vp[0]
        r["overflow"]=pg.evaluate("""()=>[...document.querySelectorAll('[data-pi-sazetak] *, .uz *')].filter(e=>e.offsetParent&&e.scrollWidth>e.clientWidth+2&&!['INPUT','SELECT','TEXTAREA'].includes(e.tagName)&&getComputedStyle(e).overflowX!=='auto').map(e=>e.tagName+'.'+e.className).slice(0,5)""")
        r["errors"]=errs; res[ime]=r; pg.close()
    b.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
bad=[k for k,r in res.items() if r["scrollW"]>r["sirina"] or r["overflow"] or r["errors"] or not r["sazetak"] or r["kandidat"]!="M11" or r["zona_nakon"]!="M11" or not r["zona_pz"] or r["zona_pz"][0]!="C" or not r["krov_C"] or "blokirano" not in r["krov_C"]]
print("SAŽETAK I PRIJEDLOG ZONE:", "sve u redu" if not bad else "PROBLEM: "+", ".join(bad))

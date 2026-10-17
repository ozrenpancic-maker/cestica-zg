import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out"); LOCAL=os.path.join(OUT,"preview_local.html")
CHROME=os.environ.get("CHROME","/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
# Prije pokretanja: node mobile/make_local.js
from playwright.sync_api import sync_playwright
import sys
SETUP=r"""
() => {
 const o=[15.97,45.84], dx=30/(111320*Math.cos(45.84*Math.PI/180)), dy=25/110540;
 const g={type:"Polygon",coordinates:[[[o[0],o[1]],[o[0]+dx,o[1]],[o[0]+dx,o[1]+dy],[o[0],o[1]+dy],[o[0],o[1]]]]};
 const parcel={type:"Feature",geometry:g,properties:{KATASTARSKA_CESTICA:"3101/2",KATASTARSKA_OPCINA:"REMETE",GRADSKA_CETVRT:"Maksimir"}};
 const rows=[{p:{Analitika:"Stambena i mješovita",Namjena:"Stambena namjena",Naziv_plana:"GUP Grada Zagreba"},share:1,geom:g}];
 const up={v:[{properties:{BROJ_UP:"2.2."}}]};
 const d={ll:{lat:45.84,lng:15.97},parcel,area:turf.area(g),rows,ces:{v:[parcel]},nam:{v:rows},up,upx:{v:[]},gn:{v:[]},checks:CHECKS.map(c=>({c,v:[]})),slope:null,zgrade:{v:{area:0,n:0,geoms:[]}},env:{v:{roads:[],roadLines:[],stops:[{n:"Remete",d:240,type:"autobus"}]}}};
 d.envelope=buildEnvelope(parcel,rows,up); window.__env=d.envelope;
 L.geoJSON(g,{style:{color:"#111",weight:3,fill:false}}).addTo(selLayer);
 render(d); map.setView([45.8401,15.9705],18);
}"""
W=[(320,640),(360,740),(390,844),(480,900),(844,390)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    for (w,h) in W:
        pg=b.new_page(viewport={"width":w,"height":h},device_scale_factor=2,has_touch=True,is_mobile=True)
        pg.route("**/*",lambda r: r.abort() if not r.request.url.startswith("file:") else r.continue_())
        pg.goto("file://"+LOCAL); pg.wait_for_timeout(300)
        pg.evaluate(SETUP); pg.wait_for_timeout(400)
        pg.screenshot(path=OUT+f"/m_{w}x{h}_half.png")
        sw=pg.evaluate("document.documentElement.scrollWidth"); 
        small=pg.evaluate("""()=>[...document.querySelectorAll('#tabs button,header .ib,.card,#lyrBtn')].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.id||e.textContent.trim().slice(0,10),Math.round(r.width),Math.round(r.height)]}).filter(x=>x[1]<44||x[2]<44)""")
        over=pg.evaluate("""()=>[...document.querySelectorAll('#sheet *')].filter(e=>e.offsetParent&&e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX!=='auto'&&!['INPUT','SELECT','TEXTAREA'].includes(e.tagName)).slice(0,5).map(e=>e.className+'|'+e.tagName+'|'+e.textContent.slice(0,30))""")
        print(w,h,"scrollW",sw,"small",small,"overflow",over)
        if w==390:
            pg.click('#tabs button[data-tab=troskovi]'); pg.wait_for_timeout(300); pg.screenshot(path=OUT+"/m_390_trosk.png")
            pg.click('#tabs button[data-tab=karta]'); pg.wait_for_timeout(300); pg.screenshot(path=OUT+"/m_390_peek.png")
            pg.click('#lyrBtn'); pg.wait_for_timeout(100); pg.screenshot(path=OUT+"/m_390_layers.png"); pg.click('#lyrBtn')
            pg.click('#tabs button[data-tab=analiza]'); pg.wait_for_timeout(300)
            pg.click('.card[data-go=sec-uvjeti]'); pg.wait_for_timeout(500); pg.screenshot(path=OUT+"/m_390_full.png")
            pg.click('#tabs button[data-tab=spremljeno]'); pg.wait_for_timeout(300); pg.screenshot(path=OUT+"/m_390_fav.png")
        pg.close()
    b.close()

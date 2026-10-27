import os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"out"); LOCAL=os.path.join(OUT,"preview_local.html")
CHROME=os.environ.get("CHROME","/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
# Prije pokretanja: node mobile/make_local.js
from playwright.sync_api import sync_playwright
import json,time
SETUP=open(os.path.join(HERE,"layout.py")).read().split('SETUP=r"""')[1].split('"""')[0]
res={}
def page(b,w,h,**kw):
    pg=b.new_page(viewport={"width":w,"height":h},device_scale_factor=2,has_touch=True,is_mobile=True,**kw)
    pg.route("**/*",lambda r: r.abort() if not r.request.url.startswith("file:") else r.continue_())
    pg.goto("file://"+LOCAL); pg.wait_for_timeout(300); return pg
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    # 1) povlačenje ručke panela
    pg=page(b,390,844); pg.evaluate(SETUP); pg.wait_for_timeout(300)
    g=pg.locator("#grab").bounding_box(); x=g["x"]+g["width"]/2; y=g["y"]+g["height"]/2
    pg.mouse.move(x,y); pg.mouse.down(); pg.mouse.move(x,y-400,steps=8); pg.mouse.up(); pg.wait_for_timeout(300)
    res["drag_up"]=pg.evaluate("UI.state")
    g=pg.locator("#grab").bounding_box(); pg.mouse.move(x,g["y"]+10); pg.mouse.down(); pg.mouse.move(x,g["y"]+700,steps=8); pg.mouse.up(); pg.wait_for_timeout(300)
    res["drag_down"]=pg.evaluate("UI.state")
    pg.click("#grab"); pg.wait_for_timeout(250); res["tap"]=pg.evaluate("UI.state")
    # 2) virtualna tipkovnica: fokus u polje, pa manji vidljivi dio ekrana
    pg.click('#tabs button[data-tab=troskovi]'); pg.wait_for_timeout(300)
    pg.evaluate("()=>{const d=document.querySelector('details[data-k=buy]'); d.open=true}")
    pg.focus("#yPrice"); pg.set_viewport_size({"width":390,"height":420}); pg.wait_for_timeout(500)
    r=pg.evaluate("()=>{const e=document.getElementById('yPrice').getBoundingClientRect(); return [Math.round(e.top),Math.round(e.bottom),innerHeight,UI.state]}")
    res["keyboard"]=r
    pg.screenshot(path=OUT+"/m_kbd.png"); pg.close()
    # 3) velika slova (stranica uvećana 130 %)
    for w in (320,390):
        pg=page(b,w,740); pg.evaluate(SETUP); pg.add_style_tag(content="#panel{zoom:1.3}"); pg.evaluate("setState('full')"); pg.wait_for_timeout(300)
        res[f"bigfont_{w}_scrollW"]=pg.evaluate("document.documentElement.scrollWidth")
        res[f"bigfont_{w}_overflow"]=pg.evaluate("""()=>[...document.querySelectorAll('#sheet *')].filter(e=>e.offsetParent&&e.scrollWidth>e.clientWidth+2&&!['INPUT','SELECT','TEXTAREA'].includes(e.tagName)&&getComputedStyle(e).overflowX!=='auto').length""")
        pg.screenshot(path=OUT+f"/m_big_{w}.png"); pg.close()
    # 4) spora veza: svaki zahtjev 2,5 s
    pg=b.new_page(viewport={"width":390,"height":844},has_touch=True,is_mobile=True)
    def slow(r):
        u=r.request.url
        if u.startswith("file:"): return r.continue_()
        if "arcgis" in u:
            time.sleep(0)  # odgoda u stranici
        r.abort()
    pg.route("**/*",lambda r: r.continue_() if r.request.url.startswith("file:") else r.abort())
    pg.goto("file://"+LOCAL); pg.wait_for_timeout(300)
    pg.evaluate("""()=>{window.fetch=(u,o)=>new Promise((res,rej)=>{const t=setTimeout(()=>res({ok:true,status:200,json:()=>Promise.resolve({type:"FeatureCollection",features:[]})}),2500); if(o&&o.signal) o.signal.addEventListener('abort',()=>{clearTimeout(t);const e=new Error('a');e.name='AbortError';rej(e)})}); inspect(L.latLng(45.84,15.97));}""")
    pg.wait_for_timeout(600); res["slow_busy"]=pg.evaluate("document.body.classList.contains('net-busy')"); res["slow_spinner"]=pg.evaluate("!!document.querySelector('#sheet .spin')")
    pg.screenshot(path=OUT+"/m_slow1.png")
    pg.wait_for_timeout(9000); res["slow_done"]=pg.evaluate("document.getElementById('sheet').textContent.slice(0,120)"); res["slow_busy_after"]=pg.evaluate("document.body.classList.contains('net-busy')")
    pg.close()
    # 5) više slojeva odjednom; svaki prekidač mora biti dostupan dodirom i kad je panel na pola zaslona (pogreška se ne skriva:
    #    provjerava se element na mjestu prekidača i stvarni dodir; dodir kroz panel ne prolazi)
    nedostupni=[]
    for (vw,vh,st) in ((390,844,"half"),(320,568,"half"),(390,844,"peek"),(360,640,"half")):
        pg=page(b,vw,vh); pg.evaluate(SETUP); pg.evaluate(f"setState('{st}')"); pg.wait_for_timeout(300)
        pg.tap("#lyrBtn"); pg.wait_for_timeout(200)
        ids=pg.evaluate("[...document.querySelectorAll('#lyrList input[type=checkbox]')].map(e=>e.id)")
        for i in ids:
            pg.evaluate(f"document.getElementById('{i}').scrollIntoView({{block:'nearest'}})"); pg.wait_for_timeout(50)
            pokriva=pg.evaluate(f"""()=>{{const e=document.getElementById('{i}'), r=e.getBoundingClientRect(), t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
              return !t?'izvan zaslona':t===e||t.closest('label')===e.closest('label')?null:(t.closest('#panel')?'panel':t.closest('#tabs')?'navigacija':(t.id||t.tagName))}}""")
            if pokriva: nedostupni.append(f"{vw}x{vh} {st} {i}: pokriva {pokriva}"); continue
            prije=pg.evaluate(f"document.getElementById('{i}').checked")
            try: pg.tap("#"+i, timeout=3000)
            except Exception as ex: nedostupni.append(f"{vw}x{vh} {st} {i}: dodir nije uspio ({str(ex).splitlines()[0][:80]})"); continue
            pg.wait_for_timeout(80)
            if pg.evaluate(f"document.getElementById('{i}').checked")==prije: nedostupni.append(f"{vw}x{vh} {st} {i}: dodir nije promijenio stanje")
        if (vw,vh,st)==(390,844,"half"): pg.screenshot(path=OUT+"/m_layers.png")
        res[f"layers_{vw}x{vh}_{st}_errors"]=pg.evaluate("window.__err||0"); pg.close()
    res["layers_nedostupni"]=nedostupni
    # 6) ispis u PDF s mobitela
    pg=page(b,390,844); pg.evaluate(SETUP); pg.emulate_media(media="print")
    vis=pg.evaluate("""()=>({tabs:getComputedStyle(document.getElementById('tabs')).display, troskovi:(e=>e?getComputedStyle(e).display:'nema odjeljka')(document.querySelector('.grp[data-g=troskovi]')||document.querySelector('details.izb.izb-tr')), grab:getComputedStyle(document.getElementById('grab')).display})""")
    res["print"]=vis
    pg.pdf(path=OUT+"/m_print.pdf",format="A4",print_background=True); pg.close()
    b.close()
print(json.dumps(res,ensure_ascii=False,indent=1))
if res.get("layers_nedostupni"):
    print("PALO: prekidači slojeva nisu dostupni dodirom:\n - "+"\n - ".join(res["layers_nedostupni"])); sys.exit(1)
print("INTERAKCIJA: svi prekidači slojeva dostupni dodirom")

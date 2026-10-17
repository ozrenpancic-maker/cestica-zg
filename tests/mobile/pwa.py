# Automatske provjere Android PWA-a u Chromiumu (Playwright + Chrome DevTools Protocol).
# Pokretanje: cd tests && python3 mobile/pwa.py
# Aplikacija se poslužuje lokalno na http://localhost:8123/cestica-zg/ (ista podmapa kao na GitHub Pagesu);
# localhost je za preglednik sigurno podrijetlo, pa service worker i instalabilnost rade kao na HTTPS-u.
# Knjižnice s CDN-a poslužuju se iz tests/node_modules; gradski GIS servisi i karte su blokirani (testira se aplikacija, ne mreža).
import os, sys, json, shutil, tempfile, threading, functools, http.server, socketserver, re
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..")); NM = os.path.join(REPO, "tests", "node_modules")
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
PORT = int(os.environ.get("PWA_PORT", "8123")); BASE = f"http://localhost:{PORT}/cestica-zg/"
res = []
def ok(c, name): res.append((bool(c), name)); print(("  ✓ " if c else "  ✗ ") + name)

# kopija aplikacije u privremenu mapu (test ažuriranja mijenja datoteke)
root = tempfile.mkdtemp(); app = os.path.join(root, "cestica-zg"); os.makedirs(app)
for f in ["index.html", "sw.js", "manifest.webmanifest", "icon.svg"]: shutil.copy(os.path.join(REPO, f), app)
shutil.copytree(os.path.join(REPO, "icons"), os.path.join(app, "icons")); shutil.copytree(os.path.join(REPO, "vendor"), os.path.join(app, "vendor"))
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self): self.send_header("Cache-Control", "max-age=600"); super().end_headers()  # kao GitHub Pages
H.extensions_map[".webmanifest"] = "application/manifest+json"
socketserver.ThreadingTCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), functools.partial(H, directory=root)); srv.daemon_threads = True
threading.Thread(target=srv.serve_forever, daemon=True).start()

LIBS = {"leaflet.min.js": "leaflet/dist/leaflet.js", "leaflet.min.css": "leaflet/dist/leaflet.css", "turf.min.js": "@turf/turf/turf.min.js"}
def route(r):
    u = r.request.url
    if u.startswith(f"http://localhost:{PORT}/"): return r.continue_()
    return r.abort()
SETUP = open(os.path.join(HERE, "layout.py"), encoding="utf-8").read().split('SETUP=r"""')[1].split('"""')[0]

with sync_playwright() as p:
    prof = tempfile.mkdtemp()  # trajni profil: u anonimnom načinu Chrome ne nudi instalaciju
    ctx = p.chromium.launch_persistent_context(prof, executable_path=CHROME, viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True, service_workers="allow",
                        user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Mobile Safari/537.36")
    ctx.route("**/*", route)
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(BASE); pg.wait_for_timeout(800)
    cdp = ctx.new_cdp_session(pg)

    print("1. Manifest i instalacija (Chrome DevTools)")
    man = cdp.send("Page.getAppManifest"); parsed = json.loads(man.get("data") or "{}")
    ok(man.get("url", "").endswith("/cestica-zg/manifest.webmanifest") and not man.get("errors"), "manifest se učitava bez grešaka: " + json.dumps(man.get("errors")))
    ok(parsed.get("name") == "ČesticaZG" and parsed.get("display") == "standalone", "naziv ČesticaZG, prikaz standalone (bez adresne trake)")
    sizes = {(i["sizes"], i.get("purpose", "any")) for i in parsed.get("icons", [])}
    ok(("192x192", "any") in sizes and ("512x512", "any") in sizes and ("512x512", "maskable") in sizes, "ikone 192, 512 i maskable")
    try: idd = cdp.send("Page.getAppId"); ok(idd.get("appId", "").startswith(BASE), "id aplikacije unutar /cestica-zg/: " + str(idd.get("appId")))
    except Exception as e: ok(False, "Page.getAppId: " + str(e))
    pg.reload(); pg.wait_for_timeout(1500)
    inst = cdp.send("Page.getInstallabilityErrors")
    ok(inst.get("installabilityErrors") == [], "Chrome ne prijavljuje prepreke za instalaciju: " + json.dumps(inst.get("installabilityErrors")))
    for ic in ["icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-512.png"]:
        r = pg.request.get(BASE + ic); ok(r.ok and r.headers.get("content-type", "").startswith("image/png"), f"{ic} dostupna")

    print("2. Service worker")
    sw = pg.evaluate("""async()=>{const r=await navigator.serviceWorker.getRegistration(); return r?{scope:r.scope,active:!!r.active,ctl:!!navigator.serviceWorker.controller}:null}""")
    ok(sw and sw["scope"] == BASE and sw["active"] and sw["ctl"], "registriran za /cestica-zg/, aktivan i upravlja stranicom: " + str(sw))
    cached = pg.evaluate("""async()=>{const out={}; for(const k of await caches.keys()){const c=await caches.open(k); out[k]=(await c.keys()).map(r=>r.url)} return out}""")
    shell = [v for k, v in cached.items() if k.startswith("czg-ljuska-")]
    allc = sum(cached.values(), [])
    ok(shell and any(u.endswith("/cestica-zg/index.html") for u in shell[0]) and any("vendor/leaflet-1.9.4/leaflet.js" in u for u in shell[0]) and any("turf.min.js" in u for u in shell[0]), "spremljena ljuska: stranica, ikone, Leaflet, Turf")
    ok(not any(("arcgis" in u or "openstreetmap" in u or "open-meteo" in u or "workers.dev" in u) for u in allc), "službeni i mrežni podaci se ne spremaju")

    # podaci korisnika za provjeru offline prikaza i ažuriranja
    pg.evaluate(SETUP); pg.wait_for_timeout(400)
    pg.evaluate("""()=>{saveCurrent(); const k=window.__cur.key; scSave(k,[{id:"s1",name:"Prizemnica 120",inp:scClean({...finInputs(),hA:120,fl:"P"}),created:"2026-10-17"}]); projPut(k,"kd",{zone:"I",rate:18.35});}""")
    keep = pg.evaluate("""()=>({favs:localStorage.getItem("favs"),scen:localStorage.getItem("scen"),proj:localStorage.getItem("proj")})""")

    print("3. Bez interneta")
    ctx.set_offline(True); pg.reload(); pg.wait_for_timeout(1500)
    ok(pg.title() and pg.locator("#map").count() == 1, "aplikacija se pokreće bez interneta")
    ok(pg.locator("#netState").is_visible() and "ne mogu se dohvatiti" in pg.locator("#netState").inner_text(), "jasna oznaka: službeni podaci se ne mogu osvježiti")
    pg.evaluate("inspect(L.latLng(45.84,15.97))"); pg.wait_for_timeout(300)
    ok("nema interneta" in pg.locator("#sheet").inner_text().lower() and "stare podatke" in pg.locator("#sheet").inner_text(), "dodir na kartu bez interneta: objašnjenje, bez starih podataka")
    pg.click('#tabs button[data-tab=spremljeno]'); pg.wait_for_timeout(300)
    t = pg.locator("#aux").inner_text()
    ok("3101/2" in t and "Prizemnica 120" in t and "€" in t, "spremljene čestice i scenariji (s iznosima) vidljivi bez interneta")
    ctx.set_offline(False); pg.wait_for_timeout(300)
    ok(not pg.locator("#netState").is_visible(), "povratak veze skriva oznaku")

    print("4. Ažuriranje na novu verziju")
    pg.goto(BASE); pg.wait_for_timeout(1200)
    old_ver = re.search(r'const VERSION = "([^"]+)"', open(os.path.join(app, "sw.js")).read()).group(1)
    for f, fn in [("index.html", lambda s: s.replace("</body>", "<!--nova-verzija-test--></body>")), ("sw.js", lambda s: s.replace(old_ver, "novaverzija1"))]:
        pth = os.path.join(app, f); txt = open(pth, encoding="utf-8").read(); open(pth, "w", encoding="utf-8").write(fn(txt))
    pg.evaluate("PWA.reg.update()"); pg.wait_for_selector("#updBar:not([hidden])", timeout=8000)
    ok(pg.locator("#updBar").is_visible() and "nova verzija" in pg.locator("#updBar").inner_text(), "obavijest 'Dostupna je nova verzija' (bez automatskog prekida rada)")
    with pg.expect_navigation(timeout=10000): pg.click("#updYes")
    pg.wait_for_timeout(1500)
    ok("nova-verzija-test" in pg.content(), "nakon potvrde učitana je nova verzija")
    ver_now = pg.evaluate("""async()=>(await caches.keys()).filter(k=>k.startsWith("czg-ljuska-"))""")
    ok(ver_now == ["czg-ljuska-novaverzija1"], "stari spremnik obrisan, aktivna nova verzija: " + str(ver_now))
    now = pg.evaluate("""()=>({favs:localStorage.getItem("favs"),scen:localStorage.getItem("scen"),proj:localStorage.getItem("proj")})""")
    ok(now["favs"] == keep["favs"] and now["scen"] == keep["scen"] and json.loads(now["proj"]).keys() == json.loads(keep["proj"]).keys(), "ažuriranje ne briše spremljene čestice, scenarije ni unose")

    print("5. Tipka Natrag (Android)")
    # dalje se testira bez automatskog ponovnog otvaranja zadnje čestice (ono je provjereno u koraku 8)
    pg.add_init_script("try{sessionStorage.removeItem('czgNastavak');localStorage.removeItem('zadnjaCestica')}catch(e){}")
    pg.goto(BASE + "?bez-nastavka"); pg.wait_for_timeout(900)
    pg.evaluate(SETUP); pg.wait_for_timeout(500)
    st = lambda: pg.evaluate("UI.state")
    ok(st() in ("half", "peek"), "čestica otvorena, panel: " + st())
    pg.evaluate("setState('full')"); pg.wait_for_timeout(200)
    pg.go_back(); pg.wait_for_timeout(300); ok(st() == "half" and pg.url.startswith(BASE), "Natrag: cijeli panel → pola, aplikacija ostaje otvorena")
    pg.go_back(); pg.wait_for_timeout(300); ok(st() == "peek", "Natrag: pola → sažetak (karta)")
    pg.click('#tabs button[data-tab=spremljeno]'); pg.wait_for_timeout(300); ok(pg.locator("#aux").is_visible(), "otvorene spremljene čestice")
    pg.go_back(); pg.wait_for_timeout(300); ok(not pg.locator("#aux").is_visible() and pg.url.startswith(BASE), "Natrag zatvara spremljene čestice")
    pg.click("#menuBtn"); pg.wait_for_timeout(150); pg.go_back(); pg.wait_for_timeout(300)
    ok(pg.locator("#menu").is_hidden(), "Natrag zatvara izbornik")
    pg.evaluate("setTab('karta')"); pg.wait_for_timeout(300)
    ok(pg.evaluate("history.state&&history.state.czg") == "osnova" and not pg.evaluate("PWA.guard"), "na osnovnom prikazu nema dodatnog koraka (Natrag izlazi iz aplikacije)")
    ok(pg.evaluate("!!window.__cur&&!!document.getElementById('bArea')") , "odabrana čestica i unosi ostaju nakon navigacije")

    print("6. Lokacija na terenu")
    ctx.grant_permissions(["geolocation"], origin=f"http://localhost:{PORT}")
    pg.evaluate("()=>{window.__inspected=null; window.inspect=ll=>{window.__inspected=[ll.lat,ll.lng]}}")
    mv0 = pg.evaluate("localStorage.getItem('mapv')")
    ctx.set_geolocation({"latitude": 45.8150, "longitude": 15.9819, "accuracy": 45})
    pg.click("#me"); pg.wait_for_timeout(800)
    s = pg.locator("#sheet").inner_text()
    ok("±45 m" in s and "ne može pouzdano" in s and pg.evaluate("window.__inspected") is None, "preciznost ±45 m: lokacija prikazana, čestica se NE odabire automatski")
    mv1 = pg.evaluate("localStorage.getItem('mapv')")
    ok(mv1 == mv0 and "45.815" not in (mv1 or ""), "GPS lokacija se ne sprema u pohranu preglednika")
    ok(pg.evaluate("Object.keys(localStorage).every(k=>!/45\\.815|15\\.981/.test(localStorage.getItem(k)||''))"), "nijedna spremljena vrijednost ne sadrži GPS koordinate")
    pg.click("#gpsUse"); pg.wait_for_timeout(200); ok(pg.evaluate("window.__inspected") == [45.815, 15.9819], "korisnik može sam odabrati česticu u središtu kruga")
    pg.evaluate("window.__inspected=null"); ctx.set_geolocation({"latitude": 45.8151, "longitude": 15.9820, "accuracy": 6})
    pg.click("#me"); pg.wait_for_timeout(800)
    ok(pg.evaluate("window.__inspected") == [45.8151, 15.982], "preciznost ±6 m: čestica na lokaciji se otvara")
    ok(pg.evaluate("document.getElementById('me').getAttribute('aria-label')") == "Prikaži moju lokaciju", "gumb 'Prikaži moju lokaciju'")

    print("7. Tipkovnica i zasloni")
    pg.goto(BASE + "?bez-nastavka"); pg.wait_for_timeout(900); pg.evaluate(SETUP); pg.wait_for_timeout(400)
    pg.click('#tabs button[data-tab=troskovi]'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelector('details[data-k=build]').open=true"); pg.wait_for_timeout(150)
    pg.tap("#bArea"); pg.set_viewport_size({"width": 390, "height": 430}); pg.wait_for_timeout(700)  # tipkovnica smanji vidljivi dio
    r = pg.evaluate("(()=>{const b=document.getElementById('bArea').getBoundingClientRect(); return [b.top,b.bottom,innerHeight,document.activeElement.id]})()")
    ok(r[3] == "bArea" and r[0] >= 0 and r[1] <= r[2], f"polje za unos ostaje vidljivo iznad tipkovnice: {r}")
    pg.set_viewport_size({"width": 390, "height": 844})
    for w, h in [(320, 640), (360, 740), (412, 915), (480, 900)]:
        pg.set_viewport_size({"width": w, "height": h}); pg.wait_for_timeout(250)
        sw_ = pg.evaluate("document.documentElement.scrollWidth")
        small = pg.evaluate("""()=>[...document.querySelectorAll('#tabs button,header .ib,#lyrBtn,#me,.pwabar .ib')].filter(e=>e.offsetParent).filter(e=>{const r=e.getBoundingClientRect();return r.width<40||r.height<40}).length""")
        ok(sw_ == w and small == 0, f"{w}×{h}: bez vodoravnog pomicanja, dodirni ciljevi dovoljno veliki")
    print("8. Nastavak nakon ponovnog pokretanja")
    pg2 = ctx.new_page(); pg2.goto(BASE); pg2.wait_for_timeout(700); pg2.evaluate(SETUP); pg2.wait_for_timeout(300)
    pg2.evaluate("pwaSaveState()"); saved = pg2.evaluate("JSON.parse(sessionStorage.getItem('czgNastavak'))"); z = pg2.evaluate("JSON.parse(localStorage.getItem('zadnjaCestica'))")
    inside = pg2.evaluate("(p)=>turf.booleanPointInPolygon(turf.point([p[1],p[0]]),window.__lastData.parcel)", saved["ll"])
    ok(saved and saved["tab"] and inside and z and z["ll"] == saved["ll"], "zadnja čestica pamti se kao točka unutar čestice (ne sirova lokacija), s karticom i stanjem panela")
    pg2.evaluate("()=>{window.__opened=null; window.inspect=ll=>{window.__opened=[ll.lat,ll.lng]; return Promise.resolve()}}")
    pg2.evaluate("window.__cur=null; clickId=0")
    pg2.reload(); pg2.wait_for_timeout(200); pg2.evaluate("()=>{window.__opened=null; window.inspect=ll=>{window.__opened=[ll.lat,ll.lng]; return Promise.resolve()}}"); pg2.wait_for_timeout(700)
    ok(pg2.evaluate("window.__opened") == saved["ll"], "nakon ponovnog učitavanja otvara se ista čestica")
    pg2.close()
    ok(not errs, "bez JS grešaka: " + "; ".join(errs[:3]))
    ctx.close(); shutil.rmtree(prof, ignore_errors=True)
srv.shutdown(); shutil.rmtree(root)
n = sum(1 for c, _ in res if c); print(f"\nPWA: {n} prošlo, {len(res)-n} palo")
sys.exit(0 if n == len(res) else 1)

from playwright.sync_api import sync_playwright
JS=r"""
() => {
 const o=[15.97,45.84], dx=40/(111320*Math.cos(45.84*Math.PI/180)), dy=25/110540;
 const g={type:"Polygon",coordinates:[[[o[0],o[1]],[o[0]+dx,o[1]],[o[0]+dx,o[1]+dy],[o[0],o[1]+dy],[o[0],o[1]]]]};
 const parcel={type:"Feature",geometry:g,properties:{KATASTARSKA_CESTICA:"1/1",KATASTARSKA_OPCINA:"ŠESTINE",GRADSKA_CETVRT:"Podsljeme"}};
 const rows=[{p:{Analitika:"Stambena i mješovita",Namjena:"Stambena",Naziv_plana:"GUP Grada Zagreba"},share:1,geom:g}];
 const up={v:[{properties:{BROJ_UP:"2.2."}}]};
 const d={ll:{lat:45.84,lng:15.97},parcel,area:turf.area(g),rows,ces:{v:[parcel]},nam:{v:rows},up,upx:{v:[]},gn:{v:[]},checks:CHECKS.map(c=>({c,v:[]})),slope:null,zgrade:{v:{area:0,n:0,geoms:[]}}};
 d.envelope=buildEnvelope(parcel,rows,up);
 ["calc","build","kd","costs","buy","total","cklist"].forEach(k=>OPEN.add(k));
 render(d);
 const set=(id,v,ev="input")=>{const e=document.getElementById(id); if(e.type==="checkbox") e.checked=v; else e.value=v; e.dispatchEvent(new Event(ev,{bubbles:true}));};
 set("kdZone","II","change"); set("yPrice","120000"); set("yAgency","3"); set("yNotary","150"); set("yKapara","12000");
 return document.getElementById("sheet").scrollHeight;
}"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg=b.new_page(viewport={"width":390,"height":844},device_scale_factor=2)
    pg.route("**/*",lambda r: r.abort() if not r.request.url.startswith("file:") else r.continue_())
    pg.goto("file:///tmp/claude-0/preview_local.html")
    pg.wait_for_timeout(500)
    print(pg.evaluate(JS))
    for k,name in [("build","b"),("buy","buy"),("total","tot"),("cklist","ck")]:
        el=pg.locator(f'details[data-k="{k}"]')
        el.scroll_into_view_if_needed(); pg.evaluate("k=>{const s=document.getElementById(\"sheet\"); const e=document.querySelector(`details[data-k=\"${k}\"]`); s.scrollTop=e.offsetTop-10}",k); pg.screenshot(path=f"/tmp/claude-0/shot_{name}.png")
    print("overflow:",pg.evaluate("document.documentElement.scrollWidth"))
    b.close()

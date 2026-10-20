#!/usr/bin/env python3
"""Priprema tlocrta zgrada otoka Krka za 3D prikaz okoline u Čestica HR.
Izvor: DGU, digitalni katastarski plan (ATOM, po k.o.): datoteka nacini_uporabe_zgrada.gml (sloj ZGRADE), isti paketi kao za tools/katastar/pripremi_krk.py.
Katastar zna samo tlocrt i način uporabe zgrade, NE visinu ni oblik krova. Zato se visina PRETPOSTAVLJA prema vrsti zgrade (tablica VISINE) i crta se kao kvadar bez krova;
aplikacija to jasno označava kao ilustraciju.
Izlaz: data/zg3d_krk/index.json i data/zg3d_krk/t/<red>_<stup>.json, isti oblik kao tools/zg3d/pripremi_zg3d.py (decimetri od JZ kuta kvadrata, delta-kodirano).
Pokretanje: python3 -I tools/zg3d/pripremi_krk_zgrade.py <mapa s raspakiranim ko-<mb> mapama> [izlaz] [datum]   (lxml, pyproj, shapely)
"""
import sys, os, re, json, math, glob, shutil
from lxml import etree
from pyproj import Transformer
from shapely.geometry import Polygon
from shapely.strtree import STRtree
DLAT, DLON = 0.004, 0.006
PREDNOST = ["338427", "337285", "337269"]  # nove izmjere imaju prednost pred starima gdje se preklapaju
# pretpostavljena visina do vijenca (m) po šifri načina uporabe; None = ne crta se (podzemno)
VISINE = {"101": 6.5, "100": 6.5, "102": 6.5, "103": 7.0, "501": 5.5, "206": 7.0, "201": 7.0, "202": 9.0, "205": 6.0, "318": 8.0, "310": 10.0, "311": 4.0,
          "601": 3.5, "405": 3.0, "406": 3.0, "401": 2.8, "402": 2.6, "404": 2.8, "403": 2.8, "610": 3.0, "605": 3.0, "606": 3.0, "701": 2.5, "900": None, "902": None}
VIS_ZADANO = 5.0
G = "{http://www.opengis.net/gml}"; O = "{http://oss}"
T = Transformer.from_crs(3765, 4326, always_xy=True)
def ring_ll(txt):
    pts = [tuple(map(float, p.split(","))) for p in txt.split()]
    lon, lat = T.transform([p[0] for p in pts], [p[1] for p in pts]); return list(zip(lon, lat))
def main(ulaz, out="data/zg3d_krk", datum=""):
    B = {}  # id -> (mb, sifra, ring)
    for f in sorted(glob.glob(os.path.join(ulaz, "ko-*", "nacini_uporabe_zgrada.gml"))):
        mb = f.split("ko-")[-1].split(os.sep)[0]
        for _, el in etree.iterparse(f, tag=O + "ZGRADE"):
            zid = el.findtext(O + "ZGRADA_ID"); sif = el.findtext(O + "SIFRA_NACINA_UPORABE_ZGRADE") or ""
            co = el.find(".//" + G + "outerBoundaryIs//" + G + "coordinates")
            if zid and co is not None and zid not in B:
                try: B[zid] = (mb, sif, ring_ll(co.text))
                except Exception: pass
            el.clear()
    print("zgrada učitano", len(B))
    # preklapanje stare i nove izmjere: zgrada iz stare k.o. ispada ako se znatno preklapa sa zgradom iz k.o. s prednošću
    P = {k: Polygon(v[2]).buffer(0) for k, v in B.items()}
    pri = [k for k, v in B.items() if v[0] in PREDNOST]; tree = STRtree([P[k] for k in pri]); drop = set()
    for k, v in B.items():
        if v[0] in PREDNOST: continue
        for i in tree.query(P[k]):
            q = P[pri[i]]; a = P[k].intersection(q).area
            if a > 0.5 * min(P[k].area, q.area): drop.add(k); break
    print("izbačeno zbog preklapanja izmjera", len(drop))
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out + "/t"); tiles = {}; n = 0; sk = 0
    for k, (mb, sif, ring) in B.items():
        if k in drop: continue
        h = VISINE.get(sif, VIS_ZADANO)
        if h is None: sk += 1; continue
        pg = P[k].simplify(0.0000008)  # ~0,1 m
        if pg.is_empty or pg.geom_type != "Polygon" or pg.area * 1.2e10 < 4: sk += 1; continue  # < ~4 m2
        c = pg.centroid; ti, tj = math.floor(c.y / DLAT), math.floor(c.x / DLON); lat0, lon0 = ti * DLAT, tj * DLON
        kx = math.cos(math.radians(lat0 + DLAT / 2)) * 1113200; ky = 1105400
        pts = [(round((x - lon0) * kx), round((y - lat0) * ky)) for x, y in list(pg.exterior.coords)[:-1]]
        flat = []; px = py = 0
        for x, y in pts: flat += [x - px, y - py]; px, py = x, y
        tiles.setdefault((ti, tj), []).append(json.dumps([0, int(round(h * 10)), [flat], []], separators=(",", ":"))); n += 1
    tot = 0; keys = []
    for (ti, tj), recs in sorted(tiles.items()):
        kk = f"{ti}_{tj}"; keys.append(kk)
        js = '{"v":1,"lat0":%s,"lon0":%s,"b":[%s]}' % (json.dumps(ti * DLAT), json.dumps(tj * DLON), ",".join(recs)); open(f"{out}/t/{kk}.json", "w").write(js); tot += len(js)
    json.dump({"v": 1, "tip": "dkp", "izvor": "DGU, digitalni katastarski plan (zgrade)", "dlat": DLAT, "dlon": DLON, "jedinica": "dm", "preuzeto": datum, "kvadrati": keys, "zgrada": n,
               "visine": "pretpostavljene prema vrsti zgrade"}, open(out + "/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("zgrada", n, "preskočeno", sk, "kvadrata", len(keys), "MB", round(tot / 1e6, 1))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "data/zg3d_krk", sys.argv[3] if len(sys.argv) > 3 else "")

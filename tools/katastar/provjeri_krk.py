"""Provjera data/kat_krk prema izvornim GML datotekama DKP-a: za slučajne točke na otoku Krku čestica iz kvadrata
(dekodirana kao u aplikaciji, WGS84) mora biti ista kao čestica iz izvornih geometrija (HTRS96/TM).
Pokretanje: python3 tools/katastar/provjeri_krk.py --ulaz MAPA_S_RASPAKIRANIM_KO"""
import argparse, glob, json, os, random, math
from lxml import etree
from pyproj import Transformer
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
G = "{http://www.opengis.net/gml}"; O = "{http://oss}"
D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "kat_krk")
TW = Transformer.from_crs(3765, 4326, always_xy=True); TM = Transformer.from_crs(4326, 3765, always_xy=True)
ap = argparse.ArgumentParser(); ap.add_argument("--ulaz", required=True); ap.add_argument("--n", type=int, default=600); a = ap.parse_args()
idx = json.load(open(os.path.join(D, "index.json"))); PR = idx["prednost"]
src = []; meta = []
for d in sorted(glob.glob(os.path.join(a.ulaz, "ko-*"))):
    for _, f in etree.iterparse(os.path.join(d, "katastarske_cestice.gml"), tag=O + "CESTICE", huge_tree=True):
        for pg in f.find(O + "GEOM").iter(G + "Polygon"):
            rr = [[tuple(map(float, p.split(",")[:2])) for p in lr.find(G + "coordinates").text.split()] for lr in pg.iter(G + "LinearRing")]
            try: src.append(Polygon(rr[0], rr[1:])); meta.append((f.findtext(O + "MATICNI_BROJ_KO"), f.findtext(O + "BROJ_CESTICE"), float(f.findtext(O + "POVRSINA_GRAFICKA") or 0)))
            except Exception: pass
        f.clear()
tree = STRtree(src)
def pick(c):
    c.sort(key=lambda m: ((PR.index(m[0]) if m[0] in PR else 99), m[2])); return c[0][:2] if c else None
def from_src(e, n):
    p = Point(e, n); return pick([meta[i] for i in tree.query(p) if src[i].contains(p)])
def ring(r):
    x = y = 0; out = []
    for i in range(0, len(r), 2): x += r[i]; y += r[i + 1]; out.append((x / 1e6, y / 1e6))
    return out
cache = {}
def from_tiles(lon, lat):
    k = f"{math.floor(lat/idx['dlat'])}_{math.floor(lon/idx['dlon'])}"
    if k not in cache:
        f = os.path.join(D, k + ".json"); cache[k] = json.load(open(f)) if os.path.exists(f) else []
    p = Point(lon, lat); c = []
    for cid, broj, ko, pov, P in cache[k]:
        for pr in P:
            rr = [ring(r) for r in pr]
            if Polygon(rr[0], rr[1:]).contains(p): c.append((ko, broj, pov or 0)); break
    return pick(c)
random.seed(7); ok = diff = none = 0; near = 0; ex = []
xmin, ymin, xmax, ymax = (min(s.bounds[0] for s in src), min(s.bounds[1] for s in src), max(s.bounds[2] for s in src), max(s.bounds[3] for s in src))
tested = 0
while tested < a.n:
    e = random.uniform(xmin, xmax); n = random.uniform(ymin, ymax)
    s = from_src(e, n)
    if s is None: continue
    tested += 1; lon, lat = TW.transform(e, n); t = from_tiles(lon, lat)
    if t == s: ok += 1
    else:
        dist = min(src[i].exterior.distance(Point(e, n)) for i in tree.query(Point(e, n).buffer(1)))
        if dist < 0.3: near += 1
        else: diff += 1; ex.append((s, t, round(dist, 2)))
res = {"tocke": tested, "iste": ok, "razlicito_uz_rub_do_0_3_m": near, "razlicito": diff, "primjeri": ex[:5]}
print(json.dumps(res, ensure_ascii=False))
json.dump(res, open(os.path.join(os.path.dirname(__file__), "provjera-krk-rezultat.json"), "w"), ensure_ascii=False, indent=1)

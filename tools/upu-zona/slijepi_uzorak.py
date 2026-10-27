#!/usr/bin/env python3
"""Drugi, slijepi uzorak čestica UPU-a 2 Kornić za završnu provjeru prijedloga zone (nakon što su pragovi i izbor
prostora boja određeni na prvom uzorku). Isti postupak kao referentni_uzorak.json, drugo sjeme, bez čestica iz prvog uzorka.
  python3 tools/upu-zona/slijepi_uzorak.py > tools/upu-zona/slijepi_uzorak.json"""
import json, os, random, sys
from shapely.geometry import shape, Polygon
from pyproj import Transformer
R = os.path.join(os.path.dirname(__file__), "..", "..")
ob = shape(json.load(open(os.path.join(os.path.dirname(__file__), "upu2_obuhvat_pgz_2026-10-27.geojson")))["features"][0]["geometry"])
prvi = {c["id"] for c in json.load(open(os.path.join(os.path.dirname(__file__), "referentni_uzorak.json")))["cestice"]}
tm = Transformer.from_crs(4326, 3765, always_xy=True)
def ring(r):
    out = []; x = y = 0
    for i in range(0, len(r), 2): x += r[i]; y += r[i + 1]; out.append((x / 1e6, y / 1e6))
    return out
kand = {}
minx, miny, maxx, maxy = ob.bounds
for f in os.listdir(os.path.join(R, "data/kat_krk")):
    if not f[0].isdigit(): continue
    for pid, broj, ko, pov, P in json.load(open(os.path.join(R, "data/kat_krk", f))):
        if ko != "315907" or pid in prvi or pid in kand or len(P) != 1: continue
        g = Polygon(ring(P[0][0]))
        if not g.is_valid or not ob.contains(g.representative_point()): continue
        r3 = [tm.transform(x, y) for x, y in g.exterior.coords]; a = Polygon(r3).area
        if 150 <= a <= 4000: kand[pid] = {"id": pid, "broj": broj, "ko": "KORNIĆ", "povrsina": round(a, 2), "prsten3765": [[round(x, 2), round(y, 2)] for x, y in r3]}
ids = sorted(kand); random.Random(20261028).shuffle(ids)
json.dump({"opis": "Slijepi uzorak čestica UPU-a 2 Kornić (slučajni odabir, sjeme 20261028, površina 150–4000 m², bez čestica referentnog uzorka) za završnu provjeru; kandidata ukupno " + str(len(ids)),
           "izvor_katastra": "data/kat_krk (DGU ATOM, 19. 10. 2026.)", "cestice": [kand[i] for i in ids[:40]]}, sys.stdout, ensure_ascii=False, indent=0)

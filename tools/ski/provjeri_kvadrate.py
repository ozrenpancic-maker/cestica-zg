"""Provjera pripremljenih kvadrata: udaljenost do najbližeg voda iz kvadrata (kako je računa aplikacija) naspram izvornih
podataka bez pojednostavljenja. Treba datoteku vodovi.pkl iz ski_provjera.py. Pokretanje: python3 tools/ski/provjeri_kvadrate.py"""
import json, math, os, pickle, random
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ski"); idx = json.load(open(os.path.join(D, "index.json")))
TM = Transformer.from_crs(4326, 3765, always_xy=True)
src = pickle.load(open("/tmp/claude-0/infra/vodovi.pkl", "rb"))
random.seed(7); R = 500
for net in ("vodovod", "kanalizacija", "struja"):
    g, m = src[net]; ref = [wkb.loads(b) for b, x in zip(g, m) if x.get("st") == "functional" and (net != "struja" or x.get("v") == "Niski napon")]; tr = STRtree(ref)
    have = set(idx["mreze"][net]["kvadrati"]); diffs = []; agree = 0; N = 300
    for _ in range(N):
        la = random.uniform(45.70, 45.90); lo = random.uniform(15.85, 16.15); x, y = TM.transform(lo, la); p = Point(x, y)
        dref = ref[tr.nearest(p)].distance(p)
        # kao aplikacija: kvadrati koji pokrivaju krug od 500 m
        i0, i1 = math.floor((la - R / 111000) / idx["dlat"]), math.floor((la + R / 111000) / idx["dlat"])
        j0, j1 = math.floor((lo - R / 77700) / idx["dlon"]), math.floor((lo + R / 77700) / idx["dlon"])
        best = None; seen = set()
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                k = f"{i}_{j}"
                if k not in have: continue
                for lid, flat in json.load(open(os.path.join(D, net, k + ".json"))):
                    if lid in seen: continue
                    seen.add(lid); xs, ys = TM.transform([v / 1e6 for v in flat[0::2]], [v / 1e6 for v in flat[1::2]])
                    d = LineString(list(zip(xs, ys))).distance(p) if len(xs) > 1 else Point(xs[0], ys[0]).distance(p)
                    best = d if best is None or d < best else best
        if dref <= R:
            if best is not None: diffs.append(abs(best - dref))
        else:
            agree += (best is None or best > R)
    diffs.sort(); q = lambda f: diffs[int(f * (len(diffs) - 1))] if diffs else float("nan")
    print(f"{net}: {len(diffs)} točaka s vodom u 500 m: razlika medijan {q(.5):.2f} m, 99 % {q(.99):.2f} m, najviše {max(diffs):.2f} m; "
          f"bez voda u 500 m: {agree}/{N-len(diffs)} se slažu")

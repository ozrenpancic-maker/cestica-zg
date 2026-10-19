"""Provjera kvadrata za otok Krk (data/ski_krk) prema izvornim INSPIRE GML datotekama _08, bez pojednostavljenja.
1) udaljenost do najbližeg voda iz kvadrata (kao u aplikaciji) naspram izvornih geometrija, za slučajne točke na otoku;
2) unutarnja usklađenost: objekti na mreži (Appurtenance) prema svom vodu.
Pokretanje: python3 tools/ski/provjeri_krk.py --vodovod DIR --kanalizacija DIR --struja DIR
(DIR = raspakirana datoteka INSPIRE_*_08.zip s UtilityLink.gml, *Pipe.gml i Appurtenance.gml)"""
import argparse, json, math, os, random, sys
from lxml import etree
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
sys.path.insert(0, os.path.dirname(__file__))
from pripremi_kvadrate import u_krk, pipes, stream

D = os.path.join(os.path.dirname(__file__), "..", "..", "data", "ski_krk"); idx = json.load(open(os.path.join(D, "index.json")))
T_TM = Transformer.from_crs(3035, 3765)                 # (N,E) 3035 → (E,N) 3765
T_W = Transformer.from_crs(3765, 4326, always_xy=True)
TM = Transformer.from_crs(4326, 3765, always_xy=True)
PIPE = {"vodovod": "WaterPipe.gml", "kanalizacija": "SewerPipe.gml", "struja": "ElectricityPipe.gml"}

def ref_lines(d, net):
    keep = pipes(os.path.join(d, PIPE[net]), "Niski napon" if net == "struja" else None); out = []
    for el in stream(os.path.join(d, "UtilityLink.gml"), "{*}UtilityLink"):
        if el.get("{http://www.opengis.net/gml/3.2}id") not in keep: continue
        pl = el.find(".//{*}posList")
        if pl is None: continue
        v = list(map(float, pl.text.split())); e, n = T_TM.transform(v[0::2], v[1::2])
        lon, lat = T_W.transform(e, n)
        if not any(u_krk(a, b) for a, b in zip(lon, lat)): continue
        out.append(LineString(list(zip(e, n))))
    return out

def appurtenances(d):
    pts = []
    for el in stream(os.path.join(d, "Appurtenance.gml"), "{*}member"):
        pos = el.find(".//{*}pos")
        if pos is None: continue
        v = list(map(float, pos.text.split()))
        e, n = T_TM.transform(v[0], v[1]); lon, lat = T_W.transform(e, n)
        if u_krk(lon, lat): pts.append(Point(e, n))
    return pts

def app_dist(d, net, src, tr, n):
    random.seed(5); pts = appurtenances(d); smp = random.sample(pts, min(n, len(pts))) if pts else []
    ds = sorted(src[tr.nearest(p)].distance(p) for p in smp)
    q = lambda f: ds[int(f * (len(ds) - 1))] if ds else float("nan")
    return len(pts), q(.5), q(.9), q(.99)

def main():
    ap = argparse.ArgumentParser()
    for n in PIPE: ap.add_argument("--" + n, required=True)
    a = ap.parse_args(); R = 500; rez = {}
    for net in PIPE:
        d = getattr(a, net); src = ref_lines(d, net); tr = STRtree(src)
        have = set(idx["mreze"][net]["kvadrati"]); diffs = []; agree = 0; N = 600; random.seed(11); cnt = 0
        while cnt < N:
            if cnt % 2:  # polovica točaka uz mrežu (do 300 m od slučajnog voda), polovica slučajno na otoku
                c = random.choice(src).interpolate(random.random(), normalized=True); ang = random.uniform(0, 2 * math.pi); r = random.uniform(0, 300)
                x, y = c.x + r * math.cos(ang), c.y + r * math.sin(ang); lo, la = T_W.transform(x, y)
            else:
                la = random.uniform(44.90, 45.26); lo = random.uniform(14.42, 14.86); x, y = TM.transform(lo, la)
            if not u_krk(lo, la): continue
            cnt += 1; p = Point(x, y); dref = src[tr.nearest(p)].distance(p)
            i0, i1 = math.floor((la - R / 111000) / idx["dlat"]), math.floor((la + R / 111000) / idx["dlat"])
            j0, j1 = math.floor((lo - R / 78500) / idx["dlon"]), math.floor((lo + R / 78500) / idx["dlon"])
            best = None; seen = set()
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    k = f"{i}_{j}"
                    if k not in have: continue
                    for lid, flat in json.load(open(os.path.join(D, net, k + ".json"))):
                        if lid in seen: continue
                        seen.add(lid); xs, ys = TM.transform([v / 1e6 for v in flat[0::2]], [v / 1e6 for v in flat[1::2]])
                        dd = LineString(list(zip(xs, ys))).distance(p) if len(xs) > 1 else Point(xs[0], ys[0]).distance(p)
                        best = dd if best is None or dd < best else best
            if dref <= R:
                if best is not None: diffs.append(abs(best - dref))
            else:
                agree += (best is None or best > R)
        diffs.sort(); q = lambda f: diffs[int(f * (len(diffs) - 1))] if diffs else float("nan")
        na, a50, a90, a99 = app_dist(d, net, src, tr, 3000)
        rez[net] = {"tocke_s_vodom": len(diffs), "razlika_medijan_m": round(q(.5), 2), "razlika_99_m": round(q(.99), 2), "razlika_max_m": round(max(diffs), 2) if diffs else None,
                    "bez_voda_slazu": f"{agree}/{N - len(diffs)}", "objekti_na_mrezi": na, "objekti_do_voda_medijan_m": round(a50, 2), "objekti_90_m": round(a90, 2), "objekti_99_m": round(a99, 2)}
        print(net, json.dumps(rez[net], ensure_ascii=False), flush=True)
    json.dump(rez, open(os.path.join(os.path.dirname(__file__), "provjera-krk-rezultat.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()

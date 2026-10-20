#!/usr/bin/env python3
"""Priprema ZG3D (3D modeli postojećih zgrada, Grad Zagreb, Otvorena dozvola) za Čestica HR.
Ulaz: ESRI File Geodatabase (.gdb) jedne gradske četvrti (https://data.gov.hr, skup „ZG3D ... 3D model GZ”).
Izlaz: data/zg3d/index.json i data/zg3d/t/<red>_<stup>.json (kvadrati ~450 x 470 m).
Po zgradi se čuva samo geometrija (bez ikakvih atributa o osobama): tlocrt, visina do najnižeg dijela krova i krovne plohe.
Koordinate: decimetri od JZ kuta kvadrata (ravninska aproksimacija), delta-kodirano; visine relativno na najnižu točku zgrade.
Pokretanje: python3 -I tools/zg3d/pripremi_zg3d.py <put do .gdb> [izlazni direktorij]   (potrebni: pyogrio, shapely, numpy)
"""
import sys, os, json, math, warnings, shutil
warnings.filterwarnings("ignore")
import numpy as np, shapely, pyogrio
from shapely.geometry import Polygon
from shapely.ops import unary_union
DLAT, DLON = 0.004, 0.006
def main(gdb, out="data/zg3d"):
    layer = pyogrio.list_layers(gdb)[0][0]
    info = pyogrio.read_info(gdb, layer=layer); n = info["features"]
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out + "/t")
    tiles = {}; stat = {"zgrada": 0, "preskoceno": 0, "godine": {}, "plohe": 0}
    CH = 4000
    for s in range(0, n, CH):
        meta, fid, geom, fields = pyogrio.raw.read(gdb, layer=layer, skip_features=s, max_features=CH, return_fids=True)
        names = list(meta["fields"]); F = dict(zip(names, fields))
        G = shapely.from_wkb(geom, on_invalid="ignore")
        for i, g in enumerate(G):
            if g is None: stat["preskoceno"] += 1; continue
            parts = list(shapely.get_parts(g))
            c0 = shapely.get_coordinates(g)
            lon, lat = float(c0[:, 0].mean()), float(c0[:, 1].mean())
            ti, tj = math.floor(lat / DLAT), math.floor(lon / DLON)
            lat0, lon0 = ti * DLAT, tj * DLON
            kx = math.cos(math.radians(lat0 + DLAT / 2)) * 111320.0 * 10; ky = 110540.0 * 10  # decimetri po stupnju
            zmin = float(F["Z_Min"][i]) if "Z_Min" in F else None
            faces = []
            for pt in parts:
                c = shapely.get_coordinates(pt, include_z=True)
                if len(c) > 1 and np.allclose(c[0], c[-1]): c = c[:-1]
                if len(c) < 3: continue
                faces.append(c)
            if not faces: stat["preskoceno"] += 1; continue
            allz = np.concatenate([f[:, 2] for f in faces]); zmin = float(allz.min()) if zmin is None or not np.isfinite(zmin) else min(zmin, float(allz.min()))
            def loc(c): return np.column_stack([(c[:, 0] - lon0) * kx, (c[:, 1] - lat0) * ky, (c[:, 2] - zmin) * 10])
            roof = []
            for c in faces:
                L = loc(c); a2 = abs(shapely.area(Polygon(L[:, :2]))) / 100.0  # m2
                if a2 < 0.05: continue                      # okomiti zid
                if a2 < 0.8: continue                       # sitni detalji (dimnjaci, gaube): ne trebaju za okolne zgrade
                if L[:, 2].max() < 3.0: continue            # pod / dno (do 0,3 m iznad najniže točke)
                roof.append(L)
            if not roof: stat["preskoceno"] += 1; continue
            foot = unary_union([Polygon(L[:, :2]).buffer(0) for L in roof]).simplify(2.5)  # 0,25 m
            rings = []
            for p in (foot.geoms if hasattr(foot, "geoms") else [foot]):
                if p.is_empty or p.geom_type != "Polygon" or p.area < 30: continue  # < 0,3 m2 (dm2 = 0,01 m2) ... 30 dm2
                rings.append(np.round(np.array(p.exterior.coords)[:-1]).astype(int))
            if not rings: stat["preskoceno"] += 1; continue
            wall = int(round(min(L[:, 2].min() for L in roof)))
            fl = []
            for L in roof:
                Li = np.round(L).astype(int)
                if len(set(map(tuple, Li))) < 3: continue
                fl.append(Li)
            def enc(P):  # prva točka apsolutno, ostale delta
                P = np.asarray(P); d = np.vstack([P[:1], np.diff(P, axis=0)]); return d.flatten().tolist()
            y = F["Godina_izv"][i]
            try: y = int(y) % 100
            except Exception: y = 0
            rec = [y, wall, [enc(r) for r in rings], [enc(f) for f in fl]]
            tiles.setdefault((ti, tj), []).append(json.dumps(rec, separators=(",", ":")))  # kao tekst: manje memorije za cijeli grad
            stat["zgrada"] += 1; stat["plohe"] += len(fl); stat["godine"][str(y)] = stat["godine"].get(str(y), 0) + 1
        print(s + CH, "/", n, flush=True)
    keys = []; tot = 0
    for (ti, tj), recs in sorted(tiles.items()):
        k = f"{ti}_{tj}"; keys.append(k)
        js = '{"v":1,"lat0":%s,"lon0":%s,"b":[%s]}' % (json.dumps(ti * DLAT), json.dumps(tj * DLON), ",".join(recs))
        open(f"{out}/t/{k}.json", "w").write(js); tot += len(js)
    idx = {"v": 1, "izvor": "ZG3D 2022, 3D modeli postojećih zgrada (Grad Zagreb), Otvorena dozvola", "dlat": DLAT, "dlon": DLON, "jedinica": "dm",
           "podrucje": os.path.basename(gdb), "kvadrati": keys, "zgrada": stat["zgrada"], "godine": stat["godine"]}
    json.dump(idx, open(out + "/index.json", "w"), separators=(",", ":"), ensure_ascii=False)
    print(stat, "kvadrata", len(keys), "MB", round(tot / 1e6, 1))
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "data/zg3d")

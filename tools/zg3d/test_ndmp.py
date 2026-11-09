# sintetički test: dvije zgrade (dvostrešna 12x8 m, vijenac 6 m, sljeme 9 m, sljeme po duljoj strani; ravna 10x10 m, 7 m) i jedna bez zgrade u LiDAR-u
import sys, os, json, math, shutil, numpy as np, tifffile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import pripremi_ndmp as M
from pyproj import Transformer
T = Transformer.from_crs(3765, 4326, always_xy=True)
import tempfile; D = tempfile.mkdtemp(prefix="ndmp-"); shutil.rmtree(D + "/kv", ignore_errors=True); shutil.rmtree(D + "/nd", ignore_errors=True); os.makedirs(D + "/kv/t"); os.makedirs(D + "/nd")
E0, N0 = 350000.0, 4990000.0  # HTRS96/TM, Krk
W = H = 120; r = np.zeros((H, W), np.float32)
def ex(e, n): return int(e), int(H - n)  # lokalni metri -> piksel; središte gore-lijevo = (E0, N0+H)
# dvostrešna: e 20..32 (12 m, dulja os istok-zapad), n 40..48 -> sljeme n=44
for n in range(40, 49):
    for e in range(20, 33):
        c, rr = ex(e, n); r[rr, c] = 6 + 3 * (1 - abs(n - 44) / 4)
for n in range(70, 81):
    for e in range(60, 71):
        c, rr = ex(e, n); r[rr, c] = 7.0
tifffile.imwrite(D + "/nd/list1.tif", r); open(D + "/nd/list1.tfw", "w").write(f"1\n0\n0\n-1\n{E0}\n{N0+H}\n")
DL, DO = 0.004, 0.006
def foot(e0, n0, e1, n1):
    return [T.transform(E0 + x - 0.5, N0 + y - 0.5) for x, y in [(e0, n0), (e1 + 1, n0), (e1 + 1, n1 + 1), (e0, n1 + 1)]]
B = [foot(20, 40, 32, 48), foot(60, 70, 70, 80), foot(90, 10, 100, 20)]
lon, lat = B[0][0]; ti, tj = math.floor(lat / DL), math.floor(lon / DO); lat0, lon0 = ti * DL, tj * DO
kx = math.cos(math.radians(lat0 + DL / 2)) * 1113200; ky = 1105400
recs = []
for f in B:
    flat = []; px = py = 0
    for x, y in f:
        X, Y = round((x - lon0) * kx), round((y - lat0) * ky); flat += [X - px, Y - py]; px, py = X, Y
    recs.append([0, 65, [flat], []])
k = f"{ti}_{tj}"; json.dump({"v": 1, "lat0": lat0, "lon0": lon0, "b": recs}, open(D + f"/kv/t/{k}.json", "w"))
json.dump({"v": 1, "tip": "dkp", "izvor": "DGU katastar", "dlat": DL, "dlon": DO, "jedinica": "dm", "kvadrati": [k]}, open(D + "/kv/index.json", "w"))
st = M.main(D + "/kv", D + "/nd", D + "/izlaz", "2026-11-09")
t = json.load(open(D + f"/izlaz/t/{k}.json")); ix = json.load(open(D + "/izlaz/index.json"))
b0, b1, b2 = t["b"]
zs = []
for fa in b0[3]:
    z = 0
    for i in range(2, len(fa), 3): z += fa[i]; zs.append(z / 10)
assert ix["tip"] == "ndmp" and "u skladu s dozvolom" in ix["izvor"], ix
assert st == {"zgrada": 3, "izmjereno": 2, "kosi": 1, "ravni": 1, "bez": 1}, st
assert len(b0[3]) == 2 and abs(b0[1] / 10 - 6.0) <= 0.5 and abs(max(zs) - 9.0) <= 0.5 and min(zs) >= 5.5, (b0[1], zs)
assert all(abs(z * 2 - round(z * 2)) < 1e-6 for z in zs), "visine zaokružene na 0,5 m"
assert b1[3] == [] and b1[1] == 70, b1[1]
assert b2[1] == 65 and b2[3] == [], "bez LiDAR podataka ostaje pretpostavka"
print("ndmp OK", st, "dvostrešna vijenac", b0[1] / 10, "sljeme", max(zs))

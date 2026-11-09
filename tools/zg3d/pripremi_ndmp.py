#!/usr/bin/env python3
"""Stvarne visine i oblik krova zgrada iz LiDAR-a DGU-a (nDMP) za Čestica HR.

Ulaz:
  1. kvadrati zgrada koje je pripremio tools/zg3d/pripremi_krk_zgrade.py (tlocrti iz katastra DGU-a, visine pretpostavljene),
  2. mapa s listovima nDMP-a (normalizirani digitalni model površina, DGU / LIFE CROLIS, LiDAR 2021.–2023.): GeoTIFF (.tif)
     s pripadnom datotekom svijeta (.tfw), HTRS96/TM (EPSG:3765), 1 x 1 m, vrijednost = visina iznad tla u metrima.
Izlaz: isti oblik kvadrata (data/zg3d_krk/t/*.json) s izmjerenom visinom vijenca i krovnim plohama, index.json s tip "ndmp".

Po zgradi: pikseli nDMP-a unutar tlocrta. Ako je razlika 95. i 10. percentila manja od 0,8 m, krov je ravan (visina = medijan).
Inače se uspoređuju dvostrešni krov sa sljemenom po duljoj i po kraćoj stranici tlocrta (vijenac i visina krova metodom
najmanjih kvadrata) i bira se onaj koji bolje odgovara izmjerenim visinama (prosječno odstupanje). Ako ni jedan ne odgovara (odstupanje veće
od 1,2 m, npr. složen ili četverostrešni krov), ostaje ravan krov na izmjerenoj visini vijenca.

Uvjet dozvole DGU-a: kod javne objave točne visine pojedinih točaka ili objekata ne smiju se moći izravno očitati. Zato se sve
visine zaokružuju na 0,5 m i u aplikaciji se prikazuje samo 3D model zgrade, bez brojčanih visina.
Izvor u aplikaciji: „Sadrži informacije tijela javne vlasti u skladu s dozvolom” (DGU, nDMP, datum preuzimanja).

Pokretanje: python3 -I tools/zg3d/pripremi_ndmp.py <ulazni kvadrati, npr. data/zg3d_krk> <mapa s nDMP listovima> [izlaz] [datum preuzimanja]
Potrebno: numpy, shapely, pyproj, tifffile.
"""
import sys, os, json, math, glob, shutil
from collections import OrderedDict
import numpy as np, shapely, tifffile
from shapely.geometry import Polygon
from pyproj import Transformer

T_FWD = Transformer.from_crs(4326, 3765, always_xy=True)
T_INV = Transformer.from_crs(3765, 4326, always_xy=True)
KORAK = 0.5            # zaokruživanje visina (m), uvjet dozvole
RAVNO = 0.8            # manja razlika sljemena i vijenca: ravan krov
MAX_ODST = 1.2         # najveće prosječno odstupanje dvostrešnog krova od izmjerenog (m)


def zaokr(v):
    return round(v / KORAK) * KORAK


class Listovi:
    """Listovi nDMP-a: okviri iz .tfw, rasteri se učitavaju po potrebi (najviše 40 u memoriji)."""
    def __init__(self, mapa):
        self.L = []
        for tif in sorted(glob.glob(os.path.join(mapa, "**", "*.tif"), recursive=True)):
            tfw = os.path.splitext(tif)[0] + ".tfw"
            if not os.path.exists(tfw):
                continue
            A, D, B, E, C, F = [float(x) for x in open(tfw).read().split()[:6]]
            with tifffile.TiffFile(tif) as t:
                h, w = t.pages[0].shape[:2]
            # središte gornjeg lijevog piksela je (C, F); A = širina piksela, E = visina (negativna)
            self.L.append({"f": tif, "A": A, "E": E, "C": C, "F": F, "w": w, "h": h,
                           "bb": (C - A / 2, F + E * (h - 0.5), C + A * (w - 0.5), F - E / 2)})
        self.cache = OrderedDict()

    def raster(self, L):
        r = self.cache.get(L["f"])
        if r is None:
            r = tifffile.imread(L["f"]).astype(np.float32)
            self.cache[L["f"]] = r
            if len(self.cache) > 40:
                self.cache.popitem(last=False)
        else:
            self.cache.move_to_end(L["f"])
        return r

    def uzorci(self, pg):
        """visine piksela čije je središte unutar poligona (EPSG:3765) i njihove koordinate"""
        x0, y0, x1, y1 = pg.bounds
        X, Y, V = [], [], []
        for L in self.L:
            b = L["bb"]
            if b[2] < x0 or b[0] > x1 or b[3] < y0 or b[1] > y1:
                continue
            c0 = max(0, int(math.floor((x0 - L["C"]) / L["A"]))); c1 = min(L["w"] - 1, int(math.ceil((x1 - L["C"]) / L["A"])))
            r0 = max(0, int(math.floor((y1 - L["F"]) / L["E"]))); r1 = min(L["h"] - 1, int(math.ceil((y0 - L["F"]) / L["E"])))
            if c1 < c0 or r1 < r0:
                continue
            cc, rr = np.meshgrid(np.arange(c0, c1 + 1), np.arange(r0, r1 + 1))
            xs = L["C"] + cc * L["A"]; ys = L["F"] + rr * L["E"]
            m = shapely.contains_xy(pg, xs, ys)
            if not m.any():
                continue
            v = self.raster(L)[rr[m], cc[m]]
            X.append(xs[m]); Y.append(ys[m]); V.append(v)
        if not V:
            return None
        X, Y, V = np.concatenate(X), np.concatenate(Y), np.concatenate(V)
        ok = np.isfinite(V) & (V > -5) & (V < 300)
        return X[ok], Y[ok], V[ok]


def dvostresni(P, os_ridge, X, Y, V):
    """dvostrešni krov sa sljemenom kroz težište u smjeru os_ridge; vijenac i visina krova metodom najmanjih kvadrata.
    Vraća (prosječno odstupanje, vijenac, plohe u EPSG:3765 s visinama)"""
    c = np.array(Polygon(P).centroid.coords[0]); d = np.array(os_ridge); n = np.array([-d[1], d[0]])
    dist = lambda x, y: (x - c[0]) * n[0] + (y - c[1]) * n[1]
    dv = np.array([dist(x, y) for x, y in P]); dmax_p, dmax_n = max(dv.max(), 1e-6), max(-dv.min(), 1e-6)
    ds = dist(X, Y)
    t = np.where(ds >= 0, 1 - np.clip(ds / dmax_p, 0, 1), 1 - np.clip(-ds / dmax_n, 0, 1))
    A = np.vstack([np.ones_like(t), t]).T
    (eave, rise), *_ = np.linalg.lstsq(A, V, rcond=None)
    if rise <= 0:
        return 1e9, eave, []
    odst = float(np.mean(np.abs(eave + rise * t - V)))
    plohe = []
    for s, dm in ((1, dmax_p), (-1, dmax_n)):
        polu = Polygon([tuple(c + d * 1e4), tuple(c + d * 1e4 + n * s * 1e4), tuple(c - d * 1e4 + n * s * 1e4), tuple(c - d * 1e4)])
        pol = Polygon(P).buffer(0).intersection(polu)
        if pol.is_empty:
            continue
        geoms = [pol] if pol.geom_type == "Polygon" else [g for g in getattr(pol, "geoms", []) if g.geom_type == "Polygon"]
        for g in geoms:
            pts = list(g.exterior.coords)[:-1]
            plohe.append([(x, y, eave + rise * (1 - min(1, abs(dist(x, y)) / dm))) for x, y in pts])
    return odst, float(eave), plohe


def obradi(L, foot_ll, wall0):
    """vrati (vijenac, plohe u stupnjevima s visinom) ili None ako nema dovoljno podataka"""
    xs, ys = T_FWD.transform([q[0] for q in foot_ll], [q[1] for q in foot_ll])
    P = list(zip(xs, ys)); pg = Polygon(P).buffer(0)
    if pg.is_empty or pg.area < 8:
        return None
    u = L.uzorci(pg)
    if u is None or len(u[2]) < max(6, 0.4 * pg.area):
        return None
    X, Y, V = u
    ridge = float(np.percentile(V, 95)); nisko = float(np.percentile(V, 10))
    if float(np.median(V)) < 1.5:  # tlocrt bez zgrade u LiDAR-u (srušena, nova ili pogreška) - zadrži pretpostavku
        return None
    if ridge - nisko < RAVNO:
        return zaokr(float(np.median(V))), []
    # duža i kraća os tlocrta (najdulja stranica)
    best, d = 0, (1.0, 0.0)
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]; Ld = math.hypot(b[0] - a[0], b[1] - a[1])
        if Ld > best:
            best, d = Ld, ((b[0] - a[0]) / Ld, (b[1] - a[1]) / Ld)
    odst, eave, plohe = min([dvostresni(P, d, X, Y, V), dvostresni(P, (-d[1], d[0]), X, Y, V)], key=lambda k: k[0])
    if odst > MAX_ODST or not plohe or eave < 1.5:
        return zaokr(float(np.median(V))), []
    out = []
    for f in plohe:
        lon, lat = T_INV.transform([q[0] for q in f], [q[1] for q in f])
        out.append([(lo, la, zaokr(z)) for lo, la, (_, _, z) in zip(lon, lat, f)])
    return zaokr(eave), out


def main(ulaz, nmapa, out=None, datum=""):
    out = out or ulaz
    idx = json.load(open(os.path.join(ulaz, "index.json")))
    L = Listovi(nmapa)
    print("listova nDMP", len(L.L))
    DL, DO = idx["dlat"], idx["dlon"]
    st = {"zgrada": 0, "izmjereno": 0, "kosi": 0, "ravni": 0, "bez": 0}
    tmp = out + ".tmp"; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp + "/t")
    for k in idx["kvadrati"]:
        t = json.load(open(os.path.join(ulaz, "t", k + ".json")))
        lat0, lon0 = t["lat0"], t["lon0"]
        kx = math.cos(math.radians(lat0 + DL / 2)) * 1113200; ky = 1105400
        recs = []
        for r in t["b"]:
            st["zgrada"] += 1
            x = y = 0; foot = []
            a = r[2][0]
            for i in range(0, len(a) - 1, 2):
                x += a[i]; y += a[i + 1]; foot.append((lon0 + x / kx, lat0 + y / ky))
            res = obradi(L, foot, r[1] / 10) if L.L else None
            if res is None:
                st["bez"] += 1; recs.append(r); continue
            wall, plohe = res
            st["izmjereno"] += 1; st["kosi" if plohe else "ravni"] += 1
            F = []
            for f in plohe:
                flat = []; px = py = pz = 0
                for lo, la, z in f:
                    X_, Y_, Z_ = round((lo - lon0) * kx), round((la - lat0) * ky), int(round(z * 10))
                    flat += [X_ - px, Y_ - py, Z_ - pz]; px, py, pz = X_, Y_, Z_
                F.append(flat)
            recs.append([r[0], int(round(wall * 10)), r[2], F, 1])  # 5. polje 1 = visina i oblik krova izmjereni (ravan krov ostaje ravan)
        js = '{"v":1,"lat0":%s,"lon0":%s,"b":[%s]}' % (json.dumps(lat0), json.dumps(lon0), ",".join(json.dumps(x, separators=(",", ":")) for x in recs))
        open(f"{tmp}/t/{k}.json", "w").write(js)
    idx2 = dict(idx)
    idx2.update({"tip": "ndmp", "visine": "iz nDMP-a DGU-a (LiDAR 2021.–2023.), zaokruženo na 0,5 m; bez podataka: pretpostavljene",
                 "izvor": idx.get("izvor", "") + "; visine i krovovi: DGU, normalizirani digitalni model površina (LIFE CROLIS). Sadrži informacije tijela javne vlasti u skladu s dozvolom",
                 "ndmp_preuzet": datum, "izmjereno": st["izmjereno"]})
    json.dump(idx2, open(tmp + "/index.json", "w"), ensure_ascii=False, separators=(",", ":"))
    if os.path.abspath(out) == os.path.abspath(ulaz) or os.path.exists(out):
        shutil.rmtree(out)
    shutil.move(tmp, out)
    print(st)
    return st


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4] if len(sys.argv) > 4 else "")

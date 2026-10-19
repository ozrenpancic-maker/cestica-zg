"""Priprema katastarskih čestica za otok Krk iz DGU-ove usluge preuzimanja DKP-a (ATOM, po katastarskoj općini).

Izvor: https://oss.uredjenazemlja.hr/oss/public/atom/ko-<matični broj>.zip (GML, HTRS96/TM, EPSG:3765), tjedno osvježavanje;
katalog DGU-a: „nema uvjeta za pristup i korištenje”. Živi DGU WFS se ne koristi jer vraća ORA-01000 ili ne odgovara.

Korištenje (Python 3, pip install lxml pyproj):
  python3 tools/katastar/pripremi_krk.py --ulaz MAPA_S_RASPAKIRANIM_KO --datum 2026-10-19
  (MAPA/ko-315907/katastarske_cestice.gml, katastarske_opcine.gml, …)
Izlaz: data/kat_krk/index.json i data/kat_krk/<kvadrat>.json, isti kvadrati kao data/ski (0,009° × 0,013°).
Čestica: [id, "broj", matični broj KO, grafička površina m², poligoni]; poligon = [prsten, …], prsten = [lon0, lat0, dlon1, dlat1, …]
u milijuntinkama stupnja (oko 0,1 m), s razlikama od prethodne točke da datoteke budu manje.
Gdje se stara i nova izmjera preklapaju (npr. Omišalj i Omišalj-Njivice), aplikacija prednost daje novijoj k.o. (popis `prednost`).
"""
import argparse, glob, json, math, os, shutil, collections
from lxml import etree
from pyproj import Transformer

DLAT, DLON = 0.009, 0.013
G = "{http://www.opengis.net/gml}"; O = "{http://oss}"
T = Transformer.from_crs(3765, 4326, always_xy=True)
PREDNOST = ["338427", "337285", "337269"]  # nove izmjere: Omišalj-Njivice, Baška-Nova, Malinska-Dubašnica

def enc_ring(pts):
    lon, lat = T.transform([p[0] for p in pts], [p[1] for p in pts])
    q = [(round(a * 1e6), round(b * 1e6)) for a, b in zip(lon, lat)]
    out = [q[0][0], q[0][1]]
    for (x0, y0), (x1, y1) in zip(q, q[1:]): out += [x1 - x0, y1 - y0]
    return out, lon, lat

def polys(geom):
    for pg in geom.iter(G + "Polygon"):
        rr = []
        for lr in pg.iter(G + "LinearRing"):
            c = lr.find(G + "coordinates")
            rr.append([tuple(map(float, p.split(",")[:2])) for p in c.text.split()])
        if rr: yield rr

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ulaz", required=True); ap.add_argument("--datum", required=True)
    ap.add_argument("--izlaz", default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "kat_krk"))
    a = ap.parse_args(); out = os.path.abspath(a.izlaz)
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    tiles = collections.defaultdict(list); kos = {}; n = 0
    for d in sorted(glob.glob(os.path.join(a.ulaz, "ko-*"))):
        t = etree.parse(os.path.join(d, "katastarske_opcine.gml")); naziv = mb = None
        for e in t.getroot().iter():
            if e.tag == O + "NAZIV": naziv = e.text
            elif e.tag == O + "MATICNI_BROJ": mb = e.text
        cnt = 0
        for _, f in etree.iterparse(os.path.join(d, "katastarske_cestice.gml"), tag=O + "CESTICE", huge_tree=True):
            cid = int(f.findtext(O + "CESTICA_ID")); broj = f.findtext(O + "BROJ_CESTICE"); ko = f.findtext(O + "MATICNI_BROJ_KO") or mb
            pov = f.findtext(O + "POVRSINA_GRAFICKA"); pov = round(float(pov), 2) if pov else None
            P = []; x0 = y0 = 1e9; x1 = y1 = -1e9
            for rr in polys(f.find(O + "GEOM")):
                pr = []
                for ring in rr:
                    e, lon, lat = enc_ring(ring); pr.append(e)
                    x0 = min(x0, min(lon)); x1 = max(x1, max(lon)); y0 = min(y0, min(lat)); y1 = max(y1, max(lat))
                P.append(pr)
            f.clear()
            while f.getprevious() is not None: del f.getparent()[0]
            if not P: continue
            rec = [cid, broj, ko, pov, P]; cnt += 1; n += 1
            for i in range(math.floor(y0 / DLAT), math.floor(y1 / DLAT) + 1):
                for j in range(math.floor(x0 / DLON), math.floor(x1 / DLON) + 1): tiles[f"{i}_{j}"].append(rec)
        kos[mb] = {"naziv": naziv, "cestica": cnt}
        print(mb, naziv, cnt, flush=True)
    for k, arr in tiles.items():
        with open(os.path.join(out, k + ".json"), "w") as f: json.dump(arr, f, ensure_ascii=False, separators=(",", ":"))
    idx = {"v": 1, "podrucje": "krk", "izvor": "Državna geodetska uprava, digitalni katastarski plan (ATOM, oss.uredjenazemlja.hr)",
           "uvjeti": "katalog DGU-a: nema uvjeta za pristup i korištenje", "preuzeto": a.datum, "dlat": DLAT, "dlon": DLON,
           "prednost": PREDNOST, "ko": kos, "kvadrati": sorted(tiles)}
    with open(os.path.join(out, "index.json"), "w") as f: json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
    print("čestica", n, "kvadrata", len(tiles))

if __name__ == "__main__": main()

"""Priprema adresa (kućni brojevi) za pretragu u aplikaciji iz DGU-ova skupa „Adrese” (INSPIRE AD, GML 3.2.1, ETRS89/LAEA, EPSG:3035).

Izvor: https://geoportal.dgu.hr/services/atom/ad/xml → INSPIRE_Addresses_(AD).zip (cijela Hrvatska, oko 84 MB).
Iz svake adrese uzima se samo: naziv ulice, kućni broj, naselje i točka. Ništa drugo se ne sprema.
Obuhvat: otok Krk i Grad Zagreb (okviri u REGIJE).

Korištenje (Python 3, pip install lxml pyproj):
  python3 tools/adrese/pripremi_adrese.py --zip INSPIRE_Addresses_(AD).zip --datum 2026-10-18
Izlaz: data/adr/ulice_<regija>.json (popis ulica po naselju) i data/adr/b/<NN>.json (kućni brojevi po ulicama, 128 skupina).
Točka: [broj, lon, lat] u milijuntinkama stupnja (oko 0,1 m).
"""
import argparse, json, os, re, subprocess, zlib, collections
from lxml import etree
from pyproj import Transformer

REGIJE = {"krk": (14.40, 44.86, 14.90, 45.26), "zg": (15.75, 45.60, 16.25, 46.00)}
AD = "{http://inspire.ec.europa.eu/schemas/ad/4.0}"; GML = "{http://www.opengis.net/gml/3.2}"; XL = "{http://www.w3.org/1999/xlink}"; GN = "{http://inspire.ec.europa.eu/schemas/gn/4.0}"
NB = 128
T = Transformer.from_crs(4326, 3035, always_xy=True); TI = Transformer.from_crs(3035, 4326, always_xy=True)

def stream(zp, name):
    p = subprocess.Popen(["unzip", "-p", zp, name], stdout=subprocess.PIPE); return p.stdout

def ulice(zp):
    out = {}
    for _, el in etree.iterparse(stream(zp, "ThoroughfareName.gml"), events=("end",), tag=AD + "ThoroughfareName", huge_tree=True):
        t = el.find(".//" + GN + "text")
        if t is not None and t.text: out["#" + el.get(GML + "id")] = t.text.strip()
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    return out

def okviri():
    o = {}
    for k, (a, b, c, d) in REGIJE.items():
        xs, ys = T.transform([a, c, a, c], [b, b, d, d]); o[k] = (min(xs) - 500, min(ys) - 500, max(xs) + 500, max(ys) + 500)
    return o

PO = re.compile(r"\s(\d{5})(\s|$)")
def bucket(k): return zlib.crc32(k.encode("utf-8")) % NB

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--zip", required=True); ap.add_argument("--datum", required=True)
    ap.add_argument("--izlaz", default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "adr"))
    a = ap.parse_args()
    U = ulice(a.zip); print("ulica u RH:", len(U))
    OK = okviri(); rows = []; n = 0
    for _, el in etree.iterparse(stream(a.zip, "Address.gml"), events=("end",), tag=AD + "Address", huge_tree=True):
        n += 1
        pos = el.find(".//" + GML + "pos")
        if pos is not None:
            y, x = map(float, pos.text.split()[:2])  # EPSG:3035 u GML-u: sjever (Y), pa istok (X)
            reg = next((k for k, (x0, y0, x1, y1) in OK.items() if x0 <= x <= x1 and y0 <= y <= y1), None)
            if reg:
                des = el.find(AD + "locator/" + AD + "AddressLocator/" + AD + "designator/" + AD + "LocatorDesignator/" + AD + "designator")
                alt = el.findtext(AD + "alternativeIdentifier") or ""
                ul = next((U[c.get(XL + "href")] for c in el.findall(AD + "component") if c.get(XL + "href", "").startswith("#ThoroughfareName")), None)
                d0 = des.text.strip() if des is not None and des.text else None
                if d0:
                    # puni kućni broj (s dodatkom, npr. 1A ili 1/1) je riječ u tekstu adrese iza naziva ulice: „Ulica 12A Naselje 10000 Pošta”
                    m = PO.search(alt); pre = (alt[:m.start()] if m else alt).strip()
                    if ul and pre.startswith(ul + " "): broj, _, nas = pre[len(ul) + 1:].partition(" ")
                    else:
                        mm = list(re.finditer(r"(?:^|\s)(" + re.escape(d0) + r"\S*)\s", pre))
                        if not mm: broj, nas = None, ""
                        else: q = mm[-1]; broj, nas = q.group(1), pre[q.end():]; ul = ul or pre[:q.start()].strip()
                    nas = nas.strip()
                    if broj and nas and broj[0].isdigit(): rows.append((reg, nas, ul or "", broj, x, y))
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    print("adresa u RH:", n, "· u obuhvatu:", len(rows))
    lon, lat = TI.transform([r[4] for r in rows], [r[5] for r in rows])
    by = collections.defaultdict(list)
    for r, o, l in zip(rows, lon, lat): by[(r[0], r[1], r[2])].append([r[3], round(o * 1e6), round(l * 1e6)])
    os.makedirs(os.path.join(a.izlaz, "b"), exist_ok=True)
    for f in os.listdir(os.path.join(a.izlaz, "b")): os.remove(os.path.join(a.izlaz, "b", f))
    B = collections.defaultdict(dict); idx = []
    for (reg, nas, ul), pts in sorted(by.items()):
        k = nas + "|" + ul; b = bucket(k)
        pts.sort(key=lambda p: (int(re.match(r"\d*", p[0]).group() or 0), p[0]))
        B[b][k] = pts
        c = [sum(p[1] for p in pts) // len(pts), sum(p[2] for p in pts) // len(pts)]
        idx.append([reg, nas, ul, b, len(pts), c[0], c[1]])
    for b, d in B.items():
        with open(os.path.join(a.izlaz, "b", f"{b:03d}.json"), "w", encoding="utf-8") as fh: json.dump(d, fh, ensure_ascii=False, separators=(",", ":"))
    # popis ulica po regiji (aplikacija učita samo onaj za regiju pretrage)
    for f in os.listdir(a.izlaz):
        if f.startswith("ulice_") or f == "index.json": os.remove(os.path.join(a.izlaz, f))
    for reg in REGIJE:
        with open(os.path.join(a.izlaz, f"ulice_{reg}.json"), "w", encoding="utf-8") as fh:
            json.dump({"v": 1, "izvor": "DGU, Adrese (INSPIRE AD), usluga preuzimanja", "preuzeto": a.datum, "regija": reg, "skupina": NB,
                       "polja": ["naselje", "ulica", "skupina", "brojeva", "lon", "lat"], "ulice": [r[1:] for r in idx if r[0] == reg]}, fh, ensure_ascii=False, separators=(",", ":"))
    print("ulica u obuhvatu:", len(idx), "· skupina:", len(B))

if __name__ == "__main__": main()

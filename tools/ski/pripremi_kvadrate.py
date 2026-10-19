"""Priprema DGU SKI podataka za aplikaciju: kvadrati od oko 1 km s funkcionalnim vodovima.
Područja: zagreb (datoteke _21, izlaz data/ski) i krk (datoteke _08 Primorsko-goranske županije, samo otok Krk, izlaz data/ski_krk).

Korištenje (Python 3, pip install lxml pyproj shapely):
  python3 tools/ski/pripremi_kvadrate.py --vodovod-link WA_UtilityLink.gml --vodovod-pipe WaterPipe.gml \
      --kanalizacija-link SW_UtilityLink.gml --kanalizacija-pipe SewerPipe.gml \
      --struja-link EL_UtilityLink.gml --struja-pipe ElectricityPipe.gml --datum 2026-10-17 [--podrucje krk]

Ulaz: INSPIRE GML (ATOM) s ski.dgu.hr, datoteke _21 (Grad Zagreb). Koordinate su EPSG:3035 s redoslijedom osi
SJEVER, ISTOK (službeni redoslijed EPSG-a); pogrešan redoslijed smješta Zagreb u Atlantik.
Izlaz: data/ski/index.json i data/ski/<mreža>/<kvadrat>.json
  kvadrat = "<floor(lat/0.009)>_<floor(lon/0.013)>" (oko 1,0 × 1,0 km); vod se upisuje u svaki kvadrat koji dodiruje
  njegov obuhvat, a aplikacija ponavljanja uklanja po oznaci voda.
  Vod: [oznaka, [lon1e6, lat1e6, lon1e6, lat1e6, ...]] (cijeli brojevi, 1e-6 stupnja ≈ 0,1 m).
Filtri: samo vodovi statusa "functional" (bez napuštenih i izvan uporabe); struja samo "Niski napon".
Pojednostavljenje: Douglas-Peucker 0,3 m u HTRS96/TM (EPSG:3765), prije pretvorbe u WGS84.
"""
import argparse, json, math, os, collections, shutil
from lxml import etree
from pyproj import Transformer
from shapely.geometry import LineString

DLAT, DLON = 0.009, 0.013
GML = "{http://www.opengis.net/gml/3.2}"; XL = "{http://www.w3.org/1999/xlink}href"
loc = lambda t: t.split("}")[-1]
T_TM = Transformer.from_crs(3035, 3765)                 # (N,E) 3035 → (E,N) 3765
T_WGS = Transformer.from_crs(3765, 4326, always_xy=True)  # (E,N) 3765 → (lon,lat)

def stream(path, tag):
    for _, el in etree.iterparse(path, events=("end",), tag=tag, huge_tree=True):
        yield el
        el.clear()
        while el.getprevious() is not None:
            del el.getparent()[0]

def pipes(path, volt):
    ok = {}
    for el in stream(path, "{*}member"):
        p = el[0]; link = st = v = None
        for c in p:
            t = loc(c.tag)
            if t == "link": link = (c.get(XL) or "").lstrip("#")
            elif t == "currentStatus": st = (c.get(XL) or "").split("/")[-1]
            elif t == "operatingVoltage": v = (c.text or "").strip()
        if link and st == "functional" and (not volt or v == volt): ok[link] = True
    return ok

# Obuhvat područja (WGS84). Krk: pravokutnik oko otoka bez kopna (crta kroz Vinodolski kanal) i bez Cresa.
KRK_KANAL = [(14.50, 45.30), (14.60, 45.225), (14.69, 45.165), (14.78, 45.11), (14.88, 45.02), (14.95, 44.95)]
def u_krk(lon, lat):
    if not (44.86 <= lat <= 45.265 and 14.42 <= lon <= 14.90): return False
    if lon < 14.50 and lat < 45.0: return False  # istočna obala Cresa
    for (x1, y1), (x2, y2) in zip(KRK_KANAL, KRK_KANAL[1:]):
        if x1 <= lon <= x2: return lat < y1 + (y2 - y1) * (lon - x1) / (x2 - x1)
    return True
PODRUCJA = {
    "zagreb": {"izlaz": "ski", "obuhvat": None, "izvor": "Državna geodetska uprava, Sustav katastra infrastrukture (INSPIRE, ski.dgu.hr), Grad Zagreb"},
    "krk": {"izlaz": "ski_krk", "obuhvat": u_krk, "izvor": "Državna geodetska uprava, Sustav katastra infrastrukture (INSPIRE, ski.dgu.hr), Primorsko-goranska županija, otok Krk"},
}
OBUHVAT = None

def build(net, link_path, pipe_path, volt, out):
    keep = pipes(pipe_path, volt)
    tiles = collections.defaultdict(list); n = 0; L = 0.0
    for el in stream(link_path, "{*}UtilityLink"):
        lid = el.get(GML + "id")
        if lid not in keep: continue
        pl = el.find(".//{*}posList")
        if pl is None: continue
        v = list(map(float, pl.text.split()))
        e, nn = T_TM.transform(v[0::2], v[1::2])
        ln = LineString(list(zip(e, nn)))
        if ln.length <= 0: continue
        s = ln.simplify(0.3, preserve_topology=False)
        lon, lat = T_WGS.transform([c[0] for c in s.coords], [c[1] for c in s.coords])
        if OBUHVAT and not any(OBUHVAT(a, b) for a, b in zip(lon, lat)): continue
        L += ln.length
        flat = []
        for a, b in zip(lon, lat): flat += [round(a * 1e6), round(b * 1e6)]
        n += 1
        k0 = (math.floor(min(lat) / DLAT), math.floor(min(lon) / DLON)); k1 = (math.floor(max(lat) / DLAT), math.floor(max(lon) / DLON))
        for i in range(k0[0], k1[0] + 1):
            for j in range(k0[1], k1[1] + 1): tiles[f"{i}_{j}"].append([n, flat])
    d = os.path.join(out, net); os.makedirs(d, exist_ok=True)
    for k, arr in tiles.items():
        with open(os.path.join(d, k + ".json"), "w") as f: json.dump(arr, f, separators=(",", ":"))
    print(f"{net}: {n} vodova, {L/1000:.0f} km, {len(tiles)} kvadrata")
    return {"vodova": n, "km": round(L / 1000), "kvadrati": sorted(tiles)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for net in ("vodovod", "kanalizacija", "struja"):
        ap.add_argument(f"--{net}-link", required=True); ap.add_argument(f"--{net}-pipe", required=True)
    ap.add_argument("--datum", required=True, help="datum preuzimanja s ski.dgu.hr (GGGG-MM-DD)")
    ap.add_argument("--podrucje", default="zagreb", choices=sorted(PODRUCJA))
    ap.add_argument("--stanje", default="", help="stanje podataka po mreži iz zaglavlja GML-a, npr. vodovod=16. 7. 2024.;kanalizacija=17. 7. 2024.;struja=3. 10. 2026.")
    ap.add_argument("--izlaz", default=None)
    a = ap.parse_args(); P = PODRUCJA[a.podrucje]; OBUHVAT = P["obuhvat"]
    out = os.path.abspath(a.izlaz or os.path.join(os.path.dirname(__file__), "..", "..", "data", P["izlaz"]))
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    idx = {"v": 1, "podrucje": a.podrucje, "izvor": P["izvor"],
           "licenca": "otvorena dozvola (NIPP); navesti izvor", "preuzeto": a.datum, "dlat": DLAT, "dlon": DLON,
           "napomena": "funkcionalni vodovi; struja samo niski napon; promjer i vrsta cijevi nisu objavljeni; evidencija može biti nepotpuna", "mreze": {}}
    idx["mreze"]["vodovod"] = build("vodovod", a.vodovod_link, a.vodovod_pipe, None, out)
    idx["mreze"]["kanalizacija"] = build("kanalizacija", a.kanalizacija_link, a.kanalizacija_pipe, None, out)
    idx["mreze"]["struja"] = build("struja", a.struja_link, a.struja_pipe, "Niski napon", out)
    if a.stanje: idx["stanje"] = dict(x.split("=", 1) for x in a.stanje.split(";") if "=" in x)
    with open(os.path.join(out, "index.json"), "w") as f: json.dump(idx, f, ensure_ascii=False, separators=(",", ":"))
    print("indeks:", os.path.join(out, "index.json"))

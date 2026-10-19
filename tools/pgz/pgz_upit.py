"""Upiti prema servisima Primorsko-goranske županije (ArcGIS REST, gisportal.pgz.hr) – ista logika kao u aplikaciji Čestica HR.

Korištenje (Python 3.9+, bez dodatnih paketa; shapely je neobavezan, za udjele zona):
  python3 pgz_upit.py kornic_cestica_735_76.geojson            # čestica iz GeoJSON-a (EPSG:4326)
  python3 pgz_upit.py --tocka 45.04405 14.61590                 # samo točka (lat lon)
Spremi izvorne odgovore servisa u mapu ./pgz_odgovori/ i ispiše sažetak.

Servisi (javni, bez ključa):
  NAMJENA_POVRSINA_NOVO – namjena površina iz prostornih planova gradova i općina (poligoni)
  IZRADA_PP             – obuhvati prostornih planova: vrsta, status, službeno glasilo, poveznice
U aplikaciji: src/app.template.html, SRC_KRK, pointQuery(), polyQuery(), inspectKrk(), krkPlans(), krkKind().
"""
import json, sys, os, re, pathlib, urllib.parse, urllib.request

PGZ = "https://gisportal.pgz.hr/server/rest/services/STANJE/"
NAMJENA = PGZ + "NAMJENA_POVRSINA_NOVO/FeatureServer/0/query"
PLANOVI = PGZ + "IZRADA_PP/FeatureServer/0/query"
POLJA_PLANOVI = "GRAD_OPCINA,VRSTA_PP,STATUS_PP,NAZIV,SN_BROJ,SN_LINK,PDF_LINK_PUBLIC,DatumStNaSnPlana,DatumDonOdlIzr"
UA = {"User-Agent": "CesticaHR-DataManager/1.0"}

def _post(url, params, timeout=30):
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        j = json.loads(r.read().decode("utf-8"))
    if isinstance(j, dict) and j.get("error"):  # ArcGIS vraća grešku kao JSON s HTTP 200
        raise RuntimeError(f"ArcGIS greška: {j['error']}")
    return j

def tocka(url, lat, lon, fields="*", geom=False):
    """Kao pointQuery() u aplikaciji: točka u WGS84, presjek, odgovor kao GeoJSON."""
    return _post(url, {"geometry": f"{lon},{lat}", "geometryType": "esriGeometryPoint", "inSR": "4326",
                       "spatialRel": "esriSpatialRelIntersects", "outFields": fields, "returnGeometry": str(geom).lower(),
                       "outSR": "4326", "f": "geojson"})

def poligon(url, geometry, fields="*", geom=True):
    """Kao polyQuery() u aplikaciji: prstenovi čestice kao Esri poligon (WGS84), POST jer je upit dug."""
    rings = geometry["coordinates"] if geometry["type"] == "Polygon" else [r for p in geometry["coordinates"] for r in p]
    return _post(url, {"geometry": json.dumps({"rings": rings, "spatialReference": {"wkid": 4326}}),
                       "geometryType": "esriGeometryPolygon", "inSR": "4326", "spatialRel": "esriSpatialRelIntersects",
                       "outFields": fields, "returnGeometry": str(geom).lower(), "outSR": "4326", "f": "geojson"})

def vrsta(p):
    """Kao krkKind() u aplikaciji: gpn = građevinsko područje naselja, gpi = izdvojeno izvan naselja, van = izvan GP-a."""
    pol = (p.get("POLAZNA_NAMJENA") or "").lower(); prim = (p.get("PRIMARNA_NAMJENA") or "").lower()
    if re.search(r"građevn|gradevn|građevinsk", pol):
        return "gpn" if "naselj" in prim else "gpi"
    return "van" if (pol or prim) else "nep"

def vazeci_planovi(features):
    """Kao krkPlans() u aplikaciji: zadnja važeća odluka po vrsti plana i jedinici (prema broju glasila), te planovi u izradi."""
    def sn_key(s):  # kao snKey(): "2020-29" -> 2020029
        m = re.search(r"(\d{4})\D+(\d+)", str(s or "")); return int(m.group(1)) * 1000 + int(m.group(2)) if m else 0
    vaz, izr = {}, []
    for f in features:
        p = f.get("properties") or {}
        if not p.get("VRSTA_PP") or p["VRSTA_PP"] == "DPPR": continue
        st = str(p.get("STATUS_PP") or "").upper()
        if st == "VAŽEĆI":
            k = p["VRSTA_PP"] + "|" + (p.get("GRAD_OPCINA") or "")
            if k not in vaz or sn_key(p.get("SN_BROJ")) > sn_key(vaz[k].get("SN_BROJ")): vaz[k] = p
        elif st == "U IZRADI": izr.append(p)
    return list(vaz.values()), izr

def main():
    a = sys.argv[1:]
    out = pathlib.Path("pgz_odgovori"); out.mkdir(exist_ok=True)
    if a and a[0] == "--tocka":
        lat, lon = float(a[1]), float(a[2]); parcel = None
    elif a:
        fc = json.loads(pathlib.Path(a[0]).read_text(encoding="utf-8"))
        parcel = fc["features"][0] if fc.get("type") == "FeatureCollection" else fc
        g = parcel["geometry"]; ring = g["coordinates"][0] if g["type"] == "Polygon" else g["coordinates"][0][0]
        lon = sum(p[0] for p in ring[:-1]) / (len(ring) - 1); lat = sum(p[1] for p in ring[:-1]) / (len(ring) - 1)
        # aplikacija koristi točku na površini čestice (turf.pointOnFeature); za konveksne čestice težište je unutra
    else:
        print(__doc__); sys.exit(2)
    nam_t = tocka(NAMJENA, lat, lon); (out / "namjena_tocka.json").write_text(json.dumps(nam_t, ensure_ascii=False, indent=1), encoding="utf-8")
    pl = tocka(PLANOVI, lat, lon, POLJA_PLANOVI); (out / "planovi_tocka.json").write_text(json.dumps(pl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"točka {lat:.6f}, {lon:.6f}")
    for f in nam_t.get("features", []):
        p = f["properties"]; print("  namjena:", p.get("OZNAKA_NAMJENE"), "·", p.get("PRIMARNA_NAMJENA"), "·", p.get("IZGRADJENOST"), "·", p.get("NASELJE"), "·", p.get("OPCINA_GRAD"), "· izvor", p.get("IZVOR_PODATAKA"), "·", vrsta(p))
    if parcel:
        nam_p = poligon(NAMJENA, parcel["geometry"]); (out / "namjena_cestica.json").write_text(json.dumps(nam_p, ensure_ascii=False, indent=1), encoding="utf-8")
        try:
            from shapely.geometry import shape
            from pyproj import Geod
            geod = Geod(ellps="GRS80"); P = shape(parcel["geometry"]); A = abs(geod.geometry_area_perimeter(P)[0])
            for f in nam_p.get("features", []):
                i = P.intersection(shape(f["geometry"])); s = abs(geod.geometry_area_perimeter(i)[0]) / A if not i.is_empty else 0
                p = f["properties"]; print(f"  udio {s*100:5.1f} %:", p.get("OZNAKA_NAMJENE"), p.get("PRIMARNA_NAMJENA"), p.get("IZGRADJENOST"))
        except ImportError:
            print("  (za udjele zona instaliraj shapely i pyproj)", len(nam_p.get("features", [])), "zona dodiruje česticu")
    vaz, izr = vazeci_planovi(pl.get("features", []))
    for p in vaz: print("  važeći:", p.get("VRSTA_PP"), "·", p.get("GRAD_OPCINA"), "· SN", p.get("SN_BROJ"), "·", (p.get("NAZIV") or "")[:80])
    for p in izr: print("  u izradi:", p.get("VRSTA_PP"), "·", p.get("GRAD_OPCINA"), "· SN", p.get("SN_BROJ"))
    print("izvorni odgovori spremljeni u", out.resolve())

if __name__ == "__main__": main()

"""Indeks brojeva katastarskih čestica za prijedloge i pretragu po broju u gradovima izvan Zagreba i Krka.

Izvor: DGU, digitalni katastarski plan (ATOM, https://oss.uredjenazemlja.hr/oss/public/atom/ko-<matični broj>.zip),
katalog DGU-a: „nema uvjeta za pristup i korištenje”. Za svaku česticu sprema se samo broj i jedna točka unutar čestice
(ne oblik): odabirom u aplikaciji karta ide na tu točku, a čestica se učitava uživo iz katastarskog sloja DGU-a.

Korištenje (Python 3, pip install lxml pyproj shapely):
  python3 tools/katastar/pripremi_brojeve_hr.py --ulaz MAPA_SA_ZIPOVIMA --datum 2026-11-09
  (MAPA/ko-329835.zip …; grad svake k.o. zadan je u GRADOVI)
Izlaz: data/kat_hr/index.json i data/kat_hr/<matični broj>.json = {"v":1,"ko":mb,"c":{"broj":[lon,lat,pov,zgr]}}: točka u milijuntinkama
stupnja, grafička površina (m², zaokružena) i 1 ako je na čestici točka zgrade iz sloja zgrada istog DKP-a (inače 0); za skener čestica.
"""
import argparse, glob, io, json, os, shutil, zipfile
from lxml import etree
from pyproj import Transformer
from shapely.geometry import Polygon, MultiPolygon
from shapely.strtree import STRtree

G = "{http://www.opengis.net/gml}"; O = "{http://oss}"
T = Transformer.from_crs(3765, 4326, always_xy=True)
# k.o. u obuhvatu gradova s obrađenim pravilima gradnje (uzorak točaka svakih ~500 m po okviru grada, DGU katastarski sloj, 2026-11-09)
GRADOVI = {
    "split": "313505 329576 329622 329657 329711 329789 329835 329860 329878 336556",
    "zadar": "334570 334588 334618 334626 334634 334774 334855 334880 335037 335193 341541",
    "rijeka": "324493 324507 324523 324531 324574 324612 324680 324698 324710 324752 324779 324850 338290 338460",
    "osijek": "300055 300101 300209 320498 320528 320609 320668 320692 320722 320749",
}
GRAD = {mb: g for g, s in GRADOVI.items() for mb in s.split()}

def poligon(geom):
    P = []
    for pg in geom.iter(G + "Polygon"):
        rr = [[tuple(map(float, p.split(",")[:2])) for p in lr.find(G + "coordinates").text.split()] for lr in pg.iter(G + "LinearRing")]
        if rr and len(rr[0]) >= 3: P.append(Polygon(rr[0], rr[1:]))
    return MultiPolygon(P) if len(P) > 1 else (P[0] if P else None)

def citaj(z, ime):
    n = next((x for x in z.namelist() if x.endswith(ime)), None)
    return z.open(n) if n else None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ulaz", required=True); ap.add_argument("--datum", required=True)
    ap.add_argument("--izlaz", default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "kat_hr"))
    a = ap.parse_args(); out = os.path.abspath(a.izlaz)
    if os.path.isdir(out): shutil.rmtree(out)
    os.makedirs(out)
    kos = {}
    for zp in sorted(glob.glob(os.path.join(a.ulaz, "*.zip"))):
        z = zipfile.ZipFile(zp); f0 = citaj(z, "katastarske_opcine.gml")
        if f0 is None: print("preskačem (nije DKP):", zp); continue
        naziv = mb = None
        for e in etree.parse(f0).getroot().iter():
            if e.tag == O + "NAZIV": naziv = e.text
            elif e.tag == O + "MATICNI_BROJ": mb = e.text
        if mb not in GRAD: print("preskačem k.o. izvan popisa:", mb, naziv); continue
        C = {}; x0 = y0 = 1e9; x1 = y1 = -1e9; GEO, KEY = [], []
        for _, f in etree.iterparse(citaj(z, "katastarske_cestice.gml"), tag=O + "CESTICE", huge_tree=True):
            broj = f.findtext(O + "BROJ_CESTICE"); g = f.find(O + "GEOM"); P = poligon(g) if g is not None else None
            pg = f.findtext(O + "POVRSINA_GRAFICKA")
            f.clear()
            while f.getprevious() is not None: del f.getparent()[0]
            if not broj or P is None or P.is_empty: continue
            p = P.representative_point(); lon, lat = T.transform(p.x, p.y)
            pov = round(float(pg)) if pg else round(P.area)
            C[broj] = [round(lon * 1e6), round(lat * 1e6), pov, 0]
            GEO.append(P); KEY.append(broj)
            x0 = min(x0, lon); x1 = max(x1, lon); y0 = min(y0, lat); y1 = max(y1, lat)
        # zgrade: točka unutar obrisa zgrade → čestica na kojoj leži (oznaka zgr = 1)
        fz = citaj(z, "nacini_uporabe_zgrada.gml"); nz = 0
        if fz is not None and GEO:
            tree = STRtree(GEO)
            for _, f in etree.iterparse(fz, tag=O + "ZGRADE", huge_tree=True):
                g = f.find(O + "GEOM"); Z = poligon(g) if g is not None else None
                f.clear()
                while f.getprevious() is not None: del f.getparent()[0]
                if Z is None or Z.is_empty: continue
                q = Z.representative_point()
                for i in tree.query(q, predicate="intersects"):
                    C[KEY[int(i)]][3] = 1; nz += 1; break
        with open(os.path.join(out, mb + ".json"), "w", encoding="utf-8") as fh:
            json.dump({"v": 1, "ko": mb, "naziv": naziv, "preuzeto": a.datum, "c": C}, fh, ensure_ascii=False, separators=(",", ":"))
        kos[mb] = {"naziv": naziv, "grad": GRAD[mb], "cestica": len(C), "okvir": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)]}
        print(mb, naziv, GRAD[mb], len(C), "zgrada", nz, flush=True)
    nema = sorted(set(GRAD) - set(kos))
    if nema: print("NEDOSTAJE:", " ".join(nema))
    idx = {"v": 1, "izvor": "Državna geodetska uprava, digitalni katastarski plan (ATOM, oss.uredjenazemlja.hr)",
           "uvjeti": "katalog DGU-a: nema uvjeta za pristup i korištenje", "preuzeto": a.datum, "ko": kos}
    with open(os.path.join(out, "index.json"), "w", encoding="utf-8") as fh: json.dump(idx, fh, ensure_ascii=False, separators=(",", ":"))
    print("k.o.:", len(kos), "čestica:", sum(v["cestica"] for v in kos.values()))

if __name__ == "__main__": main()

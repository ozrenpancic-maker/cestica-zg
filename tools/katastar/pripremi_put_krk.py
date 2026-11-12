"""Način uporabe zemljišta za čestice otoka Krka: koje čestice su prema katastru put, cesta ili voda (za skener i list čestice).

Izvor: DGU, digitalni katastarski plan (ATOM, https://oss.uredjenazemlja.hr/oss/public/atom/ko-<matični broj>.zip), sloj
nacini_uporabe_zemljista.gml; katalog DGU-a: „nema uvjeta za pristup i korištenje”. Čestice se vežu na data/kat_krk preko oznake
čestice (CESTICA_ID); pločice čestica se ne mijenjaju. Sloj načina uporabe ne pokriva sve čestice (samo novije izmjere).

Korištenje (Python 3, pip install lxml pyproj shapely):
  python3 -I tools/katastar/pripremi_put_krk.py --ulaz MAPA_SA_ZIPOVIMA --datum 2026-11-11
Pokreće se NAKON pripremi_krk.py (taj alat briše cijelu mapu data/kat_krk, pa i put.json), po mogućnosti iz istih zipova.
Izlaz: data/kat_krk/put.json = {"v":1,"preuzeto":datum,"p":{"<oznaka čestice>":2|3|4}}: 2 = prometna površina (put, cesta, ulica, prolaz,
pločnik, staza, pruga, stepenište) na barem pola površine čestice, 3 = voda (kanal, potok, more, jarak) na barem pola, 4 = druga
uporaba (dvorište, oranica, pašnjak …) na barem 80 % površine – čestica prema katastru nije put, pa oznaka po obliku u aplikaciji
vrijedi samo za trake do 6 m. Ista pravila kao u pripremi_brojeve_hr.py.
"""
import argparse, glob, json, os, sys, zipfile
from lxml import etree
from shapely.strtree import STRtree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pripremi_brojeve_hr import G, O, PROMET, VODA, poligon, citaj

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ulaz", required=True); ap.add_argument("--datum", required=True)
    ap.add_argument("--izlaz", default=os.path.join(os.path.dirname(__file__), "..", "..", "data", "kat_krk"))
    a = ap.parse_args(); out = os.path.abspath(a.izlaz)
    idx = json.load(open(os.path.join(out, "index.json"), encoding="utf-8"))
    poznate = set()
    for k in idx["kvadrati"]:
        for r in json.load(open(os.path.join(out, k + ".json"), encoding="utf-8")): poznate.add(r[0])
    P = {}; br = {2: 0, 3: 0, 4: 0}; kos = set(); pokriveno = 0
    for zp in sorted(glob.glob(os.path.join(a.ulaz, "*.zip"))):
        z = zipfile.ZipFile(zp); mb = None; f0 = citaj(z, "katastarske_opcine.gml")
        if f0 is None: print("preskačem (nije DKP):", zp); continue
        for e in etree.parse(f0).getroot().iter():
            if e.tag == O + "MATICNI_BROJ": mb = e.text
        if mb not in idx["ko"]: print("preskačem k.o. izvan otoka:", mb); continue
        kos.add(mb); GEO, ID = [], []
        for _, f in etree.iterparse(citaj(z, "katastarske_cestice.gml"), tag=O + "CESTICE", huge_tree=True):
            cid = f.findtext(O + "CESTICA_ID"); g = f.find(O + "GEOM"); Pc = poligon(g) if g is not None else None
            f.clear()
            while f.getprevious() is not None: del f.getparent()[0]
            if not cid or Pc is None or Pc.is_empty or int(cid) not in poznate: continue
            if not Pc.is_valid: Pc = Pc.buffer(0)
            if Pc.is_empty or not Pc.area > 0: continue
            GEO.append(Pc); ID.append(int(cid))
        fu = citaj(z, "nacini_uporabe_zemljista.gml")
        if fu is None or not GEO: continue
        tree = STRtree(GEO); udio = {}
        for _, f in etree.iterparse(fu, tag=O + "NACINI_UPORABE", huge_tree=True):
            naz = (f.findtext(O + "NACINA_UPORABE_ZEMLJISTA") or "").strip().upper(); g = f.find(O + "GEOM"); U = poligon(g) if g is not None else None
            f.clear()
            while f.getprevious() is not None: del f.getparent()[0]
            vr = 2 if PROMET.search(naz) else 3 if VODA.search(naz) else 0
            if U is None or U.is_empty: continue
            if not U.is_valid: U = U.buffer(0)
            for i in tree.query(U, predicate="intersects"):
                try: ar = GEO[int(i)].intersection(U).area
                except Exception: continue
                if ar > 0: udio[(int(i), vr)] = udio.get((int(i), vr), 0) + ar
        pokriveno += len({i for i, _ in udio})
        for (i, vr), ar in udio.items():
            s = ar / GEO[i].area
            if vr and s >= 0.5: P[str(ID[i])] = vr
            elif not vr and s >= 0.8 and str(ID[i]) not in P: P[str(ID[i])] = 4
    for v in P.values(): br[v] += 1
    nema = sorted(set(idx["ko"]) - kos)
    if nema: print("NEDOSTAJE k.o.:", " ".join(nema))
    with open(os.path.join(out, "put.json"), "w", encoding="utf-8") as fh:
        json.dump({"v": 1, "izvor": "Državna geodetska uprava, digitalni katastarski plan (ATOM, oss.uredjenazemlja.hr), način uporabe zemljišta",
                   "preuzeto": a.datum, "p": dict(sorted(P.items(), key=lambda t: int(t[0])))}, fh, separators=(",", ":"))
    print("k.o.:", len(kos), "čestica s oznakom:", len(P), "od", len(poznate), "(sloj uporabe dodiruje", pokriveno, ") | promet", br[2], "voda", br[3], "druga uporaba", br[4])

if __name__ == "__main__": main()

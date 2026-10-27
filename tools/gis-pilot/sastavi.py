#!/usr/bin/env python3
"""Sastavlja demo izvještaj GIS-first pilota (jedna HTML stranica) i mjerenje podataka.

    python3 tools/gis-pilot/dosje.py && python3 tools/gis-pilot/sastavi.py
    → tools/gis-pilot/dist/gis_pilot_735_76.html, dist/mjerenje.json
"""
import base64, hashlib, io, json, math, time, warnings
from collections import Counter
from pathlib import Path
warnings.filterwarnings("ignore", category=DeprecationWarning)
from PIL import Image
from pyproj import Transformer
from shapely.geometry import shape, Polygon, box
from shapely.ops import transform

T0 = time.perf_counter()
P = Path(__file__).resolve().parent; R = P.parents[1]
D = json.loads((P / "dist/dosje_735_76.json").read_text(encoding="utf-8"))
TM = Transformer.from_crs(4326, 3765, always_xy=True)
tm = lambda g: transform(TM.transform, g)


def dek(r):
    lon, lat = r[0], r[1]; pts = [(lon / 1e6, lat / 1e6)]
    for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append((lon / 1e6, lat / 1e6))
    return pts


def katastar_u(okvir_wgs, kvadrati):
    idx = json.loads((R / "data/kat_krk/index.json").read_text())
    x0, y0, x1, y1 = okvir_wgs.bounds; out = {}
    for i in range(math.floor(y0 / idx["dlat"]), math.floor(y1 / idx["dlat"]) + 1):
        for j in range(math.floor(x0 / idx["dlon"]), math.floor(x1 / idx["dlon"]) + 1):
            f = R / f"data/kat_krk/{i}_{j}.json"
            if not f.exists(): continue
            for c in json.loads(f.read_text()):
                if c[0] in out: continue
                try:
                    g = Polygon(dek(c[4][0][0]))
                    if not g.is_valid: g = g.buffer(0)
                except Exception: continue
                if g.intersects(okvir_wgs): out[c[0]] = (c[1], c[3], g)
    return out


# ---------- karta (HTRS96/TM → SVG) ----------
ces = shape(D["cestica"]["geometrija"]); cT = tm(ces); cx, cy = cT.centroid.x, cT.centroid.y
OK = 110   # ±110 m oko čestice
okT = box(cx - OK, cy - OK, cx + OK, cy + OK)
inv = Transformer.from_crs(3765, 4326, always_xy=True)
okW = transform(inv.transform, okT)
W = 660
sx = lambda x: (x - (cx - OK)) / (2 * OK) * W
sy = lambda y: ((cy + OK) - y) / (2 * OK) * W


def put(g):
    gs = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
    d = ""
    for p in gs:
        if p.geom_type != "Polygon" or p.is_empty: continue
        for ring in [p.exterior] + list(p.interiors):
            d += "M" + "L".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y, *_ in ring.coords) + "Z"
    return d


kat = katastar_u(okW, None)
susjedi = []
for cid, (broj, pov, g) in kat.items():
    gt = tm(g).intersection(okT)
    if gt.is_empty: continue
    lab = None
    if cid != D["cestica"]["dgu_id"] and tm(g).area > 120 and okT.buffer(-12).contains(tm(g).representative_point()):
        rp = tm(g).representative_point(); lab = [round(sx(rp.x), 1), round(sy(rp.y), 1), broj]
    susjedi.append({"d": put(gt), "lab": lab})
obT = tm(shape(D["planovi"]["upu2"]["geometrija"]))
ob_rub = obT.boundary.intersection(okT)
def linija(g):
    gs = [g] if g.geom_type == "LineString" else list(getattr(g, "geoms", []))
    return "".join("M" + "L".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y, *_ in l.coords) for l in gs if l.geom_type == "LineString")
na2 = next(z for z in D["zone_ppug"]["geometrije"] if z["oznaka"] == "NA2")
na2T = tm(shape(na2["geometrija"])).intersection(okT)
karta = {"w": W, "susjedi": susjedi, "cestica": put(cT), "obuhvat": linija(ob_rub), "na2": put(na2T),
         "mjerilo_px": 50 / (2 * OK) * W, "oznaka": [round(sx(cx), 1), round(sy(cy), 1)]}

# pregledna karta: cijeli obuhvat UPU-a 2
x0, y0, x1, y1 = obT.bounds; s = 220 / max(x1 - x0, y1 - y0)
pr = lambda x, y: ((x - x0) * s + 10, (y1 - y) * s + 10)
pregled = {"w": round((x1 - x0) * s + 20), "h": round((y1 - y0) * s + 20),
           "obuhvat": "M" + "L".join("%.1f,%.1f" % pr(x, y) for x, y, *_ in obT.exterior.coords) + "Z",
           "cestica": list(map(lambda v: round(v, 1), pr(cx, cy))),
           "okvir": "M" + "L".join("%.1f,%.1f" % pr(x, y) for x, y, *_ in okT.exterior.coords) + "Z"}

# ---------- rasteri (izrezi PGŽ, smanjeni za stranicu) ----------
def slika(p):
    im = Image.open(p).convert("RGB"); im.thumbnail((560, 560)); b = io.BytesIO(); im.save(b, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()
K = R / "tests/pgz-odgovori/735-76-kornic-2026-10-22/karte"
rasteri = [{"id": "karta4", "naslov": "Karta 4. Način i uvjeti gradnje", "oid": 7104, "src": slika(K / "karta4_s_cesticom.png"), "kandidat": "M11 (oznaka »M1₁«)"},
           {"id": "karta3a", "naslov": "Karta 3A. Područja posebnih uvjeta korištenja", "oid": 7102, "src": slika(K / "karta3a_s_cesticom.png"), "kandidat": "zona zaštite »C« (plavi šraf)"}]

# ---------- mjerenje: koliko podataka imamo ----------
pok = D["pokazatelji"]
stanja = Counter(p["stanje"] for p in pok)
karike = Counter(k["razina"] for p in pok for k in p["lanac"])
ulazi = [
    ("Granica i grafička površina čestice", "DGU DKP (ATOM)", "ima", "vektor, lokalno 210 862 čestica Krka"),
    ("Površina upisana u zemljišnu knjigu", "ZK / OSS", "nema", "Podaci nisu dostupni (nema javnog strojnog izvora u pilotu)"),
    ("Važeći planovi na lokaciji, datumi, glasila", "PGŽ IZRADA_PP", "ima", "29 zapisa na točki; provjereno 22. i 27. 10."),
    ("Obuhvat UPU-a 2", "PGŽ IZRADA_PP (geometrija)", "ima", "vektor, 43,24 ha"),
    ("Namjena prema PPUG-u (NA2)", "PGŽ NAMJENA_POVRSINA_NOVO", "ima", "vektor; udio na čestici 99,78 %"),
    ("Detaljna zona UPU-a (M11 / M2 / D2 …)", "PGŽ PP_RASTERI, karta 4", "kandidat", "samo raster bez legende; treba stručna potvrda"),
    ("Zona zaštite »B« / »C«", "PGŽ PP_RASTERI, karta 3A; čl. 83.", "kandidat", "samo raster; popis rubnih čestica zone »B« zastario (27/72 ne postoji)"),
    ("Tekst odredbi UPU-a 2 (čl. 1.–108.)", "SN PGŽ 19/2016, PDF", "ima", "cijeli tekst, SHA provjeren"),
    ("Pravila za stambenu gradnju", "pripremljeno ručno iz teksta", "kandidat", "30 pravila + 3 okvirne odredbe, svi citati doslovno nađeni; 0 stručno potvrđenih"),
    ("Pravna aktualnost UPU-a 2", "SN PGŽ nakon 19/2016", "nema", "nije neovisno provjereno"),
    ("Kategorija ceste i regulacijski pravac", "Grad Krk / geodet", "nema", "Podaci nisu dostupni"),
    ("Nagib terena na čestici", "DMR / geodet", "nema", "Podaci nisu dostupni u pilotu"),
    ("»Okruženje uređenih i izgrađenih čestica« (iznimka 400 m²)", "očevid / stručnjak", "nema", "Podaci nisu dostupni"),
]
# obuhvat: koliko katastarskih čestica pokriva jedna priprema područja
obW = shape(D["planovi"]["upu2"]["geometrija"]); svi = katastar_u(obW, None)
uob = [(b, p) for cid, (b, p, g) in svi.items() if g.intersection(obW).area / g.area > 0.5]
raspon = Counter("< 300 m²" if (p or 0) < 300 else "300–399 m²" if p < 400 else "400–499 m²" if p < 500 else "≥ 500 m²" for b, p in uob)
pravila_n = len(D["pravila"]["popis"]); clanci_n = len({p["clanak"] for p in D["pravila"]["popis"]})
rad = [
    {"posao": f"Potvrditi {pravila_n} pripremljenih pravila ({clanci_n} članaka) u alatu za pregled", "jednom_po": "planu", "kolicina": f"{pravila_n} pravila, čl. {', '.join(sorted({str(p['clanak']) for p in D['pravila']['popis']}, key=int))}.", "vrijeme": "nije izmjereno"},
    {"posao": "Digitalizirati zone s karte 4 (M11, M12, M2, D, …) za cijeli obuhvat", "jednom_po": "planu", "kolicina": "43,24 ha; broj zona na listu nije prebrojan", "vrijeme": "nije izmjereno"},
    {"posao": "Digitalizirati granice zona zaštite »B« i »C« s karte 3A", "jednom_po": "planu", "kolicina": "2 zone", "vrijeme": "nije izmjereno"},
    {"posao": "Riješiti sukobe i nejasnoće u tekstu (Q3, Q8, Q9, Q10)", "jednom_po": "planu", "kolicina": "4 pitanja", "vrijeme": "nije izmjereno"},
    {"posao": "Provjeriti pravnu aktualnost plana u SN PGŽ", "jednom_po": "planu i svakom novom broju glasila", "kolicina": "1", "vrijeme": "nije izmjereno"},
    {"posao": "Utvrditi kategoriju ceste, ZK površinu i uvjet okruženja", "jednom_po": "čestici", "kolicina": "Q4, Q5, Q6", "vrijeme": "nije izmjereno"},
]
mjerenje = {"pokazatelji_po_stanju": dict(stanja), "karike_po_razini": dict(karike), "ulazi": [dict(zip(("podatak", "izvor", "stanje", "napomena"), u)) for u in ulazi],
            "ulazi_po_stanju": dict(Counter(u[2] for u in ulazi)), "cestica_u_obuhvatu_upu2": len(uob), "raspon_povrsina": dict(raspon),
            "strucni_rad": rad, "pravila": pravila_n, "clanaka": clanci_n, "trajanje_dosjea_s": D["trajanje_s"]}

podaci = {"dosje": {k: D[k] for k in ("naslov", "stanje_na_dan", "cestica", "geo_cinjenice", "pokazatelji", "otvorena_pitanja", "kandidati_zona", "izvori", "potvrde")},
          "pravila": [{**p, "tehnicki": next(t for t in D["pravila"]["tehnicka_provjera"] if t["id"] == p["id"])} for p in D["pravila"]["popis"]],
          "plan": D["pravila"]["plan"], "upu2": {k: v for k, v in D["planovi"]["upu2"].items() if k != "geometrija"},
          "u_izradi": D["planovi"]["u_izradi"], "rasteri_lista": D["rasteri_upu2"], "usporedba": D["pravila"]["usporedba_s_aplikacijom"],
          "karta": karta, "pregled": pregled, "rasteri": rasteri, "mjerenje": mjerenje}
podaci["dosje"]["cestica"] = {k: v for k, v in D["cestica"].items() if k != "geometrija"}
js = json.dumps(podaci, ensure_ascii=False).replace("</", "<\\/")
html = (P / "izvjestaj.template.html").read_text(encoding="utf-8").replace("__PODACI__", js)
out = P / "dist/gis_pilot_735_76.html"; out.write_text(html, encoding="utf-8")
mjerenje["trajanje_sastavljanja_s"] = round(time.perf_counter() - T0, 2)
(P / "dist/mjerenje.json").write_text(json.dumps(mjerenje, ensure_ascii=False, indent=1), encoding="utf-8")
print(out, len(html), hashlib.sha256(out.read_bytes()).hexdigest()[:12], mjerenje["trajanje_sastavljanja_s"], "s")
print(json.dumps({k: mjerenje[k] for k in ("pokazatelji_po_stanju", "karike_po_razini", "ulazi_po_stanju", "cestica_u_obuhvatu_upu2", "raspon_povrsina")}, ensure_ascii=False))

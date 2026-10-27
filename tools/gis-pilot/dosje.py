#!/usr/bin/env python3
"""GIS-first pilot: dosje jedne katastarske čestice bez AI čitanja plana.

    python3 tools/gis-pilot/dosje.py            → tools/gis-pilot/dist/dosje_735_76.json

Lanac za svaku ključnu tvrdnju: čestica → zona → plan → članak → pravilo → izračun.
Svaka karika nosi razinu dokaza; pokazatelj je »izračunat« samo kad su sve karike na prihvaćenoj razini,
»uvjetan« kad čeka stručnu potvrdu, a »nije izračunat« kad nedostaje podatak ili postoji neriješen sukob.
Pravna valjanost se ovdje nikad ne utvrđuje. Ništa se ne čita AI-jem; pravila su unaprijed pripremljena
(pravila_upu2_pripremljena.json) i provjerena samo strojno (doslovni citat u službenom tekstu).
"""
import hashlib, json, math, re, sys, time, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from pathlib import Path
from pyproj import Geod, Transformer
from shapely.geometry import shape, Polygon, Point
from shapely.ops import transform

T0 = time.perf_counter()
P = Path(__file__).resolve().parent
R = P.parents[1]                                   # korijen repozitorija
S22 = R / "tests/pgz-odgovori/735-76-kornic-2026-10-22"
S27 = P / "izvori/pgz-2026-10-27"
GEOD = Geod(ellps="GRS80")
TM = Transformer.from_crs(4326, 3765, always_xy=True)
CESTICA = {"broj": "735/76", "ko": "KORNIĆ", "ko_mb": "315907", "dgu_id": 19311099}
DAN = "2026-10-27"

RAZINE = {   # razina dokaza → opis; »prihvaćena« = smije ući u izračun bez dodatne potvrde
    "SLUZBENI_VEKTOR": ("službeni vektorski sloj (grafički, nije geodetska izmjera ni pravna potvrda)", True),
    "SLUZBENA_EVIDENCIJA": ("službena evidencija planova (PGŽ), nije pravna potvrda", True),
    "SLUZBENA_OBJAVA": ("članak postoji u službenoj objavi (SN PGŽ)", True),
    "SLUZBENI_TEKST": ("doslovni citat pronađen u službenoj objavi; strojno provjereno, nije stručno potvrđeno", False),
    "RASTER_KANDIDAT": ("vizualno očitanje georeferenciranog rastera; nije stručno potvrđeno", False),
    "STRUCNO_POTVRDENO": ("stručna potvrda (potvrde.json)", True),
    "IZRACUN": ("izračun iz prihvaćenih ulaza", True),
    "NEDOSTAJE": ("Podaci nisu dostupni", False),
}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p): return str(Path(p).relative_to(R))
def jl(p): return json.loads(Path(p).read_text(encoding="utf-8"))


# ---------- 0. izvori i kontrolne sume ----------
def izvori():
    m22 = jl(S22 / "_meta.json"); sn = jl(S22 / "sn-19-16/_meta.json"); k = jl(S22 / "karte/_meta.json")
    rows, greske = [], []
    def dodaj(ime, putanja, ocekivano, url, dohvat, opis):
        stvarno = sha(putanja)
        if ocekivano and stvarno != ocekivano: greske.append(ime)
        rows.append({"id": ime, "datoteka": rel(putanja), "sha256": stvarno, "sha_odgovara": (stvarno == ocekivano) if ocekivano else None,
                     "url": url, "dohvat": dohvat, "opis": opis})
    for f, v in m22["odgovori"].items():
        dodaj(f"pgz22:{f}", S22 / f, v["sha256"], v["url"], m22["retrieved_utc"], "PGŽ GEOPORTAL, odgovor servisa bajt-za-bajt")
    dodaj("sn19-16:pdf", S22 / "sn-19-16/odluka_34138.pdf", sn["pdf"]["sha256"], sn["pdf"]["url"], sn["pdf"]["retrieved_utc"], "SN PGŽ 19/2016, PDF izdanja (str. 2172–2232)")
    dodaj("sn19-16:html", S22 / "sn-19-16/odluka_34138.html", sn["sha256_html"], sn["url"], sn["retrieved_utc"], "SN PGŽ 19/2016, HTML objave (čl. 1.–53., 108.)")
    dodaj("sn19-16:pdf_tekst", S22 / "sn-19-16/odluka_34138_pdf_tekst.txt", None, sn["pdf"]["url"], sn["pdf"]["retrieved_utc"], "tekst odluke izdvojen iz PDF-a")
    m27 = jl(S27 / "_meta.json")
    for f, v in m27["odgovori"].items():
        if v.get("nije_preneseno"): continue
        dodaj(f"pgz27:{f}", S27 / f, v["sha256"], v["url"], v["date"], v["opis"])
    for kk in ("karta4", "karta3a"):
        dodaj(f"raster:{kk}", S22 / f"karte/{kk}_s_cesticom.png", None, "https://gisportal.pgz.hr/server/rest/services/PP_RASTERI/PP_RASTERI/MapServer/5/export",
              m22["retrieved_utc"][:10], f"izrez lista OBJECTID {k[kk]['objectid']} ±90 m, EPSG:3765, granica čestice ucrtana crveno")
    dodaj("dgu:cestica", R / "docs/primjeri/kornic_cestica_735_76.geojson", None, "https://oss.uredjenazemlja.hr/oss/public/atom/ko-315907.zip", "2026-10-19", "DGU DKP (ATOM), granica čestice")
    return rows, greske


# ---------- 1. čestica ----------
def dekodiraj(r):
    lon, lat = r[0], r[1]; pts = [(lon / 1e6, lat / 1e6)]
    for i in range(2, len(r), 2): lon += r[i]; lat += r[i + 1]; pts.append((lon / 1e6, lat / 1e6))
    return pts


def cestica():
    gj = jl(R / "docs/primjeri/kornic_cestica_735_76.geojson")["features"][0]
    poly = shape(gj["geometry"])
    c = poly.representative_point()
    idx = jl(R / "data/kat_krk/index.json")
    kv = f"{math.floor(c.y / idx['dlat'])}_{math.floor(c.x / idx['dlon'])}"
    zap = [x for x in jl(R / f"data/kat_krk/{kv}.json") if x[1] == CESTICA["broj"] and x[2] == CESTICA["ko_mb"]]
    assert len(zap) == 1, "čestica nije jednoznačna u lokalnom katastru"
    lok = Polygon(dekodiraj(zap[0][4][0][0]))
    odst = max(abs(a - b) for p, q in zip(lok.exterior.coords, poly.exterior.coords) for a, b in zip(p, q))
    pov = abs(GEOD.geometry_area_perimeter(poly)[0])
    return {
        "broj": CESTICA["broj"], "ko": CESTICA["ko"], "ko_mb": CESTICA["ko_mb"], "dgu_id": zap[0][0],
        "povrsina_graficka_dgu_m2": zap[0][3], "povrsina_iz_koordinata_m2": round(pov, 1),
        "lokalni_kvadrat": kv, "odstupanje_lokalno_vs_izvor_stupnjeva": odst,
        "geometrija": gj["geometry"], "tocka": [round(c.x, 6), round(c.y, 6)],
        "razina": "SLUZBENI_VEKTOR", "izvor": "dgu:cestica", "datum_podataka": gj["properties"]["datum_podataka"],
        "napomena": gj["properties"]["napomena"] + " Površina upisana u zemljišnu knjigu: Podaci nisu dostupni.",
    }, poly


# ---------- 2. planovi i zone ----------
def planovi(poly):
    danas = jl(S27 / "planovi_tocka.json")["features"]; prije = jl(S22 / "planovi_tocka_doc.json")["features"]
    A = {f["attributes"]["OBJECTID"]: f["attributes"] for f in danas}; B = {f["attributes"]["OBJECTID"]: f["attributes"] for f in prije}
    promjene = sorted({k for k in A if k in B for x in A[k] if A[k][x] != B[k].get(x) and x != "TrajanjeIzrade"} | (set(A) ^ set(B)))
    vazeci = [a for a in A.values() if a["STATUS_PP"] == "VAŽEĆI"]
    u_izradi = [a for a in A.values() if a["STATUS_PP"] == "U IZRADI"]
    def kratko(a): return {k: a.get(k) for k in ("OBJECTID", "IDPLAN", "VRSTA_PP", "STATUS_PP", "SN_BROJ", "NAZIV", "DatumDonPlana", "DatumObjPlana", "DatumStNaSnPlana", "DatumStVanSnage", "SN_LINK", "PDF_LINK_PUBLIC", "obradaKarataPP", "STATUS_GIS")}
    upu = [kratko(a) for a in vazeci if a["VRSTA_PP"] in ("UPU", "DPU")]
    ob = jl(S27 / "upu2_obuhvat.geojson")["features"][0]; obg = shape(ob["geometry"])
    tm = lambda g: transform(TM.transform, g)
    return {
        "zapisa_na_tocki": len(A), "promjene_od_22_10": promjene,
        "vazeci_detaljni": upu,
        "vazeci_svi": [kratko(a) for a in sorted(vazeci, key=lambda a: a["DatumStNaSnPlanaSORT"] or 0, reverse=True)],
        "u_izradi": [kratko(a) for a in u_izradi],
        "upu2": {"svojstva": ob["properties"], "geometrija": ob["geometry"], "povrsina_ha": round(abs(GEOD.geometry_area_perimeter(obg)[0]) / 1e4, 2),
                 "cestica_unutar": obg.contains(poly), "udaljenost_do_granice_m": round(tm(poly).distance(tm(obg.boundary)), 1),
                 "razina": "SLUZBENA_EVIDENCIJA", "izvor": "pgz27:upu2_obuhvat.geojson"},
    }, obg


def zone_ppug(poly):
    nam = jl(S22 / "namjena_cestica_app.geojson")["features"]
    tm = lambda g: transform(TM.transform, g); pc = tm(poly); a = pc.area
    out = []
    for f in nam:
        g = shape(f["geometry"]); i = tm(g).intersection(pc).area
        if i > 0:
            p = f["properties"]
            out.append({"oznaka": p["OZNAKA_NAMJENE"], "polazna": p["POLAZNA_NAMJENA"], "primarna": p["PRIMARNA_NAMJENA"], "izgradjenost": p.get("IZGRADJENOST"),
                        "naselje": p.get("NASELJE"), "izvor_sloja": p.get("IZVOR_PODATAKA"), "udio": round(i / a, 4), "m2": round(i, 1)})
    out.sort(key=lambda x: -x["udio"])
    t22 = sha(S22 / "namjena_tocka_doc.json"); t27 = jl(S27 / "_meta.json")["odgovori"]["namjena_tocka.json"]["sha256"]
    return {"zone": out, "razina": "SLUZBENI_VEKTOR", "izvor": "pgz22:namjena_cestica_app.geojson",
            "tocka_ista_27_10": t22 == t27,
            "geometrije": [{"oznaka": f["properties"]["OZNAKA_NAMJENE"], "geometrija": f["geometry"]} for f in nam]}


def rasteri():
    d = jl(S27 / "rasteri_tocka_sloj5.json")["features"]
    nazivi = jl(R / "src/rules_krk.json")["upu"]["UPU 2"]["karte"]["listovi"]
    lst = []
    for f in sorted(d, key=lambda f: f["attributes"]["KARTA_SIFRA"]):
        a = f["attributes"]; s = a["KARTA_SIFRA"].split("_karta")[-1]
        lst.append({"objectid": a["OBJECTID"], "datoteka": a["Name"], "sifra": a["KARTA_SIFRA"], "naslov": nazivi.get(s, {}).get("naziv", "Podaci nisu dostupni")})
    return lst


# ---------- 3. pravila: strojna provjera citata ----------
ZAGLAVLJA = re.compile(r"^(Petak, 29\. srpnja 2016\.|SLUŽBENE NOVINE|Stranica \d+ — broj 19|Broj 19 — Stranica \d+)$")


def tekst_clanaka():
    redovi = (S22 / "sn-19-16/odluka_34138_pdf_tekst.txt").read_text(encoding="utf-8").splitlines()
    cl, tren = {}, None
    for r in redovi:
        m = re.match(r"^Članak (\d+)\.$", r.strip())
        if m: tren = int(m.group(1)); cl[tren] = []; continue
        if tren is not None and not ZAGLAVLJA.match(r.strip()): cl[tren].append(r.strip())
    return {k: re.sub(r"\s+", " ", " ".join(v)) for k, v in cl.items()}


def norm(s): return re.sub(r"\s+", " ", s).strip()


def provjeri_pravila(cl):
    D = jl(P / "pravila_upu2_pripremljena.json")
    out = []
    for p in D["pravila"] + D["okvir"]:
        t = cl.get(p["clanak"], ""); c = norm(p["citat"])
        nadeno = t.count(c)
        vr = p.get("vrijednost"); brojke = []
        if isinstance(vr, (int, float)): brojke = [vr]
        elif isinstance(vr, dict): brojke = list(vr.values())
        elif isinstance(vr, list) and all(isinstance(x, (int, float)) for x in vr): brojke = vr
        if p.get("iznimka"): brojke.append(p["iznimka"]["vrijednost"])
        fmt = lambda x: (f"{x:g}".replace(".", ",") if isinstance(x, float) and x != int(x) else str(int(x)) if isinstance(x, float) else str(x))
        vrijednosti_u_citatu = all((fmt(b) + (" m2" if p.get("jedinica") == "m2" else "")) in c or (fmt(b) in c) or (p.get("jedinica") is None and isinstance(b, float) and f"{int(b*100)}%" in c) for b in brojke) if brojke else None
        if p.get("parametar") == "zelenilo_min_udio": vrijednosti_u_citatu = "40%" in c
        if p.get("vrijednost_u_tekstu"): vrijednosti_u_citatu = p["vrijednost_u_tekstu"] in c
        out.append({"id": p["id"], "clanak": p["clanak"], "nadeno_u_clanku": nadeno, "vrijednosti_u_citatu": vrijednosti_u_citatu,
                    "tehnicki": "PROVJERENO" if nadeno >= 1 and vrijednosti_u_citatu is not False else "NIJE_PROVJERENO"})
    return D, out


def usporedi_s_aplikacijom(D):
    """Usporedba vrijednosti s postojećim src/rules_krk.json (samo čitanje; ništa se ne prepisuje)."""
    U = jl(R / "src/rules_krk.json")["upu"]["UPU 2"]["tipovi"]
    par = {"min_povrsina_cestice": "minC", "kig_max": "izg", "kis_max": "kis", "tlocrt_max": "tlMax", "tlocrt_min": "tlMin"}
    out = []
    for p in D["pravila"]:
        k = par.get(p["parametar"])
        if not k: continue
        for tip in p["vrijedi_za"]["tip"]:
            for ob in p["vrijedi_za"].get("oblik", []):
                if tip not in U or ob not in U[tip]: continue
                v = p["vrijednost"]
                if isinstance(v, dict): v = v.get(tip, v.get(ob))
                a = U[tip][ob].get(k)
                if v is None or a is None: continue
                out.append({"pravilo": p["id"], "tip": tip, "oblik": ob, "parametar": p["parametar"], "pilot": v, "aplikacija": a, "isto": float(v) == float(a)})
    return out


# ---------- 4. zone na rasteru: kandidati ----------
def kandidati_zona():
    return [
        {"predmet": "zona_upu", "vrijednost": "M11", "karta": "618_karta4 (4. Način i uvjeti gradnje), OBJECTID 7104", "razina": "RASTER_KANDIDAT",
         "tko_ocitao": "razvoj (Claude), vizualno, 22. 10. 2026. (tests/pgz-odgovori/…/USPOREDBA.md)", "izvor": "raster:karta4",
         "zasto_nije_vektor": "PGŽ katalog daje samo georeferencirani TIFF bez legende i bez vektorskih granica zona (obradaKarataPP = »5 - u raster katalogu«)",
         "napomena": "Čestica je u žutoj površini; najbliža oznaka je »M1₁« (M11) oko 60 m jugozapadno; granica obuhvata (crna isprekidana) prolazi oko 6 m istočno."},
        {"predmet": "zona_zastite", "vrijednost": "C", "karta": "618_karta3a (3A. Područja posebnih uvjeta korištenja …), OBJECTID 7102", "razina": "RASTER_KANDIDAT",
         "tko_ocitao": "razvoj (Claude), vizualno, 22. 10. 2026.", "izvor": "raster:karta3a",
         "napomena": "Čestica je unutar plavog šrafa zone zaštite; natpis »ZONA C« nije u izrezu ±90 m, nego na listu. Zona »B« je prema popisu rubnih čestica iz čl. 83. vrlo vjerojatno 80 m+ dalje (27 od 72 rubnih čestica ne postoji u današnjem katastru)."},
    ]


# ---------- 5. pokazatelji uz pravila odvajanja razina ----------
def razina_ulaza(predmet, osnovna, potvrde):
    p = [x for x in potvrde if x["predmet"] == predmet]
    if p: return "STRUCNO_POTVRDENO", p[-1]
    return osnovna, None


def pokazatelji(ces, D, teh, kand, potvrde):
    A = ces["povrsina_graficka_dgu_m2"]
    pr = {p["id"]: p for p in D["pravila"]}; th = {t["id"]: t for t in teh}
    kz = {k["predmet"]: k for k in kand}
    tipovi = [("obit", "slob", "U2-38-a1", "U2-38-a3", "U2-38-b2", "U2-38-b6"), ("obit", "dvoj", "U2-39-a1", "U2-39-a2", "U2-39-b2", "U2-39-b6"),
              ("obit", "ugr", "U2-39-a1", "U2-39-a2", "U2-39-b2", "U2-39-b6"), ("visobit", "slob", "U2-38-a2", "U2-38-a3", "U2-38-b2", "U2-38-b6"),
              ("visobit", "dvoj", "U2-39-a1", "U2-39-a2", "U2-39-b2", "U2-39-b6"), ("stamb", "slob", "U2-40-a1", None, None, None)]
    NAZ = {"obit": "obiteljska kuća", "visobit": "višeobiteljska kuća", "stamb": "stambena građevina", "slob": "slobodnostojeća", "dvoj": "dvojna", "ugr": "ugrađena"}
    out = []

    def lanac(pravila, zona_potrebna=True, zastita=False):
        k = [{"karika": "čestica", "vrijednost": f"{ces['broj']} k.o. {ces['ko']}, {A:g} m² (grafička)", "razina": ces["razina"], "izvor": ces["izvor"]},
             {"karika": "plan", "vrijednost": "UPU 2 Kornić (SN PGŽ 19/2016), VAŽEĆI prema evidenciji PGŽ 27. 10. 2026.; čestica u obuhvatu", "razina": "SLUZBENA_EVIDENCIJA", "izvor": "pgz27:upu2_obuhvat.geojson"}]
        if zona_potrebna:
            r, p = razina_ulaza("zona_upu", kz["zona_upu"]["razina"], potvrde)
            k.insert(1, {"karika": "zona", "vrijednost": (p or kz["zona_upu"])["vrijednost"], "razina": r, "izvor": kz["zona_upu"]["izvor"]})
        if zastita:
            r, p = razina_ulaza("zona_zastite", kz["zona_zastite"]["razina"], potvrde)
            k.insert(2, {"karika": "zona zaštite", "vrijednost": (p or kz["zona_zastite"])["vrijednost"], "razina": r, "izvor": kz["zona_zastite"]["izvor"]})
        for pid in pravila:
            p = pr[pid]; r, _ = razina_ulaza("pravilo:" + pid, "SLUZBENI_TEKST" if th[pid]["tehnicki"] == "PROVJERENO" else "NEDOSTAJE", potvrde)
            k.append({"karika": "članak", "vrijednost": f"čl. {p['clanak']}." + (f" {p['tocka']})" if p.get("tocka") else (f" st. {p['stavak']}." if p.get("stavak") else "")), "razina": "SLUZBENA_OBJAVA", "izvor": "sn19-16:pdf"})
            k.append({"karika": "pravilo", "vrijednost": pid, "citat": p["citat"], "razina": r, "izvor": "pravila_upu2_pripremljena.json"})
        return k

    def stanje(k, blok=None):
        if blok: return "NIJE_IZRACUNATO", [blok]
        ceka = list(dict.fromkeys(f"{x['karika']} {x['vrijednost']}: {RAZINE[x['razina']][0]}" for x in k if not RAZINE[x["razina"]][1]))
        return ("UVJETNO", ceka) if ceka else ("IZRACUNATO", [])

    # zona mora biti među dopuštenima (čl. 37. st. 2.); provjera se radi nad vrijednošću (kandidat ili potvrda)
    r_zona, pz = razina_ulaza("zona_upu", kz["zona_upu"]["razina"], potvrde)
    zona = (pz or kz["zona_upu"])["vrijednost"]
    zona_ok = zona in pr["U2-37-2"]["vrijednost"]
    _, pzs = razina_ulaza("zona_zastite", kz["zona_zastite"]["razina"], potvrde)
    zast = (pzs or kz["zona_zastite"])["vrijednost"]
    blok_svi = None if zona_ok else f"zona {zona} nije među dopuštenima za stambenu gradnju (čl. 37. st. 2.)"
    if zast == "B": blok_svi = "zona »B« (kulturno-povijesna cjelina): čl. 84. traži posebne konzervatorske uvjete; pilot ne računa uvjete gradnje"

    for tip, ob, rmin, rkig, rtl, rgbp in tipovi:
        p = pr[rmin]; v = p["vrijednost"]; v = v[tip] if isinstance(v, dict) else v
        zap = {"id": f"min_cestica:{tip}:{ob}", "pokazatelj": f"Najmanja čestica – {NAZ[tip]}, {NAZ[ob]}", "trazi": v, "ima": A}
        if A >= v: zap["rezultat"] = "ispunjeno"
        elif p.get("iznimka") and A >= p["iznimka"]["vrijednost"]:
            zap["rezultat"] = f"samo iznimno ({p['iznimka']['vrijednost']} m²): {p['iznimka']['uvjet']} – uvjet se iz podataka ne može provjeriti"
        else: zap["rezultat"] = "nije ispunjeno"
        zap["rezerva_m2"] = round(A - v, 1)
        k = lanac(["U2-37-2", rmin]); zap["lanac"] = k
        zap["stanje"], zap["ceka"] = stanje(k, blok_svi)
        if zap["rezultat"].startswith("samo iznimno") and zap["stanje"] != "NIJE_IZRACUNATO":
            zap["stanje"] = "UVJETNO"; zap["ceka"].append("uvjet iznimke: " + p["iznimka"]["uvjet"] + " (Q4)")
        out.append(zap)
        if rkig and A >= (p.get("iznimka") or {}).get("vrijednost", v):
            kig = pr[rkig]["vrijednost"]; tl = pr[rtl]["vrijednost"]; tl = tl[ob] if isinstance(tl, dict) else tl
            z = {"id": f"tlocrt_max:{tip}:{ob}", "pokazatelj": f"Najveća tlocrtna površina – {NAZ[tip]}, {NAZ[ob]}", "formula": f"min(kig {kig} × {A:g} m², {tl} m²)",
                 "vrijednost_m2": round(min(kig * A, tl), 1), "lanac": lanac(["U2-37-2", rkig, rtl])}
            z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
            kis = pr[rkig.replace("a3", "a4") if rkig.startswith("U2-38") else "U2-39-a3"]["vrijednost"]; gb = pr[rgbp]["vrijednost"][tip]
            z = {"id": f"gbp_max:{tip}:{ob}", "pokazatelj": f"Najveći GBP na čestici – {NAZ[tip]}, {NAZ[ob]}", "formula": f"min(kis {kis} × {A:g} m², {gb} m² za sve građevine na čestici)",
                 "vrijednost_m2": round(min(kis * A, gb), 1), "lanac": lanac(["U2-37-2", rkig.replace("a3", "a4") if rkig.startswith("U2-38") else "U2-39-a3", rgbp]),
                 "otvoreno": "Uračunava li se podrum u kis: tekst ne kaže izričito (kis bez riječi »nadzemni«)."}
            z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)

    z = {"id": "zelenilo_min", "pokazatelj": "Najmanja površina zelenila", "formula": f"0,4 × {A:g} m²", "vrijednost_m2": round(0.4 * A, 1), "lanac": lanac(["U2-37-2", "U2-38-g2"])}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    z = {"id": "etaze", "pokazatelj": "Najveći broj nadzemnih etaža", "vrijednost": "2 (uz podrum)", "lanac": lanac(["U2-37-2", "U2-38-b3"] + (["U2-85-2b"] if zast == "C" else []), zastita=True),
         "napomena": "Čl. 38. b) i čl. 85. (zona »C«) daju istu granicu od 2 nadzemne etaže. Iznimka čl. 38. b) al. 5 (3 nadzemne na nagibu > 12 %) za višeobiteljsku kuću je s čl. 85. u sukobu (Q10); nagib terena: Podaci nisu dostupni."}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    z = {"id": "visina", "pokazatelj": "Najveća visina građevine", "vrijednost": "7,5 m", "lanac": lanac(["U2-37-2", "U2-38-b4"])}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    z = {"id": "meda", "pokazatelj": "Najmanja udaljenost od ostalih međa", "vrijednost": "4 m (3 m bez otvora prema međi)", "lanac": lanac(["U2-37-2", "U2-38-c4"])}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    z = {"id": "parkiranje", "pokazatelj": "Parkirališna mjesta na čestici", "vrijednost": "2 po stanu", "lanac": lanac(["U2-37-2", "U2-38-h3"])}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    # namjerno se ne računa
    z = {"id": "regulacija", "pokazatelj": "Udaljenost od regulacijskog pravca", "lanac": lanac(["U2-37-2", "U2-38-c1", "U2-38-c2"])}
    z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi or "Kategorija ceste uz česticu (javna ili nerazvrstana) i položaj regulacijskog pravca: Podaci nisu dostupni."); out.append(z)
    if zast == "C":
        z = {"id": "krov", "pokazatelj": "Nagib kosog krova", "lanac": lanac(["U2-37-2", "U2-38-d2", "U2-85-2c"], zastita=True)}
        z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi or "Sukob pravila: čl. 38. d) 17°–23° ili ravni krov; čl. 85. za zonu »C« kosi krov oko 30° (Q3). Koje pravilo prevladava, mora reći stručnjak."); out.append(z)
        z = {"id": "konzervatorski", "pokazatelj": "Posebni konzervatorski uvjeti", "vrijednost": "potrebni za svaku novu gradnju", "lanac": lanac(["U2-85-2f"], zona_potrebna=False, zastita=True)}
        z["stanje"], z["ceka"] = stanje(z["lanac"]); out.append(z)
    else:
        z = {"id": "krov", "pokazatelj": "Nagib kosog krova", "vrijednost": "ravni ili kosi 17°–23°", "lanac": lanac(["U2-37-2", "U2-38-d2"], zastita=True)}
        z["stanje"], z["ceka"] = stanje(z["lanac"], blok_svi); out.append(z)
    for x in out: x["pravna_valjanost"] = "NIJE_UTVRDENA"
    return out


def otvorena_pitanja(ces, pl, zp):
    A = ces["povrsina_graficka_dgu_m2"]
    return [
        {"id": "Q1", "pitanje": "Je li čestica u zoni M11 na karti 4 UPU-a 2?", "zasto": "Zona postoji samo na rasteru; o njoj ovise svi pokazatelji gradnje.", "tko": "stručnjak (urbanist) ili lokacijska informacija Grada Krka"},
        {"id": "Q2", "pitanje": "Je li čestica u zoni zaštite »C« (karta 3A) i izvan zone »B«?", "zasto": "Zona »C« mijenja krov i traži konzervatorske uvjete (čl. 85.); zona »B« bi isključila izračun (čl. 84.).", "tko": "stručnjak ili konzervatorski odjel"},
        {"id": "Q3", "pitanje": "Vrijedi li za zonu »C« kosi krov oko 30° umjesto 17°–23° iz čl. 38. d)?", "zasto": "Dva članka istog plana daju različite nagibe.", "tko": "stručnjak; pravno tumačenje"},
        {"id": "Q4", "pitanje": "Je li čestica »u okruženju već uređenih i izgrađenih građevnih čestica« (iznimka 400 m², čl. 38. a)?", "zasto": f"Grafička površina {A:g} m² < 500 m²; slobodnostojeća obiteljska kuća moguća je samo po iznimci.", "tko": "stručnjak / lokacijska informacija"},
        {"id": "Q5", "pitanje": "Kolika je površina čestice upisana u zemljišnu knjigu?", "zasto": f"Dvojna višeobiteljska kuća traži 400 m²; rezerva je samo {A - 400:g} m² grafičke površine.", "tko": "vlasnik (ZK izvadak) ili geodet"},
        {"id": "Q6", "pitanje": "Je li cesta uz istočnu među javna ili nerazvrstana i gdje je regulacijski pravac?", "zasto": "O tome ovisi udaljenost 6/9 m ili 4/7 m (čl. 38. c).", "tko": "Grad Krk (registar nerazvrstanih cesta) / geodet"},
        {"id": "Q7", "pitanje": "Je li UPU 2 nakon SN 19/2016 mijenjan ili ukinut?", "zasto": "Evidencija PGŽ 27. 10. 2026. nema izmjena UPU-a 2 ni postupka u izradi, ali pravna aktualnost nije neovisno potvrđena.", "tko": "pravna provjera u SN PGŽ"},
        {"id": "Q8", "pitanje": "Stupanje na snagu: 05.08.2016. (evidencija) ili 06.08.2016. (čl. 108., osmi dan od objave 29.07.)?", "zasto": "Razlika od jednog dana između sloja i računanja roka.", "tko": "pravna provjera"},
        {"id": "Q10", "pitanje": "Može li višeobiteljska kuća na nagibu > 12 % imati 3 nadzemne etaže u zoni »C«?", "zasto": "Čl. 38. b) al. 5 to dopušta, čl. 85. ograničava na dvije nadzemne etaže.", "tko": "stručnjak; pravno tumačenje"},
        {"id": "Q9", "pitanje": "Uračunava li se podrum u koeficijent iskorištenosti (kis 0,75)?", "zasto": "Tekst kaže samo »koeficijent iskorištenosti«; o tome ovisi najveći GBP.", "tko": "stručnjak"},
    ]


def main():
    izv, greske = izvori()
    if greske: print("SHA ne odgovara:", greske); sys.exit(1)
    ces, poly = cestica()
    pl, ob = planovi(poly)
    zp = zone_ppug(poly)
    cl = tekst_clanaka()
    D, teh = provjeri_pravila(cl)
    potvrde = jl(P / "potvrde.json")["potvrde"]
    kand = kandidati_zona()
    pok = pokazatelji(ces, D, teh, kand, potvrde)
    na2 = next(z for z in zp["zone"] if z["oznaka"] == "NA2")
    geo = [
        {"id": "G1", "tvrdnja": f"Čestica {ces['broj']} k.o. {ces['ko']} ima grafičku površinu {ces['povrsina_graficka_dgu_m2']:g} m² (iz koordinata {ces['povrsina_iz_koordinata_m2']:g} m²).", "razina": "SLUZBENI_VEKTOR", "izvor": "dgu:cestica", "stanje": "IZRACUNATO"},
        {"id": "G2", "tvrdnja": f"Čestica je cijela unutar vektorskog obuhvata UPU-a 2 Kornić (IDPLAN 618); granica obuhvata je {pl['upu2']['udaljenost_do_granice_m']:g} m od čestice.", "razina": "SLUZBENA_EVIDENCIJA", "izvor": "pgz27:upu2_obuhvat.geojson", "stanje": "IZRACUNATO" if pl["upu2"]["cestica_unutar"] else "NIJE_IZRACUNATO"},
        {"id": "G3", "tvrdnja": f"Prema PPUG-u Krka (sloj PGŽ, izvor SN 18/19) {na2['udio']*100:.2f} % čestice je u zoni NA2 (građevinsko područje naselja Kornić, izgrađeni dio); ostatak {100-na2['udio']*100:.2f} % (P3) je rubni dodir granica.", "razina": "SLUZBENI_VEKTOR", "izvor": "pgz22:namjena_cestica_app.geojson", "stanje": "IZRACUNATO"},
        {"id": "G4", "tvrdnja": "Čl. 1. UPU-a 2: obuhvat je građevinsko područje naselja Kornić NA 2 – podudara se s G3.", "razina": "SLUZBENA_OBJAVA", "izvor": "sn19-16:pdf", "stanje": "IZRACUNATO"},
        {"id": "G5", "tvrdnja": f"Evidencija PGŽ (27. 10. 2026.): UPU 2 Kornić VAŽEĆI, SN 2016-19, na snazi od 05.08.2016., bez datuma prestanka; za točku nema UPU/DPU u izradi. Promjene zapisa od 22. 10.: {'nema' if not pl['promjene_od_22_10'] else pl['promjene_od_22_10']} (osim brojača dana izrade).", "razina": "SLUZBENA_EVIDENCIJA", "izvor": "pgz27:planovi_tocka.json", "stanje": "IZRACUNATO"},
        {"id": "G6", "tvrdnja": f"Detaljne zone UPU-a 2 postoje samo na rasteru: katalog PGŽ za točku daje {len(rasteri())} listova, nijedan vektorski sloj zona.", "razina": "SLUZBENA_EVIDENCIJA", "izvor": "pgz27:rasteri_tocka_sloj5.json", "stanje": "IZRACUNATO"},
    ]
    dosje = {
        "naslov": f"Dosje čestice {ces['broj']} k.o. {ces['ko']} (GIS-first pilot)", "stanje_na_dan": DAN,
        "status": "pilot, nije produkcija; ništa nije pravno potvrđeno", "razine_dokaza": {k: v[0] for k, v in RAZINE.items()},
        "izvori": izv, "cestica": ces, "planovi": pl, "zone_ppug": zp, "rasteri_upu2": rasteri(), "kandidati_zona": kand,
        "pravila": {"plan": D["plan"], "status_pripreme": D["status_pripreme"], "popis": D["pravila"], "okvir": D["okvir"], "tehnicka_provjera": teh,
                    "usporedba_s_aplikacijom": usporedi_s_aplikacijom(D)},
        "potvrde": potvrde, "geo_cinjenice": geo, "pokazatelji": pok, "otvorena_pitanja": otvorena_pitanja(ces, pl, zp),
        "trajanje_s": None,
    }
    dosje["trajanje_s"] = round(time.perf_counter() - T0, 3)
    out = P / "dist/dosje_735_76.json"; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dosje, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print(out, dosje["trajanje_s"], "s;", Counter(x["stanje"] for x in pok), "; pravila tehnički:", Counter(t["tehnicki"] for t in teh))
    return dosje


if __name__ == "__main__":
    main()

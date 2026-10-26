#!/usr/bin/env python3
"""EKSPERIMENT v2.1: usporedba gramatike v2.1 sa zamrznutim neovisnim oznakama (22./23. i 25./33.) i regresije.

1. Provjera integriteta svih zamrznutih datoteka v1 i obaju skupova oznaka (prekid ako se nešto promijenilo).
2. PPUG Krk dio 1 (čl. 4.–173.) kroz strukturiraj_v2 → izlaz/ppug_v2_1.json.
3. Čl. 22./23.: zamrznuti usporednik ocijeni_neovisno.py i zamrznuto mapiranje v1 nad pravilima čiji parametar oznake
   pokrivaju; ostala pravila su IZVAN_OPSEGA_OZNAKA (ne broje se ni kao točna ni kao pogrešna). Usporedba s v1 po oznaci.
4. Čl. 25./33.: zasebno, verzionirano mapiranje (oznake/neovisno_cl25_33/mapiranje_v2.json).
5. Prijedlozi u ostalim člancima PPUG-a (nisu označeni: popis za neovisni pregled).
6. UPU 2: obrasci v1 bez izmjena; ocijeni.py → mora ostati 92 / 0 / 7 / 0.
7. Determinizam: dva prolaza moraju dati isti SHA-256.

    python3 usporedi_v2.py
"""
import copy, hashlib, json, re
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v2 as s2
import ocijeni_neovisno as on
import ocijeni as oc

M = Path(__file__).resolve().parent
IZVOR = "slijepo/ppug_krk/ppug_krk_sn_2020_29.html"
OZ22 = "oznake/neovisno/neovisne_oznake_ppug_22_23.json"
OZ25 = "oznake/neovisno_cl25_33/neovisne_oznake_ppug_25_33.json"
OZ25_SHA = "b47d15c3f8d8005e53f9d1f44414155658177c30e16cf64e29a4f626f03c452d"
MAPA25 = "oznake/neovisno_cl25_33/mapiranje_v2.json"
sha = lambda p: hashlib.sha256((M / p).read_bytes()).hexdigest()
J = lambda p: json.loads((M / p).read_text(encoding="utf-8"))


def provjeri_integritet():
    z = J("ZAMRZNUTO_v1.json")
    los = [p for g in ("kod", "izvor", "izlazi", "referentne_oznake", "za_oznacavanje") for p, s in z[g].items() if sha(p) != s]
    if sha(OZ25) != OZ25_SHA:
        los.append(OZ25)
    if los:
        raise SystemExit("INTEGRITET NIJE POTVRĐEN, razvoj zaustavljen: " + ", ".join(los))
    return {"ZAMRZNUTO_v1.json": "sve kontrolne sume odgovaraju", OZ25: OZ25_SHA}


def pokreni_ppug():
    d = izdvoji_tekst(M / IZVOR, dio=1)
    return s2.strukturiraj(d, None, "PPUG Krk")


# ---------------------------------------------------------------- 22./23.
def usporedi_22_23(r):
    Mv1 = J("oznake/neovisno/mapiranje.json")
    oz = J(OZ22)
    sub = {"clanci": {}}
    izvan = []
    for k in ("22", "23"):
        c = copy.deepcopy(r["clanci"][k])
        izvan += [p for p in c["pravila"] if p["parametar"] not in Mv1["parametri"]]
        c["pravila"] = [p for p in c["pravila"] if p["parametar"] in Mv1["parametri"]]
        sub["clanci"][k] = c
    s, rez = on.ocijeni(sub, oz, Mv1)
    # v1 po oznaci
    v1 = J("izlaz/ppug_22_23_gramatika_v1.json")
    s1, rez1 = on.ocijeni(v1, oz, Mv1)
    razred = lambda R: {**{x["oznaka"]: "TOČNO" for x in R["tocno"]}, **{x["oznaka"]: "PREGLED" for x in R["pregled"] if x["oznaka"]},
                        **{z["id"]: "PROPUŠTENO" for z in R["propusteno"]}}
    a, b = razred(rez1), razred(rez)
    promjene = [{"oznaka": i, "v1": a.get(i), "v2_1": b.get(i), "razlozi_v2_1": next((x["zapis"]["razlozi"] for x in rez["pregled"] if x["oznaka"] == i), None)}
                for i in sorted(set(a) | set(b)) if a.get(i) != b.get(i)]
    return {"v1": s1, "v2_1": s, "promjene_po_oznaci": promjene,
            "pogresno": [x["zapis"] for x in rez["pogresno"]],
            "izvan_opsega_oznaka": [{"clanak": p["clanak"], "stavak": p["stavak"], "tocka": p["tocka"], "alineja": p["alineja"], "parametar": p["parametar"],
                                     "operator": p["operator"], "vrijednost": p["vrijednost"], "status": p["status"], "razlog_kod": p["razlog_kod"]} for p in izvan],
            "napomena_izvan_opsega": "Oznake 22./23. izričito ne pokrivaju sve opisne obveze (metapodaci.limitations); ova pravila nisu ocijenjena."}


# ---------------------------------------------------------------- 25./33.
def _gradevina(p, MP):
    vg = p["vrsta_gradevine"]
    sk = "+".join(vg["skupine"] or [])
    s = MP["skupine"].get(sk, sk)
    if vg["oblici"]:
        ob = "+".join(vg["oblici"])
        s += " – " + MP["oblici"].get(ob, ob)
    if vg["stanje"]:
        s += MP["stanje"][vg["stanje"]]
    if vg["uz_podrum"]:
        s += MP["uz_podrum"]
    return s


def u_zapise_25(pravila, MP):
    out, intervali = [], {}
    for p in pravila:
        par = p["parametar"]
        if p.get("interval"):
            k = (p["clanak"], p["stavak"], p["tocka"], p["alineja"], p["interval"])
            intervali.setdefault(k, []).append(p)
            continue
        out.append(_zapis(p, MP, MP["parametri"].get(par, "?" + par), MP["operatori"].get(p["operator"], p["operator"]), p["vrijednost"], [p]))
    for k, ps in intervali.items():
        mn = next((q for q in ps if q["operator"] == ">="), None); mx = next((q for q in ps if q["operator"] == "<="), None)
        if mn and mx and len(ps) == 2:
            v = f"{mn['vrijednost']:g}–{mx['vrijednost']:g}"
            out.append(_zapis(mn, MP, MP["parametri"].get(k[4], k[4]), "izmedju", v, [mn, mx]))
        else:
            out += [_zapis(q, MP, MP["parametri"].get(q["parametar"], "?" + q["parametar"]), q["operator"], q["vrijednost"], [q]) for q in ps]
    return out


def _zapis(p, MP, par, op, v, komponente):
    if p["operator"] == "nije_propisano":
        jed = None
    elif p.get("vrijednost_vrsta") == "opis":
        jed = "opis"
    elif p["jedinica"] is None and isinstance(v, (int, float)):
        jed = "koeficijent"
    else:
        jed = p["jedinica"]
    if isinstance(v, str):
        v = MP["vrijednosti"].get(v, v)
    return {"clanak": p["clanak"], "stavak": p["stavak"], "tocka": p["tocka"], "vrsta_gradevine": _gradevina(p, MP), "parametar": par,
            "operator": op, "vrijednost": v, "jedinica": jed, "vrsta_pravila": p["vrsta_pravila"],
            "uvjet_tekst": " | ".join((p["uvjeti"] or []) + [x for x in (p.get("opseg"), p.get("referenca")) if x]),
            "status": "PREGLED" if any(q["status"] == "PREGLED" for q in komponente) else "PRIJEDLOG",
            "razlog_kod": sorted({k for q in komponente for k in q["razlog_kod"]}),
            "komponente": [{"id": q["id"], "parametar": q["parametar"], "operator": q["operator"], "vrijednost": q["vrijednost"], "status": q["status"]} for q in komponente],
            "iznimke": [i for q in komponente for i in q["iznimke"]], "id": komponente[0]["id"], "izvorni_citat": p["izvorni_citat"]}


def _nv(x):
    return re.sub(r"\s+", " ", str(x)).strip().lower().replace("–", "-")


def razlike(z, o, MP):
    """Polja po kojima se zapis modula z razlikuje od oznake o (prazno = isto)."""
    r = []
    for k in ("clanak", "stavak", "tocka", "parametar", "operator", "jedinica", "vrsta_pravila"):
        if z[k] != o[k]:
            r.append(k)
    dozv = MP["vrsta_gradevine_istoznacnice"].get(z["vrsta_gradevine"], [])
    dozv = {z["vrsta_gradevine"]} | ({dozv} if isinstance(dozv, str) else set(dozv))
    if o["vrsta_gradevine"] not in dozv:
        r.append("vrsta_gradevine")
    a, b = z["vrijednost"], o["vrijednost"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs(a - b) > 1e-9:
            r.append("vrijednost")
    elif _nv(a) != _nv(b):
        r.append("vrijednost")
    dijelovi = [re.sub(r"^iznimno,?\s*", "", d.strip(), flags=re.I) for d in (o["uvjet_primjene"] or "").split("; ") if d.strip()]
    dijelovi = [d for d in dijelovi if d]
    if dijelovi:
        if not all(_nv(d) in _nv(z["uvjet_tekst"]) for d in dijelovi):
            r.append("uvjet")
    elif z["uvjet_tekst"]:
        r.append("uvjet")
    return r


def usporedi_25_33(r):
    MP = J(MAPA25)
    assert MP["oznake_sha256"] == OZ25_SHA
    Z = J(OZ25)["zapisi"]
    pravila = [p for k in ("25", "33") for p in r["clanci"].get(k, {}).get("pravila", [])]
    zap = u_zapise_25(pravila, MP)
    uzeto = [False] * len(Z)
    rez = {"tocno": [], "pogresno": [], "pregled": [], "propusteno": []}
    for z in zap:
        i = next((i for i, o in enumerate(Z) if not uzeto[i] and not razlike(z, o, MP)), None)
        if i is not None:
            uzeto[i] = True
        if z["status"] == "PREGLED":
            rez["pregled"].append({"zapis": z, "oznaka": Z[i]["id"] if i is not None else None})
        elif i is None:
            rez["pogresno"].append({"zapis": z, "najbliza_oznaka": _najbliza(z, Z, MP)})
        else:
            rez["tocno"].append({"zapis": z, "oznaka": Z[i]["id"]})
    for i, o in enumerate(Z):
        if not uzeto[i]:
            rez["propusteno"].append({"oznaka": o["id"], "najblizi_zapis": _najblizi(o, zap, MP)})
    po_oznaci = {}
    for x in rez["tocno"]:
        po_oznaci[x["oznaka"]] = "TOČNO"
    for x in rez["pregled"]:
        if x["oznaka"]:
            po_oznaci[x["oznaka"]] = "PREGLED"
    for x in rez["propusteno"]:
        po_oznaci[x["oznaka"]] = "PROPUŠTENO"
    sazetak = {}
    for c in (25, 33):
        zc = [o for o in Z if o["clanak"] == c]
        sazetak[str(c)] = {
            "oznaka": len(zc), "zapisa_modula": sum(1 for z in zap if z["clanak"] == c),
            "tocno": sum(1 for x in rez["tocno"] if x["zapis"]["clanak"] == c),
            "pogresno": sum(1 for x in rez["pogresno"] if x["zapis"]["clanak"] == c),
            "pregled": sum(1 for x in rez["pregled"] if x["zapis"]["clanak"] == c),
            "pregled_odgovara_oznaci": sum(1 for x in rez["pregled"] if x["zapis"]["clanak"] == c and x["oznaka"]),
            "pregled_bez_oznake": sum(1 for x in rez["pregled"] if x["zapis"]["clanak"] == c and not x["oznaka"]),
            "propusteno": sum(1 for o in zc if po_oznaci.get(o["id"]) == "PROPUŠTENO"),
            "po_jednoznacnosti_oznake": {j: {k: sum(1 for o in zc if o["jednoznacnost"] == j and po_oznaci.get(o["id"]) == k)
                                             for k in ("TOČNO", "PREGLED", "PROPUŠTENO")} for j in ("JASAN", "PREGLED")},
            "po_vrsti_pravila_oznake": {v: {k: sum(1 for o in zc if o["vrsta_pravila"] == v and po_oznaci.get(o["id"]) == k)
                                            for k in ("TOČNO", "PREGLED", "PROPUŠTENO")} for v in sorted({o["vrsta_pravila"] for o in zc})}}
    # povezanost iznimaka (dijagnostika, ne ulazi u razrede)
    id_oz = {x["zapis"]["id"]: x["oznaka"] for x in rez["tocno"] + rez["pregled"] if x["oznaka"]}
    iznimke = []
    for o in Z:
        z = next((x["zapis"] for x in rez["tocno"] + rez["pregled"] if x["oznaka"] == o["id"]), None)
        if z is not None:
            mod = sorted({id_oz.get(i) for i in z["iznimke"] if id_oz.get(i)})
            if mod or o["iznimke"]:
                iznimke.append({"oznaka": o["id"], "iznimke_oznaka": o["iznimke"], "iznimke_modula": mod, "isto": sorted(o["iznimke"]) == mod})
    jasne_ne_tocne = [{"oznaka": o["id"], "razred": po_oznaci.get(o["id"]), "parametar": o["parametar"], "vrijednost": o["vrijednost"],
                       "razlog_modula": next((x["zapis"]["razlog_kod"] for x in rez["pregled"] if x["oznaka"] == o["id"]), None)}
                      for o in Z if o["jednoznacnost"] == "JASAN" and po_oznaci.get(o["id"]) != "TOČNO"]
    return {"sazetak": sazetak, "jasne_oznake_koje_nisu_tocne": jasne_ne_tocne, "povezanost_iznimaka": iznimke,
            "detalji": {"tocno": [{"oznaka": x["oznaka"], "id": x["zapis"]["id"]} for x in rez["tocno"]],
                        "pregled": [{"oznaka": x["oznaka"], "id": x["zapis"]["id"], "parametar": x["zapis"]["parametar"], "vrijednost": x["zapis"]["vrijednost"],
                                     "razlog_kod": x["zapis"]["razlog_kod"]} for x in rez["pregled"]],
                        "pogresno": rez["pogresno"], "propusteno": rez["propusteno"]},
            "zapisi_modula": zap}


def _najbliza(z, Z, MP):
    k = [(len(razlike(z, o, MP)), o["id"], razlike(z, o, MP)) for o in Z if o["clanak"] == z["clanak"]]
    return min(k)[1:] if k else None


def _najblizi(o, zap, MP):
    k = [(len(razlike(z, o, MP)), z["id"], razlike(z, o, MP)) for z in zap if z["clanak"] == o["clanak"]]
    return min(k)[1:] if k else None


# ---------------------------------------------------------------- ostali članci, UPU 2, determinizam
def ostali_prijedlozi(r, oznaceni=("22", "23", "25", "33")):
    out = []
    for k, c in r["clanci"].items():
        if k in oznaceni:
            continue
        for p in c.get("pravila", []):
            out.append({"clanak": p["clanak"], "stavak": p["stavak"], "tocka": p["tocka"], "alineja": p["alineja"], "parametar": p["parametar"],
                        "operator": p["operator"], "vrijednost": p["vrijednost"], "jedinica": p["jedinica"], "status": p["status"],
                        "razlog_kod": p["razlog_kod"], "izvorni_citat": p["izvorni_citat"]})
    return {"clanci_s_pravilima": sorted({x["clanak"] for x in out}), "prijedlog": sum(x["status"] == "PRIJEDLOG" for x in out),
            "pregled": sum(x["status"] == "PREGLED" for x in out), "pravila": out,
            "napomena": "Ovi članci nisu neovisno označeni; prijedlozi se ne smiju smatrati točnima bez neovisnog pregleda."}


def upu2():
    d = J("izlaz/upu2_kornic_sn_19_2016.json")
    r = s2.strukturiraj(d, None, "UPU 2 – Kornić")
    sub = {"clanci": {k: v for k, v in r["clanci"].items() if k in ("38", "39", "40")}}
    s = oc.ocijeni(sub, J("oznake/upu2_cl38_40.json"))[0]
    g2_drugdje = [k for k, c in r["clanci"].items() if c.get("gramatika") and c.get("pravila")]
    return {"cl38_40_vlastite_oznake": s, "clanci_gdje_je_v2_dala_pravila": g2_drugdje}


def sha_obj(o):
    return hashlib.sha256(json.dumps(o, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def sve():
    integritet = provjeri_integritet()
    r = pokreni_ppug()
    r2 = pokreni_ppug()
    det = {"prolaz_1": sha_obj(r), "prolaz_2": sha_obj(r2)}
    det["isto"] = det["prolaz_1"] == det["prolaz_2"]
    izl_sha = s2.zapisi_json(r, M / "izlaz/ppug_v2_1.json")
    out = {"verzija": "v2.1", "integritet": integritet, "determinizam": det, "izlaz": {"izlaz/ppug_v2_1.json": izl_sha},
           "cl22_23": usporedi_22_23(r), "cl25_33": usporedi_25_33(r), "ostali_clanci_ppug": ostali_prijedlozi(r), "upu2": upu2(),
           "pravno_potvrdeno": 0,
           "napomena": "Čl. 25. i 33. su razvojni skup (poznati razvoju v2.1): rezultat nije dokaz generalizacije."}
    provjeri_integritet()
    return out


if __name__ == "__main__":
    o = sve()
    s = s2.zapisi_json(o, M / "izlaz/usporedba_v2_1.json")
    print("izlaz/usporedba_v2_1.json", s)
    print(json.dumps({"determinizam": o["determinizam"], "22_23_v1": o["cl22_23"]["v1"], "22_23_v2_1": o["cl22_23"]["v2_1"],
                      "promjene": o["cl22_23"]["promjene_po_oznaci"], "izvan_opsega": len(o["cl22_23"]["izvan_opsega_oznaka"]),
                      "25_33": o["cl25_33"]["sazetak"], "jasne_ne_tocne": o["cl25_33"]["jasne_oznake_koje_nisu_tocne"],
                      "pogresno_25_33": o["cl25_33"]["detalji"]["pogresno"], "propusteno_25_33": o["cl25_33"]["detalji"]["propusteno"],
                      "ostali": {k: o["ostali_clanci_ppug"][k] for k in ("clanci_s_pravilima", "prijedlog", "pregled")}, "upu2": o["upu2"]},
                     ensure_ascii=False, indent=1))

#!/usr/bin/env python3
"""EKSPERIMENT v2.6: sloj nad zamrznutom v2.5 (strukturiraj_v25 i sve zamrznute gramatike se ne mijenjaju).

Redoslijed:
 1. izvor_v26.ucitaj (normalizacija izvora, odvajanje naslova članaka) – izvan ovog modula;
 2. priprema teksta v2.6 (tisućice, indeksi kig/kis; iste duljine) → zamrznuta v2.5 (struktura, kontekst, oblici v2.4/v2.5);
 3. oblici v2.6 nad odbijenim rečenicama (subjekt izražen načinom gradnje, dvije visine / dva broja etaža u rečenici);
 4. vrsta građevine iz SVIH izraza uvoda članka/stavka (gramatika_v26.vrsta_uvoda) za pravila bez vrste;
 5. zone iz naslova članka → prostorni obuhvat svakog pravila članka;
 6. zaštite (t. 7): bez vrste, bez obuhvata koji naslov/uvod određuje ili s uvjetnim veznikom bez zapisanog uvjeta → PREGLED;
 7. citati se vraćaju u izvorni oblik po položaju.
"""
import copy, re
import gramatika as g1
import gramatika_v22 as g2
import gramatika_v25 as g5
import gramatika_v26 as g6
import strukturiraj_v23 as s23
import strukturiraj_v25 as s25

VERZIJA = g6.VERZIJA
RX_UVJETNI = re.compile(r"\b(?:ukoliko|ako|kada|osim ako|uz uvjet)\b", re.I)
VRSTA_KODOVI = ("SKUPINA_NEPOZNATA", "SUBJEKT_NEPREPOZNAT")


def _ukloni(p, kodovi, filtar=None):
    par = [(k, r) for k, r in zip(p["razlog_kod"], p["razlozi"]) if not (k in kodovi and (filtar is None or filtar(r)))]
    p["razlog_kod"] = [k for k, _ in par]; p["razlozi"] = [r for _, r in par]


def _status(p):
    if p["razlog_kod"]:
        p["status"] = "PREGLED"; p["za_izracun"] = False
    else:
        p["status"] = "PRIJEDLOG"
        p["za_izracun"] = bool(isinstance(p["vrijednost"], (int, float)) and p["operator"] in (">=", "<=", "="))
    p["obrazlozenje_statusa"] = g2._obrazlozenje(p)


def _prva_recenica(t):
    return re.split(r"(?<=[.;])\s+(?=[A-ZČĆŽŠĐ(])", t.strip(), maxsplit=1)[0] if t else ""


def vrsta_v26(cl, c, prihvati=False):
    """Pravila bez vrste: vrsta iz uvoda stavka, inače iz prve rečenice članka – samo jedna vrsta u odnosu OBJEKT_GRADNJE.
    Zaštita (t. 7): vrsta nađena ovim novim putem zapisuje se, ali pravilo ostaje PREGLED (VRSTA_IZ_UVODA_V26) dok sudac
    put ne potvrdi. prihvati=True služi samo za mjerenje mogućeg učinka i nije dio zamrznutog ponašanja."""
    S = dict(g1.stavci(c["tekst"]))
    prva_cl = _prva_recenica(c["tekst"])
    for p in cl.get("pravila", []):
        if p["vrsta_gradevine"].get("skupine"):
            continue
        uvod_st = (S.get(p["stavak"]) or "").split(":")[0] if p["stavak"] is not None else ""
        kod, dokaz, razlog = (None, None, None)
        for uvod, izvor in ((_prva_recenica(uvod_st), "uvod stavka"), (prva_cl, "prva rečenica članka")):
            if not uvod:
                continue
            kod, dokaz, razlog = g6.vrsta_uvoda(uvod)
            if kod or razlog:
                break
        if razlog == "VRSTA_VISEZNACNA":
            s25._pregled(p, "VRSTA_VISEZNACNA", f"uvod imenuje više vrsta građevine u odnosu gradnje ({dokaz}); vrsta pravila nije jednoznačna")
            continue
        if not kod:
            continue
        p["vrsta_gradevine"]["skupine"] = list(kod)
        p["izvor_vrste"] = {"izraz": dokaz, "izvor": izvor, "uvod": uvod, "verzija": VERZIJA}
        _ukloni(p, VRSTA_KODOVI)
        _ukloni(p, ("KONTEKST_IZGUBLJEN",), lambda r: "vrsta građevine" in r)
        if not prihvati:
            p["razlog_kod"].append("VRSTA_IZ_UVODA_V26")
            p["razlozi"].append(f"vrsta »{dokaz}« preuzeta iz uvoda ({izvor}) novim putem v2.6; prihvaća se tek nakon provjere")
        _status(p)


def zone_naslova(cl, naslov):
    Z = g6.zone_naslova(naslov)
    for p in cl.get("pravila", []):
        if not Z:
            continue
        postoji = {o.get("oznaka") for o in p["prostorni_obuhvat"]}
        nove = [z for z in Z if z not in postoji]
        if nove:
            p["prostorni_obuhvat"] = [o for o in p["prostorni_obuhvat"] if o["vrsta"] != "NIJE_NAVEDEN_U_ODREDBI"] + \
                [{"vrsta": "ZONA_PLANA", "oznaka": z, "dokaz": naslov, "utvrdjeno_na_lokaciji": False, "izvor": "naslov članka (v2.6)"} for z in nove]
        p["zone_konteksta"] = list(dict.fromkeys(list(p.get("zone_konteksta") or []) + Z))
        p["naslov_clanka"] = naslov


def zastite_v26(cl, naslov):
    Z = g6.zone_naslova(naslov)
    uvjeti_citata = {}
    for p in cl.get("pravila", []):
        uvjeti_citata.setdefault(p.get("izvorni_citat"), []).extend(list(p["uvjeti"]) + list(p.get("dodatni_uvjeti") or []))
    for p in cl.get("pravila", []):
        if not p["vrsta_gradevine"].get("skupine"):
            s25._pregled(p, "KONTEKST_IZGUBLJEN", "vrsta građevine nije određena ni u odredbi ni u uvodu")
        if Z and not any(o.get("oznaka") in Z for o in p["prostorni_obuhvat"]):
            s25._pregled(p, "KONTEKST_IZGUBLJEN", "naslov članka određuje zonu, a pravilo je nema u prostornom obuhvatu")
        cit = p.get("izvorni_citat") or ""
        nepripisani = [m for m in RX_UVJETNI.finditer(cit)
                       if not any(m.group(0).lower() in (u or "").lower() and (u or "") in cit for u in uvjeti_citata.get(cit, []))]
        if nepripisani and not p["uvjeti"] and not p.get("dodatni_uvjeti"):
            s25._pregled(p, "UVJET_MOGUCE_IZGUBLJEN", "citat sadrži uvjetni veznik (»ukoliko / ako / kada / uz uvjet«), a pravilo nema zapisan uvjet")
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)


def strukturiraj(dokazi, clanci, plan, prihvati_vrstu_iz_uvoda=False):
    O = {k: c["tekst"] for k, c in dokazi["clanci"].items()}
    T6 = {k: g6.pripremi(t) for k, t in O.items()}
    d6 = dict(dokazi, clanci={k: dict(c, tekst=T6[k]) for k, c in dokazi["clanci"].items()})
    r = s25.strukturiraj(d6, clanci, plan)
    r = copy.deepcopy(r)
    r["shema"] = "plan-citac-pravila/2.6"; r["gramatika_v26"] = VERZIJA
    for k, cl in r["clanci"].items():
        c6 = d6["clanci"][k]
        naslov = dokazi["clanci"][k].get("naslov_clanka")
        if cl.get("gramatika") == g2.VERZIJA:
            prije = {p["id"] for p in cl.get("pravila", [])}
            s25.dodatni_oblici(cl, c6, plan, g6.oblici, "v26.", VERZIJA)
            U = s23._uvodi_clanka(c6)
            for p in cl.get("pravila", []):
                if p["id"] in prije:
                    continue
                kont, uvod = U.get((p["stavak"], p.get("blok") if p["stavak"] is None else None), ([], ""))
                s23._dodaj_kontekst(p, kont, uvod, cl["clanak"])
                s23._samo_kao(p)
                p["obrazac_v23"] = s23.VERZIJA
            s25.kontekst_v25(cl, c6)
            s25.nadredjena_alineja(cl, c6)
            vrsta_v26(cl, c6, prihvati_vrstu_iz_uvoda)
            zone_naslova(cl, naslov)
            zastite_v26(cl, naslov)
        if naslov:
            cl["naslov_clanka"] = naslov
        r["clanci"][k] = g5.vrati_sve(cl, T6[k], O[k])
    sv = [p for c in r["clanci"].values() for p in c.get("pravila", [])]
    r["sazetak"] = dict(r.get("sazetak", {}), pravila=len(sv), prijedlog=sum(p["status"] == "PRIJEDLOG" for p in sv),
                        pregled=sum(p["status"] == "PREGLED" for p in sv),
                        odbijeno=sum(len(c.get("nepokriveno", [])) for c in r["clanci"].values()),
                        prepoznatih_clanaka=sum(1 for c in r["clanci"].values() if c.get("pravila")))
    return r


zapisi_json = s25.zapisi_json

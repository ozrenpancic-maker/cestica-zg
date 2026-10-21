#!/usr/bin/env python3
"""Mjeri identitet plana prema tests/zlatni/krk-plan-identity-v1.json.
Ulaz: {"veze":[{"odluka_id","opcina","vrsta","broj","veza"}]}  (broj = null za PPU/GUP)
Izlaz: točnost identiteta, recall višeplanskih veza, točnost vrste veze, BROJ ZABRANJENIH SPOJEVA (kritično: mora biti 0)."""
import json, sys, os, collections
Z = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "krk-plan-identity-v1.json")
def kljuc(o, opc, v, b): return (str(o), opc, v, None if b in (None, "") else str(b))
def mjeri(pred, zlatni):
    P = {kljuc(p["odluka_id"], p["opcina"], p["vrsta"], p.get("broj")): p.get("veza") for p in pred["veze"]}
    ml = [l for l in zlatni["veze"] if l["ocekivanje"] == "MUST_LINK"]
    nl = [l for l in zlatni["veze"] if l["ocekivanje"] == "MUST_NOT_LINK"]
    k = lambda l: kljuc(l["odluka_id"], l["plan"]["opcina"], l["plan"]["vrsta"], l["plan"]["broj"])
    pogodak = [l for l in ml if k(l) in P]
    po_odluci = collections.Counter(l["odluka_id"] for l in ml)
    multi = [l for l in ml if po_odluci[l["odluka_id"]] > 1 and l["veza"] == "INITIATES"]
    vrsta_ok = [l for l in pogodak if l["veza"] == "UNKNOWN" or P[k(l)] == l["veza"]]
    mlk = {k(l) for l in ml}
    zabr = [l for l in nl if k(l) in P and (P[k(l)] == l["veza"] or k(l) not in mlk)]
    r = lambda a, b: round(a / b, 3) if b else None
    return {"identitet_recall": r(len(pogodak), len(ml)), "multi_plan_recall": r(sum(1 for l in multi if k(l) in P), len(multi)),
            "tocnost_vrste_veze": r(len(vrsta_ok), len(pogodak)), "zabranjeni_spojevi": len(zabr),
            "zabranjeni_popis": [(l["id"], l["odluka_id"], l["plan"]["naziv"]) for l in zabr],
            "propusteno": [(l["id"], l["odluka_id"], l["plan"]["naziv"]) for l in ml if k(l) not in P]}
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "krk-generacije-i-radnje-v1.json")
def mjeri2(pred, zlatni, ref=None):
    """v0.16.1 metrike. Stare ključeve zadržava (iz mjeri). pred['registar'] = sve veze u registru (uklj. UNKNOWN); pred['veze'] = evaluacijski izvoz."""
    r = mjeri(pred, zlatni)
    k = lambda l: kljuc(l["odluka_id"], l["plan"]["opcina"], l["plan"]["vrsta"], l["plan"]["broj"])
    kp = lambda p: kljuc(p["odluka_id"], p["opcina"], p["vrsta"], p.get("broj"))
    ml = [l for l in zlatni["veze"] if l["ocekivanje"] == "MUST_LINK"]
    E = {kp(p): p for p in pred["veze"]}
    R = {kp(p): p for p in pred.get("registar", pred["veze"])}
    div = lambda a, b: round(a / b, 3) if b else None
    r["identity_detected_recall"] = div(sum(k(l) in R for l in ml), len(ml))
    r["identity_exported_recall"] = div(sum(k(l) in E for l in ml), len(ml))
    # vrsta veze: samo MUST_LINK s poznatom (ne-UNKNOWN) referentnom vrstom; predviđeni UNKNOWN nikad nije točan
    rv = [l for l in ml if l["veza"] != "UNKNOWN" and k(l) in E]
    r["relation_type_accuracy"] = div(sum(E[k(l)].get("veza") == l["veza"] for l in rv), len(rv))
    r["unknown_count"] = sum(1 for p in pred.get("registar", pred["veze"]) if p.get("veza") == "UNKNOWN")
    r["forbidden_merges"] = r["zabranjeni_spojevi"]
    # auto-spajanje bez dokaza: UNKNOWN ili nepotvrđena generacija s auto_merge_allowed=true
    r["auto_merge_bez_dokaza"] = sum(1 for p in pred.get("registar", pred["veze"]) if p.get("auto_merge_allowed") and (p.get("veza") == "UNKNOWN" or p.get("generation_id", "UNDETERMINED") == "UNDETERMINED"))
    if ref:
        G = [g for g in ref["generacije"] if g["dokazano"]]
        gp = lambda oid: next((p.get("generation_id") for p in pred.get("registar", pred["veze"]) if p["odluka_id"] == oid and p["vrsta"] == "UPU" and str(p.get("broj")) == "1" and p["opcina"] == "Krk"), None)
        ok = pok = 0
        for g in G:
            v = gp(g["odluka_id"]); 
            if v and v != "UNDETERMINED":
                pok += 1; ok += (v == g["generation_id"])
        r["generation_accuracy"] = div(ok, pok)             # samo pokrivene referentne generacije (L1/L2)
        r["generation_coverage"] = div(pok, len(G))
        r["generation_reference_cases"] = len(G)
        zab = [p for p in ref["generacije"] if not p["dokazano"]]
        r["generacija_bez_dokaza"] = sum(1 for g in zab if gp(g["odluka_id"]) not in (None, "UNDETERMINED"))   # nedokazane ne smiju dobiti generaciju
        a, b = gp("14783"), gp("28241")
        r["gen_A_B_spojene"] = int(bool(a) and a == b and a != "UNDETERMINED")
    return r
KANDIDATSKI = {"SHARED_FOOTPRINT_HEURISTIC", "AREA_LIST", "SUBJECT_PHRASE", "GAZETTE_CHAIN"}   # signali za pronalaženje kandidata, ne dokaz
MIN_REF = 5   # ispod ovoga generacijska točnost se prikazuje kao N/A
def nd(num, den, **kw):
    d = {"vrijednost": round(num / den, 3) if den else "N/A", "brojnik": num, "nazivnik": den}; d.update(kw); return d
def mjeri3(pred, zlatni, ref=None):
    """Spec v0.16.1: sve nove metrike kao {vrijednost, brojnik, nazivnik}; stari ključevi ostaju (mjeri/mjeri2)."""
    r = mjeri2(pred, zlatni, ref)
    k = lambda l: kljuc(l["odluka_id"], l["plan"]["opcina"], l["plan"]["vrsta"], l["plan"]["broj"])
    kp = lambda p: kljuc(p["odluka_id"], p["opcina"], p["vrsta"], p.get("broj"))
    ml = [l for l in zlatni["veze"] if l["ocekivanje"] == "MUST_LINK"]
    E = {kp(p): p for p in pred["veze"]}; R = {kp(p): p for p in pred.get("registar", pred["veze"])}
    N = len(ml)
    r["M_identity_detected_recall"] = nd(sum(k(l) in R for l in ml), N, nazivnik_opis="MUST_LINK veze; pronađeno = ispravan par (odluka, općina, vrsta, broj) u registru, uklj. UNKNOWN")
    r["M_identity_exported_recall"] = nd(sum(k(l) in E for l in ml), N, nazivnik_opis="isto, ali u evaluacijskom izvozu")
    ev = lambda l: E[k(l)].get("evidence_type") or R.get(k(l), {}).get("evidence_type")   # izvoz ili, ako ga nema u izvozu, registar
    res = [l for l in ml if k(l) in E and ev(l) and ev(l) not in KANDIDATSKI]
    r["M_identity_resolved_recall"] = nd(len(res), N, nazivnik_opis="u izvozu s dokazom koji nije samo kandidatski signal (heuristika obuhvata/popis područja/naslov/glasilo)")
    konkr = [l for l in ml if l["veza"] != "UNKNOWN"]
    odl = [l for l in konkr if k(l) in E and E[k(l)].get("veza") not in (None, "UNKNOWN")]
    tocno = [l for l in odl if E[k(l)]["veza"] == l["veza"]]
    r["M_relation_type_accuracy_decided"] = nd(len(tocno), len(odl), nazivnik_opis="konkretna referentna vrsta, sustav dao konkretnu vrstu (UNKNOWN isključen)")
    r["M_relation_type_coverage"] = nd(len(odl), len(konkr), nazivnik_opis="udio referentnih konkretnih veza za koje je sustav dao konkretnu vrstu")
    r["M_relation_type_accuracy_all"] = nd(len(tocno), len(konkr), nazivnik_opis="UNKNOWN i nedostajuće = neriješeno/netočno")
    gu = [l for l in ml if l["veza"] == "UNKNOWN"]
    r["M_unknown_count"] = {"izvoz_registar": r["unknown_count"], "referentno_UNKNOWN_u_zlatnom": len(gu),
                            "napomena": "Referentne UNKNOWN veze nisu u nazivnicima vrste veze: sam zlatni skup kaže da vrsta nije dokaziva iz čl. 1."}
    if ref:
        G1 = [g for g in ref["generacije"] if g["dokazano"] and g["razina"] == "L1"]
        G12 = [g for g in ref["generacije"] if g["dokazano"]]
        P = pred.get("registar", pred["veze"])
        def gp(oid): return next((p.get("generation_id") for p in P if p["odluka_id"] == oid and p["vrsta"] == "UPU" and str(p.get("broj")) == "1" and p["opcina"] == "Krk"), None)
        for ime, G in (("L1", G1), ("L1_L2", G12)):
            pok = [g for g in G if gp(g["odluka_id"]) not in (None, "UNDETERMINED")]
            ok = [g for g in pok if gp(g["odluka_id"]) == g["generation_id"]]
            acc = nd(len(ok), len(pok)) if len(G) >= MIN_REF else {"vrijednost": "N/A", "brojnik": len(ok), "nazivnik": len(pok), "razlog": "referentnih slučajeva %d < %d" % (len(G), MIN_REF)}
            r["M_generation_accuracy_" + ime] = acc
            r["M_generation_coverage_" + ime] = nd(len(pok), len(G))
        r["M_generation_unproven_assigned"] = nd(r["generacija_bez_dokaza"], sum(1 for g in ref["generacije"] if not g["dokazano"]))
    return r
if __name__ == "__main__":
    pr = json.load(open(sys.argv[1]))
    if len(sys.argv) > 3: pr["registar"] = json.load(open(sys.argv[3]))["links"]      # opcionalno: puni registar (plan_identity_review.json)
    ref = json.load(open(REF)) if os.path.exists(REF) else None
    r = mjeri3(pr, json.load(open(sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "-" else Z)), ref)
    print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(1 if r["zabranjeni_spojevi"] or r.get("gen_A_B_spojene") or r["auto_merge_bez_dokaza"] else 0)

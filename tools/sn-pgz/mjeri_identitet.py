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
if __name__ == "__main__":
    r = mjeri(json.load(open(sys.argv[1])), json.load(open(sys.argv[2] if len(sys.argv) > 2 else Z)))
    print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(1 if r["zabranjeni_spojevi"] else 0)

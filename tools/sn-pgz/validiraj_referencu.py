#!/usr/bin/env python3
"""Provjera konzistentnosti referentnog skupa generacija (ne algoritam; ne podešava ništa). Izlaz: JSON izvještaj; kod greške != 0."""
import json, os, sys, hashlib, collections
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni")
def validiraj(r=None, v1=None):
    r = r or json.load(open(os.path.join(B, "generacije-baska-malinska-vrbnik-v1.json"), encoding="utf-8"))
    v1 = v1 or json.load(open(os.path.join(B, "krk-plan-identity-v1.json"), encoding="utf-8"))
    G = []; P = []   # greške
    docs = {}
    for c in r["slucajevi"]:
        ids = {d["odluka_id"] for d in c["dokumenti"]}
        for d in c["dokumenti"]:
            if d["odluka_id"] in docs: G.append("dokument u dva slučaja: " + d["odluka_id"])
            docs[d["odluka_id"]] = (c["id"], d)
            if not d["dokazi"]: G.append("bez dokaza: " + d["odluka_id"])
            for e in d["dokazi"]:
                if not (e.get("clanak_izvoza") and e.get("sha256_citata") and e.get("sha256_clanka")): G.append("citat nije provjeren: %s" % d["odluka_id"])
            if d["dokazano"] != (d["razina"] == "L1"): G.append("dokazano != (razina==L1): " + d["odluka_id"])
            if not d["dokazano"] and d["generation_ref"] != "UNDETERMINED": G.append("nedokazan dokument ima generaciju: " + d["odluka_id"])
            if d["dokazano"] and not d["generation_ref"].endswith("#G1"): G.append("neočekivana oznaka: " + d["odluka_id"])
            if d["sn_vlastiti_broj"] is not None: G.append("sn_vlastiti_broj se ne izvodi: " + d["odluka_id"])
        for p in c["parovi"]:
            if p["a"] not in ids or p["b"] not in ids: G.append("par izvan slučaja %s: %s/%s" % (c["id"], p["a"], p["b"])); continue
            da, db = docs[p["a"]][1], docs[p["b"]][1]
            tok = lambda d: {t for e in d["dokazi"] for t in e["sn_navodi_u_citatu"]}
            if p["ocekivanje"] == "SAME_GENERATION":
                if not (da["dokazano"] and db["dokazano"] and p["razina"] == "L1"): G.append("SAME_GENERATION traži L1 oba: %s/%s" % (p["a"], p["b"]))
                if da["generation_ref"] != db["generation_ref"]: G.append("SAME_GENERATION različite oznake: %s/%s" % (p["a"], p["b"]))
                if not (tok(da) & tok(db)): G.append("SAME_GENERATION bez zajedničkog broja SN u citatima: %s/%s" % (p["a"], p["b"]))
            elif p["ocekivanje"] == "DIFFERENT_PLAN":
                if not (da["dokazano"] and db["dokazano"]) or da["generation_ref"] == db["generation_ref"]: G.append("DIFFERENT_PLAN neispravan: %s/%s" % (p["a"], p["b"]))
            elif p["ocekivanje"] == "REVIEW_REQUIRED":
                if da["dokazano"] and db["dokazano"] and p["razina"] == "L1": G.append("REVIEW par s dva L1 dokaza (treba SAME/DIFFERENT): %s/%s" % (p["a"], p["b"]))
            elif p["ocekivanje"] == "NOT_SUPERSEDED":
                if p["razina"] != "L1": G.append("NOT_SUPERSEDED traži L1")
            else: G.append("nepoznato očekivanje " + p["ocekivanje"])
        for ps in c.get("pravni_status", []):
            if ps["razina"] == "L1" and not all(e.get("clanak_izvoza") for e in ps["dokazi"]): G.append("pravni status bez provjerenog citata: " + ps["subjekt"])
    h = hashlib.sha256(json.dumps(r["slucajevi"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if h != r["sha256"]: G.append("sha256 skupa ne odgovara sadržaju")
    v1h = hashlib.sha256(json.dumps([v1["veze"], v1["parovi"]], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if v1h != v1["sha256"]: G.append("zamrznuti v1 je izmijenjen")
    v1ids = {l["odluka_id"] for l in v1["veze"]}
    preklop = sorted(set(docs) & v1ids)
    cnt = collections.Counter(d["razina"] for _, d in docs.values())
    fam = collections.Counter(d["generation_ref"] for _, d in docs.values() if d["dokazano"])
    pc = collections.Counter(p["ocekivanje"] for c in r["slucajevi"] for p in c["parovi"])
    return {"greske": G, "dokumenata": len(docs), "po_razini": dict(cnt), "obitelji_s_L1": dict(fam),
            "obitelji_s_najmanje_2_L1": sorted(k for k, v in fam.items() if v >= 2),
            "lanci_iste_generacije_L1": sorted({docs[p["a"]][1]["generation_ref"] for c in r["slucajevi"] for p in c["parovi"] if p["ocekivanje"] == "SAME_GENERATION"}), "parovi_po_ocekivanju": dict(pc),
            "pravni_status_slucajeva": sum(len(c.get("pravni_status", [])) for c in r["slucajevi"]),
            "preklop_s_v1_identitet": preklop, "sha256_skupa": r["sha256"], "sha256_v1_ocekivan_i_nepromijenjen": v1h == v1["sha256"]}
if __name__ == "__main__":
    o = validiraj(); print(json.dumps(o, ensure_ascii=False, indent=1)); sys.exit(1 if o["greske"] else 0)

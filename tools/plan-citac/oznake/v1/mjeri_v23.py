#!/usr/bin/env python3
"""Mjerenje v2.3 na pregledanom referentnom skupu v1 (s odlukama suca v1.1), istim postupkom kao mjeri_v22.py.

    python3 mjeri_v23.py      # izlaz: mjerenje_v23_ref_v1_1.json + sažetak

Jedina razlika u usporedbi: v2.3 zapisuje `kontekst_primjene` uz svako pravilo stavka (bloka). Kad referenca taj
kontekst ne navodi (označivači ga nisu prepisali u svaku alineju), pravilo se ne proglašava pogrešnim zbog viška
konteksta; takvi se slučajevi broje zasebno kao KONTEKST_IZNAD_REFERENCE. Kad ga referenca navodi, mora biti u pravilu.
"""
import json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(D))
import mjeri_v22 as M22
import usporedi_v22 as U22
import usporedi_v2 as U2
import strukturiraj_v23 as s23
from citac_tekst import izdvoji_tekst

KONT = {}  # id zapisa čitača -> kontekst_primjene
_raz22, _gran22 = M22.razlike, M22.granularnost


def _bez_viska(z, o):
    k = KONT.get(z["id"]) or []
    ou = U22._nv((o.get("uvjet_primjene") or ""))
    visak = [x for x in k if U22._nv(x) not in ou]
    if not visak:
        return None
    dij = [d for d in z["uvjet_tekst"].split(" | ") if d and d not in visak]
    return dict(z, uvjet_tekst=" | ".join(dij))


def granularnost(z, o, MP):
    g = _gran22(z, o, MP)
    if g is not None:
        return g
    for x in M22.inacice(o):
        z2 = _bez_viska(z, x)
        if z2 is None:
            continue
        if not U22.razlike(z2, x, MP):
            return ["KONTEKST_IZNAD_REFERENCE"]
        g2 = _gran22(z2, dict(x, prihvatljivo=None), MP)
        if g2 is not None:
            return g2 + ["KONTEKST_IZNAD_REFERENCE"]
    return None


def main():
    M22.integritet()
    M22.KONTEKST[:] = json.loads((D / "odluke_suca_v1_1.json").read_text(encoding="utf-8"))["kontekst_clanka"]
    M22.granularnost = granularnost
    MP = M22.mapa()
    ref = json.loads((D / "referenca_v1.json").read_text(encoding="utf-8"))
    run = lambda: {"ppug": s23.strukturiraj(izdvoji_tekst(M / U2.IZVOR, dio=1), None, "PPUG Krk"),
                   "upu1": s23.strukturiraj(izdvoji_tekst(M / U2.IZVOR, [14, 24], dio=2), None, "UPU 1 – Krk")}
    izlaz, izlaz2 = run(), run()
    det = all(U2.sha_obj(izlaz[k]) == U2.sha_obj(izlaz2[k]) for k in izlaz)
    for x in izlaz.values():
        for c in x["clanci"].values():
            for p in c.get("pravila", []):
                KONT[p["id"]] = p.get("kontekst_primjene") or []
    out = {"verzija_citaca": "v2.3 (razvojna)", "referenca": "oznake/v1/referenca_v1.json + odluke_suca_v1_1.json", "sha256_reference": M22.REF_SHA,
           "determinizam": det, "skupine": {}, "pravno_potvrdeno": 0}
    uk_P, uk_Z = [], []
    for g, (izv, opseg) in M22.PODRUCJE.items():
        Z = ref["skupine"][g]["zapisi"]
        P = [p for c in izlaz[izv]["clanci"].values() for p in c.get("pravila", []) if (p["clanak"], p["stavak"]) in opseg]
        s, d = M22.usporedi(P, Z, MP)
        out["skupine"][g] = {"sazetak": s, "detalji": d}
        uk_P += P; uk_Z += [dict(o, id=f"{g}:{o['id']}") for o in Z]
    out["ukupno"] = M22.usporedi(uk_P, uk_Z, MP)[0]
    M22.integritet()
    p = D / "mjerenje_v23_ref_v1_1.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, M22.sha(p), izlaz


if __name__ == "__main__":
    o, s, _ = main()
    K = ["oznaka", "zapisa_modula", "tocno_prihvaceno", "tocno_uz_pravilo_granularnosti", "pogresno_prihvaceno", "pravilno_na_pregled",
         "nepotrebno_na_pregled", "pregled_bez_oznake", "propusteno", "preciznost_prihvacenih", "pokrivenost_prihvacanja_od_JASAN"]
    for g, v in list(o["skupine"].items()) + [("UKUPNO", {"sazetak": o["ukupno"]})]:
        print(g.ljust(20), " ".join(f"{k[:10]}={v['sazetak'][k]}" for k in K))
    print("determinizam", o["determinizam"], "sha", s)

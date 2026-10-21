#!/usr/bin/env python3
"""Provjera: svaki doslovni citat iz baze mora se naći u izvornom tekstu odluke (nakon normalizacije razmaka i navodnika).
Upotreba: provjeri_citate.py baza.json ID=tekst.txt [ID=tekst.txt …]   (tekst = HTML stranica ili kopirani tekst odluke)"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
def provjeri(baza, tekstovi):
    lose = []; n = 0
    for r in baza["pravila"]:
        i = r["izvor"]; t = tekstovi.get(i["odluka_id"])
        if t is None: lose.append((r["id"], "nema teksta odluke " + str(i["odluka_id"]))); continue
        n += 1
        if S.norm(i["citat"]) not in S.norm(t): lose.append((r["id"], "citat se ne nalazi u tekstu"))
    return n, lose
if __name__ == "__main__":
    baza = json.load(open(sys.argv[1], encoding="utf-8")); T = {}
    for a in sys.argv[2:]:
        k, p = a.split("=", 1); T[int(k)] = S.u_tekst(open(p, encoding="utf-8").read())
    n, lose = provjeri(baza, T); print(f"provjereno {n} citata, neuspjeh: {len(lose)}")
    for x in lose: print(" -", *x)
    sys.exit(1 if lose else 0)

#!/usr/bin/env python3
"""Slaganje verzija članaka plana iz niza odluka (osnovna odluka -> izmjene).

Ulaz: tekstovi odluka (iz sn_pgz.py fetch ili iz izvoza). Izlaz: za svaki članak plana
lanac verzija: koja odluka ga je donijela/zamijenila cijelim tekstom, koje su ga kasnije
mijenjale djelomično (te se NE primjenjuju strojno - samo se navode).
Ništa se ne tumači: tekst bloka je doslovan isječak odluke."""
import re, json, sys, hashlib

HEAD = re.compile(r"^[ \t]*Članak[ \t]*(?:\n[ \t]*)?(\d+[a-z]?)\.[ \t]*(.*)$", re.M)
# prvi redak iza naslova koji pokazuje da je to članak ODLUKE (naredba), a ne članak plana
NAREDBA = re.compile(r"^(?:U\s+(?:članku|Odluci)|Podnaslov|Poglavlje|Naslov|Iza\s+članka|Iz\s+članka|Iznad|Dodaj\w+\s+se|Stavak|Ova\s+Odluka|Odluka|Brišu?\s+se|Briše\s+se)", re.I)

def ravni(t): return re.sub(r"[ \t]+", " ", t.replace("\r", ""))

def blokovi(tekst, osnovna=False):
    """-> [{clanak, vrsta: 'zamjena'|'novi'|'osnovni'|'naredba', naredba?, tekst}] po redu u odluci"""
    t = ravni(tekst); ms = list(HEAD.finditer(t)); out = []
    for i, m in enumerate(ms):
        kraj = ms[i + 1].start() if i + 1 < len(ms) else len(t)
        num, rest = m.group(1), m.group(2).strip()
        tijelo = t[m.end():kraj]
        prvi = rest or next((l.strip() for l in tijelo.split("\n") if l.strip()), "")
        if osnovna:
            vr = "osnovni"
        elif NAREDBA.match(prvi) or (not rest and not prvi):
            vr = "naredba"
        elif re.match(r"^mijenja\s+se\s+i\s+glasi", prvi, re.I):
            vr = "zamjena"
        else:
            vr = "novi" if re.search(r"[a-z]$", num) else "zamjena_ili_novi"
        gol = (rest + "\n" + tijelo).strip() if rest else tijelo.strip()
        out.append({"clanak": num, "vrsta": vr, "prvi_redak": prvi[:120], "tekst": gol})
    return out

def hash_(t): return hashlib.sha256(re.sub(r"\s+", " ", t).encode()).hexdigest()

if __name__ == "__main__":
    for f in sys.argv[1:]:
        for b in blokovi(open(f, encoding="utf-8").read(), osnovna=f.endswith("od1.txt")):
            print(f"{b['clanak']:>5} {b['vrsta']:<17} {len(b['tekst']):>6}  {b['prvi_redak'][:60]}")

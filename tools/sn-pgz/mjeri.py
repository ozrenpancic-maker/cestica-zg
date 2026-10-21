#!/usr/bin/env python3
"""Mjerenje točnosti prepoznavanja izmjena prema zlatnom skupu.
Ulaz: JSON s popisom {"izmjene":[{"odluka_id","ciljni_clanak_plana","stavak","tocka"?,"vrsta"?}, ...]}
(i zlatni skup tests/zlatni/punat-upu3-2020.json). Ključ pogotka: (članak, stavak, točka) - svaka razina se broji zasebno.
Izlaz: precision, recall, točnost cilja po razinama (članak, stavak, točka), popis propuštenih i lažnih.
Upotreba: mjeri.py izlaz.json [zlatni.json]"""
import json, sys, os
ZLATNI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "punat-upu3-2020.json")
def kljuc(x, razina):
    k = [str(x.get("ciljni_clanak_plana") or "")]
    if razina >= 2: k.append(str(x.get("stavak") or ""))
    if razina >= 3: k.append(str(x.get("tocka") or ""))
    return tuple(k)
def mjeri(prijavljeno, zlatno):
    r = {}
    for razina, ime in ((1, "clanak"), (2, "clanak+stavak"), (3, "clanak+stavak+tocka")):
        G = {}; P = {}
        for g in zlatno: G[kljuc(g, razina)] = G.get(kljuc(g, razina), 0) + 1
        for p in prijavljeno: P[kljuc(p, razina)] = P.get(kljuc(p, razina), 0) + 1
        tp = sum(min(G.get(k, 0), n) for k, n in P.items())
        r[ime] = {"tocno": tp, "prijavljeno": sum(P.values()), "zlatno": sum(G.values()),
                  "precision": round(tp / max(1, sum(P.values())), 3), "recall": round(tp / max(1, sum(G.values())), 3),
                  "propusteno": sorted(k for k in G if k not in P), "lazno": sorted(k for k in P if k not in G)}
    return r
if __name__ == "__main__":
    p = json.load(open(sys.argv[1], encoding="utf-8"))["izmjene"]
    z = json.load(open(sys.argv[2] if len(sys.argv) > 2 else ZLATNI, encoding="utf-8"))["izmjene"]
    z = [g for g in z if g["vrsta"] != "nejasno"]
    print(json.dumps(mjeri(p, z), ensure_ascii=False, indent=1))

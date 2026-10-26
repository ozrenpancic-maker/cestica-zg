#!/usr/bin/env python3
"""Ocjena prijedloga pravila (strukturiraj.py) prema ručno označenom skupu (oznake/*.json).

Pravilo je TOČNO kad se s ručnom oznakom slaže u: članku, točki, alineji, vrsti građevine (osnovna/pomoćna/…),
parametru, vrijednosti, jedinici, popisu vrsta građevina, vrsti pravila (OSNOVNO/IZNIMKA/UVJETNO) i uvjetu
(svi označeni odlomci uvjeta moraju biti u predloženom uvjetu, a predloženi uvjet doslovno u dokaznom tekstu).
Prijedlog sa statusom PREGLED broji se kao DVOSMISLEN. Svaki drugi prijedlog je POGREŠAN.

    python3 ocijeni.py izlaz/upu2_pravila_38_40.json oznake/upu2_cl38_40.json
"""
import json, re, sys
from pathlib import Path


def _n(s):
    return re.sub(r"\s+", " ", s or "").strip()


def kljuc(p):
    return (p["clanak"], p["tocka"], p["alineja"], p["gradjevina"], p["parametar"], p["vrsta_pravila"], tuple(sorted(p["vrste"])))


def isti_uvjet(zlatni, prijedlog, dokaz):
    if zlatni is None:
        return prijedlog is None
    if prijedlog is None or _n(prijedlog) not in _n(dokaz):
        return False
    dijelovi = zlatni if isinstance(zlatni, list) else [zlatni]
    return all(_n(d) in _n(prijedlog) for d in dijelovi)


def ista_vrijednost(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return abs(a - b) < 1e-9
    return a == b


def ocijeni(prijedlozi, oznake):
    P = [p for c in prijedlozi["clanci"].values() for p in c.get("pravila", [])]
    Z = list(oznake["pravila"])
    iskoristeno = [False] * len(Z)
    rez = {"tocno": [], "pogresno": [], "dvosmisleno": [], "propusteno": []}
    for p in P:
        if p["status"] == "PREGLED":
            rez["dvosmisleno"].append({"pravilo": p, "razlozi": p.get("razlozi")})
            continue
        nadjen = None
        for i, z in enumerate(Z):
            if iskoristeno[i] or kljuc(z) != kljuc(p):
                continue
            if ista_vrijednost(z["vrijednost"], p["vrijednost"]) and z["jedinica"] == p["jedinica"] and isti_uvjet(z["uvjet"], p["uvjet"], p["dokaz"]):
                nadjen = i; break
        if nadjen is None:
            slicni = [z for z in Z if (z["clanak"], z["tocka"], z["alineja"], z["parametar"]) == (p["clanak"], p["tocka"], p["alineja"], p["parametar"])]
            rez["pogresno"].append({"pravilo": p, "najblize_oznake": slicni})
        else:
            iskoristeno[nadjen] = True
            rez["tocno"].append(p)
    rez["propusteno"] = [z for i, z in enumerate(Z) if not iskoristeno[i]]
    zu = {(u["clanak"], u["tocka"], u["upucuje_na"]["clanak"], tuple(u["upucuje_na"]["tocke"])) for u in oznake.get("upucivanja", [])}
    pu = {(c["clanak"], u["tocka"], u["upucuje_na"]["clanak"], tuple(u["upucuje_na"]["tocke"])) for c in prijedlozi["clanci"].values() for u in c.get("upucivanja", [])}
    sazetak = {"oznaceno": len(Z), "predlozeno": len(P), "tocno": len(rez["tocno"]), "pogresno": len(rez["pogresno"]),
               "dvosmisleno": len(rez["dvosmisleno"]), "propusteno": len(rez["propusteno"]),
               "upucivanja_tocno": len(zu & pu), "upucivanja_pogresno": len(pu - zu), "upucivanja_propusteno": len(zu - pu),
               "oznake_neovisne": "NIJE" not in oznake.get("neovisnost", "NIJE")}
    return sazetak, rez


if __name__ == "__main__":
    pr = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    oz = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    s, r = ocijeni(pr, oz)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    for x in r["pogresno"]:
        p = x["pravilo"]; print("POGREŠNO", p["clanak"], p["tocka"], p["alineja"], p["parametar"], p["vrijednost"], p["vrste"], p["vrsta_pravila"])
    for z in r["propusteno"]:
        print("PROPUŠTENO", z["clanak"], z["tocka"], z["alineja"], z["parametar"], z["vrijednost"], z["vrste"], z["vrsta_pravila"])

#!/usr/bin/env python3
"""Mjerenje točnosti prepoznavanja izmjena prema zlatnom skupu (multiskup događaja, duplikati se broje).
Ulaz: JSON {"izmjene":[{"ciljni_clanak_plana","stavak","tocka","alineja"?,"ucinak"?,"razina"?}, ...]}
  ucinak: ADD | REPLACE | DELETE | RENUMBER (neobavezno; bez njega se mjere samo ciljevi)
Mjere: clanak; clanak+stavak; clanak+stavak+tocka; alineja (+alineja); ucinak (cilj+vrsta učinka); potpuna (cilj+alineja+ucinak+razina).
Zapisi bez ucinka/razine isključeni su iz tih mjera i to je ispisano. Stavke gdje je ucinak NEJASNO ne ulaze u mjerenje.
Upotreba: mjeri.py izlaz.json [zlatni.json]"""
import json, sys, os
ZLATNI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tests", "zlatni", "punat-upu3-2020.json")
if not os.path.exists(ZLATNI): ZLATNI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "punat-upu3-2020.json")
def s(x, k): v = x.get(k); return "" if v in (None, "") else str(v)
KLJUCEVI = [
    ("clanak", lambda x: (s(x, "ciljni_clanak_plana"),), False),
    ("clanak_stavak", lambda x: (s(x, "ciljni_clanak_plana"), s(x, "stavak")), False),
    ("clanak_stavak_tocka", lambda x: (s(x, "ciljni_clanak_plana"), s(x, "stavak"), s(x, "tocka")), False),
    ("alineja", lambda x: (s(x, "ciljni_clanak_plana"), s(x, "stavak"), s(x, "tocka"), s(x, "alineja")), False),
    ("ucinak", lambda x: (s(x, "ciljni_clanak_plana"), s(x, "stavak"), s(x, "tocka"), s(x, "ucinak")), True),
    ("potpuna", lambda x: (s(x, "ciljni_clanak_plana"), s(x, "stavak"), s(x, "tocka"), s(x, "alineja"), s(x, "ucinak"), s(x, "razina")), True),
]
def mjeri(prijavljeno, zlatno):
    zlatno = [g for g in zlatno if g.get("ucinak", g.get("vrsta")) not in ("NEJASNO", "nejasno")]
    r = {}
    for ime, f, treba_ucinak in KLJUCEVI:
        P = [p for p in prijavljeno if not treba_ucinak or s(p, "ucinak")]
        if treba_ucinak and not P: r[ime] = {"preskoceno": "izlaz nema polje ucinak"}; continue
        G = {}; Pc = {}
        for g in zlatno: G[f(g)] = G.get(f(g), 0) + 1
        for p in P: Pc[f(p)] = Pc.get(f(p), 0) + 1
        tp = sum(min(G.get(k, 0), n) for k, n in Pc.items())
        r[ime] = {"tocno": tp, "prijavljeno": sum(Pc.values()), "zlatno": sum(G.values()),
                  "precision": round(tp / max(1, sum(Pc.values())), 3), "recall": round(tp / max(1, sum(G.values())), 3),
                  "propusteno": sorted(k for k in G if G[k] > Pc.get(k, 0)), "lazno": sorted(k for k in Pc if Pc[k] > G.get(k, 0))}
    return r
if __name__ == "__main__":
    p = json.load(open(sys.argv[1], encoding="utf-8"))["izmjene"]
    z = json.load(open(sys.argv[2] if len(sys.argv) > 2 else ZLATNI, encoding="utf-8"))["izmjene"]
    print(json.dumps(mjeri(p, z), ensure_ascii=False, indent=1))

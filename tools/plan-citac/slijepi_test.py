#!/usr/bin/env python3
"""Početni (slijepi) test strukturiranja na izvoru za koji obrasci NISU pisani.

Pokreće postojeći čitač i strukturiranje bez ikakvih prilagodbi i za svaku alineju bilježi ishod:
PRAVILO (prijedlog), PREGLED, NEPOKRIVENO (ima broj, nema obrasca), BEZ_BROJA (nema vrijednosti), UPUCIVANJE.
Ne uspoređuje s oznakama: to radi ocijeni.py tek kad postoje neovisne oznake.

    python3 slijepi_test.py IZVOR.(pdf|html|txt) --clanci 22 23 [--naslov "…" za PDF] -o izlaz/slijepo_ppug_22_23.json
"""
import argparse, json, re
from collections import Counter
from pathlib import Path
from citac import brojevi
from citac_tekst import izdvoji_tekst
from strukturiraj import strukturiraj, tocke, alineje, vrste_clanka, OBRASCI, UPUCIVANJE


def ishodi(dokazi, clanci, plan):
    R = strukturiraj(dokazi, clanci, plan)
    out = {"izvor": dokazi.get("izvor"), "sha256": dokazi.get("sha256"), "clanci": {}, "ukupno": Counter()}
    for br in clanci:
        c = dokazi["clanci"].get(str(br))
        if not c:
            out["clanci"][str(br)] = {"status": "NIJE_IZDVOJEN"}; continue
        rc = R["clanci"][str(br)]
        zapis = {"vrste": vrste_clanka(c["tekst"]), "uvod": c["tekst"][:160], "tocke": [], "pregled": rc.get("pregled", [])}
        for t in tocke(c["tekst"]):
            naslov, al = alineje(t["tekst"])
            for ai, a in enumerate(al, 1):
                pr = [p for p in rc["pravila"] if p["tocka"] == t["slovo"] and p["alineja"] == ai]
                if UPUCIVANJE.match(a):
                    ish = "UPUCIVANJE"
                elif pr:
                    ish = "PREGLED" if all(p["status"] == "PREGLED" for p in pr) else "PRAVILO"
                elif brojevi(a):
                    ish = "NEPOKRIVENO"
                else:
                    ish = "BEZ_BROJA"
                out["ukupno"][ish] += 1
                zapis["tocke"].append({"tocka": t["slovo"], "alineja": ai, "ishod": ish, "pravila": len(pr), "tekst": a})
        if not zapis["tocke"]:
            zapis["napomena"] = "članak nema točke »a) …« s alinejama »- …« u obliku koji modul poznaje"
            out["ukupno"]["STRUKTURA_NEPOZNATA"] += 1
        out["clanci"][str(br)] = zapis
    out["ukupno"] = dict(out["ukupno"])
    out["prijedlozi"] = R
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("izvor"); a.add_argument("--clanci", type=int, nargs="+", required=True)
    a.add_argument("--naslov"); a.add_argument("--dio", type=int); a.add_argument("--plan", default="PPUG Krk"); a.add_argument("-o", "--izlaz", default="slijepo.json")
    x = a.parse_args()
    if x.izvor.lower().endswith(".pdf"):
        from citac import izdvoji
        D = izdvoji(x.izvor, x.naslov)
    else:
        D = izdvoji_tekst(x.izvor, x.clanci, x.dio)
    if D.get("status", "").startswith("ABSTAIN"):
        print(json.dumps({k: D.get(k) for k in ("status", "razlog", "sha256", "dijelovi")}, ensure_ascii=False)); raise SystemExit(2)
    r = ishodi(D, x.clanci, x.plan)
    Path(x.izlaz).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"sha256": r["sha256"], "ukupno": r["ukupno"], "problemi_izvora": D.get("problemi")}, ensure_ascii=False))

#!/usr/bin/env python3
"""Usporedba izlaza modula s NEOVISNIM oznakama (drugi označivač), uz zamrznute oznake i dogovoreno mapiranje.

Razredi: TOČNO (prijedlog = oznaka), POGREŠNO (prijedlog bez odgovarajuće oznake), PREGLED (modul ne predlaže, traži
pregled; posebno se bilježi odgovara li oznaci), PROPUŠTENO (oznaka bez prijedloga ni pregleda).
"""
import hashlib, json, re, sys
from pathlib import Path

MAPA = Path(__file__).resolve().parent
ZAMRZNUTO = {"oznake/neovisno/neovisne_oznake_ppug_22_23.json": "b56057965c75f1434a4e9c7684eac1e86393994454787ab94b2f09681be660b5"}


def provjeri_zamrznuto():
    for p, sha in ZAMRZNUTO.items():
        if hashlib.sha256((MAPA / p).read_bytes()).hexdigest() != sha:
            raise SystemExit(f"oznake {p} promijenjene nakon zamrzavanja")


def _n(s):
    return re.sub(r"\s+", " ", s or "").strip()


def u_zapise(pravilo, M, sve_vrste):
    """Pravilo modula → zapisi u granularnosti oznaka."""
    par = M["parametri"].get(pravilo["parametar"], "?" + pravilo["parametar"])
    gr = M["gradjevina"].get(pravilo["gradjevina"], pravilo["gradjevina"])
    v = pravilo["vrijednost"]
    if pravilo.get("vrijednost_vrsta") == "opis":
        jed = "opis"
    elif pravilo["jedinica"] is None and isinstance(v, (int, float)):
        jed = "koeficijent"
    else:
        jed = pravilo["jedinica"]
    if gr == "poljoprivredna_gospodarska":
        vrste = ["poljoprivredna_gospodarska"]
    elif pravilo.get("vrsta_izraz"):
        vrste = [M["nepotvrdeni_oblici"].get(pravilo["vrsta_izraz"], pravilo["vrsta_izraz"])]
    elif not pravilo.get("oblik_izricit") and sorted(pravilo["vrste"]) == sorted(sve_vrste):
        vrste = ["sve_navedene"]
    else:
        vrste = [M["oblici"][x.split("-")[1]] for x in pravilo["vrste"]]
    return [{"clanak": pravilo["clanak"], "stavak": pravilo.get("stavak"), "tocka": pravilo["tocka"], "vrsta": vr, "gradjevina": gr,
             "parametar": par, "vrijednost": v, "jedinica": jed, "vrsta_pravila": pravilo["vrsta_pravila"],
             "uvjet": pravilo["uvjet"], "status": pravilo["status"], "razlozi": pravilo.get("razlozi"), "dokaz": pravilo["dokaz"]} for vr in vrste]


def isto(z, p):
    k = ["clanak", "stavak", "tocka", "vrsta", "gradjevina", "parametar", "vrsta_pravila", "jedinica"]
    if any(z[x] != p[x] for x in k):
        return False
    a, b = z["vrijednost"], p["vrijednost"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs(a - b) > 1e-9:
            return False
    elif _n(str(a)) != _n(str(b)):
        return False
    return (not z["uvjet"] and not p["uvjet"]) or (bool(z["uvjet"]) and bool(p["uvjet"]) and _n(z["uvjet"]) in _n(p["uvjet"]))


def ocijeni(prijedlozi, oznake, M):
    zapisi = []
    for c in prijedlozi["clanci"].values():
        for p in c.get("pravila", []):
            zapisi += u_zapise(p, M, c.get("vrste") or [])
    Z = oznake["pravila"]; uzeto = [False] * len(Z)
    rez = {"tocno": [], "pogresno": [], "pregled": [], "propusteno": []}
    for p in zapisi:
        i = next((i for i, z in enumerate(Z) if not uzeto[i] and isto(z, p)), None)
        if i is not None:
            uzeto[i] = True
        if p["status"] == "PREGLED":
            rez["pregled"].append({"zapis": p, "oznaka": Z[i]["id"] if i is not None else None})
        elif i is None:
            rez["pogresno"].append({"zapis": p})
        else:
            rez["tocno"].append({"zapis": p, "oznaka": Z[i]["id"], "ocjena_oznake": Z[i]["ocjena_teksta"]})
    rez["propusteno"] = [z for i, z in enumerate(Z) if not uzeto[i]]
    s = {"oznaka": len(Z), "zapisa_modula": len(zapisi), "tocno": len(rez["tocno"]), "pogresno": len(rez["pogresno"]),
         "pregled": len(rez["pregled"]), "pregled_odgovara_oznaci": sum(1 for x in rez["pregled"] if x["oznaka"]),
         "propusteno": len(rez["propusteno"]),
         "tocno_a_oznaka_trazi_pregled": sum(1 for x in rez["tocno"] if x["ocjena_oznake"] == "PREGLED"),
         "pregled_a_oznaka_jasna": sum(1 for x in rez["pregled"] if x["oznaka"] and next(z for z in Z if z["id"] == x["oznaka"])["ocjena_teksta"] == "JASAN")}
    return s, rez


if __name__ == "__main__":
    provjeri_zamrznuto()
    pr = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    oz = json.loads((MAPA / "oznake/neovisno/neovisne_oznake_ppug_22_23.json").read_text(encoding="utf-8"))
    M = json.loads((MAPA / "oznake/neovisno/mapiranje.json").read_text(encoding="utf-8"))
    s, r = ocijeni(pr, oz, M)
    print(json.dumps(s, ensure_ascii=False, indent=1))
    for x in r["pogresno"]:
        z = x["zapis"]; print("POGREŠNO", z["clanak"], z["stavak"], z["tocka"], z["vrsta"], z["parametar"], z["vrijednost"], z["jedinica"], z["vrsta_pravila"])
    for x in r["pregled"]:
        z = x["zapis"]; print("PREGLED", x["oznaka"], z["clanak"], z["tocka"], z["vrsta"], z["parametar"], z["vrijednost"], "|", "; ".join(z["razlozi"] or []))
    for z in r["propusteno"]:
        print("PROPUŠTENO", z["id"], z["clanak"], z["stavak"], z["tocka"], z["vrsta"], z["parametar"], z["vrijednost"], z["ocjena_teksta"])

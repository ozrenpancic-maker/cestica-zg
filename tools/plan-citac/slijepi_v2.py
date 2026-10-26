#!/usr/bin/env python3
"""EKSPERIMENT v2.1: slijepi test zamrznute v2.1 na neviđenim člancima drugog plana (UPU 1 – Krk, dio 2 istog HTML-a).

Postupak (redoslijed je obvezan):
  1. `odaberi`  – članci se biraju strojno po kriteriju, bez ispisa teksta (ispisuju se samo brojevi i duljine);
  2. `tekst`    – doslovni tekst odabranih članaka zapisuje se za označivača (bez ispisa);
  3. neovisno označavanje u zasebnom kontekstu, s nadzorom rječnika iz mapiranje_v2.json; oznake se zamrzavaju;
  4. `usporedi` – tek tada se pokreće zamrznuti modul i uspoređuje s oznakama.
Prije koraka 4 provjeravaju se ZAMRZNUTO_v2.json i kontrolna suma oznaka.
"""
import hashlib, json, re, sys
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v2 as s2
import usporedi_v2 as U

M = Path(__file__).resolve().parent
D = M / "slijepo/ppug_krk/slijepi_v2"
KRITERIJ = ("članak drugog dijela dokumenta (UPU 1 – Krk) koji sadrži i »građevne čestice« i »koeficijent izgrađenosti«, duljine do 8000 znakova, "
            "bez ponovljenog broja članka; uzimaju se prva dva po rednom broju. Prvi kriterij (uz to i vrijednost u m², do 4000 znakova) nije "
            "dao nijedan članak; promijenjen je uz uvid samo u broj pogodaka i duljine članaka, ne u tekst.")


def odaberi():
    d = izdvoji_tekst(M / U.IZVOR, dio=2)
    izbor = []
    for k, c in sorted(d["clanci"].items(), key=lambda kv: kv[1]["broj"]):
        t = c["tekst"]
        if "#" not in k and "građevne čestice" in t and "koeficijent izgrađenosti" in t and len(t) <= 8000:
            izbor.append((k, c["broj"], len(t)))
    return d, izbor[:2]


def tekst():
    d, izbor = odaberi()
    D.mkdir(parents=True, exist_ok=True)
    dijelovi = [f"UPU 1 – Krk (dio 2 dokumenta), izvor {U.IZVOR}, SHA-256 {d['sha256']}. Doslovno izdvojen tekst članaka, bez oznaka i tumačenja.\n"]
    for k, br, _ in izbor:
        dijelovi.append(f"Članak {br}.\n{d['clanci'][k]['tekst']}\n")
    p = D / "za_oznacavanje_upu1.txt"
    p.write_text("\n".join(dijelovi), encoding="utf-8")
    meta = {"kriterij": KRITERIJ, "clanci": [br for _, br, _ in izbor], "duljine": [n for _, _, n in izbor],
            "sha256_teksta": hashlib.sha256(p.read_bytes()).hexdigest(), "sha256_izvora": d["sha256"]}
    (D / "odabir.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def usporedi(oznake_sha):
    z = json.loads((M / "ZAMRZNUTO_v2.json").read_text(encoding="utf-8"))
    for g in ("kod", "izlazi", "mapiranje"):
        for p, s in z[g].items():
            assert hashlib.sha256((M / p).read_bytes()).hexdigest() == s, f"promijenjeno nakon zamrzavanja v2.1: {p}"
    U.provjeri_integritet()
    po = D / "neovisne_oznake_upu1.json"
    assert hashlib.sha256(po.read_bytes()).hexdigest() == oznake_sha, "oznake promijenjene"
    meta = json.loads((D / "odabir.json").read_text(encoding="utf-8"))
    d = izdvoji_tekst(M / U.IZVOR, meta["clanci"], dio=2)
    r = s2.strukturiraj(d, None, "UPU 1 – Krk")
    MP = json.loads((M / U.MAPA25).read_text(encoding="utf-8"))
    Z = json.loads(po.read_text(encoding="utf-8"))["zapisi"]
    pravila = [p for c in r["clanci"].values() for p in c.get("pravila", [])]
    zap = U.u_zapise_25(pravila, MP)
    uzeto = [False] * len(Z)
    tocno, pogresno, pregled = [], [], []
    for x in zap:
        i = next((i for i, o in enumerate(Z) if not uzeto[i] and not U.razlike(x, o, MP)), None)
        if i is not None:
            uzeto[i] = True
        if x["status"] == "PREGLED":
            pregled.append({"id": x["id"], "oznaka": Z[i]["id"] if i is not None else None, "razlog_kod": x["razlog_kod"]})
        elif i is None:
            pogresno.append({"zapis": x, "najbliza_oznaka": U._najbliza(x, Z, MP)})
        else:
            tocno.append({"id": x["id"], "oznaka": Z[i]["id"], "jednoznacnost_oznake": Z[i]["jednoznacnost"]})
    propusteno = [{"oznaka": o["id"], "parametar": o["parametar"], "jednoznacnost": o["jednoznacnost"], "najblizi_zapis": U._najblizi(o, zap, MP)}
                  for i, o in enumerate(Z) if not uzeto[i]]
    out = {"clanci": meta["clanci"], "oznaka": len(Z), "zapisa_modula": len(zap), "tocno": len(tocno), "pogresno": len(pogresno),
           "pregled": len(pregled), "pregled_odgovara_oznaci": sum(1 for x in pregled if x["oznaka"]), "propusteno": len(propusteno),
           "oznake_izvan_rjecnika": sum(1 for o in Z if str(o["parametar"]).startswith("drugo:")),
           "odbijene_odredbe_modula": [{"clanak": c["clanak"], **{k: n.get(k) for k in ("stavak", "tocka", "alineja", "razlog_kod")}, "dokaz": n["dokaz"][:160]}
                                       for c in r["clanci"].values() for n in c.get("nepokriveno", [])],
           "clanci_odbijeni": {k: c["pregled"] for k, c in r["clanci"].items() if not c.get("pravila")},
           "detalji": {"tocno": tocno, "pogresno": pogresno, "pregled": pregled, "propusteno": propusteno},
           "izlaz_modula": r, "pravno_potvrdeno": 0}
    return out


if __name__ == "__main__":
    if sys.argv[1] == "odaberi":
        _, izbor = odaberi(); print(json.dumps([{"clanak": br, "znakova": n} for _, br, n in izbor]))
    elif sys.argv[1] == "tekst":
        print(json.dumps(tekst(), ensure_ascii=False))
    elif sys.argv[1] == "usporedi":
        o = usporedi(sys.argv[2])
        print(s2.zapisi_json(o, D / "usporedba_slijepi_v2_1.json"))
        print(json.dumps({k: v for k, v in o.items() if k not in ("detalji", "izlaz_modula")}, ensure_ascii=False, indent=1))

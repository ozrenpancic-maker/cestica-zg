#!/usr/bin/env python3
"""EKSPERIMENT v2.2: slijepi test zamrznute v2.2 na DRUGOM, prethodno neviđenom prostornom planu (faza E).

Obvezan redoslijed (kod se ne mijenja tijekom testa; svaka izmjena otvara v2.3):
  1. `odaberi IZVOR [--dio N] [--naziv "..."]` – strojni odabir članaka; ispisuju se samo brojevi i duljine, ne tekst.
     Kriterij (unaprijed zadan): članci koji sadrže »građevn« i barem jedan od izraza »koeficijent izgrađenosti«,
     »površina građevne čestice«, »udaljenost«; duljina do 8000 znakova; bez ponovljenih brojeva; prva 4 po broju.
  2. `tekst ...` – doslovni tekst odabranih članaka u slijepo/<oznaka>/za_oznacavanje.txt (bez ispisa).
  3. Neovisno označavanje u zasebnom kontekstu, sa zatvorenim popisom naziva (mapiranje_v2 + mapiranje_v22);
     oznake se spremaju i zamrzavaju (zaseban commit) PRIJE koraka 4.
  4. `usporedi ... OZNAKE_SHA` – provjera ZAMRZNUTO_v2_2.json i oznaka, zatim usporedba (usporedi_v22.usporedi_oznake).
Izvještava se: preciznost prihvaćenih, pokrivenost, udio pregleda, propuštena pravila, po članku.
"""
import argparse, hashlib, json, re
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v22 as s22
import usporedi_v22 as U

M = Path(__file__).resolve().parent
KRITERIJ = ("članci koji sadrže »građevn« i barem jedan od izraza »koeficijent izgrađenosti«, »površina građevne čestice«, »udaljenost«; "
            "duljina do 8000 znakova; bez ponovljenih brojeva članka; prva 4 po rednom broju")


def _dokazi(izvor, dio):
    p = Path(izvor)
    if p.suffix.lower() == ".pdf":
        import citac
        raise SystemExit("PDF: najprije citac.py (granice odluke, naslov plana), zatim ovaj alat nad dobivenim dokazi.json")
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    return izdvoji_tekst(p, dio=dio)


def odaberi(izvor, dio):
    d = _dokazi(izvor, dio)
    if d.get("status", "").startswith("ABSTAIN"):
        raise SystemExit(f"{d['status']}: {d.get('razlog')} {d.get('dijelovi', '')}")
    izbor = []
    for k, c in sorted(d["clanci"].items(), key=lambda kv: kv[1]["broj"]):
        t = c["tekst"]
        if "#" in k or len(t) > 8000 or "građevn" not in t:
            continue
        if re.search(r"koeficijent izgrađenosti|površina građevne čestice|udaljenost", t):
            izbor.append((k, c["broj"], len(t)))
    return d, izbor[:4]


def tekst(izvor, dio, oznaka, naziv):
    d, izbor = odaberi(izvor, dio)
    D = M / "slijepo" / oznaka; D.mkdir(parents=True, exist_ok=True)
    dij = [f"{naziv}. Izvor {Path(izvor).name}, SHA-256 {d.get('sha256')}. Doslovno izdvojen tekst članaka, bez oznaka i tumačenja.\n"]
    for k, br, _ in izbor:
        dij.append(f"Članak {br}.\n{d['clanci'][k]['tekst']}\n")
    p = D / "za_oznacavanje.txt"; p.write_text("\n".join(dij), encoding="utf-8")
    meta = {"plan": naziv, "izvor": str(izvor), "dio": dio, "kriterij": KRITERIJ, "clanci": [br for _, br, _ in izbor], "kljucevi": [k for k, _, _ in izbor],
            "duljine": [n for _, _, n in izbor], "sha256_teksta": hashlib.sha256(p.read_bytes()).hexdigest(), "sha256_izvora": d.get("sha256")}
    (D / "odabir.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


def usporedi(oznaka, oznake_sha):
    z = json.loads((M / "ZAMRZNUTO_v2_2.json").read_text(encoding="utf-8"))
    for g in ("kod", "mapiranje"):
        for p, s in z[g].items():
            assert hashlib.sha256((M / p).read_bytes()).hexdigest() == s, f"promijenjeno nakon zamrzavanja v2.2: {p}"
    U.provjeri_integritet()
    D = M / "slijepo" / oznaka
    po = D / "neovisne_oznake.json"
    assert hashlib.sha256(po.read_bytes()).hexdigest() == oznake_sha, "oznake promijenjene"
    meta = json.loads((D / "odabir.json").read_text(encoding="utf-8"))
    d = _dokazi(meta["izvor"], meta["dio"])
    d = dict(d, clanci={k: d["clanci"][k] for k in meta["kljucevi"]})
    r = s22.strukturiraj(d, None, meta["plan"])
    Z = json.loads(po.read_text(encoding="utf-8"))["zapisi"]
    P = [p for c in r["clanci"].values() for p in c.get("pravila", [])]
    MP = U.mapa()
    s, det = U.usporedi_oznake(P, Z, MP)
    return {"plan": meta["plan"], "clanci": meta["clanci"], "ukupno": s, "po_clanku": U.po_clanku(P, Z, MP, meta["clanci"]), "detalji": det,
            "odbijeno": sum(len(c.get("nepokriveno", [])) for c in r["clanci"].values()), "izlaz_modula": r, "pravno_potvrdeno": 0}


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("korak", choices=["odaberi", "tekst", "usporedi"]); a.add_argument("izvor_ili_oznaka")
    a.add_argument("--dio", type=int); a.add_argument("--oznaka", default="slijepi_v22"); a.add_argument("--naziv", default="Prostorni plan")
    a.add_argument("--sha")
    x = a.parse_args()
    if x.korak == "odaberi":
        print(json.dumps([{"clanak": br, "znakova": n} for _, br, n in odaberi(x.izvor_ili_oznaka, x.dio)[1]]))
    elif x.korak == "tekst":
        print(json.dumps(tekst(x.izvor_ili_oznaka, x.dio, x.oznaka, x.naziv), ensure_ascii=False))
    else:
        o = usporedi(x.izvor_ili_oznaka, x.sha)
        print(s22.zapisi_json(o, M / "slijepo" / x.izvor_ili_oznaka / "usporedba.json"))
        print(json.dumps({k: o[k] for k in ("plan", "clanci", "ukupno", "po_clanku", "odbijeno")}, ensure_ascii=False, indent=1))

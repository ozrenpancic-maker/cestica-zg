#!/usr/bin/env python3
"""HIBRIDNI ČITAČ v1: slijepi test na prethodno neviđenom planu (zamrznuti postupak).

Koraci (redoslijed je dio protokola):
  1. odabir članaka zamrznutim kriterijem: python3 slijepi_v26.py odaberi IZVOR
  2. neovisni označivač po uputama v1.2 dobiva za_oznacavanje.txt; oznake se zamrzavaju zasebnim commitom
  3. ulaz generatora: python3 hibrid/slijepi_hibrid.py ulaz IZVOR --clanci 12,13,14 --naziv X
       → slijepo_hibrid/X/ulaz.txt i dijelovi dio_A.txt, dio_B.txt … (cijeli članci, najviše 8 000 znakova teksta po dijelu)
  4. za svaki dio jedan izolirani poziv generatora bez alata (PROMPT_GENERATORA_v2.txt + tekst dijela);
     izlaz: izvuci.py → dio_X.json; spoji.py → gen.json (zamrznuti prije usporedbe)
  5. python3 hibrid/slijepi_hibrid.py mjeri X IZVOR --clanci 12,13,14 --gen gen.json --oznake OZNAKE.json --sha SHA_OZNAKA
Ništa se ne mijenja nakon uvida u rezultate.
"""
import argparse, hashlib, json, sys
from pathlib import Path

H = Path(__file__).resolve().parent
M = H.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(M / "oznake/v1")); sys.path.insert(0, str(H))
import izvor_v26 as I

sha = lambda b: hashlib.sha256(b).hexdigest()
MAKS_ZNAKOVA = 8000


def provjeri_zamrzavanje():
    z = json.loads((H / "ZAMRZNUTO_hibrid_v1.json").read_text(encoding="utf-8"))
    los = [p for p, s in z["datoteke"].items() if sha((M / p).read_bytes()) != s]
    if los:
        raise SystemExit("promijenjeno nakon zamrzavanja hibrida v1: " + ", ".join(los))
    return z


def tekst_clanka(c):
    t = f"Članak {c['broj']}.\n"
    if c.get("naslov_clanka"):
        t += f"[NASLOV ČLANKA: {c['naslov_clanka']}]\n"
    return t + c["tekst"] + "\n"


def ulaz(izvor, clanci, dio=None, naslov=None):
    d = I.ucitaj(izvor, dio=dio, naslov=naslov)
    if d.get("status", "").startswith("ABSTAIN"):
        raise SystemExit(f"{d['status']}: {d.get('razlog')}")
    C = {c["broj"]: c for k, c in d["clanci"].items() if "#" not in k}
    nedostaje = [b for b in clanci if b not in C]
    if nedostaje:
        raise SystemExit(f"članci nisu pronađeni: {nedostaje}")
    bl = [tekst_clanka(C[b]) for b in clanci]
    dijelovi, cur = [], ""
    for b in bl:
        if cur and len(cur) + len(b) + 1 > MAKS_ZNAKOVA:
            dijelovi.append(cur); cur = ""
        cur += ("\n" if cur else "") + b
    dijelovi.append(cur)
    return d, "\n".join(bl), dijelovi


def provjeri_poziv(izlaz_agenta, dio_txt):
    """Potvrđuje da je poziv generatoru bio točno PROMPT_GENERATORA_v2.txt s tekstom dijela (prva poruka transkripta)."""
    p = json.loads(Path(izlaz_agenta).read_text(encoding="utf-8").splitlines()[0])
    c = p.get("message", {}).get("content")
    poslano = c if isinstance(c, str) else "".join(x.get("text", "") for x in c if isinstance(x, dict))
    ocek = (H / "PROMPT_GENERATORA_v2.txt").read_text(encoding="utf-8").replace("{TEKST}", Path(dio_txt).read_text(encoding="utf-8"))
    return poslano.strip() == ocek.strip()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("radnja", choices=["ulaz", "mjeri"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--clanci", required=True)
    ap.add_argument("--naziv"); ap.add_argument("--dio", type=int); ap.add_argument("--naslov")
    ap.add_argument("--gen"); ap.add_argument("--oznake"); ap.add_argument("--sha")
    a = ap.parse_args(argv)
    br = [int(x) for x in a.clanci.split(",")]
    provjeri_zamrzavanje()
    if a.radnja == "ulaz":
        izvor = a.args[0]
        _, sve, dijelovi = ulaz(izvor, br, a.dio, a.naslov)
        out = M / "slijepo_hibrid" / a.naziv
        out.mkdir(parents=True, exist_ok=True)
        (out / "ulaz.txt").write_text(sve, encoding="utf-8")
        info = {"izvor": str(izvor), "sha256_izvora": sha(Path(izvor).read_bytes()), "clanci": br, "sha256_ulaza": sha(sve.encode()), "dijelovi": []}
        for i, t in enumerate(dijelovi):
            p = out / f"dio_{chr(65 + i)}.txt"
            p.write_text(t, encoding="utf-8")
            info["dijelovi"].append({"datoteka": p.name, "znakova": len(t), "sha256": sha(t.encode())})
        (out / "ulaz.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(info, ensure_ascii=False, indent=1))
    else:
        naziv, izvor = a.args[0], a.args[1]
        if sha(Path(a.oznake).read_bytes()) != a.sha:
            raise SystemExit("SHA oznaka ne odgovara zamrznutim oznakama")
        import mjeri as X
        d, _, _ = ulaz(izvor, br, a.dio, a.naslov)
        Z = json.loads(Path(a.oznake).read_text(encoding="utf-8"))["zapisi"]
        r = X.mjeri_skup(naziv, a.gen, d=d, Z=Z, br=br)
        out = M / "slijepo_hibrid" / naziv / "usporedba_hibrid_v1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        X.ispis({naziv: r})
        print("sha", sha(out.read_bytes()))


if __name__ == "__main__":
    main()

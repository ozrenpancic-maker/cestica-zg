#!/usr/bin/env python3
"""EKSPERIMENT v2.3: slijepi test zamrznute v2.3 na prethodno neviđenom planu (faza E).

Isti postupak i isti kriterij odabira članaka kao slijepi_v22.py (odaberi → tekst → neovisne oznake, zamrznute
prije usporedbe → usporedi); razlika je samo u čitaču (strukturiraj_v23) i u datoteci zamrzavanja (ZAMRZNUTO_v2_3.json).

    python3 slijepi_v23.py odaberi IZVOR [--dio N]
    python3 slijepi_v23.py tekst IZVOR [--dio N] --oznaka X --naziv "..."
    python3 slijepi_v23.py usporedi X --sha SHA_OZNAKA
"""
import hashlib, json, sys
from pathlib import Path
import slijepi_v22 as S
import strukturiraj_v23 as s23

M = Path(__file__).resolve().parent


def provjeri_v23():
    z = json.loads((M / "ZAMRZNUTO_v2_3.json").read_text(encoding="utf-8"))
    los = [p for g in ("kod", "mapiranje") for p, s in z[g].items() if hashlib.sha256((M / p).read_bytes()).hexdigest() != s]
    if los:
        raise SystemExit("promijenjeno nakon zamrzavanja v2.3: " + ", ".join(los))


def main(argv=None):
    import argparse
    S.s22 = s23  # isti postupak i funkcije kao v2.2, čitač v2.3
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("korak", choices=["odaberi", "tekst", "usporedi"]); a.add_argument("izvor_ili_oznaka")
    a.add_argument("--dio", type=int); a.add_argument("--oznaka", default="slijepi_v23"); a.add_argument("--naziv", default="Prostorni plan")
    a.add_argument("--sha")
    x = a.parse_args(argv)
    if x.korak == "odaberi":
        print(json.dumps([{"clanak": br, "znakova": n} for _, br, n in S.odaberi(x.izvor_ili_oznaka, x.dio)[1]]))
    elif x.korak == "tekst":
        print(json.dumps(S.tekst(x.izvor_ili_oznaka, x.dio, x.oznaka, x.naziv), ensure_ascii=False))
    else:
        provjeri_v23()
        o = S.usporedi(x.izvor_ili_oznaka, x.sha)
        o["citac"] = "v2.3"
        print(s23.zapisi_json(o, M / "slijepo" / x.izvor_ili_oznaka / "usporedba_v23.json"))
        print(json.dumps({k: o[k] for k in ("plan", "clanci", "ukupno", "po_clanku", "odbijeno")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

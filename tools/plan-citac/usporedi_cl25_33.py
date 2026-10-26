#!/usr/bin/env python3
"""Usporedba ZAMRZNUTOG izlaza modula (v1) za čl. 25. i 33. PPUG-a Krk s zamrznutim neovisnim oznakama.
Ne mijenja kod ni izlaze; prije usporedbe provjerava sve kontrolne sume."""
import hashlib, json, re
from pathlib import Path
M = Path(__file__).resolve().parent
OZNAKE = "oznake/neovisno_cl25_33/neovisne_oznake_ppug_25_33.json"
OZNAKE_SHA = "b47d15c3f8d8005e53f9d1f44414155658177c30e16cf64e29a4f626f03c452d"
sha = lambda p: hashlib.sha256((M / p).read_bytes()).hexdigest()


def provjeri():
    z = json.loads((M / "ZAMRZNUTO_v1.json").read_text(encoding="utf-8"))
    for g in ("kod", "izvor", "izlazi", "referentne_oznake", "za_oznacavanje"):
        for p, s in z[g].items():
            assert sha(p) == s, f"promijenjeno nakon zamrzavanja: {p}"
    assert sha(OZNAKE) == OZNAKE_SHA, "oznake promijenjene"


def usporedi():
    provjeri()
    izl = json.loads((M / "slijepo/ppug_krk/cl25_33/izlaz_modula_cl25_33_v1.json").read_text(encoding="utf-8"))
    Z = json.loads((M / OZNAKE).read_text(encoding="utf-8"))["zapisi"]
    out = {}
    for c in ("25", "33"):
        S = izl["strukturiranje"]["clanci"][c]
        P = S["pravila"]
        zc = [z for z in Z if str(z["clanak"]) == c]
        # modul nema prijedloga: svaka oznaka je propuštena; prijedloga koji bi mogli biti pogrešni ili za pregled nema
        out[c] = {"oznaka": len(zc), "prijedloga_modula": len(P),
                  "tocno": 0, "pogresno": 0, "pregled": sum(p["status"] == "PREGLED" for p in P), "propusteno": len(zc) if not P else None,
                  "clanak_odbijen": not P, "razlog_odbijanja": [x["razlog"] for x in S["pregled"]],
                  "oznake_po_jednoznacnosti": {k: sum(z["jednoznacnost"] == k for z in zc) for k in ("JASAN", "PREGLED")},
                  "oznake_po_vrsti": {k: sum(z["vrsta_pravila"] == k for z in zc) for k in sorted({z["vrsta_pravila"] for z in zc})},
                  "dijagnostika_odredbi": {k: sum(o["ishod"] == k for o in izl["dijagnostika_odredbi"]["clanci"][c]["odredbe"])
                                           for k in ("PREPOZNATO_BEZ_KONTEKSTA_CLANKA", "DJELOMICNO", "ODBIJENO", "BEZ_BROJA")}}
        if P:
            raise SystemExit("izlaz ima prijedloge: potrebno je mapiranje prije usporedbe")
    return out


if __name__ == "__main__":
    print(json.dumps(usporedi(), ensure_ascii=False, indent=1))

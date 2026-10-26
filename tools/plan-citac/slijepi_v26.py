#!/usr/bin/env python3
"""EKSPERIMENT v2.6: slijepi test zamrznute v2.6 na prethodno neviđenom planu.

Isti postupak i isti kriterij odabira članaka kao slijepi_v22/v23/v25 (odaberi → tekst → jedan neovisni označivač po
uputama v1.2, oznake zamrznute zasebnim commitom → usporedi). Razlike:
  - izvor se učitava preko izvor_v26.ucitaj (HTML: prijelomi redaka, naslovi članaka; PDF: Klasa/KLASA, ABSTAIN pri
    oštećenom fontu); za PDF je potreban --naslov;
  - čitač je strukturiraj_v26; zamrzavanje ZAMRZNUTO_v2_6.json.
Usporedba se izvještava dvaput, oba načina određena su prije uvida u plan:
  strogo      – usporedi_v22.usporedi_oznake s U.mapa();
  semanticki  – mjeri_v26.usporedi_oznake (nazivi v1/v2.4/v2.5/v2.6, istoznačnice, odluke suca v1.1/v1.2).

    python3 slijepi_v26.py odaberi IZVOR [--dio N] [--naslov "..."]
    python3 slijepi_v26.py tekst IZVOR [--dio N] [--naslov "..."] --oznaka X --naziv "..."
    python3 slijepi_v26.py usporedi X --sha SHA_OZNAKA
"""
import hashlib, json, sys
from pathlib import Path
import slijepi_v22 as S
import strukturiraj_v26 as s26
import izvor_v26 as I

M = Path(__file__).resolve().parent
sys.path.insert(0, str(M / "oznake/v1"))
_NASLOV = {"v": None}


def provjeri_v26():
    z = json.loads((M / "ZAMRZNUTO_v2_6.json").read_text(encoding="utf-8"))
    los = [p for g in ("kod", "mapiranje") for p, s in z[g].items() if hashlib.sha256((M / p).read_bytes()).hexdigest() != s]
    if los:
        raise SystemExit("promijenjeno nakon zamrzavanja v2.6: " + ", ".join(los))


def _dokazi(izvor, dio):
    d = I.ucitaj(izvor, dio=dio, naslov=_NASLOV["v"])
    if d.get("status", "").startswith("ABSTAIN"):
        raise SystemExit(f"{d['status']}: {d.get('razlog')}")
    return d


def usporedi(oznaka, oznake_sha):
    import mjeri_v26 as X6
    provjeri_v26()
    D = M / "slijepo" / oznaka
    po = D / "neovisne_oznake.json"
    assert hashlib.sha256(po.read_bytes()).hexdigest() == oznake_sha, "oznake promijenjene"
    meta = json.loads((D / "odabir.json").read_text(encoding="utf-8"))
    _NASLOV["v"] = meta.get("naslov_odluke")
    d = _dokazi(meta["izvor"], meta["dio"])
    d = dict(d, clanci={k: d["clanci"][k] for k in meta["kljucevi"]})
    r = s26.strukturiraj(d, None, meta["plan"])
    Z = json.loads(po.read_text(encoding="utf-8"))["zapisi"]
    u = X6.usporedi_oznake(r, Z, tuple(meta["clanci"]))
    return {"plan": meta["plan"], "clanci": meta["clanci"], "citac": "v2.6", "strogo": u["strogo"], "semanticki": u["semanticki"],
            "kontekst": X6.kontekst(r), "odbijeno": sum(len(c.get("nepokriveno", [])) for c in r["clanci"].values()),
            "izlaz_modula": r, "pravno_potvrdeno": 0}


def main(argv=None):
    import argparse
    S.s22 = s26
    S._dokazi = _dokazi
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("korak", choices=["odaberi", "tekst", "usporedi"]); a.add_argument("izvor_ili_oznaka")
    a.add_argument("--dio", type=int); a.add_argument("--oznaka", default="slijepi_v26"); a.add_argument("--naziv", default="Prostorni plan")
    a.add_argument("--naslov"); a.add_argument("--sha")
    x = a.parse_args(argv)
    _NASLOV["v"] = x.naslov
    if x.korak == "odaberi":
        print(json.dumps([{"clanak": br, "znakova": n} for _, br, n in S.odaberi(x.izvor_ili_oznaka, x.dio)[1]]))
    elif x.korak == "tekst":
        meta = S.tekst(x.izvor_ili_oznaka, x.dio, x.oznaka, x.naziv)
        if x.naslov:
            meta["naslov_odluke"] = x.naslov
            (M / "slijepo" / x.oznaka / "odabir.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(meta, ensure_ascii=False))
    else:
        o = usporedi(x.izvor_ili_oznaka, x.sha)
        print(s26.zapisi_json(o, M / "slijepo" / x.izvor_ili_oznaka / "usporedba_v26.json"))
        print(json.dumps({k: o[k]["ukupno"] for k in ("strogo", "semanticki")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

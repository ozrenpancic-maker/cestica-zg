#!/usr/bin/env python3
"""EKSPERIMENT v2.5: slijepi test zamrznute v2.5 na prethodno neviđenom planu.

Isti postupak i isti kriterij odabira članaka kao slijepi_v22.py / slijepi_v23.py (odaberi → tekst → neovisne oznake po
uputama v1.2, zamrznute zasebnim commitom prije usporedbe → usporedi); razlika je u čitaču (strukturiraj_v25) i u datoteci
zamrzavanja (ZAMRZNUTO_v2_5.json). Usporedba se izvještava dvaput, oba načina određena su prije uvida u plan:
  strogo        – usporedi_v22.usporedi_oznake s U.mapa(), točno kao slijepi test v2.3;
  pravila_v25   – pravila usporedbe razvojnog mjerenja v2.5 (mjeri_v25.usporedi_nv: nazivi v1/v2.4/v2.5, odluke suca
                  v1.1 i v1.2, granularnost v2.4, JEDINICA_BROJA_ETAZA).

    python3 slijepi_v25.py odaberi IZVOR [--dio N]
    python3 slijepi_v25.py tekst IZVOR [--dio N] --oznaka X --naziv "..."
    python3 slijepi_v25.py usporedi X --sha SHA_OZNAKA
"""
import hashlib, json, sys
from pathlib import Path
import slijepi_v22 as S
import strukturiraj_v25 as s25
import usporedi_v22 as U

M = Path(__file__).resolve().parent
sys.path.insert(0, str(M / "oznake/v1"))


def provjeri_v25():
    z = json.loads((M / "ZAMRZNUTO_v2_5.json").read_text(encoding="utf-8"))
    los = [p for g in ("kod", "mapiranje") for p, s in z[g].items() if hashlib.sha256((M / p).read_bytes()).hexdigest() != s]
    if los:
        raise SystemExit("promijenjeno nakon zamrzavanja v2.5: " + ", ".join(los))


def usporedi(oznaka, oznake_sha):
    import mjeri_v25 as X
    provjeri_v25()
    D = M / "slijepo" / oznaka
    po = D / "neovisne_oznake.json"
    assert hashlib.sha256(po.read_bytes()).hexdigest() == oznake_sha, "oznake promijenjene"
    meta = json.loads((D / "odabir.json").read_text(encoding="utf-8"))
    d = S._dokazi(meta["izvor"], meta["dio"])
    d = dict(d, clanci={k: d["clanci"][k] for k in meta["kljucevi"]})
    r = s25.strukturiraj(d, None, meta["plan"])
    Z = json.loads(po.read_text(encoding="utf-8"))["zapisi"]
    P = [p for c in r["clanci"].values() for p in c.get("pravila", [])]
    MP = U.mapa()
    s, det = U.usporedi_oznake(P, Z, MP)
    X.pripremi_usporedbu(True)
    s5, d5, po5 = X.usporedi_nv(r, Z, tuple(meta["clanci"]))
    return {"plan": meta["plan"], "clanci": meta["clanci"], "citac": "v2.5",
            "strogo": {"ukupno": s, "po_clanku": U.po_clanku(P, Z, MP, meta["clanci"]), "detalji": det},
            "pravila_v25": {"ukupno": s5, "po_clanku": po5, "detalji": d5},
            "odbijeno": sum(len(c.get("nepokriveno", [])) for c in r["clanci"].values()), "izlaz_modula": r, "pravno_potvrdeno": 0}


def main(argv=None):
    import argparse
    S.s22 = s25
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("korak", choices=["odaberi", "tekst", "usporedi"]); a.add_argument("izvor_ili_oznaka")
    a.add_argument("--dio", type=int); a.add_argument("--oznaka", default="slijepi_v25"); a.add_argument("--naziv", default="Prostorni plan")
    a.add_argument("--sha")
    x = a.parse_args(argv)
    if x.korak == "odaberi":
        print(json.dumps([{"clanak": br, "znakova": n} for _, br, n in S.odaberi(x.izvor_ili_oznaka, x.dio)[1]]))
    elif x.korak == "tekst":
        print(json.dumps(S.tekst(x.izvor_ili_oznaka, x.dio, x.oznaka, x.naziv), ensure_ascii=False))
    else:
        o = usporedi(x.izvor_ili_oznaka, x.sha)
        print(s25.zapisi_json(o, M / "slijepo" / x.izvor_ili_oznaka / "usporedba_v25.json"))
        print(json.dumps({k: o[k]["ukupno"] for k in ("strogo", "pravila_v25")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()

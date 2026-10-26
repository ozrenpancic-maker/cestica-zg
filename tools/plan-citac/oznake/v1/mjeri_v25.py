#!/usr/bin/env python3
"""Mjerenje v2.2–v2.5 na tri razvojne obitelji planova: Krk (PPUG + UPU 1, referenca v1.2), Kornić (UPU 2, vlastite
oznake čl. 38.–40.) i Novi Vinodolski (UPU, neovisne oznake slijepog testa čl. 19., 20., 23., 24. – od v2.5 razvojni).

    python3 mjeri_v25.py      # → mjerenje_v25.json + tablice

Za svaki plan i verziju mjeri se zasebno:
  struktura: članci, članci s pravilima, članci odbijeni zbog nepoznate vrste, izdvojeni kandidati (pravila), odbijene rečenice;
  točnost (na označenim člancima): točno, točno uz pravilo granularnosti, pogrešno, pravilno / nepotrebno na pregled,
  pregled bez oznake, propušteno, preciznost, pokrivenost jasnih.
Pravila usporedbe su ista za sve verzije (ocijeni_v1_2 + mjeri_v24: nazivi parametara v1 i v2.4, odluke suca v1.1 i v1.2,
pravila granularnosti v1, kontekst iznad reference, točka mjerenja). Za Kornić se koristi zamrznuti ocijeni.py.
"""
import hashlib, json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(D))
import ocijeni_v1_2 as O
import mjeri_v22 as M22, mjeri_v23 as M23, mjeri_v24 as M24
import usporedi_v22 as U22, usporedi_v2 as U2, ocijeni as oc
import strukturiraj_v22 as s22, strukturiraj_v23 as s23, strukturiraj_v24 as s24, strukturiraj_v25 as s25
from citac_tekst import izdvoji_tekst

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
NV = M / "slijepo/novi_vinodolski"
NV_OZNAKE_SHA = "d79304cdd2eabe09713bbc4ccd0a9926a430781d277ac3efe3a4407f90235aad"
VERZIJE = {"v2.2": s22, "v2.3": s23, "v2.4": s24, "v2.5": s25}


def dokumenti():
    return {"PPUG Krk": izdvoji_tekst(M / U2.IZVOR, dio=1), "UPU 1 Krk": izdvoji_tekst(M / U2.IZVOR, dio=2),
            "UPU 2 Kornić": json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8")),
            "UPU Novi Vinodolski": izdvoji_tekst(NV / "nv_upu_sn_32_2026.html", dio=None)}


def struktura(r):
    C = list(r["clanci"].values()); P = [p for c in C for p in c.get("pravila", [])]
    return {"clanaka": len(C), "clanaka_s_pravilima": sum(1 for c in C if c.get("pravila")),
            "clanaka_odbijenih_vrsta": sum(1 for c in C if not c.get("pravila") and any(x.get("razlog_kod") == "SKUPINA_NEPOZNATA" for x in c.get("pregled", []))),
            "kandidata": len(P), "prijedlog": sum(p["status"] == "PRIJEDLOG" for p in P), "pregled": sum(p["status"] == "PREGLED" for p in P),
            "odbijenih_recenica": sum(len(c.get("nepokriveno", [])) for c in C)}


def pripremi_usporedbu():
    M22.mapa = M24.mapa
    M22.KONTEKST[:] = json.loads((D / "odluke_suca_v1_1.json").read_text(encoding="utf-8"))["kontekst_clanka"]
    M23.granularnost = M24.granularnost
    U22.razlike = O.razlike_v12


def kontekst_za(izl):
    M23.KONT.clear()
    for x in izl.values():
        for c in x["clanci"].values():
            for p in c.get("pravila", []):
                M23.KONT[p["id"]] = p.get("kontekst_primjene") or []


def main():
    O.integritet()
    assert sha(NV / "neovisne_oznake.json") == NV_OZNAKE_SHA
    pripremi_usporedbu()
    doc = dokumenti()
    ref = json.loads((D / "referenca_v1_2.json").read_text(encoding="utf-8"))
    Znv = json.loads((NV / "neovisne_oznake.json").read_text(encoding="utf-8"))["zapisi"]
    out = {"struktura": {}, "krk": {}, "kornic": {}, "novi_vinodolski": {}, "pravno_potvrdeno": 0,
           "napomena": "sva tri plana su razvojni skupovi za v2.5; generalizacija se mjeri tek slijepim testom na trećem planu"}
    for v, s in VERZIJE.items():
        r = {n: s.strukturiraj(d, None, n) for n, d in doc.items()}
        out["struktura"][v] = {n: struktura(x) for n, x in r.items()}
        # Krk: referenca v1.2 (samo označeni članci/stavci, kao u mjeri_v24)
        izl = {"ppug": r["PPUG Krk"], "upu1": {"clanci": {k: c for k, c in r["UPU 1 Krk"]["clanci"].items() if k in ("14", "24")}}}
        kontekst_za(izl)
        MP = M22.mapa()
        uP, uZ = [], []
        for g, (izv, opseg) in M22.PODRUCJE.items():
            Z = ref["skupine"][g]["zapisi"]
            P = [p for c in izl[izv]["clanci"].values() for p in c.get("pravila", []) if (p["clanak"], p["stavak"]) in opseg]
            uP += P; uZ += [dict(o, id=f"{g}:{o['id']}") for o in Z]
        sk, dk = M22.usporedi(uP, uZ, MP)
        out["krk"][v] = {"ukupno": sk, "pogresno": dk["pogresno"]}
        # Kornić: zamrznuti ocijeni.py nad čl. 38.–40.
        r2 = r["UPU 2 Kornić"]
        out["kornic"][v] = oc.ocijeni({"clanci": {k: c for k, c in r2["clanci"].items() if k in ("38", "39", "40")}},
                                      json.loads((M / "oznake/upu2_cl38_40.json").read_text(encoding="utf-8")))[0]
        # Novi Vinodolski: neovisne oznake, čl. 19., 20., 23., 24.
        rn = r["UPU Novi Vinodolski"]
        izn = {"nv": {"clanci": {k: c for k, c in rn["clanci"].items() if k in ("19", "20", "23", "24")}}}
        kontekst_za(izn)
        Pn = [p for c in izn["nv"]["clanci"].values() for p in c.get("pravila", [])]
        sn, dn = M22.usporedi(Pn, Znv, MP)
        out["novi_vinodolski"][v] = {"ukupno": sn, "po_clanku": {c: M22.usporedi([p for p in Pn if p["clanak"] == c], [o for o in Znv if o["clanak"] == c], MP)[0]
                                                                for c in (19, 20, 23, 24)},
                                     "pogresno": dn["pogresno"], "pregled_bez_oznake": [x for x in dn["pregled"] if not x["oznaka"]]}
    O.integritet()
    p = D / "mjerenje_v25.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, sha(p)


if __name__ == "__main__":
    o, s = main()
    print("STRUKTURA (članci s pravilima / odbijeni zbog vrste / kandidati / prijedlog / pregled / odbijene rečenice)")
    for v, x in o["struktura"].items():
        print(v, {n: (y["clanaka_s_pravilima"], y["clanaka_odbijenih_vrsta"], y["kandidata"], y["prijedlog"], y["pregled"], y["odbijenih_recenica"]) for n, y in x.items()})
    K = [("tocno_prihvaceno", "točno"), ("tocno_uz_pravilo_granularnosti", "+gran"), ("pogresno_prihvaceno", "pogr"), ("pravilno_na_pregled", "pravPr"),
         ("nepotrebno_na_pregled", "nepPr"), ("pregled_bez_oznake", "prBez"), ("propusteno", "prop"), ("preciznost_prihvacenih", "prec"),
         ("pokrivenost_prihvacanja_od_JASAN", "odJAS")]
    for plan in ("krk", "novi_vinodolski"):
        for v, x in o[plan].items():
            print(plan[:4], v, " ".join(f"{n}={x['ukupno'][a]}" for a, n in K))
    for v, x in o["kornic"].items():
        print("kornic", v, x)
    for v, x in o["novi_vinodolski"].items():
        for e in x["pogresno"]:
            print("NV POGR", v, e["id"], e["parametar"], e["vrijednost"], e["vrsta_gradevine"], e["uvjet"][:60], e["najbliza_oznaka"])
    for v, x in o["krk"].items():
        for e in x["pogresno"]:
            print("KRK POGR", v, e["id"], e["parametar"], e["vrijednost"], e["najbliza_oznaka"])
    print("sha", s)

#!/usr/bin/env python3
"""Regresijsko mjerenje v2.5 → v2.6 na četiri obitelji planova (sve su sada razvojni skupovi):
Krk (PPUG + UPU 1, referenca v1.2), Kornić (UPU 2 čl. 38.–40.), Novi Vinodolski (neovisne oznake, čl. 19./20./23./24.)
i Crikvenica centar I (neovisne oznake slijepog testa v2.5, čl. 23.–26.).

    python3 mjeri_v26.py      # → mjerenje_v26.json + tablice

Za svaki plan i verziju:
  struktura   – članci, članci s pravilima, kandidati, prijedlog, pregled (cijeli dokument);
  točnost     – strogo i semantički (vidi dolje), na označenim člancima;
  kontekst    – broj pravila s razlozima gubitka konteksta (KONTEKST_IZGUBLJEN, KONTEKST_NADREDJENE_ALINEJE,
                VRSTA_VISEZNACNA, UVJET_MOGUCE_IZGUBLJEN) i broj takvih pravila koja bi bez zaštite bila prihvaćena.
Usporedba:
  Krk        strogo = pravila mjeri_v24 (nazivi v1 + v2.4, odluke suca v1.1/v1.2, granularnost v2.4);
             semantički = strogo + nazivi v2.5/v2.6, istoznačnice, JEDINICA_BROJA_ETAZA.
  NV, Crik.  strogo = usporedi_v22.usporedi_oznake s U.mapa() (postupak slijepog testa);
             semantički = mjeri_v25.usporedi_nv + nazivi i istoznačnice v2.6.
  Kornić     zamrznuti ocijeni.py (jedan način).
Učitavanje: v2.5 kao u svom slijepom testu (Crikvenica preko zamrznutog prilagodnika); v2.6 preko izvor_v26.ucitaj.
Referentne oznake se ne mijenjaju.
"""
import hashlib, json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(D))
import mjeri_v25 as X
import ocijeni_v1_2 as O
import mjeri_v22 as M22, mjeri_v23 as M23, mjeri_v24 as M24
import usporedi_v22 as U22, usporedi_v2 as U2, ocijeni as oc
import strukturiraj_v25 as s25, strukturiraj_v26 as s26
import izvor_v26 as I
from citac_tekst import izdvoji_tekst

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
CR = M / "slijepo/crikvenica_centar_1"
CR_OZNAKE_SHA = "5c086d342a8cb4e6456dcfc3b487e1cea10a7c23379ab05ecabf2f5478e87287"
KONTEKST_KODOVI = ("KONTEKST_IZGUBLJEN", "KONTEKST_NADREDJENE_ALINEJE", "VRSTA_VISEZNACNA", "UVJET_MOGUCE_IZGUBLJEN", "VRSTA_IZ_UVODA_V25", "VRSTA_IZ_UVODA_V26")
KLJUC = [("tocno_prihvaceno", "točno"), ("tocno_uz_pravilo_granularnosti", "+gran"), ("pogresno_prihvaceno", "pogr"),
         ("pravilno_na_pregled", "pravPr"), ("nepotrebno_na_pregled", "nepPr"), ("pregled_bez_oznake", "prBez"), ("propusteno", "prop"),
         ("preciznost_prihvacenih", "prec"), ("pokrivenost_prihvacanja_od_JASAN", "odJAS")]


def mapa26():
    MP = X.mapa25()
    dop = json.loads((D / "mapiranje_v26.json").read_text(encoding="utf-8"))
    for k, v in dop["parametri"].items():
        MP["parametri"].setdefault(k, v[0]); MP["parametri_v22"][k] = list(v)
    for k, v in dop["vrsta_gradevine_istoznacnice"].items():
        st = MP["vrsta_gradevine_istoznacnice"].get(k, [])
        st = [st] if isinstance(st, str) else list(st)
        MP["vrsta_gradevine_istoznacnice"][k] = st + [x for x in v if x not in st]
    return MP


def dokumenti(v):
    if v == "v2.5":
        return {"PPUG Krk": izdvoji_tekst(M / U2.IZVOR, dio=1), "UPU 1 Krk": izdvoji_tekst(M / U2.IZVOR, dio=2),
                "UPU 2 Kornić": json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8")),
                "UPU Novi Vinodolski": izdvoji_tekst(X.NV / "nv_upu_sn_32_2026.html", dio=None),
                "UPU Crikvenica centar I": izdvoji_tekst(CR / "crikvenica_upu_centar_1.prilagodjeno.html", dio=None)}
    return {"PPUG Krk": I.ucitaj(M / U2.IZVOR, dio=1), "UPU 1 Krk": I.ucitaj(M / U2.IZVOR, dio=2),
            "UPU 2 Kornić": json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8")),
            "UPU Novi Vinodolski": I.ucitaj(X.NV / "nv_upu_sn_32_2026.html"),
            "UPU Crikvenica centar I": I.ucitaj(CR / "crikvenica_upu_centar_1.html")}


def kontekst(r, clanci=None):
    P = [p for c in r["clanci"].values() for p in c.get("pravila", []) if clanci is None or p.get("clanak") in clanci]
    K = [p for p in P if any(k in KONTEKST_KODOVI for k in (p.get("razlog_kod") or []))]
    samo = [p for p in K if all(k in KONTEKST_KODOVI for k in (p.get("razlog_kod") or []))]
    return {"pravila": len(P), "s_gubitkom_konteksta": len(K), "zadrzano_samo_zbog_konteksta": len(samo),
            "po_razlogu": {k: sum(k in (p.get("razlog_kod") or []) for p in P) for k in KONTEKST_KODOVI}}


def oznaceni(r, br):
    return {"clanci": {k: c for k, c in r["clanci"].items() if c["clanak"] in br}}


def usporedi_oznake(r, Z, br):
    P = [p for c in oznaceni(r, br)["clanci"].values() for p in c.get("pravila", [])]
    MP = U22.mapa()
    s, d = U22.usporedi_oznake(P, Z, MP)
    X.pripremi_usporedbu(True); M22.mapa = mapa26
    s2, d2, po2 = X.usporedi_nv(oznaceni(r, br), Z, br)
    return {"strogo": {"ukupno": s, "pogresno": d["pogresno"]},
            "semanticki": {"ukupno": s2, "po_clanku": po2, "pogresno": d2["pogresno"], "detalji": d2}}


def main():
    O.integritet()
    assert sha(X.NV / "neovisne_oznake.json") == X.NV_OZNAKE_SHA
    assert sha(CR / "neovisne_oznake.json") == CR_OZNAKE_SHA
    ref = json.loads((D / "referenca_v1_2.json").read_text(encoding="utf-8"))
    Znv = json.loads((X.NV / "neovisne_oznake.json").read_text(encoding="utf-8"))["zapisi"]
    Zcr = json.loads((CR / "neovisne_oznake.json").read_text(encoding="utf-8"))["zapisi"]
    out = {"struktura": {}, "kontekst": {}, "krk": {}, "kornic": {}, "novi_vinodolski": {}, "crikvenica": {}, "pravno_potvrdeno": 0,
           "napomena": "svi planovi su razvojni skupovi za v2.6 (Crikvenica od slijepog testa v2.5); generalizacija se mjeri tek novim slijepim testom"}
    import functools

    class s26b:  # samo za mjerenje mogućeg učinka: v2.6 bez zaštite VRSTA_IZ_UVODA_V26 (nije zamrznuto ponašanje)
        strukturiraj = functools.partial(s26.strukturiraj, prihvati_vrstu_iz_uvoda=True)
    for v, s in (("v2.5", s25), ("v2.6", s26), ("v2.6_bez_zastite_vrste", s26b)):
        doc = dokumenti("v2.5" if v == "v2.5" else "v2.6")
        r = {n: s.strukturiraj(d, None, n) for n, d in doc.items()}
        out["struktura"][v] = {n: X.struktura(x) for n, x in r.items()}
        out["kontekst"][v] = {n: kontekst(x) for n, x in r.items()}
        out["kontekst"][v]["označeni NV"] = kontekst(r["UPU Novi Vinodolski"], (19, 20, 23, 24))
        out["kontekst"][v]["označeni Crikvenica"] = kontekst(r["UPU Crikvenica centar I"], (23, 24, 25, 26))
        # Krk
        upu1 = (s.strukturiraj(izdvoji_tekst(M / U2.IZVOR, [14, 24], dio=2), None, "UPU 1 – Krk") if v == "v2.5" else
                s.strukturiraj(I.ucitaj(M / U2.IZVOR, dio=2, clanci=[14, 24]), None, "UPU 1 – Krk"))
        izl = {"ppug": r["PPUG Krk"], "upu1": upu1}
        out["krk"][v] = {}
        for nacin, pravila in (("strogo", False), ("semanticki", True)):
            X.pripremi_usporedbu(pravila)
            if pravila:
                M22.mapa = mapa26
            rk = O.ocijeni(izl, ref, "v2.3", True)
            out["krk"][v][nacin] = {"ukupno": rk["ukupno"], "pogresno": rk["detalji_ukupno"]["pogresno"]}
        out["kontekst"][v]["označeni Krk"] = {"pravila_u_opsegu": sum(1 for g, (izv, op) in M22.PODRUCJE.items()
                                                                     for c in izl[izv]["clanci"].values() for p in c.get("pravila", [])
                                                                     if (p["clanak"], p["stavak"]) in op)}
        # Kornić
        r2 = r["UPU 2 Kornić"]
        out["kornic"][v] = oc.ocijeni({"clanci": {k: c for k, c in r2["clanci"].items() if k in ("38", "39", "40")}},
                                      json.loads((M / "oznake/upu2_cl38_40.json").read_text(encoding="utf-8")))[0]
        # NV i Crikvenica
        out["novi_vinodolski"][v] = usporedi_oznake(r["UPU Novi Vinodolski"], Znv, (19, 20, 23, 24))
        out["crikvenica"][v] = usporedi_oznake(r["UPU Crikvenica centar I"], Zcr, (23, 24, 25, 26))
    O.integritet()
    p = D / "mjerenje_v26.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, sha(p)


if __name__ == "__main__":
    o, s = main()
    for v, x in o["struktura"].items():
        print("STRUKTURA", v, {n: (y["clanaka_s_pravilima"], y["kandidata"], y["prijedlog"], y["pregled"]) for n, y in x.items()})
    for v, x in o["kontekst"].items():
        print("KONTEKST", v, {n: (y.get("s_gubitkom_konteksta"), y.get("zadrzano_samo_zbog_konteksta")) for n, y in x.items()})
    for plan in ("krk", "novi_vinodolski", "crikvenica"):
        for v, x in o[plan].items():
            for nacin in ("strogo", "semanticki"):
                u = x[nacin]["ukupno"]
                print(plan[:5], v, nacin.ljust(10), " ".join(f"{n}={u.get(a)}" for a, n in KLJUC))
                for e in x[nacin]["pogresno"]:
                    print("     POGR", e["id"], e["parametar"], e["vrijednost"], e.get("vrsta_gradevine"), e.get("najbliza_oznaka"))
    for v, x in o["kornic"].items():
        print("kornic", v, {k: x[k] for k in ("tocno", "pogresno", "dvosmisleno", "propusteno")})
    print("sha", s)

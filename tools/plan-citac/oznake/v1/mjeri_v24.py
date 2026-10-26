#!/usr/bin/env python3
"""Mjerenje razvojne v2.4 na referentnom skupu v1.2, istim postupkom kao ocijeni_v1_2.py (v2.2 i v2.3 za usporedbu).

    python3 mjeri_v24.py    # → mjerenje_v24_ref_v1_2.json + tablica

Dodano je samo:
  - nazivi novih šifri parametara iz mapiranje_v24.json;
  - TOCKA_MJERENJA_IZRAZ: dio uvjeta oznake »visina od <točka>« jednak je točki mjerenja čitača »od <točka>« (isti izraz bez
    riječi »visina«, koja je već parametar); broji se kao pravilo granularnosti.
Kontekst primjene broji se kao u v2.3.
SKUP JE RAZVOJNI: v2.4 je razvijana gledajući PPUG čl. 20., 39., 50. i UPU 1 čl. 24.; ovo nije dokaz generalizacije.
"""
import json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(D))
import ocijeni_v1_2 as O
import mjeri_v22 as M22
import strukturiraj_v22 as s22, strukturiraj_v23 as s23, strukturiraj_v24 as s24
import usporedi_v2 as U2

_mapa = M22.mapa


def mapa():
    MP = _mapa()
    for k, v in json.loads((D / "mapiranje_v24.json").read_text(encoding="utf-8"))["parametri"].items():
        MP["parametri"].setdefault(k, v[0]); MP["parametri_v22"][k] = list(v)
    return MP


import usporedi_v22 as U22, mjeri_v23 as M23
_gran = M23.granularnost


def granularnost(z, o, MP):
    g = _gran(z, o, MP)
    if g is not None:
        return g
    for x in M22.inacice(o):
        u = x.get("uvjet_primjene") or ""
        u2 = "; ".join(d[len("visina "):] if d.strip().lower().startswith("visina od ") else d for d in u.split("; "))
        if u2 != u:
            y = dict(x, uvjet_primjene=u2, prihvatljivo=None)
            if not U22.razlike(z, y, MP):
                return ["TOCKA_MJERENJA_IZRAZ"]
            g2 = _gran(z, y, MP)
            if g2 is not None:
                return g2 + ["TOCKA_MJERENJA_IZRAZ"]
    return None


def main():
    O.integritet()
    M22.mapa = mapa
    M22.KONTEKST[:] = json.loads((D / "odluke_suca_v1_1.json").read_text(encoding="utf-8"))["kontekst_clanka"]
    ref = json.loads((D / "referenca_v1_2.json").read_text(encoding="utf-8"))
    izl = {"v2.2": O.izlazi(s22), "v2.3": O.izlazi(s23), "v2.4": O.izlazi(s24)}
    det = U2.sha_obj(O.izlazi(s24)["ppug"]) == U2.sha_obj(izl["v2.4"]["ppug"])
    R = {}
    M23.granularnost = granularnost  # ista pravila usporedbe za sve tri verzije (v2.2 nema kontekst, pa ga pravilo ne dira)
    for v in izl:
        R[v] = O.ocijeni(izl[v], ref, "v2.3", True)
    M23.granularnost = _gran
    O.integritet()
    out = {"referenca": {"datoteka": "referenca_v1_2.json", "sha256": O.sha(D / "referenca_v1_2.json")}, "determinizam_v24": det,
           "rezultati": R, "napomena": "razvojni skup; nije dokaz generalizacije", "pravno_potvrdeno": 0}
    p = D / "mjerenje_v24_ref_v1_2.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, O.sha(p)


if __name__ == "__main__":
    o, s = main()
    K = [("tocno_prihvaceno", "točno"), ("tocno_uz_pravilo_granularnosti", "+gran"), ("pogresno_prihvaceno", "pogr"), ("pravilno_na_pregled", "pravPr"),
         ("nepotrebno_na_pregled", "nepPr"), ("pregled_bez_oznake", "prBezOzn"), ("propusteno", "prop"), ("preciznost_prihvacenih", "prec"),
         ("pokrivenost_prihvacanja_od_JASAN", "odJASAN"), ("pokrivenost_izdvajanja", "izdv")]
    for v, x in o["rezultati"].items():
        print(v, " ".join(f"{n}={x['ukupno'][a]}" for a, n in K))
        print("   ", {g[:2]: (y["tocno_prihvaceno"] + y["tocno_uz_pravilo_granularnosti"], y["pogresno_prihvaceno"], y["propusteno"]) for g, y in x["po_skupini"].items()})
    for x in o["rezultati"]["v2.4"]["detalji_ukupno"]["pogresno"]:
        print("POGR", x["id"], x["parametar"], x["vrijednost"], x["vrsta_gradevine"], x["uvjet"][:80], x["najbliza_oznaka"])
    print("determinizam", o["determinizam_v24"], "sha", s)

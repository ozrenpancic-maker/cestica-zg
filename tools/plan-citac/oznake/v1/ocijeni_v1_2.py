#!/usr/bin/env python3
"""Ponovna ocjena postojećih izlaza v2.2 i zamrznute v2.3 na referentnom skupu v1.1 i v1.2, bez promjene čitača.

    python3 ocijeni_v1_2.py      # → ocjena_v1_2.json + tablica

Tablica 2 × 2 (čitač × referenca) odvaja učinak novih oznaka (ista verzija čitača, druga referenca) od učinka koda
(ista referenca, druga verzija čitača). Zamrznuti mjeri_v22.py / mjeri_v23.py se ne mijenjaju; njihove se funkcije
koriste uz:
  - odluku 3 v1.2 u usporedbi: kod načina gradnje vrijednost »<oblik>« = »<oblik> građevine/kuće« (isti subjekt
    provjerava zamrznuta usporedba: članak, stavak, vrsta građevine);
  - put do reference kao parametar.
Prije i poslije provjerava se ZAMRZNUTO_v2_2.json i ZAMRZNUTO_v2_3.json.
"""
import hashlib, json, re, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(D))
import mjeri_v22 as M22
import mjeri_v23 as M23
import usporedi_v22 as U22
import usporedi_v2 as U2
import strukturiraj_v22 as s22
import strukturiraj_v23 as s23
from citac_tekst import izdvoji_tekst

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
REF = {"v1.1": ("referenca_v1.json", "e6b2f7a5282d99694ad8cd0cd5939e5db350fa28c8736ffd6e1eddd44a7f85cc"),
       "v1.2": ("referenca_v1_2.json", None)}
_raz = U22.razlike
_gran22 = M22.granularnost


def _oblik(v):
    return re.sub(r"\s+(građevin[ae]|kuć[ae])$", "", U22._nv(v)) if isinstance(v, str) else v


def razlike_v12(z, o, MP):
    r = _raz(z, o, MP)
    if "vrijednost" in r and z["parametar"] == "način gradnje" and o["parametar"] == "način gradnje" and _oblik(z["vrijednost"]) == _oblik(o["vrijednost"]):
        r = [x for x in r if x != "vrijednost"]
    return r


def integritet():
    for f in ("ZAMRZNUTO_v2_2.json", "ZAMRZNUTO_v2_3.json"):
        z = json.loads((M / f).read_text(encoding="utf-8"))
        los = [p for g in ("kod", "mapiranje") for p, s in z[g].items() if sha(M / p) != s]
        if los:
            raise SystemExit(f"INTEGRITET {f}: " + ", ".join(los))
    assert sha(D / REF["v1.1"][0]) == REF["v1.1"][1]


def izlazi(s):
    return {"ppug": s.strukturiraj(izdvoji_tekst(M / U2.IZVOR, dio=1), None, "PPUG Krk"),
            "upu1": s.strukturiraj(izdvoji_tekst(M / U2.IZVOR, [14, 24], dio=2), None, "UPU 1 – Krk")}


def ocijeni(izl, ref, verzija, odluka3):
    U22.razlike = razlike_v12 if odluka3 else _raz
    M22.granularnost = M23.granularnost if verzija == "v2.3" else _gran22
    M23.KONT.clear()
    if verzija == "v2.3":
        for x in izl.values():
            for c in x["clanci"].values():
                for p in c.get("pravila", []):
                    M23.KONT[p["id"]] = p.get("kontekst_primjene") or []
    MP = M22.mapa()
    out, uP, uZ = {}, [], []
    for g, (izv, opseg) in M22.PODRUCJE.items():
        Z = ref["skupine"][g]["zapisi"]
        P = [p for c in izl[izv]["clanci"].values() for p in c.get("pravila", []) if (p["clanak"], p["stavak"]) in opseg]
        out[g] = M22.usporedi(P, Z, MP)
        uP += P; uZ += [dict(o, id=f"{g}:{o['id']}") for o in Z]
    s, d = M22.usporedi(uP, uZ, MP)
    U22.razlike = _raz; M22.granularnost = _gran22
    return {"po_skupini": {g: v[0] for g, v in out.items()}, "ukupno": s, "detalji_ukupno": d}


def main():
    integritet()
    M22.KONTEKST[:] = json.loads((D / "odluke_suca_v1_1.json").read_text(encoding="utf-8"))["kontekst_clanka"]
    ref = {k: json.loads((D / f).read_text(encoding="utf-8")) for k, (f, _) in REF.items()}
    izl = {"v2.2": izlazi(s22), "v2.3": izlazi(s23)}
    R = {}
    for v in ("v2.2", "v2.3"):
        for rk in ("v1.1", "v1.2"):
            R[f"{v}|{rk}"] = ocijeni(izl[v], ref[rk], v, rk == "v1.2")
    integritet()
    out = {"citaci": {"v2.2": "ZAMRZNUTO_v2_2.json", "v2.3": "ZAMRZNUTO_v2_3.json"},
           "reference": {k: {"datoteka": f, "sha256": sha(D / f)} for k, (f, _) in REF.items()},
           "odluke": {"v1.1": sha(D / "odluke_suca_v1_1.json"), "v1.2": sha(D / "odluke_suca_v1_2.json")},
           "rezultati": R, "pravno_potvrdeno": 0}
    p = D / "ocjena_v1_2.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, sha(p)


if __name__ == "__main__":
    o, s = main()
    K = [("tocno_prihvaceno", "točno"), ("tocno_uz_pravilo_granularnosti", "+gran"), ("pogresno_prihvaceno", "pogr"), ("pravilno_na_pregled", "pravPr"),
         ("nepotrebno_na_pregled", "nepPr"), ("pregled_bez_oznake", "prBezOzn"), ("propusteno", "prop"), ("preciznost_prihvacenih", "prec"),
         ("pokrivenost_prihvacanja_od_JASAN", "odJASAN")]
    for k, v in o["rezultati"].items():
        print(k.ljust(10), " ".join(f"{n}={v['ukupno'][a]}" for a, n in K))
    for k, v in o["rezultati"].items():
        print(k, [(x["id"], x["parametar"], x["vrijednost"], x["najbliza_oznaka"]) for x in v["detalji_ukupno"]["pogresno"]])
    print("sha", s)

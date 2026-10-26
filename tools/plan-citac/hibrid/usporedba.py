#!/usr/bin/env python3
"""HIBRIDNI ČITAČ v1 – usporedba s referentnim oznakama, ista za determinističku v2.6 i za hibrid.

Kandidat i oznaka se sparuju kad se slažu u svim poljima oznake:
  članak, stavak, točka, parametar, operator, vrijednost, jedinica, vrsta građevine, vrsta pravila,
  uvjet (svaki odlomak uvjeta iz oznake mora biti u uvjetu kandidata; oznaka bez uvjeta → kandidat bez uvjeta).
Dva načina, oba određena prije slijepog testa:
  strogo      – polja doslovno (normalizirani razmaci i mala slova; točka bez zagrade);
  semanticki  – strogo, uz: točka »-« = bez točke (granica alineje); broj bez jedinice = »koeficijent« samo za kig/kis;
                vrsta građevine jednaka kad vrste_gradevine prepozna istu vrstu u oba naziva i kad su oblik
                (slobodnostojeća/dvojna/ugrađena) i stanje (nova/postojeća) isti; »=« = »dopustenje« za opisnu vrijednost.
Semantički način ne dopušta drugačiju vrijednost, operator, parametar, uvjet ni vrstu pravila.
Ishodi: točno prihvaćeno (JASAN / PREGLED oznaka), pogrešno prihvaćeno, na pregledu s oznakom, na pregledu bez oznake,
propušteno; pokrivenost JASNIH = točno prihvaćeni s JASAN oznakom / sve JASAN oznake.
"""
import re, sys
from pathlib import Path

M = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(M / "oznake/v1"))
import vrste_gradevina as vg

_n = lambda s: re.sub(r"\s+", " ", str(s if s is not None else "")).strip().lower().replace("–", "-").replace("m 2", "m²").replace("m2", "m²")
KOEF = ("kig", "kis")


def _tocka(t):
    if t is None:
        return None
    t = str(t).strip().rstrip(")")
    return t or None


def _kanon_vrste(s):
    s = s or ""
    r = vg.prepoznaj(s, samo_pocetak=False)
    ob = next((o for o, rx in (("slob", r"slobodnostoj|samostoj"), ("dvoj", r"dvojn"), ("ugr", r"ugrađ|u nizu")) if re.search(rx, s, re.I)), None)
    st = "nova" if re.search(r"\(nov", s, re.I) else ("postojeca" if re.search(r"\(postoje", s, re.I) else None)
    return (tuple(r["kodovi"]) if r else _n(re.sub(r"\(.*?\)", "", s)), ob, st)


def _jed(j, par, nacin):
    j = None if j in ("", None) else _n(j)
    if nacin == "semanticki" and j == "koeficijent" and not any(k in _n(par) for k in KOEF):
        return None
    return j


def _vr(v):
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return _n(v)


def razlike(c, o, nacin):
    r = []
    if c["clanak"] != o["clanak"]:
        r.append("clanak")
    if c["stavak"] != o.get("stavak"):
        r.append("stavak")
    tc, to = _tocka(c.get("tocka")), _tocka(o.get("tocka"))
    if tc != to and not (nacin == "semanticki" and {tc, to} <= {"-", None}):
        r.append("tocka")
    pc, po = _n(c["parametar"]), _n(o["parametar"])
    KIS = "najveći koeficijent iskoristivosti (kis)"
    if pc != po and not (nacin == "semanticki" and pc.startswith(KIS) and po.startswith(KIS) and "nadzemn" not in pc + po):
        r.append("parametar")
    oc, oo = _n(c["operator"]), _n(o["operator"])
    if oc != oo and not (nacin == "semanticki" and {oc, oo} == {"=", "dopustenje"} and _n(c.get("jedinica")) == "opis"):
        r.append("operator")
    if _jed(c.get("jedinica"), c["parametar"], nacin) != _jed(o.get("jedinica"), o["parametar"], nacin):
        r.append("jedinica")
    a, b = _vr(c["vrijednost"]), _vr(o["vrijednost"])
    if (isinstance(a, float) and isinstance(b, float) and abs(a - b) > 1e-9) or (not (isinstance(a, float) and isinstance(b, float)) and a != b):
        r.append("vrijednost")
    vc, vo = c.get("vrsta_gradevine") or "", o.get("vrsta_gradevine") or ""
    if _n(vc) != _n(vo) and not (nacin == "semanticki" and vc and vo and _kanon_vrste(vc) == _kanon_vrste(vo)):
        r.append("vrsta_gradevine")
    if c.get("vrsta_pravila") != o.get("vrsta_pravila"):
        r.append("vrsta_pravila")
    dij = [re.sub(r"^iznimno,?\s*", "", d.strip(), flags=re.I) for d in (o.get("uvjet_primjene") or "").split("; ") if d.strip()]
    dij = [d for d in dij if d]
    ut = _n(c.get("uvjet_tekst"))                       # vlastiti uvjeti odredbe
    uk = _n(c.get("uvjet_konteksta"))                   # uvjet uvoda i tekst iznimke (kontekst; iznimka je i u vrsti pravila)
    if dij:
        if not all(_n(d) in ut + " | " + uk for d in dij):
            r.append("uvjet")
    elif ut:
        r.append("uvjet")
    return r


def inacice(o):
    out = [o]
    if o.get("prihvatljivo"):
        b = dict(o); b.update({k: v for k, v in o["prihvatljivo"].items() if v is not None}); out.append(b)
    return out


def usporedi(K, Z, nacin):
    """K: kandidati {id, clanak, stavak, tocka, parametar, operator, vrijednost, jedinica, vrsta_gradevine, vrsta_pravila,
    uvjet_tekst, prihvacen(bool)}; Z: oznake. Vraća (sažetak, detalji)."""
    used = [False] * len(Z)
    D = {"tocno": [], "pogresno": [], "pregled_s_oznakom": [], "pregled_bez_oznake": [], "propusteno": []}
    for c in sorted(K, key=lambda c: not c["prihvacen"]):
        nad = next((i for i, o in enumerate(Z) if not used[i] and any(not razlike(c, x, nacin) for x in inacice(o))), None)
        if nad is not None:
            used[nad] = True
            (D["tocno"] if c["prihvacen"] else D["pregled_s_oznakom"]).append({"id": c["id"], "oznaka": Z[nad]["id"], "jednoznacnost": Z[nad].get("jednoznacnost")})
        elif c["prihvacen"]:
            bl = sorted(((len(razlike(c, o, nacin)), o["id"], razlike(c, o, nacin)) for o in Z if o["clanak"] == c["clanak"]), key=lambda x: x[0])[:1]
            D["pogresno"].append({"id": c["id"], "kandidat": {k: c[k] for k in ("clanak", "stavak", "tocka", "parametar", "operator", "vrijednost", "jedinica", "vrsta_gradevine", "vrsta_pravila", "uvjet_tekst")},
                                  "najbliza_oznaka": bl[0][1:] if bl else None, "citat": c.get("citat")})
        else:
            D["pregled_bez_oznake"].append({"id": c["id"]})
    D["propusteno"] = [{"oznaka": o["id"], "parametar": o["parametar"], "jednoznacnost": o.get("jednoznacnost")} for i, o in enumerate(Z) if not used[i]]
    jas = sum(1 for o in Z if o.get("jednoznacnost") == "JASAN")
    tj = sum(1 for x in D["tocno"] if x["jednoznacnost"] == "JASAN")
    pr = len(D["tocno"]) + len(D["pogresno"])
    s = {"oznaka": len(Z), "oznaka_JASAN": jas, "kandidata": len(K), "prihvaceno": pr, "tocno_prihvaceno": len(D["tocno"]), "tocno_prihvaceno_JASAN": tj,
         "pogresno_prihvaceno": len(D["pogresno"]), "na_pregledu": len(K) - pr, "pregled_s_oznakom": len(D["pregled_s_oznakom"]),
         "pregled_bez_oznake": len(D["pregled_bez_oznake"]), "propusteno": len(D["propusteno"]),
         "preciznost_prihvacenih": round(len(D["tocno"]) / pr, 3) if pr else None, "pokrivenost_JASNIH": round(tj / jas, 3) if jas else None}
    return s, D


# ---------------------------------------------------------------- pretvorba kandidata
def iz_hibrida(K, samo_tehnicki=False):
    out = []
    for i, k in enumerate(K):
        if k["_status"] == "ODBIJEN":
            continue
        vl = [u for u in (k.get("uvjeti") or []) if u.get("izvor") != "uvod"]
        kt = [u for u in (k.get("uvjeti") or []) if u.get("izvor") == "uvod"] + list(k.get("iznimke") or [])
        dij = [u.get("citat") for u in vl]   # uspoređuje se doslovni citat uvjeta, ne prepričani tekst
        dk = [u.get("citat") for u in kt]
        prih = k["_status"] == "AUTOMATSKI_PRIHVACEN" or (samo_tehnicki and k["_status"] == "TEHNICKI_PROVJEREN_ZA_PREGLED")
        out.append({"id": k.get("id") or f"H{i + 1:03d}", "clanak": k["clanak"], "stavak": k.get("stavak"), "tocka": k.get("_tocka", k.get("tocka")),
                    "uvjet_konteksta": " | ".join(x for x in dk if x), "parametar": k.get("parametar"),
                    "operator": k.get("operator"), "vrijednost": k.get("vrijednost"), "jedinica": k.get("jedinica"),
                    "vrsta_gradevine": (k.get("vrsta_gradevine") or {}).get("naziv"), "vrsta_pravila": k.get("vrsta_pravila"),
                    "uvjet_tekst": " | ".join(x for x in dij if x), "prihvacen": prih, "citat": k.get("citat")})
    return out


def iz_v26(pravila, MP):
    import usporedi_v22 as U22
    out = []
    for z in U22.u_zapise(pravila, MP):
        out.append({"id": z["id"], "clanak": z["clanak"], "stavak": z["stavak"], "tocka": z["tocka"], "parametar": z["parametar"], "operator": z["operator"],
                    "vrijednost": z["vrijednost"], "jedinica": z["jedinica"], "vrsta_gradevine": z["vrsta_gradevine"], "vrsta_pravila": z["vrsta_pravila"],
                    "uvjet_tekst": z["uvjet_tekst"], "prihvacen": z["status"] == "PRIJEDLOG", "citat": z.get("izvorni_citat")})
    return out

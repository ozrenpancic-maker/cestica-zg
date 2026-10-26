#!/usr/bin/env python3
"""EKSPERIMENT v2.5: struktura dokumenta i kontekst (prvi dio) + novi oblici odredbi (drugi dio).
Zamrznuti gramatika_v22 / v24 se ne mijenjaju; ovdje su samo dodaci koje koristi strukturiraj_v25.

STRUKTURA
- Priprema teksta koja čuva duljinu (svaki znak → točno jedan znak), pa se svaki citat vraća u izvorni oblik
  istim položajem u tekstu (`vrati_izvorno`):
    »•« (alineja) → »-«;  točka u kraticama »ul.«, »čl.«, »st.«, »br.«, »vis.«, »tzv.«, »npr.« → »․« (U+2024),
    »sl.« samo kad ne završava rečenicu (iza nje nije veliko slovo).
- Vrsta građevine iz cijele uvodne rečenice (`skupina_uvoda`): »… namijenjena je izgradnji poslovne građevine«,
  »uvjeti za izgradnju novih poslovnih i ugostiteljsko-turističkih građevina«, »grade se poslovne građevine«.
- Kontekst uvoda stavka (`kontekst_uvoda`): zona (planska oznaka), nova gradnja (izričito), iznimka (»Iznimno, …«).
"""
import re
import gramatika_v22 as g2
import vrste_gradevina as vg

VERZIJA = "gramatika-v2.5"
TOCKA_KRATICE = "․"
RX_KRATICA = re.compile(r"(?<![\wčćđšž])(ul|čl|st|br|vis|tzv|npr|tj|kbr)\.(?=\s*[\w(\d\'„“])", re.I)
RX_SL = re.compile(r"(?<![\wčćđšž])(sl)\.(?=\s*[,;:)\-]|\s+[a-zčćđšž])")


def pripremi(tekst):
    """Tekst iste duljine: »•« → »-«, točka kratice → U+2024."""
    t = tekst.replace("•", "-")
    t = RX_KRATICA.sub(lambda m: m.group(1) + TOCKA_KRATICE, t)
    t = RX_SL.sub(lambda m: m.group(1) + TOCKA_KRATICE, t)
    assert len(t) == len(tekst)
    return t


def vrati_izvorno(s, T, O):
    """Niz iz pripremljenog teksta T vraća u izvorni oblik iz O (isti položaj); inače samo vraća točke kratica."""
    if not isinstance(s, str) or not s:
        return s
    if len(s) >= 6:
        i = T.find(s)
        if i >= 0:
            return O[i:i + len(s)]
    return s.replace(TOCKA_KRATICE, ".")


def vrati_sve(obj, T, O):
    if isinstance(obj, dict):
        return {k: (v if k in ("id", "tocka", "status", "parametar", "operator", "vrsta_pravila", "obrazac", "gramatika") else vrati_sve(v, T, O))
                for k, v in obj.items()}
    if isinstance(obj, list):
        return [vrati_sve(v, T, O) for v in obj]
    if isinstance(obj, tuple):
        return tuple(vrati_sve(v, T, O) for v in obj)
    return vrati_izvorno(obj, T, O) if isinstance(obj, str) else obj


# ---------------------------------------------------------------- vrsta iz cijele uvodne rečenice
RX_OBJEKT = re.compile(
    r"\b(?:namijenjen\w*\s+(?:je|su)\s+)?(?:izgradnj\w+|gradnj\w+|grade\s+se|gradi\s+se|smještaj\w*)\s+(?:i\s+uređenj\w+\s+)?"
    r"(?:samo\s+)?(?:jedne\s+)?(?:nov\w+\s+|postojeć\w+\s+)?(?P<x>[^:;]+)", re.I)
RX_PAR = re.compile(r"^(?P<a>[a-zčćđšž\-]+)\s+i\s+(?P<b>[a-zčćđšž\-]+)\s+(?P<n>građevin\w*)", re.I)


def skupina_uvoda(uvod):
    """Vrsta građevine kao objekt glagola gradnje bilo gdje u uvodnoj rečenici. Vraća kodove ili None.
    »X i Y građevina« daje obje vrste. Usputni spomen (popis sadržaja) se ne uzima: objekt mora počinjati nazivom vrste."""
    for m in RX_OBJEKT.finditer(uvod or ""):
        x = m["x"].strip()
        mp = RX_PAR.match(x)
        if mp:
            kod = []
            for pr in (mp["a"], mp["b"]):
                r = vg.prepoznaj(f"{pr} {mp['n']}", samo_pocetak=True)
                if r:
                    kod += [k for k in r["kodovi"] if k not in kod]
            if kod:
                return tuple(kod)
        r = vg.prepoznaj(x, samo_pocetak=True)
        if r:
            return tuple(r["kodovi"])
    return None


# ---------------------------------------------------------------- kontekst uvoda stavka
RX_OZNAKE = re.compile(r"plansk\w+\s+oznak\w+\s+(?P<z>(?:\(?[A-Z][A-Z0-9\-]{0,10}\)?(?:\s*,\s*i\s+|\s*,\s*|\s+i\s+)?)+)|"
                       r"(?<=\s)oznakom\s+(?P<z2>[A-Z][A-Z0-9\-]{0,10})\b|"
                       r"namjene\s+–?\s*[a-zčćđšž]*\s*\((?P<z3>[A-Z][A-Z0-9]{0,4})\)", re.I)
RX_NOVA = re.compile(r"\b(?:za\s+novu\s+izgradnju|izgradnj\w+\s+nov\w+|nov\w+\s+izgradnj\w+|gradnj\w+\s+nov\w+)\b", re.I)
RX_IZNIMNO = re.compile(r"^\s*Iznimno,?\s+(?P<u>.+)$", re.I)


def oznake_zona(t):
    """Planske oznake zona iz teksta: »planskom oznakom (K1)«, »planskim oznakama (K21), (K22)«, »oznakom K21«,
    »gospodarske namjene – poslovne (K)«. Jednoslovna oznaka uzima se samo u zagradi iza »namjene«."""
    z = []
    for m in RX_OZNAKE.finditer(t or ""):
        if m["z3"]:
            kand = [m["z3"]]
        else:
            kand = [k for k in re.findall(r"[A-Z][A-Z0-9\-]{0,10}", m["z"] or m["z2"] or "") if len(k) > 1]
        z += [k for k in kand if k not in z]
    return z


def kontekst_uvoda(uvod, prethodni=None):
    """Kontekst koji uvod stavka prenosi na sva pravila stavka: zone, nova gradnja, iznimka (doslovni dokazi).
    »Na površinama iz stavka (n)« preuzima zone stavka n (prethodni: {n: kontekst})."""
    k = {"zone": oznake_zona(uvod), "nova": None, "iznimka": None, "dokaz_zone": None}
    mn = RX_NOVA.search(uvod or "")
    if mn:
        k["nova"] = mn.group()
    mi = RX_IZNIMNO.match(uvod or "")
    if mi:
        k["iznimka"] = mi["u"].strip()
    if not k["zone"] and prethodni:
        mr = re.search(r"površin\w+\s+iz\s+stavka\s+\((\d+)\)", uvod or "")
        if mr and int(mr.group(1)) in prethodni:
            k["zone"] = list(prethodni[int(mr.group(1))]["zone"])
            k["dokaz_zone"] = mr.group()
    if k["zone"] and not k["dokaz_zone"]:
        m = re.search(r"[^.;:]*(?:oznak|namjene\s*–)[^.;:]*", uvod or "")
        k["dokaz_zone"] = m.group().strip() if m else None
    return k

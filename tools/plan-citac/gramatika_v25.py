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


# ================================================================ OBLICI ODREDBI v2.5
# Svaki oblik je doslovan: vrijednosti, operatori i uvjeti uzimaju se iz teksta; ništa se ne nadopunjuje.
# Nove kategorije (ograde, zelenilo, kaskade/podzidi, krovne kućice, podzemne etaže, pomoćne građevine) su uvijek PREGLED
# (KATEGORIJA_NEVALIDIRANA) dok ih sudac ne potvrdi. Udaljenosti ovisne o visini zapisuju se kao uvjetni izraz (grane),
# nikad kao konačan broj, i uvijek su PREGLED (OVISI_O_VISINI).
R, zapis = g2.R, g2.zapis
NB = r"\d+(?:,\d+)?"
broj = lambda s: float(s.replace(",", "."))
M_ = r"(?:m|metra|metara)\b"
M2_ = r"(?:m\s*2|m²)"
KRAJ = r"\s*[.,;]?\s*$"
BROJ_RIJEC = {"jedna": 1, "jedan": 1, "jednu": 1, "dvije": 2, "dva": 2, "tri": 3, "četiri": 4, "pet": 5, "šest": 6}
RX_KOLIKO = rf"(?P<n>\d+|(?:{'|'.join(BROJ_RIJEC)})(?:\s*\(\d+\))?)"

NEVALIDIRANO = R("KATEGORIJA_NEVALIDIRANA", "nova kategorija odredbe (v2.5); prihvaća se tek nakon provjere suca")
IZVAN = R("PARAMETAR_IZVAN_POPISA", "parametar nije u zatvorenom popisu uputa za označavanje; prihvaća se tek uz pregled")
VISINSKI = R("OVISI_O_VISINI", "vrijednost ovisi o visini građevine; zapisana je kao uvjetni izraz, ne kao konačan broj")
UPUCIVANJE = R("UPUCIVANJE_NA_PROPIS", "dodatni uvjet upućuje na propis koji nije u tekstu plana")
OPERATOR_NEIZRICIT = R("OPERATOR_NEIZRICIT", "u tekstu nema »najmanje« / »najviše«; operator je zapisan doslovno kao »=«")
SUBJEKT_ALINEJE = R("SUBJEKT_IZ_ALINEJE", "subjekt »građevine« preuzet je iz prve rečenice alineje")
TUMACENJE_MOGUCE = R("TUMACENJE_MOGUCA_IZGRADNJA", "»moguća je izgradnja N« ne kaže izričito da je N najveći broj")
U_PRAVILU = R("U_PRAVILU", "»u pravilu« – odredba dopušta odstupanje koje nije određeno")


def broj_rijecju(s):
    """»4«, »četiri (4)«, »dvije (2)« → broj; riječ i broj u zagradi moraju se slagati, inače None."""
    s = s.strip()
    if s.isdigit():
        return int(s)
    m = re.match(r"([a-zčćđšž]+)(?:\s*\((\d+)\))?$", s, re.I)
    if not m or m.group(1).lower() not in BROJ_RIJEC:
        return None
    v = BROJ_RIJEC[m.group(1).lower()]
    return v if m.group(2) is None or int(m.group(2)) == v else None


def _z(par, op, v, j, vp, kw, **dod):
    d = dict(kw); d.update(dod)
    return zapis(par, op, v, j, vp, **d)


def _lit(*s):
    return [x for x in s if x]


def _skupina_namjene(n):
    r = vg.prepoznaj(f"{n} građevina", samo_pocetak=True) if n else None
    return tuple(r["kodovi"]) if r else None


def oblici(t, kont):
    """Vraća (zapisi, iskorišteni brojevi) ili None ako rečenica nije ni jedan od oblika v2.5."""
    t = t.strip()
    sk = kont.get("skupine")
    kw = dict(skupine=sk)
    prva = kont.get("prva") or ""
    pomocna_alineja = bool(re.search(r"\bmogu se graditi i pomoćne građevine\b", prva, re.I)) and prva.strip() != t

    # --- najmanja / najveća površina građevne čestice, s iznimkom za vrstu
    m = re.match(rf"površina građevne čestice ne može biti (?P<s>manja|veća) od (?P<v>{NB})\s*{M2_}"
                 rf"(?:\s*,\s*(?P<iu>iznimno (?P<iv>za [a-zčćđšž ]+?))\s+(?P<v2>{NB})\s*{M2_})?{KRAJ}", t, re.I)
    if m:
        par, op = ("minC", ">=") if m["s"].lower() == "manja" else ("maxC", "<=")
        out = [_z(par, op, broj(m["v"]), "m²", "OSNOVNO", kw)]
        if m["v2"]:
            out.append(_z(par, op, broj(m["v2"]), "m²", "IZNIMKA", kw, uvjeti=[m["iv"]],
                          razlozi=[R("VRSTA_IZ_IZNIMKE", f"iznimka vrijedi samo {m['iv']}; ta vrsta nije u uvodu stavka")]))
        return out, _lit(m["v"], m["v2"])

    # --- broj nadzemnih (i podzemnih) etaža
    m = re.match(rf"građevin[ae]\s+(?:mogu|može)\s+imati\s+do\s+{RX_KOLIKO}\s+(?P<k>nadzemn\w+ etaž\w+)"
                 rf"(?:\s+(?P<u>uz uvjet da je .+?))?{KRAJ}", t, re.I)
    if m and broj_rijecju(m["n"]) is not None:
        vp = "UVJETNO" if m["u"] else "OSNOVNO"
        return [_z("etazeMax", "<=", broj_rijecju(m["n"]), None, vp, kw, uvjeti=_lit(m["k"], m["u"]))], re.findall(r"\d+", m["n"] + " " + (m["u"] or ""))
    m = re.match(rf"najveći dopušteni broj etaža (?P<g>građevine [a-zčćđšž\- ]+?) su\s+{RX_KOLIKO}\s+(?P<k>nadzemn\w+ etaž\w+)"
                 rf"(?:\s+(?P<u>uz uvjet da je .+?))?(?:\s+te\s+(?P<pn>(?:jedna|dvije|tri|\d+)(?:\s*\(\d+\))?)\s+(?P<pk>podzemn\w+ etaž\w+)"
                 rf"(?:\s+(?P<pu>(?:ukoliko|ako) .+?))?)?{KRAJ}", t, re.I)
    if m and broj_rijecju(m["n"]) is not None:
        out = [_z("etazeMax", "<=", broj_rijecju(m["n"]), None, "UVJETNO" if m["u"] else "OSNOVNO", kw, uvjeti=_lit(m["k"], m["u"]))]
        lit = re.findall(r"\d+", m["n"] + " " + (m["u"] or ""))
        if m["pn"] and broj_rijecju(m["pn"]) is not None:
            out.append(_z("etazeMax", "<=", broj_rijecju(m["pn"]), None, "UVJETNO" if m["pu"] else "OSNOVNO", kw, uvjeti=_lit(m["pk"], m["pu"]),
                          razlozi=[R("ETAZE_PODZEMNE", "broj podzemnih etaža nije zaseban parametar zatvorenog popisa")]))
            lit += re.findall(r"\d+", m["pn"])
        return out, lit
    m = re.match(rf"moguća je izgradnja (?P<n>\d+) (?P<k>podzemn\w+ etaž\w+)\s*,?\s*(?P<u>(?:ukoliko|ako) .+?){KRAJ}", t, re.I)
    if m:
        return [_z("etazeMax", "<=", int(m["n"]), None, "UVJETNO", kw, uvjeti=[m["k"], m["u"]],
                   razlozi=[TUMACENJE_MOGUCE, R("ETAZE_PODZEMNE", "broj podzemnih etaža nije zaseban parametar zatvorenog popisa")])], [m["n"]]

    # --- udaljenost od regulacijskog pravca po kategoriji ulice (odluka suca v1.2/1: UVJETNO, kategorija u uvjetu)
    pom = dict(razlozi=[SUBJEKT_ALINEJE, NEVALIDIRANO], skupine=("pomocna",)) if pomocna_alineja else {}
    m = re.match(rf"najmanja udaljenost (?P<d>nadzemnog dijela građevin[ae] |građevin[ae] )od regulacijskog pravca (?P<u1>ul\S? [A-ZČĆĐŠŽ][\w ]+?) iznosi "
                 rf"(?P<v1>{NB})\s*{M_}\s*,\s*odnosno\s+(?P<v2>{NB})\s*{M_}\s+(?P<u2>od .+?){KRAJ}", t, re.I)
    if m:
        dod = [m["d"].strip()] if m["d"].lower().startswith("nadzemn") else []
        out = [_z("regulacija", ">=", broj(m["v1"]), "m", "UVJETNO", kw, uvjeti=_lit(m["u1"]) + dod, **pom),
               _z("regulacija", ">=", broj(m["v2"]), "m", "UVJETNO", kw, uvjeti=_lit(m["u2"]) + dod, **pom)]
        return out, _lit(m["v1"], m["v2"])
    m = re.match(r"najmanja udaljenost (?P<d>nadzemnog dijela građevin[ae] )?(?:građevin[ae] )?od regulacijskog pravca iznosi:\s*(?P<l>-.+?)\s*[.;]?\s*$", t, re.I)
    if m:
        stavke = [s.strip(" ,;") for s in re.split(r"(?:^|,)\s*-\s+", m["l"]) if s.strip(" ,;")]
        out, lit = [], []
        for s in stavke:
            ms = re.fullmatch(rf"(?P<v>{NB})\s*{M_}\s+(?P<u>od .+)", s, re.I)
            if not ms:
                return None
            out.append(_z("regulacija", ">=", broj(ms["v"]), "m", "UVJETNO", kw, uvjeti=[ms["u"]] + ([m["d"].strip()] if m["d"] else []), **pom))
            lit.append(ms["v"])
        return (out, lit) if len(out) >= 2 else None

    # --- udaljenost od granice susjedne čestice ovisna o visini građevine → uvjetni izraz
    m = re.match(rf"najmanja udaljenost od granice susjedne građevne čestice iznosi (?P<v1>{NB})\s*{M_}\s*(?P<u1>za građevine visine do (?P<h>{NB})\s*{M_})\s*,\s*"
                 rf"odnosno\s+najmanje\s+(?P<v2>{NB})\s*{M_}\s*(?P<u2>za više građevine)(?:\s*,\s*(?P<u>uz uvjet da .+?))?{KRAJ}", t, re.I)
    if m:
        izraz = {"izraz": f"{m['v1']} m ({m['u1']}); {m['v2']} m ({m['u2']})", "ovisi_o": "visina građevine", "prag": broj(m["h"]), "jedinica_praga": "m",
                 "grane": [{"uvjet_doslovno": m["u1"], "vrijednost": broj(m["v1"])}, {"uvjet_doslovno": m["u2"], "vrijednost": broj(m["v2"])}],
                 "napomena": "pripada li građevina visine točno praga prvoj grani nije provjereno; konačna vrijednost ovisi o visini"}
        rz = [VISINSKI] + ([UPUCIVANJE] if m["u"] and re.search(r"pravilnik", m["u"], re.I) else [])
        out = [_z("udaljenostOdGraniceCestice", ">=", broj(m["v1"]), "m", "UVJETNO", kw, uvjeti=_lit(m["u1"], m["u"]), razlozi=list(rz), formula=izraz),
               _z("udaljenostOdGraniceCestice", ">=", broj(m["v2"]), "m", "UVJETNO", kw, uvjeti=_lit(m["u2"], m["u"]), razlozi=list(rz), formula=izraz)]
        return out, _lit(m["v1"], m["h"], m["v2"])

    # --- pomoćne građevine u alineji (uz građevine osnovne namjene …)
    m = re.match(r"(?P<u0>uz građevine osnovne namjene)\s*,\s*(?P<u1>unutar dopuštenih graničnih vrijednosti propisanih ovim Planom \(Kig i Kis\))\s*,\s*"
                 rf"mogu se graditi i (?P<p>pomoćne građevine \([^)]*\))\s+najviše kao (?P<e>dvoetažne|jednoetažne)(?:\s+(?P<eu>od kojih je [^,]+))?\s*,\s*"
                 rf"(?P<tl>tlocrtno manje od građevina osnovne namjene)\s*,\s*visine (?P<v>{NB})\s*{M_}{KRAJ}", t, re.I)
    if m:
        kp = dict(skupine=("pomocna",))
        rz = [NEVALIDIRANO]
        out = [_z("dopustenaGradnja", "dopusteno", m["p"], "opis", "UVJETNO", kp, vrijednost_vrsta="opis", uvjeti=[m["u0"], m["u1"]], razlozi=list(rz)),
               _z("etazeMax", "<=", 2 if m["e"].lower() == "dvoetažne" else 1, None, "UVJETNO" if m["eu"] else "OSNOVNO", kp, uvjeti=_lit(m["eu"]),
                  razlozi=list(rz)),
               _z("tlMax", "opis", m["tl"], "opis", "OSNOVNO", kp, vrijednost_vrsta="opis", razlozi=list(rz) + [IZVAN]),
               _z("visinaMax", "=", broj(m["v"]), "m", "OSNOVNO", kp, razlozi=list(rz) + [OPERATOR_NEIZRICIT,
                  R("REFERENTNA_VISINA_NEPOZNATA", "nije navedeno od koje do koje točke se mjeri visina")])]
        return out, _lit(m["v"])
    m = re.match(rf"građevine moraju biti udaljene (?P<v1>{NB})\s*{M_} od susjedne građevinske čestice (?P<u1>ukoliko imaju otvore)\s*,\s*"
                 rf"odnosno (?P<v2>{NB})\s*{M_} (?P<u2>kada nemaju otvore){KRAJ}", t, re.I)
    if m:
        kp = dict(skupine=("pomocna",)) if pomocna_alineja else kw
        rz = [OPERATOR_NEIZRICIT] + ([SUBJEKT_ALINEJE, NEVALIDIRANO] if pomocna_alineja else [])
        return [_z("udaljenostOdGraniceCestice", "=", broj(m["v1"]), "m", "UVJETNO", kp, uvjeti=[m["u1"]], razlozi=list(rz)),
                _z("udaljenostOdGraniceCestice", "=", broj(m["v2"]), "m", "UVJETNO", kp, uvjeti=[m["u2"]], razlozi=list(rz))], _lit(m["v1"], m["v2"])

    # --- zelenilo
    m = re.match(rf"potrebno je ozeleniti i hortikulturno urediti najmanje (?P<v>{NB})\s*% građevne čestice(?:\s+(?P<n>[a-zčćđšž\-]+) namjene)?{KRAJ}", t, re.I)
    if m:
        s2 = _skupina_namjene(m["n"]) or sk
        return [_z("zeleniloMin", ">=", broj(m["v"]), "%", "OSNOVNO", dict(skupine=s2), razlozi=[NEVALIDIRANO])], [m["v"]]

    # --- ograde, podzidi, kaskade (predmet nije građevina iz uvoda)
    pr = lambda p: R("PREDMET_" + p.upper(), f"predmet odredbe je {p}, ne građevina iz uvoda stavka")
    m = re.match(rf"(?P<iz>iznimno,\s*)?ograde (?P<u>između (?:građevinskih|građevnih) čestica) (?P<ne>ne )?mogu biti više od (?P<v>{NB})\s*(?P<j>{M_}|cm)"
                 rf"(?:\s*,\s*ali ne više od (?P<v2>{NB})\s*(?P<j2>{M_}|cm)\s*,\s*(?P<u2>kada .+?))?(?P<n>\s*\(mjereno [^)]+\))?{KRAJ}", t, re.I)
    if m and bool(m["iz"]) == bool(m["v2"]) != bool(m["ne"]):
        j = "cm" if (m["j2"] or m["j"]).lower() == "cm" else "m"
        if m["iz"]:
            return [_z("visinaOgradeMax", "<=", broj(m["v2"]), j, "IZNIMKA", kw, uvjeti=[m["u"], m["u2"]],
                       razlozi=[NEVALIDIRANO, IZVAN, pr("ograda")])], _lit(m["v"], m["v2"])
        return [_z("visinaOgradeMax", "<=", broj(m["v"]), j, "UVJETNO", kw, uvjeti=[m["u"]], napomena=(m["n"] or "").strip(" ()") or None,
                   razlozi=[NEVALIDIRANO, IZVAN, pr("ograda")])], [m["v"]]
    m = re.match(rf"(?P<s>ulične ograde) (?P<pr>u pravilu )?se izvode .*?visine najviše (?P<v>{NB})\s*(?P<j>cm|{M_})(?P<n>\s*\(mjereno [^)]+\))?{KRAJ}", t, re.I)
    if m:
        return [_z("visinaOgradeMax", "<=", broj(m["v"]), "cm" if m["j"].lower() == "cm" else "m", "UVJETNO", kw, uvjeti=[m["s"]],
                   napomena=(m["n"] or "").strip(" ()") or None, razlozi=[NEVALIDIRANO, IZVAN, pr("ograda")] + ([U_PRAVILU] if m["pr"] else []))], [m["v"]]
    m = re.match(rf"u visini od najviše (?P<v>{NB})\s*(?P<j>cm|{M_}) ograda se izvodi kao (?P<o>puna ili čvrsta ograda)", t, re.I)
    if m:
        return [_z("visinaPunogDijelaOgradeMax", "<=", broj(m["v"]), "cm" if m["j"].lower() == "cm" else "m", "OSNOVNO", kw, uvjeti=[m["o"]],
                   razlozi=[NEVALIDIRANO, IZVAN, pr("ograda")])], [m["v"]]
    m = re.match(rf"(?:.*?(?P<u>na kosim građevinskim česticama)\s*,\s*)?zabranjuje se gradnja podzida viših od (?P<v>{NB})\s*(?P<j>cm|{M_}){KRAJ}", t, re.I)
    if m:
        return [_z("visinaPodzidaMax", "<=", broj(m["v"]), "cm" if m["j"].lower() == "cm" else "m", "UVJETNO" if m["u"] else "OSNOVNO", kw,
                   uvjeti=_lit(m["u"]), napomena="»zabranjuje se gradnja podzida viših od N« zapisano kao ≤ N",
                   razlozi=[NEVALIDIRANO, IZVAN, pr("podzid")])], [m["v"]]
    m = re.match(rf"kaskade mogu biti najviše (?P<v>{NB})\s*(?P<j>cm|{M_}) visoke (?P<u>uz obavezan odmak kaskada \(horizontalne terase\) od (?P<o>{NB})\s*{M_}){KRAJ}", t, re.I)
    if m:
        j = "cm" if m["j"].lower() == "cm" else "m"
        return [_z("visinaKaskadeMax", "<=", broj(m["v"]), j, "UVJETNO", kw, uvjeti=[m["u"]], razlozi=[NEVALIDIRANO, IZVAN, pr("kaskada")]),
                _z("odmakKaskade", "=", broj(m["o"]), "m", "OSNOVNO", kw, razlozi=[NEVALIDIRANO, IZVAN, pr("kaskada"), OPERATOR_NEIZRICIT])], _lit(m["v"], m["o"])

    # --- krov: »kosa nagiba između 18o i 25o, ravna ili drugog oblika«; »razvedeno, koso, s nagibom … 18o-25o …«
    st = r"(?:°|o|º)"
    m = re.match(rf"krovna ploha građevina može se izvesti kao (?P<k>kosa) nagiba između (?P<a>\d+){st} i (?P<b>\d+){st}\s*,\s*(?P<ost>ravna ili drugog oblika){KRAJ}", t, re.I)
    if m:
        return [_z("oblikKrovista", "dopusteno", f"{m['k']}, {m['ost']}", "opis", "OSNOVNO", kw, vrijednost_vrsta="opis"),
                _z("nagibKrovaMin", ">=", broj(m["a"]), "°", "UVJETNO", kw, uvjeti=[m["k"]], interval="nagibKrova"),
                _z("nagibKrovaMax", "<=", broj(m["b"]), "°", "UVJETNO", kw, uvjeti=[m["k"]], interval="nagibKrova")], _lit(m["a"], m["b"])
    m = re.match(rf"krovište građevine treba biti (?P<o>[a-zčćđšž]+, [a-zčćđšž]+)\s*,\s*s nagibom krovnih ploha između (?P<a>\d+){st}\s*[-–]\s*(?P<b>\d+){st}"
                 rf"(?:\s*,\s*a dozvoljava se (?P<rk>djelomična izgradnja ravnog krova) u površini od (?P<rv>{NB})\s*% građevine)?"
                 rf"(?:\s*,\s*pokrov (?P<p>[a-zčćđšž ]+ ili [a-zčćđšž ]+))?{KRAJ}", t, re.I)
    if m:
        out = [_z("oblikKrovista", "=", m["o"], "opis", "OSNOVNO", kw, vrijednost_vrsta="opis"),
               _z("nagibKrovaMin", ">=", broj(m["a"]), "°", "OSNOVNO", kw, interval="nagibKrova"),
               _z("nagibKrovaMax", "<=", broj(m["b"]), "°", "OSNOVNO", kw, interval="nagibKrova")]
        if m["rv"]:
            out.append(_z("udioRavnogKrovaMax", "<=", broj(m["rv"]), "%", "OSNOVNO", kw, uvjeti=[m["rk"]], razlozi=[NEVALIDIRANO, IZVAN]))
        if m["p"]:
            out.append(_z("pokrovKosogKrova", "=", m["p"].strip(), "opis", "OSNOVNO", kw, vrijednost_vrsta="opis"))
        return out, _lit(m["a"], m["b"], m["rv"])

    # --- krovne kućice
    m = re.match(rf"dozvoljena je izgradnja (?P<d>krovnih prozora i krovnih kućica)\s*\((?P<u>pojedina kućica) može imati površinu od najviše (?P<v>{NB})\s*{M2_}\s*\)\s*[.;]?$", t, re.I)
    if m:
        return [_z("krovneKucice", "dopusteno", m["d"], "opis", "OSNOVNO", kw, vrijednost_vrsta="opis", razlozi=[NEVALIDIRANO, IZVAN]),
                _z("povrsinaKrovneKuciceMax", "<=", broj(m["v"]), "m²", "OSNOVNO", kw, uvjeti=[m["u"]], razlozi=[NEVALIDIRANO, IZVAN])], [m["v"]]

    # --- podzemne etaže: izgrađenost / zauzimanje
    m = re.match(rf"(?P<k>podzemne etaže) mogu imati (?P<v>{NB})\s*% izgrađenost građevne čestice{KRAJ}", t, re.I)
    if m:
        return [_z("izgradjenostPodzemnihMax", "<=", broj(m["v"]), "%", "OSNOVNO", kw, uvjeti=[m["k"]], razlozi=[NEVALIDIRANO, IZVAN])], [m["v"]]
    m = re.match(rf"(?P<u>ako se (?P<k>podzemne etaže) koriste kao garažni prostori) mogu zauzimati do (?P<v>{NB})\s*% površine gradivog dijela građevne čestice{KRAJ}", t, re.I)
    if m:
        return [_z("povrsinaPodzemnihMax", "<=", broj(m["v"]), "%", "UVJETNO", kw, uvjeti=[m["k"], m["u"]], razlozi=[NEVALIDIRANO, IZVAN])], [m["v"]]
    return None

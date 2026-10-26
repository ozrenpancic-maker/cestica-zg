#!/usr/bin/env python3
"""EKSPERIMENT v2.6: dodaci nad zamrznutim gramatikama v2.2 / v2.4 / v2.5 (ne mijenjaju se).

PRIPREMA TEKSTA (svaki znak → točno jedan znak; citat se vraća u izvorni oblik po položaju)
  - hrvatske tisućice ispred mjerne jedinice: »1.500 m²« → »01500 m²« (vrijednost 1500; decimalni zarez se ne dira;
    »1.5 m« i »1.50« nisu tisućice i ostaju);
  - indeksi iz Worda: »(k ig )« → »(kig)  «, »(k is )« → »(kis)  «.
ZONE
  - iz naslova članka (»Zone … (K1 1 i K1 2 )«, »Zona T1 1 - hotel«) i iz teksta (»unutar zone K2«).
VRSTA GRAĐEVINE IZ UVODA
  - analiziraju se SVI izrazi u uvodu, ne prvi pogodak. Za svaki pogodak bilježi se odnos prema pravilima:
      OBJEKT_GRADNJE  (»izgradnji / gradi se / grade se / smještaj / namijenjen(a) je … X«),
      POSTOJECA       (»na kojoj se nalazi postojeća X«, »postojeće X … moguće je zadržati«) – opis, ne subjekt pravila,
      SPOMEN          (sve ostalo).
    Vrsta pravila uzima se samo kad je točno jedna različita vrsta u odnosu OBJEKT_GRADNJE; inače nema vrste.
OBLICI ODREDBI (novo u v2.6)
  - subjekt izražen načinom gradnje: »Građevine koje će se graditi na slobodnostojeći način / kao dvojne …«;
  - dvije vrijednosti u jednoj rečenici bez miješanja: »broj etaža je 4, ali … najviše 2 nadzemne etaže«,
    »visina … najviše 10,0 m, a ukupna visina … najviše 13,0 m«, »broj nadzemnih etaža je 6 (…)«.
"""
import re
import gramatika_v22 as g2
import gramatika_v25 as g5
import vrste_gradevina as vg

VERZIJA = "gramatika-v2.6"
R, zapis = g2.R, g2.zapis
NB = r"\d+(?:,\d+)?"
broj = lambda s: float(s.replace(",", "."))
M_ = r"(?:m|metra|metara)\b"
KRAJ = r"\s*[.,;]?\s*$"

RX_TISUCICE = re.compile(r"(?<![\d.,])(\d{1,3})((?:\.\d{3})+)(?![\d,])(?=\s*(?:m\s*2|m²|m\s*3|m³|m\b|ha\b|%|stan|postelj|ležaj|parkirn|mjest))")
RX_INDEKS = re.compile(r"\(k\s+(ig|is)\s*\)", re.I)


def pripremi(tekst):
    """v2.5 priprema + tisućice + indeksi kig/kis; duljina se čuva."""
    t = g5.pripremi(tekst)

    def tis(m):
        cijeli = m.group(1) + m.group(2).replace(".", "")
        return "0" * (len(m.group(0)) - len(cijeli)) + cijeli
    t = RX_TISUCICE.sub(tis, t)
    t = RX_INDEKS.sub(lambda m: ("(k" + m.group(1) + ")").ljust(len(m.group(0))), t)
    assert len(t) == len(tekst)
    return t


# ---------------------------------------------------------------- zone
RX_KOD = r"[A-Z]{1,3}\d{0,2}(?:\s\d{1,2})?(?:-\d{1,2})?"
RX_ZONA_NASLOV = re.compile(rf"^(?:Zon[ae]|Površin[ae]|Područj[ae])\b(?P<t>[^()]*?)(?:\((?P<z>[^)]*)\)|\s(?P<z2>{RX_KOD})\b)", re.U)


def zone_naslova(naslov):
    """Planske oznake iz naslova članka. »(K1 1 i K1 2 )« → ['K1 1', 'K1 2']; »Zona T1 1 - hotel« → ['T1 1']."""
    if not naslov:
        return []
    m = RX_ZONA_NASLOV.match(naslov.strip())
    if not m:
        return []
    if m["z"]:
        dijelovi = re.split(r"\s*(?:,|\bi\b)\s*", m["z"].strip())
        return [d.strip() for d in dijelovi if re.fullmatch(RX_KOD, d.strip())]
    return [m["z2"].strip()]


# ---------------------------------------------------------------- vrsta iz svih izraza uvoda
OKIDAC_GRADNJE = r"(?:namijenjen\w*\s+(?:je|su)\s+(?:izgradnji|smještaju|gradnji)|izgradnj\w+|gradnj\w+|grad[ie]\s+se|se\s+(?:mogu\s+|može\s+)?grad(?:e|i|iti)\b|smještaj\w*|moguć\w*\s+je\s+smještaj)"
RX_POSTOJECA = re.compile(r"\b(?:nalazi\s+se|nalaze\s+se)\s+postojeć\w+\s+(?P<x>[^.;:]+)|\bpostojeć\w+\s+(?P<y>[^.;:(]+?)\s+(?:unutar\s+[^.;:]+?\s+)?moguće\s+je\s+zadržati", re.I)


def vrste_uvoda(uvod):
    """Svi izrazi vrste u uvodu s odnosom prema pravilima. Vraća popis {kodovi, izraz, od, odnos}."""
    out = []
    t = uvod or ""
    for m in re.finditer(rf"(?=\b(?P<ok>{OKIDAC_GRADNJE})\s+(?:i\s+uređenj\w+\s+)?(?:samo\s+)?(?:jedne\s+)?(?:nov\w+\s+|postojeć\w+\s+)?(?P<x>[^.;:]+))", t, re.I):
        x = m["x"]
        r = vg.prepoznaj(x, samo_pocetak=True)
        mp = g5.RX_PAR.match(x.strip())
        if mp:
            kod = []
            for pr in (mp["a"], mp["b"]):
                rr = vg.prepoznaj(f"{pr} {mp['n']}", samo_pocetak=True)
                if rr:
                    kod += [k for k in rr["kodovi"] if k not in kod]
            if kod:
                out.append({"kodovi": tuple(kod), "izraz": x[:mp.end()], "od": m.start("x"), "odnos": "OBJEKT_GRADNJE", "okidac": m["ok"]})
                continue
        if r:
            out.append({"kodovi": tuple(r["kodovi"]), "izraz": r["izraz"], "od": m.start("x"), "odnos": "OBJEKT_GRADNJE", "okidac": m["ok"]})
    for m in RX_POSTOJECA.finditer(t):
        x = m["x"] or m["y"]
        r = vg.prepoznaj(x, samo_pocetak=False)
        if r:
            out.append({"kodovi": tuple(r["kodovi"]), "izraz": r["izraz"], "od": m.start(), "odnos": "POSTOJECA", "okidac": None})
    return sorted(out, key=lambda z: z["od"])


def vrsta_uvoda(uvod):
    """(kodovi, dokaz, razlog): jedna različita vrsta u odnosu OBJEKT_GRADNJE → ta vrsta; više → None (VRSTA_VISEZNACNA)."""
    V = [v for v in vrste_uvoda(uvod) if v["odnos"] == "OBJEKT_GRADNJE"]
    razlicite = []
    for v in V:
        if v["kodovi"] not in razlicite:
            razlicite.append(v["kodovi"])
    if len(razlicite) == 1:
        return razlicite[0], V[0]["izraz"], None
    if len(razlicite) > 1:
        return None, "; ".join(v["izraz"] for v in V), "VRSTA_VISEZNACNA"
    return None, None, None


# ---------------------------------------------------------------- oblici odredbi v2.6
IZVAN = R("PARAMETAR_IZVAN_POPISA", "parametar nije u zatvorenom popisu uputa za označavanje; prihvaća se tek uz pregled")
VIS = R("REFERENTNA_VISINA_NEPOZNATA", "nije navedeno od koje do koje točke se mjeri visina")
NACIN = {"na slobodnostojeći način": "slob", "kao slobodnostojeće": "slob", "kao dvojne": "dvoj",
         "na dvojni način": "dvoj", "kao ugrađene": "ugr", "u nizu": "ugr"}  # kodovi oblika zamrznute gramatike v2.2
RX_NACIN = "|".join(re.escape(k) for k in NACIN)


def _z(par, op, v, j, vp, kw, **dod):
    d = dict(kw); d.update(dod)
    return zapis(par, op, v, j, vp, **d)


def _broj_etaza(s):
    return int(s) if s.isdigit() else g5.broj_rijecju(s)


def oblici(t, kont):
    """Vraća (zapisi, iskorišteni brojevi) ili None."""
    t = t.strip()
    sk = kont.get("skupine")

    # --- subjekt izražen načinom gradnje
    m = re.match(rf"građevine koje će se graditi (?P<n>{RX_NACIN}) moraju biti udaljene najmanje (?P<v1>{NB})\s*{M_} od granice građevne čestice"
                 rf"(?:\s*,\s*odnosno\s+(?P<v2>{NB})\s*{M_}\s+(?P<u>(?:ukoliko|ako|kada) .+?))?{KRAJ}", t, re.I)
    if m:
        kw = dict(skupine=sk, oblici=(NACIN[m["n"].lower()],))
        out = [_z("udaljenostOdGraniceCestice", ">=", broj(m["v1"]), "m", "OSNOVNO", kw)]
        if m["v2"]:
            out.append(_z("udaljenostOdGraniceCestice", ">=", broj(m["v2"]), "m", "UVJETNO", kw, uvjeti=[m["u"]],
                          napomena="»najmanje« iz prvog dijela rečenice vrijedi i za vrijednost iza »odnosno« (odluka suca v1.3/2: naslijeđeni minimum)"))
        return out, [x for x in (m["v1"], m["v2"]) if x]
    m = re.match(rf"građevine koje će se graditi (?P<n>{RX_NACIN}) (?P<p>jednom će se stranom prislanjati uz susjednu građevinu ili granicu građevne čestice)\s*,\s*"
                 rf"a (?P<s>na ostalim stranama) moraju biti udaljene najmanje (?P<v1>{NB})\s*{M_} od granice građevne čestice"
                 rf"(?:\s*,\s*odnosno\s+(?P<v2>{NB})\s*{M_}\s+(?P<u>(?:ukoliko|ako|kada) .+?))?{KRAJ}", t, re.I)
    if m:
        kw = dict(skupine=sk, oblici=(NACIN[m["n"].lower()],))
        out = [_z("nacinPrislanjanja", "=", "jednom stranom uz susjednu građevinu ili granicu građevne čestice", "opis", "OSNOVNO", kw, vrijednost_vrsta="opis",
                  razlozi=[R("ALTERNATIVA_U_VRIJEDNOSTI", "»uz susjednu građevinu ili granicu građevne čestice« – dvije mogućnosti")]),
               _z("udaljenostOdGraniceCestice", ">=", broj(m["v1"]), "m", "UVJETNO", kw, uvjeti=[m["s"]])]
        if m["v2"]:
            out.append(_z("udaljenostOdGraniceCestice", ">=", broj(m["v2"]), "m", "UVJETNO", kw, uvjeti=[m["s"], m["u"]],
                          napomena="»najmanje« iz prvog dijela rečenice vrijedi i za vrijednost iza »odnosno« (odluka suca v1.3/2: naslijeđeni minimum)"))
        return out, [x for x in (m["v1"], m["v2"]) if x]

    # --- broj etaža i broj nadzemnih etaža u jednoj rečenici
    m = re.match(r"najveći dopušteni broj etaža je (?P<a>\d+|[a-zčćšž]+(?:\s*\(\d+\))?)\s*,\s*ali dozvoljene su najviše (?P<b>\d+|[a-zčćšž]+(?:\s*\(\d+\))?) (?P<k>nadzemn\w+ etaž\w+)" + KRAJ, t, re.I)
    if m and _broj_etaza(m["a"]) is not None and _broj_etaza(m["b"]) is not None:
        kw = dict(skupine=sk)
        return [_z("etazeMax", "<=", _broj_etaza(m["a"]), None, "OSNOVNO", kw),
                _z("etazeNadzemneMax", "<=", _broj_etaza(m["b"]), None, "OSNOVNO", kw, razlozi=[IZVAN],
                   napomena="»ali dozvoljene su najviše N nadzemne etaže« – ograničenje nadzemnih etaža unutar ukupnog broja")], \
            re.findall(r"\d+", m["a"] + " " + m["b"])
    m = re.match(r"najveći dopušteni broj (?P<k>nadzemn\w+ etaž\w+) je (?P<a>\d+)(?:\s*\((?P<n>[^)]*)\))?" + KRAJ, t, re.I)
    if m:
        return [_z("etazeNadzemneMax", "<=", int(m["a"]), None, "OSNOVNO", dict(skupine=sk), razlozi=[IZVAN], napomena=m["n"])], [m["a"]]

    # --- visina i ukupna visina u jednoj rečenici
    m = re.match(rf"visina građevine iznosi najviše (?P<a>{NB})\s*{M_}\s*,\s*a ukupna visina građevine iznosi najviše (?P<b>{NB})\s*{M_}" + KRAJ, t, re.I)
    if m:
        kw = dict(skupine=sk)
        return [_z("visinaMax", "<=", broj(m["a"]), "m", "OSNOVNO", kw, razlozi=[VIS]),
                _z("ukupnaVisinaMax", "<=", broj(m["b"]), "m", "OSNOVNO", kw, razlozi=[VIS, IZVAN])], [m["a"], m["b"]]
    return None

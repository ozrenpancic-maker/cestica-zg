#!/usr/bin/env python3
"""EKSPERIMENT v2.2: lagana morfološka normalizacija hrvatskih imenica i pridjeva (bez vanjskih ovisnosti).

Pravila skidanja nastavaka (sklonidba imenica i pridjeva, jednina i množina) povezuju padežne oblike iste riječi:
»građevina / građevine / građevinu / građevinom / građevinama« → osnova »građevin«;
»stambena / stambenih / stambenoj / stambenim« → »stamben«. Oblici se NE nabrajaju ručno.

Ograničenja (namjerno, radi sigurnosti):
- ovo je heuristika osnove, ne lematizacija: ne rješava glasovne promjene (sibilarizacija ruka/ruci, nepostojano a);
- osnova kraća od 3 znaka se ne skraćuje dalje (»kat«, »kata« → »kat«; »kuća« → »kuć«);
- složenice sa spojnicom (»sportsko-rekreacijske«) obrađuju se po dijelovima;
- izvor pravila: opća gramatika sklonidbe (nastavci), NE pravopis (pravopis ne propisuje padeže).
Sučelje odgovara jezik_hr.MorfoloskiAnalizator; `ista_lema` vraća True/False samo kad su obje osnove pouzdane, inače None.
"""
import re
import jezik_hr

# nastavci od najduljeg prema najkraćem; uključuju imeničke i pridjevske padežne nastavke (jd. i mn.)
NASTAVCI = sorted({"ama", "ima", "oga", "ome", "omu", "ega", "emu", "ijeh", "ih", "im", "om", "em", "og", "eg", "oj", "ej",
                   "a", "e", "i", "o", "u"}, key=len, reverse=True)
MIN_OSNOVA = 3
NEPROMJENJIVE = {"i", "ili", "te", "niti", "na", "u", "uz", "od", "do", "za", "s", "sa", "kao", "se", "je", "su"}


def osnova(rijec):
    """Osnova jedne riječi (mala slova). Složenica sa spojnicom → osnove dijelova spojene spojnicom."""
    w = rijec.lower().strip(".,;:()»«\"'")
    if "-" in w:
        return "-".join(osnova(x) for x in w.split("-"))
    if w in NEPROMJENJIVE or not re.fullmatch(r"[a-zčćđšž]+", w):
        return w
    for n in NASTAVCI:
        if w.endswith(n) and len(w) - len(n) >= MIN_OSNOVA:
            return w[:-len(n)]
    return w


def osnove(izraz):
    return [osnova(w) for w in re.findall(r"[\wčćđšžČĆĐŠŽ-]+", izraz or "")]


def isti_izraz(a, b):
    """Jesu li dva višerječna izraza isti izraz u drugom padežu ili broju (riječ po riječ)."""
    return osnove(a) == osnove(b)


def nadji(izraz, tekst):
    """Pojavljivanja izraza (u bilo kojem padežu ili broju) u tekstu: popis (od, do, doslovni odlomak)."""
    cilj = osnove(izraz)
    rijeci = list(re.finditer(r"[\wčćđšžČĆĐŠŽ-]+", tekst or ""))
    out = []
    for i in range(len(rijeci) - len(cilj) + 1):
        if [osnova(rijeci[i + k].group()) for k in range(len(cilj))] == cilj:
            out.append((rijeci[i].start(), rijeci[i + len(cilj) - 1].end(), tekst[rijeci[i].start():rijeci[i + len(cilj) - 1].end()]))
    return out


class Osnove(jezik_hr.MorfoloskiAnalizator):
    izvor = "heuristika osnove (nastavci sklonidbe imenica i pridjeva); nije pravopis i nije potpuna lematizacija"

    def analiziraj(self, rijec):
        o = osnova(rijec)
        if len(o) < MIN_OSNOVA:
            return []
        return [{"lema": o, "vrsta": "osnova", "obiljezja": None}]

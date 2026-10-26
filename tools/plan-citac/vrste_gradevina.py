#!/usr/bin/env python3
"""EKSPERIMENT v2.2: prepoznavanje vrste građevine (taksonomija) uz morfologija_hr (svi padeži, jednina i množina).

Kategorije: stambena (obiteljska, višeobiteljska), stambeno-poslovna (kombinirana), poslovna, gospodarska
(proizvodna, poljoprivredna gospodarska), ugostiteljsko-turistička (hotel, kamp), sportsko-rekreacijska, javna i
društvena, pomoćna, infrastrukturna. Kodovi stamb/obit/visobit/poljoprivredna jednaki su kodovima v2.1.

Svaki naziv je zapisan JEDNOM, u nominativu jednine; ostali oblici prepoznaju se preko osnova. Kombinirana namjena
(»stambeno-poslovna«, »stambene i poslovne građevine«) vraća više kodova i oznaku `kombinirano`.
"""
import re
import morfologija_hr as mf

# (kod, kategorija, nazivi u nominativu jednine). Redoslijed: specifičnije prije općenitijeg.
VRSTE = [
    ("obit+visobit", "stambena", ["obiteljska/višeobiteljska kuća"]),
    ("visobit", "stambena", ["višeobiteljska kuća", "višeobiteljska građevina"]),
    ("obit", "stambena", ["obiteljska kuća", "obiteljska građevina"]),
    ("stambeno_poslovna", "stambeno-poslovna", ["stambeno-poslovna građevina"]),
    ("stamb", "stambena", ["stambena građevina", "građevina stambene namjene", "stambena zgrada"]),
    ("poljoprivredna", "gospodarska", ["poljoprivredna gospodarska građevina"]),
    ("gospodarska", "gospodarska", ["gospodarska građevina", "građevina gospodarske namjene", "proizvodna građevina"]),
    ("poslovna", "poslovna", ["poslovna građevina", "građevina poslovne namjene"]),
    ("hotel", "ugostiteljsko-turistička", ["hotel"]),
    ("ugostiteljsko_turisticka", "ugostiteljsko-turistička", ["ugostiteljsko-turistička građevina", "građevina ugostiteljsko-turističke namjene"]),
    ("sportsko_rekreacijska", "sportsko-rekreacijska", ["sportsko-rekreacijska građevina", "građevina sportsko-rekreacijske namjene"]),
    ("javna_drustvena", "javna i društvena", ["građevina javne i društvene namjene", "javna i društvena građevina"]),
    ("pomocna", "pomoćna", ["pomoćna građevina"]),
    ("infrastrukturna", "infrastrukturna", ["građevina komunalne infrastrukture", "infrastrukturna građevina"]),
]
KODOVI_IZ = {"obit+visobit": ("obit", "visobit")}


def prepoznaj(tekst, samo_pocetak=False):
    """Prva (najranija; kod jednakog položaja najdulja) vrsta građevine u tekstu → {kodovi, kategorija, izraz, od, do,
    kombinirano} ili None. samo_pocetak: izraz mora počinjati na početku teksta (bez uvodnih riječi)."""
    nalazi = []
    for kod, kat, nazivi in VRSTE:
        for n in nazivi:
            for od, do, lit in mf.nadji(n, tekst):
                nalazi.append((od, -(do - od), kod, kat, lit, do))
    # kombinirana namjena: »stambene i poslovne građevine«
    for m in re.finditer(r"\b(stamben\w*) i (poslovn\w*) građevin\w*", tekst or "", re.I):
        nalazi.append((m.start(), -(m.end() - m.start()), "stamb+poslovna", "kombinirana", m.group(), m.end()))
    if not nalazi:
        return None
    od, _, kod, kat, lit, do = min(nalazi)
    if samo_pocetak and tekst[:od].strip():
        return None
    kodovi = KODOVI_IZ.get(kod, tuple(kod.split("+")) if "+" in kod else (kod,))
    return {"kodovi": kodovi, "kategorija": kat, "izraz": lit, "od": od, "do": do,
            "kombinirano": len(kodovi) > 1 or kod == "stambeno_poslovna"}


def sve(tekst):
    out, poz = [], 0
    while True:
        r = prepoznaj(tekst[poz:])
        if not r:
            return out
        r = dict(r, od=r["od"] + poz, do=r["do"] + poz)
        out.append(r); poz = r["do"]

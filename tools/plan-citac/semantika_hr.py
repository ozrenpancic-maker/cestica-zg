#!/usr/bin/env python3
"""EKSPERIMENT v2.1: semantički izrazi propisa, odvojeni od pravopisne normalizacije (jezik_hr.py).

Ovo je TUMAČENJE, ne pravopis. Za svaki izraz bilježi se: doslovni citat i položaj, kategorija, što znači za pravilo
i treba li ljudski pregled. Izrazi s posebnom obradom:

- »ne propisuje se« / »se ne propisuje«: NIJE_PROPISANO (vrijednost nije zadana ovom odredbom; ≠ NEOGRANIČENO);
- »samo kao«: dopuštenje navedenog oblika; zabrana ostalih je izvedena i ide u pregled;
- »najmanje«, »najmanja/i«, »ne manje od«: donja granica (>=);
- »najviše«, »najveća/i«, »ne više od«: gornja granica (<=);
- »iznimno«: iznimka od osnovnog pravila; traži uvjet i povezano osnovno pravilo;
- dodatno: »može iznositi i« (olakšica u odnosu na prethodnu odredbu), »nije ograničen« (NEOGRANIČENO, samo kad tako piše).

`provjeri_pravilo()` uspoređuje operator i vrstu pravila iz gramatike s izrazima u izvornom citatu i vraća proturječja.
"""
import re

IZRAZI = [
    ("NE_PROPISUJE_SE", r"\b(?:se ne propisuje|ne propisuje se|nije propisan\w*)\b", "NIJE_PROPISANO",
     "odredba ne zadaje vrijednost; to nije isto što i NEOGRANIČENO (ograničenje može proizlaziti iz drugih odredbi)", False),
    ("NIJE_OGRANICENO", r"\b(?:nije ograničen\w*|bez ograničenja)\b", "NEOGRANIČENO",
     "izričito neograničeno; zaključuje se samo kad tako piše", True),
    ("SAMO_KAO", r"\bsamo kao\b", "DOPUSTENJE_I_IZVEDENA_ZABRANA",
     "dopušten je samo navedeni oblik; zabrana ostalih oblika je izvedena i traži pregled (ostali oblici nisu nabrojeni)", True),
    ("NE_MANJE_OD", r"\bne manje od\b", ">=", "donja granica", False),
    ("NE_VISE_OD", r"\bne više od\b", "<=", "gornja granica", False),
    ("NAJMANJE", r"\bnajmanj(?:e|a|i|eg|u|om)\b", ">=", "donja granica (najmanja dopuštena vrijednost)", False),
    ("NAJVISE", r"\bnajviše\b|\bnajveć(?:a|i|e|eg|u|om)\b", "<=", "gornja granica (najveća dopuštena vrijednost)", False),
    ("IZNIMNO", r"\biznimno\b", "IZNIMKA", "iznimka od osnovnog pravila; traži uvjet primjene i osnovno pravilo", False),
    ("MOZE_IZNOSITI_I", r"\bmože iznositi i\b", "OLAKSICA", "olakšica u odnosu na prethodnu odredbu; odnos prema njoj treba utvrditi", True),
]


def izrazi(tekst):
    out = []
    for kod, rx, znacenje, obj, pregled in IZRAZI:
        for m in re.finditer(rx, tekst or "", re.I):
            out.append({"kod": kod, "citat": m.group(), "od": m.start(), "do": m.end(), "znacenje": znacenje,
                        "objasnjenje": obj, "trazi_pregled": pregled, "vrsta": "SEMANTICKO_TUMACENJE"})
    return sorted(out, key=lambda x: x["od"])


def provjeri_pravilo(p):
    """Proturječja između pravila (operator, vrsta pravila) i izraza u njegovu izvornom citatu. Vraća [(kod, tekst)]."""
    S = izrazi(p.get("izvorni_citat"))
    kodovi = {s["kod"] for s in S}
    op, vp = p.get("operator"), p.get("vrsta_pravila")
    out = []
    if op == "nije_propisano" and "NE_PROPISUJE_SE" not in kodovi:
        out.append(("SEMANTIKA_PROTURJECNA", "operator NIJE_PROPISANO bez izraza »ne propisuje se« u citatu"))
    if "NE_PROPISUJE_SE" in kodovi and op not in ("nije_propisano", None):
        out.append(("SEMANTIKA_PROTURJECNA", "citat sadrži »ne propisuje se«, a pravilo ima operator " + str(op)))
    if op == "zabranjeno" and "SAMO_KAO" not in kodovi:
        out.append(("SEMANTIKA_PROTURJECNA", "zabrana bez izraza »samo kao« u citatu"))
    if op in (">=", "<=") and not p.get("interval"):
        granice = {s["znacenje"] for s in S if s["znacenje"] in (">=", "<=")}
        if granice and op not in granice:
            out.append(("SEMANTIKA_PROTURJECNA", f"operator {op}, a citat izriče samo {', '.join(sorted(granice))}"))
    if "IZNIMNO" in kodovi and vp not in ("IZNIMKA", "ALTERNATIVA", "NEGATIVNO"):
        out.append(("SEMANTIKA_PROTURJECNA", "citat počinje ili sadrži »iznimno«, a pravilo nije označeno kao iznimka"))
    return out

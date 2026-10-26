#!/usr/bin/env python3
"""EKSPERIMENT v2.3: strukturiranje = zamrznuta v2.2 + dvije ciljane korekcije. Kod v1, v2.1 i v2.2 se ne mijenja.

1. Prijenos konteksta primjene (kontekst_primjene / dodatni_uvjeti).
   Uvod stavka (ili bloka) do prve dvotočke može navesti uz koju se građevinu gradi:
   »… uz građevine društvene i sportsko-rekreacijske namjene uz uvjet da:«, »Na građevnoj čestici uz obiteljsku kuću …«,
   »… uz građevinu osnovne namjene uz sljedeće granične uvjete:«.
   Taj doslovni odlomak postaje `kontekst_primjene` svakog pravila iz tog stavka (bloka) i dodaje se na početak `uvjeti`;
   posebni uvjeti alineje ostaju u `dodatni_uvjeti`. Vrsta pravila se ne mijenja (kontekst određuje na što se
   pravilo odnosi, a ne čini ga uvjetnim). Kontekst se nikad ne izmišlja: bilježi se samo doslovni odlomak
   uvoda, uz `izvor_konteksta` (članak, stavak/blok, citat uvoda).
2. »samo kao« u načinu gradnje: »X mogu se graditi samo kao samostojeće građevine« znači da je to jedini dopušteni oblik,
   pa je operator prvog pravila »=« (obvezni oblik), a ne »dopušteno«. Izvedena zabrana ostalih oblika ostaje kao u v2.2.
Sve ostalo (statusi, razlozi pregleda, primjenjivost na lokaciju) je iz v2.2. Ništa nije pravno potvrđeno.
"""
import copy, hashlib, json, re
from pathlib import Path
import gramatika as g1
import gramatika_v22 as g2
import strukturiraj_v22 as s22

VERZIJA = "gramatika-v2.3"
RX_KONTEKST = re.compile(
    r"(?:na građevnoj čestici\s+)?uz\s+(?:obiteljsk[ue]|višeobiteljsk[ue])\s+kuć[eu]"
    r"|uz\s+građevin[eu]\s+(?:[a-zčćđšž\-]+\s+(?:i\s+)?){1,4}?namjene", re.I)


def _uvod(tekst):
    t = tekst.split(":")[0] if ":" in tekst else ""
    return t


def _konteksti(tekst):
    """Doslovni odlomci konteksta iz uvoda (do prve dvotočke); [] ako uvoda nema."""
    u = _uvod(tekst)
    return [m.group().strip() for m in RX_KONTEKST.finditer(u)], u


def _uvodi_clanka(c):
    """{(stavak, blok): (konteksti, uvod)} za stavke i blokove članka."""
    out = {}
    S = g1.stavci(c["tekst"])
    if not (len(S) == 1 and S[0][0] is None):
        for sb, st in S:
            out[(sb, None)] = _konteksti(st)
    else:
        for bn, btx in g2.blokovi(c["tekst"]):
            out[(None, bn)] = _konteksti(btx)
    return out


def _dodaj_kontekst(p, kont, uvod, br):
    p["dodatni_uvjeti"] = list(p.get("uvjeti") or [])
    p["kontekst_primjene"] = list(kont)
    if kont:
        p["izvor_konteksta"] = {"clanak": br, "stavak": p["stavak"], "blok": p.get("blok"), "uvod": uvod.strip()}
        nove = [k for k in kont if not any(k.lower() in u.lower() for u in p["dodatni_uvjeti"])]
        p["uvjeti"] = nove + p["dodatni_uvjeti"]
        p["uvjet"] = "; ".join(p["uvjeti"]) or None
        p["uvjet_logika"] = g2.logika_uvjeta(p["uvjeti"])
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)
    else:
        p["izvor_konteksta"] = None


def _samo_kao(p):
    if p["parametar"] == "nacinGradnje" and p["operator"] == "dopusteno" and re.search(r"\bmogu se graditi samo kao\b", p["izvorni_citat"], re.I):
        p["operator"] = "="
        p["napomena"] = ((p.get("napomena") or "") + "; " if p.get("napomena") else "") + "»samo kao«: jedini dopušteni oblik (v2.3)"


def strukturiraj(dokazi, clanci, plan):
    r = s22.strukturiraj(dokazi, clanci, plan)
    r = copy.deepcopy(r)
    r["shema"] = "plan-citac-pravila/2.3"; r["gramatika_v23"] = VERZIJA
    for k, cl in r["clanci"].items():
        if cl.get("gramatika") != g2.VERZIJA:
            continue  # obrasci v1 (UPU 2) ostaju netaknuti
        c = dokazi["clanci"][k]
        U = _uvodi_clanka(c)
        for p in cl.get("pravila", []):
            kont, uvod = U.get((p["stavak"], p.get("blok") if p["stavak"] is None else None), ([], ""))
            _dodaj_kontekst(p, kont, uvod, cl["clanak"])
            _samo_kao(p)
            p["obrazac_v23"] = VERZIJA
    return r


zapisi_json = s22.zapisi_json

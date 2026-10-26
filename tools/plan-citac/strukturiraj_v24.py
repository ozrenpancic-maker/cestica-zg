#!/usr/bin/env python3
"""EKSPERIMENT v2.4: v2.2 (zamrznuta) → novi oblici odredbi o pomoćnim građevinama (gramatika_v24) → prijenos konteksta
i »samo kao« iz v2.3 (zamrznuta). Kod v1, v2.1, v2.2 i v2.3 se ne mijenja.

Rečenice koje v2.2 odbija (`nepokriveno`) ili ostavlja bez pravila (`bez_broja`) ponovno se čitaju oblicima v2.4.
Ako oblik odgovara, pravilo zapisuje zamrznuti gramatika_v22._zapisi (citat, uvjeti, prostorni obuhvat, razlozi, status),
a rečenica se uklanja s popisa odbijenih. Zatim svako pravilo (staro i novo) dobiva kontekst primjene kao u v2.3.
Pravila v2.2 se ne mijenjaju osim polja konteksta iz v2.3. Ništa nije pravno potvrđeno.
"""
import copy, re
from collections import Counter
import gramatika as g1
import gramatika_v22 as g2
import gramatika_v24 as g4
import strukturiraj_v22 as s22
import strukturiraj_v23 as s23
from citac import brojevi

VERZIJA = g4.VERZIJA


def _blok_od(c, dokaz):
    for bn, btx in g2.blokovi(c["tekst"]):
        if dokaz in btx:
            return bn
    return None


def _v1_vrste(c):
    S = g1.stavci(c["tekst"])
    uvod1 = S[0][1].split(":")[0] if S else ""
    skup_v1 = g1._skupina(uvod1)
    oblici_v1 = sorted({o for _, st in S for ob, rx in g1.OBLICI for _ in re.finditer(rx, st) for o in ob})
    return ([f"{skup_v1}-{o}" for o in oblici_v1] if skup_v1 and oblici_v1 else None), skup_v1


def _kontekst_dijela(cl, c, sb, blok):
    """Vrsta građevine i »gradjevina« dijela članka: najčešća među postojećim pravilima tog stavka/bloka, inače iz uvoda."""
    P = [p for p in cl.get("pravila", []) if p["stavak"] == sb and (sb is not None or p.get("blok") == blok)]
    if P:
        sk = Counter(tuple(p["vrsta_gradevine"]["skupine"]) for p in P).most_common(1)[0][0]
        gr = Counter(p["gradjevina"] for p in P).most_common(1)[0][0]
        return {"skupine": sk or None, "gradjevina": gr}
    if sb is not None:
        st = dict(g1.stavci(c["tekst"])).get(sb, "")
        uv = st.split(":")[0]
        return {"skupine": g2.skupina_strogo(uv), "gradjevina": g1._gradjevina(uv)}
    return {"skupine": None, "gradjevina": None}


def _v24_clanak(cl, c, plan):
    br = cl["clanak"]
    vrste_v1, skup_v1 = _v1_vrste(c)
    kand = [("nepokriveno", x) for x in cl.get("nepokriveno", [])] + [("bez_broja", x) for x in cl.get("bez_broja", [])]
    for _, x in kand:
        x["_blok"] = x.get("blok") if x.get("stavak") is not None else _blok_od(c, x["dokaz"])
    # prva rečenica svake alineje (za »iznimno, unutar …« koje vrijedi za cijelu alineju)
    prve = {}
    for _, x in kand:
        if x.get("recenica") == 1:
            prve[(x.get("stavak"), x["_blok"], x.get("tocka"), x.get("alineja"))] = x["dokaz"]
    for p in cl.get("pravila", []):
        if p.get("recenica") == 1:
            prve.setdefault((p["stavak"], p.get("blok"), p["tocka"], p["alineja"]), p["izvorni_citat"])
    sirovi, uzeti = [], []
    for izvor, x in kand:
        sb, blok = x.get("stavak"), x["_blok"]
        kont = _kontekst_dijela(cl, c, sb, blok)
        res = g4.oblici(x["dokaz"], dict(kont))
        if not res:
            continue
        zap, isk = res
        prva = prve.get((sb, blok, x.get("tocka"), x.get("alineja"))) if x.get("alineja") else None
        izn = g4._iznimka(prva)[0] if prva else None
        if izn:
            g4.primijeni_iznimku(zap, izn)
        lits = [b["literal"] for b in brojevi(g2.normaliziraj(x["dokaz"]))]
        ostatak = [l for l in lits if l not in isk and not re.fullmatch(r"2", l)]
        for z in zap:
            if not z.get("skupine"):
                z["skupine"] = kont.get("skupine")
            z["razlozi"] = list(z["razlozi"])
            gr = g2._gradjevina_iz(z["skupine"], kont.get("gradjevina"))
            sirovi.append((sb, x.get("tocka"), x.get("alineja"), x.get("recenica"), x["dokaz"], x["dokaz"], gr, z,
                           ostatak if z is zap[0] else [], [], {"obuhvat": [], "iznimka": None, "blok": blok}))
        uzeti.append((izvor, x))
    if not sirovi:
        return 0
    tmp = {"pravila": []}
    g2._zapisi(tmp, br, c, plan, sirovi, vrste_v1, skup_v1)
    for p in tmp["pravila"]:
        p["id"] = "v24." + p["id"]
        p["obrazac"] = VERZIJA
        if p["status"] == "PREGLED" and not p["razlog_kod"]:
            p["status"] = "PRIJEDLOG"
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)
    cl["pravila"] = cl.get("pravila", []) + tmp["pravila"]
    for izvor, x in uzeti:
        cl[izvor] = [y for y in cl[izvor] if y is not x]
    for _, x in kand:
        x.pop("_blok", None)
    cl["gramatika_v24"] = {"novih_pravila": len(tmp["pravila"]), "preuzetih_recenica": len(uzeti)}
    return len(tmp["pravila"])


def strukturiraj(dokazi, clanci, plan):
    r = copy.deepcopy(s22.strukturiraj(dokazi, clanci, plan))
    r["shema"] = "plan-citac-pravila/2.4"; r["gramatika_v23"] = s23.VERZIJA; r["gramatika_v24"] = VERZIJA
    for k, cl in r["clanci"].items():
        if cl.get("gramatika") != g2.VERZIJA:
            continue  # obrasci v1 (UPU 2) ostaju netaknuti
        c = dokazi["clanci"][k]
        _v24_clanak(cl, c, plan)
        U = s23._uvodi_clanka(c)
        for p in cl.get("pravila", []):
            kont, uvod = U.get((p["stavak"], p.get("blok") if p["stavak"] is None else None), ([], ""))
            s23._dodaj_kontekst(p, kont, uvod, cl["clanak"])
            s23._samo_kao(p)
            p["obrazac_v23"] = s23.VERZIJA
    sv = [p for c in r["clanci"].values() for p in c.get("pravila", [])]
    r["sazetak"] = {"pravila": len(sv), "prijedlog": sum(p["status"] == "PRIJEDLOG" for p in sv),
                    "pregled": sum(p["status"] == "PREGLED" for p in sv),
                    "odbijeno": sum(len(c.get("nepokriveno", [])) for c in r["clanci"].values())}
    return r


zapisi_json = s22.zapisi_json

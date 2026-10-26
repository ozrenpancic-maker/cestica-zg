#!/usr/bin/env python3
"""EKSPERIMENT v2.5: struktura dokumenta, kontekst i novi oblici odredbi nad zamrznutim slojevima.
Kod v1, v2.1, v2.2, v2.3 i v2.4 se ne mijenja.

Redoslijed:
 1. priprema teksta iste duljine (gramatika_v25.pripremi): alineja »•«, kratice »ul.«, »čl.«, »br.«, »vis.« …;
 2. članak: zamrznuti put v2.2 (strukturiraj_v22.strukturiraj_clanak); ako je odbijen zbog nepoznate vrste
    (SKUPINA_NEPOZNATA), ponovno s vrstom iz cijele uvodne rečenice (gramatika_v25.skupina_uvoda);
 3. dodatni oblici odredbi: v2.4 (pomoćne građevine), zatim v2.5 (gramatika_v25.oblici, ako postoje);
 4. kontekst: v2.3 (uz koju se građevinu gradi, »samo kao«) i v2.5 (zona, nova gradnja, iznimka iz uvoda stavka);
 5. zaštita: pravilo kojem nedostaje obvezni kontekst uvoda (vrsta, zona, nova gradnja) ide na PREGLED;
 6. svi citati i uvjeti vraćaju se u izvorni oblik (isti položaj u tekstu).
Ništa nije pravno potvrđeno.
"""
import copy, re
from collections import Counter
import gramatika as g1
import gramatika_v22 as g2
import gramatika_v24 as g4
import gramatika_v25 as g5
import strukturiraj_v22 as s22
import strukturiraj_v23 as s23
import strukturiraj_v24 as s24
from citac import brojevi

VERZIJA = g5.VERZIJA


RX_PODBLOK = re.compile(r"(?:^|\s+)(?P<n>\d{1,2}\.\d{1,2}\.(?:\d{1,2}\.)?)\s+(?P<h>[A-ZČĆĐŠŽ][^:.;]{2,120}?):?\s*$")


def _put_stavci25(rez, S, sk_cl, sirovi):
    """Kao gramatika_v22._put_stavci, uz dvije razlike za članke koje v2.2 odbija:
    (1) alineje se odvajaju i kad počinju velikim slovom (»- Građevine«, »• Građevine«) već u uvodu stavka;
    (2) brojčani podnaslov na kraju alineje (»1.2. Uređenje građevne čestice:«) odvaja se i postaje blok sljedećih alineja."""
    for sb, st in S:
        uvod, T = g1.tocke(st)
        blokovi_al = []
        if T:
            jedinice = [(t["slovo"], None, t["tekst"], None) for t in T]
        else:
            d0 = g2.RX_ALINEJA.split(st)
            u2, al = d0[0], d0[1:]
            if al:
                blok, jedinice = None, []
                mh = RX_PODBLOK.search(u2)
                if mh:
                    blok = mh["n"].rstrip("."); u2 = u2[:mh.start()].strip()
                jedinice.append((None, None, u2, None))
                for ai, a in enumerate(al, 1):
                    mh = RX_PODBLOK.search(a)
                    novi = None
                    if mh:
                        novi = mh["n"].rstrip("."); a = a[:mh.start()].strip()
                    jedinice.append(("-", ai, a, blok))
                    if novi:
                        blok = novi
                uvod = u2
            else:
                uvod = ""; jedinice = [(None, None, st, None)]
        gr = g1._gradjevina(uvod or st)
        sk_st = g2.skupina_strogo(uvod) if uvod else None
        if gr == "poljoprivredna":
            sk_st = ("poljoprivredna",)
        kont_st = {"skupine": sk_st or sk_cl, "gradjevina": gr}
        for slovo, ai, tx, blok in jedinice:
            g2._jedinica_rec(rez, sirovi, sb, slovo, ai, tx, dict(kont_st), {"blok": blok} if blok else {}, T)


def clanak_uvod(br, c, plan):
    """Kopija toka gramatika_v22.clanak; razlika je samo u vrsti iz uvoda (skupina_strogo ili skupina_uvoda)."""
    rez = {"clanak": br, "vrste": None, "pravila": [], "upucivanja": [], "nepokriveno": [], "bez_broja": [], "pregled": [], "kontekst": [],
           "gramatika": g2.VERZIJA, "struktura_v25": "vrsta iz cijele uvodne rečenice"}
    S = g1.stavci(c["tekst"])
    uvod1 = S[0][1].split(":")[0] if S else ""
    sk_cl = g2.skupina_strogo(uvod1) or g5.skupina_uvoda(uvod1)
    skup_v1 = g1._skupina(uvod1)
    oblici_v1 = sorted({o for _, st in S for ob, rx in g1.OBLICI for _ in re.finditer(rx, st) for o in ob})
    vrste_v1 = [f"{skup_v1}-{o}" for o in oblici_v1] if skup_v1 and oblici_v1 else None
    sirovi = []
    ima_stavke = not (len(S) == 1 and S[0][0] is None)
    if ima_stavke and (sk_cl or any(g2.skupina_strogo(st.split(":")[0]) or g5.skupina_uvoda(st.split(":")[0]) for _, st in S)):
        if not sk_cl:
            sk_cl = next(g5.skupina_uvoda(st.split(":")[0]) for _, st in S if g5.skupina_uvoda(st.split(":")[0]))
        _put_stavci25(rez, S, sk_cl, sirovi)
    if not ima_stavke:
        g2._put_blokovi(rez, c["tekst"], sirovi)
    if not sirovi and not rez["nepokriveno"]:
        rez["pregled"].append({"razlog": "vrsta građevine iz uvoda članka nije prepoznata (ni u cijeloj uvodnoj rečenici)", "razlog_kod": "SKUPINA_NEPOZNATA"})
        return rez
    g2._zapisi(rez, br, c, plan, sirovi, vrste_v1, skup_v1)
    brs = [sb for sb, _ in S if sb is not None]
    if brs and brs != list(range(1, len(brs) + 1)):
        rez["pregled"].append({"razlog_kod": "STRUKTURA_CLANKA_NEPOUZDANA", "razlog": f"brojevi stavaka nisu redom 1…n: {brs[:12]}"})
        for p in rez["pravila"]:
            p["razlog_kod"].append("STRUKTURA_CLANKA_NEPOUZDANA"); p["razlozi"].append("brojevi stavaka u članku nisu redom")
            p["status"] = "PREGLED"; p["za_izracun"] = False
    g2._poveznice(rez["pravila"])
    vrste = vrste_v1 if vrste_v1 is not None else sorted({x for p in rez["pravila"] for x in p["vrste"]})
    rez["vrste"] = vrste or None
    for p in rez["pravila"]:
        if p["status"] == "PREGLED" and not p["razlog_kod"]:
            p["status"] = "PRIJEDLOG"
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)
    return rez


def strukturiraj_clanak(br, c, plan):
    r = s22.strukturiraj_clanak(br, c, plan)
    if r.get("pravila") or r.get("vrste"):
        return r
    if not any(x.get("razlog_kod") == "SKUPINA_NEPOZNATA" for x in r.get("pregled", [])):
        return r
    r5 = clanak_uvod(br, c, plan)
    return r5 if (r5["pravila"] or r5["nepokriveno"]) else r


def dodatni_oblici(cl, c, plan, oblici, prefiks, verzija):
    """Isto kao strukturiraj_v24._v24_clanak, s danom funkcijom oblika (v2.4 ili v2.5)."""
    br = cl["clanak"]
    vrste_v1, skup_v1 = s24._v1_vrste(c)
    kand = [("nepokriveno", x) for x in cl.get("nepokriveno", [])] + [("bez_broja", x) for x in cl.get("bez_broja", [])]
    for _, x in kand:
        x["_blok"] = x.get("blok") if x.get("stavak") is not None else s24._blok_od(c, x["dokaz"])
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
        kont = s24._kontekst_dijela(cl, c, sb, blok)
        res = oblici(x["dokaz"], dict(kont))
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
    for _, x in kand:
        x.pop("_blok", None)
    if not sirovi:
        return 0
    tmp = {"pravila": []}
    g2._zapisi(tmp, br, c, plan, sirovi, vrste_v1, skup_v1)
    for p in tmp["pravila"]:
        p["id"] = prefiks + p["id"]
        p["obrazac"] = verzija
        if p["status"] == "PREGLED" and not p["razlog_kod"]:
            p["status"] = "PRIJEDLOG"
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)
    cl["pravila"] = cl.get("pravila", []) + tmp["pravila"]
    for izvor, x in uzeti:
        cl[izvor] = [y for y in cl[izvor] if y is not x]
    return len(tmp["pravila"])


def _pregled(p, kod, tekst):
    if kod not in p["razlog_kod"]:
        p["razlog_kod"].append(kod); p["razlozi"].append(tekst)
    p["status"] = "PREGLED"; p["za_izracun"] = False


def kontekst_v25(cl, c):
    """Zona, nova gradnja i iznimka iz uvoda stavka → svako pravilo stavka; zaštita od izgubljenog konteksta."""
    S = g1.stavci(c["tekst"])
    K, prev = {}, {}
    for sb, st in S:
        k = g5.kontekst_uvoda(st.split(":")[0] if ":" in st else st.split(". ")[0], prev)
        K[sb] = k; prev[sb] = k
    art = K.get(S[0][0]) if S else None
    for p in cl.get("pravila", []):
        k = K.get(p["stavak"]) or {"zone": [], "nova": None, "iznimka": None, "dokaz_zone": None}
        zone = k["zone"] or ((art or {}).get("zone") if p["stavak"] not in (None, S[0][0]) else [])
        p["zone_konteksta"] = list(zone or [])
        if zone:
            postoji = {o.get("oznaka") for o in p["prostorni_obuhvat"]}
            nove = [z for z in zone if z not in postoji]
            if nove:
                p["prostorni_obuhvat"] = [o for o in p["prostorni_obuhvat"] if o["vrsta"] != "NIJE_NAVEDEN_U_ODREDBI"] + \
                    [{"vrsta": "ZONA_PLANA", "oznaka": z, "dokaz": k["dokaz_zone"] or (art or {}).get("dokaz_zone"), "utvrdjeno_na_lokaciji": False,
                      "izvor": "uvod stavka (v2.5)"} for z in nove]
        nova = k["nova"] or ((art or {}).get("nova") if p["stavak"] == (S[0][0] if S else None) else None)
        if nova and p["vrsta_gradevine"].get("stanje") is None:
            p["vrsta_gradevine"]["stanje"] = "nova"
            p["kontekst_nova_gradnja"] = nova
        if k["iznimka"]:
            mz = re.match(r"(?P<u>površin\w+\s+označen\w+\s+(?:planskom\s+)?oznakom\s+[A-Z][A-Z0-9\-]*)", k["iznimka"], re.I)
            u = mz["u"] if mz else None
            if u and u not in p["uvjeti"]:
                p["uvjeti"] = [u] + p["uvjeti"]; p["uvjet"] = "; ".join(p["uvjeti"])
                p["dodatni_uvjeti"] = [u] + list(p.get("dodatni_uvjeti") or [])
            if p["vrsta_pravila"] in ("OSNOVNO", "UVJETNO", "ALTERNATIVA"):
                p["vrsta_pravila"] = "IZNIMKA"
            if not u:
                _pregled(p, "IZNIMKA_BEZ_UVJETA", "stavak počinje s »Iznimno«, ali uvjet iznimke nije doslovno izdvojen")
        # zaštita (v2.5 t. 7): obvezni kontekst uvoda mora biti u pravilu
        if not p["vrsta_gradevine"].get("skupine"):
            _pregled(p, "KONTEKST_IZGUBLJEN", "vrsta građevine nije određena ni u odredbi ni u uvodu")
        if nova and p["vrsta_gradevine"].get("stanje") != "nova" and p["vrsta_gradevine"].get("stanje") != "postojeca":
            _pregled(p, "KONTEKST_IZGUBLJEN", "uvod stavka propisuje novu gradnju, a pravilo je nema")
        if zone and not any(o.get("oznaka") in zone for o in p["prostorni_obuhvat"]):
            _pregled(p, "KONTEKST_IZGUBLJEN", "uvod stavka određuje zonu, a pravilo je nema u prostornom obuhvatu")
        p["obrazlozenje_statusa"] = g2._obrazlozenje(p)


def strukturiraj(dokazi, clanci, plan, v25_oblici=True):
    O = {k: c["tekst"] for k, c in dokazi["clanci"].items()}
    dT = dict(dokazi, clanci={k: dict(c, tekst=g5.pripremi(c["tekst"])) for k, c in dokazi["clanci"].items()})
    out = {"shema": "plan-citac-pravila/2.5", "gramatika": g2.VERZIJA, "gramatika_v25": VERZIJA, "izvor": dokazi.get("izvor"),
           "sha256_izvora": dokazi.get("sha256"), "plan": plan, "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False,
           "statusi": {"PRIJEDLOG": "ACCEPTED – automatski prihvaćen prijedlog (nije pravna potvrda)", "PREGLED": "REVIEW", "ODBIJENO": "REJECTED"}}
    for k, c in dT["clanci"].items():
        br = c["broj"]
        if clanci and br not in clanci:
            continue
        out["clanci"][k] = strukturiraj_clanak(br, c, plan)
    g2.provjeri_sukobe(out["clanci"])
    for k, cl in out["clanci"].items():
        if cl.get("gramatika") != g2.VERZIJA:
            continue  # obrasci v1 (UPU 2) ostaju netaknuti
        c = dT["clanci"][k]
        dodatni_oblici(cl, c, plan, g4.oblici, "v24.", g4.VERZIJA)
        if v25_oblici and hasattr(g5, "oblici"):
            dodatni_oblici(cl, c, plan, g5.oblici, "v25.", VERZIJA)
        U = s23._uvodi_clanka(c)
        for p in cl.get("pravila", []):
            kont, uvod = U.get((p["stavak"], p.get("blok") if p["stavak"] is None else None), ([], ""))
            s23._dodaj_kontekst(p, kont, uvod, cl["clanak"])
            s23._samo_kao(p)
        kontekst_v25(cl, c)
    for k in list(out["clanci"]):
        out["clanci"][k] = g5.vrati_sve(out["clanci"][k], dT["clanci"][k]["tekst"], O[k])
    sv = [p for c in out["clanci"].values() for p in c.get("pravila", [])]
    out["sazetak"] = {"clanaka": len(out["clanci"]),
                      "prepoznatih_clanaka": sum(1 for c in out["clanci"].values() if c.get("pravila")),
                      "odbijenih_clanaka_skupina": sum(1 for c in out["clanci"].values() if not c.get("pravila") and
                                                       any(x.get("razlog_kod") == "SKUPINA_NEPOZNATA" for x in c.get("pregled", []))),
                      "pravila": len(sv), "prijedlog": sum(p["status"] == "PRIJEDLOG" for p in sv),
                      "pregled": sum(p["status"] == "PREGLED" for p in sv),
                      "odbijeno": sum(len(c.get("nepokriveno", [])) for c in out["clanci"].values())}
    return out


zapisi_json = s22.zapisi_json

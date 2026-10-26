#!/usr/bin/env python3
"""EKSPERIMENT: opća gramatika odredbe za uvjete gradnje (umjesto obrazaca cijelih rečenica).

Članak → stavci »(n)« → točke »x)« (redom a, b, c …) → alineje »- …«. Svaka točka ili alineja je odredba:

    [iznimno,] [UVJET-PRIJE] PREDMET [SUBJEKT] GLAGOL [usporedba] VRIJEDNOSTI [, a PREDMET … VRIJEDNOSTI] [, UVJET-POSLIJE]

- PREDMET dolazi iz rječnika izraza (npr. »najmanja dopuštena površina građevne čestice« → minC);
- VRIJEDNOSTI su jedna vrijednost ili popis »- za <OBLIK>: <vrijednost>«;
- UVJET je doslovni odlomak (»ukoliko se … gradi podrum«, »uz uvjet da …«, »unutar …«, »ako se grade kao kosa«).

Načelo kao i u strukturiraj.py: svaki broj odredbe mora biti iskorišten, inače PREGLED. Nepoznat predmet ili oblik
građevine daje PREGLED ili nepokriveno, nikad pogađanje. Ništa nije pravno potvrđeno.
"""
import re
from citac import brojevi, normaliziraj_jedinice

N = r"\d+(?:,\d+)?"


def broj(s):
    return float(s.replace(",", "."))


# ---------------------------------------------------------------- rječnici
SKUPINE = [("visobit", r"višeobiteljsk\w*"), ("obit", r"obiteljsk\w*"), ("stamb", r"stambene građevine")]
OBLICI = [(("dvoj", "ugr"), r"dvojne i ugrađene građevine"), (("slob",), r"slobodnostojeće građevine"),
          (("dvoj",), r"dvojne građevine"), (("ugr",), r"ugrađene građevine")]
NEPOTVRDENI_OBLICI = [("samostojeca", r"samostojeć\w*")]  # mogući sinonim za »slobodnostojeća«: ne spaja se sam

# (regex predmeta, funkcija(m, kontekst) → (parametar, napomena ili None, pregled ili None))
PREDMETI = [
    (r"najmanja dopuštena površina građevne čestice", lambda m, k: ("minC", None, None)),
    (r"najmanja dopuštena površina tlocrtne projekcije", lambda m, k: ("tlMin", None, None)),
    (r"najveća dopuštena površina tlocrtne projekcije", lambda m, k: ("tlMax", None, None)),
    (r"najveći dopušteni koeficijent izgrađenosti(?: \(kig\))?", lambda m, k: ("kig", None, None)),
    (r"najveći dopušteni koeficijent iskoristivosti(?: \(kis\))? nadzemnih etaža", lambda m, k: ("kisNadzemni", None, None)),
    (r"najveći dopušteni koeficijent iskoristivosti(?: \(kis\))?(?! nadzemnih)",
     lambda m, k: ("kisPodrum", None, None) if k.get("podrum") else ("kis", None, "koeficijent iskoristivosti bez oznake nadzemno/podrum")),
    (r"najveći dopušteni broj etaža", lambda m, k: ("etazeMax", None, None)),
    (r"najveća dopuštena visina", lambda m, k: ("visinaMax", "točka mjerenja visine nije navedena u ovoj odredbi", None)),
    (r"visina od (?P<ref>najniže kote konačno zaravnatog terena)", lambda m, k: ("visinaMax", "mjereno od " + m["ref"], None)),
    (r"(?:najmanja )?udaljenost(?: [a-zčćđšž ]+?)? od regulacijskog pravca", lambda m, k: ("regulacija", None, None)),
    (r"(?:najmanja )?udaljenost(?: [a-zčćđšž ]+?)? od granice građevne čestice",
     lambda m, k: ("udaljenostOdGraniceCestice", None, "»granica građevne čestice« nije razgraničena od regulacijskog pravca")),
    (r"građevni pravac", lambda m, k: ("gradjevniPravac", None, None)),
]
GLAGOL = r"(?:iznosi|je|može iznositi)"
USPOREDBA = r"(?:najviše|najmanje)"
VRIJEDNOST = rf"(?:podrum i \d nadzemne etaže|jedna nadzemna etaža|(?P<v>{N})\s*(?P<j>m²|m³|m|%|°)?)"
UVJET_PRIJE = r"(?:ukoliko|ako) [^,]+?(?= najveći| najmanja| najveća)"
PREDUVJETI = [
    ("PODRUM", r"gradi podrum"),
    ("OKRUZENJE_FORMIRANO", r"građevna čestica nalazi u okruženju već formiranih građevinskih čestica"),
    ("ZONA_POVIJESNA_CJELINA", r"unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"),
    ("KOSI_KROV", r"grade kao kosa"),
    ("NEISPUNJENI_UVJETI_PLANA", r"nisu ispunjeni uvjeti propisani ovim Prostornim planom"),
]


def preduvjeti(uvjet):
    return [{"kod": k, "dokaz": m.group()} for k, rx in PREDUVJETI for m in re.finditer(rx, uvjet or "")]


# ---------------------------------------------------------------- razine
def stavci(tekst):
    poz = list(re.finditer(r"(?:^|(?<=\s))\((\d+)\)\s+(?=[A-ZČĆĐŠŽ])", tekst))
    if not poz:
        return [(None, tekst)]
    out = []
    for i, m in enumerate(poz):
        kraj = poz[i + 1].start() if i + 1 < len(poz) else len(tekst)
        out.append((int(m.group(1)), tekst[m.end():kraj].strip()))
    return out


def tocke(tekst):
    """Točke a), b), c) … samo redom (sljedeće slovo), da »točke b) ovog članka« ne postane nova točka."""
    out, ocek, zadnji = [], "a", None
    for m in re.finditer(r"(?:^|(?<=[\s:]))([a-z])\)\s+", tekst):
        if m.group(1) != ocek or re.search(r"točk\w*\s*$|točaka\s*$", tekst[max(0, m.start() - 12):m.start()]):
            continue
        if zadnji is not None:
            out[-1]["tekst"] = tekst[zadnji:m.start()].strip()
        out.append({"slovo": ocek, "pocetak": m.start()}); zadnji = m.end(); ocek = chr(ord(ocek) + 1)
    if out:
        out[-1]["tekst"] = tekst[zadnji:].strip()
        return tekst[:out[0]["pocetak"]].strip(), out
    return tekst.strip(), []


def alineje(tekst):
    m = re.search(r"(?:^|(?<=[:,.;]))\s*-\s+(?=[a-zčćđšž])", tekst)
    if not m:
        return tekst.strip(), []
    return tekst[:m.start()].strip(), [a.strip() for a in re.split(r"(?<=[,.;:)])\s*-\s+(?=[a-zčćđšž])", tekst[m.end():])]


# ---------------------------------------------------------------- odredba
def _oblik(s):
    for ob, rx in OBLICI:
        if re.fullmatch(rx, s.strip()):
            return ob
    return None


def odredba(tekst, kontekst):
    """Rasčlanjuje jednu odredbu. Vraća (stavke, ostatak_brojeva, razlozi) gdje je stavka
    (parametar, vrijednost, jedinica, oblici|None, vrsta_pravila, uvjet, napomena, pregled)."""
    t = normaliziraj_jedinice(tekst).strip()
    t = re.sub(r"(\d)(m²|m³)", r"\1 \2", t)
    razlozi, stavke, iskoristeno = [], [], []
    iznimka = bool(re.match(r"iznimno\b", t))
    t0 = re.sub(r"^iznimno,?\s*", "", t)
    # uvjet na kraju: », uz uvjet da …«
    uvjet_poslije = None
    mu = re.search(r",\s*(uz uvjet da .+?)\.?$", t0)
    if mu:
        uvjet_poslije = mu.group(1); t0 = t0[:mu.start()]
    # krovište: nagib i pokrov uz uvjet »ako se grade kao kosa«
    mk = re.search(rf"(?P<u>ako se grade? kao kos[aoe])\b.*?s nagibom krovnih ploha između (?P<a>\d+)° i (?P<b>\d+)°(?:.*?(?P<pk>pokrov mora biti (?P<pv>[^.)]+)))?", t0)
    if mk:
        stavke += [("nagibKrovaMin", broj(mk["a"]), "°", None, "UVJETNO", mk["u"], None, None),
                   ("nagibKrovaMax", broj(mk["b"]), "°", None, "UVJETNO", mk["u"], None, None)]
        if mk["pv"]:
            stavke.append(("pokrovKosogKrova", mk["pv"].strip(), "opis", None, "UVJETNO", mk["u"], None, None))
        iskoristeno += [mk["a"], mk["b"]]
        return stavke, _ostatak(t, iskoristeno), razlozi
    # rekonstrukcija postojećih građevina
    mr = re.search(r"(?P<u>Ukoliko nisu ispunjeni uvjeti propisani ovim Prostornim planom) mogu se rekonstruirati (?P<v>samo u postojećim tlocrtnim i visinskim gabaritima)", t0)
    if mr:
        stavke.append(("rekonstrukcijaAkoNisuIspunjeniUvjeti", mr["v"], "opis", None, "UVJETNO", mr["u"], None,
                       "opseg u odnosu na druge odredbe plana nije određen ovom odredbom"))
        return stavke, _ostatak(t, iskoristeno), razlozi
    # uvjet na početku i zona iznimke
    uvjet_prije = None
    mz = re.match(r"(unutar [^,]+),\s*", t0)
    if mz:
        uvjet_prije = mz.group(1); t0 = t0[mz.end():]
    mup = re.match(UVJET_PRIJE, t0)
    if mup:
        uvjet_prije = mup.group(); t0 = t0[mup.end():].strip()
    kont = dict(kontekst, podrum=bool(uvjet_prije and "podrum" in uvjet_prije))
    # subjekt ispred predmeta: »za izgradnju samostojeće obiteljske kuće«
    subjekt_prije = None
    ms = re.match(r"za izgradnju (\w+) (\w+) kuće\s+", t0)
    if ms:
        subjekt_prije = ms.group(1); t0 = t0[ms.end():]
    # dijelovi koordinirani s », a …«
    dijelovi = re.split(r",\s*a\s+(?=(?:najmanja|najveća|najveći|udaljenost)\b)", t0)
    for dio in dijelovi:
        pred = None
        for rx, f in PREDMETI:
            mp = re.match(rx, dio)
            if mp:
                pred = (mp, f(mp, kont)); break
        if not pred:
            razlozi.append(f"predmet odredbe nije u rječniku: »{dio[:60]}«"); continue
        mp, (par, napomena, pregled) = pred
        ostalo = dio[mp.end():]
        mg = re.match(rf"(?P<subj>.*?)\s*{GLAGOL}\s*:?\s*(?:{USPOREDBA}\s+)?(?P<vr>.*)$", ostalo)
        if not mg:
            razlozi.append(f"nema glagola »iznosi/je« iza predmeta »{mp.group()}«"); continue
        vr = mg["vr"].strip().rstrip(".,")
        if par == "gradjevniPravac":
            stavke.append((par, vr, "opis", None, "OSNOVNO", None, napomena, pregled)); continue
        popis = list(re.finditer(rf"-\s+(?:za\s+)?(?P<ob>[a-zčćđšž ]+?građevine)\s*:?\s*(?P<v>{N})\s*(?P<j>m²|m³|m|%)?(?=\s*(?:-|$))", vr))
        if popis and "".join(x.group() for x in popis).replace(" ", "") == vr.replace(" ", ""):
            for x in popis:
                ob = _oblik(x["ob"])
                stavke.append((par, broj(x["v"]), x["j"], ob if ob else ("NEPOZNAT", x["ob"]), "OSNOVNO", None, napomena,
                               pregled or (None if ob else f"oblik građevine »{x['ob']}« nije u rječniku")))
                iskoristeno.append(x["v"])
            continue
        me = re.fullmatch(r"(podrum i \d nadzemne etaže|jedna nadzemna etaža)", vr)
        if me:
            stavke.append((par, me.group(), "opis", None, "OSNOVNO", None, napomena, pregled))
            iskoristeno += re.findall(r"\d", me.group()); continue
        mv = re.fullmatch(rf"(?P<v>{N})\s*(?P<j>m²|m³|m|%)?", vr)
        if mv:
            stavke.append((par, broj(mv["v"]), mv["j"], None, "OSNOVNO", None, napomena, pregled)); iskoristeno.append(mv["v"]); continue
        razlozi.append(f"vrijednost nije prepoznata: »{vr[:60]}«")
    # iznimka / uvjet / subjekt
    uvjet = uvjet_poslije or uvjet_prije
    out = []
    for (par, v, j, ob, vp, uv, nap, pre) in stavke:
        if uvjet:
            vp = "IZNIMKA" if iznimka else "UVJETNO"
        elif iznimka:
            vp = "IZNIMKA"; pre = pre or "iznimka bez prepoznatog uvjeta"
        if subjekt_prije:
            sob = _oblik(subjekt_prije + " građevine")
            if sob:
                ob = sob
            else:
                nep = next((k for k, rx in NEPOTVRDENI_OBLICI if re.fullmatch(rx, subjekt_prije)), None)
                ob = ("NEPOTVRDEN", nep or subjekt_prije)
                pre = pre or f"»{subjekt_prije}« nije potvrđena istoznačnica za oblik građevine"
        out.append((par, v, j, ob, vp, uv if uv else uvjet, nap, pre))
    return out, _ostatak(t, iskoristeno), razlozi


def _ostatak(t, iskoristeno):
    """Brojevi odredbe koji nisu iskorišteni kao vrijednost (osim brojeva unutar doslovnog uvjeta)."""
    sv = [b["literal"] for b in brojevi(t)]
    for x in iskoristeno:
        if x in sv:
            sv.remove(x)
    return sv


# ---------------------------------------------------------------- članak
def _skupina(uvod):
    for k, rx in SKUPINE:
        if re.search(rx, uvod):
            return k
    return None


def _gradjevina(uvod):
    u = uvod.lower()
    if "poljoprivredne gospodarske" in u:
        return "poljoprivredna"
    if "pomoćne građevine" in u:
        return "pomocna"
    return "osnovna"


def clanak(br, c, plan):
    """Pravila članka po općoj gramatici. Isti oblik zapisa kao strukturiraj.py (uz polje stavak)."""
    rez = {"clanak": br, "vrste": None, "pravila": [], "upucivanja": [], "nepokriveno": [], "pregled": [], "gramatika": True}
    S = stavci(c["tekst"])
    uvod1 = S[0][1].split(":")[0] if S else ""
    skup = _skupina(uvod1)
    oblici = sorted({o for _, st in S for ob, rx in OBLICI for _ in re.finditer(rx, st) for o in ob})
    if not skup or not oblici:
        rez["pregled"].append({"razlog": "skupina ili oblici građevine nisu prepoznati iz članka"}); return rez
    vrste = [f"{skup}-{o}" for o in oblici]
    rez["vrste"] = vrste
    izv = c.get("izvor")
    for sb, st in S:
        uvod, T = tocke(st)
        gr = _gradjevina(uvod)
        jedinice = [(t["slovo"], None, t["tekst"]) for t in T]
        if not T:
            u2, al = alineje(st)
            uvod = u2; gr = _gradjevina(uvod)
            jedinice = [("-", ai, a) for ai, a in enumerate(al, 1)]
        for slovo, ai, tx in jedinice:
            stavke, ostatak, razlozi = odredba(tx, {"skupina": skup})
            if not stavke:
                if brojevi(tx):
                    rez["nepokriveno"].append({"stavak": sb, "tocka": slovo, "alineja": ai, "dokaz": tx, "razlozi": razlozi,
                                               "brojevi": [b["literal"] for b in brojevi(tx)]})
                continue
            pomak = c["tekst"].find(tx)
            for (par, v, j, ob, vp, uv, nap, pre) in stavke:
                rz = list(razlozi)
                if ostatak:
                    rz.append("neiskorišteni brojevi u odredbi: " + ", ".join(ostatak))
                if pre:
                    rz.append(pre)
                if isinstance(ob, tuple) and ob and ob[0] in ("NEPOZNAT", "NEPOTVRDEN"):
                    vr, izraz = [], ob[1]
                elif ob:
                    vr, izraz = [f"{skup}-{o}" for o in ob if f"{skup}-{o}" in vrste], None
                    if len(vr) != len(ob):
                        rz.append("oblik iz odredbe nije među oblicima članka")
                else:
                    vr, izraz = list(vrste), None
                ntx = normaliziraj_jedinice(tx)
                if uv and uv not in tx and uv not in ntx:
                    rz.append("uvjet nije doslovni odlomak odredbe")
                broj_v = isinstance(v, (int, float)) and not isinstance(v, bool)
                status = "PREGLED" if rz else "PRIJEDLOG"
                rez["pravila"].append({
                    "plan": plan, "clanak": br, "stavak": sb, "tocka": slovo, "alineja": ai, "gradjevina": gr, "parametar": par,
                    "vrijednost": v, "jedinica": j if j != "opis" else None, "vrijednost_vrsta": "opis" if j == "opis" else ("broj" if broj_v else None),
                    "vrste": sorted(vr), "vrsta_izraz": izraz, "oblik_izricit": ob is not None, "vrsta_pravila": vp, "uvjet": uv, "uvjet_izvorni": uv,
                    "preduvjeti": preduvjeti(uv), "napomena": nap, "obrazac": "gramatika", "dokaz": tx,
                    "izvor": dict(izv or {}, pomak=pomak), "status": status, "razlozi": rz,
                    "za_izracun": bool(broj_v and status == "PRIJEDLOG"),
                    "pravno_potvrdeno": False})
    return rez

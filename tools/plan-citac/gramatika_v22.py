#!/usr/bin/env python3
"""EKSPERIMENT v2.2: gramatika odredbe s morfologijom, taksonomijom vrsta građevina, kontekstom članka, logikom
uvjeta i prostornim obuhvatom. Zamrznute v1 (gramatika.py) i v2.1 (gramatika_v2.py) se ne mijenjaju.

Novo u v2.2 (u odnosu na v2.1):
- vrsta građevine iz vrste_gradevina.py (stambena, poslovna, gospodarska, ugostiteljsko-turistička, sportsko-rekreacijska,
  javna, pomoćna, infrastrukturna, kombinirane) preko osnova riječi (morfologija_hr.py), ne nabrajanjem oblika;
- članak bez stavaka dijeli se na blokove (numerirani podnaslovi »3. veličina …«), uvode (rečenica koja završava
  dvotočkom) i alineje (i s velikim početnim slovom); kontekst se prenosi samo unutar bloka, a novi uvod ga zamjenjuje;
- iznimka »Iznimno, od odredbi ovog članka na … k.č. …« otvara iznimni dio do kraja bloka (IZNIMKA + obuhvat čestice);
- predmeti bez obzira na veliko slovo, »koeficijent iskorištenosti«, »tlocrtna projekcija«, »ne može biti manja od«,
  izostavljeni predmet u »…, a za razvrstane ceste …«, kategorija ceste kao uvjet, udio zelenila, (h1+h2)/2;
- `prostorni_obuhvat` (što tekst kaže o mjestu primjene) odvojen od `primjenjivost_na_lokaciju` (uvijek NIJE_UTVRĐENA
  bez kartografske podloge); `uvjet_logika` (I / ILI / NE / NEJASNO); `obrazlozenje_statusa` za svako pravilo;
- dopuštenje gradnje iz uvoda stavka je PREGLED dok je ijedna njegova uvjetna alineja za pregled.

Iz v2.1:

Novo u odnosu na v1:
- normalizacija samo za raščlambu (»m 2« → »m²«, »4,0 metra« → »4,0 m«, razmak ispred interpunkcije); izvorni citat
  (`izvorni_citat`) uvijek je doslovni odlomak teksta članka;
- nazivi građevina u svim padežima (»stambenih građevina«, »građevine stambene namjene«, »obiteljske/višeobiteljske kuće«);
- glagoli »iznosi«, »je«, »može iznositi«, »određuje se«; usporedbe »najmanje«, »najviše«;
- stavak bez točaka i alineja dijeli se na rečenice; rečenica nasljeđuje subjekt i zonu prethodne rečenice istog stavka;
- vrste pravila: brojčane granice, NIJE_PROPISANO (≠ NEOGRANIČENO), dopuštenje i zabrana načina gradnje, alternative
  (»ravna ili kosa«), uvjetna pravila za oblik gradnje, iznimke, upućivanja na plan, formula max(h/2, X);
- svako pravilo ima status PRIJEDLOG (= ACCEPTED: automatski prihvaćen prijedlog, NIJE pravna potvrda) ili PREGLED
  (= REVIEW), kodove razloga i neriješene ovisnosti; neprepoznata odredba s brojem je ODBIJENO (= REJECTED).

Načelo ostaje: svaki broj odredbe mora biti iskorišten, nepoznat predmet ili oblik daje PREGLED ili odbijanje, nikad
pogađanje. Ništa nije pravno potvrđeno.
"""
import re
from citac import brojevi, normaliziraj_jedinice
import gramatika as g1  # zamrznuta v1: stavci, tocke, alineje, oblici, preduvjeti
import jezik_hr, semantika_hr, morfologija_hr, vrste_gradevina

VERZIJA = "gramatika-v2.2"
N = g1.N
broj = g1.broj


# ---------------------------------------------------------------- normalizacija (samo za raščlambu)
def normalizacija(t):
    """jezik_hr.normaliziraj (zamrznut) + v2.2: znak »º« (redni indikator) iza broja → »°« (oznaka kutnog stupnja).
    Karta položaja složena je preko obiju faza, pa izvorni_odlomak() i dalje vraća doslovni izvor."""
    n = jezik_hr.normaliziraj(t)
    p = jezik_hr._Pisac(n.tekst)
    p.zamijeni(r"(?<=\d)º", "°", "STUPANJ_ZNAK", "ZAPIS_JEDINICE", jezik_hr.P_STUPANJ, "»º« (redni indikator) iza broja → »°« (kutni stupanj)")
    if not p.tr:
        return n
    tr = list(n.transformacije)
    for x in p.tr:
        a = n.karta[x.od] if x.od < len(n.karta) else len(t); b = n.karta[x.do - 1] + 1
        tr.append(jezik_hr.Transformacija(x.pravilo, x.vrsta, t[a:b], x.novo, a, b, x.izvor_pravila, x.objasnjenje))
    return jezik_hr.Normalizacija(n.izvorni, p.t, [n.karta[i] for i in p.karta], tr)


def normaliziraj(t):
    return normalizacija(t).tekst


def _n(s):
    return re.sub(r"\s+", " ", s or "").strip()


# ---------------------------------------------------------------- rječnici
SKUPINE = [  # (kodovi, izraz u bilo kojem padežu)
    (("obit", "visobit"), r"obiteljsk\w*/višeobiteljsk\w* kuć\w*"),
    (("visobit",), r"višeobiteljsk\w* (?:kuć|građevin)\w*"),
    (("obit",), r"(?<!\w)obiteljsk\w* (?:kuć|građevin)\w*"),
    (("stamb",), r"stamben\w* građevin\w*|građevin\w* stambene namjene"),
    (("poljoprivredna",), r"poljoprivredn\w* gospodarsk\w* građevin\w*"),
]
OBLICI2 = [(("slob",), r"na slobodnostojeći način"), (("dvoj", "ugr"), r"kao dvojne/ugrađene")]
TOCNI_GLAGOLI = {"rekonstruirati", "prenamijeniti"}


class _Nalaz:
    def __init__(self, r, t):
        self.r, self.t = r, t

    def start(self):
        return self.r["od"]

    def end(self):
        return self.r["do"]

    def group(self):
        return self.t[self.r["od"]:self.r["do"]]


def skupina_u(s):
    """Vrsta građevine (vrste_gradevina.py, svi padeži): (kodovi, nalaz) ili (None, None)."""
    r = vrste_gradevina.prepoznaj(s or "")
    return (r["kodovi"], _Nalaz(r, s)) if r else (None, None)


def oblici_u(s):
    for ob, rx in OBLICI2:
        if re.search(rx, s or "", re.I):
            return ob
    return None


def R(kod, tekst):
    return (kod, tekst)


P_GRANICA = R("GRANICA_CESTICE_NERAZGRANICENA", "»granica građevne čestice« nije razgraničena od regulacijskog pravca")
P_H = R("H_NIJE_DEFINIRAN", "visina h nije definirana u ovoj odredbi (točka mjerenja i teren)")

# (regex predmeta, zadani operator, funkcija(m, kontekst) → (parametar, napomena, [razlozi]))
KIS = r"koeficijent iskori(?:stivosti|štenosti)"   # »iskorištenosti«: terminološka istoznačnica (nije pravopisna)
PREDMETI = [
    (r"najmanja (?:dopuštena )?površina građevne čestice", ">=", lambda m, k: ("minC", None, [])),
    (r"najveća (?:dopuštena )?površina građevne čestice", "<=", lambda m, k: ("maxC", None, [])),
    (r"najmanja (?:dopuštena )?(?:površina tlocrtne projekcije|tlocrtna projekcija)", ">=", lambda m, k: ("tlMin", None, [])),
    (r"najveća (?:dopuštena )?(?:površina tlocrtne projekcije|tlocrtna projekcija)", "<=", lambda m, k: ("tlMax", None, [])),
    (r"najveći (?:dopušteni )?koeficijent izgrađenosti(?: \(kig\))?", "<=", lambda m, k: ("kig", None, [])),
    (rf"najveći (?:dopušteni )?{KIS}(?: \(kis\))? nadzemnih etaža", "<=", lambda m, k: ("kisNadzemni", None, [])),
    (rf"najveći (?:dopušteni )?(?:{KIS}(?: \(kis\))?|\(kis\))(?! nadzemnih)", "<=",
     lambda m, k: ("kisPodrum", None, []) if k.get("podrum") else
     ("kis", None, [R("KIS_BEZ_OZNAKE", "koeficijent iskoristivosti bez oznake nadzemno/podrum")])),
    (r"najveći (?:dopušteni )?broj etaža", "<=", lambda m, k: ("etazeMax", None, [])),
    (r"najveća (?:dopuštena )?visina podzida", "<=",
     lambda m, k: ("visinaPodzidaMax", None, [R("REFERENTNA_VISINA_NEPOZNATA", "točke mjerenja visine podzida nisu navedene")])),
    (r"najveća (?:dopuštena )?visina", "<=",
     lambda m, k: ("visinaMax", None, [R("REFERENTNA_VISINA_NEPOZNATA", "referentna točka mjerenja visine nije navedena u ovoj odredbi")])),
    (r"visina od (?P<ref>najniže kote konačno zaravnatog terena)", "<=",
     lambda m, k: ("visinaMax", "mjereno od " + m["ref"],
                   [R("REFERENTNA_VISINA_NEPOTPUNA", "navedena je samo donja točka mjerenja; gornja točka mjerenja visine nije navedena")])),
    (r"(?:najmanja )?(?:dopuštena )?udaljenost(?: [a-zčćđšž ]+?)? od regulacijskog pravca", ">=", lambda m, k: ("regulacija", None, [])),
    (r"(?:najmanja )?(?:dopuštena )?udaljenost(?: [a-zčćđšž ]+?)? od granice građevne čestice", ">=",
     lambda m, k: ("udaljenostOdGraniceCestice", None, [P_GRANICA])),
    (r"građevni pravac", "opis", lambda m, k: ("gradjevniPravac", None, [])),
]
GLAGOL = r"(?P<gl>ne može biti (?:manj[ai]|već[ai]|viš[ai]) od|ne prelazi|iznosi|je|može iznositi|određuje se|se određuje)"
USPOREDBA = r"(?P<usp>najviše|najmanje)"
UVJET_PRIJE = r"(?:ukoliko|ako) [^,]+?(?= najveći| najmanja| najveća)"
ZONA_POV = r"unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"


# ---------------------------------------------------------------- pomoćno
def recenice(tekst):
    """Rečenice prema jezik_hr.recenice (ne dijeli iza kratica). v2.2: »… uvjete: Najveća …« se dijeli iza dvotočke
    kad iza nje slijedi veliko slovo (uvod i prva odredba u istoj rečenici)."""
    out = []
    for r in jezik_hr.recenice(tekst)[0]:
        out += [x.strip() for x in re.split(r"(?<=:)\s+(?=[A-ZČĆĐŠŽ])", r) if x.strip()]
    return out


def elementi(popis):
    """»otvore, prohodne terase i otvorena stubišta« → ['otvore', 'prohodne terase', 'otvorena stubišta']."""
    return [x.strip() for x in re.split(r",\s*|\s+i\s+|\s+niti\s+|\s+ili\s+", popis) if x.strip()]


def _korijen(izraz):
    return " ".join(w[:4] for w in izraz.lower().split())


CESTE = r"za (?:ostale \(pristupne\)|razvrstane|ostale|pristupne|nerazvrstane|državne|županijske|lokalne) ceste(?: i ulice)?"


def analiziraj_subjekt(s):
    """Subjekt između predmeta i glagola: »za izgradnju stambene građevine«, »nove obiteljske kuće«, »u NA2-NA15.2«,
    »za ostale (pristupne) ceste«. Vraća (skupine, stanje, zona_kod, ostatak, uvjeti_subjekta)."""
    s = (s or "").strip(" ,")
    zona, uvjeti = None, []
    mc = re.search(rf"(?:^|\s){CESTE}$", s)
    if mc:
        uvjeti.append(mc.group().strip()); s = s[:mc.start()].strip()
    mz = re.search(r"(?:^|\s)u (?P<z>[A-Z]{1,3}\d[\w.\-]*)$", s)
    if mz:
        zona = mz["z"]; s = s[:mz.start()].strip()
    s = re.sub(r"^za izgradnju\s+", "", s)
    stanje = None
    ms = re.match(r"(nove|novih|postojeće|postojećih)\s+", s)
    if ms:
        stanje = "nova" if ms.group(1).startswith("nov") else "postojeca"; s = s[ms.end():]
    sk, m = skupina_u(s)
    if m and m.start() == 0:
        s = s[m.end():].strip()
    else:
        sk = None
    s = re.sub(r"^građevin\w*(?: osnovne namjene)?$", "", s, flags=re.I).strip()   # opća »građevina« = građevina iz konteksta
    return sk, stanje, zona, s, uvjeti


def _ostatak(t, iskoristeno):
    sv = [b["literal"] for b in brojevi(t)]
    for x in iskoristeno:
        if x in sv:
            sv.remove(x)
    return sv


def zapis(par, op, v, j, vp, **kw):
    """Unutarnji zapis odredbe; kw: uvjeti, opseg, razlozi, napomena, oblici, skupine, stanje, uz_podrum, formula,
    interval, alternative, ovisnosti, ogranicenje, vrijednost_vrsta."""
    z = {"parametar": par, "operator": op, "vrijednost": v, "jedinica": j, "vrsta_pravila": vp,
         "uvjeti": [], "opseg": None, "razlozi": [], "napomena": None, "oblici": None, "skupine": None, "stanje": None,
         "uz_podrum": False, "formula": None, "interval": None, "alternative": None, "ovisnosti": [], "ogranicenje": None,
         "vrijednost_vrsta": None}
    z.update(kw)
    return z


# ---------------------------------------------------------------- posebni oblici odredbe
def f_nije_propisano(t, k):
    m = re.match(r"(?:ovim (?:prostornim )?planom )?se ne propisuje (?P<p>.+?)[;.]?$", t, re.I)
    if not m:
        return None
    for rx, _, f in PREDMETI:
        mp = re.match(rx, m["p"], re.I)
        if mp:
            par, nap, rz = f(mp, k)
            sk, st, zona, ost, _ = analiziraj_subjekt(m["p"][mp.end():])
            rz = list(rz)
            if ost:
                rz.append(R("SUBJEKT_NEPREPOZNAT", f"dio odredbe nije prepoznat: »{ost[:50]}«"))
            return [zapis(par, "nije_propisano", None, None, "OSNOVNO", skupine=sk, stanje=st, razlozi=rz, ogranicenje="NIJE_PROPISANO",
                          napomena="plan ovom odredbom ne propisuje vrijednost; to ne znači da je parametar NEOGRANIČEN")], []
    return [], []


def f_nacin_gradnje(t, k):
    m = re.match(r"(?P<s>.+?) mogu se graditi (?P<samo>samo )?kao (?P<ob>[a-zčćđšž]+) građevine\.?$", t, re.I)
    if not m:
        return None
    sk, ms = skupina_u(m["s"])
    if not ms or ms.group() != m["s"]:
        return [], []
    out = [zapis("nacinGradnje", "dopusteno", m["ob"], "opis", "OSNOVNO", skupine=sk, vrijednost_vrsta="opis")]
    if m["samo"]:
        out.append(zapis("nacinGradnje", "zabranjeno", f"svi načini gradnje osim: {m['ob']}", "opis", "NEGATIVNO", skupine=sk,
                         oblici=("ostali",), vrijednost_vrsta="opis", isključuje=m["ob"],
                         razlozi=[R("ZABRANA_IZVEDENA", "zabrana ostalih oblika izvedena je iz riječi »samo«; ostali oblici nisu nabrojeni")]))
    return out, []


def f_dopustena_gradnja(t, k):
    m = re.match(r"(?P<s>.+?) mogu se graditi (?P<u>na građevnoj čestici uz .+? uz poštivanje sljedećih uvjeta):?$", t, re.I)
    if not m:
        return None
    sk, ms = skupina_u(m["s"])
    if not ms or ms.group() != m["s"]:
        return [], []
    return [zapis("dopustenaGradnja", "dopusteno", None, "opis", "UVJETNO", skupine=sk, uvjeti=[m["u"]], vrijednost_vrsta="opis",
                  napomena="uvjeti su alineje ovog stavka")], []


KROV = re.compile(r"krovišta mogu biti (?P<alt>[a-zčćđšž]+ ili [a-zčćđšž]+) \((?P<u>ako se grade kao kosa) mogu biti "
                  r"(?P<alt2>[a-zčćđšž]+(?:, [a-zčćđšž]+)* ili [a-zčćđšž]+) i moraju biti s nagibom krovnih ploha između "
                  r"(?P<a>\d+)° i (?P<b>\d+)°(?:,? a| i) pokrov mora biti (?P<pv>[^.()]+)\)\.?$", re.I)


def f_krovista(t, k):
    m = KROV.match(t)
    if not m:
        if re.search(r"s nagibom krovnih ploha između \d+° i \d+°", t):
            # v1 je ovdje uzimala samo nagib; v2 ne predlaže djelomično raščlanjeno krovište
            return [], []
        return None
    u = m["u"]
    alt = lambda s: [x.strip() for x in re.split(r",\s*|\s+ili\s+", s)]
    out = [zapis("oblikKrovista", "dopusteno", m["alt"], "opis", "ALTERNATIVA", alternative=alt(m["alt"]), vrijednost_vrsta="opis"),
           zapis("vrstaKosogKrovista", "dopusteno", m["alt2"], "opis", "ALTERNATIVA", uvjeti=[u], alternative=alt(m["alt2"]), vrijednost_vrsta="opis"),
           zapis("nagibKrovaMin", ">=", broj(m["a"]), "°", "UVJETNO", uvjeti=[u], interval="nagibKrova"),
           zapis("nagibKrovaMax", "<=", broj(m["b"]), "°", "UVJETNO", uvjeti=[u], interval="nagibKrova"),
           zapis("pokrovKosogKrova", "=", m["pv"].strip(), "opis", "UVJETNO", uvjeti=[u], alternative=alt(m["pv"].strip()), vrijednost_vrsta="opis")]
    return out, [m["a"], m["b"]]


def f_rekonstrukcija(t, k):
    m = re.match(r"postojeće (?P<s>.+?) mogu se (?P<g1>rekons\w+) i (?P<g2>prenam\w+) (?P<u>u skladu s odredbama ovog Prostornog plana)\.?$", t)
    if m:
        sk, ms = skupina_u(m["s"])
        rz = [R("UPUCIVANJE_OPCE", "upućuje općenito na odredbe plana; ciljna namjena prenamjene nije navedena")]
        krivo = [g for g in (m["g1"], m["g2"]) if g not in TOCNI_GLAGOLI]
        if krivo:
            rz.append(R("TIPOGRAFSKA_POGRESKA", "pogrešno napisano u izvoru: " + ", ".join(f"»{g}«" for g in krivo)))
        return [zapis("rekonstrukcijaIPrenamjena", "dopusteno", None, "opis", "UVJETNO", skupine=sk, stanje="postojeca", uvjeti=[m["u"]],
                      razlozi=rz, vrijednost_vrsta="opis",
                      ovisnosti=["odredbe plana na koje se upućuje (»u skladu s odredbama ovog Prostornog plana«)"])], [], {"stanje": "postojeca", "skupine": sk}
    m = re.match(r"(?P<u>Ukoliko nisu ispunjeni uvjeti propisani ovim Prostornim planom) mogu se rekonstruirati (?P<v>samo u postojećim tlocrtnim i visinskim gabaritima)\.?$", t)
    if m:
        return [zapis("rekonstrukcijaAkoNisuIspunjeniUvjeti", "<=", m["v"], "opis", "UVJETNO", uvjeti=[m["u"]], vrijednost_vrsta="opis",
                      razlozi=[R("OPSEG_NEODREDEN", "opseg u odnosu na druge odredbe plana nije određen ovom odredbom")],
                      napomena="»<=« u odnosu na postojeće tlocrtne i visinske gabarite")], [], {}
    return None


UD = re.compile(
    rf"(?P<zona>{ZONA_POV}\s+)?(?P<s>.+?),?\s+(?:moraju|mora)\s+(?P<istak>s drugim dijelovima građevine \(istakom\)\s+)?biti udaljen[ae]\s+"
    r"(?:(?P<r1a>od granice [a-zčćđšž ]+?)\s+)?najmanje\s+(?:pola visine\s+)?(?P<h>\(h/2\)|h/2)\s*(?P<r1b>od granice [a-zčćđšž ]+?)?,\s*"
    rf"ali ne manje od (?P<x>{N})\s*m\b\s*(?P<r2>od granice [a-zčćđšž ]+?)?(?:,?\s*(?P<u>(?:ukoliko|ako) .+?))?\.?$", re.I)
OL = re.compile(rf"(?P<u>(?:ukoliko|ako) .+?),\s*udaljenost građevine od granice građevne čestice može iznositi i (?P<v>{N})\s*m\.?$", re.I)


def _subjekt_udaljenosti(s):
    zona = None
    mz = re.search(rf"\s*{ZONA_POV}\s*,?$", s, re.I)
    if mz:
        zona = mz.group().strip(" ,"); s = s[:mz.start()]
    sk, _ = skupina_u(s)
    ob = oblici_u(s)
    pr = re.search(r"tako da će se (?P<a>jednom stranom) \((?P<b>ugrađene s dvije ili tri strane)\) prislanjati uz (?P<uz>[^,]+)", s)
    return sk, ob, zona, pr


def _uvjet_razlozi(u):
    rz = []
    mi = re.search(r"ima (?P<p>.+)$", u)
    if mi and len(elementi(mi["p"])) > 1 and re.search(r"\s+i\s+", mi["p"]):
        rz.append(R("VEZNIK_DVOSMISLEN", f"veznik »i« u »{mi['p']}«: svi elementi zajedno ili bilo koji od njih"))
    return rz


def f_udaljenost_h2(t, k):
    m = UD.match(t)
    if not m:
        return None
    sk, ob, zona_s, pr = _subjekt_udaljenosti(m["s"])
    zona = (m["zona"] or "").strip() or zona_s
    iz_konteksta = False
    if not sk and re.fullmatch(r"građevin\w*", m["s"].strip(), re.I) and k.get("skupine"):
        sk, iz_konteksta = tuple(k["skupine"]), True     # »Građevina mora biti udaljena …« = građevina iz konteksta bloka
    if not sk:
        return [], []
    uv0 = [zona] if zona else []
    u = m["u"]
    uu = [u] if u else []
    x = broj(m["x"])
    r1 = (m["r1a"] or m["r1b"] or "").strip()
    r2 = (m["r2"] or "").strip()
    istak = (m["istak"] or "").strip() or None
    zaj = dict(skupine=sk, oblici=ob)
    out = []
    if pr:
        out.append(zapis("nacinPrislanjanja", "dopusteno", f"dvojna: {pr['a']}; ugrađena: {pr['b'].replace('ugrađene ', '')}", "opis", "ALTERNATIVA",
                         uvjeti=list(uv0), vrijednost_vrsta="opis", alternative=[f"dvojna: {pr['a']}", f"ugrađena: {pr['b'].replace('ugrađene ', '')}"],
                         razlozi=[R("TUMACENJE_ZAGRADE", "pridruživanje »jednom stranom« dvojnoj, a »(ugrađene s dvije ili tri strane)« ugrađenoj građevini je tumačenje zagrade")],
                         napomena="prislanja se uz " + pr["uz"], **zaj))
    if iz_konteksta:
        zaj["napomena"] = "vrsta građevine preuzeta iz konteksta bloka (subjekt rečenice je »građevina«)"
    ista_ref = not r2 or _korijen(r2.replace("građevinske", "građevne")) == _korijen(r1.replace("građevinske", "građevne"))
    if ista_ref and "čestice" in r1:
        rz = [P_H, P_GRANICA] + ([R("UVJET_SAMO_ZA_X", "uvjet je vezan uz donju granicu X; nije navedeno vrijedi li h/2 kad uvjet nije ispunjen")] if u else []) + _uvjet_razlozi(u or "")
        if "građevinske" in r1:
            rz.append(R("POJAM_VARIJANTA", "»granica građevinske čestice« uz »granica građevne čestice« u istom članku"))
        out.append(zapis("udaljenostOdGraniceCestice", "max(h/2, X)", x, "m", "OSNOVNO", uvjeti=uv0 + uu, opseg=istak,
                         formula={"izraz": f"max(h/2, {m['x']} m)", "h": None, "referenca": r1, "uvjet_za_X": u}, razlozi=rz, **zaj))
    else:
        if r1:
            out.append(zapis("udaljenostIstakaOdGraniceSusjedneGradjevine" if istak else "udaljenostH2", ">=", "h/2", "m", "OSNOVNO",
                             uvjeti=list(uv0), opseg=istak, vrijednost_vrsta="formula", formula={"izraz": "h/2", "h": None, "referenca": r1},
                             razlozi=[P_H, R("POJAM_NIJE_DEFINIRAN", f"»{r1[3:]}« nije definirana u ovoj odredbi"),
                                      R("RAZLICITE_REFERENTNE_TOCKE", f"h/2 se mjeri {r1}, a {m['x']} m {r2 or 'bez navedene reference'}; nisu spojeni u jednu formulu")],
                             **zaj))
        out.append(zapis("udaljenostIstakaOdGraniceCestice" if istak else "udaljenostOdGraniceCestice", ">=", x, "m", "UVJETNO" if uv0 + uu else "OSNOVNO",
                         uvjeti=uv0 + uu, opseg=istak,
                         razlozi=[P_GRANICA, R("RAZLICITE_REFERENTNE_TOCKE", f"{m['x']} m se mjeri {r2}, a h/2 {r1}; nisu spojeni u jednu formulu")] + _uvjet_razlozi(u or ""),
                         **zaj))
    return out, [m["x"], "2"], {"skupine": sk, "oblici": ob, "zona": zona, "pozitivni_uvjet": u, "ima_h2": True}


def f_olaksica(t, k):
    m = OL.match(t)
    if not m:
        return None
    u = m["u"]
    rz = [P_GRANICA]
    if k.get("ima_h2"):
        rz.append(R("ODNOS_PREMA_FORMULI_NEJASAN", "nije navedeno zamjenjuje li ova vrijednost cijeli izraz s h/2 ili samo donju granicu"))
    mf = re.search(r"na (?P<f>[a-zčćđšž ]+?) fasadama", u)
    if mf:
        rz.append(R("OPSEG_PROCELJA", f"uvjet se odnosi na {mf['f']} pročelja; nije navedeno vrijedi li olakšica prema svim granicama čestice"))
    pu = k.get("pozitivni_uvjet")
    mn = re.search(r"nisu predviđeni (?P<n>.+)$", u)
    if pu and mn:
        mi = re.search(r"ima (?P<p>.+)$", pu)
        if mi:
            neg = {_korijen(e) for e in elementi(mn["n"])}
            nedostaje = [e for e in elementi(mi["p"]) if _korijen(e) not in neg]
            if nedostaje:
                rz.append(R("NEGATIVNI_UVJET_NEPOTPUN", "u negativnom uvjetu se ne spominje: " + ", ".join(f"»{e}«" for e in nedostaje)))
    uv0 = [k["zona"]] if k.get("zona") else []
    if not k.get("skupine"):
        rz.append(R("SUBJEKT_NEPREPOZNAT", "subjekt rečenice nije naslijeđen iz prethodne rečenice stavka"))
    return [zapis("udaljenostOdGraniceCestice", ">=", broj(m["v"]), "m", "IZNIMKA", uvjeti=uv0 + [u], razlozi=rz,
                  skupine=k.get("skupine"), oblici=k.get("oblici"),
                  napomena="»može iznositi i« = olakšica u odnosu na prethodnu rečenicu stavka")], [m["v"]], {}


MEDJ = re.compile(rf"(?:(?P<u>(?:ukoliko|ako) ima više građevina na građevnoj čestici),?\s*)?najmanja (?:dopuštena )?udaljenost između građevina"
                  rf"(?P<ist> na istoj građevnoj čestici)? iznosi \(h1\+h2\)/2 \((?P<def>h1 i h2 su visine susjednih građevina)\),?\s*"
                  rf"ali ne manje od (?P<x>{N})\s*m\.?$", re.I)


def f_medjusobna(t, k):
    """Udaljenost između građevina na istoj čestici: max((h1+h2)/2, X); obje vrijednosti mjere se između istih građevina."""
    m = MEDJ.match(t)
    if not m:
        return None
    uv = [m["u"]] if m["u"] else []
    return [zapis("udaljenostIzmeduGradjevina", "max((h1+h2)/2, X)", broj(m["x"]), "m", "UVJETNO" if uv else "OSNOVNO", uvjeti=uv,
                  opseg=(m["ist"] or "").strip() or None, skupine=k.get("skupine"),
                  formula={"izraz": f"max((h1+h2)/2, {m['x']} m)", "h1_h2": m["def"], "referenca": "između susjednih građevina na istoj čestici"},
                  razlozi=[R("H_NIJE_DEFINIRAN", "h1 i h2 su »visine susjednih građevina«, ali točka mjerenja visine nije navedena")])], [m["x"], "2"], {}


KROV2 = re.compile(r"krovište može biti (?P<alt>ravno ili koso)(?: nagiba između (?P<a>\d+)° i (?P<b>\d+)°)?(?P<rep>.*?)\.?$", re.I)


def f_krovista2(t, k):
    """»Krovište može biti ravno ili koso nagiba između 17° i 23° …«: nagib se po tumačenju odnosi na koso krovište."""
    m = KROV2.match(t)
    if not m:
        return None
    rep_ = m["rep"].strip(" ,")
    zaj = [R("DIO_ODREDBE_NEPREPOZNAT", f"nastavak odredbe nije raščlanjen: »{rep_[:60]}«")] if rep_ else []
    alt = [x.strip() for x in m["alt"].split(" ili ")]
    out = [zapis("oblikKrovista", "dopusteno", m["alt"], "opis", "ALTERNATIVA", alternative=alt, vrijednost_vrsta="opis", skupine=k.get("skupine"), razlozi=list(zaj))]
    isk = []
    if m["a"]:
        rz = list(zaj) + [R("NAGIB_UZ_KOSO_TUMACENJE", "nagib je naveden uz »ravno ili koso«; da vrijedi samo za koso krovište je tumačenje")]
        out += [zapis("nagibKrovaMin", ">=", broj(m["a"]), "°", "UVJETNO", interval="nagibKrova", skupine=k.get("skupine"), razlozi=list(rz)),
                zapis("nagibKrovaMax", "<=", broj(m["b"]), "°", "UVJETNO", interval="nagibKrova", skupine=k.get("skupine"), razlozi=list(rz))]
        isk = [m["a"], m["b"]]
    return out, isk, {}


ZEL = re.compile(r"najmanje (?P<v>\d+(?:,\d+)?)\s*% površine (?P<sv>svake )?građevne čestice mora (?:biti uređeno|se urediti) kao (?P<o>parkovni nasadi i prirodno zelenilo)\.?$", re.I)


def f_zelenilo(t, k):
    m = ZEL.match(t)
    if not m:
        return None
    return [zapis("zeleniloMin", ">=", broj(m["v"]), "%", "OSNOVNO", skupine=k.get("skupine"), napomena="uređeno kao " + m["o"])], [m["v"]], {}


POSEBNI = [f_nije_propisano, f_nacin_gradnje, f_dopustena_gradnja, f_krovista, f_krovista2, f_zelenilo, f_medjusobna,
           f_rekonstrukcija, f_udaljenost_h2, f_olaksica]


# ---------------------------------------------------------------- brojčana odredba (proširena v1)
ZAGRADA_ETAZE = r"(?:potpuno ukopan[i]? podrum i )?(?:\d|dvije|tri|jedna) nadzemne? etaž[ae]"


def odredba_brojcana(t, kontekst):
    razlozi, stavke, iskoristeno = [], [], []
    iznimka = bool(re.match(r"iznimno\b", t, re.I))
    t0 = re.sub(r"^iznimno,?\s*", "", t, flags=re.I)
    uvjet_poslije = None
    mu = re.search(r",\s*(uz uvjet da .+?)\.?$", t0)
    if mu:
        uvjet_poslije = mu.group(1); t0 = t0[:mu.start()]
    uvjet_prije = None
    mz = re.match(r"(unutar [^,]+),\s*", t0)
    if mz:
        uvjet_prije = mz.group(1); t0 = t0[mz.end():]
    mup = re.match(UVJET_PRIJE, t0, re.I)
    if mup:
        uvjet_prije = mup.group(); t0 = t0[mup.end():].strip()
    kont = dict(kontekst, podrum=bool(uvjet_prije and "podrum" in uvjet_prije))
    subjekt_prije = None
    ms = re.match(r"za izgradnju (\w+) (\w+) kuće\s+", t0)
    if ms:
        subjekt_prije = ms.group(1); t0 = t0[ms.end():]
    dijelovi = re.split(r",\s*a\s+(?=(?:najmanja|najveća|najveći|udaljenost)\b|za\s|(?:ukoliko|ako)\s)", t0, flags=re.I)
    prethodni = None
    for di, dio in enumerate(dijelovi):
        uv_dio = None
        if di > 0:
            mud = re.match(UVJET_PRIJE, dio, re.I)
            if mud:
                uv_dio = mud.group(); dio = dio[mud.end():].strip()
        kd = dict(kont, podrum=kont["podrum"] or bool(uv_dio and "podrum" in uv_dio))
        pred, preuzet = None, False
        for rx, op0, f in PREDMETI:
            mp = re.match(rx, dio, re.I)
            if mp:
                pred = (mp, op0, f(mp, kd)); break
        if not pred and prethodni and di > 0 and re.match(r"za\s", dio):
            # izostavljeni predmet: »…, a za razvrstane ceste ne može biti manja od 6,0 m« → predmet prethodnog dijela
            mp0, op0, f0 = prethodni
            dio = mp0.group() + " " + dio
            mp = re.match(re.escape(mp0.group()), dio)
            pred, preuzet = (mp, op0, f0), True
        if not pred:
            razlozi.append(R("PREDMET_NEPOZNAT", f"predmet odredbe nije u rječniku: »{dio[:60]}«")); continue
        mp, op0, (par, napomena, rz0) = pred
        prethodni = pred
        ostalo = dio[mp.end():]
        mg = re.match(rf"(?P<subj>.*?)\s*{GLAGOL}\s*:?\s*(?:{USPOREDBA}\s+)?(?P<vr>.*)$", ostalo)
        if not mg:
            razlozi.append(R("NEMA_GLAGOLA", f"nema glagola iza predmeta »{mp.group()}«")); continue
        gl = mg["gl"]
        op = {"najviše": "<=", "najmanje": ">="}.get(mg["usp"], op0)
        if gl.startswith("ne može biti manj"):
            op = ">="
        elif gl.startswith("ne može biti") or gl == "ne prelazi":
            op = "<="
        sk, stanje, zona, ost, uv_subj = analiziraj_subjekt(mg["subj"])
        rz = list(rz0)
        uvj = ([uv_dio] if uv_dio else []) + uv_subj
        if preuzet:
            napomena = ((napomena + "; ") if napomena else "") + f"predmet »{mp.group()}« preuzet iz prethodnog dijela rečenice"
        if ost:
            rz.append(R("SUBJEKT_NEPREPOZNAT", f"dio odredbe između predmeta i glagola nije prepoznat: »{ost[:50]}«"))
        if sk and kontekst.get("skupine") and not set(sk) <= set(kontekst["skupine"]):
            rz.append(R("SUBJEKT_DRUGE_SKUPINE", "vrsta građevine u odredbi razlikuje se od vrste iz uvoda"))
        if zona:
            uvj.append(f"u {zona}")
            rz.append(R("ZONA_NIJE_DEFINIRANA", f"oznaka »{zona}« nije definirana u tekstu članka"))
        zaj = dict(skupine=sk, stanje=stanje, napomena=napomena, zona_kod=zona, uz_podrum=kd["podrum"])
        vr = mg["vr"].strip().rstrip(".,; ")
        if par == "gradjevniPravac":
            stavke.append(zapis(par, "opis", vr, "opis", "OSNOVNO", razlozi=rz, uvjeti=uvj, vrijednost_vrsta="opis", **zaj)); continue
        popis = list(re.finditer(rf"-\s+(?:za\s+)?(?P<ob>[a-zčćđšž ]+?građevine)\s*:?\s*(?P<v>{N})\s*(?P<j>m²|m³|m|%)?(?=\s*(?:-|$))", vr))
        if popis and "".join(x.group() for x in popis).replace(" ", "") == vr.replace(" ", ""):
            for x in popis:
                ob = g1._oblik(x["ob"])
                rzx = list(rz) + ([] if ob else [R("OBLIK_NEPOZNAT", f"oblik građevine »{x['ob']}« nije u rječniku")])
                stavke.append(zapis(par, op, broj(x["v"]), x["j"], "OSNOVNO", oblici=ob if ob else ("NEPOZNAT", x["ob"]), razlozi=rzx, uvjeti=list(uvj), **zaj))
                iskoristeno.append(x["v"])
            continue
        me = re.fullmatch(r"(podrum i \d nadzemne etaže|jedna nadzemna etaža)", vr)
        if me:
            stavke.append(zapis(par, op, me.group(), "opis", "OSNOVNO", razlozi=rz, uvjeti=uvj, vrijednost_vrsta="opis", **zaj))
            iskoristeno += re.findall(r"\d", me.group()); continue
        mv = re.fullmatch(rf"(?P<v>{N})\s*(?P<j>m²|m³|m|%)?(?:\s+(?P<op>za sve tipove gradnje))?(?:\s*\((?P<zag>[^()]+)\))?", vr)
        if mv:
            stavke.append(zapis(par, op, broj(mv["v"]), mv["j"], "OSNOVNO", razlozi=rz, uvjeti=uvj, opseg=mv["op"], **zaj))
            iskoristeno.append(mv["v"])
            if mv["zag"]:
                if par == "visinaMax" and re.fullmatch(ZAGRADA_ETAZE, mv["zag"]):
                    stavke.append(zapis("etazeMax", "<=", mv["zag"], "opis", "OSNOVNO", uvjeti=list(uvj), vrijednost_vrsta="opis",
                                        razlozi=[R("ZAGRADA_OBJASNJENJE", "broj etaža u zagradi uz visinu: nije navedeno je li zasebno ograničenje ili objašnjenje visine")],
                                        **dict(zaj, napomena=None)))
                    iskoristeno += re.findall(r"\d", mv["zag"])
                else:
                    stavke[-1]["razlozi"].append(R("ZAGRADA_NEPREPOZNATA", f"sadržaj zagrade nije raščlanjen: »{mv['zag'][:50]}«"))
            continue
        razlozi.append(R("VRIJEDNOST_NEPREPOZNATA", f"vrijednost nije prepoznata: »{vr[:60]}«"))
    uvjet = uvjet_poslije or uvjet_prije
    for z in stavke:
        if uvjet:
            z["vrsta_pravila"] = "IZNIMKA" if iznimka else "UVJETNO"
            z["uvjeti"] = [uvjet] + z["uvjeti"]
        elif iznimka:
            z["vrsta_pravila"] = "IZNIMKA"; z["razlozi"].append(R("IZNIMKA_BEZ_UVJETA", "iznimka bez prepoznatog uvjeta"))
        elif z["uvjeti"]:
            z["vrsta_pravila"] = "UVJETNO"
        if kont["podrum"]:
            z["uz_podrum"] = True
        if subjekt_prije:
            sob = g1._oblik(subjekt_prije + " građevine")
            if sob:
                z["oblici"] = sob
            else:
                nep = next((kk for kk, rx in g1.NEPOTVRDENI_OBLICI if re.fullmatch(rx, subjekt_prije)), None)
                z["oblici"] = ("NEPOTVRDEN", nep or subjekt_prije)
                z["razlozi"].append(R("OBLIK_NEPOTVRDEN", f"»{subjekt_prije}« nije potvrđena istoznačnica za oblik građevine"))
    return stavke, iskoristeno, razlozi


def odredba(tekst, kontekst):
    """Jedna rečenica odredbe → (zapisi, ostatak_brojeva, razlozi, kontekst_za_sljedeću_rečenicu)."""
    t = normaliziraj(tekst)
    iznimka = bool(re.match(r"iznimno\b", t, re.I))
    t0 = re.sub(r"^iznimno,?\s*", "", t, flags=re.I)
    for f in POSEBNI:
        r = f(t0, kontekst)
        if r is None:
            continue
        zap, isk = r[0], r[1]
        nk = r[2] if len(r) > 2 else {}
        if iznimka:
            for z in zap:
                if z["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
                    z["vrsta_pravila"] = "IZNIMKA"
        if not zap:
            return [], _ostatak(t, []), [R("OBLIK_ODREDBE_DJELOMICAN", f"oblik odredbe ({f.__name__[2:]}) prepoznat samo djelomično")], {}
        return zap, _ostatak(t, isk), [], nk
    zap, isk, razlozi = odredba_brojcana(t, kontekst)
    return zap, _ostatak(t, isk), razlozi, {}


# ---------------------------------------------------------------- kontekst, obuhvat, logika uvjeta
RX_PODNASLOV = re.compile(r"(?:(?<=[.:])\s+|^)(?P<n>\d{1,2})\.\s+(?=[a-zčćđšž])")
RX_ALINEJA = re.compile(r"(?<=[.:;,])\s+-\s+(?=[A-ZČĆĐŠŽa-zčćđšž])")
RX_ZONA = re.compile(r"\b(?:u zoni|na površini|površina)\s+(?P<naziv>[\wčćđšž-]+(?: [\wčćđšž-]+)*? namjene)\s*\((?P<oznaka>[A-Z][\w]*(?: \d+)?)\s*\)(?:\s+(?P<ime>[A-ZČĆĐŠŽ][a-zčćđšž]+)(?= dopušten| moguć| je| obuhvaća| određen|\s*$))?", re.I)
RX_RADNJA = re.compile(r"\b(?P<gl>graditi|izgradnja|izgradnju|gradnja|gradnju|rekonstrukcija|rekonstruirati)\s+(?:postojeći\w*\s+|nov\w*\s+)?(?P<x>.+)$", re.I)
RX_SUBJ = re.compile(r"^(?P<x>.+?)\s+(?:se\s+)?mogu se\s+(?:graditi|rekonstruirati)|^(?P<y>.+?)\s+mogu se\s+(?:graditi|rekonstruirati)", re.I)
RX_IZN_CL = re.compile(r"^Iznimno,\s*od odredbi ovog članka\s+(?P<ob>na .+?k\.\s?č\.?\s*[\d/]+(?:\s*k\.\s?o\.\s*[\wčćđšž-]+)?)", re.I)


def blokovi(tekst):
    """Članak bez stavaka → blokovi po numeriranim podnaslovima (samo redom 1, 2, 3 …): [(broj|None, tekst)]."""
    out, ocek, zadnji, br = [], 1, 0, None
    for m in RX_PODNASLOV.finditer(tekst):
        if int(m["n"]) != ocek:
            continue
        out.append((br, tekst[zadnji:m.start()].strip())); br = ocek; zadnji = m.end(); ocek += 1
    out.append((br, tekst[zadnji:].strip()))
    return [(b, t) for b, t in out if t]


def skupina_strogo(rec):
    """Vrsta građevine koja smije postati kontekst: subjekt na početku rečenice (»Pomoćne građevine grade se …«,
    »Građevine stambene namjene …«), subjekt ispred »mogu se graditi« ili objekt glagola gradnje (»graditi X«,
    »za izgradnju X«, »rekonstrukcija X«) kad X počinje nazivom vrste. Usputno spominjanje (popis sadržaja) se ne uzima."""
    r = vrste_gradevina.prepoznaj(rec, samo_pocetak=True)
    if r:
        return r["kodovi"]
    for m in [RX_SUBJ.match(rec), RX_RADNJA.search(rec)]:
        if m:
            x = m.groupdict().get("x") or m.groupdict().get("y")
            r = vrste_gradevina.prepoznaj(x or "", samo_pocetak=True)
            if r:
                return r["kodovi"]
    return None


def kontekst_iz(rec, stanje):
    """Rečenica bez pravila može postaviti kontekst: zonu (obuhvat), vrstu građevine iz »graditi / rekonstrukcija X«
    (X mora počinjati nazivom vrste) ili iznimni dio članka. Vraća promjene (dict) i opis."""
    pr, opis = {}, []
    mz = RX_ZONA.search(rec)
    if mz:
        pr["obuhvat"] = [{"vrsta": "ZONA_PLANA", "naziv": mz["naziv"], "oznaka": re.sub(r"\s+", "", mz["oznaka"]), "ime": mz["ime"],
                          "dokaz": mz.group().strip(), "utvrdjeno_na_lokaciji": False}]
        opis.append("zona")
    mi = RX_IZN_CL.match(rec)
    if mi:
        pr["iznimka"] = {"uvjet": mi["ob"], "obuhvat": {"vrsta": "KATASTARSKA_CESTICA", "dokaz": mi["ob"], "utvrdjeno_na_lokaciji": False}}
        opis.append("iznimka")
    sk = None
    for m in [RX_SUBJ.match(rec), RX_RADNJA.search(rec)]:
        if m:
            x = m.groupdict().get("x") or m.groupdict().get("y")
            r = vrste_gradevina.prepoznaj(x or "", samo_pocetak=True)
            if r:
                sk = r["kodovi"]; break
    if sk:
        pr["skupine"] = sk; opis.append("vrsta")
    return pr, opis


def logika_uvjeta(uvjeti):
    """Struktura uvjeta: I (više uvjeta), ILI, NE(ILI …) za »nisu … niti …«, NEJASNO za »i« u popisu i »odnosno«."""
    def jedan(u):
        mn = re.search(r"nisu predviđeni (?P<n>.+)$", u)
        if mn:
            return {"op": "NE", "arg": {"op": "ILI", "args": elementi(mn["n"])}, "tekst": u}
        mi = re.search(r"\bima (?P<p>.+)$", u)
        if mi and len(elementi(mi["p"])) > 1:
            return {"op": "NEJASNO_I_ILI", "args": elementi(mi["p"]), "tekst": u}
        if re.search(r"\bodnosno\b", u):
            return {"op": "NEJASNO", "tekst": u, "razlog": "»odnosno« može biti »ili« ili »to jest«"}
        if re.search(r"\s+ili\s+", u):
            return {"op": "ILI", "args": [x.strip() for x in re.split(r"\s+ili\s+", u)], "tekst": u}
        return {"op": "UVJET", "tekst": u}
    U = [jedan(u) for u in uvjeti]
    return None if not U else U[0] if len(U) == 1 else {"op": "I", "args": U}


def _gradjevina_iz(sk, gr0):
    if sk and "poljoprivredna" in sk:
        return "poljoprivredna"
    if sk and "pomocna" in sk:
        return "pomocna"
    return gr0 or "osnovna"


# ---------------------------------------------------------------- članak
def clanak(br, c, plan):
    rez = {"clanak": br, "vrste": None, "pravila": [], "upucivanja": [], "nepokriveno": [], "bez_broja": [], "pregled": [], "kontekst": [],
           "gramatika": VERZIJA}
    S = g1.stavci(c["tekst"])
    uvod1 = S[0][1].split(":")[0] if S else ""
    sk_cl = skupina_strogo(uvod1)
    skup_v1 = g1._skupina(uvod1)
    oblici_v1 = sorted({o for _, st in S for ob, rx in g1.OBLICI for _ in re.finditer(rx, st) for o in ob})
    vrste_v1 = [f"{skup_v1}-{o}" for o in oblici_v1] if skup_v1 and oblici_v1 else None
    sirovi = []
    ima_stavke = not (len(S) == 1 and S[0][0] is None)
    if ima_stavke and (sk_cl or any(skupina_strogo(st.split(":")[0]) for _, st in S)):
        _put_stavci(rez, S, sk_cl, sirovi)
    if not ima_stavke:
        _put_blokovi(rez, c["tekst"], sirovi)
    if not sirovi and not rez["nepokriveno"]:
        rez["pregled"].append({"razlog": "vrsta građevine iz uvoda članka nije prepoznata", "razlog_kod": "SKUPINA_NEPOZNATA"})
        return rez
    _zapisi(rez, br, c, plan, sirovi, vrste_v1, skup_v1)
    brs = [sb for sb, _ in S if sb is not None]
    if brs and brs != list(range(1, len(brs) + 1)):
        rez["pregled"].append({"razlog_kod": "STRUKTURA_CLANKA_NEPOUZDANA", "razlog": f"brojevi stavaka nisu redom 1…n: {brs[:12]}"})
        for p in rez["pravila"]:
            p["razlog_kod"].append("STRUKTURA_CLANKA_NEPOUZDANA"); p["razlozi"].append("brojevi stavaka u članku nisu redom; pripadnost odredbe dijelu članka nije pouzdana")
            p["status"] = "PREGLED"; p["za_izracun"] = False
    _poveznice(rez["pravila"])
    vrste = vrste_v1 if vrste_v1 is not None else sorted({x for p in rez["pravila"] for x in p["vrste"]})
    rez["vrste"] = vrste or None
    for p in rez["pravila"]:
        if p["status"] == "PREGLED" and not p["razlog_kod"]:
            p["status"] = "PRIJEDLOG"
        p["obrazlozenje_statusa"] = _obrazlozenje(p)
    return rez


def _jedinica_rec(rez, sirovi, sb, slovo, ai, tx, kont, dodatno, T=None):
    izn_al = None
    for ri, rec in enumerate(recenice(tx), 1):
        if ri == 1:
            mi = re.match(r"iznimno,?\s*(unutar [^,.]+?\bcjelin\w*|unutar [^,.]+(?=,))", normaliziraj(rec), re.I)
            izn_al = mi.group(1) if mi else None
        zap, ostatak, razlozi, nk = odredba(rec, kont)
        if izn_al and ri > 1:
            for z in zap:
                if izn_al not in z["uvjeti"]:
                    z["uvjeti"] = [izn_al] + list(z["uvjeti"])
                if z["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
                    z["vrsta_pravila"] = "IZNIMKA"
                z["napomena"] = ((z["napomena"] + "; ") if z["napomena"] else "") + "uvjet naslijeđen iz prve rečenice iznimne alineje"
        kont.update({kk: vv for kk, vv in nk.items() if vv is not None})
        if not zap:
            pr, opis = kontekst_iz(rec, kont)
            if pr:
                rez["kontekst"].append({"stavak": sb, "tocka": slovo, "alineja": ai, "recenica": ri, "postavlja": opis, "dokaz": rec})
                dodatno.update(pr); kont.update({k: v for k, v in pr.items() if k == "skupine"})
            if brojevi(normaliziraj(rec)) and not (slovo is None and ai is None and T):
                rez["nepokriveno"].append({"stavak": sb, "tocka": slovo, "alineja": ai, "recenica": ri, "dokaz": rec, "status": "ODBIJENO",
                                           "razlog_kod": [r[0] for r in razlozi] or ["ODREDBA_NEPREPOZNATA"],
                                           "razlozi": [r[1] for r in razlozi], "brojevi": [b["literal"] for b in brojevi(normaliziraj(rec))]})
            elif rec.strip() and not pr:
                rez["bez_broja"].append({"stavak": sb, "tocka": slovo, "alineja": ai, "recenica": ri, "dokaz": rec})
            continue
        for z in zap:
            if not z.get("skupine"):
                z["skupine"] = kont.get("skupine")
            if z.get("stanje") is None and kont.get("stanje"):
                z["stanje"] = kont["stanje"]
            sirovi.append((sb, slovo, ai, ri, tx, rec, _gradjevina_iz(z["skupine"], kont.get("gradjevina")), z, ostatak, razlozi,
                           {"obuhvat": list(dodatno.get("obuhvat") or []), "iznimka": dodatno.get("iznimka"), "blok": dodatno.get("blok")}))


def _put_stavci(rez, S, sk_cl, sirovi):
    """Put v2.1: stavci → točke ili alineje (malo početno slovo) → rečenice."""
    for sb, st in S:
        uvod, T = g1.tocke(st)
        if T:
            jedinice = [(t["slovo"], None, t["tekst"]) for t in T]
        else:
            u2, al = g1.alineje(st)
            if not al and RX_ALINEJA.search(st):
                d0 = RX_ALINEJA.split(st); u2, al = d0[0], d0[1:]
            # alineja s velikim početnim slovom (»- Iznimno, …«) koju v1 ne odvaja: zasebna alineja, da uvjet ne prijeđe u susjednu
            al = [x for a in al for x in RX_ALINEJA.split(a)]
            if al:
                uvod = u2; jedinice = [(None, None, u2)] + [("-", ai, a) for ai, a in enumerate(al, 1)]
            else:
                uvod = ""; jedinice = [(None, None, st)]
        gr = g1._gradjevina(uvod or st)
        sk_st = skupina_strogo(uvod) if uvod else None
        if gr == "poljoprivredna":
            sk_st = ("poljoprivredna",)
        kont_st = {"skupine": sk_st or sk_cl, "gradjevina": gr}
        for slovo, ai, tx in jedinice:
            _jedinica_rec(rez, sirovi, sb, slovo, ai, tx, dict(kont_st), {}, T)


def _put_blokovi(rez, tekst, sirovi):
    """Put v2.2 za članak bez stavaka: blokovi (podnaslovi) → uvod i alineje (i s velikim slovom) → rečenice.
    Kontekst članka (do prvog podnaslova) je polazište svakog bloka; uvod bloka ili alineja koja završava dvotočkom
    zamjenjuje ga do kraja bloka; iznimni dio (»Iznimno, od odredbi ovog članka …«) traje do kraja bloka."""
    clanak_stanje = {"skupine": None, "gradjevina": None}
    clanak_dod = {}
    for bi, (bn, btx) in enumerate(blokovi(tekst)):
        if bn is not None:
            stanje, dod = dict(clanak_stanje), {k: v for k, v in clanak_dod.items() if k != "iznimka"}
            dod["blok"] = bn
            mh = re.match(r"(?P<h>[^A-ZČĆĐŠŽ]+?)(?=\s+(?:[A-ZČĆĐŠŽ]|-\s)|$)", btx)
            if mh:
                pr, opis = kontekst_iz(mh["h"], stanje)
                rez["kontekst"].append({"blok": bn, "podnaslov": mh["h"].strip(), "postavlja": opis})
                dod.update(pr); stanje.update({k: v for k, v in pr.items() if k == "skupine"})
                btx = btx[mh.end():].strip()
        else:
            stanje, dod = clanak_stanje, clanak_dod
        btx = btx.strip()
        dijelovi = [""] + RX_ALINEJA.split(btx[2:]) if btx.startswith("- ") else RX_ALINEJA.split(btx)
        for pi, part in enumerate(dijelovi):
            slovo, ai = (None, None) if pi == 0 else ("-", pi)
            kont = dict(stanje)
            _jedinica_rec(rez, sirovi, None, slovo, ai, part, kont, dod)
            if part.rstrip().endswith(":") or kont.get("skupine") != stanje.get("skupine"):
                stanje["skupine"] = kont.get("skupine")        # uvod (dvotočka) vrijedi za sljedeće alineje bloka
        if bn is None:
            clanak_stanje, clanak_dod = stanje, dod


def _zapisi(rez, br, c, plan, sirovi, vrste_v1, skup_v1):
    izv = c.get("izvor")
    for n, (sb, slovo, ai, ri, tx, rec, gr, z, ostatak, razlozi, dod) in enumerate(sirovi, 1):
        rz = list(razlozi) + list(z["razlozi"])
        if ostatak:
            rz.append(R("NEISKORISTENI_BROJEVI", "neiskorišteni brojevi u odredbi: " + ", ".join(ostatak)))
        if dod.get("iznimka"):
            z["uvjeti"] = [dod["iznimka"]["uvjet"]] + list(z["uvjeti"])
            if z["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
                z["vrsta_pravila"] = "IZNIMKA"
        if not z.get("skupine"):
            rz.append(R("SKUPINA_NEPOZNATA", "vrsta građevine nije određena ni u odredbi ni u kontekstu"))
        ob = z["oblici"]
        sk = tuple(z["skupine"] or ())
        if isinstance(ob, tuple) and ob and ob[0] in ("NEPOZNAT", "NEPOTVRDEN"):
            vr, izraz = [], ob[1]
        elif vrste_v1 is not None and gr == "osnovna" and sk and set(sk) <= {skup_v1}:
            if ob:
                vr, izraz = [f"{skup_v1}-{o}" for o in ob if f"{skup_v1}-{o}" in vrste_v1], None
                if len(vr) != len(ob):
                    rz.append(R("OBLIK_IZVAN_CLANKA", "oblik iz odredbe nije među oblicima članka"))
            else:
                vr, izraz = list(vrste_v1), None
        else:
            vr = [f"{s}-{o}" for s in sk for o in ob] if ob else list(sk)
            izraz = None
        uvjeti = [u for u in z["uvjeti"] if u]
        uvjet = "; ".join(uvjeti) or None
        nrec = normaliziraj(rec)
        for u in uvjeti:
            if u not in rec and u not in nrec and u not in normaliziraj(tx) and u not in c["tekst"]:
                rz.append(R("UVJET_NIJE_DOSLOVAN", "uvjet nije doslovni odlomak odredbe"))
        if rec not in c["tekst"]:
            rz.append(R("CITAT_NIJE_DOSLOVAN", "izvorni citat nije doslovno u tekstu članka"))
        v = z["vrijednost"]
        broj_v = isinstance(v, (int, float)) and not isinstance(v, bool)
        nz = normalizacija(rec)
        privremeni = {"izvorni_citat": rec, "operator": z["operator"], "vrsta_pravila": z["vrsta_pravila"], "interval": z["interval"]}
        rz += [R(k, t) for k, t in semantika_hr.provjeri_pravilo(privremeni) if not (z["operator"] in ("max((h1+h2)/2, X)",))]
        obuhvat = list(dod.get("obuhvat") or [])
        if dod.get("iznimka"):
            obuhvat.append(dod["iznimka"]["obuhvat"])
        if any("povijesnih graditeljskih cjelina" in u for u in uvjeti):
            obuhvat.append({"vrsta": "POVIJESNA_CJELINA", "dokaz": ZONA_POV, "utvrdjeno_na_lokaciji": False})
        if z.get("zona_kod"):
            obuhvat.append({"vrsta": "OZNAKA_NEDEFINIRANA", "dokaz": z["zona_kod"], "utvrdjeno_na_lokaciji": False})
        for u in uvjeti:
            if re.fullmatch(CESTE, u):
                obuhvat.append({"vrsta": "KATEGORIJA_CESTE", "dokaz": u, "utvrdjeno_na_lokaciji": False})
        status = "PREGLED" if rz else "PRIJEDLOG"
        j = z["jedinica"]
        vv = z["vrijednost_vrsta"] or ("opis" if j == "opis" else ("broj" if broj_v else None))
        rez["pravila"].append({
            "id": f"{br}.{sb or 0}.{('b' + str(dod['blok']) + '.') if dod.get('blok') else ''}{slovo or '0'}.{ai or 0}.{ri}.{n}",
            "plan": plan, "clanak": br, "stavak": sb, "blok": dod.get("blok"), "tocka": slovo, "alineja": ai, "recenica": ri, "gradjevina": gr,
            "parametar": z["parametar"], "operator": z["operator"], "vrijednost": v, "jedinica": j if j != "opis" else None,
            "vrijednost_vrsta": vv, "vrste": sorted(vr), "vrsta_izraz": izraz, "oblik_izricit": ob is not None,
            "vrsta_gradevine": {"skupine": list(sk), "oblici": list(ob) if ob else None, "stanje": z["stanje"], "uz_podrum": z["uz_podrum"]},
            "vrsta_pravila": z["vrsta_pravila"], "uvjet": uvjet, "uvjet_izvorni": uvjet, "uvjeti": uvjeti, "uvjet_logika": logika_uvjeta(uvjeti),
            "opseg": z["opseg"], "preduvjeti": g1.preduvjeti(uvjet), "napomena": z["napomena"], "formula": z["formula"], "interval": z["interval"],
            "referenca": (z["napomena"][len("mjereno "):] if (z["napomena"] or "").startswith("mjereno od ") else None),
            "alternative": z["alternative"], "ogranicenje": z["ogranicenje"], "iskljucuje": z.get("isključuje"), "zona_kod": z.get("zona_kod"),
            "prostorni_obuhvat": obuhvat or [{"vrsta": "NIJE_NAVEDEN_U_ODREDBI", "dokaz": None, "utvrdjeno_na_lokaciji": False}],
            "primjenjivost_na_lokaciju": "NIJE_UTVRĐENA",
            "iznimke": [], "iznimka_od": None, "nerijesene_ovisnosti": list(z["ovisnosti"]),
            "obrazac": VERZIJA, "dokaz": tx, "izvorni_citat": rec, "normalizirani_citat": nz.tekst,
            "normalizacija": [{"pravilo": t.pravilo, "vrsta": t.vrsta, "izvorno": t.izvorno, "novo": t.novo, "od": t.od, "do": t.do,
                               "izvor_pravila": t.izvor_pravila} for t in nz.transformacije if t.pravilo not in ("BJELINA_RUB",)],
            "jezicne_napomene": [{k: v for k, v in x.items() if k in ("kod", "izvorno", "od", "moguce", "ispravljeno", "izvor_pravila")}
                                 for x in jezik_hr.pravopisne_napomene(rec)],
            "semanticki_izrazi": [{k: v for k, v in x.items() if k in ("kod", "citat", "od", "znacenje", "trazi_pregled")} for x in semantika_hr.izrazi(rec)],
            "izvor_clanak": br, "izvor_stavak": sb,
            "izvor": dict(izv or {}, pomak=c["tekst"].find(rec)), "status": status,
            "razlog_kod": [r[0] for r in rz], "razlozi": [r[1] for r in rz],
            "za_izracun": bool(broj_v and status == "PRIJEDLOG" and z["operator"] in (">=", "<=", "=")),
            "pravno_potvrdeno": False})


def _obrazlozenje(p):
    gdje = f"čl. {p['clanak']}." + (f" st. {p['stavak']}." if p["stavak"] else "") + (f" t. {p['tocka']})" if p["tocka"] not in (None, "-") else "") + \
           (f" al. {p['alineja']}" if p["alineja"] else "")
    if p["status"] == "PRIJEDLOG":
        return (f"PRIJEDLOG ({gdje}): odredba je u cijelosti raščlanjena, svi brojevi su iskorišteni i nema razloga za pregled. "
                f"Uvjet primjene: {p['uvjet'] or 'nema'}. Primjenjivost na lokaciju nije utvrđena (potrebna kartografska podloga). Nije pravna potvrda.")
    return f"PREGLED ({gdje}): " + "; ".join(p["razlozi"])


def _kljuc_gradjevine(p):
    vg = p["vrsta_gradevine"]
    return (p["gradjevina"], tuple(vg["skupine"]), tuple(vg["oblici"] or ()))


def _pregled(p, kod, tekst, ovisnost=None):
    p["razlog_kod"].append(kod); p["razlozi"].append(tekst); p["status"] = "PREGLED"; p["za_izracun"] = False
    if ovisnost:
        p["nerijesene_ovisnosti"].append(ovisnost)


def _poveznice(P):
    """Unutar članka: (1) kis uz podrum ovisi o neriješenoj zoni nadzemnog kis-a istog stavka; (2) pravilo zone povijesne
    cjeline u drugom stavku s istim parametrom i građevinom je iznimka od osnovnog; (3) iznimke se povezuju s osnovnim."""
    for p in P:
        if p["parametar"] == "kisPodrum":
            for q in P:
                if q["parametar"] == "kisNadzemni" and q["stavak"] == p["stavak"] and q["zona_kod"]:
                    _pregled(p, "OVISI_O_NERIJESENOJ_ODREDBI",
                             f"točka {q['tocka']}) ograničava nadzemni kis na »{q['zona_kod']}«; nije navedeno vrijedi li ta zona i za kis uz podrum",
                             f"obuhvat zone »{q['zona_kod']}« (točka {q['tocka']})")
    for p in P:
        if p["parametar"] == "dopustenaGradnja":
            ovisi = [q for q in P if q is not p and q["stavak"] == p["stavak"] and q["tocka"] == "-" and q["status"] == "PREGLED"]
            if ovisi:
                _pregled(p, "OVISI_O_UVJETIMA_ZA_PREGLED", f"dopuštenje vrijedi uz uvjete alineja stavka; {len(ovisi)} od njih je za pregled",
                         "alineje za pregled: " + ", ".join(sorted({str(q["alineja"]) for q in ovisi}, key=lambda x: int(x))))
    for p in P:
        if p["vrsta_pravila"] in ("OSNOVNO", "UVJETNO") and any("povijesnih graditeljskih cjelina" in u for u in p["uvjeti"]):
            if any(q is not p and q["stavak"] != p["stavak"] and q["parametar"] == p["parametar"] and _kljuc_gradjevine(q) == _kljuc_gradjevine(p)
                   and not any("povijesnih graditeljskih cjelina" in u for u in q["uvjeti"]) for q in P):
                p["vrsta_pravila"] = "IZNIMKA"
    for p in P:
        if p["vrsta_pravila"] != "IZNIMKA":
            continue
        for q in P:
            if q is not p and q["vrsta_pravila"] != "IZNIMKA" and q["parametar"] == p["parametar"] and _kljuc_gradjevine(q) == _kljuc_gradjevine(p):
                q["iznimke"].append(p["id"])
                p["iznimka_od"] = p["iznimka_od"] or q["id"]


def provjeri_sukobe(clanci):
    """Između članaka: zabrana oblika (»samo kao …«) i odredbe koje isti oblik dopuštaju ili uređuju njegov smještaj."""
    sva = [p for c in clanci.values() for p in c.get("pravila", [])]
    for z in [p for p in sva if p.get("operator") == "zabranjeno" and p["parametar"] == "nacinGradnje"]:
        for q in sva:
            if q["clanak"] == z["clanak"] or q["parametar"] not in ("nacinPrislanjanja", "nacinGradnje") or q.get("operator") != "dopusteno":
                continue
            ob = set(q["vrsta_gradevine"]["oblici"] or ())
            if ob & {"dvoj", "ugr"}:
                ref = f"čl. {q['clanak']}. st. {q['stavak']}."
                _pregled(z, "MOGUC_SUKOB_ODREDBI", f"{ref} uređuje dvojne/ugrađene građevine; prostorni obuhvat odredbi nije utvrđen", ref)
                _pregled(q, "MOGUC_SUKOB_ODREDBI", f"čl. {z['clanak']}. dopušta {z['vrsta_gradevine']['skupine']} samo kao »{z['iskljucuje']}«; prostorni obuhvat odredbi nije utvrđen",
                         f"čl. {z['clanak']}. st. {z['stavak']}. t. {z['tocka']})")

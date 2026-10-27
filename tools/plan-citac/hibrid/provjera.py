#!/usr/bin/env python3
"""HIBRIDNI ČITAČ v1 – deterministička provjera AI kandidata (svaka tvrdnja zasebno).

AI generator (izolirani agent, vidi UPUTE_GENERATORA_v1.md) predlaže kandidate s doslovnim citatima. Ovaj modul NE traži
da deterministička gramatika samostalno izdvoji isto pravilo; umjesto toga nezavisno provjerava svaku tvrdnju:

  izvor      citat je doslovan podniz teksta članka (nakon normalizacije razmaka)                 → inače ODBIJENO
  vrijednost broj je zaseban literal u citatu (hrvatski zapis: 0,5; 1.500; 17–23)               → inače ODBIJENO
  jedinica   uz taj broj u citatu stoji ista jedinica                                             → inače PREGLED
  operator   izveden iz riječi u citatu prije broja (najviše/najmanje/do/ne manje od/između …)   → inače PREGLED
  parametar  naziv iz zatvorenog popisa i ključne riječi parametra u citatu                       → inače PREGLED
  vrsta      izraz je doslovan, prepoznaje ga vrste_gradevine, naziv ima istu vrstu, a kad dolazi
             iz uvoda, izraz je u uvodu objekt gradnje ili subjekt uvoda i nema druge vrste           → inače PREGLED
  zona       sve oznake iz naslova članka i uvoda stavka su u kandidatu; svaka oznaka je u tekstu    → inače PREGLED
  uvjeti     svaki uvjet / iznimka doslovan; svaki uvjetni veznik iz citata (ukoliko, ako, kada,
             osim, uz uvjet, iznimno) pokriven je zapisanim uvjetom; uvjet uvoda stavka (»uz …«),
             »Iznimno« iz uvoda / alineje i nadređena alineja (»…:«) preneseni su                     → inače PREGLED
  stanje     »nova« samo uz izričit dokaz; uvod koji izričito propisuje novu gradnju se prenosi    → inače PREGLED
  dosljednost vrsta pravila odgovara uvjetima / iznimkama / zabrani; AI nije označio »nejasno«      → inače PREGLED
  kategorije opisne vrijednosti, »drugo:« parametri, visina bez točaka mjerenja, kis bez oznake,
             formule (h/2), vrijednost ovisna o visini, upućivanje na propis                          → uvijek PREGLED
  sukob      dva kandidata iste odredbe i istog konteksta s različitim vrijednostima                  → oba PREGLED

Statusi (zasebno se broje):
  IZDVOJEN               svaki AI kandidat;
  TEHNICKI_PROVJEREN     prošao izvor, vrijednost, jedinicu, operator i parametar;
  AUTOMATSKI_PRIHVACEN   tehnički provjeren i bez ijednog razloga za pregled (kontekst potvrđen);
  ZA_PREGLED             ima barem jedan razlog za pregled;
  ODBIJEN                citat ili vrijednost nisu u tekstu (izmišljeno).
Automatsko prihvaćanje nije pravna potvrda. Pravno potvrđeno: 0.
"""
import re, sys
from pathlib import Path

M = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(M))
import gramatika as g1
import gramatika_v25 as g5
import gramatika_v26 as g6
import vrste_gradevina as vg

VERZIJA = "hibrid-provjera-v1"
ZATVORENI = ["najmanja površina građevne čestice", "najveća površina građevne čestice", "najmanja površina tlocrtne projekcije građevine",
             "najveća površina tlocrtne projekcije građevine", "najveći koeficijent izgrađenosti (kig)",
             "najveći koeficijent iskoristivosti (kis) nadzemnih etaža", "najveći koeficijent iskoristivosti (kis) (uz podrum ili ukupni)",
             "najveći broj etaža", "najveća visina građevine", "najmanja udaljenost od granice građevne čestice",
             "najmanja udaljenost od regulacijskog pravca", "najmanja udaljenost između građevina na istoj čestici",
             "najmanja udaljenost istaka od granice susjedne građevine", "najmanja udaljenost istaka od granice građevne čestice",
             "položaj građevnog pravca", "najmanji udio zelenila na građevnoj čestici", "način gradnje",
             "prislanjanje uz susjednu građevinu ili granicu građevne čestice", "dopuštenost gradnje", "oblik krovišta",
             "vrsta kosog krovišta", "nagib krovnih ploha", "vrsta pokrova", "rekonstrukcija i prenamjena", "gabariti pri rekonstrukciji"]
KLJUCNE = {  # ključne riječi koje citat mora sadržavati za parametar
    "najmanja površina građevne čestice": r"površin\w*\s+(?:\w+\s+){0,2}građevn\w*\s+čestic|građevn\w*\s+čestic\w*\s+(?:\w+\s+){0,3}min",
    "najveća površina građevne čestice": r"površin\w*\s+(?:\w+\s+){0,2}građevn\w*\s+čestic|veličin\w*\s+građevn\w*\s+čestic",
    "najmanja površina tlocrtne projekcije građevine": r"tlocrtn\w*\s+projekcij",
    "najveća površina tlocrtne projekcije građevine": r"tlocrtn\w*\s+projekcij",
    "najveći koeficijent izgrađenosti (kig)": r"koeficijent\w*\s+izgrađenosti|\bkig\b",
    "najveći koeficijent iskoristivosti (kis) nadzemnih etaža": r"(?:koeficijent\w*\s+iskori\w+|\bkis\b).*nadzemn",
    "najveći koeficijent iskoristivosti (kis) (uz podrum ili ukupni)": r"(?:koeficijent\w*\s+iskori\w+|\bkis\b)",
    "najveći broj etaža": r"etaž",
    "najveća visina građevine": r"visin",
    "najmanja udaljenost od granice građevne čestice": r"udaljen\w*.*(?:granic\w*|međ\w*)|(?:granic\w*|međ\w*).*udaljen",
    "najmanja udaljenost od regulacijskog pravca": r"regulacijsk",
    "najmanja udaljenost između građevina na istoj čestici": r"između\s+građevina|međusobn",
    "najmanji udio zelenila na građevnoj čestici": r"zelen|hortikultur|parkovn",
    "nagib krovnih ploha": r"nagib",
}
TEHNICKI = {"VRIJEDNOST_NIJE_DOSLOVNA", "JEDINICA_NEPOTVRDENA", "OPERATOR_NEPOTVRDEN", "PARAMETAR_NEPOTVRDEN", "PARAMETAR_IZVAN_POPISA",
            "OPISNA_VRIJEDNOST", "FORMULA", "VRIJEDNOST_VISESTRUKA"}  # bez ovih razloga kandidat je tehnički provjeren
VEZNICI = re.compile(r"\b(ukoliko|ako|kada|osim|uz uvjet|pod uvjetom|u slučaju|iznimno)\b", re.I)
JED = {"m": r"(?:m|metr[ae]?|metara)(?![²2\w])", "m²": r"(?:m\s*2|m²)", "%": r"%", "°": r"(?:°|º|o\b)", "koeficijent": None}


def _n(s):
    return re.sub(r"\s+", " ", (s or "").replace("\xa0", " ")).strip()


def _nl(s):
    return _n(s).lower()


# ---------------------------------------------------------------- brojevi (hrvatski zapis)
RX_BROJ = re.compile(r"(?<![\d.,])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\d])")


def brojevi(t):
    """[(vrijednost, početak, kraj, literal)] – »1.500« = 1500 (tisućice), »0,5« = 0.5; »1.5« nije broj s tisućicama."""
    out = []
    for m in RX_BROJ.finditer(t or ""):
        lit = m.group(1)
        if "." in lit and not re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d+)?", lit):
            continue
        out.append((float(lit.replace(".", "").replace(",", ".")), m.start(1), m.end(1), lit))
    return out


def _pozicije(v, cit):
    return [b for b in brojevi(cit) if abs(b[0] - v) < 1e-9]


# ---------------------------------------------------------------- operator iz citata
OP_MAX = r"najviše|najveć\w*|maksimaln\w*|\bmax\b|ne\s+(?:smije|može)\s+biti\s+već\w*|ne\s+(?:smije|može)\s+biti\s+viš\w*|ne\s+više\s+od|ne\s+prelazi|nije\s+već\w*\s+od|nije\s+viš\w*\s+od|\bdo\b"
OP_MIN = r"najmanj\w*|minimaln\w*|\bmin\b|ne\s+(?:smije|može)\s+biti\s+manj\w*|ne\s+manje\s+od|barem|ne\s+(?:smije|može)\s+iznositi\s+manje"
RX_OP = re.compile(rf"(?P<max>{OP_MAX})|(?P<min>{OP_MIN})", re.I)


KRATICE = ("ul", "čl", "st", "br", "tzv", "npr", "sl", "tj", "k.č", "vis", "max", "min", "kbr", "k.o")


def pocetak_recenice(t, poz):
    """Početak rečenice koja sadrži položaj: zadnji »;« ili ». « prije položaja koji nije točka kratice ili rednog broja."""
    i = poz
    while i > 0:
        j = max(t.rfind(";", 0, i), t.rfind(". ", 0, i))
        if j < 0:
            return 0
        if t[j] == ";":
            return j + 1
        rijec = re.search(r"([\w.]+)$", t[:j])
        if rijec and (rijec.group(1).lower() in KRATICE or re.fullmatch(r"\d{1,3}", rijec.group(1))):
            i = j
            continue
        return j + 1
    return 0


def kraj_recenice(t, poz):
    i = poz
    while i < len(t):
        j = [x for x in (t.find(";", i), t.find(". ", i)) if x >= 0]
        if not j:
            return len(t)
        j = min(j)
        rijec = re.search(r"([\w.]+)$", t[:j])
        if t[j] == "." and rijec and (rijec.group(1).lower() in KRATICE or re.fullmatch(r"\d{1,3}", rijec.group(1))):
            i = j + 1
            continue
        return j + 1
    return len(t)


def operator_iz_citata(cit, poz):
    """Operator za broj na položaju poz: zadnji izraz najmanje/najviše u istoj rečenici prije broja; inače »=« ako je glagol
    »iznosi / je / su / moraju biti«. Vraća (operator, dokaz) ili (None, razlog). cit je rečenica izvornog teksta."""
    seg = cit[pocetak_recenice(cit, poz):poz]
    if re.search(r"između\s*$|između\s+[\d,.\s°ºo]+i\s*$", seg, re.I) or re.search(r"između\s+\S+\s*$", seg, re.I):
        return "izmedju", "između"
    zadnji = None
    for m in RX_OP.finditer(seg):
        zadnji = m
    if zadnji:
        return ("<=" if zadnji["max"] else ">="), zadnji.group(0)
    if re.search(r"\b(iznosi|iznose|je|su|biti|udaljen\w*|visine)\b", seg, re.I):
        return "=", "bez izričitog najmanje/najviše (doslovno =, odluka suca v1.3/2)"
    return None, "nema izraza iz kojeg se može izvesti operator"


# ---------------------------------------------------------------- kontekst članka
def stavak_tekst(art, stavak):
    S = dict(g1.stavci(art["tekst"]))
    return S.get(stavak) if stavak is not None else art["tekst"]


def uvod(t):
    """Uvod stavka/članka: tekst do prve dvotočke ako je u prvih 400 znakova, inače prva rečenica."""
    t = t or ""
    i = t.find(":")
    if 0 <= i < 400:
        return t[:i]
    return re.split(r"(?<=[.;])\s+(?=[A-ZČĆŽŠĐ(])", t.strip(), maxsplit=1)[0]


def prva_recenica(t):
    return re.split(r"(?<=[.;])\s+(?=[A-ZČĆŽŠĐ(])", (t or "").strip(), maxsplit=1)[0]


def _kod_zone(z):
    return re.sub(r"[\s()]", "", z or "").upper()


def zone_potrebne(art, stavak):
    Z = list(g6.zone_naslova(art.get("naslov")))
    st = stavak_tekst(art, stavak) or ""
    Z += g5.oznake_zona(uvod(st))
    return list(dict.fromkeys(_kod_zone(z) for z in Z if z))


def _segment_alineje(st, poz):
    """Tekst od početka alineje (zadnja »- «, »•« ili »;« prije položaja) do položaja."""
    i = max(st.rfind("; ", 0, poz), st.rfind(" - ", 0, poz), st.rfind("•", 0, poz), st.rfind(": ", 0, poz))
    return st[i + 1:poz] if i >= 0 else st[:poz]


RX_TOCKA = re.compile(r"(?:^|\s)([a-z])\)\s")
RX_UVJET_UVODA = re.compile(r"(?:na\s+građevnoj\s+čestici\s+)?\buz\s+(?:građevin|obiteljsk|višeobiteljsk|stambenu|osnovn)[^,:;]*?(?=\s+uz\s+(?:poštivanje|uvjet)|\s*$)", re.I)
RX_ALINEJA = re.compile(r"(?:^|[.;:,]\s|\s{2})[-–]\s|•")


def polozaj(st, poz):
    """Deterministički položaj odredbe u stavku: slovo točke »x)« (i kad je odredba u alineji te točke), »-« za alineju
    izvan točke, None inače. Ne oslanja se na AI."""
    seg = st[:poz]
    lt = None
    for m in RX_TOCKA.finditer(seg):
        lt = m
    la = None
    for m in RX_ALINEJA.finditer(seg):
        la = m
    if lt and not (la and la.start() > lt.start()):
        return lt.group(1)
    if la:
        return "-"          # upute označavanja v1.2: odredba u alineji (i alineji unutar točke) → »-«
    return None


def nadredjeni_uvod(st, poz):
    seg = st[:poz]
    i = seg.rfind(";")
    if i < 0:
        return None
    sub = seg[i + 1:]
    if ":" not in sub:
        return None
    u = sub[:sub.rfind(":")].strip(" -•")
    if not u or re.search(r"[.;]\s+(?:-|•|\d{1,2}\.)\s", u) or not re.match(r"\s*[-•]", sub):
        return None
    return u


# ---------------------------------------------------------------- provjera jednog kandidata
def provjeri(k, art):
    """Vraća (status, razlozi[(kod, tekst)]) za kandidata k nad člankom art {broj, tekst, naslov}."""
    R = []
    pregled = lambda kod, t: R.append((kod, t))
    T, cit = _n(art["tekst"]), _n(k.get("citat"))
    if not cit or cit not in T:
        return "ODBIJEN", [("CITAT_NIJE_DOSLOVAN", "citat nije doslovan podniz teksta članka")]
    poz_cit = T.find(cit)
    st = _n(stavak_tekst(art, k.get("stavak")) or art["tekst"])
    poz_st = st.find(cit)
    par, op, v, j = k.get("parametar") or "", k.get("operator"), k.get("vrijednost"), k.get("jedinica")

    # --- vrijednost i jedinica
    poz_v = None
    if isinstance(v, bool):
        return "ODBIJEN", [("VRIJEDNOST_NEISPRAVNA", "logička vrijednost")]
    if isinstance(v, (int, float)):
        P = _pozicije(float(v), cit)
        if not P:
            return "ODBIJEN", [("VRIJEDNOST_NIJE_U_CITATU", f"broj {v} nije zaseban literal u citatu")]
        if len(P) > 1:
            pregled("VRIJEDNOST_VISESTRUKA", f"broj {v} se u citatu pojavljuje {len(P)} puta")
        poz_v = P[0][1]
        jr = JED.get(j) if j in JED else None
        iza = cit[P[0][2]:P[0][2] + 12]
        if j in ("m", "m²", "%", "°"):
            if not re.match(rf"\s*{jr}", iza, re.I):
                pregled("JEDINICA_NEPOTVRDENA", f"uz broj nije jedinica »{j}«")
        elif j == "koeficijent":
            if "koeficijent" not in par and not re.search(r"\bki[gs]\b", par):
                pregled("JEDINICA_NEPOTVRDENA", "jedinica »koeficijent« samo za kig/kis")
        elif j is None:
            if re.match(r"\s*(?:m\b|m\s*2|m²|%|°|metr)", iza):
                pregled("JEDINICA_NEPOTVRDENA", "uz broj stoji jedinica, a kandidat je nema")
        else:
            pregled("JEDINICA_NEPOTVRDENA", f"nepoznata jedinica »{j}«")
    elif op == "izmedju" and isinstance(v, str):
        d = [x for x in re.split(r"\s*[–-]\s*", v) if x]
        try:
            vv = [float(x.replace(",", ".")) for x in d]
        except ValueError:
            return "ODBIJEN", [("VRIJEDNOST_NEISPRAVNA", f"raspon »{v}« nije broj–broj")]
        P = [_pozicije(x, cit) for x in vv]
        if len(vv) != 2 or not all(P):
            return "ODBIJEN", [("VRIJEDNOST_NIJE_U_CITATU", f"raspon »{v}« nije u citatu")]
        poz_v = P[0][0][1]
        if not re.search(r"između", cit[max(0, poz_v - 40):poz_v], re.I) and not re.search(r"\d\s*[o°º]?\s*[-–]\s*\d", cit[poz_v:poz_v + 12]):
            pregled("OPERATOR_NEPOTVRDEN", "raspon bez »između« ili »A-B«")
    else:
        if isinstance(v, str) and v and _nl(v) not in _nl(cit):
            pregled("VRIJEDNOST_NIJE_DOSLOVNA", "tekstna vrijednost nije doslovno u citatu")
        pregled("OPISNA_VRIJEDNOST", "opisna vrijednost; deterministička provjera smisla nije moguća")

    # --- operator
    aps_v = poz_cit + poz_v if poz_v is not None else None
    rec = T[pocetak_recenice(T, poz_cit):kraj_recenice(T, poz_cit + len(cit))]
    if poz_v is not None and op in ("<=", ">=", "="):
        izv, dok = operator_iz_citata(T, aps_v)
        if izv is None or izv != op:
            pregled("OPERATOR_NEPOTVRDEN", f"operator iz citata: {izv} ({dok}); kandidat: {op}")
    elif op not in ("<=", ">=", "=", "izmedju"):
        pregled("OPISNA_VRIJEDNOST", f"operator »{op}« nije brojčani")
    if re.search(r"\bh\s*/\s*2|\(h1\s*\+\s*h2\)", cit[max(0, (poz_v or 0) - 60):(poz_v or 0) + 20]):
        pregled("FORMULA", "vrijednost je dio formule (h/2, (h1+h2)/2)")

    # --- parametar
    if par.startswith("drugo"):
        pregled("PARAMETAR_IZVAN_POPISA", "parametar izvan zatvorenog popisa")
    elif par not in ZATVORENI:
        pregled("PARAMETAR_IZVAN_POPISA", f"»{par}« nije naziv iz zatvorenog popisa")
    elif par in KLJUCNE and not re.search(KLJUCNE[par], rec, re.I):
        pregled("PARAMETAR_NEPOTVRDEN", "ključne riječi parametra nisu u rečenici odredbe")
    elif par in KLJUCNE and not re.search(KLJUCNE[par], cit, re.I):
        pregled("CITAT_DIO_RECENICE", "naziv parametra je u rečenici ispred citata, a ne u citatu: kvalifikatori ispred vrijednosti nisu provjereni")
    if par == "najveća visina građevine" and not re.search(r"\bod\s+[^.;]{3,80}\bdo\b|mjeren\w*\s+od|od\s+(?:najniže\s+)?kote", rec, re.I):
        pregled("TOCKA_MJERENJA", "visina bez točaka mjerenja")
    if par.startswith("najveći koeficijent iskoristivosti") and "nadzemn" not in par and not re.search(r"podrum|ukup|ukopan", cit, re.I):
        pregled("KIS_NEJASAN", "kis bez oznake nadzemnih etaža ili podruma / ukupnog")
    if par == "najveći broj etaža" and re.search(r"nadzemn", cit, re.I):
        pregled("ETAZE_NADZEMNE", "broj etaža uz razlikovanje nadzemnih etaža: zatvoreni popis nema zaseban parametar, nije provjerljivo odnosi li se vrijednost na sve ili na nadzemne etaže")
    if re.search(r"za\s+građevine\s+visine\s+do|za\s+više\s+građevine", cit, re.I):
        pregled("OVISI_O_VISINI", "vrijednost ovisi o visini građevine")
    if re.search(r"pravilnik|posebn\w+\s+propis|u\s+skladu\s+s\s+(?:posebnim|važećim)", cit, re.I):
        pregled("UPUCIVANJE", "citat upućuje na propis izvan plana")

    # --- vrsta građevine
    vgr = k.get("vrsta_gradevine") or {}
    izraz, cizr, izvor = _n(vgr.get("izraz")), _n(vgr.get("citat_izraza")), vgr.get("izvor")
    H = _n(art.get("naslov"))
    kodovi = None
    if not izraz or not cizr or (cizr not in T and cizr not in H):
        pregled("VRSTA_NEPOTVRDENA", "izraz vrste nema doslovni citat")
    elif _nl(izraz) not in _nl(cizr):
        pregled("VRSTA_NEPOTVRDENA", "izraz vrste nije u svom citatu")
    else:
        r = vg.prepoznaj(izraz, samo_pocetak=False)
        rn = vg.prepoznaj(vgr.get("naziv") or "", samo_pocetak=False)
        if not r:
            pregled("VRSTA_NEPREPOZNATA", f"»{izraz}« nije prepoznata vrsta građevine (općeniti subjekt ili nepoznata vrsta)")
        else:
            kodovi = tuple(r["kodovi"])
            if not rn or tuple(rn["kodovi"]) != kodovi:
                pregled("VRSTA_NAZIV_NEDOSLJEDAN", "naziv vrste i izraz u tekstu ne daju istu vrstu")
            if izvor and izvor != "odredba":
                rec = next((s for s in re.split(r"(?<=[.;:])\s+", T) if cizr in s or s in cizr), cizr)
                V = g6.vrste_uvoda(rec)
                obj = {v_["kodovi"] for v_ in V if v_["odnos"] == "OBJEKT_GRADNJE"}
                subjekt = re.match(rf"\s*{re.escape(izraz)}\s+(?:se\s+)?(?:grade|gradi|mogu\s+se\s+graditi|može\s+se\s+graditi)", rec, re.I)
                i_izr = _nl(rec).find(_nl(izraz))
                objekt = i_izr >= 0 and re.search(r"(?:graditi|gradnj\w*|izgradnj\w*|rekonstrukcij\w*|rekonstruirati|smještaj\w*|grade\s+se|se\s+grade|namijenjen\w*\s+(?:je|su)\s+\w+)\s+(?:\w+\s+){0,2}$",
                                                   _nl(rec)[:i_izr] + " ", re.I)
                naslov_zone = izvor == "naslov" and re.match(rf"\s*zon\w*\s+[^-–]+[-–]\s*{re.escape(_nl(izraz))}\s*$", _nl(H))
                if not (kodovi in obj or subjekt or objekt or naslov_zone):
                    pregled("VRSTA_ODNOS_NEPOTVRDEN", "izraz vrste u uvodu nije objekt gradnje ni subjekt uvoda")
                if len(obj) > 1:
                    pregled("VRSTA_VISEZNACNA", "uvod imenuje više vrsta u odnosu gradnje")
            elif izvor == "odredba" and cizr not in cit and cit not in cizr:
                pregled("VRSTA_IZVAN_ODREDBE", "vrsta označena kao iz odredbe, a izraz nije u citatu odredbe")
        uv = uvod(st)
        ku, _, razl = g6.vrsta_uvoda(uv)
        if kodovi and ku and ku != kodovi and izvor != "odredba":
            pregled("VRSTA_SUPROTNA_UVODU", "uvod stavka imenuje drugu vrstu")

    # --- način gradnje i stanje
    ng = k.get("nacin_gradnje")
    if ng:
        cn = _n(k.get("citat_nacina"))
        rx = {"slobodnostojeća": r"slobodnostoj|samostoj", "dvojna": r"dvojn", "ugrađena": r"ugrađ|u nizu"}.get(ng)
        if not cn or cn not in T or not rx or not re.search(rx, cn, re.I):
            pregled("NACIN_NEPOTVRDEN", "način gradnje bez doslovnog dokaza")
    stanje = k.get("stanje")
    kontekst_nova = re.search(r"\bnov\w*\b|novu\s+izgradnj", uvod(st) + " " + cit, re.I)
    if stanje == "nova":
        cs = _n(k.get("citat_stanja"))
        if not cs or cs not in T or not re.search(r"\bnov", cs, re.I):
            pregled("STANJE_NEPOTVRDENO", "»nova« bez doslovnog dokaza")
    elif kontekst_nova and g5.RX_NOVA.search(uvod(st) + " " + cit):
        pregled("STANJE_IZGUBLJENO", "uvod ili odredba izričito propisuje novu gradnju, a kandidat je nema")
    if stanje == "postojeća" and not re.search(r"postojeć", cit, re.I):
        pregled("STANJE_IZ_UVODA", "»postojeća« nije u samoj odredbi; ograničava li uvod svako pravilo, nije provjereno")

    # --- zona
    Zk = {_kod_zone(z) for z in ((k.get("zona") or {}).get("oznake") or [])}
    for z in zone_potrebne(art, k.get("stavak")):
        if z not in Zk:
            pregled("ZONA_IZGUBLJENA", f"zona {z} iz naslova ili uvoda nije u kandidatu")
    TH = _kod_zone(T + " " + H)
    for z in Zk:
        if z and z not in TH:
            pregled("ZONA_NEPOTVRDENA", f"zona {z} nije u tekstu")

    # --- uvjeti i iznimke
    U = [(_n(u.get("tekst")), _n(u.get("citat")), u.get("izvor")) for u in (k.get("uvjeti") or [])]
    I = [(_n(u.get("tekst")), _n(u.get("citat"))) for u in (k.get("iznimke") or [])]
    for t_, c_, *_ in U + I:
        if not c_ or c_ not in T + " " + H:
            pregled("UVJET_NIJE_DOSLOVAN", f"uvjet/iznimka »{t_[:40]}« nema doslovni citat")
    pokriveno = [_nl(x[1]) for x in U + I]
    brojevi_cit = [b[1] for b in brojevi(cit)]
    for m in VEZNICI.finditer(cit):
        w = m.group(1).lower()
        if w == "iznimno":
            continue
        p = m.start()
        if poz_v is not None and p > poz_v and any(poz_v < b < p for b in brojevi_cit):
            continue  # veznik pripada sljedećoj vrijednosti u rečenici
        klauza = _nl(cit[p:p + 60])
        if not any(klauza[:25] in x or (x and x[:25] in _nl(cit[p:])) for x in pokriveno):
            pregled("UVJET_IZGUBLJEN", f"veznik »{w}« u citatu nije pokriven zapisanim uvjetom")
    if poz_v is not None and re.search(r"\bodnosno\s*$", cit[:poz_v].rstrip()[-12:], re.I) and not [u for u in U if u[2] == "odredba"]:
        pregled("UVJET_IZGUBLJEN", "vrijednost iza »odnosno« nema vlastiti uvjet")
    seg_al = _segment_alineje(st, poz_st if poz_st >= 0 else 0)
    trazi_iznimku = re.search(r"\biznimno\b", cit, re.I) or re.match(r"\s*\(?\d*\w?\)?\s*iznimno\b", uvod(st), re.I) or \
        re.search(r"\biznimno\b", seg_al, re.I)
    nu = nadredjeni_uvod(st, poz_st) if poz_st >= 0 else None
    if nu and re.search(r"\biznimno\b", nu, re.I):
        trazi_iznimku = True
    if trazi_iznimku and (not I or k.get("vrsta_pravila") != "IZNIMKA"):
        pregled("IZNIMKA_IZGUBLJENA", "odredba, alineja ili uvod su iznimka, a kandidat to nema")
    if nu and not any(_nl(c_)[:30] in _nl(nu) or _nl(nu)[:30] in _nl(c_) for _, c_, *_ in U + I):
        pregled("KONTEKST_NADREDJENE_ALINEJE", "uvod nadređene alineje nije prenesen")
    uv = uvod(st)
    if re.search(r"\buz\s+(?:građevin\w+|obiteljsk\w+|višeobiteljsk\w+|stambenu|osnovn\w+)", uv, re.I) and k.get("stavak") is not None:
        if not any(x[2] == "uvod" and _nl(x[1]) and _nl(x[1]) in _nl(uv) for x in U):
            pregled("UVJET_UVODA_IZGUBLJEN", "uvjet iz uvoda stavka (»uz …«) nije prenesen")
        else:
            m_uv = RX_UVJET_UVODA.search(uv)
            if m_uv and not any(x[2] == "uvod" and _nl(x[1]) == _nl(m_uv.group(0)) for x in U):
                pregled("UVJET_UVODA_NEPOTPUN", f"uvjet iz uvoda mora biti cijeli odlomak »{m_uv.group(0).strip()}«")
    if poz_v is not None:
        m_za = re.match(r"[\s\d.,]*(?:m\s*2|m²|metr\w*|m|%|°)?\s*(za\s+[^,;.:]+)", cit[poz_v:], re.I)
        if m_za and not any(_nl(m_za.group(1))[:20] in _nl(x[1]) for x in U):
            pregled("UVJET_IZGUBLJEN", f"odlomak iza vrijednosti »{m_za.group(1).strip()}« nije zapisan kao uvjet")

    # --- dosljednost vrste pravila
    vp = k.get("vrsta_pravila")
    vlastiti = [u for u in U if u[2] == "odredba"]
    ocek = "IZNIMKA" if I else ("NEGATIVNO" if op == "zabrana" else ("UVJETNO" if vlastiti else "OSNOVNO"))
    if vp != ocek:
        pregled("VRSTA_PRAVILA_NEDOSLJEDNA", f"vrsta pravila {vp}, prema uvjetima/iznimkama {ocek}")
    if k.get("nejasno"):
        pregled("AI_NEJASNO", f"generator: {str(k['nejasno'])[:120]}")

    kodovi_r = {x[0] for x in R}
    if not R:
        return "AUTOMATSKI_PRIHVACEN", R
    return ("TEHNICKI_PROVJEREN_ZA_PREGLED" if not (kodovi_r & TEHNICKI) else "ZA_PREGLED"), R


def sukobi(K):
    """Kandidati iste odredbe i istog konteksta s različitim vrijednostima → svi PREGLED (SUKOB_KANDIDATA)."""
    G = {}
    for i, k in enumerate(K):
        if k["_status"] in ("ODBIJEN",):
            continue
        kl = (k.get("clanak"), k.get("stavak"), k.get("tocka"), k.get("alineja_rb"), k.get("parametar"), _nl((k.get("vrsta_gradevine") or {}).get("naziv")),
              tuple(sorted(_nl(u.get("tekst")) for u in (k.get("uvjeti") or []))), tuple(sorted(_nl(u.get("tekst")) for u in (k.get("iznimke") or []))))
        G.setdefault(kl, []).append(i)
    for kl, I in G.items():
        if len({str(K[i].get("vrijednost")) for i in I}) > 1:
            for i in I:
                K[i]["_razlozi"].append(("SUKOB_KANDIDATA", "isti kontekst, različite vrijednosti"))
                if K[i]["_status"] == "AUTOMATSKI_PRIHVACEN":
                    K[i]["_status"] = "TEHNICKI_PROVJEREN_ZA_PREGLED"


def provjeri_sve(kandidati, clanci):
    """clanci: {broj: {broj, tekst, naslov}}. Vraća kandidate s _status i _razlozi."""
    out = []
    for k in kandidati:
        k = dict(k)
        art = clanci.get(k.get("clanak"))
        if not art:
            k["_status"], k["_razlozi"] = "ODBIJEN", [("CLANAK_NEPOSTOJI", "članak nije u ulaznom tekstu")]
        else:
            k["_status"], k["_razlozi"] = provjeri(k, art)
            st = _n(stavak_tekst(art, k.get("stavak")) or art["tekst"])
            cit = _n(k.get("citat"))
            pz = st.find(cit)
            v = k.get("vrijednost")
            if pz >= 0 and isinstance(v, (int, float)) and not isinstance(v, bool):
                Pv = _pozicije(float(v), cit)
                if Pv:
                    pz += Pv[0][1]          # položaj vrijednosti, ne početka citata (alineja unutar točke)
            k["_tocka"] = polozaj(st, pz) if pz >= 0 else k.get("tocka")
        out.append(k)
    sukobi(out)
    return out


def razine(K):
    s = lambda x: x["_status"]
    return {"izdvojeno": len(K), "odbijeno": sum(s(k) == "ODBIJEN" for k in K),
            "tehnicki_provjereno": sum(s(k) in ("AUTOMATSKI_PRIHVACEN", "TEHNICKI_PROVJEREN_ZA_PREGLED") for k in K),
            "automatski_prihvaceno": sum(s(k) == "AUTOMATSKI_PRIHVACEN" for k in K),
            "za_pregled": sum(s(k) in ("TEHNICKI_PROVJEREN_ZA_PREGLED", "ZA_PREGLED") for k in K)}

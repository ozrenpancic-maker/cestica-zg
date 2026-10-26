#!/usr/bin/env python3
"""EKSPERIMENT v2.1: hrvatski jezični sloj (pravopisna normalizacija). Zaseban modul; zamrznuta v1 se ne mijenja.

Pomoćni izvor pravopisnih pravila: Hrvatski pravopis, Institut za hrvatski jezik i jezikoslovlje, radna inačica
(2013., 44 str., SHA-256 33cbbfa7…). Korišteni su samo odjeljci o bjelini, točki, zarezu, kraticama, kosoj crti,
crtici i pisanju ije/je. Pravopis NIJE izvor pravila o padežima, sklonidbi ni morfologiji. Za to postoji zasebno
sučelje (`MorfoloskiAnalizator`), a zadana provedba ništa ne zaključuje.

Načela:
1. Normalizacija je samo PRAVOPISNA, ili mijenja ZAPIS JEDINICE iste vrijednosti. Ne tumači propis; tumačenje je
   u semantika_hr.py.
2. Svaka transformacija se bilježi: pravilo, izvorni odlomak, novi zapis, položaj u izvornom tekstu i izvor pravila.
   `izvorni_odlomak(od, do)` vraća doslovni izvorni tekst za bilo koji raspon normaliziranog teksta.
3. Pravopisne pogreške u izvoru se NE ispravljaju. Bilježe se kao napomene (»rekonsrturirati«, »slijedeće«).
"""
import difflib, re, unicodedata
from dataclasses import dataclass, field, asdict
from decimal import Decimal

PRAVOPIS = {"naziv": "Hrvatski pravopis, Institut za hrvatski jezik i jezikoslovlje, radna inačica (2013.)",
            "sha256": "33cbbfa705f8603929d0f358c9d820385ec9de7b0e7ba4e4e780ec959a79f87c",
            "uloga": "pomoćni izvor pravopisnih pravila; nije izvor pravila o padežima ni pravnog tumačenja"}
# odjeljci pravopisa (stranica PDF-a radne inačice) na koje se pravila pozivaju
P_BJELINA = "Pravopisni znakovi – Bjelina, a) između riječi (str. 33)"
P_BJELINA_NE = "Bjelina se ne nalazi: a) ispred rečeničnih znakova točke, zareza, točke sa zarezom, dvotočke (str. 34)"
P_BROJ_JEDINICA = "Bjelina: k) između broja i oznake mjerne jedinice: 3 kg, 2 m (str. 33)"
P_DECIMALNI = "Zarez u decimalnim brojevima: 5,76; bjelina se ne nalazi iza zareza u decimalnome broju: 1,41 (str. 34, 38)"
P_REDNI = "Točka se piše: b) iza rednih brojeva napisanih arapskim i rimskim brojkama (str. 34)"
P_TISUCICE = "Bjelina: h) između mjesta stotice i tisućice; u financijskome poslovanju dopuštena je točka: 10.000 (str. 33, 35)"
P_KRATICE = "Kraćenje riječi – Kratice: završavaju točkom; br., st., t., npr., tj., itd., i sl., i dr. (str. 31)"
P_KOSA = "Kosa crta bez bjelina: a) jedna od mogućnosti (ili): i/ili; b) uključenost obiju sastavnica (i) (str. 42–43)"
P_KOSA_BROJ = "Kosa crta: d) izdvajanje dijela iz cjeline; e) klase, brojevi glasila: NN 82/12; m) razlomak: 1/3 (str. 34, 43)"
P_CRTICA = "Crtica ( – ) s bjelinama: d) raspon ili značenje »od – do«: 30 – 45 minuta (str. 42)"
P_STUPANJ = "Bjelina se ne nalazi: l) između broja i oznake za kutni stupanj (str. 34)"
P_IJE = "Dvoglasnik ie: kratak se piše je: sljedeći (pridjev) (str. 10)"
P_ODNOSNO = "Zarez: »odnosno« s rastavnom ulogu (= ili) bez zareza; sa zarezom kad uvodi objašnjenje (= to jest) (str. 37)"
NIJE_PRAVOPIS = "nije iz pravopisa: ručni popis za tekstove prostornih planova"


@dataclass
class Transformacija:
    pravilo: str
    vrsta: str            # PRAVOPISNA | ZAPIS_JEDINICE
    izvorno: str
    novo: str
    od: int               # položaj u izvornom tekstu
    do: int
    izvor_pravila: str
    objasnjenje: str


@dataclass
class Normalizacija:
    izvorni: str
    tekst: str
    karta: list = field(repr=False)     # za svaki znak normaliziranog teksta: položaj u izvornom tekstu
    transformacije: list

    def izvorni_odlomak(self, od, do):
        """Doslovni izvorni tekst koji odgovara rasponu [od, do) normaliziranog teksta."""
        if od >= do:
            return ""
        a = self.karta[od]; b = self.karta[do - 1] + 1
        return self.izvorni[a:b]

    def u_rjecnik(self):
        return {"izvorni": self.izvorni, "normalizirani": self.tekst, "transformacije": [asdict(t) for t in self.transformacije]}


class _Pisac:
    def __init__(self, t):
        self.izv = t; self.t = t; self.karta = list(range(len(t))); self.tr = []

    def zamijeni(self, rx, novo, pravilo, vrsta, izvor, objasnjenje, zastavice=0):
        out, karta, poz = [], [], 0
        for m in re.finditer(rx, self.t, zastavice):
            n = novo(m) if callable(novo) else m.expand(novo)
            if n == m.group():
                continue
            out.append(self.t[poz:m.start()]); karta += self.karta[poz:m.start()]
            a = self.karta[m.start()] if m.start() < len(self.karta) else len(self.izv)
            b = (self.karta[m.end() - 1] + 1) if m.end() > m.start() else a
            # znakovi zamjene upućuju na odgovarajući izvorni raspon (prvi znak na početak, ostali proporcionalno)
            duz = max(1, len(n))
            karta += [(b - 1 if i == len(n) - 1 else min(b - 1, a + (i * (b - a)) // duz)) if b > a else a for i in range(len(n))]
            out.append(n); poz = m.end()
            self.tr.append(Transformacija(pravilo, vrsta, self.izv[a:b], n, a, b, izvor, objasnjenje))
        if poz:
            out.append(self.t[poz:]); karta += self.karta[poz:]
            self.t = "".join(out); self.karta = karta


def normaliziraj(tekst):
    """Pravopisna normalizacija za raščlambu. Izvorni tekst ostaje u Normalizacija.izvorni."""
    t = unicodedata.normalize("NFC", tekst)
    p = _Pisac(t)
    p.zamijeni(r"[\t\r\n\xa0]", " ", "BJELINA_ZNAK", "PRAVOPISNA", P_BJELINA, "prijelom retka ili tvrdi razmak → jedna bjelina")
    p.zamijeni(r"(?<=\d)(\s*)m\s+([23])(?!\d|,\d)", lambda m: " m" + ("²" if m.group(2) == "2" else "³"), "JEDINICA_EKSPONENT", "ZAPIS_JEDINICE",
               P_BROJ_JEDINICA, "eksponent jedinice odvojen pri prijelomu (»m 2«) → »m²«; vrijednost se ne mijenja")
    p.zamijeni(r"(?<=\d)(m²|m³)", r" \1", "BJELINA_BROJ_JEDINICA", "PRAVOPISNA", P_BROJ_JEDINICA, "bjelina između broja i oznake jedinice")
    p.zamijeni(r"(?<=\d)\s+(?:metra|metara|metar)\b", " m", "JEDINICA_RIJEC", "ZAPIS_JEDINICE", P_BROJ_JEDINICA,
               "naziv jedinice riječju (»metra«) → oznaka »m«; ista vrijednost i jedinica")
    p.zamijeni(r"\s+([;,.:])(?=\s|$)", r"\1", "BJELINA_ISPRED_ZNAKA", "PRAVOPISNA", P_BJELINA_NE, "uklonjena bjelina ispred rečeničnog znaka")
    p.zamijeni(r"\s{2,}", " ", "BJELINA_VISESTRUKA", "PRAVOPISNA", P_BJELINA, "više bjelina → jedna")
    p.zamijeni(r"^\s+|\s+$", "", "BJELINA_RUB", "PRAVOPISNA", P_BJELINA, "bjelina na početku ili kraju odlomka")
    return Normalizacija(t, p.t, p.karta, p.tr)


# ---------------------------------------------------------------- brojevi i jedinice
JEDINICE = {"m²": "m²", "m2": "m²", "m³": "m³", "m3": "m³", "m": "m", "metra": "m", "metara": "m", "metar": "m",
            "%": "%", "°": "°", "ha": "ha", "km": "km", "cm": "cm"}
RX_BROJ = re.compile(r"(?<![\w.,/])(?P<n>\d{1,3}(?:[ .]\d{3})+(?!\d)|\d+(?:,\d+)?)(?P<redni>\.(?!\d))?"
                     r"(?:\s*(?P<j>m²|m³|m2(?!\d)|m3(?!\d)|m\s[23](?!\d|,\d)|metara|metra|metar|ha|km|cm|m|%|°)(?![\wčćđšž]))?")


@dataclass
class Broj:
    izvorno: str
    vrijednost: object     # Decimal ili None
    vrsta: str             # DECIMALNI | CIJELI | REDNI | TISUCICE | TISUCICE_DVOSMISLENO
    jedinica: object
    od: int
    do: int
    izvor_pravila: str
    napomena: object = None


def _dec(s):
    return Decimal(s.replace(" ", "").replace(",", "."))


def brojevi(tekst):
    """Brojčani zapisi u tekstu, s vrstom i položajem; ne mijenja tekst. Ne vraća oznake (M1₁, NA15.2, h/2, 82/12)."""
    out = []
    for m in RX_BROJ.finditer(tekst):
        s, e = m.start(), m.end()
        prije = tekst[max(0, s - 12):s]
        if re.search(r"[A-Za-zČĆĐŠŽčćđšž]$", prije):
            continue                       # oznaka: NA2, M11
        if re.match(r"\s*/\s*\d|/", tekst[m.end("n"):m.end("n") + 2]) or re.search(r"/\s*$", prije):
            continue                       # razlomak ili broj glasila (str. 43); obrađuje oznake()
        n = m["n"]; j = m["j"]
        jed = JEDINICE.get(re.sub(r"\s", "", j)) if j else None
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+", n):
            out.append(Broj(m.group(), None, "TISUCICE_DVOSMISLENO", jed, s, e, P_TISUCICE,
                            "točka među znamenkama: tisućice (financijski zapis) ili oznaka; vrijednost se ne određuje"))
            continue
        if re.fullmatch(r"\d{1,3}(?: \d{3})+", n):
            out.append(Broj(m.group(), _dec(n), "TISUCICE", jed, s, e, P_TISUCICE)); continue
        if m["redni"] and not j:
            sljedi = tekst[e:e + 3]
            if not re.match(r"\s*$|\s+[a-zčćđšž]|\s*[,;:)]", sljedi) or re.search(r"(?:Članak|čl\.|st\.|t\.|al\.|stavk\w*|točk\w*|članak\w*)\s*$", prije, re.I) or re.match(r"\s+[a-zčćđšž]", sljedi):
                out.append(Broj(m.group(), _dec(n), "REDNI", None, s, e, P_REDNI, "točka iza broja označuje redni broj ili kraj rečenice")); continue
        vrsta = "DECIMALNI" if "," in n else "CIJELI"
        kraj = m.end("j") if j else m.end("n")
        out.append(Broj(tekst[s:kraj], _dec(n), vrsta, jed, s, kraj, P_DECIMALNI if vrsta == "DECIMALNI" else P_BROJ_JEDINICA))
    return out


def kljuc_vrijednosti(zapis):
    """Isti ključ za pravopisno različite zapise iste vrijednosti: »0,50« = »0,5«, »500 m 2« = »500m²«, »4,0 metra« = »4 m«."""
    b = [x for x in brojevi(zapis) if x.vrijednost is not None]
    if len(b) != 1:
        return None
    return (b[0].vrijednost.normalize(), b[0].jedinica)


def istovrijedno(a, b):
    ka, kb = kljuc_vrijednosti(a), kljuc_vrijednosti(b)
    return ka is not None and ka == kb


# ---------------------------------------------------------------- kratice, oznake strukture, rečenice
KRATICE = ["čl.", "st.", "t.", "al.", "br.", "tzv.", "npr.", "tj.", "itd.", "i sl.", "i dr.", "i d.", "itsl.", "str.", "sv.", "god.", "kbr.", "zk. ul.",
           "k.č.", "k. č.", "k.o.", "k. o.", "dr. sc.", "mr. sc.", "dipl.", "ing."]
POKRATE = ["NN", "SN", "PGŽ", "PPUG", "UPU", "DPU", "GUP", "PPŽ", "KPC"]


def kratice(tekst):
    out = []
    for k in sorted(KRATICE, key=len, reverse=True):
        for m in re.finditer(r"(?<![\wčćđšž])" + re.escape(k), tekst):
            if not any(o["od"] <= m.start() < o["do"] for o in out):
                out.append({"kratica": k, "od": m.start(), "do": m.end(), "izvor_pravila": P_KRATICE if k in ("br.", "st.", "t.", "npr.", "tj.", "itd.", "i sl.", "i dr.", "i d.", "itsl.", "str.", "sv.", "god.", "kbr.", "zk. ul.", "dr. sc.", "mr. sc.", "dipl.", "ing.", "tzv.") else NIJE_PRAVOPIS})
    for p in POKRATE:
        for m in re.finditer(rf"\b{p}\b", tekst):
            out.append({"kratica": p, "od": m.start(), "do": m.end(), "izvor_pravila": "Pokrate se pišu velikim slovima i ne završavaju točkom (str. 32)"})
    return sorted(out, key=lambda x: x["od"])


def oznake(tekst):
    """Strukturirane oznake: članak, stavak »(n)«, točka »a)«, alineja »- «, hijerarhijska numeracija, razlomci i brojevi glasila."""
    out = []
    for m in re.finditer(r"Članak\s+(\d{1,3})\.", tekst):
        out.append({"vrsta": "CLANAK", "broj": int(m.group(1)), "izvorno": m.group(), "od": m.start(), "do": m.end()})
    for m in re.finditer(r"(?:^|(?<=\s))\((\d+)\)(?=\s)", tekst):
        out.append({"vrsta": "STAVAK", "broj": int(m.group(1)), "izvorno": m.group(), "od": m.start(), "do": m.end()})
    for m in re.finditer(r"(?:^|(?<=[\s:]))([a-z])\)(?=\s)", tekst):
        out.append({"vrsta": "TOCKA", "slovo": m.group(1), "izvorno": m.group(), "od": m.start(), "do": m.end()})
    for m in re.finditer(r"(?:^|(?<=[:,.;)]\s)|(?<=[:,.;)]))\s*-\s+(?=[a-zčćđšž])", tekst):
        out.append({"vrsta": "ALINEJA", "izvorno": m.group(), "od": m.start(), "do": m.end()})
    for m in re.finditer(r"(?<![\d.])(\d+(?:\.\d+)+\.)(?=\s+[A-ZČĆĐŠŽ])", tekst):
        out.append({"vrsta": "HIJERARHIJSKA_NUMERACIJA", "izvorno": m.group(1), "od": m.start(), "do": m.end()})
    for m in re.finditer(r"\b([a-zA-Z])\s*/\s*(\d+)\b|(?<![\w/])(\d+)\s*/\s*(\d+)(?![\w/])", tekst):
        vr = "FORMULA" if m.group(1) else "RAZLOMAK_ILI_BROJ_GLASILA"
        out.append({"vrsta": vr, "izvorno": m.group(), "od": m.start(), "do": m.end(), "izvor_pravila": P_KOSA_BROJ})
    return sorted(out, key=lambda x: x["od"])


def recenice(tekst):
    """Rečenice: točka izvan zagrada iza koje slijedi bjelina i veliko slovo. Ne dijeli iza kratice (»čl.«, »npr.«).
    Iza rednog broja (»čl. 25. Ukoliko«) granica je dvosmislena (točka rednog broja može biti i kraj rečenice, str. 35 g):
    dijeli se, a dvosmislenost se bilježi."""
    K = kratice(tekst)
    kraj_kratice = {k["do"] - 1 for k in K}
    out, napomene, dubina, poc = [], [], 0, 0
    for i, ch in enumerate(tekst):
        if ch == "(":
            dubina += 1
        elif ch == ")":
            dubina = max(0, dubina - 1)
        elif ch == "." and dubina == 0 and re.match(r"\.\s+[A-ZČĆĐŠŽ]", tekst[i:]):
            if i in kraj_kratice:
                continue
            if re.search(r"(?:čl\.|st\.|t\.|al\.)\s*\d+$", tekst[max(0, i - 12):i]):
                napomene.append({"kod": "GRANICA_RECENICE_DVOSMISLENA", "pomak": i, "izvor_pravila": "Točka se ne piše: g) uz drugu točku (str. 35)"})
            out.append(tekst[poc:i + 1].strip()); poc = i + 1
    if tekst[poc:].strip():
        out.append(tekst[poc:].strip())
    return out, napomene


# ---------------------------------------------------------------- pravopisne napomene (bez ispravljanja)
POZNATE_RIJECI = ["rekonstruirati", "prenamijeniti", "graditi", "izgraditi", "dograditi", "nadograditi", "ukloniti", "zamijeniti",
                  "rekonstruirati", "prenamjena", "rekonstrukcija"]  # NIJE_PRAVOPIS: domenski glagoli i imenice
POZNATE_ZAMJENE = {"prenamjeniti": ("prenamijeniti", P_IJE + "; svršeni glagol: prenamijeniti, nesvršeni: prenamjenjivati")}


def pravopisne_napomene(tekst):
    """Moguće pravopisne pogreške i dvosmislenosti zapisa. Ništa se ne ispravlja: ispravak bi mogao promijeniti značenje."""
    out = []
    for m in re.finditer(r"\bslijedeć\w*", tekst, re.I):
        out.append({"kod": "SLIJEDECI_SLJEDECI", "izvorno": m.group(), "od": m.start(), "do": m.end(), "ispravljeno": False,
                    "objasnjenje": "»sljedeći« (pridjev, idući) piše se s je; »slijedeći« je od glagola slijediti. Značenje u izvoru se ne mijenja.",
                    "izvor_pravila": P_IJE})
    for m in re.finditer(r"[a-zčćđšž]{6,}", tekst):
        w = m.group().lower()
        if w in POZNATE_ZAMJENE:
            pr, izv = POZNATE_ZAMJENE[w]
            out.append({"kod": "MOGUCA_PRAVOPISNA_POGRESKA", "izvorno": m.group(), "od": m.start(), "do": m.end(), "moguce": pr,
                        "ispravljeno": False, "objasnjenje": "zapis odstupa od pravopisnog oblika; ne ispravlja se", "izvor_pravila": izv})
            continue
        if w in POZNATE_RIJECI:
            continue
        sl = difflib.get_close_matches(w, POZNATE_RIJECI, n=1, cutoff=0.86)
        if sl and w[:5] == sl[0][:5]:
            out.append({"kod": "MOGUCA_TIPOGRAFSKA_POGRESKA", "izvorno": m.group(), "od": m.start(), "do": m.end(), "moguce": sl[0],
                        "ispravljeno": False, "objasnjenje": "riječ je vrlo slična poznatoj riječi; ne ispravlja se automatski", "izvor_pravila": NIJE_PRAVOPIS})
    for m in re.finditer(r"(?<![\w/])([A-Za-zČĆĐŠŽčćđšž]{2,})/([A-Za-zČĆĐŠŽčćđšž]{2,})(?![\w/])", tekst):
        out.append({"kod": "KOSA_CRTA_RIJECI", "izvorno": m.group(), "od": m.start(), "do": m.end(), "ispravljeno": False,
                    "objasnjenje": "kosa crta između riječi može značiti »ili« ili uključenost obiju sastavnica; značenje određuje semantički sloj",
                    "izvor_pravila": P_KOSA})
    for m in re.finditer(r"\b([A-Z]{1,3}\d[\w.]*)-([A-Z]{1,3}\d[\w.]*)", tekst):
        out.append({"kod": "SPOJNICA_IZMEDJU_OZNAKA", "izvorno": m.group(), "od": m.start(), "do": m.end(), "ispravljeno": False,
                    "objasnjenje": "raspon se piše crticom s bjelinama; spojnica između oznaka može biti raspon ili složena oznaka; obuhvat se ne zaključuje",
                    "izvor_pravila": P_CRTICA})
    for m in re.finditer(r"(,?)\s*\bodnosno\b", tekst):
        out.append({"kod": "ODNOSNO_RASTAVNO" if not m.group(1) else "ODNOSNO_OBJASNJENJE", "izvorno": m.group().strip(), "od": m.start(), "do": m.end(),
                    "ispravljeno": False, "objasnjenje": "bez zareza »odnosno« = »ili«; sa zarezom = »to jest« (pravopisna uputa; u propisu ne mora biti dosljedno)",
                    "izvor_pravila": P_ODNOSNO})
    return sorted(out, key=lambda x: x["od"])


# ---------------------------------------------------------------- sučelje za morfologiju (bez pravopisnih pravila o padežima)
class MorfoloskiAnalizator:
    """Sučelje: analiziraj(riječ) → popis {'lema', 'vrsta', 'obiljezja'}. Pravopis nije izvor ovih podataka; prikladan
    bi bio lokalni morfološki rječnik ili označivač (bez plaćenih API-ja). Zadana provedba ne zna ništa i vraća []."""
    izvor = "nema"

    def analiziraj(self, rijec):
        return []

    def ista_lema(self, a, b):
        la = {x["lema"] for x in self.analiziraj(a)}; lb = {x["lema"] for x in self.analiziraj(b)}
        return bool(la & lb) if la and lb else None   # None = nepoznato, nikad pretpostavka


class PopisOblika(MorfoloskiAnalizator):
    """Ručni popis oblika domenskih naziva (npr. iz gramatika_v2.SKUPINE). Nije izveden iz pravopisa; pokriva samo navedeno."""
    izvor = NIJE_PRAVOPIS

    def __init__(self, popis):
        self.popis = popis   # {lema: [regex oblika]}

    def analiziraj(self, rijec):
        return [{"lema": l, "vrsta": "naziv", "obiljezja": None} for l, rx in self.popis.items() if any(re.fullmatch(r, rijec, re.I) for r in rx)]


def analiza(tekst):
    """Cjelovit jezični zapis odlomka: normalizacija s tragom, brojevi, kratice, oznake, napomene."""
    n = normaliziraj(tekst)
    return {"normalizacija": n.u_rjecnik(), "brojevi": [asdict(b) | {"vrijednost": str(b.vrijednost) if b.vrijednost is not None else None} for b in brojevi(n.izvorni)],
            "kratice": kratice(n.izvorni), "oznake": oznake(n.izvorni), "napomene": pravopisne_napomene(n.izvorni), "pravopis": PRAVOPIS}

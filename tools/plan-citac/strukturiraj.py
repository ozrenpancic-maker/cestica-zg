#!/usr/bin/env python3
"""EKSPERIMENT: strukturiranje uvjeta gradnje iz članaka koje je izdvojio citac.py.

Članak → točke a) b) … → alineje »- …« → prijedlozi pravila (parametar, vrijednost, jedinica, vrsta građevine,
OSNOVNO / IZNIMKA / UVJETNO, doslovni uvjet, dokazni tekst i položaj u PDF-u).

Načelo: radije ništa nego krivo. Pravilo nastaje samo kad alineja odgovara poznatom obrascu rečenice. Ako u alineji
ostane broj koji nijedan obrazac nije pokrio, ili se vrsta građevine ili upućivanje ne mogu jednoznačno odrediti,
pravila te alineje dobivaju status PREGLED. Ništa nije pravno potvrđeno.

    python3 strukturiraj.py izlaz/upu2_kornic_sn_19_2016.json --clanci 38 39 40 -o izlaz/upu2_pravila_38_40.json
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from citac import brojevi  # noqa: E402

SHEMA = "plan-citac/pravila-0.1"
N = r"\d+(?:,\d+)?"

# ---------------------------------------------------------------- vrste građevina iz uvodne rečenice članka
VRSTE_IZRAZI = [("obit-slob", r"slobodnostojeće obiteljske"), ("visobit-slob", r"slobodnostojeće višeobiteljske"),
                ("obit-dvoj", r"dvojne obiteljske"), ("obit-ugr", r"ugrađene obiteljske"),
                ("visobit-dvoj", r"dvojne višeobiteljske"), ("stamb", r"stambene građevne|stambene građevine")]


def vrste_clanka(tekst):
    m = re.match(r"Utvrđuju se uvjeti gradnje (.+?):", tekst)
    if not m:
        return None
    uvod = m.group(1)
    # »slobodnostojeće obiteljske odnosno slobodnostojeće višeobiteljske kuće«, »dvojne obiteljske, ugrađene obiteljske odnosno dvojne višeobiteljske kuće«
    v = [k for k, rx in VRSTE_IZRAZI if re.search(rx, uvod)]
    return v or None


def podskup(vrste, izraz):
    """Vrste članka na koje se odnosi izraz (»obiteljske kuće«, »višeobiteljske građevine«, »ugrađenu obiteljsku kuću« …).
    Vraća None ako izraz nije prepoznat ili ne pogađa nijednu vrstu članka."""
    if izraz is None:
        return list(vrste)
    i = izraz.lower()
    if "višeobiteljsk" in i:
        r = [v for v in vrste if v.startswith("visobit")]
    elif "ugrađen" in i and "obiteljsk" in i:
        r = [v for v in vrste if v == "obit-ugr"]
    elif "obiteljsk" in i:
        r = [v for v in vrste if v.startswith("obit-")]
    elif re.fullmatch(r"građevina|građevine|stambena građevina", i):
        r = list(vrste)
    else:
        return None
    return r or None


# ---------------------------------------------------------------- točke i alineje
def tocke(tekst):
    """Točke »a) Naslov …« (slovo iza kojega slijedi veliko slovo, nakon »:« ili ».«)."""
    poz = [m for m in re.finditer(r"(?:(?<=: )|(?<=\. )|^)([a-z])\) (?=[A-ZČĆĐŠŽ])", tekst)]
    out = []
    for i, m in enumerate(poz):
        kraj = poz[i + 1].start() if i + 1 < len(poz) else len(tekst)
        out.append({"slovo": m.group(1), "tekst": tekst[m.end():kraj].strip(), "pocetak": m.start()})
    return out


def alineje(tocka_tekst):
    """Naslov točke i alineje. Alineja počinje »- « iza interpunkcije. Podnabrajanje iza alineje koja završava
    dvotočkom (stavke s istom prvom riječi, npr. »- usporedno …«) pripaja se toj alineji i ne broji se."""
    m = re.search(r" - (?=[a-zčćđšž])", tocka_tekst)
    if not m:
        return tocka_tekst.strip(), []
    naslov = tocka_tekst[:m.start()].strip()
    stavke = [d.strip() for d in re.split(r"(?<=[,.;:]) - (?=[a-zčćđšž])", tocka_tekst[m.end():])]
    out, i = [], 0
    while i < len(stavke):
        a = stavke[i]
        if a.endswith(":") and i + 1 < len(stavke):
            prva = stavke[i + 1].split(" ")[0]
            j = i + 1
            while j < len(stavke) and stavke[j].split(" ")[0] == prva:
                a += " - " + stavke[j]; j += 1
            out.append(a); i = j; continue
        out.append(a); i += 1
    return naslov, out


def gradjevina(naslov):
    n = naslov.lower()
    if "pomoćne građevine" in n:
        return "pomocna"
    if "poljoprivredne gospodarske" in n:
        return "poljoprivredna"
    return "osnovna"


def broj(s):
    return float(s.replace(",", "."))


# ---------------------------------------------------------------- obrasci rečenica
KPC = r"na građevnim česticama smještenim unutar zone Kulturno-povijesne cjeline utvrđene u stavcima \(1\) i \(2\) članka 83\."
KPC2 = r"ako se građevna čestica nalazi unutar zone Kulturno-povijesne cjeline utvrđene u stavcima \(1\) i \(2\) članka 83\."
OTV = r"ako građevina nema otvore, prohodne terase ili otvorena stubišta prema tim međama"
KOTA = rf"pri čemu najniža kota zaravnatog terena uz građevinu može biti najviše (?P<kota>{N}) m iznad kote prirodnog terena"


def obrasci():
    """(ime, regex, funkcija koja iz podudaranja vraća popis (parametar, vrijednost, jedinica, izraz_vrste, vrsta_pravila, uvjet))."""
    O = []

    def add(ime, rx, f):
        O.append((ime, re.compile(rx), f))

    add("minC", rf"^najmanja površina građevne čestice(?: (?P<s1>obiteljske kuće|višeobiteljske kuće))? iznosi (?P<v1>{N}) m²"
                rf"(?:, odnosno (?P<s2>obiteljske kuće|višeobiteljske kuće) (?P<v2>{N}) m²)?"
                rf"(?:, a iznimno (?P<iv>{N}) m² (?P<iu>ako .+?))?[,.]?$",
        lambda m: [("minC", broj(m["v1"]), "m²", m["s1"], "OSNOVNO", None)]
        + ([("minC", broj(m["v2"]), "m²", m["s2"], "OSNOVNO", None)] if m["v2"] else [])
        + ([("minC", broj(m["iv"]), "m²", m["s1"], "IZNIMKA", m["iu"])] if m["iv"] else []))
    add("kig", rf"^najveći koeficijent izgrađenosti građevne čestice iznosi (?P<v>{N})[,.]?$",
        lambda m: [("kig", broj(m["v"]), None, None, "OSNOVNO", None)])
    add("kis", rf"^najveći koeficijent iskorištenosti iznosi (?P<v>{N})(?:, a iznimno (?P<iv>{N}) (?P<iu>ako se (?P<is>višeobiteljska kuća|građevina) gradi prema uvjetima alineje \d+\. točke [a-z]\) ovog članka))?[,.]?$",
        lambda m: [("kis", broj(m["v"]), None, None, "OSNOVNO", None)]
        + ([("kis", broj(m["iv"]), None, m["is"], "IZNIMKA", m["iu"])] if m["iv"] else []))
    add("tlMin", rf"^najmanja tlocrtna površina građevine iznosi (?P<v>{N}) m²[,.]?$",
        lambda m: [("tlMin", broj(m["v"]), "m²", None, "OSNOVNO", None)])
    add("tlMax", rf"^najveća tlocrtna površina građevine iznosi (?P<v>{N}) m²(?:, odnosno (?P<v2>{N}) m² za (?P<s2>ugrađenu obiteljsku kuću))?[,.]?$",
        lambda m: [("tlMax", broj(m["v"]), "m²", ("OSIM", m["s2"]) if m["v2"] else None, "OSNOVNO", None)]
        + ([("tlMax", broj(m["v2"]), "m²", m["s2"], "OSNOVNO", None)] if m["v2"] else []))
    add("etaze", r"^najveći broj etaža građevine iznosi (?P<v>podrum i \d nadzemne etaže|jedna nadzemna etaža)[,.]?$",
        lambda m: [("etazeMax", m["v"], None, None, "OSNOVNO", None)])
    add("visina", rf"^najveća visina građevine iznosi (?:(?P<v>{N}) m|(?P<vs>visinu osnovne građevine, ali ne više od {N} m)), {KOTA}[,.]?$",
        lambda m: [("visinaMax", broj(m["v"]) if m["v"] else m["vs"], "m" if m["v"] else None, None, "OSNOVNO", None),
                   ("kotaTerenaMax", broj(m["kota"]), "m", None, "OSNOVNO", None)])
    add("kosi", rf"^(?P<u>ako se (?P<s>višeobiteljska kuća|građevina) gradi na kosom terenu gdje je nagib prirodnog terena veći od {N}%) "
                rf"najveći broj etaža građevine iznosi (?P<e>podrum i \d nadzemne etaže od kojih je jedna obavezno suteren) te najveća visina građevine iznosi (?P<v>{N}) m, {KOTA}[,.]?$",
        lambda m: [("etazeMax", m["e"], None, m["s"], "IZNIMKA", m["u"]), ("visinaMax", broj(m["v"]), "m", m["s"], "IZNIMKA", m["u"]),
                   ("kotaTerenaMax", broj(m["kota"]), "m", m["s"], "IZNIMKA", m["u"])])
    add("gbp", rf"^najveći GBP iznosi (?P<v1>{N}) m² za građevnu česticu (?P<s1>obiteljske|višeobiteljske) građevine, odnosno (?P<v2>{N}) m² za građevnu česticu (?P<s2>obiteljske|višeobiteljske) građevine pri čemu se u navedeni GBP uračunavaju sve građevine na građevnoj čestici[,.]?$",
        lambda m: [("gbpMax", broj(m["v1"]), "m²", m["s1"] + " građevine", "OSNOVNO", None), ("gbpMax", broj(m["v2"]), "m²", m["s2"] + " građevine", "OSNOVNO", None)])
    add("gbpPom", rf"^najveći GBP iznosi (?P<v>{N}) m²[,.]?$",
        lambda m: [("gbpMax", broj(m["v"]), "m²", None, "OSNOVNO", None)])
    add("regCesta", rf"^najmanja udaljenost građevine od regulacijskog pravca prema (?P<c>javnoj|nerazvrstanoj) cesti iznosi (?P<v>{N}) m, pri čemu udaljenosti od osi prometne površine (?P<c2>javne|nerazvrstane) ceste ne može biti manja od (?P<o>{N}) m[,.]?$",
        lambda m: [] if m["c"][:4] != m["c2"][:4] else
        [("regulacija" + ("Javna" if m["c"] == "javnoj" else "Nerazvrstana"), broj(m["v"]), "m", None, "OSNOVNO", None),
         ("regulacija" + ("Javna" if m["c"] == "javnoj" else "Nerazvrstana") + "Os", broj(m["o"]), "m", None, "OSNOVNO", None)])
    add("interp", r"^(?P<u>kod interpolacije nove građevine između postojećih građevina na susjednim građevnim česticama koje su od regulacijske linije prema javnoj prometnoj površini udaljene manje od prethodno utvrđene udaljenosti), interpoliranu građevinu moguće je graditi i na manjoj udaljenosti od prethodno utvrđene, a uz uvjet da se građevni pravac uskladi s postojećim građevinama na susjednim građevnim česticama vodeći računa o lokalnim uvjetima[,.]?$",
        lambda m: [("regulacija", None, None, None, "IZNIMKA", m["u"])])
    add("regPom", rf"^najmanja udaljenost (?:poljoprivredne gospodarske )?građevine od regulacijskog pravca iznosi (?P<v>{N}) m, pri čemu udaljenost(?:i)? od osi postojeće ceste ne može biti manja od (?P<o>{N}) m"
                  rf"(?:; iznimno (?P<k>{KPC}) najmanja udaljenost (?:poljoprivredne gospodarske )?građevine od regulacijskog pravca iznosi (?P<kv>{N}) m)?"
                  rf"(?:; (?P<g>iznimno se garaže mogu graditi na regulacijskom pravcu ako je takav zahtjev uvjetovan konfiguracijom terena, odnosno kada je završna kota ravnog krova ista kao niveleta ulice, odnosno najviše do visine ogradnog zida visine {N} m kada to dozvoljavaju lokalni uvjeti, te ako se zadovolji uvjet da je garaža udaljena od osi postojeće ceste najmanje (?P<go>{N}) m))?[,.]?$",
        lambda m: [("regulacija", broj(m["v"]), "m", None, "OSNOVNO", None), ("regulacijaOs", broj(m["o"]), "m", None, "OSNOVNO", None)]
        + ([("regulacija", broj(m["kv"]), "m", None, "IZNIMKA", m["k"])] if m["kv"] else [])
        + ([("regulacija", "na regulacijskom pravcu", None, None, "IZNIMKA", m["g"]), ("regulacijaOs", broj(m["go"]), "m", None, "IZNIMKA", m["g"])] if m["g"] else []))
    add("meda", rf"^najmanja udaljenost građevine od ostalih međa građevne čestice(?:, izuzev međa na koje su prislonjene,)? iznosi (?P<v>{N}) m, a iznimno (?P<i>{N}) m (?P<u>{OTV}); "
                rf"iznimno (?P<k>{KPC}) najmanja udaljenost građevine od ostalih međa građevne čestice(?:, izuzev međa na koje su prislonjene,)? iznosi (?P<kv>pola visine građevine, ali ne manje od {N} m), a iznimno (?P<k2>{N}) m (?P<u2>{OTV}); "
                rf"iznimno se obvezna udaljenost od pola visine građevine ne mora primjenjivati (?P<u3>ako se (?P<s3>višeobiteljska građevina|građevina) gradi prema uvjetima alineje \d+\. točke [a-z]\) ovog članka)[,.]?$",
        lambda m: [("medaMin", broj(m["v"]), "m", None, "OSNOVNO", None), ("medaMin", broj(m["i"]), "m", None, "IZNIMKA", m["u"]),
                   ("medaMin", m["kv"], None, None, "IZNIMKA", m["k"]), ("medaMin", broj(m["k2"]), "m", None, "IZNIMKA", m.string[m.start("k"):m.end("u2")]),
                   ("medaMin", None, None, m["s3"], "IZNIMKA", m["u3"])])
    add("medaPom", rf"^najmanja udaljenost (?:pomoćne|poljoprivredne gospodarske) građevine od ostalih međa građevne čestice iznosi (?P<v>{N}) m, a iznimno (?P<i>{N}) m (?P<u>{KPC2})"
                   rf"(?:, odnosno (?P<u2>ako pomoćna građevina nema otvore može se graditi i na manjoj udaljenosti); ako se gradi na međi mora biti odijeljena vatrobranim zidom od susjedne građevine te nagib krova pomoćne građevine ne smije biti prema susjednoj građevnoj čestici)?[,.]?$",
        lambda m: [("medaMin", broj(m["v"]), "m", None, "OSNOVNO", None), ("medaMin", broj(m["i"]), "m", None, "IZNIMKA", m["u"])]
        + ([("medaMin", None, None, None, "IZNIMKA", m["u2"])] if m["u2"] else []))
    add("krov", rf"^krovište (?:građevine|pomoćne građevine|poljoprivredne gospodarske građevine) može biti ravno ili koso; (?P<u>ako se gradi kao koso) može biti (?:jednostrešno, )?dvostrešno ili višestrešno i mora biti s nagibom krovnih ploha između (?P<a>\d+)(?:°|˚|o) i (?P<b>\d+)(?:°|˚|o), a pokrov mora biti mediteran crijep ili kupa kanalica[,.]?$",
        lambda m: [("nagibKrovaMin", broj(m["a"]), "°", None, "UVJETNO", m["u"]), ("nagibKrovaMax", broj(m["b"]), "°", None, "UVJETNO", m["u"])])
    add("zelenilo", rf"^najmanje (?P<v>\d+)% površine građevne čestice mora se urediti visokim i niskim zelenilom; kao zelene površine obračunavaju se sve zelene površine kao i sve staze maksimalne širine (?P<s>{N}) m; (?P<u>odstupanja od ovog stavka moguća su samo u zonama starih naselja gdje se interpolacijama u postojećoj građevnoj strukturi dograđuju postojeće ili grade nove građevine)[,.]?$",
        lambda m: [("zelenilo", broj(m["v"]) / 100, "udio", None, "OSNOVNO", None), ("zelenilo", None, None, None, "IZNIMKA", m["u"]),
                   ("zelenaStazaMaxSirina", broj(m["s"]), "m", None, "OSNOVNO", None)])
    add("podzid", rf"^terase i potporni zidovi moraju se graditi tako da nisu u suprotnosti s oblikovnim obilježjima naselja; radi očuvanja izgleda padina (?P<u>na kosim građevnim česticama) uvjetuje se gradnja podzida visine do (?P<v>{N}) m[,.]?$",
        lambda m: [("podzidMax", broj(m["v"]), "m", None, "UVJETNO", m["u"])])
    add("ograda", rf"^ograda se može podizati na međi prema susjednim građevnim česticama, a prema ulici na način da je od osi postojeće ceste udaljena najmanje (?P<o>{N}) m; ulična ograda može se izvesti od kamena, betona, zelenila, metala i kombinacije ovih materijala, a u skladu s lokalnim uvjetima, do (?P<v>{N}) m visine[,.]?$",
        lambda m: [("ogradaOsMin", broj(m["o"]), "m", None, "OSNOVNO", None), ("ogradaVisinaMax", broj(m["v"]), "m", None, "OSNOVNO", None)])
    add("parking", rf"^(?P<u>kod nove gradnje ili rekonstrukcije građevine kojom se povećava broj samostalnih uporabnih cjelina ili GBP) potrebno je za promet u mirovanju osigurati minimalni broj parkirališnih/ garažnih mjesta najmanjih dimenzija (?P<d>{N}x{N} m) na građevnoj čestici uz građevinu osnovne namjene ili u okviru građevine osnovne namjene prema normativu (?P<v>\d+) mjesta po stanu[,.]?$",
        lambda m: [("parkiranjePoStanu", broj(m["v"]), "mjesta", None, "UVJETNO", m["u"]), ("parkirnoMjesto", m["d"], None, None, "UVJETNO", m["u"])])
    return O


OBRASCI = obrasci()
UPUCIVANJE = re.compile(r"^primjenjuju se odredbe iz točaka (?P<t>(?:[a-z]\),? (?:i )?)+)članka (?P<c>\d+)\.?$")
REF_ALINEJA = re.compile(r"alineje (\d+)\. točke ([a-z])\) ovog članka")


# ---------------------------------------------------------------- položaj u PDF-u
def _kljuc(s):
    return re.sub(r"[^0-9a-zčćđšž]", "", s.lower())


class Polozaji:
    """Položaj alineje u PDF-u: alineje se traže redom kroz normalizirani tekst blokova članka (bez razmaka i
    interpunkcije), pa isti početak dviju alineja ne može zavarati. Vraća blok u kojem alineja počinje."""
    def __init__(self, clanak):
        self.tekst, self.blok = "", []
        self.blokovi = [b for b in clanak["blokovi"] if "tekst" in b]
        for bi, b in enumerate(self.blokovi):
            k = _kljuc(b["tekst"]); self.tekst += k; self.blok += [bi] * len(k)
        self.kursor = 0

    def nadji(self, tekst):
        k = _kljuc(tekst)[:30]
        i = self.tekst.find(k, self.kursor)
        if len(k) < 10 or i < 0:
            return None
        self.kursor = i + len(k)
        b = self.blokovi[self.blok[i]]
        return {"stranica": b["stranica"], "stupac": b["stupac"], "okvir": b["okvir"]}


# ---------------------------------------------------------------- glavni postupak
def strukturiraj_clanak(br, c, plan):
    vrste = vrste_clanka(c["tekst"])
    rez = {"clanak": br, "vrste": vrste, "pravila": [], "upucivanja": [], "nepokriveno": [], "pregled": []}
    if not vrste:
        rez["pregled"].append({"razlog": "vrsta građevine iz uvodne rečenice članka nije prepoznata"})
        return rez
    T = tocke(c["tekst"])
    struktura, P = {}, Polozaji(c)
    for t in T:
        naslov, al = alineje(t["tekst"])
        struktura[t["slovo"]] = {"naslov": naslov, "alineje": al}
    for t in T:
        S = struktura[t["slovo"]]
        gr = gradjevina(S["naslov"])
        for ai, a in enumerate(S["alineje"], 1):
            up = UPUCIVANJE.match(a)
            if not any(r[1].match(a) for r in OBRASCI):
                P.nadji(a)
            if up:
                rez["upucivanja"].append({"tocka": t["slovo"], "alineja": ai, "upucuje_na": {"clanak": int(up["c"]), "tocke": re.findall(r"([a-z])\)", up["t"])}, "dokaz": a})
                continue
            nalaz = None
            for ime, rx, f in OBRASCI:
                m = rx.match(a)
                if m:
                    nalaz = (ime, m, f(m)); break
            vrijednosti = [b for b in brojevi(a)]
            if not nalaz:
                if vrijednosti:
                    rez["nepokriveno"].append({"tocka": t["slovo"], "alineja": ai, "dokaz": a, "brojevi": [b["literal"] for b in vrijednosti]})
                continue
            ime, m, stavke = nalaz
            izv = P.nadji(a)
            status, razlozi = "PRIJEDLOG", []
            if izv is None:
                status = "PREGLED"; razlozi.append("položaj alineje u PDF-u nije jednoznačan")
            if not stavke:
                rez["pregled"].append({"tocka": t["slovo"], "alineja": ai, "razlog": "obrazac je prepoznat, ali dijelovi rečenice nisu međusobno usklađeni", "dokaz": a})
                continue
            for (par, v, jed, izraz, vp, uvjet) in stavke:
                st, rz = status, list(razlozi)
                if isinstance(izraz, tuple) and izraz[0] == "OSIM":
                    iz = podskup(vrste, izraz[1])
                    vr = [x for x in vrste if iz is not None and x not in iz] if iz is not None else None
                else:
                    vr = podskup(vrste, izraz)
                if not vr:
                    st = "PREGLED"; rz.append(f"vrsta građevine »{izraz}« ne odgovara vrstama članka")
                ref = None
                if uvjet and uvjet not in a:
                    st = "PREGLED"; rz.append("uvjet nije doslovni odlomak alineje")
                if uvjet:
                    r = REF_ALINEJA.search(uvjet)
                    if r:
                        ca, ct = int(r.group(1)), r.group(2)
                        cilj = struktura.get(ct, {}).get("alineje", [])
                        if len(cilj) >= ca and cilj[ca - 1].startswith("ako se"):
                            ref = {"tocka": ct, "alineja": ca, "tekst": cilj[ca - 1]}
                        else:
                            st = "PREGLED"; rz.append(f"upućivanje na alineju {ca}. točke {ct}) nije jednoznačno")
                rez["pravila"].append({
                    "plan": plan, "clanak": br, "tocka": t["slovo"], "alineja": ai, "gradjevina": gr, "parametar": par,
                    "vrijednost": v, "jedinica": jed, "vrste": sorted(vr) if vr else [], "vrsta_pravila": vp,
                    "uvjet": uvjet, "uvjet_upucuje_na": ref, "obrazac": ime, "dokaz": a, "izvor": izv,
                    "status": st, "razlozi": rz, "pravno_potvrdeno": False})
            # svaki broj alineje mora biti pokriven podudaranjem obrasca (obrazac pokriva cijelu alineju)
            if m.end() < len(a.rstrip(",. ")):
                for p in rez["pravila"]:
                    if p["dokaz"] == a:
                        p["status"] = "PREGLED"; p["razlozi"].append("dio alineje nije pokriven obrascem")
    return rez


def strukturiraj(dokazi, clanci, plan):
    out = {"shema": SHEMA, "izvor_sha256": dokazi.get("sha256"), "plan": plan, "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False}
    for br in clanci:
        c = dokazi["clanci"].get(str(br))
        if not c:
            out["clanci"][str(br)] = {"pregled": [{"razlog": "članak nije izdvojen"}]}
            continue
        out["clanci"][str(br)] = strukturiraj_clanak(br, c, plan)
    sva = [p for c in out["clanci"].values() for p in c.get("pravila", [])]
    out["sazetak"] = {"prijedlozi": sum(p["status"] == "PRIJEDLOG" for p in sva), "pregled": sum(p["status"] == "PREGLED" for p in sva),
                      "nepokrivene_alineje": sum(len(c.get("nepokriveno", [])) for c in out["clanci"].values())}
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("dokazi"); p.add_argument("--clanci", type=int, nargs="+", required=True)
    p.add_argument("--plan", default="UPU 2 Kornić"); p.add_argument("-o", "--izlaz", default="pravila.json")
    p.add_argument("--csv", help="i tablica za ručni pregled (CSV, UTF-8 s BOM)")
    a = p.parse_args(argv)
    d = json.loads(Path(a.dokazi).read_text(encoding="utf-8"))
    r = strukturiraj(d, a.clanci, a.plan)
    Path(a.izlaz).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.csv:
        import csv
        polja = ["clanak", "tocka", "alineja", "gradjevina", "parametar", "vrijednost", "jedinica", "vrste", "vrsta_pravila", "uvjet",
                 "status", "razlozi", "stranica", "stupac", "dokaz", "pregledao", "ispravno_DA_NE", "napomena"]
        with open(a.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=polja); w.writeheader()
            for c in r["clanci"].values():
                for x in c.get("pravila", []):
                    w.writerow({**{k: x.get(k) for k in polja if k in x}, "vrste": " ".join(x["vrste"]), "razlozi": "; ".join(x["razlozi"]),
                                "stranica": (x["izvor"] or {}).get("stranica"), "stupac": (x["izvor"] or {}).get("stupac")})
    print(json.dumps(r["sazetak"], ensure_ascii=False))


if __name__ == "__main__":
    main()

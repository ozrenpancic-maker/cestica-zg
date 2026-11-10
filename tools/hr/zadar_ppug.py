#!/usr/bin/env python3
"""Uvjeti gradnje stambenih zgrada u građevinskom području grada Zadra iz PPUG-a Zadra (čl. 49.–64.a, 89.–99., 344.b–345.).

Izvor: Odluka o donošenju Prostornog plana uređenja Grada Zadra, pročišćeni tekst, Glasnik Grada Zadra 14/2023
(obuhvaća 4/04, 3/08, 4/08, 10/08, 16/11, 2/16, 6/16, 13/16, 4/17 i 14/19), PDF Zavoda za prostorno uređenje Zadarske županije.
Zadar nema GUP: unutar GP-a grada Zadra namjenu i gustoću (Sm, Smg, Sm1–Sm4, Ss, Sv, M1, M2 …) određuje kartografski
prikaz 5. „Razvoj i uređenje naselja – Zadar”; brojke su u tablicama čl. 90. i 98.
Aplikacija: izg = kig, kis = kisn (nadzemno), kisPodrum = kis (ukupno), gbpMax po obliku = GBPn iz tablice.
Pokretanje: python3 -I tools/hr/zadar_ppug.py → src/rules_krk.json → hrGradovi["ZADAR"].
"""
import json, os

IZVOR = {
    "naziv": "Prostorni plan uređenja Grada Zadra, odredbe (pročišćeni tekst)",
    "sn": "Glasnik Grada Zadra 14/2023",
    "url": "https://zpu-zadzup.hr/",
    "pdf": "https://zpu-zadzup.hr/download/prostorni_planovi/PPUG Zadra/Tekstualni dio/PPUG_Zadra_Pročišćeni_tekst.pdf",
    "status": "na snazi (pročišćeni tekst 14/2023, obuhvaća izmjene do 14/2019); nove izmjene i dopune su u pripremi",
    "provjera": "Čl. 49.–64.a, 89.–99. i 344.b–345. iz pročišćenog teksta (PDF Zavoda, tekst izvučen strojno; tablica zone Sm provjerena i na slici stranice), preuzeto 9. 11. 2026. Neovisna provjera (zasebna provjera koja nije sastavljala pravila), 9. 11. 2026.: oko 165 vrijednosti, bez odstupanja; dodana upozorenja za UPU u zonama Sm2 i Sm4 i zasebna zgrada u nizu.",
    "pravna_provjera": {"status": "NIJE_POTVRDENO",
                        "napomena": "Prema izvješću Gradskog vijeća od 27. 3. 2026. posljednje donesene izmjene su iz 2019. (14/19); postupak novih izmjena pokrenut je 3. 3. 2026. (Glasnik 4/2026) i nije završen. Presudom Visokog upravnog suda (NN 62/24) djelomično je ukinut čl. 152., koji se ne odnosi na ove uvjete. Zonu gustoće određuje kartografski prikaz 5. PPUG-a."}
}

def ob(minC, kig, kisn, kis, gbp=None, nap=None):
    o = {"minC": minC, "izg": kig, "kis": kisn, "kisPodrum": kis, "tlMin": 50, "tlMax": None}
    if gbp is not None: o["gbpMax"] = gbp
    if nap: o["napomena"] = nap
    return o

MEDA_SM = {"clanak": "55.", "min": 3, "opis": "najmanje 3 m od međe (zona manje gustoće); kod dvojnih i nizova za krajnja bočna pročelja",
           "opisIznimka": "U izgrađenom dijelu iznimno manje, po načelu reciprociteta sa susjednom građevinom, ali najmanje 1 m i bez otvora prema susjedu (čl. 55.).",
           "txt": "Udaljenost zgrade od međe ne može biti manja od 3 m u zonama manje gustoće, odnosno 5 m u ostalim zonama."}
MEDA_5 = dict(MEDA_SM, min=5, opis="najmanje 5 m od međe (zone srednje i veće gustoće, mješovita namjena)")
REG = {"clanak": "51.", "ostale": 5, "opis": "najmanje 5 m od regulacijskog pravca (kopnena naselja); kod interpolacije prema postojećim susjednim zgradama",
       "txt": "Udaljenost građevine od regulacijskog pravca u kopnenim naseljima iznosi min. 5,0 m"}
def zel(cl, m): return {"clanak": cl, "min": m, "txt": f"min. zelenila na parceli (%) {int(m*100)}"}

def T(naziv, opis, cl, et, vis, slob=None, dvoj=None, ugr=None, txt=None, visOpis=None):
    t = {"naziv": naziv, "opis": opis, "clanak": cl, "gbpMax": None, "etaze": et, "visina": vis,
         "visinaOpis": visOpis or (f"{str(vis).replace('.', ',')} m" if vis else "nije propisana"), "txt": txt or {}}
    obl = []
    if slob: t["slob"] = slob; obl.append(["slob", "samostojeća"])
    if dvoj: t["dvoj"] = dvoj; obl.append(["dvoj", "dvojna"])
    if ugr: t["ugr"] = ugr; obl.append(["ugr", "u nizu"])
    t["oblici"] = obl
    return t

TXT_SM = {"minC": "min. površina građ. čestice (m2) 350 450 250 200", "izg": "max. koef. izgrađenosti (kig) 0,30 0,30 0,30 0,40",
          "kis": "max. koef. iskoristivosti nadzemno (kisn) 0,90 0.90 0,90 0,80; max. koef. iskoristivosti (k is) 1,2 1,5 1,2 1,0",
          "gbp": "max. bruto površina GBPn (m2) nadzemno 400 600 250 200", "visina": "max. visina zgrade (m) 10 10 10 7,5", "etaze": "broj nadzemnih etaža 4 4 4 3"}
NAP_SM = ["Najmanja širina čestice na mjestu građevnog pravca: samostojeća 12 m, dvojna 8 m, niz 6 m (čl. 90.).",
          "Zgrada u nizu: visina do 7,5 m i 3 nadzemne etaže, najviše 5 jedinica u nizu (čl. 90.).",
          "Za česticu veću od 2000 m² GBPn se povećava za kisn 0,15 na dio iznad 2000 m² (čl. 90.).",
          "Parkiranje: 2 mjesta po stanu na čestici (čl. 90.)."]
def sm(kig_sd=0.30):
    a = T("Stambena zgrada (do 3 stana)", "samostojeća do 3 stana, dvojna do 2 stana (čl. 90.)", "90.",
          "4 nadzemne etaže", 10.0,
          ob(350, kig_sd, 0.90, 1.2, 400), ob(250, kig_sd, 0.90, 1.2, 250), None, TXT_SM)
    n = T("Zgrada u nizu", "1 stan po jedinici, najviše 5 jedinica u nizu (čl. 90.)", "90.", "3 nadzemne etaže", 7.5,
          ugr=ob(200, 0.40, 0.80, 1.0, 200), txt=TXT_SM)
    b = T("Samostojeća zgrada na čestici od 450 m²", "drugi stupac za samostojeću zgradu u tablici čl. 90. (broj stanova nije propisan)", "90.",
          "4 nadzemne etaže", 10.0, ob(450, kig_sd, 0.90, 1.5, 600,
          "Tablica čl. 90. za samostojeću zgradu ima dva stupca bez naziva; ovaj (450 m², GBPn 600 m², kis 1,5) nema propisan broj stanova. Što razlikuje stupce, provjeri u lokacijskoj informaciji."), txt=TXT_SM)
    return {"stamb": a, "stamb450": b, "niz": n}

ZONE, ZSET = [], {}
def dodaj(k, naziv, cfg): ZONE.append([k, naziv]); ZSET[k] = cfg
def bez(k, naziv, msg): ZONE.append([k, naziv]); ZSET[k] = {"tipovi": None, "drugaZona": msg + " Mjerodavna je lokacijska informacija Grada Zadra."}

dodaj("Sm", "Sm · stambena zona manje gustoće", {"tipovi": sm(), "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2), "napomene": NAP_SM})
dodaj("Smg", "Smg · stambena zona manje gustoće (kig 0,4)", {"tipovi": sm(0.40), "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2),
      "napomene": ["Zona Smg: vrijede uvjeti zone Sm, osim kig-a koji za nove samostojeće i dvojne zgrade može biti najviše 0,4 (čl. 90.)."] + NAP_SM})

TXT_SMX = {"izg": "max. koef. izgrađenosti (k ig) … 0,3 (u nizu 0,4)", "kis": "max. koef. iskoristivosti nadzemno (k isn) 0,6; max. koef. iskoristivosti (k is) 0,9",
           "visina": "max. visina zgrade (m) 7", "gbp": "max. bruto površina GBP (m2) nadzemno 600 (dvojna 300, niz 200)"}
def smx(minS, minD, niz=False):
    t = T("Stambena zgrada", "samostojeća do 2 stana, dvojna i u nizu 1 stan (čl. 90., zone Sm1–Sm4)", "90.", "broj etaža nije propisan (visina 7 m)", 7.0,
          ob(minS, 0.30, 0.60, 0.90, 600), ob(minD, 0.30, 0.60, 0.90, 300), ob(200, 0.40, 0.60, 0.90, 200) if niz else None, dict(TXT_SMX, minC=f"min. površina građevne čestice (m2) {minS} (dvojna {minD}{', niz 200' if niz else ''})"))
    return {"stamb": t}
NAP_SMX = ["Zone Sm2 i Sm3 imaju posebne uvjete radi zaštite vizura, Sm4 zbog prometne povezanosti (čl. 90.).", "Najmanja širina čestice: samostojeća 12 m, dvojna 8 m, niz 6 m (čl. 90.).",
           "Parkiranje: 2 mjesta po stanu i poslovnom prostoru na čestici (čl. 90.)."]
UPU_SM = lambda b, n: [f"U tablici čl. 90. uz ovu zonu stoji broj plana {b}; u čl. 345. pod tim brojem je {n}. Ako čestica leži u obuhvatu tog UPU-a, gradi se prema UPU-u (a dok nije donesen, ne mogu se ishoditi akti za gradnju); provjeri na karti 6. i u lokacijskoj informaciji."]
dodaj("Sm1", "Sm1 · Musapstan (kuće ladanjskog tipa)", {"tipovi": {"stamb": T("Kuća ladanjskog tipa (»stancija«)", "1 stan, s mogućim rekreacijskim i ugostiteljskim uslugama (čl. 90.)", "90.",
      "broj etaža nije propisan (visina 7 m)", 7.0, {"minC": 4000, "izg": 0.15, "kis": None, "kisPodrum": None, "tlMin": 50, "tlMax": None}, txt={"minC": "min. površina građevne čestice (m2) 4000", "izg": "max. koef. izgrađenosti (k ig) 0,15", "gbp": "max. bruto površina GBP (m2) nadzemno 800"})},
      "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.5), "napomene": ["Zona Sm1 uz rekreacijsku zonu šume Musapstan: kuće ladanjskog tipa (»stancija«), GBP nadzemno do 800 m², 1 stan (čl. 90.)."]})
ZSET["Sm1"]["tipovi"]["stamb"]["gbpMax"] = 800
dodaj("Sm2", "Sm2 · Donji Brig", {"tipovi": smx(500, 250), "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2), "napomene": NAP_SMX, "upozorenja": UPU_SM(9, "»stambena zona Gaj II« (UPU obvezan)")})
dodaj("Sm3", "Sm3 · Vidikovac", {"tipovi": smx(400, 200), "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2), "napomene": NAP_SMX})
dodaj("Sm4", "Sm4 · Karma", {"tipovi": smx(350, 200, niz=True), "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2), "napomene": NAP_SMX, "upozorenja": UPU_SM(66, "»UPU stambene zone Karma«")})

def ss(big=False):
    return {"stamb": T("Stambena zgrada (srednja gustoća)", "višestambena zgrada, zona Ss (čl. 90.)", "90.", "7 nadzemnih etaža" if big else "5 nadzemnih etaža", 21.0 if big else 13.0,
            ob(2000 if big else 1000, 0.30, 1.8 if big else 1.2, 4.0 if big else 3.0),
            txt={"minC": "min. površina građevne čestice (m2) 1000 2000", "izg": "max. koef. izgrađenosti (kig) 0,30 0,30",
                 "kis": "max. koef. iskoristivosti (k is) 3,0 4,0; max. koef. iskoristivosti nadzemno (kisn) 1,2 1,8", "visina": "max. visina zgrade (m) 13 21", "etaze": "broj nadzemnih etaža 5 7"})}
dodaj("Ss", "Ss · stambena zona srednje gustoće", {"tipovi": ss(), "meda": MEDA_5, "regulacija": REG, "zelenilo": zel("90.", 0.2),
      "napomene": ["Uz zelenilo 40 % i više od pola parkirališnih mjesta ispod tla kisn se može povećati za 10 % (čl. 90.).", "Parkiranje: 2 mjesta na 100 m² bruto stambenog dijela (čl. 90.)."],
      "varijante": [{"minA": 2000, "opis": "čestica od 2000 m²: 7 nadzemnih etaža, 21 m, kisn 1,8, kis 4,0", "tipovi": ss(True)}]})
dodaj("Sv", "Sv · stambena zona veće gustoće", {"tipovi": {"stamb": T("Stambena zgrada (veća gustoća)", "višestambena zgrada, zona Sv (čl. 90.)", "90.", "10 nadzemnih etaža", 30.0,
      ob(2000, 0.25, 2.5, 5.0), txt={"minC": "min. površina građevne čestice (m2) 2000", "izg": "max. koef. izgrađenosti (kig) 0,25", "kis": "max. koef. iskoristivosti (kis) 5,0 max. koef. iskoristivosti nadzemno (kisn) 2,5", "visina": "max. visina zgrade (m) 30", "etaze": "broj nadzemnih etaža 10"})},
      "meda": MEDA_5, "regulacija": REG, "zelenilo": zel("90.", 0.3), "napomene": ["Parkiranje: 2 mjesta na 100 m² bruto stambenog dijela, do 5 podzemnih etaža; najmanje 20 % zelenila uređuje se kao dječje igralište (čl. 90.)."]})
dodaj("M1", "M1 · mješovita, pretežito stambena (ostale pojedinačne čestice)", {"tipovi": {"stamb": T("Stambena ili stambeno-poslovna zgrada", "pojedinačna čestica u zoni M1 izvan zona iz tablice čl. 98.", "98.",
      "broj etaža nije propisan (visina 12 m)", 12.0, ob(600, 0.30, 1.2, 2.5), txt={"minC": "Ostale pojedinač. čestice 0,3 - 600 12 1,2 2,5", "izg": "max. koef. izgrađ. kig … 0,3", "kis": "max. koeficijent iskoristivosti nadzemno … 1,2; max. koeficijent iskoristivosti (kis) 2,5", "visina": "max. visina zgrade (m) 12"})},
      "meda": dict(MEDA_5, clanak="98.", opis="najmanje 5 m od granice čestice (zona M1)", txt="Minimalna udaljenost zgrada (unutar zone M1) od granice građevne čestice je 5,0 metara."),
      "regulacija": REG, "zelenilo": zel("98.", 0.2),
      "napomene": ["Pojedinačne čestice na Poluotoku: kig 0,4, uz konzervatorske uvjete (čl. 98.).", "Čl. 98. kaže i da koeficijent izgrađenosti u zonama iz tablica »nije ograničen«, a u istoj tablici za ostale pojedinačne čestice navodi kig 0,3; aplikacija primjenjuje 0,3.", "Za zone iz tablice čl. 98. (Suha, Put Dikla, Vitrenjak, Dražanica, Žmirići II, Bregdetti, Biogradska, Vidikovac, Smiljevac …) vrijede ukupni GBP zone i UPU; ovaj izračun ne vrijedi."]})

for k, n, m in [
    ("M2", "M2 · mješovita, pretežito poslovna", "Zona M2: osnovna namjena su poslovne, javne i društvene zgrade; za ostale pojedinačne čestice čestica 1000 m², visina 15 m, kisn 1,5, kis 2,0, kig nije ograničen (čl. 99.). Izračun za stambenu kuću nije obrađen."),
    ("MR", "MR · mješovita namjena – razvoj (Gaj, Žmirići, Čubrijan, Musapstan)", "Zona MR: gradnja tek prema UPU-u (čl. 101. i 345.)."),
    ("jezgra", "jezgra naselja (Poluotok i druge jezgre)", "Jezgre naselja (kartografski prikaz 4.): gradnja i interpolacija prema posebnim uvjetima jezgre i konzervatorskim uvjetima (čl. 65.–67.); izračun nije obrađen."),
    ("UPU", "područje UPU-a ili DPU-a (karta 6.)", "Za područja iz čl. 345. (npr. Diklo, Gaj, Vidikovac, Smiljevac, Ričina, Dračevac) vrijedi UPU ili DPU, a za ona u kojima UPU još nije donesen ne mogu se ishoditi akti za gradnju (čl. 345.)."),
    ("ostalo", "druga namjena (D, K, T, R, Z, I …) ili ostala naselja", "Za ovu namjenu ili za ostala naselja Grada Zadra (Petrčane, Kožino, Crno, otoci) uvjeti za stambenu zgradu ovdje nisu obrađeni."),
]:
    bez(k, n, m)

ZADAR = {
    "kod": "PPUG Zadar", "izvor": IZVOR,
    "obuhvat": [15.18, 44.075, 15.32, 44.15],
    "upozorenje": "Zona gustoće se ne očitava automatski: odaberi je prema kartografskom prikazu 5. „Razvoj i uređenje naselja – Zadar” PPUG-a (Sm, Smg, Sm1–Sm4, Ss, Sv, M1 …) i provjeri vrijedi li na čestici UPU ili DPU (karta 6.); potvrđuje ih lokacijska informacija.",
    "oblici": [["slob", "samostojeća"], ["dvoj", "dvojna"], ["ugr", "u nizu"]],
    "kisUkupni": False,
    "zone": ZONE, "zoneSet": ZSET, "zonaLabel": "Zona namjene i gustoće (karta 5.)",
    "zonaNapomena": "Unutar GP-a grada Zadra stambene zone su podijeljene prema gustoći (Sm, Smg, Sm1–Sm4 manja, Ss srednja, Sv veća), uz mješovite zone M1 i M2 (čl. 89.a i 90.).",
    "drugaZona": "Za odabranu zonu uvjeti za stambenu zgradu nisu obrađeni.",
    "tipovi": ZSET["Sm"]["tipovi"], "meda": MEDA_SM, "regulacija": REG, "zelenilo": zel("90.", 0.2),
    "pristup": {"napomena": "Čestica mora imati neposredan pristup na prometnu površinu; u izgrađenom dijelu zone manje gustoće iznimno preko druge čestice uz upisanu služnost (čl. 50.). Parkiranje 2 mjesta po stanu (čl. 90.)."},
    "napomene": ["Najmanja tlocrtna površina stambene zgrade 50 m²; na čestici jedna zgrada i pomoćne građevine (čl. 49.).",
                 "Koeficijenti uključuju glavnu i sve pomoćne građevine na čestici, osim nenatkrivenih bazena (čl. 64.).",
                 "Potkrovlje: nadozid najviše 1,2 m; uz ravni krov moguća uvučena krovna etaža (nadgrađe) do 3,5 m (čl. 58.)."],
}

# Rekonstrukcija postojećih zgrada (čl. 64.b, 66., 90., 151.–154., 264., 363.–365.; pročišćeni tekst Glasnik Grada Zadra 14/2023, tekst izvučen iz PDF-a Zavoda 10. 11. 2026.)
SVE_Z, POST_Z = ["rek", "dogr", "nadogr", "zamj"], ["rek", "dogr", "nadogr"]
ZADAR["rekonstrukcija"] = [
    {"zahvati": SVE_Z, "clanak": "64.b", "opis": "Uvjeti za novu gradnju primjenjuju se i na rekonstrukciju ako plan za nju ne propisuje posebne uvjete.",
     "txt": "Uvjeti za gradnju novih građevina primjenjuju se i u slučajevima rekonstrukcije ukoliko Planom nisu posebno propisani"},
    {"zahvati": POST_Z, "clanak": "152.", "opis": "Čestica manja od propisanog minimuma: rekonstrukcija samo u postojećim gabaritima; prizemna zgrada može se nadograditi za jednu etažu neovisno o kig-u, uz ostale uvjete zone.",
     "txt": "kada je površina građevna čestica manja od Planom propisanog minimuma za novu gradnju, rekonstrukcija je dozvoljena samo u postojećim gabaritima građevine, iznimno, za prizemne građevine moguća je nadogradnja jedne etaže neovisno o najvećem dopuštenom koeficijentu izgrađenosti uz poštivanje ostalih uvjeta propisanih Planom za predmetnu zonu."},
    {"zahvati": POST_Z, "clanak": "152.", "opis": "Zgrada bliže međi od propisanog: rekonstrukcija prema zatečenoj udaljenosti, uz suglasnost susjeda (osim kod reciprociteta) i bez novih otvora prema susjedu; bliže regulacijskom pravcu: prema zatečenoj udaljenosti."},
    {"zahvati": POST_Z, "clanak": "152.", "opis": "Kig veći od propisanog: rekonstrukcija dopuštena uz ostale uvjete zone; uvjeti se ispunjavaju kumulativno (za postojeći i za rekonstruirani dio). Zgrada tipa zone manje gustoće u drugoj zoni rekonstruira se prema uvjetima zone Sm."},
    {"zahvati": POST_Z, "clanak": "153.", "opis": "Postojeće zgrade koje premašuju dopušteni kig, kis ili nadzemni GBP zadržavaju se u postojećim gabaritima i ne mogu se povećavati; iznimno u zonama Ss i Sv rekonstrukcija krovišta ili nadogradnja potkrovlja za jednu stambenu jedinicu do najveće visine zone."},
    {"zahvati": POST_Z, "clanak": "151.", "opis": "Otočna naselja (zone Sm): postojeće samostojeće i dvojne zgrade rekonstruiraju se prema uvjetima plana, a postojeći nizovi samo u postojećim gabaritima."},
    {"zahvati": POST_Z, "clanak": "264.", "opis": "Parkiranje: na Poluotoku izvan jezgre rekonstrukcija bez promjene gabarita ne traži parkirna mjesta; kod povećanja GBP-a na Poluotoku i u svim jezgrama naselja obveza se odnosi samo na povećani dio, a samo na Poluotoku mjesta ne moraju biti na vlastitoj čestici."},
    {"zahvati": SVE_Z, "clanak": "66.", "opis": "U jezgrama naselja rekonstrukcija ili zamjenska zgrada dopuštena je i kad čestica nema najmanju površinu, udaljenost od susjeda ili kig, ako se zadrže zatečeni tlocrtni gabariti; iznimno dogradnja etaža ili veća visina kad se slijedi visina susjednih zgrada.",
     "txt": "U slučajevima rekonstrukcije ili gradnje zamjenske građevine dozvoljava se gradnja i kada nisu ispunjeni uvjeti minimalne površine građevinske čestice, udaljenosti od susjeda ili koeficijenta izgrađenosti, pod uvjetom da se zadrže zatečeni tlocrtni gabariti građevine."},
    {"zahvati": ["nadogr"], "clanak": "90.", "opis": "Postojeća dvojna zgrada ili niz u zoni Sm: nadogradnja radi poravnanja s visinom susjedne zgrade i/ili povećanje na najviše dva stana."},
    {"zahvati": SVE_Z, "clanak": "154.", "opis": "Na području s obvezom UPU-a do njegova donošenja dopuštena je samo nužna rekonstrukcija (čl. 364.)."},
    {"zahvati": POST_Z, "clanak": "363.–364.", "opis": "Zgrada čija je namjena protivna planu: samo nužna rekonstrukcija — obnova krova i dotrajalih dijelova unutar postojećih gabarita, bez promjene volumena i vanjskog oblika.",
     "txt": "Pod nužnom rekonstrukcijom podrazumijeva se obnova krova i svih dotrajalih dijelova zgrade unutar postojećih gabarita bez promjene volumena i vanjskog oblika građevine."},
    {"zahvati": ["rek"], "clanak": "365.", "opis": "Zatečene ruševine unutar građevinskog područja mogu se rekonstruirati pod istim uvjetima kao postojeće zgrade u toj zoni."},
]
for z in ZSET.values():
    if z.get("tipovi"): z["napomene"] = z["napomene"] + ZADAR["napomene"]

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("hrGradovi", {})["ZADAR"] = ZADAR
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zone", len(ZONE), "s izračunom", sum(1 for z in ZSET.values() if z.get("tipovi")))

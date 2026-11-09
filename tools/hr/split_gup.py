#!/usr/bin/env python3
"""Uvjeti gradnje niskih stambenih građevina iz GUP-a Splita (urbana pravila, čl. 49.–75.).

Izvor: Odredbe za provođenje GUP-a Splita – pročišćeni tekst, Službeni glasnik Grada Splita 55/2014
(split.hr, „Planovi na snazi” → GUP Splita); uključuje i ciljane izmjene za Trsteničku uvalu (41/2014).
GUP Splita ne razlikuje obiteljsku i višeobiteljsku kuću nego nisku građevinu (do P+3) prema pokazateljima:
Pp min (najmanja čestica), kig (nadzemni), kigP (podzemni), kis (ukupni), kisN (nadzemni), E (etaže).
Aplikacija: izg = kig, kis = kisN (nadzemni GBP), kisPodrum = kis (ukupni GBP s podzemnim etažama).
Visina iz čl. 49. (opće odredbe): P+2 do 10,5 m, P+3 13,5 m, P+4 16,5 m (3 m po etaži, „itd.”), sa suterenom 2 m više.
Pokretanje: python3 -I tools/hr/split_gup.py  → upisuje src/rules_krk.json → hrGradovi["SPLIT"].
"""
import json, os

IZVOR = {
    "naziv": "Generalni urbanistički plan Splita, odredbe za provođenje (pročišćeni tekst)",
    "sn": "Službeni glasnik Grada Splita 55/2014",
    "url": "https://split.hr/strateski-dokumenti/prostorno-planska-dokumentacija/planovi-na-snazi/gup-splita",
    "pdf": "https://split.hr/DesktopModules/Bring2mind/DMX/API/Entries/Download?language=hr-HR&Command=Core_Download&EntryId=6130&PortalId=0",
    "status": "na snazi (pročišćeni tekst 55/2014, uključuje i ciljane izmjene za Trsteničku uvalu 41/2014; izmjene i dopune GUP-a u izradi, prijedlog 2024.)",
    "provjera": "Čl. 49.–75. iz pročišćenog teksta (PDF sa split.hr, tekst izvučen strojno; dvostupčani prijelom), preuzeto 9. 11. 2026. Neovisna provjera (zasebna provjera koja nije sastavljala pravila), 9. 11. 2026.: oko 170 vrijednosti, brojke bez odstupanja; ispravljeni navod općih odredbi (čl. 49.) i etaže dvojnih građevina u varijantama.",
    "pravna_provjera": {"status": "NIJE_POTVRDENO",
                        "napomena": "Pročišćeni tekst iz 2014.; kasnije ciljane izmjene i izmjene u izradi nisu uspoređene. Urbano pravilo za česticu određuje kartografski prikaz „Urbana pravila” GUP-a."}
}
VIS = {2: 10.5, 3: 13.5, 4: 16.5}
def et(n): return f"podrum, prizemlje i {n} kata (Po+P+{n})"
def ob(minC, kig, kisN, kis, tl=None, nap=None):
    o = {"minC": minC, "izg": kig, "kis": kisN, "kisPodrum": kis, "tlMin": None, "tlMax": tl}
    if nap: o["napomena"] = nap
    return o
DV_NAP = "Najveća tlocrtna površina dvojne građevine je 300 m² ukupno (obje polovice zajedno), pa je za jednu polovicu manja."

def tip(cl, n, slob, dvoj, txt, gbp=None):
    t = {"naziv": "Niska stambena građevina" if n <= 3 else "Srednja stambena građevina", "opis": f"stambena ili stambeno-poslovna, najviše Po+P+{n} (čl. 49. i {cl})", "clanak": cl,
         "gbpMax": gbp, "etaze": et(n), "visina": VIS[n], "visinaOpis": f"{str(VIS[n]).replace('.', ',')} m (sa suterenom {str(VIS[n]+2).replace('.', ',')} m)" + ("" if n == 2 else "; plan izričito navodi visine do P+2 (10,5 m), za više etaža »itd.«, pa je visina izvedena s 3 m po etaži"),
         "slob": slob, "txt": txt}
    if dvoj: t["dvoj"] = dvoj
    t["oblici"] = [["slob", "slobodnostojeća"]] + ([["dvoj", "dvojna"]] if dvoj else [])
    return {"stamb": t}

MEDA_OPCA = {"clanak": "49.", "min": 3, "opis": "u neizgrađenom dijelu najmanje 3 m od međe; u izgrađenom dijelu može i manje, prema lokalnim uvjetima",
             "opisIznimka": "", "txt": "U neizgrađenom dijelu udaljenost građevina od međe je najmanje 3 m. … U izgrađenim dijelovima udaljenost građevina od međe može biti manja od 3 m, u skladu s lokalnim uvjetima."}
def meda3(cl): return {"clanak": cl, "min": 3, "opis": "najmanje 3 m od granica čestice", "opisIznimka": "", "txt": "minimalna udaljenost građevine od granica čestice 3,0 m"}
REG_OPCA = {"clanak": "49.", "ostale": 5, "opis": "u izgrađenom dijelu na postojećem građevnom pravcu u potezu; inače 5 m od pristupne ulice (sabirna 5 m, gradska ulica 10 m, magistrala 20 m)",
            "txt": "pristupna ulica i druge javno prometne površine 5,0 m … U izgrađenom dijelu … građevina se postavlja … na dominantnom postojećem građevnom pravcu"}
def reg4(cl, neiz=False): return {"clanak": cl, "ostale": 4, "razvrstane": 5 if neiz else None, "opis": "usklađeno s postojećim građevinama u potezu, ali najmanje 4 m" + (" (u neizgrađenom dijelu najmanje 5 m)" if neiz else ""),
                                  "txt": "udaljenost građevine (građevni pravac) od ulice odnosno regulacijskog pravca mora biti usklađena s prevladavajućom istom udaljenošću postojećih građevina u uličnom potezu ali ne manja od 4 m"}
def zel(cl, m, t): return {"clanak": cl, "min": m, "txt": t}
ZEL30 = "minimalno 30% površine građevne čestice obraditi kao zelenu površinu, uključujući visoko i nisko zelenilo"

ZONE, ZSET = [], {}
def dodaj(k, naziv, cfg): ZONE.append([k, f"{k} · {naziv}"]); ZSET[k] = cfg
def zona(t, meda, reg, zl, nap, upoz=None, var=None):
    z = {"tipovi": t, "meda": meda, "regulacija": reg, "zelenilo": zl, "napomene": nap}
    if upoz: z["upozorenja"] = upoz
    if var: z["varijante"] = var
    return z
def bez(k, naziv, msg): ZONE.append([k, f"{k} · {naziv}"]); ZSET[k] = {"tipovi": None, "drugaZona": msg + " Mjerodavna je lokacijska informacija Grada Splita."}

# 1.3 (čl. 52.)
dodaj("1.3", "zaštićeni dijelovi niske gradnje", zona(
    tip("52.", 2, ob(500, 0.25, 0.75, 1.75, 250), ob(250, 0.25, 0.75, 1.50, 300, DV_NAP),
        {"minC": "za novu izgradnju slobodno stojećih građevina Pp min =500 m2 … za novu izgradnju dvojnih građevina Pp min =250 m2",
         "izg": "k ig =0,25", "kis": "k is =1,75, k is N =0,75 (dvojne: k is =1,50, k is N =0,75)", "etaze": "E=Po+P+2",
         "tl": "maksimalna tlocrtna površina pod nadzemnim dijelom građevine za slobodnostojeće građevine 250 m2 … dvojne građevine ukupno 300 m2"}),
    MEDA_OPCA, reg4("52."), zel("52.", 0.3, ZEL30),
    ["Najmanja širina čestice prema ulici: slobodnostojeća 14 m, dvojna 10 m; podzemna izgrađenost (kigP) najviše 0,5 (čl. 52.).",
     "Nova čestica između dvije izgrađene: najmanje 300 m², kig 0,25, kisN 0,75, kis 1,5, Po+P+2 (čl. 52.).",
     "Gdje to dopušta prosječna visina u uličnom potezu: slobodnostojeća na čestici od 800 m², Po+P+3, obvezno ravni krov, kisN 1,0, tlocrt do 300 m² (čl. 52.); aplikacija to ne pretpostavlja."],
    ["Zaštićena povijesna cjelina: za zahvate u zonama A i B trebaju posebni uvjeti i suglasnost konzervatora, u zoni C očitovanje konzervatora (čl. 49.)."]))

# 1.5 (čl. 54.)
dodaj("1.5", "vrijedna niska izgradnja u obalnom području (Bačvice, Meje)", zona(
    tip("54.", 2, ob(600, 0.25, 0.75, 1.50, 300), ob(250, 0.25, 0.75, 1.50, 300, DV_NAP),
        {"minC": "slobodno stojećih građevina Pp min =600 m2 … dvojnih građevina Pp min =250 m2", "izg": "k ig =0,25 (nadzemni)",
         "kis": "k is =1,50, k is N=0,75", "etaze": "E=Po+P+2", "tl": "maksimalna tlocrtna površina slobodno stojeće građevine 300 m2 … dvojne građevine ukupno 300 m2"}),
    MEDA_OPCA, REG_OPCA, zel("54.", None, ""),
    ["Najmanja širina čestice prema ulici: slobodnostojeća 14 m, dvojna 10 m; podzemna izgrađenost najviše 0,5 (čl. 54.).",
     "Nadzemna gradnja u vrtovima i dvorištima unutar bloka nije moguća; velike okućnice ne mogu se prenamijeniti u građevne čestice (čl. 54.).",
     "Gdje to dopušta prosječna visina u uličnom potezu: slobodnostojeća na čestici od 800 m², Po+P+3, kisN 1,0, kis 2,0 (čl. 54.); uz Jadransku ulicu na Bačvicama iznimno kig 0,40, kisN 1,6 uz suglasnost konzervatora; aplikacija to ne pretpostavlja.",
     "Pravilo 1.5 ne propisuje postotak zelenila."],
    ["Vrijedno obalno područje: zadržavaju se postojeći regulacijski i građevni pravci, čuvaju se stabla i kameni ogradni zidovi (čl. 54.)."]))

# 2.1a (čl. 64.)
dodaj("2.1a", "dovršena naselja u kontaktnoj zoni Marjana", zona(
    tip("64.", 2, dict(ob(400, 0.25, 0.75, 1.50), gbpMax=750), ob(250, 0.25, 0.75, 1.50, 300, DV_NAP),
        {"minC": "Pp min =400 m2 … (dvojne) Pp min =250 m2", "izg": "k ig =0,25", "kis": "k is =1,50, k is N=0,75", "gbp": "maksimalni BRPN=750 m2 (za novu izgradnju i zamjenu slobodnostojeće)", "etaze": "E=Po+P+2"}),
    MEDA_OPCA, REG_OPCA, zel("64.", None, ""),
    ["Najmanja širina čestice dvojne građevine prema ulici 10 m (čl. 64.).",
     "Postojeće legalne dvojne građevine mogu se rekonstruirati ili izjednačiti po visini: kig 0,35, kigP 0,5, kisN 1,05, kis 1,55, Po+P+3 (čl. 64.)."],
    ["Pravilo 2.1a: moguća je isključivo zamjena postojećih građevina koje nisu zaštićene te rekonstrukcija u postojećim gabaritima (čl. 64.); izračun vrijedi samo za zamjensku građevinu."]))

# 2.3 (čl. 66.) s varijantama prema površini čestice
def t23(n, minC, kisN, kis):
    return tip("66.", n, ob(minC, 0.30, kisN, kis), ob(300, 0.30, 0.90, 1.50, 300, DV_NAP),
               {"minC": "Pp min =500 m2 … Pp min =800 m2 … Pp min =1200 m2 (dvojne 300 m2)", "izg": "k ig =0,30",
                "kis": "500 m2: k is =2,00, k is N=0,90, E=Po+P+2; 800 m2: k is =2,50, k is N=1,20, E=Po+P+3; 1200 m2: k is =3,00, k is N=1,50, E=Po+P+4",
                "etaze": f"E=Po+P+{n}"})
dodaj("2.3", "pretežito dovršeni prostori mješovite gradnje", zona(
    t23(2, 500, 0.90, 2.00), MEDA_OPCA, REG_OPCA,
    zel("66.", 0.2, "minimalno 20% površine građevne čestice obraditi kao zelenu površinu, uključujući visoko i nisko zelenilo"),
    ["Prema površini čestice: od 800 m² vrijedi Po+P+3 (kisN 1,2), od 1200 m² Po+P+4 (kisN 1,5) (čl. 66.).",
     "Nova čestica između dvije izgrađene: najmanje 300 m², kig 0,25, kisN 0,75, kis 1,5, Po+P+2 (čl. 66.).", "Varijante za veću česticu vrijede za slobodnostojeću građevinu; dvojna je uvijek Po+P+2 (čl. 66.).", "Podzemna izgrađenost (kigP) najviše 0,6, dvojne 0,5; širina čestice dvojne građevine 10 m (čl. 66.)."],
    var=[{"minA": 800, "samoOblik": "slob", "opis": "slobodnostojeća na čestici od 800 m²: Po+P+3, kisN 1,2, kis 2,5", "tipovi": t23(3, 800, 1.20, 2.50)},
         {"minA": 1200, "samoOblik": "slob", "opis": "slobodnostojeća na čestici od 1200 m²: Po+P+4, kisN 1,5, kis 3,0", "tipovi": t23(4, 1200, 1.50, 3.00)}]))

# 2.4 (čl. 67.)
dodaj("2.4", "planirana naselja niske gradnje na periferiji", zona(
    tip("67.", 3, ob(500, 0.35, 1.20, 1.80), ob(300, 0.35, 1.20, 1.80),
        {"minC": "slobodnostojećih građevina Pp min =500 m2 … dvojnih građevina Pp min =300 m2", "izg": "k ig =0,35", "kis": "k is =1,80, k is N=1,2", "etaze": "E=Po+P+3"}),
    meda3("67."), REG_OPCA, zel("67.", 0.3, ZEL30),
    ["Najmanja širina čestice prema ulici: slobodnostojeća 12 m, dvojna 10 m; podzemna izgrađenost najviše 0,6 (čl. 67.).",
     "Nova čestica između dvije izgrađene: najmanje 300 m², kig 0,30, kisN 0,9, kis 1,2, Po+P+2 (čl. 67.).",
     "Građevni pravac prema prevladavajućoj udaljenosti postojećih građevina u uličnom potezu (čl. 67.)."]))

# 2.5 (čl. 68.)
def t25(kig, kisN, kis):
    return tip("68.", 3, ob(500, kig, kisN, kis), ob(400, 0.35, 1.20, 1.80),
               {"minC": "slobodnostojećih građevina Pp min =500 m2 … dvojnih građevina Pp min =400 m2", "izg": f"k ig ={str(kig).replace('.', ',')}",
                "kis": f"k is ={str(kis).replace('.', ',')}, k is N={str(kisN).replace('.', ',')}", "etaze": "E=Po+P+3"})
nap25 = ["Najmanja širina čestice prema ulici: slobodnostojeća 12 m, dvojna 10 m; podzemna izgrađenost najviše 0,6 (čl. 68.).",
         "Nova čestica između dvije izgrađene: najmanje 300 m², kig 0,30, kisN 0,9, kis 1,2, Po+P+2 (čl. 68.).",
         "Na čestici većoj od 1200 m², gdje to dopušta prosječna visina uličnog poteza: Po+P+4, kig 0,30, kis 3,0, kisN 1,5 (čl. 68.); aplikacija to ne pretpostavlja."]
dodaj("2.5", "uređivanje i urbana obnova (mješovita namjena M1)", zona(t25(0.35, 1.20, 1.80), meda3("68."), REG_OPCA, zel("68.", 0.3, ZEL30), nap25))
dodaj("2.5 Bol", "uređivanje i urbana obnova, predjel Bol", zona(t25(0.40, 1.40, 2.00), meda3("68."), REG_OPCA, zel("68.", 0.3, ZEL30),
                                                                  ["Predjel Bol: slobodnostojeće kig 0,4, kigP 0,7, kis 2,0, kisN 1,4 (čl. 68.)."] + nap25))

# 3.1 (čl. 73.)
def t31(n, minC, kisN, kis):
    return tip("73.", n, ob(minC, 0.30, kisN, kis, 250), ob(400, 0.30, 0.90, 1.50, 300, DV_NAP),
               {"minC": "slobodnostojećih građevina Pp min =500 m2 … Pp min =700 m2 … dvojnih građevina Pp min =400 m2", "izg": "k ig =0,3",
                "kis": "500 m2: k is =1,5, k is N=0,9, E=Po+P+2; 700 m2: k is =2,40, k is N=1,2, E=Po+P+3", "etaze": f"E=Po+P+{n}",
                "tl": "maksimalna tlocrtna površina pod nadzemnim dijelom građevine za slobodnostojeće građevine 250 m2"})
dodaj("3.1", "sanacija i urbana obnova djelomično izgrađenih prostora (M1)", zona(
    t31(2, 500, 0.90, 1.50), meda3("73."), reg4("73.", True), zel("73.", 0.3, ZEL30),
    ["Od 700 m² čestice: Po+P+3, kisN 1,2, kis 2,4 (čl. 73.); dvojna je uvijek Po+P+2.",
     "Nova čestica između dvije izgrađene: najmanje 300 m², kig 0,3, kisN 0,9, kis 1,2, Po+P+2 (čl. 73.).",
     "Tlocrt od 250 m² plan navodi uz interpolaciju i ponovno za čestice od 700 m²; je li granica i za čestice od 500 m², tekst ne kaže jasno, pa aplikacija primjenjuje strožu vrijednost.", "Najmanja širina čestice prema ulici: slobodnostojeća 14 m, dvojna 10 m (čl. 73.).",
     "Zona M1 istočno od TTTS-a uz Žrnovnicu: najviše Po+P+2 (čl. 73.)."],
    ["Gdje je odredbama propisana izrada provedbenog dokumenta (UPU/DPU), gradi se tek prema njemu (čl. 73.); provjeri na karti „Urbana pravila” i u lokacijskoj informaciji."],
    var=[{"minA": 700, "samoOblik": "slob", "opis": "slobodnostojeća na čestici od 700 m²: Po+P+3, kisN 1,2, kis 2,4", "tipovi": t31(3, 700, 1.20, 2.40)}]))

# pravila bez izračuna
for k, n, m in [
    ("1.1", "povijesna jezgra Splita", "Pravilo 1.1: zaštita i revitalizacija povijesne jezgre; zahvati uz posebne uvjete konzervatora, izračun za kuću nije moguć (čl. 49.)."),
    ("1.2", "zaštita i dogradnja povijesne baštine", "Pravilo 1.2: zaštićena povijesna baština; uvjete određuju konzervatorski uvjeti, izračun za kuću nije moguć."),
    ("1.4", "zaštićena blokovska izgradnja XIX. i XX. st.", "Pravilo 1.4: blokovska izgradnja; nova gradnja je interpolacija u blok prema susjednim građevinama, izračun za kuću nije moguć."),
    ("1.6", "priobalno područje Bačvice", "Pravilo 1.6: stroga zaštita i prenamjena u javne sadržaje; stambena gradnja nije predviđena."),
    ("1.7", "Park šuma Marjan i parkovi (1.7–1.7d)", "Pravilo 1.7: park šuma i parkovi; nova stambena gradnja nije predviđena."),
    ("1.8", "dovršeni kompleksi jedne namjene", "Pravilo 1.8: kompleksi pretežito javne namjene; stambena gradnja nije predviđena."),
    ("1.9", "prirodne i uređene plaže", "Pravilo 1.9: plaže; gradnja nije predviđena."),
    ("2.1", "dovršena naselja (srednja i visoka gradnja)", "Pravilo 2.1: nova gradnja u zonama M1 i M2 tek na čestici od 1500 m² (kig 0,25, kisN 1,75, čl. 63.); niska kuća na manjoj čestici nije predviđena."),
    ("2.2", "noviji prostori visoke gradnje", "Pravilo 2.2: prostori visoke gradnje; izračun za kuću nije moguć."),
    ("2.6", "dovršeni kompleksi jedne namjene", "Pravilo 2.6: kompleksi jedne namjene; stambena gradnja nije predviđena."),
    ("2.7", "urbana obnova kompleksa jedne namjene", "Pravilo 2.7: kompleksi jedne namjene; stambena gradnja nije predviđena."),
    ("2.8", "parkovi", "Pravilo 2.8: parkovi; gradnja nije predviđena."),
    ("2.9", "umjetne plaže", "Pravilo 2.9: umjetne plaže; gradnja nije predviđena."),
    ("3.2", "nova regulacija na pretežito neizgrađenom prostoru", "Pravilo 3.2: gradnja tek uz provedbeni dokument prostornog uređenja (UPU ili DPU, čl. 74.). Plan za njega propisuje npr. slobodnostojeću kuću na čestici od 600 m², kig 0,25, kisN 0,75, Po+P+2, h/2 od međe; dok plan užeg područja nije donesen, aplikacija ne računa."),
    ("3.3", "djelomično izgrađeni prostori prema usvojenim planovima", "Pravilo 3.3: vrijede važeći detaljni planovi (npr. Žnjan, Duilovo, čl. 75.); uvjete određuje taj plan."),
    ("3.4", "zaštitne i vrijedne pejzažne površine", "Pravilo 3.4: pejzažne površine; stambena gradnja nije predviđena."),
    ("3.5", "pejzažne površine s rekreacijom i turizmom", "Pravilo 3.5: pejzažne površine s rekreacijom; stambena gradnja nije predviđena."),
    ("6", "gradski projekti (luka, Poljud, Kopilica, Duilovo, Meje …)", "Gradski projekti (8.6.): uvjete određuju natječaj i plan užeg područja; izračun za kuću nije moguć."),
    ("namjena", "druga namjena na karti 1 (javna, poslovna, zelenilo, promet)", "Na karti 1. „Korištenje i namjena prostora” čestica nije u stambenoj (S) ni mješovitoj (M1) namjeni, pa uvjeti za stambenu kuću ne vrijede."),
]:
    bez(k, n, m)

def ord_(z):
    k = z[0]
    if k == "namjena": return (99, 0, "")
    p = k.split(" ")[0].split(".")
    return (int(p[0]), int("".join(c for c in (p[1] if len(p) > 1 else "0") if c.isdigit()) or 0), k)
ZONE.sort(key=ord_)

SPLIT = {
    "kod": "GUP Splita", "izvor": IZVOR,
    "obuhvat": [16.39, 43.495, 16.535, 43.545],
    "upozorenje": "Urbano pravilo se ne očitava automatski: odaberi ga prema kartografskom prikazu „Urbana pravila” GUP-a Splita (karta je u odjeljku s kartama plana) i provjeri namjenu (S ili M1) na karti 1.; potvrđuje ih lokacijska informacija.",
    "oblici": [["slob", "slobodnostojeća"], ["dvoj", "dvojna"]],
    "kisUkupni": False,
    "zone": ZONE, "zoneSet": ZSET, "zonaLabel": "Urbano pravilo (karta „Urbana pravila”)",
    "zonaNapomena": "GUP Splita dijeli grad na urbana pravila (visokokonsolidirana 1.x, konsolidirana 2.x, niskokonsolidirana 3.x, gradski projekti) s uvjetima za stambenu (S) i mješovitu (M1) namjenu (čl. 49.).",
    "drugaZona": "Za odabrano urbano pravilo uvjeti za stambenu kuću nisu obrađeni.",
    "tipovi": ZSET["2.4"]["tipovi"], "meda": MEDA_OPCA, "regulacija": REG_OPCA, "zelenilo": zel("67.", 0.3, ZEL30),
    "simulator": {"krov": {"clanak": "49.", "nagibMin": 0, "nagibMax": 30, "ravniDopusten": True,
                           "txt": "Kosi krov se oblikuje kao četverostrešni ili dvostrešni sa ili bez nadozida i ima nagib krovnih ploha od najviše 30"}},
    "pristup": {"napomena": "Parkirališna mjesta prema čl. 33. GUP-a; ulaz u garažu niske stambene građevine može biti bliže od 5 m regulacijskom pravcu, u skladu s lokalnim uvjetima (čl. 49.)."},
    "napomene": ["Niska građevina je visine do P+3; treći kat može biti potkrovlje ili etaža pod ravnim krovom (najviše 40 % donje etaže, uvučena 2 m od uličnog pročelja) (čl. 49.).",
                 "Visina se mjeri od najniže točke zaravnanog terena uz pročelje do vrha stropa zadnjeg kata ili nadozida potkrovlja (nadozid najviše 1,2 m) (čl. 49.)."],
}
for z in ZSET.values():
    if z.get("tipovi"): z["napomene"] = z["napomene"] + SPLIT["napomene"]

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("hrGradovi", {})["SPLIT"] = SPLIT
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("pravila", len(ZONE), "s izračunom", sum(1 for z in ZSET.values() if z.get("tipovi")))

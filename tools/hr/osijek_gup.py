#!/usr/bin/env python3
"""Uvjeti gradnje obiteljskih zgrada iz GUP-a grada Osijeka (čl. 23.j–26., 33. i 40.).

Izvor: Odredbe za provedbu Generalnog urbanističkog plana grada Osijeka, pročišćeni tekst, Službeni glasnik Grada Osijeka
7/2025 (11. 4. 2025.; obuhvaća 5/06 … 4/24 i 23/24), PDF s osijek.hr, tekst izvučen strojno (pdftotext).
Tip stambene zgrade za česticu određuje kartografski prikaz 4.3.2. „Način gradnje”: O (obiteljske), VS (višestambene),
OVS (obiteljske i višestambene) i najveći broj nadzemnih etaža (broj u krugu); namjenu S, S1 ili M kartografski prikaz 1.
Aplikacija: izg = kig, kis = kis (plan ne razlikuje nadzemni i ukupni; podzemne etaže za vozila mogu ga povećati).
Pokretanje: python3 -I tools/hr/osijek_gup.py → src/rules_krk.json → hrGradovi["OSIJEK"].
"""
import json, os

IZVOR = {
    "naziv": "Generalni urbanistički plan grada Osijeka, odredbe za provedbu (pročišćeni tekst)",
    "sn": "Službeni glasnik Grada Osijeka 7/2025",
    "url": "https://www.osijek.hr/",
    "pdf": "https://www.osijek.hr/wp-content/uploads/2025/04/0-7_25-GUP_pro%C4%8Di%C5%A1%C4%87eni_tekst.pdf",
    "status": "na snazi (pročišćeni tekst 7/2025, obuhvaća izmjene do 23/2024); u tijeku je postupak transformacije GUP-a (prijedlog, javni uvid 15.–29. 1. 2026.)",
    "provjera": "Čl. 7., 8., 23.j–26., 33. i 40. iz pročišćenog teksta (PDF s osijek.hr, tekst izvučen strojno), preuzeto 9. 11. 2026.",
    "pravna_provjera": {"status": "NIJE_POTVRDENO",
                        "napomena": "Grad je u siječnju 2026. stavio na javni uvid prijedlog transformiranog GUP-a s drukčijim oznakama zona (npr. SM-O-2) i dijelom drukčijim pokazateljima; donošenje nije provjereno. Tip zgrade i broj etaža određuje kartografski prikaz 4.3.2. „Način gradnje”."}
}

def ob(minC, kig, kis, minIzn=None):
    o = {"minC": minC, "izg": kig, "kis": kis, "kisPodrum": kis, "tlMin": None, "tlMax": None}
    if minIzn: o["minCIznimno"] = minIzn
    return o

TXT = {"minC": "Najmanja površina građevne čestice za obiteljske zgrade je: – za samostojeću građevinu 250 m2 – za poluugrađene građevine 200 m2 – za ugrađenu građevinu 150 m2.",
       "minCIznimno": "Iznimno, u dovršenim i pretežito dovršenim dijelovima naselja, najmanja površina građevne čestice za samostojeću građevinu može biti i manja, ali ne manja od 200 m2.",
       "izg": "Koeficijent izgrađenosti (kig) građevne čestice iznosi najviše: − za samostojeću građevinu 0,4 − za poluugrađene građevine 0,5 − za ugrađene građevine 0,6.",
       "kis": "Koeficijent iskorištenosti (kis) građevne čestice iznosi najviše: − za samostojeću građevinu 1,0 − za poluugrađene građevine 1,3 − za ugrađene građevine 1,6.",
       "etaze": "Najveći broj nadzemnih etaža iznosi 3 za obiteljske zgrade i 1 za pomoćne zgrade. Broj podrumskih etaža nije ograničen.",
       "visina": "Najveća visina građevina iznosi 11,0 m uz ulično pročelje mjereno od najniže kote uređenog terena."}

def obit(et=3):
    return {"obit": {"naziv": "Obiteljska zgrada (do 3 stana)", "opis": "stambena zgrada s najviše tri stana; uz stanovanje samo čiste i tihe djelatnosti, stambeni dio veći od 50 % GBP-a (čl. 24.)",
                     "clanak": "24.–24.a", "gbpMax": None, "etaze": f"najviše {et} nadzemne etaže (i prema broju u krugu na karti 4.3.2.), podrumskih etaža neograničeno",
                     "visina": 11.0, "visinaOpis": "11,0 m uz ulično pročelje, od najniže kote uređenog terena", "txt": TXT,
                     "slob": ob(250, 0.4, 1.0, 200), "dvoj": ob(200, 0.5, 1.3), "ugr": ob(150, 0.6, 1.6),
                     "oblici": [["slob", "samostojeća"], ["dvoj", "poluugrađena"], ["ugr", "ugrađena"]]}}

MEDA = {"clanak": "25.", "min": 1, "opis": "zid uz dvorišnu među ili najmanje 1 m od nje (čl. 25. st. 9.–12.)",
        "opisIznimka": "Na dijelu građevine bližem od 3,0 m granici susjedne čestice ne smiju se projektirati ni izvoditi otvori (čl. 25. st. 15.); zid na međi mora biti puni zid bez otvora (čl. 25.a). S prozorima prema susjedu kuća je zato najmanje 3 m od međe.",
        "txt": "Zid građevine koji je paralelan s dvorišnom međom građevne čestice može biti prislonjen uz tu među ili udaljen 1 m ili više od te međe."}
REG = {"clanak": "25.", "ostale": None,
       "opis": "plan ne propisuje opću udaljenost; 5 m od regulacijskog pravca uz Strossmayerovu (zapadno od Rokove), Divaltovu i dijelove Ulice M. Gupca i Vukovarske, a uz pojedine poteze obvezno zadržavanje postojećeg građevinskog pravca (karta 4.1.2.)",
       "txt": "Građevinski pravac mora biti udaljen 5 m od regulacijskog pravca za sljedeće ulice, odnosno dijelove ulica, a označen je na kartografskom prikazu 4.1.2."}
ZEL = {"clanak": "25.b", "min": 0.3, "txt": "Najmanje 30% površine građevne čestice mora biti ozelenjeno."}
NAP = ["Najmanja duljina regulacijskog pravca 5 m kad je pristup s javne prometne površine (čl. 24. st. 11.).",
       "Postojeća čestica manja od 120 m² s obiteljskom zgradom: kig do 1,0 (čl. 24.a st. 2.).",
       "kis se može uvećati za podzemne etaže koje služe za smještaj vozila (čl. 24.a st. 6.).",
       "Dalje od 20 m od regulacijskog pravca zid uz među najviše 4 m iznad terena susjeda, za novu obiteljsku zgradu 6 m (čl. 24.a st. 14.–17.).",
       "Pomoćne zgrade (osim garaža) samo iza stambene zgrade, najviše 1 etaža i 6 m (čl. 24.a, 25.).",
       "Jedan kolni pristup na česticu, najviše 4,5 m širine (čl. 26.); parkiranje 1 PM po stanu (čl. 40.).",
       "Ograda uz među do 2 m (čl. 25.b)."]

ZONE, ZSET = [], {}
def dodaj(k, naziv, cfg): ZONE.append([k, naziv]); ZSET[k] = cfg
def bez(k, naziv, msg): ZONE.append([k, naziv]); ZSET[k] = {"tipovi": None, "drugaZona": msg + " Mjerodavna je lokacijska informacija Grada Osijeka."}

dodaj("O", "O · obiteljske zgrade (karta 4.3.2.)", {"tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL, "napomene": NAP,
      "upozorenja": ["Najveći broj nadzemnih etaža za česticu je broj u krugu na karti 4.3.2. „Način gradnje”; obiteljska zgrada ima ih najviše 3 (čl. 24.a, 33.)."]})
dodaj("OVS", "OVS · obiteljske i višestambene zgrade (karta 4.3.2.)", {"tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL,
      "napomene": ["Na površini OVS može se graditi i višestambena zgrada (više od 3 stana): čestica najmanje 700 m², kig 0,5, kis 2,5, do 6 etaža i 20 m (čl. 27.–27.a); aplikacija to ne računa."] + NAP,
      "upozorenja": ["Najveći broj nadzemnih etaža prema karti 4.3.2. odnosi se na sve zgrade; obiteljska zgrada ima ih najviše 3 (čl. 24.a, 33.)."]})
bez("VS", "VS · višestambene zgrade (karta 4.3.2.)", "Na površinama VS predviđena je gradnja višestambenih zgrada (čestica najmanje 700 m², kig 0,5, kis 2,5, čl. 27.–27.a); postojeće obiteljske zgrade mogu se rekonstruirati prema uvjetima za obiteljske zgrade (čl. 24.a st. 13.), a nova obiteljska kuća nije predviđena.")
bez("namjena", "druga namjena na karti 1 (javna, gospodarska, zelenilo, promet)", "Na ovoj namjeni stanovanje je moguće samo kao prateći sadržaj (čl. 23.j); uvjeti za obiteljsku kuću se ne primjenjuju.")

OSIJEK = {
    "kod": "GUP Osijeka", "izvor": IZVOR,
    "obuhvat": [18.60, 45.52, 18.76, 45.585],
    "upozorenje": "Tip stambene zgrade (O, OVS, VS) i broj etaža ne očitavaju se automatski: odaberi ih prema kartografskom prikazu 4.3.2. „Način gradnje” GUP-a Osijeka (karta je u odjeljku s kartama plana) i provjeri namjenu S, S1 ili M na karti 1.; potvrđuje ih lokacijska informacija.",
    "oblici": [["slob", "samostojeća"], ["dvoj", "poluugrađena"], ["ugr", "ugrađena"]],
    "kisUkupni": True,
    "zone": ZONE, "zoneSet": ZSET, "zonaLabel": "Način gradnje (karta 4.3.2.)",
    "zonaNapomena": "GUP Osijeka određuje tip stambene zgrade kartom 4.3.2. „Način gradnje”: O obiteljske zgrade, VS višestambene, OVS obje; uvjeti za obiteljske zgrade jednaki su u stambenoj (S, S1) i mješovitoj (M) namjeni (čl. 23.j–25.b).",
    "drugaZona": "Za odabrani način gradnje uvjeti za obiteljsku kuću nisu obrađeni.",
    "tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL,
    "pristup": {"napomena": "Jedan kolni pristup širine do 4,5 m i duljine do 50 m (čl. 26.); 1 parkirališno mjesto po stanu (čl. 40.)."},
    "napomene": NAP,
}

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("hrGradovi", {})["OSIJEK"] = OSIJEK
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("načina gradnje", len(ZONE), "s izračunom", sum(1 for z in ZSET.values() if z.get("tipovi")))

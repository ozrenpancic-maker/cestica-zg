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
    "provjera": "Čl. 7., 8., 23.j–26., 33. i 40. iz pročišćenog teksta (PDF s osijek.hr, tekst izvučen strojno), preuzeto 9. 11. 2026. Neovisna provjera (zasebna provjera koja nije sastavljala pravila), 9. 11. 2026.: oko 45 vrijednosti i navoda, bez odstupanja u brojkama; dopunjene napomene o namjeni S1, otvorima uz među i višestambenoj gradnji u OVS-u.",
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
        "opisIznimka": "Na dijelu građevine bližem od 3,0 m granici susjedne čestice ne smiju se projektirati ni izvoditi otvori (čl. 25. st. 15.); zid na međi mora biti puni zid bez otvora (čl. 25.a st. 1.). Čl. 25.a dopušta na 1 m od međe staklenu opeku, fiksna ostakljenja do 60 × 60 cm i male ventilacijske otvore, a otvore pod kutom od 45° ili većim prema međi slobodno; za obične prozore prema susjedu računaj s najmanje 3 m.",
        "txt": "Zid građevine koji je paralelan s dvorišnom međom građevne čestice može biti prislonjen uz tu među ili udaljen 1 m ili više od te međe."}
REG = {"clanak": "25.", "ostale": None,
       "opis": "plan ne propisuje opću udaljenost; 5 m od regulacijskog pravca uz Strossmayerovu (zapadno od Rokove), Divaltovu i dijelove Ulice M. Gupca i Vukovarske, a uz pojedine poteze obvezno zadržavanje postojećeg građevinskog pravca (karta 4.1.2.)",
       "txt": "Građevinski pravac mora biti udaljen 5 m od regulacijskog pravca za sljedeće ulice, odnosno dijelove ulica, a označen je na kartografskom prikazu 4.1.2."}
ZEL = {"clanak": "25.b", "min": 0.3, "txt": "Najmanje 30% površine građevne čestice mora biti ozelenjeno."}
NAP = ["Namjena S1: obiteljske zgrade samo za stanovanje, bez drugih djelatnosti; namjena S: druge djelatnosti najviše 25 % GBP-a obiteljske zgrade (čl. 7.). U Južnom stadionskom naselju i Filipovici samo obiteljske stambene zgrade (čl. 7. st. 9.).",
       "Najmanja duljina regulacijskog pravca 5 m kad je pristup s javne prometne površine (čl. 24. st. 11.).",
       "Postojeća čestica manja od 120 m² s obiteljskom zgradom: kig do 1,0 (čl. 24.a st. 2.).",
       "kis se može uvećati za podzemne etaže koje služe za smještaj vozila (čl. 24.a st. 6.).",
       "Dalje od 20 m od regulacijskog pravca zid uz među najviše 4 m iznad terena susjeda, za novu obiteljsku zgradu 6 m (čl. 24.a st. 14.–17.).",
       "Pomoćne zgrade (osim garaža) samo iza stambene zgrade, najviše 1 etaža i 6 m (čl. 24.a, 25.).",
       "Jedan kolni pristup na česticu, najviše 4,5 m širine (čl. 26.); parkiranje 1 PM po stanu (čl. 40.).",
       "Ograda uz među do 2 m (čl. 25.b)."]

# odredbe za postojeće zgrade (zahvati: rek = rekonstrukcija, dogr = dogradnja, nadogr = nadogradnja, zamj = zamjenska građevina)
SVE, POST = ["rek", "dogr", "nadogr", "zamj"], ["rek", "dogr", "nadogr"]
REKON = [
    {"zahvati": SVE, "clanak": "24.", "opis": "Čestica s postojećim građevinama manja od propisane može biti građevna čestica za rekonstrukciju postojeće ili gradnju nove građevine iste namjene (st. 10.).",
     "txt": "Građevna čestica s postojećim građevinama koja u pogledu najmanje površine ne udovoljava uvjetima iz stavka 8. može se smatrati građevnom česticom za rekonstrukciju postojeće ili gradnju nove građevine iste namjene."},
    {"zahvati": SVE, "clanak": "24.", "opis": "Čestica s postojećim građevinama može imati kraći regulacijski pravac od 5 m ili ga ne mora imati (st. 12.).",
     "txt": "Iznimno od prethodnog stavka građevna čestica s postojećim građevinama može imati kraći regulacijski pravac ili ga ne mora imati."},
    {"zahvati": SVE, "clanak": "24.", "opis": "Veći postojeći broj građevina na čestici od dopuštenog može se zadržati, ali ne povećati (st. 6.)."},
    {"zahvati": SVE, "clanak": "24.a", "opis": "Postojeća čestica manja od 120 m² s postojećom obiteljskom zgradom: kig do 1,0 (st. 2.).",
     "txt": "Koeficijent izgrađenosti (kig) postojeće građevne čestice manje od 120 m2 s postojećom obiteljskom zgradom može iznositi najviše 1,0."},
    {"zahvati": SVE, "clanak": "24.a", "opis": "Postojeći kig ili kis veći od dopuštenog može se pri radovima na postojećoj zgradi ili gradnji zamjenske zadržati, ali ne povećavati (st. 3. i 5.).",
     "txt": "Iznimno, ukoliko je postojeći koeficijent izgrađenosti veći od dozvoljenog, isti se prilikom izvođenja radova na postojećoj građevini ili gradnji zamjenske građevine može zadržati, ali se ne smije povećavati."},
    {"zahvati": POST, "clanak": "24.a", "opis": "Postojeća visina ili broj etaža veći od dopuštenog može se pri radovima na postojećoj zgradi zadržati, ali ne povećavati (st. 12.)."},
    {"zahvati": POST, "clanak": "24.a", "opis": "Obiteljska zgrada na površini VS (karta 4.3.2.) može se rekonstruirati prema uvjetima za obiteljske zgrade (st. 13.); na nju se ne primjenjuje ni obveza građevinskog pravca 5 m od regulacijskog pravca na ulicama navedenim u čl. 25. st. 1. (čl. 25. st. 5.).",
     "txt": "Iznimno, za obiteljske zgrade, izgrađene na površinama označenim oznakom VS (višestambene zgrade) na kartografskom prikazu 4.3.2. „Način gradnje“, dozvoljava se rekonstrukcija prema uvjetima propisanim za obiteljske zgrade (5.1. Obiteljske zgrade)."},
    {"zahvati": POST, "clanak": "24.a", "opis": "Iznimka kojom zid obiteljske zgrade uz među i dio zgrade smiju biti do 6 m (umjesto 4 m) vrijedi kod rekonstrukcije tek dalje od 25 m od regulacijskog pravca (za novu gradnju dalje od 20 m) (st. 14.–17.)."},
    {"zahvati": POST, "clanak": "25.", "opis": "Postojeća zgrada izgrađena protivno pravilima o udaljenosti zida od međe može se nadograditi u postojećim tlocrtnim gabaritima i/ili dograditi tako da dograđeni dijelovi budu u skladu s odredbama (st. 14.).",
     "txt": "Ukoliko je postojeća građevina izgrađena suprotno stavcima 6. do 10. ovog članka , ista se može nadograditi u postojećim tlorisnim gabaritima i/ili dograditi na način da dograđeni dijelovi budu sukladni ovim Odredbama."},
    {"zahvati": POST, "clanak": "25.", "opis": "Postojeća zgrada izgrađena na više katastarskih čestica, ako se ne može osnovati jedna građevna čestica, može se rekonstruirati; u zaštićenoj povijesnoj cjelini, prema uvjetima nadležnog tijela, i nadograditi u postojećim tlocrtnim gabaritima (st. 7.–8.).",
     "txt": "Ukoliko je postojeća građevina izgrađena na više katastarskih čestica, a ne postoji mogućnost osnivanja jedne građevne čestice, ista se može rekonstruirati."},
    {"zahvati": POST, "clanak": "25.a", "opis": "Postojeća zgrada koja nije usklađena s pravilima o zidu i otvorima uz među usklađuje se samo u dijelovima na kojima se rade radovi; postojeći otvori mogu se zadržati, ali ne povećavati (st. 12.)."},
    {"zahvati": POST, "clanak": "25.b", "opis": "Ako je ozelenjeni dio čestice manji od 30 %, može se zadržati, ali ne smanjivati (st. 5.).",
     "txt": "Iznimno, kod rekonstrukcije postojeće građevine ako je površina ozelenjenog dijela građevne čestice manja od propisane može se zadržati, ali se ne smije smanjivati."},
    {"zahvati": POST, "clanak": "40.", "opis": "Kod rekonstrukcije treba osigurati parkirna mjesta za povećanje površine ili promjenu namjene; iznimno se nedostajuća mjesta mogu riješiti naknadom prema aktu Grada, na udaljenosti do 400 m (st. 7.–8.)."},
    {"zahvati": POST, "clanak": "72.a", "opis": "Zgrada čija je namjena protivna planu ili je izgrađena protivno odredbama plana može se rekonstruirati u svrhu neophodnog poboljšanja uvjeta života i rada: obnova i zamjena dotrajalih dijelova i uređenje unutrašnjosti u postojećim gabaritima (bez prenamjene potkrovlja), dogradnja kupaonice ili WC-a do 6 m² ako ih nema, priključci i instalacije."},
]

ZONE, ZSET = [], {}
def dodaj(k, naziv, cfg): ZONE.append([k, naziv]); ZSET[k] = cfg
def bez(k, naziv, msg): ZONE.append([k, naziv]); ZSET[k] = {"tipovi": None, "drugaZona": msg + " Mjerodavna je lokacijska informacija Grada Osijeka."}

dodaj("O", "O · obiteljske zgrade (karta 4.3.2.)", {"tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL, "napomene": NAP,
      "upozorenja": ["Najveći broj nadzemnih etaža za česticu je broj u krugu na karti 4.3.2. „Način gradnje”; obiteljska zgrada ima ih najviše 3 (čl. 24.a, 33.)."]})
dodaj("OVS", "OVS · obiteljske i višestambene zgrade (karta 4.3.2.)", {"tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL,
      "napomene": ["Na površini OVS može se graditi i višestambena zgrada (više od 3 stana): čestica najmanje 700 m², kig 0,5, kis 2,5, do 6 etaža (i prema broju u krugu na karti 4.3.2.) i 20 m, a uz Strossmayerovu, Divaltovu, Ulicu M. Gupca i Vukovarsku istočno od Trpimirove najmanje 4 etaže (čl. 27.–27.a); aplikacija to ne računa."] + NAP,
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
    "zonaNapomena": "GUP Osijeka određuje tip stambene zgrade kartom 4.3.2. „Način gradnje”: O obiteljske zgrade, VS višestambene, OVS obje; pokazatelji za obiteljske zgrade (čestica, kig, kis, etaže, visina) jednaki su u stambenoj (S, S1) i mješovitoj (M) namjeni, a razlikuju se dopuštene druge djelatnosti (čl. 7., 8., 23.j–25.b).",
    "drugaZona": "Za odabrani način gradnje uvjeti za obiteljsku kuću nisu obrađeni.",
    "tipovi": obit(), "meda": MEDA, "regulacija": REG, "zelenilo": ZEL,
    "pristup": {"napomena": "Jedan kolni pristup širine do 4,5 m i duljine do 50 m (čl. 26.); 1 parkirališno mjesto po stanu (čl. 40.)."},
    "napomene": NAP,
    "rekonstrukcija": REKON,
}

# Prijedlog načina gradnje iz šrafure karte 4.3.2. „Način gradnje” (ISPU WMS, list KN_2_1). Plohe su iscrtane crvenom šrafurom različite
# gustoće i tona, pa se razred određuje iz srednje boje u prozoru od 5 m: s = R − (G+B)/2 (zasićenost), q = (G−B)/s (narančasti ton).
# Kalibrirano 10. 11. 2026. u pregledniku (oznake O, OVS i VS pročitane na karti; vidi docs/zona-boja/osijek.md).
OSIJEK["zonaBoje"] = {
    "naziv": "Način gradnje (karta 4.3.2.)", "pojam": "načina gradnje", "grad": "Osijek", "sloj": "HR_ISPU_GUP1_03123_R10_KN_2_1",
    "wms": ["https://gis2.mgipu.hr/srv1/PPRasterZ14_Public/wms", "https://gis3.mgipu.hr/srv1/PPRasterZ14_Public/wms",
            "https://gis4.mgipu.hr/srv1/PPRasterZ14_Public/wms", "https://gis1.mgipu.hr/srv1/PPRasterZ14_Public/wms"],
    "izvor": "ISPU (Ministarstvo prostornoga uređenja), GUP Osijeka, list KN_2_1 „Način gradnje” (karta 4.3.2.)",
    "mpx": 0.5, "kalibrirano": "2026-11-10",
    "srafura": {"r": 2.5, "vecina": {"r": 8, "omjer": 1.5}, "razredi": [
        {"zona": "OVS", "sMin": 30, "qMin": 0.13},
        {"zona": "VS", "sMin": 122, "qMax": 0.13},
        {"zona": "O", "sMin": 45, "sMax": 122, "qMax": 0.13}]},
    "boje": [{"zona": "O", "rgb": [240, 150, 150]}, {"zona": "VS", "rgb": [240, 85, 85]}, {"zona": "OVS", "rgb": [235, 125, 85]}],
}
OSIJEK["upozorenje"] = ("Način gradnje (O, OVS, VS) nije potvrđen: aplikacija ga može predložiti iz šrafure karte 4.3.2. „Način gradnje”, ali ga potvrđuješ ti "
                        "(karta je u odjeljku s kartama plana). Broj etaža (broj u krugu na karti) ne očitava se; potvrđuje ih lokacijska informacija.")

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d.setdefault("hrGradovi", {})["OSIJEK"] = OSIJEK
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("načina gradnje", len(ZONE), "s izračunom", sum(1 for z in ZSET.values() if z.get("tipovi")))

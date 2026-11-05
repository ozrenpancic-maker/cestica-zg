#!/usr/bin/env python3
"""Prenosi pravila UPU-a 3 Punat iz baze s citatima (data/pravila-sn/punat-upu3.json) u pravila aplikacije
(src/rules_krk.json → upu["UPU 3"]). Svaka vrijednost i svaki navod uzimaju se iz baze prema id-u pravila;
ništa se ne upisuje ručno osim strukture (zone, nazivi, napomene). Izvedena je samo najmanja čestica za interpolaciju
(450 m² − 10 %), uz navod na kojem počiva.

  python3 tools/sn-pgz/punat_u_aplikaciju.py          # zapisuje upu["UPU 3"] u src/rules_krk.json
  python3 tools/sn-pgz/punat_u_aplikaciju.py --provjeri   # samo provjerava je li zapis u rules_krk.json jednak izvedenom

Napomena o izvorima: tekst II. izmjena (SN PGŽ 3/2020, id 41087) dohvaćen je u cijelosti sa sn.pgz.hr; tekst ciljanih izmjena
2016. (SN PGŽ 13/2016, id 33933) potječe iz izvoza treće strane i nije uspoređen sa sn.pgz.hr. To se nosi uz svaki navod."""
import json, os, re, sys
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
BAZA = os.path.join(R, "data", "pravila-sn", "punat-upu3.json")
PRAVILA = os.path.join(R, "src", "rules_krk.json")
B = json.load(open(BAZA, encoding="utf-8"))
P = {r["id"]: r for r in B["pravila"]}
SN = {41087: "SN PGŽ 3/2020", 33933: "SN PGŽ 13/2016"}


def v(i):
    return P[i]["vrijednost"]


def cit(i, t=None, clanak=None):
    r = P[i]; z = r["izvor"]; oid = z["odluka_id"]
    tt = t or ("t. " + z["tocka"] if z.get("tocka") else ("st. " + z["stavak"] if z.get("stavak") else None))
    c = {"t": tt, "x": z["citat"], "sn": SN[oid], "pravilo": i,
         "izvorTeksta": "cijeli tekst odluke sa sn.pgz.hr" if oid == 41087 else "izvoz teksta treće strane, nije uspoređen sa sn.pgz.hr",
         "potvrdenIzvor": oid == 41087}
    if clanak or z["clanak_plana"]:
        c["clanak"] = (clanak or z["clanak_plana"]) + "."
    return c


def grupa(cl, minc, izg, kis, kisn, vis, visn, meda, tl=None, extra=None):
    g = {"clanak": cl + ".", "minC": {"obit": cit(minc)}, "izg": cit(izg), "kis": cit(kis), "kisNeizgr": cit(kisn),
         "visina": cit(vis), "visinaNeizgr": cit(visn), "meda": cit(meda)}
    if tl: g["tl"] = cit(tl)
    g.update(extra or {})
    return g


def izvedi():
    UPOZ = ["Osnovne vrijednosti (najmanja čestica, kig, kis, visina, odmaci) iz ciljanih izmjena 2016. preuzete su iz izvoza teksta treće strane i nisu uspoređene sa Službenim novinama PGŽ.",
                       "Definicije podruma i obračuna etaža (čl. 3. i 5. odredbi), parkiranje (poglavlje 5.) i udaljenost od regulacijskog pravca nisu izdvojeni, pa nisu u izračunu.",
                       "III. izmjene i dopune UPU-a 3 su u izradi; vrijednosti se mogu promijeniti."]
    slob = {"minC": v("p3-46a-cestica-min"), "minCIznimno": round(v("p3-46a-cestica-min") * (1 - v("p3-46a-interpolacija") / 100), 1),
            "izg": v("p3-46a-kig"), "kis": v("p3-46a-kis-izg"), "kisNeizgr": v("p3-46a-kis-neizg"),
            "tlMin": v("p3-46-tl-min"), "tlMax": v("p3-46-tl-slob"),
            "tlVelika": {"prag": P["p3-46-tl-slob-velika"]["uvjet"]["vrijednost"], "tl": v("p3-46-tl-slob-velika")}}
    dvoj = {"minC": v("p3-46b-cestica-min"), "izg": v("p3-46b-kig"), "kis": v("p3-46b-kis-izg"), "kisNeizgr": v("p3-46b-kis-neizg"),
            "tlMax": v("p3-46-tl-dvoj")}
    ugr = {"minC": v("p3-46c-cestica-min"), "izg": v("p3-46c-kig"), "kis": v("p3-46c-kis-izg"), "kisNeizgr": v("p3-46c-kis-neizg"),
           "napomena": "Za završnu (zadnju) jedinicu niza plan propisuje druge uvjete: čestica %s m², kig %s, kis %s u izgrađenom i %s u neizgrađenom dijelu (čl. 46c.). Izračun je za jedinicu niza koja nije završna. Najveći tlocrt za građevine u nizu nije izdvojen iz čl. 46.; prikazan je samo tlocrt iz kig-a."
           % (v("p3-46c-cestica-min-zadnja"), str(v("p3-46c-kig-zadnja")).replace(".", ","), str(v("p3-46c-kis-izg-zadnja")).replace(".", ","), str(v("p3-46c-kis-neizg-zadnja")).replace(".", ",")),
           "uvjeti": ["najveći tlocrt za građevine u nizu nije izdvojen iz čl. 46.; prikazan je samo tlocrt iz kig-a",
                      "za završnu jedinicu niza vrijede drugi uvjeti (čl. 46c.); izračun je za jedinicu niza koja nije završna",
                      "najveći broj etaža za građevine u nizu nije izdvojen iz čl. 46c."]}
    for i in ("p3-46a-visina-izg", "p3-46b-visina-izg", "p3-46c-visina-izg"): assert v(i) == v("p3-46a-visina-izg")
    for i in ("p3-46a-visina-neizg", "p3-46b-visina-neizg", "p3-46c-visina-neizg"): assert v(i) == v("p3-46a-visina-neizg")
    assert v("p3-46a-odmak-meda") == v("p3-46b-odmak-meda") == v("p3-46c-odmak-meda")
    obit = {"naziv": "Obiteljska kuća", "opis": "slobodnostojeća najviše tri stana (ili dva stana i poslovni prostor); svaka jedinica dvojne kuće najviše jedna stambena jedinica",
            "clanak": "46. i 46a.–46c.", "gbpMax": None, "etaze": "tri nadzemne etaže (slobodnostojeća i dvojna, čl. 46a.–46b.; za niz nije izdvojeno)",
            "visina": v("p3-46a-visina-izg"), "visinaNeizgr": v("p3-46a-visina-neizg"),
            "oblici": [["slob", "slobodnostojeća"], ["dvoj", "dvojna"], ["ugr", "jedinica niza (nije završna)"]],
            "slob": slob, "dvoj": dvoj, "ugr": ugr,
            "txt": {"tl": P["p3-46-tl-slob"]["izvor"]["citat"], "minCIznimno": P["p3-46a-interpolacija"]["izvor"]["citat"] + " (" + SN[41087] + ", čl. 46a. t. 8)"}}
    citati = {"izvor": "data/pravila-sn/punat-upu3.json (navodi provjereni skriptom tools/sn-pgz/provjeri_citate.py u tekstu odluke, 21. 10. 2026.)",
              "slob": grupa("46a", "p3-46a-cestica-min", "p3-46a-kig", "p3-46a-kis-izg", "p3-46a-kis-neizg", "p3-46a-visina-izg", "p3-46a-visina-neizg", "p3-46a-odmak-meda",
                            tl="p3-46-tl-slob", extra={"tlVelika": cit("p3-46-tl-slob-velika"), "tlMin": cit("p3-46-tl-min"), "minCIznimno": cit("p3-46a-interpolacija")}),
              "dvoj": grupa("46b", "p3-46b-cestica-min", "p3-46b-kig", "p3-46b-kis-izg", "p3-46b-kis-neizg", "p3-46b-visina-izg", "p3-46b-visina-neizg", "p3-46b-odmak-meda", tl="p3-46-tl-dvoj"),
              "ugr": grupa("46c", "p3-46c-cestica-min", "p3-46c-kig", "p3-46c-kis-izg", "p3-46c-kis-neizg", "p3-46c-visina-izg", "p3-46c-visina-neizg", "p3-46c-odmak-meda")}
    return {
        "kod": "UPU 3 Punat",
        "prepoznaj": "UPU\\s*3\\b[^|]*Punat",
        "jls": "PUNAT",
        "izvor": {"naziv": "Urbanistički plan uređenja UPU 3 – građevinsko područje naselja N1 – centralno naselje Punat, odredbe za provođenje",
                  "sn": "Službene novine PGŽ 34/2010, izmjene 13/2016 i 3/2020",
                  "url": P["p3-46-tl-slob"]["izvor"]["url"],
                  "status": "na snazi (zadnje II. izmjene i dopune, SN PGŽ 3/2020); III. izmjene i dopune u izradi",
                  "provjera": "Vrijednosti i navodi preuzeti su iz baze data/pravila-sn/punat-upu3.json. Čl. 46. i točke čl. 46a.–46c. koje su mijenjane 2020. potječu iz cijelog teksta II. izmjena (SN PGŽ 3/2020) sa sn.pgz.hr. Najmanja čestica, kig, kis, visina i odmaci (čl. 46a.–46c., t. 1–3, nisu mijenjani 2020.) potječu iz teksta ciljanih izmjena 2016. (SN PGŽ 13/2016) iz izvoza treće strane, koji nije uspoređen sa sn.pgz.hr.",
                  "pravna_provjera": {"status": "NIJE_POTVRDENO",
                                      "razlog": "Pročišćeni tekst UPU-a 3 nije dostupan; stanje odredbi složeno je iz osnovnog teksta 2010., ciljanih izmjena 2016. i II. izmjena 2020. Tekst iz 2016. nije uspoređen sa sn.pgz.hr, a vjerodostojno tumačenje iz 2012. nije pronađeno.",
                                      "napomena": "Pravna aktualnost UPU-a 3 Punat nije neovisno potvrđena: stanje odredbi složeno je iz više odluka, tekst izmjena iz 2016. nije uspoređen sa službenom objavom, a III. izmjene i dopune su u izradi. Uvjeti gradnje služe za orijentaciju; mjerodavna je lokacijska informacija."}},
        "zone": [["S1", "S1 (čl. 46.–46c.)"], ["S2", "S2 (čl. 46.–46c.)"], ["M1", "M1 (čl. 46.–46c.)"], ["M2", "M2 (uvjeti čl. 54c.–54e. nisu obrađeni)"], ["druga", "druga zona"]],
        "zoneSet": {"M2": {"tipovi": None, "drugaZona": "Uvjeti za zonu M2 (čl. 54c.–54e. UPU-a 3) aplikacija još nije obradila."},
                    "S1": {"upozorenja": UPOZ + ["Zona S1: poslovni dio stambene građevine ne smije prelaziti 10 % GBP-a (čl. 46a.): „" + P["p3-46a-poslovni-S1"]["izvor"]["citat"] + "”."]}},
        "zonaNapomena": "Obiteljske kuće (slobodnostojeće, dvojne, u nizu) prema čl. 46.–46c. grade se u zonama S1, S2 i M1. Zona se ne može odrediti automatski: prikazana je samo na grafičkom prikazu br. 4 UPU-a 3 (raster), bez vektorskog sloja; provjeri je na prikazu plana ili u lokacijskoj informaciji.",
        "drugaZona": "Za odabranu zonu uvjeti za obiteljske kuće iz UPU-a 3 nisu obrađeni.",
        "dioGP": {"opcije": [["", "— prema županijskom sloju —"], ["izgradeni", "izgrađeni dio"], ["neizgradeni", "neizgrađeni dio"]],
                  "napomena": "Koeficijent iskoristivosti (kis) i najveća visina ovise o tome je li čestica u izgrađenom ili neizgrađenom dijelu građevinskog područja naselja. Granica je na grafičkom dijelu plana, ne u tekstu."},
        "upozorenja": UPOZ,
        "tipovi": {"obit": obit},
        "kisUkupni": True,
        "meda": {"clanak": "46a.–46c.", "min": v("p3-46a-odmak-meda"), "opis": "h/2, najmanje 3 m; najmanje 6 m od susjednih građevina",
                 "txt": P["p3-46a-odmak-meda"]["izvor"]["citat"] + ", " + P["p3-46a-odmak-gradevine"]["izvor"]["citat"]},
        "regulacija": {"clanak": None, "opis": "udaljenost od regulacijskog pravca nije izdvojena iz odredbi UPU-a 3 (Podaci nisu dostupni)", "txt": ""},
        "zelenilo": {"clanak": "46a.–46c.", "min": v("p3-46a-zelenilo") / 100,
                     "txt": "obavezna površina zelenila: slobodnostojeća %s %%, dvojna %s %%, u nizu %s %% (završna jedinica 30 %%), čl. 46a.–46c. t. 4 (%s)" % (v("p3-46a-zelenilo"), v("p3-46b-zelenilo"), v("p3-46c-zelenilo"), SN[41087])},
        "pristup": {"napomena": "Parkiranje i pristup prema poglavlju 5. odredbi UPU-a 3 (nije izdvojeno)."},
        "napomene": ["Pojedine čestice imaju posebne uvjete (npr. k.č. 3307 k.o. Punat, čl. 46a. t. 8); aplikacija ih ne primjenjuje."],
        "citati": citati,
    }


def main():
    U = izvedi(); s = open(PRAVILA, encoding="utf-8").read(); D = json.loads(s)
    if "--provjeri" in sys.argv:
        ok = D.get("upu", {}).get("UPU 3") == U
        print("UPU 3 u rules_krk.json", "jednak je izvedenom iz baze" if ok else "RAZLIKUJE SE od izvedenog iz baze"); sys.exit(0 if ok else 1)
    D["upu"]["UPU 3"] = U
    open(PRAVILA, "w", encoding="utf-8").write(json.dumps(D, ensure_ascii=False, indent=2) + "\n")
    print("zapisano: upu[\"UPU 3\"]")


if __name__ == "__main__":
    main()

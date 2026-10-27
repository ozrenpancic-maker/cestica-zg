from a1 import *
# Članak 33
OT = "ukoliko građevina ima otvore, prohodne terase i otvorena stubišta"
BF = "Ukoliko na bočnim i stražnjim fasadama građevine nisu predviđeni otvori niti otvorena stubišta"
N_OT = "VEZNIK: »otvore, prohodne terase i otvorena stubišta« – nije jasno mora li građevina imati sve ili je dovoljno bilo koje"
N_BF = "TUMACENJE: nije jasno vrijedi li i tada uvjet h/2 te što s prohodnim terasama, koje ovdje nisu navedene"
def sl33(st, mn, mx, Z=None, I=()):
    vg = ("stambena građevina – slobodnostojeća", "Građevine stambene namjene" if st == 1 else "građevine stambene namjene",
          "Građevine stambene namjene koje će se graditi" if st == 1 else "građevine stambene namjene koje će se graditi", 'odredba')
    nc = ("slobodnostojeća", "na slobodnostojeći način")
    K(33, st, None, None, "moraju biti udaljene najmanje pola visine (h/2) od granice građevinske čestice", "najmanja udaljenost od granice građevne čestice", ">=", "h/2", "opis", vg, nac=nc, zona=Z, izn=I)
    unit = "4,0 metra" if st == 1 else "3,0 m"
    K(33, st, None, None, "udaljene najmanje pola visine (h/2) od granice građevinske čestice, ali ne manje od " + unit + " " + OT, "najmanja udaljenost od granice građevne čestice", ">=", mn, "m", vg, nac=nc, zona=Z, izn=I,
      uv=[(OT, 'odredba')], nej=N_OT)
    K(33, st, None, None, BF + ", udaljenost građevine od granice građevne čestice može iznositi i " + ("3,0 m" if st == 1 else "2,0 m"), "najmanja udaljenost od granice građevne čestice", ">=", mx, "m", vg, nac=nc, zona=Z, izn=I,
      uv=[(BF, 'odredba')], nej=N_BF)
sl33(1, 4.0, 3.0)
sl33(3, 3.0, 2.0, Z=([], PZ), I=["Iznimno, građevine stambene namjene koje će se graditi na slobodnostojeći način unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"])
def dv33(st, mn, mx, Z=None):
    izr = "Obiteljske/višeobiteljske kuće" if st == 2 else "obiteljske/višeobiteljske kuće"
    for kind in ["obiteljska kuća", "višeobiteljska kuća"]:
        for nac, pr in [("dvojna", "jednom stranom"), ("ugrađena", "s dvije ili tri strane")]:
            vg = (kind + " – " + nac, izr, izr + " koje će se graditi kao dvojne/ugrađene", 'odredba')
            nc = (nac, "koje će se graditi kao dvojne/ugrađene")
            N_K = "VEZNIK: »Obiteljske/višeobiteljske« i »dvojne/ugrađene« – kandidat je razložen po vrsti i načinu gradnje"
            K(33, st, None, None, "prislanjati uz susjednu građevinu ili granicu građevne čestice", "prislanjanje uz susjednu građevinu ili granicu građevne čestice", "dopustenje", pr, "opis", vg, nac=nc, zona=Z,
              nej="VEZNIK: »uz susjednu građevinu ili granicu građevne čestice« – bilo koje od navedenog")
            K(33, st, None, None, "moraju s drugim dijelovima građevine (istakom) biti udaljene od granice susjedne građevine najmanje h/2", "najmanja udaljenost istaka od granice susjedne građevine", ">=", "h/2", "opis", vg, nac=nc, zona=Z)
            u = "4,0 metra" if st == 2 else "3,0 m"
            K(33, st, None, None, "udaljene od granice susjedne građevine najmanje h/2, ali ne manje od " + u + " od granice građevne čestice, " + OT, "najmanja udaljenost istaka od granice građevne čestice", ">=", mn, "m", vg, nac=nc, zona=Z,
              uv=[(OT, 'odredba')], nej=N_OT)
            K(33, st, None, None, BF + ", udaljenost građevine od granice građevne čestice može iznositi i " + ("3,0 m" if st == 2 else "2,0 m"), "najmanja udaljenost istaka od granice građevne čestice", ">=", mx, "m", vg, nac=nc, zona=Z,
              uv=[(BF, 'odredba')], nej="TUMACENJE: tekst kaže »udaljenost građevine«, a ne istaka; nije jasno vrijedi li i tada h/2")
dv33(2, 4.0, 3.0)
dv33(4, 3.0, 2.0, Z=([], "Unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"))

# Članak 38
def drust(st, kinds, izr, uvod, kig, kis, kisp, vis, dcit):
    for kind in kinds:
        vg = (kind, izr, uvod, 'uvod_stavka')
        nej = None if len(kinds) == 1 else "VRSTA_OPCENITA: uvod navodi više vrsta (" + izr + "); kandidat razložen po vrsti"
        K(38, st, "a", None, "najveći dopušteni koeficijent izgrađenosti (kig) iznosi " + kig[1], "najveći koeficijent izgrađenosti (kig)", "<=", kig[0], "koeficijent", vg, nej=nej)
        K(38, st, "b", None, "najveći dopušteni koeficijent iskoristivosti (kis) nadzemnih etaža iznosi " + kis[1], "najveći koeficijent iskoristivosti (kis) nadzemnih etaža", "<=", kis[0], "koeficijent", vg, nej=nej)
        P = "ukoliko se ispod građevine gradi podrum"
        cc = P + " najveći dopušteni koeficijent iskoristivosti (kis) iznosi " + kisp[1] + " od čega je 0,8 koeficijent iskoristivosti (kis) potpuno ukopane etaže"
        K(38, st, "c", None, cc, KP, "<=", kisp[0], "koeficijent", vg, uv=[(P, 'odredba')], nej=nej)
        K(38, st, "c", None, cc, "drugo: najveći kis potpuno ukopane etaže", "<=", 0.8, "koeficijent", vg, uv=[(P, 'odredba')], nej=nej)
        K(38, st, "d", None, dcit, "najveći broj etaža", "<=", "podrum i dvije nadzemne etaže", None, vg, nej=nej)
        K(38, st, "d", None, dcit, "najveća visina građevine", "<=", vis, "m", vg, nej=nej)
NAS = "grade se unutar građevinskih područja naselja u skladu s veličinom naselja i standardima, na način da pridonose kvaliteti života u naselju"
N_STD = "UPUCIVANJE: »standardima« nisu određeni"
drust(1, ["predškolska ustanova"], "predškolskih ustanova", "Uvjeti za gradnju predškolskih ustanova", (0.5, "0,5"), (1.0, "1,0"), (1.8, "1,8"), 8.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 8,0 m")
K(38, 1, "e", None, "uvjeti o veličini građevne čestice, uređenju građevne čestice i obveznim prostorima građevina predškolskog odgoja određeni su Državnim pedagoškim standardom predškolskog odgoja (NN 63/08)",
  "najmanja površina građevne čestice", "opis", "prema Državnom pedagoškom standardu predškolskog odgoja (NN 63/08)", "opis", ("predškolska ustanova", "građevina predškolskog odgoja", "obveznim prostorima građevina predškolskog odgoja", 'odredba'),
  nej="UPUCIVANJE: veličinu građevne čestice određuje Državni pedagoški standard predškolskog odgoja (NN 63/08)")
drust(2, ["školska ustanova"], "školskih ustanova", "Uvjeti za gradnju školskih ustanova", (0.5, "0,5"), (1.0, "1,0"), (1.8, "1,8"), 8.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 8,0m")
K(38, 2, "e", None, "uvjeti o veličini građevne čestice, uređenju građevne čestice i obveznim prostorima građevina školskog odgoja određeni su Državnim pedagoškim standardom osnovnoškolskog sustava odgoja i obrazovanja (NN 63/08)",
  "najmanja površina građevne čestice", "opis", "prema Državnom pedagoškom standardu osnovnoškolskog sustava odgoja i obrazovanja (NN 63/08)", "opis", ("školska ustanova", "građevina školskog odgoja", "obveznim prostorima građevina školskog odgoja", 'odredba'),
  nej="UPUCIVANJE: veličinu građevne čestice određuje Državni pedagoški standard osnovnoškolskog sustava odgoja i obrazovanja (NN 63/08)")
ZS = ["građevina zdravstvene djelatnosti", "građevina socijalne djelatnosti"]
drust(3, ZS, "građevina zdravstvene i socijalne djelatnosti", "Uvjeti za gradnju građevina zdravstvene i socijalne djelatnosti", (0.5, "0,5"), (1.0, "1,0"), (1.8, "1,8"), 8.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 8,0m")
for kind in ZS:
    K(38, 3, "e", None, "građevine zdravstvene i socijalne djelatnosti " + NAS, "dopuštenost gradnje", "dopustenje", "unutar građevinskih područja naselja", "opis",
      (kind, "građevine zdravstvene i socijalne djelatnosti", "građevine zdravstvene i socijalne djelatnosti grade se", 'odredba'), uv=[("u skladu s veličinom naselja i standardima", 'odredba')], nej=N_STD)
K(38, 3, "f", None, "za prostore zdravstvene stanice (ambulante) optimalna površina iznosi 0,02 - 0,05 m 2 /st", "drugo: optimalna površina prostora zdravstvene stanice po stanovniku", "izmedju", "0.02–0.05", "m²",
  ("zdravstvena stanica (ambulanta)", "zdravstvene stanice (ambulante)", "za prostore zdravstvene stanice (ambulante)", 'odredba'),
  nej="TUMACENJE: jedinica je m²/st (po stanovniku), a vrijednost je »optimalna«, ne granična")
drust(4, ["građevina kulturnih djelatnosti"], "građevina kulturnih djelatnosti", "Uvjeti za gradnju građevina kulturnih djelatnosti", (0.5, "0,5"), (1.0, "1,0"), (1.8, "1,8"), 8.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 8,0m")
K(38, 4, "e", None, "građevine kulturnih djelatnosti " + NAS, "dopuštenost gradnje", "dopustenje", "unutar građevinskih područja naselja", "opis",
  ("građevina kulturnih djelatnosti", "građevine kulturnih djelatnosti", "građevine kulturnih djelatnosti grade se", 'odredba'), uv=[("u skladu s veličinom naselja i standardima", 'odredba')], nej=N_STD)
drust(5, ["vjerska građevina"], "vjerskih građevina", "Uvjeti za gradnju vjerskih građevina", (0.6, "0,6"), (1.0, "1,0"), (1.8, "1,8"), 8.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 8,0m")
K(38, 5, "d", None, "a visina zvonika može biti viša", "drugo: visina zvonika", "dopustenje", "visina zvonika može biti viša", "opis",
  ("vjerska građevina", "vjerskih građevina", "Uvjeti za gradnju vjerskih građevina", 'uvod_stavka'), nej="TUMACENJE: za zvonik nije propisana najveća visina")
drust(6, ["sportsko-rekreacijska građevina"], "sportsko-rekreacijskih građevina", "Uvjeti za gradnju sportsko-rekreacijskih građevina", (0.6, "0,6"), (1.2, "1,2"), (2.0, "2,0"), 12.0, "mogu se graditi kao podrum i dvije nadzemne etaže, najveće visine 12,0m")
K(38, 6, "e", None, "sportsko-rekreacijske građevine " + NAS, "dopuštenost gradnje", "dopustenje", "unutar građevinskih područja naselja", "opis",
  ("sportsko-rekreacijska građevina", "sportsko-rekreacijske građevine", "sportsko-rekreacijske građevine grade se", 'odredba'), uv=[("u skladu s veličinom naselja i standardima", 'odredba')], nej=N_STD)
K(38, 6, "f", None, "unutar građevinskog područja naselja omogućuje se građenje zatvorenih sportsko-rekreacijskih građevina (dvorana) te bazena i otvorenih sportskih sadržaja prema standardima koji vrijede za pojedini sportski objekt",
  "dopuštenost gradnje", "dopustenje", "zatvorene sportsko-rekreacijske građevine (dvorane), bazeni i otvoreni sportski sadržaji", "opis",
  ("sportsko-rekreacijska građevina – zatvorena (dvorana)", "zatvorenih sportsko-rekreacijskih građevina (dvorana) te bazena i otvorenih sportskih sadržaja", "građenje zatvorenih sportsko-rekreacijskih građevina (dvorana) te bazena i otvorenih sportskih sadržaja", 'odredba'),
  uv=[("prema standardima koji vrijede za pojedini sportski objekt", 'odredba')], nej="UPUCIVANJE: uvjete određuju standardi za pojedini sportski objekt")
K(38, 7, None, None, "Građevine mješovite namjene grade se prema strožim uvjetima za izgradnju od dviju kombiniranih namjena", "drugo: mjerodavni uvjeti za mješovitu namjenu", "opis", "stroži uvjeti od dviju kombiniranih namjena", "opis",
  ("građevina mješovite namjene", "Građevine mješovite namjene", "Građevine mješovite namjene grade se", 'odredba'), nej="TUMACENJE: »strožim uvjetima« treba odrediti za svaki parametar zasebno")
K(38, 8, None, None, "Građevine koje služe društvenim djelatnostima i sportsko-rekreacijskim i ostalim sadržajima javnog interesa grade se na građevnoj čestici min 500m 2 , ako ovim odredbama nije drugačije određeno",
  "najmanja površina građevne čestice", ">=", 500, "m²", ("građevina društvenih djelatnosti, sportsko-rekreacijskih i ostalih sadržaja javnog interesa", "Građevine koje služe društvenim djelatnostima i sportsko-rekreacijskim i ostalim sadržajima javnog interesa", "Građevine koje služe društvenim djelatnostima i sportsko-rekreacijskim i ostalim sadržajima javnog interesa", 'odredba'),
  uv=[("ako ovim odredbama nije drugačije određeno", 'odredba')], nej="NEDEFINIRAN_POJAM: »ostalim sadržajima javnog interesa« nije definirano; VRSTA_OPCENITA")

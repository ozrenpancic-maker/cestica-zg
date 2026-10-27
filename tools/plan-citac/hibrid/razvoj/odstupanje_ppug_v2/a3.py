from a2 import *
# Članak 39 (1)
U39 = "Uvjeti za arhitektonsko oblikovanje građevina društvene i sportsko-rekreacijske namjene"
NV = "VRSTA_OPCENITA: odredba se odnosi na građevine društvene i sportsko-rekreacijske namjene; kandidat razložen po vrsti"
for kind in ["građevina društvene namjene", "građevina sportsko-rekreacijske namjene"]:
    vgu = (kind, "građevina društvene i sportsko-rekreacijske namjene", U39, 'uvod_stavka')
    vgo = (kind, "građevine društvene ili sportsko-rekreacijske namjene", "građevine društvene ili sportsko-rekreacijske namjene moraju biti udaljene", 'odredba')
    K(39, 1, None, None, "krovište može biti ravno ili koso", "oblik krovišta", "dopustenje", "ravno ili koso", "opis", vgu, nej=NV)
    K(39, 1, None, None, "krovište može biti ravno ili koso nagiba između 17° i 23°, a kojeg predviđa usvojena tehnologija građenja pojedine građevine", "nagib krovnih ploha", "izmedju", "17–23", "°", vgu,
      uv=[("ako je koso", 'odredba')] if False else [], nej="TUMACENJE: nije jasno ograničava li dodatak »a kojeg predviđa usvojena tehnologija građenja« raspon nagiba ili ga zamjenjuje; " + NV)
    K(39, 1, None, None, "građevine društvene ili sportsko-rekreacijske namjene moraju biti udaljene najmanje pola visine (h/2) od granice građevinske čestice", "najmanja udaljenost od granice građevne čestice", ">=", "h/2", "opis", vgo, nej=NV)
    K(39, 1, None, None, "građevine društvene ili sportsko-rekreacijske namjene moraju biti udaljene najmanje pola visine (h/2) od granice građevinske čestice, ali ne manje od 4,0 metra", "najmanja udaljenost od granice građevne čestice", ">=", 4.0, "m", vgo, nej=NV)
    I = ["Iznimno, unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"]; Z = ([], PZ)
    K(39, 1, None, None, "građevine društvene ili sportsko-rekreacijske namjene moraju biti udaljene najmanje pola visine (h/2) od granice građevinske čestice", "najmanja udaljenost od granice građevne čestice", ">=", "h/2", "opis", vgo, zona=Z, izn=I, nej=NV)
    K(39, 1, None, None, "građevine društvene ili sportsko-rekreacijske namjene moraju biti udaljene najmanje pola visine (h/2) od granice građevinske čestice, ali ne manje od 3,0 metra", "najmanja udaljenost od granice građevne čestice", ">=", 3.0, "m", vgo, zona=Z, izn=I, nej=NV)
    VU = "ukoliko se na jednoj građevnoj čestici smješta više građevina"
    K(39, 1, None, None, "najmanja međusobna udaljenost između građevina definira se (h1+h2)/2", "najmanja udaljenost između građevina na istoj čestici", ">=", "(h1+h2)/2", "opis", vgu, uv=[(VU, 'odredba')], nej=NV)
    K(39, 1, None, None, "najmanja međusobna udaljenost između građevina definira se (h1+h2)/2 (h1 i h2 su visine susjednih građevina), ali ne manje od 6,0 m", "najmanja udaljenost između građevina na istoj čestici", ">=", 6.0, "m", vgu, uv=[(VU, 'odredba')], nej=NV)
    K(39, 1, "-", 1, "najmanje 20% građevne čestice mora biti hortikulturno uređen temeljem krajobraznog projekta", "najmanji udio zelenila na građevnoj čestici", ">=", 20, "%", vgu, nej=NV)
    K(39, 1, "-", 2, "kod građenja građevina društvene ili sportsko-rekreacijske namjene potrebno je na građevnoj čestici osigurati potreban broj parkirališnih mjesta u skladu s točkom 5.1.1. ovih odredbi",
      "drugo: broj parkirališnih mjesta na građevnoj čestici", "opis", "u skladu s točkom 5.1.1. ovih odredbi", "opis",
      (kind, "građevina društvene ili sportsko-rekreacijske namjene", "kod građenja građevina društvene ili sportsko-rekreacijske namjene", 'odredba'),
      nej="UPUCIVANJE: broj mjesta određuje točka 5.1.1. odredbi, koja nije dana")
pom(39, 2, "uz građevine društvene i sportsko-rekreacijske namjene", "iznimno, " + PZ, "Najmanja dopuštena udaljenost od regulacijskog pravca iznosi 4,0 metara")

# Članak 50
NO = "VRSTA_OPCENITA: »građevina osnovne namjene« bez navedene vrste; iz konteksta (pomoćne građevine ugostiteljsko-turističke namjene) moguće ugostiteljsko-turistička"
for st, mn, otv, Z, I in [("1", 6.0, "4,0", None, ()), ("1a", 5.0, "3,0", ([], PZ), ["Iznimno, " + PZ])]:
    vg = ("građevina osnovne namjene", "građevine osnovne namjene", "građevine osnovne namjene od granice", 'odredba')
    m = "6,0 metara" if st == "1" else "5,0 metara"
    U0 = "Udaljenost" if st == "1" else "udaljenost"
    K(50, st, None, None, U0 + " građevine osnovne namjene od granice građevne čestice iznosi najmanje h/2", "najmanja udaljenost od granice građevne čestice", ">=", "h/2", "opis", vg, zona=Z, izn=I, nej=NO)
    K(50, st, None, None, U0 + " građevine osnovne namjene od granice građevne čestice iznosi najmanje h/2, ali ne manje od " + m, "najmanja udaljenost od granice građevne čestice", ">=", mn, "m", vg, zona=Z, izn=I, nej=NO)
    vp = ("pomoćna građevina ugostiteljsko-turističke namjene", "pomoćne građevine ugostiteljsko-turističke namjene", "pomoćne građevine ugostiteljsko-turističke namjene mogu se graditi", 'odredba')
    K(50, st, None, None, "pomoćne građevine ugostiteljsko-turističke namjene mogu se graditi kao prizemnice i na granici građevne čestice", "prislanjanje uz susjednu građevinu ili granicu građevne čestice", "dopustenje", "na granici građevne čestice", "opis", vp, zona=Z, izn=I,
      uv=[("kao prizemnice", 'odredba')])
    K(50, st, None, None, "pomoćne građevine ugostiteljsko-turističke namjene mogu se graditi kao prizemnice", "najveći broj etaža", "=", "prizemnica", None, vp, zona=Z, izn=I)
    K(50, st, None, None, "uz uvjet da se na pročelju koja se nalazi na manjoj udaljenosti od " + otv + " metra od granice čestice ne dozvoljava izgradnja otvora", "drugo: otvori na pročelju bliže granici čestice", "zabrana", float(otv.replace(',', '.')), "m", vp, zona=Z, izn=I,
      uv=[("na pročelju koja se nalazi na manjoj udaljenosti od " + otv + " metra od granice čestice", 'odredba')])
UZ = [("osim u zaštićenim povijesnim cjelinama")]
for kind, izr in [("hotel", "hotele"), ("hotel baština", "hotele baštinu"), ("pansion", "pansione")]:
    vg = (kind, izr, "(odnosi se isključivo na hotele, hotele baštinu i pansione)", 'odredba')
    for v, u in [(5.5, "za dvosmjerne"), (4.5, "za jednosmjerne")]:
        K(50, 2, None, None, "Građevna čestica građevine ugostiteljsko-turističke namjene (odnosi se isključivo na hotele, hotele baštinu i pansione) mora se nalaziti uz prometnu površinu širine najmanje 5,5 metara za dvosmjerne i 4,5 m za jednosmjerne",
          "drugo: najmanja širina prometne površine uz građevnu česticu", ">=", v, "m", vg, uv=[(u, 'odredba')], izn=UZ,
          nej="NEDEFINIRAN_POJAM: »zaštićene povijesne cjeline« – nije jasno jesu li isto što i registrirane i evidentirane povijesne graditeljske cjeline")
vg3 = ("građevina", "građevina", "Najmanja udaljenost između građevina na istoj građevnoj čestici", 'odredba')
N3 = "VRSTA_OPCENITA: subjekt je samo »građevine«"
K(50, 3, None, None, "Najmanja udaljenost između građevina na istoj građevnoj čestici definira se (h1+h2)/2", "najmanja udaljenost između građevina na istoj čestici", ">=", "(h1+h2)/2", "opis", vg3, nej=N3)
K(50, 3, None, None, "Najmanja udaljenost između građevina na istoj građevnoj čestici definira se (h1+h2)/2 (h1 i h2 su visine susjednih građevina), ali ne manje od 6,0 m", "najmanja udaljenost između građevina na istoj čestici", ">=", 6.0, "m", vg3, nej=N3)
pom(50, 4, "uz građevine gospodarske namjene", "Iznimno, " + PZ, "Najmanja dopuštena udaljenost od regulacijskog pravca iznosi 4,0 metra")

for d in OUT:
    if isinstance(d["stavak"], str) and d["stavak"].isdigit(): d["stavak"] = int(d["stavak"])
res = {"generator": "Kandidati generirani skriptom iz doslovnog teksta; svi citati, citati izraza, načina, stanja, zona, uvjeta i iznimki provjereni kao točni podnizovi članka. Ponovljeni blokovi (pomoćne građevine čl. 20/39/50, poljoprivredne gospodarske čl. 22/23/25) generirani istim predloškom. »dvojne i ugrađene« i višestruke vrste razložene na zasebne kandidate. Stavak »1a« ostavljen kao tekst.",
       "kandidati": OUT}
print(len(OUT), ERR)
json.dump(res, open(os.path.join(D, "kandidati.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

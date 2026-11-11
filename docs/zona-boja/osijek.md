# Prijedlog načina gradnje iz šrafure karte – GUP Osijeka

Izvor: ISPU WMS `https://gis{1-4}.mgipu.hr/srv1/PPRasterZ14_Public/wms`, sloj `HR_ISPU_GUP1_03123_R10_KN_2_1`
(GUP Osijeka, kartografski prikaz 4.3.2. „Način gradnje”).

Za razliku od Splita, plohe nisu obojene punom bojom nego crvenom šrafurom na bijeloj podlozi, pa boja jedne točke ne govori ništa.
Razred daje **srednja boja okoline** (prozor 5 × 5 m):

| Način gradnje | Srednja boja plohe (RGB) | s = R − (G+B)/2 | q = (G−B)/s | Gdje je oznaka pročitana (lat, lng) |
|---|---|---|---|---|
| O (obiteljske zgrade) | ≈ 237,155,155 | 80–105 | ≈ 0 | 45.54744, 18.6993 (oznake „O”, „3”, „150”) |
| VS (višestambene zgrade) | ≈ 240,85–100,85–100 | 140–170 | ≈ 0 | 45.55162, 18.69765 (oznake „VS”, „6”, „500”) |
| OVS (obje) | ≈ 235,120–139,80–109 | 110–150 | ≈ 0,27 (narančasti ton) | 45.55250, 18.68997 (oznake „OVS”, „6”, „400”) |

Kalibracija 10. 11. 2026. u pregledniku (app.cesticahr.com): list cijelog grada 1240 × 720 px grupiran je po (s, G−B) u blokovima
5 × 5 px; pojavljuju se samo tri crvene skupine (s≈80–90/0, s≈150–170/0, s≈150/40), siva šrafura ostalih namjena i plava (voda).
Oznake su pročitane na izrezima 0,4 m/px oko navedenih točaka.

Izmjereni ton q: O i VS ≈ 0–0,06; OVS 0,20–0,33 (uzorci 241,117,78 → 0,27; 216,139,109 → 0,33; 229,126,91 → 0,29; 227,131,96 → 0,31;
skupine cijelog grada 150/40, 120/30, 100/20, 90/20).

Pravila (`rules_krk.json → hrGradovi.OSIJEK.zonaBoje.srafura`), prvi koji odgovara; prozor zaglađivanja je 11 × 11 točaka (5,5 m pri 0,5 m/px):
1. OVS: s ≥ 30 i q ≥ 0,18;
2. VS: s ≥ 122 i q < 0,10;
3. O: 45 ≤ s < 122 i q < 0,10;
ostalo (bijelo, sivo, plavo, presvijetlo, dvojbeni ton 0,10–0,18) nije razred. Točka čiji je cijeli prozor izvan lista ostaje prozirna.

Granice ploha iscrtane su dvostrukom punom crvenom linijom; zaglađena izgleda kao pruga šrafure (na stvarnoj karti oko
45.5462, 18.6985 čestica u zoni O dala je 34 % „VS”; sama linija između ploha bez razreda izgleda kao „O”). Zato se u širem prozoru
(33 × 33 točke, `vecina`): (a) točka razreda briše kad razredi zauzimaju manje od 40 % prozora (linija između sivih ili bijelih ploha),
(b) točka prelazi u drugi razred kad ga ima barem 1,5 puta više nego njezinog. Odluka za česticu ima strože pragove nego u Splitu
(`param`: prepoznato barem 60 % uzoraka, sive šrafure najviše 30 %), da čestica druge namjene uz granicu plohe ne dobije prijedlog.
Pravilo većine i ti pragovi provjereni su na umjetnim slikama (test `zonaOsijekTests`, neovisna provjera) i na stvarnoj karti (vidi dolje). Poznati preostali slučajevi (neovisna provjera na umjetnim slikama, 11. 11. 2026.): uska prometnica ili traka druge namjene (do oko 6 m; u
skeneru do oko 8 m) između dviju ploha istog razreda čita se kao taj razred; čestica druge namjene koja je 40–50 % stvarno u plohi
dobiva njezin razred; traka VS uža od 6 m između bijelih površina čita se kao O.

## Provjera na stvarnoj karti i stvarnim česticama (11. 11. 2026.)

U pregledniku (app.cesticahr.com) isti kod (`uzSrafura`, `uzOdluka` s `param`) pokrenut je nad listom KN_2_1 za 491 stvarnu česticu
(granice iz katastarskog sloja DGU-a uživo, točke iz `data/kat_hr/320668.json`) u tri područja:
- 18.6968–18.7006 / 45.5452–45.5472 (ploha O s ulicama i linijama granica): 162 čestice → 138 O, 24 bez prijedloga;
- 18.6862–18.6900 / 45.5514–45.5534 (ploha OVS uz O): 18 čestica → 12 OVS, 4 O, 2 bez prijedloga;
- 18.6900–18.6990 / 45.5535–45.5570 (mješovito O, OVS, VS, druge namjene): 311 čestica → 101 OVS, 63 VS, 21 O, 126 bez prijedloga.

Ukupno 339 prijedloga (163 O, 113 OVS, 63 VS) i 152 odustajanja (114 premalo prepoznate površine – druga namjena, oznake na karti,
ulice; 28 premala čestica; 10 više razreda ili granica kroz česticu). Prijedlozi su pregledani okom na preglednim slikama (obrisi
čestica u boji prijedloga preko karte) i na pojedinačnim izrezima (npr. k.č. 6045 s oznakom gustoće → bez prijedloga; k.č. 8935/20
uz rub plohe OVS → OVS): boja obrisa svugdje odgovara šrafuri ispod; čestice ulica i čestice na oznakama ostaju bez prijedloga;
čestice u plohi O uz liniju granice ostaju O. Pogrešan prijedlog nije uočen. Pregled okom nije potpuna provjera svake čestice, a
istinitost prema lokacijskoj informaciji nije provjeravana.

Skener: slika mora biti 1 m/px ili krupnija (inače poruka „približi kartu”); za svaku česticu čita se pet točaka (središte i četiri na
pola polumjera kruga iste površine) i svih pet mora dati isti razred, inače se čestica ne prikazuje.

Provjera na stvarnoj karti prije pravila većine (kvadratne probne plohe, ne stvarne čestice): 45.5523/18.6965 → VS 100 %;
45.5527/18.6886 → OVS 100 %; 45.5478/18.7003 → O 100 %; 45.5512/18.6960 → VS 100 %; 45.5462/18.6985 → bez prijedloga (O 66 %, VS 34 %, linija granice).

Ograničenja: broj etaža (broj u krugu) i gustoća (broj u zelenom okviru) se ne čitaju; oznake na karti (bijeli krugovi) unutar male
čestice mogu spriječiti prijedlog; DPU-ovi i UPU-ovi nisu uzeti u obzir. Prijedlog je razina C; korisnik ga prihvaća ili odbija.

Zadar (PPUG, list GP_4_RAZV): stambene zone su žuta šrafura različite gustoće bez razlike u tonu (srednje vrijednosti R+G)/2 − B ≈ 14 i ≈ 28
u blokovima 6 × 6 px), preko katastarske podloge. Razlika je mala, a rub plohe uz bijelo izgleda kao rjeđa šrafura, pa prijedlog
zasad nije napravljen; oznake Sm/Ss/Sv nisu povezane s gustoćama.

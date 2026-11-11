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

Pravila (`rules_krk.json → hrGradovi.OSIJEK.zonaBoje.srafura`), prvi koji odgovara:
1. OVS: s ≥ 30 i q ≥ 0,13;
2. VS: s ≥ 122 i q < 0,13;
3. O: 45 ≤ s < 122 i q < 0,13;
ostalo (bijelo, sivo, plavo, presvijetlo) nije razred.

Granice ploha iscrtane su dvostrukom punom crvenom linijom; zaglađena izgleda kao pruga gušće šrafure (na stvarnoj karti oko
45.5462, 18.6985 čestica u zoni O dala je 34 % „VS”). Zato točka razreda prelazi u drugi razred kad ga u prozoru polumjera 8 m ima
barem 1,5 puta više nego njezinog (`vecina`). **Pravilo većine provjereno je samo na umjetnoj slici (test `zonaOsijekTests`), ne i na
stvarnoj karti**, jer je veza s preglednikom prekinuta prije te provjere.

Provjera na stvarnoj karti prije pravila većine (kvadratne probne plohe, ne stvarne čestice): 45.5523/18.6965 → VS 100 %;
45.5527/18.6886 → OVS 100 %; 45.5478/18.7003 → O 100 %; 45.5512/18.6960 → VS 100 %; 45.5462/18.6985 → bez prijedloga (O 66 %, VS 34 %, linija granice).

Ograničenja: broj etaža (broj u krugu) i gustoća (broj u zelenom okviru) se ne čitaju; oznake na karti (bijeli krugovi) unutar male
čestice mogu spriječiti prijedlog; DPU-ovi i UPU-ovi nisu uzeti u obzir. Prijedlog je razina C; korisnik ga prihvaća ili odbija.

Zadar (PPUG, list GP_4_RAZV): stambene zone su žuta šrafura različite gustoće bez razlike u tonu (srednje vrijednosti R+G)/2 − B ≈ 14 i ≈ 28
u blokovima 6 × 6 px), preko katastarske podloge. Razlika je mala, a rub plohe uz bijelo izgleda kao rjeđa šrafura, pa prijedlog
zasad nije napravljen; oznake Sm/Ss/Sv nisu povezane s gustoćama.

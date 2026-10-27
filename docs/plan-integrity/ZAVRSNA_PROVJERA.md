# Plan Integrity v10: završna provjera (27. 10. 2026.)

**Grana:** `plan-integrity-v10-provjera`, napravljena iz `plan-integrity-v1-v10` (5b06440).
- `main` nije diran.
- Ništa nije spojeno.

**Nepromijenjeno:**
- GIS slojevi i simulator;
- postojeće planske vrijednosti u `src/rules_krk.json`. Sažetak pravila bez oznaka pravne provjere i bez novog polja `citati` ima isti SHA-256 kao prije (`6c674162…`), pa ga test čuvara prolazi bez promjene.

## Zadatak 1: kontrolne nedosljednosti (735/76)

| # | Nalaz | Uzrok | Ispravak | Test |
|---|---|---|---|---|
| 1 | »ispunjeno (404 od 300 m²)«, a citat spominje 500 i 300 m² | Primjer je bio za **dvojnu** obiteljsku kuću (prag 300 m², čl. 39. a), ali naziv nije navodio kategoriju. Uz to je citirana skraćena rečenica iz aplikacije: »500 m2 (dvojna i ugrađena: 300 m2)«. To nije doslovni tekst plana i miješa čl. 38. i 39. | Naziv navodi vrstu i način gradnje: »Najmanja površina čestice (obiteljska kuća, dvojna): ispunjeno: 404,4 m² ≥ 300 m²«. Citat je doslovni navod iz čl. 39. a) za dvojnu, odnosno iz čl. 38. a) za slobodnostojeću (500 m², iznimno 400 m²). | PI v10 #1, #1b |
| 2 | Grafička površina 405 m², a u izračunu 404 m² | Tri različite osnovice: atribut katastra 405,0 m²; površina iz koordinata 405,3 m² (Turf, WGS84); izračun koristi dio u građevinskom području naselja: 405,3 × 99,78 % = 404,4 m². Prikaz je zaokruživao na cijeli m². | Nova karika lanca »osnovica izračuna«: površina iz koordinata granice 405,3 m² (atribut katastra 405,0 m²) × udio u GP naselja 99,78 % = 404,4 m². Uz nju: dio izvan GP-a (P3 0,22 %) i pravilo zaokruživanja (uspoređuje se nezaokružena vrijednost; prikaz na 0,1 m²). Isto je u JSON izvještaju (`osnovica`, `zaokruzivanje`). | PI v10 #2 |
| 3 | Izvještaj »NA2 100 %, P3 0 %«, a GIS daje 99,78 / 0,22 % | `Math.round` na cijeli postotak | `udioTxt`: dvije decimale kad bi zaokruživanje dalo 0 % ili 100 % za udio koji to nije (»NA2 99,78 %, P3 0,22 %«). Ispravljeno i za Zagreb. | PI v10 #3 |
| 4 | Uz sukob krova citirana je odredba o etažama | Navod se tražio izrazom `/krov/`, a prvi pogodak bio je »…nadozida za **pot**krovlje« | Lanac koristi doslovne navode čl. 38. d) i čl. 85. st. 2. o nagibu. Kad navod nedostaje, karika je C i »nije potvrđeno«. | PI v10 #4 |

**Novo polje `citati` u `upu["UPU 2"]` (rules_krk.json):**
- **Sadržaj:** 23 doslovna navoda iz SN PGŽ 19/2016, za čl. 38., 39., 40. i 85.
- **Provjera:** test »PI v10 navodi« potvrđuje da je svaki doslovno u svom članku.
- **Bez polja:** za planove bez tog polja lanac uz navod piše »sažetak iz aplikacije, nije doslovni navod« (npr. PPUG Krk, čiji tekst nije u repozitoriju).
- **Pregled:** polje je novi tekst i nije izuzeto od pregleda. Pripremio ga je razvoj, a prema pravilu »tko gradi, ne ocjenjuje« treba ga neovisno pregledati.

## Zadatak 2: dodatni ulazi

- **Krk, vrsta zahvata:** novi izbornik »Vrsta zahvata« s istim popisom kao u Zagrebu.
  - Bez izbora nema zadane vrijednosti. Uvjeti se prikazuju za novu gradnju, uz otvoren uvjet »vrsta zahvata nije odabrana«.
  - Za ostale zahvate prikazuje se upozorenje i otvoren uvjet.
  - Baza pravila dobiva zahvat samo kad je odabran.
- **Zagreb, zahvat:** dosadašnja zadana »nova gradnja« ostaje za prikaz. Bazi pravila zahvat se predaje samo ako ga je korisnik izričito odabrao, pa zadana vrijednost ne postaje prešutni ulaz.
- **Zagreb, vrsta građevine:** izbornik se pojavljuje samo kad pravila baze za lokaciju traže određenu vrstu. Bez izbora ta pravila ne ulaze u izračun. Vrsta (`zgVrsta`) je odvojena od načina gradnje (`tipSel`).
- **Testovi:** pet testova »PI zahvat / PI vrsta«.

## Zadatak 3: čl. 38. i čl. 85.

Analiza je u `cl38-cl85.md`.
- **Čl. 38. d):** vrijedi za sve kuće i stambene građevine u M11/M2 (čl. 39. d i 40. c upućuju na njega). Dopušta ravni krov ili kosi krov od 17° do 23°.
- **Čl. 85. st. 2.:** za zonu »C« traži kosi krov oko 30°.
- **Pravilo o prednosti:** izričitog nema.
- **Sukob:** stvaran normativni sukob, uz nejasan opseg alineje čl. 85. Pogrešno povezivanje postojalo je samo u aplikaciji i ispravljeno je.
- **Zaključak:** automatski nije moguć, potrebno je pravno i konzervatorsko tumačenje. Status ostaje **blokirano**.

## Zadatak 4: audit buduće baze pravila

**Alat:** `tools/baza/audit_pravila.py`. Ništa ne mijenja i ništa ne uvozi. Testovi: `tests/plan_integrity/test_audit.py`, 9/9.

**Što je auditirano.** Izvoz iz ČesticaHR Data Managera nije u repozitoriju, pa je auditirano ono što postoji:
- `tools/baza/primjer_baza.json` (3 pravila);
- 30 pravila UPU-a 2 iz GIS-first pilota, pretvorena u shemu baze: 49 zapisa po vrsti građevine.

| Kategorija | Primjer baze (3) | Pilot UPU 2 (49) | Što radi aplikacija |
|---|---|---|---|
| nerazriješeni uvjeti | 0 | 0 | blokira (v6) |
| iznimke | 0 | 6 (npr. čl. 38. a: iznimno 400 m²; kis iznimno 1,0) | blokira dok `status_iznimke` nije »razriješeno« |
| bez precizne vrste građevine | 1 (`PPUG-KRK-meda`: »sve«) | 0 | »sve« se računa, ali opseg treba potvrditi; prazno = kandidat |
| bez vrste zahvata | 1 | 49 | računa se za svaki zahvat; treba potvrditi da pravilo nije samo za novu gradnju |
| nejasna revizija | 3 | 49 | uvjetno (v5); različita oznaka = blokirano |
| nepotpun ili neodgovarajući citat | 2 (»…«, skraćeno) | 3 (čl. 85.: vrijednost 2, a u tekstu »dvije«) | ručni pregled |

Detalji su u `audit/audit_primjer_baza.json` i `audit/audit_pilot_upu2.json`.

## Zadatak 5: regresija

| Skup | Prije (5b06440) | Sada |
|---|---|---|
| `tests/run.js`, puni skup | 980/980 | **994/994** (+14 testova) |
| Paket PI: v1 9, v2 16, v3 9, v10 15 | 49/49 | 49/49 |
| Audit baze | – | 9/9 |
| Build (`build.py`) | da | da |
| Mobilni `krk.py`, `layout.py` | prolaze | prolaze |
| Mobilni `pwa.py` | 42/42 | 42/42 |
| Mobilni `interaction.py` | pada (redak 53) | pada, isti uzrok (vidi dolje) |

**Uzrok pada testa `interaction.py`.**
- **Što se događa:** u koraku 5 test otvori izbornik slojeva i pokušava uključiti »Sunce« (`#lyrSun`). Pri visini 844 px panel je u stanju »pola zaslona« (vrh 409 px), a `#lyrSun` je na 463 px, pa klik završi na panelu.
- **Kada je počelo:** test je napisan kad je izbornik imao 4 sloja. Mjerenjem u pregledniku:

  | Stanje | `#lyrSun` |
  |---|---|
  | prije d9fe7c9 | 275 px |
  | d9fe7c9 (SKI) | 321 px |
  | 6b85598 (katastar) | 367 px |
  | 48323a7 (DGU ortofoto, 20. 10. 2026.) | **413 px**, prvi put ispod vrha panela |

- **Neovisnost o ovoj integraciji:** test je neovisan o Plan Integrityju. Geometrija je ista na 81ea794 (prije integracije) i na ovoj grani.
- **Zaključak:** to je i stvaran nedostatak sučelja na mobitelu. S panelom na pola zaslona donji slojevi izbornika nisu dostupni dodirom. Nije ispravljen, jer zadatak ne traži promjenu sučelja slojeva.

**Usporedba prije/poslije.** Alat je `tests/plan_integrity/usporedba_prije_poslije.js`, a rezultat `usporedba_prije_poslije.json`: isti odabiri, izgradnja prije 81ea794 i poslije ova grana. Brojevi izračuna nigdje se nisu promijenili. Promijenili su se prikaz i statusi:

| Slučaj | Pokazatelj | Prije | Poslije |
|---|---|---|---|
| 735/76, bez zone | izračun | nema (tekst upozorenja) | `blok-uvjeti` **blokirano** (detaljna zona nije potvrđena) |
| 735/76 | udio namjene | NA2 100 %, P3 0 % | NA2 99,78 %, P3 0,22 % |
| 735/76, M11, dvojna obiteljska | najmanja čestica | nije zapisano | ispunjeno: 404,4 m² ≥ 300 m², **uvjetno** |
| 735/76, M11, dvojna obiteljska | tlocrt / GBP / prostor | 101 / 200 / 133 m², C | isto, C, **uvjetno**, s lancem |
| 735/76, zona »C« | nagib krova | nije zapisano | **blokirano** (sukob čl. 38. d / 85. st. 2.) |
| 735/54, M11 | najmanja čestica | nije zapisano | ispunjeno: 771,8 m² ≥ 300 m², uvjetno |
| 735/54, M11 | tlocrt / GBP / prostor | 150 / 200 / 338 m², C | isto, uvjetno |
| Zagreb 1541/2 | udio namjene | 90 % / 10 % | 90 % / 10 % |
| Zagreb 1541/2 | najmanja čestica | nije zapisano | na granici: 594,0 m² < 600 m², **uvjetno**, otvoren uvjet za čestice manje od propisane |
| Zagreb 1541/2 | tlocrt / GBP / prostor | 178 / 356 / 354 m², B | isto, B, **uvjetno** (karta urbanih pravila iz 2024. nema potvrđenu usklađenost s tekstom iz 2025.) |

U oba prikaza nema JS grešaka.

## Otvorena pitanja

1. **Navodi `citati` (UPU 2)** treba neovisno pregledati (ti ili ChatGPT), jer ih je pripremio razvoj.
2. **Čl. 85. st. 2.:** vrijedi li zahtjev za kosim krovom za svaku novu gradnju u zoni »C« ili samo za gradnju na mjestu postojeće građevine bez vrijednosti? Ima li zona »C« prednost pred čl. 38. d)? To je pravno i konzervatorsko pitanje.
3. **Dio izvan GP-a (P3 0,22 %):** rubni dodir granica slojeva ili stvarni dio čestice? Danas se taj dio isključuje iz osnovice, kao i dosad.
4. **735/54:** raniji podatak 92 / 8 % s današnjim podacima se ne ponavlja (100 % NA2).
5. **Mobilni izbornik slojeva:** donji slojevi nisu dostupni uz panel na pola zaslona (nalaz iz testa `interaction.py`). Treba li to ispraviti?
6. **Izvoz Data Managera:** za pravi audit baze treba izvoz. Ovdje su auditirani samo primjer i pilot-pravila.

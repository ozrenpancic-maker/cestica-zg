# GIS-first pilot: čestica 735/76 k.o. Kornić (Krk)

Status:
- Pilot na grani `pilot-gis-krk` (iz `razvoj`). `main` i produkcija nisu dirani.
- Zamrznuti čitači (v2.6, hibrid v1) nisu dirani, i nije pokrenuto nikakvo novo automatsko čitanje.
- `src/rules_krk.json` nije mijenjan; samo se čita radi usporedbe.
- Stručno potvrđenih ulaza: 0. Pravno potvrđenih pravila: 0.

Demo: privatni artifact »Dosje čestice 735/76 Kornić« (https://claude.ai/artifact/TBVtRUfescK7MFqA3FXtuA).

## 1. Što pilot radi

`dosje.py` sastavlja dosje jedne čestice samo iz ovih izvora:
- javnih vektorskih slojeva (DGU, PGŽ);
- evidencije planova PGŽ;
- službenog teksta plana;
- unaprijed pripremljenih pravila.

AI ne čita plan. Svaka ključna tvrdnja ima lanac **čestica → zona → plan → članak → pravilo → izračun**. Svaka karika nosi razinu dokaza:

| Razina | Ulazi u izračun bez potvrde? |
|---|---|
| službeni vektor (DGU DKP, PGŽ NAMJENA, obuhvat iz IZRADA_PP) | da |
| službena evidencija (PGŽ IZRADA_PP, katalog rastera) | da |
| službena objava (članak postoji u SN PGŽ) | da |
| doslovni citat pravila, strojno provjeren | **ne**, čeka stručnu potvrdu |
| raster, vizualno očitanje (kandidat) | **ne**, čeka stručnu potvrdu |
| stručna potvrda (`potvrde.json`, upisuje samo stručnjak) | da |

**Stanje pokazatelja:**

| Stanje | Kada |
|---|---|
| IZRACUNATO | sve karike su na prihvaćenoj razini |
| UVJETNO | izračunat, ali neka karika čeka potvrdu |
| NIJE_IZRACUNATO | sukob pravila, nedostaje podatak, ili zona isključuje gradnju |

Pravna valjanost je uvijek »nije utvrđena«.

## 2. Rezultat za 735/76

**Utvrđeno iz službenih slojeva (6 činjenica):**
- **Površina:** grafička 405 m² (DGU, podaci od 19. 10.).
  - Lokalni katastar podudara se s izvorom na < 1e-6°.
- **Obuhvat:** čestica je cijela unutar vektorskog obuhvata UPU-a 2 Kornić (IDPLAN 618, 43,24 ha).
  - Granica obuhvata je 5,9 m istočno.
- **Namjena prema PPUG-u:** 99,78 % čestice je u NA2 (izgrađeni dio).
  - To se podudara s čl. 1. UPU-a 2 (»obuhvaća građevinsko područje naselja Kornić - NA 2«).
- **Evidencija planova** (svježe 27. 10.):
  - UPU 2 je VAŽEĆI, SN 2016-19, na snazi od 05.08.2016., bez datuma prestanka;
  - za točku nema UPU-a ni DPU-a u izradi;
  - od 22. 10. promijenio se samo brojač dana izrade.
- **Detaljne zone UPU-a 2:** postoje samo kao 9 rasterskih listova, bez vektorskog sloja.

**Kandidati koji čekaju stručnjaka:**
- zona **M11** (karta 4);
- zona zaštite **»C«** (karta 3A).

Oba su vizualno očitao razvoj 22. 10. 2026. Nisu potvrđeni.

**Pokazatelji (22):**

| Stanje | Broj |
|---|---|
| IZRACUNATO | 0 |
| UVJETNO | 20 |
| NIJE_IZRACUNATO | 2 |

Uvjetno, ako je zona M11:
- **Što je moguće po površini:**
  - dvojna i ugrađena obiteljska kuća;
  - dvojna višeobiteljska kuća (rezerva samo 5 m² prema grafičkoj površini);
  - slobodnostojeća obiteljska kuća samo po iznimci od 400 m², čiji se uvjet okruženja iz podataka ne može provjeriti;
  - slobodnostojeća višeobiteljska i stambena građevina nisu moguće.
- **Tlocrt:** najviše 101,2 m² (ugrađena 100 m²).
- **GBP:** obiteljska 200 m², dvojna višeobiteljska 303,8 m².
- **Ostalo:** 2 nadzemne etaže, visina 7,5 m, međa 4 m (3 m bez otvora), zelenilo najmanje 162 m², 2 parkirna mjesta po stanu.
- **Konzervatorski uvjeti:** obvezni u zoni »C«.

Ne računa se:
- **Nagib krova:** čl. 38. d) traži 17°–23° ili ravni krov, a čl. 85. za zonu »C« kosi krov oko 30°.
- **Udaljenost od ceste:** kategorija ceste nije poznata.

**Otvorena pitanja (10):** zona M11; zona »B«/»C«; sukob oko krova; uvjet iznimke od 400 m²; površina u zemljišnoj knjizi; kategorija ceste; pravna aktualnost UPU-a 2; stupanje na snagu 05. ili 06. 08. 2016.; ulazi li podrum u kis; 3 etaže na nagibu u zoni »C«.

**Testovi:** `python3 tools/gis-pilot/test_dosje.py` prolazi 28/28. Pokrivaju:
- kontrolne sume;
- geometriju;
- doslovne citate, uključujući negativni test;
- podudaranje s `rules_krk.json` (23/23);
- da bez potvrda ništa nije IZRACUNATO;
- da potvrda zone ne potvrđuje pravila;
- da zona D2 ili zona »B« blokira izračun;
- da izvan zone »C« krov postaje izračunljiv;
- da pravna razina ostaje »nije utvrđena«.

## 3. Koliko podataka imamo

| Ulaz | Stanje |
|---|---|
| granica i grafička površina čestice, evidencija planova, obuhvat UPU-a, namjena PPUG-a, puni tekst odredbi | **ima** (5) |
| detaljna zona UPU-a, zona zaštite, pripremljena pravila | **kandidat** (3) |
| ZK površina, pravna aktualnost, kategorija ceste, nagib terena, uvjet »okruženja« | **nema** (5) |

Po karikama lanaca (22 pokazatelja):
- 98 karika je na prihvaćenoj razini (vektor, evidencija, objava);
- 78 čeka potvrdu: 54 pravila i 24 rasterske zone.

## 4. Koliko stručnog rada traži jedno područje

Jedna priprema UPU-a 2 vrijedi za **1.184 katastarske čestice** u obuhvatu. Po grafičkoj površini:

| Površina | Čestica |
|---|---|
| manje od 300 m² | 734 |
| 300–399 m² | 102 |
| 400–499 m² | 110 |
| 500 m² i više | 238 |

Katastarska čestica nije isto što i građevna čestica.

| Posao | Jednom po | Količina |
|---|---|---|
| potvrditi pripremljena pravila (postojeći alat za pregled) | planu | 30 pravila, čl. 37.–40. i 85. |
| digitalizirati zone s karte 4 | planu | 43,24 ha; broj zona nije prebrojan |
| digitalizirati zone »B« i »C« s karte 3A | planu | 2 zone |
| riješiti sukobe u tekstu | planu | 4 pitanja |
| provjeriti pravnu aktualnost | planu i svakom novom broju SN | 1 |
| ZK površina, kategorija ceste, uvjet okruženja | čestici | 3 pitanja |

**Ljudsko vrijeme nije izmjereno** i ovdje se ne procjenjuje. Za pravila se može izmjeriti istim alatom za pregled kao u pilotu Travičića. Za digitalizaciju treba jedno mjereno stručno radno vrijeme.

**Strojno vrijeme:**

| Korak | Vrijeme |
|---|---|
| dosje | 0,1 s |
| stranica | 0,35 s |
| svježi upiti PGŽ-u (4 upita, preglednik) | ispod 1 s |

## 5. Zaključak

Koristan proizvod bez univerzalnog čitača je moguć, ali samo uz jednokratnu stručnu pripremu po planu:

- **Bez ikakvog čitanja plana**, iz javnih vektora i evidencije, sustav pouzdano kaže:
  - koja je čestica, kolika je i gdje je;
  - koji plan vrijedi i od kada;
  - je li čestica u obuhvatu;
  - koja je namjena prema PPUG-u.
- **Usko grlo nije tekst nego grafika:**
  - pravila se jednom pripreme ručno (30 pravila za UPU 2) i strojno provjere doslovnim citatom;
  - detaljne zone UPU-a postoje samo na rasteru, pa sve što ovisi o zoni ostaje uvjetno dok stručnjak ne digitalizira kartu 4 i kartu 3A ili ne potvrdi zonu po čestici.
- **Kad se zona i pravila jednom potvrde**, isti postupak vrijedi za svih 1.184 čestica u obuhvatu, a po čestici ostaju samo 3 lokalna pitanja.
- **Isti posao bez potvrde ne smije postati činjenica:** pilot to tehnički sprječava.

**Preporuka:**
- Sljedeći korak je mjereno stručno radno vrijeme za UPU 2:
  - potvrda 30 pravila u alatu za pregled;
  - digitalizacija karte 4 i karte 3A.
- Tako se dobiva stvarna cijena pripreme područja.
- Nastavljati AI čitanje nema smisla dok to ne pokaže da je čitanje teksta skuplje od digitalizacije.

## 6. Datoteke

| Datoteka | Svrha |
|---|---|
| `dosje.py` | lanac, razine dokaza, pokazatelji, otvorena pitanja |
| `pravila_upu2_pripremljena.json` | 30 pravila i 3 okvirne odredbe s doslovnim citatima |
| `potvrde.json` | stručne potvrde (prazno) |
| `izvori/pgz-2026-10-27/` | svježi odgovori PGŽ-a (evidencija, obuhvat UPU-a 2, katalog rastera) sa SHA-256 |
| `sastavi.py`, `izvjestaj.template.html` | demo stranica i `dist/mjerenje.json` |
| `test_dosje.py` | 28 testova |

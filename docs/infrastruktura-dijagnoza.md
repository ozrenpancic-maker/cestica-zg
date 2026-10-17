# Komunalna infrastruktura: dijagnoza i plan popravka (17. 10. 2026.)

## 1. Zašto aplikacija ne prikazuje udaljenosti

**Kod nije pokvaren. Ne postoji izvor uličnih mreža.** Modul ispravno radi s jedinim slojevima koje ima, a to su glavni vodovi iz GUP-a. Za vodovod, kanalizaciju, struju i plin u ulici nema podataka, pa su četiri retka namjerno postavljena na "podaci nisu dostupni".

Provjera točku po točku. Testirano je u testnom okruženju s lažnim vodom na poznatoj udaljenosti, a gradski servisi su provjereni izravnim upitima.

| # | Pitanje | Nalaz |
|---|---|---|
| 1 | Poziva li se `loadInfra` i završava li? | Da. Poziva se u `inspect()` nakon provjera slojeva i završava bez greške (8 upita, 0 grešaka). |
| 2 | Koji slojevi i ima li linija? | `3c_voda…/26` (magistralni vodoopskrbni cjevovod, 271 objekt), `GUP_Infrastruktura` 12, 13 (dalekovodi i kabeli 110 i 400 kV, 222 objekta), 14, 15 (samo **magistralni** i **VT** plinovod, 610 objekata), 1, 2 (trafostanice 110 kV) i 22 (toplovod). Sve su linije ili točke, ali **nijedna nije ulična distribucijska mreža**. GUP nema sloj kanalizacije s vodovima. |
| 3 | Postoji li izračun udaljenosti od granice? | Da: `minDistM()` računa najmanju udaljenost između granice čestice i voda u oba smjera (vrhovi voda prema stranicama čestice i obrnuto), a za vod koji siječe česticu daje 0. Test: vod 40 m od istočnog ruba daje **39,95 m**; od središta bi bilo oko 55 m. |
| 4 | Koordinate i metrika | Upiti traže i vraćaju WGS84 (`inSR`/`outSR` 4326). Udaljenosti se računaju geodetski (turf, metri). Ispravno. |
| 5 | Je li rezultat povezan s prikazom? | **Djelomično, i to je glavni uzrok.** Četiri retka (Vodovod, Kanalizacija, Struja, Plin) uvijek pišu "podaci nisu dostupni". Tako je postavljeno 17. 10. na tvoj zahtjev, jer ulične mreže nisu javne. Udaljenosti glavnih vodova iz GUP-a izračunaju se, ali vide se samo u sklopljenom popisu "Glavni vodovi iz GUP-a u blizini", i to samo do 300 m. |
| 6 | JS greške, mreža, CORS | U testu nema JS grešaka. Gradski servisi su na ArcGIS Onlineu i podržavaju CORS; u produkciji su se prikazivali (zato je prije bio dugačak tekst). Za DGU nije provjereno, vidi odjeljak 2. |
| 7 | Nedostupno ili ne postoji? | Djelomično. Kad gradski servisi ne odgovore, piše "trenutno nisu dostupni" i nudi se ponovni pokušaj. **Kad rade, a u 300 m nema glavnog voda, ne piše ništa.** To treba popraviti. Neuspjeh jednog sloja dok drugi rade također se ne prikazuje. |

**Zaključak:** iz GUP slojeva ne mogu se pouzdano izračunati udaljenosti do kućnog priključka. To su magistralni vodovi u mjerilu plana, na koje se kuća ne priključuje. Te slojeve zato ne treba koristiti za četiri tražena retka.

## 2. Izvori: što stvarno radi

| Izvor | Mreže | Geometrija | Stanje | Za udaljenost do voda u ulici |
|---|---|---|---|---|
| Grad Zagreb, ArcGIS: `GUP_Infrastruktura`, `3c_voda…`, `EnergijaGUP`, `3b_energija…` | glavni vodovi (110 kV i jači, magistralni i VT plin, magistralni vodovod, toplovod) | linije, WGS84 | **radi** (provjereno upitima) | **ne** (nisu ulične mreže) |
| Grad Zagreb: `Javni_vodovod`, `Javna_kanalizacija`, `Elektricna_energija` | — | **nema** (samo tablice statistike) | radi | ne |
| Grad Zagreb: `KI_LINIJE` (katastar infrastrukture) | razno | linije | radi | ne (probno područje od oko 140 × 110 m) |
| **DGU SKI, ATOM (GML)**: vodovod `…_21.zip` 12,9 MB, kanalizacija 5,5 MB, struja 23,3 MB | vodovod, odvodnja, elektroenergetska mreža (+ toplovod) | linije, EPSG:3035 | datoteke postoje (19. 7. 2024.); **sadržaj nije pregledan** | **moguće**, ovisi o sadržaju |
| **DGU SKI, WMS** `ski.dgu.hr/inspire/wms` | sve četiri + toplovod; **plin samo ovdje** (`US.OilGasChemicalsNetwork`) | samo slika i GetFeatureInfo (tekst ili HTML, **bez geometrije**) | servis odgovara; sadržaj odgovora i CORS nisu provjereni | udaljenost samo približno, mjerenjem na slici karte |

**Zašto DGU nije do kraja provjeren:** moja radna okolina ne smije preuzimati s `ski.dgu.hr`. Alat za čitanje weba vidi popis slojeva, ali odgovor upita za točku i sliku karte vraća kao nečitljiv binarni sadržaj. Zato ni potpunost ni točnost zagrebačkih podataka nisu potvrđene. Grad navodi da upravitelji dostavljaju "dio podataka", a priručnik SKI-ja ne navodi točnost ni potpunost.

## 3. Plan popravka

### Korak 0: odmah, bez novih izvora (ja; samo uz tvoje odobrenje)
- Kad gradski servisi rade, a u 300 m nema glavnog voda, napisati "Glavni vodovi iz GUP-a: nijedan u krugu od 300 m" umjesto praznine.
- Kad neki od slojeva GUP-a ne odgovori, a drugi rade, to jasno navesti.
- Četiri retka ostaju "Podaci nisu dostupni" dok ne dođe pouzdan izvor. Nikad 0 m ni "nema infrastrukture".

### Korak 1: provjera DGU podataka (ti, oko 15 minuta)
1. U pregledniku preuzmi tri datoteke za Grad Zagreb i pošalji mi ih ovdje:
   - `https://ski.dgu.hr/inspire/atom/INSPIRE_WaterNetwork_(US-NET-WA)_21.zip`
   - `https://ski.dgu.hr/inspire/atom/INSPIRE_SewerNetwork_(US-NET-SW)_21.zip`
   - `https://ski.dgu.hr/inspire/atom/INSPIRE_ElectricityNetwork_(US-NET-EL)_21.zip`
2. Na `ski.dgu.hr/gis` otvori 2–3 čestice za koje znaš gdje su priključci, npr. Liševo. Uključi slojeve vodovoda, kanalizacije, struje i plina i javi mi vide li se vodovi u ulici.
3. U aplikaciji: ☰ → Stanje servisa → redak "DGU katastar infrastrukture (WMS…)". Javi je li zelen, jer to pokazuje dopušta li DGU pristup iz preglednika (CORS).

### Korak 2: analiza datoteka (ja)
- Utvrđujem koje vrste objekata i atributi postoje (vrsta voda, napon, materijal, upravitelj), koliki je obuhvat Zagreba i postoje li ulični vodovi ili samo glavni.
- Pretvaram EPSG:3035 → WGS84 provjerenom knjižnicom (pyproj) i provjeravam točnost pretvorbe na poznatim točkama.
- Pišem izvještaj kvalitete po mreži. Odluka je tvoja: koristimo ili ne.

### Korak 3: integracija (ja, ako podaci prođu korak 2)
- **Bez promjene hostinga:** pripremljene, pojednostavljene linije spremaju se kao male datoteke po kvadratima od oko 1 km uz aplikaciju. Aplikacija učita samo kvadrate oko čestice, pa nema ovisnosti o DGU servisu ni o CORS-u.
- Udaljenost se računa postojećom `minDistM()`, od **granice** čestice, u krugu do 500 m:
  - `VODOVOD — najbliži evidentirani vod: X m`
  - `KANALIZACIJA — najbliži evidentirani vod: X m`
  - `STRUJA — najbliži evidentirani odgovarajući vod: X m`. "Odgovarajući" znači niskonaponski ili srednjenaponski distribucijski vod, ne 110 kV; filtar se određuje po atributu napona nakon koraka 2.
  - uz svaki redak: izvor (DGU SKI, 19. 7. 2024.) i napomena da evidencija može biti nepotpuna i da priključenje potvrđuje distributer (ViO, HEP ODS).
- **PLIN:** u ATOM-u nema podataka. Dvije mogućnosti:
  - **(a)** "Podaci nisu dostupni", dok se ne dobije izvor od DGU-a ili Gradske plinare.
  - **(b)** približno mjerenje na slici WMS karte. Traži provjeru CORS-a (korak 1.3) ili posredovanje preko Workera, a prikaz bi bio označen kao "približno, iz karte".
  - **Preporuka: (a).**
- Isti podaci idu u analizu rizika i u AI kontekst (`getInfrastructure`), tako da AI razlikuje udaljenost evidentiranog voda od mogućnosti priključenja.

### Korak 4: testovi
- poznate udaljenosti od granice (ne od središta);
- vod koji siječe česticu daje 0 m, ali uz natpis "vod prolazi česticom", ne kao "0 m do priključka";
- pretvorba koordinata;
- slučajevi "kvadrat nije učitan", "servis pao" i "nema voda u krugu";
- mobilni prikaz.

## 4. Odluka koju trebam od tebe

Kad su DGU podaci za područje učitani, a u krugu od 500 m nema nijednog evidentiranog voda, što prikazati?
- **(A)** "Nije evidentiran vod u krugu od 500 m (evidencija može biti nepotpuna)". To je informacija, a nije tvrdnja da mreže nema.
- **(B)** "Podaci nisu dostupni".

Za slučaj kad izvor ne odgovori ili ne pokriva područje uvijek se prikazuje "Podaci nisu dostupni".

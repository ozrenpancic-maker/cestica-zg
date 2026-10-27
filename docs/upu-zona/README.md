# Sažetak uvjeta gradnje i pilot prijedloga detaljne zone (UPU 2 Kornić)

Grana `sazetak-zone-upu2` (iz `razvoj` 3188619), 27. 10. 2026. Ništa nije spojeno u `main` ni u `razvoj`.

## 1. Što je iskorišteno, a što je novo

**Iskorišteno bez promjene:**
- katastarska geometrija (data/kat_krk) i GIS presjek namjene;
- prepoznavanje UPU-a 2 i listova (`rkPoznatiList`, `RASTER_KATALOZI`);
- izrez karte 4 u HTRS96/TM s granicom čestice u pikselima (`RK_ARCGIS.img`);
- ručni odabir zone i zone zaštite (`krkZonaSet`, `krkZastSet`);
- registar pouzdanosti A/B/C (`PZREG`, `pz`, `pzUser`);
- Plan Integrity v10: `piObjava`, karike lanca, `piBlok`, `piReport` / JSON izvoz;
- usporedba površina (`areaSel`, `__areaCmp.calc`);
- doslovni navodi (`citati`) i njihova provjera prema tekstu SN PGŽ 19/2016.

**Novo:**
- `piSazetakHtml`: tablica pokazatelja na vrhu „Uvjeta gradnje” (Krk i Zagreb). Sadrži:
  - vrijednost, status (izvedeno / uvjetno / blokirano) i oznaku A/B/C;
  - kratko upozorenje;
  - puni lanac na dodir retka;
  - zajedničke izvore prikazane jednom;
  - popis „Što još moraš provjeriti”.

  Stari `piLanacHtml` (lanac ponovljen po pokazatelju) sada vraća prazno. Dokazi, citati, revizije i JSON izvoz ostaju u retcima i u izvještaju.
- `calc-visina` (Krk), s doslovnim navodom čl. 38. b) / 39. b) / 40. b) u `citati.*.visina`. Navod provjerava postojeći test doslovnosti. Otvoreni uvjeti:
  - kota zaravnatog terena;
  - kosi teren za višeobiteljske i stambene građevine;
  - zona »C«.
- Iznimka: kad je ispunjen samo prag iznimke, piše „Površina zadovoljava brojčani prag iznimke, ali primjenjivost iznimke nije potvrđena”. To vrijedi u retku izračuna, u sažetku, u čipovima, u usporedbi površina i u usporedbi tipova.
- `piOsniviceHtml`: utjecaj izbora osnovice (grafička / katastar / ZK) na najmanju česticu, tlocrt i GBP. Uz to stoji napomena da odabrana površina nije službeno utvrđena površina građevne čestice.
- Pilot zone:
  - čiste funkcije `uzHist`, `uzBoja`, `uzOdluka`;
  - `uzPrijedlog`: dohvat izreza i očitanje piksela u pregledniku;
  - sučelje: prihvati / odaberi drugu / odbij, dokaz i neizvjesnost;
  - zapis izvora prihvaćene zone (`krkZonaIzvor:<čestica>`);
  - `uzProvjereno`: stručna provjera vrijedi samo za točnu česticu i reviziju lista; zapisanih provjera je 0.
- Boje legende karte 4 u `rules_krk.json` (`karte.listovi.4.legenda`, s izvorom).

## 2. Postupak prijedloga zone

1. **Vektor.** Službeni vektor detaljnih zona nije javno dostupan:
   - PGŽ `STANJE` i `PREGLEDNIK` imaju samo obuhvate planova;
   - sloj `JLS/jls_grad_krk` traži prijavu (HTTP 401).

   Zato se koristi raster karte 4 (PP_RASTERI, sloj 5, OBJECTID 7104).
2. **Razredi boja.** Izrez se očitava u pregledniku (CORS dopušta `getImageData`). Svaki uzorak (korak oko 0,25 m) dobiva razred:
   - *tamno*: linije i tekst; ne broji se;
   - *bijelo*: prometnice i podloga;
   - *sivo*;
   - zona iz legende, ili *nepoznato*.

   Za zone se koristi udaljenost tona, zasićenosti i svjetline do boje polja legende. Skenirana karta tamnija je od rastera legende, pa se ton čuva bolje od samih RGB vrijednosti.
3. **Pojasi.** Unutrašnjost čestice počinje 1 m od granice, zbog georeferenciranja i linija. Pojas od 0 do 6 m izvan granice služi samo za upozorenje »blizu granice zone«.
4. **Odustajanje.** Algoritam odustaje ako vrijedi bilo što od sljedećeg:
   - premalo uzoraka;
   - prozirni list;
   - manje od 60 % prepoznatih boja među uzorcima koji nisu linije ili tekst;
   - više od 20 % bijelog;
   - najčešća zona ima manje od 80 % obojenih uzoraka.
5. **Bez postotka pouzdanosti.** Postotak pouzdanosti se ne iskazuje. Prikazuju se udjeli razreda, pojas, izvor (list, šifra, legenda) i razlučivost.
6. **Status.** Prihvaćeni prijedlog ostaje razina C, uz izvor »prihvaćen automatski prijedlog iz rastera (pilot)«. Vrijedi samo za tu česticu. Ručna promjena zone briše zapis o prijedlogu.
7. **Uključivanje.** Pilot je **isključen za sve korisnike** (`FEATURES.upuZona=false`). Ispitivač ga uključuje adresom `?pilot=zona`, a isključuje s `?pilot=ne`.

## 3. Referentni skupovi i pragovi

Oznake su dali neovisni AI agenti koji nisu vidjeli kod ni rezultate. Zonu su očitali vizualno s karte 4 i legende, pa to **nije stručna potvrda**.

| Skup | Čestice | Uloga |
|---|---|---|
| razvojni | 42 (`tools/upu-zona/referentni_uzorak.json`, sjeme 20261027, uz 735/76 i 735/54) | izbor prostora boja i pragova; mreža od 13 800 kombinacija, kazna 5 za pogrešan prijedlog |
| slijepi | 40 (`slijepi_uzorak.json`, sjeme 20261028, bez čestica razvojnog skupa) | označen i ocijenjen tek nakon što su parametri zaključani |

Kriterij ocjene ovisi o referentnoj oznaci:
- **Jasna zona:** ishod je *točno*, *propušteno* (algoritam je odustao) ili *pogrešno*.
- **MJEŠOVITO, CESTA ili IZVAN:** točno je samo odustajanje.

| | Razvojni (42) | Slijepi (40) |
|---|---|---|
| prijedloga dano | 35 | 33 |
| točnih prijedloga | 34 | 31 |
| pogrešnih prijedloga | 1 | 2 |
| ispravno odustao (mješovito / cesta) | 4 od 5 | 0 od 2 |
| odustao, a zona je jasna | 3 | 7 |
| zamjena M11 ↔ M2 | 0 | 0 |

Na slijepom skupu:
- od 38 čestica s jasnom zonom 31 je točna, a za 7 algoritam nije dao prijedlog;
- nijedna čestica s jasnom zonom nije dobila krivu zonu.

Obje pogreške su čestice koje je označivač proglasio mješovitima, a algoritam je ponudio većinsku zonu M11:
- 181/8: M11 55 %, izvan obuhvata 45 %;
- 1478/221: M11 65 %, M12 20 %, cesta 15 %. Prijedlog je bio uz upozorenje »blizu granice«.

U razvojnom skupu pogreška je 1482/1. Označivač je zabilježio cestu 40 %, a algoritam je na čestici našao 0 % bijelog.

**Propušteni slučajevi:**
- čestice na bijelim prometnicama;
- šrafura D8 (*40/1);
- zaštitno zelenilo Z (90, 1506/4, 91): oznake i bijela podloga smanjuju udio boja;
- dijelovi s oznakama TS/D8 (*38).

Pojedinosti po čestici su u `rezultati_2026-10-27.json`. Odabrani parametri su `UZ_PARAM` u aplikaciji.

**Odluka:** pilot se ne uključuje svima, iz tri razloga:
- uzorak je mali;
- oznake nisu stručne;
- mješovite čestice dobivaju prijedlog većinske zone.

## 4. Testovi

- `tests/run.js`: 1029 / 1029. Novi testovi:
  - sažetak za 735/76, 735/54 i Zagreb 1541/2;
  - visina s doslovnim navodom;
  - tekst iznimke;
  - osnovice površine;
  - sintetičke slike (granica, šrafura, linije, bijelo, prozirno, nepoznata boja, premalo uzoraka);
  - stvarni histogrami 735/76 i 88/7;
  - cijeli put od piksela do odluke na spremljenom izrezu karte 4 (735/76 → M11);
  - nedostupan izvor;
  - obuhvat provjere vrijedi samo za česticu i reviziju;
  - pilot isključen po zadanom.
- `tests/plan_integrity/*`: 9 / 16 / 9 / 15, audit 9 / 9.
- Usporedba prije / poslije (`usporedba_prije_poslije.js`, razvoj → grana): svi postojeći pokazatelji za 735/76, 735/54 i Zagreb imaju iste vrijednosti, A/B/C i status. Novi je samo `calc-visina` (7,5 m, C, uvjetno).
- Mobitel i PWA:
  - `layout`, `interaction` (svi slojevi dostupni dodirom), `krk`, `pwa` 42 / 42;
  - novi `mobile/sazetak.py`: 735/76 sa spremljenim odgovorima PGŽ-a, kandidat M11, prihvaćanje → zona M11 (C), zona »C« → krov blokiran. Na 1280 i 390 px nema vodoravnog pomicanja ni JS grešaka.
- Trajanje u Chromiumu:
  - čestica 35 × 25 m: oko 140 ms;
  - čestica 60 × 60 m sa 120 vrhova: oko 480 ms.

  Izračun počinje tek nakon što se slika izreza učita.

## 5. Otvoreni tehnički i pravni problemi

- **Oznake i potvrda:**
  - referentne oznake su vizualne i daju ih AI agenti; za mjerodavnu točnost treba stručni referentni skup (npr. lokacijske informacije);
  - nijedna zona nije stručno provjerena (`provjereno` = []).
- **Algoritam:**
  - mješovite čestice s većinskom zonom (više od 80 % boje) dobivaju prijedlog. Moguća poboljšanja: strože odustajanje kad pojas sadrži drugu zonu, ili upozorenje »dio čestice izvan obuhvata«;
  - šrafure (D2/D8, TS) i zelenilo uz oznake često završavaju odustajanjem; prototip boje za TS nije uzorkovan;
  - boje su uzete iz rastera legende ministarstva, ne iz same karte. Drugi UPU traži novo uzorkovanje i novu validaciju.
- **Podaci i sučelje:**
  - georeferenciranje skeniranog lista i katastra može se razlikovati za nekoliko metara;
  - spremljeni ispitni izrez (180 m, 0,225 m/px) grublji je od izreza u aplikaciji (60 m, 0,075 m/px);
  - izračun traje do oko 0,5 s na glavnoj niti; za veće čestice bolji je Web Worker;
  - u osnovnom prikazu prijedlog je u „Uvjetima gradnje”; puni izrez karte vidi se tek u naprednom prikazu.
- **Pravno:** prihvaćena zona i dalje je pretpostavka korisnika (C). Mjerodavna je lokacijska informacija. Pravno potvrđenih pravila ostaje 0.

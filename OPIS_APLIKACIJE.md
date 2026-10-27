# Čestica HR: detaljan opis aplikacije

Stanje: 27. 10. 2026., grana `sazetak-zone-upu2`. Ova grana je izvedena iz `razvoj` i nije spojena u `main`.
Repozitorij: `ozrenpancic-maker/cestica-zg`. Objavljena verzija (`main`): https://ozrenpancic-maker.github.io/cestica-zg/

Dokument je za drugi AI alat ili programera koji nastavlja rad. Opisuje što aplikacija radi, kako je građena, odakle uzima podatke, koja pravila rada vrijede i što je još otvoreno.

---

## 1. Svrha

Čestica HR je mobilna web aplikacija (PWA) za provjeru zemljišta u Hrvatskoj. Korisnik dodirne točku na karti ili upiše adresu ili broj čestice. Aplikacija tada pokaže:

- katastarsku česticu: granicu, površinu, k.o. i podatke iz zemljišne knjige gdje su dostupni;
- prostorne planove koji vrijede na lokaciji (važeći, u izradi, van snage) i namjenu površine;
- uvjete gradnje iz plana: najmanju česticu, izgrađenost (kig), iskoristivost (kis), tlocrt, GBP, visinu, etaže i udaljenosti od međa i ceste. Uz svaki uvjet stoji članak plana i doslovni citat;
- teorijski prostor za gradnju na čestici, prikazan na karti i u 3D;
- rizike: klizišta, poplave, zaštićena područja, Natura 2000 i zaštitu baštine;
- infrastrukturu: udaljenosti do vodovoda, kanalizacije i niskonaponske mreže;
- troškove: komunalni doprinos, priključke, upravne pristojbe i orijentacijsku cijenu gradnje;
- sunce i energiju, pristup i okolinu, popis dokumentacije i ureda.

Za svaki podatak prikazuje se **izvor, datum i razina pouzdanosti (A/B/C)**. Ništa se ne izmišlja: kad podatak nedostaje, piše „Podaci nisu dostupni”. Pravno mjerodavna je uvijek lokacijska informacija nadležnog tijela, a aplikacija je orijentacijska.

Korisnici su građani i kupci zemljišta, projektanti i agenti. Sučelje je na hrvatskom, uz tri razine prikaza: osnovno, napredno i mobilno.

## 2. Pokrivenost

| Područje | Opseg |
|---|---|
| **Grad Zagreb** | Puna analiza. Obuhvaća:<br>• čestice Grada (2023.);<br>• GUP Zagreba: namjena i urbana pravila (pročišćeni tekst 2025., karta urbanih pravila iz javne rasprave 2024.);<br>• GUP Sesveta 2026. (prijedlog);<br>• PPGZ izvan GUP-ova;<br>• klizišta, infrastruktura (DGU SKI i karte GUP-a), komunalni doprinos i 3D zgrada. |
| **Otok Krk (pilot)** | Uključuje:<br>• čestice iz DGU DKP-a, pripremljene uz aplikaciju;<br>• namjena i evidencija planova PGŽ-a;<br>• rasterske karte UPU-a i DPU-a izrezane oko čestice;<br>• uvjeti gradnje: Grad Krk (PPUG te UPU 1, 2 i 5), Malinska, Baška, djelomično Vrbnik; Punat na `razvoj`;<br>• komunalni doprinos Grada Krka i infrastruktura. |
| **Primorsko-goranska županija** | Čestica uživo iz DGU-a, namjena i planovi PGŽ-a; uvjeti gradnje samo za obrađene JLS-ove. |
| **Ostatak Hrvatske** | Osnovni pregled: čestica (DGU), ZK, okoliš, teren i 3D. |

Glavni kontrolni slučajevi u testovima:
- **735/76 k.o. Kornić** (UPU 2 Kornić, zona M11);
- **735/54 k.o. Kornić**;
- **1541/2 k.o. Remete** (Zagreb, pravilo 2.2.).

## 3. Tehnička arhitektura

- **Jedna HTML datoteka.** Sav kod (HTML, CSS i JS, bez frameworka) je u `src/app.template.html`, oko 9 100 redaka. `python3 build.py` od nje sastavlja `index.html` i `sw.js`. Pri tome:
  - ugrađuje pravila (`src/rules*.json`);
  - provjerava njihovu strukturu i prekida ako nešto nedostaje;
  - upisuje oznaku verzije (datum i vrijeme izrade).

  Ručno se ne uređuju ni `index.html` ni `sw.js`.
- **Knjižnice** (lokalno u `vendor/`, s licencama):
  - Leaflet 1.9.4 (karta);
  - Turf 6.5.0 (geometrija, površine, presjeci);
  - MapLibre GL 4.7.1 (3D prikaz).
- **Hosting.** Statički GitHub Pages. Nema poslužitelja; svi upiti idu iz preglednika izravno javnim servisima (CORS).
- **PWA.** `manifest.webmanifest`, service worker (`src/sw.template.js` → `sw.js`) i ikone u `icons/`. Aplikacija se instalira na Android s mreže.
- **Projekcija.** HTRS96/TM (EPSG:3765) preko funkcija `tmFwd` i `tmInv` u kodu. Površine se računaju na elipsoidu (Turf).
- **Pomoćni poslužitelji** (nisu nužni za osnovni rad):
  - `worker/`: Cloudflare Worker za AI asistenta, isključen;
  - `tools/oss-posrednik`: posrednik za OSS (zemljišna knjiga). Ako ne odgovara, aplikacija nudi ručni unos ili učitavanje PDF izvatka.
- **Lokalno pohranjeno** (localStorage, po čestici; nikad se ne prenosi na drugu česticu): odabrani tip kuće, način gradnje, zahvat, zona UPU-a, zona zaštite, ZK površina, spremljene čestice i investicije.
- **Zastavice** `FEATURES` u kodu:

  | Zastavica | Stanje | Značenje |
  |---|---|---|
  | `infra` | `true` | infrastruktura |
  | `seis` | `false` | potresna opasnost, skrivena |
  | `ai` | `false` | AI asistent |
  | `upuZona` | `false` | pilot prijedloga zone; ispitivač ga uključuje dodavanjem `?pilot=zona` na adresu |

## 4. Izvori podataka

| Izvor | Što daje | Napomena |
|---|---|---|
| Grad Zagreb, ArcGIS servisi | čestice (2023.), planirana namjena GUP-a, urbana pravila, provjere, klizišta | vektorski REST |
| Odluka o GUP-u Zagreba (pročišćeni tekst 2025.), GUP Sesveta 2026., PPGZ 2017. | urbana pravila | `src/rules.json`, `rules_sesvete.json`, `rules_ppgz.json`; parseri `src/parse_*.py` |
| DGU: DKP (ATOM), WFS, SKI (INSPIRE GML) | čestice (Krk unaprijed: `data/kat_krk/`), vodovod, kanalizacija, NN mreža | `data/ski`, `data/ski_krk`; skripte u `tools/katastar`, `tools/ski` |
| PGŽ GEOPORTAL `gisportal.pgz.hr` | Tri servisa:<br>• `STANJE/IZRADA_PP`: planovi na točki (vrsta, status, SN, datum);<br>• `STANJE/NAMJENA_POVRSINA_NOVO`: namjena, oznaka zone, izgrađenost;<br>• `PP_RASTERI`: rasterske karte UPU-a i DPU-a, sloj 5/12 UPU i 6/13 DPU, export izreza u EPSG:3765. | vektor po točki i poligonu; detaljne zone UPU-a postoje samo kao raster |
| Ministarstvo prostornoga uređenja (ISPU WMS) | karte GUP-a i UPU-a Zagreba | `src/ispu_sifre.json` (provjerene šifre listova) |
| Službene novine PGŽ (sn.pgz.hr) | pravni tekst odluka | doslovni citati se provjeravaju prema spremljenom tekstu SN PGŽ 19/2016 |
| OpenStreetMap (Overpass) | ceste, sadržaji u okolini | |
| Open-Meteo / Copernicus DEM | nagib terena | |
| Ostalo | komunalni doprinos (Zagreb, Krk), HERA naknade (NN 45/2026), upravne pristojbe (NN 156/2022) | |

Uvjeti korištenja: izvor i datum navode se uz svaki podatak, a servisi PGŽ-a daju se bez jamstva. Ne koriste se plaćeni API-ji ni tajni ključevi.

## 5. Glavne funkcije (redoslijed na ekranu)

1. **Pretraga i karta.** Upis adrese ili čestice, dodir na kartu ili lokacija uređaja. Izbornik slojeva:
   - satelit, DGU ortofoto, granice čestica;
   - namjena, vodovi, sjene;
   - skener građevinskih čestica, legenda.

   Uz to postoje 3D prikaz i poveznica na Google Street View.
2. **Zaglavlje čestice.** Broj, k.o., grafička i upisana površina (katastar, ZK), dijelovi čestice iz posjedovnog lista.
3. **Sažetak čestice.** Kartice „Smije li se graditi?”, „Koliko velika kuća?” i druge, svaka s razinom pouzdanosti.
4. **Prostorni planovi na lokaciji.** Važeći, u izradi i van snage, sa SN brojem i poveznicama.
5. **Detaljna namjena (UPU), napredni prikaz.** Izrez lista plana oko čestice s ucrtanom granicom, izbor lista, povećanje i umanjenje, prikaz na glavnoj karti, status i aktualnost lista.
6. **Uvjeti gradnje.**
   - **Sažetak uvjeta gradnje (novo):**
     - tablica: pokazatelj | rezultat | status (izvedeno / uvjetno / blokirano) + A/B/C, s kratkim upozorenjem;
     - dodir retka otvara puni dokazni lanac: članak, doslovni citat, osnovica, izračun, uvjeti i iznimke, razlog statusa;
     - zajednički izvori (čestica, plan, GIS zona, detaljna zona, kartografski prikaz) prikazani su jednom;
     - istaknut je popis „Što još moraš provjeriti”;
     - blok „Osnovica površine” pokazuje kako grafička, katastarska ili ZK površina mijenja najmanju česticu, tlocrt i GBP. Uz to stoji napomena da odabrana površina nije službena površina građevne čestice.
   - **Izbornici:** vrsta zgrade (obiteljska, višeobiteljska, stambena), način gradnje (slobodnostojeća, dvojna, ugrađena), vrsta zahvata (nova gradnja, rekonstrukcija…), zona UPU-a i zona zaštite (npr. karta 3A: »B« i »C«).
   - **Izračun za česticu:** najmanja i najveća čestica, tlocrt (kig), GBP (kis), visina, etaže, prostor nakon odmaka od međa i scenariji udaljenosti od ceste.
   - **Usporedba svih tipova i načina gradnje** na toj čestici.
   - **Iznimke.** Kad je ispunjen samo prag iznimke, piše: „Površina zadovoljava brojčani prag iznimke, ali primjenjivost iznimke nije potvrđena.” Nikad se ne piše samo „ispunjeno”.
   - **Sukobi pravila prikazuju se kao blokada**, a ne kao rezultat. Primjer: nagib krova u zoni »C« (čl. 38. d prema čl. 85. st. 2. UPU-a 2).
   - **Simulator kuće na čestici.** 2D i 3D: tlocrt, etaže, krov, sjena. Simulator ne potvrđuje dopuštenost.
7. **Prijedlog detaljne zone (pilot, novo).** Opis u §8.
8. **Rizici i upozorenja, Provjere, Pristup i okolina, Komunalna infrastruktura.**
9. **Sunce i energija.** Osunčanost, fotonaponska elektrana, vjetar i bura, pogled na more.
10. **Novac i kupnja.** Komunalni i vodni doprinos, priključci, pristojbe, procjena gradnje, „Moja investicija”, kontrolna lista kupnje.
11. **Dokumentacija i gdje se obratiti.**
12. **Pouzdanost podataka.** Registar svih podataka s razinom, izvorom, obuhvatom i datumom.
13. **Izvoz.**
    - JSON izvještaj o integritetu (`piReport`, shema `cesticahr.plan_integrity.v10`);
    - ispis u PDF;
    - DXF / glTF za simulator;
    - spremanje i dijeljenje čestice.

**Mobilno (ispod 900 px):**
- karta preko cijelog ekrana;
- donji panel s tri stanja (sažetak, pola, cijeli ekran);
- donja navigacija Karta · Analiza · Troškovi · Spremljeno;
- skupine sadržaja `.grp[data-g]` samo se skrivaju i prikazuju, pa se unosi ne gube.

Prekidač „Napredno” prikazuje tehničke odjeljke, uključujući izrez karte UPU-a i registar pouzdanosti.

## 6. Model pouzdanosti i integriteta

### Razine podatka (`PZREG`, funkcije `pz`, `pzCalc`, `pzUser`)

| Razina | Značenje | Primjeri |
|---|---|---|
| **A** | službeno | servis nadležnog tijela, objava |
| **B** | preliminarno | presjek GIS-a, raster s preklopom, vrsta karte iz naziva |
| **C** | nepotvrđeno | korisnikov odabir ili pretpostavka, automatski prijedlog |

Izračun preuzima najslabiju razinu svojih ulaza.

### Status rezultata (Plan Integrity v10, `piObjava`)

| Status | Kada |
|---|---|
| **provjereno** | sve karike su stručno provjerene |
| **izvedeno** | izvori su kompatibilni |
| **uvjetno** | postoje otvoreni uvjeti, usklađenost je nepoznata ili postoji pretpostavka korisnika |
| **blokirano** | sukob pravila ili nedostaje ključni ulaz |

### Dokazni lanac

Svaki pokazatelj nosi listu karika. Polja karike:
- `karika`, `vrijednost`, `raz`;
- `izvor`, `revizija`, `status`;
- `uskladenost` (kompatibilno / nepoznata / sukob), `razlogUsk`;
- `citat`, `citatVrsta` (doslovni navod ili sažetak aplikacije);
- `pravilo`.

Uz lanac pokazatelj nosi `uvjeti` (tekst i je li razriješen) i, ako je blokiran, `blokada` s razlogom.

Pokazatelji: `calc-min`, `calc-tlocrt`, `calc-gbp`, `calc-visina`, `calc-prostor`, `blok-uvjeti`, `blok-krov`.

### Ostalo

- **Osnovica izračuna.** Nezaokružena površina (grafička iz koordinata ili upisana) × udio u građevinskom području. Prikaz je na 0,1 m².
- **Baza pravila Data Manager (vanjski alat).** Uvoz preko `RULES_DB` (`dbMatch`, `dbConditions`, `dbPublicationGate`). U izračun ulazi samo pravilo koje je pravno i GIS-ski »potvrđeno«, s člankom, citatom, revizijom i obuhvatom. `tools/baza/audit_pravila.py` provjerava bazu prije uvoza. **Pravno potvrđenih pravila trenutno je 0.**

## 7. Pravila (podaci)

### `src/rules_krk.json`

Glavna polja:
- `naselja`, `tipovi` (PPUG Krk);
- `upu["UPU 1" | "UPU 2" | "UPU 5"]`;
- `ostaleJls` (Malinska, Baška, Vrbnik…).

Svaki UPU ima:
- `kod`, `prepoznaj` (regex naziva plana);
- `zone` (npr. M11, M2, „druga”), `tipovi`;
- `meda`, `regulacija`, `zelenilo`, `pristup`;
- `simulator` (krov, zaštita B/C);
- `karte.listovi` (naslovi listova; `zona:true` za list sa zonama; `legenda` s bojama za pilot);
- `citati`: doslovni navodi po skupini, ključevi `minC`, `izg`, `kis`, `tl`, `gbp`, `visina`, `meda`, `krov`.

Primjer za UPU 2, obiteljska kuća:

| Način gradnje | minC | Napomena |
|---|---|---|
| slobodnostojeća | 500 m², iznimno 400 m² | kig 0,25, kis 0,75, tlocrt 60–200 m² |
| dvojna | 300 m² | |
| ugrađena | 300 m² | |

Zajedničko: visina 7,5 m, podrum i 2 nadzemne etaže.

Test čuva vrijednosti pravila sažetkom SHA-256. Izvan sažetka su samo `pravna_provjera`, `citati`, `legenda` i `provjereno`. Svaka promjena brojki traži neovisnu provjeru.

### Ostale datoteke

- `src/rules.json`: GUP Zagreb, 27 urbanih pravila. Za svako pravilo: članak, naziv, zone, stavke i ključevi parametara.
- `src/rules_meta.json`: izvor, verzija i status svake datoteke pravila; prikazuje se u aplikaciji.

## 8. Pilot: prijedlog detaljne zone UPU-a 2 Kornić

**Problem.** Detaljna zona (M11, M2…) postoji samo na skeniranoj karti 4 („Način i uvjeti gradnje”). Javnog vektora nema: JLS sloj traži prijavu, a slojevi PGŽ-a nose samo obuhvat plana.

**Postupak.** Aplikacija već dohvaća izrez lista oko čestice (PP_RASTERI, OBJECTID 7104). Pilot zatim:

1. Očitava piksele u pregledniku (`getImageData`).
2. Gradi histogram boja (4 bita po kanalu, korak oko 0,25 m) u tri pojasa:
   - unutar čestice, dalje od 1 m od granice;
   - uz rub;
   - u pojasu do 6 m izvan granice.
3. Razvrstava svaki uzorak:
   - tamno (linije, tekst; ne broji se);
   - bijelo (ceste);
   - sivo;
   - zona iz legende, prema udaljenosti tona, zasićenosti i svjetline do boje polja službene legende (servis legende Ministarstva, OBJECTID 2139);
   - nepoznato.
4. Odlučuje:
   - daje kandidata kad najčešća zona ima najmanje 80 % obojenih uzoraka, prepoznate boje čine najmanje 60 %, a bijelo najviše 20 %;
   - inače odustaje i navodi razlog;
   - upozorava »blizu granice zone« ako u vanjskom pojasu ima najmanje 10 % drugih zona.
5. Bez izmišljenog postotka pouzdanosti. Kao dokaz prikazuje udjele razreda, pojas, izvor, šifru lista i razlučivost.
6. Korisnik može: **Prihvati**, **Odaberi drugu zonu** ili **Odbij prijedlog**.
   - Prihvaćena zona ostaje **C** i vrijedi samo za tu česticu i tu reviziju lista.
   - Stručna provjera (`karte.listovi.4.provjereno`, trenutno prazno) vrijedi samo za točno navedenu česticu i istu reviziju.

**Validacija.** Oznake su dali neovisni AI agenti vizualno; to nije stručna potvrda.

| Skup | Ukupno | Prijedloga | Točnih | Pogrešnih | Odustao | Pogrešna zona M11↔M2 |
|---|---|---|---|---|---|---|
| razvojni | 42 | 35 | 34 | 1 | 7 | 0 |
| slijepi (nakon zaključavanja parametara) | 40 | 33 | 31 | 2 | 7 | 0 |

Sve tri pogreške su mješovite čestice kojima je ponuđena većinska zona.

Pilot je **isključen za sve korisnike** (`FEATURES.upuZona=false`). Detalji su u `docs/upu-zona/README.md` i `docs/upu-zona/rezultati_2026-10-27.json`.

## 9. Struktura repozitorija

```
src/app.template.html      cijela aplikacija (uređuje se samo ovo)
src/rules*.json            pravila (GUP, Sesvete, PPGZ, Krk), rules_meta.json, ispu_sifre.json
src/parse_gup*.py          parseri teksta odluka
src/sw.template.js         service worker
build.py                   sastavlja index.html i sw.js (provjera pravila)
index.html, sw.js          izgrađeno (ne uređivati ručno)
manifest.webmanifest, icons/, icon.svg, vendor/   PWA i knjižnice
data/                      unaprijed pripremljeni podaci (oko 240 MB)
  kat_krk/  čestice Krka (DGU DKP), kvadrati 0,009° × 0,013°
  ski/, ski_krk/  infrastruktura DGU SKI (Zagreb, Krk)
  zg3d/, zg3d_krk/  3D zgrade
  adr/  adrese i ulice
  ptn/  pomoćni podaci
  pravila-sn/  izvodi pravila iz SN
tools/                     skripte za pripremu podataka:
                           katastar, ski, pgz, ispu, sn-pgz, plan-citac, baza (audit),
                           gis-pilot, upu-zona (uzorci i oznake za pilot zone), zg3d, adrese
worker/                    Cloudflare Worker za AI asistenta (isključen)
tests/                     run.js (jsdom, oko 1 030 provjera), mobile/*.py (Playwright),
                           plan_integrity/*, pgz-odgovori/ (spremljeni odgovori servisa), zlatni/
docs/                      dokumentacija (stanje projekta, Krk pilot, PGŽ servisi, pouzdanost,
                           Android, AI, plan-integrity/, upu-zona/)
```

## 10. Pokretanje i testovi

```bash
python3 build.py                       # izgradi index.html i sw.js
python3 -m http.server                 # lokalni pregled (http://localhost:8000)
cd tests && npm install && node run.js # puni skup (jsdom); očekivano: 1029 prošlo, 0 palo
node mobile/make_local.js              # lokalna inačica za Playwright
python3 mobile/layout.py && python3 mobile/interaction.py && python3 mobile/krk.py && python3 mobile/pwa.py && python3 mobile/sazetak.py
node plan_integrity/test_v10.cjs       # i check_integrity*.cjs; python3 plan_integrity/test_audit.py
node plan_integrity/usporedba_prije_poslije.js <stari index.html> <novi index.html>   # regresija pokazatelja
```

Testovi rade bez mreže, sa spremljenim odgovorima servisa (`tests/pgz-odgovori/`).

## 11. Pravila rada (obavezno poštovati)

1. Ništa se ne izmišlja; nepoznato se prikazuje kao „Podaci nisu dostupni”.
2. Brojčana pravila uvode se samo uz konkretan članak, doslovni citat i provjerenu verziju plana. AI ne nagađa pravne uvjete. Pravno potvrđenih pravila ostaje 0 dok ih ne potvrdi stručnjak.
3. Tko gradi, ne ocjenjuje vlastiti rad. Slijepi testovi zaključavaju se prije razvoja. Grana `slijepi-testovi` sadrži zaključane oznake i ne dijeli se razvoju; **nije uključena u ovaj zip**.
4. Zamrznute verzije i zaključani referentni skupovi (`tests/zlatni/`) ne mijenjaju se; nove idu samo kao nova verzija (v2).
5. Bez plaćenih API-ja i bez tajni (ključeva) u repozitoriju ili aplikaciji.
6. U `main` (produkcija) ništa bez Ozrenova odobrenja. Rad ide na granama izvedenim iz `razvoj`.
7. Korisnikov odabir ili automatski prijedlog nikad ne postaje službeni podatak; ostaje C.
8. Ne graditi novi GIS, novi sustav pravila ni novu arhitekturu kad postojeći kod već to radi. Proširuje se postojeće.

## 12. Otvoreno

- Detaljne zone UPU-a samo su raster. Pilot treba stručni referentni skup (npr. lokacijske informacije) i bolje odustajanje kod mješovitih čestica, šrafura i oznaka. Za drugi UPU treba novo uzorkovanje legende.
- Tekstovi koji nisu obrađeni:
  - Punat (UPU 3);
  - Omišalj i Dobrinj;
  - Vrbnik 2024.;
  - UPU-ovi Malinske, Baške i Vrbnika.
- Ažurnost planova: moguće izmjene u SN koje slojevi PGŽ-a još nemaju.
- Nijedan plan nije pravno potvrđen (važenje, datum stupanja na snagu).
- Potresna opasnost i AI asistent su isključeni.
- Izračun prijedloga zone traje do oko 0,5 s na glavnoj niti; bolji je Web Worker.
- Prije objave treba ručna provjera na Android Chromeu i iPhone Safariju: povlačenje panela, tipkovnica, ispis u PDF.

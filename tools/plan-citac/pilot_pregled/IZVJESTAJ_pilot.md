# Pilot pregleda i potvrđivanja pravila: UPU 13 Travičići

Status: pilot, grana `pilot-pregled-pravila`. Nije u produkciji; `main` nije diran. Zamrznute verzije su netaknute: v2.6 i hibrid v1 provjereni su SHA-om. Svi slijepi rezultati čuvaju se na grani `slijepi-hibrid-v1-travicici`. v2.7 i novi generator nisu pokrenuti. Pravno potvrđenih pravila: 0.

## 1. Što je napravljeno

| Dio | Datoteka | Stanje |
|---|---|---|
| Izvoz podataka (109 AI kandidata, rezultati tehničke provjere, tekst članaka, evidencija i geometrija PGŽ; bez slijepih oznaka) | `izvoz_podataka.py` → `podaci/pilot_travicici.json` | 109/109 citata nađeno u tekstu |
| Logika: četiri razine, revizijski trag s lancem hasheva, mjerenje, povezivanje s česticom, važenje plana | `pregled_logika.js` | 17/17 testova (`node test_logika.js`) |
| Sučelje (jedna stranica, objavljeno kao privatni artifact) | `sucelje.template.html`, `sastavi.py` → `dist/pregled_pravila_travicici.html` | 25/25 testova u Chromiumu s lažnom bazom (`python3 test_sucelje.py`) |
| Evidencija plana i geometrija iz PGŽ servisa (preuzeto preglednikom, SHA provjeren) | `podaci/pgz_obuhvat_zona.json` | SHA `9ee6bcdd…` |

### Zadatak 1: prikaz za svaki kandidat
- Izvorni članak s doslovnim citatom označenim u tekstu.
- Parametar, operator, vrijednost i jedinica.
- Vrsta građevine (naziv, izraz, izvor), način gradnje, stanje, zona s citatom, uvjeti i iznimke s izvorom, vrsta pravila, AI napomena.
- Razlozi za pregled iz tehničke provjere (kod i objašnjenje).
- Referentni izvor: plan, glasilo, verzija teksta, poveznica, SHA izvora, SHA generatora i provjere.
- Radnje: potvrdi, ispravi i potvrdi (uređivanje polja), odbij, vrati na pregled. Obrazloženje od najmanje 10 znakova je obavezno.

### Zadatak 2: kontrola kvalitete

| Razina | Tko je postavlja | Može li se mijenjati |
|---|---|---|
| 1. AI prijedlog | generator hibrid v1 (zamrznut) | ne |
| 2. Tehnička provjera | deterministička provjera (zamrznuta) | ne |
| 3. Stručna potvrda | pregledavatelj, samo kroz revizijski trag | samo novim događajem; stari ostaje |
| 4. Pravna valjanost | nitko u pilotu: uvijek »nije utvrđena« | ne; radnja koja je pokuša postaviti se odbija |

- Ništa se ne potvrđuje automatski. Ni »prošlo sve provjere« (razina 2) nije stručna potvrda, i to provjerava test.
- Slijepe oznake nisu u podacima sučelja. Izvoz se prekida ako se pojavi neko njihovo polje.
- **Revizijski trag:** svaki događaj sadrži tko, kada, radnju, stanje prije i poslije, razlike po poljima, obrazloženje, aktivno vrijeme, SHA podataka, SHA-256 vlastitog sadržaja i hash prethodnog događaja istog pregledavatelja.
- **Zapis:** svaki pregledavatelj piše samo u svoj trag (`trag/<id>/dogadjaji`). Pravilo baze to brani: pokušaj pisanja u tuđi trag na razini Contributor odbijen je.
- **Provjera lanca:** otkriva izmijenjen ili uklonjen događaj (test).
- **Granica zaštite:** vlasnik artifacta tehnički može prepisati podatke. Lanac to čini vidljivim, ali ne nemogućim. Za pravnu uporabu trebao bi vanjski potpisani zapisnik.
- Trag se može preuzeti kao CSV.

## 2. Zadatak 3: povezivanje s obuhvatom plana i česticom

| Izvor | Što daje | Oblik | Stanje 27. 10. 2026. |
|---|---|---|---|
| PGŽ `STANJE/IZRADA_PP` (OBJECTID 913) | UPU 13: status VAŽEĆI, donesen 25. 4. 2012., objavljen 30. 4. 2012., na snazi od 7. 5. 2012., bez datuma prestanka, IDPLAN 648, SN 15/2012; poveznica glasila ista kao naš izvor | vektor (obuhvat) | preuzeto |
| PGŽ `STANJE/NAMJENA_POVRSINA_NOVO` | zona T2-5 (PPUG Opatija, SN 04/16), oko 9 351 m²; čl. 9 kaže »oko 9000 m²« | vektor | preuzeto |
| PGŽ `PP_RASTERI` | karte UPU-a, a time i zone S1, S2 i K (»5 - u raster katalogu«) | raster | samo slika: granice zona nisu strojno čitljive |
| DGU katastar (INSPIRE WFS / ATOM) | katastarske čestice | vektor | **WFS s ovog računala nije odgovorio ni na GetCapabilities**: čestice za Travičiće nisu preuzete, »Podaci nisu dostupni« |

**Model povezivanja** (u kodu i testu):
- **Lanac:** plan (status, datumi važenja, izmjene) → obuhvat → zona s planskom oznakom i vektorskom granicom → pravilo s citatom → stručna potvrda iz traga → čestica presjekom s granicom zone.
- **Kad se pravilo pridružuje čestici:** samo kad su ispunjena sva tri uvjeta:
  - pravilo je stručno potvrđeno;
  - zona ima vektorsku granicu;
  - plan vrijedi na traženi dan.
- **Pravna valjanost:** ostaje »nije utvrđena«.
- **Izmjena plana:** nova odluka dobiva nove kandidate, stara pravila zatvaraju se datumom prestanka, a trag ostaje.

**Demonstracija:**
- Pogled »Obuhvat i čestice« crta obuhvat UPU 13 i zonu T2-5 i provjerava važenje plana na današnji dan.
- Prikazuje pravila zone T2-5 po stanju stručne potvrde: sada 0 potvrđenih, 31 čeka.
- Sloj čestica uključuje se sam čim se preuzme `podaci/cestice_t2_5.json` (`sastavi.py`). Mehanizam presjeka i udjela čestice u zoni pokriven je testom.

**Ograničenja:**
- Za S1, S2 i K treba ručno digitalizirati zone s rasterske karte. To je stručni posao s vlastitim pregledom.
- Granica T2-5 je iz sloja PPUG-a, a ne iz karte UPU-a.
- Na karti T2-5 dijelom izlazi preko ruba obuhvata UPU 13. To je razlika između dva sloja PGŽ koju treba razjasniti prije uporabe.

## 3. Zadatak 4: stvarna korist

**Ljudsko vrijeme još nije izmjereno.** Mjerenje traži stvarnog pregledavatelja, a ja ga ne mogu zamijeniti ni procijeniti iz glave. Sučelje mjeri aktivno vrijeme: sat staje nakon 2 minute bez unosa i dok je stranica skrivena. Zaključak se računa sam kad su obje faze gotove.

**Protokol** (unaprijed određen, ne mijenja se nakon uvida):
- **Faza 1:** pregled AI kandidata za čl. 9 (31 kandidat). Pravila koja AI nije predložio dopisuju se ručnim unosom unutar iste faze.
- **Faza 2:** ručni unos čl. 10 od početka, bez prikaza AI kandidata.
- **Mjera:** sekunde po završenom pravilu.
- **Pristranost:** čl. 9 i 10 dijele gotovo iste blokove, a ručni unos je uvijek drugi. Učenje zato ide u korist ručnog unosa, pa je procjena konzervativna za AI.

**Pokazatelj prije mjerenja** (izračunat prema zamrznutim neovisnim oznakama, samo kao mjera, ništa se njima ne potvrđuje):

| Konačno pravilo (114 oznaka) | Broj | Što pregledavatelj mora učiniti |
|---|---|---|
| AI kandidat točan bez izmjene | 23 (20 %) | samo potvrditi |
| razlika u 1 polju (najčešće parametar 13, vrsta građevine 12) | 31 | ispraviti jedno polje |
| razlika u 2 ili više polja | 20 | ispraviti više polja |
| nema AI kandidata s istom vrijednošću | 40 (35 %) | upisati ručno |

U strogoj usporedbi točnih bez izmjene je 15. Po člancima, točnih bez izmjene:

| Članak | Točnih bez izmjene |
|---|---|
| čl. 9 | 6 od 32 |
| čl. 10 | 11 od 21 |
| čl. 13 | 6 od 50 |
| čl. 19 | 0 od 11 |

**Očekivanje, ne mjerenje:**
- Uštedu bi mogla donijeti samo petina pravila (potvrda) i dio s jednim ispravkom.
- Za oko trećinu pravila AI ne pomaže, a pregledavatelj usto mora pročitati i odbaciti pogrešne kandidate.
- Ako faza 1 ne bude barem 10 % brža po pravilu, sučelje to otvoreno piše kao »AI ne donosi stvarnu uštedu«.

## 4. Vrijeme obrade

| Korak | Vrijeme |
|---|---|
| Izvoz podataka | 0,09 s |
| Sastavljanje stranice | 0,05 s |
| Testovi logike | 0,08 s |
| Testovi sučelja (Chromium) | 11,8 s |
| AI generator za cijeli plan (već zamrznuto, iz slijepog testa) | oko 190 s usporedno, 258 676 tokena |
| Ljudski pregled i ručni unos | **još nije izmjereno** |

## 5. Preporuka
- **Ne nastavljati razvoj generatora** dok mjerenje ne pokaže uštedu.
- **Nastaviti s alatom za pregled i ručni unos**, jer vrijedi neovisno o AI-ju. Taj dio jedini vodi prema pouzdanim pravilima:
  - doslovni citat;
  - odvojene razine statusa;
  - revizijski trag;
  - veza s evidencijom i važenjem plana.
- **Odluka o AI-ju:** nakon jednog mjernog sata (faza 1 i 2, oko 1–2 sata rada):
  - ako je pregled AI kandidata sporiji ili do 10 % brži, AI izbaciti iz procesa;
  - ako je znatno brži, AI zadržati samo kao predpopunjavanje obrasca, uz isti pregled.
- **Sljedeći korak za čestice:** ponovno preuzeti DGU katastar (ATOM po k.o. ili WFS kad proradi). Tek tada se demonstracija može proširiti na konkretne čestice u zoni T2-5.

## 6. Kontrolne sume

| Datoteka | SHA-256 |
|---|---|
| `podaci/pilot_travicici.json` | `5f801d82293cabe622d6ab13c7a2a210ad21223ff219fbe8bc5242a4a86dd61b` |
| `podaci/pgz_obuhvat_zona.json` | `9ee6bcdddc238d0c4f1409b4289e2536e985195020e8fba2ebff7085db6b653f` |
| `dist/pregled_pravila_travicici.html` | `133a5aa4e3ddd6870b2c5e5f7278362d64338aea96eacf0ef6811b217b64d10a` |
| izvor plana | `fdc767ecf00b383f073694a50eb70d4ad9efc21f38bf758cc98c359d11fb01bc` |
| izlaz generatora (zamrznut) | `f17f821090f60134ac5f0eb61611eb0fa7a65c8965f48c1d2da35a272d7a3704` |

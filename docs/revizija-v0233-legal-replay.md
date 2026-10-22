# Neovisna provjera prije Legal Replaya v0.23.4: članak 126. PPUO Baška

Datum: 22. 10. 2026. Revizor: Claude (neovisni ocjenjivač). Kod Data Managera i zaključani referentni skupovi nisu mijenjani.
**Trenutačno važeće pravo se ne potvrđuje.** Sve simulacije su rađene na privremenoj kopiji teksta, samo za provjeru.

## 0. Izvori

| Izvor | Status |
|---|---|
| 34/12 (id 25645), polazni tekst koji koristi DM | stranica iz arhive; sha256 `141d6ede…efe86` = vrijednost u DM-u |
| 36/16 (id 34945) III. ID, čl. 18 | stranica iz arhive v0.18.7 |
| 6/20 (id 41160) V. ID, čl. 18 | isto |
| 17/14 (id 30488) ciljane ID; 10/18 (37167); 24/20 (41714) | isto (za isključenje drugih izmjena) |
| 13/20 (id 41290) pročišćeni tekst | isto; sha256 = vrijednost u DM-u |
| 02/17 i 18/18 | **nisam vidio stranice** (portal mi je blokiran); za 18/18 koristim samo popis izmjena iz izlaza v0.22.3 i to izričito označavam |
| `amendment_instruction_v0231.json`, `structural_address_v0233.json`, `data_manager.zip` (kod) | pregledano |

Svaka tvrdnja ispod je označena kao **[Č]** činjenica iz izvora, **[DM]** preuzeto iz izlaza DM-a ili **[P]** pretpostavka.

---

## 1. Povijesni lanac i SN 02/17

**Odgovori**

| Pitanje | Odgovor |
|---|---|
| Puni naziv | **Nije utvrđen.** Nemam stranicu ni popis broja 2/17. Odluke ga navode samo kao „02/17 - pročišćeni tekst" **[Č]** |
| Odnosi li se na PPUO Baška | **Da** **[Č]**. Devet odluka Općine Baška navodi ga u lancu objava PPUO Baška |
| Mijenja li čl. 126 | **Ne kao izmjena.** To je pročišćeni tekst, a ne odluka o izmjenama **[Č]**. Može sadržavati urednička odstupanja (§1.3) **[P]** |
| Izmjene koje utječu na prethodnika 36/16 | **Nema ih za čl. 126.** Između 34/12 i 36/16 je samo 17/14, koja čl. 126 ne mijenja **[Č]** |

**1.1 Citati koji dokazuju da je 02/17 pročišćeni tekst PPUO Baška** **[Č]**
- 36071 (27/17), čl. 6: „Prostorni plan uređenja Općine Baška(»Službene novine« Primorsko-goranske županije, broj … 01/08, 11/12, 34/12 - pročišćeni tekst, 17/14, 36/16 i 02/17 - pročišćeni tekst)".
- 37167 (10/18, IV. ID), čl. 1: „Ovom Odlukom donose se IV. izmjene i dopune Prostornog plana uređenja Općine Baška (»Službene novine« Primorsko-goranske županije, broj 01/08, 11/12, 34/12 - pročišćeni tekst, 17/14, 36/16 i 02/17 - pročišćeni tekst)".
- 41160 (6/20, V. ID), čl. 1: „… broj 01/08, 11/12, 34/12 - pročišćeni tekst, 17/14, 36/16, 02/17 - pročišćeni tekst, 10/18 i 18/18 - pročišćeni tekst".
- Isto navode 35200 i 35201 (6/17), 40183 (19/19), 40441 (27/19), 41714 (24/20) i 43050 (8/21).
- Sekundarni izvor: općinsko *Izvješće o stanju u prostoru 2019.–2022.*, str. 11, navodi „02/17 - pročišćeni tekst".

**Vremenski okvir:** 02/17 je objavljen nakon 36/16 (23. 12. 2016.). Među dokumentima u korpusu prvi ga navodi 6/17 (13. 3. 2017.) **[Č]**.

**1.2 Neposredni prethodnik 36/16 za čl. 126**
- Lanac do 36/16 je 01/08 → 11/12 → 34/12 (pročišćeni tekst) → 17/14 → 36/16 **[Č]**.
- 17/14 (30488) spominje „126" samo kao uputnicu u drugom članku („broj »106«, zamjenjuje se brojkom »126.«") i kao čl. 126. Zakona o vodama. Ne mijenja čl. 126 plana i ne prenumerira članke oko njega **[Č]**.
- Zato je stanje čl. 126 neposredno prije 36/16 jednako stanju u 34/12. To vrijedi uz rezervu da je 34/12 pročišćeni tekst, a ne izvorno doneseni tekst **[P]**, pa mogu postojati urednička odstupanja kakva vidimo i kasnije (§1.3).

**1.3 Gdje se dogodila urednička odstupanja**
Prema popisu izmjena iz v0.22.3 **[DM]**, u usporedbi 18/18→13/20:
- st. 4 je izgubio slovo „i" (slijedeće→sljedeće);
- st. 3 je dobio samo umetak iz 6/20.

Ostala odstupanja iz §4.3 (točke na kraju podalineja, „Bašćanska", veznik „i" u st. 6, izostala dvotočka) dakle **već postoje u 18/18**. Nastala su najkasnije u 02/17 ili 18/18. Koji je od ta dva pročišćena teksta uveo koje odstupanje, može se utvrditi tek iz 02/17.

**Što DM treba napraviti:** preuzeti popis broja 2/17 i stranicu pročišćenog teksta, upisati ih u registar objava (naziv, izdanje, redni broj, hash) i koristiti ga kao **prvu kontrolnu točku nakon 36/16**.

---

## 2. Alineje, podalineje i dvotočka

**2.1 Struktura polaznog teksta 34/12 se razlikuje od 13/20** **[Č]**
U 34/12 naslovi često nisu zaseban HTML redak. Primjeri iz st. 3:
- redak 1: „Najmanja dopuštena površina građevne čestice nije određena. Veličina i površina građevina";
- redak 3: „-Najveći dopušteni koeficijent iskorištenosti (kis) iznosi 3,75. Najveća visina:".

**Posljedica: granice alineja moraju se tražiti unutar teksta, a ne po HTML retcima.**

**2.2 Rječnik adresa u 36/16** **[Č]**
- **alineja** je blok na razini stavka: al. 1 je uvodni tekst, al. 2 je skupina „Veličina i površina građevina", al. 3 je skupina „Najveća visina".
- **podalineja** je stavka s crticom unutar skupine.
- 6/20 isti blok (al. 1) zove „podstavak 1".

**2.3 Je li strukturni kandidat za dvotočku (st. 4, al. 3, podal. 2) ispravno određen?**
**Na razini podalineje da, na razini riječi ne.**
- **Podalineja je točna** **[Č]**: u 34/12 st. 4 to je redak „-Najveća visina građevine 9,0 m, a najveća ukupna visina građevine 11,0 m.", prva skupina.
- **„građevine" nije jednoznačna** **[Č]**: pojavljuje se 4 puta u st. 4 (retci 6 i 11) i **dva puta u samoj ciljnoj podalineji**. v0.23.3 daje pomak početka fraze „Najveća visina građevine" (595), ali ne kaže iza koje pojave ide dvotočka.
- **Ispravna je prva pojava**, a dokazuje se slijedom **[Č]**: sljedeća uputa iste odluke zamjenjuje „9,0 m, a najveća ukupna visina građevine 11,0 m". Kad bi dvotočka išla iza druge pojave, ta stara riječ više ne bi postojala i operacija 11 ne bi imala preduvjet. U mojoj simulaciji od 4 kandidata ostaje točno 1.
- **Kandidat je u kodu ručno upisan** **[Č]**: `structural_address_v0233.py` ima posebnu granu `if op.get('operation')=='INSERT_PUNCTUATION' and op.get('old_text')=='građevine' and p=='4' and op.get('act_id')=='34945'`. To nije opće pravilo i ne smije se brojati kao rezultat algoritma.
- **Kontrolna točka:** u 13/20 dvotočke **nema** („- Najveća visina građevine u postojećim gabaritima."). Prema [DM] popisu izmjena nema je ni u 18/18. Ispravna simulacija zato **mora** dati `DEVIATION_FROM_AMENDMENT`, a ne „podudaranje".

**2.4 Kako riješiti ponovljene naslove „Veličina i površina građevina" i „Najveća visina"**
- U st. 4 postoje dvije skupine **[Č]**. Prva (al. 2 i 3) odnosi se na rekonstrukciju. Druga dolazi iza „Isključena je nova gradnja osim autobusnog kolodvora, helidroma, parkirališta uz slijedeće uvjete:".
- Pravilo **[P]**: redak koji završava dvotočkom otvara podrazinu, pa su naslovi iza njega djeca tog retka, a ne nove alineje stavka. Redni broj alineje broji se samo na razini stavka.
- 36/16 adresira „alineja 2/3" i njegove stare riječi postoje samo u prvoj skupini. To je u skladu s pravilom, ali pravilo nije službena konvencija i treba ga provjeriti na drugim odlukama.
- **Minimalno za sigurno razrješenje:** redni broj alineje + citirani naslov iz same odluke („u alineji 2. »Veličina i površina građevina«") + stara riječ koja postoji točno jednom u toj skupini. Naslov sam nikad nije dovoljan.

---

## 3. Četiri skupine nedovoljno određenih operacija

| Skupina | Što v0.23.3 kaže | Činjenice | Minimalni dokazi za sigurnu simulaciju |
|---|---|---|---|
| **Zamjena cijelog st. 2** (op. 1) | `UNIT_BOUNDARY_NOT_PROVEN` | Granica je numerirana: „(2)" do „(3)" u 34/12, jednom, uzastopno. Novi tekst počinje s „(2)" **[Č]** | (a) oznake (2) i (3) jedinstvene i uzastopne u polaznom tekstu; (b) novi tekst počinje istim brojem; (c) nijedna odluka između polaznog teksta i 36/16 ne dira st. 2 (§1.2). Granica cijelog numeriranog stavka **nije** nedokazana |
| **Zamjena al. 1 st. 3** (op. 2) | `UNIT_BOUNDARY_NOT_PROVEN` | Al. 1 u 34/12 je jedna rečenica („Najmanja dopuštena površina građevne čestice nije određena."), u istom retku s naslovom al. 2 **[Č]** | (a) početak = kraj uvodnog retka koji završava „:"; (b) kraj = početak naslova al. 2, **koji citira ista odluka** u stavku (3); (c) između nema drugog naslova. To su dva signala iz same odluke |
| **Dodavanje rečenice u st. 5** (op. 12) | `INSERTION_WITHOUT_EXPLICIT_POSITION` | Uputa: „U stavku 5. u alineji 1. dodaje se rečenica" **[Č]** | (a) konvencija „dodaje se rečenica" = na kraj navedene jedinice **[P]**, zapisana kao izričito pravilo; (b) kraj al. 1 = ispred naslova al. 2, **koji citira ista odluka** („U alineji 2. »Veličina i površina građevina«"). Položaj potvrđuje kontrolna točka 13/20, ali ona je postuvjet, ne premisa |
| **Novi st. 11** (op. 18) | `ADD_UNIT_BOUNDARY_REVIEW` | 34/12 ima točno stavke (1)–(10), iza njih slijedi „Članak 127." **[Č]** | (a) polazni tekst ima uzastopne stavke 1…N, a N = 10; (b) novi broj = N+1; (c) kraj članka je poznat; (d) nijedna međuodluka ne dodaje st. 11 |

---

## 4. Tablica svih 19 operacija

**Oznake:** `READY_FOR_SIMULATION` znači da su dokazi dovoljni za simulaciju na privremenoj kopiji, **ne** za potvrdu pravnog učinka.
- Kolona „Preduvjet" je moja provjera u polaznom tekstu: broj pojava stare riječi u stavku, i u kojem retku.
- Kolona „Kontr. točka 13/20" je rezultat moje simulacije svih 19 operacija na kopiji 34/12 i usporedbe sa 13/20.

| # | Odluka, stavak | Operacija | Cilj | Preduvjet (34/12) | Kontr. točka 13/20 | Oznaka |
|---|---|---|---|---|---|---|
| 1 | 36/16 (1) | REPLACE_UNIT | st. 2 | granice (2)…(3) jedinstvene | podudara | **READY_FOR_SIMULATION** |
| 2 | 36/16 (2) | REPLACE_UNIT | st. 3 al. 1 | al. 1 dijeli redak s naslovom al. 2 | podudara | **NEEDS_STRUCTURAL_EVIDENCE** (granica unutar retka, §3) |
| 3 | 36/16 (3) | REPLACE_WORDS „1,0" | st. 3 al. 2 podal. 1 | 1× u st. 3 (redak 2); 4× u članku | podudara | **READY_FOR_SIMULATION** (samo uz ograničenje na stavak) |
| 4 | 36/16 (3) | REPLACE_WORDS „iznosi 3,75" | st. 3 al. 2 podal. 2 | 1× (redak 3) | podudara | **READY_FOR_SIMULATION** |
| 5 | 36/16 (3) | REPLACE_WORDS „1 podzemna i 3 nadzemne … iznimno 1 podzemna i 4 …" | st. 3 al. 3 podal. 1 | 1× (redak 4) | urednička: dodana točka na kraju | **READY_FOR_SIMULATION** |
| 6 | 36/16 (3) | REPLACE_WORDS „prema lokalnim uvjetima" | st. 3 al. 3 podal. 2 | 1× (redak 5) | podudara | **READY_FOR_SIMULATION** |
| 7 | 36/16 (4) | REPLACE_WORDS „0,5 … 0,6 za skupni način gradnje" | st. 4 al. 2 podal. 1 | 1× (redak 3) | podudara | **READY_FOR_SIMULATION** |
| 8 | 36/16 (4) | REPLACE_WORDS „(kis) 1,75" | st. 4 al. 2 podal. 2 | 1× (redak 4) | podudara | **READY_FOR_SIMULATION** |
| 9 | 36/16 (4) | REPLACE_WORDS „1 podzemna i 3 nadzemne (…)" | st. 4 al. 3 podal. 1 | 1× u st. 4 (redak 5); 3× u članku | urednička: dodana točka | **READY_FOR_SIMULATION** (samo uz ograničenje na stavak) |
| 10 | 36/16 (4) | INSERT_PUNCTUATION „:" iza „građevine" | st. 4 al. 3 podal. 2 | **4× u st. 4; 2× u ciljnoj podalineji** | **odstupanje: dvotočke nema** | **AMBIGUOUS** (razrješivo slijedom s op. 11, §2.3; u v0.23.3 ručno upisano) |
| 11 | 36/16 (4) | REPLACE_WORDS „9,0 m, a najveća ukupna visina građevine 11,0 m" | st. 4 al. 3 podal. 2 | 1× (redak 6) | podudara | **READY_FOR_SIMULATION** (izvodi se zajedno s op. 10) |
| 12 | 36/16 (5) | INSERT_TEXT (rečenica) | st. 5 al. 1 | položaj nije naveden | podudara | **NEEDS_STRUCTURAL_EVIDENCE** (§3) |
| 13 | 36/16 (5) | INSERT_AFTER „za skupni način gradnje" + zarez | st. 5 al. 2 podal. 1 | 1× u st. 5 (redak 2); 2× u članku | podudara | **READY_FOR_SIMULATION** |
| 14 | 36/16 (5) | INSERT_AFTER „(kis) 1,5" + zarez | st. 5 al. 2 podal. 2 | 1× (redak 3) | podudara | **READY_FOR_SIMULATION** |
| 15 | 36/16 (5) | INSERT_AFTER „(Po/S+Pr+2 ili Po/S+Pr+1+Ppotk)" + zarez | st. 5 al. 3 podal. 1 | 1× u st. 5 (redak 4); 3× u članku | urednička: dodana točka | **READY_FOR_SIMULATION** |
| 16 | 36/16 (5) | INSERT_AFTER „11,0 m" + zarez | st. 5 al. 3 podal. 2 | 1× u st. 5 (redak 5); 2× u članku | podudara | **READY_FOR_SIMULATION** |
| 17 | 36/16 (6) | REPLACE_WORDS „smjernicama … odjela" | st. 6 | 1× u st. 6; 2× u članku (druga je u st. 2, koju op. 1 ionako zamjenjuje) | **neobjašnjeno: u 13/20 dodan veznik „i"** | **READY_FOR_SIMULATION** (kontrolna točka mora dati `UNEXPLAINED`) |
| 18 | 36/16 (7) | ADD_UNIT | st. 11 | stavci (1)–(10) uzastopni, slijedi čl. 127 | podudara | **READY_FOR_SIMULATION** |
| 19 | 6/20, čl. 18 | INSERT_AFTER „spajanje građevnih čestica nije dozvoljeno" | st. 3 al. 1 („podstavak 1") | **sidra nema u 34/12; nastaje tek op. 2 iz 36/16**; u stanju nakon 36/16: 1× | podudara | **READY_FOR_SIMULATION** (tek nakon op. 2; pravilo interpunkcije, §5) |

**Ukupno:** 16 READY_FOR_SIMULATION, 2 NEEDS_STRUCTURAL_EVIDENCE, 1 AMBIGUOUS, **0 NEEDS_HISTORICAL_SOURCE za samu simulaciju.**
02/17 i registrirani 18/18 trebaju za **potvrdu** (kontrolne točke i lanac), ne za simulaciju.

**4.1 Rezultat moje simulacije (provjera ovih oznaka)**
Svih 19 operacija primijenio sam na kopiju čl. 126 iz 34/12, a op. 10 sam razriješio slijedom s op. 11. Usporedio sam rezultat sa 13/20 nad usporedbenim slojem (bez oznaka, sažete bjeline, ujednačeni navodnici). **[Č]**
- Stavci 1, 2, 7, 8, 9, 10 i 11 su identični.
- U st. 3–6 ostaje **7 jednoznakovnih ili dvoznakovnih razlika**, nijedna sa znamenkom:

| Stavak | Simulacija | 13/20 | Klasa | Objašnjenje |
|---|---|---|---|---|
| 3, 4, 5 | „… u postojećim gabaritima - Najveća visina …" | „… gabaritima. - Najveća …" | UREDNIČKA (točka na kraju podalineje) | zamijenjene riječi nisu imale točku; pročišćeni tekst je dodao |
| 4 | „uz slijedeće uvjete" | „uz sljedeće uvjete" | UREDNIČKA (pravopis) | nastalo u 13/20 [DM] |
| 4 | „Najveća visina građevine: u postojećim …" | „Najveća visina građevine u postojećim …" | **DEVIATION_FROM_AMENDMENT** | 36/16 (4) izričito propisuje „:" |
| 5 | „Draga Bašćaska" | „Draga Bašćanska" | UREDNIČKA (ispravak tipfelera) | — |
| 6 | „uvjetima sukladno odredbama" | „uvjetima **i** sukladno odredbama" | **UNEXPLAINED → pregled** | nijedna uputa ne dodaje „i"; veznik je u klasi „nikad automatski tipografsko" |

**Zaključak simulacije:** sve sadržajne razlike između 34/12 i 13/20 u čl. 126 objašnjene su s 19 operacija iz 36/16 i 6/20. Preostala odstupanja su promjene pročišćenih tekstova bez temelja u odluci. Moraju se izvoziti, a ne prešutno izjednačiti.
To je tehnički uspjeh simulacije, **ne** potvrda pravnog učinka (§5).

---

## 5. Kriteriji za Legal Replay

**5.1 Uvjeti da se operacija smije simulirati (na privremenoj kopiji)**
- **S1 Izvor.** Odluka o izmjenama je u registru objava (izdanje, redni broj, hash) i nije nacrt ni postupovna odluka. Uputa je pohranjena **doslovno** i kanonski, s hashom.
  *Nalaz:* u v0.23.1 `old_text` sadrži artefakte „P o /S+P r +2" i „(k is ) 1,5", jer su oznake zamijenjene razmakom. Stara riječ mora se čuvati doslovno, a podudaranje raditi tek na usporedbenom sloju.
- **S2 Identitet plana.** Naslov i preambula odluke vode na istu obitelj plana. „U članku 126." se tumači samo unutar tog plana.
- **S3 Polazno stanje.** Polazno stanje članka je zadnja kontrolna točka ili stanje dobiveno simulacijom. Svaka objava iz lanca između polaznog stanja i odluke (lanac se čita iz preambula odluka) mora biti ili već simulirana ili dokazano bez učinka na članak. Rupa daje `NEEDS_HISTORICAL_SOURCE`.
  *Nalaz:* `BASELINE={'34945':'25645','41160':'37444'}` je upisan ručno. Mora se izvoditi iz lanca.
- **S4 Adresa.** Barem dva neovisna signala:
  - redni broj prema rječniku te odluke;
  - citirani naslov iz same odluke;
  - stara riječ točno jednom u razriješenoj jedinici.

  Granice jedinica se traže u tekstu, ne u HTML retcima (§2.1).
- **S5 Preduvjet.** Stara riječ postoji točno jednom u jedinici. Za umetanje bez položaja vrijedi zapisano pravilo konvencije i dokazana granica jedinice.
- **S6 Redoslijed i ovisnosti.** Operacije se primjenjuju redom iz odluke, a ovisne se razrješavaju zajedno (op. 10 i 11; op. 19 ovisi o op. 2). Više od jednog rješenja daje `AMBIGUOUS`.
- **S7 Interpunkcija na sidru.** Kad sidro završava rečenicu, a umetak je cijela rečenica, umetak ide iza završne interpunkcije (6/20 čl. 18). Pravilo mora biti zapisano i testirano, a ne implicitno.

**5.2 Postuvjeti (provjerava ih sama simulacija)**
- **P1** Nova riječ postoji točno jednom na očekivanom mjestu.
- **P2** Kod zamjene stara riječ više ne postoji u jedinici.
- **P3** Izvan ciljne jedinice nema nijedne promjene (razlika = 0).
- **P4** Strukturne invarijante vrijede: stavci su uzastopno numerirani, nema praznih jedinica, kraj članka je nepromijenjen.

**5.3 Usporedba s kasnijim pročišćenim tekstom (kontrolna točka)**
Svaka razlika dobiva jednu klasu:
- `MATCH`;
- `TYPOGRAPHIC` i `EDITORIAL` (zatvoren popis, s primjerima iz §4.1);
- `DEVIATION_FROM_AMENDMENT` (pročišćeni tekst nije proveo propisanu izmjenu);
- `UNEXPLAINED` (promjena bez upute).

Prednost ima **najbliža** kontrolna točka: za 36/16 to je 02/17, za 6/20 to je 13/20.

**5.4 Tehnički uspješan replay ≠ potvrđen pravni učinak**

| Razina | Uvjeti | Što smije tvrditi |
|---|---|---|
| `REPLAY_TECHNICAL_OK` | S1–S7 + P1–P4 | „Tekst izmjene je strojno primjenjiv na ovo polazno stanje" |
| `REPLAY_CHECKPOINT_CONSISTENT` | + kontrolna točka bez `UNEXPLAINED` (a `DEVIATION` je prijavljen) | „Simulirano stanje odgovara službenom pročišćenom tekstu, uz navedena odstupanja" |
| `LEGAL_EFFECT_CONFIRMED (na datum D)` | + sve objave u registru VERIFIED; lanac bez rupa do D; datum stupanja na snagu iz izričite odredbe; nema kasnijeg ukidanja ni izmjene do D; ljudski pregled svih `DEVIATION` i `UNEXPLAINED` | „Na datum D tekst odredbe glasi …" |
| „važeće danas" | + pokrivenost objava do danas | tek tada |

**Pravna pretpostavka [P] koju treba potvrditi pravnik:** pročišćeni tekst je deklaratoran, pa kod `DEVIATION_FROM_AMENDMENT` prevladava odluka o izmjenama (npr. dvotočka iz 36/16).

---

## 6. Nalazi o kodu v0.23.0–v0.23.3 [Č]

1. `amendment_instruction_v0231.py`:
   - `ACTS = {'34945': {… 'expected':18}, '41160': {… 'expected':1}}`, pa je `PARSED_COUNT_MATCH` provjera protiv ručno upisanog broja. Broj 18 je isti onaj koji sam naveo u prethodnoj reviziji, pa ta provjera nije neovisna.
   - Ciljni stavak **nije parsiran iz upute**, nego dolazi iz rječnika `{'1':2,'2':3,'3':3,'4':4,'5':5,'6':6,'7':11}`.
   - `target_plan`/`target_article` su konstante, a postoji posebna grana za `41160`.
2. `document_model_v0230.py`: popis od 5 dopuštenih ID-eva s hashovima, `expected_count=10 if str(publication_id)=="25645" else 11`, granice „Članak 126/127" upisane u kod.
3. `amendment_address_v0232.py` i `structural_address_v0233.py`: ručno upisan `BASELINE`, posebna grana za dvotočku (§2.3), a tekst odluke se čita iz fiksne datoteke `34945.html`.

**Posljedica:** rezultati v0.23.x vrijede za ovaj jedan članak, ali **ne dokazuju opći algoritam**. Prije širenja svaka od ovih konstanti mora postati izlaz parsera (lanac objava, ciljni stavak iz upute, broj stavaka iz teksta), a test mora proći na odluci koju razvoj nije vidio.

## 7. Preporučeni regresijski testovi za v0.23.4

1. Parser upute izvlači ciljni stavak iz „U stavku N." (ne iz rječnika). 36/16 daje ciljeve 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 11.
2. `old_text` je doslovan („Po/S+Pr+2", „(kis) 1,5"), a podudaranje radi na usporedbenom sloju.
3. Op. 10: od 4 pojave „građevine" u st. 4 ostaje točno 1, i to zbog slijeda s op. 11.
4. Op. 19 na 34/12 mora dati `PRECONDITION_FAILED` (sidro ne postoji). Na stanju nakon 36/16 mora dati 1 pojavu.
5. Op. 2 i 12: granica al. 1 određena citiranim naslovom al. 2, i kad naslov dijeli HTML redak s tekstom (34/12).
6. Simulacija 34/12 + 19 operacija prema 13/20 daje točno 7 razlika iz §4.1, s klasama iz tablice. Posebno: dvotočka daje `DEVIATION_FROM_AMENDMENT`, a veznik „i" u st. 6 daje `UNEXPLAINED`.
7. Polazno stanje se izvodi iz lanca: uklanjanje 17/14 iz analize mora dati `NEEDS_HISTORICAL_SOURCE`, a ne tihi nastavak.
8. Neovisni test: isti cjevovod na jednoj odluci o izmjenama izvan Baške, bez ručno upisanih ID-eva. Oznake pripremam ja i ostaju zaključane.

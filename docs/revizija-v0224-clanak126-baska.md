# Neovisna tehnička revizija Data Managera v0.22.4: članak 126. PPUO Baška

Datum: 22. 10. 2026. Revizor: Claude (neovisni ocjenjivač). Ne mijenja kod Data Managera ni zaključane referentne skupove.
Zaključak o trenutačno važećem pravu se **ne donosi**.

## 0. Što sam imao, a što nisam

| Imao | Nisam imao |
|---|---|
| `structure_fix_v0224.json`, `consolidated_diff_v0223.json`, `amendment_scope_v0222.json`, `run_report.json` | kod modula v0.19–v0.22.4 (ocjenjujem izlaze i izvore, ne kod) |
| Stranicu pročišćenog teksta 13/20 (id 41290); sha256 se podudara s v0.22.4 (`73f53018…ef29ef`) | 18/18 (id 37444) i 26/20 (id 41793): nisu među 177 dokumenata, a portal je iz mog okruženja blokiran |
| Odluke 36/16 (III. ID, 34945), 10/18 (IV. ID, 37167), 6/20 (V. ID, 41160), 24/20 (VI. ID, 41714) iz arhive v0.18.7 | odluku 2/17 (navedena u lancu objava, nije u korpusu) |

Zato su sve tvrdnje o 18/18 i 26/20 u ovom dokumentu pretpostavke, ne činjenice.

---

## A. Potvrđene činjenice

**F1. Reproducirao sam kanonski tekst v0.22.4 za 13/20: 11 od 11 hashova stavaka.**
Pravilo je ovo: retci stavka se spajaju razmakom, **svaka HTML oznaka postaje razmak**, slijede `unescape` i sažimanje bjelina, a `»` i `«` postaju `"`.
Posljedica: `k<sub>ig</sub>` daje „k ig", `m<sup>2</sup>` daje „m 2", `P<sub>o</sub>` daje „P o".

**F2. Zbog tog pravila doslovno povezivanje izmjene s pročišćenim tekstom ne uspijeva.**
Umetak iz 6/20, čl. 18 (578 znakova, piše „kig" bez oznaka) nalazi se doslovno u 13/20, st. 3, odmah iza „…spajanje građevnih čestica nije dozvoljeno.".
To vrijedi samo ako se inline oznake uklone **bez** razmaka. U kanonskom obliku v0.22.4 isti umetak se **ne pronalazi**, jer 13/20 ima `k<sub>ig</sub>`.

**F3. Članak 126. PPUO Baška mijenjaju samo dvije odluke u korpusu.**
Provjerio sam sve spremljene stranice za Bašku, tražeći „U članku 126.":
- **36/16 (III. ID), čl. 18:** 7 stavaka s 18 atomskih operacija. Zamjena cijelog st. 2, zamjena al. 1 st. 3, zamjene u podalinejama st. 3–5, dodavanje rečenica i zareza, dodavanje dvotočke, izmjena st. 6 i novi st. 11.
- **6/20 (V. ID), čl. 18:** jedna operacija. U st. 3, „podstavku 1." umeće iznimku za Dom kulture.
- **Odluka iz 2/18 o usklađenju UPU-1 Baška** također sadrži „U članku 126.". To je **članak 126. drugog plana** (UPU-1). Broj članka bez provjere identiteta plana daje lažne pogotke.
- **24/20 (VI. ID)** sadrži uputu „U članku …" samo za čl. 54, a **10/18 (IV. ID)** samo za čl. 59. i 115. Nijedna ne spominje čl. 126.

**F4. Ponovljena primjena operacija na 13/20: 18 od 19 operacija vidi se točno na očekivanom retku.**
Tih 19 su sve operacije iz 36/16 i 6/20. Stare vrijednosti (1,0; 3,75; „prema lokalnim uvjetima"; „(kis) 1,75") više se ne pojavljuju u st. 3, 4 i 6.
**Izuzetak:** 36/16 (4) kaže da se u st. 4, al. 3, podal. 2 „iza riječi »građevine« dodaje znak »:«". U 13/20 stoji „- Najveća visina građevine u postojećim gabaritima." bez dvotočke.
To je odstupanje pročišćenog teksta od izmjene. Interpunkcija koja je izričito propisana nije „samo tipografija".

**F5. v0.22.2 navodi 16 operacija iz 36/16; ja ih brojim 18.**
U v0.22.2 nema stavka (1) iz 36/16 (zamjena cijelog st. 2). Za stavak (4) navodi 4 radnje, a 36/16 ih ima 5, jer su umetanje dvotočke i zamjena dvije radnje u istoj podalineji. Najvjerojatnije nedostaje dvotočka.

**F6. Pravno adresiranje nije isto što i HTML redak, a nazivlje se razlikuje od odluke do odluke.**
- U 13/20 st. 3 ima 9 redaka. Redak 0 je uvodni („(3) Zona zaštite A …:").
- Isti tekstni blok (redak 1) 36/16 zove „alineja 1.", a 6/20 „podstavak 1.".
- 36/16 naslovljene skupine („Veličina i površina građevina", „Najveća visina") zove alinejama 2 i 3, a crtice ispod njih podalinejama.

**F7. Ponovljeni naslovi u st. 4 razrješavaju se rednim brojem alineje.**
St. 4 ima dvije skupine „Veličina i površina građevina"/„Najveća visina", jednu za rekonstrukciju i jednu za novu gradnju. 36/16 adresira „alineja 2"/„alineja 3", što su prve pojave, i rezultat u 13/20 to potvrđuje.
Dakle, naslov sam nije dovoljan, ali redni broj i naslov zajedno jesu.

**F8. Stavci koje v0.22.4 označava CHANGED poklapaju se s oznakama u HTML-u.**
- U usporedbi 13/20→26/20 promijenjeni su stavci 3, 4 i 5. To su **točno i jedini** stavci 13/20 s oznakama `<sub>/<sup>` (4, 8 i 7 oznaka).
- Stavci 1 i 7 jedini sadrže `»«`; u v0.22.3 bili su CHANGED samo zbog navodnika.

**F9. Nijedna odluka u korpusu ne mijenja čl. 126 između 13/20 (25. 4. 2020.) i 26/20.**
Jedine objave za Bašku u tom razdoblju su 24/20: VI. ID (mijenja čl. 54) i I. ID UPU-10.

**F10. Izlaz v0.22.4 ne sadrži popis izmjena (edits), a v0.22.3 ga je imao.**
Bez toga se klasifikacija CHANGED/UNCHANGED ne može provjeriti. Oznaka `"verified": true` znači samo „usporedba provedena".

**F11. Porijeklo snimki nije pod kontrolom registra.**
- v0.22.3 navodi putanje `C:\Users\…\Downloads\cesticahr_v0186b_ispravak_html\…`.
- 37444 i 41793 nisu u registru od 177 dokumenata, pa nisu prošli provjeru objave (footer, popis izdanja).

**F12. Lanac objava ima rupu.**
Preambula 6/20 navodi lanac 01/08, 11/12, 34/12, 17/14, 36/16, 02/17, 10/18, 18/18.
**02/17 nije u korpusu.** Za 17/14 u istom broju postoje tri akta Baške; PPUO je „ciljana izmjena", koja se prepoznaje po naslovu, ne po broju SN.

**F13. Run_report ima 35 podizvještaja od v0.19.0 do v0.22.4.**
U svima su `confirmed_amendment_chains`, `confirmed_effective_rules` i `confirmed_generations` (gdje postoje) jednaki 0. Od v0.20.1 nadalje većina se odnosi na jedan do tri članka.

---

## B. Pretpostavke (neprovjerene; kako ih provjeriti)

| # | Pretpostavka | Provjera |
|---|---|---|
| P1 | Razlike 13/20→26/20 u st. 3–5 su artefakt oznaka i preloma (26/20 je druga HTML struktura: 13 redaka umjesto 44), a ne sadržaj | usporedba nad slojem bez oznaka (§C2) na HTML-u 26/20 |
| P2 | Brisanje „i" u st. 4 (18/18→13/20) je pravopis „slijedeće"→„sljedeće". 13/20 ima oba oblika u st. 4. Može biti i brisanje veznika „i", koje bi bilo sadržajno | HTML 18/18, uvid u kontekst ±40 znakova |
| P3 | Dvotočka iz 36/16 nedostaje već u 18/18, ili je izgubljena tek u 13/20 | HTML 18/18 |
| P4 | Pročišćeni tekst je deklaratoran; pravni izvor su izvorne odluke, pa kod neslaganja prevladava izmjena | potvrda pravnika; dotad ga tretirati kao kontrolnu točku, ne kao izvor |
| P5 | 02/17 ne dira čl. 126 | preuzeti 02/17 i provjeriti |

---

## C. Odgovori na pitanja (preporuke)

### C1. Parser članaka, stavaka, alineja i podalineja
1. **Snimka je nepromjenjiva i registrirana.** Svaka korištena stranica mora biti u registru objava (sha256, izdanje, redni broj, status provjere). Lokalne putanje iz Downloads ne smiju biti izvor (F11).
2. **Profil izvora umjesto jednog parsera.** Najmanje tri profila:
   - klasični `<p>` po retku (13/20);
   - stranice s drugačijim rasporedom redaka (26/20: 984 KB, 13 redaka čl. 126 umjesto 44; vjerojatno Word-izvoz, nisam vidio);
   - PDF ili skeniran tekst, kao poseban status bez strukturnih tvrdnji.

   Profil se prepoznaje automatski, a nepoznat profil daje `STRUCTURE_UNKNOWN`.
3. **Dva tekstna sloja s mapom pomaka.**
   - *Prikazni sloj* čuva inline oznake (sub/sup).
   - *Usporedbeni sloj*: NFC; **inline oznake uklonjene bez razmaka** (sub, sup, span, b, i, font); blok oznake (`p`, `br`, `td`, `li`) postaju granica retka; nbsp postaje razmak; meka crtica se uklanja; bjeline se sažimaju; navodnici se ujednačuju.

   Svaki znak usporedbenog sloja zna svoj pomak u izvornim bajtovima, za citiranje dokaza. Popravlja F1 i F2.
4. **Strukturno stablo bez pravnih naziva.** Parser izrađuje samo članak → stavak `(n)` → retke. Svaki redak dobiva tip (`LEAD_IN` s dvotočkom, `HEADING` bez interpunkcije, `DASH_ITEM` s „- ", `TEXT`) i stabilan ID.
   Nazive „alineja/podstavak/podalineja" **ne** dodjeljuje parser (F6).
5. **Resolver adresa po odluci.** Adresu iz izmjene, npr. „st. 4, al. 2 »Veličina i površina građevina«, podal. 1", razrješava vlastiti resolver.
   Prihvaća samo kad se slažu barem **dva neovisna signala**: redni broj prema rječniku te odluke, citirani naslov, ili stara riječ koja postoji točno jednom u kandidatskom čvoru. Inače `ADDRESS_AMBIGUOUS`.
   Ponovljeni naslovi (F7) razrješavaju se tako, a ne redoslijedom pojave teksta.

### C2. Tipografske, uredničke i sadržajne razlike
Razlike se računaju na razini **tokena** usporedbenog sloja (ne znakova) i uvijek se izvoze s kontekstom. Svaka izmjena dobiva jednu klasu, a **zadana klasa je SADRŽAJNA**:
- **TIPOGRAFSKA** (zatvoren popis): bjeline i prijelomi; varijante navodnika; nbsp i meka crtica; razlika samo u oznakama (sub/sup/span); varijante crtice **koje nisu uz znamenku**.
- **UREDNIČKA** (zatvoren rječnik, svaka stavka s primjerom): pravopisni parovi (slijedeće/sljedeće), veliko slovo kod nedefiniranih pojmova, interpunkcija na kraju stavke nabrajanja **osim ako je propisana izmjenom** (F4).
- **SADRŽAJNA, nikad ne na bijeloj listi:**
  - znamenke, mjerne jedinice i %;
  - riječi ograničenja (najviše, najmanje, do, iznad, osim, isključivo, iznimno);
  - negacije (ne, nije, nisu);
  - modalni glagoli (može, mora, dozvoljeno);
  - veznici koji mijenjaju opseg (i, ili, i/ili, te, odnosno);
  - oznake zona, planova i čestica (k.č.);
  - pozivi na propise;
  - dodan ili uklonjen redak.

Jednoznakovna izmjena **nije** automatski tipografska (P2). Klasa razlike opisuje tekst, a pravnu relevantnost daje tek veza s operacijom (C3).

### C3. Povezivanje sadržajne promjene s člankom odluke o izmjenama
1. **Parser uputa** pretvara članak odluke u atomske operacije: ciljni plan, članak, adresa, vrsta (`REPLACE_UNIT`, `REPLACE_WORDS`, `INSERT_AFTER`, `INSERT_BEFORE`, `DELETE`, `ADD_UNIT`, `RENUMBER`), stara riječ, nova riječ, citat i hash.
   Jedna rečenica može nositi više operacija (F5: dvotočka i zamjena u istoj podalineji).
2. **Vrata identiteta plana.** Operacija se veže na plan samo ako naslov odluke i preambula identificiraju istu obitelj plana (F3: 2/18 je UPU-1).
3. **Ponovna primjena (replay) na kopiji.** Polazni tekst plus operacije redom objave daju predviđeni tekst.
   - Preduvjet operacije: stara riječ postoji točno jednom na razriješenoj adresi.
   - Postuvjet: nova riječ postoji, stara ne.
   - Ništa se ne zapisuje u izvor.
4. **Objašnjenje razlika.** Svaka sadržajna razlika između dva uzastopna pročišćena teksta mora imati barem jednu operaciju iz odluke objavljene **između** njih. Inače `UNEXPLAINED`: nedostaje odluka (P5), ispravak ili greška pročišćenja.
   Za 18/18→13/20 jedina sadržajna razlika u st. 3 objašnjava se s 6/20, čl. 18 (F2), što je dobar prvi pozitivni primjer.

### C4. Kontinuitet odredbe
- **Identitet odredbe:** `(obitelj plana, ID čvora)`, uz događaje u lozi (zamjena, umetanje, brisanje, prenumeracija, npr. „stavci 13.–15. postaju 11.–13.").
- **Polazište:** izvorni tekst plana (osnovna odluka). Pročišćeni tekstovi su **kontrolne točke**: uspoređuju se s predviđenim stanjem, a ne koriste se kao izvor (P4).
- **Potpunost lanca:** očekivani skup objava uzima se iz preambula samih odluka (F12) i uspoređuje s registrom. Svaka rupa (02/17) daje `CHAIN_INCOMPLETE` i blokira tvrdnju o kontinuitetu.
- **Kasniji akti:** stanje „na datum D" smije se tvrditi samo ako je pokrivenost do D potpuna, nema ukidanja (sloj klasifikatora ukidanja) i poznato je stupanje na snagu.
  Stanje „danas" zahtijeva sve to do danas. Usporedba pročišćenih tekstova nikad ne daje „važeće pravo".

### C5. Zaštita od lažno pozitivnih i automatske primjene
- Dva odvojena izlaza: `predviđeno` (replay) i `službeno` (pročišćeni tekst). Nijedan ne prepisuje drugi.
- Svaka tvrdnja `CONFIRMED_*` traži: citat odluke (hash), razriješenu adresu s dva signala, ispunjen postuvjet u sljedećoj kontrolnoj točki i potpun lanac.
- **Neovisni zlatni skup operacija** (vidi §E): moje ručne oznake, zaključane hashom, koje se ne daju razvoju. To isto smo radili za ukidanja.
- Ukloniti dvosmislene zastavice (`verified: true`) i postotke dovršenosti; izvoziti brojnik i nazivnik.

### C6. Regresijski testovi prije širenja na 177 dokumenata
Svaki test se temelji na činjenicama iz §A:
1. **Kanonizacija:** `k<sub>ig</sub>` mora dati „kig"; navodnici ujednačeni; tag, bjeline i prijelomi bez utjecaja na usporedbeni sloj (F1, F2).
2. **Umetak 6/20 čl. 18:** pronađen u 13/20 st. 3 točno jednom, iza propisanog sidra (F2).
3. **36/16 čl. 18:** parser uputa daje 18 operacija (ne 16), uključujući st. 2 i dvotočku (F5).
4. **Ponovna primjena 36/16 i 6/20 na 13/20:** 18 od 19 ispunjenih postuvjeta, a dvotočka mora dati `DEVIATION_FROM_AMENDMENT`, ne „tipografsko" (F4).
5. **Adresiranje:** „alineja 1" (36/16) i „podstavak 1" (6/20) daju isti čvor; „al. 2" u st. 4 je prva skupina (F6, F7).
6. **Vrata identiteta plana:** „U članku 126." iz odluke za UPU-1 (2/18) ne smije se vezati na PPUO (F3).
7. **Klasifikacija razlika:** sintetički parovi koji mijenjaju samo jedan token za svaku sadržajnu kategoriju iz C2 moraju dati SADRŽAJNA; promjena samo oznaka ili navodnika mora dati TIPOGRAFSKA.
8. **Nepotpuni lanac:** uklanjanje jedne objave iz lanca mora dati `CHAIN_INCOMPLETE` (F12).
9. **Porijeklo:** snimka koja nije u registru objava mora dati `PROVENANCE_UNVERIFIED` (F11).
10. **Izvoz:** svaka razlika nosi popis izmjena i kontekst (F10).

---

## D. Procjena arhitekture

**Zaključak: postojeća načela su dobra, ali način razvoja treba promijeniti prije nastavka.**

**Zadržati:**
- nepromjenjive snimke s hashom;
- registar objava (podaci za 171 akt neovisno sam provjerio na stranicama akata);
- zabranu automatske primjene;
- razdvajanje kandidata i potvrde;
- klasifikator ukidanja.

**Promijeniti:** od v0.19.0 razvoj ide kao niz uskih modula po slučaju (vXXXX po verziji, F13). Svaki rješava jedan članak, a nijedna tvrdnja nije potvrđena.
Problem nije u pravilima za usporedbu riječi, nego u tome što nedostaju tri zajednička sloja:
1. model dokumenta s dva tekstna sloja i mapom pomaka (C1);
2. parser uputa i resolver adresa (C1.5, C3);
3. ponovna primjena s kontrolnim točkama (C3, C4).

Kad ti slojevi postoje, članak 126. je **jedan ulaz u isti cjevovod**, a ne poseban modul. Isti cjevovod tada radi za članak 42. i za ostalih 175 dokumenata.

**Rizik ako se nastavi postojećim putem:** više verzija koje savršeno opisuju jedan članak, a ne generaliziraju. Tome u prilog ide i to da je v0.22.4 popravio strukturu 26/20, ali je istodobno izgubio popis izmjena (F10).

## E. Predloženi sljedeći korak (v0.23, bez širenja)
1. Ugraditi sloj modela dokumenta i dokazati ga na testovima 1, 2, 5, 9.
2. Ugraditi parser uputa i ponovnu primjenu za PPUO Baška, čl. 126 i 42; dokazati na testovima 3, 4, 6.
3. Preuzeti 18/18, 26/20 i 02/17 kao registrirane snimke; zatvoriti P1–P3 i P5.
4. Ja pripremam neovisni zaključani skup ručno označenih operacija iz 3–5 odluka izvan Baške. Odgovori ostaju kod mene, a razvoj dobiva samo preciznost, odziv i kritične pogreške.
5. Tek tada širenje na 177 dokumenata.

# plan-citac (EKSPERIMENT)

Čitač odluke o prostornom planu iz PDF-a Službenih novina PGŽ (dvostupačni prijelom). Zaseban alat: ne dira aplikaciju, `rules_krk.json`, GIS ni zoniranje i **ništa ne potvrđuje pravno** (`automatska_potvrda: 0`, `pravno_potvrdeno: false`).

    pip install pymupdf
    python3 citac.py ../../tests/pgz-odgovori/735-76-kornic-2026-10-22/sn-19-16/odluka_34138.pdf --naslov "UPU 2 - Kornić" --clanaka 108 -o izlaz/upu2_kornic_sn_19_2016.json
    python3 -m unittest -v test_citac

PyMuPDF je licenciran pod AGPL-3.0. Koristi se samo kao lokalni alat i ne ugrađuje se u aplikaciju.

## Što radi
1. **Granice odluke po sadržaju:** početak je podebljani naslov »ODLUKU o donošenju …« uz zadani naziv plana. Kraj je prvi »Klasa:« nakon toga. Ako naslov nije nađen točno jednom, vraća `ABSTAIN_GRANICA_ODLUKE`.
2. **Članci:** »Članak N.« na početku bloka, u redoslijedu čitanja (stranica → lijevi pa desni stupac → odozgo). Provjerava niz 1…N.
3. **Znakovi iz glifova:** dijakritik (ˇ ´ ¯) spaja se sa slovom ispod. Razmaci se određuju po položaju glifova. Sitne znamenke postaju indeks ili eksponent (»M1₁«, »m²«).
4. **Zaglavlja stranica** (»Stranica N — broj 19 … SLUŽBENE NOVINE«) uklanjaju se.
5. **Naslovi poglavlja** (numerirani blokovi iza kojih slijedi članak) odvajaju se u polje `poglavlje`. Naslov bez vlastitog članka ostaje u tekstu i bilježi se u `unutarnji_naslovi`.
6. **Tablice** (skupine vektorskih crta) se ne rekonstruiraju. Članak dobiva oznaku `[TABLICA – nije pouzdano rekonstruirana …]` i `status_tablica: TABLICA_NEPOUZDANA`. Izvorne ćelije čuvaju se u `tablice[].blokovi`.
7. **Rastavljene riječi** se spajaju, i preko stupca ili stranice. Crtica ostaje ako se ista složenica s crticom pojavljuje drugdje u dokumentu (»Primorsko-goranske«). Svaka odluka se bilježi (`crtice`), a izvorni tekst bloka čuva se u `sirovo`.
8. **`brojevi(tekst)` i `ima_broj(tekst, vrijednost, jedinica)`:**
   - prepoznaju »0,25,«, »0,75, a iznimno 1,0« i »40 %« kao udio 0,4;
   - ne nalaze »1,0« u »1,5«;
   - preskaču oznake stavaka »(1)«, pozive na članke, stavke i točke, k.č., broj glasila, mjerilo, oznake prikaza i cesta, godine i nabrajanja.
9. **`navod(s)`:** čita navod slijeva nadesno; riječ »čl./st./t./al.« mijenja vrstu brojeva koji slijede. Nabrajanja i rasponi (»st. 2. i 3.«, »st. 1.–3. i 5.«, »st. 2. do 4.«) ostaju stavci. Vraća i parove članak → stavci, točku pojmovnika, točku slovom »d)« i oznaku plana.
10. **Vrijednost uz oznaku** (»P₁ - 15«: broj mjesta na parkiralištu P₁) dobiva polje `oznaka`. `ima_broj()` je broji samo kad se ta oznaka izričito traži.

## Strukturiranje pravila (`strukturiraj.py`, EKSPERIMENT)

    python3 strukturiraj.py izlaz/upu2_kornic_sn_19_2016.json --clanci 38 39 40 -o izlaz/upu2_pravila_38_40.json --csv izlaz/upu2_pravila_38_40.csv
    python3 ocijeni.py izlaz/upu2_pravila_38_40.json oznake/upu2_cl38_40.json
    python3 -m unittest -v test_strukturiraj

- **Struktura:** članak → točke »a) …« → alineje »- …«. Podnabrajanje iza dvotočke ne broji se kao alineja.
- **Vrste građevina** čitaju se iz uvodne rečenice (»Utvrđuju se uvjeti gradnje …:«). »obiteljske kuće«, »višeobiteljske …« i »ugrađenu obiteljsku kuću« biraju podskup. Ako vrsta ne postoji u članku, pravilo dobiva status PREGLED.
- **Pravilo nastaje samo kad cijela alineja odgovara obrascu rečenice.** Alineja s brojem bez obrasca ide u `nepokriveno`, bez prijedloga.
- **Vrste pravila:** OSNOVNO, IZNIMKA (»a iznimno …«, »iznimno …«) i UVJETNO (vrijedi samo uz uvjet). Uvjet je uvijek doslovni odlomak alineje. Inače je status PREGLED.
- **Upućivanje »alineje 5. točke b) ovog članka«** razrješava se i provjerava (alineja mora postojati i biti uvjetna). »primjenjuju se odredbe iz točaka … članka 38.« bilježi se kao upućivanje, bez prepisivanja pravila.
- **Položaj u PDF-u:** blok u kojem alineja počinje (stranica, stupac, okvir).
- **Dvosmislen navod** (»čl. 38. i 39. st. 2.«) u `citac.navod()` dobiva `dvosmisleno: true`, a stavak se ne pripisuje nijednom članku.

### Uvjet, preduvjeti i izračun
- `uvjet_izvorni` je doslovni odlomak alineje.
- `preduvjeti` je popis: kod (npr. `ZONA_KPC`, `BEZ_OTVORA`, `KOSI_TEREN`, `GRADNJA_NA_MEDJI`), doslovni dokaz, položaj u PDF-u i parametri (npr. `nagib_veci_od_posto: 12`). Upućivanje na alineju razrješava se u preduvjete te alineje, s njihovim dokazom i položajem.
- `preduvjeti_logika`:
  - SVI;
  - NEJASNO, kad je u uvjetu »odnosno« (onda je status PREGLED).
- Dio uvjeta koji nije razvrstan u preduvjete također daje PREGLED.
- `za_izracun` je `true` samo za brojčanu vrijednost sa statusom PRIJEDLOG. Pravila s `vrijednost: null`, opisnom vrijednošću (npr. »pola visine …«, uz `vrijednost_struktura`) ili za pregled nikad nisu za izračun.
- `ne_primjenjuje_se_uz: ["ZONA_KPC"]`: osnovna vrijednost (i opća iznimka koja u zoni KPC ima izravan parnjak) kad ista alineja ima posebnu odredbu za zonu Kulturno-povijesne cjeline. Označeno kao tumačenje.

### Generalizacija
- `citac_tekst.py` izdvaja članke iz HTML-a ili običnog teksta. Uklanja zaglavlja glasila, odvaja naslove poglavlja, piše »m2« kao »m²« i spaja složenice.
- `slijepi_test.py` pokreće strukturiranje na novom izvoru bez izmjena i za svaku alineju bilježi ishod: PRAVILO, PREGLED, NEPOKRIVENO, BEZ_BROJA ili UPUCIVANJE.
- Ista odluka UPU-a 2 izdvojena drugim alatom (pdftotext): 89 točno, 5 za pregled, 5 propušteno, 0 pogrešno. Propuštena je jedna alineja, jer je pdftotext spojio »Kulturno-povijesne« u »Kulturnopovijesne«; modul ju je odbio umjesto da pogađa.

### Ručne oznake i neovisnost
`oznake/upu2_cl38_40.json` sadrži 97 pravila i 2 upućivanja, ručno iz teksta čl. 38.–40. **Oznake je napisao isti autor koji je napisao obrasce, pa rezultat 97/97 nije neovisna ocjena.** Obrasci su pisani za upravo te rečenice.

Za neovisnu ocjenu drugi označivač, bez uvida u ove oznake i u kod obrazaca, ispunjava isti oblik (`pravila_oznacavanja` u datoteci) i pokreće `ocijeni.py` sa svojom datotekom.

### Opća gramatika (`gramatika.py`) i PPUG Krk
- Gramatika radi na razinama stavak »(n)« → točka »x)« (samo redom a, b, c …) → alineja.
- Oblik odredbe: [iznimno] [uvjet] PREDMET (rječnik) [subjekt] GLAGOL [usporedba] VRIJEDNOSTI (jedna ili »- za OBLIK: vrijednost«) [, a PREDMET …] [, uz uvjet da …].
- Koristi se kad obrasci UPU-a 2 ne prepoznaju članak (`gramatika_ukljucena`).
- PPUG Krk čl. 22. i 23. prema zamrznutim neovisnim oznakama (`oznake/neovisno`, 55 zapisa): 48 točno, 0 pogrešno, 7 za pregled (svih 7 odgovara oznakama), 0 propušteno. Gramatika je pisana nakon uvida u oznake (vidi `oznake/neovisno/ZAMRZNUTO.md`).
- `kisNadzemni` i `kisPodrum` su zasebni parametri. »Povijesne graditeljske cjeline« su preduvjet `ZONA_POVIJESNA_CJELINA`, a ne `ZONA_KPC`.
- U ostatku PPUG-a (čl. 4.–173.) gramatika ne predlaže ništa izvan čl. 22. i 23. U UPU-u 2 se ne uključuje, pa je rezultat ondje i dalje 92 / 0 / 7 / 0.

## v2.1 (grana `eksperiment-citac-v2`)

    python3 strukturiraj_v2.py dokazi.json -o pravila_v2.json
    python3 usporedi_v2.py
    python3 -m unittest test_v2 test_citac test_strukturiraj

- **Zamrznuta v1 se ne mijenja.** `gramatika_v2.py` i `strukturiraj_v2.py` su nove datoteke; v1 obrasci UPU-a 2 i dalje imaju prednost.
- **Statusi** (polja prilagođena postojećoj shemi):
  - `PRIJEDLOG` = ACCEPTED (automatski prihvaćen prijedlog, nije pravna potvrda);
  - `PREGLED` = REVIEW;
  - `ODBIJENO` = REJECTED (`nepokriveno`).
- **Polja pravila:**
  - `razlog_kod` (reason_code);
  - `izvor_clanak`, `izvor_stavak`;
  - `izvorni_citat` (source_quote, doslovno iz teksta članka);
  - `vrsta_gradevine` (building_type: skupine, oblici, stanje, uz_podrum);
  - `parametar`, `operator`, `vrijednost`, `jedinica`;
  - `uvjeti` (conditions);
  - `iznimke` / `iznimka_od` (exceptions);
  - `nerijesene_ovisnosti` (unresolved_dependencies);
  - `formula`, `interval`, `alternative`, `referenca`, `ogranicenje`.
- **`NIJE_PROPISANO` ≠ `NEOGRANIČENO`.** »se ne propisuje« daje operator `nije_propisano`, vrijednost null i `za_izracun: false`. Neograničeno se zaključuje samo kad tako piše.
- **Čl. 33. (udaljenosti):**
  - `max(h/2, X)` nastaje samo kad h/2 i X imaju istu referentnu točku (granica čestice);
  - h/2 od »granice susjedne građevine« i X od granice čestice ostaju dva pravila (`RAZLICITE_REFERENTNE_TOCKE`);
  - sva pravila čl. 33. su PREGLED, s razlozima.
- **Usporedba:** čl. 22./23. idu kroz zamrznuti `ocijeni_neovisno.py`; čl. 25./33. kroz zasebno, verzionirano `oznake/neovisno_cl25_33/mapiranje_v2.json`. Interval 17–23° je jedan zapis, a granice su zasebna pravila.

### Jezični sloj (`jezik_hr.py`, `semantika_hr.py`)
- **Pomoćni izvor:** Hrvatski pravopis IHJJ-a, radna inačica 2013. (SHA-256 `33cbbfa7…`, nije u repozitoriju).
  - Korišteni su samo odjeljci o bjelini, točki, zarezu, kraticama, kosoj crti, crtici i ije/je; svako pravilo navodi stranicu.
  - **Pravopis nije izvor pravila o padežima.** `MorfoloskiAnalizator` je sučelje za morfologiju. Zadana provedba vraća »nepoznato«; `PopisOblika` je ručni popis i tako je i označen.
- **`normaliziraj()` radi samo pravopisne transformacije i transformacije zapisa jedinice:** m 2 → m², 4,0 metra → 4,0 m, bjelina.
  - Svaka transformacija se bilježi s izvornim odlomkom, položajem i izvorom pravila.
  - `izvorni_odlomak()` vraća doslovni izvor za bilo koji raspon normaliziranog teksta.
- **`brojevi()`** razlikuje decimalni zarez, redne brojeve, tisućice (»10.000« je dvosmisleno), oznake (NA15.2), formule (h/2) i brojeve glasila. `istovrijedno()` povezuje »0,50« = »0,5« i »500 m 2« = »500m²«.
- **Kratice i oznake:** kratice (čl., st., t., npr., k.č.) ne lome rečenicu, a granica iza rednog broja bilježi se kao dvosmislena. Oznake članaka, stavaka, točaka, alineja i hijerarhijske numeracije se prepoznaju.
- **Pogreške u izvoru se ne ispravljaju**, samo se bilježe u `jezicne_napomene`:
  - »rekonsrturirati«, »prenamjeniti«, »slijedeće«;
  - kosa crta između riječi (»ili« ili »i«);
  - spojnica između oznaka zona;
  - »odnosno« bez zareza ili sa zarezom.
- **Semantika je odvojena od pravopisa.** `semantika_hr.py` obrađuje »ne propisuje se«, »samo kao«, »najmanje«, »najviše«, »iznimno« i »može iznositi i«. `provjeri_pravilo()` šalje pravilo u PREGLED ako se operator ili vrsta pravila ne slažu s izrazom u citatu.

## Neriješeno (stanje: SN PGŽ 19/2016, UPU 2 Kornić)
- **Strukturiranje pokriva samo čl. 38.–40. UPU-a 2.** Za PPUG Krk (čl. 22. i 23.) obrasci se tek trebaju napisati. Do tada će te alineje ići u `nepokriveno`.
- **Prepoznavanje je provjereno samo na ovom PDF-u.** Sidra (naslov odluke, »Klasa:«), prag razmaka (1 pt), prepoznavanje zaglavlja i tablica treba provjeriti na drugim brojevima Službenih novina i na PPUG-u.
- **Tablica u čl. 53 (normativi parkiranja)** nije rekonstruirana; vrijednosti se moraju ručno prepisati i provjeriti.
- **Podstavci, alineje i iznimke** (osnovna vrijednost ili iznimka, vrsta građevine, uvjet) nisu razdvojeni. To je sljedeća faza.
- **`brojevi()` je heuristika.** Nabrajanja s malim slovom (»2. križ«) i popisi k.č. bez kose crte mogu proći kao vrijednosti. Za dokaz treba broj uz jedinicu i kontekst.
- **Greške u izvornom tekstu ostaju kako jesu:** »broj32/08«, »trgovačko- uslužne« i slično (8 crtica s razmakom unutar retka).
- **HTML iste odluke nema članke 54–107**; izvor je PDF.
- Pravna aktualnost UPU-a 2 i dalje nije potvrđena (`pravna_provjera: NIJE_POTVRDENO`).

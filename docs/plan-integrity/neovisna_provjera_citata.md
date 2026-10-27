# Neovisna provjera citata – UPU 2 Kornić (SN PGŽ 19/2016)

**Repozitorij:** /home/claude/cestica-zg (grana `plan-integrity-v10-provjera`), datoteka `src/rules_krk.json`, objekt `upu["UPU 2"].citati` (21 citat). Nijedna datoteka u repozitoriju nije mijenjana.

## Izvor i postupak

- PDF: `tests/pgz-odgovori/735-76-kornic-2026-10-22/sn-19-16/odluka_34138.pdf`
- SHA-256: `5b4ec76db4232f3efad0dd7ad01e109130bcc3a2702c95ff9857bf48590eae08`. Jednak je `pdf.sha256` u `_meta.json`, dakle **PODUDARA SE**.
- Tekst sam izvukao sam (`pdftotext` bez `-layout` i `pdfplumber` na razini znakova). Postojeću datoteku `odluka_34138_pdf_tekst.txt` nisam koristio.
- Odluka o donošenju UPU 2 – Kornić (stavka 21.) počinje na str. 2204 broja 19 i obuhvaća čl. 1.–108.
- Normalizacija prije usporedbe:
  - tekst sam prebacio u Unicode NFC, jer PDF slova sa znakovima (č, ć, š, ž) sprema rastavljeno, kao osnovno slovo i kvačicu;
  - spojeni znak „d + U+0304 + U+00AF” zamijenio sam s „đ” (u PDF-u se đ crta kao d s precrtom; vizualno je to đ);
  - uklonio sam zaglavlja stranica i spojio sve razmake i prijelome redaka.
- Za svaki pogodak automatski sam odredio članak i zadnju prethodnu oznaku točke `a)`–`i)` odnosno stavka `(n)`.
- Rastavljanje riječi na kraju retka ni u jednom citatu ne utječe na podudaranje.

### Znakovne posebnosti (provjereno na razini znakova u PDF-u)

- **„17o” / „23o” (čl. 38. d)):** u PDF-u je to slovo `o` (U+006F), u fontu AdvTTR veličine 6,0 pt umjesto 9,1 pt i podignuto oko 1,7 pt. Riječ je o tiskarskoj zamjeni za znak stupnja: vizualno piše „17°”, a u tekstnom sloju „17o”. Citat „17o i 23o” doslovno odgovara tekstnom sloju PDF-a. U prikazu bi bilo točnije pisati „17° i 23°”, ali zapis nije netočan.
- **„30˚” (čl. 85.):** u PDF-u je U+02DA (RING ABOVE). Citat koristi isti znak U+02DA. Podudara se.
- **„m2”:** u PDF-u je „2” obični znak iste veličine. Citati pišu „m2”, što se podudara.

## Tablica

| # | Grupa / ključ / tip | Navedeno (čl./t.) | Presuda | Izvorni tekst (cijela alineja, normalizirano) | Napomena |
|---|---|---|---|---|---|
| 1 | slob / minC / obit | 38. a) | TOČNO | „- najmanja površina građevne čestice obiteljske kuće iznosi 500 m2, a iznimno 400 m2 ako se građevna čestica nalazi u okruženju već uređenih i izgrađenih građevnih čestica,” | Doslovno, cijela alineja (bez završnog zareza). Vrijednosti minC 500 i minCIznimno 400 se podudaraju. |
| 2 | slob / minC / visobit | 38. a) | TOČNO | „- najmanja površina građevne čestice višeobiteljske kuće iznosi 500 m2,” | Doslovno. visobit.slob.minC = 500 se podudara. |
| 3 | slob / izg | 38. a) | TOČNO | „- najveći koeficijent izgrađenosti građevne čestice iznosi 0,25,” | Doslovno. Isti izraz ima i čl. 39./40. (te 16., 23., 26.–28.), ali je ispravno smješten. izg 0,25 se podudara. |
| 4 | slob / kis | 38. a) | TOČNO | „- najveći koeficijent iskorištenosti iznosi 0,75, a iznimno 1,0 ako se višeobiteljska kuća gradi prema uvjetima alineje 5. točke b) ovog članka.” | Doslovno (bez završne točke). kis 0,75 i visobit.kosi.kis 1,0 se podudaraju. Iznimka vrijedi samo za višeobiteljsku kuću, a obit nema `kosi`, što je u skladu s izvorom. |
| 5 | slob / tl | 38. b) | TOČNO | „- najveća tlocrtna površina građevine iznosi 200 m2,” | Doslovno. tlMax 200 (obit i visobit slob) se podudara. |
| 6 | slob / gbp | 38. b) | TOČNO | „- najveći GBP iznosi 200 m2 za građevnu česticu obiteljske građevine, odnosno 400 m2 za građevnu česticu višeobiteljske građevine pri čemu se u navedeni GBP uračunavaju sve građevine na građevnoj čestici.” | Doslovno. gbpMax 200 / 400 i gbpUkupno = true se podudaraju. |
| 7 | slob / meda | 38. c) | TOČNO | „- najmanja udaljenost građevine od ostalih međa građevne čestice iznosi 4 m, a iznimno 3 m ako građevina nema otvore, prohodne terase ili otvorena stubišta prema tim međama; iznimno na građevnim česticama smještenim unutar zone Kulturno-povijesne cjeline utvrđene u stavcima (1) i (2) članka 83. najmanja udaljenost građevine od ostalih međa građevne čestice iznosi pola visine građevine, ali ne manje od 3 m, a iznimno 2 m ako građevina nema otvore …; iznimno se obvezna udaljenost od pola visine građevine ne mora primjenjivati ako se višeobiteljska građevina gradi prema uvjetima alineje 5. točke b) ovog članka.” | Doslovno do „;”. Izostavljene su iznimke za kulturno-povijesnu cjelinu (h/2, najmanje 3 m / 2 m). One su obrađene zasebno u `meda.opisIznimka` i `napomene`, pa skraćivanje ne mijenja značenje navedenih 4 m / 3 m (izvan te cjeline). meda.min 4 i minBezOtvora 3 se podudaraju. |
| 8 | dvoj / minC / obit | 39. a) | TOČNO | „- najmanja površina građevne čestice obiteljske kuće iznosi 300 m2, odnosno višeobiteljske kuće 400 m2,” | Doslovno. obit.dvoj 300 i obit.ugr 300 se podudaraju. Čl. 39. pokriva i ugrađenu obiteljsku kuću. |
| 9 | dvoj / minC / visobit | 39. a) | TOČNO | (ista alineja kao #8) | Doslovno. visobit.dvoj.minC 400 se podudara. Čl. 39. višeobiteljsku kuću dopušta samo kao dvojnu, ne ugrađenu, a `visobit.oblici` nema „ugr”, što je u skladu s izvorom. |
| 10 | dvoj / izg | 39. a) | TOČNO | „- najveći koeficijent izgrađenosti građevne čestice iznosi 0,25,” | Doslovno. 0,25 se podudara. |
| 11 | dvoj / kis | 39. a) | TOČNO | „- najveći koeficijent iskorištenosti iznosi 0,75, a iznimno 1,0 ako se višeobiteljska kuća gradi prema uvjetima alineje 5. točke b) ovog članka.” | Doslovno. 0,75 / 1,0 se podudaraju. |
| 12 | dvoj / tl | 39. b) | TOČNO | „- najveća tlocrtna površina građevine iznosi 150 m2, odnosno 100 m2 za ugrađenu obiteljsku kuću,” | Doslovno. obit.dvoj 150, obit.ugr 100 i visobit.dvoj 150 se podudaraju. |
| 13 | dvoj / gbp | 39. b) | TOČNO | „- najveći GBP iznosi 200 m2 za građevnu česticu obiteljske građevine, odnosno 400 m2 … uračunavaju sve građevine na građevnoj čestici.” | Doslovno, istovjetno čl. 38. b). Vrijednosti se podudaraju. |
| 14 | dvoj / meda | 39. c) | NEPRIKLADNO (doslovno, ali skraćeno) | „- najmanja udaljenost građevine od ostalih međa građevne čestice, izuzev međa na koje su prislonjene, iznosi 4 m, a iznimno 3 m ako građevina nema otvore, prohodne terase ili otvorena stubišta prema tim međama; iznimno na građevnim česticama smještenim unutar zone Kulturnopovijesne cjeline … pola visine građevine, ali ne manje od 3 m, a iznimno 2 m … ovog članka.” | Tekst je doslovan i u pravom članku i točki, ali je odrezan na zarezu nakon „4 m”. Time izostaje „a iznimno 3 m ako građevina nema otvore…”, na kojem počiva vrijednost `meda.minBezOtvora = 3` (zajednička za sve oblike). Citat za slob (#7) tu iznimku sadrži, pa je ovaj za dvoj nedosljedan. Prijedlog je produžiti citat do „;”. Brojčane vrijednosti (4 / 3) odgovaraju izvoru. |
| 15 | stamb / minC / stamb | 40. a) | TOČNO | „- najmanja površina građevne čestice iznosi 500 m2,” | Doslovno. Isti izraz postoji i u drugim člancima, ali je čl. 40. a) ispravan. stamb.slob.minC 500 se podudara. |
| 16 | stamb / izg | 40. a) | TOČNO | „- najveći koeficijent izgrađenosti građevne čestice iznosi 0,25,” | Doslovno. 0,25 se podudara. |
| 17 | stamb / kis | 40. a) | TOČNO | „- najveći koeficijent iskorištenosti iznosi 0,75, a iznimno 1,0 ako se građevina gradi prema uvjetima alineje 5. točke b) ovog članka.” | Doslovno (ovdje piše „građevina”, a ne „višeobiteljska kuća”, ispravno). 0,75 i stamb.kosi.kis 1,0 se podudaraju. |
| 18 | stamb / tl | 40. b) | TOČNO | „- najveća tlocrtna površina građevine iznosi 200 m2,” | Doslovno. tlMax 200 se podudara (tlMin 100 prema prethodnoj alineji). Čl. 40. nema GBP, a gbpMax = null i nepostojanje citata za GBP u skladu su s izvorom. |
| 19 | krov | 38. d) | TOČNO | „- krovište građevine može biti ravno ili koso; ako se gradi kao koso može biti dvostrešno ili višestrešno i mora biti s nagibom krovnih ploha između 17o i 23o, a pokrov mora biti mediteran crijep ili kupa kanalica,” | Doslovno prema tekstnom sloju. „o” je u PDF-u eksponentno slovo o, vizualno „°” (vidi gore). Izostavljen je završetak o pokrovu, što ne utječe na nagib. ravniDopusten = true i nagib 17–23 se podudaraju. Primjena na dvoj i stamb je ispravna, jer čl. 39. d) i 40. c) upućuju na čl. 38. d). Isti tekst ima i čl. 27. d). |
| 20 | zastitaC_krov | 85. st. 2. | TOČNO | „(2) Za zonu »C« propisuju se sljedeći uvjeti: … – u okviru šire zone naselja mogući su zahvati … visine najviše dvije nadzemne etaže, bez povišenja nadozida za potkrovlje. Građevine moraju imati kosi krov s nagibom tradicijskog krova (oko 30˚) s pokrovom kupom kanalicom ili pločama lokalnog kamena.” | Doslovno, cijela rečenica (bez završne točke), st. (2), 2. alineja. Znak ˚ (U+02DA) je isti kao u PDF-u. krovKosi = true i krovNagib 30 se podudaraju. |
| 21 | zastitaC_etaze | 85. st. 2. | TOČNO | „– u okviru šire zone naselja mogući su zahvati promjene građevne strukture, odnosno izgradnja nove ili zamjenske na mjestu one koja nema građevinske ni kulturno povijesne vrijednosti, ali uz poštivanje povijesne građevne linije, visine najviše dvije nadzemne etaže, bez povišenja nadozida za potkrovlje.” | Doslovan ulomak, st. (2), 2. alineja. Isti izraz ponavlja se u 3. alineji (dvojne i građevine u nizu na povijesnim česticama). Ulomak počinje usred rečenice („visine” je genitiv), ali značenje nije promijenjeno. etazeMax 2 i nadozid = false se podudaraju. |

## Sažetak

- **Doslovnost:** svih 21 citata doslovno postoji u izvornom PDF-u, uz zanemarene prijelome redaka i razmake. Nema razlika ni u jednom znaku. Jedina vizualna razlika je „17o / 23o”: tekstni sloj PDF-a sadrži slovo „o” (eksponent), a ne „°”, pa je citat vjeran tekstnom sloju.
- **Članak i točka/stavak:** svih 21 nalazi se u navedenom članku i točki (čl. 85. u stavku (2)).
- **Brojčane vrijednosti u `tipovi.*`, `meda` i `simulator`:** nema neusklađenosti s citatima.

| Presuda | Broj |
|---|---|
| TOČNO | 20 |
| NEPRIKLADNO | 1 (#14 dvoj/meda: skraćen tako da izostaje iznimka „3 m bez otvora”, na kojoj počiva `meda.minBezOtvora`) |
| NETOČNO | 0 |
| KRIVI ČLANAK ILI TOČKA | 0 |

### Sporedna zapažanja (izvan 21 citata, informativno)

- `tipovi.obit.txt.minC` i `txt.tl` su sažeci s umetnutim zagradama, a ne doslovni citati. Ako ih aplikacija prikazuje kao navode, treba ih označiti kao prepričane.
- Vrijednost `kisPodrum` (0,75) nema poseban oslonac u čl. 38.–40. i nisam je provjeravao.

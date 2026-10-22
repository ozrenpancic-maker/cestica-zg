# Čestica 735/76 k.o. Kornić: izvorni odgovori PGŽ servisa i usporedba sa stanjem projekta

Dohvat: 22. 10. 2026. oko 19:58 UTC, ugrađeni preglednik na Ozrenovu računalu (oblak ne doseže gisportal.pgz.hr, CONNECT 403).
Izvor: GEOPORTAL PGŽ, gisportal.pgz.hr, `STANJE/NAMJENA_POVRSINA_NOVO` i `STANJE/IZRADA_PP` (javno, bez jamstva).
Tijela odgovora spremljena su bajt-za-bajt; SHA-256 izračunat u pregledniku i ovdje se podudara (`_meta.json`).
Razina pouzdanosti svega ispod: **kandidat** (sloj županije, nije pravna potvrda).

## Datoteke

| Datoteka | Upit |
|---|---|
| `namjena_tocka_doc.json`, `planovi_tocka_doc.json` | točno adrese iz `docs/pgz-servisi.md` (GET, `f=json`, `outFields=*`) |
| `namjena_tocka_app.geojson`, `planovi_tocka_app.geojson` | parametri kao `pointQuery()` u aplikaciji (`f=geojson`, popis polja za planove); poslano kao POST, aplikacija šalje GET s istim parametrima |
| `namjena_cestica_app.geojson` | kao `polyQuery()`: granica iz `docs/primjeri/kornic_cestica_735_76.geojson`, POST |

Oba oblika upita za planove vraćaju istih 29 zapisa (provjereno po vrsti, SN broju, statusu i nazivu).

## Rezultat

**Namjena (PPUG Krk, izvor SN 18/19)**
- Točka (45,044049, 14,615896) je unutar čestice; zona **NA2**, građevno područje naselja Kornić, izgrađeni dio.
- Po granici čestice (405,3 m²): NA2 99,78 %, P3 (ostalo poljoprivredno tlo) 0,22 %. Aplikacija P3 ne prikazuje (prag 0,5 %); to je rubni dodir granica, ne stvarni dio zone.

**Planovi koje aplikacija (`krkPlans`) prikazuje kao važeće**

| Vrsta | SN | Naziv u sloju | Stupanje na snagu |
|---|---|---|---|
| UPU | 2016-19 | Odluka o donošenju UPU 2 - Kornić | 05.08.2016. |
| PPUO/G Krk | 2020-29 | pročišćeni tekst i grafički dio PPUG Krka | 27.08.2020. |
| PPŽ | 2024-12 | pročišćeni tekst odredbi PPŽ | 15.03.2024. |

**U izradi:** V. izmjene i dopune PPUG Krka (zadnja odluka SN 2025-07; glasila 47/23, 07/25) i IV. izmjene i dopune PPŽ (SN 2026-28; 48/23, 09/25, 28/26). DPPR se ne prikazuje.

## Usporedba s `docs/STANJE-PROJEKTA.md`

| Tvrdnja u dokumentu | Nalaz | Ocjena |
|---|---|---|
| §2: sloj daje UPU 2 Kornić (SN 19/16, važeći), PPUG Krk i PPŽ | potvrđeno; PPUG = PT 29/20, PPŽ = PT 12/24 | ✔ odgovara |
| §2: zona unutar UPU-a nije automatska (raster) | `NAMJENA_POVRSINA_NOVO` daje samo zonu PPUG-a (NA2), ne zone UPU-a (M11/M2) | ✔ odgovara; dokument ne spominje NA2, vrijedi dopisati |
| §2: pravila M11/M2 (čl. 38.–40.) | ovi servisi to ne pokrivaju | – nije provjerljivo ovdje |
| §3: IZRADA_PP daje vrstu, status, SN, poveznice, datum stupanja na snagu | sva polja prisutna; status ima i vrijednost „VAN SNAGE ODLUKA O IZRADI" koju dokument ne navodi | ✔ uz dopunu |
| §5.3: izmjene PPUG Krk nakon 2020.? | sloj nema važeću odluku PPUG-a noviju od 29/20; V. ID su u izradi (odluka o izradi 47/23) | ⚠ sloj to ne može sam potvrditi; kontrola u SN ostaje otvorena |
| §5.4: rupe u registru (PPUG 41/09, 28/11, 23/15, 18/19; UPU 2 19/16 id 34138) | sloj daje SN_LINK id-eve: 41/09 → 17911, 28/11 → 22832, 23/15 → 32507 (ciljane III. ID; isti broj glasila ima i 32509, odluku o izradi van snage), 18/19 → 40132, 19/16 → 34138 | kandidati za popunu; 34138 se podudara s dokumentom |
| `pgz-servisi.md`: primjeri polja | stvarni odgovor za 735/76 sadrži i polja koja tablica ne navodi (`SEKUNDARNA_NAMJENA`, `DETALJNA_NAMJENA`, `OSJETLJIVOST`, `MIKROREGIJA`, `STATUS_GIS`, `DatumStVanSnage` …) | informativno |

## Uočeno u podacima sloja (za oprez)

- Tri zapisa bivšeg PP Općine Krk (1978., 1988., 1993.) imaju status VAN SNAGE, ali prazan `DatumStVanSnage`.
- Zapis 2015-23 „VAN SNAGE ODLUKA O IZRADI" ima datum objave (17.05.2015.) prije datuma donošenja (16.07.2015.): vjerojatno greška unosa u sloju.
- Za PPUG 41/09 `STATUS_GIS` je `INFO_TEXT_ONLY` (nema grafike u sloju).

Ništa od ovoga nije pravna potvrda; pravni dokaz ostaje objava u Službenim novinama.

## Provjera prema objavi SN PGŽ 19/2016 (id 34138)

Izvor: http://www.sn.pgz.hr/default.asp?Link=odluke&id=34138, dohvat 22. 10. 2026. 20:01 UTC. Izvorni HTML i tekst su u `sn-19-16/` (SHA-256 u `sn-19-16/_meta.json`).

| Podatak | Županijski sloj | Objava u SN | Ocjena |
|---|---|---|---|
| Glasilo | SN 2016-19 | godina XXIV., broj 19., petak 29. srpnja 2016. | ✔ |
| Donošenje | 27.07.2016. | Gradsko vijeće Grada Krka, sjednica 27. srpnja 2016. | ✔ |
| Objava | 29.07.2016. | 29. srpnja 2016. | ✔ |
| Stupanje na snagu | 05.08.2016. | čl. 108.: osmoga dana od dana objave | ⚠ uz uobičajeno računanje (dan objave se ne računa) to je 06.08.2016.; razliku od jednog dana treba potvrditi pravno |
| Obuhvat | UPU 2 sadrži točku čestice | čl. 1.: građevinsko područje naselja Kornić, NA 2 | ✔ odgovara zoni NA2 iz `NAMJENA_POVRSINA_NOVO` |

**Nalazi**
- HTML objave sadrži samo čl. 1.–53. i čl. 108.; čl. 54.–107. nisu u HTML-u (tekst skače nakon tablice parkiranja u čl. 53.). Puni tekst je u priloženom PDF-u (`download.asp?id=28072`, nije preuzet). Čl. 83. (kulturno-povijesna cjelina), na koji se pozivaju čl. 38. i napomena u aplikaciji, zato ovdje **nije provjeren**.
- U uvodu se Odluka o izradi navodi kao SN 14/08, a u čl. 1. kao SN 32/08. Neusklađenost je u samom izvoru.
- Čl. 37.–40.: svih 17 navoda iz `src/rules_krk.json` (UPU 2) doslovno se nalazi u objavi; brojke (500/400/300 m², kig 0,25, kis 0,75 i 1,0, tlocrt 60–200/150/100 m², 7,5 i 10,5 m, međe 4/3 m, regulacija 6/9 i 4/7 m, zelenilo 40 %) odgovaraju.
- **Pogreška u aplikaciji, ispravljena na `razvoj`:** aplikacija je za višeobiteljsku kuću nudila i „ugrađenu" gradnju (min. čestica 400 m², tlocrt 150 m²). Čl. 37. st. 1. dopušta višeobiteljsku kuću samo kao slobodnostojeću ili dvojnu, a čl. 39. obuhvaća ugrađenu samo za obiteljsku. Uklonjeno i dodan test.

**Za česticu 735/76 (405 m² prema grafičkom katastru, zona M11 ili M2 ako je korisnik takvu odabere):** slobodnostojeća obiteljska kuća moguća je samo po iznimci od 400 m² (okruženje uređenih i izgrađenih čestica, čl. 38.); slobodnostojeća višeobiteljska (500 m²) i stambena građevina (500 m²) nisu; dvojna obiteljska (300 m²) i dvojna višeobiteljska (400 m²) jesu prema površini. Upisana površina u zemljišnoj knjizi može se razlikovati.

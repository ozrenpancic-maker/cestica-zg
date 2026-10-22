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

# Osnovni i napredni način

Stanje 24. 10. 2026., grana `razvoj`.

**Prekidač i zadano stanje**
- Prekidač „Napredno” je u zaglavlju, uz izbornik.
- Pri svakom pokretanju aplikacija je u **osnovnom** načinu (odluka korisnika, 24. 10.). Izbor se ne pamti između pokretanja.
- Na mobitelu je prekidač mali gumb s natpisom ispod. Gumb „Traži” je ispod 420 px širine ikona, da polje za pretragu ostane upotrebljivo.

**Kako radi**
- Osnovni način samo **skriva prikaz** (CSS na `body.osnovno`, pravila iz `modCss()`).
- Izračuni, unosi, spremanje i izvještaji rade jednako u oba načina.
- Ukupna investicija u osnovnom načinu uključuje i stavke koje se uređuju u naprednom načinu (priprema terena, komunalni doprinos, priključci, okućnica). Uz nju piše koje su to stavke (`#modNap`).
- Kad se iz sažetka ili prečaca otvori napredni odjeljak, aplikacija sama prelazi u napredni način (`pogIdi` → `modSkriven`).
- Upozorenja se ne skrivaju: sažetak, ocjena gradnje, provjere simulatora, priroda i poplave, tereti.

**Osnovni način**

| Kategorija | Prikazano |
|---|---|
| 01 Prostorni planovi i namjena | namjena, ocjena građevinskog područja |
| 02 Gradnja i simulator | područje za gradnju, izračun za česticu, uvjeti gradnje, simulator (predložak, širina, dubina, etaže, okret, „Predloži položaj”, provjere), 3D pogled |
| 03 Rizici i pravne provjere | ZK izvadak, priroda i poplave (i internet), rizici i provjere, kontrolna lista kupnje |
| 04 Pristup i infrastruktura | sve |
| € Troškovi | procjena gradnje (površina, katnost, gradnja, standard, faza, podrum), kupnja zemljišta, ukupna investicija |
| 05 Projekt i dokumentacija | projekt i dozvola, gradnja i useljenje, dokumentacija, PDF, spremanje, dijeljenje |

**Samo u naprednom načinu**

| Vrsta | Što je skriveno |
|---|---|
| Odjeljci (`data-k`) | `isk`, `oku`, `skica`, `sun`, `pv`, `tipcmp`, `rparams`, `rex`, `krkTxt`, `risks`, `povijest`, `prep`, `kd`, `krkKd`, `costs`, `scen`, `vrij`, `proj`, `bfaze`; skupine „Karte prostornog plana”, „Sunce i energija” i „Pouzdanost podataka” |
| Okviri | `#rkBox` i `#sec-upu` (karte planova), `#pzBox` |
| Simulator | visina etaže, krov, nagib, sljeme, podrum, garaža, AR i udaljenosti od međa po stranama |
| Procjena gradnje | temelji, prilaz, uređenje okoliša, ručna cijena po m² |

**Testovi:** `tests/run.js`, skupina `modTests`.

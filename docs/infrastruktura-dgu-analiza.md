# DGU SKI podaci za Grad Zagreb: izvještaj kvalitete (17. 10. 2026.)

Izvor: datoteke koje si preuzeo s `ski.dgu.hr` (INSPIRE GML, Grad Zagreb, oznaka 21), ukupno oko 1,2 GB:
- vodovod: `WaterPipe`, `UtilityLink`, `Appurtenance`;
- kanalizacija: `SewerPipe`, `UtilityLink`, `Appurtenance`;
- struja: `ElectricityPipe`, `UtilityLink`, `Appurtenance`.

Analiza: `tools/ski/*.py` (lxml, pyproj, shapely); rezultati u `tools/ski/analiza-rezultat.json`.

## 1. Što datoteke sadrže

| | Vodovod | Kanalizacija | Struja |
|---|---|---|---|
| Vodova (linija) | 108.615 | 36.243 | 185.394 veza, od toga 133.980 s opisom voda |
| Ukupna duljina | 2.978 km | 2.298 km | 9.356 km |
| Funkcionalni vodovi | 104.200 (2.787 km) | 35.240 (2.221 km) | niski napon 121.327 (**4.770 km**), srednji 12.534 (2.511 km), visoki 93 (410 km) |
| Napušteni ili izvan uporabe | 4.415 | 1.003 | oko 300 |
| Promjer, vrsta vode, vrsta otpadne vode | **uskraćeno** ("Withheld") | **uskraćeno** | napon je naveden |
| Objekti na mreži | 113.194 (zasuni, okna, 25.677 hidranata…) | 70.447 (65.430 okana, slivnici…) | 236.222 (rasvjetna mjesta, stupovi, 3.126 razvodnih ormarića, 2.747 trafostanica…) |
| Obuhvat (1 km kvadrati) | 521 km² | 361 km² | 499 km² (niski napon) |

Karta obuhvata: `docs/infrastruktura-dgu-obuhvat.png`. Kanalizacija pokriva manje područje, što je očekivano, jer rubni dijelovi grada često nemaju kanalizaciju.

**Ulični vodovi postoje u sve tri mreže.** Struja ima izričito niskonaponske vodove (0,4 kV), a vodovod i kanalizacija gustu uličnu mrežu: prosječni vod je oko 27 m, uz zasune, hidrante i okna.

**Datum:** feed navodi 19. 7. 2024., ali u podacima o struji ima zapisa s datumom valjanosti 2025. i 2026. Datoteke su dakle novije od datuma u feedu, a točan datum stanja nije naveden.

## 2. Koordinate i točnost položaja

- **Sustav:** EPSG:3035 (ETRS89/LAEA), s redoslijedom osi **sjever, istok**. Pogrešan redoslijed osi stavlja Zagreb u Atlantik (provjereno). Pretvorba u WGS84 ide preko pyproja uz službeni redoslijed osi.
- **Obuhvat nakon pretvorbe:** geografska širina 45,61–45,97, dužina 15,77–16,24, što točno odgovara granicama Grada Zagreba.
- **Unutarnja usklađenost** (objekti s vlastitim koordinatama prema svom vodu):

  | Objekti | Medijan | 90 % | 99 % |
  |---|---|---|---|
  | hidranti i zasuni → vodovod | 0,00 m | 0,00 m | 0,00 m |
  | okna → kanalizacija | 0,00 m | 0,30 m | 3,8 m |
  | ormarići i trafostanice → struja | 1,3 m | 5,0 m | — |
- **Neovisna provjera s gradskim GUP slojem:** postojeći dalekovodi 110 kV iz GUP-a od DGU visokonaponskih vodova udaljeni su 0,2–8 m na 5 točaka. To je unutar točnosti karte plana, pa je položaj potvrđen.
- GUP sloj magistralnog vodovoda (PJR) razlikuje se oko 200 m. Taj sloj sadrži planirane cjevovode, pa nije mjerilo.
- **Nije provjereno:** stvarna potpunost na terenu, jer upravitelji dostavljaju "dio podataka". To treba provjeriti na česticama koje poznaješ.

## 3. Ograničenja važna za prikaz

1. **Vodovod i kanalizacija nemaju promjer ni vrstu**, pa se ne zna je li najbliži vod magistralni, ulični ili kućni priključak. Prikazuje se samo "evidentirani vod".
2. **Niski napon struje** može uključivati i kabele javne rasvjete; podaci ih ne razlikuju (atribut je samo napon). Prikaz zato mora reći "niskonaponski vod" i da priključak potvrđuje HEP ODS.
3. **Plin nije u ovim datotekama** (DGU ga ne objavljuje za preuzimanje). Ostaje "Podaci nisu dostupni".
4. Napušteni i neaktivni vodovi se isključuju.
5. Potpunost nije zajamčena. "Nema voda u krugu od X m" nije dokaz da mreže nema.

## 4. Prijedlog integracije (čeka tvoje odobrenje)

- **Priprema (jednom, skriptom u `tools/ski/`):** samo funkcionalni vodovi, za struju samo niski napon. Pretvorba u WGS84 uz pojednostavljenje do 0,3 m i podjela na kvadrate od 1 km.
- **Veličina:** vodovod 6,0 MB (1,5 MB komprimirano), kanalizacija 2,3 MB (0,6 MB), struja 10,2 MB (2,4 MB). Najveći pojedinačni kvadrat ima oko 52 kB komprimirano. Aplikacija učita samo 1–4 kvadrata oko čestice. Datoteke idu uz aplikaciju na GitHub Pages, bez novog hostinga i bez ovisnosti o DGU servisu.
- **Izračun:** postojeća `minDistM()` od **granice** čestice (testirano: 39,95 m za vod 40 m od ruba), u krugu od 500 m.
- **Prikaz:**
  - `VODOVOD — najbliži evidentirani vod: X m`
  - `KANALIZACIJA — najbliži evidentirani vod: X m`
  - `STRUJA — najbliži evidentirani niskonaponski vod: X m`
  - `PLIN — Podaci nisu dostupni`
  - pod tim: "Izvor: DGU, katastar infrastrukture (preuzeto 17. 10. 2026.). Evidencija može biti nepotpuna; mogućnost i trošak priključenja potvrđuju ViO, Odvodnja i HEP ODS."
- **Kad vod prolazi česticom:** "vod prolazi česticom (0 m)", s napomenom o mogućem ograničenju gradnje iznad voda.
- **Bez podataka** (kvadrat se ne učita, izvan obuhvata): "Podaci nisu dostupni".
- **Isti podaci idu u:** analizu rizika, kartu (sloj "Vodovi DGU", isključen dok ga ne uključiš), AI kontekst (`getInfrastructure`) i offline način (kvadrati već učitanih čestica).

## 5. Odluke koje trebam od tebe

1. **Integrirati prema prijedlogu?** Repozitorij se time povećava za oko 18 MB, a na mobitel se preuzima samo ono što zatreba.
2. **Kad u krugu od 500 m nema voda**, što prikazati?
   - **(A)** "Nije evidentiran vod u krugu od 500 m (evidencija može biti nepotpuna)";
   - **(B)** "Podaci nisu dostupni".
3. **Licenca:** DGU navodi otvorenu dozvolu, uz obvezu navođenja izvora. Navođenje sam predvidio u prikazu.
4. **Provjera na terenu:** 2–3 čestice za koje znaš gdje su priključci, npr. Liševo. Nakon integracije usporedit ćemo prikazane udaljenosti sa stvarnim stanjem.

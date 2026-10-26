# Čitač v2.5: struktura dokumenta, kontekst i novi oblici (razvoj nakon slijepog testa)

Grana: `eksperiment-citac-v2.5`, iz `eksperiment-citac-v2.4`, sa spojenom granom slijepog testa Novog Vinodolskog.
- Ništa nije spojeno u `main` i nije otvoren PR. Produkcijska pravila nisu dirana.
- Zamrznute v1, v2.1, v2.2 i v2.3, sve oznake, odluke suca i izvještaji nisu mijenjani. Provjerava se prije i poslije svakog mjerenja.
- **Novi Vinodolski je od ove verzije razvojni skup.** Njegov rezultat ovdje nije dokaz generalizacije.
- **Pravno potvrđenih pravila: 0.**

## 1. Redoslijed rada (kako je traženo)
1. Najprije struktura dokumenta, bez novih gramatičkih oblika. Izmjereno koliko je članaka i pravila postalo dostupno.
2. Tek onda novi oblici odredbi.
3. Na kraju ponovno mjerenje svih dosadašnjih razvojnih planova istim pravilima usporedbe.

## 2. Struktura dokumenta (točke 1, 2, 3 i 7 zadatka)
| Promjena | Što radi |
|---|---|
| Priprema teksta iste duljine | »•« → »-«; točka u kraticama `ul.`, `čl.`, `st.`, `br.`, `vis.`, `tzv.`, `npr.` ne prekida rečenicu. Svaki citat se istim položajem vraća u izvorni oblik, pa citati ostaju doslovni. |
| Vrsta iz cijele uvodne rečenice | Vrsta se traži kao objekt »izgradnji / grade se / smještaj …« bilo gdje u rečenici, i kad zona (K11, K21) stoji ispred. »X i Y građevina« daje obje vrste. Usputni spomen se ne uzima. |
| Kontekst uvoda stavka | Zona (»planskom oznakom (K1)«, »oznakom K21«, »namjene – poslovne (K)«), nova gradnja samo kad je izričita (odluka suca v1.2/2), »Iznimno, …« stavak (uvjet i IZNIMKA) prenose se na svako pravilo stavka. »Površine iz stavka (1)« preuzimaju zone stavka 1. |
| Alineje i podblokovi | Alineje s velikim slovom iza crtice; numerirani naslovi »1.2. Uređenje građevne čestice:« postaju blok. |
| Zaštita KONTEKST_IZGUBLJEN | Ako pravilo nema vrstu, novu gradnju ili zonu koju uvod propisuje, ide na PREGLED. |
| Zaštita KONTEKST_NADREDJENE_ALINEJE | Pravilo iz podalineje (iza alineje koja završava dvotočkom, npr. »Iznimno, … K24 … prema slijedećim općim uvjetima:«) dobiva uvod, zonu i IZNIMKA te ide na PREGLED. |
| Zaštita VRSTA_IZ_UVODA_V25 | Kad je vrsta pravila nađena samo novim putem v2.5 za dio članka bez vlastitih pravila, pravilo ide na PREGLED. Uvedeno jer je u UPU 1 Krk (čl. 35., 36., 40.–44., bez reference) inače 21 pravilo prešlo s PREGLED na PRIJEDLOG bez mogućnosti provjere. |

**Dostupnost nakon same strukture** (v2.3 → v2.5):

| Plan | Članci s pravilima | Članci odbijeni zbog nepoznate vrste | Izdvojeni kandidati |
|---|---|---|---|
| Novi Vinodolski | 2 → 10 | 163 → 148 | 4 → 70 |
| PPUG Krk | 10 → 10 | 138 → 136 | 181 → 234 (od toga +53 iz v2.4) |
| UPU 1 Krk | 76 → 76 | 30 → 23 | 1115 → 1690 (sve iz v2.4) |
| UPU 2 Kornić | 12 → 12 | 87 → 87 | 120 → 120 |

U Krku i Korniću pravila su sadržajem ista kao u v2.4 (test). Status može samo ostati ili prijeći na PREGLED, nikad obrnuto (test na cijelom UPU 1). U UPU 2 se pravilima koja su već na pregledu može samo dodati razlog KONTEKST_IZGUBLJEN.

## 3. Novi oblici odredbi (točke 4, 5 i 6)
| Oblik | Primjer | Zapis | Status |
|---|---|---|---|
| »ne može biti manja od« + iznimka | »… manja od 600 m², iznimno za benzinske stanice 500 m²« | ≥ 600 OSNOVNO; ≥ 500 IZNIMKA, uvjet »za benzinske stanice« | PREGLED (vrsta iz iznimke) |
| »do N nadzemne etaže« | »do četiri (4) nadzemne etaže uz uvjet da …« | ≤ 4, UVJETNO, uvjet doslovno; riječ i broj u zagradi moraju se slagati | PRIJEDLOG |
| broj etaža »… te jedna (1) podzemna« | | podzemne zasebno | PREGLED (ETAZE_PODZEMNE) |
| »moguća je izgradnja 2 podzemne etaže« | | ≤ 2 | PREGLED (tumačenje) |
| regulacija po ulici | »… ul. Antuna Mataije iznosi 10 metara, odnosno 4 metra od ostalih ulica …«; popis »iznosi: - 10 m od …, - 4 m od …« | dva UVJETNO pravila, kategorija u uvjetu (odluka suca v1.2/1) | PRIJEDLOG |
| udaljenost ovisna o visini | »5,0 m za građevine visine do 10,0 m, odnosno najmanje 6,0 m za više« | dvije grane uvjetnog izraza (`formula.grane`), **nikad konačan broj** | uvijek PREGLED (OVISI_O_VISINI) |
| pomoćne u alineji | »uz građevine osnovne namjene … pomoćne … najviše kao dvoetažne …, visine 4,0 m« | dopuštenje, etaže, tlocrt, visina; udaljenosti »udaljene 4,0 m« bez »najmanje« s operatorom »=« | PREGLED |
| ograde, podzidi, kaskade | visina ograde, punog dijela, podzida, kaskade, odmak kaskada | jedinica kako piše (cm/m); »zabranjuje se … viših od N« → ≤ N | PREGLED (KATEGORIJA_NEVALIDIRANA) |
| zelenilo | »najmanje 30 % građevne čestice ugostiteljsko-turističke namjene« | ≥ 30 %, vrsta iz teksta | PREGLED |
| krov | »kosa nagiba između 18o i 25o«, »18o-25o«, udio ravnog krova, pokrov | nagib kao interval | nagib/oblik PRIJEDLOG; udio ravnog krova PREGLED |
| krovne kućice, podzemne etaže | »pojedina kućica … najviše 6 m²«, »100 % izgrađenost« | | PREGLED |

Nove kategorije ostaju na pregledu dok ih sudac ne provjeri. Nijedno pravilo nije prihvaćeno samo radi pokrivenosti.

## 4. Mjerenje na sva tri razvojna plana (`oznake/v1/mjeri_v25.py`, `mjerenje_v25.json`)
Pravila usporedbe su ista za sve verzije: mjeri_v24 (ocijeni_v1_2, odluke v1.1 i v1.2, granularnost v2.4). Dodaci su u `mapiranje_v25.json`:
- **nazivi** novih šifri;
- **istoznačnica** »poslovna+ugostiteljsko_turisticka« = »poslovna i ugostiteljsko-turistička građevina«;
- **pravilo JEDINICA_BROJA_ETAZA**: zamrznuta usporedba broj bez jedinice zapisuje kao »koeficijent«.

| Plan | Verzija | Prepoznati članci | Kandidati | Točno prihvaćena | Pogrešna prihvaćanja | Pregled | Propuštena |
|---|---|---|---|---|---|---|---|
| **Krk** (PPUG + UPU 1, ref. v1.2, 268 oznaka) | v2.3 | 86 | 1296 | 77 | 0 | 54 | 167 |
| | v2.4 | 86 | 1924 | 108 | 1 | 80 | 119 |
| | **v2.5** | 86 | 1924 | **108** | **1** | 80 | 119 |
| **Kornić** (UPU 2, čl. 38.–40., 99 oznaka) | v2.3 / v2.4 / **v2.5** | 12 | 120 | 92 | **0** | 7 (dvosmisleno, odgovara oznaci) | 0 |
| **Novi Vinodolski** (čl. 19., 20., 23., 24., 151 oznaka) | v2.3 | 2 | 4 | 0 | 1 | 2 | 151 |
| | v2.4 | 2 | 4 | 0 | 1 | 2 | 151 |
| | **v2.5** | 10 | 70 | **13** | **0** | 43 | 114 |

Pregled = pravilno na pregled + nepotrebno na pregled + pregled bez oznake.
- Krk v2.5: 30 + 11 + 39. Jedina pogreška je otprije poznata (»jednoetažna« prema 1, nedosljednost reference).
- NV v2.5: 9 + 15 + 19. Preciznost prihvaćenih je 1,000, a pokrivenost JASNIH oznaka 12,6 %.

**Novi Vinodolski po članku** (točno / pogrešno / pregled / propušteno):
- 19: 0 / 0 / 14 / 56
- 20: 4 / 0 / 15 / 24
- 23: 4 / 0 / 4 / 13
- 24: 5 / 0 / 10 / 21

**Novi Vinodolski po kategoriji (v2.5).** Pregled je zbroj pregleda s oznakom i bez nje.

| Kategorija (šifra) | Točno prihvaćeno | Na pregledu | Napomena |
|---|---|---|---|
| kig | 3 | 0 | |
| regulacija po ulici (`regulacija`) | 6 | 2 | na pregledu: pomoćne u čl. 20. |
| broj etaža (`etazeMax`) | 4 | 4 | na pregledu: podzemne (3) i pomoćne (1) |
| udaljenost od granice čestice | 0 | 7 | 4 ovisne o visini, 2 pomoćne (»=«), 1 frozen GRANICA_CESTICE |
| oblik krova / nagib / pokrov / udio ravnog krova | 0 | 2 / 2 / 1 / 1 | čl. 19. VRSTA_IZ_UVODA_V25; čl. 24. podalineja K24 |
| ograde (visina, puni dio) | 0 | 4 | jedinica cm prema oznaci u m, predmet »ograda« |
| podzid, kaskade, odmak kaskada | 0 | 3 | |
| zelenilo | 0 | 2 | |
| najmanja površina čestice | 0 | 2 | |
| krovne kućice, podzemne etaže (izgrađenost / površina) | 0 | 2 + 2 | |
| pomoćne: dopuštenje, tlocrt | 0 | 2 | |
| kis, visina građevine | 0 | 3 + 4 | razlozi zamrznute v2.2 (KIS_BEZ_OZNAKE, točka mjerenja) |

**Koliko rezultat ovisi o pravilima usporedbe v2.5.** Isti izlaz v2.5 usporeden strogo (bez dodataka iz `mapiranje_v25.json`) daje 9 točno i 4 pogrešno.
- Sve 4 »pogreške« su broj etaža s točnom vrijednošću, operatorom i uvjetom. Razlika je samo naziv/jedinica zapisa.
- Načinom iz slijepog testa v2.3 (`usporedi_oznake`, `U.mapa()`) također ispada 9 točno i 4 pogrešno.
- Oba načina su zapisana u `slijepi_v25.py` prije uvida u treći plan i oba će se izvijestiti.

## 5. Što ostaje otvoreno
- **Ograde** se ne sparuju s oznakama: tekst kaže »150 cm«, a oznaka »1,5 m«, uz vrstu »ograda«. Sudac treba odlučiti o jedinici i predmetu.
- **»Udaljene 4,0 m« bez »najmanje«**: čitač bilježi »=« (doslovno), a označivač »≥«. Treba odluka suca.
- **Propušteno 114 na NV**, od toga 80 »drugo:« parametara: pristup, priključci, parkiranje, oblikovanje, dopuštenost gradnje (11). Nisu rađeni.
- **Novi putevi vrste (VRSTA_IZ_UVODA_V25)** i podalineje ostaju na pregledu dok se ne provjere.

## 6. Zamrzavanje i sljedeći korak
- v2.5 je zamrznuta u `ZAMRZNUTO_v2_5.json`: 34 datoteke koda, 6 mapiranja, razvojne reference, upute v1.2, SHA zamrznutih v2.2 i v2.3.
- Postupak slijepog testa za treći, neviđeni plan je `slijepi_v25.py`: odaberi → tekst → jedan neovisni označivač po uputama v1.2 → zaseban commit oznaka → usporedi (strogo i pravila_v25).
- Za test je potreban izvor trećeg plana.

## 7. Testovi i kontrolne sume
**Testovi:** 182 / 182 (test_citac 22, test_strukturiraj 36, test_v2 41, test_v22 29, test_v23 15, test_v24 14, test_v25 25).

| Datoteka | SHA-256 |
|---|---|
| gramatika_v25.py | `a044762c0b07c0e058d340c73f4388d82b3b79135f2179233bcdeed6a8ccd73e` |
| strukturiraj_v25.py | `492c6806f56187f1af89a3ea8aaaf66adbcf6a6e42f07d4241ec3299edfa79ca` |
| test_v25.py | `d495a4821dff50178af9c4be5e83398069fb014b636c8ea9d18a23f9c27135db` |
| slijepi_v25.py | `3350fbc9db16a3ef1ad9a3bf310a2143d5e51281771195b910f5bf948b767d93` |
| oznake/v1/mjeri_v25.py | `55f57cc6eeb0fe594e3f79677ec89607780c617db2ae269729806842616ddf8e` |
| oznake/v1/mapiranje_v25.json | `aef7ad445862fc9c53b1fffeefcd335862141d294e475ac3bd37dc12329d2291` |
| oznake/v1/mjerenje_v25.json | `802ed23d1ad081e67e43737b1f671b69e4427adec62c53dcaac7fa65887724e4` |
| slijepo/novi_vinodolski/usporedba_v25_razvojna.json | `decc71defffbc15d91c400339da72d73033e793feb8996cdbd12d678a9e28cab` |
| ZAMRZNUTO_v2_5.json | `7c884e382e847104e734168e884957ac19409656c9ed04d98596d88041a9ea82` |
| ZAMRZNUTO_v2_3.json | `e27c8c32a4118ff7b9c4a891889e6091e185f408e53a2987c8507a237aacd25e` |

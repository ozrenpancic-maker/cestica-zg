# Čitač v2.2: završni izvještaj (faze A–D, priprema faze E)

Grane:
- `eksperiment-citac-v2`: v2.1 i slijepi test v2.1;
- `eksperiment-citac-v2.2`: v2.2.

Ništa nije spojeno u `main` i nije otvoren PR. Aplikacija, GIS, zoniranje, produkcijska pravila, referentne oznake i zamrznute verzije (v1, v2.1) nisu mijenjani. Na objema granama su samo dodane datoteke.

**Pravno potvrđenih pravila: 0.**

## 1. Slijepi test v2.1: UPU 1 – Krk, čl. 14. i 24. (faza A)
- **Oznake:** 101 zapis, SHA-256 `91d187e4…`, commit `2b7b607`. Svi zapisi imaju citat, članak, stavak, parametar, vrijednost, uvjet i status, a svi citati su doslovni.
- **Usporedba:** zamrznuta v2.1 (`6e798ae`), rezultat u `8ef462d`.

| | čl. 14. | čl. 24. |
|---|---|---|
| točno prihvaćeno | 0 | 0 |
| pogrešno prihvaćeno | 0 | 0 |
| pravilno na pregled | 0 | 0 |
| nepotrebno na pregled | 0 | 0 |
| propušteno | 36 | 65 |
| dodatni prijedlozi bez oznake | 0 | 0 |

Oba članka su odbijena (`SKUPINA_NEPOZNATA`). Nije bilo ni izdvajanja ni razumijevanja pravila. Analiza je u `slijepo/ppug_krk/slijepi_v2/IZVJESTAJ_slijepi_v2_1.md`.

## 2. Šest dodatnih pravila v2.1 (faza B)
- **Dodatak oznaka:** 26 zapisa, SHA-256 `7e64ed66…`, commit `2b69a97`. Postojeći skup 22./23. nije mijenjan.
- **Rezultat:**
  - 2 točno (oblik krovišta, čl. 22. i 23.);
  - 4 sadržajno ista uz drukčiji raspored polja ili drukčiju vrstu pravila (dopuštenje gradnje; vrsta kosog krovišta UVJETNO ili ALTERNATIVA);
  - 0 pogrešno.
- **Nalaz:** dopuštenje gradnje ovisi o alinejama koje su za pregled. U v2.2 je zato PREGLED (`OVISI_O_UVJETIMA_ZA_PREGLED`).

Detalji su u `oznake/dodatak_22_23/IZVJESTAJ_dodatak.md`.

## 3. Dizajn v2.2 (faza C)
Vidi `DIZAJN_v2_2.md`: analiza uzroka, šest prioriteta i popis razloga zbog kojih se pravilo ne prihvaća automatski.

## 4. v1, v2.1 i v2.2 na razvojnim skupovima (faza D)
Svi skupovi su razvojni: poznati su razvoju v2.2. **Ovo nije dokaz generalizacije.**

| Skup | v1 | v2.1 | v2.2 (točno / pogrešno / pregled / propušteno) |
|---|---|---|---|
| PPUG čl. 22./23. (55) | 46 / 0 / 9 / 0 | 44 / 0 / 11 / 0 | 44 / 0 / 11 / 0 |
| PPUG čl. 25. (22) | 0 / 0 / 0 / 22 | 14 / 0 / 8 / 0 | 13 / 0 / 9 / 0 (dopuštenje gradnje → pregled) |
| PPUG čl. 33. (12) | 0 / 0 / 0 / 12 | 0 / 0 / 12 / 0 | 0 / 0 / 12 / 0 |
| UPU 1 čl. 14. (36) | – | 0 / 0 / 0 / 36 | 6 (+1 granularnost) / 0 / 8 / 22 |
| UPU 1 čl. 24. (65) | – | 0 / 0 / 0 / 65 | 9 (+1 granularnost) / 0 / 5 / 51 |
| dodatak st. 2. 22./23. (26) | – | 2 + 4 sadržajno / 0 | 10 (+4 granularnost) / 0 / 12 / 6 |
| PPUG čl. 20., 38., 39., 50. (84, neovisno) | – | – | 7 / 0 / 5 / 77 |
| UPU 2 čl. 38.–40. (vlastite oznake) | 92 / 0 / 7 / 0 | 92 / 0 / 7 / 0 | 92 / 0 / 7 / 0 |

**Preciznost prihvaćenih pravila (v2.2):**
- uz pravila granularnosti: 1,0 na svim skupovima;
- strogo: UPU 1 čl. 14. 0,857, čl. 24. 0,9, dodatak 0,714.

Pravila granularnosti su tri, opisana u `oznake/mapiranje_v22.json`. Svako je nastalo zato što se dva neovisna označivača razilaze oko iste rečenice, i takvi zapisi se broje zasebno.

**Razlikovanje izdvajanja od razumijevanja (UPU 1, v2.2):**

| | izdvojeno (prihvaćeno ili pregled s oznakom) | automatski prihvaćeno | nepotrebno na pregled |
|---|---|---|---|
| čl. 14. | 38,9 % | 19,4 % | 6 |
| čl. 24. | 21,5 % | 15,4 % | 4 |

»Nepotrebno na pregled« su pravila s istom vrijednošću kao oznaka JASAN. Većinom je uzrok visina bez točke mjerenja, granica čestice ili formula s h. Pregled se ne smatra točnim rezultatom.

**Dodatni prijedlozi bez oznake:**
- v2.2 je u neoznačenim člancima PPUG-a prihvatila 7 pravila (čl. 20., 38., 39., 50.). Neovisni označivač ih je naknadno provjerio (oznake `4955259…`, commit `af56a34`): **7 točno, 0 pogrešno.**
- U UPU-u 2 gramatika v2.2 ne predlaže ništa izvan čl. 38.–40.

**Pogreške nađene i ispravljene tijekom razvoja v2.2, prije zamrzavanja:**
1. Kontekst iz usputnog spomena vrste u uvodu (čl. 52., 72., 75.) → `skupina_strogo()`.
2. Čl. 24. UPU 1: pomoćne građevine dobile su vrstu »hotel«, jer članak bez stavaka nije išao putem blokova → put blokova je obvezan.
3. Rečenica iza »iznimno, unutar … cjelina« u istoj alineji bila je prihvaćena kao osnovno pravilo (čl. 20., 50.) → nasljeđivanje uvjeta iznimne alineje.
4. Alineja »- Iznimno …« (veliko slovo) nije bila odvojena → razdvajanje i uz veliko slovo.
5. Članak s ponovljenim brojevima stavaka (čl. 56.) → sva pravila su PREGLED.

**Regresije:**
- 128 / 128 testova: v1 58, v2.1 41, v2.2 29;
- determinizam potvrđen (dva prolaza, isti SHA-256);
- integritet `ZAMRZNUTO_v1.json` i `ZAMRZNUTO_v2.json` provjerava se prije i nakon svake usporedbe.

## 5. Zamrzavanje v2.2 i faza E
- **Zamrzavanje:** `ZAMRZNUTO_v2_2.json`, SHA-256 `5c8b834528cbb55833b2ea034817c0f7433e38af48e9d56dc5603569d807b733`, commit `107826e`.
- **Faza E nije provedena.** Nedostaje izvor drugog, neviđenog prostornog plana:
  - mreža radnog okruženja ne dopušta pristup sn.pgz.hr;
  - povezano računalo nije bilo dostupno.
- Postupak je spreman i zamrznut (`slijepi_v22.py`): strojni odabir članaka po unaprijed zadanom kriteriju → tekst → neovisne oznake → zamrzavanje oznaka → usporedba.

## 6. Kontrolne sume (v2.2)
| Datoteka | SHA-256 |
|---|---|
| gramatika_v22.py | `07d42d39557227833eee09726f53932987875a8e2c549dfa49b7eb2639fef179` |
| strukturiraj_v22.py | `ec96ee923ff8b3c47377a4579d6676815260e15a8d1e9986139bb4ff252f7d4b` |
| morfologija_hr.py | `a4aea29cdf2c6e41a1f03dc14b860eca0bd93f179a8cfc01ca5e67d72c3adbfd` |
| vrste_gradevina.py | `9c5abe3525b6fc813abd1cfe913b2e01b85350344b23ebeece4105da91e0c89f` |
| usporedi_v22.py | `4f34464bb4c61189d09b28bc2e74973f352f1fa99739a83808df6f7d76af3140` |
| slijepi_v22.py | `c13f55b496d20a697fcb7981948f6e8a9619a43f4ae42d2d36812894a1f4e2cb` |
| test_v22.py | `9f23da3c913530e35b5ba49e03263428ab5c44b1ba6acf36d84fa35ec734890e` |
| oznake/mapiranje_v22.json | `da6a6601447349fbad00e3176cb2652a752824352164790a466a707d73bf8b0e` |
| izlaz/usporedba_v2_2.json | `262f835ecd250f35b380ce0586ae9a553afd507cb1d41c8583b0de56bf88d6d7` |


## 7. Preostale slabosti
- **Pokrivenost na UPU-u 1 je niska:** 15–19 % automatski prihvaćeno, 22–39 % izdvojeno.
  - Opisne odredbe (namjena, oblikovanje, priključci) nisu u gramatici.
  - Nisu ni rekonstrukcijski uvjeti tipa »ne povećava se ako je veće od« ni eliptične vrijednosti (»… podrum 1,5, od čega je 0,5 …«).
- **Morfologija je heuristika:** nastavci bez glasovnih promjena, bez glagola, bez morfološkog rječnika.
- **Nagib uz »krovište može biti ravno ili koso« i dio krovišta s pokrovom »kojeg predviđa usvojena tehnologija«** su uvijek PREGLED.
- **Mapiranje za UPU 1 (razvojni skup) napisano je nakon uvida u oznake.** Za slijepi test nazivi su zatvoreni unaprijed.
- **Označivači su isti model kao razvojni**, u zasebnom kontekstu. Ljudska provjera nije provedena.
- **Postotak pravila za pregled je visok** (33–100 %, ovisno o skupu). To je namjerno, radi pravne sigurnosti.

## 8. Preporuka
**v2.2 još nije spremna za sljedeću fazu.**
- Na razvojnim skupovima nema nijednog pogrešno automatski prihvaćenog pravila, a pokrivenost na UPU-u 1 porasla je s 0 na 15–19 %.
- Primarno mjerilo uspjeha (pokrivenost na neviđenom planu bez novih pogrešno prihvaćenih pravila) još nije izmjereno.

Preporučeni sljedeći korak je faza E na neviđenom planu, s neizmijenjenom v2.2. Potreban je izvor: HTML ili PDF odluke drugog prostornog plana iz Službenih novina PGŽ, priložen u razgovor.

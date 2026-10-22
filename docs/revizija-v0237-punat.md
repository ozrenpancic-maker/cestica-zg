# Neovisna revizija v0.23.7: Punat, SN PGŽ 30/18 (id 37834), članci 1–15

Datum: 22. 10. 2026. Revizor: Claude (neovisni ocjenjivač). Produkcijski kod nije mijenjan.
Referentni skup je izrađen iz izvora, **bez gledanja izlaza parsera po operacijama**. Ne prilagođava se v0.23.7.

Referentni skup: `tests/zlatni/punat-independent-gold.json`, zaključan sha256 `66356138…de512e` nad `clanci` i `operacije`.

## 0. Izvor: priložena datoteka nije ispravna

| Datoteka | sha256 | Stanje |
|---|---|---|
| izvor koji je obradio v0.23.7 (`source_sha256`) | `f4c7b751…c5e572` | windows-1250, ispravan; **identičan mojoj arhivskoj kopiji iz v0.18.7** |
| priloženi `37834.html` | `c459a664…0fef9a5c` | UTF-8 s gubitkom: **2969 znakova zamijenjeno s U+FFFD** (č 758, š 664, đ 614, ž 320, ć 279, … te » 64 i « 56) |

Priložena kopija je očito nastala pogrešnim dekodiranjem i ponovnim spremanjem. Na njoj ne bi radili ni „Članak", ni navodnici »«, ni pretraživanje teksta. Označavao sam na ispravnom izvoru.
**Pravilo R1 (dolje)** treba ovakvu datoteku odbiti, a ne obraditi.

## 1. Sažetak

| | Referentni skup | v0.23.7 |
|---|---|---|
| Članaka s naredbom izmjene | **15 / 15** | — |
| Operacija | **17** (13 CONFIRMED, 4 REVIEW_REQUIRED) | 4 kandidata |
| Bez upozorenja | — | 2 kandidata (čl. 7 i 13) |

Po tipu: REPLACE_ARTICLE 7, REPLACE_WORDS 4, REPLACE_PARAGRAPH 2, ADD_PARAGRAPH 1, ADD_ALINEA 1, INSERT_AFTER 1, DELETE_ARTICLE 1.

**Na neviđenom dokumentu v0.23.7 bez upozorenja izdvaja najviše 2 od 17 operacija.** Nemam izlaz po operacijama, pa ne mogu potvrditi da su te 2 i točne.
Rezultat „19/19" u Baški postignut je uz ručno upisane brojeve i preslikavanja (vidi reviziju v0.23.3), pa ne govori o općoj točnosti.

## 2. Svih 15 članaka

Detalji (doslovni tekst naredbe, literali, hash novog teksta, blokovi izvora) su u JSON-u. Ovdje je pregled.

| Čl. odluke | Naredba (doslovno, skraćeno) | Cilj (PPUO Punat) | Op. | Status | v0.23.7 | Kategorija uzroka |
|---|---|---|---|---|---|---|
| 1 | „Članak 4. Prostornog plana … mijenja se i glasi:" | čl. 4 (cijeli) | 1 | CONFIRMED | EMPTY | B segmentacija |
| 2 | „Članak 5. mijenja se i glasi:" | čl. 5 | 1 | CONFIRMED (» bez «) | EMPTY | B |
| 3 | „Članak 6. mijenja se i glasi:" | čl. 6 | 1 | CONFIRMED (bez », kraj ') | EMPTY | B |
| 4 | „Članak 9. mijenja se i glasi:" | čl. 9 | 1 | CONFIRMED | NOT_UNIQUE | B |
| 5 | „U članku 10., stavak 4. riječi: 'člankom 66.' zamjenjuju se riječi: 'članku 77j.'" | čl. 10 st. 4 | 1 | CONFIRMED | NOT_UNIQUE | B, zatim C |
| 6 | „U članku 12., stavak 1. riječi: 'člankom 66.' zamjenjuju se riječi: 'članku 77j.'" | čl. 12 st. 1 | 1 | CONFIRMED | NOT_UNIQUE | B, zatim C |
| 7 | „U članku 13. iza stavka 3. dodaje se novi stavak 4. koji glasi:" | čl. 13 novi st. 4 | 1 | CONFIRMED | kandidat (1) | — |
| 8 | „Članak 17. mijenja se i glasi:" | čl. 17 | 1 | CONFIRMED | EMPTY | B |
| 9 | „Članak 18. mijenja se i glasi:" | čl. 18 | 1 | CONFIRMED | NOT_UNIQUE | B |
| 10 | „U članku 19. iza riječi: '1b' dodaje se riječ: '3b'." | čl. 19 | 1 | **REVIEW_REQUIRED** (nije rečeno što stoji između 1b i 3b) | NO_ACTIONS | C |
| 11 | „U članku 20. stavak 4. mijenja se i glasi:" | čl. 20 st. 4 | 1 | CONFIRMED | UNCLAUSED_PREFIX | D (navodnici) |
| 12 | „Članak 22. briše se." | čl. 22 (brisanje) | 1 | CONFIRMED | EMPTY | B, zatim C |
| 13 | „U članku 23. stavak 1. mijenja se i glasi:" | čl. 23 st. 1 | 1 | CONFIRMED | kandidat (1) | — |
| 14 | „Članak 23 b. mijenja se i glasi:" | čl. 23b | 1 | CONFIRMED | REVIEW (1) | C |
| 15 | „U članku 23c., stavku 1. točki 4. dodaje se nova alineja …" + „U točki 6., alineji 1., …" + „U točki 8., alineji 3., …" | čl. 23c st. 1 t. 4/6/8 | **3** | **REVIEW_REQUIRED** (položaj alineje; naslijeđeni st. 1) | REVIEW (1 od 3) | C, D |

**Kategorije:**
- **A** izdvajanje HTML-a;
- **B** segmentacija članaka odluke;
- **C** prepoznavanje naredbi (glagoli, navodnici, oznake članaka);
- **D** nasljeđivanje konteksta i svjesnost navodnika.

**Raspodjela:** B je uzrok u 9 od 15 članaka (1–6, 8, 9, 12). Iza B, C ostaje u čl. 5, 6 i 12. C je jedini uzrok u čl. 10 i 14, D jedini u čl. 11, a u čl. 15 su C i D. A ovdje ne uzrokuje izravan neuspjeh, ali je uzrok B.

## 3. Ciljana istraživanja

**3.1 `AMENDING_ARTICLE_NOT_UNIQUE` (čl. 4, 5, 6, 9)**
- `get_article` traži `\bČlanak\s+(\d+)\s*\.` (s `re.I`) u **spljoštenom** tekstu (`BeautifulSoup.get_text(' ')`).
- „Članak 4." postoji kao naslov čl. 4 odluke, ali i na početku tijela čl. 1 („Članak 4. Prostornog plana …").
- Isto vrijedi za 5 (tijelo čl. 2), 6 (čl. 3) i 9 (čl. 4).
- **Uzrok: B.** Naslov članka odluke se prepoznaje po uzorku teksta, a ne po strukturi bloka.

**3.2 Pet praznih odjeljaka (čl. 1, 2, 3, 8, 12)**
- Ista funkcija uzima kraj odjeljka kao „sljedeći `Članak N.`". Tijelo tih pet članaka počinje upravo s „Članak N." ciljnog plana, pa odjeljak završava prije nego počne.
- **Uzrok: B.**
- Na cijeloj odluci **33 od 90 članaka** počinje s „Članak N." ciljnog plana, pa problem nije rubni.

**3.3 `NO_ACTIONS_IN_CLAUSE_None` (čl. 10)**
- Naredba: „iza riječi: '1b' dodaje se riječ: '3b'".
- Popis `ACTION` ne sadrži „dodaje se riječ:", a `QUOTE` prepoznaje samo »…«.
- **Uzrok: C.**
- Na cijeloj odluci **29 od 90 članaka** koristi '…'.
- I kad se prepozna, naredba ne kaže koji razdjelnik stoji između „1b" i „3b". Zato REVIEW_REQUIRED, a ne pretpostavka.

**3.4 `UNCLAUSED_DIRECTIVE_PREFIX` (čl. 11)**
- `CLAUSE = \((\d+)\)\s+(?=U\s|Dodaje\s)` pogađa „(4) U građevinskom području …", a to je **početak navedenog novog teksta** unutar »…«.
- Ispred toga ostaje „U članku 20. stavak 4. mijenja se i glasi: »", pa se članak odbacuje.
- **Uzrok: D.** Parser ne razlikuje sintaksu naredbe od citiranog teksta.

**3.5 Čl. 14 i 15: adrese i sidra**
- **Čl. 14:**
  - cilj je u nominativu („Članak 23 b."), a `TARGET` traži samo „u članku N.";
  - oznaka ima razmak i slovo;
  - zamjenjuje se cijeli članak, pa „stavak nije pronađen" nije greška nego očekivano stanje.
- **Čl. 15:**
  - navodnici '…', pa nema starih ni novih literala;
  - „23c." ne prolazi `\d+\s*\.`;
  - „, stavku 1." bez „u" ne prolazi `CONTEXT`;
  - „dodaje se nova alineja koja glasi" i „zamjenjuje se riječi:" nisu na popisu;
  - druga i treća rečenica nemaju članak, a treba ih naslijediti iz prve.

  Izdvojena je samo 1 od 3 operacije.

## 4. Raspodjela grešaka po vrsti

| Vrsta | Primjeri | Mjesto u kodu |
|---|---|---|
| **A Izdvajanje HTML-a** | spljošteni tekst gubi granice blokova i centriranje naslova; oznake nabrajanja `&#339;` (œ) iz Worda; nema provjere gubitka kodiranja (priložena kopija) | `decode_html` (`get_text(' ')`) |
| **B Segmentacija** | naslov članka prepoznat i u rečenici „Članak N. mijenja se…"; kraj odjeljka = bilo koji „Članak N." | `get_article`, `ARTICLE` |
| **C Prepoznavanje naredbi** | zatvoren popis glagola; samo »«; oznake članaka sa slovom; nominativ „Članak N. mijenja se / briše se" | `ACTION`, `QUOTE`, `TARGET` |
| **D Kontekst i navodnici** | uzorak točke odluke unutar citata; nema nasljeđivanja članka i stavka između rečenica; cijeli članak se odbija zbog jedne greške | `numbered_clauses`, `derive_context`, `split_directives` |

Mjereno na svih 90 članaka odluke, glagoli su raznolikiji nego što pokriva v0.23.7: „mijenja se i glasi" 51, „briše se" 12, „brišu se" 4, „zamjenjuju se riječima" 9, „zamjenjuje se riječju" 3, „zamjenjuju se riječi" 2, „zamjenjuje se riječi" 2, „dodaje se nova alineja koja glasi" 2, „postaje" 2, „dodaje se riječ" 1, „dodaje se novi naslov koji glasi" 1, „zamjenjuje se brojem" 1 i drugi.

## 5. Univerzalna pravila za v0.23.8 (bez uvjeta za Punat ili Bašku)

1. **R1 Kodiranje i porijeklo.** Dekodirati prema deklariranom charsetu, strogo. Datoteku s `U+FFFD` ili hashom koji nije u registru odbiti (`ENCODING_LOSS` / `PROVENANCE_UNVERIFIED`).
2. **R2 Model blokova.** Parsirati DOM u niz blokova (`p`, `h*`, `li`, `td`) s atributima (poravnanje, podebljanje, uvlaka). Inline oznake se uklanjaju bez razmaka, `<br>` postaje prijelom retka. Spljošteni tekst služi samo za pretraživanje, nikad za segmentaciju.
3. **R3 Naslov članka odluke.** Naslov je **samostalan blok** čiji je cijeli tekst `Članak \d+[a-z]?\.`. Brojevi moraju ići uzastopno 1…N, inače `SEGMENTATION_REVIEW`. „Članak N." na početku duže rečenice je **adresa cilja**, nikad naslov.
4. **R4 Navodnici.** Prepoznati parove » «, „ ", " ", ' ' i "…" te ugniježđene navodnike (čl. 1). Kod neuparenih navodnika (čl. 2, 3) novi tekst traje do kraja članka odluke ili do sljedeće rečenice naredbe, uz `QUOTE_MISMATCH`. **Unutar citiranog teksta ne traži se sintaksa naredbe** (čl. 11).
5. **R5 Gramatika naredbe umjesto popisa izraza.** Naredba je *adresa* + *objekt* + *glagol* + *operand*:
   - objekt: riječ, riječi, broj, rečenica, tekst, znak, zarez, alineja, stavak, točka, podstavak, naslov, članak;
   - glagol po lemi: mijenjati … i glasi, zamjenjivati, dodavati, brisati, postajati;
   - operand: citat ili „koji/koja/koje glasi:" + citat ili sljedeći blokovi.

   Padež objekta (riječi/riječima/riječju) nije uvjet. Rečenica koja počinje adresom, a nema prepoznat glagol, daje `UNCLASSIFIED_DIRECTIVE`; ne preskače se.
6. **R6 Gramatika adrese.**
   - Članak `\d+\s?[a-z]?`, normaliziran („23 b" → „23b").
   - Oblici „Članak N." (subjekt), „U članku N.", „članka N.".
   - Jedinice stavak, točka, alineja, podalineja, podstavak, u bilo kojem padežu, s razdjelnicima „,", „u" ili bez njih.
7. **R7 Nasljeđivanje konteksta.**
   - Plan se nasljeđuje iz naslova odluke i punog citata u čl. 1, osim ako se drugi plan izričito navede.
   - Unutar jednog članka odluke rečenica bez članka nasljeđuje zadnji izričiti članak.
   - Rečenica koja počinje nižom razinom („U točki 6.") nasljeđuje višu razinu, ali uz `CONTEXT_INHERITED` → REVIEW, dok polazni tekst ne pokaže da je jedinica jednoznačna.
8. **R8 Položaj.** „Iza X dodaje se" je izričit. „Dodaje se nova alineja/rečenica" bez položaja daje `POSITION_UNSPECIFIED` + zapisanu konvenciju (kraj jedinice).
9. **R9 Interpunkcija rezultata.** Umetanje bez navedenog razdjelnika daje `RESULT_SEPARATOR_UNSPECIFIED` (čl. 10).
10. **R10 Oznake nabrajanja.** Simbolne oznake iz Worda (œ, §, ·, , o) postaju token oznake nabrajanja u usporedbenom sloju, a original ostaje u prikaznom sloju.
11. **R11 Greška po naredbi, ne po članku.** Jedna neprepoznata rečenica ne smije odbaciti cijeli članak; izvoz je djelomičan, sa zastavicom po operaciji.
12. **R12 Provjera pokrivenosti.** Svaka rečenica članka odluke mora biti razvrstana: naredba, nastavak naredbe, citirani tekst ili nenaredbeni tekst. Nerazvrstana daje `UNCOVERED_TEXT`. To je opća mjera protiv tihog gubitka operacija (čl. 15: 1 od 3).

## 6. Regresijski testovi za v0.23.8

1. Odbijanje priložene oštećene kopije (`U+FFFD` > 0) i prihvaćanje izvora `f4c7b751…`.
2. Segmentacija 37834 daje 90 članaka, brojeve 1…90 i nijedan prazan članak. Čl. 1, 2, 3, 8 i 12 nisu prazni.
3. Usporedba s `punat-independent-gold.json` za čl. 1–15, po operaciji:
   - tip, ciljni članak, stavak, točka i alineja;
   - stari i novi literal ili sha256 novog teksta;
   - status.

   Mjeri se **preciznost, odziv i kritične greške**, ne broj kandidata.
4. Čl. 11 daje točno 1 operaciju; „(4) U …" unutar citata nije oznaka točke.
5. Čl. 15 daje 3 operacije. Druga i treća imaju članak 23c naslijeđen, a stavak 1 označen `CONTEXT_INHERITED`.
6. Čl. 10 i čl. 15 op. 1 moraju imati status REVIEW, a ne potvrđen položaj ili rezultat.
7. Isti testovi 1–2 i R12 na Baškoj (34945, 41160) **bez ijednog upisanog ID-a, broja operacija ili preslikavanja stavaka**. Rezultat mora ostati 19 operacija.
8. Slijepi test na odluci koju razvoj nije vidio (§7).

## 7. Zaključavanje i neovisnost

- `punat-independent-gold.json` je zaključan hashom i ne mijenja se. Svaka buduća ispravka ide u novu verziju (v2) s obrazloženjem.
- **Ograničenje:** razvoj ispravlja parser upravo na ovom dokumentu, a ovaj izvještaj opisuje sve slučajeve. Zato je skup **regresijski**, a ne slijepi.
- Za stvarnu neovisnu ocjenu predlažem drugu odluku o izmjenama (druga općina, druga godina). Njezine oznake ostaju kod mene, a razvoj dobiva samo preciznost, odziv i kritične greške.
- Polazni tekst PPUO Punat (08/09, 30/10, 33/10 pročišćeni tekst, 14/15) nije u korpusu, pa jedinstvenost sidara i položaje nisam mogao provjeriti. To je sljedeći korak prije bilo kakve simulacije (replaya) za Punat.

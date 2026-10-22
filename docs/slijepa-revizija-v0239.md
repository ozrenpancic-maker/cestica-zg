# Slijepa revizija v0.23.9: odluka 35169 (Malinska-Dubašnica, SN PGŽ 5/17)

Datum: 22. 10. 2026. Ocjenjivač: Claude. Oznake i produkcijski kod nisu mijenjani.

## Preporuka: **FAIL**

Parser pronalazi naredbe dobro: preciznost otkrivanja je 100 %, a odziv 84 %. Ali **14 kritičnih pogrešaka** znači da bi primjena ovih kandidata dala pogrešan tekst plana. Pet puta bi obrisala cijeli stavak ili članak umjesto nekoliko riječi, a šest puta bi promijenila članak umjesto naslova.
Potpuno točnih operacija je 11 od 43 (25,6 %) uz stroge literale, ili 19 od 43 (44,2 %) kad se zanemare razmaci.
Za tekst s pravnim učinkom prag za PASS je **0 kritičnih pogrešaka** i upozorenje na svakom nejasnom slučaju. Taj prag nije postignut.

## 0. Integritet

| Provjera | Rezultat |
|---|---|
| Hash oznaka s grane `slijepi-testovi` | `e0c381af…6da42` = obveza iz commita 1de3e39 (zaključano prije razvoja v0.23.9) |
| Grana s oznakama | jedan commit (d1576ff), bez kasnijih izmjena |
| Hash izvora u izlazu i u paketu | `0fe98f0a…3dc0e` = isporučeni izvor |
| Segmentacija | 26 članaka odluke, bez zastavica; citirani „Članak 32." ispravno **nije** uzet kao članak odluke |

## 1. Metrike

**Pravila bodovanja:**
- **Uparivanje:** svaki kandidat se uparuje s jednom zlatnom operacijom iz iste naredbe istog članka odluke. Tablica uparivanja je u `ocijeni.py` na grani `slijepi-testovi`.
- **Vrsta:** usporedba po obitelji (zamjena jedinice, zamjena riječi, brisanje riječi, brisanje jedinice, dodavanje jedinice, umetanje, prenumeriranje).
- **Adresa:** članak + vrsta cilja (članak ili naslov) + stavak/točka/podtočka/alineja. Kod dodavanja se prihvaća i broj sidra („iza stavka N"), jer izlaz nema posebno polje za položaj.
- **Literali:** strogo = sažete bjeline i ujednačeni navodnici, kako je zaključano; bez razmaka = dodatno zanemareni svi razmaci.

| Mjera | Rezultat |
|---|---|
| Zlatnih operacija / kandidata | 43 / 36 |
| Otkrivanje: TP / FP / FN | 36 / **0** / **7** |
| Preciznost otkrivanja | 36/36 = **100 %** |
| Odziv otkrivanja | 36/43 = **83,7 %** |
| Točnost vrste (na uparenima) | 29/36 = 80,6 % |
| Točnost adrese (na uparenima) | 29/36 = 80,6 % |
| Stari literal, strogo / bez razmaka | 10/17 = 58,8 % / 10/17 = 58,8 % |
| Novi tekst, strogo / bez razmaka | 9/26 = 34,6 % / 18/26 = 69,2 % |
| **Potpuno točne operacije (strogo)** | preciznost 11/36 = **30,6 %**, odziv 11/43 = **25,6 %** |
| Potpuno točne (bez razmaka) | preciznost 19/36 = 52,8 %, odziv 19/43 = 44,2 % |
| **Kritične pogreške** (unaprijed zadana pravila) | **14** |
| Dodatna ozbiljna pogreška izvan tih pravila | 1 (čl. 26, §2.5) |

Razlika između strogih rezultata i rezultata bez razmaka u novom tekstu (9 → 18) dolazi gotovo u cijelosti od **razmaka koje parser umeće na mjestu oznaka `<sub>`/`<sup>`**: „(T1 1 )", „Z1 1", „R M", „K S1".

## 2. Pogreške po članku odluke

### 2.1 Kritične (14)

| Čl. odluke | Očekivano | Dobiveno | Opći uzrok |
|---|---|---|---|
| 3 | brisanje riječi „i površina mješovite namjene (M6)" u **naslovu** ispred čl. 14 | `DELETE_UNIT` članka 14, bez literala | (a) nema pojma „naslov ispred članka"; (b) „briše se" uvijek znači brisanje jedinice |
| 4 | brisanje riječi u čl. 14 **st. 1** | `DELETE_UNIT` cijelog st. 1 | (b) |
| 4 | brisanje riječi u čl. 14 **st. 2** | `DELETE_UNIT` cijelog st. 2 | (b) |
| 5 | zamjena **naslova** ispred čl. 19 navedenim tekstom | `REPLACE_UNIT` čl. 19 **bez novog teksta** | (a); (c) kod ove vrste ne preuzima citat iz iste rečenice |
| 7 | „lokalnog" → „županijskog" u **naslovu** ispred čl. 24 | ista zamjena u **čl. 24** | (a): adresa „ispred članka N" svodi se na članak N |
| 9 | iza „…smještajem (KS1, KS2 i KS3), te unutar" riječ „površine" → „površina" | stari = cijelo sidro, novi = „površine" | (d) dodjela literala po redu citata (1. = stari, 2. = novi) ne razlikuje sidro, cilj i zamjenu |
| 9 | brisanje riječi u čl. 28 **st. 2** | `DELETE_UNIT` cijelog st. 2 | (b) |
| 11 | zamjena u **naslovu** ispred čl. 31 | zamjena u čl. 31 | (a) |
| 14 | zamjena broja „2.1.2." → „2.1.3." u naslovu; **nejasno je koji je to članak 32**, pa se očekuje REVIEW | zamjena u čl. 32, **bez upozorenja** | (a); (e) nema prepoznavanja dvoznačnosti brojeva nakon umetanja/prenumeriranja u istoj odluci |
| 16 | zamjena u **naslovu** ispred dosadašnjeg čl. 33 | zamjena u čl. 33 | (a) |
| 18 | brisanje **naslova** ispred dosadašnjeg čl. 34 **i** članka 34 (2 operacije) | samo brisanje članka 34 | (f) složeni objekt „Naslov … i … članak … brišu se" nije rastavljen |
| 19 | brisanje riječi u čl. 35 | `DELETE_UNIT` cijelog **čl. 35** | (b) |
| 20 | brisanje **naslova** ispred čl. 41 i članka 41 | samo brisanje članka 41 | (f) |
| 24 | iza „TS PLAN-2" veznik „i" → zarez | stari = „TS PLAN-2", novi = „i" (zamjenio bi „TS PLAN-2" s „i") | (d) |

### 2.2 Propuštene operacije (7)

| Čl. | Očekivano | Opći uzrok |
|---|---|---|
| 1 | zamjena čl. 2, st. 4, t. 1, **podtočke b** (8 blokova novog teksta) | (g) glagol s greškom u izvoru „mijenja se glasi" (bez „i") ne odgovara zatvorenom obrascu. **To je 9 nepokrivenih blokova** |
| 9 | „hotel (T1)" → „hotela (T11 i T12)" (druga radnja u istoj rečenici, „te se riječ …") | (h) rečenica se dijeli samo na „. U članku…"; radnje spojene s „te"/zarezom ostaju jedna |
| 13 | dodavanje **naslova** iza čl. 31 | (f) |
| 18 | brisanje naslova | (f), kritično |
| 20 | brisanje naslova | (f), kritično |
| 24 | iza „TS PLAN-3" dodaju se riječi „i TS PLAN-4" | (h); izvor ima i grešku „dodaju riječi" (bez „se") |
| 24 | iza rečenice „Trafostanice će se graditi …" dodaje se nova rečenica | (h) |

### 2.3 Pogrešna vrsta ili nedostajući sadržaj, bez kritične posljedice

| Čl. | Očekivano | Dobiveno | Opći uzrok |
|---|---|---|---|
| 13 | novi **članak 32** s cijelim tekstom (blokovi „Članak 32." … „7. mjere zaštite okoliša …") | `INSERT_AFTER` čl. 31, **bez novog teksta** | (c) kod vrste `INSERT_AFTER` ne preuzimaju se blokovi koji slijede; nema vrste „dodaje se naslov i novi članak koji glase" |
| 22 | novi st. 10 u čl. 94 s tekstom | `RENUMBER` st. 10 → „10", bez teksta i bez upozorenja | (i) „koji postaje stavak 9." (relativna rečenica) proglašen glavnim glagolom; „postaje" ima prednost pred „dodaje se" |
| 22 | stavci 9. i 10. postaju 8. i 9. | `RENUMBER` bez cilja, **s upozorenjem** | (j) obrazac „stavci od 9. i 10." nije prepoznat. Ispravno označeno kao REVIEW |
| 22 | iza „… javne rasvjete i slično)" dodaje se **zarez** i riječ | novi tekst bez zareza | (k) „dodaje se zarez i riječ" — zarez opisan riječima nije dio literala |

### 2.4 Literali novog teksta

Kod 9 operacija novi tekst se razlikuje od zlatnog samo po umetnutim razmacima: čl. 1 (t. 3), 2, 6 (×2), 10, 11, 12, 21 i 25. Kod čl. 11 je uz to i adresa pogrešna (§2.1).
**Uzrok (l):** `extract_blocks` koristi `p.get_text(' ')`, iako komentar u kodu kaže da sub/sup ne smiju unositi razmak.

### 2.5 Ozbiljna pogreška izvan unaprijed zadanih pravila

**Čl. 26:** novi tekst st. 3 čl. 112 sadrži i **završne odredbe odluke** („III. ZAVRŠNE ODREDBE", „Glava III.", „Glava IV.", „Ova Odluka stupa na snagu…", klasu, urudžbeni broj i potpis).
**Uzrok (m):** kraj zadnjeg članka odluke određuje se samo sljedećim „Članak N.". Naslovi dijelova („III. ZAVRŠNE ODREDBE"), „Glava" i potpis nisu granice.
Primjena bi zamijenila stavak pogrešnim tekstom. Nije brojano kao kritično jer pravila zaključana prije testa ne pokrivaju ovu vrstu, ali je jednako opasno.

## 3. Devet neklasificiranih blokova

Svih 9 je u **čl. 1 odluke** (indeksi 0–8 u izlazu): naredba „U članku 2. Odluke … stavku 4. točki 1. podtočka b mijenja se glasi:" i njezinih 8 blokova novog teksta („»b) druge namjene" … „hoteli (T11 i T12)«").
- **Uzrok:** `VERB` traži „mijenja\s+se\s+i\s+glasi". Izvor ima pravopisnu grešku bez „i", pa blok nije prepoznat kao naredba, a blokovi koji slijede nemaju „trenutnu naredbu".
- **Opći problem:** nepokrivenost se vidi samo u sažetku (`uncovered_blocks: 9`). Ne postaje operacija s `REVIEW_REQUIRED`, pa se ta izmjena tiho gubi. Pravilo R12 iz revizije v0.23.7 traži upravo to.

## 4. Što v0.23.9 radi dobro

- Nema lažno pozitivnih: svaki kandidat odgovara stvarnoj naredbi.
- Segmentacija je ispravna (26 članaka) i citirani „Članak 32." ne lomi strukturu.
- Kodiranje se provjerava (`ENCODING_LOSS`).
- Prenumeriranje članaka (čl. 15, 17), brisanje alineja i stavaka (čl. 4, 22), zamjene cijelih stavaka i članaka te većina zamjena riječi s ispravnom adresom su točni.
- Jedini stvarno neriješen slučaj prenumeriranja stavaka označen je kao REVIEW.

## 5. Opći uzroci i što ispraviti (bez posebnih uvjeta za ovu odluku)

| Oznaka | Uzrok | Ispravak |
|---|---|---|
| a | nema cilja „naslov" | adresa ima vrstu cilja: `HEADING_BEFORE(n)` / `HEADING_AFTER(n)` / članak / stavak … „naslov ispred članka N" nikad se ne svodi na članak N |
| b | „briše se" = brisanje jedinice | ako rečenica sadrži „riječ/riječi" + citat, vrsta je `DELETE_WORDS` sa starim literalom; brisanje jedinice samo kad je objekt jedinica (stavak, alineja, članak, naslov) |
| c | novi tekst se uzima samo za neke vrste | jedno pravilo za sve vrste: operand je citat iz iste rečenice ili, iza „koji/koja/koje glasi/glase:", blokovi koji slijede |
| d | literali po redu citata | uloge citata iz gramatike: „iza riječi »A«" = sidro; „riječ »B« zamjenjuje se riječju »C«" = stari/novi; „veznik »i« zamjenjuje se zarezom" = novi opisan riječju |
| e | dvoznačnost brojeva unutar iste odluke | voditi stanje numeracije kroz odluku (umetnuti i dosadašnji članci). Ako isti broj označava dvije jedinice, a nema „dosadašnji/novi", daje REVIEW |
| f | složeni objekt s „i" | „Naslov … i … članak … brišu se" i „dodaje se naslov i novi članak … koji glase" rastaviti na jednu operaciju po jedinici |
| g | zatvoren obrazac glagola | tolerirati izostavljene pomoćne riječi („mijenja se glasi", „dodaju riječi") uz zastavicu `SOURCE_TYPO`; nepokrivena rečenica s adresom daje operaciju REVIEW, a ne tihi gubitak |
| h | jedna rečenica = jedna radnja | rastaviti po glagolima unutar rečenice („te se", „, iza riječi … dodaju se", „te se iza rečenice … dodaje"), uz nasljeđivanje adrese |
| i | prednost „postaje" | glavni glagol se određuje izvan relativnih rečenica („koji postaje …") |
| j | obrazac raspona | „stavci (od) 9. i 10. postaju (stavci) 8. i 9." |
| k | interpunkcija opisana riječju | „dodaje se zarez i riječ" daje novi literal s „, " na početku |
| l | razmaci na mjestu sub/sup | inline oznake se uklanjaju bez razmaka (usporedbeni sloj) |
| m | kraj zadnjeg članka | granica je i naslov dijela odluke, „Glava", „stupa na snagu", klasa ili potpis; tekst iza toga nikad nije operand |

## 6. Sljedeći korak

1. Ispraviti a–m kao opća pravila. Regresije: Punat 37834 (zaključani skup) i Baška (34945, 41160) **bez upisanih ID-eva**.
2. **Odluka 35169 je sada potrošena kao slijepi test**, jer ovaj izvještaj otkriva njezine oznake. Može postati regresijski test.
3. Za sljedeću slijepu ocjenu pripremam novu, neviđenu odluku s istim postupkom: najprije zaključavanje hashom, zatim isporuka samo identiteta i HTML-a.

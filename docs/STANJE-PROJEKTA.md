# Čestica HR: stanje projekta

Stanje 22. 10. 2026. Pišem kao dosadašnji programer aplikacije i neovisni ocjenjivač Data Managera.
Dokument je namijenjen svakom tko nastavlja rad (Ozren, ChatGPT, Claude u novom razgovoru), da ništa ne ovisi o pamćenju razgovora.

## 1. Najvažnije u jednoj rečenici

**Aplikacija već za Krk radi „čestica → planovi → namjena → karta plana → uvjeti gradnje". Data Manager ne treba to graditi ispočetka, nego puniti i provjeravati pravila koja aplikacija koristi.**

ChatGPT je 22. 10. predložio „fazu B" (čestica → planovi preko WMS-a). To već postoji u aplikaciji, preko boljeg izvora od WMS-a (vektorski ArcGIS REST, vidi §3).

## 2. Aplikacija

- **Repozitorij:** `ozrenpancic-maker/cestica-zg`.
- **Objava:** GitHub Pages (`main`) na https://ozrenpancic-maker.github.io/cestica-zg/.
- **Probna stranica za mobitel:** repozitorij `cestica-zg-proba`.

**Grane**

| Grana | Sadržaj |
|---|---|
| `main` | produkcija; zadnji merge PR #38 (21. 10.) |
| `razvoj` | rad u tijeku; **neobjavljeno:** analiza za cijelu PGŽ (čestica uživo iz DGU-a) i pravila gradnje za Punat (PPUO čl. 24.–29.); revizije Data Managera u `docs/` |
| `stabilna-2026-10-17` | sigurnosna kopija |
| `slijepi-testovi` | **zaključane oznake slijepih testova: ne otvarati i ne dijeliti razvoju** |

Pravilo: u `main` ništa bez provjere i Ozrenova odobrenja.

**Što radi**

| Područje | Stanje | Dokument |
|---|---|---|
| Grad Zagreb | puna analiza: čestica, GUP namjena i urbana pravila, PPGZ, rizici, infrastruktura (DGU SKI), troškovi, 3D | `README.md` |
| Otok Krk (pilot) | čestica (DGU), važeći planovi i planovi u izradi, namjena i izgrađenost, karta UPU/DPU izrezana oko čestice, infrastruktura, nagib; uvjeti gradnje za Grad Krk (PPUG + UPU 1, 2, 5), Malinsku, Bašku, djelomično Vrbnik; Punat na `razvoj` | `docs/krk-pilot.md`, `docs/upu-karte.md`, `docs/pgz-servisi.md` |
| Cijela Hrvatska | osnovni pregled: čestica iz DGU-a, ZK, okoliš, teren, 3D (PR #38) | — |
| Android | PWA, instalira se s mreže | `docs/android-pwa.md` |
| AI asistent | kod postoji, **isključen** (`FEATURES.ai=false`) | `docs/ai-*.md` |
| Pouzdanost | svaki podatak ima razinu (A/B/C), izvor, obuhvat i datum | `docs/pouzdanost.md` |

**Testna čestica 735/76 k.o. Kornić danas:**
- županijski sloj daje UPU 2 Kornić (SN 19/16, važeći), PPUG Krk i PPŽ;
- aplikacija izreže kartu 1 UPU-a 2 oko čestice;
- pravila za zone M11/M2 (čl. 38.–40.) provjerena su 18. 10. prema Word tekstu plana.

Zonu unutar UPU-a aplikacija **ne očitava automatski** (karta je raster), pa korisnik bira zonu.

## 3. Izvori podataka i uvjeti

| Izvor | Što daje | Uvjeti | Napomena |
|---|---|---|---|
| PGŽ `gisportal.pgz.hr` REST, `STANJE/IZRADA_PP` | planovi na točki: vrsta, status (VAŽEĆI / U IZRADI / VAN SNAGE), SN broj, poveznice, datum stupanja na snagu | GEOPORTAL PGŽ: prijenos uz navođenje izvora; bez jamstva | **vektorski, upit po točki i po poligonu**; ovo je „faza B" |
| PGŽ `STANJE/NAMJENA_POVRSINA_NOVO` | namjena iz PPUO/G, oznaka zone, izgrađenost, izvor (SN) | isto | udjeli zona po poligonu čestice |
| PGŽ `PP_RASTERI` | rasterske karte UPU/DPU | isto | zona u UPU-u samo vizualno |
| Zavod PGŽ (zavod.pgz.hr, VidiPlan) | tekst i karte planova (PDF) | isto | pomoćni izvor teksta |
| Službene novine PGŽ (sn.pgz.hr) | pravni izvor odluka | javno | registar 171 provjerene objave (Data Manager) |
| DGU (katastar, SKI) | čestice, infrastruktura | prema DGU | ortofoto DGU nije pod uvjetima PGŽ |
| ISPU (ispu.mgipu.hr) | popis objava i revizija po planu | pozadinski API bez dopuštenja **ne** koristiti | za PGŽ nepotpun (nije prikazao UPU 2 Kornić) |

U aplikaciji se uvijek navode izvor i datum. Pravni dokaz je objava u Službenim novinama.

## 4. Data Manager (Windows/Python, razvija ChatGPT)

Uloga: baza prostornih planova i pravila s dokazima. Claude je neovisni ocjenjivač.

**Što je pouzdano dovršeno**
- Registar objava SN PGŽ za korpus od 177 dokumenata: 171 s vlastitim SN brojem i datumom. Podaci su neovisno provjereni na stranicama akata; oznaku VERIFIED (potvrdu popisom izdanja) nisam mogao provjeriti, jer popisi izdanja nisu dostavljeni.
- Klasifikator ukidanja: neviđeni uzorak 7 od 7, bez postupovnih lažnih pogodaka (malen uzorak).

**Što nije**
- Generacije planova i lanci izmjena: 0 potvrđenih.
- Parser naredbi izmjena: slijepi test v0.23.9 je **FAIL**. Preciznost otkrivanja 100 %, ali samo 11 od 43 operacija potpuno točno i 14 kritičnih pogrešaka (`docs/slijepa-revizija-v0239.md`).

**Dogovoreni novi smjer (22. 10.)**
- Faza A: parser samo sigurnosno popraviti i ne širiti ga.
- Zatim katalog planova, provjera čestice i potpuni primjer Kornić, s tri razine pouzdanosti: kandidat, ručno provjereno, pravno potvrđeno.

**Moja preporuka uz to:**
- B2 (čestica → planovi, namjena) ne graditi ponovno, nego koristiti postojeće upite iz `docs/pgz-servisi.md` / `tools/pgz/pgz_upit.py`.
- Data Manager neka radi ono što aplikaciji nedostaje (§5).

**Zaključani referentni skupovi** (ne mijenjati; nove verzije samo kao v2):

| Skup | Datoteka | Status |
|---|---|---|
| identitet planova Krk | `tests/zlatni/krk-plan-identity-v1.json` | zaključan |
| generacije Baška / Malinska / Vrbnik | `tests/zlatni/generacije-baska-malinska-vrbnik-v1.json` | zaključan; **djelomično izložen** (25645 korišten u reviziji v0.23.3), zamijeniti u v2 |
| Punat 30/18, čl. 1–15 | `tests/zlatni/punat-independent-gold.json` | regresijski (razvoj ga je vidio) |
| slijepi test 35169 | grana `slijepi-testovi`, obveza `tests/zlatni/slijepi-obveze.json` | potrošen nakon ocjene v0.23.9, sada regresijski |

## 5. Što stvarno nedostaje

1. **Zona unutar UPU-a.** Za Kornić je zona samo na rasterskoj karti. Treba pitati Zavod PGŽ postoje li vektorski slojevi namjene za UPU-ove; dotad zona ostaje ručni izbor.
2. **Tekstovi planova koji nisu obrađeni:**
   - Punat (UPU 3);
   - Omišalj i Dobrinj (nema pročišćenog teksta ili je samo PDF);
   - Vrbnik u verziji iz 2024.;
   - UPU-ovi u Malinskoj, Baškoj i Vrbniku.

   Ovdje Data Manager najviše pomaže: tekst, članci i parametri s dokazom.
3. **Ažurnost.** Ima li u SN izmjena koje županijski sloj još nema (npr. PPUG Krk nakon 2020.)? To je posao za parser izmjena kao kontrolu.
4. **Rupe u registru objava:** PPUG Krk 41/09, 28/11, 23/15, 18/19; UPU 2 Kornić 19/16 (id 34138).
5. **Pravna potvrda** važenja i datuma stupanja na snagu: nijedan plan još nije pravno potvrđen.

## 6. Pravila rada

- Ništa izmišljeno; nepoznato se prikazuje kao „Podaci nisu dostupni".
- Numerička pravila samo uz konkretan članak i provjerenu verziju plana; AI ne nagađa pravne uvjete.
- Bez upisanih ID-eva i posebnih uvjeta za pojedini dokument u kodu Data Managera.
- Onaj tko gradi ne ocjenjuje vlastiti rad. Slijepi testovi se zaključavaju hashom prije razvoja i razvoj dobiva samo metrike.
- Bez plaćenih API-ja i tajni u repozitoriju; u `main` samo uz odobrenje.

## 7. Okruženje i ograničenja

- Claude u oblaku ne može otvarati sn.pgz.hr, gisportal.pgz.hr ni zavod.pgz.hr (mrežna ograničenja).
- Ako se razgovor poveže s Ozrenovim računalom, ili ako se radi u Claude Codeu lokalno, to postaje moguće.
- Data Manager radi na Ozrenovu Windows računalu.

## 8. Predloženi sljedeći koraci

1. Poslati ChatGPT-u §1, §4 i §5: faza B se ne gradi ispočetka; Data Manager preuzima postojeće upite i puni tekstove i pravila koja nedostaju.
2. Kornić kao prvi potpuni primjer u aplikaciji:
   - provjeriti rezultat za 735/76 prema SN 19/16;
   - zonu odabrati ručno, uz kartu;
   - Claude neovisno provjerava.
3. Upit Zavodu PGŽ (`zavod@pgz.hr`):
   - potvrda ponovne upotrebe u komercijalnoj aplikaciji;
   - postoje li vektorske zone namjene UPU-ova.
4. Odlučiti o objavi grane `razvoj` (PGŽ analiza, Punat) u `main` nakon pregleda.

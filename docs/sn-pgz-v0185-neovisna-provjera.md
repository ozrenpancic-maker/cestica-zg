# ČesticaHR v0.18.5 – neovisna provjera vlastitog broja SN, datuma objave i ciljnog akta

Status: priprema (21. 10. 2026.). Ne mijenja produkcijski kod Data Managera ni zaključane skupove
(`krk-plan-identity-v1.json`, `generacije-baska-malinska-vrbnik-v1.json`). Generacije se NE ocjenjuju.

Alati: `tools/sn-pgz/sn_identitet_provjera.py`, `tools/sn-pgz/test_sn_identitet.py` (51 test, 48 pokrenuto, 3 čekaju stvarni HTML),
`tests/zlatni/sn-portal-sidro-v1.json` (8 zapisa opaženih na portalu).

## 0. Što sam stvarno vidio (i što nisam)
- Portal sam dohvatio alatom WebFetch. Za `…?Link=odluke&id=28241` i `id=14783` **vratio je isti popis izdanja** (Punat/Vrbnik), a ne
  stranicu akta; zato ne znam kako izgleda zaglavlje same stranice akta ni kako se iz `id` dolazi do popisa. Rizik R1 za Data Manager.
- Iz popisa vidim: `Službene novine broj 33. Godina XXVIII. Petak, 2. listopada 2020.` → `Općina PUNAT` → `60.` + naslov + poveznica `id=41977`;
  uz neke akte posebna poveznica „PDF" s drugim `id` (npr. 41087 ↔ 31026). To je sažetak alata, ne sirovi HTML (status sidra:
  `OPAZENO_PREKO_SAZETKA_ALATA`). Parser je zato tolerantan i ima `opisi_strukturu` za prvi stvarni HTML.
- Iz korpusa (172 od 177 dokumenata) imam footer `default.asp?Link=odluke&izdanje=I&mjesto=M&odluka=O`. Nemaju ga 5 dokumenata:
  44780, 32580, 22418, 20600, 26150 (statusi PRONAĐENO_NEPROVJERENO / NEPROVJERENO).

**Neovisna potvrda značenja footera:** za 4 akta koji su i u korpusu i u popisu (41977, 41087, 37834, 20518) vrijedi
`odluka` = redni broj akta u broju (60, 5, 50, 44), `izdanje` = interni id broja (2159, 2129, 1075, 687), `mjesto` = šifra općine
(51521 = Punat; ostale u korpusu: 51500 Krk, 51511 Malinska-Dubašnica, 51513 Omišalj, 51514 Dobrinj, 51516 Vrbnik, 10007 Baška).
Trojka (izdanje, mjesto, odluka) je jedinstvena na svih 172 dokumenata (0 duplikata).

## 1. Što treba izdvojiti s portala
| Polje | Izvor na portalu | Napomena |
|---|---|---|
| `publication_id` | `id=N` u URL-u akta | identitet zapisa; nije SN broj |
| `izdanje_id`, `mjesto_id`, `redni_broj_u_izdanju` | footer akta (`izdanje`, `mjesto`, `odluka`) | ključ akta; mora se slagati s popisom |
| `sn_broj`, `sn_godina`, `sn_oznaka` („33/20") | zaglavlje popisa izdanja („broj 33 … 2020.") | **vlastiti broj SN**; nikad iz citata u tekstu |
| `godina_toma_rimski` | isto zaglavlje („XXVIII") | kontrola: 1993 + 28 − 1 = 2020 |
| `datum_izdanja` | isto zaglavlje | datum **objave**; nije datum akta ni stupanja na snagu |
| `naziv_akta` | naslov u popisu | uz njega i naslov iz teksta; razlike se bilježe |
| `izvor_zaglavlja`, `izvor_html_sha256` | meta | `PORTAL_ISSUE_LISTING` / `PORTAL_ACT_PAGE_HEADER`, hash spremljenog HTML-a |
| `dokaz_citat` | doslovni redak zaglavlja | za reviziju |

Tri različita datuma ne smiju se miješati: datum objave (portal), datum donošenja u tekstu („Krk, 13. kolovoza 2013."), datum
stupanja na snagu (iz odredbe o stupanju na snagu, računa se tek uz izričit članak). v0.18.5 treba samo prvi.

## 2. Dokaz da broj SN pripada dokumentu (a nije citiran)
Zapis je „PROVEN" samo ako vrijede **sve** stavke (provjerava `provjeri_registar` + `provjeri_akt_html`):
1. izvor je portalsko zaglavlje (R4); citat iz teksta se odbija;
2. footer akta = (izdanje, mjesto, odluka) zapisa (H2);
3. u spremljenom popisu izdanja `id` akta stoji pod zaglavljem broja N i pod istim mjestom, s istim rednim brojem (H3–H5);
4. `sn_oznaka` = broj/god. (R2), godina datuma = godina broja (R3), rimska godina odgovara (R3B);
5. isto izdanje → ista (broj, godina, datum); isti SN broj → jedno izdanje (R6); trojka i `id` jedinstveni (R5);
6. hash HTML-a prisutan i ponovljiv; PDF `id` nije zaseban akt (test `test_pdf_id_nije_akt`);
7. R7 (izdanje_id raste s datumom) je upozorenje, ne greška: ranije sam mjerio 1 inverziju veću od mjesec dana u 12 561 paru.
Bez 1–4: `sn_vlastiti_broj_unknown = true`. Nikad popunjavanje iz citata ili kronologije.

## 3. Više dokumenata citira isti broj SN (nalazi na korpusu, heuristika `citati`)
- Različitih SN PGŽ oznaka u citatima: 190; od toga 115 citira više od jednog dokumenta; najviše 34 dokumenta (01/08).
- 11 oznaka postoji i kao NN i kao SN citat (npr. 33/10, 16/04, 38/09) → glasilo mora biti dio ključa (`WRONG_GAZETTE`).
- Pre-1993 „Službene novine" (npr. 31/78, 6/83) su drugo glasilo (`SN_STARO`); 2-znamenkaste godine: ≥93 → 19xx, inače 20xx.
- Lanci „30/10, 36/10 – ispravak odluke, 16/11 i 10/16": ispravak se ne razrješava na izvorni akt (`CORRECTION_NOTICE`).
- Testovi: `TestCitati`, `TestRazrjesavanje` (31 citatelja istog SN daje isti cilj; isti broj u dva mjesta; dva akta u istom izdanju i mjestu).

## 4. Može li se po službenom broju jednoznačno razriješiti ciljni akt?
**Samo uvjetno – sam broj SN nije dovoljan.** U jednom broju je više akata i više općina.
- U korpusu: 119 različitih izdanja i 128 skupina (izdanje, mjesto). 99 skupina ima točno 1 dokument (99 dokumenata, 58 %);
  29 skupina ima 2–8 dokumenata (73 dokumenta, 42 %): za njih SN broj + općina ostaje dvosmislen (npr. izdanje 862/Baška: 8 akata).
- Dakle jednoznačno je samo ako: (a) gazeta je SN PGŽ, (b) broj/god. postoji u registru, (c) mjesto je poznato, (d) u skupini je točno
  jedan akt, ili citat sadrži redni broj/naslov koji sužava na jedan. Inače `AMBIGUOUS` / `NOT_IN_REGISTRY`.
- Većina citiranih brojeva vjerojatno nema cilj među 177 dokumenata; to se ne može procijeniti dok nema vlastitih SN brojeva.
- Razrješenje cilja nije dokaz generacije (L2 tek uz doslovan citat i jedinstven cilj).

## 5. Kriteriji neovisne ocjene izvoza v0.18.5
Ulaz koji tražim od Data Managera: `akti/<id>.html`, `popisi/*.html`, `sn_registar_v0185.json` (`{"records":[…]}` sa
poljima iz §1), `run_report.json`; pokretanje: `CESTICA_HTML_DIR=… python3 -m unittest tools/sn-pgz/test_sn_identitet.py`.

| # | Kriterij | Prag |
|---|---|---|
| K1 | Povrede FAIL u `provjeri_registar` | 0 |
| K2 | Zapisi s footerom koji se slažu s HTML-om (H1–H5) | 172/172 ili jasno popisani izuzeci |
| K3 | 5 dokumenata bez footera | `unknown`, nikad pogođeno |
| K4 | Sidro: 8 zapisa iz `sn-portal-sidro-v1.json` reproducirano (broj, god., datum, redni broj, mjesto) | 8/8 (4 provjerljiva i footerom) |
| K5 | Pokrivenost PROVEN vlastitih SN brojeva | izvještava se; nepotpunost dopuštena, popunjavanje iz citata nije |
| K6 | Razrješenje cilja: RESOLVED mora imati točnost | 100 % na mom uzorku (izrađujem iz isporučenih HTML-ova prije usporedbe; oznake zamrznute hashom) |
| K7 | AMBIGUOUS/NOT_IN_REGISTRY nikad auto-razriješeni; NN ≠ SN; ispravak ≠ izvorni akt | 0 povreda |
| K8 | Datum objave ≠ datum akta ≠ stupanje na snagu | polja odvojena |
| K9 | Nema upisanih ID-eva dokumenata u produkcijskom kodu; zaključani skupovi nepromijenjeni (sha256) | 0 / nepromijenjeni |
| K10 | Generacije: bez promjene (`UNDETERMINED`, 0 auto-spajanja); datumi objave smiju samo kao kandidatski signal | 0 potvrđenih |
| K11 | Zaključani skup generacija se ne dijeli | da |

## 6. Ograničenja
- Struktura popisa poznata je iz jednog sažetka; parser nije potvrđen na sirovom HTML-u (zato `opisi_strukturu` i 3 preskočena testa).
- Heuristika citata (glasilo, ispravak, lanci) ima pogrešaka; brojke u §3 su indikativne, ne zlatne.
- Ne znam kako doći do popisa izdanja za proizvoljan `id`; to mora riješiti Data Manager (arhiva/tražilica).

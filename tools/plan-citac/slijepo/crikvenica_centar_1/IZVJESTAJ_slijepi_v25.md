# Slijepi test zamrznute v2.5 – UPU Crikvenica centar I

- **Grana:** `slijepi-v2.5-treci-plan` (iz `eksperiment-citac-v2.5`). `main` i produkcijska pravila nisu dirani.
- **Pravno potvrđenih pravila: 0.** v2.6 nije pokrenuta.

## 1. Postupak i integritet
| Korak | Stanje |
|---|---|
| Izvor | Odredio sudac: SN PGŽ, Godina XVI. (2008.), br. 18, »Odluka o donošenju UPU Crikvenica centar I«. HTML SHA-256 `7f08f8da…c344b45` (`IZVOR.md`). |
| Prilagodnik formata | Odluka suca. Prijelom retka u HTML kodu → razmak. Zamrznut prije označavanja (`ZAMRZNUTO_v2_5_dodatak_prilagodnik.json`), izlaz `7588f0c7…7c83db13`. Provjereno: NV nepromijenjen; Krk – sva pravila ista, +6 novih na PREGLED. |
| Odabir članaka | Zamrznuti kriterij (isti kao v2.2/v2.3) → čl. 23., 24., 25., 26. |
| Oznake | Jedan neovisni označivač, samo tekst i upute v1.2, bez alata. 44 zapisa, svi citati doslovni. Zamrznute commitom `fa5cbbe` prije usporedbe, SHA-256 `5c086d34…f5478e87287`. |
| Integritet prije usporedbe | ZAMRZNUTO_v2_2, v2_3, v2_5 i dodatak prilagodnika: sve sume ispravne. |
| Usporedba | `slijepi_v25.py usporedi`, oba načina (strogo i pravila_v25) određena prije uvida u plan. |

## 2. Rezultat
| | Strogo | Pravila v2.5 (semantički) |
|---|---|---|
| oznaka (od toga JASAN) | 44 (25) | 44 (25) |
| prepoznati članci | 4 / 4 | 4 / 4 |
| izdvojeni kandidati | 7 | 7 |
| točno prihvaćeno | 0 | 0 |
| **pogrešno prihvaćeno** | **0** | **0** |
| pregled (sve s razlogom KONTEKST_IZGUBLJEN) | 7 | 7 |
| propušteno | 44 | 44 |

Oba načina daju isti rezultat. Dodatna pravila usporedbe v2.5 (nazivi, istoznačnice, jedinica broja etaža) ovdje ne mijenjaju ništa.

## 3. Obrazloženje svih 44 oznaka
### 3a. Čitač je izdvojio pravilo, ali se ne sparuje (7)
| Oznake | Što se slaže | Razlika | Je li kozmetička |
|---|---|---|---|
| kig, čl. 24., 25., 26. (Z020, Z028, Z039) | parametar, operator, vrijednost (0,5 / 0,5 / 1,0), jedinica | **vrsta građevine**: čitač je nije odredio; oznaka: građevina poslovne namjene / sadržaj komunalno-servisne namjene / hotel | **Ne** – mijenja vrstu građevine. Pravilno na PREGLED (KONTEKST_IZGUBLJEN). |
| kis, čl. 24., 25., 26. (Z021, Z029, Z040) | operator, vrijednost (1,5 / 1,5 / 3,5) | vrsta građevine (kao gore); parametar: čitač ne određuje nadzemni / ukupni kis (KIS_BEZ_OZNAKE), oznaka »uz podrum ili ukupni« uz TUMACENJE | **Ne** – vrsta građevine. Obje strane tu dvoznačnost kisa označavaju za pregled. |
| građevni pravac, čl. 23. (Z001) | parametar | vrijednost: čitač je zahvatio dio subjekta (»se grade unutar područja obuhvata …«); vrsta nije određena | **Ne** – vrijednost je pogrešno razgraničena. Na PREGLED. |

### 3b. Čitač nije izdvojio pravilo (37)
| Uzrok u čitaču | Oznake | Broj |
|---|---|---|
| Subjekt određen načinom gradnje (»Građevine koje će se graditi na slobodnostojeći način / kao dvojne moraju biti udaljene najmanje 4,0 m …, odnosno 3,0 m ukoliko …«) → PREDMET_NEPOZNAT | Z004, Z005, Z009, Z010 | 4 |
| Broj etaža »je 4, ali dozvoljene su najviše 2 nadzemne etaže« → VRIJEDNOST_NEPREPOZNATA; »najveći dopušteni broj nadzemnih etaža je 6« → PREDMET_NEPOZNAT | Z022, Z023, Z030, Z031, Z041 | 5 |
| »Visina … iznosi najviše 10,0 m, a ukupna visina … najviše 13,0 m« u jednoj rečenici → PREDMET_NEPOZNAT | Z024, Z025, Z032, Z033 | 4 |
| Broj s točkom tisućica »1.500 m 2« nije prepoznat kao broj | Z019 | 1 |
| Opisne odredbe bez broja: način gradnje, prislanjanje, zabrana niza, rekonstrukcija, dopuštenost, građevni pravac | Z002, Z003, Z006, Z007, Z008, Z011, Z012, Z013, Z014, Z017, Z026, Z038 | 12 |
| Upućivanja i opisi (DPU, natječaj, kartografski prikaz, smjernice tijela zaštite) | Z042, Z043 i dio »drugo:« ispod | 2 |
| Parametri izvan zatvorenog popisa (»drugo:«: smještaj, parkirališna mjesta, oblik i veličina čestice, detaljni uvjeti, kategorija i kapacitet hotela, način provedbe) | Z015, Z016, Z018, Z027, Z034, Z035, Z036, Z037, Z044 | 9 |

Od 19 JASNIH oznaka iz zatvorenog popisa:
- čitač je **vrijednost** pogodio u 3 slučaja (kig), ali bez vrste građevine;
- ostalih 16 nije izdvojio.

## 4. Zašto vrsta građevine nije određena (strukturni nalaz)
1. **Naslov zone spojen je s prvom rečenicom.** »Zone poslovne gradnje uz luku nautičkog turizma (K1 1 i K1 2 ) Unutar zona …« nema interpunkcije između naslova i teksta.
2. **Pohlepno traženje objekta.** `gramatika_v25.skupina_uvoda` prvo pogodi »gradnje« iz naslova (»poslovne gradnje uz luku …«). Odlomak do kraja rečenice pritom potroši i »smještaj građevina poslovne namjene«, pa se taj drugi, ispravni pogodak više ne ispituje. Sama fraza »građevina poslovne namjene« prepoznaje se ispravno (`vrste_gradevina` → poslovna).
3. **Rezervni put se nije uključio.** Vrsta iz cijelog uvoda u v2.5 traži se samo kad v2.2 ne izdvoji nijedno pravilo. Ovdje je v2.2 izdvojila kig/kis bez vrste, pa se taj put nije pokrenuo.
4. **Čl. 25. i 26. ne imenuju vrstu iz popisa** (»sadržaj komunalno-servisne namjene«, »postojeća zgrada hotela«). Ovdje je PREGLED ispravan ishod.

Zaštita KONTEKST_IZGUBLJEN radila je kako je zamišljeno: nijedno pravilo bez vrste nije prihvaćeno.

## 5. Usporedba s dosadašnjim testovima
| Test | Točno | Pogrešno | Pregled | Propušteno |
|---|---|---|---|---|
| Slijepi v2.3 – Novi Vinodolski (151 oznaka) | 0 | 1 | 2 | 151 |
| **Slijepi v2.5 – Crikvenica centar I (44 oznake)** | **0** | **0** | **7** | **44** |
| Razvojni v2.5 – Novi Vinodolski (nije slijepi) | 13 | 0 | 43 | 114 |

Sigurnost se generalizirala: 0 pogrešnih prihvaćanja. Pokrivenost se nije generalizirala: razvojni porast na Novom Vinodolskom ne prenosi se na plan drugačijeg oblika (naslovi zona bez interpunkcije, subjekt određen načinom gradnje, jedna rečenica s dvije vrijednosti).

## 6. Odvojeno zabilježena tehnička ograničenja izvora (prije Crikvenice)
Kandidati po kriteriju su odbačeni prije označavanja (`slijepo/treci_plan_v25/TIJEK_ODABIRA.md`):
- Rab UPU 41 – »KLASA:« velikim slovima;
- Omišalj UPU 2 – oštećeno kodiranje PDF-a.

To su ograničenja zamrznutog `citac.py` za PDF izvore, odvojena od ovog rezultata.

## 7. Za zajedničku odluku o smjeru (ništa nije pokrenuto)
Mogući smjerovi, bez prioriteta:
- struktura (točke 1–3 iz odjeljka 4);
- subjekt određen načinom gradnje;
- rečenice s dvije vrijednosti (»… ali najviše …«, »…, a ukupna visina …«);
- brojevi s točkom tisućica;
- `citac.py`: »KLASA:« velikim slovima.

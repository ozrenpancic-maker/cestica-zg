# Čitač v2.3: ciljana korekcija sedam pogrešaka (razvojno)

Grana: `eksperiment-citac-v2.3`, iz `eksperiment-oznake-v1`.
- Nije ništa spojeno u `main` i nije otvoren PR.
- Kod v1, v2.1 i v2.2 nije mijenjan.
- **Pravno potvrđenih pravila: 0.**

## Što je promijenjeno (`strukturiraj_v23.py`, sloj iznad zamrznute v2.2)
1. **Prijenos konteksta primjene.** Uvod stavka ili bloka (do prve dvotočke) može reći uz koju se građevinu gradi. Taj doslovni odlomak postaje `kontekst_primjene` svakog pravila tog stavka ili bloka.
   - Primjeri odlomaka: »uz građevine društvene i sportsko-rekreacijske namjene«, »uz građevine gospodarske namjene«, »na građevnoj čestici uz obiteljsku kuću«, »uz građevinu osnovne namjene«.
   - Odlomak ide na prvo mjesto u `uvjeti`. Posebni uvjeti alineje su u `dodatni_uvjeti`, a `izvor_konteksta` čuva članak, stavak ili blok i citat uvoda.
   - Primjenjuje se i na stambenu namjenu, prema preporuci: kontekst se čuva i kad ga ne treba ponavljati.
   - Vrsta pravila, status i vrijednost ostaju nepromijenjeni (test).
   - Primijenjeno na 45 pravila: PPUG čl. 20., 22., 23., 39., 50. i UPU 1 čl. 24. blok 7.
2. **»samo kao« u načinu gradnje.** »Stambene građevine mogu se graditi samo kao samostojeće« daje operator »=« umjesto »dopušteno«. Izvedena zabrana ostalih oblika ostaje.

## Mjerenje na istom razvojnom skupu (referenca v1 + odluke v1.1)
Isti postupak kao za v2.2 (`oznake/v1/mjeri_v23.py`).
- Kad v2.3 zapiše kontekst koji referenca u nekoj alineji ne navodi, to se ne broji kao pogreška.
- Takvi se slučajevi broje zasebno kao KONTEKST_IZNAD_REFERENCE (3 slučaja, UPU 1 čl. 24. blok 7).

| | v2.2 | v2.3 |
|---|---|---|
| točno (uključivo granularnost) | 70 | 73 |
| pogrešno prihvaćeno | 7 | 4 |
| pravilno na pregled | 15 | 17 |
| propušteno | 178 | 173 |
| preciznost prihvaćenih | 0,909 | 0,948 |
| prihvaćeno od jasnih zapisa | 46 % | 48 % |

**Ovo nije dokaz poboljšanja.** Korekcije su napravljene nakon uvida u ovaj skup.

## Preostale 4 »pogreške« nisu ispravljane u čitaču
Referenca za njih nije dosljedna, pa bi svaki popravak bio prilagodba ovim primjerima:
1. **Udaljenost od regulacijskog pravca po kategoriji ceste** (UPU 1 čl. 24., 4,0 m i 6,0 m). Čitač daje UVJETNO, referenca OSNOVNO. U UPU 1 čl. 14. referenca istu vrstu odredbe (»za ostale (pristupne) ceste«) bilježi kao UVJETNO.
2. **»(nova)« uz 400 m²** (UPU 1 čl. 14., k.č. 3932/1). Referenca ima »(nova)« ondje gdje tekst kaže »za gradnju«. Za »dopušteno je graditi sportsko-rekreacijske građevine« (17 zapisa) oznake nema.
3. **Način gradnje** (PPUG čl. 25.). Operator je sada »=«, kao u referenci. Ostaje razlika u vrijednosti: »samostojeće« ili »samostojeće građevine«.

## Poznata slabost: pokrivenost
- Propušteno je 173 od 268 zapisa.
- U PPUG čl. 20., 39. i 50. v2.3 ne izdvaja većinu alineja o pomoćnim građevinama (»tlocrtna projekcija nije veća od 50 m²«, visina 4,0 m, krovišta). Odbija ih kao PREDMET_NEPOZNAT ili VRIJEDNOST_NEPREPOZNATA. Test to bilježi kao poznato stanje.
- To je sljedeći prioritet (v2.4). Ne smije se razvijati na skupu na kojem se mjeri.

## Zamrzavanje i slijepi test
- **Zamrzavanje:** `ZAMRZNUTO_v2_3.json`, SHA-256 `e27c8c32a4118ff7b9c4a891889e6091e185f408e53a2987c8507a237aacd25e`. Sadrži kod, mapiranja, razvojnu referencu i upute.
- **Testovi:** 143 / 143. Ranijih 128 i 15 novih (`test_v23.py`), među kojima regresija UPU 2, determinizam i integritet v2.2.
- **Slijepi test:** `slijepi_v23.py`, isti postupak i kriterij odabira kao `slijepi_v22.py`.
- **Upute za označivače:** `UPUTE_OZNACAVANJA_v1_1.md`. Novi odjeljak 3a: uvjet iz uvoda stavka upisuje se u svaki zapis.
- **Nedostaje izvor drugog plana** (HTML ili PDF odluke iz Službenih novina PGŽ).

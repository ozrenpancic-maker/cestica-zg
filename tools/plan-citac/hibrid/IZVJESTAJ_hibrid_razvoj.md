# Hibridni čitač v1: razvojna dijagnostika i zamrzavanje

Status: eksperiment, samo grana `eksperiment-hibrid-v1`. Zamrznuta v2.6 nije mijenjana; njezin integritet je potvrđen (`slijepi_v26.provjeri_v26`). Pravno potvrđenih pravila: 0. Nije primjenjivo u produkciji.

## 1. Arhitektura
1. **Generator.** Izolirani AI pod-agent bez alata, bez plaćenih API-ja i bez pristupa oznakama ili izlazima v2.6. Dobiva samo `PROMPT_GENERATORA_v2.txt` i tekst članaka iz učitača v2.6, u dijelovima od najviše 8 000 znakova.
2. **Deterministička provjera** (`provjera.py`). Svaka tvrdnja provjerava se zasebno:
   - citat mora biti doslovan, a vrijednost mora biti u citatu; inače je kandidat ODBIJEN;
   - jedinica, operator iz rečenice izvora i ključne riječi parametra;
   - vrsta građevine: doslovni izraz, prepoznavanje istog rječnika vrsta i odnos s uvodom;
   - stanje, zona, uvjeti (veznici, »odnosno«, odlomak »za …« iza vrijednosti, cijeli uvjet uvoda), iznimke (odredba, alineja, uvod, nadređena alineja);
   - kis i broj etaža (nadzemne), točke mjerenja, formule, upućivanja, sukobi kandidata, oznaka »nejasno« od AI-ja.
   Ako se ključni uvjet ne može provjeriti, kandidat ostaje ZA_PREGLED.
3. **Razine kandidata.** IZDVOJEN → ODBIJEN / TEHNICKI_PROVJEREN_ZA_PREGLED / AUTOMATSKI_PRIHVACEN / ZA_PREGLED.
   - Tehnički provjeren: vrijednost, jedinica, operator i parametar su potvrđeni.
   - Automatski prihvaćen: dodatno je potvrđen i sav kontekst (vrsta, uvjeti, iznimke, zona, stanje).
4. **Usporedba** (`usporedba.py`). Ista je za v2.6 i hibrid, na istim oznakama, u dva načina: strogo i semantički.

## 2. Razvojni rezultati (generator v2, zamrznuta provjera)
Semantička usporedba; u zagradi je strogi način.

| Skup | Kandidata | Hibrid: točno / pogrešno prihvaćeno | Hibrid: pokrivenost JASNIH | Tehnički provjereni: točno / pogrešno | v2.6, isti usporednik: točno / pogrešno | v2.6: pokrivenost JASNIH |
|---|---|---|---|---|---|---|
| PPUG Krk | 242 | 26 / 0 (22 / 4) | 0,214 | 55 / 14 | 52 / 37 | 0,447 |
| UPU 1 Krk | 87 | 12 / 0 (9 / 3) | 0,224 | 20 / 5 | 12 / 8 | 0,224 |
| Novi Vinodolski | 111 | 10 / 0 (10 / 0) | 0,097 | 29 / 6 | 13 / 0 | 0,126 |
| Crikvenica | 43 | 4 / 0 (4 / 0) | 0,160 | 14 / 4 | 0 / 0 | 0,000 |

- **Strogi način.** Svih 7 pogrešno prihvaćenih hibrida u strogom načinu razlikuje se samo u nazivu: kis »(uz podrum ili ukupni)« prema nazivu u oznaci, ili »obiteljska građevina« / »… – jedriličarski klub« prema nazivu vrste.
- **Pogreške među tehnički provjerenima** (svi tehnički provjereni tretirani kao prihvaćeni): 14–22 %, daleko iznad praga od 2 %. Sve te pogreške zaustavile su provjere konteksta.
- **v2.6 s ovim usporednikom** ima više pogrešaka nego u svom službenom mjerenju (Krk 108 / 1). Na PPUG Krk 24 od 37 razlika su samo u polju točka (»a« prema »-« za alineju unutar točke), a 11 su u vrsti pravila. Ovaj usporednik je stroži, ali je isti za oba sustava.
- **Kornić:** referenca nije neovisna, pa nije mjeren.

## 3. Ispravci tijekom razvoja (prije zamrzavanja)
Svaki ispravak potaknula je pogrešna automatska prihvaćenost na razvojnom skupu. Oznake nisu mijenjane.
- **Citat od dijela rečenice** (NV, »odnosno 4 metra …«) → CITAT_DIO_RECENICE.
- **»hotel (postojeći)« iz uvoda** → STANJE_IZ_UVODA.
- **»najviše 2 nadzemne etaže« kao opći broj etaža** (Crikvenica) → ETAZE_NADZEMNE.
- **Alineja unutar točke** (PPUG) → točka »-« po uputama označavanja v1.2.
- **Skraćen uvjet uvoda** (»uz višeobiteljsku kuću« umjesto »na građevnoj čestici uz višeobiteljsku kuću«) → UVJET_UVODA_NEPOTPUN.
- **»za sve tipove gradnje« iza vrijednosti bez uvjeta** → UVJET_IZGUBLJEN.

## 4. Odstupanja
- **PPUG Krk, prvi pokušaj v2:** generator je koristio alate i skripte jer izlaz nije stao u jedan odgovor. Izlaz se koristi samo za dijagnostiku (`razvoj/odstupanje_ppug_v2/`). Zatim je uvedena podjela teksta na dijelove; svi dijelovi A–D generirani su bez alata.
- **Okvir poziva:** za NV, UPU 1 i Crikvenicu okvir je bio blaži (»NE koristi nikakve alate«). Za PPUG A–D i slijepi test vrijedi zamrznuti okvir `PROMPT_GENERATORA_v2.txt`. Za dio A provjereno je da je poslani poziv točno predložak + tekst (`provjeri_poziv` = True).

## 5. Trošak i vrijeme generatora (razvoj, v2)

| Skup | Tokena | Trajanje |
|---|---|---|
| Crikvenica | 88 753 | 150 s |
| UPU 1 Krk | 119 661 | 341 s |
| Novi Vinodolski | 150 670 | 531 s |
| PPUG Krk, 4 dijela | 408 856 | 957 s zbroj, oko 351 s usporedno |

- Deterministička provjera traje ispod 1 s po skupu.
- Novčani trošak: nema plaćenog API-ja; tokeni su iz razvojne sesije.

## 6. Pragovi i stanje prije slijepog testa
- **0 pogrešno prihvaćenih:** ispunjeno na razvoju u semantičkom načinu. Nula na malom uzorku nije dokaz nulte stvarne stope.
- **≥ 40 % pokrivenosti JASNIH:** nije ispunjeno ni na jednom razvojnom skupu (9,7–22,4 %).
- **≤ 2 % pogrešaka među tehnički provjerenima:** nije ispunjeno (14–22 %).

## 7. Zamrznuto
`ZAMRZNUTO_hibrid_v1.json` sadrži SHA-256 sljedećih datoteka:
- uputa, predloška poziva, sheme, provjere, usporedbe, mjerenja, izvlačenja, spajanja, slijepog postupka i testova (17/17);
- svih ovisnosti iz v2.6.

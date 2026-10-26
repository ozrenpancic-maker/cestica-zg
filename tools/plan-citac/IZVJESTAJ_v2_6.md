# Čitač v2.6 nakon slijepog testa Crikvenice

- **Grana:** `eksperiment-citac-v2.6`, iz `slijepi-v2.5-treci-plan`.
- **Nedirnuto:** `main`, produkcijski podaci, zamrznute verzije v1–v2.5, dodatak prilagodnika, sve oznake i referentni skupovi. Zamrznuti slijepi rezultat v2.5 na Crikvenici (`usporedba_v25.json`) nije mijenjan.
- **Pravno potvrđenih pravila: 0.**
- **Razvojni skup:** Crikvenica centar I je od ove verzije razvojni skup, kao Novi Vinodolski nakon v2.5. Rezultati na njoj nisu dokaz generalizacije.

## 1. Što je napravljeno (sloj nad zamrznutom v2.5)
| # | Zahtjev | Rješenje | Datoteka |
|---|---|---|---|
| 1 | Naslovi zona bez interpunkcije | Odlomak odmah iza »Članak N.« (≤ 150 znakova, bez završne interpunkcije, iza njega odlomak velikim slovom) odvaja se u `naslov_clanka`. Zone iz naslova (»(K1 1 i K1 2 )«, »Zona T1 1 - hotel«) idu u prostorni obuhvat svakog pravila članka. | `izvor_v26.py`, `gramatika_v26.zone_naslova` |
| 2 | Svi izrazi vrste u uvodu | `vrste_uvoda` bilježi svaki izraz i njegov odnos prema pravilu: OBJEKT_GRADNJE (»izgradnji / grade se / se grade / smještaj …«), POSTOJECA (»na kojoj se nalazi postojeća …«) ili spomen. Vrsta se uzima samo kad je u odnosu gradnje točno jedna različita vrsta; inače VRSTA_VISEZNACNA. | `gramatika_v26.py` |
| 3 | Subjekt izražen načinom gradnje | »Građevine koje će se graditi na slobodnostojeći način / kao dvojne …« → način gradnje (kodovi `slob`, `dvoj`, `ugr` zamrznute gramatike) i udaljenosti; »odnosno 3,0 m ukoliko …« je UVJETNO. | `gramatika_v26.oblici` |
| 4 | Dvije visine / dva broja etaža | »broj etaža je 4, ali … najviše 2 nadzemne« → dva pravila (ukupno ≤ 4; nadzemne ≤ 2). »visina … 10,0 m, a ukupna visina … 13,0 m« → visina i ukupna visina zasebno. Nove šifre su PREGLED. | `gramatika_v26.oblici` |
| 5 | Hrvatske tisućice | `1.500 m²` → 1500 (samo uz mjernu jedinicu, skupine od točno tri znamenke). `1,50 m`, `1.5 m`, »članka 110.« i »čl. 1.500 Zakona« se ne diraju (test). Citat ostaje izvoran. | `gramatika_v26.pripremi` |
| 6 | Word HTML i PDF | HTML: prijelom retka u kodu → razmak (zamrznuti prilagodnik), zatim naslovi članaka. PDF: granice odluke neovisne o veličini slova (ODLUKU/ODLUKA, Klasa/KLASA); oštećen font (þ, ÿ, ý, Ā) → ABSTAIN_KODIRANJE umjesto pogrešnog čitanja. Zamrznuti `citac.py` se ne mijenja. | `izvor_v26.py` |
| 7 | Bez vrste, obuhvata ili uvjeta → PREGLED | KONTEKST_IZGUBLJEN (vrsta ili zona iz naslova nedostaje), UVJET_MOGUCE_IZGUBLJEN (citat ima »ukoliko / ako / kada / uz uvjet«, a pravilo nema uvjet), VRSTA_VISEZNACNA, **VRSTA_IZ_UVODA_V26**. | `strukturiraj_v26.py` |

**Zaštita VRSTA_IZ_UVODA_V26 uvedena je zbog mjerenja.** Bez nje novi put za vrstu iz uvoda daje nova automatska prihvaćanja u člancima bez ikakve reference:
- UPU 1 Krk: +78 (čl. 36., 40.–45., 72.);
- UPU 2 Kornić: +7.

Njihova se točnost ne može izmjeriti. Zato se vrsta nađena tim putem zapisuje (`izvor_vrste`), ali pravilo ostaje na PREGLED dok sudac put ne provjeri. Učinak bez zaštite je izmjeren zasebno (stupac »bez zaštite«) i nije dio zamrznutog ponašanja.

**PDF izvori (točka 6).** Korišteni su samo format i broj izdvojenih članaka; odredbe nisu čitane.

| Izvor | Zamrznuto | v2.6 |
|---|---|---|
| Rab UPU 41 | ABSTAIN_GRANICA_ODLUKE | **47 članaka** (»KLASA:« velikim slovima) |
| Omišalj UPU 2 | ABSTAIN_GRANICA_ODLUKE | ABSTAIN_KODIRANJE (17 524 pogrešno preslikana znaka) |
| Mrkopalj UPU | ABSTAIN_GRANICA_ODLUKE | ABSTAIN_KODIRANJE (8 223 znaka) |

## 2. Regresija na četiri obitelji planova (`oznake/v1/mjeri_v26.py`, `mjerenje_v26.json`)
### 2a. Kandidati (cijeli dokument)
| Plan | v2.5 | v2.6 | Promjena | Prihvaćeno v2.5 → v2.6 |
|---|---|---|---|---|
| PPUG Krk | 234 | 235 | +1 | 95 → 95 |
| UPU 1 Krk | 1690 | 1708 | +18 | 409 → 409 |
| UPU 2 Kornić | 120 | 120 | 0 | 102 → 102 |
| UPU Novi Vinodolski | 70 | 70 | 0 | 18 → 18 |
| UPU Crikvenica centar I | 86 | **134** | **+48** | 3 → 3 |
| Crikvenica, označeni čl. 23.–26. | 7 | **22** | +15 | 0 → 0 |

### 2b. Točnost na označenim člancima
| Plan | Verzija | Način | Točno | Pogrešno | Pregled (pravilno / nepotrebno / bez oznake) | Propušteno | Pokrivenost JASNIH |
|---|---|---|---|---|---|---|---|
| Krk (268) | v2.5 | strogo = semantički | 108 | 1 | 30 / 11 / 39 | 119 | 71,1 % |
| | **v2.6** | strogo = semantički | **108** | **1** | 30 / 11 / 40 | 119 | 71,1 % |
| Kornić (99) | v2.5 / **v2.6** | – | 92 | **0** | 7 dvosmisleno (odgovara oznaci) | 0 | – |
| Novi Vinodolski (151) | v2.5 / **v2.6** | strogo | 9 | 4* | 7 / 4 / 32 | 131 | – |
| | v2.5 / **v2.6** | semantički | 13 | **0** | 9 / 15 / 19 | 114 | 12,6 % |
| Crikvenica (44) | v2.5 | strogo = semantički | 0 | 0 | 0 / 0 / 7 | 44 | 0 % |
| | **v2.6** | strogo | 0 | 0 | 0 / 0 / 22 | 44 | 0 % |
| | **v2.6** | semantički | 0 | **0** | 2 / 3 / 17 | **39** | 0 % |
| | v2.6 bez zaštite vrste (nije zamrznuto) | semantički | 3 | 0 | 2 / 0 / 17 | 39 | 12,0 % |
| | v2.6 bez zaštite vrste | strogo | 0 | 3** | 0 / 0 / 19 | 44 | – |

\* NV strogo: sva 4 »pogrešna« su broj etaža s točnom vrijednošću, operatorom i uvjetom. Razlika je u nazivu šifre i jedinici zapisa (vidi izvještaj v2.5).

\** Crikvenica strogo, bez zaštite:
- Dva »pogrešna« pravila (najveća površina čestice 1500 m², kig 0,5) razlikuju se samo po zapisu vrste: »poslovna građevina« prema »građevina poslovne namjene«. To je ista vrsta, istoznačnica je u `mapiranje_v26.json`.
- Treće (broj etaža ≤ 4) stroga usporedba spaja s krivom oznakom jer ne zna naziv šifre. Semantički se sparuje točno.

Te razlike ne mijenjaju vrstu građevine, uvjet ni pravni smisao. Ipak, istoznačnica je dodana nakon uvida u oznake Crikvenice, pa se izvještava odvojeno.

### 2c. Gubitak konteksta
Pravila s razlogom gubitka konteksta su ona koja imaju KONTEKST_IZGUBLJEN, KONTEKST_NADREDJENE_ALINEJE, VRSTA_VISEZNACNA, UVJET_MOGUCE_IZGUBLJEN ili VRSTA_IZ_UVODA_V25/V26. Brojevi su: ukupno / zadržana na pregledu samo zbog konteksta.

| Plan | v2.5 | v2.6 | v2.6 bez zaštite vrste |
|---|---|---|---|
| UPU 1 Krk | 909 / 21 | 953 / **104** | 829 / 26 |
| UPU 2 Kornić | 11 / 0 | 11 / 7 | 4 / 0 |
| Novi Vinodolski (označeni) | 18 / 7 | 18 / 7 | 18 / 7 |
| Crikvenica (označeni) | 7 / 0 | 22 / 3 | 15 / 0 |

Pravila na pregledu »samo zbog konteksta« (104 u UPU 1, 7 u UPU 2, 3 u Crikvenici) su upravo kandidati koje bi sudac mogao potvrditi uzorkom: vrijednost je izdvojena, nedostaje samo provjera vrste. Na Crikvenici su to kig 0,5, najveća površina čestice 1500 m² i broj etaža ≤ 4 u čl. 24. Sva tri su po oznakama točna.

### 2d. Stroga i semantička usporedba
- **Krk i Kornić:** nema razlike.
- **Novi Vinodolski:** 4 razlike, sve u nazivu i jedinici broja etaža.
- **Crikvenica v2.6:** 5 oznaka sparuje se samo semantički:
  - nazivi novih šifri: broj nadzemnih etaža, ukupna visina;
  - istoznačnica vrste »poslovna građevina« = »građevina poslovne namjene«.

  Nijedna od tih razlika ne mijenja vrstu građevine, uvjet ni pravni smisao.
- **Razlike koje nisu kozmetičke** zadržane su u obje usporedbe:
  - kis bez oznake nadzemno / ukupno;
  - čl. 25. »sadržaj komunalno-servisne namjene« bez vrste iz popisa;
  - čl. 26. »postojeća zgrada hotela«, koja je opis, a ne objekt gradnje;
  - čl. 23. općenite »građevine« bez obuhvata poglavlja.

## 3. Zaključak o v2.6
- **Sigurnost:** 0 novih pogrešnih prihvaćanja na sva četiri plana. Nijedno pravilo nije prihvaćeno u v2.6 ako nije bilo prihvaćeno u v2.5 (test na Krku, Korniću i Novom Vinodolskom).
- **Struktura:** naslovi, zone, tisućice, način gradnje, dvostruke vrijednosti i PDF granice rade. Na Crikvenici v2.6 izdvaja 22 umjesto 7 kandidata u označenim člancima i propušta 39 umjesto 44 oznake.
- **Prihvaćanje se nije povećalo.** Svaki novi kandidat čeka provjeru vrste ili je nova kategorija. To je posljedica pravila »bez potvrđenog konteksta nema prihvaćanja«, ne pogreške.
- **Ostaje izvan dosega determinističkih obrazaca:** 15 od 44 oznaka na Crikvenici i 80 od 114 propuštenih na Novom Vinodolskom su »drugo:« parametri. Mnoge preostale su opisne odredbe (način gradnje, rekonstrukcija, dopuštenost, upućivanja).

## 4. Zamrzavanje i slijepi test
- **Zamrzavanje:** v2.6 je zamrznuta u `ZAMRZNUTO_v2_6.json` (42 datoteke koda, mapiranja, razvojne reference, upute v1.2, sume v2.3 i v2.5).
- **Postupak:** `slijepi_v26.py`. Odabir, tekst i usporedba idu preko istog učitavanja izvora kao razvoj. Za PDF je potreban `--naslov`. Izvještavaju se strogo i semantički.
- **Napomena za sljedeći plan:** Rab UPU 41 nije čitan po sadržaju (korišten je samo za format PDF-a). Ipak bi za slijepi test bilo čišće uzeti plan koji nije ni otvaran.

## 5. Testovi i kontrolne sume
**Testovi:** 203 / 203 (test_citac 22, test_strukturiraj 36, test_v2 41, test_v22 29, test_v23 15, test_v24 14, test_v25 25, test_prilagodi 3, test_v26 18).

| Datoteka | SHA-256 |
|---|---|
| gramatika_v26.py | `bf066a4ea1550ae136170943cec76f209ed4e8f57e7a97492c2340cd31abd27c` |
| strukturiraj_v26.py | `9139ef00c159b763e2eb57a5243aa0523d7f5b1cc83a727ca1b8bd35629b782c` |
| izvor_v26.py | `52427e13544cc046bafee50a6e22c331b15965e52763d7af67eeda6f6b8aa95a` |
| test_v26.py | `5a82686a9da5d46a65c825f6f8c943081b5c542b7212422f4defd1d540eebb48` |
| slijepi_v26.py | `5b4e44c4dedd572ba51fc017d460b811b8d25da09a7e4f1025d305b5444552e7` |
| oznake/v1/mjeri_v26.py | `305715df0fff67f00a1ff596a33d58d1ab82febdd909ece0da8ccf7a9c352c09` |
| oznake/v1/mapiranje_v26.json | `3dbc04b5a2cd058832f0ccd767d6880a463d9971ebab2af573adc8e45df5489b` |
| oznake/v1/mjerenje_v26.json | `665c4118e1d6d95e795a529d79f2ca044069a58e65af3d6c2d5290ba18226294` |
| ZAMRZNUTO_v2_6.json | `e4e4975b24b84c8cfbd228c69cfca49979bc088a388d2bd0f5e163627f3ac4e2` |
| ZAMRZNUTO_v2_5.json | `7c884e382e847104e734168e884957ac19409656c9ed04d98596d88041a9ea82` |
| slijepo/crikvenica_centar_1/usporedba_v25.json | `021b306d1abdd332f939a30564b06b3ba84f4607bcf362519adb73cd0e352cdf` |

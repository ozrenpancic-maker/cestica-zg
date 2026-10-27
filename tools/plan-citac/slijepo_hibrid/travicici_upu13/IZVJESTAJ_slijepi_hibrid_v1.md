# Slijepi test hibridnog čitača v1: UPU 13 Travičići (Grad Opatija, SN PGŽ 15/2012)

Status: eksperiment. Ni zamrznuta v2.6 ni hibrid v1 nisu mijenjani prije ni poslije testa. Pravno potvrđenih pravila: 0. `main` i produkcija nisu dirani. v2.7 i nova arhitektura nisu pokrenuti.

## 1. Postupak (redoslijed je dio protokola)

| Korak | Što | Commit |
|---|---|---|
| 1 | Hibrid v1 zamrznut (`hibrid/ZAMRZNUTO_hibrid_v1.json`, SHA `e70d8342…`) | 69a0238 |
| 2 | Izvor preuzet nakon zamrzavanja; ranija upotreba nije nađena. 96 369 B, SHA `fdc767ec…` | 5ecd193 |
| 3 | Zamrznuti odabir (`slijepi_v26.py`): čl. 9, 10, 13 i 19; tekst za označavanje SHA `2436aab1…` | 5ecd193 |
| 4 | Ulaz generatora u 3 dijela (≤ 8 000 znakova); tekst je identičan tekstu za označavanje | efaffa6 |
| 5 | Generator: 3 izolirana poziva bez alata; za svaki potvrđeno da je poziv točno predložak + tekst; spojeno 109 kandidata, SHA `f17f8210…` | ec7c85f, 3d467e4 |
| 6 | Neovisni označivač (upute v1.2, bez alata): 114 zapisa, 60 JASAN, svi citati doslovni; oznake zamrznute prije usporedbe, SHA `32a518db…` | bdf7fcb |
| 7 | Usporedba, isti usporednik za v2.6 i hibrid; `usporedba_hibrid_v1.json` SHA `a46858d1…` | ovaj commit |

## 2. Rezultati na istim referentnim pravilima (114 oznaka, 60 JASAN)

| | v2.6 strogo | v2.6 semantički | Hibrid strogo | Hibrid semantički |
|---|---|---|---|---|
| Kandidata | 0 | 0 | 109 (3 odbijena) | 109 (3 odbijena) |
| Automatski prihvaćeno | 0 | 0 | 1 | 1 |
| Točno prihvaćeno | 0 | 0 | 0 | 0 |
| **Pogrešno prihvaćeno** | 0 | 0 | **1** | **1** |
| Na pregledu | 0 | 0 | 105 | 105 |
| – od toga s parom u oznakama | 0 | 0 | 15 | 23 (6 JASAN) |
| Propušteno | 114 | 114 | 99 | 91 |
| Pokrivenost JASNIH | 0 % | 0 % | 0 % | 0 % |

**Razine hibrida:**
- izdvojeno 109
- odbijeno 3 (vrijednost nije u citatu)
- tehnički provjereno 21
- automatski prihvaćeno 1
- za pregled 105

### Pragovi

| Prag | Cilj | Rezultat | Ishod |
|---|---|---|---|
| Pogrešno automatski prihvaćenih | 0 | 1 | **nije ispunjen** |
| Točno prihvaćenih JASAN pravila | ≥ 40 % | 0 % (0 od 60) | **nije ispunjen** |
| Pogreške među kandidatima koji prolaze automatsku (tehničku) provjeru | ≤ 2 % | semantički 15 od 21 = 71 %; strogo 20 od 21 = 95 % | **nije ispunjen** |

## 3. Svi pogrešno prihvaćeni primjeri

**H070, čl. 13, blok 3**
- Citat: »Najmanja udaljenost građevine od regulacijskog pravca odnosno od granice građevne čestice koja se nalazi uz prometnicu ili javnu površinu iznosi 6,0 m«.
- **Hibrid:** najmanja udaljenost od regulacijskog pravca ≥ 6 m, stambena građevina (iz naslova bloka »Smještaj stambene građevine …«), bez uvjeta, OSNOVNO, `nejasno` = null.
- **Oznaka Z070:** isto, ali s uvjetom »od granice građevne čestice koja se nalazi uz prometnicu ili javnu površinu« i oznakom PREGLED. Razlozi označivača:
  - VEZNIK: »odnosno« može biti istoznačnica ili druga referentna linija;
  - TOCKA_MJERENJA.
- **Zašto je provjera propustila:** provjera »odnosno« traži samo neposredno ispred vrijednosti (»… odnosno 4 metra«). Ovdje »odnosno« uvodi drugu referentnu liniju unutar naziva parametra, prije glagola. AI nije označio dvosmislenost. Izgubljen je **kontekst uvjeta**.
- Točku mjerenja provjera ispituje samo za visinu, ne za udaljenost.

## 4. Izgubljeni kontekst: tehnički provjereni, a pogrešni (semantički, 15)

| Razlika prema oznaci | Broj | Primjeri |
|---|---|---|
| samo vrsta građevine | 9 | »građevina« (naslov bloka) umjesto »turističko naselje« (čl. 9) ili »stambena građevina« (čl. 13): kig, kis, visina, zelenilo, površina čestice S1/S2 |
| vrsta građevine i uvjet | 2 | visina 9 m do vijenca / 11 m do sljemena (čl. 9) |
| operator i uvjet | 2 | »h/2, ali ne manje od 4,0 m«: oznaka max(h/2, 4,0), hibrid ≥ 4,0 |
| jedinica, vrijednost i uvjet | 1 | »1 nadzemna etaža« (čl. 10) |
| samo uvjet | 1 | H070 (automatski prihvaćen) |

Svi osim H070 ostali su na pregledu: zaustavile su ih provjere vrste (VRSTA_NEPREPOZNATA, VRSTA_ODNOS_NEPOTVRDEN) ili oznaka `nejasno` od AI-ja.

## 5. Zašto v2.6 nema nijedno pravilo
- 41 rečenica je odbijena, 0 pravila. Razlog je gotovo uvijek PREDMET_NEPOZNAT.
- Alineje u izvoru nemaju razmak iza crtice (»-najveći koeficijent …«). Numerirani blokovi (»2. Veličina i …«) slijepljeni su s rečenicama, pa gramatika ne vidi početak odredbe.
- Vrsta iz uvoda nije prepoznata ni u jednom članku.
- U dvije rečenice vrijednost nije prepoznata (VRIJEDNOST_NEPREPOZNATA).
- v2.6 je ovdje bila sigurna (0 pogrešnih), ali bez ikakve korisne pokrivenosti.

## 6. Pregled, trošak i vrijeme

| Mjera | v2.6 | Hibrid |
|---|---|---|
| Pravila za pregled | 0 | 105 |
| Tokeni | 0 | 258 676 (A 94 778, B 92 130, C 71 768) |
| Vrijeme generatora | – | 400 s zbroj, oko 190 s usporedno |
| Deterministička provjera | – | 0,25 s |
| Novčani trošak | 0 | nema plaćenog API-ja; tokeni su iz razvojne sesije |

Najčešći razlozi pregleda kod hibrida:

| Razlog | Broj |
|---|---|
| OPISNA_VRIJEDNOST | 91 |
| VRSTA_NEPREPOZNATA | 80 |
| AI_NEJASNO | 57 |
| PARAMETAR_IZVAN_POPISA | 55 |
| VRSTA_ODNOS_NEPOTVRDEN | 11 |

## 7. Procjena izvedivosti za produkciju
- **Ni v2.6 ni hibrid v1 nisu prikladni za automatsko prihvaćanje u produkciji.**
  - Hibrid je na neviđenom planu jedino pravilo koje je prihvatio prihvatio pogrešno.
  - Pokrivenost JASNIH je 0 %.
  - Stopa pogrešaka među tehnički provjerenima je 71 %.
- **Nula pogrešaka na razvoju nije prenesena na slijepi plan.** Razvojni rezultat (52 točna, 0 pogrešnih) nije dokaz nulte stvarne stope, a ovaj test to i pokazuje.
- **Što hibrid ovdje daje:** strukturirane kandidate s doslovnim citatima i razlozima pregleda. Na slijepom planu 23 kandidata na pregledu imaju par u oznakama. To bi moglo služiti samo kao pomoć ljudskom pregledu, ne kao automatska odluka. Ni to nije izmjereno kao korist.
- **Uska grla:**
  - prepoznavanje vrste građevine kad je subjekt opći ili dolazi iz naslova bloka;
  - uvjeti i referentne linije unutar naziva parametra;
  - format izvora (alineje bez razmaka) za v2.6.
- Algoritam nije mijenjan nakon uvida u rezultate. v2.7 i nova arhitektura nisu pokrenuti.

## 8. Kontrolne sume

| Datoteka | SHA-256 |
|---|---|
| izvor `travicici_upu13_sn_15_2012.html` | `fdc767ecf00b383f073694a50eb70d4ad9efc21f38bf758cc98c359d11fb01bc` |
| tekst za označavanje | `2436aab113982d62ee0ac5bd50e4bccddd2f37fd2a76754aae1d5441b3060ee1` |
| ulaz generatora | `1d2d3ebfa59d23c29d68864fbb9407d338a3063bb335efe09287160338629a29` |
| izlaz generatora `gen.json` | `f17f821090f60134ac5f0eb61611eb0fa7a65c8965f48c1d2da35a272d7a3704` |
| neovisne oznake | `32a518db448ec9d62eabae2991057bcfacec6a1356a1e39b8d28cc1043d0cb7a` |
| usporedba | `a46858d149ee50d0830e4a4cd8455301c9d9c09f82876481e6ebd75d9cffcf17` |
| zamrzavanje hibrida | `e70d834223d5757599db3c26725b86c9917e66a13bf0bd18d8d1184bd623fa76` |
| zamrzavanje v2.6 (kod) | provjereno `slijepi_v26.provjeri_v26`: netaknuto |

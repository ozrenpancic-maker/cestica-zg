# Odluke v1.2, ponovna ocjena i razvojna v2.4 (pomoćne građevine)

Grana: `eksperiment-citac-v2.4`, iz `eksperiment-citac-v2.3`.
- Nije ništa spojeno u `main` i nije otvoren PR.
- Zamrznute v2.2 i v2.3, izvorne oznake A/B, odluke v1 i v1.1 te `referenca_v1.json` nisu mijenjani. Provjerava se prije i poslije svakog mjerenja.
- Postupak slijepog testa v2.3 (`slijepi_v23.py`, `ZAMRZNUTO_v2_3.json`) nije mijenjan.
- **Pravno potvrđenih pravila: 0.**

## 1. Odluke suca v1.2
Zapisane su u `oznake/v1/odluke_suca_v1_2.json` (doslovno) i `oznake/v1/UPUTE_OZNACAVANJA_v1_2.md` (odjeljak 3b).
1. **Udaljenost od regulacijskog pravca po kategoriji ceste je UVJETNO.** Kategorija ostaje u uvjetu (UPU 1 čl. 14. i 24.).
2. **»(nova)« samo kad je izričita** u tekstu ili nedvosmislenom kontekstu. »Dopušteno je graditi« i »za gradnju« nisu dovoljni.
3. **»Samostojeće« = »samostojeće građevine«** kad je subjekt isti. Isključivost »samo kao« se čuva (operator »=«).

**Referenca v1.2** (`referenca_v1_2.json`) izvedena je iz zamrznute v1. Ima 9 promjena, svaka zabilježena u zapisu (`promjene_v1_2`):
- 2 × OSNOVNO → UVJETNO (UPU 1 čl. 24.);
- 7 × uklonjeno »(nova)« (UPU 1 čl. 14. blok k.č. 3932/1 i UPU 1 čl. 24. prateći sadržaji).

Odluka 3 ne mijenja zapise, nego se primjenjuje u usporedbi.

## 2. Ponovna ocjena bez promjene čitača (`ocijeni_v1_2.py`, `ocjena_v1_2.json`)

| | referenca v1.1 | referenca v1.2 |
|---|---|---|
| **v2.2** | točno 70, pogrešno 7, preciznost 0,909, od JASAN 46,1 % | točno 74, pogrešno 3, preciznost 0,961, od JASAN 48,7 % |
| **v2.3** | točno 73, pogrešno 4, preciznost 0,948, od JASAN 48,0 % | točno 77, pogrešno 0, preciznost 1,000, od JASAN 50,7 % |

**Rastav promjene od v2.2 / v1.1 do v2.3 / v1.2** (pogrešno 7 → 0):

| | samo oznake (v2.2: v1.1 → v1.2) | samo kod (v1.1: v2.2 → v2.3) | oboje |
|---|---|---|---|
| pogrešno prihvaćeno | 7 → 3 (−4) | 7 → 4 (−3) | 7 → 0 |
| točno (s granularnošću) | 70 → 74 | 70 → 73 | 70 → 77 |

**Provjera sedam slučajeva na stvarnim izlazima:**

| slučaj | v2.2 / v1.1 | v2.2 / v1.2 | v2.3 / v1.1 | v2.3 / v1.2 |
|---|---|---|---|---|
| PPUG čl. 25., način gradnje | pogr. | točno uz pravilo granularnosti* | pogr. | **točno** |
| UPU 1 čl. 14., 400 m² | pogr. | točno | pogr. | **točno** |
| UPU 1 čl. 24., 4,0 m | pogr. | točno | pogr. | **točno** |
| UPU 1 čl. 24., 6,0 m | pogr. | točno | pogr. | **točno** |
| PPUG čl. 39., 5,0 m | pogr. | pogr. | točno | **točno** |
| PPUG čl. 50., 5,0 m | pogr. | pogr. | točno | **točno** |
| PPUG čl. 50., 4,0 m | pogr. | pogr. | točno | **točno** |

\* v2.2 bilježi »dopušteno«, pa se slaže samo uz zamrznuto pravilo OPISNA_JEDNAKOST_ILI_DOPUSTENJE, koje ne provjerava isključivost. v2.3 bilježi »=« i zasebnu zabranu ostalih oblika.

**Zaključak:**
- Četiri pogreške riješene su odlukama suca (oznake), tri kodom v2.3 (kontekst primjene).
- Nijedna od sedam nije bila pogrešna brojka.

## 3. Razvojna v2.4: pomoćne građevine (`gramatika_v24.py`, `strukturiraj_v24.py`)
**Ustroj.** Zamrznuta v2.2 → novi oblici odredbi → kontekst i »samo kao« iz zamrznute v2.3.
- Rečenice koje v2.2 odbija ili ostavlja bez pravila čitaju se ponovno.
- Pravilo zapisuje zamrznuti `gramatika_v22._zapisi`, pa se čuvaju izvorni citat, uvjeti, prostorni obuhvat, razlozi i status.
- Svako pravilo ima `kontekst_primjene` (uz koju se građevinu pomoćna smije graditi), `dodatni_uvjeti`, `izvor_konteksta` i `prostorni_obuhvat`.

**Novi oblici odredbi:**

| Oblik | Primjer | Pravilo |
|---|---|---|
| E | »Pomoćne građevine grade se kao jednoetažne …« | etaže = »jednoetažne« |
| V | »visina od najniže kote … nije viša od visine osnovne građevine i ne prelazi visinu od 4,0 m [i jednoetažna je]« | visina ≤ visina osnovne građevine; visina ≤ 4,0 m (oba **PREGLED**, nema gornje točke mjerenja); [etaže] |
| T | »tlocrtna projekcija nije veća od 50 m²« | tlocrtna projekcija ≤ 50 m² |
| G | »[iznimno, unutar … cjelina,] mogu se graditi do granice građevne čestice« | položaj: dopušteno do granice čestice |
| O | »Ako imaju otvore prema susjednoj građevnoj čestici, moraju biti udaljene … najmanje 4,0 m« | udaljenost ≥ 4,0 m, UVJETNO |
| Z | »… odijeljene vatrobranim zidom, uz uvjet da nagib krova nije prema susjednoj čestici« | vatrobrani zid; zabrana nagiba (**PREGLED**) |
| R | »Na regulacijskom pravcu mogu se graditi samo garaže, kada …« | dopuštenje (**PREGLED**: »odnosno«, lokalni uvjeti) |
| K | alineja o krovištu koja je odbijena samo zbog zareza na kraju | ponovna raščlamba |

**Pravila sigurnosti:**
- Iznimka »iznimno, unutar povijesnih graditeljskih cjelina« vrijedi za cijelu alineju. Takvo pravilo dobiva i prostorni obuhvat POVIJESNA_CJELINA.
- Parametri izvan zatvorenog popisa uputa (vatrobrani zid, smjer nagiba, garaža na regulacijskom pravcu) uvijek su PREGLED (PARAMETAR_IZVAN_POPISA).

**Opseg i regresije:**
- Novih pravila: 53 u PPUG-u (čl. 20., 39., 50.) i 9 u UPU 1 čl. 24. blok 7.
- Pravila iz v2.3 su u v2.4 doslovno ista (test). UPU 2 je nepromijenjen. Determinizam je potvrđen.

**Mjerenje na razvojnom skupu** (referenca v1.2, ista pravila usporedbe za sve tri verzije, `mjeri_v24.py`):

| | v2.2 | v2.3 | v2.4 |
|---|---|---|---|
| točno (s granularnošću) | 74 | 77 | **108** |
| pogrešno prihvaćeno | 3 | 0 | 1 |
| pravilno na pregled | 17 | 19 | 30 |
| nepotrebno na pregled | 5 | 5 | 11 |
| propušteno | 172 | 167 | **119** |
| preciznost prihvaćenih | 0,961 | 1,000 | 0,991 |
| prihvaćeno od JASAN | 48,7 % | 50,7 % | **71,1 %** |
| pokrivenost izdvajanja | 35,8 % | 37,7 % | **55,6 %** |

**Po skupini, v2.4** (točno / pogrešno / propušteno):
- PPUG 22./23.: 40 / 0 / 13
- PPUG 25./33.: 13 / 0 / 10
- **PPUG 20./38./39./50.: 36 / 0 / 26** (u v2.3: 7 / 0 / 70)
- UPU 1 14.: 7 / 0 / 22
- UPU 1 24.: 12 / 1 / 48

**Jedina pogreška** je UPU 1 čl. 24.: »jednoetažna je«. Referenca ima broj 1, a v2.4 tekst »jednoetažna«. U PPUG-u ista referenca za isti izraz ima tekst »jednoetažne« (odluka suca: B). Referenca je nedosljedna u zapisu vrijednosti, pa čitač nisam prilagođavao.

**Mjere opreza:**
- Ovo je **razvojni rezultat**. v2.4 je razvijana gledajući upravo ove članke, pa porast pokrivenosti nije dokaz generalizacije.
- v2.4 **nije zamrznuta** i nije ušla u postupak slijepog testa. Slijepi test na neviđenom planu ostaje na zamrznutoj v2.3, prema uputi.
- U usporedbi je dodano jedno pravilo: TOCKA_MJERENJA_IZRAZ (»visina od <točka>« u uvjetu oznake = točka mjerenja čitača »od <točka>«). Novi nazivi parametara nalaze se u `mapiranje_v24.json` (samo nazivi).

## 4. Preostalo za v2.4 (nije rađeno)
- **UPU 1 čl. 24. blok 7:** opisne vrijednosti (»od susjedne građevine odijeljene vatrobranim zidom«, »nagib krova prema susjednoj …«) razlikuju se od teksta čitača. Zapisi ostaju PREGLED bez para.
- **Rekonstrukcija pomoćnih građevina** (»mogu se rekonstruirati … u postojećim gabaritima«) i dopuštenost gradnje iz uvoda bloka nisu raščlanjeni.
- **Složeni uvjeti:** »odnosno« u uvjetu za garaže sada je jedan doslovni uvjet uz PREGLED. Raščlamba na I/ILI ostaje otvorena.

## 5. Testovi i kontrolne sume
**Testovi:** 157 / 157 (test_citac 22, test_strukturiraj 36, test_v2 41, test_v22 29, test_v23 15, test_v24 14).

| Datoteka | SHA-256 |
|---|---|
| oznake/v1/odluke_suca_v1_2.json | `3efed723bfcbf18afd050385ef4d600872149e8b58ea7e8291e9052546565742` |
| oznake/v1/UPUTE_OZNACAVANJA_v1_2.md | `86d835601e8f6f5410afc5f63247952bebea8ab8e7c735513c5b48516eb98c05` |
| oznake/v1/referenca_v1_2.json | `97ba8943752b0f7aeee166493b695627c1d17da27b2052a45aef5b9331268d7a` |
| oznake/v1/ocjena_v1_2.json | `f4783817c3b4174206cda50dc948bfa331b40382e2582d2552d826f96ddb84bf` |
| gramatika_v24.py | `3e409ff32bbe5d402a9da29f7606b67636f5deeba46737c514836ee659efec5b` |
| strukturiraj_v24.py | `d90c8b775f12899be336837cd5a638957af6745368be8cfe1322a71b96f4e744` |
| test_v24.py | `be3c95b35a764556cda6a8d7ceef15a74fc53c24c85b47ddb66f8649de77dbaa` |
| oznake/v1/mapiranje_v24.json | `6b2ed70b6cea13c671d1fb5d43796056bfedc4b305935d8b3d9d60aa2d075a36` |
| oznake/v1/mjeri_v24.py | `bd57e128464683f2df72293150e35fa60bbe9a568e1afa8d3e6b0e39e027010c` |
| oznake/v1/mjerenje_v24_ref_v1_2.json | `26ffabc6601c17c276b1f3e7eaf4cb093822b9b299c7f39534fef7fcb7646a37` |
| ZAMRZNUTO_v2_3.json (nepromijenjeno) | `e27c8c32a4118ff7b9c4a891889e6091e185f408e53a2987c8507a237aacd25e` |

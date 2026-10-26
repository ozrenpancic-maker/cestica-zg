# Slijepi test zamrznute v2.3: UPU naselja Novi Vinodolski

Ovo je stvaran rezultat generalizacije na planu koji razvoj nikad nije vidio.
- Čitač je zamrznuta v2.3 (commit `60f954f`). Integritet `ZAMRZNUTO_v2_3.json` je potvrđen prije usporedbe.
- Kod, gramatika, postupak `slijepi_v23.py` i kriterij odabira nisu mijenjani.
- **Pravno potvrđenih pravila: 0.**

## Izvor i postupak
1. **Izvor:** SN PGŽ 32/2026, odluka 48, pročišćeni tekst odredbi za provedbu. SHA-256 `829aac2b45f1c0ab14b66d098cd5e5b3c06941e8b92ec28e5592508cd8f2e2f1`, preuzeto 26. 10. 2026. Pojedinosti su u `IZVOR.md`. Commit `b898c54`.
2. **Odabir** zamrznutim kriterijem: čl. 19., 20., 23. i 24. (7 936, 4 059, 2 186 i 3 902 znaka).
3. **Neovisni označivač** u zasebnom kontekstu, bez alata. Dobio je samo odabrani tekst i upute v1.2, uz polja `prostorni_obuhvat` i `blok`.
   - Rezultat: **151 referentno pravilo**, svi citati doslovni.
   - Zamrznuto prije usporedbe: SHA-256 `d79304cdd2eabe09713bbc4ccd0a9926a430781d277ac3efe3a4407f90235aad`, commit `0aea768`.
4. **Usporedba:** `slijepi_v23.py usporedi` → `usporedba_v23.json`.

## Rezultat

| | čl. 19. | čl. 20. | čl. 23. | čl. 24. | ukupno |
|---|---|---|---|---|---|
| referentnih pravila | 63 | 34 | 20 | 34 | **151** |
| pravila čitača | 0 | 3 | 0 | 0 | 3 |
| točno prihvaćeno | 0 | 0 | 0 | 0 | **0** |
| pogrešno prihvaćeno | 0 | 1 | 0 | 0 | **1** |
| ispravno na pregled | 0 | 0 | 0 | 0 | 0 |
| nepotrebno na pregled | 0 | 0 | 0 | 0 | 0 |
| pregled bez referentne oznake | 0 | 2 | 0 | 0 | 2 |
| propušteno | 63 | 34 | 20 | 34 | **151** |
| dodatni prijedlozi izvan odabranih članaka | (nije mjereno; usporedba obuhvaća samo odabrane članke) | | | | |

**Preciznost prihvaćenih:** 0,0 (0 od 1). **Pokrivenost jasnih pravila:** 0 % (0 od 103 JASAN). **Pokrivenost izdvajanja:** 0 %.

### Po vrsti referentnih pravila (sva propuštena)

| vrsta | JASAN | PREGLED | ukupno | točno |
|---|---|---|---|---|
| numerička | 15 | 7 | 22 | 0 |
| numerička uvjetna ili iznimka | 21 | 16 | 37 | 0 |
| opisna (opis, dopuštenje, =) | 37 | 15 | 52 | 0 |
| opisna uvjetna ili iznimka | 25 | 8 | 33 | 0 |
| negativna (zabrana) | 5 | 2 | 7 | 0 |
| **ukupno** | **103** | **48** | **151** | **0** |

## Sva pogrešno prihvaćena pravila
- **čl. 20. st. 2. al. 4:** »najveći dopušteni koeficijent izgrađenosti (Kig) iznosi 0,4;« → kig ≤ 0,4, vrsta »poslovna građevina«, PRIJEDLOG.
  - Vrijednost, operator i parametar su točni.
  - Referenca (Z074) ima vrstu »poslovna građevina (nova)«, jer uvod stavka kaže »prema slijedećim uvjetima za novu izgradnju«, što je izričito po odluci suca v1.2 br. 2. Čitač oznaku »nova« iz uvoda stavka ne prenosi.
  - Pogreška je u vrsti građevine (stanje), ne u brojci.

**Pravila za pregled (ne smatraju se riješenima):**
- **kis ≤ 2,0** (KIS_BEZ_OZNAKE) i **visina ≤ 11,0 m** (REFERENTNA_VISINA_NEPOZNATA).
- Oba se razlikuju od reference (Z075, Z079) samo po »(nova)«. Zato ih usporedba bilježi kao »pregled bez oznake«.

## Uzroci propuštanja
1. **Čl. 19., 23. i 24.: cijeli članak odbijen (SKUPINA_NEPOZNATA, 117 pravila).** Uvod članka ne počinje vrstom građevine koju čitač poznaje:
   - »Planom se utvrđuju opći uvjeti za izgradnju novih poslovnih i ugostiteljsko-turističkih građevina unutar površina …«
   - »Površina označena planskom oznakom (K11) … namijenjena je izgradnji poslovne građevine …«
   - »Površine označene planskim oznakama (K21) … namijenjene su izgradnji poslovnih građevina …«

   Vrsta je u objektu glagola »izgradnji« ili u sredini rečenice. Uz to se zona (K, T, K1, K11, K21–K24) zadaje kao prostorni obuhvat prije vrste.
2. **Oznaka alineje »•«** (čl. 19., 24.). Čitač poznaje samo »- «, pa se alineje s »•« ne odvajaju.
3. **Kratica »ul.« lomi rečenicu.** »… od regulacijskog pravca ul. Antuna Mataije iznosi 10 metara …« reže se iza »ul.«, pa predmet i vrijednost završe u različitim rečenicama (čl. 20. al. 9 i 11).
4. **Oblici odredbi kojih nema u gramatici** (čl. 20., PREDMET_NEPOZNAT):
   - »površina građevne čestice ne može biti manja od 600 m²« (bez »najmanja«);
   - »građevine mogu imati do 4 nadzemne etaže«;
   - »najmanja udaljenost od granice susjedne građevne čestice iznosi 5,0 m za građevine visine do 10,0 m, odnosno najmanje 6,0 m za više građevine«;
   - pomoćne građevine u jednoj dugoj alineji;
   - »iznimno za benzinske stanice 500 m²«.
5. **Stanje »nova« iz uvoda stavka** (»uvjeti za novu izgradnju«) se ne prenosi u pravilo (vidi pogrešku iznad).
6. **Mnogo opisnih odredbi:** priključci, ograde, zelenilo u postotku, kaskade, oblikovanje, pristup. 85 od 151 pravila ima parametar »drugo: …« izvan zatvorenog popisa, a takva pravila čitač ni ne pokušava izdvojiti.

## Zaključak
v2.3 na neviđenom planu **ne generalizira**:
- 0 točnih od 151 pravila;
- jedno automatski prihvaćeno pravilo (kig 0,4) ima točnu brojku, ali krivu vrstu građevine (nedostaje »nova«).

Na razvojnim skupovima preciznost je 0,95–1,00, a pokrivenost 48–51 %. Razlika pokazuje da je gramatika vezana uz oblik teksta PPUG-a Krk i UPU-a 1 Krk: uvodna rečenica s vrstom na početku, alineje »- «, oblici odredbi koji počinju s »najmanja / najveća«.

Mjera sigurnosti je djelomično radila. Čitač nije prihvatio nijednu pogrešnu brojku, a sve što nije prepoznao je odbio. Ipak je prihvatio jedno pravilo s nepotpunom vrstom građevine.

---
## Dodatak (nakon zamrzavanja izvještaja v2.3): neizmijenjena razvojna v2.4
**Ova usporedba nije slijepi test.** v2.4 (commit `1e6e522`) nije bila unaprijed zamrznuta za ovaj test. Pokrenuta je bez ikakve izmjene, nad istim zamrznutim oznakama, istim postupkom usporedbe. Rezultat je u `usporedba_v24_nezamrznuta.json`.

| | v2.3 (zamrznuta) | v2.4 (razvojna, nezamrznuta) |
|---|---|---|
| pravila čitača | 3 | 3 |
| točno | 0 | 0 |
| pogrešno | 1 | 1 |
| pregled bez oznake | 2 | 2 |
| propušteno | 151 | 151 |

**Pogreške koje bi postojeća v2.4 mogla riješiti: nijedna.**
- v2.4 dodaje oblike odredbi o pomoćnim građevinama u alinejama »- «, s kontekstom iz uvoda stavka. Ovdje se ne primjenjuju:
  - čl. 19., 23. i 24. odbijeni su prije raščlambe (SKUPINA_NEPOZNATA);
  - odredba o pomoćnim građevinama u čl. 20. (al. 11) ima drukčiji oblik (»najviše kao dvoetažne …, visine 4,0 metra. Građevine moraju biti udaljene 4,0 metra … ukoliko imaju otvore, odnosno 3,0 metra …«).
- Uzroci 1–6 iz izvještaja v2.3 nisu ni u v2.3 ni u v2.4.

## Preporuka za sljedeću razvojnu verziju (v2.5)
Redoslijed po učinku na ovom planu. Svaka stavka mora biti razvijena i provjerena na razvojnim skupovima, ne na ovom planu.
1. **Vrsta građevine iz cijele uvodne rečenice**, ne samo s početka. Obrasci »… namijenjena je izgradnji X«, »uvjeti za izgradnju novih X i Y«, »grade se X« te zona kao prostorni obuhvat (»površina označena planskom oznakom (K11)«). To otključava čl. 19., 23. i 24.
2. **Stanje »nova« iz uvoda stavka** (»uvjeti za novu izgradnju«), prema odluci suca v1.2 br. 2.
3. **Alineja »•«** kao ravnopravna alineji »- «. **Kratice koje ne završavaju rečenicu:** »ul.«, »čl.«, »st.«, »br.«, »vis.«, »sl.«.
4. **Oblici bez »najmanja / najveća«:**
   - »površina građevne čestice ne može biti manja od N«;
   - »do N nadzemne etaže«;
   - »A za građevine visine do X, odnosno najmanje B za više građevine« (uvjet ovisan o visini, uvijek PREGLED);
   - »iznimno za X N« unutar iste alineje.
5. **Ograde, zelenilo u postotku i kaskade** imaju jasne brojke, ali su izvan zatvorenog popisa parametara. Prvo treba odlučiti (sudac) proširuje li se popis. Do tada se takva pravila izdvajaju samo kao PREGLED.
6. **Sljedeći slijepi test** mora biti na trećem planu, koji ni v2.5 nije vidjela. Novi Vinodolski je od sada razvojni skup.

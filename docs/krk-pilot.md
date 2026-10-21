# Pilot: otok Krk (Grad Krk)

Stanje 18. 10. 2026., grana `razvoj`. Produkcija (`main`) nije mijenjana.

## Što radi

Dodir na otoku Krku (ili Izbornik → „Otok Krk (pilot)”) pokreće zasebnu analizu. Zagrebačka analiza se ne mijenja.

Prikaz za Krk:

| Odjeljak | Izvor | Stanje |
|---|---|---|
| Katastarska čestica (broj, k.o., površina, granica) | DGU, digitalni katastarski plan (ATOM po k.o.), `data/kat_krk/` | provjereno prema izvornim podacima (`docs/katastar-krk.md`); živi WFS ne radi (ORA-01000) |
| Namjena, građevinsko područje, izgrađeno ili neizgrađeno, udjeli na čestici | PGŽ, `STANJE/NAMJENA_POVRSINA_NOVO` | provjereno upitima na servis |
| Važeći planovi i planovi u izradi na lokaciji | PGŽ, `STANJE/IZRADA_PP` | provjereno upitima na servis |
| Nagib terena, pristup i okolina | Open-Meteo, OpenStreetMap | isti kod kao za Zagreb |
| Vodovod, kanalizacija, niskonaponska struja | DGU SKI, PGŽ (`_08`), `data/ski_krk/` | udaljenost od granice čestice; provjereno prema izvornim podacima (`docs/infrastruktura-krk.md`) |
| Telekomunikacije, plin | — | „Podaci nisu dostupni” |
| Uvjeti gradnje (obiteljska i višeobiteljska kuća, Grad Krk) | PPUG Grada Krka, pročišćeni tekst SN PGŽ 29/2020, `src/rules_krk.json` | parametri i navodi preuzeti s mrežne stranice SN-a; potrebna usporedba s cijelim tekstom |
| Komunalni doprinos (Grad Krk) | Odluka SN PGŽ 43/2018 | iznos po zoni upisuje korisnik (tablica nije u mrežnom tekstu) |
| Priključci, cijena gradnje | — | „još nisu obrađeni” |

Za ostalih šest jedinica na otoku prikazuje se isti županijski sloj, uz napomenu da pilot nije provjeren za njih. Za točke na kopnu unutar obuhvata (npr. Crikvenica) piše da su izvan područja aplikacije.

Ocjena namjene:
- „Građevinsko područje naselja” kad `POLAZNA_NAMJENA` sadrži „građevn…” i `PRIMARNA_NAMJENA` „naselje”;
- „izdvojene namjene” za ostala građevinska područja;
- „Izvan građevinskog područja” za sve ostalo.

Za „neizgrađeno” piše samo da plan *može* propisati obvezu UPU-a, ništa više.

## Uvjeti gradnje (Grad Krk)

Redoslijed odluke:
1. Druga jedinica na otoku: „zasad obrađeni samo za Grad Krk”.
2. Izvan građevinskog područja naselja: uvjeti za kuće ne vrijede.
3. Na lokaciji vrijedi UPU ili DPU (evidencija PGŽ): nema izračuna; uvjete propisuje taj plan.
4. Neizgrađeni dio GP-a: čl. 15., gradnja tek nakon UPU-a (crveno, bez brojki).
5. Naselje Krk (NA1): čl. 19. ga ne navodi za izravnu provedbu, pa su brojke samo orijentacijske.
6. Inače izračun prema čl. 22. (obiteljska) ili 23. (višeobiteljska), slobodnostojeća ili dvojna:
   - najmanja čestica, uz iznimku od 400 m²;
   - tlocrt (kig 0,25, najviše 200 ili 100 m², najmanje 60 m²);
   - nadzemni GBP (kis 0,5 i granica tipa 200 ili 400 m²), s podrumom kis 0,75;
   - etaže, visina 6,5 m;
   - od međe h/2, najmanje 4 m (3 m bez otvora), uz prostor za kuću na karti;
   - od regulacijskog pravca 4 m, uz razvrstanu cestu 6 m;
   - zelenilo 40 %, pristupni put.

Označeno kao potrebna provjera:
- vrijedi li granica GBP-a tipa i za podrum;
- etaže višeobiteljske kuće u NA1 i NA2 (definicija i čl. 23. se razlikuju);
- zaštićene povijesne cjeline.

### UPU-ovi Grada Krka

Evidencija PGŽ za Grad Krk navodi važeće UPU-ove: UPU 1 Krk (pročišćeni tekst SN 29/2020, izmjene u izradi), UPU 2 Kornić (SN 19/2016), UPU 5 Vrh (SN 2/2014), UPU 23 Torkul, UPU 25 kamp Glavotok, UPU 26 Dunat.

| UPU | Stanje u aplikaciji |
|---|---|
| UPU 2 Kornić | obrađen: zona M1, čl. 38. i 39. (kig 0,25, kis 0,75, tlocrt 60–200, dvojna 150, ugrađena 100 m², visina 7,5 m, na nagibu većem od 12 % do 10,5 m, međe 4 m, ceste 6/9 m i 4/7 m, zelenilo 40 %, 2 PM po stanu) |
| UPU 1 Krk | nije obrađen: stambena pravila (M11–M17) su iza čl. 26., koji nisu u mrežnom tekstu; treba PDF |
| UPU 5 Vrh | nije obrađen: pravila za kuće (čl. 27. i dalje) nisu u mrežnom tekstu; treba PDF |
| ostali (turistički i poslovni) | nisu obrađeni |

Zona unutar UPU-a ne može se odrediti automatski (grafički dio nije dostupan kao karta), pa se pretpostavlja M1 uz napomenu i izbor „druga zona”. Gdje vrijedi UPU, neizgrađeni dio nije blokiran čl. 15. PPUG-a, jer je UPU donesen.

### Ostale jedinice na otoku

| Jedinica | Plan | Stanje |
|---|---|---|
| Malinska-Dubašnica | PPUO, pročišćeni tekst SN 15/2023 | obrađeno: stambena građevina (do 2 jedinice), skupine GPN-1/2 (čl. 31.), GPN-3 (čl. 34.), GPN-4 (čl. 35.), GPN-5 do 12 (čl. 37.); skupina se čita iz oznake županijskog sloja; neizgrađeni dio uz provjeru uređenosti (čl. 27.) |
| Baška | PPUO, pročišćeni tekst SN 26/2020 | obrađeno: obiteljska kuća samostojeća, dvojna, skupna (čl. 30.–32.), najveća čestica 1350 m², u naselju Baška bez novih dvojnih i skupnih; neizgrađeni dio blokiran (čl. 19., 28.) |
| Vrbnik | PPUO, pročišćeni tekst SN 46/2024 | nije obrađeno: tekst je samo u PDF-u |
| Punat | PPUO, pročišćeni tekst 2010. + izmjene 2015., 2018., 2021. | nije obrađeno: nema novijeg pročišćenog teksta, potrebno spajanje izmjena |
| Omišalj | PPUO, pročišćeni tekst 2014. + izmjene 2015., 2017. | nije obrađeno: isto |
| Dobrinj | PPUO 2008. + usklađenje 2022. (PDF) | nije obrađeno: tekst je samo u PDF-u |

UPU-ovi u tim općinama (npr. UPU 1 Malinska, Radići; UPU-1 Baška; UPU 1 Vrbnik) nisu obrađeni: na njihovom obuhvatu piše da uvjete propisuje UPU.

## Komunalni doprinos (Grad Krk)

Važeća odluka je ona iz SN PGŽ 43/2018 (stranica Grada „Važnije odluke i pravilnici” ne navodi izmjene). Tablica iznosa po zonama nalazi se samo u PDF-u izdanja, koji nisam mogao pročitati, pa iznos upisuješ ti.

Za orijentaciju su prikazane zone iz prijedloga iz 2018., uz oznaku „neprovjereno”:

| Zona | Naselja | Prijedlog | Preračun (7,5345 kn/€) |
|---|---|---|---|
| I | Krk | 138 kn | 18,32 € |
| II | Kornić | 120 kn | 15,93 € |
| III | Pinezići | 100 kn | 13,27 € |
| IV | ostala naselja | 80 kn | 10,62 € |

Umanjenje od 30 % (čl. 10.) bira se ručno.

## Provjera s cijelim tekstovima (18. 10. 2026.)

Ozren je priložio dokumente; vrijednosti su uspoređene s cijelim tekstom:

| Dokument | Ishod |
|---|---|
| PPUG Grada Krka, pročišćeni elaborat (SN 29/2020), PDF | sve brojke čl. 14., 15., 17., 19., 22., 23., 33., 35. potvrđene; dopunjeno: GBP 200/400 m² uključuje pomoćne građevine (pojmovnik, točke 10. i 11.), pristupni put (točka 31.), parkiranje 2 PM/stan (čl. 107.) |
| UPU 2 Kornić (SN 19/2016), Word | potvrđeno; ispravljeno: zone M11 i M2 (ne „M1”), iznimka za kosi teren vrijedi samo za višeobiteljsku kuću i stambenu građevinu (bila je pogrešno i za obiteljsku); dodana stambena građevina (čl. 40.); GBP uključuje sve građevine na čestici |
| UPU 5 Vrh (SN 2/2014), Word | obrađeno: zone M11 i M12 (čl. 34., 35., 37., 38.) |
| UPU 1 Krk, pročišćeni elaborat (SN 29/2020), PDF | obrađeno: M11/M15/M21 (čl. 86., 90.), M12 (čl. 87., 91.), M25 stara jezgra (čl. 85., 89.); ostale zone bez kuća (čl. 84., 88.) |
| Odluka o komunalnom doprinosu Grada Krka (SN 43/2018), PDF | potvrđeno: I. zona 138 kn, II. Kornić 120 kn, III. Pinezići 100 kn, IV. ostala naselja 80 kn/m³ (čl. 6.); preračun fiksnim tečajem 7,53450; umanjenje 30 % samo do 500 m³ (čl. 10.); zona se određuje iz naselja |
| PPUO Vrbnik, pročišćeni elaborat (svibanj 2019.) | obrađeno (čl. 23.a i 23.b), ali uz upozorenje: plan je izmijenjen 2024. (SN 34/2024, pročišćeni SN 46/2024), a ta verzija nije priložena |
| Dobrinj, SN Općine Dobrinj 5/2022 | sadrži samo odluku o usklađenju PPUO sa zakonom (5 stranica), ne odredbe za provedbu; Dobrinj nije obrađen |
| Prijedlog odluke o komunalnom doprinosu (2018.) | isti kao ranije; zamijenjen donesenom odlukom |

Malinska-Dubašnica i Baška i dalje su preuzete s mrežne stranice Službenih novina (bez PDF-a).

## Koordinate

DGU servis radi u HTRS96/TM (EPSG:3765). Pretvorba je u aplikaciji (`tmFwd`/`tmInv`, Snyder) i provjerena prema pyproju na 5 točaka (Krk, Baška, Zagreb): odstupanje je ispod 2 cm.

## Što nije provjereno i zašto

1. **DGU WFS uživo.**
   - GetCapabilities odgovara: GeoServer, tipovi `cp:CadastralParcel` i `cp:CadastralZoning`, izlaz `application/json`, BBOX.
   - Moji probni GetFeature upiti nisu uspjeli preko alata za dohvat, a iz radnog okruženja servis nije dostupan.
   - Zato ne znam točan oblik JSON odgovora (raspored INSPIRE svojstava) ni smije li preglednik dohvatiti servis (CORS).
   - Kod traži broj čestice, k.o. i površinu bilo gdje u svojstvima. Ako dohvat ne uspije, piše „Katastar DGU: Podaci nisu dostupni”, a namjena se računa za dodirnutu točku.
2. **Uvjeti korištenja DGU podataka o česticama.**
   - Registar NIPP za skup „Katastarske čestice i katastarske općine INSPIRE” (0250) navodi uvjet pristupa i korištenja „Na zahtjev”.
   - GetCapabilities navodi Fees i AccessConstraints „NONE”.
   - Za sličan DGU WFS (način uporabe zemljišta) registar navodi otvorenu dozvolu, uz ograničenje od 1.000 objekata i dijagonale od 2 km po upitu. Aplikacija traži okvir od 2 × 2 m.
   - **Prije objave na produkciju treba potvrditi uvjete s DGU-om.**
3. **Vrijednosti namjene.** Vidio sam samo dva stvarna zapisa („građevna područja · naselje · GPN-1”, „poljoprivredno tlo · P3”). Ostale kategorije prikazuju se doslovno iz sloja.

## Kako provjeriti na mobitelu ili računalu

1. Otvori probnu verziju, zatim Izbornik → „Stanje servisa”. Tri retka „Krk: …” pokazuju može li preglednik dohvatiti svaki izvor.
2. Izbornik → „Otok Krk (pilot)”, pa dodirni 3–5 čestica koje poznaješ. Usporedi broj čestice i k.o. s Geoportalom DGU, a namjenu s VidiPlanom.

## Testovi

- `tests/run.js`, odjeljak 18 (25 provjera):
  - pretvorba koordinata;
  - upit prema DGU-u u HTRS96/TM;
  - prikaz čestice i namjene s udjelima;
  - planovi (zadnja važeća odluka, u izradi, bez državnog plana i planova van snage, samo http(s) poveznice);
  - „Podaci nisu dostupni” za infrastrukturu;
  - bez izmišljenih uvjeta gradnje;
  - kvar DGU-a; kopno; druga općina;
  - pretraga adrese na Krku;
  - stanje servisa.
- `tests/mobile/krk.py`: Chromium 390 × 844 i 320 × 640, bez vodoravnog pomicanja, snimke u `tests/mobile/out/krk_*.png`.

Svi testovi rade s lažnim odgovorima servisa. Stvarni servisi nisu dohvaćeni iz preglednika.

## Sljedeći koraci (nakon tvoje provjere)

0. Usporediti `src/rules_krk.json` s cijelim tekstom PPUG-a (SN 29/2020) i pročitati tablicu zona iz PDF-a SN 43/2018.
1. Ako DGU ne radi iz preglednika: opcije su posrednik (Cloudflare Worker, besplatna razina, zahtijeva tvoje odobrenje) ili prikaz bez čestice.
2. UPU 1 Krk i UPU 5 Vrh iz PDF-a.
3. Ostalih šest općina na otoku.

## Cijela Primorsko-goranska županija (21. 10. 2026.)

Okvir `PGZ_BBOX` (14,15–15,55 E; 44,45–45,65 N) usmjerava u istu analizu kao Krk. Na otoku čestica dolazi iz pripremljenog katastra, a izvan njega (kopno, Cres, Lošinj, Rab…) uživo iz DGU-a (`loadParcelHR`). Namjena i popis planova dolaze iz županijskih slojeva, koji pokrivaju cijelu županiju. Za jedinice bez obrađenih pravila piše „Uvjeti gradnje za X još nisu obrađeni”. Katastar infrastrukture (SKI) i komunalni doprinos postoje samo za Krk. Točka bez namjene u županijskom sloju (Istra, Lika, Slovenija) prelazi u osnovni pregled za državu.

Pravila gradnje za druge jedinice: tekst plana je u PDF-u koji alat ne može pročitati; PDF treba priložiti, pa se vrijednosti prepisuju u `src/rules_krk.json` (`ostaleJls`) uz doslovne navode.

### Punat: što su priložena dva PDF-a (21. 10. 2026.)

Oba su samo izmjene, bez temeljnog teksta, pa pravila za Punat još nisu uvedena u `rules_krk.json`.
- IV. izmjene i dopune PPUO Punat (SN PGŽ 10/2021): mijenjaju čl. 5, 32, 48, 77a, 77d, 97c i 107 (vile, Buka, reciklažna dvorišta, UPOV). Odredbi za stambene građevine nema.
- II. izmjene i dopune UPU 3 naselja Punat (SN PGŽ 3/2020): mijenjaju samo dio uvjeta. Iz njih je sigurno: tlocrt obiteljske kuće najviše 150 m² (dvojna 75 m², na čestici većoj od 1000 m² slobodnostojeća 200 m²), najmanje 60 m² (čl. 46); zelenilo 40 % (46a), 30 % (46b), 20 % (46c; 30 % za završnu jedinicu niza); višestambena građevina kig 0,25, kis 1,25, P+2, visina 9,0 m (7,0 m u neizgrađenom dijelu), tlocrt 80–250 m², do 4 stana (čl. 50a). Nedostaju najmanja čestica, kig, kis, visina i udaljenosti za 46a–46c.
Potrebno: UPU 3 Punat, SN PGŽ 34/10 i 13/16 (ili pročišćeni tekst) i osnovni PPUO Punat (SN 9/08, 30/10, 33/10, 14/15, 30/18 pročišćeni tekst).

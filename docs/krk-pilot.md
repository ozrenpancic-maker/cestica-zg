# Pilot: otok Krk (Grad Krk)

Stanje 18. 10. 2026., grana `razvoj`. Produkcija (`main`) nije mijenjana.

## Što radi

Dodir na otoku Krku (ili Izbornik → „Otok Krk (pilot)”) pokreće zasebnu analizu. Zagrebačka analiza se ne mijenja.

Prikaz za Krk:

| Odjeljak | Izvor | Stanje |
|---|---|---|
| Katastarska čestica (broj, k.o., površina, granica) | DGU, INSPIRE WFS `api.uredjenazemlja.hr/services/inspire/cp/wfs` | **u kodu, nije provjereno uživo** (vidi niže) |
| Namjena, građevinsko područje, izgrađeno ili neizgrađeno, udjeli na čestici | PGŽ, `STANJE/NAMJENA_POVRSINA_NOVO` | provjereno upitima na servis |
| Važeći planovi i planovi u izradi na lokaciji | PGŽ, `STANJE/IZRADA_PP` | provjereno upitima na servis |
| Nagib terena, pristup i okolina | Open-Meteo, OpenStreetMap | isti kod kao za Zagreb |
| Vodovod, kanalizacija, struja, plin | — | „Podaci nisu dostupni” (SKI za PGŽ nije pripremljen) |
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
4. Katastar infrastrukture za PGŽ (datoteka 08 na ski.dgu.hr).

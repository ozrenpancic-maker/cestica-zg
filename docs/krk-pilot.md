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
| Uvjeti gradnje | — | „Za otok Krk još nisu obrađeni” |
| Komunalni doprinos, priključci | — | „još nisu obrađeni” |

Za ostalih šest jedinica na otoku prikazuje se isti županijski sloj, uz napomenu da pilot nije provjeren za njih. Za točke na kopnu unutar obuhvata (npr. Crikvenica) piše da su izvan područja aplikacije.

Ocjena namjene:
- „Građevinsko područje naselja” kad `POLAZNA_NAMJENA` sadrži „građevn…” i `PRIMARNA_NAMJENA` „naselje”;
- „izdvojene namjene” za ostala građevinska područja;
- „Izvan građevinskog područja” za sve ostalo.

Za „neizgrađeno” piše samo da plan *može* propisati obvezu UPU-a, ništa više.

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

1. Ako DGU ne radi iz preglednika: opcije su posrednik (Cloudflare Worker, besplatna razina, zahtijeva tvoje odobrenje) ili prikaz bez čestice.
2. Odredbe za provedbu PPUG Krka (pročišćeni tekst SN 2020-29) → `rules_krk.json`, po uzoru na Zagreb.
3. Komunalni doprinos Grada Krka: pronaći važeću odluku (pronađen je samo prijedlog).
4. Katastar infrastrukture za PGŽ (datoteka 08 na ski.dgu.hr).

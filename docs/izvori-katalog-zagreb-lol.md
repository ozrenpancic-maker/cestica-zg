# Novi izvori iz kataloga „Hrvatska u izvorima” (zagreb.lol)

Katalog https://zagreb.lol/izvori-podataka/ (540 skupova, 169 izdavača) poslužio je samo kao popis za pretragu. Svaki izvor je otvoren i provjeren izravno kod izdavača (25. 10. 2026.). Aplikacija ne čita ništa sa zagreb.lol.

## 1. Plan približnih vrijednosti Grada Zagreba (odjeljak „Cijene zemljišta”)

- **Servis:** ArcGIS Grada Zagreba (ista organizacija kao namjena i urbana pravila), `Plan_pribliznih_vrijednosti/FeatureServer/0`. U istom sloju su izdanja 2019.–2026.: 690 cjenovnih blokova, polja `ppv_pv_eu_19` … `ppv_pv_eu_26`. Preglednik ga smije čitati (CORS).
- **Polja (aliasi iz servisa):**
  - `ppv_kz_26` je kategorija zemljišta.
  - `ppv_ki_26` je koeficijent iskoristivosti uzor-čestice.
  - `ppv_nz_26` je namjena zemljišta.
  - `ppv_pv_eu_26` je približna vrijednost zemljišta (EUR/m²).
  - Polja `_2` sadrže drugu vrijednost u istom bloku.
- **Pravna osnova:**
  - Zakon o procjeni vrijednosti nekretnina (NN 78/15), čl. 8: plan je kartografski prikaz cjenovnih blokova (st. 1). Približna vrijednost je općenita, prosječna vrijednost po m² za uzor-česticu (st. 3 i 5). Objavljuje se jednom godišnje (st. 8).
  - Kategorije su iz Pravilnika o metodama procjene vrijednosti nekretnina (NN 105/15), čl. 10. Za podskupine 4.1 i 4.2 navodi se samo da su podskupine četvrte kategorije (čl. 10. st. 2). Koja je koja nije pretpostavljeno.
- **Upit:** po granici čestice. Kad čestica leži u više blokova, prikazuje se udio svakog bloka, a iznos se računa po dijelovima. Kad blok ima dvije vrijednosti, prikazuje se raspon. Blok bez vrijednosti (kategorija 0) dobiva „nije utvrđena”, bez iznosa.
- **Pouzdanost B:** vrijednost se odnosi na uzor-česticu bloka, ne na ovu česticu.
- **Prikaz:**
  - grafikon 2019.–2026.;
  - usporedba s traženom cijenom iz oglasa;
  - redak u sažetku;
  - praćenje promjena (`SNAP_USP`).
- Samo za Zagreb. Za ostale gradove planovi su u eNekretninama, a javni servis nije pronađen.

## 2. Kulturna dobra iz Registra kulturnih dobara (okoliš i rizici, cijela Hrvatska)

- **Izvor:** Ministarstvo kulture i medija, geoportal.kulturnadobra.hr, upit `api/wfs/identify?wktGeom=…&elKatIds=…`. To je isto sučelje kojim geoportal odgovara na klik po karti.
- **Slojevi (ElKat):**
  - 15 Z-lista;
  - 16 P-lista;
  - 41–43 konzervatorske podloge (KPC, PZO, GOPS);
  - 47–48 UNESCO.
- **CORS:** sučelje dopušta samo vlastitu stranicu, pa upit ide preko posrednika: `?kultura=lat,lon;lat,lon;…`, najviše 60 točaka. Posrednik:
  - pretvara točke u HTRS96/TM (WKT);
  - pamti odgovor tjedan dana;
  - vraća sažetak **bez geometrije i bez imena pročelnika**.
- **Aplikacija šalje** granicu čestice uvučenu 1 m od međa, pojednostavljenu na najviše 40 točaka. Tako dobro na susjednoj čestici koje samo dodiruje među ne postaje pogodak.
- **Prikaz:**
  - naziv, status, registarski broj, vrsta i datacija dobra;
  - konzervatorska podloga;
  - nadležni konzervatorski odjel (službeni kontakt ureda).
- **Bez pogotka** piše da prostorni plan može imati evidentirana dobra kojih nema u registru (pouzdanost B).
- **Pravna napomena:** za radove na kulturnom dobru trebaju posebni uvjeti i odobrenje konzervatora (Zakon o zaštiti i očuvanju kulturnih dobara). Broj članka nije naveden jer pročišćeni tekst nije bio dostupan za provjeru.
- **Licenca ponovne uporabe nije navedena.** Registar je javni popis; aplikacija prikazuje samo sažetak uz navođenje izvora.

## 3. Geološka podloga (HGI, karta 1:300 000)

- **Izvor:** Hrvatski geološki institut, Osnovna geološka karta RH 1:300 000, INSPIRE WFS u NIPP-u (`transformiraj.nipp.hr/…_wfs`, GeoJSON). Preglednik ga smije čitati (CORS).
- **Upit u točki unutar čestice:**
  - `ge:MappedFeature` u okviru oko točke;
  - geološka jedinica (`GeologicUnit`) daje sastav (CGI litologija, prevedena na hrvatski) i starost (`GeologicEvent`, INSPIRE GeochronologicEraValue);
  - rasjedi (`ShearDisplacementStructure`) u krugu od oko 500 m, s udaljenošću do najbližeg.
- **Pouzdanost C.** Karta je pregledna, a granice su točne na stotine metara. Zato nema praga ni upozorenja po udaljenosti od rasjeda (to bi bilo brojčano pravilo bez propisa). Uvijek se upućuje na geotehnički izvještaj za lokaciju.
- Uvjeti servisa: `AccessConstraints: otherRestrictions`, `Fees: conditionsUnknown`. **Licenca nije potvrđena.**

## 4. Usporedba cijene gradnje s Biltenom IGH (odjeljak „Procjena cijene gradnje”)

- **Izvor:** Bilten N.I. „Standardna kalkulacija radova u visokogradnji – nadogradnja I”, III-2026, Institut IGH d.d. za MPGI.
  - Cijene su na dan 31. 3. 2026., bez PDV-a.
  - PDF ima 384 stranice: https://mpgi.gov.hr/UserDocsImages/dokumenti/Graditeljstvo/Bilten_N_I_3_26_cor13.pdf
  - Preuzimanje je bez naknade, uz navođenje izvora (str. 3).
- **Upisano u kod (`IGH`):**
  - za tipske samostojeće kuće A.1–A.3.a i četiri grada: „UKUPNO KUĆA” (samo kuća, bez septičke jame, uređenja čestice i garaže), GBP i neto korisna površina;
  - troškovi projektiranja i stručnog nadzora;
  - prosjek grupe A po gradu (Zagreb 2.327 €/m² neto; str. 363). Provjereno: prosjek sedam tipova za Zagreb = 2.326,5.
- **Tip kuće** se bira iz procjene:
  - P+1 s kosim krovom je A.1, a s ravnim krovom A.3;
  - P + potkrovlje je A.2;
  - s podrumom je varijanta „.a”;
  - ostale etažnosti dobivaju samo prosjek grupe A po m² neto, bez preračunavanja na GBP.
- **Grad:** Zagreb za Zagreb, Rijeka za Krk, inače najbliži od četiri grada.
- **PDV 25 %:** Zakon o porezu na dodanu vrijednost, čl. 38. st. 1.
- **Pouzdanost B:** riječ je o tipskoj kući, ne o tvom projektu. Aplikacija ne mijenja vlastitu procjenu, nego je samo uspoređuje s Biltenom.

## 5. Financiranje: stambeni kredit (novi odjeljak, napredni način)

- **Kamatne stope:** ECB Data Portal, MIR (statistika kamatnih stopa banaka) za Hrvatsku; podatke dostavlja HNB. Novi stambeni krediti kućanstvima, ugovorena godišnja stopa (AAR):
  - `M.HR.B.A2C.A.R.A.2250.EUR.N` – svi;
  - `…P…` – fiksna kamata dulje od 10 godina;
  - `…F…` – promjenjiva ili fiksna do 1 godine.
  - API je otvoren (CORS) i bez ključa. Zadnjih 13 mjeseci daje i usporedbu s prošlom godinom.
- **Izračun:** anuitetni otplatni plan s mjesečnim ratama. Iznos kredita je ukupna investicija (osnovni iznos) umanjena za vlastita sredstva.
  - Rok i kamata se mogu upisati; unosi se pamte u pregledniku.
  - Bez naknada i osiguranja, pa se upućuje na EKS iz ponude banke.
- **Pouzdanost:** C uz prosječnu kamatu tržišta, B uz kamatu koju upiše korisnik.
- **HNB tablice** (G2 i dr.) nisu korištene izravno: to su XLS datoteke na stranici HNB-a bez otvorenog API-ja, a HNB zabranjuje mijenjanje objavljenih materijala.

## Što nije korišteno i zašto

- **Oglasi (Njuškalo, Index, Oglasnik):** uvjeti korištenja ne dopuštaju strojno preuzimanje.
- **eNekretnine ZKC:** pristup samo uz ovlaštenje.
- **Google Photorealistic 3D Tiles:** plaća se.
- **DGU LiDAR DMR/DMP 1 m:** samo na zahtjev.
- **HGI katastar klizišta:** nema strojnog izvoza. Koseizmički procesi (WMS) odnose se samo na potres kod Petrinje 2020.
- **DGU ortofoto 1:1000:** anonimni WMS ima vodeni žig.

## Provjera na uređaju

Nakon spajanja posrednika (Deno, iz `main`):

1. Otvori `…/?kultura=45.8150,15.9736`. Treba vratiti Palaču Kulmer (Z-999), Grad Zagreb, Gradski zavod za zaštitu spomenika.
2. U aplikaciji otvori česticu u Gornjem gradu i česticu na Krku (stari grad Krk, Z-2684).
3. Plan približnih vrijednosti: čestica u Sesvetama. Usporedi s Geoportalom Grada Zagreba.

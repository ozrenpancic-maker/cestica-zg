# Karte prostornih planova iz rasterskih kataloga (PGŽ, ISPU)

Kad korisnik odabere česticu na Krku, aplikacija u katalogu rasterskih karata prostornih planova Zavoda za prostorno uređenje PGŽ potraži listove UPU-a i DPU-a koji pokrivaju česticu. Zatim izreže kartu oko čestice i preko nje ucrta granicu čestice.

**Detaljnu zonu (M1, M11, M2…) aplikacija ne očitava i ne pretpostavlja.**

## Izvor

- Servis: `https://gisportal.pgz.hr/server/rest/services/PP_RASTERI/PP_RASTERI/MapServer` (ArcGIS, Raster Catalog, EPSG:3765).
- Slojevi koji se pretražuju:

  | Sloj | Naziv | Plan | Sustav |
  | --- | --- | --- | --- |
  | 12 | `RASTER_5UPU_HTRS` | UPU | HTRS96 |
  | 5 | `RASTER_5UPU` | UPU | GK5 |
  | 13 | `RASTER_6DPU_HTRS` | DPU | HTRS96 |
  | 6 | `RASTER_6DPU` | DPU | GK5 |

  Isti list u oba sustava: koristi se onaj iz HTRS96.
- Polja zapisa: `OBJECTID`, `Name`, `KARTA_NAZIV`, `PLAN_NAZIV`, `OPCINA`, `GIS_SIFRA`, `MJERILO`, `KARTA_SIFRA`, `STANJE_1212`.
- UPU 2 Kornić, karta 1 (`618_karta1_i.tif`, OBJECTID 7096) nalazi se u sloju 5. Utvrdio korisnik 19. 10. 2026.

## Tijek

1. Točka na čestici (`turf.pointOnFeature`) pretvori se u HTRS96/TM (`tmFwd`). Zatim se pošalje `query` na svaki sloj: `geometryType=esriGeometryPoint`, `inSR=3765`, `spatialRel=esriSpatialRelIntersects`. Pretraga je prostorna, ne po OBJECTID-u.
2. Listovi se poredaju tako da je prvi list namjene: naziv karte spominje namjenu ili korištenje, ili je datoteka `karta1`. Korisnik može izabrati drugi list.
3. Izrez: `export` s `bbox` oko čestice u EPSG:3765, `imageSR=3765`, `layers=show:<sloj>`, `layerDefs={"<sloj>":"OBJECTID=<id>"}` (samo taj list), `f=json`.
4. Granica čestice iz DGU-a pretvara se u piksele prema okviru (`extent`) koji je servis stvarno vratio, a ne prema traženom.
5. Na glavnoj karti isti list se prikazuje kao `export` za trenutni prikaz u Web Mercatoru (`bboxSR=imageSR=3857`, `f=image`). Prikazuje se ispod granice čestice.

## Status i aktualnost lista

- List se veže uz plan iz evidencije planova PGŽ (`IZRADA_PP`) za istu točku:
  - prvo po vrsti i broju („UPU 2”);
  - ako broja nema, po riječima iz naziva.
- **Status plana:**
  - važeći (A, uz zadnju odluku u evidenciji);
  - van snage (povijesni plan, C, upozorenje „karta ne vrijedi za gradnju”);
  - samo u izradi ili nije pronađen (C).
- **Aktualnost lista:** katalog ne navodi odluku ni datum lista.
  - Ako evidencija ima samo jednu važeću odluku i nema izmjena u izradi: B („vjerojatno”).
  - Inače C: treba provjeriti grafički dio zadnje odluke.
- Izmjene plana u izradi prikazuju se kao upozorenje (C).
- Polje `STANJE_1212` prikazuje se samo kao zapis. Njegovo značenje nije potvrđeno, pa se ne koristi.
- Ako evidencija za točku navodi UPU/DPU, a katalog nema list, aplikacija to kaže. Ne zaključuje da vrijedi samo prostorni plan grada ili općine.

## Što se prikazuje

- **Plan, karta i izvor:** plan, karta (naziv, mjerilo, datoteka, šifra), izvor karte, GIS sloj i OBJECTID.
- **Provjera:** datum provjere i razina pouzdanosti. Pouzdanost je uvijek „preliminarno: georeferencirani raster”.
- **Zona:** uvijek „Detaljna zona nije potvrđena”. Skenirana karta nema digitalnu legendu povezanu s bojama.
- **Razine podataka:**
  - vektor: namjena iz PPUG-a, županijski sloj;
  - preliminarno: raster UPU-a;
  - pravno potvrđeno: samo lokacijska informacija.

## Uvjeti gradnje

- Oznake pouzdanosti A/B/C opisane su u `docs/pouzdanost.md`.

- Za UPU s pravilima po zonama izračun se radi tek kad korisnik sam odabere zonu.
- Odabir se pamti posebno za svaku česticu i ne prenosi se na druge.
- Uz izračun piše da zona nije potvrđena.
- Izračun za zonu koju je odabrao korisnik uvijek ima razinu C (korisnička pretpostavka).
- Ranija zadana vrijednost (M11 kao pretpostavka) je uklonjena.

## Proširenje

Drugi katalozi, npr. druge županije, dodaju se u `RASTER_KATALOZI` s adresom servisa, obuhvatom i popisom slojeva.

## Napomena za UPU 2 Kornić

Na karti 1 zone su označene M1 i M2. U odredbama koje aplikacija ima (SN PGŽ 19/2016, čl. 37.) zone su M11 i M2. Tu razliku treba razjasniti s legendom donesenog plana i lokacijskom informacijom prije nego što se oznaka s karte poveže s pravilima.

## Vrste kataloga

U `RASTER_KATALOZI` svaki katalog ima `tip`. Kod ne ovisi o pojedinoj čestici ni o identifikatoru lista.

| Tip | Katalog | Obuhvat | Kako radi |
| --- | --- | --- | --- |
| `arcgis` | PGŽ `PP_RASTERI` | Primorsko-goranska županija | upit po točki, `export` samo lista (`layerDefs`), granica prema vraćenom okviru |
| `wms` | ISPU, Ministarstvo (`PPRasterZ21_Public`) | Grad Zagreb | popis slojeva iz `GetCapabilities`, listovi čiji okvir obuhvaća točku, `GetMap` za točno traženi okvir |

Novi katalog dodaje se zapisom s adresom, obuhvatom i tipom. Za drugu županiju ISPU-a mijenja se samo naziv servisa (`PPRasterZxx_Public`), nakon provjere u pregledniku.

## ISPU WMS (Zagreb)

- **Poslužitelj:** prvi je `gis2.mgipu.hr`. U pregledniku je potvrđen 19. 10. 2026. (HTTP 200, CORS, 899 slojeva, EPSG:3765, EPSG:4326 i CRS:84).
  - `gis3`, `gis4` i `gis1` koriste se samo ako gis2 ne odgovori.
  - Prvi koji vrati ispravan `GetCapabilities` koristi se za cijelu česticu.
- **Listovi:** slojevi bez podslojeva čiji `EX_GeographicBoundingBox` sadrži točku čestice.
- **Naziv sloja:** `HR_ISPU_<vrsta><oznaka>_<šifra>_R<revizija>_<karta>`, npr. `HR_ISPU_GUP1_01333_R09_IS_1_1`.
  - Oznaka revizije služi samo da se vide inačice iste karte.
  - Ne dokazuje važenje lista: aktualnost lista je uvijek C.
- **Vrsta karte** se određuje iz naziva (Title):
  - korištenje i namjena;
  - urbana pravila i način gradnje;
  - uvjeti korištenja, uređenja i zaštite;
  - promet i komunalna infrastruktura;
  - ostalo ili nepoznato.

  Karta prometa nikad ne postaje karta namjene. Ako među listovima nema karte namjene, to piše iznad karte.
- **Redoslijed:**
  - karta namjene prije ostalih;
  - detaljniji plan prije općenitijeg (DPU, UPU, GUP, PPU);
  - viša oznaka revizije prije niže; starije inačice su na kraju i označene.

  Aplikacija ne odlučuje koji plan ima prednost: svi listovi su u izborniku.
- **Izrez:**
  - `GetMap` u EPSG:3765 (os E, N) za kvadrat oko čestice, 800 × 800 px, prozirna pozadina.
  - WMS vraća točno traženi okvir, pa se granica crta prema njemu.
  - Ako sloj ne podržava EPSG:3765, koristi se CRS:84.
- **Sadržaj na čestici:** okvir sloja može biti veći od stvarnog sadržaja lista. Zato se slika očita u pregledniku i računa udio granice čestice koju prekriva sadržaj (ne proziran, ne bijel).
  - List bez sadržaja na čestici aplikacija sama preskače i prelazi na sljedeći list iste vrste. To piše u prikazu.
  - Ako se slika ne može očitati, piše „nije provjereno”.
- **Glavna karta:** `GetMap` u CRS:84 za trenutni prikaz, ispod granice čestice.
- **Status plana:**
  - za GUP Grada Zagreba i Prostorni plan Grada Zagreba status je iz evidencije aplikacije (`rules_meta.json`, „na snazi”), dakle A za plan, ne za pojedini list;
  - za GUP Sesvete i UPU-e evidencije nema, pa je status C.
  - Javna evidencija planova za Zagreb, kao `IZRADA_PP` za PGŽ, još nije povezana.

## Šifre karata u ISPU-u (stanje 19. 10. 2026.)

Stvarni test na točki u Zagrebu dao je 15 slojeva:

- GUP (`HR_ISPU_GUP1_01333_R09_…`): `IS_1_1`, `IS_3_1`, `IS_4_1`, `KN_1_1`, `KN_1_2`, `KN_1_3`, `ZP_1_1`, `ZP_1_3`, `ZP_2_4`;
- `HR_ISPU_PPZP_00021_R10_…`: `IS_1_1`, `IS_3_1`, `IS_4_1`, `KN_1_1`, `ZP_1_3`, `ZP_3_2`.

**Što je provjereno:**

- Grafički dio GUP-a Grada Zagreba (čl. 5. st. 1. t. B Odluke; [prikaz izmjena 2025.](https://zagreb.hr/userdocsimages/arhiva/prostorni_planovi/izid%20gup%20grada%20zagreba_2023-/druga%20ponovna%20javna%20rasprava/01_IZID%20GUP%202025_2PJR_prikaz%20izmjena%20kroz%20sve%20faze.pdf)) ima ove kartografske prikaze u mjerilu 1:5000:
  - 1. Korištenje i namjena prostora;
  - 2. Mreža gospodarskih i društvenih djelatnosti;
  - 3a. Promet; 3b. Energetski sustav, pošta i telekomunikacije; 3c. Vodnogospodarski sustav i postupanje s otpadom;
  - 4a. Urbana pravila; 4b. Procedure urbano-prostornog uređenja; 4c. Zaštićeni i evidentirani dijelovi prirode; 4d. Nepokretna kulturna dobra.
- Objavljeno pravilo koje veže šifre ISPU-a (KN, IS, ZP i brojeve) uz te prikaze nisam našao. Prezentacija o ISPU-u navodi samo da su prikazi „imenovani i usklađeni prema dostavljenim uputama”, a te upute nisu objavljene. Navodi i da sustav ne razlikuje koji list pripada kojoj izmjeni plana ([izvor](https://www.prostorno-kkz.hr/attachments/article/79/Geoportal%20prostornih%20planova%20Maja_2_radionica%20[Compatibility%20Mode].pdf)).
- Iste šifre ne znače isto u svakom planu. ParcelIQ za GUP Knina navodi `KN_1_3` kao kartu uličnih koridora i prometa. Broj prikaza ne odgovara skupinama: GUP Zagreba ima 2 + 3 + 4 prikaza, a ISPU 3 KN + 3 IS + 3 ZP sloja.

**Zato aplikacija:**

- šifre ne tumači. Vrstu karte čita samo iz naziva sloja u servisu, ako on nije šifra, ili iz provjerene tablice `RK_SIFRE` (za svaki plan i oznaku revizije, s izvorom i datumom);
- tablicu puni tek nakon što se naslov pročita na cijelom listu (gumb „Otvori cijeli list” ili `planovi-test.html`). Tablica je zasad prazna;
- plan veže uz evidenciju samo kad ga servis imenuje. Inače je status C („plan je prepoznat samo iz šifre sloja”);
- za namjenu u Zagrebu koristi službeni vektorski sloj GIS baze planirane namjene (A), kao i dosad. Raster ISPU-a je kartografski dokaz.

## Pregled i potvrda listova (alat)

Odjeljak 3 stranice `planovi-test.html` (probna stranica):

1. Za točku pronađe sve listove čiji okvir je obuhvaća. Uz svaki prikaže minijaturu cijelog lista, ISPU šifru, Title iz servisa i nadređeni sloj.
2. Dodir na minijaturu otvara list u većoj razlučivosti (2400 px), s povećanjem ×2 i ×4.
3. Uz svaki list se upisuju:
   - plan prema listu;
   - službeni kartografski prikaz, ako je popis prikaza plana poznat (zasad GUP Grada Zagreba, iz Odluke). Odabir upisuje službeni naslov i vrstu;
   - naslov s lista;
   - vrsta: namjena, urbana pravila, promet, infrastruktura, zaštita, ostalo;
   - napomena.

   Bez naslova i vrste zapis ostaje „nepotvrđeno”. Ništa se ne popunjava iz šifre.
4. „Izvezi potvrđene u JSON” sprema sve zapise:
   - sloj, plan, revizija, šifra, Title;
   - naslov, vrsta, status;
   - izvor, datum provjere, tko je provjerio.

   Unosi se do izvoza pamte samo u tom pregledniku.

**Uvoz:**

```
python3 tools/ispu/provjeri_sifre.py ispu_sifre_….json --uvezi   # provjera i spajanje u src/ispu_sifre.json
python3 build.py                                                # ugradnja (ponovna provjera; greška zaustavlja izradu)
```

U aplikaciju (`RK_SIFRE`) ulaze samo potvrđeni zapisi s naslovom, vrstom, izvorom i datumom. Takav list dobiva vrstu s oznakom A. Format je u `tools/ispu/primjer_sifre.json` (izmišljeni plan).

## Potvrđene šifre (src/ispu_sifre.json)

Potvrdio Ozren 19. 10. 2026., usporedbom lista ISPU-a sa službenim grafičkim dijelom važećeg GUP-a (zagreb.hr, SGGZ 9/16). GUP grada Zagreba, V. ID (dopuna), revizija R09:

| Šifra | Prikaz | Vrsta |
| --- | --- | --- |
| KN_1_1 | 1. Korištenje i namjena prostora | namjena |
| KN_1_3 | 2. Mreža gospodarskih i društvenih djelatnosti | ostalo |
| IS_1_1 | 3a. Promet | promet |
| IS_3_1 | 3b. Energetski sustav, pošta i telekomunikacije | infrastruktura |
| KN_1_2 | 4a. Urbana pravila | urbana pravila |
| ZP_2_4 | 4b. Procedure urbano-prostornog uređenja | ostalo |
| ZP_1_1 | 4c. Zaštićeni i evidentirani dijelovi prirode | zaštita |
| ZP_1_3 | 4d. Nepokretna kulturna dobra | zaštita |

**Nepotvrđeno:**

- `IS_4_1` (GUP).
- Svih 6 listova PPGZ-a (`PPZP_00021_R10`, IX. ID). Tri su u izvozu bila potvrđena prikazima GUP-a. To je drugi plan, pa su vraćena na nepotvrđeno. Provjera sada takav zapis odbija, a alat za pregled za list PPGZ-a ne nudi prikaze GUP-a.

Potvrde vrijede samo za ovaj plan i ovu reviziju. Iste šifre u drugom planu ili drugoj reviziji ne koriste se.

## Provjera na stvarnim servisima (19. 10. 2026.)

Ozren je provjerio na probnoj stranici, na Android mobitelu (Chrome).

**Krk, 735/76 k.o. Kornić (PGŽ katalog):**
- aplikacija je sama našla UPU 2 Kornić, list namjene `618_karta1_i.tif`;
- granica čestice leži na karti ispravno, uz oznake M1 i D2;
- status plana je A (SN 19/2016), aktualnost lista B, zona C.

**Zagreb, 1541/2 (ISPU WMS, gis2):**
- aplikacija je sama odabrala kartu namjene GUP-a (`KN_1_1`, vrsta A iz potvrđene tablice);
- granica čestice leži ispravno: granica zone na rasteru poklapa se s granicom namjene u gradskom vektorskom sloju;
- aktualnost lista je C (list iz V. ID, dopuna), zona C.

**Nije provjereno:**
- „Prikaži na karti” (list na glavnoj karti) na mobitelu;
- listovi PPGZ-a (6, nepotvrđeni);
- drugi gradovi.

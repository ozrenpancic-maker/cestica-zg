# Detaljna namjena: karte UPU-a iz rasterskog kataloga PGŽ

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

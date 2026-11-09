# Stvarne visine i krovovi zgrada iz LiDAR-a DGU-a (nDMP)

Stanje 9. 11. 2026. Alat je spreman i ispitan na umjetnim podacima (`tools/zg3d/test_ndmp.py`). Pravih podataka još nema: nDMP se kod DGU-a dobiva na zahtjev.

## Što je nDMP

Normalizirani digitalni model površina: visina zgrada i vegetacije iznad tla, iz LiDAR snimanja cijele Hrvatske 2021.–2023. (DGU, projekt LIFE CROLIS). Rezolucija 1 x 1 m, GeoTIFF s datotekom `.tfw`, po listovima mjerila 1:2000, HTRS96/TM. Ne pokriva pojas uz istočnu granicu.

## Kako doći do podataka (radiš ti, jednom po području)

1. Podjela na listove 1:2000: `https://www.lifecrolis.hr/wp-content/uploads/2025/07/PODJELA_LIDAR_2000.7z` (shapefile). U QGIS-u ili ovdje kod mene odaberemo listove koji pokrivaju područje (npr. otok Krk).
2. Zahtjev DGU-u: obrazac „Zahtjev – podaci nDMP” na stranicama DGU-a (Pristup informacijama → Podnesi zahtjev → Ostali zahtjevi). Upisuješ svoje podatke i popis listova ili granicu područja. Namjena: komercijalna (aplikacija Čestica HR).
3. Podatke koje DGU pošalje (`.tif` i `.tfw` po listu) spremiš u jednu mapu.

## Uvjeti korištenja (iz obrasca DGU-a)

- Besplatno, neisključivo, i za komercijalnu uporabu; dopušteno prilagođavati i ugrađivati u aplikacije.
- **Kod javne objave točne koordinate i visine pojedinih točaka ili objekata ne smiju se moći izravno očitati.** Zato alat sve visine zaokružuje na 0,5 m, a aplikacija prikazuje samo 3D model okolnih zgrada, bez brojčanih visina.
- Navesti izvor: „Sadrži informacije tijela javne vlasti u skladu s dozvolom” i datum preuzimanja (aplikacija to ispisuje uz 3D pogled).
- Izmijenjeni podaci moraju biti označeni kao izmijenjeni (aplikacija piše da su visine izvedene i zaokružene).

## Obrada

```
python3 -I tools/zg3d/pripremi_ndmp.py data/zg3d_krk <mapa s nDMP listovima> data/zg3d_krk 2026-11-20
```

Za svaku katastarsku zgradu: pikseli nDMP-a unutar tlocrta → ravan krov (visina = medijan) ili dvostrešni krov sa sljemenom po duljoj ili kraćoj stranici (bira se onaj koji bolje odgovara). Složeni i četverostrešni krovovi se pojednostavljuju na ravan krov izmjerene visine. Zgrade bez LiDAR podataka (nove, srušene) zadržavaju pretpostavljenu visinu i ilustrativni krov.

Potrebno: Python 3 s paketima `numpy`, `shapely`, `pyproj`, `tifffile`.

## Šire od Krka

Za cijelu Hrvatsku podaci su veliki (desetci GB rastera ulaza, nekoliko milijuna zgrada). Plan: po gradovima i područjima koja trebaju; za cijelu državu treba prvo pripremiti tlocrte iz katastra (kao `tools/zg3d/pripremi_krk_zgrade.py`) i riješiti smještaj izlaznih kvadrata (GitHub Pages i Cloudflare Pages imaju ograničenje broja i veličine datoteka).

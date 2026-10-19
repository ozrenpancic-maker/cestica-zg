# Pouzdanost podataka (A / B / C)

Svaki važan podatak u analizi čestice ima jednu oznaku. Uz nju idu izvor, datum i obuhvat provjere ili metoda izračuna.

| Oznaka | Značenje | Primjeri |
| --- | --- | --- |
| **A** | službeno potvrđeno: podatak kako ga objavljuje službeni izvor | grafička i katastarska površina (DGU), upisana površina (OSS, javni uvid), namjena iz službenog vektora, status plana iz evidencije planova, tekst pravila iz važećeg plana |
| **B** | izračunato ili preliminarno | udio zona (GIS presjek), tlocrt i GBP iz kig-a i kis-a, prostor nakon odmaka, list UPU-a iz georeferenciranog rastera, granica urbanog pravila iz karte javne rasprave |
| **C** | nepotvrđeno | detaljna zona UPU-a, zona koju je odabrao korisnik, ručni unos površine, aktualnost lista, planovi u izradi, pristup, regulacijski pravac, komunalna opremljenost, parkiranje |

## Pravila (u kodu: `pz`, `pzCalc`, `pzUser`)

1. Izračun nikad nije bolji od **B**. Ako mu je bilo koji ulaz **C**, i rezultat je **C**. Razlog se prenosi u napomenu.
2. Korisnički odabir (npr. zona u UPU-u) uvijek je **C** i označen je kao „tvoja pretpostavka”. Ne može postati A ponovnim odabirom.
3. Službeni GIS podatak (A) potvrđuje samo sebe, ne i pravnu dopuštenost gradnje. Aplikacija pravnu dopuštenost ne utvrđuje. Nju potvrđuju lokacijska informacija i projekt.
4. Pristup s javne prometne površine, regulacijski pravac, komunalna opremljenost i parkiranje uvijek se prikazuju kao **C**, za svaki tip gradnje, dok ih aplikacija ne može provjeriti iz službenog izvora.

## Gdje se vidi

- Oznaka uz vrijednost (npr. tlocrt i GBP u „Izračunu za ovu česticu”, status i aktualnost lista UPU-a).
- Odjeljak „Pouzdanost podataka”: sve stavke za česticu, prvo C, s mjestom gdje se provjeravaju.
- Registar `PZREG` (za trenutnu česticu) temelj je budućeg PDF izvještaja i popisa „Što još provjeriti”.

# Cijene zemljišta po JLS

Pretvara službene priloge „Pregled tržišta nekretnina RH 2025” (MPGI i EIZ) u `data/ptn/ptn2025.json`. Opis je u `docs/cijene-zemljista.md`.

1. Preuzmi i raspakiraj https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Prilozi_PTN2025.zip
2. Pokreni: `python3 tools/ptn/pripremi.py <mapa Prilozi_PTN2025> data/ptn/ptn2025.json` (treba `openpyxl`).

Kad izađe novo izdanje, dovoljno je ponoviti korake s novim prilozima i provjeriti nazive listova i stupaca.

# Izvor za slijepi test v2.3

- **Plan:** Urbanistički plan uređenja naselja Novi Vinodolski. Odluka o donošenju, odredbe za provedbu (pročišćeni tekst).
- **Glasilo:** Službene novine Primorsko-goranske županije, br. 32/2026 (14. 8. 2026.), odluka 48.
- **Poveznica:** https://www.sn.pgz.hr/default.asp?Link=odluke&izdanje=3446&mjesto=51250&odluka=48
- **Preuzeto:** 26. 10. 2026. u 19:15 UTC.
  - Mreža radnog okruženja blokira sn.pgz.hr, pa je dokument dohvaćen u pregledniku na korisnikovu računalu (`fetch` iste stranice).
  - U radno okruženje prenesen je gzip + base64 u četiri dijela. Ispravnost je provjerena CRC-om gzipa i SHA-256 cijelog dokumenta.
- **Datoteka:** `nv_upu_sn_32_2026.html`, 437 506 bajtova, `text/html`.
- **SHA-256 izvornog dokumenta:** `829aac2b45f1c0ab14b66d098cd5e5b3c06941e8b92ec28e5592508cd8f2e2f1`. Izračunat u pregledniku i ponovno u radnom okruženju; isti je.
- **Provjera da dokument nije korišten u razvoju:**
  - Nijedna grana repozitorija nema ovaj dokument ni tekst UPU-a Novi Vinodolski.
  - »Novi vinodolski« se pojavljuje samo u meta-ključnim riječima web-stranice glasila u `slijepo/ppug_krk/ppug_krk_sn_2020_29.html`.
  - Razvojni skupovi v1–v2.4 su PPUG Krk, UPU 1 Krk i UPU 2 Kornić.
- **Odabir članaka:** zamrznutim postupkom `slijepi_v23.py odaberi` (kriterij nepromijenjen). Odabrani su čl. 19., 20., 23. i 24.
- **Čitač:** zamrznuta v2.3, commit `60f954f`. Integritet je provjeren s `ZAMRZNUTO_v2_3.json`.

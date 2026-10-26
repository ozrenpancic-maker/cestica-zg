# Izvor – UPU Crikvenica centar I (treći plan, slijepi test v2.5)

- Odredio sudac (Ozren Pančić), 26. 10. 2026.: https://www.sn.pgz.hr/default.asp?Link=odluke&id=14576
- Trajna poveznica: https://www.sn.pgz.hr/default.asp?Link=odluke&izdanje=556&mjesto=10003&odluka=12
- Službene novine PGŽ, Godina XVI. (2008.), broj 18.
- Naslov: »ODLUKU o donošenju Urbanističkog plana uređenja Crikvenica centar I«.
- Preuzeto ugrađenim preglednikom (pristup sa poslužitelja blokiran), gzip + base64, provjereno SHA-256.
- `crikvenica_upu_centar_1.html`: 228 011 B, SHA-256 `7f08f8da7f8eaad6d3200b530d6b9def7e0aa0a9948424437cf39e0eec344b45`, windows-1250.
- Plan nije korišten u razvoju ni u testiranju.

## Ishod zamrznutog postupka (prije označavanja)
- `slijepi_v25.py odaberi` → `[]`; zamrznuti `citac_tekst.izdvoji_tekst` → 0 članaka.
- Uzrok (provjereno samo na oznakama, ne na odredbama): stranica je HTML iz Worda. U svih 114 članaka broj stoji u sljedećem retku izvora (»Članak« ⏎ »1.«). Zamrznuti izdvajač traži »Članak N.« u istom retku.
- Zamrznuta v2.5 ovaj izvor ne može pročitati: prepoznatih članaka 0, kandidata 0. Označavanje i usporedba nisu pokrenuti.

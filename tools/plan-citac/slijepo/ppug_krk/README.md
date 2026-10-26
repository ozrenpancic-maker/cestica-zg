# Slijepi skup: PPUG Krk, čl. 22. i 23. (SN PGŽ 29/2020)

Ovdje dolazi **samo izvorni tekst** (HTML sa sn.pgz.hr, id=42441, ili PDF pročišćenog teksta), bez ikakvih oznaka i bez izmjena.
Uz datoteku se zapisuje SHA-256, URL i vrijeme dohvata (`_meta.json`).

Postupak:
1. Početni test, bez novih obrazaca:
   `python3 ../../slijepi_test.py IZVOR --clanci 22 23 --plan "PPUG Krk" -o ../../izlaz/slijepo_ppug_22_23_v0.json`
2. Neovisne oznake čl. 22. i 23. (drugi označivač, oblik kao `oznake/upu2_cl38_40.json`) spremaju se izvan ove mape.
   Razvoj ih ne vidi do ocjene.
3. Tek tada se dodaju obrasci za nove formulacije i ocjena se ponavlja (`ocijeni.py`).

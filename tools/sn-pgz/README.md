# sn-pgz (prototip)
Dohvat i obrada odluka iz Službenih novina PGŽ. Vidi `docs/sn-pgz-izvjestaj.md`.

    python3 sn_pgz.py fetch 41087 38031          # dohvat (1 zahtjev / 2 s, predmemorija u ./sn-cache)
    python3 sn_pgz.py analiziraj tekst.txt        # zaglavlje, vrsta, članci i operacije
    python3 provjeri_citate.py ../../data/pravila-sn/punat-upu3.json 41087=tekst.txt
    python3 test_sn_pgz.py                        # SN_TEKST_41087=tekst.txt za provjeru citata nad stvarnim tekstom

# Analiza priloženog izvora PPUG Krk (26. 10. 2026.)

Priložena datoteka: `ppug_krk_sn_2020_29.html`, 2.171.534 bajta, SHA-256 `b13bbfd10e53c01bf2dadb35e9a7eb7940521beef013293fab32c2fe48ce02df`.
Očekivano (izvor iz v0.25.0): SHA-256 `f67ac384d8f30d444cf19a10165f29b65ee93cf37281bb6e183abd981f5cf318`, 2.096.745 bajta.

## Nalaz: datoteka nije izvorna, dijakritici su nepovratno izgubljeni
- **37.395 znakova zamijenjeno je s U+FFFD** (zamjenski znak, bajtovi `EF BF BD`). Ostali znakovi nisu dirani, pa datoteka sama po sebi ispravno dekodira kao UTF-8.
- Pogođena su sva slova s dijakriticima (č, ć, đ, š, ž) i navodnici »«. Primjeri: »ku�a«, »gra�evne �estice«, »�lanak 22.«.
- **Razlika u veličini točno odgovara toj zamjeni:** 2.096.745 + 37.395 × 2 = 2.171.535 bajta. Svaki jednobajtni znak Windows-1250 postao je troznakovni U+FFFD. Izvorni tekst je, dakle, pročitan kao UTF-8 umjesto kao Windows-1250 i ponovno spremljen.
- Izvorna slova ne mogu se vratiti: »ku�a« može biti »kuća« ili »kuča«. Pogađanje bi značilo izmišljanje teksta.
- **`citac_tekst.py` takav izvor odbija** (`ABSTAIN_KODIRANJE`), pa početni slijepi test na njemu nije pokrenut.

## Dva pojavljivanja čl. 22. i 23.
Iako su slova oštećena, struktura dokumenta je čitljiva. U istom broju SN PGŽ 29/2020 objavljena su dva pročišćena teksta s vlastitom numeracijom članaka:

| Dio | Akt | Numeracija | Potpis (Odbor za statutarno-pravna pitanja) | Čl. 22. / 23. |
|---|---|---|---|---|
| 1 | Pročišćeni tekst odredbi za provođenje **PPUG-a Krk** (SN 7/07, 41/09, 28/11, 23/15, 18/19) | čl. 4.–173. (170 naslova) | Klasa 350-03/16-01/02, Ur. broj 2142/01-01/3-20-124 | uvjeti za **obiteljsku kuću** (22.) i **višeobiteljsku kuću** (23.) |
| 2 | Pročišćeni tekst odredbi za provođenje **UPU-a 1 – Krk** (NA1, R1₁, R3₈, R3₁₀, R3₁₁) | čl. 1.–150. (156 naslova) | Klasa 350-03/16-01/02, Ur. broj 2142/01-01/3-20-125 | razvrstavanje gospodarskih građevina (22.) i zona T1₁ (23.) |

Za PPUG Krk mjerodavno je **prvo pojavljivanje** (dio 1). `citac_tekst.py` sada prepoznaje više akata po ponovnom početku numeracije. Bez izričitog odabira dijela vraća `ABSTAIN_VISE_AKATA` s popisom dijelova; dio se bira opcijom `--dio`.

## Što treba
Izvorni HTML s točnim bajtovima, SHA-256 `f67ac384…`. Mogući putovi:
- izvorna datoteka iz v0.25.0, prenesena kao binarna (npr. preimenovana u `.bin` ili sažeta `.gz`);
- ponovni dohvat stranice <https://www.sn.pgz.hr/default.asp?Link=odluke&izdanje=2155&mjesto=51500&odluka=56> s preglednika na računalu, bez »spremi kao« pretvorbe kodne stranice.

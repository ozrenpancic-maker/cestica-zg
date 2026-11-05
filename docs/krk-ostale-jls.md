# Omišalj, Dobrinj i Vrbnik 2024. u aplikaciji

Stanje 5. 11. 2026., grana `krk-ostale-jls`. Nije spojeno u `main`.

Time sve jedinice na otoku Krku imaju uvjete gradnje iz prostornog plana općine ili grada. UPU-ovi izvan Grada Krka i Punta i dalje nisu obrađeni: kad evidencija planova pokaže važeći UPU, aplikacija javlja da uvjete propisuje taj plan.

Tekstovi su čitani u pregledniku na Ozrenovom računalu. Iz radnog okruženja Službene novine PGŽ nisu dostupne. Pravna provjera svih triju jedinica je NIJE_POTVRDENO, pa su pokazatelji uvjetni.

## Omišalj

**Izvor:** PPUO Omišalj, lanac objava 52/07, 33/09, 14/10, 37/11, 19/13, 43/14 (pročišćeni tekst), 17/15 i 9/17, prema popisu u odluci SN 31/2020.

**Članci:** čl. 44.a i 44.b iz izmjena SN 19/2013 i čl. 45. iz SN 19/2013 s izmjenama SN 9/2017.

**Tablica čl. 45. t. 1:** u izdanju 9/2017 tablica je samo slika u PDF-u. Prepisana je sa slike:

| | čestica min/max | kig min/max | od međa / od ceste |
|---|---|---|---|
| samostojeće | 250/2000 m² | 0,15/0,35 | 4/4/4/6 m |
| poluugrađene | 250/600 m² | 0,15/0,5 | 4//4/6 m |
| u nizu | 150/400 m² | 0,2/0,5 | 4/6 m |

**Ostale vrijednosti:**
- kis 0,6 (samostojeće i poluugrađene), odnosno 0,8 (niz);
- najviše 250 m² pod građevinom, najmanje 60 m²;
- podrum ili suteren i 2 nadzemne etaže;
- visina 9 m, a u zoni reducirane visine (kartografski prikaz br. 3) 7 m;
- zelenilo 30 %;
- od ceste 6 m, iznimno 4 m; od međa iznimno 3 m;
- obiteljska građevina do 400 m² GBP-a, višeobiteljska do 600 m², s pomoćnim građevinama.

**Ograničenja:**
- nova poluugrađena kuća gradi se samo kao druga polovica dvojne, a kuća u nizu samo kao interpolacija;
- neposredno se gradi samo u izgrađenom i uređenom dijelu GP-a.

**Nije provjereno:**
- pročišćeni tekst 43/2014 (na mreži nije cjelovit);
- tablica iz 2013. (na mreži je nema, ali ju je 2017. zamijenila nova).

## Dobrinj

**Izvor:** PPUO Dobrinj, SN PGŽ 24/2008 s ispravkom 7/2009. Usklađenje iz 2020. (38/2020) stavljeno je izvan snage (44/2020). Usklađenje sa Zakonom iz 2022. (Službene novine Općine Dobrinj 5/2022) nije pregledano.

**Vrijednosti (čl. 34.–71.):** individualna stambena građevina do 3 stana i 450 m² GBP-a.

| | najmanja čestica (širina) | najveća čestica | kig | kis |
|---|---|---|---|---|
| samostojeća | 400 m² (14 m) | — | 0,25, a na čestici većoj od 500 m² 0,30 | 0,75 |
| dvojna | 300 m² (11 m) | 500 m² | 0,30 | 0,9 |
| niz | 250 m² (8 m) | 300 m² | 0,30 | 0,9 |

Ostalo:
- visina 8,5 m, najviše P+2;
- najmanji tlocrt 64 m²;
- od međa 3 m;
- od razvrstane ceste 6 m, od nerazvrstane 5 m;
- zelenilo 30 %;
- krov dvostrešni ili od više ploha, nagib 20–23° (ide u simulator);
- neposredno se gradi samo u izgrađenom dijelu, na česticama i cjelinama manjim od 5000 m².

**Novo u kodu:** `izgVelika` i `krkIzg`, tj. kig koji ovisi o površini čestice.

## Vrbnik

Pravila su bila iz pročišćenog teksta iz 2019. Sada su iz pročišćenog teksta SN 11/2020 (iste vrijednosti), uz V. izmjene i dopune SN 34/2024, čl. 13.–17., primijenjene ručno:

- od nerazvrstane, lokalne i županijske ceste 4 m (prije 5 m);
- na kosom terenu (> 12 %) 3 nadzemne etaže, jedna obvezno suteren, i najviše 9,5 m (prije 10,5 m);
- dvojna kuća: najveći tlocrt 100 m² na čestici, najviše jedan stan u svakoj polovici;
- na česticama većim od 1500 m² prizemlje do 350 m² (prije: većim od 2000 m², do 250 m², samo u drugom redu);
- krov kosi 17–22°, bez atike (ide u simulator);
- nizovi i višeobiteljske građevine brisani.

Novi pročišćeni tekst nije pronađen u Službenim novinama PGŽ. Odluka o transformaciji plana (39/2024) ne mijenja odredbe.

## Testovi

`tests/run.js`: 1118 / 1118.
- Novi testovi za Omišalj i Dobrinj: izračun, neizgrađeni dio, kig ovisan o površini.
- Izmijenjeni testovi za Vrbnik.
- Provjera da je svaka brojka u svom doslovnom navodu.
- Sažetak (sha256) ostatka `rules_krk.json`: dokazano je da su stari i novi sadržaj isti bez triju izmijenjenih jedinica.

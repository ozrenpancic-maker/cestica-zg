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

## UPU-ovi u ostalim jedinicama (u tijeku)

Popis važećih UPU-ova na Krku dohvaćen je iz evidencije planova PGŽ (IZRADA_PP, 78 zapisa) 5. 11. 2026.

**Obrađeno:** UPU 9 Stara Baška (Punat, SN 21/2016), čl. 46.
- Zone: M-1 (nova gradnja) te S-P i M-P (interpolacija).
- Najmanja čestica: 450 m² (samostojeća), 225 m² (dvojna i završna jedinica niza), 150 m² (jedinica niza).
- kig 0,25 / 0,3 / 0,4, uz najveći tlocrt 150 m²; kis 0,75 / 1,0 / 1,4.
- Visina 9,0 m; 4 nadzemne etaže, od kojih je četvrta potkrovlje.
- Od međe h/2, najmanje 3 m; od ceste 6 m ili 5 m; zelenilo 40 %.
- Stavak 1. čl. 46. u mrežnom tekstu nedostaje.

**Obrađeno:** UPU 1 Vrbnik (pročišćeni tekst SN 11/2019 s izmjenama SN 34/2024, primijenjenima ručno), čl. 16., 19., 27. i 83.
- Zone: M1-1 i M1-2.
- Najmanja čestica: 400 m² (samostojeća), 300 m² (dvojna); najveća čestica više nije propisana.
- Tlocrt: 80 m² (samostojeća) ili 60 m² (dvojna) do 200 m²; na čestici većoj od 1500 m² prizemlje do 350 m².
- kig 0,30 / 0,40; kis nadzemno 0,60 / 0,80.
- Visina 6,5 m, a na kosom terenu 9,5 m.
- Od međe h/2, najmanje 4 m; od ceste 4 m; zelenilo 20 %; krov 17–22°.
- Nizovi i višeobiteljske zgrade brisani su 2024. Pročišćeni tekst SN 46/2024 nije pregledan.

**Bez stambene gradnje (provjereno u tekstu):** UPU 23 Torkul (čl. 18.) i UPU 26 Dunat (čl. 49.). Oni nisu u građevinskom području naselja, pa aplikacija već javlja da uvjeti za kuće ondje ne vrijede.

**Ostaju:**

| UPU | Stanje |
|---|---|
| UPU 3–9 u Baški | U mrežnom tekstu nema tablice veličine i izgrađenosti čestice (čl. 14.), a PDF-a nema; treba PDF ili elaborat sa zavod.pgz.hr. |
| UPU 1 Baška i UPU 2 Baška–Zarok | Pročišćeni tekst SN 6/2018. |
| UPU 1 Malinska, Radići | SN 14/2013 + izmjene 2014., 2015., 2017. |
| UPU 3 Dobrinčevo i UPU 4 Rova | SN 7/2012 i 12/2012. |
| UPU 2 Njivice i UPU Njivice – naselje | SN 38/2025 (pročišćeni tekst) i SN 12/2022. |
| UPU 2, 7 i 11 Risika | Vrbnik, 2009. |

## Primorsko-goranska županija: prostorni planovi gradova i općina

Redoslijed prema Ozrenovu izboru (5. 11. 2026.): najprije obala i otoci, pa zaleđe i Gorski kotar; prvo PPU svih mjesta, UPU-ovi poslije. Popis jedinica i zadnje glasilo plana iz županijskog sloja namjene (atribut IZVOR_PODATAKA).

| Jedinica | Stanje |
|---|---|
| Opatija | Obrađeno uz upozorenje: PPUG, pročišćeni tekst SN 8/2016 + III. izmjene SN 10/2021, čl. 20., 23., 24. i 125. Samo samostojeća kuća (nove dvojne samo kroz UPU, ugrađene samo rekonstrukcija); čestica 600 m², kig 0,3, kis nadzemni 0,9, visina 9 m (ukupna 11 m), od međa 4 m, od ceste 6 m, zelenilo 50 %. Oznake točaka čl. 24. u odluci iz 2021. ne podudaraju se s pročišćenim tekstom. |
| Rab | Obrađeno uz upozorenje: PPUG, pročišćeni tekst SN 15/2025 (PDF Zavoda), čl. 18.–23.: samostojeća 500 m² (širina 16 m), kig 0,3, kis 1,2, tlocrt 64–200 m², GBP manji od 400 m²; dvojna 400 m², kig 0,4, do 120 m²; niz 200 m², kig 0,45, do 100 m²; visina 9 m (niz 6 m); h/2, najmanje 3 m od međe; zelenilo 20 %. Udaljenost od ceste nije pronađena. |
| Lovran | U radu: osnovni tekst (2009., 2011.) + II. izmjene 2020. (Zavod, id 1431); neposredna gradnja uglavnom samo interpolacija i rekonstrukcija (čl. 14. i 18.a). |
| Novi Vinodolski | Obrađeno uz upozorenje: PPUG, pročišćeni tekst SN 18/2025 (PDF Zavoda, id 1813), čl. 25.–29.: kuća do 3 stana; samostojeća 400 m² (u neizgrađenom dijelu širina 14 m), kig 0,3 (0,4 u izgrađenom dijelu sjeverno od D8), kis 1,5 (2,0 iznad D8), tlocrt najmanje 60 m²; poluugrađena i niz 200 m², kig 0,4, kis 2,0, samo uz postojeću poluugrađenu ili prema UPU-u; visina 11,5 m (zona 1.1 NA11: 8,5 m); h/2, najmanje 4 m od međe (bez otvora 3 m). Položaj prema D8 aplikacija ne zna, pa računa s nižim vrijednostima. Udaljenost od ceste i zelenilo nisu pronađeni. |
| Crikvenica | Obrađeno uz upozorenje: PPUG, pročišćeni tekst nakon IX. izmjena (2024., PDF Zavoda, id 1804), čl. 16., 19., 27.–31. i 127.: kuća do dva stana; samostojeća i dvojna 400 m² (postojeće čestice u izgrađenom dijelu 360 m²), kig 0,3, kis 1,2, tlocrt najmanje 80 m² (dvojna 60 m²); niz samo kao interpolacija; visina 7 m, ukupna 10 m; h/2, najmanje 4 m od međe (bez otvora 3 m); od ceste 5 m (razvrstane 6 m); zelenilo 20 %; krov 17–23° ili ravni. Broj etaža plan ne propisuje. |
| Mali Lošinj | Obrađeno uz upozorenje: PPUG, pročišćeni tekst SN 25/2015 (PDF Zavoda, id 1251) + Ciljane VI. izmjene SN 32/2016 (izmjene čl. 52. i 54.), čl. 52.–61.a. Neposredno samo u izgrađenom dijelu naselja, a u naseljima Mali Lošinj i Osor samo u izdvojenim dijelovima. Kuća do 3 stana; čestica 400 / 300 / 200 m² (samostojeća / dvojna / niz), najviše 2000 m²; kig 0,3 / 0,35 / 0,5; kis 0,6 / 0,7 / 1,0 (s tavanom 0,9 / 1,05 / 1,5); tlocrt do 150 m² (prizemnica 200 m²); podrum, dvije etaže i tavan, visina 6,5 m; od međe h/2, najmanje 4 m (dvojna 5 m); građevni pravac 5–15 m; zelenilo 20 %; krov 23°. VII. izmjene su u izradi; odluka o donošenju nije pronađena. |
| Mošćenička Draga, Kostrena, Bakar, Kraljevica, Lopar, Cres | sljedeće (popis tekstova u `docs/pgz-registar-zzpu.md`) |
| Rijeka (GUP), Matulji, Kastav, Viškovo, Čavle, Jelenje, Klana, Vinodolska općina, Gorski kotar | poslije |

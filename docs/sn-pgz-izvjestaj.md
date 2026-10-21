# Baza pravila iz Službenih novina PGŽ: istraživanje i prototip (UPU 3 Punat)

Stanje 21. 10. 2026., grana `razvoj`. Kalkulator gradnje i aplikacija nisu mijenjani. Prototip: `tools/sn-pgz/`, podaci: `data/pravila-sn/punat-upu3.json`.

## 1. Dostupnost i uvjeti korištenja
- Odluke su javno dostupne kao HTML: `https://www.sn.pgz.hr/default.asp?Link=odluke&id=NNNNN`; uz neke postoji PDF `download.asp?id=NNNNN` (npr. 31026 za II. izmjene UPU 3).
- Impressum kaže samo da je to „službeno glasilo Primorsko-goranske županije”; podnožje: „© Primorsko-goranska županija 2002.–2003., sva prava pridržana”. Nema uvjeta o ponovnoj uporabi ni o automatiziranom pristupu. Meta oznake: `ROBOTS INDEX, FOLLOW`. `robots.txt` nisam mogao pročitati (alat ga nije smio dohvatiti), pa ga skripta provjerava pri svakom pokretanju.
- Zaključak: umjeren dohvat izričito zadanih ID-ova je opravdan (skripta: 1 zahtjev u 2 s, predmemorija, jasan User-Agent s kontaktom). Zbog „sva prava pridržana” cijeli tekst odluka ne objavljujemo u repozitoriju; čuvamo kratke citate, poveznice, članak, glasilo i SHA-256 teksta. Preporuka: prije šireg rada pisati na `sn.pgz@novilist.hr` / `sluzbene.novine@pgz.hr` i pitati o uvjetima i o strojno čitljivom izvozu.
- Ograničenje okruženja: iz razvojnog okruženja sn.pgz.hr nije dostupan (shell), a alat za čitanje stranica vraća sažetak modela, ne doslovni tekst. Zato je mrežni dio skripte (`sn_pgz.py fetch`) pisan za pokretanje na tvom računalu; razdvajanje i provjera rade nad tekstom koji si priložio.

## 2. Pronalaženje svih odluka za jedan UPU
Pretraga sn.pgz.hr (`Link=query&search=…`) vraća do 8 pogodaka bez straničenja i **nije potpuna**: upit „Punat” i „Punat tumačenje” dali su isti popis od 8 redaka (7 za Punat, 1 za Vrbnik). Nema izmjena iz 2016. (SN 13/16), vjerodostojnog tumačenja ni izmjena PPUO iz 2015. (SN 14/15). Ti ID-ovi koje si naveo (33933, 26150) ne vraćaju odluku nego popis pretrage. Zato je pouzdan put:
1. Plan iz evidencije PGŽ (`IZRADA_PP`: `NAZIV`, `SN_BROJ`, `SN_LINK`, `PDF_LINK_PUBLIC`) daje početnu odluku.
2. Registar ZZPU (zavod.pgz.hr) daje popis svih planova i glasila po općini.
3. Tekst svake odluke navodi prethodne (UPU 3 iz 2020.: „br. 34/10 i 13/16”); lanac se prati unatrag dok se ne dođe do osnovne odluke.
4. Pretraga sn.pgz.hr služi samo kao dopuna, nikad kao dokaz potpunosti.

## 3. Vrste odluka (`sn_pgz.vrsta`)
`izrada` (postupovni akt, bez uvjeta; npr. 38031, 41977), `donosenje`, `izmjene` (izmjene i dopune, ciljane izmjene), `procisceni` (pročišćeni tekst, to je jedino mjesto s cjelovitim stanjem), `izvan_snage`, `tumacenje`. Određuje se po naslovu, a nerazvrstano ostaje `nepoznato` i traži ručni pregled. Odluka o izradi nikad ne nosi pravila (čl. 13. odluke 41977: do izmjena vrijedi važeći UPU).

## 4. Pohrana pravila (`shema.json`)
Jedna datoteka po planu. Dijelovi: `plan`, `odluke[]` (id, vrsta, glasilo {broj, godina, datum, stavka}, url, pdf, status, sha256, `dohvaceno`), `pravila[]`, `otvorena_pitanja[]`.
Pravilo: `zona {oznaka, potvrda}`, `parametar` (kig_max, kis_max, visina_max, etaze_nadzemne_max, tlocrt_min/max, cestica_min/max, odmak_*, zelenilo_min, parkiranje_po_stanu, stanovi_max…), `vrijednost`, `jedinica`, `vrsta_gradnje`, `uvjet` (npr. čestica > 1000 m², izgrađeni dio, konkretna k.č. za iznimke), `izvor {odluka_id, clanak_odluke, clanak_plana, stavak, tocka, citat, url}`, `vazi_od/do`, `verzija`, `status_primjene`, `provjera {razina, datum, tko}`.
Svako pravilo ima doslovni citat; `provjeri_citate.py` provjerava da se citat nalazi u izvornom tekstu odluke. Razine provjere: strojno → strojno + citat pronađen → ručno → dvostruko ručno. Aplikacija smije koristiti samo razinu koju mi odredimo.

## 5. Provjera izvora uz svako pravilo
Ispunjeno: izvorni URL, članak odluke i članak plana, stavak/točka, broj glasila i datum (u `odluke`), verzija, status provjere, SHA-256 teksta. Datum stupanja na snagu izračunat je iz čl. 40. („osmog dana od dana objave”).

## 6. Povezivanje s obuhvatom i zonom
- **Plan ↔ lokacija:** `IZRADA_PP` na točki daje plan i `SN_LINK`/`PDF_LINK_PUBLIC`; iz njih se čita id/`izdanje+odluka` odluke (spoj s bazom). Spoj ide preko `SN_BROJ` i naziva, ne samo naziva.
- **Zona:** u županijskom sloju `NAMJENA_POVRSINA_NOVO` polje `OZNAKA_NAMJENE` postoji, ali nije potvrđeno odgovaraju li te oznake zonama UPU-a (S1, S2, M1, M2…) ili samo PPUO/G-u. Za to je pripremljena dijagnostika: https://ozrenpancic-maker.github.io/cestica-zg-proba/pgz-upu-test.html (ispiše sva polja oba sloja na točki; pokreni na točkama u središtu Punta).
- Zonu primjenjujemo tek kad je `potvrda` = `sloj_gis` (oznaka sloja izričito povezana s legendom UPU-a), `geometrija_plana` (poligon zone iz plana) ili `korisnik` (korisnik je izabrao uz pregled karte). Naziv UPU-a ni boja na rasteru nisu dovoljni.

## 7. Što je pronađeno za UPU 3 Punat
| Odluka | Vrsta | Glasilo | Stanje |
|---|---|---|---|
| ID 20518 | donošenje UPU 3 | SN 34/2010, 23. 8. 2010., st. 44 | pročitano samo preko sažetka; nije doslovno |
| (nepoznat ID) | izmjene SN 13/16 | SN 13/2016 | **nije pronađena**; ID 33933 ne radi |
| ID 26150 | tumačenje 2012. | — | **nije pronađeno** |
| ID 38031 | odluka o izradi II. izmjena | SN 37/2018, 27. 11. 2018. | postupovna |
| ID 41087 | II. izmjene i dopune | SN 3/2020, 14. 2. 2020., st. 5 (PDF 31026) | cijeli tekst (priložio si); na snazi od 22. 2. 2020. |
| ID 41977 | odluka o izradi III. izmjena | SN 33/2020, 2. 10. 2020., st. 60 | postupovna; izmjene nisu donesene |
| registar ZZPU | izmjene UPU 3 u izradi | SN 2025-37 | nova izmjena može uskoro promijeniti uvjete |

## 8. Što se može izdvojiti i što je problematično
Odluka 41087 ima 40 članaka. Strojna analiza (`sn_pgz.py analiziraj`) razvrstava njezine operacije po članku plana: 7 članaka zamjenjuje cijelim tekstom (28a, 44, 46, 48, 85, 99, 99e), 1 briše (100), a **25 su djelomične izmjene** (npr. „u čl. 46a. st. 1. toč. 4. mijenja se…”) čiji osnovni članak nije u priloženom tekstu.
Iz 41087 je izdvojeno **20 pravila s doslovnim citatom** (tlocrt 150/75/200 m² i najmanje 60 m² iz čl. 46; zelenilo 40/30/20 % iz čl. 46a/46b/46c; višestambena kig 0,25, kis 1,25, P+2, visina 9,0/7,0 m, tlocrt 80–250 m², 4 stana, zelenilo 30 % iz čl. 50a; bazen 100 m²; interpolacija na česticama 10 % manjim; iznimka za k.č. 3307; rampa 4 m). Svih 20 citata automatski je provjereno u stvarnom tekstu odluke.
Problematično:
- **Čl. 46a–46c** (obiteljske kuće): izmjene 2020. mijenjaju samo točke 4, 6 i 8; najmanja čestica, kig, kis, visina i etaže stoje u osnovnom tekstu iz 2016. koji nemamo. Ne može se izračunati obiteljska kuća.
- Vrsta gradnje za 46a nije izričito navedena (46b je dvojna, 46c niz); 46a je pretpostavka dok se ne vidi osnovni tekst.
- Ostalo (čl. 45, 50d, 85a–d…) isto djelomične izmjene bez osnove.
- Ugniježđeni navodnici i brojevi kao „28.a”/„50.d” u izvornom tekstu; parser ih normalizira.
- Zone se razlikuju između 2010. (S-P, S4, S1-P) i 2020. (S1, S2, M1, M2, tipologija OB/VS); stari tekst se ne smije miješati s novim bez provjere.

## 9. Kako bi izgledala integracija
1. **Prikupljanje (izvan aplikacije):** skripta na računalu s pristupom dohvaća zadane ID-ove, razdvaja vrste i članke, izrađuje lozu članaka (koji članak je cijeli tekst, a koji djelomična izmjena) i predlaže kandidate (`kandidati`, status „strojno”).
2. **Pregled čovjeka:** kandidat postaje pravilo tek s doslovnim citatom i provjerom (`provjeri_citate.py`); zona i uvjeti upisuju se ručno; dvostruka provjera za brojke koje ulaze u izračun.
3. **Objava:** JSON baza po planu u `data/pravila-sn/`; plan je `primjenjivo` samo kad su poznati osnovni tekst i sve izmjene do danas, i kad je zona potvrđena.
4. **Aplikacija:** postojeći mehanizam `rules_krk.json` (`upu`, zone koje korisnik bira) kasnije čita iz ove baze; do tada je kalkulator nepromijenjen. Prikaz uz svaku vrijednost: članak, glasilo, datum i razina provjere (kao oznake pouzdanosti A/B/C).
5. **Održavanje:** registar ZZPU i `IZRADA_PP` služe za otkrivanje novih izmjena; baza pamti SHA-256 pa se promjena teksta uoči.

## 10. Sljedeći koraci
1. Dobiti SN 13/16 (UPU 3 izmjene) i tumačenje iz 2012. (točan ID ili PDF) i ponovno pokrenuti analizu: tada se mogu zatvoriti 46a–46c.
2. Pokrenuti dijagnostiku zona na 3–4 točke u Puntu i zaključiti postoje li oznake UPU zona u županijskom sloju.
3. Pitati Službene novine o uvjetima ponovne uporabe i izvozu.
4. Tek nakon toga odlučiti o prebacivanju kalkulatora na ovu bazu.

# Katalog montažnih kuća

Stanje 5. 11. 2026., grana `montazne-kuce`. Nije spojeno u `main`.

## Što radi

U simulatoru kuće je gumb **Montažne kuće → Katalog (27 modela)**. Katalog ima tri kartice, svaka s 9 modela:

- Prizemnice
- Katnice
- S potkrovljem

Svaki model ima:
- objavljene podatke;
- ocjenu za odabranu česticu: *stane prema objavljenim podacima*, *moguće, provjeri u simulatoru*, *ne stane* ili *bez usporedbe*;
- razloge ocjene;
- poveznicu na stranicu proizvođača;
- gumb **Postavi u simulator**.

Gumb **Postavi u simulator** postavlja etaže, krov i nagib te procijenjeni tlocrt. Nakon toga sve provjere simulatora (međe, tlocrt, GBP, etaže, visina, krov) rade nad tim modelom. Ručna promjena širine, dubine ili etaža odvaja kuću od modela.

Novi izbornik **Izgled u 3D** nudi tri izgleda:
- klasični;
- moderni: bijela žbuka, antracitni krov i okviri, visoki prozori;
- moderni s drvenom oblogom: drvena obloga na katu, a kod prizemnice na istočnom dijelu kuće.

Izgled je samo ilustracija i ne utječe na provjere. Kad se model postavi u simulator, a izgled je bio klasični, prelazi na moderni (ravni krov) ili na moderni s drvom (kosi krov).

## Podaci

Datoteka `src/montazne_kuce.json` gradi se skriptom `tools/montazne/gradi_katalog.py`. Vrijednosti su prepisane sa stranica proizvođača 5. 11. 2026.

| Proizvođač | Što objavljuje | Modeli u katalogu |
|---|---|---|
| Partas | neto i bruto površina, broj soba, visina zgrade, najmanja širina i duljina zemljišta, vrsta i nagib krova | Q 405, 410, 400, 520, 140, 120 (prizemnice); Q 210, 220, 230, 250, 300 (katnice) |
| Domprojekt | neto površina, broj spavaćih soba, kategorija (prizemna, katna, s potkrovljem) | Nives, Marinela, Ingrid; Elena, Gloria; Alma, Venera, Doris, Leonida, Ema, Renata, Emanuela, Lena, Laura |
| Icon Group | bruto površina, vrsta i nagib krova; etaže iz naziva tlocrta (»Prizemlje«, »Kat«) | Lina, Petra (katnice) |

**Vanjske mjere tlocrta (širina × dužina) ne objavljuje nijedan od tri proizvođača.** Nema ih ni u katalogu Domprojekta (PDF), ni u brošuri Icona za model Astra, ni na stranicama Partasa. Zato se u katalog ne upisuju. Simulator tlocrt procjenjuje iz površine, kao i kod predloška: površina se dijeli s brojem etaža (potkrovlje kao 75 %), uz omjer stranica oko 4 : 3. Ta procjena je u napomeni jasno označena kao PROCJENA.

Etaže modela:
- **Domprojekt:** kategorija s njegove stranice.
- **Icon:** nazivi tlocrta na stranici modela.
- **Partas, katnice:** opis modela (»prizemlje i kat«).
- **Partas, prizemnice:** stranica ne navodi etaže. Šest modela svrstano je u prizemnice jer je visina zgrade od 3,95 do 5,48 m premala za dvije etaže. To je u katalogu označeno kao »izvedeno«.

Modeli Partasa kod kojih etaže nisu navedene, a visina od 6,5 do 8,2 m dopušta oba tumačenja, nisu uvršteni (Q 110, 500, 515, 525, 620, 640).

Nisu preuzeti:
- fotografije i tlocrti (autorska prava);
- cijene.

## Usporedba s česticom

Uspoređuje se samo ono što je objavljeno:

- **Etaže:** prema planu; potkrovlje se broji kao etaža.
- **GBP:**
  - kad je objavljena bruto površina, uspoređuje se s najvećim nadzemnim GBP-om;
  - kad je objavljena samo neto površina, model *ne stane* ako je već neto površina veća od dopuštenog GBP-a, a inače je *moguće, provjeri*.
- **Tlocrt:**
  - kao donja granica uzima se površina podijeljena s brojem razina;
  - ako je i ta granica veća od dopuštenog tlocrta, model *ne stane*;
  - kod prizemnice s bruto površinom tlocrt je bruto površina;
  - inače je ocjena *moguće, provjeri*.
- **Visina (Partas):** uspoređuje se s visinom iz plana. Ako je veća, javlja se samo upozorenje, jer proizvođač ne navodi mjeri li visinu do vijenca ili do sljemena.
- **Zemljište (Partas):** najmanja širina i duljina zemljišta koje traži proizvođač uspoređuju se s najmanjim pravokutnikom u koji stane čestica.
  - Ako je čestica uža ili kraća, model *ne stane*.
  - Ako nije, oblik čestice treba provjeriti u simulatoru.

Bez izračunatih uvjeta gradnje usporedbe nema.

## Testovi

`tests/run.js`, `montazneTests` (24 nova testa):
- sastav kataloga;
- vrijednosti sa stranica proizvođača;
- nema vanjskih mjera;
- pravokutnik čestice;
- sedam slučajeva usporedbe;
- sučelje;
- postavljanje u simulator i napomene;
- spremanje;
- izgled u 3D.

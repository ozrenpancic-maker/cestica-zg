# Iskop i nasip za plato kuće

Stanje 24. 10. 2026., grana `razvoj`.

## Gdje je

Odjeljak „Iskop i nasip za plato kuće” stoji ispod simulatora kuće. Radi u svim prikazima (Zagreb, Krk, PGŽ, ostatak Hrvatske) čim je kuća postavljena u simulatoru. U zagrebačkom prikazu rezultat se gumbom upisuje u „Pripremu terena”, pa ulazi u ukupnu investiciju.

## Što se računa

**Plato**
- Ravna ploha: tlocrt kuće (i garaže) uvećan za radni pojas oko kuće. Pojas je zadano 1 m, a može se upisati od 0 do 10 m.

**Kota platoa** (izbor)
- ravnoteža iskopa i nasipa (zadano; uključuje pokose);
- sve u iskop: plato na najnižoj točki terena;
- sve u nasip: plato na najvišoj točki terena;
- ručni upis kote.

**Iskop i nasip na platou**
- Teren se uzorkuje u mreži 0,25 m. Teren iznad platoa je iskop, a teren ispod platoa nasip.

**Rub platoa**
- Pokos iskopa 1 : 1, nasipa 1 : 1,5. Obujam pokosa je h²/2 × nagib × duljina ruba. Kutovi pokosa nisu uračunati, pa je rezultat malo podcijenjen.
- Ako je rub viši od 1 m, predlaže se potporni zid (duljina i prosječna visina). Ako se zid uključi, ondje se pokos ne računa.

**Ostali rezultati**
- Višak ili manjak materijala. Odvoz se računa s rastresitošću 1,25 i kamionom od oko 10 m³.
- Visinska razlika terena ispod kuće.
- Podrum: jama ispod platoa prikazuje se posebno (tlocrt × (visina etaže + 0,5 m)) i ne ulazi u iskop platoa. U procjeni gradnje je stavka 2a.
- Presjek (SVG) kroz sredinu kuće u smjeru najvećeg pada terena: teren, plato s pokosima, kuća, iskop i nasip, u mjerilu 1 : 1.

Pokosi, prag za zid, rastresitost i kamion su pretpostavke aplikacije, a ne propis. U sučelju su označeni kao pretpostavke.

**Bez dvostrukog brojanja**
- Humus i tampon ispod kuće ostaju u fazi 1 procjene gradnje („Iskop i nasip za temelje”).
- Ovdje se računa samo poravnavanje terena na plato.

## Izvor terena, redom

1. **Izmjerene visine 4 kuta kuće.** Korisnik ih upisuje relativno (npr. geodet, laserska ili cijevna libela). Između kutova teren je bilinearan. Pouzdanost **B**.
2. **Mapterhorn**, `tiles.mapterhorn.com/{z}/{x}/{y}.webp`: Terrarium kodiranje, 512 px, prvo z15, zatim z12.
   - Nije provjereno iz razvojnog okruženja (nema mreže): ima li za Hrvatsku podatke na z15 i dopušta li preglednik čitanje (CORS).
   - Izvori podataka za Hrvatsku nisu potvrđeni; popis je na mapterhorn.com/attribution.
3. **AWS Terrain Tiles** (Mapzen), `s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png`: 256 px, z15. Za Europu uključuje EU-DEM (oko 30 m).
4. **Ravnina iz nagiba okoline** (Copernicus DEM preko Open-Meteo, oko 90 m), kad pločice nisu dostupne.

Pouzdanost modela 2–4 je **C**: ne vidi terase, suhozide, stijene ni nasipe na samoj čestici. U sučelju piše koji je izvor korišten, s veličinom piksela.

Postavke (način, kota, pojas, zid, kutovi) pamte se po čestici u `localStorage` pod ključem `isk`.

## Testovi

`tests/run.js`, skupina `iskTests`. Provjeravaju:
- Terrarium dekodiranje;
- ravninu 10 % ispod kuće 10 × 10 m: 12,5 m³ iskopa i nasipa i ručno izračunate pokose;
- ravnotežu kote i načine „sve u iskop” i „sve u nasip”;
- radni pojas, garažu i prijedlog potpornog zida;
- izmjerene kutove i zamjenu izvora (Mapterhorn → AWS) s lažnim pločicama;
- prikaz, pouzdanost C i B, pamćenje postavki i upis u Pripremu terena.

## Za provjeru na stvarnom uređaju

Otvoriti česticu na kosom terenu (npr. Kornić) i u odjeljku vidjeti koji je izvor naveden.
- **Mapterhorn ili AWS:** pločice rade.
- **Open-Meteo:** pločice preglednik nije mogao pročitati.

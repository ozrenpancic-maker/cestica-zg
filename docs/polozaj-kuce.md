# Prijedlog položaja kuće i mjerenje visina kroz kameru

Stanje 24. 10. 2026., grana `razvoj`.

## 1. Prijedlog položaja (gumb „Predloži položaj” u simulatoru kuće)

**Što ostaje, a što se mijenja**
- Kuća zadržava dimenzije, etaže, krov i garažu iz simulatora.
- Mijenjaju se samo položaj i okret.

**Kandidati**
- Položaj: mreža 1 m. Ako je okvir dopuštenog prostora veći od 2.500 m², mreža je 2 m.
- Okret: svakih 5° (180° za simetričan krov, 360° s garažom). Uz to i okreti usporedni i okomiti na stranice čestice dulje od 5 m.
- Kandidat vrijedi samo ako je cijela kuća (i garaža) unutar prostora za gradnju.
  - Prostor je zeleno područje simulatora; kad je poznat, bez pojasa uz ulicu do građevnog pravca.
  - Provjera: svi kutovi su unutra, nijedna stranica ne siječe rub i nijedan vrh ruba (ni rupe) nije unutar kuće.

**Kriteriji**
- **Zemljani radovi:** iskop + nasip za plato. Isti izračun kao „Iskop i nasip” (ravnoteža, pokosi, radni pojas iz postavki), ali na mreži 1 m. Teren dolazi iz modela visina, unaprijed uzorkovanog na 0,5 m.
  - Ako je teren samo ravnina (Open-Meteo), položaj ne mijenja količine, nego samo okret.
- **Sunce:** specifična proizvodnja panela na najboljoj plohi krova (kWh/kWp, satni podaci ERA5, isti model kao „Sunčana elektrana”).
  - Za prikazane prijedloge računa se i sjena okolnih zgrada.
  - Ravni krov: okret ne mijenja proizvodnju, pa nema prijedloga „najviše sunca”.

**Prijedlozi**
- **Najmanje zemljanih radova:** među kandidatima unutar 0,1 % (+0,1 m³) od najmanjeg, odlučuje sunce, zatim najmanji pomak od sadašnjeg položaja.
- **Najviše sunca:** među kandidatima unutar 0,05 % od najvećeg, odlučuju zemljani radovi, zatim najmanji pomak.
- **Kompromis:** najmanji zbroj normaliziranih zemljanih radova i manjka sunca, uz mali utjecaj pomaka.
- Isti kandidat pod više naziva prikazuje se jednom.

**Prikaz**
- Za svaki prijedlog: okret, pomak, m³ (± % prema sadašnjem), zid i kWh/kWp (± %).
- Gumbi „Postavi kuću ovdje” i „Vrati prethodni položaj”.
- Ako je dobitak manji od 5 % zemljanih radova i 1 % sunca, piše da je sadašnji položaj već blizu najboljeg.

**Što se ne uzima u obzir**
- Pristup s ceste, pogled, privatnost, okućnica, buka.
- Teren koji model ne vidi (terase, stijene, postojeći zidovi).

**Brzina:** na čestici od 1.280 m² oko 9.400 kandidata, 0,8 s u Chromiumu na računalu.

## 2. Mjerenje visina kutova kuće kroz kameru (AR)

**Pokretanje**
- Gumb „Izmjeri kutove mobitelom (AR)” u odjeljku „Iskop i nasip”, pod izmjerenim visinama kutova.
- U AR prikazu gumb „Mjeri visine kutova” prebacuje iz poravnanja u mjerenje, a „Poravnaj kuću” vraća natrag.

**Kutovi**
- Brojevi kutova jednaki su kao u izračunu iskopa: 1 = (−š/2, −d/2), 2, 3 i 4 redom oko kuće.
- Na skici je odabrani kut narančast, a izmjereni zeleni.
- Ako je kuća poravnata, na odabranom kutu stoji narančasti stup visok 2,5 m.

**Načini mjerenja**
- **Krug na tlu:** hit-test, točka na tlu u sredini slike. Traže se točke i plohe (`entityTypes: ["point","plane"]`), jer same plohe na kosom terenu mogu biti vodoravna procjena. Ako preglednik to ne podržava, koristi se zadani hit-test.
- **Visina mobitela (štap):** položaj mobitela iz praćenja. Na svakom kutu mobitel se drži na istoj visini, npr. na vrhu štapa ili letve. Ne ovisi o prepoznavanju tla.

**Rezultat**
- Visine su relativne prema kutu 1, pa se stalni pomak poništava.
- Razmaci između kutova uspoređuju se s kućom u simulatoru (upozorenje kod razlike veće od 0,5 m ili 10 %).
- Ponovno mjerenje istog kuta pokazuje razliku u cm (zanošenje praćenja).
- „Spremi u iskop” upisuje četiri visine u „Izmjerene visine kutova”, pa iskop prelazi na pouzdanost B.

**Ograničenja**
- Točnost ovisi o praćenju (ARCore): obično nekoliko cm na 10–15 m, ali više na jednoličnoj travi, u mraku i pri brzom hodu.
- Nije zamjena za geodetski snimak.
- Ne može se testirati bez ARCore uređaja; testirane su čiste funkcije (`arVisRel`, spremanje).

## Testovi

`tests/run.js`, skupina `optTests`. Provjerava:
- smještaj u prostor i rupe;
- kad teren pada prema istoku, najmanje zemljanih radova je uz okret 90°;
- kad Sunce dolazi s juga, najviše sunca je uz okret 0°;
- tri prijedloga, odnosno spajanje kad se poklapaju;
- prikaz, „Postavi” i „Vrati”;
- relativne visine i razmake;
- spremanje izmjerenih visina u iskop.

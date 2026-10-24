# Rizici, povijest lokacije i kuća kroz kameru

Stanje 24. 10. 2026., grana `razvoj`.

## 1. Rizici (odjeljak „Priroda i poplave”, kategorija 03)

### Opasnost od poplava (Hrvatske vode)

**Izvor**
- Servis: `https://servisi.voda.hr/poplave_opasnosti/wms`, karte opasnosti od poplava (NIPP, data.gov.hr).
- Scenariji: velika vjerojatnost (povratno razdoblje oko 25 godina), srednja (oko 100 godina) i mala (oko 1000 godina; uključuje rušenje nasipa i visokih brana), prema stranici Hrvatskih voda o kartama za 2019.

**Upit**
- Servis ne dopušta čitanje iz preglednika (CORS), pa upit ide preko posrednika: `worker.next.js`, `?poplave=<lat>,<lon>`. Koristi ga Deno; Cloudflare ga dobiva tek ručnom objavom.
- Nazivi slojeva nisu upisani u kod. Posrednik čita popis slojeva iz servisa (GetCapabilities, pamti ga 7 dana) i pita samo slojeve koji se smiju upitati, a uz to nose naziv scenarija.
- Pogodak se čita iz odgovora GetFeatureInfo (JSON, običan tekst ili GML). Rezultat po točki pamti se 7 dana.
- **Stvarni servis (provjereno na Denou 24. 10. 2026.):** ima četiri sloja (`hr.fd.opasnost-od-poplave-velika-vjerojatnost`, `…-srednja-…`, `…-mala-…` i zajednički `hr.fd.vjerojatnost-pojavljivanja`), a nijedan se ne smije upitati po točki. Zato posrednik za svaki od tri scenarija traži malu prozirnu sliku (GetMap PNG, 11 × 11 piksela, oko 1 m po pikselu) i provjerava je li sredina (3 × 3 piksela) obojena. Tako se dobiva samo da/ne po scenariju, bez dubine. PNG se čita u posredniku bez biblioteka.
- **Dijagnostika:** `?poplave=<lat>,<lon>&dijag=1` vraća i popis svih slojeva servisa.

**Prikaz**
- U području opasnosti: upozorenje, scenarij s povratnim razdobljem i svojstva sloja ako postoje (npr. dubina).
- Izvan područja opasnosti: oznaka „izvan”, uz napomenu da karte ne prikazuju sve scenarije.
- Pouzdanost je **B**, jer se pita jedna točka unutar čestice.
- Bez podataka: razlog, poveznica na preglednik Hrvatskih voda i pouzdanost **C**.

**Uvjeti korištenja**
- U registru NIPP: karte su izrađene u okviru Plana upravljanja rizicima od poplava i nisu prilagođene drugim namjenama; na kartama nisu prikazani svi mogući scenariji plavljenja; korisnik prihvaća rizike korištenja.
- Licenca na data.gov.hr nije navedena. **Otvoreno:** potvrditi s Hrvatskim vodama smije li se servis koristiti u aplikaciji.

**Provjera**
Popis slojeva provjeren je na Denou (`?poplave=…&dijag=1`). Čitanje slike treba još jednom provjeriti istim URL-om nakon objave; poznata točka u području opasnosti (npr. uz Savu) mora vratiti `pogodak: true`.

### Internet (HAKOM)

**Izvor**
- HAKOM eKarta, ArcGIS REST.
- `DOSTUPNOST_SPP/Dostupnost_SPP/FeatureServer`, slojevi 91–97: razredi brzine od „≥ 1 G do 10 G” do „≥ 0 MBit do 2 MBit”, polje `BrojOperatora`.
- `DOSTUPNOST_SPP/P/MapServer`, slojevi 98–99: pokretna mreža.
- Provjereno 24. 10. 2026. upitom po točki.

**Upit**
- Izravno iz preglednika. Ako preglednik ne smije čitati HAKOM izravno, upit ide preko posrednika (`?internet=<lat>,<lon>`).

**Prikaz**
- Najveći razred na točki i broj operatora.
- Brzina 30 Mbit/s ili više je „✓”, manja je upozorenje.
- Pouzdanost je **A** (točka unutar čestice).
- Stvarnu ponudu za adresu treba provjeriti kod operatera.

### Potresna opasnost

Ostaje skrivena (`FEATURES.seis=false`, odluka od 17. 10. 2026.). Službena karta nema javni upit po koordinati.

## 2. Povijest lokacije (snimke iz zraka)

**Izvor**
- DGU, digitalni ortofoto 1:5000.
- Uključeni su samo servisi „za anonimne korisnike” bez naknade: **2011.** (`orthophoto_2011/wms`, sloj `OrthoImagery`), **2021./22.** (`orthophoto_2021_2022/ows`) i **2023./24.** (`orthophoto_2023_2024/wms`), slojevi `OI.OrthoimageCoverage`.
- Snimci 2017./18., 2019. i 2019./20. traže registraciju i prihvaćanje uvjeta korištenja ili naknadu, pa nisu uključeni. Provjereno u GetCapabilities 24. 10. 2026.

**Prikaz**
- GetMap u CRS:84, kvadrat u metrima: čestica i najmanje 25 m okolice.
- Žuta granica čestice ucrtana je preko slike.
- Dva izbornika godine i klizač za usporedbu.
- Slike se učitavaju tek kad se odjeljak otvori.
- Napomena uz prikaz: usporedba ne dokazuje je li gradnja zakonita.

## 3. Kuća kroz kameru (AR)

**Gumb:** „Kuća kroz kameru (AR)” u simulatoru kuće.

**Uvjeti**
- WebXR `immersive-ar`: Android, Chrome i Google Play usluge za AR (ARCore).
- Na drugim uređajima prikazuje se poruka i ništa se ne pokreće.

**Prikaz**
- Granica čestice (žuto), prostor za gradnju (zeleno) i kuća iz simulatora (plavo) u stvarnoj veličini: zidovi do vijenca, krov sa sljemenom i garaža.
- Vlastiti mali WebGL prikaz, bez dodatnih biblioteka.

**Poravnanje**
- **Grubo:** prema GPS-u (±nekoliko metara) i kompasu (`deviceorientationabsolute`). Bez GPS-a kuća se postavlja 8 m ispred korisnika.
- **Točno:** krug na tlu (hit-test) usmjeri se na kut čestice na terenu, odabere se njegov broj na skici i dodirne „Ovo je kut”, za dva kuta. Iz njih se računaju zakret i položaj.
- Ako se udaljenost između označenih kutova razlikuje od katastra za više od 10 %, javlja se upozorenje.
- Fino ručno pomicanje: strelice po 0,5 m i zakret po 2°.

**Testovi**
- Testirana je matematika: preračun koordinata, poravnanje prema dvama kutovima, kompas i geometrija kuće. Testirana je i poruka bez podrške.
- Sam AR (kamera, praćenje) ne može se testirati u pregledniku bez ARCore-a. **Treba ga isprobati na mobitelu.**

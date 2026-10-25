# Izvoz za projektanta, kišnica i cisterna, energija kuće

Stanje 25. 10. 2026., grana `razvoj`. Sve je u naprednom načinu.

## 1. Izvoz za projektanta (simulator kuće, gumbi uz „Kuća kroz kameru”)

### DXF (`Izvoz DXF (HTRS96/TM)`)

**Format:** AutoCAD R12 (AC1009), ASCII, metri, EPSG:3765 HTRS96/TM (`tmFwd`).

**Slojevi**

| Sloj | Sadržaj |
|---|---|
| `CESTICA` | granica čestice |
| `PROSTOR_GRADNJE` | prostor za gradnju |
| `POJAS_ULICA` | pojas uz ulicu |
| `KUCA`, `GARAZA` | kuća i garaža |
| `PLATO` | plato iskopa s radnim pojasom, ako je izračunat |
| `UDALJENOSTI` | crta i tekst od sredine svake stranice kuće do granice |
| `TEKST` | k.č., k.o., grafička površina, kuća i kota platoa, izvor i datum |

**Ograničenja**
- Tekst je samo ASCII (č → c, đ → d), jer R12 nema UTF-8.
- Granica je grafički prikaz iz katastra (DGU), a ne geodetska podloga.

**Provjera:** `ezdxf` (recover.readfile) bez grešaka i popravaka. Koordinate za Krk su oko E 349 750, N 4 989 249.

### glTF 2.0 (`Izvoz 3D (glTF)`)

**Format:** jedna datoteka `.gltf` s ugrađenim međuspremnikom (base64), boje po vrhovima.

**Sadržaj**
- kuća s krovom i garaža (geometrija kao u AR prikazu, `arGeom`);
- granica čestice i prostor za gradnju (crte);
- teren iz modela visina oko čestice ± 10 m, ako je učitan u „Iskopu i nasipu”.

**Visine:** relativne prema tlu u sredini kuće. Kuća stoji na koti platoa.

**Koordinatni sustav:** lokalni metri, x istok, y gore, z jug. Ishodište u HTRS96/TM i WGS84 zapisano je u `asset.extras`.

**Provjera:** Khronos `gltf-validator` daje 0 grešaka i 0 upozorenja. Datoteka se ispravno prikazuje u three.js.

## 2. Kišnica i cisterna (04 Pristup i infrastruktura)

**Podaci:** Open-Meteo, dnevne oborine 2016.–2025. (ERA5 / ERA5-Land).

**Dnevna bilanca spremnika**
- Spremnik je na početku pun.
- Dotok = oborina × površina krova (tlocrt kuće i garaže iz simulatora ili upis) × koeficijent otjecanja (zadano 0,8, pretpostavka).
- Potrošnja = osobe × L po osobi na dan (zadano 4 × 50 L, pretpostavka) + dodatno ljeti (lipanj–rujan).

**Rezultati**
- za spremnike od 2 do 60 m³: prosječni dani bez vode godišnje, pokrivenost potrošnje i najdulji niz dana bez vode;
- preporuka: najmanji spremnik s najviše 5 dana bez vode godišnje (prag je pretpostavka aplikacije);
- mjesečni prosjeci.

**Napomene u aplikaciji:** kišnica nije pitka bez pročišćavanja. Uvjete za cisternu mogu propisati plan i komunalno poduzeće.

## 3. Energija kuće i dizalica topline (02, uz simulator)

**Izvori**
- Tehnički propis o racionalnoj uporabi energije i toplinskoj zaštiti u zgradama:
  - Prilog B, Tablica 1 (NN 128/15): najveće dopuštene vrijednosti U za nove zgrade, Θint ≥ 18 °C;
    - θe,mj,min ≤ 3 °C: zid 0,30, prozori 1,40, krov 0,25, pod na tlu 0,30 W/(m²·K);
    - > 3 °C: zid 0,45, prozori 1,80, krov 0,30, pod 0,50.
  - Čl. 4. t. 33. (NN 102/20): referentna klima prema θmm, srednjoj temperaturi najhladnijeg mjeseca (kontinentalna ≤ 3 °C, primorska > 3 °C).
  - Prilog B, Tablica 8 (NN 102/20, čl. 7.): Q''H,nd za obiteljsku kuću.
    - Kontinentalna: 40,50 za f0 ≤ 0,20; 32,39 + 40,58·f0; 75,00 za f0 ≥ 1,05.
    - Primorska: 24,84; 17,16 + 38,42·f0; 57,50.
- Open-Meteo, dnevne srednje i minimalne temperature 2016.–2025.

**Izračun (pojednostavljeno)**
- Ovojnica iz simulatora: zidovi (opseg × visina), prozori (zadano 15 % zidova), krov (tlocrt, ili kosa ploha kod grijanog potkrovlja), pod na tlu (tlocrt). Iz nje i obujma računa se f0.
- Gubici H = Σ U·A + 0,34 · n · V. Provjetravanje: n = 0,5 h⁻¹ prozorima ili 0,15 h⁻¹ s rekuperatorom (pretpostavke).
- Toplina = H × stupanj-sati (20 °C unutra, dani sa srednjom temperaturom ispod 15 °C) − 0,95 × unutarnji dobici 5 W/m² (pretpostavke).
- Snaga = H × (20 − 1. percentil dnevnih minimuma).
- Struja = toplina / SCOP (zadano 3,5).
- Pokrivenost iz sunčane elektrane, ako je izračunata.
- Hlađenje: stupanj-dani iznad 24 °C, informativno.

**Što nije uključeno:** sunčevi dobici, toplinski mostovi, podrum, topla voda. Procjena nije proračun po HRN EN ISO 52016-1 ni energetski certifikat. Usporedba s nZEB granicom je gruba.

## Testovi

`tests/run.js`, skupina `izvTests`. Provjerava:
- DXF: zaglavlje, slojevi, raspon koordinata, ASCII, udaljenosti;
- glTF: duljine i pristupnici;
- kišnicu: ravnotežu i spremnik kad kiša pada samo zimi;
- energiju: ručno izračunate gubitke, toplinu i nZEB te obje klime;
- prikaze i promjenu U.

**Ukupno:** 834/834.

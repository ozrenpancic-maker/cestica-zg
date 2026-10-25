# Fotografija s kućom, 3D prolet i dosje čestice

Stanje 25. 10. 2026., grana `razvoj`.

## 1. Fotografija s kućom kroz kameru (AR)

**Gdje:** gumb „📷 Snimi” u AR prikazu, u oba načina (poravnanje i mjerenje visina).

**Kako radi**
- WebXR sesija traži i mogućnost `camera-access`.
- U sljedećem okviru nakon dodira radi se ovo:
  1. Slika kamere (`XRWebGLBinding.getCameraImage`) i prizor (granica, prostor za gradnju, kuća, s istom projekcijom) crtaju se u zaseban međuspremnik veličine slike kamere.
  2. Slika se čita (`readPixels`) i okreće.
  3. Dodaje se traka s natpisom (k.č., k.o., kuća, „ilustracija, nije projekt”, datum) i sve se sprema kao JPEG.
- Nudi se „Spremi” (preuzimanje) i „Podijeli” (Web Share s datotekom, ako ga preglednik podržava).
- Bez podrške za `camera-access` piše da fotografija nije moguća. AR prikaz radi i dalje.

**Ograničenje:** radi samo na Androidu s Chromeom i ARCoreom. Ne može se testirati bez uređaja. Testirani su natpis i poruka kad AR prikaz nije pokrenut.

## 2. 3D prolet kao video

**Gdje:** gumb „🎬 Prolet” u 3D pogledu.

**Tijek videa (18 s)**

| Dio | Što se događa |
|---|---|
| 0–50 % | kamera obiđe 300° oko čestice |
| 50–78 % | Sunce 21. lipnja ide od 9 do 20 h (NOAA): svjetlo na modelu i sjena kuće se pomiču; sat je u kutu |
| 78–100 % | spuštanje (+1 zum, nagib 72°) i okret prema ulazu kuće |

**Snimanje**
- Okvir 3D pogleda crta se u 2D platno s pozadinom i natpisom (k.č., k.o., „ilustracija, nije projekt”).
- Snima se `MediaRecorder` (MP4 gdje ga preglednik podržava, inače WebM), 6 Mbit/s.
- Na kraju se nude „Spremi video” i „Podijeli”.

**Provjera u Chromiumu bez grafičke kartice:** video se snimi (MP4) i okviri su ispravni. Zbog sporog programskog prikaza ima samo nekoliko okvira u sekundi; na mobitelu i računalu s grafičkom karticom je glatko.

## 3. Dosje čestice (gumb „Ispiši / spremi PDF”)

**Priprema prije ispisa**
- Otvaraju se svi odjeljci i računaju napredne analize: osunčanost, vjetar, kišnica, energija, pogled i iskop. Čeka se najviše 15 s.
- Ako je kuća postavljena, a 3D slika nije snimljena, 3D pogled se sam otvori, snimi i zatvori (najviše oko 20 s).
- Napredak se prikazuje u okviru „Pripremam dosje čestice”.

**Sadržaj**
- Naslovnica „Dosje čestice”, s područjem: Grad Zagreb, Otok Krk ili grad/općina za ostatak Hrvatske.
- Nova poglavlja:
  - „Povijest lokacije (snimke iz zraka)”: DGU 2011. i 2023./24. jedna uz drugu, s granicom čestice. Ako se snimka ne učita, piše „snimka nije učitana”.
  - „Napredne analize”: iskop, osunčanost, pogled, energija, kišnica, vjetar.
  - „Izvori podataka”: svaki izvor iz registra pouzdanosti, sa stavkama i najslabijom oznakom.
- Troškovi uključuju i cijene zemljišta u općini i procjenu vrijednosti.
- Odjeljci koji imaju svoje poglavlje ne ponavljaju se u poglavlju u kojem stoje na zaslonu.
- Neizračunati odjeljci („Otvori odjeljak…”, „Postavi kuću…”) ne ispisuju se.

**Provjera:** PDF iz Chromiuma za probnu česticu na Krku ima 21 stranicu i 13 poglavlja, ispravnim redom.

## Testovi

`tests/run.js`, skupina `dosTests`. Provjerava:
- kadrove proleta (početak, sredina, kraj prema ulazu);
- da bez MediaRecordera nema snimanja;
- natpis fotografije i poruku bez AR sesije;
- pripremu dosjea s vremenskim ograničenjem;
- naslovnicu, snimke iz zraka, napredne analize i izvore;
- da se neizračunati odjeljci ne ispisuju.

**Ukupno:** 847/847.

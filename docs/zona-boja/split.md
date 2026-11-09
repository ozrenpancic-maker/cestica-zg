# Prijedlog urbanog pravila iz boja karte – GUP Splita

Izvor: ISPU WMS `https://gis{1-4}.mgipu.hr/srv1/PPRasterZ17_Public/wms`, sloj `HR_ISPU_GUP1_04090_R07_KN_1_2`
(GUP Splita, VI. izmjene i dopune, list „Urbana pravila”). List je iscrtan čistim bojama (paleta ACI), bez skeniranja.

Kalibracija 2026-11-09 (preglednik, app.cesticahr.com): iscrtan je list 2000 × 1000 px (43,495–43,535 N, 16,40–16,53 E),
boje su grupirane, a za svaku boju je izrezano 400 × 300 px oko točke unutar plohe i pročitana oznaka pravila na karti.

| Boja (RGB) | Pravilo na karti | Gdje je oznaka očitana (lat, lng) |
|---|---|---|
| 255,127,127 | 1.1 i 3.3 (ista boja) | jezgra 43.5081, 16.4402 (1.1); 43.5099, 16.4860 (3.3) |
| 0,255,191 | 1.2 i 3.4 (ista boja) | Varoš 43.5098, 16.4335 (1.2); 43.5140, 16.5063 (3.4) |
| 221,221,0 | 1.3 i 3.5 (ista boja) | Spinut 43.5135, 16.4255 (1.3); 43.5071, 16.5291 i 43.5045, 16.5282 (3.5) |
| 255,191,0 | 1.4 | izrez klastera 16 |
| 127,255,223 | 1.5 | Meje 43.5046, 16.4252 |
| 0,221,110 / 25,224,124 / 0,184,92 | 1.7 (Marjan, 1.7–1.7d) | 43.5110, 16.4133; oznake 1.7 i 1.7d |
| 221,193,110 | 1.8 | Poljud 43.5195, 16.4310 |
| 165,0,221 | 1.9 | oznaka 1.9 (1.9a je siva i ne broji se) |
| 255,255,127 | 2.1 | izrez klastera 6 |
| 0,255,0 | 2.1a | Meje 43.5048, 16.4255 (oznaka 2.1a) |
| 0,221,221 | 2.2 | tri izreza s oznakom 2.2 |
| 221,110,165 | 2.3 | izrez klastera 15 |
| 127,255,159 | 2.4 | dvije oznake 2.4 u istom izrezu |
| 255,191,127 | 2.5 (i 2.5 Bol, isti opis pravila) | izrez klastera 8; Bol 43.5150, 16.4600 |
| 221,165,0 | 2.6 | izrez klastera 7 |
| 127,255,255 | 2.7 | dva izreza s oznakom 2.7 |
| 0,191,255 | 2.8 (i 1.7a, park) | izrez klastera 12; Bačvice (1.7a) |
| 223,127,255 | 2.9 | izrez klastera 13 |
| 255,0,255 | 3.1 | tri izreza s oznakom 3.1 |
| 92,161,184 | 3.2 | šest izreza s oznakom 3.2 |

Siva 118 (zgrade) i 219 (prometnice) te bijela (izvan pravila, šrafure gradskih projekata) ne broje se kao pravilo.
Nisu kalibrirani: 1.6 i 6 (gradski projekti, šrafura na bijelom) – za njih aplikacija ne daje prijedlog.

Postupak u aplikaciji: izrez lista oko čestice (0,5 m/px, pojas 6 m), histogram boja unutar čestice i u pojasu (`uzHist`),
odluka `uzOdluka` s parametrima `HRZ_PARAM`. Kad legenda istu boju koristi za dva pravila, nude se oba.
Prijedlog je razina C; korisnik ga prihvaća ili odbija. Mjerodavna je lokacijska informacija.

Provjera na stvarnim česticama (2026-11-09): 1537/19 → 2.4; 5207 → 1.3 ili 3.5; 1041/9 → 2.5 ili 2.5 Bol;
3243 → 3.1 uz upozorenje o granici (11 % 3.4); 9527/2 (Meje, šrafura i oznake) → bez prijedloga; 15991 (luka) → bez prijedloga.
Histogrami: `tests/pgz-odgovori/split-kn12-histogrami-2026-11-09/cestice.json`.

Rijeka: na listovima GUP-a Rijeke urbana pravila 5, 6, 7 i 8 obojena su istom bojom, pa prijedlog iz boje nije moguć.

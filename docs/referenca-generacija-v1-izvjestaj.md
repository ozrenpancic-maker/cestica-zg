# Referentni skup generacija v1 – izvještaj o dokazima (Baška, Malinska-Dubašnica, Vrbnik)

Status: jedan pregledatelj, izvor je izvoz treće strane (`cesticahr_upu_rules_draft…zadnji_test.json`), nije neovisno pravno provjereno. Skup služi samo za validaciju, ne za podešavanje algoritma. SHA-256 skupa: `382d9d6d226c8ee90731e542ad079717afeec27950f9986e98b18783f69cf6c7`.

**Razine:** L1 izričita pravna veza u tekstu (citat s lancem SN); L2 posredno; L3 kandidat. Potvrđeno je samo L1. Broj SN same odluke nije u izvozu (samo lanac koji odluka citira), pa je `sn_vlastiti_broj` svugdje prazan.

**Ograničenje:** nijedan slučaj nije „nova generacija zamjenjuje staru”; u ove tri općine izvor nema izričitu zamjenu cijelog plana. Pozitivni parovi su samo ISTA generacija.


## C1 – PPUO Malinska-Dubašnica (Malinska-Dubašnica)
*Pripadaju li pročišćeni tekst (38/09), izmjene (13/04, 14/06) i ciljane izmjene 2013. istoj generaciji, i je li ukidanje kartografskih prikaza ukidanje plana?*  
Tip: ISTA_GENERACIJA_LANAC_IZMJENA + ZAMKA_UKIDANJE_KARTOGRAFSKIH_PRIKAZA

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [17702](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17702) | L1 | MAL-PPU#G1 | 1 | 13/04 | „Ovim elaboratom utvrđen je pročišćeni tekst Odluke o donošenju Prostornog plana uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04)” | `6838b90072c9` |
| [17702](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17702) | L1 | MAL-PPU#G1 | 1 | 38/09 | „Odluke o donošenju Izmjena i dopuna Prostornog plana uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 38/09)” | `385700d5d51a` |
| [17701](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17701) | L1 | MAL-PPU#G1 | 1 | 13/04, 14/06 | „Ovim elaboratom mijenja se i dopunjuje Prostorni plan uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04 i 14/06)” | `78991b54fda3` |
| [17701](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17701) | L1 | MAL-PPU#G1 | 157 | – | „stavljaju se izvan snage kartografski prikazi Prostornog plana uređenja Općine Malinska - Dubašnica” | `f2380693e08f` |
| [27012](https://www.sn.pgz.hr/default.asp?Link=odluke&id=27012) | L1 | MAL-PPU#G1 | 1 | 13/04, 14/06, 38/09, 38/09 | „Donose se ciljane Izmjene i dopune Prostornog plana uređenja Općine Malinska-Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04, 14/06 38/09 i 38/09 - pročišćeni tekst)” | `7c85f4d514a8` |
| [27012](https://www.sn.pgz.hr/default.asp?Link=odluke&id=27012) | L1 | MAL-PPU#G1 | 12 | – | „Stupanjem na snagu ovog Plana stavljaju se izvan snage kartografski prikazi Prostornog plana uređenja Općine Malinska-Dubašnica” | `529fdbbbbc46` |
| [1876](https://www.sn.pgz.hr/default.asp?Link=odluke&id=1876) | L3 | UNDETERMINED (kand. MAL-PPU#G1) | 1 | – | „Donosi se Prostorni plan uređenja Općine Malinska - Dubašnica, u daljnjem tekstu: Plan.” | `a56a62b5dada` |

Parovi: 17701–27012 **SAME_GENERATION** (L1: oba izričito mijenjaju plan s lancem SN 13/04, 14/06; nijedan ga ne zamjenjuje); 17702–27012 **SAME_GENERATION** (L1: isti lanac 13/04, 14/06, 38/09); 17701–17702 **SAME_GENERATION** (L1: isti lanac 13/04, 14/06); 27012–17702 **NOT_SUPERSEDED** (L1: stavljanje izvan snage samo KARTOGRAFSKIH prikaza nije stavljanje plana izvan snage; ne smije dati legal_status SUPERSEDED/REPEALED ni novu generaciju); 1876–17701 **REVIEW_REQUIRED** (L3: osnovna odluka nije dokaziva iz teksta)

## C2 – UPU 1 Vrbnik (NA 1) (Vrbnik)
*Je li promjena naziva plana (Odluka 2017.) nova generacija? Nije.*  
Tip: ISTA_GENERACIJA_PROMJENA_NAZIVA

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [36462](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36462) | L1 | VRB-UPU1#G1 | 1 | 33/09 | „Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Urbanističkog plana uređenja naselja Vrbnik (NA 1) s površinama izdvojenih namjena (T i R) - UPU 1 (Službene novine Primorsko-goranske županije broj 33/09)” | `b3486291d55a` |
| [36462](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36462) | L1 | VRB-UPU1#G1 | 1 | – | „Naziv plana iz stavka 1. ovog članka mijenja se i glasi” | `78bfa4a3c794` |
| [39662](https://www.sn.pgz.hr/default.asp?Link=odluke&id=39662) | L1 | VRB-UPU1#G1 | 1 | – | „Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Urbanističkog plana uređenja UPU 1 Vrbnik - NA 1” | `616f75717529` |
| [39662](https://www.sn.pgz.hr/default.asp?Link=odluke&id=39662) | L1 | VRB-UPU1#G1 | 1 | 33/09, 35/17, 2/18 | „broj 33/09, 35/17 i 2/18-pročišćene odredbe” | `0c5be4e9501f` |
| [39830](https://www.sn.pgz.hr/default.asp?Link=odluke&id=39830) | L1 | VRB-UPU1#G1 | 22 | 33/09, 35/17, 7/19 | „(»Službene novine« Primorsko-goranske županije, broj 33/09, 35/17 i 7/19)” | `0c943789155c` |
| [39830](https://www.sn.pgz.hr/default.asp?Link=odluke&id=39830) | L1 | VRB-UPU1#G1 | 20 | – | „Elaborat »II. izmjene i dopune Urbanističkog plana uređenja UPU 1 Vrbnik - NA 1« izrađen je u 6” | `70dd47f1f2fe` |
| [17522](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17522) | L2 | UNDETERMINED (kand. VRB-UPU1#G1) | 1 | – | „Donosi se Urbanistički plan uređenja naselja Vrbnik (NA 1) s površinama izdvojenih namjena (T i R) - UPU 1” | `d073f256c73b` |

Parovi: 36462–39662 **SAME_GENERATION** (L1: isti lanac SN 33/09; naziv se razlikuje (stari naziv u 36462 st.1, novi u st.2)); 39662–39830 **SAME_GENERATION** (L1: isti lanac 33/09, 35/17); 36462–39830 **SAME_GENERATION** (L1: isti lanac 33/09); 17522–36462 **REVIEW_REQUIRED** (L2: identičan naslov, ali broj SN osnovne odluke nije u tekstu 17522)

## C3 – PPUO Vrbnik (Vrbnik)
*Pripadaju li izmjene PPUO Vrbnik 2007.–2024. istoj generaciji?*  
Tip: ISTA_GENERACIJA_LANAC_IZMJENA

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [13407](https://www.sn.pgz.hr/default.asp?Link=odluke&id=13407) | L1 | VRB-PPU#G1 | 1 | 16/04 | „Donose se Izmjene i dopune Prostornog plana uređenja Općine Vrbnik (»Službene novine« broj 16/04)” | `6e6e0e663f27` |
| [35465](https://www.sn.pgz.hr/default.asp?Link=odluke&id=35465) | L1 | VRB-PPU#G1 | 1 | 16/04, 43/07, 53/07, 22/16, 26/16 | „Donosi se III. Dopuna Prostornog plana uređenja Općine Vrbnik (»Službene novine Primorsko-goranske županije« broj 16/04, 43/07, 53/07-ispravak, 22/16 i 26/16- pročišćeni tekst” | `17b9c63750b3` |
| [48254](https://www.sn.pgz.hr/default.asp?Link=odluke&id=48254) | L1 | VRB-PPU#G1 | 1 | – | „Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Prostornog plana uređenja Općine Vrbnik” | `aa83ccb1eb9d` |
| [48254](https://www.sn.pgz.hr/default.asp?Link=odluke&id=48254) | L1 | VRB-PPU#G1 | 1 | 16/04, 43/07, 53/07, 22/16, 26/16, 11/17, 28/17, 7/19, 11/19 | „broj 16/04, 43/07, 53/07-ispravak, 22/16, 26/16- pročišćeni tekst, 11/17 i 28/17-pročišćeni tekst, 7/19 i 11/19-pročišćeni tekst” | `efc67d405b9a` |
| [34277](https://www.sn.pgz.hr/default.asp?Link=odluke&id=34277) | L3 | UNDETERMINED (kand. VRB-PPU#G1) | 1 | – | „Donose se II. Izmjene i dopune Prostornog plana uređenja Općine Vrbnik” | `b2fe68f0aaf0` |

Parovi: 35465–48254 **SAME_GENERATION** (L1: lanac 16/04, 43/07, 53/07, 22/16, 26/16 zajednički); 13407–35465 **SAME_GENERATION** (L1: osnova SN 16/04 zajednička); 13407–48254 **SAME_GENERATION** (L1: osnova SN 16/04 zajednička); 34277–35465 **REVIEW_REQUIRED** (L3: 34277 ne navodi lanac SN)

## C4 – UPU-1 Baška (N1-1) i UPU-2 Baška-Zarok (N1-2) (Baška)
*Isti broj SN 24/12 u citatima: isti plan? Ne.*  
Tip: RAZLICITI_PLANOVI_ISTI_BROJ_SN

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [36814](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36814) | L1 | BAS-UPU1#G1 | 1 | – | „usklađuje se Urbanistički plan uređenja UPU-1 Baška (N1-1)” | `549b919d9c14` |
| [36814](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36814) | L1 | BAS-UPU1#G1 | 1 | 24/12 | „broj 24/12), u nastavku teksta: Plan” | `70ec6493d687` |
| [36815](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36815) | L1 | BAS-UPU2#G1 | 1 | – | „usklađuje se Urbanistički plan uređenja UPU-2 Baška-Zarok (N1-2)” | `dc33e74ca223` |
| [36815](https://www.sn.pgz.hr/default.asp?Link=odluke&id=36815) | L1 | BAS-UPU2#G1 | 1 | 24/12, 10/16 | „broj 24/12 i 10/16)” | `26b6ef36389c` |
| [24962](https://www.sn.pgz.hr/default.asp?Link=odluke&id=24962) | L3 | UNDETERMINED (kand. BAS-UPU2#G1) | 1 | – | „Ovom Odlukom donosi se Urbanistički plan uređenja - 2 - Baška - Zarok (N1-2)” | `8e1675d282ed` |

Parovi: 36814–36815 **DIFFERENT_PLAN** (L1: isti SN 24/12 u lancu, ali izričito UPU-1 (N1-1) i UPU-2 (N1-2): isti broj glasila nije isti plan); 24962–36815 **REVIEW_REQUIRED** (L3: ime i broj plana podudarni, SN osnovne odluke nije u tekstu)

## C5 – PPUO Općine Baška (Baška)
*Dva teksta 'Donosi se PPUO Baška': dvije generacije? Ukida li novi plan stari u cijelosti?*  
Tip: ZAMKA_DVA_DONOSI_SE_I_DJELOMICNO_UKIDANJE_STAROG_PLANA

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [14008](https://www.sn.pgz.hr/default.asp?Link=odluke&id=14008) | L3 | UNDETERMINED (kand. BAS-PPU#G1) | 1 | – | „Donosi se Prostorni plan uređenja Općine Baška, u daljnjem tekstu: Plan.” | `7a2584871a24` |
| [14008](https://www.sn.pgz.hr/default.asp?Link=odluke&id=14008) | L3 | UNDETERMINED (kand. BAS-PPU#G1) | 156 | – | „u dijelu koji se odnosi na područje Općine Baška” | `7faa0be2cb0c` |
| [25645](https://www.sn.pgz.hr/default.asp?Link=odluke&id=25645) | L3 | UNDETERMINED (kand. BAS-PPU#G1) | 1 | – | „Donosi se Prostorni plan uređenja Općine Baška, u daljnjem tekstu: Plan.” | `7a2584871a24` |
| [25645](https://www.sn.pgz.hr/default.asp?Link=odluke&id=25645) | L3 | UNDETERMINED (kand. BAS-PPU#G1) | 160 | 1/08 | „Stupanjem na snagu Odluke o donošenju Prostornog plana uređenja Općine Baška (»Službene novine Primorsko-goranske županije« br. 1/08) prestaje važiti” | `5f589fccd7f4` |

Parovi: 14008–25645 **REVIEW_REQUIRED** (L3: ne smije se automatski označiti ni kao ista ni kao nova generacija)

Pravni status: Prostorni plan bivše Općine Krk (SN 31/78 ... 4/93) → **NOT_FULLY_SUPERSEDED_PARTIAL_BY_AREA** (L1) – ukidanje po općini, ne u cijelosti; legal_status ne smije biti globalni SUPERSEDED

## C6 – UPU 1 Malinska, Radići (GP-1) (Malinska-Dubašnica)
*Pripada li tekst 27287 (2. 4. 2013.) UPU 1 Radići?*  
Tip: L1_IZMJENA_I_KANDIDAT_OSNOVE

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [32729](https://www.sn.pgz.hr/default.asp?Link=odluke&id=32729) | L1 | MAL-UPU1R#G1 | 1 | – | „Odluke o donošenju Urbanističkog plana uređenja UPU 1 Malinska, Radići (GP-1)” | `0e4ec0d0d787` |
| [32729](https://www.sn.pgz.hr/default.asp?Link=odluke&id=32729) | L1 | MAL-UPU1R#G1 | 1 | 14/13, 03/14 | „broj 14/13 i 03/14” | `e8f5e17973f2` |
| [27287](https://www.sn.pgz.hr/default.asp?Link=odluke&id=27287) | L3 | UNDETERMINED (kand. MAL-UPU1R#G1) | 1 | – | „1.Građevinsko područje naselja GP-1: Malinska, Radići” | `1c33ccf66915` |

Parovi: 27287–32729 **REVIEW_REQUIRED** (L3: kandidat po području i datumu; nema izričite poveznice)

## C7 – UPU 11 Risika (NA 2_3) / UPU 2 Risika (NA 2_11) (Vrbnik)
*Dva 'UPU naselja Risika': isti plan? Ne.*  
Tip: RAZLICITI_PLANOVI_SLICAN_NAZIV

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [16714](https://www.sn.pgz.hr/default.asp?Link=odluke&id=16714) | L1 | VRB-UPU11#G1 | 1 | – | „Donosi se Urbanistički plan uređenja naselja Risika (NA 2_3) s površinom izdvojene namjene T2 4 (UPU 11)” | `5b422876f410` |
| [17523](https://www.sn.pgz.hr/default.asp?Link=odluke&id=17523) | L1 | VRB-UPU2#G1 | 1 | – | „Donosi se Urbanistički plan uređenja naselja Risika (NA 2_11) s površinama izdvojenih namjena (T2) - UPU 2” | `705b31ad71f7` |

Parovi: 16714–17523 **DIFFERENT_PLAN** (L1: isto naselje, različit broj UPU i oznaka NA)

## C8 – DPU Haludovo (SN 30/06, 2/07-ispr.) (Malinska-Dubašnica)
*Je li DPU Haludovo stavljen izvan snage, a koja odluka je samo pokretanje postupka?*  
Tip: PRAVNI_STATUS_UKIDANJE_VS_POKRETANJE

| Odluka | Razina | Generacija | Članak | SN u citatu | Citat | sha256 citata |
|---|---|---|---|---|---|---|
| [46503](https://www.sn.pgz.hr/default.asp?Link=odluke&id=46503) | L1 | MAL-DPUH#G1 | 1 | – | „Donosi se Odluka o stavljanju izvan snage Odluke o donošenju Detaljnog plana uređenja Haludovo” | `bf19329118e7` |
| [46503](https://www.sn.pgz.hr/default.asp?Link=odluke&id=46503) | L1 | MAL-DPUH#G1 | 2 | – | „Ova Odluka stupa na snagu osmog dana od dana objave” | `7306db8b9f6d` |
| [46503](https://www.sn.pgz.hr/default.asp?Link=odluke&id=46503) | L1 | MAL-DPUH#G1 | 2 | – | „Malinska, 11. svibnja 2023.” | `d040e6cc4275` |
| [45310](https://www.sn.pgz.hr/default.asp?Link=odluke&id=45310) | L1 | MAL-DPUH#G1 | 1 | – | „Donosi se Odluka o pokretanju postupka stavljanja izvan snage Detaljnog plana uređenja Haludovo” | `75079a98dd79` |
| [45310](https://www.sn.pgz.hr/default.asp?Link=odluke&id=45310) | L1 | MAL-DPUH#G1 | 13 | – | „Malinska, 15. rujna 2022.” | `3db76f8601d5` |

Pravni status: DPU Haludovo (SN 30/06, 2/07-ispr.) → **REPEALED** (L1) – Odluka 45310 (pokretanje postupka) ne ukida plan; to čini tek 46503

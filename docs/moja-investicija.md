# Moja investicija

Cilj: jedan model građevine povezuje simulator kuće na čestici sa svim izračunima. To su gradnja, priprema terena, doprinosi, krov i sunčana elektrana, vremenski plan i scenariji. Postojeći kalkulatori se nadograđuju, ne zamjenjuju. Ručni unos ostaje svugdje.

## Faze

| Faza | Sadržaj | Stanje |
| --- | --- | --- |
| I | Predlošci kuća, zajednički model građevine, simulator → procjena gradnje, troškovi po fazama | ugrađeno (Zagreb) |
| II | Temelji, prilaz, obujam za komunalni doprinos iz modela; priprema terena (postojeći odjeljak) | ugrađeno (Zagreb; obujam i na Krku) |
| III | Krovne plohe, rotacija, PVGIS, zasjenjenje | planirano |
| IV | Vremensko-financijski plan, prekretnice, usporedba scenarija | planirano |

## Faza I

### Model građevine (`zgradaModel()`, `window.__zgrada`)

Model se gradi iz simulatora (`TL`) i sadrži:

- čestica i položaj;
- okret, širina i dubina;
- tlocrt i garaža;
- katnost, nadzemne etaže, potkrovlje i podrum;
- visina etaže i visina do vijenca (procjena);
- GBP po etažama, nadzemni GBP i GBP podruma;
- krov: tip, nagib, sljeme i azimut sljemena;
- predložak.

Svaka promjena kuće u simulatoru (`tDraw`) poziva `zgSync()`.

### Predlošci

- Predlošci su 75, 100, 150, 200 i 250 m². To je **ciljni nadzemni bruto (GBP)**, ne neto površina.
- Tlocrt = GBP ÷ (broj punih etaža + 75 % za potkrovlje).
- Predloženi pravokutnik je u omjeru oko 4 : 3, širina zaokružena na 0,5 m, dubina na 0,1 m. Primjer: 150 m², P+1 → 75 m² tlocrta → 10 × 7,5 m.
- Ručna promjena širine ili dubine prebacuje predložak u „vlastite dimenzije”.

### Krov

U ovoj fazi se krov samo bilježi, a koristi se u fazi III:

- oblik (dvostrešni, četverostrešni, ravni);
- nagib;
- smjer sljemena (uzduž dulje ili kraće strane).

Azimut sljemena (0° = sjever, u smjeru kazaljke) računa se iz okreta kuće. Okret ne mijenja površinu ni cijenu.

### Povezivanje s procjenom gradnje (samo Zagreb)

- Površina (nadzemni GBP), katnost i podrum preuzimaju se iz simulatora.
- Kad ih korisnik promijeni ručno, oznaka „ručno izmijenjeno” ostaje i simulator ih više ne mijenja. Gumb „Vrati na simulator” ponovno ih povezuje.
- Na Krku procjena gradnje ne postoji: cijene u aplikaciji vrijede za okolicu Zagreba. Model građevine se i tamo gradi za kasnije faze.

### Troškovi po fazama

Cijena gradnje (površina × jedinična cijena) dijeli se na faze 1–8. Udjeli faza su **pretpostavka aplikacije**, a ne cjenik:

| Faza | Udio | U roh-bau |
| --- | --- | --- |
| 1. Iskop i nasip za temelje | izračun iz stavki (faza II) | da |
| 2. Temelji i temeljna ploča | izračun iz stavki (faza II) | da |
| 2a. Podrum (iskop jame, zidovi i strop; samo ako je odabran) | 850 €/m² tlocrta × standard (ključ u ruke) | da |
| 3. Konstrukcija, zidovi i međukatne ploče | 22 % | da |
| 4. Krov i pokrov | 9 % | da |
| 5. Vanjska stolarija i zatvaranje | 9 % | ne |
| 6. Instalacije | 17 % | ne |
| 7. Fasada i izolacija | 9 % | ne |
| 8. Unutarnji završni radovi | 22 % | ne |

- Faze 1–4 su u fazi I zajedno činile 43 % (1 = 3 %, 2 = 9 %), što odgovara omjeru roh-bau / ključ u ruke za klasičnu gradnju (600 / 1.400 €/m²). Od faze II faze 1 i 2 su izračun (vidi „Faza II”), a udjeli ostalih faza su nepromijenjeni.
- Za roh-bau se cijena roh-baua dijeli samo na faze 3–4 (22/43 i 9/43); faze 1–2 su izračun.
- Podrum je posebna stavka 2a, a ne dio temelja (ispravak 19. 10. 2026.: 60 m² prizemnica s podrumom prije je u „temeljima” imala 58.560 €).

**Bez dvostrukog obračuna:**

- Faza 1 je samo iskop i nasip za temelje. Dodatni zemljani radovi upisuju se u „Pripremi terena”.
- Uređenje okoliša (faza 9) te projekti, nadzor i rezerva (faza 10) posebne su stavke modela.

**Ručni unos:**

- Jedinična cijena (`bUnit`) i iznos svake faze (`bF_<faza>`) mogu se upisati ručno.
- Novi izračun ih ne poništava. Gumb „Vrati cijenu i faze na automatske” ih briše.
- Raspon ±10 % vrijedi samo za automatski dio.

**Standardi:**

- ekonomični × 0,85;
- standardni × 1,0;
- viši × 1,3.

Uz faze se ispisuje cijela formula jedinične cijene.

**Ručno provjerljiv primjer** (iz testova, od faze II): klasična gradnja, ključ u ruke, standardni, P+1, 150 m² (simulator 10 × 7,5 m).

- Jedinična cijena: 1.400 × 1,0 × 0,93 = 1.302 €/m²; 1.302 € × 150 m² = 195.300 €.
- Faze 3–8: 88 % od 195.300 € = 171.864 € (konstrukcija 22 % = 42.966 €, instalacije 17 % = 33.201 €).
- Faza 1 (75 m² tlocrta × 40–90 €/m²): 3.000–6.750 €, sredina 4.875 €. Faza 2 (75 m² × 72–155 €/m²): 5.400–11.625 €, sredina 8.512,5 €.
- Gradnja: 171.864 + 4.875 + 8.512,5 = 185.251,5 €.

### Pouzdanost

- Simulirana kuća je korisnički scenarij.
- Cijene su procjene (B).
- Usklađenost s pravilima je samo geometrijska. Aplikacija nikad ne tvrdi da je kuća pravno dopuštena.

## Područje za gradnju (Faza B, korak 2)

U „Uvjetima gradnje”, odmah ispod usporedbe tipova, postoji odjeljak „Područje za gradnju”, a obris je ucrtan na karti.

- **Obris (zeleno):** čestica umanjena za udaljenost od međa. Uzima se samo dio u građevinskoj namjeni: Zagreb prema pravilu GUP-a, Krk prema PPUG-u ili UPU-u (4 m).
- **Pojas uz cestu (narančasto):** od obrisa se oduzima pojas do udaljenosti od regulacijskog pravca uz rub čestice prema cesti.
  - Rub uz cestu procjenjuje se iz OpenStreetMapa (cesta do 12 m od ruba).
  - Na Krku se primjenjuje manja vrijednost iz plana (4 m), uz napomenu da je uz razvrstanu ili javnu cestu odmak veći.
- **Geometrijski moguć tlocrt** = manje od tlocrta prema kig-u i površine obrisa. Uz njega piše što ograničava: kig ili oblik čestice.
- **Pouzdanost:**
  - B kad se primjenjuje samo odmak od međa;
  - C kad je primijenjen pojas uz cestu (procjena iz OpenStreetMapa) ili kad ceste nisu učitane.

  Obris nije dopuštenje: regulacijski pravac potvrđuje lokacijska informacija.
- Gumb „Sakrij s karte” / „Prikaži na karti”.

## Prekidači na vrhu „Uvjeta gradnje” (Faza B, korak 3)

Okvir „Prije svega provjeri” sadrži uvjete koji mogu zaustaviti gradnju bez obzira na kig i kis. Svaki ima stanje (✓, !, ✕, ?) i oznaku pouzdanosti.

| Uvjet | Krk | Zagreb |
| --- | --- | --- |
| Obvezni UPU | neizgrađeni dio bez UPU-a je zapreka (A); važeći UPU iz evidencije (A) | presjek sa slojem GUP-a 4b (A, sloj javne rasprave) |
| Pristup | cesta iz OpenStreetMapa (procjena) i zahtjev plana (PPUG: 5,5 m, iznimno 3 m); uvijek C | cesta iz OpenStreetMapa (procjena); uvijek C |
| Parkiranje | 2 PGM po stanu (PPUG čl. 107, UPU 2 čl. 38); broj stanova iz tipa građevine | PGM po stanu iz pravila GUP-a; broj stanova unosi korisnik |
| Komunalna opremljenost | udaljenost do vodovoda, kanalizacije i struje (DGU katastar infrastrukture); uvijek C | isto |

**Parkiranje na čestici:**

- Potreban prostor: broj mjesta × 12,5 m² (2,5 × 5 m, bez prilaza; pretpostavka).
- Slobodna površina: čestica − geometrijski moguć tlocrt − obvezno zelenilo ili prirodni teren.
- Ako ne stane, oznaka je ✕ i pouzdanost C.

## OpenStreetMap (ceste i okolina)

- Ceste se dohvaćaju posebnim malim upitom: ceste do 20 m od ruba čestice, 10 s na poslužitelju. Ako svi poslužitelji odbiju, upit se ponavlja jednom.
- Sadržaji u blizini (stanice, vrtić, škola, trgovina, ljekarna) idu posebnim upitom. Ako on padne, ceste i pristup i dalje rade, a u „Okolini” piše da sadržaji nisu dostupni.
- Rub čestice smatra se rubom uz cestu ako je barem pola njegove duljine (3 od 5 točaka) do 12 m od osi ceste. Tako se prepoznaje i čestica 1–2 m od ceste, a bočni rubovi okomiti na cestu ne.

## Granice čestica na karti

- U „Slojevima” je prekidač „Granice čestica (DGU)”. Prikazuje granice svih katastarskih čestica iz istog sloja DGU-a (`oss:BZP_CESTICE`) iz kojeg aplikacija čita grafičku površinu.
- Sloj se crta tek od zuma 16. Na manjem zumu uz prekidač piše „približi kartu”. Ako DGU ne odgovara, piše „DGU ne odgovara”.
- Radi preko obične karte i preko satelita, a iznad karata prostornih planova. Izbor se pamti na uređaju.
- Izgled crteža (boju i debljinu linija, brojeve čestica) određuje DGU.

## Ortofoto DGU

- Prekidač „Ortofoto DGU” u „Slojevima” prikazuje službeni digitalni ortofoto Državne geodetske uprave (DOF5, otvorena dozvola) preko odabrane podloge.
- Noviji snimak (`orthophoto_2023_2024`) crta se iznad starijeg (`orthophoto_2021_2022`), pa stariji popunjava mjesta koja noviji ne pokriva. Gdje nema ni jednog, vidi se podloga (karta ili Esri satelit).
- Servis ne nudi EPSG:3857, pa se slike traže u EPSG:4326 (WMS 1.3.0, sloj `OI.OrthoimageCoverage`). Na zumu 13 i većem razlika u projekciji unutar jedne slike je zanemariva.
- Crta se od zuma 13. Ostala pravila su kao za granice čestica („približi kartu”, „DGU ne odgovara”, izbor se pamti).
- Nije provjereno u pregledniku na mobitelu (okruženje u kojem je pisano ne može dohvatiti geoportal.dgu.hr).

## Cesta ne prati katastar

Kad os ceste iz OpenStreetMapa prolazi kroz unutrašnjost odabrane čestice, aplikacija upozorava da se katastar i stvarno stanje vjerojatno ne poklapaju (primjer: Vranićeva ulica, Zagreb).

- Mjeri se duljina osi unutar čestice umanjene 1,5 m (tolerancija crteža). Upozorenje se daje od 8 m nadalje.
- Ne broje se kućni prilazi (`highway=service`) ni ceste uz rub čestice.
- Ako je čestica uska (prosječna širina manja od 12 m), a os ide njome uzduž (barem pola poluopsega), čestica je vjerojatno sama put ili cesta i upozorenja nema.
- Upozorenje je u „Prije svega provjeri” (pristup, stanje „!”) i u „Području za gradnju” (redak „Cesta i katastar”). Pouzdanost područja za gradnju tada je C.
- Uzrok može biti neprovedena cesta u katastru ili krivo ucrtana cesta u OpenStreetMapu. Aplikacija ne odlučuje koje: upućuje na usporedbu s granicama čestica i ortofotom te na lokacijsku informaciju i geodeta.

## Faza II

### Temelji (faze 1 i 2)

Faze 1 (iskop i nasip za temelje) i 2 (temelji) više nisu udio cijene po m², nego zbroj stavki po m² tlocrta. Izvor svih jediničnih cijena: emajstor.hr, „Temeljna ploča – cijena temelja za kuću 2026” (cjenik i tablica primjera za kuću 100 m²).

| Stavka | €/m² tlocrta | Faza |
| --- | --- | --- |
| Iskop (humus i iskop za tampon) | 10–20 (primjer 100 m²: 1.000–2.000 €) | 1 |
| Tamponski nasip 50 cm, zbijen | 30–70 | 1 |
| Podložni beton C12/15 | 15–25 | 2 |
| Hidroizolacija ispod ploče | 10–20 | 2 |
| Toplinska izolacija ispod ploče (XPS 2 × 10 cm) | 12–30 | 2 |
| Armiranobetonska ploča 25 cm (oplata, armatura, beton) | 35–80 | 2 |
| Trakasti temelji (samo za tip „trakasti temelji + ploča na tlu”) | 70–150 €/m traka | 2 |

- Faza 1: 40–90 €/m², faza 2: 72–155 €/m². Zajedno 112–245 €/m².
- **Provjera s tvojom procjenom:** prizemnica 60 m² s pločom → 6.720–14.700 € (sredina 10.710 €). Tvoja procjena je 7.500–15.000 €.
- Trakasti temelji: duljina traka je opseg kuće iz simulatora (bez simulatora 4 × √tlocrt). Unutarnje nosive zidove dodaješ ručno u polju „m traka”.
- S podrumom faza 1 je 0 (iskop je u podrumu 2a), a faza 2 je ploča podruma.
- **Klasična gradnja:** cijena po m² uključuje temelje, pa se njihov udio (12 %, kod roh-baua 12/43) zamjenjuje izračunom. Ukupna cijena gradnje zato je manja nego u fazi I (za 150 m² P+1 oko 10.000 €).
- **Montažna:** cijena po m² ne uključuje temelje (prije se dodavalo 90 €/m² tlocrta), pa faze 3–8 nose punu cijenu, a temelji se dodaju.
- U „Troškovima po fazama” uz faze 1 i 2 ispisana je svaka stavka s rasponom i formulom. Raspon gradnje: ±10 % na faze iz udjela, a za temelje rasponi stavki.
- Ručni iznos faze i dalje zamjenjuje izračun.

### Prilaz

- Novo polje „Prilaz od ceste”: vrsta, duljina i širina (zadano 3 m). Stavka „Prilaz” ulazi u gradnju i u rezervu. „Uređenje okoliša” je sada bez prilaza.
- Cijene (emajstor.hr, „Asfaltiranje” i „Popločavanje dvorišta”, 2026.):
  - asfalt: 27–43 €/m² (iskop, 50 cm šljunka, priprema i asfalt 6 cm);
  - betonski opločnici: 70–140 €/m² (iskop do 40 cm 15–30 € + opločnici s tamponom do 50 cm 55–110 €);
  - šljunak: 14–26 €/m², **izvedeno** (asfalt s pripremom 27–43 € − jednoslojni asfalt 6 cm 13–17 €).
- Duljina: kad nije upisana, procjenjuje se kao najkraća udaljenost od kuće u simulatoru do osi ceste iz OpenStreetMapa, umanjena za 3 m (polovica kolnika); kućni prilazi (`service`) se ne broje. To je procjena (C) i piše uz stavku.

### Obujam za komunalni doprinos iz modela

Prema Pravilniku o načinu utvrđivanja obujma i površine građevina u svrhu obračuna komunalnog doprinosa (NN 15/2019):

- obujam je stvarni obujam zatvorenih dijelova (čl. 3);
- mjeri se od gornje kote poda prema tlu do unutarnje plohe krova (čl. 4);
- ne računa se prostor ispod dijela kosog krova nižeg od 1,2 m, temelji ni strehe (čl. 5).

Model: (podrum + pune etaže) × tlocrt × visina etaže + garaža (jedna etaža) + prostor pod kosim krovom gdje je visina barem 1,2 m (numerička integracija po tlocrtu, mreža 5 cm).

**Pretpostavke aplikacije (nisu iz propisa):** krov počinje na stropu zadnje pune etaže; kad je potkrovlje, nadozid je 1,2 m; debljina krova se zanemaruje (obujam je zato malo veći od stvarnog).

**Ručno provjerljiv primjer:** 10 × 8 m prizemnica, 3 m, dvostrešni 30°, sljeme uzduž: 240 m³ + 2 × 10 × tg 30° / 2 × (4² − 2,078²) ≈ 67 m³ = 307 m³. Krov od 10° (najviše 0,7 m) ne dodaje ništa.

- Zagreb: koristi se kad je procjena gradnje povezana sa simulatorom (inače kao prije: površina × 3 m).
- Krk: obujam u „Komunalnom doprinosu (Grad Krk)” puni se iz modela; ručni upis ostaje.
- Službeno vrijedi obujam iz projekta.

### Priprema terena

Odjeljak „Priprema terena” već postoji (ručne količine, rasponi cijena, prijedlog iskopa i nasipa iz nagiba i tlocrta simulatora). U fazi II nije mijenjan; faza 1 i dalje obuhvaća samo iskop i nasip za temelje.

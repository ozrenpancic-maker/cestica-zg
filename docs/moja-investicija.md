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

Promjena 20. 10. 2026.: Overpass je kod korisnika odgovarao otprilike jednom od deset pokušaja, pa ceste više ne ovise o njemu.

- **Ceste:** prvo iz vektorskih pločica [OpenFreeMap](https://openfreemap.org). To su isti podaci OpenStreetMapa (shema OpenMapTiles, tjedno osvježavanje), s CDN-a, bez ključa i bez ograničenja broja upita.
  - Pločice z14 koje pokrivaju česticu (+30 m) dekodira mali čitač protobufa u aplikaciji (`mvtDecode`), bez vanjske biblioteke.
  - Uzimaju se dijelovi cesta do 20 m od čestice. Klase su `minor` (ulica), `tertiary`… `service` i `track`; naziv ulice dolazi iz sloja `transportation_name` (najbliža linija do 15 m).
  - Adresa pločica čita se iz TileJSON-a `https://tiles.openfreemap.org/planet` (rezerva: stil `liberty`). Kad pločica vrati 404 (nova tjedna inačica), popis se dohvati ponovno.
- **Rezerva za ceste:** Overpass s upitom pravokutnika oko čestice (+25 m), lakšim za poslužitelj od „around” oko poligona.
- **Sadržaji u blizini:** Overpass, nakon cesta. Ako ne uspije, koristi se POI sloj istih pločica: škola, vrtić, ljekarna, supermarket, stanice. Potrebna je bar pločica sa sredinom čestice.
- **Overpass, redom:** pita se jedan po jedan poslužitelj. Sljedeći kreće čim prethodni odbije ili nakon 4 s bez odgovora. Kad jedan odgovori, ostali se prekidaju. Odgovor s porukom o preopterećenju (`remark`) računa se kao neuspjeh.
- **Izvor i atribucija:** ispod „Pristupa i okoline” piše izvor cesta i sadržaja i atribucija (OpenFreeMap © OpenMapTiles, podaci © OpenStreetMap). „Stanje servisa” ima i OpenFreeMap.
- **Rub čestice uz cestu:** smatra se rubom uz cestu ako je barem pola njegove duljine (3 od 5 točaka) do 12 m od osi ceste.
- **Nije provjereno uživo:** ni OpenFreeMap ni Overpass nisu dostupni iz okruženja u kojem je pisano; testovi koriste pravu pločicu napravljenu s `vt-pbf`.

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

## Skica kuće na terenu (za izvještaj)

Odjeljak „Skica kuće na terenu” ispod simulatora (Zagreb i Krk). Pri ispisu (gumb „Ispiši / spremi PDF”) otvara se kao i ostali odjeljci i ulazi u PDF.

**Tlocrt**

- međe s duljinama stranica (iz grafičkog prikaza katastra; stranice kraće od 2 m, odnosno 5 m kad ih je više od 24, nisu označene);
- područje za gradnju (zeleno) i pojas uz cestu (narančasto), ako su izračunati za tu česticu;
- kuća i garaža iz simulatora, linije krova (sljeme; kod četverostrešnog i grebeni);
- udaljenosti od međa: od sredine svake stranice kuće okomito do granice (isto kao u simulatoru);
- izohipse iz nagiba terena, s visinama prema sredini kuće; sjever, mjerilo i strelica pada.

**Presjek** kroz sredinu kuće u smjeru pada terena, isto mjerilo vodoravno i okomito:

- teren od međe do međe s visinama na međama;
- ±0,00 je teren u sredini kuće (pretpostavka); usjek i nasip do te razine su osjenčani;
- etaže, podrum, potkrovlje (nadozid 1,2 m, pretpostavka) i krov: trokut kad je presjek okomit na sljeme, inače sljeme kao vodoravna linija (kod četverostrešnog trapez);
- kote ±0,00, vijenac, sljeme, dno podruma i razlika terena ispod kuće.

**3D prikaz (skica)** — aksonometrija bez uvećanja visina:

- teren kao blok (maketa): gornja ploha je ravnina nagiba s mrežom svakih 5 m, a na dva vidljiva boka vidi se nagib;
- međe i područje za gradnju položeni su na teren;
- kuća sa zidovima do terena (na nižoj strani vidi se podnožje ili podrum), krovom (dvostrešni: plohe i zabati; četverostrešni: četiri plohe; ravni) i garažom;
- pogled odozgo pod 30°, sa strane prema kojoj teren pada, zakrenut za 35° da se vide dva pročelja; plohe su osjenčane prema svjetlu s jugozapada;
- crta se slaganjem ploha od najdalje prema najbližoj (bez 3D biblioteke), pa se ispisuje kao vektorska slika.

U ispisu svaki dio skice (tlocrt, presjek, 3D) ostaje na jednoj stranici.

**Teren i pouzdanost**

- Teren je ravnina iz nagiba u okolini čestice (Copernicus DEM preko Open-Meteo, rezolucija oko 90 m). Smjer pada računa se iz istih pet točaka kao nagib.
- Oznaka pouzdanosti je C. Stvarni teren čestice daje geodetski snimak.
- Službeni digitalni model reljefa DGU-a (DMR) dostupan je samo registriranim korisnicima, uz ključ, pa se u aplikaciji ne koristi.

**Ručno provjerljiv primjer (iz testova)**

Čestica 30 × 25 m, kuća 10 × 8 m u sredini, P + 1 s etažama od 3 m, dvostrešni krov 30° sa sljemenom istok–zapad, pad terena 10 % prema jugu:

- udaljenosti od međa 10 i 8,5 m;
- međe na ±1,25 m;
- vijenac +6,00 m;
- sljeme +8,31 m (6 + tg 30° × 4);
- razlika terena ispod kuće 0,8 m.

## Legenda boja i izvještaj (PDF)

**Pojas uz cestu** sada se crta cijeli, od ruba čestice prema ulici do udaljenosti od regulacijskog pravca (npr. 0–5 m). Prije je bio nacrtan samo dio iza udaljenosti od međa (3–5 m), pa je izgledalo kao da se zbraja s međama. Izračun područja za gradnju nije promijenjen.

**Legenda boja** postoji na tri mjesta, iz iste funkcije (`legendaHtml`):

- u „Slojevima” na karti („Legenda boja”, s bojama namjene); na mobitelu se pri otvaranju panel spusti;
- u „Području za gradnju”;
- u izvještaju, uz skicu.

**Izvještaj:** gumb „Ispiši / spremi PDF” slaže poseban dokument za ispis (`buildReport`), a ne ispisuje sučelje.

- **Naslovnica:** tamnozelena traka sa zlatnim rubom, broj čestice i k.o., datum i koordinate, karta s česticom i kućom, šest ključnih podataka (površina, namjena, područje za gradnju, izračun, investicija, pouzdanost) i napomena o naravi izvještaja.
- **Numerirana poglavlja** (01–10): sažetak (prije svega provjeri), čestica i namjena, uvjeti gradnje, kuća na čestici (simulator, područje za gradnju, legenda, skica), rizici i provjere, infrastruktura i okolina, troškovi i investicija, sunce i energija, pouzdanost podataka, izvori.
- **Sadržaj** je kopija odjeljaka sa zaslona, pa je uvijek usklađen. Polja za unos postaju vrijednosti (automatske vrijednosti sivo), sklopivi odjeljci postaju podnaslovi, a gumbi i upute za rad u aplikaciji se izostavljaju. Prazni odjeljci (kupnja bez cijene, priprema bez unosa, scenariji) ne ulaze.
- **Stranica:** A4, naslovnica bez margina; ostale stranice imaju podnožje „Čestica HR · Izvještaj o čestici” i „Stranica X / Y”.
- **Pisma:** naslovi Georgia (serif), tekst sistemski sans; nema vanjskih fontova, pa radi i bez mreže.
- Ako se ispis pokrene iz izbornika preglednika (ne gumbom), ispisuje se sučelje kao prije.

## Cesta na skici

Ceste iz OpenStreetMapa (iste kao za pristup i pojas uz cestu) ucrtavaju se u sva tri crteža skice:

- **Tlocrt:** kolnik sivo, os bijelo isprekidano, naziv ulice uz cestu. Okvir se proširi do 12 m izvan čestice prema cesti. Gdje cesta u naravi ulazi u česticu, vidi se preklapanje.
- **Presjek:** ako pravac presjeka siječe cestu do 25 m izvan međa, presjek se produži do ceste i kolnik se nacrta na razini terena, s nazivom. Stvarna visina kolnika nije poznata.
- **3D:** blok terena se proširi do 14 m izvan čestice prema cesti, a cesta je položena na teren.
- **Širina:** iz oznake `width` u OpenStreetMapu kad postoji, inače procjena prema vrsti ceste (ulica 5 m, lokalna 6 m, sporedna 7 m, glavna 8 m, servisni put 3,5 m, poljski put 3 m); to piše uz skicu.

## Pregledno sučelje (20. 10. 2026.)

- **Više informacija:** dulja pojašnjenja (uzastopni sivi odlomci od 110 znakova nadalje) sklapaju se pod „ⓘ Više informacija”. U izvještaju su otvorena.
- **Sažetak na vrhu analize:** pet odgovora s oznakom stanja (✓, !, ✕, ?): smije li se graditi, koliko velika kuća, ima li tereta, pristup i komunalije, koliko bi koštalo. Ispod je poveznica na stavke označene s C. Dodir otvara odgovarajući odjeljak.
  - Odgovori su preuzeti iz odjeljaka ispod (isti izvor i oznaka pouzdanosti). Sažetak ne računa ništa novo.
  - Zamjenjuje stare četiri kartice na mobitelu.
- **Poglavlja kao kartice:** rizici, provjere, komunalna infrastruktura, pristup i okolina, karte planova, uvjeti gradnje, sunce i energija, novac i kupnja, pouzdanost i dokumentacija sklopljeni su u kartice s kratkim stanjem u zaglavlju. Otvorene kartice ostaju otvorene pri ponovnom prikazu.
- **Gumbi** na vrhu analize prelamaju se u novi red umjesto da izlaze iz okvira.

## Natura 2000, izvor u sažetku, 3D pogled (20. 10. 2026.)

**Natura 2000:** u „Provjerama” (Zagreb i Krk) i u sažetku (redak „Priroda i poplave”).
- Izvor: Europska agencija za okoliš (EEA), ArcGIS sloj `ProtectedSites/Natura2000Sites/MapServer/2`. To su granice područja koje dostavlja Republika Hrvatska.
- Upit je presjek s česticom, a vraća SITECODE, SITENAME i SITETYPE: A = POP (ptice), B = POVS (vrste i stanišni tipovi), C = oboje.
- U ekološkoj mreži piše da može biti potrebna ocjena prihvatljivosti za ekološku mrežu (Zakon o zaštiti prirode).
- Pouzdanost je A. Kad servis ne odgovori, piše „Podaci nisu dostupni” i oznaka je C.

**Zaštićena područja prirode:** Bioportal, WMS `services.bioportal.hr/wms`, sloj `zasticeno_podrucje_poligoni`.
- Upit je GetFeatureInfo (JSON) u do pet točaka unutar čestice.
- Polja provjerena 20. 10. 2026. na Parku prirode Medvednica: `naziv`, `kategorija_zastite`, `podkategorija_zastite`, `naziv_akt`.
- U zaštićenom području piše da mogu biti potrebni uvjeti zaštite prirode. Pouzdanost je A.

**Poplave:** karte opasnosti od poplava Hrvatskih voda poslužuje `preglednik.voda.hr/geocluster/wms`. Taj servis ne dopušta čitanje drugim stranicama (CORS; test 20. 10. 2026.). Javni `servisi.voda.hr/public_ows/wms` ima samo tri sloja, a među njima nema karata opasnosti.
- Zato aplikacija zasad daje samo poveznicu na kartu opasnosti od poplava, s oznakom C.
- Automatska provjera moguća je preko zasebnog posrednika (Cloudflare Worker), ako se odobri.

**Izvor u sažetku:** ispod svakog odgovora je izvor, datum i oznaka pouzdanosti, iz registra pouzdanosti (isti podatak kao u odjeljku).

**3D pogled:** gumb „3D” na karti.
- Biblioteka MapLibre GL 4.7.1 (`vendor/maplibre-gl-4.7.1`, licenca BSD-3) učitava se tek kad se pogled otvori. Nije u predmemoriji aplikacije.
- Satelit (Esri) ili OpenStreetMap; teren iz Terrain Tiles (Mapzen/AWS, oko 30 m).
- Granice čestica DGU (WMS u EPSG:3857), odabrana čestica (žuto), područje za gradnju (zeleno) i kuća iz simulatora. Kuća je 3D tijelo do vijenca, s krovom od šest slojeva koji se sužavaju prema sljemenu; garaža je visoka 2,8 m.
- Kamera obuhvati česticu, nagnuta je 62° i polako se okreće. „Zaustavi” ili povlačenje zaustavlja okretanje.
- Kad se pogled iscrta (ili nakon 8 s), sprema se slika i ulazi u PDF izvještaj u poglavlje „Kuća na čestici”. Ako preglednik ne dopusti čitanje slike, izvještaj je bez nje.
- Bez WebGL-a piše da preglednik ne podržava 3D prikaz.

## Procjena vrijednosti zemljišta (Troškovi → Novac i kupnja)

- **Referentni podaci (B, uz broj kupoprodaja):** Grad Zagreb, *Izvješće o tržištu nekretnina za 2025.*, građevinsko zemljište:
  prosjek po naselju (53 naselja), po veličini čestice (7 razreda) i rasponi po namjeni (S/M1/M2 niska 50–900, M visoka 300–1.200,
  K 200–500, G 120–330, I 30–200 €/m²). Izvješće navodi da je evaluirano približno 30 % ugovora i da su prosjeci ponderirani
  površinom, pa su orijentir, ne procjena. Naselje se predlaže samo kad se ime k.o. poklapa s imenom naselja; odabir korisnika je C.
- **Plan približnih vrijednosti (ISPU):** izravno čitanje iz preglednika blokira CORS (test 20. 10. 2026., `ppv-test.html`).
  Zasad korisnik prepisuje vrijednost bloka s karte (C). Automatski dohvat moguć je samo preko posrednika (Worker), uz odobrenje.
- **Usporedbe korisnika:** do 12 redaka (prodano / oglas, €/m², opis). Raspon i medijan računaju se **samo iz ostvarenih kupoprodaja**,
  najmanje 3 (5+ → srednja polovina P25–P75, inače min–max). Oglasi se prikazuju odvojeno kao tražene cijene. Bez 3 kupoprodaje:
  „Podaci nisu dostupni”. Rezultat je uvijek C.
- **Čimbenici:** samo kvalitativno (↑/↓), bez izmišljenih postotaka: veličinski razred, udio namjene za gradnju, nagib ≥ 15 %,
  ograničenja iz provjera, Natura 2000 / zaštićeno područje.
- Gumb „Upiši medijan u kupnju zemljišta” prenosi medijan × površina u „Kupnja zemljišta” samo na dodir. Usporedbe se spremaju
  i izvoze s projektom (`proj.vrij`). Krk: referentni podaci nisu dostupni, usporedbe rade.

## 3D model kuće (low-poly, za planiranje)

- `v3dModel()` gradi kuću u lokalnim metrima (širina, dubina, zakret iz simulatora) kao skup `fill-extrusion` tijela s bojom, bazom, visinom i razinom detalja.
- Dijelovi: podest/temeljna ploča (0,45 m, 20 cm šira od zidova, jasan dodir s terenom), zidovi do vijenca, krov sa strehom (0,5 m) i zabatnim prepustom (0,3 m),
  krov u slojevima naizmjenične boje (dojam crijepa), tamna letva sljemena (orijentacija krova), ravni krov s atikom, prozori s okvirom po etažama, ulazna vrata s nadstrešnicom
  na strani prema najbližoj cesti (bez cesta: prema jugu), garaža s vratima.
- Svjetlo i sjena: sunce s jugozapada (azimut 215°, 40° iznad obzora); sjena je obuhvat tlocrta i tlocrta pomaknutog od sunca, u tri prozirna sloja (meki rub).
- Razine detalja: krov sa 6 slojeva ispod zooma 18,6, sa 14 slojeva iznad; prozori, vrata i nadstrešnica od zooma 17,6; paneli samo izbliza.
- Oznaka čestice stoji na vrhu granice najdaljem od kuće i ne prima dodir.
- Priprema: solarni paneli (prekidač „Paneli”, iz površine i orijentacije u odjeljku Solarna elektrana, na kosini najbližoj odabranoj orijentaciji ili u redovima na ravnom krovu);
  prilaz (iz procjene gradnje: vrsta i širina, od ulaza do najbliže ceste, boja po vrsti); sloj terase postoji, ali je prazan dok aplikacija nema unos za terasu.
- Prikaz je ilustracija za planiranje, ne arhitektonski projekt.

## Prijedlog okućnice (Faza 1, ilustrativno)

- Odjeljak „Prijedlog okućnice” ispod simulatora kuće; gumb „Predloži okućnicu” (prijedlog postoji samo kad ga korisnik zatraži). Oznaka „Automatski prijedlog okućnice – ilustrativno”, pouzdanost C.
- Izračun je pravilima u aplikaciji (`okuIzracun`, čista funkcija, ravnina u metrima oko čestice), bez vanjskog AI-ja i bez slanja podataka.
- Pristup: točka granice uz cestu (OSM) najbliža kući; bez cesta pretpostavljen, uz napomenu. Parking 1–2 mjesta 2,5 × 5 m okomito na granicu, 1 m od nje, pomak ◀ ▶.
  Kolni prilaz od granice do parkinga (širina 2,5–5 m). Staza 1,2 m od parkinga do ulaza (strana kuće prema pristupu), oko kuće preko ugla ako treba.
  Vrt: kompaktan skup čelija 1 m² na najsunčanijem dijelu (izvan sjene kuće za podne u proljeće i jesen), dalje od ceste. Travnjak: ostatak slobodnog prostora.
- Napomene: uska čestica (zbroj slobodnog prostora sa strana kuće < 5 m) → kompaktan prijedlog; nema mjesta za parking/vrt; nagib ≥ 15 %; cesta daleko.
- Prikaz: karta (sloj u odabiru), skica tlocrta, legenda, 3D (površine na terenu; isti ulaz u kuću), izvještaj. Pomicanje kuće preračunava prijedlog.
- Izlaz za druge module: `window.__oku.povrsine` {parking, prilaz, staza, vrt, travnjak} m² i `projGet().okucnica`. Ne ulazi automatski u troškove (Faza 3).
- Faza 2 (gotovo): terasa, pomoćni objekt i tipovi okućnice (vidi ispod).

### Faza 2: terasa, pomoćni objekt, tipovi
- Tipovi (`OKU_TIP`): obiteljska (terasa 20 m² prema jugu, dubina 3,5 m, vrt 30 m²), mediteranska (terasa 30 m² prema jugozapadu, dubina 4 m, vrt 15 m², umjesto travnjaka „mediteranski vrt” sa šljunkom i nasadima),
  minimalistička (terasa 15 m², dubina 3 m, bez vrta, staza 1,5 m). Tip postavlja zadane vrijednosti i boje; sve se može ručno promijeniti.
- Terasa: uz zid kuće koji nije ulazni, okrenut najbliže smjeru tipa; ako ne stane, kraća ili plića (najmanje 2,5 m), uz napomenu.
- Pomoćni objekt (spremište, 4–30 m², zadano 12 m²): pravokutnik 3 m širok, 1 m od svih međa, u dijelu čestice dalje od ceste i kuće (prednost sjevernom dijelu).
  Napomena: udaljenost od međe i ulazi li u izgrađenost provjeriti u pravilima plana (aplikacija to ne računa).
- Prikaz: karta, skica, legenda, izvještaj; u 3D-u terasa kao ploča 15 cm, pomoćni objekt 2,5 m s krovom. Površine `terasa` i `pomocni` u `window.__oku.povrsine`.

## Glavni izbornik: analiza 01–05 i troškovi (€)

Promjena 20. 10. 2026.: „Troškovi i investicija” nije više dio numerirane analize. Na mobitelu je samo u kartici „Troškovi” (sve troškove obračunava tu),
a analiza ima 01 Prostorni planovi, 02 Gradnja i simulator, 03 Rizici, 04 Pristup i infrastruktura, 05 Projekt i dokumentacija. Na računalu se troškovi prikazuju
kao kategorija s oznakom € između 04 i 05. Tablica ispod koristi unutarnje brojeve (5 = troškovi, 6 = projekt).


Prikaz se slaže kao prije; `izbWrap()` zatim premješta postojeće odjeljke (isti elementi, id-evi i `data-k`) u kategorije. Ništa se ne kopira.

| Kategorija | Postojeći odjeljci i moduli |
|---|---|
| 01 Prostorni planovi i namjena | udjeli namjene (zone), Karte prostornog plana (GUP/UPU, rkBox), Krk: Prostorni planovi na lokaciji |
| 02 Gradnja i simulator kuće | Uvjeti gradnje (prekidači, pravilo, parametri, iznimke), Usporedba tipova, Područje za gradnju, Izračun, Simulator, Prijedlog okućnice, Skica, sva detaljna pravila / opća pravila / članak, Postojeće zgrade (Krk), Sunce i sjena, Sunčana elektrana; prečac 3D pogled |
| 03 Rizici i pravne provjere | ZK (uložak, tereti), Rizici i upozorenja, Svi nalazi, Provjere, Natura/zaštićena/poplave, Potresna opasnost; prečac Kontrolna lista |
| 04 Pristup i infrastruktura | Komunalna infrastruktura, Pristup i okolina |
| 05 Troškovi i investicija | Procjena cijene gradnje, Priprema terena, Komunalni doprinos, Priključci i dozvole, Scenariji, Procjena vrijednosti zemljišta, Kupnja, Ukupna investicija, Krk troškovi; prečac Sunčana elektrana: isplativost (isti modul iz 02) |
| 06 Projekt i dokumentacija | Projekt čestice, Pouzdanost podataka, Dokumentacija i gdje se obratiti, Kontrolna lista, Projekt i dozvola, Gradnja i useljenje, poveznice i izvori; prečaci PDF, Spremi, Podijeli |

- Otvorena je jedna glavna kategorija; pri otvaranju druge pojavi se „← Natrag na …”. Otvorena kategorija se pamti (OPEN) i pri ponovnom prikazu.
- Sažetak: na mobitelu sklopljen u jedan redak sa stanjima; potvrđena namjena ima neutralnu oznaku „i” (ne zelenu kvačicu) i tekst da uvjeti gradnje nisu potvrđeni.
- Mobitel: kartica „Troškovi” prikazuje i otvara 05; „Karta” spušta panel; dok se kuća povlači, panel se spusti. „↑ Sažetak” vraća na vrh.
- Moduli su neutralni (tanki sivi rub); zelena, narančasta i crvena ostaju samo za rezultate provjera.

### Faza 3: trošak okućnice u troškovima i scenarijima
- `okuTrosak(k)`: površine prijedloga × jedinične cijene (emajstor.hr 2026.): parking i kolni prilaz prema podlozi (šljunak 14–26, asfalt 27–43, opločnici 70–140 €/m²), staza opločnici 70–140,
  terasa (opločnici 70–140, sibirski ariš 40–85, WPC 65–110), travnjak (sjetva 2–6, busen 5–12), vrt samo priprema tla (frezanje 0,5–3), pomoćni objekt samo šupa do 5 m² (1.000–2.700 €/kom).
  Bez cijene u cjeniku: mediteranski šljunak i nasadi, pomoćni objekt veći od 5 m² → „Podaci nisu dostupni”, upis ponude (unos).
- Stavke idu u financijski model kao skupina `okucnica` (jednom): procjena gradnje, ukupna investicija, rezerva 15 %, scenariji (zajedničko za česticu, kao priprema terena).
- Bez dvostrukog obračuna: kad je okućnica uključena i ima parking/prilaz, prilaz iz procjene gradnje se ne računa; ručno upisano „uređenje okoliša” se ne zbraja (upozorenje).
- Prekidač „U procjeni troškova” (zadano uključen); tip okućnice postavlja zadane materijale (obiteljska: opločnici i sjetva; mediteranska: ariš; minimalistička: WPC i busen).

## Pristup s ceste (popravak 20. 10. 2026.)
- Mjeri se razmak od međe do ruba kolnika (os ceste iz OSM-a − pola širine: oznaka `width` ili procjena prema vrsti), a ne do osi.
- Do 3 m: čestica graniči s cestom (nogostup, bankina). 3–10 m: pojas ceste ili uska čestica između; katastarski sloj DGU (GetFeatureInfo, izravno iz preglednika)
  pita se koja je čestica na sredini razmaka i na osi ceste. Ista čestica → čestica ceste, nema upozorenja. Druga čestica → upozorenje s brojem čestice (provjeriti javno dobro ili služnost).
  Više od 10 m ili bez kolne ceste do 20 m → upozorenje i rizik „Pristup javnoj prometnici”.
- Pojas uz cestu (odmak od regulacijskog pravca) koristi isto mjerilo (rub kolnika do 10 m od međe) umjesto 12 m od osi.

## Pretraga adrese: službeni kućni brojevi DGU-a
- Izvor: DGU, „Adrese” (INSPIRE AD), usluga preuzimanja `https://geoportal.dgu.hr/services/atom/ad/xml` → `INSPIRE_Addresses_(AD).zip` (cijela RH, ETRS89/LAEA).
  Feed navodi „ograničenje javnog pristupa prema čl. 13. st. 1. t. (e) INSPIRE Direktive”, a data.gov.hr za isti skup „Otvorenu dozvolu”: uvjete treba potvrditi s DGU-om.
- `tools/adrese/pripremi_adrese.py` uzima samo ulicu, kućni broj (s dodatkom, npr. 12A, 1/1), naselje i točku za otok Krk i područje Zagreba (okviri u skripti):
  `data/adr/ulice_krk.json`, `data/adr/ulice_zg.json` (ulice s naseljem, skupinom i sredinom) i `data/adr/b/NNN.json` (kućni brojevi po ulicama, 128 skupina). Oko 267.000 adresa, 7,5 MB.
- Pretraga: kućni broj iz upita, ulica po riječima naziva (točna riječ ispred iste riječi u drugom padežu), naselje kao prednost (u Zagrebu bez naselja prednost Zagreb).
  Pogodak → točka kuće (napomena s izvorom); broj nije u registru → sredina ulice uz upozorenje; ulica nije pronađena → OpenStreetMap (Nominatim) kao prije.
- Test: uzorak od 300 adresa, točna kuća za oko 98 %.


## Okolne zgrade u 3D prikazu i 3D skici (ZG3D, Grad Zagreb)

- Izvor: ZG3D 2022, 3D modeli postojećih zgrada, Grad Zagreb (data.gov.hr, Otvorena dozvola). Neslužbeni model; zgrade su snimljene 2008. ili 2022. i ne moraju odgovarati današnjem stanju.
- Priprema: `tools/zg3d/pripremi_zg3d.py <put do .gdb>` (pyogrio, shapely, numpy) čita geobazu gradske četvrti i reže je u kvadrate ~450 × 470 m u `data/zg3d/` (index.json + t/<red>_<stup>.json). Čuva se samo geometrija: tlocrt, visina do najnižeg dijela krova i krovne plohe (decimetri, delta-kodirano); nema atributa o osobama, adresa ni vlasnika. Cijeli Zagreb: 354.709 zgrada, 146 MB u 2212 kvadrata (oko 50 MB komprimirano).
- Aplikacija: `zg3dLoad(parcel)` dohvaća samo kvadrate oko čestice (krug 80 m), bez zgrada na samoj čestici. Izvan područja s podacima (i na Krku) ništa se ne prikazuje i ništa se ne izmišlja.
- Prikazi: interaktivni 3D (kvačica „Okolne zgrade”; krovovi kao stepenice 0,35 m), 3D skica u odjeljku Skica i u ispisu izvještaja (zidovi i krovne plohe, neutralno sivo), uz napomenu o izvoru i godini snimanja.
- Druge gradske četvrti: preuzeti ZIP s portala, pokrenuti skriptu s drugim izlaznim direktorijem pa spojiti `t/` i `kvadrati` u `index.json`.

### Okolne zgrade na otoku Krku (katastar DGU)
- Izvor: digitalni katastarski plan DGU-a (ATOM, sloj zgrada po k.o., isti paketi kao `data/kat_krk`). Pripremu radi `tools/zg3d/pripremi_krk_zgrade.py <mapa s ko-*> data/zg3d_krk <datum>`; 29.065 zgrada, 825 kvadrata, 1,9 MB (oko 0,6 MB komprimirano).
- Katastar ima samo tlocrt i način uporabe zgrade. Visina se PRETPOSTAVLJA prema vrsti zgrade (kuća 6,5 m, pomoćne oko 3 m, tablica `VISINE` u skripti), a zgrade se crtaju kao kvadri bez krova. Aplikacija to piše uz prikaz; ne tvrdi da su visine stvarne.
- Podzemne zgrade i tlocrti manji od ~4 m² preskaču se; gdje se stara i nova izmjera preklapaju, vrijedi novija.

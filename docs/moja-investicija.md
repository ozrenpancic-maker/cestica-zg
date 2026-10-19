# Moja investicija

Cilj: jedan model građevine povezuje simulator kuće na čestici sa svim izračunima. To su gradnja, priprema terena, doprinosi, krov i sunčana elektrana, vremenski plan i scenariji. Postojeći kalkulatori se nadograđuju, ne zamjenjuju. Ručni unos ostaje svugdje.

## Faze

| Faza | Sadržaj | Stanje |
| --- | --- | --- |
| I | Predlošci kuća, zajednički model građevine, simulator → procjena gradnje, troškovi po fazama | ugrađeno (Zagreb) |
| II | Priprema terena, temelji, prilaz, doprinosi i naknade iz modela | planirano |
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
| 1. Iskop i nasip za temelje | 3 % | da |
| 2. Temelji i temeljna ploča | 9 % | da |
| 2a. Podrum (iskop, zidovi i ploča; samo ako je odabran) | 850 €/m² tlocrta × standard (ključ u ruke) | da |
| 3. Konstrukcija, zidovi i međukatne ploče | 22 % | da |
| 4. Krov i pokrov | 9 % | da |
| 5. Vanjska stolarija i zatvaranje | 9 % | ne |
| 6. Instalacije | 17 % | ne |
| 7. Fasada i izolacija | 9 % | ne |
| 8. Unutarnji završni radovi | 22 % | ne |

- Faze 1–4 zajedno čine 43 %, što odgovara omjeru roh-bau / ključ u ruke za klasičnu gradnju (600 / 1.400 €/m²).
- Za roh-bau se cijena roh-baua dijeli samo na faze 1–4.
- Temeljna ploča montažne kuće pribraja se fazi 2. Podrum je posebna stavka 2a, a ne dio temelja (ispravak 19. 10. 2026.: 60 m² prizemnica s podrumom prije je u „temeljima” imala 58.560 €).

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

**Ručno provjerljiv primjer** (iz testova): klasična gradnja, ključ u ruke, standardni, P+1, 150 m².

- Jedinična cijena: 1.400 × 1,0 × 0,93 = 1.302 €/m².
- Gradnja: 1.302 € × 150 m² = 195.300 €.
- Iskop i nasip za temelje 3 % = 5.859 €; konstrukcija 22 % = 42.966 €; instalacije 17 % = 33.201 €.

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

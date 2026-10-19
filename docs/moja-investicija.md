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
| 3. Konstrukcija, zidovi i međukatne ploče | 22 % | da |
| 4. Krov i pokrov | 9 % | da |
| 5. Vanjska stolarija i zatvaranje | 9 % | ne |
| 6. Instalacije | 17 % | ne |
| 7. Fasada i izolacija | 9 % | ne |
| 8. Unutarnji završni radovi | 22 % | ne |

- Faze 1–4 zajedno čine 43 %, što odgovara omjeru roh-bau / ključ u ruke za klasičnu gradnju (600 / 1.400 €/m²).
- Za roh-bau se cijena roh-baua dijeli samo na faze 1–4.
- Temeljna ploča montažne kuće i podrum pribrajaju se fazi 2.

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

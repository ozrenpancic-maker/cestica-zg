# Napredne ideje: osunčanost, vjetar, pogled, promjene i usporedba

Stanje 24. 10. 2026., grana `razvoj`. Sve je u **naprednom** načinu, osim okvira „Promjene od zadnjeg pregleda” koji se vidi uvijek.

## 1. Osunčanost dvorišta (02, uz simulator kuće)

**Što računa:** sunčane sate po točkama čestice (mreža 1 m ili više kad je čestica velika, najviše oko 700 točaka) za odabrani dan:
- 21. 6.;
- 21. 3. (isto kao 23. 9.);
- 21. 12.

**Izračun**
- Položaj Sunca svakih 30 min (NOAA, `solarPos`), dok je Sunce više od 2°.
- Točka je u sjeni kad dužina od nje prema Suncu, duga H / tan(visina Sunca) (najviše 150 m), prolazi kroz tlocrt zgrade visine H.

**Prepreke**
- Kuća iz simulatora: visina sa sredinom krova (`pvKrovH`), a garaža 3 m.
- Okolne zgrade:
  - ZG3D 2022 u Zagrebu;
  - tlocrti katastra na Krku (visine pretpostavljene);
  - inače Topografska osnova Grada Zagreba uz upisanu visinu (`SUN.nb`).

**Prikaz**
- Prosječni sati, udio dvorišta sa 6 h i više te s 4 h i više, i najsunčaniji dio čestice.
- Skica čestice po razredima sati, uz mogućnost prikaza na karti.

**Pouzdanost C:** ravni teren, bez drveća, ograda i oblačnosti.

## 2. Vjetar i bura (03, uz prirodu i poplave)

**Izvor:** Open-Meteo, povijesni satni podaci 2023.–2025. (ERA5 / ERA5-Land, Copernicus): brzina i smjer vjetra na 10 m te udari.

**Prikaz**
- Ruža vjetrova: 16 sektora i 4 razreda brzine.
- Najčešći smjer.
- Smjer najviše jakih udara (od 17,2 m/s = 8 Bf) i najjači udar.
- Sati godišnje s jakim udarima iz smjera bure (0°–90°) i juga (90°–180°). To su samo smjerovi, ne meteorološka definicija.
- Preporuka zavjetrine: strana suprotna smjeru najjačih udara.

**Pouzdanost C:** model razlučivosti 10–25 km ne vidi lokalne prolaze (na Krku je bura mjestimice jača). Za projekt je mjerodavna norma i podaci DHMZ-a.

## 3. Pogled na more s kuće (02, uz simulator)

**Izračun**
- Iz sredine kuće, za oči 1,6 m iznad poda svake etaže (i potkrovlja), prati se teren u 180 smjerova (svaka 2°) do 8 km, u koracima od 25 m.
- More je ondje gdje je model visina na razini mora (≤ 0,5 m).
- Dio mora je vidljiv ako je kut prema površini mora veći od najvećeg kuta prema terenu i zgradama bliže kući. Zgrade do 150 m uzimaju se iz ZG3D ili katastra.
- Uključena je zakrivljenost Zemlje s lomom (k = 0,13).

**Model:** pločice z11 (Mapterhorn, inače AWS Terrain Tiles), piksel 27–54 m.

**Prikaz:** stupnjevi pogleda po etaži, glavni smjer, najbliže vidljivo more i polarni prikaz s prstenom za svaku etažu.

**Pouzdanost C:** bez drveća, ograda i novih zgrada. Pogled nije pravo, jer susjed može graditi prema planu.

## 4. Promjene na spremljenoj čestici

**Snimka stanja**
- Pri spremanju čestice sprema se snimka (`favs[].snap`).
- Polja: namjena, izgrađenost, zona, urbano pravilo, građevinsko područje, status i izrada UPU-a, planovi u izradi i važeći, ZK uložak, površine u ZK i katastru, poplave, Natura, zaštićeno područje te tereti iz sažetka.

**Usporedba pri otvaranju**
- Pri ponovnom otvaranju, oko 2,5 s nakon što se podaci učitaju, uspoređuju se samo polja koja postoje i u snimci i sada. Podatak koji se još učitava ili servis koji ne odgovara nije promjena.
- Okvir „Promjene od zadnjeg pregleda” prikazuje „bilo” i „sada”.
- „Označi kao pregledano” sprema novo stanje.

## 5. Usporedba spremljenih čestica

- Tablica, odnosno kartice na mobitelu, dobila je retke: cijena građevinskog zemljišta u općini, poplave, internet, iskop i nasip, osunčanost, pogled na more i vjetar.
- Vrijednosti su zadnje poznate (`favs[].zadnje`) iz vremena kad je čestica bila otvorena. Prazno znači da odjeljak još nije izračunat.

## Testovi

`tests/run.js`, skupina `napTests`. Provjerava:
- sjenu zida (u sjeni, na Suncu, izvan sjene);
- trajanje dana 21. 6. i 21. 12.;
- prikaz osunčanosti;
- ružu vjetrova na sintetičkim podacima i preporuku zavjetrine;
- pogled: brdo zaklanja sjever, more na jugu, bliska zgrada zaklanja smjer;
- snimku pri spremanju, prikaz promjene, „Označi kao pregledano” i to da podatak koji nedostaje nije promjena.

Usput: test „Sažetak … Natura” sada čeka asinkrono osvježavanje (do 2 s) umjesto fiksnih 80 ms, pa više ne pada povremeno.

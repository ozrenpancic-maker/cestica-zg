# Skener građevinskih čestica (Grad Zagreb)

Uključuje se u popisu **Slojevi → Skener građevinskih čestica**. Radi od zuma 17, za vidljivi dio karte.

## Što radi

Za svaku katastarsku česticu u vidljivom dijelu karte (gradski sloj `KatastarskeCestice_2023`):

1. **Namjena** se određuje u točki unutar čestice (GIS baza planirane namjene). Dalje se gledaju samo čestice u građevinskom području (`BUILDABLE`).
2. **Urbano pravilo** se traži redom:
   - GUP Grada Zagreba (karta 4a);
   - ako ga nema, GUP Sesveta (prijedlog izmjena, nije na snazi);
   - izvan GUP-ova točka 2.3.1. PPGZ-a.
   - Isti postupak (`ruleLookup`) koristi i analiza čestice.
3. **Najmanja površina građevne čestice** čita se iz teksta pravila za odabrani tip kuće (slobodnostojeća, dvojna, u nizu). Parser je isti kao u analizi (`parseParams`). Izvor je članak i oznaka pravila, npr. pravilo 2.2., GUP čl. 69: najmanje 600 m².
4. **Zgrade** dolaze iz topografske osnove Grada (sloj `Objekti`). Čestica je izgrađena kad je središte neke zgrade na njoj.
5. **Obveza UPU-a** dolazi iz karte 4b (procedure).

## Razredi na karti

| Boja | Razred | Uvjet |
|---|---|---|
| zelena | potencijalna građevna čestica | građevinsko područje, bez zgrade, površina ≥ najmanje propisane |
| narančasta | dovoljno velika, ali u obuhvatu UPU-a | kao zelena; gradnja u pravilu tek nakon donošenja UPU-a |
| plavkasta | izgrađena, dovoljno velika | ima zgradu, površina ≥ najmanje propisane |
| žuta | manja od propisane, s posebnom odredbom | pravilo ima odredbu za manje čestice (rekonstrukcija, zamjenska gradnja, interpolacija) |
| crvena isprekidana | premala | površina < najmanje propisane |
| siva isprekidana | nije moguće odrediti | pravilo nije pronađeno ili ne propisuje najmanju površinu |

Nema tolerancije: 599 m² nije dovoljno uz najmanje 600 m², jer pravilo ne dopušta odstupanje.

Uz gumb „Slojevi” je sažetak s brojem čestica po razredu. U popisu slojeva je legenda i do 12 najvećih potencijalnih čestica. Dodir na česticu u popisu ili na karti otvara punu analizu te čestice.

## Ograničenja

- **Površina je grafička** (iz katastarskog plana). Mjerodavna je upisana površina iz katastra ili zemljišne knjige; analiza čestice je provjerava preko OSS-a.
- **Ne provjerava se:**
  - širina čestice uz ulicu;
  - pristup prometnoj površini;
  - komunalna opremljenost;
  - posebni uvjeti (klizišta, kulturna dobra, vodozaštita);
  - vlasništvo i tereti.
  - Za sve to treba otvoriti česticu.
- **Namjena i pravilo** određuju se u jednoj točki. Ako čestica leži u dvije zone, razred vrijedi za dio s tom točkom.
- **Radi samo za Grad Zagreb.** Za Krk i ostatak Hrvatske nema gradskih slojeva namjene i urbanih pravila u istom obliku.
- Pri velikom broju čestica servis vraća najviše 2000. Tada skener javlja da treba približiti kartu.

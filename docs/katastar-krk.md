# Katastarske čestice za otok Krk

Stanje 19. 10. 2026., grana `razvoj`.

## Zašto ne živi servis

DGU INSPIRE WFS (`api.uredjenazemlja.hr/services/inspire/cp/wfs`) za Krk ne radi pouzdano: upit u JSON-u ne odgovori, a upit u GML-u vraća grešku baze `ORA-01000: maximum open cursors exceeded` (provjereno 19. 10. 2026. u pregledniku). I kad radi, prostorni upit traje oko 15 s.

## Izvor

DGU, usluga preuzimanja digitalnog katastarskog plana (ATOM): `https://oss.uredjenazemlja.hr/oss/public/atom/ko-<matični broj>.zip`, GML, HTRS96/TM, tjedno osvježavanje. Katalog DGU-a: „nema ograničenja javnom pristupu”, „nema uvjeta za pristup i korištenje”.

Preuzete katastarske općine (24): Baška 315834, Batomalj 315842, Bogovići 315869, Dobrinj 315877, Draga Bašćanska 315885, Garica 315893, Kornić 315907, Krk 315915, Krk-grad 315923, Linardići 315931, Miholjice 315940, Omišalj 315958, Poljica 315966, Punat 315974, Skrbčići 315982, Soline 316008, Stara Baška 316016, Sužan 316024, Sveti Anton 316032, Vrbnik 316059, Vrh 316067, Malinska-Dubašnica 337269, Baška-Nova 337285, Omišalj-Njivice 338427.

## Priprema i provjera

- `tools/katastar/pripremi_krk.py`: 210.862 čestice u 593 kvadrata (`data/kat_krk/`, oko 50 MB, 19 MB komprimirano; jedan dodir učita jedan kvadrat, najviše oko 0,5 MB, komprimirano oko 150 kB).
- Koordinate u milijuntinkama stupnja (oko 0,1 m), zapisane kao razlike.
- Preklapanja stare i nove izmjere (najviše Omišalj i Omišalj-Njivice, 949 čestica, 30 ha): prednost ima novija k.o. (Omišalj-Njivice, Baška-Nova, Malinska-Dubašnica); aplikacija to napiše.
- `tools/katastar/provjeri_krk.py`: 600 slučajnih točaka, čestica iz kvadrata = čestica iz izvornog GML-a u 600/600 slučajeva.

## Prikaz

Broj čestice, k.o., površina iz geometrije i grafička površina iz katastra, granica na karti, stanje podataka. Grafička površina nije nužno ista kao površina upisana u posjedovni list ili zemljišnu knjigu.

Uz grafičku površinu prikazuje se i **površina upisana u zemljišnu knjigu**:
- automatski iz OSS-a preko posrednika (`tools/oss-posrednik`, uključuje se upisom adrese u `SRC_KRK.oss`), uz broj ZK uloška, površinu iz posjedovnog lista i dijelove čestice; podatak je neslužben;
- ili ručnim unosom / iz učitanog PDF izvatka (ima prednost pred OSS-om).
Uvjeti gradnje i dalje se računaju s grafičkom površinom.

## Osvježavanje

Preuzeti ZIP-ove istom PowerShell naredbom (popis brojeva gore), raspakirati u `ko-<broj>/` i pokrenuti obje skripte.

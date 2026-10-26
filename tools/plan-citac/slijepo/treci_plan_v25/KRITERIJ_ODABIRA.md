# Kriterij odabira trećeg plana za slijepi test v2.5

Zapisano i commitano **prije** pregleda popisa odluka (26. 10. 2026.). Odluku o načinu odabira donio je sudac (Ozren Pančić): »Ti biraš po kriteriju«.

1. **Izvor:** Službene novine Primorsko-goranske županije (sn.pgz.hr), isti izvor kao za Novi Vinodolski.
2. **Redoslijed:** odluke se pregledavaju od najnovijeg izdanja prema starijima.
3. **Uvjet po naslovu:** prva odluka čiji naslov glasi »Odluka o donošenju …« (ili »… izmjena i dopuna …«) **urbanističkog plana uređenja** ili **prostornog plana uređenja** grada/općine.
4. **Isključeno:** svi planovi Grada Krka (uključujući Kornić i ostala naselja Grada Krka), Općine Omišalj, Malinska-Dubašnica, Punat, Dobrinj, Vrbnik i Baška se **ne** isključuju; isključen je i svaki plan Grada Novog Vinodolskog. Isključen je svaki plan koji je već korišten u razvoju ili testiranju.
5. **Odabir samo po naslovu.** Odredbe se ne čitaju prije odabira.
6. **Provjera prikladnosti bez čitanja odredbi:** nad odabranim tekstom pokreće se zamrznuti `slijepi_v25.py odaberi` (isti kriterij članaka kao v2.2/v2.3). Ako ne vrati nijedan članak, uzima se sljedeća odluka po istom redoslijedu; razlog se zapisuje.
7. **Postupak nakon odabira:** izvor, datum i SHA-256 zapisuju se u `IZVOR.md`; zatim `tekst` → jedan neovisni označivač samo s tekstom i uputama v1.2 → zaseban commit oznaka → integritet (`ZAMRZNUTO_v2_5.json`, izvor, oznake) → `usporedi` (strogo i pravila_v25).

# Pregledani referentni skup oznaka v1

**Ovo nije pravna potvrda.** Skup pokazuje što tekst doslovno kaže i gdje je nejasan, za mjerenje čitača. Pravno potvrđenih pravila: 0.

## Postupak
1. Upute za označavanje v1 (`UPUTE_OZNACAVANJA_v1.md`).
2. Dva neovisna označivača:
   - A čita kao stručnjak za prostorno planiranje;
   - B čita strogo doslovno, kao upravni pravnik.
   Svaki je radio u zasebnom kontekstu, bez alata, bez uvida u čitač i u tuđe oznake. Svi citati su doslovni.
3. Oznake su zamrznute prije usporedbe (commitovi `58e4d7a` i sljedeći za G3/B).
4. Strojno sparivanje (`spoji_oznake.py`) dalo je 130 sporova (`sporovi.json`).
5. Sudac Ozren Pančić odlučio je o svih 130 sporova 26. 10. 2026. na stranici »Sudac oznaka v1« (`odluke_suca_v1.json`, doslovno).
6. Sastavljanje: `sastavi_referencu.py` → `referenca_v1.json`. Dva prolaza daju isti SHA-256.

## Rezultat

| Skupina | Zapisa | JASAN | PREGLED | s prihvatljivom alternativom | odlučio sudac |
|---|---|---|---|---|---|
| PPUG čl. 22. i 23. | 61 | 48 | 13 | 16 | 29 |
| PPUG čl. 25. i 33. | 33 | 13 | 20 | 0 | 6 |
| PPUG čl. 20., 38., 39., 50. | 77 | 42 | 35 | 14 | 34 |
| UPU 1 čl. 14. | 34 | 13 | 21 | 2 | 22 |
| UPU 1 čl. 24. | 63 | 36 | 27 | 10 | 36 |
| **Ukupno** | **268** | **152** | **116** | **42** | **127** |

**Odluke suca:** A 43, B 44, oba 39, ispravak 4. Od toga je 58 primijenjeno preko uzorka.

**Kako su odluke ugrađene:**
- 141 zapis u kojem su se A i B slagali ulazi bez izmjene.
- Kod odluke »oba« vrijedi zapis A, a vrijednosti B za razlikovna polja bilježe se u `prihvatljivo`. Čitač je točan ako pogodi bilo koju.
- Svih 16 zapisa koje je imao samo jedan označivač sudac je zadržao.

## Mjesta gdje sam primijenio odluku uz tumačenje (za provjeru suca)
1. **Tri dvostruka zapisa (PPUG čl. 20., 39., 50., 6. alineja, smjer nagiba krova).**
   - Sparivanje nije prepoznalo da je to isto pravilo, jer se razlikuju i citat i slobodni naziv parametra.
   - Sudac je zadržao oba zapisa. Spojio sam ih u jedan, a citat i naziv iz B ostali su kao prihvatljivi.
2. **UPU 1 čl. 14., parkiranje i 60 % zelenila; ispravak »Nejasno«.** Vrsta građevine se ne upisuje, a zapis ostaje PREGLED s razlogom TUMACENJE.
3. **UPU 1 čl. 14., visina 8,0 m; ispravak »Od najniže poravnate površine«.**
   - Citat ne navodi točku mjerenja, pa je nisam upisao u uvjet (pravilo »ništa se ne izmišlja«).
   - Ispravak je zabilježen u `ispravak_suca` s oznakom `ispravak_izvan_teksta`, a zapis ostaje PREGLED.
4. **PPUG čl. 25., istak h/2; ispravak »h je visina, 4 m je minimum, za 9 m visine 4,5 m«.**
   - Zapis je upisan kao `max(h/2, X)` s X = 4,0 m, uz uvjet o otvorima iz citata B.
   - Ostaje PREGLED, jer točke mjerenja visine nisu u tekstu.

## Napomene
- Jedno obrazloženje oslanja se na okolnost izvan teksta: »Podrum nije moguć ako je uz more«. Zabilježeno je doslovno.
- Stranica suca ostaje dostupna, a odluke se mogu mijenjati. Svaka izmjena traži novi izvoz i novi SHA-256 skupa (v1.1). Ovaj skup se ne mijenja.
- Skup je razvojni za UPU 1 i PPUG: tekstovi su poznati razvoju čitača. Nije zamjena za slijepi test na neviđenom planu (faza E).

## Kontrolne sume
| Datoteka | SHA-256 |
|---|---|
| referenca_v1.json | `e6b2f7a5282d99694ad8cd0cd5939e5db350fa28c8736ffd6e1eddd44a7f85cc` |
| odluke_suca_v1.json | `eab06151f4d1fa36494c5daf5a172333809cea805c9fab088485ffb7a6464ac9` |
| sastavi_referencu.py | `1fb5da4ccfb3b383f1afe1c0e08e81b6452e5e0f2c8a29a5b570c6ba9a679aa0` |

Ulazne kontrolne sume (tekstovi, oznake A i B, upute, sporovi, odluke) zapisane su u `referenca_v1.json` pod `ulazi`.

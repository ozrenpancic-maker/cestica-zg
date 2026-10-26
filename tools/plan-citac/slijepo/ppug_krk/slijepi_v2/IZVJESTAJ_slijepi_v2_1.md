# Slijepi test v2.1: UPU 1 – Krk, čl. 14. i 24.

## Postupak
| Korak | Commit | Kontrolna suma |
|---|---|---|
| Zamrznut čitač v2.1 (`ZAMRZNUTO_v2.json`) | `6e798ae` | `5971a085…` |
| Odabir članaka (strojni kriterij, `odabir.json`) i tekst za označivača | `6e798ae` | tekst `e3a0dcc6…` |
| Neovisne oznake, zamrznute prije usporedbe | `2b7b607` | `91d187e430c92fc74c8a9f8c8e655a04b3263108021ed5a38a32654150b30ee6` |
| Usporedba neizmijenjenim čitačem (`usporedba_slijepi_v2_1.json`) | ovaj commit | `717011fe…` |

- **Označivač:** pomoćni agent u zasebnom kontekstu, bez alata (isti model kao razvojni).
  - Dobio je doslovni tekst i zatvoreni popis naziva parametara iz `mapiranje_v2.json`.
  - Izlaze modula nije vidio.
- **Kriterij odabira:** prvi kriterij nije pogodio nijedan članak, pa je promijenjen. Pritom su viđeni samo brojevi pogodaka i duljine članaka, ne tekst (`odabir.json`).
- **Provjera oznaka:** svih 101 zapis ima citat, članak, stavak (null), parametar, operator, vrijednost, uvjet i jednoznačnost. Svi citati su doslovno u ulaznom tekstu.

## Rezultat po članku
| | čl. 14. | čl. 24. | ukupno |
|---|---|---|---|
| oznaka (JASAN / PREGLED) | 36 (30 / 6) | 65 (46 / 19) | 101 |
| od toga parametar izvan zatvorenog popisa (»drugo: …«) | 24 | 26 | 50 |
| točno prihvaćeno | 0 | 0 | 0 |
| pogrešno prihvaćeno | 0 | 0 | 0 |
| pravilno upućeno na pregled (oznaka PREGLED) | 0 | 0 | 0 |
| nepotrebno upućeno na pregled (oznaka JASAN) | 0 | 0 | 0 |
| propušteno | 36 | 65 | 101 |
| dodatni prijedlozi bez referentne oznake | 0 | 0 | 0 |

**Pokrivenost na neviđenom planu je 0 %, uz 0 pogrešno prihvaćenih pravila.**

Oba članka su odbijena na razini članka (`SKUPINA_NEPOZNATA`). Nijedan izdvojeni zapis nije nastao, pa nema ni izdvajanja ni razumijevanja koje bi se moglo ocijeniti.

## Dijagnostika nakon rezultata
Ovo su podaci za v2.2 (`dijagnostika_odredbi.json`); kod v2.1 nije mijenjan. Odredbe su pokrenute kroz `odredba()` bez provjere na razini članka: 0 prepoznato, 17 odbijeno s brojem, 10 bez broja.

Uzroci, u redoslijedu utjecaja:
1. **Vrsta građevine:** »sportsko-rekreacijske građevine«, »hotel«, »ugostiteljsko-turističke namjene« i »pomoćne građevine« nisu u rječniku skupina.
2. **Alineje s velikim početnim slovom** (»- Najmanja …«) se ne razdvajaju, jer v1 `alineje()` traži malo slovo. Cijeli članak postaje jedna jedinica.
3. **Predmeti ovise o velikom ili malom slovu i o točnom redoslijedu riječi.**
   - Ne prepoznaju se: »Najmanja dopuštena udaljenost građevine od regulacijskog pravca za ostale (pristupne) ceste«, »koeficijent iskorištenosti« (umjesto »iskoristivosti«).
   - Ne prepoznaju se ni izrazi tipa »ne može biti manja od«.
4. **Numerirani podnaslovi** (»3. veličina i smještaj građevina na građevnoj čestici«) se ne koriste kao kontekst.
5. **Novi oblici odredbi:**
   - postotci zelenila;
   - (h1+h2)/2;
   - »ne povećava se ako je postojeće veće od«;
   - iznimke vezane uz katastarsku česticu.

Čl. 14. i 24. su nakon ove analize poznati razvoju. Za v2.2 ne mogu služiti kao slijepi skup.

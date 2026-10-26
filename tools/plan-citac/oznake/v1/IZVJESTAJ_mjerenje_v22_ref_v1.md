# Zamrznuta v2.2 na pregledanom referentnom skupu v1

- Kod čitača nije mijenjan. Kontrolne sume iz `ZAMRZNUTO_v2_2.json` i SHA-256 reference (`e6b2f7a5…`) provjeravaju se prije i poslije mjerenja.
- Dva prolaza daju isti izlaz.
- **Skup je razvojni** (tekstovi su bili poznati razvoju v2.2), pa ovo nije dokaz generalizacije.
- Pravno potvrđenih pravila: 0.

## Što je dodano usporedbi (`mjeri_v22.py`, `mapiranje_ref_v1.json`)
Usporedba polja je zamrznuta `usporedi_v22.razlike`. Dodano je samo:
1. **Nazivi parametara** iz zatvorenog popisa uputa v1, za četiri šifre čitača (etaže, zelenilo, udaljenost između građevina, dopuštenost gradnje). Mapiraju se samo nazivi, nikad vrijednosti.
2. **Nazivi oblika:** »dvoj« znači »dvojna«, a »dvojna/ugrađena« odgovara »dvojna« ili »ugrađena«.
3. **Odluke suca »oba«:** pravilo je točno ako odgovara bilo kojoj prihvaćenoj inačici.
4. **Dva pravila granularnosti** iz uputa v1. Broje se zasebno, kao i dosadašnja:
   - **TOCKA_ILI_ALINEJA_v1** (24 slučaja): upute bilježe alineju kao »-«, a čitač slovo točke u kojoj je ta alineja.
   - **ALTERNATIVA_NIJE_VRSTA_v1** (3 slučaja): upute v1 § 3 kažu da ALTERNATIVA nije vrsta pravila.

## Rezultat

| Skupina | Oznaka (JASAN) | Točno | + granularnost | Pogrešno | Pravilno na pregled | Nepotrebno na pregled | Pregled bez oznake | Propušteno | Preciznost | Prihvaćeno od JASAN |
|---|---|---|---|---|---|---|---|---|---|---|
| PPUG čl. 22./23. | 61 (48) | 7 | 26 | 7 | 3 | 1 | 11 | 24 | 0,825 | 0,688 |
| PPUG čl. 25./33. | 33 (13) | 10 | 2 | 1 | 9 | 1 | 11 | 11 | 0,923 | 0,923 |
| PPUG čl. 20./38./39./50. | 77 (42) | 2 | 0 | 5 | 0 | 0 | 5 | 75 | 0,286 | 0,048 |
| UPU 1 čl. 14. | 34 (13) | 6 | 0 | 1 | 2 | 1 | 5 | 25 | 0,857 | 0,462 |
| UPU 1 čl. 24. | 63 (36) | 6 | 2 | 2 | 0 | 1 | 4 | 54 | 0,800 | 0,222 |
| **Ukupno** | **268 (152)** | **31** | **30** | **16** | **14** | **4** | **36** | **189** | **0,792** | **0,401** |

Preciznost = (točno + granularnost) / (točno + granularnost + pogrešno).

## Šesnaest »pogrešno prihvaćenih«: nijedna pogrešna brojka
- **12 slučajeva: nedostaje uvjet iz uvoda.** Riječ je o uvjetima »na građevnoj čestici uz (više)obiteljsku kuću« (PPUG 23.) i »uz građevine … namjene« (PPUG 20., 39., 50.).
  - Vrijednost, parametar i vrsta građevine su točni.
  - U PPUG-u 23. uvjet je u referenci po odluci suca (»Jer spominje uz obiteljsku kuću«). U čl. 20., 39. i 50. oba su ga označivača upisala jednako.
  - v2.2 taj kontekst drži na razini članka i ne upisuje ga u uvjet pravila. Prema referenci, pravilo je zato nepotpuno.
- **2 slučaja (UPU 1 čl. 24., 4,0 m i 6,0 m od regulacijskog pravca):** čitač daje UVJETNO, a referenca OSNOVNO.
- **1 slučaj (PPUG 25., način gradnje):** čitač daje »= samostojeće«, a referenca dopuštenje (sudac: »mogu i može su jednoznačni«).
- **1 slučaj (UPU 1 čl. 14., 400 m²):** čitaču nedostaje oznaka »(nova)« uz vrstu građevine.

## Glavni nalazi
1. **Pokrivenost je i dalje glavna slabost.**
   - Propušteno je 189 od 268 zapisa: 90 JASAN, 99 PREGLED.
   - Najslabiji je PPUG čl. 20./38./39./50.: čitač ondje predlaže samo 12 pravila na 77 oznaka.
2. **Kontekstni uvjet iz uvoda stavka sustavno nedostaje.** Ispravak bi uklonio 12 od 16 pogrešaka.
   - To je posao za v2.3, ne za v2.2.
   - Popravak se ne smije mjeriti na ovom skupu kao na slijepom testu.
3. **»Pregled bez oznake« (36):** čitač izdvaja i šalje na pregled pravila koja se ne sparuju ni s jednim zapisom reference. Najčešći razlozi:
   - granica čestice;
   - tipografska pogreška;
   - opseg;
   - dio odredbe neprepoznat.

## Datoteke
| Datoteka | SHA-256 |
|---|---|
| mjerenje_v22_ref_v1.json | `e78aba1f9c77b06efa27d5d8def8de892ebf4c7fce6d5144e9b6946be11ffc9c` |
| referenca_v1.json (ulaz) | `e6b2f7a5282d99694ad8cd0cd5939e5db350fa28c8736ffd6e1eddd44a7f85cc` |
| ZAMRZNUTO_v2_2.json (ulaz) | `5c8b834528cbb55833b2ea034817c0f7433e38af48e9d56dc5603569d807b733` |

## Dopuna v1.1: odluka suca o kontekstu članka (26. 10. 2026.)
Zapis je u `odluke_suca_v1_1.json`.
- **Izjava suca:** »Za ovih 12 više obiteljska kuća ili građevina stambene namjene ima isto značenje«.
- **Pojašnjenje za čl. 39. i 50.:** »ne, uvjet mora biti upisan«.
- **Primjena:**
  - uvjet iz uvoda stavka ne mora biti u uvjetu pravila samo za čl. 22. st. 2., 23. st. 2. i 20. st. 3. (obiteljska i višeobiteljska kuća, građevine stambene namjene);
  - za čl. 39. st. 2. (društvene i sportsko-rekreacijske namjene) i 50. st. 4. (gospodarske namjene) uvjet mora biti upisan.
- Takvi se slučajevi broje zasebno, kao pravilo KONTEKST_CLANKA_v1_1.
- Referentni skup v1 i mjerenje v1 ne mijenjaju se. Novo mjerenje je u `mjerenje_v22_ref_v1_1.json`.

| | v1 | v1.1 |
|---|---|---|
| točno | 31 | 31 |
| točno uz pravilo granularnosti | 30 | 39 |
| pogrešno prihvaćeno | 16 | 7 |
| propušteno | 189 | 178 |
| preciznost prihvaćenih | 0,792 | 0,909 |
| prihvaćeno od JASAN | 0,401 | 0,461 |

**Preostalih 7 pogrešaka; nijedna nije pogrešna brojka:**
- **3 slučaja (čl. 39. i 50.):** nedostaje uvjet »uz građevine … namjene«. Po odluci suca to je stvarna pogreška čitača.
- **2 slučaja (UPU 1 čl. 24.):** UVJETNO ili OSNOVNO.
- **1 slučaj (PPUG čl. 25.):** jednakost ili dopuštenje.
- **1 slučaj (UPU 1 čl. 14.):** nedostaje »(nova)«.

| Datoteka | SHA-256 |
|---|---|
| odluke_suca_v1_1.json | `492b3e8de4ba32a0795e58124ae6161ba246d42c51821f54b8676f82714ac0d7` |
| mjerenje_v22_ref_v1_1.json | `8f35a36e0248f9abf3f8f6da637274d64798f64e7998eade10621d0920235c14` |

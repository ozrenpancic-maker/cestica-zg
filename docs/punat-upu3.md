# UPU 3 Punat u aplikaciji

Stanje 5. 11. 2026., grana `punat-upu3` (iz `sazetak-zone-upu2`). Nije spojeno u `razvoj` ni u `main`.

## Što radi

Kad evidencija planova PGŽ-a na točki u Općini Punat daje važeći UPU 3 (centralno naselje N1), aplikacija više ne javlja „plan nije obrađen”. Računa uvjete gradnje iz UPU-a 3 i pri tome:

1. **Prepoznaje plan.** Naziv u evidenciji mora odgovarati `UPU\s*3\b…Punat` i jedinici `PUNAT`. UPU 3 Jurandvor u Baški se ne prepoznaje. Izvan UPU-a 3 i dalje vrijedi PPUO Punat.
2. **Zonu bira korisnik.** Zona je samo na grafičkom prikazu br. 4 (raster) i ostaje razina C. Ponuđene su:
   - S1, S2, M1: uvjeti iz čl. 46.–46c.;
   - M2: čl. 54c.–54e. nisu obrađeni, pa nema izračuna;
   - druga zona.
3. **Dio građevinskog područja.** O tome ovise kis i visina. Izbor *izgrađeni / neizgrađeni* je novi izbornik.
   - Bez izbora koristi se atribut izgrađenosti iz županijskog sloja (PPUO). To je razina B, uz otvoren uvjet da granica prema UPU-u nije potvrđena.
   - Ako sloj ne daje jednoznačan podatak, nema izračuna.
4. **Obiteljska kuća, tri načina gradnje:**

| | slobodnostojeća | dvojna | jedinica niza |
|---|---|---|---|
| najmanja čestica | 450 m² (iznimno 405 m², interpolacija −10 %) | 225 m² | 150 m² |
| kig | 0,25 | 0,3 | 0,4 |
| kis izgrađeni / neizgrađeni | 1,0 / 0,85 | 1,3 / 1,05 | 1,8 / 1,4 |
| najveći tlocrt (čl. 46.) | 150 m², 200 m² na čestici > 1000 m² | 75 m² | nije izdvojen (samo kig) |
| najmanji tlocrt | 60 m² | — | — |
| visina izgrađeni / neizgrađeni | 9,0 / 7,0 m | 9,0 / 7,0 m | 9,0 / 7,0 m |
| odmak od međa | h/2, najmanje 3 m; 6 m od susjednih građevina | isto | isto |

   Za završnu jedinicu niza plan ima druge uvjete. Oni se prikazuju kao napomena, ali se ne računaju.

## Odakle su vrijednosti

Sve vrijednosti i navodi prenose se skriptom `tools/sn-pgz/punat_u_aplikaciju.py` iz baze s citatima `data/pravila-sn/punat-upu3.json`, prema id-u pravila. Ručno se ne upisuje nijedna brojka. Izvedena je samo granica iznimke (450 m² − 10 % = 405 m²), uz navod čl. 46a. t. 8. Provjera: `python3 tools/sn-pgz/punat_u_aplikaciju.py --provjeri`.

| Izvor | Što daje | Status teksta |
|---|---|---|
| II. izmjene, SN PGŽ 3/2020 (id 41087) | čl. 46. (tlocrt), čl. 46a.–46c. t. 4, 6, 8 (zelenilo, interpolacija) | cijeli tekst sa sn.pgz.hr |
| ciljane izmjene, SN PGŽ 13/2016 (id 33933) | čl. 46a.–46c. t. 1–3: najmanja čestica, kig, kis, visina, odmaci (2020. nisu mijenjani) | **izvoz treće strane, nije uspoređen sa sn.pgz.hr** |

U aplikaciji svaki navod nosi članak, točku i glasilo. Navodi iz 2016. označeni su kao »navod iz izvoza teksta treće strane«, uz usklađenost izvora *nepoznata*, pa su svi pokazatelji **uvjetni** (C). Pravna aktualnost je NIJE_POTVRDENO:
- pročišćeni tekst ne postoji;
- tumačenje iz 2012. nije pronađeno;
- III. izmjene i dopune su u izradi.

Pravno potvrđenih pravila ostaje 0.

## Što nije obrađeno

- **Ostale vrste i zone:**
  - višestambene građevine (čl. 50a.): zona primjene i odmak od 4 m traže zasebnu obradu;
  - zona M2 (čl. 54c.–54e.);
  - čl. 50b.–50e. i 85a.–85d.
- **Uvjeti koji nisu izdvojeni iz teksta:**
  - udaljenost od regulacijskog pravca (Podaci nisu dostupni);
  - parkiranje (poglavlje 5.);
  - definicije podruma i etaža (čl. 3. i 5.);
  - najveći tlocrt i etaže za građevine u nizu.
- **Ostalo:**
  - posebni uvjeti za pojedine čestice (npr. k.č. 3307);
  - prijedlog zone iz rastera, jer listovi UPU-a 3 u katalogu PP_RASTERI i njihova legenda nisu obrađeni.

## Promjene u zajedničkom kodu

- `krkRuleStateJls`: obrađeni UPU u jedinici izvan pilota (polje `jls` u pravilu).
- `krkCit` i karika »članak«: navod može imati vlastiti članak, glasilo i status izvora. Za UPU 2 prikaz je nepromijenjen.
- `krkTlMax`: najveći tlocrt ovisan o površini čestice.
- `P.uvjeti`: otvoreni uvjeti iz pravila.
- Uvjeti visine (kota terena, kosi teren) sada ovise o pravilu, a ne vrijede za svaki plan.

Usporedba prije i poslije za 735/76, 735/54 i Zagreb 1541/2: svi pokazatelji su isti. Vrijednosti postojećih pravila čuva isti SHA-256 kao prije; UPU 3 ima vlastitu provjeru prema bazi.

## Testovi

`tests/run.js`: 1050 / 1050. Novih testova za UPU 3 ima 16:
- prepoznavanje plana i obvezan izbor zone;
- izračun u izgrađenom i neizgrađenom dijelu;
- dvojna kuća i niz;
- iznimka od 405 m² i tlocrt od 200 m² iznad 1000 m²;
- zona M2 i zona S1;
- blokada bez podatka o izgrađenosti;
- UPU 3 Jurandvor se ne prepoznaje;
- PPUO izvan UPU-a;
- jednakost svih 26 navoda s bazom i provjera da je svaka brojka u svom navodu.

Uz to prolaze:
- Plan Integrity: 9, 16, 9 i 15 testova;
- audit 9 / 9;
- `tools/sn-pgz/test_sn_pgz.py`;
- mobilni testovi: layout, interaction, krk, pwa 42 / 42, sazetak.

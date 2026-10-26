# plan-citac (EKSPERIMENT)

Čitač odluke o prostornom planu iz PDF-a Službenih novina PGŽ (dvostupačni prijelom). Zaseban alat: ne dira aplikaciju, `rules_krk.json`, GIS ni zoniranje i **ništa ne potvrđuje pravno** (`automatska_potvrda: 0`, `pravno_potvrdeno: false`).

    pip install pymupdf
    python3 citac.py ../../tests/pgz-odgovori/735-76-kornic-2026-10-22/sn-19-16/odluka_34138.pdf --naslov "UPU 2 - Kornić" --clanaka 108 -o izlaz/upu2_kornic_sn_19_2016.json
    python3 -m unittest -v test_citac

PyMuPDF je licenciran pod AGPL-3.0. Koristi se samo kao lokalni alat i ne ugrađuje se u aplikaciju.

## Što radi
1. **Granice odluke po sadržaju:** početak je podebljani naslov »ODLUKU o donošenju …« uz zadani naziv plana. Kraj je prvi »Klasa:« nakon toga. Ako naslov nije nađen točno jednom, vraća `ABSTAIN_GRANICA_ODLUKE`.
2. **Članci:** »Članak N.« na početku bloka, u redoslijedu čitanja (stranica → lijevi pa desni stupac → odozgo). Provjerava niz 1…N.
3. **Znakovi iz glifova:** dijakritik (ˇ ´ ¯) spaja se sa slovom ispod. Razmaci se određuju po položaju glifova. Sitne znamenke postaju indeks ili eksponent (»M1₁«, »m²«).
4. **Zaglavlja stranica** (»Stranica N — broj 19 … SLUŽBENE NOVINE«) uklanjaju se.
5. **Naslovi poglavlja** (numerirani blokovi iza kojih slijedi članak) odvajaju se u polje `poglavlje`. Naslov bez vlastitog članka ostaje u tekstu i bilježi se u `unutarnji_naslovi`.
6. **Tablice** (skupine vektorskih crta) se ne rekonstruiraju. Članak dobiva oznaku `[TABLICA – nije pouzdano rekonstruirana …]` i `status_tablica: TABLICA_NEPOUZDANA`. Izvorne ćelije čuvaju se u `tablice[].blokovi`.
7. **Rastavljene riječi** se spajaju, i preko stupca ili stranice. Crtica ostaje ako se ista složenica s crticom pojavljuje drugdje u dokumentu (»Primorsko-goranske«). Svaka odluka se bilježi (`crtice`), a izvorni tekst bloka čuva se u `sirovo`.
8. **`brojevi(tekst)` i `ima_broj(tekst, vrijednost, jedinica)`:**
   - prepoznaju »0,25,«, »0,75, a iznimno 1,0« i »40 %« kao udio 0,4;
   - ne nalaze »1,0« u »1,5«;
   - preskaču oznake stavaka »(1)«, pozive na članke, stavke i točke, k.č., broj glasila, mjerilo, oznake prikaza i cesta, godine i nabrajanja.
9. **`navod(s)`:** članak, raspon članaka, stavci odvojeno od članaka, točka pojmovnika, točka slovom »d)« i oznaka plana.

## Neriješeno (stanje: SN PGŽ 19/2016, UPU 2 Kornić)
- **Prepoznavanje je provjereno samo na ovom PDF-u.** Sidra (naslov odluke, »Klasa:«), prag razmaka (1 pt), prepoznavanje zaglavlja i tablica treba provjeriti na drugim brojevima Službenih novina i na PPUG-u.
- **Tablica u čl. 53 (normativi parkiranja)** nije rekonstruirana; vrijednosti se moraju ručno prepisati i provjeriti.
- **Podstavci, alineje i iznimke** (osnovna vrijednost ili iznimka, vrsta građevine, uvjet) nisu razdvojeni. To je sljedeća faza.
- **`brojevi()` je heuristika.** Nabrajanja s malim slovom (»2. križ«), popisi k.č. bez kose crte i oznake poput »P₁ - 15« mogu proći kao vrijednosti. Za dokaz treba broj uz jedinicu i kontekst.
- **Greške u izvornom tekstu ostaju kako jesu:** »broj32/08«, »trgovačko- uslužne« i slično (8 crtica s razmakom unutar retka).
- **HTML iste odluke nema članke 54–107**; izvor je PDF.
- Pravna aktualnost UPU-a 2 i dalje nije potvrđena (`pravna_provjera: NIJE_POTVRDENO`).

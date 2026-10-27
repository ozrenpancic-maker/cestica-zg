# Plan Integrity v1–v10: integracija u Čestica HR

Grana `plan-integrity-v1-v10`, napravljena iz `v02423-upu2-pravna` (to je `razvoj` + v0.24.23).
- `main` i produkcija nisu dirani.
- Produkcijska pravila nisu mijenjana: `src/rules*.json`, `rules_meta.json` i `tools/baza/primjer_baza.json` su isti.
- Ispis izvučenih parametara (`tests/audit.js`) identičan je onome prije promjene.

## 1. Što je već postojalo (pregled prije ugradnje)

| Funkcionalnost iz paketa | Stanje u aktualnoj grani prije ugradnje |
|---|---|
| `dbRuleLegal`, `dbMatch`, `dbCalc`, `dbHtml` | postoje, isti kao osnova paketa (patchevi su se primijenili s pomakom od 32 retka) |
| `dbResolve`, `dbSourceIntegrity`, dokazni lanac i izvještaj za bazu | nisu postojali |
| Baza pravila `RULES_DB` | **u produkciji je prazna** (`src/baza/baza.json` ne postoji). Odjeljak „Uvjeti iz baze” se ne prikazuje, pa v1–v10 u bazi vrijede tek kad se baza uveze. |
| Stvarni prikaz uvjeta gradnje | Krk `krkRulesHtml` (`rules_krk.json`), Zagreb (`rules.json`, urbana pravila). Pouzdanost A/B/C u registru `PZREG`; izračun nikad bolji od B, a s ulazom C i on je C. |
| Nepoznata detaljna zona (UPU) | već je bila blokirana: bez odabira nema izračuna |
| Zona »B«, neizgrađeno bez UPU-a, zabranjen način gradnje | već su bili blokirani |
| Iznimka 400 m² (»samo iznimno«), zahvat ≠ nova gradnja (Zagreb), iznimke za ulice | već su bili prikazani kao uvjet |
| Dokazni lanac po pokazatelju, status usklađenosti izvora, status rezultata (izvedeno / uvjetno / blokirano), JSON izvještaj | **nisu postojali** |

## 2. Što je ugrađeno

### Baza pravila (v1–v10 iz paketa)
- **Patchevi:** primijenjeni redom v1 → v2 → v3 → jedan objedinjeni v4–v10 (ne i pojedinačni). Svaki je prije primjene prošao `git apply --check`. Odjeljak baze nakon toga je bajt-za-bajt isti kao u referentnoj datoteci v10. Cijeli HTML nije zamijenjen.
- **Tri ispravka nad paketom:**
  - **Poznata, a različita izgrađenost ili zahvat:** pravilo se ne odnosi na lokaciju, kao prije v2. Samo **nepoznata** vrijednost ostavlja pravilo vidljivim i izbacuje ga iz izračuna. U v2 je i poznata razlika postala »vidljivo, ne računa se«.
  - **Pravilo »za sve vrste« (`sve`, `*`):** nepoznata vrsta građevine ga ne blokira. Pravilo za određenu vrstu i dalje traži poznatu vrstu (v1).
  - **Izvještaj baze:** uz pokazatelje navodi i pravila koja se ne računaju i razlog (`excluded`, `dbWhyNot`). U paketu je blokirani pokazatelj iz izvještaja nestajao.
- **Kontekst:**
  - Zagreb sada predaje bazi zahvat koji je korisnik odabrao.
  - Krk zahvat nema, pa pravila s obveznim zahvatom ostaju izvan izračuna (fail-closed).

### Aktivni prikaz (Krk, Zagreb): v4–v10 nad postojećim `PZREG`
- **Dokazni lanac** svakog građevinskog pokazatelja: najmanja čestica, tlocrt, GBP, prostor nakon odmaka. Karike su:
  1. čestica;
  2. plan (revizija, status, usklađenost);
  3. GIS zona iz vektora;
  4. detaljna zona;
  5. kartografski prikaz (list i aktualnost);
  6. zona zaštite;
  7. članak s citatom.

  Uz to idu uvjeti i iznimke.
- **Status rezultata**, odvojen od A/B/C. A/B/C se nije mijenjao.

  | Status | Kada |
  |---|---|
  | provjereno | samo uz stručnu potvrdu svih karika; takvih izvora u aplikaciji zasad nema, pa se ne dodjeljuje |
  | izvedeno | broj tehnički izveden iz evidentiranih izvora, bez nepotvrđenog ulaza |
  | uvjetno | neki ulaz je C, usklađenost izvora je nepoznata ili je uvjet otvoren |
  | blokirano | sukob, nedostaje podatak ili zona isključuje gradnju |

- **Usklađenost izvora:** `sukob`, `nepoznata` ili `kompatibilno`. Različite godine izvora same po sebi su `nepoznata`, a ne `sukob`.
- **Blokirani pokazatelji** imaju vlastite stavke (`blok-uvjeti`, `blok-krov`) s razlogom. Karte, GIS podaci, kalkulatori i 3D simulator ostaju.
- **Sukob unutar istog plana:** nagib krova po čl. 38. d) je 17°–23°, a u zoni »C« po čl. 85. oko 30°. Zapisan je kao blokiran pokazatelj s obrazloženjem. Simulator i dalje primjenjuje posebni režim, ali je označeno da njegova prednost nije stručno potvrđena.
- **Prikaz:** sklopivi odjeljak »Dokazni lanac« uz izračun. Koristi postojeće komponente (`acc`, `pzTag`, `kind st-*`).
- **JSON izvještaj (v10):** `piReport()` i gumb »Izvještaj o integritetu (JSON)« u odjeljku »Pouzdanost podataka«. Shema je `cesticahr.plan_integrity.v10`.
  - **Sadrži:** pokazatelje, pravila s citatima, izvore s revizijom i statusom, usklađenost, status rezultata, razlog blokade, otvorene uvjete i izvještaj baze (ako je uvezena).
  - **Ne sadrži:** podatke o vlasnicima, ZK terete, bilješke, financije ni adresu.
  - Primjer: `primjer_integritet_735_76.json`.

## 3. Testovi (stvarni rezultati, 27. 10. 2026.)

| Skup | Rezultat |
|---|---|
| Paket: `tests/plan_integrity/*.cjs` (v1 9, v2 16, v3 9, v10 15) | 49/49 |
| Puni skup `tests/run.js` (jsdom), prije promjene | 959/959 |
| Puni skup `tests/run.js`, poslije promjene (+1 test baze, +20 testova Plan Integrity) | 980/980 |
| `tests/mobile/krk.py`, `layout.py`, `pwa.py` (Chromium) | prolaze (PWA 42/42) |
| `tests/mobile/interaction.py` | pada i **prije** promjene, na istom mjestu (klik na sloj, redak 53); nije regresija |
| `tests/audit.js` (izvučeni parametri pravila) | identičan ispis prije i poslije |

Promijenjena su dva postojeća testa baze. Oba su promjene ponašanja koje traži v1–v2:
1. U kontekst je dodan zahvat »nova gradnja«, a novi test provjerava da bez zahvata pravilo ostaje vidljivo, ali se ne računa.
2. Naslov izračuna iz baze sada je »Izračun prema evidentiranim pravilima – UVJETNO« i ima dokazni lanac. Revizija u primjeru nije dokumentirana, pa je izračun uvjetan.

## 4. Kontrolni slučajevi (stvarni podaci)

**Kornić 735/76** (DGU i spremljeni odgovori PGŽ-a od 22. 10.)
- **Podaci:** 405 m², NA2 99,78 % i P3 0,22 %, UPU 2 Kornić.
- **Bez zone:** pokazatelji su blokirani, razlog je »detaljna zona nije potvrđena«.
- **Uz odabranu M11:**
  - najmanja čestica, tlocrt i GBP su **uvjetni**;
  - M11 i zona »C« su C (tvoj odabir);
  - usklađenost UPU-a 2 je nepoznata;
  - iznimka 400 m² je otvoren uvjet.
- **Zona »C«:** sukob oko krova je blokiran.
- **Zona »B«:** izračun je blokiran.
- **Nijedan pokazatelj** nije izveden ni provjeren.

**Kornić 735/54** (lokalni DGU katastar, PGŽ 27. 10., `tests/pgz-odgovori/735-54-kornic-2026-10-27/`)
- **Površina:** grafička 773,54 m², iz koordinata 772 m².
- **Namjena: PGŽ danas vraća samo NA2 (100 %), bez P3.** Raniji prikaz od 92 % NA2 i 8 % P3 s današnjim službenim podacima se **ne ponavlja**. Test zato ne prisiljava 92/8. Uzrok razlike nije utvrđen: možda druga granica čestice, možda drugo stanje sloja.
- **Ne miješa se s 735/76:** izračun koristi 772 m², a ne 405 m².

**Zagreb, kontrolni slučaj iz zadatka** (čestica 1541/2 k.o. Remete, urbano pravilo 2.2.; podaci Grada Zagreba od 27. 10., `tests/pgz-odgovori/zg-1541-2-remete-2026-10-27/`)
- **Namjena:** 90 % stambena, 10 % zaštitne zelene površine.
- **Karta urbanih pravila** iz javne rasprave 2024. nema potvrđenu usklađenost s tekstom GUP-a iz 2025., pa su tlocrt i GBP **uvjetni**, a ne sigurni.
- **Postojeći izračun** i usporedba tipova ostaju.
- **ISPU list** (raniji prikaz s oko 53 % pokrivenosti) u testu nije dohvaćen (nema mreže). Kad je u aplikaciji učitan, ulazi u lanac kao »kartografski list (ISPU)« s aktualnošću iz postojeće provjere.

## 5. Gdje izračun sada postaje blokiran ili uvjetan

- **Aktivni prikaz:**
  - Nijedan dosadašnji izračun nije uklonjen. Svi brojevi i oznake A/B/C ostaju.
  - Novo je to što su Krk i Zagreb sada označeni kao **uvjetni**. Razlog je nepoznata usklađenost:
    - pravna aktualnost PPUG-a Krk, UPU-a 2 i neslužbenog pročišćenog teksta GUP-a nije potvrđena;
    - karta iz 2024. nije potvrđena prema tekstu iz 2025.
  - Novi blokirani pokazatelj je nagib krova u zoni »C«.
- **Baza (kad se uveze):**
  - pravila s obveznim zahvatom ne ulaze u izračun na Krku (nema izbora zahvata);
  - pravila za određenu vrstu ne ulaze u izračun u Zagrebu (Zagreb ne predaje vrstu građevine);
  - pravila sa slobodnim `uvjet` ili `iznimke` bez `status_uvjeta` / `status_iznimke: "razriješeno"` ne ulaze u izračun;
  - pravila bez oznake revizije računaju se, ali su **uvjetna**.

## 6. Otvorena pitanja za odluku

1. Smije li se Krku dodati izbor zahvata, kao u Zagrebu, da pravila baze s obveznim zahvatom mogu ući u izračun?
2. Ima li posebni režim zone »C« (čl. 85.) prednost pred čl. 38. d) za krov? To je pravno tumačenje, ne odluka aplikacije.
3. Treba li Zagrebu vrsta građevine (obiteljska / višestambena) za pravila baze? Danas postoji samo način gradnje.
4. Uvoz baze traži inventuru: koliko pravila ima slobodni `uvjet` ili `iznimke` bez strukturiranog statusa razrješenja. Ta će pravila po v6 ostati izvan izračuna.
5. 735/54: odakle je raniji podatak 92/8 (koja granica i koje stanje sloja)?

Ništa nije spojeno u `main`.

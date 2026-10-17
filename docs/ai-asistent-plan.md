# AI asistent ČesticaZG: tehnički plan (etapa AI-1)

Stanje: listopad 2026., grana `razvoj`. Etapa AI-1 dodaje samo programsko sučelje i testove sa simuliranim modelom.
Plaćeni API nije aktiviran. **Dopuna (AI-2):** sučelje samo za čitanje, Worker s prijavom i atomskim budžetom te upute za postavljanje opisani su u `docs/ai-postavljanje.md`; ovaj dokument ostaje kao izvorni plan.

## 1. Postojeće funkcije koje AI može koristiti

| Područje | Postojeća funkcija ili stanje | Kako ga AI dobiva |
|---|---|---|
| Odabrana čestica | `window.__cur` (ključ k.o.\|broj, površina, gradivi dio, namjena, pravilo) | `getCurrentParcel` |
| Katastar i GIS | `window.__lastData` (čestica, namjena, slojevi ograničenja, okolina, nagib, zgrade) | sažeto u kontekstu, bez geometrija |
| Urbana pravila | `ruleLookup`, `pickZone`, `ruleParams` (status propisano/provjera/nije), `window.__gbp`, `window.__tl`, `RULES_META` | `getUrbanRules` |
| Rizici | `riskFindings(d)` (potvrđeno, potencijalno, neprovjereno, s izvorom i datumom) | `getParcelConstraints` |
| Infrastruktura | `loadInfra` → `window.__infra` (samo glavni vodovi iz GUP-a) | `getInfrastructure` |
| Simulator | `TL`, `tChecks()`, `tZones()`, `withinEnv()`, `tDraw()` | `validateHousePlacement`, `previewHouseChanges` |
| Financije | `finInputs()`, `finHouse(I,rate)`, `finCompute()`, `prepItems()`, `buyGet/buySet` | `calculateInvestment`, `previewInvestmentChanges` |
| Scenariji | `scList`, `scRow`, `scSave`, `scLoad`, `scAllowed` | `listScenarios`, spremanje nakon potvrde |
| Spremljene čestice | `favs()` (površina, pravilo, ograničenja, nagib, proračun) | `compareParcels` |
| PDF | `window.print()` s pripremom karte | `generateParcelReport`, zasad vraća "nije dostupno" (faza G) |

## 2. Što još nema prikladno sučelje

- **Optimalni položaj kuće** (Modul 5) još ne postoji. Alat `toward` samo pomiče kuću prema jednoj strani u koracima od 0,5 m, dok god je unutar dopuštenog prostora. To nije optimizacija i AI to mora tako i reći.
- **PDF izvještaj** se zasad radi samo ispisom stranice. Izvještaj iz podataka dolazi u fazi G.
- **Usporedba čestica** koristi podatke koji su spremljeni uz česticu. Za svježe podatke treba ponovno učitati svaku česticu (faza E).
- **Prikaz sloja na karti i prelazak na česticu** imaju gumbe, ali nemaju funkcije koje se mogu pozvati izvana. Dodaju se u etapi AI-3 (`showLayer`, `goToParcel`).
- **Zaključak "Isplati li se kupiti"** (Modul 11) ne postoji, pa AI ne smije davati takvu ocjenu bez definiranog modela bodovanja.

## 3. Povezivanje (arhitektura)

```
Aplikacija (GitHub Pages)                         Cloudflare Worker (besplatno)          Anthropic API
┌───────────────────────────────┐   HTTPS POST   ┌───────────────────────────┐        ┌─────────────┐
│ AI panel (AI-2)               │ ─────────────▶ │ provjera izvora i tokena  │ ─────▶ │ Claude      │
│ aiConverse(): petlja razgovora│ ◀───────────── │ limit poziva i budžeta    │ ◀───── │ Haiku 5.5   │
│ aiCall(): JEDINA točka za alat│  tekst + popis │ sistemske upute (fiksne)  │        └─────────────┘
│ aiValidate(): sheme, rasponi  │  traženih alata│ API ključ (tajna)         │
│ AI.pending: privremeno stanje │                │ ne izvršava alate         │
│ aiApprove(): samo klik korisn.│                └───────────────────────────┘
│ AI.undo: poništavanje         │
│ postojeće funkcije (finHouse, │
│ tChecks, ruleParams, riskF.)  │
└───────────────────────────────┘
```

Tijek jednog pitanja:
1. Korisnik upiše pitanje. Aplikacija pošalje razgovor i opise alata Workeru.
2. Model odgovori tekstom ili traži alat (npr. `getUrbanRules`).
3. Aplikacija u `aiCall` provjeri naziv i argumente, pozove postojeću funkciju i rezultat vrati modelu.
4. Najviše 6 koraka po pitanju. Ako se čestica u međuvremenu promijeni, odgovor se prekida.

Model nikad ne dobiva pristup JavaScriptu, DOM-u ni lokalnoj pohrani. Vidi samo rezultate alata.

## 4. Model i backend

**Prijedlog za početno testiranje: Claude Haiku 5.5** (`claude-haiku-5-5`), uz mogućnost da se za teža pitanja ručno izabere **Claude Sonnet 5.5**.
- Haiku 5.5: 0,10 $ ulaz / 0,50 $ izlaz po milijun tokena (za upite do 100.000 tokena).
- Sonnet 5.5: 2 $ ulaz / 10 $ izlaz po milijun tokena.
- Izvor: platform.claude.com/docs/en/about-claude/pricing (provjereno 17. 10. 2026.).
- OpenAI je također moguć (npr. GPT-5.6 Luna 0,20 $ / 1,20 $). Worker bi se samo malo promijenio, ali za jedan backend predlažem jednog dobavljača.

**Backend: Cloudflare Worker** (`worker/src/index.js`; u AI-2 zamijenio je prvi kostur):
- Besplatna razina: 100.000 zahtjeva dnevno, a KV pohrana za brojanje potrošnje 1.000 upisa dnevno. Za jednog korisnika to je daleko iznad potrebe.
- Ključ je spremljen kao tajna Workera. Nije u HTML-u, JavaScriptu, Gitu ni pregledniku.
- **Pristup Workeru (izvorni prijedlog, u AI-2 zamijenjen prijavom lozinkom i tokenom od 12 sati u sessionStorage):** osobni pristupni token (dugi nasumični niz) koji vlasnik jednom upiše na svom uređaju. Worker čuva samo njegov SHA-256 sažetak. Token nije API ključ, može se opozvati u minuti, a šteta od krađe ograničena je budžetom i limitom poziva.
  - Alternativa je Cloudflare Access (prijava e-poštom). Njegovi kolačići u Safariju na iPhoneu često ne rade kad se poziva s druge domene (github.io), pa ga ne predlažem za početak.
- Dodatno: provjera domene (samo `ozrenpancic-maker.github.io`), najviše 12 upita u minuti, najviše 1.200 izlaznih tokena po odgovoru, popis dopuštenih alata na Workeru i fiksne sistemske upute koje aplikacija ne može promijeniti.

## 5. Procijenjeni troškovi

Pretpostavka za jedno pitanje: 2 do 3 poziva modela, ukupno oko 20.000 ulaznih i 600 izlaznih tokena.
Najveći dio ulaza su opisi alata i kontekst čestice; ponavljani dio se dijelom kešira i tada je jeftiniji.

| | Haiku 5.5 | Sonnet 5.5 |
|---|---|---|
| Po pitanju | oko 0,0023 $ | oko 0,046 $ |
| 300 pitanja mjesečno | oko 0,70 $ | oko 14 $ |
| 1.000 pitanja mjesečno | oko 2,30 $ | oko 46 $ |

- **Jednokratno:** 0 $ za Cloudflare. Za Anthropic API treba otvoriti račun na Claude Console i uplatiti kredit; najmanji iznos piše pri uplati, a za testiranje je dovoljno 5 do 10 $. Pretplata na Claude (Pro/Max) **ne uključuje** potrošnju API-ja.
- **Mjesečno:** uz Haiku i normalno korištenje ispod 1 $. Predlažem granicu od 5 $ mjesečno u Workeru, a u Claude Console posebni workspace s vlastitim ograničenjem potrošnje kao drugu zaštitu.
- Aplikacija vodi i vlastitu evidenciju (`aiUse`: broj upita, tokeni, procijenjeni trošak) i ne poziva model kad je budžet potrošen.

## 6. Potvrđivanje i poništavanje

| Način | Alati | Što smije |
|---|---|---|
| Pitaj | `getCurrentParcel`, `getUrbanRules`, `getParcelConstraints`, `getInfrastructure`, `listScenarios`, `calculateInvestment`, `validateHousePlacement`, `compareParcels` | samo čitanje; izračuni u pješčaniku, stanje se vraća |
| Predloži | `previewHouseChanges`, `previewInvestmentChanges` | prijedlog u `AI.pending` (vezan uz česticu, istječe za 1 sat); prikazuje prije/poslije i provjere |
| Izvrši | `commitApprovedChanges`, `undoLastApprovedChange`, `generateParcelReport` | samo ako je korisnik kliknuo "Primijeni" (`aiApprove`, nije alat modela) |

Zaštite koje već rade i pokrivene su testovima:
- nepoznata naredba se odbija;
- nepoznat parametar se odbija (npr. pokušaj promjene poreza);
- odbija se vrijednost izvan raspona ili krivog tipa;
- odbija se alat za česticu koja nije odabrana;
- bez potvrde nema primjene, a ista radnja se ne izvršava dvaput;
- prijedlog za prethodnu česticu ne može se primijeniti na novu;
- najviše 40 poziva alata u minuti;
- prekida se petlja duža od 6 koraka.

Poništavanje: prije svake primjene sprema se snimka onoga što se mijenja. Za kalkulator to su ulazi, kupnja, priprema terena i scenariji čestice; za simulator dimenzije i položaj kuće. Pamti se najviše 20 koraka.

Brisanje i prepisivanje scenarija **nisu dostupni AI-ju**. Ako se kasnije dodaju, tražit će zasebnu potvrdu.

Tekst GUP-a, GIS atributi i dokumenti ulaze u rezultate alata kao podaci, ograničene duljine. Test potvrđuje da naredba upisana u GIS atribut ne može ništa odobriti ni primijeniti.

## 7. Datoteke

| Datoteka | Promjena |
|---|---|
| `src/app.template.html` | odjeljak "AI ASISTENT: KONTROLIRANO SUČELJE": `aiContext`, `aiValidate`, `AI_TOOLS`, `aiCall`, `aiToolSpecs`, `aiConverse`, privremeno stanje, potvrda, poništavanje, praćenje troškova; `window.__rule`; `FEATURES.ai` |
| `worker/src/index.js`, `worker/wrangler.toml` | Cloudflare Worker s Durable Objectom (AI-2; nije objavljen) |
| `tests/run.js` | odjeljak 15: 47 testova sa simuliranim modelom, bez troška |
| `docs/ai-asistent-plan.md` | ovaj plan |
| AI-2 (kasnije) | AI panel u aplikaciji, `wrangler.toml`, upute za postavljanje Workera u README-u |

## 8. Izgled sučelja (AI-2 do AI-5)

**Računalo:** bočni panel desno od karte, širok oko 360 px, može se sklopiti u traku od 44 px. Sadrži:
- na vrhu: aktivna čestica ("3101/2, k.o. Remete") i oznaka modela;
- razgovor s kratkim odgovorima i oznakama potvrđeno / izračun / procjena / nepoznato, s izvorima koji se mogu otvoriti;
- karticu prijedloga s tablicom prije/poslije, provjerama simulatora i gumbima "Primijeni" i "Odbaci";
- nakon primjene gumb "Poništi";
- na dnu potrošnju u ovom mjesecu.

**Mobitel:** nova peta stavka "AI" u donjoj navigaciji, ili plutajući gumb iznad nje. Panel se otvara do pola visine, pa karta s kućom ostaje vidljiva iznad. Može se povući na cijeli ekran. Brza pitanja su kao gumbi: Što mogu graditi? · Koliko košta? · Koji su rizici? · Predloži kuću · Usporedi parcele · Izradi izvještaj. Odgovor je najviše 3 do 4 retka, a "Detalji" otvaraju ostatak. Glasovne naredbe dolaze tek nakon pouzdanog tekstualnog upravljanja.

## 9. Sljedeći koraci (svaki uz odobrenje)

1. **AI-2:** vlasnik otvori Anthropic API račun i Cloudflare račun; postavi se Worker; dodaje se panel s pitanjima (samo način "Pitaj").
2. **AI-3:** prijedlozi na karti i u kalkulatoru, prikaz prije/poslije.
3. **AI-4:** primjena, poništavanje, izvještaji.
4. **AI-5:** dovršen mobilni panel, brza pitanja, priprema za glas.

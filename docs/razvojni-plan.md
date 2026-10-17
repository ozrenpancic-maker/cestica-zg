# ČesticaZG: pregled stanja i plan razvoja

Stanje: 17. 10. 2026., grana `razvoj`. Produkcija (`main`) odgovara objavi od 17. 10. u 17:12.

## 1. Što je gotovo

| Područje | Stanje | Gdje u kodu |
|---|---|---|
| Katastar, namjena, slojevi ograničenja, okolina, nagib, postojeće zgrade | gotovo | `inspect`, `loadView`, `CHECKS`, `loadEnv`, `loadSlope`, `loadZgrade` |
| Urbana pravila GUP Zagreb, GUP Sesvete (prijedlog), PPGZ, statusi parametara | gotovo | `ruleLookup`, `ruleParams`, `rules*.json`, `rules_meta.json` |
| Simulator kuće (pomicanje, okret, garaža, odmaci, provjere) | gotovo | `TL`, `tChecks`, `tDraw` |
| Sunce, sjene, procjena solarne elektrane (potres skriven) | gotovo | `sun*`, `pv*` |
| Komunalna infrastruktura (samo glavni vodovi iz GUP-a) | gotovo, ograničeni podaci | `loadInfra` |
| Jedinstveni financijski model: gradnja, naknade, priključci, kupnja, ukupno, rezerva | gotovo | `finInputs`, `finHouse`, `finCompute` |
| Modul 1 Rizici, Modul 2 Scenariji, Modul 3 Priprema terena | gotovo | `riskFindings`, `sc*`, `prep*` |
| Mobilno sučelje (panel u tri stanja, donja navigacija) | gotovo | odjeljak "MOBILNO SUČELJE" |
| AI-1: kontrolirano sučelje za AI | gotovo | `aiCall`, `AI_TOOLS` |
| AI-2: AI panel samo za čitanje, Worker s prijavom i budžetom | kod gotov, API nije aktiviran | `aiAsk`, `worker/` |
| **Faza 1 ovog plana: jedinstveni projektni model** | **gotovo (ovaj korak)** | `proj*` |

Otvoreno iz ranijih planova: Moduli 4–11 (povijest, optimalni položaj, terenski pregled, buka, klimatski rizici, parcelacija, vrijednost zemljišta, zaključak), faza E (usporedba čestica i izvoz u CSV/Excel), faza G (PDF izvještaj) i AI-2 do AI-5.

## 2. Zajedničke podatkovne strukture

Sve je u pregledniku (`localStorage`), a ključ projekta je `k.o.|broj čestice`:

| Spremište | Sadržaj |
|---|---|
| `proj` (novo) | kuća iz kalkulatora, simulator, zona komunalnog doprinosa, vrijeme izmjene |
| `buy`, `land` | kupnja zemljišta (`land` je stari zapis cijene koji se još koristi u spremljenim česticama) |
| `prep`, `infc` | priprema terena; radovi na priključcima |
| `scen` | investicijski scenariji |
| `ck2` | kontrolna lista koraka |
| `favs` | spremljene čestice sa sažetkom (površina, pravilo, proračun) |

`projGet(k)` sastavlja sve u jedan objekt projekta. To je osnova za izvještaje, AI, kredit, vremenski plan, upite i ponude.

## 3. Nađene nedosljednosti

| # | Nedosljednost | Stanje |
|---|---|---|
| 1 | Kuća iz kalkulatora (površina, katnost, vrsta, standard) nije se spremala; nakon ponovnog otvaranja čestice vraćale su se zadane vrijednosti | **popravljeno**: sprema se uz česticu |
| 2 | Zona komunalnog doprinosa bila je jedna za sve čestice, iako ovisi o lokaciji | **popravljeno**: sprema se uz česticu. Stara zajednička zona se ne prenosi, pa je na već spremljenim česticama treba jednom ponovno izabrati |
| 3 | Simulator nije pamtio kuću; dimenzije su prelazile s čestice na česticu | **popravljeno**: dimenzije i položaj spremaju se uz česticu |
| 4 | Simulator i kalkulator povezani su samo gumbom "Prenesi kuću u procjenu troškova" | ostaje namjerno: korisnik bira kad se tlocrt prenosi; AI-3 može predložiti prijenos |
| 5 | Cijena zemljišta zapisuje se u `buy` i u stari `land` | ostaje radi spremljenih čestica; `buy` je glavni izvor |
| 6 | Proračun u spremljenim česticama je snimka u trenutku zadnjeg izračuna | ostaje; usporedba čestica (faza E) treba ponovni izračun |
| 7 | "Gradnja" je jedna stavka s rasponom ±10 %, a master plan traži raščlambu (temelji, konstrukcija, krov, instalacije, završni radovi) | **otvoreno**: treba izvor udjela po fazama gradnje; bez izvora se ne uvodi |
| 8 | Nema statusa troška (procjena / unos / ponuda / ugovoreno / stvarno) | otvoreno: uvodi se s ponudama (faza 8) i praćenjem troškova |

## 4. Arhitektura novih funkcija

Svaki novi modul čita i piše **samo kroz projekt čestice** i koristi postojeći financijski model:

```
            ┌───────── projekt čestice (projGet) ─────────┐
            │ kuća · simulator · zona · kupnja · priprema │
            │ scenariji · kredit · vremenski plan · upiti │
            │ ponude · odabrani izvođači · stvarni troškovi│
            └──────────────┬──────────────────────────────┘
  finHouse / finCompute ───┼── jedini izvor iznosa (svaka stavka jednom)
  plan gradnje (CPM) ──────┼── trajanja i datumi → raspored plaćanja
  kredit ──────────────────┼── tranše prema rasporedu plaćanja → kamate tijekom gradnje
  upiti / troškovnik ──────┼── generiraju se iz projekta, nepoznato ostaje označeno
  ponude ──────────────────┘── nakon potvrde predlažu izmjene iznosa i rokova
```

## 5. Redoslijed (prijedlog)

| # | Faza | Plaćeni servis? | Napomena |
|---|---|---|---|
| 1 | Jedinstveni projektni model | ne | **gotovo** |
| 2 | Najveća cijena zemljišta za zadani budžet | ne | obrnuti izračun postojećeg modela |
| 3 | Kredit i financiranje | ne | anuiteti, otplatni plan, tranše, poček; pravila HNB-a provjeriti pri izradi; EKS samo uz dovoljno podataka |
| 4 | Trajanje gradnje (CPM) | ne | normativi rada moraju imati izvor; bez izvora ostaju korisnikov unos s oznakom |
| 5 | Gantt i financijski tijek | ne | povezuje fazu 4 s fazama 1 i 3 |
| 6 | Upiti izvođačima i paket upita (Word, PDF) | ne | generiranje u pregledniku |
| 7 | Informativni troškovnik i izvoz u Excel | ne | precizne količine samo iz projekta ili korisnikova unosa |
| 8 | Učitavanje i usporedba ponuda | ne za ručni unos; izdvajanje iz PDF-a bez AI-ja je djelomično | AI izdvajanje kasnije (uz odobren API) |
| 9 | Automatski raspored cijele parcele (uključuje Modul 5, optimalni položaj) | ne | deterministički algoritam; ne tvrdi globalni optimum |
| 10 | Pretraživanje parcela prema kući | ne, ali težak dohvat | gradski ArcGIS servisi ograničavaju broj zapisa po upitu; bez baze prodaje "na prodaju" se ne tvrdi |
| 11 | 3D prikaz | ne | približni model; precizan samo uz geodetsku podlogu |
| 12 | AI asistent AI-2 do AI-5 | **da** (Anthropic API, oko 1 $ mjesečno uz Haiku 5.5) | čeka odobrenje |
| 13 | Izvještaji A–F, završna mobilna optimizacija | ne | uključuje fazu G |

Moduli 4, 6, 7, 8, 9, 10 i 11 iz ranijeg plana (povijest, terenski pregled, buka, klimatski rizici, parcelacija, vrijednost zemljišta, zaključak) uklapaju se između faza 9 i 13, prema prioritetu koji odrediš.

**Navigacija na mobitelu:** master plan predlaže Karta · Analiza · Projekt · Financije · Dokumenti. Promjena je predviđena kad nastanu moduli Projekt (faze 4–9) i Dokumenti (6–8, 13), da se postojeće kartice ne mijenjaju prerano.

## 6. Rizici razvoja i održavanja

- **Podaci samo u pregledniku:** brisanje podataka preglednika briše projekte. Ublaženo izvozom i uvozom projekta. Trajno rješenje (sinkronizacija) traži backend i odobrenje.
- **Jedna velika HTML datoteka** (oko 2.800 redaka predloška): raste teže za održavanje. Prijedlog je da se novi veliki moduli (kredit, plan gradnje, upiti) pišu kao zasebne `src/*.js` datoteke koje `build.py` umeće u stranicu.
- **Vanjski servisi Grada Zagreba** mogu promijeniti adrese ili slojeve. Ublaženo statusom servisa, ponovnim pokušajima i oznakom "neprovjereno".
- **Normativi i cijene zastarijevaju:** svaka konstanta ima izvor i datum u kodu i u prikazu, a mijenja se na jednom mjestu.
- **Pravni okvir** (porezi, naknade, HNB): provjerava se pri izradi svake faze i u kodu se navodi izvor.
- **Veličina lokalne pohrane** (oko 5 MB): projekt je malen, ali ponude (PDF) se ne smiju spremati u `localStorage`. Za njih treba IndexedDB s ograničenjem veličine.

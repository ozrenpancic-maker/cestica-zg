# AI asistent: postavljanje, limiti, trošak i gašenje

Ovaj postupak radiš sam, na svom računalu. Ključevi i lozinke nikad ne idu u repozitorij, chat ni aplikaciju.
Dok ne napraviš korake 1–5, AI asistent ne može ništa poslati: u aplikaciji traži adresu servisa i prijavu.

Potrebno: računalo s instaliranim Node.js 20 ili novijim (nodejs.org) i ovaj repozitorij (grana `razvoj`).

## 1. Anthropic API račun (Claude Console)

Pretplata na Claude (Pro/Max) **ne uključuje** API. API ima zaseban račun i zasebnu naplatu.

1. Otvori **platform.claude.com** i prijavi se ili otvori račun (organizacija može biti tvoje ime).
2. **Settings → Billing → Buy credits**: uplati **5 $** (dovoljno za testiranje). Kredit je odmah dostupan, vrijedi godinu dana i nije povratan.
3. **Ne uključuj "auto-reload"**. Tako uplaćeni kredit sam po sebi ograničava potrošnju: kad se potroši, API staje.
4. **Settings → Billing → Spend limits → Set limit**: upiši **5 $** mjesečno. To je druga, neovisna granica (uz granicu u Workeru).
5. **Settings → Workspaces → Create workspace**, npr. `cesticazg`. Zasebni workspace odvaja ovaj ključ od svega drugog.
6. **Settings → API keys → Create key**, u workspaceu `cesticazg`, naziv npr. `cesticazg-worker`. Ključ se prikazuje **samo jednom**: kopiraj ga izravno u korak 4 i nigdje ga ne spremaj.

## 2. Cloudflare račun

1. Otvori **dash.cloudflare.com** i registriraj se (besplatni plan; kartica nije potrebna).
2. U **Workers & Pages** prihvati besplatnu poddomenu `….workers.dev` (npr. `ozren.workers.dev`).

Besplatni plan dopušta 100.000 zahtjeva dnevno i Durable Objecte sa SQLite pohranom, što je dovoljno.

## 3. Lozinka za prijavu u AI asistenta

U terminalu, u mapi `worker` repozitorija:

```
cd worker
node tools/nova-lozinka.mjs
```

Skripta ispiše:
- **lozinku za prijavu** (32 nasumična znaka), koju spremi u upravitelj lozinki (npr. Bitwarden, 1Password, iCloud Keychain);
- tri vrijednosti za Worker: `LOGIN_PEPPER`, `LOGIN_HASH` i `SESSION_SECRET`.

Skripta ništa ne šalje na internet i ništa ne zapisuje u datoteke. Ispis ostavi otvoren do kraja koraka 4, zatim zatvori terminal.

## 4. Postavljanje Workera i sigurni unos tajni

```
cd worker
npm install
npx wrangler login                    # otvara preglednik za prijavu u Cloudflare
npx wrangler deploy                   # prvi put: objavljuje Worker, AI je još isključen (AI_ENABLED="false")
npx wrangler secret put ANTHROPIC_API_KEY   # zalijepi ključ iz koraka 1.6 kad ga zatraži
npx wrangler secret put LOGIN_PEPPER        # vrijednost iz koraka 3
npx wrangler secret put LOGIN_HASH          # vrijednost iz koraka 3
npx wrangler secret put SESSION_SECRET      # vrijednost iz koraka 3
```

`wrangler secret put` traži vrijednost u terminalu. Ne upisuj je u naredbu, `wrangler.toml` ni bilo koju datoteku. Tajne su šifrirane u Cloudflareu i ne vide se ni na nadzornoj ploči.

Zatim u `worker/wrangler.toml` promijeni `AI_ENABLED = "false"` u `"true"` i ponovno pokreni `npx wrangler deploy`.

Wrangler ispiše adresu Workera, npr. `https://cesticazg-ai.ozren.workers.dev`.

**Provjera s računala** (ne troši API):
```
curl -i -X POST https://cesticazg-ai.ozren.workers.dev/login -H "origin: https://ozrenpancic-maker.github.io" -H "content-type: application/json" -d "{\"lozinka\":\"krivo-krivo-krivo-krivo-krivo\"}"
```
Očekivani odgovor je `401` i "Pogrešna lozinka". Svaki krivi pokušaj se broji, a nakon 5 krivih pokušaja prijava je zaključana 15 minuta.

## 5. Uključivanje u aplikaciji (pregled s grane `razvoj`)

1. Otvori pregled aplikacije s grane `razvoj` (ne produkciju).
2. Izbornik **☰ → AI asistent (testno)** → uključi.
3. Upiši adresu Workera i spremi je.
4. Prijavi se lozinkom iz koraka 3. Prijava vrijedi do zatvaranja kartice, najdulje 12 sati.

Pregled grane `razvoj` otvara se lokalnim poslužiteljem na `http://localhost:8000` (vidi `docs/ai-upute-windows.md`, korak 21). Ta adresa je već među dopuštenima u `wrangler.toml`.

## 6. Procjena stvarnog troška testiranja

Cijene Claude Haiku 5.5 (`claude-haiku-5-5`): **0,10 $** po milijun ulaznih i **0,50 $** po milijun izlaznih tokena (platform.claude.com, provjereno 17. 10. 2026.).

| Što | Pretpostavka | Trošak |
|---|---|---|
| Jedno pitanje | 2–3 poziva modela, oko 20.000 ulaznih i 600 izlaznih tokena | oko 0,002–0,003 $ |
| Cijeli ocjenski skup (47 pitanja) | `tests/ai-eval/run-eval.js` | oko 0,10–0,20 $ |
| Tjedan ručnog testiranja | 100 pitanja | oko 0,25 $ |
| Mjesec normalnog korištenja | 300 pitanja | oko 0,70 $ |

Gornje granice:
- Worker: **5 $ mjesečno**. Trošak se rezervira prije poziva, a istodobni zahtjevi ne mogu zajedno prijeći granicu.
- Najviše **12 poziva modela u minuti** (podesivo varijablom `RATE_PER_MIN`, najviše 60), **300 dnevno** i **6 poziva po pitanju**. Odgovor je najviše 1.200 tokena.
- Ponovljeni zahtjev s istom oznakom ne poziva model ponovno. Kad veza pukne, ne zna se je li Anthropic obradio zahtjev, pa se računa najgori slučaj.
- Claude Console: limit potrošnje 5 $ i uplaćeni kredit bez automatske nadoplate.

Stvarna potrošnja vidi se u aplikaciji (dno AI panela), u Claude Consoleu (**Usage**) i u Cloudflare logu (`npx wrangler tail` prikazuje samo brojke: trošak, trajanje, šifru greške).

## 7. Isključivanje AI-ja i opoziv pristupa

| Hitnost | Radnja | Učinak |
|---|---|---|
| Samo na ovom uređaju | ☰ → isključi "AI asistent (testno)" | panel nestaje, ništa se ne šalje |
| Za sve odmah | `AI_ENABLED = "false"` u `wrangler.toml`, pa `npx wrangler deploy` | Worker odbija sve pozive |
| Odjava svih prijava | povećaj `SESSION_EPOCH` (npr. "2"), pa `npx wrangler deploy` | sve postojeće prijave prestaju vrijediti |
| Promjena lozinke | ponovno `node tools/nova-lozinka.mjs` i `wrangler secret put` za LOGIN_PEPPER, LOGIN_HASH i SESSION_SECRET | stara lozinka i stari tokeni više ne rade |
| Opoziv API ključa | Claude Console → API keys → **Disable/Delete** ključ `cesticazg-worker` | Anthropic odbija sve pozive tim ključem |
| Potpuno uklanjanje | `npx wrangler delete`, zatim brisanje ključa u Consoleu | Worker i ključ više ne postoje |

Ako posumnjaš da je ključ procurio: odmah ga obriši u Consoleu, napravi novi i upiši ga s `npx wrangler secret put ANTHROPIC_API_KEY`.

## 8. Što je testirano bez objave na produkciju

- **Worker** (`cd worker && npm test`, lokalno u Miniflareu 4, isti runtime kao Cloudflare, s lažnim Anthropic API-jem, bez troška): 42 testa. Pokrivaju SQLite pohranu, prijavu, zaključavanje, krivotvorene, istekle i opozvane tokene, gašenje, istodobne zahtjeve, ponovljene zahtjeve, prekide veze, istek vremena, nezatvorene rezervacije, samo čitanje i limit iz Consolea.
- **Cijeli lanac** (aplikacija → Worker → lažni Anthropic): svih 47 ocjenskih pitanja prošlo je kroz pravi Worker bez greške, a obračun potrošnje odgovara izračunu do decimale.
- **Aplikacija** (`cd tests && npm test`): AI-1 i AI-2 testovi sa simuliranim modelom (panel, prijava, samo čitanje, injekcije, promjena čestice, greške, gašenje).
- **Ocjenski skup** (`node tests/ai-eval/run-eval.js`): sa simuliranim modelom provjerava samo da ocjenjivanje radi. **Kvaliteta stvarnih odgovora još nije izmjerena**, jer za to treba aktivan API.
- Ništa nije objavljeno na `main` ni GitHub Pages produkciju.

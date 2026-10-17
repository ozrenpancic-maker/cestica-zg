# AI asistent: upute za Windows, od računa do prvog pitanja

Vrijeme: oko 45 minuta. Trošak: 5 $ uplate na Anthropic; Cloudflare je besplatan.
Produkcijska aplikacija se ne mijenja: testiraš pregled grane `razvoj` na svom računalu.

---

## A. Što sam ja već pripremio (ne radiš ništa)

- Kod AI asistenta u aplikaciji: samo čitanje, uključuje se u izborniku.
- Cloudflare Worker (`worker/`): prijava, potrošnja i limiti; testiran lokalno, 42 od 42.
- Skripta koja generira lozinku i tajne (`worker/tools/nova-lozinka.mjs`).
- Postavke Workera (`worker/wrangler.toml`): AI je isključen dok ga ne uključiš; granica je 5 $ mjesečno; dopuštene adrese su GitHub Pages i `http://localhost:8000`.
- 47 ocjenskih pitanja i skripta za njihovo pokretanje (`tests/ai-eval/`).

## B. Što trebaš napraviti ti

Svaki korak označi kad ga završiš. Tamo gdje piše **ZALIJEPI**, vrijednost kopiraš iz koraka koji je naveden.

### Priprema računala (jednom)

1. ☐ Otvori **nodejs.org**, preuzmi verziju **LTS** za Windows i instaliraj je (sve zadane postavke).
2. ☐ Otvori **github.com/ozrenpancic-maker/cestica-zg**. Gore lijevo u izborniku grana odaberi **razvoj**, zatim **Code → Download ZIP**.
3. ☐ U mapi Preuzimanja desni klik na ZIP → **Extract All** → npr. `C:\cestica-zg`. Unutra je mapa `cestica-zg-razvoj`.

**Kako otvoriti naredbeni redak u mapi:** u File Exploreru otvori mapu, klikni u adresnu traku, upiši `cmd` i pritisni Enter. Otvori se crni prozor već postavljen u tu mapu. Koristi **cmd**, ne PowerShell.

### Anthropic (Claude Console)

4. ☐ Otvori **platform.claude.com** i otvori račun ili se prijavi. Ovo je odvojeno od pretplate na Claude.
5. ☐ **Settings → Billing → Buy credits** → upiši **5** $ → plati karticom.
6. ☐ U istom izborniku **NE** uključuj **auto-reload**.
7. ☐ **Settings → Billing → Spend limits → Set limit** → **5** $.
8. ☐ **Settings → Workspaces → Create workspace** → naziv `cesticazg`.
9. ☐ **Settings → API keys → Create key** → workspace `cesticazg`, naziv `cesticazg-worker` → **Copy**.
   Ključ se prikazuje samo jednom. Ostavi tu karticu otvorenu do koraka 17 i nigdje ga ne spremaj.

### Cloudflare

10. ☐ Otvori **dash.cloudflare.com/sign-up** i registriraj se e-poštom (besplatno). Potvrdi e-poštu.

### Lozinka i tajne

11. ☐ Otvori mapu `C:\cestica-zg\cestica-zg-razvoj\worker` i u adresnu traku upiši `cmd` + Enter.
12. ☐ Upiši i pritisni Enter:
    ```
    npm install
    ```
    Pričekaj da završi (1–2 minute).
13. ☐ Upiši:
    ```
    node tools\nova-lozinka.mjs
    ```
    Ispiše se **lozinka** i tri tajne (LOGIN_PEPPER, LOGIN_HASH, SESSION_SECRET).
    **Lozinku odmah spremi u upravitelj lozinki.** Prozor ostavi otvoren.

### Postavljanje Workera

14. ☐ U istom prozoru:
    ```
    npx wrangler login
    ```
    Otvori se preglednik → **Allow**. Vrati se u crni prozor.
15. ☐ Objavi Worker. AI je pritom još isključen:
    ```
    npx wrangler deploy
    ```
    Ako pita za poddomenu `workers.dev`, upiši kratko ime, npr. `ozren`.
    Na kraju piše adresa, npr. `https://cesticazg-ai.ozren.workers.dev`. **Zapiši je.**
16. ☐ Tajne iz koraka 13. Za svaku naredbu: pritisni Enter, **ZALIJEPI** vrijednost iz koraka 13 desnim klikom, pa opet Enter.
    ```
    npx wrangler secret put LOGIN_PEPPER
    npx wrangler secret put LOGIN_HASH
    npx wrangler secret put SESSION_SECRET
    ```
17. ☐ API ključ: pritisni Enter, **ZALIJEPI** ključ iz koraka 9, pa opet Enter.
    ```
    npx wrangler secret put ANTHROPIC_API_KEY
    ```
    Zatim zatvori karticu s ključem u Consoleu.
18. ☐ Uključi AI: otvori `worker\wrangler.toml` u Notepadu. Promijeni `AI_ENABLED = "false"` u `AI_ENABLED = "true"` i spremi.
19. ☐ Ponovno objavi:
    ```
    npx wrangler deploy
    ```
20. ☐ Zatvori crni prozor. Time se briše i ispis lozinke i tajni s ekrana.

### Prvo probno pitanje

21. ☐ Otvori mapu `C:\cestica-zg\cestica-zg-razvoj` (glavnu, ne `worker`), upiši `cmd` + Enter, pa:
    ```
    npx http-server -p 8000 -c-1
    ```
    Ako pita "Ok to proceed?", upiši `y`. Prozor ostavi otvoren.
22. ☐ U pregledniku otvori **http://localhost:8000/index.html**.
23. ☐ Dodirni ili klikni zemljište u Zagrebu i pričekaj da se čestica učita.
24. ☐ **☰** (gore desno) → označi **AI asistent (testno)**.
25. ☐ Upiši adresu Workera iz koraka 15 → **Spremi adresu**.
26. ☐ Zalijepi lozinku iz upravitelja lozinki → **Prijavi se**.
27. ☐ Klikni **"Što mogu graditi na ovoj čestici?"**. Odgovor stiže za nekoliko sekundi.
    Na dnu panela vidi se potrošnja, npr. "0,003 $ od 5 $".

### Pokretanje 47 ocjenskih pitanja (oko 0,10–0,20 $)

28. ☐ Otvori novi `cmd` u glavnoj mapi `cestica-zg-razvoj`, pa:
    ```
    cd tests
    npm install
    cd ..
    set WORKER_URL=https://cesticazg-ai.ozren.workers.dev
    set AI_LOZINKA=OVDJE_ZALIJEPI_LOZINKU
    node tests\ai-eval\run-eval.js
    ```
    Zamijeni adresu i lozinku svojima. Lozinka vrijedi samo u tom prozoru.
29. ☐ Kad završi, piše npr. `41/47 automatski prolaz`. Izvještaj je u `tests\ai-eval\izvjestaj-2026-…md`. Pošalji mi tu datoteku.
30. ☐ Zatvori prozor.

---

## Ako nešto ne radi

| Poruka | Uzrok i rješenje |
|---|---|
| `'node' is not recognized` | Node.js nije instaliran ili treba ponovno otvoriti cmd nakon instalacije (korak 1). |
| `running scripts is disabled` | Otvorio si PowerShell; koristi cmd (upiši `cmd` u adresnu traku). |
| U aplikaciji "AI servis nije dostupan" | Pogrešna adresa (korak 25) ili Worker nije objavljen (korak 19). |
| "AI asistent je isključen" | Korak 18: `AI_ENABLED` nije `"true"` ili nije ponovljen `deploy`. |
| "AI servis nije do kraja postavljen" | Nedostaje neka od četiri tajne (koraci 16–17). |
| "Pogrešna lozinka" | Lozinka mora biti ona iz koraka 13. Nakon 5 krivih pokušaja pričekaj 15 minuta. |
| "Dosegnut je limit potrošnje postavljen u Claude Consoleu" | Korak 7 ili potrošen kredit; to je očekivana zaštita. |
| Stranica se otvara, ali AI ne odgovara i nema poruke | Otvori stranicu kao `http://localhost:8000/...`, ne dvoklikom na datoteku. |

## Hitno isključivanje

- **Samo kod tebe:** ☰ → isključi "AI asistent (testno)".
- **Za sve:** u `wrangler.toml` vrati `AI_ENABLED = "false"` i pokreni `npx wrangler deploy`.
- **Ključ:** Claude Console → API keys → `cesticazg-worker` → **Delete**.

Detaljnije (opoziv prijava, promjena lozinke, brisanje Workera): `docs/ai-postavljanje.md`, odjeljak 7.

# Pristupni kodovi i dosje na e-mail (faza 1): postavljanje

Stanje 6. 11. 2026. Kod je na grani `pristup`. U aplikaciji je isključen (`FEATURES.pristup=false`) dok se Worker ne postavi.

## Kako radi

| Dio | Što radi |
|---|---|
| Aplikacija bez koda | Čestica, namjena i osnovni uvjeti gradnje. Ostali odjeljci (simulator, troškovi, 3D, okućnica, materijal, napredne analize) prikazuju karticu „Napredna funkcija”. Ispis iz preglednika ne prikazuje dosje. |
| Prijava kodom | Korisnik upiše kod (`XXXX-XXXX-XXXX`). Worker vraća potpisani token s rokom koda. Pri svakom pokretanju aplikacija provjeri token, pa opozvan kod odjavljuje. |
| Dosje na e-mail | Gumb „Pošalji dosje na e-mail”: PDF se složi u pregledniku (html2canvas + jsPDF, odjeljak po odjeljak, s podnožjem „Dosje za <e-mail>”), a Worker ga šalje preko Brevoa. Najviše 10 slanja po kodu na dan. Isto vrijedi za „Okvirne količine za upit”. |
| Administracija | `https://<worker>/admin`: stvaranje koda (oznaka, rok u danima), popis, opoziv. Kod se vidi samo pri stvaranju; u KV-u je samo njegov sažetak. |

Faza 1 zaključava sučelje. Kod naprednih funkcija još je u stranici i u javnom repozitoriju. Faza 2 ga seli iza Workera.

## Što trebaš napraviti (jednom)

### 1. Brevo (slanje e-maila, besplatno do 300 poruka na dan)
1. Otvori račun na brevo.com.
2. Senders, Domains & Dedicated IPs → Domains → dodaj `cesticahr.com` i kod pružatelja domene upiši DNS zapise koje Brevo pokaže (DKIM, DMARC). Bez toga poruke idu u neželjenu poštu.
3. SMTP & API → API Keys → Generate. Ključ kopiraj samo u korak 3 ispod, nigdje drugdje.

### 2. Cloudflare Worker
U mapi `worker-pristup` na računalu s Node.js:

```
npm install
npx wrangler login
npx wrangler kv namespace create KODOVI
```

Ispisani `id` upiši u `wrangler.toml` umjesto `UPIŠI_ID_NAKON_wrangler_kv_namespace_create`.

### 3. Tajne (svaka se upisuje kad naredba pita)

```
npx wrangler secret put TOKEN_SECRET     # dugi slučajni niz, npr. iz: node -e "console.log(crypto.randomUUID()+crypto.randomUUID())"
npx wrangler secret put CODE_PEPPER      # drugi dugi slučajni niz (ne mijenjaj ga poslije: stari kodovi prestaju vrijediti)
npx wrangler secret put ADMIN_SECRET     # tvoja administratorska lozinka (najmanje 20 znakova)
npx wrangler secret put BREVO_KEY        # ključ iz Breva
npx wrangler deploy
```

Ispisana adresa Workera (npr. `https://cesticahr-pristup.<račun>.workers.dev`) treba aplikaciji.

### 4. Uključivanje u aplikaciji
U `src/app.template.html`: `PRISTUP.api` = adresa Workera i `FEATURES.pristup:true`, zatim `python3 build.py`. To ide u `main` samo uz tvoje odobrenje. U `wrangler.toml` `ALLOWED_ORIGINS` mora sadržavati adresu s koje se aplikacija otvara.

## Svakodnevno

- Korisnik ti piše na info@cesticahr.com. Otvoriš `/admin`, upišeš lozinku, stvoriš kod (oznaka = ime ili e-mail korisnika) i pošalješ mu ga.
- Opoziv: `/admin` → Osvježi popis → Opozovi. Korisnik se odjavljuje pri sljedećem pokretanju aplikacije.
- Promjena `TOKEN_EPOCH` u `wrangler.toml` i ponovni `deploy` odjavljuje sve korisnike (kodovi ostaju valjani za novu prijavu).

## Ograničenja faze 1

- Napredni kod je u pregledniku: vješt korisnik može zaobići zaključavanje. Faza 2 (napredni paket samo uz token, privatni repozitorij, Cloudflare Pages) to rješava.
- Snimka zaslona uvijek je moguća; dosje koji stiže e-mailom nosi adresu primatelja u podnožju svake stranice.
- PDF se slaže iz slike stranice: tekst u PDF-u nije pretraživ. Karte i slike s poslužitelja koji ne dopuštaju čitanje (CORS) mogu nedostajati.
- Zaključavanje ne skriva sažetak na vrhu rezultata (osnovni način) ni karte prostornog plana.

## Testovi

- `cd worker-pristup && npm install && npm test`: Miniflare, lažni Brevo (22 provjere: kodovi, prijava, krivotvoreni token, ograničenja, opoziv, epoha, nedostajuće tajne).
- `node tests/run.js`: zaključavanje, prijava, odjava, opoziv i slanje dosjea u aplikaciji (Worker zamijenjen u testu).

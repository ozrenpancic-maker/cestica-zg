# Napredni pristup, administracija i statistika: postavljanje

Stanje 7. 11. 2026. Sve je na grani `pristup-zahtjevi`. U aplikaciji je isključeno (`FEATURES.pristup=false`, `FEATURES.analitika=false`) dok se Worker ne postavi.

## Kako radi (poluautomatsko odobravanje)

1. Korisnik u aplikaciji (ili preko poveznice `…/?zahtjev=1` s web stranice) odabere **„Zatraži besplatan napredni pristup”**, upiše e-mail i po želji namjenu.
2. Worker pošalje poruku s poveznicom za potvrdu adrese. Nepotvrđene adrese brišu se za 7 dana.
3. Nakon potvrde zahtjev je **na čekanju**, a na info@cesticahr.com stiže „Novi zahtjev za pristup ČesticaHR-u”.
4. U administraciji odabereš **Odobri**. Worker izda pojedinačni kod i pošalje ga korisniku s poveznicom za aktivaciju (`…/?pristup=KOD`).
5. Pristup traje od prve prijave: zadano 30 dana. Trajanje mijenjaš u administraciji (Postavke), bez izmjene koda.
6. Pet dana prije isteka korisnik dobije podsjetnik. U aplikaciji može zatražiti produženje; ti dobiješ obavijest.

| Dio | Gdje |
|---|---|
| Aplikacija (GitHub Pages) | obrazac, aktivacija, zaključavanje sučelja, slanje događaja za statistiku |
| Worker `cesticahr-pristup` (Cloudflare) | zahtjevi, kodovi, prijava, dosje na e-mail, administracija `/admin`, statistika, dnevni zadatak |
| D1 baza `cesticahr` (Cloudflare) | zahtjevi, sažeci kodova, dnevnik radnji, sesije, ograničenja, skupna statistika |
| Brevo | slanje e-maila |
| Cloudflare Email Routing | primanje pošte na info@cesticahr.com (prosljeđivanje na tvoj Gmail) |

## Što trebaš napraviti (jednom)

### 1. Primanje pošte na info@cesticahr.com (sada NE radi: domena nema MX zapis)
1. Cloudflare → cesticahr.com → **Email** → **Email Routing** → Get started.
2. Custom address: `info` → Action: Send to → tvoja Gmail adresa. Potvrdi poruku koja stigne na Gmail.
3. Cloudflare sam doda MX i SPF zapise. Provjera: pošalji poruku na info@cesticahr.com.

### 2. Slanje pošte (Brevo, besplatno do 300 poruka na dan)
1. Račun na brevo.com → **Senders, Domains & Dedicated IPs** → Domains → Add `cesticahr.com`.
2. Zapise koje Brevo pokaže (DKIM, kod za potvrdu, DMARC) upiši u Cloudflare → DNS. Ako Brevo nudi „Authenticate with Cloudflare”, iskoristi to.
3. Senders → dodaj `dosje@cesticahr.com` (pošiljatelj) i po želji `info@cesticahr.com`.
4. **SMTP & API → API Keys → Generate**. Ključ upisuješ samo u korak 4.

### 3. Worker i baza
U mapi `worker-pristup` (računalo s Node.js):
```
npm install
npx wrangler login
npx wrangler d1 create cesticahr
```
Ispisani `database_id` upiši u `wrangler.toml` umjesto `UPIŠI_ID_NAKON_wrangler_d1_create`, pa:
```
npx wrangler d1 migrations apply cesticahr --remote
```

### 4. Tajne (svaka se upisuje kad naredba pita)
```
npx wrangler secret put TOKEN_SECRET     # dugi slučajni niz: node -e "console.log(crypto.randomUUID()+crypto.randomUUID())"
npx wrangler secret put CODE_PEPPER      # drugi dugi slučajni niz (ne mijenjaj ga poslije)
npx wrangler secret put ADMIN_SECRET     # administratorska lozinka, najmanje 20 znakova
npx wrangler secret put ADMIN_TOTP       # tajna za drugi korak prijave (vidi ispod)
npx wrangler secret put BREVO_KEY        # ključ iz Breva
npx wrangler deploy
```
**ADMIN_TOTP (MFA):** u terminalu `node -e "const A='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';let s='';for(const b of crypto.getRandomValues(new Uint8Array(32)))s+=A[b&31];console.log(s)"`. Ispisani niz upiši kao tajnu i u aplikaciju za autentifikaciju na mobitelu (Google Authenticator, Microsoft Authenticator: „Unesi ključ za postavljanje”, vremenski). Bez ove tajne prijava radi samo lozinkom, a administracija to upozorava.

**Po želji, zaštita obrasca od robota (Cloudflare Turnstile):** Cloudflare → Turnstile → Add site, pa `npx wrangler secret put TURNSTILE_SECRET`. Bez toga obrazac štite skriveno polje, potvrda adrese i ograničenje 5 zahtjeva na sat s iste mreže.

### 5. Adresa Workera
Preporuka: Cloudflare → Workers → `cesticahr-pristup` → Settings → Domains & Routes → Add Custom Domain → `pristup.cesticahr.com`. Administracija je tada na **https://pristup.cesticahr.com/admin**.

### 6. Uključivanje u aplikaciji (tek nakon tvog odobrenja za `main`)
U `src/app.template.html`: `PRISTUP.api="https://pristup.cesticahr.com"`, `FEATURES.pristup:true`, `FEATURES.analitika:true`, pa `python3 build.py`. U `wrangler.toml` `ALLOWED_ORIGINS` mora sadržavati adresu s koje se aplikacija otvara, a `APP_URL` adresu aplikacije za poveznicu u e-mailu.

## Administracija (`/admin`)

- Prijava: lozinka i šesteroznamenkasti kod iz aplikacije za autentifikaciju. Nakon 5 neuspjelih prijava s iste mreže: čekanje 15 minuta. Sesija traje 8 sati (kolačić `__Host-`, HttpOnly, Secure, SameSite=Strict).
- **Pokazatelji** za 7, 30 ili 90 dana ili ukupno, uz definiciju svakog, grafikoni po danu i županije.
- **Zahtjevi**: e-mail, datum, namjena, status (Na čekanju, Odobren, Odbijen, Istekao, Opozvan), datum odobrenja, istek, zadnja aktivnost. Radnje: Odobri, Odbij, +30 dana, 90 dana, Neograničeno, Ponovno pošalji kod (novi kod, stari prestaje), Opozovi, Dnevnik, Obriši podatke.
- **Dnevnik**: svaka radnja s vremenom, bez e-mail adresa i kodova.

## Statistika i privatnost

- Skupni brojevi po danu: pokretanje aplikacije, pretraga, analizirana čestica, pregled ocjene, simulator, 3D, troškovi, PDF, zahtjev, aktivacija, posjet web stranice. Uz česticu se sprema samo županija.
- Bez kolačića i bez IP adrese u bazi. Broj čestice se ne šalje (šalje se samo sažetak za uklanjanje ponovljenih događaja, briše se nakon jednog dana).
- Povratni korisnici: samo uz privolu u izborniku (nasumični identifikator preglednika, u bazi samo sažetak po danu, briše se nakon 90 dana).
- Rokovi čuvanja: nepotvrđeni zahtjevi 7 dana, odbijeni 90 dana, opozvani i istekli 12 mjeseci, dnevnik 2 godine. Brisanje na zahtjev: „Obriši podatke” u administraciji.

## Testovi

- `cd worker-pristup && npm install && npm test`: Miniflare (workerd + D1), lažni Brevo, 58 provjera.
- `node tests/run.js`: obrazac, aktivacija poveznicom, neograničen pristup, produženje, statistika u aplikaciji (Worker zamijenjen u testu).

## Besplatni i napredni dio (novi model)

- **Bez koda** (kad je `FEATURES.pristup` uključen): pretraga i odabir čestice, granice, površina, duljine granica (informativno, oznake na karti) i građevinski dio čestice u m² i postotku, na karti zeleno (građevinski) i crveno (izvan). Zagreb: prema planiranoj namjeni GUP-a; Krk: županijski sloj građevinskih područja; ostatak Hrvatske i nepotpun sloj: „Nije moguće pouzdano utvrditi”.
- **Sve ostalo** (ocjena, uvjeti, pristup, mreže, ZK, simulator, 3D, okućnica, troškovi, materijal, montažne kuće, energija, PDF) samo uz odobren pristup. Pokušaj otvaranja prikazuje „Otključaj naprednu analizu zemljišta” s gumbima „Zatraži besplatan napredni pristup” i „Već imam pristupni kod”.
- Za zaključanog korisnika aplikacija **ne dohvaća i ne računa** napredne podatke (nakon čestice i namjene ne ide ni jedan upit za nagib, okolinu, mreže, ZK, 3D), pa ih nema na stranici ni u memoriji; uklanjanje elementa ništa ne otkriva. Slojevi karte s vodovima, sjenama i skenerom su zaključani.
- Statistika: besplatni pregledi, pokušaji zaključanih funkcija po funkciji, konverzija (zahtjevi iz aplikacije ÷ učitavanja s besplatnim pregledom), odobreni koji koriste napredni pristup.

## Otvoreno

- **Programski kod** naprednih funkcija i dalje je u javnoj stranici (GitHub Pages), a javni podaci dolaze izravno iz javnih servisa. Tko zna programirati, može u konzoli preglednika isključiti zaključavanje i sam dohvatiti javne podatke. Pravu zaštitu na poslužitelju daje tek faza 2: napredni dio aplikacije kao zaseban paket koji Worker šalje samo uz valjan token (i privatni repozitorij).
- Posjeti web stranice broje se tek kad objavljena stranica šalje događaj `web_posjet`.
- Odbijeni korisnik ne dobiva e-mail (upute to nisu tražile).

# Web stranica cesticahr.com i aplikacija app.cesticahr.com: postavljanje

| Adresa | Što | Gdje |
|---|---|---|
| https://cesticahr.com | web stranica (mapa `web/` u repozitoriju) | Cloudflare Pages |
| https://app.cesticahr.com | aplikacija | GitHub Pages (kao i sada) |
| https://pristup.cesticahr.com | zahtjevi, kodovi, administracija `/admin` | Cloudflare Worker (vidi `pristup-postavljanje.md`) |

Svako spajanje u `main` samo objavi i aplikaciju i web stranicu.

## 1. Aplikacija na app.cesticahr.com
1. Cloudflare → cesticahr.com → **DNS → Records → Add record**: Type `CNAME`, Name `app`, Target `ozrenpancic-maker.github.io`, Proxy status **DNS only** (siva ikona oblaka). Save.
2. GitHub → repozitorij `cestica-zg` → **Settings → Pages → Custom domain**: `app.cesticahr.com` → Save. Pričekaj zelenu kvačicu „DNS check successful” (obično nekoliko minuta).
3. Kad se pojavi, uključi **Enforce HTTPS** (certifikat može trebati do sat vremena).
4. Provjera: otvori https://app.cesticahr.com i u izborniku ☰ pogledaj verziju. Stara adresa (github.io) sama preusmjerava na novu.

Napomena: spremljene čestice i unosi čuvaju se u pregledniku po adresi. Na app.cesticahr.com kreću od početka.

Korak 2 GitHub sam zapiše kao datoteku `CNAME` u repozitorij. Datoteku ne dodaj ručno prije koraka 1: GitHub bi preusmjerio na adresu koja još ne postoji.

## 2. Web stranica na cesticahr.com
1. Cloudflare → **Workers & Pages → Create → Pages → Connect to Git**. Dopusti pristup GitHubu samo za repozitorij `cestica-zg` i odaberi ga.
2. Postavke: Project name `cesticahr`, Production branch `main`, Framework preset **None**, Build command **prazno**, Build output directory **`web`**. **Save and Deploy**.
3. Kad objava završi: projekt `cesticahr` → **Custom domains → Set up a custom domain** → `cesticahr.com` → Activate domain. Ponovi za `www.cesticahr.com`. Cloudflare sam doda DNS zapise.
4. Provjera: otvori https://cesticahr.com. Gumbi „Besplatno provjeri česticu” i „Zatraži besplatan napredni pristup” vode na app.cesticahr.com.

## 3. Nastavak
E-mail (Email Routing, Brevo), Worker i baza: `docs/pristup-postavljanje.md`, koraci 1 do 5. Worker na adresi `pristup.cesticahr.com` (korak 5 tamo) je adresa koju web stranica već koristi za brojanje posjeta.

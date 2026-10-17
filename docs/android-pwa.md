# ČesticaZG kao Android aplikacija (PWA)

## Instalacija na Android mobitel (Chrome)

1. Na mobitelu u **Chromeu** otvori adresu aplikacije (probnu, vidi niže, ili produkcijsku kad je objavljena).
2. Pričekaj da se karta učita.
3. Dodirni **⋮** (gore desno) → **Instaliraj aplikaciju** (ili **Dodaj na početni zaslon** → **Instaliraj**).
4. Potvrdi. Na početnom zaslonu pojavi se ikona **ČesticaZG**.
5. Otvori aplikaciju s ikone. Radi preko cijelog zaslona, bez adresne trake.

**Lokacija:** prvi put kad dodirneš ◎ (**Prikaži moju lokaciju**), Android pita za dopuštenje. Za čestice odaberi **Precizna lokacija**.

**Uklanjanje:** dugo pritisni ikonu → **Deinstaliraj**. Time se brišu i podaci spremljeni u aplikaciji; prije toga izvezi projekte (Troškovi → Projekt čestice → Izvezi projekt).

## Kako se ponaša

| Situacija | Ponašanje |
|---|---|
| Ima interneta | Uvijek se učitava najnovija verzija stranice; službeni podaci (katastar, GUP, slojevi Grada) dohvaćaju se uživo. |
| Nema interneta | Aplikacija se otvara. Narančasta traka kaže da se službeni podaci ne mogu dohvatiti ni osvježiti. Nova čestica se ne analizira, a stari podaci se ne prikazuju kao aktualni. Spremljene čestice i scenariji (s izračunom gradnje) vidljivi su u kartici **Spremljeno**. Karta (podloga) se ne prikazuje. |
| Nova verzija objavljena | Pri sljedećem otvaranju pojavi se **"Dostupna je nova verzija"**. **Ažuriraj** sprema unose i otvorenu česticu, učita novu verziju i ponovno otvori istu česticu. **Kasnije** zadržava staru verziju do sljedećeg otvaranja. Spremljene čestice, scenariji i unosi se ne brišu. |
| Tipka ili gesta Natrag | Redom zatvara izbornik, slojeve, Spremljeno, pa smanjuje panel (cijeli → pola → karta). Na karti izlazi iz aplikacije. |
| Android zatvori aplikaciju u pozadini | Pri sljedećem otvaranju ponovno se otvara zadnja čestica (ako ima interneta), s unosima. |
| ◎ Prikaži moju lokaciju | Plava točka i krug preciznosti. Uz preciznost do ±10 m otvara se čestica na toj točki, s upozorenjem ako je točka blizu granice. Uz lošiju preciznost aplikacija ne bira česticu sama: dodirneš česticu u krugu ili odabereš "Analiziraj česticu u središtu kruga". GPS lokacija se ne sprema i nikamo se ne šalje. |

## Probna instalacija bez promjene produkcije

GitHub Pages ove aplikacije objavljuje samo granu `main`, pa za probu treba privremena HTTPS adresa. Paket za probu je `cestica-zg-proba.zip`: sadrži `index.html`, `sw.js`, `manifest.webmanifest`, ikone i knjižnice; nema tajni.

**Preporuka: Cloudflare Pages, izravni prijenos** (besplatno, zasebna adresa):
1. Na računalu raspakiraj `cestica-zg-proba.zip`.
2. **dash.cloudflare.com** → **Workers & Pages** → **Create** → **Pages** → **Upload assets** (Direct Upload).
3. Naziv projekta npr. `cesticazg-proba` → povuci raspakiranu mapu → **Deploy**.
4. Dobiješ adresu `https://cesticazg-proba.pages.dev` i nju otvoriš na mobitelu (koraci instalacije gore).

Zašto ne drugi repozitorij na GitHub Pagesu: adresa bi bila `ozrenpancic-maker.github.io/…`, dakle isto podrijetlo kao produkcija, pa bi probna i prava aplikacija dijelile iste spremljene podatke na mobitelu. Cloudflare adresa ima vlastitu pohranu, pa proba ne može dirati podatke produkcijske aplikacije.

Druga mogućnost bez ikakvog hostinga: Chrome na računalu → `chrome://inspect` → **Port forwarding** `8000 → localhost:8000`, mobitel spojen USB-om (uključene opcije za razvojne programere i USB debugging), a na računalu `npx http-server -p 8000` u mapi paketa. Na mobitelu se otvara `http://localhost:8000`. Ovo je tehnički zahtjevnije.

## Provedeni testovi

### Automatski, u Chromiumu na računalu (Playwright i Chrome DevTools), 42/42 (`tests/mobile/pwa.py`)
- **Manifest i instalacija:**
  - manifest bez grešaka; naziv ČesticaZG; `standalone`;
  - ikone 192, 512 i maskable;
  - id aplikacije unutar `/cestica-zg/`;
  - Chrome ne prijavljuje nijednu prepreku za instalaciju.
- **Service worker:**
  - registriran za `/cestica-zg/` i upravlja stranicom;
  - sprema samo ljusku (stranica, ikone, Leaflet, Turf);
  - ne sprema službene ni mrežne podatke.
- **Bez interneta:**
  - aplikacija se pokreće i prikazuje oznaku;
  - dodir na kartu ne prikazuje stare podatke;
  - spremljene čestice i scenariji s iznosima su vidljivi.
- **Ažuriranje:**
  - obavijest o novoj verziji;
  - nakon potvrde učitava se nova verzija, a stari spremnik se briše;
  - čestice, scenariji i unosi ostaju.
- **Natrag:** cijeli panel → pola → karta; zatvaranje Spremljenog i izbornika; na karti nema dodatnog koraka.
- **Lokacija:**
  - ±45 m ne odabire česticu sama, a korisnik je može odabrati;
  - ±6 m otvara česticu;
  - GPS koordinate se nigdje ne spremaju.
- **Tipkovnica i zasloni:**
  - polje za unos ostaje vidljivo kad se smanji vidljivi dio zaslona;
  - na 320, 360, 412 i 480 px nema vodoravnog pomicanja, a dodirni ciljevi su dovoljno veliki.
- **Nastavak:** zadnja čestica pamti se kao točka unutar čestice i ponovno se otvara.

### Ostali automatski testovi
- `tests/run.js`: 281/281 (analiza, simulator, financije, scenariji, projekt, AI kod).
- `tests/mobile/layout.py` i `interaction.py`.

### Na stvarnom Android uređaju: NIJE testirano
Moja okolina nema Android uređaj. Ovo treba provjeriti na tvom mobitelu:

- [ ] instalacija kroz Chrome i ikona na početnom zaslonu (izgled maskable ikone u obliku tvog launchera);
- [ ] otvaranje s ikone bez adresne trake; boja trake stanja;
- [ ] karta, odabir čestice, analiza, simulator (povlačenje kuće prstom), kalkulator;
- [ ] gesta ili tipka Natrag (Android 13 i noviji ima prediktivnu gestu);
- [ ] tipkovnica pri unosu cijene i površine;
- [ ] način rada u zrakoplovu: pokretanje, oznaka, Spremljeno;
- [ ] ažuriranje: nova objava → obavijest → Ažuriraj → podaci ostaju;
- [ ] GPS na otvorenom: preciznost i ponašanje uz granicu čestice.

## Poznata ograničenja
- Bez interneta nema podloge karte ni analize nove čestice; to je namjerno, da se ne prikazuju zastarjeli službeni podaci.
- Fontovi se bez interneta zamjenjuju sistemskim fontom.
- Podaci su samo na uređaju. Brisanje podataka aplikacije ili deinstalacija ih briše, pa za sigurnosnu kopiju koristi "Izvezi projekt".
- GPS u gradu često ima preciznost lošiju od 10 m, pa će aplikacija češće tražiti da česticu dodirneš sam.
- iPhone i Google Play nisu u opsegu.
- AI asistent je isključen (`FEATURES.ai=false`); kod AI-1 i AI-2 je sačuvan.

# Čestica ZG

Mobilna web aplikacija: dodirneš zemljište u Zagrebu i dobiješ katastarsku česticu, namjenu iz prostornih planova, urbano pravilo GUP-a s uvjetima gradnje, provjere rizika (UPU, klizišta, zaštita, voda), pristup i okolinu, procjenu doprinosa, priključaka i cijene gradnje te popis dokumentacije s adresama ureda.

**Aplikacija:** https://ozrenpancic-maker.github.io/cestica-zg/

## Izvori podataka
- Grad Zagreb, ArcGIS servisi: katastarske čestice (2023.), planirana namjena, urbana pravila i provjere iz (ponovne) javne rasprave GUP-a 2024., baza klizišta
- Odluka o GUP-u Grada Zagreba, neslužbeni pročišćeni tekst s izmjenama 2025. (urbana pravila)
- Izmjene i dopune GUP-a Sesveta 2026., odredbe za provedbu, prijedlog za ponovnu javnu raspravu (lipanj 2026.) i karta urbanih pravila 4a
- Prostorni plan Grada Zagreba, Odredbe za provedbu (izmjene i dopune 2017.), točka 2.3.1. za građevinska područja naselja izvan GUP-ova (`src/rules_ppgz.json`)
- Topografska osnova Grada Zagreba 2018. (tlocrti postojećih zgrada); Open-Meteo / Copernicus DEM (nagib terena)
- Odluka o izmjenama i dopuni Odluke o komunalnom doprinosu (Gradska skupština, 13. 12. 2023.)
- HERA, naknada za priključenje (NN 45/2026); Uredba o Tarifi upravnih pristojbi (NN 156/2022)
- OpenStreetMap (Overpass) za ceste i sadržaje u okolini
- GUP Grada Zagreba, karte 3b (energetski sustav) i 3c (vodnogospodarski sustav) te sloj GUP_Infrastruktura: magistralni vodovod, dalekovodi i kabeli 110 kV+, trafostanice 110 kV, magistralni i VT plinovodi, toplovodi (postojeći i planirani). Ulična mreža vodovoda, kanalizacije, NN struje i distribucijskog plina nije javno objavljena (servisi Javni_vodovod i Javna_kanalizacija su samo statistika; KI_LINIJE je probno područje)

Procjene su orijentacijske. Pravno mjerodavna je lokacijska informacija Grada Zagreba.

## Izmjene
Uređuje se `src/app.template.html`, a `python3 build.py` sastavlja `index.html`.
Pravila za Sesvete: `pdfplumber` tekst prvog dijela PDF-a odredbi (bez prikaza izmjena), zatim `python3 src/parse_gup_sesvete.py ses_first.txt src/rules_sesvete.json`.

## Ažuriranje pravila (kad se plan promijeni)
Pravila su odvojena od aplikacije, u `src/rules.json` (GUP Zagreba), `src/rules_sesvete.json` (GUP Sesveta) i `src/rules_ppgz.json` (PPGZ). Izvor, verzija i status svake datoteke su u `src/rules_meta.json` i prikazuju se u aplikaciji.
1. Novi tekst odluke pretvori u tekst (`pdftotext -layout` ili `pdfplumber`) i pokreni odgovarajući `src/parse_*.py`.
2. Ažuriraj `src/rules_meta.json` (verzija, datum, status).
3. `python3 build.py` provjerava strukturu pravila i prekida ako nešto nedostaje.
4. `cd tests && node audit.js` ispisuje izvučene parametre za svako pravilo i tip kuće, za usporedbu s tekstom; `node audit.js "GUP 2.2." k` ispisuje i izvorne rečenice.
5. `cd tests && npm install && npm test` pokreće automatske testove.

## Grane
- `main`: objavljena verzija (GitHub Pages)
- `razvoj`: rad u tijeku, objavljuje se tek nakon pregleda
- `stabilna-2026-10-17`: sigurnosna kopija stabilne verzije

## Mobilno sučelje (faza M)
Ispod 900 px: karta preko cijelog ekrana, donji panel s tri stanja (sažetak, pola, cijeli ekran), donja navigacija Karta · Analiza · Troškovi · Spremljeno. Sadržaj je podijeljen u skupine (`.grp[data-g]`: sažetak, analiza, troškovi) koje se samo skrivaju i prikazuju, pa se unosi ne gube. Na računalu je raspored kao prije.

Provjere u pregledniku (Chromium, Playwright):
```
cd tests && node mobile/make_local.js && python3 mobile/layout.py && python3 mobile/interaction.py
```
Ručno na uređaju (automatski testovi to ne zamjenjuju): Android Chrome i iPhone Safari; povlačenje panela, pomicanje i okretanje kuće prstom, tipkovnica kod unosa cijene, okomito i vodoravno, veliki sustavski font, ispis u PDF.

## Android aplikacija (PWA)
`manifest.webmanifest`, `sw.js` (izrađuje ga `build.py` iz `src/sw.template.js`, s verzijom), ikone u `icons/`, knjižnice u `vendor/` (Leaflet 1.9.4, Turf 6.5.0, s licencama). Upute, testovi i ograničenja: `docs/android-pwa.md`. Testovi u Chromiumu: `cd tests && python3 mobile/pwa.py`.

## AI asistent
Plan i arhitektura: `docs/ai-asistent-plan.md`. AI-2 (samo čitanje) je u kodu, ali trenutno isključen (`FEATURES.ai=false`). Backend je u `worker/` (Cloudflare Worker + Durable Object; testovi: `cd worker && npm install && npm test`) i nije objavljen. Postavljanje, limiti, trošak i gašenje: `docs/ai-postavljanje.md`. Ocjenjivanje: `docs/ai-ocjenjivanje.md`. API ključ se nikad ne sprema u repozitorij ni u aplikaciju.

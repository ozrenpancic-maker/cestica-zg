# Prijedlog: hibridni čitač (AI predlaže, deterministički sustav provjerava)

**Status: prijedlog, ništa nije implementirano.** AI nije uključen u produkciju, ne dira `main` i ne prihvaća ništa sam. Pravno potvrđenih pravila: 0.

## 1. Zašto
Stanje nakon tri slijepa testa i v2.6:

| | Deterministički čitač |
|---|---|
| Pogrešna prihvaćanja | 0 na Krku, Korniću, Novom Vinodolskom i Crikvenici; 0 u slijepom testu v2.5 |
| Prihvaćanja na neviđenom planu | 0 (slijepi v2.3 Novi Vinodolski, slijepi v2.5 Crikvenica) |
| Razvojni dobitak | ostaje na planu na kojem je razvijen; svaki novi plan donosi nove oblike rečenica |
| Izvan dosega obrazaca | velik dio oznaka je »drugo:« ili opisne odredbe (način gradnje, rekonstrukcija, dopuštenost, upućivanja) |

Deterministički dio je dobar **sudac točnosti**, ali slab **generator kandidata**. Za jezik (raznolikost rečenica) AI je jak, za jamstvo točnosti slab. Hibrid razdvaja te dvije uloge.

## 2. Arhitektura
```
izvor (HTML/PDF) ──► izvor_v26.ucitaj ──► tekst članaka (SHA) ──┬──► deterministički čitač v2.6 ──► kandidati D
                                                                └──► AI generator (bez oznaka) ──► kandidati A (JSON)
kandidati A ──► PROVJERA (deterministička, zamrznuta) ──► status po pravilu ispod
kandidati D ∪ provjereni A ──► spajanje po (članak, stavak, parametar, vrijednost, citat) ──► izlaz + izvještaj razlika
```

**AI generator** dobiva samo tekst članka (s naslovom i uvodom stavka) i zatvoreni popis parametara. Vraća strukturirane kandidate, svaki s doslovnim citatom. Ne dobiva oznake, rezultate čitača ni referentne skupove.

## 3. Ugovor kandidata (JSON)
```json
{"clanak": 24, "stavak": null, "citat": "Najveći dopušteni koeficijent izgrađenosti (k ig ) iznosi 0,5.",
 "parametar": "kig", "operator": "<=", "vrijednost": 0.5, "jedinica": "koeficijent",
 "vrsta_gradevine": {"izraz": "građevina poslovne namjene", "citat_izraza": "planiran je smještaj građevina poslovne namjene"},
 "uvjeti": [{"tekst": "…", "citat": "…"}], "prostorni_obuhvat": {"oznake": ["K1 1", "K1 2"], "citat": "(K1 1 i K1 2 )"},
 "vrsta_pravila": "OSNOVNO", "napomena_ai": "…"}
```
Svaka tvrdnja (vrijednost, vrsta, uvjet, obuhvat) mora imati svoj doslovni citat. Tvrdnja bez citata je samo napomena i ne utječe na status.

## 4. Deterministička provjera (zamrznuta prije pokusa)
| Provjera | Pravilo | Kad ne prolazi |
|---|---|---|
| Izvor | SHA teksta članka jednak je onom iz `izvor_v26` | ODBIJENO |
| Citat | točan podniz teksta članka (nakon iste normalizacije razmaka) | ODBIJENO |
| Vrijednost | broj se nalazi u citatu kao zaseban literal (`citac.ima_broj`, tisućice v2.6); tekstna vrijednost je podniz citata | ODBIJENO |
| Jedinica | jedinica stoji uz taj broj u citatu | PREGLED |
| Operator | izveden iz izraza u citatu po zamrznutoj tablici (»najviše / ne više od« → ≤, »najmanje / ne može biti manja od« → ≥, bez izričitog minimuma → doslovno »=« prema odluci suca v1.3/2) i jednak AI-jevom | PREGLED |
| Parametar | u zatvorenom popisu; ključne riječi parametra prisutne u citatu | PREGLED (izvan popisa uvijek PREGLED) |
| Vrsta građevine | `citat_izraza` je podniz članka; `vrste_gradevina.prepoznaj` daje istu vrstu; odnos izraza je OBJEKT_GRADNJE (`gramatika_v26.vrste_uvoda`); nema druge vrste u istom odnosu | PREGLED |
| Uvjeti | svaki uvjet je podniz citata ili uvoda; svaki uvjetni veznik iz citata (»ukoliko / ako / kada / uz uvjet / iznimno«) pokriven je zapisanim uvjetom | PREGLED |
| Obuhvat | oznake zona iz naslova / uvoda (`zone_naslova`, `oznake_zona`) moraju biti u kandidatu | PREGLED |
| Sukob | kandidat proturječi kandidatu D za isti citat i parametar | PREGLED + oba zapisa sucu |

## 5. Pravilo statusa
1. **AI kandidat nikad nije automatski PRIJEDLOG.** U pokusu svaki AI kandidat koji prođe provjeru dobiva status `PROVJERENO_AI` (prolazi provjere, ali čeka suca).
2. **PRIJEDLOG nastaje samo kad se slažu oboje:** deterministički čitač je nezavisno izdvojio isto pravilo (citat, parametar, operator, vrijednost, vrsta) i nema razloga za pregled. AI tada samo potvrđuje.
3. Kandidati koje je izdvojio samo AI ostaju `PROVJERENO_AI` ili PREGLED dok sudac ne potvrdi kategoriju, kao kod novih kategorija u v2.5.
4. Neslaganje AI i D uvijek ide sucu s oba zapisa i citatom.

## 6. Pokus (prije bilo kakve odluke o produkciji)
1. **Zamrzavanje:** provjera, prompt generatora i tablica operatora zamrzavaju se prije prvog pokretanja.
2. **Razvojni skupovi:** Krk, Kornić, Novi Vinodolski, Crikvenica, s istim usporedbama kao `mjeri_v26` (strogo i semantički).
3. **Slijepi test** na novom, neotvaranom planu. Označivač i AI generator su dva različita, međusobno izolirana agenta. Oznake se zamrzavaju prije pokretanja generatora.
4. **Mjeri se zasebno:** kandidati A, A koji prolaze provjeru, A ∩ D, samo A, samo D, pogrešno među `PROVJERENO_AI`, pokrivenost JASNIH, razlike stroge i semantičke usporedbe.
5. **Prag uspjeha (prijedlog, odlučuje sudac):**
   - 0 pogrešnih među PRIJEDLOG;
   - ≤ 2 % pogrešnih među `PROVJERENO_AI`;
   - pokrivenost JASNIH na slijepom planu barem 40 % (sada 0 %).

## 7. Ograničenja i otvorena pitanja
- **Pravilo projekta »bez plaćenih API-ja i tajni«.** Pokus se može provesti bez ključeva u kodu, jednako kao neovisni označivač: generator radi kao izolirani agent u sesiji, a njegov JSON se zamrzava i obrađuje deterministički. Za produkciju bi trebala posebna odluka: lokalni otvoreni model bez tajni ili izmjena pravila. To ovaj prijedlog ne rješava.
- **Ponovljivost.** Izlaz AI-ja nije determinističan. Zato se zamrzava svaki JSON (SHA), a ne samo prompt. Usporedba uvijek radi nad zamrznutim JSON-om.
- **Tko gradi, ne ocjenjuje.** Generator, označivač i provjera moraju biti razdvojeni. Prompt generatora se ne smije prilagođavati nakon uvida u oznake slijepog plana.
- **Pravni smisao.** AI-jevo tumačenje (npr. »interpolacija«, »ulični niz«) nikad ne ulazi u vrijednost. Ostaje u `napomena_ai` i vodi na PREGLED.

## 8. Preporuka
**Primarni smjer razvoja prebaciti na hibridni čitač, uz uvjet pokusa iz odjeljka 6.** Deterministički čitač v2.6 ostaje zamrznut kao provjera i sigurnosna mreža, a ne kao glavni generator kandidata.

Obrazloženje:
- Četiri kruga obrazaca dala su odličnu sigurnost (0 pogrešnih), ali na dva neviđena plana 0 prihvaćanja.
- Svaki novi plan otkriva nove rečenične oblike, pa trošak raste po planu, a dobitak se ne prenosi.
- Provjere koje su se pokazale vrijednima (doslovni citat, broj u citatu, vrsta kao objekt gradnje, zona iz naslova, uvjetni veznik) prirodno postaju provjera AI kandidata.

Ako pokus ne zadovolji prag, nastavlja se determinističkim putem s v2.7, a zamrznuti rezultati pokusa ostaju kao dokaz.

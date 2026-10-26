# Čitač v2.2: analiza pogrešaka v2.1 i dizajn

## 1. Analiza pogrešaka slijepog testa v2.1 (UPU 1 – Krk, čl. 14. i 24.)
Rezultat v2.1 bio je 0 / 0 / 0 / 101 (točno / pogrešno / pregled / propušteno). Oba članka su odbijena na razini članka.

| # | Uzrok | Posljedica | Rješenje u v2.2 |
|---|---|---|---|
| 1 | Rječnik skupina sadržavao je samo stambene i poljoprivredne građevine | `SKUPINA_NEPOZNATA` za sportsko-rekreacijske, hotele, pomoćne | `vrste_gradevina.py`: 14 vrsta u 9 kategorija, s kombiniranim namjenama |
| 2 | Oblici riječi bili su ručni regexi po riječi (»stamben\w* građevin\w*«) | svaki novi naziv tražio je novi regex | `morfologija_hr.py`: osnove riječi (nastavci sklonidbe jd. i mn.); naziv se piše jednom, u nominativu |
| 3 | Alineje su se prepoznavale samo uz malo početno slovo (v1 `alineje`) | cijeli članak postao je jedna jedinica | razdvajanje i uz veliko slovo (»- Najmanja …«), i u putu sa stavcima |
| 4 | Numerirani podnaslovi (»3. veličina i smještaj …«) nisu bili kontekst | pravila bloka »7. pomoćne građevine« dobila bi vrstu »hotel« | `blokovi()`: kontekst se prenosi samo unutar bloka; podnaslov ili uvod s dvotočkom ga zamjenjuje |
| 5 | Predmeti su ovisili o velikom slovu i točnom redu riječi | »Najmanja dopuštena udaljenost građevine od …«, »koeficijent iskorištenosti«, »tlocrtna projekcija« | predmeti bez obzira na veliko slovo; terminološke istoznačnice |
| 6 | Novi oblici odredbi | »ne može biti manja od«; izostavljeni predmet u »…, a za razvrstane ceste …«; kategorija ceste; udio zelenila; (h1+h2)/2; zagrada s brojem etaža; »º« umjesto »°« | posebni oblici (`f_zelenilo`, `f_medjusobna`, `f_krovista2`), koordinacija s preuzetim predmetom, `CESTE` kao uvjet |

Dodatni nalaz faze B: dopuštenje gradnje iz uvoda stavka v2.1 je prihvaćala samostalno, iako ovisi o alinejama koje su za pregled.

## 2. Pogrešno prenošenje konteksta (nađeno tijekom razvoja v2.2)
Prva verzija v2.2 uzimala je prvu vrstu građevine koja se igdje spominje u uvodu. Primjeri iz PPUG-a:
- čl. 75.: »pomoćne« iz popisa sadržaja;
- čl. 52.: »ugostiteljsko-turističke« iz rečenice o prenamjeni.

Kontekst sada određuje `skupina_strogo()`. Vrsta postaje kontekst samo kao:
- subjekt na početku rečenice;
- subjekt ispred »mogu se graditi«;
- objekt glagola gradnje (»graditi X«, »za izgradnju X«, »rekonstrukcija X«), kad X počinje nazivom vrste.

Usputno spominjanje se ne uzima.

Dodatne zaštite:
- **Iznimna alineja:** rečenice iza »iznimno, unutar … cjelina« u istoj alineji nasljeđuju uvjet i vrstu IZNIMKA. Bez toga bi »Najmanja dopuštena udaljenost od regulacijskog pravca iznosi 4,0 metra« (čl. 20., 50.) bila prihvaćena kao osnovno pravilo.
- **Iznimni dio članka:** »Iznimno, od odredbi ovog članka na … k.č. …« vrijedi samo od te rečenice do kraja bloka.
- **Nepouzdana struktura:** u članku s ponovljenim brojevima stavaka (npr. čl. 56.) sva pravila su PREGLED (`STRUKTURA_CLANKA_NEPOUZDANA`).

## 3. Što v2.2 ne prihvaća automatski
Pravilo je PREGLED kad:
- **nedostaje bitan uvjet primjene:** `OVISI_O_UVJETIMA_ZA_PREGLED`, `UVJET_SAMO_ZA_X`, `SKUPINA_NEPOZNATA`;
- **prostorni obuhvat nije određen:** `ZONA_NIJE_DEFINIRANA`, `STRUKTURA_CLANKA_NEPOUZDANA`;
- **referentna točka nije jasna:** `REFERENTNA_VISINA_NEPOZNATA` / `_NEPOTPUNA`, `H_NIJE_DEFINIRAN`, `GRANICA_CESTICE_NERAZGRANICENA`;
- **formula kombinira različite mjerne reference:** `RAZLICITE_REFERENTNE_TOCKE` (h/2 i X se tada ne spajaju);
- **postoji nerazjašnjena iznimka:** `IZNIMKA_BEZ_UVJETA`, `ODNOS_PREMA_FORMULI_NEJASAN`, `MOGUC_SUKOB_ODREDBI`;
- **izvorni tekst ne opravdava zaključak:**
  - `ZABRANA_IZVEDENA`, `NAGIB_UZ_KOSO_TUMACENJE`, `TUMACENJE_ZAGRADE`, `ZAGRADA_OBJASNJENJE`;
  - `DIO_ODREDBE_NEPREPOZNAT`, `NEISKORISTENI_BROJEVI`, `SEMANTIKA_PROTURJECNA`.

## 4. Prostorna primjenjivost
`prostorni_obuhvat` bilježi što tekst kaže o mjestu primjene, s doslovnim dokazom:
- `ZONA_PLANA` (npr. R1₁ Lunta, T1₂);
- `POVIJESNA_CJELINA`;
- `KATASTARSKA_CESTICA`;
- `KATEGORIJA_CESTE`;
- `OZNAKA_NEDEFINIRANA`;
- `NIJE_NAVEDEN_U_ODREDBI`.

`primjenjivost_na_lokaciju` je uvijek `NIJE_UTVRĐENA`. Da pravilo vrijedi za određenu česticu, može se utvrditi tek iz kartografske podloge. Prepoznato pravilo nije dokaz primjenjivosti.

## 5. Logika uvjeta
`uvjet_logika`:
- `I` – više uvjeta;
- `ILI`;
- `NE(ILI …)` – »nisu predviđeni A niti B«;
- `NEJASNO_I_ILI` – »ima A, B i C«: svi zajedno ili bilo koji;
- `NEJASNO` – »odnosno«.

Formule: `max(h/2, X)` samo uz istu referencu; `max((h1+h2)/2, X)`.

## 6. Objašnjivost
Svako pravilo ima:
- izvor: članak, stavak, blok, točku, alineju i rečenicu;
- doslovni `izvorni_citat` i trag normalizacije;
- uvjet primjene;
- `obrazlozenje_statusa`: zašto je PRIJEDLOG, ili popis razloga za PREGLED.

## 7. Ovisnosti
Nema novih ovisnosti, a veliki jezični modeli se ne koriste. Morfologija je skup pravila (nastavci). Morfološki rječnik nije uveden jer prolazi iste testove bez njega.

Poznata ograničenja morfologije:
- glasovne promjene (nepostojano a: »pravac« / »pravca«; sibilarizacija);
- glagolski oblici.

## 8. Usporedba i granularnost
Pravila granularnosti (`oznake/mapiranje_v22.json`) broje se zasebno (`tocno_uz_pravilo_granularnosti`), nikad kao strogo točna:
- `GRANICA_ALINEJE`;
- `ALTERNATIVA_UZ_UVJET`;
- `OPISNA_JEDNAKOST_ILI_DOPUSTENJE`.

Svaki je nastao zato što se dva neovisna označivača razilaze za istu rečenicu.

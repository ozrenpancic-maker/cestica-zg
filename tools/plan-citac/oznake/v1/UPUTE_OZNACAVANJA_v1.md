# Upute za označavanje odredbi prostornih planova, v1

Svrha: referentni skup za mjerenje čitača.
- Dva neovisna označivača označe isti tekst po ovim uputama.
- Gdje se razilaze, odlučuje sudac (Ozren Pančić) i bilježi obrazloženje.
- **Ovo nije pravna potvrda.** Skup pokazuje što tekst doslovno kaže i gdje je nejasan.

## 1. Jedinica označavanja
- **Jedan zapis = jedno ograničenje** za jednu vrstu građevine. Primjer: »- za slobodnostojeće: 500 m², - za dvojne: 300 m²« su dva zapisa.
- **Raspon je jedan zapis:** »između 17° i 23°« → operator `izmedju`, vrijednost `"17–23"`.
- **Ne izmišljati.** Ne bilježi se ono čega nema u tekstu. Zapis `nije_propisano` nastaje samo kad tekst to izričito kaže (»ne propisuje se …«), a nikad zato što se parametar ne spominje.
- **Neobvezujući tekst se ne označava:** naslovi, ostaci prijeloma (»2.2.2.1. Obiteljska kuća«), opisi kartografskih prikaza.

## 2. Polja
| Polje | Pravilo |
|---|---|
| `id` | jedinstven u datoteci |
| `clanak`, `stavak` | broj; `stavak` je null ako članak nema oznake »(n)« |
| `tocka` | slovo točke »a)«; `"-"` ako je odredba u alineji; null za uvod stavka i za tekst bez točaka i alineja |
| `alineja_rb` | redni broj alineje unutar stavka ili bloka (1, 2, …), inače null |
| `citat` | doslovni odlomak, bez skraćivanja i bez »…«; mora sadržavati vrijednost i uvjet |
| `vrsta_gradevine` | vrsta iz teksta u nominativu jednine, oblik iza »–«: »stambena građevina – slobodnostojeća«. Stanje u zagradi: »(nova)«, »(postojeća)«. **Podrum ne ide u vrstu**, nego u uvjet |
| `parametar` | iz zatvorenog popisa (odjeljak 5); inače `"drugo: <kratki opis>"` |
| `operator` | `=`, `<=`, `>=`, `izmedju`, `max(h/2, X)`, `max((h1+h2)/2, X)`, `dopustenje`, `zabrana`, `opis`, `nije_propisano` |
| `vrijednost` | broj (decimalna točka), tekst kako piše u izvoru, ili null |
| `jedinica` | `m`, `m²`, `°`, `%`, `koeficijent` (kig, kis), `opis` ili null |
| `uvjet_primjene` | doslovni uvjeti, više njih odvojeno sa »; «; bez riječi »iznimno« (to je vrsta pravila) |
| `modal` | `mora` (obveza: »mora biti«, »iznosi«, »najviše«, »najmanje«), `moze` (mogućnost: »može / mogu biti«) |
| `alternative` | popis mogućnosti kad vrijednost nabraja »A ili B« (»ravna«, »kosa«), inače [] |
| `vrsta_pravila` | `OSNOVNO`, `IZNIMKA` (»iznimno« ili posebna zona umjesto općeg pravila), `UVJETNO` (vrijedi samo uz uvjet), `NEGATIVNO` (zabrana) |
| `jednoznacnost` | `JASAN` ili `PREGLED` (odjeljak 4) |
| `razlozi_pregleda` | kodovi iz odjeljka 4 i kratko obrazloženje |

## 3. Odluke koje su prije bile sporne
Ove su tri točke prije davale različite oznake za istu rečenicu. Sada su zabilježene kao činjenice, pa ne ovise o tumačenju:
- **ALTERNATIVA** više nije vrsta pravila. Mogućnosti se bilježe u polje `alternative`, a vrsta pravila je OSNOVNO ili UVJETNO prema uvjetu.
- **»=« ili »dopuštenje«** za »pokrov mora biti A ili B« određuje polje `modal`:
  - `mora` + alternative → operator `=`;
  - `moze` + alternative → operator `dopustenje`.
- **Granica alineje:** rečenice iza prve u istoj alineji (do sljedeće »- «) pripadaju toj alineji (`tocka "-"`, isti `alineja_rb`).

## 4. JASAN i PREGLED
Ako vrijedi barem jedno od sljedećeg, oznaka je `PREGLED` s kodom razloga:

| Kod | Kada |
|---|---|
| `TOCKA_MJERENJA` | visina ili udaljenost bez obje točke mjerenja, npr. »visina od najniže kote …« bez gornje točke; nedefiniran h |
| `NEDEFINIRAN_POJAM` | pojam ili oznaka nije definirana u tekstu: »NA2-NA15.2«, »granica susjedne građevine« |
| `VEZNIK` | »i« ili »odnosno« u uvjetu može značiti »sve« ili »bilo koje« |
| `ODNOS_ODREDBI` | nejasno zamjenjuje li vrijednost drugu ili joj se dodaje (»može iznositi i 3,0 m« uz h/2) |
| `SUKOB` | proturječi drugoj odredbi u danom tekstu |
| `UPUCIVANJE` | ovisi o odredbama koje nisu u danom tekstu (»u skladu s odredbama ovog Plana«) |
| `OBUHVAT` | primjena ovisi o zoni ili obuhvatu koji tekst ne određuje |
| `TUMACENJE` | zaključak traži tumačenje koje tekst ne daje izravno (npr. zabrana izvedena iz »samo«) |

Napomena za suca: otvorena pitanja (npr. treba li »granica građevne čestice« sama po sebi PREGLED) ne odlučuju se u uputama. Kad se označivači razilaze, o njima odlučuje sudac.

## 5. Zatvoreni popis parametara
- najmanja površina građevne čestice
- najveća površina građevne čestice
- najmanja površina tlocrtne projekcije građevine
- najveća površina tlocrtne projekcije građevine
- najveći koeficijent izgrađenosti (kig)
- najveći koeficijent iskoristivosti (kis) nadzemnih etaža
- najveći koeficijent iskoristivosti (kis) (uz podrum ili ukupni)
- najveći broj etaža
- najveća visina građevine
- najmanja udaljenost od granice građevne čestice
- najmanja udaljenost od regulacijskog pravca
- najmanja udaljenost između građevina na istoj čestici
- najmanja udaljenost istaka od granice susjedne građevine
- najmanja udaljenost istaka od granice građevne čestice
- položaj građevnog pravca
- najmanji udio zelenila na građevnoj čestici
- način gradnje
- prislanjanje uz susjednu građevinu ili granicu građevne čestice
- dopuštenost gradnje
- oblik krovišta
- vrsta kosog krovišta
- nagib krovnih ploha
- vrsta pokrova
- rekonstrukcija i prenamjena
- gabariti pri rekonstrukciji

## 6. Postupak
1. **Dva označivača.** Označivač A čita kao stručnjak za prostorno planiranje. Označivač B čita strogo doslovno, kao upravni pravnik. Rade svaki u svom kontekstu, bez alata, bez uvida u izlaze čitača i u tuđe oznake.
2. **Spajanje.** Zapisi se strojno sparuju po članku, stavku, točki, alineji, parametru, vrsti građevine i vrijednosti.
3. **Odluka suca.** Sve što se razlikuje ide sucu, uz oba prijedloga i doslovni citat. Sudac bira A, B ili oba (ako su istovrijedni) ili upisuje ispravak, i za svaku odluku daje kratko obrazloženje.
4. **Zamrzavanje.** Pregledani skup zamrzava se s kontrolnim sumama: tekst, oznake A, oznake B, odluke, konačni skup.

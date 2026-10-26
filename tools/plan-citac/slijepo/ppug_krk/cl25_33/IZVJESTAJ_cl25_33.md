# Slijepa usporedba: PPUG Krk čl. 25. i 33., zamrznuti čitač v1

**Postupak**
1. Gramatika i izlazi zamrznuti su (`ZAMRZNUTO_v1.json`, commit `6b195a5`).
2. Neovisne oznake napravljene su u zasebnom kontekstu, samo iz doslovnog teksta (`za_oznacavanje/`), a zatim zamrznute (commit `92e68a1`).
3. Tek nakon toga provedena je usporedba (`usporedi_cl25_33.py`), koja prije usporedbe provjerava sve kontrolne sume.

## Rezultat

| | čl. 25. | čl. 33. | ukupno |
|---|---|---|---|
| neovisnih oznaka | 22 | 12 | 34 |
| – od toga jasnih / za pregled (prema označivaču) | 17 / 5 | 0 / 12 | 17 / 17 |
| točno prepoznato | 0 | 0 | 0 |
| pogrešno | 0 | 0 | 0 |
| za pregled (modul) | 0 | 0 | 0 |
| propušteno | 22 | 12 | 34 |
| članak odbijen u cijelosti | da | da | |

**Stvarna pokrivenost zamrznutog čitača na ova dva neviđena članka je 0 %. Lažnih pravila nema.**

## Potpuno odbijeni članci i razlozi
Oba članka čitač je odbio s razlogom »vrsta građevine iz uvodne rečenice članka nije prepoznata«. Prvo su ih odbili obrasci UPU-a 2, a zatim i gramatika, jer nije prepoznala skupinu ni oblik građevine.

- **Čl. 25. (stambene građevine)**
  - Uvod »za izgradnju stambenih građevina« (genitiv množine) nije u rječniku skupina.
  - Oblik građevine nije naveden nijednim popisom (»- za slobodnostojeće …«), nego riječima »za sve tipove gradnje« i »samo kao samostojeće«.
  - Dijagnostika istih zamrznutih funkcija po odredbi, bez konteksta članka (ne broji se kao prijedlog):
    - stavak (2) o poljoprivrednim građevinama: 7 odredbi prepoznato;
    - stavak (1): 6 odredbi odbijeno, zbog »500 m 2 ;«, »određuje se 0,25«, »100 m 2 za sve tipove gradnje«, »0,50;«;
    - 2 odredbe bez broja: »ne propisuje se …« i »samo kao samostojeće«.
- **Čl. 33. (udaljenosti stambenih građevina)**
  - Struktura su stavci bez točaka i alineja. Predmet je izražen glagolom (»moraju biti udaljene najmanje pola visine (h/2) … ali ne manje od …«) i nije u rječniku.
  - Sva 4 stavka su odbijena.

## Što oznake pokazuju o tekstu
Ove točke su važne za proširenje gramatike, ali gramatika nije mijenjana.

**Vrste pravila koje gramatika ne zna prikazati**
- **Negativna pravila i »nije propisano«:** čl. 25. t. b) i t. h) (»samo kao samostojeće«).
- **Alternative:** ravno ili koso krovište; dvojne ili ugrađene kuće.
- **Složeni operator** »najmanje h/2, ali ne manje od X«, s uvjetom koji se odnosi na otvore.

**Dvosmislenosti koje je označivač istaknuo**
- Raspon zona »NA2-NA15.2« nije definiran u tekstu.
- Nije jasno je li kis 0,75 uz podrum ukupni kis.
- Visina »h« nije definirana.
- Veznik »i« u uvjetu »otvore, prohodne terase i otvorena stubišta« može značiti »sve zajedno« ili »bilo koje«.
- Nije jasno zamjenjuje li 3,0 m (2,0 m) cijeli izraz s h/2 ili samo donju granicu.
- Pojam »granica susjedne građevine« nije definiran.

**Proturječje unutar plana**
- Čl. 25. st. 1. t. h): stambene građevine »samo kao samostojeće«.
- Čl. 33. st. 2. i 4.: uređuju udaljenosti dvojnih i ugrađenih obiteljskih i višeobiteljskih kuća.
- Iz izvatka se ne vidi obuhvat jedne i druge odredbe.

## Ograničenja
- **Neovisnost:** označivač je isti model kao razvojni. Neovisnost je osigurana samo odvojenim kontekstom i bez pristupa izlazima, kodu i ranijim oznakama; transkript potvrđuje da nije koristio alate.
- **Granularnost oznaka** (npr. jedan zapis za raspon 17–23°) razlikuje se od granularnosti oznaka za čl. 22. i 23. To ne utječe na ovaj rezultat, jer modul nema prijedloga. Za sljedeću usporedbu treba prije usporedbe dogovoriti mapiranje.
- **Pravna potvrda: 0.**

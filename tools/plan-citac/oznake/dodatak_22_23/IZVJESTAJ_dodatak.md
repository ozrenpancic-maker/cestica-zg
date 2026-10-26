# Šest dodatnih automatski prihvaćenih pravila v2.1 (st. 2. čl. 22. i 23.)

- **Dodatak oznaka:** `oznake_dodatak_st2.json`, SHA-256 `7e64ed66b56c9ba317efd0f41eb7035163a5070907092dee44adb6881cb6a170`, commit `2b69a97`.
  - Označivač je pomoćni agent u zasebnom kontekstu, bez alata i bez uvida u izlaze modula.
  - Ulaz je doslovni st. 2. (`za_oznacavanje_st2.txt`, SHA-256 `30a8a321…`).
  - Mapiranje je napisano prije primitka oznaka (`mapiranje_dodatak.json`).
- **Postojeći referentni skup 22./23.** (`b5605796…`) nije mijenjan.
- **Citati:** 6 od 26 citata označivač je skratio s »…«: D007, D008, D011, D020, D021, D024. Ostali su doslovni.
- **Usporedba:** `usporedba_dodatak_v2_1.json` (`usporedi_dodatak.py`).

| Pravilo v2.1 | Doslovni citat (članak, stavak, alineja) | Izdvojeno pravilo | Razlog prihvaćanja u v2.1 | Oznaka | Ocjena |
|---|---|---|---|---|---|
| 22.2.0.0.1.16 | »Poljoprivredne gospodarske građevine mogu se graditi na građevnoj čestici uz obiteljsku kuću uz poštivanje sljedećih uvjeta:« (čl. 22. st. 2., uvod) | dopustenaGradnja, dopušteno, UVJETNO, uvjet »na građevnoj čestici uz obiteljsku kuću uz poštivanje sljedećih uvjeta« | cijela rečenica odgovara obliku »X mogu se graditi na građevnoj čestici uz … uz poštivanje sljedećih uvjeta«; nema brojeva ni neriješenih dijelova | D001 JASAN | sadržajno isto. Raspored je drukčiji: oznaka stavlja »na građevnoj čestici uz obiteljsku kuću« u vrijednost, a modul u uvjet |
| 23.2.0.0.1.15 | isto, »uz višeobiteljsku kuću« (čl. 23. st. 2., uvod) | isto | isto | D014 JASAN | isto kao gore |
| 22.2.-.4.1.20 | »krovišta mogu biti ravna ili kosa (…)« (čl. 22. st. 2., al. 4) | oblikKrovista, dopušteno, »ravna ili kosa«, ALTERNATIVA, bez uvjeta | cijela alineja odgovara obliku krovišta (KROV); sve vrijednosti iskorištene | D005 JASAN | **točno** |
| 23.2.-.4.1.19 | isto (čl. 23. st. 2., al. 4) | isto | isto | D018 JASAN | **točno** |
| 22.2.-.4.1.21 | »… (ako se grade kao kosa mogu biti jednostrešna, dvostrešna ili višestrešna …« (čl. 22. st. 2., al. 4) | vrstaKosogKrovista, dopušteno, »jednostrešna, dvostrešna ili višestrešna«, ALTERNATIVA, uvjet »ako se grade kao kosa« | kao gore | D006 JASAN | vrijednost, operator i uvjet su isti. Vrsta pravila se razlikuje: oznaka UVJETNO, modul ALTERNATIVA. Oznaka čl. 25. (N017) također je ALTERNATIVA uz uvjet, pa se dvije oznake međusobno razilaze |
| 23.2.-.4.1.20 | isto (čl. 23. st. 2., al. 4) | isto | isto | D019 JASAN | isto kao gore |

Dva pravila za pregled (rekonstrukcijaIPrenamjena, čl. 22. i 23., al. 7) odgovaraju oznakama D012 i D025, koje su također PREGLED.

**Nijedno od šest pravila nije pogrešno.**

## Mogući sukobi
- **dopustenaGradnja:** dopuštenje vrijedi samo uz kumulativno ispunjenje svih alineja stavka. Neke od tih alineja su u v2.1 za pregled (visina, udaljenost od granice čestice, iznimke). Označivač to navodi kao ovisnost (D001, D014).
  - **v2.1 tu ovisnost ne bilježi.** Dopuštenje je prihvaćeno samostalno, a polje `nerijesene_ovisnosti` je prazno.
  - To je slabost. Ispravlja se u v2.2: dopuštenje je PREGLED dok su uvjetne alineje za pregled.
- **Krovišta:** u ostatku PPUG-a (čl. 20., 25., 39., 45., 50., 52.) isti tekst propisuje isto, pa sukoba nema. Čl. 56. (»ravna i/ili kosa«) i čl. 39., 56., 72. i 75. (»krovište može biti ravno ili koso nagiba …«) imaju drukčiji tekst za druge vrste građevina, a v2.1 ih ne prihvaća.

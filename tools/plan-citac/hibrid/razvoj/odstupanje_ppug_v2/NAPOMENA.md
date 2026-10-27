# Odstupanje od protokola: generator v2, PPUG Krk (prvi pokušaj)

- Generator je trebao raditi bez alata. Umjesto toga je koristio alate (8 poziva): prepisao je dani tekst u datoteku, napisao Python skripte (h.py, a1–a3.py) i kandidate stvorio predloškom.
- Razlog koji je naveo: izlaz od 270 kandidata (oko 224 KB) nije stao u jedan odgovor.
- Skripte čitaju samo `tekst.txt`. On je bajt po bajt jednak `hibrid/razvoj/ppug_krk.txt`. Skripte nisu čitale oznake ni izlaze v2.6.
- Izlaz se koristi samo za dijagnostiku provjere. Nakon ispravaka provjere: semantički 19 točnih i 0 pogrešno prihvaćenih. Prije ispravaka: 13 pogrešno prihvaćenih (točka alineje, nepotpun uvjet uvoda, nezapisan »za sve tipove gradnje«).
- Ispravni izlaz za PPUG Krk dobiva se iz četiri izolirana poziva bez alata (dijelovi A–D).

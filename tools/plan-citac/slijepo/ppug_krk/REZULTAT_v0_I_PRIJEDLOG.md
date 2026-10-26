# PPUG Krk čl. 22. i 23.: početni slijepi test (v0) i prijedlog proširenja

**Izvor:** `ppug_krk_sn_2020_29.html`, SHA-256 `f67ac384…`, 2.096.745 bajta, Windows-1250. Korišten je dio 1 dokumenta (pročišćeni tekst PPUG-a, čl. 4.–173.). Dio 2 (UPU 1 – Krk) nije korišten.

## Rezultat v0 (obrasci UPU-a 2, bez ikakvih dodataka)
| | čl. 22. | čl. 23. |
|---|---|---|
| prepoznata pravila | 0 | 0 |
| za pregled | 0 | 0 |
| pogrešna pravila | 0 | 0 |
| ishod članka | odbijen: vrsta građevine iz uvoda nije prepoznata; struktura nije u poznatom obliku | isto |
| brojčanih vrijednosti u tekstu (brojanje brojeva, ne ručne oznake) | 22 | 21 |

Propuštena pravila ne mogu se točno izbrojiti bez neovisnih oznaka. Gornja granica su sve brojčane vrijednosti: 43, sve propuštene.

## Zašto ništa nije prepoznato
1. **Uvodna rečenica je drukčija:** »Utvrđuju se slijedeće granične vrijednosti za izgradnju obiteljske kuće:« umjesto »Utvrđuju se uvjeti gradnje …:«. Vrsta građevine u uvodu ne nosi oblik (slobodnostojeća, dvojna).
2. **Druga struktura:** stavci »(1)«, »(2)« iznad točaka. Točke a)–i) su rečenice bez alineja, a alineje »- za slobodnostojeće građevine: 500 m²« daju vrijednost po obliku građevine.
3. **Drugi rječnik:** »najmanja dopuštena površina tlocrtne projekcije«, »koeficijent iskoristivosti (kis) nadzemnih etaža«, »ukoliko se ispod … gradi podrum … kis«, »visina od najniže kote konačno zaravnatog terena«, »granica građevne čestice«, »registrirane i evidentirane povijesne graditeljske cjeline«, »samostojeća« (uz »slobodnostojeća«), »uz uvjet da«.
4. **Čitač:** eksponent iz HTML-a (`<sup>2</sup>`) ostaje »m 2«, a pojavljuje se i »400m²« bez razmaka. Brojevi to već prepoznaju, ali tekst dokaza nije ujednačen.

## Prijedlog proširenja (nije provedeno)
Umjesto novih obrazaca cijelih rečenica, za generalizaciju na druge planove predlažem **gramatiku odredbe s rječnikom**:
- **Razine:** članak → stavak »(n)« → točka »x)« → alineja »- …«. Točka bez alineja je sama po sebi odredba.
- **Odredba:** `[najmanja|najveća|najveći] [dopušten(a|i)] <PARAMETAR> [<VRSTA>] (iznosi|je|može iznositi)[:] <VRIJEDNOST>`, ili popis alineja `- za <OBLIK>: <VRIJEDNOST>`.
- **Rječnik parametara s doslovnim izrazima:** npr. »površina građevne čestice« → minC; »površina tlocrtne projekcije« + najmanja/najveća → tlMin/tlMax; »koeficijent izgrađenosti (kig)« → kig.
  - »kis nadzemnih etaža« → `kisNadzemni`;
  - »kis« uz »ako se gradi podrum« → `kisPodrum` (UVJETNO, preduvjet PODRUM);
  - ti parametri se ne spajaju s općim »kis« iz UPU-a 2.
- **Oblik građevine iz alineje:** »za slobodnostojeće« → slob; »za dvojne i ugrađene« → dvoj + ugr; »za dvojne« → dvoj. Spaja se s vrstom iz uvoda (obiteljska, višeobiteljska).
- **Iznimke:** »iznimno …«, »uz uvjet da …«. Novi preduvjeti, svaki s doslovnim dokazom:
  - `OKRUZENJE_FORMIRANO` (»u okruženju već formiranih građevinskih čestica«);
  - `ZONA_POVIJESNA_CJELINA` (»unutar registriranih i evidentiranih povijesnih graditeljskih cjelina«). To nije isto što i ZONA_KPC iz UPU-a 2 i ne spaja se s njom.
- **Ostaje za pregled, bez tumačenja:**
  - »najmanja udaljenost od granice građevne čestice« (međa, ili i regulacijski pravac?);
  - »visina od najniže kote konačno zaravnatog terena« (drukčija točka mjerenja od UPU-a 2);
  - »samostojeće« kao sinonim za »slobodnostojeće«;
  - alineja s dvije iznimne vrijednosti (3,0 m od granice i 5,0 m od regulacijskog pravca u istoj alineji).

## Redoslijed
1. Neovisne oznake čl. 22. i 23. (`ppug_cl22_23_izvorni_tekst.txt` je izvorni tekst bez oznaka). Treba ih napraviti drugi označivač, jer je autor modula tekst PPUG-a već vidio pri ranijem upisu pravila.
2. Provedba gramatike iz prijedloga, uz zaključan v0 test.
3. Ocjena prema neovisnim oznakama (`ocijeni.py`) i ponovni test UPU-a 2 (PDF i pdftotext): broj pogrešnih ondje mora ostati 0.

# Posrednik prema OSS-u (upisana površina čestice)

Aplikacija iz preglednika ne može izravno čitati OSS (`oss.uredjenazemlja.hr`): OSS ne dopušta upite s drugih stranica (CORS), što je provjereno 19. 10. 2026. testnom stranicom („Failed to fetch”), dok isti upit otvoren izravno u pregledniku radi.

Zato mali Cloudflare Worker (`worker.js`) za zadani `CESTICA_ID` (`?id=`) ili za točku (`?lat=&lon=`, za Zagreb, gdje gradski sloj čestica nema DGU-ov ID) pita OSS i vraća **samo**:

- `zk[]` – ZK čestice povezane s katastarskom česticom: broj, **upisana površina**, ZK uložak, glavna knjiga, ZK odjel;
- `katastar` – površina iz posjedovnog lista;
- `dijelovi[]` – dijelovi čestice (npr. kuća, dvorište) s površinama.
- `graficka` – samo za upit po točki: grafička površina iz OSS-ovog sloja čestica (WMS GetFeatureInfo `oss:BZP_CESTICE`, isti sloj koji OSS koristi kad se klikne na kartu; ne traži ključ, provjereno 19. 10. 2026.).

Imena, adrese i udjeli posjednika i vlasnika se **ne prosljeđuju**. Odgovor se pamti 24 sata (Cloudflare cache). Posrednik ne ponavlja upite; aplikacija nakon greške pokuša još jednom nakon 3 s, da OSS ne dobiva niz upita.

`CESTICA_ID` je isti broj koji je u katastarskim podacima uz aplikaciju (`data/kat_krk`, prvo polje zapisa); provjereno na čestici 735/58 k.o. Kornić (19311109).

## Ograničenja

- `/oss/public/cad/parcel-info` nije službeno dokumentirano sučelje; OSS ga može promijeniti bez najave. Tada aplikacija prikazuje „OSS: podaci nisu dostupni” i nudi ručni unos ili PDF izvatka.
- Podaci su neslužbeni (kao javni uvid na OSS-u); mjerodavan je izvadak iz zemljišne knjige.
- Besplatni Cloudflare Workers plan: 100.000 upita dnevno po računu (dijeli se s drugim Workerima/Pages Functions na istom računu).

## Postavljanje (Cloudflare nadzorna ploča)

1. Cloudflare → **Workers & Pages** → **Create** → **Create Worker**.
2. Ime: `cestica-oss` → **Deploy**.
3. **Edit code** → obriši primjer, zalijepi cijeli `worker.js` → **Deploy**.
4. Adresa Workera je oblika `https://cestica-oss.<tvoj-podracun>.workers.dev/`.
5. Provjera: otvori `https://cestica-oss.<tvoj-podracun>.workers.dev/?id=19311109` – treba vratiti JSON s `"povrsina":642` (bez imena).

Worker ne dira postojeće stranice ni DNS na računu. Ne trebaju tajni ključevi.

Adresa se upisuje u `src/app.template.html` (`SRC_KRK.oss`). Prazna adresa isključuje dohvat.

## Test bez mreže

```
node tools/oss-posrednik/test.mjs
```

`primjer.xml` je skraćeni odgovor OSS-a s **izmišljenim** imenima, za provjeru da se osobni podaci ne prosljeđuju.

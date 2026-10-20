# Prijedlog: status tereta i plombe preko OSS posrednika

**Status: prijedlog za odobrenje. `worker.js` nije mijenjan ni objavljen.**

## Cilj

Uz upisanu površinu posrednik bi vraćao samo dva statusa, bez ikakvih osobnih podataka:

- `teretiUpisa`: broj upisa u C listu (teretovnici). `0` znači da upisa nema, `null` da podatak nije poznat.
- `plomba`: ima li na ulošku plombu (upis u tijeku): `true`, `false` ili `null`.

Aplikacija to ne smije prikazati kao potvrdu da je vlasništvo pravno čisto. Prikaz:

- „C list: nema upisa (javni uvid OSS, datum)” ili „C list: 2 upisa”;
- uvijek uz rečenicu: „To nije potvrda pravnog stanja. Mjerodavan je zemljišnoknjižni izvadak.”

Oznaka pouzdanosti:

- **A**: za sam podatak iz javnog uvida, s datumom i obuhvatom „javni uvid; mjerodavan je ZK izvadak”;
- **C**: kad podatak nije dostupan.

## Što još ne znamo

`parcel-info`, koji posrednik danas čita, nema podatke o teretima ni plombama. Za to treba drugi OSS upit:

```
/oss/public/lr/lr-unit?lrUnitNumber=<uložak>&mainBookId=<glavna knjiga>&historicalOverview=false
```

Taj upit koristi i `oss-test.html`. Struktura odgovora nije provjerena, ni naziv polja za plombu ni oblik C lista. Bez stvarnog primjera kod se ne piše. Polja se ne izmišljaju.

**Potrebno od tebe:** pokreni `oss-test.html` na probnoj stranici za jednu česticu i pošalji mi rezultat. Stranica skriva imena, adrese i OIB-e, ali tekst upisa u C listu može sadržavati ime vjerovnika ili druge osobe. Prije slanja provjeri i po potrebi obriši takav tekst. Za izradu trebam samo nazive polja i strukturu.

## Sigurnosne izmjene u prijedlogu

1. **Samo dopušteni izlaz.** Nova funkcija `sazmiUlozak()` iz odgovora uzima samo:
   - broj stavki C lista;
   - logičku oznaku plombe;
   - datum stanja.

   Nijedan tekst upisa, ime, adresa, udio ni iznos ne izlazi iz Workera. Odgovor se ne prosljeđuje u cijelosti nikad, ni u slučaju greške.
2. **Bez logova.**
   - U kodu nema `console.log`; to vrijedi i danas.
   - Odgovor OSS-a, puni ZK izvadak i parametri se ne zapisuju nigdje.
   - U Cloudflareu je preporuka da *Workers Logs / Observability* i *Logpush* ostanu isključeni za `cestica-oss`. Provjerava se u postavkama Workera; ja to ne mogu vidjeti.
   - Cloudflareova osnovna analitika i dalje bilježi broj upita i adresu (ID čestice). To nije osobni podatak o vlasniku.
3. **Cache samo sažetka.** U cache (24 h) ide isključivo sažeti objekt s brojevima i oznakama, kao i danas za površine. Sirovi odgovor se ne sprema.
4. **Provjera ulaza.**
   - `lrUnitNumber` i `mainBookId` smiju biti samo brojevi (do 12 znamenki).
   - Uložak se uzima iz `parcel-info` iste čestice, ne iz upita korisnika. Tako se posrednik ne može koristiti za pretragu proizvoljnih uložaka.
5. **Isti izvori i isti broj upita prema OSS-u.**
   - Odgovor smije primiti samo `https://ozrenpancic-maker.github.io`.
   - Posrednik ne ponavlja upite.
   - Upit za uložak radi se samo kad aplikacija izričito traži status (`?id=…&ulozak=1`), ne pri svakom dohvatu površine.
6. **Napomena u svakom odgovoru:** `"napomena": "Javni uvid OSS-a; ne potvrđuje pravno stanje. Mjerodavan je ZK izvadak."`
7. **Test bez mreže.** U `test.mjs` dodaje se primjer s *izmišljenim* imenima u C listu i plombi. Test provjerava da ni jedno ime ni tekst upisa ne izađe iz Workera.

## Redoslijed

1. Ti pošalješ primjer odgovora `lr-unit` (bez osobnih podataka).
2. Ja napišem izmjenu kao zasebnu datoteku (`worker.next.js`) s testovima. `worker.js` ostaje kakav jest.
3. Ti pregledaš i odobriš.
4. Ti objaviš Worker u Cloudflareu. Tek tada aplikacija dobiva prikaz statusa, isprva samo na probnoj stranici.

## Proširenje (20. 10. 2026.): sva četiri dijela uloška

Ozren je tražio prikaz posjedovnice I i II, vlastovnice i teretovnice i odabrao opseg „struktura + tekst tereta”.

| Dio | Što posrednik vraća | Što ne vraća |
| --- | --- | --- |
| Posjedovnica I (A I) | čestice u ulošku: broj, k.o., način uporabe, površina | — |
| Posjedovnica II (A II) | redni broj, datum i broj zaprimanja, puni tekst upisa (npr. zabilježba legalizacije) | — |
| Vlastovnica (B) | broj vlasnika, udio svakog (1/2, 1/4 …), vrsta (fizička ili pravna osoba, ako OSS to razlikuje) | imena, OIB, adrese, datum rođenja |
| Teretovnica (C) | redni broj, vrsta upisa, datum i broj zaprimanja, puni tekst upisa; plomba | OIB (u tekstu se 11 znamenki zamjenjuje s „[OIB]”) |

- Tekst upisa u A II i C može sadržavati ime vjerovnika ili druge osobe; to je izričit izbor korisnika. Aplikacija ga prikazuje samo na zaslonu i u izvještaju; posrednik ga ne sprema (cache 24 h samo za odgovor bez B imena) i ne zapisuje u logove.
- Uz prikaz uvijek piše: „Javni uvid OSS-a; nije službeni izvadak i ne potvrđuje pravno stanje. Mjerodavan je ZK izvadak.”
- Nazivi polja i dalje se ne izmišljaju: za izradu treba uzorak odgovora `lr-unit`. Uzorak bez osobnih podataka pravi stranica `oss-uzorak.html` na probnoj adresi (sve u pregledniku, svaki tekst zamijenjen duljinom).
- Redoslijed ostaje: uzorak → `worker.next.js` s testovima → Ozren pregleda i odobri → Ozren objavi Worker.

## Stanje 20. 10. 2026.

- Prvi uzorak `lr-unit` (uložak 2305, k.o. Granešina Nova) potvrdio je strukturu: `possessionSheetA1.cadParcels`, `ownershipSheetB.lrUnitShares[].lrOwners`, `possessionSheetA2.lrEntries`, `encumbranceSheetC.lrEntryGroups`, `activePlumbs`.
- Napisan je `worker.next.js` (nije objavljen) s testom `test.next.mjs`: A I u cijelosti; B samo broj udjela i vlasnika te opis udjela (OIB maskiran); plomba i broj plombi; za A II, B i C upise zasad samo broj.
- U uzorku su A II, B upisi i C bili prazni, pa polja pojedinog upisa još nisu poznata. Za tekst upisa treba drugi uzorak, s česticom koja ima upis u posjedovnici II i u teretovnici.

## Stanje nakon drugog uzorka (20. 10. 2026.)

- Drugi uzorak (uložak s upisima u A II, B i C) potvrdio je oblik upisa: `{description, lrEntryId, orderNumber}`. A I može biti u `lrParcels` (umjesto `cadParcels`). C upisi su u `lrEntryGroups[].lrEntries[]` i mogu imati `lrOwners` (ovlaštenike), a vlasnik u B ima `lrEntry` (upis stjecanja). Postoji i `lastDiaryNumber`.
- `worker.next.js` sada vraća:
  - A I u cijelosti;
  - A II i C s punim tekstom (OIB zamijenjen s „[OIB]”) i brojem ovlaštenika, bez njihovih imena, adresa i OIB-a kao polja;
  - za B broj vlasnika, opise udjela i broj upisa, bez teksta (sadrži imena);
  - plombu i zadnji broj dnevnika.
- Test: `node tools/oss-posrednik/test.next.mjs`.
- Aplikacija već šalje `&ulozak=1`. Sadašnji Worker taj parametar zanemaruje, pa se ništa ne mijenja dok se ne objavi nova verzija. Nakon objave u „Vlasnici i tereti (ZK izvadak)” prikazuje se sažetak uloška, a ulazi i u PDF izvještaj.
- **Za objavu (Ozren):** pregledaj `worker.next.js`, kopiraj ga preko `worker.js` u Cloudflareu (Workers → cestica-oss → Edit code → Deploy) i provjeri da su Workers Logs i Logpush isključeni.


## 20. 10. 2026.: OSS povremeno odbija (403)
- Zaglavlja kao OSS-ova stranica (Accept-Language, Referer, Origin), User-Agent „Mozilla/5.0 (compatible; CesticaHR/1.0; +…)”.
- Jedan ponovni pokušaj u posredniku nakon 0,9–1,8 s kad OSS vrati 403, 429 ili 5xx (najviše dva upita po koraku).
- Sažetak uloška pamti se 24 h po glavnoj knjizi i broju uloška (više čestica u istom ulošku → jedan upit).
- Dijagnostika: `oss-dijag.html` na probnoj stranici (12 čestica oko točke, jedna po jedna).

## 20. 10. 2026. (navečer): OSS ograničava broj upita
- Metrika Workera: prema oss.uredjenazemlja.hr 160 odgovora 2xx i 374 odgovora 4xx u 24 h; korisnik: „pokaže par puta za redom i onda više neće” → ograničenje broja upita.
- Posrednik više ne ponavlja upit nakon 403/429; nakon odbijanja 90 s ne šalje upite OSS-u (odgovor 503, `blok: true`), da se odbijanje ne produžuje.
- U poruci greške: status, zaglavlje `Server` i vrsta odgovora OSS-a (bez sadržaja), za dijagnostiku.
- Predmemorija čestice i uloška 3 dana (aplikacija prikazuje datum dohvata); ulošci jedne čestice jedan po jedan.
- Aplikacija ne ponavlja automatski kad OSS odbija; ostaje gumb „Pokušaj ponovno”.

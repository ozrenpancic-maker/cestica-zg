# Cijene zemljišta u općini

Stanje 24. 10. 2026., grana `razvoj`.

## Izvor

- Ministarstvo prostornoga uređenja, graditeljstva i državne imovine i Ekonomski institut, Zagreb: „Pregled tržišta nekretnina Republike Hrvatske 2025”, prilozi.
- Objavljeno 30. 4. 2026. Datoteka: https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Prilozi_PTN2025.zip
- Korištene datoteke iz priloga:
  - „Medijalne cijene po m2 po jedinicama lokalne samouprave od 2012. do 2025. godine.xlsx”, listovi „Građevinska zemljišta EUR” i „Poljoprivredna zemljišta EUR”;
  - „Broj kupoprodajnih transakcija nekretnina po jedinicama lokalne samouprave od 2012. do 2025. godine .xlsx”, listovi „Građevinska zemljišta” i „Poljoprivredna zemljišta”.
- Izvor ne navodi licencu. Podaci su prikazani s punim navodom izvora.
- Pretvorba: `python3 tools/ptn/pripremi.py <mapa s raspakiranim prilozima> data/ptn/ptn2025.json`. Rezultat su 556 gradova i općina (145 KB), bez ikakve dopune.
  - „z” znači manje od 10 kupoprodaja (podatak nije objavljen zbog privatnosti); `null` znači da kupoprodaja nije bilo.
  - U broju kupoprodaja poljoprivrednog zemljišta izvor 48 puta ima „z9”, što se čita kao „z”.
  - Od 2023. medijani su u cijelim eurima.
  - Broj kupoprodaja za 2017. u izvoru je neuobičajeno malen (npr. Zagreb 14, Krk 11); prikazuje se kako je objavljen.

## Grad ili općina čestice

- **Krk i PGŽ:** iz sloja namjene PGŽ (`OPCINA_GRAD`), odnosno iz evidencije planova.
- **Zagreb:** Grad Zagreb.
- **Ostatak Hrvatske:** iz adrese u OpenStreetMapu (Nominatim reverse, jednom po čestici). Isto ime u više županija razlikuje se prema županiji.
- **Ručni odabir:** uvijek je moguć i pamti se po čestici (`localStorage` `ptnJls`).

## Prikaz

**Odjeljak „Cijene zemljišta u općini”** (kategorija € Troškovi i investicija, samo napredni način):
- medijan građevinskog zemljišta za zadnju objavljenu godinu i broj kupoprodaja; ako 2025. nije objavljena, piše zašto;
- raspon medijana 2023.–2025.;
- orijentacijski iznos: grafička površina × raspon. Piše da to nije procjena ove čestice;
- poljoprivredno zemljište, za dio čestice izvan građevinskog područja;
- grafikon medijana 2012.–2025., s prazninama gdje podatak nije objavljen;
- tražena cijena iz oglasa: €/m², položaj prema rasponu (ispod, unutar, iznad) i % prema medijanu.

**Sažetak** (i u osnovnom načinu), redak „Koliko vrijedi zemljište?”:
- medijan za grad ili općinu, uz napomenu da vrijedi za cijeli grad ili općinu, a ne za ovu česticu;
- u Zagrebu i na Krku dodan je uz postojeće usporedbe korisnika.

**Pouzdanost C:** medijan cijelog grada ili općine ne uzima u obzir položaj, pogled, pristup, opremljenost, veličinu ni namjenu. Nema izmišljenih korekcija. Za stvarnu vrijednost: usporedive prodaje (eNekretnine) ili ovlašteni procjenitelj.

## Testovi

`tests/run.js`, skupina `ptnTests`. Provjerava:
- Zagreb: medijan i broj kupoprodaja, raspon, iznos za površinu, grafikon, pouzdanost C;
- traženu cijenu i redak u sažetku;
- grad iz adrese, s istim imenom u dvije županije;
- ručni odabir;
- zadnju objavljenu godinu kad za 2025. ima manje od 10 kupoprodaja.

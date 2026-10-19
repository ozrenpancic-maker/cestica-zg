# Uvoz baze urbanističkih pravila (ČesticaHR Data Manager)

Baza se uvozi kao jedna JSON datoteka. Prije ugradnje provjerava je `tools/baza/provjeri.py`. Ako provjera javi grešku, `build.py` staje i ništa se ne objavljuje.

```
python3 tools/baza/provjeri.py izvoz.json            # provjera i sažetak
python3 tools/baza/provjeri.py izvoz.json --uvezi    # nakon provjere kopira u src/baza/baza.json
python3 build.py                                     # ugrađuje bazu u aplikaciju (ponovno je provjerava)
```

Bez `src/baza/baza.json` aplikacija radi kao i dosad. Odjeljak „Uvjeti iz baze ČesticaHR” pojavljuje se tek kad je baza uvezena. Postojeći, ručno provjereni uvjeti gradnje (GUP Zagreb, PPUG Krk, UPU-i) ostaju. Baza ih ne zamjenjuje bez posebne odluke.

Primjer formata nalazi se u `tools/baza/primjer_baza.json`. Izrađen je iz pravila PPUG-a Grada Krka koja su već ručno provjerena u aplikaciji. Jedno pravilo u njemu namjerno je označeno kao kandidat, da se vidi kako se kandidati prikazuju.

## Načela

1. **Dvije razine.**
   - `pravni_status.razina = "potvrđeno"`: pravilo je pravno provjereno.
   - `pravni_status.razina = "kandidat"`: pravilo je automatski izdvojeno i nije potvrđeno. Kandidati se prikazuju odvojeno („Istraživački kandidati, nepotvrđeno”) i nikad ne ulaze u izračun.
2. **Potvrđeno pravilo mora imati sve od navedenog. Inače se uvoz odbija.**
   - službeni izvor: `odluka_id` koji pokazuje na odluku s `url`;
   - `clanak`;
   - `citat` iz odluke;
   - `pravni_status.datum_provjere` (GGGG-MM-DD);
   - `status_vazenja` plana;
   - `primjenjivost.zone`;
   - `primjenjivost.vrste_gradnje`.

   Aplikacija istu provjeru radi i sama. Nepotpuno „potvrđeno” pravilo prikazuje kao kandidata i navodi što mu nedostaje.
3. **Pravni status i GIS primjenjivost su odvojeni.**
   - `pravni_status` kaže je li pravilo točno preneseno iz važeće odluke.
   - `gis_status` kaže je li potvrđeno da oznaka zone u GIS sloju odgovara zoni iz pravila, tj. da se pravilo može automatski primijeniti na česticu.
   - U izračun ulazi samo pravilo koje je pravno potvrđeno, GIS potvrđeno, iz plana sa statusom „važeći”, i koje odgovara odabranoj vrsti i načinu gradnje.
4. **Više planova istovremeno.**
   - Prikazuju se svi planovi čiji obuhvat i zone odgovaraju lokaciji: PPUG/PPUO, GUP, UPU i posebna ograničenja (`vrsta: "posebno"`).
   - Aplikacija ne pretpostavlja koji ima prednost.
   - Ako dva plana za isti parametar daju različite vrijednosti, prikazuje se upozorenje i taj se parametar ne koristi u izračunu.
5. **Površina u izračunu.**
   - Svaki izračun navodi korištenu površinu i izvor: grafička, upisana u katastru ili upisana u zemljišnoj knjizi.
   - Površinu korisnik bira u „Izračunu za ovu česticu”.

## Struktura

```json
{
  "verzija_sheme": "1.0",
  "izvor": "ČesticaHR Data Manager",
  "verzija_izvora": "2.0",
  "izvezeno": "2026-10-20",
  "planovi": [
    {
      "id": "PPUG-KRK",
      "naziv": "Prostorni plan uređenja Grada Krka",
      "vrsta": "PPUG",
      "jls": "Grad Krk",
      "obuhvat": {
        "jls": ["Grad Krk"],
        "opis": "cijelo područje Grada Krka",
        "gis": { "status": "potvrđeno", "sloj": "PGŽ NAMJENA_POVRSINA_NOVO" }
      },
      "status_vazenja": "važeći",
      "odluke": [
        {
          "id": "PPUG-KRK-2020-PT",
          "naziv": "…",
          "vrsta": "pročišćeni tekst",
          "glasilo": "Službene novine PGŽ",
          "broj": "29/2020",
          "datum": "GGGG-MM-DD",
          "url": "https://…"
        }
      ]
    }
  ],
  "pravila": [
    {
      "id": "PPUG-KRK-obit-kig",
      "plan_id": "PPUG-KRK",
      "odluka_id": "PPUG-KRK-2020-PT",
      "vrsta": "uvjet",
      "parametar": "kig",
      "vrijednost": 0.25,
      "jedinica": "",
      "operator": "max",
      "uvjet": "neobavezno: dodatni uvjet iz teksta",
      "clanak": "22",
      "stavak": "neobavezno",
      "citat": "…izvorni tekst…",
      "primjenjivost": {
        "zone": ["GPN-*", "NA*"],
        "izgradenost": ["izgrađeno"],
        "vrste_gradnje": ["obiteljska kuća"],
        "nacin_gradnje": ["slobodnostojeća"],
        "zahvat": ["nova gradnja"]
      },
      "pravni_status": {
        "razina": "potvrđeno",
        "datum_provjere": "2026-10-18",
        "provjerio": "…",
        "metoda": "ručno",
        "vazi_od": "…",
        "vazi_do": "…"
      },
      "gis_status": {
        "razina": "potvrđeno",
        "sloj": "…",
        "atribut": "…",
        "datum_provjere": "…",
        "napomena": "…"
      },
      "izmjena_od": "id pravila koje ovo mijenja (neobavezno)",
      "napomena": "…"
    }
  ]
}
```

### Dopuštene vrijednosti

| Polje | Vrijednosti |
|---|---|
| `planovi[].vrsta` | PPŽ, PPUG, PPUO, GUP, UPU, DPU, PPPPO, posebno, ostalo |
| `status_vazenja` | važeći, u izradi, van snage, privremena mjera |
| `odluke[].vrsta` | donošenje, izmjene i dopune, pročišćeni tekst, odluka o izradi, ostalo |
| `parametar` | min_cestica, max_cestica, kig, kis, kis_nadzemni, kis_podzemni, tlocrt_min, tlocrt_max, gbp_max, visina, etaze, udaljenost_meda, udaljenost_regulacija, zelenilo, parkiranje, zabrana_gradnje, ostalo |
| `pravni_status.razina` | potvrđeno, kandidat |
| `gis_status.razina`, `obuhvat.gis.status` | potvrđeno, kandidat, nema |

### Kako se pravilo veže uz česticu

- **`obuhvat.jls`:**
  - Na Krku je to naziv jedinice iz županijskog sloja, npr. „Grad Krk” ili „Općina Baška”.
  - U Zagrebu je to „Grad Zagreb”.
- **`primjenjivost.zone`:** oznake iz GIS sloja koje aplikacija čita na lokaciji.
  - **Krk:** `OZNAKA_NAMJENE` iz sloja PGŽ, npr. GPN-1, NA2.
  - **Zagreb:**
    - oznaka urbanog pravila, npr. 2.2.;
    - oznaka plana: GUP, GUP Sesvete ili PPGZ;
    - namjena iz GUP-a (`Analitika`).
  - **Zamjenski znakovi:**
    - `*` na kraju znači „počinje s”, npr. `GPN-*`;
    - samo `*` ili `sve` znači cijeli obuhvat.
  - **Usporedba:** oznaka se uspoređuje u cijelosti, bez razlike velikih i malih slova i dijakritika. Zato „izgrađeno” ne odgovara „neizgrađeno”.
- **`izgradenost`:** samo Krk, vrijednost `IZGRADJENOST` iz sloja PGŽ.
- **`vrste_gradnje` i `nacin_gradnje`:** uspoređuju se s vrstom i načinom gradnje koje korisnik izabere u aplikaciji.
  - Na Krku su to nazivi tipova iz pravila, npr. „Obiteljska kuća”, i način gradnje (slobodnostojeća, dvojna, ugrađena).
  - U Zagrebu je to tip kuće (slobodnostojeća, poluugrađena (dvojna), ugrađena (u nizu)).

### Izračun iz baze

| Parametar | Kako se koristi |
|---|---|
| `min_cestica` | provjera |
| `kig` | najveći tlocrt = površina × kig; ako je zadan, ograničen s `tlocrt_max` |
| `kis_nadzemni` (ako ga nema, `kis`) | najveći GBP = površina × kis; ako je zadan, ograničen s `gbp_max` |
| ostali parametri | samo se prikazuju |

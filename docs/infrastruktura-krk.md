# Komunalna infrastruktura za otok Krk (DGU SKI, Primorsko-goranska županija)

Stanje 19. 10. 2026., grana `razvoj`. Zagreb nije mijenjan (`data/ski/` je isti).

## Izvor

INSPIRE GML datoteke s `ski.dgu.hr` za Primorsko-goransku županiju (oznaka `_08`), preuzete 18. 10. 2026.:

| Mreža | Datoteka | Veličina ZIP-a | Stanje podataka (zaglavlje GML-a) |
|---|---|---|---|
| Vodovod | `INSPIRE_WaterNetwork_(US-NET-WA)_08.zip` | 13,1 MB | 16. 7. 2024. |
| Kanalizacija | `INSPIRE_SewerNetwork_(US-NET-SW)_08.zip` | 7,4 MB | 17. 7. 2024. |
| Struja | `INSPIRE_ElectricityNetwork_(US-NET-EL)_08.zip` | 26,7 MB | 3. 10. 2026. |

ATOM popis na DGU-u za struju navodi 16 kB, ali preuzeta datoteka ima 26,7 MB i noviji datum; popis je zastario.
Licenca prema registru NIPP: otvorena dozvola (data.gov.hr), uz navođenje izvora.

Slojevi preglednika `ski.dgu.hr/gis` (`hrki_ws:…`, uključujući telekomunikacije i plinovode) traže prijavu, pa se u javnoj aplikaciji ne koriste. Javni INSPIRE WMS daje samo sliku i tekstualne podatke bez geometrije; udaljenosti se iz slike ne računaju.

## Sadržaj za otok Krk

Obuhvat: otok bez kopna (crta kroz Vinodolski kanal) i bez istočne obale Cresa (`u_krk` u `tools/ski/pripremi_kvadrate.py`).

| Mreža | Funkcionalni vodovi | Duljina | Kvadrati | Napomena |
|---|---|---|---|---|
| Vodovod | 21.914 | 582 km | 239 | cijeli otok |
| Kanalizacija | 12.665 | 305 km | 102 | samo veća naselja (manja mjesta imaju sabirne jame) |
| Struja, niski napon | 15.045 | 629 km | 186 | većina naselja; srednji i visoki napon nisu uključeni |

Promjer i vrsta cijevi uskraćeni su („Withheld”), kao i u Zagrebu. Napušteni i neaktivni vodovi su isključeni.
Datoteke: `data/ski_krk/` (528 datoteka, 5,1 MB, oko 1,2 MB komprimirano).

## Provjera točnosti (`tools/ski/provjeri_krk.py`, rezultat `tools/ski/provjera-krk-rezultat.json`)

| | Vodovod | Kanalizacija | Struja (NN) |
|---|---|---|---|
| Udaljenost iz kvadrata naspram izvornih geometrija, najviše | 0,29 m | 0,26 m | 0,24 m |
| Točke bez voda u 500 m: slaže se | 232/232 | 276/276 | 269/269 |
| Objekti na mreži do svog voda, medijan | 0,00 m | 0,00 m | 0,24 m |
| … 90 % | 0,01 m | 0,00 m | 149 m |

Kod struje velik dio objekata (trafostanice, stupovi) pripada srednjem i visokom naponu, koji nisu u kvadratima, pa su daleko od niskonaponskih vodova; to nije greška položaja.

## Prikaz u aplikaciji (analiza Krka)

- Vodovod, kanalizacija, struja: „najbliži evidentirani vod: X m”, od granice čestice, u krugu od 500 m (isti izračun kao u Zagrebu).
- Bez voda u krugu: „Podaci nisu dostupni” (u krugu od 500 m nema evidentiranog voda); greška učitavanja: „Podaci nisu dostupni” uz razlog. Nikad 0 m zbog greške.
- Telekomunikacije i plin: „Podaci nisu dostupni”.
- Karta: sloj „Najbliži vodovi (DGU)” s bojama (plavo vodovod, smeđe kanalizacija, crveno struja); klik na vod pokazuje udaljenost, izvor i stanje podataka.
- Napomene: evidencija može biti nepotpuna; priključak i trošak potvrđuju Ponikve i HEP ODS; niskonaponski vod može biti kabel javne rasvjete.

## Priprema iznova

```
python3 tools/ski/pripremi_kvadrate.py --podrucje krk --vodovod-link WA/UtilityLink.gml --vodovod-pipe WA/WaterPipe.gml \
  --kanalizacija-link SW/UtilityLink.gml --kanalizacija-pipe SW/SewerPipe.gml \
  --struja-link EL/UtilityLink.gml --struja-pipe EL/ElectricityPipe.gml --datum 2026-10-18 \
  --stanje "vodovod=16. 7. 2024.;kanalizacija=17. 7. 2024.;struja=3. 10. 2026."
python3 tools/ski/provjeri_krk.py --vodovod WA --kanalizacija SW --struja EL
```

Isti postupak radi i za druga područja: dodaje se zapis u `PODRUCJA` (obuhvat i izlazna mapa).

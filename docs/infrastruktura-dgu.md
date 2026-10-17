# Komunalna infrastruktura: DGU INSPIRE / SKI izvori (provjera 17. 10. 2026.)

## Što postoji

Izvor: Sustav katastra infrastrukture (SKI), Državna geodetska uprava, Jedinstvena informacijska točka (JIT).
Glavni ATOM feed (`https://ski.dgu.hr/inspire/atom/xml`) ima četiri skupa:

| Mreža | ATOM feed | Datoteka za Grad Zagreb | Veličina | Ažurirano |
|---|---|---|---|---|
| Vodovod | `us-net-wa` | `INSPIRE_WaterNetwork_(US-NET-WA)_21.zip` | 12,9 MB | 19. 7. 2024. |
| Kanalizacija (odvodnja) | `us-net-sw` | `INSPIRE_SewerNetwork_(US-NET-SW)_21.zip` | 5,5 MB | 19. 7. 2024. |
| Električna mreža | `us-net-el` | `INSPIRE_ElectricityNetwork_(US-NET-EL)_21.zip` | 23,3 MB | 19. 7. 2024. |
| Toplovod | `us-net-th` | (po istom obrascu) | — | — |

Format: INSPIRE GML 3.2.1, zipano, koordinatni sustav ETRS89/LAEA (EPSG:3035). Datoteka 21 je Grad Zagreb. Feed navodi "nema ograničenja javnom pristupu", a NIPP navodi otvorenu dozvolu za ponovnu uporabu.

**Plin:** u ATOM preuzimanjima **nema** skupa za plin (US-NET-OG). Plin postoji samo kao sloj WMS servisa:

`https://ski.dgu.hr/inspire/wms` (WMS 1.3.0) ima slojeve `US.WaterNetwork`, `US.SewerNetwork`, `US.ElectricityNetwork`, `US.ThermalNetwork` i `US.OilGasChemicalsNetwork`. Svi su upitni (GetFeatureInfo, odgovor `text/plain` ili `text/html`) i podržavaju CRS:84 i EPSG:3765. Upotreba traži prihvaćanje uvjeta korištenja na `ski.dgu.hr/gis/startup`.

## Što NIJE provjereno i zašto

- **Stvarni sadržaj geometrija za Zagreb nije pregledan.** Moja radna okolina ne smije preuzimati datoteke s `ski.dgu.hr` (mrežna ograničenja okoline), a alat za čitanje web stranica ne otvara zip datoteke.
- **Potpunost:** Grad Zagreb na svojoj stranici navodi da vlasnici i upravitelji mreža "dostavljaju dio podataka o svojoj infrastrukturi". Nijedan izvor ne tvrdi da je katastar infrastrukture potpun, a metapodaci ne navode položajnu točnost.
- **Pristup iz preglednika (CORS):** nije poznato smije li aplikacija s GitHub Pagesa izravno pitati WMS. Zato je u "Stanje servisa" dodana provjera "DGU katastar infrastrukture (WMS…)". Ako je na tvom mobitelu zelena, preglednik može dohvatiti servis.

## Prijedlog integracije (nakon tvoje provjere, posebna faza)

1. **Ručna provjera kvalitete:** u pregledniku SKI (`ski.dgu.hr/gis`) otvori 3–5 čestica koje poznaješ (s poznatim priključcima). Provjeri jesu li ulični vodovi vodovoda, kanalizacije, NN struje i plina ucrtani i podudaraju li se sa stvarnim stanjem.
2. Ako su podaci upotrebljivi: upit **GetFeatureInfo** u krugu oko čestice za svaki sloj (pregledniku ili preko Workera ako CORS ne dopušta). Rezultat je samo "evidentiran vod u blizini (udaljenost, vrsta, upravitelj)", uz izvor i datum 19. 7. 2024.
3. Prikaz i AI moraju razlikovati:
   - **evidentiran vod na X m** (podatak iz katastra infrastrukture, može biti nepotpun);
   - **mogućnost priključenja**, koju potvrđuje samo distributer (ViO, HEP ODS, GPZ);
   - **nema podatka**, što ne znači da voda nema.
4. Za preuzimanje velikih GML datoteka u aplikaciju nema potrebe; dovoljan je upit oko čestice.

AI-2 radi i bez ovih podataka. Za ulične mreže zasad odgovara "nije dostupno" i upućuje na distributera.

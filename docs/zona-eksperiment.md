# EKSPERIMENT: kandidat detaljne zone (M11/M2) iz boje rastera UPU-a

Status: **eksperiment, isključen za korisnike**. Grana `eksperiment-zone`. Nema korisničkog prikaza.

## Što modul radi
`inferDetailedZone(ulaz)` (u kodu `ZONE_EXP.infer`) čita piksele izreza karte UPU-a unutar granice čestice i usporedi ih s uzorcima boja iz profila karte. Vraća samo jedan od šest statusa:

| Status | Značenje |
|---|---|
| `M11_CANDIDATE` / `M2_CANDIDATE` | boja jedne zone prevladava unutar čestice, a uz granicu nema druge zone |
| `MIXED_REVIEW` | na čestici su boje više zona |
| `EDGE_AMBIGUOUS` | unutrašnjost je jedne zone, ali uz granicu (± `rubMetara`) pojavljuje se druga zona |
| `LOW_CONFIDENCE` | premalo piksela, previše pozadine ili linija, boje ne odgovaraju uzorcima, pregruba karta ili za neku zonu nema uzoraka |
| `NO_DATA` | nema slike ili se ne može pročitati, kriva ili nepotpuna georeferencija, čestica izvan izreza, nema profila boja |

Svaki rezultat je nepromjenjiv objekt s `pravnoPotvrdeno:false`, `eksperiment:true`, razlogom, udjelima zona, brojem piksela i upozorenjima.

## Algoritam
1. **Provjera ulaza:** slika (RGBA, `width×height×4`), okvir u EPSG:3765 (`wkid 3765`), jednaka razlučivost po osima (±2 %), vraćeni okvir unutar `maxOdstupanjeOkviraPx` od traženog, granica čestice unutar izreza. Inače `NO_DATA`.
2. **Piksel → koordinata:** `px = (E − xmin)/res`, `py = (ymax − N)/res`, `res = (xmax − xmin)/W`. Granica čestice preračunava se iz WGS84 u HTRS96/TM funkcijom `tmFwd`.
3. **Pojasevi:** unutarnji pikseli (središte unutar čestice, udaljenost od granice ≥ `rubMetara`) i rubni pojas (± `rubMetara` s obje strane granice).
4. **Razvrstavanje piksela:** prvo se zanemaruju pozadina i tamne linije (`zanemari`), zatim se piksel dodjeljuje najbližem uzorku boje u RGB prostoru ako je unutar njegove tolerancije, inače je „nepoznat”.
5. **Odluka (`pragovi`):** najmanji broj piksela → najveći udio zanemarenih → najmanja pokrivenost → prevladavajuća zona (`dominantna`). Ako za neku zonu iz `zone` nema uzoraka, rezultat je `LOW_CONFIDENCE`. Ako rubni pojas ima više od `rubDrugaZona` druge zone, `EDGE_AMBIGUOUS`. Ako druga zona ima barem `mijesanaMin`, `MIXED_REVIEW`.

Zona bez uzorka nikad ne može biti kandidat (ništa se ne razvrstava u nju).

## Konfiguracija
`src/zone_exp.json`: popis statusa, zone, pragovi, pravila zanemarivanja i **profili** boja. `build.py` odbija gradnju ako je `ukljuceno` različit od `false`, ako se promijeni popis statusa ili ako profil sadrži česticu ili koordinate. Profil se veže uz list karte (`objectid`) ili uz plan i kartu, nikad uz česticu.

U aplikaciji **nema nijednog profila**. Privremeni testni profil za list 7104 (UPU 2 Kornić, karta 4) je u `tests/zone-exp/profil_upu2_k4_privremeni.json`. Uzorak M11 uzet je iz područja s oznakom M1₁ izvan čestice 735/76; nije iz legende. Uzorka za M2 nema.

## Sigurnost (izolacija)
- `ZONE_EXP_CFG.ukljuceno = false`. Ručno pokretanje (`ZONE_EXP.pokreni()`) radi samo uz razvojnu zastavicu `localStorage['cestica-dev-zone-exp']='1'` i rezultat samo vraća i ispisuje u konzolu.
- Modul ne poziva `pzSet`, `krkZonaSet`, `krkZastSet`, `renderKrk`, ne piše u `localStorage`, `RKAT` ni u podatke čestice. Ostatak aplikacije ga ne poziva. Testovi to provjeravaju i statički i usporedbom prikaza za 735/76 prije i poslije.

## Pristup slici (CORS)
- `export?f=json` iz PP_RASTERI aplikacija već čita iz preglednika (radi u produkciji), dakle REST odgovor JSON-a ima CORS dozvolu.
- Za čitanje piksela treba i dozvola za samu sliku (`href` iz `arcgisoutput` ili `export?f=image`). **Još nije provjereno uživo**: mreža razvojnog okruženja ne propušta `gisportal.pgz.hr`, a računalo korisnika nije bilo dostupno.
- Modul čita sliku `fetch(url,{mode:"cors",credentials:"omit"})` → `createImageBitmap` → `canvas.getImageData`. Ako preglednik odbije (CORS) ili je canvas zaštićen, vraća `NO_DATA` s razlogom. Zaštita se ne zaobilazi.

Provjera u pregledniku (konzola na stranici aplikacije):
```js
const u="https://gisportal.pgz.hr/server/rest/services/PP_RASTERI/PP_RASTERI/MapServer/export?bbox=351483.08,4990977.93,351663.08,4991157.93&bboxSR=3765&imageSR=3765&size=800,800&dpi=96&format=png&transparent=false&layers=show:5&layerDefs=%7B%225%22%3A%22OBJECTID%3D7104%22%7D&f=image";
fetch(u,{mode:"cors"}).then(r=>console.log("CORS dopušten", r.status, r.headers.get("content-type"))).catch(e=>console.log("CORS odbijen", e.message));
```

### Ako CORS blokira čitanje: prijedlog posrednika
Postojeći besplatni posrednik (Deno, `tools/oss-posrednik`) može dobiti rutu `?pgzraster=` koja:
- prima samo parametre `bbox`, `size` (najviše 800×800) i `objectid` lista; sloj je fiksno 5 ili 12, `f=image`, EPSG:3765;
- prosljeđuje upit samo na `gisportal.pgz.hr/.../PP_RASTERI/MapServer/export` (bez drugih adresa, bez kolačića i bez autentikacije);
- vraća PNG s `Access-Control-Allow-Origin` za ishodište aplikacije, uz ograničenje učestalosti i kratko predmemoriranje;
- ne mijenja sliku i ne zaobilazi nikakvu zaštitu; to je isti javni izvoz koji servis već nudi svima. Prije uključivanja treba provjeriti uvjete korištenja PGŽ geoportala.
Ruta nije napravljena dok se ne potvrdi da je potrebna i dopuštena.

## Što treba za kalibraciju M11/M2
1. Legenda karte 4 UPU-a 2 Kornić (SN PGŽ 19/2016) s bojama ili šrafurama za M1₁ i M2 te izrez iz istog servisa na kojem je potvrđena zona M2.
2. Uzorci boja iz servisa (ne iz PDF-a, jer se boje razlikuju), za svaku zonu barem nekoliko listova i područja, uz zapis izvora.
3. Provjera razlikuju li se M1₁ i M2 bojom ili samo oznakom (natpisom). Ako je boja ista, prepoznavanje bojom nije moguće i modul treba ostati na `LOW_CONFIDENCE`.
4. Skup čestica s poznatom zonom (iz lokacijske informacije), koji razvoj ne vidi, za slijepu provjeru pragova.

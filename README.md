# Čestica ZG

Mobilna web aplikacija: dodirneš zemljište u Zagrebu i dobiješ katastarsku česticu, namjenu iz prostornih planova, urbano pravilo GUP-a s uvjetima gradnje, provjere rizika (UPU, klizišta, zaštita, voda), pristup i okolinu, procjenu doprinosa, priključaka i cijene gradnje te popis dokumentacije s adresama ureda.

**Aplikacija:** https://ozrenpancic-maker.github.io/cestica-zg/

## Izvori podataka
- Grad Zagreb, ArcGIS servisi: katastarske čestice (2023.), planirana namjena, urbana pravila i provjere iz (ponovne) javne rasprave GUP-a 2024., baza klizišta
- Odluka o GUP-u Grada Zagreba, neslužbeni pročišćeni tekst s izmjenama 2025. (urbana pravila)
- Izmjene i dopune GUP-a Sesveta 2026., odredbe za provedbu, prijedlog za ponovnu javnu raspravu (lipanj 2026.) i karta urbanih pravila 4a
- Prostorni plan Grada Zagreba, Odredbe za provedbu (izmjene i dopune 2017.), točka 2.3.1. za građevinska područja naselja izvan GUP-ova (`src/rules_ppgz.json`)
- Topografska osnova Grada Zagreba 2018. (tlocrti postojećih zgrada); Open-Meteo / Copernicus DEM (nagib terena)
- Odluka o izmjenama i dopuni Odluke o komunalnom doprinosu (Gradska skupština, 13. 12. 2023.)
- HERA, naknada za priključenje (NN 45/2026); Uredba o Tarifi upravnih pristojbi (NN 156/2022)
- OpenStreetMap (Overpass) za ceste i sadržaje u okolini

Procjene su orijentacijske. Pravno mjerodavna je lokacijska informacija Grada Zagreba.

## Izmjene
Uređuje se `src/app.template.html`, a `python3 build.py` sastavlja `index.html`.
Pravila za Sesvete: `pdfplumber` tekst prvog dijela PDF-a odredbi (bez prikaza izmjena), zatim `python3 src/parse_gup_sesvete.py ses_first.txt src/rules_sesvete.json`.

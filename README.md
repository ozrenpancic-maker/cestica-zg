# Čestica ZG

Mobilna web aplikacija: dodirneš zemljište u Zagrebu i dobiješ katastarsku česticu, namjenu iz prostornih planova, urbano pravilo GUP-a s uvjetima gradnje, provjere rizika (UPU, klizišta, zaštita, voda), pristup i okolinu, procjenu doprinosa, priključaka i cijene gradnje te popis dokumentacije s adresama ureda.

**Aplikacija:** https://ozrenpancic-maker.github.io/cestica-zg/

## Izvori podataka
- Grad Zagreb, ArcGIS servisi: katastarske čestice (2023.), planirana namjena, urbana pravila i provjere iz (ponovne) javne rasprave GUP-a 2024., baza klizišta
- Odluka o GUP-u Grada Zagreba, neslužbeni pročišćeni tekst s izmjenama 2025. (urbana pravila)
- Odluka o izmjenama i dopuni Odluke o komunalnom doprinosu (Gradska skupština, 13. 12. 2023.)
- HERA, naknada za priključenje (NN 45/2026); Uredba o Tarifi upravnih pristojbi (NN 156/2022)
- OpenStreetMap (Overpass) za ceste i sadržaje u okolini

Procjene su orijentacijske. Pravno mjerodavna je lokacijska informacija Grada Zagreba.

## Izmjene
Uređuje se `src/app.template.html`, a `python3 build.py` sastavlja `index.html`.

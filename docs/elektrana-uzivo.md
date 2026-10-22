# Sunčana elektrana uživo: proizvodnja prema okretu kuće i sjeni okolnih zgrada

Stanje 23. 10. 2026., grana `razvoj`.

## Što radi

Kad je u simulatoru postavljena kuća, kalkulator sunčane elektrane zadano računa „prema kući na karti":

- **Plohe krova** iz simulatora: dvostrešni krov ima dvije plohe okomite na sljeme, četverostrešni četiri, a ravni krov ima panele na nosačima prema jugu, pa okret kuće na njemu ne mijenja proizvodnju. Nagib je nagib krova iz simulatora.
- Paneli se računaju na plohi s najvećom proizvodnjom. Tablica pokazuje proizvodnju po kWp za svaku plohu.
- **Uživo:** okret ili pomak kuće na karti te promjena krova, nagiba ili sljemena odmah preračunavaju proizvodnju, najviše jednom po sličici.
- **Graf proizvodnje prema okretu kuće** računa se u koracima od 5°: za dvostrešni krov 0–180°, za četverostrešni 0–90°, jer se okret ponavlja. Prikazuje najbolji i najlošiji okret, a gumb okreće kuću na najbolji.
- **Sjena okolnih zgrada:** obzor oko sredine krova iz zgrada u krugu 80 m. Izvori su ZG3D 2022 u Zagrebu, katastar DGU na Krku (visine pretpostavljene) i OpenStreetMap drugdje.
  - Kad je Sunce ispod obzora zgrade, izravno zračenje se ne računa.
  - Raspršeno zračenje se smanjuje za zaklonjeni dio neba.
  - Teren, drveće i dimnjaci nisu uključeni; za njih je polje „Zasjenjenje".

## Model

- Jedan dohvat s Open-Meteo (ERA5): satno globalno, izravno i raspršeno zračenje za 2023.–2025.
- Položaj Sunca računa se za sredinu svakog sata, jer je vrijednost prosjek prethodnog sata (`solarPos`, NOAA).
- Zračenje na plohu računa se izotropnim modelom neba, s albedom 0,2.
- Jedna orijentacija računa se za oko 1–3 ms, pa je moguće računanje uživo.

## Provjera prema Open-Meteo

Provjera je napravljena 22. 10. 2026. za Kornić (45,044 N, 14,616 E), za 2023.–2025. Uspoređen je godišnji zbroj zračenja na plohu (kWh/m²) iz lokalnog modela s Open-Meteo `global_tilted_irradiance` za isti nagib i smjer.

| Nagib | Smjer (Open-Meteo azimut) | Open-Meteo | Lokalni model | Razlika |
|---|---|---|---|---|
| 30° | jug (0) | 1.717,6 | 1.717,7 | 0,00 % |
| 30° | istok (−90) | 1.391,8 | 1.393,0 | +0,08 % |
| 30° | zapad (90) | 1.394,2 | 1.394,5 | +0,02 % |
| 30° | jugoistok (−45) | 1.624,0 | 1.624,7 | +0,04 % |
| 30° | jugozapad (45) | 1.626,8 | 1.626,7 | 0,00 % |
| 45° | sjever (180) | 791,4 | 792,8 | +0,18 % |
| 10° | jug | 1.605,2 | 1.606,1 | +0,05 % |
| 60° | jug | 1.596,5 | 1.595,0 | −0,10 % |
| 0° | vodoravno | 1.493,8 | 1.495,0 | +0,08 % |

Isprobani model Hay–Davies (s cirkumsolarnim dijelom) odstupao je do 11 %. Zato je odabran izotropni model, koji daje iste brojke kao dosadašnji kalkulator.

## Testovi

`tests/run.js`, skupina `pvLiveTests`, sa sintetičkom godinom vedrog neba:

- jug je bolji od istoka i zapada, istok ≈ zapad, a sjever je najlošiji;
- zgrada južno od kuće zaklanja Sunce, više zimi nego ljeti;
- niža zgrada od krova ne baca sjenu na krov;
- plohe dvostrešnog krova se okreću s kućom;
- najbolja ploha se mijenja s okretom;
- četverostrešni krov ima 4 plohe, a ravni krov je neovisan o okretu.

Tok u pregledniku (postavljanje kuće, okret, preračun, graf i gumb) provjeren je u Chromiumu.

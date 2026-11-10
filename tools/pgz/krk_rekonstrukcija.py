"""Odredbe PPUG-a Krka za rekonstrukciju, dogradnju i nadogradnju postojećih zgrada → src/rules_krk.json (ključ "rekonstrukcija" na razini Grada Krka).

Izvor: Prostorni plan uređenja Grada Krka, odredbe za provođenje (pročišćeni tekst, SN PGŽ 29/2020), PDF Zavoda za prostorno uređenje PGŽ
(zavod.pgz.hr, docsplanovigrad/1541/ppug-krka-pt.pdf); tekst izvučen iz PDF-a 10. 11. 2026. Članci 17., 56., 56.a, 78., 167., 170.
Pokretanje: python3 -I tools/pgz/krk_rekonstrukcija.py
"""
import json, os

SVE, POST = ["rek", "dogr", "nadogr", "zamj"], ["rek", "dogr", "nadogr"]
REKON = [
    {"zahvati": POST, "clanak": "56.", "opis": "Postojeće zgrade u građevinskom području naselja mogu se rekonstruirati i prenamijeniti prema odredbama za neposrednu provedbu plana (st. 2.).",
     "txt": "Postojeće građevine stambene, društvene, sportsko-rekreacijske, gospodarske, ugostiteljsko-turističke namjene u građevinskom područjima naselja mogu se rekonstruirati i prenamijeniti u skladu s odredbama za neposrednu provedbu ovog Prostornog plana."},
    {"zahvati": POST, "clanak": "56.", "opis": "Ako zgrada ima veću etažnost i visinu od propisane, rekonstruira se u postojećim visinskim gabaritima uz zadržavanje etažnosti; dogradnja smije imati visinu i etažnost propisanu planom (st. 2.).",
     "txt": "Ukoliko postojeće građevine imaju veću etažnost i visinu od propisane ovim Prostornim planom, dozvoljava se rekonstrukcija istih u postojećim visinskim gabaritima sa zadržavanjem postojeće etažnosti, a za dogradnje postojećih građevina dozvoljava se visina i etažnost propisana ovim Prostornim planom."},
    {"zahvati": POST, "clanak": "56.", "opis": "Ako zgrada ima veće tlocrtne gabarite od propisanih, rekonstruira se u postojećim tlocrtnim gabaritima, uz mogućnost nadogradnje pod uvjetima plana (st. 2.).",
     "txt": "Ukoliko postojeće građevine imaju veće tlocrtne gabarite od propisanih ovim Prostornim planom dozvoljava se rekonstrukcija u postojećim tlocrtnim gabaritima uz mogućnost nadogradnje pod uvjetima propisanim ovim Prostornim planom."},
    {"zahvati": POST, "clanak": "17.", "opis": "Zgrada u izgrađenom dijelu naselja bliže regulacijskom pravcu od propisanog može se rekonstruirati ako se postojeća udaljenost ne smanjuje (st. 3.).",
     "txt": "Postojeće građevine osnovne namjene u izgrađenim dijelovima naselja, koje se nalaze na udaljenostima manjim od onih iz stavka (1) i (2), mogu se rekonstruirati pod uvjetom da se ne smanjuje postojeća udaljenost građevine od regulacijskog pravca."},
    {"zahvati": SVE, "clanak": "170.", "opis": "U naseljima Kornić (UPU 2) i Vrh (UPU 5) do donošenja UPU-a dopuštena je gradnja unutar izgrađenog dijela građevinskog područja (NA2, NA5.1) prema odredbama ovog plana (st. 1.)."},
    {"zahvati": POST, "clanak": "170.", "opis": "Izdvojena građevinska područja izvan naselja s obvezom UPU-a (UPU 21–32): do donošenja UPU-a samo rekonstrukcija, adaptacija i dogradnja u opsegu neophodnom za poboljšanje uvjeta korištenja i rada: obnova i zamjena dotrajalih dijelova u postojećim gabaritima, priključci i instalacije, dogradnja sanitarnih prostorija (WC, kupaonica, stubište) do 10 % građevinske (bruto) površine, uređenje potkrovlja unutar postojećeg gabarita (st. 2.–3.)."},
    {"zahvati": POST, "clanak": "17.", "opis": "Kod rekonstrukcije u izgrađenom dijelu naselja iznimno su dopušteni dva ili više pristupa, odnosno parkiranje neposredno iza regulacijskog pravca, uz suglasnost nadležne uprave za ceste (st. 8.)."},
    {"zahvati": POST, "clanak": "78.", "opis": "Postojeća zgrada izvan građevinskog područja: vrijede uvjeti kao za građevinsko područje; u zaštićenim i vrijednim područjima (značajni krajobraz, osobito vrijedno tlo, šuma, vizualno eksponirane lokacije, površine za infrastrukturu) samo u opsegu neophodnom: obnova u postojećim gabaritima, priključci, sanitarije do 10 % GBP-a, potkrovlje unutar gabarita bez prekoračenja kig-a i kis-a; prenamjena u stambenu nije dopuštena."},
    {"zahvati": POST, "clanak": "167.", "opis": "Rekonstrukcijom u naselju ne smije se povećati ukupno postojeće požarno opterećenje zgrade, zone ili naselja (st. 2.)."},
]

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d["rekonstrukcija"] = REKON
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Grad Krk: odredbi za rekonstrukciju", len(REKON))

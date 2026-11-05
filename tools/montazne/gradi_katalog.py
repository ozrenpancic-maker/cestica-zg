"""Gradi src/montazne_kuce.json: interni katalog montažnih kuća (9 prizemnica, 9 katnica, 9 kuća s potkrovljem).
Svaka brojka prepisana je sa stranice proizvođača (preuzeto 5. 11. 2026., WebFetch). Ništa se ne procjenjuje ovdje;
izvedene vrijednosti (tlocrt) računa aplikacija i označava ih kao procjenu.
Proizvođači ne objavljuju vanjske mjere tlocrta (širina × dužina): Domprojekt daje neto površinu, Icon bruto,
Partas neto, bruto, visinu zgrade i najmanju širinu i duljinu zemljišta."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[2]
D = "2026-11-05"

def partas(q, neto, bruto, sobe, vis, sir, dul, nagib, krov, kat, katIzvor, nap=None):
    return dict(id=f"partas-q{q}", proizvodjac="Partas", naziv=f"Q {q}", kategorija=kat, kategorijaIzvor=katIzvor,
                neto=neto, bruto=bruto, sobe=sobe, visina=vis, minZemljiste={"sirina": sir, "duljina": dul},
                krov={"tip": krov, "nagib": nagib, "opis": ("ravni krov" if krov == "ravni" else "kosi krov") + f", nagib {str(nagib).replace('.', ',')}°"},
                url=f"https://partas.hr/q-{q}/", preuzeto=D, napomena=nap)

def dom(slug, naziv, neto, sobe, kat, krov=None, krovOpis=None, katIzvor="kategorija na stranici proizvođača"):
    return dict(id="domprojekt-" + naziv.lower(), proizvodjac="Domprojekt", naziv=naziv, kategorija=kat, kategorijaIzvor=katIzvor,
                neto=neto, bruto=None, sobe=sobe, sobeVrsta="spavaće sobe" if sobe else None, visina=None, minZemljiste=None,
                krov={"tip": krov, "nagib": 0 if krov == "ravni" else None, "opis": krovOpis} if krov else None,
                url="https://www.domprojekt.hr/" + slug, preuzeto=D,
                napomena="Proizvođač objavljuje neto površinu (na stranici modela Nives: »Ukupna neto površina«); bruto površina, vanjske mjere i visina nisu objavljene.")

def icon(slug, naziv, bruto, kat, krov, nagib, opis, katIzvor):
    return dict(id="icon-" + slug, proizvodjac="Icon Group", naziv=naziv, kategorija=kat, kategorijaIzvor=katIzvor,
                neto=None, bruto=bruto, sobe=None, visina=None, minZemljiste=None,
                krov={"tip": krov, "nagib": nagib, "opis": opis}, url=f"https://www.icon-group.hr/{slug}/", preuzeto=D,
                napomena="Proizvođač objavljuje bruto površinu; vanjske mjere i visina nisu objavljene.")

H1 = "izvedeno: visina zgrade {} m premala je za dvije etaže"
P = [
    partas(405, 85.80, 107.20, 3, 3.95, 19.34, 18.70, 2, "ravni", "P", H1.format("3,95")),
    partas(410, 83.20, 132.00, 3, 4.53, 18.00, 19.86, 2, "ravni", "P", H1.format("4,53")),
    partas(400, 106.70, 135.50, 4, 5.48, 20.52, 18.22, 22, "kosi", "P", H1.format("5,48")),
    partas(520, 106.30, 134.87, 4, 5.33, 22.08, 16.28, 22, "kosi", "P", H1.format("5,33")),
    partas(140, 165.00, 209.55, 3, 5.05, 22.70, 25.30, 2, "ravni", "P", H1.format("5,05")),
    partas(120, 185.14, 227.00, 3, 4.62, 20.31, 28.81, 1, "ravni", "P", H1.format("4,62")),
    dom("nives-niskoenergetska-montazna-kuca", "Nives", 118.54, 2, "P", "ravni", "ravni krov (opis modela)"),
    dom("marinela-niskoenergetska-montazna-kuca", "Marinela", 103.25, None, "P"),
    dom("ingrid-niskoenergetska-montazna-kuca", "Ingrid", 115.93, None, "P"),
]
K2 = "opis modela: prizemlje i kat"
K = [
    partas(210, 187.88, 238.32, 5, 8.65, 19.64, 19.60, 25, "kosi", "P1", K2),
    partas(220, 216.20, 265.92, 5, 8.67, 24.33, 20.28, 24, "kosi", "P1", K2),
    partas(230, 209.10, 265.55, 4, 8.62, 21.75, 24.35, 20, "kosi", "P1", K2, "iznad kata tavanski prostor"),
    partas(250, 229.62, 282.43, 5, 9.15, 20.08, 24.29, 40, "kosi", "P1", K2, "iznad kata tavanski dio"),
    partas(300, 233.60, 297.00, 5, 8.85, 21.90, 28.40, 25, "kosi", "P1", K2, "iznad kata slobodan tavanski prostor"),
    icon("lina", "Lina", 198.07, "P1", "cet", 25, "četverovodni krov 25° ili ravni krov", "tlocrti na stranici: »Prizemlje« i »Kat«"),
    icon("petra", "Petra", 209.63, "P1", None, None, "ravni, četverovodni, jednovodni ili dvovodni krov (nagib nije naveden)", "tlocrti na stranici: »Prizemlje« i »Kat«"),
    dom("elena-niskoenergetska-katnica", "Elena", 140.11, 3, "P1", "ravni", "katnice s ravnim krovom (opis kategorije)"),
    dom("gloria-niskoenergetska-katnica", "Gloria", 147.71, 3, "P1", "ravni", "katnice s ravnim krovom (opis kategorije)"),
]
PK = [dom(f"{n.lower()}-montazne-kuce-potkrovlje", n, a, s, "PPk") for n, a, s in [
    ("Alma", 110.12, 3), ("Venera", 126.81, 4), ("Doris", 134.54, 4), ("Leonida", 145.43, 4), ("Ema", 160.90, 3),
    ("Renata", 161.08, 4), ("Emanuela", 165.07, 3), ("Lena", 167.86, 4), ("Laura", 176.40, 4)]]

out = {
    "v": 1, "preuzeto": D,
    "opis": "Interni katalog montažnih kuća. Vrijednosti su prepisane sa stranica proizvođača; vanjske mjere tlocrta nijedan proizvođač ne objavljuje.",
    "kategorije": [["P", "Prizemnice"], ["P1", "Katnice"], ["PPk", "S potkrovljem"]],
    "izvori": [
        {"proizvodjac": "Partas", "katalog": "https://partas.hr/katalog/", "objavljuje": "neto i bruto površina, broj soba, visina zgrade, najmanja širina i duljina zemljišta, nagib i vrsta krova"},
        {"proizvodjac": "Domprojekt", "katalog": "https://www.domprojekt.hr/", "objavljuje": "neto površina, broj spavaćih soba, kategorija (prizemna, katna, s potkrovljem)"},
        {"proizvodjac": "Icon Group", "katalog": "https://www.icon-group.hr/montazne-kuce/obiteljske-kuce/", "objavljuje": "bruto površina, vrsta i nagib krova; etaže prema nazivima tlocrta"},
    ],
    "modeli": P + K + PK,
}
for m in out["modeli"]:
    for k in [k for k, v in m.items() if v is None]: del m[k]
assert [sum(m["kategorija"] == c for m in out["modeli"]) for c in ("P", "P1", "PPk")] == [9, 9, 9]
(root / "src/montazne_kuce.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(out["modeli"]), "modela")

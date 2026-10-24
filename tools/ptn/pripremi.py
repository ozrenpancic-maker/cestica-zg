"""Medijalne cijene i broj kupoprodaja zemljišta po JLS (MPGI i EIZ, Pregled tržišta nekretnina RH 2025, prilozi).

Izvor: https://mpgi.gov.hr/UserDocsImages/dokumenti/stambeno/Prilozi_PTN2025.zip (objavljeno 30. 4. 2026.)
Pokretanje: python3 tools/ptn/pripremi.py <mapa s raspakiranim prilozima> data/ptn/ptn2025.json

Vrijednosti: broj = €/m² (medijan) ili broj kupoprodaja; "z" = manje od 10 transakcija (podatak nije objavljen, privatnost);
null = nema transakcija ("." ili "-" u izvoru). Ništa se ne procjenjuje ni ne dopunjuje.
"""
import sys, os, glob, json, openpyxl

def nadji(d, pocetak):
    f = [x for x in glob.glob(os.path.join(d, "*.xlsx")) if os.path.basename(x).startswith(pocetak)]
    if len(f) != 1: raise SystemExit("nije pronađena datoteka: " + pocetak)
    return f[0]

def vr(v, dec):
    if v is None or v in (".", "-", ""): return None
    if v in ("z", "z9"): return "z"  # "z9" se u izvoru javlja 48 puta (broj kupoprodaja poljoprivrednog zemljišta); čita se kao "z"
    if isinstance(v, (int, float)): return round(float(v), dec) if dec else int(round(float(v)))
    raise SystemExit("nepoznata vrijednost: %r" % (v,))

def list_(ws, prvi_god):
    rows = list(ws.iter_rows(values_only=True)); hdr = rows[0]
    i0 = hdr.index(prvi_god); god = [str(h).strip().rstrip(".") for h in hdr[i0:i0 + 14]]
    out = {}
    for r in rows[2:]:
        if not isinstance(r[0], int): continue
        out[r[0]] = (r[1], r[2], r[i0:i0 + 14])
    return god, out

def main(d, izlaz):
    med = openpyxl.load_workbook(nadji(d, "Medijalne cijene"), read_only=True, data_only=True)
    cnt = openpyxl.load_workbook(nadji(d, "Broj kupoprodajnih transakcija"), read_only=True, data_only=True)
    god, mg = list_(med["Građevinska zemljišta EUR"], "2012.")
    _, mp = list_(med["Poljoprivredna zemljišta EUR"], "2012.")
    _, ng = list_(cnt["Građevinska zemljišta"], "2012.")
    _, np_ = list_(cnt["Poljoprivredna zemljišta"], "2012.")
    assert god == [str(y) for y in range(2012, 2026)], god
    jls = []
    for s in sorted(mg, key=lambda k: (mg[k][0], mg[k][1])):
        z, n, v = mg[s]
        jls.append([s, z, n,
                    [vr(x, 0) for x in v], [vr(x, 0) for x in ng[s][2]] if s in ng else None,
                    [vr(x, 2) for x in mp[s][2]] if s in mp else None, [vr(x, 0) for x in np_[s][2]] if s in np_ else None])
    o = {"izvor": "Ministarstvo prostornoga uređenja, graditeljstva i državne imovine i Ekonomski institut, Zagreb: Pregled tržišta nekretnina Republike Hrvatske 2025, prilozi (medijalne cijene po m² i broj kupoprodaja po JLS, 2012.–2025.)",
         "url": "https://mpgi.gov.hr/vijesti-8/predstavljene-publikacije-o-pregledu-trzista-nekretnina-republike-hrvatske-za-2024-i-2025-godinu/19831",
         "objavljeno": "2026-04-30", "godine": [int(g) for g in god],
         "polja": ["šifra", "županija", "JLS", "građevinsko €/m² (medijan)", "građevinsko broj kupoprodaja", "poljoprivredno €/m² (medijan)", "poljoprivredno broj kupoprodaja"],
         "napomena": "z = manje od 10 transakcija (podatak nije objavljen); null = nema transakcija", "jls": jls}
    with open(izlaz, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, separators=(",", ":"))
    print(len(jls), "JLS →", izlaz, os.path.getsize(izlaz), "B")

if __name__ == "__main__": main(sys.argv[1], sys.argv[2])

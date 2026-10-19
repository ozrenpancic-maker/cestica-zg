"""Provjera baze urbanističkih pravila (uvoz iz ČesticaHR Data Managera) prije ugradnje u aplikaciju.
Korištenje:
  python3 tools/baza/provjeri.py datoteka.json            # samo provjera i sažetak
  python3 tools/baza/provjeri.py datoteka.json --uvezi    # nakon uspješne provjere kopira u src/baza/baza.json
Pravila (docs/baza-uvoz.md):
  * potvrđeno pravilo mora imati službeni izvor (odluka s URL-om), članak, citat, datum provjere,
    status važenja plana i primjenjivost (zone i vrste gradnje);
  * pravni status i GIS primjenjivost provjeravaju se odvojeno;
  * kandidati se uvoze, ali aplikacija ih ne koristi u izračunu.
"""
import json, sys, re, pathlib, shutil

VRSTE_PLANA = {"PPŽ", "PPUG", "PPUO", "GUP", "UPU", "DPU", "PPPPO", "posebno", "ostalo"}
STATUS_VAZENJA = {"važeći", "u izradi", "van snage", "privremena mjera"}
VRSTE_ODLUKE = {"donošenje", "izmjene i dopune", "pročišćeni tekst", "odluka o izradi", "ostalo"}
PARAMETRI = {"min_cestica", "max_cestica", "kig", "kis", "kis_nadzemni", "kis_podzemni", "tlocrt_min", "tlocrt_max",
             "gbp_max", "visina", "etaze", "udaljenost_meda", "udaljenost_regulacija", "zelenilo", "parkiranje",
             "zabrana_gradnje", "ostalo"}
RAZINE_PRAVNE = {"potvrđeno", "kandidat"}
RAZINE_GIS = {"potvrđeno", "kandidat", "nema"}
DATUM = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL = re.compile(r"^https?://\S+$")

def provjeri(b):
    E, W = [], []  # greške (prekidaju uvoz), upozorenja
    if not isinstance(b, dict): return ["baza nije JSON objekt"], W, {}
    for k in ("verzija_sheme", "izvor", "izvezeno", "planovi", "pravila"):
        if k not in b: E.append(f"nedostaje polje '{k}'")
    if b.get("izvezeno") and not DATUM.match(str(b["izvezeno"])): E.append("izvezeno: datum mora biti GGGG-MM-DD")
    planovi, odluke = {}, {}
    for i, p in enumerate(b.get("planovi") or []):
        w = f"plan[{i}] {p.get('id','?')}"
        for k in ("id", "naziv", "vrsta", "status_vazenja", "obuhvat", "odluke"):
            if k not in p: E.append(f"{w}: nedostaje '{k}'")
        if p.get("id") in planovi: E.append(f"{w}: id se ponavlja")
        planovi[p.get("id")] = p
        if p.get("vrsta") not in VRSTE_PLANA: E.append(f"{w}: vrsta '{p.get('vrsta')}' nije jedna od {sorted(VRSTE_PLANA)}")
        if p.get("status_vazenja") not in STATUS_VAZENJA: E.append(f"{w}: status_vazenja '{p.get('status_vazenja')}' nije jedan od {sorted(STATUS_VAZENJA)}")
        ob = p.get("obuhvat") or {}
        if not ob.get("jls"): E.append(f"{w}: obuhvat.jls je obavezan (popis jedinica lokalne samouprave)")
        g = ob.get("gis") or {}
        if g and g.get("status") not in RAZINE_GIS: E.append(f"{w}: obuhvat.gis.status mora biti jedan od {sorted(RAZINE_GIS)}")
        for j, o in enumerate(p.get("odluke") or []):
            wo = f"{w} odluka[{j}] {o.get('id','?')}"
            for k in ("id", "naziv", "vrsta", "glasilo"):
                if not o.get(k): E.append(f"{wo}: nedostaje '{k}'")
            if o.get("vrsta") and o["vrsta"] not in VRSTE_ODLUKE: E.append(f"{wo}: vrsta '{o['vrsta']}' nije jedna od {sorted(VRSTE_ODLUKE)}")
            if o.get("datum") and not DATUM.match(str(o["datum"])): E.append(f"{wo}: datum mora biti GGGG-MM-DD")
            if o.get("url") and not URL.match(str(o["url"])): E.append(f"{wo}: url nije http(s) adresa")
            if o.get("id") in odluke: E.append(f"{wo}: id odluke se ponavlja")
            odluke[o.get("id")] = (p.get("id"), o)
    ids = set(); n = {"potvrđeno": 0, "kandidat": 0, "za_izracun": 0}
    for i, r in enumerate(b.get("pravila") or []):
        w = f"pravilo[{i}] {r.get('id','?')}"
        for k in ("id", "plan_id", "parametar", "vrijednost", "clanak", "primjenjivost", "pravni_status", "gis_status"):
            if k not in r: E.append(f"{w}: nedostaje '{k}'")
        if r.get("id") in ids: E.append(f"{w}: id se ponavlja")
        ids.add(r.get("id"))
        p = planovi.get(r.get("plan_id"))
        if not p: E.append(f"{w}: plan_id '{r.get('plan_id')}' ne postoji u planovima")
        if r.get("parametar") not in PARAMETRI: E.append(f"{w}: parametar '{r.get('parametar')}' nije jedan od {sorted(PARAMETRI)}")
        if r.get("odluka_id") and r["odluka_id"] not in odluke: E.append(f"{w}: odluka_id '{r['odluka_id']}' ne postoji")
        if r.get("odluka_id") in odluke and odluke[r["odluka_id"]][0] != r.get("plan_id"): E.append(f"{w}: odluka pripada drugom planu")
        ps, gs, pr = r.get("pravni_status") or {}, r.get("gis_status") or {}, r.get("primjenjivost") or {}
        if ps.get("razina") not in RAZINE_PRAVNE: E.append(f"{w}: pravni_status.razina mora biti jedna od {sorted(RAZINE_PRAVNE)}")
        if gs.get("razina") not in RAZINE_GIS: E.append(f"{w}: gis_status.razina mora biti jedna od {sorted(RAZINE_GIS)}")
        for k in ("datum_provjere",):
            if gs.get(k) and not DATUM.match(str(gs[k])): E.append(f"{w}: gis_status.{k} mora biti GGGG-MM-DD")
        if ps.get("razina") == "potvrđeno":
            n["potvrđeno"] += 1
            od = odluke.get(r.get("odluka_id"), (None, {}))[1]
            miss = []
            if not od: miss.append("odluka_id (službeni izvor)")
            elif not od.get("url"): miss.append("URL odluke")
            if not str(r.get("clanak") or "").strip(): miss.append("članak")
            if not str(r.get("citat") or "").strip(): miss.append("citat iz odluke")
            if not DATUM.match(str(ps.get("datum_provjere") or "")): miss.append("pravni_status.datum_provjere")
            if not p or p.get("status_vazenja") not in STATUS_VAZENJA: miss.append("status važenja plana")
            if not pr.get("zone"): miss.append("primjenjivost.zone")
            if not pr.get("vrste_gradnje"): miss.append("primjenjivost.vrste_gradnje")
            if miss: E.append(f"{w}: potvrđeno pravilo nema: {', '.join(miss)}")
            if gs.get("razina") == "potvrđeno" and p and p.get("status_vazenja") == "važeći": n["za_izracun"] += 1
        elif ps.get("razina") == "kandidat":
            n["kandidat"] += 1
            if not r.get("citat"): W.append(f"{w}: kandidat bez citata (prikazat će se bez navoda iz teksta)")
        if r.get("izmjena_od") and r["izmjena_od"] not in {x.get("id") for x in b.get("pravila") or []}:
            W.append(f"{w}: izmjena_od '{r['izmjena_od']}' ne postoji")
    return E, W, n

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    f = pathlib.Path(sys.argv[1]); b = json.loads(f.read_text(encoding="utf-8"))
    res = provjeri(b); E, W = res[0], res[1]; n = res[2] if len(res) > 2 else {}
    for x in W: print("UPOZORENJE:", x)
    for x in E: print("GREŠKA:", x)
    print(f"planova {len(b.get('planovi') or [])}, pravila {len(b.get('pravila') or [])}: potvrđeno {n.get('potvrđeno',0)}, kandidata {n.get('kandidat',0)}, za izračun (pravno + GIS potvrđeno, plan važeći) {n.get('za_izracun',0)}")
    if E: print(f"{len(E)} grešaka: baza se ne uvozi."); sys.exit(1)
    if "--uvezi" in sys.argv:
        dst = pathlib.Path(__file__).resolve().parents[2] / "src/baza/baza.json"; shutil.copyfile(f, dst); print("uvezeno u", dst)

if __name__ == "__main__": main()

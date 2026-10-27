#!/usr/bin/env python3
"""PILOT PREGLEDA PRAVILA: izvoz podataka za sučelje (UPU 13 Travičići).

Ulaz (zamrznuto, ne mijenja se):
  - izvor plana i odabrani članci (slijepi test hibrida v1, učitač v2.6);
  - kandidati AI generatora s rezultatom tehničke provjere (`usporedba_hibrid_v1.json`, samo polje `kandidati`);
  - evidencija plana i geometrija iz PGŽ servisa (`podaci/pgz_obuhvat_zona.json`).
NE koristi slijepe oznake (`neovisne_oznake.json`) ni dio `usporedba` iz rezultata: sučelje ih ne smije vidjeti,
a ništa se ne potvrđuje automatski.

Izlaz: `podaci/pilot_travicici.json` (+ SHA-256 na izlazu).
    python3 pilot_pregled/izvoz_podataka.py
"""
import hashlib, json, re, sys
from pathlib import Path

P = Path(__file__).resolve().parent
M = P.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(M / "hibrid"))
import slijepi_hibrid as S

IZVOR = M / "slijepo/travicici_upu13/travicici_upu13_sn_15_2012.html"
REZ = M / "slijepo_hibrid/travicici_upu13/usporedba_hibrid_v1.json"
GEN = M / "slijepo_hibrid/travicici_upu13/gen.json"
PGZ = P / "podaci/pgz_obuhvat_zona.json"
CLANCI = [9, 10, 13, 19]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

ZABRANJENA_POLJA = {"usporedba", "zapisi", "jednoznacnost", "uvjet_primjene", "razlozi_pregleda", "prostorni_obuhvat"}  # polja slijepih oznaka


def nadji(tekst, citat):
    """Položaj doslovnog citata u tekstu članka (razmaci se smiju razlikovati). Vraća (pocetak, kraj) ili None."""
    if not citat:
        return None
    rx = r"\s+".join(re.escape(w) for w in citat.split())
    m = re.search(rx, tekst)
    return (m.start(), m.end()) if m else None


def izvoz():
    S.provjeri_zamrzavanje()
    d, _, _ = S.ulaz(str(IZVOR), CLANCI)
    C = {c["broj"]: c for k, c in d["clanci"].items() if "#" not in k and c["broj"] in CLANCI}
    R = json.loads(REZ.read_text(encoding="utf-8"))
    pgz = json.loads(PGZ.read_text(encoding="utf-8"))
    kand = []
    for k in R["kandidati"]:
        t = C[k["clanak"]]["tekst"]
        poz = nadji(t, k.get("citat"))
        kand.append({
            "id": k["id"], "clanak": k["clanak"], "stavak": k.get("stavak"), "tocka": k.get("_tocka", k.get("tocka")),
            "alineja_rb": k.get("alineja_rb"), "citat": k.get("citat"), "citat_pozicija": list(poz) if poz else None,
            "ai_prijedlog": {x: k.get(x) for x in ("parametar", "operator", "vrijednost", "jedinica", "vrsta_gradevine", "nacin_gradnje",
                                                     "stanje", "zona", "uvjeti", "iznimke", "vrsta_pravila", "nejasno")},
            "tehnicka_provjera": {"status": k["_status"], "razlozi": [{"kod": a, "tekst": b} for a, b in k["_razlozi"]]},
        })
    sv = pgz["upu13_obuhvat"]["svojstva"]
    z = json.loads((M / "hibrid/ZAMRZNUTO_hibrid_v1.json").read_text(encoding="utf-8"))
    out = {
        "verzija_podataka": 1,
        "plan": {"naziv": "Urbanistički plan uređenja UPU 13 za građevinsko područje naselja Travičići i područje izdvojene namjene (T2-5)",
                 "jedinica": "Grad Opatija", "glasilo": "Službene novine Primorsko-goranske županije 15/2012", "klasa": "350-01/12-01/110",
                 "izvor_url": "https://www.sn.pgz.hr/default.asp?Link=odluke&id=24558", "izvor_sha256": sha(IZVOR),
                 "evidencija_pgz": {"status": sv["STATUS_PP"], "datum_objave": sv["DatumObjPlana"], "datum_stupanja_na_snagu": sv["DatumStNaSnPlana"],
                                    "datum_van_snage": sv["DatumStVanSnage"], "idplan": sv["IDPLAN"], "gis_sifra": sv["GIS_SIFRA"],
                                    "karte": sv["obradaKarataPP"], "pdf": sv["PDF_LINK_PUBLIC"], "provjereno": "2026-10-27",
                                    "servis": pgz["upu13_obuhvat"]["izvor"]},
                 "verzija_teksta": "osnovna odluka SN 15/2012; izmjene u evidenciji PGŽ nisu nađene (provjereno 27. 10. 2026.)"},
        "lanac": {"generator": "hibrid v1, upute v2, izolirani poziv bez alata", "gen_sha256": sha(GEN),
                  "zamrzavanje_hibrida_sha256": sha(M / "hibrid/ZAMRZNUTO_hibrid_v1.json"),
                  "provjera_sha256": z["datoteke"]["hibrid/provjera.py"], "rezultat_sha256": sha(REZ)},
        "clanci": [{"broj": b, "tekst": C[b]["tekst"]} for b in CLANCI],
        "kandidati": kand,
        "geometrija": {"upu13_obuhvat": pgz["upu13_obuhvat"]["geometrija"],
                       "zone": [{"oznaka": "T2-5", "izvor": pgz["zona_t2_5"]["izvor"], "svojstva": pgz["zona_t2_5"]["svojstva"],
                                 "geometrija": pgz["zona_t2_5"]["geometrija"]}],
                       "zone_bez_vektora": ["S1", "S2", "K"],
                       "napomena": "Zone S1, S2 i K postoje samo na rasterskoj karti UPU-a (PGŽ: »5 - u raster katalogu«); vektorska granica nije dostupna."},
    }
    s = json.dumps(out, ensure_ascii=False)
    assert not any(f'"{f}"' in s for f in ZABRANJENA_POLJA), "u izvozu su polja iz slijepih oznaka"
    p = P / "podaci/pilot_travicici.json"
    p.write_text(s, encoding="utf-8")
    return out, sha(p)


if __name__ == "__main__":
    o, h = izvoz()
    bez = [k["id"] for k in o["kandidati"] if not k["citat_pozicija"]]
    print(len(o["kandidati"]), "kandidata; citat nije nađen u tekstu:", bez, "\nsha", h)

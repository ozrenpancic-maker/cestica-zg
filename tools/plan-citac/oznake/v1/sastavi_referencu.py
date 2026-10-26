#!/usr/bin/env python3
"""Oznake v1: sastavljanje pregledanog referentnog skupa iz zamrznutih oznaka A i B i odluka suca.

    python3 sastavi_referencu.py ODLUKE_DIR

ODLUKE_DIR sadrži odluke izvezene sa stranice suca (jedna JSON datoteka po sporu).
Izlaz: odluke_suca_v1.json (sve odluke, doslovno), referenca_v1.json (konačni skup), IZVJESTAJ_referenca_v1.md.

Pravila:
- zapis u kojem se A i B slažu ulazi kakav jest (izvor "slaganje");
- RAZLIKA: izbor A ili B uzima taj zapis; "oba" uzima A i u `prihvatljivo` bilježi B-ove vrijednosti razlikovnih polja
  (čitač je točan ako pogodi bilo koju);
- SAMO_A / SAMO_B: zapis ostaje ako ga je sudac zadržao, inače se izostavlja;
- ispravak: primjenjuje se samo ono što se može izvesti iz doslovnog teksta; ostalo se bilježi u `ispravak_suca`
  i zapis ostaje PREGLED (pravilo »ništa se ne izmišlja«).
"""
import copy, glob, hashlib, json, sys
from collections import Counter
from pathlib import Path

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
SKUPINE = ["G1_ppug_22_23", "G2_ppug_25_33", "G3_ppug_20_38_39_50", "G4_upu1_14", "G5_upu1_24"]

# Ispravci suca: kako je svaki primijenjen. Ključ je id spora; tekst ispravka i obrazloženje su suca, doslovno.
ISPRAVCI = {
    # »Nejasno« o vrsti građevine (A: sportsko-rekreacijska građevina, B: bez vrste): vrsta se ne upisuje, zapis ostaje PREGLED.
    "G4_upu1_14:A007~B008": {"osnova": "B", "polja": {"vrsta_gradevine": None},
                             "dodaj_razlog": "TUMACENJE: sudac – vrsta građevine nije jasna iz teksta"},
    "G4_upu1_14:A006~B007": {"osnova": "B", "polja": {"vrsta_gradevine": None},
                             "dodaj_razlog": "TUMACENJE: sudac – vrsta građevine nije jasna iz teksta"},
    # »Od najniže poravnate površine«: točka mjerenja nije u citatu, pa se ne upisuje u uvjet; zapis ostaje PREGLED s napomenom.
    "G4_upu1_14:A030~B032": {"osnova": "A", "polja": {}, "izvan_teksta": True,
                             "dodaj_razlog": "TOCKA_MJERENJA: sudac navodi mjerenje od najniže poravnate površine; citat to ne navodi"},
    # »h je visina, 4 m je minimum, za 9 m visine 4,5 m« = max(h/2, 4,0) uz uvjet o otvorima (citat B ga sadrži doslovno).
    "G2_ppug_25_33:A025~B025": {"osnova": "B", "polja": {"operator": "max(h/2, X)", "vrijednost": 4.0},
                                "dodaj_razlog": "TOCKA_MJERENJA: sudac – h je visina građevine; točke mjerenja visine nisu u tekstu"},
}


# Isto pravilo koje sparivanje nije spojilo (različit citat i slobodni naziv parametra), a sudac je zadržao oba zapisa.
# Spaja se u jedan zapis: A ostaje, B-ov citat i naziv bilježe se kao prihvatljivi (kao odluka »oba«).
SPAJANJA = [("G3_ppug_20_38_39_50:A016~", "G3_ppug_20_38_39_50:~B016"),
            ("G3_ppug_20_38_39_50:A046~", "G3_ppug_20_38_39_50:~B047"),
            ("G3_ppug_20_38_39_50:A068~", "G3_ppug_20_38_39_50:~B070")]


def ucitaj_odluke(d):
    O = {}
    for f in sorted(glob.glob(str(Path(d) / "*.json"))):
        o = json.loads(Path(f).read_text(encoding="utf-8"))
        O[o["spor_id"]] = o
    return O


def main(odir):
    sporovi = {s["id"]: s for s in json.loads((D / "sporovi.json").read_text(encoding="utf-8"))}
    O = ucitaj_odluke(odir)
    assert set(O) == set(sporovi), f"odluke ne pokrivaju sve sporove: nedostaje {set(sporovi) - set(O)}, višak {set(O) - set(sporovi)}"
    po = D / "odluke_suca_v1.json"
    po.write_text(json.dumps({"sudac": "Ozren Pančić", "izvor": "stranica »Sudac oznaka v1«, zbirka odluke",
                              "odluke": [O[k] for k in sorted(O)]}, ensure_ascii=False, indent=1), encoding="utf-8")

    import spoji_oznake as SO
    ref, stat = {}, Counter()
    for g in SKUPINE:
        A = json.loads((D / f"oznake_A_{g}.json").read_text(encoding="utf-8"))["zapisi"]
        B = json.loads((D / f"oznake_B_{g}.json").read_text(encoding="utf-8"))["zapisi"]
        uA = {s["A"]["id"] for s in sporovi.values() if s["skupina"] == g and s["A"]}
        uB = {s["B"]["id"] for s in sporovi.values() if s["skupina"] == g and s["B"]}
        # parovi bez spora: A-zapisi koji se ne pojavljuju u sporovima (oba su ih označila jednako)
        zapisi = [dict(copy.deepcopy(a), izvor="slaganje", izvor_A=a["id"]) for a in A if a["id"] not in uA]
        stat["slaganje"] += len(zapisi)
        assert len(B) - len(uB) == len(zapisi), f"{g}: broj usklađenih zapisa A i B se razlikuje"
        for sid, s in sorted(sporovi.items()):
            if s["skupina"] != g:
                continue
            o = O[sid]; iz = o["izbor"]
            meta = {"spor": sid, "odluka": iz, "obrazlozenje_suca": o["obrazlozenje"], "datum_odluke": o["datum"]}
            if iz == "ispravak":
                p = ISPRAVCI[sid]
                z = copy.deepcopy(s[p["osnova"]]); z.update(p["polja"])
                z["jednoznacnost"] = "PREGLED"
                z["razlozi_pregleda"] = list(z.get("razlozi_pregleda") or []) + [p["dodaj_razlog"]]
                z["ispravak_suca"] = o["ispravak"]
                if p.get("izvan_teksta"):
                    z["ispravak_izvan_teksta"] = True
                stat["ispravak"] += 1
            elif s["vrsta"] == "RAZLIKA":
                z = copy.deepcopy(s["A"] if iz in ("A", "oba") else s["B"])
                if iz == "oba":
                    z["prihvatljivo"] = {f: s["B"].get(f) for f in s["polja"]}
                stat[iz] += 1
            else:
                zadrzan = (s["vrsta"] == "SAMO_A" and iz == "A") or (s["vrsta"] == "SAMO_B" and iz == "B")
                stat[f"{s['vrsta']}_{'zadržan' if zadrzan else 'izostavljen'}"] += 1
                if not zadrzan:
                    continue
                z = copy.deepcopy(s["A"] or s["B"])
            z.update(izvor="sudac", **meta, izvor_A=(s["A"] or {}).get("id"), izvor_B=(s["B"] or {}).get("id"))
            zapisi.append(z)
        for sa, sb in SPAJANJA:
            za = next((z for z in zapisi if z.get("spor") == sa), None); zb = next((z for z in zapisi if z.get("spor") == sb), None)
            if za and zb:
                za["prihvatljivo"] = {f: zb.get(f) for f in ("citat", "parametar", "vrijednost") if zb.get(f) != za.get(f)}
                za["spojeno_sa"] = {"spor": sb, "izvor_B": zb["izvor_B"], "obrazlozenje_suca": zb["obrazlozenje_suca"]}
                za["izvor_B"] = zb["izvor_B"]
                zapisi.remove(zb); stat["spojeno_isto_pravilo"] += 1
        zapisi.sort(key=lambda z: (z["clanak"], z.get("stavak") or 0, z.get("blok") or 0, z.get("alineja_rb") or 0, str(z.get("izvor_A") or z.get("izvor_B"))))
        for i, z in enumerate(zapisi, 1):
            z["id"] = f"R{i:03d}"
        ref[g] = zapisi

    out = {"naziv": "Pregledani referentni skup oznaka v1",
           "napomena": "Nije pravna potvrda. Bilježi što tekst doslovno kaže i gdje je nejasan, za mjerenje čitača.",
           "pravno_potvrdeno": 0,
           "ulazi": {**{f"tekst_{g}.txt": sha(D / f"tekst_{g}.txt") for g in SKUPINE},
                     **{f"oznake_{o}_{g}.json": sha(D / f"oznake_{o}_{g}.json") for g in SKUPINE for o in "AB"},
                     "UPUTE_OZNACAVANJA_v1.md": sha(D / "UPUTE_OZNACAVANJA_v1.md"),
                     "sporovi.json": sha(D / "sporovi.json"), "odluke_suca_v1.json": sha(po)},
           "skupine": {g: {"zapisa": len(z), "zapisi": z} for g, z in ref.items()}}
    pr = D / "referenca_v1.json"
    pr.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out, stat, O


if __name__ == "__main__":
    out, stat, O = main(sys.argv[1])
    print(json.dumps({g: v["zapisa"] for g, v in out["skupine"].items()}, ensure_ascii=False), sum(v["zapisa"] for v in out["skupine"].values()))
    print(dict(stat))
    print("sha referenca_v1.json", sha(D / "referenca_v1.json"))

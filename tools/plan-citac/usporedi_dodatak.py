#!/usr/bin/env python3
"""Provjera šest dodatnih automatski prihvaćenih pravila v2.1 u st. 2. čl. 22./23. prema zamrznutom dodatku oznaka
(oznake/dodatak_22_23/oznake_dodatak_st2.json). Postojeći referentni skup 22./23. se ne mijenja. Usporedba po poljima."""
import hashlib, json, re
from pathlib import Path
M = Path(__file__).resolve().parent
OZ = "oznake/dodatak_22_23/oznake_dodatak_st2.json"; OZ_SHA = "7e64ed66b56c9ba317efd0f41eb7035163a5070907092dee44adb6881cb6a170"
PAR = {"dopustenaGradnja": "dopuštenost gradnje uz osnovnu građevinu", "oblikKrovista": "oblik krovišta", "vrstaKosogKrovista": "vrsta kosog krovišta",
       "rekonstrukcijaIPrenamjena": "rekonstrukcija i prenamjena"}
OP = {"dopusteno": "dopustenje"}
n = lambda s: re.sub(r"\s+", " ", str(s or "")).strip().lower()


def main():
    assert hashlib.sha256((M / OZ).read_bytes()).hexdigest() == OZ_SHA
    Z = json.loads((M / OZ).read_text(encoding="utf-8"))["zapisi"]
    r = json.loads((M / "izlaz/ppug_v2_1.json").read_text(encoding="utf-8"))
    out = []
    for k in ("22", "23"):
        for p in r["clanci"][k]["pravila"]:
            if p["parametar"] not in PAR:
                continue
            o = next((z for z in Z if z["clanak"] == p["clanak"] and z["parametar"] == PAR[p["parametar"]]), None)
            mod_uv = " ".join(p["uvjeti"]); oz_uv = o["uvjet_primjene"] if o else None
            polja = {"operator": (OP.get(p["operator"], p["operator"]), o and o["operator"]),
                     "vrijednost": (p["vrijednost"], o and o["vrijednost"]),
                     "vrsta_pravila": (p["vrsta_pravila"], o and o["vrsta_pravila"]),
                     "uvjet": (mod_uv, oz_uv)}
            isto = {f: (n(a) == n(b)) for f, (a, b) in polja.items()}
            if o and not isto["uvjet"]:
                isto["uvjet"] = all(n(d) in n(mod_uv) for d in oz_uv.split("; ") if d) and bool(oz_uv) == bool(mod_uv)
            sadrzaj = o and n(" ".join(str(x) for x in (p["vrijednost"] or "", mod_uv))) .replace(" ", "") == n(" ".join(str(x) for x in (o["vrijednost"] or "", o["uvjet_primjene"]))).replace(" ", "")
            out.append({"id": p["id"], "clanak": p["clanak"], "stavak": p["stavak"], "tocka": p["tocka"], "alineja": p["alineja"],
                        "izvorni_citat": p["izvorni_citat"], "pravilo": {x: p[x] for x in ("parametar", "operator", "vrijednost", "vrsta_pravila", "uvjeti", "alternative")},
                        "status_modula": p["status"], "razlog_kod": p["razlog_kod"],
                        "oznaka": o and o["id"], "jednoznacnost_oznake": o and o["jednoznacnost"], "obrazlozenje_oznake": o and o["obrazlozenje_pregleda"],
                        "moguci_sukobi_oznaka": o and o.get("moguci_sukobi"), "polja_ista": isto, "isti_sadrzaj_vrijednost_i_uvjet": bool(sadrzaj),
                        "ocjena": ("TOČNO" if o and all(isto.values()) else "RAZLIKA_SAMO_U_VRSTI_PRAVILA" if o and [f for f, v in isto.items() if not v] == ["vrsta_pravila"] else
                                   "TOČNO_SADRŽAJNO_DRUGA_GRANULARNOST" if o and sadrzaj and isto["operator"] else
                                   "RAZLIKA" if o else "BEZ_OZNAKE") if p["status"] == "PRIJEDLOG" else
                                  ("PREGLED_ODGOVARA" if o and o["jednoznacnost"] == "PREGLED" else "PREGLED")})
    return out


if __name__ == "__main__":
    o = main()
    s = json.dumps(o, ensure_ascii=False, indent=1)
    (M / "oznake/dodatak_22_23/usporedba_dodatak_v2_1.json").write_text(s, encoding="utf-8")
    print(hashlib.sha256(s.encode()).hexdigest())
    for x in o:
        print(x["id"], x["pravilo"]["parametar"], x["status_modula"], "→", x["oznaka"], x["jednoznacnost_oznake"], x["ocjena"], {k: v for k, v in x["polja_ista"].items() if not v})

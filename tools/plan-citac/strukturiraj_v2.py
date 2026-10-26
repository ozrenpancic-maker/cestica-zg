#!/usr/bin/env python3
"""EKSPERIMENT v2.1: strukturiranje s gramatikom v2.1. Zamrznuti strukturiraj.py (v1) se ne mijenja.

Redoslijed: obrasci UPU-a 2 iz strukturiraj.py (v1, bez izmjena); ako vrsta građevine nije prepoznata, gramatika v2.1.
Na kraju se provjeravaju sukobi među člancima. Ništa nije pravno potvrđeno.

    python3 strukturiraj_v2.py dokazi.json [--clanci 22 23] -o pravila_v2.json
"""
import argparse, hashlib, json
from pathlib import Path
import strukturiraj as s1
import gramatika_v2 as g2


def strukturiraj_clanak(br, c, plan):
    r = s1.strukturiraj_clanak(br, c, plan, gramatika_ukljucena=False)
    if r["vrste"]:
        return r
    g = g2.clanak(br, c, plan)
    return g if g["vrste"] else dict(r, pregled=r["pregled"] + g["pregled"], nepokriveno=r["nepokriveno"] + g.get("nepokriveno", []))


def strukturiraj(dokazi, clanci, plan):
    out = {"shema": "plan-citac-pravila/2.1", "gramatika": g2.VERZIJA, "izvor": dokazi.get("izvor"), "sha256_izvora": dokazi.get("sha256"),
           "plan": plan, "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False,
           "statusi": {"PRIJEDLOG": "ACCEPTED – automatski prihvaćen prijedlog (nije pravna potvrda)", "PREGLED": "REVIEW", "ODBIJENO": "REJECTED"}}
    for k, c in dokazi["clanci"].items():
        br = c["broj"]
        if clanci and br not in clanci:
            continue
        out["clanci"][k] = strukturiraj_clanak(br, c, plan)
    g2.provjeri_sukobe(out["clanci"])
    sv = [p for c in out["clanci"].values() for p in c.get("pravila", [])]
    out["sazetak"] = {"pravila": len(sv), "prijedlog": sum(p["status"] == "PRIJEDLOG" for p in sv),
                      "pregled": sum(p["status"] == "PREGLED" for p in sv),
                      "odbijeno": sum(len(c.get("nepokriveno", [])) for c in out["clanci"].values())}
    return out


def zapisi_json(obj, putanja):
    s = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=False)
    Path(putanja).write_text(s, encoding="utf-8")
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("dokazi"); a.add_argument("--clanci", type=int, nargs="*"); a.add_argument("--plan", default="PPUG Krk"); a.add_argument("-o", "--izlaz", required=True)
    x = a.parse_args()
    d = json.loads(Path(x.dokazi).read_text(encoding="utf-8"))
    r = strukturiraj(d, x.clanci, x.plan)
    print(zapisi_json(r, x.izlaz), json.dumps(r["sazetak"]))

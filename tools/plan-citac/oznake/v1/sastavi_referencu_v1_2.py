#!/usr/bin/env python3
"""Referentni skup v1.2 = zamrznuti referenca_v1.json + odluke suca v1.2 (odluke_suca_v1_2.json). Izvorne oznake A/B,
odluke v1 i v1.1 te referenca_v1.json se ne mijenjaju; svaka promjena zapisa bilježi se u `promjene_v1_2` zapisa.

    python3 sastavi_referencu_v1_2.py   # → referenca_v1_2.json
"""
import copy, hashlib, json, re
from pathlib import Path

D = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
REF_V1 = "e6b2f7a5282d99694ad8cd0cd5939e5db350fa28c8736ffd6e1eddd44a7f85cc"
RX_CESTA = re.compile(r"^za\s.*\b(cest\w*|ulic\w*)\b", re.I)


def main():
    assert sha(D / "referenca_v1.json") == REF_V1, "referenca_v1.json promijenjena"
    odl = json.loads((D / "odluke_suca_v1_2.json").read_text(encoding="utf-8"))
    ref = copy.deepcopy(json.loads((D / "referenca_v1.json").read_text(encoding="utf-8")))
    ukloni_nova = {(x["skupina"], x["id"]): x["razlog"] for x in odl["odluke"][1]["primjena"]["ukloni_nova"]}
    log = []
    for g, v in ref["skupine"].items():
        for z in v["zapisi"]:
            pr = []
            # odluka 1: udaljenost od regulacijskog pravca po kategoriji ceste je UVJETNO; kategorija ostaje u uvjetu
            if z["parametar"] == "najmanja udaljenost od regulacijskog pravca":
                dij = [d.strip() for d in (z["uvjet_primjene"] or "").split(";") if d.strip()]
                if any(RX_CESTA.match(d) for d in dij) and z["vrsta_pravila"] == "OSNOVNO":
                    z["vrsta_pravila"] = "UVJETNO"; pr.append("ODLUKA_1: vrsta_pravila OSNOVNO -> UVJETNO (kategorija ceste)")
            # odluka 2: »(nova)« samo kad je izričito opravdana tekstom ili nedvosmislenim kontekstom
            if (g, z["id"]) in ukloni_nova:
                z["vrsta_gradevine"] = z["vrsta_gradevine"].replace(" (nova)", "")
                pr.append("ODLUKA_2: uklonjeno »(nova)« – " + ukloni_nova[(g, z["id"])])
            if pr:
                z["promjene_v1_2"] = pr; log.append({"skupina": g, "id": z["id"], "promjene": pr})
    nedostaje = [k for k in ukloni_nova if not any(x["skupina"] == k[0] and x["id"] == k[1] for x in log)]
    assert not nedostaje, f"odluka 2 navodi zapise kojih nema: {nedostaje}"
    ref.update(naziv="Pregledani referentni skup oznaka v1.2",
               izvedeno_iz={"referenca_v1.json": REF_V1, "odluke_suca_v1_1.json": sha(D / "odluke_suca_v1_1.json"),
                            "odluke_suca_v1_2.json": sha(D / "odluke_suca_v1_2.json")},
               promjene_v1_2=log,
               napomena_odluka_3="Odluka 3 (»samostojeće« = »samostojeće građevine«) ne mijenja zapise; primjenjuje se u usporedbi (ocijeni_v1_2.py).")
    p = D / "referenca_v1_2.json"
    p.write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
    return log, sha(p)


if __name__ == "__main__":
    log, s = main()
    for x in log:
        print(x["skupina"], x["id"], "; ".join(x["promjene"]))
    print(len(log), "promjena; referenca_v1_2.json", s)

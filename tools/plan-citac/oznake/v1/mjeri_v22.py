#!/usr/bin/env python3
"""Mjerenje zamrznute v2.2 na pregledanom referentnom skupu v1 (referenca_v1.json).

    python3 mjeri_v22.py            # izlaz: mjerenje_v22_ref_v1.json + sažetak

Kod v2.2 se ne mijenja: prije i poslije mjerenja provjeravaju se kontrolne sume iz ZAMRZNUTO_v2_2.json
i SHA-256 referentnog skupa. Usporedba polja je ona iz usporedi_v22.razlike (zamrznuta); ovdje se dodaje samo:
  1. nazivi parametara iz zatvorenog popisa uputa v1 (mapiranje_ref_v1.json, samo nazivi, nikad vrijednosti);
  2. zapisi s `prihvatljivo` (odluka suca »oba«): pravilo je točno ako se slaže s bilo kojom inačicom;
  3. pravilo iz uputa v1 (§ 3): ALTERNATIVA nije vrsta pravila, pa je ALTERNATIVA čitača jednaka OSNOVNO ili UVJETNO
     oznake; broji se odvojeno kao »točno uz pravilo granularnosti«, kao i dosadašnja tri pravila.
Razredi i mjere su isti kao u usporedi_v22.usporedi_oznake.
"""
import copy, hashlib, json, sys
from pathlib import Path

D = Path(__file__).resolve().parent
M = D.parent.parent
sys.path.insert(0, str(M))
import usporedi_v22 as U22

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
REF_SHA = "e6b2f7a5282d99694ad8cd0cd5939e5db350fa28c8736ffd6e1eddd44a7f85cc"
PODRUCJE = {"G1_ppug_22_23": ("ppug", {(22, 1), (22, 2), (23, 1), (23, 2)}),
            "G2_ppug_25_33": ("ppug", {(25, 1), (25, 2), (33, 1), (33, 2), (33, 3), (33, 4)}),
            "G3_ppug_20_38_39_50": ("ppug", {(20, 3), (38, 6), (39, 2), (50, 4)}),
            "G4_upu1_14": ("upu1", {(14, None)}),
            "G5_upu1_24": ("upu1", {(24, None)})}


def integritet():
    z = json.loads((M / "ZAMRZNUTO_v2_2.json").read_text(encoding="utf-8"))
    los = [p for g in ("kod", "mapiranje") for p, s in z[g].items() if sha(M / p) != s]
    if sha(D / "referenca_v1.json") != REF_SHA:
        los.append("oznake/v1/referenca_v1.json")
    if los:
        raise SystemExit("INTEGRITET NIJE POTVRĐEN: " + ", ".join(los))
    U22.provjeri_integritet()


def mapa():
    MP = U22.mapa()
    dop = json.loads((D / "mapiranje_ref_v1.json").read_text(encoding="utf-8"))
    for k, v in dop["parametri"].items():
        MP["parametri_v22"].setdefault(k, [])
        MP["parametri_v22"][k] = MP["parametri_v22"][k] + [x for x in v if x not in MP["parametri_v22"][k]]
        MP["parametri"].setdefault(k, v[0])
    for k, v in dop["vrsta_gradevine_istoznacnice"].items():
        st = MP["vrsta_gradevine_istoznacnice"].get(k, [])
        st = [st] if isinstance(st, str) else list(st)
        MP["vrsta_gradevine_istoznacnice"][k] = st + [x for x in v if x not in st]
    MP["oblici"].update(dop.get("oblici", {}))
    return MP


def inacice(o):
    """Zapis oznake i, za odluku »oba«, inačica s B-ovim vrijednostima razlikovnih polja."""
    t = o.get("tocka")
    o = dict(o, vrsta_gradevine=o.get("vrsta_gradevine") or "", uvjet_primjene=o.get("uvjet_primjene") or "",
             tocka=t.rstrip(")") if isinstance(t, str) and t != "-" else t)  # null = vrsta nije utvrđena
    out = [o]
    if o.get("prihvatljivo"):
        b = dict(o); b.update({k: (v if v is not None or k not in ("vrsta_gradevine", "uvjet_primjene") else "") for k, v in o["prihvatljivo"].items()}); out.append(b)
    return out


def razlike(z, o, MP):
    return min((U22.razlike(z, x, MP) for x in inacice(o)), key=len)


KONTEKST = []  # puni se iz odluke_suca_v1_1.json kad se pokrene s --v1.1


def bez_konteksta(x):
    dij = [d for d in (x.get("uvjet_primjene") or "").split("; ") if d.strip()]
    kon = {k["uvjet"].lower() for k in KONTEKST if k["clanak"] == x["clanak"] and k["stavak"] == x.get("stavak")}
    ost = [d for d in dij if d.strip().lower() not in kon]
    return dict(x, uvjet_primjene="; ".join(ost)) if len(ost) != len(dij) else None


def granularnost(z, o, MP):
    g = _granularnost(z, o, MP)
    if g is not None or not KONTEKST:
        return g
    for x in inacice(o):
        y = bez_konteksta(x)
        if y is None:
            continue
        if not U22.razlike(z, y, MP):
            return ["KONTEKST_CLANKA_v1_1"]
        g2 = _granularnost(z, dict(y, prihvatljivo=None), MP)
        if g2 is not None:
            return g2 + ["KONTEKST_CLANKA_v1_1"]
    return None


def _granularnost(z, o, MP):
    for x in inacice(o):
        r = U22.razlike(z, x, MP)
        if not r:
            return None
        gr = U22.granularnost(z, x, MP)
        if gr is not None:
            return gr
        if "tocka" in r and x["tocka"] == "-" and isinstance(z["tocka"], str) and len(z["tocka"]) == 1 and z["tocka"].isalpha():
            r2 = U22.razlike(dict(z, tocka="-"), x, MP)
            if not r2:
                return ["TOCKA_ILI_ALINEJA_v1"]
            g2 = U22.granularnost(dict(z, tocka="-"), x, MP)
            if g2 is not None:
                return g2 + ["TOCKA_ILI_ALINEJA_v1"]
        if r == ["vrsta_pravila"] and z["vrsta_pravila"] == "ALTERNATIVA" and x["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
            return ["ALTERNATIVA_NIJE_VRSTA_v1"]
        # kombinacija s dosadašnjim pravilima: ukloni razliku ALTERNATIVA pa provjeri ostatak
        if "vrsta_pravila" in r and z["vrsta_pravila"] == "ALTERNATIVA" and x["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
            g2 = U22.granularnost(dict(z, vrsta_pravila=x["vrsta_pravila"]), x, MP)
            if g2 is not None:
                return g2 + ["ALTERNATIVA_NIJE_VRSTA_v1"]
    return None


def usporedi(pravila, Z, MP):
    """Isti postupak i razredi kao usporedi_v22.usporedi_oznake, uz razlike/granularnost iznad."""
    zap = U22.u_zapise(pravila, MP)
    uzeto = [False] * len(Z)
    R = {"tocno": [], "pogresno": [], "pregled": [], "tocno_uz_granularnost": []}
    for z in zap:
        i = next((i for i, o in enumerate(Z) if not uzeto[i] and not razlike(z, o, MP)), None)
        gr = None
        if i is None:
            i = next((i for i, o in enumerate(Z) if not uzeto[i] and granularnost(z, o, MP) is not None), None)
            gr = granularnost(z, Z[i], MP) if i is not None else None
        if i is not None:
            uzeto[i] = True
        if gr is not None and z["status"] == "PRIJEDLOG":
            R["tocno_uz_granularnost"].append({"id": z["id"], "oznaka": Z[i]["id"], "pravila": gr}); continue
        o = Z[i] if i is not None else None
        if z["status"] == "PREGLED":
            R["pregled"].append({"id": z["id"], "oznaka": o and o["id"], "jednoznacnost_oznake": o and o["jednoznacnost"], "razlog_kod": z["razlog_kod"],
                                 "parametar": z["parametar"], "vrijednost": z["vrijednost"]})
        elif o is None:
            bl = min(((len(razlike(z, q, MP)), q["id"], razlike(z, q, MP)) for q in Z if q["clanak"] == z["clanak"]), default=None)
            R["pogresno"].append({"id": z["id"], "clanak": z["clanak"], "stavak": z["stavak"], "parametar": z["parametar"], "vrsta_gradevine": z["vrsta_gradevine"],
                                  "operator": z["operator"], "vrijednost": z["vrijednost"], "uvjet": z["uvjet_tekst"], "vrsta_pravila": z["vrsta_pravila"],
                                  "citat": z["izvorni_citat"], "najbliza_oznaka": bl and bl[1:]})
        else:
            R["tocno"].append({"id": z["id"], "oznaka": o["id"], "jednoznacnost_oznake": o["jednoznacnost"]})
    prop = []
    for i, o in enumerate(Z):
        if not uzeto[i]:
            bl = min(((len(razlike(z, o, MP)), z["id"], razlike(z, o, MP)) for z in zap if z["clanak"] == o["clanak"]), default=None)
            prop.append({"oznaka": o["id"], "parametar": o["parametar"], "jednoznacnost": o["jednoznacnost"], "najblizi_zapis": bl and bl[1:]})
    t, g, tg = len(R["tocno"]), len(R["pogresno"]), len(R["tocno_uz_granularnost"])
    s = {"oznaka": len(Z), "oznaka_JASAN": sum(o["jednoznacnost"] == "JASAN" for o in Z), "zapisa_modula": len(zap),
         "tocno_prihvaceno": t, "tocno_uz_pravilo_granularnosti": tg, "pogresno_prihvaceno": g,
         "pravilno_na_pregled": sum(1 for x in R["pregled"] if x["oznaka"] and x["jednoznacnost_oznake"] == "PREGLED"),
         "nepotrebno_na_pregled": sum(1 for x in R["pregled"] if x["oznaka"] and x["jednoznacnost_oznake"] == "JASAN"),
         "pregled_bez_oznake": sum(1 for x in R["pregled"] if not x["oznaka"]), "propusteno": len(prop),
         "preciznost_prihvacenih_strogo": round(t / (t + tg + g), 3) if t + tg + g else None,
         "preciznost_prihvacenih": round((t + tg) / (t + tg + g), 3) if t + tg + g else None,
         "pokrivenost_izdvajanja": round((t + tg + sum(1 for x in R["pregled"] if x["oznaka"])) / len(Z), 3) if Z else None,
         "pokrivenost_prihvacanja": round((t + tg) / len(Z), 3) if Z else None,
         "pokrivenost_prihvacanja_od_JASAN": round((t + tg) / max(1, sum(o["jednoznacnost"] == "JASAN" for o in Z)), 3),
         "udio_pregleda": round(len(R["pregled"]) / len(zap), 3) if zap else None}
    return s, dict(R, propusteno=prop)


def main(v11=False):
    integritet()
    if v11:
        KONTEKST[:] = json.loads((D / "odluke_suca_v1_1.json").read_text(encoding="utf-8"))["kontekst_clanka"]
    MP = mapa()
    ref = json.loads((D / "referenca_v1.json").read_text(encoding="utf-8"))
    izlaz = {"ppug": U22.pokreni_ppug(), "upu1": U22.pokreni_upu1()}
    izlaz2 = {"ppug": U22.pokreni_ppug(), "upu1": U22.pokreni_upu1()}
    import usporedi_v2 as U2
    det = all(U2.sha_obj(izlaz[k]) == U2.sha_obj(izlaz2[k]) for k in izlaz)
    out = {"verzija_citaca": "v2.2 (zamrznuta, 5c8b8345…)", "referenca": "oznake/v1/referenca_v1.json", "sha256_reference": REF_SHA,
           "determinizam": det, "skupine": {}, "pravno_potvrdeno": 0}
    uk_P, uk_Z = [], []
    for g, (izv, opseg) in PODRUCJE.items():
        Z = ref["skupine"][g]["zapisi"]
        P = [p for c in izlaz[izv]["clanci"].values() for p in c.get("pravila", []) if (p["clanak"], p["stavak"]) in opseg]
        s, d = usporedi(P, Z, MP)
        out["skupine"][g] = {"sazetak": s, "detalji": d}
        uk_P += P; uk_Z += [dict(o, id=f"{g}:{o['id']}") for o in Z]  # brojevi članaka se ne preklapaju među skupinama
    out["ukupno"] = usporedi(uk_P, uk_Z, MP)[0]
    integritet()
    if v11:
        out["dopuna_odluka"] = {"datoteka": "oznake/v1/odluke_suca_v1_1.json", "sha256": sha(D / "odluke_suca_v1_1.json")}
    p = D / ("mjerenje_v22_ref_v1_1.json" if v11 else "mjerenje_v22_ref_v1.json")
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out, sha(p)


if __name__ == "__main__":
    o, s = main("--v1.1" in sys.argv)
    K = ["oznaka", "oznaka_JASAN", "zapisa_modula", "tocno_prihvaceno", "tocno_uz_pravilo_granularnosti", "pogresno_prihvaceno", "pravilno_na_pregled",
         "nepotrebno_na_pregled", "pregled_bez_oznake", "propusteno", "preciznost_prihvacenih", "pokrivenost_prihvacanja_od_JASAN", "pokrivenost_izdvajanja"]
    for g, v in list(o["skupine"].items()) + [("UKUPNO", {"sazetak": o["ukupno"]})]:
        print(g.ljust(20), " ".join(f"{k[:10]}={v['sazetak'][k]}" for k in K))
    print("determinizam", o["determinizam"], "sha", s)

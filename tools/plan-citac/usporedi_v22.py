#!/usr/bin/env python3
"""EKSPERIMENT v2.2: usporedba gramatike v2.2 sa svim razvojnim skupovima i regresije (v1 i v2.1 se ne mijenjaju).

Razvojni skupovi (svi su poznati razvoju v2.2, pa NISU dokaz generalizacije):
  - PPUG čl. 22./23.: zamrznuti usporednik ocijeni_neovisno.py + zamrznuto mapiranje v1 (kao u v2.1);
  - PPUG čl. 25./33.: oznake b47d15c3…, mapiranje_v2.json + dopuna mapiranje_v22.json;
  - UPU 1 čl. 14./24.: oznake 91d187e4… (slijepi test v2.1, sada razvojni), mapiranje_v2 + dopuna;
  - dodatak st. 2. čl. 22./23.: oznake 7e64ed66… (usporedi_dodatak.py, na izlazu v2.2);
  - UPU 2 čl. 38.–40.: vlastite oznake (ocijeni.py), mora ostati 92 / 0 / 7 / 0.
Razredi: točno prihvaćeno, pogrešno prihvaćeno, pravilno na pregled (oznaka PREGLED), nepotrebno na pregled (oznaka
JASAN), pregled bez oznake, propušteno, dodatni prijedlozi bez oznake (izvan označenih članaka).
"""
import copy, hashlib, json, re
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v22 as s22
import usporedi_v2 as U
import ocijeni as oc

M = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256((M / p).read_bytes()).hexdigest()
J = lambda p: json.loads((M / p).read_text(encoding="utf-8"))
OZNAKE = {"oznake/neovisno/neovisne_oznake_ppug_22_23.json": "b56057965c75f1434a4e9c7684eac1e86393994454787ab94b2f09681be660b5",
          "oznake/neovisno_cl25_33/neovisne_oznake_ppug_25_33.json": "b47d15c3f8d8005e53f9d1f44414155658177c30e16cf64e29a4f626f03c452d",
          "slijepo/ppug_krk/slijepi_v2/neovisne_oznake_upu1.json": "91d187e430c92fc74c8a9f8c8e655a04b3263108021ed5a38a32654150b30ee6",
          "oznake/dodatak_22_23/oznake_dodatak_st2.json": "7e64ed66b56c9ba317efd0f41eb7035163a5070907092dee44adb6881cb6a170",
          "oznake/dodatak_ppug_v22/oznake_ppug_20_38_39_50.json": "4955259790c4a8d146ad4887510fee735ca3b49873d7ea4eba6ffe11a340e883"}


def provjeri_integritet():
    U.provjeri_integritet()
    z2 = J("ZAMRZNUTO_v2.json")
    los = [p for g in ("kod", "mapiranje", "za_oznacavanje") for p, s in z2[g].items() if sha(p) != s]
    los += [p for p, s in OZNAKE.items() if sha(p) != s]
    if los:
        raise SystemExit("INTEGRITET NIJE POTVRĐEN: " + ", ".join(los))
    return {"ZAMRZNUTO_v1.json": "ispravno", "ZAMRZNUTO_v2.json": "ispravno (kod, mapiranje, tekst za označavanje)", "oznake": OZNAKE}


def mapa():
    MP = copy.deepcopy(J("oznake/neovisno_cl25_33/mapiranje_v2.json"))
    D = J("oznake/mapiranje_v22.json")
    MP["skupine"].update(D["skupine"]); MP["operatori"].update(D["operatori"])
    MP["parametri_v22"] = D["parametri"]
    for k, v in D["vrsta_gradevine_istoznacnice"].items():
        MP["vrsta_gradevine_istoznacnice"][k] = v
    return MP


def _gradevina(p, MP):
    vg = p["vrsta_gradevine"]
    sk = "+".join(vg["skupine"] or [])
    s = MP["skupine"].get(sk, sk)
    if vg["oblici"]:
        ob = "+".join(vg["oblici"]); s += " – " + MP["oblici"].get(ob, ob)
    if vg["stanje"]:
        s += MP["stanje"][vg["stanje"]]
    if vg["uz_podrum"]:
        s += MP["uz_podrum"]
    return s


def _zapis(p, MP, par, op, v, komp):
    jed = None if p["operator"] == "nije_propisano" else "opis" if p.get("vrijednost_vrsta") == "opis" else \
        "koeficijent" if p["jedinica"] is None and isinstance(v, (int, float)) else p["jedinica"]
    pars = [MP["parametri"].get(par, "?" + par)] + MP["parametri_v22"].get(par, [])
    return {"clanak": p["clanak"], "stavak": p["stavak"], "tocka": p["tocka"], "blok": p.get("blok"), "vrsta_gradevine": _gradevina(p, MP),
            "parametri": pars, "parametar": pars[0], "operator": MP["operatori"].get(op, op), "vrijednost": v, "jedinica": jed,
            "vrsta_pravila": p["vrsta_pravila"],
            "uvjet_tekst": " | ".join((p["uvjeti"] or []) + [x for x in (p.get("opseg"), p.get("referenca")) if x]),
            "status": "PREGLED" if any(q["status"] == "PREGLED" for q in komp) else "PRIJEDLOG",
            "razlog_kod": sorted({k for q in komp for k in q["razlog_kod"]}), "id": komp[0]["id"], "komponente": [q["id"] for q in komp],
            "izvorni_citat": p["izvorni_citat"]}


def u_zapise(pravila, MP):
    out, iv = [], {}
    for p in pravila:
        if p.get("interval"):
            iv.setdefault((p["clanak"], p["stavak"], p.get("blok"), p["tocka"], p["alineja"], p["interval"]), []).append(p); continue
        out.append(_zapis(p, MP, p["parametar"], p["operator"], p["vrijednost"], [p]))
    for k, ps in iv.items():
        mn = next((q for q in ps if q["operator"] == ">="), None); mx = next((q for q in ps if q["operator"] == "<="), None)
        if mn and mx and len(ps) == 2:
            out.append(_zapis(mn, MP, k[5], "izmedju", f"{mn['vrijednost']:g}–{mx['vrijednost']:g}", [mn, mx]))
        else:
            out += [_zapis(q, MP, q["parametar"], q["operator"], q["vrijednost"], [q]) for q in ps]
    return out


_nv = lambda x: re.sub(r"\s+", " ", str(x)).strip().lower().replace("–", "-")


def razlike(z, o, MP):
    r = [k for k in ("clanak", "stavak", "tocka", "operator", "jedinica", "vrsta_pravila") if z[k] != o[k]]
    if o["parametar"] not in z["parametri"]:
        r.append("parametar")
    dozv = MP["vrsta_gradevine_istoznacnice"].get(z["vrsta_gradevine"], [])
    dozv = {z["vrsta_gradevine"]} | ({dozv} if isinstance(dozv, str) else set(dozv))
    bez = z["vrsta_gradevine"].replace(MP["uz_podrum"], "")
    if MP["uz_podrum"] not in o["vrsta_gradevine"]:
        d2 = MP["vrsta_gradevine_istoznacnice"].get(bez, [])
        dozv |= {bez} | ({d2} if isinstance(d2, str) else set(d2))
    if o["vrsta_gradevine"] not in dozv:
        r.append("vrsta_gradevine")
    a, b = z["vrijednost"], o["vrijednost"]
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if abs(a - b) > 1e-9:
            r.append("vrijednost")
    else:
        A = {_nv(a), _nv(MP["vrijednosti"].get(a, a)) if isinstance(a, str) else _nv(a)}
        B = {_nv(b), _nv(MP["vrijednosti"].get(b, b)) if isinstance(b, str) else _nv(b)}
        if not A & B:
            r.append("vrijednost")
    dij = [re.sub(r"^iznimno,?\s*", "", d.strip(), flags=re.I) for d in (o["uvjet_primjene"] or "").split("; ") if d.strip()]
    dij = [d for d in dij if d]
    if dij:
        if not all(_nv(d) in _nv(z["uvjet_tekst"]) for d in dij):
            r.append("uvjet")
    elif z["uvjet_tekst"]:
        r.append("uvjet")
    return r


def granularnost(z, o, MP):
    """Razlike koje su samo pitanje granularnosti oznaka (mapiranje_v22.json: pravila_granularnosti); None ako ih nema."""
    r = razlike(z, o, MP)
    if not r:
        return None
    pr = []
    for f in list(r):
        if f == "tocka" and {z["tocka"], o["tocka"]} == {"-", None}:
            pr.append("GRANICA_ALINEJE"); r.remove(f)
        elif f == "vrsta_pravila" and {z["vrsta_pravila"], o["vrsta_pravila"]} == {"ALTERNATIVA", "UVJETNO"} and z["uvjet_tekst"]:
            pr.append("ALTERNATIVA_UZ_UVJET"); r.remove(f)
        elif f == "operator" and {z["operator"], o["operator"]} == {"=", "dopustenje"} and z["jedinica"] == "opis":
            pr.append("OPISNA_JEDNAKOST_ILI_DOPUSTENJE"); r.remove(f)
    return pr if not r else None


def usporedi_oznake(pravila, Z, MP):
    zap = u_zapise(pravila, MP)
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
            R["pregled"].append({"id": z["id"], "oznaka": o and o["id"], "jednoznacnost_oznake": o and o["jednoznacnost"], "razlog_kod": z["razlog_kod"]})
        elif o is None:
            blize = min(((len(razlike(z, q, MP)), q["id"], razlike(z, q, MP)) for q in Z if q["clanak"] == z["clanak"]), default=None)
            R["pogresno"].append({"id": z["id"], "parametar": z["parametar"], "vrijednost": z["vrijednost"], "citat": z["izvorni_citat"],
                                  "najbliza_oznaka": blize and blize[1:]})
        else:
            R["tocno"].append({"id": z["id"], "oznaka": o["id"], "jednoznacnost_oznake": o["jednoznacnost"]})
    prop = []
    for i, o in enumerate(Z):
        if not uzeto[i]:
            bl = min(((len(razlike(z, o, MP)), z["id"], razlike(z, o, MP)) for z in zap if z["clanak"] == o["clanak"]), default=None)
            prop.append({"oznaka": o["id"], "parametar": o["parametar"], "jednoznacnost": o["jednoznacnost"], "najblizi_zapis": bl and bl[1:]})
    t, g = len(R["tocno"]), len(R["pogresno"])
    tg = len(R["tocno_uz_granularnost"])
    s = {"oznaka": len(Z), "zapisa_modula": len(zap), "tocno_prihvaceno": t, "tocno_uz_pravilo_granularnosti": tg, "pogresno_prihvaceno": g,
         "pravilno_na_pregled": sum(1 for x in R["pregled"] if x["oznaka"] and x["jednoznacnost_oznake"] == "PREGLED"),
         "nepotrebno_na_pregled": sum(1 for x in R["pregled"] if x["oznaka"] and x["jednoznacnost_oznake"] == "JASAN"),
         "pregled_bez_oznake": sum(1 for x in R["pregled"] if not x["oznaka"]), "propusteno": len(prop),
         "preciznost_prihvacenih_strogo": round(t / (t + tg + g), 3) if t + tg + g else None,
         "preciznost_prihvacenih": round((t + tg) / (t + tg + g), 3) if t + tg + g else None,
         "pokrivenost_izdvajanja": round((t + tg + sum(1 for x in R["pregled"] if x["oznaka"])) / len(Z), 3) if Z else None,
         "pokrivenost_prihvacanja": round((t + tg) / len(Z), 3) if Z else None,
         "udio_pregleda": round(len(R["pregled"]) / len(zap), 3) if zap else None}
    return s, dict(R, propusteno=prop)


def po_clanku(pravila, Z, MP, clanci):
    return {str(c): usporedi_oznake([p for p in pravila if p["clanak"] == c], [o for o in Z if o["clanak"] == c], MP)[0] for c in clanci}


def pokreni_ppug():
    return s22.strukturiraj(izdvoji_tekst(M / U.IZVOR, dio=1), None, "PPUG Krk")


def pokreni_upu1():
    return s22.strukturiraj(izdvoji_tekst(M / U.IZVOR, [14, 24], dio=2), None, "UPU 1 – Krk")


def dodatak(r):
    """Usporedba pravila st. 2. čl. 22./23. (v2.2) s dodatkom oznaka (po poljima, kao usporedi_dodatak.py)."""
    Z = J("oznake/dodatak_22_23/oznake_dodatak_st2.json")["zapisi"]
    MP = mapa()
    MP["parametri_v22"]["dopustenaGradnja"] = ["dopuštenost gradnje uz osnovnu građevinu"]
    pr = [p for k in ("22", "23") for p in r["clanci"][k]["pravila"] if p["stavak"] == 2]
    Zm = [dict(o, vrsta_gradevine=o["vrsta_gradevine"]) for o in Z]
    s, d = usporedi_oznake(pr, Zm, MP)
    return {"sazetak": s, "detalji": d, "napomena": "dodatak oznaka bilježi vrijednost dopuštenja gradnje drukčije (vrijednost/uvjet); vidi oznake/dodatak_22_23/IZVJESTAJ_dodatak.md"}


def dodatak_ppug(r):
    """Neovisna provjera prihvaćenih pravila v2.2 u neoznačenim člancima PPUG-a (čl. 20. st. 3, 38. st. 6, 39. st. 2,
    50. st. 4). Oznaka vrste »pomoćna građevina (uz građevinu …)«: zagrada opisuje uz koju se građevinu gradi i ne
    ulazi u usporedbu vrste (modul to bilježi u kontekstu članka)."""
    Z = [dict(o, vrsta_gradevine=re.sub(r"\s*\(uz građevin[^)]*\)", "", o["vrsta_gradevine"]))
         for o in J("oznake/dodatak_ppug_v22/oznake_ppug_20_38_39_50.json")["zapisi"]]
    opseg = {(20, 3), (38, 6), (39, 2), (50, 4)}
    pr = [p for k in ("20", "38", "39", "50") for p in r["clanci"][k]["pravila"] if (p["clanak"], p["stavak"]) in opseg]
    s, d = usporedi_oznake(pr, Z, mapa())
    return {"sazetak": s, "detalji": d}


def ostali(r, oznaceni):
    out = [{"clanak": p["clanak"], "stavak": p.get("stavak"), "blok": p.get("blok"), "tocka": p.get("tocka"), "alineja": p.get("alineja"), "parametar": p["parametar"],
            "operator": p.get("operator"), "vrijednost": p.get("vrijednost"), "uvjet": p.get("uvjet"), "skupine": (p.get("vrsta_gradevine") or {}).get("skupine"),
            "izvorni_citat": p.get("izvorni_citat", p.get("dokaz")), "gramatika": c.get("gramatika") or "obrasci v1"}
           for k, c in r["clanci"].items() if k not in oznaceni for p in c.get("pravila", []) if p["status"] == "PRIJEDLOG"]
    return {"prijedlog": len(out), "pravila": out,
            "napomena": "Prihvaćeni prijedlozi u neoznačenim člancima: nisu ocijenjeni; traže neovisno označavanje prije bilo kakve tvrdnje o točnosti."}


def sve():
    integ = provjeri_integritet()
    MP = mapa()
    r = pokreni_ppug(); r_b = pokreni_ppug()
    u1 = pokreni_upu1(); u1_b = pokreni_upu1()
    det = {"ppug": [U.sha_obj(r), U.sha_obj(r_b)], "upu1": [U.sha_obj(u1), U.sha_obj(u1_b)]}
    det["isto"] = det["ppug"][0] == det["ppug"][1] and det["upu1"][0] == det["upu1"][1]
    out = {"verzija": "v2.2", "integritet": integ, "determinizam": det,
           "izlazi": {"izlaz/ppug_v2_2.json": s22.zapisi_json(r, M / "izlaz/ppug_v2_2.json"),
                      "izlaz/upu1_14_24_v2_2.json": s22.zapisi_json(u1, M / "izlaz/upu1_14_24_v2_2.json")}}
    out["cl22_23"] = U.usporedi_22_23(r)
    Z25 = J("oznake/neovisno_cl25_33/neovisne_oznake_ppug_25_33.json")["zapisi"]
    P25 = [p for k in ("25", "33") for p in r["clanci"][k]["pravila"]]
    out["cl25_33"] = {"po_clanku": po_clanku(P25, Z25, MP, (25, 33)), "ukupno": usporedi_oznake(P25, Z25, MP)[0],
                      "detalji": usporedi_oznake(P25, Z25, MP)[1]}
    Zu = J("slijepo/ppug_krk/slijepi_v2/neovisne_oznake_upu1.json")["zapisi"]
    Pu = [p for c in u1["clanci"].values() for p in c.get("pravila", [])]
    out["upu1_14_24"] = {"po_clanku": po_clanku(Pu, Zu, MP, (14, 24)), "ukupno": usporedi_oznake(Pu, Zu, MP)[0], "detalji": usporedi_oznake(Pu, Zu, MP)[1],
                         "oznake_izvan_rjecnika_parametara": sum(1 for o in Zu if str(o["parametar"]).startswith("drugo:"))}
    out["dodatak_22_23"] = dodatak(r)
    out["dodatak_ppug_20_38_39_50"] = dodatak_ppug(r)
    out["ostali_clanci_ppug"] = ostali(r, ("22", "23", "25", "33"))
    ozn = {(x["clanak"], x["stavak"]) for x in out["ostali_clanci_ppug"]["pravila"]}
    out["ostali_clanci_ppug"]["bez_ikakve_oznake"] = sorted(ozn - {(20, 3), (38, 6), (39, 2), (50, 4)})
    d2 = J("izlaz/upu2_kornic_sn_19_2016.json")
    r2 = s22.strukturiraj(d2, None, "UPU 2 – Kornić")
    out["upu2"] = {"cl38_40_vlastite_oznake": oc.ocijeni({"clanci": {k: v for k, v in r2["clanci"].items() if k in ("38", "39", "40")}}, J("oznake/upu2_cl38_40.json"))[0],
                   "prijedlozi_gramatike_v22_drugdje": sum(1 for x in ostali(r2, ("38", "39", "40"))["pravila"] if x["gramatika"] == "gramatika-v2.2")}
    out["pravno_potvrdeno"] = 0
    out["napomena"] = "Svi skupovi su razvojni za v2.2; generalizacija se mjeri tek slijepim testom na drugom planu."
    provjeri_integritet()
    return out


if __name__ == "__main__":
    o = sve()
    print("izlaz/usporedba_v2_2.json", s22.zapisi_json(o, M / "izlaz/usporedba_v2_2.json"))
    print(json.dumps({"determinizam": o["determinizam"]["isto"], "22_23": o["cl22_23"]["v2_1"], "promjene_22_23": o["cl22_23"]["promjene_po_oznaci"],
                      "25_33": o["cl25_33"]["po_clanku"], "upu1": o["upu1_14_24"]["po_clanku"], "dodatak": o["dodatak_22_23"]["sazetak"],
                      "ostali_prijedlog": o["ostali_clanci_ppug"]["prijedlog"], "ostali_bez_oznake": o["ostali_clanci_ppug"]["bez_ikakve_oznake"],
                      "dodatak_ppug": o["dodatak_ppug_20_38_39_50"]["sazetak"], "upu2": o["upu2"]}, ensure_ascii=False, indent=1))

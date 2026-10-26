#!/usr/bin/env python3
"""HIBRIDNI ČITAČ v1 – mjerenje na razvojnim skupovima (i, nakon zamrzavanja, na slijepom planu).

    python3 hibrid/mjeri.py razvoj            # → hibrid/razvoj/mjerenje_hibrid.json + tablica
Za svaki skup: generator (zamrznuti JSON) → provjera → usporedba s istim referentnim oznakama kao deterministička v2.6
(strogo i semantički), uz razine kandidata (izdvojeno / tehnički provjereno / automatski prihvaćeno / za pregled / odbijeno)
i stopu pogrešaka među tehnički provjerenima (svi tehnički provjereni tretirani kao prihvaćeni).
"""
import hashlib, json, sys, time
from pathlib import Path

H = Path(__file__).resolve().parent
M = H.parent
sys.path.insert(0, str(M)); sys.path.insert(0, str(M / "oznake/v1")); sys.path.insert(0, str(H))
import provjera as P
import usporedba as UH
import izvor_v26 as I
import usporedi_v2 as U2
import strukturiraj_v26 as s26

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
KRK_PODRUCJE = {"ppug_krk": {(22, 1), (22, 2), (23, 1), (23, 2), (25, 1), (25, 2), (33, 1), (33, 2), (33, 3), (33, 4), (20, 3), (38, 6), (39, 2), (50, 4)},
                "upu1_krk": {(14, None), (24, None)}}
KRK_SKUPINE = {"ppug_krk": ("G1_ppug_22_23", "G2_ppug_25_33", "G3_ppug_20_38_39_50"), "upu1_krk": ("G4_upu1_14", "G5_upu1_24")}
SKUPOVI = {
    "ppug_krk": (lambda: I.ucitaj(M / U2.IZVOR, dio=1), [20, 22, 23, 25, 33, 38, 39, 50]),
    "upu1_krk": (lambda: I.ucitaj(M / U2.IZVOR, dio=2), [14, 24]),
    "nv": (lambda: I.ucitaj(M / "slijepo/novi_vinodolski/nv_upu_sn_32_2026.html"), [19, 20, 23, 24]),
    "crikvenica": (lambda: I.ucitaj(M / "slijepo/crikvenica_centar_1/crikvenica_upu_centar_1.html"), [23, 24, 25, 26]),
    "upu2_kornic": (lambda: json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8")), [38, 39, 40]),
}


def oznake(skup):
    if skup in KRK_SKUPINE:
        ref = json.loads((M / "oznake/v1/referenca_v1_2.json").read_text(encoding="utf-8"))
        return [dict(o, id=f"{g}:{o['id']}") for g in KRK_SKUPINE[skup] for o in ref["skupine"][g]["zapisi"]]
    if skup == "nv":
        return json.loads((M / "slijepo/novi_vinodolski/neovisne_oznake.json").read_text(encoding="utf-8"))["zapisi"]
    if skup == "crikvenica":
        return json.loads((M / "slijepo/crikvenica_centar_1/neovisne_oznake.json").read_text(encoding="utf-8"))["zapisi"]
    return None  # Kornić: referenca je u formatu v1 s vlastitim šiframa i nije neovisna → samo razine kandidata


def u_opsegu(skup, x):
    return skup not in KRK_PODRUCJE or (x["clanak"], x["stavak"]) in KRK_PODRUCJE[skup]


def clanci(skup, d=None):
    f, br = SKUPOVI[skup]
    d = d or f()
    C = {}
    for k, c in d["clanci"].items():
        if "#" in k or c["broj"] not in br:
            continue
        C[c["broj"]] = {"broj": c["broj"], "tekst": c["tekst"], "naslov": c.get("naslov_clanka"), "kljuc": k}
    return d, C


def mjeri_skup(skup, gen_json, d=None, Z=None, br=None):
    if br:
        SKUPOVI.setdefault(skup, (None, br))
    d, C = clanci(skup, d)
    G = json.loads(Path(gen_json).read_text(encoding="utf-8"))
    t0 = time.time()
    K = P.provjeri_sve(G["kandidati"], C)
    t_prov = time.time() - t0
    for i, k in enumerate(K):
        k["id"] = f"H{i + 1:03d}"
    Kin = [k for k in K if u_opsegu(skup, {"clanak": k.get("clanak"), "stavak": k.get("stavak")})]
    out = {"skup": skup, "generator": G.get("metapodaci"), "sha256_generatora": sha(gen_json), "razine": P.razine(Kin),
           "razlozi_pregleda": {}, "vrijeme_provjere_s": round(t_prov, 3), "kandidati": K}
    for k in Kin:
        for kod, _ in k["_razlozi"]:
            out["razlozi_pregleda"][kod] = out["razlozi_pregleda"].get(kod, 0) + 1
    Z = Z if Z is not None else oznake(skup)
    if Z is not None:
        dd = dict(d, clanci={k: d["clanci"][c["kljuc"]] for k, c in ((c["kljuc"], c) for c in C.values())})
        r6 = s26.strukturiraj(dd, None, skup)
        import mjeri_v26 as X6
        MP = X6.mapa26()
        P6 = [p for c in r6["clanci"].values() for p in c.get("pravila", []) if u_opsegu(skup, p)]
        K6 = UH.iz_v26(P6, MP)
        Kh = [x for x in UH.iz_hibrida(Kin)]
        Kt = [x for x in UH.iz_hibrida(Kin, samo_tehnicki=True)]
        out["usporedba"] = {}
        for nacin in ("strogo", "semanticki"):
            s6, d6 = UH.usporedi(K6, Z, nacin)
            sh, dh = UH.usporedi(Kh, Z, nacin)
            st, dt = UH.usporedi(Kt, Z, nacin)
            out["usporedba"][nacin] = {"v2.6": {"sazetak": s6, "pogresno": d6["pogresno"]},
                                       "hibrid": {"sazetak": sh, "pogresno": dh["pogresno"], "detalji": dh},
                                       "hibrid_tehnicki_kao_prihvaceni": {"sazetak": st, "pogresno": dt["pogresno"]}}
    return out


def main(argv):
    rez = {}
    for skup in SKUPOVI:
        g = H / "razvoj" / f"gen_{skup}.json"
        if g.exists():
            rez[skup] = mjeri_skup(skup, g)
    p = H / "razvoj" / "mjerenje_hibrid.json"
    p.write_text(json.dumps(rez, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return rez, sha(p)


def ispis(rez):
    for skup, x in rez.items():
        print(f"== {skup}  razine={x['razine']}")
        print("   razlozi:", dict(sorted(x["razlozi_pregleda"].items(), key=lambda kv: -kv[1])))
        for nacin, u in (x.get("usporedba") or {}).items():
            for var in ("v2.6", "hibrid", "hibrid_tehnicki_kao_prihvaceni"):
                s = u[var]["sazetak"]
                print(f"   {nacin:10s} {var:31s} prih={s['prihvaceno']:3d} točno={s['tocno_prihvaceno']:3d} pogr={s['pogresno_prihvaceno']:2d} "
                      f"pregled={s['na_pregledu']:3d} (s oznakom {s['pregled_s_oznakom']}) prop={s['propusteno']:3d} prec={s['preciznost_prihvacenih']} "
                      f"JASAN={s['pokrivenost_JASNIH']}")
                for e in u[var]["pogresno"] if var == "hibrid" else []:
                    print("        POGR", e["id"], e["kandidat"]["parametar"], e["kandidat"]["vrijednost"], e["kandidat"]["vrsta_gradevine"], "|", e["najbliza_oznaka"])


if __name__ == "__main__":
    r, s = main(sys.argv[1:])
    ispis(r)
    print("sha", s)

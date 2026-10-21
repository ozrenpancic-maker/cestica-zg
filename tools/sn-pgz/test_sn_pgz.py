import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
FIX = """Godina XXVIII. - broj 3. Petak, 14. veljače 2020.

OPĆINA PUNAT
5.
Na temelju članka 109. donosi
ODLUKU
o donošenju II. izmjena i dopuna Urbanističkog plana uređenja (UPU3) naselja Punat
I. TEMELJNE ODREDBE
Članak 1.
Donosi se Odluka.
Članak 12.
Članak 44. mijenja se i glasi:
»(1) Stambene se građevine strukturiraju.«
Članak 15.
U članku 46a. stavku 1. točka 4. mijenja se i glasi:
»4. Uređenje građevne čestice - obavezna je površina zelenila 40%.«
Članak 16.
Iza članka 28. dodaje se novi članak 28.a koji glasi:
»Članak 28a. Tekst.«
Članak 20.
U članku 50.d stavku 1. riječi: »8614/1« brišu se.
Članak 38.
Naslov iznad članka 100. i članak 100. brišu se.
Članak 40.
Ova Odluka stupa na snagu osmog dana.
"""
class T(unittest.TestCase):
    def test_zaglavlje(self):
        z = S.zaglavlje(S.u_tekst(FIX)); self.assertEqual((z["broj"], z["godina_izdanja"], z["datum"], z["stavka"], z["tijelo"]), (3, 28, "2020-02-14", 5, "Općina Punat"))
    def test_vrste(self):
        for n, v in [("Odluka o izradi III. Izmjena i dopuna UPU 3", "izrada"), ("Odluka o donošenju II. Izmjena i dopuna UPU 3", "izmjene"),
                     ("Odluka o donošenju UPU 3", "donosenje"), ("Odluka o donošenju PPUO Punat (pročišćeni tekst)", "procisceni"),
                     ("Odluka o stavljanju izvan snage UPU 4", "izvan_snage"), ("Vjerodostojno tumačenje odredbi UPU 3", "tumacenje"), ("Nešto drugo", "nepoznato")]:
            self.assertEqual(S.vrsta(n), v, n)
    def test_operacije(self):
        L = S.loza([{"id": 1, "datum": "2020-02-14", "vrsta": "izmjene", "tekst": S.u_tekst(FIX)}])
        self.assertEqual(L["44"]["stanje"], "cijeli_tekst_poznat")
        self.assertEqual(L["46a"]["stanje"], "osnova_potrebna"); self.assertEqual((L["46a"]["operacije"][0]["stavak"], L["46a"]["operacije"][0]["tocka"]), ("1", "4"))
        self.assertEqual(L["28a"]["stanje"], "cijeli_tekst_poznat"); self.assertEqual(L["100"]["stanje"], "izbrisan")
        self.assertEqual(L["50d"]["operacije"][0]["vrsta"], "brisanje_rijeci")
    def test_kandidati_su_samo_strojni(self):
        k = S.kandidati("Koeficijent izgrađenosti građevne čestice (kig) iznosi 0,25, visina 9,0 m, zelenila 40%, 150 m2")
        self.assertTrue({"kig", "duljina_m", "postotak", "povrsina_m2"} <= {x["vrsta"] for x in k}); self.assertTrue(all(x["status"] == "strojno" for x in k))
    def test_baza_prema_shemi(self):
        baza = json.load(open(os.path.join(ROOT, "data", "pravila-sn", "punat-upu3.json"), encoding="utf-8"))
        try: import jsonschema
        except ImportError: self.skipTest("jsonschema nije instaliran")
        jsonschema.validate(baza, json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shema.json"), encoding="utf-8")))
    def test_baza_pravila_nisu_automatska(self):
        baza = json.load(open(os.path.join(ROOT, "data", "pravila-sn", "punat-upu3.json"), encoding="utf-8"))
        self.assertTrue(all(r["status_primjene"] == "ne_primjenjivati_automatski" and r["zona"]["potvrda"] == "nepotvrdeno" for r in baza["pravila"]))
        self.assertTrue(all(r["izvor"]["citat"] and r["izvor"]["url"] and r["izvor"]["clanak_plana"] for r in baza["pravila"]))
    def test_citati_prema_stvarnom_tekstu_ako_postoji(self):
        p = os.environ.get("SN_TEKST_41087"); p16 = os.environ.get("SN_TEKST_33933")
        if not p or not os.path.exists(p): self.skipTest("SN_TEKST_41087 nije zadan")
        if not p16 or not os.path.exists(p16): self.skipTest("SN_TEKST_33933 nije zadan")
        import provjeri_citate as P
        baza = json.load(open(os.path.join(ROOT, "data", "pravila-sn", "punat-upu3.json"), encoding="utf-8"))
        n, lose = P.provjeri(baza, {41087: S.u_tekst(open(p, encoding="utf-8").read()), 33933: S.u_tekst(open(p16, encoding="utf-8").read())}); self.assertEqual(lose, [])
    def test_46abc_osnovne_vrijednosti_i_vrsta_gradnje(self):
        baza = json.load(open(os.path.join(ROOT, "data", "pravila-sn", "punat-upu3.json"), encoding="utf-8"))
        R = {r["id"]: r for r in baza["pravila"]}
        self.assertEqual((R["p3-46a-cestica-min"]["vrijednost"], R["p3-46b-cestica-min"]["vrijednost"], R["p3-46c-cestica-min"]["vrijednost"]), (450, 225, 150))
        self.assertEqual(R["p3-46a-zelenilo"]["vrsta_gradnje"], "slobodnostojeca")
        self.assertTrue(all(r["status_primjene"] == "ne_primjenjivati_automatski" and r["zona"]["potvrda"] == "nepotvrdeno" for r in baza["pravila"]))
        self.assertTrue(all(r["izvor"]["odluka_id"] in (33933, 41087) for r in baza["pravila"]))
    def test_zlatni_skupovi_i_mjerenje(self):
        import mjeri
        for ime in ("punat-upu3-2020.json", "punat-upu3-2016.json"):
            z = json.load(open(os.path.join(ROOT, "tests", "zlatni", ime), encoding="utf-8"))
            self.assertEqual(z["broj_izmjena"], len(z["izmjene"]))
            g = [x for x in z["izmjene"] if x["ucinak"] != "NEJASNO"]
            r = mjeri.mjeri(g, g)  # savršen izlaz mora dati 1.0 na svim mjerama
            for k, v in r.items(): self.assertEqual((v["precision"], v["recall"]), (1.0, 1.0), (ime, k))
            lose = [dict(x, ucinak="ADD" if x["ucinak"] != "ADD" else "DELETE") for x in g]
            r2 = mjeri.mjeri(lose, g)
            self.assertEqual(r2["clanak"]["recall"], 1.0); self.assertLess(r2["ucinak"]["recall"], 1.0)
            self.assertLess(mjeri.mjeri(g[:-5], g)["clanak"]["recall"], 1.0)
    def test_2020_zamrznut_hash(self):
        import hashlib
        z = json.load(open(os.path.join(ROOT, "tests", "zlatni", "punat-upu3-2020.json"), encoding="utf-8"))
        self.assertEqual(z["sha256_izmjena"], hashlib.sha256(json.dumps(z["izmjene"], ensure_ascii=False, sort_keys=True).encode()).hexdigest())
if __name__ == "__main__": unittest.main()


def test_identitet_zlatni_zamrznut():
    import json, hashlib, os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mjeri_identitet as M
    z = json.load(open(M.Z, encoding="utf-8"))
    assert z["sha256"] == hashlib.sha256(json.dumps([z["veze"], z["parovi"]], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    assert sum(l["ocekivanje"] == "MUST_LINK" for l in z["veze"]) >= 30
    assert sum(l["ocekivanje"] == "MUST_NOT_LINK" for l in z["veze"]) >= 10
    assert all(l["dokaz"].get("clanak_izvoza") for l in z["veze"])
    # savršena predikcija: nula zabranjenih; zabranjena veza (34173→PPU Punat) mora biti uhvaćena
    pred = {"veze": [{"odluka_id": l["odluka_id"], "opcina": l["plan"]["opcina"], "vrsta": l["plan"]["vrsta"], "broj": l["plan"]["broj"], "veza": l["veza"]}
                     for l in z["veze"] if l["ocekivanje"] == "MUST_LINK"]}
    r = M.mjeri(pred, z); assert r["zabranjeni_spojevi"] == 0 and r["identitet_recall"] == 1.0
    pred["veze"].append({"odluka_id": "34173", "opcina": "Punat", "vrsta": "PPU", "broj": None, "veza": "ADOPTS"})
    assert M.mjeri(pred, z)["zabranjeni_spojevi"] == 1


def test_identitet_v2_metrike_i_generacije():
    import json, sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mjeri_identitet as M
    z = json.load(open(M.Z, encoding="utf-8")); ref = json.load(open(M.REF, encoding="utf-8"))
    assert sum(e.get("clanak_izvoza") is not None for g in ref["generacije"] for e in g["dokazi"]) == sum(len(g["dokazi"]) for g in ref["generacije"])
    assert len(ref["radnje"]) == 9
    reg = [{"odluka_id": l["odluka_id"], "opcina": l["plan"]["opcina"], "vrsta": l["plan"]["vrsta"], "broj": l["plan"]["broj"], "veza": l["veza"], "auto_merge_allowed": False, "generation_id": "UNDETERMINED"}
           for l in z["veze"] if l["ocekivanje"] == "MUST_LINK"]
    # UNKNOWN je u izvozu, ali se ne računa kao točna vrsta veze
    r = M.mjeri2({"veze": reg}, z, ref)
    assert r["identity_exported_recall"] == 1.0 and r["unknown_count"] == 4 and r["generation_coverage"] == 0.0
    assert r["LEGACY_relation_type_accuracy"] == 1.0   # gold-UNKNOWN zapisi nisu u nazivniku
    reg.append({"odluka_id": "14783", "opcina": "Krk", "vrsta": "UPU", "broj": "1", "veza": "UNKNOWN", "auto_merge_allowed": False, "generation_id": "UNDETERMINED"})
    # pogrešno spajanje gen A i B i generacija nedokazanom slučaju moraju biti uhvaćeni
    for p in reg:
        if p["odluka_id"] in ("14783", "28241"): p["generation_id"] = "gen-B"
        if p["odluka_id"] == "35506": p["generation_id"] = "gen-B"
    r = M.mjeri2({"veze": reg}, z, ref)
    assert r["gen_A_B_spojene"] == 1 and r["generacija_bez_dokaza"] == 1
    for p in reg:
        if p["veza"] == "UNKNOWN": p["auto_merge_allowed"] = True
    assert M.mjeri2({"veze": reg}, z, ref)["auto_merge_bez_dokaza"] >= 4


def test_identitet_v0161_metrike_brojnik_nazivnik():
    import json, sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mjeri_identitet as M
    z = json.load(open(M.Z, encoding="utf-8")); ref = json.load(open(M.REF, encoding="utf-8"))
    reg = [{"odluka_id": l["odluka_id"], "opcina": l["plan"]["opcina"], "vrsta": l["plan"]["vrsta"], "broj": l["plan"]["broj"], "veza": l["veza"],
            "evidence_type": "SHARED_FOOTPRINT_HEURISTIC" if l["veza"] == "UNKNOWN" else "EXPLICIT_PLAN_NUMBER", "auto_merge_allowed": False, "generation_id": "UNDETERMINED"}
           for l in z["veze"] if l["ocekivanje"] == "MUST_LINK"]
    r = M.mjeri3({"veze": reg}, z, ref)
    assert r["M_identity_exported_recall"]["brojnik"] == r["M_identity_exported_recall"]["nazivnik"] == 38
    assert r["M_identity_resolved_recall"]["brojnik"] == 34 and r["M_identity_resolved_recall"]["izvor"] == "REGISTAR"   # četiri heuristička nisu "resolved"
    assert r["M_identity_resolved_exported_recall"]["nazivnik"] == 34 and r["M_generation_undetermined_ids"] == ["32508", "42442", "35506", "39364"]
    assert r["M_relation_type_coverage"]["nazivnik"] == 34 and r["M_relation_type_accuracy_all"]["vrijednost"] == 1.0
    assert r["M_generation_accuracy"]["vrijednost"] == "N/A"       # premalo referentnih oznaka
    for p in reg:                                                      # UNKNOWN koji je u izvozu ne smije povećati točnost
        if p["veza"] == "UNKNOWN": p["veza"] = "UNKNOWN"
    ref_pov = json.load(open(M.REF, encoding="utf-8"))
    assert [p["legal_status"] for p in ref_pov["pravni_status"]] == ["SUPERSEDED", "UNKNOWN"]


def test_referenca_generacija_konzistentna():
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import validiraj_referencu as V, json, copy
    o = V.validiraj(); assert o["greske"] == [], o["greske"]
    assert o["lanci_iste_generacije_L1"] == ["MAL-PPU#G1", "VRB-PPU#G1", "VRB-UPU1#G1"]
    r = json.load(open(os.path.join(V.B, "generacije-baska-malinska-vrbnik-v1.json"), encoding="utf-8"))
    # negativni test validatora: nedokazan dokument s generacijom mora biti uhvaćen
    r2 = copy.deepcopy(r); r2["slucajevi"][0]["dokumenti"][3]["generation_ref"] = "MAL-PPU#G1"
    assert any("nedokazan dokument ima generaciju" in g for g in V.validiraj(r2)["greske"])
    # SAME_GENERATION par s različitim lancem mora biti uhvaćen
    r3 = copy.deepcopy(r); r3["slucajevi"][0]["dokumenti"][2]["dokazi"][0]["sn_navodi_u_citatu"] = ["99/99"]
    assert any("zajedničkog broja SN" in g for g in V.validiraj(r3)["greske"])

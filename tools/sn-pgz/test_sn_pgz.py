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
if __name__ == "__main__": unittest.main()

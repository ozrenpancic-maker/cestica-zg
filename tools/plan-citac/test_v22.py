"""Testovi v2.2 (morfologija, vrste građevina, kontekst, obuhvat, logika uvjeta, regresije). v1 i v2.1 testovi ostaju."""
import unittest
from citac_tekst import izdvoji_tekst
import morfologija_hr as mf
import vrste_gradevina as vg
import gramatika_v22 as g
import strukturiraj_v2 as s21
import strukturiraj_v22 as s22
import usporedi_v22 as U

IZ = U.M / U.U.IZVOR
_C = {}


def ppug():
    if "p" not in _C:
        _C["p"] = U.pokreni_ppug()
    return _C["p"]


def upu1():
    if "u" not in _C:
        _C["u"] = U.pokreni_upu1()
    return _C["u"]


class Morfologija(unittest.TestCase):
    def test_padezi_jednina_mnozina(self):
        for a, b in [("građevina", "građevinama"), ("građevine", "građevinom"), ("kuća", "kućama"), ("stambena", "stambenih"), ("hotel", "hotela"),
                     ("pomoćne", "pomoćnih"), ("višeobiteljsku", "višeobiteljske")]:
            self.assertEqual(mf.osnova(a), mf.osnova(b), (a, b))

    def test_razlicite_rijeci_ostaju_razlicite(self):
        self.assertNotEqual(mf.osnova("kuća"), mf.osnova("kat"))
        self.assertNotEqual(mf.osnova("građevna"), mf.osnova("građevinska"))   # terminološka razlika se ne briše

    def test_izraz_u_tekstu(self):
        self.assertEqual(mf.nadji("sportsko-rekreacijska građevina", "dopušteno je graditi sportsko-rekreacijske građevine uz")[0][2],
                         "sportsko-rekreacijske građevine")

    def test_sucelje_ne_pretpostavlja(self):
        self.assertIsNone(mf.Osnove().ista_lema("i", "u"))


class VrsteGradevina(unittest.TestCase):
    def test_kategorije(self):
        for t, k in [("za izgradnju stambenih građevina", ("stamb",)), ("Obiteljske/višeobiteljske kuće koje", ("obit", "visobit")),
                     ("rekonstrukcija hotela", ("hotel",)), ("pomoćne građevine mogu se graditi", ("pomocna",)),
                     ("građevine gospodarske namjene", ("gospodarska",)), ("poljoprivredne gospodarske građevine", ("poljoprivredna",))]:
            self.assertEqual(vg.prepoznaj(t)["kodovi"], k, t)

    def test_kombinirana_namjena(self):
        self.assertTrue(vg.prepoznaj("stambene i poslovne građevine")["kombinirano"])
        self.assertTrue(vg.prepoznaj("stambeno-poslovnih građevina")["kombinirano"])

    def test_strogi_kontekst_ne_uzima_usputni_spomen(self):
        self.assertIsNone(g.skupina_strogo("U zoni moguća je izgradnja otvorenih igrališta, sportskih dvorana i ostalih pomoćnih građevina"))
        self.assertEqual(g.skupina_strogo("dopušteno je graditi sportsko-rekreacijske građevine uz slijedeće granične uvjete"), ("sportsko_rekreacijska",))
        self.assertEqual(g.skupina_strogo("Pomoćne građevine grade se kao jednoetažne"), ("pomocna",))


class Kontekst(unittest.TestCase):
    def nadji(self, cl, par, **kw):
        return [p for p in upu1()["clanci"][str(cl)]["pravila"] if p["parametar"] == par and all(p.get(k) == v for k, v in kw.items())]

    def test_blokovi_redom(self):
        t = "Uvod: 1. oblik čestice - a. 2. namjena - b. 3. veličina - c. točke 5.1. Uvjeti"
        self.assertEqual([b for b, _ in g.blokovi(t)], [None, 1, 2, 3])

    def test_blok_pomocnih_gradevina(self):
        p = self.nadji(24, "tlMax")[0]
        self.assertEqual((p["vrsta_gradevine"]["skupine"], p["blok"], p["vrijednost"]), (["pomocna"], 7, 50.0))
        self.assertEqual(self.nadji(24, "kig")[0]["vrsta_gradevine"]["skupine"], ["hotel"])

    def test_iznimni_dio_clanka(self):
        p = self.nadji(14, "tlMax")[0]
        self.assertEqual(p["vrsta_pravila"], "IZNIMKA")
        self.assertIn("k.č 3932/1", p["uvjet"])
        self.assertIn("KATASTARSKA_CESTICA", [o["vrsta"] for o in p["prostorni_obuhvat"]])
        # iznimka ne prelazi na pravila prije nje
        self.assertNotIn("IZNIMKA", [x["vrsta_pravila"] for x in self.nadji(14, "kig")])

    def test_zona_kao_obuhvat_ne_kao_primjenjivost(self):
        p = self.nadji(14, "minC")[0]
        self.assertEqual(p["prostorni_obuhvat"][0]["vrsta"], "ZONA_PLANA")
        self.assertEqual(p["primjenjivost_na_lokaciju"], "NIJE_UTVRĐENA")

    def test_iznimna_alineja_nasljeduje_zonu(self):
        p = next(p for p in ppug()["clanci"]["20"]["pravila"] if p["parametar"] == "regulacija" and p["vrijednost"] == 4.0)
        self.assertEqual(p["vrsta_pravila"], "IZNIMKA"); self.assertIn("povijesnih graditeljskih cjelina", p["uvjet"])

    def test_alineja_s_velikim_slovom_odvojena(self):
        p = next(p for p in ppug()["clanci"]["50"]["pravila"] if p["parametar"] == "regulacija" and p["vrijednost"] == 4.0)
        self.assertEqual(p["vrsta_pravila"], "IZNIMKA")

    def test_nepouzdana_struktura_clanka(self):
        c = ppug()["clanci"]["56"]
        self.assertTrue(c["pravila"]) ; self.assertTrue(all(p["status"] == "PREGLED" for p in c["pravila"]))
        self.assertIn("STRUKTURA_CLANKA_NEPOUZDANA", [x.get("razlog_kod") for x in c["pregled"]])


class Oblici(unittest.TestCase):
    def test_ne_moze_biti_manja_i_izostavljeni_predmet(self):
        z, ost, rz, _ = g.odredba("Udaljenost građevine osnovne namjene od regulacijskog pravca za ostale (pristupne) ceste i ulice ne može biti manja od 4,0 m, a za razvrstane ceste ne može biti manja od 6,0 m.", {"skupine": ("hotel",)})
        self.assertEqual([(x["parametar"], x["operator"], x["vrijednost"], x["uvjeti"]) for x in z],
                         [("regulacija", ">=", 4.0, ["za ostale (pristupne) ceste i ulice"]), ("regulacija", ">=", 6.0, ["za razvrstane ceste"])])
        self.assertEqual(ost, [])

    def test_kis_iskoristenosti_i_podrum(self):
        z, ost, rz, _ = g.odredba("Najveći dopušteni koeficijent iskorištenosti (kis) nadzemnih etaža iznosi 0,6, a ukoliko se ispod građevine gradi potpuno ukopani podrum najveći dopušteni (kis) iznosi 0,9.", {})
        self.assertEqual([(x["parametar"], x["vrijednost"]) for x in z], [("kisNadzemni", 0.6), ("kisPodrum", 0.9)])

    def test_formula_h1_h2_za_pregled(self):
        z, *_ = g.odredba("Najmanja dopuštena udaljenost između građevina na istoj građevnoj čestici iznosi (h1+h2)/2 (h1 i h2 su visine susjednih građevina), ali ne manje od 6,0 m.", {})
        self.assertEqual((z[0]["operator"], z[0]["vrijednost"]), ("max((h1+h2)/2, X)", 6.0))
        self.assertIn("H_NIJE_DEFINIRAN", [r[0] for r in z[0]["razlozi"]])

    def test_zelenilo(self):
        z, *_ = g.odredba("Najmanje 40% površine građevne čestice mora se urediti kao parkovni nasadi i prirodno zelenilo.", {})
        self.assertEqual((z[0]["parametar"], z[0]["vrijednost"], z[0]["jedinica"]), ("zeleniloMin", 40.0, "%"))

    def test_zagrada_etaza_za_pregled(self):
        z, *_ = g.odredba("Najveća dopuštena visina građevine iznosi 8,0 m (potpuno ukopan podrum i 2 nadzemne etaže).", {})
        self.assertEqual([x["parametar"] for x in z], ["visinaMax", "etazeMax"])
        self.assertTrue(all(x["razlozi"] for x in z))

    def test_stupanj_znak_s_tragom(self):
        n = g.normalizacija("nagiba između 17º i 23º, te")
        self.assertEqual(n.tekst, "nagiba između 17° i 23°, te")
        t = [x for x in n.transformacije if x.pravilo == "STUPANJ_ZNAK"]
        self.assertEqual([n.izvorni[x.od:x.do] for x in t], ["º", "º"])

    def test_logika_uvjeta(self):
        L = g.logika_uvjeta(["Ukoliko na bočnim i stražnjim fasadama građevine nisu predviđeni otvori niti otvorena stubišta"])
        self.assertEqual((L["op"], L["arg"]["op"]), ("NE", "ILI"))
        self.assertEqual(g.logika_uvjeta(["ukoliko građevina ima otvore, prohodne terase i otvorena stubišta"])["op"], "NEJASNO_I_ILI")
        self.assertEqual(g.logika_uvjeta(["a", "b"])["op"], "I")


class Objasnjivost(unittest.TestCase):
    def test_svako_pravilo_ima_izvor_citat_uvjet_i_obrazlozenje(self):
        for r in (ppug(), upu1()):
            for c in r["clanci"].values():
                for p in c.get("pravila", []):
                    if p.get("obrazac") != g.VERZIJA:
                        continue
                    self.assertTrue(p["izvorni_citat"]) ; self.assertIn("uvjet", p); self.assertTrue(p["obrazlozenje_statusa"])
                    self.assertTrue(p["prostorni_obuhvat"]); self.assertEqual(p["primjenjivost_na_lokaciju"], "NIJE_UTVRĐENA")
                    self.assertFalse(p["pravno_potvrdeno"])
                    if p["status"] == "PREGLED":
                        self.assertTrue(p["razlog_kod"])


class Regresija(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.o = U.sve()

    def test_integritet_i_determinizam(self):
        self.assertTrue(self.o["determinizam"]["isto"])

    def test_22_23(self):
        s = self.o["cl22_23"]["v2_1"]
        self.assertEqual((s["tocno"], s["pogresno"], s["pregled"], s["propusteno"]), (44, 0, 11, 0))

    def test_25_33(self):
        s = self.o["cl25_33"]["po_clanku"]
        self.assertEqual((s["25"]["tocno_prihvaceno"], s["25"]["pogresno_prihvaceno"], s["25"]["propusteno"]), (13, 0, 0))
        self.assertEqual((s["33"]["pravilno_na_pregled"], s["33"]["pogresno_prihvaceno"]), (12, 0))

    def test_upu1_i_dodatak_bez_pogresno_prihvacenih(self):
        for k in ("14", "24"):
            self.assertEqual(self.o["upu1_14_24"]["po_clanku"][k]["pogresno_prihvaceno"], 0)
        self.assertEqual(self.o["dodatak_22_23"]["sazetak"]["pogresno_prihvaceno"], 0)

    def test_dodatna_prihvacena_pravila_neovisno_provjerena(self):
        s = self.o["dodatak_ppug_20_38_39_50"]["sazetak"]
        self.assertEqual((s["tocno_prihvaceno"], s["pogresno_prihvaceno"]), (7, 0))
        self.assertEqual(self.o["ostali_clanci_ppug"]["bez_ikakve_oznake"], [])

    def test_upu2(self):
        s = self.o["upu2"]["cl38_40_vlastite_oznake"]
        self.assertEqual((s["tocno"], s["pogresno"], s["dvosmisleno"], s["propusteno"]), (92, 0, 7, 0))
        self.assertEqual(self.o["upu2"]["prijedlozi_gramatike_v22_drugdje"], 0)

    def test_v21_ishodi_isti_osim_dopustenja_gradnje(self):
        a = s21.strukturiraj(izdvoji_tekst(IZ, [22, 23, 25, 33], dio=1), None, "PPUG Krk")
        b = s22.strukturiraj(izdvoji_tekst(IZ, [22, 23, 25, 33], dio=1), None, "PPUG Krk")
        K = lambda p: (p["parametar"], p["operator"], p["vrijednost"], p["vrsta_pravila"], p["uvjet"], p["status"])
        for k in ("22", "23", "25", "33"):
            for x, y in zip(a["clanci"][k]["pravila"], b["clanci"][k]["pravila"]):
                if x["parametar"] == "dopustenaGradnja":
                    self.assertEqual(y["status"], "PREGLED"); self.assertIn("OVISI_O_UVJETIMA_ZA_PREGLED", y["razlog_kod"])
                else:
                    self.assertEqual(K(x), K(y), x["id"])


if __name__ == "__main__":
    unittest.main()

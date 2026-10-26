"""Testovi v2.1: gramatika_v2, jezik_hr, semantika_hr, usporedba. Zamrznuti v1 testovi su u test_citac/test_strukturiraj."""
import json, unittest
from decimal import Decimal
from pathlib import Path
import jezik_hr as J
import semantika_hr as S
import usporedi_v2 as U

M = Path(__file__).resolve().parent
_REZ = {}


def rez():
    if "r" not in _REZ:
        _REZ["r"] = U.pokreni_ppug()
    return _REZ["r"]


def pravila(cl):
    return rez()["clanci"][str(cl)]["pravila"]


class Integritet(unittest.TestCase):
    def test_zamrznute_datoteke_v1_i_oznake(self):
        U.provjeri_integritet()


class JezikNormalizacija(unittest.TestCase):
    def test_m_2_s_tockom_zarezom(self):
        n = J.normaliziraj("iznosi 500 m 2 ;")
        self.assertEqual(n.tekst, "iznosi 500 m²;")
        self.assertEqual({t.pravilo for t in n.transformacije}, {"JEDINICA_EKSPONENT", "BJELINA_ISPRED_ZNAKA"})
        for t in n.transformacije:
            self.assertEqual(n.izvorni[t.od:t.do], t.izvorno)

    def test_m_2_iza_kojeg_slijedi_rijec(self):
        self.assertEqual(J.normaliziraj("iznosi 100 m 2 za sve tipove gradnje;").tekst, "iznosi 100 m² za sve tipove gradnje;")

    def test_metra_u_oznaku_s_tragom(self):
        n = J.normaliziraj("ali ne manje od 4,0 metra ukoliko")
        self.assertEqual(n.tekst, "ali ne manje od 4,0 m ukoliko")
        t = next(t for t in n.transformacije if t.pravilo == "JEDINICA_RIJEC")
        self.assertEqual(t.izvorno, " metra"); self.assertEqual(t.vrsta, "ZAPIS_JEDINICE")

    def test_izvorni_odlomak_iz_normaliziranog(self):
        izv = "najmanja dopuštena\npovršina iznosi 500 m 2 ;"
        n = J.normaliziraj(izv)
        i = n.tekst.index("500 m²")
        self.assertEqual(n.izvorni_odlomak(i, i + len("500 m²")), "500 m 2")

    def test_idempotentno(self):
        for s in ["iznosi 500 m 2 ;", "6,5m", "4,0 metra ukoliko", "određuje se 0,25"]:
            a = J.normaliziraj(s).tekst
            self.assertEqual(J.normaliziraj(a).tekst, a)

    def test_ne_ispravlja_pogreske(self):
        izv = "mogu se rekonsrturirati i prenamjeniti u skladu"
        self.assertEqual(J.normaliziraj(izv).tekst, izv)
        kod = {(x["kod"], x["izvorno"]) for x in J.pravopisne_napomene(izv)}
        self.assertIn(("MOGUCA_TIPOGRAFSKA_POGRESKA", "rekonsrturirati"), kod)
        self.assertIn(("MOGUCA_PRAVOPISNA_POGRESKA", "prenamjeniti"), kod)
        self.assertTrue(all(not x["ispravljeno"] for x in J.pravopisne_napomene(izv)))

    def test_slijedece_samo_napomena(self):
        izv = "Utvrđuju se slijedeće granične vrijednosti"
        self.assertEqual(J.normaliziraj(izv).tekst, izv)
        self.assertEqual(J.pravopisne_napomene(izv)[0]["kod"], "SLIJEDECI_SLJEDECI")

    def test_gradevinske_i_gradevne_se_ne_izjednacuju(self):
        # terminološka razlika nije pravopisna: ostaje doslovno
        izv = "od granice građevinske čestice"
        self.assertEqual(J.normaliziraj(izv).tekst, izv)


class JezikBrojevi(unittest.TestCase):
    def test_decimalni_zarez_i_interpunkcija(self):
        b = J.brojevi("iznosi 0,50; a iznimno 0,25,")
        self.assertEqual([(x.vrijednost, x.vrsta) for x in b], [(Decimal("0.50"), "DECIMALNI"), (Decimal("0.25"), "DECIMALNI")])

    def test_oznaka_zone_nije_broj(self):
        self.assertEqual(J.brojevi("nadzemnih etaža u NA2-NA15.2 iznosi 0,50;")[0].izvorno, "0,50")
        self.assertEqual(len(J.brojevi("u NA2-NA15.2")), 0)
        self.assertEqual(J.pravopisne_napomene("u NA2-NA15.2")[0]["kod"], "SPOJNICA_IZMEDJU_OZNAKA")

    def test_formula_h2_nije_vrijednost(self):
        self.assertEqual(J.brojevi("najmanje pola visine (h/2) od granice"), [])
        self.assertEqual(J.oznake("najmanje h/2, ali")[0]["vrsta"], "FORMULA")

    def test_broj_glasila_nije_vrijednost(self):
        self.assertEqual(J.brojevi("(»Službene novine« broj 29/20)"), [])

    def test_istovrijedni_zapisi(self):
        self.assertTrue(J.istovrijedno("0,50", "0,5"))
        self.assertTrue(J.istovrijedno("500 m 2", "500m²"))
        self.assertTrue(J.istovrijedno("4,0 metra", "4 m"))
        self.assertFalse(J.istovrijedno("4,0 m", "4,0 m²"))
        self.assertFalse(J.istovrijedno("1,0", "1,5"))

    def test_tisucice_s_tockom_dvosmisleno(self):
        b = J.brojevi("površine 10.000 m²")
        self.assertEqual(b[0].vrsta, "TISUCICE_DVOSMISLENO"); self.assertIsNone(b[0].vrijednost)
        self.assertEqual(J.brojevi("površine 10 000 m²")[0].vrijednost, Decimal("10000"))

    def test_stupanj_i_raspon(self):
        b = J.brojevi("između 17° i 23°")
        self.assertEqual([(x.vrijednost, x.jedinica) for x in b], [(Decimal(17), "°"), (Decimal(23), "°")])

    def test_redni_broj(self):
        b = J.brojevi("iz čl. 25. st. 2. ovog plana")
        self.assertEqual([x.vrsta for x in b], ["REDNI", "REDNI"])


class JezikStruktura(unittest.TestCase):
    def test_kratice_ne_lome_recenicu(self):
        r, _ = J.recenice("Primjenjuju se odredbe iz čl. Ovo. Druga rečenica.")
        self.assertEqual(len(r), 2)
        r, nap = J.recenice("prema čl. 25. Ukoliko nije drukčije propisano.")
        self.assertEqual(len(r), 2); self.assertEqual(nap[0]["kod"], "GRANICA_RECENICE_DVOSMISLENA")

    def test_oznake_strukture(self):
        o = J.oznake("Članak 25. (1) Utvrđuju se: a) najmanja … (2) Poljoprivredne: - visina")
        self.assertEqual([x["vrsta"] for x in o], ["CLANAK", "STAVAK", "TOCKA", "STAVAK", "ALINEJA"])

    def test_kosa_crta_rijeci(self):
        k = [x["kod"] for x in J.pravopisne_napomene("Obiteljske/višeobiteljske kuće … kao dvojne/ugrađene")]
        self.assertEqual(k, ["KOSA_CRTA_RIJECI", "KOSA_CRTA_RIJECI"])

    def test_morfologija_ne_pretpostavlja(self):
        self.assertIsNone(J.MorfoloskiAnalizator().ista_lema("stambene", "stambenih"))
        p = J.PopisOblika({"stambena građevina": [r"stamben\w* građevin\w*"]})
        self.assertTrue(p.ista_lema("stambenih građevina", "stambene građevine"))


class Semantika(unittest.TestCase):
    def test_pet_izraza(self):
        kod = lambda s: [x["kod"] for x in S.izrazi(s)]
        self.assertEqual(kod("ovim prostornim planom se ne propisuje najveća dopuštena površina"), ["NE_PROPISUJE_SE", "NAJVISE"])
        self.assertIn("SAMO_KAO", kod("mogu se graditi samo kao samostojeće građevine"))
        self.assertEqual(kod("iznosi najmanje 6,0 m"), ["NAJMANJE"])
        self.assertEqual(kod("iznosi najviše 4,0 m"), ["NAJVISE"])
        self.assertEqual(kod("Iznimno, građevine"), ["IZNIMNO"])

    def test_nije_propisano_nije_neograniceno(self):
        x = S.izrazi("se ne propisuje najveća dopuštena površina")[0]
        self.assertEqual(x["znacenje"], "NIJE_PROPISANO")
        self.assertNotIn("NEOGRANIČENO", [y["znacenje"] for y in S.izrazi("se ne propisuje najveća dopuštena površina")])

    def test_proturjecje_operatora(self):
        self.assertTrue(S.provjeri_pravilo({"izvorni_citat": "iznosi najviše 4,0 m", "operator": ">=", "vrsta_pravila": "OSNOVNO"}))
        self.assertFalse(S.provjeri_pravilo({"izvorni_citat": "iznosi najviše 4,0 m", "operator": "<=", "vrsta_pravila": "OSNOVNO"}))
        self.assertTrue(S.provjeri_pravilo({"izvorni_citat": "iznimno, unutar …", "operator": ">=", "vrsta_pravila": "OSNOVNO"}))


class Clanak25(unittest.TestCase):
    def nadji(self, par, **kw):
        return [p for p in pravila(25) if p["parametar"] == par and all(p.get(k) == v for k, v in kw.items())]

    def test_citat_doslovan_i_trag_normalizacije(self):
        tekst = U.izdvoji_tekst(M / U.IZVOR, [25], dio=1)["clanci"]["25"]["tekst"]
        for p in pravila(25):
            self.assertIn(p["izvorni_citat"], tekst)
            for t in p["normalizacija"]:
                self.assertEqual(p["izvorni_citat"][t["od"]:t["do"]], t["izvorno"])

    def test_brojcane_granice(self):
        self.assertEqual([(p["vrijednost"], p["jedinica"], p["status"]) for p in self.nadji("minC")], [(500.0, "m²", "PRIJEDLOG")])
        self.assertEqual(self.nadji("kig")[0]["vrijednost"], 0.25)
        self.assertEqual(self.nadji("tlMin")[0]["opseg"], "za sve tipove gradnje")

    def test_nije_propisano(self):
        p = self.nadji("maxC")[0]
        self.assertEqual((p["operator"], p["vrijednost"], p["ogranicenje"], p["za_izracun"]), ("nije_propisano", None, "NIJE_PROPISANO", False))

    def test_zona_i_ovisni_kis(self):
        self.assertIn("ZONA_NIJE_DEFINIRANA", self.nadji("kisNadzemni")[0]["razlog_kod"])
        self.assertIn("OVISI_O_NERIJESENOJ_ODREDBI", self.nadji("kisPodrum")[0]["razlog_kod"])

    def test_samo_kao(self):
        d = self.nadji("nacinGradnje", operator="dopusteno")[0]; z = self.nadji("nacinGradnje", operator="zabranjeno")[0]
        self.assertEqual(d["status"], "PRIJEDLOG")
        self.assertEqual(z["status"], "PREGLED"); self.assertIn("ZABRANA_IZVEDENA", z["razlog_kod"]); self.assertIn("MOGUC_SUKOB_ODREDBI", z["razlog_kod"])

    def test_visina_bez_gornje_tocke_nije_prihvacena(self):
        p = self.nadji("visinaMax")[0]
        self.assertEqual(p["status"], "PREGLED"); self.assertEqual(p["referenca"], "od najniže kote konačno zaravnatog terena")

    def test_interval_nagiba_provjerljiv_po_granicama(self):
        mn, mx = self.nadji("nagibKrovaMin")[0], self.nadji("nagibKrovaMax")[0]
        self.assertEqual((mn["vrijednost"], mx["vrijednost"], mn["interval"], mx["interval"]), (17.0, 23.0, "nagibKrova", "nagibKrova"))

    def test_rekonstrukcija_upucivanje_i_pogreska(self):
        p = self.nadji("rekonstrukcijaIPrenamjena")[0]
        self.assertEqual(p["status"], "PREGLED"); self.assertIn("TIPOGRAFSKA_POGRESKA", p["razlog_kod"])
        self.assertIn("rekonsrturirati", p["izvorni_citat"])
        self.assertEqual(self.nadji("rekonstrukcijaAkoNisuIspunjeniUvjeti")[0]["vrsta_gradevine"]["stanje"], "postojeca")


class Clanak33(unittest.TestCase):
    def test_sve_za_pregled_s_razlozima(self):
        P = pravila(33)
        self.assertEqual(len(P), 12)
        self.assertTrue(all(p["status"] == "PREGLED" and p["razlog_kod"] for p in P))
        self.assertTrue(all(not p["za_izracun"] for p in P))

    def test_formula_samo_uz_istu_referencu(self):
        P = pravila(33)
        f = [p for p in P if p["operator"] == "max(h/2, X)"]
        self.assertEqual([(p["stavak"], p["vrijednost"]) for p in f], [(1, 4.0), (3, 3.0)])
        for p in f:
            self.assertIn("čestice", p["formula"]["referenca"])
        odv = [p for p in P if "RAZLICITE_REFERENTNE_TOCKE" in p["razlog_kod"]]
        self.assertEqual(len(odv), 4)   # st. 2 i 4: h/2 od granice susjedne građevine i X od granice čestice ostaju odvojeni

    def test_nasljedivanje_zone_u_drugoj_recenici(self):
        p = next(p for p in pravila(33) if p["stavak"] == 3 and p["recenica"] == 2)
        self.assertEqual(p["vrijednost"], 2.0); self.assertTrue(any("povijesnih graditeljskih cjelina" in u for u in p["uvjeti"]))
        self.assertIn("NEGATIVNI_UVJET_NEPOTPUN", p["razlog_kod"])

    def test_istak_u_st4_je_iznimka(self):
        self.assertTrue(all(p["vrsta_pravila"] in ("IZNIMKA", "ALTERNATIVA") for p in pravila(33) if p["stavak"] == 4))


class Usporedba(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = rez()
        cls.a = U.usporedi_22_23(cls.r)
        cls.b = U.usporedi_25_33(cls.r)

    def test_22_23_nema_pogresnih_i_promjene_su_samo_dokumentirane(self):
        s = self.a["v2_1"]
        self.assertEqual((s["pogresno"], s["propusteno"], s["pregled_odgovara_oznaci"]), (0, 0, s["pregled"]))
        self.assertEqual(s["tocno"] + s["pregled"], 55)
        self.assertEqual({(x["oznaka"], x["v1"], x["v2_1"]) for x in self.a["promjene_po_oznaci"]},
                         {("G022", "TOČNO", "PREGLED"), ("G046", "TOČNO", "PREGLED")})

    def test_25_33(self):
        s = self.b["sazetak"]
        self.assertEqual({k: (v["tocno"], v["pogresno"], v["pregled"], v["propusteno"]) for k, v in s.items()}, {"25": (14, 0, 8, 0), "33": (0, 0, 12, 0)})
        self.assertEqual(s["25"]["pregled_odgovara_oznaci"], 8); self.assertEqual(s["33"]["pregled_odgovara_oznaci"], 12)
        self.assertEqual(sorted(x["oznaka"] for x in self.b["jasne_oznake_koje_nisu_tocne"]), ["N013", "N014", "N022"])

    def test_nema_novih_prihvacenih_pravila_drugdje(self):
        o = U.ostali_prijedlozi(self.r)
        self.assertEqual(o["prijedlog"], 0)

    def test_upu2_bez_regresije(self):
        s = U.upu2()["cl38_40_vlastite_oznake"]
        self.assertEqual((s["tocno"], s["pogresno"], s["dvosmisleno"], s["propusteno"]), (92, 0, 7, 0))

    def test_determinizam(self):
        self.assertEqual(U.sha_obj(self.r), U.sha_obj(U.pokreni_ppug()))


if __name__ == "__main__":
    unittest.main()

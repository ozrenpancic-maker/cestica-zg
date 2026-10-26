"""Testovi strukturiranja pravila (čl. 38.–40. UPU-a 2 Kornić).
Pokretanje: python3 -m unittest -v test_strukturiraj   (iz mape tools/plan-citac; treba PyMuPDF)

Usporedba s ručnim oznakama (oznake/upu2_cl38_40.json) zaključava rezultat, ali NIJE neovisna ocjena:
oznake i obrasce piše isti autor. Ostali testovi provjeravaju opreznost (PREGLED umjesto pogađanja)
na izmijenjenim alinejama koje obrasci nisu vidjeli."""
import json, unittest
from pathlib import Path
from citac import izdvoji, navod
from strukturiraj import strukturiraj, strukturiraj_clanak, alineje, tocke, podskup
from ocijeni import ocijeni

MAPA = Path(__file__).resolve().parent
PDF = MAPA.parents[1] / "tests/pgz-odgovori/735-76-kornic-2026-10-22/sn-19-16/odluka_34138.pdf"

try:
    import pymupdf  # noqa: F401
    IMA_PDF = True
except ImportError:
    IMA_PDF = False


def lazni_clanak(tekst):
    return {"tekst": tekst, "blokovi": [{"tekst": "Članak 99. " + tekst, "stranica": 1, "stupac": "L", "okvir": [0, 0, 1, 1]}]}


UVOD = "Utvrđuju se uvjeti gradnje slobodnostojeće obiteljske odnosno slobodnostojeće višeobiteljske kuće: "


@unittest.skipUnless(IMA_PDF, "PyMuPDF nije instaliran")
class Clanci38do40(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = izdvoji(PDF, "UPU 2 - Kornić", 108)
        cls.R = strukturiraj(cls.D, [38, 39, 40], "UPU 2 Kornić")
        cls.P = [p for c in cls.R["clanci"].values() for p in c["pravila"]]
        cls.oznake = json.loads((MAPA / "oznake/upu2_cl38_40.json").read_text(encoding="utf-8"))

    def test_usporedba_s_rucnim_oznakama(self):
        s, r = ocijeni(self.R, self.oznake)
        self.assertEqual((s["oznaceno"], s["tocno"], s["pogresno"], s["dvosmisleno"], s["propusteno"]), (97, 97, 0, 0, 0), r["pogresno"][:2])
        self.assertEqual((s["upucivanja_tocno"], s["upucivanja_pogresno"]), (2, 0))
        self.assertFalse(s["oznake_neovisne"])  # oznake su iz iste ruke: ovo nije neovisna ocjena

    def test_vrste_iz_uvoda_clanka(self):
        self.assertEqual(self.R["clanci"]["38"]["vrste"], ["obit-slob", "visobit-slob"])
        self.assertEqual(self.R["clanci"]["39"]["vrste"], ["obit-dvoj", "obit-ugr", "visobit-dvoj"])
        self.assertEqual(self.R["clanci"]["40"]["vrste"], ["stamb"])

    def test_iznimke_cuvaju_uvjet(self):
        iz = [p for p in self.P if p["vrsta_pravila"] == "IZNIMKA"]
        self.assertTrue(all(p["uvjet"] and p["uvjet"] in p["dokaz"] for p in iz))
        m = [p for p in self.P if p["clanak"] == 38 and p["parametar"] == "minC"]
        self.assertEqual([(p["vrijednost"], p["vrste"], p["vrsta_pravila"]) for p in m],
                         [(500, ["obit-slob"], "OSNOVNO"), (400, ["obit-slob"], "IZNIMKA"), (500, ["visobit-slob"], "OSNOVNO")])
        self.assertEqual(m[1]["uvjet"], "ako se građevna čestica nalazi u okruženju već uređenih i izgrađenih građevnih čestica")
        # iznimka kis 1,0 vrijedi samo za višeobiteljsku kuću na kosom terenu (alineja 5. točke b)
        k = [p for p in self.P if p["parametar"] == "kis" and p["vrsta_pravila"] == "IZNIMKA"]
        self.assertEqual([(p["clanak"], p["vrste"]) for p in k], [(38, ["visobit-slob"]), (39, ["visobit-dvoj"]), (40, ["stamb"])])
        for p in k:
            self.assertEqual((p["uvjet_upucuje_na"]["tocka"], p["uvjet_upucuje_na"]["alineja"]), ("b", 5))
            self.assertIn("na kosom terenu gdje je nagib prirodnog terena veći od 12%", p["uvjet_upucuje_na"]["tekst"])
        # nijedna iznimka nije postala opće pravilo: osnovne vrijednosti ostaju osnovne
        osn = {(p["clanak"], p["parametar"], tuple(p["vrste"])): p["vrijednost"] for p in self.P if p["vrsta_pravila"] == "OSNOVNO" and p["gradjevina"] == "osnovna"}
        self.assertEqual(osn[(38, "kis", ("obit-slob", "visobit-slob"))], 0.75)
        self.assertEqual(osn[(38, "visinaMax", ("obit-slob", "visobit-slob"))], 7.5)
        self.assertEqual(osn[(38, "medaMin", ("obit-slob", "visobit-slob"))], 4)

    def test_odnosno_za_drugu_vrstu(self):
        t = {(p["parametar"], p["vrijednost"]): p["vrste"] for p in self.P if p["clanak"] == 39 and p["tocka"] in "ab"}
        self.assertEqual(t[("minC", 300)], ["obit-dvoj", "obit-ugr"]); self.assertEqual(t[("minC", 400)], ["visobit-dvoj"])
        self.assertEqual(t[("tlMax", 150)], ["obit-dvoj", "visobit-dvoj"]); self.assertEqual(t[("tlMax", 100)], ["obit-ugr"])
        self.assertEqual(t[("gbpMax", 200)], ["obit-dvoj", "obit-ugr"]); self.assertEqual(t[("gbpMax", 400)], ["visobit-dvoj"])
        self.assertFalse(any(p["parametar"] == "gbpMax" for p in self.P if p["clanak"] == 40))  # čl. 40 nema GBP

    def test_upucivanja_ne_prepisuju_pravila(self):
        self.assertEqual([u["upucuje_na"] for u in self.R["clanci"]["39"]["upucivanja"]], [{"clanak": 38, "tocke": ["d", "e", "f", "g", "h", "i"]}])
        self.assertEqual([u["upucuje_na"] for u in self.R["clanci"]["40"]["upucivanja"]], [{"clanak": 38, "tocke": ["c", "d", "e", "f", "g", "h", "i"]}])
        self.assertFalse(any(p["clanak"] == 39 and p["tocka"] == "d" for p in self.P))
        self.assertFalse(any(p["clanak"] == 40 and p["tocka"] == "c" for p in self.P))

    def test_dokaz_i_polozaj(self):
        C = self.D["clanci"]
        for p in self.P:
            self.assertIn(p["dokaz"], C[str(p["clanak"])]["tekst"])
            self.assertIsNotNone(p["izvor"])
            blok = [b for b in C[str(p["clanak"])]["blokovi"] if b.get("okvir") == p["izvor"]["okvir"] and b.get("stranica") == p["izvor"]["stranica"]]
            self.assertEqual(len(blok), 1)
            k = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
            self.assertIn(k(p["dokaz"])[:30], k(blok[0]["tekst"]) + k(" ".join(b.get("tekst", "") for b in C[str(p["clanak"])]["blokovi"])))
        a1 = [p for p in self.P if (p["clanak"], p["tocka"], p["alineja"]) == (38, "a", 1)][0]["izvor"]
        self.assertEqual((a1["stranica"], a1["stupac"]), (13, "L"))
        b6 = [p for p in self.P if (p["clanak"], p["tocka"], p["alineja"], p["parametar"]) == (39, "b", 6, "gbpMax")][0]["izvor"]
        self.assertEqual(b6["stranica"], 14)

    def test_bez_pravne_potvrde(self):
        self.assertTrue(all(p["pravno_potvrdeno"] is False for p in self.P))
        self.assertEqual((self.R["automatska_potvrda"], self.R["pravno_potvrdeno"]), (0, False))


class Opreznost(unittest.TestCase):
    """Izmijenjene alineje (nisu u izvoru): modul ne smije pogađati."""

    def pravila(self, tocka):
        return strukturiraj_clanak(99, lazni_clanak(UVOD + tocka), "TEST")

    def test_nepoznata_recenica_nije_pravilo(self):
        r = self.pravila("a) Veličina - najmanja površina građevne čestice iznosi 500 m², osim ako odluka predstavničkog tijela ne odredi drukčije.")
        self.assertEqual(r["pravila"], [])
        self.assertEqual(r["nepokriveno"][0]["brojevi"], ["500"])

    def test_kriva_alineja_u_upucivanju(self):
        r = self.pravila("a) Veličina - najveći koeficijent iskorištenosti iznosi 0,75, a iznimno 1,0 ako se višeobiteljska kuća gradi prema uvjetima alineje 7. točke b) ovog članka. "
                         "b) Veličina građevine - najmanja tlocrtna površina građevine iznosi 60 m².")
        iz = [p for p in r["pravila"] if p["vrsta_pravila"] == "IZNIMKA"][0]
        self.assertEqual(iz["status"], "PREGLED")
        self.assertIn("upućivanje na alineju 7. točke b) nije jednoznačno", iz["razlozi"])

    def test_vrsta_koje_nema_u_clanku(self):
        r = strukturiraj_clanak(99, lazni_clanak("Utvrđuju se uvjeti gradnje stambene građevne: a) Veličina - najmanja površina građevne čestice obiteljske kuće iznosi 500 m²."), "TEST")
        self.assertEqual([(p["status"], p["vrste"]) for p in r["pravila"]], [("PREGLED", [])])

    def test_nepoznat_uvod(self):
        r = strukturiraj_clanak(99, lazni_clanak("Za gradnju poslovnih građevina primjenjuju se odredbe članka 15."), "TEST")
        self.assertEqual(r["pravila"], []); self.assertTrue(r["pregled"])

    def test_iznimka_ostaje_iznimka(self):
        r = self.pravila("a) Veličina - najmanja površina građevne čestice obiteljske kuće iznosi 600 m², a iznimno 450 m² ako je čestica uz javnu cestu.")
        self.assertEqual([(p["vrijednost"], p["vrsta_pravila"], p["uvjet"]) for p in r["pravila"]],
                         [(600, "OSNOVNO", None), (450, "IZNIMKA", "ako je čestica uz javnu cestu")])

    def test_podnabrajanje_se_ne_broji(self):
        naslov, al = alineje("Uvjeti - prva, - smjer se definira prema kriterijima: - usporedno s A, - usporedno s B, - treća.")
        self.assertEqual(al, ["prva,", "smjer se definira prema kriterijima: - usporedno s A, - usporedno s B,", "treća."])
        self.assertEqual([t["slovo"] for t in tocke("x: a) Prvo - a. b) Drugo - b, prema točki c) ovog članka.")], ["a", "b"])

    def test_podskup_vrsta(self):
        V = ["obit-dvoj", "obit-ugr", "visobit-dvoj"]
        self.assertEqual(podskup(V, "obiteljske kuće"), ["obit-dvoj", "obit-ugr"])
        self.assertEqual(podskup(V, "ugrađenu obiteljsku kuću"), ["obit-ugr"])
        self.assertEqual(podskup(V, "višeobiteljska građevina"), ["visobit-dvoj"])
        self.assertIsNone(podskup(V, "poslovne građevine"))


class DvosmisleniNavodi(unittest.TestCase):
    def test_navod_vise_clanaka_sa_stavkom(self):
        for s in ("čl. 38. i 39. st. 2.", "čl. 38.–40. st. 1.", "38., 39. st. 2."):
            n = navod(s)
            self.assertTrue(n["dvosmisleno"], s); self.assertEqual(n["status"], "PREGLED")
            self.assertTrue(all(p["stavci"] == [] for p in n["parovi"]), s)  # stavak se ne pripisuje nijednom članku
        for s in ("čl. 38. st. 2. i 3.", "čl. 38. st. 2.; čl. 39. st. 1.", "čl. 38. i čl. 39. st. 2.", "čl. 38., 39. i 41."):
            self.assertFalse(navod(s)["dvosmisleno"], s)
        self.assertEqual(navod("čl. 38. i čl. 39. st. 2.")["parovi"], [{"clanak": 38, "stavci": []}, {"clanak": 39, "stavci": [2]}])


if __name__ == "__main__":
    unittest.main()

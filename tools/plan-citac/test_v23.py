"""Testovi v2.3: prijenos konteksta primjene i »samo kao«. Testovi v1, v2.1 i v2.2 ostaju i moraju prolaziti."""
import hashlib, json, unittest
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v22 as s22
import strukturiraj_v23 as s23
import usporedi_v22 as U

M = Path(__file__).resolve().parent
IZ = M / U.U.IZVOR
_C = {}


def ppug():
    if "p" not in _C:
        d = izdvoji_tekst(IZ, dio=1)
        _C["p"] = (s22.strukturiraj(d, None, "PPUG Krk"), s23.strukturiraj(d, None, "PPUG Krk"))
    return _C["p"]


def upu1():
    if "u" not in _C:
        d = izdvoji_tekst(IZ, [14, 24], dio=2)
        _C["u"] = (s22.strukturiraj(d, None, "UPU 1"), s23.strukturiraj(d, None, "UPU 1"))
    return _C["u"]


def pravila(r, cl, st=None):
    return [p for p in r["clanci"][str(cl)]["pravila"] if st is None or p["stavak"] == st]


class Kontekst(unittest.TestCase):
    def test_cl39_pomocne_regulacija(self):
        p = next(p for p in pravila(ppug()[1], 39, 2) if p["parametar"] == "regulacija")
        self.assertEqual(p["vrijednost"], 5.0)
        self.assertIn("pomocna", p["vrsta_gradevine"]["skupine"])
        self.assertEqual(p["kontekst_primjene"], ["uz građevine društvene i sportsko-rekreacijske namjene"])
        self.assertEqual(p["uvjeti"][0], "uz građevine društvene i sportsko-rekreacijske namjene")
        self.assertEqual(p["izvor_konteksta"]["clanak"], 39)

    def test_cl39_50m2_jos_nije_izdvojeno(self):
        """Poznata slabost pokrivenosti (nije cilj v2.3): »tlocrtna projekcija nije veća od 50 m²« ostaje odbijena."""
        self.assertFalse([p for p in pravila(ppug()[1], 39, 2) if p["parametar"] == "tlMax"])
        self.assertTrue(any("50 m 2" in x["dokaz"] for x in ppug()[1]["clanci"]["39"]["nepokriveno"]))

    def test_cl50_gospodarska(self):
        for p in pravila(ppug()[1], 50, 4):
            self.assertEqual(p["kontekst_primjene"], ["uz građevine gospodarske namjene"])

    def test_stambena_kontekst_sacuvan(self):
        for cl, st, k in [(20, 3, "uz građevine stambene namjene"), (22, 2, "na građevnoj čestici uz obiteljsku kuću"),
                          (23, 2, "na građevnoj čestici uz višeobiteljsku kuću")]:
            P = pravila(ppug()[1], cl, st)
            self.assertTrue(P)
            for p in P:
                self.assertEqual([x.lower() for x in p["kontekst_primjene"]], [k], (cl, st))

    def test_kontekst_je_doslovan(self):
        d = izdvoji_tekst(IZ, dio=1)
        for cl in ("20", "22", "23", "39", "50"):
            for p in ppug()[1]["clanci"][cl]["pravila"]:
                for k in p["kontekst_primjene"]:
                    self.assertIn(k, d["clanci"][cl]["tekst"])

    def test_dodatni_uvjeti_odvojeni(self):
        p = next(p for p in pravila(ppug()[1], 39, 2) if p["parametar"] == "rekonstrukcijaIPrenamjena")
        self.assertEqual(p["dodatni_uvjeti"], ["u skladu s odredbama ovog Prostornog plana"])
        self.assertEqual(p["uvjeti"], ["uz građevine društvene i sportsko-rekreacijske namjene", "u skladu s odredbama ovog Prostornog plana"])

    def test_bez_uvoda_nema_konteksta(self):
        for p in pravila(ppug()[1], 22, 1) + pravila(ppug()[1], 25):
            self.assertEqual(p["kontekst_primjene"], [])

    def test_upu1_blok7(self):
        P = [p for p in pravila(upu1()[1], 24) if p.get("blok") == 7]
        self.assertTrue(P)
        for p in P:
            self.assertEqual(p["kontekst_primjene"], ["uz građevinu osnovne namjene"])

    def test_vrsta_pravila_i_status_nepromijenjeni(self):
        for a, b in [ppug(), upu1()]:
            A = {p["id"]: p for c in a["clanci"].values() for p in c.get("pravila", [])}
            for c in b["clanci"].values():
                for p in c.get("pravila", []):
                    self.assertEqual(p["vrsta_pravila"], A[p["id"]]["vrsta_pravila"])
                    self.assertEqual(p["status"], A[p["id"]]["status"])
                    self.assertEqual(p["vrijednost"], A[p["id"]]["vrijednost"])


class SamoKao(unittest.TestCase):
    def test_cl25(self):
        P = [p for p in pravila(ppug()[1], 25) if p["parametar"] == "nacinGradnje"]
        self.assertEqual(sorted(p["operator"] for p in P), ["=", "zabranjeno"])

    def test_bez_samo_ostaje_dopusteno(self):
        for c in ppug()[1]["clanci"].values():
            for p in c.get("pravila", []):
                if p["parametar"] == "nacinGradnje" and "samo kao" not in p["izvorni_citat"]:
                    self.assertNotEqual(p["operator"], "=")


class Regresija(unittest.TestCase):
    def test_zamrznuta_v22(self):
        z = json.loads((M / "ZAMRZNUTO_v2_2.json").read_text(encoding="utf-8"))
        for p, s in z["kod"].items():
            self.assertEqual(hashlib.sha256((M / p).read_bytes()).hexdigest(), s, p)

    def test_determinizam(self):
        d = izdvoji_tekst(IZ, dio=1)
        a = s23.zapisi_json(s23.strukturiraj(d, None, "PPUG Krk"), "/dev/null")
        b = s23.zapisi_json(s23.strukturiraj(d, None, "PPUG Krk"), "/dev/null")
        self.assertEqual(a, b)

    def test_upu2_nepromijenjen(self):
        d2 = json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8"))
        a, b = s22.strukturiraj(d2, None, "UPU 2"), s23.strukturiraj(d2, None, "UPU 2")
        for k in ("38", "39", "40"):
            self.assertEqual([(p["parametar"], p["vrijednost"], p.get("uvjet")) for p in a["clanci"][k]["pravila"]],
                             [(p["parametar"], p["vrijednost"], p.get("uvjet")) for p in b["clanci"][k]["pravila"]])

    def test_pravno_potvrdeno_0(self):
        for c in ppug()[1]["clanci"].values():
            for p in c.get("pravila", []):
                self.assertFalse(p["pravno_potvrdeno"])


if __name__ == "__main__":
    unittest.main()

"""Testovi v2.6: normalizacija izvora, naslovi zona, vrsta iz svih izraza uvoda, novi oblici i zaštite.
Testovi v1–v2.5 i prilagodnika ostaju i moraju prolaziti."""
import json, unittest
from pathlib import Path
from citac_tekst import izdvoji_tekst
import izvor_v26 as I
import gramatika_v26 as g6
import strukturiraj_v25 as s25
import strukturiraj_v26 as s26
import usporedi_v22 as U

M = Path(__file__).resolve().parent
IZ = M / U.U.IZVOR
NV = M / "slijepo/novi_vinodolski/nv_upu_sn_32_2026.html"
CR = M / "slijepo/crikvenica_centar_1/crikvenica_upu_centar_1.html"
_C = {}


def rez(k):
    if k not in _C:
        if k == "cr":
            d = I.ucitaj(CR)
            d = dict(d, clanci={kk: c for kk, c in d["clanci"].items() if c["broj"] in (23, 24, 25, 26)})
        else:
            d = {"nv": lambda: I.ucitaj(NV), "upu1": lambda: I.ucitaj(IZ, dio=2), "ppug": lambda: I.ucitaj(IZ, dio=1),
                 "upu2": lambda: json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8"))}[k]()
        _C[k] = s26.strukturiraj(d, None, k)
    return _C[k]


def pravila(k, cl, par=None):
    return [p for p in rez(k)["clanci"][str(cl)].get("pravila", []) if par is None or p["parametar"] == par]


class Priprema(unittest.TestCase):
    def test_tisucice(self):
        for a, b in (("iznosi 1.500 m 2 .", "iznosi 01500 m 2 ."), ("12.000 m²", "012000 m²"), ("1.250.000 m²", "001250000 m²")):
            self.assertEqual(g6.pripremi(a), b)
        for a in ("visina 1,50 m", "nagib 1.5 m", "iz članka 110. odredbi", "čl. 1.500 Zakona", "0,5"):
            self.assertEqual(g6.pripremi(a).replace("․", "."), a)

    def test_indeks_kig_kis(self):
        self.assertEqual(g6.pripremi("koeficijent izgrađenosti (k ig ) iznosi 0,5"), "koeficijent izgrađenosti (kig)   iznosi 0,5")

    def test_zone_naslova(self):
        self.assertEqual(g6.zone_naslova("Zone poslovne gradnje uz luku nautičkog turizma (K1 1 i K1 2 )"), ["K1 1", "K1 2"])
        self.assertEqual(g6.zone_naslova("Zona T1 1 - hotel"), ["T1 1"])
        self.assertEqual(g6.zone_naslova("Zona poslovne gradnje uz komunalnu luku (K2)"), ["K2"])
        self.assertEqual(g6.zone_naslova("Uvjeti gradnje"), [])


class Vrsta(unittest.TestCase):
    def test_svi_izrazi_uvoda(self):
        u = "Zone poslovne gradnje uz luku (K1 1 ) Unutar zona poslovne gradnje uz luku planiran je smještaj građevina poslovne namjene (trgovački), na jednoj"
        V = g6.vrste_uvoda(u)
        self.assertEqual([v["kodovi"] for v in V if v["odnos"] == "OBJEKT_GRADNJE"], [("poslovna",)])
        self.assertEqual(g6.vrsta_uvoda(u)[0], ("poslovna",))

    def test_postojeca_nije_objekt(self):
        u = "Zona T1 1 predstavlja jednu građevnu česticu na kojoj se nalazi postojeća zgrada hotela."
        self.assertIsNone(g6.vrsta_uvoda(u)[0])

    def test_viseznacna(self):
        k, _, r = g6.vrsta_uvoda("Na površini se grade poslovne građevine, a uz njih je moguć smještaj stambene građevine")
        self.assertIsNone(k); self.assertEqual(r, "VRSTA_VISEZNACNA")


class Izvor(unittest.TestCase):
    def test_crikvenica_naslovi_odvojeni(self):
        d = I.ucitaj(CR)
        self.assertEqual(len(d["clanci"]), 114)
        N = {c["broj"]: c.get("naslov_clanka") for c in d["clanci"].values()}
        self.assertEqual(N[24], "Zone poslovne gradnje uz luku nautičkog turizma (K1 1 i K1 2 )")
        self.assertEqual(N[26], "Zona T1 1 - hotel")
        self.assertIsNone(N[23])

    def test_nv_tekst_nepromijenjen(self):
        a, b = izdvoji_tekst(NV, dio=None), I.ucitaj(NV)
        self.assertEqual({k: c["tekst"] for k, c in a["clanci"].items()}, {k: c["tekst"] for k, c in b["clanci"].items()})

    def test_pdf_klasa_velikim_slovima(self):
        d = I.ucitaj(M / "slijepo/rab_upu41/rab_upu41_sn_20_2026.pdf", naslov="URBANISTIČKOG PLANA UREĐENJA 41")
        self.assertEqual(len(d["clanci"]), 47)

    def test_pdf_ostecen_font_abstain(self):
        d = I.ucitaj(M / "slijepo/omisalj_upu2_njivice/omisalj_upu2_njivice_sn_38_2025.pdf", naslov="URBANISTIČKOG PLANA UREĐENJA 2-NJIVICE")
        self.assertEqual(d["status"], "ABSTAIN_KODIRANJE")


class Oblici(unittest.TestCase):
    def test_nacin_gradnje_subjekt(self):
        z, lit = g6.oblici("Građevine koje će se graditi na slobodnostojeći način moraju biti udaljene najmanje 4,0 metra od granice građevne čestice, "
                           "odnosno 3,0 m ukoliko na toj strani nisu predviđeni otvori, prohodne terase niti otvorena stubišta.", {})
        self.assertEqual([(x["operator"], x["vrijednost"], x["vrsta_pravila"], x["oblici"]) for x in z],
                         [(">=", 4.0, "OSNOVNO", ("slob",)), (">=", 3.0, "UVJETNO", ("slob",))])
        self.assertEqual(lit, ["4,0", "3,0"])

    def test_dvije_etaze_bez_mijesanja(self):
        z, _ = g6.oblici("Najveći dopušteni broj etaža je 4, ali dozvoljene su najviše 2 nadzemne etaže.", {})
        self.assertEqual([(x["parametar"], x["vrijednost"]) for x in z], [("etazeMax", 4), ("etazeNadzemneMax", 2)])

    def test_dvije_visine_bez_mijesanja(self):
        z, _ = g6.oblici("Visina građevine iznosi najviše 10,0 m, a ukupna visina građevine iznosi najviše 13,0 m.", {})
        self.assertEqual([(x["parametar"], x["vrijednost"]) for x in z], [("visinaMax", 10.0), ("ukupnaVisinaMax", 13.0)])

    def test_crikvenica_cl24(self):
        P = {p["parametar"]: p for p in pravila("cr", 24)}
        self.assertEqual(P["maxC"]["vrijednost"], 1500.0)
        self.assertIn("1.500 m 2", P["maxC"]["izvorni_citat"])
        self.assertEqual(P["kig"]["vrsta_gradevine"]["skupine"], ["poslovna"])
        self.assertTrue(all({"K1 1", "K1 2"} <= {o.get("oznaka") for o in p["prostorni_obuhvat"]} for p in P.values()))


class Zastite(unittest.TestCase):
    def test_vrsta_novim_putem_na_pregledu(self):
        for k in ("cr", "upu1", "upu2"):
            for c in rez(k)["clanci"].values():
                for p in c.get("pravila", []):
                    if p.get("izvor_vrste"):
                        self.assertEqual(p["status"], "PREGLED", (k, p["id"]))
                        self.assertIn("VRSTA_IZ_UVODA_V26", p["razlog_kod"])

    def test_bez_vrste_ili_zone_na_pregledu(self):
        for p in [p for c in rez("cr")["clanci"].values() for p in c.get("pravila", [])]:
            if not p["vrsta_gradevine"].get("skupine"):
                self.assertEqual(p["status"], "PREGLED", p["id"])

    def test_nijedno_prihvacanje_vise_nego_v25(self):
        """Krk, Kornić, NV: nijedno pravilo nije prihvaćeno u v2.6 ako nije bilo prihvaćeno u v2.5 (isti citat, parametar, vrijednost)."""
        kl = lambda p: (p.get("clanak"), p.get("parametar"), str(p.get("vrijednost")), (p.get("izvorni_citat") or "")[:80])
        for k, d5 in (("ppug", lambda: izdvoji_tekst(IZ, dio=1)), ("upu1", lambda: izdvoji_tekst(IZ, dio=2)), ("nv", lambda: izdvoji_tekst(NV, dio=None)),
                      ("upu2", lambda: json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8")))):
            a = s25.strukturiraj(d5(), None, k)
            A = {kl(p) for c in a["clanci"].values() for p in c.get("pravila", []) if p.get("status") == "PRIJEDLOG"}
            for c in rez(k)["clanci"].values():
                for p in c.get("pravila", []):
                    if p.get("status") == "PRIJEDLOG":
                        self.assertIn(kl(p), A, (k, p.get("id")))

    def test_bez_pravne_potvrde_i_determinizam(self):
        r = rez("cr")
        self.assertEqual(r["automatska_potvrda"], 0)
        self.assertFalse(r["pravno_potvrdeno"])
        d = I.ucitaj(CR)
        d = dict(d, clanci={kk: c for kk, c in d["clanci"].items() if c["broj"] in (23, 24, 25, 26)})
        self.assertEqual(json.dumps(s26.strukturiraj(d, None, "cr"), sort_keys=True, ensure_ascii=False), json.dumps(r, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()

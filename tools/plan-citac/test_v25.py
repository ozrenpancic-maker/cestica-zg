"""Testovi v2.5: struktura dokumenta, kontekst uvoda, novi oblici i zaštite. Testovi v1–v2.4 ostaju i moraju prolaziti."""
import json, unittest
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v24 as s24
import strukturiraj_v25 as s25
import gramatika_v25 as g5
import usporedi_v22 as U

M = Path(__file__).resolve().parent
IZ = M / U.U.IZVOR
NV = M / "slijepo/novi_vinodolski/nv_upu_sn_32_2026.html"
_C = {}
SAMO_V25 = ("razlog_kod", "razlozi", "obrazlozenje_statusa", "zone_konteksta", "kontekst_nova_gradnja", "nadredjeni_uvod")


def dok(k):
    if k not in _C:
        _C[k] = {"ppug": lambda: izdvoji_tekst(IZ, dio=1), "upu1": lambda: izdvoji_tekst(IZ, [14, 24], dio=2),
                 "nv": lambda: izdvoji_tekst(NV, dio=None),
                 "upu2": lambda: json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8"))}[k]()
    return _C[k]


def rez(k, mod=s25):
    kk = (k, mod.__name__)
    if kk not in _C:
        _C[kk] = mod.strukturiraj(dok(k), None, k)
    return _C[kk]


def pravila(cl, par=None, v=None, k="nv"):
    return [p for p in rez(k)["clanci"][str(cl)].get("pravila", []) if (par is None or p["parametar"] == par) and (v is None or p["vrijednost"] == v)]


def jedno(cl, par, v=None, k="nv"):
    L = pravila(cl, par, v, k)
    assert len(L) == 1, (cl, par, v, len(L))
    return L[0]


class Struktura(unittest.TestCase):
    def test_priprema_cuva_duljinu_i_citat(self):
        t = "• najmanja udaljenost od ul. Antuna Mataije, čl. 19. st. 2, vis. od 1,0 m i sl. ostalo"
        T = g5.pripremi(t)
        self.assertEqual(len(T), len(t))
        self.assertNotIn("•", T)
        self.assertEqual(g5.vrati_izvorno(T[2:40], T, t), t[2:40])
        self.assertIn("ul.", g5.vrati_izvorno("ul․", T, t))

    def test_vrsta_iz_cijele_uvodne_recenice(self):
        self.assertEqual(g5.skupina_uvoda("Planom se utvrđuju opći uvjeti za izgradnju novih poslovnih i ugostiteljsko-turističkih građevina"),
                         ("poslovna", "ugostiteljsko_turisticka"))
        self.assertEqual(g5.skupina_uvoda("Površina označena planskom oznakom (K11) namijenjena je izgradnji poslovne građevine"), ("poslovna",))
        self.assertIsNone(g5.skupina_uvoda("Unutar građevine moguć je smještaj uslužnog sadržaja"))

    def test_zone_nova_iznimka_iz_uvoda(self):
        k = g5.kontekst_uvoda("Unutar površina označenih planskom oznakom (K1) smještavaju se manji pogoni")
        self.assertEqual(k["zone"], ["K1"])
        k2 = g5.kontekst_uvoda("Na površinama iz stavka (1) ovog članka grade se poslovne građevine prema uvjetima za novu izgradnju", {1: k})
        self.assertEqual((k2["zone"], k2["nova"]), (["K1"], "za novu izgradnju"))
        k3 = g5.kontekst_uvoda("Iznimno, površina označena oznakom K21 može se graditi u skladu sa sljedećim uvjetima")
        self.assertEqual(k3["zone"], ["K21"])
        self.assertTrue(k3["iznimka"])

    def test_nv_clanci_prepoznati(self):
        for cl in (19, 20, 23, 24):
            self.assertTrue(pravila(cl), cl)

    def test_kontekst_preneseno_na_pravilo(self):
        p = jedno(20, "kig")
        self.assertEqual(p["vrsta_gradevine"]["stanje"], "nova")
        self.assertIn("K1", p["zone_konteksta"])
        self.assertTrue(any(o.get("oznaka") == "K1" for o in p["prostorni_obuhvat"]))
        self.assertIn("K11", jedno(23, "kig")["zone_konteksta"])

    def test_iznimka_stavka_k21(self):
        p = jedno(24, "etazeMax", 3)
        self.assertEqual(p["vrsta_pravila"], "IZNIMKA")
        self.assertIn("površina označena oznakom K21", p["uvjeti"])


class Oblici(unittest.TestCase):
    def test_ne_moze_biti_manja_od_s_iznimkom(self):
        z, lit = g5.oblici("površina građevne čestice ne može biti manja od 600 m 2 , iznimno za benzinske stanice 500 m 2 ;", {})
        self.assertEqual([(x["parametar"], x["operator"], x["vrijednost"], x["vrsta_pravila"]) for x in z],
                         [("minC", ">=", 600.0, "OSNOVNO"), ("minC", ">=", 500.0, "IZNIMKA")])
        self.assertEqual(z[1]["uvjeti"], ["za benzinske stanice"])
        self.assertEqual(lit, ["600", "500"])
        self.assertTrue(all(p["status"] == "PREGLED" for p in pravila(20, "minC")))

    def test_etaze_operator_i_uvjet(self):
        z, _ = g5.oblici("građevina može imati do četiri (4) nadzemne etaže uz uvjet da je četvrta etaža potkrovlje bez nadozida;", {})
        self.assertEqual((z[0]["operator"], z[0]["vrijednost"], z[0]["vrsta_pravila"]), ("<=", 4, "UVJETNO"))
        self.assertIn("uz uvjet da je četvrta etaža potkrovlje bez nadozida", z[0]["uvjeti"])
        self.assertIsNone(g5.oblici("građevina može imati do četiri (5) nadzemne etaže;", {}))

    def test_podzemne_etaze_su_pregled(self):
        P = pravila(24, "etazeMax", 1)
        self.assertEqual(len(P), 2)
        self.assertTrue(all(p["status"] == "PREGLED" and "ETAZE_PODZEMNE" in p["razlog_kod"] for p in P))

    def test_regulacija_po_ulici_uvjetno(self):
        P = sorted([p for p in pravila(20, "regulacija") if p["vrsta_gradevine"]["skupine"] == ["poslovna"]], key=lambda p: -p["vrijednost"])
        self.assertEqual([(p["vrijednost"], p["vrsta_pravila"]) for p in P], [(10.0, "UVJETNO"), (4.0, "UVJETNO")])
        self.assertIn("ul. Antuna Mataije", P[0]["uvjeti"])
        self.assertIn("od ostalih ulica te ostalih javnih površina", P[1]["uvjeti"])
        self.assertTrue(all(p["izvorni_citat"].count("ul.") == 1 for p in P))
        L = pravila(24, "regulacija")
        self.assertEqual(sorted(p["vrijednost"] for p in L), [4.0, 10.0])

    def test_udaljenost_ovisna_o_visini_nije_konacan_broj(self):
        for cl in (20, 23):
            P = pravila(cl, "udaljenostOdGraniceCestice")
            P = [p for p in P if p.get("formula") and p["formula"].get("ovisi_o") == "visina građevine"]
            self.assertEqual(len(P), 2, cl)
            for p in P:
                self.assertEqual(p["status"], "PREGLED")
                self.assertIn("OVISI_O_VISINI", p["razlog_kod"])
                self.assertEqual(len(p["formula"]["grane"]), 2)

    def test_nove_kategorije_na_pregledu(self):
        for par in ("visinaOgradeMax", "visinaPunogDijelaOgradeMax", "visinaPodzidaMax", "visinaKaskadeMax", "odmakKaskade",
                    "zeleniloMin", "povrsinaKrovneKuciceMax", "povrsinaPodzemnihMax"):
            P = pravila(19, par)
            self.assertTrue(P, par)
            self.assertTrue(all(p["status"] == "PREGLED" and "KATEGORIJA_NEVALIDIRANA" in p["razlog_kod"] for p in P), par)

    def test_zelenilo_vrsta_iz_teksta(self):
        self.assertEqual(jedno(19, "zeleniloMin", 30.0)["vrsta_gradevine"]["skupine"], ["ugostiteljsko_turisticka"])
        self.assertEqual(jedno(19, "zeleniloMin", 20.0)["vrsta_gradevine"]["skupine"], ["poslovna"])

    def test_pomocne_u_alineji_su_pregled(self):
        P = [p for p in pravila(20) if p["id"].startswith("v25.") and "pomocna" in (p["vrsta_gradevine"]["skupine"] or [])]
        self.assertGreaterEqual(len(P), 6)
        self.assertTrue(all(p["status"] == "PREGLED" for p in P))
        self.assertTrue(all(p["operator"] == "=" for p in P if p["parametar"] == "udaljenostOdGraniceCestice"))

    def test_nagib_stupanj_slovom_o(self):
        z, lit = g5.oblici("Krovna ploha građevina može se izvesti kao kosa nagiba između 18o i 25o, ravna ili drugog oblika;", {})
        self.assertEqual([(x["parametar"], x["vrijednost"]) for x in z][1:], [("nagibKrovaMin", 18.0), ("nagibKrovaMax", 25.0)])
        self.assertEqual(z[1]["uvjeti"], ["kosa"])


class Zastite(unittest.TestCase):
    def test_podalineja_nosi_kontekst_nadredjene(self):
        P = [p for p in pravila(24) if p["parametar"] in ("nagibKrovaMin", "nagibKrovaMax", "oblikKrovista", "pokrovKosogKrova")]
        self.assertEqual(len(P), 4)
        for p in P:
            self.assertEqual(p["status"], "PREGLED")
            self.assertIn("KONTEKST_NADREDJENE_ALINEJE", p["razlog_kod"])
            self.assertEqual(p["vrsta_pravila"], "IZNIMKA")
            self.assertTrue(any(o.get("oznaka") == "K24" for o in p["prostorni_obuhvat"]))

    def test_naslov_podbloka_nije_nadredjena_alineja(self):
        self.assertFalse([p for p in pravila(19) if p.get("nadredjeni_uvod")])

    def test_izgubljen_kontekst_nije_prihvacen(self):
        for k in ("nv", "ppug", "upu1"):
            for c in rez(k)["clanci"].values():
                for p in c.get("pravila", []):
                    if p["status"] == "PRIJEDLOG" and p["obrazac"] != "gramatika-v1":
                        self.assertTrue(p["vrsta_gradevine"].get("skupine"), p["id"])

    def test_nijedno_prihvaceno_bez_doslovnog_citata(self):
        for c in rez("nv")["clanci"].values():
            T = None
            for p in c.get("pravila", []):
                self.assertIn(p["izvorni_citat"][:50].replace("․", "."), p["izvorni_citat"])
                self.assertNotIn("․", p["izvorni_citat"])

    def test_v24_pravila_ne_postaju_blaza(self):
        """Svako pravilo v2.4 postoji u v2.5 s istim parametrom, operatorom i vrijednošću; status može samo ostati ili ići na PREGLED."""
        for k in ("ppug", "upu1"):
            a = {p["id"]: p for c in rez(k, s24)["clanci"].values() for p in c.get("pravila", [])}
            b = {p["id"]: p for c in rez(k)["clanci"].values() for p in c.get("pravila", [])}
            for i, p in a.items():
                self.assertIn(i, b, (k, i))
                q = b[i]
                self.assertEqual((p["parametar"], p["operator"], p["vrijednost"]), (q["parametar"], q["operator"], q["vrijednost"]), (k, i))
                if p["status"] == "PREGLED":
                    self.assertEqual(q["status"], "PREGLED", (k, i))

    def test_cijeli_upu1_bez_novih_neprovjerenih_prihvacanja(self):
        """Cijeli UPU 1 (i članci bez reference): nijedno pravilo koje je u v2.4 na pregledu ne postaje u v2.5 prihvaćeno."""
        d = izdvoji_tekst(IZ, dio=2)
        a, b = s24.strukturiraj(d, None, "u1"), s25.strukturiraj(d, None, "u1")
        kl = lambda p: (p["clanak"], p["stavak"], p.get("blok"), p["parametar"], p["operator"], str(p["vrijednost"]), p["izvorni_citat"])
        A = {}
        for c in a["clanci"].values():
            for p in c.get("pravila", []):
                A.setdefault(kl(p), []).append(p["status"])
        for c in b["clanci"].values():
            for p in c.get("pravila", []):
                if p["status"] == "PRIJEDLOG" and kl(p) in A:
                    self.assertIn("PRIJEDLOG", A[kl(p)], p["id"])

    def test_vrsta_novim_putem_nije_prihvacena(self):
        P = [p for c in rez("nv")["clanci"].values() for p in c.get("pravila", []) if "VRSTA_IZ_UVODA_V25" in p["razlog_kod"]]
        self.assertTrue(P)
        self.assertTrue(all(p["status"] == "PREGLED" for p in P))

    def test_upu2_nepromijenjen(self):
        """UPU 2: ista pravila i statusi; v2.5 smije samo dodati razlog KONTEKST_IZGUBLJEN pravilu koje je već na pregledu."""
        a, b = rez("upu2", s24), rez("upu2")
        for k, c in a["clanci"].items():
            pa, pb = c.get("pravila", []), b["clanci"][k].get("pravila", [])
            self.assertEqual(len(pa), len(pb), k)
            for x, y in zip(pa, pb):
                if x == y:
                    continue
                self.assertEqual(x["status"], "PREGLED", k)
                dod = [r for r in y["razlog_kod"] if r not in x["razlog_kod"]]
                self.assertEqual(dod, ["KONTEKST_IZGUBLJEN"], k)
                self.assertEqual({kk: v for kk, v in x.items() if kk not in SAMO_V25},
                                 {kk: v for kk, v in y.items() if kk not in SAMO_V25}, k)

    def test_bez_pravne_potvrde(self):
        r = rez("nv")
        self.assertEqual(r["automatska_potvrda"], 0)
        self.assertFalse(r["pravno_potvrdeno"])

    def test_determinizam(self):
        a = s25.strukturiraj(dok("nv"), None, "nv")
        self.assertEqual(json.dumps(a, sort_keys=True, ensure_ascii=False), json.dumps(rez("nv"), sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()

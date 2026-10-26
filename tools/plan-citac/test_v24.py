"""Testovi v2.4: alineje o pomoćnim građevinama. Testovi v1, v2.1, v2.2 i v2.3 ostaju i moraju prolaziti."""
import hashlib, json, unittest
from pathlib import Path
from citac_tekst import izdvoji_tekst
import strukturiraj_v22 as s22
import strukturiraj_v23 as s23
import strukturiraj_v24 as s24
import gramatika_v24 as g4
import usporedi_v22 as U

M = Path(__file__).resolve().parent
IZ = M / U.U.IZVOR
_C = {}


def dok(k):
    if k not in _C:
        _C[k] = izdvoji_tekst(IZ, dio=1) if k == "ppug" else izdvoji_tekst(IZ, [14, 24], dio=2)
    return _C[k]


def rez(k, mod=s24):
    kk = (k, mod.__name__)
    if kk not in _C:
        _C[kk] = mod.strukturiraj(dok(k), None, k)
    return _C[kk]


def nova(k, cl, st=None):
    return [p for p in rez(k)["clanci"][str(cl)]["pravila"] if p["id"].startswith("v24.") and (st is None or p["stavak"] == st)]


def jedno(P, par, v=None):
    L = [p for p in P if p["parametar"] == par and (v is None or p["vrijednost"] == v)]
    assert len(L) == 1, (par, v, len(L))
    return L[0]


class PomocneGradjevine(unittest.TestCase):
    def test_cl39_50m2(self):
        p = jedno(nova("ppug", 39, 2), "tlMax", 50.0)
        self.assertEqual((p["operator"], p["jedinica"], p["status"]), ("<=", "m²", "PRIJEDLOG"))
        self.assertIn("pomocna", p["vrsta_gradevine"]["skupine"])
        self.assertEqual(p["kontekst_primjene"], ["uz građevine društvene i sportsko-rekreacijske namjene"])
        self.assertEqual(p["dodatni_uvjeti"], [])
        self.assertEqual(p["izvor_konteksta"]["clanak"], 39)
        self.assertIn("50 m 2", p["izvorni_citat"])

    def test_visina_dvije_vrijednosti_uvijek_pregled(self):
        for cl, st in [(20, 3), (39, 2), (50, 4)]:
            P = nova("ppug", cl, st)
            a, b = jedno(P, "visinaMax", "visina osnovne građevine"), jedno(P, "visinaMax", 4.0)
            for p in (a, b):
                self.assertEqual(p["status"], "PREGLED")
                self.assertIn("REFERENTNA_VISINA_NEPOTPUNA", p["razlog_kod"])
                self.assertEqual(p["referenca"], "od najniže kote konačno zaravnatog terena")

    def test_etaze_i_udaljenost_s_otvorima(self):
        P = nova("ppug", 50, 4)
        e = jedno(P, "etazeMax")
        self.assertEqual((e["operator"], e["vrijednost"]), ("=", "jednoetažne"))
        u = jedno(P, "udaljenostOdGraniceCestice", 4.0)
        self.assertEqual(u["vrsta_pravila"], "UVJETNO")
        self.assertEqual(u["dodatni_uvjeti"], ["Ako imaju otvore prema susjednoj građevnoj čestici"])
        self.assertEqual(u["kontekst_primjene"], ["uz građevine gospodarske namjene"])

    def test_iznimka_povijesne_cjeline_cijela_alineja(self):
        P = [p for p in nova("ppug", 20, 3) if p["alineja"] == 6]
        self.assertTrue(P)
        for p in P:
            self.assertEqual(p["vrsta_pravila"] if p["vrsta_pravila"] != "NEGATIVNO" else "IZNIMKA", "IZNIMKA")
            self.assertIn("unutar registriranih i evidentiranih povijesnih graditeljskih cjelina", p["dodatni_uvjeti"])
            self.assertIn("POVIJESNA_CJELINA", [o["vrsta"] for o in p["prostorni_obuhvat"]])
        self.assertEqual(jedno(P, "udaljenostOdGraniceCestice")["vrijednost"], 3.0)

    def test_polozaj_na_cestici(self):
        p = [p for p in nova("ppug", 20, 3) if p["parametar"] == "nacinPrislanjanja" and p["alineja"] == 4][0]
        self.assertEqual((p["operator"], p["vrijednost"]), ("dopusteno", "do granice građevne čestice"))

    def test_krovista_alineja_sa_zarezom(self):
        P = [p for p in nova("ppug", 39, 2) if p["alineja"] == 3]
        self.assertEqual(sorted(p["parametar"] for p in P), sorted(["oblikKrovista", "vrstaKosogKrovista", "nagibKrovaMin", "nagibKrovaMax", "pokrovKosogKrova"]))
        self.assertFalse([p for p in P if "NEISKORISTENI_BROJEVI" in p["razlog_kod"]])

    def test_izvan_popisa_uvijek_pregled(self):
        for k in ("ppug", "upu1"):
            for c in rez(k)["clanci"].values():
                for p in c.get("pravila", []):
                    if p["parametar"] in ("vatrobraniZid", "nagibPremaSusjednoj", "garazaNaRegulaciji"):
                        self.assertEqual(p["status"], "PREGLED"); self.assertIn("PARAMETAR_IZVAN_POPISA", p["razlog_kod"])

    def test_upu1_blok7(self):
        P = [p for p in nova("upu1", 24) if p.get("blok") == 7]
        self.assertTrue(jedno(P, "udaljenostOdGraniceCestice", 4.0))
        self.assertEqual(jedno(P, "etazeMax")["vrijednost"], "jednoetažna")
        for p in P:
            self.assertEqual(p["kontekst_primjene"], ["uz građevinu osnovne namjene"])


class ObveznaPolja(unittest.TestCase):
    def test_svako_pravilo_v24(self):
        for k in ("ppug", "upu1"):
            for kk, c in rez(k)["clanci"].items():
                for p in c.get("pravila", []):
                    if not p["id"].startswith("v24."):
                        continue
                    self.assertTrue(p["izvorni_citat"])
                    self.assertIn(p["izvorni_citat"], dok(k)["clanci"][kk]["tekst"])
                    for f in ("kontekst_primjene", "dodatni_uvjeti", "prostorni_obuhvat", "izvor_konteksta"):
                        self.assertIn(f, p)
                    self.assertTrue(p["prostorni_obuhvat"])
                    self.assertEqual(p["primjenjivost_na_lokaciju"], "NIJE_UTVRĐENA")
                    self.assertFalse(p["pravno_potvrdeno"])
                    for u in p["uvjeti"]:
                        self.assertIn(u.lower(), dok(k)["clanci"][kk]["tekst"].lower())


class Regresija(unittest.TestCase):
    def test_pravila_v23_nepromijenjena(self):
        """Pravila koja postoje u v2.3 u v2.4 su ista (v2.4 samo dodaje pravila i uklanja preuzete rečenice iz odbijenih)."""
        for k in ("ppug", "upu1"):
            A = {p["id"]: p for c in rez(k, s23)["clanci"].values() for p in c.get("pravila", [])}
            B = {p["id"]: p for c in rez(k)["clanci"].values() for p in c.get("pravila", [])}
            self.assertTrue(set(A) <= set(B))
            for i, p in A.items():
                self.assertEqual(json.dumps(p, sort_keys=True, ensure_ascii=False), json.dumps(B[i], sort_keys=True, ensure_ascii=False), i)

    def test_zamrznute_v22_v23(self):
        for f in ("ZAMRZNUTO_v2_2.json", "ZAMRZNUTO_v2_3.json"):
            z = json.loads((M / f).read_text(encoding="utf-8"))
            for p, s in z["kod"].items():
                self.assertEqual(hashlib.sha256((M / p).read_bytes()).hexdigest(), s, (f, p))

    def test_determinizam(self):
        a = s24.zapisi_json(s24.strukturiraj(dok("ppug"), None, "PPUG"), "/dev/null")
        b = s24.zapisi_json(s24.strukturiraj(dok("ppug"), None, "PPUG"), "/dev/null")
        self.assertEqual(a, b)

    def test_upu2_nepromijenjen(self):
        d2 = json.loads((M / "izlaz/upu2_kornic_sn_19_2016.json").read_text(encoding="utf-8"))
        a, b = s22.strukturiraj(d2, None, "UPU 2"), s24.strukturiraj(d2, None, "UPU 2")
        for k in ("38", "39", "40"):
            self.assertEqual([(p["parametar"], p["vrijednost"], p.get("uvjet")) for p in a["clanci"][k]["pravila"]],
                             [(p["parametar"], p["vrijednost"], p.get("uvjet")) for p in b["clanci"][k]["pravila"]])

    def test_oblici_ne_izmisljaju(self):
        self.assertIsNone(g4.oblici("visina građevine je primjerena okolišu", {}))
        self.assertIsNone(g4.oblici("tlocrtna projekcija može biti veća od 50 m 2", {}))


if __name__ == "__main__":
    unittest.main()

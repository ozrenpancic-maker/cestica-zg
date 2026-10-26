"""Regresijski testovi čitača na službenom PDF-u UPU-a 2 Kornić (SN PGŽ 19/2016) iz repozitorija.
Pokretanje: python3 -m unittest -v test_citac   (iz mape tools/plan-citac; treba PyMuPDF)"""
import difflib, hashlib, re, unittest
from pathlib import Path
from citac import izdvoji, brojevi, ima_broj, navod

KORIJEN = Path(__file__).resolve().parents[2]
MAPA = KORIJEN / "tests/pgz-odgovori/735-76-kornic-2026-10-22/sn-19-16"
PDF = MAPA / "odluka_34138.pdf"
SHA = "5b4ec76db4232f3efad0dd7ad01e109130bcc3a2702c95ff9857bf48590eae08"
NASLOV = "UPU 2 - Kornić"

try:
    import pymupdf  # noqa: F401
    IMA_PDF = True
except ImportError:
    IMA_PDF = False


@unittest.skipUnless(IMA_PDF, "PyMuPDF nije instaliran")
class StvarniPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = izdvoji(PDF, NASLOV, 108)
        cls.C = cls.r["clanci"]

    # 1. granice odluke po sadržaju
    def test_izvor_je_repozitorijski_pdf(self):
        self.assertEqual(hashlib.sha256(PDF.read_bytes()).hexdigest(), SHA)
        self.assertEqual(self.r["sha256"], SHA)

    def test_granice_po_sadrzaju(self):
        g = self.r["granice"]
        self.assertTrue(g["pocetak"]["tekst"].startswith("ODLUKU o donošenju Urbanističkog plana uređenja"))
        self.assertEqual(g["kraj"]["klasa"], "350-02/15-02/06")
        # prva odluka u PDF-u (izmjene DPU-a, Klasa 350-03/15-01/01) i sljedeća (komunalni red) ne ulaze
        self.assertTrue(self.C["1"]["tekst"].startswith("Donosi se Urbanistički plan uređenja UPU 2 - Kornić"))
        self.assertEqual(self.C["108"]["tekst"], "Ova Odluka stupa na snagu osmoga dana od dana objave u »Službenim novinama Primorsko-goranske županije«.")
        svi = " ".join(c["tekst"] for c in self.C.values())
        self.assertNotIn("Odluke o komunalnom redu", svi)
        self.assertNotIn("Zakona o komunalnom gospodarstvu", svi)
        self.assertNotIn("Klasa:", svi)

    def test_krivi_naslov_odbija(self):
        r = izdvoji(PDF, "UPU 99 - Nepostojeći", 108)
        self.assertEqual(r["status"], "ABSTAIN_GRANICA_ODLUKE")
        self.assertEqual(r["clanci"], {})

    # 2. svih 108 članaka redom
    def test_108_clanaka_redom(self):
        self.assertEqual(self.r["status"], "IZDVOJENO_NIJE_PRAVNA_PROVJERA")
        self.assertEqual(self.r["problemi"], [])
        self.assertEqual([int(k) for k in self.C], list(range(1, 109)))
        for n in ("38", "39", "40", "83", "85"):
            self.assertIn(self.C[n]["izvor"]["stupac"], ("L", "D"))
        self.assertEqual((self.C["38"]["izvor"]["stranica"], self.C["83"]["izvor"]["stranica"], self.C["85"]["izvor"]["stranica"]), (13, 22, 23))
        self.assertTrue(self.C["83"]["tekst"].startswith("(1) Zona unutar obuhvata Plana koja ima svojstvo kulturnog dobra"))
        self.assertTrue(self.C["85"]["tekst"].startswith("(1) Zona »C« navedena u članku 83. ovih Odredbi"))

    def test_sadrzaj_odgovara_neovisnom_izdvajanju(self):
        """Tekst svakog članka mora se u cijelosti, istim redom, nalaziti u izdvajanju istog PDF-a drugim alatom
        (pdftotext, odluka_34138_pdf_tekst.txt), uz zanemarene razmake, interpunkciju i crtice na kraju retka."""
        t = (MAPA / "odluka_34138_pdf_tekst.txt").read_text(encoding="utf-8")
        heads, seq, w = [(int(m.group(1)), m.start(), m.end()) for m in re.finditer(r"Članak\s*(\d+)\s*\.", t)], [], 1
        for h in heads:
            if h[0] == w:
                seq.append(h); w += 1
        kraj = t.find("Klasa: 350-02/15-02/06")
        N = lambda s: re.sub(r"[^0-9a-zčćđšž]", "", re.sub(r"-\s*\n\s*", "", s).translate(str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉", "01234567890123456789")).lower())
        for i, (n, _, e) in enumerate(seq[:108]):
            A = N(self.C[str(n)]["tekst"].replace("[TABLICA – nije pouzdano rekonstruirana, vidi str. 17]", ""))
            B = N(t[e:(seq[i + 1][1] if i + 1 < 108 else kraj)])
            m = sum(b.size for b in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks())
            self.assertGreaterEqual(m / len(A), 0.995, f"čl. {n}")

    # 5. tablice
    def test_tablica_cl_53_oznacena(self):
        c = self.C["53"]
        self.assertEqual(c["status_tablica"], "TABLICA_NEPOUZDANA")
        self.assertIn("[TABLICA – nije pouzdano rekonstruirana, vidi str. 17]", c["tekst"])
        self.assertNotIn("ležaja", c["tekst"])  # ćelije ne ulaze u tekst članka
        self.assertIn("(2) Potrebne parkirališne površine", c["tekst"])
        self.assertEqual([(T["clanak"], T["stranica"], T["status"]) for T in self.r["tablice"]], [(53, 17, "TABLICA_NEPOUZDANA")])
        celije = " ".join(b["tekst"] for b in self.r["tablice"][0]["blokovi"])
        self.assertIn("Stanovanje 2 mjesta 1 stan", celije)  # izvorne ćelije čuvaju se za ručnu provjeru
        self.assertEqual(sum(1 for x in self.C.values() if x["status_tablica"]), 1)

    # 6. zaglavlja i naslovi poglavlja
    def test_zaglavlja_uklonjena(self):
        self.assertEqual(self.r["zaglavlja_uklonjena"], 29)
        for c in self.C.values():
            self.assertNotRegex(c["tekst"], r"Stranica \d+ — broj|SLUŽBENE NOVINE|Petak, 29\. srpnja")
        self.assertIn("kada njegove dimenzije", self.C["53"]["tekst"])  # riječ rastavljena preko prijeloma stranice

    def test_naslovi_odvojeni(self):
        self.assertTrue(self.C["19"]["tekst"].endswith("primjenjuju se odredbe članka 15."))
        self.assertTrue(self.C["20"]["tekst"].endswith("primjenjuju se odredbe članka 16."))
        self.assertTrue(self.C["21"]["poglavlje"].startswith("2.2.3. Uvjeti rekonstrukcije na građevnoj čestici poslovne građevine"))
        self.assertIn("4.1. UVJETI GRADNJE OBITELJSKE ILI VIŠEOBITELJSKE KUĆE", self.C["38"]["poglavlje"])
        self.assertIn("4.1.1. Uvjeti gradnje slobodnostojeće obiteljske ili slobodnostojeće višeobiteljske kuće", self.C["38"]["poglavlje"])
        self.assertTrue(self.C["39"]["poglavlje"].startswith("4.1.2. Uvjeti gradnje dvojne ili ugrađene obiteljske"))
        for n, c in self.C.items():
            if n != "86":
                self.assertNotRegex(c["tekst"], r"\s\d+(?:\.\d+)+\. [A-ZČĆĐŠŽ]{3,} [A-ZČĆĐŠŽ]{3,}", n)  # npr. »4.1. UVJETI GRADNJE«
        # u izvoru poglavlje 7.3. nema vlastiti članak, pa je dio čl. 86: ostaje u tekstu i bilježi se
        self.assertEqual([x["tekst"] for x in self.C["86"]["unutarnji_naslovi"]], ["7.3. MJERE ZAŠTITE AMBIJENTALNIH VRIJEDNOSTI"])
        self.assertEqual(sorted(n for n, c in self.C.items() if c.get("unutarnji_naslovi")), ["86"])
        # nabrajanje u čl. 3 (popis poglavlja odredbi) nije naslov
        self.assertIn("1. Uvjeti određivanja i razgraničavanja površina javnih i drugih namjena", self.C["3"]["tekst"])

    # 7. dijakritici i rastavljene riječi, uz izvorni tekst
    def test_dijakritici(self):
        for c in self.C.values():
            self.assertNotRegex(c["tekst"], r"[ˇ´¯]|Č lanak")
        t38 = self.C["38"]["tekst"]
        for r in ("slobodnostojeće", "višeobiteljske", "građevne čestice", "najveći koeficijent iskorištenosti"):
            self.assertIn(r, t38)
        self.assertIn("slobodnostojec´e", self.C["38"]["sirovo"])  # izvorni zapis ostaje za provjeru
        self.assertIn("Kornić", self.C["1"]["tekst"])
        # indeks i eksponent iz manjeg fonta: oznaka zone »M1₁« (u planu M1 s indeksom 1), »m²«
        self.assertIn("pretežito stambene (M1₁) ili pretežito poslovne (M2)", self.C["20"]["tekst"])
        self.assertIn("iznosi 500 m², a iznimno 400 m²", self.C["38"]["tekst"])

    def test_rastavljene_rijeci(self):
        self.assertIn("tradicijskim suhozidima", self.C["85"]["tekst"])
        self.assertIn("Primorsko-goranske županije", self.C["107"]["tekst"])  # prava crtica se čuva
        self.assertNotIn("Primorskogoranske", " ".join(c["tekst"] for c in self.C.values()))
        self.assertIn("VIŠEOBITELJSKE", self.C["38"]["poglavlje"])

    # 3. brojevi na stvarnim odlomcima
    def test_brojevi_cl_38(self):
        t = self.C["38"]["tekst"]
        self.assertIn("iznosi 0,25,", t)
        self.assertFalse(ima_broj("zona (M1₁)", 1)); self.assertFalse(ima_broj("zona (M1₁)", 11))
        self.assertTrue(ima_broj(t, 0.25)); self.assertTrue(ima_broj(t, 0.75)); self.assertTrue(ima_broj(t, 1.0))
        self.assertTrue(ima_broj(t, 0.4, "%"))  # »najmanje 40% površine građevne čestice«
        self.assertTrue(ima_broj(t, 500, "m²")); self.assertTrue(ima_broj(t, 400, "m²"))
        self.assertTrue(ima_broj(t, 7.5, "m"))
        lit = [(b["literal"], b["jedinica"]) for b in brojevi(t)]
        self.assertEqual(lit[:6], [("500", "m²"), ("400", "m²"), ("500", "m²"), ("0,25", None), ("0,75", None), ("1,0", None)])
        self.assertNotIn(("2", None), lit[:6])  # eksponent u »m2« nije vrijednost

    def test_brojevi_bez_laznih(self):
        i = self.C["38"]["tekst"].find("iznosi 7,5 m")
        odl = self.C["38"]["tekst"][i:i + 200]
        self.assertTrue(ima_broj(odl, 1.5, "m")); self.assertFalse(ima_broj(odl, 1.0, "m"))
        z = self.C["85"]["tekst"][:60]  # »(1) Zona »C« navedena u članku 83. ovih Odredbi …«
        self.assertEqual(brojevi(z), [])
        self.assertEqual(brojevi(self.C["83"]["tekst"][:400])[:1], [])  # »(1)«, »Z-5332« i k.č. nisu vrijednosti

    def test_oznake_parkiralista_nisu_uvjet(self):
        """Čl. 52. st. 6.: »- P₁ - 15 - P₂ - 5 …« su broj mjesta po parkiralištu; vrijednost se veže uz oznaku."""
        t = self.C["52"]["tekst"]
        self.assertIn("- P₁ - 15 - P₂ - 5 - P₃ - 5 - P₄ - 5 - P₅ - 3 - P₆ - 10 - P₇ - 15", t)
        ozn = [(b["oznaka"], b["literal"]) for b in brojevi(t) if b["oznaka"]]
        self.assertEqual(ozn, [("P₁", "15"), ("P₂", "5"), ("P₃", "5"), ("P₄", "5"), ("P₅", "3"), ("P₆", "10"), ("P₇", "15")])
        self.assertFalse(ima_broj(t, 15)); self.assertFalse(ima_broj(t, 10)); self.assertFalse(ima_broj(t, 1))
        self.assertTrue(ima_broj(t, 15, oznaka="P₁")); self.assertFalse(ima_broj(t, 10, oznaka="P₁"))
        self.assertFalse(any(b["literal"] in ("1", "2", "7") for b in brojevi(t) if b["oznaka"]))  # indeks oznake nije broj
        svi = [(n, b["oznaka"]) for n, c in self.C.items() for b in brojevi(c["tekst"]) if b["oznaka"]]
        self.assertEqual({n for n, _ in svi}, {"52"})  # nigdje drugdje broj nije vezan uz oznaku
        self.assertFalse(ima_broj("parkirališta P₁ i P₇", 1)); self.assertFalse(ima_broj("parkirališta P1 i P7", 7))

    def test_tablica_ne_daje_brojeve(self):
        """Ćelije tablice čl. 53 ne ulaze u tekst članka, pa iz nje ne može nastati brojčani dokaz."""
        t = self.C["53"]["tekst"]
        self.assertFalse(ima_broj(t, 2)); self.assertFalse(ima_broj(t, 30)); self.assertFalse(ima_broj(t, 1000, "m²"))
        self.assertTrue(all(c["status_tablica"] is None for n, c in self.C.items() if n != "53"))

    def test_bez_pravne_potvrde(self):
        self.assertEqual(self.r["automatska_potvrda"], 0)
        self.assertFalse(self.r["pravno_potvrdeno"])


class Brojevi(unittest.TestCase):
    def test_zarez_na_kraju_alineje(self):
        self.assertEqual([b["literal"] for b in brojevi("koeficijent izgrađenosti iznosi 0,25, - najveći")], ["0,25"])
        self.assertEqual([b["literal"] for b in brojevi("iznosi 0,75, a iznimno 1,0 ako")], ["0,75", "1,0"])

    def test_decimale_i_postotak(self):
        self.assertFalse(ima_broj("visine 1,5 m", 1.0, "m"))
        self.assertTrue(ima_broj("najmanje 40% površine", 0.4, "%"))
        self.assertFalse(ima_broj("najmanje 40% površine", 40, "m"))

    def test_oznake_nisu_vrijednosti(self):
        for t in ("(1) Zona", "u članku 83. ovih", "u člancima 26., 27. i 28. ovih", "k.č. 88/4", "broj 7/07", "mjerilu 1:5000",
                  "prikazu br. 4", "zona M11", "lokalna cesta L 58091", "od 2010. do", "500 m 2,"):
            self.assertEqual([b["literal"] for b in brojevi(t) if b["literal"] not in ("500",)], [], t)

    def test_jedinice(self):
        self.assertEqual([(b["literal"], b["jedinica"]) for b in brojevi("visine 2-5 m, nagib 17o i 23o, 2,5x5,0 m, 55 dB")],
                         [("2", "m"), ("5", "m"), ("17", "°"), ("23", "°"), ("2,5", "m"), ("5,0", "m"), ("55", "dB")])


class Navodi(unittest.TestCase):
    def test_navodi(self):
        self.assertEqual(navod("22")["clanci"], [22])
        self.assertEqual(navod("38. i 39.")["clanci"], [38, 39])
        self.assertEqual(navod("čl. 38.–40.")["clanci"], [38, 39, 40])
        n = navod("čl. 33. st. 3.–4.; čl. 17.")
        self.assertEqual((n["clanci"], n["stavci"]), ([17, 33], [3, 4]))
        n = navod("čl. 83. st. 1.–2.; čl. 38.")
        self.assertEqual((n["clanci"], n["stavci"]), ([38, 83], [1, 2]))
        n = navod("pojmovnik, točka 31.")
        self.assertEqual((n["vrsta"], n["clanci"], n["tocke"]), ("POJMOVNIK", [], [31]))
        self.assertEqual(navod("38. d)")["tocke"], ["d"])
        n = navod("UPU2 čl. 83.")
        self.assertEqual((n["plan"], n["clanci"]), ("UPU2", [83]))
        self.assertEqual(navod("")["vrsta"], "NEPOZNATO")

    def test_nabrojeni_stavci_nisu_clanci(self):
        """Neovisna provjera: »čl. 38. st. 2. i 3.« vraćao je članke [3, 38] i stavke [2]."""
        for s, cl, st in (("čl. 38. st. 2. i 3.", [38], [2, 3]), ("čl. 38. st. 1. i 2.", [38], [1, 2]),
                          ("čl. 38. st. 1., 2. i 4.", [38], [1, 2, 4]), ("čl. 38. stavak 2. ili 3.", [38], [2, 3]),
                          ("čl. 38. st. 1.–3. i 5.", [38], [1, 2, 3, 5]), ("čl. 38. st. 1. i 3.–4.", [38], [1, 3, 4]),
                          ("čl. 38. st. 2. do 4.", [38], [2, 3, 4]), ("UPU2 čl. 38. st. 2. i 3.", [38], [2, 3])):
            n = navod(s)
            self.assertEqual((n["clanci"], n["stavci"]), (cl, st), s)
            self.assertEqual(n["parovi"], [{"clanak": 38, "stavci": st}], s)

    def test_vise_clanaka_sa_stavcima(self):
        n = navod("čl. 38. st. 2. i 3.; čl. 39. st. 1.")
        self.assertEqual(n["parovi"], [{"clanak": 38, "stavci": [2, 3]}, {"clanak": 39, "stavci": [1]}])
        n = navod("čl. 38., 39. i 41.")
        self.assertEqual((n["clanci"], n["stavci"]), ([38, 39, 41], []))
        n = navod("čl. 38.–40.")
        self.assertEqual([p["clanak"] for p in n["parovi"]], [38, 39, 40])
        n = navod("čl. 85. st. 2. t. 3.")
        self.assertEqual((n["clanci"], n["stavci"], n["tocke"]), ([85], [2], [3]))


if __name__ == "__main__":
    unittest.main()

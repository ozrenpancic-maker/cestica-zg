#!/usr/bin/env python3
"""Validacijski testovi za v0.18.5: vlastiti broj SN, datum objave, razrješavanje ciljnog akta.

Pokretanje:  python3 -m unittest tools/sn-pgz/test_sn_identitet.py   (ili python3 test_sn_identitet.py)
Bez interneta. Testovi nad korpusom se preskaču ako nije zadan CESTICA_KORPUS=putanja_do_json.
Testovi nad stvarnim HTML-om Data Managera: CESTICA_HTML_DIR (vidi ispit_html_direktorija).

SINTETIČKE fiksture su označene SYN_; stvarni su samo zapisi iz tests/zlatni/sn-portal-sidro-v1.json.
"""
import json
import os
import re
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import sn_identitet_provjera as P  # noqa: E402

KORIJEN = Path(__file__).resolve().parents[2]
SIDRO = json.load(open(KORIJEN / "tests/zlatni/sn-portal-sidro-v1.json", encoding="utf-8"))


def zapis(pid, izd, mj, red, broj, god, datum, naziv="Odluka", izvor="PORTAL_ISSUE_LISTING", rim=None):
    z = {"publication_id": str(pid), "izdanje_id": izd, "mjesto_id": mj, "redni_broj_u_izdanju": red,
         "sn_broj": broj, "sn_godina": god, "sn_oznaka": f"{broj}/{god % 100:02d}",
         "datum_izdanja": datum, "naziv_akta": naziv, "izvor_zaglavlja": izvor,
         "izvor_html_sha256": "0" * 64}
    if rim:
        z["godina_toma_rimski"] = rim
    return z


# SYN_: registar sa situacijom "više akata u istom izdanju i istom mjestu" i "isti broj SN, različita mjesta"
SYN_REG = [
    zapis(1, 100, "51521", 1, 5, 2012, "2012-03-01", "Odluka o donošenju UPU 1"),
    zapis(2, 100, "51521", 2, 5, 2012, "2012-03-01", "Odluka o donošenju UPU 2"),
    zapis(3, 100, "51500", 3, 5, 2012, "2012-03-01", "Odluka o donošenju UPU 1 Krk"),
    zapis(4, 101, "51521", 1, 6, 2012, "2012-03-15", "Odluka o izmjeni UPU 1"),
    zapis(5, 90, "51521", 4, 5, 2000, "2000-03-01", "Stari plan"),
]


class TestFooter(unittest.TestCase):
    def test_footer_osnovni(self):
        t = "tekst https://www.sn.pgz.hr/default.asp?Link=odluke&izdanje=851&mjesto=51500&odluka=33 \n© Primorsko"
        self.assertEqual(P.footer_trojka(t), (851, "51500", 33))

    def test_footer_html_entitet(self):
        t = '<a href="default.asp?Link=odluke&amp;izdanje=851&amp;mjesto=51500&amp;odluka=33">x</a>'
        self.assertEqual(P.footer_trojka(t), (851, "51500", 33))

    def test_footer_nema_ili_dvosmislen(self):
        self.assertIsNone(P.footer_trojka("nema"))
        t = "Link=odluke&izdanje=1&mjesto=2&odluka=3 i Link=odluke&izdanje=1&mjesto=2&odluka=4"
        self.assertIsNone(P.footer_trojka(t))  # dva različita -> ne biramo

    def test_ordinal_u_footeru_nije_sn_broj(self):
        # 'odluka=33' je redni broj akta u izdanju, ne broj SN
        self.assertNotEqual(P.footer_trojka("Link=odluke&izdanje=851&mjesto=51500&odluka=33")[2], 851)


POPIS_TABLICA = """<html><body><table>
<tr><td>Službene novine broj 33. Godina XXVIII. Petak, 2. listopada 2020.</td></tr>
<tr><td>Općina PUNAT</td></tr>
<tr><td>60.</td><td><a href="default.asp?Link=odluke&amp;id=41977">Odluka o izradi III. Izmjena i dopuna UPU 3</a></td></tr>
<tr><td>Službene novine broj 3. Godina XXVIII. Petak, 14. veljače 2020.</td></tr>
<tr><td>Općina PUNAT</td></tr>
<tr><td>5.</td><td><a href="default.asp?Link=odluke&amp;id=41087">Odluka o donošenju II. Izmjena i dopuna UPU 3</a>
 <a href="default.asp?Link=odluke&amp;id=31026">Download odluke u PDF formatu</a></td></tr>
<tr><td>Općina VRBNIK</td></tr>
<tr><td>7.</td><td><a href="default.asp?Link=odluke&amp;id=2002">Odluka o donošenju Prostornog plana</a></td></tr>
</table></body></html>"""

POPIS_DIV = """<div class=h>Službene novine broj 33. Godina XXVIII. Petak, 2. listopada 2020.</div>
<div class=m>Općina PUNAT</div>
<p><a href="default.asp?Link=odluke&id=41977">60. Odluka o izradi III. Izmjena i dopuna UPU 3</a></p>
<div class=h>Službene novine broj 3. Godina XXVIII. Petak, 14. veljače 2020.</div>
<div class=m>Općina PUNAT</div>
<p>5. <a href="default.asp?Link=odluke&id=41087">Odluka o donošenju II. Izmjena i dopuna UPU 3</a></p>
<p><a href="default.asp?Link=odluke&id=31026">Download odluke u PDF formatu</a></p>
<div class=m>Općina VRBNIK</div>
<p><a href="default.asp?Link=odluke&id=2002">7. Odluka o donošenju Prostornog plana</a></p>"""


class TestPopisIzdanja(unittest.TestCase):
    def _provjeri(self, h):
        z = {e["publication_id"]: e for e in P.izvuci_popis(h) if not e["pdf"]}
        self.assertEqual(set(z), {"41977", "41087", "2002"})
        self.assertEqual((z["41977"]["izdanje_broj"], z["41977"]["godina"], z["41977"]["datum"], z["41977"]["redni_broj"]), (33, 2020, "2020-10-02", 60))
        self.assertEqual((z["41087"]["izdanje_broj"], z["41087"]["datum"], z["41087"]["redni_broj"]), (3, "2020-02-14", 5))
        self.assertEqual(z["2002"]["mjesto_naziv"], "Općina VRBNIK")
        self.assertEqual(z["2002"]["redni_broj"], 7)
        pdf = [e for e in P.izvuci_popis(h) if e["pdf"]]
        self.assertEqual([e["publication_id"] for e in pdf], ["31026"])
        self.assertIsNone(pdf[0]["redni_broj"])  # PDF poveznica nije zaseban akt

    def test_tablica(self):
        self._provjeri(POPIS_TABLICA)

    def test_div_varijanta(self):
        self._provjeri(POPIS_DIV)  # isto rezultat bez obzira na oznake

    def test_pdf_id_ne_postaje_akt_s_rednim_brojem(self):
        for e in P.izvuci_popis(POPIS_DIV):
            if e["pdf"]:
                self.assertIsNone(e["naslov"])

    def test_opis_strukture_javlja_nepodudaranje(self):
        o = P.opisi_strukturu("<html>nema ničega</html>")
        self.assertEqual((o["zaglavlja_izdanja"], o["zapisa"]), (0, 0))

    def test_rimska_godina(self):
        self.assertEqual(P.rimski("XXVIII"), 28)
        self.assertEqual(P.PRVA_GODINA_TOMA + P.rimski("XXVIII") - 1, 2020)
        self.assertIsNone(P.rimski("XXQ"))


class TestCitati(unittest.TestCase):
    def test_lanac_sn_pgz(self):
        c = P.citati("UPU 2 Njivice (»Službene novine PGŽ« br. 30/10, 36/10 - ispravak odluke, 16/11 i 10/16)")
        self.assertEqual([x["oznaka"] for x in c], ["30/10", "36/10", "16/11", "10/16"])
        self.assertTrue(all(x["gazeta"] == "SN_PGZ" for x in c))
        self.assertEqual([x["ispravak"] for x in c], [False, True, False, False])

    def test_nn_se_ne_miješa_sa_sn(self):
        c = P.citati("Zakon (»Narodne novine« broj 153/13 i 65/17) i plan (SN PGŽ 17/07)")
        self.assertEqual({(x["gazeta"], x["oznaka"]) for x in c}, {("NN", "153/13"), ("NN", "65/17"), ("SN_PGZ", "17/07")})

    def test_isti_broj_u_nn_i_sn_razlicit_zapis(self):
        c = P.citati("»Narodne novine« br. 33/10 i »Službene novine PGŽ« br. 33/10")
        self.assertEqual(sorted(x["gazeta"] for x in c), ["NN", "SN_PGZ"])

    def test_godina_stoljece(self):
        self.assertEqual(P.godina4("00"), 2000)
        self.assertEqual(P.godina4("94"), 1994)
        self.assertEqual(P.godina4("92"), 2092)  # granica 93: dokumentirano; <1993 mora doći s 4-znam. godinom ili SN_STARO
        self.assertEqual(P.godina4("2007"), 2007)
        c = P.citati("»Službene novine PGŽ« broj 17/2007")
        self.assertEqual((c[0]["broj"], c[0]["godina"]), (17, 2007))

    def test_staro_glasilo_prije_1993(self):
        c = P.citati("Odluka o PPU bivše Općine Krk (»Službene novine« br. 31/1978, 6/1983)")
        self.assertTrue(all(x["gazeta"] == "SN_STARO" for x in c))

    def test_razmaci_oko_kose_crte(self):
        c = P.citati("SN PGŽ 7/ 07, 41/09")
        self.assertEqual([x["oznaka"] for x in c], ["7/07", "41/09"])


class TestRazrjesavanje(unittest.TestCase):
    """Slučajevi: više dokumenata citira isti broj SN; isti broj u više mjesta; više akata u istom izdanju+mjestu."""

    def cit(self, oznaka, gaz="SN_PGZ", ispravak=False):
        b, g = oznaka.split("/")
        return {"gazeta": gaz, "broj": int(b), "godina": P.godina4(g), "oznaka": oznaka, "ispravak": ispravak}

    def test_jednoznacno_izdanje_mjesto_ordinal_naslov(self):
        r = P.razrijesi_cilj(self.cit("6/12"), SYN_REG, mjesto_id="51521")
        self.assertEqual((r["status"], r["kandidati"]), ("RESOLVED", ["4"]))

    def test_isti_broj_vise_mjesta_trazi_mjesto(self):
        self.assertEqual(P.razrijesi_cilj(self.cit("5/12"), SYN_REG)["status"], "AMBIGUOUS_NO_MUNICIPALITY")
        r = P.razrijesi_cilj(self.cit("5/12"), SYN_REG, mjesto_id="51500")
        self.assertEqual((r["status"], r["kandidati"]), ("RESOLVED", ["3"]))

    def test_vise_akata_isto_izdanje_isto_mjesto_je_dvosmisleno(self):
        r = P.razrijesi_cilj(self.cit("5/12"), SYN_REG, mjesto_id="51521")
        self.assertEqual((r["status"], sorted(r["kandidati"])), ("AMBIGUOUS", ["1", "2"]))

    def test_sužavanje_samo_uz_dokaz(self):
        self.assertEqual(P.razrijesi_cilj(self.cit("5/12"), SYN_REG, "51521", redni_broj=2)["kandidati"], ["2"])
        self.assertEqual(P.razrijesi_cilj(self.cit("5/12"), SYN_REG, "51521", naslov_dio="UPU 1")["kandidati"], ["1"])
        # naslovni dio koji pogađa oba -> ostaje dvosmisleno
        self.assertEqual(P.razrijesi_cilj(self.cit("5/12"), SYN_REG, "51521", naslov_dio="Odluka o donošenju")["status"], "AMBIGUOUS")

    def test_nn_se_ne_razrjesava_u_sn(self):
        self.assertEqual(P.razrijesi_cilj(self.cit("5/12", gaz="NN"), SYN_REG, "51521")["status"], "WRONG_GAZETTE")

    def test_nepoznat_broj_nije_u_registru(self):
        self.assertEqual(P.razrijesi_cilj(self.cit("99/12"), SYN_REG, "51521")["status"], "NOT_IN_REGISTRY")

    def test_mjesto_bez_akta_u_tom_izdanju(self):
        self.assertEqual(P.razrijesi_cilj(self.cit("6/12"), SYN_REG, "51500")["status"], "NOT_IN_REGISTRY")

    def test_ispravak_nije_izvorni_akt(self):
        r = P.razrijesi_cilj(self.cit("6/12", ispravak=True), SYN_REG, "51521")
        self.assertEqual(r["status"], "CORRECTION_NOTICE")

    def test_dvoznacnost_stoljeca(self):
        # 5/00 i 5/12 su različiti; 5/00 -> 2000, a ne 1900
        self.assertEqual(P.razrijesi_cilj(self.cit("5/00"), SYN_REG, "51521")["kandidati"], ["5"])

    def test_vise_dokumenata_citira_isti_sn_daje_isti_cilj(self):
        # 31 dokumenata citira 6/12 -> razrješenje ne ovisi o citatoru, samo o (oznaka, mjesto)
        rez = {tuple(P.razrijesi_cilj(self.cit("6/12"), SYN_REG, "51521")["kandidati"]) for _ in range(31)}
        self.assertEqual(rez, {("4",)})


class TestRegistar(unittest.TestCase):
    def test_ispravan_registar_bez_povreda(self):
        self.assertEqual([x for x in P.provjeri_registar(SYN_REG) if x["ozbiljnost"] == "FAIL"], [])

    def kodovi(self, reg):
        return {x["kod"] for x in P.provjeri_registar(reg)}

    def test_broj_iz_citata_se_odbija(self):
        r = [dict(z) for z in SYN_REG]
        r[0]["izvor_zaglavlja"] = "TEXT_CITATION"
        self.assertIn("R4_IZVOR_NIJE_PORTAL", self.kodovi(r))

    def test_nedostaje_polje(self):
        r = [dict(z) for z in SYN_REG]
        r[0]["datum_izdanja"] = None
        self.assertIn("R1_NEDOSTAJE_POLJE", self.kodovi(r))

    def test_oznaka_nekonzistentna(self):
        r = [dict(z) for z in SYN_REG]
        r[0]["sn_oznaka"] = "6/12"
        self.assertIn("R2_OZNAKA_NEKONZISTENTNA", self.kodovi(r))

    def test_godina_datuma(self):
        r = [dict(z) for z in SYN_REG]
        r[0]["datum_izdanja"] = "2011-03-01"
        self.assertIn("R3_DATUM_GODINA", self.kodovi(r))

    def test_rimska_godina_mora_odgovarati(self):
        r = [dict(zapis(9, 200, "51521", 1, 33, 2020, "2020-10-02", rim="XXVIII"))]
        self.assertEqual([x for x in P.provjeri_registar(r) if x["ozbiljnost"] == "FAIL"], [])
        r[0]["godina_toma_rimski"] = "XXVII"
        self.assertIn("R3B_RIMSKA_GODINA", self.kodovi(r))

    def test_duplikat_trojke(self):
        r = [dict(z) for z in SYN_REG] + [zapis(77, 100, "51521", 1, 5, 2012, "2012-03-01")]
        self.assertIn("R5_DUPLIKAT_TROJKE", self.kodovi(r))

    def test_isto_izdanje_razliciti_brojevi(self):
        r = [dict(z) for z in SYN_REG]
        r[1].update(sn_broj=7, sn_oznaka="7/12")
        self.assertIn("R6_IZDANJE_RAZLICITE_OZNAKE", self.kodovi(r))

    def test_isti_sn_dva_izdanja(self):
        r = [dict(z) for z in SYN_REG] + [zapis(88, 555, "51521", 1, 6, 2012, "2012-03-15")]
        self.assertIn("R6_OZNAKA_VISE_IZDANJA", self.kodovi(r))

    def test_nemonotono_je_upozorenje_ne_greska(self):
        r = [zapis(1, 10, "1", 1, 5, 2012, "2012-06-01"), zapis(2, 11, "1", 1, 6, 2012, "2012-05-01")]
        v = P.provjeri_registar(r)
        self.assertIn(("R7_NEMONOTONO", "WARN"), {(x["kod"], x["ozbiljnost"]) for x in v})


class TestHtmlKrizno(unittest.TestCase):
    AKT = "tekst akta\nhttps://www.sn.pgz.hr/default.asp?Link=odluke&izdanje=2159&mjesto=51521&odluka=60 \n© PGŽ"

    def z(self, **kw):
        z = zapis(41977, 2159, "51521", 60, 33, 2020, "2020-10-02")
        z.update(kw)
        return z

    def test_slaganje(self):
        self.assertEqual(P.provjeri_akt_html(self.z(), self.AKT, POPIS_TABLICA), [])

    def test_footer_razlika(self):
        v = P.provjeri_akt_html(self.z(redni_broj_u_izdanju=61), self.AKT, POPIS_TABLICA)
        self.assertIn("H2_FOOTER_RAZLIKA", {x["kod"] for x in v})

    def test_popis_razlika_broja_sn(self):
        v = P.provjeri_akt_html(self.z(sn_broj=34, sn_oznaka="34/20"), self.AKT, POPIS_TABLICA)
        self.assertIn("H4_POPIS_RAZLIKA", {x["kod"] for x in v})

    def test_id_koji_nije_u_popisu(self):
        v = P.provjeri_akt_html(self.z(publication_id=99999), self.AKT, POPIS_TABLICA)
        self.assertIn("H3_ID_U_POPISU", {x["kod"] for x in v})

    def test_pdf_id_nije_akt(self):
        v = P.provjeri_akt_html(self.z(publication_id=31026), self.AKT, POPIS_TABLICA)
        self.assertIn("H3_ID_U_POPISU", {x["kod"] for x in v})


class TestSidro(unittest.TestCase):
    def test_sidro_interno_konzistentno(self):
        for z in SIDRO["zapisi"]:
            self.assertEqual(z["datum"][:4], str(z["sn_godina"]))
        zz = {z["publication_id"]: z for z in SIDRO["zapisi"]}
        self.assertEqual(P.PRVA_GODINA_TOMA + P.rimski(zz["41977"]["godina_toma"]) - 1, zz["41977"]["sn_godina"])

    def test_sidro_monotono_izdanje_vs_datum(self):
        s = sorted((z["izdanje_id_korpus"], z["datum"]) for z in SIDRO["zapisi"] if z.get("izdanje_id_korpus"))
        self.assertEqual(s, sorted(s, key=lambda x: x[1]))

    def test_sidro_prolazi_validator(self):
        reg = [zapis(z["publication_id"], z["izdanje_id_korpus"], z["mjesto_id_korpus"], z["redni_broj"], z["sn_broj"], z["sn_godina"], z["datum"])
               for z in SIDRO["zapisi"] if z.get("izdanje_id_korpus")]
        self.assertEqual([x for x in P.provjeri_registar(reg) if x["ozbiljnost"] == "FAIL"], [])


KORPUS = os.environ.get("CESTICA_KORPUS")


@unittest.skipUnless(KORPUS and os.path.exists(KORPUS), "CESTICA_KORPUS nije zadan")
class TestKorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        c = json.load(open(KORPUS, encoding="utf-8"))
        arts = defaultdict(list)
        for a in c["articles"]:
            arts[str(a["document_id"])].append(a["body"])
        cls.doc = {}
        for d in c["documents"]:
            pid = re.search(r"id=(\d+)", d["url"]).group(1)
            cls.doc[pid] = (d, " ".join(arts[str(d["id"])]))

    def test_footer_jedinstven(self):
        tr = Counter()
        for pid, (d, t) in self.doc.items():
            x = P.footer_trojka(t)
            if x:
                tr[x] += 1
        self.assertGreaterEqual(sum(tr.values()), 170)
        self.assertEqual([k for k, v in tr.items() if v > 1], [])

    def test_sidro_se_poklapa_s_footerima(self):
        n = 0
        for z in SIDRO["zapisi"]:
            if z.get("izdanje_id_korpus") and z["publication_id"] in self.doc:
                self.assertEqual(P.footer_trojka(self.doc[z["publication_id"]][1]),
                                 (z["izdanje_id_korpus"], z["mjesto_id_korpus"], z["redni_footer_korpus"]))
                n += 1
        self.assertEqual(n, 4)

    def test_sn_i_mjesto_nisu_dovoljni(self):
        """Dokaz da razrješavanje samo po (izdanje, mjesto) nije jednoznačno: 73 od 172 dokumenta dijele grupu."""
        g = defaultdict(list)
        for pid, (d, t) in self.doc.items():
            x = P.footer_trojka(t)
            if x:
                g[(x[0], x[1])].append(pid)
        dvosmisleni = sum(len(v) for v in g.values() if len(v) > 1)
        self.assertGreater(dvosmisleni, 0)
        self.assertEqual((len(g), dvosmisleni), (128, 73))

    def test_citati_isti_sn_vise_dokumenata(self):
        m = defaultdict(set)
        for pid, (d, t) in self.doc.items():
            for c in P.citati(t):
                if c["gazeta"] == "SN_PGZ":
                    m[c["oznaka"]].add(pid)
        self.assertTrue(any(len(v) > 10 for v in m.values()))  # npr. 01/08, 11/12 itd.

    def test_isti_broj_u_nn_i_sn(self):
        nn, sn = set(), set()
        for pid, (d, t) in self.doc.items():
            for c in P.citati(t):
                (nn if c["gazeta"] == "NN" else sn if c["gazeta"] == "SN_PGZ" else set()).add(c["oznaka"])
        self.assertGreater(len(nn & sn), 0)


HTML_DIR = os.environ.get("CESTICA_HTML_DIR")


@unittest.skipUnless(HTML_DIR and os.path.isdir(HTML_DIR or ""), "CESTICA_HTML_DIR nije zadan")
class TestStvarniHtml(unittest.TestCase):
    """Nad HTML-om koji preuzme Data Manager. Očekivana struktura direktorija:
       HTML_DIR/akti/<publication_id>.html      stranica akta
       HTML_DIR/popisi/*.html                    popis(i) izdanja
       HTML_DIR/sn_registar_v0185.json           {"records":[...]} izvoz Data Managera
       Ovdje se ne koristi kod Data Managera: parsiranje radi sn_identitet_provjera."""

    @classmethod
    def setUpClass(cls):
        cls.reg = json.load(open(Path(HTML_DIR) / "sn_registar_v0185.json", encoding="utf-8"))["records"]
        cls.popisi = [p.read_text(encoding="utf-8", errors="replace") for p in sorted((Path(HTML_DIR) / "popisi").glob("*.html"))]

    def test_struktura_popisa_prepoznata(self):
        for h in self.popisi:
            o = P.opisi_strukturu(h)
            self.assertGreater(o["zapisa"], 0, o)
            self.assertEqual(o["bez_rednog_broja"], 0, o)

    def test_registar_validan(self):
        self.assertEqual([x for x in P.provjeri_registar(self.reg) if x["ozbiljnost"] == "FAIL"], [])

    def test_svaki_zapis_protiv_html(self):
        popis = "\n".join(self.popisi)
        greske = []
        for z in self.reg:
            f = Path(HTML_DIR) / "akti" / f"{z['publication_id']}.html"
            if not f.exists():
                greske.append((z["publication_id"], "nema HTML-a"))
                continue
            greske += [(x["publication_id"], x["kod"]) for x in P.provjeri_akt_html(z, f.read_text(encoding="utf-8", errors="replace"), popis)]
        self.assertEqual(greske, [])


if __name__ == "__main__":
    unittest.main(verbosity=1)

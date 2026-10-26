"""Testovi prilagodnika formata izvora (prilagodi_izvor.py)."""
import unittest
from pathlib import Path
import prilagodi_izvor as P
from citac_tekst import izdvoji_tekst

M = Path(__file__).resolve().parent


class Prilagodnik(unittest.TestCase):
    def test_mijenja_samo_prijelome_redaka(self):
        a = b"<p>\xc8lanak\r\n1.</p><pre>a\nb</pre><p>x\ny</p>"
        b = P.prilagodi(a)
        self.assertEqual(b, b"<p>\xc8lanak 1.</p><pre>a\nb</pre><p>x y</p>")
        P.provjera(a, b)

    def test_nv_nepromijenjen(self):
        src = M / "slijepo/novi_vinodolski/nv_upu_sn_32_2026.html"
        q = M / "slijepo/novi_vinodolski/_test_prilagodjeno.html"
        q.write_bytes(P.prilagodi(src.read_bytes()))
        try:
            a, b = izdvoji_tekst(src, dio=None), izdvoji_tekst(q, dio=None)
            self.assertEqual({k: c["tekst"] for k, c in a["clanci"].items()}, {k: c["tekst"] for k, c in b["clanci"].items()})
        finally:
            q.unlink()

    def test_crikvenica_clanci(self):
        d = izdvoji_tekst(M / "slijepo/crikvenica_centar_1/crikvenica_upu_centar_1.prilagodjeno.html", dio=None)
        self.assertEqual(len(d["clanci"]), 114)


if __name__ == "__main__":
    unittest.main()

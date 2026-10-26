#!/usr/bin/env python3
"""Prilagodnik formata izvora za slijepi test v2.5 (ne dio čitača; zamrznuti kod se ne mijenja).

HTML iz Worda prelama retke izvornog koda usred odlomka (npr. »Članak« ⏎ »1.«). Po pravilima HTML-a prijelom
retka u izvornom kodu je samo razmak; retke određuju blok-oznake (<p>, <br>, <div>, …), koje zamrznuti
citac_tekst.u_tekst već pretvara u prijelome. Prilagodnik zato svaki prijelom retka (CR, LF) izvan <pre> i
<textarea> zamjenjuje razmakom. Ništa drugo se ne mijenja: ni slova, ni brojevi, ni oznake, ni kodiranje.

    python3 prilagodi_izvor.py ULAZ.html IZLAZ.html     # ispisuje SHA-256 ulaza i izlaza
"""
import hashlib, re, sys
from pathlib import Path

VERZIJA = "prilagodi-izvor-1.0"


def prilagodi(raw: bytes) -> bytes:
    dijelovi = re.split(rb"(?is)(<(pre|textarea)\b.*?</\2>)", raw)
    out, i = [], 0
    while i < len(dijelovi):
        d = dijelovi[i]
        if i % 3 == 0:
            out.append(re.sub(rb"\r\n|\r|\n", b" ", d))
            i += 1
        else:
            out.append(d)  # <pre>/<textarea> ostaju doslovno
            i += 2
    return b"".join(out)


def provjera(a: bytes, b: bytes):
    """Jedina razlika smije biti CR/LF → razmak."""
    na = re.sub(rb"\s+", b" ", a)
    nb = re.sub(rb"\s+", b" ", b)
    assert na == nb, "prilagodnik je promijenio nešto osim prijeloma redaka"


if __name__ == "__main__":
    ul, iz = Path(sys.argv[1]), Path(sys.argv[2])
    a = ul.read_bytes(); b = prilagodi(a); provjera(a, b)
    iz.write_bytes(b)
    print(VERZIJA, "ulaz", hashlib.sha256(a).hexdigest(), "izlaz", hashlib.sha256(b).hexdigest())

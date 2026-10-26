#!/usr/bin/env python3
"""EKSPERIMENT v2.6: učitavanje izvora s normalizacijom koja ne mijenja značenje. Zamrznuti citac.py, citac_tekst.py i
prilagodi_izvor.py se ne mijenjaju; ovdje ih se samo poziva.

HTML (uključujući stariji HTML iz Worda):
  prijelom retka u HTML kodu → razmak (prilagodi_izvor), pa zamrznuti citac_tekst.izdvoji_tekst.
PDF:
  zamrznuti citac.izdvoji uz granice odluke neovisne o veličini slova: »ODLUKU / ODLUKA o donošenju …« i završni
  redak »Klasa:« / »KLASA:«. Ostalo (zaglavlja, tablice, oštećeno kodiranje → ABSTAIN) radi zamrznuti kod.

Izvorna datoteka se ne mijenja; vraćaju se SHA-256 izvora i SHA-256 normaliziranog sadržaja.
"""
import hashlib, re, tempfile
from contextlib import contextmanager
from pathlib import Path
import citac
import prilagodi_izvor as PI
import citac_tekst as CT
from citac_tekst import izdvoji_tekst

VERZIJA = "izvor-v2.6"
_frozen_granice = citac.granice_odluke
SUMNJIVI = ("þ", "ÿ", "ý", "Ā", "\x03")  # tipični ostaci pogrešnog preslikavanja fonta u hrvatskim PDF-ovima (č, đ, Č, Đ, razmak)


def granice_odluke_v26(blokovi, naslov):
    """Kao citac.granice_odluke; razlika je samo u veličini slova početka (»odluku« / »odluka«) i završnog »Klasa:«."""
    ciljani = citac._norm_cmp(naslov)
    poc = []
    for i, b in enumerate(blokovi):
        t = citac._norm_cmp(" ".join(b["linije"]))
        if re.fullmatch(r"odluk[ua]", t) and i + 1 < len(blokovi):  # »ODLUKU« sama u bloku, »o donošenju …« u sljedećem
            t = t + " " + citac._norm_cmp(" ".join(blokovi[i + 1]["linije"]))
        if not re.match(r"odluk[ua] o donošenju", t):
            continue
        okolina = t + " " + " ".join(citac._norm_cmp(" ".join(x["linije"])) for x in blokovi[i + 1:i + 3])
        if ciljani in okolina:
            poc.append(i)
    if len(poc) != 1:
        return None, None, None, f"naslov odluke nađen {len(poc)} puta (očekivano 1)"
    kraj = next((j for j in range(poc[0] + 1, len(blokovi)) if re.match(r"klasa\s*:", " ".join(blokovi[j]["linije"]), re.I)), None)
    if kraj is None:
        return None, None, None, "nema završnog podatka »Klasa:« nakon naslova"
    klasa = re.search(r"klasa:\s*([\d/-]+)", " ".join(blokovi[kraj]["linije"]), re.I)
    return poc[0], kraj, klasa.group(1) if klasa else None, None


@contextmanager
def _granice():
    citac.granice_odluke = granice_odluke_v26
    try:
        yield
    finally:
        citac.granice_odluke = _frozen_granice


def naslovi_html(raw):
    """Naslovi članaka u HTML-u: zaseban odlomak odmah iza »Članak N.«, do 150 znakova, bez završne interpunkcije,
    počinje velikim slovom i iza njega slijedi odlomak koji počinje velikim slovom. Vraća {broj: [naslovi]}."""
    t = CT.u_tekst(raw, "x.html")
    L = [re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")]
    L = [l for l in L if l]
    out = {}
    for i, l in enumerate(L[:-2]):
        m = re.match(r"^Članak\s+(\d{1,3})\.\s*$", l)
        if not m:
            continue
        h, n = L[i + 1], L[i + 2]
        if len(h) <= 150 and not re.search(r"[.:;,!?]$", h) and not re.match(r"^[-•(\d]", h) and \
                re.match(r"^[A-ZČĆŽŠĐ]", h) and re.match(r"^[A-ZČĆŽŠĐ]", n):
            out.setdefault(int(m.group(1)), []).append(h)
    return out


def odvoji_naslove(d, raw):
    """Naslov se uklanja s početka teksta članka i zapisuje u »naslov_clanka« (tekst odredbi ostaje doslovan)."""
    N = naslovi_html(raw)
    for c in d.get("clanci", {}).values():
        for h in N.get(c["broj"], []):
            if c["tekst"].startswith(h + " ") and len(c["tekst"]) > len(h) + 1:
                c["naslov_clanka"] = h
                c["tekst"] = c["tekst"][len(h) + 1:]
                break
    return d


def ucitaj(putanja, dio=None, naslov=None, clanci=None):
    p = Path(putanja)
    raw = p.read_bytes()
    if p.suffix.lower() == ".pdf":
        if not naslov:
            raise SystemExit("PDF: potreban je naslov odluke (naziv plana)")
        blokovi = citac.ucitaj_blokove(p)[0]
        tekst = " ".join(" ".join(b["linije"]) for b in blokovi)
        losi = sum(tekst.count(z) for z in SUMNJIVI)
        slova = sum(ch.isalpha() for ch in tekst) or 1
        if losi > 0.001 * slova:
            return {"shema": citac.SHEMA, "izvor": p.name, "sha256": hashlib.sha256(raw).hexdigest(), "status": "ABSTAIN_KODIRANJE",
                    "razlog": f"{losi} znakova pogrešno preslikanog fonta (npr. þ, ÿ, ý, Ā) u tekstnom sloju PDF-a; izvor nije vjeran",
                    "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False}
        with _granice():
            d = citac.izdvoji(p, naslov)
        d["normalizacija"] = {"verzija": VERZIJA, "granice": "neovisno o veličini slova (ODLUKU/ODLUKA, Klasa/KLASA)"}
        return d
    nov = PI.prilagodi(raw)
    PI.provjera(raw, nov)
    with tempfile.TemporaryDirectory() as td:
        q = Path(td) / p.name
        q.write_bytes(nov)
        d = izdvoji_tekst(q, clanci, dio=dio)
    odvoji_naslove(d, nov)
    d["sha256"] = hashlib.sha256(raw).hexdigest()
    d["normalizacija"] = {"verzija": VERZIJA, "prilagodnik": PI.VERZIJA, "sha256_normalizirano": hashlib.sha256(nov).hexdigest(),
                        "odvojeni_naslovi": sum(1 for c in d.get("clanci", {}).values() if c.get("naslov_clanka"))}
    return d

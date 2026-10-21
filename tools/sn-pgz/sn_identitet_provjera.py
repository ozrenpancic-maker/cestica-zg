#!/usr/bin/env python3
"""Neovisna provjera vlastitog broja SN, datuma objave i ciljnog akta (za ČesticaHR v0.18.5).

Ovaj modul NE koristi kod Data Managera. Sadrži vlastite, minimalne parsere:
  * footer akta:     default.asp?Link=odluke&izdanje=I&mjesto=M&odluka=O
  * popis izdanja:   "Službene novine broj N. Godina XXVIII. Petak, 2. listopada 2020."
                     + "Općina PUNAT" + "60. Naslov" + poveznica id=NNN
  * citati SN/NN u tekstu akta
  * pravila razrješavanja ciljnog akta i provjera registra (izvoza v0.18.5)

Strukturu popisa izdanja poznajemo samo iz jednog dohvata (vidi
tests/zlatni/sn-portal-sidro-v1.json); parser je zato tolerantan na oznake (radi nad linearnim
tokom teksta i poveznica) i ima način `opisi_strukturu` za ispis što je stvarno pronađeno.
Parsiranje je ISKLJUČIVO za provjeru; ništa se ne zaključuje bez dokaza (vraća None/UNKNOWN).
"""
from __future__ import annotations
import html as _html
import re
from html.parser import HTMLParser

MJESECI = {"siječnja": 1, "veljače": 2, "ožujka": 3, "travnja": 4, "svibnja": 5, "lipnja": 6,
           "srpnja": 7, "kolovoza": 8, "rujna": 9, "listopada": 10, "studenoga": 11, "studenog": 11,
           "prosinca": 12}
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
PRVA_GODINA_TOMA = 1993  # opaženo: 2020. = Godina XXVIII (1993 + 28 - 1)

FOOTER_RE = re.compile(r"Link=odluke&izdanje=(\d+)&mjesto=(\d+)&odluka=(\d+)")
ZAGLAVLJE_RE = re.compile(
    r"Službene\s+novine\s+broj\s+(\d{1,3})\.?\s+Godina\s+([IVXLC]+)\.?\s+"
    r"(?:\w+,?\s+)?(\d{1,2})\.\s*(\w+)\s+(\d{4})\.?", re.I)
MJESTO_RE = re.compile(r"^(Općina|Grad|Županija)\s+(.+)$", re.I)
REDNI_RE = re.compile(r"^(\d{1,3})\.\s*(.*)$", re.S)


def rimski(s: str) -> int | None:
    s = s.upper()
    if not s or any(ch not in ROMAN for ch in s):
        return None
    tot = 0
    for i, ch in enumerate(s):
        v = ROMAN[ch]
        tot += -v if i + 1 < len(s) and ROMAN[s[i + 1]] > v else v
    return tot


# ---------------------------------------------------------------- HTML -> tokeni
class _Lin(HTMLParser):
    """Linearizira HTML u tokene ('T', tekst) i ('A', href, tekst_poveznice)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tok, self._buf, self._a = [], [], None
        self._skip = 0

    def _flush(self):
        t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
        self._buf = []
        if t:
            self.tok.append(("T", t))

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "a":
            self._flush()
            self._a = [dict(attrs).get("href", ""), []]
        elif tag in ("br", "p", "div", "tr", "td", "th", "li", "h1", "h2", "h3", "h4", "table"):
            if self._a is None:
                self._flush()

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        if tag == "a" and self._a is not None:
            txt = re.sub(r"\s+", " ", "".join(self._a[1])).strip()
            self.tok.append(("A", _html.unescape(self._a[0]), txt))
            self._a = None
        elif tag in ("p", "div", "tr", "td", "th", "li", "h1", "h2", "h3", "h4", "table"):
            if self._a is None:
                self._flush()

    def handle_data(self, d):
        if self._skip:
            return
        (self._a[1] if self._a is not None else self._buf).append(d)

    def close(self):
        super().close()
        self._flush()


def tokeni(html_tekst: str):
    p = _Lin()
    p.feed(html_tekst)
    p.close()
    return p.tok


# ---------------------------------------------------------------- footer akta
def footer_trojka(html_ili_tekst: str):
    """(izdanje_id:int, mjesto_id:str, redni_broj:int) iz footera stranice akta; None ako ga nema.
    Ako ih ima više različitih, vraća None (dvosmisleno)."""
    t = _html.unescape(html_ili_tekst)
    sv = set(FOOTER_RE.findall(t))
    if len(sv) != 1:
        return None
    i, m, o = next(iter(sv))
    return int(i), m, int(o)


# ---------------------------------------------------------------- popis izdanja
def izvuci_popis(html_tekst: str):
    """Iz HTML-a popisa izdanja vraća zapise:
    {publication_id, izdanje_broj, godina_toma, godina, datum, mjesto_naziv, redni_broj, naslov, pdf}"""
    out, izd, mj, red = [], None, None, None
    for t in tokeni(html_tekst):
        if t[0] == "T":
            z = ZAGLAVLJE_RE.search(t[1])
            if z:
                dan, mje, god = int(z.group(3)), MJESECI.get(z.group(4).lower()), int(z.group(5))
                izd = {"broj": int(z.group(1)), "rimski": z.group(2), "godina": god,
                       "datum": f"{god:04d}-{mje:02d}-{dan:02d}" if mje else None}
                mj, red = None, None
                continue
            m = MJESTO_RE.match(t[1])
            if m and len(t[1]) < 60:
                mj = t[1].strip()
                red = None
                continue
            r = REDNI_RE.match(t[1])
            if r:
                red = (int(r.group(1)), r.group(2).strip())
            continue
        _, href, txt = t
        m = re.search(r"Link=odluke&id=(\d+)", _html.unescape(href))
        if not m or izd is None:
            continue
        pdf = bool(re.search(r"pdf", txt, re.I))
        ordn, naslov = red if red else (None, "")
        r2 = REDNI_RE.match(txt)
        if r2 and not pdf:
            ordn, naslov = int(r2.group(1)), r2.group(2).strip()
        elif txt and not pdf:
            naslov = txt
        out.append({"publication_id": m.group(1), "izdanje_broj": izd["broj"],
                    "godina_toma": izd["rimski"], "godina": izd["godina"], "datum": izd["datum"],
                    "mjesto_naziv": mj, "redni_broj": None if pdf else ordn,
                    "naslov": None if pdf else naslov, "pdf": pdf})
        if not pdf:
            red = None
    return out


def opisi_strukturu(html_tekst: str) -> dict:
    """Za prvi stvarni HTML: što je parser pronašao (da se vidi odgovara li pretpostavka strukture)."""
    tok = tokeni(html_tekst)
    zap = izvuci_popis(html_tekst)
    return {"tokena": len(tok), "zaglavlja_izdanja": sum(1 for t in tok if t[0] == "T" and ZAGLAVLJE_RE.search(t[1])),
            "poveznice_id": sum(1 for t in tok if t[0] == "A" and "Link=odluke&id=" in t[1]),
            "zapisa": len(zap), "bez_rednog_broja": sum(1 for z in zap if not z["pdf"] and z["redni_broj"] is None),
            "footer_trojka": footer_trojka(html_tekst)}


# ---------------------------------------------------------------- citati
_GAZ = re.compile(
    r"(?P<g>Narodne\s+novine|\bNN\b|Službene\s+novine(?:\s+Primorsko[\s-]*goranske\s+županije|\s+PGŽ)?|\bSN\s*PGŽ|\bSN\b)"
    r"[«»\"“”'\s,.]*(?:PGŽ[«»\"“”'\s,.]*)?(?:br\.?|broj)?\s*(?P<lanac>\d{1,3}\s*/\s*\d{2,4}(?:\s*[-–]\s*(?:ispravak|ispr\.?)[^,;()0-9]{0,40})?(?:\s*(?:,|;|\bi\b|\bte\b)\s*\d{1,3}\s*/\s*\d{2,4}(?:\s*[-–]\s*(?:ispravak|ispr\.?)[^,;()0-9]{0,40})?)*)",
    re.I)
_BR = re.compile(r"(\d{1,3})\s*/\s*(\d{2,4})(\s*[-–]\s*(?:ispravak|ispr\.?)[^,;]*)?", re.I)


def godina4(g: str) -> int:
    """Pomak stoljeća: 2-znamenkasto >= 93 -> 19xx (PGŽ SN počinje 1993.), inače 20xx."""
    n = int(g)
    if len(g) >= 4:
        return n
    return 1900 + n if n >= 93 else 2000 + n


def citati(tekst: str):
    """Citati s atribucijom glasila:
    gazeta: SN_PGZ | NN | SN_STARO (prije 1993., drugo glasilo) | SN_NEJASNO"""
    out = []
    for m in _GAZ.finditer(tekst):
        g = m.group("g").lower()
        if g.startswith("narodne") or g == "nn":
            gaz = "NN"
        elif "pgž" in g.replace(" ", "") or "primorsko" in g:
            gaz = "SN_PGZ"
        else:
            gaz = "SN_NEJASNO"
        okolina = tekst[max(0, m.start() - 60): m.end() + 60].lower()
        for b in _BR.finditer(m.group("lanac")):
            god = godina4(b.group(2))
            gz = gaz
            if gz.startswith("SN") and god < 1993:
                gz = "SN_STARO"
            elif gz == "SN_NEJASNO" and ("primorsko-goransk" in okolina or "pgž" in okolina):
                gz = "SN_PGZ"
            out.append({"gazeta": gz, "broj": int(b.group(1)), "godina": god,
                        "oznaka": f"{int(b.group(1))}/{god % 100:02d}", "ispravak": bool(b.group(3)),
                        "sirovo": b.group(0).strip()})
    return out


# ---------------------------------------------------------------- razrješavanje cilja
def razrijesi_cilj(citat: dict, registar: list[dict], mjesto_id: str | None = None,
                   naslov_dio: str | None = None, redni_broj: int | None = None) -> dict:
    """Pravila (jedini dopušteni put do ciljnog akta):
    1. gazeta mora biti SN_PGZ  (NN, SN_STARO, SN_NEJASNO -> ne razrješava se)
    2. (broj, godina) -> izdanje iz registra; nema ga -> NOT_IN_REGISTRY (ne nagađa se)
    3. filtar po mjestu (obavezan za razrješavanje)
    4. ostaje točno 1 akt -> RESOLVED; više -> AMBIGUOUS (ili sužavanje naslovom/rednim brojem)
    Ispravak (ispravak odluke) se NE razrješava na izvorni akt: vraća CORRECTION_NOTICE."""
    if citat["gazeta"] != "SN_PGZ":
        return {"status": "WRONG_GAZETTE", "kandidati": []}
    izd = [r for r in registar if r["sn_broj"] == citat["broj"] and r["sn_godina"] == citat["godina"]]
    if not izd:
        return {"status": "NOT_IN_REGISTRY", "kandidati": []}
    if citat.get("ispravak"):
        return {"status": "CORRECTION_NOTICE", "kandidati": [r["publication_id"] for r in izd]}
    if mjesto_id is None:
        return {"status": "AMBIGUOUS_NO_MUNICIPALITY", "kandidati": [r["publication_id"] for r in izd]}
    k = [r for r in izd if r["mjesto_id"] == mjesto_id]
    if redni_broj is not None:
        k = [r for r in k if r["redni_broj_u_izdanju"] == redni_broj]
    if naslov_dio and len(k) > 1:
        k = [r for r in k if naslov_dio.lower() in (r.get("naziv_akta") or "").lower()]
    ids = [r["publication_id"] for r in k]
    if len(ids) == 1:
        return {"status": "RESOLVED", "kandidati": ids}
    return {"status": "NOT_IN_REGISTRY" if not ids else "AMBIGUOUS", "kandidati": ids}


# ---------------------------------------------------------------- provjera registra
OBAVEZNO = ("publication_id", "izdanje_id", "mjesto_id", "redni_broj_u_izdanju", "sn_broj", "sn_godina",
            "sn_oznaka", "datum_izdanja", "naziv_akta", "izvor_zaglavlja", "izvor_html_sha256")
DOZVOLJEN_IZVOR = {"PORTAL_ISSUE_LISTING", "PORTAL_ACT_PAGE_HEADER"}


def provjeri_registar(zapisi: list[dict]) -> list[dict]:
    """Vraća popis povreda {kod, ozbiljnost: FAIL|WARN, publication_id, poruka}."""
    v = []

    def f(kod, o, pid, msg):
        v.append({"kod": kod, "ozbiljnost": o, "publication_id": pid, "poruka": msg})

    seen_pid, seen_tr = {}, {}
    po_izd, po_oznaka = {}, {}
    for z in zapisi:
        pid = z.get("publication_id")
        for k in OBAVEZNO:
            if z.get(k) in (None, ""):
                f("R1_NEDOSTAJE_POLJE", "FAIL", pid, f"nedostaje {k}")
        if z.get("izvor_zaglavlja") not in DOZVOLJEN_IZVOR:
            f("R4_IZVOR_NIJE_PORTAL", "FAIL", pid, f"izvor={z.get('izvor_zaglavlja')!r}: vlastiti broj SN smije doći samo s portala, ne iz citata")
        try:
            exp = f"{int(z['sn_broj'])}/{int(z['sn_godina']) % 100:02d}"
            if z.get("sn_oznaka") != exp:
                f("R2_OZNAKA_NEKONZISTENTNA", "FAIL", pid, f"sn_oznaka {z.get('sn_oznaka')} != {exp}")
            if str(z.get("datum_izdanja", ""))[:4] != str(z["sn_godina"]):
                f("R3_DATUM_GODINA", "FAIL", pid, f"datum {z.get('datum_izdanja')} ne odgovara godini {z['sn_godina']}")
            if z.get("godina_toma_rimski"):
                r = rimski(z["godina_toma_rimski"])
                if r is None or PRVA_GODINA_TOMA + r - 1 != int(z["sn_godina"]):
                    f("R3B_RIMSKA_GODINA", "FAIL", pid, f"godina toma {z['godina_toma_rimski']} ne odgovara {z['sn_godina']}")
        except (KeyError, ValueError, TypeError):
            pass
        if pid in seen_pid:
            f("R5_DUPLIKAT_ID", "FAIL", pid, "publication_id se ponavlja")
        seen_pid[pid] = z
        tr = (z.get("izdanje_id"), z.get("mjesto_id"), z.get("redni_broj_u_izdanju"))
        if tr in seen_tr and seen_tr[tr] != pid:
            f("R5_DUPLIKAT_TROJKE", "FAIL", pid, f"trojka {tr} već ima {seen_tr[tr]}")
        seen_tr[tr] = pid
        key = (z.get("sn_broj"), z.get("sn_godina"), z.get("datum_izdanja"))
        po_izd.setdefault(z.get("izdanje_id"), set()).add(key)
        po_oznaka.setdefault((z.get("sn_broj"), z.get("sn_godina")), set()).add(z.get("izdanje_id"))
    for izd, ks in po_izd.items():
        if len(ks) > 1:
            f("R6_IZDANJE_RAZLICITE_OZNAKE", "FAIL", None, f"izdanje {izd} ima različite (broj, godina, datum): {sorted(map(str, ks))}")
    for oz, ids in po_oznaka.items():
        if len(ids) > 1:
            f("R6_OZNAKA_VISE_IZDANJA", "FAIL", None, f"SN {oz[0]}/{oz[1]} vezan uz više izdanja {sorted(ids)}")
    # R7 monotonost: izdanje_id raste s vremenom (opaženo; iznimke samo upozorenje)
    ser = sorted({(z["izdanje_id"], z["datum_izdanja"]) for z in zapisi if z.get("izdanje_id") is not None and z.get("datum_izdanja")})
    for (a, da), (b, db) in zip(ser, ser[1:]):
        if db < da:
            f("R7_NEMONOTONO", "WARN", None, f"izdanje {a} ({da}) prije izdanja {b} ({db})")
    return v


def provjeri_akt_html(zapis: dict, akt_html: str, popis_html: str | None = None) -> list[dict]:
    """Križna provjera jednog zapisa protiv spremljenog HTML-a (neovisni parseri iz ovog modula)."""
    v = []
    pid = zapis.get("publication_id")
    tr = footer_trojka(akt_html)
    if tr is None:
        v.append({"kod": "H1_NEMA_FOOTERA", "ozbiljnost": "FAIL", "publication_id": pid, "poruka": "footer s izdanje/mjesto/odluka nije jednoznačan"})
    elif tr != (zapis.get("izdanje_id"), zapis.get("mjesto_id"), zapis.get("redni_broj_u_izdanju")):
        v.append({"kod": "H2_FOOTER_RAZLIKA", "ozbiljnost": "FAIL", "publication_id": pid, "poruka": f"footer {tr} != zapis"})
    if popis_html is not None:
        nad = [e for e in izvuci_popis(popis_html) if e["publication_id"] == str(pid) and not e["pdf"]]
        if len(nad) != 1:
            v.append({"kod": "H3_ID_U_POPISU", "ozbiljnost": "FAIL", "publication_id": pid, "poruka": f"id nađen {len(nad)} puta u popisu"})
        else:
            e = nad[0]
            if (e["izdanje_broj"], e["godina"], e["datum"]) != (zapis.get("sn_broj"), zapis.get("sn_godina"), zapis.get("datum_izdanja")):
                v.append({"kod": "H4_POPIS_RAZLIKA", "ozbiljnost": "FAIL", "publication_id": pid, "poruka": f"popis {e['izdanje_broj']}/{e['godina']} {e['datum']} != zapis"})
            if e["redni_broj"] != zapis.get("redni_broj_u_izdanju"):
                v.append({"kod": "H5_REDNI_BROJ", "ozbiljnost": "FAIL", "publication_id": pid, "poruka": f"redni broj u popisu {e['redni_broj']} != footer/zapis"})
    return v

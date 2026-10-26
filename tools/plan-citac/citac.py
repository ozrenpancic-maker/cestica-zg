#!/usr/bin/env python3
"""EKSPERIMENT: čitač odluke o prostornom planu iz PDF-a Službenih novina PGŽ (dvostupačni prijelom).

Samo čita lokalni PDF; ne dohvaća mrežu, ne mijenja pravila aplikacije i ništa ne potvrđuje pravno.
Izlaz: članci 1..N s izvornim (sirovim) i normaliziranim tekstom, stranicom, stupcem i okvirom,
naslovi poglavlja odvojeno, zaglavlja stranica uklonjena, tablice označene kao nepouzdane.

Korištenje:
    python3 citac.py ODLUKA.pdf --naslov "UPU 2 - Kornić" [--clanaka 108] [-o dokazi.json]
Ovisnost: PyMuPDF (pip install pymupdf).
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

SHEMA = "plan-citac/0.1"

# ---------------------------------------------------------------- znakovi
# Font u SN PGŽ dijakritike crta kao zaseban znak (ˇ ´ ¯) iznad slova; spajaju se prema položaju glifa.
DIJAKRITIK = {"ˇ": {"c": "č", "C": "Č", "s": "š", "S": "Š", "z": "ž", "Z": "Ž"},
              "´": {"c": "ć", "C": "Ć"},
              "¯": {"d": "đ", "D": "Đ"}}
RAZMAK_PT = 1.0  # razmak između glifova veći od ovoga znači granicu riječi


GORNJI = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
DONJI = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def _spoji_liniju(line):
    """Tekst jednog retka iz glifova: dijakritik se spaja s glifom ispod, razmaci se određuju po položaju,
    a sitne znamenke ispod ili iznad osnovne crte postaju indeks ili eksponent (»M1₁«, »m²«)."""
    out, x_kraj, problemi = [], None, 0
    vel = max((s["size"] for s in line["spans"] if any(not c["c"].isspace() for c in s["chars"])), default=0)
    osnova = next((c["origin"][1] for s in line["spans"] if s["size"] == vel for c in s["chars"]), None)
    for span in line["spans"]:
        for ch in span["chars"]:
            c, (x0, _, x1, _) = ch["c"], ch["bbox"]
            if c.isdigit() and osnova is not None and span["size"] < 0.8 * vel:
                c = c.translate(DONJI if ch["origin"][1] > osnova + 0.5 else GORNJI)
            if c in DIJAKRITIK:
                # znak koji pripada prethodnom slovu (glif dijakritika leži unutar njegova okvira)
                j = len(out) - 1
                while j >= 0 and out[j] == " ":
                    j -= 1
                if j >= 0 and out[j] in DIJAKRITIK[c]:
                    out[j] = DIJAKRITIK[c][out[j]]
                    del out[j + 1:]
                elif j >= 0 and c == "¯" and out[j] in ("đ", "Đ"):
                    pass  # dvostruki znak (»ured¯¯enja«)
                else:
                    out.append(c); problemi += 1
                continue
            if c.isspace():
                continue
            if x_kraj is not None and x0 - x_kraj > RAZMAK_PT and out and out[-1] != " " and c not in "⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉":
                out.append(" ")
            out.append(c)
            x_kraj = x1 if x_kraj is None else max(x_kraj, x1)
    return "".join(out).strip(), problemi


def _sirovi(block):
    return "\n".join("".join(c["c"] for s in l["spans"] for c in s["chars"]) for l in block["lines"])


# ---------------------------------------------------------------- blokovi stranice
def ucitaj_blokove(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    blokovi, zaglavlja, tablice = [], [], []
    for pi, page in enumerate(doc):
        sredina = page.rect.width / 2
        tab = _tablicna_podrucja(page)
        tablice += [{"stranica": pi + 1, "okvir": [round(v, 1) for v in t]} for t in tab]
        for b in page.get_text("rawdict")["blocks"]:
            if b["type"] != 0:
                continue
            linije = [_spoji_liniju(l) for l in b["lines"]]
            linije = [(t, p) for t, p in linije if t]
            if not linije:
                continue
            x0, y0, x1, y1 = b["bbox"]
            sir = _sirovi(b)
            rec = {"stranica": pi + 1, "stupac": "L" if (x0 + x1) / 2 < sredina else "D",
                   "okvir": [round(v, 1) for v in b["bbox"]], "linije": [t for t, _ in linije],
                   "sirovo": sir, "problemi_znakova": sum(p for _, p in linije),
                   "velicina": max(s["size"] for l in b["lines"] for s in l["spans"]),
                   "tablica": next((i for i, t in enumerate(tab) if t[0] - 2 <= (x0 + x1) / 2 <= t[2] + 2 and t[1] - 2 <= (y0 + y1) / 2 <= t[3] + 2), None)}
            if rec["tablica"] is not None:
                rec["tablica"] = len(tablice) - len(tab) + rec["tablica"]
            if _je_zaglavlje(rec, page.rect.width):
                zaglavlja.append({"stranica": pi + 1, "okvir": rec["okvir"], "tekst": " ".join(rec["linije"])})
                continue
            blokovi.append(rec)
    doc.close()
    # redoslijed čitanja: stranica, lijevi pa desni stupac, odozgo prema dolje
    blokovi.sort(key=lambda r: (r["stranica"], 0 if r["stupac"] == "L" else 1, r["okvir"][1], r["okvir"][0]))
    return blokovi, zaglavlja, tablice


def _je_zaglavlje(rec, sirina):
    t = " ".join(rec["linije"])
    return rec["okvir"][3] < 105 and rec["okvir"][2] - rec["okvir"][0] > 0.6 * sirina and bool(re.search(r"Stranica\s+\d+\s+—\s+broj\s+\d+", t))


def _tablicna_podrucja(page):
    """Okviri tablica: skupine vektorskih crta (bez linija zaglavlja i razdjelnika odluka)."""
    W = page.rect.width
    crte = [d["rect"] for d in page.get_drawings()
            if not (d["rect"].y1 < 105 and d["rect"].width > 0.6 * W)]
    skupine = []
    for r in crte:
        r = [r.x0, r.y0, r.x1, r.y1]
        for s in skupine:
            if r[0] <= s[2] + 3 and r[2] >= s[0] - 3 and r[1] <= s[3] + 3 and r[3] >= s[1] - 3:
                s[0], s[1], s[2], s[3] = min(s[0], r[0]), min(s[1], r[1]), max(s[2], r[2]), max(s[3], r[3])
                s[4] += 1
                break
        else:
            skupine.append(r + [1])
    return [s[:4] for s in skupine if s[4] >= 8 and s[3] - s[1] > 30]


# ---------------------------------------------------------------- rastavljene riječi
SLOVO = "a-zA-ZčćđšžČĆĐŠŽ"


def _spoji(tekst, ln, slozenice, odluke):
    """Spaja dva dijela teksta (retke, ili blokove preko stupca/stranice). Rastav »rije- č« spaja se, osim ako se
    ista složenica s crticom (»Primorsko-goranske«) pojavljuje negdje u dokumentu unutar retka."""
    if not tekst:
        return ln
    m = re.search(rf"([{SLOVO}]+)-$", tekst[-80:])
    n = re.match(rf"([{SLOVO}]+)", ln)
    if m and n and (n.group(1)[0].islower() or (m.group(1).isupper() and n.group(1).isupper())):
        par = (m.group(1) + "-" + n.group(1)).lower()
        if par in slozenice:
            odluke.append({"rijec": m.group(1) + "-" + n.group(1), "crtica": "zadrzana"})
            return tekst + ln
        odluke.append({"rijec": m.group(1) + n.group(1), "crtica": "uklonjena"})
        return tekst[:-1] + ln
    return tekst + " " + ln


def spoji_linije(linije, slozenice):
    tekst, odluke = "", []
    for ln in linije:
        tekst = _spoji(tekst, ln, slozenice, odluke)
    return tekst, odluke


def _slozenice(blokovi):
    s = set()
    for b in blokovi:
        for ln in b["linije"]:
            for m in re.finditer(rf"(?<![{SLOVO}])([{SLOVO}]+-[{SLOVO}]+)(?![{SLOVO}-])", ln):
                s.add(m.group(1).lower())
    return s


# ---------------------------------------------------------------- granice odluke
def _norm_cmp(s):
    return re.sub(r"\s+", " ", s).strip().lower()


def granice_odluke(blokovi, naslov):
    """Početak: podebljani naslov »ODLUKU o donošenju …« iza kojega (u istom ili sljedećem bloku) stoji naziv plana.
    Kraj: prvi blok »Klasa:« nakon početka (potpis odluke). Vraća (i_poc, i_kraj, klasa) ili razlog odbijanja."""
    ciljani = _norm_cmp(naslov)
    poc = []
    for i, b in enumerate(blokovi):
        t = _norm_cmp(" ".join(b["linije"]))
        if not t.startswith("odluku o donošenju"):
            continue
        okolina = t + " " + " ".join(_norm_cmp(" ".join(x["linije"])) for x in blokovi[i + 1:i + 3])
        if ciljani in okolina:
            poc.append(i)
    if len(poc) != 1:
        return None, None, None, f"naslov odluke nađen {len(poc)} puta (očekivano 1)"
    kraj = next((j for j in range(poc[0] + 1, len(blokovi)) if " ".join(blokovi[j]["linije"]).startswith("Klasa:")), None)
    if kraj is None:
        return None, None, None, "nema završnog podatka »Klasa:« nakon naslova"
    klasa = re.search(r"Klasa:\s*([\d/-]+)", " ".join(blokovi[kraj]["linije"]))
    return poc[0], kraj, klasa.group(1) if klasa else None, None


# ---------------------------------------------------------------- članci i naslovi
CLANAK = re.compile(r"^Članak\s+(\d{1,3})\.\s*")
NASLOV = re.compile(r"^(?:[IVX]+\.|\d+(?:\.\d+)*\.)\s+\S")


def izdvoji(pdf, naslov, ocekivano_clanaka=None):
    pdf = Path(pdf)
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    blokovi, zaglavlja, tablice = ucitaj_blokove(pdf)
    a, z, klasa, razlog = granice_odluke(blokovi, naslov)
    osnovno = {"shema": SHEMA, "izvor": pdf.name, "sha256": sha, "naslov": naslov,
               "automatska_potvrda": 0, "pravno_potvrdeno": False}
    if razlog:
        return {**osnovno, "status": "ABSTAIN_GRANICA_ODLUKE", "razlog": razlog, "clanci": {}}
    slozenice = _slozenice(blokovi)
    niz = blokovi[a:z]
    # naslovi poglavlja: numerirani blok iza kojega (preko drugih naslova) slijedi »Članak N.«
    je_cl = [bool(CLANAK.match(" ".join(b["linije"]))) for b in niz]
    je_nas = [False] * len(niz)
    def _nastavak(k):  # kratak redak bez interpunkcije na kraju: nastavak naslova u zasebnom bloku
        ln = niz[k]["linije"]
        return not je_cl[k] and len(ln) == 1 and not re.search(r"[.,;:)]$", ln[0]) and not NASLOV.match(ln[0]) and not ln[0].startswith("-")
    for i in range(len(niz) - 1, -1, -1):
        if je_cl[i] or not NASLOV.match(" ".join(niz[i]["linije"])):
            continue
        j, nast = i + 1, []
        while j < len(niz) and not je_nas[j] and _nastavak(j):
            nast.append(j); j += 1
        while j < len(niz) and je_nas[j]:
            j += 1
        if j < len(niz) and je_cl[j]:
            je_nas[i] = True
            for k in nast:
                je_nas[k] = True
    clanci, poglavlja, problemi, redoslijed = {}, [], [], []
    trenutni, poglavlje = None, None
    for i, b in enumerate(niz):
        t = " ".join(b["linije"])
        izv = {"stranica": b["stranica"], "stupac": b["stupac"], "okvir": b["okvir"]}
        if je_nas[i]:
            if poglavlja and poglavlja[-1]["_do"] == i - 1:
                poglavlja[-1]["tekst"] = _spoji(poglavlja[-1]["tekst"], spoji_linije(b["linije"], slozenice)[0], slozenice, []); poglavlja[-1]["_do"] = i
            else:
                poglavlja.append({"tekst": spoji_linije(b["linije"], slozenice)[0], "izvor": izv, "_do": i, "prije_clanka": None})
            continue
        m = CLANAK.match(t)
        if m:
            n = int(m.group(1)); redoslijed.append(n)
            if str(n) in clanci:
                problemi.append({"vrsta": "DVOSTRUKI_CLANAK", "clanak": n}); trenutni = None; continue
            pog = [p for p in poglavlja if p["prije_clanka"] is None]
            for p in pog:
                p["prije_clanka"] = n
            trenutni = clanci[str(n)] = {"broj": n, "poglavlje": " / ".join(p["tekst"] for p in pog) or None,
                                         "izvor": izv, "blokovi": [], "tablice": []}
        if trenutni is None:
            continue
        if b["tablica"] is not None:
            tid = b["tablica"]
            if tid not in trenutni["tablice"]:
                trenutni["tablice"].append(tid)
                trenutni["blokovi"].append({"tablica": tid, **izv})
            tablice[tid].setdefault("clanak", trenutni["broj"])
            tablice[tid].setdefault("blokovi", []).append({"okvir": b["okvir"], "sirovo": b["sirovo"], "tekst": t})
            continue
        tx, odl = spoji_linije(b["linije"], slozenice)
        slova = re.sub(r"[^A-Za-zČĆĐŠŽčćđšž]", "", tx)
        if NASLOV.match(tx) and len(b["linije"]) <= 2 and slova and sum(ch.isupper() for ch in slova) / len(slova) > 0.8:
            # naslov poglavlja unutar članka (izvor nema zaseban članak za to poglavlje): ostaje u tekstu, bilježi se
            trenutni.setdefault("unutarnji_naslovi", []).append({"tekst": tx, **izv})
        trenutni["blokovi"].append({"tekst": tx, "sirovo": b["sirovo"], "crtice": odl, "problemi_znakova": b["problemi_znakova"], **izv})
    for c in clanci.values():
        tekst, odl = "", []
        for bl in c["blokovi"]:
            if "tablica" in bl:
                T = tablice[bl["tablica"]]
                tekst = (tekst + " " if tekst else "") + f"[TABLICA – nije pouzdano rekonstruirana, vidi str. {T['stranica']}]"
            else:
                tekst = _spoji(tekst, bl["tekst"], slozenice, odl)
        c["crtice_izmedju_blokova"] = odl
        c["tekst"] = CLANAK.sub("", tekst, count=1).strip()
        c["sirovo"] = "\n".join(bl.get("sirovo", "") for bl in c["blokovi"])
        c["status_tablica"] = "TABLICA_NEPOUZDANA" if c["tablice"] else None
    for p in poglavlja:
        p.pop("_do", None)
    for T in tablice:
        T["status"] = "TABLICA_NEPOUZDANA"
        T["napomena"] = "Raspored ćelija nije rekonstruiran; vrijednosti i jedinice ne smiju se povezivati automatski."
    tablice = [T for T in tablice if "clanak" in T]
    N = ocekivano_clanaka or (max(redoslijed) if redoslijed else 0)
    if redoslijed != list(range(1, N + 1)):
        nedostaju = sorted(set(range(1, N + 1)) - set(redoslijed))
        problemi.append({"vrsta": "REDOSLIJED_CLANAKA", "nedostaju": nedostaju, "visak": sorted(set(redoslijed) - set(range(1, N + 1)))})
    zn = sum(bl.get("problemi_znakova", 0) for c in clanci.values() for bl in c["blokovi"])
    if zn:
        problemi.append({"vrsta": "NESPOJENI_DIJAKRITICI", "broj": zn})
    return {**osnovno, "status": "IZDVOJENO_NIJE_PRAVNA_PROVJERA" if not problemi else "IZDVOJENO_UZ_PREGLED",
            "granice": {"pocetak": {"stranica": niz[0]["stranica"], "tekst": " ".join(niz[0]["linije"])[:120]},
                        "kraj": {"stranica": blokovi[z]["stranica"], "klasa": klasa}},
            "broj_clanaka": len(clanci), "problemi": problemi, "zaglavlja_uklonjena": len(zaglavlja),
            "poglavlja": poglavlja, "tablice": tablice, "clanci": clanci}


# ---------------------------------------------------------------- brojevi
REF_RIJECI = r"(?:članak|članka|članku|člankom|člancima|članaka|čl|stavak|stavka|stavku|stavkom|stavcima|stavaka|st|točka|točke|točki|točkom|točkama|točaka|alineja|alineje|alineji|alinejama|podstavak|podstavka|podstavku)"
JEDINICE = [("m²", r"m\s*(?:²|2)(?![\d,.]*\d)"), ("m³", r"m\s*(?:³|3)(?![\d,.]*\d)"), ("%", r"%"),
            ("°", rf"(?:°|˚|o(?![{SLOVO}]))"),
            ("m", rf"(?:m(?![{SLOVO}²³\d])|metara\b|metra\b|metar\b)"), ("mm", r"mm\b"), ("cm", r"cm\b"), ("km", r"km\b"),
            ("ha", r"ha\b"), ("dB", r"dB\b"), ("l", r"l(?![{SLOVO}])".replace("{SLOVO}", SLOVO)), ("ES", r"ES\b")]
VRIJEDNOST_UZ = r"(?:iznosi|najviše|najmanje|do|od|je|i|ili|svaka|svakih|ukupno|oko|min\.?|max\.?)"


def normaliziraj_jedinice(t):
    """»500 m 2« (eksponent u zasebnom retku glifova) → »500 m²«."""
    return re.sub(r"(\d)\s*m\s+([23])(?!\d|,\d)", lambda m: m.group(1) + " m" + ("²" if m.group(2) == "2" else "³"), t)


def brojevi(tekst):
    """Brojčane vrijednosti u tekstu. Ne vraća: oznake stavaka »(1)«, alineja »a)«, pozive na članke/stavke/točke,
    numeraciju poglavlja ni eksponent jedinice. Broj iza kojega slijedi zarez ili točka (kraj alineje) se prepoznaje,
    ali »1,0« se ne nalazi u »1,5«."""
    t = normaliziraj_jedinice(tekst)
    out = []
    for m in re.finditer(r"(?<![\d.,])\d+(?:,\d+)?(?![\d]|[.,]\d)", t):
        s, e, lit = m.start(), m.end(), m.group()
        prije, iza = t[max(0, s - 16):s], t[e:e + 14]
        if prije and re.match(rf"[{SLOVO}]", prije[-1]) and not (prije[-1] in "x×" and re.search(r"\d\s*[x×]$", prije)):
            continue  # broj uz slovo (m2, M11, broj32) nije vrijednost; iznimka: dimenzija »2,5x5,0«
        if re.search(r"\d\s*:\s*$", prije):
            continue  # mjerilo »1:5000«
        if re.search(r"\(\s*$", prije) and re.match(r"\s*\)", iza):
            continue  # oznaka stavka (1)
        if re.match(r"\s*/\s*\d", iza) or re.search(r"\d\s*/\s*$", prije) or re.match(r"[A-ZČĆĐŠŽ]", iza) or re.match(r":\s*\d", iza):
            continue  # oznaka: k.č. 88/4, broj glasila 7/07, prikaz 2A, mjerilo 1:5.000
        if re.search(r"\b(?:br|broj)\.?\s*$", prije, re.I):
            continue  # »prikazu br. 4«, »broj 19«
        if "," not in lit and re.match(r"\.\s+[A-ZČĆĐŠŽ][a-zčćđšž]", iza) and not re.search(rf"\b{VRIJEDNOST_UZ}\s*$", prije):
            continue  # nabrajanje »1. Korištenje i namjena«
        if "," not in lit and 1900 <= int(lit) <= 2099 and re.match(r"\.", iza):
            continue  # godina »2010.«
        if re.search(r"\b[A-ZČĆĐŠŽ]{1,3}\s*$", prije) and not re.search(r"\b(?:DN)\s*$", prije):
            continue  # oznaka ceste ili sustava »L 58091«, »SU 6«
        if re.search(rf"\b{REF_RIJECI}\.?\s*$", prije, re.I) or re.search(rf"\b{REF_RIJECI}\.?\s*(?:\d+\.?\s*(?:i|ili|,|–|-|do)\s*)+$", t[max(0, s - 60):s], re.I):
            continue  # poziv na članak, stavak, točku
        if re.match(r"\.\s*(?:\d+\.)*\s*$", iza[:1]) and re.search(r"(?:^|\s)$", prije) and re.match(r"\.\d", iza):
            continue  # numeracija 4.1.1.
        if re.match(r"\.(?:\s|$)", iza) and re.match(rf"\.\s+(?:{REF_RIJECI}|stavka|stavku)\b", iza, re.I):
            continue  # »6. stavka«
        jed = None
        for naziv, rx in JEDINICE:
            if re.match(r"\s*" + rx, iza):
                jed = naziv; break
        dm = re.match(r"\s*[x×]\s*\d+(?:,\d+)?\s*(m)(?![{SLOVO}])".replace("{SLOVO}", SLOVO), iza)
        if jed is None and dm:
            jed = "m"  # dimenzija »2,5x5,0 m«
        rm = re.match(r"\s*[–-]\s*\d+(?:,\d+)?\s*", iza + t[e + 14:e + 30])
        if jed is None and rm:
            ost = (iza + t[e + 14:e + 30])[rm.end():]
            for naziv, rx in JEDINICE:
                if re.match(rx, ost):
                    jed = naziv; break  # raspon »2-5 m«
        om = re.search(r"(?<![\w])([A-ZČĆĐŠŽ]{1,3}[0-9₀-₉]*)\s*[-–:=]\s*$", prije)
        v = float(lit.replace(",", "."))
        out.append({"literal": lit, "vrijednost": v / 100 if jed == "%" else v, "jedinica": jed, "oznaka": om.group(1) if om else None,
                    "kontekst": t[max(0, s - 60):s] + "⟦" + lit + "⟧" + t[e:e + 40]})
    return out


def ima_broj(tekst, vrijednost, jedinica=None, oznaka=None):
    """Postoji li vrijednost (u jedinici, ako je zadana) u tekstu. Udio 0,4 odgovara zapisu »40 %«.
    Vrijednost pridružena oznaci (»P₁ - 15«: 15 mjesta na parkiralištu P₁) broji se samo kad se ta oznaka traži."""
    if isinstance(vrijednost, bool) or not isinstance(vrijednost, (int, float)):
        return False
    for b in brojevi(tekst):
        if b["oznaka"] != oznaka:
            continue
        if jedinica in ("%", "udio"):
            ok = (b["jedinica"] == "%" and abs(b["vrijednost"] - vrijednost) < 1e-9) or (b["jedinica"] is None and abs(b["vrijednost"] - vrijednost) < 1e-9 and "," in b["literal"])
        else:
            ok = abs(b["vrijednost"] - vrijednost) < 1e-9 and b["jedinica"] != "%" and (jedinica is None or b["jedinica"] == jedinica)
        if ok:
            return True
    return False


# ---------------------------------------------------------------- navodi
KONTEKST = [("clanak", r"(?:čl\.|članak|članka|članku|članci|članaka|člancima)"),
            ("stavak", r"(?:st\.|stavak|stavka|stavku|stavci|stavaka|stavcima)"),
            ("tocka", r"(?:t\.|točka|točke|točki|točaka|točkama)"),
            ("alineja", r"(?:al\.|alineja|alineje|alineji|alineja)")]


def _dio_navoda(dio):
    """Jedan dio navoda (bez »;«), slijeva nadesno: riječ »čl./st./t./al.« mijenja vrstu sljedećih brojeva;
    broj bez riječi je članak dok se ne navede stavak. »2. i 3.«, »1.–3.« i »1.–3. i 5.« ostaju u istoj vrsti."""
    tok = re.findall(r"čl\.|članak\w*|članci\w*|članc\w*|st\.|stav\w*|t\.|točk\w*|al\.|aline\w*|\d{1,3}|[–-]|\bdo\b|\bi\b|\bili\b|,|[a-z]\)", dio, re.I)
    vrsta, out, zadnji, raspon, par = "clanak", {"clanak": [], "stavak": [], "tocka": [], "alineja": [], "slovo": []}, None, False, []
    niz_clanaka, dvosmisleno = 0, False  # koliko je članaka navedeno zaredom prije stavka
    for t in tok:
        tl = t.lower()
        k = next((v for v, rx in KONTEKST if re.fullmatch(rx, tl) or (v == "clanak" and tl.startswith("član")) or (v == "stavak" and tl.startswith("stav")) or (v == "tocka" and tl.startswith("točk")) or (v == "alineja" and tl.startswith("aline"))), None)
        if k:
            if k == "stavak" and vrsta == "clanak" and niz_clanaka > 1:
                dvosmisleno = True  # »čl. 38. i 39. st. 2.«: ne zna se kojem članku pripada stavak
            if k == "clanak":
                niz_clanaka = 0
            vrsta, zadnji, raspon = k, None, False; continue
        if re.fullmatch(r"[a-z]\)", tl):
            out["slovo"].append(tl[0]); continue
        if t in ("–", "-") or tl == "do":
            raspon = zadnji is not None; continue
        if tl in ("i", "ili", ","):
            raspon = False; continue
        n = int(t)
        if raspon and zadnji is not None and 0 <= n - zadnji <= 50:
            novi = list(range(zadnji + 1, n + 1))
        else:
            novi = [n]
        out[vrsta] += novi
        if vrsta == "clanak":
            par += [{"clanak": x, "stavci": []} for x in novi]; niz_clanaka += len(novi)
        elif vrsta == "stavak" and par and not dvosmisleno:
            par[-1]["stavci"] += novi
        zadnji, raspon = n, False
    return out, par, dvosmisleno


def navod(s):
    """Navod iz tablice pravila → {vrsta, plan, clanci, stavci, tocke, alineje, slova, parovi}.
    Stavci (»st. 2. i 3.«, »st. 1.–3. i 5.«) nikad ne postaju članci; točka pojmovnika nije članak."""
    raw = str(s or "")
    t = re.sub(r"\s+", " ", raw).strip()
    plan = None
    pm = re.match(r"^(PPUG|UPU\s*\d+|KD\s*Krk)\b\s*", t, re.I)
    if pm:
        plan, t = pm.group(1), t[pm.end():]
    if re.search(r"pojmovnik", t, re.I):
        return {"vrsta": "POJMOVNIK", "plan": plan, "clanci": [], "stavci": [], "tocke": [int(x) for x in re.findall(r"točk\w*\s*(\d+)", t, re.I)],
                "alineje": [], "slova": [], "parovi": [], "dvosmisleno": False, "status": "JEDNOZNACNO", "izvorno": raw}
    sve = {"clanak": [], "stavak": [], "tocka": [], "alineja": [], "slovo": []}; parovi = []
    dvosm = False
    for dio in t.split(";"):
        o, p, dv = _dio_navoda(dio)
        dvosm = dvosm or dv
        for k in sve:
            sve[k] += o[k]
        parovi += p
    return {"vrsta": "CLANAK" if sve["clanak"] else "NEPOZNATO", "plan": plan, "clanci": sorted(set(sve["clanak"])),
            "stavci": sorted(set(sve["stavak"])), "tocke": sorted(set(sve["tocka"])) + sve["slovo"], "alineje": sorted(set(sve["alineja"])),
            "slova": sve["slovo"], "parovi": parovi, "dvosmisleno": dvosm, "status": "PREGLED" if dvosm else "JEDNOZNACNO", "izvorno": raw}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("pdf"); p.add_argument("--naslov", required=True); p.add_argument("--clanaka", type=int)
    p.add_argument("-o", "--izlaz", default="dokazi.json")
    a = p.parse_args(argv)
    r = izdvoji(a.pdf, a.naslov, a.clanaka)
    Path(a.izlaz).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("status", "razlog", "sha256", "broj_clanaka", "problemi", "zaglavlja_uklonjena")}, ensure_ascii=False))
    return 0 if r["status"] != "ABSTAIN_GRANICA_ODLUKE" else 2


if __name__ == "__main__":
    sys.exit(main())

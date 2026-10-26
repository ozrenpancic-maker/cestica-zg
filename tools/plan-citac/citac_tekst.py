#!/usr/bin/env python3
"""EKSPERIMENT: izdvajanje članaka iz običnog teksta ili HTML-a (npr. Službene novine PGŽ na webu, pročišćeni tekst PPUG-a).

Isti izlazni oblik kao citac.izdvoji() (članci s tekstom i blokovima), ali bez položaja u PDF-u: položaj je pomak
u normaliziranom tekstu datoteke. Ništa se ne potvrđuje pravno.

    python3 citac_tekst.py IZVOR.html|.txt [--clanci 22 23] -o dokazi.json
"""
import argparse, hashlib, html, json, re
from pathlib import Path
from citac import _spoji, SLOVO

SHEMA = "plan-citac-tekst/0.1"


def dekodiraj(raw):
    """UTF-8 ako je ispravan, inače kodna stranica iz <meta charset> (npr. Windows-1250, kako ga daje sn.pgz.hr)."""
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        m = re.search(rb'charset\s*=\s*["\']?([\w-]+)', raw[:4000], re.I)
        kod = (m.group(1).decode("ascii") if m else "windows-1250").lower()
        return raw.decode(kod, errors="replace"), kod


def u_tekst(raw, ime):
    """HTML → tekst s prijelomima redaka po blokovima; .txt ostaje kakav jest."""
    s = dekodiraj(raw)[0] if isinstance(raw, bytes) else raw
    if ime.lower().endswith((".htm", ".html")) or re.search(r"<(?:p|div|br|td)\b", s[:5000], re.I):
        s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
        s = re.sub(r"(?i)<br\s*/?>|</(?:p|div|tr|li|h\d)>", "\n", s)
        s = re.sub(r"<[^>]+>", " ", s)
        s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\r", "")
    return s


def izdvoji_tekst(putanja, clanci=None, dio=None):
    """dio: redni broj (1, 2, …) dijela dokumenta kad stranica sadrži više akata; dio počinje gdje numeracija
    članaka kreće ispočetka. Bez zadanog dijela, a uz više dijelova, vraća ABSTAIN_VISE_AKATA."""
    p = Path(putanja)
    raw = p.read_bytes()
    t = u_tekst(raw, p.name)
    zamjene = t.count("\ufffd")
    slova = sum(ch.isalpha() for ch in t) or 1
    if zamjene > 0.001 * slova:
        return {"shema": SHEMA, "izvor": p.name, "sha256": hashlib.sha256(raw).hexdigest(), "status": "ABSTAIN_KODIRANJE",
                "razlog": f"{zamjene} znakova zamijenjeno s U+FFFD (izgubljena slova s dijakriticima); izvor nije vjeran",
                "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False}
    linije = [re.sub(r"[ \t]+", " ", l).strip() for l in t.split("\n")]
    linije = [l for l in linije if l]
    # zaglavlja stranica glasila (»Stranica 2215 — broj 19«, naziv glasila, datum izdanja) uklanjaju se kao cijeli redci
    ZAGL = re.compile(r"^(?:Stranica \d+ [—–-] broj \d+.*|.*SLUŽBENE NOVINE PRIMORSKO-GORANSKE ŽUPANIJE.*|SLUŽBENE NOVINE|PRIMORSKO-GORANSKE ŽUPANIJE|(?:Ponedjeljak|Utorak|Srijeda|Četvrtak|Petak|Subota|Nedjelja), \d{1,2}\. \w+ \d{4}\..*)$")
    zaglavlja = sum(1 for l in linije if ZAGL.match(l))
    linije = [l for l in linije if not ZAGL.match(l)]
    # jedinice: »500 m2« → »500 m²« (eksponent u običnom tekstu)
    linije = [re.sub(r"(\d)\s*m([23])(?![\d\w])", lambda m: m.group(1) + " m" + ("²" if m.group(2) == "2" else "³"), l) for l in linije]
    # složenice s crticom: »a-b« unutar retka, ali i »a- b« unutar retka (razmak iza crtice u izvoru)
    slozenice = {m.group(1).lower() + "-" + m.group(2).lower() for l in linije for m in re.finditer(rf"(?<![{SLOVO}])([{SLOVO}]+)- ?([{SLOVO}]+)(?![{SLOVO}-])(?!$)", l)}
    # članak počinje retkom »Članak N.« (sam ili na početku retka)
    poc = [i for i, l in enumerate(linije) if re.match(r"^Članak\s+\d{1,3}\.", l)]
    # naslovi poglavlja neposredno ispred »Članak N.« (numerirani redak i njegovi nastavci bez interpunkcije) ne pripadaju prethodnom članku
    NASL = re.compile(r"^(?:[IVX]+\.|\d+(?:\.\d+)*\.)\s+\S")
    naslov_od = {}
    for i in poc:
        j, od = i - 1, None
        while j >= 0 and i - j <= 6 and not re.match(r"^Članak\s+\d", linije[j]):
            if NASL.match(linije[j]):
                od = j
            elif re.search(r"[.;:]$|,$", linije[j]) and od is None:
                break
            j -= 1
        if od is not None and all(not re.search(r"[;:]$", l) for l in linije[od:i]):
            naslov_od[i] = od
    # dijelovi dokumenta: numeracija članaka kreće ispočetka (npr. pročišćeni tekst PPUG-a pa UPU-a u istom broju glasila)
    brojevi_cl = [int(re.match(r"^Članak\s+(\d{1,3})", linije[i]).group(1)) for i in poc]
    granice = [0] + [k for k in range(1, len(poc)) if brojevi_cl[k] <= brojevi_cl[k - 1] and brojevi_cl[k] <= 4]
    dijelovi = [{"dio": d + 1, "od_clanka": brojevi_cl[g], "do_clanka": brojevi_cl[(granice[d + 1] if d + 1 < len(granice) else len(poc)) - 1],
                 "broj_clanaka": (granice[d + 1] if d + 1 < len(granice) else len(poc)) - g,
                 "naslov": next((linije[j] for j in range(poc[g] - 1, max(-1, poc[g] - 400), -1) if re.search(r"plan\w* uređenja|Odluk\w*", linije[j])), None)}
                for d, g in enumerate(granice)] if poc else []
    if len(dijelovi) > 1 and dio is None:
        return {"shema": SHEMA, "izvor": p.name, "sha256": hashlib.sha256(raw).hexdigest(), "status": "ABSTAIN_VISE_AKATA",
                "razlog": "dokument ima više dijelova s vlastitom numeracijom članaka; odaberi dio", "dijelovi": dijelovi,
                "clanci": {}, "automatska_potvrda": 0, "pravno_potvrdeno": False}
    kraj_dijela = len(linije)
    if dio is not None:
        g0 = granice[dio - 1]; g1 = granice[dio] if dio < len(granice) else len(poc)
        if g1 < len(poc):
            # dio završava ispred uvoda sljedećeg akta: zadnji potpis »Klasa:« ili naslov prije prvog članka sljedećeg dijela
            sljedeci = poc[g1]
            kraj_dijela = next((j for j in range(poc[g1 - 1] + 1, sljedeci) if re.match(r"^(?:Klasa:|Pročišćeni tekst|Glava [IVX]+\.)", linije[j])), sljedeci)
        poc = poc[g0:g1]
    out, problemi, viđeni = {}, [], {}
    for k, i in enumerate(poc):
        kraj = poc[k + 1] if k + 1 < len(poc) else kraj_dijela
        poglavlje = " ".join(linije[naslov_od[i]:i]) if i in naslov_od else None
        if k + 1 < len(poc) and poc[k + 1] in naslov_od:
            kraj = naslov_od[poc[k + 1]]
        n = int(re.match(r"^Članak\s+(\d{1,3})", linije[i]).group(1))
        viđeni[n] = viđeni.get(n, 0) + 1
        kljuc = str(n) if viđeni[n] == 1 else f"{n}#{viđeni[n]}"
        if viđeni[n] == 2:
            problemi.append({"vrsta": "PONOVLJENI_CLANAK", "clanak": n})
        if clanci and n not in clanci:
            continue
        tekst, odl = "", []
        for l in linije[i:kraj]:
            tekst = _spoji(tekst, l, slozenice, odl)
        tekst = re.sub(r"^Članak\s+\d{1,3}\.\s*", "", tekst)
        out[kljuc] = {"broj": n, "tekst": tekst, "crtice": odl, "poglavlje": poglavlje,
                      "blokovi": [{"tekst": tekst, "stranica": None, "stupac": None, "okvir": None, "redak": i + 1}],
                      "izvor": {"datoteka": p.name, "redak": i + 1}, "tablice": [], "status_tablica": None}
    return {"shema": SHEMA, "izvor": p.name, "sha256": hashlib.sha256(raw).hexdigest(), "status": "IZDVOJENO_NIJE_PRAVNA_PROVJERA",
            "dijelovi": dijelovi, "odabrani_dio": dio, "broj_clanaka": len(poc), "zaglavlja_uklonjena": zaglavlja,
            "problemi": problemi, "clanci": out, "automatska_potvrda": 0, "pravno_potvrdeno": False}


if __name__ == "__main__":
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("izvor"); a.add_argument("--clanci", type=int, nargs="*"); a.add_argument("--dio", type=int); a.add_argument("-o", "--izlaz", default="dokazi_tekst.json")
    x = a.parse_args()
    r = izdvoji_tekst(x.izvor, x.clanci, x.dio)
    Path(x.izlaz).write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: r.get(k) for k in ("status", "razlog", "sha256", "dijelovi", "broj_clanaka", "problemi")}, ensure_ascii=False))

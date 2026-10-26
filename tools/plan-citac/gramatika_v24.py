#!/usr/bin/env python3
"""EKSPERIMENT v2.4: odredbe o pomoćnim građevinama koje v2.2/v2.3 odbija (PREDMET_NEPOZNAT, VRIJEDNOST_NEPREPOZNATA,
OBLIK_ODREDBE_DJELOMICAN) ili ostavlja bez pravila. Zamrznuti gramatika_v22.py se ne mijenja; ovdje su samo novi oblici
odredbe, a zapis pravila (citat, uvjeti, obuhvat, statusi) radi zamrznuti gramatika_v22._zapisi.

Oblici (svaki je doslovan; vrijednosti i uvjeti uzimaju se iz teksta, ništa se ne nadopunjuje):
  E  »Pomoćne građevine grade se kao jednoetažne …«               → etaže = »jednoetažne« (kako piše)
  V  »visina od najniže kote … nije viša od visine osnovne građevine (,| i) ne prelazi visinu od N m [i jednoetažna je]«
                                                                    → visina ≤ visina osnovne građevine; visina ≤ N m;
                                                                      [etaže = »jednoetažna«]; uvijek PREGLED (gornja točka)
  T  »tlocrtna projekcija nije veća od N m²«                        → tlocrtna projekcija ≤ N m²
  G  »[iznimno, unutar …,] [pomoćne građevine] (se) mogu (se) graditi do granice građevne čestice«
                                                                    → prislanjanje: dopušteno do granice čestice
  O  »Ako imaju otvore prema susjednoj građevnoj čestici, moraju biti udaljene od te čestice najmanje N m«
                                                                    → udaljenost od granice ≥ N m, UVJETNO
  Z  »Ako se grade na granici građevne čestice, moraju od susjedne građevine biti odijeljene vatrobranim zidom,
      uz uvjet da nagib krova nije prema susjednoj građevnoj čestici«
                                                                    → vatrobrani zid (opisni zahtjev, UVJETNO); zabrana nagiba prema
                                                                      susjednoj čestici (PREGLED: odnos uvjeta nejasan)
  R  »Na regulacijskom pravcu mogu se graditi samo garaže, kada …«  → dopuštenje (PREGLED: »odnosno«, lokalni uvjeti)
  K  alineja o krovištu koja v2.2 odbija samo zbog zareza na kraju (razdjelnik alineja) → ponovna raščlamba bez zareza
Parametri izvan zatvorenog popisa uputa (vatrobrani zid, smjer nagiba, garaža na regulacijskom pravcu) uvijek su PREGLED
(PARAMETAR_IZVAN_POPISA), da se ne prihvate bez usporedivog naziva.
"""
import re
import gramatika_v22 as g2

VERZIJA = "gramatika-v2.4"
R, zapis, N = g2.R, g2.zapis, g2.N
broj = lambda s: float(s.replace(",", "."))
M_JED = r"(?:m|metra|metara)\b"
IZVAN_POPISA = R("PARAMETAR_IZVAN_POPISA", "parametar nije u zatvorenom popisu uputa za označavanje; prihvaća se tek uz pregled")
VIS = R("REFERENTNA_VISINA_NEPOTPUNA", "navedena je samo donja točka mjerenja; gornja točka mjerenja visine nije navedena")
NAPOMENA_VIS = "mjereno od najniže kote konačno zaravnatog terena"


def _iznimka(t):
    m = re.match(r"iznimno,?\s*(?P<u>unutar [^,.]+?\bcjelin\w*),?\s*", t, re.I)
    return (m["u"], t[m.end():]) if m else (None, t)


def oblici(t, kont):
    """Vraća (zapisi, iskorišteni brojevi) ili None ako rečenica nije ni jedan od oblika v2.4."""
    t = t.strip()
    izn, t1 = _iznimka(t)
    sk = kont.get("skupine")
    kw = dict(skupine=sk)

    m = re.match(r"pomoćne građevine grade se kao (?P<v>jednoetažne)\b", t1, re.I)
    if m:
        return [zapis("etazeMax", "=", m["v"], None, "OSNOVNO", skupine=("pomocna",))], []

    m = re.match(rf"visina od (?P<ref>najniže kote konačno zaravnatog terena) nije viša od (?P<o>visine osnovne građevine)\s*(?:,|i)\s*"
                 rf"ne prelazi visinu od (?P<v>{N})\s*{M_JED}(?P<e>,?\s*i jednoetažna je)?\s*[.,;]?$", t1, re.I)
    if m:
        out = [zapis("visinaMax", "<=", "visina osnovne građevine", "opis", "OSNOVNO", vrijednost_vrsta="opis", napomena=NAPOMENA_VIS,
                     razlozi=[VIS, R("REFERENTNA_VISINA_NEPOZNATA", "nije navedeno kako se mjeri visina osnovne građevine")], **kw),
               zapis("visinaMax", "<=", broj(m["v"]), "m", "OSNOVNO", napomena=NAPOMENA_VIS, razlozi=[VIS], **kw)]
        if m["e"]:
            out.append(zapis("etazeMax", "=", "jednoetažna", None, "OSNOVNO", **kw))
        return out, [m["v"]]

    m = re.match(rf"tlocrtna projekcija nije veća od (?P<v>{N})\s*(?:m\s*2|m²)\s*[.,;]?$", t1, re.I)
    if m:
        return [zapis("tlMax", "<=", broj(m["v"]), "m²", "OSNOVNO", **kw)], [m["v"]]

    m = re.match(r"(?:pomoćne građevine\s+)?(?:se\s+)?mogu\s+(?:se\s+)?graditi do granice građevne čestice\s*[.,;]?$", t1, re.I)
    if m:
        return [zapis("nacinPrislanjanja", "dopusteno", "do granice građevne čestice", "opis", "OSNOVNO", vrijednost_vrsta="opis",
                      uvjeti=[izn] if izn else [], **kw)], []

    m = re.match(rf"(?P<u>ako imaju otvore prema susjednoj građevnoj čestici),\s*moraju biti udaljene od te čestice najmanje (?P<v>{N})\s*{M_JED}\s*[.,;]?$", t1, re.I)
    if m:
        return [zapis("udaljenostOdGraniceCestice", ">=", broj(m["v"]), "m", "UVJETNO", uvjeti=[m["u"]],
                      napomena="udaljenost od granice susjedne građevne čestice (izričito u odredbi)", **kw)], [m["v"]]

    m = re.match(r"(?P<u>ako se grade na granici građevne čestice),\s*moraju od susjedne građevine biti odijeljene (?P<v>vatrobranim zidom),\s*"
                 r"uz uvjet da (?P<n>nagib krova nije prema susjednoj građevnoj čestici)\s*[.,;]?$", t1, re.I)
    if m:
        return [zapis("vatrobraniZid", "opis", "vatrobrani zid", "opis", "UVJETNO", vrijednost_vrsta="opis", uvjeti=[m["u"]], razlozi=[IZVAN_POPISA], **kw),
                zapis("nagibPremaSusjednoj", "zabranjeno", "prema susjednoj građevnoj čestici", "opis", "NEGATIVNO", vrijednost_vrsta="opis",
                      uvjeti=[m["u"]], razlozi=[IZVAN_POPISA, R("ODNOS_UVJETA_NEJASAN",
                                                               "nije jasno je li zabrana nagiba uvjet za gradnju na granici ili za vatrobrani zid; ne odnosi se na ravni krov")], **kw)], []

    m = re.match(r"na regulacijskom pravcu mogu se graditi samo (?P<g>garaže),\s*(?P<u>kada .+?)\s*[.,;]?$", t1, re.I)
    if m:
        return [zapis("garazaNaRegulaciji", "dopusteno", "samo garaže na regulacijskom pravcu", "opis", "IZNIMKA", vrijednost_vrsta="opis",
                      uvjeti=[m["u"]], skupine=("pomocna",),
                      razlozi=[IZVAN_POPISA, R("VEZNIK_ODNOSNO", "dvostruki »odnosno«: nije jasno jesu li uvjeti kumulativni ili alternativni"),
                               R("NEDEFINIRAN_POJAM", "»konfiguracija terena«, »lokalni uvjeti« nisu definirani")])], \
            [b["literal"] for b in g2.brojevi(g2.normaliziraj(m["u"]))]

    if re.match(r"krovišta mogu biti", t1, re.I) and re.search(r"[,;]\s*$", t1):
        zap, ost, rz, nk = g2.odredba(t1.rstrip(" ,;") + ".", kont)
        if zap and not rz:
            for z in zap:
                z["napomena"] = ((z["napomena"] + "; ") if z["napomena"] else "") + "zarez na kraju alineje uklonjen prije raščlambe (v2.4)"
            return zap, [b["literal"] for b in g2.brojevi(g2.normaliziraj(t1))]
    return None


def primijeni_iznimku(zap, izn):
    """Alineja koja počinje »iznimno, unutar … cjelina«: uvjet i vrsta IZNIMKA vrijede za sve rečenice alineje (kao v2.2)."""
    for z in zap:
        if izn and izn not in z["uvjeti"]:
            z["uvjeti"] = [izn] + list(z["uvjeti"])
        if izn and z["vrsta_pravila"] in ("OSNOVNO", "UVJETNO"):
            z["vrsta_pravila"] = "IZNIMKA"
    return zap

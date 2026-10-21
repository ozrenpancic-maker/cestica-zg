#!/usr/bin/env python3
"""Prototip: dohvat i strojna obrada odluka iz Službenih novina PGŽ (sn.pgz.hr).

Načela:
- Nema nagađanja: skripta samo dohvaća, razdvaja i označava; brojke koje izdvoji su KANDIDATI (status „strojno”)
  dok ih čovjek ne potvrdi uz članak i verziju.
- Umjeren dohvat: najviše 1 zahtjev u 2 s, predmemorija na disku (isti URL se ne dohvaća dvaput), jasan User-Agent,
  provjera robots.txt, samo popis ID-ova koji se izričito zadaju (nema pretraživanja cijele stranice).
- Izvorni tekst se NE objavljuje u repozitoriju (stranica nosi „Sva prava pridržana”); u bazi se čuvaju kratki citati,
  poveznica, članak, glasilo i sažetak teksta (SHA-256) za provjeru.
Mrežni dio mora raditi s računala koje smije do sn.pgz.hr; okruženje u kojem je alat napisan to ne smije.
"""
import hashlib, html, json, os, re, sys, time, urllib.request, urllib.robotparser
from html.parser import HTMLParser

BASE = "https://www.sn.pgz.hr/"
UA = "CesticaHR-prototype/0.1 (istrazivanje javnih prostornih planova; kontakt: ozren.pancic@gmail.com)"
DELAY = 2.0
MJESECI = {"siječnja":1,"veljače":2,"ožujka":3,"travnja":4,"svibnja":5,"lipnja":6,"srpnja":7,"kolovoza":8,"rujna":9,"listopada":10,"studenoga":11,"studenog":11,"prosinca":12}
RIM = {"I":1,"V":5,"X":10,"L":50,"C":100}

# ---------------------------------------------------------------- dohvat
class Dohvat:
    def __init__(self, cache="sn-cache"):
        self.cache = cache; os.makedirs(cache, exist_ok=True); self._t = 0; self._rp = None
    def _robots_ok(self, url):
        if self._rp is None:
            self._rp = urllib.robotparser.RobotFileParser(BASE + "robots.txt")
            try: self._rp.read()
            except Exception: self._rp = False   # robots.txt nedostupan: dopušteno uz umjeren dohvat
        return True if self._rp is False else self._rp.can_fetch(UA, url)
    def get(self, url):
        key = hashlib.sha256(url.encode()).hexdigest()[:16]; p = os.path.join(self.cache, key + ".html")
        if os.path.exists(p): return open(p, "rb").read().decode(self._enc(p), "replace")
        if not self._robots_ok(url): raise RuntimeError("robots.txt zabranjuje: " + url)
        w = DELAY - (time.time() - self._t)
        if w > 0: time.sleep(w)
        rq = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(rq, timeout=30) as r: raw = r.read(); ct = r.headers.get_content_charset() or "utf-8"
        self._t = time.time(); open(p, "wb").write(raw); open(p + ".enc", "w").write(ct)
        return raw.decode(ct, "replace")
    def _enc(self, p):
        try: return open(p + ".enc").read().strip() or "utf-8"
        except Exception: return "utf-8"
    def odluka(self, id_): return self.get(f"{BASE}default.asp?Link=odluke&id={int(id_)}")

# ---------------------------------------------------------------- HTML -> tekst
class _T(HTMLParser):
    def __init__(self): super().__init__(); self.o = []; self.skip = 0
    def handle_starttag(self, t, a):
        if t in ("script", "style"): self.skip += 1
        if t in ("br", "p", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"): self.o.append("\n")
    def handle_endtag(self, t):
        if t in ("script", "style"): self.skip = max(0, self.skip - 1)
        if t in ("p", "div", "tr", "li", "table"): self.o.append("\n")
    def handle_data(self, d):
        if not self.skip: self.o.append(d)
def u_tekst(src):
    if "<" in src[:2000] and re.search(r"<(html|body|p|div|table)\b", src, re.I):
        p = _T(); p.feed(src); src = "".join(p.o)
    src = html.unescape(src).replace("\xa0", " ").replace("\t", " ")
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ ]{2,}", " ", src)).strip()
def norm(s): return re.sub(r"\s+", " ", s.replace("»", "„").replace("«", "“").replace("”", "“")).strip()

# ---------------------------------------------------------------- zaglavlje i vrsta odluke
def rim(s):
    t = 0; v = [RIM[c] for c in s.upper() if c in RIM]
    for i, x in enumerate(v): t += -x if i + 1 < len(v) and v[i + 1] > x else x
    return t
def zaglavlje(t):
    """glasilo (broj, godina, datum), tijelo i redni broj odluke iz teksta stranice"""
    o = {"broj": None, "godina_izdanja": None, "datum": None, "stavka": None, "tijelo": None}
    m = re.search(r"Godina\s+([IVXLC]+)\.?\s*-\s*broj\s+(\d+)\.?", t)
    if m: o["godina_izdanja"], o["broj"] = rim(m.group(1)), int(m.group(2))
    m = re.search(r"(\d{1,2})\.\s*([a-zčćžšđ]+)\s+(\d{4})\.", t)
    if m and m.group(2) in MJESECI: o["datum"] = "%04d-%02d-%02d" % (int(m.group(3)), MJESECI[m.group(2)], int(m.group(1)))
    m = re.search(r"\n\s*(OPĆINA|GRAD|ŽUPANIJA)\s+([A-ZČĆŽŠĐ \-]+?)\s*\n\s*(\d+)\.\s*\n", t)
    if m: o["tijelo"], o["stavka"] = (m.group(1) + " " + m.group(2)).title(), int(m.group(3))
    return o
VRSTE = [  # redoslijed je važan: prvo specifičnije
    ("izvan_snage",   r"stavlja(nju)?\s+izvan\s+snage|prestanku\s+važenja"),
    ("tumacenje",     r"vjerodostojn\w*\s+tuma[cč]enj"),
    ("izrada",        r"odluk\w*\s+o\s+izradi"),
    ("procisceni",    r"pro[cč]i[sš][cć]en\w*\s+tekst"),
    ("izmjene",       r"izmjen\w*\s+i\s+dopun\w*|ciljan\w*\s+izmjen|izmjen\w*\s+(?:prostornog|urbanisti)"),
    ("donosenje",     r"odluk\w*\s+o\s+donošenju|odluk\w*\s+o\s+donosenju"),
]
def vrsta(naslov):
    n = norm(naslov).lower()
    for k, rx in VRSTE:
        if re.search(rx, n):
            if k == "izmjene" and re.search(r"odluk\w*\s+o\s+izradi", n): return "izrada"
            return k
    return "nepoznato"
def naslov_odluke(t):
    m = re.search(r"\bODLUKU?\b\s*\n?(.{10,300}?)\n\s*(?:I\.|OPĆE|TEMELJNE|Članak)", t, re.S)
    return norm(m.group(1)) if m else None

# ---------------------------------------------------------------- članci i operacije
RE_CL = re.compile(r"^\s*Članak\s+(\d+[a-z]?)\.\s*$", re.M)
def clanci(t):
    """članci SAME odluke (ne članci plana koje mijenja)"""
    ms = list(RE_CL.finditer(t)); out = []
    for i, m in enumerate(ms):
        a, b = m.end(), (ms[i + 1].start() if i + 1 < len(ms) else len(t))
        out.append({"clanak": m.group(1), "tekst": t[a:b].strip()})
    return out
OP = [("brise", r"(?:brišu?\s+se|briše\s+se|se\s+brišu?)"), ("zamjena_rijeci", r"zamjenjuj\w*\s+se|zamjenjuje\s+se"),
      ("dodaje", r"dodaj\w*\s+se|dodaju\s+se"), ("mijenja", r"mijenja\s+se|mijenjaju\s+se")]
def operacije(tekst):
    """što članak odluke radi s člancima plana: [{cilj, stavak, tocka, vrsta, cijeli_clanak, citat}] (strojno, treba provjeru)"""
    ops = []; T = norm(tekst)
    T = re.sub(r"\b(\d+)\.([a-z])\b(?!\w)", r"\1\2.", T)      # „28.a” i „50.d” -> „28a”, „50d”
    # „Članak 44. mijenja se i glasi” = zamjena cijelog članka
    for m in re.finditer(r"Članak\s+(\d+[a-z]?)\.\s+(mijenja\s+se\s+i\s+glasi|se\s+briše|briše\s+se)", T):
        ops.append({"cilj": m.group(1), "stavak": None, "tocka": None, "vrsta": "mijenja" if "mijenja" in m.group(2) else "brise", "cijeli_clanak": True, "citat": T[m.start():m.end() + 40]})
    # „U članku 46a. stavku 1. točka 4. mijenja se i glasi”, „U članku 29. stavak 4. mijenja se…”
    for m in re.finditer(r"U\s+članku\s+(\d+[a-z]?)\.\s*(?:\S+\s+)??(?:(?:stavk\w+|stavak)\s+(\d+[a-z]?)\.)?\s*(?:(?:točk\w+|alineja)\s+(\d+)\.)?", T):
        rest = T[m.end():m.end() + 160]; v = None
        for k, rx in OP:
            mm = re.search(rx, rest)
            if mm and (v is None or mm.start() < v[1]): v = (k, mm.start())
        if v and re.match(r"\s*(?:riječ|brojk|tekst)", rest) and v[0] in ("brise", "zamjena_rijeci"): v = ("brisanje_rijeci" if v[0] == "brise" else "zamjena_rijeci", v[1])
        if v: ops.append({"cilj": m.group(1), "stavak": m.group(2), "tocka": m.group(3), "vrsta": v[0], "cijeli_clanak": False, "citat": T[m.start():m.end() + 70]})
    for m in re.finditer(r"Iza\s+članka\s+(\d+[a-z]?)\.\s+dodaje\s+se[^„»]{0,120}?(?:novi\s+)?članak\s+(\d+[a-z]?)\.", T):
        ops.append({"cilj": m.group(2), "stavak": None, "tocka": None, "vrsta": "dodaje", "cijeli_clanak": True, "citat": T[m.start():m.end()]})
    for m in re.finditer(r"(?:Naslov\s+iznad\s+)?[Čč]lan(?:ak|ka|ku)\s+(\d+[a-z]?)\.?\s*(?:i\s+njegov\s+naslov\s+)?\s*brišu?\s+se", T):
        if not any(o["cilj"] == m.group(1) and o["vrsta"] == "brise" for o in ops):
            ops.append({"cilj": m.group(1), "stavak": None, "tocka": None, "vrsta": "brise", "cijeli_clanak": True, "citat": T[max(0, m.start() - 20):m.end()]})
    return ops

# ---------------------------------------------------------------- kandidati za brojčane vrijednosti
KAND = [("kig", r"\bkig\b[^.;\n]{0,50}?(\d[,.]\d+)"), ("kis", r"\bkis\b[^.;\n]{0,50}?(\d[,.]\d+)"),
        ("povrsina_m2", r"(\d[\d.]*(?:,\d+)?)\s*m\s*[2²]\b"), ("duljina_m", r"(?<![\d,])(\d+(?:,\d+)?)\s*m(?![\w²2])"),
        ("postotak", r"(\d+(?:,\d+)?)\s*%"), ("etaze", r"\b(P\s*\+\s*\d|Po\s*\+\s*P\s*\+\s*\d|\w+\s+nadzemn\w+\s+etaž\w+)")]
def kandidati(tekst):
    T = norm(tekst); out = []
    for k, rx in KAND:
        for m in re.finditer(rx, T, re.I):
            out.append({"vrsta": k, "vrijednost": m.group(1), "kontekst": T[max(0, m.start() - 70):m.end() + 50], "status": "strojno"})
    return out

# ---------------------------------------------------------------- loza članaka plana kroz odluke
def loza(odluke):
    """odluke: [{id, datum, vrsta, tekst}] -> po članku plana popis operacija kronološki + procjena stanja.
    Stanje je samo uputa gdje FALI osnovni tekst: djelomične izmjene bez poznate osnove označene su 'osnova_potrebna'."""
    L = {}
    for od in sorted(odluke, key=lambda o: o.get("datum") or ""):
        if od.get("vrsta") not in ("izmjene", "donosenje", "procisceni"): continue
        for c in clanci(od["tekst"]):
            for op in operacije(c["tekst"]):
                L.setdefault(op["cilj"], []).append({"odluka": od["id"], "datum": od.get("datum"), "clanak_odluke": c["clanak"], **op})
    for a, ops in L.items():
        last_full = max((i for i, o in enumerate(ops) if o["cijeli_clanak"] and o["vrsta"] in ("mijenja", "dodaje")), default=None)
        after = ops[last_full + 1:] if last_full is not None else ops
        stanje = "izbrisan" if ops[-1]["vrsta"] == "brise" and ops[-1]["cijeli_clanak"] else \
                 ("cijeli_tekst_poznat" if last_full is not None and not after else
                  ("cijeli_tekst_pa_djelomicne_izmjene" if last_full is not None else "osnova_potrebna"))
        L[a] = {"stanje": stanje, "operacije": ops}
    return L

def hash_teksta(t): return hashlib.sha256(norm(t).encode()).hexdigest()

def analiziraj(src, id_=None):
    t = u_tekst(src); z = zaglavlje(t); nas = naslov_odluke(t)
    return {"id": id_, **z, "naslov": nas, "vrsta": vrsta(nas or t[:400]), "sha256": hash_teksta(t), "broj_clanaka": len(clanci(t)), "tekst": t}

if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] == "fetch":
        D = Dohvat(); 
        for i in a[1:]:
            r = analiziraj(D.odluka(i), int(i)); r.pop("tekst"); print(json.dumps(r, ensure_ascii=False))
    elif len(a) == 2 and a[0] == "analiziraj":
        r = analiziraj(open(a[1], encoding="utf-8").read()); ops = [dict(c=c["clanak"], ops=operacije(c["tekst"])) for c in clanci(r["tekst"])]
        r.pop("tekst"); r["operacije"] = ops; print(json.dumps(r, ensure_ascii=False, indent=1))
    else: print(__doc__); print("Upotreba: sn_pgz.py fetch ID… | sn_pgz.py analiziraj datoteka.txt")

"""Sastavlja index.html iz predloška i tablice urbanih pravila.
Korištenje: python3 build.py
Pravila se ponovno izvlače iz PDF-a Odluke o GUP-u ovako:
  pdftotext -layout GUPGZ-ID2025__ODLUKA-nesluzbeno-procisceno.pdf proc.txt
  python3 src/parse_gup.py proc.txt src/rules.json
"""
import json, pathlib, sys
root = pathlib.Path(__file__).parent

import re
def normalize_rules(rules):
    """Zone u kojima je cijelo pravilo jedna rečenica (npr. "u zoni poslovne namjene Gradnja prema ...") parser spoji s nazivom zone.
    Ovdje se naziv i tekst razdvajaju, da se pravilo prikaže kao stavka."""
    for r in rules.values():
        for z in r.get("zone", []):
            if not z.get("items"):
                m = re.match(r"^(u zoni .*?namjene(?:\s+K\d)?)\s+(\S.*)$", z.get("zona", ""), re.S)
                if m:
                    z["zona"], z["items"] = m.group(1), [m.group(2).strip()]
                    z.setdefault("key", {})
    return rules

def check_rules(name, rules):
    """Provjera strukture pravila prije ugradnje, da se pogrešno izvučena datoteka ne objavi."""
    errs = []
    if not isinstance(rules, dict) or not rules:
        errs.append(f"{name}: datoteka je prazna ili nije objekt")
    for code, r in (rules or {}).items():
        for k in ("clanak", "naziv", "zone", "tekst"):
            if k not in r:
                errs.append(f"{name} {code}: nedostaje polje '{k}'")
        for z in r.get("zone", []):
            if not z.get("zona") or not isinstance(z.get("items"), list) or not z["items"]:
                errs.append(f"{name} {code}: zona bez naziva ili stavki")
            if not isinstance(z.get("key"), dict):
                errs.append(f"{name} {code}: zona '{z.get('zona','')[:30]}' nema ključeve parametara")
    if errs:
        print("\n".join(errs)); sys.exit(1)
rules = json.loads((root / "src/rules.json").read_text(encoding="utf-8")); rules = normalize_rules(rules); check_rules("GUP", rules)
tpl = (root / "src/app.template.html").read_text(encoding="utf-8")
data = json.dumps(rules, ensure_ascii=False).replace("</", "<\\/")
rules_se = json.loads((root / "src/rules_sesvete.json").read_text(encoding="utf-8")); rules_se = normalize_rules(rules_se); check_rules("SE", rules_se)
data_se = json.dumps(rules_se, ensure_ascii=False).replace("</", "<\\/")
rules_pp = json.loads((root / "src/rules_ppgz.json").read_text(encoding="utf-8")); rules_pp = normalize_rules(rules_pp); check_rules("PP", rules_pp)
meta = json.loads((root / "src/rules_meta.json").read_text(encoding="utf-8"))
data_meta = json.dumps(meta, ensure_ascii=False).replace("</", "<\\/")
data_pp = json.dumps(rules_pp, ensure_ascii=False).replace("</", "<\\/")
# pravila PPUG Grada Krka (pilot): parametri s navodima iz teksta
def check_krk(r):
    errs=[]
    for k in ("izvor","naselja","tipovi","meda","regulacija","zelenilo","izravnaProvedba","neizgradeni"):
        if k not in r: errs.append(f"KRK: nedostaje '{k}'")
    for t,v in r.get("tipovi",{}).items():
        for s in ("slob","dvoj"):
            for f in ("minC","izg","kis","kisPodrum","tlMin","tlMax"):
                if not isinstance(v.get(s,{}).get(f),(int,float)): errs.append(f"KRK {t}.{s}: nedostaje broj '{f}'")
        for f in ("clanak","gbpMax","visina","etaze"):
            if f not in v: errs.append(f"KRK {t}: nedostaje '{f}'")
    if errs: print("\n".join(errs)); sys.exit(1)
rules_krk = json.loads((root / "src/rules_krk.json").read_text(encoding="utf-8")); check_krk(rules_krk)
data_krk = json.dumps(rules_krk, ensure_ascii=False).replace("</", "<\\/")
# baza pravila iz ČesticaHR Data Managera (nije obavezna): provjera prije ugradnje (tools/baza/provjeri.py)
data_db = "null"
db_path = root / "src/baza/baza.json"
if db_path.exists():
    sys.path.insert(0, str(root / "tools/baza")); import provjeri as _pdb
    _db = json.loads(db_path.read_text(encoding="utf-8")); _E, _W, _n = _pdb.provjeri(_db)
    if _E: print("\n".join("BAZA: " + e for e in _E)); sys.exit(1)
    data_db = json.dumps(_db, ensure_ascii=False).replace("</", "<\\/")
    print(f"baza pravila: {_n}")
# potvrđene šifre kartografskih listova ISPU-a (nije obavezno): provjera prije ugradnje (tools/ispu/provjeri_sifre.py)
data_ispu = "null"
ispu_path = root / "src/ispu_sifre.json"
if ispu_path.exists():
    sys.path.insert(0, str(root / "tools/ispu")); import provjeri_sifre as _pis
    _is = json.loads(ispu_path.read_text(encoding="utf-8")); _E, _W = _pis.provjeri(_is)
    if _E: print("\n".join("ISPU ŠIFRE: " + e for e in _E)); sys.exit(1)
    data_ispu = json.dumps(_is, ensure_ascii=False).replace("</", "<\\/")
    print(f"ISPU šifre: {sum(1 for z in _is['zapisi'] if z.get('status') == 'potvrđeno')} potvrđenih")
import datetime
ver = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime("%d.%m.%Y. %H:%M")
(root / "index.html").write_text(tpl.replace("/*RULES*/null", data).replace("/*RULES_SE*/null", data_se).replace("/*RULES_PP*/null", data_pp).replace("/*RULES_META*/null", data_meta).replace("/*RULES_KRK*/null", data_krk).replace("/*RULES_DB*/null", data_db).replace("/*ISPU_SIFRE*/null", data_ispu).replace("/*VERSION*/", ver), encoding="utf-8")
# service worker: verzija = sažetak sadržaja stranice i ljuske, pa svaka promjena aplikacije daje novi sw.js
import hashlib
h = hashlib.sha256()
for f in ["index.html", "manifest.webmanifest", "icon.svg", "icons/icon-192.png", "icons/icon-512.png", "icons/icon-maskable-192.png", "icons/icon-maskable-512.png", "vendor/leaflet-1.9.4/leaflet.js", "vendor/leaflet-1.9.4/leaflet.css", "vendor/turf-6.5.0/turf.min.js"]:
    h.update((root / f).read_bytes())
sw_ver = h.hexdigest()[:12]
(root / "sw.js").write_text((root / "src/sw.template.js").read_text(encoding="utf-8").replace("/*SW_VERSION*/", sw_ver), encoding="utf-8")
print("index.html sastavljen; sw.js verzija", sw_ver)

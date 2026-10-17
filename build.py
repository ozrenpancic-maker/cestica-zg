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
import datetime
ver = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime("%d.%m.%Y. %H:%M")
(root / "index.html").write_text(tpl.replace("/*RULES*/null", data).replace("/*RULES_SE*/null", data_se).replace("/*RULES_PP*/null", data_pp).replace("/*RULES_META*/null", data_meta).replace("/*VERSION*/", ver), encoding="utf-8")
print("index.html sastavljen")

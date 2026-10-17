"""Sastavlja index.html iz predloška i tablice urbanih pravila.
Korištenje: python3 build.py
Pravila se ponovno izvlače iz PDF-a Odluke o GUP-u ovako:
  pdftotext -layout GUPGZ-ID2025__ODLUKA-nesluzbeno-procisceno.pdf proc.txt
  python3 src/parse_gup.py proc.txt src/rules.json
"""
import json, pathlib
root = pathlib.Path(__file__).parent
rules = json.loads((root / "src/rules.json").read_text(encoding="utf-8"))
tpl = (root / "src/app.template.html").read_text(encoding="utf-8")
data = json.dumps(rules, ensure_ascii=False).replace("</", "<\\/")
rules_se = json.loads((root / "src/rules_sesvete.json").read_text(encoding="utf-8"))
data_se = json.dumps(rules_se, ensure_ascii=False).replace("</", "<\\/")
rules_pp = json.loads((root / "src/rules_ppgz.json").read_text(encoding="utf-8"))
data_pp = json.dumps(rules_pp, ensure_ascii=False).replace("</", "<\\/")
import datetime
ver = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=2))).strftime("%d.%m.%Y. %H:%M")
(root / "index.html").write_text(tpl.replace("/*RULES*/null", data).replace("/*RULES_SE*/null", data_se).replace("/*RULES_PP*/null", data_pp).replace("/*VERSION*/", ver), encoding="utf-8")
print("index.html sastavljen")

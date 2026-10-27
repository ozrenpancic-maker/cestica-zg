#!/usr/bin/env python3
"""Test audita baze pravila (tools/baza/audit_pravila.py): python3 tests/plan_integrity/test_audit.py"""
import json, sys
from pathlib import Path
R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "tools/baza"))
import audit_pravila as A

ok = []; bad = []
def t(n, c): (ok if c else bad).append(n)

plan = {"id": "P", "naziv": "P", "vrsta": "UPU", "status_vazenja": "važeći", "primjenjiva_revizija": "R1", "obuhvat": {"jls": ["X"]}, "odluke": [{"id": "O", "naziv": "O", "vrsta": "donošenje", "glasilo": "SN", "url": "https://e.org"}]}
base = {"plan_id": "P", "odluka_id": "O", "parametar": "kig", "vrijednost": 0.25, "clanak": "38", "citat": "najveći koeficijent izgrađenosti građevne čestice iznosi 0,25",
        "izvor_revizija": "R1", "primjenjivost": {"zone": ["M11"], "vrste_gradnje": ["obiteljska kuća"], "zahvat": ["nova gradnja"]}, "pravni_status": {"razina": "potvrđeno"}, "gis_status": {"razina": "potvrđeno"}}
def r(i, **o):
    x = json.loads(json.dumps(base)); x["id"] = i
    for k, v in o.items():
        if k == "pr": x["primjenjivost"].update(v)
        elif v is None: x.pop(k, None)
        else: x[k] = v
    return x
B = {"planovi": [plan], "pravila": [
    r("cisto"),
    r("uvjet", uvjet="osim uz javnu cestu"), r("uvjet-ok", uvjet="x", status_uvjeta="razriješeno"),
    r("iznimka", iznimke=["400 m2 u okruženju izgrađenih čestica"]),
    r("vrsta-prazno", pr={"vrste_gradnje": []}), r("vrsta-sve", pr={"vrste_gradnje": ["sve"]}),
    r("zahvat", pr={"zahvat": []}),
    r("rev-nema", izvor_revizija=None), r("rev-razlika", izvor_revizija="R0"),
    r("cit-nema", citat=""), r("cit-skracen", citat="najveći koeficijent … 0,25"), r("cit-vrijednost", citat="najveći koeficijent izgrađenosti građevne čestice iznosi 0,30"),
]}
a = A.audit(B); K = {x["id"]: set(x["kategorije"]) for x in a["detalji"]}
t("čisto pravilo nema nalaza", K["cisto"] == set())
t("nerazriješen uvjet", "uvjet_nerazrijesen" in K["uvjet"] and "uvjet_nerazrijesen" not in K["uvjet-ok"])
t("iznimka", "iznimka" in K["iznimka"])
t("vrsta prazna i »sve«", "vrsta_neprecizna" in K["vrsta-prazno"] and "vrsta_neprecizna" in K["vrsta-sve"])
t("zahvat nije naveden", "zahvat_nenaveden" in K["zahvat"])
t("revizija: nedostaje (uvjetno) i razlika (blokirano)", "revizija_nejasna" in K["rev-nema"] and "blokirano" in next(x for x in a["detalji"] if x["id"] == "rev-razlika")["kategorije"]["revizija_nejasna"])
t("citat: prazan, skraćen, bez vrijednosti", all("citat_nepotpun" in K[i] for i in ("cit-nema", "cit-skracen", "cit-vrijednost")))
t("brojevi po kategoriji", a["po_kategoriji"]["uvjet_nerazrijesen"]["broj"] == 1 and a["po_kategoriji"]["citat_nepotpun"]["broj"] == 3 and a["bez_nalaza"] == 2)
p = A.audit(json.load(open(R / "tools/baza/primjer_baza.json", encoding="utf-8")))
t("primjer baze: 3 pravila, sva s nejasnom revizijom, 2 skraćena citata", p["pravila"] == 3 and p["po_kategoriji"]["revizija_nejasna"]["broj"] == 3 and p["po_kategoriji"]["citat_nepotpun"]["broj"] == 2)
for x in ok: print("OK  ", x)
for x in bad: print("FAIL", x)
print(f"{len(ok)}/{len(ok) + len(bad)} testova audita prolazi"); sys.exit(1 if bad else 0)

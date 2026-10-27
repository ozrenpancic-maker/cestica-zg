#!/usr/bin/env python3
"""Sastavlja jednu HTML stranicu pilota: predložak + logika + zamrznuti podaci (+ čestice ako postoje).
    python3 pilot_pregled/sastavi.py   → pilot_pregled/dist/pregled_pravila_travicici.html
"""
import hashlib, json
from pathlib import Path

P = Path(__file__).resolve().parent
d = json.loads((P / "podaci/pilot_travicici.json").read_text(encoding="utf-8"))
c = P / "podaci/cestice_t2_5.json"            # DGU čestice, samo ako su preuzete (inače se prikazuje »Podaci nisu dostupni«)
if c.exists():
    d["geometrija"]["cestice"] = json.loads(c.read_text(encoding="utf-8"))["cestice"]
podaci = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
logika = (P / "pregled_logika.js").read_text(encoding="utf-8")
html = (P / "sucelje.template.html").read_text(encoding="utf-8").replace("__PODACI__", podaci).replace("__LOGIKA__", logika)
assert "__PODACI__" not in html and "__LOGIKA__" not in html
out = P / "dist/pregled_pravila_travicici.html"
out.parent.mkdir(exist_ok=True)
out.write_text(html, encoding="utf-8")
print(out, len(html), hashlib.sha256(out.read_bytes()).hexdigest())

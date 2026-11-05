#!/usr/bin/env python3
"""Indeks brojeva katastarskih čestica za pretragu po broju i k.o. (npr. „Punat 4381/3”), iz već pripremljenih kvadrata
data/kat_krk/<kvadrat>.json (tools/katastar/pripremi_krk.py). Ne dohvaća ništa s mreže.

  python3 tools/katastar/indeks_brojeva.py

Izlaz: data/kat_krk/brojevi/<matični broj k.o.>.json = {"v":1,"ko":"315974","kv":["5005_1124",…],"c":{"4381/3":[0],…}}
(kv: kvadrati u kojima se čestica nalazi, c: broj čestice → indeksi u kv). Aplikacija učita indeks k.o., pa samo te kvadrate."""
import glob, json, os
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "kat_krk")
I = json.load(open(os.path.join(R, "index.json"), encoding="utf-8"))
po = {}
for f in sorted(glob.glob(os.path.join(R, "*_*.json"))):
    key = os.path.basename(f)[:-5]
    for pid, broj, ko, pov, P in json.load(open(f, encoding="utf-8")):
        po.setdefault(ko, {}).setdefault(broj, set()).add(key)
out = os.path.join(R, "brojevi"); os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.json")): os.remove(f)
uk = 0
for ko, c in sorted(po.items()):
    kv = sorted({k for s in c.values() for k in s}); ix = {k: i for i, k in enumerate(kv)}
    d = {"v": 1, "ko": ko, "naziv": I["ko"].get(ko, {}).get("naziv"), "preuzeto": I.get("preuzeto"), "kv": kv,
         "c": {b: sorted(ix[k] for k in s) for b, s in sorted(c.items())}}
    json.dump(d, open(os.path.join(out, ko + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    uk += len(c)
print(f"{len(po)} k.o., {uk} brojeva čestica → {out}")

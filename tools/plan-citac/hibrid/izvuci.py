#!/usr/bin/env python3
"""Izvlači JSON generatora iz zapisa izoliranog agenta (predaja rezultata) i sprema ga s metapodacima i SHA-256.
    python3 izvuci.py ZAPIS_AGENTA.jsonl IZLAZ.json --tokena N --ms N --skup IME
"""
import argparse, hashlib, json
from pathlib import Path

a = argparse.ArgumentParser(); a.add_argument("zapis"); a.add_argument("izlaz"); a.add_argument("--tokena", type=int); a.add_argument("--ms", type=int)
a.add_argument("--skup"); x = a.parse_args()
txt, alati = None, []
for l in open(x.zapis, encoding="utf-8"):
    if not l.strip():
        continue
    e = json.loads(l)
    if e.get("type") != "assistant":
        continue
    for c in (e.get("message") or {}).get("content", []):
        if isinstance(c, dict) and c.get("type") == "tool_use":
            alati.append(c["name"])
            for v in c["input"].values():
                if isinstance(v, str) and '"kandidati"' in v:
                    txt = v
        if isinstance(c, dict) and c.get("type") == "text" and '"kandidati"' in c.get("text", ""):
            txt = c["text"]
o = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
o["metapodaci"] = {"skup": x.skup, "pozvani_alati": alati, "tokena": x.tokena, "trajanje_ms": x.ms, "generator": "izolirani agent u razvojnoj sesiji, bez alata za čitanje; samo upute generatora v1 i tekst",
                   "upute": "hibrid/UPUTE_GENERATORA_v1.md"}
Path(x.izlaz).write_text(json.dumps(o, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(o["kandidati"]), "kandidata", alati, hashlib.sha256(Path(x.izlaz).read_bytes()).hexdigest())

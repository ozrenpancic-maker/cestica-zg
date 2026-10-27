#!/usr/bin/env python3
"""Spaja izlaze generatora koji je pozvan po dijelovima teksta (pravilo podjele: cijeli članci, najviše ~8 000 znakova teksta
po pozivu) u jedan JSON. Zbraja tokene i trajanje, čuva SHA svakog dijela.
    python3 hibrid/spoji.py izlaz.json dio_A.json dio_B.json ...
"""
import hashlib, json, sys
from pathlib import Path


def main(out, dijelovi):
    K, meta = [], {"dijelovi": [], "tokena": 0, "trajanje_ms": 0, "pozvani_alati": []}
    for p in dijelovi:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        K += d["kandidati"]
        m = d.get("metapodaci") or {}
        meta["skup"] = m.get("skup", meta.get("skup"))
        meta["tokena"] += m.get("tokena") or 0
        meta["trajanje_ms"] += m.get("trajanje_ms") or 0
        meta["pozvani_alati"] += m.get("pozvani_alati") or []
        meta["dijelovi"].append({"datoteka": Path(p).name, "sha256": hashlib.sha256(Path(p).read_bytes()).hexdigest(), "kandidata": len(d["kandidati"]),
                                 "generator": d.get("generator")})
    Path(out).write_text(json.dumps({"generator": "spojeno iz dijelova", "metapodaci": meta, "kandidati": K}, ensure_ascii=False), encoding="utf-8")
    print(len(K), "kandidata", hashlib.sha256(Path(out).read_bytes()).hexdigest())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])

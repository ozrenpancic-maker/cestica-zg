#!/usr/bin/env python3
"""Provjera JSON-a s potvrđenim šiframa kartografskih listova ISPU-a (izvoz iz planovi-test.html, odjeljak 3).

python3 tools/ispu/provjeri_sifre.py izvoz.json            # provjera i sažetak
python3 tools/ispu/provjeri_sifre.py izvoz.json --uvezi    # spaja potvrđene zapise u src/ispu_sifre.json

U aplikaciju ulaze samo zapisi sa statusom "potvrđeno" koji imaju naslov, vrstu, izvor i datum provjere.
Nepotvrđeni zapisi se čuvaju u datoteci, ali se ne koriste.
"""
import json, re, sys, pathlib

VRSTE = {"namjena", "urbana_pravila", "promet", "infrastruktura", "zastita", "ostalo"}
ROOT = pathlib.Path(__file__).resolve().parents[2]
CILJ = ROOT / "src/ispu_sifre.json"


def provjeri(d):
    """Vraća (greške, upozorenja). Greška zaustavlja uvoz i izradu aplikacije."""
    g, u = [], []
    if not isinstance(d, dict) or not isinstance(d.get("zapisi"), list):
        return ["nedostaje popis 'zapisi'"], u
    vidjeno = {}
    for i, z in enumerate(d["zapisi"]):
        k = f"zapis {i + 1} ({z.get('sloj', '?')})"
        m = re.match(r"^HR_ISPU_([A-Z]+?)(\d*)_(\d+)_R(\d+)_(.+)$", str(z.get("sloj", "")), re.I)
        if not m:
            g.append(f"{k}: sloj nije u obliku HR_ISPU_<plan>_<šifra>_R<revizija>_<karta>")
            continue
        plan, rev, sifra = (m[1].upper() + m[2] + "_" + m[3]), "R" + m[4], m[5]
        if (z.get("plan"), z.get("revizija"), z.get("sifra")) != (plan, rev, sifra):
            g.append(f"{k}: plan, revizija ili šifra ne odgovaraju nazivu sloja")
        # plan odabran u pregledu mora odgovarati planu sloja (npr. list PPGZ-a ne smije se potvrditi prikazom GUP-a)
        pn, vp, tt = str(z.get("plan_naziv") or ""), m[1].upper(), str(z.get("title_u_servisu") or "")
        if z.get("status") == "potvrđeno" and pn:
            if pn.startswith("GUP") and vp != "GUP":
                g.append(f"{k}: sloj je plana {vp} ({tt.split(' - ')[0] or '?'}), a potvrđen je prikazom plana '{pn}'")
            if vp == "GUP" and not pn.startswith("GUP") and pn != "drugi plan":
                g.append(f"{k}: sloj je GUP, a potvrđen je prikazom plana '{pn}'")
            if re.match(r"^PPGZ\b", tt) and pn.startswith("GUP"):
                g.append(f"{k}: Title u servisu navodi PPGZ, a potvrđen je prikazom GUP-a")
        if z.get("status") == "potvrđeno":
            for p in ("naslov", "vrsta", "izvor", "datum_provjere"):
                if not str(z.get(p) or "").strip():
                    g.append(f"{k}: potvrđeni zapis nema '{p}'")
            if z.get("vrsta") and z["vrsta"] not in VRSTE:
                g.append(f"{k}: nepoznata vrsta '{z['vrsta']}'")
            if z.get("datum_provjere") and not re.match(r"^\d{4}-\d{2}-\d{2}$", z["datum_provjere"]):
                g.append(f"{k}: datum provjere nije GGGG-MM-DD")
            if not z.get("provjerio"):
                u.append(f"{k}: nije upisano tko je provjerio")
        elif z.get("status") != "nepotvrđeno":
            g.append(f"{k}: status mora biti 'potvrđeno' ili 'nepotvrđeno'")
        kk = z.get("sloj")
        if kk in vidjeno and vidjeno[kk] != (z.get("naslov"), z.get("vrsta")) and z.get("status") == "potvrđeno":
            g.append(f"{k}: isti sloj potvrđen dvaput s različitim naslovom ili vrstom")
        if z.get("status") == "potvrđeno":
            vidjeno[kk] = (z.get("naslov"), z.get("vrsta"))
    return g, u


def spoji(stari, novi):
    """Potvrđeni zapisi iz novog izvoza zamjenjuju iste slojeve; nepotvrđeni ne brišu potvrđene."""
    po = {z["sloj"]: z for z in (stari or {}).get("zapisi", [])}
    for z in novi["zapisi"]:
        if z.get("status") == "potvrđeno" or z["sloj"] not in po or po[z["sloj"]].get("status") != "potvrđeno":
            po[z["sloj"]] = z
    return {"verzija_sheme": "1.0", "vrsta": "ISPU šifre kartografskih prikaza", "zapisi": sorted(po.values(), key=lambda z: z["sloj"])}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    d = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    g, u = provjeri(d)
    for x in u: print("upozorenje:", x)
    for x in g: print("GREŠKA:", x)
    z = d.get("zapisi", []) if isinstance(d, dict) else []
    print(f"zapisa: {len(z)}, potvrđeno: {sum(1 for x in z if x.get('status') == 'potvrđeno')}")
    if g: sys.exit(1)
    if "--uvezi" in sys.argv:
        stari = json.loads(CILJ.read_text(encoding="utf-8")) if CILJ.exists() else None
        CILJ.write_text(json.dumps(spoji(stari, d), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("spremljeno u", CILJ.relative_to(ROOT))

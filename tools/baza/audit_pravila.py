#!/usr/bin/env python3
"""Audit baze urbanističkih pravila PRIJE uvoza (Plan Integrity v10).

Za svako pravilo utvrđuje zašto bi ga aplikacija (dbMatch / dbConditions / dbPublicationGate) blokirala
ili prikazala samo uvjetno, i razvrstava ga u kategorije:
  uvjet_nerazrijesen   – slobodni tekst `uvjet` bez `status_uvjeta: "razriješeno"`          → ne ulazi u izračun (v6)
  iznimka              – `iznimka` / `iznimke` (bez `status_iznimke: "razriješeno"` blokira) → ne ulazi u izračun (v6)
  vrsta_neprecizna     – `vrste_gradnje` prazno (pravno nepotpuno) ili samo »sve« / »*«       → prazno: kandidat; »sve«: računa se, ali opseg treba potvrditi
  zahvat_nenaveden     – `primjenjivost.zahvat` nije naveden                                  → računa se za svaki zahvat; treba potvrditi da pravilo ne vrijedi samo za novu gradnju
  revizija_nejasna     – nema `izvor_revizija`/`revizija_plana` ili plan nema `primjenjiva_revizija` → uvjetno (v5); različite oznake → blokirano
  citat_nepotpun       – nema citata, citat je sažetak (… / ... / zagrade s dopunom) ili ne sadrži vrijednost → kandidat ili ručni pregled

Korištenje:
  python3 tools/baza/audit_pravila.py baza.json [--json izlaz.json]
  python3 tools/baza/audit_pravila.py --pilot pravila_upu2_pripremljena.json   # pretvori pilot-pravila u shemu baze pa auditiraj
Ništa ne mijenja i ništa ne uvozi.
"""
import argparse, json, re, sys
from collections import Counter, defaultdict

KAT = {
    "uvjet_nerazrijesen": "pravila s nerazriješenim uvjetima",
    "iznimka": "pravila s iznimkama",
    "vrsta_neprecizna": "pravila bez precizne vrste građevine",
    "zahvat_nenaveden": "pravila bez vrste zahvata",
    "revizija_nejasna": "pravila s nejasnom revizijom",
    "citat_nepotpun": "pravila s nepotpunim ili neodgovarajućim citatom",
}
WILD = {"sve", "*"}


def norm(s): return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def vrijednosti_u_citatu(r):
    v = r.get("vrijednost"); c = norm(r.get("citat"))
    vals = [v] if isinstance(v, (int, float)) else []
    if isinstance(v, str) and re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", v.strip()): vals = [float(v.replace(",", "."))]
    if not vals: return None  # složena vrijednost: ne provjerava se strojno
    out = []
    for x in vals:
        t = (f"{x:g}").replace(".", ",")
        out.append(t in c or (f"{int(x*100)}%" in c.replace(" ", "") if isinstance(x, float) and x < 1 else False))
    return all(out)


def audit(b):
    planovi = {p["id"]: p for p in b.get("planovi", [])}
    rows = []
    for r in b.get("pravila", []):
        p = planovi.get(r.get("plan_id"), {}); pr = r.get("primjenjivost") or {}; k = {}
        if r.get("uvjet") and r.get("status_uvjeta") != "razriješeno":
            k["uvjet_nerazrijesen"] = "blokirano: tekstualni uvjet »" + str(r["uvjet"])[:90] + "« nije razriješen"
        if r.get("iznimka") or r.get("iznimke"):
            k["iznimka"] = ("blokirano: iznimka nije razriješena" if r.get("status_iznimke") != "razriješeno" else "iznimka označena kao razriješena (provjeriti tko i kada)")
        v = [norm(x) for x in pr.get("vrste_gradnje") or []]
        if not v: k["vrsta_neprecizna"] = "kandidat: vrste_gradnje nisu navedene (dbRuleLegal: nedostaje »vrste gradnje«)"
        elif all(x in WILD for x in v): k["vrsta_neprecizna"] = "računa se za sve vrste (»sve«); opseg treba stručno potvrditi"
        if not pr.get("zahvat"): k["zahvat_nenaveden"] = "zahvat nije naveden: pravilo bi vrijedilo i za rekonstrukciju i dogradnju; potvrditi"
        rr = (r.get("izvor_revizija") or r.get("revizija_plana") or "").strip(); pp = (p.get("primjenjiva_revizija") or "").strip()
        if rr and pp and rr != pp: k["revizija_nejasna"] = f"blokirano: revizija pravila »{rr}« ≠ plana »{pp}«"
        elif not rr or not pp: k["revizija_nejasna"] = "uvjetno: revizija " + ("pravila" if not rr else "") + (" i " if not rr and not pp else "") + ("plana" if not pp else "") + " nije dokumentirana"
        c = str(r.get("citat") or "").strip(); vc = vrijednosti_u_citatu(r)
        if not c: k["citat_nepotpun"] = "kandidat: nema citata"
        elif "…" in c or "..." in c: k["citat_nepotpun"] = "citat je skraćen (…), nije doslovni navod"
        elif re.search(r"\([^)]*\d[^)]*\)\s*$", c) and not re.search(r"(alineje|točke|članka|stavka)", c[-40:]): k["citat_nepotpun"] = "citat završava dopunom u zagradi (sažetak, ne doslovni navod)"
        elif len(c) < 20: k["citat_nepotpun"] = "citat prekratak za provjeru"
        elif vc is False: k["citat_nepotpun"] = "vrijednost pravila ne nalazi se u citatu"
        rows.append({"id": r.get("id"), "plan": r.get("plan_id"), "clanak": r.get("clanak"), "parametar": r.get("parametar"),
                     "vrijednost": r.get("vrijednost"), "pravni_status": (r.get("pravni_status") or {}).get("razina"), "kategorije": k})
    po = defaultdict(list)
    for x in rows:
        for kk in x["kategorije"]: po[kk].append(x)
    return {"pravila": len(rows), "bez_nalaza": sum(1 for x in rows if not x["kategorije"]),
            "po_kategoriji": {kk: {"naziv": KAT[kk], "broj": len(po[kk]), "primjeri": [{"id": x["id"], "clanak": x["clanak"], "parametar": x["parametar"], "razlog": x["kategorije"][kk]} for x in po[kk][:3]]} for kk in KAT},
            "detalji": rows}


# pretvorba pravila GIS-first pilota (tools/gis-pilot/pravila_upu2_pripremljena.json, grana pilot-gis-krk) u shemu baze
PAR = {"min_povrsina_cestice": "min_cestica", "kig_max": "kig", "kis_max": "kis", "tlocrt_min": "tlocrt_min", "tlocrt_max": "tlocrt_max", "gbp_max_cestica": "gbp_max",
       "visina_max": "visina", "etaze_max": "etaze", "udaljenost_meda": "udaljenost_meda", "udaljenost_regulacija_javna_cesta": "udaljenost_regulacija",
       "udaljenost_regulacija_nerazvrstana": "udaljenost_regulacija", "zelenilo_min_udio": "zelenilo", "parkiralista_po_stanu": "parkiranje", "nadzemne_etaze_max_zona_C": "etaze"}
VRSTA = {"obit": "obiteljska kuća", "visobit": "višeobiteljska kuća", "stamb": "stambena građevina"}
NACIN = {"slob": "slobodnostojeća", "dvoj": "dvojna", "ugr": "ugrađena"}


def iz_pilota(P):
    plan = {"id": "UPU2-KORNIC", "naziv": P["plan"]["naziv"], "vrsta": "UPU", "status_vazenja": "važeći", "obuhvat": {"jls": ["Grad Krk"], "gis": {"status": "kandidat"}},
            "odluke": [{"id": "SN-19-2016", "naziv": P["plan"]["naziv"], "vrsta": "donošenje", "glasilo": P["plan"]["glasilo"], "url": P["plan"]["izvor_html"]}]}
    out = []
    for r in P["pravila"]:
        if r["parametar"] not in PAR: continue
        tipovi = r["vrijedi_za"].get("tip", []); v = r["vrijednost"]
        for t in tipovi:
            val = v.get(t) if isinstance(v, dict) and t in v else (v if not isinstance(v, dict) else None)
            if isinstance(v, dict) and val is None: val = v  # npr. tlocrt po načinu gradnje: ostaje složena vrijednost
            x = {"id": f"{r['id']}-{t}", "plan_id": plan["id"], "odluka_id": "SN-19-2016", "parametar": PAR[r["parametar"]], "vrijednost": val, "jedinica": r.get("jedinica") or "",
                 "clanak": str(r["clanak"]) + ((" " + r["tocka"] + ")") if r.get("tocka") else ""), "citat": r["citat"],
                 "primjenjivost": {"zone": ["M11", "M2"], "vrste_gradnje": [VRSTA.get(t, t)], "nacin_gradnje": [NACIN[o] for o in r["vrijedi_za"].get("oblik", [])]},
                 "pravni_status": {"razina": "kandidat"}, "gis_status": {"razina": "kandidat"}}
            if r["vrijedi_za"].get("zona_zastite"): x["primjenjivost"]["posebni_rezim"] = [r["vrijedi_za"]["zona_zastite"]]
            if r.get("iznimka"): x["iznimke"] = [f"{r['iznimka']['vrijednost']}: {r['iznimka']['uvjet']}"]
            out.append(x)
    return {"verzija_sheme": "1.0", "izvor": "GIS-first pilot (pretvoreno za audit)", "izvezeno": "2026-10-27", "planovi": [plan], "pravila": out}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("baza", nargs="?"); ap.add_argument("--pilot"); ap.add_argument("--json")
    a = ap.parse_args()
    b = iz_pilota(json.load(open(a.pilot, encoding="utf-8"))) if a.pilot else json.load(open(a.baza, encoding="utf-8"))
    R = audit(b)
    print(f"pravila: {R['pravila']} · bez nalaza: {R['bez_nalaza']}")
    for kk, v in R["po_kategoriji"].items():
        print(f"  {v['naziv']}: {v['broj']}")
        for e in v["primjeri"]: print(f"     – {e['id']} (čl. {e['clanak']}, {e['parametar']}): {e['razlog']}")
    if a.json: json.dump(R, open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return R


if __name__ == "__main__":
    main()

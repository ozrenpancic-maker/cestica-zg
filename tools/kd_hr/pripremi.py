#!/usr/bin/env python3
"""Komunalni doprinos za JLS izvan Zagreba i Grada Krka iz korisnikove tablice (data/kd_hr/izvor_tablica_v3.json).

Pravilo iz tablice: iznos se računa samo iz redaka sa statusom POTVRĐENA_TARIFA. Ostali reci ostaju kao popis izvora
("Podaci nisu dostupni"). Zagreb i Krk imaju vlastite obračune u aplikaciji i ovdje se preskaču.
Provjera u aplikaciji (6. 11. 2026., čitanje službenih PDF-ova):
  * Zaprešić: iznosi 18 / 15 / 10 €/m³ i pravilo 75 % do 700 m³ odgovaraju SN Grada Zaprešića 8/2025 (čl. 5. i 7.).
  * Bjelovar: tablica ima iznose iz ranijih odluka (9/22, 7/23, 7/24); nova Odluka o komunalnom doprinosu (sjednica
    25. 11. 2025., primjena od 1. 1. 2026., čl. 9.) propisuje 10 / 7 / 6 / 4 €/m³ i ukida te odluke. Koriste se novi iznosi.
  * Split, Dubrovnik, Rakovec: izvor nije bilo moguće otvoriti; iznosi su iz tablice, neprovjereni u aplikaciji.
Rezultat: src/kd_hr.json (ugrađuje ga build.py).
"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[2]
T = json.loads((root / "data/kd_hr/izvor_tablica_v3.json").read_text(encoding="utf-8"))
PRESKOCI = {"Zagreb", "Krk"}
BJ_URL = "https://www.bjelovar.hr/wp-content/uploads/2025/12/28.-Odluka-o-komunalnom-doprinosu.pdf"
ISPRAVCI = {
  "Bjelovar": {"zone": [["I. zona", 10.0], ["II. zona", 7.0], ["III. zona", 6.0], ["IV. zona", 4.0]],
               "akt": "Odluka o komunalnom doprinosu Grada Bjelovara (Gradsko vijeće, 25. 11. 2025.), čl. 9.; primjenjuje se od 1. 1. 2026.",
               "url": BJ_URL, "provjera": "provjereno u službenom PDF-u odluke (6. 11. 2026.)",
               "nap": "Tablica je imala iznose iz ranijih odluka (6,64 / 3,98 / 3,32 / 2,65 €/m³), koje je nova odluka ukinula. Za jednokratno plaćanje umanjenje 10 % (čl. 14.)."},
  "Zaprešić": {"akt": "Službene novine Grada Zaprešića 8/2025, čl. 5. (iznosi po zonama) i čl. 7. (75 % do 700 m³)",
               "provjera": "provjereno u Službenim novinama Grada Zaprešića 8/2025 (6. 11. 2026.)"},
}
out = {}
for r in T["data"]:
    j = r["JLS"]
    if j in PRESKOCI: continue
    e = out.setdefault(j, {"jls": j, "zup": r["Županija"], "zone": [], "status": set(), "akt": "", "url": "", "dat": "", "nap": [], "prim": ""})
    e["status"].add(r["Status"])
    if r["Službeni_akt"] and not e["akt"]: e["akt"] = r["Službeni_akt"]
    if r["URL_izvora"] and (not e["url"] or r["Status"] == "POTVRĐENA_TARIFA"): e["url"] = r["URL_izvora"]
    if r["Status"] == "POTVRĐENA_TARIFA":
        e["akt"] = r["Službeni_akt"]; e["url"] = r["URL_izvora"]
    e["dat"] = r["Datum_provjere"]
    if r["Napomena"] and r["Napomena"] not in e["nap"] and r["Status"] != "ZAMIJENJEN_RETkom_TARIFE_V3": e["nap"].append(r["Napomena"])
    if r["Primjenjivost"] and r["Status"] == "POTVRĐENA_TARIFA": e["prim"] = r["Primjenjivost"]
    if r["Status"] == "POTVRĐENA_TARIFA" and r["Iznos_EUR_m3"]:
        e["zone"].append([r["Zona"], float(r["Iznos_EUR_m3"])])
    elif r["Iznos_EUR_m3"] or r["Primjenjivost"]:
        e.setdefault("info", []).append({"zona": r["Zona"], "iznos": float(r["Iznos_EUR_m3"]) if r["Iznos_EUR_m3"] else None, "prim": r["Primjenjivost"], "status": r["Status"]})
pravila = {}
for p in T["special_rules"]:
    if p["city"] in PRESKOCI: continue
    pravila.setdefault(p["city"], []).append({"zona": p["zone"], "vrsta": p["type"], "v": p["value"], "uvjet": p["condition"], "akt": p["act"], "url": p["source"]})
for j, e in out.items():
    e["status"] = "POTVRĐENA_TARIFA" if e["zone"] else sorted(e["status"])[0]
    if j in ISPRAVCI: e.update({k: v for k, v in ISPRAVCI[j].items() if k != "nap"}); e["nap"] = [ISPRAVCI[j]["nap"]] if "nap" in ISPRAVCI[j] else e["nap"]
    e.setdefault("provjera", "iznos iz korisnikove tablice; službeni izvor nije otvoren u aplikaciji" if e["zone"] else None)
    e["pravila"] = pravila.get(j, [])
    e["nap"] = " ".join(e["nap"])
res = {"izvor": "ČesticaHR – Komunalni doprinosi, svi gradovi HR, verzija 3 (tablica korisnika, provjera 28. 10. 2026.)", "upozorenje": T["warning"],
       "jls": sorted(out.values(), key=lambda e: e["jls"])}
(root / "src/kd_hr.json").write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(len(res["jls"]), "JLS,", sum(1 for e in res["jls"] if e["zone"]), "s iznosima:", [e["jls"] for e in res["jls"] if e["zone"]])

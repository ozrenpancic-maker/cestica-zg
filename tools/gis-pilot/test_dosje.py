#!/usr/bin/env python3
"""Testovi GIS-first pilota:  python3 tools/gis-pilot/test_dosje.py"""
import copy, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dosje as M

ok, bad = [], []
def t(ime, uvjet): (ok if uvjet else bad).append(ime)

izv, greske = M.izvori()
t("sve kontrolne sume izvora odgovaraju", not greske and all(r["sha_odgovara"] in (True, None) for r in izv))
ces, poly = M.cestica()
t("čestica iz lokalnog katastra = izvorni GeoJSON DGU-a (< 1e-6°)", ces["odstupanje_lokalno_vs_izvor_stupnjeva"] < 1e-6)
t("površina čestice: grafička 405 m², iz koordinata ≈ 405", ces["povrsina_graficka_dgu_m2"] == 405.0 and abs(ces["povrsina_iz_koordinata_m2"] - 405.4) < 1)
pl, ob = M.planovi(poly)
t("čestica je unutar vektorskog obuhvata UPU-a 2", pl["upu2"]["cestica_unutar"] is True)
t("UPU 2 je jedini važeći detaljni plan na točki", [u["IDPLAN"] for u in pl["vazeci_detaljni"]] == [618])
t("evidencija se od 22. 10. nije bitno promijenila", pl["promjene_od_22_10"] == [])
zp = M.zone_ppug(poly)
t("PPUG zona NA2 pokriva > 99 % čestice", zp["zone"][0]["oznaka"] == "NA2" and zp["zone"][0]["udio"] > 0.99)
cl = M.tekst_clanaka()
t("tekst ima čl. 1.–108. bez rupa", sorted(cl) == list(range(1, 109)))
D, teh = M.provjeri_pravila(cl)
t("svi citati pripremljenih pravila nađeni doslovno u svom članku", all(x["tehnicki"] == "PROVJERENO" for x in teh))
D2 = copy.deepcopy(D); D2["pravila"][4]["citat"] = D2["pravila"][4]["citat"].replace("500", "600")
cl2 = cl
# izmijenjen citat mora pasti (provjera ne smije biti prazna formalnost)
def provjeri(Dx):
    import re
    out = []
    for p in Dx["pravila"]:
        out.append(cl2.get(p["clanak"], "").count(M.norm(p["citat"])) >= 1)
    return out
t("izmijenjen citat se ne nalazi u tekstu", provjeri(D2)[4] is False)
usp = M.usporedi_s_aplikacijom(D)
t("vrijednosti se podudaraju s postojećim src/rules_krk.json (UPU 2)", usp and all(x["isto"] for x in usp))
kand = M.kandidati_zona()

# bez stručnih potvrda: ništa nije »izračunato«, sve je uvjetno ili blokirano
pok = M.pokazatelji(ces, D, teh, kand, [])
t("bez potvrda nijedan pokazatelj gradnje nije IZRACUNATO", not any(p["stanje"] == "IZRACUNATO" for p in pok))
t("pravna valjanost je uvijek NIJE_UTVRDENA", all(p["pravna_valjanost"] == "NIJE_UTVRDENA" for p in pok))
t("svaki pokazatelj ima lanac čestica → zona → plan → članak → pravilo",
  all({"čestica", "plan", "članak", "pravilo"} <= {k["karika"] for k in p["lanac"]} for p in pok))
t("krov i regulacija se ne računaju (sukob / nedostaje podatak)", {p["id"]: p["stanje"] for p in pok}["krov"] == "NIJE_IZRACUNATO" and {p["id"]: p["stanje"] for p in pok}["regulacija"] == "NIJE_IZRACUNATO")
P = {p["id"]: p for p in pok}
t("405 m²: obiteljska slobodnostojeća samo iznimno, višeobiteljska slob. i stambena ne, dvojne da",
  P["min_cestica:obit:slob"]["rezultat"].startswith("samo iznimno") and P["min_cestica:visobit:slob"]["rezultat"] == "nije ispunjeno"
  and P["min_cestica:stamb:slob"]["rezultat"] == "nije ispunjeno" and P["min_cestica:obit:dvoj"]["rezultat"] == "ispunjeno" and P["min_cestica:visobit:dvoj"]["rezultat"] == "ispunjeno")
t("tlocrt: min(0,25 × 405, 200) = 101,2; ugrađena 100", P["tlocrt_max:obit:slob"]["vrijednost_m2"] == 101.2 and P["tlocrt_max:obit:ugr"]["vrijednost_m2"] == 100)
t("GBP: obiteljska 200, dvojna višeobiteljska 303,8", P["gbp_max:obit:slob"]["vrijednost_m2"] == 200 and P["gbp_max:visobit:dvoj"]["vrijednost_m2"] == 303.8)
t("nema tlocrta za tipove kojima čestica nije dovoljna", "tlocrt_max:visobit:slob" not in P and "tlocrt_max:stamb:slob" not in P)

# sa stručnim potvrdama zone, zaštite i svih pravila: izračunato, osim iznimke, sukoba i nedostajućeg podatka
sve = [{"predmet": "zona_upu", "vrijednost": "M11"}, {"predmet": "zona_zastite", "vrijednost": "C"}] + [{"predmet": "pravilo:" + p["id"], "vrijednost": "potvrđeno"} for p in D["pravila"]]
P2 = {p["id"]: p for p in M.pokazatelji(ces, D, teh, kand, sve)}
t("uz potvrde: dvojna obiteljska IZRACUNATO", P2["min_cestica:obit:dvoj"]["stanje"] == "IZRACUNATO" and P2["tlocrt_max:obit:dvoj"]["stanje"] == "IZRACUNATO")
t("uz potvrde: iznimka 400 m² i dalje UVJETNO (uvjet okruženja)", P2["min_cestica:obit:slob"]["stanje"] == "UVJETNO")
t("uz potvrde: krov (sukob) i regulacija (nema podatka) i dalje NIJE_IZRACUNATO", P2["krov"]["stanje"] == "NIJE_IZRACUNATO" and P2["regulacija"]["stanje"] == "NIJE_IZRACUNATO")
t("uz potvrde: pravna valjanost i dalje NIJE_UTVRDENA", all(p["pravna_valjanost"] == "NIJE_UTVRDENA" for p in P2.values()))
# samo zona bez potvrde pravila: ostaje uvjetno (potvrda zone ne potvrđuje pravila)
P3 = {p["id"]: p for p in M.pokazatelji(ces, D, teh, kand, sve[:2])}
t("potvrda zone ne potvrđuje pravila", P3["tlocrt_max:obit:dvoj"]["stanje"] == "UVJETNO")
# druga zona / zona B blokira
P4 = {p["id"]: p for p in M.pokazatelji(ces, D, teh, kand, [{"predmet": "zona_upu", "vrijednost": "D2"}])}
t("potvrđena zona D2: nema pokazatelja gradnje kuća", all(p["stanje"] == "NIJE_IZRACUNATO" for k, p in P4.items() if k.startswith(("min_cestica", "tlocrt", "gbp"))))
P5 = {p["id"]: p for p in M.pokazatelji(ces, D, teh, kand, [{"predmet": "zona_zastite", "vrijednost": "B"}])}
t("zona zaštite B: nema izračuna", P5["tlocrt_max:obit:dvoj"]["stanje"] == "NIJE_IZRACUNATO")
P6 = {p["id"]: p for p in M.pokazatelji(ces, D, teh, kand, sve[:1] + [{"predmet": "zona_zastite", "vrijednost": "izvan"}] + sve[2:])}
t("izvan zone C: krov 17°–23° izračunat, nema konzervatorskog pokazatelja", P6["krov"]["stanje"] == "IZRACUNATO" and "konzervatorski" not in P6)
t("potvrde.json u repozitoriju je prazan (razvoj ništa ne potvrđuje)", M.jl(M.P / "potvrde.json")["potvrde"] == [])

for x in ok: print("OK  ", x)
for x in bad: print("FAIL", x)
print(f"{len(ok)}/{len(ok) + len(bad)}"); sys.exit(1 if bad else 0)

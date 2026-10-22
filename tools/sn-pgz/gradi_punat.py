#!/usr/bin/env python3
"""Nadopunjuje data/pravila-sn/punat-upu3.json pravilima iz osnovnog teksta izmjena 2016. (SN 13/16)
i provjerava svaki doslovni citat u tekstu odluke.
Upotreba: gradi_punat.py TEKST_2016.txt TEKST_2020.txt   (tekstovi se NE spremaju u repozitorij)"""
import json, sys, os, re, hashlib, copy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
import verzije as V

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
BAZA = os.path.join(ROOT, "data", "pravila-sn", "punat-upu3.json")
SHEMA = os.path.join(ROOT, "tools", "sn-pgz", "shema.json")
URL = "https://www.sn.pgz.hr/default.asp?Link=odluke&id=%d"
VER16 = "Ciljane izmjene UPU 3 (SN PGŽ 13/2016)"
NAP16 = ("Tekst odluke preuzet iz izvoza treće strane (ChatGPT program), nije dohvaćen našom skriptom; "
         "citat je pronađen u tom tekstu, ali tekst nije uspoređen sa sn.pgz.hr. Datum stupanja na snagu nije u izvozu.")
# (id, parametar, vrijednost, jedinica, vrsta_gradnje, uvjet, clanak_plana, tocka, citat)
P = []
def a(*x): P.append(x)
IZG = {"dio_naselja": "izgradeni"}; NEIZG = {"dio_naselja": "neizgradeni"}
ZADNJA = {"gradevina": "zadnja_u_nizu"}
# ---- čl. 46a slobodnostojeća
a("p3-46a-cestica-min", "cestica_min", 450, "m2", "slobodnostojeca", None, "46a", "1", "Najmanja površina građevne čestice iznosi 450m 2")
a("p3-46a-interp-10", "manja_cestica_interpolacija", 10, "%", "slobodnostojeca", {"samo": "izgradeni dijelovi naselja, parcele sa svih strana okružene izgrađenim građevinama"}, "46a", "1", "Iznimno je moguće planirati interpolacije i na građevnim česticama 10% manjim od propisane")
a("p3-46a-kig", "kig_max", 0.25, "", "slobodnostojeca", None, "46a", "2", "je 0,25, a maksimalni koeficijent iskoristivosti građevinske čestice (k is ) je u:")
a("p3-46a-kis-izg", "kis_max", 1.0, "", "slobodnostojeca", IZG, "46a", "2", "izgrađenom dijelu građevinskog područja naselja 1,0")
a("p3-46a-kis-neizg", "kis_max", 0.85, "", "slobodnostojeca", NEIZG, "46a", "2", "neizgrađenom dijelu građevinskog područja naselja 0,85")
a("p3-46a-stanovi", "stanovi_max", 3, "", "slobodnostojeca", {"napomena": "ili 2 stana i poslovni prostor"}, "46a", "2", "Slobodnostojeća obiteljska kuća ima najviše tri stana")
a("p3-46a-etaze", "etaze_nadzemne_max", 3, "", "slobodnostojeca", None, "46a", "2", "i tri nadzemne etaže")
a("p3-46a-visina-izg", "visina_max", 9.0, "m", "slobodnostojeca", IZG, "46a", "2", "iznosi maksimalno 9,0 m")
a("p3-46a-visina-neizg", "visina_max", 7.0, "m", "slobodnostojeca", NEIZG, "46a", "2", "iznosi najviše 7,00 m")
a("p3-46a-odmak-meda", "odmak_meda_min", 3, "m", "slobodnostojeca", {"napomena": "pola vlastite visine, ali ne manje od 3 m; sa svih strana"}, "46a", "3", "pola vlastite visine, ali ne manje od 3m, od granice građevne čestice")
a("p3-46a-odmak-gradevine", "odmak_gradevine_min", 6, "m", "slobodnostojeca", None, "46a", "3", "a najmanje 6m od susjednih građevina")
a("p3-46a-poslovni-S1", "poslovni_udio_max", 10, "% GBP", "slobodnostojeca", {"zona": "S1"}, "46a", "2", "čija površina ne smije prelaziti 10% ukupne razvijene površine (GBP) stambene građevine")
# ---- čl. 46b dvojna
a("p3-46b-cestica-min", "cestica_min", 225, "m2", "dvojna", None, "46b", "1", "Najmanja površina građevne čestice iznosi 225m 2")
a("p3-46b-kig", "kig_max", 0.3, "", "dvojna", None, "46b", "2", "(kig) je 0,3, a maksimalni koeficijent iskoristivosti građevinske čestice (kis) je u:")
a("p3-46b-kis-izg", "kis_max", 1.3, "", "dvojna", IZG, "46b", "2", "izgrađenom dijelu građevinskog područja naselja 1,3")
a("p3-46b-kis-neizg", "kis_max", 1.05, "", "dvojna", NEIZG, "46b", "2", "neizgrađenom dijelu građevinskog područja naselja 1,05")
a("p3-46b-etaze", "etaze_nadzemne_max", 3, "", "dvojna", {"napomena": "P+2; treća može biti potkrovna, nadozid najviše 1,2 m"}, "46b", "2", "Dvojna obiteljska kuća ima najviše tri nadzemne etaže, prizemlje i dva kata")
a("p3-46b-visina-izg", "visina_max", 9.0, "m", "dvojna", IZG, "46b", "2", "iznosi maksimalno 9,0 m")
a("p3-46b-visina-neizg", "visina_max", 7.0, "m", "dvojna", NEIZG, "46b", "2", "iznosi najviše 7,00 m")
a("p3-46b-stanovi", "stanovi_max", 1, "po jedinici", "dvojna", None, "46b", "2", "Svaka jedinica dvojne obiteljske kuće može imati najviše jednu (višeetažnu) stambenu jedinicu")
a("p3-46b-odmak-meda", "odmak_meda_min", 3, "m", "dvojna", {"napomena": "pola vlastite visine, ali ne manje od 3 m; sa svih strana osim uz prometnicu/javnu površinu"}, "46b", "3", "pola vlastite visine, ali ne manje od 3m, od granice građevne čestice")
a("p3-46b-odmak-gradevine", "odmak_gradevine_min", 6, "m", "dvojna", None, "46b", "3", "a najmanje 6 m od susjednih građevina")
# ---- čl. 46c niz
a("p3-46c-cestica-min", "cestica_min", 150, "m2", "niz", None, "46c", "1", "Najmanja površina građevne čestice iznosi 150 (225 za zadnju građevinu niza) m 2")
a("p3-46c-cestica-min-zadnja", "cestica_min", 225, "m2", "niz", ZADNJA, "46c", "1", "Najmanja površina građevne čestice iznosi 150 (225 za zadnju građevinu niza) m 2")
a("p3-46c-kig", "kig_max", 0.4, "", "niz", None, "46c", "2", "(kig) je 0,4 (0,3 za zadnju građevinu u nizu)")
a("p3-46c-kig-zadnja", "kig_max", 0.3, "", "niz", ZADNJA, "46c", "2", "(kig) je 0,4 (0,3 za zadnju građevinu u nizu)")
a("p3-46c-kis-izg", "kis_max", 1.8, "", "niz", IZG, "46c", "2", "izgrađenom dijelu građevinskog područja naselja 1,8 (1,3 za zadnju")
a("p3-46c-kis-izg-zadnja", "kis_max", 1.3, "", "niz", dict(IZG, **ZADNJA), "46c", "2", "izgrađenom dijelu građevinskog područja naselja 1,8 (1,3 za zadnju")
a("p3-46c-kis-neizg", "kis_max", 1.4, "", "niz", NEIZG, "46c", "2", "neizgrađenom dijelu građevinskog područja naselja 1,4 (1,05 za zadnju")
a("p3-46c-kis-neizg-zadnja", "kis_max", 1.05, "", "niz", dict(NEIZG, **ZADNJA), "46c", "2", "neizgrađenom dijelu građevinskog područja naselja 1,4 (1,05 za zadnju")
a("p3-46c-visina-izg", "visina_max", 9.0, "m", "niz", IZG, "46c", "2", "iznosi maksimalno 9,0 m")
a("p3-46c-visina-neizg", "visina_max", 7.0, "m", "niz", NEIZG, "46c", "2", "iznosi najviše 7,00 m")
a("p3-46c-niz-max", "niz_jedinica_max", 5, "", "niz", NEIZG, "46c", "2", "u neizgrađenom dijelu građevinskog područja pet (5) jedinica")
a("p3-46c-odmak-meda", "odmak_meda_min", 3, "m", "niz", {"napomena": "pola vlastite visine, ali ne manje od 3 m; sa svih strana osim uz prometnicu/javnu površinu"}, "46c", "3", "pola vlastite visine, ali ne manje od 3m, od granice građevne čestice")
a("p3-46c-odmak-gradevine", "odmak_gradevine_min", 6, "m", "niz", None, "46c", "3", "a najmanje 6 m od susjednih građevina")
# ---- čl. 50a višestambena (točke 1 i 3 nisu mijenjane 2020.; točka 2 jest, pa su kig/kis/etaže/visina u bazi iz 2020.)
a("p3-50a-cestica-min", "cestica_min", 650, "m2", "visestambena", None, "50a", "1", "Najmanja površina građevne čestice na kojoj se izvode višestambene građevine iznosi 650m 2")
a("p3-50a-odmak-meda", "odmak_meda_min", 4, "m", "visestambena", {"napomena": "pola vlastite visine, ali ne manje od 4 m"}, "50a", "3", "pola vlastite visine, ali ne manje od 4 m, od granice građevne čestice")
a("p3-50a-odmak-gradevine", "odmak_gradevine_min", 6, "m", "visestambena", None, "50a", "3", "a najmanje 6 m od susjednih građevina")

def blokovi_clanka(tekst, clanak):
    return " ".join(S.norm(b["tekst"]) for b in V.blokovi(tekst) if b["clanak"] == clanak and b["vrsta"] in ("novi", "zamjena", "zamjena_ili_novi"))

def main(t16, t20):
    d = json.load(open(BAZA, encoding="utf-8"))
    sh = S.norm(t16)
    # odluke: 2010. i 2016. imaju sada tekst (iz izvoza)
    for o in d["odluke"]:
        if o.get("id") == 20518:
            o.update(dohvaceno="izvoz_treceg", napomena="Tekst iz izvoza treće strane (nije uspoređen sa sn.pgz.hr). Članci 46a–46c i 50a uvedeni su tek izmjenama 2016.")
        if o.get("vrsta") == "izmjene" and o.get("glasilo", {}).get("broj") == 13:
            o.update(id=33933, url=URL % 33933, status="ciljane izmjene UPU 3; uvode čl. 46a–46c, 50a–50e, 54c–54e, 85a–85d, 99a–99e",
                     dohvaceno="izvoz_treceg", sha256=hashlib.sha256(re.sub(r"\s+", " ", sh).encode()).hexdigest(),
                     napomena="Prethodni zaključak da ID 33933 ne radi bio je ograničenje alata za čitanje; ID je ispravan. " + NAP16)
    novi = {r["id"]: r for r in d["pravila"]}
    lose = []
    for (rid, par, vr, jed, vg, uv, cl, toc, cit) in P:
        blok = blokovi_clanka(t16, cl)
        if S.norm(cit) not in blok: lose.append((rid, "citat nije u bloku čl. %s iz 2016." % cl))
        novi[rid] = {"id": rid, "zona": {"oznaka": "S1|S2|M1" if cl.startswith("46") else None, "potvrda": "nepotvrdeno"},
            "parametar": par, "vrijednost": vr, "jedinica": jed, "vrsta_gradnje": vg, "uvjet": uv,
            "izvor": {"odluka_id": 33933, "clanak_odluke": None, "clanak_plana": cl, "stavak": "1", "tocka": toc, "citat": cit, "url": URL % 33933},
            "vazi_od": None, "verzija": VER16, "status_primjene": "ne_primjenjivati_automatski",
            "provjera": {"razina": "strojno_i_citat_pronaden_u_tekstu", "datum": "2026-10-21",
                "napomena": "Točka %s čl. %s nije mijenjana u II. izmjenama 2020. (čl. 46a: mijenjaju se točke 4, 6, 8; čl. 46b: točke 4, 6 i alineja 3 točke 8; čl. 46c: točke 4 i 6). Dio naselja (izgrađeni/neizgrađeni) određuje plan, ne ova baza. Ime zone: članak se odnosi na namjene S1, S2 i M1 (naslov čl. 46)." % (toc, cl) if cl.startswith("46") else "Točka %s čl. %s nije mijenjana u II. izmjenama 2020. za ovaj parametar. %s" % (toc, cl, NAP16)}}
    # vrsta gradnje za zelenilo 46a/b/c iz 2020. sada je poznata
    for rid, vg in (("p3-46a-zelenilo", "slobodnostojeca"), ("p3-46b-zelenilo", "dvojna"), ("p3-46c-zelenilo", "niz"), ("p3-46a-bazen", "slobodnostojeca"), ("p3-46a-interpolacija", "slobodnostojeca"), ("p3-46a-izn-3307-tl", "slobodnostojeca")):
        if rid in novi:
            novi[rid]["vrsta_gradnje"] = vg
            novi[rid]["provjera"]["napomena"] = "Vrsta gradnje potvrđena naslovom čl. %s u tekstu izmjena 2016. (SN 13/16)." % novi[rid]["izvor"]["clanak_plana"]
    d["pravila"] = list(novi.values())
    d["otvorena_pitanja"] = [q for q in d["otvorena_pitanja"] if not q.startswith("Osnovne vrijednosti za čl. 46a") and not q.startswith("Parkiranje")]
    d["otvorena_pitanja"] += [
        "Parkiranje: čl. 46a–46c upućuju na poglavlje 5. Odredbi (promet); čl. 5 u odluci iz 2016. nije izdvojen; potrebno je pročitati i taj članak.",
        "Definicije podruma i izračuna etaža: čl. 46a upućuje na „članak 3.”, a čl. 46b/46c na „članak 5.” (nedosljedno u izvorniku); čl. 3. je 2016. zamijenjen cijelim tekstom, ali nije izdvojen.",
        "„Izgrađeni” i „neizgrađeni” dio građevinskog područja: kig/kis i visina ovise o tome; granica je u grafičkom dijelu plana (ne u tekstu).",
        "Vjerodostojno tumačenje 2012. (ID 26150) ima 0 članaka u izvozu; nije moguće reći mijenja li tumačenje neki od uvjeta.",
        "Tekstovi 2010. i 2016. potječu iz izvoza treće strane i nisu uspoređeni sa sn.pgz.hr (tekst 2020. jest, razlike su samo u zapisu „m 2”, „k ig”, te izostavljenim naslovima članaka odluke).",
        "Članci 54c–54e (M2), 85a–85d, 50b–50e nisu izdvojeni u ovoj fazi."]
    d["napomena_prototipa"] = ("Prototip. Svako pravilo ima doslovni citat provjeren skriptom u tekstu odluke, ali nijedno se ne primjenjuje automatski dok zona nije potvrđena. "
                               "Osnovni tekst 2016. (SN 13/16) sada postoji (izvoz treće strane); tumačenje 2012. još nedostaje.")
    json.dump(d, open(BAZA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("pravila:", len(d["pravila"]), "citata neuspjelo (2016.):", lose)
    return lose

if __name__ == "__main__":
    lose = main(open(sys.argv[1], encoding="utf-8").read(), open(sys.argv[2], encoding="utf-8").read())
    sys.exit(1 if lose else 0)

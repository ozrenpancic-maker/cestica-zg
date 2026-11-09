#!/usr/bin/env python3
"""Uvjeti gradnje obiteljske i višeobiteljske kuće iz GUP-a Grada Rijeke (urbana pravila, čl. 67.–115.).

Izvor: Odluka o donošenju GUP-a Grada Rijeke, neslužbeni pročišćeni tekst (rijeka.hr, svibanj 2023.)
       + Odluka o izmjenama i dopunama (Službene novine Grada Rijeke 14/2023): čl. 69., 71., 83., 93., 94., 101., 105., 107.
Brojke su prepisane iz teksta članaka (vidi navode „txt”). Ovaj alat samo slaže JSON i upisuje ga u
src/rules_krk.json → ostaleJls["RIJEKA"]. Pokretanje: python3 -I tools/pgz/rijeka_gup.py
"""
import json, os, sys

KOD = "GUP Rijeka"
IZVOR = {
    "naziv": "Generalni urbanistički plan Grada Rijeke, odredbe za provođenje (neslužbeni pročišćeni tekst, svibanj 2023.) i izmjene i dopune (Službene novine Grada Rijeke 14/2023)",
    "sn": "Službene novine Grada Rijeke 14/2023",
    "url": "https://sn.rijeka.hr/2023/10/odluka-o-izmjenama-i-dopunama-odluke-o-donosenju-generalnog-urbanistickog-plana-grada-rijeke-4/",
    "pdf": "https://www.rijeka.hr/wp-content/uploads/2023/05/Odluka-o-dono%C5%A1enju-Generalnog-urbanisti%C4%8Dkog-plana-Grada-Rijeke-neslu%C5%BEbeni-pro%C4%8Di%C5%A1%C4%87eni-tekst.pdf",
    "status": "na snazi (izmjene i dopune SN 14/2023)",
    "provjera": "Čl. 67.–115. iz neslužbenog pročišćenog teksta (PDF s rijeka.hr, tekst izvučen strojno) i izmjene iz SN Grada Rijeke 14/2023 (čl. 20.–39. te odluke), preuzeto 9. 11. 2026.",
    "pravna_provjera": {"status": "NIJE_POTVRDENO",
                        "napomena": "Neslužbeni pročišćeni tekst; usporedba sa svim objavljenim odlukama nije napravljena. Urbano pravilo za česticu određuje kartografski prikaz 4.7 (čl. 84.)."}
}

def oblik(minC, izg, kis, prag=None, gbp=None, napomena=None):
    """prag: površina čestice iznad koje se kig i kis primjenjuju kao za tu površinu (npr. čl. 102. st. 2.)."""
    o = {"minC": minC, "minCIznimno": round(minC * 0.95), "izg": izg, "kis": kis, "kisPodrum": kis, "tlMin": 60,
         "tlMax": round(izg * prag, 1) if prag else None}
    if prag: o["_prag"] = prag
    if napomena: o["napomena"] = napomena
    return o

TXT_IZN = "građevina se može graditi na građevnoj čestici čija je površina najviše 5% (na području neposredne provedbe ovoga Plana) … manja od površine određene ovim Planom"

def tipovi(cl, gbp_ob, gbp_vo, et_ob, et_vo, vis_ob, vis_vo, st_ob, st_vo, S, D, N, txt, samo=None):
    ob = {"naziv": "Obiteljska kuća", "opis": f"najviše {st_ob} stana, GBP do {gbp_ob} m² (čl. 67. i {cl})", "clanak": cl,
          "gbpMax": gbp_ob, "gbpUkupno": True, "etaze": et_ob, "visina": vis_ob, "visinaOpis": f"{str(vis_ob).replace('.', ',')} m do vijenca",
          "slob": S, "txt": dict(txt, minCIznimno=TXT_IZN)}
    if D: ob["dvoj"] = D
    if N: ob["ugr"] = N
    out = {"obit": ob}
    if samo != "obit":
        vo = {"naziv": "Višeobiteljska kuća", "opis": f"najviše {st_vo} stanova, GBP do {gbp_vo} m² (čl. 68. i {cl})", "clanak": cl,
              "gbpMax": gbp_vo, "gbpUkupno": True, "etaze": et_vo, "visina": vis_vo, "visinaOpis": f"{str(vis_vo).replace('.', ',')} m do vijenca",
              "slob": dict(S), "txt": dict(txt, minCIznimno=TXT_IZN)}
        if D: vo["dvoj"] = dict(D)
        if N: vo["ugr"] = dict(N)
        out["visobit"] = vo
    if samo == "visobit": del out["obit"]
    # iznad praga površine kis se primjenjuje kao za prag: GBP najviše kis × prag, ako je to manje od granice tipa
    for T in out.values():
        for o in ("slob", "dvoj", "ugr"):
            P = T.get(o)
            if not P: continue
            pr = P.pop("_prag", None); P.pop("gbpMax", None)
            if pr and T.get("gbpMax") and P["kis"] * pr < T["gbpMax"]: P["gbpMax"] = round(P["kis"] * pr, 1)
    return out

def zona(t, meda, reg, zel, sirina, napomene=None, upozorenja=None):
    z = {"tipovi": t, "meda": meda, "regulacija": reg, "zelenilo": zel,
         "napomene": ([f"Najmanja širina građevne čestice duž građevnog pravca: {sirina}."] if sirina else []) + (napomene or [])}
    if upozorenja: z["upozorenja"] = upozorenja
    return z

def meda(cl, m, txt): return {"clanak": cl, "min": m, "opis": f"gradivi dio najmanje {str(m).replace('.', ',')} m od ruba čestice; od susjedne građevine najmanje 6 m (čl. 71.)", "opisIznimka": "", "txt": txt}
def reg(cl, d, osi, txt):
    r = {"clanak": cl, "opis": (f"građevni pravac najmanje {str(d).replace('.', ',')} m od regulacijskog pravca; " if d else "") + f"regulacijski pravac najmanje {str(osi).replace('.', ',')} m od osi pristupne prometnice", "txt": txt}
    if d: r["ostale"] = d
    return r
def zel(cl, m, txt): return {"clanak": cl, "min": m, "txt": txt}

ET2 = "podrum ili suteren i 2 nadzemne etaže"
ET3 = "podrum ili suteren i 3 nadzemne etaže"
PUT = "Kolno-pristupni put najmanje 4,5 m širine i najviše 50 m dužine."

ZONE, ZSET = [], {}
def dodaj(up, kod, naziv, cfg):
    key = kod
    ZONE.append([key, f"{up} · {naziv} ({kod})"])
    ZSET[key] = cfg

# --- urbano pravilo 5 (čl. 101.)
t5 = tipovi("101.", 400, 400, ET2, ET2, 8.0, 10.0, 2, 3,
            oblik(400, 0.4, 0.8, 600, 400), oblik(300, 0.45, 1.0, 450, 400), oblik(250, 0.5, 1.0, 375, 400),
            {"minC": "samostojeće građevine iznosi 400 m2, za gradnju dvojne i završne građevine niza iznosi 300 m2, a za gradnju građevine u nizu iznosi 250 m2",
             "izg": "kig iznosi: za samostojeću građevinu 0,4, za dvojnu i završnu građevinu niza 0,45, a za građevinu u nizu 0,5",
             "kis": "kis iznosi: za samostojeću građevinu 0,8, za dvojnu i za građevinu u nizu 1,0",
             "gbp": "najveća dozvoljena bruto razvijena površina građevine iznosi 400 m2",
             "etaze": "podrum ili suteren i dvije nadzemne etaže",
             "visina": "8,0 m za obiteljsku građevinu, a 10,0 m za višeobiteljsku građevinu"})
z5 = zona(t5, meda("101.", 4, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice iznosi 4,0 m"),
          reg("101.", None, 4.6, "najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 4,60 m"),
          zel("101.", 0.3, "najmanje 30% građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
          "samostojeća 14 m, dvojna i završna niza 12 m, u nizu 6 m",
          ["Za česticu veću od 600 m² (samostojeća), 450 m² (dvojna) ili 375 m² (niz) kig i kis primjenjuju se kao za tu površinu (čl. 101. st. 2.).", PUT])
for k, n in [("2-21-5.1", "Grohovo"), ("2-22-5.2", "Pašac"), ("2-24-5.3", "Svilno"), ("2-23-5.4", "Orehovica"), ("2-18-5.5", "Draga"), ("2-20-5.6", "Sveti Kuzam")]:
    dodaj("5", k, n, z5)

# --- urbano pravilo 6 (čl. 102.), a za obiteljske i višeobiteljske kuće i pravilo 9 (čl. 107. st. 3.)
def t6(kin=False):
    t = tipovi("102.", 400, 400, ET2, ET3, 8.0, 10.0, 2, 4,
               oblik(600, 0.3, 0.8, 800, 400), oblik(400, 0.4, 1.0, 600, 400), oblik(300, 0.45, 1.0, 450, 400),
               {"minC": "samostojeće građevine iznosi 600 m2, za gradnju dvojne i završne građevine niza iznosi 400 m2, a za gradnju građevine u nizu iznosi 300 m2",
                "izg": "kig iznosi: za samostojeću građevinu 0,3, za dvojnu i završnu građevinu niza 0,4, a za građevinu u nizu 0,45",
                "kis": "kis iznosi: za samostojeću građevinu 0,8, za dvojnu i za građevinu u nizu 1,0",
                "gbp": "najveća dozvoljena bruto razvijena površina građevine iznosi 400 m2",
                "etaze": "najveći dozvoljeni broj etaža višeobiteljske građevine iznosi podrum ili suteren i tri nadzemne etaže",
                "visina": "8,0 m za obiteljsku građevinu, a 10,0 m za višeobiteljsku građevinu"})
    return t
def z6(kin=False, up9=False):
    nap = ["Za česticu veću od 800 m² (samostojeća), 600 m² (dvojna) ili 450 m² (niz) kig i kis primjenjuju se kao za tu površinu (čl. 102. st. 2.).", PUT]
    if kin: nap.insert(0, "Na ovom području umjesto kis-a vrijedi koeficijent iskorištenosti nadzemno (kin) istih vrijednosti (čl. 102. st. 1.).")
    if up9: nap.insert(0, "Urbano pravilo 9: za obiteljske i višeobiteljske kuće vrijede uvjeti pravila 6 (čl. 107. st. 3.); višestambene građevine samo uz ulicu širine 9 m, na čestici od 2000 m² (nije u izračunu).")
    return zona(t6(), meda("102.", 4, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice iznosi 4,0 m"),
                reg("102.", 6, 4.6, "najmanja dozvoljena udaljenost građevnog pravca od regulacijskog pravca iznosi 6,0 m, a najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 4,60 m"),
                zel("102.", 0.35, "najmanje 35% građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
                "samostojeća 14 m, dvojna i završna niza 12 m, u nizu 8 m", nap)
for k, n in [("2-12-6.1", "Tibljaši"), ("2-15-6.2", "Donja Drenova"), ("2-10-6.3", "Srdoči"), ("2-10-6.4", "Gornji Zamet"), ("2-11-6.5", "Pehlin"),
             ("2-10-6.6", "Pilepići – Gornji Zamet"), ("2-3-6.7", "Diračje"), ("2-3-6.8", "Kantrida"), ("2-9-6.9", "Vežica"),
             ("2-12-6.10", "Škurinje"), ("2-9-6.10", "Škurinje"), ("2-12-6.11", "Bodulovo")]:
    dodaj("6", k, n, z6(kin=k in ("2-10-6.4", "2-10-6.6")))

# --- urbano pravilo 7 (čl. 103.): samo samostojeća obiteljska kuća
def z7(bosket=False):
    t = tipovi("103.", 300, None, ET3 if bosket else ET2, None, 7.0 if bosket else 8.0, None, 2, None,
               oblik(600, 0.3, 0.6, 600, 300), None, None,
               {"minC": "najmanja dozvoljena površina građevne čestice iznosi 600 m2",
                "izg": "najveći dozvoljeni koeficijent izgrađenosti (kig) iznosi 0,3",
                "kis": "najveći dozvoljeni koeficijent iskorištenosti (kis) iznosi 0,6",
                "gbp": "najveća dozvoljena građevinska bruto površina građevine iznosi 300 m2",
                "etaze": "podrum ili suteren i dvije nadzemne etaže, osim na području Bošket oznake 2.9.7.3. gdje … tri nadzemne etaže",
                "visina": "najveća dozvoljena visina građevine iznosi 8,0 m, a na području Bošket oznake 2-9-7.3. … 7,0 m"}, samo="obit")
    t["obit"]["oblici"] = [["slob", "samostojeća"]]
    return zona(t, meda("103.", 4, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice te udaljenost građevnog pravca od regulacijskog pravca iznosi 4,0 m"),
                reg("103.", 4, 4.6, "udaljenost građevnog pravca od regulacijskog pravca iznosi 4,0 m, a najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 4,60 m"),
                zel("103.", 0.3, "najmanja 30% građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
                "14 m", ["Pravilo 7 predviđa samo samostojeću obiteljsku kuću s najviše 2 stana (čl. 103.).",
                         "Za česticu veću od 600 m² kig i kis primjenjuju se kao za 600 m² (čl. 103. st. 4.).", PUT])
for k, n in [("2-9-7.1", "Strmica jug"), ("2-9-7.2", "Strmica sjever"), ("2-9-7.3", "Bošket"), ("2-9-7.4", "Gornja Vežica"), ("2-9-7.5", "Dukićevo naselje")]:
    dodaj("7", k, n, z7(bosket=k == "2-9-7.3"))

# --- urbano pravilo 8 (čl. 105.)
def z8(k):
    veliki = k in ("2-3-8.1", "2-3-8.2"); pav = k == "2-3-8.3"
    t = tipovi("105.", 400, 500, ET2, ET2 if pav else ET3, 8.0, 8.0 if pav else 10.0, 2, 6,
               oblik(900 if veliki else 800, 0.25, 0.6, 800, 400), oblik(600, 0.3, 0.8, 600, 400), oblik(400, 0.4, 0.8),
               {"minC": ("Kantrida i Marčeljeva Draga: samostojeća 900 m2, dvojna i završna niza 600 m2, u nizu 400 m2" if veliki else
                         "Pavlovac i Martinkovac: samostojeća 800 m2, dvojna i završna niza 600 m2, u nizu 400 m2"),
                "izg": "kig iznosi: za samostojeću građevinu 0,25, za dvojnu građevinu i završnu građevinu niza 0,3, a za građevinu u nizu 0,4",
                "kis": "kis iznosi: za samostojeću građevinu 0,6, za dvojnu građevinu i građevinu u nizu 0,8",
                "gbp": "najveća dozvoljena građevinska bruto površina građevine iznosi 500 m2 (obiteljska građevina po čl. 67. najviše 400 m2)",
                "etaze": "podrum ili suteren i tri nadzemne etaže, osim na području Pavlovac … podrum ili suteren i dvije nadzemne etaže",
                "visina": "obiteljske građevine 8,0 m, višeobiteljske 10,0 m; na području Pavlovac 8,0 m"})
    m = 5 if k in ("2-3-8.3", "2-10-8.4") else 4
    nap = ["Za česticu veću od 800 m² (samostojeća) ili 600 m² (dvojna) kig i kis primjenjuju se kao za tu površinu (čl. 105.).", PUT]
    if k == "2-10-8.4": nap.insert(0, "Martinkovac: višestambena višekatna građevina prema čl. 107. (izmjene SN 14/2023), nije u izračunu.")
    return zona(t, meda("105.", m, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice iznosi 4,0 m … Na područjima Pavlovac … i Martinkovac … iznosi 5,0 m"),
                reg("105.", 6, 4.6, "najmanja dozvoljena udaljenost građevnog pravca od regulacijskog pravca iznosi 6,0 m, a najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 4,60 m"),
                zel("105.", 0.4, "najmanje 40% građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
                "samostojeća 18 m, dvojna i završna niza 14 m, u nizu 12 m" if veliki else "samostojeća 16 m, dvojna i završna niza 14 m, u nizu 10 m", nap)
for k, n in [("2-3-8.1", "Kantrida"), ("2-3-8.2", "Marčeljeva Draga"), ("2-3-8.3", "Pavlovac"), ("2-10-8.4", "Martinkovac")]:
    dodaj("8", k, n, z8(k))

# --- urbano pravilo 9: obiteljske i višeobiteljske kuće prema pravilu 6 (čl. 107. st. 3.)
for k, n in [("2-9-9.1", "Gornja Vežica"), ("2-9-9.2", "Podvežica"), ("2-9-9.3", "Krimeja"), ("2-4-9.4", "Kozala"), ("2-4-9.5", "Kozala centar"),
             ("2-4-9.6", "Kantrida"), ("2-3-9.7", "Donji Zamet"), ("2-3-9.8", "Zamet centar"), ("2-3-9.9", "Diračje"), ("2-3-9.10", "Zamet"),
             ("2-3-9.11", "Krnjevo"), ("2-3-9.12", "Turnić"), ("2-3-9.13", "Podmurvice"), ("2-3-9.14", "Mlaka"), ("2-10-9.15", "Srdoči centar"),
             ("2-3-9.16", "Banderovo"), ("2-10-9.17", "Gornji Zamet centar"), ("2-10-9.18", "Martinkovac")]:
    z = z6(up9=True); z["tipovi"]["obit"]["clanak"] = "107. i 102."; z["tipovi"]["visobit"]["clanak"] = "107. i 102."
    dodaj("9", k, n, z)

# --- urbano pravilo 10 (čl. 108.): višeobiteljska kuća
t10 = tipovi("108.", None, 600, None, ET3, None, 9.0, None, 6, oblik(800, 0.3, 0.8), oblik(800, 0.3, 0.8, napomena="Dvojne samo iznimno, kao dovršenje postojeće izgradnje (čl. 108.)."), None,
             {"minC": "najmanja dozvoljena površina građevnih čestica iznosi 800 m2", "izg": "najveći dozvoljeni koeficijent izgrađenost građevne čestice iznosi 0,3",
              "kis": "najveći dozvoljeni koeficijent iskorištenosti građevne čestice iznosi 0,8", "gbp": "najveća dozvoljena građevinska bruto površina građevina iznosi 600 m2",
              "etaze": "podrum ili suteren i tri nadzemne etaže", "visina": "najveća dozvoljena visina građevine iznosi 9,0 m"}, samo="visobit")
t10["visobit"]["oblici"] = [["slob", "samostojeća"], ["dvoj", "dvojna (iznimno)"]]
dodaj("10", "2-4-10.1", "Potok", zona(t10, meda("108.", 4, "najmanja dozvoljena udaljenost građevine od granice građevne čestice iznosi 4,0"),
                                       reg("108.", 5, 4.6, "udaljenost građevnog od regulacijskog pravca iznosi najmanje 5,0 m ili građevni pravac odrediti u skladu s postojećom gradnjom"),
                                       zel("108.", 0.3, "30% građevne čestice potrebno je ozeleniti i hortikulturno urediti"), None,
                                       ["Pravilo 10 predviđa višeobiteljsku kuću (najviše 6 stanova), pretežito samostojeću (čl. 108.).",
                                        "Udaljenost regulacijskog pravca od osi prometnice pravilo 10 ne propisuje posebno; 4,6 m je vrijednost iz susjednih pravila, provjeri."]))
ZSET["2-4-10.1"]["regulacija"]["opis"] = "građevni pravac najmanje 5 m od regulacijskog pravca ili u skladu s postojećom gradnjom"

# --- urbano pravilo 13 (čl. 112.)
def z13(k):
    mali = k in ("3-9-13.7", "3-9-13.8"); trampi = k == "3-10-13.9"
    gbp = 250 if k == "3-9-13.8" else 400 if k == "3-9-13.7" else 600
    st_vo = 4 if k == "3-9-13.8" else 8 if k in ("3-2-13.1", "3-3-13.2", "3-17-13.3", "3-15-13.6") else 8
    et_vo = ET2 if mali else ET3
    vis_ob = 7.0 if mali else 8.0; vis_vo = 7.0 if mali else 10.0
    t = tipovi("112.", min(gbp, 400), gbp, ET2, et_vo, vis_ob, vis_vo, 2, st_vo,
               oblik(900, 0.25, 0.6, 1000, min(gbp, 400)), oblik(600, 0.3, 0.8, 800, min(gbp, 400)), oblik(400, 0.4, 0.8, 600, min(gbp, 400)),
               {"minC": "samostojeće građevine iznosi 900 m2, za gradnju dvojne građevine i završne građevine niza iznosi 600 m2, a za građevinu u nizu iznosi 400 m2",
                "izg": "kig iznosi: za samostojeću građevinu 0,25, za dvojnu građevinu i završnu građevinu niza 0,3 i građevinu u nizu 0,4",
                "kis": "kis iznosi: za samostojeću građevinu 0,6, za dvojnu građevinu i građevinu u nizu 0,8",
                "gbp": "najveća dozvoljena građevinska bruto površina građevine iznosi 600 m2, na području Istravino … 400 m2, a na području Kačjak … 250 m2",
                "etaze": "podrum ili suteren i tri nadzemne etaže, a na području Istravino … i Kačjak … podrum ili suteren i dvije nadzemne etaže",
                "visina": "8,0 m za obiteljske građevine te 10,0 m za višeobiteljske građevine, a na području Istravino … i Kačjak … 7,0 m"})
    nap = ["Za česticu veću od 1000 m² (samostojeća), 800 m² (dvojna) ili 600 m² (niz) kig i kis primjenjuju se kao za tu površinu (čl. 112. st. 3.).",
           "Neuređeno (niskokonsolidirano) područje: na karti 4.4 provjeri provodi li se plan neposredno ili tek kroz plan užeg područja (UPU)."]
    if k in ("3-15-13.6", "3-10-13.9"): nap.insert(0, "Na ovom području umjesto kis-a vrijedi koeficijent iskorištenosti nadzemno (kin) istih vrijednosti (čl. 112.).")
    if k in ("3-16-13.5", "3-17-13.3"): nap.append("Višestambenu višekatnu građevinu ovdje određuje plan užeg područja (čl. 113., izmjene SN 14/2023).")
    upoz = None
    if trampi:
        upoz = ["Za Trampe (3-10-13.9) čl. 112. ne navodi broj etaža, visinu ni širinu čestice; prikazane su vrijednosti ostalih područja pravila 13 i nisu potvrđene."]
        nap.append("Za Trampe članak ne navodi najmanju širinu čestice.")
    return zona(t, meda("112.", 5, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice iznosi 5,0 m"),
                reg("112.", 6, 5.0, "najmanja dozvoljena udaljenost građevnog pravca od regulacijskog pravca iznosi 6,0 m, a najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 5,0 m"),
                zel("112.", 0.4, "najmanje 40 % građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
                None if trampi else ("samostojeća 14 m, dvojna i završna niza 10 m, u nizu 8 m" if mali else "samostojeća 20 m, dvojna i završna niza 16 m, u nizu 14 m"),
                nap, upoz)
for k, n in [("3-2-13.1", "Turanj"), ("3-3-13.2", "Marčeljeva Draga"), ("3-17-13.3", "Brašćine – Pulac"), ("3-9-13.4", "Strmica"), ("3-16-13.5", "Gornja Drenova"),
             ("3-15-13.6", "Bok"), ("3-9-13.7", "Istravino"), ("3-9-13.8", "Kačjak"), ("3-10-13.9", "Trampi")]:
    dodaj("13", k, n, z13(k))

# --- urbano pravilo 14 (čl. 115.)
def z14(k):
    t = tipovi("115.", 400, 400, ET2, ET2, 8.0, 10.0, 2, 4,
               oblik(600, 0.4, 0.8, 600, 400), oblik(400, 0.45, 1.0, 400, 400), oblik(250, 0.5, 1.0, 250, 400),
               {"minC": "samostojeće građevine iznosi 600 m2, za gradnju dvojne građevine i završne građevine niza iznosi 400 m2, a za građevinu u nizu iznosi 250 m2",
                "izg": "kig iznosi: za samostojeću građevinu 0,4, za dvojnu građevinu i završnu građevinu niza 0,45 i građevinu u nizu 0,5",
                "kis": "kis iznosi: za samostojeću građevinu 0,8, za dvojnu građevinu i građevinu u nizu 1,0",
                "gbp": "najveća dozvoljena građevinska bruto površina građevine iznosi 400 m2",
                "etaze": "najveći dozvoljeni broj etaža građevine iznosi podrum ili suteren i dvije nadzemne etaže",
                "visina": "najveća dozvoljena visina obiteljske građevine iznosi 8,0 m, a višeobiteljske građevine 10,0 m"})
    nap = ["Za česticu veću od 600 m² (samostojeća), 400 m² (dvojna) ili 250 m² (niz) kig i kis primjenjuju se kao za tu površinu (čl. 115. st. 2.).",
           "Neuređeno (niskokonsolidirano) područje: na karti 4.4 provjeri provodi li se plan neposredno ili tek kroz plan užeg područja (UPU)."]
    if k in ("3-10-14.1", "3-13-14.4"): nap.insert(0, "Na ovom području umjesto kis-a vrijedi koeficijent iskorištenosti nadzemno (kin) istih vrijednosti (čl. 115.).")
    return zona(t, meda("115.", 4, "najmanja dozvoljena udaljenost gradivog dijela građevne čestice od ruba građevne čestice te najmanja dozvoljena udaljenost građevnog pravca od regulacijskog pravca iznosi 4,0 m"),
                reg("115.", 4, 4.6, "najmanja dozvoljena udaljenost građevnog pravca od regulacijskog pravca iznosi 4,0 m, a najmanja dozvoljena udaljenost regulacijskog pravca od osi pristupne prometnice iznosi 4,60 m"),
                zel("115.", 0.3, "najmanje 30% građevne čestice potrebno je ozeleniti i hortikulturno urediti"),
                "samostojeća 14 m, dvojna i završna niza 12 m, u nizu 6 m", nap)
for k, n in [("3-10-14.1", "Grpci – Pilepići"), ("3-13-14.2", "Škurinje"), ("3-4-14.3", "Kozala"), ("3-13-14.4", "Lipa"), ("3-13-14.5", "Drenova – Ivana Žorža")]:
    dodaj("14", k, n, z14(k))

# --- pravila bez izračuna za kuću
BEZ = [
    ("1", "povijesne gradske cjeline (Stari grad, Trsat, Sveti Kuzam)", "91.", "Urbano pravilo 1 (povijesne gradske cjeline): uvjete određuje točka 3.2.8.1. obrazloženja plana i konzervatorski uvjeti; aplikacija ih ne računa (čl. 91.)."),
    ("2", "gradski centar (Rijeka, Sušak)", "92.", "Urbano pravilo 2 (gradski centar): samo višestambene, stambeno-poslovne i poslovno-stambene građevine (čl. 92.); obiteljska kuća nije predviđena."),
    ("3", "osobito vrijedni predjeli višeobiteljske gradnje (Belveder, Bulevard, Pećine, Kostabela, Bivio, Razbojna, Dražica, Istarska, Podkoludrica)", "93. i 94.",
     "Urbano pravilo 3: nova gradnja samo kroz plan užeg područja, osim pojedinačne interpolacije višeobiteljske kuće uz konzervatorske uvjete (čl. 93.–94., izmjene SN 14/2023); aplikacija je ne računa."),
    ("4", "dovršena područja višestambene izgradnje", "97. i 98.", "Urbano pravilo 4: postojeće obiteljske kuće rekonstruiraju se prema pravilu 6, a nove takve kuće nije moguće planirati (čl. 97.)."),
    ("11", "planski građeno socijalno stanovanje (Podmurvice, Kantrida, Cento celle)", "109.", "Urbano pravilo 11: mješovita, pretežito poslovna namjena (čl. 109.); obiteljska kuća nije obrađena."),
    ("12", "kompleksi jedne namjene (Bolnica, Dom umirovljenika, Plase, Pulac, Sveta Katarina)", "110.", "Urbano pravilo 12: kompleksi jedne namjene; zahvati samo u funkciji osnovne namjene (čl. 110.)."),
    ("15", "zone gradskog centra za transformaciju (Štranga, Rikard Benčić, Beli Kamik, Blok Ciottina, Autobusni kolodvor)", "117.", "Urbano pravilo 15: gradi se prema čl. 92. (gradski centar); obiteljska kuća nije predviđena."),
    ("16", "kompleksi za rekonstrukciju (Školjić, Sjeverna Brajdica)", "118.", "Urbano pravilo 16: gradnja tek prema planu užeg područja; dotad samo rekonstrukcija u postojećim gabaritima (čl. 118.)."),
    ("17", "područja širenja višestambene i višeobiteljske gradnje (Lukovići, Škurinje, Sveta Katarina)", "119.", "Urbano pravilo 17: višeobiteljska i višestambena gradnja prema pokazateljima šireg područja (Gig 0,35, Kis 1,2) uz ulicu širine 12 m (čl. 119.); izračun za kuću na čestici nije moguć."),
    ("18", "potezi urbaniteta (Zvonimirova, Liburnijska, Mlaka centar)", "120.", "Urbano pravilo 18: potezi urbaniteta, gradnja do 8 nadzemnih etaža uz ulicu širine 12 m (čl. 120.); obiteljska kuća nije predviđena."),
    ("19", "gradski projekti (Delta, Kampus, Rujevica, Torpedo, Preluka, Mlaka)", "121.", "Urbano pravilo 19: gradski projekti prema obrazloženju plana i planovima užeg područja (čl. 121.); izračun za kuću nije moguć."),
]
for up, naziv, cl, msg in BEZ:
    key = "UP" + up
    ZONE.append([key, f"{up} · {naziv}"])
    ZSET[key] = {"tipovi": None, "drugaZona": msg + " Mjerodavna je lokacijska informacija Grada Rijeke."}

# zone sortirane po broju pravila
def kljuc(z):
    up = int(z[1].split(" · ")[0]); return (up, z[1])
ZONE.sort(key=kljuc)

RIJEKA = {
    "kod": KOD, "izvor": IZVOR,
    "upozorenje": "Urbano pravilo se ne očitava automatski: kvart odabireš sam prema kartografskom prikazu 4.7 GUP-a („Urbana pravila”); potvrđuje ga lokacijska informacija.",
    "oblici": [["slob", "samostojeća"], ["dvoj", "dvojna ili završna niza"], ["ugr", "u nizu"]],
    "kisUkupni": True,
    "neizgradeni": {"mod": "provjera", "clanak": "84.", "txt": "Urbana pravila provode se neposredno i posredno. … Područja grada na kojima se ovaj Plan neposredno i posredno provodi prikazana su kartografskim prikazom broj 4.4.",
                    "msg": "Neizgrađeni dio: GUP Rijeke se na nekim područjima provodi tek kroz plan užeg područja (karta 4.4). Provjeri u lokacijskoj informaciji."},
    "grupe": [{"naselje": ".*", "naziv": "GUP Grada Rijeke",
               "napomena": "Uvjeti za kuće ovise o urbanom pravilu (kartografski prikaz 4.7) i namjeni (S stambena ili M1 mješovita pretežito stambena, karta 1.); provjeri obje karte."}],
    "zone": ZONE, "zoneSet": ZSET, "zonaLabel": "Urbano pravilo (kvart, karta 4.7)",
    "zonaNapomena": "GUP Rijeke dijeli grad na 19 urbanih pravila po kvartovima (čl. 90., 100. i 111.). Ako čestica leži u dva pravila, vrijedi ono koje pokriva veći dio čestice (čl. 84.).",
    "drugaZona": "Za odabrano urbano pravilo uvjeti za obiteljske i višeobiteljske kuće nisu obrađeni.",
    "tipovi": t6(),
    "meda": z6()["meda"], "regulacija": z6()["regulacija"], "zelenilo": z6()["zelenilo"],
    "simulator": {"krov": {"clanak": "71.", "nagibMin": 0, "nagibMax": 23, "ravniDopusten": True,
                           "txt": "nagib kosog krova iznosi najviše 23 stupnja"}},
    "pristup": {"napomena": "Čestica obiteljske i višeobiteljske kuće može imati najviše dva kolna priključka na istu ulicu, širine 3–5 m (čl. 83., izmjene SN 14/2023). Parkirališna mjesta prema čl. 156."},
    "napomene": ["Najmanja tlocrtna površina osnovne građevine 60 m²; od susjedne građevine najmanje 6 m; kosi krov najviše 23°, nadozid potkrovlja najviše 90 cm (čl. 71.).",
                 "Čestica smije biti do 5 % manja od propisane (neposredna provedba), uz poštivanje kig-a i kis-a (čl. 71.).",
                 "Pomoćna građevina: jedna etaža, visina do 3 m, unutar gradivog dijela (čl. 80.); balkoni, terase i otvorena stubišta najmanje 4 m od međe (čl. 81.)."],
}

for z in ZSET.values():
    if z.get("tipovi"): z["napomene"] = z["napomene"] + RIJEKA["napomene"]

if __name__ == "__main__":
    p = os.path.join(os.path.dirname(__file__), "..", "..", "src", "rules_krk.json")
    d = json.load(open(p, encoding="utf-8"))
    d["ostaleJls"]["RIJEKA"] = RIJEKA
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("zone", len(ZONE), "s izračunom", sum(1 for z in ZSET.values() if z.get("tipovi")))

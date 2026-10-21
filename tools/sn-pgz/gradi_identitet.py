#!/usr/bin/env python3
"""Zlatni skup identiteta planova: koja odluka veže uz koji plan (i koje veze su ZABRANJENE).
Svaki dokaz je doslovni citat iz teksta odluke iz izvoza (cesticahr_upu_rules_draft*.json); skripta provjerava da citat postoji
i upisuje članak izvoza u kojem je pronađen. Zapisi su ručno pročitani (jedan pregledatelj), tekst potječe iz izvoza treće strane.
Upotreba: gradi_identitet.py IZVOZ.json  -> tests/zlatni/krk-plan-identity-v1.json"""
import json, os, re, sys, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "krk-plan-identity-v1.json")
URL = "https://www.sn.pgz.hr/default.asp?Link=odluke&id=%s"
L = []   # veze odluka -> plan
def link(oid, opc, tip, broj, naziv, veza, ocek, citat, nap="", gen=None, plan_oid=None):
    L.append({"odluka_id": oid, "plan": {"opcina": opc, "vrsta": tip, "broj": broj, "naziv": naziv, "generacija": gen},
              "veza": veza, "ocekivanje": ocek, "dokaz": {"odluka_id": oid, "citat": citat}, "napomena": nap})
# --- Punat UPU 3
link("20518","Punat","UPU","3","UPU 3 – centralno naselje Punat (N1)","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja (UPU3) građevinskog područja naselja N1 - centralno naselje Punat")
link("33933","Punat","UPU","3","UPU 3 – centralno naselje Punat (N1)","AMENDS","MUST_LINK","U Odluci o donošenju UPU 3 - građevinsko područje naselja N 1 - Centralno naselje Punat")
link("41087","Punat","UPU","3","UPU 3 – centralno naselje Punat (N1)","AMENDS","MUST_LINK","Donosi se Odluka o II. izmjenama i dopunama Urbanističkog plana uređenja (UPU3) građevinskog područja naselja N1 - centralno naselje Punat")
link("41977","Punat","UPU","3","UPU 3 – centralno naselje Punat (N1)","INITIATES","MUST_LINK","Donosi se Odluka o izradi III. izmjena i dopuna UPU3 – građevinsko područje naselja N1 – Centralno naselje Punat",
     "Odluka o izradi nije donesena izmjena; ne smije se tretirati kao izvor uvjeta.")
link("22808","Punat","UPU","4","UPU 4 – sportsko-rekreacijska namjena R6a","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja (UPU4) građevinsko područje sportsko rekreacijske namjene R6a")
link("19316","Punat","UPU","7","UPU 7 – poslovna namjena K1 Dokolovo","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja (UPU7) građevinskog područja poslovne namjene K1 - Dokolovo")
link("34173","Punat","UPU","9","UPU 9 – Stara Baška (N2)","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja - UPU 9 - građevinsko područje naselja N2 - Stara Baška sa pripadajućim građevinskim područjima sportsko-rekreacijske namjene R7a",
     "Stara Baška je naselje u Općini Punat; ime sadrži „Baška” ali nije Općina Baška.")
link("34173","Punat","PPU",None,"PPU Općine Punat","ADOPTS","MUST_NOT_LINK","Donosi se Urbanistički plan uređenja - UPU 9 - građevinsko područje naselja N2 - Stara Baška","Odluka donosi UPU 9, ne PPU. PPUO Punat samo se citira kao osnova obuhvata.")
link("34173","Baška","UPU",None,"bilo koji plan Općine Baška","REFERENCES","MUST_NOT_LINK","Odluke o donošenju Prostornog plana uređenja Općine Punat","Općina je Punat.")
# --- Baška
link("30487","Baška","DPU","2","DPU-2 groblje i proširenje groblja (G3), Batomalj","ADOPTS","MUST_LINK","Donosi se Detaljni plan uređenja groblja i proširenja groblja (G 3 ) u naselju Batomalj (DPU-2)")
link("30487","Baška","PPU",None,"PPU Općine Baška","ADOPTS","MUST_NOT_LINK","Donosi se Detaljni plan uređenja groblja i proširenja groblja (G 3 ) u naselju Batomalj (DPU-2)","PPUO Baška se samo citira kao pravna osnova (čl. 153.).")
link("25522","Baška","DPU","2","DPU-2 groblje i proširenje groblja (G3), Batomalj","INITIATES","MUST_LINK","Donosi se Odluka o izradi Detaljnog plana uređenja za izdvojeno građevinsko područje izvan naselja - groblja DPU - 2 - groblja i proširenja groblja (G 3 ) u naselju Batomalj")
link("25522","Baška","PPU",None,"PPU Općine Baška","INITIATES","MUST_NOT_LINK","Donosi se Odluka o izradi Detaljnog plana uređenja za izdvojeno građevinsko područje izvan naselja - groblja DPU - 2","PPUO Baška se samo citira.")
link("28779","Baška","UPU","3","UPU 3 – Jurandvor sjever (N2)","ADOPTS","MUST_LINK","Ovom Odlukom donosi se Urbanistički plan uređenja UPU-3 - Jurandvor - sjever (N2)")
link("28785","Baška","UPU","9","UPU 9 – Draga Bašćanska jug (N4-1)","ADOPTS","MUST_LINK","Ovom Odlukom donosi se Urbanistički plan uređenja UPU-9 - Draga Bašćanska - jug (N4-1)")
for br,naz,cit in (("3","UPU 3 – Jurandvor sjever (N2)","UPU - 3 - Jurandvor - sjever (N2), UPU - 4 - Jurandvor - jug (N2) i UPU - 5 - Jurandvor - zapad (N2)"),
                   ("4","UPU 4 – Jurandvor jug (N2)","UPU - 3 - Jurandvor - sjever (N2), UPU - 4 - Jurandvor - jug (N2) i UPU - 5 - Jurandvor - zapad (N2)"),
                   ("5","UPU 5 – Jurandvor zapad (N2)","UPU - 3 - Jurandvor - sjever (N2), UPU - 4 - Jurandvor - jug (N2) i UPU - 5 - Jurandvor - zapad (N2)")):
    link("25525","Baška","UPU",br,naz,"INITIATES","MUST_LINK",cit,"Jedna odluka o izradi za tri plana.")
for br,naz in (("6","UPU 6 – Batomalj sjever (N3-1)"),("7","UPU 7 – Batomalj jug (N3-2)")):
    link("25523","Baška","UPU",br,naz,"INITIATES","MUST_LINK","UPU - 6 - Batomalj - sjever (N3-1) i UPU - 7 - Batomalj - jug (N3-2)","Jedna odluka o izradi za dva plana.")
for br,naz in (("8","UPU 8 – Draga Bašćanska sjever (N4-1)"),("9","UPU 9 – Draga Bašćanska jug (N4-1)")):
    link("25524","Baška","UPU",br,naz,"INITIATES","MUST_LINK","UPU - 8 - Draga Bašćanska - sjever (N4-1) i UPU - 9 - Draga Bašćanska - jug (N4-1)","Jedna odluka o izradi za dva plana.")
for br,naz in (("1","UPU 1 – Baška (N1-1)"),("2","UPU 2 – Baška Zarok (N1-2)")):
    link("16599","Baška","UPU",br,naz,"INITIATES","MUST_LINK","UPU 1 - Baška (N1-1) i UPU 2 - Baška (N1-2)","Jedna odluka o izradi za dva plana.")
    for oid in ("23023","20906"):
        link(oid,"Baška","UPU",br,naz,"AMENDS_PREPARATION_DECISION","MUST_LINK","U Odluci o izradi urbanističkih planova uređenja UPU 1 Baška i UPU 2 Baška",
             "Mijenja ODLUKU O IZRADI, ne tekst plana.")
        link(oid,"Baška","UPU",br,naz,"AMENDS","MUST_NOT_LINK","U Odluci o izradi urbanističkih planova uređenja UPU 1 Baška i UPU 2 Baška",
             "Ne smije postati zakrpa teksta UPU-a: odluka mijenja odluku o izradi.")
link("36814","Baška","UPU","1","UPU 1 – Baška (N1-1)","AMENDS","MUST_LINK","Ovom Odlukom usklađuje se Urbanistički plan uređenja UPU-1 Baška (N1-1)","Usklađenje UPU-a s III. izmjenama PPUO Baška; PPUO se samo citira.")
link("36814","Baška","PPU",None,"PPU Općine Baška","AMENDS","MUST_NOT_LINK","Ovom Odlukom usklađuje se Urbanistički plan uređenja UPU-1 Baška (N1-1)","Odluka ne mijenja PPUO.")
link("35201","Baška","UPU","2","UPU 2 – Baška Zarok (N1-2)","INITIATES","MUST_LINK","Donosi se Odluka o izradi usklađenja Urbanističkog plana uređenja UPU-2 - Baška - Zarok (N1-2)")
# --- Krk
for oid in ("28241","35506","39364","42442"):
    link(oid,"Krk","UPU","1","UPU 1 Krk (NA1, R1-1 Lunta, R3-8, R3-10, R3-11)","UNKNOWN","MUST_LINK",
         "Građevinsko područje naselja Krk NA 1 (uključuje uređene plaže: Gradska plaža - R3 10 i Dražica R3 11 )",
         "Vrsta veze (donošenje/pročišćeni) ne vidi se iz članka 1.; identitet plana dokazan je popisom područja koji odgovara naslovu 32508.",gen="B (nakon PPUG SN 28/11)")
link("32508","Krk","UPU","1","UPU 1 Krk (NA1, R1-1 Lunta, R3-8, R3-10, R3-11)","INITIATES","MUST_LINK","Donosi se Odluka o izradi II. izmjena i dopuna Urbanističkog plana uređenja UPU 1-Krk (NA1, R1 1 , R3 8 , R3 10 , R3 11 )",gen="B (nakon PPUG SN 28/11)")
link("14783","Krk","UPU","1","UPU naselja Krk (starija generacija)","AMENDS","REVIEW_REQUIRED","Ovom Odlukom donose se Izmjene i dopune Urbanističkog plana uređenja naselja Krk",
     "Mijenja raniji UPU naselja Krk (SN 17/00, 18/00, 27/03, 17/04); nijedan članak nije identičan s 28241; automatski spoj s generacijom B zabranjen.",gen="A (SN 17/00 ... 17/04)")
link("37758","Krk","UPU","25","UPU 25 – kamp Glavotok (T3)","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja 25- kamp Glavotok (T3)")
# --- Dobrinj, Omišalj
link("41102","Dobrinj","UPU","9","UPU 9 – K-4 Brestovica (Gostinjac)","ADOPTS","MUST_LINK","Donosi se Urbanistički plan uređenja UPU 9 građevinskog područja K-4 Brestovica (Gostinjac)")
link("31878","Omišalj","UPU","9","UPU 9 – sportsko područje izvan naselja Omišalj","ADOPTS","MUST_LINK","Donosi se Urbanistički plan UPU 9 za dio građevinskog sportskog područja izvan naselja Omišalj")
link("43185","Omišalj","UPU","2","UPU 2 – Njivice (NA1)","INITIATES","MUST_LINK","Donosi se Odluka o pokretanju postupka stavljanja izvan snage dijela UPU 2 – Njivice (NA1)","Pokretanje postupka stavljanja izvan snage DIJELA plana; nije stavljanje izvan snage.")
link("43185","Omišalj","UPU","18","UPU 18 – Njivice ugostiteljsko-turistička (budući plan)","REFERENCES","MUST_LINK","obuhvat budućeg urbanističkog plana UPU 18","Budući plan; ne smije biti ADOPTS.")
link("43185","Omišalj","UPU","18","UPU 18 (budući plan)","ADOPTS","MUST_NOT_LINK","obuhvat budućeg urbanističkog plana UPU 18")
link("43184","Omišalj","UPU","2","UPU 2 – Njivice (NA1)","INITIATES","MUST_LINK","Donosi se Odluka o pokretanju postupka stavljanja izvan snage dijela UPU 2 – Njivice (NA1)")
link("43184","Omišalj","UPU","20","UPU 20 – Njivice naselje (budući plan)","REFERENCES","MUST_LINK","budućeg urbanističkog plana UPU 20","Budući plan; ne smije biti ADOPTS.")
link("43184","Omišalj","UPU","20","UPU 20 (budući plan)","ADOPTS","MUST_NOT_LINK","budućeg urbanističkog plana UPU 20")
link("43829","Omišalj","UPU","2","UPU 2 – Njivice (NA1)","AMENDS","REVIEW_REQUIRED","Odluka o stavljanju izvan snage dijela Urbanističkog plana uređenja UPU 2 – Njivice (NA 1)","Mijenja naziv odluke o pokretanju postupka; veza prema planu nije izmjena njegovog teksta.")
link("46708","Omišalj","UPU","2","UPU 2 – Njivice (NA1)","AMENDS","REVIEW_REQUIRED","U Odluci o pokretanju postupka stavljanja izvan snage dijela UPU 2 – Njivice (NA1)","Mijenja odluku o pokretanju postupka; ne tekst plana.")
# --- parovi
P = []
def par(a, b, ocek, citat_a, citat_b, nap=""):
    P.append({"a": a, "b": b, "ocekivanje": ocek, "dokaz_a": {"odluka_id": a, "citat": citat_a}, "dokaz_b": {"odluka_id": b, "citat": citat_b}, "napomena": nap})
# UPU 9 u četiri općine: nikad ista veza
tx = {"34173": "Donosi se Urbanistički plan uređenja - UPU 9 - građevinsko područje naselja N2 - Stara Baška",
      "28785": "Ovom Odlukom donosi se Urbanistički plan uređenja UPU-9 - Draga Bašćanska - jug (N4-1)",
      "41102": "Donosi se Urbanistički plan uređenja UPU 9 građevinskog područja K-4 Brestovica (Gostinjac)",
      "31878": "Donosi se Urbanistički plan UPU 9 za dio građevinskog sportskog područja izvan naselja Omišalj"}
ks = list(tx)
for i in range(len(ks)):
    for j in range(i + 1, len(ks)):
        par(ks[i], ks[j], "MUST_NOT_LINK", tx[ks[i]], tx[ks[j]], "Isti broj „UPU 9” u različitim općinama = različiti planovi.")
par("20518", "28779", "MUST_NOT_LINK", "Donosi se Urbanistički plan uređenja (UPU3) građevinskog područja naselja N1 - centralno naselje Punat", "Ovom Odlukom donosi se Urbanistički plan uređenja UPU-3 - Jurandvor - sjever (N2)", "UPU 3 Punat ≠ UPU 3 Baška.")
cit = "Građevinsko područje naselja Krk NA 1 (uključuje uređene plaže: Gradska plaža - R3 10 i Dražica R3 11 )"
for a, b in (("28241", "35506"), ("35506", "39364"), ("39364", "42442")):
    par(a, b, "MUST_LINK_SAME_PLAN", cit, cit, "Isti popis područja u članku 1.")
par("32508", "28241", "MUST_LINK_SAME_PLAN", "UPU 1-Krk (NA1, R1 1 , R3 8 , R3 10 , R3 11 )", cit, "Isti popis područja (NA1, R1-1 Lunta, R3-8, R3-10, R3-11).")
par("14783", "28241", "MUST_NOT_LINK_AUTOMATICALLY", "Ovom Odlukom donose se Izmjene i dopune Urbanističkog plana uređenja naselja Krk", cit, "Starija generacija plana (SN 17/00…17/04); nijedan od 150 članaka nije identičan. Smije samo u REVIEW_REQUIRED.")
par("30487", "28779", "MUST_NOT_LINK", "Donosi se Detaljni plan uređenja groblja i proširenja groblja (G 3 ) u naselju Batomalj (DPU-2)", "Ovom Odlukom donosi se Urbanistički plan uređenja UPU-3 - Jurandvor - sjever (N2)", "DPU ≠ UPU.")

def main(izvoz):
    d = json.load(open(izvoz, encoding="utf-8"))
    by = collections.defaultdict(list)
    for a in d["articles"]: by[a["document_id"]].append(a)
    U = {re.search(r"id=(\d+)", x["url"]).group(1): x for x in d["documents"]}
    lose = []
    def nadi(ev):
        x = U.get(ev["odluka_id"])
        if not x: lose.append(("nema odluke", ev["odluka_id"])); return
        for a in by[x["id"]]:
            if S.norm(ev["citat"]) in S.norm(re.sub(r"\s+", " ", a["body"])): ev["clanak_izvoza"] = a["article_no"]; ev["url"] = URL % ev["odluka_id"]; return
        lose.append(("citat nije u tekstu", ev["odluka_id"], ev["citat"][:70]))
    for l in L: nadi(l["dokaz"])
    for p in P: nadi(p["dokaz_a"]); nadi(p["dokaz_b"])
    for i, l in enumerate(L, 1): l["id"] = "l%03d" % i
    for i, p in enumerate(P, 1): p["id"] = "p%03d" % i
    h = hashlib.sha256(json.dumps([L, P], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    json.dump({"opis": "Zlatni skup identiteta planova (ODLUKA ↔ PLAN) s ZABRANJENIM vezama. Ručno pročitano iz teksta odluka iz izvoza treće strane; jedan pregledatelj; nije neovisno pravno provjereno. Zamrznut od v1: izmjena samo uz dokaz iz teksta i unos u promjene.",
               "verzija": 1, "status": "SOURCE_READ_BY_ONE_REVIEWER_NOT_INDEPENDENTLY_VERIFIED", "sha256": h,
               "promjene": ["v1: prvi popis (Punat, Baška, Krk, Dobrinj, Omišalj)."],
               "vrste_veze": ["ADOPTS", "AMENDS", "INITIATES", "REPEALS", "REFERENCES", "UNKNOWN", "AMENDS_PREPARATION_DECISION"],
               "ocekivanja": ["MUST_LINK", "MUST_NOT_LINK", "REVIEW_REQUIRED", "MUST_LINK_SAME_PLAN", "MUST_NOT_LINK_AUTOMATICALLY"],
               "veze": L, "parovi": P}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("veza:", len(L), "parova:", len(P), "problema:", lose); return lose
if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)

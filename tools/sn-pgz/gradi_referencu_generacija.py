#!/usr/bin/env python3
"""Neovisni referentni skup generacija (v1): Baška, Malinska-Dubašnica, Vrbnik. PODACI, NE ALGORITAM.
Ne smije se koristiti za podešavanje algoritma; služi samo za validaciju. Ne dira zamrznuti skup krk-plan-identity-v1.
Razine: L1 izričita pravna veza u tekstu odluke (citat + brojevi SN); L2 posredno (npr. isti naslov kao u citatu druge odluke); L3 kandidat (naziv, područje, datum).
Samo L1 je 'dokazano'. Upotreba: gradi_referencu_generacija.py IZVOZ.json -> tests/zlatni/generacije-baska-malinska-vrbnik-v1.json"""
import json, os, re, sys, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "generacije-baska-malinska-vrbnik-v1.json")
def E(o, c, uloga): return {"odluka_id": o, "citat": c, "uloga": uloga}
def D(o, ref, razina, dokazi, kandidat=None, nap=""):
    return {"odluka_id": o, "generation_ref": ref if razina == "L1" else "UNDETERMINED", "kandidat": kandidat, "razina": razina, "dokazano": razina == "L1", "dokazi": dokazi, "napomena": nap}
SL = [
 {"id": "C1", "opcina": "Malinska-Dubašnica", "plan": "PPUO Malinska-Dubašnica", "tip": "ISTA_GENERACIJA_LANAC_IZMJENA + ZAMKA_UKIDANJE_KARTOGRAFSKIH_PRIKAZA",
  "pitanje": "Pripadaju li pročišćeni tekst (38/09), izmjene (13/04, 14/06) i ciljane izmjene 2013. istoj generaciji, i je li ukidanje kartografskih prikaza ukidanje plana?",
  "dokumenti": [
   D("17702", "MAL-PPU#G1", "L1", [E("17702", "Ovim elaboratom utvrđen je pročišćeni tekst Odluke o donošenju Prostornog plana uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04)", "pročišćeni tekst lanca"),
                                    E("17702", "Odluke o donošenju Izmjena i dopuna Prostornog plana uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 38/09)", "lanac")]),
   D("17701", "MAL-PPU#G1", "L1", [E("17701", "Ovim elaboratom mijenja se i dopunjuje Prostorni plan uređenja Općine Malinska - Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04 i 14/06)", "izmjena plana"),
                                    E("17701", "stavljaju se izvan snage kartografski prikazi Prostornog plana uređenja Općine Malinska - Dubašnica", "ukidanje samo kartografskih prikaza")]),
   D("27012", "MAL-PPU#G1", "L1", [E("27012", "Donose se ciljane Izmjene i dopune Prostornog plana uređenja Općine Malinska-Dubašnica (»Službene novine Primorsko-goranske županije« broj 13/04, 14/06 38/09 i 38/09 - pročišćeni tekst)", "izmjena plana"),
                                    E("27012", "Stupanjem na snagu ovog Plana stavljaju se izvan snage kartografski prikazi Prostornog plana uređenja Općine Malinska-Dubašnica", "ukidanje samo kartografskih prikaza")]),
   D("1876", None, "L3", [E("1876", "Donosi se Prostorni plan uređenja Općine Malinska - Dubašnica, u daljnjem tekstu: Plan.", "osnovni plan, bez broja SN u tekstu")], "MAL-PPU#G1",
     "Vjerojatno osnovna odluka (SN 13/04), ali broj SN nije u tekstu odluke; ostaje kandidat.")],
  "parovi": [
   {"a": "17701", "b": "27012", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "oba izričito mijenjaju plan s lancem SN 13/04, 14/06; nijedan ga ne zamjenjuje"},
   {"a": "17702", "b": "27012", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "isti lanac 13/04, 14/06, 38/09"},
   {"a": "17701", "b": "17702", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "isti lanac 13/04, 14/06"},
   {"a": "27012", "b": "17702", "ocekivanje": "NOT_SUPERSEDED", "razina": "L1", "temelj": "stavljanje izvan snage samo KARTOGRAFSKIH prikaza nije stavljanje plana izvan snage; ne smije dati legal_status SUPERSEDED/REPEALED ni novu generaciju"},
   {"a": "1876", "b": "17701", "ocekivanje": "REVIEW_REQUIRED", "razina": "L3", "temelj": "osnovna odluka nije dokaziva iz teksta"}]},
 {"id": "C2", "opcina": "Vrbnik", "plan": "UPU 1 Vrbnik (NA 1)", "tip": "ISTA_GENERACIJA_PROMJENA_NAZIVA",
  "pitanje": "Je li promjena naziva plana (Odluka 2017.) nova generacija? Nije.",
  "dokumenti": [
   D("36462", "VRB-UPU1#G1", "L1", [E("36462", "Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Urbanističkog plana uređenja naselja Vrbnik (NA 1) s površinama izdvojenih namjena (T i R) - UPU 1 (Službene novine Primorsko-goranske županije broj 33/09)", "izmjena osnovne odluke SN 33/09"),
                                    E("36462", "Naziv plana iz stavka 1. ovog članka mijenja se i glasi", "izričita promjena naziva")]),
   D("39662", "VRB-UPU1#G1", "L1", [E("39662", "Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Urbanističkog plana uređenja UPU 1 Vrbnik - NA 1", "izmjena"), E("39662", "broj 33/09, 35/17 i 2/18-pročišćene odredbe", "lanac")]),
   D("39830", "VRB-UPU1#G1", "L1", [E("39830", "(»Službene novine« Primorsko-goranske županije, broj 33/09, 35/17 i 7/19)", "lanac"),
                                    E("39830", "Elaborat »II. izmjene i dopune Urbanističkog plana uređenja UPU 1 Vrbnik - NA 1« izrađen je u 6", "II. izmjene")], None,
     "Dokument je smjesa odluke i pročišćenog teksta; generacija se odnosi na plan, ne na pojedini dio dokumenta."),
   D("17522", None, "L2", [E("17522", "Donosi se Urbanistički plan uređenja naselja Vrbnik (NA 1) s površinama izdvojenih namjena (T i R) - UPU 1", "osnovni plan; naslov identičan naslovu u citatu 36462")], "VRB-UPU1#G1",
     "Naslov identičan naslovu osnovne odluke iz 36462 (SN 33/09), ali vlastiti broj SN nije u tekstu: L2, ne potvrđeno.")],
  "parovi": [
   {"a": "36462", "b": "39662", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "isti lanac SN 33/09; naziv se razlikuje (stari naziv u 36462 st.1, novi u st.2)"},
   {"a": "39662", "b": "39830", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "isti lanac 33/09, 35/17"},
   {"a": "36462", "b": "39830", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "isti lanac 33/09"},
   {"a": "17522", "b": "36462", "ocekivanje": "REVIEW_REQUIRED", "razina": "L2", "temelj": "identičan naslov, ali broj SN osnovne odluke nije u tekstu 17522"}]},
 {"id": "C3", "opcina": "Vrbnik", "plan": "PPUO Vrbnik", "tip": "ISTA_GENERACIJA_LANAC_IZMJENA",
  "pitanje": "Pripadaju li izmjene PPUO Vrbnik 2007.–2024. istoj generaciji?",
  "dokumenti": [
   D("13407", "VRB-PPU#G1", "L1", [E("13407", "Donose se Izmjene i dopune Prostornog plana uređenja Općine Vrbnik (»Službene novine« broj 16/04)", "izmjena plana SN 16/04")], None, "„u integralnom tekstu” ne znači novu generaciju: kasniji lanci zadržavaju 16/04 kao osnovu."),
   D("35465", "VRB-PPU#G1", "L1", [E("35465", "Donosi se III. Dopuna Prostornog plana uređenja Općine Vrbnik (»Službene novine Primorsko-goranske županije« broj 16/04, 43/07, 53/07-ispravak, 22/16 i 26/16- pročišćeni tekst", "lanac")]),
   D("48254", "VRB-PPU#G1", "L1", [E("48254", "Donosi se Odluka o izmjeni i dopuni Odluke o donošenju Prostornog plana uređenja Općine Vrbnik", "izmjena"), E("48254", "broj 16/04, 43/07, 53/07-ispravak, 22/16, 26/16- pročišćeni tekst, 11/17 i 28/17-pročišćeni tekst, 7/19 i 11/19-pročišćeni tekst", "lanac")]),
   D("34277", None, "L3", [E("34277", "Donose se II. Izmjene i dopune Prostornog plana uređenja Općine Vrbnik", "izmjena bez lanca SN u tekstu")], "VRB-PPU#G1", "Tekst ne navodi lanac SN; kandidat.")],
  "parovi": [
   {"a": "35465", "b": "48254", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "lanac 16/04, 43/07, 53/07, 22/16, 26/16 zajednički"},
   {"a": "13407", "b": "35465", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "osnova SN 16/04 zajednička"},
   {"a": "13407", "b": "48254", "ocekivanje": "SAME_GENERATION", "razina": "L1", "temelj": "osnova SN 16/04 zajednička"},
   {"a": "34277", "b": "35465", "ocekivanje": "REVIEW_REQUIRED", "razina": "L3", "temelj": "34277 ne navodi lanac SN"}]},
 {"id": "C4", "opcina": "Baška", "plan": "UPU-1 Baška (N1-1) i UPU-2 Baška-Zarok (N1-2)", "tip": "RAZLICITI_PLANOVI_ISTI_BROJ_SN",
  "pitanje": "Isti broj SN 24/12 u citatima: isti plan? Ne.",
  "dokumenti": [
   D("36814", "BAS-UPU1#G1", "L1", [E("36814", "usklađuje se Urbanistički plan uređenja UPU-1 Baška (N1-1)", "predmet"), E("36814", "broj 24/12), u nastavku teksta: Plan", "lanac")]),
   D("36815", "BAS-UPU2#G1", "L1", [E("36815", "usklađuje se Urbanistički plan uređenja UPU-2 Baška-Zarok (N1-2)", "predmet"), E("36815", "broj 24/12 i 10/16)", "lanac")]),
   D("24962", None, "L3", [E("24962", "Ovom Odlukom donosi se Urbanistički plan uređenja - 2 - Baška - Zarok (N1-2)", "osnovni plan, bez broja SN u tekstu")], "BAS-UPU2#G1", "Kandidat osnovne odluke UPU-2; SN 24/12 nije u tekstu.")],
  "parovi": [
   {"a": "36814", "b": "36815", "ocekivanje": "DIFFERENT_PLAN", "razina": "L1", "temelj": "isti SN 24/12 u lancu, ali izričito UPU-1 (N1-1) i UPU-2 (N1-2): isti broj glasila nije isti plan"},
   {"a": "24962", "b": "36815", "ocekivanje": "REVIEW_REQUIRED", "razina": "L3", "temelj": "ime i broj plana podudarni, SN osnovne odluke nije u tekstu"}]},
 {"id": "C5", "opcina": "Baška", "plan": "PPUO Općine Baška", "tip": "ZAMKA_DVA_DONOSI_SE_I_DJELOMICNO_UKIDANJE_STAROG_PLANA",
  "pitanje": "Dva teksta 'Donosi se PPUO Baška': dvije generacije? Ukida li novi plan stari u cijelosti?",
  "dokumenti": [
   D("14008", None, "L3", [E("14008", "Donosi se Prostorni plan uređenja Općine Baška, u daljnjem tekstu: Plan.", "donošenje"), E("14008", "u dijelu koji se odnosi na područje Općine Baška", "djelomično ukidanje starog plana")], "BAS-PPU#G1", "Datum odluke 3. 12. 2007."),
   D("25645", None, "L3", [E("25645", "Donosi se Prostorni plan uređenja Općine Baška, u daljnjem tekstu: Plan.", "donošenje"), E("25645", "Stupanjem na snagu Odluke o donošenju Prostornog plana uređenja Općine Baška (»Službene novine Primorsko-goranske županije« br. 1/08) prestaje važiti", "upućuje na SN 1/08 u 3. licu")], "BAS-PPU#G1",
     "Tekst upućuje na odluku iz SN 1/08 u trećem licu: ne može se dokazati je li ovo ista odluka u drugom obliku ili nova.")],
  "parovi": [
   {"a": "14008", "b": "25645", "ocekivanje": "REVIEW_REQUIRED", "razina": "L3", "temelj": "ne smije se automatski označiti ni kao ista ni kao nova generacija"}],
  "pravni_status": [{"subjekt": "Prostorni plan bivše Općine Krk (SN 31/78 ... 4/93)", "ocekivanje": "NOT_FULLY_SUPERSEDED_PARTIAL_BY_AREA", "razina": "L1",
     "dokazi": [E("14008", "u dijelu koji se odnosi na područje Općine Baška", "djelomično"), E("1876", "Donošenjem ovog Plana na području Općine Malinska - Dubašnica prestaje važiti Prostorni plan bivše Općine Krk", "po općini")],
     "temelj": "ukidanje po općini, ne u cijelosti; legal_status ne smije biti globalni SUPERSEDED"}]},
 {"id": "C6", "opcina": "Malinska-Dubašnica", "plan": "UPU 1 Malinska, Radići (GP-1)", "tip": "L1_IZMJENA_I_KANDIDAT_OSNOVE",
  "pitanje": "Pripada li tekst 27287 (2. 4. 2013.) UPU 1 Radići?",
  "dokumenti": [
   D("32729", "MAL-UPU1R#G1", "L1", [E("32729", "Odluke o donošenju Urbanističkog plana uređenja UPU 1 Malinska, Radići (GP-1)", "predmet izmjene"), E("32729", "broj 14/13 i 03/14", "lanac")]),
   D("27287", None, "L3", [E("27287", "1.Građevinsko područje naselja GP-1: Malinska, Radići", "područje u čl. 1; naslov plana nije u izvozu")], "MAL-UPU1R#G1", "Datum 2. 4. 2013. odgovara SN 14/13 samo kronološki; naslov i broj SN nisu u tekstu.")],
  "parovi": [{"a": "27287", "b": "32729", "ocekivanje": "REVIEW_REQUIRED", "razina": "L3", "temelj": "kandidat po području i datumu; nema izričite poveznice"}]},
 {"id": "C7", "opcina": "Vrbnik", "plan": "UPU 11 Risika (NA 2_3) / UPU 2 Risika (NA 2_11)", "tip": "RAZLICITI_PLANOVI_SLICAN_NAZIV",
  "pitanje": "Dva 'UPU naselja Risika': isti plan? Ne.",
  "dokumenti": [
   D("16714", "VRB-UPU11#G1", "L1", [E("16714", "Donosi se Urbanistički plan uređenja naselja Risika (NA 2_3) s površinom izdvojene namjene T2 4 (UPU 11)", "identitet")]),
   D("17523", "VRB-UPU2#G1", "L1", [E("17523", "Donosi se Urbanistički plan uređenja naselja Risika (NA 2_11) s površinama izdvojenih namjena (T2) - UPU 2", "identitet")])],
  "parovi": [{"a": "16714", "b": "17523", "ocekivanje": "DIFFERENT_PLAN", "razina": "L1", "temelj": "isto naselje, različit broj UPU i oznaka NA"}]},
 {"id": "C8", "opcina": "Malinska-Dubašnica", "plan": "DPU Haludovo (SN 30/06, 2/07-ispr.)", "tip": "PRAVNI_STATUS_UKIDANJE_VS_POKRETANJE",
  "pitanje": "Je li DPU Haludovo stavljen izvan snage, a koja odluka je samo pokretanje postupka?",
  "dokumenti": [
   D("46503", "MAL-DPUH#G1", "L1", [E("46503", "Donosi se Odluka o stavljanju izvan snage Odluke o donošenju Detaljnog plana uređenja Haludovo", "ukidanje"), E("46503", "Ova Odluka stupa na snagu osmog dana od dana objave", "stupanje na snagu"), E("46503", "Malinska, 11. svibnja 2023.", "datum")]),
   D("45310", "MAL-DPUH#G1", "L1", [E("45310", "Donosi se Odluka o pokretanju postupka stavljanja izvan snage Detaljnog plana uređenja Haludovo", "samo pokretanje"), E("45310", "Malinska, 15. rujna 2022.", "datum")])],
  "parovi": [],
  "pravni_status": [{"subjekt": "DPU Haludovo (SN 30/06, 2/07-ispr.)", "ocekivanje": "REPEALED", "razina": "L1", "legal_status_as_of": None,
     "napomena_as_of": "Datum objave u SN nije u tekstu; stupanje na snagu osmi dan od objave; datum akta 11. 5. 2023. nije datum stupanja na snagu.",
     "dokazi": [E("46503", "Donosi se Odluka o stavljanju izvan snage Odluke o donošenju Detaljnog plana uređenja Haludovo", "ukidanje")],
     "temelj": "Odluka 45310 (pokretanje postupka) ne ukida plan; to čini tek 46503"}]},
]
def main(izvoz):
    d = json.load(open(izvoz, encoding="utf-8"))
    by = collections.defaultdict(list)
    for a in d["articles"]: by[a["document_id"]].append(a)
    U = {re.search(r"id=(\d+)", x["url"]).group(1): x for x in d["documents"]}
    lose = []
    def prov(ev):
        for a in by[U[ev["odluka_id"]]["id"]]:
            if S.norm(ev["citat"]) in S.norm(re.sub(r"\s+", " ", a["body"])):
                ev["clanak_izvoza"] = a["article_no"]
                ev["sha256_citata"] = hashlib.sha256(S.norm(ev["citat"]).encode()).hexdigest()
                ev["sha256_clanka"] = hashlib.sha256(re.sub(r"\s+", " ", a["body"]).encode()).hexdigest()
                ev["sn_navodi_u_citatu"] = re.findall(r"\b\d{1,2}/\d{2}\b", ev["citat"])
                ev["url"] = "https://www.sn.pgz.hr/default.asp?Link=odluke&id=" + ev["odluka_id"]; return
        lose.append((ev["odluka_id"], ev["citat"][:70]))
    for c in SL:
        for dd in c["dokumenti"]:
            for e in dd["dokazi"]: prov(e)
            dd["url"] = "https://www.sn.pgz.hr/default.asp?Link=odluke&id=" + dd["odluka_id"]
            dd["sn_vlastiti_broj"] = None   # broj glasila same odluke nije u izvozu (samo u izdanju); ne izvodi se
        for ps in c.get("pravni_status", []):
            for e in ps["dokazi"]: prov(e)
    h = hashlib.sha256(json.dumps(SL, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    json.dump({"opis": "Neovisni referentni skup generacija (Baška, Malinska-Dubašnica, Vrbnik). Namijenjen ISKLJUČIVO validaciji; ne koristiti za podešavanje algoritma. Ne mijenja zamrznuti skup krk-plan-identity-v1. Jedan pregledatelj, nije neovisno pravno provjereno.",
               "verzija": 1, "status": "SOURCE_READ_BY_ONE_REVIEWER_NOT_INDEPENDENTLY_VERIFIED", "sha256": h, "promjene": ["v1: prvi popis"],
               "razine": {"L1": "izričita pravna veza u tekstu odluke (citat s lancem SN)", "L2": "posredno (npr. identičan naslov kao u citatu druge odluke)", "L3": "kandidat (naziv/područje/datum)"},
               "ocekivanja_parova": ["SAME_GENERATION", "DIFFERENT_PLAN", "NOT_SUPERSEDED", "REVIEW_REQUIRED"],
               "ograničenje": "Nijedan slučaj nije 'nova generacija zamjenjuje staru': u ove tri općine izvor nema izričit slučaj zamjene cijelog plana. Pozitivni parovi su isključivo ISTA generacija; ovaj skup ne može otkriti algoritam koji sve stavlja u jednu generaciju – to pokrivaju krk-plan-identity-v1 (14783 vs 28241) i negativni slučajevi C1(NOT_SUPERSEDED), C4, C5, C7.",
               "slucajevi": SL}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("problema:", lose); return lose
if __name__ == "__main__": sys.exit(1 if main(sys.argv[1]) else 0)

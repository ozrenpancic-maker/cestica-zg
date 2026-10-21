#!/usr/bin/env python3
"""Referentna analiza (NIJE dio zamrznutog zlatnog skupa identiteta): generacije UPU 1 Krk i devet ACTION_NOT_SUPPORTED slučajeva.
Svaki dokaz je doslovni citat iz teksta odluke u izvozu; skripta provjerava citat, upisuje članak izvoza i sha256 normaliziranog citata.
Razine dokaza generacije: L1 = izričito u tekstu same odluke; L2 = navod u tekstu druge odluke ili nedvosmislena veza imena/popisa; L3 = samo sličnost teksta (ne dokazuje).
Upotreba: gradi_generacije_radnje.py IZVOZ.json -> tests/zlatni/krk-generacije-i-radnje-v1.json"""
import json, os, re, sys, collections, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "krk-generacije-i-radnje-v1.json")
Q = lambda o, c, r="": {"odluka_id": o, "citat": c, "uloga": r}
GEN = [
 {"odluka_id": "14783", "generation_id": "gen-A", "razina": "L1", "dokazano": True,
  "obrazlozenje": "Odluka donosi izmjene i dopune ranijeg UPU-a naselja Krk (SN 17/00, 18/00, 27/03, 17/04); 28241 taj raniji plan (uz 22/08, 23/11, 3/13) izričito stavlja izvan snage. Datum odluke 27. 5. 2008. Njezin točan broj SN (22/08) nije u njezinu tekstu, to je samo podudarnost.",
  "dokazi": [Q("14783", "Ovom Odlukom donose se Izmjene i dopune Urbanističkog plana uređenja naselja Krk (»Službene novine Primorsko-goranske županije« broj 17/00, 18/00, 27/03, 17/04)", "sadržaj"),
             Q("14783", "Krk, 27. svibnja 2008.", "datum"),
             Q("28241", "Stupanjem na snagu ove Odluke stavljaju se izvan snage tekstualni dijelovi i kartografski prikazi Urbanističkog plana uređenja naselja Krk (»SN PGŽ« 17/00, 18/00, 27/03, 17/04, 22/08, 23/11, 3/13)", "ukidanje")]},
 {"odluka_id": "28241", "generation_id": "gen-B", "razina": "L1", "dokazano": True,
  "obrazlozenje": "Odluka (13. 8. 2013.) ukida raniji UPU naselja Krk; time počinje nova generacija. Da je to baš „Odluka o donošenju” nije dokazano iz njezina teksta (nedostaje uvodni dio), nego iz 32508.",
  "dokazi": [Q("28241", "Stupanjem na snagu ove Odluke stavljaju se izvan snage tekstualni dijelovi i kartografski prikazi Urbanističkog plana uređenja naselja Krk", "ukidanje"),
             Q("28241", "Krk, 13. kolovoza 2013.", "datum")]},
 {"odluka_id": "32508", "generation_id": "gen-B", "razina": "L2", "dokazano": True,
  "obrazlozenje": "Odluka o izradi II. izmjena navodi elaborat UPU 1-Krk objavljen u SN 30/13, 40/14, 2/15 (pročišćeni tekst); isti popis područja (NA1, R1-1, R3-8, R3-10, R3-11) kao u 28241/42442. 28241 je iz 2013.; broj SN 30/13 nije u tekstu 28241, veza je preko imena i popisa područja.",
  "dokazi": [Q("32508", "UPU 1-Krk (NA1, R1 1 , R3 8 , R3 10 , R3 11 ) (»Službene novine« broj 30/13, 40/14, 2/15- pročišćeni tekst Odredbi za provođenje", "navod elaborata")]},
 {"odluka_id": "42442", "generation_id": "gen-B", "razina": "L2", "dokazano": True,
  "obrazlozenje": "Sam tekst navodi da je pročišćeni tekst UPU 1 – Krk (NA1, R1 1 , R3 8 , R3 10 , R3 11 ) i poziva se na izmjene SN 11/17 i 18/19 istoga plana pod istim imenom kao u gen-B.",
  "dokazi": [Q("42442", "Nepotrebne prijelazne i završne odredbe su u pročišćenom tekstu izostavljene", "oblik teksta"),
             Q("42442", "Izmjena i dopuna Urbanističkog plana uređenja UPU 1 - Krk (NA1, R11, R38, R310, R311) (»Službene novine Primorsko-goranske županije« broj 18/19)", "izmjene")]},
 {"odluka_id": "35506", "generation_id": "UNDETERMINED", "kandidat": "gen-B", "razina": "L3", "dokazano": False,
  "obrazlozenje": "Tekst ne govori što je (nema uvodnog dijela ni potpisa). Zajednički su: isti navod PPUG (SN 7/07, 41/09, 28/11), isti popis područja u čl. 1, članci 94a/97a. Navodi propise iz 2016. (NN 3/16) pa je kronološki nakon 28241. To je sličnost teksta, ne dokaz generacije.",
  "dokazi": [Q("35506", "razgraničena Prostornim planom uređenja Grada Krka (SN PGŽ 7/07, 41/09 i 28/11)", "navod PPUG")]},
 {"odluka_id": "39364", "generation_id": "UNDETERMINED", "kandidat": "gen-B", "razina": "L3", "dokazano": False,
  "obrazlozenje": "Isto kao 35506; navodi NN 72/17 i 112/17 pa je nakon 2017. Od 35506 se razlikuje u 4 članka.",
  "dokazi": [Q("39364", "razgraničena Prostornim planom uređenja Grada Krka (SN PGŽ 7/ 07, 41/09 i 28/11)", "navod PPUG")]},
]
ACT = [
 {"odluka_id": "46708", "radnja": "AMENDS_REPEAL_PROCEDURE_DECISION", "status": "NEW_NARROW_TYPE", "podradnja": "ADD_PARAGRAPH",
  "opis": "Mijenja ODLUKU O POKRETANJU postupka stavljanja izvan snage dijela UPU 2 Njivice (dodaje stavke). Ne stavlja plan izvan snage i ne mijenja tekst plana.",
  "dokazi": [Q("46708", "U Odluci o pokretanju postupka stavljanja izvan snage dijela UPU 2 – Njivice (NA1)", "radnja"), Q("46708", "u članku 1. dodaje se stavak 3. koji glasi", "operacija")]},
 {"odluka_id": "43829", "radnja": "AMENDS_REPEAL_PROCEDURE_DECISION", "status": "NEW_NARROW_TYPE", "podradnja": "RENAME",
  "opis": "Mijenja samo naziv odluke o pokretanju postupka. Novi naziv sadrži „stavljanju izvan snage”, ali tekst ne dokazuje da je plan stavljen izvan snage.",
  "dokazi": [Q("43829", "mijenja se naziv Odluke te glasi: „Odluka o stavljanju izvan snage dijela Urbanističkog plana uređenja UPU 2 – Njivice (NA 1)“", "operacija")]},
 {"odluka_id": "14783", "radnja": "ADOPTS_AMENDMENTS", "status": "NEW_NARROW_TYPE", "podradnja": "FULL_ARTICLE_SET",
  "opis": "Donosi izmjene i dopune UPU-a naselja Krk (gen-A). Struktura teksta (157 članaka) nije zakrpa po člancima; oblik teksta ostaje UNDETERMINED.",
  "dokazi": [Q("14783", "Ovom Odlukom donose se Izmjene i dopune Urbanističkog plana uređenja naselja Krk", "radnja")]},
 {"odluka_id": "28241", "radnja": "REPEALS_PREVIOUS_PLAN_VERSION", "status": "NEW_NARROW_TYPE", "podradnja": "REPEALS_GEN_A",
  "opis": "Dokazano: stavlja izvan snage raniji UPU naselja Krk. Nedokazano iz vlastitog teksta: da je to odluka o donošenju (nedostaje uvod); ADOPTS ostaje UNPROVEN dok se ne pročita izvorni uvod.",
  "dokazi": [Q("28241", "Stupanjem na snagu ove Odluke stavljaju se izvan snage tekstualni dijelovi i kartografski prikazi Urbanističkog plana uređenja naselja Krk", "radnja")]},
 {"odluka_id": "35506", "radnja": "ACTION_NOT_SUPPORTED", "status": "KEPT", "podradnja": None,
  "opis": "Tekst sam ne navodi kakva je pravna radnja (nema naslova, uvoda, potpisa). Oznaka „pročišćeni tekst” dolazi samo iz heuristike izvoza. Ostaje neodređeno.",
  "dokazi": [Q("35506", "Na području obuhvata Plana ne propisuje se izrada detaljnog plana uređenja", "zadnji članak, bez završnih odredbi")]},
 {"odluka_id": "39364", "radnja": "ACTION_NOT_SUPPORTED", "status": "KEPT", "podradnja": None,
  "opis": "Isto kao 35506.", "dokazi": [Q("39364", "Na području obuhvata Plana ne propisuje se izrada detaljnog plana uređenja", "zadnji članak, bez završnih odredbi")]},
 {"odluka_id": "42442", "radnja": "PUBLISHES_CONSOLIDATED_TEXT", "status": "NEW_NARROW_TYPE", "podradnja": None,
  "opis": "Tekst sam navodi da je pročišćeni tekst (izostavljene su nepotrebne prijelazne i završne odredbe; pročišćeni grafički dio se ne objavljuje u SN). Pročišćeni tekst nije pravni akt koji mijenja plan.",
  "dokazi": [Q("42442", "Nepotrebne prijelazne i završne odredbe su u pročišćenom tekstu izostavljene", "radnja"), Q("42442", "Pročišćeni grafički dio Urbanističkog plana uređenja UPU 1 – Krk", "radnja")]},
 {"odluka_id": "39830", "radnja": "ADOPTS_AMENDMENTS", "status": "NEW_NARROW_TYPE", "podradnja": "MIXED_DOCUMENT_WITH_CONSOLIDATED_TEXT",
  "opis": "Dokument je smjesa: odluka o II. izmjenama i dopunama UPU 1 Vrbnik (čl. 20–22 odluke) + pročišćeni tekst odredbi (članci 5.–159.) + dijelovi ranijih odluka (čl. 137–138 I. izmjena, 164–166). Brojevi članaka se ponavljaju; prije izvođenja pravila treba razdvojiti dijelove. Lanac SN: 33/09, 35/17, 7/19.",
  "dokazi": [Q("39830", "Elaborat »II. izmjene i dopune Urbanističkog plana uređenja UPU 1 Vrbnik - NA 1« izrađen je u 6", "radnja"),
             Q("39830", "Pročišćeni tekst odredbi za provedbu (članci 5. - 159.) Odluke o donošenju Urbanističkog plana uređenja", "pročišćeni tekst"),
             Q("39830", "(»Službene novine« Primorsko-goranske županije, broj 33/09, 35/17 i 7/19)", "lanac SN")]},
 {"odluka_id": "32729", "radnja": "AMENDS_PLAN_ARTICLES", "status": "EXISTING_TYPE_SUFFICIENT", "podradnja": "PER_ARTICLE_PATCH",
  "opis": "Izmjene UPU 1 Malinska, Radići (GP-1) (SN 14/13, 3/14) po člancima. Postojeća vrsta radnje je dovoljna; ne radi parser operacija na razini podstavka (alineje) i stavka ('iza teksta … dodaje se', 'zamjenjuje se novom oznakom').",
  "dokazi": [Q("32729", "U članku 34. Odluke o donošenju Urbanističkog plana uređenja UPU 1 Malinska, Radići (GP-1)", "radnja"), Q("32729", "stavku 1., točki 3., podstavku 3., iza teksta »postojeća visina« dodaje se tekst »(13 metara do vijenca)«", "operacija")]},
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
                ev["clanak_izvoza"] = a["article_no"]; ev["sha256_citata"] = hashlib.sha256(S.norm(ev["citat"]).encode()).hexdigest()
                ev["url"] = "https://www.sn.pgz.hr/default.asp?Link=odluke&id=" + ev["odluka_id"]; return
        lose.append((ev["odluka_id"], ev["citat"][:70]))
    for g in GEN:
        for e in g["dokazi"]: prov(e)
    for a in ACT:
        for e in a["dokazi"]: prov(e)
    # sličnost teksta (L3), neosjetljiva na interpunkciju
    flat = lambda s: re.sub(r"[\W_]+", "", S.norm(s))
    ts = {k: collections.Counter(flat(a["body"]) for a in by[U[k]["id"]]) for k in ("28241", "35506", "39364", "42442")}
    sl = {}
    for a, b in (("28241", "35506"), ("35506", "39364"), ("39364", "42442")):
        sl[a + "->" + b] = {"identicnih_clanaka": sum((ts[a] & ts[b]).values()), "clanaka_prvog": sum(ts[a].values()), "clanaka_drugog": sum(ts[b].values())}
    kron = [{"odluka_id": "14783", "datum": "2008-05-27", "izvor": "tekst"}, {"odluka_id": "28241", "datum": "2013-08-13", "izvor": "tekst"},
            {"odluka_id": "32508", "datum": "2015-07-16", "izvor": "tekst"}, {"odluka_id": "35506", "nakon": "2016 (NN 3/16 u tekstu)", "izvor": "tekst"},
            {"odluka_id": "39364", "nakon": "2017 (NN 72/17, 112/17 u tekstu)", "izvor": "tekst"}, {"odluka_id": "42442", "nakon": "2019 (SN 18/19 u tekstu)", "izvor": "tekst"}]
    ostalo = ["Izmjene SN 40/14 (iz 32508), 11/17 i 18/19 (iz 42442) nisu u izvozu – nedostaju najmanje tri odluke o izmjenama gen-B.", "Točan broj SN za 14783 (22/08?) i 28241 (30/13?) nije u njihovu tekstu; provjeriti u izdanju."]
    h = hashlib.sha256(json.dumps([GEN, ACT], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    json.dump({"opis": "Referentna analiza generacija UPU 1 Krk i devet ACTION_NOT_SUPPORTED slučajeva. NIJE dio zamrznutog skupa krk-plan-identity-v1. Jedan pregledatelj, nije neovisno provjereno.",
               "verzija": 1, "status": "SOURCE_READ_BY_ONE_REVIEWER_NOT_INDEPENDENTLY_VERIFIED", "sha256": h, "plan_family_id": "HR-PGZ-krk-UPU-1",
               "razine_dokaza": {"L1": "izričito u tekstu odluke", "L2": "navod u tekstu druge odluke / ime i popis područja", "L3": "samo sličnost teksta – ne dokazuje"},
               "generacije": GEN, "radnje": ACT, "kronologija": kron, "slicnost_teksta_L3": sl, "otvoreno": ostalo}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("problema:", lose); print(json.dumps(sl)); return lose
if __name__ == "__main__": sys.exit(1 if main(sys.argv[1]) else 0)

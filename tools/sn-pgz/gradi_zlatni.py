#!/usr/bin/env python3
"""Zlatni skup: popis pojedinačnih izmjena II. izmjena UPU 3 Punat (SN PGŽ 3/2020, ID 41087), ručno pročitan
po članku odluke. Svaka stavka ima početak teksta koji mora biti u tom članku odluke u izvornom tekstu.
Upotreba: gradi_zlatni.py TEKST_41087.txt  -> piše tests/zlatni/punat-upu3-2020.json i provjerava početke."""
import json, os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "punat-upu3-2020.json")
Z = "zamjena_cijelog_clanka"; N = "novi_clanak"; BC = "brisanje_clanka"
ZS = "zamjena_stavka"; ZT = "zamjena_tocke"; ZA = "zamjena_alineje"; NS = "novi_stavak"; BS = "brisanje_stavka"
BR = "brisanje_rijeci"; ZR = "zamjena_rijeci"; ZN = "zamjena_naslova"; BN = "brisanje_naslova"; RB = "renumeracija_stavaka"; DEF = "nejasno"
# (clanak_odluke, ciljni_clanak_plana, stavak, tocka, alineja, vrsta, pocetak_teksta)
E = [
 ("3", "3", None, None, None, DEF, "Izrazi i pojmovi koji se upotrebljavaju u smislu ovih Odredbi"),
 ("4", "6", "2", None, "3", ZA, "u članku 6. stavku 2. alineja 3. mijenja se i glasi"),
 ("5", "7", "3", None, None, RB, "U članku 7. stavku 3. brojka: „4“", "4", "3"),
 ("5", "7", "4", None, None, RB, "U stavku 4. brojka: „5“", "5", "4"),
 ("5", "7", "5", None, None, ZS, "Stavak 5. mijenja se i glasi"),
 ("5", "7", "6", None, None, RB, "U stavku 6. brojka: „7“", "7", "6"),
 ("5", "7", "7", None, None, RB, "U stavku 7. brojka: „8“", "8", "7"),
 ("6", "10a", "4", None, None, ZS, "U članku 10a. stavak 4. mijenja se i glasi"),
 ("7", "18", "3", None, None, ZS, "U članku 18. stavak 3. mijenja se i glasi"),
 ("8", "26", "1", None, None, ZS, "U članku 26. stavak 1. mijenja se i glasi"),
 ("8", "26", "7", None, None, NS, "Iza stavka 6. dodaju se novi stavak 7."),
 ("9", "28a", None, None, None, N, "Iza članka 28. dodaje se novi članak 28.a"),
 ("10", "29", "4", None, None, ZS, "U članku 29. stavak 4. mijenja se i glasi"),
 ("10", "29", "5", None, None, ZS, "Stavak 5. mijenja se i glasi"),
 ("11", "43", "5", None, None, BS, "U članku 43. stavak 5. briše se"),
 ("11", "43", "6", None, None, RB, "Stavci 6., 7. i 8. postaju stavci 5., 6. i 7.", "6", "5"),
 ("11", "43", "7", None, None, RB, "Stavci 6., 7. i 8. postaju stavci 5., 6. i 7.", "7", "6"),
 ("11", "43", "8", None, None, RB, "Stavci 6., 7. i 8. postaju stavci 5., 6. i 7.", "8", "7"),
 ("12", "44", None, None, None, Z, "Članak 44. mijenja se i glasi"),
 ("13", "45", "1", None, None, ZS, "U članku 45. stavak 1. mijenja se i glasi"),
 ("13", "45", "5a", None, None, NS, "Iza stavka 5. dodaje se novi stavak 5a"),
 ("13", "45", "12", None, None, ZS, "Stavak 12. mijenja se i glasi"),
 ("13", "45", "19", None, None, NS, "Iza stavka 18. dodaje se novi stavak 19"),
 ("14", "46", None, None, None, Z, "Članak 46. mijenja se i glasi"),
 ("15", "46a", "1", "4", None, ZT, "U članku 46a. stavku 1. točka 4. mijenja se i glasi"),
 ("15", "46a", "1", "6", None, ZT, "U stavku 1. točka 6. mijenja se i glasi"),
 ("15", "46a", "1", "8", None, ZT, "U stavku 1. točka 8. mijenja se i glasi"),
 ("16", "46b", "1", "4", None, ZT, "U članku 46b. stavku 1. točka 4. mijenja se i glasi"),
 ("16", "46b", "1", "6", None, ZT, "U stavku 1. točka 6. mijenja se i glasi"),
 ("16", "46b", "1", "8", "3", ZA, "U stavku 1. točki 8. alineja 3. mijenja se i glasi"),
 ("17", "46c", "1", "4", None, ZT, "U članku 46c. stavku 1. točka 4. mijenja se i glasi"),
 ("17", "46c", "1", "6", None, ZT, "Točka 6. mijenja se i glasi"),
 ("18", "48", None, None, None, Z, "Članak 48. mijenja se i glasi"),
 ("19", "50a", "1", "2", None, ZT, "U članku 50a. stavku 1. točka 2. mijenja se i glasi"),
 ("19", "50a", "1", "4", None, ZT, "U stavku 1. točka 4. mijenja se i glasi"),
 ("20", "50d", "1", None, None, BR, "U članku 50.d stavku 1. riječi"),
 ("21", "58", "5", None, None, NS, "U članku 58. iza stavka 4. dodaje se novi stavak 5."),
 ("22", "59", "3", None, None, ZS, "U članku 59. stavak 3. mijenja se i glasi"),
 ("23", "70", "3", "2", None, ZT, "U članku 70. stavku 3. točka 2. mijenja se i glasi"),
 ("24", "75", None, None, None, ZN, "Naslov iznad članka 75. mijenja se i glasi"),
 ("25", "75", "3", None, None, NS, "U članku 75. dodaje se novi stavak 3."),
  ("25", "75", "3", None, None, RB, "Stavci 3., 4., 5., 6. i 7. postaju stavci 4., 5., 6., 7., i 8.", "3", "4"),
 ("25", "75", "4", None, None, RB, "Stavci 3., 4., 5., 6. i 7. postaju stavci 4., 5., 6., 7., i 8.", "4", "5"),
 ("25", "75", "5", None, None, RB, "Stavci 3., 4., 5., 6. i 7. postaju stavci 4., 5., 6., 7., i 8.", "5", "6"),
 ("25", "75", "6", None, None, RB, "Stavci 3., 4., 5., 6. i 7. postaju stavci 4., 5., 6., 7., i 8.", "6", "7"),
 ("25", "75", "7", None, None, RB, "Stavci 3., 4., 5., 6. i 7. postaju stavci 4., 5., 6., 7., i 8.", "7", "8"),
 ("26", "76", "8", None, None, NS, "U članku 76. iza stavka 7. dodaje se novi stavak 8."),
 ("26", "76", "8", None, None, RB, "Stavak 8. postaje stavak 9.", "8", "9"),
 ("26", "76", "10", None, None, NS, "Iza stavka 9. dodaje se novi stavak 10."),
 ("27", "83", "3", None, None, ZR, "U članku 83. stavku 3. riječi"),
 ("28", "84", "1", None, None, ZR, "U članku 84. stavku 1. riječ"),
 ("29", "85", None, None, None, Z, "Članak 85. mijenja se i glasi"),
 ("30", "85a", "1", "5", None, ZT, "U članku 85a. stavku 1. točka 5. mijenja se i glasi"),
 ("31", "85b", "1", "2", "3", ZA, "U članku 85b. stavku 1. točki 2. alineja 3. mijenja se i glasi"),
 ("31", "85b", "1", "5", None, ZT, "U stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("31", "85b", "1", "6", None, ZT, "U stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("32", "85c", "1", "2", "3", ZA, "U članku 85c. stavku 1. točki 2. alineja 3 mijenja se i glasi"),
 ("32", "85c", "1", "5", None, ZT, "Točke 5. i 6. mijenjaju se i glase"),
 ("32", "85c", "1", "6", None, ZT, "Točke 5. i 6. mijenjaju se i glase"),
 ("33", "85d", "1", "5", None, ZT, "U članku 85d. stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("33", "85d", "1", "6", None, ZT, "U članku 85d. stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("34", "90", "4", None, None, ZS, "U članku 90. stavak 4. mijenja se i glasi"),
 ("35", "91", "3", None, None, NS, "U članku 91. iza stavka 2. dodaju se novi stavci 3. i 4."),
 ("35", "91", "4", None, None, NS, "U članku 91. iza stavka 2. dodaju se novi stavci 3. i 4."),
 ("36", "99", None, None, None, Z, "Članak 99. mijenja se i glasi"),
 ("37", "99e", None, None, None, Z, "Članak 99e. mijenja se i glasi"),
 ("38", "100", None, None, None, BN, "Naslov iznad članka 100. i članak 100. brišu se"),
 ("38", "100", None, None, None, BC, "Naslov iznad članka 100. i članak 100. brišu se"),
 ("39", "101", None, None, None, BN, "Naslov iznad članka 101. briše se"),
]
UCINAK = {Z: ("REPLACE", "CLANAK"), N: ("ADD", "CLANAK"), BC: ("DELETE", "CLANAK"), ZS: ("REPLACE", "STAVAK"), ZT: ("REPLACE", "TOCKA"),
          ZA: ("REPLACE", "ALINEJA"), NS: ("ADD", "STAVAK"), BS: ("DELETE", "STAVAK"), BR: ("DELETE", "RIJECI"), ZR: ("REPLACE", "RIJECI"),
          ZN: ("REPLACE", "NASLOV"), BN: ("DELETE", "NASLOV"), RB: ("RENUMBER", "STAVAK"), DEF: ("NEJASNO", "CLANAK")}
INSERT_AFTER = {"Iza stavka 6. dodaju se novi stavak 7.": "stavak 6", "Iza članka 28. dodaje se novi članak 28.a": "članak 28",
                "Iza stavka 5. dodaje se novi stavak 5a": "stavak 5", "Iza stavka 18. dodaje se novi stavak 19": "stavak 18",
                "U članku 58. iza stavka 4. dodaje se novi stavak 5.": "stavak 4", "U članku 76. iza stavka 7. dodaje se novi stavak 8.": "stavak 7",
                "Iza stavka 9. dodaje se novi stavak 10.": "stavak 9", "U članku 91. iza stavka 2. dodaju se novi stavci 3. i 4.": "stavak 2"}
VERZIJA = 2
PROMJENE = ["v1 (58 izmjena): prvi popis; 8 izmjena dodano nakon što ih je pronašao tuđi parser (čl. 26/7, 29/5, 45/5a, 45/12, 45/19, 75 renumeracija, 76/8→9, 76/10).",
            "v2 (%d izmjena): rasponi ('3-7', '6-8', '5-6', '3-4') rastavljeni na pojedinačne događaje; čl. 100 podijeljen na brisanje naslova i brisanje članka; dodana polja ucinak (ADD/REPLACE/DELETE/RENUMBER), razina, insert_after, stara_oznaka/nova_oznaka. Sadržaj izmjena nije mijenjan."]
def main(tekst):
    C = {c["clanak"]: S.norm(c["tekst"]) for c in S.clanci(S.u_tekst(tekst))}
    lose = []; out = []
    for i, e in enumerate(E, 1):
        co, cp, st, to, al, vr, po = e[:7]; stara, nova = (e[7], e[8]) if len(e) > 7 else (None, None)
        if S.norm(po) not in C.get(co, ""): lose.append((i, co, po))
        uc, raz = UCINAK[vr]
        x = {"id": "z2020-%02d" % i, "odluka_id": 41087, "clanak_odluke": co, "ciljni_clanak_plana": cp, "stavak": st, "tocka": to, "alineja": al,
             "ucinak": uc, "razina": raz, "vrsta": vr, "pocetak_teksta": po}
        if po in INSERT_AFTER: x["insert_after"] = INSERT_AFTER[po]
        if stara: x["stara_oznaka"], x["nova_oznaka"] = stara, nova
        out.append(x)
    PR = list(PROMJENE); PR[1] = PR[1] % len(out)
    h = hashlib.sha256(json.dumps(out, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    json.dump({"opis": "Zlatni skup: pojedinačne izmjene II. izmjena UPU 3 Punat (SN PGŽ 3/2020), ručno pročitane po članku odluke. Članak 3. odluke („Izrazi i pojmovi”) pravni učinak nije jasan iz teksta (ucinak NEJASNO, ne ulazi u mjerenje). Skup je ZAMRZNUT od verzije 2: izmjena samo uz dokaz iz izvornog teksta i unos u promjene.",
               "verzija": VERZIJA, "sha256_izmjena": h, "promjene": PR, "status": "SOURCE_READ_BY_ONE_REVIEWER_NOT_INDEPENDENTLY_VERIFIED",
               "izvor": "https://www.sn.pgz.hr/default.asp?Link=odluke&id=41087", "broj_izmjena": len(out), "izmjene": out},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("izmjena:", len(out), "početaka koji nisu u članku:", lose); return lose
if __name__ == "__main__":
    sys.exit(1 if main(open(sys.argv[1], encoding="utf-8").read()) else 0)

#!/usr/bin/env python3
"""Zlatni skup: popis pojedinačnih izmjena II. izmjena UPU 3 Punat (SN PGŽ 3/2020, ID 41087), ručno pročitan
po članku odluke. Svaka stavka ima početak teksta koji mora biti u tom članku odluke u izvornom tekstu.
Upotreba: gradi_zlatni.py TEKST_41087.txt  -> piše tests/zlatni/punat-upu3-2020.json i provjerava početke."""
import json, os, sys
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
 ("5", "7", "3", None, None, RB, "U članku 7. stavku 3. brojka: „4“"),
 ("5", "7", "4", None, None, RB, "U stavku 4. brojka: „5“"),
 ("5", "7", "5", None, None, ZS, "Stavak 5. mijenja se i glasi"),
 ("5", "7", "6", None, None, RB, "U stavku 6. brojka: „7“"),
 ("5", "7", "7", None, None, RB, "U stavku 7. brojka: „8“"),
 ("6", "10a", "4", None, None, ZS, "U članku 10a. stavak 4. mijenja se i glasi"),
 ("7", "18", "3", None, None, ZS, "U članku 18. stavak 3. mijenja se i glasi"),
 ("8", "26", "1", None, None, ZS, "U članku 26. stavak 1. mijenja se i glasi"),
 ("9", "28a", None, None, None, N, "Iza članka 28. dodaje se novi članak 28.a"),
 ("10", "29", "4", None, None, ZS, "U članku 29. stavak 4. mijenja se i glasi"),
 ("11", "43", "5", None, None, BS, "U članku 43. stavak 5. briše se"),
 ("11", "43", "6-8", None, None, RB, "Stavci 6., 7. i 8. postaju stavci 5., 6. i 7."),
 ("12", "44", None, None, None, Z, "Članak 44. mijenja se i glasi"),
 ("13", "45", "1", None, None, ZS, "U članku 45. stavak 1. mijenja se i glasi"),
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
 ("26", "76", "8", None, None, NS, "U članku 76. iza stavka 7. dodaje se novi stavak 8."),
 ("27", "83", "3", None, None, ZR, "U članku 83. stavku 3. riječi"),
 ("28", "84", "1", None, None, ZR, "U članku 84. stavku 1. riječ"),
 ("29", "85", None, None, None, Z, "Članak 85. mijenja se i glasi"),
 ("30", "85a", "1", "5", None, ZT, "U članku 85a. stavku 1. točka 5. mijenja se i glasi"),
 ("31", "85b", "1", "2", "3", ZA, "U članku 85b. stavku 1. točki 2. alineja 3. mijenja se i glasi"),
 ("31", "85b", "1", "5-6", None, ZT, "U stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("32", "85c", "1", "2", "3", ZA, "U članku 85c. stavku 1. točki 2. alineja 3 mijenja se i glasi"),
 ("32", "85c", "1", "5-6", None, ZT, "Točke 5. i 6. mijenjaju se i glase"),
 ("33", "85d", "1", "5-6", None, ZT, "U članku 85d. stavku 1. točke 5. i 6. mijenjaju se i glase"),
 ("34", "90", "4", None, None, ZS, "U članku 90. stavak 4. mijenja se i glasi"),
 ("35", "91", "3-4", None, None, NS, "U članku 91. iza stavka 2. dodaju se novi stavci 3. i 4."),
 ("36", "99", None, None, None, Z, "Članak 99. mijenja se i glasi"),
 ("37", "99e", None, None, None, Z, "Članak 99e. mijenja se i glasi"),
 ("38", "100", None, None, None, BC, "Naslov iznad članka 100. i članak 100. brišu se"),
 ("39", "101", None, None, None, BN, "Naslov iznad članka 101. briše se"),
]
def main(tekst):
    C = {c["clanak"]: S.norm(c["tekst"]) for c in S.clanci(S.u_tekst(tekst))}
    lose = []; out = []
    for i, (co, cp, st, to, al, vr, po) in enumerate(E, 1):
        if S.norm(po) not in C.get(co, ""): lose.append((i, co, po))
        out.append({"id": "z2020-%02d" % i, "odluka_id": 41087, "clanak_odluke": co, "ciljni_clanak_plana": cp, "stavak": st, "tocka": to, "alineja": al, "vrsta": vr, "pocetak_teksta": po})
    json.dump({"opis": "Zlatni skup: pojedinačne izmjene II. izmjena UPU 3 Punat (SN PGŽ 3/2020), ručno pročitane po članku odluke. Članak 3. odluke („Izrazi i pojmovi”) pravni učinak nije jasan iz teksta (vrsta „nejasno”).",
               "izvor": "https://www.sn.pgz.hr/default.asp?Link=odluke&id=41087", "broj_izmjena": len(out), "izmjene": out},
              open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("izmjena:", len(out), "početaka koji nisu u članku:", lose); return lose
if __name__ == "__main__":
    sys.exit(1 if main(open(sys.argv[1], encoding="utf-8").read()) else 0)

#!/usr/bin/env python3
"""Zlatni skup: izmjene UPU 3 Punat iz SN PGŽ 13/2016 (ID 33933), SASTAVLJEN PRIJE mjerenja bilo kojeg parsera.
Izvor teksta: izvoz treće strane (ChatGPT program), NIJE uspoređen sa sn.pgz.hr; numeracija članaka odluke u izvozu nepouzdana,
pa se događaji vežu uz članak PLANA i početak izvornog teksta. Status: SOURCE_NOT_INDEPENDENTLY_VERIFIED.
Upotreba: gradi_zlatni_2016.py TEKST_33933.txt"""
import json, os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sn_pgz as S
import verzije as V
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tests", "zlatni", "punat-upu3-2016.json")
E = []
def e(cilj, uc, raz, poc, st=None, to=None, al=None, ins=None):
    E.append((cilj, st, to, al, uc, raz, poc, ins))
def art(cilj, poc): e(cilj, "REPLACE", "CLANAK", poc)
# ---- uvodni članci
e("1", "ADD", "STAVAK", "u članku 1. dodaje se stavak 3. koji glasi", st="3", ins="stavak 2")
e("2", "REPLACE", "POGLAVLJE", "U članku 2. mijenja se poglavlje KNJIGA 2")
art("3", "Članak 3. mijenja se i glasi")
e("4", "DELETE", "TEKST", "U članku 4. stavku 2. briše se tekst", st="2")
e("5", "REPLACE", "TOCKA", "članak 5. stavku 1. točka 4. mijenja se i glasi", st="1", to="4")
e("7", "REPLACE", "RIJECI", "U članku 7. stavku 2. riječ »lokalnog« zamijenjuje se", st="2")
e("7", "DELETE", "STAVAK", "Stavak 3. briše se. Članak 7.", st="3")
e("8", "REPLACE", "RIJECI", "U članku 8. stavku 3. riječi »poglavljem 6.« zamijenjuje se", st="3")
e("10", "REPLACE", "PODNASLOV", "Podnaslov članka 10. i članak 10. mijenja se i glasi"); art("10", "Podnaslov članka 10. i članak 10. mijenja se i glasi")
e("10a", "ADD", "PODNASLOV", "Dodaje se novi podnaslov i članak 10a. koji glasi"); e("10a", "ADD", "CLANAK", "Dodaje se novi podnaslov i članak 10a. koji glasi")
e("11", "ADD", "PODNASLOV", "Iznad podnaslova »Zone mješovite - pretežito stambene namjene (M1)« članka 11. dodaje se novi podnaslov")
for s in ("1", "4", "6"): e("11", "REPLACE", "STAVAK", "U članku 11. mijenjaju se stavci 1., 4. i 6. koji glase", st=s)
for s in ("1", "4", "5"): e("12", "REPLACE", "STAVAK", "U članku 12. mijenjaju se stavci 1., 4. i 5. koji glase", st=s)
for s in ("2", "3"): e("13", "REPLACE", "STAVAK", "U članku 13. mijenjaju se stavci 2. i 3. koji glase", st=s)
e("18", "DELETE", "POGLAVLJE", "Poglavlje »2.1. NEPOSREDNO PROVOĐENJE PLANA« u članku 18. briše se")
for s in ("3", "4"): e("18", "REPLACE", "STAVAK", "U članku 18. stavak 3. i 4. mijenja se i glasi", st=s)
e("19", "REPLACE", "STAVAK", "U članku 19. stavak 1. mijenja se i glasi", st="1")
e("20", "REPLACE", "PODNASLOV", "Podnaslov članka 20. mijenja se i glasi")
for s in ("1", "4", "5"): e("20", "REPLACE", "STAVAK", "U članku 20. stavci 1., 4. i 5. mijenjaju se i glase", st=s)
e("20a", "ADD", "PODNASLOV", "Dodaje se novi podnaslov i članak 20a. koji glasi"); e("20a", "ADD", "CLANAK", "Dodaje se novi podnaslov i članak 20a. koji glasi")
for n in ("21", "22", "23"): art(n, "Članak %s. mijenja se i glasi" % n)
e("24", "REPLACE", "PODNASLOV", "Podnaslov i članak 24. mijenja se i glasi"); art("24", "Podnaslov i članak 24. mijenja se i glasi")
art("25", "Članak 25. mijenja se i glasi"); art("26", "Članak 26. mijenja se i glasi")
e("29", "REPLACE", "TOCKA", "članak 29. stavku 4. točka 1. mijenja se i glasi", st="4", to="1")
e("29", "REPLACE", "TOCKA", "U stavku 5. točka 1. mijenja se i glasi", st="5", to="1")
e("30", "REPLACE", "STAVAK", "U članku 30. stavak 2. mijenja se i glasi", st="2")
e("31", "NEJASNO", "NASLOV", "Naslov i podnaslov članka 31. kao i")
e("32", "DELETE", "PODNASLOV", "Podnaslov članka 32. »3.1 NEPOSREDNO PROVOĐENJE PLANA« briše se")
art("36", "Članak 36. mijenja se i glasi")
e("38", "REPLACE", "PODNASLOV", "Podnaslov članak 38. mijenja se i glasi")
e("38", "ADD", "STAVAK", "U članku 38. dodaje se stavak 4. koji glasi", st="4")
art("40", "Članak 40. mijenja se i glasi"); art("41", "Članak 41. mijenja se i glasi")
e("42", "REPLACE", "STAVAK", "U članku 42. stavak 3. mijenja se i glasi", st="3")
e("43", "DELETE", "POGLAVLJE", "Poglavlje »4.1. NEPOSREDNO PROVOĐENJE« u članku 43. briše se")
art("43", "Članak 43. mijenja se i glasi"); art("44", "Članak 44. mijenja se i glasi")
e("45", "REPLACE", "PODNASLOV", "Podnaslov i članak 45. mijenja se i glasi"); art("45", "Podnaslov i članak 45. mijenja se i glasi")
e("46", "REPLACE", "PODNASLOV", "Podnaslov članak 46. mijenja se i glasi")
for s in ("1", "2"): e("46", "DELETE", "STAVAK", "U članku 46. stavak 1. i 2. brišu se", st=s)
for n in ("46a", "46b", "46c"): e(n, "ADD", "CLANAK", "Iz članka 46. dodaju se novi članci 46a., 46b. i 46c. koji glase", ins="članak 46")
e("49", "REPLACE", "PODNASLOV", "Podnaslov iznad članka 49. mijenja se i glasi")
e("50", "NEJASNO", "PODNASLOV", "Podnaslov članka 50. i")
for n in ("50a", "50b", "50c", "50d", "50e"): e(n, "ADD", "CLANAK", "Dodaju se novi podnaslovi i članci 50a., 50b., 50c., 50d. i 50e. koji glase", ins="članak 50")
e("51", "REPLACE", "PODNASLOV", "Podnaslov članka 51. i članak 51. mijenja se i glasi"); art("51", "Podnaslov članka 51. i članak 51. mijenja se i glasi")
for s in ("2", "3"): e("52", "REPLACE", "STAVAK", "U članku 52. stavak 2. i 3. mijenjaju se i glase", st=s)
for n in ("53", "54", "54a", "54b"): art(n, "Članak %s. mijenja se i glasi" % n)
for n in ("54c", "54d", "54e"): e(n, "ADD", "CLANAK", "Iza članka 54b. dodaju se novi podnaslovi i članci 54c., 54d. i 54e. koji glase", ins="članak 54b")
e("62", "ADD", "TEKST", "U članku 62. stavku 7. iza teksta", st="7")
e("65", "REPLACE", "STAVAK", "U članku 65. stavak 3. mijenja se i glasi", st="3")
art("67", "Članak 67. mijenja se i glasi")
e("68", "REPLACE", "STAVAK", "U članku 68. stavak 1. mijenja se i glasi", st="1")
art("70", "Članak 70. mijenja se i glasi")
e("74", "DELETE", "STAVAK", "U članku 74. stavak 3. briše se", st="3")
art("75", "Članak 75. mijenja se i glasi")
for s in ("2", "3"): e("76", "REPLACE", "STAVAK", "U članku 76. mijenjaju se stavci 2. i 3. te sada glase", st=s)
e("80", "REPLACE", "STAVAK", "U članku 80. stavak 1. mijenja se i glasi", st="1")
e("85", "REPLACE", "PODNASLOV", "Podnaslov članka 85. i članak 85. mijenja se i glasi"); art("85", "Podnaslov članka 85. i članak 85. mijenja se i glasi")
for n in ("85a", "85b", "85c", "85d"): e(n, "ADD", "CLANAK", "Iza članka 85. dodaju se novi članci 85a., 85b., 85c. i 85d. koji glase", ins="članak 85")
art("89", "Članak 89. mijenja se i glasi")
e("90", "ADD", "STAVAK", "U članku 90. dodaje se novi stavak 4. koji glasi", st="4")
e("91", "REPLACE", "STAVAK", "U članku 91. stavak 1. mijenja se i glasi", st="1")
art("98", "Članak 98. mijenja se i glasi")
for n in ("99a", "99b", "99c", "99d", "99e"): e(n, "ADD", "CLANAK", "Iza članka 99. dodaju se novi podnaslovi i članci 99a., 99b., 99c, 99d. i 99e. koji glase", ins="članak 99")
art("100", "Članak 100. mijenja se i glasi")
e("101", "ADD", "PODNASLOV", "Dodaje se novi podnaslov i članak 101. koji glasi"); e("101", "ADD", "CLANAK", "Dodaje se novi podnaslov i članak 101. koji glasi")

def main(tekst):
    n = S.norm(tekst); bl = V.blokovi(tekst); lose = []; out = []
    ima = {b["clanak"] for b in bl if b["vrsta"] in ("zamjena", "novi", "zamjena_ili_novi")}
    for i, (cilj, st, to, al, uc, raz, poc, ins) in enumerate(E, 1):
        if S.norm(poc) not in n: lose.append((i, cilj, "početak teksta nije u odluci", poc))
        if raz == "CLANAK" and uc in ("ADD", "REPLACE") and cilj not in ima and not poc.startswith("Podnaslov"): lose.append((i, cilj, "nema bloka članka plana", poc))
        x = {"id": "z2016-%03d" % i, "odluka_id": 33933, "clanak_odluke": None, "ciljni_clanak_plana": cilj, "stavak": st, "tocka": to, "alineja": al,
             "ucinak": uc, "razina": raz, "pocetak_teksta": poc, "status": "SOURCE_NOT_INDEPENDENTLY_VERIFIED"}
        if ins: x["insert_after"] = ins
        out.append(x)
    h = hashlib.sha256(json.dumps(out, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    json.dump({"opis": "Zlatni skup izmjena UPU 3 Punat iz SN PGŽ 13/2016, sastavljen PRIJE mjerenja ijednog parsera. Tekst potječe iz izvoza treće strane i nije uspoređen sa sn.pgz.hr; numeracija članaka odluke u izvozu je nepouzdana (clanak_odluke = null). Podnaslovi koji se dodaju uz nove članke 50a–50e, 54c–54e, 85a–85d, 99a–99e ne vode se zasebno; ucinak NEJASNO ne ulazi u mjerenje (čl. 31 naslov/podnaslov i podnaslov čl. 50: tekst izvoza je pomiješan).",
               "verzija": 1, "sha256_izmjena": h, "promjene": ["v1: prvi popis, sastavljen iz teksta bez pokretanja ijednog parsera nad njim."],
               "status": "SOURCE_NOT_INDEPENDENTLY_VERIFIED", "izvor": "https://www.sn.pgz.hr/default.asp?Link=odluke&id=33933",
               "broj_izmjena": len(out), "izmjene": out}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("izmjena:", len(out), "nejasnih:", sum(1 for x in out if x["ucinak"] == "NEJASNO"), "problema:", lose); return lose
if __name__ == "__main__":
    sys.exit(1 if main(open(sys.argv[1], encoding="utf-8").read()) else 0)

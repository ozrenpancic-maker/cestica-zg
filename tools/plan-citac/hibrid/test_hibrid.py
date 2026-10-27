#!/usr/bin/env python3
"""Testovi hibridnog čitača v1 (provjera i usporedba) na sintetičkim primjerima. Pokretanje: python3 hibrid/test_hibrid.py"""
import sys
from pathlib import Path
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent)); sys.path.insert(0, str(H.parent / "oznake/v1")); sys.path.insert(0, str(H))
import provjera as P
import usporedba as UH

ART = {"broj": 24, "naslov": "Zona T1 1 - hotel",
       "tekst": "Na površini (T1 1) dopušteno je graditi hotel uz slijedeće granične uvjete: - Najveći dopušteni koeficijent izgrađenosti (kig) iznosi 0,3. "
                "- Najveći dopušteni broj etaža je 4, ali dozvoljene su najviše 2 nadzemne etaže. "
                "- Najmanja dopuštena udaljenost nadzemnog dijela građevine od regulacijskog pravca iznosi 10 metara, odnosno 4 metra od ostalih ulica."}


def kand(**kw):
    k = {"clanak": 24, "stavak": None, "tocka": "-", "alineja_rb": 1, "citat": "Najveći dopušteni koeficijent izgrađenosti (kig) iznosi 0,3",
         "parametar": "najveći koeficijent izgrađenosti (kig)", "operator": "<=", "vrijednost": 0.3, "jedinica": "koeficijent",
         "vrsta_gradevine": {"naziv": "hotel", "izraz": "hotel", "citat_izraza": "dopušteno je graditi hotel", "izvor": "uvod_clanka"},
         "nacin_gradnje": None, "stanje": None, "zona": {"oznake": ["T1 1"], "citat": "(T1 1)"}, "uvjeti": [], "iznimke": [],
         "vrsta_pravila": "OSNOVNO", "nejasno": None}
    k.update(kw)
    return k


def kodovi(k):
    return {c for c, _ in P.provjeri(k, ART)[1]}


T = []
t = lambda f: T.append(f) or f


@t
def nedoslovni_citat_odbijen():
    assert P.provjeri(kand(citat="koeficijent izgrađenosti iznosi 0,3 (kig)"), ART)[0] == "ODBIJEN"


@t
def vrijednost_izvan_citata_odbijena():
    assert P.provjeri(kand(vrijednost=0.4), ART)[0] == "ODBIJEN"


@t
def kig_bez_razloga_tehnicki_provjeren():
    assert not (kodovi(kand()) & P.TEHNICKI)


@t
def pogresan_operator():
    assert "OPERATOR_NEPOTVRDEN" in kodovi(kand(operator=">="))


@t
def etaze_nadzemne_na_pregled():
    k = kand(citat="Najveći dopušteni broj etaža je 4, ali dozvoljene su najviše 2 nadzemne etaže", parametar="najveći broj etaža",
             vrijednost=2, jedinica=None, uvjeti=[{"tekst": "nadzemne etaže", "citat": "nadzemne etaže", "izvor": "odredba"}], vrsta_pravila="UVJETNO")
    assert "ETAZE_NADZEMNE" in kodovi(k)


@t
def citat_dio_recenice():
    k = kand(citat="odnosno 4 metra od ostalih ulica", parametar="najmanja udaljenost od regulacijskog pravca", operator=">=", vrijednost=4, jedinica="m",
             uvjeti=[{"tekst": "od ostalih ulica", "citat": "od ostalih ulica", "izvor": "odredba"}], vrsta_pravila="UVJETNO")
    assert "CITAT_DIO_RECENICE" in kodovi(k)


@t
def ai_nejasno_ide_na_pregled():
    assert "AI_NEJASNO" in kodovi(kand(nejasno="TUMACENJE: test"))


@t
def stanje_postojece_iz_uvoda():
    k = kand(vrsta_gradevine={"naziv": "hotel (postojeći)", "izraz": "hotel", "citat_izraza": "dopušteno je graditi hotel", "izvor": "uvod_clanka"}, stanje="postojeća")
    st, R = P.provjeri(k, ART)
    assert st != "AUTOMATSKI_PRIHVACEN", R


ART2 = {"broj": 22, "naslov": None,
        "tekst": "(1) Utvrđuju se slijedeće granične vrijednosti za izgradnju obiteljske kuće: a) najmanja dopuštena površina građevne čestice za izgradnju "
                 "obiteljske kuće iznosi: - za slobodnostojeće građevine: 500 m 2 - za dvojne i ugrađene građevine: 300 m 2 c) najmanja dopuštena površina "
                 "tlocrtne projekcije nove obiteljske kuće iznosi 100 m 2 za sve tipove gradnje; "
                 "(2) Poljoprivredne gospodarske građevine mogu se graditi na građevnoj čestici uz obiteljsku kuću uz poštivanje sljedećih uvjeta: "
                 "- najmanja udaljenost od granice građevne čestice iznosi 4,0 m, - krovišta mogu biti ravna."}


@t
def tocka_alineja_unutar_tocke():
    k = {"clanak": 22, "stavak": 1, "citat": "najmanja dopuštena površina građevne čestice za izgradnju obiteljske kuće iznosi: - za slobodnostojeće građevine: 500 m 2",
         "vrijednost": 500}
    assert P.provjeri_sve([k], {22: ART2})[0]["_tocka"] == "-"


@t
def uvjet_uvoda_nepotpun():
    k = {"clanak": 22, "stavak": 2, "tocka": "-", "citat": "najmanja udaljenost od granice građevne čestice iznosi 4,0 m", "parametar": "najmanja udaljenost od granice građevne čestice",
         "operator": ">=", "vrijednost": 4.0, "jedinica": "m", "vrsta_gradevine": {"naziv": "poljoprivredna gospodarska građevina", "izraz": "Poljoprivredne gospodarske građevine",
         "citat_izraza": "Poljoprivredne gospodarske građevine mogu se graditi", "izvor": "uvod_stavka"}, "zona": {"oznake": [], "citat": None},
         "uvjeti": [{"tekst": "uz obiteljsku kuću", "citat": "uz obiteljsku kuću", "izvor": "uvod"}], "iznimke": [], "vrsta_pravila": "OSNOVNO", "nejasno": None}
    assert "UVJET_UVODA_NEPOTPUN" in {c for c, _ in P.provjeri(k, ART2)[1]}
    k["uvjeti"] = [{"tekst": "na građevnoj čestici uz obiteljsku kuću", "citat": "na građevnoj čestici uz obiteljsku kuću", "izvor": "uvod"}]
    assert "UVJET_UVODA_NEPOTPUN" not in {c for c, _ in P.provjeri(k, ART2)[1]}


@t
def odlomak_za_iza_vrijednosti():
    k = {"clanak": 22, "stavak": 1, "tocka": "c", "citat": "najmanja dopuštena površina tlocrtne projekcije nove obiteljske kuće iznosi 100 m 2 za sve tipove gradnje",
         "parametar": "najmanja površina tlocrtne projekcije građevine", "operator": ">=", "vrijednost": 100, "jedinica": "m²",
         "vrsta_gradevine": {"naziv": "obiteljska kuća (nova)", "izraz": "obiteljske kuće", "citat_izraza": "nove obiteljske kuće", "izvor": "odredba"},
         "zona": {"oznake": [], "citat": None}, "uvjeti": [], "iznimke": [], "vrsta_pravila": "OSNOVNO", "nejasno": None}
    assert "UVJET_IZGUBLJEN" in {c for c, _ in P.provjeri(k, ART2)[1]}


def zapis(**kw):
    z = {"id": "X", "clanak": 24, "stavak": None, "tocka": "-", "parametar": "najveći koeficijent iskoristivosti (kis) (uz podrum ili ukupni)", "operator": "<=",
         "vrijednost": 1.5, "jedinica": "koeficijent", "vrsta_gradevine": "hotel", "vrsta_pravila": "OSNOVNO", "uvjet_tekst": "", "uvjet_konteksta": "", "prihvacen": True}
    z.update(kw)
    return z


@t
def usporedba_tocka_semanticki():
    c, o = zapis(tocka=None), dict(zapis(), uvjet_primjene=None)
    assert "tocka" in UH.razlike(c, o, "strogo") and not UH.razlike(c, o, "semanticki")


@t
def usporedba_vrijednost_nikad_semanticki():
    c, o = zapis(vrijednost=1.0), dict(zapis(), uvjet_primjene=None)
    assert "vrijednost" in UH.razlike(c, o, "semanticki")


@t
def usporedba_uvjet_mora_biti_pokriven():
    c, o = zapis(), dict(zapis(), uvjet_primjene="ukoliko se gradi podrum")
    assert "uvjet" in UH.razlike(c, o, "semanticki")
    assert not UH.razlike(zapis(uvjet_tekst="ukoliko se gradi podrum"), o, "semanticki")


@t
def usporedba_suvisni_uvjet():
    assert "uvjet" in UH.razlike(zapis(uvjet_tekst="nadzemne etaže"), dict(zapis(), uvjet_primjene=None), "semanticki")


@t
def usporedba_stanje_vrste():
    assert "vrsta_gradevine" in UH.razlike(zapis(vrsta_gradevine="hotel (postojeći)"), dict(zapis(), uvjet_primjene=None), "semanticki")


@t
def pogresno_prihvaceni_brojeni():
    s, D = UH.usporedi([zapis(vrijednost=9.9)], [dict(zapis(), uvjet_primjene=None, jednoznacnost="JASAN")], "semanticki")
    assert s["pogresno_prihvaceno"] == 1 and s["propusteno"] == 1


if __name__ == "__main__":
    bad = 0
    for f in T:
        try:
            f(); print("OK  ", f.__name__)
        except AssertionError as e:
            bad += 1; print("FAIL", f.__name__, e)
    print(f"{len(T) - bad}/{len(T)}")
    sys.exit(1 if bad else 0)

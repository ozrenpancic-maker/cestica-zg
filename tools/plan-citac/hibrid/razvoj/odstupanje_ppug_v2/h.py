import re, json, os
D = os.path.dirname(os.path.abspath(__file__))
T = open(os.path.join(D, 'tekst.txt'), encoding='utf-8').read()
ART = {}
for m in re.finditer(r'Članak (\d+)\.\n(.*?)(?=\n\nČlanak |\Z)', T, re.S):
    ART[int(m.group(1))] = m.group(2)
OUT = []
ERR = []
PZ = "unutar registriranih i evidentiranih povijesnih graditeljskih cjelina"

def chk(cl, s, what):
    if s is not None and s not in ART[cl]:
        ERR.append((cl, what, s))

def K(cl, st, to, al, cit, par, op, val, jed, vg, nac=None, stn=None, zona=None, uv=(), izn=(), nej=None):
    chk(cl, cit, 'citat')
    naziv, izraz, ciz, izv = vg
    chk(cl, ciz, 'citat_izraza')
    if izraz not in ciz: ERR.append((cl, 'izraz', izraz))
    z = {"oznake": [], "citat": None}
    if zona:
        z = {"oznake": zona[0], "citat": zona[1]}; chk(cl, zona[1], 'zona')
    uvl = []
    for t, i in uv:
        chk(cl, t, 'uvjet'); uvl.append({"tekst": t, "citat": t, "izvor": i})
    izl = []
    for t in izn:
        chk(cl, t, 'iznimka'); izl.append({"tekst": t, "citat": t})
    if op == 'zabrana': vp = 'NEGATIVNO'
    elif izl: vp = 'IZNIMKA'
    elif any(u['izvor'] == 'odredba' for u in uvl): vp = 'UVJETNO'
    else: vp = 'OSNOVNO'
    d = {"clanak": cl, "stavak": st, "tocka": to, "alineja_rb": al, "citat": cit, "parametar": par,
         "operator": op, "vrijednost": val, "jedinica": jed,
         "vrsta_gradevine": {"naziv": naziv, "izraz": izraz, "citat_izraza": ciz, "izvor": izv},
         "nacin_gradnje": nac[0] if nac else None}
    if nac: d["citat_nacina"] = nac[1]; chk(cl, nac[1], 'nacin')
    d["stanje"] = stn[0] if stn else None
    if stn: d["citat_stanja"] = stn[1]; chk(cl, stn[1], 'stanje')
    d.update({"zona": z, "uvjeti": uvl, "iznimke": izl, "vrsta_pravila": vp, "nejasno": nej})
    OUT.append(d)

KROV = [
 ("krovišta mogu biti ravna ili kosa", "oblik krovišta", "dopustenje", "ravna ili kosa", "opis", None),
 ("ako se grade kao kosa mogu biti jednostrešna, dvostrešna ili višestrešna", "vrsta kosog krovišta", "dopustenje", "jednostrešna, dvostrešna ili višestrešna", "opis", "ako se grade kao kosa"),
 ("moraju biti s nagibom krovnih ploha između 17° i 23°", "nagib krovnih ploha", "izmedju", "17–23", "°", "ako se grade kao kosa"),
 ("pokrov mora biti mediteran crijep ili kupa kanalica", "vrsta pokrova", "=", "mediteran crijep ili kupa kanalica", "opis", "ako se grade kao kosa"),
]

def krov(cl, st, al, vg, base_uv):
    for cit, par, op, val, jed, u in KROV:
        uv = list(base_uv) + ([(u, 'odredba')] if u else [])
        K(cl, st, '-', al, cit, par, op, val, jed, vg, uv=uv,
          nej=("OBUHVAT: nije sasvim jasno odnosi li se »ako se grade kao kosa« i na pokrov" if par == 'vrsta pokrova' else None))

VAT = "Ako se grade na granici građevne čestice, moraju od susjedne građevine biti odijeljene vatrobranim zidom, uz uvjet da nagib krova nije prema susjednoj građevnoj čestici"
VAT_N = "TUMACENJE: nije jasno je li »nagib krova nije prema susjednoj građevnoj čestici« uvjet za gradnju na granici ili za izvedbu vatrobranog zida"
OTV = "Ako imaju otvore prema susjednoj građevnoj čestici"
REK = "u skladu s odredbama ovog Prostornog plana"
GAB = "Ukoliko nisu ispunjeni uvjeti propisani ovim Prostornim planom mogu se rekonstruirati samo u postojećim tlocrtnim i visinskim gabaritima"
GAB_U = "Ukoliko nisu ispunjeni uvjeti propisani ovim Prostornim planom"

def pom(cl, st, uvod_uvjet, izn_txt, reg4):
    VG = ("pomoćna građevina", "Pomoćne građevine", "Pomoćne građevine grade se kao jednoetažne", "uvod_stavka")
    VGo = ("pomoćna građevina", "mogu se graditi", "mogu se graditi do granice građevne čestice", "odredba")
    B = [(uvod_uvjet, 'uvod')]
    Z = ([], PZ)
    K(cl, st, None, None, "Pomoćne građevine grade se kao jednoetažne", "najveći broj etaža", "=", 1, None, VG, uv=B)
    c1 = "visina od najniže kote konačno zaravnatog terena nije viša od visine osnovne građevine i ne prelazi visinu od 4,0 metra"
    K(cl, st, '-', 1, c1, "najveća visina građevine", "<=", "visina osnovne građevine", "opis", VG, uv=B)
    K(cl, st, '-', 1, c1, "najveća visina građevine", "<=", 4.0, "m", VG, uv=B)
    K(cl, st, '-', 2, "tlocrtna projekcija nije veća od 50 m 2", "najveća površina tlocrtne projekcije građevine", "<=", 50, "m²", VG, uv=B)
    krov(cl, st, 3, VG, B)
    K(cl, st, '-', 4, "mogu se graditi do granice građevne čestice", "prislanjanje uz susjednu građevinu ili granicu građevne čestice", "dopustenje", "do granice građevne čestice", "opis", VG, uv=B)
    K(cl, st, '-', 4, VAT, "drugo: odvajanje od susjedne građevine vatrobranim zidom", "opis", "vatrobrani zid", "opis", VG,
      uv=B + [("Ako se grade na granici građevne čestice", 'odredba'), ("uz uvjet da nagib krova nije prema susjednoj građevnoj čestici", 'odredba')], nej=VAT_N)
    K(cl, st, '-', 4, OTV + ", moraju biti udaljene od te čestice najmanje 4,0 metra", "najmanja udaljenost od granice građevne čestice", ">=", 4.0, "m", VG, uv=B + [(OTV, 'odredba')])
    K(cl, st, '-', 5, "najmanja dopuštena udaljenost od regulacijskog pravca iznosi 5,0 metara", "najmanja udaljenost od regulacijskog pravca", ">=", 5.0, "m", VG, uv=B)
    I = [izn_txt]
    K(cl, st, '-', 6, "mogu se graditi do granice građevne čestice", "prislanjanje uz susjednu građevinu ili granicu građevne čestice", "dopustenje", "do granice građevne čestice", "opis", VG, zona=Z, uv=B, izn=I)
    K(cl, st, '-', 6, VAT, "drugo: odvajanje od susjedne građevine vatrobranim zidom", "opis", "vatrobrani zid", "opis", VG, zona=Z,
      uv=B + [("Ako se grade na granici građevne čestice", 'odredba'), ("uz uvjet da nagib krova nije prema susjednoj građevnoj čestici", 'odredba')], izn=I, nej=VAT_N)
    K(cl, st, '-', 6, OTV + ", moraju biti udaljene od te čestice najmanje 3,0 metra", "najmanja udaljenost od granice građevne čestice", ">=", 3.0, "m", VG, zona=Z, uv=B + [(OTV, 'odredba')], izn=I)
    K(cl, st, '-', 6, reg4, "najmanja udaljenost od regulacijskog pravca", ">=", 4.0, "m", VG, zona=Z, uv=B, izn=I)
    VGg = ("garaža", "garaže", "na regulacijskom pravcu mogu se graditi samo garaže", "odredba")
    cg = "na regulacijskom pravcu mogu se graditi samo garaže, kada je takav zahtjev uvjetovan konfiguracijom terena, odnosno kada je završna kota ravnog krova ista kao niveleta ulice, odnosno max do visine ogradnog zida 1,1m kada to dozvoljavaju lokalni uvjeti"
    UG = [("kada je takav zahtjev uvjetovan konfiguracijom terena", 'odredba'), ("kada je završna kota ravnog krova ista kao niveleta ulice", 'odredba')]
    K(cl, st, '-', 7, cg, "drugo: gradnja na regulacijskom pravcu", "dopustenje", "samo garaže", "opis", VGg,
      uv=B + UG + [("kada to dozvoljavaju lokalni uvjeti", 'odredba')],
      nej="VEZNIK: »odnosno« između uvjeta može značiti da moraju biti ispunjeni svi ili bilo koji; NEDEFINIRAN_POJAM »lokalni uvjeti«")
    K(cl, st, '-', 7, "max do visine ogradnog zida 1,1m kada to dozvoljavaju lokalni uvjeti", "najveća visina građevine", "<=", 1.1, "m", VGg,
      uv=B + [("kada to dozvoljavaju lokalni uvjeti", 'odredba')],
      nej="TUMACENJE: nije jasno je li 1,1 m najveća visina garaže na regulacijskom pravcu ili alternativni uvjet uz »odnosno«")
    VGp = ("pomoćna građevina (postojeća)", "postojeće pomoćne građevine", "postojeće pomoćne građevine mogu se rekonsturirati", "odredba")
    S = ("postojeća", "postojeće pomoćne građevine")
    K(cl, st, '-', 8, "postojeće pomoćne građevine mogu se rekonsturirati i prenamjeniti u skladu s odredbama ovog Prostornog plana", "rekonstrukcija i prenamjena", "dopustenje", REK, "opis", VGp, stn=S, uv=B)
    K(cl, st, '-', 8, GAB, "gabariti pri rekonstrukciji", "opis", "postojeći tlocrtni i visinski gabariti", "opis", VGp, stn=S, uv=B + [(GAB_U, 'odredba')])

def polj(cl, st, uvod_uvjet, order, rek_cit):
    VG = ("poljoprivredna gospodarska građevina", "Poljoprivredne gospodarske građevine", "Poljoprivredne gospodarske građevine mogu se graditi", "uvod_stavka")
    VGo = ("poljoprivredna gospodarska građevina", "poljoprivredne gospodarske građevine", "udaljenost poljoprivredne gospodarske građevine od", "odredba")
    B = [(uvod_uvjet, 'uvod')]
    a = {k: i + 1 for i, k in enumerate(order)}
    K(cl, st, '-', a['vis'], "visina od najniže kote konačno zaravnatog terena iznosi najviše 4,0 m", "najveća visina građevine", "<=", 4.0, "m", VG, uv=B)
    K(cl, st, '-', a['gp'], "građevni pravac je iza građevnog pravca građevine osnovne namjene", "položaj građevnog pravca", "opis", "iza građevnog pravca građevine osnovne namjene", "opis", VG, uv=B)
    K(cl, st, '-', a['gr'], "najmanja udaljenost od granice građevne čestice iznosi 4,0 m", "najmanja udaljenost od granice građevne čestice", ">=", 4.0, "m", VG, uv=B)
    krov(cl, st, a['krov'], VG, B)
    K(cl, st, '-', a['reg'], "udaljenost poljoprivredne gospodarske građevine od regulacijskog pravca iznosi najmanje 6,0 m", "najmanja udaljenost od regulacijskog pravca", ">=", 6.0, "m", VGo, uv=B)
    I = ["iznimno, " + PZ]; Z = ([], PZ)
    K(cl, st, '-', a['izn'], "najmanja udaljenost poljoprivredne gospodarske građevine od granice građevne čestice iznosi 3,0 m", "najmanja udaljenost od granice građevne čestice", ">=", 3.0, "m",
      ("poljoprivredna gospodarska građevina", "poljoprivredne gospodarske građevine", "najmanja udaljenost poljoprivredne gospodarske građevine od granice", "odredba"), zona=Z, uv=B, izn=I)
    K(cl, st, '-', a['izn'], "udaljenost od regulacijskog pravca iznosi najmanje 5,0 m", "najmanja udaljenost od regulacijskog pravca", ">=", 5.0, "m",
      ("poljoprivredna gospodarska građevina", "poljoprivredne gospodarske građevine", "najmanja udaljenost poljoprivredne gospodarske građevine od granice", "odredba"), zona=Z, uv=B, izn=I)
    VGp = ("poljoprivredna gospodarska građevina (postojeća)", "postojeće poljoprivredne gospodarske građevine", "postojeće poljoprivredne gospodarske građevine mogu se", "odredba")
    S = ("postojeća", "postojeće poljoprivredne gospodarske građevine")
    K(cl, st, '-', a['rek'], rek_cit, "rekonstrukcija i prenamjena", "dopustenje", REK, "opis", VGp, stn=S, uv=B)
    K(cl, st, '-', a['rek'], GAB, "gabariti pri rekonstrukciji", "opis", "postojeći tlocrtni i visinski gabariti", "opis", VGp, stn=S, uv=B + [(GAB_U, 'odredba')])

from h import *

# Članak 20
K(20, 1, None, None, "Na jednoj građevnoj čestici može se graditi jedna građevina stambene namjene i uz nju pomoćna ili gospodarska građevina, ukoliko zadovoljavaju uvjete utvrđene ovim Prostornim planom",
  "dopuštenost gradnje", "dopustenje", "jedna građevina stambene namjene i uz nju pomoćna ili gospodarska građevina", "opis",
  ("stambena građevina", "građevina stambene namjene", "jedna građevina stambene namjene", "odredba"),
  uv=[("ukoliko zadovoljavaju uvjete utvrđene ovim Prostornim planom", 'odredba')])
K(20, 2, None, None, "Osim stambene u sklopu građevine stambene namjene omogućava se i ugostiteljsko-turistička namjena i poslovna namjena za tihe i čiste djelatnosti bez opasnosti od požara i eksplozije sa bukom manjom od 45dB noću i 55dB danju",
  "drugo: dopuštene namjene u stambenoj građevini", "dopustenje", "ugostiteljsko-turistička namjena i poslovna namjena za tihe i čiste djelatnosti", "opis",
  ("stambena građevina", "građevine stambene namjene", "u sklopu građevine stambene namjene", "odredba"),
  uv=[("za tihe i čiste djelatnosti bez opasnosti od požara i eksplozije sa bukom manjom od 45dB noću i 55dB danju", 'odredba')],
  nej="TUMACENJE: popis djelatnosti završava s »i sl.« pa nije zatvoren")
pom(20, 3, "uz građevine stambene namjene", "iznimno, " + PZ, "Najmanja dopuštena udaljenost od regulacijskog pravca iznosi 4,0 metra")

def tock(cl, st_txt, letter, nxt):
    a = ART[cl]; i = a.index(st_txt)
    s = a.index(letter + ") ", i) + len(letter) + 2
    e = a.index(nxt, s)
    return a[s:e].rstrip(" ;.")

def obit(cl, naziv, gen, uvod, nac2, R):
    # R: (letter, next_marker, par, op, jed, [v1, v2], izraz_odredbe or None, nova, uvjet)
    for L, nx, par, op, jed, vals, izr, nova, cond in R:
        cit = tock(cl, "(1)", L, nx)
        for al, (nlist, ncit) in enumerate([(["slobodnostojeća"], "za slobodnostojeće građevine"), nac2], 1):
            for nac in nlist:
                nz = naziv + " – " + nac + (" (nova)" if nova else "")
                if izr: vg = (nz, gen, izr, 'odredba')
                else: vg = (nz, gen, uvod, 'uvod_stavka')
                K(cl, 1, L, al, cit, par, op, vals[al - 1], jed, vg, nac=(nac, ncit),
                  stn=(("nova", "nove " + gen) if nova else None),
                  uv=([(cond, 'odredba')] if cond else []))

KP = "najveći koeficijent iskoristivosti (kis) (uz podrum ili ukupni)"
# Članak 22
g = "obiteljske kuće"; U22 = "granične vrijednosti za izgradnju obiteljske kuće"
obit(22, "obiteljska kuća", g, U22, (["dvojna", "ugrađena"], "za dvojne i ugrađene građevine"), [
 ("a", " b) ", "najmanja površina građevne čestice", ">=", "m²", [500, 300], "za izgradnju obiteljske kuće", False, None),
 ("c", " d) ", "najmanja površina tlocrtne projekcije građevine", ">=", "m²", [60, 60], "nove obiteljske kuće", True, None),
 ("d", " e) ", "najveća površina tlocrtne projekcije građevine", "<=", "m²", [200, 100], "nove obiteljske kuće", True, None),
 ("e", " f) ", "najveći koeficijent izgrađenosti (kig)", "<=", "koeficijent", [0.25, 0.25], None, False, None),
 ("f", " g) ", "najveći koeficijent iskoristivosti (kis) nadzemnih etaža", "<=", "koeficijent", [0.5, 0.5], None, False, None),
])
# g) has nacin citat without "za" for alineja 2
cit = tock(22, "(1)", "g", " h) ")
for al, nac, nc in [(1, "slobodnostojeća", "za slobodnostojeće građevine"), (2, "dvojna", "dvojne i ugrađene građevine"), (2, "ugrađena", "dvojne i ugrađene građevine")]:
    K(22, 1, "g", al, cit, KP, "<=", 0.75, "koeficijent", ("obiteljska kuća – " + nac, "obiteljske građevine", "ispod obiteljske građevine", "odredba"),
      nac=(nac, nc), uv=[("ukoliko se ispod obiteljske građevine gradi podrum", 'odredba')])
K(22, 1, "b", None, "iznimno za izgradnju samostojeće obiteljske kuće najmanja dopuštena površina građevne čestice može iznositi 400m²", "najmanja površina građevne čestice", ">=", 400, "m²",
  ("obiteljska kuća – slobodnostojeća", "samostojeće obiteljske kuće", "za izgradnju samostojeće obiteljske kuće", "odredba"), nac=("slobodnostojeća", "samostojeće obiteljske kuće"),
  uv=[("uz uvjet da se građevna čestica nalazi u okruženju već formiranih građevinskih čestica", 'odredba')], izn=["iznimno za izgradnju samostojeće obiteljske kuće"],
  nej="NEDEFINIRAN_POJAM: »u okruženju već formiranih građevinskih čestica« nije definirano")
K(22, 1, "h", None, "najveći dopušteni broj etaža obiteljske kuće je podrum i 2 nadzemne etaže", "najveći broj etaža", "<=", "podrum i 2 nadzemne etaže", None, ("obiteljska kuća", g, "broj etaža obiteljske kuće", 'odredba'))
K(22, 1, "i", None, "najveća dopuštena visina obiteljske kuće iznosi 6,5m", "najveća visina građevine", "<=", 6.5, "m", ("obiteljska kuća", g, "visina obiteljske kuće", 'odredba'))
polj(22, 2, "uz obiteljsku kuću", ['vis','gp','gr','krov','reg','izn','rek'], "postojeće poljoprivredne gospodarske građevine mogu se rekonsturirati i prenamjeniti u skladu s odredbama ovog Prostornog plana")

# Članak 23
g = "višeobiteljske kuće"; U23 = "granične vrijednosti za izgradnju višeobiteljske kuće"
obit(23, "višeobiteljska kuća", g, U23, (["dvojna"], "za dvojne građevine"), [
 ("a", " b) ", "najmanja površina građevne čestice", ">=", "m²", [500, 400], "za izgradnju višeobiteljske kuće", False, None),
 ("b", " c) ", "najmanja površina tlocrtne projekcije građevine", ">=", "m²", [60, 60], "nove višeobiteljske kuće", True, None),
 ("c", " d) ", "najveća površina tlocrtne projekcije građevine", "<=", "m²", [200, 100], "nove višeobiteljske kuće", True, None),
 ("d", " e) ", "najveći koeficijent izgrađenosti (kig)", "<=", "koeficijent", [0.25, 0.25], None, False, None),
 ("e", " f) ", "najveći koeficijent iskoristivosti (kis) nadzemnih etaža", "<=", "koeficijent", [0.5, 0.5], None, False, None),
])
cit = tock(23, "(1)", "f", " g) ")
for al, nac, nc in [(1, "slobodnostojeća", "za slobodnostojeće građevine"), (2, "dvojna", "dvojne građevine 0,75")]:
    K(23, 1, "f", al, cit, KP, "<=", 0.75, "koeficijent", ("višeobiteljska kuća – " + nac, "višeobiteljske građevine", "ispod višeobiteljske građevine", "odredba"),
      nac=(nac, nc), uv=[("ukoliko se ispod višeobiteljske građevine gradi podrum", 'odredba')])
K(23, 1, "g", None, "najveći dopušteni broj etaža višeobiteljske kuće je podrum i 2 nadzemne etaže", "najveći broj etaža", "<=", "podrum i 2 nadzemne etaže", None, ("višeobiteljska kuća", g, "broj etaža višeobiteljske kuće", 'odredba'))
K(23, 1, "h", None, "najveća dopuštena visina višeobiteljske kuće iznosi 6,5 m", "najveća visina građevine", "<=", 6.5, "m", ("višeobiteljska kuća", g, "visina višeobiteljske kuće", 'odredba'))
polj(23, 2, "uz višeobiteljsku kuću", ['vis','gp','gr','krov','reg','izn','rek'], "postojeće poljoprivredne gospodarske građevine mogu se rekonsturirati i prenamjeniti u skladu s odredbama ovog Prostornog plana")

# Članak 25
U25 = "granične vrijednosti za izgradnju stambenih građevina"
def s25(L, cit, par, op, val, jed, izr=None, cizr=None, nova=False, uv=(), zona=None, nej=None, nac=None):
    nz = "stambena građevina" + (" (nova)" if nova else "")
    vg = (nz, izr, cizr, 'odredba') if izr else (nz, "stambenih građevina", U25, 'uvod_stavka')
    K(25, 1, L, None, cit, par, op, val, jed, vg, stn=(("nova", "nove stambene građevine") if nova else None), uv=list(uv), zona=zona, nej=nej, nac=nac)
s25("a", "najmanja dopuštena površina građevne čestice za izgradnju stambene građevine iznosi 500 m 2", "najmanja površina građevne čestice", ">=", 500, "m²", "stambene građevine", "za izgradnju stambene građevine iznosi 500")
s25("b", "ovim prostornim planom se ne propisuje najveća dopuštena površina građevne čestice za izgradnju stambene građevine", "najveća površina građevne čestice", "nije_propisano", None, None, "stambene građevine", "za izgradnju stambene građevine;")
s25("c", "najmanja dopuštena površina tlocrtne projekcije nove stambene građevine iznosi 100 m 2 za sve tipove gradnje", "najmanja površina tlocrtne projekcije građevine", ">=", 100, "m²", "stambene građevine", "nove stambene građevine iznosi 100", nova=True)
s25("d", "najveća dopuštena površina tlocrtne projekcije nove stambene građevine iznosi 200 m 2", "najveća površina tlocrtne projekcije građevine", "<=", 200, "m²", "stambene građevine", "nove stambene građevine iznosi 200", nova=True)
s25("e", "najveći dopušteni koeficijent izgrađenosti (kig) određuje se 0,25", "najveći koeficijent izgrađenosti (kig)", "<=", 0.25, "koeficijent")
s25("f", "najveći dopušteni koeficijent iskoristivosti (kis) nadzemnih etaža u NA2-NA15.2 iznosi 0,50", "najveći koeficijent iskoristivosti (kis) nadzemnih etaža", "<=", 0.5, "koeficijent",
    zona=(["NA2-NA15.2"], "u NA2-NA15.2"), nej="OBUHVAT: oznaka je raspon zona »NA2-NA15.2« koji tekst ne razlaže; nije jasno vrijedi li kis i izvan tog raspona")
s25("g", "ukoliko se ispod stambene građevine gradi podrum najveći dopušteni koeficijent iskoristivosti (kis) iznosi 0,75", KP, "<=", 0.75, "koeficijent", "stambene građevine", "ispod stambene građevine gradi podrum",
    uv=[("ukoliko se ispod stambene građevine gradi podrum", 'odredba')])
s25("h", "stambene građevine mogu se graditi samo kao samostojeće građevine", "način gradnje", "=", "samostojeće građevine", "opis", "stambene građevine", "stambene građevine mogu se graditi samo kao samostojeće",
    nac=("slobodnostojeća", "samo kao samostojeće građevine"))
polj(25, 2, "uz stambenu građevinu", ['vis','gp','gr','izn','krov','reg','rek'], "postojeće poljoprivredne gospodarske građevine mogu se rekonsrturirati i prenamjeniti u skladu s odredbama ovog Prostornog plana")

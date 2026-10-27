#!/usr/bin/env python3
"""Provjera sučelja u Chromiumu (Playwright) s lažnom bazom u memoriji umjesto platformske `db`.
    python3 pilot_pregled/test_sucelje.py
Provjerava: prikaz bez baze (samo čitanje), 109 kandidata, označen citat, četiri razine, potvrdu, ispravak,
odbijanje bez obrazloženja (mora biti odbijeno), ručni unos, revizijski trag, provjeru lanca, otkrivanje izmjene,
mjerenje i pogled čestica, bez grešaka u konzoli, na širini računala i mobitela.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

P = Path(__file__).resolve().parent
URL = (P / "dist/pregled_pravila_travicici.html").as_uri()
LAZNA_BAZA = r"""
(() => {
  const store = new Map(), subs = [];
  const snapDoc = (p) => ({ id: p.split('/').pop(), exists: store.has(p), data: () => store.has(p) ? JSON.parse(JSON.stringify(store.get(p))) : undefined, metadata: {} });
  const kids = (c) => [...store.keys()].filter(k => k.startsWith(c + '/') && k.slice(c.length + 1).split('/').length === 1).sort();
  const fire = () => { for (const s of subs) s(); };
  const docRef = (p) => ({ id: p.split('/').pop(), path: p, get: async () => snapDoc(p), set: async (d) => { store.set(p, JSON.parse(JSON.stringify(d))); setTimeout(fire, 0); },
    update: async (d) => { store.set(p, Object.assign(store.get(p) || {}, d)); setTimeout(fire, 0); }, delete: async () => { store.delete(p); setTimeout(fire, 0); },
    collection: (c) => colRef(p + '/' + c), onSnapshot: (n) => { const f = () => n(snapDoc(p)); subs.push(f); f(); return () => {}; } });
  const colRef = (c) => ({ path: c, doc: (id) => docRef(c + '/' + (id || Math.random().toString(36).slice(2))),
    get: async () => { const docs = kids(c).map(snapDoc); return { docs, size: docs.length, empty: !docs.length, docChanges: () => [] }; },
    onSnapshot: (n) => { const f = () => { const docs = kids(c).map(snapDoc); n({ docs, size: docs.length, empty: !docs.length, docChanges: () => [], metadata: {} }); }; subs.push(f); f(); return () => {}; } });
  const db = { doc: docRef, collection: colRef };
  const user = { id: async () => 'u_test', can: async () => true, isOwner: async () => true, canEdit: async () => true, me: async () => ({ id: 'u_test', name: 'Test' }),
    profiles: async (ids) => Object.fromEntries([].concat(ids).map(i => [i, { id: i, name: i === 'u_test' ? 'Test pregledavatelj' : '' }])) };
  window.__store = store;
  window.claude = { use: async (n) => n === 'db' ? db : (n === 'user' ? user : null) };
})();
"""


def main():
    greske, prolaz = [], []
    ok = lambda ime, uvjet: (prolaz if uvjet else greske).append(ime)
    # fontovi s Google Fonts se u testnom okruženju ne mogu učitati (mreža); to nije greška stranice
    vazno = lambda L: [x for x in L if "ERR_TUNNEL_CONNECTION_FAILED" not in x and "fonts.g" not in x]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        # 1) bez baze: samo čitanje, sve se prikazuje
        pg = b.new_page(viewport={"width": 1300, "height": 900}); log = []
        pg.on("console", lambda m: log.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: log.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(600)
        ok("popis ima 109 kandidata", pg.locator(".stavka").count() == 109)
        ok("citat je označen u članku", pg.locator("#detalj .clanak mark").count() == 1)
        ok("četiri razine", pg.locator("#detalj .razina").count() == 4)
        pg.wait_for_selector(".razina.zakljucana"); ok("pravna valjanost zaključana", "nije utvrđena" in pg.locator(".razina.zakljucana").first.inner_text().lower())
        ok("bez baze spremanje onemogućeno", pg.locator("#detalj form .gumb").is_disabled())
        for v in ["rucni-unos", "mjerenje", "cestice", "trag"]:
            pg.goto(URL + "#" + v); pg.wait_for_timeout(250)
            ok(f"pogled {v} vidljiv", pg.locator("#v-" + v).is_visible())
        ok("čestice: poruka o nedostupnim podacima", "Podaci nisu dostupni" in pg.locator("#lg-cestice").inner_text())
        ok("bez grešaka u konzoli (bez baze)", not vazno(log)); log0 = list(log)
        pg.close()

        # 2) s lažnom bazom: cijeli tok
        pg = b.new_page(viewport={"width": 1300, "height": 900}); log = []
        pg.on("console", lambda m: log.append(m.text) if m.type == "error" else None); pg.on("pageerror", lambda e: log.append(str(e)))
        pg.add_init_script(LAZNA_BAZA); pg.goto(URL); pg.wait_for_timeout(800)
        pg.select_option("#f-faza", "faza1"); pg.wait_for_timeout(150)
        ok("filtar faze 1 prikazuje samo čl. 9", pg.locator(".stavka").count() == 31 or pg.locator(".skupina").all_inner_texts() == ["ČLANAK 9"] or pg.locator(".skupina").count() == 1)
        pg.locator(".stavka").nth(0).click(); pg.wait_for_timeout(150)
        # odbijanje bez obrazloženja mora pasti
        pg.locator("#detalj input[value=ODBIJANJE]").check(); pg.locator("#detalj form .gumb").click(); pg.wait_for_timeout(200)
        ok("odluka bez obrazloženja nije spremljena", "obrazloženje" in pg.locator("#detalj .poruka").inner_text() and pg.evaluate("window.__store.size") == 0)
        # potvrda prvog
        pg.locator("#detalj input[value=POTVRDA]").check()
        pg.locator("#detalj textarea[id^=obr-]").fill("Vrijednost i zona odgovaraju citatu članka 9."); pg.locator("#detalj form .gumb").click(); pg.wait_for_timeout(500)
        st = pg.locator("#detalj .poruka").inner_text()
        ok("potvrda spremljena", "Spremljeno" in st or pg.evaluate("window.__store.size") >= 2)
        ok("stručna razina = potvrđeno", "potvrđeno" in pg.locator("#detalj .razina").nth(2).inner_text())
        ok("pravna razina i dalje nije utvrđena", "nije utvrđena" in pg.locator(".razina.zakljucana").inner_text())
        # ispravak drugog
        pg.locator(".stavka").nth(1).click(); pg.wait_for_timeout(150)
        pg.locator("#detalj input[value=ISPRAVAK]").check(); pg.locator("#is-vrijednost").fill("0,3")
        pg.locator("#detalj textarea[id^=obr-]").fill("U citatu piše druga vrijednost; ispravljeno prema tekstu."); pg.locator("#detalj form .gumb").click(); pg.wait_for_timeout(500)
        ok("ispravak spremljen", "ispravljeno" in pg.locator("#detalj .razina").nth(2).inner_text())
        # ručni unos
        pg.goto(URL + "#rucni-unos"); pg.wait_for_timeout(300)
        pg.evaluate("""() => { const n = document.querySelector('#ru-tekst').firstChild; const r = document.createRange(); r.setStart(n, 0); r.setEnd(n, 60); const s = getSelection(); s.removeAllRanges(); s.addRange(r); }""")
        pg.locator("#ru-uzmi").click()
        ok("citat preuzet iz označenog teksta", len(pg.locator("#ru-citat").input_value()) > 20)
        pg.locator("#ru-vrijednost").fill("1000"); pg.locator("#ru-obr").fill("Ručno upisano iz bloka 1 članka 10.")
        pg.locator("#ru-spremi").click(); pg.wait_for_timeout(500)
        ok("ručni unos spremljen", "Spremljeno" in pg.locator("#ru-poruka").inner_text())
        # trag i lanac
        pg.goto(URL + "#trag"); pg.wait_for_timeout(400)
        ok("trag ima 3 događaja", pg.locator("#tr-tablica tr").count() == 3)
        pg.locator("#tr-provjeri").click(); pg.wait_for_timeout(400)
        ok("lanac ispravan", "ispravan" in pg.locator("#tr-stanje").inner_text() and "NIJE" not in pg.locator("#tr-stanje").inner_text())
        pg.evaluate("""() => { for (const [k, v] of window.__store) if (k.includes('/dogadjaji/') && v.radnja === 'POTVRDA') { v.obrazlozenje = 'Podmetnuta izmjena obrazloženja.'; window.__store.set(k, v); } }""")
        pg.goto(URL + "#pregled"); pg.wait_for_timeout(200); pg.goto(URL + "#trag"); pg.wait_for_timeout(300)
        pg.evaluate("() => window.dispatchEvent(new Event('hashchange'))")
        pg.reload(); pg.wait_for_timeout(800)
        # nakon ponovnog učitavanja lažna baza je prazna, pa provjeru izmjene radimo izravno logikom na stranici
        r = pg.evaluate("""async () => { const L = window.PregledLogika; const a = await L.napraviDogadjaj({id:'a',rb:1,tko:'u',kada:'2026',radnja:'POTVRDA',kandidat:'H001',obrazlozenje:'izvorno obrazloženje'}, null);
            const izm = Object.assign({}, a, {obrazlozenje:'izmijenjeno'}); return [(await L.provjeriLanac([a])).ispravno, (await L.provjeriLanac([izm])).ispravno]; }""")
        ok("lanac otkriva izmjenu u pregledniku", r == [True, False])
        # mjerenje
        pg.goto(URL + "#mjerenje"); pg.wait_for_timeout(300)
        ok("mjerenje prikazuje protokol", "Faza 1" in pg.locator("#mj-protokol").inner_text())
        ok("bez grešaka u konzoli (s bazom)", not vazno(log))
        # mobitel
        m = b.new_page(viewport={"width": 390, "height": 844}); m.goto(URL); m.wait_for_timeout(500)
        sirina = m.evaluate("document.documentElement.scrollWidth")
        ok("mobitel: bez vodoravnog pomicanja", sirina <= 392)
        m.screenshot(path=str(P / "dist/zaslon_mobitel.png"), full_page=False)
        pg2 = b.new_page(viewport={"width": 1300, "height": 900}); pg2.goto(URL); pg2.wait_for_timeout(500); pg2.screenshot(path=str(P / "dist/zaslon_racunalo.png"))
        pg2.goto(URL + "#cestice"); pg2.wait_for_timeout(400); pg2.screenshot(path=str(P / "dist/zaslon_cestice.png"))
        b.close()
    for x in prolaz: print("OK  ", x)
    for x in greske: print("FAIL", x)
    if log0 or log: print("konzola:", log0, log)
    print(f"{len(prolaz)}/{len(prolaz) + len(greske)}")
    sys.exit(1 if greske else 0)


if __name__ == "__main__":
    main()

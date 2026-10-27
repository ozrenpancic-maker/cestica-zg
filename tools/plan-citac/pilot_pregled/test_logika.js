// Testovi logike pilota pregleda: node pilot_pregled/test_logika.js
const L = require("./pregled_logika.js");
const fs = require("fs"), path = require("path");
const D = JSON.parse(fs.readFileSync(path.join(__dirname, "podaci/pilot_travicici.json"), "utf8"));
let ok = 0, bad = 0;
const t = async (ime, f) => { try { await f(); ok++; console.log("OK  ", ime); } catch (e) { bad++; console.log("FAIL", ime, "-", e.message); } };
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || "") + " " + JSON.stringify(a) + " != " + JSON.stringify(b)); };
const K = D.kandidati, k1 = K.find(k => k.tehnicka_provjera.status !== "ODBIJEN"), kOdb = K.find(k => k.tehnicka_provjera.status === "ODBIJEN");
const baza = (o) => Object.assign({ tko: "u_A", kada: "2026-10-27T08:00:00.000Z", obrazlozenje: "Provjereno prema citatu u članku.", trajanje_ms: 30000 }, o);

(async () => {
  await t("podaci: svi citati nađeni u tekstu članka", () => {
    for (const k of K) { const c = D.clanci.find(c => c.broj === k.clanak); if (!k.citat_pozicija) throw new Error(k.id);
      const isj = c.tekst.slice(...k.citat_pozicija); if (isj.split(/\s+/).join(" ") !== k.citat.split(/\s+/).join(" ")) throw new Error("pomak " + k.id); }
  });
  await t("podaci: nema polja iz slijepih oznaka", () => {
    const s = JSON.stringify(D); for (const f of ["jednoznacnost", "uvjet_primjene", "razlozi_pregleda", "zapisi", "prostorni_obuhvat"]) if (s.includes('"' + f + '"')) throw new Error(f);
  });
  await t("četiri razine su odvojene; pravna uvijek NIJE_UTVRDENA", () => {
    const r = L.razine(k1, []); eq([r.ai, r.strucna, r.pravna], ["PRIJEDLOG", "NIJE_PREGLEDANO", "NIJE_UTVRDENA"]);
    if (r.tehnicka !== k1.tehnicka_provjera.status) throw new Error("tehnička");
  });
  await t("automatska potvrda ne postoji: bez događaja nijedan kandidat nije potvrđen", () => {
    for (const k of K) if (L.potvrdenoPravilo(k, []) !== null) throw new Error(k.id);
  });
  await t("tehnički 'prošlo sve provjere' ne znači stručnu potvrdu", () => {
    const a = K.find(k => k.tehnicka_provjera.status === "AUTOMATSKI_PRIHVACEN"); eq(L.razine(a, []).strucna, "NIJE_PREGLEDANO");
  });
  await t("obrazloženje je obavezno", () => { eq(L.provjeriDogadjaj(baza({ radnja: "POTVRDA", kandidat: k1.id, obrazlozenje: "ok" }), k1).length > 0, true); });
  await t("pravna valjanost se ne može postaviti", () => {
    const g = L.provjeriDogadjaj(baza({ radnja: "POTVRDA", kandidat: k1.id, pravna_valjanost: "VALJANO" }), k1); if (!g.some(x => /pravnu/.test(x))) throw new Error(g);
  });
  await t("ispravak mora promijeniti barem jedno polje", () => {
    eq(L.provjeriDogadjaj(baza({ radnja: "ISPRAVAK", kandidat: k1.id, poslije: { vrijednost: k1.ai_prijedlog.vrijednost } }), k1).some(x => /promijeniti/.test(x)), true);
    eq(L.provjeriDogadjaj(baza({ radnja: "ISPRAVAK", kandidat: k1.id, poslije: { vrijednost: "drugo" } }), k1), []);
  });
  await t("kandidat odbijen pri provjeri ne može se samo potvrditi", () => {
    eq(L.provjeriDogadjaj(baza({ radnja: "POTVRDA", kandidat: kOdb.id }), kOdb).length, 1);
  });
  await t("stručni status = zadnji događaj; trag ostaje cijeli", async () => {
    const e1 = await L.napraviDogadjaj(baza({ id: "e1", rb: 1, radnja: "POTVRDA", kandidat: k1.id }), null);
    const e2 = await L.napraviDogadjaj(baza({ id: "e2", rb: 2, radnja: "ODBIJANJE", kandidat: k1.id, kada: "2026-10-27T08:05:00.000Z" }), e1.hash);
    const s = L.strucniStatus([e2, e1], k1.id); eq([s.stanje, s.broj], ["ODBIJENO", 2]);
    eq(L.potvrdenoPravilo(k1, [e1, e2]), null);
  });
  await t("ispravak daje pravilo s ispravljenim poljem", async () => {
    const e = await L.napraviDogadjaj(baza({ id: "e3", rb: 1, radnja: "ISPRAVAK", kandidat: k1.id, poslije: { vrijednost: 99 } }), null);
    eq(L.potvrdenoPravilo(k1, [e]).vrijednost, 99);
  });
  await t("lanac otkriva izmjenu sadržaja", async () => {
    const e1 = await L.napraviDogadjaj(baza({ id: "a", rb: 1, radnja: "POTVRDA", kandidat: k1.id }), null);
    const e2 = await L.napraviDogadjaj(baza({ id: "b", rb: 2, radnja: "VRACANJE", kandidat: k1.id }), e1.hash);
    eq((await L.provjeriLanac([e1, e2])).ispravno, true);
    const izmj = Object.assign({}, e1, { obrazlozenje: "Naknadno promijenjeno obrazloženje." });
    eq((await L.provjeriLanac([izmj, e2])).ispravno, false);
  });
  await t("lanac otkriva obrisan događaj", async () => {
    const e1 = await L.napraviDogadjaj(baza({ id: "a", rb: 1, radnja: "POTVRDA", kandidat: k1.id }), null);
    const e2 = await L.napraviDogadjaj(baza({ id: "b", rb: 2, radnja: "VRACANJE", kandidat: k1.id }), e1.hash);
    const e3 = await L.napraviDogadjaj(baza({ id: "c", rb: 3, radnja: "POTVRDA", kandidat: k1.id }), e2.hash);
    eq((await L.provjeriLanac([e1, e3])).ispravno, false);
  });
  await t("mjerenje zbraja aktivno vrijeme po načinu i članku", async () => {
    const k13 = K.find(k => k.clanak === 13);
    const ev = [baza({ radnja: "POTVRDA", kandidat: k13.id, trajanje_ms: 20000 }), baza({ radnja: "ODBIJANJE", kandidat: k13.id, trajanje_ms: 10000 }),
                baza({ radnja: "RUCNI_UNOS", clanak: 10, citat: "x", poslije: { parametar: "p" }, trajanje_ms: 90000 })];
    const m = L.mjerenje(ev, K); const a = m.find(x => x.nacin === "PREGLED_AI"), r = m.find(x => x.nacin === "RUCNI_UNOS");
    eq([a.ms, a.zavrsenih_pravila, a.s_po_pravilu, r.s_po_pravilu], [30000, 1, 30, 90]);
  });
  await t("važenje plana na dan", () => {
    const ev = D.plan.evidencija_pgz;
    eq(L.vaziNaDan(ev, "2026-10-27").vazi, true); eq(L.vaziNaDan(ev, "2012-05-01").vazi, false);
    eq(L.vaziNaDan(Object.assign({}, ev, { datum_van_snage: "01.01.2020." }), "2026-10-27").vazi, false);
  });
  await t("geometrija: površina zone T2-5 i točka u poligonu", () => {
    const z = D.geometrija.zone[0].geometrija.coordinates[0]; const a = L.povrsinaM2(z);
    if (a < 5000 || a > 20000) throw new Error("površina " + a);
    const xs = z.map(c => c[0]), ys = z.map(c => c[1]);
    eq(L.tockaUPoligonu([0, 0], z), false);
    eq(L.tockaUPoligonu([(Math.min(...xs) + Math.max(...xs)) / 2, (Math.min(...ys) + Math.max(...ys)) / 2], z), true);
  });
  await t("povezivanje: čestica u T2-5 dobiva samo stručno potvrđena pravila zone T2-5", async () => {
    const z = D.geometrija.zone[0]; const k9 = K.find(k => (k.ai_prijedlog.zona.oznake || []).includes("T2-5"));
    const ces = { prsten: z.geometrija.coordinates[0] };   // čestica = cijela zona (čl. 9: »jedinstvena građevna čestica«)
    let r = L.pravilaZaCesticu(ces, [z], K, [], 0.5); if (!r.length || r.some(x => x.stanje !== "NIJE_STRUCNO_POTVRDENO")) throw new Error("bez potvrde");
    const e = await L.napraviDogadjaj(baza({ id: "p", rb: 1, radnja: "POTVRDA", kandidat: k9.id }), null);
    r = L.pravilaZaCesticu(ces, [z], K, [e], 0.5); eq(r.find(x => x.kandidat === k9.id).stanje, "VRIJEDI");
    eq(r.filter(x => x.stanje === "VRIJEDI").length, 1);
  });
  console.log(`${ok}/${ok + bad}`); process.exit(bad ? 1 : 0);
})();

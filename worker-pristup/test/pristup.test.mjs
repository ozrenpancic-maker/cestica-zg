// Lokalni test Workera u Miniflareu (workerd + D1), s lažnim Brevoom. Ne šalje prave e-mailove i ne treba prave ključeve.
// Pokretanje: cd worker-pristup && npm install && npm test
import { Miniflare } from "miniflare";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createHmac } from "node:crypto";

let pass = 0, fail = 0; const fails = [];
const ok = (c, n) => { if (c) pass++; else { fail++; fails.push(n); } };
const COMPAT = readFileSync(new URL("../wrangler.toml", import.meta.url), "utf8").match(/compatibility_date\s*=\s*"([^"]+)"/)[1];
const SQL = readFileSync(new URL("../migrations/0001_init.sql", import.meta.url), "utf8").replace(/--[^\n]*/g, "").split(";").map((s) => s.trim()).filter(Boolean);
const ORIGIN = "https://app.cesticahr.com", ADMIN = "admin-tajna-za-test-1234567890", TOTP = "JBSWY3DPEHPK3PXP", W = "https://p.example";
const brevo = { calls: [], mode: "ok" }, dgu = { n: 0 };
async function fakeBrevo(req) { const b = await req.json(); brevo.calls.push({ h: Object.fromEntries(req.headers), b }); return brevo.mode === "ok" ? new Response(JSON.stringify({ messageId: "x" }), { status: 201 }) : new Response("{}", { status: 500 }); }
async function mf(vars = {}) {
  const m = new Miniflare({ modules: true, scriptPath: fileURLToPath(new URL("../src/index.js", import.meta.url)), compatibilityDate: COMPAT, d1Databases: ["DB"],
    bindings: { ALLOWED_ORIGINS: ORIGIN, MAIL_FROM: "dosje@cesticahr.com", MAIL_REPLY: "info@cesticahr.com", ADMIN_EMAIL: "info@cesticahr.com", APP_URL: "https://app.cesticahr.com/", IZVJESTAJA_DNEVNO: "2", TOKEN_EPOCH: "1", TRAJANJE_DANA: "30",
      TOKEN_SECRET: "token-tajna-test-abcdefghijklmnop", CODE_PEPPER: "pepper-test-0123456789", ADMIN_SECRET: ADMIN, ADMIN_TOTP: TOTP, BREVO_KEY: "xkeysib-TEST-NE-PRAVI", ...vars },
    outboundService: (req) => { const hn = new URL(req.url).hostname; if (hn === "api.brevo.com") return fakeBrevo(req); if (hn === "geoportal.dgu.hr") { dgu.n++; return new Response(new Uint8Array([0xff, 0xd8, 0xff, 1, 2, 3]), { headers: { "content-type": "image/jpeg" } }); } return new Response("blokirano u testu", { status: 599 }); } });
  const db = await m.getD1Database("DB"); for (const s of SQL) await db.prepare(s).run(); m.db = db; return m;
}
function totp(sec, off = 0) { const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"; let bits = ""; for (const c of sec) bits += A.indexOf(c).toString(2).padStart(5, "0"); const key = Buffer.from(bits.match(/.{8}/g).map((b) => parseInt(b, 2)));
  const m = Buffer.alloc(8); m.writeUInt32BE(Math.floor(Date.now() / 30000) + off, 4); const h = createHmac("sha1", key).update(m).digest(), o = h[19] & 15; return String(((h.readUInt32BE(o) & 0x7fffffff) % 1e6)).padStart(6, "0"); }
const call = (m, path, { method = "GET", body, tok, origin = ORIGIN, ip = "1.2.3.4" } = {}) => m.dispatchFetch(W + path, { method, headers: { origin, "cf-connecting-ip": ip, "content-type": "application/json", ...(tok ? { authorization: "Bearer " + tok } : {}) }, body: body == null ? undefined : JSON.stringify(body) });
async function adminLogin(m, { pw = ADMIN, kod = totp(TOTP), ip = "5.5.5.5" } = {}) { const r = await m.dispatchFetch(W + "/admin/prijava", { method: "POST", headers: { "content-type": "application/json", "x-chr-admin": "1", origin: W, "cf-connecting-ip": ip }, body: JSON.stringify({ lozinka: pw, kod }) }); const c = (r.headers.get("set-cookie") || "").split(";")[0]; return { r, c }; }
const adm = (m, c, p, body) => m.dispatchFetch(W + "/admin/api/" + p, { method: body ? "POST" : "GET", headers: { "content-type": "application/json", "x-chr-admin": "1", origin: W, cookie: c || "" }, body: body ? JSON.stringify(body) : undefined });
const zadnjiMail = () => brevo.calls[brevo.calls.length - 1];
const linkIz = (html, rx) => { const m = String(html).match(rx); return m ? m[1].replace(/&amp;/g, "&") : null; };
const PDF = Buffer.from("%PDF-1.4\n" + "x".repeat(400)).toString("base64");

let m = await mf();
// --- 1. osnovne funkcije bez registracije: Worker ne smije tražiti ništa za javne podatke (aplikacija radi bez njega); provjera bez tokena odbijena
ok((await call(m, "/provjera")).status === 401, "Bez prijave nema naprednog pristupa (provjera odbijena)");
// --- 2. zahtjev: e-mail obavezan, potvrda adrese, robot, ograničenja
ok((await call(m, "/zahtjev", { method: "POST", body: { email: "nije-email" } })).status === 400, "Zahtjev: neispravan e-mail odbijen");
let r = await call(m, "/zahtjev", { method: "POST", body: { email: "Kupac@Primjer.hr", namjena: "kupujem" } }); let j = await r.json();
ok(r.status === 200 && j.ok && brevo.calls.length === 1, "Zahtjev: zaprimljen, korisniku poslan e-mail");
const m1 = zadnjiMail(); ok(m1.b.to[0].email === "kupac@primjer.hr" && /Zaprimili smo vaš zahtjev za napredni pristup aplikaciji ČesticaHR/.test(m1.b.htmlContent) && /potvrdi adresu/.test(m1.b.htmlContent), "Zahtjev: poruka korisniku s tekstom iz uputa i poveznicom za potvrdu adrese");
const potvrda = linkIz(m1.b.htmlContent, /href="(https:\/\/p\.example\/potvrdi\?[^"]+)"/);
r = await call(m, "/zahtjev", { method: "POST", body: { email: "kupac@primjer.hr" } }); ok(r.status === 200 && brevo.calls.length === 1, "Zahtjev: ponovljeni zahtjev za istu adresu ne stvara novi zahtjev ni poruku");
r = await call(m, "/zahtjev", { method: "POST", body: { email: "robot@primjer.hr", web: "http://spam" } }); ok(r.status === 200 && brevo.calls.length === 1 && !(await m.db.prepare("SELECT id FROM zahtjev WHERE email='robot@primjer.hr'").first()), "Zahtjev: popunjeno skriveno polje (robot) tiho odbačeno");
for (let i = 0; i < 5; i++) await call(m, "/zahtjev", { method: "POST", body: { email: "x" + i + "@primjer.hr" }, ip: "7.7.7.7" });
ok((await call(m, "/zahtjev", { method: "POST", body: { email: "x9@primjer.hr" }, ip: "7.7.7.7" })).status === 429, "Zahtjev: najviše 5 zahtjeva na sat s iste mreže");
ok((await call(m, "/zahtjev", { method: "POST", body: { email: "a@b.hr" }, origin: "https://zli.example" })).status === 403, "Zahtjev: tuđa stranica ne može slati zahtjeve (CORS)");
let red = await m.db.prepare("SELECT * FROM zahtjev WHERE email='kupac@primjer.hr'").first();
ok(red.status === "nepotvrden" && red.potvrda_h && !JSON.stringify(red).includes(potvrda.split("t=")[1]), "Zahtjev: dok adresa nije potvrđena, zahtjev se ne pregledava; token potvrde nije u bazi");
r = await m.dispatchFetch(W + "/potvrdi?i=" + red.id + "&t=krivo"); ok(r.status === 400, "Potvrda: kriv token odbijen");
const nm = brevo.calls.length; r = await m.dispatchFetch(potvrda); ok(r.status === 200 && /Adresa je potvrđena/.test(await r.text()), "Potvrda adrese: zahtjev prelazi na čekanje");
const ma = brevo.calls.slice(nm).find((c) => c.b.to[0].email === "info@cesticahr.com"); ok(ma && ma.b.subject === "Novi zahtjev za pristup ČesticaHR-u" && /\/admin/.test(ma.b.htmlContent) && !/kupac@primjer\.hr/.test(ma.b.htmlContent), "Administratoru stiže »Novi zahtjev za pristup ČesticaHR-u« s poveznicom (bez adrese korisnika u poruci)");
ok((await m.dispatchFetch(potvrda)).status === 400, "Potvrda: poveznica vrijedi samo jednom");

// --- 8. korisnik ne može u administraciju; 4. ne može sam sebi odobriti
ok((await adm(m, "", "zahtjevi")).status === 401 && (await adm(m, "", "radnja", { id: red.id, radnja: "odobri" })).status === 401, "Bez administratorske prijave: popis i odobravanje odbijeni (401)");
const nema = await (await m.dispatchFetch(W + "/admin")).text(); ok(!nema.includes(ADMIN) && !nema.includes(TOTP) && /nonce-/.test((await m.dispatchFetch(W + "/admin")).headers.get("content-security-policy")), "Administratorska stranica ne sadrži lozinku ni tajnu; stroga CSP s nonceom");
ok((await adminLogin(m, { pw: "kriva-lozinka-xxxxxxxxxxxx" })).r.status === 401, "Admin: kriva lozinka odbijena");
ok((await adminLogin(m, { kod: "000000" })).r.status === 401, "Admin: točna lozinka bez točnog jednokratnog koda (MFA) odbijena");
for (let i = 0; i < 5; i++) await adminLogin(m, { pw: "krivo-xxxxxxxxxxxxxxxxxxxx", ip: "6.6.6.6" });
ok((await adminLogin(m, { ip: "6.6.6.6" })).r.status === 429, "Admin: nakon 5 neuspjelih prijava s iste adrese čekanje 15 minuta");
let L = await adminLogin(m); ok(L.r.status === 200 && /HttpOnly/.test(L.r.headers.get("set-cookie")) && /Secure/.test(L.r.headers.get("set-cookie")) && /SameSite=Strict/.test(L.r.headers.get("set-cookie")) && /^__Host-/.test(L.c), "Admin: prijava lozinkom i jednokratnim kodom; sesija u kolačiću __Host-, HttpOnly, Secure, SameSite=Strict");
const C = L.c;
ok((await adminLogin(m)).r.status === 401, "Admin: isti jednokratni kod ne može se upotrijebiti dvaput");
ok((await m.dispatchFetch(W + "/admin/api/radnja", { method: "POST", headers: { "content-type": "application/json", cookie: C }, body: JSON.stringify({ id: red.id, radnja: "odobri" }) })).status === 403, "Admin: POST bez zaštitnog zaglavlja (CSRF) odbijen i uz valjanu sesiju");
// --- 3. administrator vidi zahtjev
j = await (await adm(m, C, "zahtjevi")).json(); const Z = j.zahtjevi.find((z) => z.email === "kupac@primjer.hr");
ok(Z && Z.stanje === "ceka" && Z.namjena === "Kupujem zemljište" && j.mfa === true && !j.zahtjevi.some((z) => /^x\d@/.test(z.email)), "Admin vidi novi zahtjev (na čekanju, namjena); nepotvrđene adrese se ne prikazuju");
// --- 5. odobrenje šalje e-mail s kodom; 6. kod radi samo za taj pristup
const n0 = brevo.calls.length; r = await adm(m, C, "radnja", { id: Z.id, radnja: "odobri" }); j = await r.json();
const mo = brevo.calls[n0]; const kod = linkIz(mo && mo.b.htmlContent, /<b[^>]*>([A-Z2-9]{4}-[A-Z2-9]{4}-[A-Z2-9]{4})<\/b>/), akt = linkIz(mo && mo.b.htmlContent, /href="([^"]+\?pristup=[^"]+)"/);
ok(r.status === 200 && j.mail === true && mo.b.to[0].email === "kupac@primjer.hr" && mo.b.subject === "Vaš napredni pristup aplikaciji ČesticaHR je odobren" && kod && akt && /30 dana od aktivacije/.test(mo.b.htmlContent), "Odobrenje: automatski e-mail s pojedinačnim kodom, poveznicom za aktivaciju i trajanjem");
red = await m.db.prepare("SELECT * FROM zahtjev WHERE id=?").bind(Z.id).first(); const sve = JSON.stringify(await m.db.prepare("SELECT * FROM zahtjev").all()) + JSON.stringify(await m.db.prepare("SELECT * FROM dnevnik").all());
ok(!sve.includes(kod) && !sve.includes(kod.replace(/-/g, "")) && red.kod_h && !red.aktiviran, "Kod nije u bazi u čitljivom obliku (ni u dnevniku); pristup još nije aktiviran");
r = await call(m, "/prijava", { method: "POST", body: { kod: kod.toLowerCase().replace(/-/g, " ") } }); const P = await r.json();
red = await m.db.prepare("SELECT * FROM zahtjev WHERE id=?").bind(Z.id).first();
ok(r.status === 200 && P.token && red.aktiviran && Math.abs(red.istice - (red.aktiviran + 30 * 86400000)) < 1000, "Aktivacija: prva prijava kodom pokreće 30 dana od aktivacije");
ok((await call(m, "/provjera", { tok: P.token })).status === 200, "Kod daje pristup odobrenom korisniku");
ok((await call(m, "/prijava", { method: "POST", body: { kod: "ABCD-EFGH-JKLM" } })).status === 401, "Nepostojeći kod ne radi");
for (let i = 0; i < 10; i++) await call(m, "/prijava", { method: "POST", body: { kod: "AAAA-BBBB-CCCC" }, ip: "9.9.9.9" });
ok((await call(m, "/prijava", { method: "POST", body: { kod }, ip: "9.9.9.9" })).status === 429, "Pogađanje kodova: nakon 10 neuspjelih pokušaja s iste mreže čekanje sat vremena");
const [pp, ss] = P.token.split("."), lazni = Buffer.from(JSON.stringify({ id: Z.id, kv: red.kod_izdan, exp: Date.now() + 1e10, v: "1" })).toString("base64url") + "." + ss;
ok((await call(m, "/provjera", { tok: lazni })).status === 401, "Krivotvoreni token odbijen");
// dosje na e-mail (postojeća funkcija)
ok((await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "kupac@primjer.hr", pdf: PDF, naziv: "dosje 1551-4.pdf" } })).status === 200 && zadnjiMail().b.attachment[0].name === "dosje_1551-4.pdf", "Dosje na e-mail i dalje radi");
// dosje kao PDF bajtovi (aplikacija od 11/2026): adresa i naziv u zaglavljima, privitak u base64 prema Brevu
{ const pdfB = new TextEncoder().encode("%PDF-1.4\n" + "y".repeat(5000)), hdr = { origin: ORIGIN, "cf-connecting-ip": "1.2.3.4", authorization: "Bearer " + P.token, "content-type": "application/pdf", "x-email": encodeURIComponent("kupac@primjer.hr"), "x-naziv": encodeURIComponent("dosje-1541-2.pdf"), "x-naslov": encodeURIComponent("Dosje čestice 1541/2, k.o. Remete") };
  const n0 = brevo.calls.length; let rr = await m.dispatchFetch(W + "/izvjestaj", { method: "POST", headers: hdr, body: pdfB }); const mb = zadnjiMail().b;
  ok(rr.status === 200 && brevo.calls.length === n0 + 1 && mb.to[0].email === "kupac@primjer.hr" && mb.subject === "Dosje čestice 1541/2, k.o. Remete" && mb.attachment[0].name === "dosje-1541-2.pdf" && Buffer.from(mb.attachment[0].content, "base64").equals(Buffer.from(pdfB)), "Dosje kao PDF bajtovi: primatelj, naslov, naziv i isti sadržaj privitka");
  rr = await m.dispatchFetch(W + "/izvjestaj", { method: "POST", headers: hdr, body: new TextEncoder().encode("GIF89a" + "z".repeat(500)) }); ok(rr.status === 400, "Dosje kao bajtovi: privitak koji nije PDF odbijen");
  rr = await m.dispatchFetch(W + "/izvjestaj", { method: "POST", headers: { ...hdr, "x-email": "nije-email" }, body: pdfB }); ok(rr.status === 400, "Dosje kao bajtovi: neispravna adresa odbijena");
  const nn = brevo.calls.length; rr = await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "kupac@primjer.hr", pdf: PDF + '","to":[{"email":"zli@primjer.hr"}],"x":"' } });
  ok(rr.status === 400 && brevo.calls.length === nn, "Stari oblik: privitak s navodnikom (umetanje primatelja) odbijen"); }
// snimke DGU-a za dosje preko Workera (geoportal nema CORS)
{ const gu = "https://geoportal.dgu.hr/services/inspire/orthophoto_2011/wms?SERVICE=WMS&REQUEST=GetMap&LAYERS=OrthoImagery&WIDTH=560&HEIGHT=560&FORMAT=image%2Fjpeg";
  let rr = await call(m, "/slika?u=" + encodeURIComponent(gu)); ok(rr.status === 200 && rr.headers.get("content-type") === "image/jpeg" && rr.headers.get("access-control-allow-origin") === ORIGIN && (await rr.arrayBuffer()).byteLength === 6, "Snimka DGU-a prosljeđena s CORS zaglavljem");
  ok((await call(m, "/slika?u=" + encodeURIComponent("https://zli.example/services/inspire/x/wms?REQUEST=GetMap&FORMAT=image/png&WIDTH=10&HEIGHT=10"))).status === 403, "Snimka: drugi poslužitelj nije dopušten");
  ok((await call(m, "/slika?u=" + encodeURIComponent(gu.replace("GetMap", "GetCapabilities")))).status === 403, "Snimka: samo WMS GetMap slike");
  ok((await call(m, "/slika?u=" + encodeURIComponent(gu), { origin: "https://zli.example" })).status === 403 && (await m.dispatchFetch(W + "/slika?u=" + encodeURIComponent(gu))).status === 403, "Snimka: samo za dopuštene stranice (ne za tuđe ni bez podrijetla)"); }
// produženje na zahtjev korisnika
ok((await call(m, "/produzenje", { method: "POST", tok: P.token, body: {} })).status === 200 && zadnjiMail().b.subject === "ČesticaHR: zahtjev za produženje pristupa", "Korisnik može zatražiti produženje; administrator dobiva obavijest");
// administratorske radnje i dnevnik
await adm(m, C, "radnja", { id: Z.id, radnja: "produzi", nacin: "30" }); let r2 = await m.db.prepare("SELECT * FROM zahtjev WHERE id=?").bind(Z.id).first();
ok(Math.abs(r2.istice - (red.istice + 30 * 86400000)) < 2000 && !r2.trazi_produzenje, "Produži +30 dana od dosadašnjeg isteka");
await adm(m, C, "radnja", { id: Z.id, radnja: "produzi", nacin: "neograniceno" }); r2 = await m.db.prepare("SELECT * FROM zahtjev WHERE id=?").bind(Z.id).first(); ok(r2.istice === null && (await call(m, "/provjera", { tok: P.token })).status === 200, "Neograničen pristup");
await adm(m, C, "radnja", { id: Z.id, radnja: "produzi", nacin: "90" }); r2 = await m.db.prepare("SELECT * FROM zahtjev WHERE id=?").bind(Z.id).first(); ok(Math.abs(r2.istice - (Date.now() + 90 * 86400000)) < 5000, "Dodijeli 90 dana");
const nPos = brevo.calls.length; await adm(m, C, "radnja", { id: Z.id, radnja: "posalji" }); const kod2 = linkIz(brevo.calls[nPos].b.htmlContent, /<b[^>]*>([A-Z2-9-]{14})<\/b>/);
ok(kod2 && kod2 !== kod && (await call(m, "/prijava", { method: "POST", body: { kod } })).status === 401 && (await call(m, "/provjera", { tok: P.token })).status === 401, "Ponovno slanje: novi kod, stari kod i stare prijave više ne vrijede");
const P2 = await (await call(m, "/prijava", { method: "POST", body: { kod: kod2 } })).json(); ok(!!P2.token, "Novi kod radi");
// --- 7. istek i opoziv
await m.db.prepare("UPDATE zahtjev SET istice=? WHERE id=?").bind(Date.now() - 1000, Z.id).run();
ok((await call(m, "/provjera", { tok: P2.token })).status === 401 && /istekao/.test((await (await call(m, "/prijava", { method: "POST", body: { kod: kod2 } })).json()).error.poruka), "Istekao pristup više ne radi (i poruka kaže da je istekao)");
j = await (await adm(m, C, "zahtjevi")).json(); ok(j.zahtjevi.find((z) => z.id === Z.id).stanje === "istekao", "Admin vidi stanje »Istekao«");
await adm(m, C, "radnja", { id: Z.id, radnja: "produzi", nacin: "30" }); ok((await call(m, "/provjera", { tok: P2.token })).status === 200, "Produženjem istekli pristup ponovno radi");
await adm(m, C, "radnja", { id: Z.id, radnja: "opozovi" }); ok((await call(m, "/provjera", { tok: P2.token })).status === 401 && /opozvan/.test((await (await call(m, "/prijava", { method: "POST", body: { kod: kod2 } })).json()).error.poruka), "Opozvan pristup odmah prestaje vrijediti");
// odbijanje, dodavanje, trajanje iz postavki (bez izmjene koda)
r = await adm(m, C, "dodaj", { email: "arhitekt@primjer.hr", namjena: "arhitekt" }); const idA = (await r.json()).id;
await adm(m, C, "postavke", { trajanje_dana: 45 }); const nA = brevo.calls.length; await adm(m, C, "radnja", { id: idA, radnja: "odobri" });
ok(/45 dana od aktivacije/.test(brevo.calls[nA].b.htmlContent), "Trajanje pristupa mijenja se u postavkama administracije, bez izmjene koda");
r = await adm(m, C, "dodaj", { email: "odbij@primjer.hr" }); const idO = (await r.json()).id; await adm(m, C, "radnja", { id: idO, radnja: "odbij" });
j = await (await adm(m, C, "zahtjevi")).json(); ok(j.zahtjevi.find((z) => z.id === idO).stanje === "odbijen", "Odbijanje zahtjeva");
// --- 9. evidencija radnji
const D = (await (await adm(m, C, "dnevnik?z=" + Z.id)).json()).dnevnik.map((x) => x.radnja);
ok(["zahtjev", "potvrda adrese", "odobri", "aktivacija", "traži produženje", "produži", "ponovno pošalji kod", "opozovi"].every((x) => D.includes(x)) && !JSON.stringify(D).includes("kupac@"), "Dnevnik bilježi svaku radnju s vremenom (bez e-mail adrese i koda)");
// --- statistika i 10. bez dvostrukog brojanja
for (let i = 0; i < 3; i++) await call(m, "/dogadaj", { method: "POST", body: { e: "cestica", s: "sesija-1", o: "h-cestice-A", z: "Grad Zagreb" } });
await call(m, "/dogadaj", { method: "POST", body: { e: "cestica", s: "sesija-1", o: "h-cestice-B", z: "Primorsko-goranska" } });
await call(m, "/dogadaj", { method: "POST", body: { e: "cestica", s: "sesija-2", o: "h-cestice-A", z: "Grad Zagreb" } });
await call(m, "/dogadaj", { method: "POST", body: { e: "pokretanje", s: "sesija-1" } }); await call(m, "/dogadaj", { method: "POST", body: { e: "pokretanje", s: "sesija-1" } });
await call(m, "/dogadaj", { method: "POST", body: { e: "simulator", s: "sesija-1", o: "h-cestice-A", z: "Hogwarts" } });
ok((await call(m, "/dogadaj", { method: "POST", body: { e: "nepoznato" } })).status === 400, "Statistika: nepoznata vrsta događaja odbijena");
const PG = await (await adm(m, C, "pregled?r=7")).json();
ok(PG.dogadaji.cestica === 3 && PG.dogadaji.pokretanje === 1 && PG.dogadaji.simulator === 1, "Ponovljeni događaji se ne broje dvaput (3 analize, 1 pokretanje, 1 simulator)");
ok(PG.regije.length === 2 && PG.regije[0].dim === "Grad Zagreb" && PG.regije[0].n === 2 && !PG.regije.some((x) => x.dim === "Hogwarts"), "Regionalna statistika skupno po županiji; nepostojeća županija se ne sprema");
const dbE = JSON.stringify(await m.db.prepare("SELECT * FROM dogadaj").all()) + JSON.stringify(await m.db.prepare("SELECT * FROM ponavljanje").all());
ok(!dbE.includes("h-cestice-A") && !dbE.includes("sesija-1") && !dbE.includes("1.2.3.4"), "Statistika ne sprema česticu, sesiju ni IP adresu");
await call(m, "/dogadaj", { method: "POST", body: { e: "pokretanje", s: "s3", v: "preglednik-1" } });
ok(!(await m.db.prepare("SELECT COUNT(*) n FROM posjetitelj").first()).n, "Bez privole identifikator preglednika se ne sprema");
await call(m, "/dogadaj", { method: "POST", body: { e: "pokretanje", s: "s4", v: "preglednik-1", privola: true } });
ok((await m.db.prepare("SELECT COUNT(*) n FROM posjetitelj").first()).n === 1, "Uz privolu sprema se samo sažetak identifikatora po danu");
for (const f of ["simulator", "simulator", "troskovi", "hakiranje"]) await call(m, "/dogadaj", { method: "POST", body: { e: "zakljucano", s: "sz", o: f, f } });
for (const sid of ["a1", "a2", "a3", "a4"]) await call(m, "/dogadaj", { method: "POST", body: { e: "slobodno", s: sid } });
await call(m, "/dogadaj", { method: "POST", body: { e: "zahtjev_obrazac", s: "a1" } });
const PG2 = await (await adm(m, C, "pregled?r=30")).json();
ok(PG2.dogadaji.zakljucano === 2 && PG2.zakljucano.length === 2 && PG2.zakljucano.some((x) => x.dim === "simulator" && x.n === 1) && !PG2.zakljucano.some((x) => x.dim === "hakiranje"), "Zaključane funkcije: interes po funkciji, bez ponavljanja i bez nepoznatih naziva");
ok(PG2.dogadaji.slobodno === 4 && PG2.konverzijaSlob === 25, "Konverzija besplatne provjere: 1 zahtjev na 4 besplatna pregleda = 25 %");
ok(typeof PG2.koristeNapredno === "number" && typeof PG2.odobreniUkupno === "number", "Pokazatelj: odobreni korisnici koji koriste napredne funkcije");
ok(PG.zahtjeviUkupno >= 1 && PG.naCekanju >= 0 && typeof PG.aktivni7 === "number" && PG.razdoblje === 7, "Pregled: zahtjevi, na čekanju, aktivni korisnici za razdoblje 7 dana");
ok((await (await adm(m, C, "pregled?r=sve")).json()).razdoblje === "ukupno", "Pregled za razdoblje »ukupno«");
// dnevni zadatak: podsjetnik i rokovi čuvanja
await m.db.prepare("UPDATE zahtjev SET status='odobren', istice=?, podsjetnik=NULL, aktiviran=? WHERE id=?").bind(Date.now() + 2 * 86400000, Date.now() - 86400000, idA).run();
await m.db.prepare("UPDATE zahtjev SET stvoren=? WHERE email='x0@primjer.hr'").bind(Date.now() - 8 * 86400000).run();
const nD = brevo.calls.length; const wk = await m.getWorker(); await wk.scheduled({ cron: "17 5 * * *", scheduledTime: Date.now() });
ok(brevo.calls.slice(nD).some((c) => c.b.to[0].email === "arhitekt@primjer.hr" && /uskoro ističe/.test(c.b.subject)), "Dnevni zadatak: podsjetnik prije isteka");
ok(!(await m.db.prepare("SELECT id FROM zahtjev WHERE email='x0@primjer.hr'").first()), "Dnevni zadatak: nepotvrđeni zahtjevi stariji od 7 dana brišu se");
// brisanje osobnih podataka na zahtjev
await adm(m, C, "radnja", { id: idO, radnja: "obrisi" }); ok(!(await m.db.prepare("SELECT id FROM zahtjev WHERE id=?").bind(idO).first()), "Brisanje osobnih podataka na zahtjev korisnika");
// prijava poveznicom s e-maila (bez lozinke)
{ const nP = brevo.calls.length; const rp = await m.dispatchFetch(W + "/admin/poveznica", { method: "POST", headers: { "content-type": "application/json", "x-chr-admin": "1", origin: W, "cf-connecting-ip": "4.4.4.4" }, body: "{}" });
  const mp = brevo.calls[nP]; const lnk = linkIz(mp && mp.b.htmlContent, /href="(https:\/\/p\.example\/admin\/ulaz\?t=[^"]+)"/);
  ok(rp.status === 200 && mp && mp.b.to[0].email === "info@cesticahr.com" && lnk, "Prijava poveznicom: poveznica stiže samo na administratorski e-mail");
  const u1 = await m.dispatchFetch(lnk, { redirect: "manual" }), ck = (u1.headers.get("set-cookie") || "").split(";")[0];
  ok(u1.status === 303 && u1.headers.get("location") === "/admin" && /^__Host-/.test(ck) && (await adm(m, ck, "zahtjevi")).status === 200, "Klik na poveznicu prijavljuje u administraciju");
  ok((await m.dispatchFetch(lnk, { redirect: "manual" })).status === 400, "Poveznica vrijedi samo jednom");
  ok((await m.dispatchFetch(W + "/admin/ulaz?t=krivo", { redirect: "manual" })).status === 400, "Kriva poveznica ne prijavljuje");
  ok((await m.dispatchFetch(W + "/admin/poveznica", { method: "POST", headers: { "content-type": "application/json", origin: "https://zli.example" }, body: "{}" })).status === 403, "Tuđa stranica ne može tražiti poveznicu");
  for (let i = 0; i < 3; i++) await m.dispatchFetch(W + "/admin/poveznica", { method: "POST", headers: { "content-type": "application/json", "x-chr-admin": "1", origin: W, "cf-connecting-ip": "3.3.3.3" }, body: "{}" });
  ok((await m.dispatchFetch(W + "/admin/poveznica", { method: "POST", headers: { "content-type": "application/json", "x-chr-admin": "1", origin: W, "cf-connecting-ip": "3.3.3.3" }, body: "{}" })).status === 429, "Najviše 3 poveznice u 15 minuta"); }
// odjava
await adm(m, C, "odjava", {}); ok((await adm(m, C, "zahtjevi")).status === 401, "Odjava poništava sesiju");
// greška slanja ne ruši sustav
brevo.mode = "err"; L = await adminLogin(m, { kod: totp(TOTP, 1) }); r = await adm(m, L.c, "dodaj", { email: "greska@primjer.hr" }); const idG = (await r.json()).id;
j = await (await adm(m, L.c, "radnja", { id: idG, radnja: "odobri" })).json(); ok(j.ok && j.mail === false, "Kad slanje e-maila ne uspije, odobrenje je spremljeno i administrator to vidi (mail: false)"); brevo.mode = "ok";
const m5 = await mf({ TOKEN_SECRET: "" }); ok((await call(m5, "/prijava", { method: "POST", body: { kod: "x" } })).status === 503, "Bez tajni Worker ne radi"); await m5.dispose();
const m6 = await mf({ ADMIN_TOTP: "" }); const L6 = await adminLogin(m6, { kod: "" }); ok(L6.r.status === 200 && (await (await adm(m6, L6.c, "zahtjevi")).json()).mfa === false, "Bez ADMIN_TOTP prijava radi samo lozinkom, a administracija upozorava da MFA nije uključen"); await m6.dispose();
await m.dispose();
console.log(`${pass} prošlo, ${fail} palo`); if (fail) { console.log("PALO:\n - " + fails.join("\n - ")); process.exit(1); }

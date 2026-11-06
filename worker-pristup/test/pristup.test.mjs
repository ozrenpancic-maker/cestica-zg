// Lokalni test Workera u Miniflareu (workerd), s lažnim Brevoom. Ne šalje prave e-mailove i ne treba prave ključeve.
// Pokretanje: cd worker-pristup && npm install && npm test
import { Miniflare } from "miniflare";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

let pass = 0, fail = 0; const fails = [];
const ok = (c, n) => { if (c) pass++; else { fail++; fails.push(n); } };
const COMPAT = readFileSync(new URL("../wrangler.toml", import.meta.url), "utf8").match(/compatibility_date\s*=\s*"([^"]+)"/)[1];
const ORIGIN = "https://app.cesticahr.com", ADMIN = "admin-tajna-za-test-1234567890";
const brevo = { calls: [], mode: "ok" };
async function fakeBrevo(req) { const b = await req.json(); brevo.calls.push({ h: Object.fromEntries(req.headers), b }); return brevo.mode === "ok" ? new Response(JSON.stringify({ messageId: "x" }), { status: 201 }) : new Response("{}", { status: 500 }); }
function mf(vars = {}) {
  return new Miniflare({ modules: true, scriptPath: fileURLToPath(new URL("../src/index.js", import.meta.url)), compatibilityDate: COMPAT, kvNamespaces: ["KODOVI"],
    bindings: { ALLOWED_ORIGINS: ORIGIN, MAIL_FROM: "dosje@cesticahr.com", MAIL_REPLY: "info@cesticahr.com", IZVJESTAJA_DNEVNO: "2", TOKEN_EPOCH: "1",
      TOKEN_SECRET: "token-tajna-test-abcdefghijklmnop", CODE_PEPPER: "pepper-test-0123456789", ADMIN_SECRET: ADMIN, BREVO_KEY: "xkeysib-TEST-NE-PRAVI", ...vars },
    outboundService: (req) => new URL(req.url).hostname === "api.brevo.com" ? fakeBrevo(req) : new Response("blokirano u testu", { status: 599 }) });
}
const call = (m, path, { method = "GET", body, tok, origin = ORIGIN, ip = "1.2.3.4" } = {}) => m.dispatchFetch("https://p.example" + path, { method, headers: { origin, "cf-connecting-ip": ip, "content-type": "application/json", ...(tok ? { authorization: "Bearer " + tok } : {}) }, body: body == null ? undefined : JSON.stringify(body) });
const adm = (m, path, body, pw = ADMIN) => m.dispatchFetch("https://p.example" + path, { method: body ? "POST" : "GET", headers: { "content-type": "application/json", authorization: "Bearer " + pw }, body: body ? JSON.stringify(body) : undefined });
const PDF = Buffer.from("%PDF-1.4\n" + "x".repeat(400)).toString("base64");

let m = mf();
// --- administracija
ok((await adm(m, "/admin/kod", { oznaka: "x" }, "kriva")).status === 401, "Admin: kriva lozinka odbijena");
ok((await m.dispatchFetch("https://p.example/admin")).headers.get("content-type").startsWith("text/html") && !(await (await m.dispatchFetch("https://p.example/admin")).text()).includes(ADMIN), "Admin stranica se otvara i ne sadrži lozinku");
const K = await (await adm(m, "/admin/kod", { oznaka: "Ivan, ivan@primjer.hr", dana: 30 })).json();
ok(/^[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/.test(K.kod) && K.istice > Date.now() + 29 * 86400000, "Admin: novi kod XXXX-XXXX-XXXX, vrijedi 30 dana");
const keys = (await (await m.getKVNamespace("KODOVI")).list()).keys.map((k) => k.name).join(" ");
ok(!keys.includes(K.kod.replace(/-/g, "")) && !keys.includes(K.kod), "KV ne sadrži kod u čitljivom obliku (samo sažetak)");
const L = await (await adm(m, "/admin/kodovi")).json(); ok(L.kodovi.length === 1 && L.kodovi[0].oznaka.startsWith("Ivan") && !JSON.stringify(L).includes(K.kod), "Admin: popis kodova bez samih kodova");

// --- prijava
let r = await call(m, "/prijava", { method: "POST", body: { kod: K.kod.toLowerCase().replace(/-/g, " ") } }); const P = await r.json();
ok(r.status === 200 && P.token && P.istice === K.istice && r.headers.get("access-control-allow-origin") === ORIGIN, "Prijava: ispravan kod (mala slova, razmaci) daje token; CORS za aplikaciju");
ok((await call(m, "/provjera", { tok: P.token })).status === 200, "Provjera: valjan token");
ok((await call(m, "/prijava", { method: "POST", body: { kod: K.kod }, origin: "https://zli.example" })).status === 403, "Nedopušteno podrijetlo odbijeno");
const [pp, ss] = P.token.split("."), lazni = Buffer.from(JSON.stringify({ id: "x", exp: Date.now() + 1e10, v: "1" })).toString("base64url") + "." + ss;
ok((await call(m, "/provjera", { tok: lazni })).status === 401 && (await call(m, "/provjera", { tok: pp + ".abc" })).status === 401, "Krivotvoreni token odbijen");
for (let i = 0; i < 10; i++) await call(m, "/prijava", { method: "POST", body: { kod: "AAAA-BBBB-CCCC" }, ip: "9.9.9.9" });
ok((await call(m, "/prijava", { method: "POST", body: { kod: K.kod }, ip: "9.9.9.9" })).status === 429 && (await call(m, "/prijava", { method: "POST", body: { kod: K.kod }, ip: "8.8.8.8" })).status === 200, "Nakon 10 krivih pokušaja s iste IP adrese: čekanje sat vremena (druge adrese rade)");

// --- slanje dosjea
r = await call(m, "/izvjestaj", { method: "POST", body: { email: "kupac@primjer.hr", pdf: PDF, naziv: "dosje 735-58.pdf", naslov: "Dosje čestice 735/58" } });
ok(r.status === 401 && brevo.calls.length === 0, "Slanje bez prijave odbijeno, Brevo se ne zove");
r = await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "kupac@primjer.hr", pdf: PDF, naziv: "dosje 735-58.pdf", naslov: "Dosje čestice 735/58" } });
const c0 = brevo.calls[0];
ok(r.status === 200 && c0 && c0.h["api-key"] === "xkeysib-TEST-NE-PRAVI" && c0.b.to[0].email === "kupac@primjer.hr" && c0.b.attachment[0].name === "dosje_735-58.pdf" && c0.b.attachment[0].content === PDF && c0.b.sender.email === "dosje@cesticahr.com", "Slanje: Brevo dobiva primatelja, PDF i pošiljatelja; ključ samo u zaglavlju prema Brevu");
ok(!JSON.stringify(await r.clone().json()).includes("xkeysib"), "Odgovor aplikaciji ne sadrži ključ");
ok((await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "nije-email", pdf: PDF } })).status === 400, "Neispravan e-mail odbijen");
ok((await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "a@b.hr", pdf: Buffer.from("nije pdf " + "y".repeat(200)).toString("base64") } })).status === 400, "Privitak koji nije PDF odbijen");
await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "a@b.hr", pdf: PDF } });
r = await call(m, "/izvjestaj", { method: "POST", tok: P.token, body: { email: "a@b.hr", pdf: PDF } });
ok(r.status === 429 && brevo.calls.length === 2, "Dnevno ograničenje slanja po kodu (ovdje 2)");
brevo.mode = "err"; const m2 = mf(); const K2 = await (await adm(m2, "/admin/kod", { oznaka: "y" })).json(); const T2 = (await (await call(m2, "/prijava", { method: "POST", body: { kod: K2.kod } })).json()).token;
ok((await call(m2, "/izvjestaj", { method: "POST", tok: T2, body: { email: "a@b.hr", pdf: PDF } })).status === 502, "Greška Breva → jasna poruka, bez rušenja"); brevo.mode = "ok";

// --- opoziv i rok
const id = L.kodovi[0].id; ok((await adm(m, "/admin/opozovi", { id })).status === 200, "Admin: opoziv koda");
ok((await call(m, "/provjera", { tok: P.token })).status === 401 && (await call(m, "/prijava", { method: "POST", body: { kod: K.kod } })).status === 401, "Opozvan kod: postojeći token i nova prijava više ne rade");
const m3 = mf({ TOKEN_EPOCH: "2" }); const K3 = await (await adm(m3, "/admin/kod", {})).json(); const T3 = (await (await call(m3, "/prijava", { method: "POST", body: { kod: K3.kod } })).json()).token; await m3.dispose();
const m4 = mf(); ok((await call(m4, "/provjera", { tok: T3 })).status === 401, "Promjena TOKEN_EPOCH odjavljuje sve"); await m4.dispose();
const m5 = mf({ TOKEN_SECRET: "" }); ok((await call(m5, "/prijava", { method: "POST", body: { kod: "x" } })).status === 503, "Bez tajni Worker ne radi"); await m5.dispose();
const m6 = mf({ BREVO_KEY: "" }); const K6 = await (await adm(m6, "/admin/kod", {})).json(); const T6 = (await (await call(m6, "/prijava", { method: "POST", body: { kod: K6.kod } })).json()).token;
ok((await call(m6, "/izvjestaj", { method: "POST", tok: T6, body: { email: "a@b.hr", pdf: PDF } })).status === 503, "Bez Brevo ključa slanje javlja da nije postavljeno"); await m6.dispose();
await m.dispose(); await m2.dispose();
console.log(`${pass} prošlo, ${fail} palo`); if (fail) { console.log("PALO:\n - " + fails.join("\n - ")); process.exit(1); }

// Lokalni test Workera u Miniflareu (isti runtime kao Cloudflare, workerd) s lažnim Anthropic API-jem.
// Ne troši novac i ne treba pravi ključ. Pokretanje: cd worker && npm install && npm test
import { Miniflare } from "miniflare";
import { webcrypto as c } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

let pass = 0, fail = 0; const fails = [];
const ok = (cond, name) => { if (cond) pass++; else { fail++; fails.push(name); } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const TOML = readFileSync(new URL("../wrangler.toml", import.meta.url), "utf8");
const COMPAT = TOML.match(/compatibility_date\s*=\s*"([^"]+)"/)[1];
const ORIGIN = "https://ozrenpancic-maker.github.io";
const PW = "x".repeat(8) + "Ab3_" + "y".repeat(20), PEPPER = "test-pepper-123456789", SESSION = "test-session-secret-abcdef";
const enc = new TextEncoder();
const hk = async (k) => c.subtle.importKey("raw", enc.encode(k), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
const HASH = Buffer.from(await c.subtle.sign("HMAC", await hk(PEPPER), enc.encode(PW))).toString("hex");
const b64u = (b) => Buffer.from(b).toString("base64url");
async function forge(payload, secret = SESSION) { const p = b64u(JSON.stringify(payload)); return p + "." + b64u(await c.subtle.sign("HMAC", await hk(secret), enc.encode(p))); }

// lažni Anthropic API
const up = { calls: [], mode: "text", delay: 0 };
async function fakeAnthropic(req) {
  const body = await req.json(); up.calls.push({ headers: Object.fromEntries(req.headers), body });
  if (up.delay) await sleep(up.delay);
  if (up.mode === "throw") throw new Error("veza prekinuta");
  if (up.mode === "500") return new Response(JSON.stringify({ type: "error", error: { type: "api_error", message: "x" } }), { status: 500 });
  if (up.mode === "garbage") return new Response("{nepotpun", { status: 200 });
  if (up.mode === "console") return new Response(JSON.stringify({ type: "error", error: { type: "invalid_request_error", message: "You have reached your specified workspace API usage limits." } }), { status: 400 });
  const content = up.mode === "tool" ? [{ type: "tool_use", id: "tu_1", name: "getUrbanRules", input: {} }, { type: "tool_use", id: "tu_2", name: "commitApprovedChanges", input: { changeId: "x" } }, { type: "tool_use", id: "tu_3", name: "previewHouseChanges", input: {} }]
    : [{ type: "text", text: "KRATKO: test " + up.calls.length }];
  return new Response(JSON.stringify({ content, usage: { input_tokens: 4000, output_tokens: 200 } }), { status: 200, headers: { "content-type": "application/json" } });
}
function mf(vars = {}) {
  return new Miniflare({
    modules: true, scriptPath: fileURLToPath(new URL("../src/index.js", import.meta.url)), compatibilityDate: COMPAT,
    durableObjects: { GUARD: { className: "Guard", useSQLite: true } },
    bindings: { AI_ENABLED: "true", ALLOWED_ORIGINS: ORIGIN, MONTHLY_LIMIT_USD: "5", SESSION_EPOCH: "1", ANTHROPIC_API_KEY: "sk-ant-TEST-NE-PRAVI", LOGIN_HASH: HASH, LOGIN_PEPPER: PEPPER, SESSION_SECRET: SESSION, ...vars },
    outboundService: (req) => new URL(req.url).hostname === "api.anthropic.com" ? fakeAnthropic(req) : new Response("blokirano u testu", { status: 599 }),
  });
}
const H = (tok, o = ORIGIN) => ({ origin: o, "content-type": "application/json", ...(tok ? { authorization: "Bearer " + tok } : {}) });
const post = (m, path, body, tok, o) => m.dispatchFetch("https://w.example" + path, { method: "POST", headers: H(tok, o), body: typeof body === "string" ? body : JSON.stringify(body) });
const status = async (m, tok) => (await (await m.dispatchFetch("https://w.example/status", { headers: H(tok) })).json()).potrosnja;
let seq = 0; const tid = () => "turn-" + String(++seq).padStart(5, "0");
const chat = (turnId = tid(), step = 0, extra = {}) => ({ turnId, reqId: `${turnId}-${step}`, messages: [{ role: "user", content: "Što mogu graditi?" }],
  tools: ["getUrbanRules", "commitApprovedChanges", "previewHouseChanges", "undoLastApprovedChange", "eval"].map((n) => ({ name: n, description: "x", input_schema: { type: "object", properties: {} } })), ...extra });
const login = async (m) => (await (await post(m, "/login", { lozinka: PW })).json()).token;

console.log("compatibility_date iz wrangler.toml:", COMPAT);
// ---------- 1. SQLite Durable Object, gašenje, konfiguracija
let m = mf(); let tok = await login(m);
ok((await status(m, tok)).pohrana === "sqlite", "Durable Object koristi SQLite pohranu (jedina dostupna na besplatnom planu)");
ok(/new_sqlite_classes\s*=\s*\["Guard"\]/.test(TOML) && !/new_classes/.test(TOML), "wrangler.toml deklarira Guard kao SQLite klasu");
await m.dispose();
m = mf({ AI_ENABLED: "false" }); ok((await post(m, "/login", { lozinka: PW })).status === 503 && up.calls.length === 0, "AI_ENABLED=false gasi sve, model se ne zove"); await m.dispose();
m = mf({ SESSION_SECRET: "" }); ok((await (await post(m, "/login", { lozinka: PW })).json()).error.code === "NOT_CONFIGURED", "bez tajni Worker ne radi"); await m.dispose();

// ---------- 2. prijava i neovlašten pristup
m = mf();
ok((await post(m, "/login", { lozinka: PW }, null, "https://zlo.example")).status === 403, "nepoznato podrijetlo: 403");
ok((await post(m, "/chat", chat())).status === 401 && up.calls.length === 0, "bez tokena: 401, model se ne zove");
tok = await login(m);
const [pl] = tok.split("."), payload = JSON.parse(Buffer.from(pl, "base64url").toString());
const tampered = b64u(JSON.stringify({ ...payload, exp: payload.exp + 999999 })) + "." + tok.split(".")[1];
ok((await post(m, "/chat", chat(), tampered)).status === 401, "token s promijenjenim rokom: 401");
ok((await post(m, "/chat", chat(), await forge({ ...payload }, "kriva-tajna"))).status === 401, "token potpisan drugom tajnom: 401");
ok((await post(m, "/chat", chat(), await forge({ iat: 1, exp: Math.floor(Date.now() / 1000) - 5, ep: "1" }))).status === 401, "istekli token: 401");
ok((await post(m, "/chat", chat(), await forge({ iat: 1, exp: Math.floor(Date.now() / 1000) + 99, ep: "0" }))).status === 401, "token stare epohe: 401");
ok((await post(m, "/chat", chat(), "Bearer " + "a".repeat(700))).status === 401, "predugi token: 401");
for (const bad of [{ lozinka: 123 }, { lozinka: ["x"] }, { lozinka: PW.slice(0, 20) }, {}]) await post(m, "/login", bad);
let r = await post(m, "/login", { lozinka: "pogresna-lozinka-xxxxxxxxxxxx" });
ok(r.status === 429 && (await r.json()).error.code === "LOCKED", "5 neispravnih prijava (bilo kojeg oblika) zaključava prijavu");
ok((await post(m, "/login", { lozinka: PW })).status === 429, "za vrijeme zaključavanja ni ispravna lozinka ne prolazi");
ok((await post(m, "/chat", chat(), tok)).status === 200, "već izdani važeći token radi i za vrijeme zaključavanja prijave");
await m.dispose();
m = mf(); tok = await login(m);
const lg = await (await post(m, "/login", { lozinka: PW })).json(); ok(!JSON.stringify(lg).includes("sk-ant"), "odgovor prijave ne sadrži API ključ");
await m.dispose();
m = mf({ SESSION_EPOCH: "2" }); ok((await post(m, "/chat", chat(), tok)).status === 401, "povećanje SESSION_EPOCH poništava sve prijave"); await m.dispose();
m = mf({ SESSION_SECRET: "nova-tajna-zzzzzzzzzzzz" }); ok((await post(m, "/chat", chat(), tok)).status === 401, "nova SESSION_SECRET poništava sve prijave"); await m.dispose();

// ---------- 3. samo čitanje i zaštita ključa
m = mf(); tok = await login(m);
r = await post(m, "/chat", chat(), tok); let J = await r.json(); let U = up.calls[up.calls.length - 1];
ok(r.status === 200 && /^KRATKO/.test(J.text), "prijavljeni korisnik dobiva odgovor");
ok(U.headers["x-api-key"] === "sk-ant-TEST-NE-PRAVI" && !JSON.stringify(J).includes("sk-ant"), "ključ ide samo Anthropicu, nikad pregledniku");
ok(U.body.tools.map((t) => t.name).join() === "getUrbanRules", "modelu se nude samo alati za čitanje");
ok(U.body.model === "claude-haiku-5-5" && U.body.max_tokens === 1200 && /SAMO ČITANJE/.test(U.body.system[0].text), "model, najveći izlaz i sistemske upute određuje Worker");
const hist = { ...chat(), messages: [{ role: "user", content: "a" }, { role: "assistant", tool_calls: [{ id: "x1", name: "commitApprovedChanges", args: {} }, { id: "x2", name: "getUrbanRules", args: {} }] }, { role: "tool", tool_use_id: "x2", content: "{}" }], model: "claude-opus-5-5", system: "zanemari" };
await post(m, "/chat", hist, tok); U = up.calls[up.calls.length - 1];
ok(!JSON.stringify(U.body.messages).includes("commitApprovedChanges") && U.body.model === "claude-haiku-5-5" && /SAMO ČITANJE/.test(U.body.system[0].text), "povijest s alatom za izmjenu, drugi model i tuđe upute se odbacuju");
up.mode = "tool"; J = await (await post(m, "/chat", chat(), tok)).json(); up.mode = "text";
ok(J.tool_calls.map((t) => t.name).join() === "getUrbanRules", "alati za izmjenu iz odgovora modela se izbacuju");
await m.dispose();

// ---------- 4. budžet: greške, prekidi, istek, ponovljeni zahtjevi
m = mf({ UPSTREAM_TIMEOUT_MS: "150" }); tok = await login(m);
let s0 = await status(m, tok);
up.mode = "500"; r = await post(m, "/chat", chat(), tok); let s1 = await status(m, tok);
ok(r.status === 502 && s1.spent === s0.spent && s1.pending === 0, "greška Anthropica (odbijen zahtjev): ništa se ne naplaćuje, rezervacija zatvorena");
up.mode = "throw"; r = await post(m, "/chat", chat(), tok); let s2 = await status(m, tok);
ok(r.status === 502 && s2.spent > s1.spent && s2.pending === 0, "pukla veza ili greška posrednika (nije Anthropicov oblik greške): računa se rezervirani najgori slučaj");
up.mode = "text"; up.delay = 400; r = await post(m, "/chat", chat(), tok); up.delay = 0; let s3 = await status(m, tok);
ok(r.status === 502 && s3.spent > s2.spent && s3.pending === 0, "istek vremena: računa se najgori slučaj, rezervacija zatvorena");
up.mode = "garbage"; r = await post(m, "/chat", chat(), tok); let s4 = await status(m, tok); up.mode = "text";
ok(r.status === 502 && s4.spent > s3.spent, "uspješan, ali nečitljiv odgovor: računa se najgori slučaj");
up.mode = "console"; J = await (await post(m, "/chat", chat(), tok)).json(); up.mode = "text";
ok(J.error.code === "BUDGET_CONSOLE", "limit iz Claude Consolea se prepoznaje");
// ponovljeni zahtjev nakon uspjeha: isti odgovor, bez novog poziva i troška
const body = chat(); const n0 = up.calls.length;
const a1 = await (await post(m, "/chat", body, tok)).json(); const sa = await status(m, tok);
const a2 = await (await post(m, "/chat", body, tok)).json(); const sb = await status(m, tok);
ok(up.calls.length === n0 + 1 && a2.ponovljeno && a2.text === a1.text && sb.spent === sa.spent, "ponovljeni zahtjev (ista oznaka): spremljeni odgovor, bez novog poziva i troška");
// isti zahtjev dvaput istodobno (npr. dvostruki klik ili ponovno slanje dok prvi još traje)
up.delay = 100; const dup = chat(); const n1 = up.calls.length;
const both = await Promise.all([post(m, "/chat", dup, tok), sleep(30).then(() => post(m, "/chat", dup, tok))]); up.delay = 0;
ok(up.calls.length === n1 + 1 && both.map((x) => x.status).sort().join() === "200,409", "isti zahtjev istodobno: model se zove jednom, drugi dobiva 'u obradi'");
// ponavljanje nakon prekida: zahtjev koji nije uspio smije se ponoviti (novi poziv), ali prethodni je već naplaćen kao najgori slučaj
up.mode = "throw"; const fb = chat(); await post(m, "/chat", fb, tok); up.mode = "text"; const n2 = up.calls.length;
r = await post(m, "/chat", fb, tok); ok(r.status === 200 && up.calls.length === n2 + 1, "neuspjeli zahtjev se smije ponoviti s istom oznakom");
ok((await post(m, "/chat", { ...chat(), reqId: "drugo-pitanje-0" }, tok)).status === 400, "oznaka zahtjeva mora pripadati pitanju");
await m.dispose();
// rezervacija koju Worker nije zatvorio (npr. prekinut usred poziva) nakon isteka računa se kao potrošena
m = mf({ RES_TTL_MS: "200" }); tok = await login(m);
const ns = await m.getDurableObjectNamespace("GUARD"), stub = ns.get(ns.idFromName("glavni"));
const rv = await stub.reserve("turn-orphan1", "turn-orphan1-0", 0.01);
let so = await status(m, tok); ok(rv.ok && so.pending === 0.01, "otvorena rezervacija se vidi kao rezervirana");
await sleep(300); so = await status(m, tok);
ok(so.pending === 0 && Math.abs(so.spent - 0.01) < 1e-9, "nezatvorena rezervacija nakon isteka računa se kao potrošena (konzervativno)");
r = await post(m, "/chat", { ...chat("turn-orphan1"), reqId: "turn-orphan1-0" }, tok);
ok(r.status === 200, "zahtjev čija je rezervacija istekla može se ponoviti");
await m.dispose();

// ---------- 5. istodobnost: limit po minuti, budžet, broj koraka po pitanju
m = mf(); tok = await login(m); up.delay = 150;
let res = await Promise.all(Array.from({ length: 20 }, () => post(m, "/chat", chat(), tok)));
ok(res.filter((x) => x.status === 200).length === 12, "20 istodobnih zahtjeva: prolazi točno 12 (limit po minuti)");
up.delay = 0; await m.dispose();
m = mf({ MONTHLY_LIMIT_USD: "0.004" }); tok = await login(m); up.delay = 100; const nb = up.calls.length;
res = await Promise.all(Array.from({ length: 10 }, () => post(m, "/chat", chat(), tok))); up.delay = 0;
const okN = res.filter((x) => x.status === 200).length, rej = await Promise.all(res.filter((x) => x.status !== 200).map((x) => x.json()));
const sf = await status(m, tok);
ok(okN >= 1 && okN < 10 && rej.every((b) => b.error.code === "BUDGET") && up.calls.length - nb === okN, `budžet 0,004 $: od 10 istodobnih prolazi ${okN}, ostali odbijeni bez poziva modela`);
ok(sf.spent <= 0.004 && sf.pending === 0, "potrošnja ne prelazi granicu ni pri istodobnim zahtjevima");
await m.dispose();
m = mf(); tok = await login(m); const t6 = tid(); const codes = [];
for (let i = 0; i < 7; i++) codes.push((await post(m, "/chat", chat(t6, i), tok)).status);
ok(codes.slice(0, 6).every((x) => x === 200) && codes[6] === 429, "najviše 6 poziva modela po pitanju");
ok((await post(m, "/chat", { messages: [] }, tok)).status === 400, "zahtjev bez oznaka se odbija");
ok((await m.dispatchFetch("https://w.example/chat", { method: "POST", headers: H(tok), body: "x".repeat(90000) })).status === 413, "prevelik zahtjev se odbija");
ok((await m.dispatchFetch("https://w.example/admin", { headers: H(tok) })).status === 404, "nepoznata adresa: 404");
await m.dispose();

console.log(`\nWorker: ${pass} prošlo, ${fail} palo`);
if (fails.length) { console.log("PALO:\n - " + fails.join("\n - ")); process.exit(1); }

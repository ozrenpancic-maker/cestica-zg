// Čestica HR: zahtjevi za napredni pristup, odobravanje, pristupni kodovi, slanje dosjea na e-mail, administracija i
// skupna statistika korištenja (Cloudflare Worker + D1, besplatni plan). Model: poluautomatsko odobravanje — korisnik šalje
// zahtjev i potvrđuje adresu, administrator odobrava, sustav izdaje pojedinačni kod i šalje ga e-mailom.
// Tajne se NE upisuju ovdje ni u wrangler.toml, nego naredbom `npx wrangler secret put IME`:
//   TOKEN_SECRET  potpis tokena prijave (dugi slučajni niz)
//   CODE_PEPPER   tajna za sažetke kodova, e-mail adresa i IP adresa (ne mijenjati: stari kodovi prestaju vrijediti)
//   ADMIN_SECRET  administratorska lozinka (najmanje 20 znakova)
//   ADMIN_TOTP    tajna za drugi korak prijave (base32, aplikacija za autentifikaciju); bez nje administracija upozorava
//   BREVO_KEY     API ključ za slanje e-maila (Brevo, besplatna razina)
//   TURNSTILE_SECRET  neobavezno: Cloudflare Turnstile za zaštitu obrasca od robota
// D1: DB (shema u migrations/0001_init.sql). Ništa od toga ne ide u aplikaciju ni na web stranicu.
const enc = new TextEncoder();
const DAN = 86400000, SAT = 3600000;
const MAX_PDF = 6 * 1024 * 1024;
const NAMJENE = { kupujem: "Kupujem zemljište", gradnja: "Planiram gradnju kuće", arhitekt: "Arhitekt ili projektant", agencija: "Agencija za nekretnine", investitor: "Investitor", ostalo: "Ostalo" };
const VRSTE = { web_posjet: "Otvaranje web stranice", pokretanje: "Pokretanje aplikacije", pretraga: "Pretraživanje čestice", cestica: "Analizirana čestica", ocjena: "Pregled ocjene", simulator: "Simulator kuće", "3d": "3D prikaz", troskovi: "Izračun troškova", pdf: "PDF dosje", slobodno: "Besplatni pregled", zakljucano: "Pokušaj otvaranja zaključane funkcije", zahtjev_obrazac: "Zahtjev poslan iz aplikacije", napredno: "Korištenje naprednih funkcija (prijavljen)" };
const ZAKLJ = ["ocjena", "uvjeti", "pristup", "zk", "simulator", "3d", "troskovi", "materijal", "montazne", "energija", "pdf"];
const ZUPANIJE = ["Grad Zagreb", "Zagrebačka", "Krapinsko-zagorska", "Sisačko-moslavačka", "Karlovačka", "Varaždinska", "Koprivničko-križevačka", "Bjelovarsko-bilogorska", "Primorsko-goranska", "Ličko-senjska", "Virovitičko-podravska", "Požeško-slavonska", "Brodsko-posavska", "Zadarska", "Osječko-baranjska", "Šibensko-kninska", "Vukovarsko-srijemska", "Splitsko-dalmatinska", "Istarska", "Dubrovačko-neretvanska", "Međimurska"];
const IZVORI = ["izravno", "google", "bing", "facebook", "instagram", "linkedin", "whatsapp", "e-mail", "ostalo"];

const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const b64uStr = (s) => b64u(enc.encode(s));
const unb64u = (s) => { s = s.replace(/-/g, "+").replace(/_/g, "/"); while (s.length % 4) s += "="; return atob(s); };
async function hmac(secret, msg) { const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); return b64u(await crypto.subtle.sign("HMAC", k, enc.encode(msg))); }
function eqConst(a, b) { if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const normKod = (k) => String(k || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
const rnd = (n) => b64u(crypto.getRandomValues(new Uint8Array(n)));
// čitljiv kod bez dvosmislenih znakova (0/O, 1/I), kriptografski slučajan: XXXX-XXXX-XXXX (32^12 ≈ 1,2 · 10^18)
function noviKod() { const A = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789", r = crypto.getRandomValues(new Uint8Array(12)); let s = ""; for (let i = 0; i < 12; i++) { s += A[r[i] & 31]; if (i === 3 || i === 7) s += "-"; } return s; }
const dan = (t) => new Date(t == null ? Date.now() : t).toISOString().slice(0, 10);
const emailOk = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(e) && e.length <= 200;
const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
const datum = (t) => t ? new Date(t).toLocaleDateString("hr-HR", { timeZone: "Europe/Zagreb" }) : "";

function cors(env, req) {
  const o = req.headers.get("origin") || "", dozv = String(env.ALLOWED_ORIGINS || "").split(",").map((x) => x.trim()).filter(Boolean);
  const h = { vary: "origin" };
  if (dozv.includes(o)) Object.assign(h, { "access-control-allow-origin": o, "access-control-allow-headers": "content-type, authorization, x-email, x-naziv, x-naslov", "access-control-allow-methods": "GET, POST, OPTIONS", "access-control-max-age": "600" });
  return { h, dozvoljen: !o || dozv.includes(o) };
}
const SIG = { "x-content-type-options": "nosniff", "referrer-policy": "no-referrer", "strict-transport-security": "max-age=31536000" };
const json = (obj, status, h) => new Response(JSON.stringify(obj), { status: status || 200, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...SIG, ...(h || {}) } });
const greska = (code, poruka, status, h) => json({ error: { code, poruka } }, status, h);
const stranica = (naslov, tijelo, status) => new Response(`<!doctype html><html lang="hr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(naslov)}</title><style>body{font:17px/1.55 system-ui,sans-serif;max-width:560px;margin:0 auto;padding:32px 16px;color:#0b1210}a{color:#0f7a52}</style></head><body><h1 style="font-size:24px">${esc(naslov)}</h1>${tijelo}</body></html>`, { status: status || 200, headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'none'; style-src 'unsafe-inline'", ...SIG } });
const ip = (req) => req.headers.get("cf-connecting-ip") || "nepoznato";

// --- D1 pomoćne funkcije
const one = (env, sql, ...a) => env.DB.prepare(sql).bind(...a).first();
const all = async (env, sql, ...a) => (await env.DB.prepare(sql).bind(...a).all()).results || [];
const run = (env, sql, ...a) => env.DB.prepare(sql).bind(...a).run();
async function postavka(env, k, def) { const r = await one(env, "SELECT v FROM postavke WHERE k=?", k); return r ? r.v : def; }
async function trajanje(env) { const v = parseInt(await postavka(env, "trajanje_dana", env.TRAJANJE_DANA || "30"), 10); return v > 0 ? v : 30; }
async function zapis(env, akter, radnja, zid, detalj) { await run(env, "INSERT INTO dnevnik(t,akter,radnja,zahtjev_id,detalj) VALUES(?,?,?,?,?)", Date.now(), akter, radnja, zid || null, detalj || null); }
// ograničenje učestalosti: broj u prozoru (ključ sadrži sažetak IP adrese, ne samu adresu)
async function ogrBroj(env, k) { const r = await one(env, "SELECT n,istice FROM ogranicenje WHERE k=?", k); return r && r.istice > Date.now() ? r.n : 0; }
async function ogrPlus(env, k, ms) { const t = Date.now(); await run(env, "INSERT INTO ogranicenje(k,n,istice) VALUES(?,1,?) ON CONFLICT(k) DO UPDATE SET n=CASE WHEN istice<? THEN 1 ELSE n+1 END, istice=CASE WHEN istice<? THEN excluded.istice ELSE istice END", k, t + ms, t, t); }
const ipH = (env, req) => hmac(env.CODE_PEPPER, "ip:" + ip(req));
// statistika: skupni broj po danu, vrsti i jednoj dimenziji
async function brojDogadaj(env, vrsta, dim) { await run(env, "INSERT INTO dogadaj(dan,vrsta,dim,n) VALUES(?,?,?,1) ON CONFLICT(dan,vrsta,dim) DO UPDATE SET n=n+1", dan(), vrsta, dim || ""); }
// stanje zahtjeva prikazano administratoru (istekao se izvodi iz roka)
function stanje(z, t) { t = t || Date.now(); if (z.status === "odobren" && z.istice && z.istice < t) return "istekao"; if (z.status === "odobren" && !z.aktiviran && z.kod_rok && z.kod_rok < t) return "istekao"; return z.status; }

// Tijelo poruke za Brevo. Privitak (base64, nekoliko MB) umeće se spajanjem nizova, bez JSON.stringify i bez
// provjera znak po znak: besplatni Worker smije potrošiti najviše 10 ms procesora po zahtjevu.
function tijeloPoruke(o, attachment) {
  const j = JSON.stringify(o); if (!attachment || !attachment.length) return j;
  return j.slice(0, -1) + ',"attachment":[' + attachment.map((a) => '{"name":' + JSON.stringify(a.name) + ',"content":"' + a.content + '"}').join(",") + "]}";
}
// bajtovi u base64 (ugrađena funkcija ako postoji; inače u dijelovima)
function uBase64(u8) { if (typeof u8.toBase64 === "function") return u8.toBase64(); let s = ""; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }
// --- e-mail (Brevo); vraća true ako je poruka predana na slanje
async function posalji(env, to, subject, html, attachment) {
  if (!env.BREVO_KEY || !env.MAIL_FROM || !to) return false;
  const r = await fetch(env.MAIL_API || "https://api.brevo.com/v3/smtp/email", { method: "POST", headers: { "api-key": env.BREVO_KEY, "content-type": "application/json", accept: "application/json" },
    body: tijeloPoruke({ sender: { email: env.MAIL_FROM, name: "Čestica HR" }, to: [{ email: to }], replyTo: env.MAIL_REPLY ? { email: env.MAIL_REPLY } : undefined, subject, htmlContent: html }, attachment) }).catch(() => null);
  return !!(r && r.ok);
}
const potpis = `<p>Čestica HR · <a href="mailto:info@cesticahr.com">info@cesticahr.com</a></p>`;
function porukaOdobreno(env, kod, dana, rok) {
  const link = String(env.APP_URL || "https://app.cesticahr.com/") + "?pristup=" + encodeURIComponent(kod);
  return `<p>Vaš napredni pristup aplikaciji ČesticaHR je odobren.</p><p>Aktivirajte ga ovom poveznicom: <a href="${esc(link)}">${esc(link)}</a></p><p>ili upišite pristupni kod u aplikaciji: <b style="font-size:18px;letter-spacing:1px">${esc(kod)}</b></p>` +
    `<p>${dana ? `Pristup traje ${dana} dana od aktivacije.` : "Pristup nije vremenski ograničen."} Kod se može aktivirati do ${esc(datum(rok))}. Kod je osoban: ne dijelite ga.</p>` +
    `<p>Tijekom testne faze pristup je besplatan. Ako ovu poruku niste očekivali, zanemarite je.</p>` + potpis;
}

// --- token prijave: potpis, rok, epoha i verzija koda; stanje se svaki put provjerava u bazi
async function napraviToken(env, z) { const p = b64uStr(JSON.stringify({ id: z.id, kv: z.kod_izdan, exp: z.istice || Date.now() + 365 * DAN, v: String(env.TOKEN_EPOCH || "1") })); return p + "." + (await hmac(env.TOKEN_SECRET, p)); }
async function provjeriToken(env, req) {
  const a = req.headers.get("authorization") || "", t = a.startsWith("Bearer ") ? a.slice(7) : ""; const [p, s] = t.split(".");
  if (!p || !s || !eqConst(s, await hmac(env.TOKEN_SECRET, p))) return null;
  let P; try { P = JSON.parse(unb64u(p)); } catch (e) { return null; }
  if (!P || P.v !== String(env.TOKEN_EPOCH || "1") || !(P.exp > Date.now())) return null;
  const z = await one(env, "SELECT * FROM zahtjev WHERE id=?", String(P.id || ""));
  if (!z || z.status !== "odobren" || z.kod_izdan !== P.kv || stanje(z) !== "odobren") return null;
  if (!z.zadnja_akt || Date.now() - z.zadnja_akt > SAT) await run(env, "UPDATE zahtjev SET zadnja_akt=? WHERE id=?", Date.now(), z.id);
  return { z };
}

// --- javno: zahtjev za pristup (obrazac u aplikaciji i na web stranici)
async function zahtjev(env, req, H) {
  let b; try { b = await req.json(); } catch (e) { return greska("ZAHTJEV", "Neispravan zahtjev.", 400, H); }
  const ODG = json({ ok: true, poruka: "Ako adresa još nema zahtjev, na nju stiže e-mail s poveznicom za potvrdu. Zahtjev pregledavamo nakon potvrde adrese." }, 200, H);
  if (b && b.web) return ODG; // skriveno polje za robote: tiho odbaci
  const email = String(b && b.email || "").trim().toLowerCase(), namjena = NAMJENE[b && b.namjena] ? b.namjena : null;
  if (!emailOk(email)) return greska("EMAIL", "E-mail adresa nije ispravna.", 400, H);
  const ih = await ipH(env, req), rk = "zh:" + ih;
  if ((await ogrBroj(env, rk)) >= 5) return greska("PREVISE", "Previše zahtjeva s ove mreže. Pokušaj za sat vremena.", 429, H);
  await ogrPlus(env, rk, SAT);
  if (env.TURNSTILE_SECRET) {
    const f = new FormData(); f.append("secret", env.TURNSTILE_SECRET); f.append("response", String(b.ts || "")); f.append("remoteip", ip(req));
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: f }).then((x) => x.json()).catch(() => null);
    if (!r || !r.success) return greska("ROBOT", "Provjera da nisi robot nije uspjela. Pokušaj ponovno.", 400, H);
  }
  const eh = await hmac(env.CODE_PEPPER, "email:" + email), t = Date.now();
  let z = await one(env, "SELECT * FROM zahtjev WHERE email_h=?", eh);
  if (z) {
    const st = stanje(z, t);
    if (st === "ceka" || st === "odobren") return ODG; // već postoji: nema novog zahtjeva ni poruke
    if (st === "odbijen" && z.odluka && t - z.odluka < 30 * DAN) return ODG;
    if (st === "nepotvrden" && t - z.stvoren < 10 * 60000) return ODG; // ponovno slanje potvrde najranije za 10 minuta
  }
  const tok = rnd(24), th = await hmac(env.CODE_PEPPER, "potvrda:" + tok), id = z ? z.id : rnd(9);
  if (z) await run(env, "UPDATE zahtjev SET status='nepotvrden', namjena=?, stvoren=?, potvrda_h=?, potvrden=NULL, odluka=NULL, kod_h=NULL, kod_izdan=NULL, kod_rok=NULL, aktiviran=NULL, istice=NULL, trazi_produzenje=NULL, podsjetnik=NULL WHERE id=?", namjena, t, th, id);
  else await run(env, "INSERT INTO zahtjev(id,email,email_h,namjena,status,stvoren,potvrda_h) VALUES(?,?,?,?,'nepotvrden',?,?)", id, email, eh, namjena, t, th);
  await zapis(env, "korisnik", z ? "ponovni zahtjev" : "zahtjev", id, namjena ? NAMJENE[namjena] : null);
  const link = new URL(req.url).origin + "/potvrdi?i=" + encodeURIComponent(id) + "&t=" + encodeURIComponent(tok);
  await posalji(env, email, "ČesticaHR: potvrdi zahtjev za napredni pristup",
    `<p>Zaprimili smo vaš zahtjev za napredni pristup aplikaciji ČesticaHR. Nakon pregleda zahtjeva primit ćete obavijest na ovu e-mail adresu.</p><p>Da bismo zahtjev pregledali, potvrdite da je adresa vaša: <a href="${esc(link)}">potvrdi adresu</a> (poveznica vrijedi 7 dana).</p><p>Tijekom testne faze pristup je besplatan, a zahtjeve odobravamo pojedinačno. Ako zahtjev niste poslali vi, zanemarite ovu poruku: adresa se briše za 7 dana.</p>` + potpis);
  return ODG;
}
async function potvrdi(env, req, url) {
  const id = url.searchParams.get("i") || "", tok = url.searchParams.get("t") || "";
  const z = await one(env, "SELECT * FROM zahtjev WHERE id=?", id), t = Date.now();
  if (!z || z.status !== "nepotvrden" || !z.potvrda_h || !eqConst(z.potvrda_h, await hmac(env.CODE_PEPPER, "potvrda:" + tok)) || t - z.stvoren > 7 * DAN)
    return stranica("Poveznica nije valjana", `<p>Poveznica za potvrdu nije valjana ili je istekla. Zahtjev možeš poslati ponovno u aplikaciji.</p>`, 400);
  await run(env, "UPDATE zahtjev SET status='ceka', potvrden=?, potvrda_h=NULL WHERE id=?", t, id);
  await zapis(env, "korisnik", "potvrda adrese", id); await brojDogadaj(env, "zahtjev", z.namjena || "");
  if (env.ADMIN_EMAIL) await posalji(env, env.ADMIN_EMAIL, "Novi zahtjev za pristup ČesticaHR-u",
    `<p>Novi zahtjev za pristup ČesticaHR-u.</p><p>Namjena: ${esc(z.namjena ? NAMJENE[z.namjena] : "nije navedena")}<br>Zaprimljen: ${esc(datum(z.stvoren))}</p><p><a href="${esc(new URL(req.url).origin + "/admin")}">Otvori administraciju</a></p>`);
  return stranica("Adresa je potvrđena", `<p>Zaprimili smo vaš zahtjev za napredni pristup aplikaciji ČesticaHR. Nakon pregleda zahtjeva primit ćete obavijest na ovu e-mail adresu.</p>`);
}

// --- javno: prijava kodom (aktivacija pri prvoj prijavi), provjera, produženje, slanje dosjea
async function prijava(env, req, H) {
  const ih = await ipH(env, req), rl = "rl:" + ih;
  if ((await ogrBroj(env, rl)) >= 10) return greska("PREVISE", "Previše neuspjelih pokušaja. Pokušaj za sat vremena.", 429, H);
  let b; try { b = await req.json(); } catch (e) { return greska("ZAHTJEV", "Neispravan zahtjev.", 400, H); }
  const kod = normKod(b && b.kod); if (kod.length !== 12) { await ogrPlus(env, rl, SAT); return greska("KOD", "Kod nije ispravan.", 401, H); }
  const z = await one(env, "SELECT * FROM zahtjev WHERE kod_h=?", await hmac(env.CODE_PEPPER, "kod:" + kod)), t = Date.now(), st = z ? stanje(z, t) : null;
  if (!z || st !== "odobren") { await ogrPlus(env, rl, SAT); return greska("KOD", st === "opozvan" ? "Pristup je opozvan." : st === "istekao" ? "Pristup je istekao. Možeš zatražiti produženje." : "Kod nije ispravan.", 401, H); }
  if (!z.aktiviran) { z.aktiviran = t; z.istice = z.dana ? t + z.dana * DAN : null; await run(env, "UPDATE zahtjev SET aktiviran=?, istice=?, zadnja_akt=? WHERE id=?", z.aktiviran, z.istice, t, z.id); await zapis(env, "korisnik", "aktivacija", z.id, z.dana ? z.dana + " dana" : "neograničeno"); await brojDogadaj(env, "aktivacija", ""); }
  return json({ token: await napraviToken(env, z), istice: z.istice || null, oznaka: null }, 200, H);
}
async function produzenje(env, req, H, T) {
  if (!T.z.trazi_produzenje) { await run(env, "UPDATE zahtjev SET trazi_produzenje=? WHERE id=?", Date.now(), T.z.id); await zapis(env, "korisnik", "traži produženje", T.z.id);
    if (env.ADMIN_EMAIL) await posalji(env, env.ADMIN_EMAIL, "ČesticaHR: zahtjev za produženje pristupa", `<p>Korisnik traži produženje naprednog pristupa (ističe ${esc(datum(T.z.istice))}).</p><p><a href="${esc(new URL(req.url).origin + "/admin")}">Otvori administraciju</a></p>`); }
  return json({ ok: true }, 200, H);
}
async function izvjestaj(env, req, H, T) {
  if (!env.BREVO_KEY || !env.MAIL_FROM) return greska("NOT_CONFIGURED", "Slanje e-maila nije postavljeno.", 503, H);
  // Aplikacija šalje PDF kao bajtove (application/pdf), a adresu i naziv u zaglavljima. Stari oblik (JSON s base64) i dalje radi.
  let email, naziv, naslov, pdf;
  const dek = (v) => { try { return decodeURIComponent(v || ""); } catch (e) { return ""; } };
  if (/^application\/pdf/i.test(req.headers.get("content-type") || "")) {
    const dulj = +req.headers.get("content-length") || 0; if (dulj > MAX_PDF) return greska("PDF", "Dosje je prevelik za slanje.", 413, H);
    email = dek(req.headers.get("x-email")).trim(); naziv = dek(req.headers.get("x-naziv")); naslov = dek(req.headers.get("x-naslov"));
    if (!emailOk(email)) return greska("EMAIL", "E-mail adresa nije ispravna.", 400, H);
    const u8 = new Uint8Array(await req.arrayBuffer());
    if (u8.length > MAX_PDF) return greska("PDF", "Dosje je prevelik za slanje.", 413, H);
    if (u8.length < 100) return greska("PDF", "Dosje nije priložen.", 400, H);
    if (!(u8[0] === 0x25 && u8[1] === 0x50 && u8[2] === 0x44 && u8[3] === 0x46)) return greska("PDF", "Privitak nije PDF.", 400, H);
    pdf = uBase64(u8);
  } else {
    let b; try { b = await req.json(); } catch (e) { return greska("ZAHTJEV", "Neispravan zahtjev.", 400, H); }
    email = String(b && b.email || "").trim(); naziv = b && b.naziv; naslov = b && b.naslov; pdf = String(b && b.pdf || "");
    if (!emailOk(email)) return greska("EMAIL", "E-mail adresa nije ispravna.", 400, H);
    if (pdf.length < 100 || !/^JVBER/.test(pdf)) return greska("PDF", "Dosje nije priložen.", 400, H);
    if (pdf.length * 0.75 > MAX_PDF) return greska("PDF", "Dosje je prevelik za slanje.", 413, H);
    // pdf ide u tijelo poruke bez JSON.stringify: navodnik ili kosa crta ne smiju proći (indexOf je brz i za nekoliko MB)
    if (pdf.indexOf('"') >= 0 || pdf.indexOf("\\") >= 0 || /[^A-Za-z0-9+/=]/.test(pdf.slice(0, 4096))) return greska("PDF", "Privitak nije PDF.", 400, H);
  }
  naziv = String(naziv || "dosje-cestice.pdf").replace(/[^\w.-]/g, "_").slice(0, 80); naslov = String(naslov || "Dosje čestice").slice(0, 120);
  const lim = parseInt(env.IZVJESTAJA_DNEVNO || "10", 10), dk = "sl:" + T.z.id + ":" + dan();
  if ((await ogrBroj(env, dk)) >= lim) return greska("LIMIT", `Danas je poslano najviše ${lim} dosjea s ovim kodom. Pokušaj sutra.`, 429, H);
  const ok = await posalji(env, email, naslov, `<p>U privitku je dosje čestice iz aplikacije Čestica HR.</p><p>Dosje je sastavljen iz javnih podataka i izračuna aplikacije. Nije lokacijska informacija, izvadak iz zemljišne knjige ni projekt.</p>` + potpis,
    [{ name: naziv.endsWith(".pdf") ? naziv : naziv + ".pdf", content: pdf }]);
  if (!ok) return greska("SLANJE", "Slanje nije uspjelo. Pokušaj ponovno kasnije.", 502, H);
  await ogrPlus(env, dk, 2 * DAN);
  return json({ ok: true, poslano: email }, 200, H);
}
// --- javno: skupna statistika. Bez kolačića i bez IP adrese u bazi; čestica se ne sprema (samo sažetak za uklanjanje
// ponovljenih događaja, briše se nakon jednog dana); županija samo skupno. Identifikator preglednika samo uz privolu.
async function dogadaj(env, req, H) {
  let b; try { b = await req.json(); } catch (e) { return new Response(null, { status: 204, headers: H }); }
  const vrsta = String(b && b.e || ""); if (!VRSTE[vrsta]) return greska("VRSTA", "Nepoznat događaj.", 400, H);
  if (vrsta === "zakljucano" && !ZAKLJ.includes(b.f)) return greska("VRSTA", "Nepoznata funkcija.", 400, H);
  const ih = await ipH(env, req), rk = "ev:" + ih; if ((await ogrBroj(env, rk)) >= 600) return new Response(null, { status: 204, headers: H }); await ogrPlus(env, rk, SAT);
  const s = String(b.s || "").slice(0, 64), o = String(b.o || "").slice(0, 128);
  if (s) { const h = await hmac(env.CODE_PEPPER, "p:" + s + "|" + vrsta + "|" + o); const r = await run(env, "INSERT OR IGNORE INTO ponavljanje(h,istice) VALUES(?,?)", h, Date.now() + DAN); if (!(r.meta && r.meta.changes)) return new Response(null, { status: 204, headers: H }); }
  const dim = vrsta === "web_posjet" ? (IZVORI.includes(b.izvor) ? b.izvor : "ostalo") : vrsta === "zakljucano" ? (ZAKLJ.includes(b.f) ? b.f : "") : ZUPANIJE.includes(b.z) ? b.z : "";
  await brojDogadaj(env, vrsta, dim);
  if (b.v && b.privola === true) await run(env, "INSERT OR IGNORE INTO posjetitelj(dan,v_h) VALUES(?,?)", dan(), await hmac(env.CODE_PEPPER, "v:" + String(b.v).slice(0, 64)));
  return new Response(null, { status: 204, headers: H });
}

// --- administracija: lozinka + jednokratni kod (TOTP), sesija u kolačiću HttpOnly, sve ovlasti na poslužitelju
async function totpOk(env, kod) {
  if (!env.ADMIN_TOTP) return true;
  const c = String(kod || "").replace(/\s/g, ""); if (!/^\d{6}$/.test(c)) return false;
  const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567", s = String(env.ADMIN_TOTP).toUpperCase().replace(/[^A-Z2-7]/g, ""); let bits = "", by = [];
  for (const ch of s) bits += A.indexOf(ch).toString(2).padStart(5, "0"); for (let i = 0; i + 8 <= bits.length; i += 8) by.push(parseInt(bits.slice(i, i + 8), 2));
  const key = await crypto.subtle.importKey("raw", new Uint8Array(by), { name: "HMAC", hash: "SHA-1" }, false, ["sign"]), korak = Math.floor(Date.now() / 30000);
  const zadnji = parseInt(await postavka(env, "totp_zadnji", "0"), 10);
  for (const d of [-1, 0, 1]) { const st = korak + d; if (st <= zadnji) continue; const m = new ArrayBuffer(8); new DataView(m).setUint32(4, st); const hs = new Uint8Array(await crypto.subtle.sign("HMAC", key, m)), off = hs[19] & 15;
    const v = (((hs[off] & 127) << 24) | (hs[off + 1] << 16) | (hs[off + 2] << 8) | hs[off + 3]) % 1e6;
    if (eqConst(String(v).padStart(6, "0"), c)) { await run(env, "INSERT INTO postavke(k,v) VALUES('totp_zadnji',?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", String(st)); return true; } }
  return false;
}
const KOL = "__Host-chr_adm";
function kolacic(req) { const m = (req.headers.get("cookie") || "").match(new RegExp("(?:^|;\\s*)" + KOL + "=([^;]+)")); return m ? m[1] : null; }
async function adminSesija(env, req) { const k = kolacic(req); if (!k) return false; const r = await one(env, "SELECT istice FROM sesija WHERE h=?", await hmac(env.CODE_PEPPER, "s:" + k)); return !!(r && r.istice > Date.now()); }
async function adminPrijava(env, req) {
  const ih = await ipH(env, req), rk = "adm:" + ih;
  if ((await ogrBroj(env, rk)) >= 5) return greska("PREVISE", "Previše neuspjelih prijava. Pokušaj za 15 minuta.", 429);
  let b = {}; try { b = await req.json(); } catch (e) {}
  if (!env.ADMIN_SECRET || String(env.ADMIN_SECRET).length < 20 || !eqConst(String(b.lozinka || ""), env.ADMIN_SECRET) || !(await totpOk(env, b.kod))) { await ogrPlus(env, rk, 15 * 60000); await zapis(env, "admin", "neuspjela prijava"); return greska("ADMIN", "Prijava nije uspjela.", 401); }
  const tok = rnd(32), t = Date.now(); await run(env, "INSERT INTO sesija(h,istice) VALUES(?,?)", await hmac(env.CODE_PEPPER, "s:" + tok), t + 8 * SAT); await zapis(env, "admin", "prijava", null, env.ADMIN_TOTP ? "lozinka i jednokratni kod" : "samo lozinka (MFA nije uključen)");
  return json({ ok: true, mfa: !!env.ADMIN_TOTP }, 200, { "set-cookie": `${KOL}=${tok}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=28800` });
}
// prijava poveznicom: jednokratna poveznica na ADMIN_EMAIL (vrijedi 10 minuta), bez lozinke; sigurnost je sigurnost tog e-maila
async function adminPoveznica(env, req, url) {
  const ih = await ipH(env, req), rk = "adml:" + ih;
  if ((await ogrBroj(env, rk)) >= 3) return greska("PREVISE", "Poveznica je već poslana. Pogledaj e-mail ili pokušaj za 15 minuta.", 429);
  await ogrPlus(env, rk, 15 * 60000);
  if (!env.ADMIN_EMAIL || !env.BREVO_KEY) return greska("NOT_CONFIGURED", "Slanje e-maila nije postavljeno.", 503);
  const tok = rnd(32); await run(env, "INSERT INTO sesija(h,istice) VALUES(?,?)", await hmac(env.CODE_PEPPER, "l:" + tok), Date.now() + 10 * 60000);
  const link = url.origin + "/admin/ulaz?t=" + encodeURIComponent(tok);
  const ok = await posalji(env, env.ADMIN_EMAIL, "ČesticaHR: prijava u administraciju", `<p>Poveznica za prijavu u administraciju ČesticaHR (vrijedi 10 minuta, samo jednom):</p><p><a href="${esc(link)}">Prijavi se u administraciju</a></p><p>Ako prijavu nisi tražio ti, zanemari ovu poruku.</p>`);
  await zapis(env, "admin", "zatražena poveznica za prijavu", null, ok ? "poslana" : "slanje NIJE uspjelo");
  return ok ? json({ ok: true, na: env.ADMIN_EMAIL }) : greska("SLANJE", "Slanje e-maila nije uspjelo.", 502);
}
async function adminUlaz(env, req, url) {
  const t = url.searchParams.get("t") || "", h = await hmac(env.CODE_PEPPER, "l:" + t), r = await one(env, "SELECT istice FROM sesija WHERE h=?", h);
  if (!t || !r || r.istice < Date.now()) return stranica("Poveznica nije valjana", `<p>Poveznica je istekla ili je već upotrijebljena. <a href="/admin">Zatraži novu</a>.</p>`, 400);
  await run(env, "DELETE FROM sesija WHERE h=?", h);
  const tok = rnd(32); await run(env, "INSERT INTO sesija(h,istice) VALUES(?,?)", await hmac(env.CODE_PEPPER, "s:" + tok), Date.now() + 8 * SAT); await zapis(env, "admin", "prijava", null, "poveznicom s e-maila");
  return new Response(null, { status: 303, headers: { location: "/admin", "set-cookie": `${KOL}=${tok}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=28800`, "cache-control": "no-store", ...SIG } });
}
function zahtjevJson(z, t) { return { id: z.id, email: z.email, namjena: z.namjena ? NAMJENE[z.namjena] : null, stanje: stanje(z, t), stvoren: z.stvoren, potvrden: z.potvrden, odluka: z.odluka, aktiviran: z.aktiviran, istice: z.istice, dana: z.dana, zadnja_akt: z.zadnja_akt, trazi_produzenje: z.trazi_produzenje, kod_rok: z.kod_rok }; }
async function izdajKod(env, z, dana, nastavi) {
  const kod = noviKod(), t = Date.now(), rok = t + 30 * DAN;
  const ak = nastavi ? z.aktiviran : null, ist = nastavi ? z.istice : null;
  await run(env, "UPDATE zahtjev SET status='odobren', kod_h=?, kod_izdan=?, kod_rok=?, dana=?, aktiviran=?, istice=?, odluka=COALESCE(?,odluka), podsjetnik=NULL WHERE id=?", await hmac(env.CODE_PEPPER, "kod:" + normKod(kod)), t, rok, dana, ak, ist, nastavi ? null : t, z.id);
  const ok = await posalji(env, z.email, "Vaš napredni pristup aplikaciji ČesticaHR je odobren", porukaOdobreno(env, kod, dana, rok));
  return ok;
}
async function adminApi(env, req, url) {
  if (!(await adminSesija(env, req))) return greska("ADMIN", "Neovlašteno.", 401);
  if (req.method === "POST") { const o = req.headers.get("origin"); if (req.headers.get("x-chr-admin") !== "1" || (o && o !== url.origin)) return greska("ADMIN", "Neovlašteno.", 403); }
  const p = url.pathname.slice("/admin/api/".length), t = Date.now();
  if (p === "odjava" && req.method === "POST") { const k = kolacic(req); if (k) await run(env, "DELETE FROM sesija WHERE h=?", await hmac(env.CODE_PEPPER, "s:" + k)); await zapis(env, "admin", "odjava"); return json({ ok: true }, 200, { "set-cookie": `${KOL}=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0` }); }
  if (p === "zahtjevi") { const L = await all(env, "SELECT * FROM zahtjev WHERE status!='nepotvrden' ORDER BY stvoren DESC LIMIT 500"); return json({ zahtjevi: L.map((z) => zahtjevJson(z, t)), nepotvrdenih: (await one(env, "SELECT COUNT(*) n FROM zahtjev WHERE status='nepotvrden'")).n, mfa: !!env.ADMIN_TOTP, posta: !!env.BREVO_KEY }); }
  if (p === "dnevnik") { const z = url.searchParams.get("z"); const L = z ? await all(env, "SELECT * FROM dnevnik WHERE zahtjev_id=? ORDER BY id DESC LIMIT 200", z) : await all(env, "SELECT * FROM dnevnik ORDER BY id DESC LIMIT 200"); return json({ dnevnik: L }); }
  if (p === "postavke") {
    if (req.method === "POST") { let b = {}; try { b = await req.json(); } catch (e) {} const d = parseInt(b.trajanje_dana, 10); if (!(d >= 1 && d <= 3650)) return greska("POSTAVKE", "Trajanje mora biti od 1 do 3650 dana.", 400);
      await run(env, "INSERT INTO postavke(k,v) VALUES('trajanje_dana',?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", String(d)); await zapis(env, "admin", "postavke", null, "zadano trajanje " + d + " dana"); }
    return json({ trajanje_dana: await trajanje(env) });
  }
  if (p === "pregled") return json(await pregled(env, url.searchParams.get("r")));
  if (p === "dodaj" && req.method === "POST") {
    let b = {}; try { b = await req.json(); } catch (e) {} const email = String(b.email || "").trim().toLowerCase(); if (!emailOk(email)) return greska("EMAIL", "E-mail adresa nije ispravna.", 400);
    const eh = await hmac(env.CODE_PEPPER, "email:" + email); if (await one(env, "SELECT id FROM zahtjev WHERE email_h=?", eh)) return greska("POSTOJI", "Za tu adresu već postoji zahtjev.", 409);
    const id = rnd(9); await run(env, "INSERT INTO zahtjev(id,email,email_h,namjena,status,stvoren,potvrden,admin_dodao) VALUES(?,?,?,?,'ceka',?,?,1)", id, email, eh, NAMJENE[b.namjena] ? b.namjena : null, t, t); await zapis(env, "admin", "dodan korisnik", id);
    return json({ ok: true, id });
  }
  if (p === "radnja" && req.method === "POST") {
    let b = {}; try { b = await req.json(); } catch (e) {}
    const z = await one(env, "SELECT * FROM zahtjev WHERE id=?", String(b.id || "")); if (!z) return greska("NEMA", "Zahtjev ne postoji.", 404);
    const r = String(b.radnja || ""), st = stanje(z, t);
    if (r === "odobri") { if (!["ceka", "odbijen", "opozvan", "istekao"].includes(st)) return greska("STANJE", "Zahtjev se ne može odobriti u stanju: " + st + ".", 409);
      const dana = b.dana === 0 ? null : parseInt(b.dana, 10) > 0 ? parseInt(b.dana, 10) : await trajanje(env); const mail = await izdajKod(env, z, dana, false);
      await zapis(env, "admin", "odobri", z.id, (dana ? dana + " dana" : "neograničeno") + (mail ? ", kod poslan" : ", e-mail NIJE poslan")); return json({ ok: true, mail }); }
    if (r === "odbij") { if (st !== "ceka") return greska("STANJE", "Odbiti se može samo zahtjev na čekanju.", 409); await run(env, "UPDATE zahtjev SET status='odbijen', odluka=? WHERE id=?", t, z.id); await zapis(env, "admin", "odbij", z.id); return json({ ok: true }); }
    if (r === "opozovi") { if (st !== "odobren") return greska("STANJE", "Opozvati se može samo odobren pristup.", 409); await run(env, "UPDATE zahtjev SET status='opozvan', odluka=? WHERE id=?", t, z.id); await zapis(env, "admin", "opozovi", z.id); return json({ ok: true }); }
    if (r === "posalji") { if (st !== "odobren") return greska("STANJE", "Kod se ponovno šalje samo za odobren pristup.", 409); const mail = await izdajKod(env, z, z.dana, true); await zapis(env, "admin", "ponovno pošalji kod", z.id, mail ? "novi kod poslan, stari ne vrijedi" : "e-mail NIJE poslan"); return json({ ok: true, mail }); }
    if (r === "produzi") { if (!["odobren", "istekao"].includes(st)) return greska("STANJE", "Produžiti se može samo odobren ili istekao pristup.", 409);
      const n = String(b.nacin || "30"); let dana = z.dana, ist = z.istice;
      if (n === "neograniceno") { dana = null; ist = null; } else { const d = n === "90" ? 90 : 30; if (z.aktiviran) ist = n === "90" ? t + 90 * DAN : Math.max(z.istice || t, t) + 30 * DAN; else dana = n === "90" ? 90 : (z.dana || 0) + 30; if (z.aktiviran && dana != null) dana = Math.round((ist - z.aktiviran) / DAN); }
      await run(env, "UPDATE zahtjev SET dana=?, istice=?, status='odobren', trazi_produzenje=NULL, podsjetnik=NULL, kod_rok=CASE WHEN aktiviran IS NULL THEN ? ELSE kod_rok END WHERE id=?", dana, ist, t + 30 * DAN, z.id);
      await zapis(env, "admin", "produži", z.id, n === "neograniceno" ? "neograničeno" : n === "90" ? "90 dana" : "+30 dana"); return json({ ok: true }); }
    if (r === "obrisi") { await run(env, "DELETE FROM zahtjev WHERE id=?", z.id); await zapis(env, "admin", "brisanje osobnih podataka", z.id); return json({ ok: true }); }
    return greska("NEMA", "Nepoznata radnja.", 404);
  }
  return greska("NEMA", "Nepoznata adresa.", 404);
}
// pokazatelji za razdoblje (7, 30, 90 dana ili ukupno); svi iz baze, bez procjena
async function pregled(env, r) {
  const t = Date.now(), d = ["7", "30", "90"].includes(r) ? parseInt(r, 10) : null, od = d ? dan(t - (d - 1) * DAN) : "0000-00-00", odT = d ? t - d * DAN : 0;
  const zbroj = async (v) => ((await one(env, "SELECT COALESCE(SUM(n),0) n FROM dogadaj WHERE vrsta=? AND dan>=?", v, od)) || {}).n || 0;
  const P = {}; for (const v of [...Object.keys(VRSTE), "zahtjev", "aktivacija"]) P[v] = await zbroj(v);
  const Z = await all(env, "SELECT status,istice,aktiviran,kod_rok,zadnja_akt,potvrden FROM zahtjev WHERE status!='nepotvrden'");
  const st = Z.map((z) => stanje(z, t));
  const povratni = ((await one(env, "SELECT COUNT(*) n FROM (SELECT v_h FROM posjetitelj WHERE dan>=? GROUP BY v_h HAVING COUNT(*)>=2)", od)) || {}).n || 0;
  const jedinstveni = ((await one(env, "SELECT COUNT(DISTINCT v_h) n FROM posjetitelj WHERE dan>=?", od)) || {}).n || 0;
  const regije = await all(env, "SELECT dim, SUM(n) n FROM dogadaj WHERE vrsta='cestica' AND dim!='' AND dan>=? GROUP BY dim ORDER BY n DESC", od);
  const izvori = await all(env, "SELECT dim, SUM(n) n FROM dogadaj WHERE vrsta='web_posjet' AND dan>=? GROUP BY dim ORDER BY n DESC", od);
  const zakljucano = await all(env, "SELECT dim, SUM(n) n FROM dogadaj WHERE vrsta='zakljucano' AND dim!='' AND dan>=? GROUP BY dim ORDER BY n DESC", od);
  const odob = Z.filter((z) => z.status === "odobren"), koriste = odob.filter((z) => z.aktiviran && z.zadnja_akt && z.zadnja_akt >= odT).length;
  const niz = await all(env, "SELECT dan, vrsta, SUM(n) n FROM dogadaj WHERE dan>=? AND vrsta IN ('pokretanje','cestica','simulator','3d','pdf','zahtjev') GROUP BY dan, vrsta ORDER BY dan", d ? od : dan(t - 89 * DAN));
  return { razdoblje: d || "ukupno", od: d ? od : null, dogadaji: P, zahtjeviUkupno: Z.filter((z) => !d || (z.potvrden || 0) >= odT).length, naCekanju: st.filter((s) => s === "ceka").length,
    odobreni: st.filter((s) => s === "odobren").length, aktivni7: Z.filter((z) => stanje(z, t) === "odobren" && z.zadnja_akt > t - 7 * DAN).length, aktivni30: Z.filter((z) => stanje(z, t) === "odobren" && z.zadnja_akt > t - 30 * DAN).length,
    povratni, jedinstveni, konverzija: P.pokretanje ? Math.round((P.zahtjev / P.pokretanje) * 1000) / 10 : null,
    konverzijaSlob: P.slobodno ? Math.round((P.zahtjev_obrazac / P.slobodno) * 1000) / 10 : null, zakljucano, odobreniUkupno: odob.length, koristeNapredno: koriste, regije, izvori, niz };
}

// --- dnevni zadatak: podsjetnik prije isteka i rokovi čuvanja podataka
async function dnevno(env) {
  const t = Date.now();
  for (const z of await all(env, "SELECT * FROM zahtjev WHERE status='odobren' AND istice IS NOT NULL AND istice>? AND istice<? AND podsjetnik IS NULL", t, t + 5 * DAN)) {
    const ok = await posalji(env, z.email, "ČesticaHR: napredni pristup uskoro ističe", `<p>Vaš napredni pristup aplikaciji ČesticaHR ističe ${esc(datum(z.istice))}.</p><p>Ako želite nastaviti, u aplikaciji odaberite „Zatraži produženje”. Zahtjev pregledavamo pojedinačno.</p>` + potpis);
    if (ok) { await run(env, "UPDATE zahtjev SET podsjetnik=? WHERE id=?", t, z.id); await zapis(env, "sustav", "podsjetnik prije isteka", z.id); }
  }
  // rokovi čuvanja (vidi obavijest o privatnosti)
  await run(env, "DELETE FROM zahtjev WHERE status='nepotvrden' AND stvoren<?", t - 7 * DAN);
  await run(env, "DELETE FROM zahtjev WHERE status='odbijen' AND odluka<?", t - 90 * DAN);
  await run(env, "DELETE FROM zahtjev WHERE status='opozvan' AND odluka<?", t - 365 * DAN);
  await run(env, "DELETE FROM zahtjev WHERE status='odobren' AND istice IS NOT NULL AND istice<?", t - 365 * DAN);
  await run(env, "DELETE FROM ponavljanje WHERE istice<?", t); await run(env, "DELETE FROM ogranicenje WHERE istice<?", t); await run(env, "DELETE FROM sesija WHERE istice<?", t);
  await run(env, "DELETE FROM posjetitelj WHERE dan<?", dan(t - 90 * DAN));
  await run(env, "DELETE FROM dnevnik WHERE t<?", t - 2 * 365 * DAN);
}

function adminHtml(nonce) {
  return `<!doctype html><html lang="hr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Čestica HR – administracija</title>
<style nonce="${nonce}">body{font:15px/1.5 system-ui,sans-serif;max-width:1100px;margin:0 auto;padding:16px;color:#0b1210;background:#fff}h1{font-size:22px}h2{font-size:18px;margin:24px 0 8px}input,select,button{font:inherit;padding:9px 11px;border-radius:8px;border:1px solid #b9c2be;min-height:40px}button{background:#0b1210;color:#fff;border:0;cursor:pointer}button.s{background:#fff;color:#0b1210;border:1px solid #b9c2be}button.d{background:#b3261e}
.kp{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px}.kp div{border:1px solid #e3e8e5;border-radius:10px;padding:10px}.kp b{display:block;font-size:24px}.kp small{color:#5b6661;display:block}
table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #e3e8e5;padding:7px 4px;text-align:left;font-size:13.5px;vertical-align:top}.tw{overflow-x:auto}.st{font-weight:600}.st-ceka{color:#a86400}.st-odobren{color:#1f7a3f}.st-odbijen,.st-opozvan{color:#b3261e}.st-istekao{color:#5b6661}
.warn{background:#fbefd9;padding:8px 10px;border-radius:8px}.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}svg{max-width:100%}label{display:block;margin:8px 0 4px}[hidden]{display:none!important}</style></head><body>
<h1>Čestica HR · administracija</h1>
<section id="log"><p>Prijava je samo za administratora.</p><p><button id="pov">Pošalji mi poveznicu za prijavu</button></p><p id="pp" role="status"></p><p style="color:#5b6661">ili lozinkom:</p><label for="lz">Lozinka</label><input id="lz" type="password" autocomplete="current-password" style="width:100%;max-width:420px"><label for="mfa">Jednokratni kod (aplikacija za autentifikaciju)</label><input id="mfa" inputmode="numeric" autocomplete="one-time-code" maxlength="6"><p><button id="ul">Prijavi se</button></p><p id="lp" role="status"></p></section>
<section id="app" hidden><div class="row"><button class="s" id="od">Odjava</button><label for="rz" style="margin:0">Razdoblje</label><select id="rz"><option value="7">7 dana</option><option value="30" selected>30 dana</option><option value="90">90 dana</option><option value="sve">ukupno</option></select></div>
<p id="upoz"></p><h2>Pokazatelji</h2><div class="kp" id="kp"></div><h2>Kroz vrijeme</h2><div id="gr"></div><h2>Područja (analizirane čestice po županiji)</h2><div id="reg"></div><h2>Zaključane funkcije koje zanimaju posjetitelje</h2><div id="zak"></div>
<h2>Zahtjevi</h2><div class="row"><input id="ne" placeholder="e-mail novog korisnika" aria-label="e-mail novog korisnika"><button class="s" id="nd">Dodaj korisnika</button></div><div class="tw" id="tz"></div>
<h2>Postavke</h2><div class="row"><label for="tr" style="margin:0">Zadano trajanje pristupa (dana od aktivacije)</label><input id="tr" type="number" min="1" max="3650" style="width:110px"><button class="s" id="ts">Spremi</button></div>
<h2>Dnevnik radnji</h2><div class="tw" id="dn"></div></section>
<script nonce="${nonce}">
const $=id=>document.getElementById(id), e=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]), d=t=>t?new Date(t).toLocaleDateString("hr-HR"):"–";
const api=(p,b)=>fetch("/admin/api/"+p,b?{method:"POST",headers:{"content-type":"application/json","x-chr-admin":"1"},body:JSON.stringify(b),credentials:"same-origin"}:{credentials:"same-origin"}).then(async r=>{const j=await r.json().catch(()=>({})); if(r.status===401){$("app").hidden=true;$("log").hidden=false;} if(!r.ok) throw new Error(j.error&&j.error.poruka||"greška"); return j;});
const ST={ceka:"Na čekanju",odobren:"Odobren",odbijen:"Odbijen",istekao:"Istekao",opozvan:"Opozvan"};
const DEF={pokretanje:["Pokretanja aplikacije","otvaranja aplikacije (jedno po učitavanju)"],cestica:["Analizirane čestice","različite čestice po učitavanju aplikacije"],simulator:["Korištenja simulatora","kuća iz simulatora prikazana na čestici (jednom po čestici i učitavanju)"],"3d":["Otvoreni 3D prikazi","otvaranja 3D pogleda po čestici i učitavanju"],pdf:["Generirani PDF dosjei","složeni dosjei (ispis ili slanje e-mailom)"],ocjena:["Pregledi ocjene","prikazi ocjene čestice"],troskovi:["Izračuni troškova","prvi izračun investicije po čestici"],pretraga:["Pretraživanja","pretraživanja po adresi ili broju čestice"],web_posjet:["Posjeti web stranice","otvaranja web stranice (stranica mora slati događaj)"]};
async function sve(){ const r=$("rz").value; const [P,Z,S,D]=await Promise.all([api("pregled?r="+r),api("zahtjevi"),api("postavke"),api("dnevnik")]);
  $("upoz").innerHTML=(Z.mfa?"":'<span class="warn">Drugi korak prijave (MFA) nije uključen: postavi tajnu ADMIN_TOTP.</span> ')+(Z.posta?"":'<span class="warn">Slanje e-maila nije postavljeno (BREVO_KEY): kodovi se ne šalju.</span>');
  const k=[["Zahtjevi za pristup",P.zahtjeviUkupno,"potvrđeni zahtjevi u razdoblju"],["Na čekanju",P.naCekanju,"trenutno"],["Odobreni korisnici",P.odobreni,"trenutno aktivan odobren pristup"],["Aktivni (7 dana)",P.aktivni7,"odobreni korisnici s prijavom u zadnjih 7 dana"],["Aktivni (30 dana)",P.aktivni30,"odobreni korisnici s prijavom u zadnjih 30 dana"],["Aktivacije",P.dogadaji.aktivacija,"prve prijave kodom u razdoblju"],
    ...["web_posjet","pokretanje","cestica","ocjena","simulator","3d","troskovi","pdf"].map(v=>[DEF[v][0],P.dogadaji[v],DEF[v][1]]),["Povratni preglednici",P.povratni,"samo uz privolu: preglednici viđeni u barem 2 dana (od "+P.jedinstveni+")"],["Zahtjev nakon pokretanja",P.konverzija==null?"–":P.konverzija+" %","zahtjevi ÷ pokretanja aplikacije u razdoblju"],
    ["Besplatni pregledi",P.dogadaji.slobodno,"učitavanja aplikacije s barem jednim besplatnim pregledom čestice"],["Pokušaji zaključanih funkcija",P.dogadaji.zakljucano,"otvaranja zaključane funkcije (jednom po funkciji i učitavanju)"],
    ["Konverzija besplatne provjere",P.konverzijaSlob==null?"–":P.konverzijaSlob+" %","zahtjevi poslani iz aplikacije ÷ učitavanja s besplatnim pregledom"],["Odobreni koji koriste",P.koristeNapredno+" od "+P.odobreniUkupno,"odobreni i aktivirani korisnici s prijavom u razdoblju"]];
  $("kp").innerHTML=k.map(x=>'<div><small>'+e(x[0])+'</small><b>'+e(x[1])+'</b><small>'+e(x[2])+'</small></div>').join("");
  const dani=[...new Set(P.niz.map(x=>x.dan))], V=["pokretanje","cestica","simulator","3d","pdf","zahtjev"], C={pokretanje:"#5b6661",cestica:"#0f7a52",simulator:"#1565c0",["3d"]:"#a86400",pdf:"#6a1b9a",zahtjev:"#b3261e"};
  $("gr").innerHTML=dani.length?V.map(v=>{const pts=dani.map(dd=>{const x=P.niz.find(y=>y.dan===dd&&y.vrsta===v);return x?x.n:0}), mx=Math.max(1,...pts), w=Math.max(4,Math.floor(640/dani.length));
    return '<p style="margin:8px 0 2px">'+e(v==="zahtjev"?"Zahtjevi":DEF[v][0])+' (najveći dnevni broj: '+mx+')</p><svg width="'+(w*dani.length)+'" height="48" role="img" aria-label="'+e(v)+' po danu">'+pts.map((n,i)=>'<rect x="'+(i*w)+'" y="'+(46-Math.round(44*n/mx))+'" width="'+(w-1)+'" height="'+Math.round(44*n/mx)+'" fill="'+C[v]+'"><title>'+e(dani[i])+': '+n+'</title></rect>').join("")+'</svg>';}).join(""):"<p>Još nema događaja.</p>";
  $("zak").innerHTML=P.zakljucano.length?'<table><tr><th>Funkcija</th><th>Pokušaja</th></tr>'+P.zakljucano.map(x=>'<tr><td>'+e(x.dim)+'</td><td>'+x.n+'</td></tr>').join("")+'</table>':"<p>Još nema podataka.</p>";
  $("reg").innerHTML=P.regije.length?'<table><tr><th>Županija</th><th>Čestica</th></tr>'+P.regije.map(x=>'<tr><td>'+e(x.dim)+'</td><td>'+x.n+'</td></tr>').join("")+'</table>':"<p>Još nema podataka.</p>";
  $("tz").innerHTML='<table><tr><th>E-mail</th><th>Zahtjev</th><th>Namjena</th><th>Status</th><th>Odobren</th><th>Ističe</th><th>Zadnja aktivnost</th><th>Radnje</th></tr>'+Z.zahtjevi.map(z=>'<tr><td>'+e(z.email)+(z.trazi_produzenje?'<br><small class="st-ceka">traži produženje</small>':"")+'</td><td>'+d(z.stvoren)+'</td><td>'+e(z.namjena||"–")+'</td><td class="st st-'+z.stanje+'">'+ST[z.stanje]+'</td><td>'+d(z.odluka&&z.stanje!=="ceka"?z.odluka:null)+'</td><td>'+(z.stanje==="odobren"&&!z.aktiviran?"nije aktiviran":z.istice?d(z.istice):z.stanje==="odobren"?"neograničeno":"–")+'</td><td>'+d(z.zadnja_akt)+'</td><td><div class="row">'+
    (["ceka","odbijen","opozvan","istekao"].includes(z.stanje)?'<button data-r="odobri" data-i="'+e(z.id)+'">Odobri</button>':"")+(z.stanje==="ceka"?'<button class="s" data-r="odbij" data-i="'+e(z.id)+'">Odbij</button>':"")+
    (["odobren","istekao"].includes(z.stanje)?'<button class="s" data-r="produzi" data-n="30" data-i="'+e(z.id)+'">+30 dana</button><button class="s" data-r="produzi" data-n="90" data-i="'+e(z.id)+'">90 dana</button><button class="s" data-r="produzi" data-n="neograniceno" data-i="'+e(z.id)+'">Neograničeno</button>':"")+
    (z.stanje==="odobren"?'<button class="s" data-r="posalji" data-i="'+e(z.id)+'">Ponovno pošalji kod</button><button class="d" data-r="opozovi" data-i="'+e(z.id)+'">Opozovi</button>':"")+'<button class="s" data-r="dnevnik" data-i="'+e(z.id)+'">Dnevnik</button><button class="s" data-r="obrisi" data-i="'+e(z.id)+'">Obriši podatke</button></div></td></tr>').join("")+'</table><p><small>Nepotvrđenih adresa (ne prikazuju se, brišu se za 7 dana): '+Z.nepotvrdenih+'</small></p>';
  $("tr").value=S.trajanje_dana;
  $("dn").innerHTML='<table><tr><th>Vrijeme</th><th>Tko</th><th>Radnja</th><th>Detalj</th></tr>'+D.dnevnik.slice(0,60).map(x=>'<tr><td>'+new Date(x.t).toLocaleString("hr-HR")+'</td><td>'+e(x.akter)+'</td><td>'+e(x.radnja)+'</td><td>'+e(x.detalj||"")+'</td></tr>').join("")+'</table>';
}
$("ul").onclick=async()=>{ try{ await fetch("/admin/prijava",{method:"POST",headers:{"content-type":"application/json","x-chr-admin":"1"},credentials:"same-origin",body:JSON.stringify({lozinka:$("lz").value,kod:$("mfa").value})}).then(async r=>{const j=await r.json(); if(!r.ok) throw new Error(j.error&&j.error.poruka);}); $("lz").value=""; $("mfa").value=""; $("log").hidden=true; $("app").hidden=false; await sve(); }catch(x){ $("lp").textContent=x.message||"Prijava nije uspjela."; } };
$("pov").onclick=async()=>{ $("pp").textContent="Šaljem…"; try{ const r=await fetch("/admin/poveznica",{method:"POST",headers:{"content-type":"application/json","x-chr-admin":"1"},credentials:"same-origin",body:"{}"}); const j=await r.json(); $("pp").textContent=r.ok?"Poveznica je poslana na "+j.na+". Otvori e-mail i klikni je (vrijedi 10 minuta).":(j.error&&j.error.poruka||"Slanje nije uspjelo."); }catch(x){ $("pp").textContent="Slanje nije uspjelo."; } };
$("od").onclick=async()=>{ await api("odjava",{}).catch(()=>{}); location.reload(); };
$("rz").onchange=()=>sve().catch(x=>alert(x.message));
$("ts").onclick=()=>api("postavke",{trajanje_dana:+$("tr").value}).then(sve).catch(x=>alert(x.message));
$("nd").onclick=()=>api("dodaj",{email:$("ne").value}).then(()=>{$("ne").value="";return sve();}).catch(x=>alert(x.message));
$("tz").onclick=async ev=>{ const b=ev.target.closest("button[data-r]"); if(!b) return; const r=b.dataset.r, id=b.dataset.i;
  if(r==="dnevnik"){ const D=await api("dnevnik?z="+encodeURIComponent(id)); alert(D.dnevnik.map(x=>new Date(x.t).toLocaleString("hr-HR")+" · "+x.akter+" · "+x.radnja+(x.detalj?" ("+x.detalj+")":"")).join("\\n")||"Nema zapisa."); return; }
  if((r==="opozovi"||r==="obrisi"||r==="odbij")&&!confirm(r==="obrisi"?"Trajno obrisati podatke ovog korisnika? Radnja se ne može poništiti.":r==="opozovi"?"Odmah opozvati pristup?":"Odbiti zahtjev?")) return;
  let body={id,radnja:r}; if(r==="produzi") body.nacin=b.dataset.n; if(r==="odobri"){ const v=prompt("Trajanje u danima od aktivacije (0 = neograničeno):",$("tr").value); if(v===null) return; body.dana=+v; }
  try{ const j=await api("radnja",body); if(j.mail===false) alert("Radnja je spremljena, ali e-mail NIJE poslan. Provjeri postavke slanja i pokušaj »Ponovno pošalji kod«."); await sve(); }catch(x){ alert(x.message); } };
api("zahtjevi").then(()=>{$("log").hidden=true;$("app").hidden=false;return sve();}).catch(()=>{});
</script></body></html>`;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url), { h: H, dozvoljen } = cors(env, req);
    if (req.method === "OPTIONS") return new Response(null, { status: dozvoljen ? 204 : 403, headers: H });
    if (!env.TOKEN_SECRET || !env.CODE_PEPPER || !env.DB) return greska("NOT_CONFIGURED", "Worker nije postavljen.", 503, H);
    if (url.pathname === "/admin" && req.method === "GET") { const n = rnd(16); return new Response(adminHtml(n), { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": `default-src 'none'; connect-src 'self'; script-src 'nonce-${n}'; style-src 'nonce-${n}'; style-src-attr 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'`, "x-frame-options": "DENY", ...SIG } }); }
    if (url.pathname === "/admin/poveznica" && req.method === "POST") { const o = req.headers.get("origin"); if (req.headers.get("x-chr-admin") !== "1" || (o && o !== url.origin)) return greska("ADMIN", "Neovlašteno.", 403); return adminPoveznica(env, req, url); }
    if (url.pathname === "/admin/ulaz" && req.method === "GET") return adminUlaz(env, req, url);
    if (url.pathname === "/admin/prijava" && req.method === "POST") { const o = req.headers.get("origin"); if (req.headers.get("x-chr-admin") !== "1" || (o && o !== url.origin)) return greska("ADMIN", "Neovlašteno.", 403); return adminPrijava(env, req); }
    if (url.pathname.startsWith("/admin/api/")) return adminApi(env, req, url);
    if (url.pathname.startsWith("/admin")) return greska("NEMA", "Nepoznata adresa.", 404);
    if (url.pathname === "/potvrdi" && req.method === "GET") return potvrdi(env, req, url);
    if (!dozvoljen) return greska("ORIGIN", "Nedopušteno podrijetlo zahtjeva.", 403, H);
    if (url.pathname === "/zahtjev" && req.method === "POST") return zahtjev(env, req, H);
    if (url.pathname === "/dogadaj" && req.method === "POST") return dogadaj(env, req, H);
    if (url.pathname === "/prijava" && req.method === "POST") return prijava(env, req, H);
    if (url.pathname === "/provjera" && req.method === "GET") { const T = await provjeriToken(env, req); return T ? json({ ok: true, istice: T.z.istice || null, oznaka: null, produzenje: !!T.z.trazi_produzenje }, 200, H) : greska("TOKEN", "Prijava nije valjana.", 401, H); }
    if (url.pathname === "/produzenje" && req.method === "POST") { const T = await provjeriToken(env, req); if (!T) return greska("TOKEN", "Prijava nije valjana.", 401, H); return produzenje(env, req, H, T); }
    if (url.pathname === "/izvjestaj" && req.method === "POST") { const T = await provjeriToken(env, req); if (!T) return greska("TOKEN", "Prijava nije valjana.", 401, H); return izvjestaj(env, req, H, T); }
    return greska("NEMA", "Nepoznata adresa.", 404, H);
  },
  async scheduled(ev, env, ctx) { if (env.DB) ctx.waitUntil(dnevno(env)); },
};
export { dnevno, totpOk, noviKod, stanje };

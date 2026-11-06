// Čestica HR: pristupni kodovi za napredne funkcije i slanje dosjea na e-mail (Cloudflare Worker, besplatni plan).
// Tajne se NE upisuju ovdje ni u wrangler.toml, nego naredbom `npx wrangler secret put IME`:
//   TOKEN_SECRET  potpis tokena (dugi slučajni niz)
//   CODE_PEPPER   sol za sažetak kodova u KV-u (kod se ne sprema u čitljivom obliku)
//   ADMIN_SECRET  lozinka administratorske stranice (/admin)
//   BREVO_KEY     API ključ za slanje e-maila (Brevo, besplatna razina)
// KV: KODOVI (kodovi, ograničenja). Ništa od toga ne ide u aplikaciju.
const enc = new TextEncoder();
const MAX_PDF = 6 * 1024 * 1024; // najveći PDF (B) nakon dekodiranja
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const b64uStr = (s) => b64u(enc.encode(s));
const unb64u = (s) => { s = s.replace(/-/g, "+").replace(/_/g, "/"); while (s.length % 4) s += "="; return atob(s); };
async function hmac(secret, msg) { const k = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]); return b64u(await crypto.subtle.sign("HMAC", k, enc.encode(msg))); }
function eqConst(a, b) { if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false; let r = 0; for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i); return r === 0; }
const normKod = (k) => String(k || "").toUpperCase().replace(/[^A-Z0-9]/g, "");
async function kodKey(env, kod) { return "kod:" + (await hmac(env.CODE_PEPPER, normKod(kod))); }
// čitljiv kod bez dvosmislenih znakova (0/O, 1/I): XXXX-XXXX-XXXX
function noviKod() { const A = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789", r = crypto.getRandomValues(new Uint8Array(12)); let s = ""; for (let i = 0; i < 12; i++) { s += A[r[i] % A.length]; if (i === 3 || i === 7) s += "-"; } return s; }
const danas = () => new Date().toISOString().slice(0, 10);

function cors(env, req) {
  const o = req.headers.get("origin") || "", dozv = String(env.ALLOWED_ORIGINS || "").split(",").map((x) => x.trim()).filter(Boolean);
  const h = { "vary": "origin" };
  if (dozv.includes(o)) Object.assign(h, { "access-control-allow-origin": o, "access-control-allow-headers": "content-type, authorization", "access-control-allow-methods": "GET, POST, OPTIONS", "access-control-max-age": "600" });
  return { h, dozvoljen: !o || dozv.includes(o) };
}
const json = (obj, status, h) => new Response(JSON.stringify(obj), { status: status || 200, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...(h || {}) } });
const greska = (code, poruka, status, h) => json({ error: { code, poruka } }, status, h);

async function napraviToken(env, z) { const p = b64uStr(JSON.stringify({ id: z.id, exp: z.istice, v: String(env.TOKEN_EPOCH || "1") })); return p + "." + (await hmac(env.TOKEN_SECRET, p)); }
// token: potpis, rok, epoha i da kod nije opozvan (svaki put iz KV-a)
async function provjeriToken(env, req) {
  const a = req.headers.get("authorization") || "", t = a.startsWith("Bearer ") ? a.slice(7) : ""; const [p, s] = t.split(".");
  if (!p || !s || !eqConst(s, await hmac(env.TOKEN_SECRET, p))) return null;
  let P; try { P = JSON.parse(unb64u(p)); } catch (e) { return null; }
  if (!P || P.v !== String(env.TOKEN_EPOCH || "1") || !(P.exp > Date.now())) return null;
  const key = await env.KODOVI.get("id:" + P.id); if (!key) return null;
  const z = await env.KODOVI.get(key, "json"); if (!z || z.opozvan || !(z.istice > Date.now())) return null;
  return { z, key };
}
async function brojac(env, key, ttl) { const n = parseInt((await env.KODOVI.get(key)) || "0", 10) + 1; await env.KODOVI.put(key, String(n), { expirationTtl: ttl }); return n; }

async function prijava(env, req, H) {
  const ip = req.headers.get("cf-connecting-ip") || "nepoznato", sat = new Date().toISOString().slice(0, 13);
  const rl = "rl:" + ip + ":" + sat; if (parseInt((await env.KODOVI.get(rl)) || "0", 10) >= 10) return greska("PREVISE", "Previše neuspjelih pokušaja. Pokušaj za sat vremena.", 429, H);
  let b; try { b = await req.json(); } catch (e) { return greska("ZAHTJEV", "Neispravan zahtjev.", 400, H); }
  const kod = normKod(b && b.kod); if (kod.length !== 12) { await brojac(env, rl, 3600); return greska("KOD", "Kod nije ispravan.", 401, H); }
  const key = await kodKey(env, kod), z = await env.KODOVI.get(key, "json");
  if (!z || z.opozvan || !(z.istice > Date.now())) { await brojac(env, rl, 3600); return greska("KOD", z && z.opozvan ? "Kod je opozvan." : z ? "Kod je istekao." : "Kod nije ispravan.", 401, H); }
  return json({ token: await napraviToken(env, z), istice: z.istice, oznaka: z.oznaka || null }, 200, H);
}

async function izvjestaj(env, req, H, T) {
  if (!env.BREVO_KEY || !env.MAIL_FROM) return greska("NOT_CONFIGURED", "Slanje e-maila nije postavljeno.", 503, H);
  let b; try { b = await req.json(); } catch (e) { return greska("ZAHTJEV", "Neispravan zahtjev.", 400, H); }
  const email = String(b && b.email || "").trim(), naziv = String(b && b.naziv || "dosje-cestice.pdf").replace(/[^\w.-]/g, "_").slice(0, 80), naslov = String(b && b.naslov || "Dosje čestice").slice(0, 120);
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 200) return greska("EMAIL", "E-mail adresa nije ispravna.", 400, H);
  const pdf = String(b && b.pdf || ""); if (!/^[A-Za-z0-9+/=]+$/.test(pdf) || pdf.length < 100) return greska("PDF", "Dosje nije priložen.", 400, H);
  if (pdf.length * 0.75 > MAX_PDF) return greska("PDF", "Dosje je prevelik za slanje.", 413, H);
  if (!/^JVBER/.test(pdf)) return greska("PDF", "Privitak nije PDF.", 400, H);
  const lim = parseInt(env.IZVJESTAJA_DNEVNO || "10", 10), dk = "sl:" + T.z.id + ":" + danas();
  if (parseInt((await env.KODOVI.get(dk)) || "0", 10) >= lim) return greska("LIMIT", `Danas je poslano najviše ${lim} dosjea s ovim kodom. Pokušaj sutra.`, 429, H);
  const r = await fetch(env.MAIL_API || "https://api.brevo.com/v3/smtp/email", { method: "POST", headers: { "api-key": env.BREVO_KEY, "content-type": "application/json", accept: "application/json" },
    body: JSON.stringify({ sender: { email: env.MAIL_FROM, name: "Čestica HR" }, to: [{ email }], replyTo: env.MAIL_REPLY ? { email: env.MAIL_REPLY } : undefined, subject: naslov,
      htmlContent: `<p>U privitku je dosje čestice iz aplikacije Čestica HR.</p><p>Dosje je sastavljen iz javnih podataka i izračuna aplikacije. Nije lokacijska informacija, izvadak iz zemljišne knjige ni projekt.</p><p>Čestica HR</p>`,
      attachment: [{ name: naziv.endsWith(".pdf") ? naziv : naziv + ".pdf", content: pdf }] }) }).catch(() => null);
  if (!r || !r.ok) return greska("SLANJE", "Slanje nije uspjelo. Pokušaj ponovno kasnije.", 502, H);
  await brojac(env, dk, 2 * 86400);
  return json({ ok: true, poslano: email }, 200, H);
}

// --- administracija (lozinka ADMIN_SECRET u zaglavlju Authorization: Bearer …)
async function admin(env, req, url, H) {
  const a = req.headers.get("authorization") || "";
  if (!env.ADMIN_SECRET || !eqConst(a, "Bearer " + env.ADMIN_SECRET)) return greska("ADMIN", "Neovlašteno.", 401, H);
  if (url.pathname === "/admin/kod" && req.method === "POST") {
    let b = {}; try { b = await req.json(); } catch (e) {}
    const dana = Math.max(1, Math.min(3650, parseInt(b.dana || "365", 10) || 365)), oznaka = String(b.oznaka || "").slice(0, 120);
    const kod = noviKod(), key = await kodKey(env, kod), id = b64u(crypto.getRandomValues(new Uint8Array(9)));
    const z = { id, oznaka, stvoren: Date.now(), istice: Date.now() + dana * 86400000, opozvan: false };
    await env.KODOVI.put(key, JSON.stringify(z)); await env.KODOVI.put("id:" + id, key);
    return json({ kod, id, oznaka, istice: z.istice }, 200, H);
  }
  if (url.pathname === "/admin/kodovi" && req.method === "GET") {
    const out = []; let cursor;
    do { const L = await env.KODOVI.list({ prefix: "kod:", cursor }); for (const k of L.keys) { const z = await env.KODOVI.get(k.name, "json"); if (z) out.push({ id: z.id, oznaka: z.oznaka, stvoren: z.stvoren, istice: z.istice, opozvan: !!z.opozvan }); } cursor = L.list_complete ? null : L.cursor; } while (cursor);
    out.sort((x, y) => y.stvoren - x.stvoren); return json({ kodovi: out }, 200, H);
  }
  if (url.pathname === "/admin/opozovi" && req.method === "POST") {
    let b = {}; try { b = await req.json(); } catch (e) {}
    const key = await env.KODOVI.get("id:" + String(b.id || "")); if (!key) return greska("NEMA", "Kod ne postoji.", 404, H);
    const z = await env.KODOVI.get(key, "json"); z.opozvan = true; z.opozvanU = Date.now(); await env.KODOVI.put(key, JSON.stringify(z)); return json({ ok: true }, 200, H);
  }
  return greska("NEMA", "Nepoznata radnja.", 404, H);
}

const ADMIN_HTML = `<!doctype html><html lang="hr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Čestica HR – kodovi</title>
<style>body{font:16px system-ui,sans-serif;max-width:760px;margin:0 auto;padding:16px;color:#0b1210}input,button{font:inherit;padding:10px 12px;border-radius:8px;border:1px solid #b9c2be}button{background:#0b1210;color:#fff;border:0;cursor:pointer}table{width:100%;border-collapse:collapse;margin-top:12px}td,th{border-bottom:1px solid #e3e8e5;padding:8px 4px;text-align:left;font-size:14px}.kod{font:700 22px ui-monospace,monospace;background:#d6f7e7;padding:12px;border-radius:8px;display:inline-block}label{display:block;margin:12px 0 4px}</style></head><body>
<h1>Pristupni kodovi</h1>
<label for="lz">Administratorska lozinka</label><input id="lz" type="password" autocomplete="current-password" style="width:100%;box-sizing:border-box">
<h2>Novi kod</h2><label for="oz">Oznaka (ime ili e-mail korisnika)</label><input id="oz" style="width:100%;box-sizing:border-box"><label for="dn">Vrijedi dana</label><input id="dn" type="number" value="365" min="1" max="3650">
<p><button id="nov">Stvori kod</button></p><p id="iz" aria-live="polite"></p>
<h2>Popis</h2><p><button id="pop">Osvježi popis</button></p><div id="tb"></div>
<script>
const $=id=>document.getElementById(id), H=()=>({"content-type":"application/json",authorization:"Bearer "+$("lz").value});
const d=t=>new Date(t).toLocaleDateString("hr-HR"), esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"})[c]);
$("nov").onclick=async()=>{const r=await fetch("/admin/kod",{method:"POST",headers:H(),body:JSON.stringify({oznaka:$("oz").value,dana:+$("dn").value})}),j=await r.json();
  $("iz").innerHTML=r.ok?'Kod (prikazuje se samo sada, pošalji ga korisniku): <br><span class="kod">'+esc(j.kod)+'</span><br>vrijedi do '+d(j.istice):esc(j.error&&j.error.poruka);};
$("pop").onclick=async()=>{const r=await fetch("/admin/kodovi",{headers:H()}),j=await r.json(); if(!r.ok){$("tb").textContent=j.error&&j.error.poruka;return}
  $("tb").innerHTML='<table><tr><th>Oznaka</th><th>Stvoren</th><th>Ističe</th><th>Stanje</th><th></th></tr>'+j.kodovi.map(k=>'<tr><td>'+esc(k.oznaka)+'</td><td>'+d(k.stvoren)+'</td><td>'+d(k.istice)+'</td><td>'+(k.opozvan?"opozvan":k.istice<Date.now()?"istekao":"aktivan")+'</td><td>'+(k.opozvan?"":'<button data-id="'+esc(k.id)+'">Opozovi</button>')+'</td></tr>').join("")+'</table>';
  $("tb").querySelectorAll("button[data-id]").forEach(b=>b.onclick=async()=>{if(!confirm("Opozvati kod "+b.closest("tr").cells[0].textContent+"?"))return; await fetch("/admin/opozovi",{method:"POST",headers:H(),body:JSON.stringify({id:b.dataset.id})}); $("pop").click();});};
</script></body></html>`;

export default {
  async fetch(req, env) {
    const url = new URL(req.url), { h: H, dozvoljen } = cors(env, req);
    if (req.method === "OPTIONS") return new Response(null, { status: dozvoljen ? 204 : 403, headers: H });
    if (!env.TOKEN_SECRET || !env.CODE_PEPPER || !env.KODOVI) return greska("NOT_CONFIGURED", "Worker nije postavljen.", 503, H);
    if (url.pathname === "/admin" && req.method === "GET") return new Response(ADMIN_HTML, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'", "x-frame-options": "DENY" } });
    if (url.pathname.startsWith("/admin/")) return admin(env, req, url, {});
    if (!dozvoljen) return greska("ORIGIN", "Nedopušteno podrijetlo zahtjeva.", 403, H);
    if (url.pathname === "/prijava" && req.method === "POST") return prijava(env, req, H);
    if (url.pathname === "/provjera" && req.method === "GET") { const T = await provjeriToken(env, req); return T ? json({ ok: true, istice: T.z.istice, oznaka: T.z.oznaka || null }, 200, H) : greska("TOKEN", "Prijava nije valjana.", 401, H); }
    if (url.pathname === "/izvjestaj" && req.method === "POST") { const T = await provjeriToken(env, req); if (!T) return greska("TOKEN", "Prijava nije valjana.", 401, H); return izvjestaj(env, req, H, T); }
    return greska("NEMA", "Nepoznata adresa.", 404, H);
  },
};

// Čestica HR – posrednik prema javnom OSS-u (oss.uredjenazemlja.hr) za upisanu površinu čestice.
// Cloudflare Worker. Poziv: GET https://<worker>/?id=<CESTICA_ID>
// Vraća SAMO površine, dijelove čestice i oznake ZK uloška. Imena, adrese i udjeli posjednika/vlasnika se NE prosljeđuju.
// OSS-ova adresa /oss/public/cad/parcel-info nije službeno dokumentirano sučelje i može se promijeniti bez najave.

const OSS = "https://oss.uredjenazemlja.hr/oss/public/cad/parcel-info?parcelId=";
const ALLOWED = ["https://ozrenpancic-maker.github.io"]; // stranice koje smiju čitati odgovor (produkcija i proba su na istom originu)
const CACHE_S = 6 * 3600; // odgovor OSS-a pamti se 6 sati

const arr = x => (x == null ? [] : Array.isArray(x) ? x : [x]);
// OSS u XML-u omata liste u istoimeni element: <parcelParts><parcelParts>…</parcelParts></parcelParts>
const list = x => {
  if (x == null || x === "") return [];
  if (Array.isArray(x)) return x;
  if (typeof x === "object") { const k = Object.keys(x); if (k.length === 1 && typeof x[k[0]] === "object") return arr(x[k[0]]); }
  return [x];
};
const num = v => { const n = parseFloat(String(v ?? "").replace(",", ".")); return Number.isFinite(n) ? n : null; };

// Mali XML parser (OSS ponekad vraća XML umjesto JSON-a): elementi i tekst, bez atributa.
function xmlToObj(s) {
  s = s.replace(/<\?[\s\S]*?\?>/g, "").replace(/<!--[\s\S]*?-->/g, "");
  const ent = t => t.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&#(\d+);/g, (_, d) => String.fromCharCode(+d)).replace(/&amp;/g, "&");
  const re = /<(\/?)([A-Za-z_][\w.-]*)[^>]*?(\/?)>|([^<]+)/g;
  const root = { kids: {} }, stack = [root]; let m;
  while ((m = re.exec(s))) {
    const top = stack[stack.length - 1];
    if (m[4] != null) { if (m[4].trim()) top.text = (top.text || "") + ent(m[4].trim()); continue; }
    const [, close, name, self] = m;
    if (close) { const n = stack.pop(); const val = Object.keys(n.kids).length ? n.kids : (n.text ?? ""); const p = stack[stack.length - 1]; add(p.kids, name, val); continue; }
    if (self) { add(top.kids, name, ""); continue; }
    stack.push({ kids: {} });
  }
  function add(o, k, v) { if (k in o) { if (!Array.isArray(o[k]) || !o[k].__multi) { o[k] = [o[k]]; o[k].__multi = true; } o[k].push(v); } else o[k] = v; }
  const k = Object.keys(root.kids); return k.length === 1 ? root.kids[k[0]] : root.kids;
}

export function sazmi(d) {
  const odjeli = {};
  for (const u of list(d.lrUnitsFromParcelLinks)) odjeli[String(u.lrUnitId)] = { odjel: u.institutionName || null, vrsta: u.lrUnitTypeName || null, status: u.statusName || null };
  const zk = list(d.parcelLinks).map(l => {
    const u = l.lrUnit || {}; const o = odjeli[String(u.lrUnitId)] || {};
    return { broj: l.parcelNumber != null ? String(l.parcelNumber) : null, povrsina: num(l.area), opis: l.address || null,
      ulozak: u.lrUnitNumber != null ? String(u.lrUnitNumber) : null, glavnaKnjiga: u.mainBookName || null, odjel: o.odjel || null, vrstaUloska: o.vrsta || null, statusUloska: o.status || null };
  });
  const dijelovi = list(d.parcelParts).map(p => ({ naziv: p.name || null, povrsina: num(p.area), zgrada: String(p.building) === "true" }));
  return { ok: true, id: d.parcelId != null ? String(d.parcelId) : null, broj: d.parcelNumber != null ? String(d.parcelNumber) : null,
    koMb: d.cadMunicipalityRegNum != null ? String(d.cadMunicipalityRegNum) : null, ko: d.cadMunicipalityName || null,
    katastar: num(d.area), zk, dijelovi, izvor: "OSS (oss.uredjenazemlja.hr), neslužbeni javni podaci", dohvaceno: new Date().toISOString() };
}

function cors(origin) {
  const h = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "public, max-age=3600", "Vary": "Origin" };
  if (ALLOWED.includes(origin)) h["Access-Control-Allow-Origin"] = origin;
  return h;
}
const out = (o, status, origin) => new Response(JSON.stringify(o), { status, headers: cors(origin) });

export default {
  async fetch(req, env, ctx) {
    const origin = req.headers.get("Origin") || "";
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...cors(origin), "Access-Control-Allow-Methods": "GET", "Access-Control-Max-Age": "86400" } });
    if (req.method !== "GET") return out({ ok: false, greska: "samo GET" }, 405, origin);
    const id = new URL(req.url).searchParams.get("id") || "";
    if (!/^\d{1,12}$/.test(id)) return out({ ok: false, greska: "neispravan id" }, 400, origin);

    const cache = caches.default, ck = new Request("https://cache.local/oss/" + id);
    const hit = await cache.match(ck);
    if (hit) { const o = await hit.json(); o.izCachea = true; return out(o, 200, origin); }

    let r;
    try { r = await fetch(OSS + id, { headers: { "Accept": "application/json, text/xml;q=0.5", "User-Agent": "CesticaHR/1.0 (+https://ozrenpancic-maker.github.io/cestica-zg/)" }, signal: AbortSignal.timeout(12000) }); }
    catch (e) { return out({ ok: false, greska: "OSS ne odgovara (" + (e.name || "greška") + ")" }, 502, origin); }
    if (r.status === 404 || r.status === 204) return out({ ok: false, greska: "OSS nema česticu s tim ID-om" }, 404, origin);
    if (!r.ok) return out({ ok: false, greska: "OSS HTTP " + r.status }, 502, origin);
    const txt = await r.text(); let d;
    try { d = txt.trim().startsWith("<") ? xmlToObj(txt) : JSON.parse(txt); } catch (e) { return out({ ok: false, greska: "OSS je vratio nečitljiv odgovor" }, 502, origin); }
    if (!d || (d.parcelId == null && d.area == null)) return out({ ok: false, greska: "OSS nema česticu s tim ID-om" }, 404, origin);
    const o = sazmi(d);
    ctx.waitUntil(cache.put(ck, new Response(JSON.stringify(o), { headers: { "Content-Type": "application/json", "Cache-Control": "max-age=" + CACHE_S } })));
    return out(o, 200, origin);
  }
};

export { xmlToObj };

// Čestica HR – posrednik prema javnom OSS-u (oss.uredjenazemlja.hr) za upisanu površinu čestice.
// PRIJEDLOG (worker.next.js): nije objavljen. Dodaje sažetak ZK uloška (?id=…&ulozak=1), vidi PRIJEDLOG-tereti.md.
// Cloudflare Worker. Poziv: GET https://<worker>/?id=<CESTICA_ID>[&ulozak=1]
// Vraća SAMO površine, dijelove čestice i oznake ZK uloška. Imena, adrese i udjeli posjednika/vlasnika se NE prosljeđuju.
// OSS-ova adresa /oss/public/cad/parcel-info nije službeno dokumentirano sučelje i može se promijeniti bez najave.

const OSS = "https://oss.uredjenazemlja.hr/oss/public/cad/parcel-info?parcelId=";
const OSS_LR = "https://oss.uredjenazemlja.hr/oss/public/lr/lr-unit";
const ALLOWED = ["https://ozrenpancic-maker.github.io"]; // stranice koje smiju čitati odgovor (produkcija i proba su na istom originu)
const CACHE_S = 3 * 24 * 3600; // odgovor OSS-a pamti se 3 dana (manje upita prema OSS-u; aplikacija prikazuje datum dohvata)
const BLOK_S = 90; // kad OSS odbije (403/429), posrednik ga 90 s ne pita ništa, da se odbijanje ne produžuje novim upitima

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

function sazmi(d) {
  const odjeli = {};
  for (const u of list(d.lrUnitsFromParcelLinks)) odjeli[String(u.lrUnitId)] = { odjel: u.institutionName || null, vrsta: u.lrUnitTypeName || null, status: u.statusName || null };
  const zk = list(d.parcelLinks).map(l => {
    const u = l.lrUnit || {}; const o = odjeli[String(u.lrUnitId)] || {};
    return { broj: l.parcelNumber != null ? String(l.parcelNumber) : null, povrsina: num(l.area), opis: l.address || null,
      ulozak: u.lrUnitNumber != null ? String(u.lrUnitNumber) : null, glavnaKnjiga: u.mainBookName || null, odjel: o.odjel || null, vrstaUloska: o.vrsta || null, statusUloska: o.status || null,
      _mb: u.mainBookId != null ? String(u.mainBookId) : null };
  });
  const dijelovi = list(d.parcelParts).map(p => ({ naziv: p.name || null, povrsina: num(p.area), zgrada: String(p.building) === "true" }));
  return { ok: true, id: d.parcelId != null ? String(d.parcelId) : null, broj: d.parcelNumber != null ? String(d.parcelNumber) : null,
    koMb: d.cadMunicipalityRegNum != null ? String(d.cadMunicipalityRegNum) : null, ko: d.cadMunicipalityName || null,
    katastar: num(d.area), zk, dijelovi, izvor: "OSS (oss.uredjenazemlja.hr), neslužbeni javni podaci", dohvaceno: new Date().toISOString() };
}

function cors(origin, pamti = false) {
  const h = { "Content-Type": "application/json; charset=utf-8", "Cache-Control": pamti ? "public, max-age=3600" : "no-store", "Vary": "Origin" };
  if (ALLOWED.includes(origin)) h["Access-Control-Allow-Origin"] = origin;
  return h;
}
let COLO = null; // Cloudflareov podatkovni centar koji je obradio upit (za dijagnostiku odbijanja s OSS-a)
// preglednik smije zapamtiti samo potpun, uspješan odgovor; greške i odgovor bez uloška (ulosciGreska) ne pamti, da ponovni pokušaj stvarno ide na OSS
const out = (o, status, origin) => new Response(JSON.stringify(COLO ? { ...o, cf: COLO } : o), { status, headers: cors(origin, status === 200 && !o.ulosciGreska) });

// WGS84 -> HTRS96/TM (EPSG:3765), Snyder (USGS 1395); ista formula kao u aplikaciji (greška ispod 2 cm)
function tmFwd(lon, lat) {
  const a = 6378137, f = 1 / 298.257222101, k0 = 0.9999, lon0 = 16.5, E0 = 500000, e2 = f * (2 - f), ep2 = e2 / (1 - e2), r = Math.PI / 180;
  const M = p => { const e4 = e2 * e2, e6 = e4 * e2; return a * ((1 - e2 / 4 - 3 * e4 / 64 - 5 * e6 / 256) * p - (3 * e2 / 8 + 3 * e4 / 32 + 45 * e6 / 1024) * Math.sin(2 * p) + (15 * e4 / 256 + 45 * e6 / 1024) * Math.sin(4 * p) - (35 * e6 / 3072) * Math.sin(6 * p)); };
  const phi = lat * r, s = Math.sin(phi), c = Math.cos(phi), t = Math.tan(phi);
  const N = a / Math.sqrt(1 - e2 * s * s), T = t * t, C = ep2 * c * c, A = (lon - lon0) * r * c;
  const E = E0 + k0 * N * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T * T + 72 * C - 58 * ep2) * A ** 5 / 120);
  const Nn = k0 * (M(phi) + N * t * (A * A / 2 + (5 - T + 9 * C + 4 * C * C) * A ** 4 / 24 + (61 - 58 * T + T * T + 600 * C - 330 * ep2) * A ** 6 / 720));
  return [E, Nn];
}
const WMS = "https://wms1-gs-oss.uredjenazemlja.hr/ows2-m/wms";
// OSS povremeno odbija upite koji ne izgledaju kao upiti njegove stranice (HTTP 403). Zaglavlja su ona koja šalje i OSS-ova
// stranica (jezik, izvor, vrsta upita); posrednik se i dalje predstavlja svojim imenom u User-Agentu.
const UA = { "User-Agent": "Mozilla/5.0 (compatible; CesticaHR/1.0; +https://ozrenpancic-maker.github.io/cestica-zg/)",
  "Accept-Language": "hr-HR,hr;q=0.9,en;q=0.5", "Referer": "https://oss.uredjenazemlja.hr/", "Origin": "https://oss.uredjenazemlja.hr" };
// jedan ponovni pokušaj u posredniku nakon kratke stanke kad OSS odbije (403, 429) ili ne odgovori (5xx); ukupno najviše dva upita
const spavaj = ms => new Promise(r => setTimeout(r, ms));
const BLOK = new Request("https://cache.local/oss-blok");
class OssBlok extends Error { constructor(m) { super(m); this.blok = true; } }
async function ossFetch(u, h) {
  const b = await caches.default.match(BLOK);
  if (b) throw new OssBlok("OSS trenutno odbija upite posrednika; pokušaj ponovno za minutu-dvije (" + (await b.text()) + ")");
  let r = await fetch(u, { headers: { ...h, ...UA }, signal: AbortSignal.timeout(12000) });
  if (r.status >= 500) { await spavaj(700 + Math.floor(Math.random() * 700)); r = await fetch(u, { headers: { ...h, ...UA }, signal: AbortSignal.timeout(12000) }); }
  if (r.status === 403 || r.status === 429) {
    // bez ponavljanja: odbijanje je obično ograničenje broja upita, a svaki novi upit ga produžuje. Za dijagnostiku samo poslužitelj i vrsta odgovora.
    const opis = "HTTP " + r.status + ", " + (r.headers.get("server") || "poslužitelj ?") + ", " + ((r.headers.get("content-type") || "?").split(";")[0]);
    try { await caches.default.put(BLOK, new Response(opis, { headers: { "Cache-Control": "max-age=" + BLOK_S } })); } catch (e) {}
    throw new OssBlok("OSS je odbio upit (" + opis + ")");
  }
  return r;
}
// katastarska čestica na točki: isti sloj koji OSS koristi kad se klikne na kartu (WMS GetFeatureInfo)
async function cesticaNaTocki(lat, lon) {
  const [E, N] = tmFwd(lon, lat), d = 1;
  const q = new URLSearchParams({ SERVICE: "WMS", VERSION: "1.3.0", REQUEST: "GetFeatureInfo", FORMAT: "image/png", TRANSPARENT: "true", QUERY_LAYERS: "oss:BZP_CESTICE", LAYERS: "oss:BZP_CESTICE", STYLES: "", INFO_FORMAT: "application/json", I: "50", J: "50", CRS: "EPSG:3765", WIDTH: "101", HEIGHT: "101", BBOX: [E - d, N - d, E + d, N + d].map(x => x.toFixed(2)).join(","), FEATURE_COUNT: "1" });
  const r = await fetch(WMS + "?" + q, { headers: { Accept: "application/json", ...UA }, signal: AbortSignal.timeout(12000) });
  if (!r.ok) throw new Error("OSS karta HTTP " + r.status);
  const j = await r.json(), f = j && j.features && j.features[0];
  if (!f) return null;
  const p = f.properties || {};
  return { id: p.CESTICA_ID, broj: p.BROJ_CESTICE || null, koMb: p.MATICNI_BROJ_KO != null ? String(p.MATICNI_BROJ_KO) : null, graficka: num(p.POVRSINA_GRAFICKA), atributna: num(p.POVRSINA_ATRIBUTNA), datum: p.DATUM || null };
}
async function parcelInfo(id) {
  // bez ponavljanja ovdje: ponovni pokušaj radi aplikacija, da OSS ne dobiva niz upita
  let r; try { r = await ossFetch(OSS + id, { "Accept": "application/json, text/plain, */*" }); } catch (e) { if (e.blok) return { status: 503, greska: e.message, blok: true }; throw e; } const last = null;
  if (r.status === 404 || r.status === 204) return { status: 404 };
  if (!r.ok) return { status: 502, greska: "OSS HTTP " + (last || r.status) };
  const txt = await r.text(); let d;
  try { d = txt.trim().startsWith("<") ? xmlToObj(txt) : JSON.parse(txt); } catch (e) { return { status: 502, greska: "OSS je vratio nečitljiv odgovor" }; }
  if (!d || (d.parcelId == null && d.area == null)) return { status: 404 };
  return { status: 200, o: sazmi(d) };
}

// ---- sažetak ZK uloška (lr-unit): samo dopušteni dijelovi; imena, adrese i OIB vlasnika, posjednika i ovlaštenika iz C lista
// nikad ne izlaze kao zasebna polja. Struktura provjerena na dva uzorka od 20. 10. 2026.: upis je {description, lrEntryId, orderNumber};
// A I je u „cadParcels” ili „lrParcels”; C upisi su u grupama (lrEntryGroups[].lrEntries[]) i mogu imati lrOwners (ovlaštenike).
// Tekst upisa u A II i C prenosi se u cijelosti (odluka korisnika), uz zamjenu OIB-a (11 znamenki) s „[OIB]”.
// Tekst upisa u B (stjecanje vlasništva) se ne prenosi jer redovito sadrži imena vlasnika; vraća se samo broj upisa.
const OIB = /\b\d{11}\b/g;
// OSS u tekst upisa umeće HTML (<span>, <br>): pretvara se u običan tekst s novim redovima
const ENT = { "&nbsp;": " ", "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&apos;": "'" };
const cist = v => String(v).replace(/<br\s*\/?>/gi, "\n").replace(/<[^>]*>/g, "").replace(/&(nbsp|amp|lt|gt|quot|apos|#39);/g, m => ENT[m]).replace(/&#(\d+);/g, (_, d) => String.fromCharCode(+d))
  .split("\n").map(l => l.replace(/[ \t]+/g, " ").trim()).join("\n").replace(/\n{3,}/g, "\n\n").trim();
const tekst = v => (v == null ? null : cist(v).replace(OIB, "[OIB]"));
const rbr = v => (v == null ? null : String(v));
const upis = e => ({ rb: rbr(e.orderNumber), tekst: tekst(e.description) });
function sazmiUlozak(u) {
  if (Array.isArray(u)) u = u[0];
  if (!u || typeof u !== "object") return null;
  const B = u.ownershipSheetB || {}, A1 = u.possessionSheetA1 || {}, A2 = u.possessionSheetA2 || {}, C = u.encumbranceSheetC || {};
  const udjeli = list(B.lrUnitShares).map(sh => ({ rb: rbr(sh.orderNumber), opis: tekst(sh.description), vlasnika: list(sh.lrOwners).length, podudjela: list(sh.subSharesAndEntries).length }));
  const cest = list(A1.cadParcels).concat(list(A1.lrParcels));
  const grupe = list(C.lrEntryGroups).map(g => ({ oznaka: tekst(g.description), upisi: list(g.lrEntries).map(e => ({ ...upis(e), ovlastenika: list(e.lrOwners).length })) }));
  return {
    ulozak: u.lrUnitNumber != null ? String(u.lrUnitNumber) : null, glavnaKnjiga: u.mainBookName || null, odjel: u.institutionName || null,
    status: u.statusName || null, vrsta: u.lrUnitTypeName || null, provjeren: u.verificated === true || String(u.verificated) === "true", etaze: u.condominiums === true || String(u.condominiums) === "true",
    zadnjiDnevnik: u.lastDiaryNumber != null ? String(u.lastDiaryNumber) : null,
    plomba: list(u.activePlumbs).length > 0, plombi: list(u.activePlumbs).length,
    A1: cest.map(p => ({ broj: p.parcelNumber != null ? String(p.parcelNumber) : null, ko: p.cadMunicipalityName || null, koMb: p.cadMunicipalityRegNum != null ? String(p.cadMunicipalityRegNum) : null,
      opis: p.address || null, povrsina: num(p.area), pravoGradjenja: p.hasBuildingRight === true || String(p.hasBuildingRight) === "true",
      dijelovi: list(p.parcelParts).map(q => ({ naziv: q.name || null, povrsina: num(q.area), zgrada: q.building === true || String(q.building) === "true" })),
      posjedovniListovi: list(p.possessionSheets).map(q => q.possessionSheetNumber != null ? String(q.possessionSheetNumber) : null).filter(Boolean) })),
    A2: { upisa: list(A2.lrEntries).length, upisi: list(A2.lrEntries).map(upis) },
    B: { udjela: udjeli.length, vlasnika: udjeli.reduce((a, x) => a + x.vlasnika, 0), udjeli, upisa: list(B.lrEntries).length },
    C: { upisa: grupe.reduce((a, g) => a + g.upisi.length, 0), grupe },
    napomena: "Javni uvid OSS-a; nije službeni izvadak i ne potvrđuje pravno stanje. Mjerodavan je ZK izvadak."
  };
}
async function ulozak(broj, mb) {
  if (!/^\d{1,12}$/.test(String(broj)) || !/^\d{1,12}$/.test(String(mb))) return null;
  const q = new URLSearchParams({ lrUnitNumber: String(broj), mainBookId: String(mb), historicalOverview: "false" });
  // isti uložak dijeli više čestica: sažetak se pamti po broju uloška i glavnoj knjizi (manje upita prema OSS-u)
  const cache = caches.default, ck = new Request("https://cache.local/oss-ul/" + mb + "/" + broj), hit = await cache.match(ck);
  if (hit) return await hit.json();
  const r = await ossFetch(OSS_LR + "?" + q, { Accept: "application/json, text/plain, */*" });
  if (!r.ok) throw new Error("OSS uložak HTTP " + r.status);
  const o = sazmiUlozak(await r.json());
  if (o) await cache.put(ck, new Response(JSON.stringify(o), { headers: { "Content-Type": "application/json", "Cache-Control": "max-age=" + CACHE_S } }));
  return o;
}

export default {
  async fetch(req, env, ctx) {
    const origin = req.headers.get("Origin") || "";
    COLO = req.cf && req.cf.colo ? String(req.cf.colo) : null;
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: { ...cors(origin), "Access-Control-Allow-Methods": "GET", "Access-Control-Max-Age": "86400" } });
    if (req.method !== "GET") return out({ ok: false, greska: "samo GET" }, 405, origin);
    const sp = new URL(req.url).searchParams;
    let id = sp.get("id") || "", tocka = null;
    const lat = parseFloat(sp.get("lat")), lon = parseFloat(sp.get("lon"));
    if (!id && Number.isFinite(lat) && Number.isFinite(lon)) {
      if (lat < 42 || lat > 46.6 || lon < 13 || lon > 19.5) return out({ ok: false, greska: "točka je izvan Hrvatske" }, 400, origin);
      try { tocka = await cesticaNaTocki(lat, lon); } catch (e) { return out({ ok: false, greska: e.message || "OSS karta ne odgovara" }, 502, origin); }
      if (!tocka || tocka.id == null) return out({ ok: false, greska: "na toj točki OSS nema katastarsku česticu" }, 404, origin);
      id = String(tocka.id);
    }
    if (!/^\d{1,12}$/.test(id)) return out({ ok: false, greska: "neispravan id" }, 400, origin);

    const cache = caches.default, ck = new Request("https://cache.local/oss/" + id);
    const hit = await cache.match(ck);
    let o;
    if (hit) { o = await hit.json(); o.izCachea = true; }
    else {
      let res;
      try { res = await parcelInfo(id); } catch (e) { return out({ ok: false, greska: "OSS ne odgovara (" + (e.name || "greška") + ")" }, 502, origin); }
      if (res.status === 404) return out({ ok: false, greska: "OSS nema česticu s tim ID-om" }, 404, origin);
      if (res.status !== 200) return out({ ok: false, greska: res.greska, ...(res.blok ? { blok: true } : {}) }, res.blok ? 503 : 502, origin);
      o = res.o;
      ctx.waitUntil(cache.put(ck, new Response(JSON.stringify(o), { headers: { "Content-Type": "application/json", "Cache-Control": "max-age=" + CACHE_S } })));
    }
    if (tocka) { o.graficka = tocka.graficka; o.stanjeKarte = tocka.datum; if (!o.koMb) o.koMb = tocka.koMb; }
    // uložak samo kad ga aplikacija izričito traži; broj i glavna knjiga uzimaju se iz parcel-info iste čestice, ne iz upita
    // uložak koji je već u predmemoriji šalje se i bez „ulozak=1” (bez upita prema OSS-u)
    if (sp.get("ulozak") !== "1") { try { const h2 = await cache.match(new Request("https://cache.local/oss-lr/" + id)); if (h2) o.ulosci = await h2.json(); } catch (e) {} }
    if (sp.get("ulozak") === "1") {
      const ck2 = new Request("https://cache.local/oss-lr/" + id), hit2 = await cache.match(ck2);
      if (hit2) o.ulosci = await hit2.json();
      else {
        // čestica iz predmemorije stare verzije posrednika nema glavnu knjigu (_mb): tada se parcel-info dohvati ponovno
        if ((o.zk || []).some(z => z.ulozak && !z._mb)) { try { const fr = await parcelInfo(id); if (fr.status === 200) { o = { ...fr.o, ...(tocka ? { graficka: o.graficka, stanjeKarte: o.stanjeKarte } : {}) }; ctx.waitUntil(cache.put(ck, new Response(JSON.stringify(fr.o), { headers: { "Content-Type": "application/json", "Cache-Control": "max-age=" + CACHE_S } }))); } } catch (e) {} }
        const zk = (o.zk || []).filter(z => z.ulozak && z._mb).slice(0, 3);
        // prazan rezultat (čestica bez povezanog uloška ili nepotpun odgovor OSS-a) se ne pamti, da se sljedeći put pokuša ponovno
        // ulošci jedan po jedan (ne istodobno), da OSS ne dobije nalet upita
        try { o.ulosci = []; for (const z of zk) { const u = await ulozak(z.ulozak, z._mb); if (u) o.ulosci.push(u); } if (o.ulosci.length) ctx.waitUntil(cache.put(ck2, new Response(JSON.stringify(o.ulosci), { headers: { "Content-Type": "application/json", "Cache-Control": "max-age=" + CACHE_S } }))); }
        catch (e) { o.ulosciGreska = e.message || "OSS uložak ne odgovara"; if (e.blok) o.blok = true; }
      }
    }
    o = { ...o, zk: (o.zk || []).map(({ _mb, ...z }) => z) };
    return out(o, 200, origin);
  }
};

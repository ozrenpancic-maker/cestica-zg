// Test prijedloga posrednika (worker.next.js) bez mreže: node tools/oss-posrednik/test.next.mjs
// Uzorak lr-unit ima strukturu stvarnog odgovora (20. 10. 2026.), s izmišljenim imenima, adresom i OIB-om.
import fs from "node:fs"; import assert from "node:assert/strict";
import W from "./worker.next.js";
const xml = fs.readFileSync(new URL("./primjer.xml", import.meta.url), "utf8");
const lr = [{ lrUnitId: 8739768, lrUnitNumber: "5126", mainBookId: 31117, mainBookName: "KORNIĆ", cadastreMunicipalityId: 205010, institutionId: 285,
  institutionName: "Zemljišnoknjižni odjel Krk", status: "0", statusName: "Aktivan", verificated: true, condominiums: false, lrUnitTypeId: 1, lrUnitTypeName: "VLASNIČKI",
  activePlumbs: [],
  ownershipSheetB: { lrUnitShares: [
    { description: "Suvlasnički dio: 1/2", lrOwners: [{ lrOwnerId: 1, name: "IVAN TESTNI", address: "TESTNA 1, ZAGREB", taxNumber: "12345678901" }], lrUnitShareId: 1, subSharesAndEntries: [], status: 0, orderNumber: "1" },
    { description: "Suvlasnički dio: 1/2 (OIB 98765432109)", lrOwners: [{ lrOwnerId: 2, name: "ANA TESTNA", address: "TESTNA 2, KRK", taxNumber: "98765432109" }], lrUnitShareId: 2, subSharesAndEntries: [], status: 0, orderNumber: "2" }], lrEntries: [] },
  possessionSheetA1: { cadParcels: [{ parcelId: 19311109, parcelNumber: "735/58", cadMunicipalityId: 205010, cadMunicipalityRegNum: "315907", cadMunicipalityName: "KORNIĆ", institutionId: 700,
    address: "KUĆA, TERASA I DVORIŠTE", area: "642", buildingRemark: 0, detailSheetNumber: "1", hasBuildingRight: false,
    parcelParts: [{ parcelPartId: 1, name: "KUĆA", area: "85", possessionSheetId: 2, possessionSheetNumber: "2159", building: true }],
    possessionSheets: [{ possessionSheetId: 2, possessionSheetNumber: "2159", cadMunicipalityName: "KORNIĆ", possessors: [{ name: "IVAN TESTNI", address: "TESTNA 1" }] }] }] },
  possessionSheetA2: { lrEntries: [] }, encumbranceSheetC: { lrEntryGroups: [] } }];
let store = new Map();
globalThis.caches = { default: { match: async k => store.has(k.url) ? new Response(store.get(k.url)) : null, put: async (k, r) => { store.set(k.url, await r.text()); } } };
const ctx = { waitUntil(p) { return p; } };
const calls = [];
globalThis.fetch = async u => { u = String(u); calls.push(u); return /lr-unit/.test(u) ? new Response(JSON.stringify(lr), { status: 200, headers: { "Content-Type": "application/json" } }) : new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
// bez ulozak=1: isto kao danas, bez upita za uložak i bez internog polja _mb
let r = await W.fetch(new Request("https://w.dev/?id=19311109"), {}, ctx), s = await r.text(), o = JSON.parse(s);
assert.equal(o.ulosci, undefined); assert.ok(!calls.some(u => /lr-unit/.test(u))); assert.ok(!/_mb/.test(s));
// s ulozak=1: uložak iz parcel-info iste čestice (5126, glavna knjiga 31117)
r = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1&lrUnitNumber=999"), {}, ctx); s = await r.text(); o = JSON.parse(s);
const lrCall = calls.find(u => /lr-unit/.test(u)); assert.ok(/lrUnitNumber=5126&mainBookId=31117&historicalOverview=false/.test(lrCall), lrCall);
const U = o.ulosci[0];
assert.equal(U.ulozak, "5126"); assert.equal(U.plomba, false); assert.equal(U.B.vlasnika, 2); assert.equal(U.B.udjela, 2);
assert.deepEqual(U.B.udjeli.map(x => x.opis), ["Suvlasnički dio: 1/2", "Suvlasnički dio: 1/2 (OIB [OIB])"]);
assert.equal(U.A1[0].broj, "735/58"); assert.equal(U.A1[0].povrsina, 642); assert.deepEqual(U.A1[0].posjedovniListovi, ["2159"]); assert.equal(U.A1[0].dijelovi[0].zgrada, true);
assert.ok(/ZK izvadak/.test(U.napomena));
assert.ok(!/TESTN|12345678901|98765432109|taxNumber|lrOwners|possessors/i.test(s), "imena, adrese i OIB ne smiju izaći: " + s);
// predmemorija: drugi upit ne ide na OSS za uložak
const n = calls.filter(u => /lr-unit/.test(u)).length;
await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx);
assert.equal(calls.filter(u => /lr-unit/.test(u)).length, n);
const cached = [...store.entries()].find(([k]) => /oss-lr/.test(k))[1]; assert.ok(!/TESTN|12345678901/.test(cached), "u predmemoriji nema osobnih podataka");
console.log("worker.next: uložak OK");
// drugi oblik (uzorak 2): A I u „lrParcels”, upisi u A II, B i C; C upis s ovlaštenikom (izmišljeni podaci)
{
  const S = W.__test || null;
  const lr2 = [{ lrUnitNumber: "100200", mainBookName: "CEROVAC", institutionName: "Zemljišnoknjižni odjel Karlovac", statusName: "Aktivan", lrUnitTypeName: "VLASNIČKI", lastDiaryNumber: "Z-7530/2022", verificated: true, condominiums: false, activePlumbs: [{ x: 1 }],
    ownershipSheetB: { lrUnitShares: [{ description: "Vlasnički dio: 1/1", lrOwners: [{ lrOwnerId: 9, name: "PERO TESTNI, OIB 11111111111", taxNumber: "11111111111", lrEntry: { description: "Na temelju ugovora uknjižuje se pravo vlasništva za PERO TESTNI", orderNumber: "1.1" } }], subSharesAndEntries: [], orderNumber: "1" }],
      lrEntries: [{ description: "Zabilježba za PERO TESTNI", lrEntryId: 5, orderNumber: "1.2" }] },
    possessionSheetA1: { lrParcels: [{ parcelId: 21504489, parcelNumber: "1161", address: "KUĆA I DVORIŠTE, ŠĆULAC 11A", area: "1234", areaInAcres: "0", areaInHvat: "343", statusInLrUnit: 0, parcelParts: [] }] },
    possessionSheetA2: { lrEntries: [{ description: "<span class='lr-entry-black' >Zaprimljeno 21.03.2016.<br><br>ZABILJEŽBA,  rješenje o izvedenom stanju za kuću Šćulac 11A sa 79 m2 &amp; garažu</span>", lrEntryId: 6, orderNumber: "3.1" }] },
    encumbranceSheetC: { lrEntryGroups: [
      { description: "1.", lrEntries: [{ description: "Uknjižuje se založno pravo radi osiguranja tražbine od 50.000,00 EUR u korist BANKA TEST d.d., OIB 22222222222", lrOwners: [{ lrOwnerId: 7, name: "BANKA TEST d.d.", address: "TESTNA 3", taxNumber: "22222222222" }], lrEntryId: 7, orderNumber: "1.1" }] },
      { description: "2.", lrEntries: [{ description: "Zabilježba ovrhe", lrEntryId: 8, orderNumber: "2.1" }] }] } }];
  store = new Map(); calls.length = 0;
  globalThis.fetch = async u => { u = String(u); calls.push(u); return /lr-unit/.test(u) ? new Response(JSON.stringify(lr2), { status: 200, headers: { "Content-Type": "application/json" } }) : new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
  const r2 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), s2 = await r2.text(), U2 = JSON.parse(s2).ulosci[0];
  assert.equal(U2.A1[0].broj, "1161"); assert.equal(U2.A1[0].povrsina, 1234); assert.equal(U2.zadnjiDnevnik, "Z-7530/2022"); assert.equal(U2.plomba, true);
  assert.deepEqual(U2.A2.upisi, [{ rb: "3.1", tekst: "Zaprimljeno 21.03.2016.\n\nZABILJEŽBA, rješenje o izvedenom stanju za kuću Šćulac 11A sa 79 m2 & garažu" }]);
  assert.equal(U2.C.upisa, 2); assert.equal(U2.C.grupe[0].upisi[0].ovlastenika, 1); assert.ok(/50\.000,00 EUR u korist BANKA TEST d\.d\., OIB \[OIB\]/.test(U2.C.grupe[0].upisi[0].tekst));
  assert.equal(U2.B.upisa, 1); assert.equal(U2.B.vlasnika, 1);
  assert.ok(!/PERO|11111111111|22222222222|TESTNA 3|taxNumber|lrOwners|lrEntry"/.test(s2), "B imena, OIB-i i adrese ne izlaze: " + s2);
  console.log("worker.next: upisi A II i C OK");
  // predmemorija stare verzije (bez _mb): parcel-info se dohvati ponovno, pa uložak radi
  store = new Map(); store.set("https://cache.local/oss/19311109", JSON.stringify({ ok: true, id: "19311109", broj: "735/58", zk: [{ broj: "735/58", povrsina: 642, ulozak: "5126" }], dijelovi: [] })); calls.length = 0;
  const r3 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o3 = await r3.json();
  assert.equal(o3.ulosci.length, 1); assert.ok(calls.some(u => /parcel-info/.test(u)) && calls.some(u => /lr-unit/.test(u) && /mainBookId=31117/.test(u)));
  console.log("worker.next: stara predmemorija OK");
}

// predmemorija preglednika: uspješan odgovor smije se pamtiti, greška i odgovor bez uloška ne smiju; prazan uložak se ne pamti u Workeru
{
  store = new Map(); calls.length = 0;
  globalThis.fetch = async u => { u = String(u); calls.push(u); return /lr-unit/.test(u) ? new Response("odbijeno", { status: 403 }) : new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
  const r1 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o1 = await r1.json();
  assert.ok(o1.ulosciGreska && r1.headers.get("Cache-Control") === "no-store", "odgovor s greškom uloška: no-store");
  assert.ok(![...store.keys()].some(k => /oss-lr/.test(k)), "neuspjeli uložak se ne pamti");
  const r2 = await W.fetch(new Request("https://w.dev/?id=abc"), {}, ctx); assert.equal(r2.status, 400); assert.equal(r2.headers.get("Cache-Control"), "no-store");
  store.delete("https://cache.local/oss-blok"); // pauza nakon odbijanja (vidi test ispod)
  globalThis.fetch = async u => { u = String(u); calls.push(u); return /lr-unit/.test(u) ? new Response("[]", { status: 200, headers: { "Content-Type": "application/json" } }) : new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
  const r3 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o3b = await r3.json();
  assert.deepEqual(o3b.ulosci, []); assert.ok(![...store.keys()].some(k => /oss-lr/.test(k)), "prazan uložak se ne pamti 24 sata");
  globalThis.fetch = async u => { u = String(u); calls.push(u); return /lr-unit/.test(u) ? new Response(JSON.stringify(lr), { status: 200, headers: { "Content-Type": "application/json" } }) : new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
  const r4 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o4 = await r4.json();
  assert.equal(o4.ulosci.length, 1); assert.equal(r4.headers.get("Cache-Control"), "public, max-age=3600"); assert.ok([...store.keys()].some(k => /oss-lr/.test(k)));
  console.log("worker.next: predmemorija grešaka i praznog uloška OK");
}
// OSS odbije upit (403): posrednik ne ponavlja, 90 s ne pita OSS (pauza), zaglavlja kao OSS-ova stranica; uložak se pamti po broju uloška
{
  store = new Map(); calls.length = 0; let n = 0; const hdr = [];
  globalThis.fetch = async (u, o) => { u = String(u); calls.push(u); hdr.push(o && o.headers || {}); if (/lr-unit/.test(u)) { n++; return n === 1 ? new Response("x", { status: 403, headers: { server: "BigIP", "content-type": "text/html" } }) : new Response(JSON.stringify(lr), { status: 200, headers: { "Content-Type": "application/json" } }); } return new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } }); };
  const r1 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o1 = await r1.json();
  assert.equal(n, 1, "bez ponavljanja nakon 403"); assert.ok(o1.ulosciGreska && /HTTP 403, BigIP, text\/html/.test(o1.ulosciGreska) && o1.blok, o1.ulosciGreska);
  assert.ok(hdr.every(h => h.Referer === "https://oss.uredjenazemlja.hr/" && /CesticaHR/.test(h["User-Agent"]) && /hr-HR/.test(h["Accept-Language"])));
  const before = calls.length, r2 = await W.fetch(new Request("https://w.dev/?id=19311110"), {}, ctx), o2 = await r2.json();
  assert.equal(calls.length, before, "za vrijeme pauze nema upita prema OSS-u"); assert.equal(r2.status, 503); assert.ok(o2.blok && /odbija upite posrednika/.test(o2.greska));
  // nakon pauze: uložak stiže i pamti se po broju uloška (druga čestica u istom ulošku bez novog upita)
  store.delete("https://cache.local/oss-blok");
  const r3 = await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx), o3 = await r3.json(); assert.equal(o3.ulosci.length, 1); assert.equal(n, 2);
  store.delete([...store.keys()].find(k => /oss-lr\//.test(k)));
  await W.fetch(new Request("https://w.dev/?id=19311109&ulozak=1"), {}, ctx); assert.equal(n, 2, "uložak iz predmemorije po broju");
  console.log("worker.next: odbijanje (403) → pauza bez ponavljanja, predmemorija uloška OK");
}
// OSS vrati HTML stranicu (200, text/html) umjesto podataka: to je odbijanje (503, blok, pauza), a ne „nema čestice”
{
  store = new Map(); calls.length = 0;
  globalThis.fetch = async u => { u = String(u); calls.push(u); return new Response("<html><head><title>Zabranjeno</title></head><body><h1>Pristup odbijen</h1></body></html>", { status: 200, headers: { server: "nginx", "content-type": "text/html" } }); };
  const r = await W.fetch(new Request("https://w.dev/?id=19311109"), {}, ctx), o = await r.json();
  assert.equal(r.status, 503); assert.equal(o.ok, false); assert.ok(o.blok, JSON.stringify(o)); assert.ok(/HTML stranicu \(HTTP 200, nginx, text\/html, \d+ B, „Zabranjeno Pristup odbijen”\)/.test(o.greska), o.greska); assert.ok(!/nema česticu/.test(o.greska));
  const n = calls.length; await W.fetch(new Request("https://w.dev/?id=19311110"), {}, ctx); assert.equal(calls.length, n, "nakon HTML odbijanja pauza bez upita prema OSS-u");
  console.log("worker.next: HTML stranica umjesto podataka → odbijanje (503, blok, pauza) OK");
}
// stranica OSS-a o održavanju (24. 10. 2026.): poruka „OSS je u održavanju”
{
  store = new Map();
  globalThis.fetch = async u => new Response("<html><body><p>Poštovani, u tijeku je održavanje sustava.</p></body></html>", { status: 200, headers: { server: "nginx", "content-type": "text/html" } });
  const r = await W.fetch(new Request("https://w.dev/?id=19311109"), {}, ctx), o = await r.json();
  assert.equal(r.status, 503); assert.ok(o.blok && /^OSS je u održavanju \(HTTP 200, nginx, text\/html, \d+ B, „Poštovani, u tijeku je održavanje sustava\.”\)$/.test(o.greska), o.greska);
  console.log("worker.next: OSS u održavanju OK");
}
// poplave: slojevi iz popisa servisa (GetCapabilities), upit po točki, prepoznavanje pogotka; bez imena slojeva upisanih u kod
{
  store = new Map(); const pitano = [];
  const cap = `<?xml version="1.0"?><WMS_Capabilities version="1.3.0"><Capability><Request><GetFeatureInfo><Format>text/html</Format><Format>application/json</Format></GetFeatureInfo></Request><Layer><Title>Opasnosti</Title>
    <Layer queryable="1"><Name>hv:opasnost_velika_2019</Name><Title>Opasnost od poplava – velika vjerojatnost</Title></Layer>
    <Layer queryable="1"><Name>hv:opasnost_srednja_2019</Name><Title>Opasnost od poplava – srednja vjerojatnost</Title></Layer>
    <Layer queryable="1"><Name>hv:opasnost_mala_2019</Name><Title>Opasnost od poplava – mala vjerojatnost</Title></Layer>
    <Layer queryable="0"><Name>hv:podloga</Name><Title>Podloga</Title></Layer></Layer></Capability></WMS_Capabilities>`;
  globalThis.fetch = async u => { u = String(u); pitano.push(u);
    if (/GetCapabilities/.test(u)) return new Response(cap, { status: 200, headers: { "content-type": "text/xml" } });
    const L = new URL(u).searchParams.get("QUERY_LAYERS"), ima = /mala/.test(L);
    return new Response(JSON.stringify({ type: "FeatureCollection", features: ima ? [{ properties: { dubina: "0,5–1,5 m", scenarij: "mala" } }] : [] }), { status: 200, headers: { "content-type": "application/json" } }); };
  const r = await W.fetch(new Request("https://w.dev/?poplave=45.8,15.97", { headers: { Origin: "https://ozrenpancic-maker.github.io" } }), {}, ctx), o = await r.json();
  assert.equal(r.status, 200, JSON.stringify(o)); assert.equal(r.headers.get("Access-Control-Allow-Origin"), "https://ozrenpancic-maker.github.io");
  assert.deepEqual(o.slojevi.map(s => [s.title.split("– ")[1], s.pogodak]), [["velika vjerojatnost", false], ["srednja vjerojatnost", false], ["mala vjerojatnost", true]]);
  assert.equal(o.format, "application/json"); assert.equal(o.slojevi[2].svojstva.dubina, "0,5–1,5 m"); assert.ok(!pitano.some(u => /podloga/.test(u)), "sloj koji se ne smije upitati se ne pita");
  const n = pitano.length; const o2 = await (await W.fetch(new Request("https://w.dev/?poplave=45.8,15.97"), {}, ctx)).json(); assert.ok(o2.izCachea && pitano.length === n, "rezultat se pamti");
  const d = await (await W.fetch(new Request("https://w.dev/?poplave=45.8,15.97&dijag=1"), {}, ctx)).json(); assert.ok(d.sviSlojevi.length === 4 && /ne upituje se/.test(d.sviSlojevi[3]));
  const x = await W.fetch(new Request("https://w.dev/?poplave=48.1,11.5"), {}, ctx); assert.equal(x.status, 400);
  // servis vrati stranicu umjesto popisa slojeva: jasna greška, ništa izmišljeno
  store = new Map(); globalThis.fetch = async () => new Response("<html>Poštovani, u tijeku je održavanje sustava.</html>", { status: 200, headers: { "content-type": "text/html" } });
  const e = await (await W.fetch(new Request("https://w.dev/?poplave=45.8,15.97"), {}, ctx)).json(); assert.ok(!e.ok && /popis slojeva nije dostupan \(HTTP 200, text\/html/.test(e.greska), e.greska);
  console.log("worker.next: poplave (slojevi iz popisa servisa, pogodak, predmemorija, greške) OK");
}
// poplave, stvarni servis (24. 10. 2026.): slojevi nisu „queryable” → čita se prozirnost slike svakog scenarija
{
  const zlib = await import("node:zlib");
  const crcT = Array.from({ length: 256 }, (_, n) => { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; return c >>> 0; });
  const crc = b => { let c = 0xffffffff; for (const x of b) c = crcT[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]), c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
  // png(n, boja(x,y) → [r,g,b,a]); paleta=true → tip 3 s tRNS; filtri se izmjenjuju (0–4) da se provjeri dekodiranje
  const png = (n, boja, paleta) => {
    const ih = Buffer.alloc(13); ih.writeUInt32BE(n, 0); ih.writeUInt32BE(n, 4); ih[8] = 8; ih[9] = paleta ? 3 : 6;
    const kan = paleta ? 1 : 4, red = n * kan, rows = [], pal = [[0, 0, 0, 0], [40, 90, 200, 180]];
    let prev = Buffer.alloc(red);
    for (let y = 0; y < n; y++) {
      const cur = Buffer.alloc(red); for (let x = 0; x < n; x++) { const c = boja(x, y); if (paleta) cur[x] = c[3] ? 1 : 0; else cur.set(c, x * 4); }
      const f = y % 5, out = Buffer.alloc(red);
      for (let i = 0; i < red; i++) { const a = i >= kan ? cur[i - kan] : 0, up = prev[i], c = i >= kan ? prev[i - kan] : 0;
        const pr = f === 0 ? 0 : f === 1 ? a : f === 2 ? up : f === 3 ? (a + up) >> 1 : (() => { const p = a + up - c, pa = Math.abs(p - a), pb = Math.abs(p - up), pc = Math.abs(p - c); return pa <= pb && pa <= pc ? a : pb <= pc ? up : c; })();
        out[i] = (cur[i] - pr) & 255; }
      rows.push(Buffer.from([f]), out); prev = cur;
    }
    const dij = [Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]), chunk("IHDR", ih)];
    if (paleta) dij.push(chunk("PLTE", Buffer.from(pal.flatMap(p => p.slice(0, 3)))), chunk("tRNS", Buffer.from(pal.map(p => p[3]))));
    dij.push(chunk("IDAT", zlib.deflateSync(Buffer.concat(rows))), chunk("IEND", Buffer.alloc(0)));
    return Buffer.concat(dij);
  };
  const cap = `<WMS_Capabilities version="1.3.0"><Capability><Request><GetFeatureInfo><Format>application/json</Format></GetFeatureInfo></Request>
    <Layer><Name>hr.fd.opasnost-od-poplave-mala-vjerojatnost</Name><Title>Opasnosti od poplava, mala vjerojatnost pojavljivanja</Title></Layer>
    <Layer><Name>hr.fd.opasnost-od-poplave-srednja-vjerojatnost</Name><Title>Opasnosti od poplava, srednja vjerojatnost pojavljivanja</Title></Layer>
    <Layer><Name>hr.fd.opasnost-od-poplave-velika-vjerojatnost</Name><Title>Opasnosti od poplava, velika vjerojatnost pojavljivanja</Title></Layer>
    <Layer><Name>hr.fd.vjerojatnost-pojavljivanja</Name><Title>Opasnost od poplava, tri scenarija plavljenja</Title></Layer></Capability></WMS_Capabilities>`;
  const prazno = () => [0, 0, 0, 0], puno = () => [30, 80, 200, 200], rub = (x, y) => x < 3 ? [30, 80, 200, 200] : [0, 0, 0, 0];
  const odg = { mala: [puno, true], srednja: [puno, false], velika: [rub, false] }, pitano = [];
  store = new Map();
  globalThis.fetch = async u => { u = String(u); pitano.push(u);
    if (/GetCapabilities/.test(u)) return new Response(cap, { status: 200, headers: { "content-type": "text/xml" } });
    assert.ok(/REQUEST=GetMap/.test(u) && /TRANSPARENT=TRUE/.test(u) && !/vjerojatnost-pojavljivanja/.test(u), u);
    const k = u.match(/poplave-(mala|srednja|velika)/)[1], [f, pal] = odg[k];
    return new Response(png(11, f, pal), { status: 200, headers: { "content-type": "image/png" } }); };
  const o = await (await W.fetch(new Request("https://w.dev/?poplave=45.04,14.61&dijag=1"), {}, ctx)).json();
  assert.ok(o.ok && o.metoda === "slika", JSON.stringify(o));
  const po = Object.fromEntries(o.slojevi.map(s => [s.name.match(/(mala|srednja|velika)/)[1], s.pogodak]));
  assert.deepEqual(po, { mala: true, srednja: true, velika: false });
  assert.ok(o.slojevi.every(s => /vjerojatnost pojavljivanja/.test(s.title)));
  // sve prozirno → izvan; slika bez prozirnosti → ne može se odrediti
  odg.mala = [prazno, true]; odg.srednja = [prazno, false]; odg.velika = [prazno, false]; store = new Map();
  const o2 = await (await W.fetch(new Request("https://w.dev/?poplave=45.04,14.62"), {}, ctx)).json(); assert.ok(o2.ok && o2.slojevi.every(s => s.pogodak === false));
  globalThis.fetch = async u => /GetCapabilities/.test(String(u)) ? new Response(cap, { status: 200, headers: { "content-type": "text/xml" } }) : new Response("<ServiceExceptionReport>x</ServiceExceptionReport>", { status: 200, headers: { "content-type": "text/xml" } });
  store = new Map(); const e = await (await W.fetch(new Request("https://w.dev/?poplave=45.04,14.63"), {}, ctx)).json(); assert.ok(!e.ok && /slike servisa/.test(e.greska) && /ServiceException/.test(e.slojevi[0].greska), JSON.stringify(e));
  console.log("worker.next: poplave preko slike (slojevi bez upita po točki, PNG RGBA i paleta) OK");
}
// HAKOM: razredi brzine na točki (nepokretna i pokretna mreža)
{
  store = new Map(); const pitano = [];
  globalThis.fetch = async u => { u = String(u); pitano.push(u); const id = +u.match(/\/(\d+)\/query/)[1], ima = id === 92 || id === 94 || id === 99;
    return new Response(JSON.stringify({ features: ima ? [{ attributes: { BrojOperatora: id === 92 ? "jedan" : "više" } }] : [] }), { status: 200, headers: { "content-type": "application/json" } }); };
  const o = await (await W.fetch(new Request("https://w.dev/?internet=45.04,14.61"), {}, ctx)).json();
  assert.ok(o.ok); assert.deepEqual(o.nepokretna, [{ sloj: 92, operatora: "jedan" }, { sloj: 94, operatora: "više" }]); assert.deepEqual(o.pokretna, [{ sloj: 99, operatora: "više" }]); assert.equal(pitano.length, 9);
  globalThis.fetch = async () => new Response(JSON.stringify({ error: { code: 500, message: "json" } }), { status: 200 });
  store = new Map(); const e = await (await W.fetch(new Request("https://w.dev/?internet=45.04,14.61"), {}, ctx)).json(); assert.ok(!e.ok && /HAKOM: json/.test(e.greska));
  console.log("worker.next: HAKOM internet (razredi, greška) OK");
}
// Registar kulturnih dobara: prsten čestice → WKT u HTRS96/TM, sažetak bez geometrije, predmemorija, greške
{
  store = new Map(); const pitano = [];
  const odg = { KulturnaDobra: [{ Naziv: "Kulturno-povijesna urbanistička cjelina grada Krka", Vrsta: "Kulturnopovijesne cjeline", Klasifikacija: "urbana cjelina", RegistarskiBroj: "Z-2684", StatusZastite: "Zaštićeno kulturno dobro", Geometrija: "MULTIPOLYGON (((1 1,2 2,3 3,1 1)))", Opis: "Opis  cjeline", Datacija: "antika", Naselje: "KRK" },
      { Naziv: "Kulturno-povijesna urbanistička cjelina grada Krka", RegistarskiBroj: "Z-2684" }],
    Obrasci: { Kpc: [{ Id: 528, Naziv: "Kulturno-povijesna urbanistička cjelina grada Krka", RegistraskiBroj: "Z-2684" }], Pzo: [], Gops: [] }, Unesco: [],
    KonzervatorskiOdjeli: [{ NazivKonzervatorskogUreda: "Područni konzervatorski ured Rijeka\r\n", UlicaNaziv: "Užarska", KucniBroj: 26, NaseljeNaziv: "Rijeka", Email: "pou@min-kulture.hr", Telefon: "051 311 300", Procelnik: "ime" }] };
  globalThis.fetch = async u => { u = String(u); pitano.push(u); return new Response(JSON.stringify(odg), { status: 200, headers: { "content-type": "application/json" } }); };
  const r = await W.fetch(new Request("https://w.dev/?kultura=45.027,14.5735;45.0271,14.5736;45.0272,14.5734", { headers: { Origin: "https://ozrenpancic-maker.github.io" } }), {}, ctx), o = await r.json();
  assert.equal(r.status, 200, JSON.stringify(o)); const w = decodeURIComponent(new URL(pitano[0]).searchParams.get("wktGeom"));
  assert.ok(/^POLYGON\(\(348\d{3}\.\d\d 4989\d{3}\.\d\d,/.test(w) && w.split(",").length === 4 && /elKatIds=15,16,41,42,43,47,48/.test(pitano[0]), w);
  assert.equal(o.dobra.length, 1); assert.equal(o.dobra[0].reg, "Z-2684"); assert.equal(o.dobra[0].opis, "Opis cjeline"); assert.ok(!JSON.stringify(o).includes("MULTIPOLYGON") && !JSON.stringify(o).includes("Procelnik") && !JSON.stringify(o).includes("ime\""));
  assert.deepEqual(o.podloge, [{ vrsta: "KPC", naziv: "Kulturno-povijesna urbanistička cjelina grada Krka", reg: "Z-2684" }]);
  assert.deepEqual(o.konzervator, { naziv: "Područni konzervatorski ured Rijeka", adresa: "Užarska 26, Rijeka", email: "pou@min-kulture.hr", tel: "051 311 300" });
  const n = pitano.length; const o2 = await (await W.fetch(new Request("https://w.dev/?kultura=45.027,14.5735;45.0271,14.5736;45.0272,14.5734"), {}, ctx)).json(); assert.ok(o2.izCachea && pitano.length === n);
  const t = await (await W.fetch(new Request("https://w.dev/?kultura=45.8,15.97"), {}, ctx)).json(); assert.ok(t.ok && /^POINT\(/.test(decodeURIComponent(new URL(pitano.at(-1)).searchParams.get("wktGeom"))));
  assert.equal((await W.fetch(new Request("https://w.dev/?kultura=48.1,11.5"), {}, ctx)).status, 400);
  assert.equal((await W.fetch(new Request("https://w.dev/?kultura=" + Array(61).fill("45.1,15.1").join(";")), {}, ctx)).status, 400);
  store = new Map(); globalThis.fetch = async () => new Response('{"Message":"An error has occurred."}', { status: 500, headers: { "content-type": "application/json" } });
  const e = await W.fetch(new Request("https://w.dev/?kultura=45.8,15.97"), {}, ctx), eo = await e.json(); assert.ok(e.status === 502 && !eo.ok && /HTTP 500/.test(eo.greska), eo.greska);
  console.log("worker.next: kulturna dobra (WKT HTRS96/TM, sažetak, predmemorija, greške) OK");
}

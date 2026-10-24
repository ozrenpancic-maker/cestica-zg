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

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

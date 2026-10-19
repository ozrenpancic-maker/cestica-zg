// Test posrednika bez mreže: node tools/oss-posrednik/test.mjs
import fs from "node:fs"; import assert from "node:assert/strict";
import W from "./worker.js";
const xml = fs.readFileSync(new URL("./primjer.xml", import.meta.url), "utf8");
// isti podaci u JSON obliku (kako ih OSS-ova web aplikacija dobiva)
const j = { parcelId: 19311109, parcelNumber: "735/58", cadMunicipalityRegNum: 315907, cadMunicipalityName: "KORNIĆ", area: 642,
  parcelParts: [{ name: "KUĆA, LEDINE", area: 85, building: true }, { name: "TERASA", area: 35, building: false }, { name: "DVORIŠTE", area: 522, building: false }],
  possessionSheets: [{ possessors: [{ name: "IVAN TESTNI", address: "TESTNA 1" }] }],
  parcelLinks: [{ parcelNumber: "735/58", area: 642, address: "KUĆA, TERASA I DVORIŠTE", lrUnit: { lrUnitId: 7269240, lrUnitNumber: 5126, mainBookName: "KORNIĆ" }, parcelParts: [] }],
  lrUnitsFromParcelLinks: [{ lrUnitId: 7269240, institutionName: "Zemljišnoknjižni odjel Krk", statusName: "Aktivan", lrUnitTypeName: "VLASNIČKI" }] };
globalThis.caches = { default: { match: async () => null, put: async () => {} } };
const ctx = { waitUntil() {} };
for (const [ime, body, ct] of [["xml", xml, "application/xml"], ["json", JSON.stringify(j), "application/json"]]) {
  globalThis.fetch = async () => new Response(body, { status: 200, headers: { "Content-Type": ct } });
  const r0 = await W.fetch(new Request("https://w.dev/?id=19311109"), {}, ctx), s = await r0.text(), o = JSON.parse(s);
  assert.equal(o.broj, "735/58"); assert.equal(o.katastar, 642); assert.equal(o.koMb, "315907");
  assert.equal(o.zk.length, 1); assert.equal(o.zk[0].povrsina, 642); assert.equal(o.zk[0].ulozak, "5126"); assert.equal(o.zk[0].odjel, "Zemljišnoknjižni odjel Krk");
  assert.deepEqual(o.dijelovi.map(x => x.povrsina), [85, 35, 522]); assert.equal(o.dijelovi[0].zgrada, true);
  assert.ok(!/TESTN|ownership|possess/i.test(s), ime + ": osobni podaci ne smiju proći");
  console.log(ime, "OK");
}
// handler: mock fetch i cache
const realFetch = globalThis.fetch;
globalThis.fetch = async u => new Response(xml, { status: 200, headers: { "Content-Type": "application/xml" } });
let r = await W.fetch(new Request("https://w.dev/?id=19311109", { headers: { Origin: "https://ozrenpancic-maker.github.io" } }), {}, ctx);
assert.equal(r.status, 200); assert.equal(r.headers.get("Access-Control-Allow-Origin"), "https://ozrenpancic-maker.github.io");
const o = await r.json(); assert.equal(o.zk[0].povrsina, 642);
r = await W.fetch(new Request("https://w.dev/?id=19311109", { headers: { Origin: "https://evil.example" } }), {}, ctx);
assert.equal(r.headers.get("Access-Control-Allow-Origin"), null);
r = await W.fetch(new Request("https://w.dev/?id=abc"), {}, ctx); assert.equal(r.status, 400);
globalThis.fetch = async () => new Response("", { status: 500 });
r = await W.fetch(new Request("https://w.dev/?id=1"), {}, ctx); assert.equal(r.status, 502);
globalThis.fetch = realFetch;
console.log("handler OK");

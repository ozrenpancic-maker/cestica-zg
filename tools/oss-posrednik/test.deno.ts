// Test rezervnog posrednika (deno.ts) bez mreže: deno run -A --unstable-kv tools/oss-posrednik/test.deno.ts
const xml = await Deno.readTextFile(new URL("./primjer.xml", import.meta.url));
const lr = [{ lrUnitNumber: "5126", mainBookId: 31117, mainBookName: "KORNIĆ", institutionName: "Zemljišnoknjižni odjel Krk", statusName: "Aktivan", lrUnitTypeName: "VLASNIČKI", activePlumbs: [],
  ownershipSheetB: { lrUnitShares: [{ description: "Vlasnički dio: 1/1", lrOwners: [{ name: "IVAN TESTNI", taxNumber: "12345678901" }], orderNumber: "1" }], lrEntries: [] },
  possessionSheetA1: { cadParcels: [{ parcelNumber: "735/58", area: "642" }] }, possessionSheetA2: { lrEntries: [] }, encumbranceSheetC: { lrEntryGroups: [] } }];
const real = globalThis.fetch; let oss = 0, odbij = false;
globalThis.fetch = (async (u: any, o?: any) => { const s = String(u instanceof Request ? u.url : u);
  if (s.startsWith("https://oss.uredjenazemlja.hr")) { oss++; if (odbij) return new Response("x", { status: 403, headers: { server: "BigIP" } });
    return /lr-unit/.test(s) ? new Response(JSON.stringify(lr), { headers: { "Content-Type": "application/json" } }) : new Response(xml, { headers: { "Content-Type": "application/xml" } }); }
  return real(u, o); }) as typeof fetch;
await import("./deno.ts");
const H = { headers: { Origin: "https://ozrenpancic-maker.github.io" } }, get = async (q: string) => { const r = await real("http://localhost:8000/" + q, H); return { r, j: await r.json() }; };
const ok = (c: boolean, m: string) => { if (!c) { console.error("PALO: " + m); Deno.exit(1); } console.log("✓ " + m); };
let { r, j } = await get("?id=19311109&ulozak=1");
ok(r.status === 200 && j.ok && j.posrednik === "deno" && j.ulosci[0].ulozak === "5126" && !/TESTNI|12345678901/.test(JSON.stringify(j)) && r.headers.get("Access-Control-Allow-Origin") === "https://ozrenpancic-maker.github.io", "uložak preko Denoa, bez imena i OIB-a, CORS za aplikaciju");
const n = oss; ({ j } = await get("?id=19311109&ulozak=1")); ok(oss === n && j.ulosci.length === 1, "drugi upit iz Deno KV predmemorije (bez upita OSS-u)");
odbij = true; ({ r, j } = await get("?id=99999")); const n2 = oss; ({ r, j } = await get("?id=99998"));
ok(r.status === 503 && j.blok && oss === n2, "nakon odbijanja (403) pauza bez upita OSS-u");
console.log("deno: sve u redu"); Deno.exit(0);

// Čestica HR – rezervni posrednik prema OSS-u na Deno Deployu (drugi IP-jevi od Cloudflarea).
// Isti kod kao Cloudflare Worker (worker.next.js): sažetak ZK uloška bez imena, adresa i OIB-a, iste dopuštene stranice (CORS),
// pauza 90 s nakon odbijanja OSS-a. Umjesto Cloudflareove predmemorije koristi se Deno KV (isti ključevi i trajanje).
// Ništa se ne zapisuje u logove (nema ispisa u konzolu).
// Postavljanje: Deno Deploy → nova aplikacija iz GitHub repozitorija, ulazna datoteka tools/oss-posrednik/deno.ts.

const kv = await Deno.openKv();
const ttl = (res: Response) => { const m = (res.headers.get("Cache-Control") || "").match(/max-age=(\d+)/); return (m ? +m[1] : 3600) * 1000; };
// isto sučelje kao caches.default u Workeru: match(Request) i put(Request, Response)
const shim = { default: {
  async match(req: Request) {
    try { const r = await kv.get<{ b: string; t: string; do: number }>(["c", req.url]); const v = r.value;
      if (!v || v.do < Date.now()) return undefined; return new Response(v.b, { headers: { "Content-Type": v.t } }); } catch { return undefined; }
  },
  async put(req: Request, res: Response) {
    try { const b = await res.text(), ms = ttl(res); if (b.length > 60000) return; // ograničenje veličine zapisa u Deno KV
      await kv.set(["c", req.url], { b, t: res.headers.get("Content-Type") || "application/json", do: Date.now() + ms }, { expireIn: ms }); } catch { /* bez pamćenja */ }
  } } };
// Deno ima vlastiti globalThis.caches (samo za čitanje), pa se zamjenjuje svojstvom
Object.defineProperty(globalThis, "caches", { value: shim, configurable: true, writable: true });

const W = (await import("./worker.next.js")).default;
const ctx = { waitUntil(p: Promise<unknown>) { if (p && (p as any).catch) (p as any).catch(() => {}); } };

Deno.serve({ onListen() {} }, async (req: Request) => { // bez ispisa pri pokretanju
  const r: Response = await W.fetch(req, {}, ctx);
  // u odgovoru piše koji je posrednik odgovorio (aplikacija to prikazuje u odjeljku ZK)
  if (!(r.headers.get("Content-Type") || "").includes("json")) return r;
  const t = await r.text(); let o: any; try { o = JSON.parse(t); } catch { return new Response(t, { status: r.status, headers: r.headers }); }
  return new Response(JSON.stringify({ ...o, posrednik: "deno" }), { status: r.status, headers: r.headers });
});

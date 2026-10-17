// Generira lozinku za prijavu u AI asistenta i vrijednosti za tajne Workera. Pokreće se lokalno: node tools/nova-lozinka.mjs
// Ništa ne šalje na internet i ništa ne sprema u datoteke. Lozinku spremi u upravitelj lozinki.
import { webcrypto as c } from "node:crypto";
const rnd = (n) => Buffer.from(c.getRandomValues(new Uint8Array(n))).toString("base64url");
const lozinka = rnd(24);            // 32 znaka, 192 bita slučajnosti
const pepper = rnd(32), session = rnd(32);
const key = await c.subtle.importKey("raw", new TextEncoder().encode(pepper), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
const hash = Buffer.from(await c.subtle.sign("HMAC", key, new TextEncoder().encode(lozinka))).toString("hex");
console.log(`
Lozinka za prijavu u aplikaciji (spremi je u upravitelj lozinki, NE u repozitorij):
  ${lozinka}

Tajne za Worker (svaku upiši naredbom "npx wrangler secret put IME" i zalijepi vrijednost kad je zatraži):
  LOGIN_PEPPER   = ${pepper}
  LOGIN_HASH     = ${hash}
  SESSION_SECRET = ${session}

Nakon unosa zatvori ovaj terminal ili očisti ispis.`);

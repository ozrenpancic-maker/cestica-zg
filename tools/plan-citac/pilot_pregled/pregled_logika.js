/* PILOT PREGLEDA PRAVILA – logika bez sučelja (UMD: preglednik `window.PregledLogika`, Node `require`).
 *
 * Četiri odvojene razine, nikad spojene u jedan status:
 *   1. AI prijedlog        – kandidat generatora (zamrznut, samo za čitanje)
 *   2. Tehnička provjera   – deterministička provjera (zamrznuta, samo za čitanje)
 *   3. Stručna potvrda     – ljudski pregled; izvodi se ISKLJUČIVO iz revizijskog traga
 *   4. Pravna valjanost    – u pilotu uvijek NIJE_UTVRDENA; nijedna radnja je ne mijenja
 * Revizijski trag: događaji se samo dodaju; svaki nosi SHA-256 sadržaja i hash prethodnog događaja istog
 * pregledavatelja (lanac), pa se izmjena ili brisanje starog događaja otkriva provjerom lanca.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.PregledLogika = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const RADNJE = ["POTVRDA", "ISPRAVAK", "ODBIJANJE", "VRACANJE", "RUCNI_UNOS"];
  const STRUCNO = { NIJE_PREGLEDANO: "Nije pregledano", POTVRDENO: "Potvrđeno", ISPRAVLJENO: "Ispravljeno i potvrđeno",
                    ODBIJENO: "Odbijeno", VRACENO: "Vraćeno na pregled", RUCNO_UNESENO: "Ručno uneseno" };
  const PRAVNO = { NIJE_UTVRDENA: "Nije utvrđena" };
  const TEHNICKO = { AUTOMATSKI_PRIHVACEN: "Prošlo sve provjere", TEHNICKI_PROVJEREN_ZA_PREGLED: "Vrijednost provjerena, kontekst nije",
                     ZA_PREGLED: "Za pregled", ODBIJEN: "Odbijeno pri provjeri" };
  const POLJA = ["parametar", "operator", "vrijednost", "jedinica", "vrsta_gradevine", "zona", "uvjeti", "iznimke", "vrsta_pravila"];
  const MIN_OBRAZLOZENJE = 10;

  /* kanonski JSON: ključevi abecedno, bez razmaka (za hash) */
  function kanon(v) {
    if (v === null || typeof v !== "object") return JSON.stringify(v === undefined ? null : v);
    if (Array.isArray(v)) return "[" + v.map(kanon).join(",") + "]";
    return "{" + Object.keys(v).filter(k => v[k] !== undefined).sort().map(k => JSON.stringify(k) + ":" + kanon(v[k])).join(",") + "}";
  }

  async function sha256(tekst) {
    const b = new TextEncoder().encode(tekst);
    const c = (typeof crypto !== "undefined" && crypto.subtle) ? crypto : require("crypto").webcrypto;
    const h = await c.subtle.digest("SHA-256", b);
    return Array.from(new Uint8Array(h)).map(x => x.toString(16).padStart(2, "0")).join("");
  }

  /* sadržaj događaja koji se hashira (sve osim samog hasha) */
  function sadrzaj(e) { const o = Object.assign({}, e); delete o.hash; return o; }

  /* provjera prije spremanja; vraća popis grešaka (prazan = ispravno) */
  function provjeriDogadjaj(e, kandidat) {
    const g = [];
    if (!RADNJE.includes(e.radnja)) g.push("nepoznata radnja");
    if ("pravna_valjanost" in e || (e.poslije && "pravna_valjanost" in e.poslije)) g.push("pravnu valjanost pilot ne može mijenjati");
    if (!e.obrazlozenje || e.obrazlozenje.trim().length < MIN_OBRAZLOZENJE) g.push(`obrazloženje mora imati barem ${MIN_OBRAZLOZENJE} znakova`);
    if (!e.tko) g.push("nema pregledavatelja");
    if (!e.kada) g.push("nema vremena");
    if (e.radnja === "RUCNI_UNOS") {
      if (!e.poslije || !e.poslije.parametar) g.push("ručni unos mora imati parametar");
      if (!e.clanak) g.push("ručni unos mora imati članak");
      if (!e.citat) g.push("ručni unos mora imati doslovni citat");
    } else {
      if (!kandidat) g.push("nema kandidata");
      if (e.radnja === "ISPRAVAK" && (!e.poslije || !Object.keys(razlike(kandidat ? kandidat.ai_prijedlog : {}, e.poslije)).length))
        g.push("ispravak mora nešto promijeniti");
      if (e.radnja === "POTVRDA" && kandidat && kandidat.tehnicka_provjera.status === "ODBIJEN")
        g.push("kandidat odbijen pri provjeri ne može se samo potvrditi: ispravi ga ili odbij");
    }
    return g;
  }

  function razlike(a, b) {
    const r = {};
    for (const k of POLJA) if (b && k in b && kanon(a ? a[k] : null) !== kanon(b[k])) r[k] = { prije: a ? a[k] : null, poslije: b[k] };
    return r;
  }

  /* novi događaj s lancem: prethodni = hash zadnjeg događaja istog pregledavatelja */
  async function napraviDogadjaj(osnova, prethodniHash) {
    const e = Object.assign({ v: 1, prethodni: prethodniHash || null }, osnova);
    e.hash = await sha256(kanon(sadrzaj(e)));
    return e;
  }

  /* provjera lanca po pregledavatelju; vraća {ispravno, greske[]} */
  async function provjeriLanac(dogadjaji) {
    const po = {};
    for (const e of dogadjaji) (po[e.tko] = po[e.tko] || []).push(e);
    const greske = [];
    for (const [tko, L] of Object.entries(po)) {
      const red = L.slice().sort((x, y) => (x.rb - y.rb) || String(x.kada).localeCompare(String(y.kada)));
      let pre = null;
      for (const e of red) {
        const h = await sha256(kanon(sadrzaj(e)));
        if (h !== e.hash) greske.push({ tko, id: e.id, greska: "sadržaj izmijenjen nakon spremanja" });
        if ((e.prethodni || null) !== pre) greske.push({ tko, id: e.id, greska: "prekinut lanac (događaj nedostaje ili je umetnut)" });
        pre = e.hash;
      }
    }
    return { ispravno: greske.length === 0, greske };
  }

  /* stručni status kandidata = zadnji događaj za taj kandidat (po vremenu); trag se nikad ne prepisuje */
  function strucniStatus(dogadjaji, kandidatId) {
    const L = dogadjaji.filter(e => e.kandidat === kandidatId && e.radnja !== "RUCNI_UNOS")
                       .sort((a, b) => String(a.kada).localeCompare(String(b.kada)));
    if (!L.length) return { stanje: "NIJE_PREGLEDANO", dogadjaj: null, broj: 0 };
    const z = L[L.length - 1];
    const stanje = { POTVRDA: "POTVRDENO", ISPRAVAK: "ISPRAVLJENO", ODBIJANJE: "ODBIJENO", VRACANJE: "VRACENO" }[z.radnja];
    return { stanje, dogadjaj: z, broj: L.length };
  }

  /* sve četiri razine za jedan kandidat */
  function razine(kandidat, dogadjaji) {
    const s = strucniStatus(dogadjaji, kandidat.id);
    return { ai: "PRIJEDLOG", tehnicka: kandidat.tehnicka_provjera.status, strucna: s.stanje, pravna: "NIJE_UTVRDENA", zadnji: s.dogadjaj };
  }

  /* pravilo kakvo vrijedi nakon stručnog pregleda (null ako nije potvrđeno) */
  function potvrdenoPravilo(kandidat, dogadjaji) {
    const s = strucniStatus(dogadjaji, kandidat.id);
    if (s.stanje === "POTVRDENO") return Object.assign({}, kandidat.ai_prijedlog, { izvor: "AI + stručna potvrda", dogadjaj: s.dogadjaj.id });
    if (s.stanje === "ISPRAVLJENO") return Object.assign({}, kandidat.ai_prijedlog, s.dogadjaj.poslije, { izvor: "AI + ispravak", dogadjaj: s.dogadjaj.id });
    return null;
  }

  /* mjerenje: aktivno vrijeme po načinu rada i članku */
  function mjerenje(dogadjaji, kandidati) {
    const kc = {}; for (const k of kandidati) kc[k.id] = k.clanak;
    const out = {};
    for (const e of dogadjaji) {
      const nacin = e.radnja === "RUCNI_UNOS" ? "RUCNI_UNOS" : "PREGLED_AI";
      const cl = e.radnja === "RUCNI_UNOS" ? e.clanak : kc[e.kandidat];
      const k = nacin + ":" + cl;
      const o = out[k] = out[k] || { nacin, clanak: cl, dogadjaja: 0, ms: 0, zavrsenih_pravila: 0 };
      o.dogadjaja++; o.ms += Math.max(0, e.trajanje_ms || 0);
      if (["POTVRDA", "ISPRAVAK", "RUCNI_UNOS"].includes(e.radnja)) o.zavrsenih_pravila++;
    }
    for (const o of Object.values(out)) o.s_po_pravilu = o.zavrsenih_pravila ? Math.round(o.ms / o.zavrsenih_pravila / 100) / 10 : null;
    return Object.values(out).sort((a, b) => a.clanak - b.clanak || a.nacin.localeCompare(b.nacin));
  }

  /* --- prostorno povezivanje (WGS84, mali obuhvat: dovoljna je ravninska aproksimacija) --- */
  function tockaUPoligonu(p, prsten) {
    let u = false;
    for (let i = 0, j = prsten.length - 1; i < prsten.length; j = i++) {
      const [xi, yi] = prsten[i], [xj, yj] = prsten[j];
      if (((yi > p[1]) !== (yj > p[1])) && (p[0] < (xj - xi) * (p[1] - yi) / (yj - yi) + xi)) u = !u;
    }
    return u;
  }
  function povrsinaM2(prsten) {
    const lat0 = prsten[0][1] * Math.PI / 180, kx = 111320 * Math.cos(lat0), ky = 110540;
    let s = 0;
    for (let i = 0, j = prsten.length - 1; i < prsten.length; j = i++) s += (prsten[j][0] * kx) * (prsten[i][1] * ky) - (prsten[i][0] * kx) * (prsten[j][1] * ky);
    return Math.abs(s / 2);
  }
  /* udio čestice u zoni: mreža točaka unutar okvira čestice (deterministički, bez knjižnice) */
  function udioUZoni(cestica, zona, n) {
    n = n || 40;
    const xs = cestica.map(c => c[0]), ys = cestica.map(c => c[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    let u = 0, z = 0;
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      const p = [x0 + (i + 0.5) * (x1 - x0) / n, y0 + (j + 0.5) * (y1 - y0) / n];
      if (tockaUPoligonu(p, cestica)) { u++; if (tockaUPoligonu(p, zona)) z++; }
    }
    return u ? z / u : 0;
  }

  /* važenje plana na dan (ISO datum) iz evidencije PGŽ (datumi »dd.mm.gggg.«) */
  function vaziNaDan(evidencija, dan) {
    const d = s => { if (!s) return null; const m = /(\d{2})\.(\d{2})\.(\d{4})/.exec(s); return m ? `${m[3]}-${m[2]}-${m[1]}` : null; };
    const od = d(evidencija.datum_stupanja_na_snagu), doo = d(evidencija.datum_van_snage);
    if (!od) return { vazi: null, razlog: "nema datuma stupanja na snagu" };
    if (dan < od) return { vazi: false, razlog: `plan stupa na snagu ${od}` };
    if (doo && dan >= doo) return { vazi: false, razlog: `plan van snage od ${doo}` };
    return { vazi: true, razlog: `na snazi od ${od}` + (doo ? ` do ${doo}` : ", bez upisanog prestanka") };
  }

  /* pravila koja vrijede za česticu: samo stručno potvrđena, samo za zone s vektorskom granicom */
  function pravilaZaCesticu(cestica, zone, kandidati, dogadjaji, prag) {
    prag = prag == null ? 0.5 : prag;
    const out = [];
    for (const z of zone) {
      const udio = udioUZoni(cestica.prsten, z.geometrija.coordinates[0]);
      if (udio <= 0) continue;
      for (const k of kandidati) {
        const oz = ((k.ai_prijedlog.zona || {}).oznake) || [];
        if (!oz.includes(z.oznaka)) continue;
        const p = potvrdenoPravilo(k, dogadjaji);
        out.push({ kandidat: k.id, zona: z.oznaka, udio, pravilo: p, stanje: p ? (udio >= prag ? "VRIJEDI" : "DJELOMICNO_U_ZONI") : "NIJE_STRUCNO_POTVRDENO" });
      }
    }
    return out;
  }

  return { RADNJE, STRUCNO, PRAVNO, TEHNICKO, POLJA, MIN_OBRAZLOZENJE, kanon, sha256, provjeriDogadjaj, razlike, napraviDogadjaj,
           provjeriLanac, strucniStatus, razine, potvrdenoPravilo, mjerenje, tockaUPoligonu, povrsinaM2, udioUZoni, vaziNaDan, pravilaZaCesticu };
});

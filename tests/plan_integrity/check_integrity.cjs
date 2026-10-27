const fs=require('fs'),vm=require('vm'),assert=require('assert');
const app=fs.readFileSync(__dirname+'/../../src/app.template.html','utf8');
const start=app.indexOf('const DB_PARAM='),end=app.indexOf('function dbCalc(',start);
const s=app.slice(start,end).replace('function dbMatch(ctx,db=RULES_DB)', 'function dbMatch(ctx,db)');
const c=vm.createContext({}); vm.runInContext(s+'\nthis.f={dbMatch,dbSourceIntegrity};',c);
const p={id:'p1',naziv:'Test',status_vazenja:'važeći',primjenjiva_revizija:'R01',obuhvat:{jls:['Grad Krk'],gis:{status:'potvrđeno'}},odluke:[{id:'d1',url:'https://example.org',naziv:'Odluka'}]};
const r={id:'r1',plan_id:'p1',odluka_id:'d1',clanak:'1',citat:'citat',parametar:'kig',vrijednost:0.25,izvor_revizija:'R01',pravni_status:{razina:'potvrđeno',datum_provjere:'2026-10-27'},gis_status:{razina:'potvrđeno'},primjenjivost:{zone:['M11'],vrste_gradnje:['obiteljska kuća'],nacin_gradnje:['slobodnostojeća']}};
function m(ctx={},over={}) { const rr={...r,...over,primjenjivost:{...r.primjenjivost,...over.primjenjivost}}; return c.f.dbMatch({jls:'Grad Krk',zone:['M11'],...ctx},{planovi:[p],pravila:[rr]}).grupe[0].rules[0]; }
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'}).calc,true);
assert.strictEqual(m({nacin:'slobodnostojeća'}).calc,false,'unknown type fail closed');
assert.strictEqual(m({vrsta:'obiteljska kuća'}).calc,false,'unknown mode fail closed');
assert.strictEqual(m({vrsta:'druga',nacin:'slobodnostojeća'}).calc,false);
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'},{izvor_revizija:'R02'}).calc,false);
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'},{status_aktualnosti:'zastarjelo'}).calc,false);
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'},{integritet_izvora:'neusklađeno'}).calc,false);
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'},{izvor_revizija:''}).calc,true,'unknown rev does not imply mismatch; status remains contextual');
assert.strictEqual(m({vrsta:'obiteljska kuća',nacin:'slobodnostojeća'},{primjenjivost:{nacin_gradnje:[]}}).calc,true);
console.log('9/9 integritet testova prolazi');

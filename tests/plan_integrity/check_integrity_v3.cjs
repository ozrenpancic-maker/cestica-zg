const fs=require('fs'),vm=require('vm'),assert=require('assert');
const app=fs.readFileSync(__dirname+'/../../src/app.template.html','utf8');
const s=app.slice(app.indexOf('const DB_PARAM='),app.indexOf('function dbHtml(')).replace('function dbMatch(ctx,db=RULES_DB)','function dbMatch(ctx,db)');
const c=vm.createContext({});vm.runInContext(s+'\nthis.f={dbMatch,dbCalc,dbResolve};',c);
const p={id:'p1',naziv:'Test',vrsta:'UPU',status_vazenja:'važeći',primjenjiva_revizija:'R01',obuhvat:{jls:['Grad Krk'],gis:{status:'potvrđeno'}},odluke:[{id:'d1',url:'https://example.org',naziv:'Odluka'}]};
const rule={id:'r1',plan_id:'p1',odluka_id:'d1',clanak:'1',citat:'citat',parametar:'kig',vrijednost:0.25,izvor_revizija:'R01',pravni_status:{razina:'potvrđeno',datum_provjere:'2026-10-27'},gis_status:{razina:'potvrđeno'},primjenjivost:{zone:['M11'],vrste_gradnje:['obiteljska kuća']}};
const ctx={jls:'Grad Krk',zone:['M11'],vrsta:'obiteljska kuća'};
const make=(rs)=>c.f.dbMatch(ctx,{planovi:[p],pravila:rs.map((r,i)=>({...rule,id:'r'+i,...r}))});
let n=0;function t(name,f){f();n++;}
t('one valid',()=>assert.strictEqual(c.f.dbCalc(make([{}]),405).tl,101.25));
t('conflict same plan',()=>{const M=make([{}, {clanak:'2',vrijednost:0.3}]);assert.strictEqual(M.sukobi.length,1);assert.strictEqual(c.f.dbCalc(M,405).tl,null);assert.strictEqual(c.f.dbResolve(M,'kig').reason,'conflict')});
t('equivalent numeric',()=>{const M=make([{}, {clanak:'2',vrijednost:'0,250'}]);assert.strictEqual(M.sukobi.length,0);assert.strictEqual(c.f.dbCalc(M,405).tl,101.25)});
t('bad numeric suffix',()=>{const M=make([{vrijednost:'0.25 uvjetno'}]);assert.strictEqual(c.f.dbCalc(M,405).tl,null);assert.strictEqual(c.f.dbResolve(M,'kig').reason,'not_numeric')});
t('formula not parsed',()=>assert.strictEqual(c.f.dbCalc(make([{vrijednost:'MAX(h/2,4)'}]),405).tl,null));
t('missing source',()=>assert.strictEqual(c.f.dbResolve(make([]),'kig').reason,'missing'));
t('different unit conflict',()=>assert.strictEqual(make([{}, {jedinica:'m2'}]).sukobi.length,1));
t('provenance retained',()=>assert.strictEqual(c.f.dbResolve(make([{}]),'kig').sources[0].r.clanak,'1'));
t('unrelated parameters remain calculable',()=>{const M=make([{}, {clanak:'2',vrijednost:0.3},{parametar:'kis',vrijednost:1}]);const a=c.f.dbCalc(M,405);assert.strictEqual(a.tl,null);assert.strictEqual(a.gbp,405)});
console.log(`${n}/${n} ciljanih testova v3 prolazi`);

// Test cijelog lanca bez troška: aplikacija (jsdom) → pravi Worker (Miniflare) → lažni Anthropic. Pokretanje: cd worker && npm run test:e2e
import { Miniflare } from "miniflare";
import { fileURLToPath } from "node:url";
const ROOT = fileURLToPath(new URL("../..", import.meta.url));
import { webcrypto as c } from "node:crypto";
import { spawn } from "node:child_process";
const PW="e2e-lozinka-"+"z".repeat(20), PEPPER="pep-e2e-xxxxxxxx", SES="ses-e2e-yyyyyyyy";
const k=await c.subtle.importKey("raw",new TextEncoder().encode(PEPPER),{name:"HMAC",hash:"SHA-256"},false,["sign"]);
const HASH=Buffer.from(await c.subtle.sign("HMAC",k,new TextEncoder().encode(PW))).toString("hex");
let calls=0, toolsSeen=new Set();
const mf=new Miniflare({modules:true,scriptPath:fileURLToPath(new URL("../src/index.js", import.meta.url)),compatibilityDate:"2026-08-01",port:8787,
 durableObjects:{GUARD:{className:"Guard",useSQLite:true}},
 bindings:{AI_ENABLED:"true",ALLOWED_ORIGINS:"https://ozrenpancic-maker.github.io,http://localhost:8000",MONTHLY_LIMIT_USD:"5",SESSION_EPOCH:"1",ANTHROPIC_API_KEY:"sk-ant-TEST-NE-PRAVI",LOGIN_HASH:HASH,LOGIN_PEPPER:PEPPER,SESSION_SECRET:SES,RATE_PER_MIN:"60"},
 outboundService:async(req)=>{const b=await req.json(); calls++; b.tools.forEach(t=>toolsSeen.add(t.name));
   const last=b.messages[b.messages.length-1], hasRes=Array.isArray(last.content)&&last.content.some(x=>x.type==="tool_result");
   const content=hasRes?[{type:"text",text:"KRATKO: e2e odgovor.\nIZVORI: test"}]:[{type:"tool_use",id:"tu_"+calls,name:"getCurrentParcel",input:{}}];
   return new Response(JSON.stringify({content,usage:{input_tokens:6000,output_tokens:150}}),{headers:{"content-type":"application/json"}});}});
await mf.ready;
const p=spawn("node",["tests/ai-eval/run-eval.js"],{cwd:ROOT,env:{...process.env,WORKER_URL:"http://localhost:8787",AI_LOZINKA:PW,EVAL_PAUSE_MS:"0"},stdio:["ignore","pipe","inherit"]});
let out=""; p.stdout.on("data",d=>out+=d);
await new Promise(r=>p.on("close",r));
console.log(out.trim().split("\n").pop());
console.log("pozivi lažnog Anthropica:",calls,"| alati koje je model vidio:",[...toolsSeen].join(","));
const st=await (await mf.dispatchFetch("http://localhost:8787/login",{method:"POST",headers:{origin:"https://ozrenpancic-maker.github.io","content-type":"application/json"},body:JSON.stringify({lozinka:PW})})).json();
const s=await (await mf.dispatchFetch("http://localhost:8787/status",{headers:{origin:"https://ozrenpancic-maker.github.io",authorization:"Bearer "+st.token}})).json();
console.log("potrošnja na Workeru:",JSON.stringify(s.potrosnja)); const fs=await import("node:fs"); for(const f of fs.readdirSync(ROOT+"tests/ai-eval")) if(/^izvjestaj-\d/.test(f)) fs.unlinkSync(ROOT+"tests/ai-eval/"+f);
await mf.dispose();

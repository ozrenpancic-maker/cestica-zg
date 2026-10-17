// Ispis izvučenih parametara za sva pravila, za ručnu provjeru prema tekstu odluke.
const {JSDOM}=require("./node_modules/jsdom");
const fs=require("fs"),path=require("path");
let html=fs.readFileSync(path.join(__dirname,"..","index.html"),"utf8").replace(/<script src[^>]*><\/script>/g,"");
const w=new JSDOM(html,{runScripts:"dangerously",url:"https://e.org/",beforeParse(w){w.L=new Proxy(function(){},{get:()=>w.L,apply:()=>w.L});w.fetch=()=>Promise.reject(1)}}).window;
const E=n=>w.eval(n);
const sets={GUP:E("RULES"),SE:E("RULES_SE"),PP:E("RULES_PP")};
const only=process.argv[2];
for(const [sn,R] of Object.entries(sets)) for(const [c,r] of Object.entries(R)){
  if(only&&!(sn+" "+c).includes(only)) continue;
  for(const z of r.zone){
    if(!/stambe|mješovit/i.test(z.zona)) continue;
    const row=["slob","polu","ugr"].map(t=>{const p=E("parseParams")(E("normKeys")(z),t);return t+":"+JSON.stringify(p)}).join(" ")+"\n   "+E("ruleParams")(z,"slob",800).filter(x=>!["minC","izg","kis","gbp","teren"].includes(x.id)).map(x=>x.id+"="+(x.value||"–")+"["+x.status+"]").join(" | ");
    console.log(`${sn} ${c} | ${z.zona.slice(0,50)}\n   ${row}`);
    if(process.argv[3]) for(const [k,v] of Object.entries(E("normKeys")(z))) console.log("     ["+k+"] "+v.slice(0,260));
  }
}

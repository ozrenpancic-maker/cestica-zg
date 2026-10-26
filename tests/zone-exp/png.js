// Minimalni PNG dekoder za testove (8 bita, tipovi 2, 3 i 6, bez preplitanja). Vraća {width,height,data:RGBA}.
const zlib=require("zlib");
module.exports=function decodePng(buf){
  if(buf.readUInt32BE(0)!==0x89504e47) throw new Error("nije PNG");
  let o=8,W,H,bd,ct,il,pal=null,trns=null; const idat=[];
  while(o<buf.length){const n=buf.readUInt32BE(o), t=buf.toString("ascii",o+4,o+8), d=buf.subarray(o+8,o+8+n); o+=12+n;
    if(t==="IHDR"){W=d.readUInt32BE(0);H=d.readUInt32BE(4);bd=d[8];ct=d[9];il=d[12];}
    else if(t==="PLTE") pal=d; else if(t==="tRNS") trns=d; else if(t==="IDAT") idat.push(d); else if(t==="IEND") break;}
  if(bd!==8||il!==0||![2,3,6].includes(ct)) throw new Error("nepodržan PNG");
  const bpp={2:3,3:1,6:4}[ct], st=W*bpp, raw=zlib.inflateSync(Buffer.concat(idat)), px=Buffer.alloc(st*H);
  for(let y=0;y<H;y++){const f=raw[y*(st+1)], src=raw.subarray(y*(st+1)+1,(y+1)*(st+1)), cur=px.subarray(y*st,(y+1)*st), prev=y?px.subarray((y-1)*st,y*st):Buffer.alloc(st);
    for(let i=0;i<st;i++){const a=i>=bpp?cur[i-bpp]:0,b=prev[i],c=i>=bpp?prev[i-bpp]:0; let v=src[i];
      if(f===1)v+=a; else if(f===2)v+=b; else if(f===3)v+=(a+b)>>1; else if(f===4){const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c); v+=pa<=pb&&pa<=pc?a:pb<=pc?b:c;}
      cur[i]=v&255;}}
  const out=new Uint8ClampedArray(W*H*4);
  for(let i=0;i<W*H;i++){
    if(ct===3){const k=px[i]; out[i*4]=pal[k*3];out[i*4+1]=pal[k*3+1];out[i*4+2]=pal[k*3+2];out[i*4+3]=trns&&k<trns.length?trns[k]:255;}
    else if(ct===2){out.set([px[i*3],px[i*3+1],px[i*3+2],255],i*4);} else out.set(px.subarray(i*4,i*4+4),i*4);}
  return {width:W,height:H,data:out};
};

// Sastavlja index.html s lokalnim Leafletom i Turfom (bez mreže) za provjere u pregledniku: node mobile/make_local.js
const fs=require("fs"),path=require("path"); const R=path.join(__dirname,"..");
let h=fs.readFileSync(path.join(R,"..","index.html"),"utf8"); const lib=f=>fs.readFileSync(path.join(R,"node_modules",f),"utf8");
h=h.replace(/<script src="[^"]*leaflet[^"]*"><\/script>/,()=>"<script>"+lib("leaflet/dist/leaflet.js")+"</script>").replace(/<script src="[^"]*turf[^"]*"><\/script>/i,()=>"<script>"+lib("@turf/turf/turf.min.js")+"</script>").replace(/<link rel="stylesheet" href="https:\/\/cdnjs[^>]*>/,()=>"<style>"+lib("leaflet/dist/leaflet.css")+"</style>");
fs.mkdirSync(path.join(__dirname,"out"),{recursive:true}); fs.writeFileSync(path.join(__dirname,"out","preview_local.html"),h); console.log("tests/mobile/out/preview_local.html");

# Provjera koordinata i položaja: učitaj vodove (EPSG:3035, redoslijed osi N,E), pretvori u WGS84 i izmjeri udaljenosti od poznatih točaka.
import math, json, collections, pickle
from lxml import etree
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.strtree import STRtree
U="/mnt/user-data/uploads/"
T=Transformer.from_crs(3035,4326)          # bez always_xy: ulaz (N,E) prema EPSG:3035, izlaz (lat,lon)
TM=Transformer.from_crs(4326,3765,always_xy=True)  # HTRS96/TM za metričke udaljenosti
FILES={"vodovod":("1792266626567_UtilityLink.gml","1792266626567_WaterPipe.gml",None),"kanalizacija":("1792266613487_UtilityLink.gml","1792266613487_SewerPipe.gml",None),"struja":("1792266600131_UtilityLink.gml","1792266600131_ElectricityPipe.gml","operatingVoltage")}
GML="{http://www.opengis.net/gml/3.2}"; XL="{http://www.w3.org/1999/xlink}href"
loc=lambda t:t.split("}")[-1]
nets={}
for net,(lf,pf,vk) in FILES.items():
    info={}
    for ev,el in etree.iterparse(U+pf,events=("end",),tag="{*}member",huge_tree=True):
        p=el[0]; link=None; d={}
        for c in p:
            t=loc(c.tag)
            if t=="link": link=(c.get(XL) or "").lstrip("#")
            if t=="currentStatus": d["st"]=(c.get(XL) or "").split("/")[-1]
            if vk and t==vk: d["v"]=(c.text or "").strip()
        if link: info[link]=d
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    geoms=[];meta=[]; lat0=lon0=1e9; lat1=lon1=-1e9
    for ev,el in etree.iterparse(U+lf,events=("end",),tag="{*}UtilityLink",huge_tree=True):
        lid=el.get(GML+"id"); pl=el.find(".//{*}posList")
        if pl is not None and lid in info:
            v=list(map(float,pl.text.split()))
            la,lo=T.transform(v[0::2],v[1::2]); la=list(la); lo=list(lo)
            lat0=min(lat0,*la);lat1=max(lat1,*la);lon0=min(lon0,*lo);lon1=max(lon1,*lo)
            x,y=TM.transform(lo,la); geoms.append(LineString(list(zip(x,y)))); meta.append(info[lid])
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    nets[net]=(geoms,meta); print(net,"vodova s geometrijom:",len(geoms),"| obuhvat WGS84: lat %.4f–%.4f, lon %.4f–%.4f"%(lat0,lat1,lon0,lon1),flush=True)
pickle.dump({k:([g.wkb for g in v[0]],v[1]) for k,v in nets.items()},open("/tmp/claude-0/infra/vodovi.pkl","wb"))
TESTS=[("Trg bana Jelačića (sredina trga)",45.81305,15.97716),("Ilica kod Frankopanske (ulica)",45.81268,15.96889),("Savska c. kod Vodnikove (ulica)",45.80340,15.96620),
       ("Jarunsko jezero, sredina vode",45.78330,15.91700),("Maksimir, sredina parka",45.82680,16.01850),("Medvednica, šuma iznad Sljemena",45.90500,15.94500)]
print("\nUdaljenost do najbližeg funkcionalnog voda (m):")
trees={}
for net,(g,m) in nets.items():
    keep=[i for i,x in enumerate(m) if x.get("st") in ("functional",None) and (net!="struja" or x.get("v")=="Niski napon")]
    trees[net]=(STRtree([g[i] for i in keep]),[g[i] for i in keep])
for name,la,lo in TESTS:
    x,y=TM.transform(lo,la); p=Point(x,y); row=[]
    for net,(tr,gs) in trees.items():
        i=tr.nearest(p); row.append(f"{net} {gs[i].distance(p):7.1f}")
    print(f"  {name:40s} "+" | ".join(row))

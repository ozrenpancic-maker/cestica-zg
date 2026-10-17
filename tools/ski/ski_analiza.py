# Analiza DGU SKI INSPIRE GML za Grad Zagreb (vodovod, kanalizacija, struja). Streaming (lxml.iterparse).
import sys, json, math, collections
from lxml import etree
from pyproj import Transformer
U="/mnt/user-data/uploads/"
NETS={"vodovod":("1792266626567_UtilityLink.gml","1792266626567_WaterPipe.gml","1792266626567_Appurtenance.gml"),
      "kanalizacija":("1792266613487_UtilityLink.gml","1792266613487_SewerPipe.gml","1792266613486_Appurtenance.gml"),
      "struja":("1792266600131_UtilityLink.gml","1792266600131_ElectricityPipe.gml","1792266600131_Appurtenance.gml")}
T=Transformer.from_crs(3035,4326,always_xy=True)
GML="{http://www.opengis.net/gml/3.2}"; XL="{http://www.w3.org/1999/xlink}href"
def local(t): return t.split("}")[-1]
out={}
for net,(lf,pf,af) in NETS.items():
    st=collections.Counter(); vp=collections.Counter(); srs=collections.Counter(); fict=collections.Counter(); geomt=collections.Counter()
    n=0; L=0.0; xmin=ymin=1e18; xmax=ymax=-1e18; cells=collections.Counter(); links={}
    for ev,el in etree.iterparse(U+lf,events=("end",),tag="{*}UtilityLink",huge_tree=True):
        n+=1; lid=el.get(GML+"id")
        for c in el.iter():
            t=local(c.tag)
            if t in("LineString","Curve","MultiCurve","Point"): geomt[t]+=1; srs[c.get("srsName","")]+=1
            if t=="posList":
                v=list(map(float,c.text.split())); pts=list(zip(v[0::2],v[1::2])); ln=sum(math.dist(pts[i],pts[i+1]) for i in range(len(pts)-1)); L+=ln
                for x,y in pts: xmin=min(xmin,x);xmax=max(xmax,x);ymin=min(ymin,y);ymax=max(ymax,y)
                mx,my=pts[len(pts)//2]; cells[(int(mx//1000),int(my//1000))]+=1; links[lid]=ln
            if t=="currentStatus": st[(c.get(XL) or "").split("/")[-1] or "prazno"]+=1
            if t=="verticalPosition": vp[c.text]+=1
            if t=="fictitious": fict[c.text]+=1
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    # atributi cijevi/vodova
    attrs=collections.defaultdict(collections.Counter); pn=0; plen=collections.defaultdict(float); missing=0
    for ev,el in etree.iterparse(U+pf,events=("end",),tag="{*}member",huge_tree=True):
        pipe=el[0]; pn+=1; link=None; key=None
        for c in pipe:
            t=local(c.tag)
            if t=="link": link=(c.get(XL) or "").lstrip("#")
            elif t in("inspireId","inNetwork","beginLifespanVersion"): continue
            else:
                v=c.text.strip() if c.text and c.text.strip() else ((c.get(XL) or "").split("/")[-1] or ("nil:"+(c.get("nilReason") or "").split("/")[-1] if c.get("{http://www.w3.org/2001/XMLSchema-instance}nil") else ""))
                attrs[t][v]+=1
                if t in("operatingVoltage","sewerWaterType","waterType"): key=v
        if link in links: plen[key]+=links[link]
        else: missing+=1
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    # objekti na mreži
    app=collections.Counter(); an=0
    for ev,el in etree.iterparse(U+af,events=("end",),tag="{*}member",huge_tree=True):
        an+=1
        for c in el.iter():
            if local(c.tag) in("appurtenanceType","specificAppurtenanceType"): app[(c.get(XL) or c.text or "").split("/")[-1]]+=1
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
    lo1,la1=T.transform(xmin,ymin); lo2,la2=T.transform(xmax,ymax)
    out[net]={"veze":n,"duljina_km":round(L/1000,1),"geometrija":dict(geomt),"srs":dict(srs),"status":dict(st),"polozaj":dict(vp),"fiktivno":dict(fict),
      "bbox_wgs84":[round(lo1,4),round(la1,4),round(lo2,4),round(la2,4)],"km2_celija_s_vodom":len(cells),
      "cijevi":pn,"cijevi_bez_geometrije":missing,"atributi":{k:dict(v.most_common(12)) for k,v in attrs.items()},"duljina_po_vrsti_km":{str(k):round(v/1000,1) for k,v in plen.items()},
      "objekti":an,"vrste_objekata":dict(app.most_common(15))}
    json.dump({k:list(v) for k,v in []},open("/dev/null","w"))
    json.dump([[a,b,c] for (a,b),c in cells.items()],open(f"/tmp/claude-0/infra/{net}_celije.json","w"))
    print(net, json.dumps(out[net],ensure_ascii=False)[:1500], flush=True)
json.dump(out,open("/tmp/claude-0/infra/analiza.json","w"),ensure_ascii=False,indent=1)

import pickle, statistics, json
from lxml import etree
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import Point
from shapely.strtree import STRtree
U="/mnt/user-data/uploads/"
T=Transformer.from_crs(3035,4326); TM=Transformer.from_crs(4326,3765,always_xy=True)
d=pickle.load(open("/tmp/claude-0/infra/vodovi.pkl","rb"))
G={k:[wkb.loads(b) for b in v[0]] for k,v in d.items()}
trees={k:STRtree(v) for k,v in G.items()}
def nearest(net,x,y): p=Point(x,y); i=trees[net].nearest(p); return G[net][i].distance(p)
# 1) objekti na mreži (točke) prema vlastitoj mreži
for net,af,kinds in [("vodovod","1792266626567_Appurtenance.gml",{"hydrant","zatvarac"}),("kanalizacija","1792266613486_Appurtenance.gml",{"okno"}),("struja","1792266600131_Appurtenance.gml",{"transformatorskaStanica","razvodniOrmaric"})]:
    ds=[]; n=0
    for ev,el in etree.iterparse(U+af,events=("end",),tag="{*}member",huge_tree=True):
        k=None
        for c in el.iter():
            if c.tag.endswith("appurtenanceType") or c.tag.endswith("specificAppurtenanceType"):
                v=(c.get("{http://www.w3.org/1999/xlink}href") or c.text or "").split("/")[-1]
                if v in kinds: k=v
        pos=el.find(".//{*}pos")
        if k and pos is not None and n<4000:
            a,b=map(float,pos.text.split()[:2]); la,lo=T.transform(a,b); x,y=TM.transform(lo,la); ds.append(nearest(net,x,y)); n+=1
        el.clear()
        while el.getprevious() is not None: del el.getparent()[0]
        if n>=4000: break
    ds.sort(); q=lambda f: ds[int(f*(len(ds)-1))]
    print(f"{net}: {len(ds)} objekata ({'/'.join(sorted(kinds))}) do vlastitog voda: medijan {q(.5):.2f} m, 90 % {q(.9):.2f} m, 99 % {q(.99):.2f} m")
# 2) gradski GUP magistralni vodovod (WGS84, ArcGIS) prema DGU vodovodu
gup=[[[15.8320766132639,45.8251811726669],[15.8321184817687,45.8254350062689],[15.831959356116,45.8261148328966],[15.8323879475244,45.8269109288148],[15.8326570024981,45.8271805670225],[15.8324823603183,45.8276662181261],[15.8322922078034,45.8283271479902],[15.8323178711972,45.8288708630266],[15.8322722384609,45.8296021371468],[15.8322090200227,45.8301172590958]],
     [[15.8294694270809,45.8252001483781],[15.8291671834421,45.8256491079327],[15.8284720460063,45.8267205388716],[15.8277671419897,45.8277756396668],[15.828460159636,45.8286872463237],[15.8290010657854,45.8290083570186],[15.8303107891136,45.8292753882869],[15.8311946310930,45.8296304676631],[15.8322147240578,45.8302376307416],[15.8323379302761,45.8311535570617],[15.8311075597614,45.8312645577688],[15.8298569830982,45.8310414236301],[15.8291815073654,45.8309784965191]],
     [[16.09525383038,45.8060177047006],[16.089664110713,45.8053851505565],[16.0842005090729,45.8047093397282],[16.0816444940649,45.8043651866026],[16.0745659591122,45.8033215154325]]]
ds=[]
for line in gup:
    for lo,la in line: x,y=TM.transform(lo,la); ds.append(nearest("vodovod",x,y))
ds.sort(); print(f"GUP magistralni vodovod (3 voda, {len(ds)} točaka) do DGU vodovoda: medijan {statistics.median(ds):.1f} m, najviše {max(ds):.1f} m")
# 3) isto, ali s krivim redoslijedom osi (kontrola: mora biti potpuno pogrešno)
Tb=Transformer.from_crs(3035,4326,always_xy=True); print("kontrola krivog redoslijeda osi (prvi vod):", Tb.transform(2536512.77,4785657.26), "→ ispravno:", T.transform(2536512.77,4785657.26))

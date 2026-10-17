import pickle
from pyproj import Transformer
from shapely import wkb
from shapely.geometry import Point
from shapely.strtree import STRtree
TM=Transformer.from_crs(4326,3765,always_xy=True)
g,m=pickle.load(open("/tmp/claude-0/infra/vodovi.pkl","rb"))["struja"]
vn=[wkb.loads(b) for b,x in zip(g,m) if x.get("v")=="Visoki napon"]; tr=STRtree(vn)
pts=[(16.03857,45.87093),(16.06744,45.86546),(16.08543,45.85005),(16.08890,45.85180),(16.08722,45.85003)]
for lo,la in pts:
    x,y=TM.transform(lo,la); p=Point(x,y); i=tr.nearest(p); print(f"GUP dalekovod 110 kV postojeći ({lo},{la}) → najbliži DGU visokonaponski vod: {vn[i].distance(p):.1f} m")

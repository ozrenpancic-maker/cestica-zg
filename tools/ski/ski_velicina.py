import pickle, json, gzip, collections
from shapely import wkb
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pyproj import Transformer
TI=Transformer.from_crs(3765,4326,always_xy=True)
d=pickle.load(open("/tmp/claude-0/infra/vodovi.pkl","rb"))
fig,ax=plt.subplots(1,3,figsize=(15,5.4),dpi=110); tot={}
for k,(net,(g,m)) in enumerate(d.items()):
    keep=[wkb.loads(b) for b,x in zip(g,m) if x.get("st") in("functional",None) and (net!="struja" or x.get("v")=="Niski napon")]
    tiles=collections.defaultdict(list); nv=0; L=0
    for ln in keep:
        s=ln.simplify(0.3); c=list(s.coords); nv+=len(c); L+=ln.length
        mx,my=s.interpolate(0.5,normalized=True).coords[0]; tiles[(int(mx//1000),int(my//1000))].append([[round(x,1),round(y,1)] for x,y in c])
    raw=sum(len(json.dumps(v,separators=(",",":"))) for v in tiles.values()); gz=sum(len(gzip.compress(json.dumps(v,separators=(",",":")).encode())) for v in tiles.values())
    big=max(len(gzip.compress(json.dumps(v,separators=(",",":")).encode())) for v in tiles.values())
    tot[net]=dict(vodova=len(keep),km=round(L/1000),vrhova=nv,kvadrata_1km=len(tiles),MB=round(raw/1e6,1),MB_gzip=round(gz/1e6,1),najveci_kvadrat_kB_gzip=round(big/1e3))
    xs=[]; ys=[]; cs=[]
    for (i,j),v in tiles.items(): xs.append(i); ys.append(j); cs.append(sum(len(a) for a in v))
    ax[k].scatter(xs,ys,c=cs,s=9,marker="s",cmap="viridis"); ax[k].set_title(f"{net}{' (niski napon)' if net=='struja' else ''}: {len(tiles)} km² s vodovima"); ax[k].set_aspect("equal"); ax[k].set_xticks([]); ax[k].set_yticks([])
fig.suptitle("DGU SKI, Grad Zagreb (stanje 19. 7. 2024.): kvadrati od 1 km u kojima postoje funkcionalni vodovi"); fig.tight_layout(); fig.savefig("/tmp/claude-0/infra/obuhvat.png")
print(json.dumps(tot,ensure_ascii=False,indent=1))

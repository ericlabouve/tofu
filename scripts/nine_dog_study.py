"""Compare approved A with nine dogs and perimeter companion-shape studies."""
from pathlib import Path
import runpy,json
import numpy as np
import shapely
from shapely.geometry import Polygon,box
from shapely import affinity
from shapely.ops import unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/nine-dog-review';OUT.mkdir(parents=True,exist_ok=True)
# Reuse the exact shared-boundary construction, retaining the accepted six-dog study.
source=runpy.run_path(str(ROOT/'scripts/profile_tessellation.py'))
chosen=[p for p,(r,c) in zip(source['shapes'],source['lattice']) if 0<=r<3 and 0<=c<3]
b=unary_union(chosen).bounds
sx=120/(b[2]-b[0]);sy=100/(b[3]-b[1])
dogs=[affinity.translate(affinity.scale(p,sx,sy,origin=(0,0)),-b[0]*sx,-b[1]*sy) for p in chosen]
sheet=box(0,0,120,100)
remainder=sheet.difference(unary_union(dogs))
scraps=[p for p in getattr(remainder,'geoms',[remainder]) if p.area>1e-5]
# Use precision stable enough to avoid numerical near-contact slivers in review geometry.
print('9 dogs',sum(p.area for p in dogs)/120,'remainder regions',len(scraps),[round(p.area,1) for p in scraps],flush=True)
fig,ax=plt.subplots(figsize=(9,8))
for i,p in enumerate(dogs):
 ax.add_patch(Patch(np.array(p.exterior.coords),facecolor=['#dbb078','#edc992'][i%2],edgecolor='#564936',lw=.8));q=p.representative_point();ax.text(q.x,q.y,'D'+str(i+1),ha='center')
for i,p in enumerate(scraps):
 ax.add_patch(Patch(np.array(p.exterior.coords),facecolor='#c3d6cf',edgecolor='#564936',lw=.8));q=p.representative_point();ax.text(q.x,q.y,'R'+str(i+1),ha='center')
ax.set_xlim(-2,122);ax.set_ylim(102,-2);ax.set_aspect('equal');fig.savefig(OUT/'nine-initial.png',dpi=140)
(OUT/'nine-base.json').write_text(json.dumps(dict(dogs=[list(p.exterior.coords) for p in dogs],remainder=[list(p.exterior.coords) for p in scraps],scale=[sx,sy]),indent=2))

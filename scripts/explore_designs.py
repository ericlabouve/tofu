"""Reproducible geometric audit and silhouette studies. Units assumed millimetres."""
from pathlib import Path
import json
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely import affinity
from shapely.ops import unary_union
from scipy.interpolate import splprep, splev
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'design/review'; OUT.mkdir(parents=True,exist_ok=True)
mesh=trimesh.load(ROOT/'big_dogs_rect_13x11.stl')
def section(z):
    return [Polygon(d[:,:2]).buffer(0) for d in mesh.section([0,0,1],[0,0,z]).discrete]
loops=section(5); outer=max(loops,key=lambda p:p.area); holes=[p for p in loops if p is not outer]
opening=unary_union(holes).bounds
report=dict(units='mm assumed; STL does not encode units',bounds=mesh.bounds.tolist(),extents=mesh.extents.tolist(),watertight=bool(mesh.is_watertight),connected_components=len(mesh.split()),triangles=len(mesh.faces),volume_mm3=float(mesh.volume),opening_envelope_mm=list(opening),opening_envelope_size_mm=[opening[2]-opening[0],opening[3]-opening[1]],openings=len(holes),opening_areas_mm2=sorted([round(p.area,2) for p in holes]),section_open_area_mm2={str(z):round(sum(p.area for p in section(z))-max(p.area for p in section(z)),3) for z in [.1,5,9.9]})
mid_holes=unary_union(holes)
report['internal_contour_difference_mm2']={}
for z in [.1,9.9]:
    zs=section(z);zo=max(zs,key=lambda p:p.area)
    report['internal_contour_difference_mm2'][str(z)]=mid_holes.symmetric_difference(unary_union([p for p in zs if p is not zo])).area
fig,ax=plt.subplots(figsize=(10,9))
for i,p in enumerate(loops):
    xy=np.array(p.exterior.coords);ax.plot(xy[:,0],xy[:,1]);q=p.representative_point();ax.text(q.x,q.y,str(i))
ax.set_aspect('equal');ax.set_xlabel('mm');ax.set_ylabel('mm');fig.savefig(OUT/'prototype-section.png',dpi=140);plt.close(fig)
(OUT/'prototype-audit.json').write_text(json.dumps(report,indent=2))

sheet=box(0,0,120,100)
colors=['#f3c78e','#e7b073','#cfa46f','#f1d8b3','#ddbb8d','#ebcaa3']
def parts(g):
    return [g] if g.geom_type=='Polygon' else [p for p in g.geoms if p.geom_type=='Polygon']
def fit(p,w,h):
    a,b,c,d=p.bounds
    return affinity.scale(affinity.translate(p,-a,-b),w/(c-a),h/(d-b),origin=(0,0))
def soften(points,r=.9):
    xy=np.array(points+[points[0]],dtype=float)
    tck,_=splprep(xy.T,s=r,per=True)
    return Polygon(np.array(splev(np.linspace(0,1,300),tck)).T).buffer(0).simplify(.025,preserve_topology=True)

# A: Scale the actual measured openings; optimize crop position within source footprint.
s=1.55
source=[affinity.scale(affinity.translate(p,-opening[0],-opening[3]),s,-s,origin=(0,0)) for p in holes]
# Visual classification: nine complete dog silhouettes; the rightmost middle dog is clipped.
source_complete=[i in [0,2,4,6,7,8,12,13,15] for i,p in enumerate(loops) if p is not outer]
W=(opening[2]-opening[0])*s;H=(opening[3]-opening[1])*s
best=None
for dx in np.linspace(0,W-120,35):
 for dy in np.linspace(0,H-100,35):
    crop=box(dx,dy,dx+120,dy+100)
    complete=[p for p,g in zip(source,source_complete) if g and crop.buffer(.001).covers(p)]
    score=(len(complete),sum(p.area for p in complete))
    if best is None or score>best[0]:best=(score,dx,dy)
_,dx,dy=best
A=[];A_good=[]
for p,g in zip(source,source_complete):
    shifted=affinity.translate(p,-dx,-dy)
    for q in parts(shifted.intersection(sheet)):
        if q.area<.01:continue
        A.append(q);A_good.append(sheet.buffer(.001).covers(shifted) and g)

# B: Complete broad-legged puppies, deliberately no cut-in eyes or isolated face holes.
puppy=soften([(0,9),(3,3),(12,1),(18,3),(21,8),(21,17),(37,17),(41,12),(42,6),(46,9),(47,18),(45,24),(43,31),(44,43),(34,43),(32,32),(20,32),(17,43),(7,43),(10,29),(9,21),(2,20),(-2,16),(-2,11)],1.2)
puppy=fit(puppy,57,46)
B=[]
for row in range(2):
 for col in range(2):
    p=puppy
    if (row+col)%2:p=affinity.scale(p,-1,1,origin=(28.5,23))
    B.append(affinity.translate(p,1.5+60*col,2+50*row))
# C: Floppy-ear heads, a compact complete-shape alternative to full-body dogs.
head=soften([(9,8),(4,6),(1,10),(0,27),(2,39),(6,43),(10,40),(11,33),(12,43),(17,47),(23,47),(28,43),(29,33),(30,40),(34,43),(38,39),(40,27),(39,10),(36,6),(31,8),(28,3),(20,0),(12,3)],1.3)
head=fit(head,38.4,47.6)
C=[affinity.translate(head,.8+40*c,1.2+50*r) for r in range(2) for c in range(3)]

options=[('a','Enlarged interlocking dogs',A,A_good,'Actual prototype contours enlarged 1.55×. Boundary fragments remain.'),('b','Four rounded puppies',B,[True]*len(B),'Complete full-body silhouettes. Leftover tofu forms a connected web.'),('c','Six floppy-ear heads',C,[True]*len(C),'Compact silhouettes with broad ears. A nesting study, not a zero-scrap tessellation.')]
metrics=[]

def draw(ax,polys,good,title):
    ax.add_patch(Patch(np.array(sheet.exterior.coords),facecolor='#f0eae3',edgecolor='#756d64',lw=1))
    for i,(p,g) in enumerate(zip(polys,good)):
        ax.add_patch(Patch(np.array(p.exterior.coords),facecolor=colors[i%len(colors)] if g else '#edb7b0',edgecolor='#675a49' if g else '#a5524c',lw=.65))
        q=p.representative_point()
        if p.area>100: ax.text(q.x,q.y,str(i+1),ha='center',va='center',fontsize=8,color='#4b3e2e')
    ax.set_xlim(-3,123);ax.set_ylim(103,-3);ax.set_aspect('equal');ax.set_xticks([0,40,80,120]);ax.set_yticks([0,25,50,75,100]);ax.tick_params(labelsize=8,colors='#756d64');ax.set_xlabel('mm',color='#756d64');ax.spines[['top','right','left','bottom']].set_visible(False);ax.set_title(title,fontsize=13,loc='left',pad=14,color='#302b26')

fig,axs=plt.subplots(1,3,figsize=(16,6.5),facecolor='#fffdf9')
for ax,(key,title,polys,good,note) in zip(axs,options):
    union=unary_union(polys);complete=sum(p.area for p,g in zip(polys,good) if g)
    assert all(p.is_valid and sheet.buffer(.001).covers(p) for p in polys)
    assert abs(sum(p.area for p in polys)-union.area)<.01
    rec=dict(id=key,title=title,complete_shapes=sum(good),other_regions=len(good)-sum(good),complete_shape_area_percent=round(complete/120,1),other_area_percent=round(100-complete/120,1),note=note,shapes=[dict(points=np.round(np.array(p.exterior.coords),3).tolist(),complete=bool(g),area_mm2=round(p.area,1)) for p,g in zip(polys,good)])
    metrics.append(rec)
    draw(ax,polys,good,f'{key.upper()} / {title}')
    ax.text(0,-.27,f'{sum(good)} complete shapes · {rec["complete_shape_area_percent"]}% of sheet\n{rec["other_area_percent"]}% outside complete shapes',transform=ax.transAxes,fontsize=11,color='#594f45',linespacing=1.6)
    fig2,ax2=plt.subplots(figsize=(7,6.5),facecolor='#fffdf9');draw(ax2,polys,good,title);fig2.tight_layout();fig2.savefig(OUT/f'option-{key}.svg');plt.close(fig2)
fig.suptitle('TOFU / FIRST SILHOUETTE STUDIES',x=.05,ha='left',fontsize=20,color='#302b26')
fig.text(.05,.88,'120 × 100 mm sheets • outlines only, no decorative eyes • pink = incomplete or small regions',fontsize=11,color='#756d64')
fig.subplots_adjust(left=.05,right=.98,top=.78,bottom=.28,wspace=.18)
fig.savefig(OUT/'layout-comparison.png',dpi=160);fig.savefig(OUT/'layout-comparison.svg')
(OUT/'layout-options.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='opening_areas_mm2'},indent=2))
print(json.dumps([{k:v for k,v in m.items() if k!='shapes'} for m in metrics],indent=2))

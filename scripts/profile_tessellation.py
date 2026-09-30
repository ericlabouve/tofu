"""Shared-edge side-profile studies; all dimensions in mm.

Regularize the prototype's alternating mirrored dog lattice with a boundary-site
Voronoi partition, then deform the entire shared boundary network consistently.
No independently spaced cookie-cutter outlines or decorative face marks.
"""
from pathlib import Path
import json
import numpy as np
import trimesh
import shapely
from shapely.geometry import Polygon, MultiPoint, box
from shapely import affinity
from shapely.ops import unary_union, linemerge, polygonize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/profile-review';OUT.mkdir(parents=True,exist_ok=True)
m=trimesh.load(ROOT/'big_dogs_rect_13x11.stl')
base=Polygon(m.section([0,0,1],[0,0,5]).discrete[7][:,:2])
base=affinity.scale(affinity.translate(base,-14.4,9.18),1,-1,origin=(0,0))
PITCH_X=24.8;PITCH_Y=23.7
seeds=[];owners=[];dogs=[];heads=[];lattice=[]
for r in range(-3,7):
 for c in range(-3,8):
    mirrored=r%2!=0
    p=affinity.scale(base,-1 if mirrored else 1,1,origin=(15.55,0))
    x=c*PITCH_X+(-5.2 if mirrored else 0);y=r*PITCH_Y
    p=affinity.translate(p,x,y);dogs.append(p);lattice.append((r,c))
    heads.append((x,y,-1 if mirrored else 1))
    for t in np.arange(0,p.length,.65):
        q=p.exterior.interpolate(t);seeds.append((q.x,q.y));owners.append(len(dogs)-1)
print('Building shared boundaries...',flush=True)
cells=shapely.voronoi_polygons(MultiPoint(seeds),extend_to=box(-130,-130,280,230),ordered=True)
groups=[[] for p in dogs]
for cell,owner in zip(cells.geoms,owners):groups[owner].append(cell)
tiles=[unary_union(g) for g in groups]
# Shared simplification keeps neighboring boundaries identical.
tiles=list(shapely.coverage_simplify(np.array(tiles,dtype=object),.3))
# Smooth each shared chain once, not each dog independently. Junctions stay fixed.
network=linemerge(unary_union([p.boundary for p in tiles]))
from shapely.geometry import LineString
smooth=[]
for line in network.geoms:
    xy=np.array(line.coords)
    for _ in range(2):
        q=.75*xy[:-1]+.25*xy[1:];r=.25*xy[:-1]+.75*xy[1:]
        between=np.stack([q,r],axis=1).reshape(-1,2)
        xy=np.vstack([xy[0],between,xy[-1]])
    smooth.append(LineString(xy))
polygons=list(polygonize(smooth))
assert len(polygons)==len(tiles),(len(polygons),len(tiles))
tiles=[next(q for q in polygons if q.covers(p.representative_point())) for p in tiles]

# Smooth, global field: lift the muzzle slightly, following the supplied reference.
# Every shared vertex receives the same displacement, preserving the partition.
def warp(coords):
    xy=coords.copy();dx=np.zeros(len(xy));dy=np.zeros(len(xy))
    for x,y,sign in heads:
        ear_x=x+(.5 if sign==1 else 31.1-.5)
        muzzle_x=x+(0.7 if sign==1 else 31.1-.7)
        dy-=1.1*np.exp(-((xy[:,0]-ear_x)/1.7)**2-((xy[:,1]-y)/3.5)**2)
        dx-=sign*.5*np.exp(-((xy[:,0]-muzzle_x)/2.6)**2-((xy[:,1]-(y+3.5))/3.3)**2)
    xy[:,0]+=dx;xy[:,1]+=dy
    return xy
shapes=shapely.segmentize(np.array(tiles,dtype=object),.35)
shapes=shapely.transform(shapes,warp)
# Flatten the unwanted back hump at the shared paw/back junction.
# A single continuous displacement field moves every incident boundary together.
canonical=shapes[lattice.index((0,0))]
xy=np.array(canonical.exterior.coords)
back=xy[(xy[:,0]>=16)&(xy[:,0]<=25.7)&(xy[:,1]>9)&(xy[:,1]<14)]
back=back[np.argsort(back[:,0])]
bx,idx=np.unique(back[:,0],return_index=True);by=back[idx,1]
def smootherstep(t):
    t=np.clip(t,0,1);return t*t*t*(t*(t*6-15)+10)
def flatten_backs(coords):
    result=coords.copy();displacement=np.zeros(len(coords))
    for x,y,sign in heads:
        local_x=coords[:,0]-x
        if sign==-1:local_x=31.1-local_x
        local_y=coords[:,1]-y
        old_y=np.interp(local_x,bx,by)
        target=11.70-.04*((local_x-21.5)/3.5)**2
        weight=smootherstep((local_x-16)/2)*smootherstep((25.7-local_x)/1.0)
        displacement+=(target-old_y)*weight*np.exp(-((local_y-old_y)/2.6)**2)
    result[:,1]+=displacement
    return result
shapes=shapely.transform(shapes,flatten_backs)
shapes=shapely.set_precision(shapes,.00001)
assert all(p.is_valid and p.geom_type=='Polygon' for p in shapes)
# Study two aspect ratios. Crop search rewards full silhouettes, then their area.
sheet=box(0,0,120,100)
colors=['#d8a86e','#f0c58e','#ba8955','#e3ba87']
options=[]
for key,title,ncol,nrow in [('a','Six dogs · 3 across × 2 rows',3,2),('b','Six longer dogs · 2 across × 3 rows',2,3)]:
    chosen=[p for p,(r,c) in zip(shapes,lattice) if 0<=r<nrow and 0<=c<ncol]
    bounds=unary_union(chosen).bounds
    sx=120/(bounds[2]-bounds[0]);sy=100/(bounds[3]-bounds[1])
    scaled=[affinity.scale(p,sx,sy,origin=(0,0)) for p in shapes]
    ox=bounds[0]*sx;oy=bounds[1]*sy
    window=box(ox,oy,ox+120,oy+100)
    output=[]
    for p in scaled:
        q=p.intersection(window)
        if q.is_empty or q.area<1e-5:continue
        for piece in ([q] if q.geom_type=='Polygon' else list(q.geoms)):
            if piece.area<1e-5:continue
            shifted=affinity.translate(piece,-ox,-oy)
            output.append((shifted,window.buffer(.000001).covers(p)))
    # Suppress pointless cuts between adjacent boundary scraps.
    whole=[p for p,g in output if g]
    remainder=sheet.difference(unary_union(whole))
    scraps=[remainder] if remainder.geom_type=='Polygon' else list(remainder.geoms)
    output=[(p,True) for p in whole]+[(p,False) for p in scraps if p.area>1e-6]
    full_area=sum(p.area for p,g in output if g)
    union=unary_union([p for p,g in output]);gap=sheet.difference(union).area;overlap=sum(p.area for p,g in output)-union.area
    assert gap<.01 and abs(overlap)<.01,(gap,overlap)
    count=sum(g for p,g in output)
    # Do not label the count before measuring it.
    rec=dict(id=key,title=title,complete_shapes=count,perimeter_regions=len(scraps),smallest_perimeter_region_mm2=round(min(p.area for p in scraps),2),complete_area_percent=round(full_area/120,1),boundary_area_percent=round(100-full_area/120,1),interior_unassigned_area_mm2=round(gap,6),overlap_area_mm2=round(overlap,6),scale=[sx,sy],crop_origin=[ox,oy],nominal_cutting_line_width_mm=0,pieces=[dict(points=np.round(np.array(p.exterior.coords),4).tolist(),complete=bool(g),area_mm2=round(p.area,2)) for p,g in output])
    options.append((rec,output))
    print(title,rec['complete_area_percent'],'% full silhouettes',flush=True)

# Isolated piece shows what the cut actually produces, without eyes or fake detail.
fig,axes=plt.subplots(2,2,figsize=(14,11),gridspec_kw={'height_ratios':[2,1]},facecolor='#fffdf8')
for col,(rec,output) in enumerate(options):
    ax=axes[0,col]
    for i,(p,g) in enumerate(output):
        ax.add_patch(Patch(np.array(p.exterior.coords),facecolor=colors[i%len(colors)] if g else '#e4e0d8',edgecolor='#544a3c',lw=.65))
    ax.set_xlim(-2,122);ax.set_ylim(102,-2);ax.set_aspect('equal');ax.set_title(rec['id'].upper()+' / '+rec['title'],loc='left',fontsize=16,pad=15)
    ax.set_xticks([0,40,80,120]);ax.set_yticks([0,25,50,75,100]);ax.tick_params(labelsize=9);ax.set_xlabel('mm');ax.spines[['top','right','left','bottom']].set_visible(False)
    ax.text(0,-.2,f"{rec['complete_area_percent']}% complete profiles · {rec['boundary_area_percent']}% perimeter pieces\nShared cutting boundaries · no unassigned interior gaps",transform=ax.transAxes,fontsize=11,linespacing=1.6)
    single=max((p for p,g in output if g),key=lambda p:p.area);b=single.bounds;single=affinity.translate(single,-b[0],-b[1])
    ax=axes[1,col];ax.add_patch(Patch(np.array(single.exterior.coords),facecolor=colors[0],edgecolor='#544a3c',lw=1));ax.set_xlim(-4,b[2]-b[0]+4);ax.set_ylim(b[3]-b[1]+4,-6);ax.set_aspect('equal');ax.axis('off');ax.set_title('Actual isolated cut profile — no facial decoration',fontsize=11,pad=0)
fig.suptitle('REFERENCE-LED DOGS / SHARED-EDGE STUDY',x=.06,ha='left',fontsize=21)
fig.text(.06,.935,'120 × 100 mm · tan = whole profiles · gray = honest perimeter offcuts',fontsize=12,color='#695f50')
fig.subplots_adjust(top=.87,bottom=.05,left=.06,right=.97,hspace=.6,wspace=.2)
fig.savefig(OUT/'profile-comparison.png',dpi=160);fig.savefig(OUT/'profile-comparison.svg')
(OUT/'profiles.json').write_text(json.dumps([r for r,p in options],indent=2))

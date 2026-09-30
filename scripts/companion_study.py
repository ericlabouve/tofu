"""Vary perimeter dog profiles and test explicit companion silhouettes in leftovers.

The companion shapes are fitted cutouts, not a solved complementary tessellation.
Remaining slivers are counted as remainder, never silently assigned as useful food.
"""
from pathlib import Path
import json
import numpy as np
import shapely
from shapely.geometry import Polygon,MultiPoint,Point,box
from shapely.ops import unary_union, linemerge, polygonize
from shapely import affinity
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'design/nine-dog-review'
data=json.loads((OUT/'nine-base.json').read_text());dogs=[Polygon(p) for p in data['dogs']];sheet=box(0,0,120,100);filled=unary_union(dogs)
# Territories assign each new strip of perimeter material to one existing dog.
unique={}
for i,p in enumerate(dogs):
 for d in np.arange(0,p.length,.4):
  q=p.exterior.interpolate(d);unique.setdefault((q.x,q.y),i)
cells=shapely.voronoi_polygons(MultiPoint(list(unique)),extend_to=box(-10,-10,130,110),ordered=True)
owner=list(unique.values())
territories=[unary_union([p for p,j in zip(cells.geoms,owner) if j==i]).intersection(sheet) for i in range(9)]
GROWTH_MM=2.4
band=filled.buffer(GROWTH_MM).intersection(sheet).difference(filled)
varied=[p.union(t.intersection(band)).buffer(0) for p,t in zip(dogs,territories)]
# Numerical detached specks remain remainder rather than being counted as dogs.
varied=[max(p.geoms,key=lambda q:q.area) if p.geom_type=='MultiPolygon' else p for p in varied]
# Remove only sub-0.01 mm² numerical holes from sampled boundary assignment.
assert all(Polygon(r).area<.01 for p in varied for r in p.interiors)
varied=[Polygon(p.exterior) for p in varied]
# Close shallow notches and narrow exposed pockets, then round exposed tips.
# Assign added material using the same dog territories; never round dogs
# independently across shared boundaries.
envelope=unary_union(varied)
rounded=envelope.buffer(1.6,quad_segs=16).buffer(-1.6,quad_segs=16)
rounded=rounded.buffer(-.8,quad_segs=16).buffer(.8,quad_segs=16).intersection(sheet)
added=rounded.difference(envelope)
varied=[p.intersection(rounded).union(t.intersection(added)).buffer(0) for p,t in zip(varied,territories)]
assert all(p.geom_type=='Polygon' and not p.interiors for p in varied)
# Smooth the grown shared network once, retaining frame segments and junctions.
# This avoids smoothing dogs separately, which would create gaps or overlaps.
network=linemerge(unary_union([p.boundary for p in varied]+[sheet.boundary]))
lines=[]
from shapely.geometry import LineString
for line in network.geoms:
    xy=np.array(line.simplify(.25,preserve_topology=True).coords)
    frame=any(np.max(np.abs(xy[:,axis]-value))<1e-7 for axis,value in [(0,0),(0,120),(1,0),(1,100)])
    if not frame:
        for _ in range(3):
            q=.75*xy[:-1]+.25*xy[1:];r=.25*xy[:-1]+.75*xy[1:]
            xy=np.vstack([xy[0],np.stack([q,r],axis=1).reshape(-1,2),xy[-1]])
    lines.append(LineString(xy))
faces=list(polygonize(unary_union(lines)))
varied=[next(q for q in faces if q.covers(p.representative_point())) for p in varied]
assert len({p.wkb for p in varied})==9
# Smooth the whole neck-to-foreleg contour, with a tangent-aligned tail join.
def tail_cubic(a,b,c,d):
    t=np.linspace(0,1,65)[:,None]
    return (1-t)**3*a+3*(1-t)**2*t*np.array(b)+3*(1-t)*t**2*np.array(c)+t**3*d
ring1=np.array(varied[0].exterior.coords[:-1])
low_target=np.array([12.508941436483562,39.929488779877055])
ni=int(np.argmin(np.linalg.norm(ring1-[14.6,27],axis=1)))
li=int(np.argmin(np.linalg.norm(ring1-low_target,axis=1)))
neck=ring1[ni];low=ring1[li]
neck_curve=tail_cubic(neck,(neck[0],33),(12.0,37.8),low)
assert ni<li
varied[0]=Polygon(np.vstack([ring1[:ni],neck_curve,ring1[li+1:]]))
junction=neck_curve[32]
tangent=neck_curve[33]-neck_curve[31];tangent/=np.linalg.norm(tangent)
ring4=np.array(varied[3].exterior.coords[:-1])
left=np.array([0.1665313046552761,39.11239668434098])
i=int(np.argmin(np.linalg.norm(ring4-low,axis=1)));j=int(np.argmin(np.linalg.norm(ring4-left,axis=1)))
curve=np.vstack([tail_cubic(left,(7.8,34.4),junction-1.5*tangent,junction),neck_curve[33:]])
body=np.vstack([ring4[j:],ring4[:i+1]]) if j>i else ring4[j:i+1]
varied[3]=Polygon(np.vstack([body,curve[::-1][1:]]))
# Meet the top frame at 90 degrees instead of leaving a tapered rounded sliver.
ring1=np.array(varied[0].exterior.coords[:-1])
a=int(np.argmin(np.linalg.norm(ring1-[8.934268939643621,0],axis=1)))
b=int(np.argmin(np.linalg.norm(ring1-[4.023291160585603,4.549849162133552],axis=1)))
assert a<b
face_join=np.array([[ring1[b,0],0],ring1[b]])
varied[0]=Polygon(np.vstack([ring1[:a],face_join,ring1[b+1:]]))
# Fill the near-zero-width strip above dog 1's head leading into pocket A.
# A short rounded shoulder starts at the frame, with no long taper along it.
head_ring=np.array(varied[0].exterior.coords[:-1])
hi=int(np.argmin(np.linalg.norm(head_ring-[30.580190638711905,5.130992850402952],axis=1)))
left_top=int(np.argmin(np.linalg.norm(head_ring-[4.023291160585603,0],axis=1)))
assert hi<left_top
shoulder=tail_cubic(np.array([27.0,0]),(29.2,.6),(30.35,2.3),head_ring[hi])
varied[0]=Polygon(np.vstack([head_ring[:hi],shoulder[::-1],head_ring[left_top:]]))
assert all(p.is_valid and p.geom_type=='Polygon' for p in varied)
assert sum(p.area for p in varied)-unary_union(varied).area<.001
# Fill frame-hugging slivers in B, D, H, I, and J into their adjacent dogs.
# Snapshot pockets before filling so each requested letter maps consistently.
pockets=list(sheet.difference(unary_union(varied)).geoms)
def pocket_at(x,y):
    return next(p for p in pockets if p.covers(Point(x,y)))
# A's opposite top strip belongs to the front of dog 2's head.
front2=tail_cubic(np.array([39.2,0]),(38.95,.5),(38.62,1.8),np.array([38.52614899427853,2.9028047117234346]))
patch=Polygon(np.vstack([[44,0],front2,[44,front2[-1,1]]]))
varied[1]=varied[1].union(pocket_at(34,6).intersection(patch)).buffer(0)
# B: repeat dog 1's short shoulder on dog 2's head.
pitch=34.29470676873343
shoulder2=tail_cubic(np.array([27+pitch,0]),(29.2+pitch,.6),(30.35+pitch,2.3),np.array([30.580190638711905+pitch,5.130992850403086]))
patch=Polygon(np.vstack([[43,0],shoulder2,[43,shoulder2[-1,1]]]))
varied[1]=varied[1].union(pocket_at(68,6).intersection(patch)).buffer(0)
# D: square the butt to the left frame below the tail's existing frame entry.
varied[3]=varied[3].union(pocket_at(5,22).intersection(box(0,39.11239668434098,1,100))).buffer(0)
# H and I: extend each left foot to the bottom frame with a short shoulder.
for dog_index,shift in [(7,0),(8,pitch)]:
    foot_shoulder=tail_cubic(np.array([57.8+shift,100]),(58.8+shift,99.5),(59.4+shift,98.2),np.array([59.62725983396286+shift,96.92716611985088]))
    patch=Polygon(np.vstack([[48+shift,100],foot_shoulder,[48+shift,foot_shoulder[-1,1]]]))
    varied[dog_index]=varied[dog_index].union(pocket_at(67+shift,94).intersection(patch)).buffer(0)
# J is only a tiny corner sliver: absorb it entirely into dog 9's right foot.
corner_j=next(p for p in pockets if p.bounds[0]>115 and p.bounds[1]>99)
varied[8]=varied[8].union(corner_j).buffer(0)
if varied[8].geom_type=='MultiPolygon':
    parts=sorted(varied[8].geoms,key=lambda p:p.area,reverse=True)
    assert sum(p.area for p in parts[1:])<1e-12
    varied[8]=parts[0]
assert all(p.is_valid and p.geom_type=='Polygon' for p in varied)
assert sum(p.area for p in varied)-unary_union(varied).area<.001
# Dog 3's tail rises toward the top border instead of curling left.
# Its inside curve gives pocket C a broad opening and narrower rounded base.
ring3=np.array(varied[2].exterior.coords[:-1])
outer_i=int(np.argmin(np.linalg.norm(ring3-[120,11.392409701329692],axis=1)))
base_i=int(np.argmin(np.linalg.norm(ring3-[105.58454108325563,13.216362905760358],axis=1)))
assert outer_i<base_i
inner_tail=tail_cubic(np.array([116,0]),(116,4),(111.5,12.9),ring3[base_i])
varied[2]=Polygon(np.vstack([ring3[:outer_i+1],[[120,0]],inner_tail,ring3[base_i+1:]]))
assert varied[2].is_valid
assert sum(p.area for p in varied)-unary_union(varied).area<.001
# A classic four-lobed dog bone; its shaft is 0.38 in source units.
bone=unary_union([Point(x,y).buffer(.23,quad_segs=12) for x in [-.8,.8] for y in [-.16,.16]]+[box(-.8,-.19,.8,.19)]).simplify(.003)
body=affinity.scale(Point(-.15,0).buffer(1,quad_segs=16),.85,.4)
fish=body.union(Polygon([(.45,0),(1,.5),(.84,0),(1,-.5)])).buffer(0).simplify(.003)

# Additional single-piece outlines. No separate toe pads, eyes, or tag holes.
paw=unary_union([affinity.scale(Point(0,.2).buffer(1,quad_segs=16),.65,.5)]+[Point(x,y).buffer(.255,quad_segs=12) for x,y in [(-.59,-.14),(-.25,-.48),(.25,-.48),(.59,-.14)]]).buffer(.055).buffer(-.055)
ball=Point(0,0).buffer(1,quad_segs=32)
house=Polygon([(-1,.8),(-1,-.1),(-1.15,-.1),(0,-1.1),(1.15,-.1),(1,-.1),(1,.8),(.32,.8),(.32,.32),(.26,.1),(0,0),(-.26,.1),(-.32,.32),(-.32,.8)]).buffer(-.06).buffer(.06)
hydrant=unary_union([box(-.4,-.55,.4,.7),Point(0,-.55).buffer(.4,quad_segs=16),box(-.72,-.35,.72,-.04),box(-.62,.61,.62,.85)]).buffer(.055).buffer(-.055)
bowl=Polygon([(-1,-.4),(1,-.4),(.72,.4),(-.72,.4)]).buffer(-.08).buffer(.08)
TEMPLATES={'bones':('bone',bone),'fish':('fish',fish),'paws':('paw',paw),'balls':('ball',ball),'houses':('house',house),'hydrants':('hydrant',hydrant),'bowls':('bowl',bowl)}
assert all(p.is_valid and p.geom_type=='Polygon' for _,p in TEMPLATES.values())
import hashlib
cache_path=OUT/'fit-cache.json'
cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
def fit(template,region):
    """Vectorized, deterministic position/angle grid with uniform-scale bisection."""
    key=hashlib.sha256(b'v2-grid-1.15-'+template.wkb+region.wkb).hexdigest()
    if key in cache:
        v=cache[key];return v[0],Polygon(v[1]),v[2],v[3]
    a,b,c,d=region.bounds
    points=np.array([(x,y) for x in np.arange(a+.35,c,1.15) for y in np.arange(b+.35,d,1.15)]+[tuple(region.representative_point().coords)[0]])
    shapely.prepare(region)
    points=points[shapely.covers(region,shapely.points(points))]
    best=None
    for angle in [0,15,30,60,75,90,105,120,150,165]:
        coords=np.array(affinity.rotate(template,angle,origin=(0,0)).exterior.coords)
        lo=np.zeros(len(points));hi=np.full(len(points),min(45,np.sqrt(region.area/template.area)*1.05))
        for _ in range(11):
            scale=(lo+hi)/2
            candidates=shapely.polygons(coords[None,:,:]*scale[:,None,None]+points[:,None,:])
            inside=shapely.covers(region,candidates)
            lo=np.where(inside,scale,lo);hi=np.where(inside,hi,scale)
        i=int(np.argmax(lo));area=lo[i]**2*template.area
        if best is None or area>best[0]:best=(area,Polygon(coords*lo[i]+points[i]),float(lo[i]),angle)
    cache[key]=[best[0],list(best[1].exterior.coords),best[2],best[3]]
    cache_path.write_text(json.dumps(cache))
    return best

def fit_companions(dog_polys,template,kind):
    remaining=sheet.difference(unary_union(dog_polys))
    fitted=[]
    for region in getattr(remaining,'geoms',[remaining]):
        if region.area<120:continue
        area,shape,scale,angle=fit(template,region)
        if area>=120 and (kind!='bone' or scale*.38>=4):fitted.append(shape)
    return fitted

def record(key,title,dog_polys,companions=(),kind=None):
    union=unary_union(dog_polys+list(companions));remainder=sheet.difference(union)
    assert all(p.is_valid and p.geom_type=='Polygon' and len(p.interiors)==0 and sheet.buffer(.00001).covers(p) for p in dog_polys+list(companions))
    assert abs(sum(p.area for p in dog_polys+list(companions))-union.area)<.01
    pieces=[]
    for category,ps in [('dog',dog_polys),(kind,list(companions)),('remainder',[p for p in getattr(remainder,'geoms',[remainder]) if p.area>1e-7])]:
        for i,p in enumerate(ps):
            pieces.append(dict(category=category,profile_id=i+1 if category=='dog' else None,label_point=list(p.representative_point().coords)[0],points=np.array(p.exterior.coords).tolist(),holes=[np.array(r.coords).tolist() for r in p.interiors],area_mm2=round(p.area,2)))
    serialized=[Polygon(s['points'],s['holes']) for s in pieces]
    assert all(p.is_valid for p in serialized)
    serialized_union=unary_union(serialized)
    assert sheet.difference(serialized_union).area<.01
    assert abs(sum(p.area for p in serialized)-serialized_union.area)<.01
    dog_area=sum(p.area for p in dog_polys);comp_area=sum(p.area for p in companions)
    return dict(id=key,title=title,dogs=len(dog_polys),companions=len(companions),companion_kind=kind,dog_area_percent=round(dog_area/120,1),companion_area_percent=round(comp_area/120,1),remainder_percent=round(remainder.area/120,1),dog_dimensions_mm=[[round(p.bounds[2]-p.bounds[0],1),round(p.bounds[3]-p.bounds[1],1)] for p in dog_polys],pieces=pieces)

old=json.loads((ROOT/'design/profile-review/profiles.json').read_text())[0]
approved=[Polygon(p['points']) for p in old['pieces'] if p['complete']]
options=[]
for layout,title,polys in [('a6','A · original six',approved),('a9','A · nine dogs, 3 × 3',dogs),('varied','Nine dogs · varied perimeter',varied)]:
    options.append(record(layout,title,polys));options[-1].update(layout=layout,companion_selection='none')
    for choice,(kind,template) in TEMPLATES.items():
        fitted=fit_companions(polys,template,kind)
        key=choice if layout=='varied' else layout+'_'+choice
        options.append(record(key,title+' + '+choice,polys,fitted,kind))
        options[-1].update(layout=layout,companion_selection=choice)
        print(key,len(fitted),'companions,',options[-1]['remainder_percent'],'% remainder',flush=True)
# Local D study: extend dog 1's exposed muzzle left, then fill the tall
# pocket with a sideways bowl (broad rim at the sheet's left edge).
bowl_d_dogs=list(varied)
coords=np.array(varied[0].exterior.coords)
for xy in coords:
    x,y=xy
    if x<15 and y<15:
        weight=(max(0,1-(x/15)**2))**2 * (max(0,1-(y/15)**2))**2
        xy[0]=max(0,x-5.1*weight)
bowl_d_dogs[0]=Polygon(coords).buffer(0)
assert bowl_d_dogs[0].geom_type=='Polygon'
remaining_d=sheet.difference(unary_union(bowl_d_dogs))
pocket_d=next(p for p in getattr(remaining_d,'geoms',[remaining_d]) if p.covers(Point(5,22)))
# Flared rim and continuously curved bowl sides, shared with the dogs.
# Cubic handles give the chin a rounded turn into the foreleg rather than
# leaving a separate crescent-shaped scrap above a straight bowl wall.
def cubic(a,b,c,d):
    t=np.linspace(0,1,65)[:,None]
    return (1-t)**3*np.array(a)+3*(1-t)**2*t*np.array(b)+3*(1-t)*t**2*np.array(c)+t**3*np.array(d)
# Reflect the approved upper flare across y=23.5 to form the lower lip.
# The two sides are exact reflections, including their transition into the base.
center_y=23.5
upper1=cubic((0,8),(3.8,8.7),(3.5,11.7),(8.2,12.1))
upper2=cubic((8.2,12.1),(12.9,12.5),(14.4,13.0),(14.4,17))
upper=np.vstack([upper1,upper2[1:]])
lower=upper[::-1].copy();lower[:,1]=2*center_y-lower[:,1]
bowl_d=Polygon(np.vstack([upper,lower]))
assert bowl_d.symmetric_difference(affinity.scale(bowl_d,xfact=1,yfact=-1,origin=(0,center_y))).area<1e-8
# Absorb old slivers and give each dog the same shared bowl boundary.
addition=pocket_d.difference(bowl_d)
split_y=32.99572866699986
bowl_d_dogs[0]=bowl_d_dogs[0].union(addition.intersection(box(0,0,120,split_y))).difference(bowl_d).buffer(0)
bowl_d_dogs[3]=bowl_d_dogs[3].union(addition.intersection(box(0,split_y,120,100))).difference(bowl_d).buffer(0)
# A small relief separates the lower muzzle from the unchanged bowl flare.
# The front turns gently from the frame into the jaw, then rounds into the neck.
jaw1=cubic((0,6),(0,7),(4,9.5),(7,10))
jaw2=cubic((7,10),(10,10.5),(14.4,12),(14.4,17))
jaw=np.vstack([jaw1,jaw2[1:]])
jaw_relief=Polygon(np.vstack([jaw,upper[::-1][1:]])).buffer(0).difference(bowl_d)
assert jaw_relief.is_valid and jaw_relief.intersection(bowl_d).area<1e-8
bowl_d_dogs[0]=bowl_d_dogs[0].difference(jaw_relief).buffer(0)
if bowl_d_dogs[0].geom_type=='MultiPolygon':
    parts=sorted(bowl_d_dogs[0].geoms,key=lambda p:p.area,reverse=True)
    assert sum(p.area for p in parts[1:])<.001
    bowl_d_dogs[0]=parts[0]
options.append(record('varied_bowl_d','Nine dogs · bowl D + longer muzzle 1',bowl_d_dogs,[bowl_d],'bowl'))
options[-1].update(layout='varied',companion_selection='bowl_d')
for piece in options[-1]['pieces']:
    if piece['category']=='bowl':piece['feedback_id']='D'
(OUT/'options.json').write_text(json.dumps(options,indent=2))
(OUT/'theme-templates.json').write_text(json.dumps({name:dict(kind=kind,points=list(p.exterior.coords)) for name,(kind,p) in TEMPLATES.items()},indent=2))
# Comparison: the preferred reference, nine dogs, and the mixed-shape study.
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
COLORS={'dog':['#e2b984','#c99b64','#edc99a'],'bone':['#86afa0'],'fish':['#7fabc1'],'paw':['#ae99ba'],'ball':['#dca568'],'house':['#c28d7e'],'hydrant':['#bd7c76'],'bowl':['#94aabc'],'remainder':['#e4dfd7']}
def draw(ax,o):
    for i,s in enumerate(o['pieces']):
        p=Polygon(s['points'],s['holes']);verts=[];codes=[]
        # Orient hole rings opposite to exteriors for correct nonzero filling.
        from shapely.geometry.polygon import orient
        p=orient(p,sign=1)
        for ring in [p.exterior]+list(p.interiors):
            coords=list(ring.coords);verts.extend(coords);codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(coords)-2)+[MPath.CLOSEPOLY])
        color=COLORS[s['category']][i%len(COLORS[s['category']])]
        ax.add_patch(PathPatch(MPath(verts,codes),facecolor=color,edgecolor='#645641',lw=.6))
    ax.set_xlim(-1,121);ax.set_ylim(101,-1);ax.set_aspect('equal');ax.axis('off');ax.set_title(o['title'],loc='left',fontsize=13,pad=12)
    ax.text(0,-.12,f"{o['dog_area_percent']}% dogs · {o['companion_area_percent']}% companions\n{o['remainder_percent']}% remaining",transform=ax.transAxes,fontsize=10,linespacing=1.5)
fig,axs=plt.subplots(1,3,figsize=(16,6.5),facecolor='#fffdf8')
for ax,o in zip(axs,[next(o for o in options if o['id']==key) for key in ['a6_bones','a9_bones','bones']]):draw(ax,o)
fig.suptitle('SMOOTHER PROFILES / BONES IN EVERY LAYOUT',x=.04,ha='left',fontsize=21)
fig.text(.04,.89,'All sheets 120 × 100 mm · tan = dogs · green = bone candidates · gray = remainder',fontsize=12,color='#716859')
fig.subplots_adjust(top=.79,bottom=.21,left=.04,right=.97,wspace=.13)
fig.savefig(OUT/'comparison.png',dpi=160);fig.savefig(OUT/'comparison.svg')
fig,axs=plt.subplots(1,2,figsize=(12,6.2),facecolor='#fffdf8')
for ax,o in zip(axs,[next(o for o in options if o['id']==key) for key in ['a6_bones','a6_paws']]):draw(ax,o)
fig.subplots_adjust(top=.9,bottom=.18,wspace=.2);fig.savefig(OUT/'companions.png',dpi=160)

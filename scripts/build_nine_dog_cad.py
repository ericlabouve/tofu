"""Build the selected original a9 layout as a parametric CadQuery cutter (mm).
Run with .venv/bin/python scripts/build_nine_dog_cad.py.
"""
from pathlib import Path
import json,time
import numpy as np
import cadquery as cq
from shapely.geometry import Polygon,Point
from shapely.geometry.polygon import orient
from shapely.ops import nearest_points
import trimesh
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cad/nine-dogs-3x3';OUT.mkdir(exist_ok=True,parents=True)
SOURCE=ROOT/'design/nine-dog-review/options.json'
frozen=OUT/'layout.json'
layout=json.loads(frozen.read_text()) if frozen.exists() else next(o for o in json.loads(SOURCE.read_text()) if o['id']=='a9' and o['companion_selection']=='none')
assert layout['id']=='a9' and layout['dogs']==9 and layout['companions']==0
# Freeze the chosen layout alongside the editable CAD source parameters.
(OUT/'layout.json').write_text(json.dumps(layout,indent=2))
W,H=120.,100.
EDGE=.30;WALL=1.6;BEVEL=4.;BLADE_HEIGHT=30.;PAD_Z=28.;HEIGHT=36.
SAMPLE_STEP=.35
start=time.time()
def paired_wires(lo,hi,region):
    """Same point count, orientation, seam anchor and periodic parameters."""
    lo=orient(lo,sign=1);hi=orient(hi,sign=1)
    n=max(64,int(np.ceil(lo.exterior.length/SAMPLE_STEP)))
    anchor=Point(lo.exterior.coords[0])
    result=[]
    for z in np.linspace(0,BEVEL,9):
        offset=region.buffer(-(EDGE/2+(WALL-EDGE)/2*z/BEVEL),quad_segs=12)
        polys=list(getattr(offset,'geoms',[offset]))
        poly=orient(next(q for q in polys if q.covers(hi.representative_point())),sign=1)
        ring=poly.exterior;start=ring.project(anchor)
        points=[ring.interpolate((start+k*ring.length/n)%ring.length) for k in range(n)]
        vec=[cq.Vector(q.x-W/2,H/2-q.y,z) for q in points]
        edge=cq.Edge.makeSpline(vec,periodic=True,parameters=list(range(n+1)))
        result.append(cq.Wire.assembleEdges([edge]))
    return result
# The outer rim bevel points outward, keeping the nominal 120 x 100 layout.
rim=(cq.Workplane('XY').rect(W+2*EDGE,H+2*EDGE)
 .workplane(offset=BEVEL).rect(W+2*WALL,H+2*WALL).loft()
 .union(cq.Workplane('XY').workplane(offset=BEVEL).rect(W+2*WALL,H+2*WALL).extrude(BLADE_HEIGHT-BEVEL)))
cutters=[];apertures=[]
for i,piece in enumerate(layout['pieces']):
    region=Polygon(piece['points'],piece['holes'])
    low=region.buffer(-EDGE/2,quad_segs=12)
    high=region.buffer(-WALL/2,quad_segs=12)
    lows=list(getattr(low,'geoms',[low]));highs=list(getattr(high,'geoms',[high]))
    if any(q.is_empty for q in lows+highs):raise ValueError(f'Collapsed aperture {i}')
    if len(lows)!=len(highs):raise ValueError(f'Aperture topology changes through bevel {i}')
    for branch,hi in enumerate(highs):
        lo=next(q for q in lows if q.covers(hi.representative_point()))
        sections=paired_wires(lo,hi,region);low_wire,hi_wire=sections[0],sections[-1]
        bevel=cq.Solid.makeLoft(sections,ruled=True)
        stem=cq.Solid.extrudeLinear(hi_wire,[],cq.Vector(0,0,HEIGHT+2-BEVEL))
        below=cq.Solid.extrudeLinear(low_wire,[],cq.Vector(0,0,-1))
        cutter=bevel.fuse(stem,below)
        assert cutter.isValid(),f'Invalid aperture cutter {i}'
        cutters.append(cutter)
        apertures.append(dict(index=i+1,branch=branch,category=piece['category'],source_area_mm2=region.area,body_open_area_mm2=hi.area))
    print(f'Aperture {i+1}/{len(layout["pieces"])} ready',flush=True)
print('Cutting the integrated blade grid...',flush=True)
grid=rim.val().cut(*cutters).clean()
assert grid.isValid(), 'Invalid grid BRep'
print('Grid solids:',len(grid.Solids()),flush=True)
# Wide rounded collar and oval side pads stay above the 25 mm tofu sheet.
collar=(cq.Workplane('XY').workplane(offset=PAD_Z).sketch().rect(136,116).vertices().fillet(8).finalize().extrude(HEIGHT-PAD_Z))
for x in [-70,70]:
    collar=collar.union(cq.Workplane('XY').workplane(offset=PAD_Z).center(x,0).ellipse(16,34).extrude(HEIGHT-PAD_Z))
collar=collar.cut(cq.Workplane('XY').rect(W,H).extrude(HEIGHT+2)).edges('>Z').fillet(2)
model=grid.fuse(collar.val()).clean()
assert model.isValid(), 'Invalid complete BRep'
assert len(model.Solids())==1, 'Cutter must be one connected solid'
print('Exporting STEP and STL...',flush=True)
cq.exporters.export(model,str(OUT/'nine-dogs-3x3.step'))
model.exportStl(str(OUT/'nine-dogs-3x3.stl'),tolerance=.035,angularTolerance=.12,relative=False)
mesh=trimesh.load(OUT/'nine-dogs-3x3.stl',force='mesh')
# OCC may emit zero-area triangles along coincident tessellation seams.
removed_degenerate=int((~mesh.nondegenerate_faces()).sum())
mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0
mesh.export(OUT/'nine-dogs-3x3.stl')
assert len(mesh.split())==1
bbox=model.BoundingBox()
report=dict(layout_id='a9',dogs=9,negative_space_apertures=len(apertures)-9,nominal_layout_mm=[W,H],blade_height_mm=BLADE_HEIGHT,overall_height_mm=HEIGHT,pad_underside_mm=PAD_Z,wall_mm=WALL,edge_land_mm=EDGE,bevel_height_mm=BEVEL,top_grip_fillet_mm=2,overall_size_mm=mesh.extents.tolist(),valid_brep=model.isValid(),solids=len(model.Solids()),watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),mesh_components=1,volume_mm3=float(mesh.volume),triangles=len(mesh.faces),cadquery_version=cq.__version__,removed_degenerate_triangles=removed_degenerate,apertures=apertures)
(OUT/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='apertures'},indent=2),flush=True)

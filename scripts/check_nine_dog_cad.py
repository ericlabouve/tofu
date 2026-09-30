"""Independent checks on the exported solid and mesh; records cross-section fidelity."""
from pathlib import Path
import json
import cadquery as cq
import trimesh
import numpy as np
from shapely.geometry import Polygon
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'cad/nine-dogs-3x3'
layout=json.loads((OUT/'layout.json').read_text())
solid=cq.importers.importStep(str(OUT/'nine-dogs-3x3.step')).val()
assert solid.isValid() and len(solid.Solids())==1
m=trimesh.load(OUT/'nine-dogs-3x3.stl',force='mesh')
assert m.is_watertight and m.is_winding_consistent and m.volume>0
components=m.split();assert len(components)==1
checks=[]
for z,inset in [(0.02,.15+.65*.02/4),(1.25,.15+.65*1.25/4),(2,.475),(2.75,.15+.65*2.75/4),(10,.8),(26,.8)]:
 section=m.section([0,0,1],[0,0,z]);rings=[Polygon([(p[0]+60,50-p[1]) for p in ring]) for ring in section.discrete]
 rings=sorted(rings,key=lambda p:p.area,reverse=True)[1:]
 expected=[]
 for p in layout['pieces']:
  q=Polygon(p['points'],p['holes']).buffer(-inset,quad_segs=12)
  expected.extend(getattr(q,'geoms',[q]))
 assert len(rings)==len(expected),(z,len(rings),len(expected))
 errors=[]
 for q in expected:
  r=min(rings,key=lambda r:q.centroid.distance(r.centroid))
  errors.append(q.hausdorff_distance(r))
 checks.append(dict(z_mm=z,openings=len(rings),max_contour_error_mm=max(errors)))
 print(checks[-1],flush=True)
 assert max(errors)<.25, 'Contour deviates too far from selected layout'
b=solid.BoundingBox()
report=dict(layout_id='a9',dogs=9,through_openings=checks[0]['openings'],nominal_layout_mm=[120,100],blade_height_mm=30,overall_height_mm=36,pad_underside_mm=28,wall_mm=1.6,edge_land_mm=.30,bevel_height_mm=4,top_grip_fillet_mm=2,overall_size_mm=m.extents.tolist(),valid_brep=True,solids=1,watertight=True,winding_consistent=True,mesh_components=1,volume_mm3=float(m.volume),triangles=len(m.faces),cadquery_version=cq.__version__,cross_sections=checks)
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print('All exported CAD checks passed.')

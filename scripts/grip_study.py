"""CadQuery frame study, independent of the pending dog layout. Millimetres."""
from pathlib import Path
import json
import cadquery as cq
import trimesh
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'design/review'
OPEN_X,OPEN_Y=120,100
EDGE=.30
BEVEL_HEIGHT=4
BLADE_WALL=1.6
PRESS_UNDERSIDE=28
HEIGHT=36
# Outer cutting rim: single bevel, internal opening constant through its height.
bevel=(cq.Workplane('XY').rect(OPEN_X+2*EDGE,OPEN_Y+2*EDGE)
        .workplane(offset=BEVEL_HEIGHT).rect(OPEN_X+2*BLADE_WALL,OPEN_Y+2*BLADE_WALL).loft())
wall=(cq.Workplane('XY').workplane(offset=BEVEL_HEIGHT)
      .rect(OPEN_X+2*BLADE_WALL,OPEN_Y+2*BLADE_WALL).extrude(PRESS_UNDERSIDE-BEVEL_HEIGHT+2))
blank=bevel.union(wall)
# Rounded collar and broad palm pads, supported outside the tofu footprint.
collar=(cq.Workplane('XY').workplane(offset=PRESS_UNDERSIDE).sketch()
        .rect(136,116).vertices().fillet(8).finalize().extrude(HEIGHT-PRESS_UNDERSIDE))
for x in [-70,70]:
    pad=cq.Workplane('XY').workplane(offset=PRESS_UNDERSIDE).center(x,0).ellipse(16,34).extrude(HEIGHT-PRESS_UNDERSIDE)
    collar=collar.union(pad)
opening=cq.Workplane('XY').rect(OPEN_X,OPEN_Y).extrude(HEIGHT+2)
collar=collar.cut(opening)
collar=collar.edges('>Z').fillet(2)
model=blank.union(collar).cut(opening).clean()
assert model.val().isValid() and len(model.solids().vals())==1
cq.exporters.export(model,str(OUT/'grip-study.step'))
# Mesh is a frame-only study, named explicitly so it is not mistaken for a finished cutter.
cq.exporters.export(model,str(OUT/'frame-only-study.stl'),tolerance=.08,angularTolerance=.12)
m=trimesh.load(OUT/'frame-only-study.stl');assert m.is_watertight
# VTK depth-buffered rendering avoids painter-order artifacts on long thin walls.
import vtk
reader=vtk.vtkSTLReader();reader.SetFileName(str(OUT/'frame-only-study.stl'));reader.Update()
normals=vtk.vtkPolyDataNormals();normals.SetInputConnection(reader.GetOutputPort());normals.SetFeatureAngle(45);normals.Update()
mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort())
actor=vtk.vtkActor();actor.SetMapper(mapper);actor.GetProperty().SetColor(.29,.53,.44);actor.GetProperty().SetInterpolationToPhong();actor.GetProperty().SetSpecular(.25);actor.GetProperty().SetSpecularPower(30)
renderer=vtk.vtkRenderer();renderer.AddActor(actor);renderer.SetBackground(1,.992,.976)
window=vtk.vtkRenderWindow();window.SetOffScreenRendering(1);window.AddRenderer(renderer);window.SetSize(1400,900);window.SetMultiSamples(8)
camera=renderer.GetActiveCamera();camera.SetPosition(190,-240,210);camera.SetFocalPoint(0,0,16);camera.SetViewUp(0,0,1);camera.ParallelProjectionOn();camera.SetParallelScale(94)
renderer.ResetCameraClippingRange();window.Render()
shot=vtk.vtkWindowToImageFilter();shot.SetInput(window);shot.Update()
writer=vtk.vtkPNGWriter();writer.SetFileName(str(OUT/'frame-render.png'));writer.SetInputConnection(shot.GetOutputPort());writer.Write();window.Finalize()
fig,ax=plt.subplots(figsize=(11,8),facecolor='#fffdf9');ax.imshow(plt.imread(OUT/'frame-render.png'));ax.axis('off')
fig.text(.07,.92,'GRIP + CUTTING RIM / CADQUERY STUDY',fontsize=20,color='#302b26')
fig.text(.07,.865,'120 × 100 mm opening · 28 mm clearance below palm pads · 36 mm overall height',fontsize=11,color='#756d64')
fig.text(.07,.08,'Frame only — dog blades and their upper supports follow layout selection.\n0.30 mm nominal edge land is a prototype parameter, not a validated knife edge.',fontsize=11,color='#756d64',linespacing=1.6)
fig.savefig(OUT/'grip-study.png',dpi=160)
(OUT/'grip-study.json').write_text(json.dumps(dict(cadquery_version=cq.__version__,opening_mm=[120,100],pad_underside_mm=28,overall_height_mm=36,edge_land_mm=EDGE,bevel_height_mm=BEVEL_HEIGHT,blade_wall_mm=BLADE_WALL,valid=model.val().isValid(),solids=len(model.solids().vals()),mesh_watertight=bool(m.is_watertight),bounds_mm=m.bounds.tolist()),indent=2))
print('Valid single solid; watertight export; frame study exported.')

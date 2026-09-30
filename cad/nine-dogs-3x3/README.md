# Nine dogs / 3 × 3 — CadQuery prototype

This is the selected **A · nine dogs / 3 × 3** layout (`a9`, companions `none`), not the later varied-profile design. The source outline is frozen in [layout.json](layout.json).

- Generated `nine-dogs-3x3.step` — editable CAD exchange model, millimetres.
- Generated `nine-dogs-3x3.stl` — prototype mesh, millimetres.
- [Interactive preview and renders](index.html).
- [Parametric CadQuery source](../../scripts/build_nine_dog_cad.py).
- [Independent validation](validation.json).

## Construction

The original nine profile regions and perimeter offcuts define through-openings in one continuous cutting grid. Nominal layout is 120 × 100 mm. Each opening is inset by half the blade thickness, so finite blades slightly reduce the cutout size. The thin perimeter areas can merge into the outer wall; the original nine dogs remain intact. One narrow offcut passage separates into two openings at finite wall thickness.

Internal blades are 1.6 mm thick above a 4 mm sharpening band, tapering toward a 0.30 mm prototype cutting land. Height from cutting edge to blade top is 30 mm. The frame rises to 36 mm; its palm-pad underside is at 28 mm, giving 3 mm nominal clearance over a 25 mm tofu sheet. The two oval pads are 32 × 68 mm before blending into the collar, and their upper edges use a 2 mm radius. Overall footprint is approximately 172 × 116 mm.

The contour splines are sampled from the selected layout. Multiple offset sections control the bevel and preserve shape through its height. Numerical contour fidelity is measured on exported mesh sections, including intermediate bevel elevations. The final export is one valid CAD solid and one watertight, consistently wound mesh. Six checked elevations retain 19 openings (nine dogs plus ten perimeter offcut openings); maximum measured contour deviation is 0.128 mm. Actual mesh bounds are 172 × 116 × 36 mm. Exact dimensions and checks are in the validation report.

## Build and check

Generated STEP/STL files and `preview.bin` are intentionally excluded from Git.
On a fresh clone, create the environment and install the recorded dependencies:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
```

Then run from the repository root:

```sh
.venv/bin/python scripts/build_nine_dog_cad.py
.venv/bin/python scripts/check_nine_dog_cad.py
.venv/bin/python scripts/render_nine_dog_cad.py
```

The render script uses Numba, NumPy, Trimesh, and Pillow for a CPU depth-buffer preview. No external web libraries are needed for the interactive viewer. Serve the repository and open `cad/nine-dogs-3x3/index.html`.

This is the positive cutter prototype. Physical cutting force, release, edge durability, print support strategy, and material/casting choices remain to be tested before creating the negative casting mold. The 0.30 mm land is a printable prototype parameter, not a validated cast-resin knife specification.

## Mouse measurement

Select **Measure · drag ruler**, then drag between two points. **3D model surfaces** reads the visible mesh surface at each endpoint and reports their straight-line distance in millimetres, plus absolute X/Y/Z differences. Measurements remain attached to those coordinates when the view changes. Rotate to expose hidden points before measuring.

Use **View plane (including gaps)** for arbitrary positions that do not lie on the solid. This measures in the plane parallel to the screen; choose Top for XY plan dimensions. It is a projected distance, not surface distance along a curved blade. Clear with the button or Escape. Zoom remains available for more precise placement.

Surface picking uses a floating-point GPU framebuffer; browsers without that capability offer view-plane measurement only. Endpoint precision depends on cursor placement and the preview mesh. Numeric projection checks: `node scripts/check_measurement_math.mjs`. Live mouse verification was unavailable in this session because Computer Use denied Chrome access.

## Local exploration artifacts

The fitting cache and unused intermediate `before-*` snapshots are excluded from
Git. Existing local copies are preserved. The two `before-options.json` baselines
used by the smoothing/refinement checks remain tracked, along with review pages,
comparison images, input layouts, source references, and the original prototype.

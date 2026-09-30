# Working on the tofu cutter

## Start here

Read `README.md`, `PROJECT_PREFERENCES.md`, and `cad/nine-dogs-3x3/README.md`.
This file records lessons from the design and CAD work through September 30, 2026.
New explicit user instructions take precedence over these notes.

**The selected design is “nine dogs / 3 × 3”, layout ID `a9`, with companion
shapes set to `none`.** It is the repeated-profile layout, NOT “Nine varied
profiles”. The user rejected the other layouts for the current CAD work.
Earlier requests about bowls, dog houses, and individually reshaping dogs belong
to archived explorations; do not silently reintroduce them. Some older prose in
the project documents still describes those explorations.

## Product constraints and visual lessons

- Adults operate the cutter; children eat the playful tofu shapes.
- Firm tofu, nominal rectangular cutting layout **120 × 100 mm**. The adult
  halves a roughly 50 mm block into **25 mm thick sheets**, then presses once.
  Do not require trimming the tofu to a special outline first.
- Preserve recognizable side-profile dogs. Judge plain silhouettes without
  eyes or ear artwork; decorative marks cannot rescue an unreadable cutout.
- Shared cutting boundaries and useful portions matter. Small slivers and
  incomplete feet/heads count as waste. Interior tessellation does not imply
  zero perimeter waste. Do not claim the current design is waste-free.
- Smooth the outline in plan view, especially tail/leg/back connections. This
  is separate from keeping a sharp cutting edge in the vertical cross-section.
- Grips need broad, comfortable adult pressing surfaces outside the food area.
- Bambu printing is for prototyping. Food-contact material, resin, molding,
  cutting force, release, and edge durability are not validated. The current
  model is the positive cutter, not a negative casting mold.

## Source of truth and file map

- `cad/nine-dogs-3x3/layout.json`: frozen selected 2D layout. Preserve it when
  changing CAD construction; do not substitute the mutable exploration data.
- `scripts/build_nine_dog_cad.py`: CadQuery model and parameters.
- `scripts/check_nine_dog_cad.py`: independent checks of exported STEP/STL.
- `scripts/render_nine_dog_cad.py`: CPU renders and interactive preview mesh.
- `cad/nine-dogs-3x3/index.html`, `viewer.js`, `measurement-math.js`: 3D viewer.
- `cad/nine-dogs-3x3/validation.json`: results from the last validation run,
  not proof that subsequent edits have passed.
- `design/` and the other scripts: archived 2D exploration and review tools.
  Preserve them unless cleanup is requested. `scripts/build_nine_dog_review.py`
  generates the older 2D page; edit its generator when changing that page.
- `inspiration/` (singular): nine reference images, all previously reviewed;
  findings are in `design/INSPIRATION_REVIEW.md`.
- `big_dogs_rect_13x11.stl` and `big_dog_render.png`: original inputs. The STL
  audit measured roughly 101.4 × 84.1 mm internally; the redesign target remains
  the user's stated 120 × 100 mm.

## Build and validation

Use the repository's `.venv` if present. For a fresh checkout:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
```

Run from the repository root, in order, after geometry changes:

```sh
.venv/bin/python scripts/build_nine_dog_cad.py
.venv/bin/python scripts/check_nine_dog_cad.py
.venv/bin/python scripts/render_nine_dog_cad.py
```

Rendering uses NumPy, Trimesh, Numba, and Pillow. VTK offscreen rendering crashed
in the development environment; the CPU renderer avoids that dependency on a
working display. If cache permissions fail, point `MPLCONFIGDIR` and
`NUMBA_CACHE_DIR` at writable temporary directories.

Inspect all four regenerated views: perspective, underside/cutting edges, top,
and side. Keep the four images displayed in the root README synchronized with
the model. A successful export alone is insufficient.

Current prototype parameters (not immutable requirements):

| Parameter | Millimetres |
| --- | ---: |
| Blade height | 30 |
| Blade body thickness | 1.6 |
| Cutting land | 0.30 |
| Bevel height | 4 |
| Grip underside above cutting plane | 28 |
| Overall height | 36 |
| Upper grip fillet radius | 2 |
| Overall footprint | approximately 172 × 116 |

### Geometry lessons

- Two-section spline lofts distorted intermediate bevel contours by roughly
  1.8 mm despite plausible end profiles. The current construction uses **nine
  offset sections** through the 4 mm bevel, with ruled lofts. Check intermediate
  heights whenever changing this construction.
- Corresponding periodic spline wires need matching point counts, orientation,
  seam anchors, and parameterization. Offsetting narrow regions can split them
  into multiple polygons; do not assume one offset produces one wire.
- Finite blade thickness reduces openings compared with the nominal flat
  layout. One narrow remainder splits: current model has **19 through-openings**
  (nine dogs and ten offcut openings). Do not force the count to nine.
- Require one valid CAD solid, one connected watertight mesh, consistent winding,
  and positive volume. Check contour fidelity at multiple bevel and body heights.
  The current checker uses six heights and a maximum error threshold of 0.25 mm;
  the recorded baseline achieved under 0.128 mm. Revisit expectations explicitly
  if the geometry intentionally changes; do not loosen checks just to pass.
- NURBS bounding boxes can overestimate physical extents. The validation report
  uses exported mesh extents for the reported overall dimensions.
- CAD settings also appear in the checker/report. Keep them consistent when
  changing parameters; avoid publishing stale hard-coded dimensions.

## Viewer and measurement

Serve the repository root, for example with `python3 -m http.server 8765
--bind 127.0.0.1` (one shell command). Open
`http://127.0.0.1:8765/cad/nine-dogs-3x3/index.html`.
Check whether the port already serves this repository before starting a server;
do not terminate an unrelated process. A fresh clone needs generated
`preview.bin` before the interactive model works. Static PNGs remain available.

The viewer uses local ES modules and WebGL2, with no CDN dependencies:

- **3D model surfaces** uses a floating-point GPU picking framebuffer and reports
  Euclidean distance between visible surface points. Gaps must not fabricate hits.
- **View plane** measures projected distances, including gaps; use Top for XY
  dimensions. This is not a distance along a curved surface.
- Stored endpoints are world coordinates and must stay attached when rotating,
  changing views, or zooming. Escape/Clear removes the ruler.
- Preserve the explicit fallback to view-plane mode when float picking is absent.

For viewer changes:

```sh
node scripts/check_measurement_math.mjs
node --input-type=module --check < cad/nine-dogs-3x3/viewer.js
node --input-type=module --check < cad/nine-dogs-3x3/measurement-math.js
```

The repository does not declare Node's module type, so plain `node --check` on
these `.js` modules can misidentify them as CommonJS. Math checks do not establish
GPU picking or mouse usability. Test in a browser when available and distinguish
that from automated math checks. Prior Chrome access was denied; do not describe
that session as browser-verified.

## Git and generated assets

**The user explicitly does not want Git LFS.** Track source, frozen inputs,
documentation, small review assets, and the four CAD PNGs. Respect `.gitignore`:

- Generated current STEP/STL and `preview.bin` stay local and are rebuilt.
- The fit cache and selected unused intermediate snapshots stay local.
- Keep the `before-options.json` baselines consumed by the smoothing and varied
  refinement checks; they are not interchangeable with unused snapshots.
- Preserve the original input STL; do not globally ignore every `*.stl`.
- Do not track `.DS_Store`, environments, or caches.

A previous `git add .` included a ~159 MiB STL and ~76 MiB preview mesh, causing
GitHub to reject the push. Stage deliberate paths, inspect staged sizes and
`git diff --cached --check`, and never force-add ignored generated exports.
Adding an ignore rule does not remove an already committed blob. If an unpushed
commit needs repair, retain a backup, preserve working files, and amend only the
intended commit. Do not push backup branches containing the oversized blobs or
use `git push --all`. Do not rewrite published history without authorization.

A one-time cleanup script was written to `/tmp/fix-tofu-commit.py`; it is pinned
to an old commit and is not a reusable project tool or dependency. Temporary files
may disappear. Reinspect current Git state instead of assuming that script applies.

Some sessions cannot write `.git` even when source edits work. Report the actual
permission failure; do not claim a commit/push succeeded or work around the
restriction. Permission availability must be checked in the current session.

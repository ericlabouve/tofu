# Varied nine dogs: contour refinement and feedback IDs

The varied nine-dog layout is now the default review. IDs run left to right, top to bottom, 1–9. Labels appear on the layout; hovering, keyboard focusing, or clicking a dog highlights it and shows its ID with an isolated silhouette. Numbers are annotations only. IDs and contours are identical across the eight companion selections.

The exposed envelope receives a 1.6 mm closing pass to absorb shallow pockets, then a 0.8 mm opening pass to soften narrow tips. Added material follows the existing ownership territories. The shared boundary network is smoothed together, retaining frame segments and junctions. This is a contour study, not a guarantee of minimum CAD radii at every junction.

Dog coverage rises from 83.1% to 83.4%. With two bones, remaining area decreases from 14.5% to 14.2%. Larger pockets remain available for companion shapes. The opening remains 120 × 100 mm.

[Before and after](varied-refinement/comparison.png)

Validation: all 24 layouts remain valid, nonoverlapping partitions of the rectangle; all nine IDs are unique and consistent across varied-profile options; label anchors lie inside their dogs. Rebuild with `scripts/companion_study.py`, `scripts/build_nine_dog_review.py`, then run `scripts/smoothing_check.py` and `scripts/varied_refinement_check.py` using `.venv/bin/python`.

Negative-space regions now have letter IDs (A–J in the varied layout), visible on the drawing and on hover, focus, or click. Letters remain attached to the original empty pockets when companion shapes are enabled. The tiny bottom-right remainder is J; its label sits just outside the frame for readability. Geometry is unchanged by these annotations.

## Corner doghouse C

A new `Corner doghouse C` option fills the upper-right corner with a flat-roof doghouse. Dog 3's tail becomes a 7 mm-wide arched doorway. The right jamb and level base replace the previous sloping wedge; the house and dog 3 exchange material without leaving any gray remainder in C. The other eight dogs retain their contours and all IDs stay stable. This option intentionally changes dog 3, unlike the independently fitted companion options.

The house is approximately 26 × 13.2 mm and 222 mm². The rectangular corner determines its flat roof; a conventional peaked roof would need a different shared-boundary design. The nine dogs and house cover 85.1% of the whole sheet. All 25 partition checks passed.

Tail orientation revision: dog 3's tail now leans left toward its head (approximately 22° from vertical along the doorway shaft), using an area-preserving shear around the base. The house doorway shares that tilt. Coverage is unchanged and all 25 partition checks still pass.

### Current corner-roof revision

Supersedes the flat-roof/left-leaning studies above: the house is rotated 45° with its roof peak exactly at (120, 0), the sheet's upper-right corner. Its roof slopes follow the top and right frame edges. Dog 3's tail points up-right into the arched doorway. The house measures approximately 24 × 24 mm in sheet coordinates and 321 mm². Dog 3 and house C jointly consume the entire original C pocket; the other eight dog contours are unchanged. All 25 partition checks and stable-ID checks pass.

### Corner-house experiment removed

At the user's request, the bespoke corner-house option has been removed and dog 3 restored exactly to the refined varied-profile contour shared by the other layout options. Region C is negative space again. The default view has no companion shapes selected. The earlier corner-house notes above document a rejected experiment.

## Bowl D and longer muzzle 1

The default `Bowl D + longer muzzle 1` study extends dog 1's exposed muzzle left to the frame using a smooth, locally weighted displacement. A rounded trapezoid bowl is turned sideways to fit D, with its broad rim on the left edge. It measures approximately 14.2 × 25.3 mm, area 281 mm². Dogs cover 83.7%, the bowl 2.3%, and remainder is 14.0%. Thin strips around the bowl are still counted as remainder. Dog 3 remains restored; dogs 2–9 are unchanged. Select None to compare against the prior refined layout. All 25 partition checks pass.

### Bowl D shared-edge refinement

Bowl D expands to 346 mm² (14.4 × 31 mm), with wider obtuse inner corners. Its upper side shares 11.12 mm of straight boundary with dog 1's muzzle; the final chin transition uses a cubic curve to leave a small relief pocket. The lower side shares a full 16.01 mm straight boundary with dog 4's tail. Adjacent slivers are absorbed into dogs 1 and 4. Whole-sheet remainder falls from 14.0% to 13.4%. Shared-line lengths and all 25 partitions were verified. Tiny remainder labels use leaders for clarity.

### Curved, flared bowl revision

Replaced the straight trapezoid sides with shared cubic curves. The upper rim flares outward and turns smoothly into dog 1's rounded chin; the lower side rounds into dog 4's tail/butt boundary with matched tangent directions at the bowl's lower corner. The prior crescent-shaped chin scrap is absorbed. Bowl area is approximately 355 mm², and whole-sheet remainder is 13.3%. All 25 partitions and stable-ID checks pass. Only dogs 1 and 4 change in this option.

### Symmetric bowl lips

The approved upper flare is now reflected exactly across y=23.5 mm onto the lower lip. Bowl D is symmetric, including both rounded transitions into its straight base. Dogs 1 and 4 share the updated boundary. Reflection symmetry is asserted in the generator; all 25 partition and ID checks pass. Bowl dimensions remain 14.4 × 31 mm, area approximately 350 mm².

### Small jaw and snout relief

Added a narrow curved negative space between dog 1 and the upper bowl lip. The front of the snout now turns away from the frame through a rounded lower edge, flowing into a gently curved jaw. Bowl D retains its exact reflection symmetry. All 25 geometry partition checks and ID checks pass.

## Current baseline: plain gaps and smoother tail 4

The review now defaults to Nine varied profiles / None. Earlier companion studies remain available for comparison but are not the selected direction. Dog 4’s tail uses two tangent-aligned cubic curves through its junction with dog 1, replacing the inward kink with a rounded sweep. The adjacent dog 1 boundary follows the same cut line. All 25 partition checks and stable-ID checks pass. [Tail close-up](varied-refinement/tail4-comparison.png).

### Continuous tail-to-leg join and right-angle face

Dog 1’s left neck/foreleg is now one cubic curve through the dog 4 tail junction. The tail joins it with an aligned tangent, removing the separate hook on dog 1’s outline. Dog 1’s upper-left face has a vertical entry at the top frame, verified at exactly 90 degrees. [Before and after](varied-refinement/neck-face-comparison.png). All 25 geometry partitions and stable IDs were checked.

### Fill strip above head 1

Dog 1 now reaches the top frame across the former thin strip on the left of negative space A. A shorter curved shoulder begins at x=27 mm, replacing the long near-zero-width taper. The top-left right-angle join and the tail/leg refinement are retained. Gap A's left extent is verified at 27 mm; all 25 partition checks pass.

### Repeat frame-strip cleanup: B, D, H, I, J

Filled B's top strip into dog 2's head; D's thin left-frame strip into dog 4's butt; H and I's bottom strips into the left feet of dogs 8 and 9. Dog 9's right foot absorbs J completely, so J no longer appears as a remaining gap. Changes are additive to those dogs, with shorter curved transitions into B, H, and I. All 25 partition checks pass; additive fills and closure of the D strip and J corner were verified. [Detail views](varied-refinement/frame-gap-cleanup.png).

### A's remaining top extension

Dog 2's head now fills A's right-hand thin top extension, with a short curved entry from x=39.2 mm at the frame. Both long extensions of A are removed. Its maximum x is now approximately 39.22 mm instead of 43.23 mm. All 25 partition checks pass.

### Upward tail 3 and bowl-like negative space C

Dog 3's tail now rises to the top border, with a continuous inside curve from the back to the frame. C remains plain negative space, with a wide mouth and narrower rounded base, rather than a separate companion cutout. The former leftward tail hook is removed. [Before and after](varied-refinement/tail3-up-comparison.png). All 25 partition and stable-ID checks pass.

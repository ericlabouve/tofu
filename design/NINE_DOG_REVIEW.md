# Nine dogs and companion shapes

**Earlier iteration:** The updated [smoothing and companion review](SMOOTHING_REVIEW.md) adds bones to the original six, refines the profiles, and expands the shape options. Metrics below record the prior round.

The owner preferred A over B, requested a 3 × 3 arrangement, allowed different dog silhouettes to reduce waste, and asked what the negative areas could represent. All nine supplied images in `inspiration/` were opened individually; see the [image-by-image findings](INSPIRATION_REVIEW.md).

## Layout comparison

See the current [comparison drawing](nine-dog-review/comparison.png); it now reflects the smoothing round.

Every option uses a 120 × 100 mm rectangle and shows plain cutting silhouettes without eyes or drawn ears.

| Study | Complete dogs | Companion candidates | Area in dogs | Area in companions | Remainder |
| --- | ---: | --- | ---: | ---: | ---: |
| Preferred A, retained for comparison | 6 | None | 67.0% | 0.0% | 33.0% |
| A arranged 3 × 3 | 9 | None | 72.3% | 0.0% | 27.7% |
| Nine with varied perimeter profiles | 9 | None | 83.1% | 0.0% | 16.9% |
| Nine varied dogs + bones | 9 | 2 bones | 83.1% | 2.3% | 14.5% |
| Nine varied dogs + fish | 9 | 2 fish | 83.1% | 2.8% | 14.0% |

Percentages are rounded independently. They describe plan area inside proposed cut outlines, not tested food yield or the proportion of physical tofu that must be discarded.

The nine repeated dogs have bounding boxes near **45.1 × 43.8 mm** and areas near **964 mm²** each. The preferred six-dog A had bounding boxes near **45.1 × 60.9 mm** and areas near **1,340 mm²**. Thus the requested 3 × 3 arrangement reduces height more than width; it does not simply shrink every dimension uniformly.

## Varying the dogs

The mixed-profile study retains the shared interior dog-to-dog boundaries. Where a dog borders perimeter remainder, it gains up to 2.4 mm of surrounding area. Boundary-site territories assign each new portion to one dog, avoiding overlapping profiles. The central dog remains the reference profile while peripheral dogs become broader in different places.

This is a controlled first variation in proportions, not a finished set of distinct poses or breeds. Some outer heads and paws flatten against the rectangular frame. Review each isolated silhouette in Chrome to judge whether that tradeoff preserves the desired character. No animal is counted merely by giving an arbitrary scrap a dog label.

## Giving negative space an identity

See the current [companion drawing](nine-dog-review/companions.png); it now compares bones and paws with six dogs.

**Bones** are the strongest thematic match. Their four-lobed ends are recognizable without facial detail. Two fit the larger left-side pockets, with areas of approximately **152 and 126 mm²** and shaft widths of approximately **4.6 and 4.2 mm**.

**Fish** use slightly more of those same pockets: approximately **180 and 161 mm²**. The plain oval body and forked tail supply the identity. The fish-and-bird inspirations prompted this alternative.

**Birds** remain promising for a subsequent complementary tessellation. The cats-and-birds reference demonstrates how a dog's neck, back, and tail boundaries might also describe a bird. That requires designing both animals together; the current scraps are not being labeled as finished bird silhouettes.

These companion studies fit explicit shapes inside the remaining regions. They **do not yet share continuous boundaries with surrounding dogs**, and thin strips remain around them. All such strips are counted as remainder. This is not a zero-waste mixed-animal tessellation. The fits were found by a deterministic translation/rotation grid and scale search, not a proof of optimal packing.

A provisional **120 mm² minimum companion area** filters out tiny candidate pieces; the bone shaft also must be at least **4 mm** wide. These are design-review assumptions rather than owner-specified or physically validated food-handling requirements. The fish tails still need feature-width and release review before fabrication.

## Recommendation and remaining work

Use the varied nine-dog layout as the next geometric starting point, with the bone option as the leading companion theme. The silhouette still needs the owner's visual judgment. Further iteration should reshape the shared dog and companion contours to consume the surrounding strips instead of simply adding independent cutouts.

Keep the right-side pocket and smaller top/bottom pockets visible as unresolved remainder. Do not inflate coverage by calling those shapes useful. The sharp blade section, structural supports for companion loops, 25 mm cutting depth, and mold-related details follow the layout decision. No finished cutter STL was produced for this flat-study round.

## Checks and reproduction

The generator checks that dog and companion polygons are valid, lie within the rectangle, and do not overlap. Numerical holes smaller than 0.01 mm² from the sampled territory assignment are filled; detached numerical specks are excluded from the dog count. All remainder regions, including holes around companions, are preserved in exported geometry and drawings.

Run from the repository root using the pinned environment:

```sh
.venv/bin/python scripts/nine_dog_study.py
.venv/bin/python scripts/companion_study.py
.venv/bin/python scripts/build_nine_dog_review.py
.venv/bin/python -m http.server 8765 --bind 127.0.0.1
```

`nine_dog_study.py` reuses the existing shared-boundary generator and regenerates the previous profile comparison as well. Open `http://127.0.0.1:8765/design/nine-dog-review/index.html` to compare layouts, inspect individual cutouts, and view the nine inspiration images.

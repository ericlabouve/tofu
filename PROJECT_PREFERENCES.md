# Project preferences and design requirements

Recorded from the project discussion on September 28, 2026. This document captures the owner's stated preferences and distinguishes them from decisions still to be explored.

## Purpose and audience

- Make healthy eating engaging for young children by cutting tofu into fun, recognizable shapes.
- Adults operate the cutter. Child-friendly refers to the resulting shapes and visual character, not child operation of sharp blades.
- Aim for a professional, artistic, functional kitchen product.
- Eventually offer four cutters with unique tessellated designs, packaged as one set. Develop the dog design first, with frame and grip consistency across the future set in mind.

## Tofu and intended workflow

- Use firm tofu.
- Preserve a rectangular internal cutting area of approximately **120 mm × 100 mm**. The owner reports that the current prototype's internal opening is already the correct size; verify it from the geometry before redesigning.
  - Subsequent STL audit found an opening envelope of approximately 101.39 × 84.08 mm (assuming millimetres). Use the stated 120 × 100 mm target for new studies; see [the first design review](design/REVIEW.md). This measured discrepancy does not change the owner's target.
- Recommend that the adult slice a roughly **50 mm** thick tofu block into two sheets, each approximately **25 mm** thick.
- The tool must cut through a roughly 25 mm thick sheet in one downward press. Exact blade height and clearance remain engineering decisions.
- Do not require the adult to trim or reshape the rectangular tofu sheet before using the cutter.
- Efficiency matters: cover the sheet with an integrated cutting grid rather than requiring repeated individual cookie-cutter placements.

## Feedback on the initial prototype

Reference geometry: [big_dogs_rect_13x11.stl](big_dogs_rect_13x11.stl).
Visual reference: [big_dog_render.png](big_dog_render.png).

- The border feels ridged and lacks a comfortable place to grip and push down.
- The cutting edges are not sharp enough.
- There are too many dogs, producing cutouts that are too small.
- Some cuts produce incomplete images, such as isolated sections of a foot or head.
- The dog shapes should feel more fun and child-friendly.

## Redesign direction

- The owner likes the **bone companions** and wants them selectable with the **original six dogs**, as well as the nine-dog studies.
- Smooth the dog outlines, especially the feet and shared back connections. Remove the small back hump and unnecessary sharp contour changes while preserving the knife-like blade edge in cross-section.
- Continue exploring dog-themed companions using keyword research. Distinguish recognizable plain outlines from shapes that require decorative marks to communicate their identity.
- The owner prefers **A's proportions** over the longer B profiles. Retain A as the reference and compare a **3 × 3 layout containing nine dogs**.
- Dogs do **not** need identical silhouettes. Vary profiles where this improves rectangular coverage while keeping them recognizable.
- Explore whether remaining negative areas can become useful, recognizable companion shapes. Do not assume all non-dog area must be scrap, or claim an arbitrary leftover is an animal without checking its plain outline.
- The owner supplied nine images in [`inspiration/`](inspiration/). All nine were opened and visually reviewed; findings are recorded in [the inspiration review](design/INSPIRATION_REVIEW.md).
- **First-round silhouettes must be side-profile dogs.** The owner rejected the first exploration because the shapes did not read as dogs and too much space remained between independent cutouts. Do not pursue front-facing dog heads for this round.
- Use the supplied [original tessellation illustration](design/original-tessellation-reference.jpeg) as the visual reference: alternating mirrored profiles with raised muzzles, rounded heads, bodies, tails, and legs. Neighboring dogs should share cutting boundaries.
- Assess plain cut silhouettes separately from illustrated eyes and floppy-ear markings. Interior artwork does not automatically become a cutting feature.
- Prioritize eliminating unused space between dogs. Report perimeter offcuts separately; a gap-free interior does not establish zero waste across the whole rectangle.
- Explore multiple dog tessellations and visual styles before committing to a final design. There is freedom to depart from the existing silhouette and concept art.
- Reduce the number of dogs so each resulting piece is larger and more recognizable. The exact count is not decided.
- Favor playful, organic inner blade contours within a rigid rectangular outer frame.
- Add ergonomic outer grips or pressing surfaces that let adults apply downward force comfortably.
- Taper the cutting edges toward a knife-like edge to achieve a cookie-cutter effect. Exact edge thickness, taper, and blade construction must be resolved for the prototype and eventual casting process.
- Keep the rectangular footprint while exploring how boundary shapes can remain useful and recognizable.
- Aim for zero scraps. Very small pieces count as waste even if the layout technically fills the rectangle.
- Evaluate the tradeoff between complete dogs, rectangular coverage, and minimal waste collaboratively. No acceptable waste percentage or boundary treatment has been selected.

## CAD and manufacturing

- Use [CadQuery](https://github.com/cadquery/cadquery) to evaluate the existing prototype and develop the redesigned geometry and STL.
- A Bambu Lab printer is available for early prototyping. The printer model, nozzle, and print material are unspecified.
- Treat printed parts as development prototypes, not as approved food-contact finished products.
- The intended final manufacturing route is a negative mold used to cast a non-3D-printed, food-safe resin tool.
- No resin or mold-making process has been selected. Food-contact suitability of the final material and process has not been established.

## Open design decisions

- Dog silhouette styles, arrangement, count, and resulting piece sizes.
- Boundary treatment and the acceptable balance between recognizable complete shapes and waste.
- Grip placement, dimensions, and pressing comfort.
- Blade height, taper, edge thickness, structural support, and tofu release.
- Prototype print settings and eventual mold and casting details.
- The other three designs in the future product set.

These open decisions can be explored through prototype evaluation and design options; they do not require further clarification before that work begins.

## Varied nine-profile focus

- The varied nine-dog layout is now the preferred direction because it uses border space better.
- Soften pointed silhouettes and absorb small, easily filled negative spaces while preserving recognizable dogs and the rectangular 120 × 100 mm sheet.
- Assign stable dog IDs 1–9 for individual feedback, visible on hover or click. Maintain IDs across companion options and subsequent refinements.

## Current direction — September 30

Use Nine varied profiles with Gap shapes: None. Keep gaps as plain negative space, without bowls, bones, or other defined companion shapes. Smooth awkward tail transitions and simplify tight negative spaces. Dog 4’s tail should sweep smoothly into the shared boundary with dog 1, using dog 5’s tail as the reference.

## Selected CAD baseline — supersedes earlier layout preferences

The user rejected the other design directions and selected **A · nine dogs / 3 × 3** (layout ID `a9`, gap shapes `none`) for CAD development. Use the original repeated nine profiles, not the varied-profile edits or companion shapes. Preserve the 120 × 100 mm layout, sharp cutting edges, adult palm grips, and clearance for a 25 mm tofu sheet.

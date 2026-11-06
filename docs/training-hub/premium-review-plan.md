# Fixed-position factory development review

Brief: user-provided 6 November 2026 premium factory specification. Completion means implemented, validated and pushed development assets including editable Blender source; physical Quest testing belongs to the user. No main merge or production promotion is authorised.

## Requirements and evidence

1. Fixed viewer composition: verify application origin/eye height/facing, then inspect forward, left, right, rear, up/down and equipment views. Existing six-view evidence is useful but does not cover overhead/floor views or the runtime noticeboard together.
2. Coherent process: audit coal feed, transfer and stockpile routes, maintenance/service bays and ventilation as one mining support facility. Identify and fix visible contradictions.
3. Scale/placement: existing mesh-contact, aisle and crane sweep evidence; supplement actual fixed-view inspection and check preview noticeboard placement.
4. Materials: existing concrete/rock PBR, painted machinery and vertex AO; inspect each prominent view for flatness, repetition and texture scale before accepting.
5. Lighting: inspect every direction for contact, glare and poor visibility. Current runtime lights remain a known optimisation opportunity, not a proven hardware bottleneck.
6. Motion: existing machinery/conveyor/press tests and full-loop sampling. Review visible transfers and resets; capture representative animation if practical.
7. Interactions: real noticeboard titles/history, empty state, ray selection and app activity gating already implemented and tested locally. Include it in final composition evidence; Blender preview placeholders are not live video content.
8. Supporting detail: service bays, ducts, trays, crane, benches and thirteen added belt sections exist; retain purposeful layout and breathing room.
9. Optimisation: instancing, material batching and export simplification measured on desktop. Recheck final export; make no Quest performance claim.
10. Full experience: capture and inspect all required fixed views, record defects and their resolutions rather than assuming prior passes cover this brief.
11. Reproducibility: include self-contained editable Blender file and export commands/dependencies in development delivery. Existing native file is local-only; this remains a gap. All nine file images are packed in current live Blender, confirmed 6 November.
12. Git handover: dedicated branch feature/factory-density-performance. Verify final remote SHA, development artifact availability, screenshots, checks, limitations and headset checklist. Main remains unchanged.

## Starting state

Code-38 corrected beta CI 42144934170 passed both hosts at commit 7b7aa256333aaa4082e43736f057ecfd90d3be59. This is the earlier density candidate, not completion of the new premium review. No revised APK has been published. Existing scene GLB is checksum-pinned, 61 workflow tests pass, standalone resource pack loads scene/audio. Native authoring delivery and the expanded review above remain open.

## Current work

Extended the desktop audit from six views to include exact forward, cardinal left/right, up and down views from (0,1.25,0). Removed an abandoned preload of the untracked light-range experiment, which otherwise prevented reproducing the profiler from a fresh checkout. New captures are development evidence only.

## First visual findings

The new runtime upward capture shows very bright skylight panels and deep-dark roof steel; review exposure/material balance rather than adding more geometry. The downward capture shows a dark square viewer inlay directly under the user and a reflective metallic circle; these are visually distracting in the immediate viewing space. Live mesh bounds identify PRP_seat_inlay_hub as a 0.6m square, 5mm-thick floor detail. The rear capture has coherent service equipment and routes but dark machinery faces need lighting/material attention. These are open visual defects, not passed acceptance checks.

## Material and floor candidate, 6 November

A source-preserving pass sets painted/enamel surfaces to dielectric response and retains bare-metal materials. Skylight emission is reduced from0.55 to0.12. The obsolete metallic viewer ring and inlay are hidden. A downward ray audit identified an additional disconnected plate within PRP_bollard_baseplates at the origin; only that isolated component is removed. Existing safety bollards and painted zone markings remain.

The first candidate exposed that plate after the decorative inlay was hidden; it was not accepted as a complete floor fix. Candidate v2 corrects it. Direct GLB captures are provisional because runtime imports supply texture mipmaps/compression; the selected imported candidate is being reviewed before acceptance. Previous selected GLB is retained as pre-premium-selected.glb outside the repository.

Camera correction: main.gd sets desktop camera height to1.6m, while XR uses the tracked physical pose. Earlier1.25m captures are seated samples, not the exact desktop default. The profiler now accepts explicit eye height and defaults to1.6m. No application tracking or camera movement code was changed.

Reference basis: McLanahan's [coal process overview](https://www.mclanahan.com/solutions/coal) and [fines recovery equipment](https://www.mclanahan.com/products/ultra-fines-recovery-systems) support the interpretation of the scene as coal handling/dewatering with adjacent maintenance and ventilation services. [Godot Sky documentation](https://docs.godotengine.org/en/stable/classes/class_sky.html) describes static radiance-map cost and quality; a reflection treatment is only an option at this stage and has not been added.

Candidate v2 imported into the local application for review. Downward, rear and portal captures at1.6m inspected: central orphan plate and metal circle are absent; original painted safety zone remains. The imported texture treatment is smoother than direct GLB preview. Material/instancing and machinery tests explicitly pass (312sources/25groups;47AO/420packed surfaces; machinery issues0). Local selection is recorded in premium-candidate-state.json; the previous GLB is backed up. This candidate is not yet applied to live Blender, committed or pushed. Further lighting, full-view and interaction review remains open.

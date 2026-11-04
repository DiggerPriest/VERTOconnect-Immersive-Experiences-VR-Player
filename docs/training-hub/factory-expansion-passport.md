SCENE
- intent: dense, believable mining processing and maintenance hall based on supplied references.
- deliverable: editable Blender scene checkpoint, then reviewed game export. Existing production release stays pinned.
- units: metres; axes: right-handed Z-up
- render: preserve source lighting, camera and colour management; review renders 1280x720; source 24fps.
- dynamic: yes; slow screening drums, guarded motor drives, existing fans and coal transport, crane travel after clearance audit.

HIERARCHY
- collection/object naming: EXP_Processing, EXP_ServiceGallery, EXP_CompressedAir; semantic EXP_ names.
- parent/child relationships: screen rotor children inherit one rotation rig per unit. Fixed feed/discharge hoods never rotate.
- protected existing objects: portal/signs/traffic lights, conveyor route/hopper, fans/wall penetrations, floor wear, yard, rear service plant and overhead crane; CAM_main.

ASSETS
- A01 Existing hall | [EXISTING] detailed | 40x44x12m | origin | preserved | original scene | context
- A02 Screen A | [BLOCK] detailed target | 4x7x5m | (-12,3,0) | Y axis | grounded feet | EXP_Processing | primary rear-west machinery
- A03 Screen B | [BLOCK] detailed target | 4x7x5m | (-12,11,0) | Y axis | grounded feet | EXP_Processing | repeated processing line
- A04 West service gallery | [BLOCK] detailed target | 1.5x21x4.1m | (-16.5,5.5,0) | wall parallel | deck z4.1 | EXP_ServiceGallery | links rear service platform
- A05 Compressor/receiver skid | [BLOCK] detailed target | 5x3x3.5m | (14,11,0) | grounded | EXP_CompressedAir | right-rear plant
- A06 Service workbenches/parts | [BLOCK] detailed target | 2x6x2m | (18,5,0) | grounded | EXP_CompressedAir | right wall detail
- generation: none, zero credits.

SHOT
- active camera: preserve CAM_main portal-facing default.
- framing/lens/target: preserve source; added review camera faces rear-west from centre eye height.
- foreground: clear central floor; machinery occupies side bays; rear gallery gives upper depth.

LOOK
- material roles: existing yellow safety paint, graphite machinery, galvanized deck/handrails, grey concrete, cool teal motors, subdued red isolation controls.
- route: existing materials reused where possible; new plain Principled materials export safely.
- texture scale: preserve existing concrete and rock PBR.
- relief: bevelled edges and recessed panels, no displacement.
- metallic/roughness: painted equipment roughness .45-.65, bare steel .3-.5; no mirror chrome.
- world/background: preserve.

LIGHTING
- focal subject: portal in default view, processing line in rear view; lower service recesses remain darker.
- mood: daylight through existing high windows plus industrial practicals.
- environment: existing, no generation.
- key/fill/exposure: preserve source pending A/B renders.
- new fixtures: emissive task strips under gallery, no unbounded dynamic light additions.

MOTION
- slow constant drums; 1 revolution/25s, opposing phases; no zero scale keys.
- fixed camera for VR; no camera drift.
- crane: assess before animation; no speculative moving load.

ACCEPTANCE
- structural: supported equipment, connected gallery/stairs with rails/toeboards; central pedestrian route and door approaches remain clear; no unrelated removals.
- motion: inspect evaluated first/mid/end poses and loop seams; no moving fixed hoods, detached drive shafts or intersections.
- visual: full 360 review at eye level; no primitive placeholders in final deliverable; realistic material distinction, contact and sensible equipment connections.
- lighting: source comparison, no clipped new emissive fixtures; retain portal sign read.

References: user supplied plant/crane screenshots; Metso, Designing for efficient mill maintenance (accessed 4 November 2026), https://www.metso.com/insights/blog/mining-and-metals/reline-your-thinking-44-designing-for-efficient-mill-maintenance/ . Applied as access/platform/utility-routing inspiration, not a claim that this fictional hall is an engineered plant.
refs_read: blender-scene, blender-scene-spec, blender-modeling, blender-lookdev, blender-lighting-camera, blender-animation, blender-audit-finalize.
Phases: A specification complete; B source checkpoint preserved; C blockout pending visual gate; D detailed assets pending; E audits pending.

Progress: blockout rendered and reviewed; two detailed drum rigs, gallery/stairs, compressor/receiver, headers and benches are present in build/factory-expansion/VERTO_processing_detail.blend. Detail render reviewed. Whole-room density, guards/transfer connections, additional machinery, motion/contact audit, lighting cleanup and runtime export remain open. Source preview reports EEVEE shadow-buffer overflow; no headset performance claim is made.

Second bay pass (4 November):
- A07 twin pump skid [BLOCK], 3.8x5x2.7m at (8.2,5,0), grounded, two guarded motor shafts.
- A08 process tanks [BLOCK], each diameter2.36m, height4.05m, centres (12.2,5),(15,5), common header to existing plant. Detailed flanges/valves/level gauges.
- A09 east service gallery [BLOCK], 1.2x9m, top4.1m, x16.6 y1..10, stairs y-4.6..1. Existing conveyor clearance must be checked.
- A10 electrical MCC [BLOCK], five 1.4x1.2x2.7m cabinets on east wall, centres x19,y13.8..19.2; cable tray above at z6.4.
- A11 guarded motor test bench [BLOCK],3.7x2.2x2.7m centred(-8.2,-5.2); local motor rotor animated.
- A12 crane [EXISTING], bridge travel y9.45..7.2, trolley x-3..-6, 50second loop with rests; unloaded. No hoist scaling.
- Motion families: drums25s, pumps7.5s, testbench10s, existing fans/belts/coal; crane50s. Key only moving rigs. New lights: emissive task strips only.
- Scope: only add FIT_ServicePlant; replace screen feed boxes by recoverably hiding originals. All earlier checkpoint files preserved.
- New references: McLanahan Rotary Trommels and RCR Scrubbing/Screening, accessed4 November2026. Feed, unders collection, end discharge and drum support arrangement guide geometry. No purchased/generated assets.

Reviewed candidate (4 November):
- Authoring: build/factory-expansion/VERTO_factory_crane_fitted.blend. The earlier live session was preserved as live_before_bays_update_20261104.blend; no original checkpoints overwritten.
- 268 first-pass parts plus 409 second-pass parts, 24 tumbling coal lumps and editable equipment tags. Moving crane travels 3.75m between end poses and returns exactly to its starting pose. Source frame rate is 24fps; preserve existing fan/conveyor timing.
- bays-review-audit.json: no intersections against the existing columns, no staircase/conveyor intersections, no new equipment in the central route; crane checked at rest, intermediate and end poses against the structure.
- Contact shading: static geometry vertex AO, 16 rays per vertex, radius1.5m, 33,344 vertices across635 meshes. Moving machinery excluded from occluders to avoid baked ghost shadows. Existing floor texture and AO retained.
- Export: factory-crane-fitted.glb, 38,239,048bytes, 229,412triangles,316 mesh primitives,105materials,223animation clips; SHA256 0c4be9c3da79cb99889c030b8d5b16c54f32a5c066dafdb11496aa96deacce1e. No new image textures. Rigid siblings beneath each drum rig are combined per material only in the disposable export process.
- Actual Godot renders inspected at eye height for portal, yard door, processing and pump bays. New motion test verifies exported transforms change and batched drum meshes follow their rig. This does not prove Quest frame time, comfort or visual acceptance.
- Remaining acceptance: final source-suite run on this exact export, beta APK/native CI, one-Quest queue/restart/presence and scene-performance test. Current production remains 0.9.5/code34; candidate uses beta identity/code35.

Crane refinement: runways now at x±8.8m, bridge span17.6m, with32 new brackets/braces aligned to the existing column rows. Dense crane audit:105 poses, no tested structural intersections, loop seam0m. Intentional bracket-to-column fastening contacts are excluded from equipment collision failures. Final export motion test passes after this geometry refinement. Local full-suite run passed85 cases before the crane-only geometry refinement, and the real-export case passed again afterward. Workflow Python tests61/61 and public-source checks passed. Quest hardware acceptance remains open.

User screenshot review (4 November): remaining rear floor is too empty. Do not treat the prior candidate as the final density target. Add substantial inward equipment islands on BOTH sides of the rear lane, not just wall furniture.
- Rear-left island: heavy wheel/roller component rebuild stands at x-4.8,y9..13, footprint3x5m, maxheight3m; floor contact and retaining supports required.
- Rear-right island: hydraulic cylinder rebuild/test bench at x4.8,y11..16, footprint3x5m,maxheight2.8m; guarded slow linear ram animation, hydraulic power unit and hoses.
- Rear-left back staging: stacked mill liners/steel spares at x-5.3,y18,footprint3x3m,maxheight1.8m.
- Rear-right back plant: hydraulic filtration/power pack at x7,y18,footprint3x2m,maxheight3.5m, connected to the existing rear utility route.
- Control station: x-4.8,y6.5,footprint2.4x1.5m,maxheight2m. Native editable labels/screens; zero paid generation.
- Keep the continuous roller-door approach and viewer starting area clear. Check new footprints against the real lane/door geometry before detailed work.
- The code35 run41757751533 is intermediate; it must not be described as final scene acceptance. Further scene work required before a final test candidate.

Rear density revision implemented:
- 275 additional parts in FIT_Rear_Workcells: wheel/axle retaining stands, guarded hydraulic cylinder test bench, control station, liner storage, connected hydraulic filter plant, plus a6.1m service bridge with structural girders, column crossheads, handrails and west access stair.
- Authored checkpoint: build/factory-expansion/VERTO_rear_populated.blend. Loaded into the user's live Blender session after a timestamped recovery copy of their prior scene.
- rear-populated-audit.json passed:105 crane samples; no new equipment/column or staircase/conveyor intersections; central route clear; hydraulic rod remains inserted in its fixed barrel over its0.55m stroke and returns to the starting pose.
- Earlier CI run41757751533 is confirmed completed/cancelled because its scene was superseded. No APK was published from that run.
- New rear AO bake/export is running. Revalidate the new GLB and ram in Godot, update the exact source pin, run relevant checks, then dispatch a new beta build. The previous candidate GLB in the app does not yet include this density revision.

Rear revision export and local verification:
- AO source: VERTO_rear_populated_ambient.blend; export factory-rear-populated.glb (39,167,960bytes;244,148triangles;322mesh primitives;111materials;224clips;10textures). SHA2564c2789eeccdd975f1e6c23d997e3c9d4abe8c9f77fe05e32e0c64d72ed525834.
- This export is now installed in the app on this branch, and its exact public-source pin is updated. No production release asset was changed.
- Dedicated real-export motion test now includes the hydraulic ram. The actual exported scene, cold/suspended scene lifecycle, stockpile coal loop, playback tools and headset handover tests all passed on the new export.
- Playback tools:399 checks passed. Restart coverage now reloads a nonalphabetical multi-video queue and verifies its exact stored order plus loop/shuffle/custom settings.
- Remaining: native beta build, binary/receipt/hash verification, then one-Quest hardware and visual acceptance. This is not a claim of complete goal acceptance.

Published rear revision (4 November, final status for this candidate):
- Exact source commit0bee805ceb10e161e9673f2fbe69dcf5b6185f4d passed both native CI hosts in run41759965320. The superseded run was not used.
- Code35 beta is published under a unique filename on the existing test prerelease. No production release, older test asset or device assignment was replaced. See ../devices/factory-queue-code35-check.md for the direct APK, SHA256, provenance and required hardware checks.
- Downloaded APK v2 signature/content integrity, package identity/version and ARM64 libraries independently passed. APK-imported geometry/animation signatures match local source; all224 clips and the exact supplied MP3 are present. The packaged compiled queue script exercises single-video and multi-video wrapping.
- Public unauthenticated download and GitHub's asset digest both match SHA25684d71eddcbed1918abacfba818c67437d02af46e17d8e9e1ecca8b1585d0be1c (148,857,728bytes).
- Remaining acceptance: Ryan's rear-density/whole-room visual review, one-Quest queue/persistence/presence/Jess regression checks, comfort and performance. The active goal must remain open until these are accepted.

User acceptance and production promotion (4 November):
- After agreeing to test code35 on one Quest, Ryan reported "perfect, worked 100% perfect", then instructed "now we push to live". This accepts the scene and queue candidate; it does not supply independently measured Quest frame-time or thermal data.
- Production candidate 0.9.6/code36 retains the exact accepted scene/audio and playback scripts. Only release version metadata, distribution identity and acceptance/release documentation change for promotion.
- Merge into the actual default branch quest-360-mono, build/tag through the existing signed production pipeline, verify the published APK and deliver its distinct production URL/SHA256. Keep previous release assets and the separate beta.

Production publication complete:
- PR#1 merged into quest-360-mono at ef06da4973eac22dbd3a3e5d2be4c3a2033e0c6c. Tag v0.9.6 / code36 passed both build hosts and automatic publication in run41765514399.
- The actual signed production Quest APK passed independent identity/version/certificate/v2 integrity checks and a full public download hash check. Its imported geometry/224 animations, exact MP3 and compiled queue wrap behaviour match the accepted baseline.
- [Production APK, SHA256 and evidence](../devices/production-0.9.6.md). Existing production and beta assets are preserved. Device Manager fleet rollout remains a separate operation.

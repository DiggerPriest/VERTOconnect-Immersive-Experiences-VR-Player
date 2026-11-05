# Density and performance revision

SCENE
- intent: approximately double the visible machinery density of accepted1.0.0 and reduce the lag Ryan reports when looking around the factory.
- deliverable: updated live editable Blender scene and recoverable checkpoint; audited GLB/runtime; isolated beta APK for comparison. Keep published1.0.0 and production assignments unchanged.
- units: metres; axes: right-handed Z-up.
- render: preserve CAM_main, 24fps, frame1..1201, EEVEE, Khronos PBR Neutral/exposure0. Eye-height runtime comparisons at1.25m,85deg FOV,1280x720/2xMSAA.
- dynamic: yes; retain existing machinery and coal/crane/ram motion. Add no more than four purposeful new moving rigs; no camera animation in VR.

HIERARCHY
- existing: VERTO_Higgsfield_Mining_Concept. Live pre-change snapshot2471 objects,224 actions. Recovery before_density_preserve_live_20261105-085426.blend in local task staging; active source path remains unchanged.
- new: DENS_<cell> collections and semantic DENS_ objects/rigs. Each complete workcell remains independently editable. Shared mesh/material data for repeats; destructive batching only in disposable export.
- protected: hall, floor/wear, portal/decline/sign/green traffic light, fans and wall connections, conveyors/transfers/coal yard, crane/runways, all accepted workcells, CAM_main, queue/audio/Jess/handover behaviour.
- no generated assets and no credit spend.

ASSETS
- A01 accepted hall/plant | [EXISTING] detailed |40x44x12 |origin |preserved |existing collections |baseline18 purposeful workcell groups, not counts of bolts.
- A02 crusher/feed and guarded drive | [BLOCK] detailed |4.6x4x5.2 |(-12.6,18.2,0) |Z-up |floor pads |DENS_Crusher |large front-side mass.
- A03 filter press | [BLOCK] detailed |6.2x3x2.9 |(14,-19.2,0) |long-X |floor skid |DENS_FilterPress.
- A04 gearbox rebuild | [BLOCK] detailed |3.3x4x2.6 |(-6.9,-17.8,0) |long-Y |retaining stands |DENS_Gearbox.
- A05 lubrication/test skid | [BLOCK] detailed |3.4x4.5x2.9 |(-5.3,-10.5,0) |long-Y |floor skid |DENS_Lubrication.
- A06 welding/fixture bench | [BLOCK] detailed |2.6x3x2.8 |(4.7,0,0) |long-Y |floor pads |DENS_Welding.
- A07 motor/parts racking | [BLOCK] detailed |3.6x3x3 |(-5.4,1.8,0) |long-X |floor rack |DENS_MotorRack.
- A08 hose/filter test cart | [BLOCK] detailed |1.8x2x2.2 |(4.2,7.6,0) |long-Y |wheels |DENS_TestCart.
- A09 hydraulic press | [BLOCK] detailed |6x6x4.6 |(14,-13,0) |long-X |floor raft |DENS_Press.
- A10 dust extraction/filter skid | [BLOCK] detailed |3.8x3.2x4.7 |(15.2,16.4,0) |long-X |floor skid |DENS_Extraction.
- A11 spare rotor stand | [BLOCK] detailed |3x3x2.4 |(-12.6,-3.3,0) |long-Y |retaining stands |DENS_Rotor.
- A12 bulk spare shelves | [BLOCK] detailed |1.4x5x2.8 |(-18.4,7,0) |wall-parallel |floor rack |DENS_BulkStore.
- A13 instrument/MCC cabinets | [BLOCK] detailed |1.2x3.2x3.2 |(18.8,-.8,0) |wall-parallel |floor plinth |DENS_Instruments.
- A14 twin air receivers | [BLOCK] detailed |2.4x1.5x3.3 |(12,20.1,0) |vertical |floor pads |DENS_Receivers.
- A15 service/valve manifold | [BLOCK] detailed |2x.8x3.3 |(-7.5,21,0) |wall-parallel |floor frame |DENS_Manifold.
- A16 consumables/service rack | [BLOCK] detailed |.8x4x2.8 |(-18.8,12.5,0) |wall-parallel |floor feet |DENS_Consumables.
- A17 hose reel bank | [BLOCK] detailed |.8x4x2.8 |(-18.8,-7,0) |wall-parallel |wall brackets |DENS_Reels.
- A18 conditioning/separator skid | [BLOCK] detailed |3x3x3.6 |(11.2,-.8,0) |vertical vessels |floor skid |DENS_Conditioner.
- A19 belt service trolley | [BLOCK] detailed |1x3x1.4 |(4.1,-16.4,0) |long-Y |wheels |DENS_Trolley.
- A20 supported crusher gallery/access stair and connected overhead service banks | [BLOCK] detailed |existing bay bounds |right-front/upper side walls |attached to actual structure |DENS_AccessServices.
- Footprints are initial proposals: relocate a complete cell when collision/access audit fails, before detail. Preserve centralx±3m route and observer radius3m; door approaches/portal remain open.

SHOT
- CAM_main remains portal-facing; compare six fixed runtime directions before/after. The scene is occupied in foreground, midground and upper bays rather than furnishing only distant walls.
- Density target: at least2x purposeful workcell groups (18->36), plus approximately2x mean equipment coverage in paired fixed-view masks. Report actual coverage; duplicate bolts or a narrower camera are not evidence of density.

LOOK
- reuse graphite, teal, yellow, off-white and galvanized material roles. Preserve existing concrete/rock PBR, AO and texture scale.
- loft continuous machine housings, open hoppers, genuine frame/panel/drive/guard details, connected pipework. No unresolved primitive proxies in final runtime.
- optional export-only solid-color packing into vertex color, preserving exact PBR properties and all textured/emissive materials. Source materials remain editable.

LIGHTING
- preserve authored preview lighting and exposure. Runtime baseline:27 lights,26 omni ranges4096m, all unshadowed. Bound light influence to intended bay/tunnel/indicator and verify images; do not claim graphics preserved from a numeric range change alone.
- preserve visible fixtures/signs; add no real-time lights for new workcells. Use existing light motivation and baked/vertex contact detail.

MOTION
- preserve source loops and pauses; retain the existing animation mixer; the rest-track pruning experiment was reverted. Baseline466 active tracks in9 groups.
- investigate instancing repeated moving ore while keeping source transform nodes and exact world poses. Suspension must stop both animation and instance-buffer updates.
- new motion: guarded crusher mechanism, extractor fan, conditioning drive and press ram with clear rests/return. No moving suspended load.

ACCEPTANCE
- A inspect/spec: [x] core/spec/model/lookdev/light/animation/final-audit refs read; [x] live snapshot and baseline.
- B recoverability: [x] live recovery copy and object/bounds manifest; only DENS_ additions and explicit runtime/export optimisations in scope.
- C blockout: [ ] silhouette; [ ] proportions; [ ] depth; [ ] contact/access; [ ] six-view camera read; fix largest collision first.
- D detail: [ ] distinct complete workcells at planned fidelity; [ ] useful supports/services; [ ] preserved lighting/material identity; [ ] source remains editable.
- E audits: [ ] motion poses/loop seams; [ ] structure/access/crane clearances; [ ] paired full-color and equipment-mask views; [ ] runtime scene/audio/playback regressions; [ ] beta binary verification.
- performance: compare same views/settings and actual counters, minimum2s samples; aim lower worst-case draws and frame intervals despite greater density. Baseline desktop draws293/96/310/91/96/107; median frame intervals2.373/2.046/2.246/1.983/2.151/1.977ms. These are Apple M5 Pro desktop measurements, never Quest measurements.
- headset: user chose to continue without a connected Quest. Real headset FPS/comfort remains unverified until a beta test; do not claim the reported lag fixed from desktop proxies.

refs_read: blender-scene, blender-scene-spec, blender-modeling, blender-lookdev, blender-lighting-camera, blender-animation, blender-audit-finalize.
References: Godot4.7 stable Optimizing3D performance, MultiMeshes, and Lights/shadows (accessed5November2026); the supplied mining factory/crane photos and previously cited Metso maintenance access reference.

User refinement: layout must make operational sense, retain good textures, and include many more conveyors. Arrange two clear zones: the accepted front transfer train and maintenance bays; an additional rear/west processing train. Relocate the NEW crusher proxy to(-12.6,18.2),4.6x4x5.2m and NEW press bay to(14,-13),6x6x4.6m before detail.
- New material flow: external raw-coal receiving hopper -> C1 rear-wall infeed -> raised crusher discharge -> C2 transfer -> C3 distribution -> C4/C5 powered cross-feeds into existing screenB/screenA feed hoppers -> enclosed unders chutes -> C6 recessed fines collection -> C7 western-wall outfeed -> coal stockpile.
- Seven additional belts; each actual endpoint, grade, support, guard, drive and chute must be audited. Initial maximum grade16.8deg; no unsupported steep normal belt or gravity chute carrying material uphill.
- The elevated distributor runs beside the existing west gallery, leaving its walkway/rail usable. The new line does not cross the centralx±3m route. Preserve rear roller-door access and crane swept envelope.
- Explicit scope expansion for this flow: non-destructive, named modifiers on the rear/west wall panels and floor/joints for framed belt penetrations and a guarded, lined collection trench. Preserve source originals and texture UVs; cutters never render/export. Detail only after footprint/transfer review.
- Actual Blender coordinates/endpoints and grades are written to process-layout.json. The remaining proposed cells stay as previously specified, subject to clearance correction.
- Animation-mixer rest-track experiment did not reduce this scene's actual track count and was reverted. Keep the working mixer; focus on measured draw submission/light costs. Coal instancing passes real OpenGL world-pose/update/suspension checks; Dummy-renderer readback is explicitly unavailable.

5 November implementation update:
- Applied all 18 new native workcells, seven conveyor mechanisms, two framed wall openings, collection trench and 70 animated coal lumps to the LIVE scene using Blender's native console after the plugin disconnected. No generation credits used. Active file path and existing camera preserved.
- Recovery: /Users/rpriest/VERTOconnect-Scene-Work/density-performance/live_density_detail_20261105-144548.blend. The existing main file was not overwritten.
- Full six-view source render after detail: mean projected equipment coverage 0.2942 versus baseline 0.2423 (+21.4%). Workcell count doubled, but the visual-density target is NOT yet met. More useful upper-bay service infrastructure and final layout review remain.
- Existing-coal instancing: portal draw calls 293->227; conveyor 310->244. Same-session uninstanced control confirms counts. Desktop frame timings are variable and do not establish improved headset performance.
- New connected-detail export is isolated under mining_facility_density for review. Main app scene path and published APKs unchanged. Export-only solid colour packing is experimental until visual/runtime validation.
- Remaining: transfer clearances and floor intersections; external ground support; complete machinery motion/services; materials/contact shading; broader visible density; runtime export/audits; stable performance comparison and beta delivery.


Current state — 5 November, 16:00
- Authoritative live recovery copy: `/Users/rpriest/VERTOconnect-Scene-Work/density-performance/live_conveyor_clearances_20261105-155951.blend`. Native Blender console applied this pass; the active file path and user viewport were preserved.
- Ten added belt runs now include the 34.3 m overhead trunk, a powered trunk cross-transfer, level/low gallery underpass, enclosed distribution elevator, raised distributor and two independently supported screen cross-feeds. Separate drop chutes keep rollers and return belts apart. Raised C1 head clears the crusher hopper rim and rests on side brackets; the western wall bench moved 0.8 m as a complete assembly to clear C7.
- The latest triangle audit includes belts (previous workcell-only checks missed them) and cross-cell new geometry. No significant overlaps with existing equipment and no new mesh within the central ±3 m route were found. The only two reported cross-cell intersections are the intended C1 steel riser/stringer joints. This broad-phase + triangle test excludes small intersections below its thresholds and is not a substitute for final visual/access review.
- Six-view source comparison immediately before the final hanger/elevator adjustment: mean projected equipment coverage 0.3364 versus baseline 0.2423, +38.8%. The approximately 2x visible-density target remains OPEN; doubling workcell count does not satisfy it by itself.
- AO baked into 2,204 static meshes / 69,993 vertices in a separate export copy. Source materials remain editable; no live scene replacement or published asset change.
- Light-radius trial: 26 point lights bounded to 2–15 m in isolated profiling. Portal and rear images inspected. Desktop draw counts unchanged and variable timing does not prove a speedup. Runtime hook remains disabled pending full comparison.
- Noticeboard: implemented locally, front-right at runtime (1.8,1.75,-3.6), angled towards the seated user. Actual four distinct recent videos, cached thumbnails, tilted ray targets and playback routing; test passes history reload, photo exclusion, corners/centres, forward 85-degree bounds, disabled/empty state. Preview uses explicitly synthetic titles. Main integration parses, but real playback/input end-to-end regression and Quest usability remain OPEN. Source Blender does not yet contain the runtime-only board.
- Production 1.0.0 and the application's selected scene path remain unchanged. No new APK/release has been published for this density pass.

- Fresh corrected GLB imported into the isolated density review scene: `density_clearance_ao_20261105.glb` (42 MB). 3,049 static objects consolidated to 104 static export objects; all 324 authored animation clips exported. Live source remains unbatched/editable.
- Runtime AO defect found and fixed: imported `AO_` materials had vertex-color use disabled. The wrapper now enables authored AO and packed paint; real-export test passes 32 AO surfaces and 381 packed surfaces with nonempty color arrays. Processing and portal renders inspected after the fix.
- Corrected full-scene desktop draw calls: portal226, fans104, conveyor240, rear101, processing111, plant108. Baseline portal293/conveyor310: approximately23% fewer calls in those two heavy views despite added geometry. Other views increase, and submitted triangles increase; no claim of Quest frame-time improvement. Desktop timing remains variable.
- All jobs in this pass completed. Current remaining work includes stronger overall visual density, motion/contact/access audit beyond collision thresholds, real noticeboard playback integration tests, export/release regression checks and an isolated beta for Quest testing.

- Follow-up AO visual audit caught black wall triangles: Boolean-generated vertices were added after baking and inherited zero color (372 concrete-wall / 300 cladding vertices in runtime inspection). Fixed by evaluating modifiers in the disposable copy BEFORE AO baking. New authoritative review export: `/Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_clearance_evaluated_ao.glb`; imported into `mining_facility_density`. Strengthened real-export test now verifies every AO color channel stays >=0.61, consistent with the bake's 0.62–1 bound; PASS. Portal/noticeboard preview checked after correction. Editable live source remains unchanged by export evaluation.

Current verification update — 5 November, upper services and mesh reuse
- Offline editable candidate: `/Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_upper_services_20261105-162418.blend`. Two 32.3 m side ventilation trunks, cable ladders, hangers, registers and connected extraction headers add useful upper-bay infrastructure. Duct height was lowered to clear the existing fume duct. This pass has NOT been applied to the open Blender scene; its last verified live recovery remains the 15:59 conveyor-clearance copy. Native UI was locked at the last check; unlock request is pending.
- Six-view equipment coverage: 0.35346965 against 0.242297 baseline (+45.9%). The doubled visual-density requirement remains OPEN. Covered collision checks find no existing-equipment or central-route overlaps; only the two intentional C1 riser/stringer connections remain. Thresholded checks do not prove complete clearance or operational access.
- Current isolated Godot review GLB is now `density_upper_services_instanced.glb`, copied to `app/godot/environments/mining_facility_density/mining_facility.glb`. 3,419 static source objects consolidate to 105 export objects; source remains editable. All 324 clips retained.
- Exact animated-mesh reuse reduces exported mesh definitions from 320 to 216. `tools/training_hub/verify_mesh_reuse.py` compares every mesh node's primitive attributes/indices, materials, node transforms/hierarchy and all animation samples/targets/interpolation. Comparison with the non-deduplicated upper-service export PASS; evidence `mesh-reuse-fidelity.json` in the staging directory.
- Expanded runtime instancing fixture PASS (CPU grouping/material/idempotency/suspension). Actual imported-scene test PASS: 282 sources in 22 batches, including stockpile42, seams32, rollers36, original ore72 and 10 coal pieces on each of C1–C10. Real-export shading test PASS: 33 AO surfaces and 381 packed surfaces, bounded nonzero AO. Command uses `--headless --xr-mode off`; initial XR-enabled attempt stalled before test startup and was terminated, not counted as a test result.
- GPU pose/readback and six-view performance comparison for the expanded instancing are still OPEN; headless results do not establish headset frame-time improvement.
- Noticeboard playback integration test PASS using the real Main/board/coordinator with a fake native decoder/access boundary: exact content URI replay at 0 ms, no new poster on failed/unpresented playback, poster update after first presented frame, history clearing. Native Quest playback remains unverified for this pass. Broader player-menu190 and recent-files81 checks PASS.
- Remaining full scope: further purposeful visible density, machinery motion, final camera/material/access audit, live Blender application, GPU/performance checks, isolated beta and Quest confirmation. Production1.0.0 and the selected app scene path remain unchanged; no new APK or release published.

Live application and rendered verification — 5 November, 16:54 onward
- User unlocked the Mac. Applied `live_upper_services.py` through the native Blender console to the existing dirty scene, preserving filepath/camera/view. Console success and restored viewport inspected. Before copy: `live_before_upper_services_20261105-165437.blend`; authoritative live after copy: `live_upper_services_20261105-165438.blend`, both in the local staging directory. 370 service components, two 32.3 m ventilation trunks and two cable ladders. Previous pending-lock status is superseded.
- Rendered GPU fixture PASS. Strengthened real-export test additionally checks all 282 imported animated source poses against their MultiMesh GPU transforms at three successive samples; PASS. AO/packed-material tests still PASS.
- Corrected profiler's uninstanced control to restore EVERY source hidden by the controller (formerly only CV_ORE). Same current scene with/without instancing: portal305->125, fans130->105, conveyor307->101, rear146->102, processing189->112, plant110->74 desktop draw calls. Latest profile/evidence: `upper_instanced.json`, `uninstanced_control.json`, `imported-instance-gpu-test.log`. Primitive counts differ slightly from animation phase/culling. Portal, conveyor and rear rendered images inspected; scene remains present, central access clear.
- Desktop median frame intervals are variable and this control run was often faster despite more draw calls. Therefore only reduced submission count is proven; improved frame time is NOT proven. Quest profiling/testing remains required before claiming reduced lag.
- Gallery-cabinet idea investigated and rejected before construction: available gallery decks do not reach the proposed wall bays; the east gallery is only1.2m wide. No cabinets added that would obstruct access or float without a platform. Bench/upper-bay inspection files in staging preserve this layout evidence.
- Goal remains active: overall visible-density target, remaining purposeful detailing/motion, full layout/visual audit and isolated beta/hardware verification remain open. No production release changed.

Perimeter air distribution — 5 November, 17:10
- Added `add_workshop_air_distribution()` to the native source builder: 115m of perimeter compressed-air main, receiver feed, six isolated service outlets/quick couplers, wall brackets/clamps and a roof-supported section beside the ventilation plenum. Swept elbow rings use transported cross-section axes; repeated fittings use shared low-sided meshes. Pipes are connected to the existing receiver common header, with the rear feed routed above existing process headers.
- New candidate source: `/Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_air_distribution_20261105-170802.blend` (107 added components). An explicit thin-geometry check uses 1mm broad-phase overlap and evaluated triangle intersections against all visible existing meshes, not the earlier large-volume cutoff. Initial clashes with shelving, cable brackets, bench tooling and headers were corrected. Final `air-audit.json` has only intended intersections: the receiver/header junction and a wall plate seated on a structural column. Enclosed containment, maintenance reach and all internal new-new contacts are not proven by this triangle test.
- Six-view render completed; rear and plant views inspected after corrections. Mean equipment coverage0.35676794 against0.242297 baseline (+47.2%); the approximately2x visible-density target remains OPEN. No central-route props added.
- The Mac locked again before native application. `live_air_distribution.py` is prepared but NOT executed; last actual live copy remains `live_upper_services_20261105-165438.blend`. Preserve that distinction when resuming.
- AO/export completed in disposable copies: `density_air_final_ao.blend` and `density_air_final.glb` (44,517,368bytes). Current isolated review-folder GLB replaced with this candidate; import/runtime validation follows. Production scene selection and published1.0.0 are unchanged.
- Air candidate import completed. Headless real-export test PASS:34 AO surfaces,381 packed surfaces,282 instanced moving sources in22 batches. Export has3,526 static objects consolidated to106, with all324 source clips retained. GPU/desktop comparison has not been repeated for this small static addition; last measured performance remains the upper-services candidate.

Local application integration — 5 November, 17:18
- Changed `training_hub.MINING_SCENE` on feature/factory-density-performance to `mining_facility_density/mining_facility.tscn`. This supersedes earlier notes that the development app still selected the old scene. Published production1.0.0/APKs remain unchanged; no push, APK or release in this pass.
- Failing-first loader check proved the old path lacked the100 added conveyor-coal sources and expanded instancing. After switching the path, actual asynchronous loader test PASS, including suspended loading, audio gating, moving coal, imported-camera protection and rapid scene switching. The test helper now warms the selected scene in headless UI tests rather than the legacy asset, retaining the cold-load exception.
- Real Main/noticeboard integration test now waits for actual factory loading and invokes the real activity gate instead of forcing board visibility. PASS: board and MP3 available after load; world/audio/board suspend and resume for Jess, wearer absence, passthrough and application pause; poster routes the exact stored URI to native-player access/open at0ms. Native decoder/access remain simulated, not a Quest playback claim.
- Broader regression: player menu190 checks PASS; stockpile loop PASS max visible step0.059242m; exported equipment motion PASS. An obsolete rigid-mesh-count assertion initially failed because packed materials reduced four drum meshes to two. Independently compared old/new drum geometry in parent space: both retain exactly6,464 vertex positions with identical multiplicity under their original rotor parents. Test now checks geometry beneath each moving parent and continued motion, rather than requiring the old material split. Evidence: `drum-batching-comparison.json`.
- All Android export presets now exclude unused `environments/mining_facility/*`. The legacy source stays locally for comparison. Exported a local52MB resource pack (`density-integration-review.pck`, not an APK); loaded it in a separate empty Godot project. PASS: selected dense factory loads,100 new animated coal sources/22instance batches survive, MP3 and noticeboard script present, old factory scene/GLB absent. Evidence: `density-pack-check.log`.
- Latest native Blender remains upper-services live copy; the air distribution pass is still pending native application because the Mac relocked. Density/visual-detail scope, full final scene audit, final GPU/profile pass and beta/hardware confirmation remain open.

Rear compressed-air package — 5 November, 17:24
- Inspected three candidate bays against current geometry. Rear-left is occupied by liner storage and the service bridge; front-left would conflict with gearbox access/portal signage. Added one packaged compressor only in the clear rear-right bay: footprintx3.5–5.3,y18.75–21.25, outside the central±3m route. Native cabinet, service panels, louvres, isolators, controls, fasteners, guarded cooling fan and supported discharge connection total63 components.
- Editable candidate: `density_rear_compressor_20261105-172412.blend` in the local staging directory. Triangle check reports only the floor/plinth contacts and connection to the new air header. Cooling-fan check at25 frames across a revolution: visible motion present, no blade intersection with guard/backplate/case, loop-transform error1.11e-6. Evidence: compressor-audit.json and compressor-motion.json. This is a geometric/artistic check, not engineering certification.
- Six-view review completed; rear render inspected. Mean equipment coverage0.35832948 against0.242297 baseline (+47.9%); full visual-density target still OPEN. Central access and rear doorway remain legible.
- New export `density_compressor.glb` is imported into the selected local density scene.3,584 static source meshes consolidate to106,104 shared animated-mesh replacements retained,325/325clips exported. The four visible fan-blade meshes remain children of the new animated fan parent. Exported motion regression including that parent PASS; material/AO/instancing test PASS (34AO,385packed surfaces,282moving sources in22batches).
- `live_air_and_compressor.py` prepares both unapplied source passes with before/after copies. NOT executed: no unlock confirmation since the last verified locked UI. Live Blender remains upper-services checkpoint. The earlier resource-pack check predates this compressor and will need renewal for final candidate delivery; no new APK or published change.

Spatial-batching investigation — 5 November
- Measured explicit animation/instance updates over1,000 warmed90Hz steps in the current scene, using the headless desktop renderer: motion median28us/p9537us; instance updates median47us/p9559us. These exclude GPU/driver and do not measure Quest cost. Evidence: cpu-update-baseline.json. Avoid claiming the renderer's lag is solved from draw count alone.
- Added optional exporter flags `--static-cell-size` and `--static-cell-min-triangles`, defaulting to the existing material-only batching. Building-spanning authored pieces remain separate; no source geometry or live scene changes. Exported unselected12m full and12m selective trials from the same compressor AO checkpoint. The full trial increases static export nodes106->588 and is not selected.
- Headless camera-frustum/AABB estimates (not GPU draw counters or timing) show the selective20,000-triangle threshold lowers visible triangle submissions in every sampled view: portal294728->232892, fans268140->222212, conveyor263016->216640, rear233104->193572, processing239568->211520, plant257816->210864. Estimated visible mesh surfaces increase by25–38. Evidence: static-culling-estimate.json. This is a tradeoff requiring rendered/device comparison, not an established optimisation.
- Selective trial retains identical per-material triangle counts and exact animation samples (325clips). Strict rounded-world geometry comparison has479 differing triangle signatures and123 differing vertex positions per side at0.1mm quantisation. Numerical transform changes and triangulation are possibilities, not yet proven causes. Normal/UV/colour and rendered-image equivalence remain unverified. Do NOT replace the selected candidate with this trial until resolved.
- Regenerated default export after exporter edits: exact comparison PASS for all491mesh nodes, primitive attributes/indices, materials, transforms/hierarchy and325animation clips. Current selected app asset remains `density_compressor.glb`; experimental variants are only in staging. All investigation jobs completed. Full goal remains active.

Stable static batching investigation — 5 November, follow-up
- Direct UI retry after the user's unlock reply still reported the Mac locked. No live source mutation occurred; air distribution/compressor application remains pending. Offline work continued.
- Original spatial comparison found all positions within 0.02mm, but normal-component differences reached0.2473. Added opt-in `--stable-static-batches`: preserve evaluated corner normals and join into identity-coordinate anchors. Default remains unchanged.
- First stable exports introduced an extra colour stream on67primitives: the empty anchor did not retain the intended active/render colour selection. Explicitly select ExportColor after joining. Do not use first stable exports.
- Corrected artifacts: density_stable_global_v2.glb and density_stable_selective_v2.glb, unselected staging only; both retain325clips. Bidirectional attribute report stable-v2-spatial-attributes.json: COLOR_0 and texture-used UV deltas exactly0; no unmatched world positions within0.02mm; maximum observed position componentdelta0.0000158466m. Maximum normal componentdelta0.0002049268, with144AO_M_steel_charcoal vertices per direction narrowly exceeding unchanged0.0002tolerance. Strict comparison still FAILS; residual investigation and rendered validation remain open. Do not interpret reduced numerical error as proven visual or Quest performance equivalence.
- Added export guard requiring exactly the intended COLOR_0 channel (no missing or ambiguous COLOR_1) on AO_/PACKED_PBR materials. Executed actual guard against defective first stable global (rejected), both corrected exports (pass), and currently selected compressor export(pass). Python syntax parsed successfully.
- All jobs launched this turn finished. Current app remains density_compressor.glb; no APK, GitHub or production update. Source density target and hardware performance validation remain incomplete.

Stable batching comparison resolved — 5 November
- Converted singleton static batches through the same identity-coordinate join as larger groups under the opt-in stable flag. Regenerated BOTH controls: density_stable_global_v3.glb and density_stable_selective_v3.glb. Earlier v2-global/v3-selective mixed comparison was not an apples-to-apples control (singleton signs changed conversion); discard it as a batching-equivalence decision.
- Stable v3 pair PASS at unchanged tolerances: identical world triangle/vertex signatures at0.1mm rounding, per-material triangle counts and all325animation samples. Bidirectional vertex attribute check: NORMAL/COLOR_0/texture-used UV component differences exactly0; no unmatched positions within0.02mm. Evidence: stable-v3-pair-geometry.json, stable-v3-pair-attributes.json. This proves equivalence between these export strategies, not yet fidelity of every exported source object or rendered/performance improvement.
- Newly found existing-export defect: current density_compressor.glb has12CV_ORE nodes at360triangles each, others20. Native density_compressor_ao.blend inspection confirms ALL72CV_ORE source objects are20triangles each; CV_OreVariant_00 has15users. Stable exports preserve20pernode, accounting for4080fewer triangles (328008->323928). Evidence: ore-source-counts.json. Likely shared mesh datablock contamination when the original join uses a source object as active target; validate exact source/export primitive fidelity before replacing selected asset. The selected runtime currently retains the older export and must not be described as fixed.
- No jobs remain running from this turn. Stable flag remains opt-in, selected app/source/live Blender unchanged. Next: verify animated coal source fidelity, rendered comparison/import checks, then choose global or selective batching based on actual performance evidence rather than estimated triangle count alone.

Shared-mesh export correction adopted locally — 5 November
- Exported all72CV_ORE objects directly from the native AO checkpoint, selection-only and without batching, to ore_source_reference.glb. Independent comparison checks indexed local triangle positions/winding/corner normals at1e-6: both stable v3 exports match all72; old compressor export fails exactly12. Evidence ore-source-fidelity.json. This establishes lost duplicate triangles were an export defect, not authored detail.
- Fixed standard batching too: copy a multi-user active mesh datablock before object.join mutates it. New density_global_isolated.glb preserves all72source coal objects(1440triangles vs faulty5520). Exact regression against old export proves ONLY those12coal primitive payloads differ; all other geometry/materials, transforms, hierarchy and325animation tracks remain exact. Evidence ore-source-fidelity-isolated.json and isolated-export-regression.json.
- Copied density_global_isolated.glb into app/godot/environments/mining_facility_density/mining_facility.glb and completed headless editor import. Spatial/stable trials remain unselected. This is a LOCAL candidate correction, not published production.
- Initial runtime test stalled in XR initialisation before test code; own PID29644 terminated(SIGTERM,exit143), then rerun with --xr-mode off. Explicit material/AO/instance test PASS:34AO,385packed surfaces,282sources/22batches, all conveyor zone counts. Evidence isolated-materials-xroff.log. All launched jobs terminal. Rendered and Quest performance gates remain open; full density target remains incomplete.

East service-bench layout repair — 5 November
- Inspected current compressor source and six-view colour renders. Found legacy WKS_bench_S1 top/frame/drawers overlapping EXP_Bench_Top_1/4. Inward relocation rejected: tank, gallery posts, stair stringer and service supports occupy that strip. Evidence current-benches.json, east-bay-neighbours.json.
- Added idempotent repair_east_workbenches(): hides only3redundant legacy structural parts (recoverable in source); retains wall board/tools/light. Places existing vice on EXP bench4 and existing bins on bench7, clear of their spare bearings. No floor-route narrowing or arbitrary clutter added.
- New editable candidate density_bench_layout_20261105-181308.blend; previous compressor checkpoint retained. Bounds audit proves both additions fully supported within their worktops, correct tabletop height and no spare-bearing overlap. Rendered/inspected bench-layout-review.png (audit camera/fill only, not saved into scene). Evidence bench-layout-repair.json/bench-layout-audit.json.
- Updated pending live_air_and_compressor.py to include bench repair before after-checkpoint. Not executed in live Blender. Runtime GLB remains corrected density_global_isolated from previous pass; bench source candidate still needs AO/export integration after further layout work. No active jobs, no APK or production update. Full density and measured-performance gates remain open.

Bench candidate integrated — 5 November
- Baked AO from density_bench_layout_20261105-181308.blend into density_bench_layout_ao.blend:2739meshes/85533vertices/16materials. Editable source unchanged. Export density_bench_layout.glb retains325clips,104shared-mesh replacements,3581static source meshes->106batches. Standard shared-datablock isolation fix enabled; experimental spatial batching still off.
- Imported new GLB into selected local density scene. Added real-runtime regression assertion that all original CV_ORE source meshes contain60triangle-corner vertices (=20triangles), covering the previously proven12corrupt chunks.
- Actual selected-scene headless tests with --xr-mode off PASS: test_mining_export_materials(34AO/385packed surfaces/282instanced sources/22batches and coal-size guard), test_factory_expansion(0issues), test_stockpile_loop(explicit exit0). Logs bench-test_*.log. All sessions terminal.
- Local app now includes the bench consolidation; live open Blender still awaits pending application. Latest editable source remains density_bench_layout_20261105-181308.blend. Production/APKs unchanged. Full density target, final rendered app audit and measured headset performance remain unproven.

Twin cyclone recovery addition — 5 November
- Live Blender retry again reports Mac locked; no live mutation. Created floor-plan.png as review-only cutaway from current native bench source. Checked two rear-right candidate bays: wall bay rejected due to clean bench/receiver/MCC occupancy; inner bayx8.4–11.2,y9.2–12.4 clears existing floor plant and central route. Evidence dust-bay-neighbours.json/inner-dust-bay-neighbours.json. Note a possible existing clean-bench/MCC overlap found in rejected bay needs follow-up.
- Added idempotent add_dust_recovery_skid():58native components, twin cyclone bodies/cones, sealed collection bins, slide gates, inspection plates, bolts, inlet vacuum connection, frame/saddle supports, common outlet/filter branch, structural hangers. Connects existing DENS_DustDuct_04 at(15.2,16.55,6.8). This is visual process equipment, not certified engineering.
- First background build crashed with stoi out-of-range before any checkpoint; replaced unbounded float suffixes in new foot/leg names with two-decimal names. Retry succeeded. First render exposed insufficient body support; added rails/saddle beams and regenerated from unchanged bench checkpoint.
- Latest editable candidate: density_dust_recovery_20261105-182550.blend. External BVH collision audit: only intended branch/riser connection and hanger contacts with column caps/brackets. Render dust-recovery-review.png inspected after support fix. Audit camera/fill never saved to candidate. Evidence dust-recovery.json/dust-recovery-audit.json.
- New skid not yet included in pending live script, AO bake or app export. Selected app remains density_bench_layout.glb. All jobs terminal. Next: review new skid from default six views, assess density coverage, tidy duct junctions/materials as needed, investigate clean-bench/MCC overlap, then integrate. Density/performance goal incomplete; no APK/production update.

Dust wider-view review and clean-bench clearance — 5 November
- Six seated-view colour/mask renders completed for supported dust candidate; rear/plant renders inspected. Equipment coverage mean0.360339506 vs baseline0.242297 (~48.7%increase). New unit reads in both views while central route stays clear; full2xvisual target still unmet. Evidence layout-review/dust_recovery_coverage.json and matching colour/mask images. Coverage is a composition metric, not a performance result.
- Confirmed WKS_bench_Clean overlap with FIT_MCC_Cabinet_0. Added idempotent repair_clean_bench_clearance(): translates all8bench components +0.6X/-0.6Y. Ends bench before cabinet, increases gap from receiver to bench front, keeps pegboard/treatment coherent. Latest editable checkpoint density_clean_bench_20261105-182854.blend.
- BVH external intersection check reports only bench-frame/floor-edgeband contact; no MCC/receiver collision. Rendered clean-bench-review.png inspected. Camera/fill remain review-only. Evidence clean-bench-repair.json/clean-bench-audit.json.
- Updated pending live script to apply air/compressor/east-bench/dust/clean-bench passes with before/after copies. NOT executed. Selected runtime still bench-layout export without new cyclone/clean-bench update. Next integrate latest candidate after further review; all launched sessions terminal. No APK or production change; goal open.

Dust/clean-bench runtime integration and GPU check — 5 November
- AO-baked latest editable checkpoint to density_dust_clean_ao.blend; exported density_dust_clean.glb,3639static meshes->106batches,325clips retained. Imported into selected local density scene. No experimental stable/spatial/light-range flags enabled.
- CLI OpenGL Compatibility rendering works while native UI access remains locked. Do not treat the UI lock as preventing all rendered checks. Actual M5Pro GPU current-profile six-view draw counts126/106/102/107/113/79, triangles278748/250352/266286/235608/242432/260600; median desktop frame intervals1.328–1.496ms. These are uncapped desktop observations, NOT Quest performance or headset frame-budget proof. Evidence dust-profile/current.json and actual screenshots; rear render inspected.
- Bounded-light comparison completed separately on same export. No shadows enabled in either control;26Omni currently have4096mrange. Bounded trial median1.325–1.474ms, draw/triangle counts unchanged; differences small/variable and do not establish a meaningful gain. Rear/portal screenshots inspected; leave runtime unchanged. Evidence dust-profile/density_bounded.json. Earlier imagery light differences are real artistic changes, not free equivalence.
- Actual GPU test PASS for imported poses(3samples/all282sources), material/AO/20triangle coal guard and22instance batches. Async environment loading/suspend/audio/camera lifecycle test explicitPASS. Evidence dust-gpu-materials.log/dust-environment-test.log. All sessions terminal.
- Current local runtime includes cyclone and clean-bench clearance. Native live script remains pending. Production unchanged. Full2xvisual density target and actual headset performance validation remain open.

Spatial batching measured through normal import — 5 November
- Extended profile_factory_scene.gd to support rawGLB wrappers and explicit LOD2/LOD4 variants, with threshold included in reports. RawGLB stable-v3 control pair produced fewer triangles but extra draw calls; raw loading skips importer-generated LODs, so this alone cannot decide app adoption.
- Imported BOTH same-source stable-v3 exports under tests/density_profile (all Android presets already exclude tests/*). Wrapper/lighting identical to app. GPU imported_global vs imported_selective: portal126->155draws,276604->214170triangles,1.449->1.448msmedian; fans106->134,248208->201606,1.443->1.439; conveyor102->127,264142->217632,1.405->1.411; rear107->145,233464->193572,1.376->1.446; processing113->151,240288->211670,1.480->1.523; plant79->103,258456->209108,1.320->1.409. DesktopM5Pro/Compatibility only, no Quest extrapolation. Exact geometry/shading/animation pair proofs already recorded.
- Spatial strategy remains OFF: two views effectively tied, four slower, no demonstrated benefit to justify higher draw count. Test-onlyGLBs are comparison artifacts, not runtime dependencies. Reports/screenshots dust-profile/imported_global.* and imported_selective.*. Normal source-only default export remains selected.
- LOD2 on current dust/clean runtime saved only~1–1.4%triangles with tiny/variable desktop timing differences; no viewport setting adopted. Evidence dust-profile/lod_2.json. No foveation/render-resolution/user-quality preferences altered.
- All jobs finished. Current selected runtime and production unchanged this turn. Full density target and Quest validation still outstanding.

Connected filter process pipework — 5 November
- Added add_filter_process_headers():67native components, two continuous swept pipe paths, flange/identification bands, suspended cradles/saddles/roof anchors and isolation fittings. Feed branches from existing pump riser to fixed filter-press head; return joins existing tank return header/riser. Long runs outside crane±9.18m envelope, no new floor posts or central-path obstruction. Connections are visual process layout, not engineering certification.
- Audited proposed corridor against current geometry first. Initial BVH found unwanted feed/press-rail intersection; raised final feed connection from1.65 to2.1m. Rebuilt from unchanged clean-bench checkpoint. Final external BVH reports only intended existing pump riser, fixed press head, tank riser and return-header junctions. Evidence process-pipe-neighbours.json/filter-headers-audit.json.
- Latest editable source density_filter_headers_20261105-184849.blend. Close views inspected; first two review cameras had foreground obstructions, final filter-headers-review.png clearly shows press-end connections and overhead pipework. Audit camera/fill never saved to source. Full seated coverage still pending for this addition; do not infer2xcompletion from component count.
- Pending live script now includes headers, still unexecuted. Runtime GLB remains density_dust_clean.glb without these new headers. All jobs terminal; production/APKs unchanged. Next: broader view/coverage check and integrate audited candidate, continuing density/performance goal.

Filter-header wider review and integration — 5 November
- Six seated colour/mask renders complete; portal/conveyor views inspected. Mean equipment coverage0.362155993 (~49.5%above0.242297baseline), still below2x target. Portal and central routes remain clear. Blender renders omit the runtime-only noticeboard; do not claim these renders prove board hit targets.
- AO baked2864meshes/90541vertices/16materials; exported density_filter_headers.glb with325clips,106static batches,104shared animated mesh replacements. Imported into selected local density scene. Latest editable source remains density_filter_headers_20261105-184849.blend.
- Selected-scene material/AO/instancing/coal-shape regression PASS. Actual Main/noticeboard/coordinator integration test explicitexit0 after this import; native decoder/access use the established test double, not Quest playback. Evidence headers-test_mining_export_materials.log and headers-test_mining_noticeboard_playback.log. All jobs finished.
- Next larger density candidate to assess: maintenance catwalk alongside elevated C8 trunk. Investigate west side roughlyx-13.3..-12.2, deck~6.65m, roof/crane clearance, supports and real access before building. Rear stairs would clash with C4 transfer; do not add them blindly. A service ladder near y-6 may be an option but requires source bounds/swept geometry audit. This is an unvalidated layout idea, not completed work.
- Live Blender application remains pending, production/APKs unchanged, no goal completion claim.

### Conveyor catwalk clearance review — 2026-11-05

Saved candidate `density_trunk_catwalk_20261105-190319.blend` adds a 24 m west-side service catwalk with caged access ladder, hatch, roof hangers and a dogleg around C5 suspension. External mesh intersection audit found only intended crossbearer-to-trunk support contacts. A vertical ray grid at three lateral positions along the deck found no geometry within 2 m above deck height (ladder hatch excluded). This is a sampled geometry check, not engineering certification.

`trunk-catwalk-review.png` is partially obscured by foreground steelwork, so it is not sufficient walking-route visual proof. Additional unobstructed views remain required before selecting this candidate for export. Catwalk is not yet in the runtime asset or live Blender window. The native UI tool still reported the Mac locked after the user reported unlocking; saved-file CLI checks remained available.

### Catwalk visual review and local runtime selection

Unobstructed `trunk-catwalk-deck-review.png` shows the deck, guardrails, hatch/ladder and C8 relationship. Six seated views in staging `catwalk-views` have mean equipment coverage 0.3643991 versus baseline 0.242297 (about 50.4% higher, still below double). The new catwalk is now selected in the local density GLB; native editable source remains the trunk-catwalk checkpoint. AO export preserves 325 clips, 104 shared animated mesh replacements and 106 static material batches. Godot import completed and `test_mining_export_materials.gd` explicitly passed, including 282 instanced sources and original-coal topology checks. Pending live application script now includes catwalk; it has not been executed in the UI.

Desktop GPU profile completed for selected catwalk asset: six views retained draw counts 126/106/102/107/113/79, median frame intervals 1.382–1.508 ms. Triangle counts 249084–292224 reflect additional geometry; unchanged batches do not mean zero GPU cost. Processing runtime screenshot inspected. These M5 Pro desktop results do not establish Quest performance. Profiler now creates its output directory and fails explicitly on report-open errors; first attempt had failed to save due to a missing output directory and was terminated before rerun.

### Roof geometry budget pass

Native inventory found 323556 visible mesh triangles, including eight roof trusses at 4312 each. Exact planar dissolve recovered none and was rejected. `prepare_factory_roof_lod.py` makes a disposable copy with reversible 0.5-ratio modifiers on only STR_truss_00..07. Each is reduced to 2156 triangles, saving 17248 total. Bidirectional vertex, centroid and all edge-midpoint nearest-surface samples stayed below 7 mm; this sampled check is not a continuous Hausdorff proof. Paired seated upward renders `roof-original.png` and `roof-reduced.png` inspected: silhouettes/connections remain coherent.

Selected local asset is now `density_roof_detail.glb`, baked/exported from disposable `density_roof_detail.blend`. Original editable trunk-catwalk checkpoint unchanged. The export retains325clips/106staticbatches/104sharedanimated replacements. Godot import and material/original-coal topology test passed explicitly. Density target and headset verification remain open.

Roof-detail desktop profile: portal 292224 to 274976 triangles, 1.496 to 1.583 ms median; fans 263828 to 246580 triangles, 1.465 to 1.441 ms median; conveyor 279762 to 262514 triangles, 1.440 to 1.406 ms median; rear 249084 to 231836 triangles, 1.451 to 1.422 ms median; processing 255908 to 238660 triangles, 1.508 to 1.487 ms median; plant 274076 to 256828 triangles, 1.382 to 1.318 ms median. Single sequential runs are not sufficient to attribute a speedup; geometry reduction is verified, Quest lag remains unmeasured.

### Motor-test instrumentation addition

New native candidate /Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_test_instruments_20261105-192848.blend adds 110 components: supported instrument backboard, analogue meters, terminal rail, retained leads, isolator and parts bins. First shelf/motor interference corrected, then rear conveyor-pier/foot interference corrected. Final BVH contacts are only the two intended bench brackets against tabletop. Final close render inspected. This candidate is not yet exported or live-applied; runtime remains roof-detail GLB. Pending live script includes the addition.

### Instrument-panel runtime integration

Selected local GLB is density_instruments.glb, with motor-test panel and roof reduction combined. Import completed; materials/topology and real Main noticeboard-to-playback integration tests explicitly passed. The latter uses a fake native-decoder/access boundary and still reports two shutdown ObjectDB leaks, so this is not a hardware decoder test. Export retains325clips/104sharedanimated replacements,108staticbatches (two additional material groups). Six seated native views show mean coverage0.36562146, still short of double the baseline. Staging current-density-build.json records exact selected source/hash and unverified live/Quest/release status. Both native UI and bridge were checked: UI locked, bridge disconnected.

Instrument build GPU desktop profile completed: draw counts128/108/102/107/115/79; medians1.320–1.501ms. Instrument-facing runtime view inspected. This adds two draws where the panel is visible and 2036–2728 rendered primitives depending on view/LOD; no Quest performance claim.

### East product route candidate — not selected for runtime

Candidate /Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_east_product_20261105-194012.blend adds C11 (29.4 m elevated east trunk) and C12 (18.91 m rising side discharge), suspended trunk structure, outside trestles and named MANIFOLD wall/window cuts with framing. Rearward route was rejected because it crossed the elevated bridge. Side route at y12.0 avoided roof truss collision present at y12.4.

First detailed support audit found remaining issues: trunk lower chord meets DustRecovery_FilterBranch_1; hangers meet C11 pull wire; upper chord meets end shafts/drive; final diagonal meets C12 return/stringer; outside bearers intersect C12 return belt. Frame-to-wall and stringer contacts include intended attachments, but mechanical clearances need repair. Full C11/C12 versus surroundings audit not yet done (current audit is structure-only). Feed elevator, corner transfer, outdoor pile, support clearance repairs and coal animation remain pending. Review image inspected; this is a work-in-progress saved source only. Selected runtime remains density_instruments.glb, live scene unchanged.

### East conveyor support repairs

Latest candidate /Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_east_product_20261105-194620.blend. Shortened/lowered upper chords and final diagonals, moved hangers clear of pull wires, lowered outdoor crossbearers below return belt and added outboard saddles. Roof mounting plates separated from existing filter-header anchors by an offset at the roof attachment. Full C11/C12/structure versus surroundings audit now reports only intentional roof-truss hanger/anchor and wall-frame junctions; mechanical return/pull-wire/shaft checks have no hits. This is geometric validation, not structural certification.

Indoor feeder proposal at (10.1,-17.4) rejected: service mains at x10.4 pass through casing, with a service post at prospective hopper. Alternative external elevator envelope (11.3,-23.2),1.4x1.6x8.2m and hopper (11.3,-25.8),2x2x2.2m showed no surface intersections. Next implementation should connect outdoor feed via a properly framed front-wall opening (C11 would extend from current -17.4 to about -22.3 with supports). Outdoor feeder, that extension/opening, transfer hood, stockpile, moving coal and camera review remain unbuilt/unverified. No runtime selection of this candidate yet.

### East route connected native candidate

Latest saved source /Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_east_product_20261105-200228.blend. C11 now extends34.3m from an external elevator through a framed front-wall opening; C12 rises18.91m through the side-wall opening; C13 is a2.6m hopper feed. Added enclosed lift/drive/hatches, grizzly hopper, corner hood, enclosed stockpile loading chute, coal heap with existing YARD_Coal normal material and varied embedded chips, plus concrete service pads. Removed window-sill clashes via the named front opening and adjusted lift footing. Pads narrowed to avoid workshop floor/columns; remaining external intersections are intended roof/wall attachments and new apron under existing yard apron/coal.

Thirty new coal objects have native loops900/480/240frames, phase staggered. Motion audit passed exact loop endpoint poses and max visible per-frame steps .038113/.039394/.010834m respectively. Initial C13 interpolation jumped .856m while partly visible; constant location interpolation immediately before the invisible wrap corrected it. Exported/runtime loop fidelity still needs testing because export force-samples animation. Final pile scatter revised from overly regular chips to deterministic varied embedded chips. Exterior render review done; seated review, corner close review, optimised export, runtime motion/instance checks and performance remain pending. Runtime still density_instruments.glb.

### East conveyor runtime integration and wrap regression

Six seated native views of the connected route show mean equipment coverage0.3900482 (about61% above baseline0.242297; double target still open). Corner close view inspected. Initial exported motion test reproduced a0.256754m partially visible jump on C13 although native constant-key checks passed. Added a2.5% fully hidden interval on both sides of reset; actual imported40second test now passes30rocks, max visible step0.015761m at60Hz, zero off-belt or stagnant samples. Test first rejected older selected scene for missing C11, then reproduced export jump, then passed repaired asset.

Selected local runtime now density_east_wrap.glb from editable /Users/rpriest/VERTOconnect-Scene-Work/density-performance/density_east_product_20261105-201158.blend. Roof reduction preserved;355clips/114staticbatches. Material/topology test now requires C1–C13 and passes312instanced sources/25groups. Factory-expansion motion test passed on initial east export before wrap-only animation repair. Current-build staging manifest records selected source and hash. No live Blender application or release.

East-route desktop profile: portal: 133 draws, 287886 triangles, 1.571ms median; fans: 109 draws, 259258 triangles, 1.451ms median; conveyor: 110 draws, 276172 triangles, 1.440ms median; rear: 114 draws, 245320 triangles, 1.477ms median; processing: 116 draws, 251244 triangles, 1.501ms median; plant: 86 draws, 270312 triangles, 1.387ms median. Plant runtime screenshot inspected. Additional geometry has a real cost; this is a desktop sample, not Quest validation. Pending live application script now includes the east route but remains unexecuted.

### East conveyor inspection access correction — 5 November, 20:30
- Native candidate: `density_east_inspection_20261105-202949.blend` in density-performance staging. Adds 27.5 m suspended inspection deck and 15-riser access stair from existing gallery (183 components).
- Corrected landing to terminate at the angled upper-riser plane; previous rectangular landing covered upper treads. Relocated hanger lower connections away from filter-header supports; widened gallery rail entry; moved paired under-gallery luminaire away from stringer.
- Rebuilt from currently selected editable source, then re-ran evaluated-mesh BVH intersections and 375 vertical 2 m headroom probes: zero headroom hits. Remaining external intersections are truss anchor connections, stair-to-existing-deck joints and gallery rail/post joints. No remaining pipe-support or luminaire clashes.
- Stair close-view inspected after landing correction; final correction relocates only luminaire. This is candidate evidence, not full clearance certification: finite ray samples and external BVH tests do not cover all internal joints or every pedestrian path.
- Candidate is not yet in selected runtime GLB or live Blender. Full seated-view review, export verification, density remeasurement and headset performance remain open. Existing selected runtime and production releases unchanged.

### Inspection deck seated review and export preparation — 5 November, 20:33
- Rendered and inspected all six fixed seated views from the latest native candidate. Portal sightline and central marked aisle remain clear; inspection deck reads above existing processing equipment. These low-sample native previews are layout evidence, not final headset lighting quality.
- Projected equipment coverage mean 0.395294 (original 0.242297, approximately +63.1%). The requested doubling remains incomplete; do not count extra component objects as proof of doubled visible density.
- Disposable inspection_roof.blend passed roof reduction again: 17,248 triangles removed within the existing sampled deviation guard. inspection_ao.blend completed static vertex AO for 3,915 meshes / 96,326 vertices. Native editable checkpoint preserved.
- inspection.glb export started; selected runtime remains the previous east conveyor asset until export/import checks are complete.
- Export completed: inspection.glb (~43 MB), 355 animation clips retained, 117 static batches. Staging inspection-export-status.json records checksum and explicitly leaves runtime verification/selection/live application false. Next step is isolated Godot import and actual imported material/motion checks before selecting this asset.

### Inspection walkway runtime integration — 5 November
- Imported candidate in a temporary sibling scene with identical mining_environment wrapper. Actual imported material/mesh test passed: 40 AO surfaces, 417 packed surfaces, 312 instanced sources / 25 groups; original coal geometry guard retained.
- Actual imported C11–C13 motion passed 40-second transform audit: 30 rocks, no off-belt or stagnant pieces, max visible frame displacement 0.01576058 m.
- Desktop Compatibility 1280x720 2xMSAA six-view profile: draw calls 133/109/111/115/116/87 (portal/fans/conveyor/rear/processing/plant). Versus prior east train, adds 0–1 draw calls and 3,192–3,756 triangles per view. Median frame intervals 1.397–1.555 ms are similar desktop results, not a Quest improvement claim.
- Viewed runtime portal and plant screenshots: central portal and aisle clear, staircase and upper deck visible, tint/AO intact. Selected checked inspection.glb into local mining_facility_density asset; current-density-build.json updated. Temporary sibling candidate moved outside app to staging to avoid shipping a duplicate asset. No production/release changes; live Blender still separate.
- Density remains approximately +63.1% by six-view projected equipment coverage, short of doubling. Further purposeful workshop detail, full end-to-end checks and real Quest performance review remain open.

### Bench service detail candidate — 5 November, 20:43
- Added add_bench_rebuild_stations: two supported rotor fixtures on verified free regions of EXP_Bench_Top_1 / Top_4, plus a bearing-inspection tray on FIT_Rear_DeskWorktop; 50 components using existing steel/zinc/teal materials.
- Initial three whole-bench placements were rejected after collisions with existing vices/bins/cabinet. Repositioned using evaluated mesh/BVH free-space checks; final candidate external mesh intersection audit returns zero contacts. Floor aisles unchanged.
- Native candidate density_bench_rebuild_20261105-204142.blend remains separate from selected runtime. Close view of first rotor fixture inspected and shows supported shaft, bolted feet, and connected fixture plate. First camera was blocked by existing stairs/cabinets and was repositioned; it was not treated as a passed visual check.
- Remaining: other workstation close views, broad view value/density review, export integration. Small details must not be represented as achieving doubled visible density. Current selected/runtime asset remains inspection.glb; no production change.

### Bench polish integrated and loader regression refreshed — 5 November
- Inspected remaining mid-bench rotor and inspection tray close views. Six seated-view masks mean 0.3953379, only +0.0000437 over walkway source; these small service details are polish, not meaningful progress toward doubling visible coverage.
- Roof preparation, AO and GLB export completed with explicit markers: 355 clips and unchanged 117 static batches. Selected local app GLB updated to bench.glb; current-density-build.json records source/export/checksum. Material/instance regression PASS (40 AO/417 packed surfaces, 312 sources/25 groups).
- Cold async loading test initially failed obsolete expectations (100 new coal / <=10 motion players). Inspected actual runtime: 130 coal pieces on C1–C13; exactly 11 players, all with distinct durations on same animation root (25,14,0.416667,1.291667,0.375,10,37.5,20,50,7.5,15 seconds). Added conveyors account for new periods, not failed consolidation.
- Updated loader fixture to 130 coal/25 instance groups/11 players and added root+duration uniqueness assertion to catch needless player splitting. Loading/suspend/audio/rapid-switch test then PASS, explicit completion marker. Godot still prints one ObjectDB instance leak warning on exit; passing behavioral checks do not resolve that warning.
- Live Blender/APK/production unchanged. Density remains ~63% above baseline, not doubled. Next additions should affect the seated composition rather than accumulating tiny hidden parts.

### Visible spare-belting maintenance stand — 5 November, 20:55
- Added DENS_BeltingStore: 2.1 m diameter / .86 m wide spare conveyor belting roll, retained shaft/collars, paired A-frame supports, base pads/cross ties and parked crank. 24 components, no new animation or transparency.
- First proposed envelope intersected ENV_drain_left/grates; narrowed/shifted stand to x=-4.1, y=-4.4, z=1.38. Envelope x[-4.85,-3.35] preserves the central x±3 m route and clears drain x[-5.38,-5.02]. Final evaluated-mesh external intersection audit empty.
- Seated native close-view inspected. Reduced fabric/rubber stripe contrast after first render read too graphically; final candidate density_belting_store_20261105-205432.blend reviewed with subtle layers. Reel is visibly supported and portal remains unobstructed.
- Six-view masks on geometrically identical pre-colour-refinement candidate yielded mean coverage0.40002572 (+65.1% vs baseline0.242297), portal0.367276 vs bench0.347506. This is still short of doubled coverage. No claim final materials alter this mask measure.
- Candidate remains native-only, not selected/exported/live. Selected app asset remains checked bench.glb. Broad final-colour review, export, runtime and headset checks remain open; no release changes.

### Cross-factory transfer route investigation — 5 November
- Checked proposed overhead transfer envelope x[-11.2,10], y[3.75,5.25], z[5.65,6.85] using evaluated mesh intersection and contained-vertex tests. Route rejected: west service mains, C8 return belt/stringer, upper/lower truss chords and two diagonals intersect it.
- Existing crane bridge runs y7.2..9.45, trolley top8.72, with continuous runways at x±8.8. A new cross route must clear both the fixed runways and moving bridge/hook, not merely pass a frame1 camera view. No cross-conveyor geometry was installed. Do not cut existing structural bracing to force this route.
- Proceeding with previously audited spare-belting export while route remains unresolved. This investigation does not count as another installed conveyor or achieved density.

### Spare-belting runtime integration — 5 November
- Exported final subtle-edge reel with roof reduction/AO passes; 355 clips retained, 119 static batches. Selected belting.glb locally and updated source/checksum in current-density-build.json.
- Actual imported material/instancing test PASS:43AO/417packed,312sources/25groups. Runtime portal screenshot inspected: reel/stand present, central decline sightline and aisle clear.
- Desktop six-view profile (portal/fans/conveyor/rear/processing/plant) draws136/112/111/115/116/87, triangles295674/267046/282480/251628/256988/276620, medians1.557/1.471/1.432/1.451/1.483/1.395ms. Relative to inspection profile, includes both bench details and reel; +3draws in portal/fans, unchanged other views. Portal p95 2.019ms vs1.721 previously; a single variable desktop run does not establish headset gain or regression.
- Production, APKs and live Blender unchanged. Goal remains open: full density target, cohesive layout review of remaining additions, final app checks and Quest performance evidence still incomplete.

### Hose-repair workcell candidate — 5 November, 21:07
- Verified empty envelope x[3.35,5.65], y[2.5,5.5], z[.02,2.8] beside welding/test benches; built compact 1.9x2.6 m hose-repair workcell. Reel rack, guarded cutter, radial crimper jaws, fittings drawers and under-bench hydraulic powerpack; 245 editable components using existing materials/shared cylinder meshes, no new animation.
- Candidate density_hose_repair_20261105-210553.blend. Corrected motor to clear underside of worktop and routed two hydraulic lines around bench edge; explicit motor/hose-vs-worktop BVH test empty. External intersections only two base feet over ENV_floor_joints, not equipment or aisle obstacles.
- Inspected close seated-angle render, then rear/plant fixed-view renders. Adds identifiable mid-height equipment without closing marked aisle or rear doorway. Full six-view masks written to hose-review/hose_coverage.json; no runtime integration or performance claim yet.
- Selected app remains checked belting.glb. Live Blender, production and APK unchanged. Goal remains active; density target and full delivery gates incomplete.

### Hose-repair runtime verification — 5 November
- Native CUA retry still reports Mac locked. Saved-scene work continues; pending live application script updated to include inspection walkway, bench rebuild, spare-belting and hose repair after the previously pending services. It has not been executed in live Blender.
- Hose export pipeline passed roof reduction, AO and GLB markers:119 static batches and355clips, unchanged from belting. Selected hose.glb locally and updated current-density-build.json source/hash. Imported material/instance test explicitPASS:43AO/417packed,312sources/25groups.
- Desktop Compatibility six-view draws136/112/111/115/116/87 unchanged; +5804triangles per view due material batching. Medians1.550/1.469/1.467/1.507/1.536/1.434ms. Runtime plant view inspected; supported bench/reels and aisle clear. These are desktop counters, not verified Quest frame times.
- Investigated existing shutdown warning with verbose loader test on prior selected belting scene: behavioralPASS, one leaked RefCounted object with reference count0. This does not identify an application node, prove a scene memory leak or explain headset lag. No speculative production code change made; warning remains unresolved.
- Density coverage0.408222 (~68.5% above baseline); doubling target, live apply and final delivery still open. No APK/publication/production changes.

### Whole-layout crane/aisle check and shaft-lathe candidate — 5 November, 21:16
- Evaluated latest selected native geometry (hose repair source) against central aisle box x±3,y±21.5,z.15..2.2: no DENS obstacle hits. Checked nine moving crane meshes against new fixed DENS geometry at49poses, frames1..1201 every25: no contacts. Evidence density-crane-aisle.json. Finite sampled checks, not continuous swept-volume/access certification; animated coal excluded.
- First shaft-lathe bay intersected hopper walls/stairs/pedestrian rails and was rejected. Revised narrow envelope x[3.15,4.65],y[-13.8,-9.8],z[.02,2.1] empty by evaluated-mesh test; leaves space toward stairs and trolley ends and central route.
- Built 47-component parked shaft-repair lathe: pedestal/bed/ways, chip tray, headstock and stopped three-jaw chuck, rear half-guard, supported workpiece and tailstock, carriage/toolpost, feed screw, aisle-facing controls and splashback. No added animation/lights/material families.
- Native candidate density_shaft_lathe_20261105-211535.blend; external evaluated-mesh collision audit empty; close view inspected shows connected headstock/workpiece/tailstock and clear controls. Six seated-view review and export/runtime remain pending. This candidate is not yet selected in the app or live Blender.
- Selected app still hose.glb. Production/APKs unchanged; full density target and delivery remain incomplete.

### Shaft-lathe integration — 5 November
- Six fixed seated views rendered; portal/conveyor views inspected. Mean equipment coverage0.409635738 (+69.1% versus baseline0.242297). Lathe visible beside service railing; main aisle and portal unobstructed. Doubling remains unproven/incomplete.
- Roof/AO/export pipeline passed; selected lathe.glb locally,355clips/119staticbatches unchanged. Updated current-density-build.json and pending live script (not executed).
- Actual imported material/instance test PASS43AO/417packed,312sources/25groups. C11–C13 actual motion PASS30rocks over40s, no off-belt/stagnant rocks, max visible step0.01576058m.
- Desktop six-view draws136/112/111/115/116/87 unchanged; +1820triangles per view. Medians1.552/1.463/1.453/1.483/1.499/1.397ms remain comparable to hose scene. Runtime portal view inspected. No headset frame-time claim.
- Live Blender/APKs/production unchanged. Remaining work includes density target, full final-layout/material audit, live application and beta/headset validation; goal stays active.

### Consolidated readiness audit — 5 November
- Inspected actual source tags: all18planned workcell groups plus13belt groups, later service stations, galleries and utilities are present. Recorded density-cell-inventory.json; groups such as supports/cable trays are not counted as independent workcells.
- Current selected export passes broader factory-expansion, real Main/noticeboard integration and release-diagnostics fixtures with explicit completion markers. Native decoder/access in noticeboard test remain mocked.
- Wrote current-density-readiness.md distinguishing supported completion claims from open requirements. Asked optional visual-direction question with current runtime portal image; no answer yet, so original visible-density scope remains in force.
- No scene, production or release mutation this audit turn. Goal remains active, not complete or blocked: independent saved-scene work remains possible despite live lock.

### Service-press motion completed — 5 November, 21:30
- Added native 50-second unloaded press cycle: hold raised, .65 m downstroke, hold, return, long rest. Piston telescopes while its top remains anchored; tool plate translates. No new mesh/light required. Native candidate density_press_motion_20261105-212718.blend.
- Native audit all1201integerframes: measuredstroke.649999976m, minimum tool/bed gap.2099998m, maximum anchor deviation1.19e-7m, exact loop matrices, no errors. Linear segment extrema are covered. Raised/lowered renders inspected and show connected piston/tool plate.
- Export pipeline passed;357clips (+2),119staticbatches unchanged. Selected press.glb and updated source/hash manifest and pending live script. Existing11motion-player grouping retained (new50s clips share the existing period).
- New actual-import regression test_service_press_motion.gd: initially exposed a test type-inference parse error (not a valid negative result), corrected with explicit Transform3D. Then old static export failed explicitly for missing animated components. New export passes3001samples at60Hz plus suspension: stroke.650000095m, minclearance.209999895m, anchorerror2.38e-7m, no failures.
- Current material/instancing and cold-load/audio/suspension tests pass explicitly;43AO/419packed surfaces,312sources/25groups. Existing single RefCounted exit warning unchanged.
- This is motion polish, not added density: last six-view coverage remains0.409635738 (~69.1% above baseline). Optional density preference unanswered, original target retained. Live window/APKs/production unchanged, goal active.


## 5 November: second parked service crane

Added a parked, unloaded bridge at y=-10 with trolley x=3 on the existing continuous runway. Nine shared-mesh components; retained the original moving crane. Native inspection found only six runway interface contacts, no unrelated machinery intersections. The central aisle volume has zero new-geometry intersections; 49 sampled original-crane poses have zero contacts with additions. This is sampled geometric evidence, not engineering certification or a continuous sweep proof.

Reviewed native seated portal and actual Godot portal rendering. Portal text and entrance remain visible. Six-view mean equipment mask coverage is 0.427778742 versus original 0.242297, approximately 76.6% higher; original doubling objective remains open. Export has 121 static batches and 357 clips. Imported material/instancing test passes (45 AO,419 packed,312 sources in25 groups); original machinery and press motion tests pass explicitly.

Selected local source/export are recorded in current-density-build.json. Pending live application script includes crane; live UI remains unavailable. Nothing released. First profile overlapped headless tests and its timing is not a clean comparison; separate clean profile requested.

Clean desktop sample completed: medians1.437–1.604ms,draws140/114/115/115/116/87. Evidence: service-crane-profile-clean/service-crane.json. No Quest performance claim.


## 5 November: hydraulic service enclosure candidate

Candidate density_test_guard_20261105-214749.blend adds120 native components around the existing rear cylinder service bench. It has open crane access above, paired sliding-leaf visual guards, an external stop control, and two hose-port slots. This is visual environment dressing, not a certified pressure-test enclosure design.

Initial guard/bench intersections were corrected: end panels sit beyond existing rail ends, four end supports reach the floor, and two intermediate supports land on the existing plinth. test-guard-audit.json has zero external mesh intersections. test-guard-motion.json samples rod and clevis across49poses with zero contacts. Reviewed close native render and seated rear view. Mean six-view equipment coverage0.429651492 (~77.3% above baseline), still short of doubling. Export candidate underway; not selected for runtime or live editing yet.

Guard candidate integrated locally:122static batches,357clips,46AO/419packed material surfaces,312moving sources in25instance groups. Explicit material and factory machinery tests pass; clean profile recorded in test-guard-profile/test-guard.json. Selected native/export updated in current-density-build.json; pending live script includes guard. No release or Quest verification.


## 5 November: portal lettering export reduction

Native editable source remains density_test_guard_20261105-214749.blend. A disposable export copy halves the two baked lettering meshes: VERTOconnect13024→6512triangles;DECLINE14772→2386. Bidirectional vertex/centroid/edge-midpoint deviation samples max0.788mm and0.438mm; stronger quarter-resolution variants rejected. Total8898fewer base-mesh triangles. Selected export is sign_lod_ao.blend/sign_lod.glb; current-density-build.json updated.

Actual GLB accessor counts prove reductions survive export. An initial interpretation of unchanged rendered triangle counts as failed export was incorrect: Godot generates mesh LODs and seated rendered counts are effectively unchanged. Do not claim a frame-rate win. Actual clean comparison: GLB46455056→46254652bytes (200404saved); reported GPU memory150513217→150184689bytes (328528saved). Local frame medians1.424–1.562ms are comparable to prior sample. Imported materials/instances test explicitPASS; portal screenshot inspected and text remains readable. Original source unchanged.

New prepare_factory_sign_lod.py and build_density_export.py preserve this route for subsequent candidates: native→roof detail→sign detail→AO→GLB. Wrapper syntax checked; stages executed individually this turn. Sign preparer now explicitly materialises the modifier in the disposable copy to avoid depending on static-leaf export behavior; a second prepared candidate exists but is not selected. No Quest lag resolution or release claim.


## 5 November: inner service-bay ventilation

Candidate density_inner_vent_20261105-220135.blend adds33m of rectangular ventilation trunk over the right inner bays atx6,z6.4. Six downward registers, bolted joint bands, fabricated corner covers and six column-braced cantilevers. Feed rises at the front and connects over existing equipment to the round side main at(17.8,-17,7.35). Source-space route audit used evaluated mesh intersections rather than only oversized assembly bounding boxes. Native contacts are limited to intended column attachments and main-duct junctions; no unrelated equipment conflicts. The49-pose crane/aisle audit has no new-geometry contacts. Close view and six seated views reviewed; mean equipment coverage0.453698560 (87.25%above original0.242297), still short of2x.

Using build_density_export.py for full preserved-source→roof→sign→AO→GLB pipeline. Runtime selection and performance verification pending at this entry.

Inner ventilation integrated into selected local scene; imported materials/instances and original machinery tests explicitPASS. Reviewed actual runtime conveyor view. Static batches122,clips357,312moving sources/25groups. Desktop draw counts unchanged; ~4384extra rendered triangles. Clean medians1.450–1.551ms. Source-preserving full export wrapper now exercised successfully. Live application script updated, not executed; no release or Quest performance claim.


## 5 November: west inner-bay ventilation

Candidate density_west_vent_20261105-220717.blend adds the second33m branch, offset tox=-7 (rather than mirroringx=6directly) to clear the moving crane hook. The cross feed and braced column supports are shortened to match the offset; main connection remains(-17.8,-17,7.35). Most mesh geometry is shared with the east branch. Close native inspection confirms connected ducts, outlets and supports. External contacts are limited to existing column/main-duct joints;49sampled crane poses and central aisle check have zero hits.

Six-view mean coverage0.471659272 vs0.242297baseline (94.66%increase). Doubling target0.484594 remains slightly unmet. Native candidate reviewed; runtime selection pending at this entry.

West branch integrated locally; material/instancing and factory machinery tests pass. Actual runtime processing view reviewed; clean profile:west-vent-profile/west-vent.json. Native and export selection manifest updated; source-preserving wrapper passed. No release; live script prepared but not applied.


## 5 November: welding screens and full local review

54 native components form two pleated opaque burgundy welding screens, with wheeled feet and suspension hardware. Shifted0.35m along the bench to clear a bollard; external mesh audit now has no contacts. Aisle and49-pose crane sweep checks pass. Native source density_welding_screens_20261105-221326.blend and welding_screens_ao.blend/GLB are selected locally.

Six-view mask mean0.484372749 versus0.242297baseline =1.99909times, approximately double. Do not add meaningless geometry to chase a rounding difference. Final local seven-test set explicitPASS (density-final-tests.json); six actual runtime views inspected. Current draw counts140/114/116/116/116/89; desktop medians1.482–1.891ms. Quest remains unmeasured.

Visual review caught a remaining layout issue: spare belt reel hides fanB. Fan sightline audit21sampled target points: all21first hit DENS_Belting_Roll. FanA is mostly obscured by pre-existing FIT_TestBench components (only2directfan hits plus1none). These are not completion passes. Preserve recognisability of the requested large fan system: reposition reel first, then assess test-bench sightline without crowding routes. fan-sightlines.json records exact occluders. Live apply and final headset review remain open.


## 5 November: final fan sightline correction

Moved spare belting1.6m farther into its bay. Initial motor-bench move3m hit a column and hose reel; rejected. Final4m move shifts complete163-object motor-test station including its editable label and all instrumentation. Rotor and child blades retain their hierarchy; sampled rotor location remains stable during its rotation. Native external mesh checks show zero contacts for relocated reel and station.

Fan sightline samples: fanA21targets unobstructed by equipment (14open rays into intake,7fan-surface hits); fanB8open/fan hits and13existing structural-column hits. No reel or bench occlusion remains. Actual runtime fan/processing views reviewed; structural columns remain intact. Approximately double density remains (mean0.482915059 vs0.242297baseline,1.993x), preserving fan visibility rather than chasing a fractional screen-mask target.

Selected native density_fan_bench_clearance_20261105-222719.blend; export fan_bench_ao.blend; manifest records checksum. Material/instancing and original machinery tests rerun and explicitly pass after relocation. Previously completed other five tests have no related code changes. Clean profile fan-bench-profile/fan-bench.json: draws137/114/116/116/117/89,medians1.464–1.555ms. Actual headset lag remains unverified. Pending live application script now includes both relocations; open Blender has not received them. No release.


## 6 November: live Blender delivery verified

Loaded the audited native revision after preserving the previously open scene as live_before_final_density_20261106-093154.blend. Saved review file VERTO_factory_density_review_20261106-093358.blend. Read-only bridge verification confirms 6485 scene objects (6600 total datablock objects), all thirteen DENS_Belt collections, camera forward approximately (0,-1,0), and no unsaved changes. Native screenshot confirms portal-facing expanded factory, clear central route, conveyors, overhead services, crane and visible fans. Current manifest records live application. Audited export source remains unchanged; no APK or production update and no Quest performance claim.


## 6 November: standalone export-package verification

Exported density-review.pck with the actual Quest 3 preset. Export completed with no ERROR/WARNING log entries. Ran a standalone Godot process from staging using --main-pack (outside the source project), then loaded the density scene and mining_background.mp3 successfully from the pack. Audio length30seconds; excluded previous mining_facility scene is absent. density-pack-verification.json records size/checksum and exact scope: this is a resource pack, not an installable APK.

Local Android preflight: system Python lacks tomllib; bundled Blender Python3.13 satisfies Python requirement, but host_tools reports missing Gradle. Standard SDK/JDK directories are absent. Existing GitHub workflow supports separate beta identity via distribution_channel=beta. No workflow dispatched or account credential used; production unchanged.


## 6 November: beta source preparation

Added the reviewed density GLB exact checksum to Check-PublicSource and required density authoring/export/provenance files. The 61 workflow tests pass, including asset-boundary negative tests. A proposed 984-file source set passes the public-source checker with zero findings; beta-source-files.json and beta-source-check.json are staged outside the repository as review evidence. Git diff whitespace check passes. No source commit, push, workflow dispatch or release yet. Explicit DiggerPriest-only noninteractive credential lookup returned unavailable; no alternate account credential used. User asked to restore project-scoped DiggerPriest access.

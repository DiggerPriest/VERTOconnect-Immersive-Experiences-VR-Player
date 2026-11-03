# Higgsfield concept export review — 2 November 2026

This is an intermediate asset review, not approval for deployment. The baseline
below predates the recovered conveyor; the current local revision is recorded below.

## Verified baseline

Source: `/tmp/verto-higgsfield-concept/VERTO_concept_export.glb`.
SHA-256: `e444ddcedbfa048b6892a8483955ada6e15f6c322d291f25d2f6b69b31d05eae`.

The Python structural audit passed: 96,334 triangles, 484 mesh primitives,
74 materials and one embedded 256 × 256 concrete image. These totals do not
measure draw calls or headset performance.

An isolated Godot 4.7.2 Compatibility project imported the file successfully.
`tools/training_hub/review_higgsfield_export.gd` found 527 mesh instances,
27 lights, four cameras and four animation clips with changing keys: the two
fan rotors and the two beacon rotors. This confirms imported animation data,
not that the application's scenery lifecycle plays the clips correctly.

## Visual gate: not passed

The actual Godot seated screenshot is saved under
`build/training-hub/higgsfield-preview/godot-seated-intake.png`.
It was rendered with the exported lights and a small neutral ambient fill.
Walls, floor and yellow equipment are washed out; surface definition is poor.
The imported lighting needs calibration or replacement with baked lighting.
The screenshot also confirms that the truck and tunnel remain simplified
geometry. More preview resolution will not supply the missing surface detail.

Required before a release candidate:

- Upgrade the truck and nearby service equipment with inspected detailed assets.
- Add suitable texture detail and bake Blender-only procedural materials.
- Calibrate lighting in the target renderer, then inspect front, rear and side views.
- Reduce static mesh/material submission overhead while preserving animated roots.
- Verify the completed conveyor's rock movement and hidden recycling in Godot.
- Verify independent animation playback, pause/resume, and headset performance in
  the app. Do not treat these isolated import checks as device acceptance.

The existing released app and default panorama have not been replaced by this
review project.

## Conveyor recovery and runtime verification

The first plugin conveyor export (`VERTO_Conveyor_20261102-154348_complete.glb`)
contained no animation array. The saved `_animated.blend` checkpoint did contain
150 active object actions. A separate factory-startup Blender process exported
those actions successfully with `export_higgsfield_checkpoint.py`, leaving the
live plugin process and source checkpoint untouched. Use `--python-exit-code 1`
when running the exporter so a failed audit cannot appear as shell success.

The recovered asset is `build/training-hub/higgsfield-preview/conveyor-recovered-v2.glb`.
It was imported into the isolated `conveyor-preview` Godot project. Runtime
inspection confirmed transforms changing on all 150 animated nodes, including
72 `CV_ORE_*` nodes and 42 idlers/drums. These are sampled transform checks,
not proof of collision-free movement across the complete loop.

Godot adds constant rest tracks for neighbouring objects to imported clips.
The initial per-action playback implementation therefore left only the last fan
moving. `mining_scene_motion.gd` removes those constant tracks from duplicated
animations and groups disjoint tracks with equal durations. The corrected
controller drives all 150 moving nodes using five players, preserving original
animation resources and distinct durations. A regression fixture reproduces the
rest-track interference and checks suspension, resumption and repeated setup.
The controller is not yet attached to a released mining environment.

Review outputs: `conveyor-preview/godot-motion.json` and `godot-intake.json`.
Lighting comparison renders at imported-light scales 1, 0.03 and 0.15 confirm
that lowering energy reduces clipping; this is diagnostic calibration, not a
finished lighting bake or approved look.

## Current local PBR and floor AO revision

- Source export: `mining-pbr-ao-v2.glb`; SHA-256 `8674c4877a13deabc0176f4949a5d30f87f47f9819bcf81d453a52c1be090455`.
- Six Poly Haven 2K concrete/rock texture maps plus a separate 2K floor AO atlas. Source URLs and hashes are in `material-sources.json` beside this document.
- Floor top UVs isolated from underside and edge UVs; exported occlusion uses texture coordinate 1.
- 150 exported animated nodes retained; isolated Godot motion check passed.
- App loader test `test_mining_environment.gd` passed with the revised GLB, covering activation, suspension and switching. This is not a Quest performance or full browser-flow test.
- Runtime floor tint neutralises the warm concrete; AO affects direct light as well as ambient.
- Visual quality remains below final approval: broader lighting, equipment detail and headset validation remain open. No APK published for this revision.

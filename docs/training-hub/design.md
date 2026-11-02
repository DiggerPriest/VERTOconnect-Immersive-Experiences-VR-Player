# VERTOconnect animated training hub

This is a staged, optional environment prototype. It is **not** the finished
four-worker environment or a hardware performance certification.

## Current milestone

Four detailed trade bays and four clothed, rigged workers are integrated locally.
Electrical, plumbing, carpentry and mechanical routines have independent clocks,
phase offsets and pauses. Async loading and a hand-selectable look-around/return
control are implemented. Scenery is silent and its assets are local. Worker
tailoring and integrated visual review remain in progress.

The existing panorama remains the default. Ryan has requested the completed hub
become the default after he is satisfied with it. Do not migrate defaults before
that acceptance, including on the existing five managed headsets.

## Authoring and preview

- Blender 4.5.3 LTS arm64 is installed in `~/Applications/Blender-4.5.3.app`.
  Official DMG SHA-256:
  `73ea841053b55404bb3a71a9a22366f1f8821787fe5c899f8b55a7fff929d01b`.
- MPFB 2.0.18 is installed in Blender's `user_default` extension repository.
  Download source: `https://github.com/makehumancommunity/mpfb2/tree/v2.0.18`.
  The downloaded source ZIP SHA-256 was
  `ada7c4ff11e79cf6ed9b441bccabc52c9359f2848b988f66e89c14c30b21fed7`.
- Read [environment.md](environment.md) and [worker.md](worker.md) for reproducible
  build commands, asset provenance and specific visual limits. Source scenes and
  intermediate texture bakes go under ignored `build/training-hub/`. Only exported
  GLBs and their Godot import settings ship in the app.
- Run `python3 tools/training_hub/audit_glb.py app/godot/environments/training_hub/*.glb`
  before import; it rejects non-finite asset data and reports geometry/animation
  counts. Counts do not measure runtime draw calls or frame time.
- Import with the project's pinned Godot using `--headless --editor --import`.
- Run Godot with `--xr-mode off --path app/godot --script tests/render_training_hub.gd`.
  This renders actual Compatibility-engine screenshots at a seated eye height,
  plus worker close-ups at 0, 8 and 16 seconds. Output: `build/output/training-hub/`.
- Append `-- --record-hub` to capture 200 Godot frames at 10 fps. On macOS,
  `swift tools/training_hub/frames_to_movie.swift build/output/training-hub/frames build/output/training-hub/electrical-worker.mp4`
  makes a silent 20-second inspection preview. This preview's 10 fps encoding
  must not be confused with measured app/headset frame rate.

## Validation and remaining gates

[integration.md](integration.md) describes lifecycle/ray-input regression tests.
The primary agent reviews integrated screenshots after each asset revision;
Blender-only previews do not establish final Godot appearance.

Before accepting the four-worker scene: inspect it on one Quest 3, measure frame timing and memory, test the current video/Jess return
flows, wearer removal and repeat background switches. Complete a 30-minute soak
without casting for the performance baseline. OVR Metrics/MQDH requires device
access that has not yet been established; in-app counters are only a partial
fallback, not full GPU profiling.

After the prototype gate: improve visual defects and repeat the tests, and publish a separately identified test/release APK with its
matching hash. Preserve the package/signing identity. Do not claim this milestone
is v1 or change repository visibility without Ryan's explicit direction.

## Licensing

Architecture, tools, baked procedural surfaces and animations are custom project
work. The worker's human base comes from MPFB/MakeHuman core CC0 assets; see
`third_party/player-licenses/training-hub/MakeHuman-ASSETS.md`. No Mixamo, paid
asset-store meshes or proprietary generated-world exports are included. No
additional character/model service is contacted at runtime.

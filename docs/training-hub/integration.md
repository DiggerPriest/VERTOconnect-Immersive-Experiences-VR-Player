# Optional training-hub integration

Status: local prototype integration, not released or headset-certified.

## Behaviour

- `training_hub` is a new explicit background choice. Fresh installs and existing
  installations without a new selection continue to use the `verto` panorama.
  Do not migrate the default until Ryan approves the finished environment.
- The world is attached to the main scene, not the headset camera. Its assets are
  local GLBs loaded through a threaded `PackedScene` request.
- The workshop panorama remains visible while the scene loads and on load failure.
  A small world-space label reports loading/fallback. If loading finishes after
  another background was selected, the scene remains hidden and suspended.
- Animation and rendering are suspended for active media (including flat video),
  Jess, wearer absence, application pause, loss of XR input focus, or temporary
  passthrough. The existing Android/OpenXR browser-return path is unchanged.
- Content is disabled before it enters the scene tree, avoiding an autoplay frame
  when an asynchronous load completes during Jess or headset absence.
- Runtime uses `TrainingHub.apply_preview_lighting(environment)` for the same
  prototype ambient fill as the desktop preview. Previous ambient source, colour
  and energy are restored exactly when the scene becomes inactive or is removed.
  This does not change media shaders or install a second WorldEnvironment.
- Look around removes the library panel, navigation, footer and device-status
  bar. A hand-selectable Return to menu button remains on the existing ray-menu
  path. The mode cannot be entered while browsing during playback. Opening the
  library afresh restores its normal state.
- Four actor roots explicitly select the electrical20s, plumbing24s, carpentry18s
  and mechanical26s authored clips. Independent clocks use phase offsets0/6/9/13s
  and hold the matching end pose for4/3/5/4s. No arbitrary first-clip autoplay or
  shared global animation loop is used. Both endpoints are authored alike.
- Electrical placement is `(1.1,.0305,-7.9)`, yawPI on its mat; plumbing
  `(7.9,0,1.1)`, yawPI/2; carpentry `(-1.1,0,7.9)`, yaw0; mechanical
  `(-7.9,0,-1.1)`, yaw-PI/2. Two soft foot ellipses share one transparent draw
  per worker. These are inexpensive contact approximations, not dynamic shadows.
- Background settings expose an optional session-only performance diagnostic when
  the hub is selected. Default Off; it is not persisted. The readout reports FPS,
  average/max frame intervals, total render calls/primitives and engine/render
  memory where available. It hides during Jess, media and suspension. These are
  app counters, not GPU timing or a claim of meeting Quest refresh targets.

## Verification

Commands run with Godot 4.7.2, using `--headless --xr-mode off --path app/godot`:

- `--script tests/test_training_hub.gd`: pass. Tests missing assets/fallback,
  asynchronous completion after deselection, four named clips/independent durations,
  idle pauses/cycle restart, all four clocks pausing/resuming, opt-in diagnostics, scoped
  lighting/restoration, actual main-app Jess/media/presence switches, unchanged
  fresh-install default, panorama restoration, footer hiding and a real hand-ray
  press on Return to menu.
- `--script tests/test_background.gd`: 81 checks, zero failures. Updated the
  background-choice ordering expectation to include the optional hub after the
  unchanged default and before industrial panoramas.
- `--script tests/test_library_menu.gd`: 103 checks, zero failures.
- `git diff --check`: clean at verification time.

Earlier targeted runs reached explicit passing results but emitted macOS
FreeType/SystemFont errors. These were subsequently diagnosed and fixed (below);
the strict full-suite gate is required before release. No claim is made that these runs validate headset rendering,
Quest frame rate, GPU usage, hand tracking in hardware, browser return in hardware,
or a 30-minute thermal soak. Those remain one-headset acceptance tests.

No package/signing identity, app-default migration, Git push or release change
was performed by this workstream.

## Release readiness

The public-source checker now has five exact-path/SHA-256 GLB pins. Matching
assets may exceed the usual25MiB limit up to50MiB; all other GLBs are rejected.
Source builders, audit script, design/environment/worker provenance and MakeHuman
asset licence must accompany the binaries. Seven boundary tests cover changed bytes,
renamed copies, missing or empty provenance, and size limits. Parent workstream
owns final asset audit/pin refresh and release packaging. Reproducible
Blender source scripts and fixed dependencies should accompany generated assets;
large `.blend` intermediates need not be distributed with the Android build.

Before replacing the panorama default: perform real four-worker headset frame-rate
and thermal testing; repeat Jess close/return, media play/stop and wearer changes;
validate hand selection and look-around Return; verify offline switching and failover.
No headset test or performance claim has been made by this integration workstream.

## Texture import finding (pre-optimisation)

Inspection after the first final-asset import found GLB `embedded_image_handling=1`
(extracted PNGs). Both architecture and worker generated PNG imports had
`compress/mode=0`, `metadata.vram_texture=false`, and mipmaps enabled. The global
project enables `textures/vram_compression/import_etc2_astc`, but that alone does
not change these per-texture imports to VRAM compression. Before an Android test
release, explicitly configure the scoped hub textures to VRAM mode and verify
ETC2/ASTC variants in import outputs. Preserve this policy in the build pipeline;
do not rely on developer editor detection. See the official
[texture importer reference](https://docs.godotengine.org/en/stable/classes/class_resourceimportertexture.html).

## Reproducible VRAM import fix

`configs/training_hub_textures.py` derives expected PNG names directly from the
five embedded GLBs. After Godot extraction, it configures only those textures for
VRAM compression and mipmaps. `tools/training_hub/reimport_textures.gd` explicitly
reimports the hub folder through EditorFileSystem; ordinary startup scanning did
not reimport generated textures after external settings edits. The build helper
checks the completion receipt, rejects errors except the known editor shutdown
RID report, and verifies Android compressed variants. Both host CI tests and APK
packaging call this helper. Generated PNGs and their imports are ignored, keeping
the pinned GLBs as source-of-truth without duplicated texture payloads.

Verified locally: all23 textures report `vram_texture=true`, with `s3tc_bptc` and
`etc2_astc` imported formats and actual `.etc2.ctex` output. Four import-policy tests
and seven source-boundary tests pass. The asset preview must be checked after
compression; this does not establish Quest GPU performance.

## Host font regression repaired

The first full host run exposed an existing font failure, not just harmless log
noise: macOS `SystemFont("PingFang SC")` resolved the reserved PingFangUI collection,
which FreeType failed to load. Invalid text metrics also prevented a long filename
from creating its tooltip, causing `test_independent_playback` to dereference null.
An isolated mixed-text probe reproduced this for PingFang and succeeded for Heiti SC
and Hiragino Sans. `ray_menu.gd` now uses the bundled Inter font as the English
primary face and public macOS Heiti/Hiragino CJK fallbacks; Chinese/Japanese locales
retain a CJK primary face. Other platforms retain their CJK family selection.
Both the formerly failing tooltip test and a new four-locale mixed-title font test
complete without engine errors. The strict CI error gate remains unchanged.

Final host verification after worker refinement and font repair: **77 Godot suites,
zero failures**, using the unchanged strict `ci_support.host_tests` gate. This
includes import, scoped texture policy, all explicit completion receipts and error
checks. Results: local `artifacts/source-tests/junit.xml`; engine/test logs remain
local artifacts. Python runner was the bundled Codex runtime (Python with tomllib).
The system Python3.9 cannot run the existing build helpers requiring tomllib.

Texture verification now checks real, nonempty `.ctex` files declared by
`path.etc2`/`path.astc`, safely confined to `.godot/imported`; metadata strings
alone are insufficient. It also requires mipmaps and rejects missing/empty outputs,
path traversal, absolute paths and symlinks escaping the cache. Six policy tests
cover these cases. The authored512px `surface_detail.png` is the one intentional
source PNG; its exact ignore exception and required-source entry distinguish it
from regenerated GLB textures. It joins the23 extracted textures in the same
compression policy (24 total). No import or headset validation is inferred from
fixture test success.

Final refined-asset gate: **78 Godot suites, zero failures** (strict host runner,
including the surface mapping test with its required completion receipt), plus
**55 workflow tests passed**. All24 declared ETC2 files exist and are nonempty,
with19,400,224bytes combined on disk (not a GPU-memory measurement). The proposed
public source set contains836 files and passes with zero errors. Five asset pins
reflect the final contact-corrected workers and cleaned architecture. No signing,
package identity or default-background change was made. These local checks support
a one-headset test build; thermal/frame-rate and hand/Jess acceptance still need
actual headset evidence before the hub becomes the default.

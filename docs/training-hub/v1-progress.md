# Mining workshop v1 — release and acceptance record

Published 3 November 2026 as an additional asset on release `v0.9.4-360.24`. The eight pre-existing assets were verified unchanged. No headset assignments have been modified by this work.

## Published APK

This APK uses the production package identity: it is an update candidate, not a side-by-side beta. Meta Device Manager rejected adding it as a second app because that package already exists. A separate signed beta build is being prepared with `VERTO_ANDROID_CHANNEL=beta`, package `com.diggerpriest.immivio360.beta`, label **VERTOconnect VR Beta**. Production remains the default build channel; only the manually dispatched beta build selects the separate identity.

- URL: https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/VERTOconnect-Quest-Mining-v1-code32-20261103.apk
- SHA-256: `a22c16a852aa73369efb5e73f250571f5745cff8672edf0e7708350c401ad574`
- Size: 369,621,363 bytes; Android version code 32; version name 0.9.4.
- Package: `com.diggerpriest.immivio360`.
- Signing certificate SHA-256: `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`, matching the previous release.
- Source commit: `b314b6bccceb7711f352d623a3e741f3d2d0b78f` on `release/mining-v1-test`.
- CI run: https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41569311051 — macOS and Windows passed.
- Downloaded APK hash matches the build receipt and GitHub asset digest. Binary Android manifest independently checked for package and version code. Mining scene, compressed textures and MP3 stream are present in the APK. Public download URL returned HTTP 200.

## Beta revision — code 33 (build pending)

The user reports that the mining scene runs on Quest, with some lag, and headset removal stops playback while replacement restarts the same video at zero. They found that the returned video was zoomed in. Microphone acceptance has not been reported.

This revision makes mining the sole/default background, migrates retired saved background choices, removes old panorama/worker-scene assets from APK exports, uses the user-supplied `miningfactorymain.mp3` (30 seconds, stereo 48 kHz), and supplies a large gold V logo without lettering. Video reset now applies the fully zoomed-out limit both before the handover seek and on subsequent recenter events. Photo viewing retains its own reset behaviour. The separate beta package remains `com.diggerpriest.immivio360.beta`; production is still the default build identity.

Regression fixtures warm the shared mining resource before UI construction under Godot’s headless dummy renderer to avoid observed concurrent RID-allocation errors. The dedicated mining environment test retains cold asynchronous loading and lifecycle coverage. Environment requests are drained at shutdown and cannot restart from teardown signals. Headset performance has not been measured by these tests.

Local verification for this revision: all 83 Godot source tests and 60 workflow tests passed. A fresh signed Quest beta build is required before publication; the earlier cancelled beta build did not publish an APK.

## Scene evidence

- Final source checkpoint: `build/training-hub/source-checkpoints/VERTO_pump_connections_20261103-134309.blend`.
- App GLB SHA-256: `516bb393016c02fad611fa2b4ba015742340baf493e37f0572eaf75c51c40e33`.
- Scene: 192,500 triangles, 264 mesh primitives, 87 materials and 192 animation clips, combined into six independent runtime loop groups. Thirty scoped textures have Android compressed output.
- Rear expansion includes crane, gallery/stairs/rails, service headers, cable ladder and pump with connecting pipes. Crane bridge/trolley/hoist cleared from roof trusses using evaluated mesh intersection checks. Gallery stairs and pump checked against columns.
- Portal: curved fascia, concrete infill, orange service cables, centred illuminated sign and right-pillar green signal. Front and rear desktop app views inspected.
- Fans relocated from the conveyor bay; wall penetrations checked clear; guarded fronts and local controls inspected in a close render.
- Conveyor has transfer chute, skirt guards, return belt, idlers, drums, motor, braces and footings. Route and framed wall penetration clear the columns.
- All 42 coal pieces checked over a complete exported app loop: largest visible movement at 60 samples/sec was 0.0593 m. At the last visible frame, evaluated heap geometry covers each piece centre by at least 0.438 m. Full visual headset review is still pending.
- Grey concrete, narrow floor joints, restrained oil/tyre/coal overlays and subtle lane-marking wear implemented.
- User-visible Blender issue was Local View hiding new objects. Local View was disabled and the current checkpoint reopened; rear viewport now shows crane, gallery/stairs and pump. App default camera remains portal-facing.

## App evidence and limits

- Headset removal implementation pauses the active video and requests a restart of the same media session at 0:00 on replacement. Native proximity/display fallback, duplicate events, different-session protection and app gates have automated coverage. Actual Quest signal behaviour is not established by these tests.
- Jess requests Android microphone permission before loading the web page. Two JVM permission-startup tests passed on both runners. This addresses a possible permission/capture ordering problem; physical first-grant, denial/retry and reopening tests remain pending.
- User-supplied audio is a 30-second stereo MP3 at 48 kHz. Loop and pause/resume behaviour pass automated checks. Decoded peak was 4269/32768 and boundary sample jump 60/32768. Listening and headset volume checks remain pending.
- Intermittent headless shutdown warning remains documented: final macOS environment test reported three ObjectDB instances at exit despite successful assertions; another verbose local run did not reproduce it. The separate CI texture cleanup error in the real-worker test was addressed by waiting for queued cleanup and the fresh CI run passed.

## Remaining acceptance

The initial Quest test confirmed scenery and the pause/restart sequence, with lag and the zoom issue noted above. Retest code 33 using `docs/devices/mining-v1-headset-check.md`: microphone first-grant/denial/retry, same-video removal/replacement restart from zero, scene stability/performance/comfort, audio volume/loop and gating, and visual conveyor/portal/door/fan inspection.

Do not mark the overall goal complete until these device results and any resulting fixes are verified. After the user confirms the APK works, prepare the tested changes for merge into the fork's default branch `quest-360-mono`. Repository actions must use the DiggerPriest credential scoped to this project; never use rpvrt.

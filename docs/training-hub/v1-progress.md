# Mining workshop v1 — test release and acceptance record

Updated 3 November 2026. The revised beta is published as additional assets on release `v0.9.4-360.24`. All 11 existing assets retain their IDs, sizes and digests. No headset assignments or default-branch code were changed.

## Latest test APK — separate beta, code 33

- URL: https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/VERTOconnect-Quest-Mining-v1-Beta-code33-20261103.apk
- SHA-256: `26e8d8365ce20bf7e9b164ee497834a40cdaa5a32728fd71f37f85ce294c2abe`.
- Size: 147,110,064 bytes (140.3 MiB), versus 369,621,363 bytes for code 32; approximately 60% smaller.
- Package: `com.diggerpriest.immivio360.beta`; launcher label **VERTOconnect VR Beta**; version name 0.9.4; Android version code 33.
- APK v2 signing verified; certificate SHA-256 `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`, matching the established signing key.
- Source: `8f674e97d5b6ca60138cbb8f5b2683be8aa125dd` on `release/mining-v1-test`.
- CI: https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41577553907 — Windows and macOS passed. Windows required one retry after an exit-only dummy-renderer RID report; the first attempt's functional assertions all passed. The retry passed the full gate.
- All 83 Godot source tests and 61 workflow tests passed locally; hosted JVM/native and source checks passed before packaging.
- Downloaded APK bytes match its build receipt and the GitHub asset digest. Its binary manifest independently confirms beta package and code 33. Public APK URL returned HTTP 200.

## Changes in this beta

- Mining is the sole/default launch background. Retired saved selections migrate to mining. The settings menu and photo controls no longer offer alternative backgrounds.
- Old panorama images, the previous worker environment and their extracted textures are excluded from APK exports; the package inspector rejects retired scenery. The source assets remain available in repository history/development files. Only a shared detail texture needed by the current renderer remains.
- Video resets use the fully zoomed-out immersive limit before the handover seek and for subsequent recenter events. The photo viewer keeps its own reset behaviour. Restart still preserves the same media session, projection, stereo and queue.
- Ambience now uses the exact user-supplied `miningfactorymain.mp3` (30 seconds, stereo 48 kHz). Decoded packaged stream SHA-256 is `4270756480a1566c0788383eb1c7d5ff4797008fc03399cda247fa23d947cb98`, matching the supplied MP3. Looping and video/Jess/presence/focus gates remain in place at -22 dB.
- The revised app logo is the enlarged gold V only, with no wordmark. Release assets include a 512 x 512 opaque 32-bit PNG icon and 1440 x 1440 transparent 32-bit PNG logo.
- A rendered desktop launch from fresh settings confirmed automatic mining loading, one available background and a portal-facing view.

## Scene and lifecycle evidence

- Source checkpoint: `build/training-hub/source-checkpoints/VERTO_pump_connections_20261103-134309.blend` in the original working project.
- GLB SHA-256: `516bb393016c02fad611fa2b4ba015742340baf493e37f0572eaf75c51c40e33`.
- Geometry: 192,500 triangles, 264 mesh primitives, 87 materials and 192 animation clips, combined into six runtime loop groups. Thirty scoped textures have Android compressed output.
- Decoded mesh and animation data across 433 packaged geometry nodes match the previous tested scene. Godot resource UIDs differ between clean serializations; semantic audit SHA-256 is `3188fd48129318ec01d878b479da74bba4b5f21a6a95606d9c041ce0817776da`.
- The rear crane/gallery/stairs/rails, service headers, cable ladder and connected pump remain included. Portal, cables, signs, signal, fan wall penetrations, conveyor supports/exit and yard remain included.
- All 42 stockpile coal pieces were checked over a complete exported loop: maximum visible movement at 60 samples/sec was 0.0593 m; evaluated heap geometry covers each piece centre by at least 0.438 m at its last visible frame.
- The headless dummy renderer showed concurrent RID-allocation errors when the large scene loaded beside UI fixture construction. UI fixtures now warm the shared resource first; the dedicated mining test retains cold asynchronous loading and lifecycle coverage. Requests are drained at shutdown and cannot restart from teardown signals.
- Intermittent headless shutdown resource reports remain documented. They are not evidence of measured headset performance or a proven harmless runtime leak.

## Quest acceptance and next step

The user confirmed that the initial mining scene runs, with some lag, and removing/replacing the headset stops/restarts the same video at zero. They reported zoomed-in playback after replacement. The revised beta addresses that view-reset path and is ready for another test; its new behaviour, sound comfort and performance have not yet been retested on hardware. Microphone first-grant/denial/retry acceptance has not been reported.

Use `docs/devices/mining-v1-headset-check.md` on one Quest. After the user approves the results, prepare the tested changes for the fork's default branch `quest-360-mono`. Do not merge/promote before that confirmation. Use DiggerPriest credentials scoped to this repository; never use rpvrt.

## Earlier update candidate — production identity

The earlier code-32 asset remains unchanged at:
https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/VERTOconnect-Quest-Mining-v1-code32-20261103.apk

Its SHA-256 is `a22c16a852aa73369efb5e73f250571f5745cff8672edf0e7708350c401ad574`, package `com.diggerpriest.immivio360`, source `b314b6bccceb7711f352d623a3e741f3d2d0b78f`. It cannot be registered as a second Device Manager app because it uses the production package identity. The code-33 beta above provides the separate identity.

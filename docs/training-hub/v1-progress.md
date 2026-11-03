# Version 1 candidate — 3 November 2026

Release remains unpublished. Existing headset assignments and release assets have not been changed.

## Current evidence

- Blender checkpoint: `build/training-hub/source-checkpoints/VERTO_v1_candidate_20261103.blend`.
- Candidate GLB installed locally in `app/godot/environments/mining_facility/mining_facility.glb`; 192 animation clips exported, six independent runtime loop groups.
- Runtime environment, motion and ambience tests pass with `--headless --xr-mode off`. A prior environment run reported one RefCounted shutdown warning; a verbose rerun after the cleanup wait produced no leak warning. The warning was intermittent, so keep watching CI/device logs.
- Runtime views inspected: portal, fans, conveyor and rear door (`/tmp/verto-runtime-*.png`).
- Truck hidden; fans relocated, wall penetrations ray-tested clear. Conveyor rerouted between columns; wall opening ray-tested clear. Coal offsets corrected to belt surface; full-loop visual verification remains outstanding.
- Portal crossbars removed by connected mesh island; centred illuminated sign and right-pillar green signal confirmed in render.
- Grey concrete, narrow joints, sparse oil/tyre/coal overlays implemented. Painted line wear still needs final treatment/review.
- Source audio: 30 seconds, stereo 48 kHz. Decoded peak 4269/32768; boundary sample jump 60/32768; first/last 0.1-second RMS 456/439. No clipping; these measurements do not replace listening or headset volume testing.
- GitHub CLI installed at `/Users/rpriest/.local/bin/gh`; the signed-in account has verified push access. Current `.24` release remains unchanged; its Quest receipt identifies package `com.diggerpriest.immivio360` and signing certificate `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`.
- Current CI run 41563753232 passed on macOS and Windows, but it predates the latest rear expansion and microphone change and is not a final build.
- Latest scene is exported from `VERTO_rear_plant_visible_20261103-131729.blend`; the expanded gallery, stairs, crane, service headers and pump were inspected in Blender and a desktop Godot rear view. Headset performance and final close-clearance review remain open.
- Jess now requests Android microphone permission before loading the page, to avoid interrupting a pending WebView capture request. This is a proposed fix, not a confirmed root cause; permission grant, denial, retry and headset behaviour still need device validation.
- Workflow changes classify `-test.*` and `-rc.*` tags as prereleases, never latest, and remove asset clobbering.

## Remaining gates

- Re-run full runtime checks against the latest scene and build candidate.
- Verify the entire coal animation loop including feed, discharge and hidden recycle; check supports, guards, wall clearances and fan connections from close views.
- Finish inspection of fan controls, overhead workshop ductwork and painted-marking wear.
- Check compressed textures, lighting and anti-aliasing in the final runtime candidate. Desktop renders are not device performance evidence.
- Resolve or accurately diagnose remaining shutdown warning; run required app/native/source checks.
- Prepare isolated release branch, source/provenance documentation and unique test tag. Local workflow suite: 57 tests passed. Texture policy covers mining PNG/JPEG, with 30 Android compressed outputs verified locally; source boundary check only covered tracked files and must be repeated on the release commit.
- Build signed APK through CI, verify package/signature/version/hash and publish unique prerelease URL and SHA-256. Do not alter existing releases or headset assignments.
- User performs headset performance/comfort acceptance before wider rollout.

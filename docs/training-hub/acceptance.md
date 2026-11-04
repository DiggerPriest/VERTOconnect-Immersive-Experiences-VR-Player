# Training hub acceptance evidence

The current mining factory and queue-loop candidate was accepted by Ryan on 4 November 2026 and promoted to [production 0.9.6/code36](../devices/production-0.9.6.md). The evidence below records the earlier worker-hub prototype, before the mining-factory replacement, and is retained as history.

At that earlier prototype milestone the complete goal was not achieved. A desktop render is not a Quest performance test.

Local validation at this revision: 78 Godot suites passed the strict error and
explicit-completion gate; 55 workflow tests passed. All 24 imported scene textures
have verified ETC2 Android variants. These results include the final tool-contact and surface refinements.
No headset execution has been verified.

| Requirement | Current evidence | Remaining gate |
| --- | --- | --- |
| Full surrounding real geometry, seated view | Four actual Godot directional renders; world-root scene | Headset turn/lean check |
| Four recognizable workers and distinct trade routines | Four GLBs; named clips; runtime independent clocks; asset audits | Full-cycle recording review and headset visual acceptance |
| Modern steel/skylight/concrete/timber hub and elevated branding | Authored architecture and actual Godot screenshots | User visual acceptance; realistic polish |
| Smooth loops, planted feet, attached tools | Authoring export checks; actor timing tests | Review complete cycles in Godot and headset |
| Offline local assets and asynchronous fallback | Lifecycle tests of missing/loading/deselected cases | Offline headset switch test |
| Look around and return by hand | Real ray-input fixture test | Hardware hand-selection test |
| Pause scenery for video, Jess, wearer absence/focus loss | Main-app lifecycle regression suite | Repeated hardware transitions |
| Preserve player/browser/package/signature | Published Quest receipt matches prior package/certificate; strict host regression suite passed | Hardware player/Jess regression test |
| Practical mobile resource use | Asset counters and explicit ETC2 import verification | Quest FPS/memory plus 30-minute thermal soak |
| Preview before deployment | Actual Compatibility-renderer screenshots; one-headset test build published | User review and one-headset execution |
| Deliver APK URL and SHA-256 | v0.9.4-360.24 published; public APK downloaded, ZIP checked and SHA-256 matched | Complete for diagnostic build; final release follows acceptance |
| Become default when finished and accepted | Panorama deliberately preserved | Ryan approval then migration and verification |

Performance readouts are optional app counters, not full GPU profiling. The original
72 FPS minimum baseline and 30-minute soak remain required. Do not infer success
from desktop frame rates or triangle count. No paid assets or runtime asset services
have been introduced. Public repository visibility remains unchanged until Ryan
explicitly declares v1 and requests migration.

## Published diagnostic build

- Tag: `v0.9.4-360.24`; source commit `7d64ecfdab364c3d8a0253847a9ce613e5061c82`.
- [Successful Windows/macOS build and publication](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41365267172).
- [Direct Quest APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/Immivio-QUEST-0.9.4-release-20261102.apk).
- Size:351,993,988 bytes. SHA-256:`9d11a2c42b840cf7c495b992f2bc31d91a009bccad9aef15a823f4cc365f9ca4`.
- CI-verified package `com.diggerpriest.immivio360` and certificate SHA-256
  `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`
  match the preceding release. The downloaded APK hash matches that receipt and
  SHA256SUMS; ZIP integrity passed and hub resources/Android textures are present.
- Existing panorama remains the default. No device installation or headset test
  has been observed. See [headset-test.md](headset-test.md) for the required checks.

## Headset feedback on .24

Ryan confirmed the optional hub loads but reported all four visible workers remain
still after30seconds. Source and APK assets both advance bone poses on the host;
that does not establish animation on Quest. The runtime/rendering cause remains
unproven and needs on-device clock/bone/gate evidence.

Ryan also reported playback continuing after headset removal and persistent hand
rays. These are reopened interaction defects, not accepted regressions. Visual
acceptance was explicitly rejected: the environment is too basic and sparse.
Do not promote it to the default or describe the current art as finished.

The next visual pass must improve scene composition and believable materials,
people and trade activity at the actual seated viewing distance. The existing
procedural room is a functional prototype. A convincing finished trade bay in
Godot should be reviewed before repeating that treatment across all four bays.

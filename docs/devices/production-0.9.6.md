# Production 0.9.6 / code 36

Historical receipt; superseded by [production and dev/test 1.0.0/code37](release-1.0.0.md). This APK remains available.

Published and independently verified on 4 November 2026 after Ryan accepted the code35 beta ("worked 100% perfect") and requested production promotion.

- [Direct Quest APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.6/Immivio-QUEST-0.9.6-release-20261104.apk)
- SHA256: `6d5c0f0f1af6ea749e16989c5d849b45726af7b592cc256b93fdc748755d9733`
- Size: 148,857,712 bytes.
- VersionName: `0.9.6`; Android versionCode: `36`.
- Production package: `com.diggerpriest.immivio360`; label: `VERTOconnect VR Player`.
- Signing certificate SHA256: `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`, matching the established production key.
- Tag/source: `v0.9.6` / `ef06da4973eac22dbd3a3e5d2be4c3a2033e0c6c`.
- [Merged PR #1](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/pull/1) into the actual default branch, `quest-360-mono`.
- [Successful Windows/macOS build and publication](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41765514399).
- [Release manifest](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.6/release-manifest.json), [original Quest build receipt](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.6/Immivio-QUEST-0.9.6-release-20261104.build.json), [checksums](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.6/SHA256SUMS.txt).

The production scene, MP3 and playback scripts are unchanged from accepted beta source `0bee805`. Production preparation changes release metadata and distribution identity. The APK includes the expanded processing/rear workcells, service galleries/bridge, connected plant, moving crane/drums/ram and the supplied workshop ambience. **Loop videos** supports a single entry or any supported queue length; contents/order, loop and shuffle settings persist. Headset handover retains pause and same-video restart at zero.

Verification covered actual APK manifest identity/version, ARM64 libraries, ZIP integrity, APK v2 content digest and RSA signature, expected signing certificate, and a full unauthenticated public download. Public SHA256, GitHub asset digest, checksum file and original CI receipt agree. Extracted scene geometry and all 224 animation clips match the accepted baseline; the bundled audio matches the supplied MP3 SHA256 `4270756480a1566c0788383eb1c7d5ff4797008fc03399cda247fa23d947cb98`. The actual compiled queue script passed single-entry and two-entry wrap checks. Desktop resource inspection excludes the Android-only XR extension.

Both hosts passed the native/workflow/JVM/Godot release pipeline. All 61 local workflow tests and the 923-file public-source boundary check also passed during release preparation. User-reported headset acceptance applies to code35; the agent did not execute the production APK on a physical headset or independently measure Quest frame time/thermal behaviour. The original CI receipt retains `source_dirty:true` and has not been rewritten to claim a clean build tree.

The GitHub release is stable and marked latest. All previous production0.9.5 and code35 beta assets remain intact. Use this URL/hash to add a version to the existing production app in Meta Device Manager; no device assignment or fleet rollout was performed by this release operation. The beta remains separately installable.

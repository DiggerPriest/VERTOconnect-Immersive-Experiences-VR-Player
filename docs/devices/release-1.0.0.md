# VERTOconnect 1.0.0 — production and dev/test

Published and independently verified on 4 November 2026. Both channels are **version 1.0.0 / Android code 37**. This is a version-only promotion of the approved 0.9.6 functionality: scene, MP3, playback/queue, headset handover and Jess implementation are unchanged.

## Production — VERTOconnect VR Player

- [Direct Quest APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v1.0.0/Immivio-QUEST-1.0.0-release-20261104.apk)
- SHA256: `a8aec3abf61825a3a10fe2a120055a0c9b96a9130e442bea1e7e0f4c972b1f65`
- Size: 148,857,712 bytes.
- Package: `com.diggerpriest.immivio360`.

## Dev/test — VERTOconnect VR Beta

- [Direct test Quest APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v1.0.0/Immivio-beta-QUEST-1.0.0-release-20261104.apk)
- SHA256: `97f87b96a86e991f23dc5324b47f02507c06cdf1f367004624bcdaea963c8ff4`
- Size: 148,857,716 bytes.
- Package: `com.diggerpriest.immivio360.beta`.

Use each pair to update its matching existing Meta Device Manager app. The test app keeps the existing beta identity. Device assignments and fleet rollout were not changed by this publication.

## Provenance and checks

- [Merged PR#2](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/pull/2); source/tag: `2d34467277b8b7f381dd9b319e2efbf79d0342f4` / `v1.0.0`, on default branch `quest-360-mono`.
- [Production CI](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41769364147) and [test CI](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41769364299) each passed Windows/macOS build and test jobs. Published APKs use the canonical macOS artifacts. All 61 local workflow tests and the 924-file public-source check passed during promotion preparation.
- Both actual APKs passed manifest package/version checks, ARM64 library checks, ZIP integrity, APK v2 content-digest/RSA-signature verification and the established certificate SHA256 `e50eecdd0d06e6509417f9ac5a13509876e95a609208164ab790b94bfda69b3d`.
- Both imported scenes match the accepted geometry/animation baseline, including all 224 animation clips. Both bundled MP3s match the exact supplied audio SHA256 `4270756480a1566c0788383eb1c7d5ff4797008fc03399cda247fa23d947cb98`. Both compiled queue scripts passed single-entry and two-entry wrap checks. Desktop resource inspection excludes the Android-only XR extension.
- Both full unauthenticated downloads returned HTTP 200/APK content type and matched local independently verified bytes, original CI receipts, checksum files and GitHub asset digests.
- [Release](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/tag/v1.0.0) is stable/latest. Its original production `release-manifest.json` / `SHA256SUMS.txt` and separate `beta-release-manifest.json` / `beta-SHA256SUMS.txt` identify the two distributions. Original build receipts are retained unchanged, including their `source_dirty:true` flag.
- All previous 0.9.6 production and code35 beta assets, and the original production 1.0.0 assets during the beta upload, retained their IDs, sizes and digests.

Ryan previously accepted the code35 headset test and approved both promotions. The agent did not execute the new 1.0.0 APKs on a physical headset or independently measure frame time/thermal behaviour. The unchanged approved implementation and release/package integrity were verified.

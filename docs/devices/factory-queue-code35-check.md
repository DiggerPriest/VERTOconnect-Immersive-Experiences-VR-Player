# Code-35 beta acceptance on one Quest

Use the separate **VERTOconnect VR Beta** app (`com.diggerpriest.immivio360.beta`). Production remains code34. Keep all other headsets on the existing production app until this candidate is accepted.

Published candidate, verified 4 November 2026:

- [Direct code35 APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/VERTOconnect-Quest-Factory-Queue-Beta-code35-20261104.apk), 148,857,728 bytes, versionName0.9.5.
- SHA256: `84d71eddcbed1918abacfba818c67437d02af46e17d8e9e1ecca8b1585d0be1c`.
- Source commit: `0bee805ceb10e161e9673f2fbe69dcf5b6185f4d`. [Windows and macOS CI passed](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/actions/runs/41759965320); the macOS artifact is the published candidate.
- [Original CI receipt](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/Factory-Queue-Beta-code35-original-build.json), [candidate manifest](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/Factory-Queue-Beta-code35-manifest.json) and [independent verification](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/Factory-Queue-Beta-code35-verification.json) preserve provenance and validation limits. The original receipt retains `source_dirty:true`; it has not been rewritten to claim a clean build tree.
- Independently checked Android package/version, ARM64 libraries, ZIP integrity, APK v2 signature/content digest and expected signing certificate. Extracted geometry and all224 animation clips match the reviewed local scene semantically; the bundled MP3 matches the supplied file SHA256. The compiled queue script passed single-entry and two-entry wrap checks. Desktop resource inspection excludes the Android-only XR extension and does not prove Android execution.
- An unauthenticated full public download returned HTTP200 with APK content type and the same size/SHA256. GitHub's asset digest agrees. All older prerelease assets and the complete production release metadata remained unchanged.

Hardware acceptance is still pending. The goal is not complete until the following checks and Ryan's scene review pass.

1. Add any chosen videos to the queue, enable **Loop videos**, then start the first entry. At natural completion, each next entry must start at0:00; after the final entry, the first must play again. Exercise at least two full cycles.
2. Try one queued video: it must reopen from0:00 after completion. Turn looping off and verify final completion returns to the library. Stop must also exit playback when looping is on.
3. With multiple videos queued, remove the headset midway through a later entry. Audio/video must stop. Put the headset on again: the same entry must restart at0:00 with its view reset; after completion, the queue must continue normally.
4. Set a distinctive queue order plus loop/shuffle preferences, close the app, restart the headset and reopen the beta. Queue contents, order, loop and shuffle settings must be restored. Starting playback remains an intentional user action.
5. Look around the factory: portal starts in front; screening drums/coal, guarded test bench/pump shafts and overhead crane move; platforms, stairs, cabinets and services occupy the side/rear bays. Check the portal, roller door, exterior coal yard and existing hopper/conveyor/fan connections for regressions.
6. Listen for the supplied workshop ambience while in the factory. Enter a video or Jess and remove the headset: workshop animation/audio must suspend. Check scene comfort and responsiveness on the actual Quest; desktop render timing is not headset evidence.
7. On a headset where the beta has not yet been granted microphone access, open **Talk to Jess**, approve the microphone request and speak immediately. Jess must work without closing and reopening the app. If permission was already granted, record that the first-approval case was not exercised.

Report any visual issue, loop/restart failure, lost setting, stutter or uncomfortable sound. Do not promote this candidate to production until the one-headset check is accepted.

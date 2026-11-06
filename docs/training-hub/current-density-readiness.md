# Factory development readiness

Updated 6 November 2026. The current premium development review supersedes the earlier density-only checkpoints. See [the full review and fixed views](premium-development-review.md) and [editable source instructions](native-authoring.md).

- Scene and native source are pushed on `feature/factory-density-performance` at `384f5d292133fded829da0b91fbe256a4ff405b9`.
- Candidate identity: `1.0.1-beta.2`, Android code 39, beta package `com.diggerpriest.immivio360.beta`. It can coexist with production.
- GitHub beta build run `42153789794` was dispatched with `Release` and `distribution_channel=beta`; both macOS and Windows jobs completed successfully. The macOS APK independently passed manifest, source-receipt, certificate and APK v2 signature/content-integrity checks.
- Editable source: `assets/authoring/mining_factory.blend`, 6,522 objects, nine packed textures, no linked libraries, included/built-in fonts. Three historical non-auto-running conveyor text blocks were reviewed and checksum-pinned. The source dependency audit passes.
- Live Blender was switched to a separate code-39 review copy after saving a recovery copy of the previously open scene. Readback confirms the updated paint response, 54 retained screen components and hidden obsolete floor inlay.
- Ten fixed-position exported-scene views were inspected. Real Main captures separately exercise the empty and populated runtime board. All four tilted posters are selectable from the default camera. Test titles are fixtures; native decoder thumbnail extraction is not proved by those images.
- Seven relevant runtime checks pass: exported materials/instance transforms, machinery, noticeboard history/rays, Main playback dispatch, stockpile coal motion, headset handover logic and immersive lifecycle. The latter two are simulated desktop checks, not physical headset results.
- All 63 workflow tests pass. Public-source checks pass for 996 tracked files, including exact native/export asset pins. No unreviewed binary exemption was added.
- Optimisation retains 312 moving sources in 25 instance groups, static batching, source-preserving roof/sign export simplification, texture mipmaps and packed colours. The latest paced desktop frame intervals must not be compared as GPU timings with older unpaced profiles. Quest performance is unmeasured.
- Known limit: one ObjectDB instance is reported at shutdown by the Main playback test. It is not established as a headset performance cause.

Physical Quest testing belongs to the user and does not block development delivery. The APK is code 39 / 1.0.1-beta.2 and contains the selected density scene plus the 30-second MP3. Extracted resources load successfully in the desktop checker; Android-only extension loading on macOS is not a device execution test. No merge into main or production promotion is authorised.

## Verified beta download

[Download code-39 APK](https://github.com/DiggerPriest/VERTOconnect-Immersive-Experiences-VR-Player/releases/download/v0.9.4-360.24/VERTOconnect-Quest-Factory-Beta-code39-20261106.apk). Version `1.0.1-beta.2`, package `com.diggerpriest.immivio360.beta`. The URL uses the existing isolated test-release tag; the filename, manifest and Android version identify this new build. Existing assets were preserved.

SHA-256: `093afece5ddc7ede42aa413b06de9b4e4bf18d5ce48216146828059a06e4cf48`.

An unauthenticated full download returned HTTP 200 and matched all 180,485,542 bytes and the checksum. See `premium-review/download-verification.json` and `premium-review/build-manifest.json`. The application build is commit `384f5d2`; subsequent review-document commits do not alter its contents. Main and production were not changed.

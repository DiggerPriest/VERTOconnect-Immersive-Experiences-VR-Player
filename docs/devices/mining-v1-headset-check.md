# Mining workshop and Jess — first-headset acceptance

Use one Quest before updating the remaining fleet. No physical-headset acceptance has been recorded yet.

For a separate Device Manager app, use the **VERTOconnect VR Beta** APK with package `com.diggerpriest.immivio360.beta`. The earlier code-32 APK without “Beta” in its asset name uses the production package and cannot be registered as a second app. The beta has its own app settings and microphone permission; configure its video source/background independently and assign it only to the test headset.

## Scene and audio

1. Open Background settings and choose **Mining Facility — Animated (preview)**.
2. Confirm the starting direction faces the curved DECLINE 1 portal. Its green signal should be on and red off.
3. Turn around: confirm the crane, rear gallery/stairs, pipework and pump are visible. Check image stability, controller/menu readability and comfort while turning.
4. Watch both conveyors, the hopper transfer, the wall exit and coal discharge. Report visible gaps, floating rocks, clipping or reset jumps.
5. Listen through an entire 30-second audio loop. Confirm the volume is comfortable and no click or obvious break occurs at the loop boundary.
6. Play a video and open Jess separately. The workshop ambience must stop during either activity; it must also stop when the headset is removed.

## First microphone permission

1. If microphone permission is already granted, use the headset's app-permission settings to deny it for the player, without uninstalling or clearing app data.
2. Open Talk to Jess. Approve the microphone prompt and start a conversation. Confirm Jess hears speech without closing/restarting the player.
3. Return to videos and reopen Jess. Confirm speech works again.
4. Repeat with the microphone prompt denied; the app must remain usable. Approve permission on a later attempt or through app-permission settings, reopen Jess and confirm recovery without a full app restart.

## Removal and replacement

1. Select a video and confirm it starts at 0:00.
2. Let it play for at least 20 seconds, then remove the headset before it ends. Confirm playback/audio stops; use casting if needed to observe playback while the headset is off.
3. Put the headset back on. The **same video must start at 0:00**, rather than continue from its previous time. Repeat with a second wearer and then repeat removal twice.
4. Check the removal diagnostic identifies a presence event. A display-off fallback can be delayed by the headset's sleep policy; record any delay rather than assuming instant proximity detection.
5. With no video selected, remove and replace the headset: it must not start an unrelated video.

Record pass/fail for microphone, video removal/restart, ambience and scene performance, including headset OS version and any visible diagnostic/error text. The APK URL and SHA-256 are supplied separately after build/signature verification.
